# CORTEX 3.0 - Interrupt-Driven Task Dump System

**Version:** 3.0.0  
**Status:** 🎯 DESIGN PHASE  
**Phase:** Future Enhancement (Post CORTEX 2.0/2.1)  
**Author:** Asif Hussain  
**Date:** November 10, 2025

---

## 📋 Executive Summary

CORTEX 3.0 introduces **Interrupt-Driven Task Capture** - a lightweight, non-blocking system that lets you dump ideas into CORTEX's memory without disrupting active work. Captures happen in <5ms, preserving full context, and integrate seamlessly with CORTEX 2.1's Interactive Planning for later elaboration.

**Key Features:**
- ⚡ **Sub-5ms capture** - Zero disruption to active work
- 🎯 **Context-aware** - Captures what CORTEX was doing when interrupted
- 📋 **Task lists** - Organized by component, priority, timestamp
- 🔄 **2.1 Integration** - Tasks feed into Interactive Planning
- 🧠 **Learning** - Patterns in task dumps improve CORTEX suggestions

---

## 🎯 Problem Statement

### The Scenario

```
YOU: Working on complex refactoring
CORTEX: Updating file (50% complete)
     ↓ Editing line 47 of auth.py
     ↓ Planning to update lines 89-102 next
     
💡 YOUR BRAIN: "Oh! We should add rate limiting to the login endpoint!"

PROBLEM: You can't interrupt CORTEX to record the idea without:
  ❌ Breaking current work flow
  ❌ Losing context of what CORTEX was doing
  ❌ Forgetting the idea if you wait
  ❌ Context-switching penalty
```

### The Solution

```
CORTEX: Updating auth.py (line 47)
     ↓
YOU: "task: add rate limiting to login endpoint"
     ↓ <ENTER>
CORTEX: ✅ Captured. Continuing...
     ↓ Resumes editing line 89-102 (no disruption!)
     
LATER:
YOU: "show my tasks"
CORTEX: 
  📋 TASK DUMP (1 task)
  ───────────────────────────────────────
  1. [ ] Add rate limiting to login endpoint
     Component: authentication
     Context: Was refactoring auth.py
     Captured: 2025-11-10 14:23:15
     Priority: medium (auto-detected)
```

---

## 🏗️ Architecture Design

### Core Principle: **Zero Disruption**

**Design Philosophy:**
1. **Capture First, Process Later** - Write to queue instantly, analyze asynchronously
2. **Context Preservation** - Snapshot CORTEX state at interrupt moment
3. **Minimal Overhead** - Target <5ms for capture operation
4. **No Orchestrator** - Independent lightweight system

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                  INTERRUPT DETECTION                         │
│  Watches for: "task:", "/task", "remember:", "idea:"        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FAST CAPTURE LAYER                         │
│  • SQLite append-only queue (3-5ms write)                   │
│  • Context snapshot (file, line, operation)                 │
│  • Timestamp + auto-ID                                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ASYNC ENRICHMENT (Background)                   │
│  • Component detection (auth, UI, backend, etc.)            │
│  • Priority inference (urgency keywords)                    │
│  • Related task clustering                                  │
│  • Similarity to knowledge graph patterns                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   RETRIEVAL LAYER                            │
│  • "show tasks" - all tasks                                 │
│  • "show tasks for auth" - filtered by component            │
│  • "prioritize tasks" - sorted by importance                │
│  • Integration with 2.1 Interactive Planning                │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Technical Implementation

### 1. Fast Capture Queue (Tier 1.5)

**Location:** `src/tier1/task_queue.py`

**Schema:**
```python
@dataclass
class TaskCapture:
    """Lightweight task capture."""
    task_id: str                    # UUID
    raw_text: str                   # User's exact words
    timestamp: datetime             # Capture moment
    
    # Context snapshot (captured instantly)
    active_file: Optional[str]      # What file CORTEX was editing
    active_line: Optional[int]      # What line number
    active_operation: Optional[str] # "refactoring", "implementing", etc.
    conversation_id: str            # Current conversation
    
    # Enrichment (processed async, initially None)
    component: Optional[str] = None     # "authentication", "UI", etc.
    priority: Optional[str] = None      # "high", "medium", "low"
    related_tasks: List[str] = None     # Similar task IDs
    status: str = "pending"             # "pending", "planned", "done"
```

