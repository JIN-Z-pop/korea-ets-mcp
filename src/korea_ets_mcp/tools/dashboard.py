"""Dashboard HTML generator using Jinja2 + Plotly for K-ETS."""

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..db.manager import DBManager


def _clean_records(records: list[dict], drop_keys: set[str] | None = None) -> list[dict]:
    """Remove unnecessary fields and replace None with 0."""
    drop = drop_keys or {"fetched_at"}
    cleaned = []
    for r in records:
        row = {k: (v if v is not None else 0) for k, v in r.items() if k not in drop}
        cleaned.append(row)
    return cleaned


def _clean_summary(summary: dict) -> dict:
    """Replace None values with sensible defaults for JSON serialization."""
    result = {}
    for k, v in summary.items():
        if isinstance(v, dict):
            result[k] = {k2: (v2 if v2 is not None else 0) for k2, v2 in v.items()}
        elif isinstance(v, list):
            result[k] = [
                {k2: (v2 if v2 is not None else 0) for k2, v2 in item.items()}
                if isinstance(item, dict) else item
                for item in v
            ]
        else:
            result[k] = v if v is not None else 0
    return result


def generate_dashboard(db: DBManager, output_path: str) -> str:
    """Generate interactive HTML dashboard for K-ETS."""
    daily_data = _clean_records(db.get_all_daily_price())
    ohlcv_data = _clean_records(db.get_all_ohlcv())
    monthly_data = _clean_records(db.query_monthly())
    auction_data = _clean_records(db.query_auction())
    summary = _clean_summary(db.get_market_summary())

    template_dir = Path(__file__).parent.parent.parent.parent / "dashboard"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("template.html")

    html = template.render(
        daily_data_json=json.dumps(daily_data, ensure_ascii=False),
        ohlcv_data_json=json.dumps(ohlcv_data, ensure_ascii=False),
        monthly_data_json=json.dumps(monthly_data, ensure_ascii=False),
        auction_data_json=json.dumps(auction_data, ensure_ascii=False),
        summary_json=json.dumps(summary, ensure_ascii=False, default=str),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
