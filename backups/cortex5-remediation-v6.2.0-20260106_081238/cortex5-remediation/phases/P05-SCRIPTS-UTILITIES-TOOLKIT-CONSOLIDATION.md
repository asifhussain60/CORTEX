# Phase P05: Scripts/Utilities Toolkit Consolidation

**Epic:** cortex5-remediation  
**Phase ID:** P05  
**Status:** PLANNED  
**Created:** January 6, 2026  
**Owner:** Asif Hussain

---

## 🎯 Objective

Consolidate the `scripts/utilities/` folder into a managed **CORTEX Toolkit Orchestrator** with:
- **Audit logging** for all tool executions
- **Intelligence** about tool usage patterns and recommendations
- **Cleanup organization** strategy for continuous optimization
- **Tool lifecycle management** (create, use, archive, delete)
- **Category-based organization** with manifest-driven discovery
- **Integration** with existing `cortex-toolkit/` infrastructure

---

## 📊 Current State Analysis

### Existing Infrastructure

**✅ Already Exists:**
- `cortex-toolkit/` folder with:
  - `core/toolkit_manager.py` - ToolkitManager with audit logging
  - `core/audit_logger.py` - AuditLogger with execution/security events
  - `shared/toolkit_registry.py` - Tool discovery and invocation
  - `core/capability_matrix.py` - Tool overlap detection
  - CLI wrappers for registered tools

**📂 Scripts/Utilities (23 files):**
```
scripts/utilities/
├── analyze_all_repos_task1.3.py
├── analyze_duplicates.py
├── analyze_duplicates_v2.py
├── benchmark_parallel.py
├── check_schema.py
├── debug_dashboard.py
├── fix_test_ids.py
├── launch_admin_dashboard.py
├── migrate_conversations_full.py
├── migrate_conversations_table.py
├── migrate_entities_table.py
├── migrate_messages_table.py
├── phase2_safe_deletion.py
├── phase3_consolidation.py
├── phase4_validation.py
├── phase5_documentation.py
├── preview_docs.py
├── profile_aggregator.py
├── run_aggressive_cleanup.py
├── validate_db_schema.py
├── validate_phase2_completion.py
├── validate_phase_2.1_production.py
├── validate_phase_2.2_production.py
└── validate_phase_2.3_production.py
```

### Gap Analysis

