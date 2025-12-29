# ADO Operations User Guide

**Version:** 1.0  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Last Updated:** December 25, 2025  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

**ADO Operations** is CORTEX's Azure DevOps integration that creates professional work items (Stories, Features, Tasks, Bugs, Epics) with automatic DoR/DoD enforcement, Planning System integration, and ADO-formatted markdown ready for copy-paste.

**Key Innovation:** File-based workflow with automatic quality gates - work items can't start until ready (DoR) and can't complete until done (DoD), ensuring consistent quality across your ADO backlog.

---

## 🚀 Quick Start

### Create a User Story

```bash
# In Copilot Chat or terminal
plan ado story add user authentication
```

**What happens:**
1. **Planning System Analysis** - Complexity classification (authentication → Tier 3 HIGH)
2. **DoR Validation** - Checks 10 readiness criteria
3. **Work Item Generation** - Creates ADO-formatted markdown
4. **File Storage** - Saves to `cortex-brain/documents/ado/active/`

**Output:** `add-user-authentication-story.md` ready to copy-paste into Azure DevOps

---

### Create a Feature

```bash
# Feature wraps multiple stories
plan ado feature payment integration
```

**Creates:**
- 1 Feature work item
- 3-5 child Stories (auto-generated from complexity analysis)
- Parent-child relationships documented
- Fibonacci story point estimation (hours → story points)

---

### Complete Work Item with DoD

```bash
# Mark work complete with DoD validation
ado complete add-user-authentication-story
```

**What happens:**
1. **DoD Validation** - Checks 10 completion criteria
2. **Generate Summary** - Creates completion report with metrics
3. **Move File** - Transitions to `cortex-brain/documents/ado/completed/`
4. **Update Links** - Marks parent Feature progress

---

## 📋 Work Item Types

### 1. User Story

**Purpose:** User-facing functionality (1-3 days of work)

**Command:**
```bash
plan ado story <description>
```

**Example:**
```bash
plan ado story add email validation to registration form
```

**Generated Work Item:**
```markdown
# User Story: Add Email Validation to Registration Form

**Work Item Type:** User Story  
**State:** New  
**Priority:** 2  
**Story Points:** 5  
**Assigned To:** Unassigned

---

## Description

As a user, I want email validation on the registration form so that only valid email addresses are accepted.

---

## Acceptance Criteria

- [ ] Email validation runs on form submission
- [ ] Invalid emails show error message ("Please enter a valid email")
- [ ] Valid emails (user@example.com) are accepted
- [ ] Edge cases handled (special characters, internationalized domains)
- [ ] Validation is client-side AND server-side

---

## Technical Details

**Complexity:** Tier 2 (MEDIUM)  
**Keywords:** validation (1.0), form (0.5)  
**Estimated Hours:** 16 hours

**Implementation:**
- Phase 1: Setup (4h) - Install validation library, configure rules
- Phase 2: Implementation (8h) - Client + server validation
- Phase 3: Testing (4h) - Unit + integration tests

---

## DoR Checklist (Definition of Ready)

### Completeness
- [x] Title length: 10-100 characters ✅
- [x] Description depth: 50+ words ✅
- [x] Acceptance criteria: 3+ items ✅

### Quality
- [x] Tags present: validation, form, registration ✅
- [x] Dependencies identified: email-validator library ✅
- [x] Testability: Clear test scenarios ✅

### Prioritization
- [x] Priority assigned: 2 (High) ✅
- [x] Story points estimated: 5 points ✅
- [x] Sprint assigned: Current sprint ✅
- [x] Parent feature linked: User Registration (ID: 12345) ✅

**DoR Status:** ✅ READY (10/10 criteria met)

---

## DoD Checklist (Definition of Done)

### Implementation
- [ ] All acceptance criteria verified
- [ ] All unit tests passing (≥80% coverage)
- [ ] All integration tests passing
- [ ] Code review completed and approved

### Quality
- [ ] No critical/high security vulnerabilities
- [ ] No code smells (complexity <15)
- [ ] SOLID principles applied
- [ ] Clean architecture validated

### Documentation
- [ ] API documentation updated
- [ ] User documentation updated

### Deployment
- [ ] Deployed to staging environment
- [ ] Performance benchmarks met (validation <100ms)

**DoD Status:** ⏸️ PENDING (0/10 criteria met)
```

