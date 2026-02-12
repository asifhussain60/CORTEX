# CORTEX Autonomous Wave Execution Guide
**Version:** 2.0 | **Updated:** 2026-02-12T22:30:00Z | **Mode:** Session-Scoped | **Status:** ACTIVE ✅

---

## 🎯 Purpose

Complete guide for executing CORTEX waves (I-O) autonomously within single GitHub Copilot Chat sessions. Each wave is designed for end-to-end completion: setup → TDD → commit → verify.

---

## 📋 QUICK START: WAVE-I (READY NOW)

### Session Setup (5 minutes)

1. **Verify Prerequisites:**
   ```bash
   # Check Python environment
   python3 --version  # Should be 3.9+
   
   # Check test collection
   cd /Users/asifhussain/PROJECTS/CORTEX
   python3 -m pytest tests/ --collect-only -q | tail -5
   # Expected: 21700 tests collected, 1 error
   
   # Check git status
   git status
   # Expected: Clean working tree
   ```

2. **Open GitHub Copilot Chat:**
   - Open VS Code
   - Press `Cmd+Shift+I` (macOS) to open Copilot Chat
   - Ensure MCP tools available (cortex_* tools)

3. **Copy Execution Command:**
   ```
   /implement WAVE-I: ENH-084 Standard Phase Creation Practices
   
   Authority: cortex-registry/_cortex-master/index.yaml v2.2
   Mode: Silent autonomous with ASCII progress bars
   Session: WAVE-I-20260213-01
   Token Budget: <150k
   
   Scope:
   1. Phase template CLI tool (cortex/cli/phase_template_cli.py)
   2. 50+ validation rules (naming, structure, dependencies)
   3. 15+ CLI tests (TDD: RED→GREEN→REFACTOR)
   4. User guide documentation (.github/prompts/PHASE-CREATION-GUIDE.md)
   5. Integration with EnforcementOrchestrator (CORE-043)
   
   Success Criteria:
   - ✅ 15/15 tests passing (0 failures)
   - ✅ 2 commits pushed
   - ✅ CLI demo: Create phase in <2 minutes
   - ✅ Validation: Block orphan phase creation
   
   Depends: WAVE-H complete ✅
   ```

4. **Paste into Copilot Chat → Press Enter**

5. **Monitor Progress (expect 3-4 hours):**
   - Watch ASCII progress bars
   - Silent execution (no prompts)
   - Automatic commits
   - Completion report at end

---

## 📊 SESSION-SCOPED WAVES ROADMAP

### Execution Sequence (Sequential Dependencies)

```
WAVE-H ✅ COMPLETE
   ↓
WAVE-I ⚪ READY (3-4h) → Phase Template CLI
   ↓
WAVE-J ⚪ READY (3-4h) → Cleanup Audit
   ↓
WAVE-K ⚪ READY (3-4h) → Architecture Verification
   ↓ [MILESTONE: Wave 6 Complete]
WAVE-L ⚪ BLOCKED (4h) → Agent Redesign
   ↓
WAVE-M ⚪ BLOCKED (3h) → Language Refinement
   ↓ [MILESTONE: Wave 2 Complete]
WAVE-N ⚪ BLOCKED (4h) → Autonomous Execution
   ↓
WAVE-O ⚪ BLOCKED (4h) → Data Integrity
   ↓ [MILESTONE: Wave 3 Complete]
```

**Total Timeline:** 25-28 hours (7 sessions × 3-4h each)

---

## 🔥 WAVE DETAILS: READY TO EXECUTE (I, J, K)

### WAVE-I: Phase Template CLI (ENH-084)

**Status:** ⚪ READY (unblocked by Wave H ✅)  
**Duration:** 3-4 hours  
**Token Budget:** <150k  
**ROI:** 9.5 (HIGHEST in Wave 6)

**Value Delivered:**
- ✅ Phase creation 50% faster
- ✅ Zero orphan phases (validation enforced)
- ✅ Template-driven consistency
- ✅ 15+ CLI tests

**Deliverables:**
1. `cortex/cli/phase_template_cli.py` (NEW - 300 LOC)
2. 50+ validation rules (automated)
3. 15+ CLI tests (RED→GREEN→REFACTOR)
4. `.github/prompts/PHASE-CREATION-GUIDE.md` (user guide)

