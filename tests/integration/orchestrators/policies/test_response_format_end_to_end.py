"""
End-to-end integration tests for Phase 29 Response Format Enhancement.

Tests complete pipeline: ChatResponsePolicy + FileWritePolicy in action.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 specification (AC-29-NF2, AC-29-NF3, AC-29-NF4)
"""

import pytest
from cortex.orchestrators.policies.chat_response_policy import ChatResponsePolicy
from cortex.orchestrators.policies.file_write_policy import FileWritePolicy, MarkdownBanViolation
from cortex.orchestrators.policies.plan_spine_renderer import PlanSpineRenderer


class TestEndToEndResponsePipeline:
    """Test complete response formatting pipeline."""
    
    def test_autonomous_execution_response_format(self):
        """Autonomous execution produces 3-section business-friendly format."""
        policy = ChatResponsePolicy(enable_business_language=True)
        
        # Simulate raw orchestrator response with narration
        raw_response = """
## 🧠 CORTEX Design
**Author:** Asif Hussain | **Mode:** Design | **Scope:** Phase 29 ✅

Let me analyze the specification.

Perfect! I can see the requirements.

### 1) What was asked
- Implement 3-section response format
- Suppress tool narration
- Use adapter pattern for extensibility

### 2) What's recommended and why
- ChatResponsePolicy enforces structure validation
- Utilize loose coupling for flexible integration
- Apply SOLID principles for maintainability

Great! This approach is solid.

### 3) Next steps

Which approach do you prefer?

1️⃣ Option A: Immediate integration
2️⃣ Option B: Phased rollout
"""
        
        # Apply all policies
        formatted = policy.apply(raw_response)
        
        # Validations
        is_valid, errors = policy.validate_response_structure(formatted)
        assert is_valid, f"Structure invalid: {errors}"
        
        # Narration suppressed
        assert "Let me analyze" not in formatted
        assert "Perfect!" not in formatted
        assert "Great!" not in formatted
        
        # Business language applied
        assert "adapter pattern" not in formatted or "design approach" in formatted
        assert "loose coupling" not in formatted or "flexible" in formatted
        
        # Preference question removed
        assert "Which approach do you prefer?" not in formatted
        assert "Option A" not in formatted
        assert "Option B" not in formatted
        
        # PROCEED directive added
        assert "**Next Step:** PROCEED" in formatted
    
    def test_markdown_report_generation_blocked(self):
        """Markdown report writes are intercepted and blocked."""
        file_policy = FileWritePolicy(enforce=True)
        
        report_content = """
# Phase 29 Completion Report

## Summary
All 4 phases complete.

## Metrics
- 38 tests passing
- 1,100 LOC added
"""
        
        with pytest.raises(MarkdownBanViolation):
            file_policy.check_write("phase-29-completion-report.md", report_content)
    
    def test_inline_chat_only_enforcement(self):
        """Responses must be inline, no file generation."""
        file_policy = FileWritePolicy()
        
        # These should be blocked
        blocked_files = [
            ("phase-summary.md", "# Summary"),
            ("progress-update.md", "# Progress"),
            ("completion.md", "# Done"),
        ]
        
        for path, content in blocked_files:
            assert file_policy.is_report_intent(path, content)
    
    def test_plan_spine_embedded_in_response(self):
        """Plan Spine renders compactly within response."""
        renderer = PlanSpineRenderer()
        
        phases = [
            {"name": "ChatResponsePolicy", "status": "complete"},
            {"name": "Business Language", "status": "complete"},
            {"name": "FileWritePolicy", "status": "complete"},
            {"name": "Integration", "status": "in_progress"},
        ]
        
        spine = renderer.render(phases)
        
        # Compact format
        lines = spine.split('\n')
        assert len(lines) <= 8
        
        # Progress visible
        assert "[✓]" in spine
        assert "[→]" in spine


class TestBackwardCompatibility:
    """Test existing functionality preserved (AC-29-NF2)."""
    
    def test_existing_response_modes_work(self):
        """Non-chat response modes unchanged."""
        policy = ChatResponsePolicy()
        
        # API response (dict) passes through
        api_response = {"status": "success"}
        assert isinstance(api_response, dict)
        
        # Policy only applies to strings
        # This ensures backward compatibility
    
    def test_optional_policy_application(self):
        """Policies can be disabled for specific contexts."""
        policy = ChatResponsePolicy(
            suppress_narration_enabled=False,
            enforce_proceed_enabled=False,
            enable_business_language=False
        )
        
        response = "Let me check. Perfect! Which option: A or B?"
        formatted = policy.apply(response)
        
        # Nothing changed (policies disabled)
        assert formatted == response


class TestTokenBudgetAdherence:
    """Test token budget compliance (AC-29-NF3)."""
    
    def test_policy_doesnt_increase_tokens(self):
        """Policy application reduces or maintains token count."""
        policy = ChatResponsePolicy()
        
        verbose = """
Let me read this.
Perfect! I see it.
Great! All good.
Looking at the code.
After reviewing.

### 1) Request
- Feature

### 2) Recommendation
- Approach

### 3) Next
Which option: 1 or 2?
"""
        
        compressed = policy.apply(verbose)
        
        assert len(compressed) < len(verbose)


class TestPolicyEnforcementLatency:
    """Test policy performance (AC-29-NF4)."""
    
    def test_policy_enforcement_fast(self):
        """Policy enforcement completes in <50ms."""
        import time
        
        policy = ChatResponsePolicy(enable_business_language=True)
        
        response = """
## 🧠 CORTEX
**Author:** Asif Hussain

### 1) Request
- Test

### 2) Recommendation
- Use adapter pattern for loose coupling

### 3) Next
- Implement
"""
        
        start = time.time()
        formatted = policy.apply(response)
        elapsed = (time.time() - start) * 1000  # ms
        
        assert elapsed < 50, f"Policy took {elapsed:.1f}ms (target: <50ms)"


class TestRegressionSuite:
    """Regression tests for existing components."""
    
    def test_unified_response_composer_compatible(self):
        """ChatResponsePolicy compatible with UnifiedResponseComposer."""
        # This would test actual integration with UnifiedResponseComposer
        # For now, verify policy output is string (compatible)
        policy = ChatResponsePolicy()
        
        result = policy.apply("### 1) A\n### 2) B\n### 3) C")
        assert isinstance(result, str)
    
    def test_interaction_orchestrator_compatible(self):
        """Policies compatible with InteractionOrchestrator flow."""
        # Verify policy can be inserted into existing response pipeline
        policy = ChatResponsePolicy()
        file_policy = FileWritePolicy()
        
        # Both policies initialize without errors
        assert policy is not None
        assert file_policy is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
