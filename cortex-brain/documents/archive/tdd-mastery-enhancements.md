# TDD Mastery Enhancements: Test File Validation & Empty Test Detection

**Version:** 1.0  
**Date:** December 7, 2025  
**Rules Added:** TDD_TEST_FILE_VALIDATION, TDD_EMPTY_TEST_DETECTION  
**Author:** Asif Hussain

---

## Overview

Two new Tier 0 instincts added to `brain-protection-rules.yaml` to address critical gaps identified in the Cortex-Clean code quality review:

1. **TDD_TEST_FILE_VALIDATION** - Ensures all production code has corresponding test files
2. **TDD_EMPTY_TEST_DETECTION** - Detects and flags low-quality placeholder tests

---

## Rule 1: TDD_TEST_FILE_VALIDATION

### Purpose

Prevents the gap between CLAIMED test coverage (90%+) and ACTUAL coverage (~15-20%) by enforcing test file existence for all production code.

### Severity

**BLOCKED** - Cannot proceed without test files for production code

### Detection

Scans production code directories and validates corresponding test files exist:

```yaml
Production File Pattern → Required Test File
─────────────────────────────────────────────
*Handler.cs          → Tests/Application/Handlers/*HandlerTests.cs
*Validator.cs        → Tests/Application/Validators/*ValidatorTests.cs
*Repository.cs       → Tests/Infrastructure/Repositories/*RepositoryTests.cs
*Controller.cs       → Tests/API/Controllers/*ControllerTests.cs
*Service.cs          → Tests/Domain/*ServiceTests.cs
*Entity.cs           → Tests/Domain/*EntityTests.cs
```

### Coverage Thresholds by Layer

```
Domain Layer:        90% minimum (entities, services, exceptions)
Application Layer:   85% minimum (handlers, validators, commands, queries)
Infrastructure:      70% minimum (repositories, DbContext)
API Layer:          80% minimum (controllers, middleware, integration tests)
```

### Example: Cortex-Clean Gap Detection

**Before (Actual State):**
```
Domain Layer:        ✅ 90% (TaskEntity, TaskValidationService tested)
Application Layer:   ❌ 0% (NO handler/validator tests)
Infrastructure:      ❌ 0% (NO repository tests)
API Layer:          ❌ 0% (NO controller/integration tests)

CLAIMED: 90%+
ACTUAL: ~15-20%
GAP: 70-75% untested code
```

**After (Required Tests):**
```
Application/Handlers/
  ├── CreateTaskCommandHandlerTests.cs
  ├── UpdateTaskCommandHandlerTests.cs
  ├── DeleteTaskCommandHandlerTests.cs
  └── ToggleTaskCompletionCommandHandlerTests.cs

Application/Validators/
  ├── CreateTaskCommandValidatorTests.cs
  └── UpdateTaskCommandValidatorTests.cs

Infrastructure/Repositories/
  └── TaskRepositoryTests.cs

API/Controllers/
  └── TasksControllerTests.cs

Integration/
  └── TasksApiIntegrationTests.cs
```

### Validation Logic

```python
def validate_test_coverage():
    for layer in ['Domain', 'Application', 'Infrastructure', 'API']:
        production_files = scan_production_code(layer)
        test_files = scan_test_files(layer)
        
        for prod_file in production_files:
            test_file = find_corresponding_test(prod_file, test_files)
            
            if not test_file:
                violations.add(f"Missing: {get_test_path(prod_file)}")
            elif count_test_methods(test_file) < 3:
                violations.add(f"Insufficient: {test_file} (min 3 tests required)")
        
        coverage = calculate_layer_coverage(layer)
        if coverage < THRESHOLDS[layer]:
            violations.add(f"{layer}: {coverage}% < {THRESHOLDS[layer]}% minimum")
    
    if violations:
        BLOCK_OPERATION(violations)
```

### Benefits

- ✅ Prevents coverage inflation (claims vs reality)
- ✅ Enforces comprehensive testing across ALL layers
- ✅ Catches untested handlers, validators, repositories
- ✅ Mandates integration tests for APIs
- ✅ Builds confidence in refactoring
- ✅ Early bug detection

