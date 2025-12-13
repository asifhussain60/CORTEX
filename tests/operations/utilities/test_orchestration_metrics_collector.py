"""
Test suite for OrchestrationMetricsCollector

Tests silent background metrics collection for orchestrator engagement tracking.
Validates daily folder structure, JSON schema, performance, and reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import pytest
import time
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta


class TestOrchestrationMetricsBasicLogging:
    """Test suite for basic metrics logging"""
    
    def test_log_engagement_start(self):
        """Test logging orchestrator engagement start"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="PlanningOrchestrator",
            operation_type="plan_generation"
        )
        
        assert event_id is not None
        assert isinstance(event_id, str)
        assert len(event_id) > 0
    
    def test_log_engagement_complete(self):
        """Test logging orchestrator engagement completion"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="TDDOrchestrator",
            operation_type="test_execution"
        )
        
        success = collector.log_engagement_complete(
            event_id=event_id,
            status="success",
            result_summary="10 tests passed"
        )
        
        assert success is True
    
    def test_log_engagement_with_error(self):
        """Test logging orchestrator engagement with error"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="GitCheckpointOrchestrator",
            operation_type="checkpoint_creation"
        )
        
        success = collector.log_engagement_complete(
            event_id=event_id,
            status="error",
            error_message="Git repository not found"
        )
        
        assert success is True


class TestOrchestrationMetricsDailyFolderStructure:
    """Test suite for daily folder organization"""
    
    def test_daily_folder_created_automatically(self):
        """Test that daily folder is created automatically on first log"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="TestOrchestrator",
            operation_type="test_operation"
        )
        
        # Check that daily folder exists
        today = datetime.now().strftime("%Y-%m-%d")
        expected_folder = Path("logs/orchestration-metrics") / today
        
        assert expected_folder.exists()
        assert expected_folder.is_dir()
    
    def test_multiple_orchestrators_same_day_folder(self):
        """Test that multiple orchestrators use same daily folder"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id1 = collector.log_engagement_start(
            orchestrator_name="Orchestrator1",
            operation_type="operation1"
        )
        
        event_id2 = collector.log_engagement_start(
            orchestrator_name="Orchestrator2",
            operation_type="operation2"
        )
        
        # Both should be in same daily folder
        today = datetime.now().strftime("%Y-%m-%d")
        daily_folder = Path("logs/orchestration-metrics") / today
        
        metrics_files = list(daily_folder.glob("*.json"))
        
        # Should have at least 2 files (start events)
        assert len(metrics_files) >= 2


class TestOrchestrationMetricsJSONSchema:
    """Test suite for JSON schema validation"""
    
    def test_start_event_json_schema(self):
        """Test that start event has correct JSON schema"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="TestOrchestrator",
            operation_type="test_operation"
        )
        
        # Find the start event file
        today = datetime.now().strftime("%Y-%m-%d")
        daily_folder = Path("logs/orchestration-metrics") / today
        start_file = daily_folder / f"testorchestrator-{event_id[:8]}-start.json"
        
        assert start_file.exists()
        
        # Read and validate JSON
        with open(start_file, 'r') as f:
            event_data = json.load(f)
        
        # Required fields
        assert "event_id" in event_data
        assert "orchestrator_name" in event_data
        assert "operation_type" in event_data
        assert "timestamp" in event_data
        assert "event_type" in event_data
        assert event_data["event_type"] == "start"
    
    def test_complete_event_json_schema(self):
        """Test that complete event has correct JSON schema"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="TestOrchestrator",
            operation_type="test_operation"
        )
        
        collector.log_engagement_complete(
            event_id=event_id,
            status="success"
        )
        
        # Find the complete event file
        today = datetime.now().strftime("%Y-%m-%d")
        daily_folder = Path("logs/orchestration-metrics") / today
        complete_file = daily_folder / f"testorchestrator-{event_id[:8]}-complete.json"
        
        assert complete_file.exists()
        
        # Read and validate JSON
        with open(complete_file, 'r') as f:
            event_data = json.load(f)
        
        # Required fields
        assert "event_id" in event_data
        assert "status" in event_data
        assert "timestamp" in event_data
        assert "duration_ms" in event_data
        assert "event_type" in event_data
        assert event_data["event_type"] == "complete"


