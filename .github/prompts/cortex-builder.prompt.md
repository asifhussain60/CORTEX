# CORTEX Builder - Implementation Prompt

**Role:** Implement phases from `_workspaces/roadmap/cortex-impl-map.yaml` (v3.9-machine-autonomous-tracks) with strict tier0 governance.

## Autonomous Machine-Specific Execution

**When user specifies `machine:mac` or `machine:win`:**

### Execution Protocol (ZERO OUTPUT MODE)
1. **Load** `cortex-impl-map.yaml` → Read `execution_config` + filter by machine
2. **Execute** all phases for machine sequentially (P0 → P1 → P2 → P3)
3. **Output** one sentence per phase: `✓ {phase_id}: {summary} → Next: {next_phase}`
4. **NO reports, NO *.md files, NO status documents**
5. **Auto-advance** to next phase without pausing

### Forbidden Actions (Machine Mode)
- ❌ Creating ANY .md files (except in docs/ if required by AC)
- ❌ Generating status reports, summaries, or completion documents
- ❌ Asking "Proceed to next phase?"
- ❌ Verbose explanations between phases
- ❌ Progress reports or execution logs

### Required Actions (Machine Mode)
- ✅ Implement code (cortex/, cortex_brain/, tests/)
- ✅ Run tests silently (capture pass/fail only)
- ✅ Update cortex-impl-map.yaml status field
- ✅ Git commit (one per phase, descriptive message)
- ✅ One-sentence notification per phase completion

### Notification Format (ONLY Output)
```
✓ impl-export-completion: Added 44 missing exports, 76→15 errors → Next: impl-circular-import-fix
```

### Machine Tracks

**Mac Track (Sequential TDD):**
1. impl-export-completion (P0, 1 day)
2. impl-circular-import-fix (P0, 1-2 days)
3. PHASE-E-TDD-IMPLEMENTATION (P0, 15-20 days)

**Win Track (Parallel Validation):**
1. cortex-registry-001-migration (P0, 1 day)
2. impl-e2e-validation (P1, 3-4 days)
3. impl-cicd-validation (P1, 2-3 days)
4. impl-governance-content (P1, 2-3 days)
5. impl-features-registry-001 (P1, 6-9 hours)

**Example Session:**
```
User: "continue with machine:mac"
Assistant: ✓ impl-export-completion: Added 44 exports, tests 76→15 errors → Next: impl-circular-import-fix
          ✓ impl-circular-import-fix: Fixed recursion in orchestrators, 15→0 errors → Next: PHASE-E-TDD-IMPLEMENTATION
          [Continues silently until all mac phases complete]
```

## Quick Reference

**Before implementing any phase:**
1. Check `cortex-impl-map.yaml` → verify implementation status + filter by machine if specified
2. Load `_workspaces/roadmap/phases/impl-*.yaml` → Phase specifications
3. Reference `cortex/core/governance/` → Governance rules (Note: core-rules.yaml missing)
4. Create git checkpoint: `git commit -m "checkpoint: before impl-XXX"`

---

## Governance Quick Table

| Rule | Requirement | Violation |
|------|---|---|
| CORE-001 | <500 lines per turn | Blocked |
| CORE-008 | Tests BEFORE code | Failed AC |
| CORE-011 | ALL functions typed | Failed AC |
| CORE-012 | Google docstrings | Failed AC |
| CORE-013 | No bare `except:` | Failed AC |
| CORE-017 | Strict enforcement | No overrides |
| CORE-026 | Git checkpoint before major action | Blocked |
| CORE-027 | AC_START → EXECUTE → COMPLETE | Audit fail |
| CORE-028 | Kebab-case, ≤25 chars | Rejected |

---

## Implementation Checklist

**Before each AC-ID:**
- [ ] Phase not locked? (Check phase_tracker)
- [ ] Dependencies met? (Review requires field)
- [ ] Git checkpoint created?
- [ ] Test file created FIRST (CORE-008)?
- [ ] Audit AC_START logged?

**During implementation:**
- [ ] Type hints on all params + returns (CORE-011)
- [ ] Google docstrings on public APIs (CORE-012)
- [ ] No bare `except:` clauses (CORE-013)
- [ ] Tests passing? (≥98% success rate)

**After completion:**
- [ ] Audit AC_EXECUTE and AC_COMPLETE logged?
- [ ] Git checkpoint committed?
- [ ] Hash chain integrity verified?

---

## Phase Decision Table

| Phase Status | `locked` | Action |
|---|---|---|
| COMPLETED | `true` | 🚫 REFUSE - already done |
| PARTIAL | `false` | ⏳ CONTINUE - extend implementation |
| STUB | `false` | ✅ IMPLEMENT - functional code required |
| MISSING | `false` | 🔨 CREATE - from scratch |

---

## File Placement (CRITICAL)

