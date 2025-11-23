"""
Tests for Page Tracking & Context Retention (Milestone 2.3)

Validates session persistence, context restoration,
and multi-feature tracking.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2 - Milestone 2.3
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.workflows.page_tracking import (
    PageTracker,
    TDDContext,
    PageLocation
)
from src.workflows.tdd_state_machine import TDDStateMachine


class TestPageLocationTracking:
    """Test page location tracking."""
    
    def test_save_page_location(self):
        """Should save current page location."""
        location = PageLocation(
            filepath="src/auth/login.py",
            line_number=45,
            column_offset=8,
            function_name="authenticate_user",
            class_name="AuthService"
        )
        
        assert location.filepath == "src/auth/login.py"
        assert location.line_number == 45
        assert location.function_name == "authenticate_user"
    
    def test_location_without_function_or_class(self):
        """Should handle location without function or class context."""
        location = PageLocation(
            filepath="scripts/deploy.py",
            line_number=10,
            column_offset=0
        )
        
        assert location.function_name is None
        assert location.class_name is None


class TestTDDContextPersistence:
    """Test TDD context save/load functionality."""
    
    def test_save_and_load_context(self):
        """Should save and load TDD context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create context
            context = TDDContext(
                session_id="test_session_1",
                feature_name="User Authentication",
                current_state="red",
                last_location=PageLocation(
                    filepath="tests/test_auth.py",
                    line_number=20,
                    column_offset=4
                ),
                test_files=["tests/test_auth.py"],
                source_files=["src/auth/login.py"],
                notes="Working on login validation tests"
            )
            
            # Save context
            assert tracker.save_context(context)
            
            # Load context
            loaded = tracker.load_context("test_session_1")
            
            assert loaded is not None
            assert loaded.session_id == "test_session_1"
            assert loaded.feature_name == "User Authentication"
            assert loaded.current_state == "red"
            assert loaded.last_location.filepath == "tests/test_auth.py"
            assert loaded.last_location.line_number == 20
            assert len(loaded.test_files) == 1
            assert len(loaded.source_files) == 1
            assert "login validation" in loaded.notes
    
    def test_load_nonexistent_context(self):
        """Should return None for nonexistent session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            loaded = tracker.load_context("nonexistent_session")
            assert loaded is None
    
    def test_update_existing_context(self):
        """Should update existing context on save."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Save initial context
            context = TDDContext(
                session_id="test_session_2",
                feature_name="Payment Processing",
                current_state="red"
            )
            tracker.save_context(context)
            
            # Update context
            context.current_state = "green"
            context.notes = "Tests now passing"
            tracker.save_context(context)
            
            # Load and verify
            loaded = tracker.load_context("test_session_2")
            assert loaded.current_state == "green"
            assert "passing" in loaded.notes


class TestMultiFeatureTracking:
    """Test tracking multiple TDD sessions simultaneously."""
    
    def test_track_multiple_sessions(self):
        """Should track multiple sessions independently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create two sessions
            session1 = TDDContext(
                session_id="session_1",
                feature_name="Feature A",
                current_state="red"
            )
            
            session2 = TDDContext(
                session_id="session_2",
                feature_name="Feature B",
                current_state="green"
            )
            
            # Save both
            tracker.save_context(session1)
            tracker.save_context(session2)
            
            # Load both
            loaded1 = tracker.load_context("session_1")
            loaded2 = tracker.load_context("session_2")
            
            assert loaded1.feature_name == "Feature A"
            assert loaded1.current_state == "red"
            assert loaded2.feature_name == "Feature B"
            assert loaded2.current_state == "green"
    
    def test_list_active_sessions(self):
        """Should list all active sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create multiple sessions
            for i in range(3):
                context = TDDContext(
                    session_id=f"session_{i}",
                    feature_name=f"Feature {i}",
                    current_state="red" if i % 2 == 0 else "green"
                )
                tracker.save_context(context)
            
            # List active sessions
            active = tracker.list_active_sessions()
            
            assert len(active) == 3
            assert all(s.current_state in ("red", "green") for s in active)


