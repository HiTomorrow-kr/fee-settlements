import json

import pytest

from maintenance_bills import calculator, cli

CONFIG = {"fees": [{"name": "cleaning", "amount": 18750}], "meters": [{"name": "electricity", "unit_price": 100}]}


def run_totals(capsys, monkeypatch, readings):
    monkeypatch.setattr(calculator, "load_config", lambda: CONFIG)
    code = cli.main(["totals", "--readings-json", json.dumps(readings)])
    out = capsys.readouterr().out
    assert out.count("\n") == 1  # a single JSON line
    return code, json.loads(out)


def test_totals_prints_ok_and_the_data(capsys, monkeypatch):
    code, result = run_totals(capsys, monkeypatch, [{"name": "electricity", "previous": 0, "current": 10}])
    assert code == 0
    assert result["ok"] is True
    assert result["data"]["total"] == 18750 + 1000


def test_totals_reports_an_unknown_meter_as_an_error(capsys, monkeypatch):
    code, result = run_totals(capsys, monkeypatch, [{"name": "gas", "previous": 0, "current": 1}])
    assert code == 1
    assert result["ok"] is False
    assert "unknown meter" in result["error"]


def test_unknown_command_exits_with_a_usage_error():
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["nosuch"])
    assert exit_info.value.code == 2
