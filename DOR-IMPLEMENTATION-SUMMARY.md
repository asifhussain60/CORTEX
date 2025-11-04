# Definition of READY (DoR) - Implementation Summary

**Date:** November 4, 2025  
**Rule:** Definition of READY (Rule #21)  
**Hemisphere:** RIGHT BRAIN (Strategic Planning)  
**Complements:** Definition of DONE (Rule #20) in LEFT BRAIN

---

## What Was Created

### 📋 Rule #21: Definition of READY

**Core Principle:** Work is NOT READY for execution unless requirements are clear, testable, and scoped.

**DoR ↔ DoD Workflow:**
```
RIGHT BRAIN (DoR)  →  LEFT BRAIN (Execute)  →  DoD Validation
   ↓ Entry gate         ↓ TDD workflow          ↓ Exit gate
Prevents bad work    Red→Green→Refactor    Prevents bad work
from STARTING                               from COMPLETING
```

---

## Key Components

### 1. Rule Document

**File:** `governance/rules/definition-of-ready.md`

**DoR Criteria (ALL must pass):**
- ✅ Requirement clarity (user story + acceptance criteria)
- ✅ Technical understanding (components, architecture, approach)
- ✅ Testability (test scenarios defined, TDD approach clear)
- ✅ Dependencies (blockers identified or "None")
- ✅ Scope definition (work <4 hours, breakdown complete)
- ✅ PR integration (when applicable)

**Validation Sequence:**
1. Parse requirement for clarity
2. Analyze technical impact
3. Define test strategy
4. Identify blockers
5. Break down scope
6. Confirm DoR complete

### 2. Automation Script

**File:** `KDS/scripts/check-definition-of-ready.ps1`

**Capabilities:**
- ✅ Analyze PR descriptions for DoR compliance
- ✅ Interactive wizard to complete DoR
- ✅ Generate acceptance criteria from requirements
- ✅ Suggest test scenarios automatically
- ✅ Guide work breakdown (tasks <4h each)
- ✅ Comment on GitHub PRs with DoR status
- ✅ Create checkpoints when DoR complete

**Usage:**
```powershell
# Check PR DoR status
pwsh KDS/scripts/check-definition-of-ready.ps1 -Source "PR" -WorkItemId 123

# Interactive DoR completion wizard
pwsh KDS/scripts/check-definition-of-ready.ps1 -Interactive

# Manual DoR validation
pwsh KDS/scripts/check-definition-of-ready.ps1
```

### 3. GitHub Actions Workflow

**File:** `.github/workflows/check-dor.yml`

**Triggers:**
- PR opened, edited, synchronized
- Comment: `@kds check dor`
- Comment: `@kds help dor`

**Actions:**
- Automatically validates DoR on every PR
- Comments on PR with DoR status
- Sets PR status check (pass/fail)
- Blocks merge if DoR incomplete
- Provides help when requested

**Status Checks:**
- ✅ Green: DoR complete → Ready for execution
- ❌ Red: DoR incomplete → Complete before starting

### 4. Hemisphere Integration

**RIGHT BRAIN (Strategic Planning):**
- New agent: `readiness-validator.md` (to be created)
- Storage: `kds-brain/right-hemisphere/readiness-queue.jsonl`
- Responsibility: Enforce DoR before handing work to LEFT BRAIN
- Tools: Acceptance criteria generator, test suggester, work breakdown estimator

**LEFT BRAIN (Tactical Execution):**
- Precondition: DoR must be complete (validated by RIGHT BRAIN)
- Refuses to execute if DoR incomplete
- Uses DoR test scenarios to generate tests (TDD)
- Validates completion against DoR criteria

---

## DoR Workflow Examples

### Example 1: PR with Complete DoR

```markdown
User: Creates PR "Add PDF export to invoices"

PR Description:
  ## User Story
  As a user, I want to export invoices as PDF,
  so that I can share them with clients
  
  ## Acceptance Criteria
  ### Scenario: Successful Export
  - Given a valid invoice
  - When I click "Export PDF"
  - Then a PDF is generated
  - And it downloads automatically
  
  ## Test Strategy
  - TDD: RED → GREEN → REFACTOR
  - Tests: InvoiceExporter_Should_GeneratePDF_WhenValidInvoice
  
  ## Technical Approach
  Create InvoiceExporter service using PDF library
  
  ## Dependencies
  None
  
  ## Estimated Effort
  3 hours

GitHub Action:
  🔍 Running DoR validation...
  
  ✅ DoR Checklist:
    ✅ Acceptance criteria: 5/5
    ✅ Test scenarios: ✓
    ✅ Technical approach: ✓
    ✅ Dependencies: ✓
    ✅ Scope defined: ✓
  
  ✅ DEFINITION OF READY: COMPLETE
  
  Status: Ready to begin execution!
  
  Next steps:
    1. Create checkpoint: git tag checkpoint-pdf-export-start
    2. Follow TDD: RED → GREEN → REFACTOR
    3. Validate with DoD before merging
```

### Example 2: PR with Incomplete DoR (Interactive Help)

```markdown
User: git pull origin feature/invoice-export

KDS (automatic detection):
  🔍 Detected PR #123 in pulled changes
  
  Running DoR validation...
  
  ❌ DEFINITION OF READY: INCOMPLETE
  
  DoR Checklist:
    [❌] Acceptance criteria: 2/5 (missing Given/When/Then)
    [❌] Test scenarios: Missing
    [✅] Technical approach: ✓
    [✅] Dependencies: ✓
    [⚠️] Estimated effort: 8 hours (exceeds 4-hour recommendation)
  
  ⚠️ Starting work now may lead to:
     - Unclear requirements
     - Missed edge cases
     - Rework needed
  
  Would you like me to help complete the DoR? [Y/N]

User: Y

KDS (Interactive Wizard):
  ═══════════════════════════════════════════════════════════
    📋 DEFINITION OF READY - Interactive Wizard
  ═══════════════════════════════════════════════════════════
  
  STEP 1: Work Description
  ───────────────────────────────────────────────────────────
  Current title: Add PDF export to invoices
  Use this title? (Y/N): Y
  
  STEP 2: User Story
  ───────────────────────────────────────────────────────────
  Format: As a [role], I want [goal], so that [benefit]
  
  As a (user role): user
  I want (what goal): to export invoices as PDF
  So that (what benefit): I can share them with clients
  
  STEP 3: Acceptance Criteria (Given/When/Then)
  ───────────────────────────────────────────────────────────
  
  Scenario 1
    Scenario name: Successful Export
    Given (precondition): a valid invoice with line items
    When (action): I click the "Export PDF" button
    Then (expected outcome): a PDF file is generated and downloads
  
  Add another scenario? (Y/N): Y
  
  Scenario 2
    Scenario name: Export with Missing Data
    Given (precondition): an invoice with no line items
    When (action): I click the "Export PDF" button
    Then (expected outcome): an error message is displayed
  
  Add another scenario? (Y/N): N
  
  STEP 4: Test Strategy
  ───────────────────────────────────────────────────────────
  Based on your acceptance criteria, I suggest these tests:
  
    • InvoiceExporter_Should_GeneratePDF_WhenValidInvoice
    • InvoiceExporter_Should_ShowError_WhenNoLineItems
  
  Add custom test scenarios? (Y/N): N
  
  STEP 5: Technical Approach
  ───────────────────────────────────────────────────────────
  Describe implementation approach: Create InvoiceExporter service
  using PDF generation library, wire up to UI button
  
  STEP 6: Dependencies & Blockers
  ───────────────────────────────────────────────────────────
  Are there any blockers or dependencies? (Y/N): N
  
  STEP 7: Effort Estimation
  ───────────────────────────────────────────────────────────
  Recommendation: Break work into tasks <4 hours each
  
  Estimated total effort (hours): 8
  
  ⚠️  Estimated effort exceeds 4 hours
  Let's break this down into smaller tasks...
  
  Suggested: 2 tasks of ~4 hours each
  
    Task 1 name: Implement PDF export service
    Task 1 estimated hours: 3
    
    Task 2 name: Wire up UI and add error handling
    Task 2 estimated hours: 2
  
  ✅ DoR saved to: KDS/dor-123.md
  
  Add DoR to PR #123 as comment? (Y/N): Y
  ✅ DoR added to PR #123
  
  DoR complete! Create checkpoint before starting? (Y/N): Y
  ✅ Checkpoint created: checkpoint-pdf-export-start
  
  Ready to execute! Follow TDD: RED → GREEN → REFACTOR
```

---

## PR Integration Flow

### Flow Diagram

```
Developer                    GitHub                      KDS (RIGHT BRAIN)
    |                           |                               |
    |------ Create PR --------->|                               |
    |                           |                               |
    |                           |------ Trigger Workflow ------>|
    |                           |                               |
    |                           |                               |--- Run DoR Check
    |                           |                               |
    |                           |<----- DoR Status Comment -----|
    |<-- PR Comment ------------|                               |
    |                           |                               |
    |                           |<----- Set Status Check -------|
    |<-- PR Status: ✅/❌ ------|                               |
    |                           |                               |
    
IF DoR Incomplete:
    |                           |                               |
    |-- Comment "@kds help" -->|                               |
    |                           |                               |
    |                           |------ Trigger Help Workflow ->|
    |                           |                               |
    |                           |                               |--- Provide Template
    |                           |<----- Help Comment -----------|
    |<-- Help Comment ---------|                               |
    |                           |                               |
    |-- Run locally: ----------|                               |
    |   pwsh check-dor.ps1 -Interactive                        |
    |                           |                               |
    |-- Update PR Description ->|                               |
    |                           |                               |
    |                           |------ Re-validate DoR ------->|
    |                           |                               |
    |                           |<----- Updated Status ---------|
    |<-- PR Status: ✅ ---------|                               |
    |                           |                               |
    |-- Begin work with --------|                               |
       confidence (DoR ✅)
```

---

## Benefits

### 1. Prevents Wasted Effort

**Before DoR:**
```
Developer starts work → Realizes requirements unclear →
Asks questions → Requirements change → Rework needed
Time wasted: 2-4 hours
```

**With DoR:**
```
DoR validation → Missing criteria identified → Complete DoR (10 min) →
Start work with clarity → No rework needed
Time saved: 2-4 hours
```

### 2. Enables TDD

DoR ensures requirements are testable:
- Acceptance criteria → Test scenarios
- Given/When/Then → Test structure
- Clear outcomes → Assertions

```csharp
// From DoR acceptance criteria:
// Given: valid invoice
// When: click "Export PDF"
// Then: PDF generated

// Becomes TDD test:
[Fact]
public void InvoiceExporter_Should_GeneratePDF_WhenValidInvoice()
{
    // Given
    var invoice = CreateValidInvoice();
    var exporter = new InvoiceExporter();
    
    // When
    var result = exporter.ExportToPDF(invoice);
    
    // Then
    Assert.NotNull(result);
    Assert.True(result.Length > 0);
}
```

### 3. Improves Team Collaboration

- **PR reviewers** understand intent immediately
- **Team members** can pick up work with context
- **Stakeholders** see clear acceptance criteria
- **Future developers** have documentation

### 4. Reduces Risk

**Risks Mitigated:**
- ❌ Unclear requirements → ✅ Acceptance criteria defined
- ❌ Scope creep → ✅ Scope explicitly defined
- ❌ Missed edge cases → ✅ Multiple scenarios documented
- ❌ Blocking dependencies → ✅ Dependencies identified upfront
- ❌ Over-engineering → ✅ Effort estimation guides simplicity

### 5. Quality Gates

```
Entry Gate (DoR)              Exit Gate (DoD)
     ↓                              ↓
Requirements CLEAR     →    Implementation CORRECT
Tests DEFINED          →    Tests PASSING
Scope BOUNDED          →    Build CLEAN
Dependencies KNOWN     →    TDD FOLLOWED
Effort ESTIMATED       →    Zero ERRORS/WARNINGS
```

---

## Metrics & Success Tracking

### DoR Effectiveness Metrics

```yaml
metrics:
  completion_rate:
    measure: "(DoR complete before work / Total work items) * 100"
    target: "> 90%"
    current: "TBD (track after Week 1)"
    
  time_to_ready:
    measure: "Average time from work creation to DoR complete"
    target: "< 15 minutes (with KDS assistance)"
    current: "TBD"
    
  rework_reduction:
    measure: "Rework incidents before vs after DoR enforcement"
    target: "> 50% reduction"
    baseline: "TBD (establish baseline Week 1)"
    
  pr_approval_rate:
    measure: "(PRs approved first review / Total PRs) * 100"
    target: "> 85%"
    hypothesis: "DoR improves first-time approval"
    
  scope_accuracy:
    measure: "Actual effort vs estimated effort"
    target: "Within 25% variance"
    improvement: "DoR breakdown improves estimates"
```

### How to Track

```powershell
# View DoR statistics
pwsh KDS/scripts/dor-stats.ps1

# Example output:
DoR Compliance Report
=====================
Last 30 days:
  Total work items: 25
  DoR complete before start: 23 (92%)
  DoR incomplete: 2 (8%)
  
Average time to DoR: 12 minutes
Rework incidents: 3 (vs 7 previous period, -57%)
PR first-approval rate: 88% (vs 65% previous, +35%)
```

---

## Integration with Brain Hemispheres

### RIGHT BRAIN Agents (Strategic)

**New Agent:** `readiness-validator.md`

**Responsibilities:**
1. Validate DoR before creating work packages
2. Guide users through interactive DoR completion
3. Generate acceptance criteria from requirements
4. Suggest test scenarios automatically
5. Break down work into <4 hour tasks
6. Identify dependencies and blockers

**Storage:**
```jsonl
// kds-brain/right-hemisphere/readiness-queue.jsonl
{
  "timestamp": "2025-11-04T10:30:00Z",
  "work_item": "PR-123",
  "dor_status": "incomplete",
  "missing": ["acceptance_criteria", "test_scenarios"],
  "auto_suggestions": {
    "acceptance_criteria": "[Generated from PR description]",
    "test_scenarios": ["Test1_Should_X_When_Y", "Test2_Should_Z_When_W"]
  },
  "estimated_completion_time": "10 minutes"
}
```

### LEFT BRAIN Agents (Tactical)

**Precondition:** DoR must be ✅ (validated by RIGHT BRAIN)

**Agents:**
- `code-executor.md`: Requires work package with DoR checklist
- `test-generator.md`: Uses DoR test scenarios to generate tests
- `validation-checker.md`: Validates completion against DoR criteria

**Handoff:**
```yaml
right_to_left_handoff:
  trigger: "DoR validation complete"
  package:
    - Title: "Add PDF export"
    - Acceptance criteria: [scenarios]
    - Test scenarios: [test names]
    - Technical approach: "..."
    - Dependencies: [list]
    - Estimated effort: 3 hours
    - DoR status: "✅ COMPLETE"
  
  left_brain_action:
    - Verify DoR complete
    - Generate tests from scenarios (TDD RED)
    - Implement code (TDD GREEN)
    - Refactor (TDD REFACTOR)
    - Validate DoD before handoff to merge
```

---

## User Commands

### Check DoR Status

```powershell
# Check current PR
pwsh KDS/scripts/check-definition-of-ready.ps1 -Source "PR" -WorkItemId 123

# Check after git pull
git pull origin feature-branch
# KDS automatically runs DoR check if PR detected
```

### Complete DoR Interactively

```powershell
# Launch interactive wizard
pwsh KDS/scripts/check-definition-of-ready.ps1 -Interactive

# Wizard guides through:
# 1. Work description
# 2. User story
# 3. Acceptance criteria
# 4. Test strategy
# 5. Technical approach
# 6. Dependencies
# 7. Effort estimation & breakdown
```

### Get DoR Help on GitHub

```markdown
# In PR comments
@kds check dor      # Triggers DoR validation
@kds help dor       # Provides DoR template and guidance
```

---

## Templates

### DoR Template (Auto-generated)

The interactive wizard generates this format:

```markdown
# [Feature Name]

## User Story

**As a** [role]
**I want** [goal]
**So that** [benefit]

## Acceptance Criteria

### Scenario: [Name]
- **Given** [precondition]
- **When** [action]
- **Then** [expected outcome]

## Test Strategy

**TDD Approach:** RED → GREEN → REFACTOR

**Test Scenarios:**
- [Test method name 1]
- [Test method name 2]

## Technical Approach

[Description of implementation]

## Dependencies

[List or "None"]

## Task Breakdown (if >4 hours)

- **Task 1:** [Name] (Xh)
- **Task 2:** [Name] (Xh)

## Definition of DONE

- [ ] Build succeeds (0 errors, 0 warnings)
- [ ] All tests passing
- [ ] TDD workflow followed
- [ ] Code reviewed
- [ ] Documentation updated

---

**Estimated Effort:** X hours
**Status:** ✅ READY FOR EXECUTION
```

---

## Next Steps (Week 1 Implementation)

### Monday Tasks

1. ✅ **Rule #21 defined** (COMPLETE)
2. ✅ **Automation script created** (COMPLETE)
3. ✅ **GitHub Actions workflow created** (COMPLETE)
4. 📋 **Create RIGHT BRAIN agent:** `readiness-validator.md`
5. 📋 **Test DoR workflow** with sample PR
6. 📋 **Update work-planner.md** to enforce DoR
7. 📋 **Create readiness-queue.jsonl** storage

### Success Criteria

- [ ] DoR validates automatically on PR creation
- [ ] Interactive wizard completes DoR in <15 min
- [ ] GitHub Actions comments on PR with DoR status
- [ ] Merge blocked when DoR incomplete
- [ ] RIGHT BRAIN refuses work without DoR ✅

---

## Related Rules

- **Rule #20 (DoD):** Exit gate that validates work completion
- **Rule #19 (Checkpoint):** Create checkpoint once DoR complete
- **Rule #18 (Challenge User):** Challenge if user tries to skip DoR
- **TDD Enforcement:** DoR ensures requirements are testable

---

## Summary

### What DoR Solves

**Problem:** Developers start work with unclear requirements, leading to:
- Wasted effort on wrong implementations
- Constant clarification questions
- Scope creep and feature bloat
- Rework when requirements change
- Difficulty writing tests (unclear what to test)

**Solution:** DoR enforces clarity BEFORE work begins:
- ✅ Requirements documented (user story + acceptance criteria)
- ✅ Tests planned (TDD approach defined)
- ✅ Scope bounded (work broken into <4h tasks)
- ✅ Dependencies known (blockers identified)
- ✅ Team aligned (PR reviewers understand intent)

### DoR + DoD = Quality Gates

```
┌─────────────────────────────────────────────────────────┐
│  RIGHT BRAIN (Strategic)    LEFT BRAIN (Tactical)       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DoR (Entry Gate)     →     Execute (TDD)               │
│  ✓ Requirements clear       Red → Green → Refactor     │
│  ✓ Tests defined                                        │
│  ✓ Scope bounded           DoD (Exit Gate)              │
│  ✓ Dependencies known       ✓ Build clean               │
│                             ✓ Tests passing              │
│  Prevents bad work          ✓ TDD followed              │
│  from STARTING              ✓ Zero errors/warnings       │
│                                                          │
│                            Prevents bad work             │
│                            from COMPLETING               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

**Status:** ✅ Rule #21 (DoR) FULLY IMPLEMENTED  
**Hemisphere:** RIGHT BRAIN (Strategic Planning)  
**Automation:** PR integration + interactive wizard  
**Next:** Create readiness-validator.md agent + test workflow
