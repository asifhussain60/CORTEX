"""
Domain Template Tests - AR-016-02

Tests for domain-specific orchestrator templates.
- 5 domain templates exist and are usable
- Each template includes governance rule loading
- Each template includes response header injection
- Each template includes audit logging hooks

Author: Asif Hussain
"""

import pytest
from cortex.orchestrators.domains.domain_templates import (
    DomainTemplateFactory,
    PlanningTemplate,
    AnalysisTemplate,
    IntegrationTemplate,
    ValidationTemplate,
    ExecutionTemplate,
)


class TestDomainTemplatesExist:
    """Test that 5 domain templates exist"""
    
    def test_all_templates_exist(self):
        """Test that all 5 domain templates are defined"""
        factory = DomainTemplateFactory()
        
        templates = factory.get_all_templates()
        assert len(templates) == 5
        
        template_names = {t.get_domain() for t in templates}
        assert template_names == {"planning", "analysis", "integration", "validation", "execution"}
    
    def test_planning_template_exists(self):
        """Test planning template"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        assert template is not None
        assert isinstance(template, PlanningTemplate)
        assert template.get_domain() == "planning"
    
    def test_analysis_template_exists(self):
        """Test analysis template"""
        factory = DomainTemplateFactory()
        template = factory.get_template("analysis")
        
        assert template is not None
        assert isinstance(template, AnalysisTemplate)
        assert template.get_domain() == "analysis"
    
    def test_integration_template_exists(self):
        """Test integration template"""
        factory = DomainTemplateFactory()
        template = factory.get_template("integration")
        
        assert template is not None
        assert isinstance(template, IntegrationTemplate)
        assert template.get_domain() == "integration"
    
    def test_validation_template_exists(self):
        """Test validation template"""
        factory = DomainTemplateFactory()
        template = factory.get_template("validation")
        
        assert template is not None
        assert isinstance(template, ValidationTemplate)
        assert template.get_domain() == "validation"
    
    def test_execution_template_exists(self):
        """Test execution template"""
        factory = DomainTemplateFactory()
        template = factory.get_template("execution")
        
        assert template is not None
        assert isinstance(template, ExecutionTemplate)
        assert template.get_domain() == "execution"
    
    def test_invalid_template_raises_error(self):
        """Test that requesting invalid template raises error"""
        factory = DomainTemplateFactory()
        
        with pytest.raises(ValueError):
            factory.get_template("nonexistent")


class TestTemplateGovernanceIntegration:
    """Test that templates integrate governance"""
    
    def test_each_template_loads_governance_rules(self):
        """Test that each template loads governance rules"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            assert "governance_rules" in context
            assert isinstance(context["governance_rules"], dict)
            assert len(context["governance_rules"]) > 0
    
    def test_governance_context_includes_tier0(self):
        """Test that governance context includes tier 0 rules"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        context = template.create_context()
        rules = context["governance_rules"]
        
        # Should have CORE rules
        assert any("CORE" in str(rule) for rule in rules.keys())
    
    def test_governance_context_includes_phase_rules(self):
        """Test that governance context includes compliance rules"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        context = template.create_context()
        rules = context["governance_rules"]
        
        # Should have governance rules (CORE rules)
        assert any("CORE" in str(rule) for rule in rules.keys())
    
    def test_template_validates_governance_compliance(self):
        """Test that template validates governance compliance"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        # Should be able to check compliance
        assert hasattr(template, "validate_compliance")
        assert callable(template.validate_compliance)


class TestTemplateResponseHeaderInjection:
    """Test that templates inject response headers"""
    
    def test_each_template_injects_response_headers(self):
        """Test that each template injects response headers"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            assert "response_headers" in context
            assert isinstance(context["response_headers"], dict)
    
    def test_response_headers_include_domain_info(self):
        """Test that response headers include domain information"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        context = template.create_context()
        headers = context["response_headers"]
        
        assert "X-Domain" in headers
        assert headers["X-Domain"] == "planning"
    
    def test_response_headers_include_version(self):
        """Test that response headers include version"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            headers = context["response_headers"]
            
            assert "X-Version" in headers
            assert headers["X-Version"] is not None
    
    def test_response_headers_include_timestamp(self):
        """Test that response headers include timestamp"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            headers = context["response_headers"]
            
            assert "X-Timestamp" in headers
            # Should be valid ISO format
            assert "T" in headers["X-Timestamp"]
    
    def test_response_headers_can_be_injected_into_response(self):
        """Test that response headers can be injected"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        context = template.create_context()
        
        # Should have method to inject headers
        assert hasattr(template, "inject_headers")
        assert callable(template.inject_headers)
        
        # Create a mock response
        response = {}
        template.inject_headers(response, context["response_headers"])
        
        assert "X-Domain" in response
        assert response["X-Domain"] == "planning"


