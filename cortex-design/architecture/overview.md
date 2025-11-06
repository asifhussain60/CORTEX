# CORTEX Architecture Overview

**Version:** 2.0  
**Date:** 2025-11-06  
**Status:** 🏗️ DESIGN SPECIFICATION (Updated with complete tier designs)  
**Purpose:** High-level system architecture and component integration

---

## 🎯 System Vision

**CORTEX** (Cerebral Orchestration and Runtime Task EXecution) is a cognitive development assistant that combines:
- 🧠 **Dual-hemisphere brain architecture** (strategic planning + tactical execution)
- 💾 **4-tier memory system** (instinct, working memory, knowledge, context)
- 🤖 **10 specialist agents** (focused, single-responsibility)
- ⚡ **Performance-first design** (SQLite, indexed queries, delta updates)
- 🧪 **Test-driven methodology** (95%+ coverage, permanent regression suite)

**Core Differentiator:** CORTEX learns from every interaction, provides proactive warnings, and gets smarter over time—all while being 50-75% faster than KDS v8.

---

## �️ Four-Tier BRAIN Architecture

### Tier 0: Instinct (Governance)

**Purpose:** Immutable core values and rules that define CORTEX's behavior

**Storage:** `governance/rules/` (Markdown + YAML)  
**Size:** <50 KB (22 rules)  
**Mutability:** PERMANENT (cannot be changed by user or system)

**Contents:**
- 22 core governance rules (TDD, DoR/DoD, architectural thinking, etc.)
- Agent behavior protocols
- Hemisphere coordination rules
- Tool requirements and setup protocols
- Tier classification rules
- Amnesia recovery procedures

**Examples:**
- **Rule #5:** Test-Driven Development (RED → GREEN → REFACTOR)
- **Rule #8:** Definition of READY (requirements before work)
- **Rule #15:** Definition of DONE (zero errors/warnings)
- **Rule #22:** Brain Protection System (challenge risky changes)

**Access Pattern:** Read-only, loaded at startup, referenced by all agents

**See:** [Tier 0: Governance Design](tier0-governance.md)

---

### Tier 1: Short-Term Memory (Working Memory)

**Purpose:** Recent conversation history for context continuity

**Storage:** SQLite (`cortex-brain.db` - `conversations`, `messages`, `conversation_entities`)  
**Size:** <100 KB (last 20 conversations)  
**Performance:** <50ms for conversation queries

