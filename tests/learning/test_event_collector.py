"""
TDD Tests for LearningEventCollector

Tests MUST fail initially (RED phase) before implementation.

Test Coverage:
- Event capture (basic, thread-safe, performance)
- Event filtering (milestone, category, component, time-based)
- 18 must-have event types
- Performance guarantees (<10ms overhead)
- Global collector singleton
- Statistics and distribution

Author: Asif Hussain
Version: 1.0.0 (Phase 1 - RED phase)
"""

import pytest
import threading
import time
from datetime import datetime, timedelta
from typing import List

from src.learning.event_collector import (
    LearningEventCollector,
    get_global_collector,
    reset_global_collector,
)
from src.learning.event_taxonomy import (
    LearningEvent,
    EventType,
    EventCategory,
    EventTier,
    get_must_have_events,
)


class TestEventCollectorBasics:
    """Test basic event capture and retrieval."""
    
    def test_collector_initialization(self):
        """Test collector initializes correctly."""
        collector = LearningEventCollector()
        assert collector.enabled is True
        assert collector.get_event_count() == 0
        assert collector.get_milestone_count() == 0
    
    def test_collector_can_be_disabled(self):
        """Test collector can be disabled."""
        collector = LearningEventCollector(enabled=False)
        assert collector.enabled is False
        
        event = LearningEvent(
            event_type=EventType.PLAN_APPROVED,
            component="TestComponent",
            metadata={"test": "data"}
        )
        
        result = collector.capture_event(event)
        assert result is False
        assert collector.get_event_count() == 0
    
    def test_capture_single_event(self):
        """Test capturing a single event."""
        collector = LearningEventCollector()
        
        event = LearningEvent(
            event_type=EventType.PLAN_APPROVED,
            component="PlanningOrchestrator",
            metadata={"plan_id": "test-123", "phases": 4}
        )
        
        result = collector.capture_event(event)
        assert result is True
        assert collector.get_event_count() == 1
        
        events = collector.get_all_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.PLAN_APPROVED
        assert events[0].component == "PlanningOrchestrator"
        assert events[0].metadata["plan_id"] == "test-123"
    
    def test_capture_multiple_events(self):
        """Test capturing multiple events."""
        collector = LearningEventCollector()
        
        events_to_capture = [
            LearningEvent(EventType.PLAN_APPROVED, "PlanningOrchestrator"),
            LearningEvent(EventType.PHASE_COMPLETED, "PlanExecutionOrchestrator"),
            LearningEvent(EventType.CHECKPOINT_COMMITTED, "GitCheckpointOrchestrator"),
        ]
        
        for event in events_to_capture:
            collector.capture_event(event)
        
        assert collector.get_event_count() == 3
        retrieved = collector.get_all_events()
        assert len(retrieved) == 3
    
    def test_clear_events(self):
        """Test clearing all events."""
        collector = LearningEventCollector()
        
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "Test"))
        
        assert collector.get_event_count() == 2
        
        collector.clear_events()
        
        assert collector.get_event_count() == 0
        assert len(collector.get_all_events()) == 0


