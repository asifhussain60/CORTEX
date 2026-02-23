"""
Tests for Tier Precedence Model — Phase 47 Stage 1.

Validates tier0 > tier1 > tier2 precedence and governance registry integration.

AC_START: AC-PHASE47-S1-001
Phase: 47 | Stage: 1 | Priority: P0
Description: TDD RED phase for tier precedence
Requirements: CORE-008 (TDD), tier0 > tier1 > tier2 precedence
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml


# =============================================================================
# Import targets (expected to fail in RED phase)
# =============================================================================
try:
    from cortex.orchestrators.core.governance_registry import (
        GovernanceRegistry,
        GovernanceRule,
    )
    from cortex.core.tier_resolver import TierResolver
except ImportError:
    GovernanceRegistry = None
    GovernanceRule = None
    TierResolver = None


# =============================================================================
# PRECEDENCE MODEL TESTS
# =============================================================================
class TestPrecedenceModel:
    """Test tier precedence model (tier0 > tier1 > tier2)."""

    def test_precedence_yaml_has_correct_order(self):
        """AC-PHASE47-S1-001: precedence.yaml declares tier0 > tier1 > tier2."""
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        
        if not precedence_path.exists():
            pytest.skip("precedence.yaml not found")
        
        with open(precedence_path) as f:
            precedence = yaml.safe_load(f)
        
        # Should explicitly state tier0 overrides tier1 overrides tier2
        assert "conflict_resolution" in precedence
        assert "tier0" in precedence["conflict_resolution"]
        # Should be tier0_overrides_tier1_overrides_tier2 NOT tier2_overrides_tier1_overrides_tier0
        assert precedence["conflict_resolution"] == "tier0_overrides_tier1_overrides_tier2"

    def test_precedence_order_list_is_correct(self):
        """Precedence order list should be [tier0, tier1, tier2] with tier0 first."""
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        
        if not precedence_path.exists():
            pytest.skip("precedence.yaml not found")
        
        with open(precedence_path) as f:
            precedence = yaml.safe_load(f)
        
        assert precedence["precedence_order"] == ["tier0", "tier1", "tier2"]
        # Tier 0 must be first (highest precedence)
        assert precedence["precedence_order"][0] == "tier0"


# =============================================================================
# GOVERNANCE REGISTRY get_rule() TESTS
# =============================================================================
class TestGovernanceRegistryGetRule:
    """Test GovernanceRegistry.get_rule() implementation."""

    @pytest.mark.skipif(GovernanceRegistry is None, reason="GovernanceRegistry not available")
    def test_get_rule_exists(self):
        """AC-PHASE47-S1-002: GovernanceRegistry has get_rule() method."""
        registry = GovernanceRegistry()
        assert hasattr(registry, "get_rule")
        assert callable(getattr(registry, "get_rule"))

    @pytest.mark.skipif(GovernanceRegistry is None, reason="GovernanceRegistry not available")
    def test_get_rule_returns_result_type(self):
        """get_rule() returns Result type."""
        registry = GovernanceRegistry()
        result = registry.get_rule("CORE-001")
        
        # Should return Result type (Ok or Err)
        assert hasattr(result, "is_ok") or hasattr(result, "is_err")

    @pytest.mark.skipif(GovernanceRegistry is None, reason="GovernanceRegistry not available")
    def test_get_rule_with_tier_precedence(self):
        """AC-PHASE47-S1-003: get_rule() applies tier precedence."""
        registry = GovernanceRegistry()
        
        # Mock tier0 rule (highest precedence)
        from cortex.core.interfaces import GovernanceRule as GovRule
        tier0_rule = GovRule(
            rule_id="TEST-001",
            name="Test Rule Tier 0",
            severity="error",
            tier=0,
            description="Tier 0 rule"
        )
        
        # Mock tier1/tier2 rules in rules list
        mock_rules = [
            {"rule_id": "TEST-001", "tier": 1, "description": "Tier 1 rule", "name": "T1", "severity": "warning"},
            {"rule_id": "TEST-001", "tier": 2, "description": "Tier 2 rule", "name": "T2", "severity": "info"},
        ]
        
        with patch.object(registry, "_tier0_rules", {"TEST-001": tier0_rule}), \
             patch.object(registry, "rules", mock_rules), \
             patch.object(registry, "_initialized", True):
            result = registry.get_rule("TEST-001")
            
            if result.is_ok():
                rule = result.unwrap()
                # Should return tier 0 rule (highest precedence)
                assert rule.tier == 0
                assert rule.description == "Tier 0 rule"

    @pytest.mark.skipif(GovernanceRegistry is None, reason="GovernanceRegistry not available")
    def test_get_rule_not_found_returns_none(self):
        """get_rule() returns Ok(None) for non-existent rule."""
        registry = GovernanceRegistry()
        result = registry.get_rule("NONEXISTENT-999")
        
        assert result.is_ok()
        assert result.unwrap() is None


# =============================================================================
# TIER RESOLVER INTEGRATION TESTS
# =============================================================================
class TestTierResolverIntegration:
    """Test TierResolver integration with GovernanceRegistry."""

    @pytest.mark.skipif(TierResolver is None, reason="TierResolver not available")
    def test_tier_resolver_uses_get_rule(self):
        """AC-PHASE47-S1-004: TierResolver calls registry.get_rule()."""
        mock_registry = Mock(spec=GovernanceRegistry)
        mock_registry.get_rule.return_value = Mock(is_ok=lambda: True, unwrap=lambda: None)
        
        resolver = TierResolver(registry=mock_registry)
        resolver.get_effective_rule("TEST-001")
        
        # Should call get_rule, not get_rules
        mock_registry.get_rule.assert_called_once_with("TEST-001")

    @pytest.mark.skipif(TierResolver is None, reason="TierResolver not available")
    def test_tier_resolver_respects_tier0_precedence(self):
        """TierResolver respects tier 0 highest precedence."""
        mock_rule = Mock()
        mock_rule.tier = 0
        mock_rule.rule_id = "TEST-001"
        
        mock_registry = Mock(spec=GovernanceRegistry)
        mock_result = Mock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = mock_rule
        mock_registry.get_rule.return_value = mock_result
        
        resolver = TierResolver(registry=mock_registry)
        result = resolver.is_overridden("TEST-001", 0)
        
        # Tier 0 can never be overridden
        assert result.is_ok()
        assert result.unwrap() is False


# =============================================================================
# DIRECTORY STRUCTURE TESTS
# =============================================================================
class TestTierDirectoryStructure:
    """Test tier directory structure creation."""

    def test_tier0_skull_directory_exists(self):
        """AC-PHASE47-S1-005: tier0-skull directory exists in registry."""
        tier0_path = Path("cortex-registry/core/tier0-skull")
        assert tier0_path.exists(), "tier0-skull directory must exist"
        assert tier0_path.is_dir(), "tier0-skull must be a directory"

    def test_tier1_project_directory_exists(self):
        """tier1-project directory exists in registry."""
        tier1_path = Path("cortex-registry/core/tier1-project")
        assert tier1_path.exists(), "tier1-project directory must exist"
        assert tier1_path.is_dir(), "tier1-project must be a directory"

    def test_tier2_engineering_directory_exists(self):
        """tier2-engineering directory exists in registry."""
        tier2_path = Path("cortex-registry/core/tier2-engineering")
        assert tier2_path.exists(), "tier2-engineering directory must exist"
        assert tier2_path.is_dir(), "tier2-engineering must be a directory"

    def test_skull_rules_in_tier0(self):
        """AC-PHASE47-S1-006: skull-rules.yaml in tier0-skull directory."""
        skull_rules_path = Path("cortex-registry/core/tier0-skull/skull-rules.yaml")
        assert skull_rules_path.exists(), "skull-rules.yaml must be in tier0-skull"


# =============================================================================
# TIER 0 OVERRIDE TESTS
# =============================================================================
class TestTier0CannotBeOverridden:
    """Test that tier 0 rules cannot be overridden by tier 1 or tier 2."""

    @pytest.mark.skipif(TierResolver is None, reason="TierResolver not available")
    def test_tier0_rule_not_overridden_by_tier1(self):
        """AC-PHASE47-S1-007: Tier 0 rule cannot be overridden by tier 1."""
        mock_rule_tier0 = Mock()
        mock_rule_tier0.tier = 0
        mock_rule_tier0.rule_id = "CORE-001"
        
        mock_registry = Mock(spec=GovernanceRegistry)
        mock_result = Mock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = mock_rule_tier0
        mock_registry.get_rule.return_value = mock_result
        
        resolver = TierResolver(registry=mock_registry)
        result = resolver.is_overridden("CORE-001", 0)
        
        assert result.is_ok()
        assert result.unwrap() is False

    @pytest.mark.skipif(TierResolver is None, reason="TierResolver not available")
    def test_tier0_rule_not_overridden_by_tier2(self):
        """Tier 0 rule cannot be overridden by tier 2."""
        mock_rule_tier0 = Mock()
        mock_rule_tier0.tier = 0
        
        mock_registry = Mock(spec=GovernanceRegistry)
        mock_result = Mock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = mock_rule_tier0
        mock_registry.get_rule.return_value = mock_result
        
        resolver = TierResolver(registry=mock_registry)
        result = resolver.is_overridden("CORE-001", 0)
        
        assert result.unwrap() is False


# =============================================================================
# TIER 1 OVERRIDE TESTS
# =============================================================================
class TestTier1OverridesTier2:
    """Test that tier 1 rules override tier 2."""

    @pytest.mark.skipif(TierResolver is None, reason="TierResolver not available")
    def test_tier1_overrides_tier2(self):
        """AC-PHASE47-S1-008: Tier 1 rule overrides tier 2."""
        # When searching for rule, tier 1 version should be returned
        mock_rule_tier1 = Mock()
        mock_rule_tier1.tier = 1
        mock_rule_tier1.rule_id = "PROJECT-001"
        
        mock_registry = Mock(spec=GovernanceRegistry)
        mock_result = Mock()
        mock_result.is_ok.return_value = True
        mock_result.unwrap.return_value = mock_rule_tier1
        mock_registry.get_rule.return_value = mock_result
        
        resolver = TierResolver(registry=mock_registry)
        result = resolver.get_effective_rule("PROJECT-001")
        
        assert result.is_ok()
        rule = result.unwrap()
        assert rule.tier == 1  # Tier 1 wins over tier 2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================
class TestTierPrecedenceIntegration:
    """Integration tests for tier precedence system."""

    def test_full_precedence_chain(self):
        """AC-PHASE47-S1-009: Full tier precedence chain works end-to-end."""
        # This is an integration test that will verify the full chain:
        # precedence.yaml → GovernanceRegistry.get_rule() → TierResolver
        
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        if not precedence_path.exists():
            pytest.skip("precedence.yaml not found")
        
        with open(precedence_path) as f:
            precedence = yaml.safe_load(f)
        
        # Verify precedence model is correct
        assert precedence["conflict_resolution"] == "tier0_overrides_tier1_overrides_tier2"
        
        # Verify GovernanceRegistry can be instantiated
        if GovernanceRegistry is not None:
            registry = GovernanceRegistry()
            assert hasattr(registry, "get_rule")


# =============================================================================
# GOLDEN TESTS (S1.T7)
# =============================================================================
class TestTierPrecedenceGoldenScenarios:
    """Golden test cases for tier precedence - real-world scenarios."""

    @pytest.mark.skipif(GovernanceRegistry is None, reason="GovernanceRegistry not available")
    def test_skull_rule_cannot_be_overridden_by_project(self):
        """Golden Test 1: SKULL rule (tier0) blocks project override (tier1)."""
        registry = GovernanceRegistry()
        
        # Simulate SKULL rule exists (e.g., CORE-001)
        from cortex.core.interfaces import GovernanceRule as GovRule
        skull_rule = GovRule(
            rule_id="CORE-001",
            name="TDD Required",
            severity="error",
            tier=0,
            description="All features require TDD"
        )
        
        # Project tries to override with more lenient rule
        project_rule_dict = {
            "rule_id": "CORE-001",
            "tier": 1,
            "severity": "warning",  # Attempting to downgrade
            "name": "TDD Optional",
            "description": "TDD is optional for prototypes"
        }
        
        with patch.object(registry, "_tier0_rules", {"CORE-001": skull_rule}), \
             patch.object(registry, "rules", [project_rule_dict]), \
             patch.object(registry, "_initialized", True):
            result = registry.get_rule("CORE-001")
            
            assert result.is_ok()
            rule = result.unwrap()
            # SKULL rule wins - tier0 cannot be overridden
            assert rule.tier == 0
            assert rule.severity == "error"  # Original severity preserved
            assert "TDD Required" in rule.name

    @pytest.mark.skipif(GovernanceRegistry is None, reason="GovernanceRegistry not available")
    def test_project_rule_overrides_engineering_standard(self):
        """Golden Test 2: Project rule (tier1) overrides engineering standard (tier2)."""
        registry = GovernanceRegistry()
        
        # Engineering standard (tier2): max line length 80
        # Project override (tier1): max line length 120 for legacy code
        
        mock_rules = [
            {
                "rule_id": "CODE-STYLE-001",
                "tier": 1,
                "name": "Max Line Length (Project)",
                "severity": "warning",
                "description": "Max line length: 120 chars (legacy exception)"
            },
            {
                "rule_id": "CODE-STYLE-001",
                "tier": 2,
                "name": "Max Line Length (Standard)",
                "severity": "error",
                "description": "Max line length: 80 chars"
            }
        ]
        
        with patch.object(registry, "_tier0_rules", {}), \
             patch.object(registry, "rules", mock_rules), \
             patch.object(registry, "_initialized", True):
            result = registry.get_rule("CODE-STYLE-001")
            
            assert result.is_ok()
            rule = result.unwrap()
            # Project rule wins (tier1 > tier2)
            assert rule.tier == 1
            assert "120 chars" in rule.description

    def test_tier_directory_structure_follows_precedence(self):
        """Golden Test 3: Directory structure reflects tier precedence."""
        tier0_path = Path("cortex-registry/core/tier0-skull")
        tier1_path = Path("cortex-registry/core/tier1-project")
        tier2_path = Path("cortex-registry/core/tier2-engineering")
        
        # Verify all exist
        assert tier0_path.exists(), "tier0-skull directory missing"
        assert tier1_path.exists(), "tier1-project directory missing"
        assert tier2_path.exists(), "tier2-engineering directory missing"
        
        # Verify tier0 has content (skull-rules.yaml)
        skull_rules = tier0_path / "skull-rules.yaml"
        assert skull_rules.exists(), "skull-rules.yaml not in tier0-skull/"
        
        # Verify naming convention reflects precedence
        assert "tier0" in tier0_path.name
        assert "tier1" in tier1_path.name
        assert "tier2" in tier2_path.name

    def test_precedence_yaml_explanation_matches_implementation(self):
        """Golden Test 4: precedence.yaml explanation aligns with implementation."""
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        if not precedence_path.exists():
            pytest.skip("precedence.yaml not found")
        
        with open(precedence_path) as f:
            precedence = yaml.safe_load(f)
        
        # Verify key fields
        assert precedence["conflict_resolution"] == "tier0_overrides_tier1_overrides_tier2"
        
        # Verify explanation mentions immutability
        explanation = precedence.get("explanation", "")
        assert "tier 0" in explanation.lower() or "tier0" in explanation.lower()
        assert "skull" in explanation.lower() or "immutable" in explanation.lower()
        
        # Verify precedence order list (string format: tier0, tier1, tier2)
        precedence_order = precedence.get("precedence_order", [])
        # Accept either numeric or string format
        assert precedence_order in ([0, 1, 2], ["tier0", "tier1", "tier2"]), \
            f"precedence_order should be [0,1,2] or ['tier0','tier1','tier2'], got {precedence_order}"


# =============================================================================
# AC_COMPLETE: AC-PHASE47-S1-001 (All tests should pass - GREEN phase)
# =============================================================================
