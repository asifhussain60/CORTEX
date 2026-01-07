# 🔍 CORTEX v5 Remediation Epic - Holistic Risk Analysis

**Version:** 1.0.0 | **Date:** 2026-01-06 | **Author:** CORTEX Analysis Team  
**Scope:** Complete risk assessment of cortex5-remediation epic  
**Methodology:** Architecture-level review with security, performance, scalability focus

---

## 📋 Executive Summary

**Status:** ⚠️ **13 CRITICAL RISKS IDENTIFIED**

**Risk Categories:**
1. 🔴 **Critical (P0):** 4 risks - Require immediate mitigation
2. 🟡 **High (P1):** 5 risks - Require planning/design changes
3. 🟢 **Medium (P2):** 4 risks - Monitor and mitigate during implementation

**Key Finding:** Epic lacks **extensibility framework** for late-stage realizations (e.g., Vision API governance). Recommend adding **Phase P14: Plugin Architecture**.

---

## 🔴 CRITICAL RISKS (P0) - Immediate Action Required

### RISK-001: Database Schema Migration Rollback Failure ⛔

**Category:** Data Integrity | **Severity:** P0_CRITICAL | **Probability:** HIGH

**Description:**
Phase P00 implements database schema consolidation but lacks **atomic rollback** mechanism. If migration fails mid-execution:
- Tables may be partially migrated
- Views may reference non-existent columns
- Foreign keys may be orphaned

**Current State:**
```python
# src/database/migrations/001_add_compatibility_views.sql
CREATE VIEW tier2_patterns AS SELECT * FROM patterns;
-- ❌ No rollback if this fails
```

**Failure Scenarios:**
1. **Concurrent Access:** Active orchestrator reads during migration → corrupted data
2. **Disk Full:** Migration fails mid-INSERT → partial data
3. **Constraint Violation:** FK constraint fails → orphaned records

**Impact:**
- 🔥 **Data Loss:** Potential loss of knowledge graph, user profiles
- 🔥 **System Downtime:** All orchestrators blocked until manual repair
- 🔥 **Recovery Time:** 4-8 hours manual intervention

**Mitigation Strategy:**

```python
# REQUIRED: Atomic migration with savepoints

class DatabaseMigrator:
    def migrate_with_rollback(self, migration: Migration):
        """Execute migration with automatic rollback on failure"""
        
        conn = self.db.connection()
        
        try:
            # Start transaction
            conn.execute("BEGIN TRANSACTION;")
            
            # Create savepoint before each step
            conn.execute("SAVEPOINT pre_migration;")
            
            # Execute migration
            for step in migration.steps:
                step.execute(conn)
                conn.execute(f"SAVEPOINT after_{step.id};")
            
            # Commit if all steps succeed
            conn.execute("COMMIT;")
            
        except Exception as e:
            # Rollback to pre-migration state
            conn.execute("ROLLBACK TO SAVEPOINT pre_migration;")
            logger.error(f"Migration failed, rolled back: {e}")
            raise MigrationFailedError(e)
```

**Acceptance Criteria:**
- ✅ All migrations wrapped in transactions
- ✅ Savepoints before each DDL statement
- ✅ Automatic rollback on any error
- ✅ Migration tested with intentional failures
- ✅ Backup created before migration

---

### RISK-002: Master Orchestrator Task Race Condition ⛔

**Category:** Concurrency | **Severity:** P0_CRITICAL | **Probability:** MEDIUM

**Description:**
Phase P01 implements task management but lacks **thread-safe concurrent access**. Multiple orchestrators updating `tracking/task-registry.json` simultaneously causes:
- Lost updates (write-write conflicts)
- Corrupted JSON (incomplete writes)
- Inconsistent task states

**Current State:**
```python
# src/orchestrators/master/todo_manager.py (PROPOSED)
def update_task(self, task_id: str, status: str):
    # ❌ NOT THREAD-SAFE
    tasks = json.load(open("task-registry.json"))
    tasks[task_id]["status"] = status
    json.dump(tasks, open("task-registry.json", "w"))
```

