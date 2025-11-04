# Rule 21: Definition of READY (Tier 0 - PERMANENT)

**Priority:** CRITICAL  
**Tier:** 0 (Instinct)  
**Hemisphere:** RIGHT BRAIN (Strategic Planning)  
**Applies To:** All tasks before execution begins  
**Override:** NOT ALLOWED

---

## Rule Statement

**A task is NOT READY for execution unless and until all requirements are clear, testable, and have acceptance criteria defined.**

---

## Purpose

- Prevent premature work on unclear requirements
- Enable LEFT BRAIN to execute with confidence
- Reduce rework from incomplete understanding
- Ensure TDD can be applied (testable requirements)
- Support PR integration and team collaboration

---

## DoR ↔ DoD Relationship

```yaml
workflow:
  RIGHT BRAIN (DoR):
    phase: "BEFORE work begins"
    validates:
      - Requirements clear
      - Acceptance criteria defined
      - Dependencies identified
      - Test scenarios outlined
    output: "Work package ready for LEFT BRAIN"
  
  LEFT BRAIN (DoD):
    phase: "AFTER work completes"
    validates:
      - Build succeeds
      - Tests passing
      - TDD followed
      - Zero errors/warnings
    output: "Completed work ready for merge"

integration:
  handoff: "DoR → Execute → DoD"
  quality_gates:
    - DoR prevents bad work from starting
    - DoD prevents bad work from completing
```

---

## Definition of READY Criteria

### Required Checks (ALL Must Pass)

```yaml
definition_of_ready:
  requirement_clarity:
    required: ALWAYS
    checks:
      - User story/requirement clearly stated
      - Acceptance criteria defined (Given/When/Then)
      - Success metrics identified
      - Failure cases considered
    
  technical_understanding:
    required: ALWAYS
    checks:
      - Affected components identified
      - Architecture impact assessed
      - Technical approach outlined
      - Breaking changes flagged
    
  testability:
    required: ALWAYS
    checks:
      - Test scenarios defined
      - Test data requirements identified
      - Expected outcomes documented
      - TDD approach clear (RED → GREEN → REFACTOR)
    
  dependencies:
    required: ALWAYS
    checks:
      - Upstream dependencies identified
      - Blocking issues resolved
      - Required resources available
      - Team coordination confirmed
    
  scope_definition:
    required: ALWAYS
    checks:
      - Work breakdown complete
      - Estimated effort reasonable (<4 hours per task)
      - Out-of-scope items documented
      - Definition of DONE understood
    
  pr_integration:
    required: CONDITIONAL (when PR exists)
    checks:
      - PR linked to issue/work item
      - PR description complete
      - Target branch identified
      - Reviewers assigned
      - CI/CD pipeline ready
```

---

## Validation Sequence

```yaml
BEFORE starting work:

step_1_requirement_validation:
  action: "Parse requirement for clarity"
  questions:
    - What is the user trying to achieve?
    - What does success look like?
    - What could go wrong?
  output: "Clear user story with acceptance criteria"
  
step_2_technical_analysis:
  action: "Analyze technical impact"
  questions:
    - Which files/components will change?
    - Are there architectural implications?
    - What patterns apply?
  output: "Technical approach document"
  
step_3_test_planning:
  action: "Define test strategy"
  questions:
    - What test scenarios cover this?
    - What's the TDD approach?
    - What test data is needed?
  output: "Test plan with scenarios"
  
step_4_dependency_check:
  action: "Identify blockers"
  questions:
    - Are there blocking issues?
    - Do we have required resources?
    - Is the codebase ready?
  output: "Dependency graph + blockers list"
  
step_5_scope_breakdown:
  action: "Break work into tasks"
  questions:
    - Can this be done in <4 hours?
    - What's in/out of scope?
    - What's the DoD?
  output: "Task breakdown + estimates"
  
step_6_ready_confirmation:
  action: "Final DoR checklist"
  IF all criteria pass:
    ✅ Work is READY
    ✅ Hand to LEFT BRAIN for execution
    ✅ Create checkpoint (Rule #19)
  ELSE:
    ❌ Work NOT READY
    ❌ Gather missing information
    ❌ Do NOT start execution
```

