# CORTEX Storage Schema

**Version:** 1.0  
**Date:** 2025-11-06  
**Status:** 🏗️ DESIGN SPECIFICATION  
**Purpose:** Unified SQLite schema reference for all tiers

---

## 🎯 Overview

**Database:** `cortex-brain.db` (single SQLite file)  
**Total Tables:** 22 (Tier 0: 3, Tier 1: 4, Tier 2: 8, Tier 3: 11)  
**Target Size:** <11 MB (Tier 0: <50 KB, Tier 1: <100 KB, Tier 2: <10 MB, Tier 3: <50 KB)  
**Performance:** <10ms (fast), <50ms (medium), <100ms (complex)

**Why Single Database?**
- ✅ **Atomic transactions** across tiers
- ✅ **Foreign key integrity** (conversations → patterns → insights)
- ✅ **Simpler backup** (one file to save)
- ✅ **Easier migration** (one schema version)
- ✅ **Better performance** (no cross-database joins)

---

## 📊 Complete Schema

### Tier 0: Governance (3 tables)

#### Table: `governance_rules`

```sql
CREATE TABLE governance_rules (
    id INTEGER PRIMARY KEY,                 -- Rule number (1-22)
    title TEXT NOT NULL UNIQUE,             -- Rule title
    category TEXT NOT NULL CHECK(category IN (
        'DEVELOPMENT',                      -- TDD, code quality, testing
        'ARCHITECTURE',                     -- Design, patterns, SOLID
        'BRAIN',                            -- Memory, learning, protection
        'PROCESS',                          -- Workflows, git, automation
        'QUALITY'                           -- DoR, DoD, validation
    )),
    description TEXT NOT NULL,              -- Full rule text
    rationale TEXT NOT NULL,                -- Why this rule exists
    tier TEXT NOT NULL CHECK(tier IN ('0', '1', '2', '3', 'ALL')),
    applies_to TEXT,                        -- JSON array of agent names
    enforcement TEXT NOT NULL CHECK(enforcement IN ('REQUIRED', 'RECOMMENDED', 'OPTIONAL')),
    violation_severity TEXT NOT NULL CHECK(violation_severity IN ('CRITICAL', 'ERROR', 'WARNING', 'INFO')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    examples TEXT,                          -- JSON array of examples
    metadata TEXT                           -- JSON for extensibility
);

-- Indexes
CREATE INDEX idx_rules_category ON governance_rules(category);
CREATE INDEX idx_rules_tier ON governance_rules(tier);
CREATE INDEX idx_rules_enforcement ON governance_rules(enforcement);

-- Seed data: 22 core rules
INSERT INTO governance_rules (id, title, category, description, rationale, tier, applies_to, enforcement, violation_severity) VALUES
(5, 'Test-Driven Development', 'DEVELOPMENT', 'RED → GREEN → REFACTOR', 'Reduces bugs by 68%', 'ALL', '["test-generator", "code-executor"]', 'REQUIRED', 'CRITICAL'),
(8, 'Definition of READY', 'QUALITY', 'Requirements clear before work', 'Prevents rework', 'ALL', '["work-planner", "readiness-validator"]', 'REQUIRED', 'ERROR'),
(15, 'Definition of DONE', 'QUALITY', 'Zero errors, zero warnings', 'Ensures quality', 'ALL', '["health-validator"]', 'REQUIRED', 'CRITICAL'),
(22, 'Brain Protection System', 'BRAIN', 'Challenge risky changes', 'Protects BRAIN integrity', '0', '["brain-protector"]', 'REQUIRED', 'CRITICAL');
-- ... (18 more rules)
```

#### Table: `governance_rule_examples`

```sql
CREATE TABLE governance_rule_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,               -- Foreign key to governance_rules
    example_type TEXT NOT NULL CHECK(example_type IN ('GOOD', 'BAD', 'SCENARIO')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    code_snippet TEXT,                      -- Optional code example
    FOREIGN KEY (rule_id) REFERENCES governance_rules(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_examples_rule ON governance_rule_examples(rule_id);
CREATE INDEX idx_examples_type ON governance_rule_examples(example_type);
```

#### Table: `governance_rule_violations`

