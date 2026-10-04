"""Plain-text forensic report generator. TimeForge"""

from __future__ import annotations

from typing import List, Optional

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.reports.common import timestamp_label

DISCLAIMER = (
    "Timestamp interpretation is based on static format detection and "
    "should be validated against the source artifact."
)


def _rule(char: str = "-", width: int = 72) -> str:
    return char * width


def render_result(res: TimestampResult) -> str:
    lines: List[str] = []
    lines.append("TIMEFORGE | Forensic Timestamp Lab")
    lines.append(_rule("="))
    lines.append(f"Generated : {timestamp_label()}")
    lines.append(_rule("="))
    lines.append("")
    lines.append("INPUT")
    lines.append(_rule())
    lines.append(f"  Raw value        : {res.raw_value}")
    lines.append(f"  Normalized       : {res.normalized_value}")
    lines.append(f"  Detected format  : {res.format_name}")
    lines.append(f"  Confidence       : {res.confidence}/100 ({res.confidence_level})")
    lines.append("")
    lines.append("TIMESTAMP")
    lines.append(_rule())
    lines.append(f"  UTC              : {res.utc_str}")
    lines.append(f"  Local time       : {res.local_str}")
    lines.append(f"  Timezone         : {res.timezone_name}")
    lines.append(f"  Offset           : {res.local_offset}")
    lines.append(f"  Epoch            : {res.epoch_label}")
    lines.append(f"  Unit             : {res.unit_label}")
    lines.append(f"  Precision        : {res.precision_note}")
    if res.fraction_display:
        lines.append(f"  Fraction (ns)    : {res.fraction_display}")
    lines.append("")
    lines.append("WHY SELECTED")
    lines.append(_rule())
    for reason in res.confidence_reasons:
        lines.append(f"  - {reason}")
    lines.append("")
    lines.append("EXPLANATION")
    lines.append(_rule())
    lines.append(f"  {res.explanation}")
    lines.append("")
    lines.append("VERIFICATION")
    lines.append(_rule())
    lines.append(f"  Status : {res.verification.status}")
    for msg in res.verification.messages:
        lines.append(f"  [{msg.level}] {msg.text}")
    if not res.verification.messages:
        lines.append("  No issues raised.")
    lines.append("")
    lines.append("WARNINGS")
    lines.append(_rule())
    if res.warnings:
        for w in res.warnings:
            lines.append(f"  ! {w}")
    else:
        lines.append("  None.")
    lines.append("")
    lines.append("ALTERNATIVE INTERPRETATIONS")
    lines.append(_rule())
    if res.alternatives:
        for idx, c in enumerate(res.alternatives, 1):
            lines.append(
                f"  {idx}. {c.format_name}  |  "
                f"{c.utc_dt:%Y-%m-%d %H:%M:%S}  |  "
                f"{c.confidence}/100 ({c.confidence_level})"
            )
            for reason in c.reasons[:3]:
                lines.append(f"      - {reason}")
    else:
        lines.append("  None — interpretation is unambiguous.")
    lines.append("")
    lines.append(_rule("="))
    lines.append(f"NOTE: {DISCLAIMER}")
    return "\n".join(lines)


def render_comparison(cmp: Comparison) -> str:
    lines: List[str] = []
    lines.append("TIMEFORGE | Forensic Timestamp Lab — COMPARISON")
    lines.append(_rule("="))
    lines.append(f"Generated : {timestamp_label()}")
    lines.append(_rule("="))
    lines.append("")
    lines.append("TIMESTAMP A")
    lines.append(_rule())
    lines.append(f"  Input   : {cmp.a_input}")
    lines.append(f"  Format  : {cmp.a_format}")
    lines.append(f"  UTC     : {cmp.a_utc}")
    lines.append(f"  Local   : {cmp.a_local}")
    lines.append("")
    lines.append("TIMESTAMP B")
    lines.append(_rule())
    lines.append(f"  Input   : {cmp.b_input}")
    lines.append(f"  Format  : {cmp.b_format}")
    lines.append(f"  UTC     : {cmp.b_utc}")
    lines.append(f"  Local   : {cmp.b_local}")
    lines.append("")
    lines.append("RESULT")
    lines.append(_rule())
    lines.append(f"  Relation   : {cmp.relation}")
    lines.append(f"  Difference : {cmp.difference}")
    if cmp.difference_ns:
        lines.append(f"  Difference : {cmp.difference_ns} ns")
    for note in cmp.notes:
        lines.append(f"  Note       : {note}")
    lines.append(_rule("="))
    lines.append(f"NOTE: {DISCLAIMER}")
    return "\n".join(lines)


def render_history(
    history: List[TimestampResult],
    comparison: Optional[Comparison] = None,
) -> str:
    out = [render_result(res) for res in history]
    if comparison is not None:
        out.append(render_comparison(comparison))
    return "\n\n\n".join(out)