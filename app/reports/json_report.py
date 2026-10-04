"""JSON report generator. TimeForge"""

from __future__ import annotations

import json
from typing import List, Optional

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.reports.common import comparison_to_dict, result_to_dict


def _dump(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def render_result(res: TimestampResult) -> str:
    return _dump(result_to_dict(res))


def render_comparison(cmp: Comparison) -> str:
    return _dump(comparison_to_dict(cmp))


def render_history(
    history: List[TimestampResult],
    comparison: Optional[Comparison] = None,
) -> str:
    payload = {
        "tool": "TimeForge",
        "kind": "history",
        "count": len(history),
        "entries": [result_to_dict(r) for r in history],
    }
    if comparison is not None:
        payload["comparison"] = comparison.as_dict()
    return _dump(payload)