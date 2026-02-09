"""
Stage 2: LocalFileSystemProvider Implementation Tests

AC-PHASE50-S2-001: LocalFileSystemProvider wraps filesystem operations with abstraction
AC-PHASE50-S2-002: Supports all IKnowledgeProvider methods (read, write, list, exists, delete)
AC-PHASE50-S2-003: Error handling maps filesystem errors to StorageError hierarchy
AC-PHASE50-S2-004: Path normalization and validation prevents directory traversal
AC-PHASE50-S2-005: Supports relative and absolute paths

Target: 15 tests, 100% pass rate for Stage 2
"""

import os
import tempfile
import pytest
from pathlib import Path

from cortex.storage.provider import IKnowledgeProvider
from cortex.storage.config import StorageConfig
from cortex.storage.errors import (
    StorageError,
    PermissionError,
    NotFoundError,
    ConfigurationError,
)
from cortex.storage.providers.local import LocalFileSystemProvider


class TestLocalFileSystemProviderInitialization:
    """AC-PHASE50-S2-001: Provider initialization and configuration"""

    def test_local_provider_implements_interface(self):
        """LocalFileSystemProvider is instance of IKnowledgeProvider"""
        config = StorageConfig(backend="local", endpoint="/tmp/test")
        provider = LocalFileSystemProvider(config)
        assert isinstance(provider, IKnowledgeProvider)

    def test_local_provider_stores_config(self):
        """LocalFileSystemProvider stores StorageConfig reference"""
        config = StorageConfig(backend="local", endpoint="/tmp/test")
        provider = LocalFileSystemProvider(config)
        assert provider.config == config

    def test_local_provider_requires_endpoint(self):
        """LocalFileSystemProvider requires endpoint for base directory"""
        config = StorageConfig(backend="local", endpoint=None)
        with pytest.raises((ConfigurationError, TypeError, ValueError)):
            LocalFileSystemProvider(config)

    def test_local_provider_creates_base_directory(self):
        """LocalFileSystemProvider creates base directory if missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = os.path.join(tmpdir, "new_storage")
            config = StorageConfig(backend="local", endpoint=base_path)
            provider = LocalFileSystemProvider(config)
            assert os.path.exists(base_path)


class TestLocalFileSystemProviderReadMethod:
    """AC-PHASE50-S2-002: read() method implementation"""

    def test_read_existing_file(self):
        """read() returns content of existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            test_file = "test.txt"
            test_content = "Hello, World!"
            
            # Create test file
            file_path = os.path.join(tmpdir, test_file)
            with open(file_path, "w") as f:
                f.write(test_content)
            
            # Test
            result = provider.read(test_file)
            assert result == test_content

    def test_read_nonexistent_file_raises_not_found(self):
        """read() raises NotFoundError for missing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            with pytest.raises(NotFoundError):
                provider.read("nonexistent.txt")

    def test_read_file_with_relative_path(self):
        """read() handles relative paths within base directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            # Create nested structure
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir, exist_ok=True)
            test_content = "Nested content"
            file_path = os.path.join(subdir, "nested.txt")
            with open(file_path, "w") as f:
                f.write(test_content)
            
            # Test relative path access
            result = provider.read("subdir/nested.txt")
            assert result == test_content

    def test_read_prevents_directory_traversal(self):
        """read() prevents access outside base directory via path traversal"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            # Attempt directory traversal
            with pytest.raises((StorageError, PermissionError, NotFoundError)):
                provider.read("../../../etc/passwd")


class TestLocalFileSystemProviderWriteMethod:
    """AC-PHASE50-S2-002: write() method implementation"""

    def test_write_creates_new_file(self):
        """write() creates new file with content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            test_file = "new_file.txt"
            test_content = "New content"
            
            provider.write(test_file, test_content)
            
            # Verify file was created
            file_path = os.path.join(tmpdir, test_file)
            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == test_content

    def test_write_overwrites_existing_file(self):
        """write() overwrites existing file content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            test_file = "overwrite.txt"
            
            # Write initial content
            provider.write(test_file, "Initial")
            # Overwrite
            provider.write(test_file, "Updated")
            
            # Verify overwrite
            file_path = os.path.join(tmpdir, test_file)
            with open(file_path, "r") as f:
                assert f.read() == "Updated"

    def test_write_creates_parent_directories(self):
        """write() creates parent directories for nested paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            nested_path = "deep/nested/path/file.txt"
            content = "Nested content"
            
            provider.write(nested_path, content)
            
            # Verify structure created
            full_path = os.path.join(tmpdir, nested_path)
            assert os.path.exists(full_path)
            with open(full_path, "r") as f:
                assert f.read() == content


class TestLocalFileSystemProviderListMethod:
    """AC-PHASE50-S2-002: list() method implementation"""

    def test_list_directory_contents(self):
        """list() returns all files and directories in path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            # Create test structure
            os.makedirs(os.path.join(tmpdir, "subdir"), exist_ok=True)
            with open(os.path.join(tmpdir, "file1.txt"), "w") as f:
                f.write("content1")
            with open(os.path.join(tmpdir, "file2.txt"), "w") as f:
                f.write("content2")
            
            # Test
            result = provider.list("")
            assert "file1.txt" in result
            assert "file2.txt" in result
            assert "subdir" in result

    def test_list_empty_directory(self):
        """list() returns empty list for empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            result = provider.list("")
            assert result == []

    def test_list_nonexistent_directory(self):
        """list() raises NotFoundError for missing directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            with pytest.raises(NotFoundError):
                provider.list("nonexistent")


class TestLocalFileSystemProviderExistsMethod:
    """AC-PHASE50-S2-002: exists() method implementation"""

    def test_exists_returns_true_for_existing_file(self):
        """exists() returns True for existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            test_file = "exists.txt"
            
            with open(os.path.join(tmpdir, test_file), "w") as f:
                f.write("content")
            
            assert provider.exists(test_file) is True

    def test_exists_returns_false_for_missing_file(self):
        """exists() returns False for missing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            assert provider.exists("nonexistent.txt") is False

    def test_exists_handles_directories(self):
        """exists() returns True for existing directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir, exist_ok=True)
            
            assert provider.exists("subdir") is True


class TestLocalFileSystemProviderDeleteMethod:
    """AC-PHASE50-S2-002: delete() method implementation"""

    def test_delete_removes_existing_file(self):
        """delete() removes existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            test_file = "delete_me.txt"
            
            # Create file
            with open(os.path.join(tmpdir, test_file), "w") as f:
                f.write("content")
            
            # Delete
            provider.delete(test_file)
            
            # Verify deletion
            assert not os.path.exists(os.path.join(tmpdir, test_file))

    def test_delete_nonexistent_file_raises_not_found(self):
        """delete() raises NotFoundError for missing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            with pytest.raises(NotFoundError):
                provider.delete("nonexistent.txt")

    def test_delete_empty_directory(self):
        """delete() can remove empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(backend="local", endpoint=tmpdir)
            provider = LocalFileSystemProvider(config)
            
            # Create empty directory
            subdir = os.path.join(tmpdir, "empty_dir")
            os.makedirs(subdir, exist_ok=True)
            
            # Delete
            provider.delete("empty_dir")
            
            # Verify deletion
            assert not os.path.exists(subdir)