**API:**
```python
class TaskQueue:
    """Ultra-fast task capture system."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.queue_file = db_path / "task_queue.db"
        self._init_queue()
    
    def capture(
        self, 
        raw_text: str,
        context_snapshot: Dict[str, Any]
    ) -> str:
        """
        Capture task in <5ms.
        
        Args:
            raw_text: User's task description
            context_snapshot: Current CORTEX state
            
        Returns:
            task_id for reference
            
        Performance: <5ms (append-only write)
        """
        import uuid
        from datetime import datetime
        
        task_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        # FAST: Single INSERT, no analysis
        with sqlite3.connect(self.queue_file) as conn:
            conn.execute("""
                INSERT INTO task_queue 
                (task_id, raw_text, timestamp, active_file, 
                 active_line, active_operation, conversation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                raw_text,
                timestamp.isoformat(),
                context_snapshot.get('file'),
                context_snapshot.get('line'),
                context_snapshot.get('operation'),
                context_snapshot.get('conversation_id')
            ))
        
        # Trigger async enrichment (non-blocking)
        self._enqueue_enrichment(task_id)
        
        return task_id
    
    def _enqueue_enrichment(self, task_id: str):
        """Queue task for background processing (non-blocking)."""
        # Add to background worker queue
        # Worker runs in separate thread/process
        pass
```

### 2. Context Snapshot (Zero Cost)

**Already available in CORTEX 2.0:**

```python
class CortexEntry:
    """Entry point already tracks context."""
    
    def _get_context_snapshot(self) -> Dict[str, Any]:
        """
        Get current CORTEX state (already in memory).
        
        No additional cost - this data exists!
        """
        return {
            'file': self._current_file,           # From editor context
            'line': self._current_line,           # From editor API
            'operation': self._active_agent.name, # Current agent
            'conversation_id': self.session.conversation_id
        }
```

### 3. Interrupt Detection (Pattern Matching)

**Location:** `src/entry_point/interrupt_detector.py`

```python
class InterruptDetector:
    """Detects task dump commands in user input."""
    
    INTERRUPT_PATTERNS = [
        r'^task:\s*(.+)',           # "task: add rate limiting"
        r'^/task\s+(.+)',           # "/task add rate limiting"
        r'^remember:\s*(.+)',       # "remember: fix button color"
        r'^idea:\s*(.+)',           # "idea: refactor auth module"
        r'^todo:\s*(.+)',           # "todo: update docs"
    ]
    
    def detect(self, user_input: str) -> Optional[Dict]:
        """
        Check if input is task capture command.
        
        Returns:
            None if not task capture
            Dict with extracted task if match
            
        Performance: <1ms (regex only)
        """
        import re
        
        for pattern in self.INTERRUPT_PATTERNS:
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                return {
                    'is_interrupt': True,
                    'task_text': match.group(1).strip(),
                    'trigger': pattern
                }
        
        return None
```

### 4. Integration with Entry Point

**Location:** `src/entry_point/cortex_entry.py` (minimal changes)

```python
class CortexEntry:
    """Entry point with interrupt support."""
    
    def __init__(self, ...):
        # Existing initialization
        self.task_queue = TaskQueue(db_path)  # NEW
        self.interrupt_detector = InterruptDetector()  # NEW
    
    def process_request(self, user_input: str) -> Dict:
        """Process user request with interrupt detection."""
        
        # 1. Check for interrupt FIRST (before intent routing)
        interrupt = self.interrupt_detector.detect(user_input)
        
        if interrupt:
            # FAST PATH: Capture and return immediately
            context = self._get_context_snapshot()
            task_id = self.task_queue.capture(
                raw_text=interrupt['task_text'],
                context_snapshot=context
            )
            
            return {
                'success': True,
                'action': 'task_captured',
                'task_id': task_id,
                'response': f"✅ Task captured (#{task_id}). Continuing..."
            }
        
        # 2. Normal flow if not interrupt
        return self._normal_processing(user_input)
```