**Story Points Conversion:**
- 1-8 hours → 1 point (Simple)
- 9-16 hours → 3 points (Small)
- 17-24 hours → 5 points (Medium)
- 25-40 hours → 8 points (Large)
- 40+ hours → 13+ points (Too large, split into multiple stories)

---

### 2. Feature

**Purpose:** Group of related stories (1-2 weeks of work)

**Command:**
```bash
plan ado feature <description>
```

**Example:**
```bash
plan ado feature payment integration with Stripe
```

**Generated Work Item:**
```markdown
# Feature: Payment Integration with Stripe

**Work Item Type:** Feature  
**State:** New  
**Priority:** 1  
**Effort:** 40 hours (8 story points)

---

## Description

Integrate Stripe payment processing to enable credit card payments, subscription management, and webhook handling.

---

## Child Stories (Auto-Generated)

### Story 1: Setup Stripe Account & Configuration
**Story Points:** 1 (6 hours)
- Create Stripe account
- Configure API keys
- Setup webhook endpoints

### Story 2: Implement Payment Flow (RED Phase)
**Story Points:** 2 (10 hours)
- Write failing tests for payment processing
- Design PaymentService interface
- Write failing integration tests

### Story 3: Make Tests Pass (GREEN Phase)
**Story Points:** 3 (14 hours)
- Implement PaymentService
- Implement StripeAdapter
- Fix failing tests

### Story 4: Refactor & Security Review
**Story Points:** 2 (10 hours)
- Apply SOLID principles
- Security hardening (PCI DSS compliance)
- Performance optimization

---

## Overall Progress

[░░░░░░░░░░] 0/4 Stories Complete (0%)

**Completion Criteria:**
- All 4 child stories completed (DoD met)
- Integration tests passing
- Security review passed
- Documentation complete
```

**Features auto-generate child stories** based on Planning System complexity analysis.

---

### 3. Task

**Purpose:** Technical work, not user-facing (hours to 1 day)

**Command:**
```bash
plan ado task <description>
```

**Example:**
```bash
plan ado task setup CI/CD pipeline for authentication service
```

**Generated Work Item:**
```markdown
# Task: Setup CI/CD Pipeline for Authentication Service

**Work Item Type:** Task  
**State:** New  
**Priority:** 2  
**Estimated Hours:** 6

---

## Description

Configure GitHub Actions pipeline with automated testing, security scanning, and deployment to staging environment.

---

## Steps

1. Create `.github/workflows/auth-service.yml`
2. Configure test job (pytest, coverage ≥80%)
3. Configure security job (Bandit, OWASP checks)
4. Configure deploy job (staging environment)
5. Test pipeline with sample commit

---

## Acceptance Criteria

- [ ] Pipeline runs on every commit to main branch
- [ ] All tests must pass before deployment
- [ ] Security scan blocks deployment on HIGH/CRITICAL issues
- [ ] Deployment to staging automated
- [ ] Pipeline execution time <5 minutes

---

## DoR/DoD

**DoR:** ✅ READY
**DoD:** ⏸️ PENDING (0/5 acceptance criteria met)
```

**Tasks are simpler:** Less DoR/DoD overhead, focus on technical acceptance criteria.

---

### 4. Bug

**Purpose:** Defect or issue (hours to 2 days)

**Command:**
```bash
plan ado bug <description>
```

**Example:**
```bash
plan ado bug login fails with special characters in password
```

**Generated Work Item:**
```markdown
# Bug: Login Fails with Special Characters in Password

**Work Item Type:** Bug  
**State:** New  
**Priority:** 1 (Critical)  
**Severity:** High

---

## Description

Users cannot log in when their password contains special characters like `@`, `#`, `$`. Error message: "Invalid credentials" (even with correct password).

---

## Steps to Reproduce

1. Register user with password containing `@` symbol (e.g., `P@ssw0rd!`)
2. Attempt to log in with same credentials
3. Observe "Invalid credentials" error

**Expected:** Login succeeds  
**Actual:** Login fails with error

---

## Technical Analysis

