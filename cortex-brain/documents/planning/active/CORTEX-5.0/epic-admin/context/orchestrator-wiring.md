# 🔌 Master Orchestrator Wiring Plan

**Created:** January 4, 2026  
**Author:** Asif Hussain  
**Priority:** 🚨 CRITICAL (Architecture Foundation)  
**Status:** 📋 READY TO IMPLEMENT  
**Duration:** 0.5-1 day

---

## 🎯 Problem Statement

**Master Orchestrator exists but is NOT being used:**

### Current State

1. **✅ Implementation Complete:**
   - `src/orchestrators/master_orchestrator.py` - Fully implemented (707 lines)
   - `cortex-brain/config/master-orchestrator.yaml` - Configuration exists (294 lines)
   - Tests exist: `tests/orchestrators/test_master_orchestrator*.py` (3 files)
   - Pattern router, execution engine, state manager all implemented

2. **❌ Integration Missing:**
   - `src/entry_point/cortex_entry.py` uses legacy `router.execute()` (line 457)
   - No Master Orchestrator instantiation in entry point
   - No routing through YAML-based pattern matching
   - Direct orchestrator calls instead of registry-based dispatch

3. **⚠️ YAML-Based Execution Partial:**
   - Routing rules in YAML: ✅ (`master-orchestrator.yaml`)
   - Orchestrator manifests in YAML: ✅ (`cortex-brain/manifests/orchestrators/`)
   - Actual execution: ❌ Hardcoded Python imports

### Risk

**Without Master Orchestrator:**
- Manual routing logic scattered across codebase
- No centralized pattern matching
- No orchestrator registry
- No cross-orchestrator state coordination
- `.github/prompts/CORTEX.prompt.md` references architecture that doesn't execute

---

## 🏗️ Solution: Wire Master Orchestrator

### Phase 1: Add Master Orchestrator to CortexEntry (30 min)

**File:** `src/entry_point/cortex_entry.py`

**Changes:**

1. **Add Import:**
```python
from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB
```

2. **Add Property (after line ~150):**
```python
@property
def master_orchestrator(self):
    """Lazy-load Master Orchestrator with registry and state DB."""
    if self._master_orchestrator is None:
        try:
            # Initialize registry
            registry = OrchestratorRegistry()
            
            # Register all orchestrators
            # TODO: Auto-discovery from manifests
            # For now, manually register known orchestrators
            
            # Initialize state DB
            state_db = PlanningStateDB(
                str(self.brain_path / "databases" / "planning_state.db")
            )
            
            # Create Master Orchestrator
            self._master_orchestrator = MasterOrchestrator(
                config_path=str(self.brain_path / "config" / "master-orchestrator.yaml"),
                registry=registry,
                state_db=state_db,
                llm_fallback=None,  # Optional: add LLMIntentClassifier
                context_middleware=self.context_middleware,
                response_renderer=None,  # Optional: ResponseRenderer
                response_middleware=None  # Optional: ResponseMiddleware
            )
            
            self.logger.debug("Master Orchestrator loaded with YAML routing")
        except Exception as e:
            self.logger.warning(f"Master Orchestrator not available: {e}")
            self._master_orchestrator = None
    return self._master_orchestrator
```

3. **Add to __init__ (after line ~117):**
```python
self._master_orchestrator = None
```

4. **Replace Routing Logic (line ~457):**

**Before:**
```python
# Route to appropriate agent(s)
routing_response = self.router.execute(request)

# Execute the actual agents based on routing decision
if routing_response.success and routing_response.result:
    response = self.agent_executor.execute_routing_decision(
        routing_response.result, request
    )
else:
    # Fallback if routing failed
    response = routing_response
```

