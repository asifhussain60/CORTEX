# Template Migration Mapping

**Generated:** 2025-12-31  
**Purpose:** Phase 2 - Map existing templates to composable blocks

---

## 📊 Named Template Inventory

| Template Name | Lines | Tier | Orchestrator | Sections Count |
|---------------|-------|------|-------------|----------------|
| `autonomous_execution_progress` | 715-770 | TIER 3 | Planning | 6 |
| `ado_execution_progress` | 780-845 | TIER 3 | ADO | 7 |
| `plan_created` | 860-880 | TIER 2 | Planning | 3 |
| `progress_bar_simple` | 890-893 | TIER 2 | Generic | 1 |

**Total Named Templates:** 4

---

## 🔍 Template Deconstruction

### Template 1: `autonomous_execution_progress`

**Source Lines:** 715-770 (56 lines)

**Extractable Blocks:**

| Block ID | Block Name | Content Type | Reusable |
|----------|------------|--------------|----------|
| `cortex_header_shield` | CORTEX Header with Shield | Header | ✅ Yes |
| `progress_tracker_standard` | Progress Table | Table | ✅ Yes |
| `threat_analysis` | Security Analysis | Table (conditional) | ✅ Yes |
| `validation_status_dor_dod` | DoR/DoD Validation | Table | ✅ Yes |
| `plan_file_link` | Plan File Link | Link | ✅ Yes |
| `next_action` | Next Action | Text | ✅ Yes |

**Migration Strategy:**
```yaml
autonomous_execution_progress:
  source_lines: "715-770"
  extractable_blocks:
    - block: "cortex_header_shield"
      format: "## 🛡️🧠 CORTEX {{title}}"
      mandatory: true
      
    - block: "progress_tracker_standard"
      format: "Table with phase rows + progress bars"
      mandatory: true
      
    - block: "threat_analysis"
      format: "Security metrics table"
      mandatory: false
      condition: "threat_analysis_enabled"
      
    - block: "validation_status_dor_dod"
      format: "DoR/DoD status checks"
      mandatory: true
      
    - block: "plan_file_link"
      format: "Clickable markdown link"
      mandatory: true
      
    - block: "next_action"
      format: "Next: {{action}}"
      mandatory: true
  
  status: "migrate_to_composable"
  target_algorithm: true
```

---

### Template 2: `ado_execution_progress`

**Source Lines:** 780-845 (66 lines)

**Extractable Blocks:**

| Block ID | Block Name | Content Type | Reusable |
|----------|------------|--------------|----------|
| `cortex_header_shield` | CORTEX Header with Shield | Header | ✅ Yes (shared) |
| `progress_tracker_standard` | Progress Table | Table | ✅ Yes (shared) |
| `work_item_summary` | ADO Work Item Table | Table | ✅ Yes (ADO-specific) |
| `ado_links` | ADO External Links | List (conditional) | ✅ Yes (ADO-specific) |
| `validation_status_ado` | DoR/DoD + ADO Auth | Table | ✅ Yes (ADO-specific) |
| `plan_file_link` | Plan File Link | Link | ✅ Yes (shared) |
| `next_action` | Next Action | Text | ✅ Yes (shared) |

**Migration Strategy:**
```yaml
ado_execution_progress:
  source_lines: "780-845"
  extractable_blocks:
    - block: "cortex_header_shield"
      format: "## 🛡️🧠 CORTEX {{title}}"
      mandatory: true
      shared: true
      
    - block: "progress_tracker_standard"
      format: "Table with phase rows + progress bars"
      mandatory: true
      shared: true
      
    - block: "work_item_summary"
      format: "Epic/Feature/Story/Task table with SP"
      mandatory: true
      orchestrator_specific: "ado"
      
    - block: "ado_links"
      format: "Bulleted list of ADO URLs"
      mandatory: false
      condition: "ado_links_exist"
      orchestrator_specific: "ado"
      
    - block: "validation_status_ado"
      format: "DoR/DoD + ADO authentication check"
      mandatory: true
      orchestrator_specific: "ado"
      
    - block: "plan_file_link"
      format: "Clickable markdown link"
      mandatory: true
      shared: true
      
    - block: "next_action"
      format: "Next: {{action}}"
      mandatory: true
      shared: true
  
  status: "migrate_to_composable"
  target_algorithm: true
```

---

### Template 3: `plan_created`

**Source Lines:** 860-880 (21 lines)

**Extractable Blocks:**

| Block ID | Block Name | Content Type | Reusable |
|----------|------------|--------------|----------|
| `cortex_header_shield` | CORTEX Header with Shield | Header | ✅ Yes (shared) |
| `plan_summary_table` | Plan Metrics Table | Table | ✅ Yes |
| `plan_structure_tree` | Folder Structure ASCII | Code block | ✅ Yes |
| `plan_file_link` | Plan File Link | Link | ✅ Yes (shared) |
| `next_action` | Next Action | Text | ✅ Yes (shared) |

