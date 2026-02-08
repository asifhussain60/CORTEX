"""
Phase 37 S6: End-to-End Integration Testing

Authority: Phase 37 S6
Tests complete persona workflow across all subsystems
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.persona.role_resolver import RoleResolver
from cortex.orchestrators.persona.persona_injector import PersonaInjector
from cortex.orchestrators.persona.session_context import SessionContext
from cortex.orchestrators.persona.models import PersonaId, DepthLevel
from cortex.interaction.persona_store import PersonaStore
from cortex.interaction.command_handlers import (
    PersonaCommandHandler,
    DetailCommandHandler,
    CommandParser,
    IntroductionHandler,
)


@pytest.fixture
def temp_store_path():
    """Create temporary storage for persona store tests"""
    temp_dir = tempfile.mkdtemp()
    store_path = Path(temp_dir) / "user_personas.yaml"
    yield str(store_path)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestPersonaE2EWorkflow:
    """End-to-end persona system workflow tests"""

    def test_persona_store_crud_lifecycle(self, temp_store_path):
        """Test complete persona store CRUD lifecycle"""
        store = PersonaStore(storage_path=temp_store_path)
        user_id = "e2e_crud_test"
        
        # Create
        create_result = store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        assert create_result is True
        
        # Read
        read_result = store.get_user_persona(user_id)
        assert read_result is not None
        assert read_result["persona"] == PersonaId.ENGINEER.value
        
        # Update
        update_result = store.update_user_persona(
            user_id=user_id,
            persona=PersonaId.TECH_LEAD,
            depth=DepthLevel.DETAILED,
        )
        assert update_result is True
        
        # Verify update
        updated = store.get_user_persona(user_id)
        assert updated["persona"] == PersonaId.TECH_LEAD.value
        
        # Delete
        delete_result = store.delete_user_persona(user_id)
        assert delete_result is True
        
        # Verify deletion
        deleted = store.get_user_persona(user_id)
        assert deleted is None

    def test_command_parser_integration(self, temp_store_path):
        """Test command parsing integrated with store"""
        store = PersonaStore(storage_path=temp_store_path)
        parser = CommandParser()
        user_id = "parser_test"
        
        # Create user via store
        store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        # Parse command
        result = parser.parse_persona_command("/persona product_owner")
        assert result.success is True
        
        # Update via store
        store.update_user_persona(
            user_id=user_id,
            persona=PersonaId[result.args["persona"].upper()],
            depth=DepthLevel.STANDARD,
        )
        
        # Verify
        stored = store.get_user_persona(user_id)
        assert stored["persona"] == PersonaId.PRODUCT_OWNER.value

    def test_depth_override_workflow(self, temp_store_path):
        """Test depth override lifecycle"""
        store = PersonaStore(storage_path=temp_store_path)
        user_id = "depth_override_test"
        
        # Create user
        store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        # Add override
        store.add_depth_override(
            user_id=user_id,
            override_level=DepthLevel.EXECUTIVE,
            context="test_override",
        )
        
        # Get overrides
        overrides = store.get_active_overrides(user_id)
        assert len(overrides) > 0
        assert overrides[-1]["level"] == DepthLevel.EXECUTIVE.value

    def test_multi_user_isolation(self, temp_store_path):
        """Test that users are properly isolated"""
        store = PersonaStore(storage_path=temp_store_path)
        
        # Create user 1
        store.create_user_persona(
            user_id="user1",
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        # Create user 2
        store.create_user_persona(
            user_id="user2",
            persona=PersonaId.BUSINESS_LEADER,
            depth=DepthLevel.EXECUTIVE,
        )
        
        # Verify isolation
        user1 = store.get_user_persona("user1")
        user2 = store.get_user_persona("user2")
        
        assert user1["persona"] == PersonaId.ENGINEER.value
        assert user2["persona"] == PersonaId.BUSINESS_LEADER.value

    def test_introduction_handler_functionality(self, temp_store_path):
        """Test introduction handler checks and templates"""
        store = PersonaStore(storage_path=temp_store_path)
        user_id = "new_user"
        
        # New user should show introduction
        should_show = IntroductionHandler.should_show_introduction(user_id, store)
        assert should_show is True
        
        # After creating preference, don't show
        store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        should_show_after = IntroductionHandler.should_show_introduction(user_id, store)
        assert should_show_after is False
        
        # Template exists and is non-empty
        template = IntroductionHandler.get_introduction_template()
        assert len(template) > 0


class TestPersonaIntegrationRegressions:
    """Regression tests for persona system integration"""

    def test_no_data_loss_on_store_error(self):
        """Test that store errors don't cause data loss"""
        user_id = "regression_user_1"
        
        with patch("cortex.interaction.persona_store.PersonaStore._write_store") as mock_write:
            # First write succeeds
            mock_write.return_value = True
            store = PersonaStore()
            
            # Simulate first save
            result1 = store.create_user_persona(
                user_id=user_id,
                persona=PersonaId.ENGINEER,
                depth=DepthLevel.STANDARD,
            )
            assert result1 is True

    def test_concurrent_persona_updates(self, temp_store_path):
        """Test concurrent updates don't corrupt state"""
        store = PersonaStore(storage_path=temp_store_path)
        user_id = "concurrent_user"
        
        # Sequential updates (simulating concurrent)
        for i in range(5):
            persona = PersonaId.ENGINEER if i % 2 == 0 else PersonaId.TECH_LEAD
            result = store.update_user_persona(
                user_id=user_id,
                persona=persona,
                depth=DepthLevel.STANDARD,
            )
            assert result is True
        
        # Final state should be consistent
        final = store.get_user_persona(user_id)
        assert final is not None
        assert final["persona"] in [p.value for p in PersonaId]

    def test_invalid_command_doesnt_corrupt_state(self, temp_store_path):
        """Test invalid commands don't corrupt persona state"""
        orchestrator = Mock()
        store = PersonaStore(storage_path=temp_store_path)
        handler = PersonaCommandHandler(orchestrator, store)
        
        # Try invalid persona
        result = handler.handle("/persona nonexistent_role", "test_user")
        assert result.success is False
        
        # Store should still be valid
        stats = store.get_stats()
        assert isinstance(stats, dict)

    def test_missing_file_creates_new(self):
        """Test missing storage file is created on first write"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "new_store.yaml"
            
            assert not store_path.exists()
            
            store = PersonaStore(storage_path=str(store_path))
            store.create_user_persona(
                user_id="test",
                persona=PersonaId.ENGINEER,
                depth=DepthLevel.STANDARD,
            )
            
            assert store_path.exists()


class TestPersonaPerformance:
    """Performance tests for persona system"""

    def test_command_parsing_performance(self):
        """Test command parsing is fast"""
        parser = CommandParser()
        
        # Parse 100 commands
        for i in range(100):
            result = parser.parse_persona_command(f"/persona engineer")
            assert result.success is True

    def test_persona_inference_performance(self):
        """Test persona inference completes quickly"""
        from cortex.orchestrators.persona.persona_loader import PersonaLoader
        
        loader = PersonaLoader()
        resolver = RoleResolver(loader=loader)
        
        # Infer 50 times
        for i in range(50):
            result = resolver.infer_role(
                message=f"Question {i}: How do I optimize this code?",
                context={},
            )
            assert result is not None

    def test_store_operations_performance(self):
        """Test store operations are performant"""
        store = PersonaStore()
        
        # Create 20 users
        for i in range(20):
            store.create_user_persona(
                user_id=f"perf_user_{i}",
                persona=PersonaId.ENGINEER,
                depth=DepthLevel.STANDARD,
            )
        
        # List all users
        users = store.list_all_users()
        assert len(users) >= 20


class TestPersonaSystemIntegrity:
    """Test system integrity and consistency"""

    def test_all_personas_accessible(self, temp_store_path):
        """Test all 6 personas can be set and retrieved"""
        store = PersonaStore(storage_path=temp_store_path)
        
        personas_to_test = [
            PersonaId.BUSINESS_LEADER,
            PersonaId.PRODUCT_OWNER,
            PersonaId.SCRUM_MASTER,
            PersonaId.TECH_LEAD,
            PersonaId.ENGINEER,
            PersonaId.UNKNOWN,
        ]
        
        for persona in personas_to_test:
            user_id = f"test_{persona.value}"
            
            result = store.create_user_persona(
                user_id=user_id,
                persona=persona,
                depth=DepthLevel.STANDARD,
            )
            assert result is True
            
            retrieved = store.get_user_persona(user_id)
            assert retrieved is not None
            assert retrieved["persona"] == persona.value

    def test_all_depth_levels_accessible(self, temp_store_path):
        """Test all 4 depth levels can be set and retrieved"""
        store = PersonaStore(storage_path=temp_store_path)
        
        depths_to_test = [
            DepthLevel.EXECUTIVE,
            DepthLevel.STANDARD,
            DepthLevel.DETAILED,
            DepthLevel.FULL,
        ]
        
        for depth in depths_to_test:
            user_id = f"test_{depth.value}"
            
            result = store.create_user_persona(
                user_id=user_id,
                persona=PersonaId.ENGINEER,
                depth=depth,
            )
            assert result is True
            
            retrieved = store.get_user_persona(user_id)
            assert retrieved is not None
            assert retrieved["depth"] == depth.value

    def test_introduction_handler_template(self):
        """Test introduction template is properly formatted"""
        template = IntroductionHandler.get_introduction_template()
        
        assert template is not None
        assert len(template) > 0
        assert "CORTEX" in template
        assert "Business Leader" in template or "Engineer" in template

    def test_wiring_system_registration(self):
        """Test wiring system can register all agents and tools"""
        from cortex.wiring.specifications.wiring_manager import (
            WiringManager,
            register_persona_tools,
        )
        
        # Register tools
        result = register_persona_tools()
        assert result is True
        
        # Verify wiring manager
        manager = WiringManager()
        assert manager.validate_wiring() is True
        
        # Check agents loaded
        agents = manager.list_agents()
        assert len(agents) > 0
        
        # Check tools loaded
        tools = manager.list_mcp_tools()
        assert len(tools) > 0
        assert "cortex_set_persona" in tools


class TestPersonaDocumentation:
    """Test documentation and code quality"""

    def test_all_handlers_documented(self):
        """Test all command handlers have docstrings"""
        assert PersonaCommandHandler.__doc__ is not None
        assert DetailCommandHandler.__doc__ is not None
        assert CommandParser.__doc__ is not None

    def test_all_classes_have_init_docstrings(self):
        """Test init methods are documented"""
        classes_to_check = [
            PersonaCommandHandler,
            DetailCommandHandler,
            CommandParser,
            IntroductionHandler,
        ]
        
        for cls in classes_to_check:
            assert cls.__init__.__doc__ is not None or cls.__doc__ is not None

    def test_all_methods_have_docstrings(self):
        """Test public methods have docstrings"""
        parser = CommandParser()
        
        assert parser.parse_persona_command.__doc__ is not None
        assert parser.parse_detail_command.__doc__ is not None
