# Test File Creation Fix - Root Directory Protection

## Issue Summary
Some tests were creating folders and files in the project root directory instead of using temporary directories provided by pytest's `tmp_path` fixture.

## Root Cause Analysis
Tests that create files/directories without using `tmp_path` can pollute the project root with:
- Temporary test directories (e.g., `tier3/`)
- Sample code files
- Test fixtures that persist after test execution

## Files Fixed

### 1. tests/unit/orchestrators/test_absorption_gate.py
**Issue:** Used hardcoded path `Path("tier3/learned-patterns.yaml")` which could create `tier3` directory in root.

**Fix:** Updated `test_absorb_writes_to_tier3` to use `tmp_path` fixture:
```python
# Before
def test_absorb_writes_to_tier3(self):
    tier3_path = Path("tier3/learned-patterns.yaml")
    gate = AbsorptionGate(min_sightings=3, min_confidence=0.7, tier3_path=tier3_path)

# After
def test_absorb_writes_to_tier3(self, tmp_path):
    tier3_path = tmp_path / "tier3" / "learned-patterns.yaml"
    gate = AbsorptionGate(min_sightings=3, min_confidence=0.7, tier3_path=tier3_path)
```

**Result:** Test now creates files in temporary directory that is automatically cleaned up by pytest.

### 2. tests/unit/infrastructure/test_environment_setup.py
**Issue:** Three tests created sample code files in `PROJECT_ROOT / "tests" / "fixtures"` directory.

**Tests Fixed:**
- `test_black_format_validation`
- `test_isort_check_validation`
- `test_mypy_type_check_validation`

**Fix:** Updated all three tests to use `tmp_path` fixture:
```python
# Before
def test_black_format_validation(self) -> None:
    sample_code = Path(PROJECT_ROOT) / "tests" / "fixtures" / "sample_code.py"
    sample_code.parent.mkdir(parents=True, exist_ok=True)
    sample_code.write_text("x=1+2\n")
    try:
        # ... test code ...
    finally:
        sample_code.unlink(missing_ok=True)

# After
def test_black_format_validation(self, tmp_path: Path) -> None:
    sample_code = tmp_path / "sample_code.py"
    sample_code.write_text("x=1+2\n")
    try:
        # ... test code ...
    # No cleanup needed - tmp_path auto-cleaned
```

**Benefits:**
- No need for manual cleanup with `unlink(missing_ok=True)`
- No pollution of `tests/fixtures` directory
- Tests are more isolated and can run in parallel safely

## Verification

### Tests Still Pass
All fixed tests have been verified to pass:
```bash
# Absorption gate tests
pytest tests/unit/orchestrators/test_absorption_gate.py -xvs
# Result: 11 passed in 0.11s ✅

# Environment setup tests
pytest tests/unit/infrastructure/test_environment_setup.py::TestDevelopmentToolsConfiguration -v
# Result: Tests pass or skip if tools not available ✅
```

### No Root Pollution
Verified that running unit tests does not create files/directories in root:
```bash
# Count before: 19 files/dirs
ls -1 | wc -l
# Run tests
pytest tests/unit/ --ignore=tests/unit/tier1 -q
# Count after: 19 files/dirs (unchanged) ✅
```

## Best Practices for Test File Creation

### ✅ DO: Use tmp_path fixture
```python
def test_something(tmp_path: Path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    # Automatically cleaned up
```

### ❌ DON'T: Create files with relative paths
```python
def test_something():
    test_file = Path("test.txt")  # Creates in project root!
    test_file.write_text("content")
```

### ❌ DON'T: Use PROJECT_ROOT for test files
```python
def test_something():
    test_file = Path(PROJECT_ROOT) / "test.txt"  # Pollutes project!
    test_file.write_text("content")
```

### ✅ DO: Use fixtures directory for permanent fixtures
```python
# Only for fixtures that should be committed to git
@pytest.fixture
def sample_yaml():
    return Path(__file__).parent / "fixtures" / "sample.yaml"
```

## Impact Assessment

### Before Fix
- `tier3/` directory could be created in project root
- `tests/fixtures/sample_code.py` file would be created and deleted repeatedly
- Potential for test pollution and race conditions

### After Fix
- All test files created in isolated temporary directories
- Automatic cleanup by pytest
- Better test isolation and parallelization support
- No manual cleanup code needed

## Related Governance

- **CORE-008 (TDD)**: Tests properly isolated, can be run repeatedly
- **CORE-013 (No side effects)**: Tests no longer create persistent files
- **Test Hygiene**: Follows pytest best practices for file creation

## Recommendations

1. **Audit all tests**: Run periodic checks for tests creating files without `tmp_path`
2. **Pre-commit hook**: Consider adding a check for `Path(...).mkdir()` without `tmp_path` in test files
3. **Documentation**: Add to contributor guidelines about proper test file creation
4. **CI/CD**: Consider adding a check that fails if new files/directories appear in root after test runs

## Audit Query
To find similar issues in the future:
```bash
# Find tests that might create files without tmp_path
grep -r "\.mkdir\|write_text\|write_bytes\|\.touch" tests/ \
  | grep -v "tmp_path\|fixtures" \
  | grep "def test_"
```

---
**Date:** 2026-02-17  
**Phase:** Maintenance - Test Quality Improvement  
**Status:** ✅ Resolved  
**Files Modified:** 2  
**Tests Fixed:** 4  
