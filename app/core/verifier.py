"""Verification Engine. TimeForge

Checks a selected interpretation for date-range violations, overflow,
negative/unsigned contract violations and unrealistic dates. Never issues
judgements such as "malicious" / "benign".
"""

from __future__ import annotations

from app.formats import FORMAT_BY_ID
from app.models.timestamp_result import Candidate
from app.models.verification import (
    ERROR,
    INFO,
    VALID,
    WARN,
    WARNING,
    Verification,
)
from app.utils.validation import NormalizedInput

FORENSIC_FUTURE_CUTOFF = 2100
FORENSIC_PAST_CUTOFF = 1970


class VerificationEngine:
    @staticmethod
    def verify(
        norm: NormalizedInput,
        cand: Candidate,
        raw: str,
    ) -> Verification:
        verification = Verification()
        fmt = FORMAT_BY_ID.get(cand.format_id)
        value = _value_of(norm, cand, fmt)

        if fmt is None:  # pragma: no cover - defensive
            verification.add(ERROR, "format definition not found")
            return verification

        zero = cand.unix_ns == 0

        # -- magnitude / contract checks -----------------------------------
        if fmt.format_id.startswith("unix") and value < 0:
            verification.add(
                WARN,
                "negative value indicates a timestamp before the Unix epoch "
                "(1970-01-01) — unusual for modern artifacts",
            )
        if fmt.format_id == "filetime" and value < 0:
            verification.add(
                ERROR,
                "Windows FILETIME is an unsigned 64-bit value; negative "
                "values are structurally invalid",
            )
        if fmt.format_id == "mac_absolute" and value < 0:
            verification.add(
                WARN,
                "negative Mac Absolute Time indicates a date before "
                "2001-01-01 UTC",
            )
        if fmt.format_id == "ole":
            days = float(value)
            if days < -657434:
                verification.add(
                    ERROR,
                    "OLE date is below the minimum supported value "
                    "(100-01-01)",
                )
            elif days < 1:
                verification.add(
                    WARN,
                    "OLE date is at or before the epoch and carries only a "
                    "partial day",
                )

        # -- date-range realism ------------------------------------------
        if cand.utc_dt.year > FORENSIC_FUTURE_CUTOFF:
            verification.add(
                WARN,
                f"resulting timestamp is outside the expected forensic "
                f"analysis range (year {cand.utc_dt.year} > {FORENSIC_FUTURE_CUTOFF})",
            )
        if cand.utc_dt.year < FORENSIC_PAST_CUTOFF:
            verification.add(
                WARN,
                f"resulting timestamp predates the expected forensic "
                f"analysis range (year {cand.utc_dt.year} < {FORENSIC_PAST_CUTOFF})",
            )

        if not zero and (value == 0 or cand.nanosecond_remainder):
            pass  # informational only

        # -- precision note ------------------------------------------------
        if fmt.unit_ns < 1000:
            verification.add(
                INFO,
                f"source precision is finer than microseconds "
                f"(unit: {fmt.unit_label})",
            )
        if cand.nanosecond_remainder:
            verification.add(
                INFO,
                f"sub-microsecond remainder (+{cand.nanosecond_remainder} ns) "
                "is preserved and not discarded",
            )

        if cand.ambiguous:
            verification.add(
                WARN,
                "input is ambiguous; the reported interpretation is the "
                "highest-scoring candidate, not a certainty",
            )

        return verification


def _value_of(norm: NormalizedInput, cand: Candidate, fmt) -> float | int:
    """Recover the raw numeric value that produced the leading candidate."""
    if fmt is None:
        return 0
    for value, base, _hexflag in norm.interpretations:
        try:
            if fmt.is_float:
                dt, _, unix_ns = fmt.convert(value)
            elif isinstance(value, float):
                continue
            else:
                dt, _, unix_ns = fmt.convert(int(value))
        except Exception:
            continue
        if unix_ns == cand.unix_ns:
            return float(value) if fmt.is_float else (value if isinstance(value, int) else int(value))
    return 0