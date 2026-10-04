"""Windows FILETIME (100 ns intervals since 1601-01-01 UTC)."""

from __future__ import annotations

from app.formats.base import IntFormat, FILE_EPOCH


class FileTime(IntFormat):
    format_id = "filetime"
    name = "Windows FILETIME"
    epoch_utc = FILE_EPOCH
    epoch_label = "1601-01-01 UTC"
    unit_label = "100 ns"
    unit_ns = 100
    typical_digits = (18, 18)
    valid_digits = (16, 19)
    explanation = (
        "Number of 100-nanosecond intervals since 1601-01-01 UTC. Found "
        "in Windows file/directory/registry timestamps, NTFS MFT entries "
        "and many forensic artifacts."
    )
    typical = "133432140000000000"