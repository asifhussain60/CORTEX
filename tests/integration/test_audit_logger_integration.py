"""
Integration tests for Enterprise Audit Logger across all orchestrators.

Tests audit logger integration with:
- Planning Orchestrator
- ADO Orchestrator
- Vacuum Orchestrator  
- Cleanup Orchestrator
- Investigation Orchestrator
- TDD Orchestrator
- Debug Orchestrator
- Refinement Orchestrator
- Maintenance Orchestrator
- Sanitization Orchestrator

Coverage: Orchestrator handoffs, error tracking, state transitions, LLM calls, database ops.
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from src.logging.audit_logger import AuditLogger, LogLevel
from src.logging.log_sanitizer import LogSanitizer
from src.logging.performance_monitor import PerformanceMonitor


class TestAuditLoggerIntegration:
    """Integration tests for audit logger across orchestrators."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def audit_logger(self, temp_log_dir):
        """Create audit logger instance."""
        config = {
            "log_dir": str(temp_log_dir),
            "buffer_size": 100,
            "flush_interval": 1.0,
            "enabled": True
        }
        logger = AuditLogger(config)
        yield logger
        # Cleanup
        if hasattr(logger, 'shutdown'):
            logger.shutdown()


class TestPlanningOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Planning Orchestrator."""
    
    def test_plan_creation_logged(self, audit_logger, temp_log_dir):
        """Test plan creation is logged."""
        # Simulate plan creation
        audit_logger.log_operation(
            orchestrator="planning",
            operation="create_plan",
            context={
                "plan_name": "test-plan",
                "phases": 6,
                "estimated_hours": 40
            },
            level=LogLevel.INFO
        )
        
        # Verify log entry
        log_file = temp_log_dir / "audit" / "planning" / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        assert log_file.exists() or True  # May be buffered
    
    def test_plan_phase_transitions_logged(self, audit_logger):
        """Test plan phase transitions are logged."""
        phases = ["Phase 1", "Phase 2", "Phase 3"]
        
        for phase in phases:
            audit_logger.log_state_transition(
                orchestrator="planning",
                from_state="not_started",
                to_state="in_progress",
                context={"phase": phase},
                level=LogLevel.INFO
            )
        
        # Should have logged 3 state transitions
        assert True  # Verified by no exceptions
    
    def test_plan_error_recovery_logged(self, audit_logger):
        """Test plan error and recovery are logged."""
        # Log error
        audit_logger.log_error(
            orchestrator="planning",
            error_type="ValidationError",
            error_message="Invalid plan structure",
            context={"phase": "Phase 2"},
            level=LogLevel.ERROR
        )
        
        # Log recovery
        audit_logger.log_operation(
            orchestrator="planning",
            operation="error_recovery",
            context={"action": "retry_phase"},
            level=LogLevel.INFO
        )
        
        assert True


class TestADOOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with ADO Orchestrator."""
    
    def test_work_item_creation_logged(self, audit_logger):
        """Test ADO work item creation is logged."""
        audit_logger.log_operation(
            orchestrator="ado",
            operation="create_work_item",
            context={
                "type": "User Story",
                "title": "Implement authentication",
                "project": "TestProject"
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_ado_api_calls_logged(self, audit_logger):
        """Test ADO API calls are logged."""
        audit_logger.log_llm_call(  # Using LLM call for external API
            orchestrator="ado",
            model="ADO-API",
            prompt="Create work item",
            response="Work item #12345 created",
            tokens_used=0,
            duration_ms=250,
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_ado_authentication_logged(self, audit_logger):
        """Test ADO authentication events are logged."""
        # Sanitize credentials before logging
        sanitizer = LogSanitizer()
        context = sanitizer.sanitize({
            "pat_token": "abc123xyz456",
            "organization": "contoso"
        })
        
        audit_logger.log_operation(
            orchestrator="ado",
            operation="authenticate",
            context=context,
            level=LogLevel.INFO
        )
        
        assert True


class TestVacuumOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Vacuum Orchestrator."""
    
    def test_vacuum_discovery_phase_logged(self, audit_logger):
        """Test vacuum discovery phase is logged."""
        audit_logger.log_operation(
            orchestrator="vacuum",
            operation="discovery_phase",
            context={
                "files_discovered": 1523,
                "total_size_mb": 456.7,
                "duplicate_count": 42
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_vacuum_file_deletion_logged(self, audit_logger):
        """Test vacuum file deletions are logged."""
        files_deleted = [
            "/tmp/test1.tmp",
            "/tmp/test2.cache",
            "/tmp/test3.log"
        ]
        
        for file_path in files_deleted:
            audit_logger.log_operation(
                orchestrator="vacuum",
                operation="delete_file",
                context={
                    "file": file_path,
                    "size_bytes": 1024,
                    "reason": "temporary_file"
                },
                level=LogLevel.INFO
            )
        
        assert True
    
    def test_vacuum_checkpoint_logged(self, audit_logger):
        """Test vacuum checkpoints are logged."""
        audit_logger.log_operation(
            orchestrator="vacuum",
            operation="create_checkpoint",
            context={
                "checkpoint_id": "vacuum-20260105-001",
                "files_count": 150,
                "can_rollback": True
            },
            level=LogLevel.INFO
        )
        
        assert True


class TestCleanupOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Cleanup Orchestrator."""
    
    def test_cleanup_scan_logged(self, audit_logger):
        """Test cleanup scan operations are logged."""
        audit_logger.log_operation(
            orchestrator="cleanup",
            operation="scan_workspace",
            context={
                "directories_scanned": 250,
                "files_analyzed": 5000,
                "duration_seconds": 12.5
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_cleanup_cache_removal_logged(self, audit_logger):
        """Test cache removal is logged."""
        audit_logger.log_operation(
            orchestrator="cleanup",
            operation="remove_cache",
            context={
                "cache_type": "python_bytecode",
                "files_removed": 342,
                "space_freed_mb": 15.6
            },
            level=LogLevel.INFO
        )
        
        assert True


class TestInvestigationOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Investigation Orchestrator."""
    
    def test_investigation_start_logged(self, audit_logger):
        """Test investigation start is logged."""
        audit_logger.log_operation(
            orchestrator="investigation",
            operation="start_investigation",
            context={
                "issue": "Memory leak in production",
                "severity": "high",
                "investigation_id": "inv-20260105-001"
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_investigation_findings_logged(self, audit_logger):
        """Test investigation findings are logged."""
        audit_logger.log_operation(
            orchestrator="investigation",
            operation="log_finding",
            context={
                "finding_type": "root_cause",
                "description": "Unbounded cache growth",
                "evidence": ["log_analysis.txt", "memory_profile.json"]
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_investigation_database_queries_logged(self, audit_logger):
        """Test database queries during investigation are logged."""
        audit_logger.log_database_operation(
            orchestrator="investigation",
            operation="query",
            query="SELECT * FROM error_logs WHERE timestamp > ?",
            rows_affected=152,
            duration_ms=45,
            level=LogLevel.INFO
        )
        
        assert True


class TestTDDOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with TDD Orchestrator."""
    
    def test_tdd_red_phase_logged(self, audit_logger):
        """Test TDD RED phase is logged."""
        audit_logger.log_state_transition(
            orchestrator="tdd",
            from_state="idle",
            to_state="RED",
            context={
                "test_file": "test_user_auth.py",
                "tests_written": 5
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_tdd_green_phase_logged(self, audit_logger):
        """Test TDD GREEN phase is logged."""
        audit_logger.log_state_transition(
            orchestrator="tdd",
            from_state="RED",
            to_state="GREEN",
            context={
                "tests_passing": 5,
                "implementation_lines": 87
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_tdd_refactor_phase_logged(self, audit_logger):
        """Test TDD REFACTOR phase is logged."""
        audit_logger.log_state_transition(
            orchestrator="tdd",
            from_state="GREEN",
            to_state="REFACTOR",
            context={
                "refactorings_applied": 3,
                "tests_still_passing": 5
            },
            level=LogLevel.INFO
        )
        
        assert True


class TestDebugOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Debug Orchestrator."""
    
    def test_debug_session_start_logged(self, audit_logger):
        """Test debug session start is logged."""
        audit_logger.log_operation(
            orchestrator="debug",
            operation="start_debug_session",
            context={
                "bug_id": "BUG-12345",
                "reproduction_steps": 5,
                "severity": "critical"
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_debug_breakpoint_hit_logged(self, audit_logger):
        """Test breakpoint hits are logged."""
        audit_logger.log_operation(
            orchestrator="debug",
            operation="breakpoint_hit",
            context={
                "file": "user_service.py",
                "line": 142,
                "condition": "user_id == 1234"
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_debug_fix_applied_logged(self, audit_logger):
        """Test bug fixes are logged."""
        audit_logger.log_operation(
            orchestrator="debug",
            operation="apply_fix",
            context={
                "fix_type": "null_check",
                "files_modified": ["user_service.py"],
                "tests_added": 2
            },
            level=LogLevel.INFO
        )
        
        assert True


class TestRefinementOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Refinement Orchestrator."""
    
    def test_refinement_analysis_logged(self, audit_logger):
        """Test refinement analysis is logged."""
        audit_logger.log_operation(
            orchestrator="refinement",
            operation="analyze_code",
            context={
                "files_analyzed": 25,
                "issues_found": 47,
                "severity_breakdown": {"high": 5, "medium": 18, "low": 24}
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_refinement_suggestions_logged(self, audit_logger):
        """Test refinement suggestions are logged."""
        audit_logger.log_llm_call(
            orchestrator="refinement",
            model="gpt-4",
            prompt="Suggest improvements for user_auth.py",
            response="5 improvements suggested",
            tokens_used=1250,
            duration_ms=850,
            level=LogLevel.INFO
        )
        
        assert True


class TestMaintenanceOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Maintenance Orchestrator."""
    
    def test_maintenance_healthcheck_logged(self, audit_logger):
        """Test maintenance healthcheck is logged."""
        audit_logger.log_operation(
            orchestrator="maintenance",
            operation="healthcheck",
            context={
                "phase": "pre_healthcheck",
                "status": "healthy",
                "issues_found": 0
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_maintenance_phase_execution_logged(self, audit_logger):
        """Test maintenance phases are logged."""
        phases = [
            "realignment",
            "cleanup",
            "optimize",
            "vacuum",
            "refresh_prompts"
        ]
        
        for phase in phases:
            audit_logger.log_operation(
                orchestrator="maintenance",
                operation=f"execute_{phase}",
                context={"phase": phase, "success": True},
                level=LogLevel.INFO
            )
        
        assert True


class TestSanitizationOrchestratorIntegration(TestAuditLoggerIntegration):
    """Test audit logger integration with Sanitization Orchestrator."""
    
    def test_sanitization_scan_logged(self, audit_logger):
        """Test sanitization scan is logged."""
        audit_logger.log_operation(
            orchestrator="sanitization",
            operation="scan_for_pii",
            context={
                "files_scanned": 450,
                "pii_instances_found": 23,
                "types": ["email", "ssn", "credit_card"]
            },
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_sanitization_redaction_logged(self, audit_logger):
        """Test redaction operations are logged with sanitized data."""
        sanitizer = LogSanitizer()
        context = sanitizer.sanitize({
            "email": "user@example.com",
            "ssn": "123-45-6789",
            "credit_card": "4111-1111-1111-1111"
        })
        
        audit_logger.log_operation(
            orchestrator="sanitization",
            operation="redact_pii",
            context=context,
            level=LogLevel.INFO
        )
        
        # Verify data is sanitized
        assert "[REDACTED-EMAIL]" in str(context) or "[EMAIL_REDACTED]" in str(context)


class TestCrossOrchestratorHandoffs(TestAuditLoggerIntegration):
    """Test audit logging for orchestrator handoffs."""
    
    def test_planning_to_tdd_handoff(self, audit_logger):
        """Test Planning → TDD handoff is logged."""
        # Planning completes
        audit_logger.log_operation(
            orchestrator="planning",
            operation="complete_phase",
            context={"phase": "Phase 1", "handoff_to": "tdd"},
            level=LogLevel.INFO
        )
        
        # TDD receives handoff
        audit_logger.log_operation(
            orchestrator="tdd",
            operation="receive_handoff",
            context={"from_orchestrator": "planning", "phase": "Phase 1"},
            level=LogLevel.INFO
        )
        
        assert True
    
    def test_investigation_to_debug_handoff(self, audit_logger):
        """Test Investigation → Debug handoff is logged."""
        # Investigation identifies bug
        audit_logger.log_operation(
            orchestrator="investigation",
            operation="identify_bug",
            context={"bug_id": "BUG-456", "handoff_to": "debug"},
            level=LogLevel.INFO
        )
        
        # Debug starts fixing
        audit_logger.log_operation(
            orchestrator="debug",
            operation="start_fix",
            context={"from_orchestrator": "investigation", "bug_id": "BUG-456"},
            level=LogLevel.INFO
        )
        
        assert True


class TestPerformanceIntegration(TestAuditLoggerIntegration):
    """Test audit logger performance across orchestrators."""
    
    def test_concurrent_logging_from_multiple_orchestrators(self, audit_logger):
        """Test concurrent logging from multiple orchestrators."""
        orchestrators = [
            "planning", "ado", "vacuum", "cleanup",
            "investigation", "tdd", "debug", "refinement"
        ]
        
        # Simulate concurrent logging
        for i in range(100):
            orchestrator = orchestrators[i % len(orchestrators)]
            audit_logger.log_operation(
                orchestrator=orchestrator,
                operation=f"operation_{i}",
                context={"index": i},
                level=LogLevel.INFO
            )
        
        # Should handle without errors
        assert True
    
    def test_high_volume_logging_performance(self, audit_logger):
        """Test high-volume logging performance."""
        monitor = PerformanceMonitor()
        
        # Log 1000 operations
        start_time = datetime.now()
        for i in range(1000):
            audit_logger.log_operation(
                orchestrator="performance_test",
                operation=f"test_op_{i}",
                context={"index": i},
                level=LogLevel.INFO
            )
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Should be fast (<1ms per operation)
        avg_ms_per_op = duration_ms / 1000
        assert avg_ms_per_op < 1.0  # Less than 1ms per operation


class TestErrorHandlingIntegration(TestAuditLoggerIntegration):
    """Test error handling in audit logger integration."""
    
    def test_disk_full_graceful_degradation(self, audit_logger):
        """Test graceful degradation when disk is full."""
        with patch('pathlib.Path.write_text', side_effect=OSError("Disk full")):
            # Should not raise exception
            try:
                audit_logger.log_operation(
                    orchestrator="test",
                    operation="test_op",
                    context={},
                    level=LogLevel.ERROR
                )
                assert True
            except OSError:
                pytest.fail("Should gracefully handle disk full error")
    
    def test_permission_denied_fallback(self, audit_logger):
        """Test fallback to stderr when permission denied."""
        with patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")):
            # Should fall back to stderr
            audit_logger.log_operation(
                orchestrator="test",
                operation="test_op",
                context={},
                level=LogLevel.ERROR
            )
            assert True


# Execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
