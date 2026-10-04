"""Verification model. TimeForge"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID = "VALID"
WARNING = "WARNING"
INVALID = "INVALID"

INFO = "INFO"
WARN = "WARNING"
ERROR = "ERROR"


@dataclass
class VerificationMessage:
    level: str
    text: str


@dataclass
class Verification:
    status: str = VALID
    messages: list[VerificationMessage] = field(default_factory=list)

    def add(self, level: str, text: str) -> None:
        self.messages.append(VerificationMessage(level=level, text=text))
        if level == ERROR and self.status != INVALID:
            self.status = INVALID
        elif level == WARN and self.status == VALID:
            self.status = WARNING

    def warning_texts(self) -> list[str]:
        return [m.text for m in self.messages if m.level in (WARN, ERROR)]