---

## Acceptance Criteria Format

### Given/When/Then Template

```gherkin
Feature: [Feature Name]
  As a [user type]
  I want [goal]
  So that [benefit]

Scenario: [Scenario Name]
  Given [precondition]
  And [additional precondition]
  When [action]
  Then [expected outcome]
  And [additional outcome]

Scenario: [Error Scenario]
  Given [error condition]
  When [action]
  Then [error handling expected]
```

### Example: Invoice Export Feature

```gherkin
Feature: PDF Invoice Export
  As a user
  I want to export invoices as PDF
  So that I can share them with clients

Scenario: Successful PDF Export
  Given a valid invoice with line items
  And the invoice has customer information
  When I click the "Export PDF" button
  Then a PDF file is generated
  And the PDF contains invoice number, date, and total
  And the PDF downloads automatically

Scenario: Export with Missing Data
  Given an invoice with no line items
  When I click the "Export PDF" button
  Then an error message is displayed
  And the error states "Cannot export empty invoice"
  And no PDF is generated

Scenario: Large Invoice Export
  Given an invoice with 100+ line items
  When I click the "Export PDF" button
  Then the export completes within 5 seconds
  And the PDF is properly paginated
  And all line items are included
```

---

## PR Integration Workflow

### GitHub PR + DoR Integration

```yaml
pr_workflow:
  phase_1_pr_creation:
    trigger: "User creates PR or pulls latest changes"
    kds_action: "Analyze PR for DoR compliance"
    
  phase_2_dor_analysis:
    checks:
      - PR description contains acceptance criteria
      - Linked issue has clear requirements
      - Test scenarios documented
      - Technical approach outlined
      - Dependencies identified
    output: "DoR compliance report"
    
  phase_3_user_guidance:
    IF dor_incomplete:
      action: "Guide user to complete DoR"
      suggestions:
        - Missing acceptance criteria → Template provided
        - No test scenarios → Help define scenarios
        - Unclear scope → Help break down work
        - Blockers exist → Identify and resolve
    ELSE:
      action: "Approve DoR and enable execution"
      
  phase_4_handoff:
    action: "Create work package for LEFT BRAIN"
    includes:
      - Acceptance criteria
      - Test scenarios
      - Technical approach
      - Estimated effort
```

### KDS Commands for PR Integration

```powershell
# User pulls PR or syncs branch
git pull origin feature-branch

# KDS automatically runs DoR check
pwsh KDS/scripts/check-definition-of-ready.ps1 -Source "PR"

# Output:
🔍 Analyzing PR for Definition of READY...

PR: #123 "Add PDF export to invoices"
Source: GitHub Issue #456

DoR Checklist:
  [❌] Acceptance criteria defined
  [✅] Technical approach outlined
  [❌] Test scenarios documented
  [✅] Dependencies identified
  [⚠️] Estimated effort: 8 hours (exceeds 4-hour recommendation)

❌ WORK NOT READY

Recommendations:
  1. Add acceptance criteria (use template below)
  2. Define test scenarios for PDF generation
  3. Break work into smaller tasks (current: 8h, target: <4h)

Would you like me to help complete the DoR? [Y/N]
```

---

## Automated DoR Assistance

### KDS Helps User Reach DoR

