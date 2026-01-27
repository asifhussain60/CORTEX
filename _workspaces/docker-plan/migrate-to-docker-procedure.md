# CORTEX Migration Script
## Automated Cherry-Pick Migration to Clean Branch

**Document:** migrate-to-docker-procedure.md  
**Date:** 2026-01-27  

---

## 🎯 Migration Overview

| Phase | Description | Duration |
|-------|-------------|----------|
| **Phase 1** | Create orphan branch | 5 min |
| **Phase 2** | Cherry-pick core structure | 30 min |
| **Phase 3** | Cherry-pick orchestrators | 20 min |
| **Phase 4** | Cherry-pick infrastructure | 15 min |
| **Phase 5** | Cherry-pick tests | 20 min |
| **Phase 6** | Create new wiring system | 30 min |
| **Phase 7** | Validate & verify | 15 min |
| **TOTAL** | | ~2.5 hours |

---

## 📁 Pre-Migration Setup

### Create Migration Directory

```bash
# Create migration workspace
mkdir -p /tmp/cortex-migration
cd /tmp/cortex-migration

# Clone fresh copy for reference
git clone /Users/asifhussain/PROJECTS/CORTEX cortex-original

# Navigate to project
cd /Users/asifhussain/PROJECTS/CORTEX
```

---

## Phase 1: Create Orphan Branch

```bash
#!/bin/bash
# phase1-orphan-branch.sh

set -e

echo "=== Phase 1: Creating Orphan Branch ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Stash any uncommitted changes
git stash push -m "pre-docker-migration-$(date +%Y%m%d_%H%M%S)"

# Create orphan branch (no history)
git checkout --orphan docker-clean-v1

# Remove all files (but keep .git)
git rm -rf .

# Create initial commit
cat > README.md << 'EOF'
# CORTEX Docker-First Architecture

A clean, lean implementation with Git-backed YAML wiring.

## Quick Start

```bash
docker-compose up -d
```

## Architecture

- **Single Entry Point:** `cortex.wiring.bootstrap_cortex()`
- **Git-Backed Wiring:** YAML specifications in `cortex/wiring/specifications/`
- **Zero Database:** No SQLite, no state files

## Status

- Wiring Tests: 65 comprehensive tests
- Orchestrators: 23 production-ready
- MCP Tools: 23+ tools
EOF

git add README.md
git commit -m "Initial commit: CORTEX Docker-First Architecture"

echo "✅ Phase 1 complete: docker-clean-v1 branch created"
```

---

## Phase 2: Cherry-Pick Core Structure

```bash
#!/bin/bash
# phase2-core-structure.sh

set -e

echo "=== Phase 2: Cherry-Picking Core Structure ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Checkout specific files from main branch
# Using git restore to selectively bring files

# Root configs
git checkout main -- pyrightconfig.json 2>/dev/null || true
git checkout main -- requirements.txt 2>/dev/null || true
git checkout main -- cortex-config.yaml 2>/dev/null || true
git checkout main -- mkdocs.yml 2>/dev/null || true

# Create directory structure
mkdir -p cortex/{api,brain,cli,common,config,core,infrastructure,mcp,models,orchestrators,tools}
mkdir -p cortex/wiring/{registry,specifications}
mkdir -p cortex_brain/{tier0/governance,tier1,tier2,tier3/knowledge}
mkdir -p tests/{wiring,orchestrators,infrastructure,integration}
mkdir -p deployment
mkdir -p docs
mkdir -p scripts

# Cherry-pick cortex/__init__.py (we'll modify it later)
git checkout main -- cortex/__init__.py

# Cherry-pick core modules
FILES=(
    # API
    "cortex/api/__init__.py"
    "cortex/api/mcp_server.py"
    
    # Common
    "cortex/common/__init__.py"
    "cortex/common/models.py"
    "cortex/common/exceptions.py"
    "cortex/common/constants.py"
    "cortex/common/utils.py"
    
    # Config
    "cortex/config/__init__.py"
    "cortex/config/settings.py"
    "cortex/config/loader.py"
    
    # Core
    "cortex/core/__init__.py"
    "cortex/core/state.py"
    "cortex/core/context.py"
    "cortex/core/protocols.py"
    
    # Models
    "cortex/models/__init__.py"
    "cortex/models/base.py"
    "cortex/models/events.py"
    "cortex/models/responses.py"
)

for file in "${FILES[@]}"; do
    git checkout main -- "$file" 2>/dev/null && echo "✓ $file" || echo "✗ $file not found"
done

# Stage all
git add .
git commit -m "Add core structure: API, common, config, core, models"

echo "✅ Phase 2 complete: Core structure added"
```

