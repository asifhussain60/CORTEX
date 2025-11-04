# KDS Governance Rule #18: Challenge User Changes (Tier 0)

**Status:** ✅ ACTIVE  
**Priority:** TIER 0 (Highest - Cannot be overridden without explicit OVERRIDE command)  
**Version:** 6.0.0-Week1  
**Implemented:** 2025-11-04

---

## 📜 Rule Statement

**KDS agents MUST challenge user proposals that violate Tier 0 governance rules before executing.**

---

## 🎯 Purpose

Prevent users from accidentally (or deliberately) degrading KDS quality by:
- Skipping TDD workflow
- Modifying core brain files without proper process
- Removing critical validation steps
- Changing agent responsibilities (SOLID violations)
- Bypassing health checks

---

## ⚠️ When to Challenge

### ALWAYS Challenge These Proposals:

1. **TDD Workflow Violations**
   ```
   User: "Skip the tests for now, just implement the code"
   User: "Don't worry about RED phase, go straight to GREEN"
   User: "We can add tests later"
   ```

2. **Brain File Direct Modifications**
   ```
   User: "Just edit knowledge-graph.yaml directly"
   User: "Manually update conversation-history.jsonl"
   User: "Delete old events from events.jsonl"
   ```

3. **SOLID Violations**
   ```
   User: "Add execution logic to work-planner.md"
   User: "Make code-executor.md also do planning"
   User: "Combine test-generator and code-executor into one agent"
   ```

4. **Validation Bypasses**
   ```
   User: "Skip health validation, just commit"
   User: "Don't run tests before committing"
   User: "Ignore errors, keep going"
   ```

5. **Architecture Violations**
   ```
   User: "Create everything in one file, refactor later"
   User: "Put this in a temporary location"
   User: "Don't follow existing patterns"
   ```

---

## 🛡️ Challenge Protocol

### Step 1: Detect Violation
Agent analyzes user request against Tier 0 rules.

### Step 2: Issue Challenge
```markdown
⚠️ **CHALLENGE - Tier 0 Rule Violation Detected**

**Proposed Action:**
[Quote the user's request]

**Violation:**
[Explain which Tier 0 rule is violated]

**Why This Matters:**
[Explain the impact/risk]

**Recommended Alternative:**
[Suggest proper approach]

**Override:**
If you understand the risks and want to proceed anyway, respond with:
"OVERRIDE: [reason for override]"

Otherwise, I'll proceed with the recommended approach.
```

### Step 3: Wait for Response
- User can provide OVERRIDE with justification
- User can accept recommendation
- User can clarify/modify request

### Step 4: Log Challenge
Record challenge to `KDS/governance/challenges.jsonl`:
```json
{
  "timestamp": "ISO-8601",
  "agent": "code-executor",
  "rule_violated": "TDD_WORKFLOW",
  "user_request": "Skip tests",
  "challenge_issued": true,
  "user_response": "OVERRIDE: Prototyping, will add tests later",
  "override_granted": true,
  "outcome": "proceeded with override"
}
```

---

## 🔧 Implementation

### All Agents Must:

1. **Load Tier 0 Rules**
   ```markdown
   At agent initialization:
   - Load #file:KDS/governance/rules/challenge-user-changes.md
   - Load all Tier 0 rules
   - Keep in context during execution
   ```

2. **Check Before Execution**
   ```
   Before implementing user request:
   → Check against Tier 0 rules
   → If violation detected → Issue challenge
   → Wait for user response
   → Only proceed with approval or override
   ```

3. **Respect Overrides**
   ```
   If user provides OVERRIDE:
   → Log override with justification
   → Proceed with original request
   → Add warning comment in code/docs
   → Flag for review in next health check
   ```

---

## 📋 Tier 0 Rules Reference

### Rule Categories:

**1. TDD Workflow (Non-Negotiable)**
- RED → GREEN → REFACTOR cycle required
- Tests created BEFORE implementation
- All tests must pass before commit
- No "implement now, test later"

**2. BRAIN Integrity**
- No manual editing of BRAIN state files
- Updates only through brain-updater.md
- Events logged through proper channels
- Knowledge graph modified programmatically

**3. SOLID Principles**
- One responsibility per agent
- No mode switches
- Dependencies through abstractions
- Agents don't cross boundaries

**4. Validation Requirements**
- Health checks before commits
- Test execution mandatory
- Build validation required
- Error correction before proceeding

**5. Architecture Preservation**
- Follow existing patterns
- Files in correct locations from start
- No "temporary" implementations
- Separation of concerns maintained

---

## 🎯 Agent-Specific Checks

### work-planner.md
- ✅ Plans include test phases
- ✅ No "implement first, test later" phases
- ✅ Validation steps in every phase
- ❌ Challenge: Plans without testing

### code-executor.md
- ✅ Follows TDD cycle (RED→GREEN→REFACTOR)
- ✅ Runs tests before finalizing
- ✅ Places code in correct architectural locations
- ❌ Challenge: Implementation without tests

