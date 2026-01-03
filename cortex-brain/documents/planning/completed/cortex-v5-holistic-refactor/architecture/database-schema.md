# Database Schema Design

**Document Type:** Technical Specification  
**Plan:** CORTEX v5.0 Holistic Refactor  
**Created:** January 2, 2026

---

## 🗄️ Overview

The Planning State Database provides a single source of truth for all orchestrator execution state, enabling atomic phase operations, failure recovery, and complete audit trails.

**Technology:** SQLite (ACID transactions, embedded, zero-config)  
**Location:** `cortex-brain/database/planning_state.db`

---

## 📐 Schema Definition

### Table: plans

**Purpose:** Top-level plan tracking

```sql
CREATE TABLE plans (
    plan_id TEXT PRIMARY KEY,
    feature_name TEXT NOT NULL,
    orchestrator_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PAUSED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration_days INTEGER,
    actual_duration_days INTEGER,
    complexity_tier INTEGER CHECK(complexity_tier BETWEEN 1 AND 5),
    strategy_notes TEXT,
    created_by TEXT DEFAULT 'planning_orchestrator_v5'
);

CREATE INDEX idx_plans_status ON plans(status);
CREATE INDEX idx_plans_created_at ON plans(created_at);
```

**Example Row:**
```json
{
  "plan_id": "cortex-v5-holistic-refactor",
  "feature_name": "Pure Autonomous Architecture",
  "orchestrator_name": "planning_orchestrator_v5",
  "status": "IN_PROGRESS",
  "created_at": "2026-01-02T00:00:00Z",
  "estimated_duration_days": 35,
  "complexity_tier": 5
}
```

### Table: phases

**Purpose:** Phase-level execution tracking

```sql
CREATE TABLE phases (
    phase_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    phase_order INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'SKIPPED')),
    progress_percent INTEGER DEFAULT 0 CHECK(progress_percent BETWEEN 0 AND 100),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration_hours REAL,
    actual_duration_hours REAL,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);

CREATE INDEX idx_phases_plan_id ON phases(plan_id);
CREATE INDEX idx_phases_status ON phases(status);
CREATE INDEX idx_phases_order ON phases(plan_id, phase_order);
```

**Example Row:**
```json
{
  "phase_id": "cortex-v5-holistic-refactor-phase-0",
  "plan_id": "cortex-v5-holistic-refactor",
  "name": "Foundation Setup",
  "phase_order": 0,
  "status": "NOT_STARTED",
  "progress_percent": 0,
  "estimated_duration_hours": 8
}
```

### Table: tasks

**Purpose:** Task-level work item tracking

```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL,
    description TEXT NOT NULL,
    task_order INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'BLOCKED')),
    estimated_hours REAL,
    actual_hours REAL,
    assigned_to TEXT,
    dependencies TEXT, -- JSON array of task_ids
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_phase_id ON tasks(phase_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

### Table: artifacts

**Purpose:** Generated file tracking

```sql
CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    artifact_type TEXT NOT NULL CHECK(artifact_type IN ('context', 'report', 'code', 'config', 'documentation', 'test')),
    file_path TEXT NOT NULL,
    template_used TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size_bytes INTEGER,
    checksum TEXT,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE SET NULL
);