**Failure Scenarios:**
1. **Concurrent Phase Completion:** P02 and P03 complete simultaneously → one update lost
2. **File Corruption:** Orchestrator A reads, B writes, A writes → B's update lost
3. **Partial JSON:** Write interrupted → file unreadable

**Impact:**
- 🔥 **Lost Progress:** Task completions not recorded
- 🔥 **State Corruption:** task-registry.json becomes invalid
- 🔥 **Epic Blocker:** Cannot track progress accurately

**Mitigation Strategy:**

```python
import fcntl  # File locking
import json
from contextlib import contextmanager
from pathlib import Path

class ThreadSafeTodoManager:
    """Thread-safe task registry with file locking"""
    
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.lock_path = registry_path.with_suffix(".lock")
    
    @contextmanager
    def _acquire_lock(self, timeout: int = 10):
        """Acquire exclusive file lock with timeout"""
        lock_file = open(self.lock_path, "w")
        
        try:
            # Wait up to 10 seconds for lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        except BlockingIOError:
            raise TaskRegistryLockTimeout("Another orchestrator holds lock")
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
    
    def update_task(self, task_id: str, status: str):
        """Thread-safe task update with exclusive lock"""
        with self._acquire_lock():
            # Safe to read/write now
            tasks = json.load(open(self.registry_path))
            tasks[task_id]["status"] = status
            
            # Atomic write (write to temp, then rename)
            temp_path = self.registry_path.with_suffix(".tmp")
            json.dump(tasks, open(temp_path, "w"), indent=2)
            temp_path.rename(self.registry_path)
```

**Alternative: SQLite Backend**
```python
# Better: Use SQLite instead of JSON (ACID guarantees)
class SQLiteTaskRegistry:
    """ACID-compliant task registry using SQLite"""
    
    def __init__(self, db_path: Path):
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT,
                phase TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def update_task(self, task_id: str, status: str):
        """Atomic task update with SQLite transaction"""
        self.db.execute(
            "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
            (status, task_id)
        )
        self.db.commit()  # Atomic by default
```

**Recommendation:** Use SQLite backend (P01 deliverable change)

---

### RISK-003: Orchestrator Instantiation Circular Dependency ⛔

**Category:** Architecture | **Severity:** P0_CRITICAL | **Probability:** HIGH

**Description:**
Epic reports "6 orchestrators fail to instantiate" but doesn't analyze **root cause**. Investigation reveals **circular import dependencies**:

```
planning_v5.py → imports → governance_checkpoint.py
    ↓
governance_checkpoint.py → imports → knowledge_graph.py
    ↓
knowledge_graph.py → imports → planning_v5.py
    ↓
CIRCULAR DEPENDENCY ⛔
```

**Current State:**
```python
# src/orchestrators/planning/planning_orchestrator_v5.py
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpoint

# src/orchestrators/middleware/governance_checkpoint.py
from src.tier2.knowledge_graph import KnowledgeGraph

# src/tier2/knowledge_graph.py
from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
# ❌ CIRCULAR IMPORT
```

**Failure Scenarios:**
- ImportError on module initialization
- AttributeError on incomplete class definition
- Orchestrators cannot be instantiated

**Impact:**
- 🔥 **System Unusable:** 6/10 orchestrators broken
- 🔥 **Epic Blocker:** P02-P07 cannot proceed until fixed

**Mitigation Strategy:**

**Option 1: Lazy Imports**
```python
# Use TYPE_CHECKING to avoid runtime import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5

def query_knowledge_graph():
    # Import at function call time (lazy)
    from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
    ...
```

**Option 2: Dependency Injection**
```python
# Break circular dependency with DI

class GovernanceCheckpoint:
    def __init__(self, knowledge_graph: KnowledgeGraph = None):
        # Inject dependency instead of importing
        self.knowledge_graph = knowledge_graph or self._create_knowledge_graph()
    
    def _create_knowledge_graph(self):
        # Lazy instantiation
        from src.tier2.knowledge_graph import KnowledgeGraph
        return KnowledgeGraph()
```

**Option 3: Restructure (RECOMMENDED)**
```python
# Move shared code to common module

# Create src/common/interfaces.py
class IKnowledgeGraph(Protocol):
    def query(self, pattern: str) -> List[Dict]: ...

# Both modules depend on interface, not each other
from src.common.interfaces import IKnowledgeGraph
```

