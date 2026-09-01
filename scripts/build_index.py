import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rag.index import VectorIndex, load_documents

if __name__ == "__main__":
    docs = load_documents()
    count = VectorIndex().build(docs)
    print(f"Built vector index with {count} chunks from {len(docs)} documents.")