---

## Rule 2: TDD_EMPTY_TEST_DETECTION

### Purpose

Detects and blocks low-quality tests that provide zero validation value:
- Empty test methods
- Placeholder test names (Test1, UnitTest1)
- Meaningless assertions (Assert.True(true))
- Tests with zero assertions

### Severity

**WARNING** - Allows work to continue but requires cleanup

### Detection Patterns

```csharp
// ❌ Pattern 1: Empty Test Method
[Fact]
public void Test1()
{
    // No implementation
}

// ❌ Pattern 2: Meaningless Assertion
[Fact]
public void TestSomething()
{
    Assert.True(true);  // Always passes, tests nothing
}

// ❌ Pattern 3: Zero Assertions
[Fact]
public void TestFeature()
{
    var result = GetData();
    // No assertion - test can't fail
}

// ❌ Pattern 4: Placeholder Name
public class UnitTest1  // Generic name
{
    public void Test1() { }  // Generic name
}
```

### Example: Cortex-Clean Detection

**Found in UnitTest1.cs:**
```csharp
namespace Cortex.Clean.Tests;

public class UnitTest1  // ❌ Placeholder class name
{
    [Fact]
    public void Test1()  // ❌ Placeholder method name
    {
        // ❌ Empty body - no test logic
    }
}
```

**Impact:**
- Test count: 1 (counted by tools)
- Test value: 0% (no validation)
- Coverage: Misleading
- False sense of security

### Good Test Example

```csharp
public class TaskEntityTests
{
    [Fact]
    public void Should_CreateTask_When_ValidTitleProvided()
    {
        // Arrange
        var title = "Test Task";
        
        // Act
        var task = new TaskEntity(title);
        
        // Assert
        task.Should().NotBeNull();
        task.Title.Should().Be(title);
        task.IsCompleted.Should().BeFalse();
    }
}
```

**Quality Checklist:**
- ✅ Descriptive name (Should_[Expected]_When_[Condition])
- ✅ AAA pattern (Arrange, Act, Assert)
- ✅ At least one meaningful assertion
- ✅ Tests actual behavior
- ✅ Can fail if code breaks
- ✅ Clear, focused purpose

### Detection Confidence

```
Empty methods:           100% (AST analysis)
Placeholder names:        95% (regex: Test\d+, UnitTest\d+)
Meaningless assertions:   90% (Assert.True(true) pattern)
Zero assertions:          95% (AST statement count)
```

### Auto-Fix Options

```bash
# Scan for empty/placeholder tests
python src/utils/test_quality_scanner.py scan Tests/

# Delete empty test files
python src/utils/test_quality_scanner.py clean Tests/ --empty

# Suggest improvements
python src/utils/test_quality_scanner.py suggest Tests/UnitTest1.cs
```

### Benefits

- ✅ Real test quality visibility
- ✅ Prevents test suite degradation
- ✅ Enforces meaningful tests
- ✅ Accurate coverage metrics
- ✅ Trustworthy test suite
- ✅ Improves developer discipline

---

## Integration with Existing TDD Workflow

### Enhanced RED Phase
```
1. Write failing test (existing)
2. ✨ NEW: Validate test file location/naming
3. ✨ NEW: Scan for empty/placeholder patterns
4. Verify test fails (existing)
5. Commit RED phase (existing)
```

### Enhanced GREEN Phase
```
1. Minimal implementation (existing)
2. Run tests (existing)
3. ✨ NEW: Validate coverage increase
4. Verify tests pass (existing)
5. Commit GREEN phase (existing)
```

### Enhanced REFACTOR Phase
```
1. Clean up code (existing)
2. Remove orphaned functions (existing)
3. ✨ NEW: Validate test file completeness
4. ✨ NEW: Clean up empty/placeholder tests
5. Verify tests still pass (existing)
6. Commit REFACTOR phase (existing)
```

---

## Configuration

### Enable/Disable Rules

Edit `cortex-brain/brain-protection-rules.yaml`:

