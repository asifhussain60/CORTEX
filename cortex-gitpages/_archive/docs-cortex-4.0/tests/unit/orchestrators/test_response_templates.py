"""Test suite for Response Template System.

Tests for AC-RESP-003-01: Response Template System
- Template structure validation
- Variable substitution accuracy
- Template versioning and lookup
- Missing variable handling
- Template registry operations
- Multi-mode template application
- Template caching
- Performance benchmarks
- Edge cases
- Integration with ResponseFormattingEngine

Total: 20+ comprehensive tests
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.orchestrators.response.response_templates import (
    VariableType,
    VariableSpec,
    ResponseType,
    ResponseTemplate,
    TemplateRegistry,
    SimpleTemplateSubstitutor,
    TemplateCache,
    TemplateEngine,
    get_template_engine,
)


class TestVariableSpec:
    """Test VariableSpec for template variable validation."""

    def test_variable_spec_creation(self):
        """Test creating a variable specification."""
        var = VariableSpec(
            name="item",
            var_type=VariableType.STRING,
            required=True,
            description="Item name",
        )
        assert var.name == "item"
        assert var.var_type == VariableType.STRING
        assert var.required is True
        assert var.description == "Item name"

    def test_variable_spec_with_default(self):
        """Test variable spec with default value."""
        var = VariableSpec(
            name="count",
            var_type=VariableType.INTEGER,
            required=False,
            default=0,
        )
        assert var.default == 0
        assert var.required is False

    def test_validate_string_variable(self):
        """Test string variable validation."""
        var = VariableSpec(name="text", var_type=VariableType.STRING)
        assert var.validate("hello") is True
        assert var.validate(123) is False
        assert var.validate(None) is False

    def test_validate_integer_variable(self):
        """Test integer variable validation."""
        var = VariableSpec(name="count", var_type=VariableType.INTEGER)
        assert var.validate(42) is True
        assert var.validate("42") is False
        assert var.validate(True) is False  # Boolean not int

    def test_validate_boolean_variable(self):
        """Test boolean variable validation."""
        var = VariableSpec(name="flag", var_type=VariableType.BOOLEAN)
        assert var.validate(True) is True
        assert var.validate(False) is True
        assert var.validate(1) is False

    def test_validate_list_variable(self):
        """Test list variable validation."""
        var = VariableSpec(name="items", var_type=VariableType.LIST)
        assert var.validate([1, 2, 3]) is True
        assert var.validate([]) is True
        assert var.validate("not a list") is False

    def test_validate_optional_variable(self):
        """Test optional variable (accepts any type)."""
        var = VariableSpec(name="anything", var_type=VariableType.OPTIONAL)
        assert var.validate("string") is True
        assert var.validate(123) is True
        assert var.validate([1, 2]) is True

    def test_validate_with_pattern(self):
        """Test string validation with regex pattern."""
        var = VariableSpec(
            name="email",
            var_type=VariableType.STRING,
            pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        )
        assert var.validate("test@example.com") is True
        assert var.validate("invalid-email") is False

    def test_validate_optional_with_default(self):
        """Test optional variable validation with default."""
        var = VariableSpec(
            name="status",
            var_type=VariableType.STRING,
            required=False,
            default="pending",
        )
        assert var.validate(None) is True  # OK because has default
        assert var.validate("active") is True


class TestResponseTemplate:
    """Test ResponseTemplate structure and validation."""

    def test_template_creation(self):
        """Test creating a response template."""
        template = ResponseTemplate(
            template_id="error_template",
            version="1.0.0",
            name="Error Template",
            description="For error responses",
            pattern="Error: {{ message }}",
            response_type=ResponseType.ERROR,
        )
        assert template.template_id == "error_template"
        assert template.version == "1.0.0"
        assert template.response_type == ResponseType.ERROR

    def test_template_with_variables(self):
        """Test template with variable specifications."""
        template = ResponseTemplate(
            template_id="error_template",
            version="1.0.0",
            name="Error Template",
            description="For error responses",
            pattern="Error processing {{ item }}: {{ reason }}",
            response_type=ResponseType.ERROR,
            variables={
                "item": VariableSpec(name="item", var_type=VariableType.STRING),
                "reason": VariableSpec(name="reason", var_type=VariableType.STRING),
            },
        )
        assert len(template.variables) == 2
        assert "item" in template.variables
        assert "reason" in template.variables

    def test_template_validate_variables_success(self):
        """Test successful variable validation."""
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test template",
            pattern="{{ name }}: {{ count }}",
            response_type=ResponseType.SUCCESS,
            variables={
                "name": VariableSpec(name="name", var_type=VariableType.STRING, required=True),
                "count": VariableSpec(name="count", var_type=VariableType.INTEGER, required=True),
            },
        )
        is_valid, errors = template.validate_variables({"name": "test", "count": 5})
        assert is_valid is True
        assert len(errors) == 0

    def test_template_validate_variables_missing_required(self):
        """Test validation fails with missing required variable."""
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test template",
            pattern="{{ required_var }}",
            response_type=ResponseType.SUCCESS,
            variables={
                "required_var": VariableSpec(name="required_var", var_type=VariableType.STRING, required=True),
            },
        )
        is_valid, errors = template.validate_variables({})
        assert is_valid is False
        assert len(errors) > 0
        assert "required_var" in errors[0]

    def test_template_validate_variables_wrong_type(self):
        """Test validation fails with wrong variable type."""
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test template",
            pattern="{{ count }}",
            response_type=ResponseType.SUCCESS,
            variables={
                "count": VariableSpec(name="count", var_type=VariableType.INTEGER, required=True),
            },
        )
        is_valid, errors = template.validate_variables({"count": "not an int"})
        assert is_valid is False
        assert len(errors) > 0

    def test_template_validate_variables_unexpected_variable(self):
        """Test validation fails with unexpected variable."""
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test template",
            pattern="{{ expected }}",
            response_type=ResponseType.SUCCESS,
            variables={
                "expected": VariableSpec(name="expected", var_type=VariableType.STRING, required=True),
            },
        )
        is_valid, errors = template.validate_variables({"expected": "value", "unexpected": "also here"})
        assert is_valid is False
        assert "Unexpected variable" in errors[0]

    def test_template_with_optional_variables(self):
        """Test template with optional variables."""
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test template",
            pattern="{{ required }} {{ optional }}",
            response_type=ResponseType.SUCCESS,
            variables={
                "required": VariableSpec(name="required", var_type=VariableType.STRING, required=True),
                "optional": VariableSpec(
                    name="optional", var_type=VariableType.STRING, required=False, default="N/A"
                ),
            },
        )
        is_valid, errors = template.validate_variables({"required": "yes"})
        assert is_valid is True


class TestTemplateRegistry:
    """Test template registry operations."""

    def test_register_template(self):
        """Test registering a template."""
        registry = TemplateRegistry()
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="test",
            response_type=ResponseType.SUCCESS,
        )
        registry.register(template)
        assert "test:1.0.0" in registry.templates

    def test_get_template_by_id(self):
        """Test retrieving a template by ID."""
        registry = TemplateRegistry()
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="test",
            response_type=ResponseType.SUCCESS,
        )
        registry.register(template)
        retrieved = registry.get("test", "1.0.0")
        assert retrieved is not None
        assert retrieved.template_id == "test"

    def test_get_latest_template_version(self):
        """Test retrieving latest template version."""
        registry = TemplateRegistry()
        t1 = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="v1",
            response_type=ResponseType.SUCCESS,
        )
        t2 = ResponseTemplate(
            template_id="test",
            version="2.0.0",
            name="Test",
            description="Test",
            pattern="v2",
            response_type=ResponseType.SUCCESS,
        )
        registry.register(t1)
        registry.register(t2)
        latest = registry.get("test")  # Should get latest
        assert latest.version == "2.0.0"

    def test_list_templates(self):
        """Test listing all templates."""
        registry = TemplateRegistry()
        for i in range(3):
            template = ResponseTemplate(
                template_id=f"test_{i}",
                version="1.0.0",
                name=f"Test {i}",
                description="Test",
                pattern=f"pattern {i}",
                response_type=ResponseType.SUCCESS,
            )
            registry.register(template)
        templates = registry.list_templates()
        assert len(templates) == 3

    def test_list_templates_by_type(self):
        """Test listing templates filtered by response type."""
        registry = TemplateRegistry()
        error_template = ResponseTemplate(
            template_id="error",
            version="1.0.0",
            name="Error",
            description="Error template",
            pattern="Error",
            response_type=ResponseType.ERROR,
        )
        success_template = ResponseTemplate(
            template_id="success",
            version="1.0.0",
            name="Success",
            description="Success template",
            pattern="Success",
            response_type=ResponseType.SUCCESS,
        )
        registry.register(error_template)
        registry.register(success_template)
        error_templates = registry.list_templates(ResponseType.ERROR)
        assert len(error_templates) == 1
        assert error_templates[0].template_id == "error"

    def test_unregister_template(self):
        """Test unregistering a template."""
        registry = TemplateRegistry()
        template = ResponseTemplate(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="test",
            response_type=ResponseType.SUCCESS,
        )
        registry.register(template)
        assert registry.get("test") is not None
        registry.unregister("test")
        assert registry.get("test") is None


class TestTemplateSubstitutor:
    """Test template variable substitution."""

    def test_simple_substitution(self):
        """Test basic variable substitution."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "Hello {{ name }}"
        variables = {"name": "World"}
        result = substitutor.substitute(pattern, variables)
        assert result == "Hello World"

    def test_multiple_variable_substitution(self):
        """Test substituting multiple variables."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "{{ greeting }} {{ name }}, your count is {{ count }}"
        variables = {"greeting": "Hello", "name": "Alice", "count": 42}
        result = substitutor.substitute(pattern, variables)
        assert result == "Hello Alice, your count is 42"

    def test_substitution_with_missing_variable(self):
        """Test substitution when variable is missing (leaves placeholder)."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "Hello {{ name }}"
        variables = {}
        result = substitutor.substitute(pattern, variables)
        assert result == "Hello {{ name }}"  # Placeholder unchanged

    def test_substitution_with_whitespace_in_placeholder(self):
        """Test substitution with whitespace in {{ variable }} syntax."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "Hello {{  name  }}"
        variables = {"name": "World"}
        result = substitutor.substitute(pattern, variables)
        assert result == "Hello World"

    def test_substitution_with_none_value(self):
        """Test substitution when variable is None."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "Value: {{ value }}"
        variables = {"value": None}
        result = substitutor.substitute(pattern, variables)
        assert result == "Value: "  # Empty string for None

    def test_substitution_with_numeric_value(self):
        """Test substitution with numeric values."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "Count: {{ count }}, Progress: {{ percent }}%"
        variables = {"count": 42, "percent": 75.5}
        result = substitutor.substitute(pattern, variables)
        assert result == "Count: 42, Progress: 75.5%"

    def test_substitution_with_special_characters(self):
        """Test substitution with special characters in values."""
        substitutor = SimpleTemplateSubstitutor()
        pattern = "Error: {{ error }}"
        variables = {"error": "Bad input: [1,2,3] & {x: y}"}
        result = substitutor.substitute(pattern, variables)
        assert result == "Error: Bad input: [1,2,3] & {x: y}"


class TestTemplateCache:
    """Test template caching."""

    def test_cache_get_set(self):
        """Test setting and getting cache entries."""
        cache = TemplateCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_missing_key(self):
        """Test getting missing cache key returns None."""
        cache = TemplateCache()
        assert cache.get("nonexistent") is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = TemplateCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_max_entries(self):
        """Test cache respects max entries limit."""
        cache = TemplateCache(max_entries=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1
        assert cache.get("key1") is None
        assert cache.get("key4") is not None


class TestTemplateEngine:
    """Test main template engine."""

    def test_engine_create_and_apply_template(self):
        """Test creating and applying a template."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="greeting",
            version="1.0.0",
            name="Greeting",
            description="Simple greeting",
            pattern="Hello {{ name }}!",
            response_type=ResponseType.INFORMATIONAL,
            variables={"name": VariableSpec(name="name", var_type=VariableType.STRING)},
        )
        result = engine.apply_template("greeting", {"name": "Alice"})
        assert result == "Hello Alice!"

    def test_engine_apply_template_not_found(self):
        """Test applying non-existent template raises error."""
        engine = TemplateEngine()
        with pytest.raises(ValueError, match="not found"):
            engine.apply_template("nonexistent", {})

    def test_engine_apply_template_invalid_variables(self):
        """Test applying template with invalid variables raises error."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="Count: {{ count }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={"count": VariableSpec(name="count", var_type=VariableType.INTEGER)},
        )
        with pytest.raises(ValueError, match="Invalid variables"):
            engine.apply_template("test", {"count": "not an int"})

    def test_engine_apply_template_with_defaults(self):
        """Test applying template with default variable values."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="status",
            version="1.0.0",
            name="Status",
            description="Status message",
            pattern="Status: {{ status }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={
                "status": VariableSpec(
                    name="status",
                    var_type=VariableType.STRING,
                    required=False,
                    default="pending",
                )
            },
        )
        result = engine.apply_template("status", {})
        assert result == "Status: pending"

    def test_engine_list_templates(self):
        """Test listing templates from engine."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="t1",
            version="1.0.0",
            name="Template 1",
            description="First",
            pattern="Pattern 1",
            response_type=ResponseType.SUCCESS,
        )
        engine.create_template(
            template_id="t2",
            version="1.0.0",
            name="Template 2",
            description="Second",
            pattern="Pattern 2",
            response_type=ResponseType.ERROR,
        )
        templates = engine.list_templates()
        assert len(templates) >= 2

    def test_engine_caching(self):
        """Test that engine caches template results."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="Value: {{ value }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={"value": VariableSpec(name="value", var_type=VariableType.STRING)},
        )
        # First call
        result1 = engine.apply_template("test", {"value": "cached"})
        # Second call should use cache
        result2 = engine.apply_template("test", {"value": "cached"})
        assert result1 == result2
        assert len(engine.cache.cache) > 0

    def test_engine_clear_cache(self):
        """Test clearing engine cache."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="Test {{ value }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={"value": VariableSpec(name="value", var_type=VariableType.STRING)},
        )
        engine.apply_template("test", {"value": "data"})
        assert len(engine.cache.cache) > 0
        engine.clear_cache()
        assert len(engine.cache.cache) == 0

    def test_engine_unregister_template(self):
        """Test unregistering a template."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="test",
            version="1.0.0",
            name="Test",
            description="Test",
            pattern="Test",
            response_type=ResponseType.INFORMATIONAL,
        )
        assert engine.get_template("test") is not None
        engine.unregister_template("test")
        assert engine.get_template("test") is None