---

## 🎯 User Experience

### Capture During Work

```
USER: "Refactor the authentication module"
CORTEX: 
  ✅ Created work plan (5 steps)
  🔨 Step 1: Extract AuthService class
     • Updating src/auth.py (line 47)...

USER: "task: add rate limiting to login endpoint"

CORTEX: ✅ Captured (#a3f9). Continuing...
     • Updating src/auth.py (line 89)...
     • Moving functions to AuthService...
```

**What happened:**
1. CORTEX was editing line 47
2. Interrupt detected at `task:` keyword
3. Captured in 3ms, returned control
4. CORTEX resumed line 89 (zero disruption!)

### Review Tasks Later

```
USER: "show my tasks"

CORTEX:
  📋 TASK DUMP (3 tasks)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  🔴 HIGH PRIORITY (1)
  1. [ ] Fix security vulnerability in auth
     Component: security, authentication
     Context: Refactoring auth.py
     Captured: Nov 10, 14:15:32
     Related: #2 (rate limiting)
  
  🟡 MEDIUM PRIORITY (2)
  2. [ ] Add rate limiting to login endpoint
     Component: authentication, api
     Context: Refactoring auth.py
     Captured: Nov 10, 14:23:15
     Related: #1 (security)
  
  3. [ ] Update authentication docs
     Component: documentation
     Context: Refactoring auth.py
     Captured: Nov 10, 14:45:09
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  Commands:
  • "work on task 2" - Start planning/implementation
  • "complete task 3" - Mark as done
  • "delete task 1" - Remove from list
  • "show auth tasks" - Filter by component
```

### Interactive Planning Integration (CORTEX 2.1)

```
USER: "work on task 2"

CORTEX:
  📋 Task: Add rate limiting to login endpoint
  
  Let me ask a few questions to clarify:
  
  1️⃣ What rate limit? (requests per minute)
     • 10 (strict)
     • 30 (moderate)  
     • 100 (lenient)
     • Custom
  
USER: "30"

CORTEX:
  2️⃣ Rate limit per IP or per user?
  
USER: "per user"

CORTEX:
  3️⃣ How to handle exceeded limits?
     • Return 429 error
     • Queue request
     • Notify user
     
USER: "return 429"

CORTEX:
  ✅ Here's the implementation plan:
  
  [Detailed plan based on clarified requirements]
  
  Proceed? (yes/no/modify)
```

**Synergy:**
- Task Dump captures **WHAT** to do
- Interactive Planning clarifies **HOW** to do it
- Both stored in Tier 2 Knowledge Graph
- Learning improves over time

---

## 📊 Extensibility Enhancements

### Enhancement 1: Component-Based Task Lists

**Problem:** 50+ tasks becomes overwhelming

**Solution:** Auto-organize by component

```
USER: "show tasks for authentication"

CORTEX:
  📋 AUTHENTICATION TASKS (5)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. [ ] Add rate limiting
  2. [ ] Fix security vulnerability
  3. [x] Extract AuthService (DONE)
  4. [ ] Add JWT refresh tokens
  5. [ ] Update auth documentation
```

**Implementation:**
```python
def show_tasks(self, filter_component: Optional[str] = None):
    """Show tasks, optionally filtered by component."""
    if filter_component:
        tasks = self._filter_by_component(filter_component)
    else:
        tasks = self._get_all_tasks()
    
    # Group by component
    grouped = self._group_by_component(tasks)
    return self._format_grouped_tasks(grouped)
```

### Enhancement 2: Smart Priority Detection

**Problem:** User doesn't always specify priority

**Solution:** Auto-detect from keywords and context

