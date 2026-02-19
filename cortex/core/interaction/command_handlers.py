"""
Command Handlers for Persona System

Authority: Phase 37 S5
Implements /persona and /detail command handlers
"""

from typing import Any, Dict, Optional, Tuple

from cortex.interaction.persona_store import PersonaStore
from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.persona.models import DepthLevel, PersonaId


class CommandParseResult:
    """Result of command parsing"""

    def __init__(
        self,
        success: bool,
        command: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.command = command
        self.args = args or {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "command": self.command,
            "args": self.args,
            "error": self.error,
        }


class CommandResponse:
    """Response from command execution"""

    def __init__(
        self,
        success: bool,
        message: str = "",
        state: Optional[Dict[str, Any]] = None,
        next_action: Optional[str] = None,
    ):
        self.success = success
        self.message = message
        self.state = state or {}
        self.next_action = next_action

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "state": self.state,
            "next_action": self.next_action,
        }


class CommandParser:
    """Parse and validate user commands"""

    def __init__(self):
        """Initialize CommandParser"""
        self.valid_personas = [p.value for p in PersonaId]
        self.valid_depths = [d.value for d in DepthLevel]

    def parse_persona_command(self, user_input: str) -> CommandParseResult:
        """
        Parse /persona command.

        Syntax:
        - /persona engineer
        - /persona tech_lead
        - /persona business_leader

        Args:
            user_input: Full user input

        Returns:
            CommandParseResult with parsed arguments
        """
        parts = user_input.strip().split()

        if len(parts) < 2:
            return CommandParseResult(
                success=False,
                error="Usage: /persona {role}",
            )

        persona_arg = parts[1].upper()

        # Validate persona
        try:
            persona_enum = PersonaId[persona_arg]
        except KeyError:
            # Try with underscore conversion
            persona_arg_normalized = persona_arg.replace("-", "_")
            try:
                persona_enum = PersonaId[persona_arg_normalized]
            except KeyError:
                return CommandParseResult(
                    success=False,
                    error=f"Unknown persona: {parts[1]}. Valid: {', '.join(self.valid_personas)}",
                )

        return CommandParseResult(
            success=True,
            command="persona",
            args={"persona": persona_enum.value},
        )

    def parse_detail_command(self, user_input: str) -> CommandParseResult:
        """
        Parse /detail command.

        Syntax:
        - /detail executive
        - /detail standard
        - /detail detailed
        - /detail full
        - /detail sticky detailed
        - /detail sticky full

        Args:
            user_input: Full user input

        Returns:
            CommandParseResult with parsed arguments
        """
        parts = user_input.strip().split()

        if len(parts) < 2:
            return CommandParseResult(
                success=False,
                error="Usage: /detail {level} or /detail sticky {level}",
            )

        sticky = False
        depth_idx = 1

        # Check for sticky modifier
        if parts[1].lower() == "sticky":
            sticky = True
            depth_idx = 2

            if len(parts) < 3:
                return CommandParseResult(
                    success=False,
                    error="Usage: /detail sticky {level}",
                )

        depth_arg = parts[depth_idx].upper()

        # Validate depth
        try:
            depth_enum = DepthLevel[depth_arg]
        except KeyError:
            return CommandParseResult(
                success=False,
                error=f"Unknown depth: {parts[depth_idx]}. Valid: {', '.join(self.valid_depths)}",
            )

        return CommandParseResult(
            success=True,
            command="detail",
            args={
                "depth": depth_enum.value,
                "sticky": sticky,
            },
        )


class PersonaCommandHandler:
    """Handle /persona commands"""

    def __init__(
        self,
        orchestrator: MasterOrchestrator,
        store: Optional[PersonaStore] = None,
    ):
        """
        Initialize PersonaCommandHandler.

        Args:
            orchestrator: MasterOrchestrator instance
            store: Optional PersonaStore for persistence
        """
        self.orchestrator = orchestrator
        self.store = store or PersonaStore()
        self.parser = CommandParser()

    def handle(
        self,
        user_input: str,
        user_id: str,
    ) -> CommandResponse:
        """
        Handle /persona command.

        Args:
            user_input: Full command line
            user_id: User identifier

        Returns:
            CommandResponse with result
        """
        # Parse command
        parse_result = self.parser.parse_persona_command(user_input)

        if not parse_result.success:
            return CommandResponse(
                success=False,
                message=parse_result.error,
            )

        try:
            # Extract persona
            persona_str = parse_result.args["persona"]
            persona_enum = PersonaId[persona_str.upper()]

            # Get current depth
            current_state = self.orchestrator.get_current_state()
            depth_str = current_state.get("depth", "STANDARD") if current_state else "STANDARD"
            depth_enum = DepthLevel[depth_str.upper()]

            # Switch persona
            self.orchestrator.switch_persona(persona_enum, user_id)

            # Save preference
            self.store.update_user_persona(user_id, persona_enum, depth_enum)

            # Get new state
            new_state = self.orchestrator.get_current_state()

            return CommandResponse(
                success=True,
                message=f"✅ Persona set to {persona_enum.value}",
                state=new_state,
                next_action="continue_conversation",
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                message=f"Error setting persona: {str(e)}",
            )


