"""
Tests for Manifest Inheritance Resolver
Validates inheritance chain resolution and manifest merging

Author: Asif Hussain
Created: 2025-12-22 (Week 15 Day 2)
"""

import pytest
from pathlib import Path
from src.utils.manifest_inheritance_resolver import ManifestInheritanceResolver


def normalize_path(path: str) -> str:
    """Normalize path separators for cross-platform compatibility."""
    return path.replace('\\', '/')


@pytest.fixture
def resolver():
    """Create resolver with test manifests directory"""
    base_dir = Path(__file__).parent.parent / "cortex-brain" / "manifests"
    return ManifestInheritanceResolver(base_dir)


class TestInheritanceChain:
    """Test inheritance chain resolution"""
    
    def test_base_manifest_no_inheritance(self, resolver):
        """Base manifest should have no parent"""
        chain = resolver.get_inheritance_chain("shared/base-orchestrator-manifest.yaml")
        assert len(chain) == 1
        assert chain[0] == "shared/base-orchestrator-manifest.yaml"
    
    def test_planning_base_inherits_from_base(self, resolver):
        """Planning base should inherit from base-orchestrator"""
        chain = resolver.get_inheritance_chain("shared/planning-base-manifest.yaml")
        assert len(chain) == 2
        assert normalize_path(chain[0]) == "shared/base-orchestrator-manifest.yaml"
        assert normalize_path(chain[1]) == "shared/planning-base-manifest.yaml"
    
    def test_execution_base_inherits_from_base(self, resolver):
        """Execution base should inherit from base-orchestrator"""
        chain = resolver.get_inheritance_chain("shared/execution-base-manifest.yaml")
        assert len(chain) == 2
        assert normalize_path(chain[0]) == "shared/base-orchestrator-manifest.yaml"
        assert normalize_path(chain[1]) == "shared/execution-base-manifest.yaml"
    
    def test_analysis_base_inherits_from_base(self, resolver):
        """Analysis base should inherit from base-orchestrator"""
        chain = resolver.get_inheritance_chain("shared/analysis-base-manifest.yaml")
        assert len(chain) == 2
        assert normalize_path(chain[0]) == "shared/base-orchestrator-manifest.yaml"
        assert normalize_path(chain[1]) == "shared/analysis-base-manifest.yaml"
    
    def test_example_planning_three_level_chain(self, resolver):
        """Example planning should have 3-level chain"""
        chain = resolver.get_inheritance_chain("examples/example-planning-manifest.yaml")
        assert len(chain) == 3
        assert normalize_path(chain[0]) == "shared/base-orchestrator-manifest.yaml"
        assert normalize_path(chain[1]) == "shared/planning-base-manifest.yaml"
        assert normalize_path(chain[2]) == "examples/example-planning-manifest.yaml"


class TestManifestMerging:
    """Test manifest merging strategies"""
    
    def test_scalar_override(self, resolver):
        """Child should override parent scalar values"""
        resolved = resolver.resolve("examples/example-planning-manifest.yaml")
        
        # Child overrides
        assert resolved["metadata"]["orchestrator_name"] == "example_planning_orchestrator"
        assert resolved["metadata"]["version"] == "1.0.0"
        assert resolved["metadata"]["description"] == "Example planning orchestrator demonstrating inheritance patterns"
        
        # Parent values inherited
        assert resolved["metadata"]["category"] == "planning"  # From planning-base
        assert resolved["metadata"]["maintainer"] == "CORTEX Development Team"  # From base
    
    def test_dict_deep_merge(self, resolver):
        """Dictionaries should deep merge, not replace"""
        resolved = resolver.resolve("examples/example-execution-manifest.yaml")
        
        # metadata dict should have both parent and child fields
        assert "orchestrator_name" in resolved["metadata"]
        assert "category" in resolved["metadata"]
        assert "deployment_tier" in resolved["metadata"]
        assert "example_purpose" in resolved["metadata"]  # Custom field from child
        
        # deployment_tier overridden
        assert resolved["metadata"]["deployment_tier"] == "admin"  # Child override
    
    def test_list_replacement_for_phases(self, resolver):
        """Phases list should be replaced by child, not appended"""
        resolved = resolver.resolve("examples/example-planning-manifest.yaml")
        
        # Should have child's phases, not parent's
        phases = resolved.get("phases", [])
        assert len(phases) == 2
        assert phases[0]["id"] == "phase_1"
        assert phases[1]["id"] == "phase_2"
    
    def test_inherits_from_removed(self, resolver):
        """inherits_from key should not appear in resolved manifest"""
        resolved = resolver.resolve("examples/example-planning-manifest.yaml")
        assert "inherits_from" not in resolved


