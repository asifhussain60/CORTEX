# Phase 24: External Refactoring Tools Integration

**Version:** 1.0  
**Status:** IN PROGRESS (Subtask 1.1 Complete)  
**Authority:** Phase 24 Specification (cortex-registry/_cortex-master/phases/active/)  
**Updated:** 2026-02-07

---

## 📋 Overview

Phase 24 integrates external semantic refactoring tools (Rope, Roslyn, TypeScript LS, Java LSP) to provide type-safe, compiler-validated refactoring operations across Python, C#, TypeScript/JavaScript, and Java.

### Business Value
- 📈 **Refactoring operations:** 15 → 100+ semantic operations
- 🏢 **Enterprise adoption:** 40% → 95% (polyglot support)
- ✅ **Type safety:** Compiler-validated for C# and TypeScript
- ⚡ **Execution speed:** 10x faster than manual refactoring
- 🚀 **Team velocity:** +30% improvement

---

## 🎯 Phase Structure (8 weeks)

### Phase 1: Foundation + Python Rope (Days 1-10) ✅ IN PROGRESS
- ✅ **Subtask 1.1:** Base adapter interface + registry (Complete)
- ⚪ **Subtask 1.2:** Rope adapter + core operations
- ⚪ **Subtask 1.3:** Error handling + graceful degradation
- ⚪ **Subtask 1.4:** Integration tests + documentation

### Phase 2: C# Roslyn (Days 11-20)
- ⚪ **Subtask 2.1:** Roslyn process manager + adapter
- ⚪ **Subtask 2.2:** Type-safe operations
- ⚪ **Subtask 2.3:** Performance optimization
- ⚪ **Subtask 2.4:** Integration + tests

### Phase 3: TypeScript/JS + Java Foundation (Days 21-30)
- ⚪ **Subtask 3.1:** TypeScript LS adapter
- ⚪ **Subtask 3.2:** Java LSP foundation
- ⚪ **Subtask 3.3:** Cross-language tests
- ⚪ **Subtask 3.4:** Documentation

### Phase 4: Orchestration + MCP (Days 31-40)
- ⚪ **Subtask 4.1:** Orchestrator integration
- ⚪ **Subtask 4.2:** MCP tool exposure
- ⚪ **Subtask 4.3:** E2E tests + performance
- ⚪ **Subtask 4.4:** Final documentation + dashboard

---

## ✅ Subtask 1.1: Base Adapter Interface + Registry

**Status:** 🟢 COMPLETE  
**Completed:** 2026-02-07  
**Tests:** 13/13 passing  
**Coverage:** 100% (interface + registry)

### Architecture

```
cortex/refactoring/
├── __init__.py              # Package exports
├── models.py                # Data models (Language, Request, Result)
├── registry.py              # RefactoringToolRegistry
└── adapters/
    ├── __init__.py
    └── base.py              # RefactoringToolAdapter (ABC)
```

### Key Components

#### 1. RefactoringToolAdapter (ABC)
Abstract base class defining the contract for all refactoring tool integrations.

**Abstract Methods:**
- `get_supported_operations() -> List[str]`: List available refactoring operations
- `get_language() -> RefactoringLanguage`: Return handled programming language
- `is_available() -> bool`: Check if external tool is installed/accessible
- `execute_refactoring(request) -> Union[Ok[RefactoringResult], Err]`: Execute refactoring
- `validate_request(request) -> Union[Ok[None], Err]`: Validate request before execution

**Design Principles:**
- Graceful degradation when tools unavailable
- Type-safe operations leveraging external tool capabilities
- Performance optimization (lazy init, process pooling)
- Full audit logging (CORE-027)

#### 2. RefactoringToolRegistry
Centralized registry for managing and discovering adapters.

**Features:**
- Language-based adapter routing
- Duplicate registration prevention (CORE-035)
- Availability checking
- Supported operations discovery
- Thread-safe operations

**Key Methods:**
```python
registry = RefactoringToolRegistry()
registry.register(adapter)  # Register adapter
adapter = registry.get_adapter(RefactoringLanguage.PYTHON).unwrap()
operations = registry.get_operations_for_language(language).unwrap()
languages = registry.get_supported_languages()
available = registry.get_available_languages()
```

#### 3. Data Models

**RefactoringLanguage (Enum):**
```python
PYTHON = "python"
CSHARP = "csharp"
TYPESCRIPT = "typescript"
JAVASCRIPT = "javascript"
JAVA = "java"
```

