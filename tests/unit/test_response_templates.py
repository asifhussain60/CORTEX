"""
Comprehensive test suite for response template system.

Tests cover:
- Template loading from YAML
- Template registry operations
- Template inheritance resolution
- Template rendering with variable substitution
- Error handling and validation
- Integration with domain mappings
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.core.response_template_engine import (
    TemplateVariable,
    TemplateDefinition,
    DomainTemplateMetadata,
    ResponseTemplateRegistry,
    ResponseTemplateLoader,
    ResponseTemplateEngine,
    ResponseTemplatePopulator,
)


# =============================================================================
# TEST: TemplateVariable
# =============================================================================

class TestTemplateVariable:
    """Test TemplateVariable dataclass."""
    
    def test_create_required_string_variable(self):
        """Test creating a required string variable."""
        var = TemplateVariable(
            name="test_name",
            var_type="string",
            required=True,
            example="example"
        )
        assert var.name == "test_name"
        assert var.var_type == "string"
        assert var.required is True
        assert var.example == "example"
    
    def test_create_optional_integer_variable(self):
        """Test creating an optional integer variable."""
        var = TemplateVariable(
            name="count",
            var_type="integer",
            required=False
        )
        assert var.name == "count"
        assert var.var_type == "integer"
        assert var.required is False
    
    def test_invalid_variable_type_raises_error(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid variable type"):
            TemplateVariable(
                name="test",
                var_type="invalid_type",
                required=True
            )
    
    def test_valid_variable_types(self):
        """Test all valid variable types."""
        valid_types = ["string", "integer", "number", "boolean"]
        for vtype in valid_types:
            var = TemplateVariable(
                name=f"var_{vtype}",
                var_type=vtype,
                required=True
            )
            assert var.var_type == vtype


# =============================================================================
# TEST: TemplateDefinition
# =============================================================================

class TestTemplateDefinition:
    """Test TemplateDefinition dataclass."""
    
    def test_create_basic_template(self):
        """Test creating a basic template."""
        template = TemplateDefinition(
            id="test.status.success",
            name="Success",
            description="Success message",
            template="Success: {message}",
            variables=[
                TemplateVariable("message", "string", required=True)
            ],
            severity="INFO",
            category="status"
        )
        assert template.id == "test.status.success"
        assert template.domain == "test"
    
    def test_required_variables_property(self):
        """Test required_variables property."""
        template = TemplateDefinition(
            id="test.id",
            name="Test",
            description="Test",
            template="",
            variables=[
                TemplateVariable("required_var", "string", required=True),
                TemplateVariable("optional_var", "string", required=False),
            ],
            severity="INFO",
            category="test"
        )
        assert template.required_variables == ["required_var"]
        assert template.optional_variables == ["optional_var"]
    
    def test_domain_extraction(self):
        """Test domain extraction from template ID."""
        template = TemplateDefinition(
            id="tdd.test.success",
            name="Test",
            description="Test",
            template="",
            variables=[],
            severity="INFO",
            category="test"
        )
        assert template.domain == "tdd"
    
    def test_validate_context_all_required_present(self):
        """Test validation with all required variables present."""
        template = TemplateDefinition(
            id="test.id",
            name="Test",
            description="Test",
            template="{name} {age}",
            variables=[
                TemplateVariable("name", "string", required=True),
                TemplateVariable("age", "integer", required=True),
            ],
            severity="INFO",
            category="test"
        )
        context = {"name": "John", "age": 30}
        is_valid, errors = template.validate_context(context)
        assert is_valid is True
        assert errors == []
    
    def test_validate_context_missing_required(self):
        """Test validation fails with missing required variable."""
        template = TemplateDefinition(
            id="test.id",
            name="Test",
            description="Test",
            template="{name}",
            variables=[
                TemplateVariable("name", "string", required=True),
            ],
            severity="INFO",
            category="test"
        )
        context = {}
        is_valid, errors = template.validate_context(context)
        assert is_valid is False
        assert any("Missing required variable: name" in e for e in errors)
    
    def test_validate_context_type_checking(self):
        """Test validation checks variable types."""
        template = TemplateDefinition(
            id="test.id",
            name="Test",
            description="Test",
            template="",
            variables=[
                TemplateVariable("count", "integer", required=True),
            ],
            severity="INFO",
            category="test"
        )
        # Wrong type
        context = {"count": "not_an_integer"}
        is_valid, errors = template.validate_context(context)
        assert is_valid is False
        assert any("wrong type" in e for e in errors)
        
        # Correct type
        context = {"count": 42}
        is_valid, errors = template.validate_context(context)
        assert is_valid is True


# =============================================================================
# TEST: ResponseTemplateRegistry
# =============================================================================

class TestResponseTemplateRegistry:
    """Test ResponseTemplateRegistry singleton."""
    
    def teardown_method(self):
        """Clear registry after each test."""
        registry = ResponseTemplateRegistry.get_instance()
        registry.clear()
    
    def test_singleton_pattern(self):
        """Test registry is singleton."""
        reg1 = ResponseTemplateRegistry.get_instance()
        reg2 = ResponseTemplateRegistry.get_instance()
        assert reg1 is reg2
    
    def test_add_base_template(self):
        """Test adding base template."""
        registry = ResponseTemplateRegistry.get_instance()
        template = TemplateDefinition(
            id="base.status.success",
            name="Success",
            description="Success",
            template="Success",
            variables=[],
            severity="INFO",
            category="status"
        )
        registry.add_base_template(template)
        assert "base.status.success" in registry.base_templates
    
    def test_add_domain_template(self):
        """Test adding domain template."""
        registry = ResponseTemplateRegistry.get_instance()
        template = TemplateDefinition(
            id="tdd.test.success",
            name="Test Success",
            description="Test success",
            template="Test passed",
            variables=[],
            severity="INFO",
            category="test"
        )
        registry.add_domain_template("tdd", template)
        assert "tdd" in registry.domain_templates
        assert "tdd.test.success" in registry.domain_templates["tdd"].templates
    
    def test_get_template_domain_specific(self):
        """Test getting domain-specific template."""
        registry = ResponseTemplateRegistry.get_instance()
        template = TemplateDefinition(
            id="tdd.test.complete",
            name="Test Complete",
            description="Test",
            template="All tests passed",
            variables=[],
            severity="INFO",
            category="test"
        )
        registry.add_domain_template("tdd", template)
        
        retrieved = registry.get_template("tdd", "Test Complete")
        assert retrieved is not None
        assert retrieved.id == "tdd.test.complete"
    
    def test_get_template_base_fallback(self):
        """Test template lookup falls back to base."""
        registry = ResponseTemplateRegistry.get_instance()
        template = TemplateDefinition(
            id="base.status.success",
            name="Success",
            description="Success",
            template="Success",
            variables=[],
            severity="INFO",
            category="status"
        )
        registry.add_base_template(template)
        
        # Get from unknown domain falls back to base
        retrieved = registry.get_template("unknown_domain", "Success")
        assert retrieved is not None
        assert retrieved.id == "base.status.success"
    
    def test_get_template_by_id_o1(self):
        """Test O(1) template lookup by ID."""
        registry = ResponseTemplateRegistry.get_instance()
        template = TemplateDefinition(
            id="tdd.test.coverage",
            name="Coverage",
            description="Coverage",
            template="Coverage report",
            variables=[],
            severity="INFO",
            category="coverage"
        )
        registry.add_domain_template("tdd", template)
        
        retrieved = registry.get_template_by_id("tdd.test.coverage")
        assert retrieved is not None
        assert retrieved.id == "tdd.test.coverage"
    
    def test_get_templates_by_category(self):
        """Test getting templates by category."""
        registry = ResponseTemplateRegistry.get_instance()
        
        template1 = TemplateDefinition(
            id="base.status.success",
            name="Success",
            description="Success",
            template="",
            variables=[],
            severity="INFO",
            category="status"
        )
        template2 = TemplateDefinition(
            id="base.status.error",
            name="Error",
            description="Error",
            template="",
            variables=[],
            severity="ERROR",
            category="status"
        )
        
        registry.add_base_template(template1)
        registry.add_base_template(template2)
        
        status_templates = registry.get_templates_by_category("status")
        assert len(status_templates) == 2
    
    def test_get_templates_for_domain(self):
        """Test getting all templates for a domain."""
        registry = ResponseTemplateRegistry.get_instance()
        
        template1 = TemplateDefinition(
            id="tdd.test.success",
            name="Test Success",
            description="",
            template="",
            variables=[],
            severity="INFO",
            category="test"
        )
        template2 = TemplateDefinition(
            id="tdd.coverage.report",
            name="Coverage Report",
            description="",
            template="",
            variables=[],
            severity="INFO",
            category="coverage"
        )
        
        registry.add_domain_template("tdd", template1)
        registry.add_domain_template("tdd", template2)
        
        tdd_templates = registry.get_templates_for_domain("tdd")
        assert len(tdd_templates) == 2
    
    def test_get_statistics(self):
        """Test registry statistics."""
        registry = ResponseTemplateRegistry.get_instance()
        
        base_template = TemplateDefinition(
            id="base.status.success",
            name="Success",
            description="",
            template="",
            variables=[],
            severity="INFO",
            category="status"
        )
        registry.add_base_template(base_template)
        
        domain_template = TemplateDefinition(
            id="tdd.test.success",
            name="Test Success",
            description="",
            template="",
            variables=[],
            severity="INFO",
            category="test"
        )
        registry.add_domain_template("tdd", domain_template)
        
        stats = registry.get_statistics()
        assert stats["base_templates_count"] == 1
        assert stats["domain_templates_count"] == 1
        assert stats["total_templates"] == 2
        assert "tdd" in stats["domains"]


# =============================================================================
# TEST: ResponseTemplateLoader
# =============================================================================

class TestResponseTemplateLoader:
    """Test ResponseTemplateLoader YAML parsing."""
    
    def test_load_from_file_not_found(self):
        """Test error when YAML file not found."""
        with pytest.raises(FileNotFoundError):
            ResponseTemplateLoader.load_from_file("/nonexistent/path.yaml")
    
    def test_load_base_templates(self):
        """Test loading base templates."""
        yaml_content = {
            'base_templates': {
                'status_success': {
                    'id': 'base.status.success',
                    'name': 'Success',
                    'description': 'Success message',
                    'template': 'Success: {message}',
                    'variables': [
                        {'name': 'message', 'type': 'string', 'required': True}
                    ],
                    'severity': 'INFO',
                    'category': 'status'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            f.flush()
            
            base_templates, _ = ResponseTemplateLoader.load_from_file(f.name)
            
            assert len(base_templates) == 1
            assert 'base.status.success' in base_templates
            assert base_templates['base.status.success'].name == 'Success'
    
    def test_load_domain_templates(self):
        """Test loading domain templates."""
        yaml_content = {
            'domain_templates': {
                'tdd': {
                    'description': 'TDD templates',
                    'templates': {
                        'test_success': {
                            'id': 'tdd.test.success',
                            'name': 'Test Success',
                            'description': 'Test passed',
                            'template': 'All tests passed',
                            'variables': [],
                            'severity': 'INFO',
                            'category': 'test'
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            f.flush()
            
            _, domain_templates = ResponseTemplateLoader.load_from_file(f.name)
            
            assert 'tdd' in domain_templates
            assert 'tdd.test.success' in domain_templates['tdd']
    
    def test_load_templates_with_inheritance(self):
        """Test loading templates with inheritance."""
        yaml_content = {
            'base_templates': {
                'status_success': {
                    'id': 'base.status.success',
                    'name': 'Success',
                    'template': 'Success',
                    'variables': [],
                    'severity': 'INFO',
                    'category': 'status'
                }
            },
            'domain_templates': {
                'tdd': {
                    'description': 'TDD',
                    'templates': {
                        'test_success': {
                            'id': 'tdd.test.success',
                            'name': 'Test Success',
                            'template': 'Test Success',
                            'variables': [],
                            'severity': 'INFO',
                            'category': 'test',
                            'inherits_from': 'base.status.success'
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            f.flush()
            
            base_templates, domain_templates = ResponseTemplateLoader.load_from_file(f.name)
            
            tdd_template = domain_templates['tdd']['tdd.test.success']
            assert tdd_template.inherits_from == 'base.status.success'


# =============================================================================
# TEST: ResponseTemplateEngine
# =============================================================================

class TestResponseTemplateEngine:
    """Test ResponseTemplateEngine rendering."""
    
    def setup_method(self):
        """Setup test registry."""
        self.registry = ResponseTemplateRegistry.get_instance()
        self.registry.clear()
    
    def test_render_simple_template(self):
        """Test rendering template with variables."""
        template = TemplateDefinition(
            id="test.message",
            name="Message",
            description="Simple message",
            template="Hello, {name}! You are {age} years old.",
            variables=[
                TemplateVariable("name", "string", required=True),
                TemplateVariable("age", "integer", required=True),
            ],
            severity="INFO",
            category="test"
        )
        self.registry.add_base_template(template)
        
        engine = ResponseTemplateEngine(self.registry)
        context = {"name": "Alice", "age": 30}
        rendered = engine.render("test", "Message", context)
        
        assert rendered == "Hello, Alice! You are 30 years old."
    
    def test_render_with_optional_variables(self):
        """Test rendering with optional variables."""
        template = TemplateDefinition(
            id="test.optional",
            name="Optional",
            description="Has optional vars",
            template="Name: {name}, Comment: {comment}",
            variables=[
                TemplateVariable("name", "string", required=True),
                TemplateVariable("comment", "string", required=False),
            ],
            severity="INFO",
            category="test"
        )
        self.registry.add_base_template(template)
        
        engine = ResponseTemplateEngine(self.registry)
        context = {"name": "Bob"}
        rendered = engine.render("test", "Optional", context)
        
        assert rendered == "Name: Bob, Comment: "
    
    def test_render_fails_without_required_variable(self):
        """Test render fails if required variable missing."""
        template = TemplateDefinition(
            id="test.required",
            name="Required",
            description="Requires variables",
            template="{required_var}",
            variables=[
                TemplateVariable("required_var", "string", required=True),
            ],
            severity="INFO",
            category="test"
        )
        self.registry.add_base_template(template)
        
        engine = ResponseTemplateEngine(self.registry)
        with pytest.raises(ValueError, match="validation failed"):
            engine.render("test", "Required", {})
    
    def test_render_by_id(self):
        """Test rendering by template ID."""
        template = TemplateDefinition(
            id="tdd.test.report",
            name="Test Report",
            description="Report",
            template="Passed: {passed_count}",
            variables=[
                TemplateVariable("passed_count", "integer", required=True),
            ],
            severity="INFO",
            category="test"
        )
        self.registry.add_domain_template("tdd", template)
        
        engine = ResponseTemplateEngine(self.registry)
        context = {"passed_count": 155}
        rendered = engine.render_by_id("tdd.test.report", context)
        
        assert rendered == "Passed: 155"
    
    def test_render_inherits_parent_variables(self):
        """Test rendering resolves inherited variables."""
        parent = TemplateDefinition(
            id="base.status.report",
            name="Status Report",
            description="Base report",
            template="Status: {status}",
            variables=[
                TemplateVariable("status", "string", required=True),
            ],
            severity="INFO",
            category="status"
        )
        
        child = TemplateDefinition(
            id="tdd.test.report",
            name="Test Report",
            description="Test-specific",
            template="Tests: {passed}/{total} (Status: {status})",
            variables=[
                TemplateVariable("passed", "integer", required=True),
                TemplateVariable("total", "integer", required=True),
            ],
            severity="INFO",
            category="test",
            inherits_from="base.status.report"
        )
        
        self.registry.add_base_template(parent)
        self.registry.add_domain_template("tdd", child)
        
        engine = ResponseTemplateEngine(self.registry)
        context = {"passed": 150, "total": 155, "status": "PASS"}
        rendered = engine.render("tdd", "Test Report", context)
        
        assert "Tests: 150/155" in rendered
        assert "Status: PASS" in rendered


# =============================================================================
# TEST: ResponseTemplatePopulator
# =============================================================================

class TestResponseTemplatePopulator:
    """Test ResponseTemplatePopulator high-level interface."""
    
    def teardown_method(self):
        """Clear registry."""
        registry = ResponseTemplateRegistry.get_instance()
        registry.clear()
    
    def test_populate_from_file(self):
        """Test populating from YAML file."""
        yaml_content = {
            'base_templates': {
                'success': {
                    'id': 'base.status.success',
                    'name': 'Success',
                    'template': 'Success: {message}',
                    'variables': [{'name': 'message', 'type': 'string', 'required': True}],
                    'severity': 'INFO',
                    'category': 'status'
                }
            },
            'domain_templates': {
                'tdd': {
                    'description': 'TDD',
                    'templates': {
                        'test_success': {
                            'id': 'tdd.test.success',
                            'name': 'Test Success',
                            'template': 'Tests passed: {count}',
                            'variables': [{'name': 'count', 'type': 'integer', 'required': True}],
                            'severity': 'INFO',
                            'category': 'test'
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            f.flush()
            
            engine = ResponseTemplatePopulator.populate_from_file(f.name)
            
            # Test base template
            rendered = engine.render("unknown", "Success", {"message": "All OK"})
            assert rendered == "Success: All OK"
            
            # Test domain template
            rendered = engine.render("tdd", "Test Success", {"count": 155})
            assert rendered == "Tests passed: 155"


# =============================================================================
# TEST: Integration Tests
# =============================================================================

class TestResponseTemplateIntegration:
    """Integration tests with full template system."""
    
    def test_full_workflow_load_render(self):
        """Test full workflow: load YAML → render templates."""
        yaml_content = {
            'base_templates': {
                'status_success': {
                    'id': 'base.status.success',
                    'name': 'Success',
                    'template': '✅ {title}\n{summary}',
                    'variables': [
                        {'name': 'title', 'type': 'string', 'required': True},
                        {'name': 'summary', 'type': 'string', 'required': True},
                    ],
                    'severity': 'INFO',
                    'category': 'status'
                }
            },
            'domain_templates': {
                'tdd': {
                    'description': 'TDD',
                    'templates': {
                        'test_complete': {
                            'id': 'tdd.test.complete',
                            'name': 'Test Complete',
                            'template': '✅ Test Execution Complete\n{passed}/{total} tests passed',
                            'variables': [
                                {'name': 'passed', 'type': 'integer', 'required': True},
                                {'name': 'total', 'type': 'integer', 'required': True},
                            ],
                            'severity': 'INFO',
                            'category': 'test'
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            f.flush()
            
            # Populate
            engine = ResponseTemplatePopulator.populate_from_file(f.name)
            
            # Render TDD template
            context = {"passed": 155, "total": 155}
            rendered = engine.render("tdd", "Test Complete", context)
            assert "155/155 tests passed" in rendered
            
            # Fallback to base for unknown domain
            context = {"title": "Operation Complete", "summary": "All checks passed"}
            rendered = engine.render("unknown_domain", "Success", context)
            assert "✅ Operation Complete" in rendered
    
    def test_multiple_domains_with_shared_base_templates(self):
        """Test multiple domains sharing base templates."""
        registry = ResponseTemplateRegistry.get_instance()
        registry.clear()
        
        # Base template used by multiple domains
        base_summary = TemplateDefinition(
            id="base.summary",
            name="Summary",
            template="Summary: {summary}",
            variables=[TemplateVariable("summary", "string", required=True)],
            description="Base summary",
            severity="INFO",
            category="summary"
        )
        registry.add_base_template(base_summary)
        
        # TDD domain template
        tdd_template = TemplateDefinition(
            id="tdd.summary",
            name="Summary",
            template="TDD Summary: {summary}",
            variables=[TemplateVariable("summary", "string", required=True)],
            description="TDD summary",
            severity="INFO",
            category="summary"
        )
        registry.add_domain_template("tdd", tdd_template)
        
        # Planning domain template
        planning_template = TemplateDefinition(
            id="planning.summary",
            name="Summary",
            template="Planning Summary: {summary}",
            variables=[TemplateVariable("summary", "string", required=True)],
            description="Planning summary",
            severity="INFO",
            category="summary"
        )
        registry.add_domain_template("planning", planning_template)
        
        engine = ResponseTemplateEngine(registry)
        
        # Each domain uses its own template
        rendered_tdd = engine.render("tdd", "Summary", {"summary": "Tests pass"})
        assert rendered_tdd == "TDD Summary: Tests pass"
        
        rendered_planning = engine.render("planning", "Summary", {"summary": "On track"})
        assert rendered_planning == "Planning Summary: On track"
        
        # Unknown domain falls back to base
        rendered_base = engine.render("unknown", "Summary", {"summary": "Done"})
        assert rendered_base == "Summary: Done"


# =============================================================================
# TEST: Real YAML File Loading
# =============================================================================

class TestRealYAMLLoading:
    """Test loading actual response-templates.yaml file."""
    
    def test_load_actual_yaml_file(self):
        """Test loading the actual response-templates.yaml file."""
        from src.core.path_resolver import resolve_path
        yaml_path = resolve_path("cortex-brain", "tier2", "response-templates", "response-templates.yaml")
        
        if not yaml_path.exists():
            pytest.skip("response-templates.yaml not found in expected location")
        
        # Load templates
        engine = ResponseTemplatePopulator.populate_from_file(str(yaml_path))
        
        # Verify registry is populated
        registry = ResponseTemplateRegistry.get_instance()
        stats = registry.get_statistics()
        
        assert stats["base_templates_count"] > 0
        assert stats["domain_templates_count"] > 0
        assert "tdd" in stats["domains"]
        assert "planning" in stats["domains"]
        assert "ado" in stats["domains"]
        assert "interaction" in stats["domains"]
    
    def test_load_and_render_tdd_templates(self):
        """Test loading and rendering TDD templates."""
        from src.core.path_resolver import resolve_path
        yaml_path = resolve_path("cortex-brain", "tier2", "response-templates", "response-templates.yaml")
        
        if not yaml_path.exists():
            pytest.skip("response-templates.yaml not found")
        
        engine = ResponseTemplatePopulator.populate_from_file(str(yaml_path))
        
        # Get registry to find available templates
        registry = ResponseTemplateRegistry.get_instance()
        tdd_templates = registry.get_templates_for_domain("tdd")
        
        # If no templates found, skip
        if not tdd_templates:
            pytest.skip("No TDD templates found in YAML")
        
        # Use first available template
        template = tdd_templates[0]
        context = {
            var.name: "test_value" if var.var_type == "string" else 
                     42 if var.var_type == "integer" else
                     3.14 if var.var_type == "number" else
                     True
            for var in template.variables
        }
        
        rendered = engine.render_by_id(template.id, context)
        assert rendered is not None
        assert len(rendered) > 0
    
    def test_load_and_render_planning_templates(self):
        """Test loading and rendering Planning templates."""
        from src.core.path_resolver import resolve_path
        yaml_path = resolve_path("cortex-brain", "tier2", "response-templates", "response-templates.yaml")
        
        if not yaml_path.exists():
            pytest.skip("response-templates.yaml not found")
        
        engine = ResponseTemplatePopulator.populate_from_file(str(yaml_path))
        
        # Get registry to find available templates
        registry = ResponseTemplateRegistry.get_instance()
        planning_templates = registry.get_templates_for_domain("planning")
        
        # If no templates found, skip
        if not planning_templates:
            pytest.skip("No Planning templates found in YAML")
        
        # Use first available template
        template = planning_templates[0]
        context = {
            var.name: "test_value" if var.var_type == "string" else 
                     42 if var.var_type == "integer" else
                     3.14 if var.var_type == "number" else
                     True
            for var in template.variables
        }
        
        rendered = engine.render_by_id(template.id, context)
        assert rendered is not None
        assert len(rendered) > 0
