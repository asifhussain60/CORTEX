"""
Tests for Persona Command Handlers

Authority: Phase 37 S4, CORE-008 (TDD-first)
"""

from typing import Optional

import pytest

from cortex.interaction.persona_command_handlers import (
    CommandResult,
    PersonaCommandHandlers,
)
from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.persona.models import DepthLevel, PersonaId
from cortex.orchestrators.persona.persona_injector import PersonaInjector
from cortex.orchestrators.persona.persona_loader import PersonaLoader
from cortex.orchestrators.persona.role_resolver import RoleResolver
from cortex.orchestrators.persona.session_context import SessionContext


@pytest.fixture
def persona_loader():
    """Create a test persona loader"""
    return PersonaLoader()


@pytest.fixture
def session_context():
    """Create a test session context"""
    return SessionContext(user_id="test_user_123")


@pytest.fixture
def role_resolver(persona_loader):
    """Create a test role resolver"""
    return RoleResolver(loader=persona_loader)


@pytest.fixture
def persona_injector(persona_loader):
    """Create a test persona injector"""
    return PersonaInjector(loader=persona_loader)


@pytest.fixture
def master_orchestrator(session_context, role_resolver, persona_injector):
    """Create a test master orchestrator"""
    return MasterOrchestrator(
        session_context=session_context,
        role_resolver=role_resolver,
        persona_injector=persona_injector,
    )


@pytest.fixture
def command_handlers(master_orchestrator):
    """Create command handlers instance"""
    return PersonaCommandHandlers(orchestrator=master_orchestrator)


