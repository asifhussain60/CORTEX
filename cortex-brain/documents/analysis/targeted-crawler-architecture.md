# CORTEX Targeted Crawler System Architecture

**Date:** 2025-11-23  
**Status:** 🏗️ IN DEVELOPMENT - Phase 1 Complete  
**Version:** 2.0  
**Author:** Asif Hussain

---

## Executive Summary

The Targeted Crawler System provides **bounded, task-focused crawling** with safety mechanisms to prevent:
- ✅ Infinite loops in monolithic applications
- ✅ Excessive memory consumption
- ✅ Long-running operations
- ✅ Privacy violations

**Key Innovation:** Radius limits + circuit breakers + task scoping = safe exploration of complex codebases/databases.

---

## Problem Statement

### The Monolith Complexity Challenge

**User Concern (2025-11-23):**
> "I want CORTEX to use 'targeted' auto-crawling, meaning it should crawl what's needed for the task at hand. Concern is that in monolith applications and databases, the crawler could never return back because of complexity."

**Real-World Scenario:**
```
SignalR Hub (HostControlPanel)
  ├── Database Query (Questions table)
  │   ├── Foreign Key → Participants
  │   │   ├── Foreign Key → Sessions  
  │   │   │   ├── Foreign Key → Hosts
  │   │   │   │   ├── Foreign Key → ... (20+ more tables)
  │   │   │   │   └── ❌ INFINITE CRAWL without bounds
```

**Without Safety:** Crawler explores entire monolith (thousands of files, hundreds of tables) → never completes.

**With Targeted Crawler:** Stops at depth 3, analyzes only relevant paths → completes in seconds.

---

## Safety Mechanisms

### 1. Radius Limits

**Prevents:** Infinite traversal in interconnected systems

**Implementation:**
```python
max_depth = 3  # Stop after N hops from origin
max_breadth = 10  # Maximum children per node
```

**Example:**
```
Origin: HostControlPanel.razor (depth 0)
├── QuestionCard.razor (depth 1) ✅
│   ├── DeleteButton.razor (depth 2) ✅
│   │   ├── ConfirmModal.razor (depth 3) ✅
│   │   │   └── AlertService (depth 4) ❌ STOP (radius limit)
```

### 2. Circuit Breakers

**Prevents:** Resource exhaustion

**Triggers:**
- **Timeout:** Abort after 30 seconds
- **File Count:** Max 50 files analyzed
- **Memory:** Max 500 MB consumed

**Implementation:**
```python
def _check_circuit_breakers(self):
    # Timeout check
    if time.time() - self.start_time > timeout_seconds:
        raise CircuitBreakerException("Timeout exceeded")
    
    # File count check
    if self.files_analyzed > max_files:
        raise CircuitBreakerException("File limit exceeded")
    
    # Memory check
    if process.memory_info().rss / (1024**2) > max_memory_mb:
        raise CircuitBreakerException("Memory limit exceeded")
```

### 3. Task Scoping

**Prevents:** Analyzing irrelevant code paths

**Scopes:**
- `VIEW_STRUCTURE`: UI component hierarchy
- `DATABASE_SCHEMA`: Table relationships
- `CODE_DEPENDENCIES`: Import/call graph
- `SIGNALR_FLOW`: Real-time event chains
- `API_ENDPOINTS`: REST/GraphQL routes

**Example:**
```python
# User asks: "How does delete button work?"
config = TargetedCrawlerConfig(
    scope=CrawlScope.VIEW_STRUCTURE,
    follow_imports=True,  # ✅ Follow component imports
    follow_calls=False,   # ❌ Don't follow ALL method calls
    follow_db_fks=False,  # ❌ Don't crawl database
)
```

### 4. Privacy Protection

**Prevents:** Exposing sensitive data

**Skip Patterns:**
```python
skip_patterns = [
    r'.*password.*',
    r'.*secret.*',
    r'.*token.*',
    r'.*api[_-]?key.*',
    r'.*connection[_-]?string.*',
]
```

---

## Architecture

### Class Hierarchy

```
BaseCrawler (existing)
    ↓
TargetedCrawler (new - adds safety)
    ↓
    ├── ViewCrawler (UI views)
    ├── DatabaseCrawler (DB schema)
    ├── CodeCrawler (dependencies)
    └── SignalRCrawler (real-time flows)
```

### TargetedCrawler Base Class