**Root Cause:** URL encoding issue - `@` symbol not escaped in authentication request

**Affected Code:** `src/auth/login_handler.py` line 42

**Fix:**
```python
# Before (broken)
password = request.form['password']

# After (fixed)
password = urllib.parse.quote(request.form['password'])
```

---

## DoD Checklist

- [ ] Bug reproduced locally ✅
- [ ] Root cause identified ✅
- [ ] Fix implemented
- [ ] Regression test added
- [ ] All tests passing
- [ ] Code review approved
- [ ] Deployed to production
- [ ] Verified fix in production
```

**Bugs include root cause analysis** and specific fix recommendations.

---

### 5. Epic

**Purpose:** Large initiative spanning multiple features (months)

**Command:**
```bash
plan ado epic <description>
```

**Example:**
```bash
plan ado epic modernize payment processing infrastructure
```

**Generated Work Item:**
```markdown
# Epic: Modernize Payment Processing Infrastructure

**Work Item Type:** Epic  
**State:** New  
**Priority:** 1  
**Effort:** 6 months (200+ hours)

---

## Vision

Transform legacy payment system into modern, scalable, PCI-DSS compliant infrastructure supporting multiple payment providers and currencies.

---

## Child Features (Auto-Generated)

### Feature 1: Stripe Integration (40h)
- Payment processing
- Subscription management
- Webhook handling

### Feature 2: PayPal Integration (32h)
- Express checkout
- Recurring payments
- Refund handling

### Feature 3: Multi-Currency Support (48h)
- Currency conversion
- Localized pricing
- Exchange rate management

### Feature 4: Security Hardening (40h)
- PCI DSS compliance
- Tokenization
- Fraud detection

### Feature 5: Reporting & Analytics (40h)
- Transaction dashboard
- Revenue analytics
- Chargeback tracking

---

## Overall Progress

[░░░░░░░░░░] 0/5 Features Complete (0%)

**Timeline:** Q1-Q2 2026  
**Budget:** $150K  
**ROI:** 30% revenue increase (projected)
```

**Epics provide executive-level view** with business metrics and timeline.

---

## 🔄 Work Item Lifecycle

### 1. Create (New)

```bash
plan ado story add user profile page
```

**File Location:** `cortex-brain/documents/ado/active/add-user-profile-page-story.md`  
**Status:** New  
**DoR:** Auto-validated (10 criteria checked)

---

### 2. Start Work (Active)

Work item remains in `active/` directory while in progress.

**Update progress:**
```bash
ado update add-user-profile-page-story --progress 50
```

**Adds to work item:**
```markdown
## Progress Updates

**2025-12-25 10:30 AM:** Started Phase 1 (Setup) - 0% → 25%  
**2025-12-25 14:15 PM:** Completed Phase 1, started Phase 2 (Implementation) - 25% → 50%
```

---

### 3. Block (Impediments)

```bash
ado block add-user-profile-page-story --reason "Waiting for API endpoint"
```

**File Location:** `cortex-brain/documents/ado/blocked/add-user-profile-page-story.md`  
**Status:** Blocked  
**Blocker:** Added to work item with timestamp

**Unblock:**
```bash
ado unblock add-user-profile-page-story
```

**Returns to:** `cortex-brain/documents/ado/active/`

---

### 4. Complete (Done)

```bash
ado complete add-user-profile-page-story
```

**DoD Validation:**
1. Checks 10 completion criteria
2. If any fail → Shows remediation tasks
3. If all pass → Generates completion summary
4. Moves file to `completed/` directory

**Completion Summary:**
```markdown
## ✅ Completion Summary

**Completed:** 2025-12-25 16:45 PM  
**Duration:** 3 days (24 hours actual vs 16 estimated)  
**Efficiency:** 67% (8 hours over estimate)

### DoD Validation Results

✅ **All acceptance criteria verified**  
✅ **All unit tests passing** (87% coverage, target ≥80%)  
✅ **All integration tests passing**  
✅ **Code review completed** (2 approvals: @reviewer1, @reviewer2)  
✅ **Security scan passed** (0 HIGH/CRITICAL vulnerabilities)  
✅ **Clean code validated** (avg complexity: 8.2, target <15)  
✅ **SOLID principles applied** (validated by code review)  
✅ **Clean architecture validated** (dependency rules followed)  
✅ **Documentation updated** (API docs + user guide)  
✅ **Deployed to staging** (verified by QA team)  
✅ **Performance benchmarks met** (page load <2s, target <3s)