```python
PRIORITY_KEYWORDS = {
    'high': ['urgent', 'critical', 'bug', 'security', 'broken', 'crash'],
    'medium': ['should', 'important', 'improve', 'refactor', 'optimize'],
    'low': ['nice to have', 'eventually', 'consider', 'maybe', 'cleanup']
}

def _detect_priority(self, task_text: str, context: Dict) -> str:
    """
    Auto-detect priority from keywords and context.
    
    Rules:
    - Security keywords → HIGH
    - Active bugs → HIGH
    - During refactoring → MEDIUM
    - Documentation → LOW (unless security docs)
    """
    # Check keywords
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in task_text.lower() for kw in keywords):
            return priority
    
    # Check context
    if context.get('operation') == 'debugging':
        return 'high'
    
    return 'medium'  # Default
```

### Enhancement 3: Related Task Clustering

**Problem:** Similar tasks scattered across list

**Solution:** Show related tasks together

```
USER: "show task 2"

CORTEX:
  📋 Task #2: Add rate limiting to login endpoint
  
  Related Tasks:
  • #1: Fix security vulnerability (similar: security)
  • #4: Add JWT refresh tokens (similar: authentication)
  
  Context:
  • Captured during: auth.py refactoring
  • Similar past tasks: 3 (2 completed, 1 failed)
  • Knowledge graph pattern: "authentication-security-cluster"
```

**Implementation:**
```python
def _find_related_tasks(self, task: TaskCapture) -> List[TaskCapture]:
    """Find related tasks using multiple signals."""
    
    # 1. Same component
    component_tasks = self._filter_by_component(task.component)
    
    # 2. Text similarity (TF-IDF or embeddings)
    similar_text = self._find_similar_text(task.raw_text)
    
    # 3. Captured in same context
    same_context = self._filter_by_context(task.active_file)
    
    # 4. Knowledge graph patterns
    kg_related = self.tier2.find_related_patterns(task.component)
    
    # Combine and rank
    return self._rank_related_tasks([
        *component_tasks,
        *similar_text,
        *same_context,
        *kg_related
    ])
```

### Enhancement 4: Task Templates

**Problem:** Repetitive task types

**Solution:** Learn patterns and suggest templates

```
USER: "task: refactor authentication module"

CORTEX: ✅ Captured (#b4d2)

💡 I noticed this is similar to past refactoring tasks.
   Use template? (yes/no)
   
   Template: "Module Refactor"
   • Extract service class
   • Update tests
   • Update documentation
   • Check for breaking changes
   • Update dependencies

USER: "yes"

CORTEX: ✅ Created 5 sub-tasks from template
```

**Implementation:**
```python
@dataclass
class TaskTemplate:
    """Reusable task template."""
    name: str
    trigger_keywords: List[str]  # ["refactor", "module"]
    subtask_pattern: List[str]   # Common subtasks
    usage_count: int             # How often used
    success_rate: float          # Historical success

def _suggest_template(self, task_text: str) -> Optional[TaskTemplate]:
    """Suggest template if task matches pattern."""
    # Check knowledge graph for patterns
    patterns = self.tier2.find_task_patterns(task_text)
    
    if patterns and patterns[0].confidence > 0.8:
        return self._load_template(patterns[0].template_id)
    
    return None
```

### Enhancement 5: Cross-Repository Tasks

**Problem:** Working on multiple projects

**Solution:** Context-aware task routing

```yaml
# cortex.config.json
{
  "task_dump": {
    "project_contexts": [
      {
        "name": "CORTEX",
        "path": "D:/PROJECTS/CORTEX",
        "components": ["tier1", "tier2", "agents", "operations"]
      },
      {
        "name": "MyApp",
        "path": "D:/PROJECTS/MyApp",
        "components": ["frontend", "backend", "api", "auth"]
      }
    ]
  }
}
```

```
USER: "task: add dark mode to frontend"

CORTEX: 
  ✅ Captured (#e8f3)
  📁 Detected project: MyApp (frontend component)
  
USER: "show CORTEX tasks"

CORTEX:
  📋 CORTEX PROJECT (7 tasks)
  [Only CORTEX tasks shown]
  
USER: "show all tasks"

CORTEX:
  📋 ALL PROJECTS (15 tasks)
  
  🗂️ CORTEX (7)
  • Task 1, 2, 3...
  
  🗂️ MyApp (8)
  • Task 4, 5, 6...
```

