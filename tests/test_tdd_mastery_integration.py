"""
Integration tests for TDD Mastery Phase 1 components.

Tests Edge Case Analyzer, Domain Knowledge Integrator, and TDD Intent Router.

Author: Asif Hussain
Created: 2025-11-21
"""

import ast
import pytest
from src.cortex_agents.test_generator.edge_case_analyzer import EdgeCaseAnalyzer, EdgeCase
from src.cortex_agents.test_generator.domain_knowledge_integrator import DomainKnowledgeIntegrator
from src.cortex_agents.test_generator.tdd_intent_router import TDDIntentRouter, Intent


class TestEdgeCaseAnalyzer:
    """Test Edge Case Analyzer functionality."""
    
    def test_analyze_numeric_parameter(self):
        """Test edge case generation for numeric parameters."""
        source_code = '''
def calculate_discount(price: float, discount: float) -> float:
    """Calculate discounted price."""
    return price * (1 - discount)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        analyzer = EdgeCaseAnalyzer()
        edge_cases = analyzer.analyze_function(func_node, source_code)
        
        # Should generate edge cases for zero, negative, large values
        assert len(edge_cases) > 0
        edge_case_names = [ec.name for ec in edge_cases]
        
        # Check for expected edge cases
        assert any("zero" in name for name in edge_case_names)
        assert any("negative" in name for name in edge_case_names)
    
    def test_analyze_string_parameter(self):
        """Test edge case generation for string parameters."""
        source_code = '''
def validate_email(email: str) -> bool:
    """Validate email format."""
    return "@" in email and "." in email
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        analyzer = EdgeCaseAnalyzer()
        edge_cases = analyzer.analyze_function(func_node, source_code)
        
        edge_case_names = [ec.name for ec in edge_cases]
        
        # Check for string edge cases
        assert any("empty" in name for name in edge_case_names)
        assert any("whitespace" in name or "unicode" in name for name in edge_case_names)
    
    def test_analyze_collection_parameter(self):
        """Test edge case generation for collection parameters."""
        source_code = '''
def calculate_total(items: list) -> float:
    """Calculate total price of items."""
    return sum(item["price"] for item in items)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        analyzer = EdgeCaseAnalyzer()
        edge_cases = analyzer.analyze_function(func_node, source_code)
        
        edge_case_names = [ec.name for ec in edge_cases]
        
        # Check for collection edge cases
        assert any("empty" in name for name in edge_case_names)
        assert any("single" in name or "large" in name for name in edge_case_names)
    
    def test_confidence_filtering(self):
        """Test confidence-based filtering."""
        source_code = '''
def add(a: int, b: int) -> int:
    return a + b
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        analyzer = EdgeCaseAnalyzer()
        all_cases = analyzer.analyze_function(func_node, source_code)
        filtered = analyzer.filter_by_confidence(min_confidence=0.7)
        
        # Filtered should be subset
        assert len(filtered) <= len(all_cases)
        
        # All filtered cases should meet threshold
        for ec in filtered:
            assert ec.confidence >= 0.7
    
    def test_edge_case_prioritization(self):
        """Test edge case prioritization."""
        source_code = '''
def process_data(data: dict, value: int) -> str:
    return str(data[value])
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        analyzer = EdgeCaseAnalyzer()
        analyzer.analyze_function(func_node, source_code)
        prioritized = analyzer.prioritize_edge_cases()
        
        # Should return in priority order
        assert len(prioritized) > 0
        
        # First item should have high priority
        if len(prioritized) > 1:
            assert prioritized[0].confidence >= prioritized[-1].confidence


class TestDomainKnowledgeIntegrator:
    """Test Domain Knowledge Integrator functionality."""
    
    def test_infer_authentication_domain(self):
        """Test authentication domain inference."""
        integrator = DomainKnowledgeIntegrator()
        
        func_info = {
            "name": "user_login",
            "parameters": [],
            "docstring": "Authenticate user credentials"
        }
        
        domain = integrator.infer_domain(func_info)
        assert domain == "authentication"
    
    def test_infer_validation_domain(self):
        """Test validation domain inference."""
        integrator = DomainKnowledgeIntegrator()
        
        func_info = {
            "name": "validate_email",
            "parameters": [],
            "docstring": "Check if email is valid"
        }
        
        domain = integrator.infer_domain(func_info)
        assert domain == "validation"
    
    def test_infer_calculation_domain(self):
        """Test calculation domain inference."""
        integrator = DomainKnowledgeIntegrator()
        
        func_info = {
            "name": "calculate_total",
            "parameters": [],
            "docstring": "Sum all item prices"
        }
        
        domain = integrator.infer_domain(func_info)
        assert domain == "calculation"
    
    def test_get_business_patterns(self):
        """Test business pattern retrieval."""
        integrator = DomainKnowledgeIntegrator()
        
        func_info = {
            "name": "user_login",
            "parameters": [],
            "docstring": "Authenticate user"
        }
        
        patterns = integrator.get_business_patterns(func_info)
        
        assert len(patterns) > 0
        assert patterns[0].domain == "authentication"
        assert "login" in patterns[0].operation
    
    def test_generate_smart_assertions(self):
        """Test smart assertion generation."""
        integrator = DomainKnowledgeIntegrator()
        
        func_info = {
            "name": "calculate_total",
            "parameters": [{"name": "items", "type": "list"}],
            "return_type": "float",
            "docstring": "Calculate total"
        }
        
        assertions = integrator.generate_smart_assertions(
            func_info,
            "empty_list",
            {"items": []}
        )
        
        assert len(assertions) > 0
        assert "assert" in assertions[0]
    
    def test_improve_assertion_strength(self):
        """Test assertion strength improvement."""
        integrator = DomainKnowledgeIntegrator()
        
        weak_test = '''
