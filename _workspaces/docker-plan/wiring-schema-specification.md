# CORTEX Git-Backed Wiring System
## Single Path, Zero Drift Architecture

**Document:** wiring-schema-specification.md  
**Date:** 2026-01-27  

---

## 🎯 Design Goals

1. **SINGLE wiring path** - No alternatives, no fallbacks
2. **Git-backed SSOT** - All wiring in version-controlled YAML
3. **Zero database files** - No .db, no state corruption
4. **Deterministic order** - Same wiring across all deployments
5. **Lazy initialization** - Wire on first use, not at startup
6. **Container-safe** - Wiring happens ONCE at container start

---

## 📁 Directory Structure

```
cortex/wiring/
├── __init__.py
├── bootstrap.py                    # SINGLE entry point
│
├── specifications/                 # YAML-based SSOT (Git-tracked)
│   ├── core-wiring.yaml           # 6 core orchestrators
│   ├── domain-wiring.yaml         # 6 domain orchestrators
│   └── support-wiring.yaml        # 11 support orchestrators
│
└── registry/
    ├── __init__.py
    ├── git_backed_registry.py     # Load from YAML
    ├── lazy_orchestrator.py       # Wire on first access
    └── wiring_validator.py        # Validate wiring integrity
```

---

## 📋 Wiring Specification Format

### core-wiring.yaml

```yaml
# CORTEX Core Orchestrator Wiring Specification
# Authority: CORE-035 (Single Canonical Implementation)
# 
# This file is the SINGLE SOURCE OF TRUTH for core orchestrator wiring.
# Changes to this file require review and approval.
#
# Git-safe: Commitable, mergeable, reviewable
# Deterministic: Same order across all environments

version: "2.0"
specification_date: "2026-01-27"
git_safe: true

orchestrators:
  # STAGE 1: Comprehension (LENS Protocol)
  - name: "InteractionOrchestrator"
    module: "cortex.orchestrators.core.interaction_orchestrator"
    class: "InteractionOrchestrator"
    category: "CORE"
    tier: 1
    priority: 10
    dependencies: []
    requires_params:
      conversation_protocol:
        type: "ConversationProtocol"
        source: "cortex.brain.core.conversation_protocol"
        lazy_create: true
    capabilities:
      - comprehension
      - lens_protocol
      - challenge_generation
      - pattern_enforcement
    health_check: "execute_turn"
    mcp_adapter: "cortex.mcp.adapters.interaction_adapter"

  # STAGE 2: Intent Classification
  - name: "IntentRouter"
    module: "cortex.orchestrators.core.intent_router"
    class: "IntentRouter"
    category: "CORE"
    tier: 1
    priority: 20
    dependencies:
      - "InteractionOrchestrator"
    requires_params: {}
    capabilities:
      - intent_classification
      - confidence_scoring
      - domain_routing
      - fuzzy_matching
    health_check: "classify_intent"
    mcp_adapter: "cortex.mcp.adapters.intent_router_adapter"

  # STAGE 2.5: DoR Approval Gate
  - name: "LENSSynthesis"
    module: "cortex.orchestrators.core.lens_synthesis"
    class: "LENSSynthesis"
    category: "CORE"
    tier: 1
    priority: 25
    dependencies:
      - "IntentRouter"
    requires_params: {}
    capabilities:
      - dor_generation
      - approval_gate
      - synthesis
    health_check: "synthesize"
    mcp_adapter: "cortex.mcp.adapters.lens_adapter"

  # STAGE 3: TDD Execution
  - name: "TDDOrchestrator"
    module: "cortex.orchestrators.core.tdd_orchestrator"
    class: "TDDOrchestrator"
    category: "CORE"
    tier: 1
    priority: 30
    dependencies:
      - "InteractionOrchestrator"
      - "IntentRouter"
    requires_params: {}
    capabilities:
      - test_generation
      - tdd_workflow
      - test_execution
    health_check: "generate_tests"
    mcp_adapter: "cortex.mcp.adapters.tdd_adapter"

  # STAGE 4: Master Coordination
  - name: "MasterOrchestrator"
    module: "cortex.orchestrators.core.master_orchestrator"
    class: "MasterOrchestrator"
    category: "CORE"
    tier: 1
    priority: 100
    dependencies:
      - "InteractionOrchestrator"
      - "IntentRouter"
      - "LENSSynthesis"
      - "TDDOrchestrator"
    requires_params:
      orchestrators:
        type: "Dict[str, LazyOrchestrator]"
        source: "wiring_registry"
        inject_all: true
    capabilities:
      - coordination
      - stage_management
      - orchestrator_routing
    health_check: "coordinate_operation"
    mcp_adapter: "cortex.mcp.adapters.master_adapter"

  # Challenge Engine
  - name: "ChallengeEngine"
    module: "cortex.orchestrators.core.challenge_engine"
    class: "ChallengeEngine"
    category: "CORE"
    tier: 1
    priority: 15
    dependencies:
      - "InteractionOrchestrator"
    requires_params: {}
    capabilities:
      - challenge_generation
      - disagreement_detection
      - alternative_suggestion
    health_check: "generate_challenge"
    mcp_adapter: "cortex.mcp.adapters.challenge_adapter"

# Dependency DAG validation
dependency_rules:
  max_depth: 5
  allow_circular: false
  require_all_deps_exist: true

# Health check configuration
health_check_config:
  timeout_seconds: 5
  retry_count: 3
  fail_fast: true
```