**Location:** `src/crawlers/targeted_crawler.py`

**Key Methods:**
```python
class TargetedCrawler(BaseCrawler):
    def execute(self, origin: str) -> TargetedCrawlerResult:
        """Main entry point - enforces safety"""
        
    def crawl_targeted(self, origin: str) -> Tuple[nodes, edges, depth]:
        """Subclass implements scope-specific logic"""
        
    def _check_circuit_breakers(self) -> None:
        """Abort if limits exceeded"""
        
    def _check_radius_limit(self, depth: int) -> None:
        """Stop at max depth"""
        
    def _should_skip(self, path: str) -> bool:
        """Skip sensitive patterns"""
        
    def _mark_visited(self, node_id: str) -> bool:
        """Prevent cycles"""
```

### Breadth-First Exploration

**Why BFS?** Stays close to origin (better for task-focused analysis)

**Algorithm:**
```python
def _crawl_bfs(self, origin, get_children_func):
    queue = deque([(origin, 0)])
    visited = set()
    
    while queue:
        node, depth = queue.popleft()
        
        # Safety checks
        self._check_circuit_breakers()
        if depth >= max_depth:
            continue  # Radius limit
        
        # Get children
        children = get_children_func(node, depth)
        
        # Limit breadth
        if len(children) > max_breadth:
            children = children[:max_breadth]
        
        # Queue unvisited children
        for child in children:
            if child not in visited:
                visited.add(child)
                queue.append((child, depth + 1))
```

---

## Specialized Crawlers

### ViewCrawler (UI Views)

**Scope:** `VIEW_STRUCTURE`  
**Max Depth:** 2 (view → components → sub-components)  
**Timeout:** 15 seconds

**Extracts:**
- HTML element IDs (`id="hcp-delete-button"`)
- CSS classes (`class="question-card"`)
- Event handlers (`@onclick="DeleteQuestion"`)
- Component hierarchy

**Usage:**
```python
crawler = ViewCrawler({
    'max_depth': 2,
    'timeout_seconds': 15,
})

result = crawler.execute('HostControlPanel.razor')

print(f"Found {len(result.nodes)} components")
print(f"HTML IDs: {result.metadata['html_ids']}")
print(f"Event handlers: {result.metadata['event_handlers']}")
```

**Safety Metrics:**
```json
{
  "depth_reached": 2,
  "files_analyzed": 8,
  "memory_peak_mb": 45.3,
  "circuit_breaker_triggered": false,
  "radius_limit_hit": true,
  "warnings": ["Breadth limit: 15 components at HostControlPanel"]
}
```

### DatabaseCrawler (Schema)

**Scope:** `DATABASE_SCHEMA`  
**Max Depth:** 3 (table → FK → FK → FK)  
**Timeout:** 30 seconds

**Extracts:**
- Table relationships (foreign keys)
- Column definitions
- Indexes and constraints
- Referenced queries

**Usage:**
```python
crawler = DatabaseCrawler({
    'max_depth': 3,
    'follow_db_fks': True,
})

result = crawler.execute('Questions')  # Start from Questions table

print(f"Related tables: {[n['id'] for n in result.nodes]}")
# Output: ['Questions', 'Participants', 'Sessions', 'Hosts']
# Stops at depth 3 (doesn't crawl entire database)
```

### CodeCrawler (Dependencies)

**Scope:** `CODE_DEPENDENCIES`  
**Max Depth:** 2 (file → imports → imports)  
**Timeout:** 20 seconds

**Extracts:**
- Import statements
- Function calls (optional)
- Class inheritance
- Module dependencies

**Usage:**
```python
crawler = CodeCrawler({
    'max_depth': 2,
    'follow_imports': True,
    'follow_calls': False,  # Too expensive
})

result = crawler.execute('HostControlPanelController.cs')

print(f"Dependencies: {[n['id'] for n in result.nodes]}")
```

---

## Configuration

### TargetedCrawlerConfig

```python
@dataclass
class TargetedCrawlerConfig:
    # Radius Limits
    max_depth: int = 3
    max_breadth: int = 10
    
    # Circuit Breakers
    timeout_seconds: int = 30
    max_files: int = 50
    max_memory_mb: int = 500
    
    # Task Scoping
    scope: CrawlScope = CrawlScope.VIEW_STRUCTURE
    follow_imports: bool = True
    follow_calls: bool = False
    follow_db_fks: bool = True
    
    # Privacy Protection
    skip_patterns: List[str] = [
        r'.*password.*',
        r'.*secret.*',
        ...
    ]
    
    # Output Control
    verbose: bool = False
    max_result_size_mb: int = 5
```

