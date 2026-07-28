"""Deterministic Financial KPI Engine.
Computes standard KPIs from extracted line items so AI narratives are grounded in real math."""
from dataclasses import dataclass

PROJECTION_DAYS = [30, 60, 90, 180, 365]
PROJECTION_LABELS = {30: "30 Days", 60: "60 Days", 90: "90 Days", 180: "6 Months", 365: "12 Months"}
PROJECTED_METRICS = ["revenue", "net_profit", "cash"]

# Synonyms used to find line items in messy statement labels
SYNONYMS: dict[str, list[str]] = {
    "revenue": ["revenue", "revenue from operations", "total revenue", "net sales", "sales", "turnover", "income from operations"],
    "cogs": ["cost of goods sold", "cogs", "cost of materials consumed", "cost of sales", "cost of revenue"],
    "gross_profit": ["gross profit", "gross margin"],
    "operating_expenses": ["operating expenses", "total expenses", "other expenses", "employee benefit expense"],
    "operating_profit": ["operating profit", "ebit", "profit before interest and tax"],
    "depreciation": ["depreciation", "depreciation and amortisation", "depreciation and amortization"],
    "interest": ["finance costs", "interest expense", "interest"],
    "net_profit": ["net profit", "profit after tax", "pat", "profit for the year", "profit for the period", "net income"],
    "pbt": ["profit before tax", "pbt"],
    "total_assets": ["total assets"],
    "current_assets": ["total current assets", "current assets"],
    "current_liabilities": ["total current liabilities", "current liabilities"],
    "total_debt": ["total debt", "borrowings", "long-term borrowings", "total borrowings"],
    "equity": ["total equity", "shareholders funds", "shareholders' funds", "equity"],
    "inventory": ["inventories", "inventory", "stock"],
    "receivables": ["trade receivables", "accounts receivable", "sundry debtors", "debtors"],
    "payables": ["trade payables", "accounts payable", "sundry creditors", "creditors"],
    "cash": ["cash and cash equivalents", "cash and bank balances", "cash"],
    "operating_cash_flow": ["net cash from operating activities", "cash flow from operating activities", "operating cash flow", "net cash generated from operating activities"],
    "investing_cash_flow": ["net cash used in investing activities", "cash flow from investing activities", "net cash from investing activities"],
    "financing_cash_flow": ["net cash used in financing activities", "cash flow from financing activities", "net cash from financing activities"],
}


def match_line_items(raw_items: dict[str, float]) -> dict[str, float]:
    """Map messy statement labels onto canonical KPI inputs (longest synonym wins)."""
    matched: dict[str, float] = {}
    for canonical, names in SYNONYMS.items():
        best_len = 0
        for label, value in raw_items.items():
            for name in names:
                if name in label and len(name) > best_len:
                    matched[canonical] = value
                    best_len = len(name)
    return matched


@dataclass
class KPIResult:
    metrics: dict[str, float]

    def as_rows(self) -> list[tuple[str, float]]:
        return list(self.metrics.items())


def _safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return a / b


