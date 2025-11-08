"""Tests for HealthValidator reporting components."""

import pytest
from unittest.mock import Mock

from src.cortex_agents.health_validator.reporting import (
    ResultAnalyzer,
    ReportFormatter
)


class TestResultAnalyzer:
    """Test ResultAnalyzer functionality."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = ResultAnalyzer()
        assert analyzer.RISK_LEVELS["databases"] == "critical"
        assert analyzer.RISK_LEVELS["tests"] == "high"
    
    def test_analyze_all_passing(self):
        """Test analysis with all checks passing."""
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"},
            "git": {"status": "pass"}
        }
        
        analyzer = ResultAnalyzer()
        status, warnings, errors = analyzer.analyze_results(check_results)
        
        assert status == "healthy"
        assert len(errors) == 0
        assert len(warnings) == 0
    
    def test_analyze_with_warnings(self):
        """Test analysis with warnings."""
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"},
            "git": {
                "status": "warn",
                "message": "High uncommitted changes",
                "warnings": ["60 uncommitted files"]
            }
        }
        
        analyzer = ResultAnalyzer()
        status, warnings, errors = analyzer.analyze_results(check_results)
        
        assert status == "degraded"
        assert len(warnings) > 0
        assert len(errors) == 0
    
    def test_analyze_with_errors(self):
        """Test analysis with errors."""
        check_results = {
            "databases": {
                "status": "fail",
                "error": "Database not found",
                "errors": ["Tier 1: db file missing"]
            },
            "tests": {"status": "pass"},
            "git": {"status": "pass"}
        }
        
        analyzer = ResultAnalyzer()
        status, warnings, errors = analyzer.analyze_results(check_results)
        
        assert status == "unhealthy"
        assert len(errors) > 0
    
    def test_calculate_risk_no_errors(self):
        """Test risk calculation with no errors."""
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"}
        }
        
        analyzer = ResultAnalyzer()
        risk = analyzer.calculate_risk(check_results, [])
        
        assert risk == "low"
    
    def test_calculate_risk_critical_failure(self):
        """Test risk calculation with critical failure."""
        check_results = {
            "databases": {"status": "fail"},
            "tests": {"status": "pass"}
        }
        
        analyzer = ResultAnalyzer()
        risk = analyzer.calculate_risk(check_results, ["Database error"])
        
        assert risk == "critical"
    
    def test_calculate_risk_high_failures(self):
        """Test risk calculation with multiple high-risk failures."""
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "fail"},
            "disk": {"status": "fail"}
        }
        
        analyzer = ResultAnalyzer()
        risk = analyzer.calculate_risk(check_results, ["Test error", "Disk error"])
        
        assert risk == "high"


class TestReportFormatter:
    """Test ReportFormatter functionality."""
    
    def test_formatter_initialization(self):
        """Test formatter initializes correctly."""
        formatter = ReportFormatter()
        assert formatter is not None
    
    def test_format_healthy_message(self):
        """Test formatting healthy status message."""
        check_results = {
            "databases": {"status": "pass"},
            "tests": {"status": "pass"}
        }
        
        formatter = ReportFormatter()
        message = formatter.format_message("healthy", [], [], check_results)
        
        assert "HEALTHY" in message
        assert "databases: pass" in message
        assert "tests: pass" in message
    
    def test_format_message_with_errors(self):
        """Test formatting message with errors."""
        check_results = {
            "databases": {"status": "fail"},
            "tests": {"status": "pass"}
        }
        errors = ["databases: Database not found"]
        
        formatter = ReportFormatter()
        message = formatter.format_message("unhealthy", [], errors, check_results)
        
        assert "UNHEALTHY" in message
        assert "ERRORS" in message
        assert "Database not found" in message
    
    def test_format_message_with_warnings(self):
        """Test formatting message with warnings."""
        check_results = {
            "git": {"status": "warn"}
        }
        warnings = ["git: High uncommitted changes"]
        
        formatter = ReportFormatter()
        message = formatter.format_message("degraded", warnings, [], check_results)
        
        assert "DEGRADED" in message
        assert "WARNINGS" in message
        assert "uncommitted" in message
    
    def test_suggest_actions_database_failure(self):
        """Test action suggestions for database failures."""
        check_results = {
            "databases": {
                "status": "fail",
                "errors": ["Tier 1: database not found"]
            }
        }
        
        formatter = ReportFormatter()
        suggestions = formatter.suggest_actions(check_results, "critical")
        
        assert len(suggestions) > 0
        assert any("database" in s.lower() for s in suggestions)
        assert any("CRITICAL" in s for s in suggestions)
    
    def test_suggest_actions_test_failure(self):
        """Test action suggestions for test failures."""
        check_results = {
            "tests": {
                "status": "fail",
                "pass_rate": 0.4,
                "failed": 6
            }
        }
        
        formatter = ReportFormatter()
        suggestions = formatter.suggest_actions(check_results, "high")
        
        assert len(suggestions) > 0
        assert any("test" in s.lower() for s in suggestions)
    
    def test_suggest_actions_git_warning(self):
        """Test action suggestions for git warnings."""
        check_results = {
            "git": {
                "status": "warn",
                "uncommitted_count": 150
            }
        }
        
        formatter = ReportFormatter()
        suggestions = formatter.suggest_actions(check_results, "medium")
        
        assert len(suggestions) > 0
        assert any("commit" in s.lower() for s in suggestions)
    
    def test_suggest_actions_disk_failure(self):
        """Test action suggestions for disk failures."""
        check_results = {
            "disk_space": {
                "status": "fail",
                "free_gb": 0.5
            }
        }
        
        formatter = ReportFormatter()
        suggestions = formatter.suggest_actions(check_results, "high")
        
        assert len(suggestions) > 0
        assert any("disk" in s.lower() for s in suggestions)
    
    def test_get_status_icon(self):
        """Test status icon mapping."""
        formatter = ReportFormatter()
        
        assert formatter._get_status_icon("pass") == "✅"
        assert formatter._get_status_icon("warn") == "⚠️"
        assert formatter._get_status_icon("fail") == "❌"
        assert formatter._get_status_icon("skip") == "⏭️"
        assert formatter._get_status_icon("unknown") == "❓"
