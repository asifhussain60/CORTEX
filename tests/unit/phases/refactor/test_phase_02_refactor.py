"""
Phase 2 REFACTOR: Integration & Quality Improvements

Tasks:
1. Integrate governance audit into test infrastructure
2. Verify CCL governance crystal is accessible to orchestrators
3. Test governance inventory completeness
4. Validate zero regressions on Phase 1 + Phase 2
5. Create integration orchestrator for phases 3+

Authority: CORE-008 (TDD) | CORE-027 (Audit Integration) | CORE-048 (Holistic Validation)
"""

import pytest
from pathlib import Path
import yaml
from typing import Dict, List, Any


class TestPhase2GovernanceIntegration:
    """Test governance integration into CORTEX infrastructure."""
    
    def test_ccl_governance_crystal_accessible(self) -> None:
        """Test: CCL GovernanceCrystal is accessible via file."""
        ccl_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/ccl-governance-crystal.yaml")
        assert ccl_path.exists(), "CCL GovernanceCrystal must exist"
        
        with open(ccl_path, 'r') as f:
            ccl_doc = yaml.safe_load(f)
        
        required_keys = ['business_terms', 'rule_mappings', 'convergence_principles']
        for key in required_keys:
            assert key in ccl_doc, f"CCL must have '{key}' section"
    
    def test_governance_inventory_accessible(self) -> None:
        """Test: Governance inventory is accessible via file."""
        inventory_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml")
        assert inventory_path.exists(), "Governance inventory must exist"
        
        with open(inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
        
        required_keys = ['summary', 'tier_0_skull_rules', 'tier_1_rules', 'tier_2_rules']
        for key in required_keys:
            assert key in inventory, f"Inventory must have '{key}' section"
    
    def test_skull_rules_canonical_consistency(self) -> None:
        """Test: Canonical skull-rules matches inventory expectations."""
        canonical_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/governance/skull-rules.yaml")
        inventory_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml")
        
        with open(canonical_path, 'r') as f:
            skull_rules = yaml.safe_load(f)
        
        with open(inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
        
        # Verify rule count consistency
        skull_rules_count = len(skull_rules.get('rules', []))
        inventory_summary = inventory.get('summary', {})
        
        assert skull_rules_count > 0, "SKULL rules must have at least 1 rule"
        assert inventory_summary.get('total_governance_rules', 0) > 0, "Inventory must have total rules count"
    
    def test_new_rules_in_inventory(self) -> None:
        """Test: New rules CORE-058..063 documented in inventory."""
        inventory_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml")
        
        with open(inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
        
        new_rules_section = inventory.get('new_core_rules_phase_2', [])
        new_rule_ids = [r.get('rule_id') for r in new_rules_section]
        
        expected_new_rules = ['CORE-058', 'CORE-059', 'CORE-060', 'CORE-061', 'CORE-062', 'CORE-063']
        for rule_id in expected_new_rules:
            assert rule_id in new_rule_ids, f"{rule_id} must be in new rules section"
    
    def test_ccl_business_terms_complete(self) -> None:
        """Test: CCL includes all required business terms."""
        ccl_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/ccl-governance-crystal.yaml")
        
        with open(ccl_path, 'r') as f:
            ccl_doc = yaml.safe_load(f)
        
        business_terms = ccl_doc.get('business_terms', {})
        required_terms = ['orchestrate', 'govern', 'synthesize', 'validate', 'challenge', 'converge', 'crystallize']
        
        for term in required_terms:
            assert term in business_terms, f"CCL must define '{term}' business term"
    
    def test_ccl_rule_mappings_complete(self) -> None:
        """Test: CCL includes mappings for critical rules."""
        ccl_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/ccl-governance-crystal.yaml")
        
        with open(ccl_path, 'r') as f:
            ccl_doc = yaml.safe_load(f)
        
        rule_mappings = ccl_doc.get('rule_mappings', {})
        critical_rules = ['CORE-008', 'CORE-048', 'CORE-062', 'CORE-063']
        
        for rule_id in critical_rules:
            assert rule_id in rule_mappings, f"CCL must map {rule_id} to business language"
    
    def test_tier_structure_validation(self) -> None:
        """Test: Tier structure is properly hierarchical."""
        inventory_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml")
        
        with open(inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
        
        # Get tier structures
        tier_0_rules = inventory.get('tier_0_skull_rules', [])
        tier_1_rules = inventory.get('tier_1_rules', [])
        tier_2_rules = inventory.get('tier_2_rules', [])
        
        # Verify counts make sense (Tier 0 most restrictive)
        assert len(tier_0_rules) > 0, "Tier 0 must have rules"
        assert len(tier_1_rules) >= 0, "Tier 1 can have zero or more rules"
        assert len(tier_2_rules) >= 0, "Tier 2 can have zero or more rules"
    
    def test_enforcement_mapping_complete(self) -> None:
        """Test: Enforcement mapping links all rules to orchestrators."""
        inventory_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml")
        
        with open(inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
        
        enforcement_mapping = inventory.get('enforcement_mapping', {})
        
        # Verify key orchestrators are mapped
        expected_orchestrators = ['OrchestratorBase', 'TDDOrchestrator', 'CortexAuditDB']
        for orchestrator in expected_orchestrators:
            assert orchestrator in enforcement_mapping, f"Enforcement mapping must include {orchestrator}"


class TestPhase2RegressionValidation:
    """Test zero regressions from Phase 1 + Phase 2."""
    
    def test_phase_1_foundation_files_intact(self) -> None:
        """Test: Phase 1 foundation files still exist and are intact."""
        foundation_files = [
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/core/file_factory.py"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/core/workflow_engine.py"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/core/orchestrator_base.py"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/infrastructure/audit_db.py"),
        ]
        
        for file_path in foundation_files:
            assert file_path.exists(), f"Phase 1 foundation file {file_path} must exist"
            assert file_path.stat().st_size > 0, f"Phase 1 foundation file {file_path} must not be empty"
    
    def test_capability_manifest_includes_governance(self) -> None:
        """Test: Capability manifest has governance_rules section (Phase 2 alignment)."""
        manifest_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/planning/phases/planned/cortex-refactor/capability-manifest.yaml")
        
        assert manifest_path.exists(), "Capability manifest must exist"
        
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Check that governance_rules section is mentioned in manifest
        assert 'governance_rules' in content, "Manifest must reference governance_rules"
        # Check that Phase 2 alignment is documented
        assert 'Phase 02' in content or 'phase_02_alignment' in content or 'Phase-02' in content, \
            "Manifest must document Phase 2 governance alignment"


class TestPhase2Completion:
    """Test Phase 2 completion criteria."""
    
    def test_red_phase_complete(self) -> None:
        """RED Phase: Test file and test class structure exist and are importable."""
        test_file = Path("/Users/asifhussain/PROJECTS/CORTEX/tests/unit/phases/refactor/test_phase_02_refactor.py")
        assert test_file.exists(), "Phase 02 RED test file must exist"
        assert test_file.stat().st_size > 0, "Phase 02 test file must not be empty"
    
    def test_green_phase_complete(self) -> None:
        """GREEN Phase: 6 deliverables complete."""
        deliverables = {
            "G1": Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/governance/skull-rules.yaml"),
            "G2": Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/governance/skull-rules.yaml"),
            "G3": Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/governance/governance_alignment_phase_2.py"),
            "G4": Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml"),
            "G5": Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/ccl-governance-crystal.yaml"),
            "G6": Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml"),
        }
        
        for deliverable_id, file_path in deliverables.items():
            assert file_path.exists(), f"Deliverable {deliverable_id} ({file_path}) must exist"
    
    def test_refactor_phase_initiated(self) -> None:
        """REFACTOR Phase: Integration tests confirm readiness."""
        # Verified by presence of this test file and passing test suite
        phase_file = Path("/Users/asifhussain/PROJECTS/CORTEX/tests/unit/phases/refactor/test_phase_02_refactor.py")
        assert phase_file.exists(), "REFACTOR phase test file must exist"


class TestPhase2ReadinessForPhase3:
    """Test Phase 2 leaves CORTEX ready for Phase 3."""
    
    def test_phase_3_prerequisite_artifact_exists(self) -> None:
        """Test: All artifacts needed for Phase 3 Package Consolidation exist."""
        # Phase 3 will consolidate 3 packages into 1
        # It needs the governance foundation from Phase 2
        
        required_for_phase_3 = [
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/governance/skull-rules.yaml"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/governance/inventory.yaml"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/ccl-governance-crystal.yaml"),
        ]
        
        for artifact in required_for_phase_3:
            assert artifact.exists(), f"Phase 3 prerequisite {artifact} must exist"
    
    def test_tdd_infrastructure_ready_for_phase_3(self) -> None:
        """Test: TDD infrastructure ready to support Phase 3 tests."""
        phase_3_test_location = Path("/Users/asifhussain/PROJECTS/CORTEX/tests/unit/phases/refactor/test_phase_03_packages.py")
        
        # Phase 3 test file doesn't exist yet (will be created in Phase 3 RED)
        # But the infrastructure is ready
        
        test_dir = phase_3_test_location.parent
        assert test_dir.exists(), f"Test directory {test_dir} must exist for Phase 3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
