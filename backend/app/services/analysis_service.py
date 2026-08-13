"""Runs the KPI engine + LangGraph agent pipeline and materializes dashboard payloads."""
import logging

from app.agents.graph import run_analysis
from app.analytics.kpi_engine import compute_kpis, project_trend
from app.database.session import SessionLocal
from app.models.models import AnalysisResult, FinancialMetric
from app.repositories.repositories import DashboardRepository, MetricRepository
from app.services.progress_service import mark_done, reset

logger = logging.getLogger(__name__)


def _metrics_by_period(db) -> dict[str, dict[str, float]]:
    rows = db.query(FinancialMetric).all()
    out: dict[str, dict[str, float]] = {}
    for r in rows:
        out.setdefault(r.fiscal_period, {})[r.metric_name] = r.value
    return dict(sorted(out.items()))


def execute_analysis_run(run_id: str) -> None:
    reset(run_id)
    try:
        with SessionLocal() as db:
            periods = _metrics_by_period(db)
            # Recompute derived KPIs per period (with prior-period growth)
            ordered = list(periods.items())
            metric_repo = MetricRepository(db)
            for i, (period, items) in enumerate(ordered):
                prior = ordered[i - 1][1] if i > 0 else None
                kpis = compute_kpis(items, prior)
                for name, value in kpis.metrics.items():
                    metric_repo.upsert(FinancialMetric(fiscal_period=period, metric_name=name,
                                                       value=value, source="kpi_engine"))
            periods = _metrics_by_period(db)
            forecast = project_trend(list(periods.items()))

            state = run_analysis(periods, run_id=run_id)

            agent_outputs = {
                "financial_analyst": state.get("analyst", {}),
                "risk_detection": state.get("risks", {}),
                "market_comparison": state.get("market", {}),
                "executive_summary": state.get("summary", {}),
                "recommendation": state.get("recommendations", {}),
                "operational_highlights": state.get("operational", {}),
            }
            for agent, result in agent_outputs.items():
                db.add(AnalysisResult(run_id=run_id, agent=agent, result=result))
            db.commit()

            _materialize_dashboards(db, periods, agent_outputs)
            DashboardRepository(db).save("forecast", forecast)
            logger.info("Analysis run %s complete", run_id)
        mark_done(run_id)
    except Exception:
        mark_done(run_id, failed=True)
        raise


def _series(periods: dict, name: str) -> list[dict]:
    return [{"period": p, "value": v[name]} for p, v in periods.items() if name in v]


def _materialize_dashboards(db, periods: dict, agents: dict) -> None:
    repo = DashboardRepository(db)
    latest = list(periods.values())[-1] if periods else {}
    summary = agents.get("executive_summary", {})
    risks = agents.get("risk_detection", {})
    analyst = agents.get("financial_analyst", {})
    operational = agents.get("operational_highlights", {})

    repo.save("executive", {
        "business_health_score": summary.get("business_health_score"),
        "risk_score": risks.get("risk_score"),
        "headline": summary.get("headline", ""),
        "summary": summary.get("summary", ""),
        "kpis": {k: latest.get(k) for k in
                 ("revenue", "net_profit", "cash", "working_capital", "ebitda")},
        "revenue_series": _series(periods, "revenue"),
        "profit_series": _series(periods, "net_profit"),
        "green_flags": summary.get("green_flags", []),
        "red_flags": summary.get("red_flags", []),
        "confidence": summary.get("confidence"),
    })
    repo.save("performance", {
        "revenue_series": _series(periods, "revenue"),
        "profit_series": _series(periods, "net_profit"),
        "ebitda_series": _series(periods, "ebitda"),
        "gross_margin_series": _series(periods, "gross_margin_pct"),
        "net_margin_series": _series(periods, "net_margin_pct"),
        "operating_margin_series": _series(periods, "operating_margin_pct"),
        "period_over_period": analyst.get("period_over_period", []),
        "profitability_assessment": analyst.get("profitability_assessment", ""),
        "confidence": analyst.get("confidence"),
    })
    repo.save("fund_flow", {
        "operating": _series(periods, "operating_cash_flow"),
        "investing": _series(periods, "investing_cash_flow"),
        "financing": _series(periods, "financing_cash_flow"),
        "cash": _series(periods, "cash"),
        "current_ratio": _series(periods, "current_ratio"),
        "quick_ratio": _series(periods, "quick_ratio"),
        "debt_to_equity": _series(periods, "debt_to_equity"),
        "burn_rate_monthly": latest.get("burn_rate_monthly"),
        "runway_months": latest.get("runway_months"),
        "receivables": _series(periods, "receivables"),
        "payables": _series(periods, "payables"),
        "inventory": _series(periods, "inventory"),
        "dso": _series(periods, "dso_days"),
        "dpo": _series(periods, "dpo_days"),
        "ccc": _series(periods, "cash_conversion_cycle_days"),
        "liquidity_health_score": latest.get("liquidity_score"),
        "collection_health_score": latest.get("collection_health_score"),
        "obligation_health_score": latest.get("obligation_health_score"),
        "risk_score": risks.get("risk_score"),
        "cash_flow_summary": analyst.get("cash_flow_summary", ""),
        "working_capital_summary": analyst.get("working_capital_summary", ""),
        "confidence": analyst.get("confidence"),
    })
    repo.save("insights", {
        "top_opportunities": summary.get("top_opportunities", []),
        "top_risks": summary.get("top_risks", []),
        "key_highlights": summary.get("key_highlights", []),
        "green_flags": summary.get("green_flags", []),
        "red_flags": summary.get("red_flags", []),
        "critical_insights": summary.get("critical_insights", []),
        "recommendations": agents.get("recommendation", {}).get("recommendations", []),
        "confidence": summary.get("confidence"),
        "recommendation_confidence": agents.get("recommendation", {}).get("confidence"),
    })
    repo.save("audit", {
        "risks": [r for r in risks.get("risks", []) if r.get("category") in ("compliance", "audit")],
        "audit_observations": risks.get("audit_observations", []),
        "confidence": risks.get("confidence"),
    })
    repo.save("operational", {
        "order_book": operational.get("order_book", ""),
        "major_projects": operational.get("major_projects", []),
        "production_status": operational.get("production_status", ""),
        "legal_compliance": operational.get("legal_compliance", []),
        "exceptional_events": operational.get("exceptional_events", []),
        "confidence": operational.get("confidence"),
    })