**RefactoringRequest:**
```python
@dataclass
class RefactoringRequest:
    operation: str                    # e.g., "extract_method"
    file_path: Path                   # File to refactor
    language: RefactoringLanguage     # Programming language
    parameters: Dict[str, Any]        # Operation-specific params
```

**RefactoringResult:**
```python
@dataclass
class RefactoringResult:
    success: bool                     # Success status
    modified_files: List[Path]        # Files changed
    description: str                  # Human-readable description
    warnings: List[str]               # Warnings generated
    errors: List[str]                 # Errors encountered
    metadata: Dict[str, Any]          # Tool-specific metadata
```

### Test Coverage

**13 tests covering:**
1. ✅ Adapter interface contract validation
2. ✅ Abstract class instantiation prevention
3. ✅ Required properties (language, operations)
4. ✅ Graceful unavailability handling
5. ✅ Registry initialization
6. ✅ Adapter registration
7. ✅ Language-based retrieval
8. ✅ Missing adapter handling
9. ✅ Duplicate detection (CORE-035)
10. ✅ Language listing
11. ✅ Enum validation
12. ✅ Request model validation
13. ✅ Result model validation

### Governance Compliance

| Rule | Status | Evidence |
|------|--------|----------|
| CORE-008 | ✅ | TDD-first: tests created before implementation |
| CORE-011 | ✅ | Full type hints on all methods |
| CORE-012 | ✅ | Google-style docstrings throughout |
| CORE-027 | ✅ | AC markers in all files |
| CORE-035 | ✅ | Duplicate registration detection in registry |

### Files Created
- `cortex/refactoring/__init__.py` (27 lines)
- `cortex/refactoring/models.py` (89 lines)
- `cortex/refactoring/adapters/__init__.py` (11 lines)
- `cortex/refactoring/adapters/base.py` (131 lines)
- `cortex/refactoring/registry.py` (159 lines)
- `tests/unit/refactoring/test_refactoring_tool_adapter.py` (343 lines)

**Total:** 760 lines (417 implementation, 343 test)

---

## 🚀 Next Steps

### Immediate: Subtask 1.2 - Rope Adapter Implementation

**Estimated:** 3 days  
**Tests:** 25+ tests  
**Deliverables:**
- RopeAdapter class implementing RefactoringToolAdapter
- Python semantic refactoring operations:
  - extract_method
  - rename
  - inline
  - encapsulate_field
  - move_method
  - change_signature
- Rope-specific error handling
- Performance optimization (lazy Rope project initialization)

**Technical Approach:**
1. Create `cortex/refactoring/adapters/rope_adapter.py`
2. Implement lazy Rope project loading
3. Map CORTEX operations to Rope refactorings
4. Handle Rope exceptions gracefully
5. Generate detailed RefactoringResult
6. Add comprehensive tests (success, failure, edge cases)

---

## 📊 Progress Tracking

| Metric | Target | Current | Progress |
|--------|--------|---------|----------|
| **Subtasks Complete** | 16 | 1 | 6% |
| **Tests Passing** | 1,145 | 13 | 1% |
| **Lines of Code** | 2,330 | 417 | 18% |
| **Test Lines** | 1,060 | 343 | 32% |
| **Languages Supported** | 4 | 0 | 0% |
| **Refactoring Operations** | 100+ | 0 | 0% |

---

## 🔒 Quality Gates

**Phase 1 Exit Criteria:**
- [ ] All Rope operations implemented (6 operations)
- [ ] 85%+ test coverage for Rope adapter
- [ ] Performance: Rope startup < 2s, execution < 2s
- [ ] Graceful degradation when Rope unavailable
- [ ] Full audit logging
- [ ] Zero CORE rule violations
- [ ] Integration tests passing

---

## 📚 References

- **Phase Specification:** `cortex-registry/_cortex-master/phases/active/phase-24-external-refactoring-tools.yaml`
- **CORTEX Instructions:** `.github/copilot-instructions.md`
- **Architect Prompt:** `.github/prompts/cortex-architect.prompt.md`
- **Rope Documentation:** https://github.com/python-rope/rope
- **Roslyn API:** https://github.com/dotnet/roslyn
- **TypeScript LS:** https://github.com/typescript-language-server/typescript-language-server

---

**Last Updated:** 2026-02-07  
**Document Version:** 1.0  
**Audit Code:** AC-PHASE24.1.1-DOC-001 ✅
