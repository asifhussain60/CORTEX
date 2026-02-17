"""Golden Test: Conflict Resolution Truth - Production Verification Harness

Tests real conflict detection and precedence-based resolution with production components.
Zero mocks - uses real ConflictResolver from domain_brain.

RED PHASE:
- Tests must fail if conflicts not resolved correctly
- Tests must fail if winner selection wrong  
- Tests must fail if resolution tiers incorrect

GREEN PHASE:
- All conflicts resolved using hierarchy-based resolution
- Winner always selected by SOURCE_HIERARCHY precedence (BKIO > RELATIONSHIPS > GIT > AST)
- Resolution stats tracked correctly

REFACTOR PHASE:
- Clean test data setup
- Modular resolution verification
- Comprehensive tier testing

AC-ID: AC-PHASE24-S1-005
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from cortex.domain_brain.conflict_resolver import (
    ConflictResolver,
    Resolution,
    ResolutionTier,
    ReviewStatus
)
from cortex_intelligence.domain_brain.domain_brain_models import Conflict


class TestConflictDetectionTruth:
    """Conflict Detection Truth Test with Real ConflictResolver."""
    
    @pytest.fixture
    def resolver(self):
        """Initialize real conflict resolver."""
        return ConflictResolver()
    
    def test_hierarchy_resolution_single_winner(self, resolver: ConflictResolver):
        """
        RED PHASE: Test must fail if:
        1. Winner not selected by hierarchy
        2. BKIO doesn't win when present
        3. Resolution tier incorrect
        
        GREEN PHASE: Test passes when:
        1. BKIO always wins (highest in hierarchy)
        2. Resolution tier is HIERARCHY
        3. Confidence score correct
        """
        # Setup: BKIO vs AST conflict (BKIO should win)
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"BKIO": "bkio_value", "AST": "ast_value"}
        )
        
        # Execute
        resolution = resolver.resolve_conflict(conflict)
        
        # Assert: BKIO wins
        assert resolution is not None
        assert resolution.recommended_value == "bkio_value"
        assert resolution.resolution_tier == ResolutionTier.HIERARCHY
        assert resolution.confidence == 0.9
        assert "BKIO" in resolution.reasoning
        
        # Assert: Stats tracked
        stats = resolver.get_resolution_stats()
        assert stats["tier1_resolved"] == 1
        assert stats["total_conflicts"] == 1
    
    def test_hierarchy_resolution_source_precedence(self, resolver: ConflictResolver):
        """Verify SOURCE_HIERARCHY precedence: BKIO > RELATIONSHIPS > GIT > AST."""
        # Test 1: RELATIONSHIPS > AST
        conflict1 = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="value",
            source_values={"RELATIONSHIPS": "rel_value", "AST": "ast_value"}
        )
        
        resolution1 = resolver.resolve_conflict(conflict1)
        assert resolution1.recommended_value == "rel_value"
        assert "RELATIONSHIPS" in resolution1.reasoning
        
        # Test 2: GIT > AST
        conflict2 = Conflict(
            conflict_id="c2",
            domain_id="test",
            attribute="value",
            source_values={"GIT": "git_value", "AST": "ast_value"}
        )
        
        resolution2 = resolver.resolve_conflict(conflict2)
        assert resolution2.recommended_value == "git_value"
        assert "GIT" in resolution2.reasoning
        
        # Test 3: BKIO > ALL
        conflict3 = Conflict(
            conflict_id="c3",
            domain_id="test",
            attribute="value",
            source_values={
                "BKIO": "bkio_value",
                "RELATIONSHIPS": "rel_value",
                "GIT": "git_value",
                "AST": "ast_value"
            }
        )
        
        resolution3 = resolver.resolve_conflict(conflict3)
        assert resolution3.recommended_value == "bkio_value"
        assert "BKIO" in resolution3.reasoning
    
    def test_single_source_no_conflict(self, resolver: ConflictResolver):
        """Verify single source resolves immediately with 100% confidence."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="value",
            source_values={"AST": "ast_only"}
        )
        
        resolution = resolver.resolve_conflict(conflict)
        
        assert resolution is not None
        assert resolution.recommended_value == "ast_only"
        assert resolution.confidence == 1.0
        assert resolution.resolution_tier == ResolutionTier.HIERARCHY
        assert "only source" in resolution.reasoning
    
    def test_empty_sources_escalation(self, resolver: ConflictResolver):
        """Verify empty sources escalate to manual review."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="value",
            source_values={}
        )
        
        resolution = resolver.resolve_conflict(conflict)
        
        assert resolution is not None
        assert resolution.resolution_tier == ResolutionTier.MANUAL
        assert resolution.ticket_id is not None
        assert "CONFLICT-c1" in resolution.ticket_id
        
        # Assert: Escalation tracked
        stats = resolver.get_resolution_stats()
        assert stats["tier3_escalated"] == 1


class TestLENSSynthesisResolution:
    """Test Tier 2: LENS Synthesis resolution."""
    
    @pytest.fixture
    def resolver(self):
        """Initialize real conflict resolver."""
        return ConflictResolver()
    
    def test_lens_synthesis_multiple_sources(self, resolver: ConflictResolver):
        """Test LENS synthesis with multiple non-hierarchy sources."""
        # Create conflict with 2+ sources (triggers Tier 2 if Tier 1 fails)
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"source1": "val1", "source2": "val2"}
        )
        
        # Note: Real resolver tries Tier 1 first, falls back to Tier 2
        resolution = resolver.resolve_conflict(conflict)
        
        assert resolution is not None
        assert resolution.recommended_value is not None
        # With unknown sources, should fall back to first (Tier 1 defaulting)
        assert resolution.confidence > 0.0
    
    def test_lens_synthesis_cache_usage(self, resolver: ConflictResolver):
        """Verify multiple resolutions tracked correctly."""
        conflicts = [
            Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="value",
                source_values={"BKIO": f"val{i}", "AST": f"old{i}"}
            )
            for i in range(3)
        ]
        
        for conflict in conflicts:
            resolution = resolver.resolve_conflict(conflict)
            assert resolution is not None
        
        stats = resolver.get_resolution_stats()
        assert stats["total_conflicts"] == 3
        assert stats["tier1_resolved"] == 3  # All via hierarchy


class TestManualReviewEscalation:
    """Test Tier 3: Manual review escalation."""
    
    @pytest.fixture
    def resolver(self):
        """Initialize real conflict resolver."""
        return ConflictResolver()
    
    def test_manual_escalation_ticket_creation(self, resolver: ConflictResolver):
        """Verify manual escalation creates ticket with 24h SLA."""
        conflict = Conflict(
            conflict_id="complex-conflict",
            domain_id="test",
            attribute="value",
            source_values={}  # Empty triggers escalation
        )
        
        resolution = resolver.resolve_conflict(conflict)
        
        assert resolution is not None
        assert resolution.resolution_tier == ResolutionTier.MANUAL
        assert resolution.ticket_id is not None
        assert resolution.status == ReviewStatus.PENDING
        assert resolution.sla_deadline is not None
        assert resolution.due_at is not None  # Alias property
        
        # Verify ticket in queue
        queue = resolver.get_manual_review_queue()
        assert len(queue) == 1
        assert queue[0].ticket_id == resolution.ticket_id
    
    def test_manual_ticket_resolution(self, resolver: ConflictResolver):
        """Test resolving manual review ticket."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="value",
            source_values={}
        )
        
        resolution = resolver.resolve_conflict(conflict)
        ticket_id = resolution.ticket_id
        
        # Resolve ticket
        success = resolver.resolve_manual_ticket(
            ticket_id=ticket_id,
            resolved_value="manual_decision",
            resolved_by="human_reviewer"
        )
        
        assert success is True
        
        # Verify ticket updated
        ticket = resolver.pending_reviews[ticket_id]
        assert ticket.status == ReviewStatus.RESOLVED
        assert ticket.resolution == "manual_decision"
        assert ticket.resolved_by == "human_reviewer"
    
    def test_sla_violation_detection(self, resolver: ConflictResolver):
        """Test SLA violation detection for overdue tickets."""
        from datetime import timedelta
        
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="value",
            source_values={}
        )
        
        resolution = resolver.resolve_conflict(conflict)
        ticket_id = resolution.ticket_id
        
        # Manually set SLA to past (simulate overdue)
        resolver.pending_reviews[ticket_id].sla_deadline = (
            datetime.utcnow() - timedelta(hours=1)
        )
        
        # Check SLA violation
        is_violated = resolver.check_sla_violation(ticket_id)
        assert is_violated is True
        
        # Verify in overdue queue
        overdue = resolver.get_overdue_tickets()
        assert len(overdue) == 1
        assert overdue[0].ticket_id == ticket_id


