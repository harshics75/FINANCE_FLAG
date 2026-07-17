"""Export executive report to PDF and metrics to Excel."""
import io
from datetime import datetime, timezone

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.models.models import FinancialMetric
from app.repositories.repositories import DashboardRepository


def export_executive_pdf(db) -> bytes:
    repo = DashboardRepository(db)
    executive = (repo.latest("executive") or type("x", (), {"payload": {}})).payload
    insights = (repo.latest("insights") or type("x", (), {"payload": {}})).payload

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Executive Financial Report", styles["Title"]),
        Paragraph(datetime.now(timezone.utc).strftime("Generated %d %b %Y %H:%M UTC"), styles["Normal"]),
        Spacer(1, 12),
        Paragraph(executive.get("headline", "Financial Overview"), styles["Heading2"]),
        Paragraph(str(executive.get("summary", "Run an analysis to populate this report.")), styles["BodyText"]),
        Spacer(1, 12),
    ]

    kpis = executive.get("kpis", {}) or {}
    rows = [["KPI", "Value"]] + [[k.replace("_", " ").title(), f"{v:,.0f}" if isinstance(v, (int, float)) else "—"]
                                 for k, v in kpis.items()]
    if len(rows) > 1:
        t = Table(rows, colWidths=[8 * cm, 6 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story += [t, Spacer(1, 12)]

    for title, key in (("Key Highlights", "key_highlights"), ("Top Risks", "top_risks"),
                       ("Recommended Actions", "recommendations")):
        items = insights.get(key, [])
        if items:
            story.append(Paragraph(title, styles["Heading2"]))
            for item in items:
                text = item.get("action", str(item)) if isinstance(item, dict) else str(item)
                story.append(Paragraph(f"• {text}", styles["BodyText"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    return buf.getvalue()


def export_metrics_excel(db) -> bytes:
    rows = db.query(FinancialMetric).all()
    df = pd.DataFrame([{"Fiscal Period": r.fiscal_period, "Metric": r.metric_name,
                        "Value": r.value, "Unit": r.unit, "Source": r.source} for r in rows])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        (df if not df.empty else pd.DataFrame(columns=["Fiscal Period", "Metric", "Value"])) \
            .to_excel(writer, index=False, sheet_name="Financial Metrics")
    return buf.getvalue()
