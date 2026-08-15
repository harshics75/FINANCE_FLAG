"""CLI entrypoint. Run from backend/ inside the app container so app.agents.llm picks
up the real configured API keys:

  python -m benchmarks.cli --mode small
  python -m benchmarks.cli --mode small --resume        # continue an interrupted run
  python -m benchmarks.cli --mode medium --models groq   # single provider only
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from benchmarks import report, runner
from benchmarks.providers import PROVIDERS


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Groq vs NVIDIA Nemotron on real finance-flagging inference.")
    parser.add_argument("--mode", choices=["small", "medium", "large"], default="small")
    parser.add_argument("--models", nargs="+", default=list(PROVIDERS.keys()), choices=list(PROVIDERS.keys()))
    parser.add_argument("--run-id", default=None, help="Reuse a specific run_id (required for --resume)")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None, help="Truncate the case set to N cases (for a quick first pass)")
    parser.add_argument("--no-determinism", action="store_true", help="Skip the repeated-run determinism subset")
    parser.add_argument("--out-dir", default="benchmark_output")
    parser.add_argument("--db", default=None, help="Defaults to <out-dir>/benchmark_results.db")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = args.db or str(out_dir / "benchmark_results.db")

    if args.resume and not args.run_id:
        print("--resume requires --run-id <the run_id from the interrupted run>", file=sys.stderr)
        sys.exit(1)

    run_id = runner.run(mode=args.mode, models=args.models, db_path=db_path,
                        run_id=args.run_id, resume=args.resume, max_workers=args.max_workers,
                        limit=args.limit, include_determinism=not args.no_determinism)

    summary = report.build_summary(run_id, db_path)
    report.write_csv(str(out_dir / "benchmark_results.csv"), run_id, db_path)
    report.write_json(str(out_dir / "benchmark_summary.json"), summary)
    report.write_markdown(str(out_dir / "benchmark_report.md"), summary)
    report.write_html(str(out_dir / "benchmark_report.html"), summary)

    print(f"\nReports written to {out_dir}/:", file=sys.stderr)
    for f in ("benchmark_results.db", "benchmark_results.csv", "benchmark_summary.json",
             "benchmark_report.md", "benchmark_report.html"):
        print(f"  {out_dir / f}", file=sys.stderr)

    print("\nLeaderboard:", file=sys.stderr)
    for i, row in enumerate(summary["leaderboard"], 1):
        print(f"  {i}. {row['model']} — weighted score {row['weighted_score']}", file=sys.stderr)


if __name__ == "__main__":
    main()
