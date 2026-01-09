# CORTEX AC Enhancement Proposals

**Generated:** 2026-01-09T10:40:00Z  
**Source:** cortex-search analysis of AC v7.2.0  
**Total Proposals:** 12 new AC entries

---

## 🔴 CRITICAL: Missing Orchestrator Test Harnesses

These orchestrators are referenced in `copilot-instructions.md` routing but have no formal AC criteria:

### AC-ORC-EPIC-001 to AC-ORC-EPIC-003 (Epic Review)

```yaml
AC-ORC-EPIC-001:
  id: AC-ORC-EPIC-001
  criterion: "Epic Review generates visual progress bars and health metrics"
  acceptance:
    - "ASCII progress bars (WCAG AA compliant)"
    - "Health score calculation (0-100)"
    - "Component usage tracking (active vs inactive)"
    - "Gap detection with recommendations"
  validation: automated
  test_file: "tests/orchestrators/epic_review/test_progress_visualization.py"
  status: PENDING
  blocking: true
  priority: P0_CRITICAL

AC-ORC-EPIC-002:
  id: AC-ORC-EPIC-002
  criterion: "Epic Review performs self-healing evaluation"
  acceptance:
    - "Audit log review (last 7 days)"
    - "TDD enforcement validation"
    - "Governance compliance check"
    - "Automatic epic updates for gaps"
  validation: automated
  test_file: "tests/orchestrators/epic_review/test_self_healing.py"
  status: PENDING
  blocking: false
  priority: P1_HIGH

AC-ORC-EPIC-003:
  id: AC-ORC-EPIC-003
  criterion: "Epic Review identifies and categorizes gaps"
  acceptance:
    - "Missing feature detection"
    - "Test coverage gaps"
    - "Security vulnerability identification"
    - "Performance bottleneck detection"
  validation: automated
  test_file: "tests/orchestrators/epic_review/test_gap_detection.py"
  status: PENDING
  blocking: false
  priority: P1_HIGH
```

### AC-ORC-SAN-001 to AC-ORC-SAN-003 (Sanitization)

```yaml
AC-ORC-SAN-001:
  id: AC-ORC-SAN-001
  criterion: "Sanitization detects and removes PII"
  acceptance:
    - "Email detection and replacement"
    - "Phone number detection"
    - "Name detection (NER-based)"
    - "Address detection"
    - "Mapping file preserved for reversibility"
  validation: automated
  test_file: "tests/orchestrators/sanitization/test_pii_removal.py"
  status: PENDING
  blocking: true
  priority: P0_CRITICAL

AC-ORC-SAN-002:
  id: AC-ORC-SAN-002
  criterion: "Sanitization detects and removes secrets"
  acceptance:
    - "API key detection (regex patterns)"
    - "Connection string detection"
    - "Password detection"
    - "JWT token detection"
    - "Git credential detection"
  validation: automated
  test_file: "tests/orchestrators/sanitization/test_secret_removal.py"
  status: PENDING
  blocking: true
  priority: P0_CRITICAL

AC-ORC-SAN-003:
  id: AC-ORC-SAN-003
  criterion: "Sanitization produces reversible mappings"
  acceptance:
    - "Mapping file: sanitization-mappings.json"
    - "Reversible: original value recoverable"
    - "Consistent: same input → same replacement"
    - "Secure: mappings stored separately from sanitized data"
  validation: automated
  test_file: "tests/orchestrators/sanitization/test_mapping_reversibility.py"
  status: PENDING
  blocking: false
  priority: P1_HIGH
```

### AC-ORC-VAC-001 to AC-ORC-VAC-002 (Vacuum)

```yaml
AC-ORC-VAC-001:
  id: AC-ORC-VAC-001
  criterion: "Vacuum performs deep filesystem cleanup"
  acceptance:
    - "Orphaned file detection"
    - "Duplicate file detection"
    - "Obsolete cache removal"
    - "Empty directory cleanup"
  validation: automated
  test_file: "tests/orchestrators/vacuum/test_deep_cleanup.py"
  status: PENDING
  blocking: false
  priority: P1_HIGH

AC-ORC-VAC-002:
  id: AC-ORC-VAC-002
  criterion: "Vacuum supports dry-run with impact report"
  acceptance:
    - "Dry-run mode (no modifications)"
    - "Impact report generation"
    - "Space savings calculation"
    - "Risk assessment per file"
  validation: automated
  test_file: "tests/orchestrators/vacuum/test_dry_run.py"
  status: PENDING
  blocking: false
  priority: P2_MEDIUM
```

