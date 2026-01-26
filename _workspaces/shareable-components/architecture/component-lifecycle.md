# CORTEX Component Lifecycle Specification

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** 2026-01-26  
**Status:** SPECIFICATION  

---

## 1. Component States

```
┌─────────────┐
│   CREATED   │ Component class instantiated
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ INITIALIZING│ Loading governance, audit, knowledge
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   READY     │ Component ready to accept operations
└──────┬──────┘
       │
       ├──────────────────────────────────────┐
       ▼                                      ▼
┌─────────────┐                        ┌─────────────┐
│  EXECUTING  │ Processing operation   │   PAUSED    │ Temporarily stopped
└──────┬──────┘                        └──────┬──────┘
       │                                      │
       ├──────────────────────────────────────┤
       ▼                                      ▼
┌─────────────┐                        ┌─────────────┐
│  COMPLETED  │ Operation finished     │   ERROR     │ Operation failed
└──────┬──────┘                        └──────┬──────┘
       │                                      │
       └──────────────────┬───────────────────┘
                          ▼
                   ┌─────────────┐
                   │    READY    │ Ready for next operation
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  SHUTDOWN   │ Component terminating
                   └─────────────┘
```

---

## 2. Lifecycle Events

### 2.1 Creation Phase

```python
class ComponentLifecycle:
    """Manages component lifecycle events"""
    
    async def on_create(self, component: CORTEXComponent):
        """Called when component is instantiated"""
        component.state = ComponentState.CREATED
        await self._emit_event('component.created', {
            'name': component.metadata.name,
            'version': component.metadata.version,
            'mode': 'integrated' if component.is_integrated else 'standalone'
        })
    
    async def on_initialize(self, component: CORTEXComponent):
        """Called during component initialization"""
        component.state = ComponentState.INITIALIZING
        
        # Load governance rules
        await component.governance.load_rules(component.metadata.governance_rules)
        
        # Initialize audit
        await component.audit.initialize(component.metadata.name)
        
        # Load knowledge
        await component.knowledge.load_domain(component.metadata.domain)
        
        component.state = ComponentState.READY
        await self._emit_event('component.ready', {
            'name': component.metadata.name,
            'governance_rules': len(component.metadata.governance_rules),
            'knowledge_loaded': component.knowledge.entry_count
        })
    
    async def on_execute_start(self, component: CORTEXComponent, operation: str):
        """Called when operation execution starts"""
        component.state = ComponentState.EXECUTING
        await self._emit_event('component.executing', {
            'name': component.metadata.name,
            'operation': operation
        })
    
    async def on_execute_complete(
        self, 
        component: CORTEXComponent, 
        operation: str, 
        success: bool
    ):
        """Called when operation execution completes"""
        component.state = ComponentState.COMPLETED if success else ComponentState.ERROR
        await self._emit_event('component.operation_complete', {
            'name': component.metadata.name,
            'operation': operation,
            'success': success
        })
        
        # Return to ready state
        component.state = ComponentState.READY
    
    async def on_shutdown(self, component: CORTEXComponent):
        """Called when component is shutting down"""
        component.state = ComponentState.SHUTDOWN
        
        # Flush audit logs
        await component.audit.flush()
        
        # Cleanup resources
        await component.cleanup()
        
        await self._emit_event('component.shutdown', {
            'name': component.metadata.name
        })
```

---

## 3. Lifecycle Hooks

### 3.1 Hook Interface

```python
class ComponentHooks:
    """Hooks for component lifecycle customization"""
    
    async def before_execute(
        self, 
        operation: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Called before operation execution.
        Can modify params or abort execution.
        
        Returns:
            Modified params or raises to abort
        """
        return params
    
    async def after_execute(
        self, 
        operation: str, 
        result: Result
    ) -> Result:
        """
        Called after operation execution.
        Can modify result or add side effects.
        
        Returns:
            Modified result
        """
        return result
    
    async def on_error(
        self, 
        operation: str, 
        error: Exception
    ) -> Optional[Result]:
        """
        Called when operation fails.
        Can recover or transform error.
        
        Returns:
            Recovery result or None to propagate error
        """
        return None
    
    async def on_governance_violation(
        self, 
        operation: str, 
        violation: str
    ) -> bool:
        """
        Called when governance check fails.
        Can allow or deny override.
        
        Returns:
            True to allow operation anyway, False to block
        """
        return False
```

### 3.2 Hook Registration

```python
@register_component(
    name="test-automation",
    version="1.0.0",
    # ...
)
class TestAutomationComponent(CORTEXComponent):
    
    def __init__(self, integrated_mode: bool = False):
        super().__init__(integrated_mode)
        
        # Register lifecycle hooks
        self.hooks.register('before_execute', self._validate_ticket_id)
        self.hooks.register('after_execute', self._notify_completion)
        self.hooks.register('on_error', self._handle_ado_errors)
    
    async def _validate_ticket_id(self, operation: str, params: Dict) -> Dict:
        """Validate ticket ID format before execution"""
        if 'ticket_id' in params:
            params['ticket_id'] = self._normalize_ticket_id(params['ticket_id'])
        return params
    
    async def _notify_completion(self, operation: str, result: Result) -> Result:
        """Send notification on completion"""
        if result.is_ok and operation == 'generate_test':
            await self._send_notification(result.value)
        return result
    
    async def _handle_ado_errors(self, operation: str, error: Exception) -> Optional[Result]:
        """Handle ADO-specific errors with recovery"""
        if 'ADO' in str(error):
            # Retry with cached data
            return await self._retry_with_cache(operation)
        return None
```