### test-generator.md
- ✅ Creates tests BEFORE code implementation
- ✅ Uses component IDs (not text selectors)
- ✅ Tests placed in correct structure
- ❌ Challenge: Skipping test creation

### health-validator.md
- ✅ Runs all validation checks
- ✅ Reports failures clearly
- ✅ Blocks commits on failures
- ❌ Challenge: Skipping validation

### commit-handler.md
- ✅ Requires green tests
- ✅ Validates build status
- ✅ Enforces semantic messages
- ❌ Challenge: Committing with failures

---

## 💡 Example Challenges

### Example 1: TDD Violation
```markdown
User: "Just implement the PDF export feature, we'll add tests tomorrow"

Agent Response:
⚠️ **CHALLENGE - TDD Workflow Violation**

**Proposed Action:**
Implement PDF export feature without tests

**Violation:**
Tier 0 Rule: TDD Workflow - Tests must be created BEFORE implementation

**Why This Matters:**
- Reduces code quality
- Makes refactoring risky
- Often "tomorrow" never comes
- Violates KDS core principles

**Recommended Alternative:**
1. Create tests for PDF export (RED phase)
2. Implement feature to make tests pass (GREEN phase)
3. Refactor for quality (REFACTOR phase)
Total time: ~20% longer, 10x safer

**Override:**
Type "OVERRIDE: [reason]" to proceed without tests.
```

### Example 2: Architecture Violation
```markdown
User: "Put all the export logic in the page component for now"

Agent Response:
⚠️ **CHALLENGE - Architecture Violation**

**Proposed Action:**
Add business logic directly to page component

**Violation:**
Tier 0 Rule: Architecture Preservation - Follow existing separation patterns

**Why This Matters:**
- Violates existing service layer pattern
- Makes testing harder
- Creates technical debt
- Breaks component isolation

**Recommended Alternative:**
Based on existing architecture:
1. Create PdfExportService.cs in Services/
2. Inject into page via DI (existing pattern)
3. Page component calls service (thin UI layer)

**Override:**
Type "OVERRIDE: [reason]" to proceed with monolithic implementation.
```

### Example 3: BRAIN Integrity
```markdown
User: "Just manually edit knowledge-graph.yaml to add the pattern"

Agent Response:
⚠️ **CHALLENGE - BRAIN Integrity Violation**

**Proposed Action:**
Manually edit knowledge-graph.yaml

**Violation:**
Tier 0 Rule: BRAIN Integrity - Updates through proper channels only

**Why This Matters:**
- Bypasses confidence scoring
- Can corrupt BRAIN structure
- Breaks automatic learning
- No validation applied

**Recommended Alternative:**
1. Log event to events.jsonl (proper channel)
2. Run brain-updater.md to process event
3. Pattern added with correct confidence score
4. BRAIN structure validated

**Override:**
Type "OVERRIDE: [reason]" to manually edit BRAIN files.
```

---

## 📊 Challenge Metrics

Track challenge effectiveness:
```yaml
challenge_metrics:
  total_challenges_issued: int
  overrides_granted: int
  recommendations_accepted: int
  most_common_violations:
    - TDD_WORKFLOW: count
    - ARCHITECTURE: count
    - BRAIN_INTEGRITY: count
  override_outcomes:
    successful: int  # Override didn't cause problems
    problematic: int  # Override led to issues
```

---

## 🔄 Review Process

### Weekly Review:
- Check `governance/challenges.jsonl`
- Identify patterns in violations
- Update guidance if common confusions
- Improve challenge messaging

### If Override Rate > 30%:
- Review if rule is too strict
- Consider adding exceptions
- Improve education/docs
- Reassess rule priority

---

## ✅ Success Criteria

Rule #18 is working when:
- ✅ 90%+ of TDD violations are challenged
- ✅ Users understand WHY rules exist
- ✅ Override rate < 20%
- ✅ Overridden changes flagged for review
- ✅ Challenge log shows learning trend (fewer violations over time)

---

## 🚫 What NOT to Challenge

Don't over-challenge! These are OK:

✅ User experimenting in sandbox/test area  
✅ User explicitly prototyping ("spike solution")  
✅ User has domain expertise (e.g., "Trust me, this pattern works")  
✅ Emergency fixes (documented technical debt)  
✅ Iterative approach (tests exist, adding more features)

**Use judgment:** Challenge protects quality, not blocks productivity.

---

**Status:** Active - All agents must implement  
**Review Date:** End of Week 1 (validate challenges working)  
**Owner:** All KDS specialist agents  
**Enforcement:** Automatic challenge system + manual override option

---

## 🔗 Related Rules

- Rule #1: TDD Workflow (test-first mandatory)
- Rule #5: SOLID Principles (single responsibility)
- Rule #11: BRAIN Integrity (automated updates only)
- Rule #16: Health Validation (checks required before commit)

---

**This is a TIER 0 rule - it governs how all other rules are enforced.**
