from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from .config import DOCS_DIR, VECTOR_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME


def load_documents():
    docs = []
    for path in DOCS_DIR.glob("**/*"):
        if path.suffix.lower() in [".pdf", ".txt", ".md"]:
            if path.suffix.lower() == ".pdf":
                reader = PdfReader(str(path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append({"path": path, "text": text})
    return docs


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def main():
    print(f"Loading docs from: {DOCS_DIR}")
    documents = load_documents()
    print(f"Found {len(documents)} documents")

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)  # keeps option to precompute embeddings

    ids = []
    texts = []
    metadatas = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['path'].name}-{i}"
            ids.append(chunk_id)
            texts.append(chunk)
            metadatas.append(
                {
                    "source": doc["path"].name,
                    "chunk_id": i,
                }
            )

    print(f"Total chunks: {len(texts)}")

    # Simple mode: let Chroma compute embeddings internally
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )

    print("Ingestion done.")


if __name__ == "__main__":
    main()