class TestPersonaCommandHandlers:
    """Test PersonaCommandHandlers class"""

    def test_handlers_initialization(self, command_handlers):
        """Test handlers initialize correctly"""
        assert command_handlers.orchestrator is not None
        assert len(command_handlers.valid_personas) == 5
        assert len(command_handlers.valid_depths) == 4

    def test_handle_command_routes_persona(self, command_handlers):
        """Test command routing for /persona"""
        result = command_handlers.handle_command("/persona", "engineer")
        assert result.success is True
        assert result.persona_changed is True

    def test_handle_command_routes_detail(self, command_handlers):
        """Test command routing for /detail"""
        result = command_handlers.handle_command("/detail", "full")
        assert result.success is True
        assert result.depth_changed is True

    def test_handle_command_unknown(self, command_handlers):
        """Test unknown command handling"""
        result = command_handlers.handle_command("/unknown", "arg")
        assert result.success is False
        assert "Unknown command" in result.message

    def test_persona_command_no_args_shows_current(self, command_handlers):
        """Test /persona with no args shows current persona"""
        result = command_handlers._handle_persona_command(None)
        assert result.success is True
        assert "Current persona" in result.message

    def test_persona_command_empty_args_shows_current(self, command_handlers):
        """Test /persona with empty args shows current persona"""
        result = command_handlers._handle_persona_command("")
        assert result.success is True
        assert "Current persona" in result.message

    def test_persona_command_reset(self, command_handlers):
        """Test /persona reset"""
        # First set a persona
        command_handlers._handle_persona_command("engineer")
        # Then reset
        result = command_handlers._handle_persona_command("reset")
        assert result.success is True
        assert result.action_taken == "reset"
        assert result.persona_changed is True

    def test_persona_command_save(self, command_handlers):
        """Test /persona save"""
        result = command_handlers._handle_persona_command("save")
        assert result.success is True
        assert result.action_taken == "save"
        assert "saved to your profile" in result.message

    def test_persona_command_set_engineer(self, command_handlers):
        """Test /persona engineer"""
        result = command_handlers._handle_persona_command("engineer")
        assert result.success is True
        assert result.action_taken == "set"
        assert result.persona_changed is True
        assert result.new_persona == "engineer"

    def test_persona_command_set_business_leader(self, command_handlers):
        """Test /persona business_leader"""
        result = command_handlers._handle_persona_command("business_leader")
        assert result.success is True
        assert result.persona_changed is True
        assert result.new_persona == "business_leader"

    def test_persona_command_set_tech_lead(self, command_handlers):
        """Test /persona tech_lead"""
        result = command_handlers._handle_persona_command("tech_lead")
        assert result.success is True
        assert result.persona_changed is True

    def test_persona_command_invalid_persona(self, command_handlers):
        """Test /persona with invalid persona"""
        result = command_handlers._handle_persona_command("invalid_role")
        assert result.success is False
        assert "Invalid persona" in result.message

    def test_detail_command_no_args_shows_current(self, command_handlers):
        """Test /detail with no args shows current depth"""
        result = command_handlers._handle_detail_command(None)
        assert result.success is True
        assert "Current depth" in result.message

    def test_detail_command_empty_args_shows_current(self, command_handlers):
        """Test /detail with empty args shows current depth"""
        result = command_handlers._handle_detail_command("")
        assert result.success is True
        assert "Current depth" in result.message

    def test_detail_command_set_executive(self, command_handlers):
        """Test /detail executive"""
        result = command_handlers._handle_detail_command("executive")
        assert result.success is True
        assert result.depth_changed is True
        assert result.new_depth == "executive"
        assert result.action_taken == "temporary_override"

    def test_detail_command_set_full(self, command_handlers):
        """Test /detail full"""
        result = command_handlers._handle_detail_command("full")
        assert result.success is True
        assert result.depth_changed is True

    def test_detail_command_set_detailed(self, command_handlers):
        """Test /detail detailed"""
        result = command_handlers._handle_detail_command("detailed")
        assert result.success is True
        assert result.depth_changed is True

    def test_detail_command_sticky(self, command_handlers):
        """Test /detail sticky {level}"""
        result = command_handlers._handle_detail_command("sticky full")
        assert result.success is True
        assert result.depth_changed is True
        assert result.action_taken == "sticky_override"
        assert "for this session" in result.message

    def test_detail_command_sticky_multiple_words(self, command_handlers):
        """Test /detail sticky with multiple word args"""
        result = command_handlers._handle_detail_command("sticky executive more words")
        # Should fail because of too many parts
        assert result.success is False

    def test_detail_command_invalid_depth(self, command_handlers):
        """Test /detail with invalid depth"""
        result = command_handlers._handle_detail_command("invalid_depth")
        assert result.success is False
        assert "Invalid depth" in result.message

    def test_detail_command_temporary_vs_sticky(self, command_handlers):
        """Test difference between temporary and sticky overrides"""
        # Temporary
        result_temp = command_handlers._handle_detail_command("full")
        assert result_temp.action_taken == "temporary_override"
        assert "for this turn" in result_temp.message

        # Sticky
        result_sticky = command_handlers._handle_detail_command("sticky full")
        assert result_sticky.action_taken == "sticky_override"
        assert "for this session" in result_sticky.message

    def test_parse_command_persona(self, command_handlers):
        """Test parsing /persona command"""
        cmd, args = command_handlers.parse_command_from_message("/persona engineer")
        assert cmd == "/persona"
        assert args == "engineer"

    def test_parse_command_role_alias(self, command_handlers):
        """Test parsing /role command (alias for /persona)"""
        cmd, args = command_handlers.parse_command_from_message("/role tech_lead")
        assert cmd == "/persona"
        assert args == "tech_lead"

    def test_parse_command_detail(self, command_handlers):
        """Test parsing /detail command"""
        cmd, args = command_handlers.parse_command_from_message("/detail full")
        assert cmd == "/detail"
        assert args == "full"

    def test_parse_command_depth_alias(self, command_handlers):
        """Test parsing /depth command (alias for /detail)"""
        cmd, args = command_handlers.parse_command_from_message("/depth executive")
        assert cmd == "/detail"
        assert args == "executive"

    def test_parse_command_no_command(self, command_handlers):
        """Test parsing message with no command"""
        cmd, args = command_handlers.parse_command_from_message(
            "This is just a normal message"
        )
        assert cmd is None
        assert args is None

    def test_parse_command_persona_no_args(self, command_handlers):
        """Test parsing /persona with no args"""
        cmd, args = command_handlers.parse_command_from_message("/persona")
        assert cmd == "/persona"
        assert args is None

    def test_parse_command_sticky_detail(self, command_handlers):
        """Test parsing /detail sticky full"""
        cmd, args = command_handlers.parse_command_from_message("/detail sticky full")
        assert cmd == "/detail"
        assert args == "sticky full"

    def test_command_result_defaults(self):
        """Test CommandResult dataclass defaults"""
        result = CommandResult(success=True, message="Test")
        assert result.success is True
        assert result.message == "Test"
        assert result.action_taken is None
        assert result.persona_changed is False
        assert result.depth_changed is False

    def test_command_sequence_persona_then_detail(self, command_handlers):
        """Test sequence: set persona then change detail"""
        # Set engineer persona
        result1 = command_handlers._handle_persona_command("engineer")
        assert result1.success is True

        # Change detail to executive
        result2 = command_handlers._handle_detail_command("executive")
        assert result2.success is True

        # Both should be applied
        state = command_handlers.orchestrator.get_current_state()
        assert state["primary_persona"] == "engineer"
        assert state["active_depth"] == "executive"

    def test_handle_command_integration(self, command_handlers):
        """Test full command handling integration"""
        # Use handle_command which routes to internal handlers
        result = command_handlers.handle_command("/persona", "tech_lead")
        assert result.success is True
        assert result.persona_changed is True
        assert result.new_persona == "tech_lead"
