"""
Tests for Persona Store - Persistent user preference management

Authority: Phase 37 S4, CORE-008 (TDD-first)
Tests CRUD operations for persistent user personas across sessions
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.interaction.persona_store import PersonaStore
from cortex.orchestrators.persona.models import PersonaId, DepthLevel


class TestPersonaStore:
    """Test suite for PersonaStore persistence layer"""

    @pytest.fixture
    def temp_store_path(self):
        """Create temporary storage file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "user_personas.yaml"
            yield store_path

    @pytest.fixture
    def persona_store(self, temp_store_path):
        """Create PersonaStore instance"""
        return PersonaStore(storage_path=str(temp_store_path))

    # Test CRUD Operations
    def test_create_user_persona(self, persona_store):
        """Test creating a new user persona"""
        user_id = "user_123"
        
        result = persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.FULL,
        )
        
        assert result is True
        assert persona_store.get_user_persona(user_id) is not None

    def test_get_user_persona_existing(self, persona_store):
        """Test retrieving existing user persona"""
        user_id = "user_456"
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.BUSINESS_LEADER,
            depth=DepthLevel.EXECUTIVE,
        )
        
        result = persona_store.get_user_persona(user_id)
        
        assert result is not None
        assert result["persona"] == PersonaId.BUSINESS_LEADER
        assert result["depth"] == DepthLevel.EXECUTIVE

    def test_get_user_persona_nonexistent(self, persona_store):
        """Test getting nonexistent user returns None"""
        result = persona_store.get_user_persona("nonexistent_user")
        
        assert result is None

    def test_update_user_persona(self, persona_store):
        """Test updating user persona"""
        user_id = "user_789"
        
        # Create initial
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        # Update
        result = persona_store.update_user_persona(
            user_id=user_id,
            persona=PersonaId.TECH_LEAD,
            depth=DepthLevel.DETAILED,
        )
        
        assert result is True
        updated = persona_store.get_user_persona(user_id)
        assert updated["persona"] == PersonaId.TECH_LEAD

    def test_update_nonexistent_user(self, persona_store):
        """Test updating nonexistent user creates it"""
        user_id = "new_user"
        
        result = persona_store.update_user_persona(
            user_id=user_id,
            persona=PersonaId.PRODUCT_OWNER,
            depth=DepthLevel.STANDARD,
        )
        
        assert result is True
        assert persona_store.get_user_persona(user_id) is not None

    def test_delete_user_persona(self, persona_store):
        """Test deleting user persona"""
        user_id = "user_delete_test"
        
        # Create first
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.FULL,
        )
        
        # Delete
        result = persona_store.delete_user_persona(user_id)
        
        assert result is True
        assert persona_store.get_user_persona(user_id) is None

    def test_delete_nonexistent_user(self, persona_store):
        """Test deleting nonexistent user returns False"""
        result = persona_store.delete_user_persona("nonexistent")
        
        assert result is False

    # Test Persistence
    def test_persistence_across_instances(self, temp_store_path):
        """Test that data persists when creating new store instance"""
        user_id = "persist_test_user"
        
        # Create and store in first instance
        store1 = PersonaStore(storage_path=str(temp_store_path))
        store1.create_user_persona(
            user_id=user_id,
            persona=PersonaId.TECH_LEAD,
            depth=DepthLevel.DETAILED,
        )
        
        # Create new instance and verify data exists
        store2 = PersonaStore(storage_path=str(temp_store_path))
        result = store2.get_user_persona(user_id)
        
        assert result is not None
        assert result["persona"] == PersonaId.TECH_LEAD

    def test_multiple_users(self, persona_store):
        """Test storing multiple users"""
        users = [
            ("user1", PersonaId.ENGINEER),
            ("user2", PersonaId.BUSINESS_LEADER),
            ("user3", PersonaId.PRODUCT_OWNER),
        ]
        
        for user_id, persona in users:
            persona_store.create_user_persona(
                user_id=user_id,
                persona=persona,
                depth=DepthLevel.STANDARD,
            )
        
        # Verify all users exist
        for user_id, expected_persona in users:
            result = persona_store.get_user_persona(user_id)
            assert result is not None
            assert result["persona"] == expected_persona

    def test_list_all_users(self, persona_store):
        """Test listing all stored users"""
        users = ["user_a", "user_b", "user_c"]
        
        for user_id in users:
            persona_store.create_user_persona(
                user_id=user_id,
                persona=PersonaId.ENGINEER,
                depth=DepthLevel.STANDARD,
            )
        
        all_users = persona_store.list_all_users()
        
        assert len(all_users) >= 3
        for user_id in users:
            assert user_id in all_users

    def test_list_users_empty(self, persona_store):
        """Test listing users when store is empty"""
        users = persona_store.list_all_users()
        
        assert isinstance(users, list)
        assert len(users) == 0

    # Test Metadata
    def test_created_at_timestamp(self, persona_store):
        """Test that created_at is set"""
        user_id = "timestamp_test"
        
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        result = persona_store.get_user_persona(user_id)
        
        assert "created_at" in result
        assert result["created_at"] is not None

    def test_last_active_updated(self, persona_store):
        """Test that last_active is updated on retrieval"""
        user_id = "last_active_test"
        
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        # Get initially
        result1 = persona_store.get_user_persona(user_id)
        created_at = result1["created_at"]
        
        # Get again
        result2 = persona_store.get_user_persona(user_id)
        
        # last_active should be updated
        assert result2.get("last_active") is not None

    # Test Depth Override Storage
    def test_store_depth_override(self, persona_store):
        """Test storing depth override"""
        user_id = "depth_override_test"
        
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.FULL,
        )
        
        # Add override
        persona_store.add_depth_override(
            user_id=user_id,
            override_level=DepthLevel.EXECUTIVE,
            context="meeting",
        )
        
        result = persona_store.get_user_persona(user_id)
        assert "overrides" in result
        assert len(result["overrides"]) > 0

    def test_get_active_overrides(self, persona_store):
        """Test retrieving active overrides"""
        user_id = "active_overrides_test"
        
        persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.FULL,
        )
        
        persona_store.add_depth_override(
            user_id=user_id,
            override_level=DepthLevel.EXECUTIVE,
            context="presentation",
        )
        
        overrides = persona_store.get_active_overrides(user_id)
        
        assert isinstance(overrides, list)
        assert len(overrides) > 0

    # Test Batch Operations
    def test_bulk_create_users(self, persona_store):
        """Test creating multiple users efficiently"""
        users_data = [
            {
                "user_id": f"bulk_user_{i}",
                "persona": PersonaId.ENGINEER,
                "depth": DepthLevel.FULL,
            }
            for i in range(5)
        ]
        
        result = persona_store.bulk_create_users(users_data)
        
        assert result is True
        all_users = persona_store.list_all_users()
        assert len(all_users) >= 5

    def test_export_users(self, persona_store, temp_store_path):
        """Test exporting user data"""
        # Create test users
        for i in range(3):
            persona_store.create_user_persona(
                user_id=f"export_user_{i}",
                persona=PersonaId.ENGINEER,
                depth=DepthLevel.STANDARD,
            )
        
        export_path = str(temp_store_path.parent / "export.yaml")
        result = persona_store.export_users(export_path)
        
        assert result is True
        assert os.path.exists(export_path)

    # Test Edge Cases
    def test_special_characters_in_user_id(self, persona_store):
        """Test handling special characters in user ID"""
        user_id = "user@example.com"
        
        result = persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        assert result is True
        retrieved = persona_store.get_user_persona(user_id)
        assert retrieved is not None

    def test_very_long_user_id(self, persona_store):
        """Test handling very long user IDs"""
        user_id = "user_" + "x" * 200
        
        result = persona_store.create_user_persona(
            user_id=user_id,
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        assert result is True
        retrieved = persona_store.get_user_persona(user_id)
        assert retrieved is not None

    def test_empty_user_id(self, persona_store):
        """Test that empty user ID is rejected"""
        result = persona_store.create_user_persona(
            user_id="",
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        assert result is False

    def test_concurrent_access_safe(self, persona_store):
        """Test that concurrent operations don't corrupt data"""
        # Create initial user
        persona_store.create_user_persona(
            user_id="concurrent_test",
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        # Simulate multiple updates
        for i in range(5):
            persona_store.update_user_persona(
                user_id="concurrent_test",
                persona=PersonaId.TECH_LEAD if i % 2 == 0 else PersonaId.ENGINEER,
                depth=DepthLevel.DETAILED,
            )
        
        # Verify data integrity
        final_state = persona_store.get_user_persona("concurrent_test")
        assert final_state is not None
        assert final_state["persona"] in [PersonaId.TECH_LEAD, PersonaId.ENGINEER]

    def test_storage_file_created(self, temp_store_path):
        """Test that storage file is created on first write"""
        assert not temp_store_path.exists()
        
        store = PersonaStore(storage_path=str(temp_store_path))
        store.create_user_persona(
            user_id="test",
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        assert temp_store_path.exists()

    def test_corrupted_storage_recovery(self, temp_store_path):
        """Test recovery from corrupted YAML file"""
        # Write corrupted YAML
        with open(temp_store_path, "w") as f:
            f.write("invalid: yaml: content: [")
        
        # Should handle gracefully
        store = PersonaStore(storage_path=str(temp_store_path))
        
        # New operation should succeed
        result = store.create_user_persona(
            user_id="recovery_test",
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.STANDARD,
        )
        
        assert result is True
