"""Append-only CSV writer for commute log."""

import csv
from pathlib import Path
from .config import CSV_COLUMNS


def append_row(path, row):
    path = Path(path)
    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({col: row.get(col, "") for col in CSV_COLUMNS})
