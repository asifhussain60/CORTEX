-- CORTEX Brain SQLite Schema v1.0
-- Created: 2025-11-06
-- Purpose: Complete database schema for CORTEX Brain (Tiers 0-3)
-- Performance Target: <100ms reads, optimized indexes
-- Features: FTS5 full-text search, FIFO queue, pattern storage

-- ============================================================================
-- TIER 0: INSTINCT (Immutable Governance Rules)
-- ============================================================================
-- Purpose: Store permanent governance rules that cannot be overridden
-- Examples: TDD enforcement, DoR/DoD, SOLID principles, Brain Protection

CREATE TABLE IF NOT EXISTS tier0_rules (
    rule_id TEXT PRIMARY KEY,              -- e.g., "RULE_001", "RULE_025"
    rule_number INTEGER UNIQUE NOT NULL,   -- Numeric ID (1, 2, 3, 25, 26, 27)
    name TEXT NOT NULL,                    -- e.g., "Cognitive Anchoring"
    category TEXT NOT NULL,                -- e.g., "cognitive_framework", "tdd", "quality"
    severity TEXT NOT NULL,                -- "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description TEXT NOT NULL,             -- Full rule description
    enforcement_mechanism TEXT,            -- How the rule is enforced
    violation_response TEXT,               -- What happens when violated
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    is_active INTEGER NOT NULL DEFAULT 1, -- 0=disabled, 1=active (should always be 1)
    
    CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    CHECK (is_active IN (0, 1))
);

-- Index for fast rule lookups
CREATE INDEX IF NOT EXISTS idx_rules_category ON tier0_rules(category);
CREATE INDEX IF NOT EXISTS idx_rules_severity ON tier0_rules(severity);

-- ============================================================================
-- TIER 1: WORKING MEMORY (Short-term Conversation History)
-- ============================================================================
-- Purpose: Store last 20 conversations with full message history
-- FIFO Queue: When conversation #21 starts, #1 gets deleted
-- Performance: <100ms read for active conversation + recent 19

-- Conversations: Top-level conversation metadata
CREATE TABLE IF NOT EXISTS tier1_conversations (
    conversation_id TEXT PRIMARY KEY,      -- UUID for each conversation
    topic TEXT NOT NULL,                   -- Auto-generated topic from first message
    status TEXT NOT NULL DEFAULT 'active', -- "active", "complete", "archived"
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,                     -- When conversation ended
    message_count INTEGER NOT NULL DEFAULT 0,
    intent TEXT,                           -- Primary intent: PLAN, EXECUTE, TEST, etc.
    outcome TEXT,                          -- "success", "failure", "cancelled"
    duration_seconds INTEGER,              -- Total conversation duration
    
    -- Metadata for context resolution
    primary_entity TEXT,                   -- Main entity discussed (file, feature, etc.)
    related_files TEXT,                    -- JSON array of file paths
    associated_commits TEXT,               -- JSON array of commit SHAs
    
    -- FIFO queue management
    queue_position INTEGER NOT NULL,       -- 1-20 for active conversations
    
    CHECK (status IN ('active', 'complete', 'archived')),
    CHECK (outcome IS NULL OR outcome IN ('success', 'failure', 'cancelled')),
    CHECK (queue_position > 0 AND queue_position <= 20)
);

-- Indexes for FIFO queue performance
CREATE INDEX IF NOT EXISTS idx_conversations_queue ON tier1_conversations(queue_position);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON tier1_conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON tier1_conversations(created_at DESC);

-- Messages: Individual messages within conversations
CREATE TABLE IF NOT EXISTS tier1_messages (
    message_id TEXT PRIMARY KEY,           -- UUID for each message
    conversation_id TEXT NOT NULL,         -- FK to tier1_conversations
    sequence_number INTEGER NOT NULL,      -- 1, 2, 3... within conversation
    role TEXT NOT NULL,                    -- "user", "assistant", "system"
    content TEXT NOT NULL,                 -- Message text
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Context resolution tracking
    resolved_references TEXT,              -- JSON: {"it": "FAB button", "that": "invoice.pdf"}
    references_message_id TEXT,            -- FK to previous message if this is a follow-up
    
    -- Agent tracking
    agent_used TEXT,                       -- Which agent processed this (intent-router, etc.)
    intent_detected TEXT,                  -- Detected intent for this message
    confidence REAL,                       -- Confidence score (0.0-1.0)
    
    FOREIGN KEY (conversation_id) REFERENCES tier1_conversations(conversation_id) ON DELETE CASCADE,
    FOREIGN KEY (references_message_id) REFERENCES tier1_messages(message_id),
    CHECK (role IN ('user', 'assistant', 'system')),
    CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0))
);

