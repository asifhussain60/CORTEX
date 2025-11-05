-- ============================================================================
-- CORTEX Unified Cognitive Database Schema
-- ============================================================================
-- Version: 2.0
-- Date: 2025-11-05
-- Database: cortex-brain.db (Single SQLite file for all tiers)
-- Performance Target: All queries <200ms, most <50ms
-- Storage Target: <250KB total
-- ============================================================================

-- ============================================================================
-- TIER 0: GOVERNANCE (Instinct Layer)
-- ============================================================================
-- Purpose: Immutable rules that govern CORTEX behavior
-- Performance: <1ms rule lookups (indexed)
-- Size: ~30-40KB
-- ============================================================================

-- Core Rules Table
CREATE TABLE IF NOT EXISTS governance_rules (
    id TEXT PRIMARY KEY,                    -- Rule identifier (e.g., 'TEST_FIRST_TDD')
    number INTEGER UNIQUE NOT NULL,         -- Rule number (1-28)
    severity TEXT NOT NULL CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    category TEXT NOT NULL,                 -- Quality, protection, architecture, etc.
    name TEXT NOT NULL,                     -- Human-readable name
    description TEXT NOT NULL,              -- What the rule does
    immutable BOOLEAN DEFAULT TRUE,         -- Can this rule be changed?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version TEXT DEFAULT '1.0'
);

-- Rule Details (Normalized)
CREATE TABLE IF NOT EXISTS governance_rule_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL REFERENCES governance_rules(id) ON DELETE CASCADE,
    requirement TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    category TEXT                           -- Workflow, enforcement, etc.
);

CREATE TABLE IF NOT EXISTS governance_rule_enforcement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL REFERENCES governance_rules(id) ON DELETE CASCADE,
    agent TEXT,                             -- Which agent enforces this
    validation_point TEXT,                  -- When to check (pre-commit, etc.)
    blocker BOOLEAN DEFAULT FALSE,          -- Does it block execution?
    bypass_allowed BOOLEAN DEFAULT FALSE
);

-- Rule Violations (Audit Log)
CREATE TABLE IF NOT EXISTS governance_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL REFERENCES governance_rules(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT,                           -- What triggered violation
    severity TEXT,
    resolution TEXT,                        -- How was it resolved
    resolved_at TIMESTAMP
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_governance_rules_category ON governance_rules(category);
CREATE INDEX IF NOT EXISTS idx_governance_rules_severity ON governance_rules(severity);
CREATE INDEX IF NOT EXISTS idx_governance_violations_rule ON governance_violations(rule_id);
CREATE INDEX IF NOT EXISTS idx_governance_violations_timestamp ON governance_violations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_governance_violations_unresolved ON governance_violations(resolved_at) WHERE resolved_at IS NULL;

-- ============================================================================
-- TIER 1: WORKING MEMORY (Short-Term Memory)
-- ============================================================================
-- Purpose: Last 50 conversations with entity extraction
-- Performance: <50ms conversation queries (indexed)
-- Size: ~80-100KB (FIFO queue management)
-- ============================================================================

-- Conversations Table
CREATE TABLE IF NOT EXISTS working_memory_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT UNIQUE NOT NULL,   -- UUID
    title TEXT,
    intent TEXT,                            -- PLAN, EXECUTE, TEST, etc.
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'archived')),
    outcome TEXT,                           -- success, failed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    pattern_extracted BOOLEAN DEFAULT FALSE -- Has Tier 2 extracted patterns?
);

-- Messages Table (normalized)
CREATE TABLE IF NOT EXISTS working_memory_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL REFERENCES working_memory_conversations(conversation_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens INTEGER,                         -- Token count for monitoring
    sequence INTEGER NOT NULL               -- Message order in conversation
);

-- Entity Extraction (automatic)
CREATE TABLE IF NOT EXISTS working_memory_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL REFERENCES working_memory_conversations(conversation_id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,              -- file, commit, agent, feature, etc.
    entity_value TEXT NOT NULL,
    confidence REAL DEFAULT 1.0 CHECK(confidence BETWEEN 0.0 AND 1.0),
    first_mentioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mention_count INTEGER DEFAULT 1
);

