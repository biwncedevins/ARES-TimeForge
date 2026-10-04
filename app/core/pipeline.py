"""Analysis pipeline. TimeForge

DETECT → CONVERT → EXPLAIN → VERIFY → LOCALIZE → (COMPARE → EXPORT).
Keeps the original raw value at every step.
"""

from __future__ import annotations

from typing import List, Optional

from app.core.comparer import Comparer
from app.core.detector import DetectionEngine, DetectionError
from app.core import timezone as tzutil
from app.core.verifier import VerificationEngine
from app.formats import FORMAT_BY_ID, BaseFormat
from app.models.comparison import Comparison
from app.models.timestamp_result import Candidate, TimestampResult
from app.utils import formatting
from app.utils.validation import NormalizedInput

FORENSIC_LIMIT_PLUS = 0  # no global clamp: per-format validity governs


class AnalysisError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _precision_note(unit_label: str) -> str:
    table = {
        "seconds": "seconds",
        "milliseconds": "milliseconds",
        "microseconds": "microseconds",
        "nanoseconds": "nanoseconds (sub-microsecond digits preserved)",
        "100 ns": "100-nanosecond intervals (sub-microsecond precision)",
        "days": "fractional days",
    }
    return table.get(unit_label, unit_label)


class Pipeline:
    """Coordinate detection, conversion, verification and localization."""

    def __init__(self, detector: Optional[DetectionEngine] = None):
        self.detector = detector or DetectionEngine()

    # ------------------------------------------------------------------
    def analyze(self, raw: str, tz_name: str = "Local") -> TimestampResult:
        try:
            norm: NormalizedInput = self.detector.normalize(raw)
            candidates: List[Candidate] = self.detector.detect(raw)
        except DetectionError as exc:
            raise AnalysisError(f"Analysis failed.\nReason: {exc.message}") from exc

        if not candidates:
            raise AnalysisError(
                "Analysis failed.\nReason: no plausible format interpretation "
                "exists for this value (does not match any supported format's "
                "magnitude, range or structure)."
            )

        selected = candidates[0]
        alternatives = candidates[1:]

        fmt: BaseFormat = FORMAT_BY_ID[selected.format_id]
        dt = selected.utc_dt
        ns_remainder = selected.nanosecond_remainder

        utc_str = formatting.format_utc(dt, ns_remainder)
        aware, tz_display, offset = tzutil.localize(dt, tz_name)

        local_frac = formatting.fraction_suffix(
            aware.replace(tzinfo=None), ns_remainder
        )
        local_str = f"{aware:%Y-%m-%d %H:%M:%S}{local_frac} {offset}"

        unit_value = norm.canonical
        explanation = self._explain(
            raw, norm, fmt, dt, ns_remainder, utc_str, tz_display, local_str,
            selected.confidence_level,
        )

        verification = VerificationEngine.verify(norm, selected, raw)
        warnings = verification.warning_texts()

        return TimestampResult(
            raw_value=raw.strip(),
            normalized_value=norm.canonical,
            input_is_hex_notation=norm.is_hex_notation,
            format_id=selected.format_id,
            format_name=selected.format_name,
            epoch_label=fmt.epoch_label,
            unit_label=fmt.unit_label,
            confidence=selected.confidence,
            confidence_level=selected.confidence_level,
            confidence_reasons=list(selected.reasons),
            utc_naive=dt,
            utc_nanosecond_remainder=ns_remainder,
            utc_str=utc_str,
            local_aware=aware,
            local_str=local_str,
            local_offset=offset,
            timezone_name=tz_display,
            precision_note=_precision_note(fmt.unit_label),
            fraction_display=f"+{ns_remainder} ns" if ns_remainder else "",
            explanation=explanation,
            verification=verification,
            warnings=warnings,
            alternatives=alternatives,
            unix_ns=selected.unix_ns,
            raw_magnitude=unit_value,
        )

    # ------------------------------------------------------------------
    def compare(self, a_raw: str, b_raw: str, tz_name: str = "Local") -> Comparison:
        a = self.analyze(a_raw, tz_name)
        b = self.analyze(b_raw, tz_name)
        return Comparer.compare(a, b)

    # ------------------------------------------------------------------
    @staticmethod
    def _explain(
        raw: str,
        norm: NormalizedInput,
        fmt: BaseFormat,
        dt,
        ns_remainder: int,
        utc_str: str,
        tz_display: str,
        local_str: str,
        confidence_level: str,
    ) -> str:
        basis = {
            "dec": "decimal integer",
            "hex": "hexadecimal literal",
            "float": "floating-point value",
        }.get(norm.interpretations[0][1], "numeric value")
        fraction = formatting.fraction_suffix(dt, ns_remainder)
        return (
            f"Input {raw!r} was normalized to {norm.canonical} "
            f"({basis}). "
            f"It was interpreted as {fmt.name} (epoch {fmt.epoch_label}, "
            f"unit {fmt.unit_label}) with {confidence_level}-confidence. "
            f"{norm.canonical} {fmt.unit_label} "
            f"= {dt:%Y-%m-%d %H:%M:%S}{fraction} UTC. "
            f"Localized ({tz_display}): {local_str}."
        )