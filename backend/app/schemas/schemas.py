from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""
    role: str = "finance_manager"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------- Documents ----------
class DocumentOut(BaseModel):
    id: str
    filename: str
    doc_type: str
    fiscal_period: str
    status: str
    is_scanned: bool
    page_count: int
    size_bytes: int
    version: int
    created_at: datetime
    error: str = ""

    model_config = {"from_attributes": True}


class ChunkOut(BaseModel):
    id: str
    chunk_index: int
    page_number: int
    content: str
    content_type: str

    model_config = {"from_attributes": True}


# ---------- Analysis ----------
class AnalysisRunRequest(BaseModel):
    document_ids: list[str] = []
    fiscal_periods: list[str] = []


class AnalysisRunOut(BaseModel):
    run_id: str
    status: str


class AgentResultOut(BaseModel):
    agent: str
    status: str
    result: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Metrics / Dashboard ----------
class MetricOut(BaseModel):
    fiscal_period: str
    metric_name: str
    value: float
    unit: str

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    page: str
    payload: dict[str, Any]
    generated_at: datetime


# ---------- Chat ----------
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: int
    snippet: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation] = []
