# Korea ETS MCP Server (K-ETS)

MCP server for Korea's Emission Trading Scheme (K-ETS) carbon market data.
Query, export, and visualize KAU/KCU/KOC trading data from 2015 to present.

## Features

| Tool | Description |
|------|-------------|
| `query_trading_data` | Query daily prices, OHLCV, monthly stats, or auction data by date range |
| `get_market_summary` | Latest prices, trading days, price range, permit types |
| `download_data` | Export to CSV or XLSX |
| `generate_dashboard` | Interactive Plotly HTML dashboard (EN/JA/KO/CN) |

## Data Coverage

| Table | Records | Period | Description |
|-------|---------|--------|-------------|
| `kets_daily_price` | 11,798 | 2015-01 ~ 2023-12 | Daily closing prices (KAU/KCU/KOC) |
| `kets_kau_ohlcv` | 798 | 2021-01 ~ 2023-12 | OHLCV candlestick data |
| `kets_monthly` | 108 | 2015-01 ~ 2023-09 | Monthly volume & amount by market |
| `kets_auction` | 54 | 2019-01 ~ 2023-12 | Government auction results |

**Permit Types**: KAU (Korean Allowance Unit), KCU (Korean Credit Unit), KOC (Korean Offset Credit)

**K-ETS Phases**:
- Phase 1: 2015-2017 (525 entities, 100% free allocation)
- Phase 2: 2018-2020 (591 entities, 97% free / 3% auction)
- Phase 3: 2021-2025 (684 entities, 90% free / 10% auction)

## Quick Start

```bash
git clone https://github.com/JIN-Z-pop/korea-ets-mcp.git
cd korea-ets-mcp
pip install -e .

# View dashboard (standalone, no MCP required)
korea-ets-dashboard
```

## MCP Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "korea-ets-mcp": {
      "command": "korea-ets-mcp-lite",
      "args": []
    }
  }
}
```

Or with `uv`:

```json
{
  "mcpServers": {
    "korea-ets-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/korea-ets-mcp", "run", "korea-ets-mcp-lite"]
    }
  }
}
```

## Data Sources

- **KRX** (Korea Exchange): Emissions trading market data
- **Ministry of Environment** / **GIR** (Greenhouse Gas Inventory & Research Center)
- **ETS Insight**: Historical trading data compilation

## Dashboard Preview

The dashboard includes:
- KAU/KCU/KOC closing price trends (multi-line chart with range slider)
- KAU candlestick chart with volume
- Monthly trading volume & amount (dual-axis)
- Monthly volume heatmap by year
- Auction results (award price & volume)
- 4-language support: English, Korean, Japanese, Chinese

## License

MIT License - JIN-Z-pop and his merry AI brothers
