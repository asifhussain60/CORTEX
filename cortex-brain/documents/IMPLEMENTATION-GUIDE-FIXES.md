# CORTEX 6.0 - Critical Fixes Implementation Guide
**Date:** January 11, 2026  
**Purpose:** Step-by-step guide to implement all three critical fixes  
**Estimated Time:** 9-12 hours total

---

## Overview: The Three Critical Fixes

| Priority | AC-ID | Issue | Fix | Time |
|----------|-------|-------|-----|------|
| 1 | AC-TODO-001/003/004 | Tasks not persisted, no dependency resolution | Implement complete TodoManager | 3h |
| 2 | AC-ORCH-006 | MasterOrchestrator not integrated with TodoManager | Connect execute() to TodoManager | 3h |
| 3 | AC-ORCH-004 | Correlation ID not propagated | Add middleware + context var | 2h |

---

## Fix 1: Complete TodoManager Implementation (3 hours)

### Step 1.1: Add SQLite Schema Migration

**File:** `src/orchestrators/master/todo_manager.py`

Replace the current `__init__` method with database initialization:

```python
def __init__(self, db_path: Optional[str] = None):
    """Initialize with SQLite persistence."""
    self.logger = logging.getLogger("cortex.orchestrators.master.todo_manager")
    self.tasks: Dict[str, Task] = {}
    self.db_path = db_path or ":memory:"
    
    # Initialize database schema
    self._init_db()
    
    self.logger.info(f"TodoManager initialized with DB at {self.db_path}")

def _init_db(self):
    """Initialize SQLite database."""
    import sqlite3
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT,
            ac_id TEXT,
            error_reason TEXT
        )
    """)
    
    # Task dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_dependencies (
            task_id TEXT NOT NULL,
            depends_on_id TEXT NOT NULL,
            PRIMARY KEY (task_id, depends_on_id),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    
    conn.commit()
    conn.close()
```

### Step 1.2: Implement Persistence Methods

Add these methods to TodoManager:

```python
def _persist_task(self, task: Task):
    """Save task to database."""
    import sqlite3, json
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO tasks (
            id, name, description, status, priority,
            created_at, updated_at, metadata, ac_id, error_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task.id,
        task.name,
        task.description,
        task.status.value,
        task.priority.value,
        task.created_at.isoformat(),
        task.updated_at.isoformat(),
        json.dumps(task.metadata),
        task.ac_id,
        task.error_reason
    ))
    
    # Delete old dependencies
    cursor.execute("DELETE FROM task_dependencies WHERE task_id = ?", (task.id,))
    
    # Add new dependencies
    for dep_id in task.dependencies:
        cursor.execute("""
            INSERT INTO task_dependencies (task_id, depends_on_id)
            VALUES (?, ?)
        """, (task.id, dep_id))
    
    conn.commit()
    conn.close()

def load_from_db(self):
    """Load all tasks from database (session resumption)."""
    import sqlite3, json
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks")
    for row in cursor.fetchall():
        # Get dependencies
        cursor.execute("""
            SELECT depends_on_id FROM task_dependencies WHERE task_id = ?
        """, (row['id'],))
        deps = [d[0] for d in cursor.fetchall()]
        
        task = Task(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            status=TaskStatus(row['status']),
            priority=TaskPriority(row['priority']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            dependencies=deps,
            ac_id=row['ac_id'],
            error_reason=row['error_reason']
        )
        self.tasks[task.id] = task
    
    conn.close()
    self.logger.info(f"Loaded {len(self.tasks)} tasks from database")
```

### Step 1.3: Implement Dependency Resolution

Add these methods to TodoManager:

