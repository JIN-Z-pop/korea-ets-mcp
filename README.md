# Korea ETS MCP Server (K-ETS)

MCP server for Korea's Emission Trading Scheme (K-ETS) carbon market data.
Query, export, and visualize KAU/KCU/KOC trading data from 2015 to present.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-compatible-blue)

> **[Live Dashboard Demo](https://jin-z-pop.github.io/korea-ets-mcp/)** — Click to explore K-ETS data interactively. No installation required.

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
| `kets_daily_price` | 19,299 | 2015-01 ~ 2026-03 | Daily closing prices (KAU/KCU/KOC) |
| `kets_kau_ohlcv` | 2,097 | 2021-01 ~ 2026-03 | OHLCV candlestick data |
| `kets_monthly` | 108 | 2015-01 ~ 2023-09 | Monthly volume & amount by market |
| `kets_auction` | 54 | 2019-01 ~ 2023-12 | Government auction results |

**Permit Types**: KAU (Korean Allowance Unit), KCU (Korean Credit Unit), KOC (Korean Offset Credit)

**K-ETS Phases**:
- Phase 1: 2015-2017 (525 entities, 100% free allocation)
- Phase 2: 2018-2020 (591 entities, 97% free / 3% auction)
- Phase 3: 2021-2025 (684 entities, 90% free / 10% auction)

## Quick Start

**Recommended** (auto-manages Python version):
```bash
git clone https://github.com/JIN-Z-pop/korea-ets-mcp.git
cd korea-ets-mcp
uv run korea-ets-dashboard
```

Or with pip (requires Python 3.11+):
```bash
pip install -e .
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

## Disclaimer

This tool is provided for research and educational purposes only. The authors make no warranties regarding accuracy, completeness, or fitness for any particular purpose, and accept no liability for any loss or damage arising from its use. Use of this tool is entirely at your own risk.

본 도구는 연구·교육 목적으로 공개되었습니다. 정확성·완전성·특정 목적에 대한 적합성을 보증하지 않으며, 본 도구의 사용으로 인해 발생한 어떠한 손해에 대해서도 책임을 지지 않습니다. 이용은 전적으로 이용자 본인의 책임하에 이루어집니다.

## License

MIT License - JIN-Z-pop and his merry AI brothers
