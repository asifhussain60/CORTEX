"""
Tests for CodeExecutor Agent

Tests safe code execution functionality including file operations,
syntax validation, backup/rollback, and batch processing.
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.cortex_agents.code_executor import CodeExecutor
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class TestCodeExecutorBasics:
    """Test basic CodeExecutor functionality."""
    
    def test_initialization(self):
        """Test agent initialization."""
        executor = CodeExecutor(name="TestExecutor")
        
        assert executor.name == "TestExecutor"
        assert "create" in executor.OPERATIONS
        assert "edit" in executor.OPERATIONS
        assert "delete" in executor.OPERATIONS
        assert ".py" in executor.SYNTAX_CHECK_EXTENSIONS
    
    def test_can_handle_execute_code(self):
        """Test can_handle for code intent."""
        executor = CodeExecutor(name="TestExecutor")
        
        request = AgentRequest(
            intent=IntentType.CODE.value,
            context={},
            user_message="Execute code changes"
        )
        
        assert executor.can_handle(request) is True
    
    def test_can_handle_code_intent(self):
        """Test can_handle for code intent."""
        executor = CodeExecutor(name="TestExecutor")
        
        request = AgentRequest(
            intent=IntentType.CODE.value,
            context={},
            user_message="Write code"
        )
        
        assert executor.can_handle(request) is True
    
    def test_can_handle_string_intents(self):
        """Test can_handle for string variants."""
        executor = CodeExecutor(name="TestExecutor")
        
        for intent in ["execute", "code", "write", "modify", "create_file"]:
            request = AgentRequest(
                intent=intent,
                context={},
                user_message="Do something"
            )
            assert executor.can_handle(request) is True
    
    def test_cannot_handle_other_intents(self):
        """Test can_handle rejects non-code intents."""
        executor = CodeExecutor(name="TestExecutor")
        
        request = AgentRequest(
            intent=IntentType.PLAN.value,
            context={},
            user_message="Plan something"
        )
        
        assert executor.can_handle(request) is False


class TestFileCreation:
    """Test file creation operations."""
    
    def test_create_new_file(self):
        """Test creating a new file."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            content = "Hello, World!"
            
            result = executor._create_file(file_path, {"content": content})
            
            assert result["success"] is True
            assert result["file_path"] == file_path
            assert result["operation"] == "create"
            assert os.path.exists(file_path)
            
            with open(file_path, 'r') as f:
                assert f.read() == content
    
    def test_create_file_with_directories(self):
        """Test creating file with nested directories."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "sub", "dir", "test.txt")
            
            result = executor._create_file(file_path, {"content": "test"})
            
            assert result["success"] is True
            assert os.path.exists(file_path)
            assert os.path.exists(os.path.dirname(file_path))
    
    def test_create_file_already_exists(self):
        """Test creating file that already exists."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            
            # Create file first
            with open(file_path, 'w') as f:
                f.write("original")
            
            # Try to create again without overwrite
            result = executor._create_file(file_path, {"content": "new"})
            
            assert result["success"] is False
            assert "already exists" in result["message"].lower()
    
    def test_create_file_with_overwrite(self):
        """Test creating file with overwrite flag."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            
            # Create file first
            with open(file_path, 'w') as f:
                f.write("original")
            
            # Create with overwrite
            result = executor._create_file(
                file_path,
                {"content": "new", "overwrite": True}
            )
            
            assert result["success"] is True
            
            with open(file_path, 'r') as f:
                assert f.read() == "new"
    
    def test_create_python_file_with_syntax_validation(self):
        """Test creating Python file with valid syntax."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            content = "def hello():\n    return 'world'\n"
            
            result = executor._create_file(file_path, {"content": content})
            
            assert result["success"] is True
            assert os.path.exists(file_path)
    
    def test_create_python_file_with_syntax_error(self):
        """Test creating Python file with invalid syntax."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            content = "def hello(\n    return 'world'\n"  # Missing closing paren
            
            result = executor._create_file(file_path, {"content": content})
            
            assert result["success"] is False
            assert "syntax" in result["message"].lower()
            assert "validation_error" in result


class TestFileEditing:
    """Test file editing operations."""
    
    def test_edit_existing_file(self):
        """Test editing an existing file."""
        executor = CodeExecutor(name="TestExecutor")
        executor.backup_dir = tempfile.mkdtemp()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, "test.txt")
                
                # Create original file
                with open(file_path, 'w') as f:
                    f.write("original content")
                
                # Edit file
                result = executor._edit_file(
                    file_path,
                    {"content": "new content"}
                )
                
                assert result["success"] is True
                assert result["operation"] == "edit"
                assert "backup_path" in result
                
                with open(file_path, 'r') as f:
                    assert f.read() == "new content"
        finally:
            if os.path.exists(executor.backup_dir):
                shutil.rmtree(executor.backup_dir)
    
    def test_edit_file_with_string_replacement(self):
        """Test editing file using old_string/new_string."""
        executor = CodeExecutor(name="TestExecutor")
        executor.backup_dir = tempfile.mkdtemp()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, "test.txt")
                
                with open(file_path, 'w') as f:
                    f.write("Hello World")
                
                result = executor._edit_file(
                    file_path,
                    {"old_string": "World", "new_string": "Python"}
                )
                
                assert result["success"] is True
                
                with open(file_path, 'r') as f:
                    assert f.read() == "Hello Python"
        finally:
            if os.path.exists(executor.backup_dir):
                shutil.rmtree(executor.backup_dir)
    
    def test_edit_nonexistent_file(self):
        """Test editing file that doesn't exist."""
        executor = CodeExecutor(name="TestExecutor")
        
        result = executor._edit_file(
            "/nonexistent/file.txt",
            {"content": "new"}
        )
        
        assert result["success"] is False
        assert "not found" in result["message"].lower()
    
    def test_edit_python_file_with_syntax_validation(self):
        """Test editing Python file validates syntax."""
        executor = CodeExecutor(name="TestExecutor")
        executor.backup_dir = tempfile.mkdtemp()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, "test.py")
                
                with open(file_path, 'w') as f:
                    f.write("def hello():\n    pass\n")
                
                # Edit with invalid syntax
                result = executor._edit_file(
                    file_path,
                    {"content": "def broken(\n    pass\n"}
                )
                
                assert result["success"] is False
                assert "syntax" in result["message"].lower()
        finally:
            if os.path.exists(executor.backup_dir):
                shutil.rmtree(executor.backup_dir)


