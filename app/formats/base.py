"""Base class for timestamp formats. TimeForge"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import ClassVar, Optional, Tuple

# Naive UTC reference epochs
UNIX_EPOCH = datetime(1970, 1, 1)
FILE_EPOCH = datetime(1601, 1, 1)
ANNO_DOMINI_EPOCH = datetime(1, 1, 1)
MAC_EPOCH = datetime(2001, 1, 1)
OLE_EPOCH = datetime(1899, 12, 30)


class ConversionError(Exception):
    """Raised when a numeric value cannot be represented by a format."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BaseFormat:
    """A timestamp format: how to convert a raw value to a UTC datetime.

    Subclasses only need to declare metadata and optionally refine
    :meth:`score` / :meth:`convert`.
    """

    format_id: ClassVar[str] = "base"
    name: ClassVar[str] = "Base"
    epoch_utc: ClassVar[Optional[datetime]] = UNIX_EPOCH
    epoch_label: ClassVar[str] = "1970-01-01 UTC"
    unit_label: ClassVar[str] = "seconds"
    unit_ns: ClassVar[int] = 1_000_000_000
    typical_digits: ClassVar[Tuple[int, int]] = (9, 10)
    valid_digits: ClassVar[Tuple[int, int]] = (8, 12)
    supports_hex: ClassVar[bool] = True
    is_float: ClassVar[bool] = False
    explanation: ClassVar[str] = ""
    typical: ClassVar[str] = ""

    # -- conversion -------------------------------------------------------

    def convert(self, value: int) -> Tuple[datetime, int, int]:
        """Convert a raw integer to (utc dt, nanosecond remainder, unix_ns).

        ``utc dt`` is naive UTC floored to microseconds; the
        nanosecond remainder (0..999) preserves sub-microsecond precision.
        ``unix_ns`` is the exact count of nanoseconds from the Unix epoch.
        """
        total_ns = value * self.unit_ns
        whole_us, rem_ns = divmod(total_ns, 1000)
        try:
            dt = self.epoch_utc + timedelta(microseconds=whole_us)
        except OverflowError as exc:  # pragma: no cover - python guards years
            raise ConversionError(
                f"{self.name} value out of datetime range"
            ) from exc
        if dt.year < 1 or dt.year > 9999:
            raise ConversionError(
                f"resulting {self.name} datetime ({dt:%Y-%m-%d}) falls "
                "outside the representable range [1 .. 9999]"
            )
        unix_ns = (dt - UNIX_EPOCH) // timedelta(microseconds=1) * 1000 + rem_ns
        return dt, rem_ns, unix_ns

    # -- scoring ----------------------------------------------------------

    def score(self, value, dt: datetime, base: str) -> Tuple[int, list[str]]:
        reasons: list[str] = []
        score = 0

        if self.is_float:
            digits = len(str(abs(int(value))))
        else:
            digits = len(str(abs(value)))

        tmin, tmax = self.typical_digits
        vmin, vmax = self.valid_digits
        if tmin <= digits <= tmax:
            score += 40
            reasons.append(
                f"{digits}-digit magnitude matches the typical "
                f"{self.name} range"
            )
        elif vmin <= digits <= vmax:
            score += 22
            reasons.append(
                f"{digits}-digit magnitude is inside the valid but "
                f"non-typical {self.name} range"
            )
        else:
            reasons.append(
                f"{digits}-digit magnitude does not match typical "
                f"{self.name} magnitudes"
            )

        year = dt.year
        if 1990 <= year <= 2035:
            score += 35
            reasons.append(
                "date is within the expected modern forensic "
                "analysis range (1990-2035)"
            )
        elif 1970 <= year <= 2100:
            score += 26
            reasons.append("date is plausible (1970-2100)")
        elif 1601 <= year <= 9999:
            score += 10
            reasons.append(
                "date is representable but outside the expected "
                "forensic analysis range"
            )

        if self.is_float:
            score += 5
            reasons.append("floating-point input is characteristic of OLE")

        if base == "hex" and self.supports_hex:
            score += 3
            reasons.append("hex notation is common for this format")

        return min(100, score), reasons

    def validate(self, value) -> Optional[str]:
        """Return an error string if the raw value is structurally invalid."""
        return None


class IntFormat(BaseFormat):
    """Integer format that validates its input is an integer."""

    def validate(self, value) -> Optional[str]:
        if isinstance(value, float) and not value.is_integer():
            return f"{self.name} requires an integer value, got {value!r}"
        return None