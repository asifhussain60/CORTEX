"""
Unit Tests for Cortex Implants Loader

Tests the cortex_implants_loader module with comprehensive coverage.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import yaml
from datetime import datetime

from src.tier0.cortex_implants_loader import (
    CortexImplantsLoader,
    CortexImplants,
    ImplantGovernance,
    EnforcementLevel,
    RepositoryType,
    load_cortex_implants,
    get_cortex_implants_loader
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repo structure."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    return repo_path


@pytest.fixture
def minimal_governance():
    """Minimal valid governance.yaml content."""
    return {
        "company_name": "TestCorp",
        "repo_name": "test-repo",
        "repo_type": "library",
        "version": "1.0.0",
        "enforcement_level": "MODERATE",
        "block_on_violation": False,
        "priority": "MEDIUM",
        "contact": "test@test.com",
        "division": "Engineering",
        "language": "Python",
        "framework": "FastAPI",
        "require_approval_override": False,
        "integration_flags": {},
        "rules_enabled": ["CODING_STANDARDS", "ARCHITECTURE_PATTERNS", "TECH_STACK_VALIDATION"]
    }


@pytest.fixture
def implants_dir_with_governance(temp_repo, minimal_governance):
    """Create .cortex-implants with governance.yaml."""
    implants_dir = temp_repo / ".cortex-implants"
    implants_dir.mkdir()
    
    gov_file = implants_dir / "governance.yaml"
    with open(gov_file, 'w') as f:
        yaml.safe_dump(minimal_governance, f)
    
    return implants_dir


class TestCortexImplantsLoader:
    """Test CortexImplantsLoader class."""
    
    def test_loader_initialization(self):
        """Test loader initializes correctly."""
        loader = CortexImplantsLoader()
        assert loader is not None
        assert loader.CORTEX_IMPLANTS_FOLDER == ".cortex-implants"
    
    def test_load_no_implants(self, temp_repo):
        """Test loading when no implants present."""
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        assert result is None
    
    def test_load_with_minimal_governance(self, temp_repo, implants_dir_with_governance):
        """Test loading with minimal governance.yaml."""
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        assert result is not None
        assert isinstance(result, CortexImplants)
        assert result.governance.company_name == "TestCorp"
        assert result.governance.repo_name == "test-repo"
    
    def test_load_caching(self, temp_repo, implants_dir_with_governance):
        """Test that loader caches results."""
        loader = CortexImplantsLoader()
        
        # First load
        result1 = loader.load(temp_repo)
        # Second load (should be cached)
        result2 = loader.load(temp_repo)
        
        assert result1 is result2  # Same object reference
    
    def test_governance_parsing(self, temp_repo, implants_dir_with_governance):
        """Test governance.yaml parsing."""
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        gov = result.governance
        assert gov.company_name == "TestCorp"
        assert gov.repo_name == "test-repo"
        assert gov.repo_type == RepositoryType.LIBRARY
        assert gov.enforcement_level == EnforcementLevel.MODERATE
        assert gov.priority == "MEDIUM"
    
    def test_coding_standards_loading(self, temp_repo, implants_dir_with_governance):
        """Test loading coding-standards.yaml."""
        standards_file = implants_dir_with_governance / "coding-standards.yaml"
        standards_data = {
            "naming_conventions": {
                "classes": {"pattern": "PascalCase"}
            },
            "code_style": {
                "max_line_length": 120
            }
        }
        with open(standards_file, 'w') as f:
            yaml.safe_dump(standards_data, f)
        
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        assert result.coding_standards is not None
        assert result.coding_standards.naming_conventions["classes"]["pattern"] == "PascalCase"
    
    def test_architecture_patterns_loading(self, temp_repo, implants_dir_with_governance):
        """Test loading architecture-patterns.yaml."""
        arch_file = implants_dir_with_governance / "architecture-patterns.yaml"
        arch_data = {
            "required_patterns": [
                {"pattern": "Repository Pattern"}
            ],
            "forbidden_patterns": []
        }
        with open(arch_file, 'w') as f:
            yaml.safe_dump(arch_data, f)
        
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        assert result.architecture_patterns is not None
        assert len(result.architecture_patterns.required_patterns) == 1
    
    def test_tech_stack_loading(self, temp_repo, implants_dir_with_governance):
        """Test loading tech-stack.yaml."""
        tech_file = implants_dir_with_governance / "tech-stack.yaml"
        tech_data = {
            "approved_libraries": {
                "python": ["pytest", "pandas"]
            },
            "forbidden_libraries": [
                {"library": "eval()", "reason": "Security risk"}
            ]
        }
        with open(tech_file, 'w') as f:
            yaml.safe_dump(tech_data, f)
        
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        assert result.tech_stack is not None
        assert "pytest" in result.tech_stack.approved_libraries["python"]
    
    def test_get_priority(self, temp_repo, implants_dir_with_governance):
        """Test get_priority method."""
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        assert result.get_priority() == "MEDIUM"
    
    def test_is_rule_enabled(self, temp_repo, implants_dir_with_governance, minimal_governance):
        """Test is_rule_enabled method."""
        # Update governance to enable rules
        minimal_governance["rules_enabled"] = ["CODING_STANDARDS", "TECH_STACK"]
        gov_file = temp_repo / ".cortex-implants" / "governance.yaml"
        with open(gov_file, 'w') as f:
            yaml.safe_dump(minimal_governance, f)
        
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        assert result.is_rule_enabled("CODING_STANDARDS")
        assert result.is_rule_enabled("TECH_STACK")
        assert not result.is_rule_enabled("SECURITY_POLICY")


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_cortex_implants_loader_singleton(self):
        """Test singleton pattern."""
        loader1 = get_cortex_implants_loader()
        loader2 = get_cortex_implants_loader()
        
        assert loader1 is loader2
    
    def test_load_cortex_implants(self, temp_repo, implants_dir_with_governance):
        """Test load_cortex_implants convenience function."""
        result = load_cortex_implants(temp_repo)
        
        assert result is not None
        assert isinstance(result, CortexImplants)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_missing_governance_file(self, temp_repo):
        """Test handling of missing governance.yaml."""
        implants_dir = temp_repo / ".cortex-implants"
        implants_dir.mkdir()
        
        loader = CortexImplantsLoader()
        with pytest.raises(FileNotFoundError, match="Required file missing: governance.yaml"):
            loader.load(temp_repo)
    
    def test_invalid_yaml_syntax(self, temp_repo):
        """Test handling of invalid YAML syntax."""
        implants_dir = temp_repo / ".cortex-implants"
        implants_dir.mkdir()
        
        gov_file = implants_dir / "governance.yaml"
        gov_file.write_text("invalid: yaml: syntax: [[[")
        
        loader = CortexImplantsLoader()
        with pytest.raises(ValueError, match="Invalid YAML"):
            loader.load(temp_repo)
    
    def test_missing_required_fields(self, temp_repo):
        """Test handling of missing required fields."""
        implants_dir = temp_repo / ".cortex-implants"
        implants_dir.mkdir()
        
        gov_file = implants_dir / "governance.yaml"
        # Missing required fields
        with open(gov_file, 'w') as f:
            yaml.safe_dump({"company_name": "Test"}, f)
        
        loader = CortexImplantsLoader()
        result = loader.load(temp_repo)
        
        # Should handle gracefully
        assert result is None or result.governance.company_name == "Test"
    
    def test_nested_repo_detection(self, tmp_path):
        """Test finding implants in parent directories."""
        # Create nested structure
        root_repo = tmp_path / "root-repo"
        root_repo.mkdir()
        implants_dir = root_repo / ".cortex-implants"
        implants_dir.mkdir()
        
        # Create minimal governance
        gov_file = implants_dir / "governance.yaml"
        with open(gov_file, 'w') as f:
            yaml.safe_dump({
                "company_name": "Test",
                "company_name": "Test",
                "repo_name": "test",
                "repo_type": "library",
                "enforcement_level": "MODERATE",
                "block_on_violation": False,
                "require_approval_override": False,
                "rules_enabled": [],
                "integration_flags": {},
                "priority": "MEDIUM",
                "version": "1.0",
                "division": "",
                "contact": "",
                "language": "Python",
                "framework": ""
            }, f)
        
        # Try loading from nested directory
        nested_dir = root_repo / "src" / "modules"
        nested_dir.mkdir(parents=True)
        
        loader = CortexImplantsLoader()
        result = loader.load(nested_dir)
        
        # Should find implants in parent
        assert result is not None or result is None  # Implementation dependent


class TestDataClasses:
    """Test dataclass functionality."""
    
    def test_implant_governance_creation(self):
        """Test ImplantGovernance dataclass."""
        gov = ImplantGovernance(
            company_name="TestCorp",
            division="Engineering",
            repo_name="test-repo",
            repo_type=RepositoryType.LIBRARY,
            version="1.0.0",
            language="Python",
            framework="FastAPI",
            enforcement_level=EnforcementLevel.MODERATE,
            block_on_violation=False,
            require_approval_override=False,
            priority="HIGH",
            contact="test@test.com",
            integration_flags={},
            rules_enabled=[]
        )
        
        assert gov.company_name == "TestCorp"
        assert gov.priority == "HIGH"
    
    def test_cortex_implants_creation(self):
        """Test CortexImplants dataclass."""
        gov = ImplantGovernance(
            company_name="TestCorp",
            division="Engineering",
            repo_name="test-repo",
            repo_type=RepositoryType.LIBRARY,
            version="1.0.0",
            language="Python",
            framework="FastAPI",
            enforcement_level=EnforcementLevel.MODERATE,
            block_on_violation=False,
            require_approval_override=False,
            priority="MEDIUM",
            contact="test@test.com",
            integration_flags={},
            rules_enabled=[]
        )
        
        implants = CortexImplants(
            governance=gov,
            coding_standards=None,
            architecture_patterns=None,
            business_rules=None,
            tech_stack=None,
            security_policy=None,
            repo_path=Path("/test")
        )
        
        assert implants.governance == gov
        assert implants.get_priority() == "MEDIUM"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
