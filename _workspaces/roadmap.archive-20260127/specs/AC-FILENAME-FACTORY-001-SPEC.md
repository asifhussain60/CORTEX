# AC-FILENAME-FACTORY-001: Filename Factory Implementation Specification

**Authority:** CORTEX Master Orchestrator | **Version:** 1.0 | **Date:** 2026-01-25 | **Status:** IN PROGRESS

---

## 🎯 Executive Summary

Implements comprehensive filename and file path enforcement system across entire CORTEX codebase. ALL files (user-created and CORTEX-generated) must comply with:

- **CORE-028:** Kebab-case naming, 25-character limit, semantic acronyms
- **CORE-038:** File placement policy (subfolders, no root-level files except whitelist)
- **No exceptions:** Rules apply to `.py`, `.md`, `.yaml`, `.txt`, `.db`, test files, report files, etc.

---

## 📋 Acceptance Criteria

### AC-001: FilenameValidator Implementation
- [ ] Validates kebab-case format (regex pattern)
- [ ] Enforces 25-character limit
- [ ] Recognizes CORE-028 semantic acronym dictionary
- [ ] Returns structured violation list with suggestions
- [ ] All tests passing (TestFilenameValidator)

### AC-002: FilenameFactory Implementation
- [ ] Generates CORE-028 compliant filenames from natural language purpose
- [ ] Intelligently abbreviates to stay within 25-char limit
- [ ] Preserves semantic meaning during abbreviation
- [ ] Supports custom prefixes (e.g., "test-" for test files)
- [ ] All tests passing (TestFilenameFactory)

### AC-003: FilePathEnforcer Implementation
- [ ] Validates CORE-038 file placement policy
- [ ] Enforces subfolder requirement (no root-level files)
- [ ] Maintains whitelist of root-allowed files (README.md, etc.)
- [ ] Validates directory-specific rules (docs/, reports/, cortex/, etc.)
- [ ] All tests passing (TestFilePathEnforcer)

### AC-004: MCP Tool Exposure
- [ ] `suggest-compliant-filename` MCP tool registered
- [ ] `validate-filename` MCP tool registered
- [ ] `validate-filepath` MCP tool registered
- [ ] `suggest-compliant-path` MCP tool registered
- [ ] All tools discoverable via MCP registry
- [ ] Tools return structured JSON with reasoning

### AC-005: Master Orchestrator Integration
- [ ] Add FILE_CREATION intent type to IntentRouter
- [ ] Route FILE_CREATION to FilenameFactory
- [ ] Enforce validation before file write
- [ ] Block non-compliant files with remediation steps
- [ ] Log all decisions to audit trail (CORE-027)

### AC-006: Zero-Exception Enforcement
- [ ] All Python files (.py) must comply
- [ ] All Markdown files (.md) must comply
- [ ] All YAML files (.yaml, .yml) must comply
- [ ] All test files must comply
- [ ] All report files must comply
- [ ] All documentation files must comply
- [ ] Only whitelisted root files allowed

### AC-007: Test Coverage
- [ ] Unit tests for FilenameValidator (11 tests)
- [ ] Unit tests for FilenameFactory (7 tests)
- [ ] Unit tests for FilePathEnforcer (8 tests)
- [ ] Integration tests (3 end-to-end tests)
- [ ] All tests using CORE-008 (TDD) approach
- [ ] Test coverage ≥ 95%

---

## 📁 File Structure

### Core Implementation

```
cortex/governance/
├── filename-factory.py          # Core validation + factory
├── filename-factory-mcp.py      # MCP tool exposure
└── __init__.py                  # Module exports
```

### Test Files

```
tests/unit/governance/
└── test-filename-factory-001.py # All unit + integration tests
```

### Documentation

```
_workspaces/roadmap/specs/
└── ac-filename-factory-001-spec.md  # This spec (in subf older)

docs/guides/
└── core-028-filename-policy.md      # User guide
```

### Reports (when complete)

```
reports/governance/
└── filename-factory-impl-complete.md  # Completion report
```

---

## 🧠 Architecture

### Layer 1: Governance Rules (CORE-028, CORE-038)

Located in: `cortex_brain/tier0/governance/core-rules.yaml`

- CORE-028: Kebab-case, 25-char, semantic acronyms
- CORE-038: File placement policy, subfolder requirements

### Layer 2: Validation (FilenameValidator, FilePathEnforcer)

Located in: `cortex/governance/filename-factory.py`

**FilenameValidator:**
- Pure function, no orchestrator dependency
- Regex-based kebab-case check
- Length validation
- Suggests corrections

**FilePathEnforcer:**
- Validates directory structure compliance
- Enforces subfolder requirements
- Maintains whitelist
- Suggests compliant paths

### Layer 3: Generation (FilenameFactory)

Located in: `cortex/governance/filename-factory.py`