**After:**
```python
# Route to appropriate orchestrator via Master Orchestrator
if self.master_orchestrator:
    try:
        # Master Orchestrator uses YAML-based pattern matching
        exec_result = self.master_orchestrator.handle_request(
            user_message,
            context={
                'conversation_id': conversation_id,
                'unified_context': request.context.get('unified_context', {}),
                'workspace_root': str(config.root_path)
            }
        )
        
        # Convert ExecutionResult to AgentResponse
        response = AgentResponse(
            success=exec_result.success,
            result=exec_result.result,
            message=exec_result.message or exec_result.output,
            agent_name=exec_result.orchestrator_id,
            metadata=exec_result.metadata,
            duration_ms=exec_result.execution_time * 1000  # Convert to ms
        )
    except Exception as e:
        self.logger.warning(f"Master Orchestrator failed, falling back to legacy routing: {e}")
        # Fallback to legacy routing
        routing_response = self.router.execute(request)
        if routing_response.success and routing_response.result:
            response = self.agent_executor.execute_routing_decision(
                routing_response.result, request
            )
        else:
            response = routing_response
else:
    # Fallback if Master Orchestrator not available
    routing_response = self.router.execute(request)
    if routing_response.success and routing_response.result:
        response = self.agent_executor.execute_routing_decision(
            routing_response.result, request
        )
    else:
        response = routing_response
```

---

### Phase 2: Populate Orchestrator Registry (30 min)

**File:** `src/mcp/registry.py` (or create if missing)

**Implementation:**

```python
"""
Orchestrator Registry - Dynamic orchestrator discovery and registration.

Supports:
- Manual registration
- Auto-discovery from manifests
- Orchestrator lifecycle management
"""

from typing import Dict, Any, Optional, Callable
from pathlib import Path
import yaml
import logging


class OrchestratorRegistry:
    """
    Central registry for all CORTEX orchestrators.
    
    Enables:
    - Dynamic orchestrator discovery
    - Orchestrator metadata management
    - Lazy-loading of orchestrator implementations
    """
    
    def __init__(self, manifests_dir: Optional[Path] = None):
        """
        Initialize registry.
        
        Args:
            manifests_dir: Path to orchestrator manifests directory
                          (default: cortex-brain/manifests/orchestrators/)
        """
        self.logger = logging.getLogger("cortex.mcp.registry")
        self._orchestrators: Dict[str, Dict[str, Any]] = {}
        self._factories: Dict[str, Callable] = {}
        
        if manifests_dir is None:
            manifests_dir = Path("cortex-brain/manifests/orchestrators")
        
        self.manifests_dir = Path(manifests_dir)
        
        # Auto-discover orchestrators from manifests
        if self.manifests_dir.exists():
            self._discover_orchestrators()
    
    def register(
        self,
        orchestrator_id: str,
        factory: Callable,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register orchestrator with factory function.
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            factory: Function that creates orchestrator instance
            metadata: Optional metadata (name, version, description, etc.)
        """
        self._orchestrators[orchestrator_id] = metadata or {}
        self._factories[orchestrator_id] = factory
        self.logger.info(f"Registered orchestrator: {orchestrator_id}")
    
    def get(self, orchestrator_id: str) -> Optional[Any]:
        """
        Get orchestrator instance by ID.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            Orchestrator instance or None if not found
        """
        factory = self._factories.get(orchestrator_id)
        if factory:
            return factory()
        return None
    
    def list_orchestrators(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered orchestrators with metadata."""
        return self._orchestrators.copy()
    
    def _discover_orchestrators(self):
        """Auto-discover orchestrators from YAML manifests."""
        if not self.manifests_dir.exists():
            self.logger.warning(f"Manifests directory not found: {self.manifests_dir}")
            return
        
        for manifest_file in self.manifests_dir.glob("*-manifest.yaml"):
            try:
                with open(manifest_file, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                orchestrator_id = manifest.get('id')
                if not orchestrator_id:
                    continue
                
                # Extract metadata
                metadata = {
                    'name': manifest.get('name'),
                    'version': manifest.get('version'),
                    'description': manifest.get('description'),
                    'autonomous': manifest.get('autonomous', False),
                    'manifest_path': str(manifest_file)
                }
                
                # Store metadata (factory registered manually for now)
                self._orchestrators[orchestrator_id] = metadata
                self.logger.debug(f"Discovered orchestrator: {orchestrator_id}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load manifest {manifest_file}: {e}")
```

---

### Phase 3: Register Known Orchestrators (30 min)

**Add to Phase 1 (in `master_orchestrator` property):**

