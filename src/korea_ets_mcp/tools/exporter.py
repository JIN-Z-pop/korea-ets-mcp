"""Data export to CSV and XLSX for Korea ETS."""

import csv
from pathlib import Path

from ..db.manager import DBManager

DAILY_FIELDS = ["date", "permit_type", "closing_price"]

OHLCV_FIELDS = [
    "date", "kau_type", "volume",
    "open_price", "high_price", "low_price", "close_price",
]

MONTHLY_FIELDS = [
    "year", "month",
    "kau_exchange_vol", "kau_otc_vol", "kau_auction_vol",
    "kcu_exchange_vol", "kcu_otc_vol",
    "koc_exchange_vol", "koc_otc_vol",
    "kau_exchange_amt", "kau_otc_amt", "kau_auction_amt",
    "kcu_exchange_amt", "kcu_otc_amt",
    "koc_exchange_amt", "koc_otc_amt",
    "avg_price",
]

AUCTION_FIELDS = [
    "auction_date", "compliance_year", "permit_type",
    "bid_qty", "offer_qty", "offer_ratio",
    "bidder_count", "winner_count",
    "min_bid_price", "max_bid_price", "avg_award_price",
    "award_qty", "award_amount", "award_ratio",
]

_MARKET_CONFIG = {
    "daily": {"fields": DAILY_FIELDS, "method": "get_all_daily_price"},
    "ohlcv": {"fields": OHLCV_FIELDS, "method": "get_all_ohlcv"},
    "monthly": {"fields": MONTHLY_FIELDS, "method": "query_monthly"},
    "auction": {"fields": AUCTION_FIELDS, "method": "query_auction"},
}


def _get_data(db: DBManager, market: str, start_date: str | None, end_date: str | None) -> tuple[list[dict], list[str]]:
    config = _MARKET_CONFIG.get(market)
    if not config:
        raise ValueError(f"Unknown market: {market}")

    if start_date or end_date:
        if market == "daily":
            data = db.query_daily_price(start_date or "2000-01-01", end_date or "2099-12-31")
        elif market == "ohlcv":
            data = db.query_ohlcv(start_date or "2000-01-01", end_date or "2099-12-31")
        elif market == "monthly":
            sy = int(start_date[:4]) if start_date else None
            ey = int(end_date[:4]) if end_date else None
            data = db.query_monthly(sy, ey)
        else:
            data = db.query_auction()
    else:
        data = getattr(db, config["method"])()

    return data, config["fields"]


def export_csv(
    db: DBManager, market: str, output_path: str,
    start_date: str | None = None, end_date: str | None = None,
):
    """Export data to CSV."""
    data, fields = _get_data(db, market, start_date, end_date)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def export_xlsx(
    db: DBManager, market: str, output_path: str,
    start_date: str | None = None, end_date: str | None = None,
):
    """Export data to XLSX."""
    from openpyxl import Workbook

    data, fields = _get_data(db, market, start_date, end_date)
    wb = Workbook()
    ws = wb.active
    ws.title = f"K-ETS {market.title()} Data"
    ws.append(fields)
    for row in data:
        ws.append([row.get(f) for f in fields])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
