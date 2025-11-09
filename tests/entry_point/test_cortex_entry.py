"""
Integration Tests for CORTEX Entry Point

Tests the complete flow from user message to formatted response,
including session management, tier integration, and agent routing.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.entry_point import CortexEntry
from src.cortex_agents.base_agent import AgentResponse


class TestCortexEntryInitialization:
    """Test entry point initialization."""
    
    def test_entry_point_creation(self):
        """Test basic entry point creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            # Create tier directories
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain))
            assert entry is not None
            assert entry.parser is not None
            assert entry.formatter is not None
            assert entry.router is not None
    
    def test_entry_point_with_logging(self):
        """Test entry point with logging enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=True)
            assert entry.logger is not None
    
    def test_entry_point_without_logging(self):
        """Test entry point with logging disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            assert entry.logger is not None  # Logger still exists, just not configured


class TestSingleRequestProcessing:
    """Test processing single requests."""
    
    @pytest.fixture
    def entry(self):
        """Create entry point with mocked dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            
            # Mock router to return success response
            entry.router.execute = Mock(return_value=AgentResponse(
                success=True,
                result={"files": ["test.py"]},
                message="Task completed successfully",
                agent_name="MockAgent"
            ))
            
            # Mock tier1 methods
            entry.tier1.process_message = Mock()
            entry.tier1.end_conversation = Mock()
            entry.tier1.get_summary = Mock(return_value={
                "total_conversations": 5,
                "total_messages": 20
            })
            
            # Mock session manager
            entry.session_manager.start_session = Mock(return_value="test-conv-123")
            entry.session_manager.get_active_session = Mock(return_value=None)
            entry.session_manager.end_session = Mock()
            
            yield entry
    
    def test_process_simple_request(self, entry):
        """Test processing a simple request."""
        response = entry.process("Create a test file")
        
        assert response is not None
        assert "SUCCESS" in response
        assert "Task completed successfully" in response
    
    def test_process_with_new_session(self, entry):
        """Test processing creates new session."""
        entry.session_manager.get_active_session.return_value = None
        
        entry.process("Test message")
        
        # Should create new session
        entry.session_manager.start_session.assert_called_once()
    
    def test_process_with_existing_session(self, entry):
        """Test processing resumes existing session."""
        entry.session_manager.get_active_session.return_value = "existing-conv-456"
        
        entry.process("Continue work", resume_session=True)
        
        # Should not create new session
        entry.session_manager.start_session.assert_not_called()
    
    def test_process_logs_to_tier1(self, entry):
        """Test that request/response are logged to Tier 1."""
        entry.process("Test message")
        
        # Should log both user message and assistant response
        assert entry.tier1.process_message.call_count == 2
    
    def test_process_with_markdown_format(self, entry):
        """Test response formatting as markdown."""
        response = entry.process("Test", format_type="markdown")
        
        assert "##" in response  # Markdown header
        assert "**" in response  # Markdown bold
    
    def test_process_with_json_format(self, entry):
        """Test response formatting as JSON."""
        response = entry.process("Test", format_type="json")
        
        assert "{" in response
        assert '"success"' in response
    
    def test_process_with_metadata(self, entry):
        """Test processing with custom metadata."""
        metadata = {"source": "test_suite", "priority": "high"}
        
        entry.process("Test", metadata=metadata)
        
        # Router should receive request with metadata
        call_args = entry.router.execute.call_args
        request = call_args[0][0]
        assert "source" in request.context or "source" in request.metadata


class TestBatchProcessing:
    """Test processing multiple requests."""
    
    @pytest.fixture
    def entry(self):
        """Create entry point for batch testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            
            # Mock router
            entry.router.execute = Mock(return_value=AgentResponse(
                success=True,
                result={},
                message="Success",
                agent_name="TestAgent"
            ))
            
            # Mock tier1
            entry.tier1.process_message = Mock()
            
            # Mock session
            entry.session_manager.start_session = Mock(return_value="batch-conv-789")
            entry.session_manager.get_active_session = Mock(return_value=None)
            
            yield entry
    
    def test_process_batch_multiple_messages(self, entry):
        """Test processing multiple messages."""
        messages = [
            "Create test file",
            "Add function",
            "Run tests"
        ]
        
        response = entry.process_batch(messages)
        
        assert response is not None
        assert "3/3" in response or "successful" in response
    
    def test_process_batch_with_resume(self, entry):
        """Test batch with session resumption."""
        entry.session_manager.get_active_session.return_value = "batch-conv-789"
        
        messages = ["Message 1", "Message 2"]
        entry.process_batch(messages, resume_session=True)
        
        # Should use same conversation
        assert entry.session_manager.start_session.call_count == 0
    
    def test_process_batch_without_resume(self, entry):
        """Test batch with new session per message."""
        messages = ["Message 1", "Message 2", "Message 3"]
        entry.process_batch(messages, resume_session=False)
        
        # Should create new session for each message
        assert entry.session_manager.start_session.call_count == 3


