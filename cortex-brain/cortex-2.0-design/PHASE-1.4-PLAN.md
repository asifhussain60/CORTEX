# Phase 1.4: Agent Modularization Plan

**Created:** 2025-11-08  
**Updated:** 2025-01-15  
**Status:** IN PROGRESS (40% Complete - 2/5 agents)  
**Goal:** Refactor 5 monolithic agent files into SOLID-compliant modular structure

## Progress Summary

✅ **ErrorCorrector** - COMPLETE (702 lines → 18 modules)  
✅ **HealthValidator** - COMPLETE (660 lines → 11 modules)  
⏭️ CodeExecutor - PENDING (639 lines)  
⏭️ TestGenerator - PENDING (622 lines)  
⏭️ WorkPlanner - PENDING (617 lines)

---

## Overview

### Target Files
1. **error_corrector.py** - 702 lines
2. **health_validator.py** - 659 lines  
3. **code_executor.py** - 639 lines
4. **test_generator.py** - 622 lines
5. **work_planner.py** - 617 lines

**Total:** 3,239 lines → ~25-30 modules (<200 lines each)

### Success Criteria
- ✅ All files <500 lines (target: <200 lines per module)
- ✅ Zero circular dependencies
- ✅ All existing tests passing
- ✅ Test coverage ≥85% (add 60+ new tests)
- ✅ Performance maintained
- ✅ No breaking changes in public APIs

---

## 1. ErrorCorrector Analysis (702 lines)

### Current Structure
```python
class ErrorCorrector(BaseAgent):
    - __init__
    - can_handle
    - execute
    - _is_protected_path
    - _parse_error                    # Router to specific parsers
    - _parse_pytest_error            # 35 lines
    - _parse_syntax_error            # 33 lines
    - _parse_import_error            # 24 lines
    - _parse_runtime_error           # 47 lines
    - _parse_linter_error            # 23 lines
    - _find_fix_patterns             # 30 lines
    - _get_builtin_patterns          # 80 lines (large switch)
    - _apply_fix                     # 65 lines
    - _fix_indentation               # 36 lines
    - _suggest_package_install       # 11 lines
    - _suggest_import                # 28 lines
    - _suggest_remove_import         # 17 lines
    - _check_missing_colons          # 37 lines
```

### Proposed Modular Structure

```
src/cortex_agents/error_corrector/
├── __init__.py                      # Export ErrorCorrector
├── agent.py                         # Main coordinator (120 lines)
│   └── ErrorCorrector class
│       - can_handle()
│       - execute()
│       - _is_protected_path()
│       - _find_fix_patterns()
│       - _apply_fix()
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py               # Abstract base (30 lines)
│   ├── pytest_parser.py             # Parse pytest errors (50 lines)
│   ├── syntax_parser.py             # Parse syntax errors (50 lines)
│   ├── import_parser.py             # Parse import errors (45 lines)
│   ├── runtime_parser.py            # Parse runtime errors (60 lines)
│   └── linter_parser.py             # Parse linter errors (40 lines)
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py             # Abstract base (25 lines)
│   ├── indentation_strategy.py      # Fix indentation (50 lines)
│   ├── import_strategy.py           # Add/remove imports (60 lines)
│   ├── syntax_strategy.py           # Fix syntax errors (50 lines)
│   └── package_strategy.py          # Suggest packages (30 lines)
└── validators/
    ├── __init__.py
    ├── path_validator.py            # Protected path checks (40 lines)
    └── fix_validator.py             # Validate fixes (40 lines)
```

**Total Modules:** 15 files  
**Largest Module:** agent.py (120 lines)  
**Tests to Add:** 12 unit tests

---

## 2. HealthValidator Analysis (659 lines)

### Current Structure
- Large validation orchestrator
- Multiple validation strategies embedded
- Report generation mixed in

### Proposed Modular Structure

