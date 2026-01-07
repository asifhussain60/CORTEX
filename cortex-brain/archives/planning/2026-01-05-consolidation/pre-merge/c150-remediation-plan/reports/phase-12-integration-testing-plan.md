# Phase 12: GitHub Copilot Integration Testing

**Date:** January 4, 2026  
**Plan:** C150 Remediation Plan  
**Status:** 🔄 IN PROGRESS

## Test Objective

Validate that all 5 operational orchestrators (Planning v5, ADO v2, Sanitization v2, Cleanup v2, Vacuum v2) are correctly integrated with GitHub Copilot's Master Orchestrator routing system via `.github/prompts/CORTEX.prompt.md`.

## Test Environment

- **Routing File:** `.github/prompts/CORTEX.prompt.md` (v5.1.0)
- **Master Orchestrator:** GitHub Copilot (LLM proxy mode)
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Orchestrator Registry:** `cortex-brain/config/orchestrator-registry.json`

## Routing Table (from CORTEX.prompt.md)

| Pattern (Regex) | Orchestrator | Priority | Mode | Status |
|-----------------|--------------|----------|------|--------|
| `^(plan\|create a plan\|make a plan)` | Planning v5 | 10 | autonomous | ✅ REGISTERED |
| `^(ado\|ado story\|ado feature\|azure devops)` | ADO v2 | 30 | auto | ✅ REGISTERED |
| `^(sanitize\|anonymize\|redact\|remove sensitive)` | Sanitization v2 | 40 | autonomous | ✅ REGISTERED |
| `^(cleanup\|cleanup cache\|cleanup logs\|cleanup artifacts)` | Cleanup v2 | 55 | selective | ✅ REGISTERED |
| `^(vacuum\|deep clean\|organize files)` | Vacuum v2 | 45 | autonomous | ✅ REGISTERED |

## Test Cases

### Test Suite 1: Intent Pattern Matching

#### Test 1.1: Planning v5 - "plan" Pattern
**Input:** `plan user authentication system`  
**Expected Match:** Planning v5  
**Priority:** 10 (highest)  
**Confidence:** 1.0 (exact pattern match)

**Routing Expectations:**
- Pattern matched: `^(plan|create a plan|make a plan)`
- Orchestrator: PlanningOrchestratorV5
- Mode: autonomous
- Hand-off header: `## 🛡️🧠 CORTEX Planning v5 Execution`
- Response template: `autonomous_execution_progress`
- GitHub Copilot should STOP after routing

**Validation Checklist:**
- [ ] Pattern matches correctly
- [ ] Orchestrator identified as Planning v5
- [ ] Hand-off header includes 🛡️ shield icon
- [ ] Transformation adds domain context (security, database, API)
- [ ] Routing message references response template
- [ ] GitHub Copilot stops after routing (no implementation)

---

#### Test 1.2: Planning v5 - "create a plan" Pattern
**Input:** `create a plan for multi-tenant SaaS`  
**Expected Match:** Planning v5  
**Validation:** Same as Test 1.1

---

#### Test 1.3: Planning v5 - "make a plan" Pattern
**Input:** `make a plan API rate limiting`  
**Expected Match:** Planning v5  
**Validation:** Same as Test 1.1

---

#### Test 1.4: ADO v2 - "ado story" Pattern
**Input:** `ado story implement user registration`  
**Expected Match:** ADO v2  
**Priority:** 30  
**Mode:** auto

**Routing Expectations:**
- Pattern matched: `^(ado|ado story|ado feature|azure devops)`
- Orchestrator: ADOOrchestratorV2
- Hand-off header: `## 🛡️🧠 CORTEX ADO v2 Execution`
- Transformation includes work item hierarchy (Epic → Feature → Story → Task)

**Validation Checklist:**
- [ ] Pattern matches correctly
- [ ] Orchestrator identified as ADO v2
- [ ] Mode set to "auto" (not "wizard")
- [ ] Transformation mentions work item types
- [ ] Story point estimation referenced
- [ ] GitHub Copilot stops after routing

---

#### Test 1.5: ADO v2 - "ado feature" Pattern
**Input:** `ado feature payment integration`  
**Expected Match:** ADO v2  
**Validation:** Same as Test 1.4

---

#### Test 1.6: Sanitization v2 - "sanitize" Pattern
**Input:** `sanitize codebase remove API keys`  
**Expected Match:** Sanitization v2  
**Priority:** 40  
**Mode:** autonomous

