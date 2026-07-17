from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_any
from app.database.session import get_db
from app.models.models import ChatHistory, User
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.chat_service import answer_question

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, user: User = Depends(require_any), db: Session = Depends(get_db)):
    """Ask questions like: Why did profit decline? Compare FY2024 vs FY2025. Summarize the annual report."""
    return answer_question(db, user.id, payload.session_id, payload.message)


@router.get("/sessions/{session_id}")
def history(session_id: str, user: User = Depends(require_any), db: Session = Depends(get_db)):
    rows = (db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id, ChatHistory.user_id == user.id)
            .order_by(ChatHistory.created_at).all())
    return [{"role": r.role, "content": r.content, "citations": r.citations} for r in rows]