```
src/cortex_agents/health_validator/
├── __init__.py
├── agent.py                         # Main coordinator (150 lines)
├── validators/
│   ├── __init__.py
│   ├── base_validator.py            # Abstract base (30 lines)
│   ├── test_validator.py            # Test health checks (120 lines)
│   ├── build_validator.py           # Build health checks (100 lines)
│   ├── code_quality_validator.py    # Quality metrics (110 lines)
│   └── performance_validator.py     # Performance checks (100 lines)
└── reporting/
    ├── __init__.py
    └── report_generator.py          # Health reports (80 lines)
```

**Total Modules:** 9 files  
**Largest Module:** agent.py (150 lines)  
**Tests to Add:** 12 unit tests

---

## 3. CodeExecutor Analysis (639 lines)

### Current Structure
- Multiple execution strategies (shell, python, node)
- Result formatting embedded
- Error handling duplicated

### Proposed Modular Structure

```
src/cortex_agents/code_executor/
├── __init__.py
├── agent.py                         # Main coordinator (120 lines)
├── executors/
│   ├── __init__.py
│   ├── base_executor.py             # Abstract base (40 lines)
│   ├── shell_executor.py            # Shell commands (100 lines)
│   ├── python_executor.py           # Python code (120 lines)
│   ├── node_executor.py             # Node.js code (100 lines)
│   └── script_executor.py           # Script files (90 lines)
├── handlers/
│   ├── __init__.py
│   ├── result_handler.py            # Process results (70 lines)
│   └── error_handler.py             # Handle errors (60 lines)
└── validators/
    ├── __init__.py
    └── code_validator.py            # Validate code safety (50 lines)
```

**Total Modules:** 12 files  
**Largest Module:** python_executor.py (120 lines)  
**Tests to Add:** 12 unit tests

---

## 4. TestGenerator Analysis (622 lines)

### Current Structure
- Code analysis mixed with template generation
- Multiple test framework strategies
- Template management embedded

### Proposed Modular Structure

```
src/cortex_agents/test_generator/
├── __init__.py
├── agent.py                         # Main coordinator (120 lines)
├── analyzers/
│   ├── __init__.py
│   ├── code_analyzer.py             # Analyze code structure (140 lines)
│   ├── function_analyzer.py         # Analyze functions (80 lines)
│   └── class_analyzer.py            # Analyze classes (80 lines)
├── generators/
│   ├── __init__.py
│   ├── base_generator.py            # Abstract base (40 lines)
│   ├── pytest_generator.py          # pytest tests (100 lines)
│   └── unittest_generator.py        # unittest tests (90 lines)
└── templates/
    ├── __init__.py
    └── template_manager.py          # Test templates (80 lines)
```

**Total Modules:** 11 files  
**Largest Module:** code_analyzer.py (140 lines)  
**Tests to Add:** 12 unit tests

---

## 5. WorkPlanner Analysis (617 lines)

### Current Structure
- Planning strategies mixed together
- Task breakdown embedded
- Dependency management inline

### Proposed Modular Structure

```
src/cortex_agents/work_planner/
├── __init__.py
├── agent.py                         # Main coordinator (120 lines)
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py             # Abstract base (30 lines)
│   ├── feature_strategy.py          # Feature planning (100 lines)
│   ├── bug_fix_strategy.py          # Bug fix planning (90 lines)
│   └── refactor_strategy.py         # Refactoring plans (90 lines)
├── breakdown/
│   ├── __init__.py
│   ├── task_breakdown.py            # Break into tasks (100 lines)
│   └── dependency_manager.py        # Task dependencies (80 lines)
└── estimation/
    ├── __init__.py
    └── estimator.py                 # Time estimation (70 lines)
```

**Total Modules:** 11 files  
**Largest Module:** agent.py (120 lines)  
**Tests to Add:** 12 unit tests

---

## Implementation Order

### Week 1 (Days 1-2): ErrorCorrector
1. Create directory structure
2. Extract parsers (pytest, syntax, import, runtime, linter)
3. Extract strategies (indentation, import, syntax, package)
4. Extract validators (path, fix)
5. Create agent.py coordinator
6. Write 12 unit tests
7. Update imports throughout codebase
8. Verify all tests pass

