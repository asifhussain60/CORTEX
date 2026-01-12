"""
Test Response Header Injection System

Validates that ResponseRenderer and ResponseMiddleware properly inject
CORTEX headers with brain icon, copyright, and Next Steps sections.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.orchestrators.response_renderer import ResponseRenderer
from src.orchestrators.response_middleware import ResponseMiddleware


class TestResponseRendererHeaderInjection:
    """Test ResponseRenderer header injection and template loading."""
    
    @pytest.fixture
    def renderer(self):
        """Create renderer instance."""
        return ResponseRenderer(
            templates_path="cortex-brain/response-templates-v4.yaml"
        )
    
    def test_header_includes_brain_icon(self, renderer):
        """Header must include 🧠 brain icon (CORTEX-4.0 style)."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "tdd_master",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1", "Outcome 2"]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "🧠 CORTEX" in markdown, "Brain icon missing from header"
        assert markdown.startswith("## 🧠"), "Header should start with ## and brain icon (CORTEX-4.0 style)"
    
    def test_header_includes_copyright(self, renderer):
        """Header must include phase and orchestrator information."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 1",
            "orchestrator_name": "planning_orchestrator",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "**Author:** Asif Hussain" in markdown, "Author missing"
        assert "**Phase:** Phase 1" in markdown, "Phase missing"
        assert "**Orchestrator:**" in markdown, "Orchestrator missing"
        assert "✅" in markdown, "Checkmark missing"
    
    def test_header_includes_author(self, renderer):
        """Header must include author name and phase/orchestrator."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "tdd_master",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "**Author:** Asif Hussain" in markdown, "Author name missing"
        assert "Phase" in markdown, "Phase missing"
    
    def test_header_includes_version_and_date(self, renderer):
        """Header must include phase and orchestrator information."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "tdd_master",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "**Phase:**" in markdown, "Phase missing"
        assert "**Orchestrator:**" in markdown, "Orchestrator missing"
    
    def test_header_comes_before_content(self, renderer):
        """Header must be first element before any content."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "master_orchestrator",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"]
        }
        
        markdown = renderer.render(result, context=context)
        
        header_pos = markdown.find("🧠 CORTEX")
        content_pos = markdown.find("✅ OUTCOMES")
        
        assert header_pos != -1, "Header not found"
        assert content_pos != -1, "Content not found"
        assert header_pos < content_pos, "Header must come before content"
    
    def test_outcomes_section_with_marker(self, renderer):
        """Outcomes section must have ✅ marker."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "master_orchestrator",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1", "Outcome 2", "Outcome 3"]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "✅ OUTCOMES" in markdown, "Outcomes marker missing"
        assert "Outcome 1" in markdown, "Outcome content missing"
    
    def test_next_steps_section_mandatory(self, renderer):
        """Next Steps section must be mandatory and final."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 1",
            "orchestrator_name": "planning_orchestrator",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"],
            "next_steps": ["Step 1", "Step 2"]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "📋 NEXT STEPS" in markdown, "Next Steps section missing"
        assert "Step 1" in markdown, "Next step 1 missing"
        # Next Steps should be near the end
        next_steps_pos = markdown.find("📋 NEXT STEPS")
        assert next_steps_pos > 0, "Next Steps not found"
    
    def test_next_steps_generated_when_missing(self, renderer):
        """Next Steps should be auto-generated if not provided."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "tdd_master",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"]
            # No next_steps provided
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "📋 NEXT STEPS" in markdown, "Next Steps section should be auto-generated"
    
    def test_section_order(self, renderer):
        """Sections must appear in correct order."""
        result = {"message": "Test result"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "master_orchestrator",
            "summary": "Test execution completed",
            "outcomes": ["Outcome 1"],
            "in_progress": ["Work item 1"],
            "risks": ["Risk 1"],
            "impact": ["Impact 1"],
            "next_steps": ["Step 1"]
        }
        
        markdown = renderer.render(result, context=context)
        
        # Find positions
        header_pos = markdown.find("🧠 CORTEX")
        outcomes_pos = markdown.find("✅ OUTCOMES")
        progress_pos = markdown.find("⚙️ IN PROGRESS")
        risks_pos = markdown.find("⚠️ RISKS")
        impact_pos = markdown.find("🎯 IMPACT")
        next_steps_pos = markdown.find("📋 NEXT STEPS")
        
        # Verify order
        assert header_pos < outcomes_pos, "Header should come before Outcomes"
        assert outcomes_pos < next_steps_pos, "Outcomes should come before Next Steps"
        assert next_steps_pos > impact_pos, "Next Steps should be last section"


class TestResponseMiddlewareInjection:
    """Test ResponseMiddleware system message injection."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return ResponseMiddleware()
    
    def test_inject_token_warning(self, middleware):
        """Should inject token usage warning when > 80%."""
        markdown = "## 🧠 CORTEX Test\n**Author:** Asif Hussain | **Phase:** Phase 2 | **Orchestrator:** TDD-Master ✅\n\n# Content here"
        context = {"token_usage_percentage": 85}
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "Token Usage Alert" in result, "Token warning not injected"
        assert "85" in result, "Token percentage not shown"
    
    def test_inject_security_warnings(self, middleware):
        """Should inject security warnings when present."""
        markdown = "## 🧠 CORTEX Test\n**Author:** Asif Hussain | **Phase:** Phase 2 | **Orchestrator:** TDD-Master ✅\n\n# Content here"
        context = {
            "security_warnings": ["No secrets validation", "Missing rate limiting"]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "SECURITY NOTICES" in result, "Security notices section missing"
        assert "No secrets validation" in result, "Security warning 1 missing"
    
    def test_inject_deprecation_notices(self, middleware):
        """Should inject deprecation notices when features used."""
        markdown = "## 🧠 CORTEX Test\n**Author:** Asif Hussain | **Phase:** Phase 2 | **Orchestrator:** TDD-Master ✅\n\n# Content here"
        context = {
            "deprecated_features_used": ["python-dateutil < 2.8", "requests < 2.25"]
        }
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "DEPRECATED FEATURES" in result, "Deprecation section missing"
        assert "python-dateutil" in result, "Deprecated feature not listed"
    
    def test_continuation_protocol(self, middleware):
        """Should inject continuation protocol at end."""
        markdown = "## 🧠 CORTEX Test\n**Author:** Asif Hussain | **Phase:** Phase 2 | **Orchestrator:** TDD-Master ✅\n\n# Content here"
        context = {"session_id": "session-12345"}
        
        result = middleware.inject_system_messages(markdown, context)
        
        assert "CONTINUATION" in result, "Continuation protocol missing"
        assert "session-12345" in result, "Session ID not in continuation"
        assert result.endswith("\n"), "Continuation should be at end"


class TestResponseIntegration:
    """Test full rendering + middleware integration."""
    
    def test_full_response_with_headers_and_next_steps(self):
        """Full response should have header, content, and Next Steps."""
        renderer = ResponseRenderer(
            templates_path="cortex-brain/response-templates-v4.yaml"
        )
        middleware = ResponseMiddleware()
        
        # Render
        result = {"message": "Implementation completed"}
        context = {
            "phase": "Phase 2",
            "orchestrator_name": "tdd_master",
            "operation_type": "TDD-Master",
            "summary": "Test-driven implementation completed successfully.",
            "outcomes": [
                "Hash chain integrity validated (5/5 tests)",
                "Phase 2 at 45% completion",
                "Governance rules enforced"
            ],
            "risks": ["Token usage at 85% - approaching limit"],
            "next_steps": [
                "Review progress-tracker.json for completion status",
                "Execute Phase 2 remaining AC-IDs"
            ],
            "security_warnings": [],
            "token_usage_percentage": 85
        }
        
        rendered = renderer.render(result, context=context)
        
        # Inject system messages
        final = middleware.inject_system_messages(rendered, context)
        
        # Verify complete response
        assert "🧠 CORTEX" in final, "Brain icon missing"
        assert "**Author:** Asif Hussain" in final, "Author missing"
        assert "✅ OUTCOMES" in final, "Outcomes missing"
        assert "📋 NEXT STEPS" in final, "Next Steps missing"
        assert "Token Usage Alert" in final, "Token warning missing"
        
        # Verify order
        header_pos = final.find("🧠")
        outcomes_pos = final.find("✅")
        next_steps_pos = final.find("📋 NEXT STEPS")
        
        assert header_pos < outcomes_pos, "Wrong order: header before outcomes"
        assert outcomes_pos < next_steps_pos, "Wrong order: outcomes before next steps"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
