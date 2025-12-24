# Phase 7: Operations Simplification

**Duration:** Weeks 15-17 (15 days) | **Status:** ⏳ NOT STARTED | **Progress:** 0%

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Executive Summary

**Goal:** Simplify CORTEX operations by reducing manifest redundancy, implementing universal adapters, and enabling dependency injection auto-discovery across all 16 orchestrators.

**Rationale:** With 16 orchestrators migrated (Phase 6), operational complexity has increased. This phase addresses:
- 60%+ manifest redundancy across orchestrators
- Manual dependency wiring in 13+ locations
- Fragmented adapter patterns (Azure DevOps, GitHub, file systems)
- Configuration sprawl (14 YAML files)

**Impact:**
- 70% reduction in manifest size
- 90% auto-discovery of dependencies
- Single universal adapter interface
- 50% faster onboarding for new orchestrators

**Dependencies:** Phase 6 complete (16 orchestrators migrated)

---

## 📋 Phase Objectives

### Primary Goals

1. **Manifest Consolidation** - Reduce 14 YAML manifests to 3 canonical sources
2. **Universal Adapters** - Single interface for Azure DevOps, GitHub, file operations
3. **Auto-Discovery** - Dependency injection with automatic wiring
4. **Configuration Centralization** - Unified config management

### Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Manifest Files | 14 | 3 | File count in `cortex-brain/manifests/` |
| Manifest Size | ~8,500 lines | ~2,500 lines | Total LOC across manifests |
| Manual DI Wiring | 13 locations | 0 | Grep for manual `__init__` wiring |
| Adapter Interfaces | 6 | 1 | Count of distinct adapter interfaces |
| Config Files | 8 | 1 | Files in `cortex-brain/config/` |
| Onboarding Time | 4 hours | 2 hours | Time to add new orchestrator |

---

## 🗓️ Timeline & Milestones

### Week 15: Manifest Consolidation (Days 1-5)

**Milestone:** Reduce manifest redundancy by 70%

**Tasks:**
1. Audit existing manifests (analyze redundancy)
2. Design 3-tier manifest architecture
3. Implement CoreManifest (orchestrator metadata)
4. Implement ConfigManifest (runtime configuration)
5. Implement IntegrationManifest (external systems)
6. Migrate 16 orchestrators to new manifests
7. Validate backward compatibility

**Deliverables:**
- `cortex-brain/manifests/core-manifest.yaml` (orchestrator registry)
- `cortex-brain/manifests/config-manifest.yaml` (configuration)
- `cortex-brain/manifests/integration-manifest.yaml` (external APIs)
- Migration guide for orchestrators
- 20 tests for manifest loading/validation

### Week 16: Universal Adapters (Days 6-10)

**Milestone:** Single adapter interface for all external systems

**Tasks:**
1. Design UniversalAdapter interface (CRUD + search)
2. Implement AzureDevOpsAdapter (work items, pipelines)
3. Implement GitHubAdapter (issues, actions, repos)
4. Implement FileSystemAdapter (local/network files)
5. Implement adapter factory with auto-detection
6. Migrate existing adapter usages
7. Add adapter middleware (caching, retry, rate limiting)

**Deliverables:**
- `src/orchestration_4_0/adapters/universal_adapter.py` (interface)
- `src/orchestration_4_0/adapters/azure_devops_adapter.py`
- `src/orchestration_4_0/adapters/github_adapter.py`
- `src/orchestration_4_0/adapters/filesystem_adapter.py`
- `src/orchestration_4_0/adapters/adapter_factory.py`
- 30 tests for adapters (CRUD, error handling, middleware)

### Week 17: Auto-Discovery, LLM Intent Detection & Validation (Days 11-15)

**Milestone:** Dependency injection with zero manual wiring + LLM-powered intent routing