**Execution Command:** *(see Quick Start above)*

**Verification:**
```bash
# After completion, verify:
python3 -m pytest tests/unit/cli/test_phase_template_cli.py -v
# Expected: 15/15 passing

# Test CLI:
python3 -m cortex.cli.phase_template_cli create --name "test-phase" --priority "P1-HIGH"
# Expected: Phase created in <2 minutes
```

---

### WAVE-J: Cleanup Audit (ENH-085 S1-S2)

**Status:** ⚪ READY (will be unblocked after Wave I)  
**Duration:** 3-4 hours  
**Token Budget:** <170k  
**ROI:** 8.8

**Value Delivered:**
- ✅ Codebase reduction: 15-25%
- ✅ Duplicate code eliminated (CORE-035)
- ✅ Dead code archived
- ✅ 18+ detection tests

**Deliverables:**
1. `cortex/tools/duplicate_detector.py` (AST-based, 400 LOC)
2. `cortex/tools/dead_code_analyzer.py` (import graph, 350 LOC)
3. Phase archival workflow (automated to `.archive/`)
4. 18+ detection tests (TDD)

**Execution Command:**
```
/implement WAVE-J: ENH-085 Completed Phase Cleanup Audit

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-J-20260214-01
Token Budget: <170k

Scope:
1. Duplicate code detection (AST-based, CORE-035 enforcement)
2. Dead code identification (import graph + usage analysis)
3. Phase archival workflow (automated archival to .archive/)
4. 18+ detection tests (TDD: RED→GREEN→REFACTOR)
5. Integration with VacuumOrchestrator (ENH-036)

Success Criteria:
- ✅ 18/18 tests passing
- ✅ 2 commits pushed
- ✅ Codebase reduced 15-25% (verified via git diff --stat)
- ✅ Zero duplicate code violations (CORE-035)
- ✅ Dead code archived (not deleted, for rollback)

Depends: WAVE-I complete
```

**Verification:**
```bash
# After completion:
python3 -m pytest tests/unit/tools/test_duplicate_detector.py -v
python3 -m pytest tests/unit/tools/test_dead_code_analyzer.py -v
# Expected: 18/18 passing

# Check codebase reduction:
git diff HEAD~2 --stat | tail -5
# Expected: Net reduction 15-25%
```

---

### WAVE-K: Architecture Verification (ENH-086)

**Status:** ⚪ READY (will be unblocked after Wave J)  
**Duration:** 3-4 hours  
**Token Budget:** <160k  
**ROI:** 9.0  
**Milestone:** ✅ **WAVE 6 CLEANUP COMPLETE**

**Value Delivered:**
- ✅ CORE rules: 100% compliance (30/30)
- ✅ MCP-FIRST: 0 violations (CORE-049)
- ✅ Architecture patterns verified
- ✅ 15+ compliance tests

**Deliverables:**
1. `cortex/governance/compliance/core_rules_verifier.py` (30/30 rules, 450 LOC)
2. `cortex/governance/compliance/mcp_first_detector.py` (CORE-049, 280 LOC)
3. Architecture pattern checks (Strategy, EventBus, TDD)
4. 15+ compliance tests (TDD)

**Execution Command:**
```
/implement WAVE-K: ENH-086 Architecture Alignment Verification

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-K-20260215-01
Token Budget: <160k

Scope:
1. CORE rules verification (30/30 automated checks)
2. MCP-FIRST violation detection (CORE-049)
3. Architecture pattern enforcement (Strategy, EventBus)
4. 15+ compliance tests (TDD: RED→GREEN→REFACTOR)
5. Integration with EnforcementOrchestrator (7-agent system)

Success Criteria:
- ✅ 15/15 tests passing
- ✅ 2 commits pushed
- ✅ 100% CORE rules compliance (30/30)
- ✅ 0 MCP-FIRST violations detected
- ✅ Architecture patterns verified (Strategy, EventBus)

Depends: WAVE-J complete
Milestone: Wave 6 Cleanup COMPLETE ✅
```

