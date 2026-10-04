"""Mac Absolute Time (seconds since 2001-01-01 UTC, Cocoa)."""

from __future__ import annotations

from app.formats.base import IntFormat, MAC_EPOCH


class MacAbsoluteTime(IntFormat):
    format_id = "mac_absolute"
    name = "Mac Absolute Time"
    epoch_utc = MAC_EPOCH
    epoch_label = "2001-01-01 UTC"
    unit_label = "seconds"
    unit_ns = 1_000_000_000
    typical_digits = (9, 10)
    valid_digits = (8, 12)
    explanation = (
        "Seconds since 2001-01-01 UTC (Cocoa NSDate timeIntervalSinceReferenceDate). "
        "Found in macOS/iOS filesystem metadata and plist artifacts. "
        "Needs +978307200 to convert to Unix seconds."
    )
    typical = "742123456"