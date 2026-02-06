"""
Tests for RepositoryOnboardingOrchestrator Enhancement (Phase 28.2)
TDD RED Phase - Tests written BEFORE implementation

Test Coverage:
- Repository scanning and analysis
- Profile generation from scan results
- Company domains detection
- Tech stack identification
- Security baseline assessment
- Standards extraction
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch


def test_onboarding_orchestrator_scan_repository():
    """Test repository structure scanning."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should scan repository and return scan results
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    scan_results = orchestrator.scan_repository(repo_path)
    
    assert scan_results is not None
    assert 'structure' in scan_results
    assert 'tech_stack' in scan_results


def test_onboarding_orchestrator_detect_company_domains():
    """Test company domains structure detection."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should detect company/domains/ structure
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    has_domains, domains_path, detected_domains = orchestrator.detect_company_domains(
        repo_path
    )
    
    # KSESSIONS may or may not have company domains - we test the detection logic
    assert isinstance(has_domains, bool)
    if has_domains:
        assert domains_path is not None
        assert isinstance(detected_domains, list)


def test_onboarding_orchestrator_analyze_tech_stack():
    """Test technology stack analysis."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should identify languages, frameworks, dependencies
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    tech_stack = orchestrator.analyze_tech_stack(repo_path)
    
    assert tech_stack is not None
    assert 'primary_language' in tech_stack
    assert 'languages' in tech_stack
    assert isinstance(tech_stack['languages'], list)


def test_onboarding_orchestrator_assess_security_baseline():
    """Test security baseline assessment."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should assess security configuration
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    security_baseline = orchestrator.assess_security_baseline(repo_path)
    
    assert security_baseline is not None
    assert 'secrets_management' in security_baseline
    assert 'vulnerabilities_detected' in security_baseline


def test_onboarding_orchestrator_extract_standards():
    """Test standards extraction from repository."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should extract coding standards, test patterns
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    standards = orchestrator.extract_standards(repo_path)
    
    assert standards is not None
    assert 'coding_style' in standards or 'test_patterns' in standards


def test_onboarding_orchestrator_generate_profile():
    """Test complete profile generation from scan results."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    from cortex_brain.onboarded_repos import RepositoryProfile
    
    # RED: Should generate complete RepositoryProfile
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    profile = orchestrator.generate_profile(repo_path)
    
    assert isinstance(profile, RepositoryProfile)
    assert profile.name == "KSESSIONS"
    assert profile.path == str(repo_path)
    assert profile.onboarded_at is not None


def test_onboarding_orchestrator_onboard_repository():
    """Test full onboarding workflow (scan → profile → save)."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    from cortex_brain.onboarded_repos import ProfileStore
    from tempfile import TemporaryDirectory
    
    # RED: Should complete full onboarding
    orchestrator = RepositoryOnboardingOrchestrator()
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
        profile = orchestrator.onboard_repository_with_profile(
            repo_path=repo_path,
            profile_store=store
        )
        
        assert profile is not None
        assert store.exists("KSESSIONS")


def test_onboarding_orchestrator_graceful_missing_repo():
    """Test graceful handling of missing repository."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator,
        RepositoryNotFoundError
    )
    
    # RED: Should raise RepositoryNotFoundError
    orchestrator = RepositoryOnboardingOrchestrator()
    
    with pytest.raises(RepositoryNotFoundError):
        orchestrator.scan_repository(Path("/nonexistent/repo"))


def test_onboarding_orchestrator_detect_test_framework():
    """Test test framework detection."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should detect pytest, unittest, etc.
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    test_info = orchestrator.detect_test_framework(repo_path)
    
    assert test_info is not None
    assert 'has_tests' in test_info
    assert 'test_framework' in test_info


def test_onboarding_orchestrator_analyze_dependencies():
    """Test dependency analysis from requirements.txt, pyproject.toml."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should parse dependencies
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    dependencies = orchestrator.analyze_dependencies(repo_path)
    
    assert isinstance(dependencies, list)
