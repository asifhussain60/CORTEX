"""
TDD tests for event models - Phase 0 Foundation.

Tests for: OrchestratorEvent, EventType enum, EventPayload with correlation IDs
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD - tests BEFORE code), CORE-011 (type hints), CORE-012 (docstrings)
"""

import unittest
from datetime import datetime
from uuid import UUID


class TestEventTypeEnum(unittest.TestCase):
    """Tests for EventType enumeration."""
    
    def test_event_type_has_expected_values(self) -> None:
        """Verify EventType has all orchestrator communication events."""
        from cortex.models.event_models import EventType
        
        expected = {
            "REQUEST_RECEIVED",
            "INTENT_CLASSIFIED",
            "PLANNING_REQUIRED",
            "PLAN_GENERATED",
            "PLAN_APPROVED",
            "PHASE_STARTED",
            "PHASE_COMPLETE",
            "PHASE_REVIEW_COMPLETE",
            "IMPLEMENTATION_COMPLETE",
            "FINAL_REVIEW_COMPLETE",
            "GATE_DECISION_MADE",
            "ERROR_OCCURRED"
        }
        actual = {e.name for e in EventType}
        self.assertEqual(actual, expected)
    
    def test_event_type_is_string_enum(self) -> None:
        """Verify EventType values are JSON-serializable strings."""
        from cortex.models.event_models import EventType
        
        self.assertEqual(EventType.REQUEST_RECEIVED.value, "REQUEST_RECEIVED")
        self.assertIsInstance(EventType.PLAN_APPROVED.value, str)


class TestOrchestratorEventModel(unittest.TestCase):
    """Tests for OrchestratorEvent data model."""
    
    def test_orchestrator_event_creation(self) -> None:
        """Verify OrchestratorEvent captures orchestrator communication."""
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        event = OrchestratorEvent(
            event_type=EventType.INTENT_CLASSIFIED,
            source_orchestrator="IntentRouter",
            target_orchestrator="PlanningOrchestrator",
            payload={"intent": "IMPLEMENT", "confidence": 0.95},
            correlation_id="task-123"
        )
        
        self.assertEqual(event.event_type, EventType.INTENT_CLASSIFIED)
        self.assertEqual(event.source_orchestrator, "IntentRouter")
        self.assertEqual(event.payload["intent"], "IMPLEMENT")
        self.assertEqual(event.correlation_id, "task-123")
    
    def test_orchestrator_event_has_uuid(self) -> None:
        """Verify OrchestratorEvent auto-generates event_id."""
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        event = OrchestratorEvent(
            event_type=EventType.REQUEST_RECEIVED,
            source_orchestrator="MasterOrchestrator",
            payload={"request": "implement feature"}
        )
        
        self.assertIsNotNone(event.event_id)
        # Should be a valid UUID string
        UUID(event.event_id)  # Will raise if invalid
    
    def test_orchestrator_event_has_timestamp(self) -> None:
        """Verify OrchestratorEvent auto-generates timestamp."""
        from cortex.models.event_models import OrchestratorEvent, EventType
        
        before = datetime.now()
        event = OrchestratorEvent(
            event_type=EventType.PHASE_STARTED,
            source_orchestrator="WorkflowOrchestrator",
            payload={"phase": 1}
        )
        after = datetime.now()
        
        self.assertIsNotNone(event.timestamp)
        self.assertGreaterEqual(event.timestamp, before)
        self.assertLessEqual(event.timestamp, after)


class TestEventChainModel(unittest.TestCase):
    """Tests for EventChain (linked event sequence)."""
    
    def test_event_chain_creation(self) -> None:
        """Verify EventChain can track related events."""
        from cortex.models.event_models import EventChain
        
        chain = EventChain(
            correlation_id="task-456",
            event_ids=["evt-1", "evt-2", "evt-3"],
            started_at=datetime.now(),
            completed=False
        )
        
        self.assertEqual(chain.correlation_id, "task-456")
        self.assertEqual(len(chain.event_ids), 3)
        self.assertFalse(chain.completed)
    
    def test_event_chain_completion(self) -> None:
        """Verify EventChain can mark completion with timestamp."""
        from cortex.models.event_models import EventChain
        
        now = datetime.now()
        chain = EventChain(
            correlation_id="task-789",
            event_ids=["evt-a", "evt-b"],
            started_at=now,
            completed=True,
            completed_at=now
        )
        
        self.assertTrue(chain.completed)
        self.assertIsNotNone(chain.completed_at)


class TestEventSubscriptionModel(unittest.TestCase):
    """Tests for EventSubscription (pub/sub pattern)."""
    
    def test_event_subscription_creation(self) -> None:
        """Verify EventSubscription defines what orchestrator listens to."""
        from cortex.models.event_models import EventSubscription, EventType
        
        subscription = EventSubscription(
            subscriber_id="PlanningOrchestrator",
            event_types=[EventType.INTENT_CLASSIFIED, EventType.REQUEST_RECEIVED],
            filter_source=None  # Listen to all sources
        )
        
        self.assertEqual(subscription.subscriber_id, "PlanningOrchestrator")
        self.assertEqual(len(subscription.event_types), 2)
        self.assertIsNone(subscription.filter_source)
    
    def test_event_subscription_with_source_filter(self) -> None:
        """Verify EventSubscription can filter by source orchestrator."""
        from cortex.models.event_models import EventSubscription, EventType
        
        subscription = EventSubscription(
            subscriber_id="ReviewOrchestrator",
            event_types=[EventType.PHASE_COMPLETE],
            filter_source="WorkflowOrchestrator"
        )
        
        self.assertEqual(subscription.filter_source, "WorkflowOrchestrator")


class TestEventPayloadPatterns(unittest.TestCase):
    """Tests for common event payload patterns."""
    
    def test_intent_classified_payload(self) -> None:
        """Verify payload structure for INTENT_CLASSIFIED events."""
        from cortex.models.event_models import IntentClassifiedPayload
        
        payload = IntentClassifiedPayload(
            intent="IMPLEMENT",
            confidence=0.92,
            complexity="MODERATE",
            suggested_orchestrator="PlanningOrchestrator"
        )
        
        self.assertEqual(payload.intent, "IMPLEMENT")
        self.assertEqual(payload.confidence, 0.92)
        self.assertEqual(payload.complexity, "MODERATE")
    
    def test_phase_complete_payload(self) -> None:
        """Verify payload structure for PHASE_COMPLETE events."""
        from cortex.models.event_models import PhaseCompletePayload
        
        payload = PhaseCompletePayload(
            phase_id="phase_1",
            success=True,
            artifacts_created=["file1.py", "test_file1.py"],
            duration_seconds=120.5
        )
        
        self.assertTrue(payload.success)
        self.assertEqual(len(payload.artifacts_created), 2)
        self.assertEqual(payload.duration_seconds, 120.5)


if __name__ == "__main__":
    unittest.main()
