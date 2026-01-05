"""
Test suite for CORTEX Audit Logging System.

Purpose: Test JSON logging, rotation, context managers, decorators.
Phase: 28 (RED phase)
"""

import json
import os
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestAuditLogger(unittest.TestCase):
    """Test core audit logging infrastructure."""
    
    def setUp(self):
        """Create temporary log directory."""
        self.log_dir = tempfile.mkdtemp()
        self.log_file = Path(self.log_dir) / "test-audit.jsonl"
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if Path(self.log_dir).exists():
            shutil.rmtree(self.log_dir, ignore_errors=True)
    
    def test_audit_logger_initialization(self):
        """Test AuditLogger can be instantiated with config."""
        from src.orchestrators.audit_logger import AuditLogger
        
        config = {
            "log_dir": self.log_dir,
            "rotation_size_mb": 10,
            "backup_count": 5,
            "retention_days": 30
        }
        logger = AuditLogger(config)
        
        self.assertIsNotNone(logger)
        self.assertEqual(logger.log_dir, Path(self.log_dir))
        self.assertEqual(logger.rotation_size_mb, 10)
        self.assertEqual(logger.backup_count, 5)
    
    def test_log_handoff_event(self):
        """Test logging handoff events with correct schema."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        request_id = "test-uuid-1234"
        event_data = {
            "pattern_matched": "^(plan|create a plan)",
            "confidence": 1.0,
            "priority": 10,
            "raw_request": "plan OAuth2 system",
            "transformed_request": "plan OAuth2 system with JWT..."
        }
        
        logger.log_handoff(request_id, "planning_v5", event_data)
        
        # Verify log file created
        handoff_log = Path(self.log_dir) / f"handoffs-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.assertTrue(handoff_log.exists())
        
        # Parse and verify JSON structure
        with open(handoff_log) as f:
            log_entry = json.loads(f.read())
        
        self.assertEqual(log_entry["event_type"], "handoff")
        self.assertEqual(log_entry["context"]["request_id"], request_id)
        self.assertEqual(log_entry["context"]["orchestrator"], "planning_v5")
        self.assertEqual(log_entry["data"]["pattern_matched"], "^(plan|create a plan)")
        self.assertIn("timestamp", log_entry)
    
    def test_log_execution_event(self):
        """Test logging execution events (phase start/end)."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        event_data = {
            "phase_number": 23,
            "phase_name": "Fix Python CLI Import Chain",
            "status": "complete",
            "duration_seconds": 0.33,
            "outputs": ["src/config/__init__.py", "src/config/config_manager.py"]
        }
        
        logger.log_execution("plan-uuid", "planning_v5", event_data)
        
        # Verify log entry
        execution_log = Path(self.log_dir) / f"executions-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.assertTrue(execution_log.exists())
        
        with open(execution_log) as f:
            log_entry = json.loads(f.read())
        
        self.assertEqual(log_entry["event_type"], "execution")
        self.assertEqual(log_entry["data"]["phase_number"], 23)
        self.assertEqual(log_entry["data"]["status"], "complete")
    
    def test_log_performance_metric(self):
        """Test logging performance metrics with units."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        logger.log_performance(
            request_id="perf-test-1",
            metric_name="import_time",
            value=450.5,
            unit="ms"
        )
        
        perf_log = Path(self.log_dir) / f"performance-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.assertTrue(perf_log.exists())
        
        with open(perf_log) as f:
            log_entry = json.loads(f.read())
        
        self.assertEqual(log_entry["event_type"], "performance")
        self.assertEqual(log_entry["data"]["metric_name"], "import_time")
        self.assertEqual(log_entry["data"]["value"], 450.5)
        self.assertEqual(log_entry["data"]["unit"], "ms")
    
    def test_log_error_event(self):
        """Test logging errors with stack traces."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        error_data = {
            "error_type": "ImportError",
            "error_message": "cannot import name 'config' from 'src.config'",
            "stack_trace": "Traceback (most recent call last)...",
            "phase": 23,
            "remediation": "Fix import chain"
        }
        
        logger.log_error("error-uuid", "planning_v5", error_data)
        
        error_log = Path(self.log_dir) / f"errors-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.assertTrue(error_log.exists())
        
        with open(error_log) as f:
            log_entry = json.loads(f.read())
        
        self.assertEqual(log_entry["event_type"], "error")
        self.assertEqual(log_entry["data"]["error_type"], "ImportError")
    
    def test_audit_context_manager(self):
        """Test context manager tracks request lifecycle."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        with logger.audit_context("test-request", "planning_v5") as ctx:
            ctx.add_data("pattern", "plan")
            ctx.add_data("confidence", 1.0)
            time.sleep(0.01)  # Simulate work
        
        # Verify context logged on exit
        handoff_log = Path(self.log_dir) / f"handoffs-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(handoff_log) as f:
            log_entry = json.loads(f.read())
        
        self.assertEqual(log_entry["context"]["request_id"], "test-request")
        self.assertIn("duration_ms", log_entry["data"])
    
    def test_log_rotation(self):
        """Test log files rotate at size threshold."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({
            "log_dir": self.log_dir,
            "rotation_size_mb": 0.001  # 1KB for testing
        })
        
        # Write enough data to trigger rotation
        for i in range(200):
            logger.log_handoff(f"request-{i}", "test_orch", {"data": "x" * 100})
        
        # Check for rotation files
        log_files = list(Path(self.log_dir).glob("handoffs-*.jsonl*"))
        self.assertGreater(len(log_files), 1, "Log rotation did not occur")
    
    def test_no_sensitive_data_in_logs(self):
        """Test sensitive data is redacted from logs."""
        from src.orchestrators.audit_logger import AuditLogger
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        sensitive_data = {
            "api_key": "sk-1234567890abcdef",
            "password": "supersecret",
            "token": "ghp_abcdef123456",
            "safe_data": "this is fine"
        }
        
        logger.log_handoff("redact-test", "test", sensitive_data)
        
        handoff_log = Path(self.log_dir) / f"handoffs-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(handoff_log) as f:
            content = f.read()
        
        # Sensitive values should be redacted
        self.assertNotIn("sk-1234567890abcdef", content)
        self.assertNotIn("supersecret", content)
        self.assertNotIn("ghp_abcdef123456", content)
        
        # Safe data should remain
        self.assertIn("this is fine", content)


