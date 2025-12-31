mode: agent
description: "CORTEX System Maintenance - Automated health checks, auto-repair, and system optimization"
applyTo: "**"
---

# 🩺 CORTEX System Maintenance

**Purpose:** Automatically diagnose AND repair CORTEX system issues to maintain peak performance. This is NOT a diagnostic-only tool - it FIXES problems automatically.

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🤖 Autonomous Execution Mode

**⚠️ CRITICAL: This prompt is designed for FULLY AUTONOMOUS execution.**

### Execution Behavior

| Setting | Value | Description |
|---------|-------|-------------|
| **Auto-Proceed** | ✅ ENABLED | Phases execute sequentially without user confirmation |
| **Auto-Repair** | ✅ ENABLED | Issues are fixed immediately upon detection |
| **Auto-Commit** | ✅ ENABLED | Changes are committed to git after each phase |
| **Pause Points** | ❌ NONE | No user interaction required between phases |
| **Rollback** | ✅ AUTO | Failed phases trigger automatic rollback |

### ⛔ FORBIDDEN Behaviors in Autonomous Mode

**❌ NEVER DO THESE:**
- Ask "Should I proceed?" or "Do you want me to continue?"
- Wait for user confirmation before starting next phase
- Output "Ready for next phase?" messages
- Pause execution after discovery/reports
- Request approval for auto-repair actions
- Generate partial reports and stop

**✅ ALWAYS DO THESE:**
- Execute ALL 10 phases in sequence automatically
- Proceed to next phase immediately after current phase completes
- Auto-repair ALL detected issues without asking
- Commit changes after each phase automatically
- Generate final consolidated report ONLY at Phase 10 completion
- Show visual progress tracker at phase transitions

### Phase Transition Logic

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS EXECUTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   START ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5       │
│               │           │           │           │           │             │
│               ▼           ▼           ▼           ▼           ▼             │
│           [auto]      [auto]      [auto]      [auto]      [auto]           │
│               │           │           │           │           │             │
│               └───────────┴───────────┴───────────┴───────────┘             │
│                                   │                                         │
│   Phase 6 ◄── Phase 7 ◄── Phase 8 ◄── Phase 9 ◄── Phase 10 ◄──┘           │
│      │           │           │           │           │                      │
│      ▼           ▼           ▼           ▼           ▼                      │
│   [auto]      [auto]      [auto]      [auto]    [FINAL]                    │
│                                                     │                       │
│                                                     ▼                       │
│                                           CONSOLIDATED REPORT               │
│                                                     │                       │
│                                                     ▼                       │
│                                                   END                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Auto-Transition Rules

**After EACH phase completion, IMMEDIATELY:**

1. **Render Progress Tracker** (visual ASCII progress bar)
2. **Log Phase Summary** (one-liner: `✅ Phase N complete: {summary}`)
3. **Start Next Phase** (no delay, no confirmation)
4. **On Error:** Auto-repair OR rollback OR skip with warning

**Phase Completion Template:**
```
✅ Phase {N} - {NAME}: Complete
   └─ Actions: {count} | Fixed: {fixed_count} | Skipped: {skipped_count}
   └─ Duration: {seconds}s
   └─ Auto-proceeding to Phase {N+1}...
```

| Phase | Progress | Status |
|-------|----------|--------|
| Phase {N} | `██████████` | 100% ✅ Complete |
| Phase {N+1} | `░░░░░░░░░░` | 0% 🔄 Starting |

### Error Handling in Autonomous Mode

| Error Type | Action | Continue? |
|------------|--------|-----------|
| **Non-Critical** | Log warning, continue | ✅ YES |
| **Critical (fixable)** | Auto-repair, retry | ✅ YES |
| **Critical (unfixable)** | Log error, skip phase | ✅ YES (with warning) |
| **Catastrophic** | Rollback, abort | ❌ NO |

**Catastrophic = Only if continuing would corrupt the system**

### Invocation

**Standard (autonomous):**
```
system maintenance
```

**With specific phases:**
```
system maintenance --phases 1,2,5
```

**Dry-run (no changes):**
```
system maintenance --dry-run
```

---

## ⛔ DATA PRESERVATION RULES

**Before ANY cleanup/deletion operation, verify:**

- [ ] `cortex-brain/lessons-learned.yaml` preserved
- [ ] `cortex-brain/knowledge-graph.yaml` preserved
- [ ] `cortex-brain/tier1/*.md` preserved
- [ ] `cortex-brain/tier2/*.yaml` preserved
- [ ] User-added documents in `cortex-brain/documents/` preserved
- [ ] `cortex-brain/user-dictionary.yaml` preserved
- [ ] All `.db` files in `tier1/`, `tier2/`, `tier3/` preserved
- [ ] `copilot_instructions` in plan files preserved during regeneration
- [ ] `metadata.notes` and `metadata.tags` in plans preserved
- [ ] `named_templates` in `response-templates-v4.yaml` preserved

**Critical Data Locations (NEVER DELETE):**

```
cortex-brain/
├── tier1/*.db              # Conversations, working memory
├── tier2/*.db              # Knowledge graph, learned patterns  
├── tier3/*.db              # Development context, metrics
├── lessons-learned.yaml    # Accumulated learnings
├── knowledge-graph.yaml    # Relationship mappings
├── user-dictionary.yaml    # Custom terminology
├── documents/              # User-created content
└── response-templates-v4.yaml (named_templates section)
```

**References:**
- Data Preservation: `cortex-brain/documents/implementation-guides/phase-2.5-data-preservation-rules.md`
- Brain Protection: `cortex-brain/brain-protection-rules.yaml`
- Upgrade Preservation: UPGRADE_BRAIN_PRESERVATION instinct

---

## 🎯 Core Philosophy

**MAINTENANCE = DIAGNOSE + AUTO-REPAIR + VERIFY**

| Phase | Action | Automation Level |
|-------|--------|------------------|
| **DIAGNOSE** | Identify gaps, errors, unwired components | ✅ Fully Automated |
| **AUTO-REPAIR** | Patch source code, wire components, fix issues | ✅ Fully Automated |
| **VERIFY** | Confirm 100% health, run tests, validate fixes | ✅ Fully Automated |

**⚠️ CRITICAL:** If maintenance only identifies problems but doesn't fix them, it's a BUG in the maintenance system itself.

---

## 🚨 Enforcement Rules

### Rule 1: AUTO-REPAIR is MANDATORY

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

### Rule 2: Idempotency

Running maintenance twice on the same system should:
- ✅ Produce identical results (no changes second time)
- ✅ Report "All systems healthy" if no issues
- ✅ Not break previously working components

### Rule 3: Persistence

Maintenance fixes MUST:
- ✅ Modify source code (not just configs)
- ✅ Be git-committable
- ✅ Persist across `git pull` operations
- ✅ Work on all machines without re-running maintenance

**Reference:** `cortex-brain/documents/analysis/maintenance-wiring-persistence-gap.md`

### Rule 4: GAPS-1230 Alignment (NEW - December 30, 2025)

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

### Rule 5: Visual Progress Tracker Enforcement (NEW - December 30, 2025)

**ALL Executive Summaries MUST include Visual Progress Tracker at the TOP.**

**❌ FORBIDDEN:**
- Executive summaries without visual tracker
- Progress reports lacking ASCII progress bars
- Phase outputs without completion visualization

**✅ REQUIRED FORMAT:**

---
### 📊 {OPERATION_NAME} STATUS

**Overall Progress:** `████████░░░░░░░░░░░░` **XX%** {STATUS_EMOJI} {STATUS_TEXT}

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - {Name} | `██████████` | 100% ✅ Complete |
| Phase 2 - {Name} | `████████░░` | 80% 🔄 In Progress |
| Phase 3 - {Name} | `░░░░░░░░░░` | 0% ⏳ Pending |

📊 **Tests:** XX/XX passing | **Code:** X,XXX LOC | **Status:** {STATUS}

---

**Locations that MUST have visual tracker:**
- `cortex-brain/documents/planning/active/*/00-*.md` (master plans)
- `cortex-brain/documents/reports/*.md` (all reports)
- Phase completion messages in chat responses

**Reference:** `cortex-brain/response-templates/planning.yaml` → `visual_progress_tracker`

### Rule 6: Planning Executioner Visual Progress Bar (NEW - December 30, 2025)

**Planning executioner MUST render visual progress bar at END of each phase.**

**❌ FORBIDDEN:**
- Phase completions without progress visualization
- Text-only status updates
- Autonomous mode skipping progress_bar component

**✅ REQUIRED:**
- `template_renderer.py` → `_render_with_components()` MUST include `progress_bar`
- Planning responses MUST use templates from `response-templates-v4.yaml`
- Each phase completion shows: `[████████░░] 80%` style progress

**Implementation Check:**
```python
# src/response_templates/template_renderer.py
# Line ~229: autonomous mode must NOT skip progress_bar
components = ['header', 'body', 'progress_bar', 'footer']  # progress_bar REQUIRED
```

**Template Reference:**
- `cortex-brain/response-templates/base-components.yaml` → `progress_bar_visual`
- `cortex-brain/response-templates/planning.yaml` → `visual_progress_tracker`

**Test Coverage:**
- `tests/response_templates/test_visual_progress.py` - Validates progress bar rendering
- Integration tests must verify progress bar appears in all phase outputs

### Rule 7: Autonomous Execution Enforcement (NEW - December 30, 2025)

**Maintenance MUST execute ALL phases without user interaction.**

**❌ FORBIDDEN:**
- Asking "Should I proceed to Phase N?"
- Waiting for user confirmation between phases
- Stopping after discovery/reports to ask for approval
- Partial execution (running phases 1-3 and stopping)
- Interactive prompts mid-execution
- "Let me know when you're ready" messages

**✅ REQUIRED:**
- Execute phases 1→10 in sequence automatically
- Auto-repair ALL detected issues immediately
- Auto-commit changes after each phase
- Show visual progress tracker at transitions
- Generate consolidated report ONLY at Phase 10
- Proceed to next phase immediately after current completes

**Validation Pattern:**
```
✅ CORRECT:
   Phase 1 complete → Phase 2 starts immediately
   
❌ WRONG:
   Phase 1 complete → "Ready for Phase 2?" → waits
```

### Rule 8: Response Template Integrity (NEW - December 30, 2025)

**ALL response template references MUST resolve to existing files.**

**Problem:** Template cleanup revealed:
- 27 files referencing non-existent `5-part-standard.yaml`
- Duplicate template files causing routing conflicts
- Missing introduction templates referenced in routing rules
- Inconsistent schema versions across template files

**Solution:** Validate template integrity on every maintenance run.

**✅ REQUIRED Validation Checks:**
1. Every `inherits_from` reference points to existing file
2. Every `template:` in routing rules points to defined template
3. No orphaned template definitions (defined but never used)
4. Schema versions are consistent (v4.0)
5. Introduction templates exist for all audiences
6. No duplicate template definition files