```yaml
# Disable TDD_TEST_FILE_VALIDATION (not recommended)
- rule_id: TDD_TEST_FILE_VALIDATION
  enabled: false  # Add this line

# Change severity to WARNING instead of BLOCKED
- rule_id: TDD_TEST_FILE_VALIDATION
  severity: warning  # Instead of blocked
```

### Adjust Coverage Thresholds

```yaml
# In brain-protection-rules.yaml, modify thresholds:
layer_coverage_requirements:
  domain: 90%      # Default
  application: 85% # Default
  infrastructure: 70% # Default
  api: 80%         # Default
```

---

## Validation Commands

### Check Current Coverage Status

```bash
# Scan project for test coverage gaps
python -m src.main "validate test coverage"

# Check specific layer
python -m src.main "validate application layer coverage"
```

### Detect Empty/Placeholder Tests

```bash
# Scan all tests for quality issues
python -m src.main "scan tests for quality"

# Report empty tests
python -m src.main "find empty tests"
```

### Run Full TDD Validation

```bash
# Complete TDD Mastery validation
python -m src.main "validate tdd compliance"
```

---

## Expected Workflow Impact

### Before Enhancements

```
Developer: "I have 90% test coverage"
Reality: Only domain layer tested
CORTEX: ✅ Accepts claim (no validation)
Result: False confidence, production bugs
```

### After Enhancements

```
Developer: "I have 90% test coverage"
CORTEX: 🔍 Validating...
  - Domain: ✅ 90% (TaskEntity, Services)
  - Application: ❌ 0% (Missing handler/validator tests)
  - Infrastructure: ❌ 0% (Missing repository tests)
  - API: ❌ 0% (Missing controller/integration tests)
  
CORTEX: ❌ BLOCKED - Actual coverage 15%, claimed 90%
  
Required Actions:
  1. Create Tests/Application/Handlers/*HandlerTests.cs
  2. Create Tests/Infrastructure/Repositories/*RepositoryTests.cs
  3. Create Tests/Integration/*ApiTests.cs
  4. Re-run validation after test creation

Result: Honest coverage, comprehensive testing
```

---

## Metrics & Success Criteria

### Success Indicators

- ✅ Test file count matches production file count
- ✅ Each layer meets minimum coverage threshold
- ✅ Zero empty/placeholder tests in codebase
- ✅ All tests have meaningful assertions
- ✅ Integration tests exist for all API endpoints

### Failure Indicators

- ❌ Coverage claims > actual coverage (>10% gap)
- ❌ Layers with 0% coverage
- ❌ Empty test files (UnitTest1.cs style)
- ❌ Tests with no assertions
- ❌ Placeholder test names (Test1, TestMethod1)

---

## Rollout Strategy

### Phase 1: Detection Only (Week 1)
- Enable rules in WARNING mode
- Generate reports on existing gaps
- No blocking behavior
- Build awareness

### Phase 2: Soft Enforcement (Week 2-3)
- Block NEW code without tests
- Allow existing gaps temporarily
- Provide clear guidance
- Track improvement metrics

### Phase 3: Full Enforcement (Week 4+)
- Block ALL operations with test gaps
- Enforce empty test cleanup
- Mandatory coverage thresholds
- Zero tolerance for placeholder tests

---

## Related Documentation

- `cortex-brain/brain-protection-rules.yaml` - Complete rule definitions
- `.github/prompts/modules/tdd-mastery-guide.md` - TDD workflow guide
- `cortex-sample-apps/Cortex-Clean/CODE-QUALITY-REVIEW.md` - Gap analysis that motivated these rules
- `src/tier0/README.md` - Governance framework

---

## Summary

These two rules transform TDD Mastery from **workflow enforcement** (RED→GREEN→REFACTOR) to **quality assurance** (comprehensive, meaningful tests). They prevent the Cortex-Clean scenario where claimed coverage (90%+) drastically exceeds actual coverage (~15-20%).

**Key Takeaway:** Test count ≠ Test value. These rules ensure both quantity AND quality.
