"""
Tests for HealthValidator Agent

Tests system health validation functionality including database checks,
test suite validation, git status monitoring, and risk assessment.
"""

import os
import pytest
import sqlite3
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.cortex_agents.health_validator import HealthValidator
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class TestHealthValidatorBasics:
    """Test basic HealthValidator functionality."""
    
    def test_initialization(self):
        """Test agent initialization."""
        validator = HealthValidator(name="TestValidator")
        
        assert validator.name == "TestValidator"
        assert validator.THRESHOLDS["test_pass_rate"] == 0.95
        assert validator.THRESHOLDS["disk_space_gb"] == 1.0
        assert validator.RISK_LEVELS["databases"] == "critical"
    
    def test_can_handle_health_check(self):
        """Test can_handle for health_check intent."""
        validator = HealthValidator(name="TestValidator")
        
        request = AgentRequest(
            intent=IntentType.HEALTH_CHECK.value,
            context={},
            user_message="Check system health"
        )
        
        assert validator.can_handle(request) is True
    
    def test_can_handle_validate(self):
        """Test can_handle for validate intent."""
        validator = HealthValidator(name="TestValidator")
        
        request = AgentRequest(
            intent=IntentType.VALIDATE.value,
            context={},
            user_message="Validate system before deployment"
        )
        
        assert validator.can_handle(request) is True
    
    def test_can_handle_string_intents(self):
        """Test can_handle for string variants."""
        validator = HealthValidator(name="TestValidator")
        
        for intent in ["health", "check", "validate"]:
            request = AgentRequest(
                intent=intent,
                context={},
                user_message="Check"
            )
            assert validator.can_handle(request) is True
    
    def test_cannot_handle_other_intents(self):
        """Test can_handle rejects non-health intents."""
        validator = HealthValidator(name="TestValidator")
        
        request = AgentRequest(
            intent=IntentType.PLAN.value,
            context={},
            user_message="Plan a feature"
        )
        
        assert validator.can_handle(request) is False