CREATE INDEX idx_artifacts_plan_id ON artifacts(plan_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
```

**Example Row:**
```json
{
  "artifact_id": "artifact-master-plan-001",
  "plan_id": "cortex-v5-holistic-refactor",
  "phase_id": "cortex-v5-holistic-refactor-phase-0",
  "artifact_type": "documentation",
  "file_path": "00-MASTER-PLAN-V5.md",
  "template_used": "templates/master-plan-v5.jinja2",
  "generated_at": "2026-01-02T00:00:00Z"
}
```

### Table: validations

**Purpose:** Validation checkpoint tracking

```sql
CREATE TABLE validations (
    validation_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL,
    check_name TEXT NOT NULL,
    check_type TEXT NOT NULL CHECK(check_type IN ('file_exists', 'json_schema', 'markdown_headers', 'test_pass', 'custom')),
    passed BOOLEAN NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    details TEXT, -- JSON with check-specific data
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

CREATE INDEX idx_validations_phase_id ON validations(phase_id);
CREATE INDEX idx_validations_passed ON validations(passed);
```

### Table: state_snapshots

**Purpose:** Point-in-time state capture for recovery

```sql
CREATE TABLE state_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    snapshot_type TEXT NOT NULL CHECK(snapshot_type IN ('pre_phase', 'post_phase', 'error', 'manual')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state_data TEXT NOT NULL, -- JSON snapshot of plan state
    file_system_manifest TEXT, -- JSON list of files created
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

CREATE INDEX idx_snapshots_plan_id ON state_snapshots(plan_id);
CREATE INDEX idx_snapshots_type ON state_snapshots(snapshot_type);
```

---

## 🔄 Transaction Patterns

### Pattern 1: Phase Execution with Rollback

```python
def execute_phase(self, phase_config: dict):
    with self.db.transaction() as tx:
        # Update phase status
        tx.execute("""
            UPDATE phases 
            SET status = 'IN_PROGRESS', started_at = ? 
            WHERE phase_id = ?
        """, (datetime.now(), phase_config['id']))
        
        try:
            # Create snapshot
            snapshot_id = self.create_snapshot(tx, phase_config['id'], 'pre_phase')
            
            # Execute phase logic
            results = self.execute_phase_logic(phase_config)
            
            # Record artifacts
            for artifact in results['artifacts']:
                tx.execute("""
                    INSERT INTO artifacts (artifact_id, plan_id, phase_id, artifact_type, file_path, template_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (artifact['id'], self.plan_id, phase_config['id'], artifact['type'], artifact['path'], artifact['template']))
            
            # Run validations
            validation_results = self.validate_phase(tx, phase_config)
            
            if all(v['passed'] for v in validation_results):
                # Mark phase complete
                tx.execute("""
                    UPDATE phases 
                    SET status = 'COMPLETED', completed_at = ?, progress_percent = 100 
                    WHERE phase_id = ?
                """, (datetime.now(), phase_config['id']))
                
                # Create post-phase snapshot
                self.create_snapshot(tx, phase_config['id'], 'post_phase')
            else:
                raise ValidationError("Phase validation failed")
                
        except Exception as e:
            # Rollback will happen automatically
            self.create_snapshot(tx, phase_config['id'], 'error')
            tx.execute("""
                UPDATE phases 
                SET status = 'FAILED' 
                WHERE phase_id = ?
            """, (phase_config['id'],))
            raise
```

### Pattern 2: Recovery from Snapshot

```python
def recover_from_failure(self, plan_id: str, target_snapshot_id: str = None):
    # Get latest successful snapshot if not specified
    if not target_snapshot_id:
        snapshot = self.db.query("""
            SELECT * FROM state_snapshots 
            WHERE plan_id = ? AND snapshot_type = 'post_phase'
            ORDER BY created_at DESC LIMIT 1
        """, (plan_id,))
    else:
        snapshot = self.db.query("""
            SELECT * FROM state_snapshots 
            WHERE snapshot_id = ?
        """, (target_snapshot_id,))
    
    # Restore state
    state_data = json.loads(snapshot['state_data'])
    file_manifest = json.loads(snapshot['file_system_manifest'])
    
    # Restore database state
    with self.db.transaction() as tx:
        # Reset phase statuses
        for phase in state_data['phases']:
            tx.execute("""
                UPDATE phases 
                SET status = ?, progress_percent = ?, started_at = ?, completed_at = ?
                WHERE phase_id = ?
            """, (phase['status'], phase['progress'], phase['started_at'], phase['completed_at'], phase['id']))
    
    # Restore filesystem
    for file_entry in file_manifest:
        if file_entry['action'] == 'created' and not os.path.exists(file_entry['path']):
            # Recreate file from backup
            self.restore_file(file_entry['path'], file_entry['backup_path'])
```

---

## 📊 Query Examples

### Get Plan Progress

```sql
SELECT 
    p.plan_id,
    p.feature_name,
    p.status,
    COUNT(ph.phase_id) as total_phases,
    SUM(CASE WHEN ph.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_phases,
    AVG(ph.progress_percent) as overall_progress
FROM plans p
LEFT JOIN phases ph ON p.plan_id = ph.plan_id
WHERE p.plan_id = ?
GROUP BY p.plan_id;
```

### Get Current Phase Details

```sql
SELECT 
    ph.name,
    ph.status,
    ph.progress_percent,
    COUNT(t.task_id) as total_tasks,
    SUM(CASE WHEN t.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_tasks
FROM phases ph
LEFT JOIN tasks t ON ph.phase_id = t.phase_id
WHERE ph.plan_id = ? AND ph.status = 'IN_PROGRESS'
GROUP BY ph.phase_id;
```

### Get Failed Validations

```sql
SELECT 
    ph.name as phase_name,
    v.check_name,
    v.error_message,
    v.executed_at
FROM validations v
JOIN phases ph ON v.phase_id = ph.phase_id
WHERE ph.plan_id = ? AND v.passed = 0
ORDER BY v.executed_at DESC;
```

### Get Artifact Summary

```sql
SELECT 
    artifact_type,
    COUNT(*) as count,
    SUM(file_size_bytes) as total_size_bytes
FROM artifacts
WHERE plan_id = ?
GROUP BY artifact_type;
```

---

## 🔧 Migration Script

```python
# migrate_to_planning_state_db.py

import sqlite3
from pathlib import Path

def create_database(db_path: Path):
    """Create planning state database with schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables (schema definitions above)
    # ... execute CREATE TABLE statements ...
    
    conn.commit()
    conn.close()

def migrate_existing_plans(db_path: Path, plans_dir: Path):
    """Migrate existing JSON/markdown plans to database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for plan_dir in plans_dir.glob("*/"):
        master_plan = plan_dir / "00-master-plan.md"
        tracking_json = plan_dir / "tracking" / "progress-tracker.json"
        
        if master_plan.exists():
            # Parse markdown to extract plan metadata
            plan_data = parse_master_plan(master_plan)
            
            # Insert plan record
            cursor.execute("""
                INSERT INTO plans (plan_id, feature_name, status, created_at, complexity_tier)
                VALUES (?, ?, ?, ?, ?)
            """, (plan_data['id'], plan_data['feature'], plan_data['status'], 
                  plan_data['created'], plan_data['complexity']))
            
            # Insert phases
            for phase in plan_data['phases']:
                cursor.execute("""
                    INSERT INTO phases (phase_id, plan_id, name, phase_order, status, progress_percent)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (phase['id'], plan_data['id'], phase['name'], 
                      phase['order'], phase['status'], phase['progress']))
    
    conn.commit()
    conn.close()
```

---

## ✅ Benefits

1. **Atomic Operations** - Phase execution is all-or-nothing via transactions
2. **Recovery** - Rollback to any snapshot on failure
3. **Audit Trail** - Complete history of plan execution
4. **Query Performance** - SQL queries instead of parsing markdown/JSON
5. **Single Source of Truth** - No state fragmentation
6. **Observable State** - Real-time progress queries
7. **Testability** - Mock database, verify state changes

---

## 📚 References

- SQLite ACID transactions: https://www.sqlite.org/transactional.html
- Planning State Database implementation: `future-structure/src/database/planning_state.py`
- Migration script: `future-structure/scripts/migrate_planning_db.py`
