"""Orchestrates dataset -> provider calls -> scoring -> storage. Resumable (skips work
already recorded for this run_id), rate-limited per provider, runs different providers
concurrently (each provider's own RateLimiter throttles same-provider concurrency
regardless of thread count, so cross-provider parallelism is always safe)."""
from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from benchmarks import dataset, scoring
from benchmarks.providers import PROVIDERS, call_provider
from benchmarks.storage import BenchmarkStore, RequestRecord

DETERMINISM_SUBSET_SIZE = 8   # cases (out of the full set) that also get repeated runs
DETERMINISM_REPEATS = 3       # total runs for those cases (1 baseline + 2 extra)


@dataclass
class WorkItem:
    case_id: str
    category: str
    prompt: str
    model: str
    repeat_index: int


def _build_work_items(cases: list, models: list[str], include_determinism: bool = True) -> list[WorkItem]:
    items: list[WorkItem] = []
    determinism_ids = {c.case_id for c in cases[:DETERMINISM_SUBSET_SIZE]} if include_determinism else set()
    for case in cases:
        for model in models:
            items.append(WorkItem(case.case_id, case.category, case.prompt, model, 0))
            if case.case_id in determinism_ids:
                for r in range(1, DETERMINISM_REPEATS):
                    items.append(WorkItem(case.case_id, case.category, case.prompt, model, r))
    return items


# Providers that have hit their daily cap mid-run — stop sending them new work, but let
# in-flight calls finish naturally.
_exhausted: set[str] = set()


def _process(item: WorkItem, run_id: str, store: BenchmarkStore) -> tuple[str, bool]:
    if item.model in _exhausted:
        return item.model, False
    request_id = f"{run_id}:{item.case_id}:{item.model}:{item.repeat_index}"
    result = call_provider(item.model, item.prompt)
    if result.error and "Daily cap" in result.error:
        _exhausted.add(item.model)

    store.save_request(RequestRecord(
        request_id=request_id, run_id=run_id, case_id=item.case_id, category=item.category,
        model=item.model, repeat_index=item.repeat_index, response_raw=result.text,
        latency_ms=result.latency_ms, input_tokens=result.input_tokens,
        output_tokens=result.output_tokens, total_tokens=result.total_tokens,
        retry_count=result.retry_count, error=result.error,
    ))
    if result.text is not None:
        store.save_score(scoring.score_response(request_id, result.text, item.prompt))
    return item.model, result.error is None


def run(mode: str, models: list[str], db_path: str, run_id: str | None = None,
       resume: bool = False, max_workers: int = 4, limit: int | None = None,
       include_determinism: bool = True) -> str:
    for m in models:
        if m not in PROVIDERS:
            raise ValueError(f"Unknown provider {m!r}; available: {list(PROVIDERS)}")

    cases = dataset.generate(mode)
    if limit is not None:
        cases = cases[:limit]
    run_id = run_id or f"{mode}-{int(time.time())}"
    store = BenchmarkStore(db_path)
    store.start_run(run_id, mode, models, len(cases))
    for case in cases:
        store.upsert_case(case)

    work = _build_work_items(cases, models, include_determinism)
    if resume:
        before = len(work)
        work = [w for w in work if not store.is_done(run_id, w.case_id, w.model, w.repeat_index)]
        print(f"[resume] {before - len(work)}/{before} already completed, {len(work)} remaining", file=sys.stderr)

    total = len(work)
    done = 0
    ok = 0
    print(f"[run {run_id}] mode={mode} models={models} cases={len(cases)} total_calls={total}", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_process, item, run_id, store): item for item in work}
        for future in as_completed(futures):
            item = futures[future]
            try:
                _, success = future.result()
                ok += int(success)
            except Exception as exc:  # noqa: BLE001
                print(f"[error] {item.model}/{item.case_id}: {exc}", file=sys.stderr)
            done += 1
            if done % 10 == 0 or done == total:
                print(f"[progress] {done}/{total} ({ok} ok)", file=sys.stderr)

    store.finish_run(run_id)
    if _exhausted:
        print(f"[note] stopped early for exhausted providers: {sorted(_exhausted)}", file=sys.stderr)
    print(f"[done] run_id={run_id} db={db_path}", file=sys.stderr)
    return run_id