```python
def get_executable_tasks(self) -> List[Task]:
    """Get tasks ready to execute (dependencies satisfied)."""
    executable = []
    
    for task in self.tasks.values():
        if task.status != TaskStatus.PENDING:
            continue
        
        # Check dependencies
        all_complete = all(
            self.tasks[dep_id].status == TaskStatus.COMPLETE
            for dep_id in task.dependencies
            if dep_id in self.tasks
        )
        
        if all_complete:
            executable.append(task)
    
    # Sort by priority
    executable.sort(key=lambda t: t.priority.value)
    return executable

def resolve_dependencies_topological(self) -> List[List[str]]:
    """Topological sort of tasks (checks for cycles)."""
    visited = set()
    visiting = set()
    result = []
    
    def visit(task_id: str):
        if task_id in visited:
            return
        if task_id in visiting:
            raise ValueError(f"Circular dependency: {task_id}")
        
        visiting.add(task_id)
        task = self.tasks.get(task_id)
        if task:
            for dep_id in task.dependencies:
                visit(dep_id)
        visiting.remove(task_id)
        visited.add(task_id)
        result.append(task_id)
    
    for task_id in self.tasks.keys():
        visit(task_id)
    
    # Group by depth
    depth_map = {}
    for task_id in result:
        max_depth = 0
        task = self.tasks.get(task_id)
        if task:
            for dep_id in task.dependencies:
                max_depth = max(max_depth, depth_map.get(dep_id, 0))
        depth_map[task_id] = max_depth + 1
    
    # Return grouped by level
    levels = {}
    for task_id, depth in depth_map.items():
        if depth not in levels:
            levels[depth] = []
        levels[depth].append(task_id)
    
    return [levels[d] for d in sorted(levels.keys())]

def validate_dependencies(self) -> Tuple[bool, List[str]]:
    """Validate no missing tasks or cycles."""
    errors = []
    
    for task_id, task in self.tasks.items():
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                errors.append(f"Task {task_id} depends on missing {dep_id}")
    
    try:
        self.resolve_dependencies_topological()
    except ValueError as e:
        errors.append(str(e))
    
    return len(errors) == 0, errors
```

### Step 1.4: Update create_task() and update_task_status()

Modify existing methods to call `_persist_task()`:

```python
def create_task(
    self,
    name: str,
    description: Optional[str] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    metadata: Optional[Dict[str, Any]] = None,
    dependencies: Optional[List[str]] = None,
    ac_id: Optional[str] = None
) -> Task:
    """Create task and persist to DB."""
    now = datetime.utcnow()
    task_id = str(uuid.uuid4())
    
    task = Task(
        id=task_id,
        name=name,
        description=description,
        status=TaskStatus.PENDING,
        priority=priority or TaskPriority.MEDIUM,
        created_at=now,
        updated_at=now,
        metadata=metadata or {},
        dependencies=dependencies or [],
        ac_id=ac_id
    )
    
    self.tasks[task_id] = task
    self._persist_task(task)  # ← NEW: Persist immediately
    
    self.logger.info(f"Task created: {name}", extra={"task_id": task_id})
    return task

def update_task_status(
    self,
    task_id: str,
    status: TaskStatus,
    error_reason: Optional[str] = None
) -> bool:
    """Update task status and persist."""
    task = self.tasks.get(task_id)
    if not task:
        return False
    
    old_status = task.status
    task.status = status
    task.updated_at = datetime.utcnow()
    if error_reason:
        task.error_reason = error_reason
    
    self._persist_task(task)  # ← NEW: Persist change
    
    self.logger.info(
        f"Task status: {old_status.value} → {status.value}",
        extra={"task_id": task_id}
    )
    return True
```

### Step 1.5: Run Tests

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Run TodoManager tests only
python3 -m pytest tests/infrastructure/test_todo_manager.py -v

