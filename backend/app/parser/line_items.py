"""Shared heuristic line-item extraction, usable against Excel rows (typed cells)
or PDF table rows (string cells): the first label-like cell in a row is the
line-item name. Statutory statements commonly show the current period next to
one or more comparative (prior-period) columns, so when a fiscal_period is
given we locate the column whose header date range actually matches it,
instead of assuming the value is the first or last numeric cell in the row."""
import re

_NUM_RE = re.compile(r"^\(?-?[\d,]+\.?\d*\)?%?$")
_YEAR_RE = re.compile(r"(?:19|20)\d{2}")
_FY_RE = re.compile(r"^FY(\d{4})-(\d{2})$")


def _to_number(cell) -> float | None:
    if isinstance(cell, bool):
        return None
    if isinstance(cell, (int, float)):
        return float(cell)
    if not isinstance(cell, str):
        return None
    s = cell.strip().replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    if not s or not _NUM_RE.match(s):
        return None
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()%")
    if not s or s == "-":
        return None
    try:
        value = float(s)
    except ValueError:
        return None
    return -value if negative else value


def _target_end_year(fiscal_period: str | None) -> int | None:
    """FY2024-25 covers Apr 2024-Mar 2025, so statements describe it by its end year, 2025."""
    if not fiscal_period:
        return None
    m = _FY_RE.match(fiscal_period)
    return int(m.group(1)) + 1 if m else None


def _find_period_column(rows, target_end_year: int) -> int | None:
    """Scan header rows for the column whose date range ends in target_end_year.
    Only returns a column when exactly one match is found, to stay safe on
    layouts we don't recognize."""
    last_year_by_col: dict[int, int] = {}
    for row in rows[:6]:
        for idx, cell in enumerate(row):
            if isinstance(cell, str):
                years = _YEAR_RE.findall(cell)
                if years:
                    last_year_by_col[idx] = int(years[-1])
    matches = [idx for idx, year in last_year_by_col.items() if year == target_end_year]
    return matches[0] if len(matches) == 1 else None


def extract_line_items(rows, fiscal_period: str | None = None) -> dict[str, float]:
    """rows: iterable of iterables of cells (str, int, float, or None)."""
    rows = list(rows)
    target_end_year = _target_end_year(fiscal_period)
    period_col = _find_period_column(rows, target_end_year) if target_end_year else None

    items: dict[str, float] = {}
    for row in rows:
        label = None
        for cell in row:
            if isinstance(cell, str) and cell.strip() and _to_number(cell) is None:
                label = cell.strip().lower()
                break
        if label is None:
            continue

        if period_col is not None and period_col < len(row):
            value = _to_number(row[period_col])
        else:
            value = None
            for cell in row:
                num = _to_number(cell)
                if num is not None:
                    value = num
        if value is not None:
            items[label] = value
    return items
