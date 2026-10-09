from functools import lru_cache
from typing import Any

from backend.app.core.config import settings


class SentenceTransformerEmbedding:
    """Shared embedding adapter for document and query vectors."""

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is required for FinGuide RAG. "
                "Install backend/requirements.txt in the backend environment."
            ) from exc

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self.dimension = self._model.get_embedding_dimension()
        if not isinstance(self.dimension, int) or self.dimension <= 0:
            raise RuntimeError(
                f"Embedding model {model_name!r} reported invalid dimension "
                f"{self.dimension!r}."
            )

    def embed_query(self, text: str) -> list[float]:
        return self._encode([text])[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._encode(texts)

    def _encode(self, texts: list[str]) -> list[list[float]]:
        encoded: Any = self._model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        vectors = encoded.tolist()
        if len(vectors) != len(texts) or any(
            len(vector) != self.dimension for vector in vectors
        ):
            raise RuntimeError(
                f"Embedding model {self.model_name!r} returned an unexpected "
                f"vector shape; expected {len(texts)} vectors of "
                f"{self.dimension} dimensions."
            )
        return vectors


@lru_cache(maxsize=1)
def get_embedding_function() -> SentenceTransformerEmbedding:
    """Load the configured model once; never substitute incompatible vectors."""
    return SentenceTransformerEmbedding(settings.EMBEDDING_MODEL)
