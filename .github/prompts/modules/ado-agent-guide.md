# ADO Agent Guide

**Purpose:** Unified wrapper agent for Azure DevOps operations (work items, code review, planning)  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The ADO Agent is a wrapper agent that routes Azure DevOps-related intents to appropriate orchestrators. It provides a unified entry point for ADO operations including story creation, feature planning, work summaries, and code review integration.

**Key Features:**
- ADO-formatted markdown output (copy-paste ready for Azure DevOps)
- Complete work tracking (files changed, decisions made, acceptance criteria)
- Integration with planning and code review systems
- Lazy orchestrator loading (performance optimization)

---

## 🚀 Commands

**Natural Language Triggers:**
- `plan ado`
- `plan ado story`
- `plan ado feature`
- `create ado work item`
- `ado summary`
- `ado pr review`
- `review ado pr`

**Use Cases:**
- Creating user stories with ADO format
- Planning features with acceptance criteria
- Generating work summaries for sprint reviews
- Reviewing pull requests with ADO integration
- Tracking development progress

---

## 📊 Workflow Steps

### Phase 1: Intent Detection (instant)
```
Identify ADO operation type:

Intents:
• ADO_STORY - Create user story
• ADO_FEATURE - Create feature
• ADO_SUMMARY - Generate work summary
• ADO_WORKITEM - Generic work item creation
• CODE_REVIEW - Pull request review with ADO integration

Routing:
All intents → UnifiedEntryPointOrchestrator with appropriate method
```

### Phase 2: Orchestrator Routing (instant)
```
Route to appropriate method:

ADO_STORY → UnifiedEntryPointOrchestrator.execute_ado_story()
ADO_FEATURE → UnifiedEntryPointOrchestrator.execute_ado_feature()
ADO_SUMMARY → UnifiedEntryPointOrchestrator.generate_work_summary()
CODE_REVIEW → UnifiedEntryPointOrchestrator.execute_code_review()

Lazy Loading:
Orchestrator initialized on first use (not at agent creation)
Performance: <50ms first call, <5ms subsequent calls
```

### Phase 3: Operation Execution (varies by operation)
```
Execute operation and return ADO-formatted result:

Story Creation (5-10 min):
1. Gather requirements
2. Define acceptance criteria
3. Estimate story points
4. Generate ADO markdown

Feature Planning (15-30 min):
1. Feature decomposition
2. Story breakdown
3. Sprint planning
4. Dependency mapping

Work Summary (2-5 min):
1. Scan git history
2. Extract file changes
3. Identify decisions
4. Format for sprint review

Code Review (10-20 min):
1. Analyze pull request diff
2. Check code quality
3. Validate tests
4. Generate ADO comment
```

---

## 🔧 Configuration

**Config File:** `cortex.config.json`

```json
{
  "ado_agent": {
    "default_project": "MyProject",
    "default_area_path": "MyProject\\Development",
    "default_iteration_path": "MyProject\\Sprint 1",
    "ado_api_endpoint": "https://dev.azure.com/{organization}",
    "ado_api_version": "7.0",
    "lazy_load_orchestrators": true,
    "markdown_output_format": "ado"
  }
}
```

**Options:**
- `default_project` - ADO project name (default: `"MyProject"`)
- `default_area_path` - Area path for work items (default: `"MyProject\\Development"`)
- `default_iteration_path` - Sprint/iteration path (default: `"MyProject\\Sprint 1"`)
- `ado_api_endpoint` - Azure DevOps API URL
- `ado_api_version` - ADO REST API version (default: `"7.0"`)
- `lazy_load_orchestrators` - Delay orchestrator initialization (default: `true`)
- `markdown_output_format` - Output format: `ado`, `github`, `generic` (default: `ado`)

---

## 📈 Examples

### Example 1: Create ADO User Story
```
User: "plan ado story - user login feature"

CORTEX:
  📝 Creating ADO User Story
  
  Gathering requirements...
  
  Q: What is the primary user goal?
  A: Allow registered users to securely access their accounts
  
  Q: What are the key acceptance criteria?
  A: Email/password validation, session management, error handling
  
  Q: Story point estimate (1, 2, 3, 5, 8, 13)?
  A: 5 (large - 1-2 days)
  
  ✅ Story created!
  
  ---
  # User Story #12345: Implement User Login
  
  **Story Points:** 5 | **Priority:** 2 (High) | **Tags:** authentication, backend, security
  
  ## Description
  As a **registered user**  
  I want to **log in with email and password**  
  So that **I can securely access my account and personalized data**
  
  ## Acceptance Criteria
  - [ ] User can enter email and password on login form
  - [ ] System validates credentials against database
  - [ ] Successful login creates JWT token and session
  - [ ] Failed login displays clear error message
  - [ ] Session expires after 30 minutes of inactivity
  - [ ] "Remember me" option extends session to 30 days
  
  ## Implementation Plan
  1. Create `/api/auth/login` endpoint (Express.js)
  2. Implement bcrypt password validation
  3. Generate JWT token with user ID, role, expiry
  4. Store session in Redis with 30-minute TTL
  5. Add rate limiting (10 attempts per 15 minutes)
  6. Write unit tests (80%+ coverage)
  
  ## Technical Notes
  **Architecture:**
  - Backend: Node.js + Express
  - Database: PostgreSQL (user table)
  - Cache: Redis (session store)
  - Security: bcrypt (password hashing), jsonwebtoken (JWT)
  
  **Dependencies:**
  - Requires: User registration feature (Story #12340)
  - Blocks: Password reset feature (Story #12350)
  
  **Security Considerations:**
  - OWASP A02: Cryptographic Failures (✅ bcrypt for passwords)
  - OWASP A07: Authentication Failures (✅ rate limiting implemented)
  - HTTPS required for login endpoint
  
  ## Testing Strategy
  - Unit tests: Login controller, JWT generation, session management
  - Integration tests: Full login flow with database
  - E2E tests: Selenium login form submission
  - Security tests: SQL injection, XSS, brute force protection
  
  ---
  
  📋 Copy the markdown above and paste directly into Azure DevOps.
  Story will be created in: MyProject\Development\Sprint 1
```