### domain-wiring.yaml

```yaml
# CORTEX Domain Orchestrator Wiring Specification
version: "2.0"
specification_date: "2026-01-27"

orchestrators:
  - name: "RefactoringOrchestrator"
    module: "cortex.orchestrators.domain.refactoring_orchestrator"
    class: "RefactoringOrchestrator"
    category: "DOMAIN"
    tier: 2
    priority: 200
    dependencies:
      - "MasterOrchestrator"
      - "TDDOrchestrator"
    capabilities:
      - code_refactoring
      - solid_analysis
      - pattern_detection
    health_check: "analyze_refactoring"
    mcp_adapter: "cortex.mcp.adapters.refactoring_adapter"

  - name: "PlanningOrchestrator"
    module: "cortex.orchestrators.domain.planning_orchestrator"
    class: "PlanningOrchestrator"
    category: "DOMAIN"
    tier: 2
    priority: 210
    dependencies:
      - "MasterOrchestrator"
    capabilities:
      - plan_generation
      - phase_management
      - roadmap_creation
    health_check: "generate_plan"
    mcp_adapter: "cortex.mcp.adapters.planning_adapter"

  - name: "DocumentationOrchestrator"
    module: "cortex.orchestrators.domain.documentation_orchestrator"
    class: "DocumentationOrchestrator"
    category: "DOMAIN"
    tier: 2
    priority: 220
    dependencies:
      - "MasterOrchestrator"
    capabilities:
      - doc_generation
      - api_documentation
      - readme_creation
    health_check: "generate_documentation"
    mcp_adapter: "cortex.mcp.adapters.documentation_adapter"

  # ... remaining domain orchestrators
```

### support-wiring.yaml

```yaml
# CORTEX Support Orchestrator Wiring Specification
version: "2.0"
specification_date: "2026-01-27"

orchestrators:
  - name: "OnboardingOrchestrator"
    module: "cortex.orchestrators.core.onboarding_orchestrator"
    class: "OnboardingOrchestrator"
    category: "SUPPORT"
    tier: 3
    priority: 300
    dependencies:
      - "MasterOrchestrator"
    capabilities:
      - user_onboarding
      - project_setup
      - environment_configuration
    health_check: "onboard_user"
    mcp_adapter: "cortex.mcp.adapters.onboarding_adapter"

  - name: "ToolDiscoveryOrchestrator"
    module: "cortex.orchestrators.core.tool_discovery_orchestrator"
    class: "ToolDiscoveryOrchestrator"
    category: "SUPPORT"
    tier: 3
    priority: 310
    dependencies:
      - "MasterOrchestrator"
    capabilities:
      - tool_discovery
      - capability_mapping
      - feature_recall
    health_check: "discover_tools"
    mcp_adapter: "cortex.mcp.adapters.tool_discovery_adapter"

  # ... remaining 9 support orchestrators
```

---

## 🔧 Implementation

### bootstrap.py (Single Entry Point)

