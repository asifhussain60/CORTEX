# Phase 1.5 Continuation Prompt - MCP-Copilot CLI Bridge

**Phase:** 1.5 - MCP-Copilot CLI Bridge (4 hours)  
**Status:** 🔴 CRITICAL BLOCKER  
**Priority:** HIGHEST (unblocks 7,067 lines of dormant code)

---

## 🎯 Phase Objective

Create terminal-based CLI bridge that makes MCP orchestrators callable by GitHub Copilot via `run_in_terminal`.

**Problem:** Phase 1 built Python MCP infrastructure but GitHub Copilot cannot invoke it.  
**Solution:** CLI wrapper script that bridges Copilot → Terminal → MCP → Python Orchestrators

---

## 📋 Task Checklist

### Task 1.5.1: Create CLI Bridge Script (2h)
- [ ] Create `scripts/cortex-cli.py` with universal orchestrator invocation
- [ ] Implement argument parsing (orchestrator name, user request, options)
- [ ] Load MCP registry from `cortex-brain/config/mcp-server.yaml`
- [ ] Call `invoke_orchestrator()` from `src/mcp/tools/invoke_orchestrator.py`
- [ ] Format output for terminal display (progress bars, colors)
- [ ] Add error handling (user-friendly messages, no tracebacks)
- [ ] Implement version checking (CLI vs orchestrator compatibility)
- [ ] Test cross-platform compatibility (Mac minimum, Windows/Linux nice-to-have)

**CLI Interface:**
```bash
python scripts/cortex-cli.py plan "Build user authentication"
python scripts/cortex-cli.py planning continue
python scripts/cortex-cli.py ado "create story for feature X"
python scripts/cortex-cli.py cleanup cache
python scripts/cortex-cli.py vacuum /path/to/cleanup
python scripts/cortex-cli.py orchestrate <name> <request>
```

### Task 1.5.2: Update CORTEX.prompt.md Protocol (1h)
- [ ] Replace "HAND-OFF → STOP" with "HAND-OFF → INVOKE" (lines 80-95)
- [ ] Update Intent Router table with CLI invocation examples
- [ ] Add terminal bridge documentation section
- [ ] Update Planning System row: "INVOKE: `python scripts/cortex-cli.py plan`"
- [ ] Update ADO Operations row: "INVOKE: `python scripts/cortex-cli.py ado`"
- [ ] Update Cleanup v2 row with CLI example
- [ ] Update Vacuum v2 row with CLI example

### Task 1.5.3: Update copilot-instructions.md (30min)
- [ ] Replace "CORTEX routes and stops" with "CORTEX invokes Python orchestrators"
- [ ] Add terminal invocation protocol section
- [ ] Document run_in_terminal usage pattern
- [ ] Add troubleshooting guide (Python not found, permission issues)

### Task 1.5.4: Integration Testing (30min)
- [ ] Test: Planning continuation ("continue with plan")
- [ ] Test: ADO story creation ("ado story for feature X")
- [ ] Test: Cleanup operation ("cleanup cache")
- [ ] Test: Vacuum operation ("vacuum /path")
- [ ] Test: Error handling (invalid orchestrator, missing params)
- [ ] Test: Cross-platform (Mac verified minimum)
- [ ] Create `tests/test_cortex_cli.py` with automated tests

---

## ✅ Completion Criteria

- [ ] CLI bridge operational (all 7 orchestrators callable)
- [ ] CORTEX.prompt.md updated with INVOKE protocol
- [ ] copilot-instructions.md updated with terminal invocation guide
- [ ] 4 integration tests pass (planning, ado, cleanup, vacuum)
- [ ] Error messages user-friendly (no raw Python tracebacks)
- [ ] Cross-platform compatibility verified (Mac minimum)
- [ ] Git checkpoint created: `checkpoint-phase-1.5-cli-bridge`

**Success Metric:** User says "continue with plan" → Copilot executes `python scripts/cortex-cli.py planning continue` → Planning v5 resumes autonomously

---

## 🚀 Impact

**Code Activated:** 7,067 lines across 8 phases
- Planning System v5: 763 lines
- Master Orchestrator: 584 lines
- Cleanup v2: 1,955 lines
- Vacuum v2: 2,442 lines
- ADO v2: ~200 lines
- Context Middleware: ~150 lines
- State tracking: ~973 lines

**Phases Unblocked:**
- Phase 3: Master Orchestrator (finally callable)
- Phase 4: Planning v5 (finally executable)
- Phase 4.5: Context Middleware (finally engaged)
- Phase 6.1-6.3: ADO/Cleanup/Vacuum (finally autonomous)
- Phase 6.5-6.8: TDD/Debug/Sanitization migrations (can now be truly autonomous)

**ROI:** 81:1 (40.5 days activated / 4 hours effort)

---

## 🔗 Next Phase

**After Phase 1.5 Complete:**
- Phase 6.5: TDD v2 Migration (4 days) - NOW truly autonomous
- Phase 6.6: Debug v2 Migration (3 days) - NOW truly autonomous
- Phase 6.7: Sanitization v2 Migration (2 days) - NOW truly autonomous
- Phase 6.8: Refinement Enhancements (4 hours) - Remains GUIDED

**Key Change:** Phases 6.5-6.8 were "approved for AUTONOMOUS" but blocked by invocation mechanism. Phase 1.5 unblocks them.

---

## 📁 Files to Create/Modify

**New Files:**
- `scripts/cortex-cli.py` (CLI bridge implementation)
- `scripts/__init__.py` (package initialization)
- `tests/test_cortex_cli.py` (integration tests)

**Modified Files:**
- `.github/prompts/CORTEX.prompt.md` (HAND-OFF → INVOKE protocol)
- `.github/copilot-instructions.md` (terminal invocation guide)
- `00-MASTER-PLAN-V5.md` (Phase 1.5 added, priorities updated)

**Git Checkpoint:**
- Commit message: "✅ Phase 1.5 COMPLETE: MCP-Copilot CLI Bridge - 7,067 lines activated"
- Tag: `checkpoint-phase-1.5-cli-bridge`

---

**To resume Phase 1.5:** Start with Task 1.5.1 (Create CLI Bridge Script)
