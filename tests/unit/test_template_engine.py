"""
Tests for Custom Response Templates System

AC-AR-009-01: Response templates loaded from cortex-brain/tier2/
AC-AR-009-02: Templates support variable substitution
AC-AR-009-03: Template inheritance working
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from src.core.template_engine import TemplateEngine, TemplateRegistry, TemplateInfo


class TestTemplateRegistry:
    """Test template registry functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        TemplateRegistry.reset_instance()
    
    def test_registry_singleton(self):
        """Test registry singleton pattern"""
        reg1 = TemplateRegistry.instance()
        reg2 = TemplateRegistry.instance()
        
        assert reg1 is reg2
    
    def test_register_template(self):
        """Test registering a template"""
        registry = TemplateRegistry.instance()
        
        template = TemplateInfo(
            name="test_template",
            domain="governance",
            version="1.0",
            variables=["rule_id", "status"],
            content="Rule {{rule_id}} status: {{status}}"
        )
        
        result = registry.register_template(template)
        
        assert result.is_ok()
        assert registry.get_template("test_template") is not None
    
    def test_get_template(self):
        """Test retrieving a template"""
        registry = TemplateRegistry.instance()
        
        template = TemplateInfo(
            name="test_template",
            domain="governance",
            version="1.0",
            variables=["name"],
            content="Hello {{name}}"
        )
        
        registry.register_template(template)
        retrieved = registry.get_template("test_template")
        
        assert retrieved is not None
        assert retrieved.name == "test_template"
        assert retrieved.domain == "governance"
    
    def test_get_nonexistent_template(self):
        """Test retrieving nonexistent template"""
        registry = TemplateRegistry.instance()
        
        template = registry.get_template("nonexistent")
        
        assert template is None
    
    def test_list_templates(self):
        """Test listing all templates"""
        registry = TemplateRegistry.instance()
        
        # Register multiple templates
        for i in range(3):
            template = TemplateInfo(
                name=f"template_{i}",
                domain="governance",
                version="1.0",
                variables=[],
                content=""
            )
            registry.register_template(template)
        
        templates = registry.list_templates()
        
        assert len(templates) == 3
    
    def test_list_templates_by_domain(self):
        """Test listing templates by domain"""
        registry = TemplateRegistry.instance()
        
        # Register templates in different domains
        governance_template = TemplateInfo(
            name="gov_template",
            domain="governance",
            version="1.0",
            variables=[],
            content=""
        )
        audit_template = TemplateInfo(
            name="audit_template",
            domain="audit",
            version="1.0",
            variables=[],
            content=""
        )
        
        registry.register_template(governance_template)
        registry.register_template(audit_template)
        
        gov_templates = registry.list_templates("governance")
        
        assert len(gov_templates) == 1
        assert gov_templates[0].name == "gov_template"


@pytest.mark.ac("AR-009-01")
class TestTemplateLoading:
    """Test AC-AR-009-01: Template loading"""
    
    def setup_method(self):
        """Setup for each test"""
        TemplateRegistry.reset_instance()
    
    def test_load_templates_creates_directory(self):
        """Test that load_templates creates directory if missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = os.path.join(temp_dir, "templates")
            engine = TemplateEngine(template_dir=template_dir)
            
            result = engine.load_templates()
            
            assert result.is_ok()
            assert os.path.exists(template_dir)
    
    def test_load_json_templates(self):
        """Test loading JSON templates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test JSON template
            template_data = {
                "name": "test_template",
                "domain": "governance",
                "version": "1.0",
                "content": "Rule {{rule_id}} is {{status}}"
            }
            
            template_file = os.path.join(temp_dir, "test_template.json")
            with open(template_file, 'w') as f:
                json.dump(template_data, f)
            
            engine = TemplateEngine(template_dir=temp_dir)
            result = engine.load_templates()
            
            assert result.is_ok()
            loaded_count = result.unwrap()
            assert loaded_count == 1
    
    def test_load_templates_from_tier2(self):
        """Test loading templates from default cortex-brain location"""
        engine = TemplateEngine()
        
        result = engine.load_templates()
        
        # Should succeed even if no templates exist yet
        assert result.is_ok()