### Lessons Learned

**What Worked Well:**
- TDD approach caught 3 bugs early
- Pair programming accelerated implementation

**Challenges:**
- API endpoint delayed start by 1 day
- Initial complexity estimate was optimistic

**Improvements for Next Time:**
- Buffer time for external dependencies
- Break down large tasks into smaller chunks
```

**File Location:** `cortex-brain/documents/ado/completed/add-user-profile-page-story.md`

---

### 5. Cancel (Abandoned)

```bash
ado cancel add-user-profile-page-story --reason "Requirements changed"
```

**File Location:** `cortex-brain/documents/ado/cancelled/add-user-profile-page-story.md`  
**Status:** Cancelled  
**Reason:** Documented in work item

---

## 📊 DoR/DoD Quality Gates

### Definition of Ready (DoR) - 10 Criteria

**Prevents work from starting until ready:**

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Title Length** | 10-100 characters | ❌ "Fix bug" → ✅ "Login fails with special characters" |
| **Description Depth** | 50+ words | ❌ "Add validation" → ✅ Full context with user impact |
| **Acceptance Criteria** | 3+ items | ❌ "Make it work" → ✅ Specific, testable criteria |
| **Tags Present** | 2+ tags | ✅ validation, form, registration |
| **Dependencies** | Identified | ✅ Requires email-validator library |
| **Testability** | Clear test scenarios | ✅ Valid emails pass, invalid emails fail |
| **Priority** | Assigned (1-4) | ✅ Priority 2 (High) |
| **Story Points** | Estimated (1,3,5,8,13) | ✅ 5 points (Medium story) |
| **Sprint** | Assigned | ✅ Sprint 42 (Dec 23-Jan 3) |
| **Parent Linked** | Feature/Epic linked | ✅ Parent: User Registration (ID: 12345) |

**DoR Incomplete Example:**
```markdown
## ⚠️ DoR Incomplete - Cannot Start Work

**Missing:** 3 criteria

❌ **Acceptance Criteria** (0/3+ required)
**Remediation:**
1. Define success criteria (what does "done" look like?)
2. Add edge cases (invalid inputs, error scenarios)
3. Add performance criteria (response time targets)

❌ **Dependencies** (not identified)
**Remediation:**
1. List external APIs or services required
2. Document library/package dependencies
3. Identify team dependencies (waiting for other teams)

❌ **Story Points** (not estimated)
**Remediation:**
1. Use Planning Poker with team
2. Break down tasks and estimate hours
3. Convert to story points (1-8h→1pt, 9-16h→3pt, etc.)

**Next Step:** Complete remediation tasks, then re-validate DoR
```

---

### Definition of Done (DoD) - 10 Criteria

**Prevents work from completing until done:**

| Criterion | Description | Validation |
|-----------|-------------|------------|
| **Acceptance Criteria** | All verified | Manual QA signoff |
| **Unit Tests** | ≥80% coverage | Automated (pytest) |
| **Integration Tests** | Passing | Automated (CI/CD) |
| **Code Review** | Approved | 2+ reviewers |
| **Security** | No HIGH/CRITICAL | Bandit scan |
| **Clean Code** | Complexity <15 | Radon analysis |
| **SOLID Principles** | Applied | Code review |
| **Clean Architecture** | Validated | Dependency checks |
| **Documentation** | Updated | Manual review |
| **Staging Deployment** | Successful | Automated (CI/CD) |
| **Performance** | Benchmarks met | Load testing |

**DoD Failure Example:**
```markdown
## ❌ DoD Failed - Cannot Complete Work

**Failed:** 2 criteria

❌ **Unit Tests** (72% coverage, target ≥80%)
**Remediation:**
1. Add tests for error handling (src/auth/login_handler.py lines 42-58)
2. Add tests for edge cases (special characters, long passwords)
3. Run `pytest --cov=src/auth --cov-report=html` to verify

