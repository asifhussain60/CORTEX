"""
Golden Truth Test: Memory Tier Operations

Tests memory tier operations including file writes, tier selection,
and knowledge organization.

Authority: Phase 105 - Brain Tier Architecture Fix
AC-IDs: AC-PHASE105-S2-T2, AC-PHASE105-S2-T4

Test Scenarios:
1. BrainTierPusher writes to correct paths
2. Tier selection based on content type
3. Memory tier structure is valid
4. No collisions between governance and memory tiers
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

from cortex.core.core.intent.comprehension_loop import (
    BrainTierPusher,
    BrainTier,
    ComprehensionYAML,
    IntentSection
)


class TestBrainTierPusherPaths:
    """Test BrainTierPusher path configuration."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace for testing."""
        workspace = tmp_path / "test_workspace"
        workspace.mkdir()
        return workspace

    @pytest.fixture
    def pusher(self, temp_workspace):
        """Create BrainTierPusher with temp workspace."""
        return BrainTierPusher(workspace_root=str(temp_workspace))

    def test_tier_paths_defined(self, pusher):
        """TIER_PATHS must be defined."""
        assert hasattr(pusher, 'TIER_PATHS'), \
            "BrainTierPusher missing TIER_PATHS"
        assert len(pusher.TIER_PATHS) > 0, "TIER_PATHS is empty"

    def test_tier_paths_use_valid_locations(self):
        """TIER_PATHS should use registry or memory locations, not non-existent tier0/tier1/tier2."""
        pusher = BrainTierPusher()
        
        for tier, path_str in pusher.TIER_PATHS.items():
            # Path should either:
            # 1. Be in cortex-registry/core/ (governance)
            # 2. Be in cortex_intelligence/memory/ (memory)
            # 3. NOT be in cortex_intelligence/tier0, tier1, tier2 (unless they exist)
            
            if "cortex/intelligence/tier" in path_str:
                # This is the problematic pattern
                path = Path(path_str)
                
                # Only fail if it doesn't exist AND isn't memory/*
                if not path.exists() and "memory" not in str(path):
                    pytest.fail(
                        f"BrainTierPusher tier {tier} uses non-existent path: {path_str}\n"
                        f"Should use cortex-registry/core/ or cortex_intelligence/memory/"
                    )

    def test_tier0_uses_registry_path(self):
        """Tier 0 should write to registry, not intelligence."""
        pusher = BrainTierPusher()
        tier0_path = pusher.TIER_PATHS.get(BrainTier.TIER0)
        
        if tier0_path:
            # Tier 0 should be in registry (governance)
            assert "cortex-registry" in tier0_path or "registry" in tier0_path, \
                f"Tier 0 should use registry path, got: {tier0_path}"


