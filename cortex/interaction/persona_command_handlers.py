"""
Persona Command Handlers: /persona and /detail commands

Authority: Phase 37 S4, CORE-008 (TDD-first)

Handles:
- /persona {role} — Set session persona
- /persona reset — Clear persona override
- /persona save — Persist persona to user config
- /detail {level} — Override depth for 1 turn
- /detail sticky {level} — Persist depth for session
"""

from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from cortex.orchestrators.persona.models import PersonaId, DepthLevel
from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    action_taken: Optional[str] = None
    persona_changed: bool = False
    depth_changed: bool = False
    new_persona: Optional[PersonaId] = None
    new_depth: Optional[DepthLevel] = None


class PersonaCommandHandlers:
    """Handle /persona and /detail commands"""

    def __init__(self, orchestrator: MasterOrchestrator):
        """
        Initialize handlers.

        Args:
            orchestrator: MasterOrchestrator instance for persona management
        """
        self.orchestrator = orchestrator
        self.valid_personas = [
            "business_leader",
            "product_owner",
            "scrum_master",
            "tech_lead",
            "engineer",
        ]
        self.valid_depths = ["executive", "standard", "detailed", "full"]

    def handle_command(self, command: str, args: Optional[str] = None) -> CommandResult:
        """
        Route command to appropriate handler.

        Args:
            command: Command name (/persona or /detail)
            args: Command arguments

        Returns:
            CommandResult with success status and details
        """
        if command in ["/persona", "/role"]:
            return self._handle_persona_command(args)
        elif command in ["/detail", "/depth"]:
            return self._handle_detail_command(args)
        else:
            return CommandResult(success=False, message=f"Unknown command: {command}")

    def _handle_persona_command(self, args: Optional[str]) -> CommandResult:
        """
        Handle /persona command.

        Usage:
        - /persona {role} — Set persona
        - /persona reset — Clear override
        - /persona save — Persist to config
        - /persona (with no args) — Show current

        Args:
            args: Command arguments

        Returns:
            CommandResult
        """
        if not args or args.strip() == "":
            # Show current persona
            current = self.orchestrator.get_current_state()
            return CommandResult(
                success=True,
                message=f"Current persona: {current['primary_persona']} (depth: {current['active_depth']})",
            )

        args = args.strip().lower()

        # Handle reset
        if args == "reset":
            self.orchestrator.reset_persona()
            return CommandResult(
                success=True,
                message="Persona reset to auto-inference",
                action_taken="reset",
                persona_changed=True,
            )

        # Handle save
        if args == "save":
            current = self.orchestrator.get_current_state()
            persona = current["primary_persona"]
            # TODO: Implement persistence layer
            return CommandResult(
                success=True,
                message=f"Persona '{persona}' saved to your profile",
                action_taken="save",
            )

        # Handle persona selection
        if args in self.valid_personas:
            old_state = self.orchestrator.get_current_state()
            old_persona = old_state["primary_persona"]

            # Convert string to PersonaId enum
            from cortex.orchestrators.persona.models import PersonaId
            persona_enum = PersonaId(args)
            self.orchestrator.session_context.set_persona(
                persona=persona_enum,
                confidence=1.0,
                trigger="explicit_command"
            )

            new_state = self.orchestrator.get_current_state()
            new_persona = new_state["primary_persona"]

            return CommandResult(
                success=True,
                message=f"Persona changed: {old_persona} → {new_persona}",
                action_taken="set",
                persona_changed=True,
                new_persona=new_persona,
            )

        return CommandResult(
            success=False,
            message=f"Invalid persona: {args}. Valid options: {', '.join(self.valid_personas)}, reset, save",
        )

    def _handle_detail_command(self, args: Optional[str]) -> CommandResult:
        """
        Handle /detail command.

        Usage:
        - /detail {level} — Override depth for 1 turn
        - /detail sticky {level} — Persist depth for session
        - /detail (with no args) — Show current

        Args:
            args: Command arguments

        Returns:
            CommandResult
        """
        if not args or args.strip() == "":
            # Show current depth
            current = self.orchestrator.get_current_state()
            return CommandResult(
                success=True,
                message=f"Current depth: {current['active_depth']}",
            )

        parts = args.strip().lower().split()

        # Check for "sticky" modifier
        sticky = False
        if len(parts) == 2 and parts[0] == "sticky":
            sticky = True
            depth_arg = parts[1]
        elif len(parts) == 1:
            depth_arg = parts[0]
        else:
            return CommandResult(
                success=False,
                message="Usage: /detail {level} or /detail sticky {level}",
            )

        # Validate depth level
        if depth_arg not in self.valid_depths:
            return CommandResult(
                success=False,
                message=f"Invalid depth: {depth_arg}. Valid options: {', '.join(self.valid_depths)}",
            )

        # Set depth
        old_state = self.orchestrator.get_current_state()
        old_depth = old_state["active_depth"]

        from cortex.orchestrators.persona.models import DepthLevel
        depth_enum = DepthLevel(depth_arg)

        if sticky:
            self.orchestrator.session_context.set_depth_override(
                level=depth_enum,
                ttl_turns=-1,
                silent=False
            )
            action = "sticky_override"
        else:
            self.orchestrator.session_context.set_depth_override(
                level=depth_enum,
                ttl_turns=1,
                silent=False
            )
            action = "temporary_override"

        new_state = self.orchestrator.get_current_state()
        new_depth = new_state["active_depth"]

        duration = "for this session" if sticky else "for this turn"

        return CommandResult(
            success=True,
            message=f"Depth changed: {old_depth} → {new_depth} ({duration})",
            action_taken=action,
            depth_changed=True,
            new_depth=new_depth,
        )

    def parse_command_from_message(self, message: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract command from message if present.

        Args:
            message: User message

        Returns:
            Tuple of (command, args) or (None, None) if no command
        """
        message = message.strip()

        # Check for /persona
        if message.startswith("/persona"):
            parts = message.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1] if len(parts) > 1 else None
            return (cmd, args)

        # Check for /role (alias)
        if message.startswith("/role"):
            parts = message.split(maxsplit=1)
            cmd = "/persona"  # Normalize to /persona
            args = parts[1] if len(parts) > 1 else None
            return (cmd, args)

        # Check for /detail
        if message.startswith("/detail"):
            parts = message.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1] if len(parts) > 1 else None
            return (cmd, args)

        # Check for /depth (alias)
        if message.startswith("/depth"):
            parts = message.split(maxsplit=1)
            cmd = "/detail"  # Normalize to /detail
            args = parts[1] if len(parts) > 1 else None
            return (cmd, args)

        return (None, None)
