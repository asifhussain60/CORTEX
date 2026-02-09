"""
Pytest configuration for Phase 50 storage backend tests.

Handles module-level mocking for optional cloud SDK dependencies (boto3, azure-storage-blob)
to allow tests to run without requiring these packages to be installed.

This enables:
- Individual developers to test LocalFileSystemProvider without cloud SDKs
- CI/CD pipelines to validate all providers with mocked dependencies
- Optional dependency pattern: graceful degradation if boto3/azure not installed
"""

import sys
from unittest.mock import MagicMock, Mock

# Pre-flight: Mock boto3 and botocore before any test imports them
def pytest_configure(config):
    """Configure pytest and mock cloud SDKs at session start."""
    
    # Mock boto3 ecosystem
    mock_boto3 = MagicMock()
    mock_botocore = MagicMock()
    mock_botocore_exceptions = MagicMock()
    
    # Configure botocore.exceptions with necessary error classes
    mock_botocore_exceptions.NoCredentialsError = type('NoCredentialsError', (Exception,), {})
    mock_botocore_exceptions.ClientError = type('ClientError', (Exception,), {})
    
    sys.modules['boto3'] = mock_boto3
    sys.modules['botocore'] = mock_botocore
    sys.modules['botocore.exceptions'] = mock_botocore_exceptions
    
    # Mock azure ecosystem
    mock_azure = MagicMock()
    mock_azure_core = MagicMock()
    mock_azure_core_exceptions = MagicMock()
    mock_azure_storage = MagicMock()
    mock_azure_storage_blob = MagicMock()
    mock_azure_identity = MagicMock()
    
    # Configure azure.core.exceptions with necessary error classes
    mock_azure_core_exceptions.ResourceNotFoundError = type('ResourceNotFoundError', (Exception,), {})
    mock_azure_core_exceptions.ClientAuthenticationError = type('ClientAuthenticationError', (Exception,), {})
    
    sys.modules['azure'] = mock_azure
    sys.modules['azure.core'] = mock_azure_core
    sys.modules['azure.core.exceptions'] = mock_azure_core_exceptions
    sys.modules['azure.storage'] = mock_azure_storage
    sys.modules['azure.storage.blob'] = mock_azure_storage_blob
    sys.modules['azure.identity'] = mock_azure_identity
