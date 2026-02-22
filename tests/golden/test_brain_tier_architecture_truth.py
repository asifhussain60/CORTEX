"""
Golden Truth Test: Brain Tier Architecture Validation

Tests the complete brain tier architecture for structural integrity,
precedence enforcement, and operational correctness.

Authority: Phase 105 - Brain Tier Architecture Fix
AC-IDs: AC-PHASE105-001 through AC-PHASE105-010

This test validates:
1. Tier directory structure exists
2. Precedence rules match implementation
3. Governance and memory tiers are separate
4. All tier operations work correctly
5. No architectural contradictions exist
"""

import pytest
from pathlib import Path
from typing import Dict, List
import yaml

from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.core.core.tier_resolver import TierResolver
from cortex.core.core.intent.comprehension_loop import BrainTierPusher


class TestTierDirectoryStructure:
    """Validate tier directory structure exists and is correct."""

    def test_governance_tier_directories_exist(self):
        """Governance tiers must exist at registry level."""
        registry_path = Path("cortex-registry/core")
        
        assert (registry_path / "tier0-skull").exists(), \
            "Tier 0 (SKULL) governance directory missing"
        assert (registry_path / "tier1-project").exists(), \
            "Tier 1 (Project) governance directory missing"
        assert (registry_path / "tier2-engineering").exists(), \
            "Tier 2 (Engineering) governance directory missing"

    def test_memory_tier_directories_exist(self):
        """Memory tiers must exist in cortex/intelligence (Phase 3 consolidation)."""
        memory_path = Path("cortex/intelligence/memory")
        
        # New clarified names (migrated from cortex.intelligence to cortex/intelligence)
        assert (memory_path / "tier1_learned").exists() or \
               (memory_path / "tier1_learned").exists(), \
            "Learned patterns memory tier missing"
        assert (memory_path / "tier2_adaptive").exists() or \
               (memory_path / "tier2_adaptive").exists(), \
            "Adaptive intelligence memory tier missing"
        assert (memory_path / "scratch_space").exists() or \
               (memory_path / "tier3_scratch").exists(), \
            "Scratch space memory tier missing"

    def test_governance_and_memory_tiers_separate(self):
        """Governance tiers and memory tiers must be in separate locations."""
        registry_path = Path("cortex-registry/core")
        intelligence_path = Path("cortex/intelligence")
        
        # Governance at registry level
        assert registry_path.exists()
        assert any((registry_path / f"tier{i}-{name}").exists() 
                  for i, name in [(0, "skull"), (1, "project"), (2, "engineering")])
        
        # Memory at intelligence level
        assert intelligence_path.exists()
        assert (intelligence_path / "memory").exists()


class TestTierPrecedenceConsistency:
    """Validate precedence definitions are consistent across system."""

    def test_precedence_yaml_matches_tier_resolver(self):
        """precedence.yaml must match TierResolver implementation."""
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        
        if precedence_path.exists():
            with open(precedence_path) as f:
                precedence_config = yaml.safe_load(f)
            
            # Should be tier0 > tier1 > tier2 (not the reverse)
            conflict_resolution = precedence_config.get("conflict_resolution", "")
            
            # Accept correct format
            assert "tier0" in conflict_resolution, \
                "Tier 0 must be in conflict resolution"
            
            # The correct format is tier0_overrides_tier1_overrides_tier2
            # NOT tier2_overrides_tier1_overrides_tier0
            assert not conflict_resolution.startswith("tier2_overrides"), \
                f"Precedence is reversed! Found: {conflict_resolution}. " \
                f"Should be: tier0_overrides_tier1_overrides_tier2"

    def test_tier_resolver_precedence_order(self):
        """TierResolver must define correct precedence order."""
        resolver = TierResolver()
        precedence_order = resolver.get_precedence_order()
        
        # Should be [(0, ...), (1, ...), (2, ...)] in that order
        assert precedence_order[0][0] == 0, "Tier 0 must have highest precedence"
        assert precedence_order[1][0] == 1, "Tier 1 must be second"
        assert precedence_order[2][0] == 2, "Tier 2 must be third"
        
        # Verify Tier 0 is SKULL (immutable)
        assert "SKULL" in precedence_order[0][1] or "Immutable" in precedence_order[0][1]


