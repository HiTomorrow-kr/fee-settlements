# maintenance-bills

maintenance-bills generates maintenance fee bills as PNG images. It is a standalone program with no messaging-platform dependency, so any bot can drive it as a subprocess.

## Requirements

- Python 3.11+
- Chrome or Chromium and a matching chromedriver on `PATH`, for PNG rendering

## Usage

```bash
python -m maintenance_bills <command>
```

Every command prints a single JSON line to stdout: `{"ok": true, "data": ...}` or `{"ok": false, "error": "..."}`, with exit code 0 or 1.

Data lives at `data/` inside this repo by default; set `MAINTENANCE_BILLS_DATA_DIR` to override.
