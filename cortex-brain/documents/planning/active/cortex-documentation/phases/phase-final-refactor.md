# Final Phase: REFACTOR & Cleanup

**Duration:** TBD  
**Status:** ⏸️ Not Started  
**Purpose:** Comprehensive cleanup to prevent technical debt

---

## 🎯 Objectives

1. Detect and remove orphaned code
2. Eliminate duplicate code patterns
3. Complete ≥18 cleanup tasks per file category
4. Ensure SKULL rule compliance

---

## 🔍 Orphaned Code Detection

### Detection Methods
- AST analysis for unused imports
- Dead code analysis (unreachable functions)
- Unused variable detection
- Orphaned test files

### Tool
```bash
python src/operations/utilities/orphan_detector.py   --scan-dir src/orchestrators/{feature}/   --output context/orphaned-code-report.json
```

---

## 🔁 Duplicate Code Removal

### Detection
- Copy-paste pattern matching
- Similar function signature analysis
- Redundant logic identification

### Consolidation Strategy
- Extract to shared utilities
- Create base classes for common patterns
- Implement mixins for cross-cutting concerns

---

## 📋 Cleanup Tasks (≥18 per category)

### Test Files
- [ ] Remove commented-out tests
- [ ] Consolidate duplicate fixtures
- [ ] Update outdated docstrings
- [ ] Fix flaky tests
- [ ] Add missing assertions
- [ ] Improve test naming
- [ ] (12 more tasks)

### Implementation Files
- [ ] Remove unused imports
- [ ] Eliminate dead code
- [ ] Consolidate duplicate logic
- [ ] Update type hints
- [ ] Fix linting warnings
- [ ] Improve error messages
- [ ] (12 more tasks)

### Configuration Files
- [ ] Remove obsolete configs
- [ ] Validate YAML syntax
- [ ] Update documentation links
- [ ] Consolidate duplicates
- [ ] Add missing defaults
- [ ] Improve comments
- [ ] (12 more tasks)

---

## 🛡️ SKULL Rule Enforcement

### Rules to Validate
1. **REFACTOR_CLEANUP** - Whole-file cleanup completed
2. **TDD_ENFORCEMENT** - All tests still passing
3. **HOLISTIC_DISCOVERY** - No new duplication introduced

### Validation
```bash
pytest tests/ -v --cov=src --cov-report=html
python scripts/validate_cleanup.py --plan {plan_name}
```

---

## 📊 Success Criteria

- ✅ Zero orphaned code remaining
- ✅ <5% code duplication (via radon cc)
- ✅ ≥18 cleanup tasks per file category completed
- ✅ 100% test coverage maintained
- ✅ All SKULL rules passing
- ✅ Git checkpoint created

---

## 📝 Deliverables

1. `context/orphaned-code-report.json` - Detection results
2. `context/duplicate-code-analysis.md` - Consolidation summary
3. `reports/cleanup-completion-report.md` - Task completion log
4. Updated codebase with all cleanup applied
5. Git checkpoint: `checkpoint-final-refactor-complete`