class TestGovernanceRegistryTierSupport:
    """Validate GovernanceRegistry implements tier operations correctly."""

    def test_governance_registry_has_get_rule_method(self):
        """GovernanceRegistry must have get_rule() method."""
        registry = GovernanceRegistry.instance()
        
        assert hasattr(registry, 'get_rule'), \
            "GovernanceRegistry missing get_rule() method - TierResolver is unusable!"

    def test_get_rule_returns_result_type(self):
        """get_rule() must return Result type."""
        registry = GovernanceRegistry.instance()
        registry.initialize()
        
        # Try to get a rule (may not exist, that's OK)
        result = registry.get_rule("CORE-008")
        
        # Must return Result type (Ok or Err)
        assert hasattr(result, 'is_ok') and hasattr(result, 'is_err'), \
            "get_rule() must return Result type"

    def test_tier_precedence_in_rule_lookup(self):
        """Rule lookup must respect tier precedence."""
        registry = GovernanceRegistry.instance()
        registry.initialize()
        
        # If we have tier0 rules, they should be found first
        if hasattr(registry, '_tier0_rules') and registry._tier0_rules:
            # Get any tier0 rule
            tier0_rule_id = list(registry._tier0_rules.keys())[0]
            result = registry.get_rule(tier0_rule_id)
            
            if result.is_ok():
                rule = result.unwrap()
                assert rule is not None
                assert rule.tier == 0, \
                    f"Tier 0 rule {tier0_rule_id} returned with wrong tier: {rule.tier}"


class TestTierResolverIntegration:
    """Validate TierResolver integration with GovernanceRegistry."""

    def test_tier_resolver_can_get_rules(self):
        """TierResolver must be able to get rules through registry."""
        resolver = TierResolver()
        
        # This should not raise AttributeError
        try:
            result = resolver.get_effective_rule("CORE-008")
            assert result is not None
        except AttributeError as e:
            pytest.fail(f"TierResolver.get_effective_rule() failed: {e}")

    def test_tier_resolver_checks_precedence(self):
        """TierResolver must check tier precedence."""
        resolver = TierResolver()
        
        # Check precedence for a rule
        try:
            result = resolver.check_tier_precedence("CORE-008")
            # Should return (tier, description) or error
            assert result is not None
        except AttributeError:
            pytest.fail("TierResolver.check_tier_precedence() failed")

    def test_tier_0_cannot_be_overridden(self):
        """Tier 0 rules must never be overridden by lower tiers."""
        resolver = TierResolver()
        
        # Tier 0 should never report as overridden
        result = resolver.is_overridden("CORE-008", tier=0)
        
        if result.is_ok():
            is_overridden = result.unwrap()
            assert is_overridden is False, \
                "Tier 0 rules must never be overridden!"


class TestBrainTierPusherPaths:
    """Validate BrainTierPusher writes to correct locations."""

    def test_brain_tier_pusher_has_valid_paths(self):
        """BrainTierPusher TIER_PATHS must point to existing directories."""
        pusher = BrainTierPusher()
        
        # Check all tier paths are defined
        assert hasattr(pusher, 'TIER_PATHS'), \
            "BrainTierPusher missing TIER_PATHS attribute"
        
        tier_paths = pusher.TIER_PATHS
        assert len(tier_paths) > 0, "TIER_PATHS is empty"

    def test_tier_paths_dont_reference_nonexistent_dirs(self):
        """BrainTierPusher must not write to non-existent tier0/tier1/tier2."""
        pusher = BrainTierPusher()
        
        for tier, path_str in pusher.TIER_PATHS.items():
            path = Path(path_str)
            
            # The path should either exist OR be createable
            # (we don't want paths like cortex/intelligence/tier0/ which don't exist)
            parent = path.parent
            
            # If it references cortex/intelligence/tierX, parent should exist
            if "cortex.intelligence" in str(path) and "tier" in path.name:
                # This is suspicious - should be in memory/ or registry/
                if not path.exists():
                    pytest.fail(
                        f"BrainTierPusher tier {tier} references non-existent path: {path}. "
                        f"Should be in memory/ or cortex-registry/core/"
                    )


