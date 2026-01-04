# 🎯 Sub-Plan 10: Enhanced Acceptance Validation System

**Plan ID:** acceptance-validation-system  
**Parent:** CORTEX-5.0  
**Duration:** 1 week  
**Status:** ⏳ NOT STARTED  
**Created:** January 4, 2026

---

## 📊 Progress

**Overall:** `░░░░░░░░░░` **0%** ⏳ NOT STARTED

---

## 🎯 Objective

Implement comprehensive 3-tier checkpoint validation system with hybrid test harnesses, semantic icon usage, and interactive HTML viewer for acceptance criteria tracking.

**Gaps Addressed:**
1. No automated checkpoint validation after sub-plans
2. Acceptance criteria lack test coverage mapping
3. DoD/DoR checkmarks create false completion impression
4. No visual dashboard for non-technical stakeholders
5. Manual validation is error-prone and incomplete

**Success Criteria:**
- ✅ 3-tier checkpoint system operational (L1: Task, L2: Phase, L3: Master)
- ✅ 52 automated tests + 39 validation scripts implemented
- ✅ Icon semantics standardized (✅ only for verified completion)
- ✅ HTML viewer renders YAML acceptance criteria interactively
- ✅ All 130 CORTEX-5.0 criteria mapped to validation method
- ✅ Integration with plan orchestrator for automated checkpoints

---

## 🏗️ Architecture

### 3-Tier Checkpoint System

```
┌─────────────────────────────────────────────────────────────┐
│ L3: MASTER VALIDATION (End of Plan)                         │
│ Scope: All 130 acceptance criteria                          │
│ Frequency: Once per major release                           │
│ Blocker: Production deployment                              │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ (blocks if fail)
┌─────────────────────────────────────────────────────────────┐
│ L2: PHASE EXIT VALIDATION (End of Sub-Plan)                 │
│ Scope: Phase criteria + Parent plan subset                  │
│ Frequency: After each of 10 sub-plans                       │
│ Blocker: Dependent sub-plans                                │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ (blocks if fail)
┌─────────────────────────────────────────────────────────────┐
│ L1: TASK COMPLETION VALIDATION (End of Task)                │
│ Scope: Task-specific DoD (5-10 items)                       │
│ Frequency: After each task in implementation guide          │
│ Blocker: Next task in same phase                            │
└─────────────────────────────────────────────────────────────┘
```

**Rationale for 3 Tiers:**
- **L1 (Task):** Catches micro failures early (code quality, unit tests)
- **L2 (Phase):** Catches integration failures (cross-component compatibility)
- **L3 (Master):** Catches architectural failures (system-wide compliance)

Single-tier validation creates false confidence - components can pass locally but fail holistically.

---

## 📋 Hybrid Validation System

**Problem:** Not all acceptance criteria are testable via traditional unit tests.

**Solution:** 4-category hybrid validation approach.

### Category Breakdown (130 Total Criteria)

| Category | Count | Method | Automation | Example |
|----------|-------|--------|------------|---------|
| **Functional** | 52 (40%) | Automated tests | 100% | "Routing accuracy ≥95%" → `test_routing_accuracy()` |
| **Architectural** | 39 (30%) | AST + Pattern validation | 100% | "Zero hybrid ambiguity" → AST scan for manifest directives |
| **Experiential** | 26 (20%) | Human checklist | 0% | "Documentation clear" → Manual review by 2 reviewers |
| **Performance** | 13 (10%) | Benchmark harnesses | 100% | "Query latency <30ms" → Performance test suite |

**Total Automation:** 104/130 (80%)  
**Manual Validation:** 26/130 (20%)

**Cost-Benefit Analysis:**

| Approach | Test Count | Automation | Dev Velocity Impact | Confidence Level |
|----------|------------|------------|---------------------|------------------|
| **100% Automated Tests** | 130 | 100% | -40% | Medium (false positives) |
| **Hybrid System** (Proposed) | 52 tests + 39 scripts + 26 manual | 80% | -20% | High (balanced) |
| **Manual Only** | 0 | 0% | No impact | Low (human error) |

**Winner:** Hybrid System - Best balance of accuracy, efficiency, and confidence.

---

## 🎨 Icon Semantic System

**Problem:** Current DoD/DoR sections show ✅ icons for incomplete work, creating false impression.

**Solution:** Strict icon semantics with clear state mapping.

### Icon Definition Table

| State | Icon | Usage Context | Example |
|-------|------|---------------|---------|
| **Not Started** | `⬜` | DoD/DoR items not begun | `⬜ All tests pass` |
| **In Progress** | `🔄` | Active work | `🔄 Writing tests` |
| **Complete** | `✅` | **ONLY verified completion** | `✅ All 52 tests passing` |
| **Blocked** | `⏸️` | Cannot start (dependencies) | `⏸️ Waiting for Sub-Plan 03` |
| **Failed** | `❌` | Validation failed | `❌ Test coverage 40% (target 80%)` |
| **Skipped** | `⏭️` | Intentionally omitted | `⏭️ Integration tests (out of scope)` |

