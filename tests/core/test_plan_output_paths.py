"""
Plan Output Paths — Canonical Location Tests

AC_START: AC-FIX-PLAN-PATHS-001
Bug: Plans not created in cortex-registry due to wrong default paths.
Violations: V1 (PhaseManager active→planned), V2 (PhaseCreator CWD default),
            V3 (PlanRegistry active→planning/phases/planned),
            V4 (KnowledgeSynthesizer wrong root), V5 (AbsorptionGate wrong root)
Authority: cortex-architect.prompt.md — all planning/YAML artifacts MUST be
           written only to cortex-registry/.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml


# ─────────────────────────────────────────────────────────────────────────────
# V1 — PhaseManager must use phases/planned/, NOT phases/active/
# ─────────────────────────────────────────────────────────────────────────────

class TestPhaseManagerUsesPlannedDir:
    """PhaseManager.active_phases_dir must resolve to phases/planned/."""

    def test_active_phases_dir_is_planned_not_active(self, tmp_path: Path) -> None:
        """active_phases_dir must point to phases/planned/, not phases/active/."""
        from cortex.core.registry.phase_manager import PhaseManager

        registry_root = tmp_path / "cortex-registry" / "_cortex-master"
        (registry_root / "phases" / "planned").mkdir(parents=True)
        (registry_root / "phases" / "completed").mkdir(parents=True)
        (registry_root / "phases" / "deprecated").mkdir(parents=True)
        (registry_root / "index.yaml").write_text("active_phases: []\nstatistics: {}")

        manager = PhaseManager(registry_root=str(registry_root))

        # Check the final path component directly (avoids tmpdir name matching)
        assert manager.active_phases_dir.name == "planned", (
            f"active_phases_dir.name must be 'planned', got: {manager.active_phases_dir.name!r}"
        )
        assert manager.active_phases_dir.name != "active", (
            f"active_phases_dir.name must NOT be 'active', got: {manager.active_phases_dir.name!r}"
        )

    def test_phase_yaml_saved_to_planned_folder(self, tmp_path: Path) -> None:
        """Saved phase YAML must land in phases/planned/, not phases/active/."""
        from cortex.core.registry.phase_manager import PhaseManager

        registry_root = tmp_path / "cortex-registry" / "_cortex-master"
        planned_dir = registry_root / "phases" / "planned"
        planned_dir.mkdir(parents=True)
        (registry_root / "phases" / "completed").mkdir(parents=True)
        (registry_root / "phases" / "deprecated").mkdir(parents=True)
        (registry_root / "index.yaml").write_text(
            "active_phases: []\nstatistics: {completed_phases: 0, active_phases: 0}"
        )

        manager = PhaseManager(registry_root=str(registry_root))
        data = {"id": "phase-test", "title": "Test", "status": "planned"}
        manager._save_phase_yaml(data, "phase-test-fixture.yaml", folder="active")

        # The file must land under planned/, NOT a new active/ dir
        assert (planned_dir / "phase-test-fixture.yaml").exists(), (
            "Phase YAML was not saved to planned/ directory"
        )
        # active/ must NOT have been created
        assert not (registry_root / "phases" / "active").exists(), (
            "phases/active/ was created — it must not exist; use planned/"
        )

    def test_index_file_reference_uses_planned(self, tmp_path: Path) -> None:
        """Index file entry must reference phases/planned/... not phases/active/..."""
        from cortex.core.registry.phase_manager import PhaseManager

        registry_root = tmp_path / "cortex-registry" / "_cortex-master"
        (registry_root / "phases" / "planned").mkdir(parents=True)
        (registry_root / "phases" / "completed").mkdir(parents=True)
        (registry_root / "phases" / "deprecated").mkdir(parents=True)
        index_data = {"active_phases": [], "statistics": {"completed_phases": 0, "active_phases": 0}}
        (registry_root / "index.yaml").write_text(yaml.dump(index_data))

        manager = PhaseManager(registry_root=str(registry_root))
        spec = {
            "id": "phase-test",
            "name": "Test Phase",
            "status": "planned",
            "priority": "P1",
            "roi": 7.0,
            "description": "Fixture test phase",
            "problem": {"current_state": "X", "gaps": [], "impact": "Y"},
            "solution": {"approach": "Z", "benefits": []},
            "deliverables": ["D1", "D2"],
        }
        manager.create_phase(spec)

        idx = yaml.safe_load((registry_root / "index.yaml").read_text())
        entries = idx.get("active_phases", [])
        assert entries, "No entry in index.yaml after create_phase"

        file_ref = entries[0].get("file", "")
        assert "planned" in file_ref, (
            f"Index 'file' key must reference 'planned/', got: {file_ref!r}"
        )
        assert "active" not in file_ref, (
            f"Index 'file' key must NOT reference 'active/', got: {file_ref!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# V2 — PhaseCreator CLI must default output to cortex-registry, not CWD
# ─────────────────────────────────────────────────────────────────────────────

class TestPhaseCreatorDefaultOutputPath:
    """CLI phase_creator must write to cortex-registry, not CWD."""

    def test_default_output_resolves_into_cortex_registry(self, tmp_path: Path) -> None:
        """When --output is omitted, file must go into cortex-registry/_cortex-master/phases/planned/."""
        from cortex.cli.phase_creator import PhaseCreator

        planned_dir = tmp_path / "cortex-registry" / "_cortex-master" / "phases" / "planned"
        planned_dir.mkdir(parents=True)

        creator = PhaseCreator(cortex_root=tmp_path)
        spec = creator.create_from_template("standard", enhancement_id="ENH-999", title="Test")

        # Resolve default output path the same way the CLI command will
        default_path = creator.default_output_path("ENH-999")

        assert "cortex-registry" in str(default_path), (
            f"Default output path must be inside cortex-registry, got: {default_path}"
        )
        assert "ENH-999".lower() in str(default_path).lower() or "enh-999" in str(default_path).lower(), (
            f"Default path must include phase id, got: {default_path}"
        )

    def test_save_spec_writes_into_registry_by_default(self, tmp_path: Path) -> None:
        """save_spec with default path must write into cortex-registry, not CWD."""
        from cortex.cli.phase_creator import PhaseCreator

        planned_dir = tmp_path / "cortex-registry" / "_cortex-master" / "phases" / "planned"
        planned_dir.mkdir(parents=True)

        creator = PhaseCreator(cortex_root=tmp_path)
        spec = creator.create_from_template("standard", enhancement_id="ENH-998", title="Registry Test")

        output_path = creator.default_output_path("ENH-998")
        creator.save_spec(spec, output_path)

        assert output_path.exists(), f"Spec not written to {output_path}"
        # Must not have written to CWD
        cwd_file = Path("enh-998.yaml")
        assert not cwd_file.exists(), "File was written to CWD — must go to cortex-registry instead"


# ─────────────────────────────────────────────────────────────────────────────
# V3 — PlanRegistry must write to planning/phases/planned/, not planning/active/
# ─────────────────────────────────────────────────────────────────────────────

class TestPlanRegistryCanonicalPath:
    """PlanRegistry must align with cortex-registry/planning/phases/planned/."""

    def test_active_path_points_to_phases_planned(self, tmp_path: Path) -> None:
        """active_path must be planning/phases/planned/, not planning/active/."""
        from cortex.core.registry.plan_registry import PlanRegistry

        planning_root = tmp_path / "cortex-registry" / "planning"
        registry = PlanRegistry(registry_path=str(planning_root))

        assert "phases" in str(registry.active_path), (
            f"active_path must contain 'phases/', got: {registry.active_path}"
        )
        assert "planned" in str(registry.active_path), (
            f"active_path must contain 'planned', got: {registry.active_path}"
        )
        assert str(registry.active_path).endswith("planned") or "planned" in str(registry.active_path), (
            f"active_path must point to planning/phases/planned/, got: {registry.active_path}"
        )

    def test_no_bare_active_dir_created(self, tmp_path: Path) -> None:
        """PlanRegistry must NOT create a bare active/ dir outside phases/."""
        from cortex.core.registry.plan_registry import PlanRegistry

        planning_root = tmp_path / "cortex-registry" / "planning"
        PlanRegistry(registry_path=str(planning_root))

        bare_active = planning_root / "active"
        assert not bare_active.exists(), (
            f"Bare planning/active/ was created — must use planning/phases/planned/ instead"
        )


# ─────────────────────────────────────────────────────────────────────────────
# V4 — KnowledgeSynthesizer must default to cortex-registry/knowledge/
# ─────────────────────────────────────────────────────────────────────────────

class TestKnowledgeSynthesizerOutputPath:
    """KnowledgeSynthesizer default root must be cortex-registry/knowledge/."""

    def test_default_knowledge_root_is_in_registry(self) -> None:
        """Default knowledge_root must be cortex-registry/knowledge/, not cortex/knowledge/."""
        from cortex.intelligence.learning.knowledge_synthesizer import KnowledgeSynthesizer

        synth = KnowledgeSynthesizer()

        assert "cortex-registry" in str(synth.knowledge_root), (
            f"KnowledgeSynthesizer.knowledge_root must be in cortex-registry/, "
            f"got: {synth.knowledge_root}"
        )
        assert "cortex/knowledge" not in str(synth.knowledge_root).replace("cortex-registry", ""), (
            f"KnowledgeSynthesizer must NOT write into cortex/knowledge/ (Python package), "
            f"got: {synth.knowledge_root}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# V5 — AbsorptionGate must default tier3 path to cortex-registry/knowledge/
# ─────────────────────────────────────────────────────────────────────────────

class TestAbsorptionGateTier3Path:
    """AbsorptionGate tier3_path must default to cortex-registry/knowledge/."""

    def test_default_tier3_path_is_in_registry(self) -> None:
        """tier3_path must be cortex-registry/knowledge/..., not cortex/knowledge/..."""
        from cortex.orchestrators.workflow.absorption_gate import AbsorptionGate

        gate = AbsorptionGate()

        assert "cortex-registry" in str(gate.tier3_path), (
            f"AbsorptionGate.tier3_path must be in cortex-registry/, "
            f"got: {gate.tier3_path}"
        )
        assert "cortex/knowledge" not in str(gate.tier3_path).replace("cortex-registry", ""), (
            f"AbsorptionGate must NOT write into cortex/knowledge/ (Python package), "
            f"got: {gate.tier3_path}"
        )


# AC_COMPLETE: AC-FIX-PLAN-PATHS-001 ✅