```python
# Register all orchestrators
registry.register(
    'planning_v5',
    lambda: self.planning_orchestrator,
    metadata={'name': 'Planning v5', 'autonomous': True}
)

registry.register(
    'tdd_orchestrator',
    lambda: self.tdd_orchestrator,
    metadata={'name': 'TDD Mastery', 'autonomous': False}
)

# Add other orchestrators as they're implemented
# TODO: Auto-discovery from registry.list_orchestrators()
```

---

### Phase 4: Update CORTEX.prompt.md (15 min)

**File:** `.github/prompts/CORTEX.prompt.md`

**Add Status Section:**

```markdown
## 🔌 Architecture Status

**Master Orchestrator:** ✅ WIRED (Since v5.0.2)

**Flow:**
```
User Input → CortexEntry.process()
                ↓
        Master Orchestrator
                ↓
        Pattern Router (YAML)
                ↓
        Orchestrator Registry
                ↓
        Orchestrator Execution
```

**Fallback:** Legacy routing if Master Orchestrator unavailable
```

---

### Phase 5: Validation & Testing (30 min)

**Tests to Run:**

1. **Unit Tests:**
```bash
pytest tests/orchestrators/test_master_orchestrator.py -v
pytest tests/orchestrators/test_master_orchestrator_integration.py -v
```

2. **Integration Test:**
```bash
python -m src.main "plan test-feature"
# Should route through Master Orchestrator → Planning v5
```

3. **Manual Validation:**
```bash
python -m src.main "help"  # Template response
python -m src.main "plan user auth"  # Master Orchestrator → Planning
python -m src.main "tdd implement login"  # Master Orchestrator → TDD
```

**Expected Logs:**
```
INFO cortex.orchestrators.master: MasterOrchestrator initialized with context middleware...
INFO cortex.entry_point: Master Orchestrator loaded with YAML routing
INFO cortex.orchestrators.master: Routing request via pattern match: plan -> planning_v5
```

---

## ✅ Success Criteria

**After wiring:**

1. ✅ Master Orchestrator instantiated in `CortexEntry`
2. ✅ Orchestrator registry populated
3. ✅ Pattern matching routes through YAML config
4. ✅ Legacy routing works as fallback
5. ✅ All tests pass
6. ✅ Manual validation confirms YAML-based routing
7. ✅ Logs show "Master Orchestrator" in routing path

---

## 📊 Impact

**Benefits:**

- ✅ Centralized routing (single source of truth)
- ✅ YAML-based pattern matching (no code changes for new patterns)
- ✅ Orchestrator registry (dynamic discovery)
- ✅ Cross-orchestrator state coordination
- ✅ Aligns code with documented architecture

**Risk Mitigation:**

- Fallback to legacy routing if Master Orchestrator fails
- Gradual migration (both paths work)
- Comprehensive test coverage

---

## 🔗 Related

- **Master Orchestrator:** `src/orchestrators/master_orchestrator.py`
- **Configuration:** `cortex-brain/config/master-orchestrator.yaml`
- **Tests:** `tests/orchestrators/test_master_orchestrator*.py`
- **Prompt:** `.github/prompts/CORTEX.prompt.md`

---

## 📝 Implementation Notes

**Order of Operations:**

1. ✅ Add property to CortexEntry
2. ✅ Initialize registry and state DB
3. ✅ Register known orchestrators
4. ✅ Replace routing logic with Master Orchestrator call
5. ✅ Add fallback to legacy routing
6. ✅ Update documentation
7. ✅ Run tests
8. ✅ Manual validation

**Git Checkpoint:**
```bash
git add src/entry_point/cortex_entry.py src/mcp/registry.py .github/prompts/CORTEX.prompt.md
git commit -m "feat(orchestration): Wire Master Orchestrator into entry point

- Add Master Orchestrator to CortexEntry with lazy loading
- Create OrchestratorRegistry for dynamic discovery
- Route all requests through YAML-based pattern matching
- Fallback to legacy routing for graceful degradation
- Update CORTEX.prompt.md with wiring status

Closes: Master Orchestrator wiring gap
Impact: Centralized routing, YAML-based patterns, registry support"
```

**NO PUSH** (SKULL GIT_NO_PUSH_ENFORCEMENT)
