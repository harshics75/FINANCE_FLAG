"""Aggregates a run's SQLite results into CSV / JSON / Markdown / HTML reports, plus a
weighted leaderboard. Every number here comes from rows actually recorded during the
run — nothing is estimated or assumed. P95/P99 are computed only when there are enough
samples to mean anything; otherwise the report says so explicitly instead of printing a
number that looks precise but isn't.
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from benchmarks.providers import PROVIDERS, estimate_cost_usd
from benchmarks.storage import BenchmarkStore

MIN_SAMPLES_FOR_PERCENTILES = 20

# Documented, not hidden: how the leaderboard's overall score is composed.
LEADERBOARD_WEIGHTS = {
    "reasoning": 0.30,       # avg reasoning_score (grounded, causal, substantive)
    "financial_accuracy": 0.25,  # avg of risk_explanation_score + priority_accuracy
    "latency": 0.15,         # inverse-normalized avg latency (faster = higher)
    "token_efficiency": 0.10,  # inverse-normalized avg total tokens (fewer = higher)
    "consistency": 0.10,     # based on determinism-subset output variance (lower = higher)
    "formatting": 0.10,      # schema_compliant rate
}


def _percentile(sorted_vals: list[float], p: float) -> float:
    k = (len(sorted_vals) - 1) * p
    f, c = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def _normalize_inverse(value: float, lo: float, hi: float) -> float:
    """Lower raw value -> higher normalized score (0-10). Flat 10 if all models tie."""
    if hi <= lo:
        return 10.0
    return round(10.0 * (1 - (value - lo) / (hi - lo)), 2)


def build_summary(run_id: str, db_path: str) -> dict:
    store = BenchmarkStore(db_path)
    rows = [dict(r) for r in store.fetch_results(run_id)]
    if not rows:
        raise ValueError(f"No requests recorded for run_id={run_id} in {db_path}")

    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)

    per_model: dict[str, dict] = {}
    for model, mrows in by_model.items():
        successes = [r for r in mrows if r["error"] is None]
        failures = [r for r in mrows if r["error"] is not None]
        latencies = sorted(r["latency_ms"] for r in successes if r["latency_ms"] is not None)
        in_toks = [r["input_tokens"] for r in successes if r["input_tokens"] is not None]
        out_toks = [r["output_tokens"] for r in successes if r["output_tokens"] is not None]
        tot_toks = [r["total_tokens"] for r in successes if r["total_tokens"] is not None]
        scores = [r["overall_score"] for r in successes if r["overall_score"] is not None]
        reasoning = [r["reasoning_score"] for r in successes if r["reasoning_score"] is not None]
        risk_expl = [r["risk_explanation_score"] for r in successes if r["risk_explanation_score"] is not None]
        priority_acc = [r["priority_accuracy"] for r in successes if r["priority_accuracy"] is not None]
        action_q = [r["action_quality"] for r in successes if r["action_quality"] is not None]
        json_valid_n = sum(1 for r in successes if r["json_valid"])
        schema_ok_n = sum(1 for r in successes if r["schema_compliant"])
        hallucinated_n = sum(1 for r in successes if r["hallucination_flag"])

        limits = PROVIDERS.get(model)
        total_in = sum(in_toks) if in_toks else 0
        total_out = sum(out_toks) if out_toks else 0
        ref_cost_total = estimate_cost_usd(model, total_in, total_out)

        percentiles_valid = len(latencies) >= MIN_SAMPLES_FOR_PERCENTILES
        per_model[model] = {
            "requests": len(mrows),
            "successes": len(successes),
            "failures": len(failures),
            "success_rate_pct": round(100 * len(successes) / len(mrows), 1) if mrows else 0.0,
            "latency_ms": {
                "avg": round(statistics.mean(latencies), 1) if latencies else None,
                "min": round(min(latencies), 1) if latencies else None,
                "max": round(max(latencies), 1) if latencies else None,
                "median": round(statistics.median(latencies), 1) if latencies else None,
                "p95": round(_percentile(latencies, 0.95), 1) if percentiles_valid else None,
                "p99": round(_percentile(latencies, 0.99), 1) if percentiles_valid else None,
                "percentiles_note": None if percentiles_valid else
                    f"Only {len(latencies)} samples (<{MIN_SAMPLES_FOR_PERCENTILES}) — P95/P99 omitted as not statistically meaningful at this sample size.",
            },
            "tokens": {
                "avg_input": round(statistics.mean(in_toks), 1) if in_toks else None,
                "avg_output": round(statistics.mean(out_toks), 1) if out_toks else None,
                "avg_total": round(statistics.mean(tot_toks), 1) if tot_toks else None,
                "max_response": max(out_toks) if out_toks else None,
                "min_response": min(out_toks) if out_toks else None,
            },
            "cost": {
                "is_free_tier": limits.is_free if limits else None,
                "actual_cost_usd": 0.0 if (limits and limits.is_free) else None,
                "reference_cost_at_paid_rate_usd": round(ref_cost_total, 4) if ref_cost_total is not None else None,
                "note": "Actual cost was $0 (free-tier key). The paid-rate figure is a reference only — "
                       "what this run would have cost if metered at the provider's published paid pricing."
                       if (limits and limits.is_free) else None,
            },
            "quality": {
                "avg_overall_score": round(statistics.mean(scores), 2) if scores else 0.0,
                "avg_reasoning_score": round(statistics.mean(reasoning), 2) if reasoning else 0.0,
                "avg_risk_explanation_score": round(statistics.mean(risk_expl), 2) if risk_expl else 0.0,
                "avg_priority_accuracy": round(statistics.mean(priority_acc), 2) if priority_acc else 0.0,
                "avg_action_quality": round(statistics.mean(action_q), 2) if action_q else 0.0,
                "json_valid_rate_pct": round(100 * json_valid_n / len(successes), 1) if successes else 0.0,
                "schema_compliant_rate_pct": round(100 * schema_ok_n / len(successes), 1) if successes else 0.0,
                "hallucination_rate_pct": round(100 * hallucinated_n / len(successes), 1) if successes else 0.0,
            },
        }

    # Determinism: cases that got repeat_index > 0 recorded.
    determinism: dict[str, dict] = {}
    for model, mrows in by_model.items():
        by_case: dict[str, list[dict]] = defaultdict(list)
        for r in mrows:
            if r["error"] is None:
                by_case[r["case_id"]].append(r)
        repeated_cases = {cid: rs for cid, rs in by_case.items() if len(rs) > 1}
        if not repeated_cases:
            continue
        identical_count = 0
        score_variances = []
        for cid, rs in repeated_cases.items():
            texts = [(r["response_raw"] or "").strip() for r in rs]
            if len(set(texts)) == 1:
                identical_count += 1
            case_scores = [r["overall_score"] for r in rs if r["overall_score"] is not None]
            if len(case_scores) > 1:
                score_variances.append(statistics.variance(case_scores))
        determinism[model] = {
            "cases_repeated": len(repeated_cases),
            "runs_per_case": len(next(iter(repeated_cases.values()))) if repeated_cases else 0,
            "identical_output_rate_pct": round(100 * identical_count / len(repeated_cases), 1),
            "avg_score_variance": round(statistics.mean(score_variances), 3) if score_variances else 0.0,
        }

    # Leaderboard.
    models = list(per_model.keys())
    lat_avgs = {m: per_model[m]["latency_ms"]["avg"] or 0 for m in models}
    tok_avgs = {m: per_model[m]["tokens"]["avg_total"] or 0 for m in models}
    lat_lo, lat_hi = (min(lat_avgs.values()), max(lat_avgs.values())) if lat_avgs else (0, 0)
    tok_lo, tok_hi = (min(tok_avgs.values()), max(tok_avgs.values())) if tok_avgs else (0, 0)

    leaderboard = []
    for m in models:
        pm = per_model[m]
        reasoning = pm["quality"]["avg_reasoning_score"]
        fin_acc = (pm["quality"]["avg_risk_explanation_score"] + pm["quality"]["avg_priority_accuracy"]) / 2
        latency_score = _normalize_inverse(lat_avgs[m], lat_lo, lat_hi)
        token_score = _normalize_inverse(tok_avgs[m], tok_lo, tok_hi)
        det = determinism.get(m)
        consistency_score = round(10.0 - min(10.0, (det["avg_score_variance"] if det else 0) * 2), 2)
        formatting_score = pm["quality"]["schema_compliant_rate_pct"] / 10

        weighted = (
            reasoning * LEADERBOARD_WEIGHTS["reasoning"]
            + fin_acc * LEADERBOARD_WEIGHTS["financial_accuracy"]
            + latency_score * LEADERBOARD_WEIGHTS["latency"]
            + token_score * LEADERBOARD_WEIGHTS["token_efficiency"]
            + consistency_score * LEADERBOARD_WEIGHTS["consistency"]
            + formatting_score * LEADERBOARD_WEIGHTS["formatting"]
        )
        leaderboard.append({
            "model": m, "weighted_score": round(weighted, 3),
            "reasoning": reasoning, "financial_accuracy": round(fin_acc, 2),
            "latency_score": latency_score, "token_efficiency_score": token_score,
            "consistency_score": consistency_score, "formatting_score": round(formatting_score, 2),
        })
    leaderboard.sort(key=lambda x: x["weighted_score"], reverse=True)

    return {
        "run_id": run_id, "per_model": per_model, "determinism": determinism,
        "leaderboard": leaderboard, "weights": LEADERBOARD_WEIGHTS,
        "raw_row_count": len(rows),
    }


def write_csv(rows_path: str, run_id: str, db_path: str) -> None:
    store = BenchmarkStore(db_path)
    rows = [dict(r) for r in store.fetch_results(run_id)]
    if not rows:
        return
    with open(rows_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(json_path: str, summary: dict) -> None:
    Path(json_path).write_text(json.dumps(summary, indent=2))


def _svg_bar_chart(title: str, data: dict[str, float], unit: str = "", width: int = 480) -> str:
    if not data:
        return ""
    max_val = max(data.values()) or 1
    bar_h, gap, left_pad = 28, 14, 160
    height = len(data) * (bar_h + gap) + 40
    bars = []
    for i, (label, value) in enumerate(data.items()):
        y = 30 + i * (bar_h + gap)
        bar_w = max(2, (value / max_val) * (width - left_pad - 70))
        bars.append(
            f'<text x="{left_pad - 10}" y="{y + bar_h * 0.65}" text-anchor="end" '
            f'font-size="12" fill="var(--ink-soft,#666)">{label}</text>'
            f'<rect x="{left_pad}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="4" fill="var(--accent,#4f7cff)"/>'
            f'<text x="{left_pad + bar_w + 8}" y="{y + bar_h * 0.65}" font-size="12" '
            f'fill="var(--ink,#111)">{value:g}{unit}</text>'
        )
    return (
        f'<div class="chart"><div class="chart-title">{title}</div>'
        f'<svg viewBox="0 0 {width} {height}" width="100%" style="max-width:{width}px">{"".join(bars)}</svg></div>'
    )


def write_markdown(md_path: str, summary: dict) -> None:
    lines = [f"# Benchmark Report — {summary['run_id']}", ""]
    lines.append(f"Total requests recorded: {summary['raw_row_count']}")
    lines.append("")
    lines.append("## Leaderboard")
    lines.append("")
    lines.append("Weighted score composition: " + ", ".join(
        f"{k}={v*100:.0f}%" for k, v in summary["weights"].items()))
    lines.append("")
    lines.append("| Rank | Model | Weighted Score | Reasoning | Financial Accuracy | Latency | Token Eff. | Consistency | Formatting |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, row in enumerate(summary["leaderboard"], 1):
        lines.append(f"| {i} | {row['model']} | {row['weighted_score']} | {row['reasoning']} | "
                     f"{row['financial_accuracy']} | {row['latency_score']} | {row['token_efficiency_score']} | "
                     f"{row['consistency_score']} | {row['formatting_score']} |")
    lines.append("")

    for model, pm in summary["per_model"].items():
        lines.append(f"## {model}")
        lines.append("")
        lines.append(f"- Requests: {pm['requests']} ({pm['successes']} ok, {pm['failures']} failed, "
                     f"{pm['success_rate_pct']}% success rate)")
        lat = pm["latency_ms"]
        lines.append(f"- Latency (ms): avg {lat['avg']}, median {lat['median']}, min {lat['min']}, max {lat['max']}"
                     + (f", P95 {lat['p95']}, P99 {lat['p99']}" if lat["p95"] is not None else ""))
        if lat["percentiles_note"]:
            lines.append(f"  - _{lat['percentiles_note']}_")
        tok = pm["tokens"]
        lines.append(f"- Tokens: avg input {tok['avg_input']}, avg output {tok['avg_output']}, "
                     f"avg total {tok['avg_total']}, max response {tok['max_response']}, min response {tok['min_response']}")
        cost = pm["cost"]
        cost_line = f"- Cost: actual $0 (free tier)" if cost["is_free_tier"] else "- Cost: (paid provider, no free tier)"
        if cost["reference_cost_at_paid_rate_usd"] is not None:
            cost_line += f" — would cost ${cost['reference_cost_at_paid_rate_usd']} at published paid rates for this run's volume"
        lines.append(cost_line)
        q = pm["quality"]
        lines.append(f"- Quality: overall {q['avg_overall_score']}/10, reasoning {q['avg_reasoning_score']}/10, "
                     f"risk explanation {q['avg_risk_explanation_score']}/10, action quality {q['avg_action_quality']}/10")
        lines.append(f"- Formatting: JSON valid {q['json_valid_rate_pct']}%, schema compliant {q['schema_compliant_rate_pct']}%")
        lines.append(f"- Hallucination proxy rate: {q['hallucination_rate_pct']}% (heuristic — see scoring.py docstring)")
        det = summary["determinism"].get(model)
        if det:
            lines.append(f"- Determinism ({det['cases_repeated']} cases × {det['runs_per_case']} runs): "
                         f"{det['identical_output_rate_pct']}% byte-identical, avg score variance {det['avg_score_variance']}")
        lines.append("")

    Path(md_path).write_text("\n".join(lines))


def write_html(html_path: str, summary: dict) -> None:
    charts = []
    charts.append(_svg_bar_chart("Avg latency (ms)",
                                 {m: pm["latency_ms"]["avg"] or 0 for m, pm in summary["per_model"].items()}, " ms"))
    charts.append(_svg_bar_chart("Avg total tokens per request",
                                 {m: pm["tokens"]["avg_total"] or 0 for m, pm in summary["per_model"].items()}))
    charts.append(_svg_bar_chart("Overall quality score (0-10)",
                                 {m: pm["quality"]["avg_overall_score"] for m, pm in summary["per_model"].items()}))
    charts.append(_svg_bar_chart("Reasoning score (0-10)",
                                 {m: pm["quality"]["avg_reasoning_score"] for m, pm in summary["per_model"].items()}))
    charts.append(_svg_bar_chart("Hallucination proxy rate (%)",
                                 {m: pm["quality"]["hallucination_rate_pct"] for m, pm in summary["per_model"].items()}))
    charts.append(_svg_bar_chart("Weighted leaderboard score",
                                 {row["model"]: row["weighted_score"] for row in summary["leaderboard"]}))

    rows_html = "".join(
        f"<tr><td>{i+1}</td><td>{r['model']}</td><td>{r['weighted_score']}</td><td>{r['reasoning']}</td>"
        f"<td>{r['financial_accuracy']}</td><td>{r['latency_score']}</td><td>{r['token_efficiency_score']}</td>"
        f"<td>{r['consistency_score']}</td><td>{r['formatting_score']}</td></tr>"
        for i, r in enumerate(summary["leaderboard"])
    )

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Benchmark Report — {summary['run_id']}</title>
<style>
:root {{ --bg:#0f1115; --surface:#171a21; --ink:#e8eaf0; --ink-soft:#9aa2b1; --accent:#4f7cff; --line:#262b36; }}
body {{ background:var(--bg); color:var(--ink); font-family:-apple-system,Segoe UI,sans-serif; margin:0; padding:40px 24px; }}
.wrap {{ max-width:960px; margin:0 auto; }}
h1 {{ font-size:24px; }} h2 {{ font-size:16px; color:var(--ink-soft); text-transform:uppercase; letter-spacing:.08em; margin-top:40px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; margin:12px 0; }}
th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }}
th {{ color:var(--ink-soft); font-weight:600; font-size:12px; text-transform:uppercase; }}
.charts {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:16px; }}
.chart {{ background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:16px; }}
.chart-title {{ font-size:13px; color:var(--ink-soft); margin-bottom:8px; }}
.note {{ font-size:13px; color:var(--ink-soft); }}
</style></head><body><div class="wrap">
<h1>Benchmark Report — {summary['run_id']}</h1>
<p class="note">{summary['raw_row_count']} requests recorded. Weights: {", ".join(f"{k}={v*100:.0f}%" for k, v in summary['weights'].items())}</p>
<h2>Leaderboard</h2>
<table><tr><th>Rank</th><th>Model</th><th>Weighted</th><th>Reasoning</th><th>Fin. Accuracy</th>
<th>Latency</th><th>Token Eff.</th><th>Consistency</th><th>Formatting</th></tr>{rows_html}</table>
<h2>Charts</h2>
<div class="charts">{"".join(charts)}</div>
</div></body></html>"""
    Path(html_path).write_text(html)
