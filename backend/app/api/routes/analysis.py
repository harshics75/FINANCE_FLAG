import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_any, require_finance
from app.database.session import get_db
from app.models.models import FinancialMetric, User
from app.repositories.repositories import AnalysisRepository, AuditLogRepository
from app.schemas.schemas import (AgentResultOut, AnalysisRunOut, AnalysisRunRequest, MetricOut)
from app.services.worker import run_analysis_task

router = APIRouter()


@router.post("/run", response_model=AnalysisRunOut)
def run_analysis(payload: AnalysisRunRequest, user: User = Depends(require_finance),
                 db: Session = Depends(get_db)):
    """Kick off the full LangGraph agent pipeline over all processed documents."""
    run_id = str(uuid.uuid4())
    AuditLogRepository(db).log(user.id, "analysis.run", "run", run_id)
    try:
        run_analysis_task.delay(run_id)
    except Exception:
        from app.services.analysis_service import execute_analysis_run
        execute_analysis_run(run_id)
        return AnalysisRunOut(run_id=run_id, status="completed")
    return AnalysisRunOut(run_id=run_id, status="queued")


@router.get("/runs/{run_id}", response_model=list[AgentResultOut], dependencies=[Depends(require_any)])
def get_run(run_id: str, db: Session = Depends(get_db)):
    return AnalysisRepository(db).by_run(run_id)


@router.get("/agents/{agent}/latest", response_model=AgentResultOut | None, dependencies=[Depends(require_any)])
def latest_agent_result(agent: str, db: Session = Depends(get_db)):
    return AnalysisRepository(db).latest_by_agent(agent)


@router.get("/metrics", response_model=list[MetricOut], dependencies=[Depends(require_any)])
def list_metrics(db: Session = Depends(get_db)):
    return db.query(FinancialMetric).order_by(FinancialMetric.fiscal_period).all()