class TestOrchestrationMetricsEventMatching:
    """Test suite for matching start/complete events"""
    
    def test_event_id_matches_start_and_complete(self):
        """Test that event_id matches between start and complete events"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        event_id = collector.log_engagement_start(
            orchestrator_name="TestOrchestrator",
            operation_type="test_operation"
        )
        
        collector.log_engagement_complete(
            event_id=event_id,
            status="success"
        )
        
        # Read both files
        today = datetime.now().strftime("%Y-%m-%d")
        daily_folder = Path("logs/orchestration-metrics") / today
        start_file = daily_folder / f"testorchestrator-{event_id[:8]}-start.json"
        complete_file = daily_folder / f"testorchestrator-{event_id[:8]}-complete.json"
        
        with open(start_file, 'r') as f:
            start_data = json.load(f)
        
        with open(complete_file, 'r') as f:
            complete_data = json.load(f)
        
        # Event IDs should match
        assert start_data["event_id"] == complete_data["event_id"]


class TestOrchestrationMetricsDecorator:
    """Test suite for @with_orchestration_metrics decorator"""
    
    def test_decorator_available(self):
        """Test that decorator is importable"""
        from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics
        
        assert callable(with_orchestration_metrics)
    
    def test_decorator_tracks_success(self):
        """Test that decorator tracks successful orchestrator execution"""
        from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics
        
        @with_orchestration_metrics("TestOrchestrator")
        def test_orchestrator():
            return {"success": True}
        
        result = test_orchestrator()
        
        assert result["success"] is True
        
        # Verify metrics logged
        today = datetime.now().strftime("%Y-%m-%d")
        daily_folder = Path("logs/orchestration-metrics") / today
        
        metrics_files = list(daily_folder.glob("testorchestrator-*-start.json"))
        assert len(metrics_files) > 0
    
    def test_decorator_tracks_errors(self):
        """Test that decorator tracks orchestrator errors"""
        from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics
        
        @with_orchestration_metrics("ErrorOrchestrator")
        def failing_orchestrator():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_orchestrator()
        
        # Verify error logged
        today = datetime.now().strftime("%Y-%m-%d")
        daily_folder = Path("logs/orchestration-metrics") / today
        
        complete_files = list(daily_folder.glob("errororchestrator-*-complete.json"))
        assert len(complete_files) > 0
        
        # Read complete file and check error
        with open(complete_files[0], 'r') as f:
            event_data = json.load(f)
        
        assert event_data["status"] == "error"
        assert "error" in event_data


class TestOrchestrationMetricsPerformance:
    """Test suite for performance requirements"""
    
    def test_log_start_performance_under_5ms(self):
        """Test that log_engagement_start completes in <5ms"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        start_time = time.time()
        
        for _ in range(100):
            collector.log_engagement_start(
                orchestrator_name="PerfTestOrchestrator",
                operation_type="perf_test"
            )
        
        elapsed_ms = ((time.time() - start_time) / 100) * 1000
        
        assert elapsed_ms < 5, f"Average log_start time {elapsed_ms:.2f}ms exceeds 5ms limit"
    
    def test_log_complete_performance_under_5ms(self):
        """Test that log_engagement_complete completes in <5ms"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        # Create events to complete
        event_ids = []
        for _ in range(100):
            event_id = collector.log_engagement_start(
                orchestrator_name="PerfTestOrchestrator",
                operation_type="perf_test"
            )
            event_ids.append(event_id)
        
        start_time = time.time()
        
        for event_id in event_ids:
            collector.log_engagement_complete(
                event_id=event_id,
                status="success"
            )
        
        elapsed_ms = ((time.time() - start_time) / 100) * 1000
        
        assert elapsed_ms < 5, f"Average log_complete time {elapsed_ms:.2f}ms exceeds 5ms limit"


class TestOrchestrationMetricsReportGeneration:
    """Test suite for report generation"""
    
    def test_generate_report_for_7_days(self):
        """Test generating metrics report for last 7 days"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        # Create some metrics
        event_id = collector.log_engagement_start(
            orchestrator_name="PlanningOrchestrator",
            operation_type="plan_generation"
        )
        
        collector.log_engagement_complete(
            event_id=event_id,
            status="success"
        )
        
        # Generate report
        report = collector.generate_report(days=7)
        
        assert report is not None
        assert "total_engagements" in report
        assert "orchestrators" in report
        assert "time_period" in report
    
    def test_report_includes_aggregate_statistics(self):
        """Test that report includes aggregate statistics"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        # Create multiple engagements
        for _ in range(5):
            event_id = collector.log_engagement_start(
                orchestrator_name="TestOrchestrator",
                operation_type="test_operation"
            )
            collector.log_engagement_complete(event_id=event_id, status="success")
        
        report = collector.generate_report(days=7)
        
        # Should have statistics
        assert report["total_engagements"] >= 5
        assert "TestOrchestrator" in report["orchestrators"]
        
        orchestrator_stats = report["orchestrators"]["TestOrchestrator"]
        assert "total_engagements" in orchestrator_stats
        assert "success_rate" in orchestrator_stats
        assert "avg_duration_ms" in orchestrator_stats


class TestOrchestrationMetricsRetentionPolicy:
    """Test suite for 30-day retention policy"""
    
    def test_retention_policy_archives_old_data(self):
        """Test that data older than 30 days is archived"""
        from src.operations.utilities.orchestration_metrics_collector import OrchestrationMetricsCollector
        
        collector = OrchestrationMetricsCollector()
        
        # Create old folder (31 days ago)
        old_date = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
        old_folder = Path("logs/orchestration-metrics") / old_date
        old_folder.mkdir(parents=True, exist_ok=True)
        
        # Create dummy file
        dummy_file = old_folder / "old-metric.json"
        dummy_file.write_text('{"test": "data"}')
        
        # Run retention policy
        archived_count = collector.apply_retention_policy(days=30)
        
        # Old folder should be archived or removed
        assert not old_folder.exists() or len(list(old_folder.glob("*.json"))) == 0
        assert archived_count > 0
