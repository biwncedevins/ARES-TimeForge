"""Unix epoch formats (seconds / milliseconds / microseconds / nanoseconds)."""

from __future__ import annotations

from app.formats.base import IntFormat, UNIX_EPOCH


class UnixSeconds(IntFormat):
    format_id = "unix_seconds"
    name = "Unix Seconds"
    epoch_utc = UNIX_EPOCH
    epoch_label = "1970-01-01 UTC"
    unit_label = "seconds"
    unit_ns = 1_000_000_000
    typical_digits = (9, 10)
    valid_digits = (8, 12)
    explanation = (
        "Whole seconds elapsed since 1970-01-01 00:00:00 UTC. The most "
        "common representation produced by POSIX time()."
    )
    typical = "1716201234"


class UnixMilliseconds(IntFormat):
    format_id = "unix_ms"
    name = "Unix Milliseconds"
    epoch_utc = UNIX_EPOCH
    epoch_label = "1970-01-01 UTC"
    unit_label = "milliseconds"
    unit_ns = 1_000_000
    typical_digits = (12, 13)
    valid_digits = (11, 15)
    explanation = (
        "Milliseconds elapsed since the Unix epoch. Common in JSON "
        "APIs, JavaScript Date.now() and SQLite MS columns."
    )
    typical = "1716201234567"


class UnixMicroseconds(IntFormat):
    format_id = "unix_us"
    name = "Unix Microseconds"
    epoch_utc = UNIX_EPOCH
    epoch_label = "1970-01-01 UTC"
    unit_label = "microseconds"
    unit_ns = 1_000
    typical_digits = (16, 16)
    valid_digits = (15, 18)
    explanation = (
        "Microseconds elapsed since the Unix epoch. Produced by Go's "
        "Time.UnixMicro and many high-resolution logging systems."
    )
    typical = "1716201234567890"


class UnixNanoseconds(IntFormat):
    format_id = "unix_ns"
    name = "Unix Nanoseconds"
    epoch_utc = UNIX_EPOCH
    epoch_label = "1970-01-01 UTC"
    unit_label = "nanoseconds"
    unit_ns = 1
    typical_digits = (19, 19)
    valid_digits = (18, 21)
    explanation = (
        "Nanoseconds elapsed since the Unix epoch. Produced by Go's "
        "Time.UnixNano and Linux CLOCK_REALTIME. Nanosecond precision "
        "exceeds datetime resolution; the extra digits are preserved "
        "and reported separately."
    )
    typical = "1716201234567890123"