**Tasks:**
1. Design DI container with auto-discovery
2. Implement service registration via decorators
3. Implement dependency resolution (constructor injection)
4. Add lifecycle management (singleton, transient, scoped)
5. Migrate 16 orchestrators to DI container
6. **Integrate LLM Intent Detection** (NEW - upgrade from keyword-based to semantic routing)
7. Wire LLMIntentRouter into IntentRouter with hybrid approach (fast path → LLM → fallback)
8. Add Tier 2 caching for intent classifications (reduce LLM calls by 80%)
9. Implement confidence-based fallback to regex (threshold: 0.8)
10. Test end-to-end with 50+ real user requests (measure accuracy improvement)
11. Create configuration validator
12. E2E validation of all orchestrators
13. Performance benchmarking
14. Documentation and migration guide

**Deliverables:**
- `src/orchestration_4_0/di/container.py` (DI container)
- `src/orchestration_4_0/di/decorators.py` (@service, @inject)
- `src/orchestration_4_0/di/lifecycle.py` (scope management)
- **`src/cortex_agents/intent_router.py` (LLM integration)** - Wire LLMIntentRouter with hybrid classification
- **`tests/cortex_agents/test_llm_intent_router.py`** - 20+ tests for LLM classification accuracy
- Migration complete for 16 orchestrators
- 25 tests for DI container
- Performance report (<10% regression, LLM latency <500ms p95)
- Complete documentation

**LLM Intent Detection Implementation:**

```python
# src/cortex_agents/intent_router.py (enhanced)

from .llm_intent_router import LLMIntentRouter, LLMIntentConfig

class IntentRouter(BaseAgent):
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None, config=None):
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.config = config or {}
        
        # Initialize LLM Intent Router (NEW)
        llm_config = LLMIntentConfig(
            enabled=self.config.get('llm_intent_enabled', False),
            provider=self.config.get('llm_provider', 'openai'),
            model=self.config.get('llm_model', 'gpt-3.5-turbo'),
            fast_path_threshold=0.8,
            tier2_similarity_threshold=0.85
        )
        self.llm_router = LLMIntentRouter(
            config=llm_config,
            tier2_kg=tier2_kg,
            fallback_classifier=self
        )
        
        self.logger.info(f"Intent Router initialized with LLM: {llm_config.enabled}")
    
    def _classify_intent_with_rules(self, request: AgentRequest) -> IntentClassificationResult:
        """Enhanced classification with LLM support"""
        
        # Phase 1: Fast keyword pre-screening (< 10ms)
        fast_result = self._fast_keyword_classification(request)
        if fast_result.confidence >= 0.8:
            self.logger.debug(f"Fast path: {fast_result.intent} (confidence: {fast_result.confidence})")
            return fast_result
        
        # Phase 2: LLM classification (100-500ms)
        if self.llm_router.config.enabled:
            try:
                llm_result = self.llm_router.classify_intent(
                    request,
                    conversation_history=self._get_recent_history(request)
                )
                if llm_result.confidence >= 0.8:
                    self.logger.info(
                        f"LLM classification: {llm_result.intent} "
                        f"(confidence: {llm_result.confidence}, method: {llm_result.method})"
                    )
                    return llm_result.to_standard_result()
                else:
                    self.logger.info(f"LLM confidence too low ({llm_result.confidence}), using fallback")
            except Exception as e:
                self.logger.warning(f"LLM classification failed: {e}, falling back to regex")
        
        # Phase 3: Fallback to regex (< 10ms)
        return self._classify_intent_regex(request)
```

**Performance Targets:**
- Fast path hit rate: 40% (exact matches)
- Tier 2 cache hit rate: 40% (similar past requests)
- LLM calls: 20% of requests
- Accuracy: 70% → 95%+ (25% improvement)
- Latency p50: <50ms (fast path), p95: <500ms (LLM), p99: <1s

**Test Coverage:**
- Unit tests: 20+ for LLM router, 15+ for hybrid routing
- Integration tests: 10+ with mock LLM, 5+ with real LLM (CI optional)
- E2E tests: 50 real user requests with accuracy validation

---

## 🏗️ Architecture Design

### 1. Manifest Consolidation Architecture

**Problem:** 14 YAML files with 60% redundancy across orchestrators

**Solution:** 3-tier manifest architecture with inheritance

