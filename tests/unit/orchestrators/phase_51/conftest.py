"""
Phase 51 pre-flight pytest configuration
Mocks optional cloud SDK dependencies (boto3, azure, hvac)
"""

import sys
from unittest.mock import MagicMock


def pytest_configure(config):
    """
    Pre-flight configuration to mock cloud SDKs before test collection.
    
    AWS Secrets Manager (boto3):
    - boto3.client('secretsmanager')
    - botocore.exceptions.ClientError
    
    Azure Key Vault:
    - azure.keyvault.secrets.SecretClient
    - azure.core.exceptions
    
    HashiCorp Vault (hvac):
    - hvac.Client
    """
    
    # ===========================================================================
    # AWS Mocking (boto3 + botocore)
    # ===========================================================================
    
    if 'boto3' not in sys.modules:
        sys.modules['boto3'] = MagicMock()
    
    if 'botocore' not in sys.modules:
        sys.modules['botocore'] = MagicMock()
    
    if 'botocore.exceptions' not in sys.modules:
        botocore_exceptions = MagicMock()
        
        # Create ClientError exception class
        class ClientError(Exception):
            def __init__(self, error_response, operation_name):
                self.response = error_response
                self.operation_name = operation_name
        
        botocore_exceptions.ClientError = ClientError
        sys.modules['botocore.exceptions'] = botocore_exceptions
    
    # ===========================================================================
    # Azure Mocking
    # ===========================================================================
    
    if 'azure' not in sys.modules:
        sys.modules['azure'] = MagicMock()
    
    if 'azure.core' not in sys.modules:
        sys.modules['azure.core'] = MagicMock()
    
    if 'azure.identity' not in sys.modules:
        sys.modules['azure.identity'] = MagicMock()
    
    if 'azure.core.exceptions' not in sys.modules:
        azure_exceptions = MagicMock()
        
        # Create exception classes
        class ClientAuthenticationError(Exception):
            pass
        
        class ResourceNotFoundError(Exception):
            pass
        
        azure_exceptions.ClientAuthenticationError = ClientAuthenticationError
        azure_exceptions.ResourceNotFoundError = ResourceNotFoundError
        sys.modules['azure.core.exceptions'] = azure_exceptions
    
    if 'azure.keyvault.secrets' not in sys.modules:
        sys.modules['azure.keyvault.secrets'] = MagicMock()
    
    # ===========================================================================
    # HashiCorp Vault Mocking (hvac)
    # ===========================================================================
    
    if 'hvac' not in sys.modules:
        sys.modules['hvac'] = MagicMock()