class TestFileDeletion:
    """Test file deletion operations."""
    
    def test_delete_file_with_confirmation(self):
        """Test deleting file with confirmation."""
        executor = CodeExecutor(name="TestExecutor")
        executor.backup_dir = tempfile.mkdtemp()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, "test.txt")
                
                with open(file_path, 'w') as f:
                    f.write("content")
                
                result = executor._delete_file(
                    file_path,
                    {"confirm": True}
                )
                
                assert result["success"] is True
                assert result["operation"] == "delete"
                assert not os.path.exists(file_path)
                assert "backup_path" in result
        finally:
            if os.path.exists(executor.backup_dir):
                shutil.rmtree(executor.backup_dir)
    
    def test_delete_file_without_confirmation(self):
        """Test deleting file requires confirmation."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            
            with open(file_path, 'w') as f:
                f.write("content")
            
            result = executor._delete_file(file_path, {})
            
            assert result["success"] is False
            assert "confirmation" in result["message"].lower()
            assert os.path.exists(file_path)  # File still exists
    
    def test_delete_nonexistent_file(self):
        """Test deleting file that doesn't exist."""
        executor = CodeExecutor(name="TestExecutor")
        
        result = executor._delete_file(
            "/nonexistent/file.txt",
            {"confirm": True}
        )
        
        assert result["success"] is False
        assert "not found" in result["message"].lower()