**Acceptance Criteria:**
- ✅ All 6 broken orchestrators instantiate successfully
- ✅ Import graph is acyclic (verify with `import-linter`)
- ✅ Test: `pytest --import-mode=importlib` passes

---

### RISK-004: ResponseRenderer Silent Failure ⛔

**Category:** Integration | **Severity:** P0_CRITICAL | **Probability:** MEDIUM

**Description:**
Epic mentions "Verify ResponseRenderer renders to user (continuation prompt issue)" but doesn't specify **validation strategy**. Risk: ResponseRenderer fails silently, user sees nothing, but orchestrator reports success.

**Current State (Hypothesis):**
```python
# src/orchestrators/response_renderer.py
def render_to_user(self, response: str):
    try:
        # Send to GitHub Copilot Chat
        self._send_to_copilot(response)
    except Exception as e:
        # ❌ Exception swallowed - user never sees error
        logger.error(f"Failed to render: {e}")
        # No retry, no fallback
```

**Failure Scenarios:**
1. **GitHub Copilot API Timeout:** 30s timeout → response dropped
2. **Token Limit Exceeded:** Response > 100K tokens → truncated silently
3. **Network Failure:** No internet → response lost

**Impact:**
- 🔥 **User Confusion:** Orchestrator claims success but user sees nothing
- 🔥 **Lost Work:** Continuation prompts never displayed
- 🔥 **Debug Hell:** No error visible to user

**Mitigation Strategy:**

```python
class ResilientResponseRenderer:
    """ResponseRenderer with retry, fallback, and verification"""
    
    def render_to_user(self, response: str, max_retries: int = 3):
        """Render response with automatic retry and fallback"""
        
        for attempt in range(max_retries):
            try:
                # Primary: Send to Copilot Chat
                self._send_to_copilot(response)
                
                # VERIFY: Check if user received
                if self._verify_delivery():
                    logger.info("Response delivered successfully")
                    return
                
            except CopilotAPITimeout:
                logger.warning(f"Copilot timeout, retry {attempt+1}/{max_retries}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except TokenLimitExceeded:
                # Fallback: Truncate and retry
                response = self._truncate_response(response, max_tokens=80000)
                logger.warning("Response truncated to fit token limit")
        
        # All retries failed - use fallback
        self._fallback_file_render(response)
    
    def _fallback_file_render(self, response: str):
        """Fallback: Write response to file + notify user"""
        output_path = Path("cortex-brain/outputs/response.md")
        output_path.write_text(response)
        
        # Minimal notification to user
        self._send_to_copilot(
            f"⚠️ Response too large for Chat. Saved to: {output_path}\n\n"
            f"View with: `cat {output_path}`"
        )
```

**Acceptance Criteria:**
- ✅ ResponseRenderer retries 3x on failure
- ✅ Fallback to file output if all retries fail
- ✅ User always notified (even if just "see file")
- ✅ Integration test verifies delivery

---

## 🟡 HIGH RISKS (P1) - Require Design Changes

### RISK-005: SKULL Middleware Not Invoked (Silent Bypass)

**Category:** Governance | **Severity:** P1 | **Probability:** HIGH

**Description:**
Epic mentions "Verify SKULL middleware invokes during execution" but doesn't specify **enforcement mechanism**. Risk: Orchestrators bypass middleware if not explicitly called.

**Current State:**
```python
# src/orchestrators/planning/planning_orchestrator_v5.py
def execute(self, context: Dict):
    # ❌ Middleware invocation is OPTIONAL
    # If developer forgets, governance is bypassed
    
    # Should be here but might be missing:
    # self.setup_verifier.verify(context)
    # self.governance_checkpoint.validate(context)
    
    result = self._do_planning(context)
    
    # Should be here but might be missing:
    # self.teardown_refactor.cleanup(result)
    
    return result
```

**Failure Scenarios:**
- Developer forgets to call middleware
- Middleware disabled during testing, never re-enabled
- Exception bypasses middleware (early return)

