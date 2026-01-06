# Phase 4: Response Templates & Accessibility

**Phase ID:** P004 | **Duration:** 1.5 weeks | **Status:** ⏸️ NOT STARTED | **Priority:** 🟡 MEDIUM

---

## 🎯 Phase Objective

Implement WCAG AA-compliant response templates for autonomous orchestrators with progress bars, concise mode, and accessibility rules.

---

## 📦 Features Included

| Feature ID | Name | Status | Dependencies | Priority |
|------------|------|--------|--------------|----------|
| **F005** | Response Templates | ⏸️ Pending | F002 | 🟡 MEDIUM |

---

## ✅ Acceptance Criteria

- [ ] `autonomous_execution_progress` template with progress bars
- [ ] Phase-level progress updates (not per-task narration)
- [ ] Concise mode by default (3-line format)
- [ ] Verbose mode available on request
- [ ] Max 40-line summary constraint
- [ ] WCAG AA cognitive load compliance
- [ ] No verbose narration ("Now I'll...", "Perfect!", etc.)
- [ ] Template rendering system for all 8 orchestrators
- [ ] Accessibility rules enforced in templates

---

## 🔗 Dependencies

**Requires:**
- Phase 0 (Foundation)
- F002 (Governance Rules) - accessibility rules defined

**Enables:**
- Phase 5 (Continuation System) - progress templates
- Phase 6 (Plan Viewer) - template-based rendering

---

## 📋 Implementation Tasks

### Week 1: Template System
1. **Core Template Engine**
   - Create `TemplateRenderer` class
   - Load templates from `response-templates-v4.yaml`
   - Variable substitution engine
   - Conditional rendering logic

2. **Autonomous Execution Progress Template**
   - Design progress bar component
   - Phase-level update format
   - Completion summary format
   - Error/warning formatting

3. **Concise Mode (Default)**
   ```markdown
   ## 🛡️ {Orchestrator} → Invoking via terminal
   
   **Pattern:** `{regex}` | **Confidence:** 1.0 | **Mode:** {mode}
   
   ✅ **INVOKING PYTHON** - `python3 -m src.main "{request}"`
   ```

4. **Verbose Mode (On Request)**
   - Detailed transformation logs
   - Per-task narration
   - Diagnostic information
   - Extended summaries

### Week 2: Integration & Accessibility
1. **Accessibility Rules Implementation**
   - COGNITIVE_LOAD: 1 update per phase
   - SILENT_TASKS: Hide task completion narration
   - CONCISE_DEFAULT: Use concise by default
   - PROGRESS_FREQUENCY: Phase start/end only
   - SUMMARY_CAP: ≤40 lines
   - NO_NARRATION: Eliminate commentary

2. **Orchestrator Integration**
   - Update all 8 orchestrators to use templates
   - Planning orchestrator
   - ADO orchestrator
   - Vacuum orchestrator
   - Cleanup orchestrator
   - Investigation orchestrator
   - Sanitization orchestrator
   - Maintenance orchestrator
   - Refinement orchestrator

3. **Testing**
   - Template rendering tests (10 tests)
   - Accessibility validation (6 tests)
   - Integration tests (8 orchestrators)

---

## 🧪 Testing Requirements

- **Unit Tests:** 10 tests (template rendering)
- **Accessibility Tests:** 6 tests (WCAG AA compliance)
- **Integration Tests:** 8 tests (1 per orchestrator)
- **Coverage Target:** ≥85%

---

## 📈 Success Metrics

- **Cognitive Load Reduction:** 60% fewer update messages
- **Summary Length:** ≤40 lines (100% compliance)
- **Narration Elimination:** 0 commentary phrases
- **WCAG AA Compliance:** 100%
- **Template Coverage:** 8/8 orchestrators

---

## 🔍 Template Examples

### Concise Mode (Default)
```markdown
## 🛡️ Planning → Autonomous Execution

**Phase 1/5:** Foundation ████████░░ 80% ⚡ IN PROGRESS

✅ Requirements compilation complete
✅ Gap analysis documented
🔄 Feature design in progress...
```

### Progress Bar Component
```
Overall Progress: ███████░░░░░░░░░░░ 35% ⚡ IN PROGRESS
Phase 2/8: Goal Inheritance ██████████ 100% ✅ COMPLETE
Phase 3/8: TDD Harness ████░░░░░░ 40% ⚡ IN PROGRESS
```

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Template maintenance overhead | 🟢 LOW | Centralized YAML + versioning |
| Accessibility rule violations | 🟡 MEDIUM | Automated validation + CI checks |
| Verbose mode complexity | 🟢 LOW | Separate template sets |

---

## ♿ Accessibility Rules Reference

| Rule | Enforcement |
|------|-------------|
| **COGNITIVE_LOAD** | 1 update per phase (not per task) |
| **SILENT_TASKS** | Task narration hidden from user |
| **CONCISE_DEFAULT** | 3-line format unless requested |
| **PROGRESS_FREQUENCY** | Phase start, completion, overall only |
| **SUMMARY_CAP** | ≤40 lines (readability) |
| **NO_NARRATION** | No "Now I'll...", "Perfect!", etc. |

---

## 🚀 Next Phase

**Phase 5:** Cross-Session Continuation (F006)

**Handoff Criteria:**
- All templates implemented
- WCAG AA compliance validated
- 8 orchestrators integrated
- Accessibility tests passing
