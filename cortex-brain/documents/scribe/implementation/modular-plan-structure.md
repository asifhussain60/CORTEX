# Modular Plan Structure Implementation Guide

**Feature:** Planning System 2.0 - REQ-009  
**Version:** 3.1.0  
**Created:** December 13, 2025  
**Status:** 🔧 Implementation Pending  
**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Overview

This guide documents the implementation of modular plan structure support in Planning System 2.0, enabling plans to be organized in dedicated folders with master plans and sub-plans.

---

## 📊 Current vs. Proposed Structure

### Current Structure (Single File)

```
cortex-brain/documents/planning/
├── PLAN-2025-12-13-CORTEX-SCRIBE-ENHANCEMENT.md  (985 lines)
└── archived/
    └── PLAN-2025-11-21-ENTERPRISE-DOC-*.md
```

**Limitations:**
- ❌ Large plans become unwieldy (500+ lines)
- ❌ No parallel development support
- ❌ Difficult to navigate and maintain
- ❌ All content in single file

### Proposed Structure (Modular)

```
cortex-brain/documents/planning/
├── PLAN-2025-12-13-CORTEX-SCRIBE/
│   ├── MASTER-PLAN.md                    # Overview + TOC with links
│   ├── sub-plans/
│   │   ├── phase-1-analysis.md           # Individual phase plans
│   │   ├── phase-2-architecture.md
│   │   ├── phase-3-implementation.md
│   │   ├── phase-4-testing.md
│   │   ├── phase-5-deployment.md
│   │   └── phase-6-documentation.md
│   ├── resources/
│   │   ├── diagrams/
│   │   │   ├── architecture.mmd
│   │   │   └── workflow.mmd
│   │   └── references/
│   │       └── external-docs.md
│   └── artifacts/
│       ├── feature-tracker.md            # Feature implementation tracker
│       ├── decision-log.md               # Architecture decision records
│       └── execution-log.md              # Phase execution history
└── archived/
```

**Benefits:**
- ✅ Better organization for large plans
- ✅ Parallel development (multiple engineers on different phases)
- ✅ Easier navigation and maintenance
- ✅ Clear separation of concerns
- ✅ Reusable sub-plans across projects

---

## 🏗️ Implementation Plan

### Phase 1: Folder Generator (3 hours)

**Goal:** Create folder structure generation utility

**Tasks:**

1. **Add `create_plan_folder_structure()` method to `PlanningOrchestrator`**
   ```python
   def create_plan_folder_structure(self, plan_name: str, plan_date: str) -> Path:
       """
       Create modular plan folder structure.
       
       Args:
           plan_name: Feature name (e.g., "CORTEX-SCRIBE")
           plan_date: Date in YYYY-MM-DD format
           
       Returns:
           Path to plan root folder
       """
       folder_name = f"PLAN-{plan_date}-{plan_name}"
       plan_root = Path(f"cortex-brain/documents/planning/{folder_name}")
       
       # Create directory structure
       (plan_root / "sub-plans").mkdir(parents=True, exist_ok=True)
       (plan_root / "resources/diagrams").mkdir(parents=True, exist_ok=True)
       (plan_root / "resources/references").mkdir(parents=True, exist_ok=True)
       (plan_root / "artifacts").mkdir(parents=True, exist_ok=True)
       
       return plan_root
   ```

2. **Generate MASTER-PLAN.md template**
   ```markdown
   # 🧠 CORTEX {Feature Name} - Master Plan
   
   **Plan ID:** PLAN-{DATE}-{NAME}
   **Created:** {Date}
   **Status:** 🔍 Planning
   **Author:** Asif Hussain
   
   ---
   
   ## 📑 Plan Structure
   
   This is a **modular plan** organized in dedicated folder structure:
   
   - **Master Plan** (this file) - Overview and navigation
   - **Sub-Plans** - Individual phase implementations
   - **Resources** - Diagrams, references, external docs
   - **Artifacts** - Trackers, logs, decision records
   
   ---
   
   ## 🎯 Executive Summary
   
   {Overview of feature and objectives}
   
   ---
   
   ## 📋 Sub-Plans (Phases)
   
   1. [Phase 1: Analysis](sub-plans/phase-1-analysis.md)
   2. [Phase 2: Architecture](sub-plans/phase-2-architecture.md)
   3. [Phase 3: Implementation](sub-plans/phase-3-implementation.md)
   4. [Phase 4: Testing](sub-plans/phase-4-testing.md)
   5. [Phase 5: Deployment](sub-plans/phase-5-deployment.md)
   6. [Phase 6: Documentation](sub-plans/phase-6-documentation.md)
   
   ---
   
   ## 📊 Artifacts
   
   - [Feature Tracker](artifacts/feature-tracker.md) - Implementation progress
   - [Decision Log](artifacts/decision-log.md) - Architecture decisions
   - [Execution Log](artifacts/execution-log.md) - Phase execution history
   
   ---
   
   ## 📁 Resources
   
   - [Architecture Diagrams](resources/diagrams/)
   - [External References](resources/references/)
   ```