```yaml
# cortex-brain/manifests/core-manifest.yaml
orchestrators:
  planning_system_v3:
    version: "3.0"
    module: "src.orchestration_4_0.orchestrators.planning"
    class: "PlanningSystemV3"
    category: "core"
    dependencies:
      - "brain_tier2"
      - "agentic_ai_agents"
    phases:
      - discovery
      - complexity_analysis
      - plan_generation
      - validation
    
  tdd_orchestrator_v4:
    version: "4.0"
    module: "src.orchestration_4_0.orchestrators.tdd"
    class: "TDDOrchestratorV4"
    category: "core"
    dependencies:
      - "qa_orchestrator"
      - "brain_tier2"
    phases:
      - red
      - green
      - refactor
      - validate

# ... 14 more orchestrators
```

```yaml
# cortex-brain/manifests/config-manifest.yaml
defaults:
  timeout_seconds: 300
  max_retries: 3
  log_level: "INFO"
  cache_enabled: true

orchestrators:
  planning_system_v3:
    timeout_seconds: 600
    complexity_thresholds:
      low: 10
      medium: 30
      high: 50
  
  tdd_orchestrator_v4:
    test_frameworks:
      - pytest
      - unittest
    coverage_threshold: 85

# Environment-specific overrides
environments:
  development:
    log_level: "DEBUG"
    cache_enabled: false
  
  production:
    timeout_seconds: 600
    max_retries: 5
```

```yaml
# cortex-brain/manifests/integration-manifest.yaml
external_systems:
  azure_devops:
    enabled: true
    organization_url: "${AZURE_DEVOPS_ORG_URL}"
    pat_token: "${AZURE_DEVOPS_PAT}"
    api_version: "6.0"
    rate_limit: 200  # requests/minute
  
  github:
    enabled: true
    api_url: "https://api.github.com"
    token: "${GITHUB_TOKEN}"
    api_version: "2022-11-28"
    rate_limit: 5000  # requests/hour
  
  filesystem:
    enabled: true
    base_paths:
      - "d:/PROJECTS"
      - "c:/code"
    watch_enabled: true
```

**Benefits:**
- Single source of truth for orchestrator metadata
- Environment-specific overrides without duplication
- Easy addition of new orchestrators (5 lines vs 50)
- Validation at startup prevents runtime errors

### 2. Universal Adapter Interface

**Problem:** 6 different adapter interfaces with inconsistent patterns

**Solution:** Single UniversalAdapter interface with platform-specific implementations

```python
# src/orchestration_4_0/adapters/universal_adapter.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

class ResourceType(Enum):
    """Types of resources managed by adapters"""
    WORK_ITEM = "work_item"
    PIPELINE = "pipeline"
    REPOSITORY = "repository"
    FILE = "file"
    ISSUE = "issue"
    PR = "pull_request"

class UniversalAdapter(ABC):
    """
    Universal adapter interface for all external systems.
    
    Provides CRUD + Search operations with consistent error handling,
    caching, retry logic, and rate limiting.
    """
    
    @abstractmethod
    async def create(
        self,
        resource_type: ResourceType,
        data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new resource"""
        pass
    
    @abstractmethod
    async def read(
        self,
        resource_type: ResourceType,
        resource_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Read an existing resource"""
        pass
    
    @abstractmethod
    async def update(
        self,
        resource_type: ResourceType,
        resource_id: str,
        data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing resource"""
        pass
    
    @abstractmethod
    async def delete(
        self,
        resource_type: ResourceType,
        resource_id: str,
        **kwargs
    ) -> bool:
        """Delete a resource"""
        pass
    
    @abstractmethod
    async def search(
        self,
        resource_type: ResourceType,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for resources"""
        pass
    
    @abstractmethod
    async def list(
        self,
        resource_type: ResourceType,
        parent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List resources"""
        pass

# Factory with auto-detection
class AdapterFactory:
    """Factory for creating appropriate adapter based on context"""
    
    @staticmethod
    def create(adapter_type: str, config: Dict[str, Any]) -> UniversalAdapter:
        """Create adapter instance"""
        if adapter_type == "azure_devops":
            return AzureDevOpsAdapter(config)
        elif adapter_type == "github":
            return GitHubAdapter(config)
        elif adapter_type == "filesystem":
            return FileSystemAdapter(config)
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    @staticmethod
    def auto_detect() -> UniversalAdapter:
        """Auto-detect appropriate adapter from environment"""
        if os.getenv("AZURE_DEVOPS_PAT"):
            return AdapterFactory.create("azure_devops", {})
        elif os.getenv("GITHUB_TOKEN"):
            return AdapterFactory.create("github", {})
        else:
            return AdapterFactory.create("filesystem", {})
```

