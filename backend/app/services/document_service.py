"""End-to-end document processing pipeline (runs in Celery worker):
validate → detect scanned → text/tables → OCR → chunk → embed → vector store → metadata."""
import logging
import os

from app.analytics.kpi_engine import match_line_items
from app.config.settings import get_settings
from app.database.session import SessionLocal
from app.models.models import Chunk, DocStatus, Document, Embedding, FinancialMetric
from app.parser.excel_parser import parse_excel
from app.parser.pdf_parser import parse_pdf, table_to_markdown
from app.rag.chunker import ChunkPayload, chunk_table, chunk_text
from app.rag.pipeline import index_chunks
from app.repositories.repositories import MetricRepository

logger = logging.getLogger(__name__)
settings = get_settings()


def save_upload(data: bytes, filename: str) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, filename)
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(path):  # simple versioned filenames
        path = f"{base}_v{n}{ext}"
        n += 1
    with open(path, "wb") as f:
        f.write(data)
    return path


def process_document(document_id: str) -> None:
    with SessionLocal() as db:
        doc = db.get(Document, document_id)
        if not doc:
            logger.error("Document %s not found", document_id)
            return
        try:
            doc.status = DocStatus.processing
            db.commit()

            payloads: list[ChunkPayload] = []
            line_items: dict[str, float] = {}

            if doc.storage_path.lower().endswith(".pdf"):
                parsed = parse_pdf(doc.storage_path)
                doc.is_scanned = parsed.is_scanned
                doc.page_count = parsed.metadata.get("page_count", 0)
                doc.meta = {**doc.meta, **parsed.metadata}
                for page in parsed.pages:
                    payloads.extend(chunk_text(page.text, page.page_number))
                    for table in page.tables:
                        payloads.append(chunk_table(table_to_markdown(table), page.page_number))
            else:
                for sheet in parse_excel(doc.storage_path):
                    payloads.append(chunk_table(sheet.markdown, 0, sheet=sheet.name))
                    line_items.update(sheet.line_items)

            chunks = [
                Chunk(document_id=doc.id, chunk_index=i, page_number=p.page_number,
                      content=p.content, content_type=p.content_type, meta=p.meta)
                for i, p in enumerate(payloads) if p.content.strip()
            ]
            db.add_all(chunks)
            db.commit()

            index_chunks(
                [c.id for c in chunks],
                [c.content for c in chunks],
                [{"document_id": doc.id, "filename": doc.filename,
                  "page_number": c.page_number, "content": c.content[:2000],
                  "doc_type": doc.doc_type, "fiscal_period": doc.fiscal_period} for c in chunks],
            )
            db.add_all([Embedding(chunk_id=c.id, vector_store=settings.vector_store) for c in chunks])

            # Persist deterministic line items as metrics keyed by fiscal period
            if line_items and doc.fiscal_period:
                repo = MetricRepository(db)
                for name, value in match_line_items(line_items).items():
                    repo.upsert(FinancialMetric(document_id=doc.id, fiscal_period=doc.fiscal_period,
                                                metric_name=name, value=value, source="parser"))

            doc.status = DocStatus.embedded
            db.commit()
            logger.info("Document %s processed: %d chunks", doc.id, len(chunks))
        except Exception as exc:
            logger.exception("Processing failed for %s", document_id)
            doc.status = DocStatus.failed
            doc.error = str(exc)[:2000]
            db.commit()
            raise
