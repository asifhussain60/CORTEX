"""
Golden Tests: CortexMasterPlanOrchestrator

Authority: CORE-008 (TDD mandatory), CORE-035 (single canonical impl)
Coverage: Sequence computation, phase lifecycle, workflow template loading,
          folder management, registry sync, execution workflow.

Test tiers:
  - Unit: Each method in isolation
  - Integration: Orchestrator + registry + folder management
  - Golden: End-to-end create + execute workflow
  - Negative: Wrong inputs, corrupt registry, missing folders
  - Edge: Empty registry, all-complete, concurrent creates
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import yaml

from cortex.orchestrators.core.master_plan_orchestrator import (
    CortexMasterPlanOrchestrator,
    PhaseCreationRequest,
    PhaseLifecycleError,
    PhaseRecord,
    RegistrySyncResult,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def tmp_registry(tmp_path: Path) -> Path:
    """Build a minimal cortex-master.yaml + planning/phases folder structure."""
    registry_dir = tmp_path / "cortex-registry"
    registry_dir.mkdir()
    # SSOT: phases live at cortex-registry/planning/phases/ per copilot-instructions.md
    phases_dir = tmp_path / "cortex-registry" / "planning" / "phases"
    (phases_dir / "planned").mkdir(parents=True)
    (phases_dir / "completed").mkdir(parents=True)
    (phases_dir / "deferred").mkdir(parents=True)

    # Create lifecycle workflow templates folder with both required templates
    template_dir = tmp_path / "cortex-registry" / "workflows" / "templates" / "lifecycle"
    template_dir.mkdir(parents=True)
    _write_creation_template(template_dir)
    _write_execution_template(template_dir)

    master_yaml = {
        "metadata": {
            "version": "7.9",
            "total_phases": 3,
            "active": 0,
            "completed": 3,
            "planned": 0,
        },
        "phases": [
            {"id": "phase-01", "title": "Bootstrapper", "status": "complete", "sequence": 1},
            {"id": "phase-02", "title": "EventBus", "status": "complete", "sequence": 2},
            {"id": "phase-03", "title": "LensEngine", "status": "complete", "sequence": 3},
        ],
    }
    (registry_dir / "cortex-master.yaml").write_text(yaml.dump(master_yaml))
    return tmp_path


def _write_creation_template(template_dir: Path) -> None:
    """Write a minimal master-plan-orchestrator.yaml into template_dir."""
    content = {
        "workflow": {
            "name": "master_plan_orchestrator",
            "stages": [
                {"name": "sequence_check", "order": 1},
                {"name": "sync_folders", "order": 2},
                {"name": "create_entry", "order": 3},
                {"name": "create_file", "order": 4},
            ],
        }
    }
    (template_dir / "master-plan-orchestrator.yaml").write_text(yaml.dump(content))


def _write_execution_template(template_dir: Path) -> None:
    """Write a minimal master-plan-execution.yaml into template_dir."""
    content = {
        "workflow": {
            "name": "master_plan_execution",
            "stages": [
                {"name": "gap_analysis", "order": 1},
                {"name": "tdd_red_phase", "order": 2},
                {"name": "autonomous_execute", "order": 3},
                {"name": "refactor_cycle", "order": 4},
                {"name": "governance_audit", "order": 5},
                {"name": "registry_update", "order": 6},
                {"name": "commit_and_push", "order": 7},
            ],
        }
    }
    (template_dir / "master-plan-execution.yaml").write_text(yaml.dump(content))


@pytest.fixture
def orchestrator(tmp_registry: Path) -> CortexMasterPlanOrchestrator:
    """Create orchestrator pointed at tmp registry."""
    return CortexMasterPlanOrchestrator(registry_root=tmp_registry)


@pytest.fixture
def orchestrator_with_planned(tmp_registry: Path) -> CortexMasterPlanOrchestrator:
    """Registry with a mix of completed and anomalous phases."""
    registry_dir = tmp_registry / "cortex-registry"
    master_yaml = {
        "metadata": {
            "version": "7.9",
            "total_phases": 5,
            "active": 0,
            "completed": 3,
            "planned": 2,
        },
        "phases": [
            {"id": "phase-01", "title": "Bootstrapper", "status": "complete", "sequence": 1},
            {"id": "phase-02", "title": "EventBus", "status": "complete", "sequence": 2},
            {"id": "phase-03", "title": "LensEngine", "status": "complete", "sequence": 3},
            {"id": "phase-04", "title": "HealthPipeline", "status": "complete", "sequence": 4},
            {"id": "phase-100", "title": "AnomolousPhase", "status": "planned", "sequence": 100},
        ],
    }
    (registry_dir / "cortex-master.yaml").write_text(yaml.dump(master_yaml))

    # Place phase-04 in planned/ (should be in completed/)
    # SSOT: phases live at cortex-registry/planning/phases/
    planned_dir = tmp_registry / "cortex-registry" / "planning" / "phases" / "planned"
    (planned_dir / "phase-04-health-pipeline.yaml").write_text("phase_id: phase-04\nstatus: complete\n")
    (planned_dir / "phase-100-anomolous-phase.yaml").write_text("phase_id: phase-100\nstatus: planned\n")

    return CortexMasterPlanOrchestrator(registry_root=tmp_registry)


# ============================================================================
# UNIT TESTS: next_sequence_number
# ============================================================================


class TestNextSequenceNumber:
    """Tests for sequence number computation from cortex-master.yaml."""

    def test_returns_sequential_next_after_highest(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Next sequence = max(existing) + 1, ignoring gaps or out-of-order."""
        assert orchestrator.next_sequence_number() == 4

    def test_anomalous_high_number_ignored_in_sequence(self, orchestrator_with_planned: CortexMasterPlanOrchestrator) -> None:
        """phase-100 must NOT dictate next sequence — reads last valid sequential number."""
        # 4 sequential phases complete, next should be 5 NOT 101
        assert orchestrator_with_planned.next_sequence_number() == 5

    def test_empty_registry_returns_one(self, tmp_registry: Path) -> None:
        """Empty phase list → first phase is sequence 1."""
        registry_dir = tmp_registry / "cortex-registry"
        (registry_dir / "cortex-master.yaml").write_text(yaml.dump({"metadata": {"total_phases": 0}, "phases": []}))
        orch = CortexMasterPlanOrchestrator(registry_root=tmp_registry)
        assert orch.next_sequence_number() == 1

    def test_sequence_uses_sequential_max_not_id_number(self, tmp_registry: Path) -> None:
        """Sequence field is authoritative — ignores phase ID numbers."""
        registry_dir = tmp_registry / "cortex-registry"
        data = {
            "metadata": {"total_phases": 2},
            "phases": [
                {"id": "phase-99", "status": "complete", "sequence": 1},
                {"id": "phase-01", "status": "complete", "sequence": 2},
            ],
        }
        (registry_dir / "cortex-master.yaml").write_text(yaml.dump(data))
        orch = CortexMasterPlanOrchestrator(registry_root=tmp_registry)
        assert orch.next_sequence_number() == 3


