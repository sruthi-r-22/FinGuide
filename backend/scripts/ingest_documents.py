"""FinGuide AI's explicit, backup-protected PDF collection re-index command."""
import argparse
import sys
from pathlib import Path

# Add the project root so the script works when launched from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.core.config import resolve_chroma_persist_dir, settings
from backend.app.rag.retriever import vector_store


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild only FinGuide AI's finguide_banking_docs collection. "
            "A project-local Chroma directory is backed up before replacement."
        )
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="explicitly rebuild the FinGuide AI collection",
    )
    args = parser.parse_args()
    if not args.reindex:
        parser.error("pass --reindex to explicitly replace the FinGuide AI collection")

    print(f"Documents directory: {settings.DOCUMENTS_DIR}")
    print(f"Chroma persistence directory: {resolve_chroma_persist_dir()}")
    print("Reading PDFs and validating embeddings before replacing the collection...")
    result = vector_store.reindex_all()
    print(
        f"Re-index completed: {result['documents_indexed']} documents, "
        f"{result['total_chunks']} chunks."
    )
    if result["backup_path"]:
        print(f"Previous Chroma data backed up to: {result['backup_path']}")
    else:
        print("No prior Chroma directory existed, so no backup was needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
