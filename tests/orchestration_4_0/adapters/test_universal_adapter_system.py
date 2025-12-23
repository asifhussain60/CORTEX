"""
Comprehensive Tests for Universal Adapter System

Tests for base adapter, filesystem adapter, and factory pattern.
Target: 90%+ coverage for Phase 7B Task 7.6

Author: CORTEX 4.0
Created: December 23, 2025
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestration_4_0.adapters import (
    UniversalAdapter,
    ResourceType,
    AdapterResponse,
    AdapterError,
    AdapterFactory,
    FileSystemAdapter,
    AzureDevOpsAdapter,
    GitHubAdapter
)


# ==============================================================================
# Test Group 1: AdapterResponse and Error Handling (8 tests)
# ==============================================================================

class TestAdapterResponse:
    """Test standard response format"""
    
    def test_successful_response_with_data(self):
        """Test successful response includes data"""
        response = AdapterResponse(success=True, data={"key": "value"})
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error is None
    
    def test_failed_response_with_error(self):
        """Test failed response includes error message"""
        response = AdapterResponse(success=False, error="Something went wrong")
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.data is None
    
    def test_success_without_data_raises_error(self):
        """Test that success=True requires data"""
        with pytest.raises(ValueError, match="Success response must include data"):
            AdapterResponse(success=True, data=None)
    
    def test_failure_without_error_raises_error(self):
        """Test that success=False requires error message"""
        with pytest.raises(ValueError, match="Failure response must include error message"):
            AdapterResponse(success=False, error=None)
    
    def test_response_with_metadata(self):
        """Test response can include metadata"""
        response = AdapterResponse(
            success=True,
            data={"result": "ok"},
            metadata={"duration": 1.5, "retries": 2}
        )
        assert response.metadata["duration"] == 1.5
        assert response.metadata["retries"] == 2


class TestAdapterError:
    """Test custom adapter exception"""
    
    def test_adapter_error_with_message(self):
        """Test AdapterError with message only"""
        error = AdapterError("Test error")
        assert str(error) == "Test error"
        assert error.error_code is None
        assert error.details == {}
    
    def test_adapter_error_with_code_and_details(self):
        """Test AdapterError with code and details"""
        error = AdapterError(
            "Configuration invalid",
            error_code="INVALID_CONFIG",
            details={"field": "api_key", "reason": "missing"}
        )
        assert error.error_code == "INVALID_CONFIG"
        assert error.details["field"] == "api_key"
    
    def test_adapter_error_is_exception(self):
        """Test AdapterError can be raised and caught"""
        with pytest.raises(AdapterError) as exc_info:
            raise AdapterError("Test exception")
        assert "Test exception" in str(exc_info.value)


# ==============================================================================
# Test Group 2: AdapterFactory (8 tests)
# ==============================================================================

class TestAdapterFactory:
    """Test adapter factory pattern"""
    
    def test_register_adapter(self):
        """Test registering a new adapter type"""
        class CustomAdapter(UniversalAdapter):
            async def create(self, *args, **kwargs):
                pass
            async def read(self, *args, **kwargs):
                pass
            async def update(self, *args, **kwargs):
                pass
            async def delete(self, *args, **kwargs):
                pass
            async def search(self, *args, **kwargs):
                pass
            async def list(self, *args, **kwargs):
                pass
            def get_capabilities(self):
                return {}
            def validate_config(self):
                return True
        
        AdapterFactory.register("custom", CustomAdapter)
        assert "custom" in AdapterFactory.list_adapters()
    
    def test_create_filesystem_adapter(self):
        """Test creating filesystem adapter explicitly"""
        adapter = AdapterFactory.create("filesystem", {"base_path": "."})
        assert isinstance(adapter, FileSystemAdapter)
    
    def test_create_unknown_adapter_raises_error(self):
        """Test creating unknown adapter type raises ValueError"""
        with pytest.raises(ValueError, match="Unknown adapter type"):
            AdapterFactory.create("nonexistent")
    
    @patch.dict('os.environ', {'AZURE_DEVOPS_PAT': 'test-pat'})
    def test_auto_detect_azure_devops(self):
        """Test auto-detection selects Azure DevOps when PAT present"""
        adapter = AdapterFactory.auto_detect()
        assert isinstance(adapter, AzureDevOpsAdapter)
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'test-token'}, clear=True)
    def test_auto_detect_github(self):
        """Test auto-detection selects GitHub when token present"""
        adapter = AdapterFactory.auto_detect()
        assert isinstance(adapter, GitHubAdapter)
    
    @patch.dict('os.environ', {}, clear=True)
    def test_auto_detect_fallback_to_filesystem(self):
        """Test auto-detection falls back to filesystem"""
        adapter = AdapterFactory.auto_detect()
        assert isinstance(adapter, FileSystemAdapter)
    
    def test_auto_detect_with_preferred_adapter(self):
        """Test auto-detection respects preferred adapter"""
        adapter = AdapterFactory.auto_detect(preferred="filesystem")
        assert isinstance(adapter, FileSystemAdapter)
    
    def test_list_adapters(self):
        """Test listing registered adapters"""
        adapters = AdapterFactory.list_adapters()
        assert "filesystem" in adapters
        assert "azure_devops" in adapters
        assert "github" in adapters


# ==============================================================================
# Test Group 3: FileSystemAdapter - Create Operations (6 tests)
# ==============================================================================

@pytest.mark.asyncio
class TestFileSystemAdapterCreate:
    """Test filesystem adapter create operations"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def adapter(self, temp_dir):
        """Create filesystem adapter with temp directory"""
        return FileSystemAdapter({"base_path": str(temp_dir)})
    
    async def test_create_text_file(self, adapter, temp_dir):
        """Test creating plain text file"""
        response = await adapter.create(
            ResourceType.FILE,
            {"path": "test.txt", "content": "Hello, World!"}
        )
        assert response.success is True
        assert (temp_dir / "test.txt").exists()
        assert (temp_dir / "test.txt").read_text() == "Hello, World!"
    
    async def test_create_json_file(self, adapter, temp_dir):
        """Test creating JSON file"""
        data = {"name": "CORTEX", "version": "4.0"}
        response = await adapter.create(
            ResourceType.FILE,
            {"path": "config.json", "content": data, "format": "json"}
        )
        assert response.success is True
        created_data = json.loads((temp_dir / "config.json").read_text())
        assert created_data["name"] == "CORTEX"
    
    async def test_create_yaml_file(self, adapter, temp_dir):
        """Test creating YAML file"""
        data = {"enabled": True, "timeout": 30}
        response = await adapter.create(
            ResourceType.FILE,
            {"path": "config.yaml", "content": data, "format": "yaml"}
        )
        assert response.success is True
        created_data = yaml.safe_load((temp_dir / "config.yaml").read_text())
        assert created_data["enabled"] is True
    
    async def test_create_file_with_nested_path(self, adapter, temp_dir):
        """Test creating file in nested directories"""
        response = await adapter.create(
            ResourceType.FILE,
            {"path": "dir1/dir2/file.txt", "content": "Nested"}
        )
        assert response.success is True
        assert (temp_dir / "dir1" / "dir2" / "file.txt").exists()
    
    async def test_create_directory(self, adapter, temp_dir):
        """Test creating directory"""
        response = await adapter.create(
            ResourceType.REPOSITORY,
            {"path": "new_directory"}
        )
        assert response.success is True
        assert (temp_dir / "new_directory").is_dir()
    
    async def test_create_unsupported_resource_type(self, adapter):
        """Test creating unsupported resource type fails"""
        response = await adapter.create(
            ResourceType.WORK_ITEM,
            {"data": "test"}
        )
        assert response.success is False
        assert "Unsupported resource type" in response.error