### Implementation Schema

```yaml
# cortex-brain/config/icon-semantics.yaml
icon_system:
  version: "1.0"
  rules:
    green_checkmark:
      unicode: "✅"
      usage: "ONLY for verified completed work"
      forbidden_contexts:
        - "DoD items that are not complete"
        - "DoR items before work starts"
        - "Placeholder sections"
      allowed_contexts:
        - "Completed tasks with proof"
        - "Passing tests"
        - "Validated deliverables"
    
    empty_checkbox:
      unicode: "⬜"
      usage: "Work not started"
      contexts:
        - "DoD items in new sub-plans"
        - "Future tasks"
        - "Pending validations"
    
    in_progress:
      unicode: "🔄"
      usage: "Active work underway"
      contexts:
        - "Current phase"
        - "Tasks being implemented"
        - "Tests being written"
```

### Enforcement

**Automated Linting:**
```python
# src/validators/icon_validator.py
def validate_icon_usage(markdown_file: Path) -> List[ValidationError]:
    """
    Scan markdown for improper ✅ usage.
    
    Rules:
    - ✅ in DoD section → ERROR if sub-plan status != 'complete'
    - ✅ in DoR section → ERROR (DoR is pre-work)
    - ✅ without completion proof → WARNING
    """
```

**Pre-Commit Hook:**
```bash
# .git/hooks/pre-commit
python src/validators/icon_validator.py cortex-brain/documents/planning/active/
```

---

## 🌐 Interactive HTML Viewer

**Problem:** YAML acceptance criteria are:
- Not accessible to non-technical stakeholders
- Difficult to visualize progress
- Hard to navigate on mobile devices
- Lack real-time status updates

**Solution:** Standalone HTML viewer with embedded YAML parser.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│ acceptance-criteria.yaml (Source of Truth)               │
└──────────────────────────────────────────────────────────┘
                    │
                    │ (reads via fetch API)
                    ▼
┌──────────────────────────────────────────────────────────┐
│ cortex-acceptance-viewer.html (Standalone)               │
│                                                           │
│ [Embedded Libraries]                                      │
│ - js-yaml (YAML parsing)                                  │
│ - Chart.js (progress visualization)                       │
│ - Tailwind CSS (styling)                                  │
│                                                           │
│ [Features]                                                │
│ ✅ Real-time progress bars                               │
│ ✅ Filterable criteria list                              │
│ ✅ Test coverage mapping                                 │
│ ✅ Checkpoint validation status                          │
│ ✅ Export to PDF/PNG                                      │
│ ✅ Mobile responsive                                      │
│ ✅ Dark mode support                                      │
│ ✅ Keyboard navigation (WCAG AA)                          │
└──────────────────────────────────────────────────────────┘
```

### Key Features

#### 1. Visual Progress Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ CORTEX-5.0 Acceptance Criteria Dashboard               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Overall Progress:  ████████░░ 80% (104/130)            │
│                                                         │
│ By Category:                                            │
│ Functional       ████████░░  40/52  (77%)  [52 tests]  │
│ Architectural    ██████████  39/39 (100%)  [39 scripts]│
│ Experiential     ████░░░░░░  10/26  (38%)  [manual]    │
│ Performance      ██████████  13/13 (100%)  [13 tests]  │
│                                                         │
│ Checkpoint Status:                                      │
│ L1 (Task)        ✅ 145/145 passing                    │
│ L2 (Phase)       🔄 7/10 complete                      │
│ L3 (Master)      ⏸️ Blocked (Sub-Plans 08-09 pending)  │
└─────────────────────────────────────────────────────────┘
```

#### 2. Interactive Criteria List
```
┌─────────────────────────────────────────────────────────┐
│ [Filter: All ▼] [Category: Functional ▼] [Search: ___]│
├─────────────────────────────────────────────────────────┤
│ ✅ Master Orchestrator routing accuracy ≥95%           │
│    Test: tests/orchestrators/test_master_routing.py:42 │
│    Last Run: 2026-01-04 10:30 ✅ PASS                  │
│    Coverage: 12 test cases                             │
│                                                         │
│ 🔄 Token efficiency ≥99.6% (cross-session context)    │
│    Test: tests/middleware/test_context_injection.py:28 │
│    Last Run: 2026-01-04 10:28 🔄 IN PROGRESS          │
│    Coverage: 8/10 test cases                           │
│                                                         │
│ ⬜ Documentation clarity validated by 2 reviewers      │
│    Method: Manual checklist                            │
│    Status: ⏳ NOT STARTED                              │
│    Assigned: [Reviewer 1] [Reviewer 2]                 │
└─────────────────────────────────────────────────────────┘
```

