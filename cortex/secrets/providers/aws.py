"""AWS Secrets Manager provider"""

import boto3
import json
from typing import Optional, Dict, Any, List
from cortex.secrets.provider import ISecretsProvider
from cortex.secrets.config import SecretsConfig
from cortex.secrets.errors import (
    SecretNotFoundError,
    AuthError,
    PermissionError as SecretsPermissionError,
    StorageError,
)


class AWSSecretsProvider(ISecretsProvider):
    """AWS Secrets Manager provider for enterprise secrets management"""
    
    def __init__(self, config: SecretsConfig):
        """
        Initialize AWS Secrets Manager provider.
        
        Args:
            config: SecretsConfig with provider_type='aws', region, optional kms_key_id
        """
        if config.provider_type != "aws":
            raise ValueError(f"AWSSecretsProvider requires provider_type='aws', got {config.provider_type}")
        
        self.config = config
        self.region = config.region or "us-east-1"
        
        # Create boto3 client
        self.client = boto3.client('secretsmanager', region_name=self.region)
    
    def get(self, secret_id: str) -> Optional[str]:
        """
        Retrieve secret from AWS Secrets Manager.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value as string
            
        Raises:
            SecretNotFoundError: If secret doesn't exist
            PermissionError: If lacking access
            StorageError: If backend fails
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            return response.get('SecretString') or response.get('SecretBinary')
        
        except Exception as e:
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
            
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundError(f"Secret not found: {secret_id}")
            elif error_code in ('AccessDeniedException', 'UnrecognizedClientException'):
                raise SecretsPermissionError(f"Permission denied for secret: {secret_id}")
            else:
                raise StorageError(f"Failed to retrieve secret: {str(e)}")
    
    def set(self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Create or update secret in AWS Secrets Manager.
        
        Args:
            secret_id: Secret name
            value: Secret value
            metadata: Optional metadata (kms_key_id, tags, description)
            
        Raises:
            PermissionError: If lacking write access
            StorageError: If backend fails
        """
        try:
            kwargs = {
                'Name': secret_id,
                'SecretString': value,
            }
            
            # Use KMS key if specified
            if metadata and 'kms_key_id' in metadata:
                kwargs['KmsKeyId'] = metadata['kms_key_id']
            elif self.config.metadata and 'kms_key_id' in self.config.metadata:
                kwargs['KmsKeyId'] = self.config.metadata['kms_key_id']
            
            # Add tags if provided
            if metadata and 'tags' in metadata:
                kwargs['Tags'] = [
                    {'Key': k, 'Value': v}
                    for k, v in metadata['tags'].items()
                ]
            
            self.client.create_secret(**kwargs)
        
        except Exception as e:
            raise StorageError(f"Failed to create secret: {str(e)}")
    
    def delete(self, secret_id: str) -> None:
        """
        Delete secret from AWS Secrets Manager.
        
        Secrets are soft-deleted with a 7-day recovery window by default.
        
        Args:
            secret_id: Secret name or ARN
            
        Raises:
            SecretNotFoundError: If secret doesn't exist
            PermissionError: If lacking delete access
            StorageError: If backend fails
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=7  # Allow 7-day recovery
            )
        
        except Exception as e:
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
            
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundError(f"Secret not found: {secret_id}")
            elif error_code in ('AccessDeniedException', 'UnrecognizedClientException'):
                raise SecretsPermissionError(f"Permission denied for secret: {secret_id}")
            else:
                raise StorageError(f"Failed to delete secret: {str(e)}")
    
    def rotate(self, secret_id: str) -> str:
        """
        Trigger rotation of secret in AWS Secrets Manager.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            New version ID
            
        Raises:
            SecretNotFoundError: If secret doesn't exist
            PermissionError: If lacking rotate access
            StorageError: If backend fails
        """
        try:
            response = self.client.rotate_secret(SecretId=secret_id)
            return response.get('VersionId', '')
        
        except Exception as e:
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '')
            
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundError(f"Secret not found: {secret_id}")
            elif error_code in ('AccessDeniedException', 'UnrecognizedClientException'):
                raise SecretsPermissionError(f"Permission denied for secret: {secret_id}")
            else:
                raise StorageError(f"Failed to rotate secret: {str(e)}")
    
    def list(self, prefix: str = "") -> List[str]:
        """
        List secrets from AWS Secrets Manager.
        
        Args:
            prefix: Optional prefix filter (applied client-side)
            
        Returns:
            List of secret names/ARNs
            
        Raises:
            PermissionError: If lacking list access
            StorageError: If backend fails
        """
        try:
            secrets = []
            paginator = self.client.get_paginator('list_secrets')
            
            for page in paginator.paginate():
                for secret in page.get('SecretList', []):
                    secrets.append(secret['Name'])
            
            # Filter by prefix if provided
            if prefix:
                secrets = [s for s in secrets if s.startswith(prefix)]
            
            return sorted(secrets)
        
        except Exception as e:
            raise StorageError(f"Failed to list secrets: {str(e)}")