---

## Phase 3: Cherry-Pick Orchestrators

```bash
#!/bin/bash
# phase3-orchestrators.sh

set -e

echo "=== Phase 3: Cherry-Picking Orchestrators ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Core Orchestrators
CORE_ORCHESTRATORS=(
    "cortex/orchestrators/__init__.py"
    "cortex/orchestrators/base_orchestrator.py"
    "cortex/orchestrators/core/__init__.py"
    "cortex/orchestrators/core/master_orchestrator.py"
    "cortex/orchestrators/core/interaction_orchestrator.py"
    "cortex/orchestrators/core/intent_router.py"
    "cortex/orchestrators/core/tdd_orchestrator.py"
    "cortex/orchestrators/core/workflow_orchestrator.py"
    "cortex/orchestrators/core/wrapped_tdd_orchestrator.py"
)

# Domain Orchestrators
DOMAIN_ORCHESTRATORS=(
    "cortex/orchestrators/domain/__init__.py"
    "cortex/orchestrators/domain/refactoring_orchestrator.py"
    "cortex/orchestrators/domain/planning_orchestrator.py"
    "cortex/orchestrators/domain/domain_orchestrator.py"
    "cortex/orchestrators/domain/conversation_orchestrator.py"
    "cortex/orchestrators/domain/selenium_playwright_orchestrator.py"
)

# Support Orchestrators
SUPPORT_ORCHESTRATORS=(
    "cortex/orchestrators/support/__init__.py"
    "cortex/orchestrators/support/onboarding_orchestrator.py"
    "cortex/orchestrators/support/tool_discovery_orchestrator.py"
    "cortex/orchestrators/support/upgrade_orchestrator.py"
    "cortex/orchestrators/support/rollback_orchestrator.py"
    "cortex/orchestrators/support/setup_orchestrator.py"
    "cortex/orchestrators/support/composed_orchestrator.py"
    "cortex/orchestrators/support/composed_orchestrator_config.py"
)

# Documentation Orchestrators
DOC_ORCHESTRATORS=(
    "cortex/orchestrators/documentation/__init__.py"
    "cortex/orchestrators/documentation/documentation_orchestrator.py"
)

# Cherry-pick all
for file in "${CORE_ORCHESTRATORS[@]}" "${DOMAIN_ORCHESTRATORS[@]}" "${SUPPORT_ORCHESTRATORS[@]}" "${DOC_ORCHESTRATORS[@]}"; do
    git checkout main -- "$file" 2>/dev/null && echo "✓ $file" || echo "✗ $file not found"
done

git add .
git commit -m "Add orchestrators: 23 production-ready orchestrators"

echo "✅ Phase 3 complete: All orchestrators added"
```

---

## Phase 4: Cherry-Pick Infrastructure

```bash
#!/bin/bash
# phase4-infrastructure.sh

set -e

echo "=== Phase 4: Cherry-Picking Infrastructure ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Audit & Logging (PRESERVE - Enterprise Grade)
AUDIT_FILES=(
    "cortex/infrastructure/__init__.py"
    "cortex/infrastructure/enhanced_audit_logger.py"
    "cortex/infrastructure/audit_hash_chain.py"
    "cortex/infrastructure/audit_types.py"
    "cortex/infrastructure/log_config.py"
    "cortex/infrastructure/structured_logger.py"
)

# Resilience (PRESERVE - Enterprise Grade)
RESILIENCE_FILES=(
    "cortex/infrastructure/circuit_breaker.py"
    "cortex/infrastructure/retry_handler.py"
    "cortex/infrastructure/rate_limiter.py"
    "cortex/infrastructure/resilience/__init__.py"
    "cortex/infrastructure/resilience/circuit_breaker.py"
    "cortex/infrastructure/resilience/rate_limiter.py"
    "cortex/infrastructure/resilience/retry.py"
)

# Observability (PRESERVE)
OBSERVABILITY_FILES=(
    "cortex/infrastructure/prometheus_metrics.py"
    "cortex/infrastructure/health_check.py"
    "cortex/infrastructure/telemetry.py"
    "cortex/observability/__init__.py"
    "cortex/observability/metrics.py"
    "cortex/observability/tracing.py"
)

# Execution
EXECUTION_FILES=(
    "cortex/execution/__init__.py"
    "cortex/execution/task_executor.py"
    "cortex/execution/async_executor.py"
)

# Cherry-pick all
for file in "${AUDIT_FILES[@]}" "${RESILIENCE_FILES[@]}" "${OBSERVABILITY_FILES[@]}" "${EXECUTION_FILES[@]}"; do
    git checkout main -- "$file" 2>/dev/null && echo "✓ $file" || echo "✗ $file not found"
done

git add .
git commit -m "Add infrastructure: audit, resilience, observability, execution"

echo "✅ Phase 4 complete: Infrastructure added"
```

