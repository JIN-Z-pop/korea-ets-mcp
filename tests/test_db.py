"""Tests for database operations."""

import pytest


def test_init_db(db):
    """Test database initialization creates tables."""
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = {t[0] for t in tables}
    assert "kets_daily_price" in table_names
    assert "kets_kau_ohlcv" in table_names
    assert "kets_monthly" in table_names
    assert "kets_auction" in table_names
    assert "fetch_log" in table_names
    conn.close()


def test_query_daily_price(real_db):
    """Test daily price query returns data."""
    data = real_db.query_daily_price("2023-01-01", "2023-12-31")
    assert len(data) > 0
    assert "date" in data[0]
    assert "permit_type" in data[0]
    assert "closing_price" in data[0]


def test_query_daily_price_filtered(real_db):
    """Test daily price query with permit type filter."""
    data = real_db.query_daily_price("2023-01-01", "2023-12-31", "KAU23")
    assert len(data) > 0
    assert all(d["permit_type"] == "KAU23" for d in data)


def test_query_ohlcv(real_db):
    """Test OHLCV query returns data."""
    data = real_db.query_ohlcv("2023-01-01", "2023-12-31")
    assert len(data) > 0
    assert "open_price" in data[0]
    assert "close_price" in data[0]


def test_query_monthly(real_db):
    """Test monthly query returns data."""
    data = real_db.query_monthly(2023, 2023)
    assert len(data) > 0
    assert "kau_exchange_vol" in data[0]


def test_query_auction(real_db):
    """Test auction query returns data."""
    data = real_db.query_auction()
    assert len(data) > 0
    assert "avg_award_price" in data[0]


def test_market_summary(real_db):
    """Test market summary returns comprehensive data."""
    summary = real_db.get_market_summary()
    assert "daily_price" in summary
    assert "latest_prices" in summary
    assert "permit_types" in summary
    assert "ohlcv" in summary
    assert "monthly" in summary
    assert "auction" in summary
    assert summary["daily_price"]["total_trading_days"] > 0


def test_get_latest_date(real_db):
    """Test latest date retrieval."""
    date = real_db.get_latest_date()
    assert date is not None
    assert date.startswith("202")
