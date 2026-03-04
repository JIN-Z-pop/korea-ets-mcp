"""Query engine for Korea ETS data."""

from ..db.manager import DBManager


def query_trading_data(
    db: DBManager,
    market: str,
    start_date: str,
    end_date: str,
    permit_type: str | None = None,
) -> list[dict]:
    """Query trading data for a date range.

    market: 'daily', 'ohlcv', or 'monthly'
    """
    if market == "daily":
        return db.query_daily_price(start_date, end_date, permit_type)
    elif market == "ohlcv":
        return db.query_ohlcv(start_date, end_date, permit_type)
    elif market == "monthly":
        sy = int(start_date[:4]) if start_date else None
        ey = int(end_date[:4]) if end_date else None
        return db.query_monthly(sy, ey)
    elif market == "auction":
        return db.query_auction(permit_type)
    else:
        raise ValueError(f"Unknown market: {market}. Use 'daily', 'ohlcv', 'monthly', or 'auction'.")


def get_market_summary(db: DBManager) -> dict:
    """Get comprehensive K-ETS market summary."""
    return db.get_market_summary()