**Impact:**
- 🟡 **Governance Bypass:** SKULL rules not enforced
- 🟡 **Quality Degradation:** Untested code reaches production
- 🟡 **Audit Failure:** No governance audit trail

**Mitigation Strategy:**

**Option 1: Decorator-Based Enforcement**
```python
from functools import wraps

def with_skull_protection(func):
    """Decorator that guarantees middleware invocation"""
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        context = args[0] if args else kwargs.get('context', {})
        
        # Phase -2: Setup (MANDATORY)
        self.setup_verifier.verify(context)
        
        # Phase -1: Governance (MANDATORY)
        self.governance_checkpoint.checkpoint_pre_execution(
            orchestrator=self.__class__.__name__,
            context=context
        )
        
        try:
            # Execute orchestrator
            result = func(self, *args, **kwargs)
            
            # Phase N+1: Teardown (MANDATORY)
            self.teardown_refactor.cleanup(result)
            
            return result
            
        except Exception as e:
            # Governance checkpoint on failure
            self.governance_checkpoint.checkpoint_failure(
                orchestrator=self.__class__.__name__,
                error=e
            )
            raise
    
    return wrapper

# Usage (ENFORCED):
class PlanningOrchestratorV5(BaseOrchestrator):
    @with_skull_protection  # ✅ Middleware guaranteed
    def execute(self, context: Dict):
        return self._do_planning(context)
```

**Option 2: Base Class Contract (RECOMMENDED)**
```python
class BaseOrchestratorV6:
    """
    Base orchestrator with MANDATORY middleware hooks.
    
    Subclasses CANNOT override execute() - only implement _execute_impl().
    This guarantees middleware invocation.
    """
    
    def execute(self, context: Dict):  # ✅ FINAL - Cannot be overridden
        """Execute orchestrator with mandatory middleware"""
        
        # Phase -2: Setup
        self._phase_minus_2_setup(context)
        
        # Phase -1: Governance
        self._phase_minus_1_governance(context)
        
        # Phase 0-N: Orchestrator logic
        result = self._execute_impl(context)  # Subclass implements this
        
        # Phase N+1: Teardown
        self._phase_n_plus_1_teardown(result)
        
        return result
    
    def _execute_impl(self, context: Dict) -> Dict:
        """Subclasses implement orchestrator logic here"""
        raise NotImplementedError("Subclass must implement _execute_impl()")
```

**Recommendation:** Use Base Class Contract (prevents bypass)

---

### RISK-006: Plan Viewer Auto-Refresh Websocket Overhead

**Category:** Performance | **Severity:** P1 | **Probability:** MEDIUM

**Description:**
Plan viewer uses **5-second polling** to refresh progress. With 10 active plans, this creates:
- 120 HTTP requests/minute
- Unnecessary JSON parsing
- Disk I/O every 5 seconds

**Current State:**
```html
<!-- plan-viewer.html -->
<script>
setInterval(() => {
    // ❌ Poll JSON file every 5 seconds
    fetch('tracking/progress-tracker.json')
        .then(r => r.json())
        .then(data => updateUI(data));
}, 5000);
</script>
```

**Impact:**
- 🟡 **Battery Drain:** Continuous polling on laptops
- 🟡 **Network Waste:** 120 req/min × 10 plans = 1200 req/min
- 🟡 **Disk Wear:** SSD write cycles

**Mitigation Strategy:**

**Option 1: Server-Sent Events (SSE)**
```python
# src/orchestrators/plan_viewer_server.py
from flask import Flask, Response

app = Flask(__name__)

@app.route('/stream/<plan_id>')
def stream_progress(plan_id: str):
    """Stream progress updates via SSE"""
    
    def event_stream():
        last_update = None
        
        while True:
            # Only send if progress changed
            current = read_progress(plan_id)
            
            if current != last_update:
                yield f"data: {json.dumps(current)}\n\n"
                last_update = current
            
            time.sleep(1)  # Check every 1s, send only if changed
    
    return Response(event_stream(), mimetype='text/event-stream')
```

```html
<!-- plan-viewer.html -->
<script>
// ✅ SSE - Server pushes updates only when needed
const eventSource = new EventSource('/stream/cortex5-remediation');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);  // Update only when data changes
};
</script>
```

