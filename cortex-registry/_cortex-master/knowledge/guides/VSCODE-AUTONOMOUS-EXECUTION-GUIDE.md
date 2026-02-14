# VSCode Copilot Chat: Autonomous Execution Guide
**Version:** 1.0 | **Date:** 2026-02-14 | **Scope:** 5 Pending Waves | **Duration:** 3.5 hours | **Token Budget:** 380K

---

## 🚨 PRE-EXECUTION CHECKLIST

Before starting, verify:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Virtual environment created and activated
- [ ] Setup script executed: `python .cortex/setup-mcp.py`
- [ ] VS Code reloaded: Command Palette → Developer: Reload Window
- [ ] `.vscode/settings.json` exists and **NOT tracked** by git
- [ ] On `CORTEX` branch only: `git branch`
- [ ] Git hooks active: `git config core.hooksPath` returns `.githooks`
- [ ] All tests passing: `pytest tests/ -q` → 412/412 passing

**Expected Output After Setup:**
```
✅ CORTEX ready for ARCHITECT operations
✅ MCP tools: 10 available
✅ Orchestrator: TDDOrchestrator (auto-start)
✅ Silent mode: ENABLED
```

---

## 📋 5-WAVE EXECUTION PLAN

### Wave 1: Documentation Vacuum (45 min)

**Goal:** Reduce 167 files → ≤20 files in `_cortex-master/`

**VSCode Command:**
```
/implement WAVE-1: Documentation vacuum - archive 47+ obsolete files, consolidate wave status to single tracker, achieve ≤20 files in _cortex-master root
```

**Success Criteria:**
- ✅ `ls -la cortex-registry/_cortex-master/ | wc -l` returns ≤25 (includes . and ..)
- ✅ 47+ files archived to `_archive/superseded/`
- ✅ `WAVES-EXECUTION-TRACKER.yaml` created (single source of truth)
- ✅ All tests passing (412/412)
- ✅ AC_START → AC_COMPLETE markers logged

**Governance Rules Enforced:**
- CORE-002: No markdown sprawl (root clean)
- CORE-035: Single canonical implementation (tracker)

---

### Wave 2: MCP Enforcement (60 min)

**Goal:** Implement native tool interception layer to prevent MCP bypass

**VSCode Command:**
```
/implement WAVE-2: MCP bypass prevention - implement native tool interception layer with 3-method MCP detection (tool_query, env_vars, network_port), block IMPLEMENT/FIX intents from direct file operations
```

**Success Criteria:**
- ✅ `tests/mcp/test_interception_layer.py`: 16/16 tests passing
- ✅ MCP detection working: tool_query → env_vars → localhost detection
- ✅ Pre-flight check integrated with EnforcementOrchestrator
- ✅ Coverage ≥95%
- ✅ AC_START → AC_COMPLETE markers logged

**Governance Rules Enforced:**
- CORE-049: Silent Autonomous (no bypasses)
- CORE-050: MCP Circuit Breaker (pre-flight validation)
- MCP-FIRST: All operations via cortex_* tools

---

### Wave 3: Automation Hooks (45 min)

**Goal:** Implement automated registry sync hooks

**VSCode Command:**
```
/implement WAVE-3: Automation hooks - implement StatusUpdateHook (phase completion → registry sync, 5 min SLA), RegistryValidator (prevent contradictions), RecommendationGate (LENS + registry + ROI consultation)
```

**Success Criteria:**
- ✅ `tests/automation/test_automation_hooks.py`: 20/20 tests passing
- ✅ StatusUpdateHook triggered on orchestrator completion
- ✅ Registry validator prevents state contradictions
- ✅ RecommendationGate active before suggestions
- ✅ Coverage ≥90%
- ✅ AC_START → AC_COMPLETE markers logged

**Governance Rules Enforced:**
- CORE-035: Single canonical implementation (validated)
- CORE-036: Industry standards (via LENS)

---

### Wave 4: Governance Audit (30 min)

**Goal:** Comprehensive compliance verification

**VSCode Command:**
```
/audit WAVE-4: Governance compliance check - run comprehensive audit against CORE-002,CORE-008,CORE-028,CORE-035,CORE-051,CORE-052, verify settings.json NOT tracked, verify CORTEX branch only, generate compliance report
```

**Success Criteria:**
- ✅ 0 P0 violations detected
- ✅ ≤2 P1 warnings (acceptable)
- ✅ CORE-051 verified: settings.json not tracked
- ✅ CORE-052 verified: CORTEX branch only
- ✅ File naming compliance checked (109 SCREAMING_CASE → 0)
- ✅ Compliance report generated: `governance-compliance-report-2026-02-14.yaml`
- ✅ AC_START → AC_COMPLETE markers logged

**Governance Rules Enforced:**
- All 8 key CORE rules validated

---

### Wave 5: Final Consolidation (30 min)

**Goal:** Archive session, generate production handoff

**VSCode Command:**
```
/plan WAVE-5: Final consolidation - archive all session docs to _archive/2026-02-14-session/, update master-plan.yaml status to COMPLETE, generate CORTEX-STATUS-2026-02-14.yaml (single source of truth), update README.md with new architecture status, create production deployment checklist
```

**Success Criteria:**
- ✅ All session docs archived to `_archive/2026-02-14-session/`
- ✅ `master-plan.yaml` marked COMPLETE
- ✅ `CORTEX-STATUS-2026-02-14.yaml` created (single authoritative source)
- ✅ `README.md` updated with status
- ✅ Production deployment checklist generated
- ✅ All tests passing (412/412)
- ✅ AC_START → AC_COMPLETE markers logged

**Governance Rules Enforced:**
- CORE-002: Documentation clean
- All compliance rules maintained

