"""
Tests for Documentation Generation Orchestrator.

Tests docstring extraction, API reference generation, and usage guide creation.
"""

import pytest
import ast
from pathlib import Path
from src.operations.utilities.documentation_generation_orchestrator import (
    DocumentationGenerationOrchestrator,
    DocstringInfo,
    APIReference,
    UsageGuide
)


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return DocumentationGenerationOrchestrator()


@pytest.fixture
def sample_module_code():
    """Sample Python module for testing."""
    return '''
def add(x, y):
    """Add two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
    """
    return x + y

class Calculator:
    """Simple calculator class."""
    
    def multiply(self, x, y):
        """Multiply two numbers."""
        return x * y
'''


class TestDocstringExtraction:
    """Test docstring extraction capabilities."""

    def test_extract_function_docstring(self, orchestrator, sample_module_code):
        """Test extracting function docstrings."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        
        assert len(docstrings) > 0
        assert any(d.name == 'add' for d in docstrings)

    def test_extract_class_docstring(self, orchestrator, sample_module_code):
        """Test extracting class docstrings."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        
        assert any(d.name == 'Calculator' for d in docstrings)
        assert any(d.type == 'class' for d in docstrings)

    def test_extract_method_docstring(self, orchestrator, sample_module_code):
        """Test extracting method docstrings."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        
        assert any(d.name == 'multiply' for d in docstrings)

    def test_docstring_content(self, orchestrator, sample_module_code):
        """Test docstring content extraction."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        add_doc = next(d for d in docstrings if d.name == 'add')
        
        assert 'Add two numbers' in add_doc.docstring
        assert 'Args:' in add_doc.docstring


class TestAPIReferenceGeneration:
    """Test API reference generation."""

    def test_generate_api_reference(self, orchestrator, sample_module_code):
        """Test basic API reference generation."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        api_ref = orchestrator.generate_api_reference(docstrings, module_name="calculator")
        
        assert isinstance(api_ref, APIReference)
        assert api_ref.module_name == "calculator"
        assert len(api_ref.markdown) > 0

    def test_api_reference_includes_functions(self, orchestrator, sample_module_code):
        """Test API reference includes functions."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        api_ref = orchestrator.generate_api_reference(docstrings)
        
        assert '## add' in api_ref.markdown or '### add' in api_ref.markdown

    def test_api_reference_includes_classes(self, orchestrator, sample_module_code):
        """Test API reference includes classes."""
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        api_ref = orchestrator.generate_api_reference(docstrings)
        
        assert 'Calculator' in api_ref.markdown


class TestUsageGuideCreation:
    """Test usage guide generation."""

    def test_create_usage_guide_basic(self, orchestrator):
        """Test basic usage guide creation."""
        examples = [
            {"title": "Example 1", "code": "print('hello')"}
        ]
        guide = orchestrator.create_usage_guide("MyModule", examples)
        
        assert isinstance(guide, UsageGuide)
        assert guide.module_name == "MyModule"
        assert len(guide.markdown) > 0

    def test_usage_guide_includes_examples(self, orchestrator):
        """Test usage guide includes code examples."""
        examples = [
            {"title": "Basic Usage", "code": "x = 1 + 2"}
        ]
        guide = orchestrator.create_usage_guide("test", examples)
        
        assert "Basic Usage" in guide.markdown
        assert "```" in guide.markdown

    def test_usage_guide_with_description(self, orchestrator):
        """Test usage guide with description."""
        guide = orchestrator.create_usage_guide(
            "test",
            [],
            description="This is a test module"
        )
        
        assert "This is a test module" in guide.markdown


class TestIntegration:
    """Test integrated documentation workflows."""

    def test_full_documentation_workflow(self, orchestrator, sample_module_code):
        """Test complete documentation generation workflow."""
        # Extract docstrings
        docstrings = orchestrator.extract_docstrings(sample_module_code)
        
        # Generate API reference
        api_ref = orchestrator.generate_api_reference(docstrings, module_name="calc")
        
        # Create usage guide
        examples = [{"title": "Example", "code": "calc.add(1, 2)"}]
        usage = orchestrator.create_usage_guide("calc", examples)
        
        assert len(docstrings) > 0
        assert len(api_ref.markdown) > 0
        assert len(usage.markdown) > 0
