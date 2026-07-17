"""Shared heuristic line-item extraction, usable against Excel rows (typed cells)
or PDF table rows (string cells): the first label-like cell in a row is the
line-item name, the last numeric cell is its value."""
import re

_NUM_RE = re.compile(r"^\(?-?[\d,]+\.?\d*\)?%?$")


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


def extract_line_items(rows) -> dict[str, float]:
    """rows: iterable of iterables of cells (str, int, float, or None)."""
    items: dict[str, float] = {}
    for row in rows:
        label, value = None, None
        for cell in row:
            if label is None and isinstance(cell, str) and cell.strip() and _to_number(cell) is None:
                label = cell.strip().lower()
            num = _to_number(cell)
            if num is not None:
                value = num
        if label and value is not None:
            items[label] = value
    return items