class TestBatchOperations:
    """Test batch operation execution."""
    
    def test_batch_create_multiple_files(self):
        """Test batch creation of multiple files."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            operations = [
                {
                    "operation": "create",
                    "file_path": os.path.join(tmpdir, "file1.txt"),
                    "content": "content1"
                },
                {
                    "operation": "create",
                    "file_path": os.path.join(tmpdir, "file2.txt"),
                    "content": "content2"
                }
            ]
            
            result = executor._execute_batch(
                AgentRequest(
                    intent="execute",
                    context={"operations": operations},
                    user_message="Batch create"
                )
            )
            
            assert result["success"] is True
            assert result["operations_completed"] == 2
            assert result["operations_failed"] == 0
            assert len(result["files_modified"]) == 2
    
    def test_batch_with_failures(self):
        """Test batch operations with some failures."""
        executor = CodeExecutor(name="TestExecutor")
        
        operations = [
            {
                "operation": "create",
                # Missing file_path
                "content": "content"
            },
            {
                "operation": "edit",
                "file_path": "/nonexistent/file.txt",
                "content": "new"
            }
        ]
        
        result = executor._execute_batch(
            AgentRequest(
                intent="execute",
                context={"operations": operations},
                user_message="Batch test"
            )
        )
        
        assert result["success"] is False
        assert result["operations_failed"] == 2


class TestCodeExecutorIntegration:
    """Test full CodeExecutor workflow."""
    
    def test_execute_create_operation(self):
        """Test full execute with create operation."""
        executor = CodeExecutor(name="TestExecutor")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            
            request = AgentRequest(
                intent=IntentType.CODE.value,
                context={
                    "operation": "create",
                    "file_path": file_path,
                    "content": "Test content"
                },
                user_message="Create a test file"
            )
            
            response = executor.execute(request)
            
            assert response.success is True
            assert response.result["success"] is True
            assert os.path.exists(file_path)
            assert response.metadata["operation"] == "create"
    
    def test_execute_with_invalid_operation(self):
        """Test execute with invalid operation type."""
        executor = CodeExecutor(name="TestExecutor")
        
        request = AgentRequest(
            intent=IntentType.CODE.value,
            context={"operation": "invalid_op"},
            user_message="Do something"
        )
        
        response = executor.execute(request)
        
        assert response.success is False
        assert "unknown operation" in response.message.lower()
    
    def test_suggest_actions_on_success(self):
        """Test action suggestions after successful execution."""
        executor = CodeExecutor(name="TestExecutor")
        
        result = {"success": True, "operation": "create"}
        actions = executor._suggest_next_actions(result)
        
        assert len(actions) > 0
        assert any("test" in a.lower() for a in actions)
    
    def test_suggest_actions_on_failure(self):
        """Test action suggestions after failed execution."""
        executor = CodeExecutor(name="TestExecutor")
        
        result = {
            "success": False,
            "validation_error": "Syntax error"
        }
        actions = executor._suggest_next_actions(result)
        
        assert len(actions) > 0
        assert any("syntax" in a.lower() or "error" in a.lower() for a in actions)


class TestSyntaxValidation:
    """Test syntax validation functionality."""
    
    def test_should_validate_python(self):
        """Test Python files are marked for validation."""
        executor = CodeExecutor(name="TestExecutor")
        
        assert executor._should_validate_syntax("test.py") is True
        assert executor._should_validate_syntax("module.py") is True
    
    def test_should_not_validate_text(self):
        """Test text files skip validation."""
        executor = CodeExecutor(name="TestExecutor")
        
        assert executor._should_validate_syntax("test.txt") is False
        assert executor._should_validate_syntax("README.md") is False
    
    def test_validate_valid_python_syntax(self):
        """Test validation of valid Python code."""
        executor = CodeExecutor(name="TestExecutor")
        
        valid_code = "def hello():\n    return 'world'\n"
        is_valid, error = executor._validate_syntax(valid_code, "test.py")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_python_syntax(self):
        """Test validation of invalid Python code."""
        executor = CodeExecutor(name="TestExecutor")
        
        invalid_code = "def hello(\n    return 'world'\n"
        is_valid, error = executor._validate_syntax(invalid_code, "test.py")
        
        assert is_valid is False
        assert error is not None
        assert "syntax error" in error.lower()


class TestBackupAndRollback:
    """Test backup and rollback functionality."""
    
    def test_create_backup_dir(self):
        """Test backup directory creation."""
        executor = CodeExecutor(name="TestExecutor")
        executor.current_operation_id = "test_op_123"
        
        backup_dir = executor._create_backup_dir()
        
        assert os.path.exists(backup_dir)
        assert "cortex_backup" in backup_dir
        
        # Cleanup
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
    
    def test_backup_file(self):
        """Test file backup."""
        executor = CodeExecutor(name="TestExecutor")
        executor.backup_dir = tempfile.mkdtemp()
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, "test.txt")
                
                with open(file_path, 'w') as f:
                    f.write("original")
                
                backup_path = executor._backup_file(file_path)
                
                assert backup_path is not None
                assert os.path.exists(backup_path)
                
                with open(backup_path, 'r') as f:
                    assert f.read() == "original"
        finally:
            if os.path.exists(executor.backup_dir):
                shutil.rmtree(executor.backup_dir)