-- Files Mentioned (for context)
CREATE TABLE IF NOT EXISTS working_memory_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL REFERENCES working_memory_conversations(conversation_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    action TEXT,                            -- created, modified, deleted, read
    mentioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Git Commits Linked to Conversations (NEW - requested feature)
CREATE TABLE IF NOT EXISTS working_memory_commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL REFERENCES working_memory_conversations(conversation_id) ON DELETE CASCADE,
    commit_hash TEXT NOT NULL,
    commit_message TEXT,
    commit_timestamp TIMESTAMP,
    files_changed INTEGER,
    lines_added INTEGER,
    lines_deleted INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_wm_conversations_created ON working_memory_conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wm_conversations_status ON working_memory_conversations(status);
CREATE INDEX IF NOT EXISTS idx_wm_messages_conversation ON working_memory_messages(conversation_id, sequence);
CREATE INDEX IF NOT EXISTS idx_wm_entities_conversation ON working_memory_entities(conversation_id);
CREATE INDEX IF NOT EXISTS idx_wm_entities_type ON working_memory_entities(entity_type, entity_value);
CREATE INDEX IF NOT EXISTS idx_wm_files_conversation ON working_memory_files(conversation_id);
CREATE INDEX IF NOT EXISTS idx_wm_commits_conversation ON working_memory_commits(conversation_id);
CREATE INDEX IF NOT EXISTS idx_wm_commits_hash ON working_memory_commits(commit_hash);

-- ============================================================================
-- TIER 2: KNOWLEDGE GRAPH (Long-Term Memory)
-- ============================================================================
-- Purpose: Consolidated patterns and learnings
-- Performance: <100ms pattern searches (FTS5)
-- Size: ~100-120KB
-- ============================================================================

-- Patterns Table (Full-Text Search)
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_patterns USING fts5(
    pattern_id UNINDEXED,                   -- UUID
    pattern_type,                           -- intent, workflow, file_relationship, etc.
    name,                                   -- Pattern name
    description,                            -- What this pattern represents
    content,                                -- Detailed pattern data (JSON)
    tokenize = 'porter'                     -- Stemming for better matching
);

-- Pattern Metadata (not searchable)
CREATE TABLE IF NOT EXISTS knowledge_pattern_metadata (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    name TEXT NOT NULL,
    confidence REAL DEFAULT 0.5 CHECK(confidence BETWEEN 0.0 AND 1.0),
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_conversation_ids TEXT            -- JSON array of originating conversations
);

-- File Relationships (co-modification tracking)
CREATE TABLE IF NOT EXISTS knowledge_file_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file1 TEXT NOT NULL,
    file2 TEXT NOT NULL,
    comod_count INTEGER DEFAULT 0,          -- How many times modified together
    confidence REAL DEFAULT 0.0 CHECK(confidence BETWEEN 0.0 AND 1.0),
    last_comod TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file1, file2)
);

-- Workflow Templates
CREATE TABLE IF NOT EXISTS knowledge_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    steps TEXT NOT NULL,                    -- JSON array of steps
    success_rate REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    avg_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Error Patterns (learn from mistakes)
CREATE TABLE IF NOT EXISTS knowledge_error_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    fix_description TEXT,
    fix_pattern TEXT,                       -- JSON of fix steps
    frequency INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0.5,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_type ON knowledge_pattern_metadata(pattern_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_confidence ON knowledge_pattern_metadata(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_used ON knowledge_pattern_metadata(last_used DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_file_rel_files ON knowledge_file_relationships(file1, file2);
CREATE INDEX IF NOT EXISTS idx_knowledge_workflows_success ON knowledge_workflows(success_rate DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_errors_type ON knowledge_error_patterns(error_type);

-- ============================================================================
-- TIER 3: CONTEXT INTELLIGENCE (Development Metrics)
-- ============================================================================
-- Purpose: Time-series project metrics for proactive insights
-- Performance: <10ms queries (indexed), <10sec collection
-- Size: ~40-50KB (historical data, pruned after 90 days)
-- ============================================================================

-- Git Activity Metrics (time-series)
CREATE TABLE IF NOT EXISTS context_git_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commits_30d INTEGER DEFAULT 0,
    commits_per_day REAL DEFAULT 0.0,
    contributors TEXT,                      -- JSON array
    lines_added INTEGER DEFAULT 0,
    lines_deleted INTEGER DEFAULT 0,
    net_growth INTEGER DEFAULT 0,
    velocity_trend TEXT CHECK(velocity_trend IN ('increasing', 'stable', 'decreasing')),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp)                       -- One entry per collection
);

-- File Hotspots (churn tracking)
CREATE TABLE IF NOT EXISTS context_file_hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commit_count INTEGER DEFAULT 0,
    churn_rate REAL DEFAULT 0.0,            -- Percentage of all commits
    stability TEXT CHECK(stability IN ('STABLE', 'MODERATE', 'UNSTABLE')),
    recommendation TEXT,                    -- Automated suggestion
    UNIQUE(file_path, timestamp)
);

-- Test Metrics (time-series)
CREATE TABLE IF NOT EXISTS context_test_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_tests INTEGER DEFAULT 0,
    pass_rate REAL DEFAULT 0.0,
    coverage_percent REAL DEFAULT 0.0,
    flaky_count INTEGER DEFAULT 0,
    avg_duration_ms REAL DEFAULT 0.0,
    test_types TEXT,                        -- JSON: {unit: 50, integration: 20, e2e: 10}
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp)
);

