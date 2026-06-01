# RCT Field Tracking Manager

> A lightweight desktop app for **offline RCT follow-up surveys with randomly
> recruited crowds in public squares**.
> Paper questionnaire + barcode + USB scanner, end-to-end — no complex setup.

[中文](README.zh.md) | English

---

## 1. Overview

For randomized controlled trials (RCT) recruiting subjects on-site, this app covers:

**On-site registration → auto-assign a unique barcode → print barcoded paper
questionnaires → verify identity & mark status with a USB scanner across multiple
follow-up rounds → ledger management, export & statistics.**

It does **NOT** OCR questionnaire answers — it only handles **identity ledger and
pairing management**. All data lives locally in `data/` (a single SQLite file +
settings) and can be copied as a whole; **no database server to install**.

## 2. Features

| Module | Capability |
| --- | --- |
| Registration | Enter name / 11-digit mobile / gender / RCT group; strict phone validation; duplicate-phone warning; auto global Subject ID + barcode; preview & single/batch print (Code 128) |
| Scan & Match | Scanner pops up subject info + follow-up history; mark status (Valid / Void / Mismatch / Damaged / Lost); manual barcode/ID lookup fallback for damaged codes |
| Ledger | Full ledger; filter by ID / name / phone / group / round / status; edit, reprint, delete; one-click Excel export (SPSS-friendly) |
| Statistics | Totals, per-group counts, per-round valid / void / lost counts |
| Settings | Switch Chinese/English; barcode rule config; DB backup / restore |
| Logs | Trace register / scan / status / export / backup actions; export CSV |

## 3. Barcode Rule

```
barcode = group prefix + zero-padded sequence
  A = Intervention →  A00001, A00002 …
  B = Control      →  B00001, B00002 …
Subject ID (globally unique) = S + global sequence  →  S000001, S000002 …
```

- **One person, one barcode, reused across all rounds.**
- Prefix and digit count are configurable in Settings (affects **new** records only).

## 4. Project Layout

```
rct_tracker/
├── main.py                 entry point
├── requirements.txt        dependencies
├── run.bat                 one-click run from source (Windows)
├── build.bat               one-click build exe (Windows)
├── app/
│   ├── config.py           paths & settings
│   ├── i18n.py             zh/en internationalization
│   ├── db.py               SQLite data layer
│   ├── logger.py           operation logs
│   ├── barcode_util.py     Code128 generation & printing
│   ├── excel_export.py     Excel export
│   └── ui/                 Tkinter tab views
└── data/                   auto-created at runtime (db, backups, barcodes, logs)
```

## 5. Requirements

- OS: **Windows 7/10/11** (macOS / Linux also fine for development)
- Python **3.8+** (only for running from source; the built exe needs no Python)
- Hardware: ordinary **USB wired barcode scanner** (driver-free, acts as keyboard) + desktop printer

## 6. Quick Start (from source)

1. Install Python 3.8+ from <https://www.python.org/downloads/> — **check
   "Add Python to PATH"** during installation.
2. **Recommended:** double-click **`run.bat`** (auto-installs deps and launches).
3. Or manually:
   ```bat
   python -m pip install -r requirements.txt
   python main.py
   ```

## 7. Build a Double-Click EXE

Double-click **`build.bat`** (uses PyInstaller). Result:

```
dist\RCT_Tracker.exe   ← double-click to run, no Python needed
```

