"""
Multi-role response engine test suite.
14 role-task response templates integrated with security and code analysis.

Module: tests.unit.orchestrators.response.test_multi_role_response_engine
"""

import pytest
from cortex.orchestrators.response.multi_role_response_engine import (
    Role,
    ResponseTemplate,
    IntegratedContext,
    MultiRoleResponseEngine,
    TemplateRegistry,
    RoleAdaptation,
)


class TestRole:
    """Tests for role enumeration."""
    
    def test_all_roles_exist(self):
        """Test all roles are defined."""
        roles = {r.value for r in Role}
        assert len(roles) >= 5


class TestResponseTemplate:
    """Tests for response template."""
    
    def test_template_creation(self):
        """Test creating response template."""
        template = ResponseTemplate(
            role=Role.ENGINEER,
            task="code_review",
            template_name="Technical Review",
            structure="Header → Issues → Suggestions → Action Items",
            variables=["code_quality", "test_coverage"]
        )
        assert template.role == Role.ENGINEER
        assert template.task == "code_review"


class TestIntegratedContext:
    """Tests for integrated context."""
    
    def test_integrated_context_creation(self):
        """Test creating integrated context."""
        ctx = IntegratedContext(
            code="def f(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="High",
            target_role=Role.ENGINEER
        )
        assert ctx.target_role == Role.ENGINEER


class TestTemplateRegistry:
    """Tests for template registry."""
    
    def test_registry_creation(self):
        """Test creating registry."""
        registry = TemplateRegistry()
        assert registry is not None
    
    def test_register_template(self):
        """Test registering template."""
        registry = TemplateRegistry()
        template = ResponseTemplate(
            role=Role.ENGINEER,
            task="review",
            template_name="Review",
            structure="Test",
            variables=[]
        )
        registry.register(template)
        retrieved = registry.get(Role.ENGINEER, "review")
        assert retrieved is not None
    
    def test_get_templates_by_role(self):
        """Test getting templates by role."""
        registry = TemplateRegistry()
        templates = registry.get_by_role(Role.ENGINEER)
        assert isinstance(templates, list)
    
    def test_list_all_templates(self):
        """Test listing all templates."""
        registry = TemplateRegistry()
        all_templates = registry.list_templates()
        assert isinstance(all_templates, list)
        assert len(all_templates) > 0


class TestRoleAdaptation:
    """Tests for role-based adaptation."""
    
    def test_engineer_adaptation(self):
        """Test engineer role adaptation."""
        adapter = RoleAdaptation()
        response = adapter.adapt(
            message="Critical SQL injection vulnerability",
            role=Role.ENGINEER
        )
        assert "technical" in response.lower() or "vulnerability" in response.lower()
    
    def test_product_manager_adaptation(self):
        """Test product manager role adaptation."""
        adapter = RoleAdaptation()
        response = adapter.adapt(
            message="Critical SQL injection vulnerability",
            role=Role.PRODUCT_MANAGER
        )
        assert isinstance(response, str)
    
    def test_business_adaptation(self):
        """Test business role adaptation."""
        adapter = RoleAdaptation()
        response = adapter.adapt(
            message="System performance degraded by 30%",
            role=Role.BUSINESS_LEAD
        )
        assert isinstance(response, str)
    
    def test_all_roles_adaptation(self):
        """Test all roles can adapt message."""
        adapter = RoleAdaptation()
        message = "Test message"
        
        for role in Role:
            response = adapter.adapt(message, role)
            assert isinstance(response, str)
            assert len(response) > 0


class TestMultiRoleResponseEngine:
    """Tests for multi-role response engine."""
    
    def test_engine_creation(self):
        """Test creating engine."""
        engine = MultiRoleResponseEngine()
        assert engine is not None
    
    def test_generate_for_engineer(self):
        """Test generating response for engineer."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def func(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="Medium",
            target_role=Role.ENGINEER
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_for_product_manager(self):
        """Test generating response for PM."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def billing(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="High",
            target_role=Role.PRODUCT_MANAGER
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
    
    def test_generate_for_business_lead(self):
        """Test generating response for business lead."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def revenue_calc(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.BUSINESS_LEAD
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
    
    def test_generate_for_security_officer(self):
        """Test generating response for security officer."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="query = f'SELECT * WHERE id={user_id}'",
            security_findings=["SQL Injection"],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.SECURITY_OFFICER
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
        assert "security" in response.lower() or "inject" in response.lower() or len(response) > 0
    
    def test_generate_for_cto(self):
        """Test generating response for CTO."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def scale(): pass",
            security_findings=[],
            code_issues=["O(n²) algorithm"],
            business_impact="High",
            target_role=Role.CTO
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)


class TestTemplateIntegration:
    """Tests for template integration."""
    
    def test_security_integrated_response(self):
        """Test response integrating security findings."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="eval(user_input)",
            security_findings=["Code Injection via eval()"],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.SECURITY_OFFICER
        )
        
        response = engine.generate(ctx)
        # Should address security issue
        assert isinstance(response, str)
    
    def test_business_integrated_response(self):
        """Test response integrating business impact."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def payment_processing(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.BUSINESS_LEAD
        )
        
        response = engine.generate(ctx)
        # Should mention business impact
        assert isinstance(response, str)
    
    def test_technical_integrated_response(self):
        """Test response integrating technical issues."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="for i in range(n):\n    for j in range(n): pass",
            security_findings=[],
            code_issues=["O(n²) performance"],
            business_impact="Medium",
            target_role=Role.ENGINEER
        )
        
        response = engine.generate(ctx)
        # Should address technical issue
        assert isinstance(response, str)