```sql
CREATE TABLE governance_rule_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,               -- Foreign key to governance_rules
    violation_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent TEXT NOT NULL,                    -- Which agent violated
    context TEXT NOT NULL,                  -- What was being done
    severity TEXT NOT NULL,                 -- Copied from rule
    auto_corrected BOOLEAN NOT NULL DEFAULT 0,
    correction_action TEXT,                 -- What was done to fix
    metadata TEXT,                          -- JSON for details
    FOREIGN KEY (rule_id) REFERENCES governance_rules(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_violations_rule ON governance_rule_violations(rule_id);
CREATE INDEX idx_violations_timestamp ON governance_rule_violations(violation_timestamp DESC);
CREATE INDEX idx_violations_agent ON governance_rule_violations(agent);
CREATE INDEX idx_violations_severity ON governance_rule_violations(severity);
```

---

### Tier 1: Short-Term Memory (4 tables)

#### Table: `conversations`

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,                    -- UUID (e.g., "conv_2025-11-06_1430_abc123")
    topic TEXT NOT NULL,                    -- Extracted from first message
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,                 -- NULL if active
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'completed', 'deleted')),
    message_count INTEGER NOT NULL DEFAULT 0,
    outcome TEXT CHECK(outcome IN ('success', 'abandoned', 'error', NULL)),
    duration_seconds INTEGER,               -- Calculated when completed
    tags TEXT,                              -- JSON array
    metadata TEXT                           -- JSON object
);

-- Indexes
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_outcome ON conversations(outcome);

-- FIFO enforcement trigger
CREATE TRIGGER enforce_fifo_limit
AFTER INSERT ON conversations
WHEN (SELECT COUNT(*) FROM conversations WHERE status != 'deleted') > 20
BEGIN
    UPDATE conversations 
    SET status = 'deleted'
    WHERE id = (
        SELECT id FROM conversations 
        WHERE status = 'completed' 
        ORDER BY created_at ASC 
        LIMIT 1
    );
END;
```

#### Table: `messages`

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,              -- Message order
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent TEXT,                             -- Agent that generated (if assistant)
    tool_calls TEXT,                        -- JSON array
    metadata TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    UNIQUE(conversation_id, sequence)
);

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_role ON messages(role);
```

#### Table: `conversation_entities`

```sql
CREATE TABLE conversation_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('file', 'intent', 'agent', 'component', 'test', 'error')),
    entity_value TEXT NOT NULL,
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    first_mention_message_id INTEGER,       -- Message where first appeared
    mention_count INTEGER NOT NULL DEFAULT 1,
    last_mention_message_id INTEGER,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (first_mention_message_id) REFERENCES messages(id) ON DELETE SET NULL,
    FOREIGN KEY (last_mention_message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_entities_conversation ON conversation_entities(conversation_id);
CREATE INDEX idx_entities_type ON conversation_entities(entity_type);
CREATE INDEX idx_entities_value ON conversation_entities(entity_value);
CREATE INDEX idx_entities_confidence ON conversation_entities(confidence DESC);
```

#### Table: `conversation_files`

```sql
CREATE TABLE conversation_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('read', 'write', 'create', 'delete', 'reference')),
    message_id INTEGER,                     -- Message where file was mentioned
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_files_conversation ON conversation_files(conversation_id);
CREATE INDEX idx_files_path ON conversation_files(file_path);
CREATE INDEX idx_files_action ON conversation_files(action);
```

---

### Tier 2: Long-Term Knowledge (8 tables)

#### Table: `patterns`

```sql
CREATE TABLE patterns (
    id TEXT PRIMARY KEY,                    -- UUID
    pattern_type TEXT NOT NULL CHECK(pattern_type IN (
        'workflow', 'intent', 'file_relationship', 'architectural',
        'validation', 'correction', 'test', 'naming'
    )),
    name TEXT NOT NULL,
    description TEXT,
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    usage_count INTEGER NOT NULL DEFAULT 1,
    success_count INTEGER NOT NULL DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_conversations TEXT,              -- JSON array of conversation IDs
    metadata TEXT,
    tags TEXT
);

-- Indexes
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON patterns(confidence DESC);
CREATE INDEX idx_patterns_usage ON patterns(usage_count DESC);
CREATE INDEX idx_patterns_success_rate ON patterns((CAST(success_count AS REAL) / usage_count) DESC);
CREATE INDEX idx_patterns_last_used ON patterns(last_used DESC);
CREATE INDEX idx_patterns_created ON patterns(created_at DESC);

-- Pattern decay trigger
CREATE TRIGGER pattern_decay
AFTER UPDATE OF last_used ON patterns
WHEN (julianday('now') - julianday(new.last_used)) > 90
BEGIN
    UPDATE patterns
    SET confidence = MAX(0.3, confidence * 0.95)
    WHERE id = new.id;
END;
```

#### Table: `workflow_steps`

