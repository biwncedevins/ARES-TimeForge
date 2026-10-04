"""OLE Automation Date (floating-point days since 1899-12-30).

The OLE date accepts fractional-day values; integers are treated as a
whole number of days for compatibility.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Tuple

from app.formats.base import (
    BaseFormat,
    ConversionError,
    OLE_EPOCH,
    UNIX_EPOCH,
)

# Valid OLE range: 100-01-01 .. 9999-12-31 (in days since 1899-12-30).
OLE_MIN_DAYS = -657434.0
# Modern Excel days are ~ 40000 .. 75000.
OLE_MODERN_MIN = 40000.0
OLE_MODERN_MAX = 75000.0


class OleAutomationDate(BaseFormat):
    format_id = "ole"
    name = "OLE Automation Date"
    epoch_utc = OLE_EPOCH
    epoch_label = "1899-12-30 UTC"
    unit_label = "days"
    unit_ns = 86_400_000_000_000 * 1_000  # 1 day in ns (floating usage only)
    typical_digits = (5, 5)
    valid_digits = (4, 7)
    supports_hex = False
    is_float = True
    explanation = (
        "Floating-point number of days since 1899-12-30, as used by "
        "OLE Automation, Excel and COM/VBA Date serials."
    )
    typical = "45221.0000001"

    def convert(self, value) -> Tuple[datetime, int, int]:
        try:
            days = float(value)
        except (TypeError, ValueError) as exc:
            raise ConversionError(f"invalid OLE Automation Date value {value!r}") from exc
        if days < OLE_MIN_DAYS:
            raise ConversionError(
                f"OLE date {value} is below the minimum supported date "
                "(100-01-01)"
            )
        if days >= 2958466.0:
            raise ConversionError(
                f"OLE date {value} is beyond the maximum supported date "
                "(9999-12-31)"
            )
        try:
            dt = OLE_EPOCH + timedelta(days=days)
        except OverflowError as exc:
            raise ConversionError("OLE date out of datetime range") from exc
        if dt.year < 1 or dt.year > 9999:
            raise ConversionError("OLE date out of datetime range")
        unix_ns = (
            (dt - UNIX_EPOCH) // timedelta(microseconds=1)
        ) * 1000
        return dt, 0, unix_ns

    def score(self, value, dt: datetime, base: str) -> Tuple[int, list[str]]:
        score, reasons = super().score(value, dt, base)
        if isinstance(value, (float, Decimal)) or "." in str(value):
            score += 5
            reasons.append("fractional input matches OLE day units")
        days = float(value)
        if OLE_MODERN_MIN <= days <= OLE_MODERN_MAX:
            score += 8
            reasons.append("value is within the modern Excel serial range")
        else:
            score -= 0
            reasons.append("value is outside the common Excel serial range")
        return min(100, score), reasons

    def validate(self, value) -> Optional[str]:
        return None