**Migration Example:**
```python
# OLD (inconsistent interfaces)
ado_client = AzureDevOpsClient(org_url, pat)
work_item = ado_client.get_work_item(item_id)

github_client = GitHubClient(token)
issue = github_client.fetch_issue(repo, issue_num)

file_ops = FileOperations()
content = file_ops.read_file(path)

# NEW (unified interface)
adapter = AdapterFactory.auto_detect()
work_item = await adapter.read(ResourceType.WORK_ITEM, item_id)
issue = await adapter.read(ResourceType.ISSUE, issue_id)
file_content = await adapter.read(ResourceType.FILE, file_path)
```

**Benefits:**
- Consistent error handling across platforms
- Easy mocking for tests (single interface)
- Middleware support (caching, retry, logging)
- Platform switching without code changes

### 3. Dependency Injection Auto-Discovery

**Problem:** 13+ locations with manual dependency wiring

**Solution:** DI container with decorator-based registration

```python
# src/orchestration_4_0/di/container.py

from typing import Type, Any, Dict, Callable
from enum import Enum

class ServiceLifetime(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class DIContainer:
    """
    Dependency injection container with auto-discovery.
    
    Features:
    - Constructor injection
    - Decorator-based registration
    - Lifecycle management (singleton/transient/scoped)
    - Circular dependency detection
    """
    
    def __init__(self):
        self._services: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lifetimes: Dict[Type, ServiceLifetime] = {}
    
    def register(
        self,
        service_type: Type,
        implementation: Callable,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ):
        """Register a service"""
        self._services[service_type] = implementation
        self._lifetimes[service_type] = lifetime
    
    def resolve(self, service_type: Type) -> Any:
        """Resolve a service instance"""
        if service_type not in self._services:
            raise ValueError(f"Service not registered: {service_type}")
        
        lifetime = self._lifetimes[service_type]
        
        # Singleton: return cached instance
        if lifetime == ServiceLifetime.SINGLETON:
            if service_type not in self._singletons:
                self._singletons[service_type] = self._create_instance(service_type)
            return self._singletons[service_type]
        
        # Transient: create new instance
        return self._create_instance(service_type)
    
    def _create_instance(self, service_type: Type) -> Any:
        """Create service instance with dependency resolution"""
        implementation = self._services[service_type]
        
        # Get constructor parameters
        import inspect
        sig = inspect.signature(implementation.__init__)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            # Resolve dependency
            param_type = param.annotation
            if param_type in self._services:
                params[param_name] = self.resolve(param_type)
        
        return implementation(**params)

# Decorators for registration
def service(
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    interface: Type = None
):
    """Decorator to register a service"""
    def decorator(cls):
        service_type = interface or cls
        container.register(service_type, cls, lifetime)
        return cls
    return decorator

def inject(*dependencies: Type):
    """Decorator to inject dependencies into methods"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            resolved_deps = [container.resolve(dep) for dep in dependencies]
            return func(*args, *resolved_deps, **kwargs)
        return wrapper
    return decorator

# Global container instance
container = DIContainer()
```