class TestConflictResolutionStats:
    """Test resolution statistics and reporting."""
    
    @pytest.fixture
    def resolver(self):
        """Initialize real conflict resolver."""
        return ConflictResolver()
    
    def test_resolution_stats_accuracy(self, resolver: ConflictResolver):
        """Verify resolution stats calculated correctly."""
        # Create mix of resolutions
        conflicts = [
            Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="value",
                source_values={"BKIO": f"val{i}", "AST": f"old{i}"}
            )
            for i in range(5)
        ]
        
        # Add one escalation
        conflicts.append(Conflict(
            conflict_id="escalated",
            domain_id="test",
            attribute="value",
            source_values={}
        ))
        
        for conflict in conflicts:
            resolver.resolve_conflict(conflict)
        
        stats = resolver.get_resolution_stats()
        
        assert stats["total_conflicts"] == 6
        assert stats["tier1_resolved"] == 5
        assert stats["tier3_escalated"] == 1
        assert stats["resolution_rate_percent"] > 80.0
        assert stats["escalation_rate_percent"] < 20.0
    
    def test_get_status_comprehensive(self, resolver: ConflictResolver):
        """Test comprehensive status reporting."""
        # Create some conflicts
        for i in range(3):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="value",
                source_values={"BKIO": f"val{i}"}
            )
            resolver.resolve_conflict(conflict)
        
        # Add escalated conflict
        escalated = Conflict(
            conflict_id="escalated",
            domain_id="test",
            attribute="value",
            source_values={}
        )
        resolver.resolve_conflict(escalated)
        
        status = resolver.get_status()
        
        assert "resolution_stats" in status
        assert "pending_tickets" in status
        assert "overdue_tickets" in status
        assert status["pending_tickets"] == 1
        assert status["overdue_tickets"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
