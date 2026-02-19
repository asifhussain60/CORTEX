# REPHRASE Mode Enforcement Documentation

**Version:** 2.0  
**Updated:** 2026-02-17  
**Authority:** CORTEX REPHRASE MODE + Golden Test Suite  
**Status:** ✅ ENFORCED

---

## Overview

REPHRASE mode is a **text transformation step ONLY** that converts verbose/unclear user requests into clean, single-paragraph prompts optimized for CORTEX MasterOrchestrator consumption.

**Core Principle:** REPHRASE outputs EXACTLY ONE paragraph of plain text (copy-pasteable into new GitHub Copilot Chat session).

---

## Enforcement Rules

### ✅ REQUIRED OUTPUT FORMAT

```
{REFINED_REQUEST_AS_SINGLE_PARAGRAPH_WITH_CORTEX_CONTEXT}
```

**Example:**
```
Implement user authentication for admin panel security via TDDOrchestrator with module-level scope, including JWT token validation, role-based access control, and secure session management following CORTEX governance rules CORE-008 (TDD mandatory) and CORE-011 (type hints required).
```

### ✅ MUST INCLUDE

1. **Action verb** (Implement, Fix, Refactor, Analyze, etc.)
2. **Clear scope** (module, component, system)
3. **CORTEX orchestrator reference** (e.g., "via TDDOrchestrator")
4. **Governance rule references** (e.g., "per CORE-008")
5. **Technical context inline** (not as separate sections)

### ❌ FORBIDDEN IN OUTPUT

