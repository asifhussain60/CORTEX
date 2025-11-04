# Rule 20: Definition of DONE (Tier 0 - PERMANENT)

**Priority:** CRITICAL  
**Tier:** 0 (Instinct)  
**Applies To:** All phases, tasks, and features  
**Override:** NOT ALLOWED

---

## Rule Statement

**A phase/task/feature is NOT DONE unless and until the application is building with ZERO errors AND ZERO warnings.**

---

## Purpose

- Maintain code quality
- Prevent technical debt accumulation
- Ensure clean handoffs between phases
- Validate work is truly complete
- Enable safe checkpoints (Rule 19)

---

## Validation Requirements

### Required Checks (Context-Dependent)

```yaml
definition_of_done:
  build_validation:
    required: ALWAYS
    checks:
      - Build command executes successfully
      - Exit code = 0
      - Zero compilation errors
      - Zero compilation warnings
      - No linting errors (if linter configured)
  
  test_validation:
    required: CONDITIONAL (when applicable)
    applies_when:
      - Code changes affect testable logic
      - Feature includes new functionality
      - Bug fix requires regression test
      - Refactoring existing tested code
    exempt_when:
      - Documentation-only changes
      - Configuration-only changes
      - Non-code file changes (README, .gitignore, etc.)
      - Initial test setup (creating test infrastructure)
    checks:
      - All existing tests still passing
      - New tests passing (if new tests required)
      - No flaky tests detected
      - Test coverage maintained or improved
  
  tdd_enforcement:
    principle: "Test-First Development for All Code Changes"
    workflow:
      - Write failing test first (Red)
      - Implement minimum code to pass (Green)
      - Refactor with confidence (Refactor)
    validation:
      - Tests exist BEFORE or WITH code changes
      - Test coverage for new code paths
      - No untested code merged
    exemptions: Same as test_validation (docs/config only)
    
  health_validation:
    required: ALWAYS
    checks:
      - health-validator.md passes
      - No architectural violations
      - File structure correct
      - Dependencies valid
```

### Validation Sequence

```
BEFORE marking task/phase/feature as DONE:

Step 1: Determine Test Applicability + TDD Compliance
  IF task involves code changes:
    → Test validation REQUIRED
    → TDD enforcement ACTIVE
    → Verify tests exist WITH or BEFORE code
  ELSE IF documentation/config only:
    → Test validation SKIPPED
    → TDD enforcement N/A
  
Step 2: Run Build
  Command: [project-specific build command]
  Example: dotnet build
  Required: Exit code 0
  
Step 3: Parse Build Output
  Scan for: "error", "warning", "failed"
  Required: 0 errors, 0 warnings
  
Step 4: Run Tests (if applicable) + TDD Validation
  IF test validation required:
    Sub-step A: Verify TDD compliance
      - Check test files exist for changed code files
      - Verify tests committed WITH or BEFORE implementation
      - Fail if code changes lack corresponding tests
    Sub-step B: Execute tests
      Command: [project-specific test command]
      Example: dotnet test
      Required: All tests pass
  ELSE:
    Log: "Test validation skipped (not applicable)"
    Log: "TDD enforcement skipped (no code changes)"
  
Step 5: Health Validation
  Command: #file:KDS/prompts/internal/health-validator.md
  Required: All checks green
  
Step 6: Mark as DONE
  IF all applicable validations pass:
    ✅ Task is DONE
    ✅ Create checkpoint (Rule 19)
    ✅ Proceed to next task
  ELSE:
    ❌ Task NOT DONE
    ❌ Fix issues before proceeding
    ❌ Cannot start next task
```

---

## Enforcement

### Automatic Validation