class TestTierSystemSeparation:
    """Validate clear separation between tier systems."""

    def test_governance_tiers_in_registry(self):
        """Governance tiers (0,1,2) should be in cortex-registry."""
        # Tier 0, 1, 2 for governance
        tier0 = Path("cortex-registry/core/tier0-skull")
        tier1 = Path("cortex-registry/core/tier1-project")
        tier2 = Path("cortex-registry/core/tier2-engineering")
        
        # At least one should exist (after phase 105)
        governance_exists = tier0.exists() or tier1.exists() or tier2.exists()
        
        assert governance_exists, \
            "Governance tiers should be in cortex-registry/core/"

    def test_memory_tiers_in_intelligence(self):
        """Memory tiers should be in cortex/intelligence/memory."""
        memory_path = Path("cortex/intelligence/memory")
        
        assert memory_path.exists(), \
            "Memory tier directory must exist"
        
        # Should have at least one tier subdirectory
        tier_dirs = [d for d in memory_path.iterdir() 
                    if d.is_dir() and ('tier' in d.name or 'learned' in d.name or 
                                      'adaptive' in d.name or 'scratch' in d.name)]
        
        assert len(tier_dirs) > 0, \
            "Memory tiers missing in cortex/intelligence/memory/"

    def test_no_tier_mixing(self):
        """Governance and memory tier files should not be mixed."""
        # Governance rules should not be in memory/
        memory_path = Path("cortex/intelligence/memory")
        if memory_path.exists():
            skull_files = list(memory_path.rglob("*skull*.yaml"))
            assert len(skull_files) == 0, \
                f"SKULL rules found in memory tiers: {skull_files}"
        
        # Memory patterns should not be in registry/core/
        registry_path = Path("cortex-registry/core")
        if registry_path.exists():
            learned_files = list(registry_path.rglob("*learned*.yaml"))
            scratch_files = list(registry_path.rglob("*scratch*.yaml"))
            assert len(learned_files) == 0 and len(scratch_files) == 0, \
                "Memory tier files found in governance registry"


class TestTierArchitectureDocumentation:
    """Validate tier architecture is documented correctly."""

    def test_tier_system_documented_in_init(self):
        """cortex.intelligence.__init__.py should document tier system."""
        init_file = Path("cortex/intelligence/__init__.py")
        
        if init_file.exists():
            content = init_file.read_text()
            
            # Should mention tier system
            assert "tier" in content.lower() or "TIER" in content, \
                "Tier system not documented in cortex.intelligence.__init__.py"

    def test_precedence_yaml_has_explanation(self):
        """precedence.yaml should have clear explanation."""
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        
        if precedence_path.exists():
            with open(precedence_path) as f:
                config = yaml.safe_load(f)
            
            assert "explanation" in config, \
                "precedence.yaml missing explanation field"
            
            explanation = config["explanation"]
            assert len(explanation) > 50, \
                "precedence.yaml explanation too short"