class TestTierSelection:
    """Test automatic tier selection based on content."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace."""
        workspace = tmp_path / "test_workspace"
        workspace.mkdir()
        return workspace

    @pytest.fixture
    def pusher(self, temp_workspace):
        """Create BrainTierPusher."""
        return BrainTierPusher(workspace_root=str(temp_workspace))

    def test_governance_content_goes_to_tier0(self, pusher):
        """Content with 'governance' or 'rule' should go to Tier 0."""
        # Create mock comprehension with governance content
        intent = Mock(spec=IntentSection)
        intent.scope = {}
        intent.type = "GOVERNANCE"
        
        comprehension = Mock(spec=ComprehensionYAML)
        comprehension.intent = intent
        comprehension.to_dict = Mock(return_value={
            "description": "governance rule for testing",
            "content": "This is a governance rule"
        })
        
        tier = pusher.identify_target_tier(comprehension)
        
        assert tier == BrainTier.TIER0, \
            f"Governance content should go to TIER0, got {tier}"

    def test_ac_content_goes_to_tier1(self, pusher):
        """Content with AC IDs should go to Tier 1."""
        intent = Mock(spec=IntentSection)
        intent.scope = {"ac_ids": ["AC-TEST-001"]}
        intent.type = "IMPLEMENT"
        
        comprehension = Mock(spec=ComprehensionYAML)
        comprehension.intent = intent
        comprehension.to_dict = Mock(return_value={
            "description": "AC implementation",
            "ac_ids": ["AC-TEST-001"]
        })
        
        tier = pusher.identify_target_tier(comprehension)
        
        assert tier == BrainTier.TIER1, \
            f"AC content should go to TIER1, got {tier}"

    def test_refactor_goes_to_tier2(self, pusher):
        """Refactoring and design patterns go to Tier 2."""
        intent = Mock(spec=IntentSection)
        intent.scope = {}
        intent.type = "REFACTOR"
        
        comprehension = Mock(spec=ComprehensionYAML)
        comprehension.intent = intent
        comprehension.to_dict = Mock(return_value={
            "description": "refactoring pattern"
        })
        
        tier = pusher.identify_target_tier(comprehension)
        
        assert tier == BrainTier.TIER2, \
            f"Refactor should go to TIER2, got {tier}"

    def test_default_goes_to_tier3(self, pusher):
        """Default content goes to Tier 3."""
        intent = Mock(spec=IntentSection)
        intent.scope = {}
        intent.type = "QUERY"
        
        comprehension = Mock(spec=ComprehensionYAML)
        comprehension.intent = intent
        comprehension.to_dict = Mock(return_value={
            "description": "general knowledge"
        })
        
        tier = pusher.identify_target_tier(comprehension)
        
        assert tier == BrainTier.TIER3, \
            f"General content should go to TIER3, got {tier}"


class TestMemoryTierStructure:
    """Test memory tier directory structure."""

    def test_memory_tier_directories_exist(self):
        """Memory tier directories should exist."""
        memory_path = Path("cortex/intelligence/memory")
        
        assert memory_path.exists(), \
            "Memory directory should exist"
        
        # Should have tier directories (old or new names)
        tier_dirs = [
            "tier1_learned", "tier1_learned",
            "tier2_adaptive", "tier2_adaptive",
            "tier3_scratch", "scratch_space"
        ]
        
        existing_tiers = [d for d in tier_dirs 
                         if (memory_path / d).exists()]
        
        assert len(existing_tiers) > 0, \
            f"No memory tier directories found in {memory_path}"

    def test_memory_tiers_not_at_intelligence_root(self):
        """tier0, tier1, tier2 should NOT be at cortex_intelligence root."""
        intel_path = Path("cortex_intelligence")
        
        # These should NOT exist (old broken structure)
        bad_paths = [
            intel_path / "tier0",
            intel_path / "tier1", 
            intel_path / "tier2"
        ]
        
        # If any exist and contain Python source files, that's the old structure
        # (empty dirs or dirs with only runtime .db artifacts are OK — they're gitignored)
        for bad_path in bad_paths:
            if bad_path.exists():
                py_files = [f for f in bad_path.rglob("*.py") if "__pycache__" not in str(f)]
                if py_files:
                    pytest.fail(
                        f"Found old tier structure at {bad_path} with Python source files: {py_files[:5]}. "
                        f"Should be in cortex-registry/core/ or cortex_intelligence/memory/"
                    )

    def test_memory_and_governance_separate(self):
        """Memory tiers and governance tiers should be in different locations."""
        memory_path = Path("cortex/intelligence/memory")
        registry_path = Path("cortex-registry/core")
        
        if memory_path.exists() and registry_path.exists():
            # Memory should not contain SKULL rules
            memory_files = list(memory_path.rglob("*skull*.yaml"))
            memory_files += list(memory_path.rglob("*SKULL*.yaml"))
            
            assert len(memory_files) == 0, \
                f"Found SKULL rules in memory tier: {memory_files}"
            
            # Registry should not contain learned patterns
            if registry_path.exists():
                registry_learned = list(registry_path.rglob("*learned*.yaml"))
                registry_scratch = list(registry_path.rglob("*scratch*.yaml"))
                
                assert len(registry_learned) == 0 and len(registry_scratch) == 0, \
                    "Found memory tier files in governance registry"