```sql
CREATE TABLE workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    step_type TEXT NOT NULL CHECK(step_type IN (
        'plan', 'test_create', 'implement', 'refactor', 'validate', 'commit', 'deploy'
    )),
    description TEXT NOT NULL,
    agent TEXT,
    estimated_duration_seconds INTEGER,
    success_rate REAL,
    common_errors TEXT,                     -- JSON array
    metadata TEXT,
    FOREIGN KEY (pattern_id) REFERENCES patterns(id) ON DELETE CASCADE,
    UNIQUE(pattern_id, step_number)
);

-- Indexes
CREATE INDEX idx_workflow_pattern ON workflow_steps(pattern_id, step_number);
CREATE INDEX idx_workflow_type ON workflow_steps(step_type);
```

#### Table: `file_relationships`

```sql
CREATE TABLE file_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_a TEXT NOT NULL,
    file_b TEXT NOT NULL,
    relationship_type TEXT NOT NULL CHECK(relationship_type IN (
        'co_modification', 'dependency', 'test_target', 'component_parent', 'api_consumer'
    )),
    co_occurrence_count INTEGER NOT NULL DEFAULT 1,
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    last_observed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    CHECK(file_a < file_b)
);

-- Indexes
CREATE INDEX idx_file_rel_files ON file_relationships(file_a, file_b);
CREATE INDEX idx_file_rel_type ON file_relationships(relationship_type);
CREATE INDEX idx_file_rel_confidence ON file_relationships(confidence DESC);
CREATE INDEX idx_file_rel_count ON file_relationships(co_occurrence_count DESC);

-- Unique constraint
CREATE UNIQUE INDEX idx_file_rel_unique ON file_relationships(file_a, file_b, relationship_type);
```

#### Table: `intent_patterns`

```sql
CREATE TABLE intent_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase_pattern TEXT NOT NULL,
    intent TEXT NOT NULL CHECK(intent IN ('PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'GOVERN', 'CORRECT', 'RESUME', 'ASK')),
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    match_count INTEGER NOT NULL DEFAULT 1,
    success_count INTEGER NOT NULL DEFAULT 0,
    last_matched TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    UNIQUE(phrase_pattern, intent)
);

-- Indexes
CREATE INDEX idx_intent_phrase ON intent_patterns(phrase_pattern);
CREATE INDEX idx_intent_type ON intent_patterns(intent);
CREATE INDEX idx_intent_confidence ON intent_patterns(confidence DESC);
CREATE INDEX idx_intent_success ON intent_patterns((CAST(success_count AS REAL) / match_count) DESC);
```

#### Table: `architectural_patterns`

```sql
CREATE TABLE architectural_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_type TEXT NOT NULL,
    location_pattern TEXT NOT NULL,
    naming_convention TEXT,
    template_structure TEXT,               -- JSON template
    dependencies_pattern TEXT,              -- JSON array
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    example_count INTEGER NOT NULL DEFAULT 1,
    last_observed TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_arch_type ON architectural_patterns(component_type);
CREATE INDEX idx_arch_confidence ON architectural_patterns(confidence DESC);
CREATE INDEX idx_arch_examples ON architectural_patterns(example_count DESC);
```

#### Table: `validation_insights`

```sql
CREATE TABLE validation_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL CHECK(insight_type IN (
        'file_confusion', 'missing_test', 'build_error', 'test_failure', 'anti_pattern', 'performance'
    )),
    pattern_name TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_validation_type ON validation_insights(insight_type);
CREATE INDEX idx_validation_pattern ON validation_insights(pattern_name);
CREATE INDEX idx_validation_confidence ON validation_insights(confidence DESC);
CREATE INDEX idx_validation_count ON validation_insights(occurrence_count DESC);
```

#### Table: `correction_history`

```sql
CREATE TABLE correction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correction_type TEXT NOT NULL CHECK(correction_type IN (
        'wrong_file', 'wrong_intent', 'architectural_violation', 'tdd_skip', 'dod_violation'
    )),
    error_description TEXT NOT NULL,
    correction_action TEXT NOT NULL,
    conversation_id TEXT,                   -- Where correction happened
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_correction_type ON correction_history(correction_type);
CREATE INDEX idx_correction_conversation ON correction_history(conversation_id);
CREATE INDEX idx_correction_timestamp ON correction_history(occurred_at DESC);
```

#### Table: `test_patterns`

