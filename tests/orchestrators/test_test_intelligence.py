"""
Tests for Test Intelligence Module

Validates test type detection, framework suggestions,
and headed/headless recommendations.

Author: Asif Hussain
Version: 3.8.4
"""

import pytest
from src.orchestrators.test_intelligence import (
    TestIntelligence,
    TestType,
    ExecutionMode,
    detect_test_requirements
)


class TestTestIntelligence:
    """Test suite for test intelligence detection."""
    
    def test_detect_e2e_browser_requirements(self):
        """Should detect browser automation from user interaction keywords."""
        intelligence = TestIntelligence()
        
        description = "User clicks login button and fills email and password fields"
        requirements = intelligence.analyze_requirements(description)
        
        # Should detect unit + e2e_browser
        assert len(requirements) >= 2
        e2e_req = next((r for r in requirements if r.test_type == TestType.E2E_BROWSER), None)
        assert e2e_req is not None
        assert e2e_req.headed_recommended is True
        assert "Playwright" in e2e_req.framework_hints or "Cypress" in e2e_req.framework_hints
    
    def test_detect_visual_regression_requirements(self):
        """Should detect visual regression from styling keywords."""
        intelligence = TestIntelligence()
        
        description = "Responsive design with custom styling and visual appearance updates"
        requirements = intelligence.analyze_requirements(description)
        
        visual_req = next((r for r in requirements if r.test_type == TestType.VISUAL_REGRESSION), None)
        assert visual_req is not None
        assert visual_req.headed_recommended is True
        assert visual_req.execution_mode == ExecutionMode.HEADED_REQUIRED
    
    def test_detect_api_integration_requirements(self):
        """Should detect API testing from endpoint keywords."""
        intelligence = TestIntelligence()
        
        description = "REST API endpoints for authentication with JWT tokens"
        requirements = intelligence.analyze_requirements(description)
        
        api_req = next((r for r in requirements if r.test_type == TestType.E2E_API), None)
        assert api_req is not None
        assert api_req.headed_recommended is False
        assert api_req.execution_mode == ExecutionMode.HEADLESS
    
    def test_detect_performance_requirements(self):
        """Should detect performance testing from load/speed keywords."""
        intelligence = TestIntelligence()
        
        description = "Optimize performance for 1000 concurrent users with low latency"
        requirements = intelligence.analyze_requirements(description)
        
        perf_req = next((r for r in requirements if r.test_type == TestType.PERFORMANCE), None)
        assert perf_req is not None
        assert perf_req.headed_recommended is False
    
    def test_detect_security_requirements(self):
        """Should detect security testing from security keywords."""
        intelligence = TestIntelligence()
        
        description = "Implement authentication with XSS and CSRF protection"
        requirements = intelligence.analyze_requirements(description)
        
        sec_req = next((r for r in requirements if r.test_type == TestType.SECURITY), None)
        assert sec_req is not None
        assert "OWASP" in sec_req.framework_hints or "Bandit" in sec_req.framework_hints
    
    def test_always_includes_unit_tests(self):
        """Should always recommend unit tests regardless of description."""
        intelligence = TestIntelligence()
        
        description = "Simple helper function"
        requirements = intelligence.analyze_requirements(description)
        
        unit_req = next((r for r in requirements if r.test_type == TestType.UNIT), None)
        assert unit_req is not None
        assert unit_req.confidence == 1.0
    
    def test_multiple_test_types_detected(self):
        """Should detect multiple test types from complex description."""
        intelligence = TestIntelligence()
        
        description = """
        User login feature with email and password.
        User clicks login button and sees dashboard.
        REST API authentication with JWT.
        Responsive design for mobile and desktop.
        Performance target: <200ms response time.
        """
        
        requirements = intelligence.analyze_requirements(description)
        
        # Should detect: unit, e2e_browser, e2e_api, visual_regression, performance
        assert len(requirements) >= 4
        test_types = {r.test_type for r in requirements}
        assert TestType.UNIT in test_types
        assert TestType.E2E_BROWSER in test_types
        assert TestType.E2E_API in test_types
    
    def test_generate_test_strategy_summary(self):
        """Should generate comprehensive test strategy summary."""
        intelligence = TestIntelligence()
        
        description = "User navigates through checkout flow with API integration"
        requirements = intelligence.analyze_requirements(description)
        summary = intelligence.generate_test_strategy_summary(requirements)
        
        assert "test_types" in summary
        assert "automation_required" in summary
        assert "framework_suggestions" in summary
        assert summary["automation_required"] is True  # Browser automation detected
    
    def test_format_for_planning_template(self):
        """Should format requirements for planning template."""
        intelligence = TestIntelligence()
        
        description = "User fills form and submits"
        requirements = intelligence.analyze_requirements(description)
        formatted = intelligence.format_for_planning_template(requirements)
        
        assert "🧪 **Test Strategy:**" in formatted
        assert "Unit" in formatted
        assert "E2E Browser" in formatted
        assert "Framework" in formatted.lower() or "Suggested" in formatted
    
    def test_format_with_user_preferences(self):
        """Should use user preferences when available."""
        intelligence = TestIntelligence()
        
        description = "User workflow testing"
        requirements = intelligence.analyze_requirements(description)
        
        user_prefs = {
            "e2e_browser": "Playwright",
            "unit": "pytest"
        }
        
        formatted = intelligence.format_for_planning_template(requirements, user_prefs)
        
        assert "Playwright" in formatted
        assert "from your profile" in formatted
    
    def test_convenience_function(self):
        """Should provide convenience function for quick detection."""
        requirements = detect_test_requirements("User login with API authentication")
        
        assert len(requirements) > 0
        assert any(r.test_type == TestType.UNIT for r in requirements)
    
    def test_headed_vs_headless_recommendations(self):
        """Should correctly recommend headed vs headless execution."""
        intelligence = TestIntelligence()
        
        # Browser interaction - should recommend headed for dev
        browser_desc = "User clicks buttons and fills forms"
        browser_reqs = intelligence.analyze_requirements(browser_desc)
        e2e_req = next((r for r in browser_reqs if r.test_type == TestType.E2E_BROWSER), None)
        assert e2e_req.headed_recommended is True
        
        # API only - should recommend headless
        api_desc = "REST API endpoint integration"
        api_reqs = intelligence.analyze_requirements(api_desc)
        api_req = next((r for r in api_reqs if r.test_type == TestType.E2E_API), None)
        assert api_req.headed_recommended is False
    
    def test_framework_hints_not_prescriptive(self):
        """Should provide framework hints without prescribing."""
        intelligence = TestIntelligence()
        
        description = "E2E user workflow"
        requirements = intelligence.analyze_requirements(description)
        
        e2e_req = next((r for r in requirements if r.test_type == TestType.E2E_BROWSER), None)
        
        # Should suggest multiple frameworks
        assert len(e2e_req.framework_hints) > 1
        # Should include popular options
        frameworks_str = " ".join(e2e_req.framework_hints)
        assert any(fw in frameworks_str for fw in ["Playwright", "Cypress", "Selenium"])
    
    def test_confidence_scores(self):
        """Should assign appropriate confidence scores."""
        intelligence = TestIntelligence()
        
        # Strong browser indicators
        strong_desc = "User clicks login button and navigates to dashboard"
        strong_reqs = intelligence.analyze_requirements(strong_desc)
        e2e_strong = next((r for r in strong_reqs if r.test_type == TestType.E2E_BROWSER), None)
        assert e2e_strong.confidence >= 0.8
        
        # Unit tests always 100% confidence
        unit_req = next((r for r in strong_reqs if r.test_type == TestType.UNIT), None)
        assert unit_req.confidence == 1.0
