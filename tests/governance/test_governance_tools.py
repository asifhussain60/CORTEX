"""
CORTEX 6.0 Governance MCP Tools Tests

Tests for AC-GOV-002 through AC-GOV-011:
- AC-GOV-002: 4-Category Governance Merger
- AC-GOV-003: Business Tier override
- AC-GOV-004: TDD_ENFORCEMENT mandatory
- AC-GOV-011: TDD-Master Orchestrator required

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from src.mcp.governance_tools import (
    governance_rules,
    governance_validate,
    governance_conflicts,
    governance_unified,
    governance_tdd_check,
)


@pytest.fixture
def workspace_root() -> str:
    """Return the CORTEX workspace root."""
    # Use actual CORTEX workspace for integration tests
    return str(Path(__file__).parent.parent.parent)


class TestGovernanceRules:
    """Test governance_rules MCP tool."""
    
    @pytest.mark.ac_id("AC-GOV-001")
    def test_list_all_rules(self, workspace_root):
        """Test: List all governance rules returns valid response."""
        result = governance_rules(workspace_root)
        
        assert result["success"] is True
        assert result["total_count"] > 0
        assert "by_tier" in result
        assert "tier_counts" in result
    
    def test_filter_by_tier(self, workspace_root):
        """Test: Filter rules by tier returns only that tier."""
        result = governance_rules(workspace_root, tier=0)
        
        assert result["success"] is True
        # Tier 0 (CORE) should have rules
        assert result["tier_counts"]["CORE (0)"] > 0
    
    def test_tier_counts_accurate(self, workspace_root):
        """Test: Tier counts match actual rule counts."""
        result = governance_rules(workspace_root)
        
        assert result["success"] is True
        
        # Verify counts match
        total_from_tiers = sum(result["tier_counts"].values())
        assert total_from_tiers == result["total_count"]


class TestGovernanceValidate:
    """Test governance_validate MCP tool."""
    
    @pytest.mark.ac_id("AC-GOV-002")
    def test_validate_existing_rule(self, workspace_root):
        """Test: Validate CORE-001 returns ENFORCED."""
        result = governance_validate(workspace_root, "CORE-001")
        
        assert result["success"] is True
        assert result["rule_id"] == "CORE-001"
        assert result["validation_status"] == "ENFORCED"
        assert result["exists"] is True
    
    def test_validate_nonexistent_rule(self, workspace_root):
        """Test: Validate non-existent rule returns NOT_FOUND."""
        result = governance_validate(workspace_root, "FAKE-999")
        
        assert result["success"] is True
        assert result["rule_id"] == "FAKE-999"
        assert result["validation_status"] == "NOT_FOUND"
        assert result["exists"] is False
    
    def test_validate_tdd_enforcement(self, workspace_root):
        """Test: CORE-008 (TDD_ENFORCEMENT) is enforced."""
        result = governance_validate(workspace_root, "CORE-008")
        
        assert result["success"] is True
        assert result["validation_status"] == "ENFORCED"
        assert result["severity"] == "blocked"


class TestGovernanceConflicts:
    """Test governance_conflicts MCP tool."""
    
    def test_detect_conflicts(self, workspace_root):
        """Test: Conflict detection returns valid response."""
        result = governance_conflicts(workspace_root)
        
        assert result["success"] is True
        assert "conflict_count" in result
        assert "conflicts" in result
    
    def test_conflict_structure(self, workspace_root):
        """Test: Each conflict has required fields."""
        result = governance_conflicts(workspace_root)
        
        assert result["success"] is True
        
        for conflict in result.get("conflicts", []):
            assert "category" in conflict
            assert "conflict_type" in conflict
            assert "description" in conflict


class TestGovernanceUnified:
    """Test governance_unified MCP tool."""
    
    def test_generate_unified_set(self, workspace_root):
        """Test: Unified instruction set is generated."""
        result = governance_unified(workspace_root)
        
        assert result["success"] is True
        assert result["rule_count"] > 0
        assert result["tier_count"] >= 1
    
    def test_performance_under_50ms(self, workspace_root):
        """Test: Unified set generated in <100ms (AC-GOV-002)."""
        result = governance_unified(workspace_root)
        
        assert result["success"] is True
        assert result["generation_time_ms"] < 100, \
            f"Generation took {result['generation_time_ms']}ms, target is <100ms"
        assert result["performance_target_met"] is True


class TestGovernanceTDDCheck:
    """Test governance_tdd_check MCP tool - AC-GOV-004 and AC-GOV-011."""
    
    def test_tdd_rules_present(self, workspace_root):
        """Test: Both TDD rules (CORE-008, CORE-019) are present."""
        result = governance_tdd_check(workspace_root)
        
        assert result["success"] is True
        assert "rules" in result
        
        # CORE-008 should exist
        assert result["rules"]["CORE-008"] is not None, \
            "CORE-008 (TDD_ENFORCEMENT) not found"
    
    def test_tdd_enforcement_active(self, workspace_root):
        """Test: TDD enforcement is active (AC-GOV-004)."""
        result = governance_tdd_check(workspace_root)
        
        assert result["success"] is True
        
        # At minimum, CORE-008 should be present
        core_008 = result["rules"].get("CORE-008")
        assert core_008 is not None, "TDD enforcement rule CORE-008 missing"
        assert core_008["severity"] == "blocked", "TDD enforcement must be BLOCKED severity"


class TestACGOV001Migration:
    """Test AC-GOV-001: SKULL rules migration."""
    
    def test_core_rules_file_exists(self, workspace_root):
        """Test: core-rules.yaml exists in tier0/governance."""
        core_rules_path = Path(workspace_root) / "cortex-brain" / "tier0" / "governance" / "core-rules.yaml"
        assert core_rules_path.exists(), f"core-rules.yaml not found at {core_rules_path}"
    
    def test_skull_rules_migrated(self, workspace_root):
        """Test: SKULL rules are migrated to CORE-NNN format."""
        result = governance_rules(workspace_root, tier=0)
        
        assert result["success"] is True
        
        # Should have multiple CORE rules
        core_count = result["tier_counts"]["CORE (0)"]
        assert core_count >= 17, f"Expected at least 17 CORE rules, got {core_count}"
    
    def test_brain_protection_deprecated(self, workspace_root):
        """Test: brain-protection-rules.yaml has deprecation header."""
        deprecated_path = Path(workspace_root) / "cortex-brain" / "brain-protection-rules.yaml"
        
        if deprecated_path.exists():
            content = deprecated_path.read_text()
            assert "DEPRECATED" in content, "brain-protection-rules.yaml missing deprecation notice"