# ==============================================================================
# Test Group 4: FileSystemAdapter - Read Operations (6 tests)
# ==============================================================================

@pytest.mark.asyncio
class TestFileSystemAdapterRead:
    """Test filesystem adapter read operations"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            (path / "test.txt").write_text("Hello")
            (path / "data.json").write_text('{"key": "value"}')
            (path / "config.yaml").write_text("setting: true")
            yield path
    
    @pytest.fixture
    def adapter(self, temp_dir):
        """Create filesystem adapter"""
        return FileSystemAdapter({"base_path": str(temp_dir)})
    
    async def test_read_text_file(self, adapter):
        """Test reading plain text file"""
        response = await adapter.read(ResourceType.FILE, "test.txt")
        assert response.success is True
        assert response.data["content"] == "Hello"
    
    async def test_read_json_file_auto_format(self, adapter):
        """Test reading JSON file with auto-detection"""
        response = await adapter.read(ResourceType.FILE, "data.json")
        assert response.success is True
        assert response.data["content"]["key"] == "value"
    
    async def test_read_yaml_file_auto_format(self, adapter):
        """Test reading YAML file with auto-detection"""
        response = await adapter.read(ResourceType.FILE, "config.yaml")
        assert response.success is True
        assert response.data["content"]["setting"] is True
    
    async def test_read_nonexistent_file(self, adapter):
        """Test reading non-existent file fails"""
        response = await adapter.read(ResourceType.FILE, "missing.txt")
        assert response.success is False
        assert "not found" in response.error.lower()
    
    async def test_read_directory_info(self, adapter, temp_dir):
        """Test reading directory information"""
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file1.txt").write_text("test1")
        (temp_dir / "subdir" / "file2.txt").write_text("test2")
        
        response = await adapter.read(ResourceType.REPOSITORY, "subdir")
        assert response.success is True
        assert response.data["file_count"] == 2
    
    async def test_read_with_explicit_format(self, adapter):
        """Test reading file with explicit format specification"""
        response = await adapter.read(ResourceType.FILE, "data.json", format="text")
        assert response.success is True
        assert isinstance(response.data["content"], str)


# ==============================================================================
# Test Group 5: FileSystemAdapter - Update & Delete (5 tests)
# ==============================================================================

@pytest.mark.asyncio
class TestFileSystemAdapterModify:
    """Test filesystem adapter update and delete operations"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            (path / "test.txt").write_text("Original")
            yield path
    
    @pytest.fixture
    def adapter(self, temp_dir):
        """Create filesystem adapter"""
        return FileSystemAdapter({"base_path": str(temp_dir)})
    
    async def test_update_file_content(self, adapter, temp_dir):
        """Test updating file content"""
        response = await adapter.update(
            ResourceType.FILE,
            "test.txt",
            {"content": "Updated"}
        )
        assert response.success is True
        assert (temp_dir / "test.txt").read_text() == "Updated"
    
    async def test_update_with_backup(self, adapter, temp_dir):
        """Test updating file with backup creation"""
        response = await adapter.update(
            ResourceType.FILE,
            "test.txt",
            {"content": "New content"},
            backup=True
        )
        assert response.success is True
        assert (temp_dir / "test.txt.bak").exists()
        assert (temp_dir / "test.txt.bak").read_text() == "Original"
    
    async def test_update_nonexistent_file(self, adapter):
        """Test updating non-existent file fails"""
        response = await adapter.update(
            ResourceType.FILE,
            "missing.txt",
            {"content": "test"}
        )
        assert response.success is False
    
    async def test_delete_file(self, adapter, temp_dir):
        """Test deleting file"""
        response = await adapter.delete(ResourceType.FILE, "test.txt")
        assert response.success is True
        assert not (temp_dir / "test.txt").exists()
    
    async def test_delete_nonexistent_resource(self, adapter):
        """Test deleting non-existent resource fails"""
        response = await adapter.delete(ResourceType.FILE, "missing.txt")
        assert response.success is False


