"""Comparison Engine. TimeForge"""

from __future__ import annotations

from datetime import timedelta

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.utils.formatting import format_delta


class Comparer:
    """Compare two analyzed timestamps using their precise UTC instants."""

    @staticmethod
    def compare(a: TimestampResult, b: TimestampResult) -> Comparison:
        delta_ns = b.unix_ns - a.unix_ns
        if delta_ns == 0:
            relation = "SAME TIME"
            difference = "00:00:00"
        else:
            magnitude = abs(delta_ns)
            whole_us, rem = divmod(magnitude, 1000)
            difference = format_delta(timedelta(microseconds=whole_us), rem)
            if delta_ns > 0:
                relation = "A BEFORE B"
            else:
                relation = "A AFTER B"

        notes: list[str] = []
        if a.utc_nanosecond_remainder or b.utc_nanosecond_remainder or abs(delta_ns) % 1000:
            notes.append(
                "comparison uses full nanosecond precision even if "
                "displayed times are truncated at microseconds"
            )
        else:
            notes.append("difference computed at microsecond precision")

        return Comparison(
            a_input=a.raw_value,
            b_input=b.raw_value,
            a_format=a.format_name,
            b_format=b.format_name,
            a_utc=a.utc_str,
            b_utc=b.utc_str,
            a_local=a.local_str,
            b_local=b.local_str,
            a_timezone=a.timezone_name,
            b_timezone=b.timezone_name,
            relation=relation,
            difference=difference,
            difference_ns=abs(delta_ns),
            equal=delta_ns == 0,
            notes=notes,
        )