class TestTierArchitectureIntegrity:
    """Validate overall tier architecture integrity."""

    def test_no_contradictory_precedence(self):
        """System should not have contradictory precedence definitions."""
        # Check precedence.yaml
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        yaml_precedence = None
        
        if precedence_path.exists():
            with open(precedence_path) as f:
                config = yaml.safe_load(f)
            yaml_precedence = config.get("conflict_resolution", "")
        
        # Check TierResolver
        resolver = TierResolver()
        code_precedence = resolver.get_precedence_order()
        
        # They should agree: Tier 0 > Tier 1 > Tier 2
        if yaml_precedence:
            # YAML should NOT say tier2 overrides tier1 overrides tier0
            assert not yaml_precedence.startswith("tier2_overrides"), \
                f"CONTRADICTORY PRECEDENCE! YAML says: {yaml_precedence}, " \
                f"but code says: Tier 0 > Tier 1 > Tier 2"

    def test_all_tier_systems_coexist(self):
        """Multiple tier systems can coexist if clearly separated."""
        # Governance tiers: 0-2 (registry)
        # Memory tiers: 1-3 (intelligence/memory)
        # This is OK as long as they're separate
        
        governance_path = Path("cortex-registry/core")
        memory_path = Path("cortex/intelligence/memory")
        
        # Both should exist
        assert governance_path.exists() or memory_path.exists(), \
            "Neither governance nor memory tiers exist"
        
        # If both exist, they should be separate
        if governance_path.exists() and memory_path.exists():
            # No overlap in files
            governance_files = set(p.name for p in governance_path.rglob("*.yaml"))
            memory_files = set(p.name for p in memory_path.rglob("*.yaml"))
            
            # Some overlap is OK (like __init__.py), but not governance rules
            skull_in_memory = any("skull" in f.lower() for f in memory_files)
            assert not skull_in_memory, \
                "SKULL rules should not be in memory tiers"

    def test_tier_resolver_usable(self):
        """TierResolver should be fully functional."""
        resolver = TierResolver()
        
        # All methods should be callable
        methods = ['get_effective_rule', 'get_tier_for_rule', 
                  'is_overridden', 'check_tier_precedence', 'get_precedence_order']
        
        for method_name in methods:
            assert hasattr(resolver, method_name), \
                f"TierResolver missing method: {method_name}"
            
            method = getattr(resolver, method_name)
            assert callable(method), \
                f"TierResolver.{method_name} is not callable"


# ============================================================================
# SUMMARY TEST
# ============================================================================

def test_brain_tier_architecture_summary():
    """
    Summary test that validates all critical aspects of tier architecture.
    
    This test should PASS after Phase 105 is complete.
    It should FAIL before Phase 105, highlighting the architectural issues.
    """
    issues = []
    
    # 1. Check directory structure
    registry_tiers = Path("cortex-registry/core")
    if not any((registry_tiers / f"tier{i}-{n}").exists() 
              for i, n in [(0, "skull"), (1, "project"), (2, "engineering")]):
        issues.append("❌ Governance tier directories missing at registry level")
    
    # 2. Check precedence consistency
    precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
    if precedence_path.exists():
        with open(precedence_path) as f:
            config = yaml.safe_load(f)
        conflict_res = config.get("conflict_resolution", "")
        if conflict_res.startswith("tier2_overrides"):
            issues.append("❌ Precedence YAML contradicts TierResolver (reversed)")
    
    # 3. Check GovernanceRegistry API
    registry = GovernanceRegistry.instance()
    if not hasattr(registry, 'get_rule'):
        issues.append("❌ GovernanceRegistry missing get_rule() method")
    
    # 4. Check TierResolver integration
    try:
        resolver = TierResolver()
        resolver.get_effective_rule("CORE-008")
    except AttributeError:
        issues.append("❌ TierResolver cannot call registry.get_rule()")
    
    # 5. Check BrainTierPusher paths
    pusher = BrainTierPusher()
    for tier, path_str in pusher.TIER_PATHS.items():
        if "cortex/intelligence/tier" in path_str and not Path(path_str).exists():
            issues.append(f"❌ BrainTierPusher tier {tier} points to non-existent: {path_str}")
    
    # Report all issues
    if issues:
        issue_report = "\n".join(issues)
        pytest.fail(
            f"\n\n🚨 BRAIN TIER ARCHITECTURE IS INVALID 🚨\n\n"
            f"Found {len(issues)} critical issues:\n\n{issue_report}\n\n"
            f"Run Phase 105 to fix these issues.\n"
        )
    
    # If we get here, architecture is valid!
    print("\n✅ Brain tier architecture is valid and coherent!")
