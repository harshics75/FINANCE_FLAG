"""SQLite persistence for benchmark runs. One DB file per run (or reused across resumed
runs via --resume, keyed by run_id) so results are inspectable with any SQLite tool
independent of this framework."""
from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    models TEXT NOT NULL,
    total_cases INTEGER NOT NULL,
    started_at REAL NOT NULL,
    finished_at REAL
);

CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    prompt TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS requests (
    request_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    category TEXT NOT NULL,
    model TEXT NOT NULL,
    repeat_index INTEGER NOT NULL DEFAULT 0,
    timestamp REAL NOT NULL,
    response_raw TEXT,
    latency_ms REAL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    retry_count INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    UNIQUE(run_id, case_id, model, repeat_index)
);

CREATE TABLE IF NOT EXISTS scores (
    request_id TEXT PRIMARY KEY REFERENCES requests(request_id),
    json_valid INTEGER,
    schema_compliant INTEGER,
    missing_fields TEXT,
    reasoning_score REAL,
    risk_explanation_score REAL,
    priority_accuracy REAL,
    action_quality REAL,
    hallucination_flag INTEGER,
    overall_score REAL
);

CREATE INDEX IF NOT EXISTS idx_requests_run_model ON requests(run_id, model);
CREATE INDEX IF NOT EXISTS idx_requests_case ON requests(case_id);
"""


@dataclass
class CaseRecord:
    case_id: str
    category: str
    prompt: str


@dataclass
class RequestRecord:
    request_id: str
    run_id: str
    case_id: str
    category: str
    model: str
    repeat_index: int = 0
    timestamp: float = field(default_factory=time.time)
    response_raw: Optional[str] = None
    latency_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    retry_count: int = 0
    error: Optional[str] = None


@dataclass
class ScoreRecord:
    request_id: str
    json_valid: bool
    schema_compliant: bool
    missing_fields: str  # comma-joined field names, "" if none
    reasoning_score: float
    risk_explanation_score: float
    priority_accuracy: float
    action_quality: float
    hallucination_flag: bool
    overall_score: float


class BenchmarkStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def start_run(self, run_id: str, mode: str, models: list[str], total_cases: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO runs (run_id, mode, models, total_cases, started_at) VALUES (?,?,?,?,?)",
                (run_id, mode, ",".join(models), total_cases, time.time()),
            )

    def finish_run(self, run_id: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE runs SET finished_at = ? WHERE run_id = ?", (time.time(), run_id))

    def upsert_case(self, case: CaseRecord) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO cases (case_id, category, prompt) VALUES (?,?,?)",
                (case.case_id, case.category, case.prompt),
            )

    def is_done(self, run_id: str, case_id: str, model: str, repeat_index: int = 0) -> bool:
        """Used for --resume: skip work already recorded (with no error) for this run."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT error FROM requests WHERE run_id=? AND case_id=? AND model=? AND repeat_index=?",
                (run_id, case_id, model, repeat_index),
            ).fetchone()
            return row is not None and row["error"] is None

    def save_request(self, req: RequestRecord) -> None:
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO requests
                (request_id, run_id, case_id, category, model, repeat_index, timestamp,
                 response_raw, latency_ms, input_tokens, output_tokens, total_tokens, retry_count, error)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (req.request_id, req.run_id, req.case_id, req.category, req.model, req.repeat_index,
                 req.timestamp, req.response_raw, req.latency_ms, req.input_tokens, req.output_tokens,
                 req.total_tokens, req.retry_count, req.error),
            )

    def save_score(self, score: ScoreRecord) -> None:
        d = asdict(score)
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO scores
                (request_id, json_valid, schema_compliant, missing_fields, reasoning_score,
                 risk_explanation_score, priority_accuracy, action_quality, hallucination_flag, overall_score)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (d["request_id"], int(d["json_valid"]), int(d["schema_compliant"]), d["missing_fields"],
                 d["reasoning_score"], d["risk_explanation_score"], d["priority_accuracy"],
                 d["action_quality"], int(d["hallucination_flag"]), d["overall_score"]),
            )

    def fetch_results(self, run_id: str) -> list[sqlite3.Row]:
        with self._conn() as conn:
            return conn.execute(
                """SELECT r.*, s.json_valid, s.schema_compliant, s.missing_fields, s.reasoning_score,
                          s.risk_explanation_score, s.priority_accuracy, s.action_quality,
                          s.hallucination_flag, s.overall_score
                   FROM requests r LEFT JOIN scores s ON r.request_id = s.request_id
                   WHERE r.run_id = ? ORDER BY r.timestamp""",
                (run_id,),
            ).fetchall()
