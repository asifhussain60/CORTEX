# 🚨 Enforcement Rules

## 🎯 Core Philosophy

**MAINTENANCE = DIAGNOSE + AUTO-REPAIR + VERIFY**

| Phase | Action | Automation Level |
|-------|--------|------------------|
| **DIAGNOSE** | Identify gaps, errors, unwired components | ✅ Fully Automated |
| **AUTO-REPAIR** | Patch source code, wire components, fix issues | ✅ Fully Automated |
| **VERIFY** | Confirm 100% health, run tests, validate fixes | ✅ Fully Automated |

**⚠️ CRITICAL:** If maintenance only identifies problems but doesn't fix them, it's a BUG in the maintenance system itself.

---

## Rule 1: AUTO-REPAIR is MANDATORY

**❌ FORBIDDEN:**
- Generating reports without fixing issues
- Leaving wiring gaps after maintenance completes
- Requiring manual intervention for known issues
- Outputting "TODO: Fix manually" messages

**✅ REQUIRED:**
- Every detected issue has an auto-repair handler
- 100% wiring coverage achieved automatically
- All tests passing (100%) after maintenance
- Source code committed with fixes

---

## Rule 2: Idempotency

Running maintenance twice on the same system should:
- ✅ Produce identical results (no changes second time)
- ✅ Report "All systems healthy" if no issues
- ✅ Not break previously working components

---

## Rule 3: Persistence

Maintenance fixes MUST:
- ✅ Modify source code (not just configs)
- ✅ Be git-committable
- ✅ Persist across `git pull` operations
- ✅ Work on all machines without re-running maintenance

**Reference:** `cortex-brain/documents/analysis/maintenance-wiring-persistence-gap.md`

---

## Rule 4: GAPS-1230 Alignment

**Phase 17 Implementation Alignment** enforces 5 CRITICAL system behaviors:

**✅ GAP 1 - LLM Intent Classification:**
- Intent router MUST use `LLMIntentClassifier` (not regex patterns)
- Fallback to regex only when LLM unavailable
- Location: `src/cortex_agents/llm_intent_classifier.py`

**✅ GAP 2 - Auto-Engagement Planning:**
- Planning MUST auto-engage for HIGH/CRITICAL complexity requests
- `AutoEngagementEngine` evaluates: LOC, domains, security, architecture, history
- Override patterns honored ("--no-plan", "skip plan", "just implement")
- Location: `src/orchestrators/planning/auto_engagement_engine.py`

**✅ GAP 3 - Incremental AST Context:**
- AST context MUST build incrementally per conversation turn
- NOT one-time at session start
- `IncrementalASTBuilder` extracts symbols from user messages
- Location: `src/orchestrators/planning/incremental_ast_builder.py`

**✅ GAP 4 - Active Knowledge Consultation:**
- Knowledge library (35+ YAML, 525+ rules) MUST be actively consulted
- Orchestrators call `KnowledgeConsultant.consult()` before operations
- Location: `src/orchestrators/base/knowledge_consultant.py`

**✅ GAP 5 - Extended LLM Usage:**
- LLM used for BOTH complexity assessment AND intent classification
- Not complexity-only (TieredRouter pattern)

**Reference:** `cortex-brain/documents/planning/active/CORTEX-4.0-GAPS-1230/`

---

## Rule 5: Visual Progress Tracker Enforcement

**ALL Executive Summaries MUST include Visual Progress Tracker at the TOP.**

**❌ FORBIDDEN:**
- Executive summaries without visual tracker
- Progress reports lacking ASCII progress bars
- Phase outputs without completion visualization

**✅ REQUIRED FORMAT:**

```
### 📊 {OPERATION_NAME} STATUS

**Overall Progress:** `████████░░░░░░░░░░░░` **XX%** {STATUS_EMOJI} {STATUS_TEXT}

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - {Name} | `██████████` | 100% ✅ Complete |
| Phase 2 - {Name} | `████████░░` | 80% 🔄 In Progress |
| Phase 3 - {Name} | `░░░░░░░░░░` | 0% ⏳ Pending |

📊 **Tests:** XX/XX passing | **Code:** X,XXX LOC | **Status:** {STATUS}
```

**Locations:**
- `cortex-brain/documents/planning/active/*/00-*.md` (master plans)
- `cortex-brain/documents/reports/*.md` (all reports)
- Phase completion messages in chat responses

---

## Rule 6: Planning Executioner Visual Progress Bar

**Planning executioner MUST render visual progress bar at END of each phase.**

**✅ REQUIRED:**
- `template_renderer.py` → `_render_with_components()` MUST include `progress_bar`
- Planning responses MUST use templates from `response-templates-v4.yaml`
- Each phase completion shows: `[████████░░] 80%` style progress

---

## Rule 7: Autonomous Execution Enforcement

**Maintenance MUST execute ALL phases without user interaction.**

**❌ FORBIDDEN:**
- Asking "Should I proceed to Phase N?"
- Waiting for user confirmation between phases
- Stopping after discovery/reports to ask for approval
- Partial execution (running phases 1-3 and stopping)
- Interactive prompts mid-execution

**✅ REQUIRED:**
- Execute phases 1→11 in sequence automatically
- Auto-repair ALL detected issues immediately
- Auto-commit changes after each phase
- Show visual progress tracker at transitions
- Generate consolidated report ONLY at Phase 11
- Proceed to next phase immediately after current completes

---

## Rule 8: Response Template Integrity

**ALL response template references MUST resolve to existing files.**

**✅ REQUIRED Validation Checks:**
1. Every `inherits_from` reference points to existing file
2. Every `template:` in routing rules points to defined template
3. No orphaned template definitions (defined but never used)
4. Schema versions are consistent (v4.0)
5. Introduction templates exist for all audiences
6. No duplicate template definition files

**Location in Pipeline:** Phase 2b (Template Validation) + Phase 11 (Final Verification)

---

## Rule 9: Plan Content Validation

**ALL plans in `planning/active/*/00-master-plan.md` MUST contain mandatory sections:**

**✅ REQUIRED Content:**
1. Visual progress tracking (progress bars)
2. Response template references
3. Final REFACTOR phase
4. copilot_instructions block (or equivalent)

**Location in Pipeline:** Phase 7 (Knowledge) + Phase 11 (Final Verification)

---

## Rule 10: Orchestrator Hand-off Enforcement

**HAND-OFF Orchestrators (marked with 🛡️) MUST take over completely.**

**✅ REQUIRED Hand-off Orchestrators:**

| Orchestrator | Trigger Keywords | Response Template | Header |
|--------------|------------------|-------------------|--------|
| **Planning System** | `plan`, `create a plan`, `make a plan` | `autonomous_execution_progress` | `## 🛡️🧠 CORTEX Plan Execution` |
| **ADO Operations** | `ado story`, `ado feature`, `plan ado` | `ado_execution_progress` | `## 🛡️🧠 CORTEX ADO Work Item Generation` |

**Visual Confirmation:**
- 🛡️ = Orchestrator engaged and using correct template
- If response does NOT show 🛡️ header → Hand-off failed

**Location in Pipeline:** Phase 2b (Template Validation) + Phase 11 (Final Verification)

---

**For detailed rule specifications, validation scripts, and auto-repair actions, see original cortex-maintenance.prompt.md (archived).**
