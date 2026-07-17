"""PDF parsing: digital-vs-scanned detection, text, tables, metadata, OCR fallback."""
import logging
from dataclasses import dataclass, field

import fitz  # PyMuPDF
import pdfplumber

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ParsedPage:
    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)


@dataclass
class ParsedDocument:
    pages: list[ParsedPage]
    metadata: dict
    is_scanned: bool

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.text for p in self.pages)


def detect_scanned(path: str, sample_pages: int = 3) -> bool:
    """A PDF is treated as scanned when its first pages contain almost no extractable text."""
    with fitz.open(path) as doc:
        pages = min(sample_pages, len(doc))
        chars = sum(len(doc[i].get_text().strip()) for i in range(pages))
    return chars < 50 * pages


def _ocr_azure(path: str) -> list[ParsedPage]:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    client = DocumentIntelligenceClient(settings.azure_di_endpoint,
                                        AzureKeyCredential(settings.azure_di_api_key))
    with open(path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", body=f)
    result = poller.result()
    pages = []
    for i, page in enumerate(result.pages, start=1):
        text = "\n".join(line.content for line in (page.lines or []))
        pages.append(ParsedPage(page_number=i, text=text))
    return pages


def _ocr_tesseract(path: str) -> list[ParsedPage]:
    import pytesseract
    from PIL import Image
    import io

    pages = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            pages.append(ParsedPage(page_number=i, text=pytesseract.image_to_string(img)))
    return pages


def parse_pdf(path: str) -> ParsedDocument:
    is_scanned = detect_scanned(path)

    with fitz.open(path) as doc:
        metadata = {k: v for k, v in (doc.metadata or {}).items() if v}
        metadata["page_count"] = len(doc)

    if is_scanned:
        logger.info("Scanned PDF detected, running OCR via %s", settings.ocr_provider)
        try:
            pages = _ocr_azure(path) if settings.ocr_provider == "azure_di" and settings.azure_di_api_key \
                else _ocr_tesseract(path)
        except Exception:
            logger.exception("Primary OCR failed, falling back to Tesseract")
            pages = _ocr_tesseract(path)
        return ParsedDocument(pages=pages, metadata=metadata, is_scanned=True)

    pages: list[ParsedPage] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            tables = []
            for tbl in page.extract_tables() or []:
                tables.append([[(c or "").strip() for c in row] for row in tbl])
            pages.append(ParsedPage(page_number=i, text=text, tables=tables))
    return ParsedDocument(pages=pages, metadata=metadata, is_scanned=False)


def table_to_markdown(table: list[list[str]]) -> str:
    if not table:
        return ""
    header, *rows = table
    lines = ["| " + " | ".join(header) + " |",
             "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)