```python
"""
CORTEX Wiring Bootstrap - SINGLE ENTRY POINT

This is the ONLY way to initialize CORTEX wiring.
Any other initialization path is a CORE-035 violation.

Usage:
    from cortex.wiring import bootstrap_cortex
    cortex = bootstrap_cortex()
    
NOT ALLOWED:
    from cortex.orchestrators.core.database_registry import DatabaseBackedRegistry
    from cortex.orchestrators.bootstrap import OrchestratorBootstrap
"""

import logging
from pathlib import Path
from typing import Optional

from .registry.git_backed_registry import GitBackedRegistry
from .registry.wiring_validator import WiringValidator

logger = logging.getLogger(__name__)

_CORTEX_INSTANCE: Optional['CORTEXRuntime'] = None
_WIRING_COMPLETE: bool = False


class CORTEXRuntime:
    """
    CORTEX Runtime - Initialized once via bootstrap_cortex().
    
    Holds wired orchestrators and provides access to MCP tools.
    """
    
    def __init__(self, registry: GitBackedRegistry):
        self.registry = registry
        self.master = registry.get_master_orchestrator()
        self._wiring_hash = registry.compute_wiring_hash()
    
    def execute(self, operation: str, **kwargs):
        """Execute operation through MasterOrchestrator."""
        return self.master.coordinate_operation(operation, **kwargs)
    
    def get_orchestrator(self, name: str):
        """Get orchestrator by name (lazy wiring)."""
        return self.registry.get_orchestrator(name)
    
    @property
    def wiring_hash(self) -> str:
        """Get deterministic wiring hash for verification."""
        return self._wiring_hash


def bootstrap_cortex() -> CORTEXRuntime:
    """
    Bootstrap CORTEX with git-backed wiring.
    
    This is the SINGLE entry point for CORTEX initialization.
    
    Returns:
        CORTEXRuntime: Fully wired CORTEX instance
    
    Raises:
        WiringValidationError: If wiring specs invalid
    """
    global _CORTEX_INSTANCE, _WIRING_COMPLETE
    
    # Return existing instance if already wired
    if _WIRING_COMPLETE and _CORTEX_INSTANCE is not None:
        logger.info("Returning existing CORTEX instance")
        return _CORTEX_INSTANCE
    
    logger.info("=" * 60)
    logger.info("CORTEX Bootstrap: Git-Backed Wiring")
    logger.info("=" * 60)
    
    # Step 1: Load git-backed specifications
    specs_dir = Path(__file__).parent / "specifications"
    logger.info(f"Loading wiring specifications from: {specs_dir}")
    
    registry = GitBackedRegistry(specs_dir)
    
    # Step 2: Validate wiring specifications
    logger.info("Validating wiring specifications...")
    validator = WiringValidator(registry)
    validation_result = validator.validate_all()
    
    if not validation_result.success:
        logger.error(f"Wiring validation failed: {validation_result.errors}")
        raise WiringValidationError(validation_result.errors)
    
    logger.info(f"✅ Wiring validation passed: {validation_result.orchestrator_count} orchestrators")
    
    # Step 3: Create runtime
    _CORTEX_INSTANCE = CORTEXRuntime(registry)
    _WIRING_COMPLETE = True
    
    logger.info(f"✅ CORTEX wired successfully")
    logger.info(f"   Wiring hash: {_CORTEX_INSTANCE.wiring_hash}")
    logger.info("=" * 60)
    
    return _CORTEX_INSTANCE


def get_cortex() -> CORTEXRuntime:
    """
    Get the CORTEX runtime instance.
    
    If not yet bootstrapped, calls bootstrap_cortex() automatically.
    """
    global _CORTEX_INSTANCE
    
    if _CORTEX_INSTANCE is None:
        return bootstrap_cortex()
    
    return _CORTEX_INSTANCE


def is_wired() -> bool:
    """Check if CORTEX is wired."""
    return _WIRING_COMPLETE


def get_wiring_hash() -> str:
    """Get the current wiring hash."""
    if _CORTEX_INSTANCE is None:
        raise RuntimeError("CORTEX not yet bootstrapped")
    return _CORTEX_INSTANCE.wiring_hash


class WiringValidationError(Exception):
    """Raised when wiring validation fails."""
    pass
```

### git_backed_registry.py

