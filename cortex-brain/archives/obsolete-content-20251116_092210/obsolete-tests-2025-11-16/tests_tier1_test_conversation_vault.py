"""
Tests for CORTEX 3.0 Conversation Vault

Tests vault storage, archival, and retrieval functionality.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from src.tier1.conversation_vault import (
    ConversationVaultManager,
    ConversationMetadata,
    ConversationTurn,
    create_vault_manager
)


class TestConversationVault:
    """Test conversation vault functionality."""
    
    @pytest.fixture
    def temp_vault(self, tmp_path):
        """Create temporary vault for testing."""
        vault_path = tmp_path / "test-vault"
        vault = ConversationVaultManager(str(vault_path))
        yield vault
    
    def test_vault_initialization(self, temp_vault):
        """Should create vault directories."""
        assert temp_vault.vault_path.exists()
        assert temp_vault.metadata_path.exists()
    
    def test_create_conversation_file(self, temp_vault):
        """Should create conversation file with metadata."""
        metadata = ConversationMetadata(
            conversation_id="test-conv-001",
            timestamp=datetime.now().isoformat(),
            quality_score=12,
            quality_level="EXCELLENT",
            semantic_elements={
                'multi_phase_planning': True,
                'phase_count': 3,
                'challenge_accept_flow': True
            },
            total_turns=2,
            user_topic="Implement Authentication System"
        )
        
        turns = [
            ConversationTurn(
                turn_number=1,
                user_prompt="Plan authentication",
                assistant_response="Phase 1: Core Auth, Phase 2: Guards, Phase 3: Testing",
                timestamp=datetime.now().isoformat()
            )
        ]
        
        filepath = temp_vault.create_conversation_file(
            metadata=metadata,
            turns=turns,
            filename="2025-11-13-auth-planning.md"
        )
        
        assert filepath.exists()
        content = filepath.read_text()
        
        # Verify frontmatter
        assert "conversation_id: test-conv-001" in content
        assert "quality_level: EXCELLENT" in content
        assert "quality_score: 12" in content
        
        # Verify content
        assert "# Implement Authentication System" in content
        assert "Turn 1" in content
        assert "Plan authentication" in content
    
    def test_metadata_saved_separately(self, temp_vault):
        """Should save metadata as JSON file."""
        metadata = ConversationMetadata(
            conversation_id="test-conv-002",
            timestamp=datetime.now().isoformat(),
            quality_score=8,
            quality_level="GOOD",
            semantic_elements={},
            total_turns=1,
            user_topic="Quick Fix"
        )
        
        temp_vault.create_conversation_file(
            metadata=metadata,
            turns=[],
            filename="quick-fix.md"
        )
        
        metadata_file = temp_vault.metadata_path / "test-conv-002.json"
        assert metadata_file.exists()
        
        saved_metadata = json.loads(metadata_file.read_text())
        assert saved_metadata['conversation_id'] == "test-conv-002"
        assert saved_metadata['quality_level'] == "GOOD"
    
    def test_get_conversation_by_id(self, temp_vault):
        """Should retrieve conversation file by ID."""
        metadata = ConversationMetadata(
            conversation_id="test-conv-003",
            timestamp=datetime.now().isoformat(),
            quality_score=10,
            quality_level="EXCELLENT",
            semantic_elements={},
            total_turns=1,
            user_topic="Test Conversation"
        )
        
        temp_vault.create_conversation_file(
            metadata=metadata,
            turns=[],
            filename="test-conversation.md"
        )
        
        found_file = temp_vault.get_conversation_by_id("test-conv-003")
        assert found_file is not None
        assert found_file.name == "test-conversation.md"
    
    def test_list_conversations(self, temp_vault):
        """Should list all conversations in vault."""
        # Create multiple conversations
        for i in range(3):
            metadata = ConversationMetadata(
                conversation_id=f"test-conv-00{i+4}",
                timestamp=datetime.now().isoformat(),
                quality_score=5 + i,
                quality_level="GOOD" if i < 2 else "EXCELLENT",
                semantic_elements={},
                total_turns=1,
                user_topic=f"Test {i+1}"
            )
            
            temp_vault.create_conversation_file(
                metadata=metadata,
                turns=[],
                filename=f"test-{i+1}.md"
            )
        
        conversations = temp_vault.list_conversations(limit=10)
        assert len(conversations) == 3
    
    def test_quality_filtering(self, temp_vault):
        """Should filter conversations by quality level."""
        # Create EXCELLENT conversation
        metadata_excellent = ConversationMetadata(
            conversation_id="test-conv-007",
            timestamp=datetime.now().isoformat(),
            quality_score=12,
            quality_level="EXCELLENT",
            semantic_elements={},
            total_turns=1,
            user_topic="High Quality"
        )
        
        temp_vault.create_conversation_file(
            metadata=metadata_excellent,
            turns=[],
            filename="excellent.md"
        )
        
        # Create GOOD conversation
        metadata_good = ConversationMetadata(
            conversation_id="test-conv-008",
            timestamp=datetime.now().isoformat(),
            quality_score=7,
            quality_level="GOOD",
            semantic_elements={},
            total_turns=1,
            user_topic="Medium Quality"
        )
        
        temp_vault.create_conversation_file(
            metadata=metadata_good,
            turns=[],
            filename="good.md"
        )
        
        # Filter for EXCELLENT only
        excellent_convs = temp_vault.list_conversations(quality_filter="EXCELLENT")
        assert len(excellent_convs) == 1
        assert excellent_convs[0]['quality_level'] == "EXCELLENT"
    
    def test_vault_stats(self, temp_vault):
        """Should compute vault statistics."""
        # Create test conversations
        for i in range(5):
            metadata = ConversationMetadata(
                conversation_id=f"test-conv-{i+100}",
                timestamp=datetime.now().isoformat(),
                quality_score=5 + (i * 2),
                quality_level="GOOD" if i < 3 else "EXCELLENT",
                semantic_elements={},
                total_turns=2 + i,
                user_topic=f"Test {i+1}"
            )
            
            temp_vault.create_conversation_file(
                metadata=metadata,
                turns=[],
                filename=f"test-stats-{i+1}.md"
            )
        
        stats = temp_vault.get_vault_stats()
        
        assert stats['total_conversations'] == 5
        assert stats['quality_distribution']['GOOD'] == 3
        assert stats['quality_distribution']['EXCELLENT'] == 2
        assert stats['total_turns'] == sum(2 + i for i in range(5))
        assert stats['average_quality_score'] > 0
    
    def test_create_vault_manager_factory(self, tmp_path):
        """Should create vault manager via factory function."""
        vault_path = tmp_path / "factory-vault"
        
        vault = create_vault_manager(config={'vault_path': str(vault_path)})
        
        assert vault.vault_path == vault_path
        assert vault.vault_path.exists()


class TestVaultIntegration:
    """Test vault integration with Tier 1 import."""
    
    def test_vault_workflow(self, tmp_path):
        """Should handle complete capture → import → archive workflow."""
        vault_path = tmp_path / "workflow-vault"
        vault = ConversationVaultManager(str(vault_path))
        
        # Simulate Smart Hint creating capture file
        capture_file = vault.vault_path / "2025-11-13-test-workflow.md"
        capture_file.write_text("# Test Workflow\n\n[Conversation content here]")
        
        # Simulate import with metadata
        metadata = ConversationMetadata(
            conversation_id="workflow-conv-001",
            timestamp=datetime.now().isoformat(),
            quality_score=10,
            quality_level="EXCELLENT",
            semantic_elements={'multi_phase_planning': True},
            total_turns=3,
            user_topic="Test Workflow"
        )
        
        # Archive conversation
        turns = [
            ConversationTurn(
                turn_number=1,
                user_prompt="Test",
                assistant_response="Response",
                timestamp=datetime.now().isoformat()
            )
        ]
        
        filepath = vault.create_conversation_file(
            metadata=metadata,
            turns=turns,
            filename="2025-11-13-test-workflow-archived.md"
        )
        
        # Verify archived
        assert filepath.exists()
        assert vault.get_conversation_by_id("workflow-conv-001") is not None
        
        # Verify stats updated
        stats = vault.get_vault_stats()
        assert stats['total_conversations'] >= 1