# ==============================================================================
# Test Group 6: FileSystemAdapter - Search & List (4 tests)
# ==============================================================================

@pytest.mark.asyncio
class TestFileSystemAdapterQuery:
    """Test filesystem adapter search and list operations"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with multiple files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            (path / "file1.txt").write_text("test1")
            (path / "file2.md").write_text("# Test")
            (path / "data.json").write_text("{}")
            (path / "subdir").mkdir()
            (path / "subdir" / "file3.txt").write_text("test3")
            yield path
    
    @pytest.fixture
    def adapter(self, temp_dir):
        """Create filesystem adapter"""
        return FileSystemAdapter({"base_path": str(temp_dir)})
    
    async def test_search_files_by_pattern(self, adapter):
        """Test searching files by name pattern"""
        response = await adapter.search(ResourceType.FILE, "file")
        assert response.success is True
        assert len(response.data) >= 2  # file1.txt, file3.txt (recursive)
    
    async def test_search_with_custom_pattern(self, adapter):
        """Test searching with custom glob pattern"""
        response = await adapter.search(
            ResourceType.FILE,
            "txt",
            filters={"pattern": "*.txt"}
        )
        assert response.success is True
        file_names = [item["name"] for item in response.data]
        assert "file1.txt" in file_names
    
    async def test_list_directory_contents(self, adapter):
        """Test listing directory contents"""
        response = await adapter.list(ResourceType.FILE)
        assert response.success is True
        assert len(response.data) == 4  # 3 files + 1 subdir
    
    async def test_list_with_pagination(self, adapter):
        """Test listing with limit and offset"""
        response = await adapter.list(ResourceType.FILE, limit=2, offset=1)
        assert response.success is True
        assert len(response.data) == 2


# ==============================================================================
# Test Group 7: Adapter Configuration & Capabilities (3 tests)
# ==============================================================================

class TestAdapterCapabilities:
    """Test adapter capabilities and configuration"""
    
    def test_filesystem_capabilities(self):
        """Test filesystem adapter reports correct capabilities"""
        adapter = FileSystemAdapter()
        capabilities = adapter.get_capabilities()
        assert ResourceType.FILE in capabilities
        assert "create" in capabilities[ResourceType.FILE]
        assert "read" in capabilities[ResourceType.FILE]
    
    def test_filesystem_validate_config_success(self):
        """Test filesystem adapter config validation succeeds"""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = FileSystemAdapter({"base_path": tmpdir})
            assert adapter.validate_config() is True
    
    def test_filesystem_validate_config_failure(self):
        """Test filesystem adapter config validation fails for bad path"""
        adapter = FileSystemAdapter({"base_path": "/nonexistent/path"})
        with pytest.raises(AdapterError, match="does not exist"):
            adapter.validate_config()