**Routing Expectations:**
- Pattern matched: `^(sanitize|anonymize|redact|remove sensitive)`
- Orchestrator: SanitizationOrchestratorV2
- Hand-off header: `## 🛡️🧠 CORTEX Sanitization v2 Execution`
- Transformation includes PII types (API keys, passwords, tokens)

**Validation Checklist:**
- [ ] Pattern matches correctly
- [ ] Orchestrator identified as Sanitization v2
- [ ] Transformation mentions PII/secret detection
- [ ] Mapping preservation referenced
- [ ] Dry-run mode mentioned
- [ ] GitHub Copilot stops after routing

---

#### Test 1.7: Cleanup v2 - "cleanup cache" Pattern
**Input:** `cleanup cache and logs`  
**Expected Match:** Cleanup v2  
**Priority:** 55  
**Mode:** selective

**Routing Expectations:**
- Pattern matched: `^(cleanup|cleanup cache|cleanup logs)`
- Orchestrator: CleanupOrchestratorV2
- Hand-off header: `## 🛡️🧠 CORTEX Cleanup v2 Execution`
- Transformation includes safety validation

**Validation Checklist:**
- [ ] Pattern matches correctly
- [ ] Orchestrator identified as Cleanup v2
- [ ] Mode set to "selective"
- [ ] Safety validation referenced
- [ ] Rollback support mentioned
- [ ] GitHub Copilot stops after routing

---

#### Test 1.8: Vacuum v2 - "vacuum" Pattern
**Input:** `vacuum reorganize project files`  
**Expected Match:** Vacuum v2  
**Priority:** 45  
**Mode:** autonomous

**Routing Expectations:**
- Pattern matched: `^(vacuum|deep clean|organize files)`
- Orchestrator: VacuumOrchestratorV2
- Hand-off header: `## 🛡️🧠 CORTEX Vacuum v2 Execution`
- Transformation includes archival strategy

**Validation Checklist:**
- [ ] Pattern matches correctly
- [ ] Orchestrator identified as Vacuum v2
- [ ] Deep file reorganization referenced
- [ ] Safety validation mentioned
- [ ] Archive support referenced
- [ ] GitHub Copilot stops after routing

---

### Test Suite 2: Request Transformation Quality

#### Test 2.1: Context Enrichment
**Input:** `plan user auth`  
**Expected Transformation:**
- ✅ Security context (OAuth2, JWT, session management)
- ✅ Database context (users table, roles, permissions)
- ✅ API context (login, logout, refresh endpoints)
- ✅ Testing context (unit, integration, security tests)

**Validation:**
- [ ] Raw input transformed (not passed directly)
- [ ] Domain knowledge injected
- [ ] Implicit requirements extracted
- [ ] Cross-cutting concerns identified

---

#### Test 2.2: Artifact Specification
**Input:** `plan payment gateway`  
**Expected Transformation:**
- ✅ Expected artifacts listed (folders, files, reports)
- ✅ Integration points identified (Stripe, PayPal, etc.)
- ✅ Security requirements (PCI-DSS compliance)
- ✅ Testing requirements (sandbox mode, test cards)

**Validation:**
- [ ] Artifacts clearly specified
- [ ] Integration complexity acknowledged
- [ ] Compliance requirements mentioned
- [ ] Testing strategy outlined

---

### Test Suite 3: Hand-Off Protocol Compliance

#### Test 3.1: Shield Icon Display
**Requirement:** All autonomous orchestrator responses MUST include 🛡️ shield icon in header

**Test Cases:**
- Planning v5: `## 🛡️🧠 CORTEX Planning v5 Execution`
- ADO v2: `## 🛡️🧠 CORTEX ADO v2 Execution`
- Sanitization v2: `## 🛡️🧠 CORTEX Sanitization v2 Execution`
- Cleanup v2: `## 🛡️🧠 CORTEX Cleanup v2 Execution`
- Vacuum v2: `## 🛡️🧠 CORTEX Vacuum v2 Execution`

**Validation:**
- [ ] Shield icon present in all responses
- [ ] Format matches template: `## 🛡️🧠 CORTEX {Name}`
- [ ] Icon visible to user (not rendered as Unicode placeholder)

---

#### Test 3.2: GitHub Copilot Stop Point
**Requirement:** After displaying routing message, GitHub Copilot MUST NOT:
- Execute tasks itself
- Provide implementation guidance
- Continue conversation
- Read manifest files

**Test:** After routing message, verify no additional content follows

**Validation:**
- [ ] Routing message is final output
- [ ] No implementation steps provided
- [ ] No code generation after routing
- [ ] No "Next steps" section (orchestrator handles this)

