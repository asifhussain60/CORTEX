"""
Unit tests for TemplateInheritance module.

Tests cover:
- Single-level inheritance
- Multi-level inheritance (3 levels)
- Section overrides
- Component overrides  
- Deep dictionary merging
- Circular inheritance detection
- Inheritance chain resolution
- Error handling

Author: CORTEX Test Suite
Date: December 5, 2025
Version: 1.0
"""

import pytest
import yaml
from pathlib import Path
from src.response_templates.template_inheritance import (
    TemplateInheritance,
    TemplateInheritanceError,
    CircularInheritanceError
)
from src.response_templates.component_registry import ComponentRegistry


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create temporary template directory with base templates."""
    template_dir = tmp_path / "response-templates"
    template_dir.mkdir()
    
    # Create base templates directory
    base_dir = template_dir / "core" / "base-templates"
    base_dir.mkdir(parents=True)
    
    # Create grandparent template
    grandparent_file = base_dir / "grandparent.yaml"
    grandparent_data = {
        "id": "grandparent",
        "sections": {
            "header": "Grandparent Header",
            "body": "Grandparent Body",
            "footer": "Grandparent Footer"
        },
        "metadata": {
            "version": "1.0",
            "author": "System"
        }
    }
    with open(grandparent_file, 'w') as f:
        yaml.dump(grandparent_data, f)
    
    # Create parent template (inherits from grandparent)
    parent_file = base_dir / "parent.yaml"
    parent_data = {
        "id": "parent",
        "inherits": "core/base-templates/grandparent.yaml",
        "sections": {
            "body": "Parent Body Override",
            "new_section": "Parent New Section"
        }
    }
    with open(parent_file, 'w') as f:
        yaml.dump(parent_data, f)
    
    # Create circular reference template A
    circular_a_file = base_dir / "circular_a.yaml"
    circular_a_data = {
        "id": "circular_a",
        "inherits": "core/base-templates/circular_b.yaml",
        "sections": {"content": "A"}
    }
    with open(circular_a_file, 'w') as f:
        yaml.dump(circular_a_data, f)
    
    # Create circular reference template B
    circular_b_file = base_dir / "circular_b.yaml"
    circular_b_data = {
        "id": "circular_b",
        "inherits": "core/base-templates/circular_a.yaml",
        "sections": {"content": "B"}
    }
    with open(circular_b_file, 'w') as f:
        yaml.dump(circular_b_data, f)
    
    # Create components directory for component registry
    components_dir = template_dir / "core" / "components"
    components_dir.mkdir(parents=True)
    
    return template_dir


@pytest.fixture
def component_registry(temp_template_dir):
    """Create ComponentRegistry instance."""
    return ComponentRegistry(
        components_dir=temp_template_dir,
        cache_ttl_seconds=300
    )


@pytest.fixture
def inheritance_engine(temp_template_dir, component_registry):
    """Create TemplateInheritance instance."""
    return TemplateInheritance(
        template_dir=temp_template_dir,
        component_registry=component_registry
    )


class TestTemplateInheritance:
    """Test suite for TemplateInheritance class."""
    
    def test_initialization(self, inheritance_engine, temp_template_dir):
        """Test engine initialization."""
        assert inheritance_engine.template_dir == temp_template_dir
        assert inheritance_engine.component_registry is not None
        assert len(inheritance_engine.base_template_cache) == 0
    
    def test_no_inheritance(self, inheritance_engine):
        """Test template without inheritance directive."""
        template = {
            "id": "simple",
            "sections": {
                "header": "Simple Header",
                "body": "Simple Body"
            }
        }
        
        result = inheritance_engine.resolve_inheritance(template)
        
        assert result["id"] == "simple"
        assert result["sections"]["header"] == "Simple Header"
        assert "inherits" not in result
    
    def test_single_level_inheritance(self, inheritance_engine):
        """Test inheriting from one base template."""
        child_template = {
            "id": "child",
            "inherits": "core/base-templates/grandparent.yaml",
            "sections": {
                "body": "Child Body Override"
            }
        }
        
        result = inheritance_engine.resolve_inheritance(child_template)
        
        # Should have grandparent's header and footer
        assert result["sections"]["header"] == "Grandparent Header"
        assert result["sections"]["footer"] == "Grandparent Footer"
        
        # Should have child's body override
        assert result["sections"]["body"] == "Child Body Override"
        
        # Should have grandparent's metadata
        assert result["metadata"]["version"] == "1.0"
        
        # Inherits directive should be removed
        assert "inherits" not in result
    
    def test_multi_level_inheritance(self, inheritance_engine):
        """Test 3-level inheritance (child → parent → grandparent)."""
        child_template = {
            "id": "child",
            "inherits": "core/base-templates/parent.yaml",
            "sections": {
                "footer": "Child Footer Override"
            }
        }
        
        result = inheritance_engine.resolve_inheritance(child_template)
        
        # Should have grandparent's header (not overridden)
        assert result["sections"]["header"] == "Grandparent Header"
        
        # Should have parent's body (overrode grandparent)
        assert result["sections"]["body"] == "Parent Body Override"
        
        # Should have child's footer (overrode grandparent)
        assert result["sections"]["footer"] == "Child Footer Override"
        
        # Should have parent's new section
        assert result["sections"]["new_section"] == "Parent New Section"
        
        # Should have inherited metadata
        assert result["metadata"]["version"] == "1.0"
    
    def test_section_override(self, inheritance_engine):
        """Test overriding specific sections."""
        template = {
            "id": "override_test",
            "inherits": "core/base-templates/grandparent.yaml",
            "sections": {
                "header": "New Header",
                "body": "New Body"
                # footer not overridden
            }
        }
        
        result = inheritance_engine.resolve_inheritance(template)
        
        assert result["sections"]["header"] == "New Header"
        assert result["sections"]["body"] == "New Body"
        assert result["sections"]["footer"] == "Grandparent Footer"  # Original
    
    def test_deep_merge_nested_dicts(self, inheritance_engine):
        """Test deep merging of nested dictionaries."""
        base = {
            "id": "base",
            "config": {
                "setting1": "value1",
                "setting2": "value2",
                "nested": {
                    "a": 1,
                    "b": 2
                }
            }
        }
        
        override = {
            "id": "child",
            "config": {
                "setting2": "override2",
                "setting3": "value3",
                "nested": {
                    "b": 20,
                    "c": 30
                }
            }
        }
        
        result = inheritance_engine._merge_templates(base, override)
        
        # Should have merged config
        assert result["config"]["setting1"] == "value1"  # From base
        assert result["config"]["setting2"] == "override2"  # Overridden
        assert result["config"]["setting3"] == "value3"  # From override
        
        # Should have deep merged nested dict
        assert result["config"]["nested"]["a"] == 1  # From base
        assert result["config"]["nested"]["b"] == 20  # Overridden
        assert result["config"]["nested"]["c"] == 30  # From override
    
    def test_circular_inheritance_detection(self, inheritance_engine):
        """Test that circular inheritance is detected."""
        template = {
            "id": "circular_test",
            "inherits": "core/base-templates/circular_a.yaml"
        }
        
        with pytest.raises(CircularInheritanceError, match="Circular inheritance"):
            inheritance_engine.resolve_inheritance(template)
    
    def test_missing_base_template(self, inheritance_engine):
        """Test error when base template doesn't exist."""
        template = {
            "id": "orphan",
            "inherits": "core/base-templates/nonexistent.yaml"
        }
        
        with pytest.raises(TemplateInheritanceError, match="Base template not found"):
            inheritance_engine.resolve_inheritance(template)
    
    def test_inheritance_chain_resolution(self, inheritance_engine):
        """Test getting the full inheritance chain."""
        template = {
            "id": "child",
            "inherits": "core/base-templates/parent.yaml"
        }
        
        chain = inheritance_engine.get_inheritance_chain(template)
        
        # Should return list of base template paths
        assert isinstance(chain, (list, tuple))
        assert len(chain) >= 1  # At least the immediate parent
        assert "parent" in str(chain[0]) if len(chain) > 0 else True
    
    def test_validate_inheritance_chain(self, inheritance_engine):
        """Test validating inheritance chain."""
        # Valid chain
        valid_template = {
            "id": "valid",
            "inherits": "core/base-templates/parent.yaml"
        }
        
        result = inheritance_engine.validate_inheritance_chain(valid_template)
        
        # validate_inheritance_chain returns (is_valid: bool, errors: Optional[List])
        if isinstance(result, tuple):
            is_valid, errors = result
            assert is_valid is True or errors is None or len(errors) == 0
        elif isinstance(result, list):
            # Returns list of errors
            assert len(result) == 0
        else:
            # Returns boolean
            assert result is True
        
        # Invalid chain (circular)
        invalid_template = {
            "id": "invalid",
            "inherits": "core/base-templates/circular_a.yaml"
        }
        
        try:
            result = inheritance_engine.validate_inheritance_chain(invalid_template)
            # If no exception, check result format
            if isinstance(result, tuple):
                is_valid, errors = result
                assert is_valid is False or (errors and len(errors) > 0)
            elif isinstance(result, list):
                assert len(result) > 0  # Should have errors
            else:
                assert result is False
        except CircularInheritanceError:
            # Acceptable - validation detected circular ref
            pass
    
    def test_base_template_caching(self, inheritance_engine):
        """Test that base templates are cached."""
        template1 = {
            "id": "child1",
            "inherits": "core/base-templates/grandparent.yaml"
        }
        
        template2 = {
            "id": "child2",
            "inherits": "core/base-templates/grandparent.yaml"
        }
        
        # Resolve both
        result1 = inheritance_engine.resolve_inheritance(template1)
        result2 = inheritance_engine.resolve_inheritance(template2)
        
        # Cache should have grandparent
        assert len(inheritance_engine.base_template_cache) > 0
        
        # Both should have same base content
        assert result1["sections"]["header"] == result2["sections"]["header"]
    
    def test_preserve_child_unique_fields(self, inheritance_engine):
        """Test that child template's unique fields are preserved."""
        template = {
            "id": "child",
            "inherits": "core/base-templates/grandparent.yaml",
            "unique_field": "child_only",
            "child_metadata": {
                "custom": "value"
            }
        }
        
        result = inheritance_engine.resolve_inheritance(template)
        
        assert result["unique_field"] == "child_only"
        assert result["child_metadata"]["custom"] == "value"
    
    def test_list_override_behavior(self, inheritance_engine):
        """Test how lists are handled in merge (replace vs extend)."""
        base = {
            "id": "base",
            "items": ["base1", "base2"]
        }
        
        override = {
            "id": "child",
            "items": ["child1"]
        }
        
        result = inheritance_engine._merge_templates(base, override)
        
        # Lists should be replaced, not merged
        assert result["items"] == ["child1"]
    
    def test_resolve_with_components(self, inheritance_engine):
        """Test resolving inheritance with component references."""
        template = {
            "id": "with_components",
            "inherits": "core/base-templates/grandparent.yaml",
            "sections": {
                "header": "{component:core/components/headers.yaml#custom}"
            }
        }
        
        # Should resolve without error (component may not exist, but structure is valid)
        result = inheritance_engine.resolve_with_components(template, context={})
        
        assert result is not None
        assert "sections" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