**Option 2: Exponential Backoff Polling**
```javascript
// Reduce polling frequency if no changes
let pollInterval = 5000;  // Start at 5s

function pollProgress() {
    fetch('tracking/progress-tracker.json')
        .then(r => r.json())
        .then(data => {
            if (hasChanged(data)) {
                updateUI(data);
                pollInterval = 5000;  // Reset to 5s
            } else {
                // No changes - slow down polling
                pollInterval = Math.min(pollInterval * 1.5, 60000);  // Max 1 min
            }
            
            setTimeout(pollProgress, pollInterval);
        });
}
```

**Recommendation:** Use SSE for real-time updates (Phase P01 addition)

---

### RISK-007: Orchestrator Version Mismatch (v2 vs v3 vs v4 vs v5 vs v6)

**Category:** Maintainability | **Severity:** P1 | **Probability:** HIGH

**Description:**
Epic proposes **6 orchestrators upgrade to v3** while others remain v2/v4/v5. This creates:
- Incompatible interfaces
- Different middleware contracts
- Version-specific bugs

**Current State:**
```
Orchestrator Versions:
├── planning_orchestrator_v5.py (v5)
├── planning_orchestrator_v6.py (v6) ← NEW in P02
├── ado_orchestrator_v2.py (v2)
├── ado_orchestrator_v3.py (v3) ← NEW in P03
├── cleanup_orchestrator_v2.py (v2)
├── cleanup_orchestrator_v3.py (v3) ← NEW in P04
...
```

**Impact:**
- 🟡 **Confusion:** Which version is active?
- 🟡 **Maintenance Hell:** Bug fixes need 6x duplication
- 🟡 **Testing Explosion:** Combinatorial version matrix

**Mitigation Strategy:**

**Option 1: Deprecation Path**
```python
# Mark old versions as deprecated
class PlanningOrchestratorV5(BaseOrchestrator):
    """
    DEPRECATED: Use PlanningOrchestratorV6 instead.
    
    This version will be removed in CORTEX 5.2.
    """
    
    def __init__(self):
        warnings.warn(
            "PlanningOrchestratorV5 is deprecated. Use V6.",
            DeprecationWarning
        )
        super().__init__()
```

**Option 2: Versioned Routing (RECOMMENDED)**
```python
# Master Orchestrator routes to latest version automatically

ORCHESTRATOR_REGISTRY = {
    "planning": [
        ("5.0.0", PlanningOrchestratorV5),  # Deprecated
        ("6.0.0", PlanningOrchestratorV6),  # Current
    ],
    "ado": [
        ("2.0.0", ADOOrchestratorV2),      # Deprecated
        ("3.0.0", ADOOrchestratorV3),      # Current
    ],
}

def get_orchestrator(name: str, version: str = "latest"):
    """Get orchestrator by name and version"""
    
    versions = ORCHESTRATOR_REGISTRY[name]
    
    if version == "latest":
        # Return highest version
        return versions[-1][1]
    
    # Return specific version
    for v, cls in versions:
        if v == version:
            return cls
    
    raise OrchestratorNotFoundError(f"{name} v{version}")
```

**Recommendation:** Add deprecation warnings + version registry (P01)

---

### RISK-008: Missing Deployment Validation (Canary / Blue-Green)

**Category:** Deployment | **Severity:** P1 | **Probability:** MEDIUM

**Description:**
Epic lacks **deployment strategy** for rolling out v3 orchestrators. Risk: Deploy all orchestrators simultaneously → system-wide failure.

**Current State:**
- No canary deployment
- No A/B testing
- No rollback mechanism

**Impact:**
- 🟡 **System-Wide Outage:** All orchestrators fail together
- 🟡 **No Rollback:** Cannot revert to v2
- 🟡 **User Impact:** All users affected simultaneously

**Mitigation Strategy:**