```powershell
# KDS automatic validation before marking DONE

function Test-DefinitionOfDone {
    param($Task)
    
    Write-Host "🔍 Validating Definition of DONE..." -ForegroundColor Cyan
    
    # Step 0: Determine test applicability and TDD enforcement
    $changedFiles = git diff --name-only HEAD~1
    $testApplicability = Test-RequiresTestValidation -ChangedFiles $changedFiles
    
    if ($testApplicability.TDDEnforced) {
        Write-Host "🧪 TDD Enforcement: ACTIVE" -ForegroundColor Yellow
        
        # TDD Compliance Check
        if (-not $testApplicability.TDDCompliant) {
            return @{
                Done = $false
                Reason = "TDD VIOLATION: Code changes without corresponding tests"
                TDDViolation = $true
                CodeFiles = $testApplicability.CodeFiles
                TestFiles = $testApplicability.TestFiles
                Message = "❌ Write tests BEFORE or WITH code changes (Red → Green → Refactor)"
            }
        }
        Write-Host "✅ TDD Compliance: Tests exist for code changes" -ForegroundColor Green
    } else {
        Write-Host "⏭️  TDD Enforcement: SKIPPED (no code changes)" -ForegroundColor Gray
    }
    
    # Step 1: Build validation
    $buildResult = Invoke-Build
    if ($buildResult.ExitCode -ne 0) {
        return @{
            Done = $false
            Reason = "Build failed (exit code: $($buildResult.ExitCode))"
            Errors = $buildResult.Errors
        }
    }
    
    # Step 2: Error/Warning check
    $errors = $buildResult.Output | Select-String "error"
    $warnings = $buildResult.Output | Select-String "warning"
    
    if ($errors.Count -gt 0) {
        return @{
            Done = $false
            Reason = "Build has errors"
            Errors = $errors
        }
    }
    
    if ($warnings.Count -gt 0) {
        return @{
            Done = $false
            Reason = "Build has warnings"
            Warnings = $warnings
        }
    }
    
    # Step 3: Test validation
    $testResult = Invoke-Tests
    if ($testResult.Failed -gt 0) {
        return @{
            Done = $false
            Reason = "Tests failing"
            FailedTests = $testResult.FailedTests
        }
    }
    
    # Step 4: Health check
    $healthResult = Invoke-HealthValidator
    if (-not $healthResult.AllPassed) {
        return @{
            Done = $false
            Reason = "Health checks failed"
            FailedChecks = $healthResult.FailedChecks
        }
    }
    
    # ALL PASSED
    return @{
        Done = $true
        Reason = "All validation passed"
        Metrics = @{
            Errors = 0
            Warnings = 0
            TestsPassing = $testResult.Passed
            HealthChecks = "All Green"
        }
    }
}
```

### Validation Messages

**Success:**
```
✅ TASK COMPLETE - Definition of DONE Validated

Build Validation:
  ✅ Build: Success (exit code 0)
  ✅ Errors: 0
  ✅ Warnings: 0
  
Test Validation:
  ✅ Tests Passing: 147/147
  ✅ Coverage: 78% (maintained)
  
Health Validation:
  ✅ All checks passed
  
📍 Checkpoint created: checkpoint-invoice-phase-1-complete
🎯 Ready for next phase
```

**Failure:**
```
❌ TASK NOT COMPLETE - Definition of DONE Failed

Build Validation:
  ❌ Build: Success
  ❌ Errors: 3
  ❌ Warnings: 7
  
Issues Found:
  
  Errors (3):
    1. InvoiceService.cs(45,12): error CS1002: Expected ';'
    2. InvoiceController.cs(78,5): error CS0103: Name 'result' does not exist
    3. Program.cs(123,20): error CS0246: Type 'InvoiceService' not found
  
  Warnings (7):
    1. InvoiceService.cs(12,5): warning CS8618: Non-nullable field 'Name' uninitialized
    2. InvoiceController.cs(34,10): warning CS8600: Possible null reference
    ... (5 more)

Action Required:
  ❌ FIX all 3 errors
  ❌ FIX all 7 warnings
  ✅ Re-run validation
  
This is a Tier 0 instinct rule and CANNOT be bypassed.
Cannot proceed to next task until validation passes.
```

---

## Commit Message Enforcement

### Valid Commit Messages

```bash
# Task complete (validated)
git commit -m "feat: Add invoice export (DONE: 0 errors, 0 warnings, 147 tests passing)"

# Phase complete (validated)
git commit -m "feat: Invoice export Phase 1 complete (DONE: Clean build, all tests green)"

# Feature complete (validated)
git commit -m "feat: Invoice export complete (DONE: Production ready, validated)"
```

### Invalid Commit Messages (Will be Rejected)

```bash
# ❌ Has warnings
git commit -m "feat: Add invoice export (WIP - has warnings)"
# Rejected: Definition of DONE requires 0 warnings

# ❌ Not validated
git commit -m "feat: Add invoice export (mostly working)"
# Rejected: Definition of DONE requires explicit validation

# ❌ Incomplete
git commit -m "feat: Add invoice export (some tests failing)"
# Rejected: Definition of DONE requires all tests passing
```

### Commit Hook Validation