---

## Phase 5: Cherry-Pick Brain & Knowledge

```bash
#!/bin/bash
# phase5-brain-knowledge.sh

set -e

echo "=== Phase 5: Cherry-Picking Brain & Knowledge ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Brain Core
BRAIN_CORE=(
    "cortex/brain/__init__.py"
    "cortex/brain/core/__init__.py"
    "cortex/brain/core/governance_registry.py"
    "cortex/brain/core/state_manager.py"
    "cortex/brain/core/context_manager.py"
    "cortex/brain/core/knowledge/__init__.py"
    "cortex/brain/core/knowledge/knowledge_repository.py"
)

# Domain Brain
DOMAIN_BRAIN=(
    "cortex/domain_brain/__init__.py"
    "cortex/domain_brain/business_knowledge_repository.py"
)

# cortex_brain Tier 0 (Governance)
TIER0_FILES=(
    "cortex_brain/__init__.py"
    "cortex_brain/tier0/__init__.py"
    "cortex_brain/tier0/governance/__init__.py"
    "cortex_brain/tier0/governance/core_rules.yaml"
    "cortex_brain/tier0/governance/immutable_governance.yaml"
)

# cortex_brain Tier 3 (Knowledge YAMLs)
# Note: These will be copied as a directory

# Cherry-pick all
for file in "${BRAIN_CORE[@]}" "${DOMAIN_BRAIN[@]}" "${TIER0_FILES[@]}"; do
    git checkout main -- "$file" 2>/dev/null && echo "✓ $file" || echo "✗ $file not found"
done

# Copy entire tier3/knowledge directory
git checkout main -- cortex_brain/tier3/knowledge/ 2>/dev/null || echo "✗ tier3/knowledge/ not found"

git add .
git commit -m "Add brain: governance, state, knowledge (35+ YAMLs)"

echo "✅ Phase 5 complete: Brain & Knowledge added"
```

---

## Phase 6: Cherry-Pick MCP & Tools

```bash
#!/bin/bash
# phase6-mcp-tools.sh

set -e

echo "=== Phase 6: Cherry-Picking MCP & Tools ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# MCP Core
MCP_FILES=(
    "cortex/mcp/__init__.py"
    "cortex/mcp/server.py"
    "cortex/mcp/protocol.py"
    "cortex/mcp/handlers.py"
    "cortex/mcp/tools/__init__.py"
    "cortex/mcp/tools/registry.py"
    "cortex/mcp/tools/base_tool.py"
)

# Tools
TOOL_FILES=(
    "cortex/tools/__init__.py"
    "cortex/tools/total_recall_agent.py"
    "cortex/tools/code_analyzer.py"
    "cortex/tools/file_operations.py"
    "cortex/tools/git_operations.py"
    "cortex/tools/search_tools.py"
)

# Intent Router (keep as separate module)
INTENT_FILES=(
    "cortex/intent_router/__init__.py"
    "cortex/intent_router/router.py"
    "cortex/intent_router/classifier.py"
)

# CLI
CLI_FILES=(
    "cortex/cli/__init__.py"
    "cortex/cli/main.py"
    "cortex/cli/commands.py"
)

# Cherry-pick all
for file in "${MCP_FILES[@]}" "${TOOL_FILES[@]}" "${INTENT_FILES[@]}" "${CLI_FILES[@]}"; do
    git checkout main -- "$file" 2>/dev/null && echo "✓ $file" || echo "✗ $file not found"
done

git add .
git commit -m "Add MCP, tools, intent router, CLI"

echo "✅ Phase 6 complete: MCP & Tools added"
```

---

## Phase 7: Create New Wiring System