```sql
CREATE TABLE test_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_type TEXT NOT NULL CHECK(test_type IN ('ui', 'unit', 'integration', 'e2e')),
    pattern_name TEXT NOT NULL,
    framework TEXT NOT NULL,                -- e.g., 'Playwright', 'Jest', 'xUnit'
    selector_pattern TEXT,                  -- For UI tests (ID-based recommended)
    test_data_pattern TEXT,                 -- JSON template
    success_rate REAL,
    usage_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_test_type ON test_patterns(test_type);
CREATE INDEX idx_test_framework ON test_patterns(framework);
CREATE INDEX idx_test_success ON test_patterns(success_rate DESC);
```

---

### Tier 3: Development Context (11 tables)

#### Table: `context_git_metrics`

```sql
CREATE TABLE context_git_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    commits_count INTEGER NOT NULL DEFAULT 0,
    lines_added INTEGER NOT NULL DEFAULT 0,
    lines_deleted INTEGER NOT NULL DEFAULT 0,
    net_growth INTEGER NOT NULL DEFAULT 0,
    files_changed INTEGER NOT NULL DEFAULT 0,
    contributor TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, contributor)
);

-- Indexes
CREATE INDEX idx_git_date ON context_git_metrics(metric_date DESC);
CREATE INDEX idx_git_contributor ON context_git_metrics(contributor);
CREATE INDEX idx_git_commits ON context_git_metrics(commits_count DESC);

-- Materialized view for velocity
CREATE VIEW git_velocity AS
SELECT 
    date(metric_date, '-' || (strftime('%w', metric_date)) || ' days') AS week_start,
    SUM(commits_count) AS commits_per_week,
    SUM(lines_added) AS lines_added_per_week,
    SUM(lines_deleted) AS lines_deleted_per_week,
    SUM(net_growth) AS net_growth_per_week,
    COUNT(DISTINCT metric_date) AS days_with_activity
FROM context_git_metrics
WHERE metric_date >= date('now', '-30 days')
    AND contributor IS NULL
GROUP BY week_start
ORDER BY week_start DESC;
```

#### Table: `context_file_hotspots`

```sql
CREATE TABLE context_file_hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_commits INTEGER NOT NULL DEFAULT 0,
    file_edits INTEGER NOT NULL DEFAULT 0,
    churn_rate REAL NOT NULL CHECK(churn_rate >= 0.0 AND churn_rate <= 1.0),
    stability TEXT NOT NULL CHECK(stability IN ('STABLE', 'MODERATE', 'UNSTABLE')),
    last_modified TIMESTAMP,
    lines_changed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_path, period_start, period_end)
);

-- Indexes
CREATE INDEX idx_hotspot_file ON context_file_hotspots(file_path);
CREATE INDEX idx_hotspot_churn ON context_file_hotspots(churn_rate DESC);
CREATE INDEX idx_hotspot_stability ON context_file_hotspots(stability);
CREATE INDEX idx_hotspot_period ON context_file_hotspots(period_start, period_end);

-- Stability classification trigger
CREATE TRIGGER classify_file_stability
BEFORE INSERT ON context_file_hotspots
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.churn_rate < 0.10 THEN 'STABLE'
        WHEN NEW.churn_rate < 0.20 THEN 'MODERATE'
        ELSE 'UNSTABLE'
    END INTO NEW.stability;
END;
```

#### Table: `context_test_metrics`

```sql
CREATE TABLE context_test_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    test_type TEXT NOT NULL CHECK(test_type IN ('ui', 'unit', 'integration', 'e2e')),
    tests_discovered INTEGER NOT NULL DEFAULT 0,
    tests_run INTEGER NOT NULL DEFAULT 0,
    tests_passed INTEGER NOT NULL DEFAULT 0,
    tests_failed INTEGER NOT NULL DEFAULT 0,
    tests_skipped INTEGER NOT NULL DEFAULT 0,
    pass_rate REAL CHECK(pass_rate >= 0.0 AND pass_rate <= 1.0),
    coverage_percentage REAL CHECK(coverage_percentage >= 0.0 AND coverage_percentage <= 1.0),
    avg_duration_seconds REAL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, test_type)
);

-- Indexes
CREATE INDEX idx_test_date ON context_test_metrics(metric_date DESC);
CREATE INDEX idx_test_type ON context_test_metrics(test_type);
CREATE INDEX idx_test_pass_rate ON context_test_metrics(pass_rate DESC);
CREATE INDEX idx_test_coverage ON context_test_metrics(coverage_percentage DESC);
```

#### Table: `context_flaky_tests`

