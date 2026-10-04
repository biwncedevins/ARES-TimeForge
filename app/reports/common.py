"""Shared report content builders. TimeForge"""

from __future__ import annotations

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.utils import formatting


def result_to_dict(res: TimestampResult) -> dict:
    return res.as_dict(include_comparison=True)


def comparison_to_dict(cmp: Comparison) -> dict:
    return {"comparison": cmp.as_dict()}


def result_flat(res: TimestampResult) -> dict:
    """Flat field set used by CSV export."""
    alternatives = "; ".join(
        f"{c.format_name} ({c.confidence_level})" for c in res.alternatives
    )
    return {
        "raw_value": res.raw_value,
        "normalized_value": res.normalized_value,
        "detected_format": res.format_name,
        "confidence": res.confidence,
        "confidence_level": res.confidence_level,
        "epoch": res.epoch_label,
        "unit": res.unit_label,
        "utc": res.utc_str,
        "local_time": res.local_str,
        "timezone": res.timezone_name,
        "offset": res.local_offset,
        "verification": res.verification.status,
        "warnings": " | ".join(res.warnings),
        "alternatives": alternatives,
        "explanation": res.explanation,
    }


def comparison_flat(cmp: Comparison) -> dict:
    return {
        "a_input": cmp.a_input,
        "a_format": cmp.a_format,
        "a_utc": cmp.a_utc,
        "a_local": cmp.a_local,
        "b_input": cmp.b_input,
        "b_format": cmp.b_format,
        "b_utc": cmp.b_utc,
        "b_local": cmp.b_local,
        "relation": cmp.relation,
        "difference": cmp.difference,
        "difference_ns": cmp.difference_ns,
        "notes": " | ".join(cmp.notes),
    }


def timestamp_label() -> str:
    return formatting.utcnow_iso()