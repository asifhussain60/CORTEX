"""
Conversation Continuation Tests - Resuming conversations from checkpoints.

Tests for continuing multi-turn conversations, recovering state, and chaining continuations.
"""

import pytest
import json
from typing import Dict, Any
from datetime import datetime

from cortex.orchestrators.conversation_continuer import ConversationContinuer
from cortex.orchestrators.state_recovery import StateRecovery
from cortex.brain.core.checkpoint_manager import CheckpointManager
from cortex.orchestrators.continuation_chain import ContinuationChain


class TestConversationContinuer:
    """Tests for resuming conversations from checkpoints."""

    def test_continuer_initializes(self) -> None:
        """Test ConversationContinuer initialization."""
        continuer = ConversationContinuer()
        assert continuer is not None

    def test_continuer_saves_checkpoint(self) -> None:
        """Test creating a checkpoint."""
        continuer = ConversationContinuer()
        
        state = {"turn": 1, "context": {"user": "Alice"}}
        checkpoint_id = continuer.create_checkpoint(state)
        
        assert checkpoint_id is not None
        assert len(checkpoint_id) > 0

    def test_continuer_resumes_from_checkpoint(self) -> None:
        """Test resuming conversation from checkpoint."""
        continuer = ConversationContinuer()
        
        state = {"turn": 1, "context": {"user": "Alice"}}
        checkpoint_id = continuer.create_checkpoint(state)
        
        resumed = continuer.resume_from_checkpoint(checkpoint_id)
        assert resumed is not None
        assert resumed["turn"] == 1
        assert resumed["context"]["user"] == "Alice"

    def test_continuer_tracks_multiple_checkpoints(self) -> None:
        """Test tracking multiple checkpoints."""
        continuer = ConversationContinuer()
        
        cp1 = continuer.create_checkpoint({"turn": 1})
        cp2 = continuer.create_checkpoint({"turn": 2})
        cp3 = continuer.create_checkpoint({"turn": 3})
        
        assert cp1 != cp2
        assert cp2 != cp3
        
        assert continuer.resume_from_checkpoint(cp1)["turn"] == 1
        assert continuer.resume_from_checkpoint(cp2)["turn"] == 2
        assert continuer.resume_from_checkpoint(cp3)["turn"] == 3

    def test_continuer_no_data_loss(self) -> None:
        """Test that resume has no data loss."""
        continuer = ConversationContinuer()
        
        original = {
            "turn": 5,
            "history": ["msg1", "msg2", "msg3"],
            "context": {"a": 1, "b": 2, "c": 3},
        }
        
        cp = continuer.create_checkpoint(original)
        resumed = continuer.resume_from_checkpoint(cp)
        
        assert resumed == original


class TestStateRecovery:
    """Tests for state recovery and context restoration."""

    def test_recovery_initializes(self) -> None:
        """Test StateRecovery initialization."""
        recovery = StateRecovery()
        assert recovery is not None

    def test_recovery_saves_state(self) -> None:
        """Test saving execution state."""
        recovery = StateRecovery()
        
        state = {"context": {"user_id": "u123", "session": "s456"}}
        recovery.save_state(state)
        
        assert recovery.get_state() is not None

    def test_recovery_restores_context(self) -> None:
        """Test restoring execution context."""
        recovery = StateRecovery()
        
        original_context = {"user_id": "u123", "session": "s456", "data": [1, 2, 3]}
        recovery.save_state(original_context)
        
        restored = recovery.get_state()
        assert restored == original_context

    def test_recovery_validates_consistency(self) -> None:
        """Test consistency validation."""
        recovery = StateRecovery()
        
        state = {"timestamp": datetime.now().isoformat(), "turn": 1}
        recovery.save_state(state)
        
        is_consistent = recovery.validate_consistency()
        assert isinstance(is_consistent, bool)

    def test_recovery_accuracy(self) -> None:
        """Test recovery accuracy threshold."""
        recovery = StateRecovery()
        
        states = [
            {"data": f"state_{i}", "value": i}
            for i in range(10)
        ]
        
        for state in states:
            recovery.save_state(state)
            restored = recovery.get_state()
            assert restored == state


