"""Korea ETS MCP Server (Lite) — Dashboard & Data Query Tools.

Public-facing server with 4 read-only tools for querying and visualizing
Korea's Emission Trading Scheme (K-ETS) data: KAU, KCU, KOC.
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .db.manager import DBManager
from .tools.query import query_trading_data as _query, get_market_summary as _summary
from .tools.exporter import export_csv, export_xlsx
from .tools.dashboard import generate_dashboard as _gen_dashboard

mcp = FastMCP("korea-ets-mcp")

_BASE_DIR = Path(__file__).parent.parent.parent
_DB_PATH = _BASE_DIR / "data" / "korea_ets.db"
_VALID_MARKETS = ("daily", "ohlcv", "monthly", "auction")


def _get_db() -> DBManager:
    db = DBManager(_DB_PATH)
    db.init_db()
    return db


def _validate_market(market: str) -> None:
    if market not in _VALID_MARKETS:
        raise ValueError(f"market must be one of {_VALID_MARKETS}, got '{market}'")


def _validate_output_path(path: str) -> Path:
    resolved = Path(path).resolve()
    allowed = (_BASE_DIR / "data").resolve()
    if not resolved.is_relative_to(allowed):
        raise ValueError(f"Output path must be within {allowed}")
    return resolved


@mcp.tool()
def query_trading_data(
    market: str,
    start_date: str = "",
    end_date: str = "",
    permit_type: str = "",
) -> str:
    """Query K-ETS historical trading data.

    Args:
        market: 'daily' (closing prices), 'ohlcv' (candlestick), 'monthly' (summary), or 'auction'
        start_date: Start date (YYYY-MM-DD). For monthly, use year only (e.g., '2020').
        end_date: End date (YYYY-MM-DD). For monthly, use year only.
        permit_type: Filter by permit type (KAU, KCU, KOC, or specific like KAU23). Optional.
    """
    _validate_market(market)
    db = _get_db()
    data = _query(db, market, start_date or "2000-01-01", end_date or "2099-12-31",
                  permit_type or None)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
def get_market_summary() -> str:
    """Get K-ETS market summary: latest prices, trading days, price range, permit types, and data coverage."""
    db = _get_db()
    summary = _summary(db)
    return json.dumps(summary, ensure_ascii=False, default=str)


@mcp.tool()
def download_data(
    market: str = "daily",
    format: str = "csv",
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Export K-ETS trading data as CSV or XLSX file.

    Args:
        market: 'daily', 'ohlcv', 'monthly', or 'auction' (default: 'daily')
        format: 'csv' or 'xlsx' (default: 'csv')
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
    """
    _validate_market(market)
    db = _get_db()
    output_dir = _BASE_DIR / "data" / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    ext = "xlsx" if format == "xlsx" else "csv"
    filename = f"kets_{market}_data.{ext}"
    output_path = str(output_dir / filename)

    if format == "xlsx":
        export_xlsx(db, market, output_path, start_date, end_date)
    else:
        export_csv(db, market, output_path, start_date, end_date)

    return json.dumps({"path": output_path, "format": format, "market": market})


@mcp.tool()
def generate_dashboard(output_path: str | None = None) -> str:
    """Generate interactive Plotly HTML dashboard with all K-ETS market data.

    Includes: KAU/KCU/KOC price trends, OHLCV candlestick, monthly volume heatmap,
    auction results. Supports EN/JA/KO/CN languages.

    Args:
        output_path: Optional custom output path (default: data/dashboard.html)
    """
    db = _get_db()
    path = output_path or str(_BASE_DIR / "data" / "dashboard.html")
    _validate_output_path(path)
    result = _gen_dashboard(db, path)
    return json.dumps({"path": result, "status": "generated"})


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