---

## Results Format

### TargetedCrawlerResult

```python
@dataclass
class TargetedCrawlerResult:
    scope: CrawlScope
    origin: str
    timestamp: str
    duration_seconds: float
    
    # Graph structure
    nodes: List[Dict]  # [{'id': 'file.razor', 'type': 'view', 'depth': 0}]
    edges: List[Tuple]  # [('parent', 'child', 'references')]
    
    # Scope-specific metadata
    metadata: Dict  # {'html_ids': [...], 'event_handlers': [...]}
    
    # Safety metrics
    depth_reached: int
    files_analyzed: int
    memory_peak_mb: float
    circuit_breaker_triggered: bool
    radius_limit_hit: bool
    
    # Warnings
    warnings: List[str]
    skipped_paths: List[str]
```

**Example:**
```json
{
  "scope": "view_structure",
  "origin": "HostControlPanel.razor",
  "duration_seconds": 2.3,
  "nodes": [
    {"id": "HostControlPanel.razor", "type": "view", "depth": 0},
    {"id": "QuestionCard.razor", "type": "component", "depth": 1},
    {"id": "DeleteButton.razor", "type": "component", "depth": 2}
  ],
  "edges": [
    ["HostControlPanel.razor", "QuestionCard.razor", "uses"],
    ["QuestionCard.razor", "DeleteButton.razor", "uses"]
  ],
  "metadata": {
    "html_ids": ["hcp-question-card", "hcp-delete-button"],
    "event_handlers": [
      {"event_type": "onclick", "handler": "DeleteQuestion"}
    ]
  },
  "safety_metrics": {
    "depth_reached": 2,
    "files_analyzed": 3,
    "memory_peak_mb": 45.3,
    "circuit_breaker_triggered": false,
    "radius_limit_hit": true
  }
}
```

---

## Usage Examples

### Scenario 1: Debug UI Button

**User Question:** "Why isn't the delete button working?"

```python
from src.crawlers.targeted_crawler import ViewCrawler

# Configure bounded crawl
crawler = ViewCrawler({
    'max_depth': 2,
    'verbose': True,
})

# Execute targeted analysis
result = crawler.execute('HostControlPanel.razor')

# Extract insights
for handler in result.metadata['event_handlers']:
    if 'delete' in handler['handler'].lower():
        print(f"Delete handler: {handler['handler']} (line {handler['line']})")
        print(f"Button ID: {handler['element_id']}")
```

**Output:**
```
Delete handler: ShowDeleteModal (line 2126)
Button ID: hcp-question-delete-button
Files analyzed: 3
Duration: 1.8s
```

### Scenario 2: Trace Database Query

**User Question:** "What tables does this query touch?"

```python
from src.crawlers.targeted_crawler import DatabaseCrawler

crawler = DatabaseCrawler({
    'max_depth': 3,
    'follow_db_fks': True,
})

result = crawler.execute('Questions')

tables = [n['id'] for n in result.nodes if n['type'] == 'table']
print(f"Related tables: {tables}")
```

**Output:**
```
Related tables: ['Questions', 'Participants', 'Sessions', 'Hosts']
Files analyzed: 0 (database metadata only)
Duration: 0.5s
```

---

## Safety Validation

### Test Cases

**Test 1: Radius Limit Enforcement**
```python
def test_radius_limit():
    # Create deeply nested structure (10 levels)
    # Crawler with max_depth=3
    result = crawler.execute(origin)
    assert result.depth_reached <= 3
    assert result.radius_limit_hit == True
```

**Test 2: Circuit Breaker (Timeout)**
```python
def test_timeout():
    # Configure 1-second timeout
    crawler = ViewCrawler({'timeout_seconds': 1})
    
    # Crawl large file
    result = crawler.execute('MassiveView.razor')
    
    assert result.circuit_breaker_triggered == True
    assert result.duration_seconds <= 1.5  # Allow 0.5s overhead
```

**Test 3: Memory Limit**
```python
def test_memory_limit():
    crawler = ViewCrawler({'max_memory_mb': 100})
    result = crawler.execute(origin)
    assert result.memory_peak_mb <= 150  # Allow 50MB overhead
```

