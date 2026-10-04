"""Detection Engine. TimeForge

Heuristic detection across all registered formats. Does NOT equate a
successful conversion with a correct interpretation: candidates are scored
on magnitude, digit-length bands, date plausibility and structural input
characteristics, and ambiguous inputs deliberately keep multiple
interpretations visible with per-candidate confidence.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from app.core.converter import ConversionEngine
from app.formats import FORMATS, BaseFormat, ConversionError
from app.models.timestamp_result import Candidate
from app.utils.validation import InputError, NormalizedInput, normalize_raw

MIN_SCORE = 15
AMBIGUITY_GAP = 10


class DetectionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DetectionEngine:
    """Turn a raw string into a ranked list of plausible interpretations."""

    def __init__(self, formats: Optional[List[BaseFormat]] = None):
        self.formats = formats if formats is not None else FORMATS

    def normalize(self, raw: str) -> NormalizedInput:
        try:
            return normalize_raw(raw)
        except InputError as exc:
            raise DetectionError(exc.message) from exc

    def detect(self, raw: str) -> List[Candidate]:
        """Return all plausible candidates, best first (after adjustment)."""
        norm = self.normalize(raw)
        candidates: List[Candidate] = []
        seen_keys: set = set()

        for value, base, hexflag in norm.interpretations:
            for fmt in self.formats:
                if fmt.is_float:
                    if norm.kind != "float":
                        continue
                    conversion_value = float(value)
                else:
                    if isinstance(value, Decimal):
                        if value != value.to_integral_value():
                            continue
                        conversion_value = int(value)
                    else:
                        conversion_value = value

                if not fmt.is_float and not isinstance(conversion_value, int):
                    continue

                error_hint = fmt.validate(conversion_value)
                if error_hint:
                    continue

                try:
                    cand = ConversionEngine.candidate(
                        fmt, conversion_value, base, hexflag
                    )
                except ConversionError:
                    continue

                if cand.confidence < MIN_SCORE:
                    continue

                key = (cand.unix_ns, base)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                candidates.append(cand)

        candidates.sort(
            key=lambda c: (c.confidence, _format_order(c.format_id)),
            reverse=True,
        )
        self._apply_ambiguity(candidates)
        return candidates

    def _apply_ambiguity(self, candidates: List[Candidate]) -> None:
        """Reduce over-confidence when a close second interpretation exists."""
        if len(candidates) < 2:
            return
        top, second = candidates[0], candidates[1]
        gap = top.confidence - second.confidence
        if gap <= AMBIGUITY_GAP:
            top.confidence = max(
                MIN_SCORE + 5, min(second.confidence + 6, top.confidence - 10)
            )
            top.ambiguous = True
            from app.utils.formatting import confidence_level

            top.confidence_level = confidence_level(top.confidence)
            top.reasons = list(top.reasons) + [
                "multiple plausible interpretations remain after scoring "
                "— result is inherently ambiguous"
            ]


def _format_order(fmt_id: str) -> int:
    # Deterministic tie-breaker; later-registered formats rank lower.
    try:
        for i, fmt in enumerate(FORMATS):
            if fmt.format_id == fmt_id:
                return -i
    except Exception:  # pragma: no cover
        pass
    return 0