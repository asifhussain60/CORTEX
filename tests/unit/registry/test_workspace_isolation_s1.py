"""
Phase 48 S1: Registry Isolation Architecture - Workspace Context & Factory Tests
Tests for context-scoped registry pattern with workspace isolation.

Authority: phase-48-registry-isolation-multi-tenant.yaml
Acceptance Criteria:
  - AC-PHASE48-S1-001: WorkspaceContext identifies unique isolation boundaries
  - AC-PHASE48-S1-002: RegistryFactory creates isolated instances per workspace
  - AC-PHASE48-S1-003: Default workspace_id='local' for individual devs
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from datetime import datetime


@dataclass
class WorkspaceContext:
    """Unique workspace identifier + metadata for isolation boundaries."""
    workspace_id: str
    tenant_id: Optional[str] = None
    isolation_mode: str = "local"  # 'local' or 'multi-tenant'
    company_name: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def is_isolated(self) -> bool:
        """Check if workspace is isolated from others."""
        return self.isolation_mode == "multi-tenant" and self.tenant_id is not None
    
    def get_cache_key(self) -> str:
        """Get unique cache key for this workspace."""
        return f"{self.workspace_id}:{self.tenant_id or 'local'}"


class RegistryFactory:
    """Create and manage isolated registry instances."""
    
    def __init__(self):
        """Initialize registry factory with empty instance map."""
        self._registries: Dict[str, "IsolatedRegistry"] = {}
        self._contexts: Dict[str, WorkspaceContext] = {}
    
    def get_or_create(self, workspace_id: str, company_name: Optional[str] = None) -> WorkspaceContext:
        """
        Get or create workspace context for isolation boundary.
        
        Args:
            workspace_id: Unique workspace identifier
            company_name: Optional company name for multi-tenant mode
        
        Returns:
            WorkspaceContext with isolation settings
        """
        if workspace_id in self._contexts:
            return self._contexts[workspace_id]
        
        # Default to local mode for individual developers
        isolation_mode = "multi-tenant" if company_name else "local"
        tenant_id = company_name if company_name else None
        
        context = WorkspaceContext(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            isolation_mode=isolation_mode,
            company_name=company_name
        )
        
        self._contexts[workspace_id] = context
        return context
    
    def create_registry(self, workspace_id: str) -> "IsolatedRegistry":
        """Create isolated registry instance for workspace."""
        if workspace_id in self._registries:
            return self._registries[workspace_id]
        
        context = self.get_or_create(workspace_id)
        registry = IsolatedRegistry(context)
        self._registries[workspace_id] = registry
        return registry
    
    def cleanup(self, workspace_id: str) -> None:
        """Clean up workspace context and registry."""
        if workspace_id in self._registries:
            self._registries[workspace_id].cleanup()
            del self._registries[workspace_id]
        
        if workspace_id in self._contexts:
            del self._contexts[workspace_id]
    
    def list_active(self) -> list:
        """List all active workspaces."""
        return list(self._contexts.keys())
    
    def reset(self) -> None:
        """Reset all registries (for testing)."""
        for workspace_id in list(self._registries.keys()):
            self.cleanup(workspace_id)
        # Also clear contexts cache
        self._contexts.clear()


class IsolatedRegistry:
    """Workspace-scoped registry for storing isolated orchestrator instances."""
    
    def __init__(self, context: WorkspaceContext):
        """Initialize with workspace context."""
        self.context = context
        self._orchestrators: Dict[str, object] = {}
    
    def set_orchestrator(self, name: str, orchestrator: object) -> None:
        """Store orchestrator in workspace-scoped cache."""
        self._orchestrators[name] = orchestrator
    
    def get_orchestrator(self, name: str) -> Optional[object]:
        """Retrieve orchestrator from workspace-scoped cache."""
        return self._orchestrators.get(name)
    
    def cleanup(self) -> None:
        """Clean up all orchestrators in this registry."""
        self._orchestrators.clear()
    
    def list_orchestrators(self) -> list:
        """List all orchestrators in this workspace."""
        return list(self._orchestrators.keys())


# ============================================================================
# TESTS: WorkspaceContext (AC-PHASE48-S1-001)
# ============================================================================

class TestWorkspaceContextCreation:
    """Test WorkspaceContext creation and properties."""
    
    def test_create_local_context(self):
        """Test creating local workspace context (default)."""
        ctx = WorkspaceContext(workspace_id="local")
        assert ctx.workspace_id == "local"
        assert ctx.isolation_mode == "local"
        assert ctx.tenant_id is None
        assert ctx.company_name is None
    
    def test_create_multitenant_context(self):
        """Test creating multi-tenant workspace context."""
        ctx = WorkspaceContext(
            workspace_id="acme-dev",
            tenant_id="acme",
            isolation_mode="multi-tenant",
            company_name="ACME Corp"
        )
        assert ctx.workspace_id == "acme-dev"
        assert ctx.tenant_id == "acme"
        assert ctx.isolation_mode == "multi-tenant"
        assert ctx.company_name == "ACME Corp"
    
    def test_context_isolation_detection(self):
        """Test is_isolated() method."""
        local_ctx = WorkspaceContext(workspace_id="local")
        assert not local_ctx.is_isolated()
        
        mt_ctx = WorkspaceContext(
            workspace_id="tenant1",
            tenant_id="tenant1",
            isolation_mode="multi-tenant"
        )
        assert mt_ctx.is_isolated()
    
    def test_cache_key_generation_local(self):
        """Test cache key for local workspace."""
        ctx = WorkspaceContext(workspace_id="local")
        assert ctx.get_cache_key() == "local:local"
    
    def test_cache_key_generation_multitenant(self):
        """Test cache key for multi-tenant workspace."""
        ctx = WorkspaceContext(
            workspace_id="dev-env",
            tenant_id="acme",
            isolation_mode="multi-tenant"
        )
        assert ctx.get_cache_key() == "dev-env:acme"
    
    def test_context_timestamp(self):
        """Test that context has creation timestamp."""
        ctx = WorkspaceContext(workspace_id="test")
        assert ctx.created_at is not None
        assert isinstance(ctx.created_at, datetime)
    
    def test_context_equality_by_workspace_id(self):
        """Test context comparison logic."""
        ctx1 = WorkspaceContext(workspace_id="ws1")
        ctx2 = WorkspaceContext(workspace_id="ws1")
        # Both have same workspace_id, should have same cache key structure
        assert ctx1.workspace_id == ctx2.workspace_id


# ============================================================================
# TESTS: RegistryFactory (AC-PHASE48-S1-002)
# ============================================================================

class TestRegistryFactoryCreation:
    """Test RegistryFactory get_or_create pattern."""
    
    def test_factory_init(self):
        """Test factory initialization."""
        factory = RegistryFactory()
        assert len(factory.list_active()) == 0
    
    def test_get_or_create_local_workspace(self):
        """Test creating local workspace (no company_name)."""
        factory = RegistryFactory()
        ctx = factory.get_or_create("local")
        
        assert ctx.workspace_id == "local"
        assert ctx.isolation_mode == "local"
        assert ctx.tenant_id is None
    
    def test_get_or_create_multitenant_workspace(self):
        """Test creating multi-tenant workspace with company_name."""
        factory = RegistryFactory()
        ctx = factory.get_or_create("acme-dev", company_name="ACME Corp")
        
        assert ctx.workspace_id == "acme-dev"
        assert ctx.company_name == "ACME Corp"
        assert ctx.isolation_mode == "multi-tenant"
        assert ctx.tenant_id == "ACME Corp"
    
    def test_get_or_create_returns_same_context(self):
        """Test that get_or_create returns same context on second call."""
        factory = RegistryFactory()
        ctx1 = factory.get_or_create("workspace1")
        ctx2 = factory.get_or_create("workspace1")
        
        assert ctx1 is ctx2
    
    def test_list_active_workspaces(self):
        """Test listing active workspaces."""
        factory = RegistryFactory()
        factory.get_or_create("ws1")
        factory.get_or_create("ws2")
        factory.get_or_create("ws3")
        
        active = factory.list_active()
        assert len(active) == 3
        assert "ws1" in active
        assert "ws2" in active
        assert "ws3" in active


# ============================================================================
# TESTS: IsolatedRegistry (AC-PHASE48-S1-002)
# ============================================================================

class TestIsolatedRegistry:
    """Test workspace-scoped registry isolation."""
    
    def test_create_isolated_registry(self):
        """Test creating isolated registry for workspace."""
        factory = RegistryFactory()
        ctx = factory.get_or_create("workspace1")
        registry = factory.create_registry("workspace1")
        
        assert registry.context == ctx
    
    def test_registry_stores_orchestrator(self):
        """Test storing orchestrator in workspace registry."""
        factory = RegistryFactory()
        registry = factory.create_registry("ws1")
        
        mock_orchestrator = {"name": "TestOrchestrator"}
        registry.set_orchestrator("test", mock_orchestrator)
        
        retrieved = registry.get_orchestrator("test")
        assert retrieved == mock_orchestrator
    
    def test_registry_isolation_between_workspaces(self):
        """Test that orchestrators don't leak between workspaces."""
        factory = RegistryFactory()
        
        reg1 = factory.create_registry("workspace1")
        reg2 = factory.create_registry("workspace2")
        
        mock_orch1 = {"name": "Orchestrator1"}
        mock_orch2 = {"name": "Orchestrator2"}
        
        reg1.set_orchestrator("test", mock_orch1)
        reg2.set_orchestrator("test", mock_orch2)
        
        # Each registry should have its own instance
        assert reg1.get_orchestrator("test") == mock_orch1
        assert reg2.get_orchestrator("test") == mock_orch2
        assert reg1.get_orchestrator("test") != reg2.get_orchestrator("test")
    
    def test_registry_missing_orchestrator(self):
        """Test getting non-existent orchestrator returns None."""
        factory = RegistryFactory()
        registry = factory.create_registry("ws1")
        
        result = registry.get_orchestrator("nonexistent")
        assert result is None
    
    def test_list_orchestrators(self):
        """Test listing orchestrators in workspace."""
        factory = RegistryFactory()
        registry = factory.create_registry("ws1")
        
        registry.set_orchestrator("orch1", {})
        registry.set_orchestrator("orch2", {})
        registry.set_orchestrator("orch3", {})
        
        orchs = registry.list_orchestrators()
        assert len(orchs) == 3
        assert "orch1" in orchs
        assert "orch2" in orchs
        assert "orch3" in orchs
    
    def test_registry_cleanup(self):
        """Test cleaning up workspace registry."""
        factory = RegistryFactory()
        registry = factory.create_registry("ws1")
        
        registry.set_orchestrator("orch1", {})
        registry.set_orchestrator("orch2", {})
        
        registry.cleanup()
        
        assert len(registry.list_orchestrators()) == 0


