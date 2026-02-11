"""
MasterOrchestrator: Coordinate RoleResolver → PersonaInjector pipeline

Authority: Phase 37 S3, CORE-008 (TDD-first)

Orchestrates:
- Role detection via RoleResolver
- Persona injection via PersonaInjector
- Session state management via SessionContext
- Natural language depth triggers
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from cortex.orchestrators.persona.models import DepthLevel, PersonaId
from cortex.orchestrators.persona.persona_injector import PersonaInjector
from cortex.orchestrators.persona.role_resolver import RoleResolver
from cortex.orchestrators.persona.session_context import SessionContext


@dataclass
class PersonaResult:
    """Result of persona processing"""
    detected_persona: PersonaId
    confidence: float = 0.0
    active_depth: DepthLevel = DepthLevel.STANDARD
    formatted_response: str = ""
    format_rules_applied: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.format_rules_applied is None:
            self.format_rules_applied = []


class MasterOrchestrator:
    """
    Coordinate RoleResolver → PersonaInjector pipeline.

    Flow:
    1. Message arrives
    2. RoleResolver detects persona + confidence
    3. SessionContext updates persona state
    4. PersonaInjector formats response per persona + depth
    5. PersonaResult returned with formatted output

    Attributes:
        session_context: SessionContext managing in-session state
        role_resolver: RoleResolver for persona detection
        persona_injector: PersonaInjector for response formatting
    """

    # Natural language depth triggers
    NL_DEPTH_TRIGGERS = {
        DepthLevel.EXECUTIVE: [
            r'\b(give\s+me\s+the\s+bluf|bluf|executive\s+summary|tldr|summarize)',
            r'\b(high\s+level|high.level|overview)',
        ],
        DepthLevel.DETAILED: [
            r'\b(technical\s+details|architecture|internals)',
            r'\b(how\s+does\s+this\s+work|explain\s+how)',
        ],
        DepthLevel.FULL: [
            r'\b(show\s+me\s+the\s+code|full\s+code|implementation)',
            r'\b(detailed\s+code|all\s+the\s+code)',
        ],
    }

    def __init__(
        self,
        session_context: SessionContext,
        role_resolver: RoleResolver,
        persona_injector: PersonaInjector
    ):
        """
        Initialize MasterOrchestrator.

        Args:
            session_context: SessionContext managing in-session state
            role_resolver: RoleResolver for persona detection
            persona_injector: PersonaInjector for response formatting
        """
        self.session_context = session_context
        self.role_resolver = role_resolver
        self.persona_injector = persona_injector

    def process(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        response_to_format: Optional[str] = None
    ) -> PersonaResult:
        """
        Process message and return formatted result.

        Args:
            message: User message to process
            context: Optional context dict with additional signals
            response_to_format: Optional pre-generated response to format

        Returns:
            PersonaResult with detected persona and formatted output
        """
        if context is None:
            context = {}

        # Step 1: Detect persona from message + context
        detected_persona, confidence = self.role_resolver.infer_role(
            message=message,
            context=context
        )

        # Step 2: Update session state
        self.session_context.set_persona(
            persona=detected_persona,
            confidence=confidence,
            trigger="message_analysis"
        )

        # Step 3: Check for depth overrides in message or context
        active_depth = self._detect_depth_override(message, context)
        if active_depth != self.session_context.get_active_depth():
            self.session_context.set_depth_override(
                active_depth,
                ttl_turns=1 if context.get('depth_override') else 1
            )

        # Step 4: Get current active depth
        final_depth = self.session_context.get_active_depth()

        # Step 5: Format response if provided
        formatted_response = ""
        format_rules_applied = []

        if response_to_format:
            formatted_response = self.persona_injector.format_response(
                response=response_to_format,
                persona=detected_persona,
                depth=final_depth
            )
            # Track that formatting was applied
            format_rules_applied = ["code_filtered", "metrics_filtered", "word_limited"]

        # Step 6: Advance turn counter
        self.session_context.advance_turn()

        return PersonaResult(
            detected_persona=detected_persona,
            confidence=confidence,
            active_depth=final_depth,
            formatted_response=formatted_response,
            format_rules_applied=format_rules_applied
        )

    def _detect_depth_override(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> DepthLevel:
        """
        Detect depth override from natural language or context.

        Args:
            message: User message
            context: Context dict that may contain depth_override

        Returns:
            DepthLevel if override detected, else current depth
        """
        import re

        # Check context first
        if 'depth_override' in context:
            depth_str = context['depth_override']
            try:
                return DepthLevel(depth_str.lower())
            except ValueError:
                pass

        # Check natural language triggers
        message_lower = message.lower()

        for depth, patterns in self.NL_DEPTH_TRIGGERS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return depth

        # No override detected
        return self.session_context.get_active_depth()

    def get_switch_history(self) -> List[Dict[str, Any]]:
        """
        Get persona switch history.

        Returns:
            List of persona switches
        """
        return self.session_context.get_switch_history()

    def reset_persona(self) -> None:
        """Reset persona to UNKNOWN"""
        self.session_context.reset()

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current session state.

        Returns:
            Dict with current state
        """
        return self.session_context.get_state_dict()