❌ **Security** (1 HIGH vulnerability detected)
**Issue:** SQL Injection risk in user input validation
**File:** src/auth/validators.py line 23
**Remediation:**
1. Use parameterized queries instead of string concatenation
2. Add input sanitization
3. Re-run `bandit -r src/` to verify

**Next Step:** Fix issues, then re-validate DoD
```

---

## 🎯 Usage Examples

### Example 1: Create Story with Full Context

```bash
plan ado story implement two-factor authentication for login
```

**Generated Work Item:**
- **Complexity:** Tier 3 (HIGH) - security keyword detected
- **Story Points:** 8 points (25-40 hours)
- **Child Stories:** 4 auto-generated (Setup, RED, GREEN, REFACTOR)
- **DoR:** ✅ READY (all 10 criteria met)
- **TDD Integration:** Automatic RED→GREEN→REFACTOR phases

---

### Example 2: Create Feature with Multiple Stories

```bash
plan ado feature modernize user authentication system
```

**Generated:**
1. **Feature Work Item** (Epic-level)
   - 5 child stories (2FA, SSO, password policy, session management, audit logging)
   - Total effort: 80 hours (13 story points)
   - Timeline: 2 weeks

2. **Child Stories** (Auto-generated)
   - Story 1: Implement 2FA (8 pts, HIGH priority)
   - Story 2: Add SSO support (5 pts, MEDIUM priority)
   - Story 3: Enforce password policy (3 pts, MEDIUM priority)
   - Story 4: Session management (3 pts, LOW priority)
   - Story 5: Audit logging (2 pts, LOW priority)

3. **Dependencies** (Auto-detected)
   - Story 1 → Story 2 (2FA must exist before SSO)
   - Story 3 → Story 1 (Password policy affects 2FA)

---

### Example 3: Complete Story with DoD Validation

```bash
# Complete the work
ado complete implement-2fa-story

# If DoD fails, shows remediation
## ❌ DoD Failed
- Unit test coverage: 72% (target ≥80%)
- Security scan: 1 HIGH vulnerability

# Fix issues
pytest tests/auth/test_2fa.py --cov=src/auth/2fa.py
bandit -r src/auth/2fa.py

# Re-validate
ado complete implement-2fa-story

# Success!
## ✅ Completion Summary
- Duration: 3 days (24h actual vs 20h estimated)
- DoD: 10/10 criteria met
- File moved: active/ → completed/
```

---

## 🔗 Planning System Integration

ADO Operations inherits **8 requirements** from Planning System:

### 1. Acceptance Criteria Approval Gate

**Inherited Feature:** Work cannot start until acceptance criteria approved by stakeholder

**ADO Implementation:**
```markdown
## Acceptance Criteria (Stakeholder Approval Required)

**Approved By:** @product_owner  
**Approved Date:** 2025-12-25  
**Approval Notes:** Criteria align with user research findings

- [x] Email validation runs on form submission
- [x] Invalid emails show error message
- [x] Valid emails are accepted
```

---

### 2. Interactive DoR Workflow

**Inherited Feature:** Guided DoR checklist with remediation suggestions

**ADO Implementation:**
```bash
# Interactive DoR validation
ado validate-dor add-email-validation-story

## DoR Validation (Interactive)

Criterion 1/10: Title length (10-100 characters)
Current: "Add email validation to registration form" (44 characters) ✅

Criterion 2/10: Description depth (50+ words)
Current: 23 words ❌
Remediation: Add user context, technical approach, and success criteria

[Y] Add missing context now? y

Enter additional description:
> "Users need confidence that email addresses are valid..."

Criterion 2/10: Description depth ✅ (75 words)
... continues for all 10 criteria
```

---

### 3. Contextual Review Orchestrator Integration

**Inherited Feature:** Code review guided by CORTEX with quality checks

**ADO Implementation:**
- DoD criterion: "Code review completed" triggers Contextual Review Orchestrator
- Reviews code for SOLID principles, clean architecture, security issues
- Generates review report as part of completion summary

---

### 4. Visual Progress Rendering

**Inherited Feature:** Real-time progress bars in work item markdown

**ADO Implementation:**
```markdown
## Overall Progress: 50%

[██████████░░░░░░░░░░] 50%