class DetailCommandHandler:
    """Handle /detail commands"""

    def __init__(
        self,
        orchestrator: MasterOrchestrator,
        store: Optional[PersonaStore] = None,
    ):
        """
        Initialize DetailCommandHandler.

        Args:
            orchestrator: MasterOrchestrator instance
            store: Optional PersonaStore for persistence
        """
        self.orchestrator = orchestrator
        self.store = store or PersonaStore()
        self.parser = CommandParser()

    def handle(
        self,
        user_input: str,
        user_id: str,
    ) -> CommandResponse:
        """
        Handle /detail command.

        Args:
            user_input: Full command line
            user_id: User identifier

        Returns:
            CommandResponse with result
        """
        # Parse command
        parse_result = self.parser.parse_detail_command(user_input)

        if not parse_result.success:
            return CommandResponse(
                success=False,
                message=parse_result.error,
            )

        try:
            # Extract depth and sticky flag
            depth_str = parse_result.args["depth"]
            sticky = parse_result.args["sticky"]

            depth_enum = DepthLevel[depth_str.upper()]

            # Set depth
            self.orchestrator.set_depth(depth_enum)

            if sticky:
                # Add override to store
                self.store.add_depth_override(
                    user_id=user_id,
                    override_level=depth_enum,
                    context="/detail sticky command",
                )
            else:
                # Single turn override
                self.store.add_depth_override(
                    user_id=user_id,
                    override_level=depth_enum,
                    context="/detail command (single-turn)",
                )

            # Get new state
            new_state = self.orchestrator.get_current_state()

            mode = "sticky" if sticky else "single-turn"

            return CommandResponse(
                success=True,
                message=f"✅ Detail level set to {depth_enum.value} ({mode})",
                state=new_state,
                next_action="continue_conversation",
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                message=f"Error setting detail: {str(e)}",
            )


class IntroductionHandler:
    """Handle introduction template on first interaction"""

    @staticmethod
    def should_show_introduction(
        user_id: str,
        store: PersonaStore,
    ) -> bool:
        """
        Determine if introduction should be shown.

        Args:
            user_id: User identifier
            store: PersonaStore for checking history

        Returns:
            True if introduction should be shown
        """
        # Check if user has persona preference
        persona = store.get_user_persona(user_id)

        return persona is None

    @staticmethod
    def get_introduction_template() -> str:
        """
        Get introduction template.

        Returns:
            Introduction text
        """
        template = """
🧠 CORTEX Introduction

I'm CORTEX — your Cognitive Real-Time Execution System.

To optimize our collaboration, what's your primary role?

1️⃣ **Business Leader** — Executive summaries, ROI metrics, KPIs
2️⃣ **Product Owner / Scrum Master** — Business guidance, roadmaps, planning
3️⃣ **Tech Lead / Manager** — Architecture, system design, team guidance
4️⃣ **Software Engineer** — Full technical depth, code, implementation

*Selection persists for your session, adjustable via `/persona {role}`*

**Usage:**
- `/persona engineer` — Switch to engineer mode
- `/detail executive` — Single-turn summary (2-3 sentences)
- `/detail sticky detailed` — Lock in detailed depth for session
"""
        return template.strip()

    @staticmethod
    def handle_first_interaction(
        user_id: str,
        orchestrator: MasterOrchestrator,
        store: PersonaStore,
    ) -> CommandResponse:
        """
        Handle first interaction flow.

        Args:
            user_id: User identifier
            orchestrator: MasterOrchestrator instance
            store: PersonaStore for persistence

        Returns:
            CommandResponse with introduction template
        """
        if not IntroductionHandler.should_show_introduction(user_id, store):
            return CommandResponse(
                success=False,
                message="User already has persona preference",
            )

        introduction = IntroductionHandler.get_introduction_template()

        return CommandResponse(
            success=True,
            message=introduction,
            next_action="await_persona_selection",
        )
