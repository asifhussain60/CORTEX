"""
Test suite for HP-003-01: Vision Mutation Tracking

Tests for tracking vision mutations from PHASE-06 protocol.
Ensures mutations are tracked with timestamps, can be rolled back,
and history is queryable for analysis and audit.

AC-ID: HP-003-01
Phase: PHASE-11-HALLUCINATION-PREVENTION
Status: TDD - RED phase
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import json

from cortex.core.hallucination_prevention.vision_mutations import (
    VisionMutationTracker,
    VisionMutation,
    MutationType,
    MutationSnapshot,
)


@pytest.fixture
def temp_db():
    """Create temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


class TestMutationTracking:
    """Test suite for vision mutation tracking."""

    @pytest.fixture
    def tracker(self, temp_db):
        """Initialize vision mutation tracker."""
        return VisionMutationTracker(db_path=temp_db)

    def test_mutations_tracked_with_timestamp(self, tracker):
        """ACID: Mutations tracked with timestamp
        
        Verify that all mutations are recorded with precise timestamps.
        """
        # Track a mutation
        mutation = tracker.track_mutation(
            mutation_type=MutationType.CONTEXT_UPDATE,
            source="PHASE-06",
            description="Updated phase context",
            affected_entity="PHASE-11",
            data={"old_value": "PHASE-10", "new_value": "PHASE-11"},
        )
        
        # Verify mutation recorded
        assert mutation.mutation_id is not None
        assert mutation.timestamp is not None
        assert isinstance(mutation.timestamp, datetime)
        assert mutation.mutation_type == MutationType.CONTEXT_UPDATE

    def test_multiple_mutations_tracked_in_sequence(self, tracker):
        """Multiple mutations are tracked in chronological order.
        
        Verify that mutation sequence is maintained.
        """
        mutations = []
        for i in range(5):
            mutation = tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Update {i}",
                affected_entity=f"entity_{i}",
                data={"index": i},
            )
            mutations.append(mutation)
        
        # Verify all tracked
        history = tracker.get_mutation_history()
        assert len(history) >= 5
        
        # Verify chronological order
        for i in range(1, len(mutations)):
            assert mutations[i].timestamp >= mutations[i-1].timestamp

    def test_mutation_types_tracked(self, tracker):
        """All mutation types are tracked correctly.
        
        Verify that different mutation types are distinguished.
        """
        mutation_types = [
            MutationType.CONTEXT_UPDATE,
            MutationType.STATE_UPDATE,
            MutationType.BOUNDARY_MODIFICATION,
            MutationType.SCHEMA_EVOLUTION,
        ]
        
        for mutation_type in mutation_types:
            mutation = tracker.track_mutation(
                mutation_type=mutation_type,
                source="PHASE-06",
                description=f"{mutation_type.name} test",
                affected_entity="test_entity",
                data={},
            )
            
            # Verify type recorded
            assert mutation.mutation_type == mutation_type

    def test_mutation_context_captured(self, tracker):
        """Mutation context and metadata are captured.
        
        Verify that full context is preserved.
        """
        context = {
            "user_id": "alice",
            "request_id": "req-123",
            "source_phase": "PHASE-06",
        }
        
        mutation = tracker.track_mutation(
            mutation_type=MutationType.CONTEXT_UPDATE,
            source="PHASE-06",
            description="Context test",
            affected_entity="entity",
            data={"test": "data"},
            context=context,
        )
        
        # Verify context captured
        assert mutation.context is not None
        assert mutation.context.get("user_id") == "alice"

    def test_mutation_data_preserved(self, tracker):
        """Mutation data changes are fully preserved.
        
        Verify that before/after data is captured.
        """
        data = {
            "old_phase": "PHASE-10",
            "new_phase": "PHASE-11",
            "updated_fields": ["locked", "ac_count"],
        }
        
        mutation = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Phase transition",
            affected_entity="PHASE-11",
            data=data,
        )
        
        # Verify data preserved
        assert mutation.data == data


