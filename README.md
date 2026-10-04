# TimeForge — Forensic Timestamp Lab

Offline-first desktop tool for Windows that converts raw timestamp values
into clear timestamp interpretations: format detection, conversion,
timezone localization, verification, comparison and static export.

```text
VALUE
↓
DETECT
↓
CONVERT
↓
EXPLAIN
↓
VERIFY
↓
COMPARE
↓
EXPORT
```

Built with **Python + PySide6**, packaged as **`TimeForge.exe`** (no Python
required on the target machine).

---

## Important

- Automatic detection is **heuristic**.
- Multiple interpretations may exist for a single value.
- Confidence does **not** guarantee correctness.
- Missing or ambiguous data is **never invented** — it is reported as
  alternatives with per-candidate confidence.
- Analyst validation is required before any conclusion is drawn.

---

## Features

- Auto format detection with ranked candidates and per-candidate confidence
- Unix seconds / milliseconds / microseconds / nanoseconds
- Windows FILETIME, .NET Ticks, Chromium and WebKit timestamps
- Mac Absolute Time (Cocoa) and OLE Automation Date
- Decimal, `0x…` hex and bare-hex input
- UTC-anchored conversion with Local / IANA custom timezone support (`zoneinfo`)
- DST, ambiguous and nonexistent local wall-time handling
- Verification engine (range, overflow, unsigned contracts, unrealistic dates)
- Before/after/same-time comparison with exact timedelta differences
- Session-only history and one-click copy (UTC / Local / Full result)
- Static exports: JSON, CSV, TXT, HTML
- Pure dark / black forensics design language, dense and minimal
- Fully offline: no network, no API, no external services, no execution of input

---

## Supported Formats

| Format                | Epoch                 | Unit          | Typical representation |
| --------------------- | --------------------- | ------------- | ---------------------- |
| Unix Seconds          | 1970-01-01 UTC        | seconds       | 1716201234             |
| Unix Milliseconds     | 1970-01-01 UTC        | milliseconds  | 1716201234567          |
| Unix Microseconds     | 1970-01-01 UTC        | microseconds  | 1716201234567890       |
| Unix Nanoseconds      | 1970-01-01 UTC        | nanoseconds   | 1716201234567890123    |
| Windows FILETIME      | 1601-01-01 UTC        | 100 ns        | 133432140000000000     |
| .NET Ticks            | 0001-01-01            | 100 ns        | 638309371234567890     |
| Chromium Timestamp    | 1601-01-01 UTC        | microseconds  | 13343214000000000      |
| WebKit Timestamp      | 1601-01-01 UTC        | microseconds  | 13343214000000000      |
| Mac Absolute Time     | 2001-01-01 UTC        | seconds       | 742123456              |
| OLE Automation Date   | 1899-12-30 UTC        | days          | 45221.5                |

All formats accept decimal integers, hex (`0x…`), bare hex, floats (OLE),
and whitespace-padded input.

---

## Detection Pipeline

```text
VALUE
 ↓
NORMALIZE      → strip whitespace, validate characters, classify
                 (decimal int / hex / float / signed)
 ↓
DETECT         → run every registered format
                 magnitude · digit-length · date plausibility · input shape
 ↓
RANK           → score each candidate 0–100 (High / Medium / Low)
 ↓
AMBIGUITY      → if the second interpretation is close, confidence is
                 lowered and both interpretations are kept visible
 ↓
SELECT         → highest-scoring interpretation is primary
 ↓
EXPLAIN        → human-readable conversion narrative
 ↓
VERIFY         → range / overflow / contract / realism checks
 ↓
LOCALIZE       → UTC is authoritative, Local/Custom derived from it
 ↓
EXPORT
```

Example of the ambiguity rule — the input `742123456`:

- `Unix Seconds` → 1993-07-08 (High-ish)
- `Mac Absolute Time` → 2024-07-08 (equally plausible)

TimeForge does **not** guess. Both are listed, one is marked selected, and
confidence is reduced because multiple plausible interpretations remain.

---

## Confidence Model

Confidence is a score (0–100) built from explicit rules:

1. **Magnitude / digit-length** — does the size of the value match the
   typical or at least the valid range for that format?
2. **Date plausibility** — 1990–2035 is the modern forensic window;
   1970–2100 is plausible; representable-but-unusual gets less weight.
3. **Input shape** — `0x…`/bare-hex input nudges byte-oriented formats;
   float input points strongly to OLE; a hex reading of an all-digit string
   is discounted so it never crowds out the decimal reading.
4. **Ambiguity discount** — when the runner-up is within 10 points, the
   primary confidence is pulled down and a warning is emitted.