1. **Markdown formatting:**
   - NO headers (`#`, `##`, `###`)
   - NO code blocks (`` ``` ``)
   - NO tables (`| col |`)
   - NO bullet lists (`-`, `*`)
   - NO horizontal rules (`---`, `***`)

2. **Multi-paragraph output:**
   - NO double newlines (`\n\n`)
   - NO more than 3 single newlines (sentence breaks OK)

3. **Filler words:**
   - NO "I think", "probably", "maybe", "some kind of"
   - NO "or something", "really", "very", "just"
   - NO contractions ("that's" → "that is")

4. **Metrics/metadata:**
   - NO token reduction percentages
   - NO confidence scores
   - NO before/after comparisons

5. **Challenge protocol:**
   - NO challenge protocol appended (that's for IMPLEMENT mode)

### ❌ FORBIDDEN SIDE EFFECTS

1. **Repository file I/O:**
   - NO reading files (`open()`, `read_file`)
   - NO listing directories (`os.listdir()`, `list_dir`)
   - NO writing/modifying files
   - NO searching codebase

2. **Agent workflow invocation:**
   - NO calling other orchestrators
   - NO triggering execution workflows
   - NO MCP tools other than `cortex_classify`

3. **Fallback for repo context needs:**
   - IF repo context required → return literal token `REQUIRES_REPO_CONTEXT`
   - DO NOT attempt to fetch context autonomously

---

## Golden Test Suite

**Location:** `tests/e2e/test_rephrase_mode_golden.py`

**Coverage:**

| Test ID | Enforcement | Status |
|---------|-------------|--------|
| GT-ENFORCE-001 | Single paragraph output | ✅ |
| GT-ENFORCE-002 | No markdown formatting | ✅ |
| GT-ENFORCE-003 | Filler words removed | ✅ |
| GT-ENFORCE-004 | CORTEX context present | ✅ |
| GT-ENFORCE-005 | Copy-pasteable format | ✅ |
| GT-ENFORCE-006 | No file I/O drift | ✅ |
| GT-ENFORCE-007 | Safe fallback (REQUIRES_REPO_CONTEXT) | ✅ |
| GT-ENFORCE-008 | Mode isolation | ✅ |
| GT-ENFORCE-009 | Idempotency | ✅ |

**Integration Tests:** `tests/integration/test_rephrase_mcp_integration.py`

| Test ID | Integration Point | Status |
|---------|------------------|--------|
| INT-001 | MCP output format | ✅ |
| INT-002 | Filler word removal via MCP | ✅ |
| INT-003 | CORTEX context injection via MCP | ✅ |
| INT-004 | Governance rule injection | ✅ |
| INT-005 | Performance budget (<500ms) | ✅ |
| INT-006 | No file I/O during MCP call | ✅ |

---

## Running Tests

### E2E Golden Tests

```bash
# Run all golden tests
pytest tests/e2e/test_rephrase_mode_golden.py -v

# Run specific enforcement test
pytest tests/e2e/test_rephrase_mode_golden.py::TestRephraseGolden::test_rephrase_output_single_paragraph -v

# Run with coverage
pytest tests/e2e/test_rephrase_mode_golden.py --cov=cortex.rephrase --cov-report=term-missing
```

### Integration Tests (requires MCP)

```bash
# Set MCP enabled flag
export CORTEX_MCP_ENABLED=true

# Run integration tests
pytest tests/integration/test_rephrase_mcp_integration.py -v

# Run specific integration test
pytest tests/integration/test_rephrase_mcp_integration.py::TestRephraseMCPIntegration::test_rephrase_via_mcp_single_paragraph -v
```

### Full Test Suite

```bash
# Run all REPHRASE tests
pytest tests/e2e/test_rephrase_mode_golden.py tests/integration/test_rephrase_mcp_integration.py -v

# Run with markers
pytest -m rephrase -v
```

---

## CI/CD Integration

**GitHub Actions Workflow:** `.github/workflows/test-rephrase-mode.yml`

```yaml
name: REPHRASE Mode Enforcement

on: [push, pull_request]

jobs:
  golden-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run golden tests
        run: pytest tests/e2e/test_rephrase_mode_golden.py -v --tb=short
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: rephrase-test-results
          path: test-results/
```

---

## Troubleshooting

### Issue: Output contains multiple paragraphs

**Symptom:** Test `GT-ENFORCE-001` fails with "Output contains multiple paragraphs"

**Fix:**
1. Check rephrase implementation for `\n\n` insertion
2. Ensure output builder concatenates into single string
3. Strip trailing/leading whitespace before return

### Issue: Markdown headers in output

**Symptom:** Test `GT-ENFORCE-002` fails with "Output contains markdown header"

**Fix:**
1. Remove any `#` header logic from rephrase formatter
2. Use plain text only (no markdown rendering)
3. Validate output with regex: `^#{1,6}\s`

### Issue: REPHRASE attempts file I/O

**Symptom:** Test `GT-ENFORCE-006` fails with "REPHRASE mode attempted file I/O"

**Fix:**
1. Check rephrase implementation for `open()`, `read_file()` calls
2. Return `REQUIRES_REPO_CONTEXT` token instead
3. Let caller (MasterOrchestrator) provide context explicitly

### Issue: Filler words not removed

**Symptom:** Test `GT-ENFORCE-003` fails with "Output contains filler word"

**Fix:**
1. Add filler word regex to cleaning pipeline
2. Use pattern: `r"\b(I think|probably|maybe)\b"`
3. Replace with empty string or better phrasing

---

## SSOT References

**Primary Specs:**
- `.github/prompts/cortex-architect.prompt.md` § REPHRASE MODE
- `.github/agents/core/request-rephrase-orchestrator.md` (full orchestrator spec)

**Enforcement:**
- `tests/e2e/test_rephrase_mode_golden.py` (golden test suite)
- `tests/integration/test_rephrase_mcp_integration.py` (MCP integration)

**Related:**
- `.github/agents/core/CORTEX.md` § `/rephrase` command
- `.github/agents/core/stage-0-governance-audit-spec.md` (pre-rephrase governance)

---

## Change Log

| Date | Version | Change | Authority |
|------|---------|--------|-----------|
| 2026-02-17 | 2.0 | Golden test suite + single-paragraph enforcement | User directive |
| 2026-02-16 | 1.1 | Strict execution constraints (no file I/O) | Drift prevention |
| 2026-02-14 | 1.0 | Initial REPHRASE mode spec | Phase 101 |

---

**Status:** ✅ ENFORCED with golden tests  
**Coverage:** 9/9 enforcement rules validated  
**Integration:** MCP cortex_classify tool  
**CI/CD:** GitHub Actions workflow ready

*Authority: CORTEX REPHRASE MODE + E2E Golden Test Suite*