**Migration Strategy:**
```yaml
plan_created:
  source_lines: "860-880"
  extractable_blocks:
    - block: "cortex_header_shield"
      format: "## 🛡️🧠 CORTEX {{title}}"
      mandatory: true
      shared: true
      
    - block: "plan_summary_table"
      format: "Plan ID/phases/effort/files table"
      mandatory: true
      
    - block: "plan_structure_tree"
      format: "ASCII folder tree in code block"
      mandatory: true
      
    - block: "plan_file_link"
      format: "Clickable markdown link"
      mandatory: true
      shared: true
      
    - block: "next_action"
      format: "Next: {{action}}"
      mandatory: true
      shared: true
  
  status: "migrate_to_composable"
  target_algorithm: true
```

---

### Template 4: `progress_bar_simple`

**Source Lines:** 890-893 (4 lines)

**Extractable Blocks:**

| Block ID | Block Name | Content Type | Reusable |
|----------|------------|--------------|----------|
| `progress_bar_inline` | Inline Progress Bar | Text | ✅ Yes |

**Migration Strategy:**
```yaml
progress_bar_simple:
  source_lines: "890-893"
  extractable_blocks:
    - block: "progress_bar_inline"
      format: "[{{filled}}{{empty}}] {{percentage}}%"
      mandatory: true
      
  status: "migrate_to_composable"
  target_algorithm: false  # Too simple, keep as-is
```

---

## 🧩 Composable Block Registry

### Shared Blocks (Used by Multiple Templates)

| Block ID | Usage Count | Templates |
|----------|-------------|-----------|
| `cortex_header_shield` | 3 | autonomous_execution_progress, ado_execution_progress, plan_created |
| `progress_tracker_standard` | 2 | autonomous_execution_progress, ado_execution_progress |
| `plan_file_link` | 3 | autonomous_execution_progress, ado_execution_progress, plan_created |
| `next_action` | 3 | autonomous_execution_progress, ado_execution_progress, plan_created |

### Orchestrator-Specific Blocks

| Block ID | Orchestrator | Templates |
|----------|-------------|-----------|
| `threat_analysis` | Planning | autonomous_execution_progress |
| `work_item_summary` | ADO | ado_execution_progress |
| `ado_links` | ADO | ado_execution_progress |
| `validation_status_ado` | ADO | ado_execution_progress |
| `plan_summary_table` | Planning | plan_created |
| `plan_structure_tree` | Planning | plan_created |

### Generic Blocks (Single Use, Potential Reuse)

| Block ID | Templates | Reuse Potential |
|----------|-----------|-----------------|
| `validation_status_dor_dod` | autonomous_execution_progress | High (all planning/execution) |
| `progress_bar_inline` | progress_bar_simple | High (quick status updates) |

---

## 📋 Block Categorization

### Category 1: Mandatory (Always Present)

| Block | Description |
|-------|-------------|
| `cortex_header_shield` | Orchestrator-engaged header with 🛡️ |
| `next_action` | Final directive |

### Category 2: Conditional (Context-Driven)

| Block | Condition |
|-------|-----------|
| `progress_tracker_standard` | `multi_phase_operation` |
| `threat_analysis` | `threat_analysis_enabled` |
| `validation_status_dor_dod` | `validation_required` |
| `work_item_summary` | `orchestrator_type == 'ado'` |
| `ado_links` | `ado_links_exist` |
| `plan_file_link` | `plan_created` |
| `plan_summary_table` | `operation == 'plan_creation'` |
| `plan_structure_tree` | `operation == 'plan_creation'` |

---

## 🚀 Migration Roadmap

### Phase 1: Core Shared Blocks ✅
- [x] Identify shared blocks
- [x] Map to existing templates
- [x] Define reuse criteria

### Phase 2: Orchestrator-Specific Blocks (Next)
- [ ] Catalog ADO-specific blocks
- [ ] Catalog Planning-specific blocks
- [ ] Define other orchestrator needs (TDD, Debug, Lens, etc.)

### Phase 3: Block Composition Rules
- [ ] Define mandatory vs optional
- [ ] Define ordering rules
- [ ] Define context signal triggers

### Phase 4: Algorithm Integration
- [ ] Implement block selection algorithm
- [ ] Implement rendering engine
- [ ] Validate against existing templates

---

## 🎯 Next Steps

**Immediate:**
1. ✅ Complete migration mapping (this document)
2. ⏳ Design template selection algorithm (Phase 3)
3. ⏳ Define composable_blocks schema (Phase 5)

**Future:**
- Create TDD-specific blocks (test cycle status, coverage metrics)
- Create Debug-specific blocks (hypothesis, root cause, fix verification)
- Create Lens-specific blocks (analytics, health metrics, recommendations)

---

**Phase 2 Complete:** ✅ Migration mapping documented  
**Next Phase:** Intelligent Template Algorithm Design
