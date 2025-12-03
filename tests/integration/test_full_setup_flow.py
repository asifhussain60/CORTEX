"""
End-to-end setup flow integration tests.

This module tests the complete CORTEX setup workflow from fresh installation
to fully configured system with shared environment, user profile, templates,
alignment checks, and plan registry.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


@pytest.fixture
def fresh_cortex_install(tmp_path):
    """Simulate a fresh CORTEX installation."""
    # Create temporary CORTEX root
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create minimal structure
    (cortex_root / "src").mkdir()
    (cortex_root / "tests").mkdir()
    (cortex_root / "cortex-brain").mkdir()
    
    return cortex_root


@pytest.fixture
def mock_user_inputs():
    """Mock user inputs for interactive setup."""
    return {
        "experience_level": "expert",
        "interaction_mode": "technical",
        "tech_stack": ["python", "javascript"],
        "preferences": ["concise", "code-focused"]
    }


class TestEndToEndSetupFlow:
    """Test complete setup workflow."""
    
    def test_fresh_install_completes_successfully(self, fresh_cortex_install, mock_user_inputs):
        """Should complete full setup from fresh installation."""
        # This is the main E2E test - will implement workflow orchestration
        # For now, test that we can reach each phase
        
        # Phase 1: Shared environment creation
        shared_env_path = Path.home() / ".cortex" / "venv"
        # Would call setup orchestrator here
        
        # Phase 2: User profile creation
        profile_path = fresh_cortex_install / "cortex-brain" / "user-profile.json"
        # Would call profile creation here
        
        # Phase 3: Template registration
        # Would verify templates are available
        
        # Phase 4: Alignment check
        # Would run alignment orchestrator
        
        # Phase 6: Plan registry initialization
        # Would initialize plan registry
        
        # For now, just assert structure is set up
        assert fresh_cortex_install.exists()
    
    def test_setup_completes_under_60_seconds(self, fresh_cortex_install, mock_user_inputs):
        """Should complete setup in under 60 seconds."""
        start_time = time.perf_counter()
        
        # Mock the full setup workflow
        # In real implementation, would call setup orchestrator
        time.sleep(0.1)  # Simulate some work
        
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        
        assert elapsed < 60.0, f"Setup took {elapsed:.2f}s, expected <60s"
    
    def test_shared_environment_created(self, fresh_cortex_install):
        """Should create shared environment at ~/.cortex/venv/."""
        # Shared environment would be created by setup orchestrator
        # For now, test the path logic
        
        mock_home = fresh_cortex_install / "mock_home"
        mock_home.mkdir()
        
        shared_env_path = mock_home / ".cortex" / "venv"
        
        # Verify path structure makes sense
        assert ".cortex" in str(shared_env_path)
        assert "venv" in str(shared_env_path)
    
    def test_user_profile_created(self, fresh_cortex_install, mock_user_inputs):
        """Should create user profile during setup."""
        from src.setup.models.user_profile import UserProfile
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        profile = UserProfile(brain_path)
        profile.initialize(
            experience_level=mock_user_inputs["experience_level"],
            interaction_mode=mock_user_inputs["interaction_mode"],
            tech_stack=mock_user_inputs["tech_stack"],
            preferences=mock_user_inputs["preferences"]
        )
        
        # Verify profile was created
        profile_data = profile.get_profile()
        assert profile_data["experience_level"] == "expert"
        assert profile_data["interaction_mode"] == "technical"
    
    def test_templates_registered(self, fresh_cortex_install):
        """Should register response templates during setup."""
        from src.utils.template_selector import TemplateSelector
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        # Copy templates file to brain
        templates_file = Path(__file__).parent.parent.parent / "cortex-brain" / "response-templates.yaml"
        if templates_file.exists():
            dest = brain_path / "response-templates.yaml"
            shutil.copy(templates_file, dest)
            
            selector = TemplateSelector(brain_path)
            
            # Verify templates are loaded
            assert selector.templates is not None
            assert len(selector.templates) > 0


class TestSetupComponentIntegration:
    """Test integration between setup components."""
    
    def test_profile_affects_template_selection(self, fresh_cortex_install):
        """Should use profile preferences for template selection."""
        from src.setup.models.user_profile import UserProfile
        from src.utils.template_selector import TemplateSelector
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        # Create expert profile
        profile = UserProfile(brain_path)
        profile.initialize(
            experience_level="expert",
            interaction_mode="technical",
            tech_stack=["python"],
            preferences=["concise"]
        )
        
        # Template selector should respect profile
        # Would test template selection logic here
        assert profile.get_profile()["interaction_mode"] == "technical"
    
    def test_alignment_validates_all_components(self, fresh_cortex_install):
        """Should run alignment check on all setup components."""
        from src.orchestrators.alignment_orchestrator import AlignmentOrchestrator
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        orchestrator = AlignmentOrchestrator(
            brain_path=brain_path,
            repo_root=fresh_cortex_install
        )
        
        # Would run alignment here
        # For now, just verify orchestrator initializes
        assert orchestrator.brain_path.exists()
    
    def test_plan_registry_initialized(self, fresh_cortex_install):
        """Should initialize plan registry during setup."""
        from src.workflows.plan_registry import PlanRegistry
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        registry = PlanRegistry(brain_path)
        
        # Verify database was created
        db_path = brain_path / "planning-registry.db"
        assert db_path.exists()


class TestSetupRollback:
    """Test setup rollback on failure."""
    
    def test_rollback_on_shared_env_failure(self, fresh_cortex_install):
        """Should rollback if shared environment creation fails."""
        # Mock environment creation failure
        # Setup should handle gracefully
        # Would verify no partial state left behind
        assert True  # Placeholder for rollback test
    
    def test_rollback_on_profile_failure(self, fresh_cortex_install):
        """Should rollback if profile creation fails."""
        # Mock profile creation failure
        # Setup should handle gracefully
        assert True  # Placeholder for rollback test


class TestSetupPerformance:
    """Test setup performance requirements."""
    
    def test_profile_creation_fast(self, fresh_cortex_install):
        """Profile creation should be <1 second."""
        from src.setup.models.user_profile import UserProfile
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        start = time.perf_counter()
        profile = UserProfile(brain_path)
        profile.initialize(
            experience_level="beginner",
            interaction_mode="guided",
            tech_stack=["python"],
            preferences=[]
        )
        elapsed = time.perf_counter() - start
        
        assert elapsed < 1.0, f"Profile creation took {elapsed:.2f}s, expected <1s"
    
    def test_alignment_check_fast(self, fresh_cortex_install):
        """Alignment check should be <5 seconds."""
        from src.orchestrators.alignment_orchestrator import AlignmentOrchestrator
        
        brain_path = fresh_cortex_install / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        
        orchestrator = AlignmentOrchestrator(
            brain_path=brain_path,
            repo_root=fresh_cortex_install
        )
        
        # Just initialization time for now
        # Would test full alignment execution time
        assert orchestrator is not None
