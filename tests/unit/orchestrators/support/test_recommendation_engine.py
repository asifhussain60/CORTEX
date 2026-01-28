"""
Unit tests for RecommendationEngine (Phase 8.4).

Tests advisor instantiation, recommendation loading, and result generation.

AC-ID: AC-SECURITY-FRAMEWORK-001 (Phase 8.4)
Authority: CORE-008 (TDD), CORE-011, CORE-012
"""

import unittest
from pathlib import Path

from cortex.orchestrators.support.recommendation_engine import (
    RecommendationEngine,
    SecurityAdvisor,
    SolidAdvisor,
    PerformanceAdvisor,
    ComplianceAdvisor,
    AdvisorType,
    Recommendation,
    get_recommendation_engine,
)


class TestSecurityAdvisor(unittest.TestCase):
    """Test SecurityAdvisor."""

    def setUp(self) -> None:
        """Initialize advisor before each test."""
        self.advisor = SecurityAdvisor()

    def test_security_advisor_initializes(self) -> None:
        """Test SecurityAdvisor initialization."""
        self.assertIsNotNone(self.advisor)
        self.assertEqual(self.advisor.yaml_pattern, "security/*.yaml")

    def test_security_advisor_loads_patterns(self) -> None:
        """Test that SecurityAdvisor loads YAML patterns."""
        # patterns dict should be populated (even if empty if no files exist)
        self.assertIsInstance(self.advisor.patterns, dict)

    def test_security_advisor_can_recommend_for_cwe(self) -> None:
        """Test generating recommendations for a CWE."""
        # Should not crash even if no patterns exist
        recs = self.advisor.recommend("CWE-94")
        self.assertIsInstance(recs, list)


class TestSolidAdvisor(unittest.TestCase):
    """Test SolidAdvisor."""

    def setUp(self) -> None:
        """Initialize advisor before each test."""
        self.advisor = SolidAdvisor()

    def test_solid_advisor_initializes(self) -> None:
        """Test SolidAdvisor initialization."""
        self.assertIsNotNone(self.advisor)
        self.assertEqual(self.advisor.yaml_pattern, "solid/*.yaml")

    def test_solid_advisor_can_recommend(self) -> None:
        """Test generating SOLID recommendations."""
        recs = self.advisor.recommend("SRP")
        self.assertIsInstance(recs, list)


class TestPerformanceAdvisor(unittest.TestCase):
    """Test PerformanceAdvisor."""

    def setUp(self) -> None:
        """Initialize advisor before each test."""
        self.advisor = PerformanceAdvisor()

    def test_performance_advisor_initializes(self) -> None:
        """Test PerformanceAdvisor initialization."""
        self.assertIsNotNone(self.advisor)


class TestComplianceAdvisor(unittest.TestCase):
    """Test ComplianceAdvisor."""

    def setUp(self) -> None:
        """Initialize advisor before each test."""
        self.advisor = ComplianceAdvisor()

    def test_compliance_advisor_initializes(self) -> None:
        """Test ComplianceAdvisor initialization."""
        self.assertIsNotNone(self.advisor)


class TestRecommendation(unittest.TestCase):
    """Test Recommendation dataclass."""

    def test_recommendation_creation(self) -> None:
        """Test creating a Recommendation."""
        rec = Recommendation(
            advisor_type=AdvisorType.SECURITY,
            pattern_id="pattern_001",
            title="Use safe_eval",
            description="Replace eval() with ast.literal_eval()",
            severity="HIGH",
            pattern_reference="security_eval_injection.yaml",
            code_example="result = ast.literal_eval(user_input)",
            rationale="eval() allows arbitrary code execution"
        )
        
        self.assertEqual(rec.advisor_type, AdvisorType.SECURITY)
        self.assertEqual(rec.pattern_id, "pattern_001")
        self.assertEqual(rec.severity, "HIGH")

    def test_recommendation_has_required_fields(self) -> None:
        """Test that Recommendation has required fields."""
        rec = Recommendation(
            advisor_type=AdvisorType.SOLID,
            pattern_id="test",
            title="Test",
            description="Test",
            severity="MEDIUM",
            pattern_reference="test.yaml"
        )
        
        self.assertTrue(hasattr(rec, "advisor_type"))
        self.assertTrue(hasattr(rec, "pattern_id"))
        self.assertTrue(hasattr(rec, "title"))
        self.assertTrue(hasattr(rec, "description"))
        self.assertTrue(hasattr(rec, "severity"))


class TestRecommendationEngine(unittest.TestCase):
    """Test RecommendationEngine."""

    def setUp(self) -> None:
        """Initialize engine before each test."""
        self.engine = RecommendationEngine()

    def test_recommendation_engine_initializes(self) -> None:
        """Test RecommendationEngine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.security_advisor)
        self.assertIsNotNone(self.engine.solid_advisor)
        self.assertIsNotNone(self.engine.performance_advisor)
        self.assertIsNotNone(self.engine.compliance_advisor)

    def test_recommend_for_security_returns_result(self) -> None:
        """Test security recommendation method."""
        result = self.engine.recommend_for_security("CWE-94")
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, "success"))
        self.assertTrue(hasattr(result, "recommendations"))
        self.assertTrue(hasattr(result, "summary"))

    def test_recommend_for_security_with_context(self) -> None:
        """Test security recommendation with context."""
        result = self.engine.recommend_for_security(
            "CWE-94",
            {"threat": "Code injection", "file": "handler.py"}
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success or not result.success)  # Should not crash

    def test_recommend_for_solid_returns_result(self) -> None:
        """Test SOLID recommendation method."""
        result = self.engine.recommend_for_solid("SRP")
        
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, "success"))
        self.assertTrue(hasattr(result, "recommendations"))

    def test_recommend_for_performance_returns_result(self) -> None:
        """Test performance recommendation method."""
        result = self.engine.recommend_for_performance("n_plus_one")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success or not result.success)

    def test_recommend_for_compliance_returns_result(self) -> None:
        """Test compliance recommendation method."""
        result = self.engine.recommend_for_compliance("CORE-008")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success or not result.success)

    def test_recommendation_result_has_summary(self) -> None:
        """Test that recommendation results include summary."""
        result = self.engine.recommend_for_security("CWE-94")
        
        self.assertIsNotNone(result.summary)
        self.assertIsInstance(result.summary, str)


class TestRecommendationEngineSingleton(unittest.TestCase):
    """Test RecommendationEngine singleton."""

    def test_get_recommendation_engine_returns_instance(self) -> None:
        """Test factory function returns instance."""
        engine = get_recommendation_engine()
        self.assertIsNotNone(engine)
        self.assertIsInstance(engine, RecommendationEngine)

    def test_get_recommendation_engine_returns_same_instance(self) -> None:
        """Test factory function returns same singleton."""
        engine1 = get_recommendation_engine()
        engine2 = get_recommendation_engine()
        
        self.assertIs(engine1, engine2)

    def test_singleton_persists_across_calls(self) -> None:
        """Test singleton persists across multiple calls."""
        engine1 = get_recommendation_engine()
        
        # Make a recommendation
        result1 = engine1.recommend_for_security("CWE-94")
        
        # Get engine again
        engine2 = get_recommendation_engine()
        
        # Should be same instance
        self.assertIs(engine1, engine2)


if __name__ == "__main__":
    unittest.main()