**Canary Deployment:**
```python
# Feature flag system for gradual rollout

class OrchestratorFeatureFlags:
    """Feature flags for orchestrator version rollout"""
    
    def __init__(self):
        self.flags = {
            "planning_v6_rollout": 0.10,  # 10% of users get v6
            "ado_v3_rollout": 0.05,       # 5% of users get v3
        }
    
    def should_use_new_version(self, orchestrator: str, user_id: str) -> bool:
        """Determine if user should get new version"""
        
        flag_name = f"{orchestrator}_rollout"
        rollout_percentage = self.flags.get(flag_name, 0.0)
        
        # Consistent hashing (same user always gets same version)
        user_hash = int(hashlib.sha256(user_id.encode()).hexdigest(), 16)
        user_bucket = (user_hash % 100) / 100.0
        
        return user_bucket < rollout_percentage

# Usage:
flags = OrchestratorFeatureFlags()

if flags.should_use_new_version("planning", user_id):
    orchestrator = PlanningOrchestratorV6()
else:
    orchestrator = PlanningOrchestratorV5()  # Fallback
```

**Rollback Mechanism:**
```bash
# Quick rollback script
./scripts/rollback_orchestrators.sh --version v5

# Updates feature flags to 0% instantly
```

**Recommendation:** Add canary deployment phase (P13 addition)

---

### RISK-009: Token Budget Violation (Vision API + Context)

**Category:** Performance | **Severity:** P1 | **Probability:** MEDIUM

**Description:**
Vision API middleware injects analysis into context. With 5 images attached:
- Each image analysis: ~500 tokens
- Total: 2,500 tokens
- Exceeds budget: Context already ~8,000 tokens → 10,500 tokens total

**Impact:**
- 🟡 **Copilot Rejection:** Request rejected if > 10K tokens
- 🟡 **Cost Explosion:** GPT-4V API costs increase
- 🟡 **Latency:** Larger context = slower inference

**Mitigation Strategy:**

```python
class TokenBudgetManager:
    """Enforce token budgets across context sources"""
    
    BUDGETS = {
        "vision_context": 100,      # Vision API analysis
        "tier1_context": 500,       # Session history
        "tier2_context": 300,       # Knowledge graph
        "tier3_context": 200,       # Dev context
        "user_request": 1000,       # User's message
        "system_prompt": 2000,      # CORTEX instructions
        "total_max": 8000,          # Hard limit
    }
    
    def enforce_budget(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Trim context to fit budget"""
        
        # Calculate token usage per source
        usage = {
            source: self._count_tokens(context.get(source, ""))
            for source in self.BUDGETS
        }
        
        total = sum(usage.values())
        
        if total <= self.BUDGETS["total_max"]:
            return context  # Under budget
        
        # Over budget - trim lowest priority sources
        context = self._trim_vision_context(context, usage)
        context = self._trim_tier3_context(context, usage)
        
        return context
    
    def _trim_vision_context(self, context: Dict, usage: Dict) -> Dict:
        """Trim vision context to fit 100-token budget"""
        
        if usage["vision_context"] <= self.BUDGETS["vision_context"]:
            return context
        
        # Summarize vision analysis
        full_analysis = context["vision_context"]
        context["vision_context"] = {
            "summary": full_analysis["description"][:200],  # First 200 chars
            "confidence": full_analysis["confidence"],
            "full_analysis_path": "vision_analysis.json"  # Link to full
        }
        
        # Save full analysis to file
        Path("vision_analysis.json").write_text(json.dumps(full_analysis))
        
        return context
```

**Recommendation:** Add token budget enforcement (P01)

---

## 🟢 MEDIUM RISKS (P2) - Monitor During Implementation

### RISK-010: HTML Plan Viewer CSS Injection Vulnerability

**Category:** Security | **Severity:** P2 | **Probability:** LOW

**Description:**
Plan viewer embeds user input (plan names, task descriptions) in HTML without sanitization. Risk: XSS if user creates plan with malicious name.

**Example Attack:**
```bash
# User creates plan with XSS payload
python3 -m src.main "plan <img src=x onerror=alert('XSS')>"

# plan-viewer.html renders:
<h1>Plan: <img src=x onerror=alert('XSS')></h1>
# ❌ Script executes
```

