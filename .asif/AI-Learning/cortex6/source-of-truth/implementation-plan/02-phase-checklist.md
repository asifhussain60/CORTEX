# CORTEX 6.0 - 9-Phase Implementation Checklist

**Version:** 6.0.0 | **Author:** Asif Hussain  
**Purpose:** Step-by-step implementation guide for greenfield build

---

## 📋 Pre-Build Checklist

- [ ] Backup completed (run `01-BACKUP-MIGRATION.sh`)
- [ ] Empty workspace confirmed
- [ ] Python 3.11+ installed
- [ ] Git initialized in workspace
- [ ] Source of truth documents accessible

---

## 🏗️ Phase 0: Project Setup (1 day)

### Objectives
- Create folder structure
- Initialize Python environment
- Setup configuration files

### Tasks

- [ ] **0.1** Create all directories per `machine-readable/01-folder-structure.yaml`
  - [ ] `cortex-brain/` and subdirectories
  - [ ] `src/` and subdirectories
  - [ ] `tests/` and subdirectories
  - [ ] `.github/prompts/`

- [ ] **0.2** Create root configuration files
  - [ ] `requirements.txt`
  - [ ] `pyproject.toml`
  - [ ] `pytest.ini`
  - [ ] `.gitignore`
  - [ ] `README.md`

- [ ] **0.3** Initialize Python environment
  - [ ] Create virtual environment: `python -m venv venv`
  - [ ] Activate: `source venv/bin/activate`
  - [ ] Install dependencies: `pip install -r requirements.txt`

- [ ] **0.4** Initialize Git
  - [ ] `git init`
  - [ ] `git add .`
  - [ ] `git commit -m "Phase 0: Project structure"`

### Validation Gate
```bash
# All directories exist
ls -la cortex-brain/ src/ tests/
# Python works
python --version
# Git initialized
git status
```

---

## 🏛️ Phase 1: Governance System (3 days)

### Objectives
- Implement 4-category governance merger
- Migrate 61 SKULL rules
- Create governance validation

### Tasks

- [ ] **1.1** Create CORTEX Tier 0 rules file
  - [ ] `cortex-brain/tier0/governance/core-rules.yaml`
  - [ ] Migrate all 61 SKULL rules (renumber as CORE-001 to CORE-061)
  - [ ] Define rule schema

- [ ] **1.2** Implement Governance Merger
  - [ ] `src/orchestrators/core/governance_merger.py`
  - [ ] 6-step merge algorithm
  - [ ] Conflict detection
  - [ ] Resolution strategies

- [ ] **1.3** Write governance tests
  - [ ] `tests/governance/test_merge_algorithm.py`
  - [ ] `tests/governance/test_conflict_resolution.py`
  - [ ] Test fixtures in `tests/fixtures/`

- [ ] **1.4** Create audit logger (runtime enforcement)
  - [ ] `src/orchestrators/middleware/audit_logger.py`
  - [ ] AuditContextManager (cannot bypass)

### Validation Gate
```bash
# Run governance tests
pytest tests/governance/ -v
# Verify merge produces valid output
python -c "from src.orchestrators.core.governance_merger import GovernanceMerger; print(GovernanceMerger().merge())"
```

---

## 🗄️ Phase 2: State Management (3 days)

### Objectives
- Implement SQLite with WAL mode
- Optimistic locking
- Checkpoint/resume system

### Tasks

- [ ] **2.1** Implement State Manager
  - [ ] `src/orchestrators/core/state_manager.py`
  - [ ] SQLite initialization with WAL mode
  - [ ] Table creation (14 tables)
  - [ ] Optimistic locking with version columns

- [ ] **2.2** Implement database schema
  - [ ] Execute `machine-readable/03-database-schema.sql`
  - [ ] Verify WAL mode active

- [ ] **2.3** Implement checkpoint manager
  - [ ] Checkpoint creation every 5 tasks
  - [ ] Resume from latest checkpoint

- [ ] **2.4** Write state management tests
  - [ ] `tests/unit/test_state_manager.py`
  - [ ] Concurrent access tests
  - [ ] Optimistic locking collision tests

### Validation Gate
```bash
# Run state tests
pytest tests/unit/test_state_manager.py -v
# Verify WAL mode
sqlite3 cortex-brain/database/cortex.db "PRAGMA journal_mode;"
# Should output: wal
```

---

## 📊 Phase 3: TODO Orchestrator (3 days)

