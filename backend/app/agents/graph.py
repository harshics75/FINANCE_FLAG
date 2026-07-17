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


def node_market_comparison(state: AnalysisState) -> AnalysisState:
    result = run_json(T.SYSTEM_BASE, T.MARKET_COMPARISON.format(
        metrics=_metrics_str(state), context=state.get("context", "")))
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


def build_graph():
    g = StateGraph(AnalysisState)
    g.add_node("context", node_context)
    g.add_node("financial_analyst", node_financial_analyst)
    g.add_node("risk_detection", node_risk_detection)
    g.add_node("market_comparison", node_market_comparison)
    g.add_node("executive_summary", node_executive_summary)
    g.add_node("recommendation", node_recommendation)

    g.set_entry_point("context")
    g.add_edge("context", "financial_analyst")
    g.add_edge("financial_analyst", "risk_detection")
    g.add_edge("risk_detection", "market_comparison")
    g.add_edge("market_comparison", "executive_summary")
    g.add_edge("executive_summary", "recommendation")
    g.add_edge("recommendation", END)
    return g.compile()


def run_analysis(metrics: dict) -> AnalysisState:
    graph = build_graph()
    return graph.invoke({"metrics": metrics})