**Key Features:**
- **FIFO queue:** Last 20 conversations (oldest deleted when #21 arrives)
- **Entity extraction:** Files, intents, agents, components automatically tagged
- **Context resolution:** "Make it purple" knows what "it" refers to
- **Boundary detection:** Auto-detects when conversations end
- **Active protection:** Current conversation never deleted (even if oldest)

**Data Flow:**
```
User message → Conversation created/continued
              ↓
Entity extraction (files mentioned, intent detected)
              ↓
Message stored with metadata
              ↓
When conversation #21 starts → Conversation #1 marked for deletion
              ↓
Before deletion → Patterns extracted → Moved to Tier 2
              ↓
Conversation #1 deleted (space reclaimed)
```

**Query Examples:**
- "What files did we discuss in the last conversation?"
- "Show me all conversations about testing"
- "What was the outcome of the dark mode feature?"

**See:** [Tier 1: Short-Term Memory Design](tier1-stm-design.md)

---

### Tier 2: Long-Term Memory (Knowledge Graph)

**Purpose:** Consolidated patterns and learned wisdom (permanent)

**Storage:** SQLite (`cortex-brain.db` - `patterns`, `workflow_steps`, `file_relationships`, etc.)  
**Size:** <10 MB (grows over time, optimized)  
**Performance:** <100ms for pattern queries

**Key Features:**
- **Pattern consolidation:** Successful workflows extracted from deleted Tier 1 conversations
- **Confidence scoring:** Patterns weighted by success rate (0.0-1.0)
- **Pattern decay:** Unused patterns (>90 days) lose confidence
- **Multiple pattern types:** Workflows, intents, file relationships, architectural, validation, corrections, tests, naming

**Pattern Types:**

1. **Workflow Patterns** - Multi-step processes
   ```yaml
   export_feature_workflow:
     steps: [plan, test_create, implement, validate, commit]
     confidence: 0.92
     usage_count: 14
     success_rate: 0.96
   ```

2. **Intent Patterns** - Natural language → intent mappings
   ```yaml
   "add a button" → PLAN (confidence: 0.95)
   "continue" → EXECUTE (confidence: 0.98)
   "test this" → TEST (confidence: 0.94)
   ```

3. **File Relationships** - Co-modification patterns
   ```yaml
   HostControlPanel.razor ↔ noor-canvas.css
   co_occurrence: 47 times (75% correlation)
   ```

4. **Architectural Patterns** - Component structure
   ```yaml
   blazor_component:
     location: Components/**/*.razor
     naming: PascalCase
     dependencies: [Razor, DI]
     confidence: 0.89
   ```

**Data Flow:**
```
Tier 1 conversation deleted (FIFO) → Pattern extraction
                                     ↓
Analyze conversation for successful workflows, file pairs, intents
                                     ↓
Create/update patterns in Tier 2 with confidence scores
                                     ↓
Next request → Query Tier 2 → High-confidence patterns → Smart suggestions
```

**See:** [Tier 2: Long-Term Memory Design](tier2-ltm-design.md)

---

### Tier 3: Development Context (Project Intelligence)

**Purpose:** Real-time project metrics and proactive warnings

**Storage:** SQLite (`cortex-brain.db` - `context_git_metrics`, `context_file_hotspots`, etc.)  
**Size:** <50 KB (30-day rolling window)  
**Performance:** <10ms for context queries

**Key Features:**
- **Delta collection:** Only process new commits since last collection (3s vs 2-5 min)
- **1-hour throttling:** Balances freshness with performance
- **Time-series analysis:** Trends, forecasts, correlations
- **Proactive insights:** Velocity drops, file hotspots, flaky tests, build health

**Metrics Tracked:**

1. **Git Activity**
   - Commit velocity (per day/week)
   - Lines added/deleted/net
   - File hotspots (high churn rate)
   - Contributor patterns

2. **Code Health**
   - File stability classification (stable/moderate/unstable)
   - Test coverage trends
   - Build success rates

3. **Testing Activity**
   - Test discovery by type (UI, unit, integration)
   - Pass/fail rates
   - Flaky test detection (>10% failure rate)

4. **CORTEX Usage**
   - Session patterns by time of day
   - Intent distribution (PLAN, EXECUTE, TEST, etc.)
   - Workflow success rates (TDD vs non-TDD)
   - Session duration analysis

5. **Work Patterns**
   - Productive time slots (10am-12pm: 94% success)
   - Session duration sweet spots (30-60 min optimal)
   - Focus duration correlation with quality

6. **Correlations**
   - Commit size vs success rate (r = -0.72, smaller is better)
   - Test-first vs rework rate (r = -0.85, TDD reduces rework)
   - CORTEX usage vs velocity (r = 0.79, usage increases productivity)

**Proactive Warnings:**
```
⚠️ Velocity dropped 35% this week (baseline: 42 commits/week, current: 27)
💡 Consider smaller commits, more frequent tests

⚠️ HostControlPanel.razor is a hotspot (28% churn, unstable)
💡 Add extra testing - file frequently modified

⚠️ fab-button.spec.ts fails 15% of the time (flaky test)
💡 Investigate and stabilize (add waits, fix race conditions)
```

**See:** [Tier 3: Development Context Design](tier3-context-design.md)

---

## 🧠 Hemisphere Architecture

### RIGHT BRAIN (Strategic Planning)

**Role:** Analyze, plan, protect

**Agents:**
- `intent-router.md` - Classify requests
- `work-planner.md` - Create strategic plans
- `brain-protector.md` - Guard integrity
- `readiness-validator.md` - Enforce Definition of Ready

**Data Access:**
```
Tier 0: Read governance rules
Tier 1: Read recent conversations (context)
Tier 2: Search patterns (intelligence)
Tier 3: Query metrics (data-driven planning)
```

**Output:** Work packages for LEFT BRAIN

---

### LEFT BRAIN (Tactical Execution)

**Role:** Execute, test, validate

**Agents:**
- `test-generator.md` - Create tests (TDD)
- `code-executor.md` - Implement code
- `health-validator.md` - Validate completion
- `commit-handler.md` - Semantic commits

**Data Access:**
```
Tier 0: Read Definition of Done
Tier 1: Write conversation messages
Tier 2: (via RIGHT BRAIN queries)
```

**Output:** Completed, validated work

---

## 🔄 Data Flow

### Request Processing Flow

```
User Request
    ↓
[RIGHT BRAIN: Intent Router]
    ↓ (queries Tier 2 patterns)
[RIGHT BRAIN: Work Planner]
    ↓ (checks Tier 0 DoR)
[RIGHT BRAIN: Readiness Validator]
    ↓ (creates work package)
────────────────────────────────
[LEFT BRAIN: Test Generator]
    ↓ (TDD: RED)
[LEFT BRAIN: Code Executor]
    ↓ (TDD: GREEN)
[LEFT BRAIN: Code Executor]
    ↓ (TDD: REFACTOR)
[LEFT BRAIN: Health Validator]
    ↓ (checks Tier 0 DoD)
[LEFT BRAIN: Commit Handler]
    ↓
Completed Work
```

### Learning Flow

```
Conversation Messages (Tier 1)
    ↓ (50+ messages OR 24h)
[Brain Updater]
    ↓ (pattern extraction)
Patterns (Tier 2)
    ↓ (usage tracking)
Confidence Updates
    ↓ (decay algorithm)
Pattern Pruning (<0.30)
```

### Context Collection Flow

```
Git Repository
    ↓ (every 5 min, delta only)
[Context Collector]
    ↓
Git Activity JSON (Tier 3)
    ↓
Work Patterns Analysis
    ↓
Proactive Warnings
```

---

## 🗄️ SQLite Database Schema

### Single Database: `cortex-brain.db`

**Tables:**
```sql
-- TIER 0: Governance
governance_rules (22 rows, static)
governance_rule_examples
governance_rule_violations

-- TIER 1: Short-Term Memory
conversations (max 20 rows, FIFO)
messages (linked to conversations)
conversation_entities (extracted data)
conversation_files (file references)

-- TIER 2: Long-Term Knowledge
patterns (grows over time)
patterns_fts (FTS5 virtual table)
components (code components)
component_relationships
workflows
error_corrections

-- TIER 3: (Uses JSON file, not SQLite)
```

**Indexes:**
```sql
-- Tier 1 indexes
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence);
CREATE INDEX idx_entities_conversation ON conversation_entities(conversation_id);

-- Tier 2 indexes
CREATE INDEX idx_patterns_confidence ON patterns(confidence DESC);
CREATE INDEX idx_patterns_category ON patterns(category);
CREATE INDEX idx_patterns_last_used ON patterns(last_used DESC);
CREATE INDEX idx_relationships_components ON component_relationships(component_a, component_b);
```

---

## 🚀 Performance Targets

### Query Performance

| Query Type | Target | Measurement |
|------------|--------|-------------|
| Tier 0: Rule lookup | <1ms | Direct primary key |
| Tier 1: Conversation load | <50ms | With messages + entities |
| Tier 1: Entity search | <30ms | Indexed search |
| Tier 2: Pattern search (FTS5) | <100ms | Full-text search |
| Tier 2: Pattern retrieval | <50ms | By confidence/category |
| Tier 3: Context load | <200ms | JSON parse + cache |

### Storage Performance

| Metric | Target | Current (KDS v8) | Improvement |
|--------|--------|------------------|-------------|
| Total storage | <270 KB | 1.2 MB | **4.4x smaller** |
| Tier 0 | <20 KB | N/A | New |
| Tier 1 | <100 KB | ~400 KB | **4x smaller** |
| Tier 2 | <120 KB | ~700 KB | **5.8x smaller** |
| Tier 3 | <50 KB | ~100 KB | **2x smaller** |

### Learning Performance

| Operation | Target | Current (KDS v8) |
|-----------|--------|------------------|
| Pattern extraction | <2 min | ~5-7 min |
| FTS5 index rebuild | <500ms | N/A |
| Confidence calculation | <100ms | ~300ms |
| FIFO rotation | <50ms | ~200ms |

---

## 🔐 Cross-Tier Access Rules

### Access Matrix

| Tier | Can Read From | Can Write To | Rationale |
|------|---------------|--------------|-----------|
| **Tier 0** | (Self only) | (Immutable) | Governance rules never change |
| **Tier 1** | Tier 0 | Tier 1 | STM records conversations |
| **Tier 2** | Tier 0, 1 | Tier 2 | LTM learns from STM |
| **Tier 3** | (External) | Tier 3 | Metrics from git/tests |

### Agent Access Rules

| Agent | Hemisphere | Reads | Writes |
|-------|------------|-------|--------|
| intent-router | RIGHT | T0, T2 | - |
| work-planner | RIGHT | T0, T1, T2, T3 | - |
| brain-protector | RIGHT | T0, T2 | - |
| readiness-validator | RIGHT | T0 | - |
| test-generator | LEFT | T0 | T1 (messages) |
| code-executor | LEFT | T0 | T1 (messages) |
| health-validator | LEFT | T0 | T1 (messages) |
| commit-handler | LEFT | T0 | T1 (messages) |
| brain-updater | BOTH | T1 | T2 |
| context-collector | BOTH | (Git) | T3 |

---

## 📦 File Structure

```
CORTEX/
├── cortex-brain.db              # Single SQLite database (Tier 0, 1, 2)
├── tier3-context.json           # Development metrics (Tier 3)
├── src/
│   ├── tier0/                   # Governance rules
│   │   ├── governance.py
│   │   └── rules_loader.py
│   ├── tier1/                   # Short-term memory
│   │   ├── conversations.py
│   │   ├── entities.py
│   │   └── fifo.py
│   ├── tier2/                   # Long-term knowledge
│   │   ├── patterns.py
│   │   ├── fts_search.py
│   │   └── confidence.py
│   ├── tier3/                   # Development context
│   │   ├── git_collector.py
│   │   ├── metrics.py
│   │   └── cache.py
│   ├── agents/
│   │   ├── right_brain/         # Strategic agents
│   │   └── left_brain/          # Tactical agents
│   └── shared/
│       ├── db_connection.py
│       └── query_executor.py
└── tests/
    ├── tier0/                   # 15 tests
    ├── tier1/                   # 58 tests
    ├── tier2/                   # 79 tests
    ├── tier3/                   # 44 tests
    ├── agents/                  # 125 tests
    └── integration/             # 49 tests
```

---

## 🔄 Migration from KDS v8

### Data Migration Path

```
KDS v8 (YAML/JSONL)              CORTEX (SQLite/JSON)
─────────────────────            ────────────────────

governance/rules.md        →     cortex-brain.db (Tier 0)
conversation-history.jsonl →     cortex-brain.db (Tier 1)
knowledge-graph.yaml       →     cortex-brain.db (Tier 2)
development-context.yaml   →     tier3-context.json
```

### Migration Tools

```python
# scripts/migrate-tier1.py
# Converts conversation-history.jsonl → SQLite Tier 1

# scripts/migrate-tier2.py
# Converts knowledge-graph.yaml → SQLite Tier 2

# scripts/validate-migration.py
# Compares KDS vs CORTEX query results
```

---

## ✅ Quality Gates

### Definition of Ready (RIGHT BRAIN)

**Before work begins:**
- ✅ Requirements clear
- ✅ Acceptance criteria defined
- ✅ Test scenarios outlined
- ✅ Dependencies identified
- ✅ Scope broken down (<4h tasks)

**Storage:** Tier 0 (governance rules)

### Definition of Done (LEFT BRAIN)

**Before work completes:**
- ✅ Build succeeds (0 errors, 0 warnings)
- ✅ All tests passing
- ✅ TDD workflow followed (RED → GREEN → REFACTOR)
- ✅ Health validation passed
- ✅ Semantic commit created

**Storage:** Tier 0 (governance rules)

---

## 🧪 Testing Strategy

### Test Distribution

| Tier/Component | Test Count | Coverage Target |
|----------------|------------|-----------------|
| Tier 0 | 15 | 100% |
| Tier 1 | 58 | 95% |
| Tier 2 | 79 | 95% |
| Tier 3 | 44 | 90% |
| Agents | 125 | 95% |
| Integration | 49 | 90% |
| **Total** | **370** | **95%+** |

### Test Types

**Unit Tests:**
- Tier implementations
- Agent logic
- Query functions
- Utility functions

**Integration Tests:**
- Cross-tier queries
- Agent workflows
- BRAIN learning cycle
- Data migration

**Performance Tests:**
- Query latency benchmarks
- Storage size validation
- Learning cycle timing
- FIFO rotation speed

---

## 📊 Monitoring & Observability

### Health Metrics

```python
# Brain health check
{
  "tier0": {
    "rules_loaded": 22,
    "rule_lookup_avg_ms": 0.5
  },
  "tier1": {
    "conversations_count": 18,  # out of 20 max
    "oldest_conversation_age_days": 45,
    "entity_extraction_success_rate": 0.96
  },
  "tier2": {
    "patterns_count": 3247,
    "avg_confidence": 0.82,
    "fts_search_avg_ms": 45,
    "patterns_decayed_last_week": 12
  },
  "tier3": {
    "last_collection_ago_min": 3,
    "git_commits_analyzed": 1249,
    "cache_hit_rate": 0.91
  }
}
```

### Performance Monitoring

```python
# Query performance tracking
{
  "query_type": "tier2_pattern_search",
  "avg_latency_ms": 42,
  "p95_latency_ms": 87,
  "p99_latency_ms": 145,
  "queries_last_hour": 234
}
```

---

## 🚀 Deployment Architecture

### Local Development

```
Developer Machine
├── CORTEX/src/           (Python source)
├── cortex-brain.db       (SQLite)
├── tier3-context.json    (Metrics)
└── pytest                (Run tests)
```

### Production (User Machine)

```
User's KDS Directory
├── CORTEX/
│   ├── cortex-brain.db   (Brain storage)
│   └── tier3-context.json
├── prompts/              (Agent prompts)
└── dashboard/            (React dashboard, optional)
```

**No servers, no APIs, no external dependencies**

---

## 🔧 Extension Points

### Adding New Tiers (Future)

```python
# Tier 4 example: Team Collaboration (future)
class Tier4TeamKnowledge:
    """
    Shared knowledge across team members.
    Storage: SQLite (team-brain.db)
    """
    def share_pattern(self, pattern_id: str, team_id: str):
        # Sync pattern to team database
        pass
```

### Adding New Agents

```python
# New agent: Performance Optimizer
class PerformanceOptimizer:
    """
    RIGHT BRAIN agent that suggests optimizations.
    Queries: Tier 2 (slow patterns), Tier 3 (code metrics)
    """
    def suggest_optimizations(self):
        # Analyze patterns + metrics
        # Return optimization suggestions
        pass
```

---

## 📚 Related Documents

- [Tier 0: Governance Design](tier0-governance.md)
- [Tier 1: STM Design](tier1-stm-design.md)
- [Tier 2: LTM Design](tier2-ltm-design.md)
- [Tier 3: Context Design](tier3-context-design.md)
- [Storage Schema](storage-schema.md)
- [Performance Targets](performance-targets.md)
- [Dashboard Requirements](../dashboard-requirements.md)

---

**Status:** ✅ Architecture Overview Complete  
**Next:** Create detailed tier design documents  
**Version:** 1.0 (Initial design)

