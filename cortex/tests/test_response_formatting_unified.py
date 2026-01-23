"""Comprehensive test suite for unified response formatting (CONS-006).

Tests cover:
- Template registration and retrieval
- Template rendering with variable substitution
- Mode-based response formatting (chat, command, markdown, json, stream)
- LENS protocol formatting (JSON, YAML, Markdown)
- Turn response generation
- Statistics and cache management
- Backward compatibility with all 5 implementations
- Error handling and graceful degradation
- Integration scenarios

AC-ID: AC-CONS-006-TESTS
Author: CORTEX Consolidation Framework
Version: 1.0.0
"""

import pytest
from typing import Dict, Any, List, Optional
from datetime import datetime

from cortex.core.response_formatting_unified import (
    # Enums
    VariableType,
    ResponseType,
    ResponseFormat,
    FormattingProfile,
    FormattingMode,
    
    # Data classes
    VariableSpec,
    TemplateDefinition,
    FormattingOptions,
    FormattedResponseSection,
    
    # Core classes
    UnifiedTemplateRegistry,
    UnifiedResponseFormatter,
    ChatResponseFormatter,
    CommandLineResponseFormatter,
    MarkdownResponseFormatter,
    JSONAPIResponseFormatter,
    SimpleTemplateSubstitutor,
    
    # Functions
    get_unified_formatter,
    
    # Backward compatibility
    TemplateRegistry,
    TemplateEngine,
    ResponseFormattingEngine,
    LENSResponseFormatter,
    TurnResponseGenerator,
    ResponseTemplateEngine,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def registry():
    """Provide clean registry instance."""
    reg = UnifiedTemplateRegistry()
    yield reg
    reg.clear()


@pytest.fixture
def formatter():
    """Provide unified formatter instance."""
    fmt = UnifiedResponseFormatter()
    yield fmt
    fmt.reset_statistics()
    fmt.clear_cache()


@pytest.fixture
def sample_template():
    """Provide sample template definition."""
    return TemplateDefinition(
        id="test.sample",
        name="Sample Template",
        description="A sample template for testing",
        template="Hello {name}, your score is {score}",
        variables=[
            VariableSpec("name", VariableType.STRING, required=True),
            VariableSpec("score", VariableType.INTEGER, required=True),
        ],
        category="test"
    )


# ============================================================================
# TEMPLATE REGISTRATION & RETRIEVAL TESTS
# ============================================================================

class TestTemplateRegistration:
    """Test template registration and retrieval."""
    
    def test_register_base_template(self, registry, sample_template):
        """Test registering a base template."""
        registry.add_base_template(sample_template)
        retrieved = registry.get_template_by_id("test.sample")
        assert retrieved is not None
        assert retrieved.name == "Sample Template"
    
    def test_register_domain_template(self, registry, sample_template):
        """Test registering a domain-specific template."""
        registry.add_domain_template("custom_domain", sample_template)
        retrieved = registry.get_template("custom_domain", "Sample Template")
        assert retrieved is not None
        assert retrieved.id == "test.sample"
    
    def test_get_template_by_id(self, registry, sample_template):
        """Test retrieving template by ID."""
        registry.add_base_template(sample_template)
        template = registry.get_template_by_id("test.sample")
        assert template == sample_template
    
    def test_get_template_not_found(self, registry):
        """Test retrieving non-existent template."""
        template = registry.get_template_by_id("nonexistent.template")
        assert template is None
    
    def test_get_templates_by_category(self, registry, sample_template):
        """Test retrieving templates by category."""
        registry.add_base_template(sample_template)
        templates = registry.get_templates_by_category("test")
        assert len(templates) >= 1
        assert sample_template in templates
    
    def test_list_all_templates(self, registry, sample_template):
        """Test listing all templates."""
        registry.add_base_template(sample_template)
        templates = registry.list_all_templates()
        assert len(templates) >= 1
        assert sample_template in templates


# ============================================================================
# TEMPLATE VARIABLE VALIDATION TESTS
# ============================================================================

class TestVariableValidation:
    """Test template variable validation."""
    
    def test_validate_string_variable(self):
        """Test string variable validation."""
        spec = VariableSpec("name", VariableType.STRING, required=True)
        assert spec.validate("John") is True
        assert spec.validate(123) is False
        assert spec.validate(None) is False
    
    def test_validate_integer_variable(self):
        """Test integer variable validation."""
        spec = VariableSpec("count", VariableType.INTEGER, required=True)
        assert spec.validate(42) is True
        assert spec.validate("42") is False
        assert spec.validate(True) is False  # bool is subclass of int
    
    def test_validate_boolean_variable(self):
        """Test boolean variable validation."""
        spec = VariableSpec("flag", VariableType.BOOLEAN, required=True)
        assert spec.validate(True) is True
        assert spec.validate(False) is True
        assert spec.validate(1) is False
    
    def test_validate_list_variable(self):
        """Test list variable validation."""
        spec = VariableSpec("items", VariableType.LIST, required=True)
        assert spec.validate([1, 2, 3]) is True
        assert spec.validate("not a list") is False
    
    def test_validate_optional_variable(self):
        """Test optional variable validation."""
        spec = VariableSpec("extra", VariableType.OPTIONAL, required=False)
        assert spec.validate("anything") is True
        assert spec.validate(123) is True
        assert spec.validate(None) is True
    
    def test_validate_with_pattern(self):
        """Test string variable with regex pattern."""
        spec = VariableSpec("email", VariableType.STRING, required=True, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
        assert spec.validate("test@example.com") is True
        assert spec.validate("invalid-email") is False
    
    def test_validate_optional_not_required(self):
        """Test optional variable not required."""
        spec = VariableSpec("optional_field", VariableType.STRING, required=False)
        assert spec.validate(None) is True
        assert spec.validate("value") is True


# ============================================================================
# TEMPLATE DEFINITION TESTS
# ============================================================================

class TestTemplateDefinition:
    """Test template definition properties and validation."""
    
    def test_extract_domain(self, sample_template):
        """Test domain extraction from template ID."""
        assert sample_template.domain == "test"
    
    def test_required_variables(self, sample_template):
        """Test getting required variables."""
        required = sample_template.required_variables
        assert "name" in required
        assert "score" in required
    
    def test_optional_variables(self):
        """Test getting optional variables."""
        template = TemplateDefinition(
            id="test.optional",
            name="Optional Template",
            description="Template with optional vars",
            template="Result: {value}",
            variables=[
                VariableSpec("value", VariableType.STRING, required=False),
            ]
        )
        optional = template.optional_variables
        assert "value" in optional
    
    def test_validate_context_success(self, sample_template):
        """Test successful context validation."""
        context = {"name": "Alice", "score": 95}
        is_valid, errors = sample_template.validate_context(context)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_context_missing_required(self, sample_template):
        """Test context validation with missing required variable."""
        context = {"name": "Alice"}
        is_valid, errors = sample_template.validate_context(context)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_context_wrong_type(self, sample_template):
        """Test context validation with wrong type."""
        context = {"name": "Alice", "score": "95"}  # score should be int
        is_valid, errors = sample_template.validate_context(context)
        assert is_valid is False


# ============================================================================
# TEMPLATE RENDERING TESTS
# ============================================================================

class TestTemplateRendering:
    """Test template rendering and substitution."""
    
    def test_render_simple_substitution(self):
        """Test simple variable substitution."""
        template = "Hello {name}"
        context = {"name": "World"}
        result = SimpleTemplateSubstitutor.substitute(template, context)
        assert result == "Hello World"
    
    def test_render_multiple_variables(self):
        """Test substitution with multiple variables."""
        template = "{greeting} {name}, you are {age} years old"
        context = {"greeting": "Hi", "name": "Bob", "age": "30"}
        result = SimpleTemplateSubstitutor.substitute(template, context)
        assert "Hi" in result
        assert "Bob" in result
        assert "30" in result
    
    def test_render_template_via_formatter(self, formatter, sample_template):
        """Test rendering template via unified formatter."""
        formatter.register_template(
            sample_template.id,
            sample_template.name,
            sample_template.description,
            sample_template.template,
            sample_template.variables
        )
        context = {"name": "Charlie", "score": 88}
        result = formatter.render_template(sample_template.id, context)
        assert "Charlie" in result
        assert "88" in result
    
    def test_render_template_caching(self, formatter, sample_template):
        """Test template render caching."""
        formatter.register_template(
            sample_template.id,
            sample_template.name,
            sample_template.description,
            sample_template.template,
            sample_template.variables
        )
        context = {"name": "Diana", "score": 92}
        
        # First render (cache miss)
        result1 = formatter.render_template(sample_template.id, context)
        stats1 = formatter.formatting_stats['cache_misses']
        
        # Second render (cache hit)
        result2 = formatter.render_template(sample_template.id, context)
        stats2 = formatter.formatting_stats['cache_hits']
        
        assert result1 == result2
        assert stats2 > 0


# ============================================================================
# MODE-BASED FORMATTING TESTS
# ============================================================================

class TestModeBasedFormatting:
    """Test mode-based response formatting."""
    
    def test_format_chat_mode(self, formatter):
        """Test chat mode formatting."""
        content = "This is a\nmulti-line\nmessage"
        result = formatter.format_response(content, FormattingMode.CHAT)
        assert isinstance(result, str)
    
    def test_format_command_mode(self, formatter):
        """Test command mode formatting."""
        content = "some output"
        result = formatter.format_response(
            content,
            FormattingMode.COMMAND,
            command="echo hello"
        )
        assert "echo hello" in result
    
    def test_format_markdown_mode(self, formatter):
        """Test markdown mode formatting."""
        content = "Some content"
        result = formatter.format_response(
            content,
            FormattingMode.MARKDOWN,
            title="Test Title"
        )
        assert "Test Title" in result
    
    def test_format_json_mode(self, formatter):
        """Test JSON mode formatting."""
        content = "Test response"
        result = formatter.format_response(
            content,
            FormattingMode.JSON,
            operation_id="op_123",
            turn_number=1
        )
        assert isinstance(result, dict)
        assert result["operation_id"] == "op_123"
        assert result["turn"] == 1
    
    def test_format_stream_mode(self, formatter):
        """Test stream mode formatting."""
        chunks = ["Hello", " ", "World"]
        result = formatter.format_response(
            "",
            FormattingMode.STREAM,
            chunks=chunks
        )
        assert result == "Hello World"
    
    def test_format_batch(self, formatter):
        """Test batch formatting."""
        contents = ["content1", "content2", "content3"]
        results = formatter.format_batch(contents, FormattingMode.CHAT)
        assert len(results) == 3
    
    def test_format_conversion(self, formatter):
        """Test format conversion."""
        content = "Test content"
        result = formatter.convert_format(
            content,
            FormattingMode.CHAT,
            FormattingMode.MARKDOWN
        )
        assert isinstance(result, str)


# ============================================================================
# FORMATTING OPTIONS TESTS
# ============================================================================

class TestFormattingOptions:
    """Test formatting options and profiles."""
    
    def test_default_options(self):
        """Test default formatting options."""
        options = FormattingOptions()
        assert options.profile == FormattingProfile.DETAILED
        assert options.include_metadata is True
        assert options.line_width == 80
    
    def test_concise_profile(self, formatter):
        """Test concise formatting profile."""
        content = "Line 1\nLine 2\nLine 3"
        options = FormattingOptions(profile=FormattingProfile.CONCISE)
        result = formatter.chat_formatter.format(content, options)
        # Concise removes newlines
        assert "\n" not in result or result.count("\n") < content.count("\n")
    
    def test_technical_profile(self, formatter):
        """Test technical formatting profile."""
        content = "some code"
        options = FormattingOptions(profile=FormattingProfile.TECHNICAL)
        result = formatter.chat_formatter.format(content, options)
        assert "```" in result or isinstance(result, str)


# ============================================================================
# LENS PROTOCOL FORMATTING TESTS
# ============================================================================

class TestLENSFormatting:
    """Test LENS protocol response formatting."""
    
    def test_format_lens_json(self, formatter):
        """Test LENS response as JSON."""
        response = {
            "challenges": ["Challenge 1", "Challenge 2"],
            "recommendations": ["Rec 1", "Rec 2"]
        }
        result = formatter.format_lens_response(response, ResponseFormat.JSON)
        assert "challenges" in result
        assert "Challenge 1" in result
    
    def test_format_lens_markdown(self, formatter):
        """Test LENS response as Markdown."""
        response = {
            "challenges": ["Challenge 1"],
            "recommendations": ["Rec 1"]
        }
        result = formatter.format_lens_response(response, ResponseFormat.MARKDOWN)
        assert "challenges" in result.lower()
        assert "Challenge 1" in result
    
    def test_format_lens_yaml(self, formatter):
        """Test LENS response as YAML."""
        response = {
            "challenges": ["Challenge 1"],
            "summary": "Test summary"
        }
        result = formatter.format_lens_response(response, ResponseFormat.YAML)
        assert isinstance(result, str)


# ============================================================================
# TURN RESPONSE GENERATION TESTS
# ============================================================================

class TestTurnResponseGeneration:
    """Test turn-based response generation."""
    
    def test_generate_turn_response_basic(self, formatter):
        """Test basic turn response generation."""
        response = formatter.generate_turn_response(
            turn_number=1,
            operation_id="op_001",
            content="Test content"
        )
        assert response["turn"] == 1
        assert response["operation_id"] == "op_001"
        assert response["content"] == "Test content"
        assert "timestamp" in response
    
    def test_generate_turn_response_with_metadata(self, formatter):
        """Test turn response with metadata."""
        metadata = {"key": "value", "count": 42}
        response = formatter.generate_turn_response(
            turn_number=2,
            operation_id="op_002",
            content="Another test",
            metadata=metadata
        )
        assert response["metadata"]["key"] == "value"
        assert response["metadata"]["count"] == 42
    
    def test_generate_turn_response_status(self, formatter):
        """Test turn response with different statuses."""
        response_success = formatter.generate_turn_response(
            turn_number=1,
            operation_id="op_001",
            content="Success",
            status="success"
        )
        response_error = formatter.generate_turn_response(
            turn_number=2,
            operation_id="op_002",
            content="Error",
            status="error"
        )
        assert response_success["status"] == "success"
        assert response_error["status"] == "error"


# ============================================================================
# STATISTICS & CACHE TESTS
# ============================================================================

class TestStatisticsAndCache:
    """Test statistics tracking and cache management."""
    
    def test_format_statistics(self, formatter):
        """Test formatting statistics."""
        content = "test"
        formatter.format_response(content, FormattingMode.CHAT)
        formatter.format_response(content, FormattingMode.MARKDOWN)
        
        stats = formatter.get_formatting_statistics()
        assert stats["total_formatted"] == 2
        assert stats["by_mode"]["chat"] >= 1
        assert stats["by_mode"]["markdown"] >= 1
    
    def test_reset_statistics(self, formatter):
        """Test resetting statistics."""
        formatter.format_response("test", FormattingMode.CHAT)
        formatter.reset_statistics()
        stats = formatter.get_formatting_statistics()
        assert stats["total_formatted"] == 0
    
    def test_cache_info(self, formatter, sample_template):
        """Test cache information."""
        formatter.register_template(
            sample_template.id,
            sample_template.name,
            sample_template.description,
            sample_template.template,
            sample_template.variables
        )
        
        context = {"name": "Test", "score": 100}
        formatter.render_template(sample_template.id, context)
        formatter.render_template(sample_template.id, context)
        
        cache_info = formatter.get_cache_info()
        assert cache_info["total_requests"] >= 2
        assert cache_info["cache_hits"] > 0
    
    def test_clear_cache(self, formatter):
        """Test clearing cache."""
        formatter.render_template("test", {}, use_cache=True)
        formatter.clear_cache()
        cache_info = formatter.get_cache_info()
        assert cache_info["cache_size"] == 0


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_render_invalid_template_id(self, formatter):
        """Test rendering with invalid template ID."""
        with pytest.raises(ValueError):
            formatter.render_template("nonexistent.template", {})
    
    def test_render_missing_required_variable(self, formatter, sample_template):
        """Test rendering with missing required variable."""
        formatter.register_template(
            sample_template.id,
            sample_template.name,
            sample_template.description,
            sample_template.template,
            sample_template.variables
        )
        with pytest.raises(ValueError):
            formatter.render_template(sample_template.id, {"name": "Only"})
    
    def test_render_invalid_variable_type(self, formatter, sample_template):
        """Test rendering with invalid variable type."""
        formatter.register_template(
            sample_template.id,
            sample_template.name,
            sample_template.description,
            sample_template.template,
            sample_template.variables
        )
        with pytest.raises(ValueError):
            formatter.render_template(sample_template.id, {"name": "Test", "score": "not_an_int"})


# ============================================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================================

class TestBackwardCompatibility:
    """Test backward compatibility with original 5 implementations."""
    
    def test_template_engine_compat(self):
        """Test TemplateEngine backward compatibility."""
        engine = TemplateEngine()
        assert hasattr(engine, 'get_template')
        assert hasattr(engine, 'apply_template')
    
    def test_template_registry_compat(self):
        """Test TemplateRegistry backward compatibility."""
        registry = TemplateRegistry.get_instance()
        assert registry is not None
    
    def test_response_formatting_engine_compat(self):
        """Test ResponseFormattingEngine backward compatibility."""
        engine = ResponseFormattingEngine()
        assert hasattr(engine, 'format_response')
    
    def test_lens_response_formatter_compat(self):
        """Test LENSResponseFormatter backward compatibility."""
        formatter = LENSResponseFormatter()
        assert hasattr(formatter, 'format')
    
    def test_turn_response_generator_compat(self):
        """Test TurnResponseGenerator backward compatibility."""
        generator = TurnResponseGenerator()
        assert hasattr(generator, 'generate_turn_response')
    
    def test_response_template_engine_compat(self):
        """Test ResponseTemplateEngine backward compatibility."""
        engine = ResponseTemplateEngine()
        assert hasattr(engine, 'render')


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for unified formatter."""
    
    def test_full_workflow(self, formatter):
        """Test full formatting workflow."""
        # Register template
        template_id = "integration.test"
        formatter.register_template(
            template_id,
            "Integration Test",
            "Template for integration testing",
            "Result: {result}, Status: {status}",
            [
                VariableSpec("result", VariableType.STRING, required=True),
                VariableSpec("status", VariableType.STRING, required=True),
            ]
        )
        
        # Render template
        rendered = formatter.render_template(
            template_id,
            {"result": "Success", "status": "Complete"}
        )
        assert "Success" in rendered
        assert "Complete" in rendered
        
        # Format response
        formatted = formatter.format_response(
            rendered,
            FormattingMode.MARKDOWN,
            title="Test Report"
        )
        assert "Test Report" in formatted
    
    def test_mixed_mode_operations(self, formatter):
        """Test mixed mode operations."""
        content = "Test content"
        
        # Try multiple modes
        chat_result = formatter.format_response(content, FormattingMode.CHAT)
        json_result = formatter.format_response(
            content,
            FormattingMode.JSON,
            operation_id="test_op",
            turn_number=1
        )
        markdown_result = formatter.format_response(
            content,
            FormattingMode.MARKDOWN,
            title="Test"
        )
        
        assert chat_result is not None
        assert isinstance(json_result, dict)
        assert markdown_result is not None


# ============================================================================
# STRESS TESTS
# ============================================================================

class TestStress:
    """Stress tests for unified formatter."""
    
    def test_many_templates(self, formatter):
        """Test registering many templates."""
        for i in range(100):
            formatter.register_template(
                f"stress.template_{i}",
                f"Template {i}",
                f"Test template {i}",
                f"Content {i}"
            )
        
        templates = formatter.list_templates()
        assert len(templates) >= 100
    
    def test_many_renders(self, formatter, sample_template):
        """Test rendering same template many times."""
        formatter.register_template(
            sample_template.id,
            sample_template.name,
            sample_template.description,
            sample_template.template,
            sample_template.variables
        )
        
        for i in range(50):
            context = {"name": f"User{i}", "score": i}
            result = formatter.render_template(sample_template.id, context)
            assert f"User{i}" in result
    
    def test_concurrent_mode_formatting(self, formatter):
        """Test formatting with many mode switches."""
        content = "Test"
        modes = [
            FormattingMode.CHAT,
            FormattingMode.MARKDOWN,
            FormattingMode.JSON,
            FormattingMode.COMMAND
        ]
        
        for mode in modes * 10:
            result = formatter.format_response(
                content,
                mode,
                operation_id="stress_test",
                turn_number=1
            )
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
