# Orchestrator Unwiring Fix — Permanent Solution

## Summary

This document captures the permanent fixes applied to resolve orchestrator unwiring issues
in the CORTEX system — broken imports, missing modules, and stub implementations that
prevented the MCP pipeline from functioning correctly.

## Fix References

### AC-PERMANENT-FIX-001: MCP Import Path Correction

**Problem:** `cortex/mcp/tools/core.py` had incorrect import paths for TDD, Refactoring,
and LENS orchestrators, causing `ModuleNotFoundError` at runtime.

**Fix:** Corrected all three import paths to point to the actual module locations:
- `cortex.orchestrators.core.tdd_orchestrator.TDDOrchestrator`
- `cortex.orchestrators.domain.refactoring_orchestrator.RefactoringOrchestrator`
- `cortex.lens.analyzers.lens_orchestrator.LENSOrchestrator`

### AC-PERMANENT-FIX-002: Governance Registry Real Implementation

**Problem:** `cortex/orchestrators/core/governance_registry.py` was a stub that always
returned `passed: True`, providing no actual governance enforcement.

**Fix:** Implemented real gate checking with:
- Tier 0 CORE rule loading from YAML (35 rules from `core-rules.yaml`)
- `registry_template` pattern with singleton, auto-initialization, and fallback rules
- `check_gate()` evaluates registered rules against operation specifications
- `get_all_rules()` returns rules grouped by tier for the rule evaluator
- `_operation_satisfies_rule()` checks CORE-008 (TDD), CORE-011 (types), CORE-013 (exceptions)

### AC-PERMANENT-FIX-003: Rule Evaluator Context Extraction

**Problem:** `cortex/brain/core/rule_evaluator.py` called `self.context_extractor.extract_context()`
which did not exist, causing `AttributeError` at runtime.

**Fix:** Replaced external dependency with inline validators:
- 5 built-in CORE rule validators (CORE-001, 008, 011, 012, 013)
- File-based applicability checks (test files exempt from tier 2 rules)
- Generic fallback for unknown rules using violation flags
- Tier-priority evaluation (tier 0 blocking)

## Verification

All fixes verified via:
- 856 passing tests (brain/core + orchestrators)
- Import smoke tests for all 11 orchestrators
- Runtime rule evaluation tests (violations correctly detected)
