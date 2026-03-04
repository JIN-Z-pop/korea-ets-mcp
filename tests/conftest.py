"""Pytest configuration for Korea ETS MCP tests."""

import pytest
from pathlib import Path

from korea_ets_mcp.db.manager import DBManager


@pytest.fixture
def db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_korea_ets.db"
    manager = DBManager(db_path)
    manager.init_db()
    return manager


@pytest.fixture
def real_db():
    """Use the actual korea_ets.db for integration tests."""
    db_path = Path(__file__).parent.parent / "data" / "korea_ets.db"
    if not db_path.exists():
        pytest.skip("korea_ets.db not found")
    manager = DBManager(db_path)
    manager.init_db()
    return manager
