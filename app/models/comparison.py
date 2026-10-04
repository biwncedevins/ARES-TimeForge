"""Comparison model. TimeForge"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Comparison:
    a_input: str
    b_input: str
    a_format: str
    b_format: str
    a_utc: str
    b_utc: str
    a_local: str
    b_local: str
    a_timezone: str
    b_timezone: str
    relation: str  # A BEFORE B | A AFTER B | SAME TIME | A == B
    difference: str
    difference_ns: int = 0
    equal: bool = False
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "a": {
                "input": self.a_input,
                "format": self.a_format,
                "utc": self.a_utc,
                "local_time": self.a_local,
                "timezone": self.a_timezone,
            },
            "b": {
                "input": self.b_input,
                "format": self.b_format,
                "utc": self.b_utc,
                "local_time": self.b_local,
                "timezone": self.b_timezone,
            },
            "relation": self.relation,
            "difference": self.difference,
            "difference_ns": self.difference_ns,
            "equal": self.equal,
            "notes": self.notes,
        }