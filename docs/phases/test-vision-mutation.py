"""
Tests for Vision Mutation Tracker - AC-AR-015-01

Comprehensive test coverage for vision mutation tracking including:
- Recording mutations with metadata
- Validating mutation consistency
- Creating snapshots
- Reviewing and applying mutations
- Impact analysis
- History queries and filtering
- Persistence and loading
"""

import pytest
from datetime import datetime
from pathlib import Path
import json
import tempfile

from src.core.vision_mutation_tracker import (
    VisionMutationTracker,
    VisionMutation,
    VisionSnapshot,
    VisionImpact,
    MutationType,
    MutationStatus,
    ImpactArea,
    ImpactSeverity,
    VisionMutationValidator,
)


@pytest.fixture
def vision_tracker():
    """Create a fresh vision tracker for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "mutations.json"
        tracker = VisionMutationTracker(storage_path=storage_path)
        yield tracker


@pytest.fixture
def sample_impact():
    """Create a sample impact analysis."""
    return VisionImpact(
        affected_areas={ImpactArea.TIER0_GOVERNANCE, ImpactArea.ORCHESTRATOR_BEHAVIOR},
        severity=ImpactSeverity.HIGH,
        estimated_affected_systems=3,
        required_orchestrator_updates=True,
        requires_phase_adjustment=False,
        description="Test impact analysis",
    )


@pytest.fixture
def sample_mutation(sample_impact):
    """Create a sample mutation."""
    return VisionMutation(
        mutation_id="VMUT-00001",
        mutation_type=MutationType.STATEMENT_UPDATE,
        timestamp=datetime.now(),
        author="test_author",
        motivation="Test motivation for change",
        previous_value="Old vision statement",
        new_value="New vision statement that is longer",
        impact_analysis=sample_impact,
    )


class TestVisionImpact:
    """Test VisionImpact data structure."""

    def test_impact_creation(self, sample_impact):
        """Test creating an impact analysis."""
        assert sample_impact.severity == ImpactSeverity.HIGH
        assert len(sample_impact.affected_areas) == 2
        assert sample_impact.required_orchestrator_updates is True

    def test_impact_serialization(self, sample_impact):
        """Test converting impact to and from dictionary."""
        impact_dict = sample_impact.to_dict()
        
        assert impact_dict["severity"] == "high"
        assert "tier0_governance" in impact_dict["affected_areas"]
        assert impact_dict["required_orchestrator_updates"] is True

    def test_impact_deserialization(self, sample_impact):
        """Test loading impact from dictionary."""
        impact_dict = sample_impact.to_dict()
        restored = VisionImpact.from_dict(impact_dict)
        
        assert restored.severity == sample_impact.severity
        assert restored.affected_areas == sample_impact.affected_areas
        assert restored.required_orchestrator_updates == sample_impact.required_orchestrator_updates


class TestVisionMutation:
    """Test VisionMutation data structure."""

    def test_mutation_creation(self, sample_mutation):
        """Test creating a mutation."""
        assert sample_mutation.mutation_id == "VMUT-00001"
        assert sample_mutation.status == MutationStatus.PROPOSED
        assert sample_mutation.reviewed_by is None

    def test_mutation_serialization(self, sample_mutation):
        """Test converting mutation to dictionary."""
        mut_dict = sample_mutation.to_dict()
        
        assert mut_dict["mutation_id"] == "VMUT-00001"
        assert mut_dict["mutation_type"] == "statement_update"
        assert mut_dict["status"] == "proposed"

    def test_mutation_deserialization(self, sample_mutation):
        """Test loading mutation from dictionary."""
        mut_dict = sample_mutation.to_dict()
        restored = VisionMutation.from_dict(mut_dict)
        
        assert restored.mutation_id == sample_mutation.mutation_id
        assert restored.author == sample_mutation.author
        assert restored.motivation == sample_mutation.motivation


class TestVisionSnapshot:
    """Test VisionSnapshot data structure."""

    def test_snapshot_creation(self):
        """Test creating a snapshot."""
        vision_content = {"statement": "Test vision", "principles": []}
        snapshot = VisionSnapshot(
            snapshot_id="SNAP-00001",
            timestamp=datetime.now(),
            mutation_id="VMUT-00001",
            vision_content=vision_content,
            hash_value="abc123",
            description="Test snapshot",
        )
        
        assert snapshot.snapshot_id == "SNAP-00001"
        assert snapshot.vision_content == vision_content

    def test_snapshot_serialization(self):
        """Test converting snapshot to dictionary."""
        vision_content = {"statement": "Test vision"}
        snapshot = VisionSnapshot(
            snapshot_id="SNAP-00001",
            timestamp=datetime(2026, 1, 14),
            mutation_id="VMUT-00001",
            vision_content=vision_content,
            hash_value="abc123",
            description="Test snapshot",
        )
        
        snap_dict = snapshot.to_dict()
        assert snap_dict["snapshot_id"] == "SNAP-00001"
        assert snap_dict["vision_content"] == vision_content


class TestVisionMutationValidator:
    """Test VisionMutationValidator."""

    def test_valid_mutation(self, sample_mutation):
        """Test validating a valid mutation."""
        validator = VisionMutationValidator()
        is_valid, error = validator.validate_mutation(sample_mutation)
        
        assert is_valid is True
        assert error == ""

    def test_invalid_motivation(self, sample_mutation):
        """Test mutation with invalid motivation."""
        validator = VisionMutationValidator()
        sample_mutation.motivation = "short"
        is_valid, error = validator.validate_mutation(sample_mutation)
        
        assert is_valid is False
        assert "motivation" in error.lower()

    def test_no_change_mutation(self, sample_mutation):
        """Test mutation that doesn't change value."""
        validator = VisionMutationValidator()
        sample_mutation.new_value = sample_mutation.previous_value
        is_valid, error = validator.validate_mutation(sample_mutation)
        
        assert is_valid is False
        assert "change" in error.lower()

    def test_missing_impact_analysis(self, sample_mutation):
        """Test mutation with missing impact analysis."""
        validator = VisionMutationValidator()
        sample_mutation.impact_analysis = None
        is_valid, error = validator.validate_mutation(sample_mutation)
        
        assert is_valid is False
        assert "impact" in error.lower()