**❌ FORBIDDEN:**
- `inherits_from: core/base-templates/5-part-standard.yaml` (file doesn't exist)
- Template references to undefined templates
- Duplicate routing/component files in `cortex-brain/` root
- Multiple template definition files (only `response-templates-v4.yaml` allowed)

**🔧 Auto-Repair Actions:**
- Remove orphaned `inherits_from` references
- Delete duplicate files in `cortex-brain/` root (keep `response-templates/` versions)
- Generate missing introduction templates
- Update routing rules to reference valid templates
- Archive legacy template files to `cortex-brain/archives/`

**Validation Script:**
```python
python3 -c "
import yaml
import os
from pathlib import Path

print('🔍 Validating Response Template Integrity...\n')

# Load routing rules
routing_file = Path('cortex-brain/response-templates/response-routing-rules.yaml')
if routing_file.exists():
    with open(routing_file, 'r', encoding='utf-8') as f:
        routing = yaml.safe_load(f)
    
    # Get template file mappings
    mappings = routing.get('validation', {}).get('template_file_mappings', {})
    
    errors = []
    for template_id, file_path in mappings.items():
        if not Path(file_path).exists():
            errors.append(f'❌ {template_id} → {file_path} (NOT FOUND)')
    
    if errors:
        print('\n'.join(errors))
        print(f'\n❌ {len(errors)} broken reference(s) found!')
        exit(1)
    else:
        print(f'✅ All {len(mappings)} template references are valid!')
else:
    print('❌ Routing rules file not found!')
    exit(1)
"
```

**Location in Pipeline:** Phase 2b (Template Validation) + Phase 11 (Final Verification)

**Success Criteria:**
- ✅ Zero orphaned `inherits_from` references
- ✅ All routing rule templates resolve correctly
- ✅ Single source of truth: `response-templates-v4.yaml`
- ✅ Schema version consistency (v4.0)
- ✅ No duplicate template files

---

### Rule 9: Plan Content Validation (NEW - December 30, 2025)

**ALL plans in `planning/active/*/00-master-plan.md` MUST contain mandatory sections.**

**Problem:** Plans created manually bypass Planning Orchestrator, missing:
- Visual progress tracking sections
- Response template reminders
- Final REFACTOR phase enforcement
- copilot_instructions block

**This has caused 12+ failures** where plans lacked required content.

**✅ REQUIRED Validation Checks (Phase 7 - Knowledge):**

```bash
# Validate all master plans have mandatory content
for plan in cortex-brain/documents/planning/active/*/00-master-plan.md; do
  echo "Checking: $plan"
  
  # Check 1: Visual Progress Tracking
  if ! grep -q "Progress.*\[█\|░\]" "$plan" 2>/dev/null; then
    echo "  ❌ Missing: Visual progress tracking (progress bars)"
    MISSING_CONTENT=true
  fi
  
  # Check 2: Response Template Reference
  if ! grep -q "autonomous_execution_progress\|response-templates-v4.yaml" "$plan" 2>/dev/null; then
    echo "  ❌ Missing: Response template reference"
    MISSING_CONTENT=true
  fi
  
  # Check 3: Final REFACTOR Phase
  if ! grep -qi "final.*refactor\|REFACTOR.*phase\|SKULL.*REFACTOR" "$plan" 2>/dev/null; then
    echo "  ❌ Missing: Final REFACTOR phase (SKULL enforcement)"
    MISSING_CONTENT=true
  fi
  
  # Check 4: copilot_instructions block OR reminder
  if ! grep -q "copilot_instructions\|tdd_enforcement\|final_refactor_required" "$plan" 2>/dev/null; then
    echo "  ❌ Missing: copilot_instructions block"
    MISSING_CONTENT=true
  fi
done
```

**🔧 Auto-Repair Actions:**

When missing content detected, append to plan:
```markdown
---

## ⚠️ MANDATORY Requirements (Auto-Added by Maintenance)

### Visual Progress Tracking
Use `autonomous_execution_progress` template from `response-templates-v4.yaml` (line 863)

| # | Phase | Status | Progress | TDD Status |
|---|-------|--------|----------|------------|
| **Overall** | 🟡 | `[░░░░░░░░░░░░░░░░░░░░]` 0% | Phase 0/N | - |

### Response Template Helpers
- `generate_progress_bar(percentage, width=20, filled='█', empty='░')`
- `generate_tdd_status(red_done, green_done, refactor_done)`
- `render_autonomous_progress(...)` - Full convenience method

### Final REFACTOR Phase (MANDATORY - SKULL Rule)
Per `REFACTOR_CODE_CLEANUP_ENFORCEMENT`:
- ✅ Whole-file cleanup (not just new code)
- ✅ Complexity ≤30 for all functions
- ✅ SOLID principles enforced
- ✅ Zero dead code/unused imports
- ✅ 100% test pass rate

### copilot_instructions
```yaml
copilot_instructions:
  response_template: "autonomous_execution_progress"
  progress_updates: true
  tdd_enforcement: true
  final_refactor_required: true
  checkpoint_frequency: "per_phase"
```

**Reference:** `planning-system-4.0-manifest.yaml` (lines 118-157, 639-677)
```

**❌ FORBIDDEN:**
- Plans without visual progress bars
- Plans without REFACTOR phase
- Plans without template references
- Skipping plan content validation in maintenance

**Location in Pipeline:** Phase 7 (Knowledge) + Phase 11 (Final Verification)

**Success Criteria:**
- ✅ 100% of active plans have visual progress tracking
- ✅ 100% of active plans reference response templates
- ✅ 100% of active plans have Final REFACTOR phase
- ✅ 100% of active plans have copilot_instructions or equivalent

---

### Rule 10: Orchestrator Hand-off Enforcement (NEW - December 30, 2025)

**HAND-OFF Orchestrators (marked with 🛡️) MUST take over completely.**

**Problem:** Intent Router was telling LLM to "create folder structure" instead of **handing off** to the orchestrator, causing:
- ❌ Plans created without `copilot_instructions` block
- ❌ No visual progress tracking hints
- ❌ No response template usage
- ❌ No REFACTOR phase enforcement

**Solution:** When HAND-OFF orchestrators are detected, they MUST use their designated response templates.

**✅ REQUIRED Hand-off Orchestrators:**

| Orchestrator | Trigger Keywords | Response Template | Header |
|--------------|------------------|-------------------|--------|
| **Planning System** | `plan`, `create a plan`, `make a plan` | `autonomous_execution_progress` | `## 🛡️🧠 CORTEX Plan Execution` |
| **ADO Operations** | `ado story`, `ado feature`, `plan ado` | `ado_execution_progress` | `## 🛡️🧠 CORTEX ADO Work Item Generation` |

**Visual Confirmation:**
- 🛡️ = Orchestrator engaged and using correct template
- If response does NOT show 🛡️ header → Hand-off failed

**✅ REQUIRED Validation Checks:**

```bash
# Check response templates have orchestrator_engaged flag
grep -q "orchestrator_engaged: true" cortex-brain/response-templates-v4.yaml && echo "✅ Templates configured" || echo "❌ Missing orchestrator_engaged flag"

# Check Intent Router has HAND-OFF entries
grep -q "🛡️.*HAND-OFF" .github/prompts/CORTEX.prompt.md && echo "✅ Intent Router configured" || echo "❌ Missing HAND-OFF entries"

# Check response template headers have shield icon
grep -q "## 🛡️🧠 CORTEX" cortex-brain/response-templates-v4.yaml && echo "✅ Templates have shield icon" || echo "❌ Missing shield icon in templates"
```

**🔧 Auto-Repair Actions:**

If HAND-OFF orchestrators missing from Intent Router:
```markdown
| `/CORTEX Plan [x]`, `create a plan`, `make a plan`, `plan: [x]` | 🛡️ **Planning System** | `planning-system-4.0-manifest.yaml` | **HAND-OFF** → Use `autonomous_execution_progress` template |
| `plan ado`, `ado story`, `ado feature` | 🛡️ **ADO Operations** | `ado-planning-manifest.yaml` | **HAND-OFF** → Use `ado_execution_progress` template |
```

If response templates missing shield icon:
- Update `autonomous_execution_progress` header to: `## 🛡️🧠 CORTEX Plan Execution`
- Update `ado_execution_progress` header to: `## 🛡️🧠 CORTEX ADO Work Item Generation`

**❌ FORBIDDEN:**
- HAND-OFF orchestrators without 🛡️ marker in Intent Router
- Response templates without `orchestrator_engaged: true` flag
- Response headers without 🛡️ shield icon
- Manual plan creation bypassing Planning Orchestrator

**Extensibility:**
To add new HAND-OFF orchestrators:
1. Add 🛡️ marker to Intent Router table
2. Add `orchestrator_engaged: true` to response template
3. Add `## 🛡️🧠 CORTEX {Operation}` header to template
4. Add to this rule's validation checks

**Location in Pipeline:** Phase 2b (Template Validation) + Phase 11 (Final Verification)

**Success Criteria:**
- ✅ All HAND-OFF orchestrators have 🛡️ in Intent Router
- ✅ All HAND-OFF templates have `orchestrator_engaged: true`
- ✅ All HAND-OFF response headers show 🛡️ shield icon
- ✅ User sees 🛡️ when orchestrator is correctly engaged

---

## 🎯 11-Phase Optimized Maintenance Pipeline

**⚠️ EVERY PHASE = DIAGNOSE + AUTO-REPAIR + VERIFY**

### Pipeline Strategy: DISCOVER → CLEAN → PRESERVE → WIRE → TEST → VERIFY

| Phase | Focus Area | Diagnose | Auto-Repair | Verify |
|-------|-----------|----------|-------------|--------|
| **1** | **🔍 DISCOVERY** | **Scan entire system for enhancements, gaps, bloat** | **Generate comprehensive action report** | **All issues cataloged** |
| **2** | **🗑️ CLEANUP** | Clear caches, validate templates, remove legacy, resolve duplicates, delete backups | **7 sub-phases (2a-2g):** Cache clear, template validation, legacy removal, duplicate resolution, backup deletion | Zero bloat, valid templates, no legacy refs |
| **3** | **⛔ PRESERVATION** | Validate protected data paths exist | Verify no critical data in cleanup targets | All user data safe |
| **4** | **🔧 SCAFFOLDING** | Check toolkit generators exist | Create missing generators | Test generation works |
| **5** | **🔌 WIRING** | Detect unwired components | Auto-wire orchestrators, agents | 100% wiring coverage |
| **6** | **🧪 TESTING** | Run full test suite | Delete obsolete tests, fix bugs | 100% pass rate |
| **7** | **📚 KNOWLEDGE** | Scan knowledge library, **validate plan content (Rule 9)** | Fix broken refs, sync YAML↔MD, **auto-repair plans** | All guidelines accessible, **plans conformant** |
| **8** | **🗂️ ORGANIZATION** | Check report structure | Archive old, consolidate duplicates | Clean hierarchy |
| **9** | **🔀 ROUTING** | Validate intent router | Fix broken manifest paths | All routes functional |
| **10** | **📝 PROMPTS** | Measure prompt bloat | Regenerate lean prompts | Each <200 lines |
| **11** | **✅ VERIFICATION** | Run health diagnostics | Fix critical issues | Health score ≥95 |

### Phase Execution Order (Optimized for Efficiency)

```
Phase 1: DISCOVERY (Holistic Scan)
  ├─ Identify all unwired components
  ├─ Find all backup files/folders
  ├─ Detect duplicate reports
  ├─ Measure prompt bloat
  ├─ Check knowledge library sync
  ├─ Validate test suite health
  └─ Generate master action report
  
Phase 2: CLEANUP (Remove Waste)
  ├─ Delete backups
  ├─ Delete duplicates
  └─ Archive old reports
  
Phase 3: PRESERVATION (Validate Protected Data)
  └─ Verify critical data paths safe
  
Phase 4: SCAFFOLDING (Foundation)
  └─ Verify/create toolkit generators
  
Phase 5: WIRING (Connections)
  ├─ Auto-wire orchestrators
  ├─ Register agents
  └─ Update manifests
  
Phase 6: TESTING (Quality)
  ├─ Run test suite
  └─ Delete obsolete tests
  
Phase 7: KNOWLEDGE (Content)
  └─ Sync knowledge library
  
Phase 8: ORGANIZATION (Structure)
  └─ Organize reports
  
Phase 9: ROUTING (Navigation)
  └─ Fix intent router
  
Phase 10: PROMPTS (Templates)
  └─ Regenerate lean prompts
  
Phase 11: VERIFICATION (Final Health Check)
  └─ Confirm 100% system health
```

### 🤖 Autonomous Execution Block

**⚠️ EXECUTE ALL PHASES IN SEQUENCE WITHOUT STOPPING**

When `system maintenance` is invoked, execute this consolidated flow:

```python
# PSEUDO-CODE FOR AUTONOMOUS EXECUTION
# This is the EXACT behavior Copilot must follow

def execute_maintenance():
    """
    Autonomous 10-phase maintenance pipeline.
    NO USER INTERACTION between phases.
    """
    phases = [
        (1, "DISCOVERY", discover_system),
        (2, "CLEANUP", cleanup_waste),
        (3, "PRESERVATION", validate_preservation),
        (4, "SCAFFOLDING", verify_scaffolds),
        (5, "WIRING", wire_components),
        (6, "TESTING", run_tests),
        (7, "KNOWLEDGE", sync_knowledge),
        (8, "ORGANIZATION", organize_reports),
        (9, "ROUTING", fix_routing),
        (10, "PROMPTS", optimize_prompts),
        (11, "VERIFICATION", verify_health),
    ]
    
    results = {}
    
    for phase_num, phase_name, phase_func in phases:
        # Show progress BEFORE phase
        render_progress_tracker(phase_num, "IN_PROGRESS")
        
        # Execute phase (NO CONFIRMATION)
        result = phase_func()
        
        # Auto-repair if issues found
        if result.issues:
            for issue in result.issues:
                auto_repair(issue)  # FIX IMMEDIATELY
        
        # Log completion (NO PAUSE)
        log(f"✅ Phase {phase_num} - {phase_name}: Complete")
        
        # Store result
        results[phase_num] = result
        
        # IMMEDIATELY proceed to next phase
        # ⛔ NO: "Ready for Phase N+1?"
        # ⛔ NO: "Should I continue?"
        # ✅ YES: Just start next phase
    
    # ONLY at end: Generate consolidated report
    generate_final_report(results)
    commit_all_changes()
    
    return "✅ All 10 phases complete!"
```

### Execution Checkpoints (Auto-Validated)

**At each phase transition, auto-validate:**

| Checkpoint | Validation | On Failure |
|------------|------------|------------|
| Phase 1→2 | Discovery report exists | Regenerate |
| Phase 2→3 | Zero backups remain | Re-cleanup |
| Phase 3→4 | Protected data verified | Stop maintenance |
| Phase 4→5 | Scaffolds verified | Create missing |
| Phase 5→6 | 100% wiring coverage | Re-wire |
| Phase 6→7 | Tests passing | Fix failures |
| Phase 7→8 | Knowledge synced | Re-sync |
| Phase 8→9 | Reports organized | Re-organize |
| Phase 9→10 | Routes functional | Re-route |
| Phase 10→11 | Prompts optimized | Re-optimize |
| Phase 11→END | Health ≥95% | Escalate |

### Final Report Structure

**Generated ONLY after Phase 10 completion:**

```markdown
# 🩺 CORTEX Maintenance Report

**Date:** {date}
**Duration:** {total_duration}
**Status:** ✅ ALL PHASES COMPLETE

## Visual Progress Tracker

---
### 🚑 SYSTEM MAINTENANCE COMPLETE

**Overall Progress:** `████████████████████` **100%** ✅ HEALTHY

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Discovery | `██████████` | 100% ✅ |
| Phase 2 - Cleanup | `██████████` | 100% ✅ |
| Phase 3 - Preservation | `██████████` | 100% ✅ |
| Phase 4 - Scaffolding | `██████████` | 100% ✅ |
| Phase 5 - Wiring | `██████████` | 100% ✅ |
| Phase 6 - Testing | `██████████` | 100% ✅ |
| Phase 7 - Knowledge | `██████████` | 100% ✅ |
| Phase 8 - Organization | `██████████` | 100% ✅ |
| Phase 9 - Routing | `██████████` | 100% ✅ |
| Phase 10 - Prompts | `██████████` | 100% ✅ |
| Phase 11 - Verification | `██████████` | 100% ✅ |

📊 **Issues Found:** {count} | **Auto-Fixed:** {fixed} | **Health:** {score}%

---

## Phase Summaries
{phase_summaries}

## Changes Made
{git_diff_summary}

## Next Maintenance
Recommended: {next_date}
```

---

## Phase 1: Holistic System Discovery 🔍 - COMPREHENSIVE SCAN

### ⚠️ DISCOVERY FIRST, ACTION SECOND

**Purpose:** Scan the ENTIRE CORTEX system to identify ALL enhancement opportunities, gaps, bloat, and issues BEFORE any repairs are made. This creates a master action plan for Phases 2-10.

**Philosophy:** "Measure twice, cut once" - Comprehensive discovery prevents duplicate work and ensures optimal repair strategy.

---

### 1a. Discover Unwired Components

**Use the PROVEN wiring integrity checker with snake_case conversion:**

```powershell
# Run the official wiring integrity checker
echo "🔍 Running comprehensive wiring integrity check..."
python scripts/check_wiring_integrity.py

# Check results
if ($LASTEXITCODE -eq 0) {
    echo "✅ Wiring check complete"
    
    # Parse the JSON report for actionable data
    $report = Get-Content "cortex-brain/health-reports/wiring-report-*.json" | ConvertFrom-Json | Select-Object -Last 1
    
    $totalComponents = $report.summary.total_components
    $wiredCount = $report.summary.wired_count
    $unwiredCount = $report.summary.unwired_count
    $coverage = $report.summary.coverage_percentage
    
    echo "  📊 Total Components: $totalComponents"
    echo "  ✅ Wired: $wiredCount"
    echo "  ⚠️  Unwired: $unwiredCount"
    echo "  📈 Coverage: $coverage%"
    
    # List unwired components by category
    if ($unwiredCount -gt 0) {
        echo ""
        echo "⚠️  UNWIRED COMPONENTS DETECTED:"
        echo ""
        
        if ($report.orchestrators.unwired.Count -gt 0) {
            echo "  Orchestrators: $($report.orchestrators.unwired -join ', ')"
        }
        if ($report.agents.unwired.Count -gt 0) {
            echo "  Agents: $($report.agents.unwired -join ', ')"
        }
        if ($report.modules.unwired.Count -gt 0) {
            echo "  Modules: $($report.modules.unwired -join ', ')"
        }
        if ($report.plugins.unwired.Count -gt 0) {
            echo "  Plugins: $($report.plugins.unwired -join ', ')"
        }
        
        echo ""
        echo "👉 These will be auto-wired in Phase 5"
    } else {
        echo ""
        echo "🎉 100% WIRING COVERAGE - All components properly wired!"
    }
    
} else {
    echo "❌ Wiring check failed - see errors above"
    exit 1
}

# Save discovery summary
cat > cortex-brain/discovery-reports/unwired-components-$(Get-Date -Format "yyyyMMdd").txt << EOF
# Unwired Components Discovery Report

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Total Components:** $totalComponents
**Wired:** $wiredCount
**Unwired:** $unwiredCount
**Coverage:** $coverage%

## Unwired Components:
$(if ($unwiredCount -eq 0) { "✅ None - 100% coverage achieved!" } else { $report | ConvertTo-Json -Depth 10 })

## Next Steps:
$(if ($unwiredCount -gt 0) { "Phase 5 will auto-wire all $unwiredCount components using bulk_wire_components.py" } else { "No action needed - system fully wired" })
EOF

echo "📄 Report saved: cortex-brain/discovery-reports/unwired-components-$(Get-Date -Format 'yyyyMMdd').txt"
```

**Why This Approach:**
- Uses `check_wiring_integrity.py` with **CamelCase→snake_case conversion** (proven to work)
- Detects all 4 component types: Orchestrators, Agents, Modules, Plugins
- Excludes utility classes (OrchestratorStatus, AgentRequest, etc.)
- Generates JSON report for Phase 5 bulk wiring
- No false positives (14.6% → 100% success rate)

---

### 1b. Discover Backup Files and Folders

**Find ALL backup files and folders recursively:**

```bash
echo "🔍 Scanning for backup files and folders..."

# Find backup directories
find . -type d \( \
  -name "*backup*" -o \
  -name "*_backup_*" -o \
  -name "*.backup" -o \
  -name "*archive*" -o \
  -name "*old*" -o \
  -name "*_bak" \
\) ! -path "./.git/*" ! -path "./node_modules/*" | sort > /tmp/backup_dirs.txt

# Find backup files
find . -type f \( \
  -name "*.backup" -o \
  -name "*.bak" -o \
  -name "*~" -o \
  -name "*.old" -o \
  -name "*_backup_*" \
\) ! -path "./.git/*" ! -path "./node_modules/*" | sort > /tmp/backup_files.txt

# Count and report
BACKUP_DIRS=$(wc -l < /tmp/backup_dirs.txt)
BACKUP_FILES=$(wc -l < /tmp/backup_files.txt)

echo "  📂 Backup directories: $BACKUP_DIRS"
echo "  📄 Backup files: $BACKUP_FILES"

# Calculate total size
BACKUP_SIZE=$(du -ch $(cat /tmp/backup_dirs.txt /tmp/backup_files.txt 2>/dev/null) 2>/dev/null | tail -1 | awk '{print $1}')
echo "  � Total backup size: $BACKUP_SIZE"

# Save report
cat > cortex-brain/discovery-reports/backup-bloat-$(date +%Y%m%d).txt << EOF
# Backup Bloat Discovery Report

**Directories:** $BACKUP_DIRS
**Files:** $BACKUP_FILES
**Total Size:** $BACKUP_SIZE

## Directories:
$(cat /tmp/backup_dirs.txt)

## Files:
$(cat /tmp/backup_files.txt)
EOF
```

---

### 1c. Discover Duplicate Reports

**Find duplicate reports across the brain:**

```bash
echo "🔍 Scanning for duplicate reports..."

# Find all report files
find cortex-brain/documents/reports/ -type f -name "*.md" | sort > /tmp/all_reports.txt

# Detect duplicates by content hash
find cortex-brain/documents/reports/ -type f -name "*.md" -exec md5 {} \; | sort | uniq -d > /tmp/duplicate_hashes.txt

# Detect duplicates by similar names
find cortex-brain/documents/reports/ -type f -name "*.md" -exec basename {} \; | sort | uniq -d > /tmp/duplicate_names.txt

DUPLICATE_COUNT=$(wc -l < /tmp/duplicate_names.txt)
echo "  📋 Duplicate reports: $DUPLICATE_COUNT"

# Save report
cat > cortex-brain/discovery-reports/duplicate-reports-$(date +%Y%m%d).txt << EOF
# Duplicate Reports Discovery

**Duplicates by name:** $(wc -l < /tmp/duplicate_names.txt)
**Duplicates by content:** $(wc -l < /tmp/duplicate_hashes.txt)

## Duplicate Names:
$(cat /tmp/duplicate_names.txt)
EOF
```

---

### 1d. Discover Prompt Bloat

**Measure prompt file sizes to detect bloat:**

```bash
echo "🔍 Scanning for prompt bloat..."

# Find all prompt files
find .github/prompts/ -name "*.prompt.md" -o -name "*.md" > /tmp/prompt_files.txt

# Measure each prompt
cat > /tmp/prompt_bloat_report.txt << 'EOF'
# Prompt Bloat Discovery Report

| File | Lines | Size | Status |
|------|-------|------|--------|
EOF

while read -r file; do
  LINES=$(wc -l < "$file")
  SIZE=$(du -h "$file" | awk '{print $1}')
  
  if [ "$LINES" -gt 200 ]; then
    STATUS="⚠️  BLOATED"
  else
    STATUS="✅ OK"
  fi
  
  echo "| $file | $LINES | $SIZE | $STATUS |" >> /tmp/prompt_bloat_report.txt
done < /tmp/prompt_files.txt

# Save report
cp /tmp/prompt_bloat_report.txt cortex-brain/discovery-reports/prompt-bloat-$(date +%Y%m%d).txt
cat /tmp/prompt_bloat_report.txt
```

---

### 1e. Discover Knowledge Library Sync Issues

**Check for YAML ↔ Markdown sync problems:**

```bash
echo "🔍 Scanning knowledge library sync..."

# Check for orphaned YAML files (no corresponding .md)
find cortex-brain/knowledge/ -name "*.yaml" > /tmp/knowledge_yaml.txt
find cortex-brain/knowledge/ -name "*.md" > /tmp/knowledge_md.txt

# Compare counts
YAML_COUNT=$(wc -l < /tmp/knowledge_yaml.txt)
MD_COUNT=$(wc -l < /tmp/knowledge_md.txt)

echo "  📚 YAML files: $YAML_COUNT"
echo "  📄 Markdown files: $MD_COUNT"

if [ "$YAML_COUNT" -ne "$MD_COUNT" ]; then
  echo "  ⚠️  SYNC ISSUE: Counts don't match"
else
  echo "  ✅ Counts match"
fi

# Save report
cat > cortex-brain/discovery-reports/knowledge-sync-$(date +%Y%m%d).txt << EOF
# Knowledge Library Sync Discovery

**YAML Files:** $YAML_COUNT
**Markdown Files:** $MD_COUNT
**Status:** $([ "$YAML_COUNT" -eq "$MD_COUNT" ] && echo "✅ Synced" || echo "⚠️  Out of Sync")
EOF
```

---

### 1f. Discover Test Suite Health

**Check test suite for obsolete/failing tests:**

```bash
echo "🔍 Scanning test suite health..."

# Run tests and capture results (non-blocking)
python3 -m pytest tests/orchestrators/planning/ --collect-only 2>&1 | tee /tmp/test_collection.txt

# Count test files and tests
TEST_FILES=$(find tests/ -name "test_*.py" | wc -l)
TEST_COUNT=$(grep -c "test session starts" /tmp/test_collection.txt || echo "0")

echo "  🧪 Test files: $TEST_FILES"
echo "  🧪 Test cases: $TEST_COUNT"

# Check for obsolete markers
OBSOLETE_TESTS=$(grep -r "DEPRECATED\|LEGACY\|OLD\|TODO.*delete" tests/ | wc -l)
echo "  ⚠️  Obsolete test markers: $OBSOLETE_TESTS"

# Save report
cat > cortex-brain/discovery-reports/test-suite-health-$(date +%Y%m%d).txt << EOF
# Test Suite Health Discovery

**Test Files:** $TEST_FILES
**Test Cases:** $TEST_COUNT
**Obsolete Markers:** $OBSOLETE_TESTS

## Obsolete Tests:
$(grep -r "DEPRECATED\|LEGACY\|OLD" tests/ || echo "None found")
EOF
```

---

### 1g. Generate Master Action Report

**Consolidate all discoveries into a master action plan:**

```bash
echo "📊 Generating Master Action Report..."

cat > cortex-brain/discovery-reports/MASTER-ACTION-PLAN-$(date +%Y%m%d).md << 'EOF'
# 🎯 CORTEX Maintenance Master Action Plan

**Date:** $(date +%Y-%m-%d)
**Phase:** Discovery Complete

---

## 📋 Discovery Summary

| Category | Issues Found | Priority | Target Phase |
|----------|-------------|----------|--------------|
| Unwired Components | $(wc -l < /tmp/unwired_components_report.txt) | HIGH | Phase 4 (Wiring) |
| Backup Bloat | $(cat /tmp/backup_dirs.txt /tmp/backup_files.txt | wc -l) files/dirs | HIGH | Phase 2 (Cleanup) |
| Duplicate Reports | $(wc -l < /tmp/duplicate_names.txt) | MEDIUM | Phase 7 (Organization) |
| Prompt Bloat | $(grep "BLOATED" /tmp/prompt_bloat_report.txt | wc -l) files | MEDIUM | Phase 9 (Prompts) |
| Knowledge Sync Issues | $([ "$(wc -l < /tmp/knowledge_yaml.txt)" -ne "$(wc -l < /tmp/knowledge_md.txt)" ] && echo "YES" || echo "NONE") | LOW | Phase 6 (Knowledge) |
| Obsolete Tests | $(grep -r "DEPRECATED" tests/ | wc -l) | HIGH | Phase 5 (Testing) |

---

## 🚀 Recommended Execution Order

1. **Phase 2: Cleanup** - Delete $(cat /tmp/backup_dirs.txt /tmp/backup_files.txt | wc -l) backup files/folders (recover $(du -sh $(cat /tmp/backup_dirs.txt /tmp/backup_files.txt 2>/dev/null) 2>/dev/null | awk '{sum+=$1} END {print sum}')MB)
2. **Phase 3: Scaffolding** - Verify toolkit generators
3. **Phase 4: Wiring** - Wire $(wc -l < /tmp/unwired_components_report.txt) components
4. **Phase 5: Testing** - Delete $(grep -r "DEPRECATED" tests/ | wc -l) obsolete tests
5. **Phase 6: Knowledge** - Sync knowledge library
6. **Phase 7: Organization** - Consolidate $(wc -l < /tmp/duplicate_names.txt) duplicate reports
7. **Phase 8: Routing** - Fix intent router paths
8. **Phase 9: Prompts** - Regenerate $(grep "BLOATED" /tmp/prompt_bloat_report.txt | wc -l) bloated prompts
9. **Phase 10: Verification** - Final health check

---

## 📁 Discovery Reports Generated

- unwired-components-$(date +%Y%m%d).txt
- backup-bloat-$(date +%Y%m%d).txt
- duplicate-reports-$(date +%Y%m%d).txt
- prompt-bloat-$(date +%Y%m%d).txt
- knowledge-sync-$(date +%Y%m%d).txt
- test-suite-health-$(date +%Y%m%d).txt

---

## ✅ Next Step

**Execute Phase 2: Cleanup** to remove $(cat /tmp/backup_dirs.txt /tmp/backup_files.txt | wc -l) waste items.

EOF

# Display master report
cat cortex-brain/discovery-reports/MASTER-ACTION-PLAN-$(date +%Y%m%d).md

echo ""
echo "✅ Phase 1 Discovery Complete!"
echo "📊 Master Action Plan: cortex-brain/discovery-reports/MASTER-ACTION-PLAN-$(date +%Y%m%d).md"
```

---

### 1h. Success Criteria

**Phase 1 is complete when:**

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Master report exists | `ls cortex-brain/discovery-reports/MASTER-ACTION-PLAN-*.md` | 1 file |
| All sub-reports exist | `ls cortex-brain/discovery-reports/*-$(date +%Y%m%d).txt` | 6 files |
| Action counts captured | `grep "Issues Found" cortex-brain/discovery-reports/MASTER-ACTION-PLAN-*.md` | All categories listed |
| Execution order defined | `grep "Recommended Execution Order" cortex-brain/discovery-reports/MASTER-ACTION-PLAN-*.md` | Phases 2-10 listed |

---

## Phase 2: System Cleanup 🗑️ - COMPREHENSIVE WASTE REMOVAL

### ⚠️ USES PHASE 1 DISCOVERY DATA

**Purpose:** Delete ALL backup folders, files, duplicate reports, clear caches, validate templates, and remove legacy references.

**Input:** Phase 1 discovery reports (`/tmp/backup_dirs.txt`, `/tmp/backup_files.txt`, `/tmp/duplicate_names.txt`)

**Output:** Clean repository with zero bloat, validated templates, cleared caches, no legacy references.

**Sub-Phases:**
- **2a:** Clear VS Code & Python caches
- **2b:** Validate response templates (progress bars, autonomous execution)
- **2c:** Remove legacy 5-part template references
- **2d:** Resolve duplicate files
- **2e:** Delete backup directories
- **2f:** Delete backup files
- **2g:** Consolidate duplicate reports

---

### 2a. Clear VS Code & Python Caches 🧹

**Purpose:** Remove stale cached data for fresh workspace state.

**Actions:**
```powershell
# Windows paths for VS Code cache
$VSCodeCache = @(
    "$env:APPDATA\Code\Cache",
    "$env:APPDATA\Code\CachedData",
    "$env:APPDATA\Code\CachedExtensions",
    "$env:APPDATA\Code\CachedExtensionVSIXs"
)

# Clear VS Code caches
foreach ($path in $VSCodeCache) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✅ Cleared: $path"
    }
}

# Clear workspace-specific state
Remove-Item -Path ".vscode/.history" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".vscode/.cache" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".vscode/*.log" -Force -ErrorAction SilentlyContinue

# Clear Python caches
Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -File -Filter "*.pyc" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Directory -Filter ".pytest_cache" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Directory -Filter ".mypy_cache" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

Write-Host "✅ All caches cleared"
```

**Python Toolkit:** `cortex-toolkit/maintenance/clear_caches.py`

---

### 2b. Validate Response Templates 🎯

**Purpose:** Ensure visual progress bars are wired correctly and autonomous execution is enabled.

**Validation Checks:**

| Check | Expected Value | File(s) to Verify |
|-------|----------------|-------------------|
| Planning progress template | `autonomous_execution_progress` | `planning_orchestrator.py` |
| Visual progress bars | Unicode blocks `█░` | `response-templates-v4.yaml` |
| Autonomous execution default | `True` | All orchestrator files |
| Progress bar components | `progress_bar_visual` | `base-components.yaml` |

**Actions:**
```powershell
# Check for progress bar templates
$templatesFile = "cortex-brain\response-templates-v4.yaml"
$content = Get-Content $templatesFile -Raw

if ($content -match "progress_bar.*█.*░") {
    Write-Host "✅ Progress bar templates valid"
} else {
    Write-Host "❌ Progress bar templates missing or invalid"
}

# Check autonomous execution defaults
$orchestrators = Get-ChildItem -Path "src\orchestrators" -Filter "*.py" -Recurse
foreach ($file in $orchestrators) {
    $fileContent = Get-Content $file.FullName -Raw
    if ($fileContent -match "auto_execute.*=.*True|autonomous_execution.*:.*True") {
        Write-Host "✅ $($file.Name): Autonomous execution enabled"
    }
}
```

**Python Toolkit:** `cortex-toolkit/maintenance/validate_templates.py`

---

### 2c. Remove Legacy 5-Part Template References 🗑️

**Purpose:** Remove ALL references to deprecated 5-part response templates.

**Target Patterns to DELETE:**
```yaml
inherits_from: core/base-templates/5-part-standard.yaml
5-part-standard
five-part-standard
5_part_standard
```

**Actions:**
```powershell
# Search for 5-part references
$files = Get-ChildItem -Path "cortex-brain\response-templates" -Filter "*.yaml" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "5-part|five-part|5_part") {
        Write-Host "🔧 Removing legacy references from: $($file.Name)"
        
        # Remove inherits_from lines
        $content = $content -replace "inherits_from:.*5-part.*\n", ""
        
        # Save cleaned content
        Set-Content -Path $file.FullName -Value $content
        Write-Host "✅ Cleaned: $($file.Name)"
    }
}
```

**Replacement Template:** `core/base-templates/adaptive-base.yaml`

**Python Toolkit:** `cortex-toolkit/maintenance/remove_legacy_refs.py`

---

### 2d. Resolve Duplicate Files 🔍

**Purpose:** Find and resolve conflicting duplicate files.

**Detection Algorithm:**
1. Find files with same base name in different locations
2. Compare content hashes (SHA-256)
3. If different content: identify correct version by:
   - Version number in header
   - Last modification date
   - Line count (more comprehensive usually correct)
4. Keep correct version, delete others

**Actions:**
```powershell
# Find duplicate template files
$duplicates = @{
    "response-templates-v4.yaml" = @(
        "cortex-brain\response-templates-v4.yaml"
    )
    "response-routing-rules.yaml" = @(
        "cortex-brain\response-routing-rules.yaml",
        "cortex-brain\response-templates\response-routing-rules.yaml"
    )
}

foreach ($name in $duplicates.Keys) {
    $files = $duplicates[$name]
    Write-Host "🔍 Checking duplicates for: $name"
    
    # Keep v4 or newest version
    $keepFile = $files | Where-Object { $_ -match "v4" } | Select-Object -First 1
    if (-not $keepFile) {
        $keepFile = $files | Sort-Object { (Get-Item $_).LastWriteTime } -Descending | Select-Object -First 1
    }
    
    # Delete others
    foreach ($file in $files) {
        if ($file -ne $keepFile -and (Test-Path $file)) {
            Write-Host "🗑️  Deleting duplicate: $file"
            Remove-Item -Path $file -Force
        }
    }
    
    Write-Host "✅ Kept: $keepFile"
}
```

**Python Toolkit:** `cortex-toolkit/maintenance/resolve_duplicates.py`

---

### 2e. Delete Backup Directories (from Phase 1 Discovery)

### 2e. Delete Backup Directories (from Phase 1 Discovery)

**ALL BACKUPS MUST BE DELETED.** No exceptions.

```bash
echo "🗑️  Phase 2e: Deleting backup directories from Phase 1 discovery..."

# Verify Phase 1 data exists
if [ ! -f /tmp/backup_dirs.txt ]; then
  echo "❌ ERROR: Phase 1 discovery data missing. Run Phase 1 first."
  exit 1
fi

# Count items to delete
BACKUP_DIRS=$(wc -l < /tmp/backup_dirs.txt)
echo "  Deleting $BACKUP_DIRS backup directories..."

# Delete each directory
cat /tmp/backup_dirs.txt | while read dir; do
  if [ -d "$dir" ]; then
    echo "    Deleting: $dir"
    rm -rf "$dir"
  fi
done

echo "  ✅ Backup directories deleted"
```

---

### 2f. Delete Backup Files (from Phase 1 Discovery)

```bash
echo "🗑️  Phase 2f: Deleting backup files from Phase 1 discovery..."

BACKUP_FILES=$(wc -l < /tmp/backup_files.txt)
echo "  Deleting $BACKUP_FILES backup files..."

# Delete each file
cat /tmp/backup_files.txt | while read file; do
  if [ -f "$file" ]; then
    echo "    Deleting: $file"
    rm -f "$file"
  fi
done

echo "  ✅ Backup files deleted"
```

---

### 2g. Consolidate Duplicate Reports (from Phase 1 Discovery)

### 2g. Consolidate Duplicate Reports (from Phase 1 Discovery)

```bash
echo "🗑️  Phase 2g: Consolidating duplicate reports from Phase 1 discovery..."

if [ -f /tmp/duplicate_names.txt ]; then
  DUPLICATE_COUNT=$(wc -l < /tmp/duplicate_names.txt)
  echo "  Consolidating $DUPLICATE_COUNT duplicate reports..."
  
  # For each duplicate, keep newest, delete older versions
  cat /tmp/duplicate_names.txt | while read report_name; do
    # Find all instances
    find cortex-brain/documents/reports/ -name "$report_name" -type f | sort -r | tail -n +2 | xargs rm -f
    echo "    Consolidated: $report_name"
  done
  
  echo "  ✅ Duplicate reports consolidated"
else
  echo "  ℹ️  No duplicate reports found"
fi
```

---

### 2h. Verify Cleanup Complete

**Verification that all cleanup sub-phases completed successfully:**

| Sub-Phase | Verification | Expected Result |
|-----------|--------------|-----------------|
| 2a - Caches | Check cache dirs empty | 0 cache files remain |
| 2b - Templates | Validate progress bars | All templates valid |
| 2c - Legacy | Search for 5-part refs | 0 references found |
| 2d - Duplicates | Check for duplicate files | 0 duplicates remain |
| 2e-2g - Backups | Verify Phase 1 targets deleted | 0 backups remain |

**⛔ WHY DELETE ALL BACKUPS?**
1. **Git is the backup system** - All changes are version controlled
2. **Backups create bloat** - Duplicate files waste disk space
3. **Backups confuse tools** - Search tools find stale copies
4. **Backups violate DRY** - Don't Repeat Yourself principle
  -name "*.bak" -o \
  -name "*~" -o \
  -name "*.old" -o \
  -name "*_backup_*" \
\) ! -path "./.git/*" ! -path "./node_modules/*" | sort > /tmp/cortex_backup_files.txt

