"""
Test suite for pre-commit validator (hybrid smart gate).

Tests two-stage validation:
- Stage 1: Quick health check (100ms)
- Stage 2: Full wiring validation (triggered on failure)

CORE-008: TDD - Tests before code
CORE-027: Audit trail for pre-commit operations
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Tuple

# These will be implemented next
from cortex.infrastructure.pre_commit_validator import (
    PreCommitValidator,
    HealthCheckResult,
    WiringValidationResult,
    HybridGateDecision,
    PreCommitConfig,
    PreCommitAuditLogger,
)


class TestHealthCheckStage:
    """Stage 1: Quick health check (sub-200ms)"""
    
    def test_health_check_quick_return_on_healthy_registry(self):
        """Health check should return TRUE and complete in <200ms when registry is healthy"""
        validator = PreCommitValidator()
        
        start = datetime.now()
        result = validator.quick_health_check()
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        assert result.is_healthy is True
        assert elapsed < 200, f"Health check took {elapsed}ms (max: 200ms)"
        assert result.orchestrators_count >= 23
        assert result.wired_count >= 23
    
    def test_health_check_detects_uninitialized_registry(self):
        """Health check should detect uninitialized registry"""
        validator = PreCommitValidator()
        
        # Mock uninitialized state
        with patch('cortex.infrastructure.pre_commit_validator.DatabaseBackedRegistry') as mock_db:
            mock_db.side_effect = RuntimeError("Registry not initialized")
            
            result = validator.quick_health_check()
            
            assert result.is_healthy is False
            assert "not initialized" in result.error_message.lower()
    
    def test_health_check_detects_missing_orchestrators(self):
        """Health check should detect missing orchestrators (<23)"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'get_registry_stats') as mock_stats:
            mock_stats.return_value = {'total': 22, 'wired': 22}
            
            result = validator.quick_health_check()
            
            assert result.is_healthy is False
            assert "Expected 23 orchestrators" in result.error_message
    
    def test_health_check_detects_unwired_orchestrators(self):
        """Health check should detect unwired orchestrators"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'get_registry_stats') as mock_stats:
            mock_stats.return_value = {'total': 23, 'wired': 20}
            
            result = validator.quick_health_check()
            
            assert result.is_healthy is False
            assert "3 orchestrators not wired" in result.error_message
    
    def test_health_check_caches_result(self):
        """Health check should cache result for 5 seconds"""
        validator = PreCommitValidator()
        
        # First call
        result1 = validator.quick_health_check()
        cache_hit = False
        
        # Second call immediately after should be cached
        with patch.object(validator, 'get_registry_stats') as mock_stats:
            result2 = validator.quick_health_check()
            cache_hit = not mock_stats.called
        
        assert cache_hit is True
        assert result1 == result2


class TestWiringValidationStage:
    """Stage 2: Full wiring validation (triggered on failure)"""
    
    def test_full_validation_validates_all_23_orchestrators(self):
        """Full validation should check all 23 orchestrators are wired"""
        validator = PreCommitValidator()
        
        result = validator.full_wiring_validation()
        
        assert result.is_valid is True
        assert result.total_orchestrators == 23
        assert result.wired_orchestrators == 23
        assert len(result.orchestrator_details) == 23
    
    def test_full_validation_identifies_unwired_orchestrator(self):
        """Full validation should identify specific unwired orchestrators"""
        validator = PreCommitValidator()
        
        # Mock one unwired orchestrator
        with patch.object(validator, 'get_all_orchestrators') as mock_get:
            orchestrators = [
                {'id': i, 'name': f'Orchestrator{i}', 'wired': 1} 
                for i in range(1, 23)
            ]
            orchestrators.append({'id': 23, 'name': 'BrokenOrch', 'wired': 0})
            mock_get.return_value = orchestrators
            
            result = validator.full_wiring_validation()
            
            assert result.is_valid is False
            assert 'BrokenOrch' in [o['name'] for o in result.unwired_orchestrators]
            assert result.unwired_count == 1
    
    def test_full_validation_checks_schema_integrity(self):
        """Full validation should verify schema matches expected structure"""
        validator = PreCommitValidator()
        
        result = validator.full_wiring_validation()
        
        assert result.schema_valid is True
        assert 'orchestrators' in result.schema_tables
    
    def test_full_validation_checks_mcp_adapter_exposure(self):
        """Full validation should verify MCP adapters are exposed for wired orchestrators"""
        validator = PreCommitValidator()
        
        result = validator.full_wiring_validation()
        
        assert result.mcp_adapters_exposed is True
        assert result.exposed_adapter_count == 23
    
    def test_full_validation_generates_remediation_steps(self):
        """Full validation should suggest remediation steps on failure"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'get_all_orchestrators') as mock_get:
            orchestrators = [
                {'id': i, 'name': f'Orchestrator{i}', 'wired': 1} 
                for i in range(1, 23)
            ]
            orchestrators.append({'id': 23, 'name': 'BrokenOrch', 'wired': 0})
            mock_get.return_value = orchestrators
            
            result = validator.full_wiring_validation()
            
            assert result.remediation_steps is not None
            assert len(result.remediation_steps) > 0
            assert 'BrokenOrch' in result.remediation_steps[0]


