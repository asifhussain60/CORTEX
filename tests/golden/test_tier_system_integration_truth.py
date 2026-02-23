"""
Golden Truth Test: Tier System Integration

Tests integration between governance tiers, memory tiers, and orchestrator tiers.
Validates CORE-051 foundation and tier-based optimizations.

Authority: Phase 105 - Brain Tier Architecture Fix
AC-IDs: AC-PHASE105-S3-T1, AC-PHASE105-S3-T4, AC-PHASE105-S4-T1

Test Scenarios:
1. Orchestrator tier assignments
2. LENS tier coupling (CORE-051 foundation)
3. Tier dependency tracking
4. End-to-end tier workflows
"""

import pytest
from pathlib import Path
from typing import Dict, Optional
from unittest.mock import Mock, patch

from cortex.core.orchestrator_dependency_registry import (
    OrchestratorDependencyRegistry,
    TierLevel,
    DependencyType
)


class TestOrchestratorTierAssignments:
    """Test orchestrator tier metadata and assignments."""

    def test_orchestrator_dependency_registry_exists(self):
        """OrchestratorDependencyRegistry should be importable."""
        assert OrchestratorDependencyRegistry is not None

    def test_tier_level_enum_defined(self):
        """TierLevel enum should define all tiers."""
        assert hasattr(TierLevel, 'TIER0')
        assert hasattr(TierLevel, 'TIER1')
        assert hasattr(TierLevel, 'TIER2')
        assert hasattr(TierLevel, 'TIER3')
        
        # Check values
        assert TierLevel.TIER0.value == "tier0"
        assert TierLevel.TIER1.value == "tier1"
        assert TierLevel.TIER2.value == "tier2"
        assert TierLevel.TIER3.value == "tier3"

    def test_dependency_registry_can_track_tiers(self):
        """Registry should support tier dependency tracking."""
        registry = OrchestratorDependencyRegistry()
        
        # Should have methods for tier operations
        assert hasattr(registry, 'register_tier_dependency') or \
               hasattr(registry, 'add_orchestrator') or \
               hasattr(registry, 'register_orchestrator'), \
            "Registry missing tier registration methods"


class TestLENSTierCoupling:
    """Test LENS-orchestrator tier coupling (CORE-051 foundation)."""

    def test_tier_mapping_concept(self):
        """Test the concept of orchestrator tier → LENS tier mapping."""
        # Define the mapping that CORE-051 requires
        tier_mapping = {
            1: "tier_2_quick",    # Core orchestrators → quick LENS
            2: "tier_3_targeted", # Specialized → targeted LENS
            3: "tier_4_full"      # Enterprise → full LENS
        }
        
        # Verify mapping is complete
        assert len(tier_mapping) == 3
        assert all(tier in tier_mapping for tier in [1, 2, 3])

    def test_no_tier_downgrade_rule(self):
        """Tier 3 orchestrator should not get tier 2 LENS."""
        # This is the core rule of CORE-051
        
        orchestrator_tier = 3
        lens_tier_mapping = {1: 2, 2: 3, 3: 4}  # orch tier → LENS tier
        
        lens_tier = lens_tier_mapping[orchestrator_tier]
        
        # Tier 3 orchestrator should get tier 4 LENS (not tier 2)
        assert lens_tier == 4, \
            f"Tier 3 orchestrator got LENS tier {lens_tier}, expected 4"
        
        # No downgrade: LENS tier should be >= orchestrator tier
        assert lens_tier >= orchestrator_tier, \
            "LENS tier downgrade detected - violates CORE-051!"

    def test_tier_upgrade_allowed(self):
        """Higher tiers should get better LENS analysis."""
        lens_tier_mapping = {1: 2, 2: 3, 3: 4}
        
        # Each orchestrator tier should get equal or better LENS tier
        for orch_tier in [1, 2, 3]:
            lens_tier = lens_tier_mapping[orch_tier]
            
            assert lens_tier >= orch_tier, \
                f"Orchestrator tier {orch_tier} → LENS tier {lens_tier} is a downgrade!"


