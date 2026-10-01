# fee-settlements

[한국어](docs/readme-ko.md) | English

fee-settlements fills in maintenance fee settlement sheets and saves them as images. It is a standalone program with no messaging-platform dependency, so any bot (Telegram, Discord, ...) can drive it as a subprocess.

## Key Features

- A settlement sheet page that works in a browser without a server
- Two identical copies on one A4 landscape sheet: whatever is typed into the left copy appears in the right copy
- Direct entry of item amounts, meter readings, the settlement period, the bank account and the signature lines
- Automatic monthly total, VAT (10% of the taxable total, rounded to the nearest 10 won) and settlement amount, with every calculated cell still editable
- Meter readings with thousands separators, where a month's current reading carries into the next month's previous reading
- PNG export of the whole sheet at twice the page size
- Print button for printing the sheet on one A4 landscape page
- No install step — works via PYTHONPATH on any host with Python 3.11+

## Usage

```bash
python -m maintenance_bills totals --readings-json '[{"name": "<meter name>", "previous": 100, "current": 110}]'
python -m maintenance_bills generate --state-file sheet.json --language en --output sheet.pdf
```

Every command prints a single JSON line to stdout: `{"ok": true, "data": ...}` or `{"ok": false, "error": "..."}`, exit code 0/1. Fixed fee amounts and meter unit prices are set in bill_config.json, and each reading name must match a meter name there.

The generate command fills the page with a sheet saved by its Save JSON button and prints it to an A4 landscape PDF. It needs Chrome.

To fill in a sheet by hand in a browser, open templates/bill.html, click a cell and type, then use the save button to download the PNG.

## Integration

An orchestrator clones this repo on the same host and adds it to `PYTHONPATH`, then invokes `python -m maintenance_bills <command> ...` as a subprocess and parses the single JSON line it prints.

## Testing

```bash
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
