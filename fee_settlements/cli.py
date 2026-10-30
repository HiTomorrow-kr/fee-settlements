import argparse
import json
import sys

from . import calculator, generator


def _print_ok(data) -> None:
    print(json.dumps({"ok": True, "data": data}, ensure_ascii=False))


def _print_err(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))


def _cmd_totals(args: argparse.Namespace) -> int:
    readings = json.loads(args.readings_json)
    try:
        totals = calculator.compute_totals(calculator.load_config(), readings)
    except (KeyError, ValueError) as e:
        _print_err(f"invalid input: {e}")
        return 1
    _print_ok(totals)
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    try:
        with open(args.state_file, encoding="utf-8") as f:
            state_text = f.read()
    except OSError as e:
        _print_err(f"cannot read the sheet file: {e}")
        return 1
    try:
        path = generator.generate_pdf(state_text, args.language, args.output or generator.default_output_path())
    except generator.GenerateError as e:
        _print_err(str(e))
        return 1
    _print_ok({"path": path})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fee_settlements")
    sub = parser.add_subparsers(dest="command", required=True)

    totals = sub.add_parser("totals", help="compute the bill figures from meter readings")
    totals.add_argument("--readings-json", required=True)
    totals.set_defaults(func=_cmd_totals)

    generate = sub.add_parser("generate", help="print a saved sheet to an A4 landscape PDF")
    generate.add_argument("--state-file", required=True, help="the JSON saved by the page")
    generate.add_argument("--language", choices=["ko", "en"], help="label language; default is the one saved in the sheet")
    generate.add_argument("--output", help="PDF path; default is a new file in the data folder")
    generate.set_defaults(func=_cmd_generate)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
