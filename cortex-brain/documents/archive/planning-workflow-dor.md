# CORTEX Planning Workflow with DoR Enforcement

**Version:** 1.0  
**Status:** ✅ PRODUCTION  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 🎯 Overview

This document defines CORTEX's planning workflow with **Definition of Ready (DoR) enforcement** as the critical gating mechanism. CORTEX MUST NOT proceed to analysis or execution phases until DoR is met with **zero ambiguity**.

---

## 📋 Three-Phase Workflow

### Phase 1: Planning (User-Collaborative) ✅ Required

**Purpose:** Establish complete understanding with zero ambiguity before any automated work begins.

**Triggers:**
- "plan [feature]"
- "let's plan"
- "plan a feature"
- "help me plan"

**Process:**

```mermaid
flowchart TD
    A[User: "plan authentication"] --> B[CORTEX: Detect PLAN intent]
    B --> C[Create planning file]
    C --> D[Start Interactive Session]
    D --> E[Ask Clarifying Questions]
    E --> F{All Questions<br/>Answered?}
    F -->|No| E
    F -->|Yes| G[Validate DoR Checklist]
    G --> H{DoR Complete?}
    H -->|No| I[Show DoR Gaps]
    I --> E
    H -->|Yes| J[Generate Detailed Plan]
    J --> K[User Reviews Plan]
    K --> L{Approve Plan?}
    L -->|No| M[User Refines]
    M --> K
    L -->|Yes| N[Phase 2: Analysis]
```

---

## ✅ Definition of Ready (DoR) Checklist

**CRITICAL:** ALL items must be checked before proceeding to Analysis phase.

### 1. Requirements Documented (Zero Ambiguity)

❌ **Vague:** "Improve performance"  
✅ **Specific:** "Reduce API response time to <200ms for 95th percentile"

❌ **Vague:** "Add authentication"  
✅ **Specific:** "Implement JWT-based authentication with email/password login, session management (15-min timeout), and password reset via email"

**Validation Questions:**
- Can a developer implement this without asking clarifying questions?
- Are all terms defined with measurable criteria?
- Are there any "probably", "maybe", "usually" words in requirements?

---

### 2. Dependencies Identified & Validated

**What to Identify:**
- Files that will be modified (exact paths)
- Services that will be called (exact endpoints/APIs)
- Database tables (exact schema)
- External libraries (exact packages/versions)
- Other systems (exact integration points)

**Validation Required:**

```python
# CORTEX MUST verify before marking DoR complete:

# Check file exists
if not Path("src/services/auth_service.py").exists():
    raise DORIncomplete("Referenced file does not exist")

# Check API accessibility
if not can_reach_api("https://api.email-service.com"):
    raise DORIncomplete("Email service API not accessible")

# Check database table exists
if not db.table_exists("users"):
    raise DORIncomplete("Users table does not exist")
```

**Common Mistakes:**
- Assuming files exist without checking
- Referencing services that aren't configured
- Missing database migration requirements

---

### 3. Technical Design Approach Agreed

**Required Elements:**
- Architecture pattern (MVC, microservices, etc.)
- Technology stack (languages, frameworks, libraries)
- Data flow (how data moves through system)
- Security considerations (authentication, authorization, encryption)
- Error handling strategy

**Example:**

```markdown
## Technical Design Approach

**Architecture:** Layered architecture (Controller → Service → Repository)
**Stack:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
**Data Flow:** 
1. User submits login form (POST /api/auth/login)
2. AuthController validates input
3. AuthService checks credentials against Users table
4. JWT token generated and returned
5. Client stores token in httpOnly cookie

**Security:**
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens signed with RS256
- HTTPS only (enforce in production)
- Rate limiting: 5 attempts per 15 minutes

**Error Handling:**
- 401 for invalid credentials
- 429 for rate limit exceeded
- 500 for server errors
- All errors logged to centralized logging service
```

---

### 4. Test Strategy Defined

**Required:**
- Unit test approach (what to test, coverage target)
- Integration test approach (what integrations to test)
- End-to-end test approach (user workflows)
- Test data strategy (fixtures, mocking)
- Coverage threshold (minimum %)

**Example:**

```markdown
## Test Strategy

**Unit Tests (Target: 90% coverage)**
- AuthService: login(), logout(), refresh_token()
- PasswordHasher: hash(), verify()
- JWTGenerator: generate(), validate()

**Integration Tests**
- Login flow (email/password → JWT token)
- Token refresh flow
- Password reset flow (email integration)
- Session timeout behavior

**E2E Tests (Playwright)**
- User can login with valid credentials
- User cannot login with invalid credentials
- User can reset password via email
- User session expires after 15 minutes

**Test Data**
- Fixtures: 5 test users with varied roles
- Mock email service (no real emails sent in tests)
- Isolated test database (SQLite in-memory)
```

