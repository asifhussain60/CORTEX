# 🔍 Feature Discovery Module - Sub-Plan

**Purpose:** Auto-discover new orchestrators, register in cortex-operations.yaml, run baseline scan  
**Complexity:** LOW (1 existing file, no consolidation)  
**LOC:** 377 (existing implementation - already complete)  
**Test Strategy:** SMOKE TEST ONLY (2 tests: initialization + metadata extraction)

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Next:** [DevOps Orchestrator Plan](02-devops-orchestrator-plan.md)
- **Checklist:** [Feature Discovery Baseline Scan Checklist](feature-discovery-baseline-scan-checklist.md)

---

## 1️⃣ Existing State (Current Implementation)

### Current Files

| File | LOC | Purpose | Status |
|------|-----|---------|--------|
| `src/operations/modules/epm/auto_registration_orchestrator.py` | 377 | Auto-registration orchestrator | ✅ COMPLETE |

**Total LOC:** 377 lines (already implemented)

### Current Feature Discovery Workflow

**1. Discovery Scan**
- Scan `src/orchestrators/` directory
- Identify Python files with `Orchestrator` class
- Extract metadata from docstrings
- Parse natural language triggers

**2. Metadata Extraction**
- Operation name (from class name)
- Display name (from docstring)
- Description (from docstring)
- Category (inferred from directory structure)
- Natural language triggers (from docstring patterns)
- Module path (file location)

**3. Registration Process**
- Generate YAML entry for cortex-operations.yaml
- Validate YAML syntax
- Dry-run preview (show what would be added)
- Approval workflow (manual confirmation)
- Write to cortex-operations.yaml

**4. Baseline Scan (NEW - CRITICAL)**
- Scan entire CORTEX codebase for orchestrators
- Identify any orchestrators NOT in orchestration-master-plan.md
- Generate discovery report with LOC counts
- Update master plan metrics (71+ orchestrators → actual count)
- This is the PREREQUISITE step before implementation begins

### Current Issues & Pain Points

**Fragmentation:**
- Discovery scan is manual (not automated)
- No integration with System Maintenance
- Baseline scan checklist exists but not integrated

**Reliability:**
- No periodic re-scan to catch new orchestrators
- Discovery report not persisted
- No validation that master plan is up-to-date

**Scalability:**
- Single-project focus (no multi-tenant support)
- No filtering by deployment tier (admin vs user operations)
- No orchestrator dependency detection

---

## 2️⃣ New Structure

### Target Architecture

```
src/operations/modules/epm/
├── __init__.py
├── auto_registration_orchestrator.py   # Main orchestrator (377 LOC - EXISTING)
└── baseline_scanner.py                 # NEW: Baseline scan utility (150 LOC)
```

**Total Target LOC:** 527 lines (40% expansion from 377)

### Component Responsibilities

**Auto-Registration Orchestrator (`auto_registration_orchestrator.py` - 377 LOC)**
- ✅ EXISTING: Metadata extraction from docstrings
- ✅ EXISTING: Natural language trigger generation
- ✅ EXISTING: YAML entry creation
- ✅ EXISTING: Dry-run preview
- ✅ EXISTING: Approval workflow
- ✅ EXISTING: Write to cortex-operations.yaml

**Baseline Scanner (`baseline_scanner.py` - 150 LOC) - NEW**
- Scan entire CORTEX codebase for orchestrators
- Compare discovered orchestrators vs master plan
- Generate discovery report (LOC, categories, directories)
- Persist report to `cortex-brain/discovery-reports/`
- Validate master plan completeness

---

## 3️⃣ State Machine Design

### Feature Discovery Workflow States

**NOTE:** Feature Discovery is NOT a state machine orchestrator. It's a utility module that runs as part of System Maintenance or on-demand.

**Workflow Phases:**

