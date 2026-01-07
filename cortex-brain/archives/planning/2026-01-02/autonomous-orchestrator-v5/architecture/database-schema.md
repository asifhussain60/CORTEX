# Planning State Database Schema

**Database:** `planning_state.db`  
**Location:** `cortex-brain/database/`  
**Engine:** SQLite 3.x  
**Purpose:** Single source of truth for all planning orchestrator state

---

## 🎯 Design Principles

1. **Atomic Operations** - Each phase execution is a transaction
2. **Point-in-Time Recovery** - Snapshots enable rollback to any state
3. **Audit Trail** - Complete history of all operations
4. **Query Performance** - Indexed for fast progress queries
5. **Extensibility** - Schema supports future orchestrator types

---

## 📊 Schema Diagram

```
┌─────────────┐
│   plans     │
│ (plan_id PK)│
└──────┬──────┘
       │ 1:N
       ↓
┌─────────────┐       ┌──────────────┐
│   phases    │       │  artifacts   │
│(phase_id PK)│←─────→│(artifact_id) │
└──────┬──────┘  N:N  └──────────────┘
       │ 1:N
       ↓
┌─────────────┐
│   tasks     │
│(task_id PK) │
└─────────────┘

┌──────────────────┐       ┌─────────────────┐
│  validations     │       │ state_snapshots │
│(validation_id PK)│       │ (snapshot_id PK)│
└──────────────────┘       └─────────────────┘
```

---

## 📋 Table Definitions

### `plans`

Stores high-level plan metadata.

```sql
CREATE TABLE plans (
    plan_id TEXT PRIMARY KEY,
    feature_name TEXT NOT NULL,
    plan_type TEXT NOT NULL DEFAULT 'feature',
    status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'failed', 'archived')),
    complexity_tier INTEGER CHECK (complexity_tier BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_days INTEGER,
    actual_days REAL,
    created_by TEXT DEFAULT 'cortex',
    metadata JSON,
    UNIQUE (feature_name, status)
);

CREATE INDEX idx_plans_status ON plans(status);
CREATE INDEX idx_plans_created ON plans(created_at DESC);
```

**Fields:**
- `plan_id` - Unique identifier (e.g., `user-authentication-plan`)
- `feature_name` - Human-readable name
- `plan_type` - `feature`, `bugfix`, `refactor`, `documentation`
- `status` - Current state
- `metadata` - JSON blob for extensibility

### `phases`

Individual execution phases within a plan.

```sql
CREATE TABLE phases (
    phase_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES plans(plan_id) ON DELETE CASCADE,
    phase_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_hours REAL,
    actual_hours REAL,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    config JSON,
    UNIQUE (plan_id, phase_number)
);

CREATE INDEX idx_phases_plan ON phases(plan_id, phase_number);
CREATE INDEX idx_phases_status ON phases(status);
```

**Fields:**
- `phase_id` - `{plan_id}-phase-{number}`
- `phase_number` - Sequential order (0, 1, 2...)
- `config` - Phase-specific configuration from manifest
- `retry_count` - For automatic retry logic

### `tasks`

Granular tasks within each phase.

```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL REFERENCES phases(phase_id) ON DELETE CASCADE,
    task_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    task_type TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_minutes REAL,
    actual_minutes REAL,
    dependencies JSON,
    results JSON,
    UNIQUE (phase_id, task_number)
);

CREATE INDEX idx_tasks_phase ON tasks(phase_id, task_number);
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Fields:**
- `dependencies` - JSON array of task_ids that must complete first
- `results` - JSON output from task execution (files created, data extracted)

### `artifacts`

Registry of all generated files and outputs.

```sql
CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES plans(plan_id) ON DELETE CASCADE,
    phase_id TEXT REFERENCES phases(phase_id),
    artifact_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    UNIQUE (plan_id, file_path)
);

