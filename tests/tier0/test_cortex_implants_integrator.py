"""
Unit Tests for Cortex Implants Integrator

Tests the cortex_implants_integrator module.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import yaml

from src.tier0.cortex_implants_integrator import (
    CortexImplantsIntegrator,
    get_implants_integrator,
    has_cortex_implants
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repo structure."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    return repo_path


@pytest.fixture
def setup_implants(temp_repo):
    """Setup cortex-implants with all files."""
    implants_dir = temp_repo / ".cortex-implants"
    implants_dir.mkdir()
    
    # governance.yaml
    gov_data = {
        "company_name": "TestCorp",
        "division": "Engineering",
        "repo_name": "test-repo",
        "repo_type": "library",
        "version": "1.0.0",
        "language": "Python",
        "framework": "FastAPI",
        "enforcement_level": "MODERATE",
        "block_on_violation": False,
        "require_approval_override": False,
        "priority": "HIGH",
        "contact": "test@test.com",
        "integration_flags": {},
        "rules_enabled": ["CODING_STANDARDS", "TECH_STACK_VALIDATION", "ARCHITECTURE_PATTERNS"]
    }
    with open(implants_dir / "governance.yaml", 'w') as f:
        yaml.safe_dump(gov_data, f)
    
    # tech-stack.yaml
    tech_data = {
        "approved_libraries": {
            "python": ["pytest", "pandas", "numpy"]
        },
        "forbidden_libraries": [
            {"library": "eval", "reason": "Security risk"},
            {"library": "pickle", "reason": "Use JSON"}
        ],
        "language_features": {
            "python_version": "3.8+"
        }
    }
    with open(implants_dir / "tech-stack.yaml", 'w') as f:
        yaml.safe_dump(tech_data, f)
    
    # architecture-patterns.yaml
    arch_data = {
        "required_patterns": [
            {"pattern": "Repository Pattern"},
            {"pattern": "Dependency Injection"}
        ],
        "anti_patterns": [
            {"pattern": "Singleton", "reason": "Avoid overuse"}
        ],
        "layer_boundaries": []
    }
    with open(implants_dir / "architecture-patterns.yaml", 'w') as f:
        yaml.safe_dump(arch_data, f)
    
    return implants_dir


class TestCortexImplantsIntegrator:
    """Test CortexImplantsIntegrator class."""
    
    def test_initialization_without_implants(self, temp_repo):
        """Test integrator initializes without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert integrator is not None
        assert not integrator.has_implants()
    
    def test_initialization_with_implants(self, temp_repo, setup_implants):
        """Test integrator loads implants correctly."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert integrator.has_implants()
        assert integrator.implants is not None
    
    def test_get_priority(self, temp_repo, setup_implants):
        """Test get_priority method."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert integrator.get_priority() == "HIGH"
    
    def test_get_priority_no_implants(self, temp_repo):
        """Test get_priority returns NONE without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert integrator.get_priority() == "NONE"
    
    def test_should_override_cortex(self, temp_repo, setup_implants):
        """Test should_override_cortex with HIGH priority."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert integrator.should_override_cortex()
    
    def test_should_not_override_cortex(self, temp_repo):
        """Test should_override_cortex without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert not integrator.should_override_cortex()
    
    def test_get_tech_stack_restrictions(self, temp_repo, setup_implants):
        """Test get_tech_stack_restrictions."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        tech = integrator.get_tech_stack_restrictions()
        
        assert tech is not None
        assert "approved_libraries" in tech
        assert "pytest" in tech["approved_libraries"]["python"]
    
    def test_get_tech_stack_restrictions_no_implants(self, temp_repo):
        """Test get_tech_stack_restrictions without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        tech = integrator.get_tech_stack_restrictions()
        
        assert tech is None
    
    def test_validate_tech_stack(self, temp_repo, setup_implants):
        """Test validate_tech_stack method."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        # Valid libraries
        violations = integrator.validate_tech_stack(["pytest", "pandas"])
        assert len(violations) == 0
        
        # Forbidden library
        violations = integrator.validate_tech_stack(["eval"])
        assert len(violations) > 0
        assert "eval" in str(violations[0])
    
    def test_validate_tech_stack_no_implants(self, temp_repo):
        """Test validate_tech_stack without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        violations = integrator.validate_tech_stack(["anything"])
        assert len(violations) == 0  # No restrictions
    
    def test_validate_architecture(self, temp_repo, setup_implants):
        """Test validate_architecture method."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        # Plan with required patterns
        plan = {
            "description": "Using Repository Pattern and Dependency Injection"
        }
        violations = integrator.validate_architecture(plan)
        assert len(violations) == 0
        
        # Plan with forbidden pattern
        plan = {
            "description": "Using Singleton pattern everywhere"
        }
        violations = integrator.validate_architecture(plan)
        assert len(violations) > 0
    
    def test_get_context_summary(self, temp_repo, setup_implants):
        """Test get_context_summary method."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        summary = integrator.get_context_summary()
        
        assert "Cortex Implants Active" in summary
        assert "TestCorp" in summary
        assert "test-repo" in summary
    
    def test_get_context_summary_no_implants(self, temp_repo):
        """Test get_context_summary without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        summary = integrator.get_context_summary()
        
        assert summary == ""


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_implants_integrator(self):
        """Test get_implants_integrator singleton."""
        integrator1 = get_implants_integrator()
        integrator2 = get_implants_integrator()
        
        # Should return same instance
        assert integrator1 is integrator2
    
    def test_has_cortex_implants(self, temp_repo, setup_implants):
        """Test has_cortex_implants convenience function."""
        result = has_cortex_implants(temp_repo)
        
        assert result is True
    
    def test_has_cortex_implants_false(self, temp_repo):
        """Test has_cortex_implants returns False."""
        result = has_cortex_implants(temp_repo)
        
        assert result is False


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_repo_detection(self, tmp_path):
        """Test automatic repo detection."""
        # Create repo with .git
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        
        # Initialize from subdirectory
        sub_dir = repo_path / "src"
        sub_dir.mkdir()
        
        import os
        os.chdir(sub_dir)
        
        integrator = CortexImplantsIntegrator()
        
        # Should detect parent repo
        assert integrator.repo_path.name == "test-repo"
    
    def test_invalid_implants(self, temp_repo):
        """Test handling of invalid implants."""
        implants_dir = temp_repo / ".cortex-implants"
        implants_dir.mkdir()
        
        # Create invalid governance.yaml
        gov_file = implants_dir / "governance.yaml"
        gov_file.write_text("invalid: yaml: [[[")
        
        integrator = CortexImplantsIntegrator(temp_repo)
        
        # Should handle gracefully
        assert not integrator.has_implants()


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def test_high_priority_override(self, temp_repo, setup_implants):
        """Test HIGH priority overrides CORTEX."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        assert integrator.get_priority() == "HIGH"
        assert integrator.should_override_cortex()
    
    def test_tech_stack_validation_workflow(self, temp_repo, setup_implants):
        """Test complete tech stack validation workflow."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        # Validate approved libraries
        violations = integrator.validate_tech_stack(["pytest", "pandas"])
        assert len(violations) == 0
        
        # Validate forbidden library
        violations = integrator.validate_tech_stack(["eval"])
        assert len(violations) >= 1  # May have multiple violations (forbidden + not approved)
        assert any("eval" in v.lower() for v in violations)
    
    def test_graceful_degradation(self, temp_repo):
        """Test system works without implants."""
        integrator = CortexImplantsIntegrator(temp_repo)
        
        # All methods should work without implants
        assert not integrator.has_implants()
        assert integrator.get_priority() == "NONE"
        assert integrator.get_tech_stack_restrictions() is None
        assert integrator.validate_tech_stack(["anything"]) == []
        assert integrator.get_context_summary() == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
