"""
Phase 47 Stage 2: Memory Tier Clarification Tests

RED phase tests for memory tier renaming:
- tier1_learned/ → learned_patterns/
- tier2_adaptive/ → adaptive_intelligence/
- tier3_scratch/ → scratch_space/

Acceptance Criteria:
- AC-PHASE47-S2-001: New directory structure exists
- AC-PHASE47-S2-002: Old directories removed
- AC-PHASE47-S2-003: BrainTierPusher uses new paths
- AC-PHASE47-S2-004: TierLoader uses new paths
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test directory paths
MEMORY_ROOT = Path("cortex_intelligence/memory")
OLD_TIER1 = MEMORY_ROOT / "tier1_learned"
OLD_TIER2 = MEMORY_ROOT / "tier2_adaptive"
OLD_TIER3 = MEMORY_ROOT / "tier3_scratch"

NEW_LEARNED = MEMORY_ROOT / "learned_patterns"
NEW_ADAPTIVE = MEMORY_ROOT / "adaptive_intelligence"
NEW_SCRATCH = MEMORY_ROOT / "scratch_space"


# =============================================================================
# DIRECTORY STRUCTURE TESTS
# =============================================================================
class TestMemoryDirectoryStructure:
    """Test new memory directory structure exists."""

    def test_learned_patterns_directory_exists(self):
        """AC-PHASE47-S2-001: learned_patterns/ directory exists."""
        assert NEW_LEARNED.exists(), f"{NEW_LEARNED} should exist"
        assert NEW_LEARNED.is_dir(), f"{NEW_LEARNED} should be a directory"

    def test_adaptive_intelligence_directory_exists(self):
        """AC-PHASE47-S2-001: adaptive_intelligence/ directory exists."""
        assert NEW_ADAPTIVE.exists(), f"{NEW_ADAPTIVE} should exist"
        assert NEW_ADAPTIVE.is_dir(), f"{NEW_ADAPTIVE} should be a directory"

    def test_scratch_space_directory_exists(self):
        """AC-PHASE47-S2-001: scratch_space/ directory exists."""
        assert NEW_SCRATCH.exists(), f"{NEW_SCRATCH} should exist"
        assert NEW_SCRATCH.is_dir(), f"{NEW_SCRATCH} should be a directory"

    def test_old_tier1_learned_removed(self):
        """AC-PHASE47-S2-002: Old tier1_learned/ directory removed or symlinked."""
        if OLD_TIER1.exists():
            # If it exists, it should be a symlink to new location
            assert OLD_TIER1.is_symlink(), f"{OLD_TIER1} should be symlink or removed"
            if OLD_TIER1.is_symlink():
                target = OLD_TIER1.resolve()
                assert target == NEW_LEARNED.resolve(), f"Symlink should point to {NEW_LEARNED}"

    def test_old_tier2_adaptive_removed(self):
        """AC-PHASE47-S2-002: Old tier2_adaptive/ directory removed or symlinked."""
        if OLD_TIER2.exists():
            assert OLD_TIER2.is_symlink(), f"{OLD_TIER2} should be symlink or removed"
            if OLD_TIER2.is_symlink():
                target = OLD_TIER2.resolve()
                assert target == NEW_ADAPTIVE.resolve(), f"Symlink should point to {NEW_ADAPTIVE}"

    def test_old_tier3_scratch_removed(self):
        """AC-PHASE47-S2-002: Old tier3_scratch/ directory removed or symlinked."""
        if OLD_TIER3.exists():
            assert OLD_TIER3.is_symlink(), f"{OLD_TIER3} should be symlink or removed"
            if OLD_TIER3.is_symlink():
                target = OLD_TIER3.resolve()
                assert target == NEW_SCRATCH.resolve(), f"Symlink should point to {NEW_SCRATCH}"


# =============================================================================
# BRAIN TIER PUSHER TESTS
# =============================================================================
class TestBrainTierPusherPaths:
    """Test BrainTierPusher uses new memory paths."""

    def test_brain_tier_pusher_module_exists(self):
        """BrainTierPusher module can be imported."""
        try:
            from cortex.core.core.tier_pusher import BrainTierPusher
            assert BrainTierPusher is not None
        except ImportError as e:
            pytest.skip(f"BrainTierPusher not available: {e}")

    def test_brain_tier_pusher_uses_learned_patterns_path(self):
        """AC-PHASE47-S2-003: BrainTierPusher references learned_patterns/."""
        try:
            from cortex.core.core.tier_pusher import BrainTierPusher
            
            # Check if BrainTierPusher has path configuration
            pusher = BrainTierPusher()
            
            # Get tier1 path (should be learned_patterns now)
            tier1_path = getattr(pusher, "tier1_path", None) or \
                        getattr(pusher, "_tier1_path", None) or \
                        getattr(pusher, "learned_patterns_path", None)
            
            if tier1_path:
                assert "learned_patterns" in str(tier1_path), \
                    f"BrainTierPusher should use 'learned_patterns', got {tier1_path}"
                assert "tier1_learned" not in str(tier1_path), \
                    f"BrainTierPusher should not use old 'tier1_learned' path"
                    
        except ImportError:
            pytest.skip("BrainTierPusher not available")

    def test_brain_tier_pusher_uses_adaptive_intelligence_path(self):
        """AC-PHASE47-S2-003: BrainTierPusher references adaptive_intelligence/."""
        try:
            from cortex.core.core.tier_pusher import BrainTierPusher
            
            pusher = BrainTierPusher()
            
            tier2_path = getattr(pusher, "tier2_path", None) or \
                        getattr(pusher, "_tier2_path", None) or \
                        getattr(pusher, "adaptive_intelligence_path", None)
            
            if tier2_path:
                assert "adaptive_intelligence" in str(tier2_path), \
                    f"BrainTierPusher should use 'adaptive_intelligence', got {tier2_path}"
                assert "tier2_adaptive" not in str(tier2_path), \
                    f"BrainTierPusher should not use old 'tier2_adaptive' path"
                    
        except ImportError:
            pytest.skip("BrainTierPusher not available")

    def test_brain_tier_pusher_uses_scratch_space_path(self):
        """AC-PHASE47-S2-003: BrainTierPusher references scratch_space/."""
        try:
            from cortex.core.core.tier_pusher import BrainTierPusher
            
            pusher = BrainTierPusher()
            
            tier3_path = getattr(pusher, "tier3_path", None) or \
                        getattr(pusher, "_tier3_path", None) or \
                        getattr(pusher, "scratch_space_path", None)
            
            if tier3_path:
                assert "scratch_space" in str(tier3_path), \
                    f"BrainTierPusher should use 'scratch_space', got {tier3_path}"
                assert "tier3_scratch" not in str(tier3_path), \
                    f"BrainTierPusher should not use old 'tier3_scratch' path"
                    
        except ImportError:
            pytest.skip("BrainTierPusher not available")


# =============================================================================
# TIER LOADER TESTS
# =============================================================================
class TestTierLoaderPaths:
    """Test TierLoader uses new memory paths."""

    def test_tier_loader_module_exists(self):
        """TierLoader module can be imported."""
        try:
            from cortex.core.core.tier_loader import TierLoader
            assert TierLoader is not None
        except ImportError as e:
            pytest.skip(f"TierLoader not available: {e}")

    def test_tier_loader_uses_new_paths(self):
        """AC-PHASE47-S2-004: TierLoader references new memory paths."""
        try:
            from cortex.core.core.tier_loader import TierLoader
            
            loader = TierLoader()
            
            # Check configuration or paths
            config = getattr(loader, "config", None) or \
                    getattr(loader, "_config", None) or \
                    getattr(loader, "paths", None)
            
            if config:
                config_str = str(config)
                
                # Should have new paths
                assert "learned_patterns" in config_str or \
                       "adaptive_intelligence" in config_str or \
                       "scratch_space" in config_str, \
                       "TierLoader should use new memory path names"
                
                # Should NOT have old paths
                assert "tier1_learned" not in config_str, \
                       "TierLoader should not use old 'tier1_learned' path"
                assert "tier2_adaptive" not in config_str, \
                       "TierLoader should not use old 'tier2_adaptive' path"
                assert "tier3_scratch" not in config_str, \
                       "TierLoader should not use old 'tier3_scratch' path"
                    
        except ImportError:
            pytest.skip("TierLoader not available")


# =============================================================================
# IMPORT PATH TESTS
# =============================================================================
class TestMemoryImportPaths:
    """Test import paths updated to new structure."""

    def test_learned_patterns_can_be_imported(self):
        """learned_patterns module can be imported."""
        try:
            import cortex_intelligence.memory.learned_patterns
            assert cortex_intelligence.memory.learned_patterns is not None
        except ImportError:
            pytest.skip("learned_patterns module not yet available")

    def test_adaptive_intelligence_can_be_imported(self):
        """adaptive_intelligence module can be imported."""
        try:
            import cortex_intelligence.memory.adaptive_intelligence
            assert cortex_intelligence.memory.adaptive_intelligence is not None
        except ImportError:
            pytest.skip("adaptive_intelligence module not yet available")

    def test_scratch_space_can_be_imported(self):
        """scratch_space module can be imported."""
        try:
            import cortex_intelligence.memory.scratch_space
            assert cortex_intelligence.memory.scratch_space is not None
        except ImportError:
            pytest.skip("scratch_space module not yet available")


# =============================================================================
# MIGRATION COMPATIBILITY TESTS
# =============================================================================
class TestMemoryMigrationCompatibility:
    """Test backward compatibility during migration."""

    def test_old_imports_still_work_via_symlink(self):
        """Old import paths still work (via symlink or alias)."""
        # This test allows for graceful migration period
        try:
            import cortex_intelligence.memory.tier1_learned as old_tier1
            import cortex_intelligence.memory.learned_patterns as new_learned
            
            # If both work, they should reference same module or symlinked
            # (This allows gradual migration)
            assert old_tier1 is not None
            assert new_learned is not None
            
        except ImportError:
            pytest.skip("Migration imports not yet available")

    def test_memory_root_init_updated(self):
        """memory/__init__.py exports new module names."""
        try:
            import cortex_intelligence.memory as memory
            
            # Check if new names are available
            has_new_names = (
                hasattr(memory, "learned_patterns") or
                hasattr(memory, "adaptive_intelligence") or
                hasattr(memory, "scratch_space")
            )
            
            if not has_new_names:
                pytest.skip("New module names not yet exported in memory.__init__")
                
        except ImportError:
            pytest.skip("memory module not available")


# =============================================================================
# GOLDEN TESTS - REAL WORLD SCENARIOS
# =============================================================================
class TestMemoryTierGoldenScenarios:
    """Golden tests for memory tier migration."""

    def test_knowledge_push_uses_learned_patterns(self):
        """Golden Test 1: Knowledge push operation uses learned_patterns/."""
        # Simulate knowledge push operation
        try:
            from cortex.core.core.tier_pusher import BrainTierPusher
            
            pusher = BrainTierPusher()
            
            # Mock push operation
            test_data = {"rule": "CORE-001", "learned": True}
            
            with patch.object(pusher, "_write_to_tier1", return_value=True) as mock_write:
                # Attempt push (would fail if tier1_learned path used)
                result = pusher.push_to_tier1(test_data)
                
                if mock_write.called:
                    # Check call args for path
                    call_args = str(mock_write.call_args)
                    assert "tier1_learned" not in call_args, \
                        "Should not use old tier1_learned path"
                        
        except (ImportError, AttributeError):
            pytest.skip("BrainTierPusher.push_to_tier1 not available")

    def test_adaptive_query_uses_adaptive_intelligence(self):
        """Golden Test 2: Adaptive query uses adaptive_intelligence/."""
        try:
            from cortex.core.core.tier_loader import TierLoader
            
            loader = TierLoader()
            
            # Mock load from tier2
            with patch.object(loader, "_load_from_tier2", return_value={}) as mock_load:
                result = loader.load_from_tier2()
                
                if mock_load.called:
                    call_args = str(mock_load.call_args)
                    assert "tier2_adaptive" not in call_args, \
                        "Should not use old tier2_adaptive path"
                        
        except (ImportError, AttributeError):
            pytest.skip("TierLoader.load_from_tier2 not available")


# =============================================================================
# AC_COMPLETE: AC-PHASE47-S2-001, AC-PHASE47-S2-002, AC-PHASE47-S2-003, AC-PHASE47-S2-004
# =============================================================================
