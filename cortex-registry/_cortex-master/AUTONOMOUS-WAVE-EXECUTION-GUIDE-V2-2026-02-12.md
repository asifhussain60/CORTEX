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
   Mode: Silent autonomous execution (structured progress reports)
   Session: WAVE-I-20260213-01
   Token Budget: <150k
   
   Scope:
   1. Phase template CLI tool (cortex/cli/phase_template_cli.py)
   2. 50+ validation rules (naming, structure, dependencies)
   3. 15+ CLI tests (TDD: RED→GREEN→REFACTOR)
   4. User guide documentation (.github/prompts/PHASE-CREATION-GUIDE.md)
   5. Integration with EnforcementOrchestrator (CORE-043)
   
   Response Format: Markdown tables per `.github/prompts/SILENT-EXECUTION-RESPONSE-TEMPLATE.md`
   
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
WAVE-J ⚪ READY (4-5h) → MCP Enforcement + Tool Consolidation (91→18)
   ↓                     ├─ Prompt/Agent hardening
   ↓                     ├─ Tool consolidation (80% reduction)
   ↓                     └─ 25 high-value tests (integration+regression+e2e)
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

**Total Timeline:** 26-30 hours (7 sessions × 3-5h each)

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

### WAVE-J: MCP Enforcement + Tool Consolidation (ENH-085 ENHANCED)

**Status:** ⚪ READY (will be unblocked after Wave I)  
**Duration:** 4-5 hours  
**Token Budget:** <180k  
**ROI:** 9.5 (CRITICAL - blocks all other waves if MCP broken)

**Value Delivered:**
- ✅ MCP-FIRST: Hard enforcement (cannot bypass)
- ✅ Tool sprawl: 91→18 tools (80% reduction)
- ✅ Prompts/Agents: Mandatory MCP pre-flight checks
- ✅ Test harness: Integration + regression + e2e
- ✅ Cross-platform: Windows/macOS/Linux verified

**Deliverables:**

**Stage 1: Prompt Hardening (copilot-instructions.md)**
1. Move MCP check to ABSOLUTE TOP (line 1-50)
2. Visual "gate closed" ASCII when blocked
3. Preserve DIAGNOSE/SETUP escape hatch (CORE-050 tiered)
4. Remove ALL "fallback to native tools" language

**Stage 2: Agent Enforcement (11 core agents)**
1. Add MCP pre-flight check to EVERY agent header
2. Standardize "MCP Required" section in all agents
3. Remove any "work without MCP" instructions
4. Add dependency declaration: `requires: [cortex_mcp_server]`

**Stage 3: Tool Consolidation (91→18)**
1. `cortex_debug` (13→1): Single entry with operation param
2. `cortex_governance` (6→1): Unified governance tool
3. `cortex_dashboard` (10→1): Single dashboard tool
4. `cortex_plan` (5→1): Unified planning tool
5. `cortex_validate` (5→1): Unified validation tool
6. REMOVE: echo_tool, sample_tool, transform_tool (dev-only)
7. Deprecation aliases for backward compatibility

**Stage 4: Test Harness (HIGH VALUE - 25 tests)**

