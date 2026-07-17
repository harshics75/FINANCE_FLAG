from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_any
from app.database.session import get_db
from app.repositories.repositories import DashboardRepository
from app.schemas.schemas import DashboardOut

router = APIRouter()

PAGES = {"executive", "performance", "cash_flow", "working_capital", "insights", "audit", "operational"}


@router.get("/{page}", response_model=DashboardOut, dependencies=[Depends(require_any)])
def get_dashboard(page: str, db: Session = Depends(get_db)):
    if page not in PAGES:
        raise HTTPException(404, f"Unknown dashboard page. Valid: {sorted(PAGES)}")
    row = DashboardRepository(db).latest(page)
    if not row:
        return DashboardOut(page=page, payload={}, generated_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc))
    return DashboardOut(page=page, payload=row.payload, generated_at=row.generated_at)