**Test 4: Privacy Protection**
```python
def test_skip_sensitive():
    result = crawler.execute('ConfigFile.cs')
    assert 'connection_string_password' in result.skipped_paths
    assert len([n for n in result.nodes if 'password' in n['id']]) == 0
```

---

## Integration with CORTEX

### Onboarding Workflow

```python
# When user onboards application
onboarding_modules = [
    ViewCrawler({'max_depth': 2}),
    DatabaseCrawler({'max_depth': 3}),
    CodeCrawler({'max_depth': 2}),
]

for crawler in onboarding_modules:
    result = crawler.execute(entry_point)
    store_in_knowledge_graph(result)
```

### Natural Language Queries

**User:** "How does the delete button work?"

**CORTEX:**
1. Detects `VIEW_STRUCTURE` scope
2. Runs `ViewCrawler` on `HostControlPanel.razor`
3. Finds `hcp-question-delete-button` → `ShowDeleteModal()` (line 2126)
4. Traces SignalR flow: `BroadcastQuestionDeleted` → `session_212` group
5. Returns: "Delete button triggers ShowDeleteModal() which broadcasts to session group. Check if SignalR connection active."

**No manual crawling needed** - automatic, bounded, safe.

---

## Implementation Status

### Phase 1: Foundation ✅ COMPLETE (2025-11-23)

- [x] Create `TargetedCrawler` base class
- [x] Implement radius limits
- [x] Implement circuit breakers
- [x] Implement privacy protection
- [x] Implement BFS algorithm

**Files Created:**
- `src/crawlers/targeted_crawler.py` (485 lines)

**Key Features:**
- Radius limits (max_depth, max_breadth)
- Circuit breakers (timeout, file count, memory)
- Task scoping (CrawlScope enum)
- Privacy protection (skip patterns)

### Phase 2: Specialized Crawlers (Not Started)

- [ ] Implement `ViewCrawler` (Blazor/Razor/React)
- [ ] Implement `DatabaseCrawler` (schema analysis)
- [ ] Implement `CodeCrawler` (dependencies)
- [ ] Implement `SignalRCrawler` (event flows)

**Estimated:** 6-8 hours

### Phase 3: Testing (Not Started)

- [ ] Unit tests for safety mechanisms
- [ ] Integration tests with mock monolith
- [ ] Performance benchmarks

**Estimated:** 4-6 hours

### Phase 4: Documentation (In Progress)

- [x] Architecture document (this file)
- [ ] API reference
- [ ] Usage examples
- [ ] Migration guide from manual crawling

**Estimated:** 2-3 hours

---

## Next Steps

1. **Complete ViewCrawler Implementation** (2-3 hours)
   - HTML ID extraction
   - Component hierarchy
   - Event handler tracing

2. **Create Integration Tests** (2-3 hours)
   - Mock monolith application
   - Verify bounded behavior
   - Test all safety mechanisms

3. **Update Deployment Validation** (1-2 hours)
   - Add crawler checks to `validate_deployment.py`
   - Verify safety mechanisms in CI/CD

4. **Create Feedback Orchestrator** (3-4 hours)
   - `/CORTEX feedback` entry point
   - Generate structured reports (JSON/YAML)
   - GitHub Issue template formatter

---

## Appendix: Design Decisions

### Why Breadth-First (Not Depth-First)?

**BFS Advantages:**
- Stays close to origin (better for task-focused analysis)
- Explores siblings before going deep (more relevant results first)
- Easier to enforce radius limits

**DFS Disadvantages:**
- Goes deep quickly (may miss relevant siblings)
- Harder to enforce balanced exploration
- More likely to hit irrelevant paths

### Why Circuit Breakers?

**Real-World Failure Mode:**
- Developer forgets to set `max_depth`
- Crawler explores entire monolith (10,000+ files)
- Server runs out of memory
- User waits 10+ minutes → gives up

**Circuit Breakers:**
- Hard timeout (30s default)
- Hard memory limit (500 MB default)
- Fail fast with clear error message

### Why Privacy Protection?

**Incident Prevention:**
- Crawler accidentally stores `connection_string` in knowledge graph
- User shares CORTEX brain export
- Credentials leaked publicly

**Skip Patterns:**
- Block sensitive variable names
- Block sensitive file patterns
- Warn user when skipped

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Repository:** https://github.com/asifhussain60/CORTEX  
**Status:** Living Document - Updated as implementation progresses
