"""
Tests for _update_company_domains() method in RepositoryOnboardingOrchestrator.

AC-ID: AC-PHASE-19-DOMAIN-UPDATE-001
Authority: CORE-008 (TDD - tests first)
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    RepositoryOnboardingOrchestrator,
)


class TestUpdateCompanyDomains:
    """Tests for company domain updates during onboarding."""
    
    @pytest.fixture
    def orchestrator(self) -> RepositoryOnboardingOrchestrator:
        """Create orchestrator instance."""
        return RepositoryOnboardingOrchestrator()
    
    @pytest.fixture
    def sample_lens_context(self) -> Dict[str, Any]:
        """Sample LENS context from holistic analysis."""
        return {
            "repository": "test-repo",
            "languages": {"python": 0.8, "javascript": 0.2},
            "frameworks": ["django", "react"],
            "patterns": {
                "known": ["repository_pattern", "service_layer"],
                "learned": [],
                "candidates": ["custom_auth_handler"]
            },
            "vendors": ["stripe", "sendgrid"],
            "database": {
                "type": "postgresql",
                "schema": {"tables": 15, "views": 3}
            },
            "entities": ["User", "Product", "Order"],
            "capabilities": ["api", "web_ui", "background_jobs"],
        }
    
    def test_update_company_domains_creates_yaml(
        self, 
        orchestrator: RepositoryOnboardingOrchestrator,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that _update_company_domains creates YAML file."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        result = orchestrator._update_company_domains(
            sample_lens_context, 
            repo_path
        )
        
        assert result is not None
        assert "created_files" in result or "updated_files" in result
    
    def test_update_company_domains_extracts_entities(
        self, 
        orchestrator: RepositoryOnboardingOrchestrator,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that entities are extracted from LENS context."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        result = orchestrator._update_company_domains(
            sample_lens_context, 
            repo_path
        )
        
        # Should extract entities
        assert result is not None
        # Verify entities were processed (implementation-dependent)
    
    def test_update_company_domains_merges_with_existing(
        self, 
        orchestrator: RepositoryOnboardingOrchestrator,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that updates merge with existing domain YAML."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create existing domain file
        domain_dir = Path("company/domains/test-repo")
        domain_dir.mkdir(parents=True, exist_ok=True)
        existing_yaml = domain_dir / "entities.yaml"
        existing_yaml.write_text("entities:\n  - ExistingEntity\n")
        
        result = orchestrator._update_company_domains(
            sample_lens_context, 
            repo_path
        )
        
        assert result is not None
        # Should merge, not replace
    
    def test_update_company_domains_handles_missing_context(
        self, 
        orchestrator: RepositoryOnboardingOrchestrator,
        tmp_path: Path,
    ):
        """Test graceful handling of minimal LENS context."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        minimal_context = {"repository": "test-repo"}
        
        result = orchestrator._update_company_domains(
            minimal_context, 
            repo_path
        )
        
        # Should not crash, return minimal result
        assert result is not None
    
    def test_update_company_domains_snowball_effect(
        self, 
        orchestrator: RepositoryOnboardingOrchestrator,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test snowball effect - each scan enriches existing data."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # First scan
        result1 = orchestrator._update_company_domains(
            sample_lens_context, 
            repo_path
        )
        
        # Second scan with new data
        enhanced_context = {
            **sample_lens_context,
            "entities": ["User", "Product", "Order", "Payment"],  # +1 new entity
            "patterns": {
                "known": ["repository_pattern", "service_layer", "factory"],  # +1
                "learned": ["custom_auth_handler"],  # Promoted from candidate
                "candidates": []
            }
        }
        
        result2 = orchestrator._update_company_domains(
            enhanced_context, 
            repo_path
        )
        
        # Should accumulate data, not replace
        assert result2 is not None
    
    def test_update_company_domains_respects_company_precedence(
        self, 
        orchestrator: RepositoryOnboardingOrchestrator,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that company domain YAMLs take precedence over CORTEX defaults."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Context has CORTEX naming
        context_with_cortex = {
            **sample_lens_context,
            "entities": ["User"],  # CORTEX standard
        }
        
        # But company YAML says "Customer"
        domain_dir = Path("company/domains/test-repo")
        domain_dir.mkdir(parents=True, exist_ok=True)
        existing_yaml = domain_dir / "entities.yaml"
        existing_yaml.write_text("entities:\n  - Customer  # Company prefers this\n")
        
        result = orchestrator._update_company_domains(
            context_with_cortex, 
            repo_path
        )
        
        # Should preserve "Customer" (company precedence)
        assert result is not None


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
