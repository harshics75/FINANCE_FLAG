"""Qualitative business-impact reasoning for market moves — deliberately rule-based,
not LLM-generated. A specific rupee figure ("procurement cost +Rs8.6 Cr") would
require real ERP purchasing volumes this system doesn't have; inventing one just
because a commodity moved would be a fabricated number wearing an AI costume. Instead
every move maps to qualitative, directionally-honest statements plus a risk level —
the same standard applied to every other "AI" number in this app.
"""

# Metals/energy inputs that raise cost when price rises; a manufacturer's risk framing
# flips relative to inputs whose price falling would raise cost (e.g. a currency move).
COST_HEADWIND_SERIES = {"copper", "aluminum", "oil", "brent", "natural_gas", "fed_funds_rate"}

DEPARTMENTS = {
    "copper": ["Procurement", "Finance", "Manufacturing"],
    "aluminum": ["Procurement", "Finance", "Manufacturing"],
    "oil": ["Procurement", "Finance", "Logistics"],
    "brent": ["Procurement", "Finance", "Logistics"],
    "natural_gas": ["Manufacturing", "Finance"],
    "fed_funds_rate": ["Finance", "Treasury"],
    "usd_inr": ["Finance", "Procurement", "Sales"],
}

LABELS = {
    "copper": "Copper", "aluminum": "Aluminum", "oil": "Crude Oil (WTI)",
    "brent": "Crude Oil (Brent)", "natural_gas": "Natural Gas",
    "fed_funds_rate": "US Fed Funds Rate", "usd_inr": "USD/INR",
}


def _magnitude(pct: float) -> str:
    a = abs(pct)
    if a < 2:
        return "small"
    if a < 5:
        return "moderate"
    return "large"


def _risk_level(series: str, pct: float) -> str:
    mag = _magnitude(pct)
    headwind = (pct > 0) if series in COST_HEADWIND_SERIES else (pct < 0)
    if not headwind:
        return "low"
    return {"small": "low", "moderate": "medium", "large": "high"}[mag]


def assess(series: str, change_pct: float | None) -> dict | None:
    """Returns a qualitative impact block for one series' latest move, or None if
    there's no change figure to reason about."""
    if change_pct is None or series not in LABELS:
        return None

    label = LABELS[series]
    mag = _magnitude(change_pct)
    headwind = (change_pct > 0) if series in COST_HEADWIND_SERIES else (change_pct < 0)
    direction = "increased" if change_pct > 0 else "decreased"

    bullets: list[str] = []
    if series in ("copper", "aluminum") and headwind:
        bullets = [
            "Procurement costs may increase for copper/aluminum-intensive orders.",
            "Manufacturing margins may come under pressure if pricing isn't passed through.",
            "Finance should monitor raw-material exposure on open contracts.",
            "Procurement should evaluate supplier contracts and hedging options.",
        ]
    elif series in ("copper", "aluminum") and not headwind:
        bullets = [
            "Procurement costs may ease for copper/aluminum-intensive orders.",
            "This may be a favorable window to build inventory or lock in supplier pricing.",
        ]
    elif series in ("oil", "brent") and headwind:
        bullets = [
            "Freight and logistics costs may rise.",
            "Input costs for plastics/coatings/energy-intensive processes may increase.",
            "Finance should watch fuel surcharges on inbound and outbound shipments.",
        ]
    elif series in ("oil", "brent") and not headwind:
        bullets = [
            "Freight and logistics costs may ease.",
        ]
    elif series == "natural_gas" and headwind:
        bullets = [
            "Energy-intensive manufacturing processes may see higher input costs.",
            "Finance should monitor utility/energy line items against budget.",
        ]
    elif series == "fed_funds_rate" and headwind:
        bullets = [
            "Borrowing costs may rise on any variable-rate or upcoming debt.",
            "Treasury should reassess working-capital financing costs.",
        ]
    elif series == "usd_inr":
        if change_pct > 0:
            bullets = [
                "A weaker rupee raises the cost of imported raw materials priced in USD.",
                "Export-oriented revenue may benefit from a favorable conversion rate.",
                "Finance should review FX hedges on open USD-denominated contracts.",
            ]
        else:
            bullets = [
                "A stronger rupee eases the cost of imported raw materials priced in USD.",
                "Export-oriented revenue may see a less favorable conversion rate.",
            ]
    else:
        bullets = ["Monitor this metric for downstream cost or margin effects."]

    return {
        "series": series,
        "label": label,
        "headline": f"{label} {direction} {abs(change_pct):.1f}%",
        "magnitude": mag,
        "risk_level": _risk_level(series, change_pct),
        "affected_departments": DEPARTMENTS.get(series, []),
        "business_impact": bullets,
        "basis": "Rule-based qualitative reasoning — no fabricated financial figures; "
                 "connect ERP purchasing data for quantified impact estimates.",
    }


def assess_all(market_data: dict) -> list[dict]:
    out = []
    for series, payload in market_data.items():
        if series == "usd_inr":
            continue  # no change_pct available for the FX spot rate today
        pct = payload.get("month_change_pct") if isinstance(payload, dict) else None
        result = assess(series, pct)
        if result:
            out.append(result)
    return out


def assess_weather(risk_assessments: list[dict]) -> list[dict]:
    """Same qualitative-impact shape as assess(), for hubs Open-Meteo flagged as
    high-risk. Only ever built from a real forecast — a hub with no flags produces no
    entry, rather than a manufactured "all clear" statement."""
    out = []
    for hub in risk_assessments:
        flags = hub.get("flags") or []
        if not flags or hub.get("status") != "live":
            continue
        bullets = []
        if "heavy_rain" in flags:
            bullets.append(f"Heavy rainfall forecast near {hub['hub']} could delay inbound/outbound shipments.")
        if "storm_wind" in flags:
            bullets.append(f"High winds forecast near {hub['hub']} may disrupt port/logistics operations.")
        if "heatwave" in flags:
            bullets.append(f"Heatwave forecast near {hub['hub']} may affect site labor productivity and outdoor works.")
        out.append({
            "series": f"weather_{hub['key']}", "label": hub["hub"],
            "headline": f"{hub['hub']}: {', '.join(f.replace('_', ' ') for f in flags)} forecast (next 3 days)",
            "magnitude": "moderate", "risk_level": "medium",
            "affected_departments": ["Logistics", "Operations"],
            "business_impact": bullets,
            "basis": "Open-Meteo 3-day forecast, simple disclosed thresholds — not an official IMD warning.",
        })
    return out
