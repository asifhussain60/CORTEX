# Phase 26: Lean Prompt Architecture v5.3.0 - Summary

**Date:** 2026-01-05  
**Author:** CORTEX Planning System v5  
**Plan:** C150 Remediation  
**Gap ID:** GAP-ARCH-4

---

## 📋 Overview

Phase 26 implements the **Lean Prompt Architecture v5.3.0**, moving 300+ lines of transformation logic from prompt files to Python + YAML, reducing maintenance burden by 75%.

---

## 🎯 Motivation

**User Request (2026-01-05):**
> "Push as much logic as possible to master orchestrator keeping cortex prompt lean so changes don't affect orchestrator"

**Problem:**
- CORTEX.prompt.md (250 lines) + copilot-instructions.md (150 lines) = **400 lines of prompt logic**
- Transformation logic duplicated across 2 files
- No unit tests for transformation logic
- Changes require editing multiple files
- Prompt file drift over time (inconsistent patterns)

---

## 📊 Proposal Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **CORTEX.prompt.md** | 250 lines | 50 lines | **-80%** |
| **copilot-instructions.md** | 150 lines | 50 lines | **-67%** |
| **Total Prompt Lines** | 400 lines | 100 lines | **-75%** |
| **Python Logic** | 0 lines | 200 lines | **+200** (testable) |
| **YAML Config** | 418 lines | 550 lines | **+132** (transformation rules) |
| **Unit Tests** | 0 tests | 20+ tests | **NEW** |

---

## 🏗️ Architecture Changes

### New Components

1. **RequestTransformer (Python)** - `src/orchestrators/request_transformer.py` (200 lines)
   - `MetaDirectiveParser`: Extract `[no verbose]`, `[concise]`, `[explain]` from requests
   - `PatternMatcher`: Match user intent against routing patterns
   - `TransformationEngine`: Transform request → Python CLI command

2. **Enhanced Master Orchestrator YAML** - `cortex-brain/config/master-orchestrator.yaml` (+132 lines)
   - `transformation_rules` section
   - `meta_directives` mapping (8 directives)
   - `transformation_templates` (12 templates)
   - `routing_enhancements`

3. **Reduced Prompt Files**
   - CORTEX.prompt.md: Purpose (3) + Protocol (7) + Router (20) + Examples (15) + Footer (5) = **50 lines**
   - copilot-instructions.md: Entry (5) + Routing (10) + Format (10) + SKULL (10) + Quick Start (10) + Footer (5) = **50 lines**

---

## 📝 Implementation Plan

### Phase 1: Create RequestTransformer Module (3.0 hrs)
- Create `src/orchestrators/request_transformer.py` (200 lines)
- Implement `MetaDirectiveParser`, `PatternMatcher`, `TransformationEngine`
- Add unit tests: `tests/orchestrators/test_request_transformer.py` (150 lines)

### Phase 2: Enhance Master Orchestrator YAML (2.0 hrs)
- Add `transformation_rules` section to `master-orchestrator.yaml`
- Define `meta_directive_patterns` (8 directives)
- Define `transformation_templates` (12 templates)
- Add `routing_enhancements` section

### Phase 3: Reduce CORTEX.prompt.md (1.5 hrs)
- Backup to `.v5.2.0.backup`
- Reduce to 50 lines (Purpose + Protocol + Router + Examples + Footer)
- Remove transformation details, verbose examples, orchestrator descriptions

### Phase 4: Reduce copilot-instructions.md (1.5 hrs)
- Backup to `.v5.0.0.backup`
- Reduce to 50 lines (Entry + Routing + Format + SKULL + Quick Start + Footer)
- Remove orchestrator tables, transformation logic, verbose docs

---

## ✅ Benefits

| Benefit | Impact |
|---------|--------|
| **Single Source of Truth** | Python + YAML (no prompt file drift) |
| **Testable Logic** | 20+ unit tests for transformation logic |
| **Easier Maintenance** | Changes in 1 place (Python or YAML), not 2+ files |
| **No Duplication** | Intent matching in YAML only, referenced by Python |
| **Better Debugging** | Python stack traces, not prompt interpretation errors |
| **Version Control** | Python diffs are clearer than prompt file diffs |

---

## 🔄 Migration Path

1. **Backup:** Create `.v5.2.0.backup` and `.v5.0.0.backup` files
2. **Implement:** Build RequestTransformer + enhance YAML
3. **Test:** Run 20+ unit tests + integration tests
4. **Reduce:** Shrink prompt files to 50 lines each
5. **Validate:** Test all 12+ orchestrator routing patterns
6. **Rollback Plan:** Restore from backups if issues detected

---

## 📂 Outputs

```
src/orchestrators/request_transformer.py (200 lines)
tests/orchestrators/test_request_transformer.py (150 lines)
cortex-brain/config/master-orchestrator.yaml (+132 lines)
.github/prompts/CORTEX.prompt.md (50 lines, -200 lines)
.github/copilot-instructions.md (50 lines, -100 lines)
backups/prompt-migration-v5.3.0/
  ├── CORTEX.prompt.md.v5.2.0.backup (250 lines)
  └── copilot-instructions.md.v5.0.0.backup (150 lines)
reports/lean-prompt-migration-report.md
```

---

## 🧪 Validation Criteria

### Unit Tests
- ✅ `test_request_transformer.py`: 20+ test cases for parsing/transformation
- ✅ `test_master_orchestrator_yaml.py`: Validate YAML schema

### Integration Tests
- ✅ `python3 -m src.main 'plan user-auth'` → Correct CLI command generated
- ✅ `python3 -m src.main 'ado story login'` → Correct ADO command
- ✅ Meta-directives: `'plan [concise] dashboard'` → `mode=concise` passed

### Acceptance Criteria
- ✅ CORTEX.prompt.md ≤50 lines
- ✅ copilot-instructions.md ≤50 lines
- ✅ All 12+ orchestrator routing patterns work
- ✅ Meta-directive extraction 100% accurate
- ✅ Transformation logic has 95%+ test coverage

---

## 📚 References

- **Proposal Document:** `cortex-brain/documents/architecture/lean-prompt-proposal-v5.3.0.md` (12KB)
- **C150 Plan:** `cortex-brain/documents/planning/active/c150-remediation-plan/00-c150-remediation-plan.yaml` (Phase 26)
- **Gap Definition:** `GAP-ARCH-4: Prompt File Logic Duplication & Drift`
- **POC Validation:** `cortex-brain/documents/planning/active/poc-python-execution/reports/poc-success-summary.md`

---

## 🎯 Next Steps

**Priority Order:**
1. **Phase 23 (CRITICAL):** Fix Python CLI import chain (blocks all execution)
2. **Phase 24 (HIGH):** Fix PlanningStateDB signatures (blocks Planning v5)
3. **Phase 26 (MEDIUM):** Implement Lean Prompt Architecture (optimization)

**Recommendation:** Fix Phases 23-24 first to reach 95% production readiness, then implement Phase 26 for long-term maintainability.

---

**Status:** ✅ PROPOSED (documented in C150 plan)  
**Estimated Hours:** 8.0 hours  
**Total C150 Hours:** 169 hours (updated from 161)
