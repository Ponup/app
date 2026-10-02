import json
from io import BytesIO

from pypdf import PdfReader

INDEXED_MIME_TYPES = {"text/markdown", "text/plain", "application/json", "application/pdf"}


def is_image(mime_type: str) -> bool:
    return mime_type.lower().startswith("image/")


def extract(data: bytes, mime_type: str) -> str | None:
    if mime_type not in INDEXED_MIME_TYPES:
        return None
    if mime_type == "application/pdf":
        return "\n\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data))).strip()
    text = data.decode("utf-8")
    if mime_type == "application/json":
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    return text


def chunk(text: str, size: int = 3200, overlap: int = 400) -> list[str]:
    """Chunk near paragraph boundaries; defaults approximate 800/100 tokens."""
    text = text.strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind("\n\n", start + size // 2, end)
            if boundary > start:
                end = boundary
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return [value for value in chunks if value]
