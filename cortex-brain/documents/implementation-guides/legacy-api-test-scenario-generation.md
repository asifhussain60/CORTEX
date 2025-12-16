# Legacy API Test Scenario Generation

**Feature:** CORTEX Lens Test Case Generation  
**Version:** 3.0  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 16, 2025

---

## Overview

The Legacy API Modernizer (CORTEX Lens) has been enhanced to automatically generate comprehensive test scenarios organized by priority (P0, P1, P2) for documented legacy APIs. This feature creates structured test cases based on extracted business rules, validations, and database operations.

---

## Purpose

**Problem:**
- Legacy APIs lack documented test cases
- Unclear which tests are critical vs nice-to-have
- Manual test case creation is time-consuming and error-prone
- Risk of missing edge cases during modernization

**Solution:**
- Auto-generate test scenarios from legacy code analysis
- Organize by priority (P0/P1/P2) for phased testing
- Include concrete test steps and expected results
- Reference legacy code line numbers for traceability

---

## Test Priority Levels

### P0 - Critical Path Tests 🔴

**Definition:** Core functionality that MUST work - business critical path

**Sources:**
- Primary method execution (Execute, Run, Process)
- First 3 business rules extracted from code
- Critical database operations (INSERT, UPDATE, DELETE)

**Criteria:**
- Must achieve 100% pass rate before release
- Blocking for deployment
- Automate in CI/CD pipeline

**Example P0 Tests:**
- Execute primary operation successfully
- Critical business rule enforcement
- Database transaction integrity

---

### P1 - Happy Path Variations 🟡

**Definition:** API works correctly with different valid inputs and common scenarios

**Sources:**
- Business rules 4-6 (variations)
- Database SELECT operations
- Common workflow paths

**Criteria:**
- Target 95%+ pass rate
- Non-blocking but investigated
- Automate in nightly builds

**Example P1 Tests:**
- Business rule variations (TRUE/FALSE conditions)
- Data retrieval with/without results
- Multiple valid input combinations

---

### P2 - Edge Cases & Error Handling 🟢

**Definition:** API handles unusual scenarios and errors gracefully

**Sources:**
- All validation rules
- Business rules 7-9 (boundary conditions)
- Transaction failure scenarios

**Criteria:**
- Target 90%+ pass rate
- Investigated if patterns emerge
- Automate in weekly regression

**Example P2 Tests:**
- Input validation (null, empty, invalid format)
- Boundary value testing
- Database rollback verification

---

## Generated Test Scenario Structure

### Document Layout

```markdown
# Test Scenarios - {ApiName}

## Overview
- Priority explanations
- Test coverage summary

## 🔴 P0 - Critical Path Tests
### P0-001: Test Name
- Objective
- Preconditions
- Test Steps
- Expected Results
- Legacy Reference
- Priority Justification

## 🟡 P1 - Happy Path Variations
### P1-001: Test Name
...

## 🟢 P2 - Edge Cases
### P2-001: Test Name
...

## Test Execution Summary
- Total counts by priority
- Execution order recommendations
- Test data requirements
- Automation recommendations
```

---

## Each Test Scenario Includes

1. **Test ID:** `P0-001`, `P1-001`, `P2-001` format
2. **Test Name:** Descriptive title from business rule
3. **Objective:** Clear statement of what's being tested
4. **Preconditions:** Required state before execution
5. **Test Steps:** Numbered, executable steps
6. **Expected Results:** Specific, measurable outcomes
7. **Legacy Reference:** Line numbers in original code
8. **Priority Justification:** Why this priority level

---

## Usage Scenarios

### For QA Teams

1. **Manual Test Planning**
   - Use generated scenarios as baseline test plan
   - Add environment-specific details
   - Customize test data for your context

2. **Test Case Management**
   - Import into test management tools (JIRA, Azure DevOps)
   - Map to requirements
   - Track execution results

3. **Regression Testing**
   - Verify modernized API matches legacy behavior
   - Compare outputs for same inputs
   - Validate business rules still enforced

### For Developers

1. **Automated Test Creation**
   - Convert to xUnit/NUnit test methods
   - Use as template for test structure
   - Ensure coverage of all priorities

2. **TDD Implementation**
   - Start with P0 tests (RED phase)
   - Implement to pass (GREEN phase)
   - Refactor with P1/P2 coverage

3. **Code Review**
   - Verify implementation covers all test scenarios
   - Check edge cases are handled
   - Validate error handling

