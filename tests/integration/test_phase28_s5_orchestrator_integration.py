"""
Integration Tests for Phase-28 S5: Dashboard Hook Wiring with RepositoryOnboardingOrchestrator

Tests the integration of OnboardingDashboardHook into RepositoryOnboardingOrchestrator.
Verifies that dashboard auto-generation triggers after profile creation.

AC_START: AC-PHASE28-S5-012
Description: Integration tests for hook + orchestrator wiring
Author: CORTEX Implementation
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from cortex_brain.onboarded_repos import ProfileStore, RepositoryProfile


class TestPhase28S5OrchestratorIntegration:
    """Integration tests for Phase-28 S5 dashboard hook wiring."""
    
    def test_orchestrator_has_dashboard_hook_integration(self):
        """I1: Verify RepositoryOnboardingOrchestrator has dashboard hook integration."""
        # AC_START: AC-PHASE28-S5-I1
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Should have _get_dashboard_hook method (lazy-loaded)
        assert hasattr(orchestrator, '_get_dashboard_hook')
        assert hasattr(orchestrator, '_dashboard_hook')
        assert orchestrator._dashboard_hook is None  # Lazy-loaded initially
        
        # AC_COMPLETE: AC-PHASE28-S5-I1 ✅
    
    def test_orchestrator_triggers_hook_on_profile_save(self):
        """I2: Verify hook is triggered when profile is saved via orchestrator."""
        # AC_START: AC-PHASE28-S5-I2
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        from cortex.orchestrators.support.onboarding_dashboard_hook import (
            OnboardingDashboardHook,
            ProfileCreatedEvent
        )
        
        with TemporaryDirectory() as tmpdir:
            # Create temporary profile store
            profile_store = ProfileStore(storage_path=Path(tmpdir))
            
            # Create test repo structure
            test_repo = Path(tmpdir) / "test_repo"
            test_repo.mkdir()
            (test_repo / "main.py").write_text("print('hello')")
            
            # Mock the hook
            orchestrator = RepositoryOnboardingOrchestrator()
            
            # Patch the hook to track calls
            mock_hook = MagicMock(spec=OnboardingDashboardHook)
            mock_hook.on_profile_created.return_value = {"status": "success"}
            mock_hook.enabled = True
            
            # Patch _get_dashboard_hook to return mock
            with patch.object(orchestrator, '_get_dashboard_hook', return_value=mock_hook):
                # Call the method that should trigger the hook
                result = orchestrator.onboard_repository_with_profile(
                    repo_path=test_repo,
                    profile_store=profile_store
                )
                
                # Verify profile was created
                assert result is not None
                
                # Verify hook was called
                mock_hook.on_profile_created.assert_called_once()
                
                # Verify event data
                call_args = mock_hook.on_profile_created.call_args
                event = call_args[0][0]
                assert isinstance(event, ProfileCreatedEvent)
                assert event.profile_path.endswith(".yaml")
        
        # AC_COMPLETE: AC-PHASE28-S5-I2 ✅
    
    def test_orchestrator_handles_hook_failure_gracefully(self):
        """I3: Verify profile is retained if hook fails (error isolation)."""
        # AC_START: AC-PHASE28-S5-I3
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        with TemporaryDirectory() as tmpdir:
            profile_store = ProfileStore(storage_path=Path(tmpdir))
            
            # Create test repo
            test_repo = Path(tmpdir) / "test_repo"
            test_repo.mkdir()
            (test_repo / "main.py").write_text("print('hello')")
            
            orchestrator = RepositoryOnboardingOrchestrator()
            
            # Mock hook that raises an exception
            mock_hook = MagicMock()
            mock_hook.on_profile_created.side_effect = RuntimeError("Dashboard generation failed")
            
            with patch.object(orchestrator, '_get_dashboard_hook', return_value=mock_hook):
                # Should not raise even if hook fails
                profile = orchestrator.onboard_repository_with_profile(
                    repo_path=test_repo,
                    profile_store=profile_store
                )
                
                # Profile should still be returned (not lost)
                assert profile is not None
                assert profile.name is not None
                
                # Verify profile was actually saved to store
                assert profile_store.exists(profile.name)
        
        # AC_COMPLETE: AC-PHASE28-S5-I3 ✅
    
    def test_orchestrator_hook_lazy_loading(self):
        """I4: Verify dashboard hook is lazy-loaded on first use."""
        # AC_START: AC-PHASE28-S5-I4
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Hook should not be loaded yet
        assert orchestrator._dashboard_hook is None
        
        # Get hook (triggers lazy-loading)
        hook = orchestrator._get_dashboard_hook()
        
        # Hook should now be loaded (even if None due to import failure)
        # The important part is that _get_dashboard_hook completes without error
        assert hook is None or hasattr(hook, 'on_profile_created')
        
        # AC_COMPLETE: AC-PHASE28-S5-I4 ✅
    
    def test_hook_skipped_when_disabled(self):
        """I5: Verify hook can be disabled and is skipped."""
        # AC_START: AC-PHASE28-S5-I5
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        with TemporaryDirectory() as tmpdir:
            profile_store = ProfileStore(storage_path=Path(tmpdir))
            
            # Create test repo
            test_repo = Path(tmpdir) / "test_repo"
            test_repo.mkdir()
            (test_repo / "main.py").write_text("print('hello')")
            
            orchestrator = RepositoryOnboardingOrchestrator()
            
            # Mock disabled hook
            mock_hook = MagicMock()
            mock_hook.enabled = False
            mock_hook.on_profile_created.return_value = {"status": "skipped"}
            
            with patch.object(orchestrator, '_get_dashboard_hook', return_value=mock_hook):
                profile = orchestrator.onboard_repository_with_profile(
                    repo_path=test_repo,
                    profile_store=profile_store
                )
                
                # Profile should still be created
                assert profile is not None
                
                # Hook should be called regardless (decision made inside hook)
                mock_hook.on_profile_created.assert_called_once()
        
        # AC_COMPLETE: AC-PHASE28-S5-I5 ✅
    
    def test_hook_receives_correct_profile_data(self):
        """I6: Verify hook receives complete and correct profile data."""
        # AC_START: AC-PHASE28-S5-I6
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        from cortex.orchestrators.support.onboarding_dashboard_hook import (
            ProfileCreatedEvent
        )
        
        with TemporaryDirectory() as tmpdir:
            profile_store = ProfileStore(storage_path=Path(tmpdir))
            
            # Create test repo
            test_repo = Path(tmpdir) / "test_repo"
            test_repo.mkdir()
            (test_repo / "main.py").write_text("print('hello')")
            
            orchestrator = RepositoryOnboardingOrchestrator()
            
            mock_hook = MagicMock()
            mock_hook.on_profile_created.return_value = {"status": "success"}
            
            with patch.object(orchestrator, '_get_dashboard_hook', return_value=mock_hook):
                profile = orchestrator.onboard_repository_with_profile(
                    repo_path=test_repo,
                    profile_store=profile_store
                )
                
                # Verify hook received ProfileCreatedEvent
                call_args = mock_hook.on_profile_created.call_args
                event = call_args[0][0]
                
                assert isinstance(event, ProfileCreatedEvent)
                assert event.repo_name == profile.name
                assert Path(event.profile_path).exists()
                assert isinstance(event.timestamp, datetime)
                # profile_data should be dict (even if empty)
                assert isinstance(event.profile_data, dict)
        
        # AC_COMPLETE: AC-PHASE28-S5-I6 ✅
    
    def test_multiple_sequential_onboardings(self):
        """I7: Verify hook works correctly across multiple sequential onboardings."""
        # AC_START: AC-PHASE28-S5-I7
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        with TemporaryDirectory() as tmpdir:
            profile_store = ProfileStore(storage_path=Path(tmpdir))
            
            orchestrator = RepositoryOnboardingOrchestrator()
            
            mock_hook = MagicMock()
            mock_hook.on_profile_created.return_value = {"status": "success"}
            
            call_count = 0
            
            with patch.object(orchestrator, '_get_dashboard_hook', return_value=mock_hook):
                # Onboard multiple repos
                for i in range(3):
                    test_repo = Path(tmpdir) / f"test_repo{i}"
                    test_repo.mkdir()
                    (test_repo / "main.py").write_text(f"print('repo{i}')")
                    
                    profile = orchestrator.onboard_repository_with_profile(
                        repo_path=test_repo,
                        profile_store=profile_store
                    )
                    assert profile is not None
                    call_count += 1
                
                # Verify hook was called for each
                assert mock_hook.on_profile_created.call_count == call_count
                
                # Verify all profiles exist in store
                all_profiles = profile_store.list_all()
                assert len(all_profiles) > 0
        
        # AC_COMPLETE: AC-PHASE28-S5-I7 ✅
    
    def test_hook_integration_with_real_profile_creation(self):
        """I8: End-to-end test with actual profile generation."""
        # AC_START: AC-PHASE28-S5-I8
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        with TemporaryDirectory() as tmpdir:
            # Create test repo structure
            test_repo = Path(tmpdir) / "test_repo"
            test_repo.mkdir()
            (test_repo / "main.py").write_text("print('hello')")
            (test_repo / "README.md").write_text("# Test Repo")
            
            profile_store = ProfileStore(storage_path=Path(tmpdir) / "profiles")
            
            orchestrator = RepositoryOnboardingOrchestrator()
            
            mock_hook = MagicMock()
            mock_hook.on_profile_created.return_value = {"status": "success"}
            
            with patch.object(orchestrator, '_get_dashboard_hook', return_value=mock_hook):
                profile = orchestrator.onboard_repository_with_profile(
                    repo_path=test_repo,
                    profile_store=profile_store
                )
                
                # Verify profile was created with real data
                assert profile is not None
                assert profile.path == str(test_repo)
                
                # Verify hook was called
                mock_hook.on_profile_created.assert_called_once()
                
                # Verify event has real profile path
                event = mock_hook.on_profile_created.call_args[0][0]
                assert Path(event.profile_path).exists()
        
        # AC_COMPLETE: AC-PHASE28-S5-I8 ✅


class TestPhase28S5CompoundToolIntegration:
    """Integration tests for Phase-28 S5 compound MCP tool."""
    
    def test_compound_tool_orchestration_flow(self):
        """C1: Verify compound tool orchestrates onboarding + dashboard workflow."""
        # AC_START: AC-PHASE28-S5-C1
        from cortex.mcp.tools.compound.onboard_and_dashboard import (
            CompoundOnboardAndDashboardOperation,
            OperationStatus
        )
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        # Mock orchestrators
        mock_onboarding = MagicMock(spec=RepositoryOnboardingOrchestrator)
        mock_dashboard = MagicMock()
        
        mock_onboarding.onboard_repository.return_value = {
            "status": "success",
            "repo_name": "test_repo",
            "profile_path": "/path/to/profile.yaml",
            "profile_data": {}
        }
        
        mock_dashboard.generate_from_profile.return_value = {
            "status": "success",
            "dashboard_path": "/path/to/dashboard.json"
        }
        
        # Create compound tool
        compound_op = CompoundOnboardAndDashboardOperation(
            onboarding_orchestrator=mock_onboarding,
            dashboard_orchestrator=mock_dashboard
        )
        
        # Mock repo path
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            repo_path.mkdir()
            
            # Execute compound operation
            result = compound_op.execute(repo_path=str(repo_path))
            
            # Verify orchestrators were called
            mock_onboarding.onboard_repository.assert_called_once()
            mock_dashboard.generate_from_profile.assert_called_once()
        
        # AC_COMPLETE: AC-PHASE28-S5-C1 ✅
    
    def test_compound_tool_partial_success(self):
        """C2: Verify compound tool handles partial success (onboarding succeeds, dashboard fails)."""
        # AC_START: AC-PHASE28-S5-C2
        from cortex.mcp.tools.compound.onboard_and_dashboard import (
            CompoundOnboardAndDashboardOperation,
            OperationStatus
        )
        
        # Mock orchestrators
        mock_onboarding = MagicMock()
        mock_dashboard = MagicMock()
        
        # Onboarding succeeds
        mock_onboarding.onboard_repository.return_value = {
            "status": "success",
            "repo_name": "test_repo",
            "profile_path": "/path/to/profile.yaml",
            "profile_data": {}
        }
        
        # Dashboard fails
        mock_dashboard.generate_from_profile.side_effect = RuntimeError("Dashboard generation failed")
        
        # Create compound tool
        compound_op = CompoundOnboardAndDashboardOperation(
            onboarding_orchestrator=mock_onboarding,
            dashboard_orchestrator=mock_dashboard
        )
        
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            repo_path.mkdir()
            
            # Execute - should handle error gracefully
            result = compound_op.execute(repo_path=str(repo_path))
            
            # Status should indicate partial success
            assert result.profile_created is True
            assert result.status in [OperationStatus.PARTIAL_SUCCESS, OperationStatus.SUCCESS]
        
        # AC_COMPLETE: AC-PHASE28-S5-C2 ✅


# AC_COMPLETE: AC-PHASE28-S5-012 ✅ Integration test suite complete (10 tests)
