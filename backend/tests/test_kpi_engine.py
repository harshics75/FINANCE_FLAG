from app.analytics.kpi_engine import compute_kpis, match_line_items


def test_match_line_items_synonyms():
    raw = {"revenue from operations": 1000.0, "profit after tax": 80.0,
           "trade receivables": 200.0, "total current assets": 500.0,
           "total current liabilities": 300.0}
    m = match_line_items(raw)
    assert m["revenue"] == 1000.0
    assert m["net_profit"] == 80.0
    assert m["receivables"] == 200.0


def test_compute_margins_and_working_capital():
    items = {"revenue": 1000.0, "cogs": 600.0, "net_profit": 100.0,
             "current_assets": 500.0, "current_liabilities": 300.0,
             "receivables": 200.0, "payables": 150.0, "inventory": 120.0}
    k = compute_kpis(items).metrics
    assert k["gross_profit"] == 400.0
    assert k["gross_margin_pct"] == 40.0
    assert k["net_margin_pct"] == 10.0
    assert k["working_capital"] == 200.0
    assert k["current_ratio"] == 1.67
    assert "cash_conversion_cycle_days" in k


def test_revenue_growth_vs_prior():
    k = compute_kpis({"revenue": 1200.0}, {"revenue": 1000.0}).metrics
    assert k["revenue_growth_pct"] == 20.0