### Objectives
- DAG-based work tracking
- Dependency management
- Progress calculation

### Tasks

- [ ] **3.1** Implement TODO Orchestrator
  - [ ] `src/orchestrators/core/todo_orchestrator.py`
  - [ ] TaskNode dataclass
  - [ ] DAG operations (add, query, update)

- [ ] **3.2** Implement dependency management
  - [ ] `add_task()` with dependencies
  - [ ] `get_ready_tasks()` - tasks with satisfied deps
  - [ ] `detect_circular_dependencies()` - DFS cycle detection

- [ ] **3.3** Implement progress tracking
  - [ ] `calculate_progress()` - overall metrics
  - [ ] `get_critical_path()` - longest dependency chain

- [ ] **3.4** Write TODO orchestrator tests
  - [ ] `tests/unit/test_todo_orchestrator.py`
  - [ ] DAG operations tests
  - [ ] Circular dependency detection tests

### Validation Gate
```bash
# Run TODO tests
pytest tests/unit/test_todo_orchestrator.py -v
# Verify DAG operations
python -c "
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator
from src.orchestrators.core.state_manager import StateManager
todo = TodoOrchestrator(StateManager())
t1 = todo.add_task('Task 1')
t2 = todo.add_task('Task 2', dependencies=[t1])
print(f'Ready tasks: {[t.title for t in todo.get_ready_tasks()]}')
"
```

---

## 🔀 Phase 4: Pattern Router (2 days)

### Objectives
- O(1) Trie-based routing
- Pattern registration
- Orchestrator lookup

### Tasks

- [ ] **4.1** Implement Trie Router
  - [ ] `src/orchestrators/routing/trie_router.py`
  - [ ] Trie data structure
  - [ ] Pattern registration
  - [ ] O(1) lookup

- [ ] **4.2** Register all orchestrator patterns
  - [ ] Planning: `^(plan|create a plan)`
  - [ ] TDD: `^(tdd|start tdd)`
  - [ ] All 10+ patterns from `CORTEX.prompt.md`

- [ ] **4.3** Write routing performance tests
  - [ ] `tests/performance/test_routing_performance.py`
  - [ ] Benchmark < 5ms for 100 patterns

### Validation Gate
```bash
# Run performance tests
pytest tests/performance/test_routing_performance.py -v
# Verify O(1) routing
python -c "
import time
from src.orchestrators.routing.trie_router import TrieRouter
router = TrieRouter()
# Register patterns
router.register('plan', 'PlanningOrchestrator')
router.register('tdd', 'TDDOrchestrator')
# Measure lookup
start = time.time()
for _ in range(1000):
    router.route('plan OAuth2')
elapsed = (time.time() - start) * 1000
print(f'1000 lookups: {elapsed:.2f}ms ({elapsed/1000:.3f}ms each)')
"
```

---

## 🎯 Phase 5: Master Orchestrator (3 days)

### Objectives
- Entry point integration
- Pipeline coordination
- Output formatting

### Tasks

- [ ] **5.1** Implement Master Orchestrator
  - [ ] `src/orchestrators/core/master_orchestrator.py`
  - [ ] `execute()` main entry point
  - [ ] Pipeline: Audit → Governance → Route → Execute

- [ ] **5.2** Implement entry point
  - [ ] `src/main.py`
  - [ ] CLI argument parsing
  - [ ] Output format (markdown/json)

- [ ] **5.3** Integrate all components
  - [ ] GovernanceMerger integration
  - [ ] PatternRouter integration
  - [ ] TodoOrchestrator integration
  - [ ] StateManager integration

- [ ] **5.4** Write integration tests
  - [ ] `tests/integration/test_end_to_end.py`

### Validation Gate
```bash
# Run E2E tests
pytest tests/integration/test_end_to_end.py -v
# Test CLI
python -m src.main "help" --format markdown
```

---

## 🔧 Phase 6: Workflow Orchestrators (5 days)

### Objectives
- Implement 10+ workflow orchestrators
- TDD for each orchestrator
- Integration with TODO system

### Tasks

- [ ] **6.1** Planning Orchestrator
  - [ ] `src/orchestrators/workflows/planning_orchestrator.py`
  - [ ] Tests first (RED)
  - [ ] Implementation (GREEN)

- [ ] **6.2** TDD Orchestrator
  - [ ] `src/orchestrators/workflows/tdd_orchestrator.py`
  - [ ] RED→GREEN→REFACTOR cycle

