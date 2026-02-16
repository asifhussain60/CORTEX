"""
Tests for IntentRouter workflow template suggestion.

Phase 100 Stage 3: IntentRouter integration with WorkflowTemplateRegistry

Test Coverage:
- classify_intent_with_workflow_suggestion() method
- Visual context detection (screenshot attachments)
- Template suggestion logic
- Fallback to standard classification

Author: Asif Hussain
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# AC_START: AC-PHASE100-004
# Description: IntentRouter workflow template suggestion


class TestIntentClassificationWithTemplates:
    """Test intent classification with workflow template suggestions."""

    def test_classify_with_visual_context_suggests_frontend_template(self):
        """Should suggest frontend-visual-tdd template when screenshot attached."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        context = {
            "description": "Fix button styling issue",
            "intent": "FIX",
            "attachments": [
                {"type": "image/png", "name": "screenshot.png"}
            ],
        }

        intent, template_id = router.classify_intent_with_workflow_suggestion(context)

        assert intent == "FIX"
        assert template_id == "tdd/frontend-visual"

    def test_classify_without_visual_context_no_template(self):
        """Should not suggest template when no visual context."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        context = {
            "description": "Fix backend API bug",
            "intent": "FIX",
            "attachments": [],
        }

        intent, template_id = router.classify_intent_with_workflow_suggestion(context)

        assert intent == "FIX"
        assert template_id is None

    def test_classify_implement_with_api_keyword_suggests_api_template(self):
        """Should suggest api-service template for API implementation."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        context = {
            "description": "Implement new REST API endpoint for user authentication",
            "intent": "IMPLEMENT",
            "keywords": ["api", "endpoint", "authentication"],
        }

        intent, template_id = router.classify_intent_with_workflow_suggestion(context)

        assert intent == "IMPLEMENT"
        assert template_id == "tdd/api-service"

    def test_classify_security_audit_suggests_security_template(self):
        """Should suggest security-compliance template for security audits."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        context = {
            "description": "Run security compliance audit",
            "intent": "AUDIT",
            "keywords": ["security", "compliance", "audit"],
        }

        intent, template_id = router.classify_intent_with_workflow_suggestion(context)

        assert intent == "AUDIT"
        assert template_id == "security/compliance-audit"

    def test_classify_generic_implement_no_specific_template(self):
        """Should use generic feature template for standard implementations."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        context = {
            "description": "Implement new user profile feature",
            "intent": "IMPLEMENT",
            "keywords": ["feature", "user", "profile"],
        }

        intent, template_id = router.classify_intent_with_workflow_suggestion(context)

        assert intent == "IMPLEMENT"
        assert template_id == "tdd/feature-implementation"


# AC_COMPLETE: AC-PHASE100-004 ✅ 5/5 tests written (RED phase)
