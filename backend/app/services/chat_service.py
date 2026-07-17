"""Chat with financial reports: RAG retrieval + grounded answer with citations."""
import uuid

from app.agents.llm import get_llm
from app.models.models import ChatHistory
from app.prompts import templates as T
from app.rag.pipeline import build_context, retrieve
from app.repositories.repositories import ChatRepository
from app.schemas.schemas import ChatResponse, Citation


def answer_question(db, user_id: str, session_id: str | None, question: str) -> ChatResponse:
    session_id = session_id or str(uuid.uuid4())
    repo = ChatRepository(db)

    chunks = retrieve(question, k=8)
    context = build_context(chunks)
    history = "\n".join(f"{m.role}: {m.content}" for m in repo.history(session_id))

    llm = get_llm(temperature=0.2)
    resp = llm.invoke([("system", T.CHAT_SYSTEM),
                       ("user", T.CHAT_USER.format(context=context, history=history, question=question))])
    answer = resp.content

    citations = [Citation(document_id=c.document_id, filename=c.filename,
                          page_number=c.page_number, snippet=c.content[:200]) for c in chunks[:4]]

    repo.add(ChatHistory(user_id=user_id, session_id=session_id, role="user", content=question))
    repo.add(ChatHistory(user_id=user_id, session_id=session_id, role="assistant",
                         content=answer, citations=[c.model_dump() for c in citations]))
    return ChatResponse(session_id=session_id, answer=answer, citations=citations)
