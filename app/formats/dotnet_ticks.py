""".NET Ticks (100 ns intervals since 0001-01-01)."""

from __future__ import annotations

from app.formats.base import IntFormat, ANNO_DOMINI_EPOCH


class DotNetTicks(IntFormat):
    format_id = "dotnet_ticks"
    name = ".NET Ticks"
    epoch_utc = ANNO_DOMINI_EPOCH
    epoch_label = "0001-01-01"
    unit_label = "100 ns"
    unit_ns = 100
    typical_digits = (18, 18)
    valid_digits = (17, 20)
    explanation = (
        "Number of 100-nanosecond intervals since 0001-01-01 (proleptic "
        "Gregorian). DateTime.Ticks in .NET / C#. Equal to Windows "
        "FILETIME + 116444736000000000."
    )
    typical = "638309371234567890"