**Usage Example:**
```python
# Register services with decorators
from src.orchestration_4_0.di import service, inject, ServiceLifetime
from src.brain.tier2.knowledge_graph import KnowledgeGraph
from src.orchestration_4_0.orchestrators.cicd import BrainIntegrator

@service(lifetime=ServiceLifetime.SINGLETON)
class KnowledgeGraph:
    def __init__(self, db_path: str):
        self.db_path = db_path

@service(lifetime=ServiceLifetime.TRANSIENT, interface=BrainIntegrator)
class BrainIntegratorImpl:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

# Orchestrator with auto-injection
@service(lifetime=ServiceLifetime.TRANSIENT)
class CICDSelfHealingOrchestrator(BaseOrchestrator):
    def __init__(
        self,
        name: str,
        devops_orchestrator: DevOpsOrchestrator,
        brain_integrator: BrainIntegrator,  # Auto-injected
        logger: logging.Logger = None
    ):
        super().__init__(name, logger)
        self.devops = devops_orchestrator
        self.brain = brain_integrator  # Automatically resolved

# Resolve orchestrator (all dependencies auto-wired)
orchestrator = container.resolve(CICDSelfHealingOrchestrator)
```

**Benefits:**
- Zero manual wiring in orchestrator __init__
- Easy testing (mock dependencies in container)
- Lifecycle control (prevent memory leaks)
- Circular dependency detection

---

## 📦 Deliverables

### Code Deliverables

1. **Manifest System** (Week 15)
   - `cortex-brain/manifests/core-manifest.yaml` (orchestrator registry)
   - `cortex-brain/manifests/config-manifest.yaml` (configuration)
   - `cortex-brain/manifests/integration-manifest.yaml` (external systems)
   - `src/orchestration_4_0/manifests/loader.py` (manifest loading)
   - `src/orchestration_4_0/manifests/validator.py` (validation)
   - 20 tests

2. **Universal Adapters** (Week 16)
   - `src/orchestration_4_0/adapters/universal_adapter.py` (interface)
   - `src/orchestration_4_0/adapters/azure_devops_adapter.py`
   - `src/orchestration_4_0/adapters/github_adapter.py`
   - `src/orchestration_4_0/adapters/filesystem_adapter.py`
   - `src/orchestration_4_0/adapters/adapter_factory.py`
   - `src/orchestration_4_0/adapters/middleware.py` (caching, retry)
   - 30 tests

3. **DI Container** (Week 17)
   - `src/orchestration_4_0/di/container.py` (core container)
   - `src/orchestration_4_0/di/decorators.py` (@service, @inject)
   - `src/orchestration_4_0/di/lifecycle.py` (scope management)
   - Migration of 16 orchestrators
   - 25 tests

### Documentation Deliverables

1. **Migration Guides**
   - Manifest migration guide (from old to new format)
   - Adapter migration guide (platform-specific examples)
   - DI migration guide (manual to auto-wiring)

2. **Architecture Documentation**
   - Manifest architecture diagrams
   - Adapter pattern documentation
   - DI container architecture
   - Configuration management guide

3. **API Documentation**
   - Universal adapter API reference
   - DI container API reference
   - Manifest schema documentation

### Validation Deliverables

1. **Test Suites**
   - 20 manifest tests (loading, validation, inheritance)
   - 30 adapter tests (CRUD, error handling, middleware)
   - 25 DI tests (registration, resolution, lifecycle)
   - E2E orchestrator tests (all 16 orchestrators)

2. **Performance Reports**
   - Manifest loading benchmark
   - Adapter performance comparison
   - DI overhead measurement
   - Overall regression testing (<10% acceptable)

---

## 🧪 Testing Strategy

### Unit Tests (75 total)

**Manifest System (20 tests):**
- Manifest loading from YAML
- Validation of orchestrator metadata
- Configuration inheritance
- Environment-specific overrides
- Error handling for malformed YAML

**Universal Adapters (30 tests):**
- CRUD operations per adapter type
- Search/list functionality
- Error handling and retry logic
- Caching middleware
- Rate limiting middleware
- Adapter factory auto-detection

**DI Container (25 tests):**
- Service registration
- Dependency resolution
- Singleton vs transient lifecycle
- Circular dependency detection
- Constructor injection
- Decorator functionality

### Integration Tests (16 orchestrators)