```
1. SCAN_CODEBASE
   ↓ (scan src/orchestrators/, src/operations/, src/cortex_agents/)
2. EXTRACT_METADATA
   ↓ (parse docstrings, identify triggers)
3. GENERATE_YAML_ENTRIES
   ↓ (format YAML blocks)
4. DRY_RUN_PREVIEW
   ↓ (show what would be added)
5. APPROVAL_GATE
   ↓ (manual confirmation required)
6. WRITE_TO_YAML
   ↓ (persist to cortex-operations.yaml)
7. COMPLETED
```

**Baseline Scan Phases:**

```
1. FULL_CODEBASE_SCAN
   ↓ (find ALL orchestrators in CORTEX)
2. COMPARE_WITH_MASTER_PLAN
   ↓ (identify missing orchestrators)
3. GENERATE_DISCOVERY_REPORT
   ↓ (LOC counts, categories, directories)
4. PERSIST_REPORT
   ↓ (save to cortex-brain/discovery-reports/)
5. VALIDATION_CHECK
   ↓ (verify master plan completeness)
6. COMPLETED
```

---

## 4️⃣ Integration Points

### System Maintenance Integration

**System Maintenance triggers periodic discovery:**
```python
# Phase 3: Optimize (includes feature discovery)
system_maintenance.execute_phase("OPTIMIZE", {
    "feature_discovery": True,
    "scan_interval": "weekly"
})
```

**Baseline Scan is ONE-TIME (before implementation):**
```python
# Phase 0: Baseline scan (run ONCE before starting orchestrator consolidation)
baseline_scanner.run_baseline_scan(
    output_dir="cortex-brain/discovery-reports",
    compare_with_master_plan=True,
    persist_report=True
)
```

### Intelligence Orchestrator Integration

**Intelligence uses discovery metadata:**
```python
# Intelligence orchestrator suggests new features based on discovery
intelligence_orchestrator.suggest_enhancements({
    "discovered_orchestrators": discovery_report.orchestrators,
    "consolidation_opportunities": discovery_report.duplicates
})
```

---

## 5️⃣ Implementation Details

### Auto-Registration Orchestrator Component

**Purpose:** Extract metadata and register in cortex-operations.yaml

**Key Methods (EXISTING):**
```python
class AutoRegistrationOrchestrator:
    def extract_natural_language_triggers(
        self,
        docstring: str,
        operation_name: str
    ) -> List[str]:
        """Extract natural language triggers from docstring."""
        
    def generate_yaml_entry(
        self,
        entry: RegistrationEntry
    ) -> str:
        """Generate YAML entry for cortex-operations.yaml."""
        
    def register_operation(
        self,
        entry: RegistrationEntry,
        dry_run: bool = True
    ) -> bool:
        """Register operation in cortex-operations.yaml."""
```

**Metadata Extraction Patterns:**
- **Commands:** `Commands: <command list>`
- **Usage:** `Usage: <usage example>`
- **Triggers:** `Triggers: <trigger list>`
- **Description:** First paragraph of docstring

### Baseline Scanner Component (NEW)

**Purpose:** Scan entire CORTEX codebase and generate discovery report

**Key Methods:**
```python
class BaselineScanner:
    def scan_codebase(
        self,
        directories: List[str] = None
    ) -> Dict[str, Any]:
        """Scan CORTEX codebase for all orchestrators."""
        
    def compare_with_master_plan(
        self,
        discovered: List[str],
        master_plan_path: str
    ) -> Dict[str, Any]:
        """Compare discovered orchestrators with master plan."""
        
    def generate_discovery_report(
        self,
        scan_results: Dict[str, Any],
        comparison: Dict[str, Any]
    ) -> str:
        """Generate markdown discovery report."""
        
    def persist_report(
        self,
        report_content: str,
        output_dir: str
    ) -> str:
        """Save discovery report to cortex-brain/discovery-reports/."""
```