# Should see:
# ✅ test_create_task PASSED
# ✅ test_update_task_status PASSED
# ✅ test_get_executable_tasks PASSED
# ✅ test_topological_sort PASSED
# ✅ ... (15 total)
```

---

## Fix 2: Connect MasterOrchestrator to TodoManager (3 hours)

### Step 2.1: Add _evaluate_request() Method

**File:** `src/orchestrators/master_orchestrator.py`

Add this method to MasterOrchestrator class:

```python
def _evaluate_request(
    self,
    request: str,
    unified_rules: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Evaluate request against governance rules.
    Returns list of required_actions.
    """
    
    actions = []
    
    # Step 1: Check SKULL rules (tier 0)
    for rule in unified_rules.get('skull_rules', []):
        if rule.get('tier') == 0:
            # Check if request violates this SKULL rule
            if self._check_skull_violation(request, rule):
                self.logger.warning(
                    f"SKULL rule violated: {rule['id']}",
                    extra={'rule': rule['name']}
                )
                # Return empty actions (block request)
                return []
    
    # Step 2: Determine action type from request
    request_lower = request.lower()
    
    if any(word in request_lower for word in ['plan', 'design', 'architect']):
        actions.append({
            'id': str(uuid.uuid4()),
            'name': 'Generate Plan',
            'type': 'planning',
            'priority': 1,
            'ac_id': 'AC-PLAN-001'
        })
    
    elif any(word in request_lower for word in ['test', 'validate']):
        actions.append({
            'id': str(uuid.uuid4()),
            'name': 'Run Tests',
            'type': 'testing',
            'priority': 2,
            'ac_id': 'AC-TDD-003'
        })
    
    elif any(word in request_lower for word in ['implement', 'create', 'build']):
        actions.append({
            'id': str(uuid.uuid4()),
            'name': 'Implement Feature',
            'type': 'implementation',
            'priority': 2,
            'ac_id': 'AC-TDD-004'
        })
    
    # Step 3: Add governance rules applied to each action
    for action in actions:
        action['governance_rules_applied'] = [
            r['id'] for r in unified_rules.get('all_rules', [])
        ]
    
    return actions

def _check_skull_violation(self, request: str, rule: Dict) -> bool:
    """Check if request violates a SKULL rule."""
    rule_id = rule.get('id')
    
    # CORE-019: TDD Enforcement - no direct coding
    if rule_id == 'CORE-019':
        if any(word in request.lower() for word in ['write code', 'code directly', 'direct implementation']):
            return True
    
    # Add more SKULL rule checks as needed
    
    return False
```

### Step 2.2: Update handle_request() → execute()

Replace the simple `handle_request()` method with complete `execute()`:

```python
def execute(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute request with full governance-to-todo pipeline.
    AC-ORCH-006: MasterOrchestrator is IN CHARGE
    """
    
    # Setup context
    correlation_id = str(uuid.uuid4())
    context = context or {}
    context.update({
        'request': request,
        'correlation_id': correlation_id,
        'timestamp': datetime.utcnow()
    })
    
    self.logger.info(
        "MasterOrchestrator.execute() starting",
        extra={'correlation_id': correlation_id, 'request': request[:100]}
    )
    
    try:
        # ===== STEP 1: Load Governance =====
        self.logger.info("Loading governance rules", extra={'correlation_id': correlation_id})
        unified_rules = self.governance_merger.merge_all_tiers()
        
        # ===== STEP 2: Evaluate Request =====
        self.logger.info("Evaluating request", extra={'correlation_id': correlation_id})
        required_actions = self._evaluate_request(request, unified_rules)
        
        if not required_actions:
            self.logger.warning(
                "Request blocked by governance",
                extra={'correlation_id': correlation_id}
            )
            return {
                'correlation_id': correlation_id,
                'success': False,
                'error': 'Request violates governance rules'
            }
        
        # ===== STEP 3: Create Tasks =====
        self.logger.info(
            "Creating tasks from required_actions",
            extra={'correlation_id': correlation_id, 'action_count': len(required_actions)}
        )
        
        task_ids = []
        for action in required_actions:
            task = self.todo_manager.create_task(
                name=action['name'],
                priority=TaskPriority(action.get('priority', 3)),
                ac_id=action.get('ac_id'),
                metadata={
                    'action_id': action['id'],
                    'governance_rules': action.get('governance_rules_applied', []),
                    'correlation_id': correlation_id
                }
            )
            task_ids.append(task.id)
        
        # ===== STEP 4: Execute Tasks =====
        self.logger.info(
            "Executing tasks in dependency order",
            extra={'correlation_id': correlation_id, 'task_count': len(task_ids)}
        )
        
        results = {}
        completed_count = 0
        
        while True:
            # Get executable tasks (dependencies satisfied)
            executable = self.todo_manager.get_executable_tasks()
            if not executable:
                break
            
            for task in executable:
                self.logger.info(
                    "Task executing",
                    extra={'correlation_id': correlation_id, 'task_id': task.id, 'name': task.name}
                )
                
                try:
                    # Mark in progress
                    self.todo_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                    
                    # Execute task
                    result = self._execute_task(task, context)
                    results[task.id] = result
                    
                    # Mark complete
                    self.todo_manager.update_task_status(task.id, TaskStatus.COMPLETE)
                    completed_count += 1
                    
                    self.logger.info(
                        "Task complete",
                        extra={'correlation_id': correlation_id, 'task_id': task.id}
                    )
                    
                except Exception as e:
                    self.logger.error(
                        "Task failed",
                        extra={'correlation_id': correlation_id, 'task_id': task.id, 'error': str(e)}
                    )
                    self.todo_manager.update_task_status(
                        task.id,
                        TaskStatus.FAILED,
                        error_reason=str(e)
                    )
        
        return {
            'correlation_id': correlation_id,
            'success': completed_count == len(task_ids),
            'task_count': len(task_ids),
            'tasks_completed': completed_count,
            'results': results
        }
        
    except Exception as e:
        self.logger.error(
            "MasterOrchestrator.execute() failed",
            extra={'correlation_id': correlation_id, 'error': str(e)}
        )
        raise
```

### Step 2.3: Add _execute_task() Method

```python
def _execute_task(self, task: Task, context: Dict) -> Dict[str, Any]:
    """Execute a single task via appropriate orchestrator."""
    
    ac_id = task.ac_id or 'AC-UNKNOWN'
    
    # Route to appropriate orchestrator
    if 'plan' in task.name.lower():
        orchestrator = self.registry.get('planning_orchestrator')
    elif 'test' in task.name.lower():
        orchestrator = self.registry.get('tdd_orchestrator')
    else:
        orchestrator = self.registry.get('default_orchestrator')
    
    if not orchestrator:
        raise ValueError(f"No orchestrator for task: {task.name}")
    
    # Execute with context
    result = orchestrator.execute(
        task.description or task.name,
        context=context
    )
    
    return result
```

### Step 2.4: Run Integration Tests

```bash
# Run MasterOrchestrator tests
python3 -m pytest tests/orchestrators/test_master_orchestrator.py -v -k "governance or todo"

# Should show tests passing
```

---

## Fix 3: Add Correlation ID Middleware (2 hours)

### Step 3.1: Create Middleware File

**File:** `src/orchestrators/middleware/correlation_id_middleware.py`

```python
"""Correlation ID Middleware - AC-ORCH-004"""

import logging
import uuid
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Thread-safe context variable
_correlation_id_context: ContextVar[str] = ContextVar(
    'correlation_id',
    default=None
)


class CorrelationIdMiddleware:
    """Middleware for correlation ID injection and validation."""
    
    PRIORITY = 1  # Execute first
    
    def __init__(self):
        self.logger = logging.getLogger("cortex.middleware.correlation_id")
    
    def pre_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inject correlation_id."""
        correlation_id = context.get('correlation_id')
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            context['correlation_id'] = correlation_id
        
        _correlation_id_context.set(correlation_id)
        
        self.logger.debug(
            "Correlation ID injected",
            extra={'correlation_id': correlation_id}
        )
        
        return context
    
    def post_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify correlation_id propagated."""
        correlation_id = context.get('correlation_id')
        
        if not correlation_id:
            self.logger.warning("Correlation ID missing from context")
        
        return context


def get_correlation_id() -> Optional[str]:
    """Get current correlation_id."""
    return _correlation_id_context.get()


def set_correlation_id(correlation_id: str):
    """Set correlation_id."""
    _correlation_id_context.set(correlation_id)
```

### Step 3.2: Update EnhancedAuditLogger

**File:** `src/infrastructure/enhanced_audit_logger.py` (modify log() method)

```python
from src.orchestrators.middleware.correlation_id_middleware import get_correlation_id

def log(
    self,
    level: str,
    message: str,
    correlation_id: Optional[str] = None,
    **extra
):
    """Log with auto-injected correlation_id."""
    
    # Get correlation_id from context if not provided
    if not correlation_id:
        correlation_id = get_correlation_id()
    
    # Build audit entry
    audit_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level,
        'message': message,
        'correlation_id': correlation_id,  # ← AUTO-INJECTED
        **extra
    }
    
    # Persist to database
    self._persist_audit_entry(audit_entry)
