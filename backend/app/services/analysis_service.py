"""Runs the KPI engine + LangGraph agent pipeline and materializes dashboard payloads."""
import logging

from app.agents.graph import run_analysis
from app.analytics.kpi_engine import compute_kpis
from app.database.session import SessionLocal
from app.models.models import AnalysisResult, FinancialMetric
from app.repositories.repositories import DashboardRepository, MetricRepository

logger = logging.getLogger(__name__)


def _metrics_by_period(db) -> dict[str, dict[str, float]]:
    rows = db.query(FinancialMetric).all()
    out: dict[str, dict[str, float]] = {}
    for r in rows:
        out.setdefault(r.fiscal_period, {})[r.metric_name] = r.value
    return dict(sorted(out.items()))


def execute_analysis_run(run_id: str) -> None:
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

        state = run_analysis(periods)

        agent_outputs = {
            "financial_analyst": state.get("analyst", {}),
            "risk_detection": state.get("risks", {}),
            "market_comparison": state.get("market", {}),
            "executive_summary": state.get("summary", {}),
            "recommendation": state.get("recommendations", {}),
        }
        for agent, result in agent_outputs.items():
            db.add(AnalysisResult(run_id=run_id, agent=agent, result=result))
        db.commit()

        _materialize_dashboards(db, periods, agent_outputs)
        logger.info("Analysis run %s complete", run_id)


def _series(periods: dict, name: str) -> list[dict]:
    return [{"period": p, "value": v[name]} for p, v in periods.items() if name in v]


def _materialize_dashboards(db, periods: dict, agents: dict) -> None:
    repo = DashboardRepository(db)
    latest = list(periods.values())[-1] if periods else {}
    summary = agents.get("executive_summary", {})
    risks = agents.get("risk_detection", {})

    repo.save("executive", {
        "business_health_score": summary.get("business_health_score"),
        "risk_score": risks.get("risk_score"),
        "headline": summary.get("headline", ""),
        "summary": summary.get("summary", ""),
        "kpis": {k: latest.get(k) for k in
                 ("revenue", "net_profit", "cash", "working_capital", "ebitda")},
        "revenue_series": _series(periods, "revenue"),
        "profit_series": _series(periods, "net_profit"),
    })
    repo.save("performance", {
        "revenue_series": _series(periods, "revenue"),
        "profit_series": _series(periods, "net_profit"),
        "ebitda_series": _series(periods, "ebitda"),
        "gross_margin_series": _series(periods, "gross_margin_pct"),
        "net_margin_series": _series(periods, "net_margin_pct"),
        "period_over_period": agents.get("financial_analyst", {}).get("period_over_period", []),
    })
    repo.save("cash_flow", {
        "operating": _series(periods, "operating_cash_flow"),
        "investing": _series(periods, "investing_cash_flow"),
        "financing": _series(periods, "financing_cash_flow"),
        "cash": _series(periods, "cash"),
        "current_ratio": _series(periods, "current_ratio"),
    })
    repo.save("working_capital", {
        "receivables": _series(periods, "receivables"),
        "payables": _series(periods, "payables"),
        "inventory": _series(periods, "inventory"),
        "dso": _series(periods, "dso_days"),
        "dpo": _series(periods, "dpo_days"),
        "ccc": _series(periods, "cash_conversion_cycle_days"),
    })
    repo.save("insights", {
        "top_opportunities": summary.get("top_opportunities", []),
        "top_risks": summary.get("top_risks", []),
        "key_highlights": summary.get("key_highlights", []),
        "recommendations": agents.get("recommendation", {}).get("recommendations", []),
    })
    repo.save("audit", {
        "risks": [r for r in risks.get("risks", []) if r.get("category") in ("compliance", "audit")],
        "audit_observations": risks.get("audit_observations", []),
    })
