"""Conversion Engine. TimeForge"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Tuple

from app.formats.base import BaseFormat, ConversionError
from app.models.timestamp_result import Candidate


class ConversionEngine:
    """Converts a raw numeric value through a format into a UTC datetime.

    The raw value is never discarded; every converted result retains the
    original input at the pipeline level.
    """

    @staticmethod
    def convert(fmt: BaseFormat, value) -> Tuple[datetime, int, int]:
        """Return ``(utc naive dt, nanosecond remainder, unix_ns)``.

        Raises ConversionError when the value cannot be represented.
        """
        if fmt.is_float:
            return fmt.convert(value)
        if isinstance(value, Decimal):
            if value != value.to_integral_value():
                raise ConversionError(
                    f"{fmt.name} requires an integer value, got {value!r}"
                )
            value = int(value)
        if not isinstance(value, int):
            raise ConversionError(
                f"{fmt.name} requires an integer value, got {value!r}"
            )
        return fmt.convert(value)

    @staticmethod
    def candidate(
        fmt: BaseFormat,
        value,
        base: str,
        is_hex_notation: bool,
    ) -> Candidate:
        dt, ns_remainder, unix_ns = ConversionEngine.convert(fmt, value)
        score, reasons = fmt.score(value, dt, base)
        if base == "hex" and not is_hex_notation:
            score = int(score * 0.8)
            reasons.append(
                "interpreted as hexadecimal although the input was "
                "entered as decimal digits"
            )
        from app.utils.formatting import confidence_level

        return Candidate(
            format_id=fmt.format_id,
            format_name=fmt.name,
            utc_dt=dt,
            nanosecond_remainder=ns_remainder,
            confidence=min(100, score),
            confidence_level=confidence_level(min(100, score)),
            reasons=reasons,
            unix_ns=unix_ns,
        )