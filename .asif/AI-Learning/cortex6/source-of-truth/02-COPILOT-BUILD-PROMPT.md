# 🎯 CORTEX 6.0 - GitHub Copilot Build Prompt

**Purpose:** Complete instructions for GitHub Copilot to build CORTEX 6.0 from scratch  
**Version:** 6.0.0 | **Author:** Asif Hussain | **Date:** 2026-01-07

---

## 📋 Pre-Build Checklist

Before starting, ensure:

- [ ] You are in an EMPTY folder (or have run backup script)
- [ ] Python 3.11+ is installed
- [ ] Git is initialized in the workspace
- [ ] This prompt is loaded in GitHub Copilot Chat

---

## 🚀 Step 1: Backup Existing CORTEX (if applicable)

**macOS/Linux:**
```bash
cd /path/to/CORTEX
mkdir -p __backup
mv * __backup/ 2>/dev/null || true
mv .* __backup/ 2>/dev/null || true
mv __backup/__backup . 2>/dev/null || true
```

**Windows PowerShell:**
```powershell
cd D:\PROJECTS\CORTEX
New-Item -ItemType Directory -Force -Path "__backup"
Get-ChildItem -Force | Where-Object { $_.Name -ne "__backup" } | Move-Item -Destination "__backup"
```

---

## 🏗️ Step 2: Create Folder Structure

Create exactly this directory structure:

```
CORTEX-6/
├── cortex-brain/
│   ├── tier0/
│   │   └── governance/          # 61 SKULL rules migrated here
│   ├── tier1/                   # Active instruction set (runtime)
│   ├── tier2/
│   │   └── knowledge-graph/     # Learned patterns
│   ├── tier3/
│   │   └── dev-context/         # Development context
│   ├── database/                # SQLite databases
│   └── config/
│       └── master-orchestrator.yaml
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── orchestrators/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── master_orchestrator.py
│   │   │   ├── todo_orchestrator.py
│   │   │   ├── state_manager.py
│   │   │   └── governance_merger.py
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   ├── planning_orchestrator.py
│   │   │   ├── tdd_orchestrator.py
│   │   │   ├── ado_orchestrator.py
│   │   │   ├── vacuum_orchestrator.py
│   │   │   ├── cleanup_orchestrator.py
│   │   │   ├── investigation_orchestrator.py
│   │   │   ├── sanitization_orchestrator.py
│   │   │   ├── debug_orchestrator.py
│   │   │   ├── refinement_orchestrator.py
│   │   │   └── maintenance_orchestrator.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── audit_logger.py
│   │   │   ├── resource_limiter.py
│   │   │   └── silent_executor.py
│   │   └── routing/
│   │       ├── __init__.py
│   │       └── trie_router.py
│   └── mcp/
│       ├── __init__.py
│       └── server.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_master_orchestrator.py
│   │   ├── test_todo_orchestrator.py
│   │   ├── test_state_manager.py
│   │   ├── test_governance_merger.py
│   │   └── orchestrators/
│   │       └── __init__.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_end_to_end.py
│   │   └── test_multi_repo.py
│   ├── performance/
│   │   ├── __init__.py
│   │   └── test_routing_performance.py
│   └── governance/
│       ├── __init__.py
│       └── test_merge_algorithm.py
│
├── .github/
│   └── prompts/
│       └── CORTEX.prompt.md     # Entry point for Copilot
│
├── repos.yaml                   # Multi-repo registry
├── requirements.txt
├── pyproject.toml
├── pytest.ini
└── README.md
```

---

## 📦 Step 3: Initialize Python Environment

**requirements.txt:**
```txt
# Core
pyyaml>=6.0
pathlib>=1.0

# Database
sqlite3  # Built-in

# MCP
jsonrpcserver>=5.0

# Testing
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21

# Type checking
mypy>=1.0

# Utilities
python-dateutil>=2.8
```

**pyproject.toml:**
```toml
[project]
name = "cortex"
version = "6.0.0"
description = "Cognitive Orchestration Runtime for Task Execution and eXpertise"
authors = [{name = "Asif Hussain"}]
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## 🔧 Step 4: Build Core Components (Phase 1)

### 4.1 Entry Point (`src/main.py`)

```python
#!/usr/bin/env python3
"""CORTEX 6.0 - Entry Point

Transforms user requests and routes to appropriate orchestrator.
All orchestrators execute via Python (not Copilot Chat).
"""

import sys
import argparse
from pathlib import Path

from orchestrators.core.master_orchestrator import MasterOrchestrator


def main():
    parser = argparse.ArgumentParser(description="CORTEX 6.0")
    parser.add_argument("request", nargs="?", help="User request to process")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    if not args.request:
        print("Usage: python -m src.main 'your request here'")
        sys.exit(1)
    
    master = MasterOrchestrator()
    result = master.execute(args.request, output_format=args.format)
    print(result)


if __name__ == "__main__":
    main()
