# CORTEX Lens Testing Continuation Prompt

**Date:** December 13, 2025  
**Session Type:** Autonomous Testing Continuation  
**Context:** Phase 6 - Testing & Optimization

---

## 📋 Quick Context

Continue CORTEX Lens Phase 6 testing. Current status:
- **287 tests passing** (269 + 18 orchestrator), **23 skipped**
- **Coverage: 66%** (target: 75%)
- **Completed modules:**
  - ✅ Collectors (9 modules, 48 tests)
  - ✅ Analyzers (4 modules, 32 tests)
  - ✅ Core (3 modules, 63 tests)
  - ✅ Generators (5 modules, 76 tests)
  - ✅ Narratives (7 modules, 20 tests via integration)
  - ✅ Orchestrator (1 module, 18 tests, 100% coverage)

## 🎯 Next Targets

**Immediate Focus: CLI Module (101 LOC, 0% coverage)**

The CLI module (`src/cortex_lens/cli.py`) is the command-line interface entry point. Create comprehensive tests to cover:

1. **Argument Parsing**
   - `scan` command with path argument
   - `analyze` command with options (--output, --template, --format)
   - `compare` command with multiple paths
   - Invalid argument handling

2. **Command Execution**
   - Verify CLI delegates to CortexLens class correctly
   - Test output path handling (default vs custom)
   - Test template selection
   - Test export format options (json, yaml, csv)

3. **Error Handling**
   - Invalid repository paths
   - Missing required arguments
   - Permission errors
   - Malformed options

4. **Integration**
   - End-to-end command execution (mocked CortexLens)
   - Help text display
   - Version information

**Expected Outcome:**
- Create `tests/cortex_lens/test_cli.py` with ~20-25 tests
- Push coverage from 66% → ~70%
- Achieve 100% CLI module coverage

## 📚 Reference Files

- **Plan:** `cortex-brain/documents/planning/cortex-lens-plan-v2.md`
- **CLI Source:** `src/cortex_lens/cli.py`
- **Orchestrator Tests (Reference):** `tests/cortex_lens/test_orchestrator.py`

## 🚀 Start Command

```
"Analyze CLI module and create comprehensive tests. Reference orchestrator tests for mocking patterns."
```

---

## 📊 Success Metrics

- [ ] 20-25 CLI tests created
- [ ] All tests passing
- [ ] Coverage: 66% → 70%
- [ ] CLI module: 0% → 100%
- [ ] No regressions (287 → 307 passing tests)