**Discovery Report Structure:**
```markdown
# Feature Discovery Baseline Scan Report

**Date:** December 10, 2025  
**Scan Duration:** 2.3 seconds  
**Directories Scanned:** src/orchestrators/, src/operations/, src/cortex_agents/

## Summary

- **Total Orchestrators Found:** 73
- **Master Plan Count:** 71+
- **Missing from Master Plan:** 2
- **Consolidation Opportunities:** 5

## Discovered Orchestrators

| Name | LOC | Directory | Category | Status |
|------|-----|-----------|----------|--------|
| brain_tuning_orchestrator | 425 | src/orchestrators/ | Intelligence | Not in master plan |
| ... | ... | ... | ... | ... |

## Missing Orchestrators (NOT in Master Plan)

1. **brain_tuning_orchestrator** (425 LOC) - src/orchestrators/brain_tuning_orchestrator.py
2. **feature_toggle_orchestrator** (312 LOC) - src/operations/feature_toggle_orchestrator.py

## Consolidation Opportunities

- **Dashboard Files:** 5 files (4,263 LOC) → Consolidate to 1 file (1,800 LOC)
- **Git Operations:** 2 files (1,102 LOC) → Consolidate to 1 file (700 LOC)

## Recommendations

1. Update orchestration-master-plan.md to include missing orchestrators
2. Review consolidation opportunities for Phase 1-4 planning
3. Re-run baseline scan after master plan updates
```

---

## 6️⃣ Configuration

### Feature Discovery Configuration

**File:** `cortex-brain/config/feature-discovery-config.yaml`