class TestVisionMutationRecording:
    """Test recording mutations in the tracker."""

    def test_record_mutation(self, vision_tracker, sample_impact):
        """Test recording a single mutation."""
        success, msg, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision for clarity and alignment",
            previous_value="Old vision",
            new_value="New improved vision statement",
            impact_analysis=sample_impact,
        )
        
        assert success is True
        assert mut_id is not None
        assert "VMUT" in mut_id

    def test_record_multiple_mutations(self, vision_tracker, sample_impact):
        """Test recording multiple mutations."""
        mut_ids = []
        for i in range(3):
            success, _, mut_id = vision_tracker.record_mutation(
                mutation_type=MutationType.PRINCIPLE_ADD,
                author=f"author_{i}",
                motivation=f"Add principle {i} for better guidance",
                previous_value="",
                new_value=f"Principle {i}",
                impact_analysis=sample_impact,
            )
            assert success is True
            mut_ids.append(mut_id)
        
        assert len(mut_ids) == 3
        assert mut_ids[0] != mut_ids[1]

    def test_record_invalid_mutation(self, vision_tracker, sample_impact):
        """Test recording an invalid mutation."""
        success, msg, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="bob",
            motivation="short",  # Too short
            previous_value="Same",
            new_value="Same",  # No change
            impact_analysis=sample_impact,
        )
        
        assert success is False
        assert mut_id is None

    def test_record_mutation_with_tags(self, vision_tracker, sample_impact):
        """Test recording mutation with tags."""
        success, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Major vision update for new direction",
            previous_value="Old",
            new_value="New improved direction",
            impact_analysis=sample_impact,
            tags=["major", "strategic", "2026-planning"],
        )
        
        assert success is True
        mutation = vision_tracker.mutations[mut_id]
        assert "major" in mutation.tags
        assert len(mutation.tags) == 3

    def test_record_mutation_with_dependencies(self, vision_tracker, sample_impact):
        """Test recording mutation with dependencies."""
        # First mutation
        _, _, mut_id_1 = vision_tracker.record_mutation(
            mutation_type=MutationType.PRINCIPLE_ADD,
            author="alice",
            motivation="Add foundational principle for consistency",
            previous_value="",
            new_value="Principle A",
            impact_analysis=sample_impact,
        )
        
        # Second mutation depends on first
        success, _, mut_id_2 = vision_tracker.record_mutation(
            mutation_type=MutationType.PRINCIPLE_ADD,
            author="alice",
            motivation="Add related principle for framework",
            previous_value="",
            new_value="Principle B",
            impact_analysis=sample_impact,
            depends_on=[mut_id_1],
        )
        
        assert success is True
        mutation = vision_tracker.mutations[mut_id_2]
        assert mut_id_1 in mutation.depends_on_mutations


