from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader

from src.schemas import SourceDocument
from src.utils.text import clean_text


def _document_id(path: Path) -> str:
    digest = hashlib.sha1(path.name.encode("utf-8")).hexdigest()[:10]
    return f"pdf-{digest}"


def load_manifest(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding="utf-8"))
    return {item["filename"]: item for item in records}


def load_pdf_documents(pdf_dir: Path, manifest_path: Path) -> list[SourceDocument]:
    """Extract one SourceDocument per non-empty PDF page.

    Page-level documents produce precise retrieval and citations such as
    `Student Terms and Conditions, page 14`.
    """
    manifest = load_manifest(manifest_path)
    documents: list[SourceDocument] = []

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        metadata = manifest.get(pdf_path.name, {})
        reader = PdfReader(str(pdf_path))
        title = metadata.get("title") or (reader.metadata.title if reader.metadata else None) or pdf_path.stem
        base_id = metadata.get("id") or _document_id(pdf_path)
        source_url = metadata.get("url", "")
        category = metadata.get("category", "University PDF")
        campus_scope = metadata.get("campus_scope", "Ulster University / London branch campus")
        last_verified = metadata.get("last_verified", "")

        for page_number, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")
            if len(text) < 40:
                continue
            documents.append(
                SourceDocument(
                    id=f"{base_id}-p{page_number}",
                    title=title,
                    category=category,
                    campus_scope=campus_scope,
                    url=source_url,
                    text=text,
                    last_verified=last_verified,
                    source_type="pdf",
                    filename=pdf_path.name,
                    page=page_number,
                )
            )
    return documents


def pdf_inventory(pdf_dir: Path) -> Iterable[Path]:
    return sorted(pdf_dir.glob("*.pdf"))