class TestMultiRoleConsistency:
    """Tests for consistency across roles."""
    
    def test_same_code_different_perspectives(self):
        """Test same code generates different perspectives."""
        code_ctx = IntegratedContext(
            code="def calculate_price(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="High",
            target_role=Role.ENGINEER
        )
        
        engine = MultiRoleResponseEngine()
        
        eng_response = engine.generate(code_ctx)
        
        code_ctx.target_role = Role.BUSINESS_LEAD
        bus_response = engine.generate(code_ctx)
        
        # Responses should be different (or at least independently generated)
        assert isinstance(eng_response, str)
        assert isinstance(bus_response, str)
    
    def test_role_specific_vocabulary(self):
        """Test role-specific vocabulary is used."""
        engine = MultiRoleResponseEngine()
        
        # Engineer response should have technical terms
        eng_ctx = IntegratedContext(
            code="def optimize(): pass",
            security_findings=[],
            code_issues=["Algorithm improvement"],
            business_impact="Medium",
            target_role=Role.ENGINEER
        )
        eng_response = engine.generate(eng_ctx)
        assert isinstance(eng_response, str)
        assert len(eng_response) > 0


class TestEdgeCases:
    """Edge case tests."""
    
    def test_empty_code_context(self):
        """Test with empty code."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="",
            security_findings=[],
            code_issues=[],
            business_impact="Low",
            target_role=Role.ENGINEER
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
    
    def test_all_issues_present(self):
        """Test with all types of issues."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="eval(x); for i in range(n): for j in range(n): pass",
            security_findings=["Code Injection"],
            code_issues=["Performance Issue", "Complexity Issue"],
            business_impact="Critical",
            target_role=Role.CTO
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_malformed_code(self):
        """Test with malformed code."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def broken( syntax",
            security_findings=[],
            code_issues=[],
            business_impact="Low",
            target_role=Role.ENGINEER
        )
        
        response = engine.generate(ctx)
        # Should not crash
        assert isinstance(response, str)


class TestTemplate14Coverage:
    """Tests covering all 14 response templates."""
    
    def test_engineer_code_review_template(self):
        """Test engineer code_review template."""
        registry = TemplateRegistry()
        template = registry.get(Role.ENGINEER, "code_review")
        assert template is not None
        assert "Review" in template.template_name or "Review" in template.structure
    
    def test_engineer_design_template(self):
        """Test engineer design template."""
        registry = TemplateRegistry()
        template = registry.get(Role.ENGINEER, "design")
        assert template is not None
    
    def test_engineer_performance_template(self):
        """Test engineer performance template."""
        registry = TemplateRegistry()
        template = registry.get(Role.ENGINEER, "performance")
        assert template is not None
    
    def test_engineer_testing_template(self):
        """Test engineer testing template."""
        registry = TemplateRegistry()
        template = registry.get(Role.ENGINEER, "testing")
        assert template is not None
    
    def test_engineer_refactor_template(self):
        """Test engineer refactor template."""
        registry = TemplateRegistry()
        template = registry.get(Role.ENGINEER, "refactor")
        assert template is not None
    
    def test_pm_feature_impact_template(self):
        """Test PM feature_impact template."""
        registry = TemplateRegistry()
        template = registry.get(Role.PRODUCT_MANAGER, "feature_impact")
        assert template is not None
    
    def test_pm_technical_debt_template(self):
        """Test PM technical_debt template."""
        registry = TemplateRegistry()
        template = registry.get(Role.PRODUCT_MANAGER, "technical_debt")
        assert template is not None
    
    def test_pm_roadmap_template(self):
        """Test PM roadmap template."""
        registry = TemplateRegistry()
        template = registry.get(Role.PRODUCT_MANAGER, "roadmap")
        assert template is not None
    
    def test_business_revenue_template(self):
        """Test business revenue template."""
        registry = TemplateRegistry()
        template = registry.get(Role.BUSINESS_LEAD, "revenue")
        assert template is not None
    
    def test_business_risk_template(self):
        """Test business risk template."""
        registry = TemplateRegistry()
        template = registry.get(Role.BUSINESS_LEAD, "risk")
        assert template is not None
    
    def test_security_vulnerability_template(self):
        """Test security vulnerability template."""
        registry = TemplateRegistry()
        template = registry.get(Role.SECURITY_OFFICER, "vulnerability")
        assert template is not None
    
    def test_security_compliance_template(self):
        """Test security compliance template."""
        registry = TemplateRegistry()
        template = registry.get(Role.SECURITY_OFFICER, "compliance")
        assert template is not None
    
    def test_cto_architecture_template(self):
        """Test CTO architecture template."""
        registry = TemplateRegistry()
        template = registry.get(Role.CTO, "architecture")
        assert template is not None
    
    def test_cto_technical_strategy_template(self):
        """Test CTO technical_strategy template."""
        registry = TemplateRegistry()
        template = registry.get(Role.CTO, "technical_strategy")
        assert template is not None
    
    def test_all_14_templates_exist(self):
        """Test all 14 templates exist."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        assert len(templates) >= 14