```yaml
name: feature_discovery
version: 1.0.0

scan_directories:
  - src/orchestrators/
  - src/operations/
  - src/cortex_agents/
  - src/operations/modules/

exclude_patterns:
  - "**/__pycache__/**"
  - "**/test_*.py"
  - "**/*.pyc"

metadata_extraction:
  docstring_patterns:
    - "Commands?:\\s*\\n((?:[-*]\\s*.+\\n?)+)"
    - "Usage:\\s*`([^`]+)`"
    - "Triggers?:\\s*\\n((?:[-*]\\s*.+\\n?)+)"
  
  category_mapping:
    orchestrators: "Orchestration"
    operations: "Operations"
    cortex_agents: "Intelligence"
    modules: "Utilities"

registration:
  approval_required: true
  dry_run_default: true
  backup_operations_yaml: true

baseline_scan:
  output_dir: "cortex-brain/discovery-reports"
  compare_with_master_plan: true
  persist_report: true
  master_plan_path: "cortex-brain/documents/planning/orchestration-master-plan.md"
```

---

## 7️⃣ Testing Strategy

### Smoke Tests (2 tests)

**Test 1: Initialization**
```python
def test_auto_registration_orchestrator_initialization():
    """Verify auto-registration orchestrator initializes correctly."""
    project_root = Path("d:/PROJECTS/CORTEX")
    orchestrator = AutoRegistrationOrchestrator(project_root)
    
    assert orchestrator is not None
    assert orchestrator.operations_yaml.exists()
```

**Test 2: Metadata Extraction**
```python
def test_extract_metadata_from_docstring():
    """Verify metadata extraction from docstring."""
    orchestrator = AutoRegistrationOrchestrator()
    
    docstring = """
    Brain Tuning Orchestrator
    
    Commands:
    - tune brain
    - optimize cognitive
    
    Usage: `tune brain --depth=deep`
    """
    
    triggers = orchestrator.extract_natural_language_triggers(
        docstring,
        "brain_tuning"
    )
    
    assert "brain tuning" in triggers
    assert "tune brain" in triggers
    assert "optimize cognitive" in triggers
```

**Why only 2 tests?**
- Feature Discovery is a utility module (not workflow orchestrator)
- Smoke tests validate initialization and core metadata extraction
- Comprehensive tests would be 10+ tests (excessive for utility validation)

---

## 8️⃣ Migration Strategy

### Phase 0: Baseline Scan (Week 0 - DAY 1)

**CRITICAL:** This is the PREREQUISITE step before all other work.

1. **Run Baseline Scan** (using checklist)
   - Execute: `python -m src.operations.modules.epm.baseline_scanner`
   - Scan entire CORTEX codebase
   - Generate discovery report
   - Persist to `cortex-brain/discovery-reports/baseline-scan-YYYY-MM-DD.md`

2. **Review Discovery Report**
   - Identify orchestrators NOT in master plan
   - Validate LOC counts (is it really 71+ orchestrators or more?)
   - Identify consolidation opportunities

3. **Update Master Plan**
   - Add missing orchestrators to orchestration-master-plan.md
   - Update metrics (71+ → actual count)
   - Adjust Phase 1-4 consolidation targets

4. **Commit Baseline Scan Results**
   - Git commit: "Phase 0 baseline scan complete - [X] orchestrators discovered"
   - Push to cortex3-orchestration branch

### Phase 1-4: Integration (Ongoing)

- Feature Discovery runs periodically during System Maintenance
- New orchestrators auto-discovered and proposed for registration
- Manual approval required before adding to cortex-operations.yaml

---

## 9️⃣ Extensibility Analysis

**Extensibility Rating: ⭐⭐⭐⭐ (4/5) - Highly extensible**

### Why Highly Extensible?

**1. Metadata Patterns**
- Custom docstring patterns can be added
- Example: Add support for `@triggers` decorator

**2. Category Mapping**
- New categories can be added to configuration
- Example: Add "Security" category for security-focused orchestrators

**3. Approval Workflow**
- Custom approval logic (e.g., auto-approve low-risk operations)
- Slack/Teams integration for approval notifications

**4. Discovery Filters**
- Custom filters for orchestrator discovery
- Example: Only discover orchestrators with >100 LOC

### Extension Example: Custom Metadata Pattern

```python
# Add custom metadata pattern
class AutoRegistrationOrchestrator:
    def extract_complexity_level(self, docstring: str) -> str:
        """Extract complexity level from docstring."""
        patterns = [
            r'Complexity:\s*(HIGH|MEDIUM|LOW)',
            r'@complexity\s*(HIGH|MEDIUM|LOW)'
        ]
        for pattern in patterns:
            match = re.search(pattern, docstring, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return "MEDIUM"  # default
```

---

## 🔟 Success Criteria

**Completion Checklist:**
- [ ] Baseline scan executed successfully
- [ ] Discovery report generated and persisted
- [ ] Master plan updated with baseline scan findings
- [ ] All discovered orchestrators documented
- [ ] Consolidation targets validated
- [ ] Smoke tests passing (2/2 - 100% success rate)
- [ ] Git commit with baseline scan results
- [ ] Ready to begin Phase 1 Core Infrastructure

**Metrics:**
- Baseline scan duration: < 5 minutes
- Discovery report completeness: 100% (all orchestrators found)
- Master plan accuracy: 100% (no missing orchestrators)

---

## 1️⃣1️⃣ Baseline Scan Execution

### Using the Checklist

**File:** [feature-discovery-baseline-scan-checklist.md](feature-discovery-baseline-scan-checklist.md)

**Steps:**
1. Set CORTEX project root
2. Run baseline scanner
3. Review discovery report
4. Update master plan
5. Commit results
6. Proceed to Phase 1

**Estimated Time:** 30-60 minutes (including master plan updates)

---

## 1️⃣2️⃣ Related Documents

- [Orchestration Master Plan](../orchestration-master-plan.md)
- [Feature Discovery Baseline Scan Checklist](feature-discovery-baseline-scan-checklist.md)
- [DevOps Orchestrator Plan](02-devops-orchestrator-plan.md)
- [System Maintenance Orchestrator](../../implementation-guides/system-maintenance-orchestrator.md)

---

**Next Steps:** Run baseline scan immediately, then create remaining Phase 1-4 sub-plans.