```

### 4.2 Master Orchestrator (`src/orchestrators/core/master_orchestrator.py`)

Implement with:
- Pattern matching via Trie router (O(1))
- Governance merger integration
- State management
- Audit logging

**Key Methods:**
```python
class MasterOrchestrator:
    def __init__(self):
        self.router = TrieRouter()
        self.state_manager = StateManager()
        self.governance_merger = GovernanceMerger()
        self.audit_logger = AuditLogger()
    
    def execute(self, request: str, output_format: str = "markdown") -> str:
        """Execute user request through orchestration pipeline."""
        # 1. Log audit entry
        # 2. Load unified instruction set
        # 3. Route to orchestrator
        # 4. Execute and return result
        pass
    
    def _route(self, request: str) -> tuple[str, dict]:
        """Route request to appropriate orchestrator."""
        pass
```

### 4.3 TODO Orchestrator (`src/orchestrators/core/todo_orchestrator.py`)

**DAG-Based Work Tracking:**

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import uuid


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    id: str
    title: str
    status: TaskStatus
    dependencies: list[str]  # IDs of tasks this depends on
    metadata: dict
    created_at: str
    updated_at: str


class TodoOrchestrator:
    """DAG-based work tracking with smart dependency management."""
    
    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.dag: dict[str, TaskNode] = {}
    
    def add_task(self, title: str, dependencies: list[str] = None) -> str:
        """Add task to DAG, return task ID."""
        pass
    
    def get_ready_tasks(self) -> list[TaskNode]:
        """Return tasks with all dependencies satisfied."""
        pass
    
    def detect_circular_dependencies(self) -> list[list[str]]:
        """DFS cycle detection, return cycles found."""
        pass
    
    def calculate_progress(self) -> dict:
        """Calculate overall progress metrics."""
        pass
```

### 4.4 State Manager (`src/orchestrators/core/state_manager.py`)

**SQLite with WAL + Optimistic Locking:**

```python
import sqlite3
from pathlib import Path
from contextlib import contextmanager


class StateManager:
    """Persistent state with SQLite WAL and optimistic locking."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path("cortex-brain/database/cortex.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite with WAL mode."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        self._create_tables(conn)
        conn.close()
    
    def _create_tables(self, conn):
        """Create all required tables."""
        # See machine-readable/03-database-schema.sql
        pass
    
    @contextmanager
    def transaction(self):
        """Context manager for atomic transactions."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def save_with_optimistic_lock(self, table: str, data: dict, version: int) -> bool:
        """Save with optimistic locking, return success."""
        pass
```

### 4.5 Governance Merger (`src/orchestrators/core/governance_merger.py`)

**4-Category Intelligent Merging:**

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import yaml


class RuleSource(Enum):
    CORTEX_TIER0 = "cortex_tier0"
    BUSINESS_TIER0 = "business_tier0"
    COMPANY_PRACTICES = "company_practices"
    KNOWLEDGE_PATTERNS = "knowledge_patterns"


class RuleType(Enum):
    COMPLIANCE = "compliance"
    SECURITY = "security"
    ENGINEERING = "engineering"
    ADVISORY = "advisory"


@dataclass
class GovernanceRule:
    id: str
    source: RuleSource
    rule_type: RuleType
    content: dict
    priority: int
    override_allowed: bool


class GovernanceMerger:
    """4-Category Intelligent Governance Merger."""
    
    def __init__(self):
        self.cortex_tier0_path = Path("cortex-brain/tier0/governance/core-rules.yaml")
    
    def merge(self, repo_path: Path = None) -> dict:
        """
        Merge 4 governance sources into Unified Instruction Set.
        
        Algorithm:
        1. Load all sources
        2. Categorize rules by type
        3. Detect conflicts
        4. Resolve conflicts (priority-based)
        5. Generate unified instruction set
        6. Validate no contradictions
        """
        pass
    
    def _load_cortex_tier0(self) -> list[GovernanceRule]:
        """Load CORTEX Tier 0 (61 SKULL rules)."""
        pass
    
    def _load_business_tier0(self, repo_path: Path) -> list[GovernanceRule]:
        """Load Business Tier 0 from repo."""
        pass
    
    def _detect_conflicts(self, rules: list[GovernanceRule]) -> list[dict]:
        """Detect conflicts between rules from different sources."""
        pass
    
    def _resolve_conflicts(self, conflicts: list[dict]) -> list[GovernanceRule]:
        """
        Resolve conflicts:
        - COMPLIANCE: Business wins
        - EXTENSION: CORTEX wins, log warning
        - ADVISORY: Active rule wins, demote to suggestion
        """
        pass