# Count files found
BACKUP_FILE_COUNT=$(wc -l < /tmp/cortex_backup_files.txt)
echo "📄 Found $BACKUP_FILE_COUNT backup files"

# Display preview (first 20)
head -20 /tmp/cortex_backup_files.txt
```

**Expected Output:**
```
📄 Found 10+ backup files
./docs/features/planning-system.html.backup
./docs/features/orchestrators.html.backup
./cortex-brain/response-templates-v4.yaml.backup
./.github/workflows/deploy-docs.yml.backup
...
```

### 0c. Generate Deletion Report (DRY-RUN)

```bash
# Generate detailed deletion report
cat > /tmp/cortex_backup_cleanup_report.md << 'EOF'
# CORTEX Backup Cleanup Report
**Date:** $(date +%Y-%m-%d)
**Action:** DELETION (Irreversible)

## Summary

| Category | Count | Total Size |
|----------|-------|------------|
| Backup Directories | $(wc -l < /tmp/cortex_backup_dirs.txt) | $(du -sh $(cat /tmp/cortex_backup_dirs.txt 2>/dev/null) 2>/dev/null | awk '{sum+=$1} END {print sum "MB"}') |
| Backup Files | $(wc -l < /tmp/cortex_backup_files.txt) | $(du -ch $(cat /tmp/cortex_backup_files.txt 2>/dev/null) 2>/dev/null | tail -1 | awk '{print $1}') |

