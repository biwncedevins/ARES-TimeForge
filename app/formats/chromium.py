"""Chromium / WebKit timestamps (microseconds since 1601-01-01 UTC).

Chromium stores WebKit timestamps as microseconds since the Windows
epoch. WebKit (Safari/WebKit) uses the same representation, which is why
the two converters are numerically identical.
"""

from __future__ import annotations

from app.formats.base import IntFormat, FILE_EPOCH


class ChromiumTimestamp(IntFormat):
    format_id = "chromium"
    name = "Chromium Timestamp"
    epoch_utc = FILE_EPOCH
    epoch_label = "1601-01-01 UTC"
    unit_label = "microseconds"
    unit_ns = 1_000
    typical_digits = (17, 17)
    valid_digits = (16, 18)
    explanation = (
        "Microseconds since 1601-01-01 UTC. Used by Google Chrome in "
        "history, cookies and downloads databases."
    )
    typical = "13343214000000000"


class WebKitTimestamp(IntFormat):
    format_id = "webkit"
    name = "WebKit Timestamp"
    epoch_utc = FILE_EPOCH
    epoch_label = "1601-01-01 UTC"
    unit_label = "microseconds"
    unit_ns = 1_000
    typical_digits = (17, 17)
    valid_digits = (16, 18)
    explanation = (
        "Microseconds since 1601-01-01 UTC. WebKit (Safari) timestamps "
        "share the Chromium representation."
    )
    typical = "13343214000000000"