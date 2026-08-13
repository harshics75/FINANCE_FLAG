from datetime import datetime, timedelta, timezone

from app.database.session import SessionLocal
from app.services import relevance_scoring, sector_profiles


def test_power_outranks_cement_in_sector_weight(client):
    """client fixture triggers app startup (and therefore seed_sector_profiles)."""
    with SessionLocal() as db:
        weights = sector_profiles.sector_weight_table(db)
    assert weights["power"] > weights["cement"]
    assert weights["oil_gas"] > weights["cement"]


def test_emerging_sector_gets_baseline_not_zero(client):
    with SessionLocal() as db:
        weights = sector_profiles.sector_weight_table(db)
    assert weights["data_centres"] == sector_profiles.EMERGING_BASELINE_WEIGHT
    assert weights["data_centres"] > 0


def test_export_excluded_from_sector_ranking(client):
    with SessionLocal() as db:
        weights = sector_profiles.sector_weight_table(db)
    assert "export" not in weights


def test_equal_value_power_project_outranks_cement_project():
    now = datetime.now(timezone.utc)
    power_score, _ = relevance_scoring.score(
        sector_weight=0.9, project_value_cr=5000, stage="Tender Awarded", published_at=now)
    cement_score, _ = relevance_scoring.score(
        sector_weight=0.1, project_value_cr=5000, stage="Tender Awarded", published_at=now)
    assert power_score > cement_score


def test_strategic_override_can_lift_a_low_sector_project():
    now = datetime.now(timezone.utc)
    baseline, _ = relevance_scoring.score(
        sector_weight=0.1, project_value_cr=5000, stage="Tender Awarded", published_at=now)
    overridden, _ = relevance_scoring.score(
        sector_weight=0.1, project_value_cr=5000, stage="Tender Awarded", published_at=now,
        strategic_override=True)
    assert overridden > baseline


def test_unknown_project_value_scores_neutral_not_zero():
    score, breakdown = relevance_scoring.score(sector_weight=0.5, project_value_cr=None)
    assert breakdown["value"] > 0


def test_score_is_clamped_0_to_100():
    score, _ = relevance_scoring.score(
        sector_weight=1.0, project_value_cr=1_000_000, stage="Bidding Open",
        published_at=datetime.now(timezone.utc), confidence=100, strategic_override=True)
    assert 0 <= score <= 100


def test_stale_undated_opportunity_scores_lower_than_fresh():
    fresh, _ = relevance_scoring.score(sector_weight=0.5, published_at=datetime.now(timezone.utc))
    old, _ = relevance_scoring.score(sector_weight=0.5, published_at=datetime.now(timezone.utc) - timedelta(days=180))
    undated, _ = relevance_scoring.score(sector_weight=0.5, published_at=None)
    assert fresh > old
    assert fresh > undated
