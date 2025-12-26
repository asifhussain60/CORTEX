# Task 7.7: DI Container Implementation Plan

**Phase:** 7B - Operations Simplification (Architectural Implementation)  
**Author:** Asif Hussain  
**Created:** December 23, 2025  
**Status:** 🎯 READY TO START  
**Duration:** 3-4 days  
**Complexity:** HIGH

---

## 🎯 Objective

Implement Dependency Injection Container with auto-discovery and migrate 16 orchestrators to use constructor injection pattern, eliminating manual dependency wiring.

**Success Criteria:**
- ✅ DI Container with auto-discovery, lifecycle management, scopes
- ✅ 16 orchestrators migrated with backward compatibility
- ✅ 100% test coverage (30+ unit tests, 10+ integration tests)
- ✅ Performance targets met (<50ms startup, <10MB memory)
- ✅ Complete documentation (API reference + migration guide)

---

## 📊 Current Architecture Analysis

### Existing Orchestrator Patterns

**Pattern 1: Manual Dependencies (Legacy)**
```python
# src/orchestrators/base/base_orchestrator.py
class BaseOrchestrator(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.brain = BrainInterface(workspace_root, brain_config)
        self.template_manager = None  # Manually managed
        self.safety_guardrail = SafetyGuardrail(adaptive_config)
```

**Pattern 2: Partial Injection (4.0 Style)**
```python
# src/orchestration_4_0/base/base_orchestrator.py
class BaseOrchestrator(ABC):
    def __init__(
        self,
        name: str,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.logger = logger or logging.getLogger(f"cortex.orchestration.{name}")
        self.phase_manager = PhaseManager(orchestrator_name=name)
        self.error_handler = ErrorHandler(orchestrator_name=name)
```

### 16 Orchestrators to Migrate

**CRITICAL Priority (Package 1):**
1. `ExecutionOrchestrator` - Core execution engine
2. `BaseOrchestrator` (both versions) - Foundation class
3. `TDDOrchestrator` - Test-driven development
4. `PlanningOrchestrator` - Planning System

**HIGH Priority (Package 2):**
5. `DocumentationOrchestrator` - Self-documentation
6. `DevOpsOrchestrator` - CI/CD integration
7. `ADOOrchestrator` - Azure DevOps planning
8. `SanitizationOrchestrator` - Code sanitization

**MEDIUM Priority (Package 3):**
9. `SystemMaintenanceOrchestrator` - System health
10. `CICDSelfHealingOrchestrator` - Auto-repair
11. `BrainIntegrationOrchestrator` - Brain sync
12. `MultiAgentOrchestrator` - Agent coordination

**LOW Priority (Package 4):**
13. `AgentLearningEngine` - Pattern learning
14. `ExecutionModeManager` - Mode switching
15. `ContextValidator` - Context validation
16. `PhaseLifecycleManager` - Phase tracking

### Common Dependencies

**Every orchestrator needs:**
- Logger (logging.Logger)
- Configuration (Dict or ConfigManager)
- Brain Interface (BrainInterface)
- Template Manager (TemplateManager)
- Manifest Loader (ManifestLoader) - NEW from Task 7.5

**Execution orchestrators need:**
- Phase Manager (PhaseManager)
- Error Handler (ErrorHandler)
- Safety Guardrail (SafetyGuardrail)
- Checkpoint Manager (CheckpointManager)

**Planning orchestrators need:**
- Plan Validator (PlanValidator)
- Markdown Renderer (MarkdownRenderer)
- Complexity Analyzer (ComplexityAnalyzer)
- TDD Requirements Generator (TDDRequirementsGenerator)

**DevOps orchestrators need:**
- Platform Client (AzureDevOpsClient, GitHubActionsClient)
- Failure Analyzer (FailureAnalyzer)
- Auto-Fix Engine (AutoFixEngine)

---

## 🏗️ Implementation Phases

### Phase 1: DI Container Core (Day 1, 6-8 hours)

