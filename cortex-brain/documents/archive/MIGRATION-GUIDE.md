# Token-Optimized Planning Structure Migration Guide

**Purpose:** Guide for extracting phases from monolithic MASTER-PLAN.md into token-optimized structure  
**Version:** 1.0  
**Author:** CORTEX Development Team  
**Created:** December 20, 2025

---

## 📋 Overview

**Problem:** MASTER-PLAN.md = 7,283 lines (~20,000 tokens) causes massive context window consumption

**Solution:** 4-tier hierarchical structure with smart loading

**Benefits:**
- **95% token reduction** for status queries (20,000 → 400 tokens)
- **94% token reduction** for architecture queries (20,000 → 1,200 tokens)
- **87% token reduction** for phase-specific queries (20,000 → 2,500 tokens)
- Better git diff history (smaller files = clearer changes)
- Faster loading for specific contexts
- Scalable pattern for all complex plans

---

## 🏗️ New Structure

```
CORTEX-3.0-4.0/
├── CORTEX4-STATUS.md                    # Tier 1: Visual tracker (~150 lines, ~400 tokens)
├── 00-MASTER-PLAN.md                    # Tier 2: Overview (~300 lines, ~800 tokens)
├── metadata/
│   └── plan-metadata.yaml               # Machine-readable metadata
├── phases/                              # Tier 3: Phase details
│   ├── README.md                        # Navigation guide
│   ├── phase-01-pre-migration-cleanup.md
│   ├── phase-02-autonomous-execution.md
│   ├── phase-03-foundation.md
│   ├── phase-04-documentation-visualization.md
│   ├── phase-04.5-documentation-generation.md
│   ├── phase-05-brain-agentic-ai.md
│   ├── phase-06-orchestrator-consolidation.md
│   ├── phase-07-operations-simplification.md
│   ├── phase-08-testing-validation.md
│   ├── phase-09-documentation-finalization.md
│   └── phase-10-knowledge-library.md
├── workers/                             # Tier 4: Granular sub-tasks (optional)
│   ├── phase-06/
│   │   ├── week-07-execution-orchestrator.md
│   │   ├── week-07-documentation-orchestrator.md
│   │   ├── week-08-planning-system-core.md
│   │   └── week-09-planning-system-intelligence.md
│   └── phase-10/
│       ├── week-22-engineering-fundamentals.md
│       └── ...
└── archive/
    └── MASTER-PLAN-original-v1.5.md     # Original 7,283-line file
```

---

## 📊 Migration Status

### ✅ Completed

1. **Folder structure created** (`phases/`, `metadata/`, `workers/`, `archive/`)
2. **Metadata YAML created** (`plan-metadata.yaml` with smart routing config)
3. **Status file created** (`CORTEX4-STATUS.md` with visual tracker)
4. **Master hub created** (`00-MASTER-PLAN.md` with overview only)
5. **Phase README created** (`phases/README.md` for navigation)
6. **Smart loader utility created** (`src/utils/smart_plan_loader.py`)

### ⏸️ Pending (Manual Extraction Required)

**Why Manual?** 7,283 lines with complex nested structure requires careful section identification

**Phases to Extract:** (11 files)

1. **phase-01-pre-migration-cleanup.md** (~lines 2895-3100 of original)
2. **phase-02-autonomous-execution.md** (~lines 3115-3300 of original)
3. **phase-03-foundation.md** (~lines 4171-4640 of original)
4. **phase-04-documentation-visualization.md** (~lines 4641-4870 of original)
5. **phase-04.5-documentation-generation.md** (~lines 8276-8528 of original)
6. **phase-05-brain-agentic-ai.md** (~lines 4032-4170 + 4871-4906 of original)
7. **phase-06-orchestrator-consolidation.md** (~lines 4907-5827 of original)
8. **phase-07-operations-simplification.md** (~lines 5828-5943 of original)
9. **phase-08-testing-validation.md** (~lines 5944-6044 of original)
10. **phase-09-documentation-finalization.md** (~lines 6045-6624 of original)
11. **phase-10-knowledge-library.md** (~lines 7307-8275 of original)

**Extraction Strategy:**

```bash
# For each phase:
# 1. Identify line range in original MASTER-PLAN.md
# 2. Extract section content
# 3. Add phase header with backlinks
# 4. Save to phases/phase-{id}-{name}.md
```

