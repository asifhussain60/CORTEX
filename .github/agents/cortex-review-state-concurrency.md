# CORTEX Review Agent: State Management & Concurrency Flaws

## Distributed State, Race Conditions & Multi-Threading Issues

**Purpose:** Identify state management defects, race conditions, deadlocks, concurrent access issues, and synchronization problems that cause non-deterministic failures.

**Why Critical:** State bugs are the hardest to reproduce and debug. They appear randomly under load but pass in single-threaded tests.

---

## 🚫 FILE PLACEMENT POLICY

**Output Locations:**
- ✅ YAML findings: `_workspaces/roadmap/issues/Findings-STATE-YYYYMMDD.yaml`
- ✅ Terminal: Human-readable output
- ❌ NO `.md` files (report structure in YAML only)

---

## CHECKS PERFORMED

### 1. Race Conditions & Synchronization

**What to look for:**
- Unsynchronized access to shared state
- Check-then-act patterns (TOCTOU - Time of Check to Time of Use)
- Mutable default arguments
- Missing locks on critical sections
- Double-checked locking (broken pattern)

**Search patterns:**
```bash
# Find potential race conditions
grep -rn "self\._\|self\.shared_\|global " cortex/ --include="*.py" | grep -v "__"

# Find unsynchronized dict/list updates
grep -rn "\.append\|\.extend\|\.update\|\.pop\|\.remove" cortex/ --include="*.py" | grep -v "test"

# Find mutable default arguments (race condition vector)
grep -rn "def.*=\[\|def.*={" cortex/ --include="*.py"

# Find threading without locks
grep -rn "Thread\|threading\|concurrent\|asyncio" cortex/ --include="*.py" | grep -v "import"

# Find unprotected atomic operations
grep -rn "if.*exists\|if.*in.*dict\|if.*in.*list" cortex/ --include="*.py" | grep -v "test"
```

**Red Flags:**
```python
# ❌ RACE CONDITION: Check-then-act without atomicity
if key not in self.cache:  # Check happens here
    self.cache[key] = expensive_computation()  # Act here - race window!

# ✅ FIX: Use atomic pattern
with self.cache_lock:
    if key not in self.cache:
        self.cache[key] = expensive_computation()

# ❌ RACE CONDITION: Unsynchronized state update
self.counter += 1  # Non-atomic on CPU level

# ✅ FIX: Use atomic operation
self.counter_lock.acquire()
try:
    self.counter += 1
finally:
    self.counter_lock.release()

# ❌ RACE CONDITION: Mutable default argument
def process_items(items=[]):  # DANGEROUS: shared across all calls!
    items.append(new_item)
    return items

# ✅ FIX: Use None as default
def process_items(items=None):
    if items is None:
        items = []
    items.append(new_item)
    return items
```

**Evidence locations:**
- `cortex/infrastructure/` - Connection pool state
- `cortex/orchestrators/` - Orchestrator state during parallel execution
- `cortex/knowledge/` - Cache implementations
- `cortex/execution/` - Execution state tracking

---

### 2. Deadlock Patterns

**What to look for:**
- Multiple locks acquired in different orders
- Nested lock acquisition
- Locks held during I/O operations
- Missing timeout on lock acquisition
- Circular dependencies between resources

**Search patterns:**
```bash
# Find nested lock usage
grep -rn "with.*lock.*:\|acquire\|release" cortex/ --include="*.py" | grep -B2 -A2 "with.*lock"

# Find file operations that might block
grep -rn "open(\|with open\|\.read\|\.write" cortex/ --include="*.py" | grep -v "test"

# Find database operations without timeout
grep -rn "db\.\|query\(\|execute\(" cortex/ --include="*.py" | grep -v "timeout\|timeout_seconds"

# Find potential circular waits
grep -rn "Event\(\|Condition\(\|Lock\(\|RLock\(" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ DEADLOCK: Locks acquired in different orders
# Thread A: acquire(lock1) -> wait for lock2
# Thread B: acquire(lock2) -> wait for lock1

# ❌ DEADLOCK: Lock held during I/O
with self.lock:
    response = requests.get(url)  # Network I/O can hang indefinitely
    self.cache[url] = response

# ✅ FIX: Release lock before I/O
response = requests.get(url)  # No lock
with self.lock:
    self.cache[url] = response

# ❌ DEADLOCK: No timeout on blocking wait
event.wait()  # Can wait forever

# ✅ FIX: Always use timeout
if not event.wait(timeout=5.0):
    raise TimeoutError("Event never fired")
```

---

### 3. Atomicity Violations