```bash
#!/bin/bash
# phase7-wiring-system.sh

set -e

echo "=== Phase 7: Creating New Wiring System ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Create wiring directory structure
mkdir -p cortex/wiring/registry
mkdir -p cortex/wiring/specifications

# Create __init__.py
cat > cortex/wiring/__init__.py << 'EOF'
"""
CORTEX Wiring Module - Single Entry Point
==========================================

This is the ONLY wiring mechanism in CORTEX.
All orchestrator instantiation goes through here.

Usage:
    from cortex.wiring import bootstrap_cortex, get_cortex

    cortex = bootstrap_cortex()  # Initialize once
    cortex = get_cortex()        # Get singleton
"""

from cortex.wiring.bootstrap import (
    bootstrap_cortex,
    get_cortex,
    is_wired,
    get_wiring_hash,
)

__all__ = [
    "bootstrap_cortex",
    "get_cortex",
    "is_wired",
    "get_wiring_hash",
]
EOF

# Create bootstrap.py (Single Entry Point)
cat > cortex/wiring/bootstrap.py << 'BOOTSTRAP_EOF'
"""
CORTEX Bootstrap - Single Entry Point
=====================================

This is the ONLY way to initialize CORTEX wiring.
"""

import threading
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from cortex.wiring.registry.git_backed_registry import GitBackedRegistry

logger = logging.getLogger(__name__)

# Global singleton
_CORTEX_INSTANCE: Optional["CortexInstance"] = None
_WIRING_COMPLETE: bool = False
_WIRING_LOCK = threading.Lock()


@dataclass
class CortexInstance:
    """Singleton CORTEX instance."""
    registry: GitBackedRegistry
    wiring_hash: str
    orchestrator_count: int


def bootstrap_cortex(
    specs_dir: Optional[Path] = None
) -> CortexInstance:
    """
    Bootstrap CORTEX - Single Entry Point.
    
    This function is idempotent - calling multiple times
    returns the same instance.
    
    Args:
        specs_dir: Optional path to specifications directory.
                   Defaults to cortex/wiring/specifications/
    
    Returns:
        CortexInstance with registry and wiring hash
    """
    global _CORTEX_INSTANCE, _WIRING_COMPLETE
    
    # Fast path - already wired
    if _WIRING_COMPLETE and _CORTEX_INSTANCE:
        return _CORTEX_INSTANCE
    
    with _WIRING_LOCK:
        # Double-check inside lock
        if _WIRING_COMPLETE and _CORTEX_INSTANCE:
            return _CORTEX_INSTANCE
        
        logger.info("🔌 CORTEX wiring started...")
        
        # Default specs directory
        if specs_dir is None:
            specs_dir = Path(__file__).parent / "specifications"
        
        # Create registry from YAML specs
        registry = GitBackedRegistry(specs_dir)
        
        # Compute wiring hash
        wiring_hash = registry.compute_wiring_hash()
        
        # Create instance
        _CORTEX_INSTANCE = CortexInstance(
            registry=registry,
            wiring_hash=wiring_hash,
            orchestrator_count=len(registry.get_all_specs())
        )
        
        _WIRING_COMPLETE = True
        
        logger.info(
            f"✅ CORTEX wired: {_CORTEX_INSTANCE.orchestrator_count} orchestrators, "
            f"hash={wiring_hash}"
        )
        
        return _CORTEX_INSTANCE


def get_cortex() -> CortexInstance:
    """Get the singleton CORTEX instance."""
    if not _WIRING_COMPLETE or not _CORTEX_INSTANCE:
        return bootstrap_cortex()
    return _CORTEX_INSTANCE


def is_wired() -> bool:
    """Check if CORTEX is wired."""
    return _WIRING_COMPLETE


def get_wiring_hash() -> Optional[str]:
    """Get the wiring hash."""
    if _CORTEX_INSTANCE:
        return _CORTEX_INSTANCE.wiring_hash
    return None
BOOTSTRAP_EOF

# Create git_backed_registry.py
cat > cortex/wiring/registry/git_backed_registry.py << 'REGISTRY_EOF'
"""
Git-Backed Registry - YAML-based Wiring Specifications
======================================================
"""

import yaml
import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorSpec:
    """Specification for an orchestrator from YAML."""
    name: str
    module: str
    class_name: str
    category: str  # CORE, DOMAIN, SUPPORT, DOCUMENTATION
    tier: int
    priority: int
    dependencies: List[str] = field(default_factory=list)
    requires_params: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    health_check: str = ""
    mcp_adapter: str = ""


class GitBackedRegistry:
    """Git-backed registry using YAML specifications."""
    
    def __init__(self, specs_dir: Path):
        self.specs_dir = specs_dir
        self._specs: Dict[str, OrchestratorSpec] = {}
        self._wiring_order: List[str] = []
        self._lazy_orchestrators: Dict[str, Any] = {}
        
        self._load_specifications()
        self._compute_wiring_order()
    
    def _load_specifications(self) -> None:
        """Load all YAML specifications."""
        yaml_files = list(self.specs_dir.glob("*.yaml"))
        
        for yaml_file in yaml_files:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            
            for orch_def in data.get("orchestrators", []):
                spec = OrchestratorSpec(
                    name=orch_def["name"],
                    module=orch_def["module"],
                    class_name=orch_def["class_name"],
                    category=orch_def.get("category", "UNKNOWN"),
                    tier=orch_def.get("tier", 1),
                    priority=orch_def.get("priority", 100),
                    dependencies=orch_def.get("dependencies", []),
                    requires_params=orch_def.get("requires_params", {}),
                    capabilities=orch_def.get("capabilities", []),
                    health_check=orch_def.get("health_check", ""),
                    mcp_adapter=orch_def.get("mcp_adapter", "")
                )
                self._specs[spec.name] = spec
        
        logger.info(f"Loaded {len(self._specs)} orchestrator specs")
    
    def _compute_wiring_order(self) -> None:
        """Compute topological wiring order."""
        # Kahn's algorithm for topological sort
        in_degree = {name: 0 for name in self._specs}
        
        for name, spec in self._specs.items():
            for dep in spec.dependencies:
                if dep in in_degree:
                    in_degree[name] += 1
        
        # Start with nodes with no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        queue.sort(key=lambda n: self._specs[n].priority)
        
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            
            for name, spec in self._specs.items():
                if node in spec.dependencies:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
            
            queue.sort(key=lambda n: self._specs[n].priority)
        
        if len(order) != len(self._specs):
            raise ValueError("Circular dependency detected in orchestrators")
        
        self._wiring_order = order
    
    def get_all_specs(self) -> Dict[str, OrchestratorSpec]:
        """Get all orchestrator specifications."""
        return self._specs.copy()
    
    def get_wiring_order(self) -> List[str]:
        """Get the computed wiring order."""
        return self._wiring_order.copy()
    
    def get_orchestrator(self, name: str) -> Any:
        """Get lazy orchestrator by name."""
        from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
        
        if name not in self._lazy_orchestrators:
            if name not in self._specs:
                raise KeyError(f"Unknown orchestrator: {name}")
            
            spec = self._specs[name]
            self._lazy_orchestrators[name] = LazyOrchestrator(spec, self)
        
        return self._lazy_orchestrators[name]
    
    def compute_wiring_hash(self) -> str:
        """Compute deterministic hash of all specifications."""
        content = ""
        for name in sorted(self._specs.keys()):
            spec = self._specs[name]
            content += f"{name}:{spec.module}:{spec.priority}:{sorted(spec.dependencies)}\n"
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
REGISTRY_EOF

# Create lazy_orchestrator.py
cat > cortex/wiring/registry/lazy_orchestrator.py << 'LAZY_EOF'
"""
Lazy Orchestrator - On-Demand Wiring
====================================
"""

import threading
import logging
import importlib
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.wiring.registry.git_backed_registry import GitBackedRegistry, OrchestratorSpec

logger = logging.getLogger(__name__)


class LazyOrchestrator:
    """Lazy wrapper for orchestrator - wires on first use."""
    
    # Attributes that don't trigger wiring
    _SPECIAL_ATTRS = {
        'is_wired', 'spec', 'force_wire', '_instance', '_lock', '_registry',
        '__class__', '__dict__', '__doc__', '__module__', '__weakref__'
    }
    
    def __init__(self, spec: "OrchestratorSpec", registry: "GitBackedRegistry"):
        object.__setattr__(self, '_spec', spec)
        object.__setattr__(self, '_registry', registry)
        object.__setattr__(self, '_instance', None)
        object.__setattr__(self, '_lock', threading.Lock())
        object.__setattr__(self, '_is_wired', False)
    
    @property
    def is_wired(self) -> bool:
        return object.__getattribute__(self, '_is_wired')
    
    @property
    def spec(self) -> "OrchestratorSpec":
        return object.__getattribute__(self, '_spec')
    
    def force_wire(self) -> None:
        """Force immediate wiring."""
        if self.is_wired:
            return
        
        with object.__getattribute__(self, '_lock'):
            if self.is_wired:
                return
            
            spec = self.spec
            logger.info(f"Wiring {spec.name}...")
            
            # Import module
            module = importlib.import_module(spec.module)
            cls = getattr(module, spec.class_name)
            
            # Resolve required parameters
            kwargs = self._resolve_params(spec.requires_params)
            
            # Create instance
            instance = cls(**kwargs)
            
            object.__setattr__(self, '_instance', instance)
            object.__setattr__(self, '_is_wired', True)
            
            logger.info(f"✓ Wired {spec.name}")
    
    def _resolve_params(self, requires_params: dict) -> dict:
        """Resolve required parameters for orchestrator."""
        kwargs = {}
        
        for param_name, param_spec in requires_params.items():
            if param_spec.get("lazy_create"):
                # Create lazily based on type
                param_type = param_spec.get("type")
                if param_type == "ConversationProtocol":
                    from cortex.core.protocols import ConversationProtocol
                    kwargs[param_name] = ConversationProtocol()
                elif param_type == "StateManager":
                    from cortex.brain.core.state_manager import get_state_manager
                    kwargs[param_name] = get_state_manager()
                # Add more types as needed
        
        return kwargs
    
    def __getattr__(self, name: str) -> Any:
        if name in LazyOrchestrator._SPECIAL_ATTRS:
            return object.__getattribute__(self, name)
        
        # Wire on first real attribute access
        self.force_wire()
        
        instance = object.__getattribute__(self, '_instance')
        return getattr(instance, name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name in LazyOrchestrator._SPECIAL_ATTRS:
            object.__setattr__(self, name, value)
        else:
            self.force_wire()
            instance = object.__getattribute__(self, '_instance')
            setattr(instance, name, value)
LAZY_EOF

# Create registry __init__.py
cat > cortex/wiring/registry/__init__.py << 'EOF'
"""Registry module for git-backed wiring."""

from cortex.wiring.registry.git_backed_registry import GitBackedRegistry, OrchestratorSpec
from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator

__all__ = ["GitBackedRegistry", "OrchestratorSpec", "LazyOrchestrator"]
EOF

git add cortex/wiring/
git commit -m "Add git-backed wiring system: bootstrap, registry, lazy loading"

echo "✅ Phase 7 complete: Wiring system created"
```