**1.1: Service Container Class**
```python
# src/di/service_container.py

from typing import Any, Callable, Dict, Type, Optional, Union
from enum import Enum
from dataclasses import dataclass
import inspect

class ServiceScope(Enum):
    """Service lifecycle scope."""
    SINGLETON = "singleton"  # One instance for entire app
    TRANSIENT = "transient"  # New instance per resolution
    SCOPED = "scoped"         # One instance per request/context

@dataclass
class ServiceRegistration:
    """Service registration metadata."""
    service_type: Type
    implementation: Union[Type, Callable]
    scope: ServiceScope
    dependencies: List[str]
    singleton_instance: Optional[Any] = None

class ServiceContainer:
    """
    Dependency Injection Container.
    
    Features:
    - Auto-wiring via constructor inspection
    - Lifecycle management (singleton, transient, scoped)
    - Circular dependency detection
    - Lazy resolution
    """
    
    def __init__(self):
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._resolving: Set[str] = set()  # Track circular deps
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        
    def register(
        self,
        service_type: Type,
        implementation: Optional[Union[Type, Callable]] = None,
        scope: ServiceScope = ServiceScope.TRANSIENT
    ) -> None:
        """Register service with container."""
        impl = implementation or service_type
        key = self._get_service_key(service_type)
        
        # Extract dependencies from constructor
        dependencies = self._extract_dependencies(impl)
        
        self._registrations[key] = ServiceRegistration(
            service_type=service_type,
            implementation=impl,
            scope=scope,
            dependencies=dependencies
        )
    
    def resolve(self, service_type: Type, scope_id: Optional[str] = None) -> Any:
        """Resolve service instance."""
        key = self._get_service_key(service_type)
        
        if key not in self._registrations:
            raise KeyError(f"Service not registered: {service_type.__name__}")
        
        # Circular dependency check
        if key in self._resolving:
            raise RuntimeError(f"Circular dependency detected: {key}")
        
        registration = self._registrations[key]
        
        # Return singleton instance
        if registration.scope == ServiceScope.SINGLETON:
            if registration.singleton_instance is None:
                registration.singleton_instance = self._create_instance(registration)
            return registration.singleton_instance
        
        # Return scoped instance
        if registration.scope == ServiceScope.SCOPED and scope_id:
            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}
            if key not in self._scoped_instances[scope_id]:
                self._scoped_instances[scope_id][key] = self._create_instance(registration)
            return self._scoped_instances[scope_id][key]
        
        # Create transient instance
        return self._create_instance(registration)
    
    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create instance with auto-wiring."""
        key = self._get_service_key(registration.service_type)
        self._resolving.add(key)
        
        try:
            # Resolve dependencies
            resolved_deps = {}
            for dep_name, dep_type in registration.dependencies.items():
                resolved_deps[dep_name] = self.resolve(dep_type)
            
            # Create instance
            return registration.implementation(**resolved_deps)
        
        finally:
            self._resolving.discard(key)
    
    def _extract_dependencies(self, cls: Type) -> Dict[str, Type]:
        """Extract constructor dependencies via inspection."""
        sig = inspect.signature(cls.__init__)
        dependencies = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get type annotation
            if param.annotation != inspect.Parameter.empty:
                dependencies[param_name] = param.annotation
        
        return dependencies
    
    def _get_service_key(self, service_type: Type) -> str:
        """Generate unique key for service type."""
        return f"{service_type.__module__}.{service_type.__name__}"
```

**1.2: Tests (RED Phase)**
```python
# tests/di/test_service_container.py

class TestServiceContainer:
    """Test DI Container core functionality."""
    
    def test_register_and_resolve_transient(self):
        """Test transient scope creates new instance each time."""
    
    def test_register_and_resolve_singleton(self):
        """Test singleton scope returns same instance."""
    
    def test_register_and_resolve_scoped(self):
        """Test scoped instance lifetime."""
    
    def test_auto_wire_dependencies(self):
        """Test automatic dependency resolution."""
    
    def test_circular_dependency_detection(self):
        """Test circular dependency raises error."""
    
    def test_missing_dependency_error(self):
        """Test missing dependency raises KeyError."""
    
    def test_resolve_unregistered_service(self):
        """Test resolving unregistered service raises error."""
    
    def test_clear_scoped_instances(self):
        """Test scope cleanup."""
```

---

### Phase 2: Auto-Discovery System (Day 1-2, 4-6 hours)

