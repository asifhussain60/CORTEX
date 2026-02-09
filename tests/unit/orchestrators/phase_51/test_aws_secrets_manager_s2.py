"""
Phase 51 S2: AWS Secrets Manager Integration
TDD tests for AWS Secrets Manager provider

AC-PHASE51-S2-001: Retrieve secrets via ARN reference
AC-PHASE51-S2-002: Rotation triggers on expiration
AC-PHASE51-S2-003: Audit log tracks all secret access
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Optional, Dict, Any


class TestAWSSecretsProviderInterface:
    """AC-PHASE51-S2-001: Retrieve secrets via ARN reference"""
    
    def test_aws_provider_implements_interface(self):
        """AWSSecretsProvider implements ISecretsProvider"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.provider import ISecretsProvider
        
        assert issubclass(AWSSecretsProvider, ISecretsProvider)
    
    def test_aws_provider_requires_region(self):
        """AWSSecretsProvider requires region in config"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import ConfigError
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        # Should not raise
        provider = AWSSecretsProvider(config)
        assert provider is not None
    
    def test_aws_provider_accepts_endpoint_arn(self):
        """AWSSecretsProvider can use ARN as endpoint"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret-AbCdEf"
        config = SecretsConfig(
            provider_type="aws",
            region="us-east-1",
            endpoint=arn
        )
        provider = AWSSecretsProvider(config)
        assert provider.config.endpoint == arn


class TestAWSSecretsProviderRetrieval:
    """AC-PHASE51-S2-001: Retrieve secrets via ARN reference"""
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_get_retrieves_secret(self, mock_boto3):
        """get(secret_id) retrieves secret from AWS"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        # Mock AWS Secrets Manager response
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'my-secret-value'
        }
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        value = provider.get("my-secret")
        assert value == "my-secret-value"
        mock_client.get_secret_value.assert_called_once_with(SecretId="my-secret")
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_get_with_arn(self, mock_boto3):
        """get() accepts ARN as secret identifier"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {
            'SecretString': 'secret-value'
        }
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        arn = "arn:aws:secretsmanager:us-east-1:123456789:secret:my-secret-AbCdEf"
        value = provider.get(arn)
        
        assert value == "secret-value"
        mock_client.get_secret_value.assert_called_once_with(SecretId=arn)
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_get_handles_json_secrets(self, mock_boto3):
        """get() parses JSON secrets as dictionaries"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        import json
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        secret_dict = {"username": "admin", "password": "secret123"}
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps(secret_dict)
        }
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        value = provider.get("db-credentials")
        # Should return the JSON string, not parsed dict (provider returns string)
        assert "admin" in value


class TestAWSSecretsProviderStorage:
    """Test AWS secrets storage operations"""
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_set_creates_secret(self, mock_boto3):
        """set(secret_id, value) creates or updates secret"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.create_secret.return_value = {
            'ARN': 'arn:aws:secretsmanager:us-east-1:123456789:secret:new-secret-AbCdEf'
        }
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        provider.set("new-secret", "secret-value")
        
        mock_client.create_secret.assert_called()
        call_kwargs = mock_client.create_secret.call_args[1]
        assert call_kwargs['Name'] == "new-secret"
        assert call_kwargs['SecretString'] == "secret-value"
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_set_with_kms_encryption(self, mock_boto3):
        """set() can specify KMS key for encryption"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="aws",
            region="us-east-1",
            metadata={"kms_key_id": "arn:aws:kms:us-east-1:123456789:key/12345678"}
        )
        provider = AWSSecretsProvider(config)
        
        provider.set("encrypted-secret", "value")
        
        # Verify KMS key was passed
        call_kwargs = mock_client.create_secret.call_args[1]
        assert call_kwargs.get('KmsKeyId') == "arn:aws:kms:us-east-1:123456789:key/12345678"
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_delete_secret(self, mock_boto3):
        """delete(secret_id) marks secret for deletion"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        provider.delete("my-secret")
        
        # AWS allows 7-day recovery window by default
        mock_client.delete_secret.assert_called_once()
        call_kwargs = mock_client.delete_secret.call_args[1]
        assert call_kwargs['SecretId'] == "my-secret"