class TestSessionManagement:
    """Test session management features."""
    
    @pytest.fixture
    def entry(self):
        """Create entry point for session testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            
            # Mock session manager
            entry.session_manager.get_active_session = Mock(return_value="active-session")
            entry.session_manager.get_session_info = Mock(return_value={
                "conversation_id": "active-session",
                "start_time": "2025-11-06T10:00:00",
                "status": "active",
                "message_count": 5
            })
            entry.session_manager.end_session = Mock()
            
            # Mock tier1
            entry.tier1.end_conversation = Mock()
            
            yield entry
    
    def test_get_session_info_active(self, entry):
        """Test getting info for active session."""
        info = entry.get_session_info()
        
        assert info is not None
        assert info["conversation_id"] == "active-session"
        assert info["status"] == "active"
    
    def test_get_session_info_no_active(self, entry):
        """Test getting info when no active session."""
        entry.session_manager.get_active_session.return_value = None
        
        info = entry.get_session_info()
        assert info is None
    
    def test_end_session(self, entry):
        """Test explicitly ending session."""
        entry.end_session()
        
        # Should end session in manager and tier1
        entry.session_manager.end_session.assert_called_once_with("active-session")
        entry.tier1.end_conversation.assert_called_once_with("active-session")
    
    def test_end_session_no_active(self, entry):
        """Test ending session when none active."""
        entry.session_manager.get_active_session.return_value = None
        
        entry.end_session()
        
        # Should not call end methods
        entry.session_manager.end_session.assert_not_called()
        entry.tier1.end_conversation.assert_not_called()


class TestHealthStatus:
    """Test system health checking."""
    
    @pytest.fixture
    def entry(self):
        """Create entry point for health testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            
            # Mock tier APIs
            entry.tier1.get_summary = Mock(return_value={
                "total_conversations": 10,
                "total_messages": 50
            })
            entry.tier2.get_statistics = Mock(return_value={
                "total_patterns": 25,
                "total_relationships": 40
            })
            entry.tier3.get_context_summary = Mock(return_value={
                "velocity": {"trend": "increasing"}
            })
            
            yield entry
    
    def test_get_health_status_healthy(self, entry):
        """Test health status when all tiers healthy."""
        health = entry.get_health_status()
        
        assert health["overall_status"] == "healthy"
        assert "tier1" in health["tiers"]
        assert "tier2" in health["tiers"]
        assert "tier3" in health["tiers"]
        assert health["tiers"]["tier1"]["status"] == "healthy"
    
    def test_get_health_status_tier1_error(self, entry):
        """Test health status when Tier 1 has error."""
        entry.tier1.get_summary = Mock(side_effect=Exception("DB error"))
        
        health = entry.get_health_status()
        
        assert health["overall_status"] == "degraded"
        assert health["tiers"]["tier1"]["status"] == "error"
    
    def test_get_health_status_includes_timestamp(self, entry):
        """Test health status includes timestamp."""
        health = entry.get_health_status()
        
        assert "timestamp" in health
        assert "2025" in health["timestamp"]


class TestErrorHandling:
    """Test error handling in entry point."""
    
    @pytest.fixture
    def entry(self):
        """Create entry point for error testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            
            # Mock session
            entry.session_manager.start_session = Mock(return_value="error-conv")
            entry.session_manager.get_active_session = Mock(return_value=None)
            
            # Mock tier1
            entry.tier1.process_message = Mock()
            
            yield entry
    
    def test_process_with_router_error(self, entry):
        """Test graceful handling of router errors."""
        entry.router.execute = Mock(side_effect=Exception("Router failed"))
        
        response = entry.process("Test message")
        
        assert response is not None
        assert "ERROR" in response
        assert "Router failed" in response
    
    def test_process_batch_with_partial_errors(self, entry):
        """Test batch processing with some errors."""
        # First call succeeds, second fails, third succeeds
        entry.router.execute = Mock(side_effect=[
            AgentResponse(True, {}, "Success", "Agent"),
            Exception("Middle error"),
            AgentResponse(True, {}, "Success", "Agent"),
        ])
        
        response = entry.process_batch(["Msg1", "Msg2", "Msg3"])
        
        assert response is not None
        # Should still return response even with errors
        assert "Response" in response or "successful" in response


class TestIntegrationWithTiers:
    """Test integration with Tier 1, 2, 3 APIs."""
    
    @pytest.fixture
    def entry(self):
        """Create entry point with tier integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = Path(tmpdir)
            (brain / "tier1").mkdir(parents=True)
            (brain / "tier2").mkdir(parents=True)
            (brain / "tier3").mkdir(parents=True)
            
            entry = CortexEntry(brain_path=str(brain), enable_logging=False)
            
            # Mock router
            entry.router.execute = Mock(return_value=AgentResponse(
                success=True,
                result={"action": "created_file"},
                message="File created",
                agent_name="CodeExecutor"
            ))
            
            # Real tier mocks
            entry.tier1.process_message = Mock()
            entry.tier1.get_summary = Mock(return_value={})
            
            entry.tier2.get_statistics = Mock(return_value={
                "total_patterns": 15
            })
            
            entry.tier3.get_context_summary = Mock(return_value={
                "velocity": {"trend": "stable"}
            })
            
            # Mock session
            entry.session_manager.start_session = Mock(return_value="integration-conv")
            entry.session_manager.get_active_session = Mock(return_value=None)
            
            yield entry
    
    def test_router_receives_tier_apis(self, entry):
        """Test router is initialized with tier APIs."""
        assert entry.router.tier1 is not None
        assert entry.router.tier2 is not None
        assert entry.router.tier3 is not None
    
    def test_conversation_logged_to_tier1(self, entry):
        """Test conversation is logged to Tier 1."""
        entry.process("Test message")
        
        # Verify Tier 1 received messages
        assert entry.tier1.process_message.called
        
        # Should log both user and assistant messages
        assert entry.tier1.process_message.call_count >= 2
    
    def test_health_checks_all_tiers(self, entry):
        """Test health check queries all tiers."""
        health = entry.get_health_status()
        
        # Should call tier APIs
        entry.tier1.get_summary.assert_called_once()
        entry.tier2.get_statistics.assert_called_once()
        entry.tier3.get_context_summary.assert_called_once()
        
        # Health should include all tiers
        assert "tier1" in health["tiers"]
        assert "tier2" in health["tiers"]
        assert "tier3" in health["tiers"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
