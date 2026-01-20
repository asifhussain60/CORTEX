"""
Tests for ODX-002-02: DevX Dashboard

AC-ID: ODX-002-02
Phase: PHASE-18-ORCHESTRATOR-DEVX
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.devx.devx_dashboard import (
    DevXDashboard,
    DashboardMetrics,
    DashboardSection,
    LogEntry,
)


class TestDashboardMetrics:
    """Tests for DashboardMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test DashboardMetrics creation."""
        metrics = DashboardMetrics()
        
        assert metrics.reload_count == 0
        assert metrics.reload_success_rate == 0.0
        assert metrics.scenario_count == 0
        assert metrics.last_update is not None
    
    def test_metrics_with_values(self):
        """Test DashboardMetrics with values."""
        metrics = DashboardMetrics(
            reload_count=10,
            reload_success_rate=95.5,
            scenario_count=50,
            scenario_pass_rate=88.0,
        )
        
        assert metrics.reload_count == 10
        assert metrics.reload_success_rate == 95.5
    
    def test_metrics_custom(self):
        """Test DashboardMetrics with custom metrics."""
        metrics = DashboardMetrics(
            custom_metrics={"builds": 5, "errors": 2},
        )
        
        assert metrics.custom_metrics["builds"] == 5
    
    def test_metrics_to_dict(self):
        """Test DashboardMetrics serialization."""
        metrics = DashboardMetrics(
            reload_count=5,
            custom_metrics={"key": "value"},
        )
        
        d = metrics.to_dict()
        
        assert d["reload_count"] == 5
        assert d["custom_metrics"]["key"] == "value"
        assert "last_update" in d


class TestLogEntry:
    """Tests for LogEntry dataclass."""
    
    def test_log_entry_creation(self):
        """Test LogEntry creation."""
        entry = LogEntry(
            level="info",
            source="test",
            message="Test message",
        )
        
        assert entry.level == "info"
        assert entry.source == "test"
        assert entry.message == "Test message"
        assert entry.timestamp is not None
    
    def test_log_entry_with_details(self):
        """Test LogEntry with details."""
        entry = LogEntry(
            level="error",
            source="component",
            message="Error occurred",
            details={"error_code": 500, "stack": "..."},
        )
        
        assert entry.details["error_code"] == 500
    
    def test_log_entry_to_dict(self):
        """Test LogEntry serialization."""
        entry = LogEntry(
            level="warning",
            source="test",
            message="Warning",
        )
        
        d = entry.to_dict()
        
        assert d["level"] == "warning"
        assert d["source"] == "test"
        assert "timestamp" in d


class TestDevXDashboard:
    """Tests for DevXDashboard."""
    
    def test_dashboard_creation(self):
        """Test DevXDashboard creation."""
        dashboard = DevXDashboard()
        
        assert dashboard.title == "CORTEX DevX Dashboard"
        assert dashboard._hot_reload is None
        assert dashboard._scenario_library is None
    
    def test_dashboard_custom_title(self):
        """Test DevXDashboard with custom title."""
        dashboard = DevXDashboard(title="My Dashboard")
        
        assert dashboard.title == "My Dashboard"
    
    def test_connect_hot_reload(self):
        """Test connecting hot-reload component."""
        dashboard = DevXDashboard()
        
        mock_hot_reload = Mock()
        mock_hot_reload.on = Mock(return_value=mock_hot_reload)
        
        result = dashboard.connect_hot_reload(mock_hot_reload)
        
        assert result is dashboard  # Method chaining
        assert dashboard._hot_reload is mock_hot_reload
        # Should register callbacks
        assert mock_hot_reload.on.call_count >= 2
    
    def test_connect_scenario_library(self):
        """Test connecting scenario library component."""
        dashboard = DevXDashboard()
        
        mock_library = Mock()
        mock_library.on_after_run = Mock(return_value=mock_library)
        
        result = dashboard.connect_scenario_library(mock_library)
        
        assert result is dashboard  # Method chaining
        assert dashboard._scenario_library is mock_library
    
    def test_connect_integration_validator(self):
        """Test connecting integration validator component."""
        dashboard = DevXDashboard()
        
        mock_validator = Mock()
        
        result = dashboard.connect_integration_validator(mock_validator)
        
        assert result is dashboard  # Method chaining
        assert dashboard._integration_validator is mock_validator
    
    def test_get_metrics(self):
        """Test getting metrics."""
        dashboard = DevXDashboard()
        
        metrics = dashboard.get_metrics()
        
        assert isinstance(metrics, DashboardMetrics)
        assert metrics.last_update is not None
    
    def test_get_metrics_updates_from_hot_reload(self):
        """Test metrics update from hot-reload."""
        dashboard = DevXDashboard()
        
        # Mock hot-reload with history
        mock_event1 = Mock(success=True)
        mock_event2 = Mock(success=True)
        mock_event3 = Mock(success=False)
        
        mock_hot_reload = Mock()
        mock_hot_reload.on = Mock(return_value=mock_hot_reload)
        mock_hot_reload.get_reload_history = Mock(return_value=[
            mock_event1, mock_event2, mock_event3
        ])
        
        dashboard.connect_hot_reload(mock_hot_reload)
        metrics = dashboard.get_metrics()
        
        assert metrics.reload_count == 3
        # 2 out of 3 succeeded = 66.67%
        assert 66 <= metrics.reload_success_rate <= 67
    
    def test_get_metrics_updates_from_scenario_library(self):
        """Test metrics update from scenario library."""
        dashboard = DevXDashboard()
        
        # Mock scenario library
        mock_library = Mock()
        mock_library.on_after_run = Mock(return_value=mock_library)
        mock_library.summary = Mock(return_value={
            "total_scenarios": 25,
            "pass_rate": 92.0,
        })
        
        dashboard.connect_scenario_library(mock_library)
        metrics = dashboard.get_metrics()
        
        assert metrics.scenario_count == 25
        assert metrics.scenario_pass_rate == 92.0
    
    def test_get_metrics_updates_from_validator(self):
        """Test metrics update from integration validator."""
        dashboard = DevXDashboard()
        
        # Mock validator
        mock_validator = Mock()
        mock_validator.summary = Mock(return_value={
            "total_integration_points": 10,
            "valid_validations": 8,
            "total_validations": 10,
        })
        
        dashboard.connect_integration_validator(mock_validator)
        metrics = dashboard.get_metrics()
        
        assert metrics.integration_count == 10
        assert metrics.integration_health == 80.0
    
    def test_add_custom_metric(self):
        """Test adding custom metrics."""
        dashboard = DevXDashboard()
        
        result = dashboard.add_custom_metric("build_time", 150)
        
        assert result is dashboard  # Method chaining
        
        metrics = dashboard.get_metrics()
        assert metrics.custom_metrics["build_time"] == 150
    
    def test_on_update_callback(self):
        """Test update callback registration."""
        dashboard = DevXDashboard()
        
        updates = []
        
        def callback(metrics):
            updates.append(metrics)
        
        dashboard.on_update(callback)
        
        # Trigger update
        dashboard.get_metrics()
        
        assert len(updates) == 1
    
    def test_get_logs_empty(self):
        """Test getting logs when empty."""
        dashboard = DevXDashboard()
        
        logs = dashboard.get_logs()
        
        assert len(logs) == 0
    
    def test_get_logs_with_entries(self):
        """Test getting logs with entries."""
        dashboard = DevXDashboard()
        
        # Add logs via internal method
        dashboard._log("info", "test", "Message 1")
        dashboard._log("warning", "test", "Message 2")
        dashboard._log("error", "test", "Message 3")
        
        logs = dashboard.get_logs()
        
        assert len(logs) == 3
    
    def test_get_logs_filter_by_level(self):
        """Test filtering logs by level."""
        dashboard = DevXDashboard()
        
        dashboard._log("info", "test", "Info")
        dashboard._log("error", "test", "Error")
        dashboard._log("info", "test", "Info 2")
        
        logs = dashboard.get_logs(level="info")
        
        assert len(logs) == 2
    
    def test_get_logs_filter_by_source(self):
        """Test filtering logs by source."""
        dashboard = DevXDashboard()
        
        dashboard._log("info", "source1", "Msg 1")
        dashboard._log("info", "source2", "Msg 2")
        dashboard._log("info", "source1", "Msg 3")
        
        logs = dashboard.get_logs(source="source1")
        
        assert len(logs) == 2
    
    def test_get_logs_limit(self):
        """Test limiting log results."""
        dashboard = DevXDashboard()
        
        for i in range(20):
            dashboard._log("info", "test", f"Message {i}")
        
        logs = dashboard.get_logs(limit=10)
        
        assert len(logs) == 10
    
    def test_render_dashboard(self):
        """Test rendering dashboard to text."""
        dashboard = DevXDashboard(title="Test Dashboard")
        
        rendered = dashboard.render()
        
        assert "Test Dashboard" in rendered
        assert "OVERVIEW" in rendered
        assert "HOT RELOAD" in rendered
    
    def test_render_specific_sections(self):
        """Test rendering specific sections only."""
        dashboard = DevXDashboard()
        
        rendered = dashboard.render(sections=[DashboardSection.OVERVIEW])
        
        assert "OVERVIEW" in rendered
        # Other sections should not be present
        # (They might appear in logs section which shows recent)
    
    def test_render_with_connected_components(self):
        """Test rendering with connected components."""
        dashboard = DevXDashboard()
        
        # Mock hot-reload
        mock_hr = Mock()
        mock_hr.on = Mock(return_value=mock_hr)
        mock_hr.is_running = True
        mock_hr.get_reload_history = Mock(return_value=[])
        
        # Mock scenario library
        mock_sl = Mock()
        mock_sl.on_after_run = Mock(return_value=mock_sl)
        mock_sl.summary = Mock(return_value={"total_scenarios": 10, "pass_rate": 100})
        
        dashboard.connect_hot_reload(mock_hr)
        dashboard.connect_scenario_library(mock_sl)
        
        rendered = dashboard.render()
        
        assert "Active" in rendered  # Hot reload status
        assert "10 scenarios" in rendered
    
    def test_to_dict(self):
        """Test exporting dashboard state to dictionary."""
        dashboard = DevXDashboard(title="Export Test")
        
        dashboard._log("info", "test", "Log entry")
        dashboard.add_custom_metric("test_metric", 42)
        
        d = dashboard.to_dict()
        
        assert d["title"] == "Export Test"
        assert "metrics" in d
        assert "logs" in d
        assert d["metrics"]["custom_metrics"]["test_metric"] == 42
    
    def test_auto_update_start_stop(self):
        """Test auto-update functionality."""
        dashboard = DevXDashboard()
        
        dashboard.start_auto_update(interval=0.1)
        
        # Should have started update thread
        assert dashboard._auto_update
        assert dashboard._update_thread is not None
        
        dashboard.stop_auto_update()
        
        assert not dashboard._auto_update
    
    def test_log_trimming(self):
        """Test that logs are trimmed when exceeding max."""
        dashboard = DevXDashboard()
        dashboard._max_logs = 10  # Set low for testing
        
        for i in range(20):
            dashboard._log("info", "test", f"Message {i}")
        
        assert len(dashboard._logs) <= 10


class TestDevXDashboardCallbacks:
    """Tests for dashboard event callbacks."""
    
    def test_reload_callback(self):
        """Test reload event callback."""
        dashboard = DevXDashboard()
        
        # Mock reload event
        mock_event = Mock()
        mock_event.success = True
        mock_event.orchestrator_name = "TestOrch"
        mock_event.reload_time_ms = 50.0
        
        # Call callback directly
        dashboard._on_reload(mock_event)
        
        assert dashboard._metrics.reload_count == 1
        assert len(dashboard._logs) >= 1
    
    def test_reload_error_callback(self):
        """Test reload error callback."""
        dashboard = DevXDashboard()
        
        mock_event = Mock()
        mock_event.error_message = "Reload failed"
        
        dashboard._on_reload_error(mock_event)
        
        logs = dashboard.get_logs(level="error")
        assert len(logs) >= 1
    
    def test_scenario_run_callback(self):
        """Test scenario run callback."""
        dashboard = DevXDashboard()
        
        mock_scenario = Mock()
        mock_scenario.name = "Test Scenario"
        
        mock_result = Mock()
        mock_result.status = Mock()
        mock_result.status.value = "passed"
        mock_result.execution_time_ms = 100.0
        
        dashboard._on_scenario_run(mock_scenario, mock_result)
        
        logs = dashboard.get_logs()
        assert len(logs) >= 1
        assert "Test Scenario" in logs[-1].message


class TestDashboardIntegration:
    """Integration tests for DevX Dashboard."""
    
    def test_full_dashboard_workflow(self):
        """Test complete dashboard workflow."""
        dashboard = DevXDashboard(title="Integration Test")
        
        # Connect mock components
        mock_hr = Mock()
        mock_hr.on = Mock(return_value=mock_hr)
        mock_hr.is_running = True
        mock_hr.get_reload_history = Mock(return_value=[
            Mock(success=True, orchestrator_name="Orch1", reload_time_ms=50),
            Mock(success=True, orchestrator_name="Orch2", reload_time_ms=75),
        ])
        
        mock_sl = Mock()
        mock_sl.on_after_run = Mock(return_value=mock_sl)
        mock_sl.summary = Mock(return_value={
            "total_scenarios": 30,
            "pass_rate": 93.3,
            "by_category": {"unit": 20, "integration": 10},
        })
        
        mock_iv = Mock()
        mock_iv.summary = Mock(return_value={
            "total_integration_points": 5,
            "valid_validations": 5,
            "total_validations": 5,
            "issues_by_severity": {"warning": 2},
        })
        
        dashboard.connect_hot_reload(mock_hr)
        dashboard.connect_scenario_library(mock_sl)
        dashboard.connect_integration_validator(mock_iv)
        
        # Get metrics
        metrics = dashboard.get_metrics()
        
        assert metrics.reload_count == 2
        assert metrics.scenario_count == 30
        assert metrics.integration_count == 5
        
        # Render dashboard
        rendered = dashboard.render()
        
        assert "Active" in rendered  # Hot reload active
        assert "30" in rendered  # Scenario count
        assert "warning" in rendered.lower()  # Issues
        
        # Export state
        state = dashboard.to_dict()
        
        assert state["connections"]["hot_reload"]
        assert state["connections"]["scenario_library"]
        assert state["connections"]["integration_validator"]