class TestEventFiltering:
    """Test event filtering by various criteria."""
    
    def test_get_milestone_events(self):
        """Test filtering milestone events only."""
        collector = LearningEventCollector()
        
        # Milestones
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "Test"))
        
        # Non-milestones
        collector.capture_event(LearningEvent(EventType.PLAN_CREATED, "Test"))
        collector.capture_event(LearningEvent(EventType.PHASE_STARTED, "Test"))
        
        milestones = collector.get_milestone_events()
        assert len(milestones) == 2
        assert all(e.is_milestone() for e in milestones)
    
    def test_get_events_by_type(self):
        """Test filtering by event type."""
        collector = LearningEventCollector()
        
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test1"))
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test2"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "Test3"))
        
        approved_events = collector.get_events_by_type(EventType.PLAN_APPROVED)
        assert len(approved_events) == 2
        assert all(e.event_type == EventType.PLAN_APPROVED for e in approved_events)
    
    def test_get_events_by_category(self):
        """Test filtering by learning category."""
        collector = LearningEventCollector()
        
        # Milestones category
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "Test"))
        
        # ADO workflows category
        collector.capture_event(LearningEvent(EventType.ADO_STORY_CREATED, "Test"))
        
        milestone_events = collector.get_events_by_category(EventCategory.MILESTONES)
        assert len(milestone_events) == 2
        
        ado_events = collector.get_events_by_category(EventCategory.ADO_WORKFLOWS)
        assert len(ado_events) == 1
    
    def test_get_events_by_component(self):
        """Test filtering by source component."""
        collector = LearningEventCollector()
        
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "PlanningOrchestrator"))
        collector.capture_event(LearningEvent(EventType.PLAN_CREATED, "PlanningOrchestrator"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "PlanExecutionOrchestrator"))
        
        planning_events = collector.get_events_by_component("PlanningOrchestrator")
        assert len(planning_events) == 2
        assert all(e.component == "PlanningOrchestrator" for e in planning_events)
    
    def test_get_events_since(self):
        """Test filtering by timestamp."""
        collector = LearningEventCollector()
        
        past = datetime.now() - timedelta(hours=2)
        recent = datetime.now()
        
        # Create events with explicit timestamps
        old_event = LearningEvent(EventType.PLAN_APPROVED, "Test")
        old_event.timestamp = past
        
        new_event = LearningEvent(EventType.PHASE_COMPLETED, "Test")
        new_event.timestamp = recent
        
        collector.capture_event(old_event)
        collector.capture_event(new_event)
        
        cutoff = datetime.now() - timedelta(hours=1)
        recent_events = collector.get_events_since(cutoff)
        
        assert len(recent_events) == 1
        assert recent_events[0].event_type == EventType.PHASE_COMPLETED
    
    def test_get_recent_events(self):
        """Test getting events from last N hours."""
        collector = LearningEventCollector()
        
        # Event from 25 hours ago
        old_event = LearningEvent(EventType.PLAN_APPROVED, "Test")
        old_event.timestamp = datetime.now() - timedelta(hours=25)
        
        # Event from 1 hour ago
        recent_event = LearningEvent(EventType.PHASE_COMPLETED, "Test")
        recent_event.timestamp = datetime.now() - timedelta(hours=1)
        
        collector.capture_event(old_event)
        collector.capture_event(recent_event)
        
        last_24h = collector.get_recent_events(hours=24)
        
        assert len(last_24h) == 1
        assert last_24h[0].event_type == EventType.PHASE_COMPLETED


class TestMustHaveEvents:
    """Test all 18 must-have event types."""
    
    def test_planning_events(self):
        """Test 6 planning & execution events."""
        collector = LearningEventCollector()
        
        planning_events = [
            EventType.PLAN_CREATED,
            EventType.PLAN_APPROVED,
            EventType.PLAN_ABANDONED,
            EventType.PHASE_STARTED,
            EventType.PHASE_COMPLETED,
            EventType.CHECKPOINT_COMMITTED,
        ]
        
        for event_type in planning_events:
            event = LearningEvent(event_type, "TestComponent")
            collector.capture_event(event)
        
        assert collector.get_event_count() == 6
        
        # Verify milestone detection
        milestones = collector.get_milestone_events()
        assert len(milestones) == 3  # APPROVED, COMPLETED, COMMITTED
    
    def test_ado_events(self):
        """Test 4 ADO work management events."""
        collector = LearningEventCollector()
        
        ado_events = [
            EventType.ADO_STORY_CREATED,
            EventType.ADO_FEATURE_CREATED,
            EventType.ADO_WORK_ITEM_COMPLETED,
            EventType.ADO_ACCEPTANCE_CRITERIA_VALIDATED,
        ]
        
        for event_type in ado_events:
            event = LearningEvent(event_type, "ADOUtility")
            collector.capture_event(event)
        
        assert collector.get_event_count() == 4
        
        # All ADO events in same category
        ado_category = collector.get_events_by_category(EventCategory.ADO_WORKFLOWS)
        assert len(ado_category) == 4
    
    def test_routing_events(self):
        """Test 3 workflow routing events."""
        collector = LearningEventCollector()
        
        routing_events = [
            EventType.WORKFLOW_STARTED,
            EventType.OPERATION_ROUTED,
            EventType.WORKFLOW_COMPLETED,
        ]
        
        for event_type in routing_events:
            event = LearningEvent(event_type, "UnifiedEntryPointOrchestrator")
            collector.capture_event(event)
        
        assert collector.get_event_count() == 3
        
        # WORKFLOW_COMPLETED is milestone
        milestones = collector.get_milestone_events()
        assert len(milestones) == 1
    
    def test_planning_strategy_events(self):
        """Test 6 planning strategy events."""
        collector = LearningEventCollector()
        
        strategy_events = [
            EventType.PLANNING_REQUEST,
            EventType.PLAN_STRATEGY_SELECTED,
            EventType.PLAN_VALIDATED,
            EventType.INTERACTIVE_PLANNING_STARTED,
            EventType.CLARIFICATION_REQUESTED,
            EventType.REQUIREMENTS_FINALIZED,
        ]
        
        for event_type in strategy_events:
            event = LearningEvent(event_type, "WorkPlanner")
            collector.capture_event(event)
        
        assert collector.get_event_count() == 6
        
        # Check category
        strategy_category = collector.get_events_by_category(EventCategory.PLANNING_STRATEGIES)
        assert len(strategy_category) == 6
    
    def test_all_18_must_have_events(self):
        """Test all 19 must-have events captured correctly."""
        collector = LearningEventCollector()
        
        must_have = get_must_have_events()
        assert len(must_have) == 19  # Updated: 6 planning strategy events (not 5)
        
        for event_type in must_have:
            event = LearningEvent(event_type, "TestComponent")
            result = collector.capture_event(event)
            assert result is True
        
        assert collector.get_event_count() == 19


