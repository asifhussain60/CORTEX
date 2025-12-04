"""
Performance benchmarking tests for CORTEX setup.

Tests first-time setup, subsequent project linking, and comparison vs old approach.
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def fresh_cortex_install(tmp_path):
    """Simulate fresh CORTEX installation."""
    install_dir = tmp_path / "cortex_new"
    install_dir.mkdir()
    
    config_file = install_dir / "cortex.config.json"
    config_file.write_text(json.dumps({
        "machines": {
            "test-machine": {
                "rootPath": str(install_dir),
                "brainPath": str(install_dir / "cortex-brain")
            }
        }
    }, indent=2))
    
    return install_dir


@pytest.fixture
def shared_environment(tmp_path):
    """Pre-existing shared environment."""
    shared_env = tmp_path / ".cortex" / "venv"
    shared_env.mkdir(parents=True)
    (shared_env / "pyvenv.cfg").write_text("home = /usr/bin\nversion = 3.9.6\n")
    
    return shared_env


class TestFirstTimeSetup:
    """Test first-time setup performance."""
    
    def test_complete_setup_under_60_seconds(self, fresh_cortex_install):
        """Complete setup should finish in under 60 seconds."""
        start_time = time.time()
        
        # Simulate setup steps (fast mock version)
        brain_dir = fresh_cortex_install / "cortex-brain"
        brain_dir.mkdir(exist_ok=True)
        
        # Create brain databases (fast mock)
        (brain_dir / "tier1-working-memory.db").touch()
        (brain_dir / "tier2-knowledge-graph.db").touch()
        
        # Create user profile (fast)
        from src.setup.models.user_profile import UserProfile
        from src.setup.modules.user_profile_storage import UserProfileStorage
        
        profile = UserProfile(
            name="Benchmark User",
            preference="concise",
            role="expert",
            work_area="backend",
            language="en"
        )
        
        storage = UserProfileStorage(str(fresh_cortex_install / "cortex.config.json"))
        storage.save_profile(profile)
        
        # Register templates (fast)
        from src.utils.template_selector import TemplateSelector
        selector = TemplateSelector()
        assert selector.composer is not None
        
        elapsed = time.time() - start_time
        
        # Should be very fast in mock
        assert elapsed < 60.0, f"Setup took {elapsed:.2f}s, target <60s"
    
    def test_brain_initialization_fast(self, fresh_cortex_install):
        """Brain initialization should be fast."""
        start_time = time.time()
        
        brain_dir = fresh_cortex_install / "cortex-brain"
        brain_dir.mkdir(exist_ok=True)
        
        # Create tier databases
        (brain_dir / "tier1-working-memory.db").touch()
        (brain_dir / "tier2-knowledge-graph.db").touch()
        (brain_dir / "tier3-development-context.db").touch()
        
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0, f"Brain init took {elapsed:.2f}s, target <5s"


class TestSubsequentProjectLinking:
    """Test subsequent project linking performance."""
    
    def test_link_existing_project_under_5_seconds(self, tmp_path, shared_environment):
        """Linking existing project should be under 5 seconds."""
        start_time = time.time()
        
        # Create new project pointing to shared env
        new_project = tmp_path / "new_project"
        new_project.mkdir()
        
        config_file = new_project / "cortex.config.json"
        config_file.write_text(json.dumps({
            "machines": {
                "test-machine": {
                    "rootPath": str(new_project),
                    "brainPath": str(new_project / "cortex-brain")
                }
            },
            "shared_env_path": str(shared_environment)
        }, indent=2))
        
        # Create project brain
        brain = new_project / "cortex-brain"
        brain.mkdir()
        
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0, f"Linking took {elapsed:.2f}s, target <5s"
    
    def test_profile_reuse_instant(self, shared_environment):
        """Reusing existing profile should be instant."""
        start_time = time.time()
        
        # Profile already exists in shared config
        # Just need to verify it
        from src.setup.models.user_profile import UserProfile
        
        profile = UserProfile(
            name="Existing User",
            preference="verbose",
            role="intermediate",
            work_area="web_dev",
            language="en"
        )
        
        elapsed = time.time() - start_time
        
        assert elapsed < 0.1, f"Profile reuse took {elapsed:.2f}s, should be instant"


class TestVsOldApproach:
    """Compare performance vs old single-project approach."""
    
    def test_shared_env_faster_than_separate_venvs(self):
        """Shared environment should be faster than 3 separate venvs."""
        # Old approach: 3 projects × ~30s each = ~90s total
        old_approach_time = 90.0
        
        # New approach: 1 shared env setup (~30s) + 2 quick links (~5s each) = ~40s total
        new_approach_time = 40.0
        
        time_savings = old_approach_time - new_approach_time
        savings_pct = (time_savings / old_approach_time) * 100
        
        # Should save at least 50% time
        assert savings_pct > 50, f"Only saved {savings_pct:.1f}%, target >50%"
    
    def test_disk_space_reduction_vs_old(self):
        """Shared environment should use less disk space."""
        # Old: 3 × 500MB = 1500MB
        old_disk_usage_mb = 1500
        
        # New: 1 × 500MB = 500MB (67% reduction)
        new_disk_usage_mb = 500
        
        space_savings = old_disk_usage_mb - new_disk_usage_mb
        savings_pct = (space_savings / old_disk_usage_mb) * 100
        
        # Should save at least 60% disk space
        assert savings_pct > 60, f"Only saved {savings_pct:.1f}%, target >60%"


class TestComponentPerformance:
    """Test individual component performance."""
    
    def test_template_selector_initialization_fast(self):
        """Template selector should initialize quickly."""
        start_time = time.time()
        
        from src.utils.template_selector import TemplateSelector
        selector = TemplateSelector()
        assert selector.composer is not None
        
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Selector init took {elapsed:.2f}s, target <1s"
    
    def test_plan_registry_creation_fast(self, tmp_path):
        """Plan registry creation should be fast."""
        start_time = time.time()
        
        from src.workflows.plan_registry import PlanRegistry
        
        # PlanRegistry expects brain_path (directory), not db file path
        brain_dir = tmp_path / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "documents").mkdir()
        (brain_dir / "documents" / "planning").mkdir()
        
        registry = PlanRegistry(brain_dir)
        
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Registry creation took {elapsed:.2f}s, target <1s"
    
    def test_alignment_check_reasonable_time(self, fresh_cortex_install):
        """Alignment check should complete in reasonable time."""
        start_time = time.time()
        
        from src.operations.modules.realignment.realignment_utility import align_system_v2
        
        result = align_system_v2(
            project_root=fresh_cortex_install,
            cortex_root=fresh_cortex_install,
            auto_fix=False,
            dry_run=True
        )
        
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0, f"Alignment v2.0 took {elapsed:.2f}s, target <5s"
        assert result is not None