**What to look for:**
- Multi-step operations without atomic boundaries
- State changed between validation and use
- Partial updates leaving system in inconsistent state
- No rollback mechanism for failed multi-step operations

**Search patterns:**
```bash
# Find sequential state modifications
grep -rn "self\.field1 =\|self\.field2 =" cortex/ --include="*.py" | head -20

# Find operations that should be atomic
grep -rn "delete\|insert\|update" cortex/ --include="*.py" | grep -v "test"

# Find missing transaction wrappers
grep -rn "@atomic\|@transaction\|begin\|commit\|rollback" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ ATOMICITY VIOLATION: Partial update
self.user.name = new_name
self.user.email = new_email
self.user.save()  # If this fails, name changed but email didn't

# ✅ FIX: Atomic update
self.user.update(name=new_name, email=new_email)

# ❌ ATOMICITY VIOLATION: Delete without cascade
user = User.get(id)
user.posts.clear()
user.delete()  # If delete fails, posts orphaned

# ✅ FIX: Use database cascade
class User:
    posts = relationship('Post', cascade='all,delete-orphan')
```

---

### 4. Memory Visibility Issues

**What to look for:**
- Thread-local storage misuse
- Cached values not invalidated between threads
- Memory barriers missing
- Volatile field access patterns

**Search patterns:**
```bash
# Find thread-local usage
grep -rn "threading\.local\|ThreadLocal" cortex/ --include="*.py"

# Find module-level caches
grep -rn "^[A-Z_]*_CACHE\|^[A-Z_]*_STORE" cortex/ --include="*.py"

# Find potential stale read patterns
grep -rn "@cache\|@lru_cache\|functools\.cache" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ VISIBILITY ISSUE: Stale cached value
@functools.lru_cache(maxsize=128)
def get_config():
    return CONFIG_GLOBAL  # If CONFIG_GLOBAL changed, cache returns old value

# ✅ FIX: Add cache invalidation
@functools.lru_cache(maxsize=128)
def get_config():
    return CONFIG_GLOBAL

def update_config(new_config):
    global CONFIG_GLOBAL
    CONFIG_GLOBAL = new_config
    get_config.cache_clear()  # Invalidate cache

# ❌ VISIBILITY ISSUE: Thread-local not cleared
thread_local = threading.local()
def process():
    thread_local.user = get_current_user()
    # If thread reused, thread_local.user might have old value

# ✅ FIX: Always clear thread-local
def process():
    try:
        thread_local.user = get_current_user()
        # Process
    finally:
        del thread_local.user  # Clean up
```

---

### 5. Global State Contamination

**What to look for:**
- Module-level mutable state
- Singleton pattern without thread safety
- Global dictionaries/lists modified during execution
- Shared state between test runs

**Search patterns:**
```bash
# Find module-level mutable state
grep -rn "^[a-z_].*= \[\|^[a-z_].*= {" cortex/ --include="*.py" | grep -v "^_"

# Find singleton patterns
grep -rn "class.*Singleton\|_instance\|_shared" cortex/ --include="*.py"

# Find global keyword
grep -rn "^global " cortex/ --include="*.py"

# Find module-level functions that modify state
grep -rn "def.*().*:$" cortex/ --include="*.py" | head -5
```

**Red Flags:**
```python
# ❌ GLOBAL STATE: Module-level mutable dict
CONFIG = {}  # Shared across all imports

def set_config(key, value):
    CONFIG[key] = value

# ✅ FIX: Encapsulate in class
class ConfigManager:
    def __init__(self):
        self.config = {}
    
    def set_config(self, key, value):
        with self.lock:
            self.config[key] = value

# ❌ GLOBAL STATE: Unsafe singleton
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# ✅ FIX: Thread-safe singleton
class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
```

---

### 6. Async/Await Pitfalls

**What to look for:**
- Missing await on async calls
- Blocking operations in async context
- Unhandled task exceptions
- Resource cleanup in async code
- Race conditions in async code