```sql
CREATE TABLE context_flaky_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    test_type TEXT NOT NULL CHECK(test_type IN ('ui', 'unit', 'integration', 'e2e')),
    first_detected TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_runs INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    failure_rate REAL NOT NULL CHECK(failure_rate >= 0.0 AND failure_rate <= 1.0),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'FIXED', 'IGNORED')),
    failure_pattern TEXT,                   -- JSON array
    resolution_notes TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_name)
);

-- Indexes
CREATE INDEX idx_flaky_name ON context_flaky_tests(test_name);
CREATE INDEX idx_flaky_rate ON context_flaky_tests(failure_rate DESC);
CREATE INDEX idx_flaky_status ON context_flaky_tests(status);
CREATE INDEX idx_flaky_last_seen ON context_flaky_tests(last_seen DESC);

-- Auto-mark as FIXED trigger
CREATE TRIGGER auto_fix_flaky_tests
AFTER UPDATE OF last_seen ON context_flaky_tests
WHEN NEW.status = 'ACTIVE'
    AND (julianday('now') - julianday(NEW.last_seen)) > 30
BEGIN
    UPDATE context_flaky_tests
    SET status = 'FIXED',
        resolution_notes = 'Auto-resolved: No failures in 30 days'
    WHERE id = NEW.id;
END;
```

#### Table: `context_build_metrics`

```sql
CREATE TABLE context_build_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    builds_total INTEGER NOT NULL DEFAULT 0,
    builds_successful INTEGER NOT NULL DEFAULT 0,
    builds_failed INTEGER NOT NULL DEFAULT 0,
    success_rate REAL CHECK(success_rate >= 0.0 AND success_rate <= 1.0),
    avg_build_time_seconds REAL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date)
);

-- Indexes
CREATE INDEX idx_build_date ON context_build_metrics(metric_date DESC);
CREATE INDEX idx_build_success_rate ON context_build_metrics(success_rate DESC);
```

#### Table: `context_work_patterns`

```sql
CREATE TABLE context_work_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_date DATE NOT NULL,
    time_slot TEXT NOT NULL CHECK(time_slot IN (
        '00-02', '02-04', '04-06', '06-08', '08-10', '10-12',
        '12-14', '14-16', '16-18', '18-20', '20-22', '22-24'
    )),
    sessions_count INTEGER NOT NULL DEFAULT 0,
    sessions_successful INTEGER NOT NULL DEFAULT 0,
    success_rate REAL CHECK(success_rate >= 0.0 AND success_rate <= 1.0),
    avg_duration_minutes INTEGER,
    avg_focus_duration_minutes INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pattern_date, time_slot)
);

-- Indexes
CREATE INDEX idx_work_date ON context_work_patterns(pattern_date DESC);
CREATE INDEX idx_work_slot ON context_work_patterns(time_slot);
CREATE INDEX idx_work_success ON context_work_patterns(success_rate DESC);

-- Materialized view for best times
CREATE VIEW best_work_times AS
SELECT 
    time_slot,
    SUM(sessions_count) AS total_sessions,
    SUM(sessions_successful) AS total_successful,
    AVG(success_rate) AS avg_success_rate,
    AVG(avg_duration_minutes) AS avg_duration
FROM context_work_patterns
WHERE pattern_date >= date('now', '-30 days')
GROUP BY time_slot
HAVING total_sessions >= 3
ORDER BY avg_success_rate DESC;
```

#### Table: `context_cortex_usage`

```sql
CREATE TABLE context_cortex_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    intent_type TEXT NOT NULL CHECK(intent_type IN ('PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'GOVERN', 'CORRECT', 'RESUME', 'ASK')),
    requests_count INTEGER NOT NULL DEFAULT 0,
    successful_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    avg_response_time_seconds REAL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, intent_type)
);

-- Indexes
CREATE INDEX idx_cortex_date ON context_cortex_usage(metric_date DESC);
CREATE INDEX idx_cortex_intent ON context_cortex_usage(intent_type);
CREATE INDEX idx_cortex_success ON context_cortex_usage((CAST(successful_count AS REAL) / requests_count) DESC);
```

#### Table: `context_correlations`

