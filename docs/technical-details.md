# CORTEX Technical Details

**Version:** 3.0  
**Last Updated:** November 6, 2025  
**Status:** Production Ready

---

## 📐 Architecture Overview

CORTEX is a **cognitive operating system** that provides AI assistants with persistent memory, context awareness, and learning capabilities. It implements a three-tier brain architecture modeled after human cognition.

### Core Design Principles

1. **Local-First**: All core functionality works offline
2. **SOLID Compliance**: Single Responsibility, Interface Segregation, Dependency Inversion
3. **Test-Driven**: 100% test coverage (439/439 tests passing)
4. **Performance**: Sub-100ms queries, optimized for speed
5. **Modular**: Easy to extend without modifying existing code

---

## 🧠 Three-Tier Brain System

### Tier 1: Working Memory (Short-Term)

**Purpose:** Recent conversation history and immediate context

**Technology Stack:**
```
- Storage: SQLite 3.x
- Schema: Relational (conversations, messages, entities, files)
- Performance: <50ms queries (avg: 23ms)
- Capacity: Last 20 conversations (FIFO queue)
```

**Database Schema:**
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    intent TEXT,
    outcome TEXT,
    duration_seconds INTEGER
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE files_modified (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    modification_type TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

**Key Features:**
- FIFO deletion (conversation #21 deletes #1)
- Active conversation protection (never deleted even if oldest)
- Full-text entity extraction
- File modification tracking
- Reference resolution ("it", "that file", etc.)

**Performance Benchmarks:**
```
Operation                 Time      Result
─────────────────────────────────────────
Insert conversation       8ms       ✅
Query last 20             12ms      ✅
Search by entity          23ms      ✅
Full conversation load    15ms      ✅
FIFO deletion            5ms       ✅
```

---

### Tier 2: Knowledge Graph (Long-Term)

**Purpose:** Learned patterns, relationships, and accumulated wisdom

**Technology Stack:**
```
- Storage: SQLite 3.x with FTS5 (Full-Text Search)
- Schema: Patterns + Full-Text Index
- Performance: <150ms searches (avg: 87ms)
- Capacity: Unlimited (grows with usage)
```

**Database Schema:**
```sql
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    scope TEXT NOT NULL CHECK(scope IN ('generic', 'application')),
    namespaces TEXT NOT NULL, -- JSON array
    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
    occurrences INTEGER DEFAULT 1,
    last_seen TEXT NOT NULL,
    created_at TEXT NOT NULL,
    data TEXT -- JSON storage for complex structures
);

-- Full-Text Search Index
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    title,
    description,
    content='patterns',
    content_rowid='id'
);

-- Automatic sync trigger
CREATE TRIGGER patterns_ai AFTER INSERT ON patterns BEGIN
    INSERT INTO patterns_fts(rowid, title, description)
    VALUES (new.id, new.title, new.description);
END;
```

**Pattern Types:**
```yaml
intent_patterns:
  - Phrase → Intent mapping ("add button" → PLAN)
  - Confidence scoring (0.0-1.0)
  - Usage frequency tracking

file_relationships:
  - Co-modification patterns (75% correlation)
  - Dependency graphs
  - Change propagation predictions

workflow_patterns:
  - Successful task sequences
  - Time estimates based on history
  - Test-first vs test-skip effectiveness

architectural_patterns:
  - Component structure (where files live)
  - Naming conventions (PascalCase, kebab-case)
  - Framework patterns (Blazor, React, etc.)

validation_insights:
  - Common mistakes (wrong file, wrong approach)
  - Correction history
  - Anti-patterns to avoid
```

**Knowledge Boundaries (NEW - v3.0):**
```yaml
Scope Classification:
  - generic: CORTEX core intelligence (NEVER deleted)
  - application: Project-specific (deleted on amnesia)

Namespace Isolation:
  - CORTEX-core: Universal patterns (TDD, SOLID, routing)
  - ProjectName: Application-specific patterns
  - Multi-namespace: Shared patterns (boosted in search)

Search Boosting:
  - Current project patterns: 2.0x boost
  - Generic patterns: 1.5x boost
  - Other projects: 0.5x boost
```

**Pattern Cleanup Automation:**
```python
# Automatic maintenance (runs daily)
1. Confidence Decay:
   - Patterns unused >30 days: -1% per day
   - Prevents stale data accumulation

2. Pattern Consolidation:
   - Similarity >70% → Merge patterns
   - Combines occurrences, averages confidence
   - Reduces redundancy

3. Stale Removal:
   - Age >90 days + confidence <50% → Delete
   - Safety: Never touches CORTEX-core
   - Audit log: All deletions recorded

4. Database Optimization:
   - VACUUM (reclaim space)
   - FTS5 rebuild (refresh search index)
   - Integrity check (validate constraints)
```

**Performance Benchmarks:**
```
Operation                     Time      Result
───────────────────────────────────────────────
Insert pattern                15ms      ✅
FTS5 search (single term)     42ms      ✅
FTS5 search (multi-term)      87ms      ✅
Namespace filter              8ms       ✅
Confidence decay (100 items)  45ms      ✅
Pattern consolidation         320ms     ✅
Stale pattern removal         180ms     ✅
```

---

### Tier 3: Context Intelligence (Development Metrics)

**Purpose:** Holistic project understanding and proactive warnings

**Technology Stack:**
```
- Storage: JSON file (optimized for read speed)
- Collection: Git + Test + Build metrics
- Performance: <10ms queries (avg: 4ms)
- Update: Throttled (1x per hour maximum)
```

**Data Structure:**
```json
{
  "metadata": {
    "last_updated": "2025-11-06T22:00:00Z",
    "collection_duration_ms": 2847,
    "project_root": "D:/PROJECTS/CORTEX"
  },
  "git_activity": {
    "commit_count_30d": 1237,
    "commits_per_week": 42,
    "file_hotspots": [
      {
        "file": "HostControlPanel.razor",
        "churn_rate": 0.28,
        "edits_30d": 89,
        "classification": "unstable"
      }
    ],
    "velocity_trend": "increasing"
  },
  "code_changes": {
    "lines_added_week": 3877,
    "lines_deleted_week": 2104,
    "net_change": 1773,
    "average_commit_size": 89
  },
  "testing_activity": {
    "test_count": 439,
    "pass_rate": 1.0,
    "test_first_adoption": 0.96,
    "flaky_tests": []
  },
  "work_patterns": {
    "peak_productivity_hours": ["10:00-12:00"],
    "session_success_rates": {
      "09:00-10:00": 0.89,
      "10:00-12:00": 0.94,
      "14:00-16:00": 0.81
    },
    "average_session_duration": 47
  },
  "proactive_warnings": [
    {
      "type": "file_hotspot",
      "severity": "medium",
      "message": "HostControlPanel.razor is unstable (28% churn)",
      "recommendation": "Add extra validation phase"
    },
    {
      "type": "velocity_drop",
      "severity": "high",
      "message": "Velocity down 68% this week",
      "recommendation": "Smaller commits, more frequent tests"
    }
  ]
}
```

**Collection Process:**
```python
# Automatic collection (throttled to 1x/hour)
1. Git History Analysis:
   - Last 30 days of commits
   - File modification patterns
   - Churn rate calculation
   - Contributor patterns

2. Test Metrics:
   - Test count and pass rates
   - Flaky test detection (>10% failure rate)
   - Coverage trends
   - Test-first vs test-skip effectiveness

3. Build Metrics:
   - Build success rates
   - Average build time
   - Deployment frequency

4. Correlation Analysis:
   - Commit size vs success rate
   - Test-first vs rework time
   - Session time vs productivity
```

**Performance Benchmarks:**
```
Operation                 Time      Result
─────────────────────────────────────────
Load context (JSON)       4ms       ✅
Query git metrics         2ms       ✅
Query test metrics        1ms       ✅
Query work patterns       3ms       ✅
Full collection          2847ms    ✅ (throttled)
```

---

## 🤖 Agent System

### Architecture

CORTEX implements 10 specialist agents following SOLID principles:

```
Universal Entry Point (cortex.md)
           ↓
    Intent Router
           ↓
    ┌──────┴──────┬──────────┬─────────┬──────────┐
    ↓             ↓          ↓         ↓          ↓
Work Planner  Code Exec  Tester  Validator  Error Fixer
    ↓             ↓          ↓         ↓          ↓
   ...        (5 more specialist agents)
```

**Design Principles:**
1. **Single Responsibility**: One agent = one job (no mode switches)
2. **Interface Segregation**: Dedicated agents instead of multi-mode handlers
3. **Dependency Inversion**: Abstractions for storage/testing/file access

### Agent Roster

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Intent Router** | Analyze request, route to specialist | Natural language | Agent selection |
| **Work Planner** | Create multi-phase plans | Feature description | Phased work plan |
| **Code Executor** | Implement code (TDD) | Task specification | Implementation |
| **Test Generator** | Create/run tests | Feature/component | Test suite |
| **Error Corrector** | Fix Copilot mistakes | Correction request | Fixed code |
| **Session Resumer** | Resume after breaks | Session ID | Progress report |
| **Health Validator** | System health checks | Validation request | Health report |
| **Change Governor** | Review CORTEX changes | Diff/proposal | Approval/rejection |
| **Screenshot Analyzer** | Extract requirements | Image | Requirements doc |
| **Commit Handler** | Intelligent git commits | Changed files | Semantic commits |

### Agent Communication

**Abstractions (Dependency Inversion):**
```python
# Session Access
class SessionLoader:
    """Abstract session storage (file/db/cloud agnostic)"""
    def load_session(session_id: str) -> Session
    def save_session(session: Session) -> bool
    def list_sessions() -> List[Session]

# Test Execution
class TestRunner:
    """Abstract test execution (framework agnostic)"""
    def discover_tests(path: str) -> List[Test]
    def run_tests(pattern: str) -> TestResult
    def get_coverage() -> CoverageReport

# File Operations
class FileAccessor:
    """Abstract file I/O (path agnostic)"""
    def read_file(path: str) -> str
    def write_file(path: str, content: str) -> bool
    def search_files(pattern: str) -> List[str]

# Brain Queries
class BrainQuery:
    """Abstract BRAIN access (tier agnostic)"""
    def search_patterns(query: str) -> List[Pattern]
    def get_conversations(limit: int) -> List[Conversation]
    def get_context() -> DevelopmentContext
```

**Default Implementations:**
- SessionLoader → Local files (`sessions/*.json`)
- TestRunner → Project's existing tools (pytest, jest, playwright)
- FileAccessor → PowerShell/Python built-ins
- BrainQuery → SQLite + JSON (local storage)

---

## 🔄 Dual-Hemisphere Architecture

### Left Hemisphere (Tactical Executor)

**Purpose:** Precise code execution, TDD enforcement, detail verification

**Responsibilities:**
```yaml
Sequential Workflows:
  - RED: Write failing test
  - GREEN: Minimal implementation
  - REFACTOR: Clean up code
  - Validate: Zero errors/warnings

File Operations:
  - Exact line-by-line edits
  - Syntax verification
  - Build validation

Quality Enforcement:
  - All tests must pass
  - Zero build errors
  - Zero warnings
  - Accessibility compliance
```

**Agents:**
- Code Executor (`code-executor.md`)
- Test Generator (`test-generator.md`)
- Error Corrector (`error-corrector.md`)
- Health Validator (`health-validator.md`)
- Commit Handler (`commit-handler.md`)

**Performance:**
```
Operation                Time      Tests
────────────────────────────────────────
Code execution           ~3min     ✅
Test creation           ~2min     ✅
Validation suite        ~1min     ✅
Commit handling         ~30s      ✅
```

---

### Right Hemisphere (Strategic Planner)

**Purpose:** Architecture design, pattern recognition, future projection

**Responsibilities:**
```yaml
Strategic Planning:
  - Break features into phases
  - Estimate effort (data-driven)
  - Assess risks
  - Recommend workflows

Pattern Recognition:
  - "Similar to feature X from 3 weeks ago"
  - Reuse proven templates
  - Warn about known pitfalls

Context Awareness:
  - File hotspots (high churn = extra care)
  - Co-modification patterns
  - Best time to work (94% success at 10am)
  - Test-first vs test-skip effectiveness

Brain Protection:
  - Challenge risky proposals
  - Enforce Tier 0 rules (TDD, DoR, DoD)
  - Prevent CORTEX degradation
```

**Agents:**
- Intent Router (`intent-router.md`)
- Work Planner (`work-planner.md`)
- Screenshot Analyzer (`screenshot-analyzer.md`)
- Change Governor (`change-governor.md`)
- Session Resumer (`session-resumer.md`)

**Performance:**
```
Operation                Time      Accuracy
──────────────────────────────────────────
Intent routing           <5s       94%
Plan generation          ~2min     ✅
Context analysis         ~1min     ✅
Risk assessment          ~30s      ✅
```

---

### Corpus Callosum (Coordination)

**Purpose:** Message passing between hemispheres

**Message Queue:**
```jsonl
{"timestamp": "...", "from": "RIGHT", "to": "LEFT", "type": "STRATEGIC_PLAN", "data": {...}}
{"timestamp": "...", "from": "LEFT", "to": "RIGHT", "type": "EXECUTION_COMPLETE", "data": {...}}
```

**Coordination Patterns:**
```
RIGHT plans → Corpus callosum → LEFT executes
LEFT results → Corpus callosum → RIGHT learns
```

**Storage:** `cortex-brain/corpus-callosum/coordination-queue.jsonl`

---

## 🛡️ Tier 0: Governance (Immutable Rules)

### Core Principles

**Definition of READY:**
- Clear requirements documented
- Acceptance criteria defined
- Dependencies identified
- Risks assessed

**Test-Driven Development:**
- Always RED → GREEN → REFACTOR
- Test BEFORE implementation
- Never skip tests

**Definition of DONE:**
- All tests passing (100%)
- Zero build errors
- Zero warnings
- Code reviewed
- Documentation updated

**SOLID Principles:**
- Single Responsibility per agent
- Open/Closed (extend without modify)
- Interface Segregation (no mode switches)
- Dependency Inversion (abstractions)

**Local-First:**
- Zero external dependencies for core
- Works offline
- Fast (no network latency)
- Portable

**Incremental File Creation:**
- Large files (>100 lines) created in chunks
- Prevents "response length limit" errors
- Each chunk 100-150 lines maximum

### Rule Enforcement

**Storage:** SQLite database (`tier0-governance.db`)

```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    rule_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    enforceable INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE violations (
    id INTEGER PRIMARY KEY,
    rule_id INTEGER NOT NULL,
    description TEXT,
    event_id TEXT,
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution_notes TEXT,
    FOREIGN KEY (rule_id) REFERENCES rules(id)
);
```

**Violation Detection:**
```python
# Automatic checks
1. Pre-commit hooks (build, test, lint)
2. Agent validation (before executing)
3. BRAIN updates (pattern quality)
4. Periodic health checks
```

---

## 📊 Performance Metrics

### System-Wide Benchmarks

```
Component               Target      Actual    Status
─────────────────────────────────────────────────────
Tier 1 queries          <100ms      23ms      ✅ 4.3x faster
Tier 2 search           <150ms      87ms      ✅ 1.7x faster
Tier 3 queries          <10ms       4ms       ✅ 2.5x faster
Intent routing          <5s         2.3s      ✅ 2.2x faster
Test execution          varies      ✅        100% pass rate
Build validation        <30s        18s       ✅ 1.7x faster
Commit handling         <60s        28s       ✅ 2.1x faster
```

### Memory Footprint

```
Component               Size        Growth Rate
──────────────────────────────────────────────
Tier 1 database         2.4 MB      FIFO (capped)
Tier 2 database         18.7 MB     ~500 KB/month
Tier 3 JSON             127 KB      Stable
Events log              3.2 MB      ~200 KB/month
Total BRAIN             24.4 MB     ~700 KB/month
```

### Test Coverage

```
Module                  Tests       Coverage
────────────────────────────────────────────
Tier 1                  16/16       100%
Tier 2                  25/25       100%
Tier 3                  13/13       100%
Knowledge Boundaries    30/30       100%
Agents (10 total)       229/229     100%
Entry Point             90/90       100%
Migrations              36/36       100%
──────────────────────────────────────────
TOTAL                   439/439     100% ✅
```

---

## 🔐 Security & Privacy

### Data Storage

**Local-First Architecture:**
- All BRAIN data stored locally
- No cloud dependencies required
- User controls all data
- Easy to backup/migrate

**File Locations:**
```
cortex-brain/
├── conversation-history.jsonl    (Tier 1 - conversations)
├── tier1-working-memory.db        (Tier 1 - SQLite)
├── tier2-knowledge-graph.db       (Tier 2 - SQLite + FTS5)
├── development-context.json       (Tier 3 - metrics)
├── events.jsonl                   (Tier 4 - event stream)
└── tier0-governance.db            (Tier 0 - rules)
```

**Data Retention:**
```yaml
Tier 1: Last 20 conversations (FIFO deletion)
Tier 2: Unlimited (with cleanup automation)
Tier 3: Last 30 days (rolling window)
Tier 4: Unlimited (can be purged manually)
Tier 0: Permanent (governance rules)
```

### Amnesia & Migration

**Selective Amnesia:**
```python
# Delete application data, preserve CORTEX intelligence
amnesia_manager.clear_application_data(
    namespaces=['KSESSIONS'],
    preserve_generic=True,
    safety_threshold=0.5  # Prevent >50% deletion
)

# Result:
# ✅ CORTEX-core patterns preserved
# ❌ KSESSIONS patterns deleted
# ✅ Generic patterns preserved
# ✅ Audit log created
```

**Migration Between Projects:**
```python
# Export CORTEX intelligence
exporter.export_generic_patterns(
    output='cortex-patterns-export.yaml',
    min_confidence=0.70
)

# Import to new project
importer.import_patterns(
    source='cortex-patterns-export.yaml',
    target_namespace='NewProject'
)
```

---

## 🚀 Deployment

### Requirements

**Minimum:**
- Python 3.9+
- SQLite 3.35+
- Git 2.30+
- 50 MB disk space
- PowerShell 7.0+ (Windows) or Bash 4.0+ (Linux/Mac)

**Recommended:**
- Python 3.11+
- SQLite 3.40+
- 200 MB disk space
- SSD for optimal performance

### Installation

```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Run setup
python setup_cortex.py

# Configure
cp cortex.config.example.json cortex.config.json
# Edit cortex.config.json with your settings

# Verify installation
python -m pytest CORTEX/tests/ -v

# Expected: 439/439 tests passing ✅
```

### Configuration

**cortex.config.json:**
```json
{
  "project_name": "CORTEX",
  "version": "3.0.0",
  "brain_path": "cortex-brain",
  "tier1_db": "tier1-working-memory.db",
  "tier2_db": "tier2-knowledge-graph.db",
  "tier3_json": "development-context.json",
  "conversation_limit": 20,
  "auto_brain_update": true,
  "event_threshold": 50,
  "tier3_throttle_hours": 1,
  "cleanup_enabled": true,
  "cleanup_decay_rate": 0.01,
  "cleanup_stale_days": 90,
  "cleanup_consolidation_threshold": 0.70
}
```

---

## 🧪 Testing Strategy

### Test-Driven Development

**Workflow:**
```
1. RED: Write failing test
2. GREEN: Minimal implementation
3. REFACTOR: Clean up
4. VALIDATE: All tests pass
```

**Test Pyramid:**
```
           /\
          /  \  E2E Tests (10%)
         /────\
        /      \  Integration Tests (30%)
       /────────\
      /          \  Unit Tests (60%)
     /────────────\
```

**Coverage Enforcement:**
- Minimum: 95% coverage
- Target: 100% coverage
- Current: 100% ✅

### Test Execution

```bash
# Run all tests
pytest CORTEX/tests/ -v

# Run specific tier
pytest CORTEX/tests/tier1/ -v
pytest CORTEX/tests/tier2/ -v
pytest CORTEX/tests/tier3/ -v

# Run with coverage
pytest --cov=CORTEX --cov-report=html

# Run knowledge boundaries
pytest CORTEX/tests/tier2/test_knowledge_boundaries.py -v
```

---

## 📈 Monitoring & Observability

### Health Checks

**Automatic:**
```python
# Built-in health validator
health_report = health_validator.run_all_checks()

# Returns:
{
  "overall_status": "healthy",
  "tier1_status": "healthy",
  "tier2_status": "healthy",
  "tier3_status": "healthy",
  "agent_status": "healthy",
  "issues": []
}
```

**Manual:**
```bash
# Run health check script
python scripts/health_check.py

# Run brain integrity test
python scripts/test-brain-integrity.py
```

### Metrics Collection

**Brain Efficiency:**
```python
# Collect efficiency metrics
python scripts/corpus-callosum/collect-brain-metrics.py

# Metrics stored in:
cortex-brain/corpus-callosum/efficiency-history.jsonl
```

**Dashboard:**
```bash
# Launch comprehensive dashboard
python scripts/launch-dashboard.ps1

# Serves on: http://localhost:8000
# Features:
#   - Health checks (7 categories)
#   - BRAIN integrity (13 checks)
#   - Efficiency metrics (5 components)
#   - 30-day trend charts
#   - Smart recommendations
```

---

## 🔧 Maintenance

### Daily (Automatic)

```
✅ Pattern cleanup (decay, consolidation, removal)
✅ Event processing (when 50+ events)
✅ Tier 3 collection (when >1 hour old)
✅ FIFO deletion (when 21st conversation)
```

### Weekly (Recommended)

```
□ Review proactive warnings
□ Check test pass rates
□ Verify disk space
□ Review commit patterns
```

### Monthly (Recommended)

```
□ Run deep health check
□ Review knowledge graph quality
□ Check for stale patterns
□ Backup BRAIN data
□ Update documentation
```

### Troubleshooting

**Common Issues:**

1. **Slow queries:**
   ```sql
   -- Rebuild indexes
   VACUUM;
   REINDEX;
   ```

2. **Stale patterns:**
   ```python
   # Run cleanup manually
   python scripts/cleanup_patterns.py
   ```

3. **Test failures:**
   ```bash
   # Verify environment
   pytest CORTEX/tests/ -v
   ```

4. **BRAIN corruption:**
   ```bash
   # Restore from backup
   cp backups/pre-X/tier2-knowledge-graph.db cortex-brain/
   ```

---

## 📚 API Reference

### Tier 1 API

```python
from CORTEX.src.tier1 import ConversationManager

# Initialize
manager = ConversationManager(db_path="tier1-working-memory.db")

# Create conversation
conv_id = manager.create_conversation(
    title="Add purple button",
    intent="PLAN",
    outcome="success"
)

# Add messages
manager.add_message(
    conversation_id=conv_id,
    role="user",
    content="I want to add a purple button"
)

# Search conversations
results = manager.search_conversations(
    query="purple button",
    limit=10
)

# Get conversation
conv = manager.get_conversation(conv_id)
```

### Tier 2 API

```python
from CORTEX.src.tier2 import KnowledgeGraph

# Initialize
kg = KnowledgeGraph(db_path="tier2-knowledge-graph.db")

# Search patterns (FTS5)
patterns = kg.search_patterns(
    query="button animation",
    namespace="CORTEX-core",
    min_confidence=0.70
)

# Add pattern
kg.add_pattern(
    pattern_type="workflow_patterns",
    title="Button creation workflow",
    description="TDD workflow for UI buttons",
    scope="generic",
    namespaces=["CORTEX-core"],
    confidence=0.85
)

# Get recommendations
cleanup_recs = kg.get_cleanup_recommendations()
```

### Tier 3 API

```python
from CORTEX.src.tier3 import ContextManager

# Initialize
cm = ContextManager(json_path="development-context.json")

# Get metrics
git_metrics = cm.get_git_activity()
test_metrics = cm.get_testing_activity()
work_patterns = cm.get_work_patterns()

# Get warnings
warnings = cm.get_proactive_warnings()

# Collect fresh data
cm.collect_metrics(force=True)
```

---

## 🎯 Roadmap

### Completed ✅

- [x] Three-tier brain architecture
- [x] 10 specialist agents
- [x] Knowledge boundaries (80%)
- [x] Pattern cleanup automation
- [x] Enhanced amnesia
- [x] Test coverage 100%
- [x] Performance optimization
- [x] Documentation

### In Progress 🔄

- [ ] Dashboard implementation (Sub-Group 4C)
- [ ] Knowledge boundaries Phase 3 (Brain Protector)
- [ ] MkDocs full setup

### Planned 📋

- [ ] Mind Palace (advanced spatial memory)
- [ ] Real-time dashboard updates
- [ ] VS Code extension
- [ ] Cloud sync (optional)
- [ ] Multi-project support
- [ ] Advanced analytics

---

## 📞 Support

- **Documentation:** [MkDocs Site](http://localhost:8000)
- **Issues:** [GitHub Issues](https://github.com/asifhussain60/CORTEX/issues)
- **Repository:** [GitHub](https://github.com/asifhussain60/CORTEX)

---

**Last Updated:** November 6, 2025  
**Version:** 3.0  
**Status:** Production Ready  
**Test Coverage:** 100% (439/439 tests passing) ✅