---

## 🔄 Integration with CORTEX 2.1

### Workflow: Task Dump → Interactive Planning

```
┌─────────────────────────────────────────┐
│ 1. INTERRUPT & CAPTURE (CORTEX 3.0)    │
│    User: "task: add websocket support"  │
│    → 3ms capture, zero disruption      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. BACKGROUND ENRICHMENT                │
│    → Component: "backend, api"          │
│    → Priority: "medium"                 │
│    → Related: 2 similar tasks           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. USER REVIEWS TASK (Later)           │
│    User: "work on task 5"               │
│    → Triggers CORTEX 2.1 planner       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. INTERACTIVE PLANNING (CORTEX 2.1)   │
│    CORTEX: Asks clarifying questions    │
│    • "Which protocol? (Socket.io/raw)"  │
│    • "Client-side or server-side?"      │
│    • "Authentication needed?"           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 5. REFINED PLAN                         │
│    → Detailed implementation plan       │
│    → Saved to Tier 2 Knowledge Graph    │
│    → Ready for execution                │
└─────────────────────────────────────────┘
```

### Data Flow

```python
# Task Dump creates initial record
task = TaskCapture(
    task_id="a3f9",
    raw_text="add websocket support",
    component="backend",
    priority="medium",
    status="pending"
)

# Later: User triggers planning
user_input = "work on task a3f9"

# CORTEX 2.1 loads task context
planning_context = {
    'original_task': task.raw_text,
    'component': task.component,
    'related_tasks': task.related_tasks,
    'capture_context': task.active_file  # Was working on server.py
}

# Interactive Planning uses context for smarter questions
planner = InteractivePlannerAgent(tier1, tier2)
questions = planner.generate_questions(
    request=task.raw_text,
    context=planning_context  # Enriched context from Task Dump!
)

# After planning: Update task with plan
task.status = "planned"
task.plan_id = plan.plan_id  # Link to detailed plan
tier1.update_task(task)
```

### Synergy Benefits

1. **Context Preservation:**
   - Task Dump captures WHERE you were
   - Planning asks questions based on THAT context
   - Example: "You were editing server.py - add websockets there?"

2. **Priority Guidance:**
   - Task Dump detected priority from keywords
   - Planner adjusts question complexity accordingly
   - High priority → simpler, faster questions

3. **Related Task Awareness:**
   - Task Dump found 2 related tasks
   - Planner asks: "This relates to tasks #3 and #7. Same approach?"
   - Reduces duplicate planning

4. **Learning Loop:**
   - Task Dump patterns → Knowledge Graph
   - Planning success/failure → Knowledge Graph
   - Future task dumps get better priority/component detection

---

## 📈 Performance Targets

| Operation | Target | Acceptable | Unacceptable |
|-----------|--------|-----------|--------------|
| **Interrupt Detection** | <1ms | <2ms | >5ms |
| **Task Capture** | <5ms | <10ms | >20ms |
| **Context Snapshot** | <1ms | <2ms | >5ms |
| **Total Interrupt** | <10ms | <15ms | >25ms |
| **Background Enrichment** | N/A | Async | Blocking |
| **Task Retrieval** | <50ms | <100ms | >200ms |

**Why these targets:**
- **10ms total** = User doesn't notice (human perception ~20ms)
- **Async enrichment** = Zero impact on active work
- **Fast retrieval** = Instant task list display

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_interrupt_detection():
    """Verify interrupt patterns detected correctly."""
    detector = InterruptDetector()
    
    # Positive cases
    assert detector.detect("task: add feature")
    assert detector.detect("/task add feature")
    assert detector.detect("remember: fix bug")
    
    # Negative cases
    assert not detector.detect("add a new feature")
    assert not detector.detect("let's plan something")

def test_capture_performance():
    """Verify capture completes in <5ms."""
    queue = TaskQueue(test_db_path)
    context = {'file': 'test.py', 'line': 42}
    
    start = time.perf_counter()
    task_id = queue.capture("test task", context)
    duration_ms = (time.perf_counter() - start) * 1000
    
    assert duration_ms < 5.0
    assert task_id is not None

