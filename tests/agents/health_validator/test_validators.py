"""Tests for HealthValidator validators."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import os
import sqlite3
import tempfile

from src.cortex_agents.health_validator.validators import (
    DatabaseValidator,
    TestValidator,
    GitValidator,
    DiskValidator,
    PerformanceValidator
)


class TestDatabaseValidator:
    """Test DatabaseValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = DatabaseValidator()
        assert validator.max_size_mb == 500
        assert validator.get_risk_level() == "critical"
    
    def test_check_missing_database(self):
        """Test check with missing database."""
        validator = DatabaseValidator()
        result = validator._check_single_database("/nonexistent/db.sqlite", "Test")
        
        assert result["status"] == "fail"
        assert "not found" in result["error"]
        assert result["name"] == "Test"
    
    def test_check_healthy_database(self):
        """Test check with healthy database."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
            conn.close()
            
            validator = DatabaseValidator()
            result = validator._check_single_database(db_path, "Test")
            
            assert result["status"] == "pass"
            assert result["name"] == "Test"
            assert "size_mb" in result
        finally:
            os.unlink(db_path)
    
    def test_check_oversized_database(self):
        """Test check with oversized database."""
        validator = DatabaseValidator(max_size_mb=0.001)  # Very small threshold
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
            # Write some data to make it exceed threshold
            tmp.write(b"x" * 10000)
        
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
            conn.close()
            
            result = validator._check_single_database(db_path, "Test")
            
            assert result["status"] == "warn"
            assert "exceeds threshold" in result["error"]
        finally:
            os.unlink(db_path)
    
    def test_check_all_databases(self):
        """Test checking all tier databases."""
        mock_tier1 = Mock()
        mock_tier1.db_path = None  # No database
        
        validator = DatabaseValidator(mock_tier1)
        result = validator.check()
        
        assert "status" in result
        assert "details" in result
        assert isinstance(result["details"], list)


class TestTestValidator:
    """Test TestValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = TestValidator()
        assert validator.pass_rate_threshold == 0.85
        assert validator.get_risk_level() == "high"
    
    @patch('subprocess.run')
    def test_successful_test_run(self, mock_run):
        """Test successful test execution."""
        mock_result = Mock()
        mock_result.stdout = "10 passed in 1.5s"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        validator = TestValidator(pass_rate_threshold=0.8)
        result = validator.check()
        
        assert result["status"] == "pass"
        assert result["passed"] == 10
        assert result["pass_rate"] >= 0.8
    
    @patch('subprocess.run')
    def test_failed_tests(self, mock_run):
        """Test with failing tests."""
        mock_result = Mock()
        mock_result.stdout = "5 passed, 5 failed in 2.0s"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        validator = TestValidator(pass_rate_threshold=0.9)
        result = validator.check()
        
        assert result["status"] == "fail"
        assert result["passed"] == 5
        assert result["failed"] == 5
        assert result["pass_rate"] < 0.9


class TestGitValidator:
    """Test GitValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = GitValidator()
        assert validator.max_uncommitted == 50
        assert validator.get_risk_level() == "medium"
    
    @patch('subprocess.run')
    def test_not_git_repo(self, mock_run):
        """Test check when not in git repository."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        validator = GitValidator()
        result = validator.check()
        
        assert result["status"] == "skip"
        assert "Not a git repository" in result["message"]
    
    @patch('subprocess.run')
    def test_clean_git_status(self, mock_run):
        """Test check with clean git status."""
        # Mock git rev-parse (check if git repo)
        mock_rev_parse = Mock()
        mock_rev_parse.returncode = 0
        
        # Mock git status (no changes)
        mock_status = Mock()
        mock_status.stdout = ""
        
        mock_run.side_effect = [mock_rev_parse, mock_status]
        
        validator = GitValidator()
        result = validator.check()
        
        assert result["status"] == "pass"
        assert result["uncommitted_count"] == 0
    
    @patch('subprocess.run')
    def test_many_uncommitted_changes(self, mock_run):
        """Test check with many uncommitted changes."""
        mock_rev_parse = Mock()
        mock_rev_parse.returncode = 0
        
        mock_status = Mock()
        # Simulate 60 uncommitted files
        mock_status.stdout = "\n".join([f"M file{i}.txt" for i in range(60)])
        
        mock_run.side_effect = [mock_rev_parse, mock_status]
        
        validator = GitValidator(max_uncommitted=50)
        result = validator.check()
        
        assert result["status"] == "warn"
        assert result["uncommitted_count"] == 60


class TestDiskValidator:
    """Test DiskValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = DiskValidator()
        assert validator.min_free_gb == 1.0
        assert validator.get_risk_level() == "high"
    
    def test_check_disk_space(self):
        """Test disk space check."""
        validator = DiskValidator()
        result = validator.check()
        
        assert "status" in result
        assert "free_gb" in result
        assert "total_gb" in result
        assert "used_percent" in result
        assert result["free_gb"] >= 0
        assert result["total_gb"] > 0


class TestPerformanceValidator:
    """Test PerformanceValidator functionality."""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = PerformanceValidator()
        assert validator.min_velocity == 5.0
        assert validator.get_risk_level() == "medium"
    
    def test_no_tier3(self):
        """Test check when Tier 3 is not available."""
        validator = PerformanceValidator(tier3_context=None)
        result = validator.check()
        
        assert result["status"] == "skip"
        assert "not available" in result["message"]
    
    def test_good_performance(self):
        """Test check with good performance metrics."""
        mock_tier3 = Mock()
        mock_tier3.get_context_summary.return_value = {
            "average_velocity": 8.5
        }
        
        validator = PerformanceValidator(tier3_context=mock_tier3, min_velocity=5.0)
        result = validator.check()
        
        assert result["status"] == "pass"
        assert result["metrics"]["velocity"] == 8.5
    
    def test_low_performance(self):
        """Test check with low performance metrics."""
        mock_tier3 = Mock()
        mock_tier3.get_context_summary.return_value = {
            "average_velocity": 3.0
        }
        
        validator = PerformanceValidator(tier3_context=mock_tier3, min_velocity=5.0)
        result = validator.check()
        
        assert result["status"] == "warn"
        assert len(result["warnings"]) > 0
