"""Correlation engine — computed only from real MarketSnapshot history, never
fabricated. Each series gets one snapshot recorded per calendar day (see
market_data_service._record_snapshots), so correlation quality grows naturally as the
app is used. Pairs without enough overlapping history report their status honestly
instead of guessing a number.
"""
from itertools import combinations

from app.models.models import MarketSnapshot

MIN_POINTS = 5

PAIR_LABELS = {
    "copper": "Copper", "aluminum": "Aluminum", "oil": "Crude Oil (WTI)",
    "brent": "Crude Oil (Brent)", "natural_gas": "Natural Gas",
    "fed_funds_rate": "US Fed Funds Rate", "usd_inr": "USD/INR",
}


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    denom = (var_x * var_y) ** 0.5
    if denom == 0:
        return None
    return round(cov / denom, 3)


def get_series_history(db, series: str) -> list[dict]:
    """Raw recorded points for one series — powers sparklines. Whatever length exists;
    no backfilling or interpolation, since that would mean inventing values."""
    rows = (
        db.query(MarketSnapshot)
        .filter(MarketSnapshot.series == series)
        .order_by(MarketSnapshot.recorded_at)
        .all()
    )
    return [{"date": r.recorded_at.date().isoformat(), "value": r.value} for r in rows]


def compute_correlations(db) -> list[dict]:
    rows = db.query(MarketSnapshot).order_by(MarketSnapshot.recorded_at).all()
    by_series: dict[str, dict[str, float]] = {}
    for r in rows:
        by_series.setdefault(r.series, {})[r.recorded_at.date().isoformat()] = r.value

    series_names = sorted(k for k in by_series if k in PAIR_LABELS)
    results = []
    for a, b in combinations(series_names, 2):
        common_days = sorted(set(by_series[a]) & set(by_series[b]))
        if len(common_days) < MIN_POINTS:
            results.append({
                "pair": [PAIR_LABELS[a], PAIR_LABELS[b]],
                "status": "insufficient_history",
                "points_collected": len(common_days),
                "points_needed": MIN_POINTS,
            })
            continue
        xs = [by_series[a][d] for d in common_days]
        ys = [by_series[b][d] for d in common_days]
        corr = _pearson(xs, ys)
        if corr is None:
            continue
        results.append({
            "pair": [PAIR_LABELS[a], PAIR_LABELS[b]],
            "status": "computed",
            "correlation": corr,
            "points_used": len(common_days),
            "strength": (
                "strong" if abs(corr) >= 0.7 else "moderate" if abs(corr) >= 0.4 else "weak"
            ),
        })
    return results