class TestHybridSmartGate:
    """Hybrid gate logic: Health check → Full validation if needed"""
    
    def test_hybrid_gate_allows_commit_on_healthy_status(self):
        """Hybrid gate should allow commit immediately if health check passes"""
        validator = PreCommitValidator()
        
        decision = validator.evaluate_commit()
        
        assert decision.allow_commit is True
        assert decision.decision_type == "FAST_PATH"
        assert decision.validation_time_ms < 200
    
    def test_hybrid_gate_runs_full_validation_on_unhealthy_status(self):
        """Hybrid gate should run Stage 2 if Stage 1 fails"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'quick_health_check') as mock_health:
            mock_result = Mock()
            mock_result.is_healthy = False
            mock_result.error_message = "Test failure"
            mock_health.return_value = mock_result
            
            decision = validator.evaluate_commit()
            
            assert decision.decision_type == "FALLBACK_PATH"
            # Stage 2 was called
            assert decision.full_validation_triggered is True
    
    def test_hybrid_gate_blocks_commit_on_validation_failure(self):
        """Hybrid gate should block commit if full validation finds issues"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'full_wiring_validation') as mock_full:
            mock_result = Mock()
            mock_result.is_valid = False
            mock_result.unwired_orchestrators = [
                {'id': 23, 'name': 'BrokenOrch'}
            ]
            mock_result.remediation_steps = ["1. Fix BrokenOrch wiring"]
            mock_full.return_value = mock_result
            
            decision = validator.evaluate_commit()
            
            assert decision.allow_commit is False
            assert "BrokenOrch" in decision.failure_reason
    
    def test_hybrid_gate_decision_includes_metrics(self):
        """Hybrid gate decision should include performance metrics"""
        validator = PreCommitValidator()
        
        decision = validator.evaluate_commit()
        
        assert decision.validation_time_ms is not None
        assert decision.validation_time_ms > 0
        assert decision.stage_executed in ["STAGE_1", "STAGE_1_2", "FULL"]
    
    def test_hybrid_gate_decision_includes_remediation(self):
        """Hybrid gate decision should include remediation on failure"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'full_wiring_validation') as mock_full:
            mock_result = Mock()
            mock_result.is_valid = False
            mock_result.unwired_orchestrators = []
            mock_result.remediation_steps = ["Step 1", "Step 2"]
            mock_full.return_value = mock_result
            
            decision = validator.evaluate_commit()
            
            assert decision.remediation_steps is not None


class TestPreCommitConfig:
    """YAML-based configuration for extensibility"""
    
    def test_config_loads_from_yaml(self):
        """Config should load from .cortex/pre-commit-config.yaml"""
        config = PreCommitConfig.from_yaml()
        
        assert config is not None
        assert config.expected_orchestrator_count >= 23
        assert config.stage_1_timeout_ms == 200
        assert config.stage_2_timeout_ms == 3000
    
    def test_config_can_extend_for_future_orchestrators(self):
        """Config should support adding future orchestrators without code changes"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
expected_orchestrator_count: 30
stage_1_timeout_ms: 200
stage_2_timeout_ms: 3000
validators:
  - type: wiring
    required: true
  - type: mcp_adapter
    required: true
  - type: schema
    required: true
""")
            f.flush()
            
            config = PreCommitConfig.from_yaml(f.name)
            
            assert config.expected_orchestrator_count == 30
            assert len(config.validators) == 3
    
    def test_config_validates_schema(self):
        """Config should validate YAML schema"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: structure:")
            f.flush()
            
            with pytest.raises(ValueError):
                PreCommitConfig.from_yaml(f.name)


