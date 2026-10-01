import json

from . import config


def load_config(path: str = config.CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_totals(bill_config: dict, readings: list[dict]) -> dict:
    """Builds the bill figures from the fixed fees and the meter readings.

    Each reading is `{"name", "previous", "current"}`. A meter's amount is
    its usage (current - previous) times the unit price in the config.
    """
    unit_prices = {m["name"]: m["unit_price"] for m in bill_config["meters"]}

    meters = []
    for reading in readings:
        name = reading["name"]
        if name not in unit_prices:
            raise ValueError(f"unknown meter: {name}")
        usage = reading["current"] - reading["previous"]
        if usage < 0:
            raise ValueError(f"current reading is lower than previous: {name}")
        meters.append({
            "name": name,
            "previous": reading["previous"],
            "current": reading["current"],
            "usage": usage,
            "unit_price": unit_prices[name],
            "amount": round(usage * unit_prices[name]),
        })

    fees = [{"name": f["name"], "amount": f["amount"]} for f in bill_config["fees"]]
    total = sum(f["amount"] for f in fees) + sum(m["amount"] for m in meters)
    return {"fees": fees, "meters": meters, "total": total}
