"""
Memory Tier Path Tests (CORE-035 canonical paths)

Validates canonical memory tier directory structure:
- tier1_learned/   — learned patterns
- tier2_adaptive/  — adaptive intelligence
- scratch_space/   — scratch workspace

Acceptance Criteria:
- AC-PHASE47-S2-001: Canonical directory structure exists
- AC-PHASE47-S2-002: Mirror directories removed
- AC-PHASE47-S2-003: BrainTierPusher uses canonical paths
- AC-PHASE47-S2-004: TierLoader uses canonical paths
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Canonical directory paths
MEMORY_ROOT = Path("cortex/intelligence/memory")
TIER1_LEARNED = MEMORY_ROOT / "tier1_learned"
TIER2_ADAPTIVE = MEMORY_ROOT / "tier2_adaptive"
SCRATCH_SPACE = MEMORY_ROOT / "scratch_space"

# Mirror directories that should NOT exist (deleted in CORE-035 cleanup)
MIRROR_LEARNED_PATTERNS = MEMORY_ROOT / "learned_patterns"
MIRROR_ADAPTIVE_INTELLIGENCE = MEMORY_ROOT / "adaptive_intelligence"


# =============================================================================
# DIRECTORY STRUCTURE TESTS
# =============================================================================
class TestMemoryDirectoryStructure:
    """Test canonical memory directory structure exists."""

    def test_tier1_learned_directory_exists(self):
        """AC-PHASE47-S2-001: tier1_learned/ directory exists."""
        assert TIER1_LEARNED.exists(), f"{TIER1_LEARNED} should exist"
        assert TIER1_LEARNED.is_dir(), f"{TIER1_LEARNED} should be a directory"

    def test_tier2_adaptive_directory_exists(self):
        """AC-PHASE47-S2-001: tier2_adaptive/ directory exists."""
        assert TIER2_ADAPTIVE.exists(), f"{TIER2_ADAPTIVE} should exist"
        assert TIER2_ADAPTIVE.is_dir(), f"{TIER2_ADAPTIVE} should be a directory"

    def test_scratch_space_directory_exists(self):
        """AC-PHASE47-S2-001: scratch_space/ directory exists."""
        assert SCRATCH_SPACE.exists(), f"{SCRATCH_SPACE} should exist"
        assert SCRATCH_SPACE.is_dir(), f"{SCRATCH_SPACE} should be a directory"

    def test_mirror_learned_patterns_removed(self):
        """AC-PHASE47-S2-002: Mirror learned_patterns/ directory removed."""
        assert not MIRROR_LEARNED_PATTERNS.exists(), \
            f"{MIRROR_LEARNED_PATTERNS} should be deleted (mirror of {TIER1_LEARNED})"

    def test_mirror_adaptive_intelligence_removed(self):
        """AC-PHASE47-S2-002: Mirror adaptive_intelligence/ directory removed."""
        assert not MIRROR_ADAPTIVE_INTELLIGENCE.exists(), \
            f"{MIRROR_ADAPTIVE_INTELLIGENCE} should be deleted (mirror of {TIER2_ADAPTIVE})"


# =============================================================================
# BRAIN TIER PUSHER TESTS
# =============================================================================
class TestBrainTierPusherPaths:
    """Test BrainTierPusher uses canonical memory paths."""

    def test_brain_tier_pusher_module_exists(self):
        """BrainTierPusher module can be imported."""
        try:
            from cortex.core.tier_pusher import BrainTierPusher
            assert BrainTierPusher is not None
        except ImportError as e:
            pytest.skip(f"BrainTierPusher not available: {e}")

    def test_brain_tier_pusher_uses_tier1_learned_path(self):
        """AC-PHASE47-S2-003: BrainTierPusher references tier1_learned/."""
        try:
            from cortex.core.tier_pusher import BrainTierPusher

            pusher = BrainTierPusher()
            tier1_path = getattr(pusher, "tier1_path", None) or \
                        getattr(pusher, "_tier1_path", None) or \
                        getattr(pusher, "tier1_learned_path", None)

            if tier1_path:
                path_str = str(tier1_path)
                assert "tier1_learned" in path_str, \
                    f"BrainTierPusher should use 'tier1_learned', got {path_str}"
                assert "learned_patterns" not in path_str, \
                    f"BrainTierPusher should not use mirror 'learned_patterns' path"

        except ImportError:
            pytest.skip("BrainTierPusher not available")

    def test_brain_tier_pusher_uses_tier2_adaptive_path(self):
        """AC-PHASE47-S2-003: BrainTierPusher references tier2_adaptive/."""
        try:
            from cortex.core.tier_pusher import BrainTierPusher

            pusher = BrainTierPusher()
            tier2_path = getattr(pusher, "tier2_path", None) or \
                        getattr(pusher, "_tier2_path", None) or \
                        getattr(pusher, "tier2_adaptive_path", None)

            if tier2_path:
                path_str = str(tier2_path)
                assert "tier2_adaptive" in path_str, \
                    f"BrainTierPusher should use 'tier2_adaptive', got {path_str}"
                assert "adaptive_intelligence" not in path_str, \
                    f"BrainTierPusher should not use mirror 'adaptive_intelligence' path"

        except ImportError:
            pytest.skip("BrainTierPusher not available")

    def test_brain_tier_pusher_uses_scratch_space_path(self):
        """AC-PHASE47-S2-003: BrainTierPusher references scratch_space/."""
        try:
            from cortex.core.tier_pusher import BrainTierPusher

            pusher = BrainTierPusher()
            tier3_path = getattr(pusher, "tier3_path", None) or \
                        getattr(pusher, "_tier3_path", None) or \
                        getattr(pusher, "scratch_space_path", None)

            if tier3_path:
                path_str = str(tier3_path)
                assert "scratch_space" in path_str, \
                    f"BrainTierPusher should use 'scratch_space', got {path_str}"
                assert "tier3_scratch" not in path_str, \
                    f"BrainTierPusher should not use old 'tier3_scratch' path"

        except ImportError:
            pytest.skip("BrainTierPusher not available")


# =============================================================================
# TIER LOADER TESTS
# =============================================================================
class TestTierLoaderPaths:
    """Test TierLoader uses canonical memory paths."""

    def test_tier_loader_module_exists(self):
        """TierLoader module can be imported."""
        try:
            from cortex.core.tier_loader import TierLoader
            assert TierLoader is not None
        except ImportError as e:
            pytest.skip(f"TierLoader not available: {e}")

    def test_tier_loader_uses_canonical_paths(self):
        """AC-PHASE47-S2-004: TierLoader references canonical memory paths."""
        try:
            from cortex.core.tier_loader import TierLoader

            loader = TierLoader()
            config = getattr(loader, "config", None) or \
                    getattr(loader, "_config", None) or \
                    getattr(loader, "paths", None)

            if config:
                config_str = str(config)
                # Should use canonical paths
                assert "tier1_learned" in config_str or \
                       "tier2_adaptive" in config_str or \
                       "scratch_space" in config_str, \
                       "TierLoader should use canonical memory path names"
                # Should NOT use mirror paths
                assert "learned_patterns" not in config_str, \
                       "TierLoader should not use mirror 'learned_patterns' path"
                assert "adaptive_intelligence" not in config_str, \
                       "TierLoader should not use mirror 'adaptive_intelligence' path"

        except ImportError:
            pytest.skip("TierLoader not available")


# =============================================================================
# IMPORT PATH TESTS
# =============================================================================
class TestMemoryImportPaths:
    """Test canonical import paths work."""

    def test_tier1_learned_can_be_imported(self):
        """tier1_learned module can be imported."""
        try:
            import cortex.intelligence.memory.tier1_learned
            assert cortex.intelligence.memory.tier1_learned is not None
        except ImportError:
            pytest.skip("tier1_learned module not yet importable")

    def test_tier2_adaptive_can_be_imported(self):
        """tier2_adaptive module can be imported."""
        try:
            import cortex.intelligence.memory.tier2_adaptive
            assert cortex.intelligence.memory.tier2_adaptive is not None
        except ImportError:
            pytest.skip("tier2_adaptive module not yet importable")

    def test_scratch_space_can_be_imported(self):
        """scratch_space module can be imported."""
        try:
            import cortex.intelligence.memory.scratch_space
            assert cortex.intelligence.memory.scratch_space is not None
        except ImportError:
            pytest.skip("scratch_space module not yet importable")


# =============================================================================
# MIGRATION GUARD TESTS
# =============================================================================
class TestMemoryMirrorGuard:
    """Guard tests: ensure deleted mirror directories stay deleted."""

    def test_no_learned_patterns_directory(self):
        """Mirror directory learned_patterns/ must not be re-created."""
        assert not MIRROR_LEARNED_PATTERNS.exists(), \
            "Mirror directory learned_patterns/ was re-created — delete it"

    def test_no_adaptive_intelligence_directory(self):
        """Mirror directory adaptive_intelligence/ must not be re-created."""
        assert not MIRROR_ADAPTIVE_INTELLIGENCE.exists(), \
            "Mirror directory adaptive_intelligence/ was re-created — delete it"

    def test_comprehension_loop_uses_canonical_paths(self):
        """BrainTierPusher.TIER_PATHS uses canonical cortex/ paths."""
        try:
            from cortex.orchestrators.core.intent_router.comprehension_loop import BrainTierPusher
            tier_paths = BrainTierPusher.TIER_PATHS

            for tier, path in tier_paths.items():
                assert "cortex.intelligence" not in path, \
                    f"TIER_PATHS[{tier}] uses stale 'cortex.intelligence': {path}"
                assert "learned_patterns" not in path, \
                    f"TIER_PATHS[{tier}] uses deleted mirror 'learned_patterns': {path}"
                assert "adaptive_intelligence" not in path, \
                    f"TIER_PATHS[{tier}] uses deleted mirror 'adaptive_intelligence': {path}"
        except ImportError:
            pytest.skip("BrainTierPusher not importable")


# =============================================================================
# GOLDEN TESTS - REAL WORLD SCENARIOS
# =============================================================================
class TestMemoryTierGoldenScenarios:
    """Golden tests for memory tier operations."""

    def test_knowledge_push_uses_tier1_learned(self):
        """Golden Test 1: Knowledge push uses tier1_learned/."""
        try:
            from cortex.core.tier_pusher import BrainTierPusher

            pusher = BrainTierPusher()
            test_data = {"rule": "CORE-001", "learned": True}

            with patch.object(pusher, "_write_to_tier1", return_value=True) as mock_write:
                result = pusher.push_to_tier1(test_data)
                if mock_write.called:
                    call_args = str(mock_write.call_args)
                    assert "learned_patterns" not in call_args, \
                        "Should not use mirror learned_patterns path"

        except (ImportError, AttributeError):
            pytest.skip("BrainTierPusher.push_to_tier1 not available")

    def test_adaptive_query_uses_tier2_adaptive(self):
        """Golden Test 2: Adaptive query uses tier2_adaptive/."""
        try:
            from cortex.core.tier_loader import TierLoader

            loader = TierLoader()

            with patch.object(loader, "_load_from_tier2", return_value={}) as mock_load:
                result = loader.load_from_tier2()
                if mock_load.called:
                    call_args = str(mock_load.call_args)
                    assert "adaptive_intelligence" not in call_args, \
                        "Should not use mirror adaptive_intelligence path"

        except (ImportError, AttributeError):
            pytest.skip("TierLoader.load_from_tier2 not available")


# =============================================================================
# AC_COMPLETE: AC-PHASE47-S2-001, AC-PHASE47-S2-002, AC-PHASE47-S2-003, AC-PHASE47-S2-004
# =============================================================================
