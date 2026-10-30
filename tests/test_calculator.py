import json

import pytest

from fee_settlements import calculator

CONFIG = {
    "fees": [{"name": "cleaning", "amount": 18750}, {"name": "security", "amount": 11330}],
    "meters": [{"name": "electricity", "unit_price": 100}, {"name": "water", "unit_price": 100.4}],
}


def test_meter_amount_is_usage_times_unit_price():
    result = calculator.compute_totals(CONFIG, [{"name": "electricity", "previous": 100, "current": 110}])
    assert result["meters"] == [
        {"name": "electricity", "previous": 100, "current": 110, "usage": 10, "unit_price": 100, "amount": 1000}
    ]


def test_total_adds_fixed_fees_and_meter_amounts():
    result = calculator.compute_totals(CONFIG, [{"name": "electricity", "previous": 0, "current": 10}])
    assert result["total"] == 18750 + 11330 + 1000


def test_meter_amount_is_rounded_to_whole_won():
    result = calculator.compute_totals(CONFIG, [{"name": "water", "previous": 0, "current": 3}])
    assert result["meters"][0]["amount"] == 301  # 3 * 100.4 = 301.2


def test_no_readings_gives_the_fixed_fees_only():
    result = calculator.compute_totals(CONFIG, [])
    assert result["meters"] == []
    assert result["total"] == 18750 + 11330


def test_unknown_meter_is_rejected():
    with pytest.raises(ValueError, match="unknown meter"):
        calculator.compute_totals(CONFIG, [{"name": "gas", "previous": 0, "current": 1}])


def test_current_reading_below_previous_is_rejected():
    with pytest.raises(ValueError, match="lower than previous"):
        calculator.compute_totals(CONFIG, [{"name": "electricity", "previous": 10, "current": 5}])


def test_load_config_reads_json(tmp_path):
    path = tmp_path / "bill_config.json"
    path.write_text(json.dumps(CONFIG), encoding="utf-8")
    assert calculator.load_config(str(path)) == CONFIG