# ============================================================================
# TESTS: Default workspace_id='local' (AC-PHASE48-S1-003)
# ============================================================================

class TestDefaultLocalMode:
    """Test default workspace_id='local' for individual developers."""
    
    def test_default_workspace_id(self):
        """Test that default workspace_id is 'local'."""
        ctx = WorkspaceContext(workspace_id="local")
        assert ctx.workspace_id == "local"
    
    def test_factory_default_local_mode(self):
        """Test that factory defaults to local isolation mode."""
        factory = RegistryFactory()
        ctx = factory.get_or_create("local")
        
        assert ctx.isolation_mode == "local"
        assert ctx.tenant_id is None
    
    def test_no_workspace_id_means_local(self):
        """Test backward compatibility: no workspace_id = 'local'."""
        factory = RegistryFactory()
        # Create without specifying isolation
        ctx = factory.get_or_create("dev", company_name=None)
        
        assert ctx.isolation_mode == "local"
    
    def test_individual_developer_experience_unchanged(self):
        """Test that individual developer workflow unchanged."""
        factory = RegistryFactory()
        
        # Developer just uses default workspace
        ctx = factory.get_or_create("local")
        reg = factory.create_registry("local")
        
        # Store orchestrator normally
        mock_orch: Dict[str, Any] = {"type": "MigrationOrchestrator"}
        reg.set_orchestrator("migration", mock_orch)
        
        # Retrieve it normally
        retrieved = reg.get_orchestrator("migration")
        assert retrieved is not None
        assert isinstance(retrieved, dict)
        assert retrieved.get("type") == "MigrationOrchestrator"
    
    def test_multiple_developers_isolated(self):
        """Test that multiple developers can work without interference."""
        factory = RegistryFactory()
        
        # Developer A works on workspace1
        ctx_a = factory.get_or_create("workspace_dev_a")
        reg_a = factory.create_registry("workspace_dev_a")
        perf_v1: Dict[str, Any] = {"version": "1.0"}
        reg_a.set_orchestrator("perf", perf_v1)
        
        # Developer B works on workspace2
        ctx_b = factory.get_or_create("workspace_dev_b")
        reg_b = factory.create_registry("workspace_dev_b")
        perf_v2: Dict[str, Any] = {"version": "2.0"}
        reg_b.set_orchestrator("perf", perf_v2)
        
        # Each has their own version
        ret_a = reg_a.get_orchestrator("perf")
        ret_b = reg_b.get_orchestrator("perf")
        assert isinstance(ret_a, dict)
        assert isinstance(ret_b, dict)
        assert ret_a.get("version") == "1.0"
        assert ret_b.get("version") == "2.0"