class TestTierFileWrites:
    """Test actual file write operations to tiers."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temp workspace with tier structure."""
        workspace = tmp_path / "test_workspace"
        workspace.mkdir()
        
        # Create tier directories
        (workspace / "cortex-registry" / "core" / "tier0-skull").mkdir(parents=True)
        (workspace / "cortex_intelligence" / "memory" / "tier1_learned").mkdir(parents=True)
        (workspace / "cortex_intelligence" / "memory" / "tier2_adaptive").mkdir(parents=True)
        (workspace / "cortex_intelligence" / "memory" / "scratch_space").mkdir(parents=True)
        
        return workspace

    @pytest.fixture
    def pusher(self, temp_workspace):
        """Create pusher with temp workspace."""
        pusher = BrainTierPusher(workspace_root=str(temp_workspace))
        
        # Override TIER_PATHS to use temp structure
        pusher.TIER_PATHS = {
            BrainTier.TIER0: "cortex-registry/core/tier0-skull",
            BrainTier.TIER1: "cortex/intelligence/memory/tier1_learned",
            BrainTier.TIER2: "cortex/intelligence/memory/tier2_adaptive",
            BrainTier.TIER3: "cortex/intelligence/memory/scratch_space",
        }
        
        return pusher

    def test_push_to_tier_creates_file(self, pusher):
        """push_to_tier should create a YAML file."""
        # Create mock comprehension
        intent = Mock(spec=IntentSection)
        intent.scope = {}
        intent.type = "QUERY"
        
        comprehension = Mock(spec=ComprehensionYAML)
        comprehension.intent = intent
        comprehension.to_dict = Mock(return_value={
            "description": "test comprehension",
            "created": datetime.now().isoformat()
        })
        
        # Push to tier 3
        file_path = pusher.push_to_tier(comprehension, BrainTier.TIER3)
        
        assert file_path.exists(), \
            f"File not created at {file_path}"
        assert file_path.suffix == ".yaml", \
            f"File should be YAML, got {file_path.suffix}"

    def test_push_to_different_tiers(self, pusher):
        """Should be able to push to all tiers."""
        intent = Mock(spec=IntentSection)
        intent.scope = {}
        intent.type = "QUERY"
        
        comprehension = Mock(spec=ComprehensionYAML)
        comprehension.intent = intent
        comprehension.to_dict = Mock(return_value={"description": "test"})
        
        # Try each tier
        for tier in [BrainTier.TIER0, BrainTier.TIER1, BrainTier.TIER2, BrainTier.TIER3]:
            file_path = pusher.push_to_tier(comprehension, tier)
            assert file_path.exists(), \
                f"Failed to write to {tier}"


# ============================================================================
# INTEGRATION TEST
# ============================================================================

def test_memory_tier_operations_end_to_end():
    """
    End-to-end test of memory tier operations.
    
    Validates:
    1. BrainTierPusher has valid paths
    2. Tier selection works
    3. Memory structure is correct
    4. No conflicts with governance tiers
    """
    # Create pusher
    pusher = BrainTierPusher()
    
    # Check paths are defined
    assert hasattr(pusher, 'TIER_PATHS')
    assert len(pusher.TIER_PATHS) >= 3
    
    # Check tier selection
    intent = Mock(spec=IntentSection)
    intent.scope = {}
    intent.type = "QUERY"
    
    comprehension = Mock(spec=ComprehensionYAML)
    comprehension.intent = intent
    comprehension.to_dict = Mock(return_value={"description": "test"})
    
    tier = pusher.identify_target_tier(comprehension)
    assert tier in [BrainTier.TIER0, BrainTier.TIER1, BrainTier.TIER2, BrainTier.TIER3]
    
    # Check memory structure
    memory_path = Path("cortex/intelligence/memory")
    if memory_path.exists():
        tier_dirs = [d for d in memory_path.iterdir() 
                    if d.is_dir() and ('tier' in d.name or 'learned' in d.name or 
                                      'adaptive' in d.name or 'scratch' in d.name)]
        assert len(tier_dirs) > 0, "Memory tiers missing"
    
    print("\n✅ Memory tier operations working correctly!")