---

## Phase 8: Create YAML Specifications

```bash
#!/bin/bash
# phase8-yaml-specs.sh

set -e

echo "=== Phase 8: Creating YAML Specifications ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Create core-wiring.yaml
cat > cortex/wiring/specifications/core-wiring.yaml << 'CORE_YAML'
# CORTEX Core Orchestrators
# Priority 1-100: Core orchestrators
# Lower number = wired first

metadata:
  version: "1.0"
  category: "CORE"
  description: "Core orchestrators - wired first"

orchestrators:
  - name: MasterOrchestrator
    module: cortex.orchestrators.core.master_orchestrator
    class_name: MasterOrchestrator
    category: CORE
    tier: 0
    priority: 1
    dependencies: []
    requires_params: {}
    capabilities:
      - orchestration
      - routing
      - coordination
    health_check: "self.is_healthy()"
    mcp_adapter: cortex.mcp.adapters.master_adapter

  - name: InteractionOrchestrator
    module: cortex.orchestrators.core.interaction_orchestrator
    class_name: InteractionOrchestrator
    category: CORE
    tier: 1
    priority: 10
    dependencies:
      - MasterOrchestrator
    requires_params:
      conversation_protocol:
        type: ConversationProtocol
        lazy_create: true
    capabilities:
      - user_interaction
      - conversation_management
    health_check: "self.protocol is not None"
    mcp_adapter: cortex.mcp.adapters.interaction_adapter

  - name: IntentRouter
    module: cortex.orchestrators.core.intent_router
    class_name: IntentRouter
    category: CORE
    tier: 1
    priority: 20
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - intent_classification
      - routing
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.intent_adapter

  - name: TDDOrchestrator
    module: cortex.orchestrators.core.tdd_orchestrator
    class_name: TDDOrchestrator
    category: CORE
    tier: 1
    priority: 30
    dependencies:
      - MasterOrchestrator
      - IntentRouter
    requires_params: {}
    capabilities:
      - test_driven_development
      - test_generation
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.tdd_adapter

  - name: WorkflowOrchestrator
    module: cortex.orchestrators.core.workflow_orchestrator
    class_name: WorkflowOrchestrator
    category: CORE
    tier: 1
    priority: 40
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - workflow_execution
      - task_sequencing
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.workflow_adapter

  - name: WrappedTDDOrchestrator
    module: cortex.orchestrators.core.wrapped_tdd_orchestrator
    class_name: WrappedTDDOrchestrator
    category: CORE
    tier: 1
    priority: 50
    dependencies:
      - TDDOrchestrator
    requires_params: {}
    capabilities:
      - wrapped_tdd
    health_check: "True"
    mcp_adapter: ""
CORE_YAML

# Create domain-wiring.yaml
cat > cortex/wiring/specifications/domain-wiring.yaml << 'DOMAIN_YAML'
# CORTEX Domain Orchestrators
# Priority 101-200: Domain orchestrators

metadata:
  version: "1.0"
  category: "DOMAIN"
  description: "Domain-specific orchestrators"

orchestrators:
  - name: RefactoringOrchestrator
    module: cortex.orchestrators.domain.refactoring_orchestrator
    class_name: RefactoringOrchestrator
    category: DOMAIN
    tier: 2
    priority: 101
    dependencies:
      - MasterOrchestrator
      - TDDOrchestrator
    requires_params: {}
    capabilities:
      - code_refactoring
      - pattern_application
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.refactoring_adapter

  - name: PlanningOrchestrator
    module: cortex.orchestrators.domain.planning_orchestrator
    class_name: PlanningOrchestrator
    category: DOMAIN
    tier: 2
    priority: 102
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - project_planning
      - task_breakdown
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.planning_adapter

  - name: DomainOrchestrator
    module: cortex.orchestrators.domain.domain_orchestrator
    class_name: DomainOrchestrator
    category: DOMAIN
    tier: 2
    priority: 103
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - domain_logic
    health_check: "True"
    mcp_adapter: ""

  - name: ConversationOrchestrator
    module: cortex.orchestrators.domain.conversation_orchestrator
    class_name: ConversationOrchestrator
    category: DOMAIN
    tier: 2
    priority: 104
    dependencies:
      - InteractionOrchestrator
    requires_params: {}
    capabilities:
      - conversation_flow
      - dialog_management
    health_check: "True"
    mcp_adapter: ""

  - name: SeleniumPlaywrightOrchestrator
    module: cortex.orchestrators.domain.selenium_playwright_orchestrator
    class_name: SeleniumPlaywrightOrchestrator
    category: DOMAIN
    tier: 2
    priority: 105
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - browser_automation
      - ui_testing
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.automation_adapter
DOMAIN_YAML

# Create support-wiring.yaml
cat > cortex/wiring/specifications/support-wiring.yaml << 'SUPPORT_YAML'
# CORTEX Support Orchestrators
# Priority 201-300: Support orchestrators

metadata:
  version: "1.0"
  category: "SUPPORT"
  description: "Support and utility orchestrators"

orchestrators:
  - name: OnboardingOrchestrator
    module: cortex.orchestrators.support.onboarding_orchestrator
    class_name: OnboardingOrchestrator
    category: SUPPORT
    tier: 3
    priority: 201
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - user_onboarding
      - setup_guidance
    health_check: "True"
    mcp_adapter: ""

  - name: ToolDiscoveryOrchestrator
    module: cortex.orchestrators.support.tool_discovery_orchestrator
    class_name: ToolDiscoveryOrchestrator
    category: SUPPORT
    tier: 3
    priority: 202
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - tool_discovery
      - capability_mapping
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.discovery_adapter

  - name: UpgradeOrchestrator
    module: cortex.orchestrators.support.upgrade_orchestrator
    class_name: UpgradeOrchestrator
    category: SUPPORT
    tier: 3
    priority: 203
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - version_upgrade
      - migration
    health_check: "True"
    mcp_adapter: ""

  - name: RollbackOrchestrator
    module: cortex.orchestrators.support.rollback_orchestrator
    class_name: RollbackOrchestrator
    category: SUPPORT
    tier: 3
    priority: 204
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - version_rollback
      - state_recovery
    health_check: "True"
    mcp_adapter: ""

  - name: SetupOrchestrator
    module: cortex.orchestrators.support.setup_orchestrator
    class_name: SetupOrchestrator
    category: SUPPORT
    tier: 3
    priority: 205
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - environment_setup
      - configuration
    health_check: "True"
    mcp_adapter: ""

  - name: ComposedOrchestrator
    module: cortex.orchestrators.support.composed_orchestrator
    class_name: ComposedOrchestrator
    category: SUPPORT
    tier: 3
    priority: 206
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - orchestrator_composition
      - pipeline_execution
    health_check: "True"
    mcp_adapter: ""

  - name: DocumentationOrchestrator
    module: cortex.orchestrators.documentation.documentation_orchestrator
    class_name: DocumentationOrchestrator
    category: SUPPORT
    tier: 3
    priority: 210
    dependencies:
      - MasterOrchestrator
    requires_params: {}
    capabilities:
      - documentation_generation
      - doc_maintenance
    health_check: "True"
    mcp_adapter: cortex.mcp.adapters.documentation_adapter
SUPPORT_YAML

git add cortex/wiring/specifications/
git commit -m "Add YAML wiring specifications: core, domain, support"

echo "✅ Phase 8 complete: YAML specifications created"
```