### Example 2: Generate Work Summary
```
User: "ado summary for last sprint"

CORTEX:
  📊 Generating ADO Work Summary
  
  Analyzing git history (last 14 days)...
  
  **Sprint Summary (Sprint 12 - Nov 15-29, 2025)**
  
  ## Completed Work Items
  
  ### ✅ User Story #12345: Implement User Login (5 points)
  **Status:** Done  
  **Files Changed:** 8 files, +427 lines, -89 lines
  - `src/controllers/auth.controller.js` (new)
  - `src/middleware/rate-limiter.js` (new)
  - `src/routes/auth.routes.js` (new)
  - `tests/auth.controller.test.js` (new)
  - `package.json` (updated dependencies)
  
  **Key Decisions:**
  • Chose JWT over session cookies (stateless, better for microservices)
  • Implemented Redis for session store (faster than database)
  • Added rate limiting to prevent brute force attacks
  
  **Test Coverage:** 87% (target: 80% - ✅ Met)
  
  ---
  
  ### ✅ User Story #12346: Password Reset Flow (3 points)
  **Status:** Done  
  **Files Changed:** 5 files, +234 lines, -12 lines
  - `src/controllers/password-reset.controller.js` (new)
  - `src/services/email.service.js` (updated)
  - `src/templates/reset-email.html` (new)
  
  **Key Decisions:**
  • Email-based reset (no SMS to reduce cost)
  • 1-hour expiry for reset tokens
  • SendGrid for email delivery (99.9% SLA)
  
  **Test Coverage:** 92% (target: 80% - ✅ Exceeded)
  
  ---
  
  ## In Progress
  
  ### 🔄 User Story #12347: Role-Based Access Control (8 points)
  **Status:** In Progress (60% complete)  
  **Blocked By:** None  
  **Estimated Completion:** Dec 2, 2025
  
  ---
  
  ## Sprint Metrics
  
  **Velocity:** 8 story points completed (target: 10 points)  
  **Completion Rate:** 80% (2 of 3 stories done)  
  **Test Coverage:** 89.5% average (target: 80% - ✅ Met)  
  **Code Review:** 100% of PRs reviewed within 24 hours
  
  **Burndown:**
  - Day 1-3: 10 points remaining
  - Day 4-7: 8 points remaining (Story #12346 completed)
  - Day 8-14: 2 points remaining (Story #12345 completed)
  - Day 15: Sprint end (2 points carried over)
  
  ---
  
  ## Risks & Blockers
  
  **None identified** - Sprint progressed smoothly
  
  ---
  
  📋 Copy this summary for sprint retrospective and demo.
```

