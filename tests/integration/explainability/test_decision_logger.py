"""
WAVE-O Stage 4 Tests: Decision Traceability Logger (ENH-068)
RED Phase - 5 tests for decision logging and audit trails
"""

import pytest
from pathlib import Path
from datetime import datetime
from cortex.intelligence.explainability.decision_logger import (
    DecisionTraceabilityLogger,
    DecisionLog,
    DecisionType,
    DecisionOutcome
)


class TestDecisionLogging:
    """Test decision logging functionality"""
    
    @pytest.fixture
    def logger(self):
        """Create decision logger"""
        return DecisionTraceabilityLogger()
    
    def test_log_resolution_decision(self, logger):
        """Test logging a resolution decision"""
        decision = logger.log_decision(
            decision_type=DecisionType.RESOLUTION,
            context={"contradiction": "timestamp mismatch"},
            outcome=DecisionOutcome.APPROVED,
            rationale="High confidence automatic resolution",
            confidence=0.95
        )
        
        assert decision is not None
        assert decision.decision_type == DecisionType.RESOLUTION
        assert decision.outcome == DecisionOutcome.APPROVED
        assert decision.confidence == 0.95
        assert decision.timestamp is not None
    
    def test_log_validation_decision(self, logger):
        """Test logging a validation decision"""
        decision = logger.log_decision(
            decision_type=DecisionType.VALIDATION,
            context={"file": "test.yaml", "check": "timestamp"},
            outcome=DecisionOutcome.FAILED,
            rationale="Completion date after last_updated",
            confidence=1.0
        )
        
        assert decision.decision_type == DecisionType.VALIDATION
        assert decision.outcome == DecisionOutcome.FAILED


class TestDecisionHistory:
    """Test decision history retrieval"""
    
    @pytest.fixture
    def logger(self):
        """Create decision logger"""
        return DecisionTraceabilityLogger()
    
    def test_retrieve_all_decisions(self, logger):
        """Test retrieving all decisions"""
        # Log multiple decisions
        logger.log_decision(
            decision_type=DecisionType.RESOLUTION,
            context={},
            outcome=DecisionOutcome.APPROVED
        )
        logger.log_decision(
            decision_type=DecisionType.VALIDATION,
            context={},
            outcome=DecisionOutcome.FAILED
        )
        
        history = logger.get_history()
        
        assert len(history) == 2
    
    def test_filter_by_decision_type(self, logger):
        """Test filtering history by decision type"""
        # Log mixed decisions
        logger.log_decision(DecisionType.RESOLUTION, {}, DecisionOutcome.APPROVED)
        logger.log_decision(DecisionType.VALIDATION, {}, DecisionOutcome.FAILED)
        logger.log_decision(DecisionType.RESOLUTION, {}, DecisionOutcome.REJECTED)
        
        resolution_history = logger.get_history(decision_type=DecisionType.RESOLUTION)
        
        assert len(resolution_history) == 2
        assert all(d.decision_type == DecisionType.RESOLUTION for d in resolution_history)


class TestAuditTrail:
    """Test audit trail generation"""
    
    @pytest.fixture
    def logger(self):
        """Create decision logger"""
        return DecisionTraceabilityLogger()
    
    def test_generate_audit_trail(self, logger):
        """Test generating audit trail report"""
        # Log decisions
        logger.log_decision(DecisionType.RESOLUTION, {}, DecisionOutcome.APPROVED, confidence=0.95)
        logger.log_decision(DecisionType.VALIDATION, {}, DecisionOutcome.FAILED, confidence=1.0)
        
        audit_trail = logger.generate_audit_trail()
        
        assert audit_trail is not None
        assert len(audit_trail) > 0
        assert "RESOLUTION" in audit_trail
        assert "VALIDATION" in audit_trail
    
    def test_audit_trail_includes_timestamps(self, logger):
        """Test audit trail includes decision timestamps"""
        logger.log_decision(DecisionType.RESOLUTION, {}, DecisionOutcome.APPROVED)
        
        audit_trail = logger.generate_audit_trail()
        
        # Should contain timestamp information
        assert any(char.isdigit() for char in audit_trail)  # Contains date/time