**Per-Orchestrator Validation:**
- Orchestrator loads from manifest
- Dependencies auto-injected via DI
- Adapters work correctly
- Configuration applied correctly
- E2E workflow execution

### Performance Tests

**Benchmarks:**
- Manifest loading time (<100ms)
- Adapter operation latency (<50ms overhead)
- DI resolution time (<10ms per orchestrator)
- Overall regression (<10%)

---

## 📊 Success Criteria

### Phase Complete When:

1. ✅ **Manifest Consolidation**
   - 14 YAML files reduced to 3
   - 70% reduction in total manifest size
   - All 16 orchestrators migrated
   - 20/20 manifest tests passing

2. ✅ **Universal Adapters**
   - Single adapter interface implemented
   - 3 platform adapters working (Azure DevOps, GitHub, FileSystem)
   - Middleware support (caching, retry, rate limiting)
   - 30/30 adapter tests passing

3. ✅ **DI Auto-Discovery**
   - DI container operational
   - 16 orchestrators migrated (zero manual wiring)
   - Lifecycle management working
   - 25/25 DI tests passing

4. ✅ **Validation Complete**
   - All 16 orchestrators E2E tested
   - Performance regression <10%
   - Documentation complete
   - Migration guides available

---

## 🚨 Risks & Mitigation

### High Risk

**Risk:** Breaking changes in orchestrator interfaces during DI migration

**Mitigation:**
- Incremental migration (2-3 orchestrators per day)
- Backward compatibility layer during transition
- Comprehensive E2E tests per orchestrator
- Rollback plan (git tags at each milestone)

### Medium Risk

**Risk:** Performance regression from DI overhead

**Mitigation:**
- Singleton lifecycle for heavy services
- Lazy initialization where possible
- Performance benchmarking at each milestone
- Optimization if >10% regression detected

### Low Risk

**Risk:** Adapter interface doesn't cover all use cases

**Mitigation:**
- Design review with actual usage patterns
- Extension points in adapter interface
- Platform-specific methods as needed
- Iterative enhancement based on feedback

---

## 📈 Metrics & KPIs

### Development Metrics

| Metric | Measurement Method | Target |
|--------|-------------------|--------|
| Manifest Reduction | LOC count before/after | 70% reduction |
| Manual DI Locations | Grep for manual wiring | 0 locations |
| Test Coverage | pytest --cov | 85%+ |
| Test Pass Rate | pytest results | 100% |

### Operational Metrics

| Metric | Measurement Method | Target |
|--------|-------------------|--------|
| Orchestrator Load Time | Timing in startup | <100ms |
| Adapter Overhead | Timing per operation | <50ms |
| DI Resolution Time | Timing per resolve | <10ms |
| Overall Performance | E2E orchestrator timing | <10% regression |

### Quality Metrics

| Metric | Measurement Method | Target |
|--------|-------------------|--------|
| Code Duplication | SonarQube/pylint | <5% |
| Cyclomatic Complexity | Radon/pylint | <10 avg |
| Documentation Coverage | Docstring analysis | 90%+ |

---

## 🎯 Next Steps

**Immediate Actions:**
1. Create Week 15 task list (manifest consolidation)
2. Design 3-tier manifest schema
3. Set up test fixtures for 16 orchestrators
4. Begin manifest audit (redundancy analysis)

**Phase 8 Preparation:**
- Identify testing gaps across all orchestrators
- Design comprehensive validation framework
- Plan performance benchmarking suite

---

## 📚 References

- [Phase 6: Orchestrator Consolidation](./phase-06-orchestrator-consolidation.md)
- [Phase 8: Testing & Validation](./phase-08-testing-validation.md)
- [Master Plan](../00-MASTER-PLAN.md)
- [Dependency Injection Patterns](https://en.wikipedia.org/wiki/Dependency_injection)
- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter)

---

**Last Updated:** December 22, 2025
**Status:** ⏳ READY TO START (Phase 6 complete)
**Next Milestone:** Week 15 Day 1 - Manifest consolidation kickoff