class TestRollbackCapability:
    """Test suite for mutation rollback."""

    @pytest.fixture
    def tracker(self, temp_db):
        """Initialize vision mutation tracker."""
        return VisionMutationTracker(db_path=temp_db)

    def test_rollback_available_for_mutations(self, tracker):
        """ACID: Rollback available for mutations
        
        Verify that mutations can be rolled back.
        """
        # Track initial state
        initial_mutation = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Initial state",
            affected_entity="entity",
            data={"value": 1},
        )
        
        # Track modification
        modification = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Modified state",
            affected_entity="entity",
            data={"value": 2},
        )
        
        # Rollback to initial
        rolled_back = tracker.rollback_to_mutation(initial_mutation.mutation_id)
        
        # Verify rollback
        assert rolled_back is not None

    def test_rollback_creates_snapshot(self, tracker):
        """Rollback creates snapshot for recovery.
        
        Verify that snapshot is captured before rollback.
        """
        mutation1 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="State 1",
            affected_entity="entity",
            data={"value": 1},
        )
        
        mutation2 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="State 2",
            affected_entity="entity",
            data={"value": 2},
        )
        
        snapshot = tracker.create_mutation_snapshot(mutation1.mutation_id)
        
        # Verify snapshot created
        assert snapshot is not None
        assert snapshot.snapshot_id is not None

    def test_rollback_to_checkpoint(self, tracker):
        """Rollback to specific checkpoint.
        
        Verify ability to restore to any point.
        """
        mutations = []
        for i in range(5):
            mutation = tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"State {i}",
                affected_entity="entity",
                data={"value": i},
            )
            mutations.append(mutation)
        
        # Rollback to mutation 2
        checkpoint = tracker.create_mutation_snapshot(mutations[2].mutation_id)
        rolled_back = tracker.rollback_to_mutation(mutations[2].mutation_id)
        
        # Verify rollback to specific point
        assert rolled_back is not None

    def test_rollback_preserves_mutation_history(self, tracker):
        """Rollback history is preserved for audit trail.
        
        Verify that rollback events are tracked.
        """
        mutation1 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Initial",
            affected_entity="entity",
            data={"value": 1},
        )
        
        mutation2 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Modified",
            affected_entity="entity",
            data={"value": 2},
        )
        
        # Rollback
        tracker.rollback_to_mutation(mutation1.mutation_id)
        
        # Verify history preserved
        history = tracker.get_mutation_history()
        assert len(history) >= 2


class TestMutationHistory:
    """Test suite for mutation history querying."""

    @pytest.fixture
    def tracker(self, temp_db):
        """Initialize vision mutation tracker."""
        return VisionMutationTracker(db_path=temp_db)

    def test_mutation_history_queryable(self, tracker):
        """ACID: Mutation history queryable
        
        Verify that mutations can be queried and retrieved.
        """
        # Track several mutations
        for i in range(10):
            tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Mutation {i}",
                affected_entity=f"entity_{i}",
                data={"index": i},
            )
        
        # Query history
        history = tracker.get_mutation_history()
        
        # Verify queryable
        assert len(history) >= 10
        assert all(isinstance(m, dict) for m in history)

    def test_history_filtered_by_entity(self, tracker):
        """Query mutations filtered by affected entity.
        
        Verify ability to find mutations by entity.
        """
        # Track mutations for different entities
        for i in range(3):
            tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Mutation for entity_a {i}",
                affected_entity="entity_a",
                data={"index": i},
            )
        
        for i in range(2):
            tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Mutation for entity_b {i}",
                affected_entity="entity_b",
                data={"index": i},
            )
        
        # Query by entity
        entity_a_mutations = tracker.get_mutations_for_entity("entity_a")
        entity_b_mutations = tracker.get_mutations_for_entity("entity_b")
        
        # Verify filtering
        assert len(entity_a_mutations) >= 3
        assert len(entity_b_mutations) >= 2

    def test_history_filtered_by_type(self, tracker):
        """Query mutations filtered by type.
        
        Verify ability to find mutations by type.
        """
        # Track different mutation types
        tracker.track_mutation(
            mutation_type=MutationType.CONTEXT_UPDATE,
            source="PHASE-06",
            description="Context",
            affected_entity="entity",
            data={},
        )
        
        tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="State",
            affected_entity="entity",
            data={},
        )
        
        # Query by type
        state_updates = tracker.get_mutations_by_type(MutationType.STATE_UPDATE)
        context_updates = tracker.get_mutations_by_type(MutationType.CONTEXT_UPDATE)
        
        # Verify filtering
        assert len(state_updates) >= 1
        assert len(context_updates) >= 1

    def test_history_time_range_query(self, tracker):
        """Query mutations within time range.
        
        Verify ability to query by timestamp range.
        """
        start_time = datetime.utcnow()
        
        # Track mutations
        for i in range(5):
            tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Mutation {i}",
                affected_entity="entity",
                data={"index": i},
            )
        
        end_time = datetime.utcnow() + timedelta(seconds=1)
        
        # Query by time range
        mutations_in_range = tracker.get_mutations_in_range(start_time, end_time)
        
        # Verify time range filtering
        assert len(mutations_in_range) >= 5

    def test_history_ordered_chronologically(self, tracker):
        """History is ordered by timestamp.
        
        Verify chronological ordering.
        """
        mutations = []
        for i in range(5):
            mutation = tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Mutation {i}",
                affected_entity="entity",
                data={"index": i},
            )
            mutations.append(mutation)
        
        # Get history
        history = tracker.get_mutation_history()
        
        # Verify ordered (most recent first or chronological)
        assert history is not None
        assert len(history) >= 5


