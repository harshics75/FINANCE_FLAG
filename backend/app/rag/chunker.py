"""Semantic chunking: paragraph-aware splitting with overlap; tables kept whole."""
from dataclasses import dataclass, field


@dataclass
class ChunkPayload:
    content: str
    page_number: int
    content_type: str = "text"
    meta: dict = field(default_factory=dict)


def chunk_text(text: str, page_number: int, max_chars: int = 1600, overlap: int = 200) -> list[ChunkPayload]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[ChunkPayload] = []
    buf = ""
    for para in paragraphs:
        if len(buf) + len(para) + 2 <= max_chars:
            buf = f"{buf}\n\n{para}".strip()
        else:
            if buf:
                chunks.append(ChunkPayload(content=buf, page_number=page_number))
            buf = (buf[-overlap:] + "\n\n" + para).strip() if overlap and buf else para
    if buf:
        chunks.append(ChunkPayload(content=buf, page_number=page_number))
    return chunks


def chunk_table(markdown: str, page_number: int, sheet: str = "") -> ChunkPayload:
    return ChunkPayload(content=markdown, page_number=page_number,
                        content_type="table", meta={"sheet": sheet})