## Directories to Delete

\`\`\`
$(cat /tmp/cortex_backup_dirs.txt)
\`\`\`

## Files to Delete

\`\`\`
$(cat /tmp/cortex_backup_files.txt)
\`\`\`

## Justification

- **Git Version Control:** All code changes are in git history
- **No Data Loss:** Backups are redundant with git commits
- **Disk Space Recovery:** Removes duplicate files
- **Search Clarity:** Prevents tools from indexing stale copies

## Execution Command

To delete all backups, run:
\`\`\`bash
# Delete directories
cat /tmp/cortex_backup_dirs.txt | xargs rm -rf

# Delete files
cat /tmp/cortex_backup_files.txt | xargs rm -f

# Verify deletion
find . -type d -name "*backup*" ! -path "./.git/*" | wc -l
# Expected: 0
\`\`\`

EOF

# Display report
cat /tmp/cortex_backup_cleanup_report.md

# Save report to brain
cp /tmp/cortex_backup_cleanup_report.md cortex-brain/cleanup-reports/backup-cleanup-$(date +%Y%m%d_%H%M%S).md
```

### 0d. Execute Backup Deletion (AUTO-REPAIR)

**⚠️ THIS IS IRREVERSIBLE - ALL BACKUPS WILL BE PERMANENTLY DELETED**

```bash
# Step 1: Delete backup directories
echo "🗑️  Deleting backup directories..."
cat /tmp/cortex_backup_dirs.txt | while read dir; do
  if [ -d "$dir" ]; then
    echo "  Deleting: $dir"
    rm -rf "$dir"
  fi
done

# Step 2: Delete backup files
echo "🗑️  Deleting backup files..."
cat /tmp/cortex_backup_files.txt | while read file; do
  if [ -f "$file" ]; then
    echo "  Deleting: $file"
    rm -f "$file"
  fi
done

# Step 3: Verify deletion
echo ""
echo "✅ Verification:"
REMAINING_DIRS=$(find . -type d -name "*backup*" ! -path "./.git/*" | wc -l)
REMAINING_FILES=$(find . -type f \( -name "*.backup" -o -name "*.bak" \) ! -path "./.git/*" | wc -l)

echo "  Backup directories remaining: $REMAINING_DIRS (Expected: 0)"
echo "  Backup files remaining: $REMAINING_FILES (Expected: 0)"

if [ "$REMAINING_DIRS" -eq 0 ] && [ "$REMAINING_FILES" -eq 0 ]; then
  echo ""
  echo "✅ SUCCESS: All backups deleted!"
else
  echo ""
  echo "⚠️  WARNING: Some backups remain. Run discovery again."
fi
```

### 0e. Commit Cleanup to Git

```bash
# Stage deleted files
git add -A

# Commit with descriptive message
git commit -m "chore: delete all backup folders and files

- Removed backup directories: $(wc -l < /tmp/cortex_backup_dirs.txt)
- Removed backup files: $(wc -l < /tmp/cortex_backup_files.txt)
- Reason: Git version control makes backups redundant
- Disk space recovered: $(du -sh $(cat /tmp/cortex_backup_dirs.txt 2>/dev/null) 2>/dev/null | awk '{sum+=$1} END {print sum "MB"}')

Justification: 
- Git is the canonical backup system
- Backups create bloat and confuse search tools
- All changes are version controlled

Generated by: Phase 0 - Backup Cleanup"

# Push to remote
git push origin CORTEX-4.0
```

### 0f. Success Criteria

**✅ MANDATORY CHECKS:**

| Check | Command | Expected Result |
|-------|---------|-----------------|
| No backup directories | `find . -type d -name "*backup*" ! -path "./.git/*" \| wc -l` | `0` |
| No backup files | `find . -type f -name "*.backup" ! -path "./.git/*" \| wc -l` | `0` |
| No .bak files | `find . -type f -name "*.bak" ! -path "./.git/*" \| wc -l` | `0` |
| Changes committed | `git status --porcelain \| wc -l` | `0` |
| Cleanup report exists | `ls cortex-brain/cleanup-reports/backup-cleanup-*.md` | 1 file |

**If ANY check fails:**
1. Review remaining backups
2. Identify protection rules (e.g., `.gitignore`)
3. Delete manually or update discovery patterns
4. Re-run Phase 0 until 100% clean

### 0g. Prevention - Update .gitignore

**Add backup patterns to .gitignore to prevent future accumulation:**

```bash
# Add backup patterns to .gitignore
cat >> .gitignore << 'EOF'

# ========================================
# Backup Files (PHASE 0 CLEANUP)
# ========================================
# Git version control makes backups redundant
*.backup
*.bak
*~
*.old
*_backup_*
backup_*/
*backup*/

# Timestamped backups
*_backup_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*
*.backup.[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*

# Archive folders
archive/
archives/
_archive/
.archive/
old/
_old/

EOF

# Commit .gitignore update
git add .gitignore
git commit -m "chore: prevent backup file accumulation in .gitignore

- Added patterns for *.backup, *.bak, *~, *.old
- Block backup directories: backup_*/, archive/, old/
- Prevent timestamped backups: *_backup_YYYYMMDD_*

Reason: Git version control makes backups redundant.
Part of: Phase 0 - Backup Cleanup maintenance"

git push origin CORTEX-4.0
```

### 0h. Enforcement in CI/CD (Future Enhancement)

**Add pre-commit hook to reject backup files:**

```bash
# .git/hooks/pre-commit (future enhancement)
#!/bin/bash

BACKUP_FILES=$(git diff --cached --name-only | grep -E '\.(backup|bak|old)$|_backup_|backup_')

if [ -n "$BACKUP_FILES" ]; then
  echo "❌ ERROR: Backup files detected in commit:"
  echo "$BACKUP_FILES"
  echo ""
  echo "⛔ BLOCKED: Backup files violate Phase 0 cleanup rules."
  echo "   Git version control makes backups redundant."
  echo ""
  echo "Action required:"
  echo "  1. Delete backup files: git rm <file>"
  echo "  2. Use git history instead: git log <file>"
  echo "  3. Re-commit without backups"
  exit 1
fi

exit 0
```

---

## Phase 3: Data Preservation Validation ⛔

**Reference:** `cortex-brain/documents/implementation-guides/phase-2.5-data-preservation-rules.md`

**Purpose:** Protect critical user data during file regeneration operations (Phase 2 cleanup, Phase 9 prompt regeneration).

### Protected Fields in Plan Files

When regenerating plan files (`*.yaml`, `00-master-plan.md`), MUST preserve:

- **copilot_instructions** - GitHub Copilot runtime config (`response_template`, `progress_updates`, `tdd_enforcement`, `checkpoint_frequency`)
- **metadata.notes** - User annotations and implementation notes
- **metadata.tags** - User categorization
- **threat_analysis** - ThreatModeler output (STRIDE categories, mitigations)
- **session_metadata** - Execution history, checkpoints, rollback points

### Protected Fields in Response Templates

When regenerating `response-templates-v4.yaml`, MUST preserve:

- **named_templates** - All user-defined templates
- **named_templates.autonomous_execution_progress** - Planning orchestrator dependency
- **named_templates.*.format** - User customizations, progress bar layouts

### Preservation Process

**Before regenerating ANY file:**

1. **Extract protected fields** using `yq eval .copilot_instructions`, `.metadata.notes`, `.named_templates`
2. **Perform regeneration** (template/structure changes)
3. **Re-inject protected fields** using `yq eval-all` merge
4. **Verify preservation** with mandatory checks
5. **Commit with confirmation** including "Protected Fields Preserved" message

**Verification Example:**

```bash
# Verify copilot_instructions preserved in regenerated plan
COPILOT_CHECK=$(yq eval 'has("copilot_instructions")' plan.yaml)
if [ "$COPILOT_CHECK" != "true" ]; then
  echo "ERROR: copilot_instructions LOST during regeneration!"
  exit 1
fi
```

**Success Criteria:**

- All regenerated plans have `copilot_instructions` section
- `response-templates-v4.yaml` has `named_templates` section
- Git commits include preservation confirmation
- No user data loss after Phase 2 cleanup or Phase 9 regeneration

**Full implementation:** See `cortex-brain/documents/implementation-guides/phase-2.5-data-preservation-rules.md`

---

## Phase 4: Toolkit Scaffolding Validation 🛠️

### 4a. Verify Scaffold Generators Exist

**Critical:** Ensure automation utilities are present and functional.

```bash
# Check plan scaffold generator
test -f cortex-toolkit/core/utilities/plan_scaffold_generator.py || echo "ERROR: Plan scaffold generator missing!"

# Check orchestrator scaffold generator
test -f cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py || echo "ERROR: Orchestrator scaffold generator missing!"

# Verify both are registered in toolkit manifest
grep -q "plan-scaffold" cortex-toolkit/toolkit-manifest.yaml || echo "ERROR: Plan scaffold not registered!"
grep -q "orchestrator-scaffold" cortex-toolkit/toolkit-manifest.yaml || echo "ERROR: Orchestrator scaffold not registered!"
```

### 4a-2. Verify Interactive Planning Session ✨ NEW

**Critical:** Ensure interactive planning workflow is properly wired.

```bash
# Check interactive session module exists
test -f src/orchestrators/planning/interactive_session.py || echo "ERROR: Interactive session module missing!"

# Verify session states are defined
grep -q "class SessionState" src/orchestrators/planning/interactive_session.py || echo "ERROR: SessionState enum missing!"

# Check for key workflow classes
grep -q "class PlanningSession" src/orchestrators/planning/interactive_session.py || echo "ERROR: PlanningSession class missing!"
grep -q "class DiscoveryEngine" src/orchestrators/planning/interactive_session.py || echo "ERROR: DiscoveryEngine class missing!"
grep -q "class ApprovalWorkflow" src/orchestrators/planning/interactive_session.py || echo "ERROR: ApprovalWorkflow class missing!"
grep -q "class CleanupPhase" src/orchestrators/planning/interactive_session.py || echo "ERROR: CleanupPhase class missing!"
```

**Expected Workflow States:**
- `INITIALIZING` → `DISCOVERY` → `CONTEXT_GATHERING` → `USER_REVIEW`
- `USER_REVIEW` → `APPROVED` or `REFINING`
- `APPROVED` → `DRAFTING` → `CLEANUP` → `FINALIZED`

**Test Interactive Planning:**
```bash
# Run interactive planning tests (29 tests expected)
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v

# Expected: 18 session tests + 11 workflow tests = 29 total
```

### 4a-3. Verify Vision API Auto-Engagement 👁️ NEW

**Critical:** Ensure Vision API automatically engages when images are attached.

```bash
# Check vision orchestrator exists
test -f src/tier1/vision_orchestrator.py || echo "ERROR: Vision orchestrator missing!"

# Check image detector exists
test -f src/tier1/image_detector.py || echo "ERROR: Image detector missing!"

# Check vision context middleware
test -f src/operations/utilities/vision_context_middleware.py || echo "ERROR: Vision context middleware missing!"

# Verify auto-detection is enabled in config
grep -q "auto_detect_images" cortex.config.json || echo "WARNING: Auto-detect not configured!"
grep -q "auto_analyze_on_detect" cortex.config.json || echo "WARNING: Auto-analyze not configured!"
```

**Expected Features:**
- ✅ Automatic image detection in chat attachments
- ✅ Auto-engage Vision API without user prompting
- ✅ Context injection into planning/debugging workflows
- ✅ Duplicate image caching (24hr TTL)
- ✅ Token budget enforcement (500 token limit)

**Test Vision Auto-Engagement:**
```python
# Smoke test: Verify vision orchestrator detects images
from src.tier1.vision_orchestrator import VisionOrchestrator
from src.tier1.image_detector import ImageDetector

# Load config
import json
with open('cortex.config.json') as f:
    config = json.load(f)

# Initialize orchestrator
orchestrator = VisionOrchestrator(config)

# Test image detection (dry run)
result = orchestrator.process_request(
    user_request="analyze this",
    attachments=[
        {'type': 'image', 'path': '/path/to/test.png', 'mime': 'image/png'}
    ]
)

print(f"✅ Images found: {result['images_found']}")
print(f"✅ Auto-analyze: {orchestrator.auto_analyze}")
print(f"✅ Auto-inject: {orchestrator.inject_context}")
```

### 4b. Test Scaffold Generators

```bash
# Test plan scaffold generator (dry run)
python cortex-toolkit/core/utilities/plan_scaffold_generator.py "test-plan" --dry-run

# Test orchestrator scaffold generator (dry run)
python cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py --type planning "test-plan" --dry-run

# List available templates
python cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py --list-templates
```

**Expected Output:**
- ✅ Dry run shows 4 folders for planning (context, reports, artifacts, tracking)
- ✅ progress-tracker.json would be created
- ✅ All orchestrator templates listed (planning, sanitization, tdd, ado, maintenance)

### 4c. Verify Manifest Integration

Check that planning system manifest references automation:

```bash
# Verify automation section exists in planning manifest
grep -A 5 "automation:" cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
```

**Expected Fields:**
- `tool:` points to `plan_scaffold_generator.py`
- `usage:` shows command syntax
- `benefits:` lists automation advantages
- `enforcement:` references maintenance requirement

### 4d. Enforcement Rule

**⚠️ MANDATORY:** All new plans MUST use scaffold generator.

**Manual folder creation is DEPRECATED** as of CORTEX 4.0.1.

**Validation:** During Phase 7 (Regenerate Prompts), verify CORTEX.prompt.md and planning-system-4.0-manifest.yaml both enforce scaffold usage.

---

## Phase 5: Component Wiring 🔌 - AUTO-WIRE ALL GAPS

### ⚠️ ENHANCED WIRING DETECTION (December 30, 2025)

**Breakthrough:** Fixed wiring checker to use **CamelCase→snake_case conversion**, achieving 100% coverage.

**Before Fix:**
- Reported 14.6% coverage (45/309 wired)
- False negatives: "ApplicationHealthOrchestrator" vs "application_health_orchestrator"

**After Fix:**
- 100% coverage (299/299 wired)
- Proper name matching with snake_case conversion
- Excludes utility classes (OrchestratorStatus, AgentRequest, etc.)

---

### Phase 5a: Run Comprehensive Wiring Check (DIAGNOSE)

```powershell
# Use the proven wiring integrity checker
echo "🔍 Running comprehensive wiring check..."
python scripts/check_wiring_integrity.py

# Parse JSON report for unwired components
$latestReport = Get-ChildItem "cortex-brain/health-reports/wiring-report-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$report = Get-Content $latestReport.FullName | ConvertFrom-Json

$unwiredCount = $report.summary.unwired_count
$coverage = $report.summary.coverage_percentage

if ($unwiredCount -eq 0) {
    echo "✅ 100% WIRING COVERAGE - All $($report.summary.total_components) components wired!"
    echo "👉 Skipping Phase 5b - no wiring needed"
} else {
    echo "⚠️  WIRING GAPS DETECTED: $unwiredCount components unwired ($coverage% coverage)"
    echo "👉 Proceeding to Phase 5b - Auto-wiring"
}
```

**Success Criteria:**
- JSON report generated in `cortex-brain/health-reports/`
- Coverage percentage calculated correctly
- Unwired components listed by category (orchestrators, agents, modules, plugins)

---

### Phase 5b: Auto-Wire Components (AUTO-REPAIR) 🔥

**⚠️ ONLY RUN IF Phase 5a detected unwired components**

```powershell
# Check if wiring needed
$latestReport = Get-ChildItem "cortex-brain/health-reports/wiring-report-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$report = Get-Content $latestReport.FullName | ConvertFrom-Json

if ($report.summary.unwired_count -gt 0) {
    echo "🔧 Auto-wiring $($report.summary.unwired_count) components..."
    
    # Option 1: Use bulk wiring tool (RECOMMENDED)
    python scripts/bulk_wire_components.py --report $latestReport.FullName --execute
    
    # Option 2: Manual wiring entries (if bulk tool fails)
    # Add unwired components to cortex-operations.yaml
    # Format: {snake_case_name}: {relative_path_to_module}
    
    echo "✅ Wiring entries added to cortex-operations.yaml"
    
    # Verify wiring success
    echo "🔍 Re-running wiring check to verify..."
    python scripts/check_wiring_integrity.py
    
    $newReport = Get-ChildItem "cortex-brain/health-reports/wiring-report-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $newData = Get-Content $newReport.FullName | ConvertFrom-Json
    
    if ($newData.summary.unwired_count -eq 0) {
        echo "🎉 SUCCESS: 100% wiring coverage achieved!"
    } else {
        echo "⚠️  WARNING: $($newData.summary.unwired_count) components still unwired"
        echo "👉 Manual intervention may be required"
    }
} else {
    echo "✅ No wiring needed - skipping auto-wire step"
}
```

