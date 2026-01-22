# CORTEX Eval Track - Quick Reference Card

## Configuration Summary

**Status:** ✅ COMPLETE  
**Commits:** 4  
**Phases Configured:** 10  
**Output Verbosity:** MINIMAL (single-line per phase)  
**Mock Implementations:** FORBIDDEN  

---

## Execution Command

```bash
machine:eval
```

**Result:** All eval track phases execute silently, autonomously until completion or blocker

---

## Execution Output Format

```
✓ {phase-id}: {brief-summary} → Next: {next-phase-id}
```

**Example:**
```
✓ PHASE-EVAL-001-TEST-REMEDIATION: Completed → Next: PHASE-AUDIT-001-EXPORT-VERIFY
✓ PHASE-AUDIT-001-EXPORT-VERIFY: Collection verified → Next: PHASE-AUDIT-002-PHASE-E-VERIFY
✓ PHASE-AUDIT-002-PHASE-E-VERIFY: 90%+ real implementations → Next: PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT
```

---

## Phases in Execution Order

| Seq | Phase ID | Title | Type | Status |
|-----|----------|-------|------|--------|
| 0 | PHASE-EVAL-001 | Test Remediation | test_fix | ✅ COMPLETED |
| 1 | PHASE-AUDIT-001 | Export Verification | audit | NOT_STARTED |
| 1 | PHASE-AUDIT-002 | Phase E Verification | audit | NOT_STARTED |
| 2 | PHASE-AUDIT-003 | Import Migration | audit | NOT_STARTED |
| 2 | PHASE-AUDIT-004 | Governance Compliance | audit | NOT_STARTED |
| 3 | CLEANUP-001 | Roadmap Maintenance | cleanup | NOT_STARTED |
| 3 | PHASE-AUDIT-005 | Git Checkpoint | verify | NOT_STARTED |
| 4 | PHASE-AUDIT-006 | Docstring Compliance | analysis | NOT_STARTED |
| 4 | PHASE-AUDIT-007 | Coverage Baseline | metrics | NOT_STARTED |
| 6 | PHASE-KG-001 | Knowledge Graph Foundation | feature | NOT_STARTED |

---

## Key Mandates

### ✅ REQUIRED
- Real code solving actual problems
- Production-ready quality
- 100% type hints (CORE-011)
- Google docstrings (CORE-012)
- Comprehensive tests
- Full AC completion
- No bare except clauses (CORE-013)

### ❌ FORBIDDEN
- Mock objects/implementations
- Stub code with empty methods
- Hardcoded return values
- Governance rule violations
- Incomplete AC implementations
- User confirmation prompts
- Multi-line output between phases
- Status/progress reports
- .md files (except docs/)

---

## Governance Rules Enforced

| Rule | Requirement |
|------|-------------|
| CORE-001 | Production quality code |
| CORE-008 | Tests-first (TDD) |
| CORE-011 | 100% type hints |
| CORE-012 | Google docstrings |
| CORE-013 | No bare except |
| CORE-017 | Strict governance |
| CORE-026 | Git checkpoints |
| CORE-027 | Audit trail logging |

---

## Configuration Files

| File | Type | Location |
|------|------|----------|
| cortex-impl-map.yaml | Main config | _workspaces/roadmap/ |
| EVAL-TRACK-AUTONOMOUS-EXECUTION-CONFIG.md | Docs | _workspaces/roadmap/ |
| EVAL-TRACK-CONFIGURATION-COMPLETE.md | Docs | _workspaces/roadmap/ |
| EVAL-TRACK-VERIFICATION-FINAL.md | Report | _workspaces/roadmap/ |

---

## Testing & Validation

**Pre-Execution Checks:**
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('_workspaces/roadmap/cortex-impl-map.yaml')); print('✅ YAML valid')"

# Verify eval phases exist
grep -c "track: \"eval\"" _workspaces/roadmap/cortex-impl-map.yaml
```

**Expected:** 10+ eval track phases configured

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| YAML parse error | Run validation command above |
| Phase not executing | Check dependencies in cortex-impl-map.yaml |
| Mock code found | Reject and require real implementation |
| Test threshold failed | Run tests with real implementation |
| Output too verbose | Verify `verbosity: "minimal"` in config |

---

## Related Documentation

- Full config: `EVAL-TRACK-AUTONOMOUS-EXECUTION-CONFIG.md`
- Completion status: `EVAL-TRACK-CONFIGURATION-COMPLETE.md`
- Verification report: `EVAL-TRACK-VERIFICATION-FINAL.md`
- Authority: `cortex-builder.prompt.md` §ZERO OUTPUT MODE

---

## Ready for Execution ✅

All systems configured. Eval track ready for autonomous execution.

```bash
machine:eval
```

No user intervention required. All phases will execute silently with real implementations until completion.