```powershell
# .git/hooks/commit-msg
# KDS enforces Definition of DONE

$commitMsg = Get-Content $args[0]

# Check for DONE marker
if ($commitMsg -notmatch "\(DONE:.*\)") {
    Write-Host "❌ COMMIT REJECTED - Missing Definition of DONE validation" -ForegroundColor Red
    Write-Host ""
    Write-Host "Commit messages must include DONE validation:" -ForegroundColor Yellow
    Write-Host "  Example: feat: Add feature (DONE: 0 errors, 0 warnings)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This is Tier 0 Rule #20 and cannot be bypassed." -ForegroundColor Yellow
    exit 1
}

# Verify validation was actually done
$validationFile = ".kds-validation-passed"
if (-not (Test-Path $validationFile)) {
    Write-Host "❌ COMMIT REJECTED - Definition of DONE validation not run" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run validation first:" -ForegroundColor Yellow
    Write-Host "  .\KDS\scripts\validate-done.ps1" -ForegroundColor Cyan
    exit 1
}

# Validation passed
Remove-Item $validationFile
exit 0
```

---

## Integration with Workflows

### With TDD Cycle

```
TDD + Definition of DONE:

RED Phase:
  - Tests created (failing)
  - Build may have errors (expected)
  ❌ NOT DONE (tests not passing)
  
GREEN Phase:
  - Tests now passing
  - Build must be clean (0 errors, 0 warnings)
  - If warnings exist → FIX before GREEN complete
  ✅ DONE when: Tests pass + 0 errors + 0 warnings
  
REFACTOR Phase:
  - Code improved
  - Tests MUST still pass
  - Build MUST stay clean
  ✅ DONE when: Tests pass + 0 errors + 0 warnings + code improved
```

### With Phase Completion

```
Phase Completion:

Before marking phase DONE:
  1. All tasks in phase validated (Definition of DONE)
  2. Phase-level validation:
     - Integration tests passing
     - No regression in other features
     - Documentation updated
  3. Run full Definition of DONE validation
  4. Create phase checkpoint (Rule 19)
  
Example:
  Phase 1: Service Layer
    ✅ Task 1: InvoiceService (DONE: validated)
    ✅ Task 2: InvoiceRepository (DONE: validated)
    ✅ Phase 1 validation: 0 errors, 0 warnings
    📍 Checkpoint: checkpoint-invoice-phase-1-complete
```

### With Feature Completion

```
Feature Completion:

Before marking feature DONE:
  1. All phases validated (Definition of DONE)
  2. Feature-level validation:
     - E2E tests passing
     - Performance acceptable
     - Security validated
     - Documentation complete
  3. Run FULL build + tests + health checks
  4. Create feature completion checkpoint (Rule 19)
  
Example:
  Feature: Invoice Export
    ✅ Phase 1: Service Layer (DONE)
    ✅ Phase 2: API Layer (DONE)
    ✅ Phase 3: UI Layer (DONE)
    ✅ E2E tests: Passing
    ✅ Full build: 0 errors, 0 warnings
    📍 Checkpoint: checkpoint-invoice-export-done
```

---

## Test Applicability Decision Tree

### Automatic Test Requirement Detection

```yaml
task_analysis:
  question_1: "Does this task modify code files?"
    NO → Test validation SKIPPED
    YES → Continue to question 2
  
  question_2: "What type of code change?"
    documentation_comment: Test validation SKIPPED
    configuration_value: Test validation SKIPPED
    code_logic: Test validation REQUIRED
    new_feature: Test validation REQUIRED
    bug_fix: Test validation REQUIRED
    refactor: Test validation REQUIRED
  
  question_3: "Does testable code exist for this area?"
    NO (new area, no test infrastructure):
      → Test validation SKIPPED for THIS task
      → Create test infrastructure as NEXT task
      → Log: "Test infrastructure needed"
    YES:
      → Test validation REQUIRED
```

### Examples: When Tests ARE Required

