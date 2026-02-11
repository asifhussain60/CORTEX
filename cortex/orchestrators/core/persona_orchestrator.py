"""
PersonaOrchestrator - Main coordinator for persona workflow.

Integrates all persona components: inference → styling → injection → commands.

AC_START: AC-PHASE37.4-002
"""

import json
from typing import Any, Dict, List, Optional

from cortex.orchestrators.core.depth_manager import DepthManager
from cortex.orchestrators.core.persona_commands import (
    DetailCommandHandler,
    PersonaCommandHandler,
)
from cortex.orchestrators.core.persona_injector import PersonaInjector
from cortex.orchestrators.core.persona_loader import PersonaLoader
from cortex.orchestrators.core.response_styler import ResponseStyler
from cortex.orchestrators.core.role_resolver import RoleResolver


class PersonaOrchestrator:
    """Main coordinator for persona system."""

    def __init__(self):
        """Initialize persona orchestrator."""
        # Component initialization
        self.role_resolver = RoleResolver()
        self.persona_loader = PersonaLoader()
        self.depth_manager = DepthManager()
        self.response_styler = ResponseStyler()
        self.persona_injector = PersonaInjector()

        # Command handlers - pass shared managers
        self.persona_command_handler = PersonaCommandHandler()
        self.detail_command_handler = DetailCommandHandler()

        # Override handlers' managers with orchestrator's managers
        self.persona_command_handler.persona_loader = self.persona_loader
        self.detail_command_handler.persona_loader = self.persona_loader
        self.detail_command_handler.depth_manager = self.depth_manager

        # Session state
        self._explicit_persona: Optional[str] = None  # User-set persona
        self._inferred_persona: Optional[str] = None  # Auto-inferred
        self._current_depth: Optional[str] = None

    def process_request(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process request through complete persona workflow.

        Args:
            query: User query
            context: Optional context dict with signals for inference

        Returns:
            Result dict with persona_id, depth_id, styled_response, injected_prompt
        """
        context = context or {}
        context["query"] = query

        # Determine active persona
        if self._explicit_persona:
            # User explicitly set persona - use it
            persona_id = self._explicit_persona
            confidence = 1.0
            inference_used = False
        else:
            # No explicit persona - infer from context
            inference_result = self.role_resolver.infer_persona(context)
            persona_id = inference_result.persona_id
            confidence = inference_result.confidence
            inference_used = True
            self._inferred_persona = persona_id

        # Determine active depth
        depth_override = self.depth_manager.get_current_depth()
        if depth_override:
            depth_id = depth_override
        else:
            # Use persona default
            persona = self.persona_loader.get_persona(persona_id)
            depth_id = persona.depth if persona and persona.depth else "standard"
            self.depth_manager.set_persona_default(depth_id)

        self._current_depth = depth_id

        # Build result
        result = {
            "persona_id": persona_id,
            "depth_id": depth_id,
            "confidence": confidence,
            "inference_used": inference_used
        }

        return result

    def style_response(
        self,
        response: str,
        available_metrics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Apply persona-based styling to response.

        Args:
            response: Raw response text
            available_metrics: Optional metrics dictionary

        Returns:
            Styled response
        """
        state = self.get_current_state()
        persona_id = state["persona_id"]
        depth_id = state["depth_id"]

        # Get effective word limit from depth (overrides persona default)
        depth = self.persona_loader.get_depth_level(depth_id)
        persona = self.persona_loader.get_persona(persona_id)

        if depth and persona:
            # Create a modified persona with depth word limit
            import copy
            styled_persona = copy.copy(persona)
            styled_persona.word_limit = depth.word_limit

            # Unfortunately ResponseStyler uses persona_id string, not object
            # So we need to modify the persona object in-place temporarily
            original_limit = persona.word_limit
            persona.word_limit = depth.word_limit

            styled = self.response_styler.apply_style(
                response,
                persona_id,
                available_metrics
            )

            # Restore
            persona.word_limit = original_limit
            return styled

        return self.response_styler.apply_style(
            response,
            persona_id,
            available_metrics
        )

    def inject_persona_context(self, prompt_template: str) -> str:
        """Inject persona context into prompt template.

        Args:
            prompt_template: Prompt with optional {{PERSONA_INJECTION_POINT}}

        Returns:
            Prompt with persona context injected
        """
        state = self.get_current_state()

        return self.persona_injector.inject(
            prompt_template,
            state["persona_id"],
            state["depth_id"]
        )

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute /persona or /detail command.

        Args:
            command: Full command string

        Returns:
            Result dictionary
        """
        if command.startswith("/persona"):
            result = self.persona_command_handler.execute(command)

            # Update state if successful
            if result["success"] and "persona_id" in result:
                self._explicit_persona = result["persona_id"]

                # Reset depth to new persona's default
                persona = self.persona_loader.get_persona(result["persona_id"])
                if persona and persona.depth:
                    self.depth_manager.clear_override()
                    self.depth_manager.set_persona_default(persona.depth)
                    self._current_depth = persona.depth

            return result

        elif command.startswith("/detail"):
            result = self.detail_command_handler.execute(command)

            # Update state if successful
            if result["success"] and "depth_id" in result:
                self._current_depth = result["depth_id"]

            return result

        else:
            return {
                "success": False,
                "message": f"Unknown command: {command}"
            }

    def get_current_state(self) -> Dict[str, Any]:
        """Get current persona/depth state.

        Returns:
            State dictionary with persona_id, depth_id, etc.
        """
        # Determine active persona
        if self._explicit_persona:
            persona_id = self._explicit_persona
        elif self._inferred_persona:
            persona_id = self._inferred_persona
        else:
            persona_id = "engineer"  # Default

        # Determine active depth (check override first)
        depth_override = self.depth_manager.get_current_depth()
        if depth_override:
            depth_id = depth_override
        elif self._current_depth:
            depth_id = self._current_depth
        else:
            persona = self.persona_loader.get_persona(persona_id)
            depth_id = persona.depth if persona and persona.depth else "standard"

        # Get persona default depth for reference
        persona = self.persona_loader.get_persona(persona_id)
        persona_default_depth = persona.depth if persona and persona.depth else "standard"

        return {
            "persona_id": persona_id,
            "depth_id": depth_id,
            "persona_default_depth": persona_default_depth,
            "explicit_persona": self._explicit_persona is not None
        }

    def consume_turn(self) -> None:
        """Consume a turn (decrement depth TTL if active)."""
        self.depth_manager.consume_turn()

        # Update current depth if override expired
        override = self.depth_manager.get_current_depth()
        if override:
            self._current_depth = override
        else:
            # Revert to persona default
            state = self.get_current_state()
            persona = self.persona_loader.get_persona(state["persona_id"])
            if persona:
                self._current_depth = persona.depth

    def serialize_state(self) -> str:
        """Serialize session state to JSON.

        Returns:
            JSON string of state
        """
        state = {
            "explicit_persona": self._explicit_persona,
            "inferred_persona": self._inferred_persona,
            "current_depth": self._current_depth,
            "depth_override": None
        }

        # Serialize depth override if active
        override = self.depth_manager.get_override()
        if override:
            state["depth_override"] = {
                "depth_id": override.depth_id,
                "turns_remaining": override.turns_remaining,
                "sticky": override.sticky
            }

        return json.dumps(state)

    def restore_state(self, serialized: str) -> None:
        """Restore session state from JSON.

        Args:
            serialized: JSON string of state
        """
        state = json.loads(serialized)

        self._explicit_persona = state.get("explicit_persona")
        self._inferred_persona = state.get("inferred_persona")
        self._current_depth = state.get("current_depth")

        # Restore depth override if present
        depth_override = state.get("depth_override")
        if depth_override:
            self.depth_manager.set_override(
                depth_override["depth_id"],
                turns=depth_override["turns_remaining"],
                sticky=depth_override["sticky"]
            )


# AC_COMPLETE: AC-PHASE37.4-002 ✅ PersonaOrchestrator implemented
