import argparse
import json
import sys


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="maintenance_bills")
    parser.add_subparsers(dest="command", required=True)
    try:
        parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    print(json.dumps({"ok": False, "error": "not implemented"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    sys.exit(main())