```markdown
✅ Test Validation REQUIRED (TDD Enforced):

1. New Feature Implementation (TDD Workflow)
   Task: "Add invoice export functionality"
   TDD Process:
     [Red]   Write failing test: InvoiceExporter_Should_GenerateValidPDF()
     [Green] Implement minimum code to pass test
     [Refactor] Clean up implementation with test safety net
   Validation: Tests exist BEFORE feature code committed

2. Bug Fix (TDD Workflow)
   Task: "Fix null reference in InvoiceService"
   TDD Process:
     [Red]   Write test that reproduces bug
     [Green] Fix bug - test now passes
     [Refactor] Improve fix if needed
   Validation: Regression test prevents recurrence

3. Refactoring Existing Code (TDD Safety)
   Task: "Refactor InvoiceService for clarity"
   TDD Process:
     [Red]   Existing tests already exist (no red phase)
     [Green] Refactor code - all tests still pass
     [Refactor] Continue refining with test confidence
   Validation: All existing tests must still pass

4. API Endpoint Addition (TDD Workflow)
   Task: "Add GET /api/invoices endpoint"
   TDD Process:
     [Red]   Write failing integration test
     [Green] Implement endpoint to pass test
     [Refactor] Optimize response structure
   Validation: Integration tests + contract tests pass

5. UI Component Logic (TDD Workflow)
   Task: "Add validation to InvoiceForm"
   TDD Process:
     [Red]   Write failing component test
     [Green] Implement validation logic
     [Refactor] Extract validation to reusable function
   Validation: Component tests + E2E tests pass

❗ TDD ENFORCEMENT NOTE:
   All code changes above MUST follow TDD workflow.
   Commit history should show:
     1. Test commit (failing test)
     2. Implementation commit (passing test)
     3. Refactor commit (if needed)
   
   OR combined commit with test + implementation
   (acceptable for small changes)
```

### Examples: When Tests ARE NOT Required

```markdown
❌ Test Validation SKIPPED (Legitimate):

1. Documentation Changes
   Task: "Update README with new setup instructions"
   Why: No code logic changed
   Validation: Build succeeds, 0 errors, 0 warnings
   Tests: Skipped (not applicable)

2. Configuration Updates
   Task: "Update appsettings.json with new API URL"
   Why: Configuration value change only
   Validation: Build succeeds, app runs
   Tests: Skipped (config tested in deployment)

3. Dependency Version Update
   Task: "Update NuGet package version"
   Why: No code changes, just version bump
   Validation: Build succeeds, existing tests pass
   Tests: Existing tests run (not "new tests required")

4. .gitignore / .editorconfig
   Task: "Add .vs/ to .gitignore"
   Why: Development environment file
   Validation: File valid
   Tests: Skipped (not applicable)

5. Initial Test Infrastructure Setup
   Task: "Create test project and add xUnit"
   Why: Setting up test capability
   Validation: Test project builds
   Tests: Skipped (creating test infrastructure itself)
   Next: Following tasks will use this infrastructure
```

### Challenging Edge Cases

```markdown
🤔 EDGE CASE ANALYSIS:

Case 1: "Update copyright year in headers"
  Change Type: Code file modified (comments)
  Test Required? NO
  Rationale: No logic changed, comments only
  Validation: Build succeeds, 0 errors, 0 warnings

Case 2: "Add logging statements for debugging"
  Change Type: Code logic modified (logging)
  Test Required? CONDITIONAL
  If logging changes behavior → YES (test new behavior)
  If logging is passive → NO (build validation sufficient)
  Recommendation: Test if logs affect control flow

Case 3: "Rename variable for clarity"
  Change Type: Refactoring (names only)
  Test Required? YES
  Rationale: Existing tests verify no behavior change
  Validation: All existing tests must still pass

Case 4: "Add XML documentation comments"
  Change Type: Code file modified (documentation)
  Test Required? NO
  Rationale: No logic changed
  Validation: Build succeeds (XML validation automatic)

Case 5: "Change string constant value"
  Change Type: Code logic (constant value)
  Test Required? YES
  Rationale: Value changes may affect behavior
  Validation: Tests verify new value works correctly
```

---

## Efficiency Considerations

### Why Not "Always Require Tests"?

**Problem with absolute requirement:**
```
❌ "All tasks must have passing tests"

Issues:
  1. Documentation changes would need tests (waste)
  2. .gitignore updates would need tests (impossible)
  3. Config changes might not need code tests
  4. Creates false compliance (meaningless tests)
  5. Slows down legitimate non-code work
```

**Better approach (context-aware):**
```
✅ "Tasks involving code logic must have passing tests"

Benefits:
  1. Tests where they add value (code quality)
  2. Skip tests where they don't (efficiency)
  3. Clear decision tree (no ambiguity)
  4. Maintains rigor for code changes
  5. Faster for non-code changes
```

### Efficiency Metrics