@pytest.mark.ac("AR-009-02")
class TestTemplateSubstitution:
    """Test AC-AR-009-02: Variable substitution"""
    
    def setup_method(self):
        """Setup for each test"""
        TemplateRegistry.reset_instance()
    
    def test_simple_substitution(self):
        """Test simple variable substitution"""
        registry = TemplateRegistry.instance()
        
        template = TemplateInfo(
            name="greeting",
            domain="general",
            version="1.0",
            variables=["name"],
            content="Hello {{name}}, welcome to CORTEX!"
        )
        registry.register_template(template)
        
        engine = TemplateEngine()
        result = engine.render("greeting", {"name": "Alice"})
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert "Hello Alice" in rendered
        assert "{{name}}" not in rendered
    
    def test_multiple_substitutions(self):
        """Test multiple variable substitutions"""
        registry = TemplateRegistry.instance()
        
        template = TemplateInfo(
            name="rule_status",
            domain="governance",
            version="1.0",
            variables=["rule_id", "status", "severity"],
            content="Rule {{rule_id}} is {{status}} ({{severity}})"
        )
        registry.register_template(template)
        
        engine = TemplateEngine()
        result = engine.render("rule_status", {
            "rule_id": "SKULL-001",
            "status": "ACTIVE",
            "severity": "HIGH"
        })
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert "SKULL-001" in rendered
        assert "ACTIVE" in rendered
        assert "HIGH" in rendered
    
    def test_missing_variable_error(self):
        """Test error when variable is missing"""
        registry = TemplateRegistry.instance()
        
        template = TemplateInfo(
            name="test",
            domain="general",
            version="1.0",
            variables=["name", "age"],
            content="{{name}} is {{age}} years old"
        )
        registry.register_template(template)
        
        engine = TemplateEngine()
        result = engine.render("test", {"name": "Bob"})  # Missing 'age'
        
        assert result.is_err()
    
    def test_nonexistent_template_error(self):
        """Test error when template doesn't exist"""
        engine = TemplateEngine()
        result = engine.render("nonexistent", {})
        
        assert result.is_err()
    
    def test_numeric_variable_conversion(self):
        """Test that numeric variables are converted to strings"""
        registry = TemplateRegistry.instance()
        
        template = TemplateInfo(
            name="count",
            domain="general",
            version="1.0",
            variables=["count"],
            content="Total: {{count}}"
        )
        registry.register_template(template)
        
        engine = TemplateEngine()
        result = engine.render("count", {"count": 42})
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert "Total: 42" in rendered


