from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from src.config import get_settings
from src.rag.pdf_loader import load_pdf_documents
from src.schemas import RetrievedChunk, SourceDocument
from src.utils.openai_client import get_openai_client
from src.utils.text import chunk_text


class VectorIndex:
    """Persistent FAISS cosine-similarity index using OpenAI embeddings.

    FAISS stores the normalized embedding matrix in ``index.faiss``. Chunk text
    and citation metadata are stored beside it in ``chunks.json``. OpenAI is
    used only to create document and query embeddings; retrieval is local.
    """

    INDEX_FILENAME = "index.faiss"
    CHUNKS_FILENAME = "chunks.json"
    META_FILENAME = "index_meta.json"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.settings.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.settings.index_dir / self.INDEX_FILENAME
        self.chunks_path = self.settings.index_dir / self.CHUNKS_FILENAME
        self.meta_path = self.settings.index_dir / self.META_FILENAME

    def exists(self) -> bool:
        if not self.index_path.is_file() or not self.chunks_path.is_file():
            return False
        try:
            index = faiss.read_index(str(self.index_path))
            chunks = json.loads(self.chunks_path.read_text(encoding="utf-8"))
            return index.ntotal > 0 and index.ntotal == len(chunks)
        except Exception:
            return False

    def count(self) -> int:
        if not self.exists():
            return 0
        return int(faiss.read_index(str(self.index_path)).ntotal)

    @staticmethod
    def _chunk_record(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "chunk_id": str(item["chunk_id"]),
            "document_id": str(item["document_id"]),
            "title": str(item["title"]),
            "url": str(item.get("url") or ""),
            "category": str(item.get("category") or "University information"),
            "text": str(item["text"]),
            "source_type": str(item.get("source_type") or "pdf"),
            "filename": str(item.get("filename") or ""),
            "page": int(item.get("page") or 0) or None,
        }

    def build(self, documents: list[SourceDocument]) -> int:
        chunks: list[dict[str, Any]] = []
        for doc in documents:
            for i, text in enumerate(chunk_text(doc.text)):
                chunks.append(
                    self._chunk_record(
                        {
                            "chunk_id": f"{doc.id}-chunk-{i}",
                            "document_id": doc.id,
                            "title": doc.title,
                            "url": doc.url,
                            "category": doc.category,
                            "text": text,
                            "source_type": doc.source_type,
                            "filename": doc.filename,
                            "page": doc.page,
                        }
                    )
                )

        if not chunks:
            raise ValueError(
                "No PDF text chunks were produced. Add PDF files to data/pdfs or run "
                "python scripts/download_official_pdfs.py."
            )

        client = get_openai_client()
        vectors: list[list[float]] = []
        batch_size = 96
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            response = client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=[item["text"] for item in batch],
            )
            vectors.extend(row.embedding for row in response.data)

        matrix = np.asarray(vectors, dtype="float32")
        if matrix.ndim != 2 or matrix.shape[0] != len(chunks):
            raise RuntimeError("The embedding service returned an unexpected vector matrix.")
        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)

        # Write a complete replacement in a temporary directory, then move each
        # file into place. This prevents a failed re-embed from deleting the old
        # usable index before the new one has been created.
        temp_dir = self.settings.index_dir / ".building"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_index = temp_dir / self.INDEX_FILENAME
        temp_chunks = temp_dir / self.CHUNKS_FILENAME
        temp_meta = temp_dir / self.META_FILENAME
        faiss.write_index(index, str(temp_index))
        temp_chunks.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
        temp_meta.write_text(
            json.dumps(
                {
                    "embedding_model": self.settings.openai_embedding_model,
                    "dimension": int(matrix.shape[1]),
                    "chunk_count": len(chunks),
                    "metric": "cosine_similarity_via_normalized_inner_product",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        for source, destination in (
            (temp_index, self.index_path),
            (temp_chunks, self.chunks_path),
            (temp_meta, self.meta_path),
        ):
            source.replace(destination)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return len(chunks)

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        if not self.exists():
            raise FileNotFoundError("FAISS knowledge base is missing or incomplete. Re-embed the PDFs.")

        index = faiss.read_index(str(self.index_path))
        chunks = json.loads(self.chunks_path.read_text(encoding="utf-8"))
        client = get_openai_client()
        response = client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=[query],
        )
        query_vector = np.asarray([response.data[0].embedding], dtype="float32")
        if query_vector.shape[1] != index.d:
            raise RuntimeError(
                "The query embedding dimension differs from the saved FAISS index. "
                "Re-embed the PDFs after changing OPENAI_EMBEDDING_MODEL."
            )
        faiss.normalize_L2(query_vector)
        limit = min(top_k or self.settings.top_k, index.ntotal)
        scores, positions = index.search(query_vector, limit)

        retrieved: list[RetrievedChunk] = []
        for score, position in zip(scores[0], positions[0]):
            if position < 0:
                continue
            item = chunks[int(position)]
            retrieved.append(
                RetrievedChunk(
                    chunk_id=item["chunk_id"],
                    document_id=item["document_id"],
                    title=item["title"],
                    url=item.get("url", ""),
                    category=item.get("category", "University information"),
                    text=item["text"],
                    score=float(score),
                    source_type=item.get("source_type", "pdf"),
                    filename=item.get("filename", ""),
                    page=item.get("page"),
                )
            )
        return retrieved


def load_documents(path: Path | None = None) -> list[SourceDocument]:
    settings = get_settings()
    documents = load_pdf_documents(settings.pdf_dir, settings.pdf_manifest_path)
    if settings.use_manual_dataset:
        data_path = path or settings.raw_data_path
        if data_path.exists():
            raw = json.loads(data_path.read_text(encoding="utf-8"))
            documents.extend(SourceDocument(**item) for item in raw)
    return documents