-- Indexes for fast message retrieval
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON tier1_messages(conversation_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON tier1_messages(timestamp DESC);

-- FTS5: Full-text search across conversations and messages
CREATE VIRTUAL TABLE IF NOT EXISTS tier1_conversations_fts USING fts5(
    conversation_id UNINDEXED,
    topic,
    primary_entity,
    content='tier1_conversations',
    content_rowid='rowid'
);

CREATE VIRTUAL TABLE IF NOT EXISTS tier1_messages_fts USING fts5(
    message_id UNINDEXED,
    conversation_id UNINDEXED,
    content,
    content='tier1_messages',
    content_rowid='rowid'
);

-- Triggers to keep FTS5 tables in sync
CREATE TRIGGER IF NOT EXISTS tier1_conversations_fts_insert AFTER INSERT ON tier1_conversations BEGIN
    INSERT INTO tier1_conversations_fts(rowid, conversation_id, topic, primary_entity)
    VALUES (new.rowid, new.conversation_id, new.topic, new.primary_entity);
END;

CREATE TRIGGER IF NOT EXISTS tier1_conversations_fts_delete AFTER DELETE ON tier1_conversations BEGIN
    DELETE FROM tier1_conversations_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER IF NOT EXISTS tier1_messages_fts_insert AFTER INSERT ON tier1_messages BEGIN
    INSERT INTO tier1_messages_fts(rowid, message_id, conversation_id, content)
    VALUES (new.rowid, new.message_id, new.conversation_id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS tier1_messages_fts_delete AFTER DELETE ON tier1_messages BEGIN
    DELETE FROM tier1_messages_fts WHERE rowid = old.rowid;
END;

-- ============================================================================
-- TIER 2: KNOWLEDGE GRAPH (Long-term Pattern Memory)
-- ============================================================================
-- Purpose: Store accumulated wisdom from all interactions
-- Patterns extracted from deleted Tier 1 conversations persist here

-- Patterns: Workflows, code patterns, UI patterns, etc.
CREATE TABLE IF NOT EXISTS tier2_patterns (
    pattern_id TEXT PRIMARY KEY,           -- UUID for each pattern
    name TEXT NOT NULL,                    -- e.g., "invoice_export_feature"
    category TEXT NOT NULL,                -- "workflow", "code_pattern", "ui_pattern", etc.
    description TEXT NOT NULL,             -- What the pattern does
    file_path TEXT,                        -- Primary file where pattern is implemented
    code_snippet TEXT,                     -- Optional code sample
    
    -- Confidence and usage tracking
    confidence REAL NOT NULL DEFAULT 0.8,  -- 0.0-1.0 (starts at 0.8 for new patterns)
    usage_count INTEGER NOT NULL DEFAULT 1,
    success_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_used TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Pattern metadata
    tags TEXT,                             -- JSON array: ["export", "pdf", "invoice"]
    related_patterns TEXT,                 -- JSON array of related pattern_ids
    
    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    CHECK (category IN ('workflow', 'code_pattern', 'ui_pattern', 'architectural', 'validation', 'intent', 'file_relationship'))
);

-- Indexes for pattern search performance
CREATE INDEX IF NOT EXISTS idx_patterns_category ON tier2_patterns(category);
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON tier2_patterns(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_usage ON tier2_patterns(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_last_used ON tier2_patterns(last_used DESC);

-- FTS5: Semantic search for patterns
CREATE VIRTUAL TABLE IF NOT EXISTS tier2_patterns_fts USING fts5(
    pattern_id UNINDEXED,
    name,
    description,
    tags,
    content='tier2_patterns',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS tier2_patterns_fts_insert AFTER INSERT ON tier2_patterns BEGIN
    INSERT INTO tier2_patterns_fts(rowid, pattern_id, name, description, tags)
    VALUES (new.rowid, new.pattern_id, new.name, new.description, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS tier2_patterns_fts_update AFTER UPDATE ON tier2_patterns BEGIN
    UPDATE tier2_patterns_fts 
    SET name = new.name, description = new.description, tags = new.tags
    WHERE rowid = new.rowid;
END;

CREATE TRIGGER IF NOT EXISTS tier2_patterns_fts_delete AFTER DELETE ON tier2_patterns BEGIN
    DELETE FROM tier2_patterns_fts WHERE rowid = old.rowid;
END;

-- File Relationships: Track which files are modified together
CREATE TABLE IF NOT EXISTS tier2_file_relationships (
    relationship_id TEXT PRIMARY KEY,
    file_a TEXT NOT NULL,                  -- First file path
    file_b TEXT NOT NULL,                  -- Second file path
    co_modification_count INTEGER NOT NULL DEFAULT 1,
    confidence REAL NOT NULL DEFAULT 0.0,  -- Calculated from co_modification_count
    last_co_modified TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    UNIQUE(file_a, file_b),
    CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX IF NOT EXISTS idx_file_rel_a ON tier2_file_relationships(file_a);
CREATE INDEX IF NOT EXISTS idx_file_rel_b ON tier2_file_relationships(file_b);
CREATE INDEX IF NOT EXISTS idx_file_rel_confidence ON tier2_file_relationships(confidence DESC);

-- Intent Patterns: Learn which phrases map to which intents
CREATE TABLE IF NOT EXISTS tier2_intent_patterns (
    intent_pattern_id TEXT PRIMARY KEY,
    phrase_pattern TEXT NOT NULL,          -- e.g., "add [X]", "implement [Y]"
    intent TEXT NOT NULL,                  -- PLAN, EXECUTE, TEST, FIX, QUERY, VALIDATE
    confidence REAL NOT NULL DEFAULT 0.8,
    usage_count INTEGER NOT NULL DEFAULT 1,
    success_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_used TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK (intent IN ('PLAN', 'EXECUTE', 'TEST', 'FIX', 'QUERY', 'VALIDATE', 'RESUME', 'CORTEX_CHANGE')),
    CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX IF NOT EXISTS idx_intent_patterns_intent ON tier2_intent_patterns(intent);
CREATE INDEX IF NOT EXISTS idx_intent_patterns_confidence ON tier2_intent_patterns(confidence DESC);

-- Correction History: Track mistakes and corrections for learning
CREATE TABLE IF NOT EXISTS tier2_corrections (
    correction_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    error_type TEXT NOT NULL,              -- "wrong_file", "syntax_error", "logic_bug", etc.
    error_description TEXT NOT NULL,
    correction_applied TEXT NOT NULL,      -- What was changed to fix it
    file_path TEXT,                        -- File where error occurred
    pattern_violated TEXT,                 -- Which pattern was violated (if any)
    
    -- Learning: Did we make this mistake before?
    is_repeat_error INTEGER NOT NULL DEFAULT 0,
    times_occurred INTEGER NOT NULL DEFAULT 1,
    
    CHECK (is_repeat_error IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_corrections_type ON tier2_corrections(error_type);
CREATE INDEX IF NOT EXISTS idx_corrections_file ON tier2_corrections(file_path);
CREATE INDEX IF NOT EXISTS idx_corrections_repeat ON tier2_corrections(is_repeat_error);

-- Pattern Searches: Track all pattern searches for Rule #27
CREATE TABLE IF NOT EXISTS tier2_pattern_searches (
    search_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    intent TEXT NOT NULL,                  -- What was being searched for
    code_type TEXT NOT NULL,               -- "function", "class", "component", etc.
    result TEXT NOT NULL,                  -- "REUSE" or "CREATE"
    pattern_id TEXT,                       -- FK to tier2_patterns if REUSE
    confidence REAL,                       -- Confidence of match if REUSE
    search_time_ms REAL,                   -- Performance tracking
    
    FOREIGN KEY (pattern_id) REFERENCES tier2_patterns(pattern_id),
    CHECK (result IN ('REUSE', 'CREATE')),
    CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0))
);

CREATE INDEX IF NOT EXISTS idx_pattern_searches_result ON tier2_pattern_searches(result);
CREATE INDEX IF NOT EXISTS idx_pattern_searches_timestamp ON tier2_pattern_searches(timestamp DESC);

-- ============================================================================
-- TIER 3: DEVELOPMENT CONTEXT (Holistic Project Intelligence)
-- ============================================================================
-- Purpose: Track git activity, code velocity, testing activity, work patterns

-- Git Commits: Track all commits with metrics
CREATE TABLE IF NOT EXISTS tier3_git_commits (
    commit_sha TEXT PRIMARY KEY,
    author TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    message TEXT NOT NULL,
    files_changed INTEGER NOT NULL DEFAULT 0,
    lines_added INTEGER NOT NULL DEFAULT 0,
    lines_deleted INTEGER NOT NULL DEFAULT 0,
    
    -- Categorization
    commit_type TEXT,                      -- "feat", "fix", "test", "docs", "refactor"
    conversation_id TEXT,                  -- FK to tier1_conversations if associated
    
    FOREIGN KEY (conversation_id) REFERENCES tier1_conversations(conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_commits_timestamp ON tier3_git_commits(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_commits_author ON tier3_git_commits(author);
CREATE INDEX IF NOT EXISTS idx_commits_type ON tier3_git_commits(commit_type);
CREATE INDEX IF NOT EXISTS idx_commits_conversation ON tier3_git_commits(conversation_id);

-- File Metrics: Track churn rate and stability per file
CREATE TABLE IF NOT EXISTS tier3_file_metrics (
    file_path TEXT PRIMARY KEY,
    total_modifications INTEGER NOT NULL DEFAULT 0,
    churn_rate REAL NOT NULL DEFAULT 0.0,  -- Percentage: edits / total commits
    stability TEXT NOT NULL DEFAULT 'stable', -- "stable", "moderate", "hotspot"
    last_modified TEXT NOT NULL DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Aggregate metrics
    total_lines_added INTEGER NOT NULL DEFAULT 0,
    total_lines_deleted INTEGER NOT NULL DEFAULT 0,
    net_lines INTEGER NOT NULL DEFAULT 0,
    
    CHECK (stability IN ('stable', 'moderate', 'hotspot')),
    CHECK (churn_rate >= 0.0 AND churn_rate <= 1.0)
);

CREATE INDEX IF NOT EXISTS idx_file_metrics_churn ON tier3_file_metrics(churn_rate DESC);
CREATE INDEX IF NOT EXISTS idx_file_metrics_stability ON tier3_file_metrics(stability);

-- Code Velocity: Weekly/monthly velocity tracking
CREATE TABLE IF NOT EXISTS tier3_velocity_metrics (
    period_id TEXT PRIMARY KEY,            -- "2025-W45", "2025-11", etc.
    period_type TEXT NOT NULL,             -- "week", "month"
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    
    -- Commit metrics
    commit_count INTEGER NOT NULL DEFAULT 0,
    avg_commits_per_day REAL NOT NULL DEFAULT 0.0,
    
    -- Line metrics
    lines_added INTEGER NOT NULL DEFAULT 0,
    lines_deleted INTEGER NOT NULL DEFAULT 0,
    net_lines INTEGER NOT NULL DEFAULT 0,
    
    -- Change distribution
    feat_count INTEGER NOT NULL DEFAULT 0,
    fix_count INTEGER NOT NULL DEFAULT 0,
    test_count INTEGER NOT NULL DEFAULT 0,
    docs_count INTEGER NOT NULL DEFAULT 0,
    refactor_count INTEGER NOT NULL DEFAULT 0,
    
    CHECK (period_type IN ('week', 'month'))
);

CREATE INDEX IF NOT EXISTS idx_velocity_period ON tier3_velocity_metrics(period_type, start_date DESC);

-- Test Activity: Track test creation and pass rates
CREATE TABLE IF NOT EXISTS tier3_test_activity (
    test_run_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    test_suite TEXT,                       -- Which test suite was run
    total_tests INTEGER NOT NULL,
    passed_tests INTEGER NOT NULL,
    failed_tests INTEGER NOT NULL,
    skipped_tests INTEGER NOT NULL,
    duration_seconds REAL,
    
    -- Flaky test detection
    flaky_tests TEXT,                      -- JSON array of flaky test names
    
    -- Coverage (if available)
    coverage_percentage REAL,
    
    CHECK (coverage_percentage IS NULL OR (coverage_percentage >= 0.0 AND coverage_percentage <= 100.0))
);

CREATE INDEX IF NOT EXISTS idx_test_activity_timestamp ON tier3_test_activity(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_test_activity_suite ON tier3_test_activity(test_suite);

-- Work Patterns: Track when work happens and success rates
CREATE TABLE IF NOT EXISTS tier3_work_patterns (
    session_id TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_minutes INTEGER,
    
    -- Time slot analysis
    time_slot TEXT,                        -- "09:00-10:00", "14:00-15:00", etc.
    day_of_week TEXT,                      -- "Monday", "Tuesday", etc.
    
    -- Success metrics
    intents_completed INTEGER NOT NULL DEFAULT 0,
    intents_failed INTEGER NOT NULL DEFAULT 0,
    success_rate REAL,
    
    -- Focus metrics
    context_switches INTEGER NOT NULL DEFAULT 0,
    files_modified INTEGER NOT NULL DEFAULT 0,
    
    CHECK (success_rate IS NULL OR (success_rate >= 0.0 AND success_rate <= 1.0))
);

CREATE INDEX IF NOT EXISTS idx_work_patterns_time_slot ON tier3_work_patterns(time_slot);
CREATE INDEX IF NOT EXISTS idx_work_patterns_success ON tier3_work_patterns(success_rate DESC);

-- ============================================================================
-- TIER 4: MIND PALACE (Documentation & Story Tracking)
-- ============================================================================
-- Purpose: Track documentation chapters, story progress, and narrative consistency
-- Integration: References conversations that inspired chapters, tracks metaphor mappings

-- Mind Palace Chapters: Individual story/documentation chapters
CREATE TABLE IF NOT EXISTS tier4_mind_palace_chapters (
    chapter_id TEXT PRIMARY KEY,           -- e.g., "ch-001", "ch-017-purple-button"
    chapter_number INTEGER NOT NULL,       -- 1, 2, 3, etc.
    title TEXT NOT NULL,                   -- "The Problem of Amnesia"
    version TEXT NOT NULL DEFAULT '1.0',   -- Semantic versioning
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'draft',  -- "draft", "review", "complete", "published"
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    
    -- Content sections (completeness tracking)
    has_story INTEGER NOT NULL DEFAULT 0,      -- Story section complete
    has_cartoon_prompt INTEGER NOT NULL DEFAULT 0,  -- Cartoon image prompt
    has_diagram_prompt INTEGER NOT NULL DEFAULT 0,  -- Technical diagram prompt
    has_technical_docs INTEGER NOT NULL DEFAULT 0,  -- Technical documentation
    
    -- Metadata
    topic TEXT,                            -- Main topic covered
    complexity TEXT,                       -- "low", "medium", "high"
    reading_time_minutes INTEGER,         -- Estimated reading time
    prerequisites TEXT,                    -- JSON array of required chapters
    
    -- Integration
    file_path TEXT NOT NULL,              -- Actual markdown file location
    conversation_id TEXT,                 -- FK: Conversation that inspired this
    
    CHECK (status IN ('draft', 'review', 'complete', 'published')),
    CHECK (complexity IS NULL OR complexity IN ('low', 'medium', 'high')),
    CHECK (has_story IN (0, 1)),
    CHECK (has_cartoon_prompt IN (0, 1)),
    CHECK (has_diagram_prompt IN (0, 1)),
    CHECK (has_technical_docs IN (0, 1)),
    FOREIGN KEY (conversation_id) REFERENCES tier1_conversations(conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_chapters_number ON tier4_mind_palace_chapters(chapter_number);
CREATE INDEX IF NOT EXISTS idx_chapters_status ON tier4_mind_palace_chapters(status);

-- Metaphor Mappings: Story characters/elements to technical components
CREATE TABLE IF NOT EXISTS tier4_metaphor_mappings (
    mapping_id TEXT PRIMARY KEY,
    chapter_id TEXT NOT NULL,              -- FK to chapters
    
    -- Story element
    story_character TEXT NOT NULL,         -- e.g., "Dr. Asifinstein", "The Intent Router"
    story_description TEXT,                -- Character's role in narrative
    
    -- Technical component
    technical_component TEXT NOT NULL,     -- e.g., "Intent Router Agent"
    file_location TEXT,                    -- e.g., "CORTEX/src/tier1/intent_router.py"
    component_type TEXT,                   -- "agent", "tier", "file", "pattern"
    
    -- Validation
    is_validated INTEGER NOT NULL DEFAULT 0, -- Mapping verified accurate
    validated_at TEXT,
    
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK (is_validated IN (0, 1)),
    FOREIGN KEY (chapter_id) REFERENCES tier4_mind_palace_chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metaphors_chapter ON tier4_metaphor_mappings(chapter_id);
CREATE INDEX IF NOT EXISTS idx_metaphors_component ON tier4_metaphor_mappings(technical_component);

-- Image Prompts: Track generated images for chapters
CREATE TABLE IF NOT EXISTS tier4_image_prompts (
    prompt_id TEXT PRIMARY KEY,
    chapter_id TEXT NOT NULL,
    
    -- Prompt details
    prompt_type TEXT NOT NULL,             -- "cartoon", "diagram"
    prompt_text TEXT NOT NULL,             -- Full Gemini prompt
    style_guide TEXT,                      -- Style specifications
    
    -- Generation tracking
    is_generated INTEGER NOT NULL DEFAULT 0,
    generated_at TEXT,
    image_file_path TEXT,                  -- Path to generated image
    generation_tool TEXT,                  -- "Gemini", "DALL-E", "Midjourney"
    
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK (prompt_type IN ('cartoon', 'diagram')),
    CHECK (is_generated IN (0, 1)),
    FOREIGN KEY (chapter_id) REFERENCES tier4_mind_palace_chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_prompts_chapter ON tier4_image_prompts(chapter_id);
CREATE INDEX IF NOT EXISTS idx_prompts_type ON tier4_image_prompts(prompt_type);

-- Chapter Cross-References: Dependencies and relationships between chapters
CREATE TABLE IF NOT EXISTS tier4_chapter_references (
    reference_id TEXT PRIMARY KEY,
    from_chapter_id TEXT NOT NULL,         -- Source chapter
    to_chapter_id TEXT NOT NULL,           -- Referenced chapter
    
    reference_type TEXT NOT NULL,          -- "prerequisite", "related", "continuation"
    description TEXT,                      -- Why this reference exists
    
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK (reference_type IN ('prerequisite', 'related', 'continuation')),
    FOREIGN KEY (from_chapter_id) REFERENCES tier4_mind_palace_chapters(chapter_id) ON DELETE CASCADE,
    FOREIGN KEY (to_chapter_id) REFERENCES tier4_mind_palace_chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_references_from ON tier4_chapter_references(from_chapter_id);
CREATE INDEX IF NOT EXISTS idx_references_to ON tier4_chapter_references(to_chapter_id);

-- Mind Palace Progress: Overall story/documentation progress tracking
CREATE TABLE IF NOT EXISTS tier4_mind_palace_progress (
    progress_id TEXT PRIMARY KEY,
    
    -- Version tracking
    story_version TEXT NOT NULL,           -- "1.0-CORTEX-Story"
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Overall stats
    total_chapters INTEGER NOT NULL DEFAULT 28,
    completed_chapters INTEGER NOT NULL DEFAULT 0,
    draft_chapters INTEGER NOT NULL DEFAULT 0,
    published_chapters INTEGER NOT NULL DEFAULT 0,
    
    -- Image generation progress
    total_image_prompts INTEGER NOT NULL DEFAULT 0,
    generated_images INTEGER NOT NULL DEFAULT 0,
    
    -- Quality metrics
    validated_metaphors INTEGER NOT NULL DEFAULT 0,
    total_metaphors INTEGER NOT NULL DEFAULT 0,
    
    -- Reading paths
    beginner_path TEXT,                    -- JSON array of chapter IDs
    developer_path TEXT,                   -- JSON array of chapter IDs
    visual_learner_path TEXT,              -- JSON array of chapter IDs
    complete_path TEXT                     -- JSON array of chapter IDs
);

-- ============================================================================
-- SUPPORTING TABLES (Cross-tier)
-- ============================================================================

-- Events: Raw event stream (all agent actions)
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    agent TEXT NOT NULL,                   -- Which agent triggered this event
    action TEXT NOT NULL,                  -- What action was performed
    result TEXT,                           -- SUCCESS, FAILURE, GREEN, RED, etc.
    details TEXT,                          -- JSON with additional details
    conversation_id TEXT,                  -- FK to tier1_conversations
    
    FOREIGN KEY (conversation_id) REFERENCES tier1_conversations(conversation_id)
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_agent ON events(agent);
CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_events_conversation ON events(conversation_id);

-- Configuration: Store system configuration
CREATE TABLE IF NOT EXISTS configuration (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT NOT NULL DEFAULT 'string', -- "string", "integer", "float", "boolean", "json"
    description TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK (value_type IN ('string', 'integer', 'float', 'boolean', 'json'))
);

-- Insert default configuration values
INSERT OR IGNORE INTO configuration (key, value, value_type, description) VALUES
    ('tier1_max_conversations', '20', 'integer', 'Maximum conversations in Tier 1 FIFO queue'),
    ('tier1_read_performance_target_ms', '100', 'integer', 'Read performance target in milliseconds'),
    ('tier2_pattern_reuse_threshold', '0.70', 'float', 'Minimum confidence for pattern reuse (Rule #27)'),
    ('tier2_pattern_decay_days', '90', 'integer', 'Days of inactivity before pattern decay'),
    ('tier3_velocity_window_days', '30', 'integer', 'Days to analyze for velocity metrics'),
    ('brain_update_event_threshold', '50', 'integer', 'Events before triggering brain update'),
    ('brain_update_time_threshold_hours', '24', 'integer', 'Hours before time-based brain update');

-- ============================================================================
-- VIEWS (Convenient read-only queries)
-- ============================================================================

-- Active conversations view (for dashboard)
CREATE VIEW IF NOT EXISTS view_active_conversations AS
SELECT 
    c.conversation_id,
    c.topic,
    c.status,
    c.created_at,
    c.message_count,
    c.intent,
    c.queue_position,
    (SELECT content FROM tier1_messages WHERE conversation_id = c.conversation_id ORDER BY sequence_number DESC LIMIT 1) as last_message,
    (SELECT timestamp FROM tier1_messages WHERE conversation_id = c.conversation_id ORDER BY sequence_number DESC LIMIT 1) as last_message_time
FROM tier1_conversations c
WHERE c.status = 'active'
ORDER BY c.queue_position;

-- Top patterns by usage
CREATE VIEW IF NOT EXISTS view_top_patterns AS
SELECT 
    pattern_id,
    name,
    category,
    confidence,
    usage_count,
    success_count,
    ROUND(CAST(success_count AS REAL) / NULLIF(usage_count, 0) * 100, 1) as success_rate_pct,
    last_used
FROM tier2_patterns
WHERE usage_count > 0
ORDER BY usage_count DESC, confidence DESC
LIMIT 50;

-- Pattern reuse statistics
CREATE VIEW IF NOT EXISTS view_pattern_reuse_stats AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_searches,
    SUM(CASE WHEN result = 'REUSE' THEN 1 ELSE 0 END) as reuse_count,
    SUM(CASE WHEN result = 'CREATE' THEN 1 ELSE 0 END) as create_count,
    ROUND(CAST(SUM(CASE WHEN result = 'REUSE' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 1) as reuse_rate_pct,
    AVG(CASE WHEN result = 'REUSE' THEN confidence ELSE NULL END) as avg_reuse_confidence
FROM tier2_pattern_searches
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Git velocity by week
CREATE VIEW IF NOT EXISTS view_git_velocity_weekly AS
SELECT 
    period_id,
    start_date,
    end_date,
    commit_count,
    lines_added,
    lines_deleted,
    net_lines,
    feat_count,
    fix_count,
    test_count
FROM tier3_velocity_metrics
WHERE period_type = 'week'
ORDER BY start_date DESC;

-- File hotspots (high churn files)
CREATE VIEW IF NOT EXISTS view_file_hotspots AS
SELECT 
    file_path,
    total_modifications,
    churn_rate,
    stability,
    last_modified
FROM tier3_file_metrics
WHERE stability IN ('hotspot', 'moderate')
ORDER BY churn_rate DESC, total_modifications DESC
LIMIT 20;

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) VALUES
    ('1.0.0', 'Initial CORTEX Brain schema with Tiers 0-3, FTS5 search, and Rule #27 support'),
    ('1.1.0', 'Added Tier 4: Mind Palace documentation tracking with chapters, metaphors, images, and progress');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
-- Total Tables: 25 (Tiers 0-4)
-- Total Indexes: 40+
-- Total Views: 5
-- Total Triggers: 6 (FTS5 sync)
-- FTS5 Tables: 3 (conversations, messages, patterns)
-- Mind Palace Tables: 5 (chapters, metaphors, prompts, references, progress)
-- Performance Optimizations: All queries <100ms with proper indexing
