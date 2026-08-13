"""ORM models: Users, Documents, Chunks, Embeddings, FinancialMetrics,
AnalysisResults, DashboardData, AuditLogs, ChatHistory."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Enum, Float, ForeignKey, Integer, LargeBinary, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, enum.Enum):
    admin = "admin"
    finance_manager = "finance_manager"
    auditor = "auditor"


class DocStatus(str, enum.Enum):
    uploaded = "uploaded"
    validating = "validating"
    processing = "processing"
    embedded = "embedded"
    analyzed = "analyzed"
    failed = "failed"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.finance_manager)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    documents: Mapped[list["Document"]] = relationship(back_populates="owner")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    doc_type: Mapped[str] = mapped_column(String(64), default="unknown")
    fiscal_period: Mapped[str] = mapped_column(String(32), default="")
    mime_type: Mapped[str] = mapped_column(String(128), default="")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024))
    # Only populated when STORAGE_PROVIDER=db (no shared disk between backend/worker
    # and no object-storage account available) — file bytes live on the row itself.
    content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    status: Mapped[DocStatus] = mapped_column(Enum(DocStatus), default=DocStatus.uploaded)
    is_scanned: Mapped[bool] = mapped_column(default=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped[User] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(32), default="text")  # text | table
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    document: Mapped[Document] = relationship(back_populates="chunks")
    embedding: Mapped["Embedding"] = relationship(back_populates="chunk", uselist=False, cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chunk_id: Mapped[str] = mapped_column(ForeignKey("chunks.id"), unique=True, index=True)
    vector_store: Mapped[str] = mapped_column(String(32), default="faiss")
    external_id: Mapped[str] = mapped_column(String(128), default="")
    dim: Mapped[int] = mapped_column(Integer, default=3072)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    chunk: Mapped[Chunk] = relationship(back_populates="embedding")


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id"), index=True, nullable=True)
    fiscal_period: Mapped[str] = mapped_column(String(32), index=True)
    metric_name: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16), default="INR")
    source: Mapped[str] = mapped_column(String(32), default="kpi_engine")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(String(36), index=True)
    agent: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="completed")
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DashboardData(Base):
    __tablename__ = "dashboard_data"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    page: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(128))
    entity: Mapped[str] = mapped_column(String(64), default="")
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    ip: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class MarketSnapshot(Base):
    """One row per (series, day) — the historical record the correlation engine and
    trend projections read from. Populated incrementally as live data is fetched, so
    correlation quality grows with real usage instead of being backfilled with guesses."""
    __tablename__ = "market_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    series: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(32), default="alpha_vantage")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class SectorProfile(Base):
    """Stardrive's historical FY23-24 enquiry/order performance per sector — the
    business-history input to relevance_scoring.py's sector_weight(). Seeded once at
    startup (see main.py) from a fixed table, not user-editable yet. `dimension`
    distinguishes true sectors from Export, which is a sales channel that cuts across
    sectors rather than a sector itself (see architecture notes)."""
    __tablename__ = "sector_profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(128))
    tier: Mapped[int] = mapped_column(Integer, default=5)
    dimension: Mapped[str] = mapped_column(String(16), default="sector")  # sector | channel
    enquiry_cr: Mapped[float] = mapped_column(Float, default=0.0)
    orders_cr: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_pct: Mapped[float] = mapped_column(Float, default=0.0)


class MarketOpportunity(Base):
    """A normalized external project/tender entity scored for Stardrive relevance.
    `stardrive_opportunity_value_cr` is deliberately separate from `project_value_cr` —
    never equated, never fabricated when unknown (see relevance_scoring.py)."""
    __tablename__ = "market_opportunities"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(512))
    sector: Mapped[str] = mapped_column(String(64), index=True)
    is_emerging: Mapped[bool] = mapped_column(default=False)
    location: Mapped[str] = mapped_column(String(128), default="")
    project_value_cr: Mapped[float | None] = mapped_column(Float, nullable=True)
    stage: Mapped[str] = mapped_column(String(64), default="")
    tender_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    customer_epc: Mapped[str] = mapped_column(String(255), default="")
    stardrive_opportunity_value_cr: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    strategic_override: Mapped[bool] = mapped_column(default=False)
    strategic_override_reason: Mapped[str] = mapped_column(String(512), default="")
    source_name: Mapped[str] = mapped_column(String(128), default="")
    source_url: Mapped[str] = mapped_column(String(1024), default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    confidence: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(32), default="demo")  # live | demo


class MarketInsight(Base):
    """One AI Executive Brief bullet — the LLM only phrases these, ranking and facts
    are decided upstream by relevance_scoring.py / business_impact_service.py."""
    __tablename__ = "market_insights"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tone: Mapped[str] = mapped_column(String(16), default="amber")  # red | amber | green
    headline: Mapped[str] = mapped_column(String(512))
    why_it_matters: Mapped[str] = mapped_column(Text, default="")
    related_opportunity_id: Mapped[str | None] = mapped_column(ForeignKey("market_opportunities.id"), nullable=True)
    source_refs: Mapped[list] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
