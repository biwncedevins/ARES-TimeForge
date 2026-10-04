"""Generate assets/timeforge.ico from assets/timeforge.svg.

Renders the SVG at multiple sizes with PySide6 (QtSvg) and packs the PNG
frames into a single multi-resolution ICO file (Vista+ PNG-in-ICO entries).

Usage:
    python tools/make_icon.py
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "assets" / "timeforge.svg"
ICO_PATH = ROOT / "assets" / "timeforge.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def render_png(size: int) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice, Qt
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QImage, QPainter

    app = QApplication.instance() or QApplication(["make_icon"])
    renderer = QSvgRenderer(str(SVG_PATH))
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError(f"Could not encode PNG for size {size}")
    buffer.close()
    return bytes(buffer.data())


def build_ico(frames: list[tuple[int, bytes]]) -> bytes:
    header = struct.pack("<HHH", 0, 1, len(frames))
    entries = b""
    payload = b""
    offset = 6 + 16 * len(frames)
    for size, png in frames:
        dim = 0 if size >= 256 else size
        entries += struct.pack(
            "<BBBBHHII",
            dim,
            dim,
            0,
            0,
            1,
            32,
            len(png),
            offset,
        )
        payload += png
        offset += len(png)
    return header + entries + payload


def main() -> int:
    if not SVG_PATH.exists():
        print(f"ERROR: {SVG_PATH} not found", file=sys.stderr)
        return 1
    frames: list[tuple[int, bytes]] = []
    for size in SIZES:
        frames.append((size, render_png(size)))
    ICO_PATH.write_bytes(build_ico(frames))
    print(f"Wrote {ICO_PATH} ({len(frames)} resolutions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())