3. **Add README.md to each subdirectory**
   - `sub-plans/README.md` - Explains phase organization
   - `resources/README.md` - Documents resource types
   - `artifacts/README.md` - Describes artifact purposes

**Validation:**
- ✅ Folder structure created correctly
- ✅ All directories have README files
- ✅ MASTER-PLAN.md generated with correct links

---

### Phase 2: Content Splitter (3 hours)

**Goal:** Extract phases from single-file plans into individual sub-plans

**Tasks:**

1. **Add `split_plan_into_phases()` method**
   ```python
   def split_plan_into_phases(self, plan_content: str, plan_root: Path) -> List[Path]:
       """
       Split comprehensive plan into individual phase files.
       
       Args:
           plan_content: Full plan markdown content
           plan_root: Root folder for plan
           
       Returns:
           List of generated sub-plan file paths
       """
       phases = self._extract_phases_from_plan(plan_content)
       sub_plan_files = []
       
       for i, phase in enumerate(phases, start=1):
           phase_name = phase['name'].lower().replace(' ', '-')
           file_path = plan_root / f"sub-plans/phase-{i}-{phase_name}.md"
           
           # Generate phase markdown
           phase_md = self._generate_phase_markdown(phase, i)
           file_path.write_text(phase_md)
           
           sub_plan_files.append(file_path)
       
       return sub_plan_files
   ```