**❌ Missing:**
1. **Orchestrator for scripts/utilities/** - No centralized management
2. **Manifest for utilities** - No metadata, capabilities, dependencies
3. **Audit logging integration** - No execution tracking for utilities
4. **Usage intelligence** - No pattern analysis or recommendations
5. **Cleanup automation** - No continuous optimization strategy
6. **Category organization** - All utilities in flat structure
7. **Lifecycle management** - No archival/deletion policies

---

## 🏗️ Solution Architecture

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│         CORTEX Toolkit Orchestrator (NEW)                   │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ScriptsUtilitiesManager                               │ │
│  │  - Tool discovery (scan scripts/utilities/)           │ │
│  │  - Manifest generation (auto-create metadata)         │ │
│  │  - Category classification (analysis, migration, etc) │ │
│  │  - Audit logging (track all executions)              │ │
│  │  - Usage intelligence (pattern analysis)             │ │
│  │  - Cleanup recommendations (archive/delete)          │ │
│  └───────────────────────────────────────────────────────┘ │
│                         ↓                                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Integration with Existing cortex-toolkit/             │ │
│  │  - ToolkitManager (execution engine)                  │ │
│  │  - AuditLogger (event tracking)                       │ │
│  │  - ToolkitRegistry (tool discovery)                   │ │
│  │  - CapabilityMatrix (overlap detection)              │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Organized Toolkit Structure                     │
│                                                             │
│  cortex-toolkit/                                            │
│  ├── scripts-utilities/  (NEW - categorized utilities)     │
│  │   ├── manifest.yaml                                     │
│  │   ├── analysis/                                         │
│  │   │   ├── analyze_duplicates.py                         │
│  │   │   ├── analyze_all_repos_task1.3.py                  │
│  │   │   └── manifest.yaml                                 │
│  │   ├── database/                                         │
│  │   │   ├── check_schema.py                               │
│  │   │   ├── validate_db_schema.py                         │
│  │   │   └── manifest.yaml                                 │
│  │   ├── migration/                                        │
│  │   │   ├── migrate_conversations_full.py                 │
│  │   │   ├── migrate_conversations_table.py                │
│  │   │   └── manifest.yaml                                 │
│  │   ├── cleanup/                                          │
│  │   │   ├── run_aggressive_cleanup.py                     │
│  │   │   ├── phase2_safe_deletion.py                       │
│  │   │   └── manifest.yaml                                 │
│  │   ├── validation/                                       │
│  │   │   ├── validate_phase2_completion.py                 │
│  │   │   ├── validate_phase_2.1_production.py              │
│  │   │   └── manifest.yaml                                 │
│  │   └── dashboards/                                       │
│  │       ├── debug_dashboard.py                            │
│  │       ├── launch_admin_dashboard.py                     │
│  │       └── manifest.yaml                                 │
│  └── cli/wrappers/  (Auto-generate for all utilities)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases

### Phase P05.1: Audit Infrastructure Setup
**Duration:** 2 hours  
**Deliverables:**
1. Audit logging integration for scripts/utilities
2. Execution event tracking system
3. Usage statistics collector
4. Performance metrics tracker

**Tasks:**
- [ ] Extend AuditLogger to support scripts/utilities category
- [ ] Create execution event schema for utilities
- [ ] Implement usage pattern tracking
- [ ] Add performance profiling hooks

---

### Phase P05.2: Tool Discovery & Classification
**Duration:** 3 hours  
**Deliverables:**
1. Automated tool discovery scanner
2. Category classification system
3. Manifest auto-generation
4. Capability extraction

**Tasks:**
- [ ] Build ScriptsUtilitiesManager class
- [ ] Implement AST-based capability extraction
- [ ] Create category classifier (analysis, migration, cleanup, validation, database, dashboards)
- [ ] Auto-generate manifest.yaml for each utility

**Category Rules:**
```yaml
categories:
  analysis:
    patterns: [analyze_, benchmark_, profile_]
    capabilities: [code_analysis, duplicate_detection, performance_profiling]
  
  database:
    patterns: [check_schema, validate_db, migrate_*_table]
    capabilities: [schema_validation, migration, database_operations]
  
  cleanup:
    patterns: [cleanup, phase*_deletion, phase*_consolidation]
    capabilities: [file_cleanup, safe_deletion, consolidation]
  
  validation:
    patterns: [validate_phase, validate_*_production]
    capabilities: [phase_validation, production_readiness]
  
  dashboards:
    patterns: [launch_, debug_dashboard, preview_]
    capabilities: [visualization, debugging, monitoring]
  
  migration:
    patterns: [migrate_]
    capabilities: [data_migration, schema_migration]
```

---

### Phase P05.3: Organization & Migration
**Duration:** 2 hours  
**Deliverables:**
1. Category-based folder structure
2. Migrated utilities with manifests
3. CLI wrapper generation
4. Updated registry

**Tasks:**
- [ ] Create `cortex-toolkit/scripts-utilities/` structure
- [ ] Migrate 23 utilities to categorized folders
- [ ] Generate manifest.yaml for each category
- [ ] Auto-generate CLI wrappers

---

### Phase P05.4: Intelligence System
**Duration:** 4 hours  
**Deliverables:**
1. Usage pattern analyzer
2. Tool recommendation engine
3. Overlap detection system
4. Cleanup automation

**Tasks:**
- [ ] Build usage pattern analyzer (most/least used tools)
- [ ] Create recommendation engine (suggest similar tools)
- [ ] Integrate CapabilityMatrix for overlap detection
- [ ] Implement cleanup automation (archive stale tools)

**Intelligence Features:**
```python
class UsageIntelligence:
    def analyze_patterns(self) -> UsageReport:
        """Analyze tool usage patterns from audit logs"""
        - Most/least used tools
        - Execution frequency trends
        - Success/failure rates
        - Performance bottlenecks
    
    def recommend_tools(self, task: str) -> List[Tool]:
        """Recommend tools based on task description"""
        - Semantic search across capabilities
        - Usage history correlation
        - Success rate weighting
    
    def detect_duplicates(self) -> List[ToolOverlap]:
        """Detect overlapping functionality"""
        - Use CapabilityMatrix
        - AST similarity analysis
        - Manual review flagging
    
    def recommend_cleanup(self) -> CleanupPlan:
        """Recommend archival/deletion candidates"""
        - Tools unused for >90 days
        - Deprecated tools
        - Duplicate functionality
        - Test-only utilities
```

---

### Phase P05.5: Cleanup Automation
**Duration:** 2 hours  
**Deliverables:**
1. Continuous cleanup orchestrator
2. Archival policies
3. Deletion safeguards
4. Cleanup reports

**Tasks:**
- [ ] Create continuous cleanup orchestrator
- [ ] Implement archival policies (90-day unused → archive)
- [ ] Add deletion safeguards (require explicit approval)
- [ ] Generate cleanup recommendations report

**Archival Policy:**
```yaml
archival_policy:
  triggers:
    - unused_for_days: 90
    - marked_deprecated: true
    - duplicate_of: another_tool
    - test_only: true
  
  safeguards:
    - require_approval: true
    - create_backup: true
    - log_audit_event: true
    - notify_owner: true
  
  archive_location: "cortex-brain/archives/utilities/{category}/{date}/"
```

---

### Phase P05.6: Integration & Testing
**Duration:** 3 hours  
**Deliverables:**
1. Master Orchestrator integration
2. CLI command registration
3. Test suite
4. Documentation

**Tasks:**
- [ ] Integrate with Master Orchestrator (new pattern: `^(toolkit|manage tools)`)
- [ ] Register CLI commands (list, invoke, analyze, cleanup)
- [ ] Create test suite for ScriptsUtilitiesManager
- [ ] Write comprehensive documentation

**CLI Commands:**
```bash
# List all utilities by category
python3 -m src.main "toolkit list scripts-utilities"

# Invoke utility with audit logging
python3 -m src.main "toolkit invoke analyze_duplicates --audit"

# Analyze usage patterns
python3 -m src.main "toolkit analyze usage scripts-utilities"

# Get cleanup recommendations
python3 -m src.main "toolkit cleanup recommend scripts-utilities"

# Archive stale tools
python3 -m src.main "toolkit cleanup archive scripts-utilities --auto-approve"
```

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Tool Discovery** | 100% | All 23 utilities discovered and categorized |
| **Audit Coverage** | 100% | All tool executions logged with audit events |
| **Manifest Generation** | 100% | Auto-generated manifests for all utilities |
| **CLI Wrapper Coverage** | 100% | Wrappers for all utilities |
| **Usage Intelligence** | 90%+ accuracy | Recommendation engine accuracy |
| **Cleanup Automation** | Zero stale tools | Tools unused >90 days archived |
| **Performance** | <500ms overhead | Audit logging + intelligence overhead |

---

## 🛡️ Brain Protection (SKULL) Compliance

**Rules Applied:**
1. **HOLISTIC_DISCOVERY** - Search existing `cortex-toolkit/` before creating duplicates
2. **TDD_ENFORCEMENT** - RED→GREEN→REFACTOR for all new components
3. **PLANNING_ISOLATION** - This plan creates structure ONLY, implementation in separate phase
4. **HAND_OFF_PROTOCOL** - Autonomous Python execution via terminal invocation

---

## 📂 Deliverables Structure

```
cortex-brain/documents/planning/active/cortex5-remediation/
├── phases/
│   ├── P05-SCRIPTS-UTILITIES-TOOLKIT-CONSOLIDATION.md (this file)
│   └── P05-implementation-checklist.md
├── artifacts/
│   ├── P05-category-classification.yaml
│   ├── P05-manifest-templates.yaml
│   └── P05-cleanup-policy.yaml
├── reports/
│   ├── P05-discovery-report.md
│   ├── P05-usage-intelligence-report.md
│   └── P05-cleanup-recommendations.md
└── tracking/
    └── P05-progress-tracker.json
```

---

## 🚀 Next Steps

**To execute this plan:**
```bash
python3 -m src.main "execute phase P05 of cortex5-remediation epic - scripts utilities toolkit consolidation" --format markdown
```

**Dependencies:**
- Phase P02 complete (Master Orchestrator operational)
- Phase P03 complete (Investigation system operational)
- `cortex-toolkit/` infrastructure verified

**Estimated Duration:** 16 hours (2 days)  
**Priority:** Medium (enhances developer experience, not blocking)

---

**Created By:** CORTEX Planning System v5  
**Date:** January 6, 2026  
**Review Status:** Pending stakeholder approval
