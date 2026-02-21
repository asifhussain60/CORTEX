"""
Phase 48-registry Stage 3: Tenant Context Middleware - MCP Integration

Authority: phase-48-registry-isolation.yaml
AC-IDs: AC-PHASE48-REG-S3-001 through AC-PHASE48-REG-S3-003

Middleware for injecting workspace context into MCP tool requests:
- Extract workspace_id from request headers/metadata
- Create WorkspaceContext automatically
- Inject context into tool parameters
- Maintain workspace isolation

Example:
    # In MCP server request handler
    >>> middleware = TenantContextMiddleware()
    >>> request = {"headers": {"X-Workspace-ID": "acme-dev"}}
    >>> context = middleware.extract_context(request)
    >>> enhanced_params = middleware.inject_context(tool_params, context)
"""

# AC_START: AC-PHASE48-REG-S3-001
# Description: Tenant context middleware for MCP tool integration
# Stage: Phase 48-registry S3

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceContext:
    """
    Workspace context for MCP tool execution.
    
    Attributes:
        workspace_id: Unique workspace identifier
        tenant_id: Tenant identifier (for multi-tenant setups)
        user_id: Optional user identifier
        metadata: Optional metadata dict
    
    Example:
        >>> context = WorkspaceContext(
        ...     workspace_id="acme-dev",
        ...     tenant_id="acme",
        ...     user_id="alice@acme.com"
        ... )
    """
    workspace_id: str
    tenant_id: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace_id": self.workspace_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "metadata": self.metadata
        }


class TenantContextMiddleware:
    """
    Middleware for injecting workspace context into MCP tool requests.
    
    Features:
    - Extract workspace_id from request headers or context
    - Create WorkspaceContext automatically
    - Inject context into tool parameters
    - Maintain workspace isolation
    
    Example:
        >>> middleware = TenantContextMiddleware()
        >>> request = {"headers": {"X-Workspace-ID": "acme-dev"}}
        >>> context = middleware.extract_context(request)
        >>> tool_params = {"operation": "implement"}
        >>> enhanced = middleware.inject_context(tool_params, context)
    """
    
    def __init__(self) -> None:
        """Initialize tenant context middleware."""
        self._current_context: Optional[WorkspaceContext] = None
        logger.debug("TenantContextMiddleware initialized")
    
    def extract_context(self, request: Dict[str, Any]) -> WorkspaceContext:
        """
        Extract workspace context from request.
        
        Extraction order:
        1. Request headers (X-Workspace-ID, X-Tenant-ID)
        2. Request context dict
        3. Default to local workspace
        
        Args:
            request: MCP tool request with headers/metadata
        
        Returns:
            WorkspaceContext with workspace_id and tenant_id
        
        Example:
            >>> request = {
            ...     "headers": {
            ...         "X-Workspace-ID": "acme-dev",
            ...         "X-Tenant-ID": "acme"
            ...     }
            ... }
            >>> context = middleware.extract_context(request)
            >>> print(context.workspace_id)
            acme-dev
        """
        # Try to extract from headers
        headers = request.get("headers", {})
        workspace_id = headers.get("X-Workspace-ID")
        tenant_id = headers.get("X-Tenant-ID")
        user_id = headers.get("X-User-ID")
        
        # Fallback to context dict
        if not workspace_id:
            context_dict = request.get("context", {})
            workspace_id = context_dict.get("workspace_id")
            tenant_id = context_dict.get("tenant_id")
            user_id = context_dict.get("user_id")
        
        # Default to local workspace (single-tenant mode)
        if not workspace_id:
            workspace_id = "local"
            tenant_id = "local"
            logger.debug("No workspace context in request, defaulting to 'local'")
        
        # Ensure tenant_id matches workspace_id if not provided
        if not tenant_id:
            tenant_id = workspace_id
        
        context = WorkspaceContext(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            user_id=user_id,
            metadata=request.get("metadata", {})
        )
        
        logger.info(
            f"Extracted workspace context: workspace_id={workspace_id}, "
            f"tenant_id={tenant_id}"
        )
        
        return context
    
    def inject_context(
        self,
        tool_params: Dict[str, Any],
        context: WorkspaceContext
    ) -> Dict[str, Any]:
        """
        Inject workspace context into tool parameters.
        
        Args:
            tool_params: Original tool parameters
            context: Workspace context to inject
        
        Returns:
            Enhanced parameters with workspace context
        
        Example:
            >>> tool_params = {"operation": "implement"}
            >>> context = WorkspaceContext("acme-dev", "acme")
            >>> enhanced = middleware.inject_context(tool_params, context)
            >>> print(enhanced["workspace_context"]["workspace_id"])
            acme-dev
        """
        # Create enhanced parameters with workspace context
        enhanced_params = {
            **tool_params,
            "workspace_context": context.to_dict()
        }
        
        logger.debug(
            f"Injected workspace context into tool params: "
            f"workspace_id={context.workspace_id}"
        )
        
        return enhanced_params
    
    def set_current_context(self, context: WorkspaceContext) -> None:
        """
        Set current workspace context for this request.
        
        Args:
            context: Workspace context to set
        
        Example:
            >>> context = WorkspaceContext("acme-dev", "acme")
            >>> middleware.set_current_context(context)
        """
        self._current_context = context
        logger.debug(f"Current context set: workspace_id={context.workspace_id}")
    
    def get_current_context(self) -> Optional[WorkspaceContext]:
        """
        Get current workspace context.
        
        Returns:
            Current WorkspaceContext or None
        
        Example:
            >>> context = middleware.get_current_context()
            >>> if context:
            ...     print(context.workspace_id)
        """
        return self._current_context
    
    def clear_context(self) -> None:
        """
        Clear workspace context after request.
        
        Should be called after each MCP tool request completes
        to prevent context leakage between requests.
        
        Example:
            >>> try:
            ...     # Process tool request
            ...     pass
            ... finally:
            ...     middleware.clear_context()
        """
        if self._current_context:
            workspace_id = self._current_context.workspace_id
            self._current_context = None
            logger.debug(f"Context cleared for workspace_id={workspace_id}")
    
    def process_request(
        self,
        request: Dict[str, Any],
        tool_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process full request: extract context + inject into params.
        
        Convenience method that combines extract_context and inject_context.
        
        Args:
            request: MCP tool request
            tool_params: Tool parameters
        
        Returns:
            Enhanced parameters with workspace context
        
        Example:
            >>> request = {"headers": {"X-Workspace-ID": "acme-dev"}}
            >>> tool_params = {"operation": "implement"}
            >>> enhanced = middleware.process_request(request, tool_params)
        """
        context = self.extract_context(request)
        self.set_current_context(context)
        return self.inject_context(tool_params, context)
    
    def __repr__(self) -> str:
        """Return string representation."""
        context_info = "None"
        if self._current_context:
            context_info = f"workspace_id={self._current_context.workspace_id}"
        return f"TenantContextMiddleware(current_context={context_info})"


# AC_COMPLETE: AC-PHASE48-REG-S3-001 ✅ Tenant context middleware for MCP integration
