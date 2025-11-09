"""
Tests for SessionResumer Agent

Validates conversation restoration, context reconstruction,
and integration with Tier 1 working memory.
"""

import pytest
from datetime import datetime
from src.cortex_agents.session_resumer import SessionResumer
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class TestSessionResumerBasics:
    """Test basic SessionResumer functionality"""
    
    def test_resumer_initialization(self, mock_tier_apis):
        """Test SessionResumer initialization"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        assert resumer.name == "Resumer"
        assert resumer.tier1 is not None
        assert resumer.tier2 is not None
        assert resumer.tier3 is not None
        assert len(resumer.supported_intents) > 0
    
    def test_resumer_can_handle_resume_intent(self, mock_tier_apis):
        """Test SessionResumer handles resume intents"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-123"},
            user_message="Resume previous conversation"
        )
        
        assert resumer.can_handle(request) is True
    
    def test_resumer_can_handle_restore_intent(self, mock_tier_apis):
        """Test SessionResumer handles restore_session intents"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="restore_session",
            context={"conversation_id": "conv-123"},
            user_message="Restore session"
        )
        
        assert resumer.can_handle(request) is True
    
    def test_resumer_rejects_invalid_intent(self, mock_tier_apis):
        """Test SessionResumer rejects non-resume intents"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Write some code"
        )
        
        assert resumer.can_handle(request) is False


class TestConversationRestoration:
    """Test conversation restoration from Tier 1"""
    
    def test_restore_conversation_from_tier1(self, mock_tier_apis, mocker):
        """Test successful conversation restoration"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        # Mock Tier 1 conversation data
        mock_get_conversation = mocker.MagicMock(return_value={
            "success": True,
            "conversation": {
                "conversation_id": "conv-123",
                "summary": "Working on authentication feature",
                "messages": [
                    {
                        "role": "user",
                        "content": "Add user authentication",
                        "timestamp": "2025-11-06T10:00:00",
                        "metadata": {
                            "files": ["auth.py", "user.py"],
                            "entities": ["User", "Auth"]
                        }
                    },
                    {
                        "role": "assistant",
                        "content": "I'll create the authentication module",
                        "timestamp": "2025-11-06T10:01:00",
                        "metadata": {}
                    }
                ],
                "updated_at": "2025-11-06T10:01:00"
            }
        })
        resumer.tier1.get_conversation = mock_get_conversation
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-123"},
            user_message="Resume conversation about authentication"
        )
        
        response = resumer.execute(request)
        
        assert response.success is True
        assert response.result["conversation_id"] == "conv-123"
        assert len(response.result["messages"]) == 2
        assert response.result["summary"] == "Working on authentication feature"
        assert "auth.py" in response.result["files_discussed"]
        assert "User" in response.result["entities"]
        assert len(response.result["timeline"]) == 2
    
    def test_restore_missing_conversation(self, mock_tier_apis, mocker):
        """Test handling of missing conversation"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        # Mock Tier 1 to return not found
        mock_get_conversation = mocker.MagicMock(return_value={
            "success": False,
            "conversation": None
        })
        resumer.tier1.get_conversation = mock_get_conversation
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-999"},
            user_message="Resume missing conversation"
        )
        
        response = resumer.execute(request)
        
        assert response.success is False
        assert "not found" in response.message.lower()
        assert response.metadata.get("error") is not None
    
    def test_restore_without_conversation_id(self, mock_tier_apis):
        """Test handling of request without conversation_id"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        request = AgentRequest(
            intent="resume",
            context={},  # No conversation_id
            user_message="Resume conversation"
        )
        
        response = resumer.execute(request)
        
        assert response.success is False
        assert "no conversation_id" in response.message.lower()


class TestContextReconstruction:
    """Test context reconstruction from conversation history"""
    
    def test_reconstruct_context_with_files(self, mock_tier_apis, mocker):
        """Test context reconstruction extracts files"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        # Mock conversation with file mentions
        mock_get_conversation = mocker.MagicMock(return_value={
            "success": True,
            "conversation": {
                "conversation_id": "conv-123",
                "summary": "Code review",
                "messages": [
                    {
                        "role": "user",
                        "content": "Review `auth.py` and `models/user.py`",
                        "timestamp": "2025-11-06T10:00:00",
                        "metadata": {
                            "files": ["auth.py"]
                        }
                    },
                    {
                        "role": "assistant",
                        "content": "I'll check `config.yaml` as well",
                        "timestamp": "2025-11-06T10:01:00",
                        "metadata": {}
                    }
                ],
                "updated_at": "2025-11-06T10:01:00"
            }
        })
        resumer.tier1.get_conversation = mock_get_conversation
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-123"},
            user_message="Resume code review"
        )
        
        response = resumer.execute(request)
        
        assert response.success is True
        files = response.result["files_discussed"]
        assert "auth.py" in files
        assert "models/user.py" in files
        assert "config.yaml" in files
    
    def test_reconstruct_context_with_entities(self, mock_tier_apis, mocker):
        """Test context reconstruction extracts entities"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        # Mock conversation with entities
        mock_get_conversation = mocker.MagicMock(return_value={
            "success": True,
            "conversation": {
                "conversation_id": "conv-456",
                "summary": "Database design",
                "messages": [
                    {
                        "role": "user",
                        "content": "Design User and Post models",
                        "timestamp": "2025-11-06T11:00:00",
                        "metadata": {
                            "entities": ["User", "Post"]
                        }
                    },
                    {
                        "role": "assistant",
                        "content": "Add Comment model too",
                        "timestamp": "2025-11-06T11:01:00",
                        "metadata": {
                            "entities": ["Comment"]
                        }
                    }
                ],
                "updated_at": "2025-11-06T11:01:00"
            }
        })
        resumer.tier1.get_conversation = mock_get_conversation
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-456"},
            user_message="Resume database design"
        )
        
        response = resumer.execute(request)
        
        assert response.success is True
        entities = response.result["entities"]
        assert "User" in entities
        assert "Post" in entities
        assert "Comment" in entities
    
    def test_reconstruct_timeline(self, mock_tier_apis, mocker):
        """Test timeline reconstruction from messages"""
        resumer = SessionResumer("Resumer", **mock_tier_apis)
        
        # Mock conversation with multiple messages
        mock_get_conversation = mocker.MagicMock(return_value={
            "success": True,
            "conversation": {
                "conversation_id": "conv-789",
                "summary": "Feature development",
                "messages": [
                    {
                        "role": "user",
                        "content": "Start authentication feature",
                        "timestamp": "2025-11-06T09:00:00",
                        "metadata": {}
                    },
                    {
                        "role": "assistant",
                        "content": "Created auth.py",
                        "timestamp": "2025-11-06T09:15:00",
                        "metadata": {}
                    },
                    {
                        "role": "user",
                        "content": "Add tests",
                        "timestamp": "2025-11-06T09:30:00",
                        "metadata": {}
                    }
                ],
                "updated_at": "2025-11-06T09:30:00"
            }
        })
        resumer.tier1.get_conversation = mock_get_conversation
        
        request = AgentRequest(
            intent="resume",
            context={"conversation_id": "conv-789"},
            user_message="Resume feature work"
        )
        
        response = resumer.execute(request)
        
        assert response.success is True
        timeline = response.result["timeline"]
        assert len(timeline) == 3
        assert timeline[0]["role"] == "user"
        assert timeline[1]["role"] == "assistant"
        assert "timestamp" in timeline[0]
        assert "summary" in timeline[0]