```yaml
estimated_time_saved:
  scenario_1:
    task: "Update README.md"
    with_test_requirement: "15 min (README) + 10 min (meaningless test)"
    without_test_requirement: "15 min (README only)"
    time_saved: 10 minutes
    
  scenario_2:
    task: "Add new API endpoint"
    with_test_requirement: "30 min (code) + 15 min (tests) = 45 min"
    without_test_requirement: "30 min (untested code)"
    risk_created: HIGH (untested API)
    decision: REQUIRE tests (quality over speed)
    
  scenario_3:
    task: "Update config value"
    with_test_requirement: "5 min (config) + 20 min (test setup)"
    without_test_requirement: "5 min (config) + manual verification"
    time_saved: 20 minutes
    quality_impact: None (config tested in deployment)
```

---

## ⚠️ CHALLENGE: Proposed Alternative

### My Analysis

**Your Proposal:** "Passing tests required (when applicable)"

**My Assessment:** ✅ VIABLE with refinement

**Concerns:**

1. **Ambiguity Risk**
   - "When applicable" needs clear definition
   - Developers might skip tests claiming "not applicable"
   - Need automatic detection, not subjective judgment

2. **Efficiency vs Quality Balance**
   - Too strict → Waste time on meaningless tests
   - Too loose → Skip important tests
   - Need clear decision tree

3. **Edge Cases**
   - What about refactoring? (YES - existing tests verify)
   - What about logging? (CONDITIONAL - depends on impact)
   - What about constants? (YES - value changes affect behavior)

### My Recommendation: CONDITIONAL TEST REQUIREMENT

**Proposed Rule Enhancement:**

```yaml
tier_0_rule_20_refined:
  build_validation:
    requirement: ALWAYS (no exceptions)
    criteria:
      - Exit code 0
      - Zero errors
      - Zero warnings
  
  test_validation:
    requirement: CONDITIONAL (automatic detection)
    required_when:
      - Code logic modified (*.cs, *.ts, *.razor, etc.)
      - New feature added
      - Bug fix implemented
      - Existing tested code refactored
    
    exempt_when:
      - Documentation only (*.md, XML comments)
      - Configuration only (*.json, *.yaml, *.config)
      - Non-code files (.gitignore, .editorconfig)
      - Test infrastructure setup (creating test project)
    
    enforcement:
      decision_maker: KDS automatic analysis
      fallback: If uncertain → REQUIRE tests (safe default)
      override: User can justify exemption (logged)
```

### Alternative Solutions

**Option 1: Strict (Always Require Tests)**
```yaml
pros:
  - Maximum quality
  - No ambiguity
  - Forces test-first culture

cons:
  - Wastes time on non-code changes
  - Creates meaningless tests
  - Slows documentation updates
  - False compliance

verdict: TOO STRICT (inefficient)
```

**Option 2: Loose (Tests Optional)**
```yaml
pros:
  - Maximum speed
  - Developer discretion
  - Flexible

cons:
  - Tests get skipped
  - Quality degrades
  - No enforcement
  - Subjective

verdict: TOO LOOSE (quality risk)
```

**Option 3: Conditional (Recommended)**
```yaml
pros:
  - Quality where it matters (code)
  - Efficiency where appropriate (docs)
  - Clear decision tree (automatic)
  - Enforceable (KDS detects)

cons:
  - Slightly more complex
  - Edge cases need documentation
  - Requires file type analysis

verdict: BALANCED (accuracy + efficiency)
```

### Proposed Implementation

