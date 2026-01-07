-- ADO Planning System Schema
-- CORTEX 2.1 - Simplified ADO Tracking
-- Created: 2025-11-17

-- Main ADO items table
CREATE TABLE IF NOT EXISTS ado_items (
    id TEXT PRIMARY KEY,              -- UUID (e.g., "a1b2c3d4-e5f6-7890-1234-567890abcdef")
    ado_number TEXT UNIQUE NOT NULL,  -- User-provided ADO number (e.g., "ADO-12345")
    type TEXT NOT NULL,               -- "Bug", "Feature", or "Task"
    acceptance_criteria TEXT NOT NULL, -- JSON array of acceptance criteria
    technical_notes TEXT,             -- Optional implementation context
    generated_dod TEXT NOT NULL,      -- JSON array of DoD items (auto-generated from type)
    status TEXT DEFAULT 'planning',   -- "planning", "in-progress", "blocked", "completed"
    file_path TEXT NOT NULL,          -- Path to markdown file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CHECK (type IN ('Bug', 'Feature', 'Task')),
    CHECK (status IN ('planning', 'in-progress', 'blocked', 'completed'))
);

-- Index for fast ADO number lookup
CREATE INDEX IF NOT EXISTS idx_ado_number ON ado_items(ado_number);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_ado_status ON ado_items(status);

-- Index for type-based queries
CREATE INDEX IF NOT EXISTS idx_ado_type ON ado_items(type);

-- ADO activity log (track status changes and updates)
CREATE TABLE IF NOT EXISTS ado_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ado_id TEXT NOT NULL,             -- Foreign key to ado_items.id
    activity_type TEXT NOT NULL,      -- "created", "status_changed", "updated", "completed"
    old_value TEXT,                   -- Previous value (for changes)
    new_value TEXT,                   -- New value (for changes)
    notes TEXT,                       -- Optional activity notes
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ado_id) REFERENCES ado_items(id) ON DELETE CASCADE
);

-- Index for activity lookups
CREATE INDEX IF NOT EXISTS idx_activity_ado_id ON ado_activity(ado_id);

-- DoD completion tracking (checkboxes in generated DoD)
CREATE TABLE IF NOT EXISTS ado_dod_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ado_id TEXT NOT NULL,             -- Foreign key to ado_items.id
    dod_item TEXT NOT NULL,           -- DoD checklist item text
    is_completed BOOLEAN DEFAULT 0,   -- 0 = unchecked, 1 = checked
    completed_at TIMESTAMP,
    FOREIGN KEY (ado_id) REFERENCES ado_items(id) ON DELETE CASCADE
);

-- Index for DoD item lookups
CREATE INDEX IF NOT EXISTS idx_dod_ado_id ON ado_dod_items(ado_id);

-- File relationships (track files modified during ADO work)
CREATE TABLE IF NOT EXISTS ado_file_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ado_id TEXT NOT NULL,             -- Foreign key to ado_items.id
    file_path TEXT NOT NULL,          -- Relative path to modified file
    relationship_type TEXT NOT NULL,  -- "created", "modified", "deleted", "tested"
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ado_id) REFERENCES ado_items(id) ON DELETE CASCADE
);

-- Index for file relationship lookups
CREATE INDEX IF NOT EXISTS idx_file_rel_ado_id ON ado_file_relationships(ado_id);

-- Trigger: Update updated_at timestamp on changes
CREATE TRIGGER IF NOT EXISTS update_ado_timestamp 
AFTER UPDATE ON ado_items
FOR EACH ROW
BEGIN
    UPDATE ado_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Log status changes automatically
CREATE TRIGGER IF NOT EXISTS log_status_change 
AFTER UPDATE OF status ON ado_items
FOR EACH ROW
WHEN NEW.status != OLD.status
BEGIN
    INSERT INTO ado_activity (ado_id, activity_type, old_value, new_value, notes)
    VALUES (NEW.id, 'status_changed', OLD.status, NEW.status, 'Status changed from ' || OLD.status || ' to ' || NEW.status);
END;

-- Trigger: Set completed_at timestamp when status becomes "completed"
CREATE TRIGGER IF NOT EXISTS set_completed_timestamp 
AFTER UPDATE OF status ON ado_items
FOR EACH ROW
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE ado_items SET completed_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Views for common queries

-- Active ADO items (not completed)
CREATE VIEW IF NOT EXISTS active_ados AS
SELECT 
    id,
    ado_number,
    type,
    status,
    created_at,
    updated_at
FROM ado_items
WHERE status != 'completed'
ORDER BY created_at DESC;

-- Completed ADO items
CREATE VIEW IF NOT EXISTS completed_ados AS
SELECT 
    id,
    ado_number,
    type,
    completed_at,
    created_at
FROM ado_items
WHERE status = 'completed'
ORDER BY completed_at DESC;

-- ADO summary statistics
CREATE VIEW IF NOT EXISTS ado_stats AS
SELECT 
    type,
    status,
    COUNT(*) as count
FROM ado_items
GROUP BY type, status;
