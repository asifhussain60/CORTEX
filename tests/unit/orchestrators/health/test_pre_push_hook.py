"""Unit Tests for Pre-Push Health Hook

Tests pre-push hook warning logic.

Author: CORTEX Framework
Phase: PHASE-95 S4
CORE Rules: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.health.hooks.pre_push_health import (
    check_health_score,
    main as pre_push_main,
)
from cortex.orchestrators.health.reports.health_report import HealthReport, HealthMetrics


class TestPrePushHook:
    """Test suite for pre-push hook."""
    
    @patch("cortex.orchestrators.health.hooks.pre_push_health.HealthOrchestrator")
    def test_check_health_no_warnings(self, mock_orchestrator_class: Mock, tmp_path: Path, capsys) -> None:
        """Test health check with no warnings.
        
        Args:
            mock_orchestrator_class: Mock HealthOrchestrator class
            tmp_path: Pytest temporary directory
            capsys: Pytest capsys fixture
        """
        # Mock report with good health
        mock_report = Mock(spec=HealthReport)
        mock_report.metrics = HealthMetrics(
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            health_score=95.0,
        )
        
        mock_orchestrator = Mock()
        mock_orchestrator.run_health_check.return_value = mock_report
        mock_orchestrator_class.return_value = mock_orchestrator
        
        check_health_score(tmp_path)
        
        captured = capsys.readouterr()
        assert "passed" in captured.out.lower()
        assert "95" in captured.out
    
    @patch("cortex.orchestrators.health.hooks.pre_push_health.HealthOrchestrator")
    def test_check_health_with_critical_issues(self, mock_orchestrator_class: Mock, tmp_path: Path, capsys) -> None:
        """Test health check with critical issues.
        
        Args:
            mock_orchestrator_class: Mock HealthOrchestrator class
            tmp_path: Pytest temporary directory
            capsys: Pytest capsys fixture
        """
        mock_report = Mock(spec=HealthReport)
        mock_report.metrics = HealthMetrics(
            total_issues=2,
            critical_issues=2,
            high_issues=0,
            health_score=60.0,
        )
        
        mock_orchestrator = Mock()
        mock_orchestrator.run_health_check.return_value = mock_report
        mock_orchestrator_class.return_value = mock_orchestrator
        
        check_health_score(tmp_path)
        
        captured = capsys.readouterr()
        assert "CRITICAL" in captured.out
        assert "2" in captured.out
    
    @patch("cortex.orchestrators.health.hooks.pre_push_health.HealthOrchestrator")
    def test_check_health_with_high_issues(self, mock_orchestrator_class: Mock, tmp_path: Path, capsys) -> None:
        """Test health check with high priority issues.
        
        Args:
            mock_orchestrator_class: Mock HealthOrchestrator class
            tmp_path: Pytest temporary directory
            capsys: Pytest capsys fixture
        """
        mock_report = Mock(spec=HealthReport)
        mock_report.metrics = HealthMetrics(
            total_issues=3,
            critical_issues=0,
            high_issues=3,
            health_score=70.0,
        )
        
        mock_orchestrator = Mock()
        mock_orchestrator.run_health_check.return_value = mock_report
        mock_orchestrator_class.return_value = mock_orchestrator
        
        check_health_score(tmp_path)
        
        captured = capsys.readouterr()
        assert "HIGH" in captured.out
        assert "3" in captured.out
    
    @patch("cortex.orchestrators.health.hooks.pre_push_health.HealthOrchestrator")
    def test_check_health_low_score(self, mock_orchestrator_class: Mock, tmp_path: Path, capsys) -> None:
        """Test health check with low health score.
        
        Args:
            mock_orchestrator_class: Mock HealthOrchestrator class
            tmp_path: Pytest temporary directory
            capsys: Pytest capsys fixture
        """
        mock_report = Mock(spec=HealthReport)
        mock_report.metrics = HealthMetrics(
            total_issues=5,
            critical_issues=0,
            high_issues=0,
            medium_issues=5,
            health_score=75.0,
        )
        
        mock_orchestrator = Mock()
        mock_orchestrator.run_health_check.return_value = mock_report
        mock_orchestrator_class.return_value = mock_orchestrator
        
        check_health_score(tmp_path)
        
        captured = capsys.readouterr()
        assert "below 80" in captured.out.lower()
        assert "75" in captured.out
    
    @patch("cortex.orchestrators.health.hooks.pre_push_health.check_health_score")
    def test_main_success(self, mock_check: Mock) -> None:
        """Test main function successful execution.
        
        Args:
            mock_check: Mock check_health_score
        """
        exit_code = pre_push_main()
        
        assert exit_code == 0
        mock_check.assert_called_once()
    
    @patch("cortex.orchestrators.health.hooks.pre_push_health.check_health_score")
    def test_main_handles_exception(self, mock_check: Mock, capsys) -> None:
        """Test main function handles exceptions gracefully.
        
        Args:
            mock_check: Mock check_health_score
            capsys: Pytest capsys fixture
        """
        mock_check.side_effect = RuntimeError("Test error")
        
        exit_code = pre_push_main()
        
        assert exit_code == 0  # Always succeeds
        captured = capsys.readouterr()
        assert "failed" in captured.out.lower()