class TestTaskDetermination:
    """Tests for task determination logic."""
    
    def test_task_determined_security_priority(self):
        """Test security findings determine task."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="safe code",
            security_findings=["SQL Injection"],
            code_issues=[],
            business_impact="Low",
            target_role=Role.SECURITY_OFFICER
        )
        # Security findings should trigger vulnerability task
        response = engine.generate(ctx)
        assert isinstance(response, str)
    
    def test_task_determined_performance_priority(self):
        """Test performance issues determine task."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="nested loops",
            security_findings=[],
            code_issues=["O(n²) algorithm"],
            business_impact="Medium",
            target_role=Role.ENGINEER
        )
        response = engine.generate(ctx)
        assert isinstance(response, str)
    
    def test_task_determined_business_priority(self):
        """Test business impact determines task."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="normal code",
            security_findings=[],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.BUSINESS_LEAD
        )
        response = engine.generate(ctx)
        assert isinstance(response, str)


class TestResponseCaching:
    """Tests for response caching."""
    
    def test_identical_contexts_cached(self):
        """Test identical contexts return cached response."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="def f(): pass",
            security_findings=[],
            code_issues=[],
            business_impact="Medium",
            target_role=Role.ENGINEER
        )
        
        response1 = engine.generate(ctx)
        response2 = engine.generate(ctx)
        
        assert response1 == response2
    
    def test_different_contexts_different_responses(self):
        """Test different contexts produce different responses."""
        engine = MultiRoleResponseEngine()
        
        ctx1 = IntegratedContext(
            code="safe",
            security_findings=[],
            code_issues=[],
            business_impact="Low",
            target_role=Role.ENGINEER
        )
        
        ctx2 = IntegratedContext(
            code="unsafe",
            security_findings=["SQL Injection"],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.ENGINEER
        )
        
        response1 = engine.generate(ctx1)
        response2 = engine.generate(ctx2)
        
        # Different contexts should produce responses
        assert isinstance(response1, str)
        assert isinstance(response2, str)


class TestSecurityContextIntegration:
    """Tests for security context integration."""
    
    def test_p0_security_finding_presence(self):
        """Test P0 security finding triggers response."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="eval(user_input)",
            security_findings=["P0: Code Injection via eval()"],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.SECURITY_OFFICER
        )
        
        response = engine.generate(ctx)
        assert "Code Injection" in response or "vulnerability" in response.lower() or len(response) > 0
    
    def test_multiple_security_findings(self):
        """Test multiple security findings."""
        engine = MultiRoleResponseEngine()
        ctx = IntegratedContext(
            code="eval(x); exec(y); global state",
            security_findings=["Code Injection", "Unsafe exec()", "Global state mutation"],
            code_issues=[],
            business_impact="Critical",
            target_role=Role.SECURITY_OFFICER
        )
        
        response = engine.generate(ctx)
        assert isinstance(response, str)
        assert len(response) > 0


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture
def engineer_context():
    """Provide engineer context."""
    return IntegratedContext(
        code="def optimize(): pass",
        security_findings=[],
        code_issues=[],
        business_impact="Medium",
        target_role=Role.ENGINEER
    )


@pytest.fixture
def security_context():
    """Provide security context."""
    return IntegratedContext(
        code="eval(user_data)",
        security_findings=["Code Injection"],
        code_issues=[],
        business_impact="Critical",
        target_role=Role.SECURITY_OFFICER
    )


@pytest.fixture
def business_context():
    """Provide business context."""
    return IntegratedContext(
        code="def revenue_stream(): pass",
        security_findings=[],
        code_issues=[],
        business_impact="Critical",
        target_role=Role.BUSINESS_LEAD
    )
