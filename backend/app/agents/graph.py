"""LangGraph workflow orchestrating the five agents:

  kpi_context → financial_analyst → risk_detection → market_comparison
             → executive_summary → recommendation → END
"""
import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.llm import run_json
from app.prompts import templates as T
from app.rag.pipeline import build_context, retrieve
from app.services.market_data_service import get_live_market_data
from app.services.progress_service import mark_node_complete

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict, total=False):
    metrics: dict            # {period: {metric: value}}
    context_query: str
    context: str
    analyst: dict
    risks: dict
    market: dict
    summary: dict
    recommendations: dict
    mis_context: str
    operational: dict


def _metrics_str(state: AnalysisState) -> str:
    return json.dumps(state.get("metrics", {}), indent=2, default=str)


def node_context(state: AnalysisState) -> AnalysisState:
    query = state.get("context_query", "financial performance revenue profit cash flow risks audit observations")
    chunks = retrieve(query, k=10)
    return {"context": build_context(chunks)}


def node_financial_analyst(state: AnalysisState) -> AnalysisState:
    result = run_json(T.SYSTEM_BASE, T.FINANCIAL_ANALYST.format(
        metrics=_metrics_str(state), context=state.get("context", "")))
    return {"analyst": result}


def node_risk_detection(state: AnalysisState) -> AnalysisState:
    result = run_json(T.SYSTEM_BASE, T.RISK_DETECTION.format(
        metrics=_metrics_str(state), context=state.get("context", "")))
    return {"risks": result}


def _market_data_str() -> str:
    data = get_live_market_data()
    if not data:
        return "unavailable"
    return json.dumps(data, indent=2)


def node_market_comparison(state: AnalysisState) -> AnalysisState:
    result = run_json(T.SYSTEM_BASE, T.MARKET_COMPARISON.format(
        metrics=_metrics_str(state), context=state.get("context", ""),
        market_data=_market_data_str()))
    return {"market": result}


def node_executive_summary(state: AnalysisState) -> AnalysisState:
    result = run_json(T.SYSTEM_BASE, T.EXECUTIVE_SUMMARY.format(
        analyst=json.dumps(state.get("analyst", {})),
        risks=json.dumps(state.get("risks", {})),
        market=json.dumps(state.get("market", {}))))
    return {"summary": result}


def node_recommendation(state: AnalysisState) -> AnalysisState:
    result = run_json(T.SYSTEM_BASE, T.RECOMMENDATION.format(
        summary=json.dumps(state.get("summary", {})),
        risks=json.dumps(state.get("risks", {}))))
    return {"recommendations": result}


def node_mis_context(state: AnalysisState) -> AnalysisState:
    chunks = retrieve(
        "order book production status major projects legal compliance exceptional events cost overrun delay",
        k=10, filters={"doc_type": "monthly_mis"})
    return {"mis_context": build_context(chunks)}


def node_operational_highlights(state: AnalysisState) -> AnalysisState:
    mis_context = state.get("mis_context", "")
    if not mis_context.strip():
        return {"operational": {}}
    result = run_json(T.SYSTEM_BASE, T.OPERATIONAL_HIGHLIGHTS.format(context=mis_context))
    return {"operational": result}


def build_graph():
    g = StateGraph(AnalysisState)
    g.add_node("retrieve_context", node_context)
    g.add_node("financial_analyst", node_financial_analyst)
    g.add_node("risk_detection", node_risk_detection)
    g.add_node("market_comparison", node_market_comparison)
    g.add_node("executive_summary", node_executive_summary)
    g.add_node("recommendation", node_recommendation)
    g.add_node("retrieve_mis_context", node_mis_context)
    g.add_node("operational_highlights", node_operational_highlights)

    g.set_entry_point("retrieve_context")
    g.add_edge("retrieve_context", "financial_analyst")
    g.add_edge("financial_analyst", "risk_detection")
    g.add_edge("risk_detection", "market_comparison")
    g.add_edge("market_comparison", "executive_summary")
    g.add_edge("executive_summary", "recommendation")
    g.add_edge("recommendation", "retrieve_mis_context")
    g.add_edge("retrieve_mis_context", "operational_highlights")
    g.add_edge("operational_highlights", END)
    return g.compile()


def run_analysis(metrics: dict, run_id: str | None = None) -> AnalysisState:
    graph = build_graph()
    if not run_id:
        return graph.invoke({"metrics": metrics})

    # Stream node-by-node so genuine live progress can be published as each one
    # actually completes, instead of only knowing the result at the very end.
    state: dict = {"metrics": metrics}
    for update in graph.stream({"metrics": metrics}, stream_mode="updates"):
        for node_name, node_output in update.items():
            state.update(node_output)
            mark_node_complete(run_id, node_name)
    return state  # type: ignore[return-value]