---

## 🔧 Phase File Template

```markdown
# Phase {ID}: {Name}

**Duration:** {X} days | **Weeks:** Week {Y}-{Z} | **Status:** {STATUS}

[↑ Back to Master Plan](../00-MASTER-PLAN.md) | [↑ Back to Status](../CORTEX4-STATUS.md) | [↑ Phase Index](./README.md)

---

## 📋 Overview

{Brief summary of phase purpose and goals}

## 🎯 Objectives

{Numbered list of phase objectives}

## 📦 Deliverables

{Key outputs and artifacts}

## 🔗 Dependencies

**Prerequisites:**
{List of blocking dependencies}

**Enables:**
{List of phases unblocked by this phase}

## 📅 Timeline

### Week {N}: {Focus Area}

**Days {X}-{Y}:**
{Detailed day-by-day breakdown}

**Deliverables:**
{Week-specific outputs}

**Validation:**
{Week-specific checks}

## ✅ Success Criteria

**Technical:**
{Technical validation criteria}

**Quality:**
{Quality gates}

**Metrics:**
{Measurable outcomes}

## 📚 Related Documents

{Links to related architecture/analysis docs}

---

**Last Updated:** {Date}  
**Phase Owner:** {Name}
```

---

## 🤖 Smart Loader Integration

### Usage in Orchestrators

```python
from src.utils.smart_plan_loader import SmartPlanLoader

# Initialize loader
loader = SmartPlanLoader("d:/PROJECTS/CORTEX")

# Query 1: Status only (~400 tokens)
status = loader.load_plan_context("What's the current status?")

# Query 2: Phase-specific (~2,500 tokens)
phase6 = loader.load_plan_context("Tell me about Phase 6")

# Query 3: Architecture (~1,200 tokens)
arch = loader.load_plan_context("What's the architecture strategy?")

# Estimate tokens before loading
estimated = loader.get_token_estimate("What's the current status?")
print(f"Will load ~{estimated} tokens")  # 400
```

### Query Intent Classification

**Smart Loader Automatically Detects:**

| Query Pattern | Intent | Loads | Tokens |
|---------------|--------|-------|--------|
| "status", "summary", "progress" | status_only | CORTEX4-STATUS.md | ~400 |
| "architecture", "dependencies", "design" | architecture | Status + Master Hub | ~1,200 |
| "phase 6", "Phase 06" | phase_specific | Status + Phase 6 | ~2,500 |
| "week 9", "Week 09" | week_specific | Status + Worker File | ~1,000 |
| Other | default | Status + Master Hub | ~1,200 |

---

## 🔄 Orchestrator Updates Required

### 1. Update PlanFolderManager (`src/workflows/plan_folder_manager.py`)

**Change:**
```python
# OLD: Single master-plan.md file
master_plan = plan_folder / "master-plan.md"

# NEW: Hierarchical structure with smart loading
from src.utils.smart_plan_loader import SmartPlanLoader
loader = SmartPlanLoader(cortex_root)
plan_content = loader.load_plan_context(query)
```

**Impact:** Minimal (wrapper compatibility maintained)

### 2. Update PlanningOrchestrator (`src/orchestrators/planning/planning_orchestrator.py`)

**Change:**
```python
# Add smart loader for plan context loading
def load_plan_context(self, query: str) -> str:
    """Load plan context optimized for query intent."""
    loader = SmartPlanLoader(self.workspace_root)
    return loader.load_plan_context(query)
```

**Impact:** Internal method, no API changes

### 3. Update Documentation References

**Files to Update:**
- `planning-system-4.0-manifest.yaml` (reference to MASTER-PLAN.md)
- `CORTEX.prompt.md` (planning system instructions)
- `cortex-brain/response-templates-v4.yaml` (plan loading templates)

**Changes:**
```yaml
# OLD
master_plan: "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md"

# NEW
master_plan_structure:
  status: "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/CORTEX4-STATUS.md"
  master_hub: "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/00-MASTER-PLAN.md"
  phases: "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/phases/"
  smart_loader: "src/utils/smart_plan_loader.py"
```

---

## 📈 Token Optimization Metrics

### Before Migration

