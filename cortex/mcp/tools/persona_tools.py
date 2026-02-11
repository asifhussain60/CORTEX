"""
MCP Tools for Persona System

Authority: Phase 37 S4
Exposes persona management via MCP interface
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from cortex.interaction.persona_store import PersonaStore
from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.persona.models import DepthLevel, PersonaId


class PersonaSetResult:
    """Result of setting a persona"""

    def __init__(
        self,
        success: bool,
        persona: Optional[str] = None,
        depth: Optional[str] = None,
        previous_persona: Optional[str] = None,
        message: str = "",
    ):
        self.success = success
        self.persona = persona
        self.depth = depth
        self.previous_persona = previous_persona
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "persona": self.persona,
            "depth": self.depth,
            "previous_persona": self.previous_persona,
            "message": self.message,
        }


class PersonaState:
    """Current persona state"""

    def __init__(
        self,
        user_id: str,
        current_persona: str,
        current_depth: str,
        available_personas: List[str],
        available_depths: List[str],
        has_active_override: bool = False,
        override_level: Optional[str] = None,
        override_expires_at: Optional[str] = None,
    ):
        self.user_id = user_id
        self.current_persona = current_persona
        self.current_depth = current_depth
        self.available_personas = available_personas
        self.available_depths = available_depths
        self.has_active_override = has_active_override
        self.override_level = override_level
        self.override_expires_at = override_expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "current_persona": self.current_persona,
            "current_depth": self.current_depth,
            "available_personas": self.available_personas,
            "available_depths": self.available_depths,
            "has_active_override": self.has_active_override,
            "override_level": self.override_level,
            "override_expires_at": self.override_expires_at,
        }


class DepthSetResult:
    """Result of setting depth level"""

    def __init__(
        self,
        success: bool,
        depth: Optional[str] = None,
        previous_depth: Optional[str] = None,
        is_override: bool = False,
        message: str = "",
    ):
        self.success = success
        self.depth = depth
        self.previous_depth = previous_depth
        self.is_override = is_override
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "depth": self.depth,
            "previous_depth": self.previous_depth,
            "is_override": self.is_override,
            "message": self.message,
        }


class InferenceResult:
    """Result of persona inference"""

    def __init__(
        self,
        inferred_persona: str,
        confidence: float,
        reasoning: str,
        signals_detected: List[str],
    ):
        self.inferred_persona = inferred_persona
        self.confidence = confidence
        self.reasoning = reasoning
        self.signals_detected = signals_detected

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inferred_persona": self.inferred_persona,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "signals_detected": self.signals_detected,
        }


class PersonaHistory:
    """User's persona history"""

    def __init__(
        self,
        user_id: str,
        entries: List[Dict[str, Any]],
        total_switches: int,
    ):
        self.user_id = user_id
        self.entries = entries
        self.total_switches = total_switches

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "entries": self.entries,
            "total_switches": self.total_switches,
        }


