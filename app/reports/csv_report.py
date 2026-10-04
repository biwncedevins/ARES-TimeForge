"""CSV report generator. TimeForge"""

from __future__ import annotations

import csv
from io import StringIO
from typing import List, Optional

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.reports.common import comparison_flat, result_flat

RESULT_FIELDS = [
    "raw_value",
    "normalized_value",
    "detected_format",
    "confidence",
    "confidence_level",
    "epoch",
    "unit",
    "utc",
    "local_time",
    "timezone",
    "offset",
    "verification",
    "warnings",
    "alternatives",
    "explanation",
]

COMPARISON_FIELDS = [
    "a_input",
    "a_format",
    "a_utc",
    "a_local",
    "b_input",
    "b_format",
    "b_utc",
    "b_local",
    "relation",
    "difference",
    "difference_ns",
    "notes",
]


def _writerow(writer, row: dict) -> None:
    writer.writerow([row.get(f, "") for f in RESULT_FIELDS])


def render_result(res: TimestampResult) -> str:
    out = StringIO()
    writer = csv.writer(out, lineterminator="\r\n")
    writer.writerow(RESULT_FIELDS)
    _writerow(writer, result_flat(res))
    return out.getvalue()


def render_comparison(cmp: Comparison) -> str:
    out = StringIO()
    writer = csv.writer(out, lineterminator="\r\n")
    writer.writerow(COMPARISON_FIELDS)
    row = comparison_flat(cmp)
    writer.writerow([row.get(f, "") for f in COMPARISON_FIELDS])
    return out.getvalue()


def render_history(
    history: List[TimestampResult],
    comparison: Optional[Comparison] = None,
) -> str:
    out = StringIO()
    writer = csv.writer(out, lineterminator="\r\n")
    writer.writerow(RESULT_FIELDS)
    for res in history:
        _writerow(writer, result_flat(res))
    if comparison is not None:
        writer.writerow([])
        writer.writerow(["comparison"])
        writer.writerow(COMPARISON_FIELDS)
        row = comparison_flat(comparison)
        writer.writerow([row.get(f, "") for f in COMPARISON_FIELDS])
    return out.getvalue()