"""Tests for governance.db sanitization (PHASE-DEPLOYMENT-001 AC-DEP-001-01).

This module tests the sanitization of development entries from governance.db,
ensuring production deployments contain only tier0 seed rules.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_db(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary governance.db with test data.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary database.
    """
    db_path = tmp_path / "governance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create audit_log table
    cursor.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY,
            ac_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            source TEXT,
            is_production INTEGER DEFAULT 0
        )
    """)
    
    # Insert test data - mix of dev and production entries
    test_entries = [
        ("TEST-001", "2026-01-01T10:00:00Z", "VALIDATE", "dev", 0),
        ("DEV-002", "2026-01-01T11:00:00Z", "EXECUTE", "dev", 0),
        ("AC-PROD-001", "2026-01-15T10:00:00Z", "DEPLOY", "production", 1),
        ("TEST-CLEANUP-003", "2026-01-01T12:00:00Z", "CLEANUP", "dev", 0),
        ("AC-CORE-001", "2026-01-15T11:00:00Z", "ENFORCE", "production", 1),
        ("DEV-TEMP-004", "2026-01-01T13:00:00Z", "DEBUG", "dev", 0),
    ]
    
    cursor.executemany(
        "INSERT INTO audit_log (ac_id, timestamp, operation, source, is_production) VALUES (?, ?, ?, ?, ?)",
        test_entries
    )
    
    conn.commit()
    conn.close()
    
    yield db_path


@pytest.fixture
def sanitizer_module():
    """Import the sanitizer module.
    
    Returns:
        The sanitize_governance_db module.
    """
    from scripts.deployment import sanitize_governance_db
    return sanitize_governance_db


class TestSanitizeRemovesDevEntries:
    """Tests for AC-DEP-001-01: Audit log scrubbing removes dev-only entries."""
    
    def test_sanitize_removes_test_entries(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Sanitization removes entries with TEST prefix in AC-ID.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        result = sanitizer.sanitize()
        
        # Verify TEST entries removed
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id LIKE 'TEST%'")
        test_count = cursor.fetchone()[0]
        conn.close()
        
        assert test_count == 0, "TEST entries should be removed"
        assert result.removed_count > 0, "Should report removed entries"
    
    def test_sanitize_removes_dev_entries(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Sanitization removes entries with DEV prefix in AC-ID.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        sanitizer.sanitize()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id LIKE 'DEV%'")
        dev_count = cursor.fetchone()[0]
        conn.close()
        
        assert dev_count == 0, "DEV entries should be removed"
    
    def test_sanitize_identifies_dev_patterns(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Sanitizer correctly identifies all dev-only patterns.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        
        dev_patterns = sanitizer.get_dev_patterns()
        
        assert "TEST%" in dev_patterns
        assert "DEV%" in dev_patterns
        assert "DEBUG%" in dev_patterns or "DEV%" in dev_patterns


class TestSanitizePreservesProductionAudit:
    """Tests for preserving production audit trail during sanitization."""
    
    def test_sanitize_preserves_production_entries(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Production entries (is_production=1) are preserved.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        sanitizer.sanitize()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE is_production = 1")
        prod_count = cursor.fetchone()[0]
        conn.close()
        
        assert prod_count == 2, "Production entries should be preserved"
    
    def test_sanitize_preserves_ac_core_entries(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """AC-CORE entries (tier0 rules) are preserved regardless of source.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        sanitizer.sanitize()
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-CORE%'")
        core_count = cursor.fetchone()[0]
        conn.close()
        
        assert core_count >= 1, "AC-CORE entries should be preserved"


class TestSanitizeGeneratesReport:
    """Tests for sanitization report generation."""
    
    def test_sanitize_generates_report(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Sanitization generates a report of what was removed.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        result = sanitizer.sanitize()
        
        assert result.report is not None
        assert "removed" in result.report.lower() or result.removed_count >= 0
    
    def test_report_includes_retention_policy(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Report includes retention policy information.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        result = sanitizer.sanitize()
        
        assert hasattr(result, 'retention_policy') or 'policy' in result.report.lower()
    
    def test_report_lists_removed_entries(
        self, temp_db: Path, sanitizer_module
    ) -> None:
        """Report lists the AC-IDs that were removed.
        
        Args:
            temp_db: Path to temporary database.
            sanitizer_module: The sanitizer module.
        """
        sanitizer = sanitizer_module.GovernanceDBSanitizer(temp_db)
        result = sanitizer.sanitize()
        
        assert result.removed_ac_ids is not None
        assert len(result.removed_ac_ids) >= 3  # TEST-001, DEV-002, etc.