class PersonaTools:
    """MCP tools for persona management"""

    def __init__(self, master_orchestrator: MasterOrchestrator):
        """
        Initialize PersonaTools.

        Args:
            master_orchestrator: MasterOrchestrator instance for persona operations
        """
        self.orchestrator = master_orchestrator
        self.store = PersonaStore()

    def cortex_set_persona(
        self,
        user_id: str,
        persona: str,
    ) -> PersonaSetResult:
        """
        Set persona for user.

        Args:
            user_id: User identifier
            persona: Persona name (BUSINESS_LEADER, PRODUCT_OWNER, etc.)

        Returns:
            PersonaSetResult with success status and details
        """
        try:
            # Validate persona
            try:
                persona_enum = PersonaId[persona.upper()]
            except KeyError:
                return PersonaSetResult(
                    success=False,
                    message=f"Invalid persona: {persona}",
                )

            # Get current state
            current_state = self.orchestrator.get_current_state()
            previous_persona = current_state.get("persona") if current_state else None

            # Set persona via orchestrator
            self.orchestrator.switch_persona(persona_enum, user_id)

            # Store preference
            current_depth_str = current_state.get("depth", "STANDARD") if current_state else "STANDARD"
            current_depth = DepthLevel[current_depth_str.upper()]
            self.store.update_user_persona(user_id, persona_enum, current_depth)

            return PersonaSetResult(
                success=True,
                persona=persona,
                depth=current_depth.value,
                previous_persona=previous_persona,
                message=f"Persona set to {persona}",
            )
        except Exception as e:
            return PersonaSetResult(
                success=False,
                message=f"Error setting persona: {str(e)}",
            )

    def cortex_get_persona(self, user_id: str) -> PersonaState:
        """
        Get current persona state for user.

        Args:
            user_id: User identifier

        Returns:
            PersonaState with current settings and available options
        """
        try:
            # Get from orchestrator
            state = self.orchestrator.get_current_state()

            if not state:
                # Default state
                return PersonaState(
                    user_id=user_id,
                    current_persona="ENGINEER",
                    current_depth="STANDARD",
                    available_personas=[p.value for p in PersonaId],
                    available_depths=[d.value for d in DepthLevel],
                )

            # Get stored preferences
            stored = self.store.get_user_persona(user_id)

            # Check for active overrides
            overrides = self.store.get_active_overrides(user_id)
            has_override = len(overrides) > 0
            override_level = overrides[-1]["level"] if has_override else None

            return PersonaState(
                user_id=user_id,
                current_persona=state.get("persona", "ENGINEER"),
                current_depth=state.get("depth", "STANDARD"),
                available_personas=[p.value for p in PersonaId],
                available_depths=[d.value for d in DepthLevel],
                has_active_override=has_override,
                override_level=override_level,
            )
        except Exception:
            # Return default on error
            return PersonaState(
                user_id=user_id,
                current_persona="ENGINEER",
                current_depth="STANDARD",
                available_personas=[p.value for p in PersonaId],
                available_depths=[d.value for d in DepthLevel],
            )

    def cortex_set_depth(
        self,
        user_id: str,
        depth: str,
        is_override: bool = False,
        context: Optional[str] = None,
    ) -> DepthSetResult:
        """
        Set depth level for user.

        Args:
            user_id: User identifier
            depth: Depth level (EXECUTIVE, STANDARD, DETAILED, FULL)
            is_override: Whether this is a single-turn override
            context: Optional context for override

        Returns:
            DepthSetResult with success status
        """
        try:
            # Validate depth
            try:
                depth_enum = DepthLevel[depth.upper()]
            except KeyError:
                return DepthSetResult(
                    success=False,
                    message=f"Invalid depth: {depth}",
                )

            # Get current state
            current_state = self.orchestrator.get_current_state()
            previous_depth = current_state.get("depth") if current_state else "STANDARD"

            # Set via orchestrator
            self.orchestrator.set_depth(depth_enum)

            if is_override:
                # Add override to store
                self.store.add_depth_override(user_id, depth_enum, context)
            else:
                # Update permanent preference
                persona_str = current_state.get("persona", "ENGINEER") if current_state else "ENGINEER"
                persona_enum = PersonaId[persona_str.upper()]
                self.store.update_user_persona(user_id, persona_enum, depth_enum)

            return DepthSetResult(
                success=True,
                depth=depth,
                previous_depth=previous_depth,
                is_override=is_override,
                message=f"Depth set to {depth}" + (" (override)" if is_override else ""),
            )
        except Exception as e:
            return DepthSetResult(
                success=False,
                message=f"Error setting depth: {str(e)}",
            )

    def cortex_infer_persona(
        self,
        context: Optional[str] = None,
        user_input: Optional[str] = None,
    ) -> InferenceResult:
        """
        Infer persona from context and input.

        Args:
            context: Conversation context
            user_input: User's current input

        Returns:
            InferenceResult with inferred persona and confidence
        """
        try:
            # Call role resolver for inference
            result = self.orchestrator.infer_role(context, user_input)

            return InferenceResult(
                inferred_persona=result.get("persona", "ENGINEER"),
                confidence=result.get("confidence", 0.0),
                reasoning=result.get("reasoning", ""),
                signals_detected=result.get("signals", []),
            )
        except Exception as e:
            return InferenceResult(
                inferred_persona="ENGINEER",
                confidence=0.0,
                reasoning=f"Error during inference: {str(e)}",
                signals_detected=[],
            )

    def cortex_persona_history(
        self,
        user_id: str,
        limit: Optional[int] = None,
    ) -> PersonaHistory:
        """
        Get user's persona switch history.

        Args:
            user_id: User identifier
            limit: Max entries to return

        Returns:
            PersonaHistory with switch records
        """
        try:
            # Get history from orchestrator
            history = self.orchestrator.get_switch_history(user_id)

            if limit:
                history = history[:limit]

            # Count total switches
            total_switches = len(self.orchestrator.get_switch_history(user_id))

            return PersonaHistory(
                user_id=user_id,
                entries=history,
                total_switches=total_switches,
            )
        except Exception:
            return PersonaHistory(
                user_id=user_id,
                entries=[],
                total_switches=0,
            )