A `data\` folder is auto-created next to the exe for all data, so you can copy the
whole folder to back it up.

> Manual command:
> ```bat
> pip install pyinstaller
> pyinstaller --onefile --windowed --name RCT_Tracker --collect-all barcode main.py
> ```
> `--collect-all barcode` bundles the barcode library's font data — **do not omit it.**

## 7b. Running & Building on macOS

The app is cross-platform Python; macOS works too (`.bat` is Windows-only, use `.command` on Mac).

### Run (either way)

- **Double-click (recommended):** double-click **`run.command`** — it creates a venv,
  installs deps, and launches. If macOS says "cannot be opened / unidentified developer",
  right-click `run.command` → **Open** → **Open**, or run `chmod +x run.command` first.
- **Terminal:**
  ```bash
  cd rct_tracker
  python3 -m venv .venv && source .venv/bin/activate
  python -m pip install -r requirements.txt
  python main.py
  ```

> **About Tkinter (GUI library):** it ships with Python, it is *not* a pip package.
> If you see `ModuleNotFoundError: No module named 'tkinter'`/`_tkinter`: Homebrew users
> run `brew install python-tk`; or install the official [python.org](https://www.python.org/downloads/macos/)
> Python (Tkinter included). The system's old Python may lack it.

### Build a macOS app (.app)

Double-click **`build_mac.command`** (PyInstaller; macOS uses `--windowed` to produce a
`.app`, no `--onefile`). You get `dist/RCT_Tracker.app`. First launch may need
right-click → Open to pass Gatekeeper. Data still lives in `data/` next to the app.

### macOS differences (everything else is identical)

- **Printing:** the print page opens in your browser — press **`⌘+P`** (Windows: `Ctrl+P`).
- **Scanner:** USB HID scanners are plug-and-play on Mac too; dismiss the "Keyboard Setup Assistant" if it pops up.
- **Chinese text:** the system "PingFang SC" font is used automatically.
- **Open data folder:** the Settings button opens it in Finder.

## 8. Usage

### Registration
1. Enter name, mobile (**must be 11 digits**, otherwise blocked), gender, group.
2. Click "Save & Generate Barcode" → Subject ID and barcode are assigned and previewed.
   A duplicate-phone warning appears if the number already exists.
3. Choose to print now, or select any row in "Recent registrations" and click "Print Barcode".

### Scan & Match (multi-round follow-up)
1. Pick the **current follow-up round** (1/2/3) at the top.
2. Keep the cursor in the scan box and scan the barcode on the questionnaire.
3. The subject's info and per-round history pop up automatically.
4. Click a status button: **Valid / Void / Mismatch / Damaged / Lost** (applied to the
   current round). Use "Undo last" to revert a mistake.
5. **Damaged-code fallback:** type the barcode or Subject ID manually and click "Look up".

> A USB scanner behaves like a keyboard: it "types" the barcode and presses Enter,
> so keep the input box focused for continuous scanning.

### Ledger
- Multi-condition search; double-click a row to edit.
- "Export Excel" creates a 4-sheet workbook (see below).
- "Reprint barcode" batch-reprints selected rows (multi-select supported).
- Back up before "Delete selected" (irreversible).

### Statistics / Settings / Logs
- Statistics: totals, per-group and per-round sample counts.
- Settings: language toggle, barcode rule, backup/restore, open data folder.
- Logs: view & export all actions as CSV.

## 9. Field Notes

### A. Barcode printing
- Generates **Code 128** PNGs at 300 DPI and opens a **print page** in your browser
  (print dialog pops up automatically; press `Ctrl+P`). Batch labels auto-tile.
- Tips: use laser/thermal printers; print at **100% / actual size** (do **not**
  "shrink to fit"); keep quiet zones (already reserved) — don't crop near the bars;
  **test-scan one** printed label before mass distribution.
- On Windows you can also send an image straight to the default printer via
  `barcode_util.print_image_windows()`.

### B. Scanner setup
- Use a **USB wired, driver-free, HID keyboard-mode** 1D scanner (most cheap ones qualify).
- Plug and play. Make sure the scanner **appends Enter** after each scan (usually the
  factory default; if not, scan the "add Enter suffix" config code from its manual).
- Test in Notepad first: a scan should output characters and move to a new line.
- Keep the cursor in the scan box (the Scan tab auto-focuses it).

### C. Backup & restore
- **Real-time save:** every registration / status mark is written to the local DB instantly.
- **Auto backup:** a DB snapshot is taken on every startup (`data\backups\`).
- **Manual backup:** Settings → "Back up database now". **Back up periodically during
  field work** and copy the whole `data\` folder to a USB/cloud drive off-site.
- **Restore / rollback:** Settings → "Restore from backup" (the current DB is auto-backed-up
  first, so it's doubly safe).
- **Migrate machines:** just copy the `data\` folder over.

## 10. Export & Data Dictionary

The exported Excel has 4 sheets:

| Sheet | Purpose |
| --- | --- |
| `Data` | **Machine-friendly:** English variable names + coded values, ready for SPSS/R/Python |
| `Ledger` | **Human-friendly:** localized headers and labels |
| `Statistics` | Summary counts |
| `Dictionary` | Code → meaning mapping |

| Field | Code | Meaning |
| --- | --- | --- |
| gender | M / F / O | Male / Female / Other |
| group | A / B | Intervention / Control |
| round1–3 | (empty) | Not yet followed up |
| | valid | Valid |
| | void | Void / blank |
| | mismatch | Info mismatch |
| | damaged | Barcode damaged |
| | lost | Lost to follow-up |

## 11. FAQ

- **Barcode dependency missing?** Run `pip install python-barcode pillow openpyxl`, or use `run.bat`.
- **Garbled Chinese / boxes?** The OS lacks a CJK font; install one (Windows ships "Microsoft YaHei").
- **Scan does nothing?** Check: cursor in the scan box; scanner Enter-suffix enabled; test in Notepad.
- **Barcode won't scan?** Check print clarity & scale; reprint via the ledger.
- **Non-11-digit phone?** Strictly blocked (tweak the rule in `register_frame.py` if needed).

## 12. Storage & Privacy

- All data is **stored locally**, never uploaded — suitable for temporary field sites.
- DB: `data\rct_data.db`; backups: `data\backups\`; barcodes: `data\barcodes\`;
  text logs: `data\logs\`; exports: `exports\`.
- Subject data is sensitive — secure your backup media and dispose of it per your ethics protocol.

---
Lightweight · offline · easy to tweak. Cleanly layered (see comments in `app/`) for further development.