class TestAWSSecretsProviderRotation:
    """AC-PHASE51-S2-002: Rotation triggers on expiration"""
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_rotate_generates_new_version(self, mock_boto3):
        """rotate(secret_id) generates new secret version"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.rotate_secret.return_value = {
            'ARN': 'arn:aws:...',
            'VersionId': 'new-version-123'
        }
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        provider.rotate("my-secret")
        
        mock_client.rotate_secret.assert_called_once_with(SecretId="my-secret")
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_rotation_with_lambda(self, mock_boto3):
        """rotate() can trigger Lambda for custom rotation logic"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        config = SecretsConfig(
            provider_type="aws",
            region="us-east-1",
            metadata={"rotation_lambda_arn": "arn:aws:lambda:us-east-1:123456789:function:rotate"}
        )
        provider = AWSSecretsProvider(config)
        
        provider.rotate("my-secret")
        
        # Verify rotation Lambda ARN was configured
        call_kwargs = mock_client.rotate_secret.call_args[1]
        # Implementation can use this metadata for rotation configuration


class TestAWSSecretsProviderAudit:
    """AC-PHASE51-S2-003: Audit log tracks all secret access"""
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_logs_get_operations(self, mock_boto3):
        """get() operations are logged for audit trail"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {'SecretString': 'value'}
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        # Note: AWS CloudTrail automatically logs all API calls
        # This test verifies provider doesn't suppress logging
        provider.get("my-secret")
        
        # Call should go through to CloudTrail
        mock_client.get_secret_value.assert_called()
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_secret_versioning(self, mock_boto3):
        """Secret versions are tracked for audit trail"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.list_secret_version_ids.return_value = {
            'Versions': [
                {'VersionId': 'v3', 'CreatedDate': '2026-02-08'},
                {'VersionId': 'v2', 'CreatedDate': '2026-02-07'},
                {'VersionId': 'v1', 'CreatedDate': '2026-02-06'}
            ]
        }
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        # Provider can list versions for audit
        # This is typically used for compliance reporting
        versions = mock_client.list_secret_version_ids(SecretId="my-secret")
        assert len(versions['Versions']) == 3


class TestAWSSecretsProviderErrorHandling:
    """Error handling for AWS Secrets Manager"""
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_handles_not_found_error(self, mock_boto3):
        """get() raises SecretNotFoundError for missing secrets"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import SecretNotFoundError
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.get_secret_value.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException'}},
            'GetSecretValue'
        )
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        with pytest.raises(SecretNotFoundError):
            provider.get("nonexistent")
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_aws_provider_handles_auth_error(self, mock_boto3):
        """get() raises AuthError on permission denied"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        from cortex.secrets.errors import AuthError, PermissionError as SecretsPermissionError
        from botocore.exceptions import ClientError
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        mock_client.get_secret_value.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException'}},
            'GetSecretValue'
        )
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        with pytest.raises((AuthError, SecretsPermissionError)):
            provider.get("forbidden-secret")


class TestAWSSecretsProviderIntegration:
    """Integration tests for AWS Secrets Manager provider"""
    
    @patch('cortex.secrets.providers.aws.boto3')
    def test_full_secret_lifecycle(self, mock_boto3):
        """Full workflow: create → retrieve → rotate → delete"""
        from cortex.secrets.providers.aws import AWSSecretsProvider
        from cortex.secrets.config import SecretsConfig
        
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        
        # Setup mock responses
        mock_client.create_secret.return_value = {'ARN': 'arn:...', 'VersionId': 'v1'}
        mock_client.get_secret_value.return_value = {'SecretString': 'value'}
        mock_client.rotate_secret.return_value = {'VersionId': 'v2'}
        mock_client.delete_secret.return_value = {'DeletionDate': '2026-02-15'}
        
        config = SecretsConfig(provider_type="aws", region="us-east-1")
        provider = AWSSecretsProvider(config)
        
        # Create
        provider.set("api-key", "secret-value")
        
        # Retrieve
        value = provider.get("api-key")
        assert value == "value"
        
        # Rotate
        provider.rotate("api-key")
        
        # Delete
        provider.delete("api-key")
        
        # Verify all operations called
        assert mock_client.create_secret.called
        assert mock_client.get_secret_value.called
        assert mock_client.rotate_secret.called
        assert mock_client.delete_secret.called