```

---

## 🧪 Step 5: Implement Tests (Phase 1)

### 5.1 Test Configuration (`tests/conftest.py`)

```python
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_db():
    """Provide temporary database for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield db_path


@pytest.fixture
def sample_governance_rules():
    """Provide sample governance rules for testing."""
    return {
        "cortex_tier0": [...],
        "business_tier0": [...],
        "company_practices": [...],
        "knowledge_patterns": [...]
    }
```

### 5.2 Unit Test Example (`tests/unit/test_todo_orchestrator.py`)

```python
import pytest
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, TaskStatus


class TestTodoOrchestrator:
    
    def test_add_task_returns_id(self, temp_db):
        """Adding a task returns a valid UUID."""
        todo = TodoOrchestrator(state_manager=MockStateManager(temp_db))
        task_id = todo.add_task("Test task")
        assert task_id is not None
        assert len(task_id) == 36  # UUID format
    
    def test_get_ready_tasks_respects_dependencies(self, temp_db):
        """Ready tasks only returned when dependencies satisfied."""
        todo = TodoOrchestrator(state_manager=MockStateManager(temp_db))
        task1 = todo.add_task("First task")
        task2 = todo.add_task("Second task", dependencies=[task1])
        
        ready = todo.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == task1
    
    def test_detect_circular_dependencies(self, temp_db):
        """Circular dependencies are detected."""
        todo = TodoOrchestrator(state_manager=MockStateManager(temp_db))
        # Create circular: A -> B -> C -> A
        task_a = todo.add_task("A")
        task_b = todo.add_task("B", dependencies=[task_a])
        task_c = todo.add_task("C", dependencies=[task_b])
        # This should fail or return cycle
        cycles = todo.detect_circular_dependencies()
        # Verify cycle detection logic
```

---

## 🌐 Step 6: Implement MCP Server (Phase 3)

### 6.1 MCP Server (`src/mcp/server.py`)

```python
"""CORTEX MCP Server - JSON-RPC 2.0 API."""

from jsonrpcserver import method, serve, Success, Error


@method
def cortex_plan(feature: str, context: dict = None) -> dict:
    """Create execution plan for feature."""
    # Route to PlanningOrchestrator
    pass


@method
def cortex_todo_create(title: str, dependencies: list = None) -> dict:
    """Create TODO in DAG."""
    pass


@method
def cortex_todo_list(status: str = None) -> list:
    """List TODOs, optionally filtered by status."""
    pass


@method
def cortex_governance_merge(repo_path: str = None) -> dict:
    """Merge governance rules and return unified instruction set."""
    pass


@method
def cortex_orchestrator_execute(orchestrator: str, params: dict) -> dict:
    """Execute specific orchestrator with params."""
    pass


def start_server(host: str = "localhost", port: int = 5000):
    """Start MCP server."""
    serve(host, port)


if __name__ == "__main__":
    start_server()
```

---

## 📊 Step 7: Database Schema

Execute the schema from `machine-readable/03-database-schema.sql`:

```sql
-- Enable WAL mode
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;

-- Tasks table (DAG nodes)
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    dependencies TEXT,  -- JSON array of task IDs
    metadata TEXT,      -- JSON object
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,
    orchestrator TEXT NOT NULL,
    request TEXT,
    result TEXT,
    user_context TEXT
);

-- Governance rules table
CREATE TABLE IF NOT EXISTS governance_rules (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    content TEXT NOT NULL,  -- JSON
    priority INTEGER NOT NULL,
    override_allowed INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 1
);

-- State checkpoints table
CREATE TABLE IF NOT EXISTS checkpoints (
    id TEXT PRIMARY KEY,
    orchestrator TEXT NOT NULL,
    state TEXT NOT NULL,  -- JSON
    created_at TEXT NOT NULL
);
```

---

## ✅ Step 8: Validation Gates

After each phase, validate:

### Phase 1 Gate (Core Components)
- [ ] `python -m src.main "help"` returns command list
- [ ] All unit tests pass: `pytest tests/unit/ -v`
- [ ] Database creates with WAL mode
- [ ] TODO DAG supports add/query/dependencies

### Phase 2 Gate (Resilience)
- [ ] Trie router achieves O(1) < 5ms
- [ ] State persistence < 100ms
- [ ] Rollback recovers from failure

### Phase 3 Gate (MCP)
- [ ] MCP server responds to JSON-RPC
- [ ] Multi-repo operations work
- [ ] Governance merge produces valid output

### Phase 4 Gate (Final)
- [ ] All tests pass (80%+ coverage)
- [ ] All 25 edge cases mitigated
- [ ] Performance SLAs met
- [ ] Documentation complete

---

## 🎯 Build Command Summary

```bash
# 1. Backup (if needed)
./implementation-plan/01-BACKUP-MIGRATION.sh

# 2. Create folder structure
# (Use file creation tools or scripts)

# 3. Initialize Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run tests (TDD)
pytest tests/ -v --cov=src

# 5. Start MCP server
python -m src.mcp.server

# 6. Validate
python -m src.main "help"
```

---

## 📚 Reference Documents

- **Master Spec:** `00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml`
- **Database Schema:** `machine-readable/03-database-schema.sql`
- **Component Specs:** `machine-readable/02-component-specs.yaml`
- **Test Specs:** `machine-readable/07-test-specifications.yaml`

---

**When building, execute phases sequentially. Each phase builds on the previous.**

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