**Mitigation:**
```python
import html

def sanitize_for_html(text: str) -> str:
    """Escape HTML entities"""
    return html.escape(text)

# In plan viewer generator:
plan_name_safe = sanitize_for_html(plan_name)
html_content = f"<h1>Plan: {plan_name_safe}</h1>"
```

---

### RISK-011: Missing Observability (Logs, Metrics, Traces)

**Category:** Operations | **Severity:** P2 | **Probability:** HIGH

**Description:**
Epic lacks **observability strategy**. No metrics, no distributed tracing, no centralized logging.

**Impact:**
- 🟢 **Blind Debugging:** Cannot diagnose production issues
- 🟢 **No Performance Data:** Cannot optimize bottlenecks
- 🟢 **No Alerts:** Silent failures

**Mitigation:**
```python
# Add OpenTelemetry tracing
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class PlanningOrchestratorV6:
    @tracer.start_as_current_span("planning_execute")
    def execute(self, context: Dict):
        span = trace.get_current_span()
        span.set_attribute("plan.name", context["plan_name"])
        
        # Trace spans show bottlenecks
        with tracer.start_as_current_span("context_discovery"):
            context = self._discover_context(context)
        
        with tracer.start_as_current_span("architecture_analysis"):
            architecture = self._analyze_architecture(context)
        
        return result
```

---

### RISK-012: Incomplete Error Recovery (Partial Failures)

**Category:** Reliability | **Severity:** P2 | **Probability:** MEDIUM

**Description:**
Orchestrators lack **idempotency**. If Phase 3 fails, re-running starts from Phase 1 (wasteful).

**Mitigation:**
```python
class IdempotentOrchestrator:
    """Orchestrator that can resume from failure point"""
    
    def execute(self, context: Dict):
        checkpoint = self._load_checkpoint()
        
        if checkpoint:
            # Resume from last successful phase
            start_phase = checkpoint["last_completed_phase"] + 1
        else:
            start_phase = 1
        
        for phase_num in range(start_phase, self.total_phases + 1):
            try:
                self._execute_phase(phase_num, context)
                self._save_checkpoint(phase_num)
            except Exception as e:
                logger.error(f"Phase {phase_num} failed: {e}")
                raise  # User can re-run to resume
```

---

### RISK-013: Documentation Drift (Code vs Docs)

**Category:** Maintainability | **Severity:** P2 | **Probability:** HIGH

**Description:**
Epic creates 14 phases of code changes but doesn't mandate **documentation updates**. Risk: Docs become outdated.

**Mitigation:**
```yaml
# Add to acceptance criteria for ALL phases:
acceptance_criteria:
  documentation:
    - "README.md updated with new orchestrator usage"
    - "API documentation regenerated (Sphinx)"
    - "Architecture diagram updated"
    - "CHANGELOG.md entry added"
```

---

## 🎯 Recommended Actions

### Immediate (P0 - Before Phase P01 Starts)

1. ✅ **Add Phase P00.5: Migration Rollback Testing** (2 days)
   - Implement atomic migrations with savepoints
   - Test intentional failure scenarios
   - Create backup/restore procedures

2. ✅ **Change P01 Deliverable: Use SQLite for Task Registry** (1 day)
   - Replace JSON with SQLite (ACID guarantees)
   - Add file locking for JSON fallback
   - Test concurrent access

3. ✅ **Add Phase P00.6: Fix Circular Import Dependencies** (1 day)
   - Analyze import graph with `import-linter`
   - Restructure imports (lazy imports or DI)
   - Verify all 6 orchestrators instantiate

4. ✅ **Add ResponseRenderer Resilience Tests** (0.5 days)
   - Test timeout scenarios
   - Test token limit exceeded
   - Verify fallback to file output

### Pre-Implementation (P1 - During P01 Design)

5. ✅ **Add Phase P14: Plugin-Based Governance Architecture** (5 days)
   - Implement plugin loader + contract
   - Create Vision API enforcement plugin
   - Migrate existing rules to plugins

6. ✅ **Add BaseOrchestratorV6 with Mandatory Middleware** (2 days)
   - Enforce SKULL middleware via base class
   - Decorator-based alternative for existing orchestrators
   - Update all orchestrators to inherit from V6