### For Product Managers

1. **Acceptance Criteria**
   - P0 tests define minimum viable functionality
   - P1 tests define expected behavior
   - P2 tests define robustness

2. **Risk Assessment**
   - P0 failures = high risk (block release)
   - P1 failures = medium risk (investigate)
   - P2 failures = low risk (backlog)

---

## File Location

**Output Structure:**
```
specifications/
└── {api-name}/
    ├── business-spec.md
    ├── openapi.yaml
    ├── openapi.json
    ├── traceability-matrix.md
    ├── diagrams/
    │   ├── flowchart.mmd
    │   ├── sequence.mmd
    │   └── dependency.mmd
    └── tests/                    ← NEW
        └── test-scenarios.md     ← Priority-based test cases
```

---

## Generation Process

### How Test Scenarios Are Created

1. **Analysis Phase** (in `legacy_spec_generator.py`)
   - Extract methods, business rules, validations, DB operations
   - Classify by layer (Domain, UseCase, Infrastructure)
   - Identify primary execution method

2. **P0 Generation**
   - Primary method → P0-001 (execution test)
   - First 3 business rules → P0-002 to P0-004
   - Critical DB ops (INSERT/UPDATE/DELETE) → Remaining P0 tests

3. **P1 Generation**
   - Business rules 4-6 → Variation testing
   - SELECT operations → Data retrieval tests

4. **P2 Generation**
   - All validations → Input validation tests
   - Business rules 7-9 → Boundary condition tests
   - DB operations → Transaction rollback test

5. **Output Phase**
   - Create `tests/` directory
   - Generate `test-scenarios.md`
   - Include summary statistics

---

## Command-Line Usage

### Generate Specifications with Test Scenarios

```powershell
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py `
  "C:\path\to\LegacyApi.cs" `
  "C:\output\directory"
```

**Output:**
```
🔍 Analyzing LegacyApi.cs...
✅ Analysis complete:
   - Methods: X
   - Business Rules: X
   - Validations: X
   - DB Operations: X

📝 Generating specifications...
   ✅ business-spec.md
   ✅ traceability-matrix.md
   📋 Generating test scenarios...
   ✅ tests/test-scenarios.md (XXXX chars)
   ✅ openapi.yaml
   ✅ openapi.json
```

---

## Example Test Scenarios

### P0 - Critical Path Example

```markdown
### P0-001: Execute Primary Operation Successfully

**Objective:** Verify that the main operation executes without errors

**Preconditions:**
- All required inputs are provided and valid
- System is in ready state
- Database connections are available

**Test Steps:**
1. Initialize XGenerateFundingInvoice with valid configuration
2. Call `Execute()` method
3. Verify operation completes successfully

**Expected Results:**
- Method executes without throwing exceptions
- Return value indicates success
- Database operations complete as expected

**Legacy Reference:** Lines 19-139

**Priority Justification:** Core entry point for all API functionality
```

### P1 - Happy Path Example

```markdown
### P1-001: InvoiceAmount Validation - Variation Testing

**Objective:** Test business rule with various valid input combinations

**Scenarios:**

**Scenario A: Condition TRUE**
- Input: InvoiceAmount > 0
- Expected: Processing continues

**Scenario B: Condition FALSE**
- Input: InvoiceAmount <= 0
- Expected: Validation error raised

**Test Steps:**
1. Execute Scenario A with positive amount
2. Verify processing continues
3. Execute Scenario B with zero amount
4. Verify error raised

**Expected Results:**
- Both scenarios handled correctly
- Appropriate error messages
- No data corruption

**Legacy Reference:** Line 21 (UseCase Layer)
```

### P2 - Edge Case Example

```markdown
### P2-001: Validation - Null Invoice Date

**Objective:** Verify input validation for InvoiceDate field

**Test Data:**

**Invalid Case:**
- Field: InvoiceDate
- Value: null
- Expected Error: "Invoice date is required."

**Valid Case:**
- Field: InvoiceDate
- Value: DateTime.Today
- Expected: Validation passes

**Test Steps:**
1. Attempt operation with null InvoiceDate
2. Verify validation error is raised
3. Verify error message matches expected
4. Retry with valid InvoiceDate
5. Verify operation proceeds

**Expected Results:**
- Invalid input rejected with clear error message
- Valid input accepted
- No data corruption on validation failure

**Legacy Reference:** Line 24
```

---

## Test Execution Recommendations

### Recommended Order

