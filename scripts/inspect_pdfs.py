from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    settings = get_settings()
    manifest = {
        item["filename"]: item
        for item in json.loads(settings.pdf_manifest_path.read_text(encoding="utf-8"))
    }
    files = sorted(settings.pdf_dir.glob("*.pdf"))
    if not files:
        raise SystemExit(f"No PDFs found in {settings.pdf_dir}")

    print(f"PDF dataset directory: {settings.pdf_dir}")
    print(f"Documents: {len(files)}")
    total_pages = 0
    for path in files:
        reader = PdfReader(str(path))
        pages = len(reader.pages)
        total_pages += pages
        title = manifest.get(path.name, {}).get("title", path.stem)
        print(f"- {title}")
        print(f"  file: {path.name}")
        print(f"  pages: {pages}")
        print(f"  size_mb: {path.stat().st_size / (1024 * 1024):.2f}")
        print(f"  sha256: {sha256(path)}")
    print(f"Total pages: {total_pages}")


if __name__ == "__main__":
    main()