```markdown
User: I pulled the PR for invoice export

KDS (RIGHT BRAIN - DoR Validator):
  🔍 Analyzing PR #123...
  
  ❌ DEFINITION OF READY: INCOMPLETE
  
  Missing Items:
    1. Acceptance criteria not defined
    2. Test scenarios missing
    3. Work too large (8h, recommend <4h)
  
  ✅ Let me help you reach DoR!
  
  --- STEP 1: Acceptance Criteria ---
  
  I found the requirement: "Add PDF export to invoices"
  
  Let me draft acceptance criteria:
  
  ```gherkin
  Feature: PDF Invoice Export
    As a user
    I want to export invoices as PDF
    So that I can share them with clients
  
  Scenario: Successful Export
    Given a valid invoice
    When I click "Export PDF"
    Then a PDF is generated
    And it downloads automatically
  ```
  
  Does this match your understanding? [Y/N/Edit]

User: Yes

KDS:
  ✅ Acceptance criteria saved
  
  --- STEP 2: Test Scenarios ---
  
  Based on acceptance criteria, I recommend these tests:
  
  1. InvoiceExporter_Should_GeneratePDF_WhenValidInvoice
  2. InvoiceExporter_Should_ThrowException_WhenInvoiceEmpty
  3. InvoiceExporter_Should_CompleteFast_WhenLargeInvoice
  
  TDD Approach:
    [Red] Write failing test for scenario 1
    [Green] Implement minimum export functionality
    [Refactor] Extract PDF generation logic
  
  Approve test plan? [Y/N/Edit]

User: Yes

KDS:
  ✅ Test scenarios saved
  
  --- STEP 3: Work Breakdown ---
  
  Current estimate: 8 hours
  Recommendation: Break into smaller tasks (<4h each)
  
  Suggested breakdown:
    Task 1: PDF generation service (3h)
      - Create InvoiceExporter class
      - Implement basic PDF generation
      - Tests: scenarios 1-2
    
    Task 2: UI integration (2h)
      - Add "Export PDF" button
      - Wire up service
      - Tests: E2E test
    
    Task 3: Error handling (2h)
      - Handle missing data
      - Add user feedback
      - Tests: scenario 2-3
    
    Task 4: Performance optimization (1h)
      - Optimize large invoices
      - Add progress indicator
      - Tests: scenario 3
  
  Accept breakdown? [Y/N/Customize]

User: Yes

KDS:
  ✅ Work breakdown saved
  
  --- DEFINITION OF READY: COMPLETE ---
  
  ✅ Acceptance criteria: Defined
  ✅ Test scenarios: Documented
  ✅ Work breakdown: 4 tasks, each <4h
  ✅ Dependencies: None identified
  ✅ Technical approach: Clear
  
  Ready to begin execution!
  
  Next steps:
    1. Create checkpoint: git tag checkpoint-pdf-export-start
    2. Start with Task 1 (PDF generation service)
    3. Follow TDD: RED → GREEN → REFACTOR
  
  Shall I create the checkpoint? [Y/N]
```

---

## DoR Templates

### Template 1: User Story + Acceptance Criteria

```markdown
## User Story

**As a** [user role]
**I want** [goal]
**So that** [benefit]

## Acceptance Criteria

### Scenario 1: [Happy Path]
- **Given** [precondition]
- **When** [action]
- **Then** [expected outcome]

### Scenario 2: [Error Case]
- **Given** [error condition]
- **When** [action]
- **Then** [error handling]

### Scenario 3: [Edge Case]
- **Given** [edge condition]
- **When** [action]
- **Then** [expected behavior]

## Test Strategy

- **TDD Approach:** RED → GREEN → REFACTOR
- **Test Scenarios:** [list test names]
- **Test Data:** [describe test data needs]

## Technical Approach

- **Affected Components:** [list components]
- **Architecture Pattern:** [pattern to use]
- **Breaking Changes:** [Yes/No + details]

## Dependencies

- **Blockers:** [list or "None"]
- **Required Resources:** [list or "None"]
- **Upstream Work:** [list or "None"]

## Definition of DONE

- [ ] Build succeeds (0 errors, 0 warnings)
- [ ] All tests passing
- [ ] TDD workflow followed
- [ ] Code reviewed
- [ ] Documentation updated
```

### Template 2: Bug Fix DoR

