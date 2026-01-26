"""
Test suite for GovernanceRegistry Tier loading and integration.

Purpose:
    Test loading of Tier 0/1/2 rules and registry initialization.

Coverage:
    - initialize() - loads Tier 0 rules
    - get_all_rules() - returns Dict[str, List[GovernanceRule]]
    - rule_count_by_tier() - returns Dict[int, int]
    - Registry consistency across multiple initializations

Author: Asif Hussain
Version: 1.0
"""

import pytest
from cortex.brain.core.governance_registry import GovernanceRegistry


class TestRegistryBasics:
    """Test basic registry operations."""

    def test_initialize_loads_tier0(self) -> None:
        """Test that initialize() loads Tier 0 rules."""
        registry = GovernanceRegistry()
        registry.initialize()

        # get_all_rules() returns Dict[str, List[GovernanceRule]]
        all_rules = registry.get_all_rules()
        tier0 = all_rules.get("tier0", [])
        
        assert len(tier0) > 0

    def test_get_all_rules_structure(self) -> None:
        """Test structure of get_all_rules()."""
        registry = GovernanceRegistry()
        registry.initialize()

        all_rules = registry.get_all_rules()
        
        # Check all tiers present
        assert "tier0" in all_rules
        assert "tier1" in all_rules
        assert "tier2" in all_rules
        
        # All should be lists
        assert isinstance(all_rules["tier0"], list)
        assert isinstance(all_rules["tier1"], list)
        assert isinstance(all_rules["tier2"], list)

    def test_rule_count_by_tier(self) -> None:
        """Test rule_count_by_tier()."""
        registry = GovernanceRegistry()
        registry.initialize()

        counts = registry.rule_count_by_tier()
        
        assert isinstance(counts, dict)
        assert 0 in counts
        assert 1 in counts
        assert 2 in counts
        assert counts[0] > 0  # Should have Tier 0 rules

    def test_tier0_is_populated(self) -> None:
        """Test that Tier 0 is populated after initialization."""
        registry = GovernanceRegistry()
        registry.initialize()

        all_rules = registry.get_all_rules()
        tier0 = all_rules["tier0"]
        
        # Should have all CORE rules
        rule_ids = {r.rule_id for r in tier0}
        assert "CORE-001" in rule_ids  # Example CORE rule
        assert "CORE-008" in rule_ids  # TDD rule
        assert "CORE-035" in rule_ids  # Duplicate detection rule


class TestConsistency:
    """Test consistency across operations."""

    def test_repeated_initialization(self) -> None:
        """Test repeated initialization is consistent."""
        # First init
        reg1 = GovernanceRegistry()
        reg1.initialize()
        rules1 = reg1.get_all_rules()
        tier0_1 = rules1["tier0"]

        # Second init
        reg2 = GovernanceRegistry()
        reg2.initialize()
        rules2 = reg2.get_all_rules()
        tier0_2 = rules2["tier0"]

        # Should be identical
        assert len(tier0_1) == len(tier0_2)
        ids1 = {r.rule_id for r in tier0_1}
        ids2 = {r.rule_id for r in tier0_2}
        assert ids1 == ids2

    def test_multiple_get_all_rules_calls(self) -> None:
        """Test that multiple get_all_rules() calls return consistent data."""
        registry = GovernanceRegistry()
        registry.initialize()

        # Get rules multiple times
        rules1 = registry.get_all_rules()
        rules2 = registry.get_all_rules()

        # Count should be identical
        assert len(rules1["tier0"]) == len(rules2["tier0"])
        assert len(rules1["tier1"]) == len(rules2["tier1"])
        assert len(rules1["tier2"]) == len(rules2["tier2"])

    def test_tier_counts_match_get_all_rules(self) -> None:
        """Test that rule_count_by_tier() matches get_all_rules()."""
        registry = GovernanceRegistry()
        registry.initialize()

        counts = registry.rule_count_by_tier()
        all_rules = registry.get_all_rules()

        # Counts should match
        assert counts[0] == len(all_rules["tier0"])
        assert counts[1] == len(all_rules["tier1"])
        assert counts[2] == len(all_rules["tier2"])


class TestTierStructure:
    """Test the structure and content of tiers."""

    def test_tier0_rules_have_expected_attributes(self) -> None:
        """Test that Tier 0 rules have expected attributes."""
        registry = GovernanceRegistry()
        registry.initialize()

        all_rules = registry.get_all_rules()
        tier0 = all_rules["tier0"]

        # All should be Rule objects with key attributes
        for rule in tier0:
            assert hasattr(rule, "rule_id")
            assert hasattr(rule, "name")
            assert hasattr(rule, "tier")
            assert rule.rule_id  # ID should not be empty
            assert rule.tier == 0  # Tier should be 0

    def test_rule_ids_are_unique(self) -> None:
        """Test that all rule IDs are unique."""
        registry = GovernanceRegistry()
        registry.initialize()

        all_rules = registry.get_all_rules()
        
        # Collect all rule IDs
        all_ids = []
        for tier_key in ["tier0", "tier1", "tier2"]:
            all_ids.extend([r.rule_id for r in all_rules[tier_key]])

        # Check uniqueness
        assert len(all_ids) == len(set(all_ids))

    def test_empty_tiers_are_lists(self) -> None:
        """Test that empty tiers are still lists."""
        registry = GovernanceRegistry()
        registry.initialize()

        all_rules = registry.get_all_rules()
        
        # All tier keys should have lists (even if empty)
        assert isinstance(all_rules["tier0"], list)
        assert isinstance(all_rules["tier1"], list)
        assert isinstance(all_rules["tier2"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