class TestVisionMutationReview:
    """Test reviewing and approving mutations."""

    def test_review_approve_mutation(self, vision_tracker, sample_impact):
        """Test approving a mutation."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision for clarity",
            previous_value="Old",
            new_value="New improved vision",
            impact_analysis=sample_impact,
        )
        
        success, msg = vision_tracker.review_mutation(
            mutation_id=mut_id,
            approved=True,
            reviewer="bob",
            notes="Looks good",
        )
        
        assert success is True
        mutation = vision_tracker.mutations[mut_id]
        assert mutation.status == MutationStatus.APPROVED
        assert mutation.reviewed_by == "bob"

    def test_review_reject_mutation(self, vision_tracker, sample_impact):
        """Test rejecting a mutation."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision statement",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        success, msg = vision_tracker.review_mutation(
            mutation_id=mut_id,
            approved=False,
            reviewer="bob",
            notes="Needs more review",
        )
        
        assert success is True
        mutation = vision_tracker.mutations[mut_id]
        assert mutation.status == MutationStatus.REJECTED

    def test_cannot_review_already_reviewed(self, vision_tracker, sample_impact):
        """Test that already reviewed mutations cannot be re-reviewed."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        # First review
        vision_tracker.review_mutation(mut_id, True, "bob")
        
        # Second review should fail
        success, msg = vision_tracker.review_mutation(
            mut_id, False, "charlie", "Changed my mind"
        )
        
        assert success is False


class TestVisionMutationApplication:
    """Test applying approved mutations."""

    def test_apply_approved_mutation(self, vision_tracker, sample_impact):
        """Test applying an approved mutation."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        # Approve
        vision_tracker.review_mutation(mut_id, True, "bob")
        
        # Apply
        success, msg = vision_tracker.apply_mutation(mut_id)
        
        assert success is True
        mutation = vision_tracker.mutations[mut_id]
        assert mutation.status == MutationStatus.APPLIED
        assert mutation.applied_timestamp is not None

    def test_cannot_apply_unapproved_mutation(self, vision_tracker, sample_impact):
        """Test that unapproved mutations cannot be applied."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        success, msg = vision_tracker.apply_mutation(mut_id)
        
        assert success is False


class TestVisionSnapshots:
    """Test snapshot creation and management."""

    def test_create_snapshot(self, vision_tracker, sample_impact):
        """Test creating a snapshot."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        vision_content = {"statement": "New", "principles": ["P1", "P2"]}
        success, snap_id = vision_tracker.create_snapshot(
            mutation_id=mut_id,
            vision_content=vision_content,
            description="After first update",
        )
        
        assert success is True
        assert snap_id is not None
        snapshot = vision_tracker.snapshots[snap_id]
        assert snapshot.vision_content == vision_content

    def test_get_latest_snapshot(self, vision_tracker, sample_impact):
        """Test getting the latest snapshot."""
        _, _, mut_id_1 = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="First update",
            previous_value="V0",
            new_value="V1",
            impact_analysis=sample_impact,
        )
        
        _, snap_id_1 = vision_tracker.create_snapshot(
            mut_id_1, {"version": 1}, "Snapshot 1"
        )
        
        _, _, mut_id_2 = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Second update",
            previous_value="V1",
            new_value="V2",
            impact_analysis=sample_impact,
        )
        
        _, snap_id_2 = vision_tracker.create_snapshot(
            mut_id_2, {"version": 2}, "Snapshot 2"
        )
        
        latest = vision_tracker.get_latest_snapshot()
        assert latest.snapshot_id == snap_id_2

    def test_get_snapshot_history(self, vision_tracker, sample_impact):
        """Test getting all snapshots in order."""
        for i in range(3):
            _, _, mut_id = vision_tracker.record_mutation(
                mutation_type=MutationType.STATEMENT_UPDATE,
                author="alice",
                motivation=f"Vision update round {i} for testing purposes",
                previous_value=f"V{i}",
                new_value=f"V{i+1}",
                impact_analysis=sample_impact,
            )
            vision_tracker.create_snapshot(
                mut_id, {"version": i+1}, f"Snapshot {i+1}"
            )
        
        history = vision_tracker.get_snapshot_history()
        assert len(history) == 3
        # Should be in chronological order
        for i in range(1, len(history)):
            assert history[i].timestamp >= history[i-1].timestamp