| Test Type | File | Purpose | Priority |
|-----------|------|---------|----------|
| **Integration** | test_mcp_server_init_syncs_tools.py | Verify 18 tools registered on server start | P0 |
| **Integration** | test_mcp_tool_invocation_e2e.py | Full roundtrip: Copilot → MCP → Orchestrator → Response | P0 |
| **Regression** | test_mcp_required_for_implement.py | IMPLEMENT intent blocked without MCP | P0 |
| **Regression** | test_mcp_required_for_fix.py | FIX intent blocked without MCP | P0 |
| **Regression** | test_mcp_required_for_refactor.py | REFACTOR intent blocked without MCP | P0 |
| **Regression** | test_diagnose_allowed_without_mcp.py | DIAGNOSE intent allowed (escape hatch) | P0 |
| **Regression** | test_setup_allowed_without_mcp.py | SETUP intent allowed (escape hatch) | P0 |
| **E2E** | test_cross_platform_mcp_setup.py | Windows/macOS/Linux path detection | P0 |
| **E2E** | test_settings_json_not_tracked.py | .vscode/settings.json NOT in git | P0 |
| **E2E** | test_post_checkout_hook_regenerates.py | Hook regenerates settings on pull | P1 |
| **Unit** | test_tool_consolidation_aliases.py | Old tool names → new unified tools | P1 |
| **Unit** | test_tool_registry_sync_count.py | Exactly 18 tools after consolidation | P1 |
| **Unit** | test_dev_tools_removed.py | echo/sample/transform not in production | P1 |
| **Governance** | test_core_050_tiered_blocking.py | Tiered blocking per CORE-050 | P0 |
| **Governance** | test_core_051_cross_platform.py | Cross-platform compliance per CORE-051 | P0 |

**Stage 5: Documentation Sync**
1. Update MCP-SETUP-GUIDE.md with consolidated tools
2. Update CORTEX.prompt.md tool reference (18 tools)
3. Archive old tool documentation to .archive/

**Execution Command:**
```
/implement WAVE-J: MCP Enforcement + Tool Consolidation (ENH-085 ENHANCED)

Authority: cortex-registry/_cortex-master/index.yaml v2.2
Mode: Silent autonomous execution (structured progress reports)
Session: WAVE-J-20260214-01
Token Budget: <180k

Scope:
1. Prompt hardening (MCP check at TOP of copilot-instructions.md)
2. Agent enforcement (11 core agents + MCP pre-flight)
3. Tool consolidation (91→18 tools, 80% reduction)
4. Test harness (25 tests: integration + regression + e2e + governance)
5. Documentation sync (MCP-SETUP-GUIDE.md, CORTEX.prompt.md)

Success Criteria:
- ✅ 25/25 tests passing (0 failures)
- ✅ 3 commits pushed
- ✅ Tool count: 91→18 (verified via cortex_tools_catalog)
- ✅ MCP blocking: IMPLEMENT/FIX/REFACTOR blocked without MCP
- ✅ Escape hatch: DIAGNOSE/SETUP allowed without MCP
- ✅ Cross-platform: Windows/macOS/Linux verified
- ✅ .vscode/settings.json NOT tracked in git

Depends: WAVE-I complete
```

**Verification:**
```bash
# After completion:
python3 -m pytest tests/integration/mcp/ -v
python3 -m pytest tests/regression/mcp_enforcement/ -v
python3 -m pytest tests/e2e/cross_platform/ -v
# Expected: 25/25 passing

# Verify tool count:
python3 -c "
from cortex.mcp.server import MCPServer
from cortex.mcp.tool_registry import get_mcp_tool_registry
server = MCPServer()
print(f'Tools: {len(get_mcp_tool_registry().list_all())}')
"
# Expected: Tools: 18

# Verify settings.json not tracked:
git ls-files | grep .vscode/settings.json
# Expected: (empty - not tracked)
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
Mode: Silent autonomous execution (structured progress reports)
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
Mode: Silent autonomous execution (structured progress reports)
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
Mode: Silent autonomous execution (structured progress reports)
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
Mode: Silent autonomous execution (structured progress reports)
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
Mode: Silent autonomous execution (structured progress reports)
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
| J | 25/25 | 3 | 4-5h | 91→18 tools + MCP blocking verified |
| K | 15/15 | 2 | 3-4h | 30/30 CORE rules passing |
| L | 25/25 | 3 | 4h | 60% token reduction |
| M | 20/20 | 2 | 3h | 90% intent accuracy |
| N | 25/25 | 3 | 4h | Approve→done working |
| O | 30/30 | 3 | 4h | Data integrity checks passing |

**Total:** 155 tests, 18 commits, 26-30 hours

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