class TestThreadSafety:
    """Test thread-safe operations."""
    
    def test_concurrent_event_capture(self):
        """Test capturing events from multiple threads."""
        collector = LearningEventCollector()
        event_count = 100
        thread_count = 10
        
        def capture_events():
            for i in range(event_count // thread_count):
                event = LearningEvent(EventType.PLAN_APPROVED, f"Thread-{threading.current_thread().name}")
                collector.capture_event(event)
        
        threads = [threading.Thread(target=capture_events) for _ in range(thread_count)]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert collector.get_event_count() == event_count
    
    def test_concurrent_read_write(self):
        """Test concurrent reads and writes."""
        collector = LearningEventCollector()
        
        def writer():
            for i in range(50):
                event = LearningEvent(EventType.PHASE_COMPLETED, "Writer")
                collector.capture_event(event)
                time.sleep(0.001)  # Small delay
        
        def reader():
            for i in range(50):
                events = collector.get_all_events()
                milestones = collector.get_milestone_events()
                time.sleep(0.001)
        
        write_thread = threading.Thread(target=writer)
        read_threads = [threading.Thread(target=reader) for _ in range(3)]
        
        write_thread.start()
        for thread in read_threads:
            thread.start()
        
        write_thread.join()
        for thread in read_threads:
            thread.join()
        
        assert collector.get_event_count() == 50


class TestPerformance:
    """Test performance guarantees (<10ms overhead)."""
    
    def test_single_event_capture_performance(self):
        """Test single event capture is <10ms."""
        collector = LearningEventCollector()
        
        event = LearningEvent(EventType.PLAN_APPROVED, "Test")
        
        start = time.perf_counter()
        collector.capture_event(event)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert elapsed_ms < 10.0, f"Event capture took {elapsed_ms:.2f}ms (target <10ms)"
    
    def test_bulk_event_capture_performance(self):
        """Test bulk event capture maintains <10ms average."""
        collector = LearningEventCollector()
        
        for i in range(100):
            event = LearningEvent(EventType.PLAN_APPROVED, f"Test-{i}")
            collector.capture_event(event)
        
        stats = collector.get_performance_stats()
        
        assert stats["total_events"] == 100
        assert stats["avg_capture_time_ms"] < 10.0
        assert stats["overhead_target_met"] is True
    
    def test_milestone_filtering_performance(self):
        """Test milestone filtering is fast."""
        collector = LearningEventCollector()
        
        # Create mix of milestone and non-milestone events
        for i in range(50):
            collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
            collector.capture_event(LearningEvent(EventType.PLAN_CREATED, "Test"))
        
        start = time.perf_counter()
        milestones = collector.get_milestone_events()
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert len(milestones) == 50
        assert elapsed_ms < 10.0


class TestGlobalCollector:
    """Test global collector singleton."""
    
    def test_global_collector_singleton(self):
        """Test global collector returns same instance."""
        reset_global_collector()
        
        collector1 = get_global_collector()
        collector2 = get_global_collector()
        
        assert collector1 is collector2
    
    def test_global_collector_persistence(self):
        """Test global collector persists events."""
        reset_global_collector()
        
        collector = get_global_collector()
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        
        # Get collector again
        collector2 = get_global_collector()
        assert collector2.get_event_count() == 1
    
    def test_global_collector_reset(self):
        """Test global collector can be reset."""
        reset_global_collector()
        
        collector1 = get_global_collector()
        collector1.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        
        reset_global_collector()
        
        collector2 = get_global_collector()
        assert collector2.get_event_count() == 0


class TestStatistics:
    """Test statistics and distribution methods."""
    
    def test_performance_stats(self):
        """Test performance statistics calculation."""
        collector = LearningEventCollector()
        
        for i in range(10):
            collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        
        stats = collector.get_performance_stats()
        
        assert stats["total_events"] == 10
        assert "avg_capture_time_ms" in stats
        assert "max_capture_time_ms" in stats
        assert "overhead_target_met" in stats
    
    def test_category_distribution(self):
        """Test category distribution calculation."""
        collector = LearningEventCollector()
        
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "Test"))
        collector.capture_event(LearningEvent(EventType.ADO_STORY_CREATED, "Test"))
        collector.capture_event(LearningEvent(EventType.ADO_FEATURE_CREATED, "Test"))
        
        distribution = collector.get_category_distribution()
        
        assert distribution[EventCategory.MILESTONES.value] == 2
        assert distribution[EventCategory.ADO_WORKFLOWS.value] == 2
    
    def test_component_distribution(self):
        """Test component distribution calculation."""
        collector = LearningEventCollector()
        
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "PlanningOrchestrator"))
        collector.capture_event(LearningEvent(EventType.PLAN_CREATED, "PlanningOrchestrator"))
        collector.capture_event(LearningEvent(EventType.PHASE_COMPLETED, "PlanExecutionOrchestrator"))
        
        distribution = collector.get_component_distribution()
        
        assert distribution["PlanningOrchestrator"] == 2
        assert distribution["PlanExecutionOrchestrator"] == 1


