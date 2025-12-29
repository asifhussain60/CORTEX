"""
Universal Adapter Base Class

Abstract interface for all external system integrations in CORTEX 4.0.
Provides consistent CRUD operations, error handling, and resource management.

Author: CORTEX 4.0
Phase: 7B - Operations Simplification (Task 7.6)
Created: December 23, 2025
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ResourceType(Enum):
    """Types of resources managed by adapters"""
    WORK_ITEM = "work_item"
    PIPELINE = "pipeline"
    REPOSITORY = "repository"
    FILE = "file"
    ISSUE = "issue"
    PULL_REQUEST = "pull_request"
    PROJECT = "project"
    USER = "user"
    COMMENT = "comment"


@dataclass
class AdapterResponse(Generic[T]):
    """Standard response format for adapter operations"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate response consistency"""
        if self.success and self.data is None:
            raise ValueError("Success response must include data")
        if not self.success and self.error is None:
            raise ValueError("Failure response must include error message")


class AdapterError(Exception):
    """Base exception for adapter operations"""
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class UniversalAdapter(ABC):
    """
    Universal adapter interface for all external systems.
    
    Provides CRUD + Search operations with consistent error handling,
    caching, retry logic, and rate limiting.
    
    Implementations:
    - AzureDevOpsAdapter: Work items, pipelines, repos
    - GitHubAdapter: Issues, PRs, repos
    - FileSystemAdapter: Local files (YAML, JSON, Markdown)
    
    Design Principles:
    - Async API for non-blocking I/O
    - Standard response format (AdapterResponse)
    - Consistent error handling (AdapterError)
    - Platform-agnostic resource types
    - Middleware support (caching, retry, logging)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize adapter with configuration.
        
        Args:
            config: Platform-specific configuration (credentials, URLs, etc.)
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def create(
        self,
        resource_type: ResourceType,
        data: Dict[str, Any],
        **kwargs
    ) -> AdapterResponse[Dict[str, Any]]:
        """
        Create a new resource.
        
        Args:
            resource_type: Type of resource to create
            data: Resource data (platform-specific fields)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            AdapterResponse with created resource data
            
        Raises:
            AdapterError: If creation fails
        """
        pass
    
    @abstractmethod
    async def read(
        self,
        resource_type: ResourceType,
        resource_id: str,
        **kwargs
    ) -> AdapterResponse[Dict[str, Any]]:
        """
        Read an existing resource.
        
        Args:
            resource_type: Type of resource to read
            resource_id: Unique identifier for the resource
            **kwargs: Additional platform-specific parameters
            
        Returns:
            AdapterResponse with resource data
            
        Raises:
            AdapterError: If resource not found or read fails
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        resource_type: ResourceType,
        resource_id: str,
        data: Dict[str, Any],
        **kwargs
    ) -> AdapterResponse[Dict[str, Any]]:
        """
        Update an existing resource.
        
        Args:
            resource_type: Type of resource to update
            resource_id: Unique identifier for the resource
            data: Updated resource data (partial or full)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            AdapterResponse with updated resource data
            
        Raises:
            AdapterError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        resource_type: ResourceType,
        resource_id: str,
        **kwargs
    ) -> AdapterResponse[bool]:
        """
        Delete a resource.
        
        Args:
            resource_type: Type of resource to delete
            resource_id: Unique identifier for the resource
            **kwargs: Additional platform-specific parameters
            
        Returns:
            AdapterResponse with deletion status
            
        Raises:
            AdapterError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        resource_type: ResourceType,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        **kwargs
    ) -> AdapterResponse[List[Dict[str, Any]]]:
        """
        Search for resources matching criteria.
        
        Args:
            resource_type: Type of resource to search
            query: Search query (platform-specific syntax)
            filters: Additional filters (key-value pairs)
            limit: Maximum number of results
            **kwargs: Additional platform-specific parameters
            
        Returns:
            AdapterResponse with list of matching resources
            
        Raises:
            AdapterError: If search fails
        """
        pass
    
    @abstractmethod
    async def list(
        self,
        resource_type: ResourceType,
        parent_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs
    ) -> AdapterResponse[List[Dict[str, Any]]]:
        """
        List resources (optionally under a parent).
        
        Args:
            resource_type: Type of resource to list
            parent_id: Parent resource ID (e.g., project ID for work items)
            limit: Maximum number of results
            offset: Pagination offset
            **kwargs: Additional platform-specific parameters
            
        Returns:
            AdapterResponse with list of resources
            
        Raises:
            AdapterError: If listing fails
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[ResourceType, List[str]]:
        """
        Get adapter capabilities (supported operations per resource type).
        
        Returns:
            Mapping of resource types to supported operations
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate adapter configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            AdapterError: If configuration is invalid
        """
        pass


class AdapterFactory:
    """
    Factory for creating appropriate adapter based on context.
    
    Supports:
    - Explicit adapter type selection
    - Auto-detection from environment
    - Configuration-based instantiation
    """
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, adapter_type: str, adapter_class: type):
        """Register an adapter implementation"""
        cls._registry[adapter_type] = adapter_class
        logger.info(f"Registered adapter: {adapter_type} -> {adapter_class.__name__}")
    
    @classmethod
    def create(
        cls,
        adapter_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> UniversalAdapter:
        """
        Create adapter instance by type.
        
        Args:
            adapter_type: Adapter identifier (azure_devops, github, filesystem)
            config: Platform-specific configuration
            
        Returns:
            Configured adapter instance
            
        Raises:
            ValueError: If adapter type unknown
        """
        if adapter_type not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown adapter type: {adapter_type}. "
                f"Available: {available}"
            )
        
        adapter_class = cls._registry[adapter_type]
        return adapter_class(config)
    
    @classmethod
    def auto_detect(
        cls,
        preferred: Optional[str] = None
    ) -> UniversalAdapter:
        """
        Auto-detect appropriate adapter from environment.
        
        Detection priority:
        1. Preferred adapter (if specified and available)
        2. Azure DevOps (if AZURE_DEVOPS_PAT or AZURE_DEVOPS_ORG_URL set)
        3. GitHub (if GITHUB_TOKEN set)
        4. FileSystem (fallback)
        
        Args:
            preferred: Preferred adapter type (overrides auto-detection)
            
        Returns:
            Auto-detected adapter instance
        """
        # Check preferred
        if preferred and preferred in cls._registry:
            logger.info(f"Using preferred adapter: {preferred}")
            return cls.create(preferred)
        
        # Auto-detect from environment
        if os.getenv("AZURE_DEVOPS_PAT") or os.getenv("AZURE_DEVOPS_ORG_URL"):
            logger.info("Auto-detected: Azure DevOps (PAT or ORG_URL found)")
            return cls.create("azure_devops", {
                "org_url": os.getenv("AZURE_DEVOPS_ORG_URL"),
                "pat": os.getenv("AZURE_DEVOPS_PAT")
            })
        
        if os.getenv("GITHUB_TOKEN"):
            logger.info("Auto-detected: GitHub (GITHUB_TOKEN found)")
            return cls.create("github", {
                "token": os.getenv("GITHUB_TOKEN")
            })
        
        # Fallback to filesystem
        logger.info("Auto-detected: FileSystem (no cloud credentials found)")
        return cls.create("filesystem")
    
    @classmethod
    def list_adapters(cls) -> List[str]:
        """Get list of registered adapter types"""
        return list(cls._registry.keys())