def test_context_snapshot():
    """Verify context captured correctly."""
    entry = CortexEntry(...)
    entry._current_file = "auth.py"
    entry._current_line = 47
    
    snapshot = entry._get_context_snapshot()
    
    assert snapshot['file'] == "auth.py"
    assert snapshot['line'] == 47
```

### Integration Tests

```python
def test_interrupt_during_work():
    """Verify zero disruption during active work."""
    entry = CortexEntry(...)
    
    # Start long-running operation
    future = entry.process_request_async("refactor auth module")
    time.sleep(0.5)  # Simulate partial completion
    
    # Interrupt with task
    result = entry.process_request("task: add rate limiting")
    
    assert result['success'] is True
    assert result['action'] == 'task_captured'
    
    # Original work continues
    original_result = future.result()
    assert original_result['success'] is True

def test_task_to_planning_flow():
    """Verify task integrates with 2.1 planning."""
    # Capture task
    task_id = task_queue.capture("add websocket support", context)
    
    # Trigger planning
    planner = InteractivePlannerAgent(tier1, tier2)
    task = task_queue.get_task(task_id)
    
    questions = planner.generate_questions(
        request=task.raw_text,
        context={'original_task_id': task_id}
    )
    
    assert len(questions) > 0
    assert questions[0].context['original_task_id'] == task_id
```

---

## 🚀 Implementation Roadmap

### Phase 3.1: Core Task Dump (2 weeks)

**Week 1:**
- [ ] Create `src/tier1/task_queue.py` (FastCapture API)
- [ ] Create `src/entry_point/interrupt_detector.py` (Pattern matching)
- [ ] Add interrupt detection to `cortex_entry.py`
- [ ] Database schema for task queue
- [ ] Unit tests (interrupt detection, capture performance)

**Week 2:**
- [ ] Background enrichment worker
- [ ] Component detection algorithm
- [ ] Priority inference engine
- [ ] Integration tests (end-to-end capture flow)
- [ ] Performance benchmarks (<5ms capture validated)

### Phase 3.2: Task Management (1 week)

**Week 3:**
- [ ] Task retrieval API (`show tasks`)
- [ ] Filtering by component, priority, status
- [ ] Numbered list display
- [ ] Task completion/deletion commands
- [ ] Update commands (priority, component)

### Phase 3.3: CORTEX 2.1 Integration (1 week)

**Week 4:**
- [ ] Task → Planning workflow
- [ ] Context passing to Interactive Planner
- [ ] Plan linking (task.plan_id → plan record)
- [ ] Learning loop (task patterns → knowledge graph)
- [ ] Integration tests (full task-to-completion flow)

### Phase 3.4: Extensibility Enhancements (2 weeks)

**Week 5:**
- [ ] Related task clustering
- [ ] Task templates system
- [ ] Smart priority detection (advanced)
- [ ] Component auto-categorization (ML-based)

**Week 6:**
- [ ] Cross-repository support
- [ ] Task analytics dashboard
- [ ] Export/import task lists
- [ ] Documentation and tutorials

**Total:** 6 weeks (can run parallel with CORTEX 2.0 Phase 8-9)

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Capture Speed** | <5ms | Benchmark tests |
| **Zero Disruption** | 100% | Integration tests (work continues) |
| **Context Accuracy** | >95% | Manual review of captured context |
| **Priority Detection** | >85% | User confirmation rate |
| **Component Detection** | >90% | Auto-categorization accuracy |
| **User Adoption** | >70% | Active usage after 1 month |
| **Task Completion** | >60% | Tasks marked done / total captured |
| **2.1 Integration** | 100% | All tasks compatible with planner |

---

## 🎯 Quick Reference

### User Commands

```bash
# Capture tasks (during work)
task: add rate limiting
/task add feature
remember: fix bug
idea: refactor module
todo: update docs