class TestCheckpointManager:
    """Tests for checkpoint creation and management."""

    def test_checkpoint_manager_initializes(self) -> None:
        """Test CheckpointManager initialization."""
        manager = CheckpointManager()
        assert manager is not None

    def test_checkpoint_manager_creates_checkpoint(self) -> None:
        """Test creating checkpoints with full API."""
        manager = CheckpointManager()
        
        data = {"turn": 1, "context": {}}
        result = manager.create_checkpoint(
            operation_id="test-op-1",
            operation_type="TEST",
            state_snapshot=data,
            recovery_instructions="Resume from turn 1",
        )
        
        assert result.is_ok()
        checkpoint = result.unwrap()
        assert checkpoint is not None
        assert checkpoint.metadata.operation_id == "test-op-1"

    def test_checkpoint_compression(self) -> None:
        """Test checkpoint compression with large data."""
        manager = CheckpointManager()
        
        # Large state
        large_data = {
            "history": ["msg"] * 1000,
            "context": {"data": list(range(100))},
        }
        
        result = manager.create_checkpoint(
            operation_id="test-compression",
            operation_type="LARGE_OP",
            state_snapshot=large_data,
            recovery_instructions="Handle large data",
        )
        
        assert result.is_ok()
        checkpoint = result.unwrap()
        assert checkpoint is not None

    def test_checkpoint_durability(self) -> None:
        """Test checkpoint is durable (can persist)."""
        manager = CheckpointManager()
        
        data = {"turn": 1, "data": "important"}
        result = manager.create_checkpoint(
            operation_id="test-durable",
            operation_type="DURABLE",
            state_snapshot=data,
            recovery_instructions="Resume important data",
        )
        
        assert result.is_ok()
        checkpoint = result.unwrap()
        
        # Retrieve by ID (returns Result, needs unwrap)
        restore_result = manager.get_checkpoint(checkpoint.metadata.checkpoint_id)
        assert restore_result.is_ok()
        restored = restore_result.unwrap()
        assert restored.state_snapshot == data

    def test_checkpoint_validation(self) -> None:
        """Test checkpoint validation."""
        manager = CheckpointManager()
        
        data = {"turn": 1, "context": {}}
        result = manager.create_checkpoint(
            operation_id="test-validate",
            operation_type="VALIDATE",
            state_snapshot=data,
            recovery_instructions="Validate checkpoint",
        )
        
        assert result.is_ok()
        checkpoint = result.unwrap()
        
        # validate_checkpoint returns Result[bool]
        is_valid_result = manager.validate_checkpoint(checkpoint.metadata.checkpoint_id)
        assert is_valid_result.is_ok()
        assert is_valid_result.unwrap() is True


class TestContinuationChain:
    """Tests for chaining multiple continuations."""

    def test_chain_initializes(self) -> None:
        """Test ContinuationChain initialization."""
        chain = ContinuationChain()
        assert chain is not None

    def test_chain_single_continuation(self) -> None:
        """Test single continuation in chain."""
        chain = ContinuationChain()
        
        cp1 = "checkpoint-1"
        chain.add_checkpoint(cp1)
        
        result = chain.execute()
        assert result is not None
        assert len(result) == 1

    def test_chain_multiple_continuations(self) -> None:
        """Test chaining multiple continuations."""
        chain = ContinuationChain()
        
        chain.add_checkpoint("checkpoint-1")
        chain.add_checkpoint("checkpoint-2")
        chain.add_checkpoint("checkpoint-3")
        
        assert chain.get_chain_length() == 3

    def test_chain_execution_order(self) -> None:
        """Test execution maintains order."""
        chain = ContinuationChain()
        
        for i in range(1, 6):
            chain.add_checkpoint(f"checkpoint-{i}")
        
        results = chain.execute()
        assert results is not None
        assert len(results) == 5
        assert results[0] == "checkpoint-1"
        assert results[-1] == "checkpoint-5"

    def test_chain_failure_recovery(self) -> None:
        """Test recovery from failure in chain."""
        chain = ContinuationChain()
        
        chain.add_checkpoint("checkpoint-1")
        chain.add_checkpoint("checkpoint-2")
        chain.add_checkpoint("checkpoint-3")
        
        # Skip failed checkpoint
        skipped = chain.skip_checkpoint("checkpoint-2")
        assert skipped is True
        assert chain.get_chain_length() == 2
        
        # Verify correct checkpoints remain
        remaining = chain.get_remaining_checkpoints()
        assert "checkpoint-1" in remaining
        assert "checkpoint-3" in remaining