- [ ] **6.3** ADO Orchestrator
  - [ ] `src/orchestrators/workflows/ado_orchestrator.py`
  - [ ] Work item generation

- [ ] **6.4** Remaining Orchestrators (parallel development)
  - [ ] Vacuum, Cleanup, Investigation
  - [ ] Sanitization, Debug, Refinement
  - [ ] Maintenance

### Validation Gate
```bash
# Run all orchestrator tests
pytest tests/unit/orchestrators/ -v
# Test each orchestrator
python -m src.main "plan test feature" --format markdown
python -m src.main "tdd test module" --format markdown
```

---

## 🌐 Phase 7: MCP Server (3 days)

### Objectives
- JSON-RPC 2.0 implementation
- Tool exposure
- Multi-repo support

### Tasks

- [ ] **7.1** Implement MCP Server
  - [ ] `src/mcp/server.py`
  - [ ] JSON-RPC 2.0 methods
  - [ ] Tool registration

- [ ] **7.2** Implement multi-repo manager
  - [ ] `repos.yaml` configuration
  - [ ] Path resolution
  - [ ] Context switching

- [ ] **7.3** Write MCP tests
  - [ ] `tests/integration/test_multi_repo.py`
  - [ ] MCP method tests

### Validation Gate
```bash
# Start MCP server
python -m src.mcp.server &
# Test JSON-RPC call
curl -X POST http://localhost:5000 -d '{"jsonrpc":"2.0","method":"cortex.help","id":1}'
```

---

## 🧪 Phase 8: Testing & Coverage (3 days)

### Objectives
- Achieve 80%+ overall coverage
- 90%+ core component coverage
- All edge cases tested

### Tasks

- [ ] **8.1** Coverage audit
  - [ ] Run `pytest --cov=src --cov-report=html`
  - [ ] Identify coverage gaps

- [ ] **8.2** Add missing tests
  - [ ] Unit tests for uncovered paths
  - [ ] Edge case tests (25 scenarios)

- [ ] **8.3** Performance validation
  - [ ] Routing < 5ms
  - [ ] State persistence < 100ms
  - [ ] Governance merge < 50ms

### Validation Gate
```bash
# Full test suite with coverage
pytest tests/ --cov=src --cov-report=term-missing
# Verify coverage
# Overall: >= 80%
# Core: >= 90%
```

---

## 📦 Phase 9: Documentation & Polish (2 days)

### Objectives
- Complete documentation
- CORTEX.prompt.md for Copilot
- Final validation

### Tasks

- [ ] **9.1** Create CORTEX.prompt.md
  - [ ] `.github/prompts/CORTEX.prompt.md`
  - [ ] Terminal invocation instructions
  - [ ] Pattern routing table

- [ ] **9.2** Write README
  - [ ] Installation instructions
  - [ ] Usage examples
  - [ ] Architecture overview

- [ ] **9.3** Final validation
  - [ ] All tests pass
  - [ ] All documentation complete
  - [ ] Clean git history

### Validation Gate
```bash
# Final test run
pytest tests/ -v
# Verify CORTEX works
python -m src.main "help"
# Git status clean
git status
```

---

## 📊 Progress Summary

| Phase | Name | Duration | Status |
|-------|------|----------|--------|
| 0 | Project Setup | 1 day | ⬜ |
| 1 | Governance System | 3 days | ⬜ |
| 2 | State Management | 3 days | ⬜ |
| 3 | TODO Orchestrator | 3 days | ⬜ |
| 4 | Pattern Router | 2 days | ⬜ |
| 5 | Master Orchestrator | 3 days | ⬜ |
| 6 | Workflow Orchestrators | 5 days | ⬜ |
| 7 | MCP Server | 3 days | ⬜ |
| 8 | Testing & Coverage | 3 days | ⬜ |
| 9 | Documentation | 2 days | ⬜ |

**Total:** 28 days (4 weeks of focused work)

---

## 🎯 Success Criteria

At completion:

- [ ] All tests pass (80%+ coverage)
- [ ] `python -m src.main "help"` works
- [ ] MCP server responds to JSON-RPC
- [ ] 4-category governance produces unified set
- [ ] TODO DAG supports 1000+ nodes
- [ ] Pattern routing < 5ms
- [ ] State persistence < 100ms
- [ ] All 25 edge cases mitigated
- [ ] Documentation complete

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