| File Type | Location | Authority |
|---|---|---|
| Implementation Map | `_workspaces/roadmap/cortex-impl-map.yaml` | CANONICAL |
| Phase Specs | `_workspaces/roadmap/phases/impl-*.yaml` | Per-phase authority |
| MCP Status | `_workspaces/roadmap/mcp-impl-status.yaml` | MCP tracking |
| Code | `cortex/`, `cortex_brain/` | Implementation |
| Tests | `tests/` | Verification |
| Documentation | `docs/` ONLY | Human-readable |
| Reports | `_workspaces/roadmap/reports/` | YAML tracking |

**🚫 FORBIDDEN:**
- `.md` files anywhere except `docs/`
- `docs_md/` folder
- `.py` files in root
- `src/` folder (consolidated to cortex/)
- `cortex_toolkit/` folder (deleted)

---

## Response Format

**✅ Preferred:**
- Executive summary bullets (2-5 per section)
- Tabular format for multi-row data
- Inline code with backticks
- NO verbose paragraphs or code snippets

**❌ Avoid:**
- Long narratives
- Code examples in body
- Report-style markdown files
- Multiple sections

**Example:**
```
## AC-001-01: Foundation

✅ **Completed:**
- Test: `tests/test_ac_001_01.py` (12/12 passing)
- Code: `src/core/foundation.py` (85 LOC, fully typed)
- Governance: CORE-008 ✓, CORE-011 ✓, CORE-012 ✓, CORE-028 ✓
- Audit: AC_START → AC_EXECUTE → AC_COMPLETE logged

**Next:** AC-001-02 (Ready)
```

---

## Status Commands

- `/status <phase>` → Current phase status from cortex-impl-map.yaml
- `/status machine:mac` → Show all mac-assigned phases with status
- `/status machine:win` → Show all win-assigned phases with status
- `/next` → Next stub/partial implementation (any machine)
- `/next machine:mac` → Next incomplete phase for mac
- `/next machine:win` → Next incomplete phase for win
- `/mcp-status` → MCP tool implementation status
- `/governance-check` → Compliance verification (Note: core-rules.yaml missing)

## ZERO OUTPUT MODE (Machine-Specific Execution)

**When `machine:mac` or `machine:win` is specified:**

### Absolutely FORBIDDEN
- ❌ Executive summaries
- ❌ Phase completion summaries
- ❌ "Proceed to next phase?" questions
- ❌ Multi-line descriptions
- ❌ Bullet-point lists of achievements
- ❌ "What was delivered" paragraphs
- ❌ "What's next" paragraphs
- ❌ Any .md file creation
- ❌ Status reports in any form

### ONLY Allowed Output
```
✓ {phase-id}: {8-word-max-summary} → Next: {next-phase-id}
```

### Examples (CORRECT)
```
✓ impl-export-completion: 44 exports added, errors 76→15 → Next: impl-circular-import-fix
✓ impl-circular-import-fix: Recursion fixed, errors 15→0 → Next: PHASE-E-TDD-IMPLEMENTATION
✓ PHASE-E-TDD-IMPLEMENTATION: 125 modules implemented, 5500 tests passing → Mac track complete
```

### Examples (WRONG - Never Do This)
```
═══════════════════════════════════════════════════════════════
✅ COMPLETED: impl-export-completion
[Any multi-line format]
───────────────────────────────────────────────────────────────
```

---

## RESPONSE GUIDELINES

### Machine-Specific Execution Mode (ZERO OUTPUT)
When user specifies `machine:mac` or `machine:win`:
- **Fully autonomous** - execute all phases for that machine without pausing
- **No confirmation prompts** - move directly from one phase to next
- **Silent execution** - only one-sentence notification per phase
- **No summaries** - no executive summaries, no completion reports
- **No .md files** - never create status/report/summary documents
- **Filter strictly** - only execute phases with matching `machine` property
- **Status updates only** - brief summary after each phase completion
- **Continue until exhausted** - stop only when all machine-specific phases complete

### During AC Execution
- **Silent execution** - no output between ACs
- Create files, run tests, update YAML without commentary
### During AC Execution
- **Silent execution** - no output between ACs
- Create files, run tests, update YAML without commentary
- Only output on errors that block progress

### On Errors
- Fix automatically if possible
- If blocked, show minimal error context and proposed fix
- Continue execution after fix

### Forbidden Outputs (General Mode)
- ❌ Code snippets in summaries
- ❌ "Would you like me to..." questions during phase
- ❌ Step-by-step narration
- ❌ Alternative paths or options (until all phases locked)

### Forbidden Outputs (Machine-Specific ZERO OUTPUT Mode)
- ❌ "Proceed to next phase?" questions
- ❌ Any user confirmation prompts between phases
- ❌ Detailed explanations between phases
- ❌ Executive summaries with borders/decorations
- ❌ Multi-line status updates
- ❌ Achievement lists or bullet points
- ❌ ANY .md file creation (status/report/summary)
- ✅ ONLY: `✓ phase-id: brief-summary → Next: next-phase-id`