class TestVisionImpactAnalysis:
    """Test impact analysis and calculations."""

    def test_get_mutation_impact(self, vision_tracker, sample_impact):
        """Test retrieving mutation impact analysis."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        impact = vision_tracker.get_mutation_impact_analysis(mut_id)
        assert impact is not None
        assert impact.severity == ImpactSeverity.HIGH

    def test_combined_impact_empty(self, vision_tracker):
        """Test combining empty mutation list."""
        success, impact = vision_tracker.calculate_combined_impact([])
        
        assert success is True
        assert impact.severity == ImpactSeverity.LOW
        assert len(impact.affected_areas) == 0

    def test_combined_impact_single(self, vision_tracker, sample_impact):
        """Test combining single mutation."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update vision",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        success, combined = vision_tracker.calculate_combined_impact([mut_id])
        
        assert success is True
        assert combined.severity == sample_impact.severity

    def test_combined_impact_multiple(self, vision_tracker):
        """Test combining multiple mutations."""
        impact_low = VisionImpact(
            affected_areas={ImpactArea.TIER2_RESPONSE},
            severity=ImpactSeverity.LOW,
            estimated_affected_systems=1,
            required_orchestrator_updates=False,
            requires_phase_adjustment=False,
            description="Low impact",
        )
        
        impact_high = VisionImpact(
            affected_areas={ImpactArea.TIER0_GOVERNANCE},
            severity=ImpactSeverity.HIGH,
            estimated_affected_systems=3,
            required_orchestrator_updates=True,
            requires_phase_adjustment=True,
            description="High impact",
        )
        
        _, _, mut_id_1 = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Low impact update",
            previous_value="Old",
            new_value="New",
            impact_analysis=impact_low,
        )
        
        _, _, mut_id_2 = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="bob",
            motivation="High impact change",
            previous_value="Old2",
            new_value="New2",
            impact_analysis=impact_high,
        )
        
        success, combined = vision_tracker.calculate_combined_impact([mut_id_1, mut_id_2])
        
        assert success is True
        assert combined.severity == ImpactSeverity.HIGH
        assert len(combined.affected_areas) == 2
        assert combined.estimated_affected_systems == 4
        assert combined.required_orchestrator_updates is True


class TestMutationHistory:
    """Test querying mutation history."""

    def test_get_all_history(self, vision_tracker, sample_impact):
        """Test getting all mutation history."""
        for i in range(3):
            vision_tracker.record_mutation(
                mutation_type=MutationType.PRINCIPLE_ADD,
                author="alice",
                motivation=f"Add principle {i}",
                previous_value="",
                new_value=f"Principle {i}",
                impact_analysis=sample_impact,
            )
        
        history = vision_tracker.get_mutation_history()
        assert len(history) == 3

    def test_filter_by_author(self, vision_tracker, sample_impact):
        """Test filtering history by author."""
        vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Alice's update",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="bob",
            motivation="Bob's update",
            previous_value="Old",
            new_value="Newer",
            impact_analysis=sample_impact,
        )
        
        alice_history = vision_tracker.get_mutation_history(author="alice")
        assert len(alice_history) == 1
        assert alice_history[0].author == "alice"

    def test_filter_by_status(self, vision_tracker, sample_impact):
        """Test filtering history by status."""
        _, _, mut_id_1 = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="First update",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        _, _, mut_id_2 = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Second update",
            previous_value="New",
            new_value="Newer",
            impact_analysis=sample_impact,
        )
        
        vision_tracker.review_mutation(mut_id_1, True, "bob")
        
        proposed = vision_tracker.get_mutation_history(status=MutationStatus.PROPOSED)
        assert len(proposed) == 1

    def test_filter_by_type(self, vision_tracker, sample_impact):
        """Test filtering history by mutation type."""
        vision_tracker.record_mutation(
            mutation_type=MutationType.PRINCIPLE_ADD,
            author="alice",
            motivation="Add principle",
            previous_value="",
            new_value="P1",
            impact_analysis=sample_impact,
        )
        
        vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update statement",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        adds = vision_tracker.get_mutation_history(mutation_type=MutationType.PRINCIPLE_ADD)
        assert len(adds) == 1

    def test_history_limit(self, vision_tracker, sample_impact):
        """Test limiting history results."""
        for i in range(5):
            vision_tracker.record_mutation(
                mutation_type=MutationType.PRINCIPLE_ADD,
                author="alice",
                motivation=f"Principle {i}",
                previous_value="",
                new_value=f"P{i}",
                impact_analysis=sample_impact,
            )
        
        limited = vision_tracker.get_mutation_history(limit=2)
        assert len(limited) == 2


