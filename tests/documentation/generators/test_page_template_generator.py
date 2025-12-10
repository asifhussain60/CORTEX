"""
Tests for PageTemplateGenerator

TDD RED Phase - Tests written BEFORE implementation
These tests MUST fail initially to prove they test real behavior.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil
import yaml


class TestPageTemplateGeneratorRED:
    """
    RED Phase Tests - Must fail before implementation
    
    Acceptance Criteria:
    1. 6 template types implemented
    2. API docs extracted from all src/ modules
    3. Operation guides auto-generated for all 55+ operations
    4. Templates support custom frontmatter
    5. Generated pages pass MkDocs validation
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with sample source files"""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create src/ directory with sample modules
        src_dir = workspace / "src"
        src_dir.mkdir()
        
        # Create sample Python module with docstrings
        sample_module = src_dir / "sample_module.py"
        sample_module.write_text('''"""
Sample Module

This module demonstrates docstring extraction.
"""

def sample_function(param1: str, param2: int) -> bool:
    """
    Sample function with docstring.
    
    Args:
        param1: First parameter (string)
        param2: Second parameter (integer)
        
    Returns:
        Boolean result
        
    Example:
        >>> sample_function("test", 42)
        True
    """
    return True


class SampleClass:
    """
    Sample class with methods.
    
    Attributes:
        name: Instance name
        value: Instance value
    """
    
    def __init__(self, name: str):
        """Initialize with name"""
        self.name = name
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get instance information.
        
        Returns:
            Dictionary with instance details
        """
        return {"name": self.name}
