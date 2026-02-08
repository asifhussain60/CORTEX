"""
Unit tests for Phase 45 Stage 2: Plan-specific event models.

Tests the new EventType enums and event payloads for plan lifecycle
management via OrchestratorEventBus.

AC-ID: AC-PLAN-SYSTEM-STAGE2-001
Authority: phase-45-enhanced-planning-system.yaml § Stage 2
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from datetime import datetime
from uuid import uuid4

import pytest

from cortex.models.event_models import (
    EventType,
    OrchestratorEvent,
    PlanIntentDetectedPayload,
    PlanCreatedPayload,
    PlanEnrichedPayload,
    PlanStateChangedPayload,
    PlanArchivedPayload,
)


class TestPlanEventTypes:
    """Test plan-specific EventType enums."""

    def test_plan_intent_detected_event_type_exists(self) -> None:
        """Plan intent detection event type should exist."""
        assert hasattr(EventType, "PLAN_INTENT_DETECTED")
        assert EventType.PLAN_INTENT_DETECTED == "PLAN_INTENT_DETECTED"

    def test_plan_created_event_type_exists(self) -> None:
        """Plan created event type should exist."""
        assert hasattr(EventType, "PLAN_CREATED")
        assert EventType.PLAN_CREATED == "PLAN_CREATED"

    def test_plan_enriched_event_type_exists(self) -> None:
        """Plan enriched event type should exist."""
        assert hasattr(EventType, "PLAN_ENRICHED")
        assert EventType.PLAN_ENRICHED == "PLAN_ENRICHED"

    def test_plan_state_changed_event_type_exists(self) -> None:
        """Plan state changed event type should exist."""
        assert hasattr(EventType, "PLAN_STATE_CHANGED")
        assert EventType.PLAN_STATE_CHANGED == "PLAN_STATE_CHANGED"

    def test_plan_archived_event_type_exists(self) -> None:
        """Plan archived event type should exist."""
        assert hasattr(EventType, "PLAN_ARCHIVED")
        assert EventType.PLAN_ARCHIVED == "PLAN_ARCHIVED"


class TestPlanIntentDetectedPayload:
    """Test PLAN_INTENT_DETECTED payload."""

    def test_create_basic_payload(self) -> None:
        """Should create payload with required fields."""
        payload = PlanIntentDetectedPayload(
            plan_id="plan-123",
            user_context="Implement phase 45",
            detected_type="IMPLEMENT",
            confidence=0.95,
        )
        
        assert payload.plan_id == "plan-123"
        assert payload.user_context == "Implement phase 45"
        assert payload.detected_type == "IMPLEMENT"
        assert payload.confidence == 0.95

    def test_payload_with_defaults(self) -> None:
        """Should handle optional fields with defaults."""
        payload = PlanIntentDetectedPayload()
        
        assert payload.plan_id is None
        assert payload.user_context == ""
        assert payload.detected_type == ""
        assert payload.confidence == 0.0

    def test_payload_serialization(self) -> None:
        """Should convert to dict for EventBus."""
        payload = PlanIntentDetectedPayload(
            plan_id="plan-456",
            detected_type="FIX",
            confidence=0.85,
        )
        
        payload_dict = payload.__dict__
        assert isinstance(payload_dict, dict)
        assert payload_dict["plan_id"] == "plan-456"
        assert payload_dict["detected_type"] == "FIX"


class TestPlanCreatedPayload:
    """Test PLAN_CREATED payload."""

    def test_create_with_all_fields(self) -> None:
        """Should create payload with all fields."""
        created_at = datetime.now()
        payload = PlanCreatedPayload(
            plan_id="plan-789",
            title="Feature Implementation Plan",
            status="approved",
            created_at=created_at,
        )
        
        assert payload.plan_id == "plan-789"
        assert payload.title == "Feature Implementation Plan"
        assert payload.status == "approved"
        assert payload.created_at == created_at

    def test_create_with_defaults(self) -> None:
        """Should use default status if not provided."""
        payload = PlanCreatedPayload(
            plan_id="plan-abc",
            title="Test Plan",
        )
        
        assert payload.status == "pending"
        assert payload.created_at is None


class TestPlanEnrichedPayload:
    """Test PLAN_ENRICHED payload."""

    def test_create_enrichment_payload(self) -> None:
        """Should create enrichment payload with sources."""
        payload = PlanEnrichedPayload(
            plan_id="plan-def",
            enrichment_sources=["GitLensEnricher", "CodeLensEnricher"],
            enrichment_data={"affected_files": ["file1.py", "file2.py"]},
            quality_score=0.87,
        )
        
        assert payload.plan_id == "plan-def"
        assert len(payload.enrichment_sources) == 2
        assert payload.enrichment_data["affected_files"] == ["file1.py", "file2.py"]
        assert payload.quality_score == 0.87

    def test_create_with_empty_enrichment(self) -> None:
        """Should handle empty enrichment (Stage 2 interim)."""
        payload = PlanEnrichedPayload(plan_id="plan-ghi")
        
        assert payload.plan_id == "plan-ghi"
        assert payload.enrichment_sources == []
        assert payload.enrichment_data == {}
        assert payload.quality_score == 0.0


class TestPlanStateChangedPayload:
    """Test PLAN_STATE_CHANGED payload."""

    def test_create_state_change_payload(self) -> None:
        """Should create state change payload."""
        changed_at = datetime.now()
        payload = PlanStateChangedPayload(
            plan_id="plan-jkl",
            old_status="pending",
            new_status="in_progress",
            reason="User approved plan",
            changed_at=changed_at,
        )
        
        assert payload.plan_id == "plan-jkl"
        assert payload.old_status == "pending"
        assert payload.new_status == "in_progress"
        assert payload.reason == "User approved plan"
        assert payload.changed_at == changed_at

    def test_state_change_with_defaults(self) -> None:
        """Should handle default reason."""
        payload = PlanStateChangedPayload(
            plan_id="plan-mno",
            old_status="approved",
            new_status="completed",
        )
        
        assert payload.reason == ""
        assert payload.changed_at is None


class TestPlanArchivedPayload:
    """Test PLAN_ARCHIVED payload."""

    def test_create_archive_payload(self) -> None:
        """Should create archive payload."""
        archived_at = datetime.now()
        payload = PlanArchivedPayload(
            plan_id="plan-pqr",
            archive_path="cortex-registry/planning/completed/2026/plan-pqr",
            completion_status="completed",
            archived_at=archived_at,
        )
        
        assert payload.plan_id == "plan-pqr"
        assert "2026" in payload.archive_path
        assert payload.completion_status == "completed"
        assert payload.archived_at == archived_at

    def test_archive_with_different_statuses(self) -> None:
        """Should support different completion statuses."""
        for status in ["completed", "cancelled", "deferred"]:
            payload = PlanArchivedPayload(
                plan_id="plan-stu",
                archive_path="/path/to/archive",
                completion_status=status,
            )
            assert payload.completion_status == status


class TestOrchestratorEventWithPlanPayloads:
    """Test OrchestratorEvent with plan payloads."""

    def test_plan_created_event(self) -> None:
        """Should create PLAN_CREATED event."""
        payload = PlanCreatedPayload(
            plan_id="plan-vwx",
            title="Test Plan",
            status="approved",
        )
        
        event = OrchestratorEvent(
            event_type=EventType.PLAN_CREATED,
            source_orchestrator="PlanOrchestrator",
            payload=payload.__dict__,
        )
        
        assert event.event_type == EventType.PLAN_CREATED
        assert event.source_orchestrator == "PlanOrchestrator"
        assert event.payload["plan_id"] == "plan-vwx"

    def test_plan_state_changed_event_with_correlation_id(self) -> None:
        """Should track correlation ID for event chains."""
        correlation_id = str(uuid4())
        payload = PlanStateChangedPayload(
            plan_id="plan-yz",
            old_status="pending",
            new_status="approved",
        )
        
        event = OrchestratorEvent(
            event_type=EventType.PLAN_STATE_CHANGED,
            source_orchestrator="PlanOrchestrator",
            payload=payload.__dict__,
            correlation_id=correlation_id,
        )
        
        assert event.correlation_id == correlation_id
        assert event.event_type == EventType.PLAN_STATE_CHANGED

    def test_plan_enriched_event_broadcast(self) -> None:
        """PLAN_ENRICHED should be broadcast (no target)."""
        payload = PlanEnrichedPayload(
            plan_id="plan-abc",
            enrichment_sources=["TestEnricher"],
            quality_score=0.90,
        )
        
        event = OrchestratorEvent(
            event_type=EventType.PLAN_ENRICHED,
            source_orchestrator="EnhancedPlanningOrchestrator",
            payload=payload.__dict__,
            target_orchestrator=None,  # Broadcast
        )
        
        assert event.target_orchestrator is None
        assert event.source_orchestrator == "EnhancedPlanningOrchestrator"


class TestEventPayloadIntegration:
    """Integration tests for event payloads."""

    def test_plan_lifecycle_event_sequence(self) -> None:
        """Should create consistent event sequence for plan lifecycle."""
        plan_id = "plan-lifecycle-001"
        correlation_id = str(uuid4())
        
        # Event 1: Plan created
        created_payload = PlanCreatedPayload(
            plan_id=plan_id,
            title="Lifecycle Test Plan",
            status="pending",
        )
        created_event = OrchestratorEvent(
            event_type=EventType.PLAN_CREATED,
            source_orchestrator="PlanOrchestrator",
            payload=created_payload.__dict__,
            correlation_id=correlation_id,
        )
        
        assert created_event.payload["plan_id"] == plan_id
        
        # Event 2: Plan enriched
        enriched_payload = PlanEnrichedPayload(
            plan_id=plan_id,
            enrichment_sources=["Source1"],
            quality_score=0.75,
        )
        enriched_event = OrchestratorEvent(
            event_type=EventType.PLAN_ENRICHED,
            source_orchestrator="EnhancedPlanningOrchestrator",
            payload=enriched_payload.__dict__,
            correlation_id=correlation_id,
        )
        
        assert enriched_event.correlation_id == created_event.correlation_id
        
        # Event 3: Plan state changed
        state_payload = PlanStateChangedPayload(
            plan_id=plan_id,
            old_status="pending",
            new_status="in_progress",
        )
        state_event = OrchestratorEvent(
            event_type=EventType.PLAN_STATE_CHANGED,
            source_orchestrator="PlanOrchestrator",
            payload=state_payload.__dict__,
            correlation_id=correlation_id,
        )
        
        assert state_event.correlation_id == correlation_id
        
        # Verify all events linked by correlation_id
        events = [created_event, enriched_event, state_event]
        for event in events:
            assert event.correlation_id == correlation_id