```markdown
## Bug Description

**What's broken:** [description]
**Expected behavior:** [what should happen]
**Actual behavior:** [what's happening]
**Reproduction steps:**
1. [step 1]
2. [step 2]
3. [observe error]

## Root Cause Analysis

**Hypothesis:** [what's causing the bug]
**Evidence:** [logs, screenshots, stack traces]
**Impact:** [severity + affected users]

## Fix Approach

**Solution:** [how to fix]
**Test Strategy:**
1. Write failing test that reproduces bug (RED)
2. Implement fix to pass test (GREEN)
3. Refactor if needed (REFACTOR)

**Regression Prevention:** [how to prevent recurrence]

## DoR Checklist

- [ ] Bug reproduced consistently
- [ ] Root cause identified
- [ ] Fix approach validated
- [ ] Test scenario defined
- [ ] No blocking dependencies
- [ ] Estimated effort <4 hours

## Definition of DONE

- [ ] Bug no longer reproduces
- [ ] Regression test passes
- [ ] All existing tests still pass
- [ ] Build succeeds (0 errors, 0 warnings)
```

---

## Enforcement Mechanisms

```yaml
automated_enforcement:
  pr_webhook:
    trigger: "PR created or updated"
    action: "Run DoR validation"
    output: "Comment on PR with DoR status"
    
  git_hook:
    trigger: "git pull (with remote changes)"
    action: "Check for PR-related changes"
    validation: "Run DoR check if PR detected"
    
  kds_command:
    command: "pwsh KDS/scripts/check-dor.ps1"
    usage: "Manual DoR validation"
    output: "Interactive DoR completion wizard"
    
  right_brain_agent:
    agent: "work-planner.md"
    responsibility: "Ensure DoR before creating work packages"
    enforcement: "Refuse to hand work to LEFT BRAIN if DoR incomplete"
```

---

## Integration with Hemisphere Architecture

### RIGHT BRAIN Responsibility

```yaml
right_brain_dor:
  agents:
    intent_router:
      role: "Initial DoR triage"
      action: "Classify incoming work + check DoR status"
      
    work_planner:
      role: "DoR enforcement"
      action: "Validate DoR before creating execution plan"
      output: "Work package (only if DoR complete)"
      
    readiness_validator:
      role: "DoR automation (NEW AGENT)"
      action: "Guide user through DoR completion"
      tools:
        - Acceptance criteria generator
        - Test scenario suggester
        - Work breakdown estimator
        - Dependency analyzer

  storage:
    location: "kds-brain/right-hemisphere/readiness-queue.jsonl"
    format: |
      {
        "timestamp": "2025-11-04T10:30:00Z",
        "work_item": "PR-123",
        "dor_status": "incomplete",
        "missing": ["acceptance_criteria", "test_scenarios"],
        "auto_suggestions": {
          "acceptance_criteria": "[generated template]",
          "test_scenarios": ["test1", "test2"]
        }
      }
```

### LEFT BRAIN Reception

```yaml
left_brain_dod:
  precondition: "DoR must be complete (RIGHT BRAIN validated)"
  
  agents:
    code_executor:
      requires: "Work package from RIGHT BRAIN with DoR ✅"
      validates: "DoR checklist in work package"
      refuses: "Execute if DoR incomplete"
      
    test_generator:
      requires: "Test scenarios from DoR"
      action: "Generate tests from acceptance criteria"
      
    validation_checker:
      role: "DoD enforcement"
      action: "Validate completion against DoR criteria"

  handoff:
    right_to_left: "DoR ✅ → Execute"
    left_to_corpus: "DoD ✅ → Merge"
```

---

## GitHub Actions Integration

### .github/workflows/check-dor.yml

```yaml
name: Definition of READY Check

on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  check-dor:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup PowerShell
        uses: azure/powershell@v1
      
      - name: Run DoR Validation
        id: dor
        run: |
          pwsh KDS/scripts/check-definition-of-ready.ps1 -PR ${{ github.event.pull_request.number }}
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const dorStatus = '${{ steps.dor.outputs.status }}';
            const dorReport = '${{ steps.dor.outputs.report }}';
            
            const body = dorStatus === 'complete' 
              ? '✅ **Definition of READY: COMPLETE**\n\n' + dorReport
              : '❌ **Definition of READY: INCOMPLETE**\n\n' + dorReport +
                '\n\nUse `@kds help dor` to get assistance completing DoR.';
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
      
      - name: Block merge if DoR incomplete
        if: steps.dor.outputs.status != 'complete'
        run: |
          echo "::error::DoR validation failed. Complete DoR before merging."
          exit 1
```