**Why Bulk Wiring Works:**
- Reads unwired components from Phase 5a JSON report
- Generates proper YAML entries with relative paths
- Merges into `cortex-operations.yaml` without duplicates
- Git-committable changes persist across machines

**Reference:** `scripts/bulk_wire_components.py` (269 LOC, proven in production)

---

### Phase 5c: Validate Response Template Wiring 🎯

**Check template file references are correct:**

```powershell
# Check for obsolete template references
echo "🔍 Validating response template references..."

$badRefs = Select-String -Path "src\**\*.py" -Pattern "response-templates\.yaml" -Exclude "*response-templates-v4*"

if ($badRefs.Count -gt 0) {
    echo "⚠️  Found $($badRefs.Count) files referencing old template file"
    
    # Auto-fix: Update to v4
    foreach ($match in $badRefs) {
        $file = $match.Path
        (Get-Content $file) -replace 'response-templates\.yaml', 'response-templates-v4.yaml' | Set-Content $file
    }
    
    echo "✅ Updated all references to response-templates-v4.yaml"
} else {
    echo "✅ All template references correct (v4)"
}

# Verify no duplicate template files
if (Test-Path "cortex-brain\response-templates.yaml") {
    echo "⚠️  Old template file exists - archiving..."
    Move-Item "cortex-brain\response-templates.yaml" "cortex-brain\archives\response-templates-v3-legacy.yaml"
    echo "✅ Legacy template archived"
} else {
    echo "✅ No template file conflicts"
}
```

---

### Phase 5d: Final Verification (VERIFY)

```powershell
# Final wiring check
echo "🔍 Final wiring verification..."
python scripts/check_wiring_integrity.py

# Expected: 100% coverage
$finalReport = Get-ChildItem "cortex-brain/health-reports/wiring-report-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$finalData = Get-Content $finalReport.FullName | ConvertFrom-Json

if ($finalData.summary.coverage_percentage -eq 100) {
    echo "✅ Phase 5 Complete: 100% wiring coverage verified"
    echo "📊 Total Components: $($finalData.summary.total_components)"
    echo "✅ All Wired: $($finalData.summary.wired_count)"
} else {
    echo "❌ Phase 5 Failed: Coverage at $($finalData.summary.coverage_percentage)%"
    echo "⚠️  $($finalData.summary.unwired_count) components still unwired"
    exit 1
}
```

**Success Criteria:**
- ✅ 100% wiring coverage (unwired_count = 0)
- ✅ All template references use v4 file
- ✅ No duplicate template files
- ✅ Changes committed to git
- ✅ Wiring persists across `git pull` on other machines

**Expected Output:**
```
🔧 CORTEX Auto-Wiring Script v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Wiring Gaps Detected:
  ❌ Planning Orchestrator: Decision logic not called
  ❌ Agent Registry: InteractivePlanner missing

🔧 Applying Fixes...
  [1/4] Wiring decision logic... ✅ SUCCESS (18 lines modified)
  [2/4] Creating agent registry... ✅ SUCCESS (23 lines added)
  [3/4] Wiring execution method... ⏭️  SKIPPED (exists)
  [4/4] Updating operations config... ✅ SUCCESS (1 field modified)

✅ Wiring Coverage: 100% (was 50%)
```

### 5d. Commit Wiring Fixes

**⚠️ CRITICAL:** These changes MUST be committed to persist across machines.

```bash
# Review changes
git diff src/orchestrators/ src/cortex_agents/ cortex-operations.yaml

# Stage wiring fixes
git add src/orchestrators/planning/planning_orchestrator.py
git add src/cortex_agents/agent_registry.py
git add cortex-operations.yaml

# Commit with descriptive message
git commit -m "fix: auto-wire planning orchestrator interactive mode

- Added interactive mode check in execute() method
- Created agent_registry.py with InteractivePlanner registration
- Updated cortex-operations.yaml with interactive_mode flag

Wiring coverage: 50% → 100%
Generated by: scripts/auto_wire_orchestrators.py"

# Push to remote
git push origin CORTEX-4.0
```

### 5e. Verify Persistence on Another Machine

```bash
# On Machine B (fresh clone or pull)
git pull origin CORTEX-4.0

# Verify wiring WITHOUT running auto-wire script
python3 scripts/check_wiring_integrity.py

# Expected: 100% wiring coverage (no manual fixes needed)
```

**Success Criteria:**
- ✅ Auto-wire script runs without errors
- ✅ Source files modified (planning_orchestrator.py, agent_registry.py, cortex-operations.yaml)
- ✅ Wiring check shows 100% coverage
- ✅ Changes committed and pushed to remote
- ✅ `git pull` on Machine B shows 100% wiring (without re-running auto-wire)

### 5f. Troubleshooting

**Issue:** Auto-wire script fails with "No wiring report found"

**Solution:**
```bash
# Generate fresh wiring report first
python3 scripts/check_wiring_integrity.py
# Then run auto-wire
python3 scripts/auto_wire_orchestrators.py --execute
```

**Issue:** Wiring coverage still <100% after auto-wire

**Solution:**
```bash
# Check which components are still unwired
python3 scripts/check_wiring_integrity.py | grep "❌"
# Review auto-wire log for skipped patterns
cat cortex-brain/health-reports/auto-wire-log-*.txt
```

**Issue:** Need to undo auto-wiring changes

**Solution:**
```bash
# Restore from automatic backups
python3 scripts/auto_wire_orchestrators.py --undo
# Or manually restore from .bak files
ls -lah src/**/*.bak.*
```

---

## Phase 6: Test Suite Health 🧪 - ZERO TOLERANCE POLICY

### ⚠️ CRITICAL ENFORCEMENT RULE

**NO TEST FAILURES ALLOWED.** Period.

If tests fail during maintenance:
1. **Identify root cause** - Is functionality broken OR is test obsolete?
2. **Fix or DELETE** - Either fix the code OR delete the obsolete test
3. **Never settle** - "99% pass rate" = FAILURE. Target is 100%.

### When to Run Tests

Run the full test suite during maintenance when:
- ✅ **Interactive planning system** has been modified
- ✅ **Core orchestrators** have been updated
- ✅ **Brain protection rules** have changed
- ✅ **Fixture patterns** need validation
- ❌ **Minor documentation updates** (skip tests)
- ❌ **Knowledge library additions** (skip tests unless validation required)

### Test Suite Execution

**⚠️ CRITICAL: Always run tests SEQUENTIALLY (never in parallel) to avoid race conditions and flaky test results.**

```bash
# Run full planning orchestrator test suite SEQUENTIALLY (MUST be 100% passing)
python3 -m pytest tests/orchestrators/planning/ --tb=short -v -n0

# REQUIRED: 100% pass rate (no failures, no errors, no skips without justification)
# -n0 flag ensures sequential execution (no parallel workers)

# Run core functionality tests only (faster validation) - SEQUENTIAL
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py \
                 tests/orchestrators/planning/test_toolkit_integration.py \
                 tests/orchestrators/planning/test_interactive_workflow_integration.py -v -n0

# REQUIRED: 100% passing (currently 42/48 total core tests)

# Alternative: Use Python test runner script for sequential execution
python3 run_tests_sequential.py tests/orchestrators/planning/

# Use test runner script for specific categories (all run sequentially)
./test_planning.sh interactive   # Interactive session workflow
./test_planning.sh toolkit        # Toolkit integration
./test_planning.sh wiring         # Interactive wiring validation
./test_planning.sh quick          # Core functionality only
./test_planning.sh all            # Full suite
```

### Test Health Metrics - ZERO TOLERANCE

| Metric | REQUIRED | Action if NOT Met |
|--------|----------|-------------------|
| **Core Tests Pass Rate** | **100%** | **STOP MAINTENANCE - Fix immediately or delete obsolete tests** |
| **Full Suite Pass Rate** | **100%** | **DELETE obsolete tests or refactor to match current functionality** |
| **Error Count** | **0** | **CRITICAL - Fix all errors before continuing** |
| **Failure Count** | **0** | **CRITICAL - No failures allowed** |
| **Test Execution Time** | <30s | Acceptable, monitor for regression |

### Obsolete Test Detection & Deletion Protocol

**When functionality changes (e.g., Planning orchestrator refactored), tests MUST be updated or deleted.**

#### Step 1: Identify Obsolete Tests

```bash
# Run tests and capture failures
python3 -m pytest tests/orchestrators/planning/ -v --tb=line 2>&1 | tee test_results.txt

# Look for these patterns indicating obsolete tests:
grep -E "(AttributeError|ImportError|ModuleNotFoundError)" test_results.txt
grep -E "test.*old.*api" test_results.txt
grep -E "DEPRECATED|LEGACY|OLD" tests/orchestrators/planning/*.py
```

**Red Flags for Obsolete Tests:**
- ❌ Tests for methods/classes that no longer exist
- ❌ Tests importing deprecated modules
- ❌ Tests with `@pytest.mark.skip` without clear justification
- ❌ Tests passing but not exercising actual code paths (mocks everything)
- ❌ Tests for APIs that were refactored but tests weren't updated

#### Step 2: Classify Failures

For EACH failing test, determine:

**A. Obsolete Test (DELETE)**
- Tests code that was intentionally removed/refactored
- Tests deprecated APIs with no replacement
- Tests mock-heavy scenarios that don't validate real behavior
- Tests marked "TODO" or "WIP" for >30 days

**B. Misaligned Test (REFACTOR)**
- Tests valid functionality but uses old API
- Tests correct behavior but with wrong assertions
- Tests proper code path but with outdated fixtures

**C. Real Bug (FIX CODE)**
- Tests valid, current functionality that's actually broken
- Tests core behavior that should work but doesn't

#### Step 3: Execute Cleanup

```bash
# Create cleanup manifest
cat > /tmp/test_cleanup_plan.md << 'EOF'
# Test Cleanup Plan - $(date +%Y-%m-%d)

## Tests to DELETE (Obsolete)
- [ ] tests/orchestrators/planning/test_old_planning_api.py - Uses deprecated PlanningOrchestrator v3 API
- [ ] tests/orchestrators/planning/test_legacy_validation.py - Tests removed ValidationEngine

## Tests to REFACTOR (Misaligned)
- [ ] tests/orchestrators/planning/test_execute_workflow.py - Update to use new execute() signature
- [ ] tests/orchestrators/planning/test_plan_generation.py - Update fixtures for new folder structure

## Tests to FIX (Real Bugs)
- [ ] tests/orchestrators/planning/test_error_handling.py - Core error handling broken, fix orchestrator

## Justification
- Functionality changed: Planning orchestrator refactored in CORTEX 4.0.1 with interactive wiring
- Old tests validate APIs that no longer exist
- New tests created: test_interactive_workflow_integration.py (19 tests)
EOF

# Review and approve cleanup plan
cat /tmp/test_cleanup_plan.md

# DELETE obsolete tests (after approval)
git rm tests/orchestrators/planning/test_old_*.py
git rm tests/orchestrators/planning/test_legacy_*.py

# Commit cleanup
git add -A
git commit -m "test: delete obsolete planning tests after orchestrator refactor

- Removed tests for deprecated v3 API
- Removed tests for removed ValidationEngine
- Kept: 42 core tests (100% passing)
- Added: test_interactive_workflow_integration.py (19 tests)

Justification: Planning orchestrator refactored with interactive wiring.
Old tests validate non-existent APIs. New tests cover current functionality."
```

#### Step 4: Validate 100% Pass Rate

```bash
# Run tests again - MUST be 100% passing
python3 -m pytest tests/orchestrators/planning/ -v

# If ANY test fails:
# - Go back to Step 1
# - Do NOT proceed with maintenance until 100% passing

# Generate cleanup report
python3 scripts/generate_test_cleanup_report.py \
  --before test_results.txt \
  --after test_results_clean.txt \
  --output cortex-brain/documents/reports/test-suite-cleanup-$(date +%Y%m%d).md
```

### Common Test Failure Patterns & Solutions

| Failure Pattern | Root Cause | Solution |
|----------------|------------|----------|
| `AttributeError: 'Orchestrator' object has no attribute 'old_method'` | Method removed during refactor | **DELETE** test (obsolete) |
| `ModuleNotFoundError: No module named 'old_module'` | Module renamed/removed | **DELETE** test (obsolete) |
| `AssertionError: Expected 'old_value' but got 'new_value'` | Behavior changed intentionally | **REFACTOR** test assertions |
| `RuntimeError: Config missing required key` | New config requirements | **REFACTOR** fixtures |
| `TypeError: execute() missing 1 required positional argument` | Signature changed | **REFACTOR** test calls |
| Tests pass but coverage shows code not executed | Over-mocked, not testing real code | **REFACTOR** to use real implementations |

### Test Refactoring Guidelines

When refactoring tests to match new functionality:

**1. Update Fixtures**
```python
# OLD (obsolete)
@pytest.fixture
def orchestrator():
    return PlanningOrchestrator()  # Old API, no config

# NEW (current)
@pytest.fixture
def orchestrator():
    config = {
        "cortex_root": "/path/to/CORTEX",
        "brain_dir": "cortex-brain",
    }
    return PlanningOrchestrator(config=config)  # New API
```

**2. Update Method Calls**
```python
# OLD (obsolete)
result = orchestrator.generate_plan(name="test")

# NEW (current)
result = orchestrator.execute(feature_name="test", interactive=False)
```

**3. Update Assertions**
```python
# OLD (obsolete)
assert result.status == "success"

# NEW (current)
assert result.status == OrchestratorStatus.SUCCESS
assert result.data["mode"] == "autonomous"
```

**4. Reduce Mocking**
```python
# OLD (over-mocked, doesn't test real behavior)
@patch('orchestrator.generate')
@patch('orchestrator.validate')
@patch('orchestrator.render')
def test_execute(mock_render, mock_validate, mock_generate):
    # Test passes but doesn't validate actual orchestrator behavior
    pass

# NEW (tests real integration)
def test_execute_autonomous_mode(orchestrator, tmp_path):
    # Use real orchestrator with real filesystem
    result = orchestrator.execute(feature_name="test", output_dir=tmp_path)
    assert result.status == OrchestratorStatus.SUCCESS
    # Validates real file creation, not mocked behavior
```

### Maintenance Enforcement

**❌ BLOCKING CONDITION:** If test pass rate < 100%, maintenance CANNOT proceed.

**Required Actions:**
1. ✅ Identify ALL failing tests
2. ✅ Classify each as Obsolete / Misaligned / Real Bug
3. ✅ DELETE obsolete tests immediately
4. ✅ REFACTOR misaligned tests to match current API
5. ✅ FIX real bugs in code
6. ✅ Re-run tests - MUST achieve 100% pass rate
7. ✅ Commit cleanup with detailed justification
8. ✅ Generate test cleanup report

**Only then** can maintenance continue to next phase.

### Test Report Location

After running tests and cleanup, check:
- `cortex-brain/documents/reports/test-suite-cleanup-{DATE}.md` for cleanup report
- Report MUST show: Before → After with 100% pass rate achieved

---

## Phase 7: Knowledge Library Validation 📚 CRITICAL

### 7a. Knowledge Library Structure Check

**Source of Truth:** `cortex-brain/knowledge/`

Verify knowledge library structure and accessibility:

```bash
# Verify knowledge library structure
test -d cortex-brain/knowledge || echo "ERROR: Knowledge library missing!"

# Count knowledge files by category
for dir in cortex-brain/knowledge/*/; do
  echo "$(basename "$dir"): $(find "$dir" -name "*.yaml" | wc -l) files"
done

# Verify README exists and is current
test -f cortex-brain/knowledge/README.md || echo "ERROR: Knowledge README missing!"

# Check for orphaned YAML files (not in a category)
find cortex-brain/knowledge/ -maxdepth 1 -name "*.yaml" -type f
```

**Expected Categories:**
- `database/` - Database best practices (Oracle, SQL Server, etc.)
- `ddd/` - Domain-Driven Design patterns
- `devops/` - DevOps and infrastructure
- `domains/` - Domain-specific knowledge (RAG, embeddings)
- `engineering/` - Software engineering principles
- `performance/` - Performance optimization
- `security/` - Security best practices
- `testing/` - Testing strategies and patterns
- `ui-ux/` - UI/UX design guidelines

### 7a.1 Security Injection Verification (Phase 2 - Security Enhancement)

**Purpose:** Verify that automatic security injection is active in all orchestrators.

**This sub-phase validates Phase 2 Security Enhancement requirements:**

| Orchestrator | Security Injection Method | Verification |
|--------------|---------------------------|--------------|
| **Planning Orchestrator** | `_inject_automatic_security_section()` | Method exists and is called in `_generate_plan()` |
| **ADO Orchestrator** | Security work item templates | Manifest has `phase2_enhancement` sections |
| **TDD Orchestrator** | Security test generation in RED phase | Manifest has security test patterns |
| **Maintenance** | This verification (7a.1) | Self-verifying |

**Validation Commands:**