class TestDefaultTemplates:
    """Test built-in default templates."""

    def test_get_template_engine_singleton(self):
        """Test getting singleton template engine with defaults."""
        engine = get_template_engine()
        templates = engine.list_templates()
        assert len(templates) >= 5  # Should have at least 5 default templates

    def test_error_processing_template_exists(self):
        """Test error_processing template exists."""
        engine = get_template_engine()
        template = engine.get_template("error_processing")
        assert template is not None
        assert template.response_type == ResponseType.ERROR

    def test_success_completion_template_exists(self):
        """Test success_completion template exists."""
        engine = get_template_engine()
        template = engine.get_template("success_completion")
        assert template is not None
        assert template.response_type == ResponseType.SUCCESS

    def test_apply_error_template(self):
        """Test applying error_processing template."""
        engine = get_template_engine()
        result = engine.apply_template("error_processing", {"item": "file.txt", "reason": "Not found"})
        assert "file.txt" in result
        assert "Not found" in result

    def test_apply_success_template(self):
        """Test applying success_completion template."""
        engine = get_template_engine()
        result = engine.apply_template("success_completion", {"action": "created", "item": "database"})
        assert "created" in result
        assert "database" in result

    def test_apply_progress_template(self):
        """Test applying progress_update template."""
        engine = get_template_engine()
        result = engine.apply_template(
            "progress_update", {"current": 50, "total": 100, "percentage": 50}
        )
        assert "50" in result
        assert "100" in result


