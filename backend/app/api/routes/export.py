from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import require_any
from app.database.session import get_db
from app.services.export_service import export_executive_pdf, export_metrics_excel

router = APIRouter()


@router.get("/pdf", dependencies=[Depends(require_any)])
def export_pdf(db: Session = Depends(get_db)):
    data = export_executive_pdf(db)
    return Response(data, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=executive-report.pdf"})


@router.get("/excel", dependencies=[Depends(require_any)])
def export_excel(db: Session = Depends(get_db)):
    data = export_metrics_excel(db)
    return Response(data,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=financial-metrics.xlsx"})