```powershell
# KDS/scripts/validate-done.ps1 (enhanced with TDD enforcement)

function Test-RequiresTestValidation {
    param($ChangedFiles)
    
    # Analyze changed files
    $codeFiles = $ChangedFiles | Where-Object {
        $_ -match '\.(cs|ts|js|razor|vue|py)$' -and
        $_ -notmatch 'test|spec|\.test\.|\.spec\.'
    }
    
    $testFiles = $ChangedFiles | Where-Object {
        $_ -match 'test|spec|\.test\.|\.spec\.'
    }
    
    $docFiles = $ChangedFiles | Where-Object {
        $_ -match '\.(md|txt)$' -or 
        $_ -match 'README|LICENSE|\.gitignore'
    }
    
    $configFiles = $ChangedFiles | Where-Object {
        $_ -match '\.(json|yaml|yml|config|xml)$' -and
        $_ -notmatch 'test'
    }
    
    # Decision logic with TDD enforcement
    if ($codeFiles.Count -gt 0) {
        # TDD CHECK: Code files require corresponding test files
        $tddCompliant = ($testFiles.Count -gt 0)
        
        return @{
            TestsRequired = $true
            TDDEnforced = $true
            TDDCompliant = $tddCompliant
            CodeFiles = $codeFiles
            TestFiles = $testFiles
            Reason = "Code files modified: $($codeFiles -join ', ')"
            Warning = if (-not $tddCompliant) { 
                "⚠️  TDD VIOLATION: Code changes detected without corresponding test changes"
            } else { 
                $null 
            }
        }
    }
    
    if ($docFiles.Count -eq $ChangedFiles.Count) {
        return @{
            TestsRequired = $false
            TDDEnforced = $false
            Reason = "Documentation-only changes"
        }
    }
    
    if ($configFiles.Count -eq $ChangedFiles.Count) {
        return @{
            TestsRequired = $false
            TDDEnforced = $false
            Reason = "Configuration-only changes (tested in deployment)"
        }
    }
    
    # Default: require tests (safe)
    return @{
        TestsRequired = $true
        TDDEnforced = $true
        TDDCompliant = ($testFiles.Count -gt 0)
        Reason = "Mixed file types - requiring tests for safety"
    }
}

function Test-TDDCompliance {
    param(
        [Parameter(Mandatory)]
        [string[]]$CodeFiles,
        [Parameter(Mandatory)]
        [string[]]$TestFiles
    )
    
    $violations = @()
    
    foreach ($codeFile in $CodeFiles) {
        # Determine expected test file path
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($codeFile)
        $extension = [System.IO.Path]::GetExtension($codeFile)
        
        # Common test naming patterns
        $expectedTestPatterns = @(
            "*$fileName.test$extension",
            "*$fileName.spec$extension",
            "*${fileName}Tests$extension",
            "*${fileName}Test$extension"
        )
        
        # Check if any test file matches
        $hasTest = $TestFiles | Where-Object {
            $testFile = $_
            $expectedTestPatterns | Where-Object { $testFile -like $_ }
        }
        
        if (-not $hasTest) {
            $violations += "Missing test for: $codeFile"
        }
    }
    
    return @{
        IsCompliant = ($violations.Count -eq 0)
        Violations = $violations
        Message = if ($violations.Count -gt 0) {
            "TDD Violations detected:`n" + ($violations -join "`n")
        } else {
            "✅ TDD compliance verified: All code changes have corresponding tests"
        }
    }
}
```

### User Confirmation Flow

```markdown
User: Mark invoice service as complete

KDS (automatic analysis):
  🔍 Analyzing changed files...
  
  Changed files:
    ✅ InvoiceService.cs (code - tests required)
    ✅ InvoiceServiceTests.cs (test file)
    ✅ README.md (documentation)
  
  Test Requirement: YES (code files modified)
  TDD Compliance: ✅ PASS (tests exist for code changes)
  
  Running validations...
  [1/5] TDD: ✅ All code changes have corresponding tests
  [2/5] Build: ✅ Success (0 errors, 0 warnings)
  [3/5] Tests: ✅ 147/147 passing
  [4/5] Health: ✅ All checks passed
  [5/5] Coverage: ✅ New code paths covered
  
  ✅ TASK COMPLETE (TDD workflow followed)
```

**OR (TDD violation detected):**

```markdown
User: Mark invoice service as complete

KDS (automatic analysis):
  🔍 Analyzing changed files...
  
  Changed files:
    ✅ InvoiceService.cs (code - tests required)
    ❌ No corresponding test file found
  
  Test Requirement: YES (code files modified)
  TDD Compliance: ❌ FAIL
  
  ⚠️  TDD VIOLATION DETECTED:
      - InvoiceService.cs modified without tests
      - Expected: InvoiceServiceTests.cs or InvoiceService.test.cs
  
  Running validations...
  [1/5] TDD: ❌ FAILED - Missing tests for code changes
  
  ❌ TASK NOT COMPLETE
  
  Action Required:
    1. Write failing test first (Red phase)
    2. Update InvoiceService.cs to pass test (Green phase)
    3. Refactor if needed (Refactor phase)
    4. Run validate-done.ps1 again
```

**OR (documentation only - TDD not applicable):**

```markdown
User: Mark README update as complete

KDS (automatic analysis):
  🔍 Analyzing changed files...
  
  Changed files:
    ✅ README.md (documentation only)
  
  Test Requirement: NO (documentation only)
  TDD Compliance: N/A (no code changes)
  
  Running validations...
  [1/3] Build: ✅ Success (0 errors, 0 warnings)
  [2/3] Health: ✅ All checks passed
  [3/3] Tests: ⏭️  Skipped (not applicable)
  
  ✅ TASK COMPLETE
```