---

#### Test 3.3: Response Template Reference
**Requirement:** Routing message MUST reference correct response template

**Expected Templates:**
- Planning v5: `autonomous_execution_progress`
- ADO v2: `autonomous_execution_progress`
- Sanitization v2: `autonomous_execution_progress`
- Cleanup v2: `autonomous_execution_progress`
- Vacuum v2: `autonomous_execution_progress`

**Validation:**
- [ ] Template name included in routing message
- [ ] Template path correct: `cortex-brain/response-templates-v4.yaml`
- [ ] Template exists at specified location

---

### Test Suite 4: Edge Cases

#### Test 4.1: Ambiguous Input
**Input:** `clean` (could match "cleanup" or "deep clean" patterns)  
**Expected:** Priority-based resolution (Cleanup v2 wins: priority 55 > Vacuum v2 priority 45)

**Validation:**
- [ ] Higher priority orchestrator selected
- [ ] Confidence score reflects ambiguity
- [ ] User not confused by routing choice

---

#### Test 4.2: No Pattern Match
**Input:** `optimize database queries`  
**Expected:** LLM classification fallback (no exact pattern match)

**Validation:**
- [ ] Fallback mechanism triggered
- [ ] Best-effort orchestrator selection
- [ ] Confidence score < 1.0 (indicates inference)
- [ ] User informed of classification method

---

#### Test 4.3: Multiple Orchestrator Relevance
**Input:** `plan and implement ADO stories for cleanup feature`  
**Expected:** Planning v5 wins (priority 10 highest)

**Validation:**
- [ ] Highest priority pattern matched first
- [ ] Other patterns ignored
- [ ] PLANNING_ISOLATION rule enforced (plan only, no implementation)

---

### Test Suite 5: SKULL Rules Enforcement

#### Test 5.1: PLANNING_ISOLATION
**Input:** `plan and implement user authentication`  
**Expected:** Planning v5 creates plan structure ONLY (no implementation)

**Validation:**
- [ ] Planning orchestrator invoked
- [ ] Implementation keywords ignored
- [ ] User informed plan is first step (not implementation)

---

#### Test 5.2: HAND_OFF_PROTOCOL
**Input:** Any autonomous orchestrator pattern  
**Expected:** GitHub Copilot transforms, routes, and STOPS

**Validation:**
- [ ] Transformation performed
- [ ] Routing message displayed
- [ ] GitHub Copilot stops (no further action)
- [ ] Python orchestrator takes over

---

#### Test 5.3: AUTONOMOUS_ONLY
**Requirement:** NO manual orchestration by GitHub Copilot  
**Expected:** All orchestrators execute via Python, not Copilot

**Validation:**
- [ ] No step-by-step implementation by Copilot
- [ ] No file creation by Copilot
- [ ] Routing message confirms autonomous execution

---

## Test Execution Log

### Planning v5 Tests

**Test 1.1:** ⏳ PENDING  
**Test 1.2:** ⏳ PENDING  
**Test 1.3:** ⏳ PENDING

### ADO v2 Tests

**Test 1.4:** ⏳ PENDING  
**Test 1.5:** ⏳ PENDING

### Sanitization v2 Tests

**Test 1.6:** ⏳ PENDING

### Cleanup v2 Tests

**Test 1.7:** ⏳ PENDING

### Vacuum v2 Tests

**Test 1.8:** ⏳ PENDING

### Transformation Tests

**Test 2.1:** ⏳ PENDING  
**Test 2.2:** ⏳ PENDING

### Hand-Off Protocol Tests

**Test 3.1:** ⏳ PENDING  
**Test 3.2:** ⏳ PENDING  
**Test 3.3:** ⏳ PENDING

### Edge Case Tests

**Test 4.1:** ⏳ PENDING  
**Test 4.2:** ⏳ PENDING  
**Test 4.3:** ⏳ PENDING

### SKULL Rules Tests

**Test 5.1:** ⏳ PENDING  
**Test 5.2:** ⏳ PENDING  
**Test 5.3:** ⏳ PENDING

---

## Issues Found

*(To be populated during testing)*

---

## Recommendations

*(To be populated after testing)*

---

## Summary

**Total Test Cases:** 21  
**Executed:** 0  
**Passed:** 0  
**Failed:** 0  
**Blocked:** 0

**Status:** Test plan created, awaiting execution

---

*Generated by C150 Remediation Plan - Phase 12*  
*Test plan created: January 4, 2026*  
*Next: Execute tests via GitHub Copilot chat*