```python
"""
Git-Backed Orchestrator Registry

Loads all wiring from YAML specifications.
No database. Pure git-backed SSOT.

Key Properties:
- Deterministic: Same wiring order across all environments
- Git-safe: All wiring in version control
- Team-safe: YAML merges are trivial
- Debuggable: Wiring visible in git diff
"""

import yaml
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .lazy_orchestrator import LazyOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorSpec:
    """Specification for a single orchestrator."""
    name: str
    module: str
    class_name: str
    category: str
    tier: int
    priority: int
    dependencies: List[str]
    requires_params: Dict[str, Any]
    capabilities: List[str]
    health_check: str
    mcp_adapter: str


class GitBackedRegistry:
    """
    Load orchestrator wiring from git-backed YAML specifications.
    
    NEVER creates .db files.
    NEVER stores state outside git.
    ALWAYS deterministic based on YAML content.
    """
    
    def __init__(self, specs_dir: Path):
        self.specs_dir = specs_dir
        self._specs: Dict[str, OrchestratorSpec] = {}
        self._wiring_order: List[str] = []
        self._lazy_orchestrators: Dict[str, LazyOrchestrator] = {}
        
        self._load_all_specs()
        self._compute_wiring_order()
        self._create_lazy_orchestrators()
    
    def _load_all_specs(self) -> None:
        """Load all YAML specifications from git-backed directory."""
        yaml_files = [
            "core-wiring.yaml",
            "domain-wiring.yaml", 
            "support-wiring.yaml"
        ]
        
        for yaml_file in yaml_files:
            yaml_path = self.specs_dir / yaml_file
            if not yaml_path.exists():
                logger.warning(f"Wiring spec not found: {yaml_path}")
                continue
            
            logger.info(f"Loading: {yaml_file}")
            with open(yaml_path) as f:
                spec_data = yaml.safe_load(f)
            
            for orch_def in spec_data.get("orchestrators", []):
                spec = OrchestratorSpec(
                    name=orch_def["name"],
                    module=orch_def["module"],
                    class_name=orch_def["class"],
                    category=orch_def["category"],
                    tier=orch_def["tier"],
                    priority=orch_def["priority"],
                    dependencies=orch_def.get("dependencies", []),
                    requires_params=orch_def.get("requires_params", {}),
                    capabilities=orch_def.get("capabilities", []),
                    health_check=orch_def.get("health_check", ""),
                    mcp_adapter=orch_def.get("mcp_adapter", "")
                )
                self._specs[spec.name] = spec
                logger.debug(f"  Loaded: {spec.name} (priority={spec.priority})")
        
        logger.info(f"Loaded {len(self._specs)} orchestrator specifications")
    
    def _compute_wiring_order(self) -> None:
        """Compute deterministic wiring order using topological sort."""
        # Kahn's algorithm for topological sort
        in_degree = {name: 0 for name in self._specs}
        
        for name, spec in self._specs.items():
            for dep in spec.dependencies:
                if dep in in_degree:
                    in_degree[name] += 1
        
        # Start with orchestrators that have no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        queue.sort(key=lambda n: self._specs[n].priority)  # Sort by priority
        
        result = []
        while queue:
            # Pick lowest priority (most important)
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree of dependents
            for name, spec in self._specs.items():
                if current in spec.dependencies:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
                        queue.sort(key=lambda n: self._specs[n].priority)
        
        if len(result) != len(self._specs):
            # Circular dependency detected
            remaining = set(self._specs.keys()) - set(result)
            raise ValueError(f"Circular dependencies detected: {remaining}")
        
        self._wiring_order = result
        logger.info(f"Wiring order: {self._wiring_order}")
    
    def _create_lazy_orchestrators(self) -> None:
        """Create lazy orchestrator wrappers for each spec."""
        for name in self._wiring_order:
            spec = self._specs[name]
            self._lazy_orchestrators[name] = LazyOrchestrator(spec, self)
        
        logger.info(f"Created {len(self._lazy_orchestrators)} lazy orchestrators")
    
    def get_orchestrator(self, name: str) -> LazyOrchestrator:
        """Get lazy orchestrator by name."""
        if name not in self._lazy_orchestrators:
            raise KeyError(f"Unknown orchestrator: {name}")
        return self._lazy_orchestrators[name]
    
    def get_master_orchestrator(self) -> LazyOrchestrator:
        """Get the MasterOrchestrator."""
        return self.get_orchestrator("MasterOrchestrator")
    
    def get_all_specs(self) -> Dict[str, OrchestratorSpec]:
        """Get all orchestrator specifications."""
        return self._specs.copy()
    
    def get_wiring_order(self) -> List[str]:
        """Get deterministic wiring order."""
        return self._wiring_order.copy()
    
    def compute_wiring_hash(self) -> str:
        """
        Compute deterministic hash of wiring configuration.
        
        Same YAML specs = same hash, regardless of environment.
        """
        content = ""
        for name in sorted(self._specs.keys()):
            spec = self._specs[name]
            content += f"{name}:{spec.module}:{spec.priority}:{sorted(spec.dependencies)}\n"
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
```