def compute_kpis(items: dict[str, float], prior_items: dict[str, float] | None = None) -> KPIResult:
    g = items.get
    m: dict[str, float] = {}

    revenue = g("revenue")
    cogs = g("cogs")
    gross_profit = g("gross_profit") or (revenue - cogs if revenue is not None and cogs is not None else None)
    net_profit = g("net_profit")
    op_profit = g("operating_profit")
    dep = g("depreciation") or 0.0

    if revenue is not None:
        m["revenue"] = revenue
    if net_profit is not None:
        m["net_profit"] = net_profit
    if gross_profit is not None:
        m["gross_profit"] = gross_profit
        if (gm := _safe_div(gross_profit, revenue)) is not None:
            m["gross_margin_pct"] = round(gm * 100, 2)
    if (nm := _safe_div(net_profit, revenue)) is not None:
        m["net_margin_pct"] = round(nm * 100, 2)
    if op_profit is not None:
        m["operating_profit"] = op_profit
        if (om := _safe_div(op_profit, revenue)) is not None:
            m["operating_margin_pct"] = round(om * 100, 2)
        m["ebitda"] = op_profit + dep
    elif net_profit is not None:
        interest = g("interest") or 0.0
        pbt = g("pbt")
        base = pbt if pbt is not None else net_profit
        m["ebitda"] = base + interest + dep

    ca, cl = g("current_assets"), g("current_liabilities")
    if ca is not None and cl is not None:
        m["working_capital"] = ca - cl
        if (cr := _safe_div(ca, cl)) is not None:
            m["current_ratio"] = round(cr, 2)
            # Disclosed heuristic, not an AI judgment: industry-standard current-ratio
            # benchmark of 2.0 = fully healthy, scaled linearly 0-100.
            m["liquidity_score"] = round(min(100.0, max(0.0, cr / 2.0 * 100)), 1)
        if (qr := _safe_div(ca - (g("inventory") or 0.0), cl)) is not None:
            m["quick_ratio"] = round(qr, 2)
    if (dr := _safe_div(g("total_debt"), g("equity"))) is not None:
        m["debt_to_equity"] = round(dr, 2)
    if (da := _safe_div(g("total_debt"), g("total_assets"))) is not None:
        m["debt_ratio"] = round(da, 2)

    for key in ("cash", "inventory", "receivables", "payables",
                "operating_cash_flow", "investing_cash_flow", "financing_cash_flow"):
        if g(key) is not None:
            m[key] = g(key)

    # Working-capital efficiency (days) — requires revenue/cogs
    if revenue:
        if (dso := _safe_div(g("receivables"), revenue)) is not None:
            m["dso_days"] = round(dso * 365, 1)
    if cogs:
        if (dpo := _safe_div(g("payables"), cogs)) is not None:
            m["dpo_days"] = round(dpo * 365, 1)
        if (dio := _safe_div(g("inventory"), cogs)) is not None:
            m["dio_days"] = round(dio * 365, 1)
    if all(k in m for k in ("dso_days", "dpo_days", "dio_days")):
        m["cash_conversion_cycle_days"] = round(m["dso_days"] + m["dio_days"] - m["dpo_days"], 1)

    # Growth vs prior period
    if prior_items:
        prev_rev = prior_items.get("revenue")
        if revenue is not None and prev_rev:
            m["revenue_growth_pct"] = round((revenue - prev_rev) / abs(prev_rev) * 100, 2)
        prev_np = prior_items.get("net_profit")
        if net_profit is not None and prev_np:
            m["profit_growth_pct"] = round((net_profit - prev_np) / abs(prev_np) * 100, 2)

        # Burn rate / runway: only meaningful when cash actually declined between
        # periods — assumes ~12 months between annual fiscal periods. Omitted
        # entirely (not zero, not infinite) when cash isn't shrinking.
        prev_cash = prior_items.get("cash")
        cur_cash = g("cash")
        if cur_cash is not None and prev_cash is not None and cur_cash < prev_cash:
            burn = (prev_cash - cur_cash) / 12.0
            if burn > 0:
                m["burn_rate_monthly"] = round(burn, 2)
                m["runway_months"] = round(cur_cash / burn, 1)

    return KPIResult(metrics=m)


def project_trend(ordered_periods: list[tuple[str, dict[str, float]]]) -> dict:
    """Deterministic trend-based projection — NOT an AI forecast. Extrapolates the
    growth rate observed between the two most recent fiscal periods forward at fixed
    day-checkpoints, assuming that rate holds steady. Confidence is a plain function
    of how many historical periods back it, not a model's self-assessment."""
    if len(ordered_periods) < 2:
        return {"available": False, "reason": "Need at least 2 fiscal periods of data to compute a trend."}

    latest_period, latest = ordered_periods[-1]
    _, prior = ordered_periods[-2]

    n_periods = len(ordered_periods)
    confidence = min(30 + (n_periods - 1) * 15, 90)

    annual_rates: dict[str, float] = {}
    for metric in PROJECTED_METRICS:
        cur, prev = latest.get(metric), prior.get(metric)
        # (1 + rate) must stay positive for compound extrapolation to be real-valued —
        # a metric that flipped sign or fell >100% can't be geometrically projected.
        if cur is not None and prev not in (None, 0) and (1 + (cur - prev) / abs(prev)) > 0:
            annual_rates[metric] = (cur - prev) / abs(prev)

    milestones = []
    for days in PROJECTION_DAYS:
        frac = days / 365.0
        point: dict = {"label": PROJECTION_LABELS[days], "days": days, "confidence": confidence}
        for metric in PROJECTED_METRICS:
            base, rate = latest.get(metric), annual_rates.get(metric)
            point[metric] = round(base * ((1 + rate) ** frac), 2) if base is not None and rate is not None else None
        milestones.append(point)

    return {
        "available": True,
        "base_period": latest_period,
        "periods_used": n_periods,
        "confidence": confidence,
        "today": {metric: latest.get(metric) for metric in PROJECTED_METRICS},
        "milestones": milestones,
    }