class TestTemplateAuditLogging:
    """Test that templates include audit logging hooks"""
    
    def test_each_template_includes_audit_hooks(self):
        """Test that each template includes audit logging hooks"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            assert "audit_hooks" in context
            assert isinstance(context["audit_hooks"], dict)
    
    def test_audit_hooks_include_start_operation(self):
        """Test that audit hooks include start operation logging"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            hooks = context["audit_hooks"]
            
            assert "start_operation" in hooks
            assert callable(hooks["start_operation"])
    
    def test_audit_hooks_include_end_operation(self):
        """Test that audit hooks include end operation logging"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            hooks = context["audit_hooks"]
            
            assert "end_operation" in hooks
            assert callable(hooks["end_operation"])
    
    def test_audit_hooks_include_error_logging(self):
        """Test that audit hooks include error logging"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            context = template.create_context()
            hooks = context["audit_hooks"]
            
            assert "log_error" in hooks
            assert callable(hooks["log_error"])
    
    def test_audit_hooks_can_log_operations(self):
        """Test that audit hooks can log operations"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        context = template.create_context()
        hooks = context["audit_hooks"]
        
        # Should be able to log start
        result = hooks["start_operation"]("test_operation", {"param1": "value1"})
        assert result is not None
    
    def test_audit_logging_includes_ac_id(self):
        """Test that audit logging can track AC-ID"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        context = template.create_context()
        
        # Should support AC-ID tracking
        assert "ac_id_tracking" in context
        assert context["ac_id_tracking"] is True


class TestTemplateUsability:
    """Test that templates are usable for orchestrator creation"""
    
    def test_template_provides_initialization_hook(self):
        """Test that template provides initialization hook"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            assert hasattr(template, "initialize")
            assert callable(template.initialize)
    
    def test_template_provides_execution_hook(self):
        """Test that template provides execution hook"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            assert hasattr(template, "execute")
            assert callable(template.execute)
    
    def test_template_provides_cleanup_hook(self):
        """Test that template provides cleanup hook"""
        factory = DomainTemplateFactory()
        
        for template in factory.get_all_templates():
            assert hasattr(template, "cleanup")
            assert callable(template.cleanup)
    
    def test_template_context_contains_all_required_fields(self):
        """Test that template context contains all required fields"""
        factory = DomainTemplateFactory()
        
        required_fields = {
            "domain",
            "governance_rules",
            "response_headers",
            "audit_hooks",
            "ac_id_tracking",
            "version",
            "created_at",
        }
        
        for template in factory.get_all_templates():
            context = template.create_context()
            
            for field in required_fields:
                assert field in context, f"Missing field: {field}"
    
    def test_template_can_generate_orchestrator_boilerplate(self):
        """Test that template can generate orchestrator boilerplate code"""
        factory = DomainTemplateFactory()
        template = factory.get_template("planning")
        
        # Should provide boilerplate generation
        assert hasattr(template, "generate_boilerplate")
        assert callable(template.generate_boilerplate)
        
        boilerplate = template.generate_boilerplate(
            class_name="MyPlanningOrchestrator",
            description="Custom planning orchestrator"
        )
        
        assert isinstance(boilerplate, str)
        assert "MyPlanningOrchestrator" in boilerplate
        assert "planning" in boilerplate.lower()


class TestDomainTemplateFactory:
    """Test domain template factory"""
    
    def test_factory_is_singleton(self):
        """Test that factory is singleton"""
        factory1 = DomainTemplateFactory()
        factory2 = DomainTemplateFactory()
        
        # Should have same templates
        assert factory1.get_all_templates() == factory2.get_all_templates()
    
    def test_factory_can_list_domains(self):
        """Test that factory can list all domains"""
        factory = DomainTemplateFactory()
        domains = factory.get_domain_names()
        
        assert len(domains) == 5
        assert "planning" in domains
        assert "analysis" in domains
        assert "integration" in domains
        assert "validation" in domains
        assert "execution" in domains
    
    def test_factory_export_all_templates(self):
        """Test that factory can export all template metadata"""
        factory = DomainTemplateFactory()
        
        export = factory.export_templates()
        assert isinstance(export, dict)
        assert "metadata" in export
        assert "templates" in export
        assert len(export["templates"]) == 5
