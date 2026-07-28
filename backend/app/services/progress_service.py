"""Live per-node progress for the analysis pipeline, backed by Redis. Populated by
run_analysis() as it streams through the LangGraph (see agents/graph.py), and read by
the frontend's Agent Network page while a run is in flight."""
import json

import redis

from app.config.settings import get_settings

settings = get_settings()
_redis: redis.Redis | None = None

TTL_SECONDS = 3600

# Matches the exact node order wired in agents/graph.py build_graph().
NODE_ORDER = [
    "retrieve_context", "financial_analyst", "risk_detection", "market_comparison",
    "executive_summary", "recommendation", "retrieve_mis_context", "operational_highlights",
]


def _cache() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _key(run_id: str) -> str:
    return f"analysis:progress:{run_id}"


def reset(run_id: str) -> None:
    _cache().setex(_key(run_id), TTL_SECONDS, json.dumps({"completed": [], "status": "running"}))


def mark_node_complete(run_id: str, node_name: str) -> None:
    key = _key(run_id)
    raw = _cache().get(key)
    data = json.loads(raw) if raw else {"completed": [], "status": "running"}
    if node_name not in data["completed"]:
        data["completed"].append(node_name)
    _cache().setex(key, TTL_SECONDS, json.dumps(data))


def mark_done(run_id: str, failed: bool = False) -> None:
    key = _key(run_id)
    raw = _cache().get(key)
    data = json.loads(raw) if raw else {"completed": [], "status": "running"}
    data["status"] = "failed" if failed else "done"
    _cache().setex(key, TTL_SECONDS, json.dumps(data))


def get_progress(run_id: str) -> dict:
    raw = _cache().get(_key(run_id))
    data = json.loads(raw) if raw else {"completed": [], "status": "unknown"}
    return {**data, "nodes": NODE_ORDER}
