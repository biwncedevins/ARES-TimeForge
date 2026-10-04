"""Static HTML report generator. TimeForge

Produces a fully self-contained local file. No network, no server, no
external resources.
"""

from __future__ import annotations

import html
from typing import List, Optional

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.reports.common import timestamp_label
from app.utils.theme import (
    ACCENT,
    BG,
    BORDER,
    DANGER,
    OK,
    PANEL,
    TEXT,
    TEXT_DIM as DIM,
)

DISCLAIMER = (
    "Timestamp interpretation is based on static format detection and "
    "should be validated against the source artifact."
)

_ESC = html.escape


def _page(body: str, title: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{title}</title>"
        "<style>"
        f"body{{background:{BG};color:{TEXT};font-family:'Segoe UI',Verdana,sans-serif;margin:0;padding:24px;}}"
        f".wrap{{max-width:960px;margin:0 auto;}}"
        f"h1{{font-size:20px;font-weight:600;margin:0 0 2px;}}"
        f".tagline{{color:{DIM};font-size:12px;margin:0 0 20px;}}"
        f".meta{{color:{DIM};font-size:11px;margin-bottom:18px;}}"
        f"h2{{font-size:12px;letter-spacing:1.5px;color:{ACCENT};text-transform:uppercase;margin:22px 0 8px;}}"
        f"table{{border-collapse:collapse;width:100%;font-size:12.5px;}}"
        f"td,th{{border:1px solid {BORDER};padding:5px 8px;text-align:left;vertical-align:top;}}"
        f"th{{background:{PANEL};color:{DIM};font-weight:600;}}"
        f"pre{{background:{PANEL};border:1px solid {BORDER};padding:10px;font-family:Consolas,monospace;font-size:12px;white-space:pre-wrap;}}"
        f".note{{color:{DIM};font-size:11px;margin-top:24px;border-top:1px solid {BORDER};padding-top:10px;}}"
        f".ok{{color:{OK};}}.warn{{color:{ACCENT};}}.err{{color:{DANGER};}}"
        "</style></head><body><div class=\"wrap\">"
        f"<h1>TimeForge</h1><p class=\"tagline\">Forensic Timestamp Lab</p>"
        f"<p class=\"meta\">Generated {_ESC(timestamp_label())} · Offline/static report</p>"
        f"{body}"
        f"<p class=\"note\">{DISCLAIMER}</p>"
        "</div></body></html>"
    )


def _kv(rows: List[tuple]) -> str:
    cells = "\n".join(
        f"<tr><th>{_ESC(k)}</th><td>{v}</td></tr>" for k, v in rows
    )
    return f"<table>{cells}</table>"


def _msg_class(level: str) -> str:
    return {"ERROR": "err", "WARNING": "warn", "INFO": ""}.get(level, "")


def render_result(res: TimestampResult) -> str:
    body: List[str] = []
    body.append("<h2>Timestamp Analysis</h2>")
    body.append(
        _kv(
            [
                ("Input", _ESC(res.raw_value)),
                ("Normalized", _ESC(res.normalized_value)),
                ("Detected Format", _ESC(res.format_name)),
                ("Confidence", f"{res.confidence}/100 ({res.confidence_level})"),
                ("UTC", _ESC(res.utc_str)),
                ("Local Time", _ESC(res.local_str)),
                ("Timezone", _ESC(res.timezone_name)),
                ("Offset", _ESC(res.local_offset)),
                ("Epoch", _ESC(res.epoch_label)),
                ("Unit", _ESC(res.unit_label)),
                ("Precision", _ESC(res.precision_note)),
            ]
        )
    )
    body.append("<h2>Verification</h2>")
    rows = [f"<tr><th>Status</th><td class=\"{_msg_class(res.verification.status)}\">{_ESC(res.verification.status)}</td></tr>"]
    for msg in res.verification.messages:
        rows.append(
            f"<tr><th>{_ESC(msg.level)}</th><td class=\"{_msg_class(msg.level)}\">"
            f"{_ESC(msg.text)}</td></tr>"
        )
    if not res.verification.messages:
        rows.append("<tr><th>Info</th><td>No issues raised.</td></tr>")
    body.append(f"<table>{''.join(rows)}</table>")
    body.append("<h2>Explanation</h2>")
    body.append(f"<pre>{_ESC(res.explanation)}</pre>")
    if res.warnings:
        body.append("<h2>Warnings</h2>")
        body.append("<ul>" + "".join(
            f"<li class=\"warn\">{_ESC(w)}</li>" for w in res.warnings
        ) + "</ul>")
    body.append("<h2>Alternative Interpretations</h2>")
    if res.alternatives:
        rows: List[tuple] = []
        for c in res.alternatives:
            utc_txt = c.utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            utc_txt += f".{c.utc_dt.microsecond:06d}"
            if c.nanosecond_remainder:
                utc_txt += f"{c.nanosecond_remainder:03d}"
            rows.append(("Format", f"<a name=\"alt\">{_ESC(c.format_name)}</a>"))
            rows.append(("UTC", _ESC(utc_txt)))
            rows.append(
                ("Confidence", f"{c.confidence}/100 ({c.confidence_level})")
            )
            rows.append(("Reason", _ESC("; ".join(c.reasons[:4]))))
        body.append(_kv(rows))
    else:
        body.append("<p>None — interpretation is unambiguous.</p>")
    return _page("\n".join(body), "TimeForge — Analysis Result")


def render_comparison(cmp: Comparison) -> str:
    body: List[str] = []
    body.append("<h2>Comparison</h2>")
    body.append(
        _kv(
            [
                ("Timestamp A input", _ESC(cmp.a_input)),
                ("A Format", _ESC(cmp.a_format)),
                ("A UTC", _ESC(cmp.a_utc)),
                ("A Local", _ESC(cmp.a_local)),
                ("Timestamp B input", _ESC(cmp.b_input)),
                ("B Format", _ESC(cmp.b_format)),
                ("B UTC", _ESC(cmp.b_utc)),
                ("B Local", _ESC(cmp.b_local)),
                ("Relation", _ESC(cmp.relation)),
                ("Difference", _ESC(cmp.difference)),
            ]
        )
    )
    if cmp.notes:
        body.append("<ul>" + "".join(f"<li>{_ESC(n)}</li>" for n in cmp.notes) + "</ul>")
    return _page("\n".join(body), "TimeForge — Comparison")


def render_history(
    history: List[TimestampResult],
    comparison: Optional[Comparison] = None,
) -> str:
    body: List[str] = [f"<h2>History ({len(history)})</h2>"]
    for res in history:
        body.append(render_result(res))
    if comparison is not None:
        body.append(render_comparison(comparison))
    return _page("\n".join(body), "TimeForge — History")