Levels: `High ≥ 75`, `Medium ≥ 45`, `Low < 45`. A candidate is never
reported at 100 % unless it is the only structurally valid interpretation
(and even then the analyst must verify it).

**Correctness caveat:** a successful conversion is *not* treated as proof
of the interpretation. The score is a heuristic estimate only.

---

## Timezone Handling

- Uses Python `zoneinfo` backed by the `tzdata` package on Windows so the
  full IANA database is available offline.
- **UTC is authoritative.** Local time and any custom zone (e.g.
  `Asia/Riyadh`, `America/New_York`) are derived from the UTC instant, so
  DST transitions can never make the UTC value ambiguous.
- Adjustable timezone via an editable combo: `Local`, `UTC` or any IANA name.
- Ambiguous and nonexistent local wall-times (DST fall-back / spring-forward
  gaps) are handled with the PEP 495 `fold` flag when mapping local→UTC.

---

## Verification

The verification engine checks each selected interpretation and reports:

- date-range violations (representable vs expected forensic window)
- datetime overflow (`year < 1` or `year > 9999`)
- invalid FILETIME (negative unsigned values)
- invalid OLE values (below minimum / above maximum)
- negative timestamps (pre-epoch Unix, pre-2001 Mac)
- unrealistic future or past dates

It never issues verdicts such as *malicious / benign* — only
`INFO / WARNING / ERROR` style checks with a final `VALID / WARNING / INVALID`
status.

---

## Comparison

Two arbitrary values are each analyzed, and their **precise UTC instants**
are compared with `datetime` / `timedelta` semantics:

```text
UTC A                 UTC B
A BEFORE B
Difference: 00:03:17.442333
```

Relations: `A BEFORE B`, `A AFTER B`, `SAME TIME`. Differences are rendered
to full nanosecond precision (shown as `DD day(s), HH:MM:SS.ffffff[nnn]`).

---

## Precision

- Original raw value is always preserved (`RAW VALUE` / `NORMALIZED`).
- Conversion keeps seconds, milliseconds, and microseconds exactly.
- Nanosecond inputs carry a remaining fraction that `datetime` cannot hold;
  TimeForge preserves it and reports it explicitly
  (e.g. `utc=… 54.567890123`, `fraction=+123 ns`).
- Comparison time differences are computed at full nanosecond precision.

---

## Export

| Format | Contents |
| ------ | -------- |
| JSON   | raw, normalized, format, confidence, epoch, unit, utc, local, timezone, offset, verification, warnings, alternatives, comparison |
| CSV    | key analytical fields, one row per interpretation / per comparison |
| TXT    | readable forensic report with sections and reasons |
| HTML   | self-contained static report, local-only, includes the disclaimer |

Every export is written as a plain local file. No server, no `localhost`,
no API, no network request of any kind. HTML reports include:

> Timestamp interpretation is based on static format detection and should be validated against the source artifact.

---

## Architecture

```text
TimeForge/
├── app/
│   ├── main.py                  → thin entry (delegates to top-level main.py)
│   ├── ui/
│   │   ├── main_window.py       → topbar + sidebar + QStackedWidget + status bar
│   │   ├── topbar.py            → New / Analyze / Compare / Export
│   │   ├── sidebar.py           → page navigation
│   │   ├── analyzer_view.py     → input + result grid + alternatives + copy
│   │   ├── compare_view.py      → timestamp A/B comparison
│   │   ├── formats_view.py      → format reference table
│   │   ├── history_view.py      → session history
│   │   ├── export_dialog.py     → scope/format/target export page
│   │   ├── about_view.py        → about + security statement
│   │   ├── common.py            → shared GUI helpers
│   │   └── styles.py            → pure-dark QSS design system
│   ├── core/
│   │   ├── detector.py          → heuristic detection + ambiguity handling
│   │   ├── converter.py         → per-format conversion engine
│   │   ├── timezone.py          → zoneinfo resolution / localization / fold
│   │   ├── verifier.py          → verification engine
│   │   ├── comparer.py          → comparison engine
│   │   └── pipeline.py          → workflow orchestrator
│   ├── formats/
│   │   ├── base.py              → BaseFormat + conversion/scoring primitives
│   │   ├── unix.py              → seconds / ms / µs / ns
│   │   ├── filetime.py          → Windows FILETIME
│   │   ├── dotnet_ticks.py      → .NET Ticks
│   │   ├── chromium.py          → Chromium + WebKit
│   │   ├── mac_absolute.py      → Mac Absolute Time
│   │   └── ole.py               → OLE Automation Date
│   ├── models/
│   │   ├── timestamp_result.py  → result + candidate dataclasses
│   │   ├── comparison.py
│   │   └── verification.py
│   ├── reports/
│   │   ├── json_report.py · csv_report.py · txt_report.py · html_report.py
│   │   └── common.py
│   └── utils/
│       ├── formatting.py        → date/delta/offset rendering
│       ├── validation.py        → input normalization
│       └── resources.py         → source / frozen path resolution
├── assets/                      → timeforge.svg + timeforge.ico
├── tests/                       → deterministic unittest suite + GUI smoke tests
├── tools/                       → icon builder + on-screen launch test
├── main.py                      → application entry point
├── requirements.txt
├── pyproject.toml
├── build.bat
├── run.bat
├── README.md
├── LICENSE
└── .gitignore
```