CREATE INDEX idx_artifacts_plan ON artifacts(plan_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
```

**Fields:**
- `artifact_type` - `master_plan`, `progress_tracker`, `context_summary`, `report`
- `checksum` - SHA256 for integrity validation
- `metadata` - Template used, generation params

### `validations`

Results of validation checkpoints.

```sql
CREATE TABLE validations (
    validation_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL REFERENCES phases(phase_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    check_type TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    expected_value TEXT,
    actual_value TEXT
);

CREATE INDEX idx_validations_phase ON validations(phase_id);
CREATE INDEX idx_validations_passed ON validations(passed);
```

**Fields:**
- `check_type` - `folder_exists`, `file_created`, `schema_valid`, `test_passed`
- `details` - Explanation of failure or success

### `state_snapshots`

Point-in-time captures for rollback capability.

```sql
CREATE TABLE state_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES plans(plan_id) ON DELETE CASCADE,
    phase_id TEXT REFERENCES phases(phase_id),
    snapshot_type TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state_data JSON NOT NULL,
    file_checksums JSON
);

CREATE INDEX idx_snapshots_plan ON state_snapshots(plan_id, captured_at DESC);
```

**Fields:**
- `snapshot_type` - `pre_phase`, `post_phase`, `error_state`, `manual`
- `state_data` - Complete orchestrator state (variables, context, config)
- `file_checksums` - All artifact checksums for integrity validation

---

## 🔄 Transaction Patterns

### Phase Execution Transaction

```python
def execute_phase(plan_id: str, phase_number: int):
    with database.transaction():
        # 1. Create snapshot
        snapshot_id = create_snapshot(plan_id, phase_id, 'pre_phase')
        
        # 2. Update phase status
        update_phase(phase_id, status='running', started_at=now())
        
        # 3. Execute tasks
        for task in get_phase_tasks(phase_id):
            execute_task(task)
        
        # 4. Run validations
        for validation in get_phase_validations(phase_id):
            result = run_validation(validation)
            if not result.passed:
                raise ValidationError(result.details)
        
        # 5. Update phase status
        update_phase(phase_id, status='completed', completed_at=now())
        
        # 6. Create post-snapshot
        create_snapshot(plan_id, phase_id, 'post_phase')
```

**On Failure:**
- Transaction rolls back automatically
- Phase status remains `pending` or reverts to `failed`
- Pre-phase snapshot preserved for recovery
- Error captured in `phases.error_message`

### Rollback to Snapshot

```python
def rollback_to_snapshot(snapshot_id: str):
    with database.transaction():
        snapshot = get_snapshot(snapshot_id)
        
        # 1. Restore database state
        restore_state_from_json(snapshot.state_data)
        
        # 2. Verify file checksums
        verify_artifacts(snapshot.file_checksums)
        
        # 3. Mark subsequent phases as pending
        reset_phases_after(snapshot.phase_id)
        
        # 4. Create rollback record
        create_snapshot(plan_id, snapshot.phase_id, 'rollback')
```

---

## 📈 Progress Queries

### Overall Plan Progress

```sql
SELECT 
    p.plan_id,
    p.feature_name,
    p.status,
    COUNT(ph.phase_id) as total_phases,
    SUM(CASE WHEN ph.status = 'completed' THEN 1 ELSE 0 END) as completed_phases,
    COUNT(t.task_id) as total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) / COUNT(t.task_id), 1) as progress_percentage
FROM plans p
LEFT JOIN phases ph ON p.plan_id = ph.plan_id
LEFT JOIN tasks t ON ph.phase_id = t.phase_id
WHERE p.plan_id = ?
GROUP BY p.plan_id;
```

### Current Phase Status

```sql
SELECT 
    ph.name,
    ph.status,
    ph.started_at,
    ph.estimated_hours,
    ROUND((JULIANDAY('now') - JULIANDAY(ph.started_at)) * 24, 2) as hours_elapsed,
    COUNT(t.task_id) as total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
FROM phases ph
LEFT JOIN tasks t ON ph.phase_id = t.phase_id
WHERE ph.plan_id = ? AND ph.status = 'running'
GROUP BY ph.phase_id;
```

### Failed Validations

```sql
SELECT 
    v.check_name,
    v.check_type,
    v.details,
    v.expected_value,
    v.actual_value,
    ph.name as phase_name
FROM validations v
JOIN phases ph ON v.phase_id = ph.phase_id
WHERE ph.plan_id = ? AND v.passed = 0
ORDER BY v.executed_at DESC;
```

---

## 🔧 Database Operations API

### Python Interface

```python
class PlanningDatabase:
    def create_plan(self, feature_name: str, metadata: dict) -> str:
        """Create new plan, return plan_id"""
        
    def get_plan_status(self, plan_id: str) -> dict:
        """Return current plan state with progress"""
        
    def start_phase(self, phase_id: str) -> None:
        """Mark phase as running, create pre-snapshot"""
        
    def complete_phase(self, phase_id: str) -> None:
        """Mark phase as completed, create post-snapshot"""
        
    def fail_phase(self, phase_id: str, error: str) -> None:
        """Mark phase as failed, capture error state"""
        
    def create_artifact(self, plan_id: str, artifact_type: str, file_path: str) -> str:
        """Register generated artifact"""
        
    def run_validation(self, phase_id: str, check_name: str, check_type: str, passed: bool, details: str) -> None:
        """Record validation result"""
        
    def create_snapshot(self, plan_id: str, phase_id: str, snapshot_type: str, state_data: dict) -> str:
        """Capture current state"""
        
    def rollback_to_snapshot(self, snapshot_id: str) -> None:
        """Restore state from snapshot"""
        
    def get_progress(self, plan_id: str) -> dict:
        """Calculate progress metrics"""
```

---

## 🚀 Migration Strategy

### Initial Setup

```python
def initialize_database():
    """Create all tables and indexes"""
    conn = sqlite3.connect('planning_state.db')
    with open('schema.sql') as f:
        conn.executescript(f.read())
    conn.commit()
```

### Migrate Existing Plans

```python
def migrate_legacy_plan(plan_folder: str):
    """Convert JSON-based plan to database"""
    # 1. Read progress-tracker.json
    # 2. Create plan record
    # 3. Create phase records
    # 4. Register artifacts from folder scan
    # 5. Create snapshot of current state
```

---

## 📊 Benefits Summary

| Capability | Before (JSON files) | After (Database) |
|------------|--------------------|--------------------|
| **State Query** | Parse multiple files | Single SQL query |
| **Progress Calc** | Manual aggregation | Automatic with views |
| **Failure Recovery** | Restart from scratch | Rollback transaction |
| **Audit Trail** | None | Complete history |
| **Concurrent Access** | File locks | ACID transactions |
| **Validation** | Manual checks | Automated with schema |

---

**Schema Version:** 1.0  
**Last Updated:** January 2, 2026  
**Status:** Ready for implementation
