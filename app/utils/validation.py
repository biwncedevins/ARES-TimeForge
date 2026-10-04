"""Input normalization and validation. TimeForge"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import List, Tuple, Union

Numeric = Union[int, Decimal, float]


class InputError(Exception):
    """Raised for structurally invalid raw input."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class NormalizedInput:
    """A parsed, validated raw timestamp value.

    ``interpretations`` lists every numeric reading that should be fed to
    the detection engine. For a plain decimal integer the only reading is
    decimal; for an all-digit string a hex reading is also offered as a
    low-confidence alternative when it produces a plausible date.
    """

    raw: str
    canonical: str
    kind: str  # "int" | "float"
    is_hex_notation: bool
    digit_count: int
    negative: bool
    interpretations: List[Tuple[Numeric, str, bool]]  # (value, base, hex_notation)


def _parse_decimal(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise InputError(f"not a valid decimal integer: {text!r}") from exc
    return value


def _parse_bare_hex(text: str) -> int:
    try:
        return int(text, 16)
    except ValueError as exc:
        raise InputError(f"not a valid hexadecimal value: {text!r}") from exc


def normalize_raw(raw: str) -> NormalizedInput:
    """Normalize a raw input string into numeric readings.

    Raises InputError with a human-readable reason when the string cannot
    represent any supported timestamp.
    """
    text = raw.strip()
    if not text:
        raise InputError("input is empty")

    allowed = set("0123456789abcdefABCDEFxX+-.")
    bad = sorted({c for c in text if c not in allowed})
    if bad:
        raise InputError(
            f"contains invalid characters: {' '.join(repr(c) for c in bad)}"
        )

    if text.startswith(("+0x", "-0x")):
        sign = -1 if text.startswith("-") else 1
        digits = text.lstrip("+-")[2:]
        if not digits or not all(c in "0123456789abcdefABCDEF" for c in digits):
            raise InputError(f"malformed hex literal: {text!r}")
        value = sign * int(digits, 16) if digits else 0
        return NormalizedInput(
            raw=raw,
            canonical=str(value),
            kind="int",
            is_hex_notation=True,
            digit_count=len(str(abs(value))),
            negative=value < 0,
            interpretations=[(value, "hex", True)],
        )

    if text.lower().startswith("0x"):
        digits = text[2:]
        if not digits or not all(c in "0123456789abcdefABCDEF" for c in digits):
            raise InputError(f"malformed hex literal: {text!r}")
        value = int(digits, 16)
        return NormalizedInput(
            raw=raw,
            canonical=str(value),
            kind="int",
            is_hex_notation=True,
            digit_count=len(digits),
            negative=value < 0,
            interpretations=[(value, "hex", True)],
        )

    if "." in text:
        try:
            value = Decimal(text)
        except InvalidOperation as exc:
            raise InputError(f"not a valid number: {text!r}") from exc
        return NormalizedInput(
            raw=raw,
            canonical=format(value, "f").rstrip("0").rstrip(".") or "0",
            kind="float",
            is_hex_notation=False,
            digit_count=len(str(abs(int(value)))),
            negative=value < 0,
            interpretations=[(value, "float", False)],
        )

    if text.startswith(("+", "-")) and not text[1:].isdigit():
        raise InputError(f"invalid characters after sign: {text!r}")

    if text.isdigit():
        value = _parse_decimal(text)
        interp: List[Tuple[Numeric, str, bool]] = [(value, "dec", False)]
        # All-digit strings are always interpreted as decimal. A hex reading
        # is only added when length/parity suggests a hex artifact.
        if len(text) >= 8:
            hex_value = _parse_bare_hex(text)
            if hex_value != value:
                interp.append((hex_value, "hex", False))
        return NormalizedInput(
            raw=raw,
            canonical=text,
            kind="int",
            is_hex_notation=False,
            digit_count=len(text),
            negative=value < 0,
            interpretations=interp,
        )

    if text.lstrip("+-").isdigit():
        value = _parse_decimal(text)
        return NormalizedInput(
            raw=raw,
            canonical=str(value),
            kind="int",
            is_hex_notation=False,
            digit_count=len(str(abs(value))),
            negative=value < 0,
            interpretations=[(value, "dec", False)],
        )

    # Bare hex with at least one a-f letter.
    if text.isalnum():
        value = _parse_bare_hex(text)
        return NormalizedInput(
            raw=raw,
            canonical=str(value),
            kind="int",
            is_hex_notation=True,
            digit_count=len(text),
            negative=value < 0,
            interpretations=[(value, "hex", True)],
        )

    raise InputError(f"unrecognized timestamp input: {text!r}")