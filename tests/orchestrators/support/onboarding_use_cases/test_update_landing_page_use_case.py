"""
AC-054A-S1-16,17,18: UpdateLandingPageUseCase Tests

TDD Test Suite (5+ tests):
- AC-054A-S1-16: Use case updates landing page hub
- AC-054A-S1-17: Uses LandingPageGenerator
- AC-054A-S1-18: 5+ unit tests with mock generator

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LandingPageEntry:
    """Landing page entry."""
    repo_name: str
    description: str
    url: str
    category: str
    featured: bool


class TestUpdateLandingPageUseCase:
    """Test landing page hub updates."""

    @pytest.fixture
    def use_case(self):
        """Initialize UpdateLandingPageUseCase."""
        from cortex.orchestrators.support.onboarding_use_cases import UpdateLandingPageUseCase
        return UpdateLandingPageUseCase()

    @pytest.fixture
    def repo_entry(self) -> dict:
        """Fixture: Repository entry data."""
        return {
            "name": "cortex",
            "description": "Cognitive Real-Time Execution System",
            "url": "https://github.com/test/cortex",
            "category": "AI/ML",
            "featured": True,
            "thumbnail": "/images/cortex-thumb.png",
        }

    def test_updates_landing_page(self, use_case, repo_entry):
        """AC-054A-S1-16a: Updates landing page hub."""
        result = use_case.execute(repo_entry)
        
        assert result is not None
        assert result.repo_name == "cortex"

    def test_creates_landing_page_entry(self, use_case, repo_entry):
        """AC-054A-S1-16b: Creates proper landing page entry."""
        result = use_case.execute(repo_entry)
        
        assert isinstance(result, LandingPageEntry)

    def test_uses_landing_page_generator(self):
        """AC-054A-S1-17: Uses LandingPageGenerator."""
        from cortex.orchestrators.support.onboarding_use_cases import UpdateLandingPageUseCase
        
        use_case = UpdateLandingPageUseCase()
        assert hasattr(use_case, 'landing_page_generator')

    def test_preserves_entry_metadata(self, use_case, repo_entry):
        """AC-054A-S1-18a: Preserves entry metadata."""
        result = use_case.execute(repo_entry)
        
        assert result.description == repo_entry["description"]
        assert result.url == repo_entry["url"]
        assert result.featured == repo_entry["featured"]

    def test_categorizes_entries(self, use_case):
        """AC-054A-S1-18b: Categorizes entries properly."""
        various_entries = [
            {"name": "ml-repo", "category": "AI/ML", "description": "ML framework"},
            {"name": "web-repo", "category": "Web", "description": "Web framework"},
            {"name": "db-repo", "category": "Database", "description": "Database tool"},
        ]
        
        for entry in various_entries:
            result = use_case.execute(entry)
            assert result.category == entry["category"]

    def test_handles_missing_optional_fields(self, use_case):
        """AC-054A-S1-18c: Handles missing optional fields."""
        minimal_entry = {
            "name": "minimal",
            "description": "Minimal repo",
            "url": "https://github.com/test/minimal",
            "category": "Other",
        }
        result = use_case.execute(minimal_entry)
        
        assert result is not None
        assert result.repo_name == "minimal"
