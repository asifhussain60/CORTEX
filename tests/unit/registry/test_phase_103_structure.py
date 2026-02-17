"""
Phase 103 Golden Tests: Registry Structure Validation

Purpose: Enforce separation between CORTEX internal development (_cortex-master/)
         and user production repo planning (planning/).

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
    
    def test_cortex_master_structure_preserved(self):
        """Verify _cortex-master/ internal structure remains intact for CORTEX development."""
        required_paths = [
            self.registry / "_cortex-master" / "core" / "governance",
            self.registry / "_cortex-master" / "core" / "config",
            self.registry / "_cortex-master" / "core" / "meta",
            self.registry / "_cortex-master" / "core" / "specifications",
            self.registry / "_cortex-master" / "core" / "wiring",
            self.registry / "_cortex-master" / "phases" / "planned",
            self.registry / "_cortex-master" / "phases" / "completed",
            self.registry / "_cortex-master" / "phases" / "deferred",
            self.registry / "_cortex-master" / "knowledge",
            self.registry / "_cortex-master" / "baselines",
            self.registry / "_cortex-master" / "dashboard" / "data",
        ]
        
        for path in required_paths:
            assert path.exists(), f"Missing _cortex-master path: {path}"
    
    def test_cortex_master_core_files_exist(self):
        """Verify critical CORTEX core files are preserved."""
        critical_files = [
            self.registry / "_cortex-master" / "core" / "governance" / "core-rules.yaml",
            self.registry / "_cortex-master" / "core" / "config" / "master-plan.yaml",
            self.registry / "_cortex-master" / "core" / "meta" / "modes.yaml",
            self.registry / "_cortex-master" / "core" / "meta" / "response-format.yaml",
            self.registry / "_cortex-master" / "core" / "specifications" / "orchestrator-dispatch.yaml",
        ]
        
        for file_path in critical_files:
            assert file_path.exists(), f"Missing critical file: {file_path}"
    
    def test_cortex_phase_103_in_correct_location(self):
        """Verify Phase 103 YAML stays in _cortex-master/phases/planned/."""
        phase_103_path = self.registry / "_cortex-master" / "phases" / "planned" / "phase-103-registry-intelligence-consolidation.yaml"
        assert phase_103_path.exists(), "Phase 103 missing from _cortex-master/phases/planned/"
    
    def test_planning_folder_separation(self):
        """Verify planning/ folder is separate from _cortex-master/ for user work."""
        # User-facing planning structure
        user_paths = [
            self.registry / "planning" / "phases",
            self.registry / "planning" / "workflows",
        ]
        
        for path in user_paths:
            assert path.exists(), f"Missing user planning path: {path}"
        
        # Verify CORTEX internal phases stay in _cortex-master/
        cortex_phase = self.registry / "_cortex-master" / "phases" / "planned" / "phase-103-registry-intelligence-consolidation.yaml"
        assert cortex_phase.exists(), "CORTEX internal phase missing from _cortex-master/phases/planned/"
        
        # Verify user phases (if any) are in planning/
        # This is expected to be empty initially until user creates plans
        planning_phases = self.registry / "planning" / "phases"
        if planning_phases.exists():
            # Check it doesn't contain CORTEX-numbered phases (phase-XXX pattern)
            cortex_phases_in_planning = list(planning_phases.glob("phase-*.yaml"))
            assert len(cortex_phases_in_planning) == 0, f"Found CORTEX phases in user planning/: {cortex_phases_in_planning}"
    
    def test_no_duplicate_governance_rules(self):
        """Ensure governance rules exist only in _cortex-master/core/governance."""
        cortex_gov = self.registry / "_cortex-master" / "core" / "governance"
        user_gov = self.registry / "governance"
        
        assert cortex_gov.exists(), "Missing CORTEX governance in _cortex-master/"
        assert (cortex_gov / "core-rules.yaml").exists(), "Missing core-rules.yaml"
        
        # User governance should be for their repos, not CORTEX internals
        # If user_gov exists, it should contain user-specific rules, not CORTEX development rules
        if user_gov.exists() and (user_gov / "rules.yaml").exists():
            cortex_rules_file = cortex_gov / "core-rules.yaml"
            user_rules_file = user_gov / "rules.yaml"
            
            # Read YAML to check for rule ID overlap (not line-by-line text)
            with open(cortex_rules_file) as f:
                cortex_data = yaml.safe_load(f) or {}
            with open(user_rules_file) as f:
                user_data = yaml.safe_load(f) or {}
            
            # Extract rule IDs (assuming format: rules: [{id: "CORE-001"}, ...])
            cortex_ids = {r.get("id", "") for r in cortex_data.get("rules", [])}
            user_ids = {r.get("id", "") for r in user_data.get("rules", [])}
            
            overlap = cortex_ids & user_ids
            assert len(overlap) == 0, f"Found duplicate rule IDs: {overlap}"
    
    def test_knowledge_base_structure(self):
        """Verify knowledge structure for CORTEX internal KB in _cortex-master."""
        # CORTEX internal knowledge stays in _cortex-master/knowledge/
        cortex_kb = self.registry / "_cortex-master" / "knowledge"
        assert cortex_kb.exists(), "Missing _cortex-master/knowledge/ folder"
        
        required_kb_folders = [
            "architecture",
            "cloud",
            "security",
            "testing",
            "engineering",
            "config",
        ]
        
        for folder in required_kb_folders:
            path = cortex_kb / folder
            assert path.exists(), f"Missing _cortex-master/knowledge/{folder}"
        
        # User knowledge-base/ is separate (for onboarded repos)
        user_kb = self.registry / "knowledge-base"
        if user_kb.exists():
            # Should NOT contain CORTEX development KB
            assert not (user_kb / "config" / "orchestrator_specs.json").exists(), \
                "CORTEX orchestrator specs leaked into user knowledge-base/"
    
    def test_cortex_status_files_location(self):
        """Verify CORTEX status files remain in _cortex-master/."""
        status_files = list(self.registry.glob("_cortex-master/CORTEX-STATUS-*.yaml"))
        assert len(status_files) > 0, "Missing CORTEX status files in _cortex-master/"
        
        # Should NOT be in root or user-facing folders
        root_status = list(self.registry.glob("CORTEX-STATUS-*.yaml"))
        assert len(root_status) == 0, "CORTEX status files leaked to registry root"
    
    def test_baselines_in_cortex_master(self):
        """Verify CORTEX baselines stay in _cortex-master/baselines/."""
        baselines = self.registry / "_cortex-master" / "baselines"
        assert baselines.exists(), "Missing _cortex-master/baselines/"
        
        baseline_files = list(baselines.glob("*.json"))
        assert len(baseline_files) > 0, "No baseline files found in _cortex-master/baselines/"
    
    def test_master_index_location(self):
        """Verify master-index.yaml is in _cortex-master/."""
        master_index = self.registry / "_cortex-master" / "master-index.yaml"
        assert master_index.exists(), "Missing _cortex-master/master-index.yaml"
    
    def test_no_planning_in_cortex_master(self):
        """Ensure _cortex-master/ doesn't contain user planning artifacts."""
        forbidden_paths = [
            self.registry / "_cortex-master" / "planning",
            self.registry / "_cortex-master" / "user-phases",
            self.registry / "_cortex-master" / "production-plans",
        ]
        
        for path in forbidden_paths:
            assert not path.exists(), f"Found forbidden user planning path in _cortex-master/: {path}"
    
    def test_planning_folder_exists_for_users(self):
        """Verify planning/ folder exists for user production work."""
        planning = self.registry / "planning"
        assert planning.exists(), "Missing planning/ folder for user work"
        
        # Should have basic structure
        assert (planning / "phases").exists(), "Missing planning/phases/"
        assert (planning / "workflows").exists(), "Missing planning/workflows/"


class TestPhase103PythonReferences:
    """Validate Python code references updated correctly."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.cortex_root = Path(__file__).parent.parent.parent.parent
        self.registry = self.cortex_root / "cortex-registry"
    
    def test_no_old_cortex_master_imports(self):
        """Check Python files don't use old _cortex-master paths incorrectly."""
        # This is a smoke test - actual validation would require parsing imports
        # For now, we just ensure the registry structure is correct
        assert self.registry.exists()
        assert (self.registry / "_cortex-master").exists()
        
        # If there are Python files that load registry paths, they should use:
        # "cortex-registry/_cortex-master/..." for CORTEX internal
        # "cortex-registry/planning/..." for user work
        pass  # Full validation would scan all .py files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
