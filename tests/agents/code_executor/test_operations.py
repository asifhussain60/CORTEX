"""Tests for CodeExecutor operations."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

from src.cortex_agents.code_executor.operations import (
    CreateOperation,
    EditOperation,
    DeleteOperation,
    BatchOperation
)
from src.cortex_agents.code_executor.validators import SyntaxValidator
from src.cortex_agents.code_executor.backup import BackupManager


class TestCreateOperation:
    """Test CreateOperation functionality."""
    
    def test_create_new_file(self):
        """Test creating a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            content = "def hello():\n    pass"
            
            op = CreateOperation()
            result = op.execute(file_path, {"content": content})
            
            assert result["success"] is True
            assert result["operation"] == "create"
            assert os.path.exists(file_path)
            assert Path(file_path).read_text() == content
    
    def test_create_with_existing_file(self):
        """Test creating file when it already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("existing")
            
            op = CreateOperation()
            result = op.execute(file_path, {"content": "new"})
            
            assert result["success"] is False
            assert "already exists" in result["message"]
    
    def test_create_with_overwrite(self):
        """Test creating file with overwrite flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("existing")
            
            op = CreateOperation()
            result = op.execute(file_path, {"content": "new", "overwrite": True})
            
            assert result["success"] is True
            assert Path(file_path).read_text() == "new"
    
    def test_create_with_invalid_syntax(self):
        """Test creating file with invalid Python syntax."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            invalid_content = "def hello(\n    pass"  # Missing closing paren
            
            validator = SyntaxValidator()
            op = CreateOperation(validator=validator)
            result = op.execute(file_path, {"content": invalid_content})
            
            assert result["success"] is False
            assert "validation" in result["message"].lower()
    
    def test_create_nested_directory(self):
        """Test creating file in nested directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nested", "dir", "test.py")
            
            op = CreateOperation()
            result = op.execute(file_path, {"content": "# test"})
            
            assert result["success"] is True
            assert os.path.exists(file_path)


class TestEditOperation:
    """Test EditOperation functionality."""
    
    def test_edit_existing_file(self):
        """Test editing an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("old content")
            
            op = EditOperation()
            result = op.execute(file_path, {"content": "new content"})
            
            assert result["success"] is True
            assert result["operation"] == "edit"
            assert Path(file_path).read_text() == "new content"
    
    def test_edit_nonexistent_file(self):
        """Test editing a file that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.py")
            
            op = EditOperation()
            result = op.execute(file_path, {"content": "new"})
            
            assert result["success"] is False
            assert "not found" in result["message"].lower()
    
    def test_edit_with_string_replacement(self):
        """Test editing file with old_string/new_string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("def old():\n    pass")
            
            op = EditOperation()
            result = op.execute(file_path, {
                "old_string": "old",
                "new_string": "new"
            })
            
            assert result["success"] is True
            assert "def new():" in Path(file_path).read_text()
    
    def test_edit_with_backup(self):
        """Test that editing creates a backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            original_content = "original"
            Path(file_path).write_text(original_content)
            
            backup_mgr = BackupManager()
            backup_mgr.create_backup_dir()
            
            op = EditOperation(backup_manager=backup_mgr)
            result = op.execute(file_path, {"content": "modified"})
            
            assert result["success"] is True
            assert result["backup_path"] is not None
            assert os.path.exists(result["backup_path"])
    
    def test_edit_with_validation_failure(self):
        """Test editing with syntax validation failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("def hello():\n    pass")
            
            invalid_content = "def bad(\n    pass"
            
            validator = SyntaxValidator()
            op = EditOperation(validator=validator)
            result = op.execute(file_path, {"content": invalid_content})
            
            assert result["success"] is False
            # Original file should be unchanged
            assert "def hello():" in Path(file_path).read_text()


class TestDeleteOperation:
    """Test DeleteOperation functionality."""
    
    def test_delete_existing_file(self):
        """Test deleting an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("content")
            
            op = DeleteOperation()
            result = op.execute(file_path, {"confirm": True})
            
            assert result["success"] is True
            assert result["operation"] == "delete"
            assert not os.path.exists(file_path)
    
    def test_delete_without_confirmation(self):
        """Test deleting without confirmation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("content")
            
            op = DeleteOperation()
            result = op.execute(file_path, {"confirm": False})
            
            assert result["success"] is False
            assert "confirmation" in result["message"].lower()
            assert os.path.exists(file_path)
    
    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "nonexistent.py")
            
            op = DeleteOperation()
            result = op.execute(file_path, {"confirm": True})
            
            assert result["success"] is False
            assert "not found" in result["message"].lower()
    
    def test_delete_with_backup(self):
        """Test that deletion creates a backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            Path(file_path).write_text("content")
            
            backup_mgr = BackupManager()
            backup_mgr.create_backup_dir()
            
            op = DeleteOperation(backup_manager=backup_mgr)
            result = op.execute(file_path, {"confirm": True})
            
            assert result["success"] is True
            assert result["backup_path"] is not None
            assert os.path.exists(result["backup_path"])


class TestBatchOperation:
    """Test BatchOperation functionality."""
    
    def test_batch_multiple_creates(self):
        """Test batch creation of multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            operations = [
                {"operation": "create", "file_path": os.path.join(tmpdir, "file1.py"), "content": "# file1"},
                {"operation": "create", "file_path": os.path.join(tmpdir, "file2.py"), "content": "# file2"},
            ]
            
            op = BatchOperation()
            result = op.execute("", {"operations": operations})
            
            assert result["success"] is True
            assert result["operations_completed"] == 2
            assert result["operations_failed"] == 0
            assert len(result["files_modified"]) == 2
    
    def test_batch_mixed_operations(self):
        """Test batch with mixed operation types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial file
            existing_file = os.path.join(tmpdir, "existing.py")
            Path(existing_file).write_text("old")
            
            operations = [
                {"operation": "create", "file_path": os.path.join(tmpdir, "new.py"), "content": "new"},
                {"operation": "edit", "file_path": existing_file, "content": "updated"},
            ]
            
            op = BatchOperation()
            result = op.execute("", {"operations": operations})
            
            assert result["success"] is True
            assert result["operations_completed"] == 2
    
    def test_batch_with_failures(self):
        """Test batch operation with some failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            operations = [
                {"operation": "create", "file_path": os.path.join(tmpdir, "good.py"), "content": "# good"},
                {"operation": "edit", "file_path": "/nonexistent/bad.py", "content": "bad"},
            ]
            
            op = BatchOperation()
            result = op.execute("", {"operations": operations})
            
            assert result["success"] is False  # At least one failure
            assert result["operations_completed"] >= 1
            assert result["operations_failed"] >= 1
    
    def test_batch_empty_operations(self):
        """Test batch with no operations."""
        op = BatchOperation()
        result = op.execute("", {"operations": []})
        
        assert result["success"] is False
        assert "no operations" in result["message"].lower()