```

### Step 3.3: Register Middleware in MasterOrchestrator

**File:** `src/orchestrators/master_orchestrator.py`

```python
from src.orchestrators.middleware.correlation_id_middleware import CorrelationIdMiddleware

class MasterOrchestrator:
    def __init__(self, ...):
        # ... existing code ...
        
        # Add correlation ID middleware (first in pipeline)
        self.correlation_id_middleware = CorrelationIdMiddleware()
        
        # Add to pre-execution middlewares
        if not hasattr(self, 'pre_middlewares'):
            self.pre_middlewares = []
        
        self.pre_middlewares.insert(0, self.correlation_id_middleware)
    
    def execute(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute with correlation ID middleware."""
        
        context = context or {}
        
        # Pre-execution middleware (inject correlation_id)
        for middleware in self.pre_middlewares:
            context = middleware.pre_execution(context)
        
        try:
            # ... existing execute logic ...
            pass
        finally:
            # Post-execution middleware (validate)
            for middleware in self.post_middlewares:
                context = middleware.post_execution(context)
```

### Step 3.4: Run Middleware Tests

```bash
python3 -m pytest tests/orchestrators/test_correlation_id_middleware.py -v

# Should show 4 tests passing
```

---

## Final Validation

### Step 4.1: Run All Three Fix Tests

```bash
# Run all tests for the three fixes
python3 -m pytest tests/infrastructure/test_todo_manager.py \
                   tests/orchestrators/test_master_orchestrator.py \
                   tests/orchestrators/test_correlation_id_middleware.py \
                   -v --tb=short

# Expected: 24/24 passing
```

### Step 4.2: Run Full Test Suite

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

python3 -m pytest tests/ -v --tb=short 2>&1 | tail -50

# Expected: Should see same ~1360 tests passing, plus new tests from fixes
```

### Step 4.3: Verify Audit Evidence

```bash
python3 scripts/audit_based_evidence_validator.py

# Expected improvement:
# Phase 1: Before: 85% verified (29/34)
#          After:  95%+ verified (32+/34)
```

---

## Success Criteria

✅ **AC-TODO-001/003/004 Complete**
- `create_task()` creates tasks in PENDING status
- `update_task_status()` transitions tasks through lifecycle
- `load_from_db()` enables session resumption
- `get_executable_tasks()` respects dependencies
- 15+ tests passing

✅ **AC-ORCH-006 Complete**
- `execute()` merges governance
- `execute()` evaluates request
- `execute()` creates tasks via TodoManager
- `execute()` executes tasks in order
- 5+ tests passing

✅ **AC-ORCH-004 Complete**
- Correlation ID automatically injected
- Correlation ID in all audit events
- No fragmented audit trails
- 4+ tests passing

✅ **Phase 1 Verification: 95%+**
- All critical gaps closed
- Evidence validator shows 95%+ completion
- Ready for Phase 2

---

## Timeline

| Task | Duration | Start | End |
|------|----------|-------|-----|
| Fix 1 (TodoManager) | 3h | Hour 0 | Hour 3 |
| Fix 2 (MasterOrchestrator) | 3h | Hour 3 | Hour 6 |
| Fix 3 (Correlation ID) | 2h | Hour 6 | Hour 8 |
| Testing + Validation | 2h | Hour 8 | Hour 10 |
| Documentation | 1h | Hour 10 | Hour 11 |
| **Total** | **~11h** | | |

---

**Implementation Guide Complete**  
**Ready for Execution**  
**Next: Begin Fix 1 Implementation**