---

### 5. Acceptance Criteria Measurable

**Format:** Must be testable with pass/fail result.

❌ **Not Measurable:** "Authentication should work well"  
✅ **Measurable:** "User can login with email/password and receive JWT token within 500ms"

**Template:**

```markdown
## Acceptance Criteria

1. **AC1: User Login**
   - Given: User has valid email/password
   - When: User submits login form
   - Then: User receives JWT token
   - And: Token is valid for 15 minutes
   - And: Response time < 500ms

2. **AC2: Invalid Credentials**
   - Given: User has invalid email/password
   - When: User submits login form
   - Then: User receives 401 error
   - And: Error message is "Invalid credentials"
   - And: Attempt is logged

3. **AC3: Rate Limiting**
   - Given: User has attempted login 5 times
   - When: User attempts 6th login within 15 minutes
   - Then: User receives 429 error
   - And: Error message is "Too many attempts"
```

**Validation:** Can you write an automated test for each AC?

---

### 6. User Approval on Scope

**Required:**
- User explicitly approves the scope defined
- User understands what WILL be built
- User understands what WON'T be built (out of scope)
- User agrees to timeline and phases

**Approval Format:**

```markdown
## Scope Approval

**In Scope:**
✅ Email/password login
✅ JWT token generation
✅ Session management (15-min timeout)
✅ Password reset via email
✅ Rate limiting (5 attempts per 15 min)

**Out of Scope:**
❌ OAuth (Google, Facebook) - Phase 2
❌ Multi-factor authentication - Phase 2
❌ Remember me functionality - Phase 2
❌ Biometric authentication - Future

**User Approval:**
[ ] I understand the scope defined above
[ ] I approve proceeding with this scope
[ ] I understand out-of-scope items are not included

User: [Name]
Date: [YYYY-MM-DD]
```

---

## 🚫 DoR Enforcement Rules

### CORTEX MUST NOT:

1. **Proceed to Analysis Phase if DoR is incomplete**
   - Block "approve plan" command until DoR checklist is 100% complete
   - Display missing DoR items clearly

2. **Assume referenced files/services exist without verification**
   - Always run file checks: `Path(file).exists()`
   - Always test API accessibility: `requests.get(api).status_code == 200`
   - Always validate database tables: `SELECT * FROM information_schema.tables WHERE table_name='users'`

3. **Accept vague requirements**
   - Challenge any "improve", "better", "faster" without measurable criteria
   - Challenge any "probably", "maybe", "usually" in requirements
   - Challenge any ambiguous terms: "secure" → "encrypted with AES-256"

### CORTEX MUST:

1. **Ask clarifying questions until zero ambiguity**
   - Keep asking until requirements are specific and measurable
   - Refuse to proceed with vague answers

2. **Validate all assumptions**
   - Check files exist
   - Check services are accessible
   - Check database schema matches expectations
   - Check dependencies are installed

3. **Display DoR status clearly**
   ```markdown
   📋 **Definition of Ready Status**
   
   ✅ Requirements documented (zero ambiguity)
   ✅ Dependencies identified & validated
   ⏳ Technical design approach (in progress)
   ❌ Test strategy (not defined)
   ❌ Acceptance criteria (too vague)
   ❌ User approval (not received)
   
   **Cannot proceed until all items are ✅**
   ```

---

## 📝 Interactive Session Example

### Step 1: User Initiates Planning