### AC-ORC-INV-001 to AC-ORC-INV-002 (Investigation)

```yaml
AC-ORC-INV-001:
  id: AC-ORC-INV-001
  criterion: "Investigation performs root cause analysis"
  acceptance:
    - "Error trace analysis"
    - "Dependency chain tracing"
    - "Timeline reconstruction"
    - "Evidence chain documentation"
  validation: automated
  test_file: "tests/orchestrators/investigation/test_root_cause.py"
  status: PENDING
  blocking: false
  priority: P1_HIGH

AC-ORC-INV-002:
  id: AC-ORC-INV-002
  criterion: "Investigation generates actionable report"
  acceptance:
    - "Executive summary"
    - "Root cause identification"
    - "Remediation recommendations"
    - "Prevention measures"
  validation: automated
  test_file: "tests/orchestrators/investigation/test_report_generation.py"
  status: PENDING
  blocking: false
  priority: P2_MEDIUM
```

---

## 🟠 HIGH: Agent Criteria

### AC-AGENT-001 to AC-AGENT-002 (LLM Intent Classifier)

```yaml
AC-AGENT-001:
  id: AC-AGENT-001
  criterion: "LLMIntentClassifier routes with ≥95% accuracy"
  acceptance:
    - "Test: 100 sample intents → ≥95 correct routes"
    - "Ambiguous intents resolved via confidence scoring"
    - "Unknown intents routed to fallback handler"
  validation: automated
  test_file: "tests/agents/test_intent_classifier_accuracy.py"
  status: PENDING
  blocking: false
  priority: P1_HIGH

AC-AGENT-002:
  id: AC-AGENT-002
  criterion: "LLMIntentClassifier falls back to regex on failure"
  acceptance:
    - "LLM timeout → regex fallback"
    - "LLM error → regex fallback"
    - "Fallback logged to audit"
    - "No user-visible degradation"
  validation: automated
  test_file: "tests/agents/test_intent_classifier_fallback.py"
  status: PENDING
  blocking: false
  priority: P2_MEDIUM
```

---

## 🟡 MEDIUM: Structural Enhancements

### Test Organization Clarification

**Proposed Update to AC-TEST-ORG-001:**

```yaml
AC-TEST-ORG-001:
  id: AC-TEST-ORG-001
  criterion: "All tests organized in single tests/ folder with logical subfolders"
  acceptance:
    - "All unit tests: tests/unit/"
    - "All integration tests: tests/integration/"
    - "Orchestrator-specific tests: tests/{unit,integration}/orchestrators/{name}/"
    - "No scattered test files outside tests/"
    - "Test file naming: test_*.py or *_test.py"
  validation: automated
  test_file: "tests/test_organization/test_folder_structure.py"
  status: PENDING
  blocking: true
  priority: P0_CRITICAL
  
  # NOTE: Updated to allow orchestrator subfolders for organization
  rationale: "Orchestrator subfolders improve test discoverability while maintaining single tests/ root"
```

---

## 📊 Impact Summary

| Category | New ACs | Priority | Effort |
|----------|---------|----------|--------|
| Epic Review | 3 | P0/P1 | 3h |
| Sanitization | 3 | P0/P1 | 3h |
| Vacuum | 2 | P1/P2 | 2h |
| Investigation | 2 | P1/P2 | 2h |
| Agents | 2 | P1/P2 | 2h |
| Test Organization | 1 (update) | P0 | 30m |
| **TOTAL** | **13** | - | **12h 30m** |

---

## 🚀 Recommended Actions

1. **Immediate:** Add AC-ORC-EPIC-* and AC-ORC-SAN-* (blocking)
2. **High Priority:** Add AC-ORC-VAC-*, AC-ORC-INV-*, AC-AGENT-*
3. **Structural:** Update AC-TEST-ORG-001 to clarify subfolder policy

---

**Report Generated:** 2026-01-09T10:40:00Z  
**Report Location:** `cortex-brain/analysis/ac-enhancements-2026-01-09.md`  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