---

## Phase 9: Cherry-Pick Tests

```bash
#!/bin/bash
# phase9-tests.sh

set -e

echo "=== Phase 9: Cherry-Picking Tests ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Test utilities
git checkout main -- tests/conftest.py 2>/dev/null || true
git checkout main -- tests/__init__.py 2>/dev/null || true

# Orchestrator tests
ORCH_TESTS=(
    "tests/orchestrators/test_master_orchestrator.py"
    "tests/orchestrators/test_intent_router.py"
    "tests/orchestrators/test_tdd_orchestrator.py"
    "tests/orchestrators/test_interaction_orchestrator.py"
    "tests/orchestrators/test_refactoring_orchestrator.py"
)

# Infrastructure tests
INFRA_TESTS=(
    "tests/infrastructure/test_audit_logger.py"
    "tests/infrastructure/test_circuit_breaker.py"
    "tests/infrastructure/test_resilience.py"
)

# Integration tests
INT_TESTS=(
    "tests/integration/test_mcp_server.py"
    "tests/integration/test_orchestrator_integration.py"
)

# Cherry-pick tests
for file in "${ORCH_TESTS[@]}" "${INFRA_TESTS[@]}" "${INT_TESTS[@]}"; do
    git checkout main -- "$file" 2>/dev/null && echo "✓ $file" || echo "✗ $file not found"
done

git add tests/
git commit -m "Add tests: orchestrators, infrastructure, integration"

echo "✅ Phase 9 complete: Tests added"
```