### Week 1 (Days 3-4): HealthValidator & CodeExecutor
1. HealthValidator: Extract validators + reporting
2. Write 12 unit tests for HealthValidator
3. CodeExecutor: Extract executors + handlers + validators
4. Write 12 unit tests for CodeExecutor
5. Update imports
6. Verify all tests pass

### Week 1 (Days 5-6): TestGenerator & WorkPlanner
1. TestGenerator: Extract analyzers + generators + templates
2. Write 12 unit tests for TestGenerator
3. WorkPlanner: Extract strategies + breakdown + estimation
4. Write 12 unit tests for WorkPlanner
5. Update imports
6. Verify all tests pass

### Week 1 (Day 7): Integration & Validation
1. Write 10 integration tests (agent workflows)
2. Run complete test suite (target: 77 + 60 = 137 tests passing)
3. Verify Phase 1.4 success criteria
4. Update documentation
5. Create PHASE-1.4-COMPLETE.md

---

## Testing Strategy

### Unit Tests (60 tests total)
- **ErrorCorrector:** 12 tests
  - Parser tests (5): pytest, syntax, import, runtime, linter
  - Strategy tests (4): indentation, import, syntax, package
  - Validator tests (2): path, fix
  - Integration test (1): full error correction flow

- **HealthValidator:** 12 tests
  - Validator tests (4): test, build, code quality, performance
  - Report generator test (1)
  - Integration tests (7): various health check scenarios

- **CodeExecutor:** 12 tests
  - Executor tests (4): shell, python, node, script
  - Handler tests (2): result, error
  - Validator test (1): code safety
  - Integration tests (5): execution workflows

- **TestGenerator:** 12 tests
  - Analyzer tests (3): code, function, class
  - Generator tests (2): pytest, unittest
  - Template test (1)
  - Integration tests (6): test generation workflows

- **WorkPlanner:** 12 tests
  - Strategy tests (3): feature, bug fix, refactor
  - Breakdown tests (2): task breakdown, dependencies
  - Estimator test (1)
  - Integration tests (6): planning workflows

### Integration Tests (10 tests)
1. Complete error correction workflow (ErrorCorrector)
2. Health check with all validators (HealthValidator)
3. Code execution with error handling (CodeExecutor)
4. Test generation for real code (TestGenerator)
5. Work planning for feature (WorkPlanner)
6. Multi-agent collaboration: WorkPlanner → TestGenerator
7. Multi-agent collaboration: CodeExecutor → ErrorCorrector
8. Multi-agent collaboration: HealthValidator → ErrorCorrector
9. Router integration with all agents
10. Workflow pipeline with all agents

---

## Migration Strategy

### Backward Compatibility
1. Keep original agent.py files as facades initially
2. Deprecate old imports gradually
3. Update all callers incrementally
4. Remove old files after 100% validation

### Import Updates Required
- `src/router.py` - Update agent imports
- `src/workflows/*.py` - Update agent imports
- `tests/agents/*.py` - Update test imports
- Any other modules importing agents

---

## Performance Targets

- Agent initialization: <10ms (no change)
- Error parsing: <5ms per error
- Strategy execution: <50ms per fix
- Test generation: <100ms per file
- Work planning: <200ms per plan
- Health validation: <500ms complete check

---

## Risk Mitigation

### Risks
1. Breaking existing workflows
2. Test failures during migration
3. Circular dependencies
4. Performance regression

### Mitigation
1. Incremental migration with backward compatibility
2. Run tests after every module extraction
3. Careful import management, use dependency injection
4. Benchmark after each agent modularization

---

## Success Metrics

- ✅ All 5 agents modularized
- ✅ All files <200 lines (target), <500 lines (hard limit)
- ✅ 60+ new unit tests passing
- ✅ 10+ integration tests passing
- ✅ All existing tests still passing (77/77 minimum)
- ✅ Zero circular dependencies
- ✅ Test coverage ≥85%
- ✅ Performance maintained or improved
- ✅ No breaking changes

---

**Next Step:** Begin ErrorCorrector modularization (Day 1)
