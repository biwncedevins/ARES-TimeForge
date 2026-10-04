"""Cross-mode resource path resolution. TimeForge"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def resource_root() -> Path:
    """Return the base directory holding bundled assets at runtime."""
    if is_frozen():
        base = getattr(sys, "_MEIPASS", None)
        if base:
            return Path(base)
    return _PROJECT_ROOT


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def icon_path() -> Path:
    ico = resource_path("assets", "timeforge.ico")
    if ico.exists():
        return ico
    return resource_path("assets", "timeforge.svg")


def app_version() -> str:
    return "1.0.0"