# GUIDED Orchestrators Assessment Plan

**Plan Type:** Assessment + Selective Migration  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.4)  
**Status:** ⏸️ NOT STARTED  
**Estimated Duration:** 9 days (3d assessment + 6d selective migrations)

---

## 📋 Overview

This plan assesses FOUR GUIDED orchestrators (TDD, Debug, Sanitization, Refinement) to determine which should convert to AUTONOMOUS and which should remain GUIDED.

### Decision Criteria

1. **Complexity of Operations** - Does it require complex AST parsing, multi-phase analysis?
2. **Workflow Simplicity** - Can it be expressed as pure Python logic?
3. **State Management Needs** - Does it require transactional rollback?
4. **User Interaction Requirements** - Does it benefit from approval workflows?
5. **Maintenance Cost** - Is Python easier to maintain than manifest instructions?

---

## 🎯 Preliminary Assessments

| Orchestrator | Current Type | Complexity | Preliminary Recommendation |
|--------------|--------------|------------|----------------------------|
| **TDD Mastery** | 📋 GUIDED | HIGH | 🔴 **DISCUSSION REQUIRED** |
| **Debug** | 📋 GUIDED | MEDIUM-HIGH | 🟡 **LIKELY AUTONOMOUS** |
| **Sanitization** | 📋 GUIDED | HIGH | 🟢 **AUTONOMOUS** (High Confidence) |
| **Refinement** | 📋 GUIDED | MEDIUM | 🔵 **REMAIN GUIDED** (High Confidence) |

---

## ⚠️ CRITICAL: TDD Orchestrator

**TDD orchestrator enhancement requires stakeholder design discussion BEFORE proceeding.**

**Trade-Offs to Discuss:**
- **AUTONOMOUS:** Better state tracking, transactional execution, Master Orch integration, BUT complex REFACTOR automation
- **GUIDED:** Simpler manifest updates, tool call sequences work well, BUT no state persistence
- **HYBRID:** Autonomous test execution + GUIDED refinement (best of both worlds, more complex architecture)

**Deliverable:** Phase 1 creates `artifacts/tdd-stakeholder-discussion.md` with trade-off analysis and three options.

---

## 📁 Plan Structure

```
guided-orchestrators-assessment/
├── 00-master-plan.md             # This file's companion (detailed phase breakdown)
├── README.md                      # This file (quick reference)
├── context/                       # Analysis documents
│   ├── tdd-orchestrator-analysis.md
│   ├── debug-orchestrator-analysis.md
│   ├── sanitization-orchestrator-analysis.md
│   └── refinement-orchestrator-analysis.md
├── artifacts/                     # Recommendations & deliverables
│   ├── autonomous-vs-guided-decision-matrix.md
│   ├── orchestrator-evaluation-template.md
│   ├── stakeholder-communication-plan.md
│   ├── tdd-autonomous-feasibility.md
│   ├── tdd-stakeholder-discussion.md (⚠️ CRITICAL)
│   ├── debug-autonomous-recommendation.md
│   ├── sanitization-autonomous-recommendation.md
│   ├── refinement-remain-guided-recommendation.md
│   ├── consolidated-recommendations.md
│   └── migration-roadmap.md
├── reports/                       # Assessment reports
│   └── assessment-completion-report.md (generated at end)
└── tracking/                      # Progress tracking
    └── progress-tracker.json
```

---

## 🚀 Getting Started

### Phase 0: Assessment Framework (1 day)
Create decision matrix, evaluation template, stakeholder communication plan

### Phase 1-4: Orchestrator Analysis (2.5 days)
Analyze TDD, Debug, Sanitization, Refinement against decision criteria

### Phase 5: Strategic Recommendations (0.5 days)
Consolidate findings, create migration roadmap

### Phase 6: Selective Migrations (5 days)
Execute approved migrations:
- **Sanitization v2** (2 days) - HIGH confidence autonomous conversion
- **Debug v2** (3 days) - HIGH confidence autonomous conversion
- **Refinement Enhancement** (0.5 days) - Update manifest for Master Orch routing
- **TDD Migration** (TBD) - Pending stakeholder discussion

---

## 📊 Expected Outcomes

### Assessment Phase (Phases 0-5)
- ✅ All 4 orchestrators analyzed
- ✅ Decision matrix established
- ✅ TDD stakeholder discussion document prepared
- ✅ Debug autonomous conversion recommended (HIGH confidence)
- ✅ Sanitization autonomous conversion recommended (HIGH confidence)
- ✅ Refinement GUIDED retention recommended (HIGH confidence)
- ✅ Migration roadmap created

### Migration Phase (Phase 6)
- ✅ Sanitization Orchestrator v2 implemented (if approved)
- ✅ Debug Orchestrator v2 implemented (if approved)
- ✅ Refinement manifest enhanced for Master Orch routing
- ⏸️ TDD migration (pending stakeholder decision)

---

## 🔗 Integration Points

### Master Orchestrator
All autonomous conversions will integrate with Master Orchestrator routing:
- **Sanitization v2:** Pattern `^(sanitize|sanitization|make generic).*$`
- **Debug v2:** Pattern `^(debug|fix error|analyze failure).*$`
- **Refinement (enhanced):** Pattern `^(refine|improve|enhance).*$` (remains GUIDED)

### BaseOrchestrator v4.1
Autonomous conversions inherit from BaseOrchestrator v4.1:
- Config-driven execution (YAML manifests)
- Template rendering (Jinja2)
- State persistence (PlanningStateDB)
- Rollback capabilities

### Planning System v5
Migration plans use Planning v5 structure:
- 4 subfolders: `context/`, `artifacts/`, `reports/`, `tracking/`
- Master plan with visual progress tracker
- JSON progress metadata
- Checkpoint creation

---

## 📝 Notes

- **Assessment First, Migration Second:** Phase 0-5 analyze and recommend. Phase 6 executes approved migrations.
- **TDD Critical Decision:** Do NOT enhance TDD orchestrator until stakeholder discussion complete.
- **High Confidence Recommendations:** Debug and Sanitization have HIGH confidence for autonomous conversion.
- **Remain GUIDED:** Refinement benefits from current GUIDED approach (analysis phases work well with tool call sequences).
- **Selective Execution:** Phase 6 migrations are conditional on approval.

---

**Quick Reference:**
- **Master Plan:** `00-master-plan.md` (detailed phase breakdown)
- **Progress Tracker:** `tracking/progress-tracker.json` (machine-readable metadata)
- **TDD Discussion:** `artifacts/tdd-stakeholder-discussion.md` (created in Phase 1)
- **Consolidated Recommendations:** `artifacts/consolidated-recommendations.md` (created in Phase 5)
