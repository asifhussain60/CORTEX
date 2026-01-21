"""
Tests for REMEDIATION-002 Phase B: File Utilities Centralization.

AC-REM-002-04: Centralize file I/O operations into cortex/common/file_utils.py.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
from pathlib import Path
from typing import Any, Dict


class TestFileOperationsRead(unittest.TestCase):
    """Tests for file reading utilities."""
    
    def test_read_text_file(self) -> None:
        """read_text should read file contents as string."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, World!")
            temp_path = f.name
        
        try:
            content = FileOperations.read_text(temp_path)
            self.assertEqual(content, "Hello, World!")
        finally:
            os.unlink(temp_path)
    
    def test_read_text_file_not_found(self) -> None:
        """read_text should raise FileNotFoundError for missing file."""
        from cortex.common.file_utils import FileOperations
        
        with self.assertRaises(FileNotFoundError):
            FileOperations.read_text("/nonexistent/file.txt")
    
    def test_read_yaml_file(self) -> None:
        """read_yaml should parse YAML file to dict."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("key: value\nlist:\n  - item1\n  - item2")
            temp_path = f.name
        
        try:
            data = FileOperations.read_yaml(temp_path)
            self.assertEqual(data["key"], "value")
            self.assertEqual(data["list"], ["item1", "item2"])
        finally:
            os.unlink(temp_path)
    
    def test_read_yaml_invalid_file(self) -> None:
        """read_yaml should raise YAMLError for invalid YAML."""
        from cortex.common.file_utils import FileOperations
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            with self.assertRaises(yaml.YAMLError):
                FileOperations.read_yaml(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_read_json_file(self) -> None:
        """read_json should parse JSON file to dict."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value", "number": 42}')
            temp_path = f.name
        
        try:
            data = FileOperations.read_json(temp_path)
            self.assertEqual(data["key"], "value")
            self.assertEqual(data["number"], 42)
        finally:
            os.unlink(temp_path)
    
    def test_read_lines(self) -> None:
        """read_lines should return list of lines."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("line1\nline2\nline3")
            temp_path = f.name
        
        try:
            lines = FileOperations.read_lines(temp_path)
            self.assertEqual(lines, ["line1", "line2", "line3"])
        finally:
            os.unlink(temp_path)


class TestFileOperationsWrite(unittest.TestCase):
    """Tests for file writing utilities."""
    
    def test_write_text_file(self) -> None:
        """write_text should write string to file."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            FileOperations.write_text(path, "Hello!")
            
            self.assertTrue(path.exists())
            self.assertEqual(path.read_text(), "Hello!")
    
    def test_write_yaml_file(self) -> None:
        """write_yaml should write dict as YAML."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            data = {"key": "value", "list": [1, 2, 3]}
            FileOperations.write_yaml(path, data)
            
            self.assertTrue(path.exists())
            content = path.read_text()
            self.assertIn("key: value", content)
    
    def test_write_json_file(self) -> None:
        """write_json should write dict as JSON."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            data = {"key": "value", "number": 42}
            FileOperations.write_json(path, data)
            
            self.assertTrue(path.exists())
            content = path.read_text()
            self.assertIn('"key"', content)
    
    def test_write_creates_parent_dirs(self) -> None:
        """write operations should create parent directories."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "test.txt"
            FileOperations.write_text(path, "nested content")
            
            self.assertTrue(path.exists())


class TestFileOperationsUtility(unittest.TestCase):
    """Tests for utility file operations."""
    
    def test_exists(self) -> None:
        """exists should return True for existing file."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            self.assertTrue(FileOperations.exists(temp_path))
            self.assertFalse(FileOperations.exists("/nonexistent/path"))
        finally:
            os.unlink(temp_path)
    
    def test_ensure_dir(self) -> None:
        """ensure_dir should create directory if not exists."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_directory"
            FileOperations.ensure_dir(new_dir)
            
            self.assertTrue(new_dir.exists())
            self.assertTrue(new_dir.is_dir())
    
    def test_safe_delete(self) -> None:
        """safe_delete should delete file without raising on missing."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        # Should succeed
        FileOperations.safe_delete(temp_path)
        self.assertFalse(os.path.exists(temp_path))
        
        # Should not raise on missing file
        FileOperations.safe_delete("/nonexistent/file.txt")


class TestFileOperationsBackup(unittest.TestCase):
    """Tests for backup functionality."""
    
    def test_backup_file(self) -> None:
        """backup should create timestamped backup copy."""
        from cortex.common.file_utils import FileOperations
        
        with tempfile.TemporaryDirectory() as tmpdir:
            original = Path(tmpdir) / "original.txt"
            original.write_text("original content")
            
            backup_path = FileOperations.backup(original)
            
            self.assertTrue(backup_path.exists())
            self.assertIn("original", backup_path.name)
            self.assertEqual(backup_path.read_text(), "original content")


class TestAtomicFileWrite(unittest.TestCase):
    """Tests for atomic file writing."""
    
    def test_atomic_write_success(self) -> None:
        """atomic_write should write file atomically."""
        from cortex.common.file_utils import atomic_write
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "atomic.txt"
            
            with atomic_write(path) as f:
                f.write("atomic content")
            
            self.assertTrue(path.exists())
            self.assertEqual(path.read_text(), "atomic content")
    
    def test_atomic_write_failure_cleans_up(self) -> None:
        """atomic_write should clean up temp file on failure."""
        from cortex.common.file_utils import atomic_write
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "atomic_fail.txt"
            
            try:
                with atomic_write(path) as f:
                    f.write("partial content")
                    raise ValueError("Intentional failure")
            except ValueError:
                pass
            
            # File should not exist after failed write
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