### Example 3: ADO Pull Request Review
```
User: "review ado pr #456"

CORTEX:
  🔍 ADO Pull Request Review
  
  Analyzing PR #456: "feat: Add user login endpoint"
  
  **PR Metadata:**
  • Author: john.doe@company.com
  • Created: Nov 28, 2025
  • Files Changed: 8
  • Lines: +427, -89
  • Commits: 7
  
  ---
  
  ## Code Review Summary
  
  **Overall Assessment:** ✅ Approved with minor suggestions
  
  ### ✅ Strengths
  1. **Comprehensive Testing** - 87% coverage, including edge cases
  2. **Security Best Practices** - bcrypt for passwords, JWT for tokens, rate limiting
  3. **Clear Documentation** - JSDoc comments, README updates
  4. **Error Handling** - Proper HTTP status codes, descriptive error messages
  
  ### ⚠️ Suggestions
  
  #### 1. Extract Magic Numbers (Minor)
  **File:** `src/middleware/rate-limiter.js:15`
  ```javascript
  // Current (magic numbers)
  const limiter = rateLimit({ windowMs: 900000, max: 10 });
  
  // Suggested (named constants)
  const RATE_LIMIT_WINDOW_MS = 15 * 60 * 1000; // 15 minutes
  const RATE_LIMIT_MAX_ATTEMPTS = 10;
  const limiter = rateLimit({ 
    windowMs: RATE_LIMIT_WINDOW_MS, 
    max: RATE_LIMIT_MAX_ATTEMPTS 
  });
  ```
  
  #### 2. Add Input Validation (Medium)
  **File:** `src/controllers/auth.controller.js:32`
  ```javascript
  // Add email format validation before database query
  if (!validator.isEmail(email)) {
    return res.status(400).json({ error: 'Invalid email format' });
  }
  ```
  
  #### 3. Consider Token Refresh Strategy (Low)
  **General:** Current JWT expires after 30 minutes. Consider implementing refresh tokens to improve UX (users stay logged in longer without compromising security).
  
  ### 🧪 Test Results
  - ✅ Unit Tests: 42 passed, 0 failed
  - ✅ Integration Tests: 12 passed, 0 failed
  - ✅ Lint: 0 errors, 0 warnings
  - ✅ Security Scan: 0 vulnerabilities
  
  ### 📝 ADO Work Item Validation
  - ✅ Linked to Story #12345
  - ✅ All acceptance criteria addressed
  - ✅ Implementation plan followed
  - ✅ Test coverage target met (87% > 80%)
  
  ---
  
  ## Recommendation
  **Approve** - Code is production-ready. Suggestions are non-blocking and can be addressed in follow-up PRs if desired.
  
  ---
  
  📋 Copy this review and post as ADO PR comment.
```

---

## 🎓 Key Concepts

### ADO Work Item Hierarchy
```
Epic (organizational goal, 3-6 months)
  └─ Feature (shippable capability, 1-3 sprints)
      └─ User Story (user-facing value, 1-5 days)
          └─ Task (technical work, <1 day)
```

### ADO Markdown Format
**Special Tags:**
- `#12345` - Work item ID auto-link
- `@user` - Mention Azure DevOps user
- `[Title](#url)` - External link
- `:emoji:` - Emoji support (`:white_check_mark:` = ✅)

### Lazy Loading Pattern
**Benefits:**
- Faster agent initialization (<5ms vs ~200ms)
- Reduced memory footprint (no unused orchestrators)
- Better scaling (1000+ agents possible)

**Implementation:**
```python
def _get_unified_orchestrator(self):
    if self._unified_orchestrator is None:
        # Load only when needed
        from src.orchestrators.unified_entry_point_orchestrator import UnifiedEntryPointOrchestrator
        self._unified_orchestrator = UnifiedEntryPointOrchestrator()
    return self._unified_orchestrator
```

---

## 🔍 Troubleshooting

### Issue: "UnifiedEntryPointOrchestrator not found"
**Cause:** Orchestrator not installed or import path incorrect  
**Solution:** Check `src/orchestrators/unified_entry_point_orchestrator.py` exists

### Issue: "ADO API authentication failed"
**Cause:** Missing or invalid Personal Access Token (PAT)  
**Solution:** Create PAT in Azure DevOps (User Settings → Personal Access Tokens), add to `cortex.config.json`

### Issue: "Work item creation failed - invalid area path"
**Cause:** Area path doesn't exist in ADO project  
**Solution:** Verify area path in Azure DevOps (Project Settings → Project Configuration → Areas)

### Issue: "Agent intent not recognized"
**Cause:** Intent type mismatch or string comparison failure  
**Solution:** Check `IntentType` enum values, ensure `can_handle()` logic covers all ADO intents

---

## 🧪 Testing

**Test Files:**
- `tests/test_ado_agent.py` - Intent routing, orchestrator loading

**Key Test Scenarios:**
1. Intent detection for all ADO operations
2. Lazy orchestrator loading (verify delayed initialization)
3. ADO markdown formatting
4. Error handling for missing orchestrator
5. Work item API integration (mocked)

**Run Tests:**
```bash
pytest tests/test_ado_agent.py -v
```

---

## 🔗 Integration

**Dependencies:**
- `UnifiedEntryPointOrchestrator` - Handles all ADO operations
- `IntentType` enum - Defines ADO intent types
- `BaseAgent` - Agent framework base class

**Called By:**
- Natural language commands ("plan ado", "ado summary")
- Intent router when ADO keywords detected
- Code review workflows

**Calls:**
- `UnifiedEntryPointOrchestrator.execute_ado_story()` - Story creation
- `UnifiedEntryPointOrchestrator.execute_ado_feature()` - Feature planning
- `UnifiedEntryPointOrchestrator.generate_work_summary()` - Work tracking
- `UnifiedEntryPointOrchestrator.execute_code_review()` - PR analysis

---

## 📚 Related Documentation

- **Unified Entry Point Orchestrator Guide** - Detailed ADO operation documentation
- **SWAGGER Entry Point Orchestrator Guide** - DoR validation and estimation
- **Code Review Guide** - Pull request analysis workflow
- **Azure DevOps API Reference** - REST API documentation

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions) - See LICENSE  
**Repository:** https://github.com/asifhussain60/CORTEX
