from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import require_any, require_finance
from app.database.session import get_db
from app.models.models import Document, User
from app.parser.validator import classify_doc_type, validate_upload
from app.repositories.repositories import AuditLogRepository, DocumentRepository
from app.schemas.schemas import ChunkOut, DocumentOut
from app.services.document_service import save_upload
from app.services.worker import process_document_task

router = APIRouter()


@router.post("/upload", response_model=DocumentOut)
async def upload_document(request: Request, file: UploadFile,
                          fiscal_period: str = Form(""),
                          user: User = Depends(require_finance),
                          db: Session = Depends(get_db)):
    """Upload a PDF or Excel financial document. Processing runs asynchronously."""
    data = await validate_upload(file)
    path = save_upload(data, file.filename or "upload.bin")
    doc = DocumentRepository(db).create(Document(
        owner_id=user.id, filename=file.filename or "upload",
        doc_type=classify_doc_type(file.filename or ""),
        fiscal_period=fiscal_period, mime_type=file.content_type or "",
        size_bytes=len(data), storage_path=path,
    ))
    AuditLogRepository(db).log(user.id, "document.upload", "document", doc.id,
                               {"filename": doc.filename})
    try:
        process_document_task.delay(doc.id)
    except Exception:
        # Redis unavailable (e.g. local dev without worker) → process synchronously
        from app.services.document_service import process_document
        process_document(doc.id)
        db.refresh(doc)
    return doc


@router.get("", response_model=list[DocumentOut], dependencies=[Depends(require_any)])
def list_documents(db: Session = Depends(get_db)):
    return DocumentRepository(db).list_all()


@router.get("/{document_id}", response_model=DocumentOut, dependencies=[Depends(require_any)])
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = DocumentRepository(db).get(document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/{document_id}/chunks", response_model=list[ChunkOut], dependencies=[Depends(require_any)])
def get_chunks(document_id: str, db: Session = Depends(get_db)):
    doc = DocumentRepository(db).get(document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return sorted(doc.chunks, key=lambda c: c.chunk_index)[:200]