# View tasks
show tasks                    # All tasks
show my tasks                 # Alias
show tasks for auth          # Filter by component
show high priority tasks     # Filter by priority
show task 5                  # Specific task details

# Manage tasks
work on task 5               # Start planning/implementation
complete task 3              # Mark as done
delete task 7                # Remove from list
prioritize task 2 high       # Update priority
move task 4 to backend       # Update component

# Advanced
show related tasks 5         # Show clustered tasks
export tasks to file.json   # Export task list
import tasks from file.json # Import task list
```

### Developer API

```python
# Capture API
from src.tier1 import TaskQueue

queue = TaskQueue(db_path)
task_id = queue.capture(
    raw_text="add rate limiting",
    context_snapshot={'file': 'auth.py', 'line': 47}
)

# Retrieval API
tasks = queue.get_all_tasks()
auth_tasks = queue.filter_by_component('authentication')
high_priority = queue.filter_by_priority('high')

# Integration with 2.1
from src.cortex_agents import InteractivePlannerAgent

planner = InteractivePlannerAgent(tier1, tier2)
task = queue.get_task(task_id)
questions = planner.generate_questions(
    request=task.raw_text,
    context={'original_task_id': task_id}
)
```

---

## 💡 Key Design Decisions

### ✅ Why NOT Use Orchestrator?

**Orchestrator is for:**
- Multi-module workflows (setup, story refresh)
- Phase-based execution with dependencies
- Complex error handling and rollback
- 50-100ms overhead acceptable

**Task Dump needs:**
- **Sub-5ms capture** (20x faster than orchestrator)
- **Zero disruption** (orchestrator pauses work)
- **Simple workflow** (just write to queue)
- **No phases** (single operation: append)

**Decision:** Independent lightweight system

### ✅ Why SQLite Queue?

**Alternatives considered:**
- In-memory list (lost on crash)
- JSON file (slow, requires locking)
- Redis (external dependency)

**SQLite chosen because:**
- ✅ Append-only writes = 3-5ms
- ✅ ACID guarantees (no data loss)
- ✅ No external dependencies
- ✅ Built-in indexing for fast retrieval
- ✅ Already used in Tier 1

### ✅ Why Async Enrichment?

**Could do synchronously:**
- Component detection: +20ms
- Priority inference: +15ms
- Related task clustering: +50ms
- **Total: +85ms** (unacceptable!)

**Async approach:**
- Capture: 5ms ✅
- Enrichment: background thread ✅
- User sees enriched data on next `show tasks` ✅
- **Zero impact on interrupt** ✅

### ✅ Why Integration with 2.1?

**Task Dump alone:**
- ❌ User writes vague task
- ❌ No clarification
- ❌ Implementation might be wrong

**Task Dump + Interactive Planning (2.1):**
- ✅ User dumps quick idea
- ✅ Later: CORTEX asks clarifying questions
- ✅ Refined plan ensures correct implementation
- ✅ Learning loop improves both systems

**Synergy is powerful!**

---

## 🎓 Learning Opportunities

### Pattern Detection

As users capture tasks, CORTEX learns:

1. **Component Patterns:**
   - "Add X to login" → authentication component
   - "Fix Y in navbar" → UI component
   - "Optimize Z query" → database component

2. **Priority Patterns:**
   - Security keywords → always high priority
   - Documentation → usually low (unless blocking)
   - Refactoring during bug fix → medium

3. **Related Task Clusters:**
   - Authentication tasks often come in batches
   - UI changes trigger documentation updates
   - Performance optimizations cluster by component

4. **Template Recognition:**
   - "Refactor X" → Extract class, update tests, docs
   - "Add Y feature" → Plan, implement, test, document
   - "Fix Z bug" → Reproduce, fix, test, prevent

### Knowledge Graph Updates

```yaml
# Tier 2 Knowledge Graph learns from task patterns
task_patterns:
  authentication_security_cluster:
    frequency: 15  # Seen 15 times
    tasks:
      - "add rate limiting"
      - "fix security vulnerability"
      - "update auth tokens"
    confidence: 0.92
    average_completion_time: "3.5 hours"
    common_blockers:
      - "missing test coverage"
      - "breaking changes in auth library"
    
  refactor_module_template:
    usage_count: 23
    success_rate: 0.87
    subtasks:
      - "Extract service class"
      - "Update tests"
      - "Update documentation"
      - "Check breaking changes"
    average_duration: "2.1 hours"