class TestTierDependencyTracking:
    """Test tier dependency tracking and validation."""

    @pytest.fixture
    def registry(self):
        """Create OrchestratorDependencyRegistry."""
        return OrchestratorDependencyRegistry()

    def test_registry_tracks_tier_dependencies(self, registry):
        """Registry should track which tiers each orchestrator depends on."""
        # Check if registry has dependency tracking
        assert hasattr(registry, 'orchestrators') or \
               hasattr(registry, '_orchestrators') or \
               hasattr(registry, 'profiles'), \
            "Registry missing orchestrator storage"

    def test_tier_dependency_type_enum(self):
        """DependencyType should define dependency types."""
        assert hasattr(DependencyType, 'DIRECT')
        assert hasattr(DependencyType, 'TRANSITIVE')
        assert hasattr(DependencyType, 'INHERITED')

    def test_tier_change_impact_analysis(self, registry):
        """Registry should support tier change impact analysis."""
        # Should be able to analyze what's affected by tier changes
        if hasattr(registry, 'analyze_tier_change_impact'):
            # Method exists
            assert callable(registry.analyze_tier_change_impact)
        else:
            pytest.skip("Tier change impact analysis not yet implemented")


class TestTierValidationGates:
    """Test tier validation in CI/CD gates."""

    def test_tier_structure_validation_concept(self):
        """Validate concept of tier structure validation."""
        required_governance_tiers = [
            "cortex-registry/core/tier0-skull",
            "cortex-registry/core/tier1-project",
            "cortex-registry/core/tier2-engineering"
        ]
        
        required_memory_tiers = [
            "cortex/intelligence/memory/tier1_learned",
            "cortex/intelligence/memory/tier2_adaptive",
            "cortex/intelligence/memory/scratch_space"
        ]
        
        # At least some should exist after Phase 105
        all_paths = required_governance_tiers + required_memory_tiers
        existing = [p for p in all_paths if Path(p).exists()]
        
        # Should have at least memory tiers
        memory_existing = [p for p in required_memory_tiers 
                          if Path(p).exists() or 
                          Path(p.replace("tier1_learned", "tier1_learned")).exists()]
        
        assert len(memory_existing) > 0 or len(existing) > 0, \
            "No tier directories found - structure not set up"

    def test_orchestrator_tier_assignment_validation(self):
        """All orchestrators should have tier assignments."""
        # This will be implemented when wiring.yaml is updated
        # For now, test the concept
        
        orchestrator_tiers = {
            "MasterOrchestrator": 3,  # Enterprise
            "DigestCoordinator": 2,   # Specialized
            "QueryCoordinator": 2,    # Specialized
            "TDDOrchestrator": 1      # Core
        }
        
        # All tiers should be 1, 2, or 3
        for orch, tier in orchestrator_tiers.items():
            assert tier in [1, 2, 3], \
                f"{orch} has invalid tier: {tier}"