```sql
CREATE TABLE context_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    metric_a TEXT NOT NULL,
    metric_b TEXT NOT NULL,
    correlation_coefficient REAL NOT NULL CHECK(correlation_coefficient >= -1.0 AND correlation_coefficient <= 1.0),
    sample_size INTEGER NOT NULL,
    confidence_level REAL NOT NULL CHECK(confidence_level >= 0.0 AND confidence_level <= 1.0),
    insight TEXT,
    last_calculated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_corr_name ON context_correlations(correlation_name);
CREATE INDEX idx_corr_coefficient ON context_correlations(ABS(correlation_coefficient) DESC);
CREATE INDEX idx_corr_confidence ON context_correlations(confidence_level DESC);

-- Pre-defined correlations
INSERT INTO context_correlations (correlation_name, description, metric_a, metric_b, correlation_coefficient, sample_size, confidence_level, insight) VALUES
('commit_size_vs_success', 'Correlation between commit size and success rate', 'lines_changed', 'success_rate', -0.72, 0, 0.0, 'Pending calculation'),
('test_first_vs_rework', 'Correlation between TDD and rework rate', 'test_first_flag', 'rework_rate', -0.85, 0, 0.0, 'Pending calculation'),
('cortex_usage_vs_velocity', 'Correlation between CORTEX usage and commit velocity', 'cortex_usage_rate', 'velocity', 0.79, 0, 0.0, 'Pending calculation'),
('session_duration_vs_quality', 'Correlation between session length and success rate', 'session_duration', 'success_rate', -0.34, 0, 0.0, 'Pending calculation');
```

#### Table: `context_insights`

```sql
CREATE TABLE context_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL CHECK(insight_type IN (
        'velocity_drop', 'file_hotspot', 'flaky_test', 'build_health',
        'test_coverage', 'productivity_time', 'session_duration', 'correlation_discovery'
    )),
    severity TEXT NOT NULL DEFAULT 'INFO' CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    related_entity TEXT,
    data_snapshot TEXT,                     -- JSON
    acknowledged BOOLEAN NOT NULL DEFAULT 0,
    acknowledged_at TIMESTAMP,
    dismissed BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_insight_type ON context_insights(insight_type);
CREATE INDEX idx_insight_severity ON context_insights(severity);
CREATE INDEX idx_insight_entity ON context_insights(related_entity);
CREATE INDEX idx_insight_active ON context_insights(acknowledged, dismissed);
CREATE INDEX idx_insight_created ON context_insights(created_at DESC);
```

#### Table: `context_collection_log`

```sql
CREATE TABLE context_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    collector_name TEXT NOT NULL,
    collection_type TEXT NOT NULL CHECK(collection_type IN ('full', 'delta')),
    records_processed INTEGER NOT NULL DEFAULT 0,
    duration_seconds REAL NOT NULL,
    success BOOLEAN NOT NULL DEFAULT 1,
    error_message TEXT,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_collection_timestamp ON context_collection_log(collection_timestamp DESC);
CREATE INDEX idx_collection_name ON context_collection_log(collector_name);
CREATE INDEX idx_collection_success ON context_collection_log(success);
```

---

## 🔗 Cross-Tier Relationships

### Foreign Key Constraints

```sql
-- Tier 1 → Tier 2 (Pattern extraction)
ALTER TABLE patterns ADD COLUMN source_conversation_ids TEXT;  -- JSON array

-- Tier 2 → Tier 3 (Validation correlation)
-- No direct FK (different lifecycle)

-- Tier 0 ← All Tiers (Read-only reference)
-- No FK (Tier 0 is immutable)
```

### Referential Integrity

**Cascade Deletes:**
- Conversation deleted → All messages deleted
- Conversation deleted → All entities deleted
- Pattern deleted → All workflow steps deleted
- Rule deleted → All examples deleted

**Set NULL on Delete:**
- Message deleted → Entity references set to NULL
- Conversation deleted → Correction history reference set to NULL

---

## 📊 Database Statistics & Optimization

### Table Size Estimates

```sql
-- Query to get table sizes
SELECT 
    name AS table_name,
    SUM(pgsize) AS size_bytes,
    SUM(pgsize) / 1024.0 AS size_kb,
    SUM(pgsize) / 1024.0 / 1024.0 AS size_mb
FROM dbstat
GROUP BY name
ORDER BY size_bytes DESC;
```

**Expected Sizes (after 30 days of use):**

| Table | Rows | Size (KB) | Tier |
|-------|------|-----------|------|
| `messages` | ~2,000 | ~40 KB | Tier 1 |
| `patterns` | ~3,000 | ~60 KB | Tier 2 |
| `context_git_metrics` | ~900 | ~15 KB | Tier 3 |
| `conversations` | 20 | ~5 KB | Tier 1 |
| `workflow_steps` | ~8,000 | ~35 KB | Tier 2 |
| `file_relationships` | ~1,500 | ~25 KB | Tier 2 |
| `conversation_entities` | ~5,000 | ~30 KB | Tier 1 |
| **Total** | **~21,420** | **~300 KB** | **All** |

### Index Analysis

```sql
-- Query to analyze index usage
SELECT 
    name AS index_name,
    tbl_name AS table_name,
    sql AS definition
FROM sqlite_master
WHERE type = 'index'
    AND name NOT LIKE 'sqlite_%'
ORDER BY tbl_name, name;
```

