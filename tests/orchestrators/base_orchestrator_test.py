"""
Base Test Class for Orchestrator Golden Tests

Provides common fixtures and assertions for orchestrator testing.
Zero mocks - all tests use real components (EventBus, Registry, SQLite).

Authority: AC-GOLDEN-FRAMEWORK-001
"""
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import pytest


class BaseOrchestratorTest:
    """Base class for all orchestrator tests - provides real component fixtures."""
    
    @pytest.fixture
    def real_event_bus(self):
        """
        Real EventBus instance (no mocks).
        
        Returns:
            EventBus: Live event bus for testing
            
        Note: EventBus located at cortex.core.event_bus (not cortex.common.event_bus)
        """
        from cortex.core.event_bus import EventBus
        return EventBus()
    
    @pytest.fixture
    def audit_db(self, tmp_path: Path) -> Path:
        """
        Real SQLite audit database with schema.
        
        Args:
            tmp_path: pytest temporary directory
            
        Returns:
            Path: Database file path
        """
        db_path = tmp_path / "audit.db"
        conn = sqlite3.connect(db_path)
        
        # Create audit_log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ac_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        return db_path
    
    @pytest.fixture
    def real_registry(self):
        """
        Real GitBackedRegistry instance (loads from cortex-registry/).
        
        Returns:
            GitBackedRegistry: Live registry for testing
        """
        from cortex.registry.git_backed_registry import GitBackedRegistry
        return GitBackedRegistry()
    
    def assert_audit_trail(self, db_path: Path, expected_ac_id: str) -> None:
        """
        Verify audit trail entry exists.
        
        Args:
            db_path: Path to audit database
            expected_ac_id: Expected AC marker ID
            
        Raises:
            AssertionError: If audit entry not found
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT ac_id FROM audit_log WHERE ac_id = ?",
            (expected_ac_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, f"Audit trail missing for {expected_ac_id}"
    
    def assert_no_mocks_used(self, test_instance: Any) -> None:
        """
        Verify test uses zero mocks (golden test requirement).
        
        Args:
            test_instance: Test instance to inspect
            
        Raises:
            AssertionError: If Mock objects detected
        """
        from unittest.mock import Mock, MagicMock
        
        for attr_name in dir(test_instance):
            attr = getattr(test_instance, attr_name)
            if isinstance(attr, (Mock, MagicMock)):
                raise AssertionError(
                    f"Mock detected: {attr_name}. Golden tests require real components."
                )
    
    def create_test_context(self, **overrides) -> Dict[str, Any]:
        """
        Create test orchestration context.
        
        Args:
            **overrides: Context field overrides
            
        Returns:
            Dict: Context dictionary
        """
        default_context = {
            "source": "test",
            "intent": "IMPLEMENT",
            "user_request": "test request",
            "session_id": "test-session-001"
        }
        default_context.update(overrides)
        return default_context
