"""Thin data-access layer so services never touch the ORM session directly."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (AnalysisResult, AuditLog, ChatHistory, Chunk,
                               DashboardData, Document, FinancialMetric, User)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, doc: Document) -> Document:
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get(self, doc_id: str) -> Document | None:
        return self.db.get(Document, doc_id)

    def list_all(self, limit: int = 100) -> list[Document]:
        return list(self.db.scalars(select(Document).order_by(Document.created_at.desc()).limit(limit)))

    def update(self, doc: Document) -> Document:
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def add_chunks(self, chunks: list[Chunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()


class MetricRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, metric: FinancialMetric) -> None:
        existing = self.db.scalar(
            select(FinancialMetric).where(
                FinancialMetric.fiscal_period == metric.fiscal_period,
                FinancialMetric.metric_name == metric.metric_name,
            )
        )
        if existing:
            existing.value = metric.value
            existing.unit = metric.unit
            existing.source = metric.source
        else:
            self.db.add(metric)
        self.db.commit()

    def by_period(self, period: str) -> list[FinancialMetric]:
        return list(self.db.scalars(select(FinancialMetric).where(FinancialMetric.fiscal_period == period)))

    def series(self, metric_name: str) -> list[FinancialMetric]:
        return list(self.db.scalars(
            select(FinancialMetric).where(FinancialMetric.metric_name == metric_name)
            .order_by(FinancialMetric.fiscal_period)
        ))


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, result: AnalysisResult) -> None:
        self.db.add(result)
        self.db.commit()

    def by_run(self, run_id: str) -> list[AnalysisResult]:
        return list(self.db.scalars(select(AnalysisResult).where(AnalysisResult.run_id == run_id)))

    def latest_by_agent(self, agent: str) -> AnalysisResult | None:
        return self.db.scalar(
            select(AnalysisResult).where(AnalysisResult.agent == agent)
            .order_by(AnalysisResult.created_at.desc()).limit(1)
        )


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, page: str, payload: dict) -> None:
        self.db.add(DashboardData(page=page, payload=payload))
        self.db.commit()

    def latest(self, page: str) -> DashboardData | None:
        return self.db.scalar(
            select(DashboardData).where(DashboardData.page == page)
            .order_by(DashboardData.generated_at.desc()).limit(1)
        )


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: str | None, action: str, entity: str = "", entity_id: str = "",
            detail: dict | None = None, ip: str = "") -> None:
        self.db.add(AuditLog(user_id=user_id, action=action, entity=entity,
                             entity_id=entity_id, detail=detail or {}, ip=ip))
        self.db.commit()


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, msg: ChatHistory) -> None:
        self.db.add(msg)
        self.db.commit()

    def history(self, session_id: str, limit: int = 20) -> list[ChatHistory]:
        rows = list(self.db.scalars(
            select(ChatHistory).where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.desc()).limit(limit)
        ))
        return list(reversed(rows))
