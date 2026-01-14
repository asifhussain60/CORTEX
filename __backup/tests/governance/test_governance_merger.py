"""
Tests for GovernanceMerger - 4-Category Governance System.

This module tests the governance merger that combines rules from:
1. CORTEX Tier 0 (Core brain protection - SKULL rules)
2. Business Tier 0 (Company compliance rules)
3. Company Best Practices (Engineering standards)
4. Knowledge Best Practices (Learned patterns)

Author: CORTEX feat03-governance Phase 2
Created: 2026-01-08
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Import the classes (now implemented)
from src.orchestrators.core.governance_merger import (
    GovernanceMerger,
    GovernanceRule,
    GovernanceConflict,
    UnifiedInstructionSet,
)


@pytest.fixture
def sample_core_rules() -> Dict[str, Any]:
    """Sample CORTEX Tier 0 rules."""
    return {
        "schema_version": "6.0",
        "governance_tier": 0,
        "category": "CORTEX_CORE",
        "precedence": "HIGHEST",
        "rules": [
            {
                "rule_id": "CORE-001",
                "category": "orchestration_lifecycle",
                "severity": "blocked",
                "name": "Incremental Autonomous Execution",
                "description": "ALL orchestrators MUST work in small increments.",
            },
            {
                "rule_id": "CORE-008",
                "category": "development_workflow",
                "severity": "blocked",
                "name": "TDD Enforcement",
                "description": "Tests MUST be written BEFORE implementation.",
            },
        ],
    }


@pytest.fixture
def sample_business_rules() -> Dict[str, Any]:
    """Sample Business Tier 0 rules."""
    return {
        "schema_version": "1.0",
        "governance_tier": 1,
        "category": "BUSINESS_TIER_0",
        "precedence": "HIGH",
        "rules": [
            {
                "rule_id": "BIZ-001",
                "category": "compliance",
                "severity": "blocked",
                "name": "GDPR Compliance",
                "description": "PII must be encrypted at rest and in transit.",
            },
            {
                "rule_id": "BIZ-002",
                "category": "security",
                "severity": "blocked",
                "name": "Audit Trail Required",
                "description": "All data access must be logged.",
            },
        ],
    }


@pytest.fixture
def sample_company_practices() -> Dict[str, Any]:
    """Sample Company Best Practices rules."""
    return {
        "schema_version": "1.0",
        "governance_tier": 2,
        "category": "COMPANY_PRACTICES",
        "precedence": "MEDIUM",
        "rules": [
            {
                "rule_id": "COMP-001",
                "category": "code_quality",
                "severity": "warning",
                "name": "Code Review Required",
                "description": "All code changes require peer review.",
            },
            {
                "rule_id": "COMP-002",
                "category": "testing",
                "severity": "warning",
                "name": "80% Coverage Minimum",
                "description": "Test coverage must be at least 80%.",
            },
        ],
    }


@pytest.fixture
def sample_knowledge_practices() -> Dict[str, Any]:
    """Sample Knowledge Best Practices rules."""
    return {
        "schema_version": "1.0",
        "governance_tier": 3,
        "category": "KNOWLEDGE_PRACTICES",
        "precedence": "LOW",
        "rules": [
            {
                "rule_id": "KNOW-001",
                "category": "patterns",
                "severity": "info",
                "name": "Prefer Factory Pattern",
                "description": "Use factory pattern for object creation.",
            },
        ],
    }


@pytest.fixture
def conflicting_rules() -> Dict[str, Any]:
    """Sample rules that conflict with each other."""
    return {
        "tier0": {
            "rule_id": "CORE-008",
            "category": "development_workflow",
            "severity": "blocked",
            "name": "TDD Enforcement",
            "requirement": "Tests MUST be written first",
            "precedence": "HIGHEST",
        },
        "tier2": {
            "rule_id": "COMP-003",
            "category": "development_workflow",
            "severity": "warning",
            "name": "TDD Recommended",
            "requirement": "Tests SHOULD be written first",
            "precedence": "MEDIUM",
        },
    }


class TestGovernanceMerger:
    """Test suite for GovernanceMerger."""

    def test_governance_merger_initialization(self, tmp_path):
        """Test GovernanceMerger can be initialized."""

        merger = GovernanceMerger(governance_root=tmp_path)
        assert merger is not None
        assert merger.governance_root == tmp_path

    def test_load_core_rules(self, tmp_path, sample_core_rules):
        """Test loading CORTEX Tier 0 core rules."""

        # Create core-rules.yaml
        core_rules_path = tmp_path / "tier0" / "governance"
        core_rules_path.mkdir(parents=True)
        
        import yaml
        with open(core_rules_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        core_rules = merger.load_core_rules()

        assert len(core_rules) == 2
        assert core_rules[0].rule_id == "CORE-001"
        assert core_rules[0].precedence == "HIGHEST"

    def test_load_business_rules(self, tmp_path, sample_business_rules):
        """Test loading Business Tier 0 rules."""

        # Create business-rules.yaml
        business_path = tmp_path / "tier1" / "governance"
        business_path.mkdir(parents=True)
        
        import yaml
        with open(business_path / "business-rules.yaml", "w") as f:
            yaml.dump(sample_business_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        business_rules = merger.load_business_rules()

        assert len(business_rules) == 2
        assert business_rules[0].rule_id == "BIZ-001"

    def test_load_company_practices(self, tmp_path, sample_company_practices):
        """Test loading Company Best Practices."""

        # Create company-practices.yaml
        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        
        import yaml
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(sample_company_practices, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        company_rules = merger.load_company_practices()

        assert len(company_rules) == 2
        assert company_rules[0].rule_id == "COMP-001"

    def test_load_knowledge_practices(self, tmp_path, sample_knowledge_practices):
        """Test loading Knowledge Best Practices."""

        # Create knowledge-practices.yaml
        knowledge_path = tmp_path / "tier3" / "governance"
        knowledge_path.mkdir(parents=True)
        
        import yaml
        with open(knowledge_path / "knowledge-practices.yaml", "w") as f:
            yaml.dump(sample_knowledge_practices, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        knowledge_rules = merger.load_knowledge_practices()

        assert len(knowledge_rules) == 1
        assert knowledge_rules[0].rule_id == "KNOW-001"

    def test_load_all_categories(self, tmp_path, sample_core_rules, sample_business_rules, 
                                  sample_company_practices, sample_knowledge_practices):
        """Test loading rules from all 4 categories."""

        # Create all governance files
        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        business_path = tmp_path / "tier1" / "governance"
        business_path.mkdir(parents=True)
        with open(business_path / "business-rules.yaml", "w") as f:
            yaml.dump(sample_business_rules, f)

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(sample_company_practices, f)

        knowledge_path = tmp_path / "tier3" / "governance"
        knowledge_path.mkdir(parents=True)
        with open(knowledge_path / "knowledge-practices.yaml", "w") as f:
            yaml.dump(sample_knowledge_practices, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        all_rules = merger.load_all_rules()

        # Should have 2 + 2 + 2 + 1 = 7 rules total
        assert len(all_rules) == 7
        
        # Verify all tiers represented
        tiers = {rule.governance_tier for rule in all_rules}
        assert tiers == {0, 1, 2, 3}


class TestConflictDetection:
    """Test suite for conflict detection algorithm."""

    def test_detect_no_conflicts(self, tmp_path, sample_core_rules, sample_business_rules):
        """Test that non-conflicting rules are identified correctly."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        business_path = tmp_path / "tier1" / "governance"
        business_path.mkdir(parents=True)
        with open(business_path / "business-rules.yaml", "w") as f:
            yaml.dump(sample_business_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        conflicts = merger.detect_conflicts()

        assert len(conflicts) == 0

    def test_detect_category_conflicts(self, tmp_path, conflicting_rules):
        """Test detection of conflicting rules in same category."""

        # Create conflicting TDD rules
        import yaml
        
        core_rules = {
            "rules": [conflicting_rules["tier0"]]
        }
        company_rules = {
            "rules": [conflicting_rules["tier2"]]
        }

        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(core_rules, f)

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(company_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        conflicts = merger.detect_conflicts()

        assert len(conflicts) > 0
        assert conflicts[0].category == "development_workflow"
        assert "TDD" in conflicts[0].description

    def test_detect_severity_conflicts(self, tmp_path):
        """Test detection of severity conflicts (blocked vs warning)."""

        import yaml
        
        # Same rule ID but different severities
        core_rules = {
            "rules": [{
                "rule_id": "CODE-001",
                "severity": "blocked",
                "name": "Code Quality",
            }]
        }
        company_rules = {
            "rules": [{
                "rule_id": "CODE-001",
                "severity": "warning",
                "name": "Code Quality",
            }]
        }

        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(core_rules, f)

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(company_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        conflicts = merger.detect_conflicts()

        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == "severity_mismatch"


class TestConflictResolution:
    """Test suite for conflict resolution strategies."""

    def test_tier_precedence_resolution(self, tmp_path, conflicting_rules):
        """Test that Tier 0 always wins in conflicts."""

        import yaml
        
        core_rules = {"rules": [conflicting_rules["tier0"]]}
        company_rules = {"rules": [conflicting_rules["tier2"]]}

        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(core_rules, f)

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(company_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        resolved_rules = merger.resolve_conflicts()

        # Tier 0 rule should win
        tdd_rule = next(r for r in resolved_rules if "TDD" in r.name)
        assert tdd_rule.rule_id == "CORE-008"
        assert tdd_rule.severity == "blocked"
        assert tdd_rule.governance_tier == 0

    def test_severity_upgrade_resolution(self, tmp_path):
        """Test that higher severity wins when same tier."""

        import yaml
        
        # Two tier 2 rules, one blocked, one warning
        company_rules = {
            "rules": [
                {
                    "rule_id": "TEST-001",
                    "severity": "blocked",
                    "category": "testing",
                },
                {
                    "rule_id": "TEST-001",
                    "severity": "warning",
                    "category": "testing",
                },
            ]
        }

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(company_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        resolved_rules = merger.resolve_conflicts()

        test_rule = next(r for r in resolved_rules if r.rule_id == "TEST-001")
        assert test_rule.severity == "blocked"

    def test_merge_complementary_rules(self, tmp_path):
        """Test that complementary rules are merged, not conflicted."""

        import yaml
        
        # Rules that complement each other (different aspects)
        core_rules = {
            "rules": [{
                "rule_id": "SEC-001",
                "category": "security",
                "requirement": "Encrypt data at rest",
            }]
        }
        business_rules = {
            "rules": [{
                "rule_id": "SEC-002",
                "category": "security",
                "requirement": "Encrypt data in transit",
            }]
        }

        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(core_rules, f)

        business_path = tmp_path / "tier1" / "governance"
        business_path.mkdir(parents=True)
        with open(business_path / "business-rules.yaml", "w") as f:
            yaml.dump(business_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        resolved_rules = merger.resolve_conflicts()

        # Both rules should be present (no conflict)
        assert len(resolved_rules) == 2


class TestUnifiedInstructionSet:
    """Test suite for Unified Instruction Set generation."""

    def test_generate_unified_instruction_set(self, tmp_path, sample_core_rules, 
                                               sample_business_rules):
        """Test generating unified instruction set from merged rules."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        business_path = tmp_path / "tier1" / "governance"
        business_path.mkdir(parents=True)
        with open(business_path / "business-rules.yaml", "w") as f:
            yaml.dump(sample_business_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        unified_set = merger.generate_unified_instruction_set()

        assert unified_set is not None
        assert isinstance(unified_set, UnifiedInstructionSet)
        assert len(unified_set.rules) == 4  # 2 core + 2 business

    def test_unified_set_has_metadata(self, tmp_path, sample_core_rules):
        """Test that unified instruction set includes metadata."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        unified_set = merger.generate_unified_instruction_set()

        assert unified_set.version is not None
        assert unified_set.generated_at is not None
        assert unified_set.tier_count == 1  # Only tier 0 rules
        assert unified_set.rule_count == 2

    def test_unified_set_preserves_precedence(self, tmp_path, sample_core_rules, 
                                               sample_company_practices):
        """Test that unified set preserves tier precedence ordering."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(sample_company_practices, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        unified_set = merger.generate_unified_instruction_set()

        # Rules should be sorted by tier (0 before 2)
        tiers = [rule.governance_tier for rule in unified_set.rules]
        assert tiers == sorted(tiers)

    def test_unified_set_exports_to_dict(self, tmp_path, sample_core_rules):
        """Test that unified instruction set can be exported to dict."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        unified_set = merger.generate_unified_instruction_set()

        exported = unified_set.to_dict()
        assert isinstance(exported, dict)
        assert "rules" in exported
        assert "metadata" in exported
        assert len(exported["rules"]) == 2

    def test_unified_set_exports_to_yaml(self, tmp_path, sample_core_rules):
        """Test that unified instruction set can be exported to YAML."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        merger = GovernanceMerger(governance_root=tmp_path)
        unified_set = merger.generate_unified_instruction_set()

        yaml_output = unified_set.to_yaml()
        assert isinstance(yaml_output, str)
        assert "rules:" in yaml_output
        assert "CORE-001" in yaml_output


class TestEndToEndMerge:
    """End-to-end tests for complete merge workflow."""

    def test_full_merge_workflow(self, tmp_path, sample_core_rules, sample_business_rules,
                                  sample_company_practices, sample_knowledge_practices):
        """Test complete merge workflow from load to unified set."""

        import yaml
        
        # Set up all governance files
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        business_path = tmp_path / "tier1" / "governance"
        business_path.mkdir(parents=True)
        with open(business_path / "business-rules.yaml", "w") as f:
            yaml.dump(sample_business_rules, f)

        practices_path = tmp_path / "tier2" / "governance"
        practices_path.mkdir(parents=True)
        with open(practices_path / "company-practices.yaml", "w") as f:
            yaml.dump(sample_company_practices, f)

        knowledge_path = tmp_path / "tier3" / "governance"
        knowledge_path.mkdir(parents=True)
        with open(knowledge_path / "knowledge-practices.yaml", "w") as f:
            yaml.dump(sample_knowledge_practices, f)

        # Execute full merge
        merger = GovernanceMerger(governance_root=tmp_path)
        unified_set = merger.merge()

        # Verify results
        assert unified_set is not None
        assert len(unified_set.rules) == 7
        assert unified_set.tier_count == 4
        
        # Verify tier 0 rules are first
        first_rule = unified_set.rules[0]
        assert first_rule.governance_tier == 0
        assert first_rule.precedence == "HIGHEST"

    def test_merge_with_audit_logging(self, tmp_path, sample_core_rules):
        """Test that merge process logs to audit system."""

        import yaml
        
        core_path = tmp_path / "tier0" / "governance"
        core_path.mkdir(parents=True)
        with open(core_path / "core-rules.yaml", "w") as f:
            yaml.dump(sample_core_rules, f)

        with patch('src.orchestrators.core.governance_merger.EnterpriseAuditLogger') as mock_logger:
            merger = GovernanceMerger(governance_root=tmp_path)
            unified_set = merger.merge()

            # Verify audit logging occurred
            assert mock_logger.return_value.log.called
            assert mock_logger.return_value.log.call_count >= 4  # load + merge operations