class TestValidation:
    """Test manifest validation"""
    
    def test_base_manifest_missing_required_fields(self, resolver):
        """Base manifest has null values for required fields"""
        resolved = resolver.resolve("shared/base-orchestrator-manifest.yaml")
        errors = resolver.validate_manifest(resolved)
        
        # Should have errors for null required fields
        assert len(errors) > 0
        assert any("orchestrator_name" in err for err in errors)
        assert any("description" in err for err in errors)
    
    def test_example_manifest_valid(self, resolver):
        """Example manifests should be valid after inheritance"""
        resolved = resolver.resolve("examples/example-planning-manifest.yaml")
        errors = resolver.validate_manifest(resolved)
        
        # Should be valid (all required fields filled)
        assert len(errors) == 0
    
    def test_invalid_category(self, resolver):
        """Invalid category should be caught"""
        # Create temporary invalid manifest
        invalid = {
            "schema_version": "1.0",
            "metadata": {
                "orchestrator_name": "test",
                "version": "1.0.0",
                "description": "Test orchestrator for validation",
                "category": "invalid_category",  # Invalid
                "last_updated": "2025-12-22",
                "maintainer": "Test"
            }
        }
        
        errors = resolver.validate_manifest(invalid)
        assert len(errors) > 0
        assert any("Invalid category" in err for err in errors)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_nonexistent_manifest(self, resolver):
        """Should raise FileNotFoundError for missing manifest"""
        with pytest.raises(FileNotFoundError):
            resolver.resolve("nonexistent/manifest.yaml")
    
    def test_circular_inheritance_detection(self, resolver):
        """Should detect and raise error for circular inheritance"""
        # This would require creating temp manifests with circular refs
        # Skipping for now (would need temp file creation)
        pass
    
    def test_empty_manifest(self, resolver):
        """Empty manifest should still resolve"""
        # Would need temp file for this test
        pass


class TestRealWorldScenarios:
    """Test with actual CORTEX manifests"""
    
    def test_planning_base_inheritance(self, resolver):
        """Planning base should inherit all base fields"""
        resolved = resolver.resolve("shared/planning-base-manifest.yaml")
        
        # Should have schema_version from base
        assert "schema_version" in resolved
        assert resolved["schema_version"] == "1.0"
        
        # Should have metadata from both
        assert "metadata" in resolved
        assert "category" in resolved["metadata"]
        assert resolved["metadata"]["category"] == "planning"
        
        # Should have planning-specific sections
        assert "definition_of_ready" in resolved
        assert "definition_of_done" in resolved
        assert "complexity_analysis" in resolved
    
    def test_execution_base_inheritance(self, resolver):
        """Execution base should inherit all base fields"""
        resolved = resolver.resolve("shared/execution-base-manifest.yaml")
        
        # Should have execution-specific sections
        assert "phase_execution" in resolved
        assert "rollback" in resolved
        assert "git_integration" in resolved
        
        # Category should be execution
        assert resolved["metadata"]["category"] == "execution"
    
    def test_analysis_base_inheritance(self, resolver):
        """Analysis base should inherit all base fields"""
        resolved = resolver.resolve("shared/analysis-base-manifest.yaml")
        
        # Should have analysis-specific sections
        assert "discovery" in resolved
        assert "ast_analysis" in resolved
        assert "dependency_analysis" in resolved
        
        # Category should be analysis
        assert resolved["metadata"]["category"] == "analysis"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