**2.1: Module Scanner**
```python
# src/di/auto_discovery.py

import ast
import importlib
from pathlib import Path
from typing import Dict, List, Type

class ModuleScanner:
    """
    Auto-discover orchestrators and register with container.
    
    Features:
    - AST-based scanning (no imports)
    - Manifest validation
    - Dependency graph construction
    - Caching for performance
    """
    
    def __init__(self, container: ServiceContainer, cortex_root: Path):
        self.container = container
        self.cortex_root = cortex_root
        self.cache_file = cortex_root / ".cortex-brain/cache/di-discovery.json"
    
    def discover_and_register(
        self,
        scan_paths: List[Path],
        force_refresh: bool = False
    ) -> Dict[str, Type]:
        """
        Discover orchestrators and register with container.
        
        Returns:
            Dict mapping orchestrator names to classes
        """
        if not force_refresh and self._load_cache():
            return self._import_from_cache()
        
        discovered = {}
        
        for scan_path in scan_paths:
            for py_file in scan_path.rglob("*_orchestrator.py"):
                orchestrators = self._scan_file(py_file)
                discovered.update(orchestrators)
        
        # Register with container
        for name, orch_class in discovered.items():
            self._register_orchestrator(orch_class)
        
        # Save cache
        self._save_cache(discovered)
        
        return discovered
    
    def _scan_file(self, file_path: Path) -> Dict[str, Type]:
        """Scan file for orchestrator classes."""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        orchestrators = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseOrchestrator
                if self._inherits_base_orchestrator(node):
                    # Import class
                    module_path = self._file_to_module_path(file_path)
                    module = importlib.import_module(module_path)
                    orch_class = getattr(module, node.name)
                    
                    orchestrators[node.name] = orch_class
        
        return orchestrators
    
    def _register_orchestrator(self, orch_class: Type) -> None:
        """Register orchestrator with appropriate dependencies."""
        # Determine scope based on class attributes
        scope = ServiceScope.SINGLETON  # Most orchestrators are singletons
        
        # Register with container
        self.container.register(
            service_type=orch_class,
            scope=scope
        )
    
    def _inherits_base_orchestrator(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from BaseOrchestrator."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseOrchestrator":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "BaseOrchestrator":
                return True
        return False
```

**2.2: Manifest Integration**
```python
# src/di/manifest_provider.py

from src.utils.manifest_loader import ManifestLoader

class ManifestProvider:
    """
    Provide manifest-based configuration to DI container.
    
    Integrates with Task 7.5 ManifestLoader.
    """
    
    def __init__(self, container: ServiceContainer, cortex_root: str):
        self.container = container
        self.manifest_loader = ManifestLoader(cortex_root)
    
    def register_from_manifests(self) -> None:
        """Register services from manifest files."""
        # Load core manifest
        core_manifest = self.manifest_loader.load_manifest("core")
        
        for orchestrator_id, metadata in core_manifest["orchestrators"].items():
            # Register orchestrator with metadata
            self._register_with_metadata(orchestrator_id, metadata)
    
    def _register_with_metadata(self, orchestrator_id: str, metadata: Dict) -> None:
        """Register orchestrator with manifest metadata."""
        # Metadata used for validation, not instantiation
        pass
```

---

### Phase 3: Orchestrator Migration (Day 2-3, 8-10 hours)

**3.1: Package 1 - Critical Orchestrators**

**Migration Template:**
```python
# BEFORE (Manual Dependencies)
class ExecutionOrchestrator:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.logger = logger or logging.getLogger("cortex.execution")
        self.config = config or {}
        self.phase_manager = PhaseManager(orchestrator_name="execution")
        self.error_handler = ErrorHandler(orchestrator_name="execution")

# AFTER (DI Container)
from src.di.decorators import orchestrator
from src.di.container import Provide, CortexContainer

@orchestrator
class ExecutionOrchestrator:
    def __init__(
        self,
        logger: logging.Logger = Provide[CortexContainer.logger],
        config: Dict[str, Any] = Provide[CortexContainer.config],
        phase_manager: PhaseManager = Provide[CortexContainer.phase_manager],
        error_handler: ErrorHandler = Provide[CortexContainer.error_handler],
        brain_interface: BrainInterface = Provide[CortexContainer.brain_interface],
        template_manager: TemplateManager = Provide[CortexContainer.template_manager]
    ):
        self.logger = logger
        self.config = config
        self.phase_manager = phase_manager
        self.error_handler = error_handler
        self.brain = brain_interface
        self.templates = template_manager
```