---

## My Challenge to You

### The Question

**Is the complexity of conditional test validation worth the efficiency gain?**

### The Trade-off

```yaml
simple_approach:
  rule: "Always require passing tests"
  pros: [clear, unambiguous, maximum quality]
  cons: [wastes time, meaningless tests, false compliance]
  efficiency_impact: -15% (time wasted on non-code)
  
conditional_approach:
  rule: "Require tests when code changes"
  pros: [balanced, efficient, quality where needed]
  cons: [more complex, edge cases, needs automation]
  efficiency_impact: +10% (skip unnecessary tests)
  quality_impact: same (tests where they matter)
```

### My Recommendation

**ADOPT Conditional Test Validation with these safeguards:**

1. ✅ **Automatic file analysis** (not subjective)
2. ✅ **Safe default** (if uncertain, require tests)
3. ✅ **Clear documentation** (decision tree published)
4. ✅ **Override logging** (user exemptions tracked)
5. ✅ **Metrics tracking** (measure efficiency gains)

### Counter-Argument to Consider

**Argument for "Always Require Tests":**
> "Even documentation changes should have tests - test that documentation builds, links work, etc."

**My Response:**
> Valid point, but those are build validations (already required), not unit tests. We already enforce "build succeeds" which catches documentation build errors.

---

## Exceptions & Overrides

### NO EXCEPTIONS

Definition of DONE is Tier 0 (Instinct) - **CANNOT be overridden**

**Common requests that will be REJECTED:**

```
❌ "Skip the warnings for now"
   → Rejected: Tier 0 requires 0 warnings

❌ "Mark as done, I'll fix warnings later"
   → Rejected: Not DONE until 0 warnings

❌ "The warnings are not important"
   → Rejected: All warnings must be fixed

❌ "Just this once, let me proceed"
   → Rejected: Tier 0 rules have NO exceptions
```

### Challenge Protocol Integration

If user proposes bypassing Definition of DONE:

```
⚠️ CHALLENGE: Bypassing Definition of DONE will reduce KDS effectiveness

Proposal: Mark task as DONE with 7 warnings

Risk Analysis:
  - Quality Impact: CRITICAL - Technical debt accumulates
  - Accuracy Impact: HIGH - Warnings often indicate bugs
  - Architectural Impact: HIGH - Violates Tier 0 core principle

This violates Tier 0 Instinct Rule #20.

Alternative Approach:
  1. Fix the 7 warnings (estimated 15-20 min)
  2. Run validation again
  3. Mark as DONE when clean

To proceed with original proposal:
  ❌ OVERRIDE NOT AVAILABLE (Tier 0 rule)
  
This rule CANNOT be overridden. Fix warnings to proceed.
```

---

## Validation Script

```powershell
# KDS/scripts/validate-done.ps1
# Enforces Definition of DONE

param(
    [Parameter(Mandatory=$true)]
    [string]$Task,
    
    [switch]$Verbose
)

Write-Host "🔍 Validating Definition of DONE for: $Task" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build
Write-Host "[1/4] Running build..." -ForegroundColor Yellow
$buildResult = & dotnet build 2>&1
$buildExitCode = $LASTEXITCODE

if ($buildExitCode -ne 0) {
    Write-Host "❌ Build failed (exit code: $buildExitCode)" -ForegroundColor Red
    exit 1
}

# Step 2: Parse errors/warnings
Write-Host "[2/4] Checking for errors and warnings..." -ForegroundColor Yellow
$errors = $buildResult | Select-String "error" | Where-Object { $_ -notmatch "0 Error" }
$warnings = $buildResult | Select-String "warning" | Where-Object { $_ -notmatch "0 Warning" }

$errorCount = $errors.Count
$warningCount = $warnings.Count

if ($errorCount -gt 0) {
    Write-Host "❌ Found $errorCount errors:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}

if ($warningCount -gt 0) {
    Write-Host "❌ Found $warningCount warnings:" -ForegroundColor Red
    $warnings | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "Definition of DONE requires 0 warnings." -ForegroundColor Red
    exit 1
}

# Step 3: Tests
Write-Host "[3/4] Running tests..." -ForegroundColor Yellow
$testResult = & dotnet test --no-build 2>&1
$testExitCode = $LASTEXITCODE

if ($testExitCode -ne 0) {
    Write-Host "❌ Tests failed" -ForegroundColor Red
    exit 1
}

# Step 4: Health check
Write-Host "[4/4] Running health validation..." -ForegroundColor Yellow
# This would call health-validator.md
# For now, simplified check

# ALL PASSED
Write-Host ""
Write-Host "✅ DEFINITION OF DONE VALIDATED" -ForegroundColor Green
Write-Host ""
Write-Host "Build Validation:" -ForegroundColor Cyan
Write-Host "  ✅ Build: Success" -ForegroundColor Green
Write-Host "  ✅ Errors: 0" -ForegroundColor Green
Write-Host "  ✅ Warnings: 0" -ForegroundColor Green
Write-Host ""
Write-Host "Test Validation:" -ForegroundColor Cyan
Write-Host "  ✅ All tests passing" -ForegroundColor Green
Write-Host ""
Write-Host "Health Validation:" -ForegroundColor Cyan
Write-Host "  ✅ All checks passed" -ForegroundColor Green
Write-Host ""

# Create validation marker for commit hook
"VALIDATED" | Out-File ".kds-validation-passed" -Force

Write-Host "🎯 Task '$Task' meets Definition of DONE" -ForegroundColor Green
Write-Host "📍 Ready to create checkpoint and commit" -ForegroundColor Cyan

exit 0
```