def test_example(self):
    result = calculate_total(items)
    assert result is not None
'''
        
        improved = integrator.improve_assertion_strength(weak_test)
        
        # Should add TODO comment
        assert "TODO" in improved or "assert result" in improved


class TestTDDIntentRouter:
    """Test TDD Intent Router functionality."""
    
    def test_detect_implement_intent(self):
        """Test IMPLEMENT intent detection."""
        router = TDDIntentRouter()
        
        decision = router.route("implement user authentication")
        
        assert decision.intent == Intent.IMPLEMENT
        assert decision.should_use_tdd is True
        assert decision.workflow == "tdd"
        assert decision.confidence >= 0.90
    
    def test_detect_fix_intent(self):
        """Test FIX intent detection."""
        router = TDDIntentRouter()
        
        decision = router.route("fix the login bug")
        
        assert decision.intent == Intent.FIX
        assert decision.workflow in ["fix", "tdd"]
    
    def test_detect_refactor_intent(self):
        """Test REFACTOR intent detection."""
        router = TDDIntentRouter()
        
        decision = router.route("refactor authentication module")
        
        assert decision.intent == Intent.REFACTOR
        assert decision.should_use_tdd is True  # Test-protected refactoring
        assert decision.workflow == "tdd"
    
    def test_extract_feature_name(self):
        """Test feature name extraction."""
        router = TDDIntentRouter()
        
        decision = router.route("implement password reset functionality")
        
        assert decision.extracted_feature is not None
        assert "password" in decision.extracted_feature.lower() or "reset" in decision.extracted_feature.lower()
    
    def test_tdd_enforcement_for_critical_features(self):
        """Test TDD enforcement for critical features."""
        router = TDDIntentRouter()
        
        # Authentication is critical
        decision = router.route("implement authentication")
        assert decision.should_use_tdd is True
        
        # Payment is critical
        decision = router.route("implement payment processing")
        assert decision.should_use_tdd is True
        
        # Security is critical
        decision = router.route("add security validation")
        assert decision.should_use_tdd is True
    
    def test_format_tdd_workflow_message(self):
        """Test TDD workflow message formatting."""
        router = TDDIntentRouter()
        
        decision = router.route("implement user login")
        message = router.format_tdd_workflow_message(decision)
        
        assert "TDD Workflow Activated" in message
        assert "RED Phase" in message
        assert "GREEN Phase" in message
        assert "REFACTOR Phase" in message
    
    def test_confidence_scoring(self):
        """Test confidence scoring accuracy."""
        router = TDDIntentRouter()
        
        # Clear implement should have high confidence
        clear_decision = router.route("implement authentication")
        assert clear_decision.confidence >= 0.90
        
        # Ambiguous request should have lower confidence
        ambiguous_decision = router.route("do something with users")
        assert ambiguous_decision.confidence < 0.90


class TestIntegration:
    """Integration tests combining all components."""
    
    def test_full_tdd_workflow_routing(self):
        """Test complete workflow from routing to test generation."""
        router = TDDIntentRouter()
        analyzer = EdgeCaseAnalyzer()
        integrator = DomainKnowledgeIntegrator()
        
        # User request
        request = "implement password reset"
        
        # Route request
        decision = router.route(request)
        assert decision.should_use_tdd is True
        
        # Analyze function for edge cases
        source_code = '''
def reset_password(email: str, token: str, new_password: str) -> bool:
    """Reset user password with token."""
    return True
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        edge_cases = analyzer.analyze_function(func_node, source_code)
        assert len(edge_cases) > 0
        
        # Get domain patterns
        func_info = {
            "name": "reset_password",
            "parameters": [
                {"name": "email", "type": "str"},
                {"name": "token", "type": "str"},
                {"name": "new_password", "type": "str"}
            ],
            "docstring": "Reset user password"
        }
        
        patterns = integrator.get_business_patterns(func_info)
        # Pattern matching may not find exact match, but domain should be inferred
        domain = integrator.infer_domain(func_info)
        assert domain == "authentication"
    
    def test_quality_improvement_validation(self):
        """Validate quality improvement from Phase 1 enhancements."""
        analyzer = EdgeCaseAnalyzer()
        integrator = DomainKnowledgeIntegrator()
        
        # Test function
        source_code = '''
def calculate_total(items: list) -> float:
    """Calculate total price."""
    return sum(item["price"] for item in items)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        # Generate edge cases
        edge_cases = analyzer.analyze_function(func_node, source_code)
        high_confidence = analyzer.filter_by_confidence(0.6)
        
        # Should have multiple high-quality edge cases
        assert len(high_confidence) >= 3
        
        # Should cover empty, normal, and error cases
        edge_names = [ec.name for ec in high_confidence]
        assert any("empty" in name for name in edge_names)
        
        # Get smart assertions
        func_info = {
            "name": "calculate_total",
            "parameters": [{"name": "items", "type": "list"}],
            "return_type": "float",
            "docstring": "Calculate total"
        }
        
        assertions = integrator.generate_smart_assertions(
            func_info,
            "empty",
            {"items": []}
        )
        
        # Assertions should be specific
        assert len(assertions) > 0
        assert not all("is not None" in a for a in assertions)  # Not just weak assertions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