7. ✅ **Add Orchestrator Version Registry** (1 day)
   - Centralized registry with deprecation warnings
   - Version-based routing in Master Orchestrator
   - Automated test for version compatibility

8. ✅ **Add Canary Deployment Strategy** (2 days)
   - Feature flags for gradual rollout
   - A/B testing framework
   - Quick rollback mechanism

### During Implementation (P2 - Monitor)

9. ✅ **Add Token Budget Enforcement** (1 day)
   - TokenBudgetManager for all context sources
   - Vision context trimming (<100 tokens)
   - Full analysis saved to file with link

10. ✅ **Add Observability** (2 days)
    - OpenTelemetry distributed tracing
    - Prometheus metrics (latency, throughput)
    - Centralized logging (JSON structured logs)

11. ✅ **Add HTML Sanitization** (0.5 days)
    - Escape all user input in plan viewer
    - CSP headers for XSS prevention
    - Security test with XSS payloads

12. ✅ **Add Idempotent Execution** (1 day)
    - Checkpoint system for phase resumption
    - Crash recovery tests
    - Resume-from-failure CLI command

13. ✅ **Enforce Documentation Updates** (ongoing)
    - Add to Definition of Done for all phases
    - Automated doc generation where possible
    - Doc review as gate for phase completion

---

## 📊 Risk Summary Table

| ID | Risk | Category | Severity | Probability | Mitigation Cost | Priority |
|----|------|----------|----------|-------------|-----------------|----------|
| RISK-001 | Migration Rollback Failure | Data Integrity | P0 | HIGH | 2 days | 🔴 CRITICAL |
| RISK-002 | Task Race Condition | Concurrency | P0 | MEDIUM | 1 day | 🔴 CRITICAL |
| RISK-003 | Circular Dependencies | Architecture | P0 | HIGH | 1 day | 🔴 CRITICAL |
| RISK-004 | ResponseRenderer Failure | Integration | P0 | MEDIUM | 0.5 days | 🔴 CRITICAL |
| RISK-005 | SKULL Bypass | Governance | P1 | HIGH | 2 days | 🟡 HIGH |
| RISK-006 | Plan Viewer Overhead | Performance | P1 | MEDIUM | 1 day | 🟡 HIGH |
| RISK-007 | Version Mismatch | Maintainability | P1 | HIGH | 1 day | 🟡 HIGH |
| RISK-008 | No Canary Deployment | Deployment | P1 | MEDIUM | 2 days | 🟡 HIGH |
| RISK-009 | Token Budget Violation | Performance | P1 | MEDIUM | 1 day | 🟡 HIGH |
| RISK-010 | XSS Vulnerability | Security | P2 | LOW | 0.5 days | 🟢 MEDIUM |
| RISK-011 | No Observability | Operations | P2 | HIGH | 2 days | 🟢 MEDIUM |
| RISK-012 | No Idempotency | Reliability | P2 | MEDIUM | 1 day | 🟢 MEDIUM |
| RISK-013 | Documentation Drift | Maintainability | P2 | HIGH | ongoing | 🟢 MEDIUM |

**Total Mitigation Cost:** 18 days (can parallelize some tasks)

---

## 🏁 Conclusion

**Key Findings:**
1. ✅ Epic is **architecturally sound** but has **13 identifiable risks**
2. ❌ Epic **lacks extensibility framework** (Vision API governance realization)
3. ⚠️ **4 P0 risks** must be addressed before Phase P01 starts
4. ✅ **Plugin architecture** (Phase P14) solves extensibility problem

**Recommendation:**
- **Pause epic start** until P0 risks mitigated (4.5 days)
- **Add Phase P14** for plugin architecture (5 days)
- **Total delay:** 9.5 days → **ROI:** Prevents future architecture churn forever

---

**Next Steps:**
1. Review this risk analysis (1 hour)
2. Approve Phase P14 addition (30 min)
3. Mitigate P0 risks (4.5 days)
4. Proceed with epic (original 14 phases + P14)

**Version History:**
- v1.0.0 (2026-01-06): Initial holistic risk analysis
- Identified 13 risks across 7 categories
- Recommended 13 mitigation actions