class TestDatabaseChecks:
    """Test database health checking."""
    
    def test_check_databases_all_pass(self):
        """Test database checks when all databases are healthy."""
        # Create temporary test database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Initialize database with valid structure
            conn = sqlite3.connect(tmp_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            # Create mock tier APIs with db_path
            tier1 = Mock()
            tier1.db_path = tmp_path
            
            validator = HealthValidator(name="TestValidator", tier1_api=tier1)
            result = validator._check_databases()
            
            assert result["status"] == "pass"
            assert len(result["details"]) > 0
            assert result["details"][0]["status"] == "pass"
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_check_databases_missing_file(self):
        """Test database check when file doesn't exist."""
        tier1 = Mock()
        tier1.db_path = "/nonexistent/database.db"
        
        validator = HealthValidator(name="TestValidator", tier1_api=tier1)
        result = validator._check_databases()
        
        assert result["status"] == "fail"
        assert len(result["errors"]) > 0
        assert "not found" in result["errors"][0].lower()
    
    def test_check_databases_no_path(self):
        """Test database check when no path is configured."""
        tier1 = Mock()
        tier1.db_path = None  # Explicitly set to None
        
        validator = HealthValidator(name="TestValidator", tier1_api=tier1)
        result = validator._check_databases()
        
        # Should skip the check
        assert len(result["details"]) > 0
        assert result["details"][0]["status"] == "skip"
    
    def test_check_single_database_size_warning(self):
        """Test database size threshold warning."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create database
            conn = sqlite3.connect(tmp_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            validator = HealthValidator(name="TestValidator")
            
            # Mock the size check to return large size
            with patch('os.path.getsize', return_value=600 * 1024 * 1024):  # 600MB
                result = validator._check_single_database(tmp_path, "TestDB")
                
                assert result["status"] == "warn"
                assert "exceeds threshold" in result["error"]
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestHealthChecks:
    """Test various health check methods."""
    
    def test_check_tests_skip(self):
        """Test test check when skipped."""
        validator = HealthValidator(name="TestValidator")
        result = validator._check_tests(skip=True)
        
        assert result["status"] == "skip"
        assert "skipped" in result["message"].lower()
    
    @patch('subprocess.run')
    def test_check_tests_all_pass(self, mock_run):
        """Test test check when all tests pass."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="50 passed in 1.23s",
            stderr=""
        )
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_tests(skip=False)
        
        assert result["status"] == "pass"
        assert result["passed"] == 50
        assert result["failed"] == 0
        assert result["pass_rate"] >= 0.95
    
    @patch('subprocess.run')
    def test_check_tests_some_failures(self, mock_run):
        """Test test check with some failures."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="40 passed, 10 failed in 2.34s",
            stderr=""
        )
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_tests(skip=False)
        
        assert result["status"] == "fail"
        assert result["passed"] == 40
        assert result["failed"] == 10
        assert result["pass_rate"] < 0.95
    
    @patch('subprocess.run')
    def test_check_git_status_clean(self, mock_run):
        """Test git check with clean repository."""
        # First call: check if git repo
        # Second call: get status
        mock_run.side_effect = [
            Mock(returncode=0, stdout=".git", stderr=""),
            Mock(returncode=0, stdout="", stderr="")
        ]
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_git_status()
        
        assert result["status"] == "pass"
        assert result["uncommitted_count"] == 0
        assert "no uncommitted" in result["message"].lower()
    
    @patch('subprocess.run')
    def test_check_git_status_with_changes(self, mock_run):
        """Test git check with uncommitted changes."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout=".git", stderr=""),
            Mock(returncode=0, stdout="M file1.py\nM file2.py\n", stderr="")
        ]
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_git_status()
        
        assert result["status"] == "pass"
        assert result["uncommitted_count"] == 2
        assert "acceptable" in result["message"].lower()
    
    @patch('subprocess.run')
    def test_check_git_status_many_changes(self, mock_run):
        """Test git check with many uncommitted changes."""
        # Create 60 lines of changes
        changes = "\n".join([f"M file{i}.py" for i in range(60)])
        
        mock_run.side_effect = [
            Mock(returncode=0, stdout=".git", stderr=""),
            Mock(returncode=0, stdout=changes, stderr="")
        ]
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_git_status()
        
        assert result["status"] == "warn"
        assert result["uncommitted_count"] == 60
        assert "high" in result["message"].lower()
    
    @patch('os.statvfs')
    def test_check_disk_space_sufficient(self, mock_statvfs):
        """Test disk space check with sufficient space."""
        # Mock disk stats: 100GB free
        mock_stat = Mock()
        mock_stat.f_bavail = 100 * (1024 ** 3) // 4096  # blocks
        mock_stat.f_frsize = 4096  # block size
        mock_stat.f_blocks = 500 * (1024 ** 3) // 4096  # total blocks
        mock_statvfs.return_value = mock_stat
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_disk_space()
        
        assert result["status"] == "pass"
        assert result["free_gb"] > 1.0
    
    @patch('os.statvfs')
    def test_check_disk_space_low(self, mock_statvfs):
        """Test disk space check with low space."""
        # Mock disk stats: 0.5GB free
        mock_stat = Mock()
        mock_stat.f_bavail = int(0.5 * (1024 ** 3) / 4096)  # blocks
        mock_stat.f_frsize = 4096  # block size
        mock_stat.f_blocks = 100 * (1024 ** 3) // 4096  # total blocks
        mock_statvfs.return_value = mock_stat
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_disk_space()
        
        assert result["status"] == "fail"
        assert result["free_gb"] < 1.0
    
    def test_check_performance_no_tier3(self):
        """Test performance check without Tier 3."""
        validator = HealthValidator(name="TestValidator")
        result = validator._check_performance()
        
        assert result["status"] == "skip"
    
    def test_check_performance_with_tier3(self):
        """Test performance check with Tier 3 data."""
        tier3 = Mock()
        tier3.get_context_summary.return_value = {
            "average_velocity": 15.0,
            "total_commits": 100
        }
        
        validator = HealthValidator(name="TestValidator", tier3_context=tier3)
        result = validator._check_performance()
        
        assert result["status"] == "pass"
        assert "velocity" in result["metrics"]


class TestHealthAnalysis:
    """Test health check analysis and risk assessment."""
    
    def test_analyze_results_all_pass(self):
        """Test analysis when all checks pass."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"},
            "git": {"status": "pass"}
        }
        
        status, warnings, errors = validator._analyze_results(check_results)
        
        assert status == "healthy"
        assert len(warnings) == 0
        assert len(errors) == 0
    
    def test_analyze_results_with_warnings(self):
        """Test analysis with warnings."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"},
            "git": {"status": "warn", "message": "Many uncommitted changes"}
        }
        
        status, warnings, errors = validator._analyze_results(check_results)
        
        assert status == "degraded"
        assert len(warnings) == 1
        assert "git" in warnings[0].lower()
        assert len(errors) == 0
    
    def test_analyze_results_with_errors(self):
        """Test analysis with errors."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "databases": {"status": "fail", "error": "Database not found"},
            "tests": {"status": "pass"},
            "git": {"status": "pass"}
        }
        
        status, warnings, errors = validator._analyze_results(check_results)
        
        assert status == "unhealthy"
        assert len(errors) == 1
        assert "database" in errors[0].lower()
    
    def test_calculate_risk_low(self):
        """Test risk calculation with no errors."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"}
        }
        errors = []
        
        risk = validator._calculate_risk(check_results, errors)
        assert risk == "low"
    
    def test_calculate_risk_critical(self):
        """Test risk calculation with critical database failure."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "databases": {"status": "fail", "error": "Corruption detected"},
            "tests": {"status": "pass"}
        }
        errors = ["databases: Corruption detected"]
        
        risk = validator._calculate_risk(check_results, errors)
        assert risk == "critical"
    
    def test_calculate_risk_high(self):
        """Test risk calculation with multiple high-risk failures."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "fail"},
            "disk_space": {"status": "fail"}
        }
        errors = ["tests: Failed", "disk_space: Low"]
        
        risk = validator._calculate_risk(check_results, errors)
        assert risk == "high"