```bash
# Check Planning Orchestrator has security injection
grep -q "_inject_automatic_security_section" src/orchestrators/planning/planning_orchestrator.py && \
  echo "✅ Planning Orchestrator: Security injection method exists" || \
  echo "❌ Planning Orchestrator: Missing _inject_automatic_security_section()"

# Check security injection is called in plan generation
grep -A 5 "_generate_plan" src/orchestrators/planning/planning_orchestrator.py | \
  grep -q "_inject_automatic_security_section" && \
  echo "✅ Planning Orchestrator: Security injection is called" || \
  echo "❌ Planning Orchestrator: Security injection NOT called in _generate_plan()"

# Check security knowledge constants exist
grep -q "SECURITY_KNOWLEDGE_LIBRARY_PATH" src/orchestrators/planning/planning_orchestrator.py && \
  echo "✅ Planning Orchestrator: Security knowledge path defined" || \
  echo "❌ Planning Orchestrator: Missing SECURITY_KNOWLEDGE_LIBRARY_PATH"

# Check ADO manifest has security enhancements
grep -q "phase2_enhancement" cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml && \
  echo "✅ ADO Manifest: Phase 2 security enhancement configured" || \
  echo "❌ ADO Manifest: Missing phase2_enhancement sections"

# Check ADO has security work item templates
grep -q "security_story_templates" cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml && \
  echo "✅ ADO Manifest: Security story templates defined" || \
  echo "❌ ADO Manifest: Missing security_story_templates"

# Check TDD manifest has security test generation
grep -q "security.*test\|Security Testing" cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml && \
  echo "✅ TDD Manifest: Security testing configured" || \
  echo "❌ TDD Manifest: Missing security test generation"

# Verify security knowledge library exists
test -d cortex-brain/knowledge-library/security && \
  echo "✅ Security knowledge library exists" || \
  echo "❌ Security knowledge library missing!"

# Count security knowledge documents
SECURITY_DOCS=$(find cortex-brain/knowledge-library/security -name "*.md" | wc -l | tr -d ' ')
echo "📊 Security knowledge documents: $SECURITY_DOCS"
if [ "$SECURITY_DOCS" -lt 10 ]; then
  echo "⚠️ Warning: Expected at least 10 security documents (Phase 1 deliverables)"
fi
```

**Expected Results (Phase 2 Complete):**

| Check | Expected | Auto-Repair |
|-------|----------|-------------|
| `_inject_automatic_security_section()` exists | ✅ Method defined | Alert if missing |
| Security injection called in `_generate_plan()` | ✅ Called | Alert if missing |
| `SECURITY_KNOWLEDGE_LIBRARY_PATH` defined | ✅ Constant exists | Alert if missing |
| ADO `phase2_enhancement` sections | ✅ Present | Alert if missing |
| ADO `security_story_templates` | ✅ Defined | Alert if missing |
| TDD security test generation | ✅ Configured | Alert if missing |
| Security knowledge library | ✅ ≥10 documents | Alert if missing |

**🔧 Auto-Repair Actions:**

If security injection missing from Planning Orchestrator:
```
❌ CRITICAL: Security injection not implemented in Planning Orchestrator
   Action: Review Phase 2 Security Enhancement implementation
   Reference: cortex-brain/documents/planning/active/security-enhancement/00-master-plan.md
```

If ADO security templates missing:
```
❌ CRITICAL: ADO security work item templates not configured
   Action: Update ado-planning-manifest.yaml with security_story_templates
   Reference: Phase 2.2 ADO Integration Security Injection
```

**Success Criteria:**
- ✅ ALL coding plans automatically include threat modeling section
- ✅ ADO work items automatically include security stories  
- ✅ Security knowledge library accessible (17+ documents from Phase 1)
- ✅ Planning, ADO, TDD orchestrators have security integration

### 7a.2 Security Folder Verification in Plans (Phase 3 - Security Documentation)

**Purpose:** Verify that all active plans have the required security/ subfolder and security-documentation.md.

**This sub-phase validates Phase 3 Security Documentation Automation requirements.**

| Component | Verification | Auto-Repair |
|-----------|--------------|-------------|
| Security folder exists | `{plan}/security/` directory | Create if missing |
| Security documentation exists | `security-documentation.md` | Generate from template |
| Security template exists | `cortex-brain/templates/security/plan-security-template.md` | Alert if missing |
| Scaffold generator updated | `--retrofit-security` option works | Alert if missing |

**Validation Commands:**

```bash
# Check security folder template exists
test -f cortex-brain/templates/security/plan-security-template.md && \
  echo "✅ Security template exists" || \
  echo "❌ Security template missing!"

# Check security documentation standards
test -f cortex-brain/knowledge-library/security/security-documentation-standards.md && \
  echo "✅ Security documentation standards exist" || \
  echo "❌ Security documentation standards missing!"

# Count plans with security folders
PLANS_TOTAL=$(find cortex-brain/documents/planning/active -maxdepth 1 -type d | wc -l | tr -d ' ')
PLANS_WITH_SECURITY=$(find cortex-brain/documents/planning/active -maxdepth 2 -type d -name "security" | wc -l | tr -d ' ')

echo "📊 Plans with security folders: $PLANS_WITH_SECURITY / $PLANS_TOTAL"

# List plans missing security folders
echo "🔍 Plans missing security folders:"
for plan in cortex-brain/documents/planning/active/*/; do
  if [ ! -d "$plan/security" ]; then
    echo "   ❌ $(basename "$plan")"
  fi
done

# Check scaffold generator has retrofit capability
grep -q "retrofit_security_folder\|--retrofit-security" cortex-toolkit/core/utilities/plan_scaffold_generator.py && \
  echo "✅ Scaffold generator: Security retrofit capability exists" || \
  echo "❌ Scaffold generator: Missing retrofit capability"
```

**Expected Results (Phase 3 Complete):**

| Check | Expected | Auto-Repair |
|-------|----------|-------------|
| Security template exists | ✅ | Alert if missing |
| Security documentation standards | ✅ | Alert if missing |
| All plans have security/ folder | ✅ 100% | Retrofit missing |
| Security documentation in each plan | ✅ | Generate from template |
| Scaffold generator updated | ✅ | Alert if missing |

**🔧 Auto-Repair Actions:**

If plan missing security folder:
```bash
# Retrofit single plan
python3 cortex-toolkit/core/utilities/plan_scaffold_generator.py "{plan-name}" --retrofit-security

# Retrofit ALL plans (batch operation)
python3 cortex-toolkit/core/utilities/plan_scaffold_generator.py --retrofit-all
```

Report format for missing security folders:
```
⚠️ WARNING: {count} plans missing security folders

Plans requiring security retrofit:
   • {plan-name-1}
   • {plan-name-2}

Auto-repair: Running --retrofit-all...
✅ Retrofitted {count} plans with security folders
```

**Success Criteria:**
- ✅ ALL active plans have `security/` subfolder
- ✅ ALL active plans have `security/security-documentation.md`
- ✅ Security template is available for new plans
- ✅ Scaffold generator automatically includes security folder
- ✅ Retrofit capability available for existing plans

### 7b. Knowledge Library Reference Validation

**Critical:** Ensure orchestrators and modules can reference knowledge library.

Verify these systems wire to knowledge library:

| System | Knowledge Usage | Verification |
|--------|----------------|--------------|
| **Code Review Orchestrator** | Validates code against guidelines | Check manifest references `cortex-brain/knowledge/` |
| **Sanitization Orchestrator** | Applies best practices during cleanup | Check for knowledge library imports |
| **Refactoring Orchestrator** | Identifies anti-patterns | Check pattern detection references |
| **TDD Orchestrator** | Guides test design | Check test pattern references |
| **Documentation Generator** | Auto-generates docs from guidelines | Check template references |

### 7c. Knowledge Library Sync Validation (NEW)

**Critical:** Ensure markdown templates stay in sync with YAML knowledge library.

```bash
# Run knowledge library sync check
python3 scripts/sync_knowledge_library.py --check-status

# Generate sync report
python3 scripts/sync_knowledge_library.py --report > cortex-brain/health-reports/knowledge-sync-report.md
```

**Expected Output:**
```
📊 Knowledge Library Sync Status

✅ glassmorphism-design-standards: none (in sync)
⚠️  [other-file]: sync_md_to_yaml (markdown changed)
```

**If out of sync detected:**
```bash
# Dry run to preview changes
python3 scripts/sync_knowledge_library.py --sync-all --dry-run

# Perform sync (updates hashes, flags manual review)
python3 scripts/sync_knowledge_library.py --sync-all
```

**Sync Registry Files:**
- `glassmorphism-design-standards.yaml` ↔ `glassmorphism-design-standards-v2.md`
- Future template ↔ YAML pairs automatically detected via `metadata.sync` section

### 7d. Knowledge File Schema Validation

Each knowledge YAML must have:

```yaml
metadata:
  title: "Guideline Name"
  category: "Category"
  version: "X.Y"
  created: "YYYY-MM-DD"
  updated: "YYYY-MM-DD"
  tags: [tag1, tag2, ...]
  
  # Sync configuration (if synced with markdown template)
  sync:
    source_markdown: "cortex-brain/documents/templates/filename.md"
    sync_enabled: true
    sync_direction: "bidirectional"
    last_sync: "2025-12-29T00:00:00Z"
  
  generated_docs:
    - path: "docs/guidelines/{category}/{filename}.md"

{category}_section:
  principle: "Core principle statement"
  importance: "Why it matters"
  rules:
    - id: "unique_id_###"
      name: "Rule Name"
      severity: "CRITICAL|HIGH|MEDIUM|LOW"
      examples:
        good: [...]
        bad: [...]
```

### 7e. Validation Commands

```bash
# Check all YAML files for metadata section
for f in cortex-brain/knowledge/**/*.yaml; do
  grep -q "metadata:" "$f" || echo "MISSING metadata: $f"
done

# Verify severity levels are valid
for f in cortex-brain/knowledge/**/*.yaml; do
  grep -E "severity: \"(CRITICAL|HIGH|MEDIUM|LOW)\"" "$f" > /dev/null || \
    echo "Invalid severity in: $f"
done

# Check for duplicate rule IDs
grep -rh "id: \"" cortex-brain/knowledge/ | sort | uniq -d

# Verify README is up to date (check statistics)
grep "Total:" cortex-brain/knowledge/README.md
```

### 7f. Integration Verification

Verify orchestrators can load knowledge library:

```bash
# Check for knowledge library imports in orchestrators
grep -r "knowledge" src/orchestrators/*.py | grep -E "(import|load|read)"

# Check for knowledge references in manifests
grep -r "knowledge" cortex-brain/manifests/orchestrators/*.yaml

# Verify brain protection rules reference knowledge library
grep -A 5 "knowledge" cortex-brain/brain-protection-rules.yaml
```

### 7g. Knowledge Library Health Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total Guidelines | 30 | 30+ | ✅ |
| Categories | 9 | 8+ | ✅ |
| Total Rules | 525+ | 500+ | ✅ |
| Critical Rules | 77+ | 75+ | ✅ |
| Files with Metadata | 30/30 | 100% | ✅ |
| Files with Examples | 30/30 | 100% | ✅ |

### 7h. Plan Content Validation (Rule 9 Enforcement) 🚨 NEW

**Critical:** Validate ALL active plans have mandatory sections per Rule 9.

**Validation Script:**

```bash
echo "🔍 Validating plan content (Rule 9)..."

PLANS_CHECKED=0
PLANS_FAILED=0

for plan in cortex-brain/documents/planning/active/*/00-master-plan.md; do
  if [ ! -f "$plan" ]; then continue; fi
  
  PLANS_CHECKED=$((PLANS_CHECKED + 1))
  PLAN_NAME=$(basename $(dirname "$plan"))
  ISSUES=""
  
  # Check 1: Visual Progress Tracking (progress bars)
  if ! grep -qE "\[█|░\]|Progress.*%|\`█+░*\`" "$plan" 2>/dev/null; then
    ISSUES="$ISSUES\n  ❌ Missing: Visual progress tracking"
  fi
  
  # Check 2: Response Template Reference
  if ! grep -qi "autonomous_execution_progress\|response-templates-v4\.yaml\|response_template" "$plan" 2>/dev/null; then
    ISSUES="$ISSUES\n  ❌ Missing: Response template reference"
  fi
  
  # Check 3: Final REFACTOR Phase
  if ! grep -qiE "final.*refactor|refactor.*phase.*mandatory|SKULL.*REFACTOR|Phase.*6.*REFACTOR" "$plan" 2>/dev/null; then
    ISSUES="$ISSUES\n  ❌ Missing: Final REFACTOR phase (SKULL enforcement)"
  fi
  
  # Check 4: copilot_instructions or equivalent
  if ! grep -qi "copilot_instructions\|tdd_enforcement.*true\|final_refactor_required" "$plan" 2>/dev/null; then
    ISSUES="$ISSUES\n  ❌ Missing: copilot_instructions block"
  fi
  
  if [ -n "$ISSUES" ]; then
    echo "⚠️  Plan: $PLAN_NAME"
    echo -e "$ISSUES"
    PLANS_FAILED=$((PLANS_FAILED + 1))
  else
    echo "✅ Plan: $PLAN_NAME - All requirements met"
  fi
done

echo ""
echo "📊 Plan Content Validation Summary:"
echo "   Plans checked: $PLANS_CHECKED"
echo "   Plans passing: $((PLANS_CHECKED - PLANS_FAILED))"
echo "   Plans failing: $PLANS_FAILED"

if [ $PLANS_FAILED -gt 0 ]; then
  echo ""
  echo "🔧 AUTO-REPAIR: Run plan content fixer..."
  # Auto-repair triggered in next step
fi
```

**Auto-Repair Action:**

When plan fails validation, append mandatory sections:

```bash
# For each failing plan, append missing sections
for plan in cortex-brain/documents/planning/active/*/00-master-plan.md; do
  # Check if already has all requirements
  if grep -qi "MANDATORY Requirements.*Auto-Added" "$plan" 2>/dev/null; then
    continue  # Already fixed
  fi
  
  # Append mandatory section template
  cat >> "$plan" << 'MANDATORY_SECTION'

---

## ⚠️ MANDATORY Requirements (Auto-Added by Maintenance)

### Visual Progress Tracking
Use `autonomous_execution_progress` template from `response-templates-v4.yaml` (line 863)

| # | Phase | Status | Progress | TDD Status |
|---|-------|--------|----------|------------|
| **Overall** | 🟡 | `[░░░░░░░░░░░░░░░░░░░░]` 0% | Phase 0/N | - |

### Response Template Helpers
- `generate_progress_bar(percentage, width=20, filled='█', empty='░')`
- `generate_tdd_status(red_done, green_done, refactor_done)`
- `render_autonomous_progress(...)` - Full convenience method

### Final REFACTOR Phase (MANDATORY - SKULL Rule)
Per `REFACTOR_CODE_CLEANUP_ENFORCEMENT`:
- ✅ Whole-file cleanup (not just new code)
- ✅ Complexity ≤30 for all functions
- ✅ SOLID principles enforced
- ✅ Zero dead code/unused imports
- ✅ 100% test pass rate

### copilot_instructions
```yaml
copilot_instructions:
  response_template: "autonomous_execution_progress"
  progress_updates: true
  tdd_enforcement: true
  final_refactor_required: true
  checkpoint_frequency: "per_phase"
```

**Reference:** `planning-system-4.0-manifest.yaml` (lines 118-157, 639-677)

MANDATORY_SECTION

  echo "✅ Auto-repaired: $plan"
done
```

**Success Criteria:**
- ✅ 100% of active plans have visual progress tracking
- ✅ 100% of active plans reference response templates
- ✅ 100% of active plans have Final REFACTOR phase
- ✅ 100% of active plans have copilot_instructions or equivalent

---

## Phase 8: Report Organization 🗂️

```bash
# Phase 8: Reports in cortex-brain/health-reports/
ls -lah cortex-brain/health-reports/
```

---

## Phase 9: Intent Router Validation ⚠️ CRITICAL

### 9a. Manifest Path Verification

**Source of Truth:** `cortex-brain/manifests/orchestrators/`

Scan all orchestrator manifests and verify CORTEX.prompt.md references them correctly:

| Manifest File | Orchestrator | Must Have Triggers |
|---------------|--------------|-------------------|
| `planning-system-4.0-manifest.yaml` | Planning System | `plan [x]`, `create a plan`, `make a plan` |
| `tdd-orchestrator-v4-manifest.yaml` | TDD Mastery | `start tdd`, `run tests`, `tdd [x]` |
| `ado-planning-manifest.yaml` | ADO Operations | `plan ado`, `ado story`, `ado feature` |
| `code-sanitization-manifest.yaml` | Sanitization | `sanitize`, `make generic`, `anonymize` |
| `refinement-orchestrator-manifest.yaml` | Refinement | `refine`, `improve cortex` |

### 9b. Duplicate Template Definition Detection 🚨 NEW

**Problem:** Custom templates can be defined in MULTIPLE locations with DIFFERENT detection systems, causing routing failures.

**Duplicate Detection Scan:**

```bash
# Scan for business_value template definitions
grep -r "business_value" \
  cortex-brain/response-templates-v4.yaml \
  cortex-brain/response-templates/*.yaml \
  cortex-brain/response-templates/operations/**/*.yaml

# Scan for introduction template definitions  
grep -r "introduction" \
  cortex-brain/response-templates-v4.yaml \
  cortex-brain/response-templates/*.yaml
```

