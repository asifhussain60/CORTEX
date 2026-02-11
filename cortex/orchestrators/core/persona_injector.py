"""
PersonaInjector agent for prompt template injection.

Injects persona/depth context into prompt templates at {{PERSONA_INJECTION_POINT}}.

AC_START: AC-PHASE37.3-003
"""

from typing import Optional

from cortex.orchestrators.core.persona_loader import PersonaLoader


class PersonaInjector:
    """Inject persona context into prompt templates."""

    INJECTION_MARKER = "{{PERSONA_INJECTION_POINT}}"

    def __init__(self):
        """Initialize persona injector."""
        self.persona_loader = PersonaLoader()

    def inject(
        self,
        prompt_template: str,
        persona_id: str,
        depth_id: str
    ) -> str:
        """Inject persona context into prompt template.

        Args:
            prompt_template: Prompt template with optional {{PERSONA_INJECTION_POINT}}
            persona_id: Persona ID
            depth_id: Depth level ID

        Returns:
            Prompt with persona context injected
        """
        context_block = self.generate_context_block(persona_id, depth_id)

        if self.INJECTION_MARKER in prompt_template:
            # Replace marker with context
            return prompt_template.replace(self.INJECTION_MARKER, context_block)
        else:
            # Append to end if no marker
            return prompt_template + "\n\n" + context_block

    def generate_context_block(
        self,
        persona_id: str,
        depth_id: str
    ) -> str:
        """Generate formatted persona context block.

        Args:
            persona_id: Persona ID
            depth_id: Depth level ID

        Returns:
            Formatted context block
        """
        # Load persona and depth
        persona = self.persona_loader.get_persona(persona_id)
        depth = self.persona_loader.get_depth_level(depth_id)

        # Use default if unknown
        if not persona:
            persona = self.persona_loader.get_persona("engineer")  # Default
        if not depth:
            depth = self.persona_loader.get_depth_level("standard")  # Default

        # Generate context block
        context = f"""
### 🎭 Active Persona: {persona.id.replace('_', ' ').title()}

**Response Format:** {persona.format}
**Detail Level:** {depth.id.title()} ({depth.word_limit or 300} words max)
**Code Blocks:** {"Shown" if persona.show_code else "Hidden"}
**Metrics:** {", ".join(persona.metric_types) if persona.show_metrics else "None"}

**Guidance:**
- Keep responses {"concise and executive-level" if (depth.word_limit or 300) <= 150 else "detailed and comprehensive" if (depth.word_limit or 300) >= 500 else "balanced with key details"}
- {"Focus on business impact and ROI" if persona.id == "business_leader" else "Focus on user value and features" if persona.id == "product_owner" else "Focus on technical implementation" if persona.id == "engineer" else "Focus on architecture and design" if persona.id == "tech_lead" else "Focus on process and workflow"}
- Word limit: {depth.word_limit or 300} words (strict enforcement)
""".strip()

        return context


# AC_COMPLETE: AC-PHASE37.3-003 ✅ PersonaInjector implemented