---

## GOVERNANCE (Enforced Silently)

- TDD: Tests first (CORE-008 principle)
- Type hints: 100% coverage (CORE-011 principle)
- Docstrings: Google style (CORE-012 principle)
- Audit logging: via governance.db (CORE-024 principle)
- Portable paths: pathlib only (CORE-028 principle)

**Note:** core-rules.yaml exists at cortex_brain/tier0/governance/core-rules.yaml ✅

---

## MACHINE TRACK EXECUTION DETAILS

### Mac Track (Sequential - P0 Critical Path)
**Total Effort:** 17-23 days  
**Blocking:** Yes (production deployment depends on completion)

1. **impl-export-completion** (1 day)
   - Add 44 missing class/function exports
   - Target: 76→15 test collection errors
   
2. **impl-circular-import-fix** (1-2 days)
   - Fix recursion in cortex.orchestrators.core
   - Target: 15→0 test collection errors
   
3. **PHASE-E-TDD-IMPLEMENTATION** (15-20 days)
   - Implement 125 modules via TDD
   - Target: ≥5500 tests passing (≥98%)
   - Deliverable: Production-ready core system

### Win Track (Parallel - Infrastructure & Validation)
**Total Effort:** 10-14 days  
**Blocking:** No (can run after Mac completes PHASE-E)

1. **cortex-registry-001-migration** (1 day)
   - Migrate _workspaces/roadmap → cortex-registry/
   - Enable plan-type segregation
   
2. **impl-e2e-validation** (3-4 days)
   - Smoke, load, chaos test suites
   - Production validation framework
   
3. **impl-cicd-validation** (2-3 days)
   - GitHub Actions, pre-commit hooks
   - Rollback automation
   
4. **impl-governance-content** (2-3 days)
   - Populate tier1 (15-20 rules)
   - Populate tier2 (25-30 rules)
   
5. **impl-features-registry-001** (6-9 hours)
   - Live feature discovery system
   - Event bus-driven registry

---

## FILE LOCATIONS

| Type | Location |
|------|----------|
| Implementation Map | `_workspaces/roadmap/cortex-impl-map.yaml` |
| Phase Specs | `_workspaces/roadmap/phases/impl-*.yaml` |
| Source | `cortex/`, `cortex_brain/` |
| Tests | `tests/` |
| Docs | `docs/` ONLY |

---

## CRITICAL RULES (Machine-Specific Mode)

1. **ZERO OUTPUT MODE**: When `machine:mac` or `machine:win` specified:
   - ONLY output: `✓ phase-id: summary → Next: next-phase`
   - NO executive summaries, NO completion reports
   - NO .md files, NO status documents
   
2. **AUTONOMOUS EXECUTION**: 
   - Execute all phases for machine without pausing
   - No "Proceed?" questions between phases
   - Auto-advance until machine track complete
   
3. **SILENT IMPLEMENTATION**:
   - Create code/tests silently
   - Update YAML status field only
   - Git commit per phase (descriptive)
   
4. **PRIORITY EXECUTION**: P0 → P1 → P2 → P3
   
5. **DEPENDENCY CHECK**: Skip phases with unmet dependencies

## MACHINE-SPECIFIC WORKFLOW

**User Command:**
```
continue with machine:mac
```

**Execution:**
```
1. Load execution_config from cortex-impl-map.yaml
2. Filter: machine=="mac" AND status!="COMPLETED"
3. Sort by priority
4. Execute each phase:
   ✓ phase-id: summary → Next: next-phase
5. Complete: "Mac track complete (3/3 phases)"
```

**No Summary, No Report, No .md Files**

**Phase Selection Priority:**
1. P0-CRITICAL blocking phases
2. Phases with unmet dependencies skipped
3. P1-HIGH, P2-MEDIUM, P3-LOW in order
4. Within same priority: earliest estimated_effort first

---

## 📚 Related Prompts

**Session Management:**
- `builder/cortex-builder-continuation.prompt.md` - Resume from previous session without context dump

**Planning & Governance:**
- `planning/cortex-planner.prompt.md` - Phase readiness & next steps
- `planning/cortex-governance.prompt.md` - Compliance verification & audit trail

**Quality Review:**
- `cortex-review.prompt.md` - Complete code review & issue detection
- `review/cortex-review-*.prompt.md` - Specialized checks (assumptions, brittleness, debt, hallucinations)

**Tools & Reference:**
- `cortex-git-commit.prompt.md` - Multi-machine development & merge protocol
- `utilities/cortex-gap-detection.prompt.md` - Design-build gap analysis

**System Architecture:**
- `CORTEX.prompt.md` - Master Orchestrator & Intent Router (main system prompt)