class TestAuditDecorators(unittest.TestCase):
    """Test performance decorators (@timed, @logged)."""
    
    def setUp(self):
        """Create temporary log directory."""
        self.log_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.log_dir, ignore_errors=True)
    
    def test_timed_decorator(self):
        """Test @timed decorator logs execution time."""
        from src.orchestrators.audit_logger import AuditLogger, timed
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        @timed(logger, "test_function")
        def slow_function():
            time.sleep(0.01)
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")
        
        # Verify performance log created
        perf_log = Path(self.log_dir) / f"performance-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.assertTrue(perf_log.exists())
        
        with open(perf_log) as f:
            log_entry = json.loads(f.read())
        
        self.assertEqual(log_entry["data"]["metric_name"], "test_function_duration")
        self.assertGreater(log_entry["data"]["value"], 10)  # >10ms
    
    def test_logged_decorator(self):
        """Test @logged decorator logs function calls."""
        from src.orchestrators.audit_logger import AuditLogger, logged
        
        logger = AuditLogger({"log_dir": self.log_dir})
        
        @logged(logger, "test_orchestrator")
        def tracked_function(arg1, arg2):
            return arg1 + arg2
        
        result = tracked_function(5, 3)
        self.assertEqual(result, 8)
        
        # Verify execution log created
        exec_log = Path(self.log_dir) / f"executions-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.assertTrue(exec_log.exists())
        
        with open(exec_log) as f:
            # Read all lines and parse last one
            lines = f.readlines()
            log_entry = json.loads(lines[-1])
        
        self.assertEqual(log_entry["data"]["function"], "tracked_function")
        self.assertEqual(log_entry["data"]["args"], [5, 3])


if __name__ == "__main__":
    unittest.main()