class TestContinuationIntegration:
    """Integration tests for conversation continuation."""

    def test_continuer_and_recovery_integration(self) -> None:
        """Test continuer with state recovery."""
        continuer = ConversationContinuer()
        recovery = StateRecovery()
        
        state = {"turn": 1, "data": "test"}
        cp = continuer.create_checkpoint(state)
        
        recovery.save_state(state)
        recovered = recovery.get_state()
        
        assert recovered == state
        assert cp is not None

    def test_checkpoint_manager_in_chain(self) -> None:
        """Test checkpoint manager with continuation chain."""
        manager = CheckpointManager()
        chain = ContinuationChain()
        
        for i in range(1, 4):
            result = manager.create_checkpoint(
                operation_id=f"chain-op-{i}",
                operation_type="CHAIN",
                state_snapshot={"turn": i},
                recovery_instructions=f"Resume from turn {i}",
            )
            assert result.is_ok()
            checkpoint = result.unwrap()
            chain.add_checkpoint(checkpoint.metadata.checkpoint_id)
        
        assert chain.get_chain_length() == 3

    def test_end_to_end_conversation_continuation(self) -> None:
        """Test complete conversation continuation flow."""
        continuer = ConversationContinuer()
        recovery = StateRecovery()
        manager = CheckpointManager()
        chain = ContinuationChain()
        
        # Turn 1
        state1 = {"turn": 1, "user": "Alice", "messages": ["hello"]}
        cp1 = continuer.create_checkpoint(state1)
        result1 = manager.create_checkpoint(
            operation_id="e2e-turn-1",
            operation_type="CONVERSATION",
            state_snapshot=state1,
            recovery_instructions="Resume from turn 1",
        )
        assert result1.is_ok()
        chain.add_checkpoint(result1.unwrap().metadata.checkpoint_id)
        
        # Turn 2
        state2 = {"turn": 2, "user": "Alice", "messages": ["hello", "response"]}
        cp2 = continuer.create_checkpoint(state2)
        result2 = manager.create_checkpoint(
            operation_id="e2e-turn-2",
            operation_type="CONVERSATION",
            state_snapshot=state2,
            recovery_instructions="Resume from turn 2",
        )
        assert result2.is_ok()
        chain.add_checkpoint(result2.unwrap().metadata.checkpoint_id)
        
        # Simulate resuming from turn 1
        resumed = continuer.resume_from_checkpoint(cp1)
        assert resumed is not None
        assert resumed.get("turn") == 1
        
        # Verify chain integrity
        assert chain.get_chain_length() == 2

    def test_timeout_recovery(self) -> None:
        """Test recovery from timeout."""
        continuer = ConversationContinuer()
        recovery = StateRecovery()
        
        # Simulate interrupted conversation
        state = {"turn": 1, "interrupted_at": datetime.now().isoformat()}
        cp = continuer.create_checkpoint(state)
        recovery.save_state(state)
        
        # Later: resume
        resumed = continuer.resume_from_checkpoint(cp)
        assert resumed is not None
        assert "interrupted_at" in resumed