```

---

## 🔮 Future Enhancements (Beyond 3.0)

### Voice-Based Task Capture

```
USER: *clicks mic* "Task: add dark mode to settings page"
CORTEX: ✅ Captured (#f8a2). Continuing...
```

### AI-Generated Task Breakdowns

```
USER: "task: refactor authentication"

CORTEX: 
  ✅ Captured (#c4d9)
  
  💡 I broke this into 5 sub-tasks:
  1. Extract AuthService class
  2. Add JWT token validation
  3. Update unit tests
  4. Update integration tests
  5. Update authentication docs
  
  Accept breakdown? (yes/no/edit)
```

### Proactive Task Suggestions

```
CORTEX: Implementing login feature...
     ✅ Login form created
     ✅ API endpoint added
     ✅ Tests written
     
💡 Suggested tasks based on this work:
  1. Add "Forgot Password" flow
  2. Add rate limiting to login
  3. Update security documentation
  
  Capture any? (1,2,3 or no)
```

### Cross-Team Task Sharing

```yaml
# Share task list with team
tasks:
  export: team-tasks.json
  format: JIRA-compatible
  
# Import from team member
tasks:
  import: alice-tasks.json
  filter: component=backend
```

---

## 📚 Documentation Structure

```
cortex-brain/cortex-3.0-design/
├── TASK-DUMP-SYSTEM-DESIGN.md (this file)
├── INTERRUPT-PERFORMANCE-ANALYSIS.md
├── TASK-QUEUE-API-REFERENCE.md
├── CORTEX-2.1-INTEGRATION-GUIDE.md
├── TESTING-STRATEGY.md
└── IMPLEMENTATION-ROADMAP.md

docs/
└── features/
    └── task-dump-user-guide.md

src/tier1/
├── task_queue.py          # Core capture system
└── task_enrichment.py     # Background enrichment

src/entry_point/
└── interrupt_detector.py  # Pattern matching

tests/tier1/
└── test_task_queue.py     # Unit + performance tests
```

---

## ✅ Definition of Done

**CORTEX 3.0 Task Dump is complete when:**

1. ✅ Interrupt detection works (<1ms)
2. ✅ Task capture completes (<5ms)
3. ✅ Zero disruption to active work (integration tests pass)
4. ✅ Context snapshot accurate (>95%)
5. ✅ Background enrichment functional
6. ✅ Component detection accurate (>90%)
7. ✅ Priority inference accurate (>85%)
8. ✅ Task retrieval fast (<50ms)
9. ✅ Filtering/sorting works (component, priority, status)
10. ✅ 2.1 integration complete (task → planning workflow)
11. ✅ All tests passing (unit + integration + performance)
12. ✅ Documentation complete (user guide + API reference)
13. ✅ User adoption >70% after 1 month
14. ✅ Task completion rate >60%

---

## 🎯 Summary

**CORTEX 3.0 Task Dump System:**

✅ **Solves:** Idea capture without disrupting active work  
✅ **Performance:** <5ms capture, zero disruption  
✅ **Integration:** Feeds into CORTEX 2.1 Interactive Planning  
✅ **Extensible:** Component lists, templates, cross-repo support  
✅ **Learning:** Patterns improve over time via Knowledge Graph  

**Key Innovation:** Interrupt-driven capture with async enrichment = best of both worlds (fast + smart)

**Timeline:** 6 weeks (can parallel with CORTEX 2.0 Phase 8-9)

**Status:** DESIGN COMPLETE ✅ - Ready for implementation approval

---

*Design by: Asif Hussain*  
*Date: November 10, 2025*  
*Version: 3.0.0 (Draft 1)*  
*Next: Implementation approval + Phase 3.1 kickoff*
