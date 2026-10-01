# fee-settlements

fee-settlements fills in maintenance fee settlement sheets and saves them as images. The sheet is a single HTML page that works in a browser without a server.

## Sheet

- The page is A4 landscape with two identical copies side by side. The left copy is filled in and the right copy follows it, so both always show the same values.
- Each copy has three columns of item names and amounts, a monthly total, unpaid and late fee rows, a settlement total, meter readings for 전기, 수도, 가스, 온수, 난방 and 정수 over up to three months, the settlement period, signature lines, the bank account and the settlement amount.
- The 이미지로 저장 button saves the whole sheet as one PNG at twice the page size.

## Calculation

- The monthly total is the sum of the taxable total, the VAT and the tax-exempt total.
- The VAT is 10% of the taxable total, rounded to the nearest 10 won.
- The settlement amount is the settlement total followed by the won sign.
- Meter readings accept digits and one decimal point and show thousands separators. A month's current reading is carried into the next month's previous reading.
- Every calculated cell can be typed over.

## Usage

Open templates/bill.html in a browser, click a cell and type. The bank name label can be typed over as well.

## Command line

```bash
python -m maintenance_bills totals --readings-json '[{"name": "전기", "previous": 100, "current": 110}]'
```

The command needs Python 3.11 or later. It prints a single JSON line, `{"ok": true, "data": ...}` or `{"ok": false, "error": "..."}`, with exit code 0 or 1. The data holds the fixed fees and the metered amounts, which are usage times the unit price, and their total. Fixed fee amounts and meter unit prices are kept in bill_config.json.

Data lives at data/ inside this repo by default; set `MAINTENANCE_BILLS_DATA_DIR` to override.
