"""Format registry. TimeForge

New formats plug in by subclassing BaseFormat and adding an entry to
``FORMATS``; the UI and detection engine pick them up automatically.
"""

from __future__ import annotations

from typing import Dict, List

from .base import ConversionError, BaseFormat
from .unix import (
    UnixSeconds,
    UnixMilliseconds,
    UnixMicroseconds,
    UnixNanoseconds,
)
from .filetime import FileTime
from .dotnet_ticks import DotNetTicks
from .chromium import ChromiumTimestamp, WebKitTimestamp
from .mac_absolute import MacAbsoluteTime
from .ole import OleAutomationDate

FORMATS: List[BaseFormat] = [
    UnixSeconds(),
    UnixMilliseconds(),
    UnixMicroseconds(),
    UnixNanoseconds(),
    FileTime(),
    DotNetTicks(),
    ChromiumTimestamp(),
    WebKitTimestamp(),
    MacAbsoluteTime(),
    OleAutomationDate(),
]

FORMAT_BY_ID: Dict[str, BaseFormat] = {f.format_id: f for f in FORMATS}

__all__ = [
    "FORMATS",
    "FORMAT_BY_ID",
    "ConversionError",
    "BaseFormat",
]