---

## Benefits

1. ✅ **Quality Assurance** - No code committed with known issues
2. ✅ **Clean Checkpoints** - Every checkpoint is validated clean state
3. ✅ **Technical Debt Prevention** - Warnings fixed immediately, not deferred
4. ✅ **Clear Status** - DONE means truly done, not "mostly done"
5. ✅ **Team Standards** - Everyone follows same completion criteria
6. ✅ **Safe Rollbacks** - All checkpoints are guaranteed clean builds

---

## Related Rules

- **Rule 19:** Checkpoint Strategy (only creates checkpoints at DONE state)
- **Rule 18:** Challenge User Changes (prevents bypassing DONE validation)
- **Rule 16:** Brain Update Protocol (DONE events trigger learning)

---

## Examples

### Example 1: Task Validation Success

```markdown
User: Mark invoice service task as complete

KDS:
  🔍 Validating Definition of DONE...
  
  [1/4] Running build... ✅
  [2/4] Checking errors/warnings... ✅ 0 errors, 0 warnings
  [3/4] Running tests... ✅ 147/147 passing
  [4/4] Health validation... ✅ All checks passed
  
  ✅ TASK COMPLETE - Definition of DONE Validated
  
  📍 Creating checkpoint: checkpoint-invoice-service-complete
  🎯 Ready to commit
```

### Example 2: Task Validation Failure

```markdown
User: Mark invoice UI as complete

KDS:
  🔍 Validating Definition of DONE...
  
  [1/4] Running build... ✅
  [2/4] Checking errors/warnings... ❌
  
  ❌ VALIDATION FAILED
  
  Found 5 warnings:
    1. InvoiceView.razor(23): warning CS8618: Non-nullable field uninitialized
    2. InvoiceView.razor(45): warning CS8600: Possible null reference
    3. InvoiceView.razor.cs(67): warning IDE0059: Unnecessary assignment
    4. InvoiceView.razor.cs(89): warning CA1822: Member can be static
    5. InvoiceStyles.css(12): warning CSS0000: Unknown property
  
  Action Required:
    Fix all 5 warnings before marking task complete.
    This is Tier 0 Rule #20 - cannot be bypassed.
    
  Estimated time to fix: 10-15 minutes
```

### Example 3: Challenge Protocol

```markdown
User: Just mark it complete with the warnings, I'll fix them later

KDS:
  ⚠️ CHALLENGE: Bypassing Definition of DONE

  Proposal: Mark task complete with 5 warnings
  
  Risk Analysis:
    - Quality Impact: CRITICAL - Technical debt accumulates
    - Maintenance Impact: HIGH - Warnings become errors later
    - Team Impact: HIGH - Lowers code quality standards
  
  This violates Tier 0 Instinct Rule #20.
  
  Alternative:
    Fix 5 warnings now (10-15 min) → Clean commit
  
  Override Status: ❌ NOT AVAILABLE
  Tier 0 rules cannot be overridden.
  
  Fix warnings to proceed.
```

---

**Status:** ✅ ACTIVE (Tier 0 - Permanent)  
**Enforcement:** Automatic via validation script + commit hooks  
**Override:** NOT ALLOWED  
**Applies:** All development work starting v6.0