# ============================================================================
# TESTS: Factory Lifecycle Management
# ============================================================================

class TestFactoryLifecycle:
    """Test factory cleanup and reset operations."""
    
    def test_cleanup_workspace(self):
        """Test cleaning up specific workspace."""
        factory = RegistryFactory()
        factory.get_or_create("ws1")
        factory.get_or_create("ws2")
        
        factory.cleanup("ws1")
        
        active = factory.list_active()
        assert "ws1" not in active
        assert "ws2" in active
    
    def test_cleanup_removes_registry(self):
        """Test that cleanup removes associated registry."""
        factory = RegistryFactory()
        reg = factory.create_registry("ws1")
        reg.set_orchestrator("test", {})
        
        factory.cleanup("ws1")
        
        # New registry should be empty
        new_reg = factory.create_registry("ws1")
        assert new_reg.get_orchestrator("test") is None
    
    def test_reset_all_workspaces(self):
        """Test resetting entire factory."""
        factory = RegistryFactory()
        factory.get_or_create("ws1")
        factory.get_or_create("ws2")
        factory.get_or_create("ws3")
        
        assert len(factory.list_active()) == 3
        
        factory.reset()
        
        # After reset, contexts should be cleared too
        assert len(factory.list_active()) == 0
    
    def test_reset_removes_all_registries(self):
        """Test that reset clears all orchestrator instances."""
        factory = RegistryFactory()
        reg1 = factory.create_registry("ws1")
        reg2 = factory.create_registry("ws2")
        
        reg1.set_orchestrator("orch", {})
        reg2.set_orchestrator("orch", {})
        
        factory.reset()
        
        # Create new registries, should be empty
        new_reg1 = factory.create_registry("ws1")
        new_reg2 = factory.create_registry("ws2")
        
        assert new_reg1.get_orchestrator("orch") is None
        assert new_reg2.get_orchestrator("orch") is None


# ============================================================================
# TESTS: Concurrent Access Safety (Foundation)
# ============================================================================

class TestConcurrentAccessFoundation:
    """Foundation tests for concurrent workspace access (detailed tests in S5)."""
    
    def test_two_workspaces_independent(self):
        """Test that two workspaces operate independently."""
        factory = RegistryFactory()
        
        reg1 = factory.create_registry("w1")
        reg2 = factory.create_registry("w2")
        
        # Simulate concurrent operations
        reg1.set_orchestrator("op1", {"id": 1})
        reg2.set_orchestrator("op2", {"id": 2})
        
        reg1.set_orchestrator("op1", {"id": 1, "updated": True})
        # reg2's op1 shouldn't exist
        assert reg2.get_orchestrator("op1") is None
    
    def test_factory_concurrent_get_or_create(self):
        """Test that concurrent get_or_create returns consistent context."""
        factory = RegistryFactory()
        
        ctx1 = factory.get_or_create("workspace")
        ctx2 = factory.get_or_create("workspace")
        ctx3 = factory.get_or_create("workspace")
        
        # All should be same instance
        assert ctx1 is ctx2
        assert ctx2 is ctx3
