"""
Tests for MasterOrchestrator workflow template routing.

Phase 100 Stage 3: MasterOrchestrator Stage 2 integration

Test Coverage:
- Template routing when suggested by IntentRouter
- Fallback to standard routing when no template
- Seamless user experience

Author: Asif Hussain
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

# AC_START: AC-PHASE100-005
# Description: MasterOrchestrator template routing


class TestMasterOrchestratorTemplateRouting:
    """Test MasterOrchestrator routing with workflow templates."""

    @patch("cortex.orchestrators.core.master_orchestrator.IntentRouter")
    @patch("cortex.orchestrators.workflow.template_registry.WorkflowTemplateRegistry")
    def test_routes_to_workflow_when_template_suggested(
        self, mock_registry_class, mock_router_class
    ):
        """Should route to AutonomousWorkflowExecutor when template suggested."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        # Mock IntentRouter suggests template
        mock_router = MagicMock()
        mock_router.classify_intent_with_workflow_suggestion.return_value = (
            "IMPLEMENT",
            "tdd/feature-implementation",
        )
        mock_router_class.return_value = mock_router

        # Mock template registry
        mock_registry = MagicMock()
        mock_registry.get_template.return_value = {
            "id": "tdd/feature-implementation",
            "name": "Feature Implementation TDD",
            "steps": [],
        }
        mock_registry_class.return_value = mock_registry

        orchestrator = MasterOrchestrator()
        context = {
            "description": "Implement user authentication",
            "intent": "IMPLEMENT",
        }

        # This should route through workflow template path
        routing_decision = orchestrator._check_for_workflow_template(context)

        assert routing_decision is not None
        assert routing_decision["template_id"] == "tdd/feature-implementation"

    @patch("cortex.orchestrators.core.master_orchestrator.IntentRouter")
    def test_standard_routing_when_no_template(self, mock_router_class):
        """Should use standard routing when no template suggested."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        # Mock IntentRouter does NOT suggest template
        mock_router = MagicMock()
        mock_router.classify_intent_with_workflow_suggestion.return_value = (
            "IMPLEMENT",
            None,  # No template
        )
        mock_router_class.return_value = mock_router

        orchestrator = MasterOrchestrator()
        context = {
            "description": "Implement custom feature",
            "intent": "IMPLEMENT",
        }

        routing_decision = orchestrator._check_for_workflow_template(context)

        assert routing_decision is None  # Falls back to standard routing

    @patch("cortex.orchestrators.core.master_orchestrator.IntentRouter")
    @patch("cortex.orchestrators.workflow.template_registry.WorkflowTemplateRegistry")
    def test_seamless_user_experience_no_template_prompt(
        self, mock_registry_class, mock_router_class
    ):
        """Should not prompt user to choose template (transparent)."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        # Mock IntentRouter suggests template
        mock_router = MagicMock()
        mock_router.classify_intent_with_workflow_suggestion.return_value = (
            "FIX",
            "tdd/frontend-visual",
        )
        mock_router_class.return_value = mock_router

        # Mock template registry
        mock_registry = MagicMock()
        mock_registry.get_template.return_value = {
            "id": "tdd/frontend-visual",
            "name": "Frontend Visual TDD",
            "steps": [],
        }
        mock_registry_class.return_value = mock_registry

        orchestrator = MasterOrchestrator()
        context = {
            "description": "Fix button styling",
            "intent": "FIX",
            "attachments": [{"type": "image/png"}],
        }

        routing_decision = orchestrator._check_for_workflow_template(context)

        # Template selected automatically, no user interaction
        assert routing_decision is not None
        assert "requires_user_choice" not in routing_decision
        assert routing_decision["template_id"] == "tdd/frontend-visual"


# AC_COMPLETE: AC-PHASE100-005 ✅ 3/3 tests written (RED phase)