**Verification:**
```bash
# After completion:
python3 -m pytest tests/unit/governance/compliance/ -v
# Expected: 15/15 passing

# Run compliance audit:
python3 -m cortex.governance.compliance.core_rules_verifier
# Expected: 30/30 rules passing

python3 -m cortex.governance.compliance.mcp_first_detector
# Expected: 0 violations detected
```

---

## 🔒 BLOCKED WAVES (L-O): Post-Wave K

### WAVE-L: Agent Redesign (phase-81 S1-S3)

**Status:** ⚪ BLOCKED (requires Wave K)  
**Duration:** 4 hours  
**Token Budget:** <180k  
**ROI:** 8.0

**Execution After Wave K Complete:**
```
/implement WAVE-L: phase-81 Agent Architecture Redesign S1-S3

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-L-20260216-01

Scope:
1. Agent lazy loading system
2. Agent-orchestrator patterns
3. 11-agent consolidation
4. 25+ agent tests (TDD)

Success: All tests passing + 3 commits + 60% token reduction
Depends: WAVE-K complete (Wave 6 finished)
```

---

### WAVE-M: Language Refinement (ENH-078)

**Status:** ⚪ BLOCKED (requires Wave L)  
**Duration:** 3 hours  
**Token Budget:** <160k  
**ROI:** 8.2

**Execution After Wave L Complete:**
```
/implement WAVE-M: ENH-078 Language Refinement Complete

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-M-20260217-01

Scope:
1. Intent classification refinement
2. Clarification reduction system
3. NLP pipeline updates
4. 20+ language tests (TDD)

Success: All tests passing + 2 commits + 90% intent accuracy
Depends: WAVE-L complete
Milestone: Wave 2 Intelligence COMPLETE ✅
```

---

### WAVE-N: Autonomous Execution (ENH-067)

**Status:** ⚪ BLOCKED (requires Wave M)  
**Duration:** 4 hours  
**Token Budget:** <180k  
**ROI:** 8.5

**Execution After Wave M Complete:**
```
/implement WAVE-N: ENH-067 Autonomous Plan Execution

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-N-20260218-01

Scope:
1. Autonomous execution engine
2. Progress tracking system
3. Rollback mechanism
4. 25+ execution tests (TDD)

Success: All tests passing + 3 commits + approve→done working
Depends: WAVE-M complete
```

---

### WAVE-O: Data Integrity (ENH-068/069)

**Status:** ⚪ BLOCKED (requires Wave N)  
**Duration:** 4 hours  
**Token Budget:** <190k  
**ROI:** 8.3

**Execution After Wave N Complete:**
```
/implement WAVE-O: ENH-068/069 Data Integrity & Explainability

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-O-20260219-01

Scope:
1. Data integrity validation
2. Dashboard explainability layer
3. KPI transparency features
4. 30+ validation tests (TDD)

Success: All tests passing + 3 commits + trust features deployed
Depends: WAVE-N complete
Milestone: Wave 3 Autonomy COMPLETE ✅
```

---

## 📊 SESSION EXECUTION CHECKLIST

### Before Starting Each Wave

- [ ] Previous wave complete (verify git log)
- [ ] Test collection passing (21700+)
- [ ] Git workspace clean
- [ ] Python environment active
- [ ] VS Code + Copilot Chat ready
- [ ] Token budget understood (<200k)

### During Execution (Silent Mode)

- [ ] Watch ASCII progress bars
- [ ] NO interruptions (let it run)
- [ ] Monitor token usage (if visible)
- [ ] Note any errors immediately

### After Completion

- [ ] Verify tests passing (run pytest)
- [ ] Check commits pushed (git log)
- [ ] Update index.yaml wave status
- [ ] Create completion report (optional)
- [ ] Start next wave (if unblocked)

---

## 🎯 SUCCESS CRITERIA PER WAVE

| Wave | Tests | Commits | Duration | Key Metric |
|------|-------|---------|----------|------------|
| I | 15/15 | 2 | 3-4h | CLI demo <2min |
| J | 18/18 | 2 | 3-4h | 15-25% codebase reduction |
| K | 15/15 | 2 | 3-4h | 30/30 CORE rules passing |
| L | 25/25 | 3 | 4h | 60% token reduction |
| M | 20/20 | 2 | 3h | 90% intent accuracy |
| N | 25/25 | 3 | 4h | Approve→done working |
| O | 30/30 | 3 | 4h | Data integrity checks passing |

