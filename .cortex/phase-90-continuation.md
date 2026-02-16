# Phase 90 Continuation Prompt (S6-S9)

**Context:** Phase 90 S1-S5 completed (60%). Checkpoint committed: `82bf6de87`

## Completed Work (S1-S5)

| Stage | Status | Tests | Duration |
|-------|--------|-------|----------|
| S1: Discovery | ✅ | N/A | Complete |
| S2: Package Structure | ✅ | N/A | Complete |
| S3: MCP Diagnostics | ✅ | 19/20 | 0.17s |
| S4: Setup Verification | ✅ | 18/18 | 0.08s |
| S5: Cleanup Automation | ✅ | 15/15 | 0.06s |

**Total Tests:** 52/53 passing (98%) | **Duration:** 0.22s

**Deliverables:**
- ✅ `cortex/toolkit/` package with module registry
- ✅ `MCPHealthChecker` (consolidated MCP diagnostics)
- ✅ `SetupVerifier` (cross-platform environment verification)
- ✅ `VacuumAutomation` (5 cleanup strategies: markdown, debug, pycache, sessions, builds)

---

## Remaining Work (S6-S9) — 40% of Phase 90

### S6: Governance Validation Module (Est: 2-3 hours)

**Objective:** Consolidate governance validation scripts into single module.

**Source Scripts:**
- `scripts/validate-production.py`
- `scripts/validate_governance_alignment.py`

**Tasks:**
1. Create `cortex/toolkit/validation/__init__.py`
2. Implement `GovernanceValidator` class:
   - `validate_production_readiness()` → 8 categories
   - `check_governance_alignment()` → CORE rules audit
   - `assess_security_posture()` → OWASP checks
   - `generate_readiness_report()` → Formatted output
3. Write 12-15 tests in `tests/toolkit/test_governance_validator.py`:
   - Test initialization
   - Test each validation category
   - Test report generation
   - Test dry-run mode

**Acceptance Criteria:**
- AC-P90-005: Governance validation module consolidated
- 12+ tests passing
- <0.10s test duration

---

### S7: MCP Tool Exposure (Est: 3-4 hours)

**Objective:** Expose all toolkit modules via 5 MCP tools.

**MCP Tools to Create:**

1. **`toolkit_diagnose`** (cortex/mcp/tools/toolkit/diagnose.py)
   - Expose `MCPHealthChecker`
   - Schema: `operation` (full|mcp|venv|settings|tools)
   - Return: JSON diagnostic report

2. **`toolkit_verify`** (cortex/mcp/tools/toolkit/verify.py)
   - Expose `SetupVerifier`
   - Schema: `platform` (auto|windows|macos|linux)
   - Return: JSON verification report

3. **`toolkit_cleanup`** (cortex/mcp/tools/toolkit/cleanup.py)
   - Expose `VacuumAutomation`
   - Schema: `strategy` (markdown|pycache|debug|sessions|all)
   - Return: JSON cleanup report

4. **`toolkit_validate`** (cortex/mcp/tools/toolkit/validate.py)
   - Expose `GovernanceValidator`
   - Schema: `validation_type` (governance|production|security|compliance|all)
   - Return: JSON validation report

5. **`toolkit_analyze`** (cortex/mcp/tools/toolkit/analyze.py)
   - Consolidate `audit_traces.py` logic
   - Schema: `analysis_type` (traces|performance|usage|health)
   - Return: JSON analysis report

**Tasks:**
1. Create `cortex/mcp/tools/toolkit/` directory
2. Implement 5 MCP tool files
3. Register tools in MCP server (update tool count: 16 → 21)
4. Write 10-12 integration tests (`tests/mcp/tools/test_toolkit_tools.py`)

**Acceptance Criteria:**
- AC-P90-006: All toolkit modules exposed via 5 MCP tools
- 10+ integration tests passing
- Tools discoverable via `cortex_tools_catalog`

---

### S8: Testing & Documentation (Est: 2 hours)