class TestHealthValidatorIntegration:
    """Test full health validation workflow."""
    
    @patch('subprocess.run')
    @patch('os.statvfs')
    def test_execute_healthy_system(self, mock_statvfs, mock_run):
        """Test execute with healthy system."""
        # Mock disk space
        mock_stat = Mock()
        mock_stat.f_bavail = 100 * (1024 ** 3) // 4096
        mock_stat.f_frsize = 4096
        mock_stat.f_blocks = 500 * (1024 ** 3) // 4096
        mock_statvfs.return_value = mock_stat
        
        # Mock git and tests
        mock_run.side_effect = [
            Mock(returncode=0, stdout="50 passed in 1.23s", stderr=""),  # tests
            Mock(returncode=0, stdout=".git", stderr=""),  # git check
            Mock(returncode=0, stdout="", stderr="")  # git status
        ]
        
        # Create temp database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            conn = sqlite3.connect(tmp_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
            conn.close()
            
            tier1 = Mock()
            tier1.db_path = tmp_path
            
            validator = HealthValidator(name="TestValidator", tier1_api=tier1)
            
            request = AgentRequest(
                intent=IntentType.HEALTH_CHECK.value,
                context={},
                user_message="Check system health"
            )
            
            response = validator.execute(request)
            
            assert response.success is True
            assert response.result["status"] == "healthy"
            assert response.result["risk_level"] == "low"
            assert len(response.result["errors"]) == 0
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_execute_with_failures(self):
        """Test execute with system failures."""
        tier1 = Mock()
        tier1.db_path = "/nonexistent/db.db"
        
        validator = HealthValidator(name="TestValidator", tier1_api=tier1)
        
        request = AgentRequest(
            intent=IntentType.HEALTH_CHECK.value,
            context={"skip_tests": True},  # Skip tests to isolate db failure
            user_message="Check system health"
        )
        
        response = validator.execute(request)
        
        assert response.success is False
        assert response.result["status"] == "unhealthy"
        assert len(response.result["errors"]) > 0
        assert "database" in response.result["errors"][0].lower()
    
    def test_suggest_actions_healthy(self):
        """Test action suggestions for healthy system."""
        validator = HealthValidator(name="TestValidator")
        
        actions = validator._suggest_actions("healthy", [], [])
        
        assert len(actions) > 0
        assert "ready" in actions[0].lower()
    
    def test_suggest_actions_database_error(self):
        """Test action suggestions for database errors."""
        validator = HealthValidator(name="TestValidator")
        
        errors = ["database: Corruption detected"]
        actions = validator._suggest_actions("unhealthy", errors, [])
        
        assert any("database" in a.lower() for a in actions)
        assert any("integrity" in a.lower() or "repair" in a.lower() for a in actions)
    
    def test_suggest_actions_test_error(self):
        """Test action suggestions for test failures."""
        validator = HealthValidator(name="TestValidator")
        
        errors = ["tests: 10 failed"]
        actions = validator._suggest_actions("unhealthy", errors, [])
        
        assert any("test" in a.lower() for a in actions)
        assert any("fix" in a.lower() for a in actions)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_execute_exception_handling(self):
        """Test execute handles exceptions gracefully."""
        validator = HealthValidator(name="TestValidator")
        
        # Force an error by passing invalid request
        request = AgentRequest(
            intent=IntentType.HEALTH_CHECK.value,
            context=None,  # Will cause error when accessing context
            user_message="Check"
        )
        
        # Patch context to raise exception
        with patch.object(validator, '_check_databases', side_effect=Exception("Test error")):
            response = validator.execute(request)
            
            assert response.success is False
            assert "failed" in response.message.lower()
    
    def test_format_message_variations(self):
        """Test message formatting for different statuses."""
        validator = HealthValidator(name="TestValidator")
        
        check_results = {
            "db": {"status": "pass"},
            "tests": {"status": "fail"},
            "git": {"status": "warn"}
        }
        
        # Healthy
        msg = validator._format_message("healthy", check_results, [], [])
        assert "healthy" in msg.lower()
        
        # Degraded
        msg = validator._format_message("degraded", check_results, ["warning"], [])
        assert "degraded" in msg.lower()
        
        # Unhealthy
        msg = validator._format_message("unhealthy", check_results, [], ["error"])
        assert "unhealthy" in msg.lower()
    
    @patch('subprocess.run')
    def test_check_tests_timeout(self, mock_run):
        """Test test check handles timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 30)
        
        validator = HealthValidator(name="TestValidator")
        result = validator._check_tests(skip=False)
        
        assert result["status"] == "fail"
        assert "timed out" in result["error"].lower()
