"""
Phase 103 Golden Tests: Registry Structure Validation

Purpose: Enforce CURRENT registry structure with separation of concerns.

Author: Asif Hussain
Date: 2026-02-17
"""

import pytest
from pathlib import Path
import yaml


class TestPhase103RegistryStructure:
    """Validate Phase 103 registry consolidation maintains separation of concerns."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.registry = Path(__file__).parent.parent.parent.parent / "cortex-registry"
        assert self.registry.exists(), f"Registry not found at {self.registry}"

    def test_registry_core_structure(self):
        """Verify cortex-registry/core/ structure exists."""
        required_paths = [
            self.registry / "core" / "governance",
            self.registry / "core" / "config",
            self.registry / "core" / "specifications",
            self.registry / "core" / "wiring",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing core path: {path}"

    def test_cortex_master_phases_structure(self):
        """Verify _cortex-master/phases/ structure for CORTEX internal development."""
        required_paths = [
            self.registry / "_cortex-master" / "phases" / "planned",
            self.registry / "_cortex-master" / "phases" / "completed",
            self.registry / "_cortex-master" / "phases" / "deferred",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing _cortex-master/phases path: {path}"

    def test_planning_folder_exists(self):
        """Verify planning/ folder exists for user production planning."""
        required_paths = [
            self.registry / "planning" / "phases",
            self.registry / "planning" / "phases" / "planned",
            self.registry / "planning" / "phases" / "completed",
            self.registry / "planning" / "phases" / "deferred",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing planning path: {path}"

    def test_artifacts_structure(self):
        """Verify artifacts/ structure for templates and workflows."""
        required_paths = [
            self.registry / "artifacts" / "templates",
            self.registry / "artifacts" / "templates" / "documentation",
            self.registry / "artifacts" / "templates" / "phases",
            self.registry / "artifacts" / "templates" / "responses",
            self.registry / "artifacts" / "workflows",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing artifacts path: {path}"

    def test_integration_structure(self):
        """Verify integration/ structure for interaction patterns."""
        required_paths = [
            self.registry / "integration" / "interaction",
            self.registry / "integration" / "patterns",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing integration path: {path}"

    def test_knowledge_base_structure(self):
        """Verify knowledge/ structure for architecture and security KB."""
        required_paths = [
            self.registry / "knowledge" / "architecture",
            self.registry / "knowledge" / "security",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing knowledge path: {path}"

    def test_metrics_structure(self):
        """Verify metrics/ structure for baselines, dashboards, reports, status."""
        required_paths = [
            self.registry / "metrics" / "baselines",
            self.registry / "metrics" / "dashboards",
            self.registry / "metrics" / "reports",
            self.registry / "metrics" / "status",
        ]
        for path in required_paths:
            assert path.exists(), f"Missing metrics path: {path}"

    def test_cortex_master_yaml_exists(self):
        """Verify cortex-master.yaml exists as the main registry index."""
        cortex_master = self.registry / "cortex-master.yaml"
        assert cortex_master.exists(), "Missing cortex-master.yaml"
        with open(cortex_master) as f:
            data = yaml.safe_load(f)
        assert data is not None, "cortex-master.yaml is empty or invalid"
        assert "metadata" in data, "cortex-master.yaml missing metadata section"

    def test_phase_104_in_planned(self):
        """Verify Phase 104 YAML is in _cortex-master/phases/planned/."""
        phase_104_path = (
            self.registry / "_cortex-master" / "phases" / "planned" 
            / "phase-104-registry-intelligence-consolidation.yaml"
        )
        assert phase_104_path.exists(), "Phase 104 missing from _cortex-master/phases/planned/"

    def test_completed_phases_exist(self):
        """Verify completed phases exist in _cortex-master/phases/completed/."""
        completed_path = self.registry / "_cortex-master" / "phases" / "completed"
        completed_files = list(completed_path.glob("*.yaml"))
        assert len(completed_files) > 0, "No completed phases found"

    def test_no_cortex_phases_in_user_planning(self):
        """Verify user planning phase files remain under planning/phases/."""
        planning_phases = self.registry / "planning" / "phases"
        assert planning_phases.exists(), "Missing planning/phases"
        phase_files = list(planning_phases.glob("**/phase-*.yaml"))
        assert len(phase_files) > 0, "Expected planning/phases to contain phase YAMLs"
        assert all("_cortex-master" not in str(path) for path in phase_files)

    def test_core_governance_gitkeep(self):
        """Verify core/governance has at least a .gitkeep or governance files."""
        governance_path = self.registry / "core" / "governance"
        files = list(governance_path.iterdir())
        assert len(files) > 0, "core/governance is empty"

    def test_separation_of_concerns(self):
        """Verify clear separation between CORTEX internal and user structures."""
        cortex_internal = self.registry / "_cortex-master"
        assert cortex_internal.exists(), "Missing _cortex-master/"
        user_planning = self.registry / "planning"
        assert user_planning.exists(), "Missing planning/"
        core = self.registry / "core"
        assert core.exists(), "Missing core/"
        assert not (cortex_internal / "core").exists(), "_cortex-master/ should NOT have core/"
        assert not (user_planning / "governance").exists(), "planning/ should NOT have governance"


class TestPhase103PythonReferences:
    """Validate Python code references align with current registry structure."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.cortex_root = Path(__file__).parent.parent.parent.parent
        self.registry = self.cortex_root / "cortex-registry"

    def test_registry_exists(self):
        """Verify registry exists."""
        assert self.registry.exists()
        assert (self.registry / "_cortex-master").exists()
        assert (self.registry / "core").exists()
        assert (self.registry / "planning").exists()

    def test_cortex_master_yaml_valid(self):
        """Verify cortex-master.yaml is valid YAML with expected structure."""
        cortex_master = self.registry / "cortex-master.yaml"
        assert cortex_master.exists()
        with open(cortex_master) as f:
            data = yaml.safe_load(f)
        for key in ["metadata", "phase_status"]:
            assert key in data, f"cortex-master.yaml missing '{key}' section"


class TestRegistryYAMLFolderStructure:
    """Validate YAML files are created in correct registry folders."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.registry = Path(__file__).parent.parent.parent.parent / "cortex-registry"

    def test_all_top_level_folders_exist(self):
        """Verify all expected top-level folders exist in cortex-registry."""
        expected_folders = [
            "_cortex-master", "artifacts", "core", "integration",
            "knowledge", "metrics", "planning",
        ]
        for folder in expected_folders:
            folder_path = self.registry / folder
            assert folder_path.exists(), f"Missing top-level folder: {folder}"
            assert folder_path.is_dir(), f"{folder} is not a directory"

    def test_gitkeep_files_in_empty_folders(self):
        """Verify .gitkeep files exist in otherwise empty structural folders."""
        structural_folders = [
            self.registry / "core" / "config",
            self.registry / "core" / "governance",
            self.registry / "core" / "specifications",
            self.registry / "core" / "wiring",
            self.registry / "integration" / "interaction",
            self.registry / "integration" / "patterns",
            self.registry / "artifacts" / "workflows",
            self.registry / "knowledge" / "architecture",
            self.registry / "knowledge" / "security",
            self.registry / "metrics" / "baselines",
            self.registry / "metrics" / "dashboards",
            self.registry / "metrics" / "reports",
            self.registry / "metrics" / "status",
        ]
        for folder in structural_folders:
            assert folder.exists(), f"Structural folder missing: {folder}"
            files = list(folder.iterdir())
            assert len(files) > 0 or (folder / ".gitkeep").exists(), f"Folder {folder} empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
