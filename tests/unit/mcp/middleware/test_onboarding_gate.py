"""
Tests for Onboarding Gate Middleware (Phase 28.3)
TDD RED Phase - Tests written BEFORE implementation

Test Coverage:
- Onboarding gate blocks unonboarded repositories
- Onboarding gate allows onboarded repositories
- Auto-trigger onboarding for new repositories
- External repo operations enforcement
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


def test_onboarding_gate_blocks_unonboarded():
    """Test that OnboardingGate blocks operations on unonboarded repos."""
    from cortex.mcp.middleware.onboarding_gate import OnboardingGate
    from cortex_brain.onboarded_repos import ProfileStore
    from tempfile import TemporaryDirectory
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        gate = OnboardingGate(profile_store=store)
        
        # Request for unonboarded repo
        request = {
            'operation': 'analyze',
            'repo_path': '/path/to/unonboarded/repo'
        }
        
        # Should block
        result = gate.check_onboarding(request)
        assert result['onboarded'] is False
        assert 'error' in result or 'action_required' in result


def test_onboarding_gate_allows_onboarded():
    """Test that OnboardingGate allows operations on onboarded repos."""
    from cortex.mcp.middleware.onboarding_gate import OnboardingGate
    from cortex_brain.onboarded_repos import ProfileStore, RepositoryProfile
    from tempfile import TemporaryDirectory
    from datetime import datetime
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        # Onboard a repository
        profile = RepositoryProfile(
            name="ONBOARDED_REPO",
            path="/path/to/onboarded",
            onboarded_at=datetime.now()
        )
        store.save(profile)
        
        gate = OnboardingGate(profile_store=store)
        
        # Request for onboarded repo
        request = {
            'operation': 'analyze',
            'repo_path': '/path/to/onboarded'
        }
        
        # Should allow
        result = gate.check_onboarding(request)
        assert result['onboarded'] is True


def test_onboarding_gate_auto_trigger():
    """Test that OnboardingGate can auto-trigger onboarding."""
    from cortex.mcp.middleware.onboarding_gate import OnboardingGate
    from cortex_brain.onboarded_repos import ProfileStore
    from tempfile import TemporaryDirectory
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        gate = OnboardingGate(profile_store=store, auto_onboard=True)
        
        # Mock repo path (KSESSIONS)
        ksessions_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
        
        if not ksessions_path.exists():
            pytest.skip("KSESSIONS not found")
        
        request = {
            'operation': 'analyze',
            'repo_path': str(ksessions_path)
        }
        
        # Should auto-trigger onboarding
        result = gate.process_request(request)
        
        # After processing, repo should be onboarded
        assert store.exists("KSESSIONS")


def test_onboarding_gate_extract_repo_path():
    """Test extraction of repo_path from various request formats."""
    from cortex.mcp.middleware.onboarding_gate import OnboardingGate
    
    gate = OnboardingGate()
    
    # Test different request formats
    requests = [
        {'repo_path': '/path/to/repo'},
        {'parameters': {'repo_path': '/path/to/repo'}},
        {'target': '/path/to/repo'},
    ]
    
    for req in requests:
        repo_path = gate.extract_repo_path(req)
        if repo_path:
            assert '/path/to/repo' in repo_path


def test_onboarding_gate_skip_cortex_operations():
    """Test that gate skips checks for CORTEX-internal operations."""
    from cortex.mcp.middleware.onboarding_gate import OnboardingGate
    
    gate = OnboardingGate()
    
    # CORTEX-internal requests should pass through
    cortex_requests = [
        {'operation': 'health_check'},
        {'operation': 'list_tools'},
        {'repo_path': '/Users/asifhussain/PROJECTS/CORTEX'},  # CORTEX itself
    ]
    
    for req in cortex_requests:
        result = gate.should_check_onboarding(req)
        assert result is False  # Should skip onboarding check
