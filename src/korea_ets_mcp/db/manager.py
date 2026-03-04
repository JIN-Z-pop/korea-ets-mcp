"""Database manager for Korea ETS (K-ETS) data."""

import sqlite3
from datetime import datetime
from pathlib import Path

from .models import SCHEMA_SQL


class DBManager:
    def __init__(self, db_path: str | Path = "data/korea_ets.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def close(self):
        """Ensure no lingering connections (for Windows file cleanup)."""
        pass

    def init_db(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    # === Query: Daily Price ===

    def query_daily_price(
        self, start_date: str, end_date: str, permit_type: str | None = None
    ) -> list[dict]:
        with self._connect() as conn:
            if permit_type:
                rows = conn.execute(
                    "SELECT * FROM kets_daily_price "
                    "WHERE date BETWEEN ? AND ? AND permit_type = ? ORDER BY date",
                    (start_date, end_date, permit_type),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM kets_daily_price "
                    "WHERE date BETWEEN ? AND ? ORDER BY date, permit_type",
                    (start_date, end_date),
                ).fetchall()
            return [dict(r) for r in rows]

    def get_all_daily_price(self, permit_type: str | None = None) -> list[dict]:
        with self._connect() as conn:
            if permit_type:
                rows = conn.execute(
                    "SELECT * FROM kets_daily_price WHERE permit_type = ? ORDER BY date",
                    (permit_type,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM kets_daily_price ORDER BY date, permit_type"
                ).fetchall()
            return [dict(r) for r in rows]

    # === Query: KAU OHLCV ===

    def query_ohlcv(
        self, start_date: str, end_date: str, kau_type: str | None = None
    ) -> list[dict]:
        with self._connect() as conn:
            if kau_type:
                rows = conn.execute(
                    "SELECT * FROM kets_kau_ohlcv "
                    "WHERE date BETWEEN ? AND ? AND kau_type = ? ORDER BY date",
                    (start_date, end_date, kau_type),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM kets_kau_ohlcv "
                    "WHERE date BETWEEN ? AND ? ORDER BY date, kau_type",
                    (start_date, end_date),
                ).fetchall()
            return [dict(r) for r in rows]

    def get_all_ohlcv(self, kau_type: str | None = None) -> list[dict]:
        with self._connect() as conn:
            if kau_type:
                rows = conn.execute(
                    "SELECT * FROM kets_kau_ohlcv WHERE kau_type = ? ORDER BY date",
                    (kau_type,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM kets_kau_ohlcv ORDER BY date, kau_type"
                ).fetchall()
            return [dict(r) for r in rows]

    # === Query: Monthly ===

    def query_monthly(
        self, start_year: int | None = None, end_year: int | None = None
    ) -> list[dict]:
        with self._connect() as conn:
            if start_year and end_year:
                rows = conn.execute(
                    "SELECT * FROM kets_monthly WHERE year BETWEEN ? AND ? ORDER BY year, month",
                    (start_year, end_year),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM kets_monthly ORDER BY year, month"
                ).fetchall()
            return [dict(r) for r in rows]

    # === Query: Auction ===

    def query_auction(self, permit_type: str | None = None) -> list[dict]:
        with self._connect() as conn:
            if permit_type:
                rows = conn.execute(
                    "SELECT * FROM kets_auction WHERE permit_type LIKE ? ORDER BY auction_date",
                    (f"%{permit_type}%",),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM kets_auction ORDER BY auction_date"
                ).fetchall()
            return [dict(r) for r in rows]

    # === Summary ===

    def get_market_summary(self) -> dict:
        """Get comprehensive K-ETS market summary."""
        with self._connect() as conn:
            # Daily price summary (KAU types only for main price)
            price_row = conn.execute("""
                SELECT
                    COUNT(DISTINCT date) as total_trading_days,
                    MIN(date) as first_date,
                    MAX(date) as last_date,
                    MIN(closing_price) as min_price,
                    MAX(closing_price) as max_price,
                    ROUND(AVG(closing_price)) as avg_price
                FROM kets_daily_price
                WHERE permit_type LIKE 'KAU%' AND closing_price > 0
            """).fetchone()

            # Latest prices per permit type
            latest_prices = conn.execute("""
                SELECT permit_type, closing_price, date
                FROM kets_daily_price dp
                WHERE date = (SELECT MAX(date) FROM kets_daily_price)
                ORDER BY permit_type
            """).fetchall()

            # Permit types
            types_row = conn.execute(
                "SELECT DISTINCT permit_type FROM kets_daily_price ORDER BY permit_type"
            ).fetchall()

            # OHLCV summary
            ohlcv_row = conn.execute("""
                SELECT COUNT(*) as ohlcv_records,
                       MIN(date) as ohlcv_first, MAX(date) as ohlcv_last
                FROM kets_kau_ohlcv
            """).fetchone()

            # Monthly summary
            monthly_row = conn.execute("""
                SELECT COUNT(*) as monthly_records,
                       MIN(year) as first_year, MAX(year) as last_year
                FROM kets_monthly
            """).fetchone()

            # Auction summary
            auction_row = conn.execute("""
                SELECT COUNT(*) as auction_count,
                       MIN(auction_date) as first_auction,
                       MAX(auction_date) as last_auction
                FROM kets_auction
            """).fetchone()

            return {
                "daily_price": dict(price_row) if price_row else {},
                "latest_prices": [dict(r) for r in latest_prices],
                "permit_types": [r["permit_type"] for r in types_row],
                "ohlcv": dict(ohlcv_row) if ohlcv_row else {},
                "monthly": dict(monthly_row) if monthly_row else {},
                "auction": dict(auction_row) if auction_row else {},
            }

    def get_latest_date(self) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT MAX(date) as max_date FROM kets_daily_price"
            ).fetchone()
            return row["max_date"] if row else None

    # === Logging ===

    def log_fetch(self, market: str, records_added: int, status: str, message: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO fetch_log (market, fetched_at, records_added, status, message) "
                "VALUES (?, ?, ?, ?, ?)",
                (market, datetime.now().isoformat(), records_added, status, message),
            )

    def get_fetch_logs(self, limit: int = 10) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM fetch_log ORDER BY fetched_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
