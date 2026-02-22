"""
Pytest configuration for orchestrators e2e tests.

Authority: AC-GOLDEN-E2E-CONFTEST
Provides fixtures for LENS golden tests and orchestrator e2e testing.
"""
import sqlite3
import pytest
from pathlib import Path
from typing import Generator

from tests.orchestrators.e2e.test_lens_golden_harness import (
    LENSGoldenTestHarness,
    TempRepoBuilder,
)
from tests.orchestrators.e2e.test_golden_harness import GoldenTestHarness


@pytest.fixture
def lens_harness(tmp_path: Path) -> Generator[LENSGoldenTestHarness, None, None]:
    """
    Create LENS golden test harness with temp database.
    
    Args:
        tmp_path: Pytest temp path
    
    Returns:
        LENSGoldenTestHarness instance
    """
    db_path = tmp_path / "audit.db"
    
    # Apply schema
    schema_path = Path(__file__).parent.parent.parent.parent / "cortex.intelligence" / "audit" / "schema.sql"
    
    if schema_path.exists():
        conn = sqlite3.connect(str(db_path))
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.close()
    else:
        # Create minimal schema if main schema not found
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                activity TEXT NOT NULL,
                details TEXT,
                status TEXT
            )
        """)
        conn.close()
    
    fixture_path = tmp_path / "fixtures"
    harness = LENSGoldenTestHarness(db_path=db_path, fixture_path=fixture_path)
    
    yield harness
    
    # Cleanup
    harness.cleanup()


@pytest.fixture
def temp_repo_builder(tmp_path: Path) -> Generator[TempRepoBuilder, None, None]:
    """
    Create temp repository builder.
    
    Args:
        tmp_path: Pytest temp path
    
    Returns:
        TempRepoBuilder instance
    """
    builder = TempRepoBuilder(tmp_path / "repos")
    
    yield builder
    
    # Cleanup
    builder.cleanup()


@pytest.fixture
def golden_harness(tmp_path: Path) -> Generator[GoldenTestHarness, None, None]:
    """
    Create golden test harness.
    
    Args:
        tmp_path: Pytest temp path
    
    Returns:
        GoldenTestHarness instance
    """
    db_path = tmp_path / "test_audit.db"
    harness = GoldenTestHarness(db_path=db_path)
    
    yield harness
    
    harness.cleanup()
