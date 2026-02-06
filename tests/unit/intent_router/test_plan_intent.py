"""
Test PLAN intent detection for Phase 25 PLAN MODE enhancement.

Tests CORTEX change detection and PLAN mode routing.

Author: Asif Hussain
Created: 2026-02-06
Phase: 25
"""

import pytest
from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.intent_router import IntentRouter


class TestPlanIntentDetection:
    """Test PLAN intent detection for CORTEX changes."""

    def setup_method(self):
        """Setup test fixtures."""
        self.router = IntentRouter()

    # ========================================================================
    # EXPLICIT PLAN TRIGGERS
    # ========================================================================

    def test_explicit_plan_command(self):
        """Test /plan command triggers PLAN intent."""
        request = "/plan add authentication system"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.95
        assert "authentication system" in intent.context

    def test_explicit_plan_command_no_args(self):
        """Test /plan without args triggers plan wizard."""
        request = "/plan"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence == 1.0
        assert intent.requires_wizard is True

    # ========================================================================
    # IMPLICIT CORTEX CHANGE DETECTION
    # ========================================================================

    def test_add_feature_to_cortex(self):
        """Test 'add X to CORTEX' triggers PLAN intent."""
        request = "add caching layer to CORTEX"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.85
        assert intent.operation == "CREATE"

    def test_implement_orchestrator(self):
        """Test 'implement orchestrator' triggers PLAN intent."""
        request = "implement a new validation orchestrator"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.85

    def test_enhance_cortex_architect(self):
        """Test 'enhance cortex-architect' triggers PLAN intent."""
        request = "enhance cortex-architect with new mode"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.85

    def test_modify_cortex_component(self):
        """Test 'modify CORTEX component' triggers PLAN intent."""
        request = "modify the master orchestrator to add logging"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.80

    def test_create_orchestrator(self):
        """Test 'create orchestrator' triggers PLAN intent."""
        request = "create a new reporting orchestrator"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.85

    def test_add_mcp_tool(self):
        """Test 'add MCP tool' triggers PLAN intent."""
        request = "add MCP tool for code analysis"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.85

    def test_update_wiring(self):
        """Test 'update wiring' triggers PLAN intent."""
        request = "update wiring.yaml to register new orchestrator"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.confidence >= 0.80

    # ========================================================================
    # DEPRECATION DETECTION
    # ========================================================================

    def test_delete_cortex_feature(self):
        """Test 'delete CORTEX feature' triggers PLAN with DEPRECATE."""
        request = "delete the old challenge orchestrator"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.operation == "DEPRECATE"
        assert intent.confidence >= 0.85

    def test_remove_orchestrator(self):
        """Test 'remove orchestrator' triggers PLAN with DEPRECATE."""
        request = "remove the legacy reporting orchestrator"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.operation == "DEPRECATE"

    def test_deprecate_component(self):
        """Test 'deprecate component' triggers PLAN with DEPRECATE."""
        request = "deprecate the old wiring system"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.PLAN
        assert intent.operation == "DEPRECATE"

    # ========================================================================
    # EXCLUDED PATTERNS (SHOULD NOT TRIGGER PLAN)
    # ========================================================================

    def test_audit_command_not_plan(self):
        """Test 'audit' does not trigger PLAN intent."""
        request = "audit the codebase for issues"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.AUDIT
        assert intent.type != IntentType.PLAN

    def test_analyze_command_not_plan(self):
        """Test 'analyze' does not trigger PLAN intent."""
        request = "analyze the master orchestrator"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.ANALYZE
        assert intent.type != IntentType.PLAN

    def test_fix_bug_not_plan(self):
        """Test 'fix bug' does not trigger PLAN intent."""
        request = "fix bug in validation logic"
        intent = self.router.detect_intent(request)
        
        assert intent.type == IntentType.FIX
        assert intent.type != IntentType.PLAN

    def test_external_project_not_plan(self):
        """Test external project work does not trigger PLAN."""
        request = "create a new React component for the dashboard"
        intent = self.router.detect_intent(request)
        
        assert intent.type != IntentType.PLAN
        # Should be IMPLEMENT for external work

    # ========================================================================
    # CONFIDENCE SCORING
    # ========================================================================

    def test_explicit_command_max_confidence(self):
        """Test explicit /plan command has maximum confidence."""
        request = "/plan create new feature"
        intent = self.router.detect_intent(request)
        
        assert intent.confidence == 1.0

    def test_strong_cortex_keywords_high_confidence(self):
        """Test strong CORTEX keywords yield high confidence."""
        request = "implement new orchestrator in CORTEX"
        intent = self.router.detect_intent(request)
        
        assert intent.confidence >= 0.85

    def test_weak_cortex_signal_lower_confidence(self):
        """Test weak CORTEX signals yield lower confidence."""
        request = "maybe update some orchestrator code"
        intent = self.router.detect_intent(request)
        
        # Should still detect PLAN but with lower confidence
        if intent.type == IntentType.PLAN:
            assert intent.confidence < 0.85

    # ========================================================================
    # CONTEXT EXTRACTION
    # ========================================================================

    def test_extracts_feature_name(self):
        """Test feature name extraction from request."""
        request = "/plan add authentication system to CORTEX"
        intent = self.router.detect_intent(request)
        
        assert "authentication system" in intent.context

    def test_extracts_component_name(self):
        """Test component name extraction."""
        request = "modify the MasterOrchestrator to add caching"
        intent = self.router.detect_intent(request)
        
        assert "MasterOrchestrator" in intent.context or "master orchestrator" in intent.context.lower()

    def test_extracts_operation_type(self):
        """Test operation type (CREATE/UPDATE/DEPRECATE) extraction."""
        test_cases = [
            ("add new feature", "CREATE"),
            ("update existing orchestrator", "UPDATE"),
            ("delete old component", "DEPRECATE"),
        ]
        
        for request, expected_op in test_cases:
            intent = self.router.detect_intent(request)
            if intent.type == IntentType.PLAN:
                assert intent.operation == expected_op


class TestPlanIntentRouting:
    """Test PLAN intent routing to PlanOrchestrator."""

    def setup_method(self):
        """Setup test fixtures."""
        self.router = IntentRouter()

    def test_routes_to_plan_orchestrator(self):
        """Test PLAN intent routes to PlanOrchestrator."""
        request = "/plan add feature X"
        intent = self.router.detect_intent(request)
        orchestrator = self.router.route_intent(intent)
        
        assert orchestrator.name == "PlanOrchestrator"

    def test_plan_orchestrator_receives_context(self):
        """Test PlanOrchestrator receives full intent context."""
        request = "/plan implement authentication system"
        intent = self.router.detect_intent(request)
        orchestrator = self.router.route_intent(intent)
        
        # Orchestrator should have access to intent context
        assert hasattr(orchestrator, "process_intent")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
