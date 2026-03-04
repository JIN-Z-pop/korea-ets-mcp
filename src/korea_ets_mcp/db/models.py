"""SQLite schema definitions for Korea ETS (K-ETS) data."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS kets_daily_price (
    date TEXT NOT NULL,
    permit_type TEXT NOT NULL,
    closing_price INTEGER NOT NULL,
    fetched_at TEXT,
    PRIMARY KEY (date, permit_type)
);

CREATE TABLE IF NOT EXISTS kets_kau_ohlcv (
    date TEXT NOT NULL,
    kau_type TEXT NOT NULL,
    volume INTEGER,
    open_price INTEGER,
    high_price INTEGER,
    low_price INTEGER,
    close_price INTEGER,
    fetched_at TEXT,
    PRIMARY KEY (date, kau_type)
);

CREATE TABLE IF NOT EXISTS kets_monthly (
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    kau_exchange_vol INTEGER DEFAULT 0,
    kau_otc_vol INTEGER DEFAULT 0,
    kau_auction_vol INTEGER DEFAULT 0,
    kcu_exchange_vol INTEGER DEFAULT 0,
    kcu_otc_vol INTEGER DEFAULT 0,
    koc_exchange_vol INTEGER DEFAULT 0,
    koc_otc_vol INTEGER DEFAULT 0,
    kau_exchange_amt INTEGER DEFAULT 0,
    kau_otc_amt INTEGER DEFAULT 0,
    kau_auction_amt INTEGER DEFAULT 0,
    kcu_exchange_amt INTEGER DEFAULT 0,
    kcu_otc_amt INTEGER DEFAULT 0,
    koc_exchange_amt INTEGER DEFAULT 0,
    koc_otc_amt INTEGER DEFAULT 0,
    avg_price INTEGER DEFAULT 0,
    fetched_at TEXT,
    PRIMARY KEY (year, month)
);

CREATE TABLE IF NOT EXISTS kets_auction (
    auction_date TEXT NOT NULL,
    compliance_year TEXT NOT NULL,
    permit_type TEXT NOT NULL,
    bid_qty REAL,
    offer_qty REAL,
    offer_ratio REAL,
    bidder_count INTEGER,
    winner_count INTEGER,
    min_bid_price REAL,
    max_bid_price REAL,
    avg_award_price REAL,
    award_qty REAL,
    award_amount REAL,
    award_ratio REAL,
    fetched_at TEXT,
    PRIMARY KEY (auction_date, permit_type)
);

CREATE TABLE IF NOT EXISTS fetch_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market TEXT NOT NULL,
    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
    records_added INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    message TEXT
);
"""
