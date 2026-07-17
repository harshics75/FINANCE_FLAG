"""Excel financial statement parsing into text + numeric line items."""
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ParsedSheet:
    name: str
    markdown: str
    line_items: dict[str, float] = field(default_factory=dict)


def parse_excel(path: str) -> list[ParsedSheet]:
    sheets: list[ParsedSheet] = []
    xls = pd.ExcelFile(path)
    for name in xls.sheet_names:
        df = xls.parse(name, header=None).dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            continue
        md = df.head(200).to_markdown(index=False)
        line_items = _extract_line_items(df)
        sheets.append(ParsedSheet(name=name, markdown=md, line_items=line_items))
    return sheets


def _extract_line_items(df: pd.DataFrame) -> dict[str, float]:
    """Heuristic: first text cell in a row is the label, last numeric cell is the value."""
    items: dict[str, float] = {}
    for _, row in df.iterrows():
        label, value = None, None
        for cell in row:
            if label is None and isinstance(cell, str) and cell.strip():
                label = cell.strip().lower()
            if isinstance(cell, (int, float)) and not pd.isna(cell):
                value = float(cell)
        if label and value is not None:
            items[label] = value
    return items