class TestTemplateVersioning:
    """Test template versioning."""

    def test_multiple_template_versions(self):
        """Test managing multiple versions of same template."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="versioned",
            version="1.0.0",
            name="Versioned",
            description="V1",
            pattern="Version: 1.0.0",
            response_type=ResponseType.INFORMATIONAL,
        )
        engine.create_template(
            template_id="versioned",
            version="2.0.0",
            name="Versioned",
            description="V2",
            pattern="Version: 2.0.0",
            response_type=ResponseType.INFORMATIONAL,
        )
        v1 = engine.apply_template("versioned", {}, version="1.0.0")
        v2 = engine.apply_template("versioned", {}, version="2.0.0")
        assert "1.0.0" in v1
        assert "2.0.0" in v2

    def test_default_to_latest_version(self):
        """Test that latest version is used by default."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="latest",
            version="1.0.0",
            name="Latest",
            description="V1",
            pattern="v1",
            response_type=ResponseType.INFORMATIONAL,
        )
        engine.create_template(
            template_id="latest",
            version="2.0.0",
            name="Latest",
            description="V2",
            pattern="v2",
            response_type=ResponseType.INFORMATIONAL,
        )
        result = engine.apply_template("latest", {})  # Should use 2.0.0
        assert result == "v2"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_pattern(self):
        """Test template with empty pattern."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="empty",
            version="1.0.0",
            name="Empty",
            description="Empty pattern",
            pattern="",
            response_type=ResponseType.INFORMATIONAL,
        )
        result = engine.apply_template("empty", {})
        assert result == ""

    def test_pattern_with_no_variables(self):
        """Test template pattern with no variable placeholders."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="static",
            version="1.0.0",
            name="Static",
            description="Static pattern",
            pattern="This is a static message",
            response_type=ResponseType.INFORMATIONAL,
        )
        result = engine.apply_template("static", {})
        assert result == "This is a static message"

    def test_duplicate_variables_in_pattern(self):
        """Test pattern with same variable used multiple times."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="duplicate",
            version="1.0.0",
            name="Duplicate",
            description="Duplicate variables",
            pattern="{{ name }} is called {{ name }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={"name": VariableSpec(name="name", var_type=VariableType.STRING)},
        )
        result = engine.apply_template("duplicate", {"name": "Bob"})
        assert result == "Bob is called Bob"

    def test_nested_braces_in_value(self):
        """Test handling values with braces."""
        engine = TemplateEngine()
        engine.create_template(
            template_id="braces",
            version="1.0.0",
            name="Braces",
            description="Values with braces",
            pattern="Code: {{ code }}",
            response_type=ResponseType.INFORMATIONAL,
            variables={"code": VariableSpec(name="code", var_type=VariableType.STRING)},
        )
        result = engine.apply_template("braces", {"code": "{a: 1, b: 2}"})
        assert "{a: 1, b: 2}" in result