#### 3. Test Coverage Mapping
- Click any criteria → Opens test file in editor
- Hover → Shows test summary
- Badge shows pass/fail/pending status
- Last run timestamp

#### 4. Export Options
- **PDF Report** - For stakeholders
- **PNG Screenshot** - For presentations
- **Markdown Summary** - For documentation
- **CSV Export** - For spreadsheet analysis

### Accessibility (WCAG AA Compliance)

```yaml
accessibility_features:
  screen_reader:
    - ARIA labels on all interactive elements
    - Semantic HTML5 structure
    - Alt text for visual progress bars
    - Keyboard shortcuts announced
  
  keyboard_navigation:
    - Tab order logical and predictable
    - "/" to focus search
    - "?" to show keyboard shortcuts
    - Arrow keys to navigate criteria
  
  visual:
    - Contrast ratio ≥4.5:1 (normal text)
    - Contrast ratio ≥3:1 (large text)
    - Icons paired with text labels
    - No information conveyed by color alone
  
  cognitive_load:
    - Progress bars show percentage + count
    - Filters clearly labeled
    - Simple, consistent layout
    - No auto-refresh (user-triggered)
```

---

## 📦 Implementation Plan

### Phase 1: Schema Design (1 day)

**Task 1.1:** Create `acceptance-criteria-schema.yaml`
- 3-tier checkpoint definitions
- Icon semantic rules
- Test mapping structure
- Validation method taxonomy

**Task 1.2:** Map 130 CORTEX-5.0 criteria to validation methods
- 52 Functional → Automated tests
- 39 Architectural → AST/Pattern scripts
- 26 Experiential → Manual checklists
- 13 Performance → Benchmark harnesses

**Deliverable:** 
```
cortex-brain/config/
├── acceptance-criteria-schema.yaml
├── acceptance-validation-mapping.yaml
└── icon-semantics.yaml
```

---

### Phase 2: Hybrid Test Harness (2 days)

**Task 2.1:** Functional Tests (52 tests)
```
tests/acceptance/functional/
├── test_routing_accuracy.py          # Master Orchestrator
├── test_token_efficiency.py          # Context Middleware
├── test_planning_structure.py        # Planning v5
├── test_state_management.py          # PlanningStateDB
└── ... (48 more tests)
```

**Task 2.2:** Architectural Validation Scripts (39 scripts)
```
src/validators/architectural/
├── hybrid_ambiguity_scanner.py       # AST-based
├── manifest_directive_checker.py     # Pattern matching
├── orchestrator_isolation_validator.py
└── ... (36 more scripts)
```

**Task 2.3:** Experiential Checklists (26 checklists)
```
cortex-brain/validation/manual/
├── documentation_review_checklist.yaml
├── ux_intuitiveness_checklist.yaml
├── stakeholder_approval_template.yaml
└── ... (23 more checklists)
```

**Task 2.4:** Performance Benchmarks (13 harnesses)
```
tests/acceptance/performance/
├── benchmark_query_latency.py
├── benchmark_routing_speed.py
├── benchmark_token_efficiency.py
└── ... (10 more benchmarks)
```

---

### Phase 3: Icon Standardization (1 day)

**Task 3.1:** Icon Validator Implementation
```python
# src/validators/icon_validator.py
class IconValidator:
    def validate_markdown_file(self, path: Path) -> ValidationReport
    def enforce_checkmark_rules(self, content: str) -> List[Error]
    def suggest_icon_corrections(self, errors: List[Error]) -> List[Suggestion]
```

**Task 3.2:** Batch Update All Sub-Plans
- Scan `cortex-brain/documents/planning/active/CORTEX-5.0/`
- Replace ✅ with ⬜ in incomplete DoD/DoR sections
- Update progress bars to use semantic icons
- Validate no false completion indicators

**Task 3.3:** Pre-Commit Hook Integration
```bash
#!/bin/bash
# .git/hooks/pre-commit
python src/validators/icon_validator.py --fix
git add -u  # Stage corrections
```

---

### Phase 4: HTML Viewer (2 days)

**Task 4.1:** Core Viewer Structure
```html
<!-- cortex-brain/viewers/acceptance-viewer.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CORTEX Acceptance Criteria Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">
</head>
<body>
    <div id="app">
        <!-- Vue.js app renders here -->
    </div>
    <script src="./acceptance-viewer.js"></script>
</body>
</html>
```