---

## Phase 10: Docker Setup

```bash
#!/bin/bash
# phase10-docker.sh

set -e

echo "=== Phase 10: Docker Setup ==="

cd /Users/asifhussain/PROJECTS/CORTEX

# Create Dockerfile
cat > Dockerfile << 'DOCKERFILE'
# CORTEX MCP Server - Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY cortex/ ./cortex/
COPY cortex_brain/ ./cortex_brain/

# Set Python path
ENV PYTHONPATH=/app

# Wire on startup
RUN python -c "from cortex.wiring import bootstrap_cortex; bootstrap_cortex()"

# Expose MCP port
EXPOSE 8443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from cortex.wiring import is_wired; exit(0 if is_wired() else 1)"

# Run MCP server
CMD ["python", "-m", "cortex.mcp.server"]
DOCKERFILE

# Create docker-compose.yml
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  cortex-mcp:
    build: .
    image: cortex/mcp-server:latest
    container_name: cortex-mcp-server
    ports:
      - "8443:8443"
    environment:
      - PYTHONUNBUFFERED=1
      - CORTEX_ENV=production
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "python", "-c", "from cortex.wiring import is_wired; exit(0 if is_wired() else 1)"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
COMPOSE

# Create .dockerignore
cat > .dockerignore << 'IGNORE'
.git
.github
.vscode
__pycache__
*.pyc
*.pyo
*.db
*.db-journal
*.db-wal
*.db-shm
.cortex/
_workspaces/
_backups/
*.md
docs/
tests/
reports/
*.log
.env
IGNORE

git add Dockerfile docker-compose.yml .dockerignore
git commit -m "Add Docker configuration"

echo "✅ Phase 10 complete: Docker setup added"
```

---

## 🚀 Complete Migration Script

```bash
#!/bin/bash
# run-complete-migration.sh

set -e

echo "🚀 CORTEX Complete Migration to Docker-Clean Branch"
echo "===================================================="

# Run all phases
./phase1-orphan-branch.sh
./phase2-core-structure.sh
./phase3-orchestrators.sh
./phase4-infrastructure.sh
./phase5-brain-knowledge.sh
./phase6-mcp-tools.sh
./phase7-wiring-system.sh
./phase8-yaml-specs.sh
./phase9-tests.sh
./phase10-docker.sh

echo ""
echo "✅ Migration Complete!"
echo ""
echo "Next Steps:"
echo "1. Run tests: pytest tests/wiring/ -v"
echo "2. Build Docker: docker-compose build"
echo "3. Start server: docker-compose up -d"
echo "4. Verify: curl http://localhost:8443/health"
```

---

## 📊 Expected Results

After migration:

| Metric | Before | After |
|--------|--------|-------|
| Python Files | 1,592 | ~450 |
| Test Files | 500 | ~150 |
| MD Files | 753 | ~15 |
| Wiring Systems | 7 | 1 |
| Database Files | Multiple | 0 |
| Lines of Code | ~200K | ~60K |