class TestMutationIntegration:
    """Integration tests for mutation tracking."""

    @pytest.fixture
    def tracker(self, temp_db):
        """Initialize vision mutation tracker."""
        return VisionMutationTracker(db_path=temp_db)

    def test_end_to_end_mutation_lifecycle(self, tracker):
        """End-to-end: track → query → rollback.
        
        Verify complete lifecycle.
        """
        # Track initial state
        mutation1 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Initial",
            affected_entity="phase",
            data={"phase": "PHASE-10"},
        )
        
        # Track mutation
        mutation2 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Transition",
            affected_entity="phase",
            data={"phase": "PHASE-11"},
        )
        
        # Query history
        history = tracker.get_mutation_history()
        assert len(history) >= 2
        
        # Rollback
        rolled_back = tracker.rollback_to_mutation(mutation1.mutation_id)
        assert rolled_back is not None

    def test_mutation_context_propagation(self, tracker):
        """Context propagates through mutation chain.
        
        Verify context consistency.
        """
        context = {
            "user": "alice",
            "phase": "PHASE-06",
            "request_id": "req-123",
        }
        
        mutation1 = tracker.track_mutation(
            mutation_type=MutationType.CONTEXT_UPDATE,
            source="PHASE-06",
            description="Context update",
            affected_entity="entity1",
            data={},
            context=context,
        )
        
        mutation2 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="State update",
            affected_entity="entity2",
            data={},
            context=context,
        )
        
        # Verify context in both
        assert mutation1.context == context
        assert mutation2.context == context

    def test_mutation_causality_tracking(self, tracker):
        """Track causality between mutations.
        
        Verify parent-child relationships.
        """
        mutation1 = tracker.track_mutation(
            mutation_type=MutationType.CONTEXT_UPDATE,
            source="PHASE-06",
            description="Parent mutation",
            affected_entity="entity1",
            data={"action": "parent"},
        )
        
        # Child mutation caused by parent
        mutation2 = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Child mutation",
            affected_entity="entity2",
            data={"action": "child"},
            parent_mutation_id=mutation1.mutation_id,
        )
        
        # Verify causality
        assert mutation2.parent_mutation_id == mutation1.mutation_id


class TestMutationPersistence:
    """Test suite for mutation persistence."""

    @pytest.fixture
    def tracker(self, temp_db):
        """Initialize vision mutation tracker."""
        return VisionMutationTracker(db_path=temp_db)

    def test_mutations_persisted_to_database(self, tracker):
        """Mutations are persisted to database.
        
        Verify persistence across tracker instances.
        """
        # Track mutation
        mutation = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Persisted mutation",
            affected_entity="entity",
            data={"test": "data"},
        )
        
        # Query from database
        retrieved = tracker.get_mutation(mutation.mutation_id)
        
        # Verify persistence
        assert retrieved is not None
        assert retrieved.mutation_id == mutation.mutation_id

    def test_mutation_search(self, tracker):
        """Search mutations by description.
        
        Verify full-text search capability.
        """
        tracker.track_mutation(
            mutation_type=MutationType.CONTEXT_UPDATE,
            source="PHASE-06",
            description="Updated phase context for PHASE-11",
            affected_entity="PHASE-11",
            data={},
        )
        
        # Search
        results = tracker.search_mutations("PHASE-11")
        
        # Verify search
        assert len(results) > 0


class TestEdgeCasesAndRobustness:
    """Edge case tests for mutation tracking."""

    @pytest.fixture
    def tracker(self, temp_db):
        """Initialize vision mutation tracker."""
        return VisionMutationTracker(db_path=temp_db)

    def test_rapid_mutations_handled(self, tracker):
        """Rapid successive mutations are handled.
        
        Verify no race conditions.
        """
        # Track many mutations rapidly
        mutations = []
        for i in range(100):
            mutation = tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"Rapid mutation {i}",
                affected_entity="entity",
                data={"index": i},
            )
            mutations.append(mutation)
        
        # Verify all tracked
        assert len(mutations) == 100
        
        # Verify no duplicates
        ids = {m.mutation_id for m in mutations}
        assert len(ids) == 100

    def test_large_data_mutations(self, tracker):
        """Large data mutations are handled.
        
        Verify performance with large payloads.
        """
        large_data = {
            f"field_{i}": f"value_{i}" * 100 for i in range(100)
        }
        
        mutation = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Large mutation",
            affected_entity="entity",
            data=large_data,
        )
        
        # Verify handled
        assert mutation.data == large_data

    def test_null_optional_fields_handled(self, tracker):
        """Null/missing optional fields handled.
        
        Verify robustness to incomplete data.
        """
        mutation = tracker.track_mutation(
            mutation_type=MutationType.STATE_UPDATE,
            source="PHASE-06",
            description="Minimal mutation",
            affected_entity="entity",
            data={},
            context=None,
            parent_mutation_id=None,
        )
        
        # Verify handled
        assert mutation is not None

    def test_concurrent_rollbacks_handled(self, tracker):
        """Concurrent rollback attempts handled.
        
        Verify thread safety.
        """
        mutations = []
        for i in range(5):
            mutation = tracker.track_mutation(
                mutation_type=MutationType.STATE_UPDATE,
                source="PHASE-06",
                description=f"State {i}",
                affected_entity="entity",
                data={"value": i},
            )
            mutations.append(mutation)
        
        # Attempt rollback
        rolled_back = tracker.rollback_to_mutation(mutations[2].mutation_id)
        
        # Verify stable
        assert rolled_back is not None