class TestMutationStatistics:
    """Test mutation statistics and reporting."""

    def test_stats_empty(self, vision_tracker):
        """Test statistics with no mutations."""
        stats = vision_tracker.get_mutation_stats()
        
        assert stats["total_mutations"] == 0
        assert len(stats["by_type"]) == 0
        assert len(stats["by_author"]) == 0

    def test_stats_populated(self, vision_tracker, sample_impact):
        """Test statistics with multiple mutations."""
        for i in range(2):
            vision_tracker.record_mutation(
                mutation_type=MutationType.PRINCIPLE_ADD,
                author="alice",
                motivation=f"Add principle number {i} for framework",
                previous_value="",
                new_value=f"P{i}",
                impact_analysis=sample_impact,
            )
        
        vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="bob",
            motivation="Update the vision statement for clarity",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        stats = vision_tracker.get_mutation_stats()
        
        assert stats["total_mutations"] == 3
        assert stats["by_type"]["principle_add"] == 2
        assert stats["by_author"]["alice"] == 2
        assert stats["by_author"]["bob"] == 1


class TestMutationExport:
    """Test exporting mutations and snapshots."""

    def test_export_all_mutations(self, vision_tracker, sample_impact):
        """Test exporting all mutations."""
        for i in range(2):
            vision_tracker.record_mutation(
                mutation_type=MutationType.PRINCIPLE_ADD,
                author="alice",
                motivation=f"Add principle number {i} for testing",
                previous_value="",
                new_value=f"P{i}",
                impact_analysis=sample_impact,
            )
        
        export = vision_tracker.export_mutations()
        
        assert export["total"] == 2
        assert len(export["mutations"]) == 2

    def test_export_specific_mutations(self, vision_tracker, sample_impact):
        """Test exporting specific mutations."""
        mut_ids = []
        for i in range(3):
            _, _, mut_id = vision_tracker.record_mutation(
                mutation_type=MutationType.PRINCIPLE_ADD,
                author="alice",
                motivation=f"Add principle number {i} for testing",
                previous_value="",
                new_value=f"P{i}",
                impact_analysis=sample_impact,
            )
            mut_ids.append(mut_id)
        
        export = vision_tracker.export_mutations([mut_ids[0], mut_ids[2]])
        
        assert export["total"] == 2
        assert mut_ids[0] in export["mutations"]
        assert mut_ids[2] in export["mutations"]

    def test_export_snapshots(self, vision_tracker, sample_impact):
        """Test exporting snapshots."""
        _, _, mut_id = vision_tracker.record_mutation(
            mutation_type=MutationType.STATEMENT_UPDATE,
            author="alice",
            motivation="Update the vision statement for testing",
            previous_value="Old",
            new_value="New",
            impact_analysis=sample_impact,
        )
        
        vision_tracker.create_snapshot(mut_id, {"version": 1}, "Snap 1")
        vision_tracker.create_snapshot(mut_id, {"version": 2}, "Snap 2")
        
        export = vision_tracker.export_snapshots()
        
        assert export["total"] == 2
        assert len(export["snapshots"]) == 2


class TestMutationPersistence:
    """Test saving and loading mutations."""

    def test_save_and_load(self):
        """Test persisting mutations to disk and reloading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "mutations.json"
            
            # Create tracker and add mutation
            tracker1 = VisionMutationTracker(storage_path=storage_path)
            impact = VisionImpact(
                affected_areas={ImpactArea.TIER0_GOVERNANCE},
                severity=ImpactSeverity.HIGH,
                estimated_affected_systems=2,
                required_orchestrator_updates=True,
                requires_phase_adjustment=False,
                description="Test",
            )
            
            _, _, mut_id = tracker1.record_mutation(
                mutation_type=MutationType.STATEMENT_UPDATE,
                author="alice",
                motivation="Test save and load functionality",
                previous_value="Old",
                new_value="New",
                impact_analysis=impact,
            )
            
            tracker1._save_to_storage()
            
            # Create new tracker and verify data loaded
            tracker2 = VisionMutationTracker(storage_path=storage_path)
            
            assert mut_id in tracker2.mutations
            mutation = tracker2.mutations[mut_id]
            assert mutation.author == "alice"
            assert mutation.motivation == "Test save and load functionality"
