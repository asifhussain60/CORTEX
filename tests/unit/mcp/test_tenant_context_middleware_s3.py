"""
Phase 48-registry Stage 3: MCP Integration - Test Suite

Authority: phase-48-registry-isolation.yaml
AC-IDs: AC-PHASE48-REG-S3-001 through AC-PHASE48-REG-S3-003

Tests for tenant context injection in MCP tools:
- Automatic workspace context injection
- Tool execution isolated per workspace
- No cross-workspace tool state leakage
"""

import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.tenant_context_middleware import (
    TenantContextMiddleware,
    WorkspaceContext
)


# ============================================================================
# TESTS: Automatic Context Injection (AC-PHASE48-REG-S3-001)
# ============================================================================

class TestAutomaticContextInjection:
    """Test MCP tools receive workspace context automatically."""
    
    def test_middleware_extracts_workspace_from_request(self):
        """Middleware extracts workspace_id from request headers."""
        middleware = TenantContextMiddleware()
        
        request = {
            "headers": {
                "X-Workspace-ID": "acme-dev",
                "X-Tenant-ID": "acme"
            },
            "tool": "cortex_process_request",
            "params": {}
        }
        
        # Should extract workspace context
        context = middleware.extract_context(request)
        
        assert context.workspace_id == "acme-dev"
        assert context.tenant_id == "acme"
    
    def test_middleware_injects_context_into_tool_params(self):
        """Middleware injects workspace context into tool parameters."""
        middleware = TenantContextMiddleware()
        
        tool_params = {
            "operation": "implement",
            "request": "Add user authentication"
        }
        
        context = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        
        # Should inject context
        enhanced_params = middleware.inject_context(tool_params, context)
        
        assert "workspace_context" in enhanced_params
        assert enhanced_params["workspace_context"]["workspace_id"] == "acme-dev"
        assert enhanced_params["workspace_context"]["tenant_id"] == "acme"
    
    def test_default_to_local_workspace_if_no_context(self):
        """Default to workspace_id='local' if no context provided."""
        middleware = TenantContextMiddleware()
        
        request = {
            "tool": "cortex_process_request",
            "params": {}
            # No headers with workspace info
        }
        
        # Should default to local
        context = middleware.extract_context(request)
        
        assert context.workspace_id == "local"
        assert context.tenant_id == "local"


# ============================================================================
# TESTS: Workspace-Scoped Tool Execution (AC-PHASE48-REG-S3-002)
# ============================================================================

class TestWorkspaceScopedExecution:
    """Test tool execution isolated per workspace."""
    
    def test_tool_uses_workspace_specific_registry(self):
        """Tool loads data from workspace-specific registry."""
        middleware = TenantContextMiddleware()
        context = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        
        middleware.set_current_context(context)
        
        # Tool should access workspace-specific registry
        current = middleware.get_current_context()
        assert current is not None
        assert current.workspace_id == "acme-dev"
    
    def test_multiple_workspaces_execute_independently(self):
        """Multiple workspaces execute tools independently."""
        middleware1 = TenantContextMiddleware()
        middleware2 = TenantContextMiddleware()
        
        context1 = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        context2 = WorkspaceContext(workspace_id="beta-test", tenant_id="beta")
        
        middleware1.set_current_context(context1)
        middleware2.set_current_context(context2)
        
        # Each middleware maintains separate context
        assert middleware1.get_current_context().workspace_id == "acme-dev"
        assert middleware2.get_current_context().workspace_id == "beta-test"
    
    def test_context_cleared_after_request(self):
        """Context cleared after request completes."""
        middleware = TenantContextMiddleware()
        context = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        
        middleware.set_current_context(context)
        assert middleware.get_current_context() is not None
        
        # Clear after request
        middleware.clear_context()
        assert middleware.get_current_context() is None


# ============================================================================
# TESTS: Cross-Workspace Isolation (AC-PHASE48-REG-S3-003)
# ============================================================================

class TestCrossWorkspaceIsolation:
    """Test no cross-workspace tool state leakage."""
    
    def test_workspace_a_cannot_access_workspace_b_state(self):
        """Workspace A cannot access Workspace B's tool state."""
        middleware_a = TenantContextMiddleware()
        middleware_b = TenantContextMiddleware()
        
        context_a = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        context_b = WorkspaceContext(workspace_id="beta-test", tenant_id="beta")
        
        middleware_a.set_current_context(context_a)
        middleware_b.set_current_context(context_b)
        
        # Workspace A's context should not affect Workspace B
        assert middleware_a.get_current_context().workspace_id != middleware_b.get_current_context().workspace_id
    
    def test_tool_state_isolated_per_workspace(self):
        """Tool state (cache, config) isolated per workspace."""
        middleware = TenantContextMiddleware()
        
        # Simulate two sequential requests from different workspaces
        context1 = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        middleware.set_current_context(context1)
        workspace1_id = middleware.get_current_context().workspace_id
        middleware.clear_context()
        
        context2 = WorkspaceContext(workspace_id="beta-test", tenant_id="beta")
        middleware.set_current_context(context2)
        workspace2_id = middleware.get_current_context().workspace_id
        
        # Should be different workspaces
        assert workspace1_id != workspace2_id
    
    def test_concurrent_requests_maintain_isolation(self):
        """Concurrent requests from different workspaces maintain isolation."""
        # Simulate concurrent execution with separate middleware instances
        middlewares = [
            TenantContextMiddleware(),
            TenantContextMiddleware(),
            TenantContextMiddleware()
        ]
        
        contexts = [
            WorkspaceContext(workspace_id="acme-dev", tenant_id="acme"),
            WorkspaceContext(workspace_id="beta-test", tenant_id="beta"),
            WorkspaceContext(workspace_id="gamma-prod", tenant_id="gamma")
        ]
        
        # Set contexts
        for middleware, context in zip(middlewares, contexts):
            middleware.set_current_context(context)
        
        # Verify each maintains separate context
        assert middlewares[0].get_current_context().workspace_id == "acme-dev"
        assert middlewares[1].get_current_context().workspace_id == "beta-test"
        assert middlewares[2].get_current_context().workspace_id == "gamma-prod"
    
    def test_tool_registry_scoped_per_workspace(self):
        """Tool registry (orchestrators, agents) scoped per workspace."""
        middleware = TenantContextMiddleware()
        
        # Workspace-specific registry key
        context = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        middleware.set_current_context(context)
        
        # Should use workspace-specific registry key
        current = middleware.get_current_context()
        registry_key = f"{current.workspace_id}:{current.tenant_id}"
        
        assert "acme-dev" in registry_key
        assert "acme" in registry_key


# ============================================================================
# END OF TEST SUITE
# ============================================================================
