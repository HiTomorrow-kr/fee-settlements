# fee-settlements

[한국어](docs/readme-ko.md) | English

fee-settlements fills in maintenance fee settlement sheets and exports them as PNG or PDF.

## Key Features

- Fill in the sheet in a browser, with no server
- Monthly total, VAT and settlement amount are calculated automatically
- Export the sheet as a PNG, or print a saved sheet to an A4 landscape PDF

## Getting Started

```bash
git clone https://github.com/HiTomorrow-kr/fee-settlements.git
cd fee-settlements
pip install -e .
```

## Usage

To fill in a sheet by hand, open templates/bill.html in a browser, click a cell and type, then use the save button to download a PNG.

To calculate totals or print a saved sheet from the command line:

```bash
python -m fee_settlements totals --readings-json '[{"name": "<meter name>", "previous": 100, "current": 110}]'
python -m fee_settlements generate --state-file sheet.json --language en --output sheet.pdf
```

- Set fixed fee amounts and meter unit prices in bill_config.json. Each reading name must match a meter name there.
- `generate` prints a sheet saved with the Save JSON button. It needs Chrome.

## License

MIT — see [LICENSE](LICENSE).
