"""
Stage 3: S3StorageProvider Implementation Tests

AC-PHASE50-S3-001: S3StorageProvider uses boto3 for AWS S3 interaction
AC-PHASE50-S3-002: Supports all IKnowledgeProvider methods with S3 operations
AC-PHASE50-S3-003: Maps S3 errors to StorageError hierarchy
AC-PHASE50-S3-004: Handles authentication via config credentials or environment
AC-PHASE50-S3-005: Supports optional bucket path prefix (endpoint parsing)

Target: 18 tests, 100% pass rate for Stage 3
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import NoCredentialsError, ClientError

from cortex.storage.provider import IKnowledgeProvider
from cortex.storage.config import StorageConfig
from cortex.storage.errors import (
    StorageError,
    PermissionError,
    NotFoundError,
    NetworkError,
    ConfigurationError,
)
from cortex.storage.providers.s3 import S3StorageProvider


class TestS3StorageProviderInitialization:
    """AC-PHASE50-S3-001: S3 provider initialization and configuration"""

    def test_s3_provider_implements_interface(self):
        """S3StorageProvider is instance of IKnowledgeProvider"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket/prefix",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3'):
            provider = S3StorageProvider(config)
            assert isinstance(provider, IKnowledgeProvider)

    def test_s3_provider_parses_bucket_and_prefix(self):
        """S3StorageProvider parses s3://bucket/prefix from endpoint"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket/knowledge/prefix",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3'):
            provider = S3StorageProvider(config)
            assert provider.bucket_name == "my-bucket"
            assert provider.prefix == "knowledge/prefix"

    def test_s3_provider_handles_bucket_only_endpoint(self):
        """S3StorageProvider handles endpoint with bucket name only"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3'):
            provider = S3StorageProvider(config)
            assert provider.bucket_name == "my-bucket"
            assert provider.prefix == ""

    def test_s3_provider_requires_endpoint(self):
        """S3StorageProvider requires endpoint (S3 bucket URI)"""
        config = StorageConfig(
            backend="s3",
            endpoint=None,
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with pytest.raises((ConfigurationError, ValueError)):
            S3StorageProvider(config)

    def test_s3_provider_initializes_boto3_client(self):
        """S3StorageProvider initializes boto3 S3 client"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            provider = S3StorageProvider(config)
            assert provider.s3_client == mock_client


class TestS3StorageProviderReadMethod:
    """AC-PHASE50-S3-002: read() method for S3 objects"""

    def test_read_existing_object(self):
        """read() retrieves content from S3 object"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_response = {"Body": Mock(read=Mock(return_value=b"S3 content"))}
            mock_client.get_object.return_value = mock_response
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            result = provider.read("file.txt")
            
            assert result == "S3 content"
            mock_client.get_object.assert_called_once()

    def test_read_nonexistent_object_raises_not_found(self):
        """read() raises NotFoundError for missing S3 object"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            error_response = {"Error": {"Code": "NoSuchKey"}}
            mock_client.get_object.side_effect = ClientError(error_response, "GetObject")
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            with pytest.raises(NotFoundError):
                provider.read("nonexistent.txt")

    def test_read_handles_network_errors(self):
        """read() raises NetworkError on connection failure"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_client.get_object.side_effect = Exception("Connection timeout")
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            with pytest.raises(NetworkError):
                provider.read("file.txt")

    def test_read_with_prefix(self):
        """read() constructs S3 key from prefix and path"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket/knowledge",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_response = {"Body": Mock(read=Mock(return_value=b"content"))}
            mock_client.get_object.return_value = mock_response
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            provider.read("domains/ai.yaml")
            
            # Verify correct key was used
            call_args = mock_client.get_object.call_args
            assert "knowledge/domains/ai.yaml" in str(call_args)


class TestS3StorageProviderWriteMethod:
    """AC-PHASE50-S3-002: write() method for S3 objects"""

    def test_write_creates_object(self):
        """write() uploads content to S3"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            provider.write("file.txt", "new content")
            
            mock_client.put_object.assert_called_once()

    def test_write_handles_permission_errors(self):
        """write() raises PermissionError on access denied"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            error_response = {"Error": {"Code": "AccessDenied"}}
            mock_client.put_object.side_effect = ClientError(error_response, "PutObject")
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            with pytest.raises(PermissionError):
                provider.write("file.txt", "content")


class TestS3StorageProviderListMethod:
    """AC-PHASE50-S3-002: list() method for S3 objects"""

    def test_list_bucket_contents(self):
        """list() returns objects in S3 prefix"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket/knowledge",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_response = {
                "Contents": [
                    {"Key": "knowledge/file1.txt"},
                    {"Key": "knowledge/file2.txt"}
                ]
            }
            mock_client.list_objects_v2.return_value = mock_response
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            result = provider.list("")
            
            assert "file1.txt" in result
            assert "file2.txt" in result

    def test_list_empty_prefix(self):
        """list() returns empty list when prefix has no objects"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_client.list_objects_v2.return_value = {}
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            result = provider.list("empty")
            
            assert result == []


class TestS3StorageProviderExistsMethod:
    """AC-PHASE50-S3-002: exists() method for S3 objects"""

    def test_exists_returns_true_for_existing_object(self):
        """exists() returns True for existing S3 object"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_client.head_object.return_value = {}
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            result = provider.exists("file.txt")
            
            assert result is True

    def test_exists_returns_false_for_missing_object(self):
        """exists() returns False for missing S3 object"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            error_response = {"Error": {"Code": "NotFound"}}
            mock_client.head_object.side_effect = ClientError(error_response, "HeadObject")
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            result = provider.exists("missing.txt")
            
            assert result is False


class TestS3StorageProviderDeleteMethod:
    """AC-PHASE50-S3-002: delete() method for S3 objects"""

    def test_delete_removes_object(self):
        """delete() removes S3 object"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            provider.delete("file.txt")
            
            mock_client.delete_object.assert_called_once()

    def test_delete_nonexistent_object_raises_not_found(self):
        """delete() raises NotFoundError for missing object"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"}
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_client = Mock()
            error_response = {"Error": {"Code": "NoSuchKey"}}
            mock_client.head_object.side_effect = ClientError(error_response, "HeadObject")
            mock_client.delete_object.side_effect = ClientError(error_response, "DeleteObject")
            mock_boto3.client.return_value = mock_client
            
            provider = S3StorageProvider(config)
            with pytest.raises(NotFoundError):
                provider.delete("nonexistent.txt")


class TestS3StorageProviderAuthentication:
    """AC-PHASE50-S3-004: S3 authentication handling"""

    def test_s3_uses_config_credentials(self):
        """S3StorageProvider uses credentials from config"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials={
                "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
                "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            }
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            S3StorageProvider(config)
            mock_boto3.client.assert_called_once()

    def test_s3_uses_environment_credentials_when_none_provided(self):
        """S3StorageProvider uses environment credentials if config has none"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials=None
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            S3StorageProvider(config)
            mock_boto3.client.assert_called_once()

    def test_s3_handles_no_credentials_error(self):
        """S3StorageProvider raises PermissionError on missing credentials"""
        config = StorageConfig(
            backend="s3",
            endpoint="s3://my-bucket",
            credentials=None
        )
        with patch('cortex.storage.providers.s3.boto3') as mock_boto3:
            mock_boto3.client.side_effect = NoCredentialsError()
            with pytest.raises((PermissionError, ConfigurationError)):
                S3StorageProvider(config)