**Total:** 148 tests, 17 commits, 25-28 hours

---

## 🚨 TROUBLESHOOTING

### Issue: "MCP tools not available"

**Symptoms:**
- Copilot Chat error: "cortex_process_request not found"
- VS Code not showing MCP tools

**Fix:**
```bash
# Run MCP setup
cd /Users/asifhussain/PROJECTS/CORTEX
python3 .cortex/setup-mcp.py

# Reload VS Code
# Command Palette → Developer: Reload Window

# Verify in new Copilot Chat session
```

---

### Issue: "Tests failing after wave completion"

**Symptoms:**
- pytest shows failures
- Regression in previously passing tests

**Fix:**
```bash
# Check git diff
git diff HEAD~1

# Identify failing tests
python3 -m pytest tests/ -v --tb=short | grep FAILED

# Rollback if critical
git revert HEAD

# Report issue for investigation
```

---

### Issue: "Token budget exceeded mid-wave"

**Symptoms:**
- Copilot Chat stops responding
- "Token limit reached" message

**Fix:**
1. **Save Progress:**
   ```bash
   git add -A
   git commit -m "WAVE-{X}: Checkpoint (partial completion)"
   ```

2. **Open New Copilot Chat Session**

3. **Resume with Continuation Prompt:**
   ```
   /continue WAVE-{X}: Resume from checkpoint
   
   Context: Previous session hit token limit
   Checkpoint: {describe what was completed}
   Remaining: {list incomplete tasks}
   
   Authority: cortex-registry/_cortex-master/index.yaml v2.2
   Mode: Silent autonomous (resume)
   ```

---

## 📈 PROGRESS TRACKING

### Update index.yaml After Each Wave

```yaml
# Example: After WAVE-I completion
- wave: "I"
  status: "complete"  # ⚪ READY → ✅ COMPLETE
  completion_date: "2026-02-13"
  tests_completed: 15
  commits_completed: 2
```

### Create Completion Report (Optional)

```markdown
# WAVE-{X} Completion Report
**Date:** 2026-02-{DD}
**Duration:** {X}h
**Tests:** {Y}/{Y} passing
**Commits:** {Z} pushed

## Deliverables
- ✅ {Deliverable 1}
- ✅ {Deliverable 2}
- ...

## Verification
```bash
# Commands run to verify
```

## Next Steps
Start WAVE-{X+1} (unblocked)
```

---

## 🎯 MILESTONES

| Milestone | Waves | Tests | Status |
|-----------|-------|-------|--------|
| **Foundation** | A-E | 148 | ✅ COMPLETE |
| **Orchestrator Consolidation** | 7 | 233 | ✅ COMPLETE |
| **Planning Capability** | 8 | 108 | ✅ COMPLETE |
| **Response Templates** | H | 65 | ✅ COMPLETE |
| **Wave 6 Cleanup** | I-K | 48 | ⚪ READY |
| **Wave 2 Intelligence** | L-M | 45 | ⚪ BLOCKED |
| **Wave 3 Autonomy** | N-O | 55 | ⚪ BLOCKED |

---

## 📚 REFERENCE DOCUMENTS

| Document | Location | Purpose |
|----------|----------|---------|
| Master Index | `cortex-registry/_cortex-master/index.yaml` | Wave specifications |
| Reality Sync | `IMPLEMENTATION-REALITY-SYNC-V4-2026-02-12.md` | Verification report |
| Architect Prompt | `.github/prompts/cortex-architect.prompt.md` | Execution rules |
| CORE Rules | `cortex-registry/governance/core-rules.yaml` | Governance standards |

---

## ✅ READY TO EXECUTE

**Current State:** WAVE-I ready (unblocked by Wave H ✅)

**Next Action:** Copy WAVE-I execution command → Paste into Copilot Chat → Execute

**Expected Completion:** 2026-02-13 (3-4 hours)

**After WAVE-I:** WAVE-J becomes ready (auto-unblocked)

---

**Generated:** 2026-02-12T22:30:00Z  
**Authority:** cortex-architect.prompt.md v15.3  
**Registry:** cortex-registry/_cortex-master/index.yaml v2.2  
**Status:** ✅ ACTIVE & READY
