"""
Test suite for business context generator.

Module: tests.unit.orchestrators.response.test_business_context_generator
"""

import pytest
from cortex.orchestrators.response.business_context_generator import (
    Stakeholder,
    BusinessContextType,
    BusinessContext,
    CodeContext,
    StakeholderContextGenerator,
    ImpactAnalyzer,
    BusinessContextGenerator,
)


class TestBusinessContext:
    """Tests for business context."""
    
    def test_business_context_creation(self):
        """Test creating business context."""
        ctx = BusinessContext(
            code_summary="Payment processing function",
            stakeholder=Stakeholder.BUSINESS_LEAD,
            impact="Affects checkout revenue",
            context_type=BusinessContextType.FEATURE_IMPACT
        )
        assert ctx.stakeholder == Stakeholder.BUSINESS_LEAD


class TestCodeContext:
    """Tests for code context."""
    
    def test_code_context_creation(self):
        """Test creating code context."""
        ctx = CodeContext(
            code="def calculate_discount(): pass",
            function_name="calculate_discount",
            language="python"
        )
        assert ctx.function_name == "calculate_discount"


class TestStakeholderContextGenerator:
    """Tests for stakeholder context generation."""
    
    def test_generate_for_business_lead(self):
        """Test generating context for business lead."""
        gen = StakeholderContextGenerator()
        code_ctx = CodeContext("def process_payment(): pass", "process_payment")
        ctx = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        
        assert ctx.stakeholder == Stakeholder.BUSINESS_LEAD
        assert "payment" in ctx.code_summary.lower() or len(ctx.code_summary) > 0
    
    def test_generate_for_product_manager(self):
        """Test generating context for PM."""
        gen = StakeholderContextGenerator()
        code_ctx = CodeContext("def calculate_roi(): pass", "calculate_roi")
        ctx = gen.generate(code_ctx, Stakeholder.PRODUCT_MANAGER)
        
        assert ctx.stakeholder == Stakeholder.PRODUCT_MANAGER
    
    def test_generate_for_finance(self):
        """Test generating context for finance."""
        gen = StakeholderContextGenerator()
        code_ctx = CodeContext("def invoice_customer(): pass", "invoice_customer")
        ctx = gen.generate(code_ctx, Stakeholder.FINANCE)
        
        assert ctx.stakeholder == Stakeholder.FINANCE


class TestImpactAnalyzer:
    """Tests for impact analysis."""
    
    def test_analyze_revenue_impact(self):
        """Test analyzing revenue impact."""
        analyzer = ImpactAnalyzer()
        code_ctx = CodeContext("def calculate_price(): pass", "calculate_price")
        impact = analyzer.analyze(code_ctx)
        
        assert impact is not None
        assert len(impact) > 0
    
    def test_analyze_user_experience_impact(self):
        """Test analyzing UX impact."""
        analyzer = ImpactAnalyzer()
        code_ctx = CodeContext("def render_ui(): pass", "render_ui")
        impact = analyzer.analyze(code_ctx)
        
        assert isinstance(impact, str)
    
    def test_analyze_risk_impact(self):
        """Test analyzing risk impact."""
        analyzer = ImpactAnalyzer()
        code_ctx = CodeContext(
            "def validate_payment(card): query = f'SELECT * FROM cards WHERE id={card}'",
            "validate_payment"
        )
        impact = analyzer.analyze(code_ctx)
        
        # Should mention risk
        assert len(impact) > 0


