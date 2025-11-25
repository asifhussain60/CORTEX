# Interactive Planner Agent Guide

**Purpose:** Collaborative planning through guided dialogue with ambiguity detection  
**Version:** 2.1  
**Status:** ✅ Production Ready (CORTEX 2.1 Enhancement)  
**Audience:** CORTEX Users planning features, projects, or implementations

---

## Overview

InteractivePlannerAgent creates implementation plans through intelligent dialogue. Instead of generating plans from unclear requirements, it asks clarifying questions to eliminate ambiguity and ensure Definition of Ready (DoR) compliance.

**Key Capabilities:**
- 🎯 Confidence-based routing (auto-execute vs question mode)
- ❓ Intelligent clarifying questions with priorities
- ✅ Automatic DoR validation
- 🔄 Two-way sync with PlanSyncManager
- 📊 Question types: Required, Optional, Multiple Choice, Yes/No, Free Text
- 🧠 Learns from previous plans to ask better questions

---

## Confidence-Based Routing

InteractivePlannerAgent adapts its behavior based on requirement clarity:

| Confidence Score | Behavior | Example |
|------------------|----------|---------|
| **>85% (High)** | Execute immediately | "Create a login page with email/password fields" |
| **60-85% (Medium)** | Confirm plan with user | "Add authentication to the app" → Shows plan → "Approve?" |
| **<60% (Low)** | Interactive questioning | "Make it better" → Asks 5-8 clarifying questions |

**Example Flow:**

```
User: "plan authentication"
InteractivePlannerAgent: 🔍 Analyzing request clarity...
   Confidence: 55% (LOW) → Entering question mode

   I need to clarify a few things:

   Q1 [REQUIRED]: What type of authentication?
      A) Username/password
      B) OAuth 2.0 (Google, GitHub)
      C) Multi-factor (SMS, TOTP)
      D) SSO (SAML)

   Q2 [REQUIRED]: Where will user credentials be stored?
      A) Local database (SQL Server, PostgreSQL)
      B) External provider (Auth0, Firebase)
      C) LDAP/Active Directory

   Q3 [OPTIONAL]: Session management requirements?
      Default: 30-minute timeout, refresh tokens
      [Enter custom requirements or press Enter for default]
```

---

## Usage Scenarios

### Scenario 1: Clear Requirements (High Confidence)

**User:** "create a login page with email field, password field, remember me checkbox, and submit button"

**InteractivePlannerAgent:**
```
🎯 Confidence: 92% (HIGH) → Auto-executing

✅ Plan created: Login Page Implementation
   
   Components:
   - Email input (type="email", required, validation)
   - Password input (type="password", required, min 8 chars)
   - Remember me checkbox (persist session for 30 days)
   - Submit button (disabled until valid)

   Acceptance Criteria:
   - Email validates format (regex)
   - Password shows/hide toggle
   - Form submission with AJAX
   - Error messages for validation failures

   Estimated time: 4 hours
   Dependencies: AuthService, SessionManager

Plan saved. Ready to implement?
```

---

### Scenario 2: Ambiguous Requirements (Low Confidence)

**User:** "improve the dashboard performance"

**InteractivePlannerAgent:**
```
🔍 Confidence: 40% (LOW) → Question mode activated

I detected ambiguity in your request. Let me ask some clarifying questions:

Q1 [REQUIRED - Priority 5]: What specific performance issue?
   A) Page load time too slow (> 3 seconds)
   B) UI lag/freezing during interactions
   C) API response delays
   D) Large data rendering issues

Q2 [REQUIRED - Priority 5]: What is the current performance metric?
   Example: "Dashboard loads in 8 seconds"
   [Your answer]: _

Q3 [REQUIRED - Priority 5]: What is your target performance?
   Example: "Dashboard must load in < 2 seconds"
   [Your answer]: _

Q4 [OPTIONAL - Priority 3]: Any specific user workflows affected?
   Default: General dashboard usage
   [Your answer or press Enter for default]: _

Answering these will help me create a precise optimization plan.
```

---

### Scenario 3: Medium Confidence (Confirmation Mode)

**User:** "add user registration"

**InteractivePlannerAgent:**
```
🔍 Confidence: 72% (MEDIUM) → Confirmation mode

I've created a plan based on standard user registration patterns. 
Please review and confirm:

📋 User Registration Implementation Plan

Features:
- Registration form: Email, Password, Confirm Password, Terms Checkbox
- Email verification workflow (send verification link)
- Password strength indicator (weak/medium/strong)
- Account activation on email confirmation

Technical Approach:
- Backend: POST /api/auth/register endpoint
- Email service: SendGrid integration
- Database: Add Users table with email_verified field
- Frontend: Reactive form with async validators

DoR Checklist:
✅ Requirements clear (standard registration flow)
✅ Dependencies identified (SendGrid API key needed)
⚠️ Security review: NEED TO ADD - password hashing (bcrypt), rate limiting
✅ Acceptance criteria defined

Estimated Time: 8 hours

Does this match your expectations? 
(Reply "yes" to approve, "modify [aspect]" to adjust, or "questions" for clarification)
```