---

## 4. Health Checks

### 4.1 Component Health

```python
@dataclass
class ComponentHealth:
    """Component health status"""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    checks: Dict[str, bool]
    last_check: str
    uptime_seconds: float
    operations_processed: int
    errors_count: int
    
    @property
    def is_healthy(self) -> bool:
        return self.status == 'healthy'


class HealthChecker:
    """Health checking for components"""
    
    async def check_health(self, component: CORTEXComponent) -> ComponentHealth:
        """Perform comprehensive health check"""
        checks = {}
        
        # Check governance availability
        checks['governance'] = await self._check_governance(component)
        
        # Check audit system
        checks['audit'] = await self._check_audit(component)
        
        # Check knowledge access
        checks['knowledge'] = await self._check_knowledge(component)
        
        # Check MCP tools registration
        checks['mcp_tools'] = await self._check_mcp_tools(component)
        
        # Determine overall status
        if all(checks.values()):
            status = 'healthy'
        elif any(checks.values()):
            status = 'degraded'
        else:
            status = 'unhealthy'
        
        return ComponentHealth(
            status=status,
            checks=checks,
            last_check=datetime.now().isoformat(),
            uptime_seconds=component.uptime,
            operations_processed=component.operation_count,
            errors_count=component.error_count
        )
    
    async def _check_governance(self, component: CORTEXComponent) -> bool:
        """Check if governance system is responsive"""
        try:
            result = component.governance.validate_operation('health_check', {})
            return True
        except Exception:
            return False
    
    async def _check_audit(self, component: CORTEXComponent) -> bool:
        """Check if audit system is working"""
        try:
            component.audit.log_health_check()
            return True
        except Exception:
            return False
    
    async def _check_knowledge(self, component: CORTEXComponent) -> bool:
        """Check if knowledge is accessible"""
        try:
            entries = component.knowledge.get_entries(limit=1)
            return True
        except Exception:
            return False
    
    async def _check_mcp_tools(self, component: CORTEXComponent) -> bool:
        """Check if MCP tools are registered"""
        try:
            tools = component.get_mcp_tools()
            return len(tools) > 0
        except Exception:
            return False
```

### 4.2 Health Endpoint

```python
# MCP health tool (auto-registered for all components)
@mcp_tool(description="Check component health status")
async def health_check(self) -> ComponentHealth:
    """
    Get current health status of the component.
    
    Returns:
        ComponentHealth with status, checks, and metrics
    """
    checker = HealthChecker()
    return await checker.check_health(self)
```

---

## 5. Graceful Shutdown

### 5.1 Shutdown Sequence

```python
class GracefulShutdown:
    """Manages graceful component shutdown"""
    
    def __init__(self, component: CORTEXComponent):
        self.component = component
        self.shutdown_requested = False
        self.active_operations: Set[str] = set()
    
    async def request_shutdown(self, timeout_seconds: float = 30.0):
        """
        Request graceful shutdown.
        
        Waits for active operations to complete before shutdown.
        Forces shutdown after timeout.
        """
        self.shutdown_requested = True
        
        # Log shutdown initiation
        self.component.audit.log_operation_start(
            component=self.component.metadata.name,
            operation='shutdown',
            params={'timeout': timeout_seconds}
        )
        
        # Wait for active operations
        start_time = datetime.now()
        while self.active_operations:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                # Force shutdown
                await self._force_shutdown()
                return
            
            await asyncio.sleep(0.1)
        
        # Clean shutdown
        await self._clean_shutdown()
    
    async def _clean_shutdown(self):
        """Perform clean shutdown"""
        # Flush all pending audit logs
        await self.component.audit.flush()
        
        # Save any cached state
        if hasattr(self.component, '_save_state'):
            await self.component._save_state()
        
        # Notify lifecycle
        await self.component.lifecycle.on_shutdown(self.component)
    
    async def _force_shutdown(self):
        """Force shutdown with warnings"""
        pending = len(self.active_operations)
        self.component.audit.log_warning(
            f"Force shutdown with {pending} pending operations"
        )
        
        # Cancel pending operations
        for op_id in self.active_operations:
            self.component.audit.log_operation_complete(
                operation_id=op_id,
                success=False,
                error='Cancelled due to shutdown'
            )
        
        await self._clean_shutdown()
```

---

## 6. Resource Management

### 6.1 Connection Pooling

