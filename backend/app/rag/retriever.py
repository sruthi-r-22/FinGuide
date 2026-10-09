import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.core.config import PROJECT_DIR, resolve_chroma_persist_dir, settings
from backend.app.rag.embeddings import get_embedding_function
from backend.app.rag.generator import (
    is_verified_official_metadata,
    official_metadata_verification_issues,
)
from backend.app.rag.ingest import load_all_document_chunks
from backend.app.rag.relevance import (
    RETRIEVAL_SCORE_THRESHOLD,
    cosine_similarity_from_squared_l2,
)


COLLECTION_NAME = "finguide_banking_docs"
CHROMA_DISTANCE_SPACE = "l2"


class IncompatibleCollectionError(RuntimeError):
    """Raised when a stored collection cannot be queried by the configured model."""


class VectorStoreManager:
    def __init__(self) -> None:
        self._embedding_fn = None
        self.chroma_client = None
        self.collection = None
        self._initialized = False
        self._lock = threading.RLock()

    @property
    def embedding_fn(self):
        if self._embedding_fn is None:
            self._embedding_fn = get_embedding_function()
        return self._embedding_fn

    def _connect(self) -> None:
        if self.chroma_client is not None:
            return

        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "chromadb is required for FinGuide RAG. "
                "Install backend/requirements.txt in the backend environment."
            ) from exc

        persist_dir = resolve_chroma_persist_dir()
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "FinGuide AI document chunks",
                "embedding_model": self.embedding_fn.model_name,
                "embedding_dimension": self.embedding_fn.dimension,
                "hnsw:space": CHROMA_DISTANCE_SPACE,
            },
            embedding_function=None,
        )

    def _check_embedding_vectors(self, vectors: list[list[float]]) -> None:
        dimension = self.embedding_fn.dimension
        if any(len(vector) != dimension for vector in vectors):
            raise RuntimeError(
                f"Configured embedding model {settings.EMBEDDING_MODEL!r} "
                f"must produce {dimension}-dimensional vectors."
            )

    def _validate_collection(self) -> None:
        count = self.collection.count()
        if count == 0:
            return

        metadata = self.collection.metadata or {}
        distance_space = metadata.get("hnsw:space", CHROMA_DISTANCE_SPACE)
        if distance_space != CHROMA_DISTANCE_SPACE:
            raise IncompatibleCollectionError(
                f"Chroma collection {COLLECTION_NAME!r} uses distance space "
                f"{distance_space!r}; FinGuide expects {CHROMA_DISTANCE_SPACE!r}. "
                "Re-index this collection using POST /api/sources/reindex or "
                "`python backend/scripts/ingest_documents.py --reindex`; "
                "the re-index process makes a project-local backup first."
            )

        stored_model = metadata.get("embedding_model")
        if stored_model and stored_model != self.embedding_fn.model_name:
            raise IncompatibleCollectionError(
                f"Chroma collection {COLLECTION_NAME!r} uses embedding model "
                f"{stored_model!r}, but the configured model is "
                f"{self.embedding_fn.model_name!r}. Re-index this collection "
                "using POST /api/sources/reindex or "
                "`python backend/scripts/ingest_documents.py --reindex`; "
                "the re-index process makes a project-local backup first."
            )

        stored = self.collection.get(limit=1, include=["embeddings"])
        embeddings = stored.get("embeddings")
        if embeddings is None or len(embeddings) == 0:
            raise IncompatibleCollectionError(
                f"Chroma collection {COLLECTION_NAME!r} contains {count} records "
                "but no readable embeddings. Re-index this collection through "
                "the documented backup-protected process."
            )

        stored_dimension = len(embeddings[0])
        expected_dimension = self.embedding_fn.dimension
        if stored_dimension != expected_dimension:
            raise IncompatibleCollectionError(
                f"Chroma collection {COLLECTION_NAME!r} stores "
                f"{stored_dimension}-dimensional vectors, while configured "
                f"model {self.embedding_fn.model_name!r} produces "
                f"{expected_dimension}-dimensional vectors. Chroma cannot query "
                "this incompatible index. Re-index this collection using "
                "POST /api/sources/reindex or "
                "`python backend/scripts/ingest_documents.py --reindex`; "
                "the re-index process makes a project-local backup first."
            )

    def _embed_chunks(self, chunks: list[dict[str, Any]]) -> list[list[float]]:
        vectors = self.embedding_fn.embed_documents([chunk["text"] for chunk in chunks])
        if len(vectors) != len(chunks):
            raise RuntimeError(
                f"Embedding model returned {len(vectors)} vectors for "
                f"{len(chunks)} document chunks."
            )
        self._check_embedding_vectors(vectors)
        return vectors

    def initialize(self) -> None:
        with self._lock:
            if self._initialized:
                return
            self._connect()
            self._validate_collection()
            if self.collection.count() == 0:
                chunks = load_all_document_chunks()
                if chunks:
                    vectors = self._embed_chunks(chunks)
                    self.collection.upsert(
                        ids=[chunk["id"] for chunk in chunks],
                        documents=[chunk["text"] for chunk in chunks],
                        metadatas=[chunk["metadata"] for chunk in chunks],
                        embeddings=vectors,
                    )
                    self._validate_collection()
            self._initialized = True

    def _backup_persistence_directory(self) -> Path | None:
        persist_dir = resolve_chroma_persist_dir()
        project_dir = PROJECT_DIR.resolve()
        if persist_dir == project_dir or project_dir not in persist_dir.parents:
            raise RuntimeError(
                "Refusing to re-index because CHROMA_PERSIST_DIR resolves outside "
                f"the FinGuide project: {persist_dir}. Configure a project-local "
                "directory before replacing this collection."
            )

        if not persist_dir.exists():
            return None
        if not persist_dir.is_dir():
            raise RuntimeError(
                f"CHROMA_PERSIST_DIR is not a directory: {persist_dir}"
            )

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = persist_dir.with_name(f"{persist_dir.name}.backup-{timestamp}")
        shutil.copytree(persist_dir, backup_dir)
        return backup_dir

    def reindex_all(self) -> dict[str, Any]:
        """Replace only the FinGuide collection after validating and backing it up."""
        with self._lock:
            self._connect()
            chunks = load_all_document_chunks()
            if not chunks:
                raise ValueError(
                    f"No readable PDF chunks were found in {settings.DOCUMENTS_DIR}; "
                    "the existing collection was left unchanged."
                )

            vectors = self._embed_chunks(chunks)
            backup_dir = self._backup_persistence_directory()
            operation_id = uuid.uuid4().hex
            staging_name = f"finguide_rebuild_{operation_id}"
            previous_name = f"finguide_previous_{operation_id}"
            metadata = {
                "description": "FinGuide AI document chunks",
                "embedding_model": self.embedding_fn.model_name,
                "embedding_dimension": self.embedding_fn.dimension,
                "hnsw:space": CHROMA_DISTANCE_SPACE,
            }
            staging = self.chroma_client.create_collection(
                name=staging_name,
                metadata=metadata,
                embedding_function=None,
            )
            original_renamed = False

            try:
                staging.upsert(
                    ids=[chunk["id"] for chunk in chunks],
                    documents=[chunk["text"] for chunk in chunks],
                    metadatas=[chunk["metadata"] for chunk in chunks],
                    embeddings=vectors,
                )
                if staging.count() != len(chunks):
                    raise RuntimeError(
                        f"Staging collection contains {staging.count()} chunks; "
                        f"expected {len(chunks)}."
                    )
                staged_vectors = staging.get(limit=1, include=["embeddings"]).get(
                    "embeddings"
                )
                if (
                    staged_vectors is None
                    or len(staged_vectors) == 0
                    or len(staged_vectors[0]) != self.embedding_fn.dimension
                ):
                    raise RuntimeError(
                        "Staged collection failed its embedding dimension check."
                    )

                self.collection.modify(name=previous_name)
                original_renamed = True
                staging.modify(name=COLLECTION_NAME)
                self.collection = self.chroma_client.get_collection(
                    name=COLLECTION_NAME,
                    embedding_function=None,
                )
                self._validate_collection()
            except Exception as exc:
                if original_renamed:
                    try:
                        collection_names = {
                            collection.name
                            for collection in self.chroma_client.list_collections()
                        }
                        if COLLECTION_NAME in collection_names:
                            self.chroma_client.get_collection(
                                name=COLLECTION_NAME,
                                embedding_function=None,
                            ).modify(name=staging_name)
                        self.chroma_client.get_collection(
                            name=previous_name,
                            embedding_function=None,
                        ).modify(name=COLLECTION_NAME)
                    except Exception as restore_error:
                        raise RuntimeError(
                            "Re-indexing failed and the previous collection could "
                            f"not be restored in place: {restore_error}. Its "
                            f"project-local backup is at {backup_dir}."
                        ) from exc
                cleanup_error = None
                try:
                    self.chroma_client.delete_collection(name=staging_name)
                except Exception as cleanup_exception:
                    cleanup_error = cleanup_exception
                if cleanup_error:
                    raise RuntimeError(
                        "Re-indexing failed; the previous collection was not "
                        "reported as replaced, but the staging collection "
                        f"{staging_name!r} could not be cleaned up: {cleanup_error}"
                    ) from exc
                raise

            self._initialized = True
            document_count = len({chunk["metadata"]["document_id"] for chunk in chunks})
            return {
                "documents_indexed": document_count,
                "total_chunks": len(chunks),
                "backup_path": str(backup_dir) if backup_dir else None,
            }

    def retrieve(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        with self._lock:
            self.initialize()
            count = self.collection.count()
            if count == 0:
                return []

            query_embedding = self.embedding_fn.embed_query(query)
            self._check_embedding_vectors([query_embedding])
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"],
            )

            retrieved = []
            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            for index, document in enumerate(docs):
                distance = distances[index] if index < len(distances) else None
                relevance_score = (
                    cosine_similarity_from_squared_l2(float(distance))
                    if distance is not None
                    else 0.0
                )
                if relevance_score < RETRIEVAL_SCORE_THRESHOLD:
                    continue
                retrieved.append(
                    {
                        "id": ids[index] if index < len(ids) else None,
                        "text": document,
                        "metadata": metas[index],
                        "score": relevance_score,
                    }
                )
            return retrieved

    def get_sources_overview(self) -> list[dict[str, Any]]:
        with self._lock:
            self.initialize()
            result = self.collection.get(include=["metadatas"])
            documents: dict[str, dict[str, Any]] = {}
            for metadata in result.get("metadatas") or []:
                document_id = metadata.get("document_id", metadata.get("filename", "unknown"))
                document = documents.setdefault(
                    document_id,
                    {
                        "document_id": document_id,
                        "filename": metadata.get("filename", "Unknown"),
                        "title": metadata.get("document_title", "Unknown source"),
                        "publisher": metadata.get("publisher"),
                        "authority": metadata.get("authority"),
                        "source_url": metadata.get("source_url"),
                        "published_date": metadata.get("published_date"),
                        "reference_status": metadata.get("reference_status", "unknown"),
                        "content_type": metadata.get("content_type", "unknown"),
                        "is_generated_summary": metadata.get("is_generated_summary"),
                        "verification_method": metadata.get("verification_method"),
                        "verified_by": metadata.get("verified_by"),
                        "sha256": metadata.get("sha256"),
                        "provenance_note": metadata.get("provenance_note"),
                        "last_verified": metadata.get("last_verified"),
                        "pages_count": 0,
                        "chunks_count": 0,
                        "_pages": set(),
                    },
                )
                document["chunks_count"] += 1
                page = metadata.get("page_number")
                if page is not None:
                    document["_pages"].add(page)

            overview = []
            for document in documents.values():
                document["pages_count"] = len(document.pop("_pages"))
                document["document_title"] = document["title"]
                if not is_verified_official_metadata(document, require_page=False):
                    document["source_url"] = None
                    reasons = "; ".join(
                        official_metadata_verification_issues(
                            document, require_page=False
                        )
                    )
                    note = (
                        "Reference URL withheld because official-source "
                        f"verification failed: {reasons}."
                    )
                    document["provenance_note"] = " ".join(
                        part
                        for part in (
                            document.get("provenance_note"),
                            note,
                        )
                        if part
                    )
                document.pop("document_title", None)
                document.pop("sha256", None)
                overview.append(document)
            return overview


vector_store = VectorStoreManager()
