"""
Phase 50 Stage 1: Storage Provider Interface - TDD Tests
AC-PHASE50-S1-001: IKnowledgeProvider defines all storage operations
AC-PHASE50-S1-002: Factory returns correct provider based on config
AC-PHASE50-S1-003: Error handling covers all failure modes
"""

import pytest
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


# S1 Test Suite - Storage Provider Interface Design (12 tests)

class TestIKnowledgeProviderProtocol:
    """AC-PHASE50-S1-001: IKnowledgeProvider defines all storage operations"""
    
    def test_knowledge_provider_has_read_method(self):
        """IKnowledgeProvider.read(path: str) -> str"""
        from cortex.storage.provider import IKnowledgeProvider
        assert hasattr(IKnowledgeProvider, 'read')
    
    def test_knowledge_provider_has_write_method(self):
        """IKnowledgeProvider.write(path: str, content: str) -> None"""
        from cortex.storage.provider import IKnowledgeProvider
        assert hasattr(IKnowledgeProvider, 'write')
    
    def test_knowledge_provider_has_list_method(self):
        """IKnowledgeProvider.list(path: str) -> List[str]"""
        from cortex.storage.provider import IKnowledgeProvider
        assert hasattr(IKnowledgeProvider, 'list')
    
    def test_knowledge_provider_has_exists_method(self):
        """IKnowledgeProvider.exists(path: str) -> bool"""
        from cortex.storage.provider import IKnowledgeProvider
        assert hasattr(IKnowledgeProvider, 'exists')
    
    def test_knowledge_provider_has_delete_method(self):
        """IKnowledgeProvider.delete(path: str) -> None"""
        from cortex.storage.provider import IKnowledgeProvider
        assert hasattr(IKnowledgeProvider, 'delete')


class TestStorageConfigDataclass:
    """Storage configuration dataclass with all required fields"""
    
    def test_storage_config_has_backend_field(self):
        """StorageConfig.backend: str"""
        from cortex.storage.config import StorageConfig
        config = StorageConfig(backend="local", endpoint=None, credentials=None)
        assert config.backend == "local"
    
    def test_storage_config_has_endpoint_field(self):
        """StorageConfig.endpoint: Optional[str]"""
        from cortex.storage.config import StorageConfig
        config = StorageConfig(backend="s3", endpoint="https://s3.amazonaws.com", credentials=None)
        assert config.endpoint == "https://s3.amazonaws.com"
    
    def test_storage_config_has_credentials_field(self):
        """StorageConfig.credentials: Optional[Dict[str, Any]]"""
        from cortex.storage.config import StorageConfig
        creds = {"access_key": "test"}
        config = StorageConfig(backend="s3", endpoint=None, credentials=creds)
        assert config.credentials == creds
    
    def test_storage_config_has_cache_ttl_field(self):
        """StorageConfig.cache_ttl_seconds: int"""
        from cortex.storage.config import StorageConfig
        config = StorageConfig(backend="local", endpoint=None, credentials=None, cache_ttl_seconds=3600)
        assert config.cache_ttl_seconds == 3600


class TestStorageProviderFactory:
    """AC-PHASE50-S1-002: Factory returns correct provider based on config"""
    
    def test_factory_returns_local_provider_for_local_backend(self):
        """get_provider(backend='local') returns LocalFileSystemProvider"""
        from cortex.storage.factory import StorageProviderFactory
        from cortex.storage.config import StorageConfig
        from cortex.storage.providers.local import LocalFileSystemProvider
        
        config = StorageConfig(backend="local", endpoint=None, credentials=None)
        provider = StorageProviderFactory.get_provider(config)
        assert isinstance(provider, LocalFileSystemProvider)
    
    def test_factory_returns_s3_provider_for_s3_backend(self):
        """get_provider(backend='s3') returns S3StorageProvider"""
        from cortex.storage.factory import StorageProviderFactory
        from cortex.storage.config import StorageConfig
        from cortex.storage.providers.s3 import S3StorageProvider
        
        config = StorageConfig(backend="s3", endpoint="https://s3.amazonaws.com", credentials={"bucket": "cortex-knowledge"})
        provider = StorageProviderFactory.get_provider(config)
        assert isinstance(provider, S3StorageProvider)
    
    def test_factory_returns_azure_provider_for_azure_backend(self):
        """get_provider(backend='azure') returns AzureBlobProvider"""
        from cortex.storage.factory import StorageProviderFactory
        from cortex.storage.config import StorageConfig
        from cortex.storage.providers.azure import AzureBlobProvider
        
        config = StorageConfig(backend="azure", endpoint="https://account.blob.core.windows.net", credentials={"container": "cortex-knowledge"})
        provider = StorageProviderFactory.get_provider(config)
        assert isinstance(provider, AzureBlobProvider)


class TestStorageErrorHandling:
    """AC-PHASE50-S1-003: Error handling covers all failure modes"""
    
    def test_storage_error_exception_exists(self):
        """StorageError base exception for all storage failures"""
        from cortex.storage.errors import StorageError
        assert issubclass(StorageError, Exception)
    
    def test_network_error_exception_exists(self):
        """NetworkError for remote storage failures"""
        from cortex.storage.errors import NetworkError, StorageError
        assert issubclass(NetworkError, StorageError)
    
    def test_permission_error_exception_exists(self):
        """PermissionError for access control failures"""
        from cortex.storage.errors import PermissionError as StoragePermissionError, StorageError
        assert issubclass(StoragePermissionError, StorageError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
