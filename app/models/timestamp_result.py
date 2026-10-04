"""Result model. TimeForge"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from .verification import Verification


@dataclass
class Candidate:
    """A single plausible interpretation produced by the detection engine.

    ``utc_dt`` is stored as a naive UTC datetime extended with an integer
    nanosecond remainder so sub-microsecond precision is never lost.
    """

    format_id: str
    format_name: str
    utc_dt: datetime
    nanosecond_remainder: int = 0
    confidence: int = 0
    confidence_level: str = "Low"
    reasons: list[str] = field(default_factory=list)
    unix_ns: int = 0
    ambiguous: bool = False


@dataclass
class TimestampResult:
    """Complete analysis of a single raw timestamp value."""

    raw_value: str
    normalized_value: str
    input_is_hex_notation: bool

    format_id: str
    format_name: str
    epoch_label: str
    unit_label: str

    confidence: int
    confidence_level: str
    confidence_reasons: list[str]

    utc_naive: datetime
    utc_nanosecond_remainder: int
    utc_str: str
    local_aware: Optional[datetime]
    local_str: str
    local_offset: str
    timezone_name: str

    precision_note: str
    fraction_display: str
    explanation: str

    verification: Verification
    warnings: list[str]
    alternatives: list[Candidate]

    unix_ns: int
    raw_magnitude: str

    def utc_datetime(self) -> datetime:
        return self.utc_naive.replace(tzinfo=None) + timedelta(
            microseconds=0
        ) + timedelta(microseconds=self.utc_nanosecond_remainder // 1000)

    def as_dict(self, include_comparison: bool = True) -> dict:
        data = {
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "detected_format": self.format_name,
            "format_id": self.format_id,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
            "epoch": self.epoch_label,
            "unit": self.unit_label,
            "utc": self.utc_str,
            "local_time": self.local_str,
            "timezone": self.timezone_name,
            "offset": self.local_offset,
            "precision": self.precision_note,
            "fraction": self.fraction_display,
            "explanation": self.explanation,
            "verification": {
                "status": self.verification.status,
                "messages": [
                    {"level": m.level, "text": m.text}
                    for m in self.verification.messages
                ],
            },
            "warnings": self.warnings,
            "confidence_reasons": self.confidence_reasons,
            "alternatives": [
                {
                    "format": c.format_name,
                    "utc": _fmt_dt(c.utc_dt, c.nanosecond_remainder),
                    "confidence": c.confidence,
                    "confidence_level": c.confidence_level,
                    "reasons": c.reasons,
                }
                for c in self.alternatives
            ],
        }
        if include_comparison:
            data["comparison"] = None
        return data


def _fmt_dt(dt: datetime, ns_remainder: int) -> str:
    s = dt.strftime("%Y-%m-%d %H:%M:%S")
    base = dt.microsecond
    if ns_remainder:
        return f"{s}.{base:06d}{ns_remainder:03d}"
    return f"{s}.{base:06d}"