### Phase 1: Setup ✅ COMPLETE (100%)
### Phase 2: Implementation 🔄 IN PROGRESS (75%)
### Phase 3: Testing ⏸️ NOT STARTED (0%)
### Phase 4: Refactor ⏸️ NOT STARTED (0%)
```

---

## 📈 Command Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `plan ado story <description>` | Create user story | `plan ado story add search functionality` |
| `plan ado feature <description>` | Create feature | `plan ado feature payment integration` |
| `plan ado task <description>` | Create task | `plan ado task setup CI/CD pipeline` |
| `plan ado bug <description>` | Create bug | `plan ado bug login fails with @` |
| `plan ado epic <description>` | Create epic | `plan ado epic modernize platform` |

### Lifecycle Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ado list` | List all work items | `ado list --status active` |
| `ado show <id>` | Show work item details | `ado show add-search-story` |
| `ado update <id> --progress <pct>` | Update progress | `ado update add-search-story --progress 75` |
| `ado block <id> --reason <text>` | Block work item | `ado block add-search-story --reason "API down"` |
| `ado unblock <id>` | Unblock work item | `ado unblock add-search-story` |
| `ado complete <id>` | Complete with DoD | `ado complete add-search-story` |
| `ado cancel <id> --reason <text>` | Cancel work item | `ado cancel add-search-story --reason "Duplicate"` |

### Validation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ado validate-dor <id>` | Validate Definition of Ready | `ado validate-dor add-search-story` |
| `ado validate-dod <id>` | Validate Definition of Done | `ado validate-dod add-search-story` |

### Reporting Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ado summary` | Generate team summary | `ado summary --sprint current` |
| `ado velocity` | Calculate team velocity | `ado velocity --sprints 3` |

---

## 🛠️ Troubleshooting

### Issue: DoR validation failing

**Symptoms:** Work item can't start, DoR incomplete

**Solution:**
```bash
# Check specific failures
ado validate-dor <work-item-id>

# Follow remediation steps
# Example: Add missing acceptance criteria
vim cortex-brain/documents/ado/active/<work-item-file>

# Re-validate
ado validate-dor <work-item-id>
```

---

### Issue: DoD validation failing

**Symptoms:** Work item can't complete, DoD incomplete

**Solution:**
```bash
# Check specific failures
ado validate-dod <work-item-id>

# Example: Fix unit test coverage
pytest --cov=src --cov-report=html
# Coverage was 72%, add more tests → 82%

# Re-validate
ado complete <work-item-id>
```

---

### Issue: Work item file not found

**Symptoms:** `ado show <id>` returns "File not found"

**Solution:**
```bash
# List all work items to find correct ID
ado list

# Check all status directories
ls cortex-brain/documents/ado/active/
ls cortex-brain/documents/ado/blocked/
ls cortex-brain/documents/ado/completed/
ls cortex-brain/documents/ado/cancelled/
```

---

## 🎓 Best Practices

### ✅ DO

1. **Complete DoR before starting:** Prevents mid-work blockers
2. **Use complexity detection:** Let CORTEX classify tier vs manual estimation
3. **Update progress regularly:** Keeps stakeholders informed
4. **Follow TDD phases:** Auto-generated RED→GREEN→REFACTOR ensures quality
5. **Block early:** Don't wait if impediments arise

### ❌ DON'T

1. **Skip DoR validation:** 40% higher failure rate without DoR
2. **Force DoD completion:** Quality gates exist for a reason
3. **Edit work items manually:** Use `ado update` commands for consistency
4. **Create work items outside ADO Operations:** Loses DoR/DoD enforcement
5. **Ignore completion summaries:** Lessons learned prevent future issues

---

## 📚 Related Documentation

- **Planning System:** `cortex-brain/documents/implementation-guides/planning-system-user-guide.md`
- **Architecture:** `cortex-brain/documents/archive/ado-operations-architecture-completion.md`
- **TDD Integration:** `cortex-brain/documents/implementation-guides/tdd-orchestrator-v4-user-guide.md`
- **Command Reference:** `.github/prompts/CORTEX.prompt.md`

---

**Document Version:** 1.0.0  
**Status:** ✅ PRODUCTION  
**Next Update:** v1.1 with Azure DevOps API integration (Phase 7-9)