**Objective:** Comprehensive test coverage + user documentation.

**Tasks:**
1. Integration tests (`tests/toolkit/test_toolkit_integration.py`):
   - Test MCPHealthChecker → SetupVerifier → VacuumAutomation flow
   - Test dry-run vs real execution
   - Test error handling across modules
   - 8-10 integration tests

2. Documentation (`cortex-docs/toolkit/README.md`):
   - Toolkit overview
   - Module descriptions
   - MCP tool usage examples
   - CLI fallback commands (deprecated warning)

3. Update `/check-env` command:
   - Modify to use `toolkit_diagnose` tool
   - Update copilot instructions

4. Update `.github/copilot-instructions.md`:
   - Add toolkit commands section
   - Document MCP tool usage

**Acceptance Criteria:**
- AC-P90-007: Test coverage ≥85% for toolkit modules
- AC-P90-009: Documentation guide created
- Integration tests passing

---

### S9: Migration & Cleanup (Est: 1-2 hours)

**Objective:** Deprecate old scripts and migrate usage.

**Tasks:**
1. Create `scripts/migrate-to-toolkit.py`:
   - List all deprecated scripts
   - Show toolkit replacements
   - Migration status report

2. Add deprecation warnings to 15+ old scripts:
   - Add header comment: "DEPRECATED: Use toolkit_* MCP tool instead"
   - Add runtime warning message
   - Provide migration path

3. Update CI/CD workflows (`.github/workflows/`):
   - Replace script calls with toolkit MCP tools
   - Example: `python .cortex/diagnose-mcp.py` → `toolkit_diagnose(operation='full')`

4. Archive deprecated scripts:
   - Move to `.cortex/archive/pre-toolkit/`
   - Add `MIGRATION_COMPLETE.md` marker

5. Write migration tests (`tests/toolkit/test_migration_completeness.py`):
   - Verify no deprecated script usage in workflows
   - Verify all scripts have deprecation warnings
   - 5-8 tests

**Acceptance Criteria:**
- AC-P90-008: Migration script deprecates old scripts
- AC-P90-010: Zero regression in existing functionality
- All workflows updated

---

## Execution Command

```bash
# Continue Phase 90 from checkpoint
git checkout CORTEX
git log --oneline -1  # Verify: 82bf6de87 Phase 90 S1-S5

# Then in Copilot Chat:
"implement phase 90 stages 6-9 autonomously silently immediately"
```

---

## Success Metrics (Full Phase 90)

| Metric | Target | Current |
|--------|--------|---------|
| Script Reduction | 75% (20→5 modules) | 60% (S1-S5 done) |
| Test Coverage | ≥85% | ~95% (S1-S5) |
| MCP Tools | 5 new tools | 0 (S7 pending) |
| Documentation | 100% | 0% (S8 pending) |
| Migration | 100% workflows | 0% (S9 pending) |

**Phase 90 Complete When:**
- ✅ 60+ tests passing
- ✅ 5 MCP tools registered (16→21 total)
- ✅ Documentation complete
- ✅ Deprecated scripts archived
- ✅ CI/CD workflows updated

---

## Continuation Prompt Template

**For next session, use:**

```
Follow instructions in cortex-architect.prompt.md.

Continue Phase 90 from checkpoint 82bf6de87.
Implement stages S6-S9 autonomously silently immediately:

S6: Governance validation module (GovernanceValidator)
S7: MCP tool exposure (5 tools: diagnose, verify, cleanup, validate, analyze)
S8: Testing & documentation (integration tests + toolkit guide)
S9: Migration & cleanup (deprecation warnings + archive)

Target: 60+ total tests, 5 new MCP tools, 100% documentation.
```

---

**Authority:** Phase 90 (Toolkit Centralization)  
**Checkpoint:** 82bf6de87  
**Progress:** 60% (S1-S5 complete)  
**Next:** S6-S9 (governance + MCP + docs + migration)