---

## Question Types & Priorities

**Question Types:**

| Type | Description | Example |
|------|-------------|---------|
| **REQUIRED** | Must answer to proceed | "What authentication type?" |
| **OPTIONAL** | Can skip (uses default) | "Session timeout?" (default: 30 min) |
| **MULTIPLE_CHOICE** | Select from options | "A) OAuth B) SAML C) Basic Auth" |
| **YES_NO** | Boolean decision | "Enable password reset?" |
| **FREE_TEXT** | Open-ended | "Describe the expected workflow" |

**Priority Levels (1-5):**

- **Priority 5 (Critical):** Required for any meaningful plan (e.g., "What is the feature?")
- **Priority 4 (High):** Affects architecture decisions (e.g., "Where is data stored?")
- **Priority 3 (Medium):** Affects implementation details (e.g., "Session timeout?")
- **Priority 2 (Low):** Nice-to-have context (e.g., "Preferred UI library?")
- **Priority 1 (Info):** Background info only (e.g., "Who requested this feature?")

---

## Integration with CORTEX Planning System

### Two-Way Sync with PlanSyncManager

InteractivePlannerAgent automatically syncs with CORTEX's planning system:

1. **Plan Creation:** Agent creates plan → Saved to planning database
2. **Plan Updates:** User modifies plan file → Syncs back to agent context
3. **Plan Approval:** User approves → Triggers implementation workflow
4. **Plan Tracking:** Agent monitors progress → Updates planning documents

**Example:**
```
User: "plan payment processing"
InteractivePlannerAgent: [asks questions] → Creates plan
System: Plan saved to cortex-brain/documents/planning/features/PLAN-20251125-payment.md

[User edits plan file in VS Code]
InteractivePlannerAgent: 🔄 Detected plan changes → Syncing context

User: "approve plan"
System: Plan approved → Payment implementation workflow started
```

---

### DoR (Definition of Ready) Enforcement

InteractivePlannerAgent validates DoR before plan approval:

**DoR Checklist:**
- [ ] Requirements documented with zero ambiguity
- [ ] Dependencies identified and validated
- [ ] Technical design approach agreed
- [ ] Test strategy defined
- [ ] Acceptance criteria measurable
- [ ] Security review complete (OWASP checklist)
- [ ] User approval on scope

**If DoR incomplete:**
```
⚠️ DoR Validation Failed

Missing:
- Security review not completed
- Test strategy not defined

Would you like me to:
A) Run security review now (2 min)
B) Generate test strategy (1 min)
C) Do both
D) Skip for now (not recommended)
```

---

## Configuration

**Planning Mode (cortex.config.json):**
```json
{
  "interactive_planner": {
    "confidence_threshold_high": 85,
    "confidence_threshold_low": 60,
    "max_questions": 10,
    "question_timeout": 300,
    "default_behavior": "question_mode",
    "enable_learning": true,
    "save_plans_to": "cortex-brain/documents/planning/"
  }
}
```

**Confidence Thresholds:**
- Adjust based on your risk tolerance
- Lower thresholds → More auto-execution (faster but riskier)
- Higher thresholds → More questions (slower but safer)

---

## State Machine

```
DETECTING → Analyze request clarity
   ↓
[Confidence Check]
   ├─ High (>85%) → EXECUTING → COMPLETED
   ├─ Medium (60-85%) → CONFIRMING → EXECUTING → COMPLETED
   └─ Low (<60%) → QUESTIONING → [User Answers] → EXECUTING → COMPLETED
   
ABORTED ← User can abort at any state
```

---

## Troubleshooting

### Issue: "Too many questions asked"

**Cause:** Low confidence + complex feature

**Solution:**
- Provide more details upfront: "plan OAuth 2.0 authentication with Google sign-in"
- Adjust confidence threshold in config (raise `confidence_threshold_low`)

---

### Issue: "Plan doesn't match expectations"

**Cause:** Medium confidence auto-execution

**Solution:**
- Use confirmation mode: "plan [feature] with confirmation"
- Review plan before approval
- Answer questions to clarify

---

### Issue: "Planning timed out"

**Cause:** Question timeout exceeded (default: 5 minutes)

**Solution:**
- Respond faster to questions
- Adjust `question_timeout` in config
- Use "resume plan" to continue

---

## Best Practices

**DO:**
- ✅ Provide specific details to trigger high-confidence mode
- ✅ Answer questions thoughtfully (impacts plan quality)
- ✅ Review medium-confidence plans before approval
- ✅ Use "approve plan" only when DoR complete

**DON'T:**
- ❌ Skip required questions (blocks plan creation)
- ❌ Approve plans with incomplete DoR (causes issues later)
- ❌ Rush through question mode (leads to poor plans)
- ❌ Ignore security review warnings

---

## Related Commands

- `plan [feature]` - Start interactive planning
- `approve plan` - Approve plan and start implementation
- `resume plan [name]` - Continue interrupted planning
- `show plan [name]` - View existing plan details
- `planning status` - Show all active plans

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 2.1 (Interactive Planning Enhancement)  
**Last Updated:** November 25, 2025