**Total Indexes:** 75+ across all tables

**Most Critical Indexes:**
- `idx_patterns_confidence` - Pattern queries by confidence
- `idx_messages_conversation` - Fast message retrieval
- `idx_git_date` - Recent git metrics
- `idx_hotspot_churn` - File hotspot detection

---

## 🚀 Performance Optimization Strategies

### 1. Indexed Query Patterns

```sql
-- FAST (<10ms): Direct index lookup
SELECT * FROM conversations WHERE id = ?;
SELECT * FROM patterns WHERE confidence > 0.8 ORDER BY confidence DESC LIMIT 10;

-- MEDIUM (<50ms): Index scan with filter
SELECT * FROM messages WHERE conversation_id = ? ORDER BY sequence;
SELECT * FROM context_file_hotspots WHERE churn_rate > 0.2 ORDER BY churn_rate DESC;

-- COMPLEX (<100ms): Join with aggregation
SELECT 
    c.id, c.topic, COUNT(m.id) AS message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.status = 'active'
GROUP BY c.id;
```

### 2. Materialized Views

```sql
-- Pre-computed git velocity (updated on insert)
CREATE VIEW git_velocity AS ...;  -- Already defined above

-- Pre-computed best work times
CREATE VIEW best_work_times AS ...;  -- Already defined above

-- Additional useful views
CREATE VIEW active_patterns AS
SELECT * FROM patterns
WHERE confidence >= 0.5
    AND (last_used IS NULL OR last_used >= date('now', '-90 days'))
ORDER BY confidence DESC, usage_count DESC;

CREATE VIEW recent_insights AS
SELECT * FROM context_insights
WHERE acknowledged = 0
    AND dismissed = 0
    AND (expires_at IS NULL OR expires_at > datetime('now'))
ORDER BY severity DESC, created_at DESC;
```

### 3. Query Optimization Techniques

```sql
-- Use EXPLAIN QUERY PLAN to analyze
EXPLAIN QUERY PLAN
SELECT * FROM patterns WHERE pattern_type = 'workflow' AND confidence > 0.8;

-- Expected output should show "SEARCH" not "SCAN"
-- Example:
-- 0|0|0|SEARCH TABLE patterns USING INDEX idx_patterns_confidence (confidence>?)
```

### 4. WAL Mode for Concurrency

```sql
-- Enable Write-Ahead Logging
PRAGMA journal_mode = WAL;

-- Benefits:
-- - Readers don't block writers
-- - Writers don't block readers
-- - Better concurrency for CORTEX operations
```

### 5. Vacuum and Analyze

```sql
-- Regular maintenance (run weekly)
VACUUM;                    -- Reclaim deleted space
ANALYZE;                   -- Update query planner statistics

-- Auto-vacuum (set once)
PRAGMA auto_vacuum = INCREMENTAL;
```

---

## 🔧 Migration Scripts

### Schema Creation

```python
# scripts/create_schema.py
import sqlite3

def create_cortex_schema(db_path: str):
    """Create complete CORTEX schema in SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read schema from this file
    with open('storage-schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Execute all CREATE statements
    cursor.executescript(schema_sql)
    
    # Verify tables created
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    expected_count = 22
    
    assert len(tables) == expected_count, \
        f"Expected {expected_count} tables, got {len(tables)}"
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created {len(tables)} tables in {db_path}")
```

### Schema Validation

```python
# scripts/validate_schema.py
def validate_cortex_schema(db_path: str):
    """Validate CORTEX schema integrity."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    checks = []
    
    # Check 1: All tables exist
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    table_count = cursor.fetchone()[0]
    checks.append(('Table count', table_count == 22))
    
    # Check 2: All indexes exist
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
    """)
    index_count = cursor.fetchone()[0]
    checks.append(('Index count', index_count >= 75))
    
    # Check 3: Foreign keys enabled
    cursor.execute("PRAGMA foreign_keys")
    fk_enabled = cursor.fetchone()[0] == 1
    checks.append(('Foreign keys', fk_enabled))
    
    # Check 4: All triggers exist
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='trigger'
    """)
    trigger_count = cursor.fetchone()[0]
    checks.append(('Trigger count', trigger_count >= 5))
    
    # Print results
    for check_name, passed in checks:
        status = '✅' if passed else '❌'
        print(f"{status} {check_name}: {passed}")
    
    conn.close()
    
    return all(passed for _, passed in checks)
```

### Data Migration from KDS v8

```python
# scripts/migrate_kds_to_cortex.py
def migrate_kds_data(kds_path: str, cortex_db_path: str):
    """
    Migrate KDS v8 data to CORTEX SQLite.
    
    Migrates:
    - governance/rules.md → governance_rules table
    - conversation-history.jsonl → conversations + messages tables
    - knowledge-graph.yaml → patterns + related tables
    - development-context.yaml → context_* tables
    """
    # Implementation in separate migration script
    pass
```

---

## 📚 Schema Versioning

### Version Table

```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    migration_script TEXT
);

-- Initial version
INSERT INTO schema_version (version, description, migration_script) VALUES
(1, 'Initial CORTEX schema', 'create_schema.sql');
```

### Migration Pattern

```sql
-- Example: Adding new column in v2
-- migration_v2.sql

BEGIN TRANSACTION;

-- Add new column
ALTER TABLE patterns ADD COLUMN hemisphere TEXT CHECK(hemisphere IN ('LEFT', 'RIGHT', 'BOTH'));

-- Update schema version
INSERT INTO schema_version (version, description, migration_script) VALUES
(2, 'Add hemisphere column to patterns', 'migration_v2.sql');

COMMIT;
```

---

## ✅ Testing Schema

### Schema Tests

```python
def test_schema_integrity():
    """Test database schema is correctly created."""
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    create_cortex_schema(':memory:')
    
    # Verify table count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    assert cursor.fetchone()[0] == 22
    
def test_foreign_key_constraints():
    """Test foreign keys enforce referential integrity."""
    conn = sqlite3.connect(':memory:')
    conn.execute("PRAGMA foreign_keys = ON")
    
    create_cortex_schema(':memory:')
    
    # Insert conversation
    conn.execute("""
        INSERT INTO conversations (id, topic) 
        VALUES ('conv_test', 'Test Topic')
    """)
    
    # Insert message with FK
    conn.execute("""
        INSERT INTO messages (conversation_id, sequence, role, content)
        VALUES ('conv_test', 1, 'user', 'Test message')
    """)
    
    # Delete conversation should cascade
    conn.execute("DELETE FROM conversations WHERE id = 'conv_test'")
    
    # Verify message deleted
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = 'conv_test'")
    assert cursor.fetchone()[0] == 0

def test_triggers_fire():
    """Test triggers execute correctly."""
    conn = sqlite3.connect(':memory:')
    create_cortex_schema(':memory:')
    
    # Test FIFO trigger
    for i in range(21):
        conn.execute("""
            INSERT INTO conversations (id, topic, status)
            VALUES (?, ?, ?)
        """, (f'conv_{i}', f'Topic {i}', 'completed'))
    
    # Verify oldest conversation deleted
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE status != 'deleted'")
    assert cursor.fetchone()[0] == 20
```

---

## 📊 Performance Benchmarks

### Query Benchmarks

```python
def benchmark_queries():
    """Benchmark critical query performance."""
    import time
    
    # Populate test data (10,000 patterns)
    populate_test_data(pattern_count=10000)
    
    benchmarks = {}
    
    # Benchmark 1: Fast query (<10ms)
    start = time.time()
    cursor.execute("SELECT * FROM patterns WHERE confidence > 0.8 LIMIT 10")
    cursor.fetchall()
    benchmarks['pattern_lookup'] = (time.time() - start) * 1000
    
    # Benchmark 2: Medium query (<50ms)
    start = time.time()
    cursor.execute("""
        SELECT p.*, COUNT(ws.id) as step_count
        FROM patterns p
        LEFT JOIN workflow_steps ws ON p.id = ws.pattern_id
        WHERE p.pattern_type = 'workflow'
        GROUP BY p.id
        LIMIT 20
    """)
    cursor.fetchall()
    benchmarks['workflow_query'] = (time.time() - start) * 1000
    
    # Print results
    for query, duration_ms in benchmarks.items():
        status = '✅' if duration_ms < 50 else '⚠️'
        print(f"{status} {query}: {duration_ms:.2f}ms")
    
    return benchmarks
```

---

## 📚 Related Documentation

- [Overview](overview.md) - High-level architecture
- [Tier 0: Governance Design](tier0-governance.md)
- [Tier 1: Short-Term Memory Design](tier1-stm-design.md)
- [Tier 2: Long-Term Memory Design](tier2-ltm-design.md)
- [Tier 3: Development Context Design](tier3-context-design.md)
- [Performance Targets](performance-targets.md) (TODO)
- [Agent Contracts](agent-contracts.md) (TODO)

---

**Status:** ✅ Storage Schema Complete  
**Next:** Create Agent Contracts design  
**Version:** 1.0 (Initial specification)
