"""Tests for MCP server lite tools."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def server_module():
    """Import server module with real DB path."""
    db_path = Path(__file__).parent.parent / "data" / "korea_ets.db"
    if not db_path.exists():
        pytest.skip("korea_ets.db not found")

    import korea_ets_mcp.server_lite as srv
    srv._DB_PATH = db_path
    return srv


def test_query_trading_data(server_module):
    result = json.loads(server_module.query_trading_data("daily", "2023-01-01", "2023-12-31"))
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_market_summary(server_module):
    result = json.loads(server_module.get_market_summary())
    assert "daily_price" in result
    assert "latest_prices" in result


def test_download_csv(server_module, tmp_path):
    server_module._BASE_DIR = tmp_path
    (tmp_path / "data" / "korea_ets.db").parent.mkdir(parents=True, exist_ok=True)
    import shutil
    src_db = Path(__file__).parent.parent / "data" / "korea_ets.db"
    shutil.copy2(src_db, tmp_path / "data" / "korea_ets.db")
    server_module._DB_PATH = tmp_path / "data" / "korea_ets.db"

    result = json.loads(server_module.download_data("daily", "csv"))
    assert result["format"] == "csv"
    assert Path(result["path"]).exists()


def test_generate_dashboard(server_module, tmp_path):
    # Reset _BASE_DIR to project root so path validation passes for default path
    server_module._BASE_DIR = Path(__file__).parent.parent
    server_module._DB_PATH = Path(__file__).parent.parent / "data" / "korea_ets.db"
    out = str(Path(__file__).parent.parent / "data" / "dashboard.html")
    result = json.loads(server_module.generate_dashboard(out))
    assert result["status"] == "generated"
    assert Path(result["path"]).exists()
    content = Path(result["path"]).read_text(encoding="utf-8")
    assert "K-ETS" in content
