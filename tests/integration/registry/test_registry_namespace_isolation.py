"""
Golden Tests for CORTEX Registry Structure Validation

Authority: Phase 103 Recovery - Registry Structure Correction
Created: 2026-02-17
Updated: 2026-02-17 - Aligned to current registry structure
Purpose: Enforce semantic separation between CORTEX meta-system and user repository plans

Current Structure:
- cortex-registry/_cortex-master/phases/ - CORTEX internal phase tracking
- cortex-registry/planning/phases/ - User production repository plans
- cortex-registry/core/ - Shared governance, config, wiring
"""

import pytest
from pathlib import Path
import yaml
import re


class TestCortexMasterNamespaceIsolation:
    """Test suite ensuring _cortex-master contains only CORTEX meta-system content."""
    
    CORTEX_MASTER_ROOT = Path("cortex-registry/_cortex-master")
    
    def test_cortex_master_directory_exists(self):
        """Verify _cortex-master directory is preserved."""
        assert self.CORTEX_MASTER_ROOT.exists(), \
            "_cortex-master directory missing (critical namespace separation lost)"
        assert self.CORTEX_MASTER_ROOT.is_dir(), \
            "_cortex-master should be directory, not file"
    
    def test_cortex_phases_directory_structure(self):
        """Verify phases directory structure in _cortex-master."""
        phases_root = self.CORTEX_MASTER_ROOT / "phases"
        assert phases_root.exists(), "_cortex-master/phases missing"
        
        expected_subdirs = ["planned", "completed", "deferred"]
        for subdir in expected_subdirs:
            path = phases_root / subdir
            assert path.exists(), f"Missing phases/{subdir}"


class TestUserPlanningNamespaceIsolation:
    """Test suite ensuring planning/ contains only user repository plans."""
    
    PLANNING_ROOT = Path("cortex-registry/planning")
    
    def test_planning_directory_exists(self):
        """Verify planning/ directory exists for user repository plans."""
        assert self.PLANNING_ROOT.exists(), \
            "planning/ directory missing (required for user repo plans)"
        assert self.PLANNING_ROOT.is_dir(), \
            "planning/ should be directory, not file"
    
    def test_planning_phases_structure(self):
        """Verify planning/phases directory structure."""
        phases_root = self.PLANNING_ROOT / "phases"
        assert phases_root.exists(), "planning/phases missing"
        
        expected_subdirs = ["planned", "completed", "deferred"]
        for subdir in expected_subdirs:
            path = phases_root / subdir
            assert path.exists(), f"Missing planning/phases/{subdir}"
    
    def test_planning_phases_are_valid_yaml(self):
        """Verify all phase YAML files in planning/phases are valid YAML.

        planning/phases/ is the canonical SSOT for CORTEX phase detail files
        (per golden tests for phase-50, phase-76, phase-77). This test enforces
        that every file present is parseable — not that the directory is empty.
        """
        phases_dirs = [
            self.PLANNING_ROOT / "phases" / "planned",
            self.PLANNING_ROOT / "phases" / "completed",
            self.PLANNING_ROOT / "phases" / "deferred",
        ]

        for phases_dir in phases_dirs:
            if not phases_dir.exists():
                continue
            for yaml_file in phases_dir.glob("*.yaml"):
                with open(yaml_file, "r") as f:
                    try:
                        data = yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        raise AssertionError(
                            f"Invalid YAML in {yaml_file.name}: {e}"
                        ) from e
                assert data is not None, f"Empty phase file: {yaml_file.name}"


class TestPhaseFileDistribution:
    """Test suite validating phase file counts and distribution."""
    
    def test_cortex_master_has_phases(self):
        """Verify _cortex-master has development phases."""
        phases_root = Path("cortex-registry/_cortex-master/phases")
        assert phases_root.exists(), "Missing _cortex-master/phases"
        
        all_phases = list(phases_root.glob("**/*.yaml"))
        assert len(all_phases) > 0, "No phases found in _cortex-master/phases"
        
        print(f"✅ CORTEX _cortex-master phases: {len(all_phases)}")
    
    def test_completed_phases_exist(self):
        """Verify completed phases exist in _cortex-master/phases/completed/."""
        completed = Path("cortex-registry/_cortex-master/phases/completed")
        assert completed.exists(), "Missing _cortex-master/phases/completed"
        
        completed_files = list(completed.glob("*.yaml"))
        assert len(completed_files) > 0, "No completed phases found"
        
        print(f"✅ Completed phases: {len(completed_files)}")
    
    def test_phase_distribution_logged(self):
        """Log phase distribution across namespaces for audit."""
        cortex_planned = len(list(Path("cortex-registry/_cortex-master/phases/planned").glob("*.yaml")))
        cortex_completed = len(list(Path("cortex-registry/_cortex-master/phases/completed").glob("*.yaml")))
        cortex_deferred = len(list(Path("cortex-registry/_cortex-master/phases/deferred").glob("*.yaml")))
        
        total_phases = cortex_planned + cortex_completed + cortex_deferred
        
        print(f"\n📊 Phase Distribution Audit:")
        print(f"  CORTEX Planned: {cortex_planned}")
        print(f"  CORTEX Completed: {cortex_completed}")
        print(f"  CORTEX Deferred: {cortex_deferred}")
        print(f"  Total: {total_phases}")
        
        assert total_phases > 0, "No CORTEX phases found (critical issue)"


class TestCoreStructure:
    """Test suite for cortex-registry/core/ structure."""
    
    CORE_ROOT = Path("cortex-registry/core")
    
    def test_core_directory_exists(self):
        """Verify core/ directory exists."""
        assert self.CORE_ROOT.exists(), "core/ directory missing"
        assert self.CORE_ROOT.is_dir(), "core/ should be directory"
    
    def test_core_subdirectories_exist(self):
        """Verify core subdirectories exist.

        Note: governance/ and config/ were merged to top-level namespaces by
        Phase 108 (GAP-108-04, GAP-108-05) and no longer live under core/.
        """
        expected = ["specifications", "wiring"]
        for subdir in expected:
            path = self.CORE_ROOT / subdir
            assert path.exists(), f"Missing core/{subdir}"


class TestAccessPatternEnforcement:
    """Test suite enforcing agent write permission rules."""
    
    def test_cortex_master_yaml_exists(self):
        """Verify cortex-master.yaml exists as main index."""
        index = Path("cortex-registry/cortex-master.yaml")
        assert index.exists(), "cortex-master.yaml missing"
        
        with open(index, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "cortex-master.yaml is empty"
        assert "metadata" in data, "Missing metadata section"
    
    def test_cortex_architect_prompt_exists(self):
        """Verify cortex-architect.prompt.md exists."""
        prompt = Path(".github/prompts/cortex-architect.prompt.md")
        assert prompt.exists(), "cortex-architect.prompt.md not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