**Task 4.2:** YAML Parser Integration
```javascript
// acceptance-viewer.js
async function loadAcceptanceCriteria() {
    const response = await fetch('./acceptance-criteria.yaml');
    const yamlText = await response.text();
    const criteria = jsyaml.load(yamlText);
    return criteria;
}
```

**Task 4.3:** Interactive Components
- Progress bar visualizer
- Filterable criteria table
- Test coverage mapping
- Checkpoint status indicators
- Export functionality

**Task 4.4:** Accessibility Enhancements
- ARIA labels
- Keyboard navigation
- High contrast mode
- Screen reader testing

---

### Phase 5: Integration & Automation (1 day)

**Task 5.1:** Plan Orchestrator Integration
```python
# src/orchestrators/planning/checkpoint_validator.py
class CheckpointValidator:
    def run_l1_validation(self, task_id: str) -> ValidationResult
    def run_l2_validation(self, phase_id: str) -> ValidationResult
    def run_l3_validation(self) -> ValidationResult
    def block_on_failure(self, result: ValidationResult) -> None
```

**Task 5.2:** Automated Checkpoint Triggers
```python
# After task completion
@task_complete_hook
def validate_task(task: Task):
    result = CheckpointValidator().run_l1_validation(task.id)
    if not result.passed:
        raise ValidationError(f"L1 validation failed: {result.failures}")

# After phase completion
@phase_complete_hook
def validate_phase(phase: Phase):
    result = CheckpointValidator().run_l2_validation(phase.id)
    if not result.passed:
        block_dependent_phases(phase)
```

**Task 5.3:** Continuous Validation Dashboard
- Real-time status updates
- Slack/email notifications on failures
- Auto-refresh HTML viewer

---

## ✅ Definition of Done

**Phase 1: Schema Design**
- ⬜ `acceptance-criteria-schema.yaml` created
- ⬜ 130 criteria mapped to validation methods
- ⬜ Icon semantics documented

**Phase 2: Hybrid Test Harness**
- ⬜ 52 functional tests implemented and passing
- ⬜ 39 architectural validation scripts operational
- ⬜ 26 experiential checklists defined
- ⬜ 13 performance benchmarks passing

**Phase 3: Icon Standardization**
- ⬜ Icon validator implemented
- ⬜ All 10 sub-plans updated with correct icons
- ⬜ Pre-commit hook enforcing icon rules

**Phase 4: HTML Viewer**
- ⬜ Standalone HTML viewer functional
- ⬜ YAML parsing working
- ⬜ All features implemented (filter, search, export)
- ⬜ WCAG AA compliance validated

**Phase 5: Integration**
- ⬜ 3-tier checkpoints integrated in plan orchestrator
- ⬜ Automated blocking on validation failures
- ⬜ Dashboard shows real-time status

**Final Validation**
- ⬜ All 130 criteria have validation coverage
- ⬜ 80% automation achieved (104/130 automated)
- ⬜ Zero false completion indicators
- ⬜ HTML viewer accessible on all devices
- ⬜ Documentation complete

---

## 🔗 Dependencies

**Blocks:**
- Sub-Plan 09 (Final Validation) - L3 validation replaces manual gap analysis

**Blocked By:**
- Sub-Plan 00 (Test Coverage Sprint) - Need test infrastructure (50% complete)

---

## 📊 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Checkpoint Accuracy** | 95%+ | False positive rate <5% |
| **Automation Coverage** | 80%+ | 104/130 criteria automated |
| **Icon Compliance** | 100% | Zero ✅ on incomplete work |
| **HTML Viewer Usage** | 3+ exports/week | Adoption tracking |
| **Validation Speed** | <2 min/checkpoint | Performance benchmarks |
| **Accessibility Score** | WCAG AA | Lighthouse audit ≥90 |

---

## 💡 Alternatives Considered

### Alternative 1: 100% Automated Tests
**Rejected:** 40% dev velocity loss, high false positive rate, unmaintainable.

### Alternative 2: Manual Validation Only
**Rejected:** Human error-prone, not scalable, no CI/CD integration.

### Alternative 3: JSON Schema for Acceptance Criteria
**Rejected:** Less human-readable, no comments, inconsistent with CORTEX manifests.

### Alternative 4: Web Dashboard (Server-Based)
**Rejected:** Deployment complexity, requires backend, not portable.

---

## 📝 Notes

**Design Decisions:**
1. **3-tier validation** prevents false confidence at all levels
2. **Hybrid approach** balances automation with human judgment
3. **YAML format** maintains consistency with CORTEX architecture
4. **Standalone HTML** eliminates deployment barriers
5. **Semantic icons** eliminate ambiguity and build trust

**Risks:**
- Test maintenance burden (mitigated by focusing on critical 80%)
- Manual validation bottleneck (mitigated by clear checklists)
- HTML viewer adoption (mitigated by excellent UX)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
