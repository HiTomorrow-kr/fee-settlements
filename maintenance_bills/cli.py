import argparse
import json
import sys

from . import calculator


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maintenance_bills")
    sub = parser.add_subparsers(dest="command", required=True)

    totals = sub.add_parser("totals", help="compute the bill figures from meter readings")
    totals.add_argument("--readings-json", required=True)
    totals.set_defaults(func=_cmd_totals)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