@pytest.mark.ac("AR-009-03")
class TestTemplateInheritance:
    """Test AC-AR-009-03: Template inheritance"""
    
    def setup_method(self):
        """Setup for each test"""
        TemplateRegistry.reset_instance()
    
    def test_simple_inheritance(self):
        """Test simple template inheritance"""
        registry = TemplateRegistry.instance()
        
        # Parent template with {{body}} placeholder
        parent = TemplateInfo(
            name="base_layout",
            domain="general",
            version="1.0",
            variables=[],
            content="<response>\n{{body}}\n</response>"
        )
        
        # Child template that extends parent
        child = TemplateInfo(
            name="governance_response",
            domain="governance",
            version="1.0",
            variables=["rule_id"],
            content="<rule>{{rule_id}}</rule>",
            parent_template="base_layout"
        )
        
        registry.register_template(parent)
        registry.register_template(child)
        
        engine = TemplateEngine()
        result = engine.render("governance_response", {"rule_id": "SKULL-001"})
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert "<response>" in rendered
        assert "SKULL-001" in rendered
        assert "</response>" in rendered
    
    def test_multi_level_inheritance(self):
        """Test multiple levels of template inheritance"""
        registry = TemplateRegistry.instance()
        
        # Level 1: Base layout
        base = TemplateInfo(
            name="base",
            domain="general",
            version="1.0",
            variables=[],
            content="<root>{{body}}</root>"
        )
        
        # Level 2: Intermediate
        intermediate = TemplateInfo(
            name="intermediate",
            domain="general",
            version="1.0",
            variables=[],
            content="<section>{{body}}</section>",
            parent_template="base"
        )
        
        # Level 3: Final
        final = TemplateInfo(
            name="final",
            domain="general",
            version="1.0",
            variables=["content"],
            content="<item>{{content}}</item>",
            parent_template="intermediate"
        )
        
        registry.register_template(base)
        registry.register_template(intermediate)
        registry.register_template(final)
        
        engine = TemplateEngine()
        result = engine.render("final", {"content": "Hello"})
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert "<root>" in rendered
        assert "<section>" in rendered
        assert "Hello" in rendered
        assert "</section>" in rendered
        assert "</root>" in rendered
    
    def test_inherited_template_with_variables(self):
        """Test that child template variables work with inheritance"""
        registry = TemplateRegistry.instance()
        
        parent = TemplateInfo(
            name="wrapper",
            domain="general",
            version="1.0",
            variables=[],
            content='<wrapper type="{{type}}">{{body}}</wrapper>'
        )
        
        child = TemplateInfo(
            name="content",
            domain="general",
            version="1.0",
            variables=["type", "message"],
            content="<message>{{message}}</message>",
            parent_template="wrapper"
        )
        
        registry.register_template(parent)
        registry.register_template(child)
        
        engine = TemplateEngine()
        result = engine.render("content", {
            "type": "info",
            "message": "Processing"
        })
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert 'type="info"' in rendered
        assert "Processing" in rendered
    
    def test_inheritance_chain_with_multiple_bodies(self):
        """Test that inheritance correctly replaces body placeholder"""
        registry = TemplateRegistry.instance()
        
        parent = TemplateInfo(
            name="parent",
            domain="general",
            version="1.0",
            variables=[],
            content="<parent>{{body}}</parent>"
        )
        
        child = TemplateInfo(
            name="child",
            domain="general",
            version="1.0",
            variables=["value"],
            content="<child>{{value}}</child>",
            parent_template="parent"
        )
        
        registry.register_template(parent)
        registry.register_template(child)
        
        engine = TemplateEngine()
        result = engine.render("child", {"value": "TEST"})
        
        assert result.is_ok()
        rendered = result.unwrap()
        # Should only have one set of parent tags
        assert rendered.count("<parent>") == 1
        assert rendered.count("</parent>") == 1


class TestTemplateInfo:
    """Test TemplateInfo dataclass"""
    
    def test_template_info_creation(self):
        """Test creating template info"""
        template = TemplateInfo(
            name="test",
            domain="governance",
            version="1.0",
            variables=["var1", "var2"],
            content="Content with {{var1}} and {{var2}}"
        )
        
        assert template.name == "test"
        assert template.domain == "governance"
        assert len(template.variables) == 2
        assert template.parent_template is None
    
    def test_template_info_with_parent(self):
        """Test template info with parent reference"""
        template = TemplateInfo(
            name="child",
            domain="governance",
            version="1.0",
            variables=["id"],
            content="{{id}}",
            parent_template="parent"
        )
        
        assert template.parent_template == "parent"


class TestTemplateIntegration:
    """Integration tests for template system"""
    
    def setup_method(self):
        """Setup for each test"""
        TemplateRegistry.reset_instance()
    
    def test_complete_template_workflow(self):
        """Test complete workflow: register, load, render"""
        registry = TemplateRegistry.instance()
        
        # Register templates
        base = TemplateInfo(
            name="base",
            domain="governance",
            version="1.0",
            variables=[],
            content="[RESPONSE]\n{{body}}\n[/RESPONSE]"
        )
        
        rule_template = TemplateInfo(
            name="rule_violation",
            domain="governance",
            version="1.0",
            variables=["rule_id", "message"],
            content="VIOLATION: {{rule_id}} - {{message}}",
            parent_template="base"
        )
        
        registry.register_template(base)
        registry.register_template(rule_template)
        
        # Render template
        engine = TemplateEngine()
        result = engine.render("rule_violation", {
            "rule_id": "SKULL-001",
            "message": "Governance policy violated"
        })
        
        assert result.is_ok()
        rendered = result.unwrap()
        assert "[RESPONSE]" in rendered
        assert "SKULL-001" in rendered
        assert "Governance policy violated" in rendered
        assert "[/RESPONSE]" in rendered
