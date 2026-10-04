"""Presentation helpers. TimeForge"""

from __future__ import annotations

from datetime import datetime, timedelta, tzinfo, timezone
from typing import Optional


def confidence_level(score: int) -> str:
    if score >= 75:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def fraction_suffix(utc_naive: datetime, ns_remainder: int) -> str:
    """Render the fractional-seconds portion, e.g '.567123' or ''."""
    us = utc_naive.microsecond
    if us:
        fraction = f".{us:06d}"
        if ns_remainder:
            fraction += f"{ns_remainder:03d}"
        return fraction
    return ""


def format_utc(utc_naive: datetime, ns_remainder: int = 0) -> str:
    return f"{utc_naive:%Y-%m-%d %H:%M:%S}{fraction_suffix(utc_naive, ns_remainder)}"


def format_astime_aware(dt: datetime) -> str:
    """Format an aware datetime as 'YYYY-MM-DD HH:MM:SS.SSS +03:00'."""
    frac = fraction_suffix(dt.replace(tzinfo=None), 0)
    offset = offset_str(dt.utcoffset())
    return f"{dt:%Y-%m-%d %H:%M:%S}{frac} {offset}"


def offset_str(offset: Optional[timedelta]) -> str:
    if offset is None:
        return "+00:00"
    if not isinstance(offset, timedelta) and hasattr(offset, "utcoffset"):
        try:
            offset = offset.utcoffset(datetime.now(offset))
        except Exception:  # pragma: no cover - defensive
            offset = offset.utcoffset(None)
        if offset is None:
            return "+00:00"
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def format_delta(delta: timedelta, ns_remainder: int = 0) -> str:
    """Render a timedelta as [D day(s), ]HH:MM:SS[.ffffff[nnn]]."""
    total_us = delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds
    sign = "-" if total_us < 0 else ""
    total_us = abs(total_us)
    days, rem = divmod(total_us, 86_400_000_000)
    hours, rem = divmod(rem, 3_600_000_000)
    minutes, rem = divmod(rem, 60_000_000)
    seconds, us = divmod(rem, 1_000_000)
    frac = f".{us:06d}" if us else ""
    if ns_remainder:
        frac += f"{ns_remainder:03d}"
    day_part = f"{days} day(s), " if days else ""
    return f"{sign}{day_part}{hours:02d}:{minutes:02d}:{seconds:02d}{frac}"


def local_zone_name() -> str:
    """Best-effort name for the machine's local timezone."""
    try:
        return datetime.now().astimezone().tzname() or "Local"
    except Exception:  # pragma: no cover - protective only
        return "Local"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")