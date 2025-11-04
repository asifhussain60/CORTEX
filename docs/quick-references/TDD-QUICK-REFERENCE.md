# TDD Quick Reference Card

**Rule:** Definition of DONE (Rule #20) - TDD ENFORCED  
**Status:** ✅ Active and Mandatory  
**Scope:** All code changes

---

## 🎯 The Rule

**Code changes are NOT DONE until TDD workflow is followed:**
1. ❌ **RED** - Write failing test
2. ✅ **GREEN** - Implement minimum code to pass
3. 🔄 **REFACTOR** - Clean up with test safety net

---

## ✅ When TDD is Enforced

**REQUIRED (TDD Active):**
- ✅ New feature implementation
- ✅ Bug fixes
- ✅ Refactoring existing code
- ✅ API endpoint additions
- ✅ UI component logic changes
- ✅ Service layer modifications
- ✅ Business logic updates

**SKIPPED (TDD Not Applicable):**
- ⏭️ Documentation changes (README.md, etc.)
- ⏭️ Configuration updates (appsettings.json, etc.)
- ⏭️ Non-code files (.gitignore, .editorconfig, etc.)
- ⏭️ Initial test infrastructure setup

---

## 🔄 TDD Workflow

### 1. RED Phase - Write Failing Test

```csharp
// InvoiceExporterTests.cs
[Fact]
public void InvoiceExporter_Should_GeneratePDF_WhenValidDataProvided()
{
    // Arrange
    var exporter = new InvoiceExporter();
    var invoice = CreateTestInvoice();
    
    // Act
    var result = exporter.ExportToPDF(invoice);
    
    // Assert
    Assert.NotNull(result);
    Assert.True(result.Length > 0);
}
```

**Run test:** ❌ FAILS (InvoiceExporter doesn't exist yet)

### 2. GREEN Phase - Implement Minimum Code

```csharp
// InvoiceExporter.cs
public class InvoiceExporter
{
    public byte[] ExportToPDF(Invoice invoice)
    {
        // Minimum code to pass test
        return new byte[] { 0x25, 0x50, 0x44, 0x46 }; // PDF header
    }
}
```

**Run test:** ✅ PASSES (minimal implementation)

### 3. REFACTOR Phase - Clean Up

```csharp
// InvoiceExporter.cs (improved)
public class InvoiceExporter
{
    private readonly IPDFGenerator _pdfGenerator;
    
    public InvoiceExporter(IPDFGenerator pdfGenerator)
    {
        _pdfGenerator = pdfGenerator;
    }
    
    public byte[] ExportToPDF(Invoice invoice)
    {
        var document = _pdfGenerator.CreateDocument();
        document.AddInvoiceData(invoice);
        return document.ToByteArray();
    }
}
```

**Run test:** ✅ STILL PASSES (refactored safely)

---

## 🚫 Common Violations

### ❌ VIOLATION: Code Without Tests

```
Changed files:
  ✅ InvoiceExporter.cs (NEW CODE)
  ❌ No test file found

Result: BLOCKED by TDD enforcement
```

**Fix:**
```bash
# Create test file first
touch InvoiceExporterTests.cs
# Write failing test (RED)
# Then implement InvoiceExporter.cs (GREEN)
```

### ❌ VIOLATION: Implementation Before Test

```
Git history:
  1. commit abc123 "feat: Add InvoiceExporter"
  2. commit def456 "test: Add tests for InvoiceExporter"

Result: Tests came AFTER implementation (not TDD)
```

**Correct order:**
```
Git history:
  1. commit abc123 "test: Add failing InvoiceExporter test"
  2. commit def456 "feat: Implement InvoiceExporter to pass test"
```

---

## ✅ Validation Flow

### Success Example

```
User: Mark invoice export as complete

KDS Analysis:
  🔍 Changed files:
      ✅ InvoiceExporterTests.cs (test)
      ✅ InvoiceExporter.cs (implementation)
  
  🧪 TDD Enforcement: ACTIVE
  
  Validations:
    [1/5] TDD Compliance: ✅ Tests exist for code
    [2/5] Build: ✅ 0 errors, 0 warnings
    [3/5] Tests: ✅ 147/147 passing
    [4/5] Coverage: ✅ 85% (target: >80%)
    [5/5] Health: ✅ All checks passed
  
  ✅ TASK COMPLETE (TDD workflow followed)
```

### Failure Example

```
User: Mark invoice export as complete

KDS Analysis:
  🔍 Changed files:
      ✅ InvoiceExporter.cs (implementation)
      ❌ No test file found
  
  🧪 TDD Enforcement: ACTIVE
  
  Validations:
    [1/5] TDD Compliance: ❌ FAILED
  
  ⚠️ TDD VIOLATION:
     Missing tests for: InvoiceExporter.cs
     Expected: InvoiceExporterTests.cs
  
  ❌ TASK NOT COMPLETE
  
  Required Actions:
    1. Write failing test (RED)
    2. Verify code passes test (GREEN)
    3. Refactor if needed (REFACTOR)
    4. Re-validate
```

---

## 🛠️ Commands

### Validate TDD Compliance

```powershell
# Check if current changes follow TDD
pwsh KDS/scripts/validate-done.ps1

# Output:
# 🔍 Analyzing changed files...
# 🧪 TDD Enforcement: ACTIVE
# ✅ TDD Compliance: Tests exist for all code changes
```

### Override TDD (Logged & Tracked)

```powershell
# Use only for exceptional cases
pwsh KDS/scripts/validate-done.ps1 -OverrideTDD -Reason "Creating test infrastructure"

# ⚠️ Override logged to: kds-brain/events.jsonl
```

### View TDD Statistics

```powershell
# Show TDD compliance over time
pwsh KDS/scripts/tdd-stats.ps1

# Output:
# TDD Compliance: 95.7% (45/47 commits)
# Test Coverage: 83.2%
# Violations: 2 (last 30 days)
```

---

## 💡 Tips for Success

### 1. Think Test-First

**Before coding, ask:**
- What behavior am I implementing?
- How can I verify it works?
- What's the simplest test I can write?

### 2. Write Smallest Possible Test

```csharp
// ✅ GOOD: Specific, focused test
[Fact]
public void Sum_Should_ReturnZero_WhenBothInputsAreZero()
{
    Assert.Equal(0, Calculator.Sum(0, 0));
}

// ❌ BAD: Too broad, testing multiple behaviors
[Fact]
public void Calculator_Should_DoMath()
{
    Assert.Equal(5, Calculator.Sum(2, 3));
    Assert.Equal(2, Calculator.Subtract(5, 3));
    Assert.Equal(15, Calculator.Multiply(3, 5));
}
```

### 3. Implement Minimum to Pass

Don't over-engineer. Start simple, refactor later.

```csharp
// ✅ GOOD: Minimum implementation (GREEN phase)
public int Sum(int a, int b)
{
    return a + b;
}

// ❌ BAD: Over-engineered for simple test
public int Sum(int a, int b)
{
    var calculator = CalculatorFactory.Create();
    var validator = new InputValidator();
    validator.Validate(a, b);
    return calculator.PerformOperation(a, b, OperationType.Addition);
}
```

### 4. Refactor with Confidence

Once tests pass, you can refactor safely.

```csharp
// GREEN phase (tests passing)
public int Sum(int a, int b)
{
    return a + b;
}

// REFACTOR phase (improve without breaking tests)
public int Sum(params int[] numbers)
{
    return numbers.Sum(); // More flexible, tests still pass
}
```

---

## 🎓 Learning Resources

### TDD Cycle Explained

```
┌─────────────────────────────────────────┐
│  RED → GREEN → REFACTOR                 │
├─────────────────────────────────────────┤
│                                         │
│  RED: Write failing test                │
│    ↓                                    │
│  GREEN: Implement minimum code          │
│    ↓                                    │
│  REFACTOR: Improve with test safety     │
│    ↓                                    │
│  (Repeat for next feature)              │
│                                         │
└─────────────────────────────────────────┘
```

### Benefits of TDD

1. **Design:** Tests force good API design
2. **Confidence:** Refactor without fear
3. **Documentation:** Tests show how to use code
4. **Regression:** Bugs stay fixed
5. **Coverage:** All paths tested

### Common Mistakes

1. ❌ Writing tests after implementation
2. ❌ Testing too much in one test
3. ❌ Not running test before implementing
4. ❌ Skipping refactor phase
5. ❌ Mocking too much (test behavior, not implementation)

---

## 📋 Checklist

### Before Starting Work

- [ ] Understand the requirement
- [ ] Think about how to verify it
- [ ] Write the test name first

### During RED Phase

- [ ] Write failing test
- [ ] Run test - verify it FAILS
- [ ] Commit test (optional for tracking)

### During GREEN Phase

- [ ] Implement minimum code to pass
- [ ] Run test - verify it PASSES
- [ ] Commit implementation

### During REFACTOR Phase

- [ ] Improve code quality
- [ ] Run tests - verify still PASSING
- [ ] Commit refactor

### Before Marking DONE

- [ ] All tests passing
- [ ] Build: 0 errors, 0 warnings
- [ ] TDD compliance verified
- [ ] Health checks passed
- [ ] Ready for checkpoint

---

## 🚀 Quick Start Examples

### Example 1: Add Validation

```csharp
// 1. RED - Test first
[Fact]
public void Validate_Should_ThrowException_WhenEmailInvalid()
{
    var validator = new EmailValidator();
    Assert.Throws<ValidationException>(() => 
        validator.Validate("not-an-email"));
}

// 2. GREEN - Implement
public class EmailValidator
{
    public void Validate(string email)
    {
        if (!email.Contains("@"))
            throw new ValidationException();
    }
}

// 3. REFACTOR - Improve
public void Validate(string email)
{
    var emailRegex = new Regex(@"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$");
    if (!emailRegex.IsMatch(email))
        throw new ValidationException("Invalid email format");
}
```

### Example 2: Fix Bug

```csharp
// 1. RED - Test that reproduces bug
[Fact]
public void Calculate_Should_HandleNegativeNumbers()
{
    var calculator = new Calculator();
    Assert.Equal(-5, calculator.Sum(-2, -3)); // Currently fails
}

// 2. GREEN - Fix bug
public int Sum(int a, int b)
{
    return a + b; // Now handles negatives
}

// 3. REFACTOR - Add validation if needed
public int Sum(int a, int b)
{
    ValidateInputs(a, b);
    return a + b;
}
```

---

## 🔗 Related Documents

- **Rule #20 Full Spec:** `governance/rules/definition-of-done.md`
- **Brain Hemispheres:** `KDS-V6-BRAIN-HEMISPHERES-DESIGN.md`
- **TDD Enforcement Summary:** `TDD-ENFORCEMENT-SUMMARY.md`
- **Progressive Intelligence Plan:** `KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md`

---

**Remember:** TDD is not about writing more code. It's about writing the RIGHT code, CONFIDENTLY.

**Mantra:** ❌ RED → ✅ GREEN → 🔄 REFACTOR → 🎯 DONE
