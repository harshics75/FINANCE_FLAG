"""Excel financial statement parsing into text + numeric line items."""
from dataclasses import dataclass, field

import pandas as pd

from app.parser.line_items import extract_line_items


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
        rows = [[None if pd.isna(cell) else cell for cell in row] for row in df.itertuples(index=False)]
        line_items = extract_line_items(rows)
        sheets.append(ParsedSheet(name=name, markdown=md, line_items=line_items))
    return sheets