**Critical Files to Check:**

1. **Primary:** `cortex-brain/response-templates-v4.yaml` (custom_templates section)
2. **Legacy:** `cortex-brain/response-templates/operations/general/general.yaml`
3. **Routing:** `cortex-brain/response-templates/response-routing-rules.yaml`

**Validation Rules:**

| Template | Source of Truth | Forbidden Duplicates |
|----------|----------------|----------------------|
| `business_value` | `response-templates-v4.yaml` (custom_templates) | ❌ `operations/general/general.yaml` |
| `introduction_professional` | `response-templates-v4.yaml` (custom_templates) | ❌ `operations/general/general.yaml` |
| `introduction_leadership` | `response-templates-v4.yaml` (custom_templates) | ❌ Any other location |
| `introduction_product` | `response-templates-v4.yaml` (custom_templates) | ❌ Any other location |
| `introduction_engineering` | `response-templates-v4.yaml` (custom_templates) | ❌ Any other location |

**Auto-Fix Strategy:**

```python
# Pseudo-code for duplicate removal
def fix_duplicate_templates():
    # Step 1: Load v4.0 custom_templates as source of truth
    v4_templates = load_yaml("response-templates-v4.yaml")["custom_templates"]
    
    # Step 2: Scan legacy locations
    legacy_file = "response-templates/operations/general/general.yaml"
    legacy_templates = load_yaml(legacy_file)
    
    # Step 3: Detect duplicates
    duplicates = []
    for template_id in v4_templates.keys():
        if template_id in legacy_templates:
            duplicates.append({
                "template_id": template_id,
                "source_of_truth": "response-templates-v4.yaml",
                "duplicate_location": legacy_file
            })
    
    # Step 4: Auto-remove duplicates from legacy files
    for dup in duplicates:
        remove_from_legacy(dup["template_id"], dup["duplicate_location"])
        log(f"✅ Removed duplicate: {dup['template_id']} from {dup['duplicate_location']}")
    
    # Step 5: Verify routing rules point to v4.0
    routing_rules = load_yaml("response-templates/response-routing-rules.yaml")
    for intent in routing_rules["intent_detection"]["priority_1_exact_match"]:
        if intent["template"] in v4_templates.keys():
            # Ensure template field matches v4.0 definition
            validate_routing(intent, v4_templates)
    
    return len(duplicates)
```

**Detection Output:**

```markdown
### 🔍 Duplicate Template Scan Results

| Template ID | v4.0 Definition | Duplicate Found | Action |
|-------------|-----------------|-----------------|--------|
| business_value | ✅ Yes (lines 603-890) | ⚠️ Yes (general.yaml:1254) | 🔧 AUTO-FIX: Remove from general.yaml |
| introduction_professional | ✅ Yes (lines 520-602) | ❌ None | ✅ OK |
| introduction_leadership | ✅ Yes (lines 520-602) | ❌ None | ✅ OK |

**Status:** 1 duplicate found and auto-fixed
**Health Impact:** Template routing restored to 100%
```

**Python Detection Script:**

```python
# Add to src/maintenance/template_duplicate_detector.py
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def detect_duplicate_templates() -> List[Dict]:
    """
    Detect custom templates defined in multiple locations.
    
    Returns:
        List of duplicate definitions with locations
    """
    duplicates = []
    
    # Source of truth
    v4_path = Path("cortex-brain/response-templates-v4.yaml")
    v4_data = yaml.safe_load(v4_path.read_text())
    v4_custom = v4_data.get("custom_templates", {})
    
    # Legacy locations to scan
    legacy_paths = [
        Path("cortex-brain/response-templates/operations/general/general.yaml"),
        Path("cortex-brain/response-templates/template-base.yaml"),
    ]
    
    for template_id in v4_custom.keys():
        for legacy_path in legacy_paths:
            if not legacy_path.exists():
                continue
            
            legacy_content = legacy_path.read_text()
            if template_id in legacy_content:
                duplicates.append({
                    "template_id": template_id,
                    "source_of_truth": str(v4_path),
                    "duplicate_location": str(legacy_path),
                    "severity": "HIGH"  # Causes routing failures
                })
    
    return duplicates

def auto_fix_duplicates(duplicates: List[Dict]) -> int:
    """Remove duplicate template definitions from legacy files."""
    fixed_count = 0
    
    for dup in duplicates:
        legacy_path = Path(dup["duplicate_location"])
        legacy_data = yaml.safe_load(legacy_path.read_text())
        
        # Remove the duplicate key
        if dup["template_id"] in legacy_data:
            del legacy_data[dup["template_id"]]
            
            # Write back
            legacy_path.write_text(yaml.dump(legacy_data, sort_keys=False))
            fixed_count += 1
            print(f"✅ Removed {dup['template_id']} from {legacy_path.name}")
    
    return fixed_count
```

### 9c. Custom Template Routing Integration 🆕

**Problem:** `TemplateManager` (src/templates/) doesn't detect custom templates from v4.0 YAML.

**Detection Check:**

```bash
# Verify TemplateManager loads custom_templates section
grep -n "custom_templates" src/templates/template_manager.py

# Expected: Should parse custom_templates from YAML and register intent patterns
# Actual: ❌ NO custom_templates parsing found
```

**Auto-Fix: Add Custom Template Detection to TemplateManager**

```python
# Add to src/templates/template_manager.py

class TemplateManager:
    def __init__(self, config_path: Optional[Path] = None):
        # ... existing code ...
        
        # NEW: Load custom templates
        self.custom_templates = self.config.get("custom_templates", {})
        self._register_custom_templates()
    
    def _register_custom_templates(self) -> None:
        """Register custom templates with intent pattern matching."""
        for template_id, template_config in self.custom_templates.items():
            intent_patterns = template_config.get("intent_patterns", [])
            
            # Register each pattern for quick lookup
            for pattern in intent_patterns:
                self._intent_to_template_map[pattern.lower()] = template_id
            
            self.logger.info(
                f"Registered custom template: {template_id} "
                f"({len(intent_patterns)} patterns)"
            )
    
    def detect_custom_template(self, user_request: str) -> Optional[str]:
        """
        Detect if user request matches a custom template.
        
        Args:
            user_request: User's request text
        
        Returns:
            Template ID if matched, None otherwise
        """
        request_lower = user_request.lower()
        
        # Check each registered pattern
        for pattern, template_id in self._intent_to_template_map.items():
            if pattern in request_lower:
                self.logger.info(f"Custom template detected: {template_id}")
                return template_id
        
        return None
    
    def render_custom_template(self, template_id: str) -> str:
        """
        Render a custom template by ID.
        
        Args:
            template_id: ID of custom template
        
        Returns:
            Rendered markdown content
        """
        if template_id not in self.custom_templates:
            raise ValueError(f"Unknown custom template: {template_id}")
        
        template_config = self.custom_templates[template_id]
        format_str = template_config.get("format", "")
        
        # Return the pre-formatted content directly
        # Custom templates are complete, static responses
        return format_str
```

**Integration with generate_response():**

```python
def generate_response(
    self,
    context: TemplateContext,
    content: Dict[str, str]
) -> str:
    """Generate response (modified to check custom templates first)."""
    
    # NEW: Check for custom template match FIRST
    custom_template_id = self.detect_custom_template(context.request)
    if custom_template_id:
        return self.render_custom_template(custom_template_id)
    
    # Existing tier-based logic...
    tier = self.tier_selector.select_tier(context)
    # ... rest of existing code
```

### 9d. Output Structure Validation

Planning System MUST specify folder structure from manifest:
```yaml
output_location: cortex-brain/documents/planning/active/{PLAN_NAME}/
required_subfolders: [context/, reports/, artifacts/, tracking/]
required_files: [00-master-plan.md]
```

### 9e. Validation Commands

```bash
# Check for broken/old paths
grep -r "orchestrator-manifests" .github/prompts/  # Should return NOTHING

# Verify all manifest references exist
for f in $(grep -oh "cortex-brain/manifests/orchestrators/[^\"']*" .github/prompts/*.md); do
  [ -f "$f" ] || echo "MISSING: $f"
done

# NEW: Detect duplicate template definitions
python -c "
import yaml
from pathlib import Path

v4 = yaml.safe_load(Path('cortex-brain/response-templates-v4.yaml').read_text())
custom = list(v4.get('custom_templates', {}).keys())

# Scan legacy files
legacy = Path('cortex-brain/response-templates/operations/general/general.yaml')
if legacy.exists():
    content = legacy.read_text()
    for template_id in custom:
        if template_id in content:
            print(f'DUPLICATE: {template_id} in {legacy}')
"

# Verify TemplateManager loads custom templates
grep -n "custom_templates" src/templates/template_manager.py || \
  echo "⚠️ WARNING: TemplateManager missing custom_templates support"
```

**Phase 9 Success Criteria:**

- [ ] All manifest paths in CORTEX.prompt.md are valid
- [ ] Zero duplicate custom template definitions detected
- [ ] TemplateManager has `detect_custom_template()` method
- [ ] TemplateManager has `render_custom_template()` method  
- [ ] Custom templates take priority over tier-based routing
- [ ] All custom template intent_patterns are registered

---

## Phase 10: Regenerate Lean Prompts (WITH COMPLETE INTENT ROUTER WIRING)

**Goal:** Create minimal, clean prompt files with proper intent routing for ALL orchestrators.

**Reference:** `cortex-brain/documents/analysis/orchestrator-inventory-2025-12-29.md`

### 10a. Pre-Regeneration: Orchestrator Discovery

**BEFORE regenerating prompts, scan ALL orchestrator manifests:**

```bash
# List all orchestrator manifests
find cortex-brain/manifests/orchestrators/ -name "*-manifest.yaml" -o -name "*-orchestrator*.yaml"

# Extract orchestrator names and capabilities
grep -h "orchestrator_name:" cortex-brain/manifests/orchestrators/*.yaml
```

**Required Orchestrators for Intent Router (Minimum 8):**

1. **Planning System** - `planning-system-4.0-manifest.yaml`
2. **TDD Mastery** - `tdd-orchestrator-v4-manifest.yaml`
3. **Debug Orchestrator** - `debug-orchestrator-manifest.yaml`
4. **CORTEX Lens** - `cortex-lens-v3-manifest.yaml`
5. **ADO Planning** - `ado-planning-manifest.yaml`
6. **Code Sanitization** - `code-sanitization-manifest.yaml`
7. **Refinement** - `refinement-orchestrator-manifest.yaml`
8. **System Maintenance** - `cortex-maintenance.prompt.md`

**Optional but Recommended:**
- Onboarding (via `onboarding_interactive.py`)
- Technical Documentation (`technical-documentation-orchestrator-manifest.yaml`)

### 10b. CORTEX.prompt.md COMPLETE Structure (Target: <200 lines)

**Template with ALL orchestrators wired:**

```markdown
# 🎯 CORTEX Universal Entry Point

**Version:** 4.0.1 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Website:** https://asifhussain60.github.io/CORTEX/  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## ⚠️ Parse User Request FIRST

Remove meta-directives before intent classification:
- `Follow instructions in...` → REMOVE
- `Use *.prompt.md...` → REMOVE  
- `Reference file:///...` → REMOVE

---

## 🚨 PLANNING DETECTION (HIGHEST PRIORITY)

**⛔ STOP! Check this FIRST before ANY work:**

### Planning Command Patterns (MUST create plan, NOT implement):
- `/CORTEX Plan [feature]`
- `/CORTEX plan [feature]`
- `create a plan for [feature]`
- `make a plan for [feature]`
- `plan: [feature]`
- `planning [feature]`

### Implementation Patterns (Execute without planning):
- `implement [feature]`
- `build [feature]`
- `create [feature]` (without "plan")
- `add [feature]`
- `fix [issue]`

### ⛔ MANDATORY RULE:
**If ANY planning pattern detected → STOP → Create plan structure → DO NOT IMPLEMENT**

### Example Detection:
```
User: "/CORTEX Plan user authentication"
✅ CORRECT: Create planning/active/user-authentication/ + 4 subfolders → STOP
❌ WRONG: Start implementing auth code

User: "implement user authentication"  
✅ CORRECT: Begin implementation directly
❌ WRONG: Create a plan first
```

---

## 🔀 Intent Router

| Command | Orchestrator | Manifest | Output |
|---------|--------------|----------|--------|
| `/CORTEX Plan [x]`, `create a plan`, `make a plan`, `plan: [x]` | **Planning System** | `planning-system-4.0-manifest.yaml` | `planning/active/{NAME}/` + 4 subfolders **→ STOPS HERE** |
| `start tdd`, `run tests`, `tdd [x]` | TDD Mastery | `tdd-orchestrator-v4-manifest.yaml` | Tests in `tests/` |
| `debug [issue]`, `fix bug`, `troubleshoot` | Debug Orchestrator | `debug-orchestrator-manifest.yaml` | Bug report + fix |
| `open lens`, `show dashboard`, `analytics` | CORTEX Lens | `cortex-lens-v3-manifest.yaml` | Dashboard visualization |
| `onboard`, `getting started`, `learn cortex` | Onboarding | Via `onboarding_interactive.py` | Interactive 6-phase guide |
| `plan ado`, `ado story`, `ado feature` | ADO Operations | `ado-planning-manifest.yaml` | ADO work items |
| `sanitize`, `make generic`, `anonymize` | Sanitization | `code-sanitization-manifest.yaml` | Sanitized codebase |
| `refine`, `improve cortex`, `optimize code` | Refinement | `refinement-orchestrator-manifest.yaml` | 7-phase improvement |
| `system maintenance`, `health check` | Maintenance | Via `cortex-maintenance.prompt.md` | Health reports |
| `help`, `show commands` | Help | Template-based | Command list |

**Manifest Path:** `cortex-brain/manifests/orchestrators/{manifest-file}`

### ⚠️ Planning vs. Implementation

**Planning Commands = Create folder structure ONLY (NO CODE):**
- `/CORTEX Plan user-auth` → Creates `planning/active/user-auth/` + subfolders → **STOPS**
- `create a plan for API` → Creates `planning/active/api/` + subfolders → **STOPS**

**Implementation Commands = Execute code directly:**
- `implement user-auth` → Writes code immediately (no plan creation)
- `build API endpoint` → Creates files immediately (no plan creation)

### Planning System Output Structure

All plans MUST create:
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md    # Main plan
├── context/             # Context artifacts
├── reports/             # Progress reports
├── artifacts/           # Supporting files
└── tracking/            # progress-tracker.json
```

---

## 📋 Response Format (v4.0)

**Header (ALWAYS):**
```markdown
## 🧠 CORTEX {Title}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
```

**Body (Adaptive):**

| Tier | Tokens | Structure |
|------|--------|-----------|
| INSTANT | <50 | `{answer}` |
| FOCUSED | 50-200 | `{explanation}` + `**Next:**` |
| STRUCTURED | 200-600 | `**Context:**` + `**Changes:**` + `**Next:**` |
| COMPREHENSIVE | 600+ | Multiple `### {Sections}` |

**Next Steps:** EXACTLY ONE action OR `✅ All work complete!`

**Completion (when ALL work done):**
```markdown
# 🎉 CONGRATULATIONS
## 🧠 CORTEX {Operation}
...
✅ **All work complete!** No further action required.
```

---

## 🛡️ Brain Protection (SKULL)

| Rule | Enforcement |
|------|-------------|
| **TDD_ENFORCEMENT** | RED→GREEN→REFACTOR mandatory |
| **HOLISTIC_DISCOVERY** | Search before create (prevent duplication) |
| **REFACTOR_CLEANUP** | Remove orphaned/duplicate code |
| **GIT_ISOLATION** | CORTEX code never in user repos |
| **PLANNING_ISOLATION** | Planning commands create plans ONLY, never implement |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{category}/`

Categories: `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

```
cortex-brain/                    src/
├── tier0/ (Governance)          ├── tier0-3/ (Brain tiers)
├── tier1/ (Working memory)      ├── cortex_agents/ (2 agents)
├── tier2/ (Knowledge graph)     ├── orchestrators/ (8 workflows)
├── tier3/ (Dev context)         └── response_templates/
└── manifests/orchestrators/
```

---

## 📋 Quick Reference

| Command | Description |
|---------|-------------|
| `/CORTEX Plan [feature]` | Create planning folder (NO implementation) |
| `start tdd` | RED→GREEN→REFACTOR workflow |
| `debug [issue]` | Investigate and fix bug |
| `open lens` | Show analytics dashboard |
| `system maintenance` | 6-phase health pipeline |
| `sanitize [dir]` | Remove company data |
| `refine` | 7-phase system improvement |
| `help` | Show all commands |

---

## 📚 Resources

- **Learning:** `cortex-brain/documents/learning-paths/`
- **Templates:** `cortex-brain/response-templates-v4.yaml`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Maintenance:** `.github/prompts/cortex-maintenance.prompt.md`

---

**Quick Start:** Say `help` to see all operations.

**Anti-Bloat:** This file MUST stay under 200 lines.
```

### 10c. copilot-instructions.md COMPLETE Structure (Target: <150 lines)

**Template with ALL operations referenced:**

```markdown
# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant with long-term memory, context awareness, and strategic planning  
**Version:** 4.0.1 | **Author:** Asif Hussain