---

## 🎯 EXECUTION WORKFLOW

### Sequential Execution (Waves must run in order)

```
WAVE-1 (Documentation) ✅ COMPLETE
   ↓
WAVE-2 (MCP Enforcement) ← START HERE
   ↓
WAVE-3 (Automation Hooks)
   ↓
WAVE-4 (Governance Audit)
   ↓
WAVE-5 (Final Consolidation) ← END
```

### Each Wave Execution Flow

1. **Copy the VSCode Command** from wave section above
2. **Open VSCode Copilot Chat** (Cmd+I or ⌘+I on Mac)
3. **Paste the command** and press Enter
4. **MCP auto-starts** (no manual setup needed)
5. **Monitor progress** via ASCII progress bars
6. **No mid-execution prompts** (silent autonomous mode)
7. **On completion:**
   - Review AC markers: `AC_START: AC-WAVE-X-*-001 → AC_COMPLETE`
   - Check test results in completion table
   - Verify success criteria above
   - **Copy AC_COMPLETE marker** (needed for continuation if token limit hit)

### Token Budget Management

**Total Budget:** 380K tokens across 5 waves

| Wave | Budget | Actual | Status |
|------|--------|--------|--------|
| 1    | 80K    | TBD    | Ready  |
| 2    | 100K   | TBD    | Ready  |
| 3    | 90K    | TBD    | Ready  |
| 4    | 60K    | TBD    | Ready  |
| 5    | 50K    | TBD    | Ready  |

**If response truncated during wave:**
1. Copilot automatically commits progress to git
2. Copy the AC_COMPLETE marker from truncated response
3. Start new Copilot chat session
4. Paste: `/continue {wave_number} {checkpoint_marker}`
5. Execution resumes from checkpoint

---

## ⚠️ TROUBLESHOOTING

### Symptom: MCP tools not appearing

**Resolution:**
```bash
1. python .cortex/setup-mcp.py
2. Command Palette → Developer: Reload Window
3. Retry in Copilot chat: type @cortex
```

### Symptom: Tests failing during WAVE

**Important:** ❌ NEVER skip tests (CORE-008 violation)

**Resolution:**
1. Read test error completely
2. Fix root cause in source code
3. Run tests to verify: `pytest {test_file} -v`
4. In Copilot chat: `/continue {wave_number}`

### Symptom: Response truncated (token limit hit)

**Resolution:**
1. Response shows AC_COMPLETE marker: `AC_COMPLETE: AC-WAVE-X-*-001 ✅`
2. Progress committed to git automatically
3. Start new Copilot chat
4. Paste: `/continue wave_{number} AC-WAVE-X-*-001`

### Symptom: Git hooks not configured

**Resolution:**
```bash
git config core.hooksPath .githooks
# Verify:
git config core.hooksPath
# Expected output: .githooks
```

---

## 📊 MONITORING PROGRESS

### During Execution (Silent Mode)

- ✅ Progress bars (inline code blocks)
- ✅ Table updates
- ❌ NO narration
- ❌ NO mid-execution prompts
- ❌ NO step-by-step explanations

### On Completion

```markdown
## 🏛️ CORTEX Architect WAVE-X
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

<hr>

📋 **WAVE-X Stage N: [Component]**

`██████████` 100% Complete

| # | Status | Stage | Detail |
|---|--------|-------|--------|
| 1 | ✅ | Component 1 | Result |
| 2 | ✅ | Component 2 | Result |

**Tests:** 20/20 | **Coverage:** 95%
**AC Marker:** AC-WAVE-X-*-001 ✅ COMPLETE

<hr>
```

---

## 🔗 REFERENCE COMMANDS

| Scenario | Command |
|----------|---------|
| Start WAVE-1 | `/implement WAVE-1: ...` |
| Start WAVE-2+ | `/implement WAVE-2: ...` |
| Run audit (WAVE-4) | `/audit WAVE-4: ...` |
| Plan/consolidate (WAVE-5) | `/plan WAVE-5: ...` |
| Resume after interruption | `/continue wave_{N} AC-MARKER` |
| Check MCP status | Type `@cortex` in Copilot chat |
| Force reload MCP | Reload VS Code window + retry |

---

## 📝 SESSION WORKFLOW

```
Session Start
   ↓
Pre-flight check (checklist above)
   ↓
WAVE-1: Copy command → Paste → Execute
   ↓ (after WAVE-1 complete)
WAVE-2: Copy command → Paste → Execute
   ↓ (after WAVE-2 complete)
WAVE-3: Copy command → Paste → Execute
   ↓ (after WAVE-3 complete)
WAVE-4: Copy command → Paste → Execute
   ↓ (after WAVE-4 complete)
WAVE-5: Copy command → Paste → Execute
   ↓
Session Complete ✅
All governance rules verified
Production-ready status achieved
```

---

## ✅ SUCCESS CRITERIA (ALL WAVES)

**Global Success Metrics:**

- ✅ 412/412 tests passing (no skipped tests)
- ✅ Coverage ≥80% maintained
- ✅ 0 P0 governance violations
- ✅ ≤2 P1 warnings (acceptable)
- ✅ All CORE rules verified: CORE-002, 008, 028, 035, 051, 052
- ✅ MCP-FIRST enforcement active
- ✅ AC markers logged for audit trail
- ✅ All commits pushed to remote CORTEX branch
- ✅ `_cortex-master/` ≤20 files
- ✅ Single source of truth: `CORTEX-STATUS-2026-02-14.yaml`

**Final Status:** 🟢 PRODUCTION READY

---

*Autonomous execution guide for CORTEX Phase 2 Consolidation. 5 waves, ~3.5 hours, silent mode throughout.*