```
User: "plan authentication feature"

CORTEX:
✅ Created planning file (opened in VS Code)
💬 Starting interactive planning session with DoR enforcement...

I need to ensure zero ambiguity before proceeding. Let me ask some clarifying questions:

📋 Definition of Ready Checklist:
☐ Requirements documented (zero ambiguity)
☐ Dependencies identified & validated
☐ Technical design approach agreed
☐ Test strategy defined
☐ Acceptance criteria measurable
☐ User approval on scope

🔍 Clarifying Questions (Must answer ALL):

1. **Feature Scope** - What EXACTLY does "authentication" include?
   - Login with email/password?
   - OAuth (Google, Facebook)?
   - Multi-factor authentication?
   - Password reset?
   - Session management?

2. **Users** - Who are the SPECIFIC users?
   - Admin users?
   - Regular users?
   - Guest users?
   - Different roles with different access?

3. **Integration Points** - What EXACT systems/APIs/databases?
   - Which database? (PostgreSQL, MySQL, SQLite?)
   - Which email service? (SendGrid, Mailgun, AWS SES?)
   - Any existing authentication service?

4. **Constraints** - What are the MEASURABLE limits?
   - Maximum login time? (e.g., <500ms)
   - Session timeout? (e.g., 15 minutes)
   - Rate limiting? (e.g., 5 attempts per 15 min)

5. **Success Metrics** - How do we MEASURE success?
   - 100% of users can login?
   - <500ms response time?
   - 0% security vulnerabilities?

6. **Dependencies** - What files/services MUST exist?
   - User model in database?
   - Email service configured?
   - Any existing auth code?

⚠️ I will not proceed until DoR is met with zero ambiguity.
```

---

### Step 2: User Provides Answers

```
User:
1. Email/password login only (OAuth is Phase 2). Include password reset via email.
2. Regular users (admin auth is separate system).
3. PostgreSQL database (users table exists). SendGrid for emails (API key in .env).
4. Login <500ms. Session timeout 15 minutes. Rate limit 5 attempts per 15 min.
5. Success = 100% of valid users can login with <500ms response time.
6. Users table exists (I just created it). SendGrid API key configured.
```

---

### Step 3: CORTEX Validates Dependencies

```
CORTEX:
🔍 Validating dependencies...

✅ Checking database: PostgreSQL connected
✅ Checking users table: EXISTS (columns: id, email, password_hash, created_at)
✅ Checking SendGrid API key: CONFIGURED (.env file)
✅ Checking SendGrid accessibility: REACHABLE (status 200)

All dependencies validated!

📋 Definition of Ready Status:
✅ Requirements documented (zero ambiguity)
✅ Dependencies identified & validated
⏳ Technical design approach (generating...)
⏳ Test strategy (generating...)
⏳ Acceptance criteria (generating...)
☐ User approval on scope

Generating detailed plan...
```

---

### Step 4: CORTEX Generates Plan

```
CORTEX:
✅ Plan generated! Review the planning document.

📋 Definition of Ready Status:
✅ Requirements documented (zero ambiguity)
✅ Dependencies identified & validated
✅ Technical design approach (layered architecture, FastAPI, JWT)
✅ Test strategy (90% unit coverage, integration tests, E2E tests)
✅ Acceptance criteria (5 measurable criteria defined)
☐ User approval on scope

📄 Planning Document: cortex-brain/documents/planning/features/PLAN-2025-11-19-authentication.md

Please review the plan and confirm scope approval:

**In Scope:**
✅ Email/password login
✅ JWT token generation
✅ Session management (15-min timeout)
✅ Password reset via email
✅ Rate limiting (5 attempts per 15 min)

**Out of Scope:**
❌ OAuth (Phase 2)
❌ Multi-factor authentication (Phase 2)

Do you approve this scope? (Yes/No)
```

---

### Step 5: User Approves

```
User: "Yes, approve"

CORTEX:
✅ Scope approved by user

📋 Definition of Ready Status:
✅ Requirements documented (zero ambiguity)
✅ Dependencies identified & validated
✅ Technical design approach (layered architecture, FastAPI, JWT)
✅ Test strategy (90% unit coverage, integration tests, E2E tests)
✅ Acceptance criteria (5 measurable criteria defined)
✅ User approval on scope

🎉 DoR COMPLETE! Ready to proceed to Analysis phase.

Say "approve plan" to start Analysis phase (crawler, knowledge graph, analysis report).
```

---

## 🚀 Phase 2: Analysis (Automatic, After DoR)

**Only triggered after DoR is complete and user approves plan.**

See main planning workflow document for Analysis phase details.

---

## 🎓 Key Principles

1. **Zero Ambiguity** - No vague requirements allowed
2. **Validation Required** - Never assume, always verify
3. **User Approval Gate** - User must explicitly approve scope
4. **Blocking Mechanism** - Cannot proceed if DoR incomplete
5. **Transparency** - Always show DoR status clearly

---

## 📚 Related Documents

- Main Planning Workflow: `cortex-brain/documents/planning/planning-workflow.md`
- DoR Templates: `cortex-brain/templates/planning/dor-checklist.md`
- Response Templates: `cortex-brain/response-templates.yaml`

---

**Document Status:** ✅ Complete  
**Last Updated:** 2025-11-19  
**Next Review:** 2025-12-19