''')
        
        # Create cortex-operations.yaml
        operations_file = workspace / "cortex-operations.yaml"
        operations_data = {
            "operations": [
                {
                    "name": "test_operation_1",
                    "description": "First test operation",
                    "category": "testing",
                    "command": "test 1",
                    "parameters": [
                        {"name": "param1", "type": "string", "required": True}
                    ]
                },
                {
                    "name": "test_operation_2",
                    "description": "Second test operation",
                    "category": "testing",
                    "command": "test 2",
                    "parameters": []
                }
            ]
        }
        
        with open(operations_file, 'w') as f:
            yaml.dump(operations_data, f)
        
        # Create templates directory
        templates_dir = workspace / "templates"
        templates_dir.mkdir()
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_class_exists(self):
        """AC1 Setup: PageTemplateGenerator class must exist"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        assert PageTemplateGenerator is not None
    
    def test_six_template_types_exist(self, temp_workspace):
        """AC1: 6 template types implemented"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Should have 6 template types
        template_types = generator.get_template_types()
        
        assert len(template_types) == 6
        assert "api_reference" in template_types
        assert "operation_guide" in template_types
        assert "module_docs" in template_types
        assert "feature_showcase" in template_types
        assert "tutorial" in template_types
        assert "troubleshooting" in template_types
    
    def test_extracts_docstrings_from_python_modules(self, temp_workspace):
        """AC2: API docs extracted from all src/ modules"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Extract docstrings from sample module
        module_path = temp_workspace / "src" / "sample_module.py"
        docstrings = generator.extract_module_docstrings(module_path)
        
        # Should extract module docstring
        assert "module" in docstrings
        assert "Sample Module" in docstrings["module"]
        
        # Should extract function docstrings
        assert "functions" in docstrings
        assert len(docstrings["functions"]) >= 1
        assert "sample_function" in docstrings["functions"][0]["name"]
        
        # Should extract class docstrings
        assert "classes" in docstrings
        assert len(docstrings["classes"]) >= 1
        assert "SampleClass" in docstrings["classes"][0]["name"]
    
    def test_generates_api_reference_page(self, temp_workspace):
        """AC2: Generate API reference from Python docstrings"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Generate API reference for sample module
        module_path = temp_workspace / "src" / "sample_module.py"
        api_page = generator.generate_api_reference(module_path)
        
        assert api_page is not None
        assert "sample_function" in api_page
        assert "SampleClass" in api_page
        assert "Args:" in api_page or "Parameters:" in api_page
        assert "Returns:" in api_page
    
    def test_discovers_all_src_modules(self, temp_workspace):
        """AC2: API docs extracted from all src/ modules"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Discover all Python modules in src/
        modules = generator.discover_python_modules()
        
        assert len(modules) >= 1
        assert any("sample_module.py" in str(m) for m in modules)
    
    def test_generates_operation_guides(self, temp_workspace):
        """AC3: Operation guides auto-generated for all 55+ operations"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Load operations from YAML
        operations_file = temp_workspace / "cortex-operations.yaml"
        operation_guides = generator.generate_operation_guides(operations_file)
        
        # Should generate guide for each operation
        assert len(operation_guides) == 2  # Test has 2 operations
        
        # Each guide should have required sections
        for guide in operation_guides:
            assert "name" in guide
            assert "description" in guide
            assert "command" in guide
            assert "content" in guide
    
    def test_operation_guide_has_proper_structure(self, temp_workspace):
        """AC3: Operation guide has proper markdown structure"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        operations_file = temp_workspace / "cortex-operations.yaml"
        guides = generator.generate_operation_guides(operations_file)
        
        first_guide = guides[0]["content"]
        
        # Should have frontmatter
        assert first_guide.startswith("---")
        
        # Should have headings
        assert "# " in first_guide or "## " in first_guide
        
        # Should have description
        assert "description" in first_guide.lower() or "Description" in first_guide
    
    def test_templates_support_custom_frontmatter(self, temp_workspace):
        """AC4: Templates support custom frontmatter"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Generate page with custom frontmatter
        custom_frontmatter = {
            "title": "Custom Page",
            "category": "custom",
            "weight": 50,
            "author": "Test Author"
        }
        
        page_content = generator.generate_from_template(
            template_type="module_docs",
            data={"module_name": "test"},
            frontmatter=custom_frontmatter
        )
        
        # Should include custom frontmatter
        assert "---" in page_content
        assert "title: Custom Page" in page_content
        assert "author: Test Author" in page_content
    
    def test_generated_pages_have_valid_frontmatter(self, temp_workspace):
        """AC5: Generated pages pass MkDocs validation"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Generate a page
        module_path = temp_workspace / "src" / "sample_module.py"
        page = generator.generate_api_reference(module_path)
        
        # Should have valid YAML frontmatter
        assert page.startswith("---")
        
        # Extract frontmatter
        parts = page.split("---")
        assert len(parts) >= 3  # Empty, frontmatter, content
        
        frontmatter_str = parts[1]
        
        # Should parse as valid YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            assert isinstance(frontmatter, dict)
            assert "title" in frontmatter
        except yaml.YAMLError:
            pytest.fail("Generated frontmatter is not valid YAML")
    
    def test_generated_pages_have_valid_markdown(self, temp_workspace):
        """AC5: Generated pages have valid markdown structure"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Generate pages from different templates
        module_path = temp_workspace / "src" / "sample_module.py"
        api_page = generator.generate_api_reference(module_path)
        
        # Check for valid markdown elements
        assert "#" in api_page  # Headings
        
        # Should have content after frontmatter
        content_section = api_page.split("---", 2)[2] if api_page.count("---") >= 2 else api_page
        assert len(content_section.strip()) > 0
    
    def test_all_template_types_can_generate_pages(self, temp_workspace):
        """AC1: All 6 template types can generate pages"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        template_types = generator.get_template_types()
        
        for template_type in template_types:
            # Should be able to generate a page from each template
            # Even if minimal, should not crash
            try:
                if template_type == "api_reference":
                    page = generator.generate_from_template(
                        template_type,
                        data={"module_name": "test", "functions": [], "classes": []}
                    )
                elif template_type == "operation_guide":
                    page = generator.generate_from_template(
                        template_type,
                        data={"name": "test_op", "description": "Test", "command": "test"}
                    )
                else:
                    page = generator.generate_from_template(
                        template_type,
                        data={"title": "Test"}
                    )
                
                assert page is not None
                assert len(page) > 0
                
            except Exception as e:
                pytest.fail(f"Template {template_type} failed to generate: {e}")
    
    def test_handles_module_without_docstrings(self, temp_workspace):
        """Edge Case: Module without docstrings should not crash"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        # Create module without docstrings
        no_docs_module = temp_workspace / "src" / "no_docs.py"
        no_docs_module.write_text("def function_without_docs():\n    pass\n")
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Should handle gracefully
        try:
            docstrings = generator.extract_module_docstrings(no_docs_module)
            assert docstrings is not None
        except Exception as e:
            pytest.fail(f"Should handle missing docstrings gracefully, but raised: {e}")
    
    def test_handles_invalid_operations_yaml(self, temp_workspace):
        """Edge Case: Invalid operations YAML should not crash"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        # Create invalid YAML file
        invalid_file = temp_workspace / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content:")
        
        generator = PageTemplateGenerator(temp_workspace)
        
        # Should handle gracefully
        try:
            guides = generator.generate_operation_guides(invalid_file)
            assert guides is not None or guides == []
        except Exception as e:
            pytest.fail(f"Should handle invalid YAML gracefully, but raised: {e}")
    
    def test_handles_nonexistent_src_directory(self, temp_workspace):
        """Edge Case: Missing src/ directory should return empty list"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        # Create workspace without src/ directory
        no_src_workspace = temp_workspace / "no_src"
        no_src_workspace.mkdir()
        
        generator = PageTemplateGenerator(no_src_workspace)
        modules = generator.discover_python_modules()
        
        assert modules == []
    
    def test_handles_invalid_template_type(self, temp_workspace):
        """Edge Case: Invalid template type should raise ValueError"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        generator = PageTemplateGenerator(temp_workspace)
        
        with pytest.raises(ValueError, match="Unknown template type"):
            generator.generate_from_template("nonexistent_template", {})
    
    def test_operations_yaml_without_operations_key(self, temp_workspace):
        """Edge Case: YAML without 'operations' key should return empty"""
        from documentation.generators.page_template_generator import (
            PageTemplateGenerator
        )
        
        # Create YAML without operations key
        no_ops_file = temp_workspace / "no_ops.yaml"
        with open(no_ops_file, 'w') as f:
            yaml.dump({"some_other_key": "value"}, f)
        
        generator = PageTemplateGenerator(temp_workspace)
        guides = generator.generate_operation_guides(no_ops_file)
        
        assert guides == []
