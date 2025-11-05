# Phase Plan Storage Analysis

**Date:** 2025-11-05  
**Question:** Should CORTEX phase plans be stored in SQLite or remain as Markdown files?  
**Decision:** 📋 **Markdown files (current approach) - RECOMMENDED**

---

## 🎯 Executive Summary

**Recommendation:** Keep phase plans as **Markdown files** in `cortex-design/phase-plans/`

**Rationale:**
- Phase plans are **design documentation**, not operational data
- They are **human-edited** frequently during planning
- They require **version control** (git) for collaboration
- They are **read-once** artifacts (during implementation)
- SQLite offers **no performance benefit** for this use case

**When to use SQLite:** Operational runtime data (rules, conversations, patterns, metrics)  
**When to use Markdown:** Design documentation, plans, specifications

---

## 📊 Detailed Analysis

### Data Characteristics Comparison

| Characteristic | Phase Plans | Governance Rules (SQLite) | Conversations (SQLite) |
|---|---|---|---|
| **Frequency of writes** | Rarely (during planning) | Once (migration) | Frequently (every interaction) |
| **Frequency of reads** | Once per phase | Many (every validation) | Many (context resolution) |
| **Human editing** | ✅ Constant (design iteration) | ❌ Never (programmatic only) | ❌ Never (programmatic only) |
| **Version control** | ✅ Critical (design decisions) | 🟡 Nice-to-have (audit) | ❌ Not needed (transient) |
| **Query complexity** | Simple (read by phase #) | Complex (by category, severity) | Complex (by entity, intent) |
| **Performance critical** | ❌ No (read once) | ✅ Yes (<1ms lookups) | ✅ Yes (<50ms queries) |
| **Data volume** | Small (6 files, ~30KB) | Small (28 rules, ~40KB) | Medium (50 conversations, ~100KB) |
| **Collaboration** | ✅ High (design reviews) | ❌ Low (stable rules) | ❌ None (single-user) |

### Storage Technology Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE DECISION TREE                      │
└─────────────────────────────────────────────────────────────┘

Is data human-edited frequently?
    ├─ YES → Is version control critical?
    │          ├─ YES → Is it design documentation?
    │          │          ├─ YES → 📋 MARKDOWN (Phase Plans, Design Docs)
    │          │          └─ NO  → Consider YAML/JSON in git
    │          └─ NO  → Consider database with audit log
    └─ NO  → Is query performance critical?
               ├─ YES → Is query complexity high?
               │          ├─ YES → 🗄️ SQLITE (Rules, Conversations, Patterns)
               │          └─ NO  → Consider JSON files
               └─ NO  → Is it operational data?
                          ├─ YES → 🗄️ SQLITE (Metrics, Events)
                          └─ NO  → 📋 MARKDOWN (Docs, Specs)
```

---

## 🔍 Use Case Analysis

### Phase Plans as Markdown Files ✅ RECOMMENDED

**Strengths:**
1. **Human-Readable Design Docs**
   - Easy to read in GitHub/VS Code
   - Side-by-side comparison during reviews
   - Searchable across all plans
   - Diff-friendly for design iterations

2. **Git Integration**
   - Every design change tracked with commit
   - Branch-based plan variations
   - PR review workflow for plan changes
   - Revert design decisions easily

3. **Collaboration**
   - Multiple people can review/comment
   - GitHub discussions on specific sections
   - Merge conflicts handled naturally
   - Design decisions documented in commits

4. **Tooling Support**
   - Markdown preview in editors
   - Documentation generators (Docusaurus, MkDocs)
   - Export to PDF/HTML for presentations
   - Copy/paste for documentation

5. **Simplicity**
   - No migration complexity
   - No schema evolution
   - No database maintenance
   - Direct file access

**Weaknesses:**
1. No structured queries ("Which phases are complete?")
2. No programmatic status tracking
3. Must parse markdown for automation
4. No relational links between phases

**When This Works:**
- ✅ Planning and design phase (NOW)
- ✅ Documentation artifacts
- ✅ Design reviews and iterations
- ✅ Knowledge transfer to team

---

### Phase Plans in SQLite ❌ NOT RECOMMENDED

**Strengths:**
1. **Structured Queries**
   ```sql
   -- Get all incomplete phases
   SELECT * FROM phase_plans WHERE status = 'not_started'
   
   -- Get phases by estimated duration
   SELECT * FROM phase_plans WHERE duration_hours > 10
   
   -- Track plan evolution
   SELECT version, updated_at FROM phase_plan_history
   ```

2. **Programmatic Access**
   - Agents can query plan status
   - Automated progress tracking
   - Cross-phase dependency checks
   - Analytics on plan accuracy

3. **Relational Structure**
   - Link phases to tasks
   - Track task completion
   - Rollup metrics (% complete)
   - Dependency graphs

**Weaknesses:**
1. **Poor Human Editing**
   - Edit via SQL or admin UI (cumbersome)
   - No markdown formatting
   - Lose design narrative
   - Difficult to review changes

2. **No Version Control**
   - Database changes not in git diffs
   - Design iterations not visible
   - Can't revert easily
   - Collaboration harder

3. **Premature Optimization**
   - Plans read once per phase (no perf benefit)
   - Query complexity not needed
   - Database overhead for 6 files
   - Migration complexity unjustified

4. **Design vs Runtime Separation**
   - Plans are **design artifacts**, not runtime data
   - Like storing architecture diagrams in DB
   - Conflates documentation with operation

**When This Might Work:**
- ❌ Real-time plan status dashboards (overkill)
- ❌ Complex plan queries (not needed)
- ❌ Automated plan generation (not the case)

---

## 🏗️ Hybrid Approach (CONSIDERED BUT REJECTED)

### Option: Markdown Source + SQLite Cache

**Idea:**
- Keep phase plans in Markdown (source of truth)
- Parse into SQLite for queries (derived data)
- Update cache when markdown changes

**Example:**
```python
# Parse markdown → SQLite
def sync_plan_to_database(plan_file: str):
    plan = parse_markdown(plan_file)
    db.upsert_plan(
        phase_number=plan.phase_number,
        name=plan.name,
        duration=plan.duration,
        tasks=plan.tasks
    )
```

**Why Rejected:**
1. **Complexity:** Maintain parser + sync logic
2. **Sync Issues:** Markdown and DB can drift
3. **No Real Benefit:** Plans queried rarely
4. **Premature:** No proven need for structured queries

**When to Reconsider:**
- If building plan analytics dashboard
- If generating plans programmatically
- If tracking plan accuracy over time
- If complex cross-phase queries needed

---

## 📋 What SHOULD Be in SQLite (for reference)

### Operational Runtime Data ✅

**1. Governance Rules (Tier 0)**
- ✅ Programmatically queried (<1ms)
- ✅ Indexed by category/severity
- ✅ Immutable after migration
- ✅ Relational requirements

**2. Conversations (Tier 1)**
- ✅ FIFO queue management (delete oldest)
- ✅ Entity extraction queries
- ✅ Fast context resolution
- ✅ Cross-conversation search

**3. Knowledge Patterns (Tier 2)**
- ✅ Pattern matching queries (FTS5)
- ✅ Confidence decay updates
- ✅ Relationship graphs
- ✅ High read frequency

**4. Development Metrics (Tier 3)**
- ✅ Time-series queries
- ✅ Correlation analysis
- ✅ Hotspot detection
- ✅ Trend calculations

### Design Documentation ✅ Markdown

**1. Phase Plans**
- 📋 Human-edited during design
- 📋 Version controlled in git
- 📋 Read once per phase
- 📋 Narrative structure important

**2. Architecture Docs**
- 📋 CORTEX-DNA.md (vision)
- 📋 WHY-CORTEX-IS-BETTER.md (rationale)
- 📋 STORAGE-DESIGN-ANALYSIS.md (decisions)
- 📋 HOLISTIC-REVIEW-PROTOCOL.md (process)

**3. Reviews**
- 📋 phase-0-review.md (audit trail)
- 📋 phase-1-review.md (learnings)
- 📋 Git commits (decision context)

---

## 🎯 Decision Summary

### Recommendation: Markdown Files

**Store phase plans in:** `cortex-design/phase-plans/phase-{N}-{name}.md`

**Rationale:**
1. ✅ **Design Artifact:** Plans are documentation, not runtime data
2. ✅ **Human-Edited:** Constant iteration during planning
3. ✅ **Version Control:** Design decisions tracked in git
4. ✅ **Collaboration:** PR reviews, comments, discussions
5. ✅ **Simplicity:** No migration, no schema, no sync
6. ✅ **Tooling:** Markdown preview, export, search
7. ✅ **No Performance Need:** Read once per phase

### When to Migrate to SQLite

**Trigger conditions:**
1. **Plan Analytics Needed:** "Which phases took longest?"
2. **Automated Plan Generation:** Plans created by CORTEX, not humans
3. **Real-Time Dashboards:** Live plan status tracking
4. **Complex Queries:** Cross-phase dependency analysis

**None of these conditions exist currently.**

---

## 📝 Implementation Guidelines

### Phase Plan File Organization

**Current (CORRECT):**
```
cortex-design/
├── phase-plans/
│   ├── PHASE-PLAN-TEMPLATE.md
│   ├── phase-0-governance.md
│   ├── phase-1-working-memory.md
│   ├── phase-2-knowledge-graph.md
│   ├── phase-3-context-intelligence-updated.md
│   ├── phase-4-agents.md
│   ├── phase-5-entry-point.md
│   └── phase-6-migration-validation.md
├── reviews/
│   ├── phase-0-review.md
│   ├── phase-1-review.md
│   └── ...
└── architecture/
    ├── unified-database-schema.sql  ← SQLite schema for runtime data
    └── STORAGE-DESIGN-ANALYSIS.md   ← This decision documented
```

### Metadata Extraction (If Needed Later)

If plan analytics become necessary, extract metadata to SQLite **without migrating content**:

```sql
-- Minimal metadata cache (not full content)
CREATE TABLE phase_plan_metadata (
    phase_number INTEGER PRIMARY KEY,
    name TEXT,
    duration_hours_estimate TEXT,
    duration_hours_actual REAL,
    status TEXT CHECK(status IN ('not_started', 'in_progress', 'review', 'complete')),
    file_path TEXT,  -- Reference to markdown source
    last_updated TIMESTAMP
);
```

**Key:** Markdown remains source of truth, database is cache.

---

## ✅ Final Answer

**Question:** Should phase plans be stored in SQLite?

**Answer:** **NO** - Keep them as Markdown files

**Why:**
- Phase plans are **design documentation**, not operational data
- They require **human editing** and **version control**
- They are **read once** during implementation (no performance need)
- SQLite offers **no benefit** and adds **unnecessary complexity**

**What goes in SQLite:**
- Governance rules (runtime validation)
- Conversations (context resolution)
- Knowledge patterns (pattern matching)
- Development metrics (analytics)

**What stays in Markdown:**
- Phase plans (design docs)
- Architecture docs (rationale)
- Reviews (audit trail)
- Specifications (human-readable)

---

**Decision Date:** 2025-11-05  
**Confidence:** 0.98 (very high - clear separation of concerns)  
**Review Date:** After Phase 4 (if plan analytics become needed)