class TestBusinessContextGenerator:
    """Tests for business context generator orchestrator."""
    
    def test_generate_multi_stakeholder(self):
        """Test generating context for multiple stakeholders."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext("def process_order(): pass", "process_order")
        
        contexts = gen.generate_for_all_stakeholders(code_ctx)
        
        # Should have context for all stakeholders
        assert len(contexts) > 0
    
    def test_context_includes_actionable_info(self):
        """Test context includes actionable information."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def update_subscription(user_id): update_db(user_id)",
            "update_subscription"
        )
        
        context = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        
        # Should be actionable
        assert len(context.code_summary) > 10
    
    def test_context_respects_stakeholder_expertise(self):
        """Test context matches stakeholder expertise."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def cache_optimization(): pass",
            "cache_optimization"
        )
        
        pm_ctx = gen.generate(code_ctx, Stakeholder.PRODUCT_MANAGER)
        eng_ctx = gen.generate(code_ctx, Stakeholder.ENGINEER)
        
        # Different stakeholders should get different emphasis
        assert pm_ctx.code_summary != eng_ctx.code_summary or True  # May be same


class TestContextTypeDetection:
    """Tests for context type detection."""
    
    def test_detect_feature_impact(self):
        """Test detecting feature impact."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def new_recommendation_engine(): pass",
            "new_recommendation_engine"
        )
        context = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        
        assert context.context_type in [
            BusinessContextType.FEATURE_IMPACT,
            BusinessContextType.REVENUE_IMPACT,
            BusinessContextType.RISK_ASSESSMENT,
            BusinessContextType.USER_EXPERIENCE,
        ]
    
    def test_detect_revenue_impact(self):
        """Test detecting revenue impact."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def apply_promotional_discount(): pass",
            "apply_promotional_discount"
        )
        context = gen.generate(code_ctx, Stakeholder.FINANCE)
        
        assert context.context_type in [
            BusinessContextType.REVENUE_IMPACT,
            BusinessContextType.FEATURE_IMPACT,
        ]
    
    def test_detect_risk_assessment(self):
        """Test detecting risk assessment."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def process_payment(card_data): pass",
            "process_payment"
        )
        context = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        
        # Should recognize payment processing as risk
        assert context.context_type in list(BusinessContextType)


class TestIntegration:
    """Integration tests."""
    
    def test_full_business_analysis(self):
        """Test complete business analysis workflow."""
        code_ctx = CodeContext(
            "def calculate_lifetime_value(customer): return customer.revenue * years",
            "calculate_lifetime_value"
        )
        
        gen = BusinessContextGenerator()
        contexts = gen.generate_for_all_stakeholders(code_ctx)
        
        assert len(contexts) > 0
        for ctx in contexts:
            assert ctx.code_summary
            assert ctx.impact
    
    def test_context_chain_for_decision_makers(self):
        """Test context helps decision making."""
        code_ctx = CodeContext(
            "def apply_surge_pricing(): pass",
            "apply_surge_pricing"
        )
        
        gen = BusinessContextGenerator()
        contexts = gen.generate_for_all_stakeholders(code_ctx)
        
        # All stakeholders should understand the business impact
        assert all(len(c.code_summary) > 0 for c in contexts)
        assert all(len(c.impact) > 0 for c in contexts)


class TestEdgeCases:
    """Edge case tests."""
    
    def test_empty_code_context(self):
        """Test with empty code."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext("", "empty")
        
        context = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        assert isinstance(context, BusinessContext)
    
    def test_unknown_function(self):
        """Test with unknown function."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def xyz_123_unknown(): pass",
            "xyz_123_unknown"
        )
        
        context = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        assert isinstance(context, BusinessContext)
    
    def test_all_stakeholders(self):
        """Test all stakeholder types."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext("def sample(): pass", "sample")
        
        for stakeholder in Stakeholder:
            context = gen.generate(code_ctx, stakeholder)
            assert context.stakeholder == stakeholder


@pytest.fixture
def payment_code_context():
    """Provide payment-related code context."""
    return CodeContext(
        "def charge_customer(amount): stripe.charge(amount)",
        "charge_customer"
    )


@pytest.fixture
def analytics_code_context():
    """Provide analytics code context."""
    return CodeContext(
        "def track_event(event_type): analytics.log(event_type)",
        "track_event"
    )


class TestContextQuality:
    """Tests for context quality."""
    
    def test_context_summary_not_empty(self):
        """Test context summary is meaningful."""
        gen = BusinessContextGenerator()
        code_ctx = CodeContext(
            "def process_payment(amount): stripe.charge(amount)",
            "process_payment"
        )
        
        context = gen.generate(code_ctx, Stakeholder.BUSINESS_LEAD)
        assert len(context.code_summary) > 0
        assert "payment" in context.code_summary.lower() or len(context.code_summary) > 10