**FilenameFactory:**
- Converts natural language → kebab-case filename
- Intelligently abbreviates using CORE-028 acronyms
- Respects 25-char limit
- Supports test/doc/report prefixes

### Layer 4: MCP Exposure

Located in: `cortex/governance/filename-factory-mcp.py`

**Tools:**
- `suggest-compliant-filename`: Claude-facing suggestion tool
- `validate-filename`: Check filename compliance
- `validate-filepath`: Check path compliance
- `suggest-compliant-path`: Suggest valid path

### Layer 5: Orchestration Integration

**Master Orchestrator Enhancement:**
- Detect FILE_CREATION intent
- Route to FilenameFactory
- Validate result against FilePathEnforcer
- Block non-compliant files
- Log decisions to audit trail

---

## 🔄 Workflow

### User Creates File (Example)

```
1. User: "I need to create a logging analysis utility"
2. Claude: suggest-compliant-filename()
   → "log-ana-util.py" (15 chars)
3. User: "Where should it go?"
4. Claude: suggest-compliant-path()
   → "/cortex/governance/log-ana-util.py"
5. Master Orchestrator:
   ├─ Detect: FILE_CREATION intent
   ├─ Run: FilenameValidator.validate()
   │  → ✅ Valid
   ├─ Run: FilePathEnforcer.validate_path()
   │  → ✅ Valid
   ├─ Allow file write
   └─ Log to audit trail: AC_FILE_CREATED
```

### Invalid File Attempt (Blocked)

```
1. User: "Create cortex_vacuum_executor.py in cortex/"
2. Master Orchestrator:
   ├─ Detect: FILE_CREATION intent
   ├─ Run: FilenameValidator.validate()
   │  → ❌ VIOLATION: Underscores instead of hyphens
   ├─ Run: FilePathEnforcer.validate_path()
   │  → ❌ VIOLATION: Not in subfolder
   ├─ Block file creation
   └─ Return:
      Filename violations: [CORE-028 underscore issue]
      Path violations: [CORE-038 subfolder issue]
      Suggestions: [cortex-vacuum-exec.py, cortex/governance/...]
```

---

## 🛠 Implementation Phases

### Phase 1: Core Modules (Current)
- [x] FilenameValidator class
- [x] FilenameFactory class
- [x] FilePathEnforcer class
- [x] All unit tests (TDD)
- [ ] All tests passing

### Phase 2: MCP Exposure
- [ ] MCP tool decorators
- [ ] Tool registration
- [ ] Tool discoverability
- [ ] Tool integration tests

### Phase 3: Orchestration Integration
- [ ] IntentRouter enhancement (FILE_CREATION)
- [ ] Master Orchestrator routing
- [ ] Pre-write validation hook
- [ ] Audit trail logging

### Phase 4: System-Wide Enforcement
- [ ] Apply to all existing files (migration)
- [ ] Pre-commit hook enforcement
- [ ] CI/CD pipeline checks
- [ ] Governance registry wiring

### Phase 5: Documentation & Migration
- [ ] User guide (CORE-028)
- [ ] Migration plan for existing non-compliant files
- [ ] Remediation scripts
- [ ] Completion report

---

## 📊 CORE Rules Applied

| Rule | Aspect | Implementation |
|------|--------|-----------------|
| CORE-008 | TDD | Tests written first, all tests in test-filename-factory-001.py |
| CORE-011 | Type Hints | All functions have complete type annotations |
| CORE-012 | Docstrings | Google-style docstrings on all classes/methods |
| CORE-013 | Exception Handling | No bare except; specific exception types |
| CORE-024 | MCP Decorator | @mcp_tool on all exposed functions |
| CORE-027 | Audit Logging | All decisions logged to audit trail |
| CORE-028 | Naming | FilenameValidator enforces CORE-028 |
| CORE-038 | Placement | FilePathEnforcer enforces CORE-038 |

---

## ✅ Quality Gates

- [ ] All 29 unit tests passing
- [ ] All 3 integration tests passing
- [ ] Type checking passes (Pylance strict mode)
- [ ] Linting passes (flake8, pylint)
- [ ] Coverage ≥ 95%
- [ ] No governance violations (CORE rules)
- [ ] Audit trail complete
- [ ] Git checkpoint created

---

## 🚀 Success Criteria

1. **NO files** can be created outside of CORE-028/CORE-038 without violation
2. **All existing files** reviewed for compliance (migration plan)
3. **Master Orchestrator** blocks non-compliant file creation
4. **Claude** has 4 MCP tools for filename/path suggestions
5. **Tests** verify complete enforcement across all file types
6. **Zero exceptions:** Rules apply uniformly

---

## 📞 Questions & Clarifications

- When should migration of existing non-compliant files occur?
- Should pre-commit hooks enforce CORE-028/CORE-038?
- How aggressive should Master Orchestrator blocking be?
- Should there be a grace period for legacy files?

---

**Next Steps:** Run tests, verify all pass, then proceed to MCP exposure.
