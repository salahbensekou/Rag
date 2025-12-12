from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR.parent / "docs"
VECTOR_DB_DIR = BASE_DIR / "data" / "chroma"

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docs")