class TestEventSerialization:
    """Test event serialization to/from dict."""
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = LearningEvent(
            event_type=EventType.PLAN_APPROVED,
            component="PlanningOrchestrator",
            metadata={"plan_id": "test-123"},
            session_id="session-456",
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "plan_approved"
        assert event_dict["component"] == "PlanningOrchestrator"
        assert event_dict["metadata"]["plan_id"] == "test-123"
        assert event_dict["session_id"] == "session-456"
        assert "timestamp" in event_dict
        assert "category" in event_dict
        assert "tier" in event_dict
    
    def test_event_from_dict(self):
        """Test reconstructing event from dictionary."""
        original = LearningEvent(
            event_type=EventType.PHASE_COMPLETED,
            component="PlanExecutionOrchestrator",
            metadata={"phase": "Phase 1"},
        )
        
        event_dict = original.to_dict()
        reconstructed = LearningEvent.from_dict(event_dict)
        
        assert reconstructed.event_type == original.event_type
        assert reconstructed.component == original.component
        assert reconstructed.metadata == original.metadata
    
    def test_event_roundtrip(self):
        """Test full serialization roundtrip."""
        original = LearningEvent(
            event_type=EventType.ADO_STORY_CREATED,
            component="ADOUtility",
            metadata={"story_id": "US-789", "title": "Test Story"},
            session_id="test-session",
            user_context={"user": "test_user"},
        )
        
        # Roundtrip: event -> dict -> event
        event_dict = original.to_dict()
        reconstructed = LearningEvent.from_dict(event_dict)
        
        assert reconstructed.event_type == original.event_type
        assert reconstructed.component == original.component
        assert reconstructed.metadata == original.metadata
        assert reconstructed.session_id == original.session_id
        assert reconstructed.user_context == original.user_context


class TestMustHaveFiltering:
    """Test must-have event filtering in Phase 1."""
    
    def test_filters_should_have_events_when_enabled(self):
        """Test that should-have events are filtered out in Phase 1."""
        collector = LearningEventCollector(filter_must_have_only=True)
        
        # Try to capture should-have event
        should_have_event = LearningEvent(
            event_type=EventType.HEALTH_SCAN_STARTED,  # Tier 2 event
            component="HealthScanner"
        )
        
        result = collector.capture_event(should_have_event)
        assert result is False
        assert collector.get_event_count() == 0
    
    def test_allows_must_have_events(self):
        """Test that must-have events are captured in Phase 1."""
        collector = LearningEventCollector(filter_must_have_only=True)
        
        must_have_event = LearningEvent(
            event_type=EventType.PLAN_APPROVED,  # Tier 1 event
            component="PlanningOrchestrator"
        )
        
        result = collector.capture_event(must_have_event)
        assert result is True
        assert collector.get_event_count() == 1
    
    def test_captures_all_events_when_filtering_disabled(self):
        """Test that all events are captured when filter is disabled."""
        collector = LearningEventCollector(filter_must_have_only=False)
        
        # Capture both tiers
        collector.capture_event(LearningEvent(EventType.PLAN_APPROVED, "Test"))
        collector.capture_event(LearningEvent(EventType.HEALTH_SCAN_STARTED, "Test"))
        
        assert collector.get_event_count() == 2