-- Build Metrics (time-series)
CREATE TABLE IF NOT EXISTS context_build_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    build_status TEXT CHECK(build_status IN ('passing', 'failing', 'unknown')),
    build_duration_sec REAL DEFAULT 0.0,
    warnings_count INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    deployment_status TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp)
);

-- Work Patterns (time-series)
CREATE TABLE IF NOT EXISTS context_work_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    productive_time TEXT,                   -- e.g., "10am-12pm"
    avg_session_minutes INTEGER DEFAULT 0,
    focus_duration_minutes INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    session_distribution TEXT,              -- JSON: {morning: 40%, afternoon: 35%, evening: 25%}
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp)
);

-- Correlations (discovered relationships)
CREATE TABLE IF NOT EXISTS context_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_type TEXT NOT NULL,         -- e.g., 'commit_size_vs_success'
    metric1 TEXT NOT NULL,
    metric2 TEXT NOT NULL,
    correlation_coefficient REAL,           -- -1.0 to 1.0
    sample_size INTEGER,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insight TEXT,                           -- Human-readable finding
    UNIQUE(correlation_type, metric1, metric2)
);

-- Proactive Insights (automated warnings/recommendations)
CREATE TABLE IF NOT EXISTS context_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL CHECK(insight_type IN ('warning', 'recommendation', 'info')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    metric_basis TEXT,                      -- Which metric triggered this
    confidence REAL DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP
);

-- Indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_context_git_time ON context_git_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_hotspots_file ON context_file_hotspots(file_path, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_hotspots_time ON context_file_hotspots(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_test_time ON context_test_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_build_time ON context_build_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_work_time ON context_work_patterns(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_context_correlations_type ON context_correlations(correlation_type);
CREATE INDEX IF NOT EXISTS idx_context_insights_type ON context_insights(insight_type, acknowledged);
CREATE INDEX IF NOT EXISTS idx_context_insights_created ON context_insights(created_at DESC);

-- ============================================================================
-- CONFIGURATION & METADATA
-- ============================================================================

-- System Configuration (loaded at startup)
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT CHECK(type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Database Metadata
CREATE TABLE IF NOT EXISTS system_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata
INSERT OR IGNORE INTO system_metadata (key, value) VALUES
    ('schema_version', '2.0'),
    ('created_at', datetime('now')),
    ('last_backup', NULL),
    ('total_size_kb', '0');

-- Insert default configuration
INSERT OR IGNORE INTO system_config (key, value, type, description) VALUES
    ('tier1_max_conversations', '50', 'integer', 'Maximum conversations in Tier 1 (FIFO)'),
    ('tier1_auto_extract', 'true', 'boolean', 'Auto-extract patterns before deletion'),
    ('tier2_confidence_threshold', '0.30', 'string', 'Minimum confidence to keep patterns'),
    ('tier2_consolidation_similarity', '0.75', 'string', 'Similarity threshold for merging patterns'),
    ('tier3_collection_interval_minutes', '60', 'integer', 'How often to collect metrics'),
    ('tier3_history_retention_days', '90', 'integer', 'How long to keep historical data');

-- ============================================================================
-- VIEWS (Convenience Queries)
-- ============================================================================

-- Active Conversations (not extracted yet)
CREATE VIEW IF NOT EXISTS view_active_conversations AS
SELECT 
    c.conversation_id,
    c.title,
    c.intent,
    c.created_at,
    c.message_count,
    COUNT(DISTINCT e.entity_value) as entity_count,
    COUNT(DISTINCT f.file_path) as file_count
FROM working_memory_conversations c
LEFT JOIN working_memory_entities e ON c.conversation_id = e.conversation_id
LEFT JOIN working_memory_files f ON c.conversation_id = f.conversation_id
WHERE c.status = 'active' AND c.pattern_extracted = FALSE
GROUP BY c.conversation_id;

-- Top Patterns by Confidence
CREATE VIEW IF NOT EXISTS view_top_patterns AS
SELECT 
    pattern_id,
    pattern_type,
    name,
    confidence,
    usage_count,
    success_count,
    ROUND(CAST(success_count AS REAL) / NULLIF(usage_count, 0) * 100, 1) as success_rate_pct,
    last_used
FROM knowledge_pattern_metadata
WHERE confidence >= 0.70
ORDER BY confidence DESC, usage_count DESC
LIMIT 50;

-- File Hotspots (Latest)
CREATE VIEW IF NOT EXISTS view_current_hotspots AS
SELECT 
    h.file_path,
    h.churn_rate,
    h.stability,
    h.recommendation,
    h.timestamp as last_measured
FROM context_file_hotspots h
INNER JOIN (
    SELECT file_path, MAX(timestamp) as max_time
    FROM context_file_hotspots
    GROUP BY file_path
) latest ON h.file_path = latest.file_path AND h.timestamp = latest.max_time
WHERE h.stability IN ('MODERATE', 'UNSTABLE')
ORDER BY h.churn_rate DESC;

-- Velocity Trend (Last 30 Days)
CREATE VIEW IF NOT EXISTS view_velocity_trend AS
SELECT 
    DATE(timestamp) as date,
    commits_per_day,
    velocity_trend,
    net_growth
FROM context_git_metrics
WHERE timestamp >= DATE('now', '-30 days')
ORDER BY timestamp DESC;

-- Unacknowledged Insights
CREATE VIEW IF NOT EXISTS view_pending_insights AS
SELECT 
    insight_type,
    title,
    description,
    metric_basis,
    confidence,
    created_at
FROM context_insights
WHERE acknowledged = FALSE
ORDER BY 
    CASE insight_type
        WHEN 'warning' THEN 1
        WHEN 'recommendation' THEN 2
        WHEN 'info' THEN 3
    END,
    created_at DESC;

-- ============================================================================
-- TRIGGERS (Automatic Maintenance)
-- ============================================================================

-- Update message count when new message added
CREATE TRIGGER IF NOT EXISTS trg_update_message_count
AFTER INSERT ON working_memory_messages
BEGIN
    UPDATE working_memory_conversations
    SET message_count = message_count + 1
    WHERE conversation_id = NEW.conversation_id;
END;

-- Update pattern metadata when used
CREATE TRIGGER IF NOT EXISTS trg_update_pattern_usage
AFTER UPDATE ON knowledge_pattern_metadata
WHEN NEW.usage_count > OLD.usage_count
BEGIN
    UPDATE knowledge_pattern_metadata
    SET 
        last_used = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE pattern_id = NEW.pattern_id;
END;

-- Auto-update updated_at timestamps
CREATE TRIGGER IF NOT EXISTS trg_governance_rules_updated
AFTER UPDATE ON governance_rules
BEGIN
    UPDATE governance_rules
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_pattern_metadata_updated
AFTER UPDATE ON knowledge_pattern_metadata
BEGIN
    UPDATE knowledge_pattern_metadata
    SET updated_at = CURRENT_TIMESTAMP
    WHERE pattern_id = NEW.pattern_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_config_updated
AFTER UPDATE ON system_config
BEGIN
    UPDATE system_config
    SET updated_at = CURRENT_TIMESTAMP
    WHERE key = NEW.key;
END;

-- ============================================================================
-- PERFORMANCE OPTIMIZATIONS
-- ============================================================================

-- Enable Write-Ahead Logging for better concurrency
PRAGMA journal_mode = WAL;

-- Increase cache size for better read performance
PRAGMA cache_size = -8000;  -- 8MB cache

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Auto-vacuum to keep database compact
PRAGMA auto_vacuum = INCREMENTAL;

-- Analyze tables for query optimization
ANALYZE;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
