"""Timezone resolution and localization. TimeForge

Uses Python's ``zoneinfo`` backed by the ``tzdata`` package on Windows so
the full IANA database is available offline.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.utils.formatting import offset_str

UTC = timezone.utc

PRESET_ZONES = [
    "UTC",
    "Local",
    "Asia/Riyadh",
    "Asia/Dubai",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Europe/London",
    "Europe/Paris",
    "America/New_York",
    "America/Los_Angeles",
    "Australia/Sydney",
    "Africa/Cairo",
]

_SENTINEL = object()
_TZDATA_PRESENT = False


def _detect_tzdata() -> bool:
    try:
        import tzdata  # noqa: F401

        return True
    except ImportError:
        return False


_TZDATA_PRESENT = _detect_tzdata()


class TimeZoneError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


_UTC_CACHE: Optional[ZoneInfo] = None


def utc_zone() -> ZoneInfo:
    global _UTC_CACHE
    if _UTC_CACHE is None:
        _UTC_CACHE = ZoneInfo("UTC")
    return _UTC_CACHE


def resolve(name: str) -> timezone | ZoneInfo:
    """Return a tzinfo object for a user-supplied zone name."""
    if name in ("Local", "local", "", None):
        raise TimeZoneError("'Local' is handled by the localizer, not resolve()")
    if name.upper() == "UTC":
        return UTC
    try:
        zone = ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        if not _TZDATA_PRESENT:
            raise TimeZoneError(
                f"timezone database is missing; install the 'tzdata' package "
                f"to resolve '{name}'"
            ) from exc
        raise TimeZoneError(f"unknown timezone: {name!r}") from exc
    return zone


def is_known_zone(name: str) -> bool:
    if name in ("Local", "") or name.upper() == "UTC":
        return True
    try:
        ZoneInfo(name)
        return True
    except ZoneInfoNotFoundError:
        return False


def localize(
    utc_naive: datetime,
    tz_name: str,
) -> Tuple[datetime, str, str]:
    """Convert a naive UTC datetime to the requested timezone.

    Returns ``(aware local datetime, display name, offset string)``.
    Ambiguity cannot occur when mapping UTC -> local; DST transitions are
    handled by ``zoneinfo``/``astimezone``.
    """
    if tz_name in ("Local", "local", ""):
        aware = utc_naive.replace(tzinfo=UTC).astimezone()
        return aware, "Local", offset_str(aware.utcoffset())
    if tz_name.upper() == "UTC":
        aware = utc_naive.replace(tzinfo=UTC)
        return aware, "UTC", offset_str(aware.utcoffset())
    zone = resolve(tz_name)
    aware = utc_naive.replace(tzinfo=UTC).astimezone(zone)
    display = zone.key if getattr(zone, "key", None) else tz_name
    return aware, display, offset_str(aware.utcoffset())


def localize_from_utc_ns(
    unix_ns: int,
    tz_name: str,
) -> Tuple[datetime, str, str]:
    micro, rem = divmod(unix_ns, 1000)
    utc_naive = datetime(1970, 1, 1) + timedelta(microseconds=micro)
    aware, name, offset = localize(utc_naive, tz_name)
    return aware, name, offset


def from_local_to_utc(
    local_naive: datetime,
    tz_name: str,
) -> Tuple[datetime, str]:
    """Map an assumed-local wall-clock time to UTC.

    Handles ambiguous (fold) and nonexistent (DST-gap) wall times.
    Returns ``(utc naive via tzinfo+fold, note)`` where note describes an
    ambiguity or gap when detected.
    """
    if tz_name in ("Local", "local", ""):
        return local_naive.astimezone(UTC).replace(tzinfo=None), "interpreted using system local timezone"
    zone = resolve(tz_name)
    first = local_naive.replace(tzinfo=zone, fold=0).astimezone(UTC).replace(tzinfo=None)
    second = local_naive.replace(tzinfo=zone, fold=1).astimezone(UTC).replace(tzinfo=None)
    if first == second:
        return first, "unambiguous wall time"
    if second > first:
        # fall-back: the wall time occurs twice; fold=0 picks the earlier one.
        return first, (
            f"ambiguous wall time (DST fall-back); resolved as fold=0, "
            f"alternative {second:%Y-%m-%d %H:%M:%S}"
        )
    # second < first: spring-forward gap — the wall time does not exist.
    return first, (
        f"wall time does not exist during the DST gap (spring-forward); "
        f"resolved as fold=0"
    )