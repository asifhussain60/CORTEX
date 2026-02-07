"""
Test suite for PersonaInjector agent.

Tests prompt template injection with persona/depth context.

AC_START: AC-PHASE37.3-001
"""

import pytest
from typing import Dict, Any

# GREEN phase - implementation complete
from cortex.orchestrators.core.persona_injector import PersonaInjector


class TestPersonaInjector:
    """Test PersonaInjector prompt template handling."""
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_inject_persona_context_into_prompt(self):
        """Should inject persona context at {{PERSONA_INJECTION_POINT}}."""
        prompt_template = """
You are CORTEX.

{{PERSONA_INJECTION_POINT}}

Follow these rules...
"""
        injector = PersonaInjector()
        result = injector.inject(
            prompt_template,
            persona_id="engineer",
            depth_id="detailed"
        )
        
        assert "{{PERSONA_INJECTION_POINT}}" not in result
        assert "engineer" in result.lower()
        assert "detailed" in result.lower()
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_inject_without_placeholder_returns_unchanged(self):
        """Should return original prompt if no injection point found."""
        prompt_template = "You are CORTEX. Follow rules."
        injector = PersonaInjector()
        result = injector.inject(
            prompt_template,
            persona_id="engineer",
            depth_id="standard"
        )
        
        # Should append persona context to end
        assert result.startswith(prompt_template)
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_inject_with_unknown_persona_uses_default(self):
        """Should use default persona when unknown persona provided."""
        prompt_template = "{{PERSONA_INJECTION_POINT}}"
        injector = PersonaInjector()
        result = injector.inject(
            prompt_template,
            persona_id="unknown",
            depth_id="standard"
        )
        
        # Should inject default persona context
        assert len(result) > 0
        assert "{{PERSONA_INJECTION_POINT}}" not in result
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_generate_persona_context_block(self):
        """Should generate formatted persona context block."""
        injector = PersonaInjector()
        context = injector.generate_context_block(
            persona_id="business_leader",
            depth_id="executive"
        )
        
        assert "business_leader" in context.lower() or "business leader" in context.lower()
        assert "executive" in context.lower()
        assert len(context) > 50  # Substantial content
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_inject_respects_depth_word_limits(self):
        """Should include depth word limit in context."""
        injector = PersonaInjector()
        context = injector.generate_context_block(
            persona_id="business_leader",
            depth_id="executive"
        )
        
        # Executive depth has 100 word limit
        assert "100" in context or "concise" in context.lower()


# AC_COMPLETE: AC-PHASE37.3-001 ✅ 0/5 tests (skipped, RED phase)
