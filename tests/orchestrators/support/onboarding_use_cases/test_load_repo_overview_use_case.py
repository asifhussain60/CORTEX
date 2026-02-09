"""
AC-054A-S1-01,02,03: LoadRepoOverviewUseCase Tests

TDD Test Suite (5+ tests):
- AC-054A-S1-01: Use case extracts basic repo metadata
- AC-054A-S1-02: Uses JSONProfileRepository for storage
- AC-054A-S1-03: 5+ unit tests (no orchestrator dependency)

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class RepoMetadata:
    """Repository metadata model."""
    name: str
    url: str
    language: str
    stars: int
    forks: int
    last_updated: str


class TestLoadRepoOverviewUseCase:
    """Test extraction of basic repository metadata."""

    @pytest.fixture
    def use_case(self):
        """Initialize LoadRepoOverviewUseCase."""
        # Will be implemented in cortex/orchestrators/support/onboarding_use_cases/
        from cortex.orchestrators.support.onboarding_use_cases import LoadRepoOverviewUseCase
        return LoadRepoOverviewUseCase()

    @pytest.fixture
    def mock_repo_data(self) -> Dict[str, Any]:
        """Fixture: Mock repository data."""
        return {
            "name": "test-repo",
            "url": "https://github.com/test/repo",
            "language": "Python",
            "stars": 150,
            "forks": 25,
            "last_updated": "2026-02-08",
            "description": "Test repository",
        }

    def test_extract_basic_metadata(self, use_case, mock_repo_data):
        """AC-054A-S1-01: Extract basic repo metadata."""
        result = use_case.execute(mock_repo_data)
        
        assert result is not None
        assert result.name == "test-repo"
        assert result.url == "https://github.com/test/repo"
        assert result.language == "Python"

    def test_uses_repository_interface(self, use_case):
        """AC-054A-S1-02: Uses JSONProfileRepository for storage."""
        # Use case should have repository injected
        assert hasattr(use_case, 'repository')
        assert use_case.repository is not None

    def test_returns_metadata_model(self, use_case, mock_repo_data):
        """AC-054A-S1-03a: Returns proper metadata model."""
        result = use_case.execute(mock_repo_data)
        assert isinstance(result, RepoMetadata)

    def test_handles_missing_fields(self, use_case):
        """AC-054A-S1-03b: Handles missing optional fields gracefully."""
        incomplete_data = {
            "name": "repo",
            "url": "https://github.com/test/repo",
            # Missing: language, stars, forks, etc.
        }
        result = use_case.execute(incomplete_data)
        assert result is not None
        assert result.name == "repo"

    def test_no_orchestrator_dependency(self, use_case):
        """AC-054A-S1-03c: No direct RepositoryOnboardingOrchestrator dependency."""
        # Use case should only depend on repository and models
        from cortex.orchestrators.support.onboarding_use_cases import LoadRepoOverviewUseCase
        from inspect import signature
        
        sig = signature(LoadRepoOverviewUseCase.__init__)
        params = list(sig.parameters.keys())
        
        # Should not depend on orchestrator
        assert "orchestrator" not in params
        assert "repository" in params or "repo" in params


class TestLoadRepoOverviewIntegration:
    """Integration tests with repository."""

    def test_save_overview_to_repository(self, tmp_path):
        """Test saving extracted overview to repository."""
        from cortex.orchestrators.support.onboarding_use_cases import LoadRepoOverviewUseCase
        from cortex.repositories import JSONProfileRepository
        
        repo = JSONProfileRepository(storage_path=tmp_path)
        use_case = LoadRepoOverviewUseCase(repository=repo)
        
        mock_data = {
            "name": "integration-test",
            "url": "https://github.com/test/integration",
            "language": "Python",
            "stars": 50,
            "forks": 5,
            "last_updated": "2026-02-09",
        }
        
        result = use_case.execute(mock_data)
        assert result is not None
        assert result.name == "integration-test"
