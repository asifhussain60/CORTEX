"""
Stage 4: AzureBlobProvider Implementation Tests

AC-PHASE50-S4-001: AzureBlobProvider uses azure-storage-blob SDK
AC-PHASE50-S4-002: Supports all IKnowledgeProvider methods with Azure Blob operations
AC-PHASE50-S4-003: Maps Azure errors to StorageError hierarchy
AC-PHASE50-S4-004: Handles authentication via config credentials or DefaultAzureCredential
AC-PHASE50-S4-005: Supports optional container path prefix

Target: 15 tests, 100% pass rate for Stage 4
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

from cortex.storage.provider import IKnowledgeProvider
from cortex.storage.config import StorageConfig
from cortex.storage.errors import (
    StorageError,
    PermissionError,
    NotFoundError,
    NetworkError,
    ConfigurationError,
)
from cortex.storage.providers.azure import AzureBlobProvider


class TestAzureBlobProviderInitialization:
    """AC-PHASE50-S4-001: Azure provider initialization and configuration"""

    def test_azure_provider_implements_interface(self):
        """AzureBlobProvider is instance of IKnowledgeProvider"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient'):
            provider = AzureBlobProvider(config)
            assert isinstance(provider, IKnowledgeProvider)

    def test_azure_provider_parses_account_and_container(self):
        """AzureBlobProvider parses account and container from endpoint"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient'):
            provider = AzureBlobProvider(config)
            assert provider.account_name == "mystorageacct"
            assert provider.container_name == "knowledge"

    def test_azure_provider_requires_endpoint(self):
        """AzureBlobProvider requires endpoint (Azure storage URI)"""
        config = StorageConfig(
            backend="azure",
            endpoint=None,
            credentials={"account_key": "key"}
        )
        with pytest.raises((ConfigurationError, ValueError)):
            AzureBlobProvider(config)

    def test_azure_provider_initializes_blob_client(self):
        """AzureBlobProvider initializes Azure BlobServiceClient"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.from_connection_string.return_value = mock_client
            provider = AzureBlobProvider(config)
            assert provider.blob_client is not None


class TestAzureBlobProviderReadMethod:
    """AC-PHASE50-S4-002: read() method for Azure blobs"""

    def test_read_existing_blob(self):
        """read() retrieves content from Azure blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_data = Mock()
            mock_blob_data.readall.return_value = b"Azure content"
            mock_blob_client.download_blob.return_value = mock_blob_data
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            result = provider.read("file.txt")
            
            assert result == "Azure content"

    def test_read_nonexistent_blob_raises_not_found(self):
        """read() raises NotFoundError for missing Azure blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_client.download_blob.side_effect = ResourceNotFoundError("Blob not found")
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            with pytest.raises(NotFoundError):
                provider.read("nonexistent.txt")

    def test_read_handles_network_errors(self):
        """read() raises NetworkError on connection failure"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_client.download_blob.side_effect = Exception("Connection timeout")
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            with pytest.raises(NetworkError):
                provider.read("file.txt")


class TestAzureBlobProviderWriteMethod:
    """AC-PHASE50-S4-002: write() method for Azure blobs"""

    def test_write_creates_blob(self):
        """write() uploads content to Azure blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            provider.write("file.txt", "new content")
            
            mock_blob_client.upload_blob.assert_called_once()

    def test_write_handles_permission_errors(self):
        """write() raises PermissionError on access denied"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_client.upload_blob.side_effect = ClientAuthenticationError("Access denied")
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            with pytest.raises(PermissionError):
                provider.write("file.txt", "content")


class TestAzureBlobProviderListMethod:
    """AC-PHASE50-S4-002: list() method for Azure blobs"""

    def test_list_container_blobs(self):
        """list() returns blobs in container"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob1 = Mock(name="file1.txt")
            mock_blob2 = Mock(name="file2.txt")
            
            mock_container = Mock()
            mock_container.list_blobs.return_value = [mock_blob1, mock_blob2]
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            result = provider.list("")
            
            assert "file1.txt" in result
            assert "file2.txt" in result

    def test_list_empty_container(self):
        """list() returns empty list when container has no blobs"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_container = Mock()
            mock_container.list_blobs.return_value = []
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            result = provider.list("")
            
            assert result == []


class TestAzureBlobProviderExistsMethod:
    """AC-PHASE50-S4-002: exists() method for Azure blobs"""

    def test_exists_returns_true_for_existing_blob(self):
        """exists() returns True for existing Azure blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_props = Mock()
            mock_blob_client.get_blob_properties.return_value = mock_blob_props
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            result = provider.exists("file.txt")
            
            assert result is True

    def test_exists_returns_false_for_missing_blob(self):
        """exists() returns False for missing Azure blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_client.get_blob_properties.side_effect = ResourceNotFoundError("Not found")
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            result = provider.exists("missing.txt")
            
            assert result is False


class TestAzureBlobProviderDeleteMethod:
    """AC-PHASE50-S4-002: delete() method for Azure blobs"""

    def test_delete_removes_blob(self):
        """delete() removes Azure blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            provider.delete("file.txt")
            
            mock_blob_client.delete_blob.assert_called_once()

    def test_delete_nonexistent_blob_raises_not_found(self):
        """delete() raises NotFoundError for missing blob"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "key"}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client = Mock()
            mock_blob_client = Mock()
            mock_blob_client.get_blob_properties.side_effect = ResourceNotFoundError("Not found")
            
            mock_container = Mock()
            mock_container.get_blob_client.return_value = mock_blob_client
            mock_client.get_container_client.return_value = mock_container
            mock_client_class.from_connection_string.return_value = mock_client
            
            provider = AzureBlobProvider(config)
            with pytest.raises(NotFoundError):
                provider.delete("nonexistent.txt")


class TestAzureBlobProviderAuthentication:
    """AC-PHASE50-S4-004: Azure authentication handling"""

    def test_azure_uses_account_key(self):
        """AzureBlobProvider uses account key from credentials"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials={"account_key": "SharedKeyLike..."}
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            AzureBlobProvider(config)
            mock_client_class.from_connection_string.assert_called_once()

    def test_azure_uses_default_credentials_when_none_provided(self):
        """AzureBlobProvider uses DefaultAzureCredential when no creds in config"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials=None
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            AzureBlobProvider(config)
            mock_client_class.assert_called_once()

    def test_azure_handles_authentication_error(self):
        """AzureBlobProvider raises PermissionError on auth failure"""
        config = StorageConfig(
            backend="azure",
            endpoint="https://mystorageacct.blob.core.windows.net/knowledge",
            credentials=None
        )
        with patch('cortex.storage.providers.azure.BlobServiceClient') as mock_client_class:
            mock_client_class.side_effect = ClientAuthenticationError("Invalid credentials")
            with pytest.raises((PermissionError, ConfigurationError)):
                AzureBlobProvider(config)