2. **Implement `_extract_phases_from_plan()`**
   - Parse markdown headers (## Phase N:)
   - Extract phase content and metadata
   - Preserve code blocks, lists, diagrams

3. **Generate feature tracker artifact**
   ```python
   def generate_feature_tracker(self, features: List[Dict], plan_root: Path):
       """
       Create feature-tracker.md artifact from feature list.
       """
       tracker_path = plan_root / "artifacts/feature-tracker.md"
       # ... implementation
   ```

**Validation:**
- ✅ Phases extracted correctly
- ✅ Sub-plan files created with proper formatting
- ✅ Feature tracker artifact generated
- ✅ Links in master plan are valid

---

### Phase 3: Integration (2 hours)

**Goal:** Integrate modular structure into planning workflow

**Tasks:**

1. **Add configuration option to `cortex.config.json`**
   ```json
   {
     "planning": {
       "plan_structure_mode": "single_file",  // or "modular"
       "default_phases": 6,
       "auto_generate_tracker": true
     }
   }
   ```

2. **Update `PlanningOrchestrator.execute()`**
   ```python
   def execute(self, feature_request: str, config: PlanningConfig):
       # ... existing planning logic ...
       
       if config.plan_structure_mode == "modular":
           plan_root = self.create_plan_folder_structure(plan_name, plan_date)
           self.generate_master_plan(plan_root, plan_summary)
           self.split_plan_into_phases(plan_content, plan_root)
           self.generate_feature_tracker(features, plan_root)
           return f"Modular plan created: {plan_root}"
       else:
           # Generate single-file plan (existing behavior)
           return self.generate_single_file_plan(plan_content)
   ```

3. **Update response template**
   ```markdown
   ## 🧠 CORTEX Planning Complete
   
   ### 📁 Plan Location
   
   **Modular Plan:** [PLAN-{DATE}-{NAME}/](file:///{path})
   
   **Quick Links:**
   - [Master Plan](file:///{path}/MASTER-PLAN.md)
   - [Phase 1](file:///{path}/sub-plans/phase-1-analysis.md)
   - [Feature Tracker](file:///{path}/artifacts/feature-tracker.md)
   ```

4. **Create migration utility**
   ```bash
   # scripts/migrate_plan_to_modular.py
   python -m scripts.migrate_plan_to_modular \
       cortex-brain/documents/planning/PLAN-2025-12-13-CORTEX-SCRIBE-ENHANCEMENT.md
   ```

**Validation:**
- ✅ Configuration option works
- ✅ Modular plans generated when enabled
- ✅ Single-file plans still work (backward compatibility)
- ✅ Response template shows correct links
- ✅ Migration utility converts existing plans

---

## 🚀 Migration Strategy

### Migrating Existing Plans

**Option 1: Keep as single file** (recommended for plans <500 lines)
- No action needed
- Plans continue to work as-is

**Option 2: Migrate to modular** (recommended for plans >500 lines)

```bash
# Run migration utility
python -m scripts.migrate_plan_to_modular \
    cortex-brain/documents/planning/PLAN-2025-12-13-CORTEX-SCRIBE-ENHANCEMENT.md

# Result:
# ✅ Created: cortex-brain/documents/planning/PLAN-2025-12-13-CORTEX-SCRIBE/
# ✅ Generated: MASTER-PLAN.md
# ✅ Created: 6 sub-plans
# ✅ Generated: feature-tracker.md
# ✅ Archived: Original single file → archived/
```

---

## 📋 Implementation Checklist

### Phase 1: Folder Generator
- [ ] Add `create_plan_folder_structure()` method
- [ ] Create MASTER-PLAN.md template
- [ ] Generate README files for subdirectories
- [ ] Test folder structure creation
- [ ] Validate all directories created correctly

### Phase 2: Content Splitter
- [ ] Add `split_plan_into_phases()` method
- [ ] Implement `_extract_phases_from_plan()` parser
- [ ] Create `_generate_phase_markdown()` formatter
- [ ] Add `generate_feature_tracker()` method
- [ ] Test phase extraction accuracy
- [ ] Validate sub-plan formatting

### Phase 3: Integration
- [ ] Add `plan_structure_mode` configuration
- [ ] Update `PlanningOrchestrator.execute()` with mode switch
- [ ] Update response template with modular links
- [ ] Create `scripts/migrate_plan_to_modular.py` utility
- [ ] Test modular plan generation end-to-end
- [ ] Verify backward compatibility (single-file still works)
- [ ] Document migration process

### Testing
- [ ] Unit tests for folder structure generator
- [ ] Unit tests for content splitter
- [ ] Integration tests for end-to-end workflow
- [ ] Test migration utility on existing plans
- [ ] Validate links in master plan are correct
- [ ] Test with both configuration modes

### Documentation
- [ ] Update Planning System 2.0 guide
- [ ] Add modular structure examples
- [ ] Document migration process
- [ ] Update CHANGELOG.md with REQ-009

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Folder structure generated correctly
- ✅ Master plan with valid links
- ✅ Sub-plans extracted and formatted
- ✅ Feature tracker artifact created
- ✅ Configuration option works
- ✅ Backward compatibility maintained

### Quality Requirements
- ✅ All links in master plan are valid
- ✅ Phase content preserved during extraction
- ✅ Formatting consistent across sub-plans
- ✅ No data loss during migration

### Performance Requirements
- ✅ Folder creation <100ms
- ✅ Content splitting <500ms for 1000-line plans
- ✅ Migration utility completes <2 seconds

---

## 📊 Estimated Effort

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1: Folder Generator | 3 hours | Folder creation, MASTER-PLAN template, README files |
| Phase 2: Content Splitter | 3 hours | Phase extraction, sub-plan generation, tracker creation |
| Phase 3: Integration | 2 hours | Configuration, workflow updates, migration utility |
| **Total** | **8 hours** | **Implementation + testing + documentation** |

---

## 🔗 Related Documents

- [Planning System 2.0 Manifest](../../orchestrator-manifests/planning-system-2.0-manifest.yaml) - REQ-009
- [Planning Orchestrator Guide](../../../.github/prompts/modules/planning-orchestrator-guide.md)
- [CORTEX Scribe Enhancement Plan](../planning/PLAN-2025-12-13-CORTEX-SCRIBE-ENHANCEMENT.md) - Example plan to migrate

---

## 📝 Notes

**When to use modular structure:**
- ✅ Plans >500 lines
- ✅ Multiple engineers working on different phases
- ✅ Need to track artifacts separately (decisions, features, logs)
- ✅ Complex plans with many diagrams/resources

**When to use single file:**
- ✅ Plans <500 lines
- ✅ Simple features with 3-4 phases
- ✅ Solo development
- ✅ Quick prototyping

---

**Implementation Target:** Q1 2026 (Medium priority)  
**Backward Compatibility:** 100% (single-file mode remains default)
