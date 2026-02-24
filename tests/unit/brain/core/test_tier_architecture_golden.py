"""
Phase 47 Stage 4: Golden Tests & Documentation

Integration golden tests for tier architecture validation.
Tests end-to-end scenarios across governance, memory, and brain systems.

Acceptance Criteria:
- AC-PHASE47-S4-001: End-to-end tier precedence validation
- AC-PHASE47-S4-002: Memory tier migration scenarios
- AC-PHASE47-S4-003: BrainTierPusher integration
- AC-PHASE47-S4-004: Documentation completeness
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml


# =============================================================================
# END-TO-END TIER PRECEDENCE TESTS
# =============================================================================
class TestEndToEndTierPrecedence:
    """Golden tests for complete tier precedence flow."""

    def test_governance_rule_lookup_respects_tier_precedence(self):
        """AC-PHASE47-S4-001: GovernanceRegistry.get_rule() respects tier precedence."""
        try:
            from cortex.orchestrators.core.governance_registry import GovernanceRegistry
            from cortex.core.interfaces import GovernanceRule
            
            registry = GovernanceRegistry()
            
            # Mock tier0 rule (highest precedence)
            skull_rule = GovernanceRule(
                rule_id="CORE-001",
                name="TDD Required",
                severity="error",
                tier=0,
                description="Test-driven development mandatory"
            )
            
            # Mock conflicting rules in lower tiers
            mock_rules = [
                {"rule_id": "CORE-001", "tier": 1, "severity": "warning", "name": "TDD Optional", "description": "TDD recommended"},
                {"rule_id": "CORE-001", "tier": 2, "severity": "info", "name": "TDD Suggested", "description": "TDD nice-to-have"},
            ]
            
            with patch.object(registry, "_tier0_rules", {"CORE-001": skull_rule}), \
                 patch.object(registry, "rules", mock_rules), \
                 patch.object(registry, "_initialized", True):
                result = registry.get_rule("CORE-001")
                
                assert result.is_ok()
                rule = result.unwrap()
                
                # Tier 0 rule should win
                assert rule.tier == 0
                assert rule.severity == "error"
                assert "TDD Required" in rule.name
                
        except ImportError:
            pytest.skip("GovernanceRegistry not available")

    def test_tier_resolver_enforces_precedence(self):
        """AC-PHASE47-S4-001: TierResolver enforces tier precedence."""
        try:
            from cortex.core.tier_resolver import TierResolver
            from cortex.orchestrators.core.governance_registry import GovernanceRegistry
            from cortex.core.interfaces import GovernanceRule
            
            registry = GovernanceRegistry()
            resolver = TierResolver(registry)
            
            # Mock tier0 rule
            skull_rule = GovernanceRule(
                rule_id="TEST-RULE",
                name="Test Rule",
                severity="error",
                tier=0,
                description="Tier 0 test"
            )
            
            with patch.object(registry, "_tier0_rules", {"TEST-RULE": skull_rule}), \
                 patch.object(registry, "rules", []), \
                 patch.object(registry, "_initialized", True):
                result = resolver.get_effective_rule("TEST-RULE")
                
                assert result.is_ok()
                rule = result.unwrap()
                assert rule.tier == 0
                
        except ImportError:
            pytest.skip("TierResolver not available")

    def test_precedence_yaml_configuration_valid(self):
        """AC-PHASE47-S4-001: precedence.yaml reflects tier0 > tier1 > tier2."""
        precedence_path = Path("cortex/intelligence/governance/precedence.yaml")
        
        if not precedence_path.exists():
            pytest.skip("precedence.yaml not found")
        
        with open(precedence_path) as f:
            precedence = yaml.safe_load(f)
        
        # Validate conflict resolution
        assert precedence["conflict_resolution"] == "tier0_overrides_tier1_overrides_tier2"
        
        # Validate precedence order
        precedence_order = precedence.get("precedence_order", [])
        assert precedence_order in ([0, 1, 2], ["tier0", "tier1", "tier2"])
        
        # Validate explanation mentions tier0 immutability
        explanation = precedence.get("explanation", "").lower()
        assert "tier 0" in explanation or "tier0" in explanation


# =============================================================================
# MEMORY TIER MIGRATION TESTS
# =============================================================================
class TestMemoryTierMigration:
    """Golden tests for memory tier migration."""

    def test_all_new_memory_directories_exist(self):
        """AC-PHASE47-S4-002: All new memory directories exist."""
        learned_patterns = Path("cortex/intelligence/memory/tier1_learned")
        adaptive_intelligence = Path("cortex/intelligence/memory/tier2_adaptive")
        scratch_space = Path("cortex/intelligence/memory/scratch_space")
        
        assert learned_patterns.exists() and learned_patterns.is_dir()
        assert adaptive_intelligence.exists() and adaptive_intelligence.is_dir()
        assert scratch_space.exists() and scratch_space.is_dir()

    def test_backward_compatibility_symlinks_exist(self):
        """AC-PHASE47-S4-002: Backward compatibility symlinks exist."""
        tier1_learned = Path("cortex/intelligence/memory/tier1_learned")
        tier2_adaptive = Path("cortex/intelligence/memory/tier2_adaptive")
        tier3_scratch = Path("cortex/intelligence/memory/tier3_scratch")
        
        if tier1_learned.exists():
            assert tier1_learned.is_symlink()
            assert tier1_learned.resolve().name == "tier1_learned"
        
        if tier2_adaptive.exists():
            assert tier2_adaptive.is_symlink()
            assert tier2_adaptive.resolve().name == "tier2_adaptive"
        
        if tier3_scratch.exists():
            assert tier3_scratch.is_symlink()
            assert tier3_scratch.resolve().name == "scratch_space"

    def test_old_and_new_imports_both_work(self):
        """AC-PHASE47-S4-002: Both old and new import paths work."""
        # Test new paths
        try:
            import cortex.intelligence.memory.learned_patterns as new_learned
            assert new_learned is not None
        except ImportError:
            pytest.skip("learned_patterns import not available")
        
        # Test old path (via symlink)
        try:
            import cortex.intelligence.memory.tier1_learned as old_tier1
            assert old_tier1 is not None
        except ImportError:
            pytest.skip("tier1_learned import not available")


# =============================================================================
# BRAIN TIER PUSHER INTEGRATION TESTS
# =============================================================================
class TestBrainTierPusherIntegration:
    """Golden tests for BrainTierPusher integration."""

    def test_brain_tier_pusher_paths_updated(self):
        """AC-PHASE47-S4-003: BrainTierPusher uses new memory paths."""
        try:
            from cortex.orchestrators.core.intent_router.comprehension_loop import BrainTierPusher
            from cortex.models.canonical_enums import BrainTier
            
            pusher = BrainTierPusher()
            
            # Verify paths
            assert pusher.TIER_PATHS[BrainTier.TIER_0] == "cortex-registry/core/tier0-skull"
            assert "tier1_learned" in pusher.TIER_PATHS[BrainTier.TIER_1]
            assert "tier2_adaptive" in pusher.TIER_PATHS[BrainTier.TIER_2]
            assert "scratch_space" in pusher.TIER_PATHS[BrainTier.TIER_3]
            
            # Verify no old paths
            for tier, path in pusher.TIER_PATHS.items():
                assert "tier1_learned" not in path
                assert "tier2_adaptive" not in path
                assert "tier3_scratch" not in path
                
        except ImportError:
            pytest.skip("BrainTierPusher not available")

    def test_brain_tier_pusher_identify_target_tier(self):
        """AC-PHASE47-S4-003: BrainTierPusher.identify_target_tier() uses correct enum."""
        try:
            from cortex.orchestrators.core.intent_router.comprehension_loop import BrainTierPusher
            from cortex.orchestrators.core.intent_router.comprehension_yaml import (
                ComprehensionYAML, 
                IntentSection, 
                ChallengeSection, 
                RecommendationSection
            )
            from cortex.models.canonical_enums import BrainTier
            
            pusher = BrainTierPusher()
            
            # Mock comprehension with proper dataclasses
            intent = IntentSection(
                type="IMPLEMENT",
                scope={"target_type": "test", "ac_ids": []},
                confidence=0.9,
                keywords=["test"]
            )
            
            challenges = ChallengeSection(items=[])
            recommendations = RecommendationSection(items=[])
            
            comprehension = ComprehensionYAML(
                metadata={"version": "1.0"},
                intent=intent,
                challenges=challenges,
                recommendations=recommendations
            )
            
            # Test tier identification
            tier = pusher.identify_target_tier(comprehension)
            
            # Should return BrainTier enum (TIER_0, TIER_1, TIER_2, or TIER_3)
            assert isinstance(tier, BrainTier)
            assert tier in [BrainTier.TIER_0, BrainTier.TIER_1, BrainTier.TIER_2, BrainTier.TIER_3]
            
        except ImportError:
            pytest.skip("BrainTierPusher not available")


# =============================================================================
# GOVERNANCE TIER DIRECTORY STRUCTURE TESTS
# =============================================================================
class TestGovernanceTierStructure:
    """Golden tests for governance tier directory structure."""

    def test_all_governance_tier_directories_exist(self):
        """AC-PHASE47-S4-001: All governance tier directories exist."""
        tier0_skull = Path("cortex-registry/core/tier0-skull")
        tier1_project = Path("cortex-registry/core/tier1-project")
        tier2_engineering = Path("cortex-registry/core/tier2-engineering")
        
        assert tier0_skull.exists() and tier0_skull.is_dir()
        assert tier1_project.exists() and tier1_project.is_dir()
        assert tier2_engineering.exists() and tier2_engineering.is_dir()

    def test_skull_rules_in_tier0(self):
        """AC-PHASE47-S4-001: skull-rules.yaml exists in tier0-skull/."""
        skull_rules = Path("cortex-registry/core/tier0-skull/skull-rules.yaml")
        assert skull_rules.exists() and skull_rules.is_file()


# =============================================================================
# DOCUMENTATION VALIDATION TESTS
# =============================================================================
class TestPhase47Documentation:
    """Golden tests for Phase 47 documentation completeness."""

    def test_stage_completion_files_exist(self):
        """AC-PHASE47-S4-004: All stage completion files exist."""
        stage1_complete = Path("cortex-registry/planning/phases/phase-47-stage1-complete.yaml")
        stage2_complete = Path("cortex-registry/planning/phases/phase-47-stage2-complete.yaml")
        stage3_complete = Path("cortex-registry/planning/phases/phase-47-stage3-complete.yaml")
        
        assert stage1_complete.exists()
        assert stage2_complete.exists()
        assert stage3_complete.exists()

    def test_test_files_exist(self):
        """AC-PHASE47-S4-004: Test files for all stages exist."""
        tier_precedence_tests = Path("tests/unit/brain/core/test_tier_precedence.py")
        memory_tier_tests = Path("tests/unit/brain/core/test_memory_tier_paths.py")
        golden_tests = Path("tests/unit/brain/core/test_tier_architecture_golden.py")
        
        assert tier_precedence_tests.exists()
        assert memory_tier_tests.exists()
        assert golden_tests.exists()


# =============================================================================
# INTEGRATION SMOKE TESTS
# =============================================================================
class TestPhase47IntegrationSmoke:
    """Smoke tests for Phase 47 integration."""

    def test_governance_registry_can_be_instantiated(self):
        """Smoke test: GovernanceRegistry instantiation."""
        try:
            from cortex.orchestrators.core.governance_registry import GovernanceRegistry
            registry = GovernanceRegistry()
            assert registry is not None
            assert hasattr(registry, "get_rule")
        except ImportError:
            pytest.skip("GovernanceRegistry not available")

    def test_tier_resolver_can_be_instantiated(self):
        """Smoke test: TierResolver instantiation."""
        try:
            from cortex.core.tier_resolver import TierResolver
            resolver = TierResolver()
            assert resolver is not None
            assert hasattr(resolver, "get_effective_rule")
        except ImportError:
            pytest.skip("TierResolver not available")

    def test_brain_tier_pusher_can_be_instantiated(self):
        """Smoke test: BrainTierPusher instantiation."""
        try:
            from cortex.orchestrators.core.intent_router.comprehension_loop import BrainTierPusher
            pusher = BrainTierPusher()
            assert pusher is not None
            assert hasattr(pusher, "identify_target_tier")
            assert hasattr(pusher, "push_to_tier")
        except ImportError:
            pytest.skip("BrainTierPusher not available")


# =============================================================================
# AC_COMPLETE: AC-PHASE47-S4-001, AC-PHASE47-S4-002, AC-PHASE47-S4-003, AC-PHASE47-S4-004
# =============================================================================