class TestAuditTrail:
    """CORE-027: Audit trail for pre-commit operations"""
    
    def test_audit_logger_records_commit_evaluation(self):
        """Audit logger should record every commit evaluation"""
        logger = PreCommitAuditLogger()
        validator = PreCommitValidator(audit_logger=logger)
        
        validator.evaluate_commit()
        
        audit_records = logger.get_recent_records(limit=1)
        assert len(audit_records) > 0
        assert audit_records[0]['event_type'] == 'PRE_COMMIT_EVALUATION'
    
    def test_audit_logger_records_decision_details(self):
        """Audit logger should record decision details (allow/block, reason)"""
        logger = PreCommitAuditLogger()
        validator = PreCommitValidator(audit_logger=logger)
        
        decision = validator.evaluate_commit()
        validator.audit_logger.log_decision(decision)
        
        audit_records = logger.get_recent_records(limit=1)
        assert audit_records[0]['allow_commit'] == decision.allow_commit
        assert audit_records[0]['validation_time_ms'] == decision.validation_time_ms
    
    def test_audit_logger_persists_to_database(self):
        """Audit logger should persist records to .cortex/pre_commit_audit.log"""
        logger = PreCommitAuditLogger()
        
        logger.log_record({
            'event_type': 'TEST_EVENT',
            'timestamp': datetime.now().isoformat(),
            'details': 'test'
        })
        
        # Verify persistence
        import sqlite3
        conn = sqlite3.connect('.cortex/pre_commit_audit.log')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pre_commit_audit WHERE event_type = 'TEST_EVENT'")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count > 0


class TestIntegrationScenarios:
    """Integration tests for end-to-end scenarios"""
    
    def test_scenario_healthy_commit_fast_path(self):
        """Scenario: Developer commits with healthy system → Fast path (100ms)"""
        validator = PreCommitValidator()
        
        decision = validator.evaluate_commit()
        
        assert decision.allow_commit is True
        assert decision.decision_type == "FAST_PATH"
        assert decision.validation_time_ms < 200
    
    def test_scenario_unhealthy_commit_fallback_recovery(self):
        """Scenario: Health check fails → Stage 2 validates → All good → Allow"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'quick_health_check') as mock_health, \
             patch.object(validator, 'full_wiring_validation') as mock_full:
            
            # Stage 1 fails
            health_result = Mock()
            health_result.is_healthy = False
            mock_health.return_value = health_result
            
            # Stage 2 passes (recovery)
            full_result = Mock()
            full_result.is_valid = True
            mock_full.return_value = full_result
            
            decision = validator.evaluate_commit()
            
            assert decision.allow_commit is True
            assert decision.decision_type == "FALLBACK_PATH"
    
    def test_scenario_multiple_consecutive_commits(self):
        """Scenario: Multiple commits in succession use caching effectively"""
        validator = PreCommitValidator()
        
        # First commit - full check
        decision1 = validator.evaluate_commit()
        time1 = decision1.validation_time_ms
        
        # Second commit immediately - should use cache
        decision2 = validator.evaluate_commit()
        time2 = decision2.validation_time_ms
        
        # Second should be faster (cached)
        assert time2 <= time1
        assert decision2.decision_type == "FAST_PATH"


class TestErrorHandling:
    """Error handling and edge cases"""
    
    def test_validator_handles_database_connection_error(self):
        """Validator should gracefully handle database connection errors"""
        validator = PreCommitValidator()
        
        with patch('cortex.infrastructure.pre_commit_validator.sqlite3.connect') as mock_conn:
            mock_conn.side_effect = sqlite3.DatabaseError("Connection failed")
            
            decision = validator.evaluate_commit()
            
            assert decision.allow_commit is False
            assert "Database error" in decision.failure_reason
    
    def test_validator_handles_missing_orchestrator_module(self):
        """Validator should detect missing orchestrator module"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'get_all_orchestrators') as mock_get:
            mock_get.return_value = [
                {'id': 1, 'name': 'BrokenOrch', 'module_path': 'cortex.missing.module', 'wired': 1}
            ]
            
            result = validator.full_wiring_validation()
            
            # Should detect module doesn't exist
            assert result.is_valid is False
    
    def test_validator_handles_timeout_gracefully(self):
        """Validator should timeout Stage 2 after 3 seconds"""
        validator = PreCommitValidator()
        
        with patch.object(validator, 'full_wiring_validation') as mock_full:
            # Simulate timeout
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Stage 2 validation exceeded 3s limit")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(4)  # Set 4 second alarm (Stage 2 should timeout at 3)
            
            try:
                decision = validator.evaluate_commit()
            except TimeoutError:
                pass
            finally:
                signal.alarm(0)  # Cancel alarm


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