class TestSessionManagement:
    """Test session lifecycle management."""
    
    def test_delete_session(self):
        """Should delete session from storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create session
            context = TDDContext(
                session_id="delete_me",
                feature_name="Test Feature",
                current_state="red"
            )
            tracker.save_context(context)
            
            # Verify exists
            assert tracker.load_context("delete_me") is not None
            
            # Delete
            assert tracker.delete_session("delete_me")
            
            # Verify deleted
            assert tracker.load_context("delete_me") is None
    
    def test_update_page_location(self):
        """Should update page location for existing session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create session
            context = TDDContext(
                session_id="update_location",
                feature_name="Test Feature",
                current_state="red"
            )
            tracker.save_context(context)
            
            # Update location
            new_location = PageLocation(
                filepath="src/module.py",
                line_number=100,
                column_offset=12
            )
            
            assert tracker.update_page_location("update_location", new_location)
            
            # Verify update
            loaded = tracker.load_context("update_location")
            assert loaded.last_location.filepath == "src/module.py"
            assert loaded.last_location.line_number == 100
    
    def test_add_note_to_session(self):
        """Should add notes to existing session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create session
            context = TDDContext(
                session_id="note_test",
                feature_name="Test Feature",
                current_state="red",
                notes="Initial note"
            )
            tracker.save_context(context)
            
            # Add note
            tracker.add_note("note_test", "Second note added")
            
            # Verify
            loaded = tracker.load_context("note_test")
            assert "Initial note" in loaded.notes
            assert "Second note added" in loaded.notes


class TestContextRestoration:
    """Test complete context restoration for resume capability."""
    
    def test_restore_with_file_lists(self):
        """Should restore session with all file lists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create session with multiple files
            context = TDDContext(
                session_id="restore_test",
                feature_name="Multi-file Feature",
                current_state="green",
                test_files=[
                    "tests/test_auth.py",
                    "tests/test_validation.py"
                ],
                source_files=[
                    "src/auth/login.py",
                    "src/auth/validation.py",
                    "src/models/user.py"
                ]
            )
            tracker.save_context(context)
            
            # Restore
            loaded = tracker.load_context("restore_test")
            
            assert len(loaded.test_files) == 2
            assert len(loaded.source_files) == 3
            assert "tests/test_auth.py" in loaded.test_files
            assert "src/models/user.py" in loaded.source_files
    
    def test_context_serialization(self):
        """Should serialize and deserialize context correctly."""
        context = TDDContext(
            session_id="serialize_test",
            feature_name="Serialization Test",
            current_state="refactor",
            last_location=PageLocation(
                filepath="src/test.py",
                line_number=42,
                column_offset=8
            )
        )
        
        # Serialize
        data = context.to_dict()
        
        # Deserialize
        restored = TDDContext.from_dict(data)
        
        assert restored.session_id == context.session_id
        assert restored.feature_name == context.feature_name
        assert restored.current_state == context.current_state
        assert restored.last_location.filepath == context.last_location.filepath


class TestStateMachineIntegration:
    """Test integration with TDD state machine."""
    
    def test_save_with_state_machine(self):
        """Should save context along with state machine snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "test_sessions.db"
            tracker = PageTracker(storage_path=str(storage_path))
            
            # Create state machine
            machine = TDDStateMachine("Test Feature", "machine_test")
            machine.start_red_phase()
            machine.complete_red_phase(tests_written=5)
            
            # Create context
            context = TDDContext(
                session_id="machine_test",
                feature_name="Test Feature",
                current_state="red"
            )
            
            # Save with state machine
            assert tracker.save_context(context, state_machine=machine)
            
            # Verify context saved
            loaded = tracker.load_context("machine_test")
            assert loaded is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
