"""Report generation dispatch. TimeForge

Supported kinds:
    json | csv | txt | html

Each entry point returns the serialized text for a result, a comparison,
or a full history (results + comparison) depending on scope.
"""

from __future__ import annotations

from typing import List, Optional

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult

QUALIFIERS = {
    "json": ".json",
    "csv": ".csv",
    "txt": ".txt",
    "html": ".html",
}


class ReportError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def render(
    kind: str,
    results: List[TimestampResult],
    comparison: Optional[Comparison] = None,
) -> str:
    from . import csv_report, html_report, json_report, txt_report

    kind = kind.lower()
    if not results and comparison is None:
        raise ReportError("nothing to export")

    if comparison is not None and not results:
        if kind == "json":
            return json_report.render_comparison(comparison)
        if kind == "csv":
            return csv_report.render_comparison(comparison)
        if kind == "txt":
            return txt_report.render_comparison(comparison)
        if kind == "html":
            return html_report.render_comparison(comparison)

    if len(results) == 1 and comparison is None:
        res = results[0]
        if kind == "json":
            return json_report.render_result(res)
        if kind == "csv":
            return csv_report.render_result(res)
        if kind == "txt":
            return txt_report.render_result(res)
        if kind == "html":
            return html_report.render_result(res)

    # History / combined
    if kind == "json":
        return json_report.render_history(results, comparison)
    if kind == "csv":
        return csv_report.render_history(results, comparison)
    if kind == "txt":
        return txt_report.render_history(results, comparison)
    if kind == "html":
        return html_report.render_history(results, comparison)

    raise ReportError(f"unsupported export format: {kind!r}")


def default_filename(kind: str) -> str:
    return f"timeforge_report{QUALIFIERS.get(kind, '.txt')}"


__all__ = ["render", "ReportError", "QUALIFIERS", "default_filename"]