---

## User Interaction Examples

### Example 1: Starting New Work

```markdown
User: I want to add PDF export feature

KDS (RIGHT BRAIN - DoR Validator):
  📋 Let's ensure this work is READY before starting.
  
  Running DoR check...
  
  ❌ DEFINITION OF READY: INCOMPLETE
  
  I need to understand:
    1. What should the PDF contain?
    2. When should export happen?
    3. How should users access it?
  
  Would you like me to help define acceptance criteria? [Y/N]

User: Yes

KDS:
  Great! I'll ask some questions...
  
  Q1: Who will use this PDF export?
  User: Customers receiving invoices
  
  Q2: What triggers the export?
  User: User clicks "Export PDF" button
  
  Q3: What must be in the PDF?
  User: Invoice number, date, line items, total
  
  ✅ Based on your answers, here's the DoR:
  
  [Shows complete acceptance criteria]
  
  Approve? [Y/N/Edit]
```

### Example 2: PR Pull with Incomplete DoR

```markdown
User: git pull origin feature/invoice-export

KDS (Automatic DoR Check):
  🔍 Detected PR #123 in pulled changes
  
  Running DoR validation...
  
  PR: "Add PDF export to invoices"
  Status: ❌ NOT READY
  
  Issues:
    1. No acceptance criteria in PR description
    2. Test plan missing
    3. Work not broken down
  
  ⚠️ Starting work now may lead to:
     - Unclear requirements
     - Missed edge cases
     - Rework needed
  
  Recommendation: Complete DoR first (5-10 min investment)
  
  Options:
    1. Let me help complete DoR (interactive)
    2. Show DoR template (I'll fill it myself)
    3. Skip DoR (not recommended)
  
  Choose [1/2/3]:
```

---

## Benefits

### 1. **Prevents Wasted Effort**
- No coding with unclear requirements
- Reduces rework from misunderstanding
- Catches scope creep early

### 2. **Enables TDD**
- Testable requirements = clear tests
- Acceptance criteria → test scenarios
- DoR ensures TDD is possible

### 3. **Improves Collaboration**
- Clear handoff: RIGHT BRAIN → LEFT BRAIN
- PR reviewers understand intent
- Team alignment on scope

### 4. **Reduces Risk**
- Dependencies identified upfront
- Breaking changes flagged early
- Effort estimation more accurate

### 5. **Complements DoD**
```
DoR (entry gate) → Execute → DoD (exit gate)
  ↓                             ↓
Prevents bad work from starting | Prevents bad work from completing
```

---

## Metrics

```yaml
dor_effectiveness_metrics:
  completion_rate:
    calculation: "(DoR complete / Total work items) * 100"
    target: "> 90%"
    
  time_to_ready:
    calculation: "Avg time from work creation to DoR complete"
    target: "< 15 minutes (with KDS assistance)"
    
  rework_reduction:
    calculation: "Rework incidents before vs after DoR"
    target: "> 50% reduction"
    
  pr_approval_rate:
    calculation: "(PRs approved first try / Total PRs) * 100"
    target: "> 85%"
    impact: "DoR improves first-time approval rate"
```

---

## Related Rules

- **Rule #20 (DoD):** DoR is the entry gate, DoD is the exit gate
- **Rule #19 (Checkpoint):** Create checkpoint once DoR complete
- **Rule #18 (Challenge User):** Challenge if user skips DoR
- **TDD Enforcement:** DoR ensures requirements are testable

---

## Next Steps

1. Create `KDS/scripts/check-definition-of-ready.ps1`
2. Add RIGHT BRAIN agent: `readiness-validator.md`
3. Create GitHub Actions workflow
4. Add DoR templates to `templates/`
5. Integrate with PR workflow

---

**Status:** ✅ Rule #21 Defined  
**Hemisphere:** RIGHT BRAIN (Strategic Planning)  
**Complements:** Rule #20 (DoD) in LEFT BRAIN (Tactical Execution)  
**Integration:** PR webhook + git pull automation