### lazy_orchestrator.py

```python
"""
Lazy Orchestrator - Wire on first access.

Benefits:
- No initialization deadlocks
- Parameters resolved at wire time
- Fast startup (only wire what's used)
"""

import threading
import importlib
import logging
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .git_backed_registry import GitBackedRegistry, OrchestratorSpec

logger = logging.getLogger(__name__)


class LazyOrchestrator:
    """
    Wrapper that wires orchestrator on first method access.
    
    Thread-safe: Uses lock for concurrent access.
    Lazy: Only wires when actually used.
    """
    
    def __init__(self, spec: 'OrchestratorSpec', registry: 'GitBackedRegistry'):
        self.spec = spec
        self.registry = registry
        self._instance: Optional[Any] = None
        self._lock = threading.Lock()
        self._wired = False
    
    def __getattr__(self, name: str) -> Any:
        """Wire on first attribute access."""
        # Skip special attributes
        if name.startswith('_'):
            raise AttributeError(name)
        
        # Wire if not yet wired
        if not self._wired:
            self._wire()
        
        return getattr(self._instance, name)
    
    def _wire(self) -> None:
        """Wire this orchestrator with parameter injection."""
        with self._lock:
            if self._wired:
                return
            
            logger.info(f"Wiring: {self.spec.name}")
            
            # Import module and class
            module = importlib.import_module(self.spec.module)
            OrchestratorClass = getattr(module, self.spec.class_name)
            
            # Resolve required parameters
            params = self._resolve_params()
            
            # Instantiate
            try:
                self._instance = OrchestratorClass(**params)
                self._wired = True
                logger.info(f"✅ Wired: {self.spec.name}")
            except Exception as e:
                logger.error(f"❌ Failed to wire {self.spec.name}: {e}")
                raise
    
    def _resolve_params(self) -> dict:
        """Resolve required parameters for orchestrator."""
        params = {}
        
        for param_name, param_def in self.spec.requires_params.items():
            if param_def.get("lazy_create"):
                # Create parameter on demand
                params[param_name] = self._create_param(param_def)
            elif param_def.get("inject_all"):
                # Inject all orchestrators (for MasterOrchestrator)
                params[param_name] = self.registry._lazy_orchestrators
            elif param_def.get("source"):
                # Get from another module
                params[param_name] = self._import_param(param_def["source"])
        
        return params
    
    def _create_param(self, param_def: dict) -> Any:
        """Create a parameter on demand."""
        param_type = param_def.get("type")
        source = param_def.get("source", "")
        
        if not source:
            return None
        
        try:
            module_path, class_name = source.rsplit(".", 1)
            module = importlib.import_module(module_path)
            ParamClass = getattr(module, class_name)
            return ParamClass()
        except Exception as e:
            logger.warning(f"Could not create param {param_type}: {e}")
            return None
    
    def _import_param(self, source: str) -> Any:
        """Import a parameter from a module."""
        try:
            module_path, attr_name = source.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, attr_name)
        except Exception as e:
            logger.warning(f"Could not import param from {source}: {e}")
            return None
    
    @property
    def is_wired(self) -> bool:
        """Check if orchestrator is wired."""
        return self._wired
    
    def force_wire(self) -> None:
        """Force wire this orchestrator."""
        self._wire()
```

---

## 🔒 Single Path Enforcement

The new architecture enforces a SINGLE wiring path:

```
ALLOWED:
  from cortex.wiring import bootstrap_cortex
  cortex = bootstrap_cortex()

NOT ALLOWED (will not exist in codebase):
  ❌ from cortex.orchestrators.core.database_registry import DatabaseBackedRegistry
  ❌ from cortex.orchestrators.bootstrap import OrchestratorBootstrap  
  ❌ from cortex.orchestrators.core.orchestrator_registry import OrchestratorRegistry
  ❌ from cortex.orchestrators.core.db_wiring_init import initialize_database_wiring
```

These files will NOT be migrated to the new branch.

---

## 📊 Wiring Guarantees

| Guarantee | How Enforced |
|-----------|--------------|
| **Single Path** | Only `bootstrap.py` exists |
| **No Database** | No SQLite code in codebase |
| **Deterministic** | Topological sort + priority |
| **Git-Backed** | YAML in version control |
| **Lazy Loading** | LazyOrchestrator pattern |
| **Thread-Safe** | Lock on first access |
| **Hash Verification** | Wiring hash for validation |