**Backward Compatibility Layer:**
```python
# src/di/compatibility.py

def create_orchestrator_legacy(
    orchestrator_class: Type,
    logger: Optional[logging.Logger] = None,
    config: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Create orchestrator using legacy pattern.
    
    Bridges old code to new DI system without breaking changes.
    """
    # Use container internally but expose legacy API
    container = get_global_container()
    
    # Override default dependencies if provided
    if logger:
        container.register_instance(logging.Logger, logger)
    if config:
        container.register_instance(dict, config)
    
    return container.resolve(orchestrator_class)
```

**3.2: Migration Checklist (Per Orchestrator)**

- [ ] Add `@orchestrator` decorator
- [ ] Convert constructor to use `Provide[]` pattern
- [ ] Update all internal instantiations to use DI
- [ ] Add tests for DI resolution
- [ ] Test backward compatibility
- [ ] Update documentation
- [ ] Run full test suite
- [ ] Performance benchmark

---

### Phase 4: Testing & Validation (Day 3, 4-6 hours)

**4.1: Unit Tests**
- Service container (registration, resolution, scopes)
- Auto-discovery (scanning, caching, manifest integration)
- Circular dependency detection
- Missing dependency handling
- Scope cleanup

**4.2: Integration Tests**
- Orchestrator creation through container
- Cross-orchestrator dependencies
- Manifest-based configuration
- Adapter resolution (from Task 7.6)
- Performance benchmarks

**4.3: Backward Compatibility Tests**
- Legacy instantiation patterns
- Mixed DI/legacy usage
- Configuration overrides

---

### Phase 5: Documentation & Completion (Day 4, 4-6 hours)

**5.1: API Reference**
- ServiceContainer API
- ServiceScope enum
- @orchestrator decorator
- Provide[] pattern
- Auto-discovery API

**5.2: Migration Guide**
- Step-by-step migration instructions
- Before/after examples
- Common pitfalls
- Troubleshooting

**5.3: Completion Report**
- Implementation summary
- Test metrics (coverage, pass rate)
- Performance benchmarks
- Migration status (16/16 orchestrators)
- Known limitations
- Future enhancements

---

## 📈 Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Container startup | <50ms | <100ms |
| Auto-discovery | <200ms | <500ms |
| Service resolution | <1ms | <5ms |
| Memory overhead | <10MB | <20MB |
| Cache hit rate | >90% | >75% |

---

## 🚨 Risk Mitigation

**Risk 1: Breaking Changes**
- **Mitigation:** Backward compatibility layer
- **Test:** Legacy instantiation tests

**Risk 2: Circular Dependencies**
- **Mitigation:** Detection + clear error messages
- **Test:** Circular dependency test cases

**Risk 3: Performance Degradation**
- **Mitigation:** Caching, lazy resolution
- **Test:** Benchmark suite

**Risk 4: Complex Orchestrator Dependencies**
- **Mitigation:** Phased migration (4 packages)
- **Test:** Integration tests per package

---

## 📦 Deliverables

1. ✅ `src/di/service_container.py` - Core DI container
2. ✅ `src/di/auto_discovery.py` - Auto-discovery system
3. ✅ `src/di/manifest_provider.py` - Manifest integration
4. ✅ `src/di/decorators.py` - @orchestrator decorator
5. ✅ `src/di/compatibility.py` - Backward compatibility
6. ✅ `tests/di/` - 30+ unit tests
7. ✅ `tests/integration/test_di_orchestrators.py` - 10+ integration tests
8. ✅ 16 migrated orchestrators
9. ✅ `cortex-brain/documents/implementation-guides/di-container-api-reference.md`
10. ✅ `cortex-brain/documents/implementation-guides/di-migration-guide.md`
11. ✅ `cortex-brain/documents/reports/task-7.7-completion-report.md`

---

## 🔄 Next Steps After Task 7.7

**Task 7.8:** Refactor operation registry to use manifest cross-references (2-3 days)  
**Task 7.9:** Simplify CLI wrappers using ManifestLoader (2 days)  
**Phase 8:** Testing & Validation (3 weeks)

---

**Ready to begin:** Task 7.7 Phase 1 - DI Container Core implementation