```python
class ComponentResources:
    """Resource management for components"""
    
    def __init__(self, component: CORTEXComponent):
        self.component = component
        self._connections: Dict[str, Any] = {}
        self._pools: Dict[str, Any] = {}
    
    async def get_connection(self, resource_type: str) -> Any:
        """Get or create connection to resource"""
        if resource_type not in self._connections:
            self._connections[resource_type] = await self._create_connection(
                resource_type
            )
        return self._connections[resource_type]
    
    async def get_pool(self, resource_type: str, size: int = 5) -> Any:
        """Get or create connection pool"""
        if resource_type not in self._pools:
            self._pools[resource_type] = await self._create_pool(
                resource_type, size
            )
        return self._pools[resource_type]
    
    async def cleanup(self):
        """Cleanup all resources"""
        for conn in self._connections.values():
            await self._close_connection(conn)
        
        for pool in self._pools.values():
            await self._close_pool(pool)
        
        self._connections.clear()
        self._pools.clear()
```

### 6.2 Memory Management

```python
class ComponentMemory:
    """Memory management for components"""
    
    def __init__(self, max_cache_mb: float = 100):
        self.max_cache_bytes = max_cache_mb * 1024 * 1024
        self._cache: Dict[str, Any] = {}
        self._cache_sizes: Dict[str, int] = {}
        self._total_size: int = 0
    
    def cache(self, key: str, value: Any, size_bytes: int):
        """Cache value with size tracking"""
        # Evict if necessary
        while self._total_size + size_bytes > self.max_cache_bytes:
            self._evict_oldest()
        
        self._cache[key] = value
        self._cache_sizes[key] = size_bytes
        self._total_size += size_bytes
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        return self._cache.get(key)
    
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            size = self._cache_sizes.pop(oldest_key)
            del self._cache[oldest_key]
            self._total_size -= size
```

---

## 7. Metrics & Observability

### 7.1 Component Metrics

```python
@dataclass
class ComponentMetrics:
    """Metrics collected for component"""
    operations_total: int = 0
    operations_success: int = 0
    operations_failed: int = 0
    operations_in_progress: int = 0
    
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    governance_checks_total: int = 0
    governance_violations: int = 0
    
    audit_entries_total: int = 0
    audit_entries_pending: int = 0
    
    memory_used_bytes: int = 0
    cache_hit_rate: float = 0.0


class MetricsCollector:
    """Collects and exposes component metrics"""
    
    def __init__(self, component: CORTEXComponent):
        self.component = component
        self._latencies: List[float] = []
        self._metrics = ComponentMetrics()
    
    def record_operation(self, latency_ms: float, success: bool):
        """Record operation completion"""
        self._metrics.operations_total += 1
        if success:
            self._metrics.operations_success += 1
        else:
            self._metrics.operations_failed += 1
        
        self._latencies.append(latency_ms)
        self._update_latency_percentiles()
    
    def get_metrics(self) -> ComponentMetrics:
        """Get current metrics snapshot"""
        return self._metrics
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        m = self._metrics
        name = self.component.metadata.name.replace('-', '_')
        
        lines.append(f'cortex_component_operations_total{{component="{name}"}} {m.operations_total}')
        lines.append(f'cortex_component_operations_success{{component="{name}"}} {m.operations_success}')
        lines.append(f'cortex_component_operations_failed{{component="{name}"}} {m.operations_failed}')
        lines.append(f'cortex_component_latency_p50{{component="{name}"}} {m.p50_latency_ms}')
        lines.append(f'cortex_component_latency_p95{{component="{name}"}} {m.p95_latency_ms}')
        lines.append(f'cortex_component_latency_p99{{component="{name}"}} {m.p99_latency_ms}')
        
        return '\n'.join(lines)
```

---

## 8. Integration Points

### 8.1 CORTEX Integration Lifecycle

When component transitions from standalone to integrated mode:

```python
class IntegrationTransition:
    """Manages transition from standalone to integrated mode"""
    
    async def transition_to_integrated(self, component: CORTEXComponent):
        """
        Transition component from standalone to integrated mode.
        
        This happens when:
        1. CORTEX is installed in the environment
        2. Component detects CORTEX availability
        3. User explicitly requests integration
        """
        # Migrate audit logs to CORTEX
        await self._migrate_audit_logs(component)
        
        # Upgrade governance to full CORTEX
        await self._upgrade_governance(component)
        
        # Connect to knowledge repository
        await self._connect_knowledge(component)
        
        # Register with DatabaseBackedRegistry
        await self._register_with_cortex(component)
        
        # Update mode flag
        component._integrated_mode = True
    
    async def _migrate_audit_logs(self, component: CORTEXComponent):
        """Migrate standalone audit logs to CORTEX"""
        from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
        
        cortex_audit = EnhancedAuditLogger.instance()
        standalone_logs = component.audit.get_all_logs()
        
        for log in standalone_logs:
            cortex_audit.import_log(log)
    
    async def _register_with_cortex(self, component: CORTEXComponent):
        """Register component with CORTEX registry"""
        from cortex.orchestrators import get_database_registry
        
        registry = get_database_registry()
        await registry.register_component(
            name=component.metadata.name,
            version=component.metadata.version,
            component_class=type(component).__name__,
            module=type(component).__module__
        )
```
