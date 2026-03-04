"""Fetch K-ETS trading data from KRX ETS platform (ets.krx.co.kr).

Downloads daily price data using KRX's OTP-based API.
Data range: 2024-01 to present (to fill the gap after existing 2015-2023 data).
"""

import json
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

DB_PATH = Path(__file__).parent.parent / "data" / "korea_ets.db"

# KRX ETS API endpoints
BASE_URL = "https://ets.krx.co.kr"
PAGE_URL = f"{BASE_URL}/contents/ETS/03/03010000/ETS03010000.jsp"
OTP_URL = f"{BASE_URL}/contents/COM/GenerateOTP.jspx"
DATA_URL = f"{BASE_URL}/contents/ETS/99/ETS99000001.jspx"

BLD = "ETS/03/03010000/ets03010000_05"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": PAGE_URL,
}


def parse_int(s: str) -> int:
    """Parse Korean formatted number: '9,200' -> 9200, '-' -> 0."""
    if not s or s == "-" or s == "0":
        return 0
    return int(s.replace(",", ""))


def parse_float(s: str) -> float:
    """Parse float: '3.14' -> 3.14."""
    if not s or s == "-":
        return 0.0
    return float(s.replace(",", ""))


def fetch_month(session: requests.Session, year: int, month: int) -> list[dict]:
    """Fetch one month of data from KRX ETS."""
    from calendar import monthrange

    _, last_day = monthrange(year, month)
    from_date = f"{year}{month:02d}01"
    to_date = f"{year}{month:02d}{last_day:02d}"

    # Generate OTP
    otp_resp = session.post(OTP_URL, data={
        "name": "form",
        "bld": BLD,
    }, timeout=10)

    if otp_resp.status_code != 200:
        print(f"  OTP failed: {otp_resp.status_code}")
        return []

    # Fetch data with OTP
    data_resp = session.post(DATA_URL, data={
        "code": otp_resp.text,
        "isu_cd": "",
        "fromdate": from_date,
        "todate": to_date,
        "pagePath": "/contents/ETS/03/03010000/ETS03010000.jsp",
    }, timeout=30)

    if data_resp.status_code != 200 or not data_resp.text:
        print(f"  Data fetch failed: {data_resp.status_code}")
        return []

    try:
        result = json.loads(data_resp.text)
        items = result.get("DS1", [])
        return items
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return []


def insert_daily_price(conn: sqlite3.Connection, items: list[dict]) -> int:
    """Insert daily price records. Returns count of new records."""
    count = 0
    now = datetime.now().isoformat()

    for item in items:
        date = item.get("trd_dd", "")
        permit_type = item.get("isu_eng_abbrv", "")
        closing_price = parse_int(item.get("tdd_clsprc", "0"))

        if not date or not permit_type or closing_price == 0:
            continue

        # Format date: 2024-01-31
        if len(date) == 10:
            pass  # already formatted
        elif len(date) == 8:
            date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"

        try:
            conn.execute(
                "INSERT OR IGNORE INTO kets_daily_price (date, permit_type, closing_price, fetched_at) "
                "VALUES (?, ?, ?, ?)",
                (date, permit_type, closing_price, now),
            )
            if conn.total_changes:
                count += 1
        except sqlite3.IntegrityError:
            pass

    return count


def insert_ohlcv(conn: sqlite3.Connection, items: list[dict]) -> int:
    """Insert OHLCV records for KAU types. Returns count of new records."""
    count = 0
    now = datetime.now().isoformat()

    for item in items:
        date = item.get("trd_dd", "")
        kau_type = item.get("isu_eng_abbrv", "")
        if not kau_type.startswith("KAU"):
            continue

        open_p = parse_int(item.get("tdd_opnprc", "0"))
        high_p = parse_int(item.get("tdd_hgprc", "0"))
        low_p = parse_int(item.get("tdd_lwprc", "0"))
        close_p = parse_int(item.get("tdd_clsprc", "0"))
        volume = parse_int(item.get("acc_trdvol", "0"))

        if not date or close_p == 0:
            continue

        try:
            conn.execute(
                "INSERT OR IGNORE INTO kets_kau_ohlcv "
                "(date, kau_type, volume, open_price, high_price, low_price, close_price, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (date, kau_type, volume, open_p, high_p, low_p, close_p, now),
            )
            if conn.total_changes:
                count += 1
        except sqlite3.IntegrityError:
            pass

    return count


def main():
    print(f"=== K-ETS Data Fetcher (KRX ETS) ===")
    print(f"DB: {DB_PATH}")

    # Date range: 2024-01 to current month
    start_year, start_month = 2024, 1
    now = datetime.now()
    end_year, end_month = now.year, now.month

    # Setup session
    session = requests.Session()
    session.headers.update(HEADERS)

    # Visit page first to get session cookie
    session.get(PAGE_URL, timeout=10)
    print(f"Session established. Cookies: {len(session.cookies)}")

    conn = sqlite3.connect(str(DB_PATH))

    # Check existing data
    existing = conn.execute("SELECT MAX(date) FROM kets_daily_price").fetchone()[0]
    print(f"Existing data up to: {existing}")

    total_daily = 0
    total_ohlcv = 0

    y, m = start_year, start_month
    while (y, m) <= (end_year, end_month):
        print(f"\nFetching {y}-{m:02d}...", end=" ", flush=True)

        items = fetch_month(session, y, m)
        print(f"{len(items)} records", end="")

        if items:
            before_daily = conn.execute("SELECT COUNT(*) FROM kets_daily_price").fetchone()[0]
            before_ohlcv = conn.execute("SELECT COUNT(*) FROM kets_kau_ohlcv").fetchone()[0]

            insert_daily_price(conn, items)
            insert_ohlcv(conn, items)
            conn.commit()

            after_daily = conn.execute("SELECT COUNT(*) FROM kets_daily_price").fetchone()[0]
            after_ohlcv = conn.execute("SELECT COUNT(*) FROM kets_kau_ohlcv").fetchone()[0]

            new_daily = after_daily - before_daily
            new_ohlcv = after_ohlcv - before_ohlcv
            total_daily += new_daily
            total_ohlcv += new_ohlcv
            print(f" -> +{new_daily} daily, +{new_ohlcv} ohlcv")
        else:
            print(" -> no data")

        # Rate limiting
        time.sleep(0.5)

        # Next month
        m += 1
        if m > 12:
            m = 1
            y += 1

    conn.close()

    print(f"\n=== DONE ===")
    print(f"New daily_price records: {total_daily}")
    print(f"New kau_ohlcv records: {total_ohlcv}")

    # Verify
    conn = sqlite3.connect(str(DB_PATH))
    for table in ["kets_daily_price", "kets_kau_ohlcv", "kets_monthly", "kets_auction"]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {cnt} total records")

    max_date = conn.execute("SELECT MAX(date) FROM kets_daily_price").fetchone()[0]
    print(f"Latest date: {max_date}")
    conn.close()


if __name__ == "__main__":
    main()