**Query:** "What's the current status of CORTEX 4.0?"  
**Loads:** Entire MASTER-PLAN.md (7,283 lines)  
**Tokens:** ~20,000  
**Time:** ~2-3 seconds

### After Migration

**Query:** "What's the current status of CORTEX 4.0?"  
**Loads:** CORTEX4-STATUS.md only (150 lines)  
**Tokens:** ~400  
**Time:** <1 second  
**Reduction:** **95%**

---

## 🎯 Validation Checklist

**Structure:**
- [ ] All 11 phase files created
- [ ] All phase files have backlinks to master plan
- [ ] Phases README has navigation links
- [ ] Metadata YAML has all phase entries
- [ ] Original MASTER-PLAN.md archived

**Content:**
- [ ] Status tracker has visual progress bars
- [ ] Master hub has architecture overview
- [ ] Each phase has overview, objectives, deliverables
- [ ] Each phase has timeline and success criteria
- [ ] Phase dependencies documented

**Integration:**
- [ ] Smart loader utility tested
- [ ] PlanFolderManager updated (optional)
- [ ] PlanningOrchestrator updated (optional)
- [ ] Manifest references updated
- [ ] Response templates updated (optional)

**Testing:**
- [ ] Smart loader loads status correctly
- [ ] Smart loader routes phase queries correctly
- [ ] Smart loader estimates tokens accurately
- [ ] Token reduction validated (95% for status queries)
- [ ] Navigation links work correctly

---

## 🚀 Rollout Plan

### Phase 1: Structure Setup (COMPLETE)
- ✅ Create folder structure
- ✅ Create metadata YAML
- ✅ Create status file
- ✅ Create master hub
- ✅ Create smart loader utility

### Phase 2: Content Extraction (PENDING)
- ⏸️ Extract Phase 1 content
- ⏸️ Extract Phase 2 content
- ⏸️ Extract Phase 3 content
- ⏸️ Extract Phase 4 content
- ⏸️ Extract Phase 4.5 content
- ⏸️ Extract Phase 5 content
- ⏸️ Extract Phase 6 content
- ⏸️ Extract Phase 7 content
- ⏸️ Extract Phase 8 content
- ⏸️ Extract Phase 9 content
- ⏸️ Extract Phase 10 content

### Phase 3: Integration (PENDING)
- ⏸️ Update PlanFolderManager (optional)
- ⏸️ Update PlanningOrchestrator (optional)
- ⏸️ Update manifest references
- ⏸️ Update response templates (optional)

### Phase 4: Validation (PENDING)
- ⏸️ Test smart loader
- ⏸️ Validate token reduction
- ⏸️ Test navigation links
- ⏸️ Verify content completeness

### Phase 5: Documentation (PENDING)
- ⏸️ Update planning system docs
- ⏸️ Add pattern to CORTEX.prompt.md
- ⏸️ Create migration guide (this file)

---

## 📚 Future Plans

**Standard Pattern for All Complex Plans:**

This token-optimized structure becomes the **standard MO** for:
- Planning System 4.0 plans
- ADO planning plans
- Architecture migration plans
- Any plan >2,000 lines

**Automatic Generation:**

Planning Orchestrator should auto-create this structure:
```python
def generate_plan(self, complexity: PlanComplexity) -> PlanResult:
    if complexity >= PlanComplexity.MEDIUM:
        # Create hierarchical structure
        self._create_status_file()
        self._create_master_hub()
        self._create_phase_files()
        self._create_metadata_yaml()
    else:
        # Single file for simple plans
        self._create_single_plan_file()
```

---

## 🤝 Contributing

**Extracting Phase Content:**

1. Identify phase section in original MASTER-PLAN.md
2. Copy content (preserve formatting)
3. Add phase header with backlinks
4. Add "Last Updated" footer
5. Save to `phases/phase-{id}-{name}.md`
6. Update phases/README.md navigation
7. Test links

**Reporting Issues:**

- Token estimates incorrect? Update `metadata/plan-metadata.yaml`
- Smart loader routing wrong? Update `src/utils/smart_plan_loader.py`
- Navigation broken? Check backlinks in phase files

---

**Last Updated:** December 20, 2025  
**Maintained By:** CORTEX Development Team  
**Pattern Version:** 1.0