# ============================================================================
# UNIT TESTS: sync_phase_folders
# ============================================================================


class TestSyncPhaseFolders:
    """Tests for moving phases to correct folders based on status in registry."""

    def test_completed_phases_moved_from_planned_to_completed(
        self, orchestrator_with_planned: CortexMasterPlanOrchestrator
    ) -> None:
        """phase-04 has status=complete but is in planned/ → must move to completed/."""
        result = orchestrator_with_planned.sync_phase_folders()
        assert result.moved_to_completed >= 1
        completed_dir = orchestrator_with_planned._phases_dir / "completed"
        planned_dir = orchestrator_with_planned._phases_dir / "planned"
        assert any("phase-04" in f.name for f in completed_dir.iterdir())
        assert not any("phase-04" in f.name for f in planned_dir.iterdir())

    def test_anomalous_phase_flagged_in_result(
        self, orchestrator_with_planned: CortexMasterPlanOrchestrator
    ) -> None:
        """phase-100 in planned/ has out-of-sequence ID (100 > 5 phases) → anomaly."""
        result = orchestrator_with_planned.sync_phase_folders()
        assert len(result.anomalies) >= 1
        assert any("phase-100" in a for a in result.anomalies)

    def test_no_moves_when_already_synced(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Clean registry → no files moved."""
        result = orchestrator.sync_phase_folders()
        assert result.moved_to_completed == 0
        assert result.moved_to_deferred == 0

    def test_sync_result_is_registry_sync_result(
        self, orchestrator: CortexMasterPlanOrchestrator
    ) -> None:
        result = orchestrator.sync_phase_folders()
        assert isinstance(result, RegistrySyncResult)


# ============================================================================
# UNIT TESTS: create_phase
# ============================================================================


class TestCreatePhase:
    """Tests for PhaseCreationRequest → cortex-master.yaml entry + yaml file."""

    def test_creates_entry_in_registry_first(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Registry entry must be written BEFORE file is created (spec requirement)."""
        req = PhaseCreationRequest(
            title="Master Plan Orchestrator",
            description="CORTEX phase lifecycle management orchestrator",
            priority="P0",
        )
        record = orchestrator.create_phase(req)
        # Registry must have the new entry
        registry = orchestrator._load_registry()
        ids = [p["id"] for p in registry.get("phases", [])]
        assert record.phase_id in ids

    def test_creates_yaml_file_in_planned_folder(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Phase YAML file must land in planned/ folder."""
        req = PhaseCreationRequest(
            title="Master Plan Orchestrator",
            description="Phase lifecycle management",
            priority="P0",
        )
        record = orchestrator.create_phase(req)
        planned_dir = orchestrator._phases_dir / "planned"
        files = list(planned_dir.iterdir())
        assert any(record.phase_id in f.name for f in files)

    def test_phase_id_uses_sequential_number(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Phase ID must be phase-04 (3 existing + 1), not phase-100 or random."""
        req = PhaseCreationRequest(title="New Phase", description="desc", priority="P1")
        record = orchestrator.create_phase(req)
        assert record.phase_id == "phase-04"

    def test_phase_file_name_matches_id_and_title(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """File name: phase-04-master-plan-orchestrator.yaml (snake_case, CORE-028)."""
        req = PhaseCreationRequest(title="Master Plan Orchestrator", description="desc", priority="P0")
        record = orchestrator.create_phase(req)
        planned_dir = orchestrator._phases_dir / "planned"
        file_names = [f.name for f in planned_dir.iterdir()]
        assert f"phase-04-master-plan-orchestrator.yaml" in file_names

    def test_registry_metadata_total_phases_incremented(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """total_phases in metadata must increment by 1 after creation."""
        req = PhaseCreationRequest(title="New Phase", description="desc", priority="P1")
        orchestrator.create_phase(req)
        registry = orchestrator._load_registry()
        assert registry["metadata"]["total_phases"] == 4

    def test_create_phase_returns_phase_record(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        req = PhaseCreationRequest(title="Test Phase", description="desc", priority="P2")
        record = orchestrator.create_phase(req)
        assert isinstance(record, PhaseRecord)
        assert record.sequence == 4

    def test_two_sequential_creates_get_sequential_numbers(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Two back-to-back creates → phase-04 then phase-05."""
        req1 = PhaseCreationRequest(title="Phase Four", description="desc", priority="P1")
        req2 = PhaseCreationRequest(title="Phase Five", description="desc", priority="P1")
        r1 = orchestrator.create_phase(req1)
        r2 = orchestrator.create_phase(req2)
        assert r1.phase_id == "phase-04"
        assert r2.phase_id == "phase-05"


# ============================================================================
# UNIT TESTS: load_workflow_template
# ============================================================================


class TestLoadWorkflowTemplate:
    """Tests for workflow template loading from YAML."""

    def test_loads_creation_template(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """master-plan-orchestrator.yaml must load without error."""
        template = orchestrator.load_workflow_template("master-plan-orchestrator")
        assert template is not None
        assert "workflow" in template

    def test_loads_execution_template(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """master-plan-execution.yaml must load without error."""
        template = orchestrator.load_workflow_template("master-plan-execution")
        assert template is not None
        assert "workflow" in template

    def test_missing_template_raises_error(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Non-existent template name raises PhaseLifecycleError."""
        with pytest.raises(PhaseLifecycleError, match="template not found"):
            orchestrator.load_workflow_template("non-existent-template")

    def test_creation_template_has_required_stages(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Creation template must have: sequence_check, sync_folders, create_entry, create_file stages."""
        template = orchestrator.load_workflow_template("master-plan-orchestrator")
        stage_names = [s["name"] for s in template["workflow"]["stages"]]
        for required in ["sequence_check", "sync_folders", "create_entry", "create_file"]:
            assert required in stage_names, f"Missing stage: {required}"

    def test_execution_template_has_required_stages(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Execution template must have: gap_analysis, autonomous_execute, refactor_cycle stages."""
        template = orchestrator.load_workflow_template("master-plan-execution")
        stage_names = [s["name"] for s in template["workflow"]["stages"]]
        for required in ["gap_analysis", "autonomous_execute", "refactor_cycle"]:
            assert required in stage_names, f"Missing stage: {required}"


# ============================================================================
# INTEGRATION TESTS: full create + sync cycle
# ============================================================================


class TestCreateAndSyncIntegration:
    """Integration: create_phase triggers sync_phase_folders first."""

    def test_create_phase_syncs_folders_before_creating(
        self, orchestrator_with_planned: CortexMasterPlanOrchestrator
    ) -> None:
        """Phase creation must sync folders first — anomalous phase-100 cannot affect next sequence."""
        req = PhaseCreationRequest(title="New Work", description="desc", priority="P0")
        record = orchestrator_with_planned.create_phase(req)
        # phase-04 is complete → should be synced to completed before computing next
        assert record.sequence == 5  # NOT 101

    def test_registry_remains_consistent_after_create(
        self, orchestrator: CortexMasterPlanOrchestrator
    ) -> None:
        """After create, registry phases list has N+1 entries with no sequence gaps."""
        req = PhaseCreationRequest(title="Seq Test", description="desc", priority="P1")
        orchestrator.create_phase(req)
        registry = orchestrator._load_registry()
        sequences = sorted(p["sequence"] for p in registry["phases"])
        assert sequences == list(range(1, len(sequences) + 1))


# ============================================================================
# NEGATIVE TESTS
# ============================================================================


class TestNegativeCases:
    """Error handling and edge cases."""

    def test_missing_registry_file_raises_lifecycle_error(self, tmp_path: Path) -> None:
        """No cortex-master.yaml → PhaseLifecycleError on init."""
        with pytest.raises(PhaseLifecycleError, match="registry not found"):
            CortexMasterPlanOrchestrator(registry_root=tmp_path)

    def test_create_phase_with_empty_title_raises_value_error(
        self, orchestrator: CortexMasterPlanOrchestrator
    ) -> None:
        with pytest.raises(ValueError, match="title"):
            orchestrator.create_phase(PhaseCreationRequest(title="", description="desc", priority="P0"))

    def test_create_phase_with_invalid_priority_raises_value_error(
        self, orchestrator: CortexMasterPlanOrchestrator
    ) -> None:
        with pytest.raises(ValueError, match="priority"):
            orchestrator.create_phase(PhaseCreationRequest(title="Test", description="desc", priority="INVALID"))

    def test_corrupt_registry_yaml_raises_lifecycle_error(self, tmp_path: Path) -> None:
        """Corrupt YAML raises PhaseLifecycleError, not raw yaml.YAMLError."""
        registry_dir = tmp_path / "cortex-registry"
        registry_dir.mkdir()
        # Use a YAML tab-indentation error which yaml.safe_load raises YAMLError on
        (registry_dir / "cortex-master.yaml").write_text("metadata:\n\t bad_tab_key: broken")
        # SSOT: phases live at cortex-registry/planning/phases/
        (tmp_path / "cortex-registry" / "planning" / "phases" / "planned").mkdir(parents=True)
        (tmp_path / "cortex-registry" / "planning" / "phases" / "completed").mkdir(parents=True)
        (tmp_path / "cortex-registry" / "planning" / "phases" / "deferred").mkdir(parents=True)
        template_dir = tmp_path / "cortex-registry" / "workflows" / "templates" / "lifecycle"
        template_dir.mkdir(parents=True)
        with pytest.raises(PhaseLifecycleError, match="corrupt"):
            CortexMasterPlanOrchestrator(registry_root=tmp_path)

    def test_sync_without_planned_folder_raises_lifecycle_error(self, tmp_path: Path) -> None:
        """Missing planned/ folder raises PhaseLifecycleError during sync."""
        registry_dir = tmp_path / "cortex-registry"
        registry_dir.mkdir()
        (registry_dir / "cortex-master.yaml").write_text(yaml.dump({"metadata": {"total_phases": 0}, "phases": []}))
        # Don't create phases folders
        with pytest.raises(PhaseLifecycleError):
            CortexMasterPlanOrchestrator(registry_root=tmp_path)


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Blind spots and boundary conditions."""

    def test_phase_id_zero_padded_to_two_digits(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Sequences 1-9 must be zero-padded: phase-04 not phase-4."""
        req = PhaseCreationRequest(title="Test", description="desc", priority="P1")
        record = orchestrator.create_phase(req)
        assert record.phase_id == "phase-04"
        assert "-04-" in record.phase_id or record.phase_id.endswith("-04")

    def test_phase_id_three_digits_when_over_99(self, tmp_registry: Path) -> None:
        """Sequence 100+ uses 3-digit zero-padded ID: phase-100."""
        registry_dir = tmp_registry / "cortex-registry"
        phases = [{"id": f"phase-{i:02d}", "status": "complete", "sequence": i} for i in range(1, 100)]
        (registry_dir / "cortex-master.yaml").write_text(yaml.dump({"metadata": {"total_phases": 99}, "phases": phases}))
        orch = CortexMasterPlanOrchestrator(registry_root=tmp_registry)
        req = PhaseCreationRequest(title="Century Phase", description="desc", priority="P1")
        record = orch.create_phase(req)
        assert record.phase_id == "phase-100"

    def test_title_to_file_slug_handles_special_chars(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Title 'CORTEX: Master-Plan (v2)' → cortex-master-plan-v2 slug (CORE-028)."""
        req = PhaseCreationRequest(title="CORTEX: Master-Plan (v2)", description="desc", priority="P1")
        record = orchestrator.create_phase(req)
        assert "cortex-master-plan-v2" in record.file_path.name

    def test_status_only_in_cortex_master_yaml_not_in_phase_file(
        self, orchestrator: CortexMasterPlanOrchestrator
    ) -> None:
        """Phase YAML files must NOT contain authoritative status (per spec §4)."""
        req = PhaseCreationRequest(title="Status Test", description="desc", priority="P1")
        record = orchestrator.create_phase(req)
        phase_content = yaml.safe_load(record.file_path.read_text())
        # Status field in the file is informational only — registry is SSOT
        assert "status_ssot" not in phase_content or phase_content.get("status_ssot") == "cortex-master.yaml"

    def test_concurrent_creates_produce_unique_sequences(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """Rapid sequential creates must produce unique, gapless sequences."""
        records = []
        for i in range(5):
            req = PhaseCreationRequest(title=f"Phase {i}", description="desc", priority="P1")
            records.append(orchestrator.create_phase(req))
        sequences = [r.sequence for r in records]
        assert sequences == list(range(4, 9))  # 4,5,6,7,8


# ============================================================================
# GOLDEN TESTS: End-to-end plan creation + execution workflow
# ============================================================================


class TestGoldenEndToEnd:
    """End-to-end golden tests verifying full create + execute cycle."""

    def test_golden_create_phase_50(self, orchestrator_with_planned: CortexMasterPlanOrchestrator) -> None:
        """
        GOLDEN: Create CortexMasterPlanOrchestrator as phase-50 in the CORTEX registry.
        Verifies: sync → sequence 5 → file created → registry updated.
        """
        req = PhaseCreationRequest(
            title="Cortex Master Plan Orchestrator",
            description="Dedicated orchestrator for CORTEX phase lifecycle management",
            priority="P0",
        )
        record = orchestrator_with_planned.create_phase(req)

        # Sequence = 5 (4 sequential complete phases after sync moves phase-04 back)
        assert record.sequence == 5
        assert record.phase_id == "phase-05"
        assert record.file_path.exists()

        # Registry updated
        registry = orchestrator_with_planned._load_registry()
        ids = [p["id"] for p in registry["phases"]]
        assert "phase-05" in ids

    def test_golden_registry_status_ssot(self, orchestrator: CortexMasterPlanOrchestrator) -> None:
        """
        GOLDEN: cortex-master.yaml is the only status SSOT — phase files are execution specs only.
        """
        req = PhaseCreationRequest(title="SSOT Test Phase", description="desc", priority="P0")
        record = orchestrator.create_phase(req)

        # Status lives in registry only
        registry = orchestrator._load_registry()
        phase_entry = next(p for p in registry["phases"] if p["id"] == record.phase_id)
        assert phase_entry["status"] == "planned"

        # The file has no conflicting status authority
        phase_data = yaml.safe_load(record.file_path.read_text())
        assert phase_data.get("metadata", {}).get("status_authority") in (None, "cortex-master.yaml")