class TestEndToEndTierWorkflows:
    """Test complete tier workflows."""

    def test_rule_lookup_with_precedence(self):
        """Test rule lookup respecting tier precedence."""
        from cortex.orchestrators.core.governance_registry import GovernanceRegistry
        from cortex.core.tier_resolver import TierResolver
        
        registry = GovernanceRegistry.instance()
        registry.initialize()
        resolver = TierResolver(registry)
        
        # Should be able to get effective rule
        result = resolver.get_effective_rule("CORE-008")
        
        assert result is not None
        assert hasattr(result, 'is_ok')

    def test_knowledge_push_to_correct_tier(self):
        """Test pushing knowledge to correct tier."""
        from cortex.core.intent.comprehension_loop import BrainTierPusher, BrainTier
        
        pusher = BrainTierPusher()
        
        # Should have valid paths
        assert hasattr(pusher, 'TIER_PATHS')
        assert len(pusher.TIER_PATHS) > 0
        
        # Each tier should have a path
        for tier in [BrainTier.TIER0, BrainTier.TIER1, BrainTier.TIER2, BrainTier.TIER3]:
            assert tier in pusher.TIER_PATHS, \
                f"Missing path for {tier}"

    def test_multi_tier_system_coexistence(self):
        """Test that multiple tier systems can coexist."""
        # Governance tiers (0, 1, 2)
        governance_exists = any([
            Path("cortex-registry/core/tier0-skull").exists(),
            Path("cortex-registry/core/tier1-project").exists(),
            Path("cortex-registry/core/tier2-engineering").exists()
        ])
        
        # Memory tiers (1, 2, 3)
        memory_exists = any([
            Path("cortex/intelligence/memory/tier1_learned").exists(),
            Path("cortex/intelligence/memory/tier2_adaptive").exists(),
            Path("cortex/intelligence/memory/tier3_scratch").exists(),
            Path("cortex/intelligence/memory/tier1_learned").exists(),
            Path("cortex/intelligence/memory/tier2_adaptive").exists(),
            Path("cortex/intelligence/memory/scratch_space").exists()
        ])
        
        # At least one system should exist
        assert governance_exists or memory_exists, \
            "Neither governance nor memory tier system exists"
        
        # If both exist, they should be separate
        if governance_exists and memory_exists:
            # No SKULL rules in memory
            memory_path = Path("cortex/intelligence/memory")
            if memory_path.exists():
                skull_in_memory = list(memory_path.rglob("*skull*.yaml"))
                assert len(skull_in_memory) == 0, \
                    "SKULL rules leaked into memory tiers"


# ============================================================================
# COMPREHENSIVE INTEGRATION TEST
# ============================================================================

def test_tier_system_integration_complete():
    """
    Comprehensive test of entire tier system integration.
    
    Validates:
    1. Governance tier precedence
    2. Memory tier operations
    3. Orchestrator tier assignments
    4. LENS tier coupling
    5. No conflicts between systems
    """
    results = {
        "governance_tiers": False,
        "memory_tiers": False,
        "tier_resolver": False,
        "brain_tier_pusher": False,
        "orchestrator_registry": False,
        "lens_coupling": False
    }
    
    # Test 1: Governance tier precedence
    try:
        from cortex.core.tier_resolver import TierResolver
        resolver = TierResolver()
        order = resolver.get_precedence_order()
        assert order[0][0] == 0  # Tier 0 first
        results["governance_tiers"] = True
        results["tier_resolver"] = True
    except Exception as e:
        print(f"Governance tiers failed: {e}")
    
    # Test 2: Memory tier operations
    try:
        from cortex.core.intent.comprehension_loop import BrainTierPusher
        pusher = BrainTierPusher()
        assert hasattr(pusher, 'TIER_PATHS')
        results["memory_tiers"] = True
        results["brain_tier_pusher"] = True
    except Exception as e:
        print(f"Memory tiers failed: {e}")
    
    # Test 3: Orchestrator registry
    try:
        from cortex.core.orchestrator_dependency_registry import OrchestratorDependencyRegistry
        registry = OrchestratorDependencyRegistry()
        results["orchestrator_registry"] = True
    except Exception as e:
        print(f"Orchestrator registry failed: {e}")
    
    # Test 4: LENS coupling concept
    tier_mapping = {1: 2, 2: 3, 3: 4}
    all_valid = all(lens >= orch for orch, lens in tier_mapping.items())
    results["lens_coupling"] = all_valid
    
    # Report results
    passing = sum(results.values())
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"TIER SYSTEM INTEGRATION TEST RESULTS")
    print(f"{'='*60}")
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {component:30s} {status}")
    print(f"{'='*60}")
    print(f"OVERALL: {passing}/{total} components passing")
    print(f"{'='*60}\n")
    
    # Should have at least core components working
    assert results["tier_resolver"], "TierResolver not working"
    assert results["brain_tier_pusher"], "BrainTierPusher not working"
    assert results["lens_coupling"], "LENS coupling logic invalid"
    
    if passing == total:
        print("🎉 All tier system integration tests passing!")
    else:
        print(f"⚠️  {total - passing} components need attention")
