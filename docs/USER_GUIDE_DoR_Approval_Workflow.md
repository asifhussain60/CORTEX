# 📖 User Guide: DoR Approval Workflow

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Understanding Markdown Reflections](#understanding-markdown-reflections)
4. [Approval States & Decisions](#approval-states--decisions)
5. [The Modification Workflow](#the-modification-workflow)
6. [Multi-Turn Conversations](#multi-turn-conversations)
7. [Best Practices](#best-practices)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Degree of Reflection (DoR) Approval Workflow** is a governance framework that ensures all operations go through proper classification and user approval before execution. It provides:

- **Intent Classification:** Automatic analysis of what you're asking the system to do
- **User Approval:** Clear markdown display for informed decision-making
- **Execution Gating:** Only approved operations proceed
- **Audit Trail:** Complete logging of all decisions

### Why This Matters

Before the DoR Workflow, operations might execute without proper review. Now:
- ✅ Every operation is classified (what type? scope? impact?)
- ✅ Users see clear markdown reflecting the system's understanding
- ✅ Users explicitly approve, reject, or request modifications
- ✅ Execution only happens after approval

---

## Core Concepts

### 1. Intent Classification

When you submit a request, the system classifies it into one of three types:

| Intent Type | Use Case | Example |
|-------------|----------|---------|
| **IMPLEMENT** | Add new functionality | "Add caching to database queries" |
| **FIX** | Resolve existing issues | "Fix timeout in authentication" |
| **REFACTOR** | Improve existing code | "Reorganize payment module structure" |

### 2. Scope Levels

The system identifies how much code/impact is affected:

| Scope | Impact | Example |
|-------|--------|---------|
| **FILE** | Single file only | Updating utility function |
| **MODULE** | Multiple related files | Changes to auth module |
| **DOMAIN** | Cross-module impact | Changes affecting payment processing |
| **SYSTEM** | Entire application | Database schema changes |

### 3. Confidence Score

The system rates how confident it is in its classification:

```
0.0 --------|---------- 1.0
Low Confidence          High Confidence
(Review carefully)      (Likely correct)
```

### 4. Approval States

Every request goes through a state machine:

```
PENDING ──→ APPROVED ──→ Execute
  ├─────→ REJECTED ──→ Blocked
  └─────→ MODIFIED ──→ Re-classify
```

---

## Understanding Markdown Reflections

When you submit a request, the system responds with a **Markdown Reflection** - a structured document showing its understanding of your request.

### Example Markdown Reflection

```markdown
# Intent Reflection

## Request
"Fix the database timeout issue in the user authentication flow"

## Classification

### Intent Type
**INTENT:** FIX  
**Confidence:** 0.92

### Scope
**SCOPE:** DOMAIN  
**Reason:** Changes affect authentication domain and database layer

### Target Handler
**MODULE:** `cortex.core.auth.db_handler`  
**RESPONSIBILITY:** Manages database connections and timeouts

## Governance Rules

The following CORE governance rules will be applied:

1. **CORE-008: Test-Driven Development**
   - All changes require passing unit tests
   - Coverage must be ≥ 80%

2. **CORE-011: Type Hints**
   - All function signatures must include type hints
   - No `Any` type except with documented justification

3. **CORE-032: Mandatory Intent Classification**
   - This request has been classified as: FIX
   - Classification is mandatory for execution

4. **AC-AUDIT-TRAIL: Complete Logging**
   - All decisions will be logged with timestamps
   - Modification chain will be tracked

## Estimated Impact

- **Files Affected:** 3-5 files
- **Test Coverage Required:** New tests for timeout handling
- **Breaking Changes:** None expected
- **Rollback Complexity:** Medium

## Questions for Clarification

- Should we implement exponential backoff for retries?
- What's the acceptable timeout threshold (current: 30s)?
- Should we add monitoring/alerting for timeout events?

---

## Your Options

1. **APPROVE** ✅ Proceed with this classification and execute
2. **REJECT** ❌ Block this operation - request not approved
3. **MODIFY** ✏️ Clarify your request - system will re-classify
```

### Key Sections Explained

| Section | What It Means | Why It Matters |
|---------|--------------|----------------|
| **Request** | Echo of what you asked | Verify system understood you correctly |
| **Intent Type** | IMPLEMENT / FIX / REFACTOR | Determines which rules apply |
| **Confidence** | 0.0-1.0 score | Low confidence (< 0.7) = review carefully |
| **Scope** | FILE / MODULE / DOMAIN / SYSTEM | Shows impact magnitude |
| **Target Handler** | Module that will execute | Where the work happens |
| **Governance Rules** | CORE-### rules | What standards will be enforced |
| **Estimated Impact** | Files, tests, breaking changes | What to expect |
| **Questions** | Clarifications needed | Answer to refine classification |

### How to Read Confidence Scores

```
Confidence: 0.95 → System is very confident → Usually safe to approve
Confidence: 0.78 → System is fairly confident → Review carefully
Confidence: 0.62 → System is uncertain → Use MODIFY for clarification
```

---

## Approval States & Decisions

### State 1: PENDING ⏳

**What it means:** System awaits your decision

**Your options:**
- ✅ **APPROVE** - System got it right, proceed
- ❌ **REJECT** - Not the right time/approach, block it
- ✏️ **MODIFY** - I need to clarify my request

### State 2: APPROVED ✅

**What it means:** You've said "yes", operation can execute

**What happens:**
- Operation proceeds immediately
- All governance rules are enforced
- Audit trail records the approval
- Tests run before actual changes

**Example:**
```
User: "Fix the timeout issue"
System: [Shows markdown reflection]
User: "Looks good" → APPROVE
System: [Runs tests, applies fix, logs decision]
```

### State 3: REJECTED ❌

**What it means:** You've said "no", operation is blocked

**When to reject:**
- Confidence score is too low (< 0.70)
- Wrong intent detected (system thought FIX, you meant IMPLEMENT)
- Not the right time for this change
- Wrong scope detected

**Example:**
```
User: "Refactor payment module"
System: [Shows it classified as DOMAIN-wide change affecting 12 files]
User: "That's too broad" → REJECT
System: [Operation blocked, no changes applied]
```

### State 4: MODIFIED ✏️

**What it means:** You want to clarify/rephrase your request

**When to modify:**
- System misunderstood your request
- Confidence score is moderate (0.65-0.80)
- You want to add context/constraints
- You need to reduce or expand scope

**What happens:**
1. You provide new/clarified request
2. System re-classifies with new information
3. New markdown reflection shown
4. You make new decision (approve/reject/modify again)

**Example:**
```
User: "Add feature"
System: [Shows IMPLEMENT with 0.65 confidence, unclear scope]
User: MODIFY → "Add caching layer specifically to user_lookup function"
System: [Re-classifies as IMPLEMENT, FILE scope, 0.94 confidence]
User: [Reviews updated reflection] → APPROVE
```

---

## The Modification Workflow

### Why Modify?

Use MODIFY when system confidence is low or understanding is unclear.

### Step-by-Step Modification Flow

#### Step 1: Review the Reflection
```
System shows: FIX, DOMAIN scope, 0.62 confidence
→ Moderate confidence, not clear enough
```

#### Step 2: Submit Clarification
```
Original: "Fix the payment issue"
Modified: "Fix the payment processing error that occurs 
          when invoice amount is > $10,000 - specifically 
          in the tax calculation step"
```

#### Step 3: Review New Reflection
```
System now shows: FIX, MODULE scope, 0.89 confidence
→ Much clearer! Shows specific file affected.
```

#### Step 4: Make Final Decision
```
Now confident → APPROVE
```

### Modification Tips

| Tip | Example | Result |
|-----|---------|--------|
| **Be specific** | "Fix login timeout" vs "Fix timeout in auth flow when login takes > 30s" | Higher confidence |
| **Mention scope limits** | "Only modify cache.py, don't touch database layer" | Narrower scope |
| **Add constraints** | "Implement with < 5ms overhead, use Redis only" | Better targeting |
| **Reference related issues** | "Fix from issue #234 reported by Alice" | More context |

---

## Multi-Turn Conversations

### Single-Turn Workflow
```
Turn 1: 
  - User: [Request]
  - System: [Shows markdown]
  - User: APPROVE
  - System: [Executes]
```

### Multi-Turn Workflow
```
Turn 1:
  - User: [Request]
  - System: [Shows markdown, confidence = 0.65]
  - User: MODIFY (not approved yet)

Turn 2:
  - User: [Clarified request]
  - System: [Re-classifies, confidence = 0.88]
  - User: APPROVE (decision stored)

Turn 3:
  - User: [Different request]
  - System: [New classification]
  - User: REJECT

Turn 4:
  - User: [Back to original]: "What was the status of that first request?"
  - System: [Shows APPROVED state from Turn 2]
  - User: "Execute that" → System proceeds with Turn 2's operation
```

### Key Multi-Turn Features

| Feature | What It Does |
|---------|--------------|
| **State Persistence** | APPROVED decision stays valid across turns |
| **Context Preservation** | Classification info survives multiple requests |
| **Reset Available** | Start fresh workflow when needed |
| **Modification Chain** | Track original → modified → final request |

### When State Persists

- ✅ APPROVED state remains valid
- ✅ Context available for later queries
- ✅ Audit trail tracks all decisions
- ❌ PENDING state requires new decision each turn
- ❌ REJECTED state blocks unless reversed

### Resetting State

When starting completely new work, reset to clear previous state:

```
User: "Clear the approval state for new work"
System: [State reset, PENDING]
User: [New request] → Fresh classification
```

---

## Best Practices

### 1. Review Confidence Scores

```
✅ 0.90-1.00 → Approve confidently
⚠️  0.70-0.89 → Review carefully before approving
🔄 0.60-0.69 → Consider MODIFY for clarification
❌ < 0.60   → MODIFY or REJECT
```

### 2. Check the Scope

```
FILE scope   → Safe, limited impact
MODULE scope → Review related files
DOMAIN scope → Careful, affects multiple areas
SYSTEM scope → Very careful, full app impact
```

### 3. Understand Governance Rules

Before approving, check which CORE rules apply:

- **CORE-008 (TDD):** Will need tests - expect longer implementation
- **CORE-011 (Type Hints):** All functions must be typed
- **CORE-012 (Docstrings):** All functions must be documented
- **CORE-032 (Intent Classification):** Always required
- **AC-AUDIT-TRAIL:** Decisions logged - you can see history

### 4. Know When to Modify

| Situation | Action |
|-----------|--------|
| Confidence < 0.70 | Modify for clarification |
| Wrong intent detected | Modify to correct |
| Scope too broad | Modify to narrow it |
| Missing context | Modify to add details |
| Confidence 0.70+ but unsure | Review rules, then decide |

### 5. Use Clear Language

**❌ Poor:** "Update stuff"  
**✅ Good:** "Update cache invalidation in product search module to use TTL approach"

**❌ Poor:** "Fix issues"  
**✅ Good:** "Fix memory leak in WebSocket connection handler - specifically in cleanup_on_disconnect"

### 6. Leverage Multi-Turn

```
Turn 1: Complex request → Low confidence → MODIFY
Turn 2: Clarified request → High confidence → APPROVE
Turn 3: Different work → New classification
Turn 4: Reference Turn 2 result → Execute previous approved work
```

---

## Common Workflows

### Workflow 1: Quick Approval

```
1. User submits request
2. System shows markdown with 0.92 confidence
3. User reviews: Looks correct!
4. User: APPROVE
5. System: Executes immediately
```

**When to use:** High-confidence requests, clear scope

---

### Workflow 2: Clarification Needed

```
1. User: "Fix payment bug"
2. System: FIX, 0.65 confidence, DOMAIN scope
3. User thinks: Confidence too low
4. User: MODIFY → "Fix the NPE in tax_calculator when 
                    state_code is empty"
5. System: FIX, 0.91 confidence, MODULE scope
6. User: APPROVE
7. System: Executes
```

**When to use:** Moderate confidence or unclear scope

---

### Workflow 3: Rejection + Retry

```
1. User: "Refactor authentication"
2. System: REFACTOR, 0.78 confidence, DOMAIN scope
3. User thinks: Too broad, affecting too much
4. User: REJECT
5. Later, User: "Refactor password validation function only"
6. System: REFACTOR, 0.89 confidence, FILE scope
7. User: APPROVE
8. System: Executes
```

**When to use:** First attempt was too broad

---

### Workflow 4: Multi-Turn with Context

```
Turn 1:
  User: "Add monitoring"
  System: IMPLEMENT, 0.67 confidence, needs clarification
  User: MODIFY

Turn 2:
  User: "Add metrics collection to payment processor"
  System: IMPLEMENT, 0.88 confidence, MODULE scope
  User: APPROVE ✓

Turn 3:
  User: "What else needs monitoring?"
  System: [Suggests areas, references Turn 2 APPROVED state]
  User: [Uses Turn 2's decision as context for Turn 3 work]

Turn 4:
  User: "Execute the approved payment monitoring from Turn 2"
  System: [Executes because Turn 2 is APPROVED]
```

**When to use:** Complex features requiring multiple decisions

---

## Troubleshooting

### Problem: Low Confidence Score

**Symptom:** System shows confidence < 0.65

**Solution:**
1. Review what system understood
2. Use MODIFY to add context
3. Be more specific in request
4. Example:
   ```
   Before: "Improve performance"
   After: "Improve payment_processor.validate() response time 
           from 500ms to < 100ms using caching"
   ```

**Result:** Confidence usually jumps to 0.85+

---

### Problem: Wrong Intent Detected

**Symptom:** System classified as FIX but you meant IMPLEMENT

**Solution:**
1. Don't approve - instincts are usually right
2. Use REJECT or MODIFY
3. In modification, explicitly state intent:
   ```
   "Actually this is IMPLEMENT - we're adding new 
    retry_with_backoff feature, not fixing existing code"
   ```
4. System re-classifies correctly

---

### Problem: Scope Too Broad

**Symptom:** System shows DOMAIN or SYSTEM scope when you expected FILE

**Solution:**
1. Use MODIFY to narrow scope
2. Add specific file/function names:
   ```
   Before: "Refactor error handling"
   After: "Refactor error handling in cache.py 
           specifically the CacheError class"
   ```
3. Results usually change from DOMAIN to MODULE or FILE

---

### Problem: Can't Decide (PENDING State)

**Symptom:** Markdown reflection exists but you're unsure

**Solution:**
1. **Ask for clarification:** Use MODIFY to ask system questions
2. **Check governance rules:** See which CORE rules apply
3. **Review risk:** Check "Estimated Impact" section
4. **Consult others:** If unsure, discuss before approving
5. **Start smaller:** MODIFY to reduce scope if needed

---

### Problem: Execution Failed After Approval

**Symptom:** You approved but execution encountered error

**Solution:**
1. Check audit trail for error details
2. Review governance rules enforcement
3. System will log specific failure reason
4. For retry:
   - Fix underlying issue
   - State resets to PENDING
   - Re-submit request
   - System re-classifies

---

### Problem: Lost Track of Multi-Turn State

**Symptom:** Multiple turns, unsure what's APPROVED vs PENDING

**Solution:**
1. Ask system: "What decisions have been made?"
2. System displays all turn states and decisions
3. Use explicit reset if starting new work:
   ```
   "Reset state for new workflow"
   System: [Clears state, ready for new requests]
   ```

---

## FAQ

### Q: What if I approve but then change my mind?

**A:** If execution hasn't started, system can be interrupted. If execution started, audit trail shows decision. For future decisions, REJECT or MODIFY. Next time, clarify before approving.

### Q: Does my approval expire?

**A:** No. APPROVED state remains valid across turns until:
- New request supersedes it
- You explicitly reset state
- System detects significant change in context

### Q: Can I see why system classified something a certain way?

**A:** Yes! Markdown reflection explains:
- Intent type chosen
- Scope reasoning
- Confidence score basis
- Governance rules applied
- Target handler identified

### Q: What if I make a mistake in my modification?

**A:** No problem!
1. Use MODIFY again with clearer request
2. System re-classifies with new information
3. You can change decision (approve/reject/modify again)
4. Audit trail tracks all versions

### Q: How long does classification take?

**A:** < 100ms typically. Fast enough for real-time interaction.

### Q: Can state be shared between users?

**A:** No. Each user has separate approval state. Multi-user workflows require explicit coordination through your request text.

### Q: What happens if governance rules conflict?

**A:** All rules are designed to work together (verified by CORE-032 governance validation). System enforces all applicable rules without conflict.

---

## Key Takeaways

✅ **Every operation is classified** before execution  
✅ **Markdown reflections show system's understanding** - review them  
✅ **Three decisions available:** APPROVE, REJECT, MODIFY  
✅ **Confidence scores guide your decision** - < 0.70? Use MODIFY  
✅ **State persists across turns** - enable complex workflows  
✅ **Modification clarifies scope** - use for low-confidence requests  
✅ **Audit trail tracks everything** - transparency & accountability  
✅ **Governance rules apply** - quality assurance built-in  

---

## Quick Reference Card

| Need | Do This |
|------|---------|
| Approve quickly | High confidence + clear scope → APPROVE |
| Understand better | Low confidence → MODIFY with more details |
| Too broad | DOMAIN/SYSTEM scope → REJECT or MODIFY narrower |
| Change decision | Can MODIFY anytime before execution |
| Continue later | APPROVED state persists across turns |
| Start fresh | Reset state for new workflow |
| Understand rules | Check markdown "Governance Rules" section |
| See history | Audit trail shows all decisions + timestamps |

---

## Support & Examples

For more information:
- **Architecture Guide:** `ARCHITECTURE_DoR_Approval_System.md`
- **Test Examples:** `tests/unit/orchestrators/core/test_master_orchestrator_e2e_dor_workflow.py`
- **Troubleshooting:** `OPERATIONS_DoR_Approval_System.md`

---

**Last Updated:** January 24, 2026  
**Status:** Production Ready ✅
