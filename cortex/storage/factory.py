"""
Storage provider factory.
Authority: Phase 50 Stage 1 - Storage Backend Abstraction
AC-PHASE50-S1-002: Factory returns correct provider based on config
"""

from typing import TYPE_CHECKING
from cortex.storage.config import StorageConfig
from cortex.storage.errors import ConfigurationError

if TYPE_CHECKING:
    from cortex.storage.provider import IKnowledgeProvider


class StorageProviderFactory:
    """
    Factory for creating knowledge storage provider instances.
    
    Supports:
    - local: LocalFileSystemProvider
    - s3: S3StorageProvider
    - azure: AzureBlobProvider
    """
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, backend: str, provider_class):
        """Register a provider class for a backend type."""
        cls._providers[backend] = provider_class
    
    @classmethod
    def get_provider(cls, config: StorageConfig) -> "IKnowledgeProvider":
        """
        Create a provider instance for the given configuration.
        
        Args:
            config: StorageConfig instance
            
        Returns:
            IKnowledgeProvider instance
            
        Raises:
            ConfigurationError: If backend not registered or config invalid
        """
        if config.backend not in cls._providers:
            raise ConfigurationError(
                f"Unknown backend: {config.backend}. "
                f"Available: {list(cls._providers.keys())}"
            )
        
        provider_class = cls._providers[config.backend]
        return provider_class(config)


# Register default providers (lazy import to avoid circular dependencies)
def _register_default_providers():
    """Register built-in providers."""
    try:
        from cortex.storage.providers.local import LocalFileSystemProvider
        StorageProviderFactory.register_provider("local", LocalFileSystemProvider)
    except ImportError:
        pass
    
    try:
        from cortex.storage.providers.s3 import S3StorageProvider
        StorageProviderFactory.register_provider("s3", S3StorageProvider)
    except ImportError:
        pass
    
    try:
        from cortex.storage.providers.azure import AzureBlobProvider
        StorageProviderFactory.register_provider("azure", AzureBlobProvider)
    except ImportError:
        pass


_register_default_providers()