**Search patterns:**
```bash
# Find async functions
grep -rn "async def\|await " cortex/ --include="*.py"

# Find potential missing await
grep -rn "coro\|coroutine\|async_\|\.async_" cortex/ --include="*.py"

# Find blocking calls in async context
grep -rn "requests\.\|\.sleep\|time\.time" cortex/ --include="*.py" | grep -B5 "async def"

# Find unhandled tasks
grep -rn "asyncio\.create_task\|asyncio\.gather" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ ASYNC ISSUE: Missing await
async def fetch_data():
    result = await api_call()  # ✓ Correct
    data = db_query()  # ❌ Should be: data = await db_query()
    return result, data

# ❌ ASYNC ISSUE: Blocking in async
async def process():
    time.sleep(5)  # ❌ Blocks entire event loop
    return True

# ✅ FIX: Use async-friendly sleep
async def process():
    await asyncio.sleep(5)  # ✓ Yields control
    return True

# ❌ ASYNC ISSUE: Unhandled exception in task
async def background_work():
    raise Exception("Unhandled")

asyncio.create_task(background_work())  # Exception never seen!

# ✅ FIX: Handle exceptions
async def background_work():
    try:
        raise Exception("Handled")
    except Exception as e:
        logger.error(f"Background task failed: {e}")
```

---

### 7. Event Ordering Bugs

**What to look for:**
- Assumptions about operation ordering
- Missing event synchronization
- Race between setup and execution
- Out-of-order state transitions

**Search patterns:**
```bash
# Find event-driven patterns
grep -rn "Event\|Signal\|emit\|publish\|subscribe" cortex/ --include="*.py"

# Find state machines
grep -rn "state.*=\|status.*=\|_state" cortex/ --include="*.py" | grep -v "test"

# Find callback handlers
grep -rn "on_\|handle_\|_callback" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ ORDERING: Assumption about execution order
event.set()  # Signal worker thread
result = process()  # Might run before worker thread sees signal

# ✅ FIX: Explicit synchronization
with event_lock:
    event.set()
result = process()

# ❌ ORDERING: State transition without validation
def start_processing():
    self.status = "processing"  # What if already "processing"?

# ✅ FIX: Validate state transitions
def start_processing(self):
    if self.status != "idle":
        raise InvalidStateError(f"Cannot start from {self.status}")
    self.status = "processing"
```

---

## OUTPUT FORMAT

**Create YAML report:** `_workspaces/roadmap/issues/Findings-STATE-YYYYMMDD.yaml`

```yaml
state_management_findings:
  metadata:
    agent: "STATE_MANAGEMENT_AND_CONCURRENCY"
    timestamp: "2026-01-23T14:30:00Z"
    confidence_grades: ["A", "B"]  # No speculation (C-grade)
    evidence_locations: ["cortex/infrastructure/", "cortex/orchestrators/"]

  race_conditions:
    - finding_id: "RC-001"
      severity: "CRITICAL"
      component: "cortex/knowledge/cache.py"
      line_numbers: [45, 47]
      issue: "Check-then-act race condition on cache.get_or_compute()"
      evidence_grade: "A"
      evidence_text: "Lines 45-47 show unguarded access. Lines within critical section."
      reproduction: "Run test_concurrent_cache under ThreadPoolExecutor"
      fix_complexity: "MEDIUM"
      affected_ac_ids: ["AC-CACHE-001", "AC-KNOWLEDGE-002"]

  deadlock_risks:
    - finding_id: "DL-001"
      severity: "HIGH"
      component: "cortex/orchestrators/coordinator.py"
      issue: "Nested lock acquisition without timeout"
      evidence_grade: "B"
      evidence_text: "acquire(lock1) then acquire(lock2) possible in multiple code paths"
      potential_blocking_pairs: ["orchestrator_lock", "phase_lock"]
      fix_complexity: "HIGH"

  atomicity_violations:
    - finding_id: "AV-001"
      severity: "HIGH"
      component: "cortex/execution/executor.py"
      issue: "Multi-step state update without transaction"
      evidence_grade: "A"
      affected_ac_ids: ["AC-EXEC-003"]

  summary:
    critical_findings: 2
    high_findings: 5
    medium_findings: 3
    total_state_bugs: 10
    recommendation: "REMEDIATE CRITICAL before production deployment"
```

---

## DECISION LOGIC

```yaml
decision_tree:
  found_critical_race:
    finding: "Race condition in AC_START lifecycle"
    severity: "CRITICAL"
    action: "BLOCK DEPLOYMENT - Fix immediately"
    timeline: "URGENT (8 hours)"
    
  found_high_deadlock_risk:
    finding: "Locks acquired in different orders"
    severity: "HIGH"
    action: "Fix before deployment"
    timeline: "IMMEDIATE (24 hours)"
    
  found_global_state:
    finding: "Module-level mutable state shared across threads"
    severity: "HIGH"
    action: "Refactor to thread-safe singleton"
    timeline: "IMMEDIATE (24 hours)"
    
  found_async_issues:
    finding: "Missing await on async operations"
    severity: "CRITICAL"
    action: "Fix all instances"
    timeline: "URGENT (4 hours)"
```
