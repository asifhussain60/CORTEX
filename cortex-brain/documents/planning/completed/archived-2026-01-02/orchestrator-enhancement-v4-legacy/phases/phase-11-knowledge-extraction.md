# Phase 11: Knowledge Extraction

**[← Back to Master Plan](../00-MASTER-PLAN.md)** | **[Previous: REFACTOR](phase-10-refactor.md)** | **[Next: Documentation Update →](phase-12-documentation-update.md)**

---

## 📋 Phase Overview

| Attribute | Value |
|-----------|-------|
| **Phase ID** | 11 |
| **Name** | Knowledge Extraction |
| **Status** | ⏸️ Not Started |
| **Duration** | ~1 day |
| **Tasks Complete** | 0/12 (0%) |
| **Dependencies** | Phase 10 (REFACTOR complete) |

---

## 🎯 Objective

**Extract knowledge** from completed implementation and **update brain tiers** with:
- New patterns discovered during implementation
- Module relationships and dependencies
- Lessons learned (what worked / what didn't)
- Obsolete patterns that should be replaced

**Key Innovation:** This phase transforms implementation artifacts into **reusable knowledge** for future projects.

---

## 📊 Progress Tracker

**Phase Progress:** `░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Task ID | Task | Status | Duration |
|---------|------|--------|----------|
| 11.1 | Aggregate patterns from all phases | ⏸️ Not Started | 2h |
| 11.2 | Extract MCP tool invocation patterns | ⏸️ Not Started | 1h |
| 11.3 | Extract orchestrator self-validation patterns | ⏸️ Not Started | 1h |
| 11.4 | Extract continuous KL integration patterns | ⏸️ Not Started | 1h |
| 11.5 | Extract progress rendering patterns | ⏸️ Not Started | 1h |
| 11.6 | Extract hierarchical plan structure patterns | ⏸️ Not Started | 1h |
| 11.7 | Update Tier 2 knowledge graph | ⏸️ Not Started | 2h |
| 11.8 | Update Tier 3 development context | ⏸️ Not Started | 2h |
| 11.9 | Update lessons-learned.yaml | ⏸️ Not Started | 1h |
| 11.10 | Detect and replace obsolete patterns | ⏸️ Not Started | 2h |
| 11.11 | Validate bidirectional links | ⏸️ Not Started | 1h |
| 11.12 | Generate knowledge extraction report | ⏸️ Not Started | 1h |

**Total:** 16 hours (~1 day)

---

## 🧠 Brain Tier Update Strategy

### Tier 1 Updates (Conversation Context)
**File:** `cortex-brain/conversation-context.jsonl`

**Update Type:** Append

```jsonl
{
  "timestamp": "2026-01-02T16:45:00Z",
  "event": "plan_completed",
  "plan_id": "orchestrator-enhancement",
  "feature": "Planning System v5.0 - Robust Architecture",
  "status": "completed",
  "duration_days": 49,
  "compliance_score": 10.0,
  "patterns_extracted": 23,
  "modules_created": 12,
  "files_modified": 87
}
```

---

### Tier 2 Updates (Knowledge Graph)
**File:** `cortex-brain/knowledge-graph.yaml`

**Update Type:** Add nodes + edges, mark obsolete

```yaml
# NEW NODES

- id: mcp_tool_orchestrator_invocation_pattern
  type: pattern
  domain: integration
  description: "MCP tool pattern for guaranteed orchestrator execution"
  source: orchestrator-enhancement/phase-01
  created: "2026-01-02"
  confidence: high
  reusability: high
  examples:
    - src/mcp/tools/orchestrator_invocation.py
  related_patterns:
    - orchestrator_base_class_pattern
    - mcp_tool_decorator_pattern
  supersedes:
    - terminal_wrapper_pattern  # Obsolete

- id: continuous_knowledge_library_pattern
  type: pattern
  domain: knowledge-management
  description: "Query knowledge library at every phase, extract patterns back"
  source: orchestrator-enhancement/phase-03
  created: "2026-01-02"
  confidence: high
  reusability: high
  examples:
    - src/orchestrators/planning/knowledge_library_integration.py
  related_patterns:
    - brain_tier_update_pattern
    - pattern_extraction_pattern

- id: hierarchical_plan_structure_pattern
  type: pattern
  domain: planning
  description: "Master plan + phase sub-files with 2-way linking"
  source: orchestrator-enhancement/phase-06
  created: "2026-01-02"
  confidence: high
  reusability: high
  examples:
    - cortex-brain/documents/planning/active/orchestrator-enhancement/
  related_patterns:
    - bidirectional_linking_pattern
    - plan_navigation_pattern

# OBSOLETE NODES (marked deprecated)

- id: terminal_wrapper_pattern
  type: pattern
  domain: integration
  status: deprecated  # ← MARKED OBSOLETE
  deprecated_date: "2026-01-02"
  deprecated_reason: "Replaced by MCP tool pattern (more robust, type-safe)"
  replaced_by: mcp_tool_orchestrator_invocation_pattern
  migration_guide: cortex-brain/documents/migrations/terminal-wrapper-to-mcp-tool.md

- id: monolithic_plan_pattern
  type: pattern
  domain: planning
  status: deprecated  # ← MARKED OBSOLETE
  deprecated_date: "2026-01-02"
  deprecated_reason: "Replaced by hierarchical plan structure (better scalability)"
  replaced_by: hierarchical_plan_structure_pattern
  migration_guide: cortex-brain/documents/migrations/monolithic-to-hierarchical-plans.md
```

---

### Tier 3 Updates (Development Context)
**File:** `cortex-brain/development-context.yaml`

**Update Type:** Add modules, update relationships

```yaml
# NEW MODULES

modules:
  - name: src.mcp.tools.orchestrator_invocation
    type: mcp_tool
    purpose: "Guaranteed orchestrator execution bridge"
    created: "2026-01-02"
    maintainer: CORTEX Development Team
    dependencies:
      - src.orchestrators.base.base_orchestrator
      - src.orchestrators.planning.planning_orchestrator
    used_by:
      - .github.prompts.CORTEX  # Intent router
    test_coverage: 95%
    status: active

  - name: src.orchestrators.planning.knowledge_library_integration
    type: module
    purpose: "Continuous knowledge library queries and pattern extraction"
    created: "2026-01-02"
    dependencies:
      - cortex-brain/knowledge-library
      - src.brain.tier2.knowledge_graph_updater
      - src.brain.tier3.dev_context_updater
    test_coverage: 92%
    status: active

  - name: src.orchestrators.planning.hierarchical_plan_generator
    type: module
    purpose: "Generate master + phase sub-files with 2-way linking"
    created: "2026-01-02"
    dependencies:
      - src.orchestrators.planning.plan_generator
    test_coverage: 88%
    status: active

# OBSOLETE MODULES (marked deprecated)

  - name: src.utils.terminal_wrapper
    type: utility
    status: deprecated  # ← MARKED OBSOLETE
    deprecated_date: "2026-01-02"
    deprecated_reason: "Replaced by MCP tool pattern"
    replaced_by: src.mcp.tools.orchestrator_invocation
    migration_deadline: "2026-03-01"  # 2 months to migrate
```

**File:** `cortex-brain/file-relationships.yaml`

```yaml
# NEW RELATIONSHIPS

relationships:
  - file: .github/prompts/CORTEX.prompt.md
    imports:
      - src.mcp.tools.orchestrator_invocation  # NEW: via MCP tool call
    imported_by: []
    
  - file: src/orchestrators/planning/planning_orchestrator.py
    imports:
      - src.orchestrators.planning.knowledge_library_integration  # NEW
      - src.orchestrators.planning.hierarchical_plan_generator  # NEW
    imported_by:
      - src.mcp.tools.orchestrator_invocation
```

**File:** `cortex-brain/lessons-learned.yaml`

```yaml
# NEW LESSONS

lessons:
  - id: lesson_001_mcp_tool_invocation
    date: "2026-01-02"
    category: integration
    lesson: "MCP tools provide guaranteed execution vs. prompt interpretation"
    what_worked:
      - Type-safe parameters validated by MCP schema
      - Observable progress (structured return values)
      - Error handling built-in
    what_didnt_work:
      - Terminal wrappers: CORTEX can't parse output easily
      - Prompt directives: LLM interprets "STOP" ambiguously
    recommendation: "Use MCP tools for all orchestrator invocations"
    confidence: high
    reusability: high

  - id: lesson_002_continuous_knowledge_library
    date: "2026-01-02"
    category: knowledge-management
    lesson: "Knowledge library should be queried continuously, not just once"
    what_worked:
      - Querying at every phase provided phase-specific context
      - Extracting patterns after each phase built living knowledge base
      - Pattern reuse rate increased from 20% to 80%
    what_didnt_work:
      - One-time Phase -1 query: missed phase-specific patterns
    recommendation: "Query KL at every phase + extract patterns back"
    confidence: high
    reusability: high

  - id: lesson_003_hierarchical_plan_structure
    date: "2026-01-02"
    category: planning
    lesson: "Hierarchical plans (master + sub-files) scale better than monolithic"
    what_worked:
      - Phase files can be edited independently (no merge conflicts)
      - 2-way linking provides clear navigation
      - Parallel phase editing (multiple contributors)
    what_didnt_work:
      - Monolithic plans: merge conflicts, hard to navigate
    recommendation: "Use hierarchical structure for TIER 3-4 plans"
    confidence: high
    reusability: high
```

---

## 🔍 Pattern Extraction Workflow

### Task 11.1: Aggregate Patterns from All Phases

**Input:** Phase execution reports from Phase 0-10

**Process:**
```python
# Aggregate all patterns extracted during continuous KL integration
all_patterns = []
for phase in phases:
    phase_patterns = load_patterns(f"tracking/phase-{phase.num}-patterns.json")
    all_patterns.extend(phase_patterns)

# Deduplicate patterns (same pattern extracted multiple times)
unique_patterns = deduplicate_patterns(all_patterns)

# Categorize patterns by domain
categorized = {
    "integration": [p for p in unique_patterns if p.domain == "integration"],
    "planning": [p for p in unique_patterns if p.domain == "planning"],
    "visualization": [p for p in unique_patterns if p.domain == "visualization"],
    "knowledge-management": [p for p in unique_patterns if p.domain == "knowledge-management"],
    # ...
}
```

**Output:** `tracking/aggregated-patterns.json` (23 unique patterns)

---

### Task 11.7: Update Tier 2 Knowledge Graph

**Process:**
```python
# Load knowledge graph
kg = KnowledgeGraph.load("cortex-brain/knowledge-graph.yaml")

# Add new pattern nodes
for pattern in unique_patterns:
    node_id = kg.add_pattern_node(
        pattern=pattern,
        related_patterns=pattern.related_to
    )
    logger.info(f"✅ Added pattern node: {node_id}")

# Mark obsolete patterns
obsolete = [
    ("terminal_wrapper_pattern", "mcp_tool_orchestrator_invocation_pattern"),
    ("monolithic_plan_pattern", "hierarchical_plan_structure_pattern"),
]

for old_id, new_id in obsolete:
    kg.replace_obsolete_pattern(
        obsolete_pattern_id=old_id,
        new_pattern_id=new_id,
        reason="Replaced by more robust implementation"
    )
    logger.info(f"✅ Replaced obsolete pattern: {old_id} → {new_id}")

# Validate bidirectional links
validation = kg.validate_bidirectional_links()
if not validation.passed:
    raise ValueError(f"Orphaned references found: {validation.orphaned}")

# Save updated graph
kg.save("cortex-brain/knowledge-graph.yaml")
```

**Output:** Updated `knowledge-graph.yaml` with 23 new nodes, 2 deprecated nodes

---

### Task 11.10: Detect and Replace Obsolete Patterns

**Obsolete Pattern Detection:**
```python
# Compare old patterns with new patterns
obsolete_patterns = []

for old_pattern in existing_patterns:
    # Check if new pattern supersedes old pattern
    for new_pattern in unique_patterns:
        if new_pattern.supersedes == old_pattern.id:
            obsolete_patterns.append({
                "old": old_pattern,
                "new": new_pattern,
                "reason": new_pattern.supersedes_reason
            })

# Generate migration guide for each obsolete pattern
for obsolete in obsolete_patterns:
    migration_guide = generate_migration_guide(
        old_pattern=obsolete["old"],
        new_pattern=obsolete["new"],
        reason=obsolete["reason"]
    )
    
    # Save migration guide
    guide_path = f"cortex-brain/documents/migrations/{obsolete['old'].id}-to-{obsolete['new'].id}.md"
    save_file(guide_path, migration_guide)
```

**Output:** 2 migration guides created

---

## 📊 Knowledge Extraction Report

```markdown
# Knowledge Extraction Report - Planning System v5.0

**Date:** January 2, 2026  
**Plan:** orchestrator-enhancement  
**Duration:** 49 days

---

## Summary

| Metric | Value |
|--------|-------|
| **Patterns Extracted** | 23 |
| **New Knowledge Graph Nodes** | 23 |
| **Obsolete Patterns Deprecated** | 2 |
| **Modules Added to Dev Context** | 12 |
| **Lessons Learned** | 8 |
| **Migration Guides Created** | 2 |

---

## Top Patterns Extracted

1. **MCP Tool Orchestrator Invocation Pattern** (confidence: high, reusability: high)
   - Guarantees orchestrator execution vs. prompt interpretation
   - Type-safe parameters, observable progress, error handling
   
2. **Continuous Knowledge Library Pattern** (confidence: high, reusability: high)
   - Query KL at every phase, extract patterns back
   - Transforms KL into living, growing knowledge base
   
3. **Hierarchical Plan Structure Pattern** (confidence: high, reusability: high)
   - Master + phase sub-files with 2-way linking
   - Better scalability, parallel editing, no merge conflicts

---

## Brain Tier Updates

### Tier 2 (Knowledge Graph)
- ✅ Added 23 pattern nodes
- ✅ Deprecated 2 obsolete patterns
- ✅ Added 47 bidirectional edges
- ✅ No orphaned references

### Tier 3 (Development Context)
- ✅ Registered 12 new modules
- ✅ Updated file relationships (87 files)
- ✅ Added 8 lessons learned
- ✅ Deprecated 2 obsolete modules

---

## Obsolete Patterns Replaced

1. **terminal_wrapper_pattern** → **mcp_tool_orchestrator_invocation_pattern**
   - Reason: MCP tool is more robust and type-safe
   - Migration Guide: `migrations/terminal-wrapper-to-mcp-tool.md`
   - Deadline: March 1, 2026

2. **monolithic_plan_pattern** → **hierarchical_plan_structure_pattern**
   - Reason: Hierarchical structure scales better
   - Migration Guide: `migrations/monolithic-to-hierarchical-plans.md`
   - Deadline: March 1, 2026

---

## Next Steps

1. Review extracted patterns with team
2. Prioritize pattern reuse in upcoming projects
3. Migrate from obsolete patterns (2-month deadline)
4. Update documentation library (Phase 12)
```

---

## ✅ Acceptance Criteria

- [ ] All patterns from all phases aggregated (23 patterns)
- [ ] Tier 2 knowledge graph updated (23 nodes, 2 deprecated)
- [ ] Tier 3 development context updated (12 modules)
- [ ] Lessons learned documented (8 lessons)
- [ ] Obsolete patterns detected and marked (2 patterns)
- [ ] Migration guides created (2 guides)
- [ ] Bidirectional links validated (no orphaned references)
- [ ] Knowledge extraction report generated

---

## 🚀 Next Phase

**[Phase 12: Documentation Library Update →](phase-12-documentation-update.md)**

In the final phase, we'll update the documentation library with:
- Best practices extracted from implementation
- Code examples and templates
- Cross-references to related patterns
- Archived obsolete documentation

---

**[← Back to Master Plan](../00-MASTER-PLAN.md)** | **[Previous: REFACTOR](phase-10-refactor.md)**
