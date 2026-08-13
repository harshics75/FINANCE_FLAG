"""Stardrive's historical FY23-24 enquiry/order performance per sector — the business-
history input to relevance_scoring.py. Seeded once at startup (see main.py:seed_sector_profiles,
mirroring seed_admin()) from a fixed table; not user-editable yet.

sector_weight() is what makes a new Power project outrank an equal-value Cement project
without hardcoding "Power = 10, Cement = 2" per sector: each sector's weight is a blend of
its historical enquiry share, order share, and conversion rate, all normalized against the
other sectors in the table. Emerging sectors (Data Centres, Semiconductor, EV, ...) have no
historical row and always get EMERGING_BASELINE_WEIGHT, never inherit an established sector's
exposure — see opportunity_extraction_service.py for where is_emerging is set.
"""
from sqlalchemy.orm import Session

from app.models.models import SectorProfile

# (key, label, tier, dimension, enquiry_cr, orders_cr, conversion_pct)
# Source: Stardrive FY23-24 enquiry/order data as supplied by management.
SEED_TABLE: list[tuple[str, str, int, str, float, float, float]] = [
    ("power", "Power", 1, "sector", 44.15, 10.72, 24.3),
    ("oil_gas", "Oil & Gas", 1, "sector", 30.17, 6.69, 22.2),
    ("steel", "Steel", 2, "sector", 24.32, 4.57, 18.8),
    ("export", "Export", 2, "channel", 41.21, 6.60, 16.0),
    ("solar", "Solar / Renewable Energy", 3, "sector", 8.55, 1.34, 15.7),
    ("water", "Water", 4, "sector", 20.86, 1.84, 8.8),
    ("mining_infra_others", "Mining / Infrastructure / Others", 4, "sector", 15.88, 0.0, 0.0),
    ("cement", "Cement", 5, "sector", 15.22, 0.45, 3.0),
]

# Emerging sectors: no historical Stardrive exposure, tracked separately per spec — a new
# opportunity here is always labelled "EMERGING OPPORTUNITY", never implied to be a core market.
EMERGING_SECTORS = {
    "data_centres": "Data Centres",
    "semiconductor": "Semiconductor Fabs",
    "ev_manufacturing": "EV Manufacturing",
    "battery_plants": "Battery Plants",
    "industrial_parks": "Industrial Parks",
    "airports": "Airports",
    "metro_rail": "Metro / Rail",
}
EMERGING_BASELINE_WEIGHT = 0.35  # medium — deliberately below any core sector's typical weight

# Blend weights for sector_weight(); must sum to 1.0.
ENQUIRY_SHARE_WEIGHT = 0.4
ORDER_SHARE_WEIGHT = 0.3
CONVERSION_WEIGHT = 0.3


def seed_sector_profiles(db: Session) -> None:
    """Idempotent seed, called at app startup alongside seed_admin()."""
    if db.query(SectorProfile.id).first():
        return
    for key, label, tier, dimension, enquiry_cr, orders_cr, conversion_pct in SEED_TABLE:
        db.add(SectorProfile(key=key, label=label, tier=tier, dimension=dimension,
                              enquiry_cr=enquiry_cr, orders_cr=orders_cr, conversion_pct=conversion_pct))
    db.commit()


def list_sector_profiles(db: Session, dimension: str | None = None) -> list[SectorProfile]:
    q = db.query(SectorProfile)
    if dimension:
        q = q.filter(SectorProfile.dimension == dimension)
    return q.order_by(SectorProfile.tier).all()


def _normalize(values: dict[str, float]) -> dict[str, float]:
    """Min-max normalize to [0, 1]; a flat input (all equal) normalizes to 1.0 for all —
    no signal to rank on, so nobody gets penalized."""
    lo, hi = min(values.values()), max(values.values())
    if hi == lo:
        return {k: 1.0 for k in values}
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


def sector_weight_table(db: Session) -> dict[str, float]:
    """Returns {sector_key: weight in [0,1]} for every SECTOR-dimension profile (Export,
    being a channel, is excluded from the sector ranking) plus every emerging sector at
    EMERGING_BASELINE_WEIGHT."""
    profiles = list_sector_profiles(db, dimension="sector")
    if not profiles:
        return dict.fromkeys(EMERGING_SECTORS, EMERGING_BASELINE_WEIGHT)

    enquiry_norm = _normalize({p.key: p.enquiry_cr for p in profiles})
    orders_norm = _normalize({p.key: p.orders_cr for p in profiles})
    conversion_norm = _normalize({p.key: p.conversion_pct for p in profiles})

    weights = {
        p.key: round(
            ENQUIRY_SHARE_WEIGHT * enquiry_norm[p.key]
            + ORDER_SHARE_WEIGHT * orders_norm[p.key]
            + CONVERSION_WEIGHT * conversion_norm[p.key],
            4,
        )
        for p in profiles
    }
    weights.update(dict.fromkeys(EMERGING_SECTORS, EMERGING_BASELINE_WEIGHT))
    return weights


def sector_weight(db: Session, sector_key: str) -> float:
    return sector_weight_table(db).get(sector_key, EMERGING_BASELINE_WEIGHT)
