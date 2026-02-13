"""
Tests for Scaffolder Audit Logger (AC-WAVE-2-S1-AUDIT-001)

Comprehensive test coverage for audit trail logging functionality.
"""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from cortex.tools.scaffolder_audit_logger import (
    AuditLogEntry,
    AuditOperation,
    QualityScoreBreakdown,
    RegistryQueryResult,
    ReplacementAction,
    ScaffolderAuditLogger,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    db_path.unlink()


@pytest.fixture
def audit_logger(temp_db):
    """Create audit logger with temp database."""
    return ScaffolderAuditLogger(db_path=temp_db)


class TestScaffolderAuditLoggerInitialization:
    """Test audit logger initialization."""
    
    def test_logger_creates_audit_table(self, temp_db):
        """Audit logger creates table on init."""
        logger = ScaffolderAuditLogger(db_path=temp_db)
        
        with sqlite3.connect(str(temp_db)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='scaffolder_audit_log'"
            )
            tables = cursor.fetchall()
            assert len(tables) == 1
            assert tables[0][0] == "scaffolder_audit_log"
    
    def test_logger_creates_indices(self, temp_db):
        """Audit logger creates indices for performance."""
        logger = ScaffolderAuditLogger(db_path=temp_db)
        
        with sqlite3.connect(str(temp_db)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            indices = {row[0] for row in cursor.fetchall()}
            assert "idx_scaffolder_audit_operation" in indices
            assert "idx_scaffolder_audit_orchestrator" in indices


class TestPreScaffoldingCheckLogging:
    """Test pre-scaffolding registry query logging."""
    
    def test_log_pre_scaffolding_check_writes_entry(self, audit_logger):
        """Pre-scaffolding check logs entry with all fields."""
        query_result = RegistryQueryResult(
            found=True,
            location="cortex/orchestrators/core/master_orchestrator.py",
            capability_overlap=0.8,
            name_collision=True,
        )
        
        ac_marker = audit_logger.log_pre_scaffolding_check(
            orchestrator_name="TestOrchestrator",
            query_result=query_result,
            decision="upgrade",
            decision_rationale="Existing implementation found, propose upgrade",
            user_override=False,
        )
        
        assert ac_marker.startswith("AC-WAVE-2-S1A-")
        
        # Verify entry in database
        logs = audit_logger.query_logs(orchestrator_name="TestOrchestrator")
        assert len(logs) == 1
        assert logs[0].operation == AuditOperation.PRE_SCAFFOLDING_CHECK.value
        assert logs[0].orchestrator_name == "TestOrchestrator"
        assert logs[0].details["decision"] == "upgrade"
    
    def test_log_duplicate_not_found(self, audit_logger):
        """Log when no duplicate found."""
        query_result = RegistryQueryResult(found=False)
        
        ac_marker = audit_logger.log_pre_scaffolding_check(
            orchestrator_name="NewOrchestrator",
            query_result=query_result,
            decision="create_new",
            decision_rationale="No existing implementation",
            user_override=False,
        )
        
        logs = audit_logger.query_logs(orchestrator_name="NewOrchestrator")
        assert len(logs) == 1
        assert logs[0].details["registry_query_result"]["found"] is False
        assert logs[0].details["decision"] == "create_new"


class TestHolisticReplacementLogging:
    """Test holistic replacement operation logging."""
    
    def test_log_holistic_replacement_success(self, audit_logger):
        """Holistic replacement logs all actions."""
        actions = [
            ReplacementAction(action="backup", path="/old/path", success=True),
            ReplacementAction(action="scaffold", path="/new/path", success=True),
            ReplacementAction(action="migrate_tests", path="/tests", success=True, details="15 tests migrated"),
        ]
        
        ac_marker = audit_logger.log_holistic_replacement(
            orchestrator_name="TestOrchestrator",
            old_location="/old/implementation",
            old_version="1.0",
            collision_type="name",
            user_choice="replace",
            actions_taken=actions,
            registry_updated=True,
            core_035_violation=False,
        )
        
        assert ac_marker.startswith("AC-WAVE-2-S1B-")
        
        logs = audit_logger.query_logs(orchestrator_name="TestOrchestrator")
        assert len(logs) == 1
        assert logs[0].operation == AuditOperation.HOLISTIC_REPLACEMENT.value
        assert len(logs[0].details["actions_taken"]) == 3
        assert logs[0].details["registry_updated"] is True
    
    def test_log_core_035_violation_attempt(self, audit_logger):
        """Log CORE-035 violation when user tries to create version."""
        ac_marker = audit_logger.log_holistic_replacement(
            orchestrator_name="TestOrchestrator",
            old_location="/old/implementation",
            old_version="1.0",
            collision_type="both",
            user_choice="version",
            actions_taken=[],
            registry_updated=False,
            core_035_violation=True,
        )
        
        logs = audit_logger.query_logs(orchestrator_name="TestOrchestrator")
        assert len(logs) == 1
        assert logs[0].details["core_035_violation"] is True
        assert logs[0].details["user_choice"] == "version"


class TestIntelligentTestGenerationLogging:
    """Test intelligent test generation logging."""
    
    def test_log_demand_generation_stage(self, audit_logger):
        """Log demand generation stage."""
        demand_analysis = {
            "spec_source": "wiring/specifications/test_orchestrator.yaml",
            "capabilities_identified": 5,
            "edge_cases_detected": 3,
            "demand_yaml_generated": True,
        }
        
        ac_marker = audit_logger.log_intelligent_test_generation(
            orchestrator_name="TestOrchestrator",
            stage="demand",
            spec_source="wiring/specifications/test_orchestrator.yaml",
            demand_analysis=demand_analysis,
        )
        
        assert ac_marker.startswith("AC-WAVE-2-S2-TESTORCHESTRATOR-")
        
        logs = audit_logger.query_logs(orchestrator_name="TestOrchestrator")
        assert len(logs) == 1
        assert logs[0].details["stage"] == "demand"
        assert logs[0].details["demand_analysis"]["capabilities_identified"] == 5
    
    def test_log_composition_stage(self, audit_logger):
        """Log test composition stage."""
        composition = {
            "tests_composed": 10,
            "golden_path_limited": True,
            "realistic_data_injected": True,
            "mocks_minimized": True,
        }
        
        audit_logger.log_intelligent_test_generation(
            orchestrator_name="TestOrchestrator",
            stage="compose",
            spec_source="wiring/specifications/test_orchestrator.yaml",
            demand_analysis={},
            composition=composition,
        )
        
        logs = audit_logger.query_logs(orchestrator_name="TestOrchestrator")
        assert len(logs) == 1
        assert logs[0].details["composition"]["tests_composed"] == 10
    
    def test_log_validation_stage(self, audit_logger):
        """Log quality validation stage."""
        quality_scores = QualityScoreBreakdown(
            coverage_score=0.85,
            realism_score=0.90,
            maintainability_score=0.75,
            brittleness_score=0.05,
            composite_score=0.82,
            gate_passed=True,
            brittleness_patterns=["hardcoded_sleep"],
        )
        
        audit_logger.log_intelligent_test_generation(
            orchestrator_name="TestOrchestrator",
            stage="validate",
            spec_source="wiring/specifications/test_orchestrator.yaml",
            demand_analysis={},
            quality_validation=quality_scores,
        )
        
        logs = audit_logger.query_logs(orchestrator_name="TestOrchestrator")
        assert len(logs) == 1
        assert logs[0].details["quality_validation"]["composite_score"] == 0.82
        assert logs[0].details["quality_validation"]["gate_passed"] is True


class TestAuditLogQuerying:
    """Test audit log query functionality."""
    
    def test_query_logs_by_operation(self, audit_logger):
        """Query logs filtered by operation type."""
        # Log different operations
        query_result = RegistryQueryResult(found=False)
        audit_logger.log_pre_scaffolding_check(
            orchestrator_name="Orch1",
            query_result=query_result,
            decision="create_new",
            decision_rationale="test",
        )
        
        audit_logger.log_intelligent_test_generation(
            orchestrator_name="Orch2",
            stage="demand",
            spec_source="test.yaml",
            demand_analysis={},
        )
        
        # Query by operation
        pre_check_logs = audit_logger.query_logs(
            operation=AuditOperation.PRE_SCAFFOLDING_CHECK.value
        )
        assert len(pre_check_logs) == 1
        assert pre_check_logs[0].orchestrator_name == "Orch1"
        
        test_gen_logs = audit_logger.query_logs(
            operation=AuditOperation.INTELLIGENT_TEST_GENERATION.value
        )
        assert len(test_gen_logs) == 1
        assert test_gen_logs[0].orchestrator_name == "Orch2"
    
    def test_query_logs_by_orchestrator_name(self, audit_logger):
        """Query logs filtered by orchestrator name."""
        query_result = RegistryQueryResult(found=False)
        
        audit_logger.log_pre_scaffolding_check(
            orchestrator_name="OrchestratorA",
            query_result=query_result,
            decision="create_new",
            decision_rationale="test",
        )
        
        audit_logger.log_pre_scaffolding_check(
            orchestrator_name="OrchestratorB",
            query_result=query_result,
            decision="create_new",
            decision_rationale="test",
        )
        
        logs_a = audit_logger.query_logs(orchestrator_name="OrchestratorA")
        assert len(logs_a) == 1
        assert logs_a[0].orchestrator_name == "OrchestratorA"
    
    def test_query_logs_respects_limit(self, audit_logger):
        """Query logs respects limit parameter."""
        query_result = RegistryQueryResult(found=False)
        
        # Create 5 log entries
        for i in range(5):
            audit_logger.log_pre_scaffolding_check(
                orchestrator_name=f"Orch{i}",
                query_result=query_result,
                decision="create_new",
                decision_rationale="test",
            )
        
        logs = audit_logger.query_logs(limit=3)
        assert len(logs) == 3
