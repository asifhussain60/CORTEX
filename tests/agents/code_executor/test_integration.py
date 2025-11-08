"""Integration tests for CodeExecutor agent."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

from src.cortex_agents.code_executor import CodeExecutor
from src.cortex_agents.base_agent import AgentRequest


class TestCodeExecutorIntegration:
    """Test CodeExecutor agent integration."""
    
    def test_agent_initialization(self):
        """Test agent initializes with all components."""
        agent = CodeExecutor("TestExecutor")
        
        assert agent.name == "TestExecutor"
        assert agent.validator is not None
        assert agent.OPERATIONS == ["create", "edit", "delete", "batch"]
    
    def test_can_handle_code_intent(self):
        """Test agent recognizes code intent."""
        agent = CodeExecutor("TestExecutor")
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Execute code"
        )
        
        assert agent.can_handle(request) is True
    
    def test_can_handle_create_file_intent(self):
        """Test agent recognizes create_file intent."""
        agent = CodeExecutor("TestExecutor")
        
        request = AgentRequest(
            intent="create_file",
            context={},
            user_message="Create a file"
        )
        
        assert agent.can_handle(request) is True
    
    def test_cannot_handle_other_intent(self):
        """Test agent rejects unrelated intents."""
        agent = CodeExecutor("TestExecutor")
        
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check health"
        )
        
        assert agent.can_handle(request) is False
    
    def test_execute_create_operation(self):
        """Test executing create operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "new.py")
            
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="create_file",
                context={
                    "operation": "create",
                    "file_path": file_path,
                    "content": "def hello():\n    pass"
                },
                user_message="Create file"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            assert os.path.exists(file_path)
            assert response.result["operation"] == "create"
    
    def test_execute_edit_operation(self):
        """Test executing edit operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "existing.py")
            Path(file_path).write_text("old content")
            
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="edit_file",
                context={
                    "operation": "edit",
                    "file_path": file_path,
                    "content": "new content"
                },
                user_message="Edit file"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            assert Path(file_path).read_text() == "new content"
    
    def test_execute_delete_operation(self):
        """Test executing delete operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "delete_me.py")
            Path(file_path).write_text("content")
            
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="delete_file",
                context={
                    "operation": "delete",
                    "file_path": file_path,
                    "confirm": True
                },
                user_message="Delete file"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            assert not os.path.exists(file_path)
    
    def test_execute_batch_operation(self):
        """Test executing batch operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="execute",
                context={
                    "operation": "batch",
                    "operations": [
                        {
                            "operation": "create",
                            "file_path": os.path.join(tmpdir, "file1.py"),
                            "content": "# file1"
                        },
                        {
                            "operation": "create",
                            "file_path": os.path.join(tmpdir, "file2.py"),
                            "content": "# file2"
                        }
                    ]
                },
                user_message="Batch create"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            assert response.result["operations_completed"] == 2
            assert len(response.result["files_modified"]) == 2
    
    def test_execute_with_validation_failure(self):
        """Test execution fails with invalid syntax."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "bad.py")
            
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="create_file",
                context={
                    "operation": "create",
                    "file_path": file_path,
                    "content": "def bad(\n    pass"  # Invalid syntax
                },
                user_message="Create bad file"
            )
            
            response = agent.execute(request)
            
            assert response.success is False
            assert not os.path.exists(file_path)
    
    def test_execute_creates_backup(self):
        """Test execution creates backup directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="create_file",
                context={
                    "operation": "create",
                    "file_path": file_path,
                    "content": "# test"
                },
                user_message="Create file"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            assert "backup_dir" in response.metadata
            assert response.metadata["backup_dir"] is not None
    
    def test_execute_with_tier1_logging(self):
        """Test execution logs to Tier 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            
            mock_tier1 = Mock()
            agent = CodeExecutor("TestExecutor", tier1_api=mock_tier1)
            
            request = AgentRequest(
                intent="create_file",
                context={
                    "operation": "create",
                    "file_path": file_path,
                    "content": "# test"
                },
                user_message="Create file",
                conversation_id="conv123"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            mock_tier1.process_message.assert_called_once()
    
    def test_response_includes_next_actions(self):
        """Test response includes suggested next actions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            
            agent = CodeExecutor("TestExecutor")
            request = AgentRequest(
                intent="create_file",
                context={
                    "operation": "create",
                    "file_path": file_path,
                    "content": "# test"
                },
                user_message="Create file"
            )
            
            response = agent.execute(request)
            
            assert response.success is True
            assert response.next_actions is not None
            assert len(response.next_actions) > 0