1. **Run P0 first** - Must achieve 100% pass rate
2. **Run P1 second** - Target 95%+ pass rate
3. **Run P2 third** - Target 90%+ pass rate

### Test Data Requirements

- Database with test schema matching production
- Sample data covering all business rule scenarios
- Mock services for external dependencies
- Test users with appropriate permissions

### Automation Strategy

| Priority | Frequency | Pipeline Integration | Blocking |
|----------|-----------|---------------------|----------|
| P0 | Every commit | CI/CD (PR builds) | Yes |
| P1 | Nightly | Scheduled builds | No |
| P2 | Weekly | Regression suite | No |

---

## Converting to Automated Tests

### Example: P0 Test → xUnit

**Generated Scenario:**
```markdown
### P0-001: Execute Primary Operation Successfully

**Test Steps:**
1. Initialize API with valid configuration
2. Call Execute() method
3. Verify operation completes successfully
```

**xUnit Implementation:**
```csharp
[Fact]
[Trait("Category", "P0")]
[Trait("Priority", "Critical")]
public async Task Execute_WithValidConfiguration_ShouldCompleteSuccessfully()
{
    // Arrange - Step 1
    var api = new XGenerateFundingInvoice();
    var config = CreateValidConfiguration();
    
    // Act - Step 2
    var result = await api.Execute(config);
    
    // Assert - Step 3
    result.Should().NotBeNull();
    result.Success.Should().BeTrue();
    result.Errors.Should().BeEmpty();
}
```

---

## Integration with Existing Workflows

### Planning System 2.0

Test scenarios integrate seamlessly with Planning System 2.0:

1. **Phase 1 (Requirements):** Use test scenarios as acceptance criteria
2. **Phase 2 (Design):** Map test scenarios to architecture layers
3. **Phase 3 (Implementation):** Convert to automated tests
4. **Phase 4 (Testing):** Execute and report results

### ADO Work Items

Map test scenarios to Azure DevOps:

- P0 tests → **Blocker** bugs if fail
- P1 tests → **High priority** bugs
- P2 tests → **Medium priority** bugs

---

## Metrics & Reporting

### Test Coverage Metrics

Track in test execution summary:

```markdown
**Total Test Scenarios:** 15
- P0 (Critical): 4 tests (27%)
- P1 (Happy Path): 4 tests (27%)
- P2 (Edge Cases): 7 tests (46%)
```

### Pass Rate Targets

- P0: 100% (hard requirement)
- P1: 95% (investigate failures)
- P2: 90% (monitor trends)

---

## Limitations & Considerations

### What's NOT Generated

- Performance tests (load, stress, spike)
- Security tests (penetration, authentication)
- UI/UX tests (for web interfaces)
- Integration tests (multi-system scenarios)

### Manual Enhancement Needed

- Environment-specific test data
- User credential management
- External service mocking strategies
- Performance benchmarks

### Known Issues

- Complex business rules may need manual clarification
- Some validations may not be detected (custom validators)
- Database operations in stored procs not analyzed

---

## Troubleshooting

### Issue: No Test Scenarios Generated

**Cause:** Insufficient business logic detected

**Solution:** Check that legacy code has:
- At least 1 method
- Some if/else statements
- Validations or DB operations

### Issue: Test Scenarios Too Generic

**Cause:** Limited information in legacy code

**Solution:** Manually enhance:
- Add specific test data examples
- Clarify expected behaviors
- Add environment details

### Issue: Missing Test Cases

**Cause:** Complex logic not extracted

**Solution:**
- Review business-spec.md for additional rules
- Manually add test scenarios
- Use as baseline, not complete test plan

---

## Future Enhancements

### Planned Features

- [ ] Generate xUnit/NUnit test code directly
- [ ] Integration test scenarios (multi-API)
- [ ] Performance test templates
- [ ] Test data generation
- [ ] Coverage gap analysis

### Feedback & Contributions

Submit issues/enhancements to: github.com/asifhussain60/CORTEX

---

## Related Documentation

- [CORTEX Lens Usage Guide](cortex-lens-usage-guide.md)
- [OpenAPI Generation Guide](openapi-generation-guide.md)
- [Planning System 2.0 Manifest](../../planning-system-2.0-manifest.yaml)
- [TDD Best Practices](../INTELLIGENT-TDD-QUICK-REF.md)

---

**Version:** 3.0.0  
**Status:** Production Ready  
**Last Updated:** December 16, 2025  
**Enhancement:** Priority-based test scenario generation