**Extensibility:** a new format is a subclass of `BaseFormat` (set the
epoch, unit, digit bands, explanation) plus one line in
`app/formats/__init__.py`. The detection engine, pipeline, UI and reports
pick it up automatically — no UI changes required.

---

## Installation (source)

```bat
python -m pip install -r requirements.txt
python main.py
```

Requires Python 3.11+. The **verified release** was built and tested on
**Python 3.11.5** with **PySide6 6.11.2**, **PyInstaller 6.22.3** and
**tzdata 2026.4**; the bundled `dist/TimeForge.exe` runs standalone without
Python.

---

## Usage

1. Type (or paste) a raw value into `ENTER TIMESTAMP VALUE`.
2. Press `Analyze` (or `Ctrl+Enter`) to run **Auto Detect**.
3. Read the result panel: format, confidence, UTC, Local, timezone, offset,
   epoch, unit, verification, warnings and explanation.
4. Inspect `POSSIBLE INTERPRETATIONS` — ambiguous inputs show alternatives
   with their own confidence instead of a single forced answer.
5. Use `Copy UTC` / `Copy Local` / `Copy Full Result` as needed.
6. `Compare` any two values; `History` keeps session-only entries;
   `Export` writes JSON / CSV / TXT / HTML files.

### Shortcuts

| Shortcut        | Action                             |
| --------------- | ---------------------------------- |
| `Ctrl+N`        | New session                        |
| `Ctrl+Enter`    | Analyze                            |
| `Ctrl+V`        | Paste & analyze (when focus is not in an edit field; native paste otherwise) |
| `Ctrl+Shift+C`  | Copy UTC                           |
| `Ctrl+E`        | Open Export                        |
| `Ctrl+F`        | Focus the value input              |

---

## Building

```bat
build.bat
```

```
dist\
└── TimeForge.exe      (one-file, windowed, icon embedded)
```

The build uses PyInstaller:

```bat
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name TimeForge --icon assets\timeforge.ico ^
    --add-data "assets;assets" --hidden-import tzdata --collect-data tzdata main.py
```

`timeforge.ico` is regenerated from `assets/timeforge.svg`
(`python tools/make_icon.py`) when missing.

---

## Testing

```bat
python -m unittest discover tests -v
```

Coverage includes deterministic values for every format, hex and `0x…`
input, invalid input, overflow, negative values, ambiguous detection,
confidence bounds, UTC, local timezone, DST ambiguity/gaps, before/after/
same comparisons, precision, verification, and all four export formats —
plus offscreen GUI smoke tests (layout, visibility, page navigation,
analyze/compare/export flows, history, timezone switching, resize).

Open the **real** window to verify rendering:

```bat
python tools\gui_launch_test.py
```

And verify the frozen EXE self-checks:

```bat
dist\TimeForge.exe --selftest
```

---

## Security Model

- **Offline by construction**: zero network APIs, zero UI, zero HTTP.
- **No execution of input**: timestamps and strings are treated strictly as
  data; no subprocess, no PowerShell, no CMD, no browser, no eval.
- No telemetry, no update checks, no cloud.
- All state is in-memory and session-only; nothing is transmitted anywhere.

The tool performs **no** external calls of any kind; the only files it
writes are the exports you explicitly create.

---

## Limitations

- Automatic detection is heuristic and can be ambiguous; confidence does not
  guarantee correctness.
- `datetime` represents times from year 1 to 9999; values outside that range
  are reported as overflow rather than silently clamped.
- Nanosecond values display the extra sub-microsecond fraction explicitly;
  it is preserved exactly for comparisons and exports.
- OLE Automation Dates beyond the standard 100-01-01 … 9999-12-31 range are
  rejected.
- Local timezone naming uses the IANA database via `tzdata`; if that package
  is absent, custom zone names resolve with the OS database only.

---

## License

MIT — see [LICENSE](LICENSE).