---

## 🎯 Entry Point

**Primary:** Load `.github/prompts/CORTEX.prompt.md` for all intent routing.

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 🔀 Intent Routing

All command routing is defined in `CORTEX.prompt.md`. Key orchestrators:

| Intent Pattern | Route To |
|----------------|----------|
| `plan`, `create a plan`, `make a plan` | Planning System → folder with 4 subfolders **→ NO IMPLEMENTATION** |
| `tdd`, `start tdd`, `run tests` | TDD Orchestrator → RED→GREEN→REFACTOR |
| `debug`, `fix bug`, `troubleshoot` | Debug Orchestrator → investigation + fix |
| `lens`, `dashboard`, `analytics` | CORTEX Lens → visualization |
| `ado`, `ado story`, `ado feature` | ADO Operations → work items |
| `sanitize`, `make generic` | Sanitization → 5-phase cleanup |
| `maintenance`, `health check` | Maintenance → 6-phase pipeline |
| `refine`, `improve` | Refinement → 7-phase improvement |

**Manifest Location:** `cortex-brain/manifests/orchestrators/`

---

## 📋 Response Format

Defer to `CORTEX.prompt.md` for full spec. Summary:

- **Header:** Always include `## 🧠 CORTEX {Title}` + author line
- **Body:** Scales with complexity (INSTANT → COMPREHENSIVE)
- **Next Steps:** EXACTLY ONE action OR completion message
- **Completion:** Use `# 🎉 CONGRATULATIONS` when all work done

---

## 🛡️ Brain Protection (SKULL)

| Rule | Action |
|------|--------|
| TDD_ENFORCEMENT | Tests must fail before implementation |
| HOLISTIC_DISCOVERY | Search before create (prevent duplication) |
| GIT_ISOLATION | CORTEX code never commits to user repos |
| PLANNING_ISOLATION | Planning commands create plans ONLY, never implement |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs  
**✅ REQUIRED:** `cortex-brain/documents/{category}/`

Categories: `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

```
cortex-brain/           # Long-term memory (4-tier brain)
├── tier0/ (Governance) 
├── tier1/ (Working memory)
├── tier2/ (Knowledge graph)
├── tier3/ (Dev context)
└── manifests/orchestrators/

src/                    # Implementation
├── cortex_agents/      # 2 specialist agents
├── orchestrators/      # 8 workflow orchestrators
└── response_templates/ # Template rendering
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Intent router (source of truth) |
| `.github/prompts/cortex-maintenance.prompt.md` | 6-phase maintenance |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules |
| `cortex-brain/response-templates-v4.yaml` | Response templates |
| `cortex-brain/manifests/orchestrators/` | All orchestrator manifests |

---

## 🚀 Quick Start

Say `help` in Copilot Chat to see all operations.

**For maintenance:** Use `system maintenance` to run 6-phase health pipeline.

---

**Anti-Bloat:** This file MUST stay under 150 lines. All details defer to CORTEX.prompt.md.
```

### 10d. Wiring Rules

1. **Single Source of Truth:** `CORTEX.prompt.md` is the intent router
2. **copilot-instructions.md:** Points TO CORTEX.prompt.md, doesn't duplicate
3. **ALL Manifests:** Every orchestrator in `cortex-brain/manifests/orchestrators/` MUST be in Intent Router
4. **Minimum 3 Triggers:** Each orchestrator needs ≥3 command patterns
5. **Output Specs:** All operations include clear output specification
6. **Planning Isolation:** Planning commands include "→ STOPS HERE" or "→ NO IMPLEMENTATION"
7. **SKULL Integration:** PLANNING_ISOLATION rule referenced in both files
8. **Knowledge Library:** All orchestrators reference `cortex-brain/knowledge/` for guidelines

### 10e. Auto-Repair Actions

When regenerating prompts, AUTOMATICALLY:

1. **Scan** `cortex-brain/manifests/orchestrators/` for all `.yaml` files
2. **Extract** orchestrator names and capabilities
3. **Populate** Intent Router table with ALL orchestrators (minimum 8)
4. **Add** 3+ trigger patterns per orchestrator
5. **Specify** output location/format for each orchestrator
6. **Verify** all manifest paths resolve to existing files
7. **Enforce** line limits: CORTEX.prompt.md <200, copilot-instructions.md <150
8. **Validate** no duplicate entries between files
9. **Ensure** PLANNING_ISOLATION rule in SKULL section
10. **Backup** existing files before overwriting

### 10f. Validation Commands

```bash
# Check all orchestrators are wired
for manifest in cortex-brain/manifests/orchestrators/*-manifest.yaml; do
  orchestrator=$(basename "$manifest" | sed 's/-manifest.yaml//')
  grep -q "$orchestrator" .github/prompts/CORTEX.prompt.md || echo "MISSING: $orchestrator"
done

# Verify no broken paths
grep -r "orchestrator-manifests" .github/prompts/  # Should return NOTHING

# Verify all manifest references exist
for f in $(grep -oh "cortex-brain/manifests/orchestrators/[^\"']*" .github/prompts/*.md); do
  [ -f "$f" ] || echo "MISSING: $f"
done

# Check line counts
wc -l .github/prompts/CORTEX.prompt.md  # Should be <200
wc -l .github/copilot-instructions.md   # Should be <150
```

---

## ✅ Success Criteria

| Check | Pass Condition |
|-------|----------------|
| Health Score | ≥ 90/100 |
| Wiring Coverage | 100% |
| **Intent Router Completeness** 🆕 | **Minimum 8 orchestrators with 3+ triggers each** |
| **Interactive Wiring** 🆕 | All 6 components for Planning & ADO orchestrators |
| Knowledge Library | All 9 categories present, README current |
| Knowledge Guidelines | 30+ files with valid metadata |
| Knowledge Integration | Orchestrators reference knowledge library |
| Manifest Paths | All resolve to existing files |
| Intent Triggers | Each orchestrator has ≥3 triggers |
| CORTEX.prompt.md | <200 lines, **ALL orchestrators wired** |
| copilot-instructions.md | <150 lines, defers to CORTEX.prompt.md |
| Output Structures | Planning System has folder spec |
| **PLANNING_ISOLATION** 🆕 | **Rule enforced in both prompt files** |
| **Interactive Planning** 🆕 | Session workflow tests 100% passing |
| **Vision Auto-Engagement** 🆕 | Image detection and analysis wired |
| **Test Suite Health** 🆕 | **100% pass rate (ZERO failures, ZERO errors, ZERO obsolete tests)** |

---

## 📋 Validation Checklist

Run during every maintenance cycle:

### Core System
- [ ] Health score ≥90
- [ ] All manifest paths resolve to existing files
- [ ] No references to deprecated `orchestrator-manifests/` path
- [ ] Each orchestrator has ≥3 trigger phrases
- [ ] Planning System has output folder structure specified
- [ ] CORTEX.prompt.md is <200 lines
- [ ] copilot-instructions.md is <150 lines
- [ ] copilot-instructions.md defers to CORTEX.prompt.md (no duplication)
- [ ] Reports folder cleaned (see Phase 8)

### Data Preservation (Phase 3) 🆕
- [ ] `cortex-brain/lessons-learned.yaml` exists and not empty
- [ ] `cortex-brain/knowledge-graph.yaml` exists and not empty
- [ ] `cortex-brain/tier1/*.db` files preserved (no deletion)
- [ ] `cortex-brain/tier2/*.db` files preserved (no deletion)
- [ ] `cortex-brain/tier3/*.db` files preserved (no deletion)
- [ ] `cortex-brain/user-dictionary.yaml` exists and not empty
- [ ] User documents in `cortex-brain/documents/` preserved
- [ ] `copilot_instructions` in active plan files intact
- [ ] `named_templates` in `response-templates-v4.yaml` intact
- [ ] Zero accidental deletions of critical data paths

### Intent Router Completeness 🆕
- [ ] Planning System orchestrator in Intent Router
- [ ] TDD Mastery orchestrator in Intent Router
- [ ] Debug Orchestrator in Intent Router
- [ ] CORTEX Lens orchestrator in Intent Router
- [ ] ADO Planning orchestrator in Intent Router
- [ ] Code Sanitization orchestrator in Intent Router
- [ ] Refinement orchestrator in Intent Router
- [ ] System Maintenance orchestrator in Intent Router
- [ ] Onboarding/Help orchestrator in Intent Router
- [ ] Minimum 8 orchestrators total in Intent Router
- [ ] All orchestrators have 3+ trigger patterns
- [ ] All orchestrators have output specifications
- [ ] Planning commands include "→ STOPS HERE" or "→ NO IMPLEMENTATION" indicator
- [ ] PLANNING_ISOLATION rule in SKULL section of CORTEX.prompt.md
- [ ] PLANNING_ISOLATION rule in SKULL section of copilot-instructions.md
- [ ] copilot-instructions.md mirrors ALL primary operations from CORTEX.prompt.md
- [ ] No orchestrator manifests exist without Intent Router entry

### Interactive Wiring 🆕
- [ ] Decision logic exists in Planning & ADO orchestrators
- [ ] Decision logic is CALLED in execute() method
- [ ] Interactive agents registered in agent_registry.py
- [ ] Execution flow has conditional routing (interactive vs autonomous)
- [ ] Interactive execution method implemented and functional
- [ ] UI bridge exists (user_interface.py) for question/answer handling
- [ ] Integration tests cover end-to-end interactive workflow
- [ ] Wiring validation script passes: `./scripts/validate_interactive_wiring.sh`
- [ ] Interactive wiring coverage: 100% for active orchestrators
- [ ] Pre-commit hook prevents unwired interactive code

### Knowledge Library
- [ ] Knowledge library has all 9 categories present
- [ ] Knowledge library README.md is current (stats match actual files)
- [ ] All knowledge YAML files have valid metadata section
- [ ] All knowledge rules have valid severity levels (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] No duplicate rule IDs across knowledge library
- [ ] Orchestrators reference knowledge library in code/manifests
- [ ] Brain protection rules reference knowledge library

### Interactive Planning 🆕
- [ ] Interactive session module exists (`src/orchestrators/planning/interactive_session.py`)
- [ ] SessionState enum with 8 states (INITIALIZING → FINALIZED)
- [ ] PlanningSession, DiscoveryEngine, ApprovalWorkflow, CleanupPhase classes exist
- [ ] Session state transitions validated (DISCOVERY → CONTEXT_GATHERING → USER_REVIEW → APPROVED → DRAFTING → CLEANUP → FINALIZED)
- [ ] Interactive planning tests: 29/29 passing (100%)
- [ ] End-to-end workflow test passing (full lifecycle validation)
- [ ] Conversation history tracking operational
- [ ] Iterative refinement loop functional

### Vision API Auto-Engagement 🆕
- [ ] Vision orchestrator exists (`src/tier1/vision_orchestrator.py`)
- [ ] Image detector exists (`src/tier1/image_detector.py`)
- [ ] Vision context middleware exists (`src/operations/utilities/vision_context_middleware.py`)
- [ ] Config has `auto_detect_images: true`
- [ ] Config has `auto_analyze_on_detect: true`
- [ ] Config has `auto_inject_context: true`
- [ ] Image detection works for PNG, JPG, JPEG formats
- [ ] Vision API auto-engages without user prompting
- [ ] Duplicate image caching operational (24hr TTL)
- [ ] Token budget enforcement active (500 token limit)
- [ ] Context injection into planning/debugging workflows verified

### Test Suite Health 🆕
- [ ] Core tests (interactive + toolkit + wiring): **100% passing (ZERO failures)**
- [ ] Full planning test suite: **100% passing (ZERO failures)**
- [ ] Error count: **0 (MANDATORY)**
- [ ] Failure count: **0 (MANDATORY)**
- [ ] Test execution time: <30 seconds
- [ ] Obsolete tests **DELETED** (tests for removed/refactored APIs)
- [ ] Misaligned tests **REFACTORED** (tests updated to match current functionality)
- [ ] Test cleanup report generated in `cortex-brain/documents/reports/`
- [ ] Cleanup report shows Before → After with 100% achievement
- [ ] Git commit includes detailed justification for deleted tests

---

## Phase 11: Final System Verification ✅

**Purpose:** Comprehensive health check to verify ALL previous phases completed successfully and system is at 100% health.

### 11a. Run System Health Diagnostic

```bash
# Run comprehensive health scan
python3 scripts/cortex_system_doctor.py --quick

# Expected: Health score ≥95%
```

### 11b. Verify All Phase Completions

```bash
# Check Phase 1: Discovery reports exist
ls cortex-brain/discovery-reports/MASTER-ACTION-PLAN-*.md

# Check Phase 2: Zero backups
find . -name "*backup*" ! -path "./.git/*" | wc -l  # Expected: 0

# Check Phase 2b: Template validation (Rule 8)
python3 -c "
import yaml
import os
from pathlib import Path

routing_file = Path('cortex-brain/response-templates/response-routing-rules.yaml')
if routing_file.exists():
    with open(routing_file, 'r', encoding='utf-8') as f:
        routing = yaml.safe_load(f)
    mappings = routing.get('validation', {}).get('template_file_mappings', {})
    errors = [f'❌ {tid} → {fp}' for tid, fp in mappings.items() if not Path(fp).exists()]
    if errors:
        print('\n'.join(errors))
        print(f'❌ FAIL: {len(errors)} broken template references')
        exit(1)
    else:
        print(f'✅ PASS: All {len(mappings)} template references valid')
else:
    print('❌ FAIL: Routing rules missing')
    exit(1)
"

# Check Phase 3: Generators functional
test -f cortex-toolkit/core/utilities/plan_scaffold_generator.py && echo "✅"

# Check Phase 4: 100% wiring
python3 scripts/check_wiring_integrity.py  # Expected: 100%

# Check Phase 5: Tests passing
python3 -m pytest tests/orchestrators/planning/ -v  # Expected: 100% pass

# Check Phase 6: Knowledge synced
# (Verified in Phase 6)

# Check Phase 7: Reports organized
# (Verified in Phase 7)

# Check Phase 8: Router functional
# (Verified in Phase 8)

# Check Phase 9: Prompts lean
find .github/prompts/ -name "*.prompt.md" -exec wc -l {} \; | awk '$1 > 200 {print}' | wc -l  # Expected: 0

# Check Phase 10: Template integrity (Rule 8 final check)
echo "Verifying template file structure..."
test -f cortex-brain/response-templates-v4.yaml && echo "✅ Master template file exists"
test ! -f cortex-brain/response-routing-rules.yaml && echo "✅ No duplicate routing files in root"
test ! -f cortex-brain/response-profile-variants.yaml && echo "✅ No duplicate profile files in root"
```

### 11c. Generate Final Health Report

```bash
cat > cortex-brain/health-reports/maintenance-complete-$(date +%Y%m%d).md << 'EOF'
# 🎉 CORTEX Maintenance Complete

**Date:** $(date +%Y-%m-%d)
**Status:** ✅ ALL PHASES COMPLETE

## Phase Completion Status

| Phase | Status | Verification |
|-------|--------|--------------|
| Phase 1: Discovery | ✅ | Master action plan generated |
| Phase 2: Cleanup | ✅ | Zero backups remain |
| Phase 3: Scaffolding | ✅ | Generators functional |
| Phase 4: Wiring | ✅ | 100% wiring coverage |
| Phase 5: Testing | ✅ | 100% test pass rate |
| Phase 6: Knowledge | ✅ | Library synced |
| Phase 7: Organization | ✅ | Reports organized |
| Phase 8: Routing | ✅ | Intent router functional |
| Phase 9: Prompts | ✅ | All prompts <200 lines |
| Phase 10: Verification | ✅ | Health score ≥95% |

## System Health Score

**Overall:** 100%

## Next Maintenance

**Recommended:** 7 days from now ($(date -v+7d +%Y-%m-%d))

EOF

cat cortex-brain/health-reports/maintenance-complete-$(date +%Y%m%d).md
```

### 11d. Commit All Maintenance Changes

```bash
# Stage all changes
git add -A

# Commit with comprehensive message
git commit -m "chore: complete 11-phase maintenance cycle

Phase 1: Discovery - Cataloged all system issues
Phase 2: Cleanup - Deleted $(cat /tmp/backup_dirs.txt /tmp/backup_files.txt 2>/dev/null | wc -l) backup items
Phase 3: Preservation - Verified all critical data paths safe
Phase 4: Scaffolding - Verified toolkit generators
Phase 5: Wiring - Achieved 100% component wiring
Phase 6: Testing - 100% test pass rate
Phase 7: Knowledge - Synced knowledge library
Phase 8: Organization - Consolidated reports
Phase 9: Routing - Fixed intent router paths
Phase 10: Prompts - Regenerated lean prompts
Phase 11: Verification - System health 100%

Health Score: 95%+ (was X%)
Issues Resolved: $(grep "Issues Found" cortex-brain/discovery-reports/MASTER-ACTION-PLAN-*.md | awk '{sum+=$3} END {print sum}')

Next maintenance: $(date -v+7d +%Y-%m-%d)"

# Push to remote
git push origin CORTEX-4.0
```

---

**🎉 MAINTENANCE CYCLE COMPLETE!**

All 11 phases executed successfully. System at peak health.

---

**End of Maintenance Prompt**
