"""
Test suite for pre-commit validator (hybrid smart gate).

Docker-first architecture: Tests YAML-backed wiring validation.

CORE-008: TDD - Tests before code
CORE-027: Audit trail for pre-commit operations
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch

import pytest

from cortex.infrastructure.pre_commit_validator import (
    DecisionType,
    HealthCheckResult,
    HybridGateDecision,
    PreCommitAuditLogger,
    PreCommitConfig,
    PreCommitValidator,
    WiringValidationResult,
)


class TestHealthCheckStage:
    """Stage 1: Quick health check (sub-200ms)"""

    def test_health_check_returns_result(self):
        """Health check should return a HealthCheckResult"""
        validator = PreCommitValidator()
        result = validator.quick_health_check()
        assert isinstance(result, HealthCheckResult)

    def test_health_check_detects_wiring_error(self):
        """Health check should detect wiring configuration errors"""
        validator = PreCommitValidator()

        with patch('cortex.infrastructure.pre_commit_validator.get_orchestrator_count_by_category') as mock_fn:
            mock_fn.side_effect = RuntimeError("Config not available")

            result = validator.quick_health_check()

            assert result.is_healthy is False
            assert "not available" in result.error_message.lower()


class TestWiringValidationStage:
    """Stage 2: Full wiring validation"""

    def test_full_validation_returns_result(self):
        """Full validation should return a WiringValidationResult"""
        validator = PreCommitValidator()
        result = validator.full_wiring_validation()
        assert isinstance(result, WiringValidationResult)


class TestHybridSmartGate:
    """Hybrid gate logic"""

    def test_hybrid_gate_allows_commit_on_healthy_status(self):
        """Hybrid gate should allow commit if health check passes"""
        validator = PreCommitValidator()

        with patch.object(validator, 'quick_health_check') as mock_health:
            mock_health.return_value = HealthCheckResult(
                is_healthy=True,
                orchestrators_count=23,
                wired_count=23,
            )

            decision = validator.evaluate_commit()

            assert decision.allow_commit is True
            assert decision.decision_type == DecisionType.FAST_PATH


class TestPreCommitConfig:
    """YAML-based configuration"""

    def test_config_loads_defaults(self):
        """Config should load defaults when no YAML file exists"""
        config = PreCommitConfig.from_yaml('/nonexistent/path.yaml')

        assert config is not None
        assert config.expected_orchestrator_count == 23


class TestAuditTrail:
    """CORE-027: Audit trail for pre-commit operations"""

    def test_audit_logger_records_decisions(self):
        """Audit logger should record decisions"""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            logger = PreCommitAuditLogger(log_path=f.name)

            decision = HybridGateDecision(
                allow_commit=True,
                decision_type=DecisionType.FAST_PATH,
                validation_time_ms=50.0,
                stage_executed="STAGE_1",
            )

            logger.log_decision(decision)

            records = logger.get_recent_records(limit=1)
            assert len(records) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
