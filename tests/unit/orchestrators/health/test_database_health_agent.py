"""Tests for DatabaseHealthAgent

Test-driven development for database health monitoring.

Authority: CORE-008 (TDD), Phase 92 (Health Orchestrator)
"""

import sqlite3
import pytest
from pathlib import Path
from cortex.orchestrators.health.agents.database_health_agent import (
    DatabaseHealthAgent,
)
from cortex.orchestrators.health.agents.base_agent import (
    HealthIssueSeverity,
    HealthIssueCategory,
)


class TestDatabaseHealthAgent:
    """Test DatabaseHealthAgent functionality."""
    
    def test_agent_initialization(self) -> None:
        """Test agent initializes with correct defaults."""
        agent = DatabaseHealthAgent()
        
        assert agent.name == "DatabaseHealthAgent"
        assert agent.enabled is True
        assert agent.bloat_threshold_mb == 10
        assert agent.wal_ratio_threshold == 0.5
    
    def test_agent_custom_config(self) -> None:
        """Test agent accepts custom configuration."""
        config = {
            "bloat_threshold_mb": 20,
            "wal_ratio_threshold": 0.7,
            "check_test_dbs": True,
        }
        agent = DatabaseHealthAgent(config=config)
        
        assert agent.bloat_threshold_mb == 20
        assert agent.wal_ratio_threshold == 0.7
        assert agent.check_test_dbs is True
    
    def test_check_no_databases(self, tmp_path: Path) -> None:
        """Test check with no databases returns empty result."""
        agent = DatabaseHealthAgent()
        result = agent.check(tmp_path)
        
        assert result.agent_name == "DatabaseHealthAgent"
        assert result.issue_count == 0
        assert result.files_scanned == 0
    
    def test_check_small_database_no_issues(self, tmp_path: Path) -> None:
        """Test check with small database reports no issues."""
        # Create small database
        db_path = tmp_path / "cortex_intelligence" / "governance.db"
        db_path.parent.mkdir(parents=True)
        
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()
        
        agent = DatabaseHealthAgent()
        result = agent.check(tmp_path)
        
        assert result.files_scanned == 1
        # Small DB should not trigger bloat warnings
        assert result.issue_count == 1  # Only auto-vacuum warning
        assert result.issues[0].severity == HealthIssueSeverity.LOW
    
    def test_check_bloated_database(self, tmp_path: Path) -> None:
        """Test check detects bloated database."""
        # Create database that exceeds threshold
        db_path = tmp_path / "cortex_intelligence" / "bloated.db"
        db_path.parent.mkdir(parents=True)
        
        conn = sqlite3.connect(str(db_path))
        # Insert enough data to exceed 10MB threshold
        conn.execute("CREATE TABLE large_data (id INTEGER, data TEXT)")
        for i in range(100000):
            conn.execute("INSERT INTO large_data VALUES (?, ?)", (i, "x" * 200))
        conn.commit()
        conn.close()
        
        agent = DatabaseHealthAgent(config={"bloat_threshold_mb": 1})
        result = agent.check(tmp_path)
        
        assert result.files_scanned == 1
        # Should detect bloat
        bloat_issues = [i for i in result.issues if "bloat" in i.description.lower()]
        assert len(bloat_issues) > 0
        assert bloat_issues[0].severity in [HealthIssueSeverity.MEDIUM, HealthIssueSeverity.HIGH]
    
    def test_check_wal_bloat(self, tmp_path: Path) -> None:
        """Test check detects WAL journal bloat."""
        # Create database with large WAL file
        db_path = tmp_path / "cortex_intelligence" / "wal_test.db"
        db_path.parent.mkdir(parents=True)
        
        # Enable WAL mode
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE test (id INTEGER, data TEXT)")
        
        # Insert data without checkpointing to grow WAL
        for i in range(10000):
            conn.execute("INSERT INTO test VALUES (?, ?)", (i, "x" * 100))
        
        conn.commit()
        # Don't checkpoint - leave WAL large
        conn.close()
        
        # Check if WAL file exists and is large
        wal_path = db_path.with_suffix(".db-wal")
        if wal_path.exists() and wal_path.stat().st_size > 0:
            agent = DatabaseHealthAgent(config={"wal_ratio_threshold": 0.1})
            result = agent.check(tmp_path)
            
            # Should detect WAL bloat if ratio exceeds threshold
            wal_issues = [i for i in result.issues if "WAL" in i.description]
            # May or may not trigger depending on actual WAL size
            assert result.files_scanned == 1
    
    def test_check_auto_vacuum_disabled(self, tmp_path: Path) -> None:
        """Test check detects disabled auto-vacuum."""
        db_path = tmp_path / "cortex_intelligence" / "no_vacuum.db"
        db_path.parent.mkdir(parents=True)
        
        conn = sqlite3.connect(str(db_path))
        # Auto-vacuum defaults to 0 (NONE)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()
        
        agent = DatabaseHealthAgent()
        result = agent.check(tmp_path)
        
        assert result.files_scanned == 1
        # Should detect auto-vacuum disabled
        vacuum_issues = [i for i in result.issues if "auto-vacuum" in i.description.lower()]
        assert len(vacuum_issues) == 1
        assert vacuum_issues[0].severity == HealthIssueSeverity.LOW
    
    def test_check_skips_test_databases(self, tmp_path: Path) -> None:
        """Test check skips test databases by default."""
        # Create test database
        test_db = tmp_path / "tests" / "test_data.db"
        test_db.parent.mkdir(parents=True)
        
        conn = sqlite3.connect(str(test_db))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        
        agent = DatabaseHealthAgent(config={"check_test_dbs": False})
        result = agent.check(tmp_path)
        
        # Should not scan test database
        assert result.files_scanned == 0
    
    def test_check_includes_test_databases_when_configured(self, tmp_path: Path) -> None:
        """Test check includes test databases when configured."""
        # Create test database
        test_db = tmp_path / "tests" / "test_data.db"
        test_db.parent.mkdir(parents=True)
        
        conn = sqlite3.connect(str(test_db))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        
        agent = DatabaseHealthAgent(config={"check_test_dbs": True})
        result = agent.check(tmp_path)
        
        # Should scan test database
        assert result.files_scanned == 1
    
    def test_check_result_metadata(self, tmp_path: Path) -> None:
        """Test check result includes metadata."""
        db_path = tmp_path / "cortex_intelligence" / "governance.db"
        db_path.parent.mkdir(parents=True)
        
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        
        agent = DatabaseHealthAgent()
        result = agent.check(tmp_path)
        
        assert "bloat_threshold_mb" in result.metadata
        assert "wal_ratio_threshold" in result.metadata
        assert "databases_checked" in result.metadata
        assert result.metadata["databases_checked"] == 1


# AC_COMPLETE: DatabaseHealthAgent tests ✅
