from pathlib import Path
from src.config import get_settings
from src.ingestion import ingest_directory, SUPPORTED
from src.vectorstore import ensure_index

ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = ROOT / "documents"


def main():
    s = get_settings()

    if not s.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")
    if not s.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is missing. Add it to your .env file.")

    print("=" * 68)
    print("CloudOps Sentinel - Pinecone Knowledge Base Ingestion")
    print("=" * 68)
    print(f"OpenAI embedding model : {s.embedding_model}")
    print(f"Embedding dimension    : {s.embedding_dimension}")
    print(f"Pinecone index         : {s.pinecone_index_name}")
    print(f"Pinecone namespace     : {s.pinecone_namespace}")
    print(f"Documents directory    : {DOCUMENTS_DIR}")
    print()

    ensure_index()
    print("[1/2] Pinecone index is ready.")

    files = [
        p for p in sorted(DOCUMENTS_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED
    ] if DOCUMENTS_DIR.exists() else []

    if not files:
        print("[2/2] No supported documents found. Add files to ./documents and run again.")
        return

    print(f"[2/2] Ingesting {len(files)} document(s)...")
    for path in files:
        print(f"      - {path.name}")

    total_chunks = ingest_directory(DOCUMENTS_DIR)

    print()
    print("Knowledge base is ready.")
    print(f"Indexed chunks: {total_chunks}")
    print(f"Index: {s.pinecone_index_name}")
    print(f"Namespace: {s.pinecone_namespace}")


if __name__ == "__main__":
    main()
