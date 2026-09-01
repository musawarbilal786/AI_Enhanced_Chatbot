import re


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def chunk_text(text: str, chunk_size: int = 1100, overlap: int = 180) -> list[str]:
    text = clean_text(text)
    if len(text) <= chunk_size:
        return [text] if text else []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            split = max(text.rfind(". ", start, end), text.rfind("; ", start, end))
            if split > start + chunk_size // 2:
                end = split + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks
