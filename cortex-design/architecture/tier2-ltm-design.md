# Tier 2: Long-Term Memory (LTM) Design

**Version:** 1.0  
**Date:** 2025-11-06  
**Status:** 🏗️ DESIGN SPECIFICATION  
**Purpose:** Knowledge graph and pattern consolidation (permanent learning)

---

## 🎯 Overview

**Tier 2 = LONG-TERM MEMORY** - Copilot's accumulated wisdom that grows smarter over time.

**Purpose:**
- Store consolidated patterns extracted from deleted Tier 1 conversations
- Learn from successful workflows and common corrections
- Map file relationships and co-modification patterns
- Build architectural knowledge over time
- Enable pattern-based suggestions and proactive warnings
- Provide data-driven estimates based on historical patterns

**Storage:** SQLite (`cortex-brain.db`)  
**Size Target:** <10 MB (grows over time but optimized)  
**Performance Target:** <100ms for pattern queries

**Key Differentiator from Tier 1:**
- **Tier 1:** Raw conversations (last 20, deleted when expired)
- **Tier 2:** Extracted patterns (permanent, confidence-weighted)

---

## 📊 SQLite Schema

### Table: `patterns`

```sql
CREATE TABLE patterns (
    id TEXT PRIMARY KEY,                    -- UUID (e.g., "pattern_workflow_export_feature_abc123")
    pattern_type TEXT NOT NULL CHECK(pattern_type IN (
        'workflow',                         -- Multi-step process patterns
        'intent',                           -- Natural language → intent mappings
        'file_relationship',                -- Files modified together
        'architectural',                    -- Component structure patterns
        'validation',                       -- Common errors/warnings
        'correction',                       -- Copilot mistakes to avoid
        'test',                             -- Testing patterns
        'naming'                            -- Naming conventions
    )),
    name TEXT NOT NULL,                     -- Human-readable pattern name
    description TEXT,                       -- What this pattern represents
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    usage_count INTEGER NOT NULL DEFAULT 1, -- How many times pattern applied
    success_count INTEGER NOT NULL DEFAULT 0, -- How many times it succeeded
    last_used TIMESTAMP,                    -- Last time pattern was referenced
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_conversations TEXT,              -- JSON array of conversation IDs that fed this pattern
    metadata TEXT,                          -- JSON for pattern-specific data
    tags TEXT                               -- JSON array of searchable tags
);

-- Indexes
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON patterns(confidence DESC);
CREATE INDEX idx_patterns_usage ON patterns(usage_count DESC);
CREATE INDEX idx_patterns_success_rate ON patterns((CAST(success_count AS REAL) / usage_count) DESC);
CREATE INDEX idx_patterns_last_used ON patterns(last_used DESC);
CREATE INDEX idx_patterns_created ON patterns(created_at DESC);

-- Pattern decay: reduce confidence for unused patterns
CREATE TRIGGER pattern_decay
AFTER UPDATE OF last_used ON patterns
WHEN (julianday('now') - julianday(new.last_used)) > 90  -- 90 days unused
BEGIN
    UPDATE patterns
    SET confidence = MAX(0.3, confidence * 0.95)  -- Reduce by 5%, floor at 0.3
    WHERE id = new.id;
END;
```

### Table: `workflow_steps`

```sql
CREATE TABLE workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,               -- Foreign key to patterns table
    step_number INTEGER NOT NULL,           -- Order of step in workflow
    step_type TEXT NOT NULL CHECK(step_type IN (
        'plan',                             -- Planning/analysis phase
        'test_create',                      -- Test creation (RED)
        'implement',                        -- Implementation (GREEN)
        'refactor',                         -- Refactoring phase
        'validate',                         -- Validation/health check
        'commit',                           -- Git commit
        'deploy'                            -- Deployment step
    )),
    description TEXT NOT NULL,              -- What this step does
    agent TEXT,                             -- Recommended agent for this step
    estimated_duration_seconds INTEGER,     -- Average time for this step
    success_rate REAL,                      -- Historical success rate (0.0-1.0)
    common_errors TEXT,                     -- JSON array of common errors
    metadata TEXT,                          -- JSON for step-specific data
    FOREIGN KEY (pattern_id) REFERENCES patterns(id) ON DELETE CASCADE,
    UNIQUE(pattern_id, step_number)
);

-- Indexes
CREATE INDEX idx_workflow_pattern ON workflow_steps(pattern_id, step_number);
CREATE INDEX idx_workflow_type ON workflow_steps(step_type);
```

### Table: `file_relationships`

```sql
CREATE TABLE file_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_a TEXT NOT NULL,                   -- First file in relationship
    file_b TEXT NOT NULL,                   -- Second file in relationship
    relationship_type TEXT NOT NULL CHECK(relationship_type IN (
        'co_modification',                  -- Modified together frequently
        'dependency',                       -- File A depends on File B
        'test_target',                      -- File A tests File B
        'component_parent',                 -- File A contains File B
        'api_consumer'                      -- File A calls API in File B
    )),
    co_occurrence_count INTEGER NOT NULL DEFAULT 1,  -- How many times modified together
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    last_observed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    CHECK(file_a < file_b)                  -- Enforce alphabetical ordering to prevent duplicates
);

-- Indexes
CREATE INDEX idx_file_rel_files ON file_relationships(file_a, file_b);
CREATE INDEX idx_file_rel_type ON file_relationships(relationship_type);
CREATE INDEX idx_file_rel_confidence ON file_relationships(confidence DESC);
CREATE INDEX idx_file_rel_count ON file_relationships(co_occurrence_count DESC);

-- Unique constraint
CREATE UNIQUE INDEX idx_file_rel_unique ON file_relationships(file_a, file_b, relationship_type);
```

### Table: `intent_patterns`

```sql
CREATE TABLE intent_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase_pattern TEXT NOT NULL,           -- Regex or text pattern (e.g., "add a button")
    intent TEXT NOT NULL CHECK(intent IN ('PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'GOVERN', 'CORRECT', 'RESUME', 'ASK')),
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    match_count INTEGER NOT NULL DEFAULT 1, -- How many times this pattern matched
    success_count INTEGER NOT NULL DEFAULT 0, -- How many times routing was correct
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

### Table: `architectural_patterns`

```sql
CREATE TABLE architectural_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_type TEXT NOT NULL,           -- e.g., "blazor_component", "service", "api_controller"
    location_pattern TEXT NOT NULL,         -- Path pattern (e.g., "Components/**/*.razor")
    naming_convention TEXT,                 -- e.g., "PascalCase", "kebab-case"
    template_structure TEXT,                -- JSON template for this component type
    dependencies_pattern TEXT,              -- Common dependencies (JSON array)
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    example_count INTEGER NOT NULL DEFAULT 1, -- How many examples observed
    last_observed TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_arch_type ON architectural_patterns(component_type);
CREATE INDEX idx_arch_confidence ON architectural_patterns(confidence DESC);
CREATE INDEX idx_arch_examples ON architectural_patterns(example_count DESC);
```

### Table: `validation_insights`

```sql
CREATE TABLE validation_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL CHECK(insight_type IN (
        'file_confusion',                   -- Wrong file edited
        'missing_test',                     -- Test skipped
        'build_error',                      -- Common build errors
        'test_failure',                     -- Common test failures
        'anti_pattern',                     -- Bad practices detected
        'performance'                       -- Performance issues
    )),
    description TEXT NOT NULL,              -- What the insight is
    trigger_conditions TEXT,                -- JSON: When to show this insight
    recommendation TEXT,                    -- What to do about it
    severity TEXT CHECK(severity IN ('info', 'warning', 'error')),
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    last_occurred TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_validation_type ON validation_insights(insight_type);
CREATE INDEX idx_validation_severity ON validation_insights(severity);
CREATE INDEX idx_validation_count ON validation_insights(occurrence_count DESC);
```

### Table: `correction_history`

```sql
CREATE TABLE correction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL CHECK(error_type IN (
        'wrong_file',                       -- Worked on incorrect file
        'wrong_intent',                     -- Misunderstood user intent
        'architectural_mismatch',           -- Violated architectural pattern
        'test_skip',                        -- Skipped TDD
        'incomplete_implementation'         -- Left work unfinished
    )),
    original_action TEXT NOT NULL,          -- What Copilot tried to do
    correction_action TEXT NOT NULL,        -- What was actually needed
    file_context TEXT,                      -- Files involved (JSON)
    conversation_id TEXT,                   -- Source conversation (if available)
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    last_occurred TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- Indexes
CREATE INDEX idx_correction_type ON correction_history(error_type);
CREATE INDEX idx_correction_count ON correction_history(occurrence_count DESC);
CREATE INDEX idx_correction_last ON correction_history(last_occurred DESC);
```

### FTS5 Virtual Table (Full-Text Search)

```sql
-- Full-text search across patterns
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    name,
    description,
    tags,
    content='patterns',
    content_rowid='rowid'
);

-- Triggers to keep FTS index updated
CREATE TRIGGER patterns_fts_insert AFTER INSERT ON patterns
BEGIN
    INSERT INTO patterns_fts(rowid, name, description, tags)
    VALUES (new.rowid, new.name, new.description, new.tags);
END;

CREATE TRIGGER patterns_fts_delete AFTER DELETE ON patterns
BEGIN
    DELETE FROM patterns_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER patterns_fts_update AFTER UPDATE ON patterns
BEGIN
    UPDATE patterns_fts SET name = new.name, description = new.description, tags = new.tags 
    WHERE rowid = new.rowid;
END;
```

---

## 🔄 Consolidation Algorithm

### Pattern Extraction from Tier 1

**When:** Triggered when a conversation is deleted from Tier 1 (FIFO rotation)

**Process:**

```python
def consolidate_conversation_to_tier2(conversation_id):
    """
    Extract patterns from a Tier 1 conversation before deletion.
    
    This is called by the FIFO trigger when conversation #21 arrives
    and conversation #1 needs to be deleted.
    """
    
    # Step 1: Extract workflow patterns
    workflow_pattern = extract_workflow_pattern(conversation_id)
    if workflow_pattern:
        upsert_workflow_pattern(workflow_pattern)
    
    # Step 2: Extract file relationships
    file_pairs = get_conversation_file_pairs(conversation_id)
    for file_a, file_b in file_pairs:
        upsert_file_relationship(file_a, file_b, 'co_modification')
    
    # Step 3: Extract intent patterns
    messages = get_conversation_messages(conversation_id)
    for msg in messages:
        if msg.role == 'user':
            intent = infer_intent(msg.content)
            upsert_intent_pattern(msg.content, intent)
    
    # Step 4: Extract corrections
    corrections = get_conversation_corrections(conversation_id)
    for correction in corrections:
        upsert_correction_history(correction)
    
    # Step 5: Extract validation insights
    errors = get_conversation_errors(conversation_id)
    for error in errors:
        upsert_validation_insight(error)
    
    # Step 6: Update architectural patterns
    components = get_conversation_components(conversation_id)
    for component in components:
        upsert_architectural_pattern(component)
    
    return True
```

### Workflow Pattern Extraction

```python
def extract_workflow_pattern(conversation_id):
    """
    Analyze conversation messages to identify repeatable workflow.
    
    Example: "Plan → Test (RED) → Implement (GREEN) → Validate → Commit"
    """
    messages = get_messages_with_agents(conversation_id)
    
    # Detect workflow steps
    steps = []
    for msg in messages:
        if msg.role == 'assistant' and msg.agent:
            step_type = infer_step_type(msg.agent, msg.content)
            steps.append({
                'step_number': len(steps) + 1,
                'step_type': step_type,
                'agent': msg.agent,
                'description': extract_step_description(msg.content),
                'estimated_duration': msg.duration_seconds
            })
    
    # Only create pattern if workflow has 3+ steps
    if len(steps) < 3:
        return None
    
    # Check if similar pattern exists
    similar = find_similar_workflow(steps)
    if similar:
        # Merge with existing pattern
        return merge_workflow_patterns(similar, steps)
    else:
        # Create new pattern
        return {
            'pattern_type': 'workflow',
            'name': generate_workflow_name(steps),
            'description': generate_workflow_description(steps),
            'confidence': 0.7,  # Initial confidence
            'steps': steps,
            'source_conversations': [conversation_id]
        }
```

### File Relationship Extraction

```python
def upsert_file_relationship(file_a, file_b, relationship_type):
    """
    Record or update file co-modification pattern.
    
    Confidence increases with each co-occurrence.
    """
    # Ensure alphabetical ordering (file_a < file_b)
    if file_a > file_b:
        file_a, file_b = file_b, file_a
    
    existing = db.query("""
        SELECT * FROM file_relationships
        WHERE file_a = ? AND file_b = ? AND relationship_type = ?
    """, (file_a, file_b, relationship_type))
    
    if existing:
        # Update existing relationship
        new_count = existing.co_occurrence_count + 1
        new_confidence = min(0.98, 0.5 + (new_count * 0.05))  # Cap at 0.98
        
        db.execute("""
            UPDATE file_relationships
            SET co_occurrence_count = ?,
                confidence = ?,
                last_observed = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_count, new_confidence, existing.id))
    else:
        # Create new relationship
        db.execute("""
            INSERT INTO file_relationships (file_a, file_b, relationship_type, confidence)
            VALUES (?, ?, ?, 0.5)
        """, (file_a, file_b, relationship_type))
```

### Intent Pattern Learning

```python
def upsert_intent_pattern(phrase, intent, was_correct=True):
    """
    Learn from user phrases and their corresponding intents.
    
    Over time, builds vocabulary for accurate routing.
    """
    # Normalize phrase for pattern matching
    pattern = normalize_phrase_to_pattern(phrase)
    
    existing = db.query("""
        SELECT * FROM intent_patterns
        WHERE phrase_pattern = ? AND intent = ?
    """, (pattern, intent))
    
    if existing:
        # Update existing pattern
        new_match_count = existing.match_count + 1
        new_success_count = existing.success_count + (1 if was_correct else 0)
        success_rate = new_success_count / new_match_count
        new_confidence = min(0.98, success_rate)
        
        db.execute("""
            UPDATE intent_patterns
            SET match_count = ?,
                success_count = ?,
                confidence = ?,
                last_matched = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_match_count, new_success_count, new_confidence, existing.id))
    else:
        # Create new pattern
        db.execute("""
            INSERT INTO intent_patterns (phrase_pattern, intent, confidence)
            VALUES (?, ?, 0.7)
        """, (pattern, intent))

def normalize_phrase_to_pattern(phrase):
    """
    Convert specific phrase to generalized pattern.
    
    Examples:
    - "Add purple button" → "add [color] button"
    - "Create InvoiceService" → "create [name]Service"
    - "Test the export feature" → "test the [feature]"
    """
    # Implementation would use NLP/regex to identify variables
    # and replace with placeholders
    pass
```

---

## 🔍 Query Patterns (Usage Examples)

### Query 1: Find Similar Workflows

```sql
-- Find workflow patterns similar to current task
SELECT p.*, COUNT(ws.id) as step_count
FROM patterns p
LEFT JOIN workflow_steps ws ON p.id = ws.pattern_id
WHERE p.pattern_type = 'workflow'
  AND p.confidence >= 0.7
  AND p.tags LIKE '%export%'  -- Task-specific tag
GROUP BY p.id
ORDER BY p.confidence DESC, p.usage_count DESC
LIMIT 5;
```

### Query 2: Find Related Files

```sql
-- Find files commonly modified with target file
SELECT 
    CASE 
        WHEN fr.file_a = ? THEN fr.file_b
        ELSE fr.file_a
    END as related_file,
    fr.relationship_type,
    fr.confidence,
    fr.co_occurrence_count,
    fr.last_observed
FROM file_relationships fr
WHERE (fr.file_a = ? OR fr.file_b = ?)
  AND fr.confidence >= 0.6
ORDER BY fr.confidence DESC, fr.co_occurrence_count DESC
LIMIT 10;
```

### Query 3: Detect Intent from User Message

```sql
-- Match user message against known intent patterns
SELECT 
    ip.intent,
    ip.confidence,
    ip.phrase_pattern,
    (CAST(ip.success_count AS REAL) / ip.match_count) as success_rate
FROM intent_patterns ip
WHERE ip.phrase_pattern LIKE '%' || ? || '%'  -- Fuzzy matching
  OR ? LIKE '%' || ip.phrase_pattern || '%'
ORDER BY ip.confidence DESC, success_rate DESC
LIMIT 3;
```

### Query 4: Get Architectural Guidance

```sql
-- Find architectural pattern for component type
SELECT 
    ap.component_type,
    ap.location_pattern,
    ap.naming_convention,
    ap.template_structure,
    ap.dependencies_pattern,
    ap.confidence
FROM architectural_patterns ap
WHERE ap.component_type = ?  -- e.g., "blazor_component"
  AND ap.confidence >= 0.7
ORDER BY ap.example_count DESC, ap.confidence DESC
LIMIT 1;
```

### Query 5: Proactive Warning Lookup

```sql
-- Check for common mistakes when working on file
SELECT 
    vi.description,
    vi.recommendation,
    vi.severity,
    vi.occurrence_count
FROM validation_insights vi
WHERE vi.insight_type = 'file_confusion'
  AND vi.trigger_conditions LIKE '%' || ? || '%'  -- File name
  AND vi.occurrence_count >= 3  -- Must have happened multiple times
ORDER BY vi.occurrence_count DESC, vi.severity
LIMIT 5;
```

### Query 6: Learn from Corrections

```sql
-- Find similar past corrections to avoid repeating mistakes
SELECT 
    ch.error_type,
    ch.original_action,
    ch.correction_action,
    ch.file_context,
    ch.occurrence_count
FROM correction_history ch
WHERE ch.file_context LIKE '%' || ? || '%'  -- Current file
  OR ch.error_type = ?  -- Current error type
ORDER BY ch.occurrence_count DESC, ch.last_occurred DESC
LIMIT 3;
```

---

## 📈 Confidence Scoring System

### Initial Confidence Assignment

**New Pattern Sources:**

| Source | Initial Confidence | Rationale |
|--------|-------------------|-----------|
| Direct observation (imports, dependencies) | 0.95 | High certainty |
| Successful workflow completion | 0.85 | Proven pattern |
| Single conversation extraction | 0.70 | Good starting point |
| Inferred pattern (naming, location) | 0.60 | Reasonable assumption |
| Statistical correlation | 0.50 | Needs validation |

### Confidence Updates (Reinforcement Learning)

**Success Reinforcement:**
```python
def reinforce_pattern_success(pattern_id):
    """
    Increase confidence when pattern is used successfully.
    """
    pattern = get_pattern(pattern_id)
    
    # Increment usage and success counters
    new_usage = pattern.usage_count + 1
    new_success = pattern.success_count + 1
    success_rate = new_success / new_usage
    
    # Update confidence (asymptotic approach to 0.98)
    new_confidence = min(0.98, pattern.confidence + (0.98 - pattern.confidence) * 0.1)
    
    db.execute("""
        UPDATE patterns
        SET usage_count = ?,
            success_count = ?,
            confidence = ?,
            last_used = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_usage, new_success, new_confidence, pattern_id))
```

**Failure Penalty:**
```python
def penalize_pattern_failure(pattern_id):
    """
    Decrease confidence when pattern leads to error.
    """
    pattern = get_pattern(pattern_id)
    
    # Increment usage, don't increment success
    new_usage = pattern.usage_count + 1
    success_rate = pattern.success_count / new_usage
    
    # Reduce confidence (exponential decay)
    new_confidence = max(0.3, pattern.confidence * 0.85)
    
    db.execute("""
        UPDATE patterns
        SET usage_count = ?,
            confidence = ?,
            last_used = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_usage, new_confidence, pattern_id))
```

**Pattern Decay (Automatic via Trigger):**
```sql
-- Defined earlier in schema
-- Reduces confidence by 5% if unused for 90+ days
-- Floor at 0.3 to prevent deletion of potentially useful patterns
```

### Confidence Thresholds for Actions

| Confidence Range | Action | Description |
|-----------------|--------|-------------|
| 0.90 - 1.00 | **Auto-apply** | High confidence, apply automatically |
| 0.70 - 0.89 | **Suggest** | Good confidence, present as option |
| 0.50 - 0.69 | **Consider** | Moderate confidence, mention if relevant |
| 0.30 - 0.49 | **Monitor** | Low confidence, track but don't suggest |
| 0.00 - 0.29 | **Prune** | Very low confidence, candidate for deletion |

---

## 🔄 Pattern Lifecycle

### 1. **Birth** (Pattern Created)

**Trigger:** Conversation deleted from Tier 1, patterns extracted

```
Conversation #1 deleted (FIFO)
    ↓
Extract workflow pattern
    ↓
Pattern created with confidence = 0.70
    ↓
Stored in Tier 2
```

### 2. **Growth** (Pattern Reinforced)

**Trigger:** Pattern successfully applied to new work

```
User: "Add invoice export"
    ↓
Query Tier 2 → Find "export_feature_workflow" (confidence 0.72)
    ↓
Apply pattern successfully
    ↓
Reinforce pattern: confidence 0.72 → 0.75
                   usage_count: 3 → 4
                   success_count: 2 → 3
```

### 3. **Maturity** (Pattern Stabilizes)

**Trigger:** Pattern reaches high confidence through repeated success

```
Pattern used 20+ times successfully
    ↓
Confidence stabilizes at 0.92-0.98
    ↓
Pattern becomes "trusted" - auto-applied without confirmation
```

### 4. **Decay** (Pattern Ages)

**Trigger:** Pattern unused for 90+ days

```
Last used: 2025-08-01
Current date: 2025-11-06 (98 days later)
    ↓
Decay trigger fires
    ↓
Confidence: 0.85 → 0.81 (5% reduction)
    ↓
Still preserved but lower priority
```

### 5. **Obsolescence** (Pattern Becomes Irrelevant)

**Trigger:** Confidence drops below 0.30 due to failures or decay

```
Confidence falls to 0.28
    ↓
Pattern marked for deletion
    ↓
Archived to historical data (optional)
    ↓
Removed from active query results
```

### 6. **Revival** (Old Pattern Becomes Relevant Again)

**Trigger:** Decayed pattern successfully applied

```
Old pattern (confidence 0.35) matched
    ↓
Applied successfully
    ↓
Confidence: 0.35 → 0.42 (reinforcement)
    ↓
Pattern "revived" back into active use
```

---

## 🔗 Integration with Other Tiers

### Tier 1 → Tier 2 (Pattern Extraction)

**Trigger:** FIFO rotation deletes conversation from Tier 1

```sql
-- Tier 1 FIFO trigger (in conversations table)
CREATE TRIGGER enforce_fifo_limit
AFTER INSERT ON conversations
WHEN (SELECT COUNT(*) FROM conversations WHERE status != 'deleted') > 20
BEGIN
    -- Call Tier 2 consolidation BEFORE deletion
    SELECT consolidate_conversation(?);  -- Custom function
    
    -- Then mark oldest for deletion
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

### Tier 2 → Tier 3 (Development Metrics Feed)

**Purpose:** Tier 2 patterns inform Tier 3 metrics analysis

```python
def enrich_tier3_metrics_with_tier2_patterns():
    """
    Use Tier 2 patterns to enhance Tier 3 development context.
    
    Example: Tier 2 knows "HostControlPanel.razor often modified with noor-canvas.css"
             Tier 3 can now warn: "This file is a hotspot (Tier 2 pattern)"
    """
    
    # Get file relationships from Tier 2
    hotspots = db.query("""
        SELECT file_a, file_b, confidence, co_occurrence_count
        FROM file_relationships
        WHERE relationship_type = 'co_modification'
          AND confidence >= 0.7
        ORDER BY co_occurrence_count DESC
    """)
    
    # Feed to Tier 3 for correlation analysis
    for hotspot in hotspots:
        tier3.record_file_correlation(
            file_a=hotspot.file_a,
            file_b=hotspot.file_b,
            confidence=hotspot.confidence,
            source='tier2_learning'
        )
```

### Tier 3 → Tier 2 (Velocity Validation)

**Purpose:** Tier 3 git metrics validate Tier 2 workflow estimates

```python
def validate_workflow_estimates_from_git():
    """
    Compare Tier 2 workflow time estimates with actual Tier 3 git data.
    
    Adjust estimates based on real-world performance.
    """
    
    # Get workflows with time estimates
    workflows = db.query("""
        SELECT p.id, p.name, SUM(ws.estimated_duration_seconds) as total_estimate
        FROM patterns p
        JOIN workflow_steps ws ON p.id = ws.pattern_id
        WHERE p.pattern_type = 'workflow'
        GROUP BY p.id
    """)
    
    for workflow in workflows:
        # Get actual times from Tier 3
        actual_times = tier3.get_feature_completion_times(workflow.name)
        
        if actual_times:
            avg_actual = sum(actual_times) / len(actual_times)
            
            # Update workflow step estimates
            if abs(avg_actual - workflow.total_estimate) > (workflow.total_estimate * 0.2):
                # Estimate is off by >20%, adjust
                adjustment_factor = avg_actual / workflow.total_estimate
                update_workflow_step_estimates(workflow.id, adjustment_factor)
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  TIER 1 (STM)  │ ◄───── Active conversation recorded
         │ Last 20 convos │
         └────────┬───────┘
                  │
                  │ FIFO rotation (conversation #21 arrives)
                  │
                  ▼
         ┌────────────────┐
         │ CONSOLIDATION  │ ◄───── Extract patterns before deletion
         │    PROCESS     │
         └────────┬───────┘
                  │
                  ├─────► Workflow patterns
                  ├─────► File relationships
                  ├─────► Intent patterns
                  ├─────► Architectural patterns
                  ├─────► Validation insights
                  └─────► Correction history
                  │
                  ▼
         ┌────────────────┐
         │  TIER 2 (LTM)  │ ◄───── Patterns stored permanently
         │ Knowledge Graph│
         └────────┬───────┘
                  │
                  ├─────► Query: "Find similar workflow"
                  ├─────► Query: "Related files?"
                  ├─────► Query: "Detect intent"
                  └─────► Query: "Architectural guidance"
                  │
                  ▼
         ┌────────────────┐
         │ AGENT ROUTING  │ ◄───── Intent router queries Tier 2
         │  & EXECUTION   │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │   TIER 3 (DC)  │ ◄───── Development context feeds back
         │  Git, Tests,   │         to validate Tier 2 estimates
         │    Velocity    │
         └────────────────┘
```

---

## ⚡ Performance Optimization

### Indexing Strategy

**Primary Indexes (Already Defined):**
- Pattern type, confidence, usage count, success rate
- File relationships by files, type, confidence
- Intent patterns by phrase, intent, confidence
- FTS5 for full-text search on names and descriptions

**Composite Indexes (Additional):**

```sql
-- Query: Find high-confidence workflows with many steps
CREATE INDEX idx_patterns_workflow_confidence 
ON patterns(pattern_type, confidence DESC, usage_count DESC)
WHERE pattern_type = 'workflow';

-- Query: Find recent file relationships
CREATE INDEX idx_file_rel_recent 
ON file_relationships(last_observed DESC, confidence DESC)
WHERE confidence >= 0.6;

-- Query: Find successful intent patterns
CREATE INDEX idx_intent_success_rate
ON intent_patterns(intent, (CAST(success_count AS REAL) / match_count) DESC);
```

### Query Performance Targets

| Query Type | Target Time | Complexity |
|------------|-------------|------------|
| Find similar workflow | <100ms | O(log n) with indexes |
| Get related files | <50ms | O(1) with hash index |
| Detect intent | <30ms | O(log n) with FTS |
| Architectural lookup | <50ms | O(1) with type index |
| Pattern consolidation | <500ms | O(n) but async |

### Caching Strategy

```python
class Tier2Cache:
    """
    In-memory cache for frequently accessed patterns.
    """
    
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0
    
    def get_pattern(self, pattern_id):
        """Get pattern from cache or DB."""
        if pattern_id in self.cache:
            self.hit_count += 1
            # Move to end (LRU)
            self.cache.move_to_end(pattern_id)
            return self.cache[pattern_id]
        
        # Cache miss
        self.miss_count += 1
        pattern = db.query("SELECT * FROM patterns WHERE id = ?", (pattern_id,))
        
        if pattern:
            self.add_to_cache(pattern_id, pattern)
        
        return pattern
    
    def add_to_cache(self, pattern_id, pattern):
        """Add pattern to cache with LRU eviction."""
        if len(self.cache) >= self.max_size:
            # Evict oldest
            self.cache.popitem(last=False)
        
        self.cache[pattern_id] = pattern
    
    def invalidate(self, pattern_id):
        """Remove pattern from cache when updated."""
        if pattern_id in self.cache:
            del self.cache[pattern_id]
    
    def get_stats(self):
        """Cache hit rate statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }
```

---

## 🔧 Edge Cases & Error Handling

### Edge Case 1: Duplicate Patterns

**Problem:** Multiple conversations extract similar patterns

**Solution:**
```python
def find_similar_workflow(new_steps):
    """
    Detect if workflow pattern already exists before creating duplicate.
    
    Similarity threshold: 80% matching steps
    """
    existing_workflows = db.query("""
        SELECT p.*, GROUP_CONCAT(ws.step_type, ',') as step_sequence
        FROM patterns p
        JOIN workflow_steps ws ON p.id = ws.pattern_id
        WHERE p.pattern_type = 'workflow'
        GROUP BY p.id
    """)
    
    for workflow in existing_workflows:
        existing_steps = workflow.step_sequence.split(',')
        new_step_types = [s['step_type'] for s in new_steps]
        
        similarity = calculate_sequence_similarity(existing_steps, new_step_types)
        
        if similarity >= 0.8:
            # Similar workflow found - merge instead of creating new
            return workflow.id
    
    return None

def merge_workflow_patterns(existing_id, new_steps):
    """
    Merge new observations into existing pattern.
    
    - Average step durations
    - Update confidence
    - Increment usage count
    """
    existing_pattern = get_pattern(existing_id)
    
    # Update confidence (weighted average)
    new_confidence = (existing_pattern.confidence * existing_pattern.usage_count + 0.7) / (existing_pattern.usage_count + 1)
    
    db.execute("""
        UPDATE patterns
        SET confidence = ?,
            usage_count = usage_count + 1,
            source_conversations = json_insert(source_conversations, '$[#]', ?)
        WHERE id = ?
    """, (new_confidence, new_conversation_id, existing_id))
    
    # Update step estimates (weighted average)
    for new_step in new_steps:
        merge_workflow_step(existing_id, new_step)
```

### Edge Case 2: Conflicting Patterns

**Problem:** Two patterns suggest different actions for same situation

**Solution:**
```python
def resolve_pattern_conflict(pattern_a, pattern_b):
    """
    When multiple patterns match, choose based on:
    1. Confidence (higher wins)
    2. Success rate (if confidence similar)
    3. Recency (if success rate similar)
    """
    
    # Confidence difference >10%
    if abs(pattern_a.confidence - pattern_b.confidence) > 0.1:
        return pattern_a if pattern_a.confidence > pattern_b.confidence else pattern_b
    
    # Success rate difference >5%
    success_a = pattern_a.success_count / pattern_a.usage_count
    success_b = pattern_b.success_count / pattern_b.usage_count
    
    if abs(success_a - success_b) > 0.05:
        return pattern_a if success_a > success_b else pattern_b
    
    # Choose more recent
    return pattern_a if pattern_a.last_used > pattern_b.last_used else pattern_b
```

### Edge Case 3: Pattern Explosion

**Problem:** Too many low-confidence patterns clutter database

**Solution:** Periodic cleanup

```sql
-- Delete patterns with very low confidence and no recent usage
DELETE FROM patterns
WHERE confidence < 0.30
  AND last_used < datetime('now', '-180 days')  -- 6 months unused
  AND usage_count < 3;  -- Never really validated
```

### Edge Case 4: Stale Architectural Patterns

**Problem:** Project structure changes, old patterns become obsolete

**Solution:**
```python
def detect_stale_architectural_patterns():
    """
    Validate architectural patterns against current codebase.
    
    Mark as stale if location_pattern no longer matches files.
    """
    patterns = db.query("""
        SELECT * FROM architectural_patterns
        WHERE confidence >= 0.5
    """)
    
    for pattern in patterns:
        # Check if location pattern still valid
        matching_files = glob.glob(pattern.location_pattern, workspace_root)
        
        if len(matching_files) == 0:
            # No files match - pattern is stale
            db.execute("""
                UPDATE architectural_patterns
                SET confidence = 0.2,  -- Mark as obsolete
                    metadata = json_set(metadata, '$.stale', 1)
                WHERE id = ?
            """, (pattern.id,))
        elif len(matching_files) < pattern.example_count * 0.5:
            # Significantly fewer examples - reduce confidence
            db.execute("""
                UPDATE architectural_patterns
                SET confidence = confidence * 0.7
                WHERE id = ?
            """, (pattern.id,))
```

---

## 🧹 Maintenance & Housekeeping

### Daily Maintenance

**Run automatically:** Every 24 hours

```python
def daily_tier2_maintenance():
    """
    Daily housekeeping tasks for Tier 2.
    """
    
    # 1. Update pattern decay (automatic via trigger, but verify)
    db.execute("""
        UPDATE patterns
        SET confidence = MAX(0.3, confidence * 0.95)
        WHERE julianday('now') - julianday(last_used) > 90
          AND confidence > 0.3
    """)
    
    # 2. Recalculate success rates
    db.execute("""
        UPDATE patterns
        SET metadata = json_set(
            metadata, 
            '$.success_rate', 
            CAST(success_count AS REAL) / NULLIF(usage_count, 0)
        )
        WHERE usage_count > 0
    """)
    
    # 3. Update FTS indexes (if manual updates needed)
    db.execute("INSERT INTO patterns_fts(patterns_fts) VALUES('rebuild')")
    db.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    
    # 4. Analyze database for query optimization
    db.execute("ANALYZE")
```

### Weekly Maintenance

**Run automatically:** Every Sunday at 2am

```python
def weekly_tier2_maintenance():
    """
    Weekly deep cleaning and optimization.
    """
    
    # 1. Delete very low confidence patterns
    deleted = db.execute("""
        DELETE FROM patterns
        WHERE confidence < 0.30
          AND last_used < datetime('now', '-180 days')
          AND usage_count < 3
        RETURNING id
    """)
    
    log.info(f"Deleted {len(deleted)} obsolete patterns")
    
    # 2. Consolidate duplicate file relationships
    consolidate_duplicate_file_relationships()
    
    # 3. Detect and mark stale architectural patterns
    detect_stale_architectural_patterns()
    
    # 4. Vacuum database to reclaim space
    db.execute("VACUUM")
    
    # 5. Reindex for performance
    db.execute("REINDEX")
```

### Monthly Maintenance

**Run automatically:** First day of month

```python
def monthly_tier2_maintenance():
    """
    Monthly reporting and health checks.
    """
    
    # 1. Generate pattern health report
    report = {
        'total_patterns': db.scalar("SELECT COUNT(*) FROM patterns"),
        'high_confidence': db.scalar("SELECT COUNT(*) FROM patterns WHERE confidence >= 0.8"),
        'active_patterns': db.scalar("SELECT COUNT(*) FROM patterns WHERE last_used > datetime('now', '-30 days')"),
        'avg_confidence': db.scalar("SELECT AVG(confidence) FROM patterns"),
        'workflow_count': db.scalar("SELECT COUNT(*) FROM patterns WHERE pattern_type = 'workflow'"),
        'file_relationships': db.scalar("SELECT COUNT(*) FROM file_relationships"),
        'intent_patterns': db.scalar("SELECT COUNT(*) FROM intent_patterns")
    }
    
    save_monthly_report(report)
    
    # 2. Identify underutilized patterns for review
    underutilized = db.query("""
        SELECT * FROM patterns
        WHERE created_at < datetime('now', '-90 days')
          AND usage_count < 3
        ORDER BY confidence DESC
    """)
    
    if underutilized:
        log.warning(f"Found {len(underutilized)} underutilized patterns for manual review")
    
    # 3. Export backup
    export_tier2_backup()
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
class TestTier2Consolidation:
    """Test pattern extraction from Tier 1 conversations."""
    
    def test_workflow_extraction(self):
        """Verify workflow pattern correctly extracted."""
        conversation = create_test_conversation(
            messages=[
                {"role": "user", "content": "Add export feature"},
                {"role": "assistant", "agent": "work-planner", "content": "Creating plan..."},
                {"role": "assistant", "agent": "test-generator", "content": "Writing tests..."},
                {"role": "assistant", "agent": "code-executor", "content": "Implementing..."}
            ]
        )
        
        pattern = extract_workflow_pattern(conversation.id)
        
        assert pattern is not None
        assert pattern['pattern_type'] == 'workflow'
        assert len(pattern['steps']) == 3
        assert pattern['steps'][0]['step_type'] == 'plan'
        assert pattern['steps'][1]['step_type'] == 'test_create'
        assert pattern['steps'][2]['step_type'] == 'implement'
    
    def test_file_relationship_extraction(self):
        """Verify file co-modification patterns extracted."""
        conversation = create_test_conversation(
            files=['ComponentA.razor', 'styles.css', 'ComponentA.razor.cs']
        )
        
        consolidate_conversation_to_tier2(conversation.id)
        
        relationships = db.query("""
            SELECT * FROM file_relationships
            WHERE file_a = 'ComponentA.razor' OR file_b = 'ComponentA.razor'
        """)
        
        assert len(relationships) == 2  # ComponentA.razor ↔ styles.css, ComponentA.razor ↔ .cs
        assert all(r.confidence >= 0.5 for r in relationships)
    
    def test_intent_pattern_learning(self):
        """Verify intent patterns learned from messages."""
        upsert_intent_pattern("add a button", "PLAN", was_correct=True)
        upsert_intent_pattern("add a button", "PLAN", was_correct=True)
        upsert_intent_pattern("add a link", "PLAN", was_correct=True)
        
        pattern = db.query_one("""
            SELECT * FROM intent_patterns
            WHERE phrase_pattern LIKE '%add a%'
        """)
        
        assert pattern.confidence >= 0.7
        assert pattern.match_count == 3
        assert pattern.success_count == 3

class TestTier2Queries:
    """Test pattern retrieval and matching."""
    
    def test_find_similar_workflow(self):
        """Verify similar workflow patterns found."""
        # Insert test workflows
        create_test_workflow("export_feature", steps=['plan', 'test_create', 'implement'])
        create_test_workflow("import_feature", steps=['plan', 'test_create', 'implement'])
        
        results = db.query("""
            SELECT * FROM patterns
            WHERE pattern_type = 'workflow'
              AND confidence >= 0.7
        """)
        
        assert len(results) >= 2
    
    def test_file_relationship_query(self):
        """Verify related files found."""
        # Insert test relationships
        create_test_file_relationship("FileA.cs", "FileB.cs", confidence=0.85)
        create_test_file_relationship("FileA.cs", "FileC.cs", confidence=0.65)
        
        related = get_related_files("FileA.cs", min_confidence=0.6)
        
        assert len(related) == 2
        assert related[0].confidence >= related[1].confidence  # Sorted by confidence

class TestTier2Confidence:
    """Test confidence scoring and updates."""
    
    def test_confidence_reinforcement(self):
        """Verify confidence increases with success."""
        pattern_id = create_test_pattern(confidence=0.7, usage_count=1, success_count=1)
        
        reinforce_pattern_success(pattern_id)
        
        updated = get_pattern(pattern_id)
        assert updated.confidence > 0.7
        assert updated.usage_count == 2
        assert updated.success_count == 2
    
    def test_confidence_penalty(self):
        """Verify confidence decreases with failure."""
        pattern_id = create_test_pattern(confidence=0.8, usage_count=5, success_count=4)
        
        penalize_pattern_failure(pattern_id)
        
        updated = get_pattern(pattern_id)
        assert updated.confidence < 0.8
        assert updated.usage_count == 6
        assert updated.success_count == 4  # Unchanged
    
    def test_pattern_decay(self):
        """Verify confidence decays for unused patterns."""
        pattern_id = create_test_pattern(
            confidence=0.85,
            last_used=datetime.now() - timedelta(days=100)
        )
        
        # Manually trigger decay
        db.execute("""
            UPDATE patterns
            SET confidence = MAX(0.3, confidence * 0.95)
            WHERE id = ?
        """, (pattern_id,))
        
        updated = get_pattern(pattern_id)
        assert updated.confidence < 0.85
        assert updated.confidence >= 0.3
```

### Integration Tests

```python
class TestTier1ToTier2Integration:
    """Test Tier 1 → Tier 2 consolidation flow."""
    
    def test_fifo_triggers_consolidation(self):
        """Verify conversation #21 triggers pattern extraction from #1."""
        # Fill Tier 1 with 20 conversations
        for i in range(20):
            create_and_complete_conversation(f"Conversation {i+1}")
        
        # Verify Tier 1 at capacity
        tier1_count = db.scalar("SELECT COUNT(*) FROM conversations WHERE status != 'deleted'")
        assert tier1_count == 20
        
        # Conversation #1 should have extractable patterns
        conv1 = db.query_one("SELECT * FROM conversations ORDER BY created_at ASC LIMIT 1")
        assert conv1 is not None
        
        # Create conversation #21 (triggers FIFO)
        create_and_complete_conversation("Conversation 21")
        
        # Verify Tier 1 still at 20 (oldest deleted)
        tier1_count_after = db.scalar("SELECT COUNT(*) FROM conversations WHERE status != 'deleted'")
        assert tier1_count_after == 20
        
        # Verify patterns extracted to Tier 2
        tier2_patterns = db.query("SELECT * FROM patterns WHERE source_conversations LIKE ?", (f'%{conv1.id}%',))
        assert len(tier2_patterns) > 0  # At least one pattern extracted
    
    def test_conversation_entities_fed_to_tier2(self):
        """Verify entities from Tier 1 create Tier 2 patterns."""
        conversation = create_test_conversation_with_entities(
            entities=[
                {'type': 'file', 'value': 'Service.cs'},
                {'type': 'intent', 'value': 'PLAN'},
                {'type': 'agent', 'value': 'work-planner'}
            ]
        )
        
        consolidate_conversation_to_tier2(conversation.id)
        
        # Check architectural pattern created
        arch_pattern = db.query_one("""
            SELECT * FROM architectural_patterns
            WHERE metadata LIKE '%Service.cs%'
        """)
        assert arch_pattern is not None

class TestTier2ToTier3Integration:
    """Test Tier 2 → Tier 3 data flow."""
    
    def test_tier2_patterns_enrich_tier3_metrics(self):
        """Verify Tier 2 file relationships inform Tier 3 hotspot detection."""
        # Create Tier 2 file relationships
        create_test_file_relationship("FileA.cs", "FileB.cs", confidence=0.85, co_occurrence=10)
        
        # Enrich Tier 3
        enrich_tier3_metrics_with_tier2_patterns()
        
        # Verify Tier 3 has correlation data
        tier3_correlation = tier3.get_file_correlation("FileA.cs", "FileB.cs")
        assert tier3_correlation is not None
        assert tier3_correlation.confidence >= 0.85
        assert tier3_correlation.source == 'tier2_learning'
    
    def test_tier3_validates_tier2_estimates(self):
        """Verify Tier 3 git data adjusts Tier 2 workflow estimates."""
        # Create workflow with estimate
        workflow_id = create_test_workflow(
            name="export_feature",
            steps=[
                {'step_type': 'plan', 'estimated_duration_seconds': 300},
                {'step_type': 'test_create', 'estimated_duration_seconds': 600},
                {'step_type': 'implement', 'estimated_duration_seconds': 900}
            ]
        )
        
        # Mock Tier 3 actual times (slower than estimate)
        tier3.mock_feature_completion_times("export_feature", [2400, 2600, 2200])  # Avg 2400s vs 1800s estimate
        
        # Run validation
        validate_workflow_estimates_from_git()
        
        # Verify estimates updated
        updated_steps = db.query("""
            SELECT * FROM workflow_steps
            WHERE pattern_id = ?
            ORDER BY step_number
        """, (workflow_id,))
        
        total_updated = sum(s.estimated_duration_seconds for s in updated_steps)
        assert total_updated > 1800  # Should be closer to actual 2400s
```

---

## 📚 Reference Queries (Cookbook)

### Query: "What's the best workflow for this task?"

```sql
-- Find most successful workflow patterns for task type
SELECT 
    p.id,
    p.name,
    p.description,
    p.confidence,
    (CAST(p.success_count AS REAL) / p.usage_count) as success_rate,
    p.usage_count,
    COUNT(ws.id) as step_count
FROM patterns p
LEFT JOIN workflow_steps ws ON p.id = ws.pattern_id
WHERE p.pattern_type = 'workflow'
  AND p.confidence >= 0.7
  AND (p.tags LIKE '%export%' OR p.name LIKE '%export%')  -- Task type
GROUP BY p.id
ORDER BY success_rate DESC, p.confidence DESC, p.usage_count DESC
LIMIT 3;
```

### Query: "What files should I check when modifying X?"

```sql
-- Find all files related to target file
SELECT 
    CASE 
        WHEN fr.file_a = 'TargetFile.cs' THEN fr.file_b
        ELSE fr.file_a
    END as related_file,
    fr.relationship_type,
    fr.confidence,
    fr.co_occurrence_count as times_seen,
    datetime(fr.last_observed) as last_seen
FROM file_relationships fr
WHERE (fr.file_a = 'TargetFile.cs' OR fr.file_b = 'TargetFile.cs')
  AND fr.confidence >= 0.6
ORDER BY fr.confidence DESC, fr.co_occurrence_count DESC;
```

### Query: "Has Copilot made this mistake before?"

```sql
-- Find past corrections for similar context
SELECT 
    ch.error_type,
    ch.original_action as what_copilot_tried,
    ch.correction_action as what_was_needed,
    ch.occurrence_count as times_repeated,
    datetime(ch.last_occurred) as last_time
FROM correction_history ch
WHERE ch.file_context LIKE '%CurrentFile.cs%'
   OR ch.error_type = 'wrong_file'
ORDER BY ch.occurrence_count DESC, ch.last_occurred DESC
LIMIT 5;
```

### Query: "What's the naming convention for this component type?"

```sql
-- Get architectural guidance for component
SELECT 
    ap.naming_convention,
    ap.location_pattern,
    ap.template_structure,
    ap.dependencies_pattern,
    ap.example_count as examples_found,
    ap.confidence
FROM architectural_patterns ap
WHERE ap.component_type = 'blazor_component'
  AND ap.confidence >= 0.7
ORDER BY ap.example_count DESC, ap.confidence DESC
LIMIT 1;
```

---

## 🎯 Success Metrics

### Pattern Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Average pattern confidence | >0.75 | `SELECT AVG(confidence) FROM patterns` |
| High-confidence patterns (≥0.8) | >60% | `SELECT COUNT(*) WHERE confidence >= 0.8 / COUNT(*)` |
| Pattern success rate | >80% | `SELECT AVG(success_count / usage_count)` |
| Active patterns (used in 30d) | >50% | `SELECT COUNT(*) WHERE last_used > datetime('now', '-30 days')` |

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Pattern query time | <100ms | Time to execute find_similar_workflow |
| File relationship lookup | <50ms | Time to get_related_files |
| Intent detection | <30ms | Time to match intent pattern |
| Consolidation time | <500ms | Time to consolidate_conversation_to_tier2 |

### Learning Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Patterns extracted per conversation | 3-7 | Average patterns created per consolidation |
| Pattern reuse rate | >40% | % of queries that find matching pattern |
| Confidence improvement rate | +5-10%/month | Track confidence trend over time |
| Stale pattern rate | <10% | % of patterns unused for 90+ days |

---

## 📖 Related Documentation

- [Architecture Overview](overview.md)
- [Tier 0: Governance](tier0-governance.md)
- [Tier 1: STM Design](tier1-stm-design.md)
- [Tier 3: Development Context](tier3-development-context.md)
- [Storage Schema](storage-schema.md)

---

**Status:** ✅ Tier 2 LTM Design Complete  
**Next:** Create Tier 3 Development Context design  
**Version:** 1.0 (Initial design)
