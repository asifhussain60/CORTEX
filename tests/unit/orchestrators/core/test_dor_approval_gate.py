"""
Tests for DoR Approval Gate.

AC-ID: AC-GOVE-DOR-001
Tests Definition of Ready approval gate and intent reflection.
"""

import pytest
from unittest.mock import Mock, patch

from cortex.orchestrators.core.dor_approval_gate import (
    DoRApprovalGate,
    IntentReflection,
    ApprovalStatus,
    ApprovalDecision,
    reflect_intent,
)
from cortex.orchestrators.core.intent_router import IntentType, RoutingDecision


class TestIntentReflection:
    """Tests for IntentReflection dataclass."""

    def test_to_markdown_high_confidence(self) -> None:
        """Test markdown generation with high confidence."""
        reflection = IntentReflection(
            intent_type="implement",
            target_handler="BuilderOrchestrator",
            confidence=0.9,
            scope="MODULE",
            key_entities=["AC-FR-001"],
            estimated_impact="low",
            governance_rules=["CORE-008", "CORE-011"],
        )
        
        md = reflection.to_markdown()
        
        assert "### 📋 Intent Classification" in md
        assert "`implement`" in md
        assert "`BuilderOrchestrator`" in md
        assert "🟢 High" in md
        assert "90%" in md
        assert "`MODULE`" in md
        assert "⏳ Awaiting approval" in md

    def test_to_markdown_medium_confidence(self) -> None:
        """Test markdown generation with medium confidence."""
        reflection = IntentReflection(
            intent_type="fix",
            target_handler="FixOrchestrator",
            confidence=0.65,
            scope="FILE",
        )
        
        md = reflection.to_markdown()
        
        assert "🟡 Medium" in md
        assert "65%" in md

    def test_to_markdown_low_confidence(self) -> None:
        """Test markdown generation with low confidence."""
        reflection = IntentReflection(
            intent_type="refactor",
            target_handler="RefactorOrchestrator",
            confidence=0.4,
            scope="SYSTEM",
            estimated_impact="high",
        )
        
        md = reflection.to_markdown()
        
        assert "🔴 Low" in md
        assert "40%" in md
        assert "🔴 High" in md

    def test_to_markdown_truncates_entities(self) -> None:
        """Test that entities are truncated if more than 3."""
        reflection = IntentReflection(
            intent_type="implement",
            target_handler="Test",
            confidence=0.8,
            scope="MODULE",
            key_entities=["AC-001", "AC-002", "AC-003", "AC-004", "AC-005"],
        )
        
        md = reflection.to_markdown()
        
        assert "+2 more" in md

    def test_to_markdown_no_entities(self) -> None:
        """Test markdown without entities."""
        reflection = IntentReflection(
            intent_type="fix",
            target_handler="Test",
            confidence=0.7,
            scope="FILE",
            key_entities=[],
        )
        
        md = reflection.to_markdown()
        
        assert "Entities" not in md


class TestApprovalDecision:
    """Tests for ApprovalDecision dataclass."""

    def test_approved_decision(self) -> None:
        """Test approved decision creation."""
        decision = ApprovalDecision(
            status=ApprovalStatus.APPROVED,
            feedback="Looks good",
        )
        
        assert decision.status == ApprovalStatus.APPROVED
        assert decision.feedback == "Looks good"
        assert decision.timestamp is not None

    def test_modified_decision(self) -> None:
        """Test modified decision with corrected intent."""
        decision = ApprovalDecision(
            status=ApprovalStatus.MODIFIED,
            feedback="Changed to refactor",
            modified_intent="refactor",
        )
        
        assert decision.status == ApprovalStatus.MODIFIED
        assert decision.modified_intent == "refactor"


class TestDoRApprovalGate:
    """Tests for DoRApprovalGate."""

    @pytest.fixture
    def mock_router_instance(self) -> Mock:
        """Create mock router instance."""
        router = Mock()
        router.classify_intent.return_value = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="BuilderOrchestrator",
            confidence_score=0.85,
            reasoning="Detected implementation intent",
        )
        router.execute_orchestrated.return_value = Mock(
            is_ok=Mock(return_value=True),
            value={"result": "success"},
        )
        return router

    @pytest.fixture
    def mock_factory(self, mock_router_instance: Mock) -> Mock:
        """Create mock factory."""
        factory = Mock()
        factory.create_router.return_value = mock_router_instance
        return factory

    def test_classify_and_reflect(self, mock_factory: Mock) -> None:
        """Test classify_and_reflect generates reflection."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            reflection = gate.classify_and_reflect(
                text="Implement new feature",
                context={"domain": "features"},
            )
            
            assert isinstance(reflection, IntentReflection)
            assert reflection.intent_type == "implement"
            assert reflection.target_handler == "BuilderOrchestrator"
            assert reflection.confidence == 0.85

    def test_classify_empty_text_raises(self) -> None:
        """Test that empty text raises ValueError."""
        gate = DoRApprovalGate()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            gate.classify_and_reflect(text="", context={})

    def test_is_pending_after_classify(self, mock_factory: Mock) -> None:
        """Test is_pending is True after classification."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            
            assert gate.is_pending is True
            assert gate.is_approved is False

    def test_approve_sets_approved(self, mock_factory: Mock) -> None:
        """Test approve() sets approval status."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            gate.approve(feedback="LGTM")
            
            assert gate.is_approved is True
            assert gate.is_pending is False

    def test_reject_sets_rejected(self, mock_factory: Mock) -> None:
        """Test reject() sets rejection status."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            gate.reject(reason="Wrong intent")
            
            assert gate.is_approved is False
            assert gate.is_pending is False

    def test_modify_allows_execution(self, mock_factory: Mock) -> None:
        """Test modify() allows execution."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            gate.modify(corrected_intent="fix")
            
            assert gate.is_approved is True

    def test_execute_without_approval_raises(self, mock_factory: Mock) -> None:
        """Test execute_if_approved raises without approval."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            
            with pytest.raises(RuntimeError, match="approval required"):
                gate.execute_if_approved()

    def test_approve_without_classification_raises(self) -> None:
        """Test approve() without classification raises."""
        gate = DoRApprovalGate()
        
        with pytest.raises(RuntimeError, match="No pending classification"):
            gate.approve()

    def test_get_reflection_markdown(self, mock_factory: Mock) -> None:
        """Test get_reflection_markdown returns markdown."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            
            md = gate.get_reflection_markdown()
            
            assert "### 📋 Intent Classification" in md
            assert "Awaiting approval" in md

    def test_reset_clears_state(self, mock_factory: Mock) -> None:
        """Test reset() clears all state."""
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            gate = DoRApprovalGate()
            gate.classify_and_reflect(text="Test", context={})
            gate.approve()
            gate.reset()
            
            assert gate.is_pending is False
            assert gate.is_approved is False
            assert gate.get_reflection_markdown() == ""


class TestReflectIntentFunction:
    """Tests for reflect_intent convenience function."""

    def test_reflect_intent_returns_markdown(self) -> None:
        """Test reflect_intent returns markdown string."""
        mock_router = Mock()
        mock_router.classify_intent.return_value = RoutingDecision(
            intent_type=IntentType.FIX,
            target_handler="FixOrchestrator",
            confidence_score=0.75,
            reasoning="Fix detected",
        )
        
        mock_factory = Mock()
        mock_factory.create_router.return_value = mock_router
        
        with patch(
            "cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory",
            return_value=mock_factory,
        ):
            md = reflect_intent("Fix the bug", {"domain": "core"})
            
            assert "### 📋 Intent Classification" in md
            assert "`fix`" in md
