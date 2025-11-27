# CORTEX Hands-On Tutorial Program

**Purpose:** Interactive learning program teaching CORTEX through practical exercises  
**Version:** 1.0  
**Status:** ✅ PRODUCTION READY  
**Duration:** 15-30 minutes (customizable)

---

## 🎯 Tutorial Overview

This hands-on program guides you through CORTEX capabilities with real exercises, not just documentation. You'll learn by doing:

1. **CORTEX Basics** (5 min) - Understanding the system
2. **Planning Workflow** (5-7 min) - How to plan features
3. **Development with TDD** (8-10 min) - Write tests, implement features
4. **Testing & Validation** (5-7 min) - Verify your work
5. **Architecture Intelligence** (5-7 min) - Strategic health analysis and trend tracking

**What You'll Build:** A simple user authentication feature (login form with validation) + architecture health tracking

---

## 📚 Tutorial Structure

### Learning Path Options

**🚀 Quick Start (15 min)**
- Learn essentials only (Modules 1-3)
- Skip theory, focus on commands
- Build simplified version

**📖 Standard (30 min)**
- Balanced theory + practice (Modules 1-4)
- All core workflows covered
- Complete feature implementation

**🎓 Comprehensive (40 min)**
- Deep understanding (Modules 1-5)
- Advanced features included
- Production-ready implementation + architecture analysis

---

## 🎓 Module 1: CORTEX Basics (5 min)

### What You'll Learn
- How CORTEX works (brain architecture)
- Natural language commands
- Help system navigation
- Brain memory system

### Hands-On Exercise 1.1: Explore CORTEX Capabilities

**Task:** Discover what CORTEX can do

**Commands to Try:**
```
help
```

**Expected Output:**
- Table of all available commands
- Natural language triggers
- Operation categories

**Understanding Check:**
- ✅ Can you find the planning command?
- ✅ Can you find the TDD workflow command?
- ✅ Can you find the feedback command?

---

### Hands-On Exercise 1.2: Check CORTEX Brain Memory

**Task:** See what CORTEX remembers about your workspace

**Commands to Try:**
```
show context
```

**Expected Output:**
- Conversation history loaded
- Context quality score
- Memory health status

**Understanding Check:**
- ✅ What's your context quality score?
- ✅ How many conversations loaded?
- ✅ Is your memory health good?

---

### Hands-On Exercise 1.3: System Health Check

**Task:** Validate CORTEX is working correctly

**Commands to Try:**
```
healthcheck
```

**Expected Output:**
- System status (Healthy/Warning/Unhealthy)
- Database integrity check
- Feature availability check

**Understanding Check:**
- ✅ Is your CORTEX healthy?
- ✅ Are all features available?
- ✅ Any warnings to address?

---

## 📋 Module 2: Planning Workflow (5-7 min)

### What You'll Learn
- Feature planning process
- DoR (Definition of Ready) validation
- DoD (Definition of Done) criteria
- Security review (OWASP)
- Acceptance criteria writing

### Hands-On Exercise 2.1: Plan Authentication Feature

**Task:** Create a complete plan for user login feature

**Scenario:**
You need to build a login page with:
- Email input field
- Password input field
- "Remember me" checkbox
- Submit button
- "Forgot password" link

**Commands to Try:**
```
plan user authentication
```

**CORTEX Will Ask You:**

**Q1: What EXACTLY does this feature do?**
```
Your Answer Example:
"Allows users to log in with email and password. 
Validates credentials against database. 
Shows error messages if login fails.
Redirects to dashboard on success."
```

**Q2: Who are the SPECIFIC users?**
```
Your Answer Example:
"Registered users with email accounts in our system.
Admin users (elevated permissions).
Guest users (limited access)."
```

**Q3: What are the EXACT systems/APIs/databases?**
```
Your Answer Example:
"UserDatabase (SQL Server)
AuthenticationAPI (JWT token generation)
SessionManager (cookie handling)
EmailService (password reset)"
```

**Q4: What are the MEASURABLE limits?**
```
Your Answer Example:
"Login response time: < 500ms
Failed login attempts: 3 max before lockout
Session timeout: 30 minutes
Password complexity: 8+ chars, 1 uppercase, 1 number"
```

**Q5: How do we MEASURE success?**
```
Your Answer Example:
"95% of logins complete in < 500ms
< 1% authentication errors (excluding wrong password)
Zero security vulnerabilities in penetration test
User satisfaction: 4.5+ stars"
```

**Q6: What files/services MUST exist?**
```
Your Answer Example:
"Controllers/AuthController.cs (to be created)
Models/User.cs (exists)
Services/AuthenticationService.cs (to be created)
Views/Login.cshtml (to be created)
appsettings.json (exists)"
```

**Q7: What security risks exist?**
```
Your Answer Example:
"SQL injection via email input
XSS via error messages
Brute force password attacks
Session hijacking
CSRF attacks"
```

---

### Understanding CORTEX's Response

**CORTEX will now:**

1. ✅ **Validate your answers** for ambiguity
2. ⚠️ **Challenge vague terms** (e.g., "improve" → "improve by how much?")
3. 🔒 **Run OWASP security review** automatically
4. 📋 **Check DoR completion** (all checkboxes)
5. ✅ **Generate planning document** when approved

**Expected Output:**
```
✅ DoR Status: COMPLETE

✓ Requirements documented (zero ambiguity)
✓ Dependencies identified & validated
✓ Technical design approach agreed
✓ Test strategy defined
✓ Acceptance criteria measurable
✓ Security review passed (OWASP checklist complete)
✓ User approval on scope

Creating: cortex-brain/documents/planning/features/PLAN-20251125-authentication.md
```

---

### Hands-On Exercise 2.2: Review Planning Document

**Task:** Open and review the generated plan

**File Location:**
```
cortex-brain/documents/planning/features/PLAN-20251125-authentication.md
```

**What to Look For:**
- ✅ Phase breakdown (Foundation → Core → Validation)
- ✅ Risk analysis section
- ✅ Security hardening tasks
- ✅ Task generation with acceptance criteria
- ✅ Milestone-based implementation plan

**Understanding Check:**
- ✅ Can you identify Phase 1 tasks?
- ✅ Are security risks documented?
- ✅ Are acceptance criteria measurable?
- ✅ Is DoD (Definition of Done) clear?

---

### Hands-On Exercise 2.3: Approve Plan

**Task:** Approve the plan to move to implementation

**Commands to Try:**
```
approve plan
```

**Expected Output:**
```
✅ Plan approved and moved to approved/
✅ Ready for implementation
✅ TDD workflow can now begin

Planning file moved to:
cortex-brain/documents/planning/features/approved/APPROVED-20251125-authentication.md
```

---

## 💻 Module 3: Development with TDD (8-10 min)

### What You'll Learn
- RED→GREEN→REFACTOR cycle
- Test-first development
- Auto-debug on failures
- Performance-based refactoring
- Test location isolation

### Hands-On Exercise 3.1: Start TDD Workflow

**Task:** Initialize TDD session for authentication feature

**Commands to Try:**
```
start tdd workflow for user authentication
```

**Expected Output:**
```
✅ Workspace discovered: [Your project type]
✅ Test framework: [pytest/jest/xunit detected]
✅ Ready for RED state - write your failing test

TDD Session ID: tdd-20251125-123456
Phase: RED (Write Failing Test)
```

---

### Hands-On Exercise 3.2: Discover UI Elements (View Discovery)

**Task:** Auto-discover element IDs before writing tests

**Commands to Try:**
```
discover views in src/Views/Account/Login.cshtml
```

**Expected Output:**
```
🔍 Scanning: Login.cshtml

✅ Found 5 elements:
   • #emailInput (text input)
   • #passwordInput (password input)
   • #rememberMeCheckbox (checkbox)
   • #loginButton (submit button)
   • #forgotPasswordLink (link)

✅ Stored in brain (Tier 2)
✅ Available for test generation

Selector strategies generated:
   • By ID: #emailInput
   • By Name: input[name="email"]
   • By Aria-Label: input[aria-label="Email"]
```

**Time Saved:** 60+ minutes of manual inspection → <5 minutes automated

---

### Hands-On Exercise 3.3: Generate Tests (RED Phase)

**Task:** Create failing tests for login functionality

**Commands to Try:**
```
generate tests for login validation
```

**CORTEX will:**
1. ✅ Use discovered element IDs (95%+ accuracy)
2. ✅ Generate test file in YOUR repo (not CORTEX folder)
3. ✅ Follow YOUR naming conventions
4. ✅ Use YOUR test framework

**Expected Output:**
```
✅ Test file created: tests/test_login_validation.py

Generated 6 tests:
   • test_valid_login_redirects_to_dashboard
   • test_invalid_email_shows_error
   • test_invalid_password_shows_error
   • test_empty_fields_show_validation_errors
   • test_remember_me_persists_session
   • test_forgot_password_link_navigates

Using real element IDs:
   #emailInput, #passwordInput, #loginButton
```

---

### Hands-On Exercise 3.4: Run Tests (Expect Failures - RED State)

**Task:** Execute tests to confirm RED state

**Commands to Try:**
```
run tests
```

**Expected Output:**
```
🔧 Running tests with pytest...

❌ FAILED tests/test_login_validation.py::test_valid_login_redirects_to_dashboard
   AssertionError: Element #emailInput not found

❌ FAILED tests/test_login_validation.py::test_invalid_email_shows_error
   NotImplementedError: validate_email() not implemented

Tests completed in 2.50s
   Passed: 0 ✓
   Failed: 6 ✗

❌ Entering RED state (expected)

📊 Auto-Debug Session Started
   Debug ID: debug-20251125-123456
   Tracking function execution...
```

**Understanding Check:**
- ✅ Tests failed as expected (RED state)
- ✅ Auto-debug session started automatically
- ✅ Error messages are clear

---

### Hands-On Exercise 3.5: Implement Feature (GREEN Phase)

**Task:** Write code to pass tests

**What to Implement:**

**File: Controllers/AuthController.cs**
```csharp
public class AuthController : Controller
{
    private readonly IAuthenticationService _authService;

    public AuthController(IAuthenticationService authService)
    {
        _authService = authService;
    }

    [HttpPost]
    public async Task<IActionResult> Login(LoginViewModel model)
    {
        if (!ModelState.IsValid)
            return View(model);

        var result = await _authService.ValidateCredentials(
            model.Email, 
            model.Password
        );

        if (result.Success)
        {
            // Create session
            await _authService.CreateSession(
                result.User, 
                model.RememberMe
            );
            
            return RedirectToAction("Dashboard", "Home");
        }

        ModelState.AddModelError("", "Invalid email or password");
        return View(model);
    }
}
```

**File: Services/AuthenticationService.cs**
```csharp
public class AuthenticationService : IAuthenticationService
{
    private readonly UserDbContext _db;

    public async Task<AuthResult> ValidateCredentials(
        string email, 
        string password)
    {
        var user = await _db.Users
            .FirstOrDefaultAsync(u => u.Email == email);

        if (user == null)
            return AuthResult.Failed("User not found");

        if (!BCrypt.Verify(password, user.PasswordHash))
            return AuthResult.Failed("Invalid password");

        return AuthResult.Success(user);
    }

    public async Task CreateSession(User user, bool rememberMe)
    {
        var session = new Session
        {
            UserId = user.Id,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = rememberMe 
                ? DateTime.UtcNow.AddDays(30)
                : DateTime.UtcNow.AddMinutes(30)
        };

        _db.Sessions.Add(session);
        await _db.SaveChangesAsync();
    }
}
```

---

### Hands-On Exercise 3.6: Run Tests Again (Expect Pass - GREEN State)

**Task:** Verify tests pass after implementation

**Commands to Try:**
```
run tests
```

**Expected Output:**
```
🔧 Running tests with pytest...

✅ PASSED tests/test_login_validation.py::test_valid_login_redirects_to_dashboard
✅ PASSED tests/test_login_validation.py::test_invalid_email_shows_error
✅ PASSED tests/test_login_validation.py::test_invalid_password_shows_error
✅ PASSED tests/test_login_validation.py::test_empty_fields_show_validation_errors
✅ PASSED tests/test_login_validation.py::test_remember_me_persists_session
✅ PASSED tests/test_login_validation.py::test_forgot_password_link_navigates

Tests completed in 3.20s
   Passed: 6 ✓
   Failed: 0 ✗

✅ Entering GREEN state

📊 Performance Data Captured:
   • ValidateCredentials: avg 145ms (SLOW_FUNCTION detected)
   • CreateSession: avg 89ms (acceptable)
   • DatabaseQuery: total 850ms (BOTTLENECK detected)

💡 Auto-Feedback Collection triggered
   Creating feedback report...
```

**Understanding Check:**
- ✅ All tests passing (GREEN state)
- ✅ Performance data captured automatically
- ✅ Bottlenecks identified
- ✅ Feedback report created

---

### Hands-On Exercise 3.7: Refactor (REFACTOR Phase)

**Task:** Get performance-based refactoring suggestions

**Commands to Try:**
```
suggest refactorings
```

**Expected Output:**
```
🎯 Found 3 performance issues:

1. ValidateCredentials() - SLOW_FUNCTION (avg 145ms)
   Confidence: 0.95
   Suggestion: Add caching for user lookups
   Impact: 70% faster (145ms → 45ms)
   
   Recommended Change:
   • Add MemoryCache for User objects
   • Cache key: "user:email:{email}"
   • TTL: 5 minutes
   
2. DatabaseQuery() - BOTTLENECK (total 850ms)
   Confidence: 0.95
   Suggestion: Add indexes on Email and PasswordHash columns
   Impact: 60% faster (850ms → 340ms)
   
   Recommended Change:
   • CREATE INDEX IX_Users_Email ON Users(Email)
   • Consider query optimization

3. CheckPermissions() - HOT_PATH (called 23 times)
   Confidence: 0.95
   Suggestion: Batch permission checks
   Impact: 50% fewer queries
   
   Recommended Change:
   • Load all permissions in single query
   • Use in-memory filter instead of repeated DB calls
```

---

### Hands-On Exercise 3.8: Apply Refactoring

**Task:** Implement suggested improvements

**Add Caching:**
```csharp
public class AuthenticationService : IAuthenticationService
{
    private readonly UserDbContext _db;
    private readonly IMemoryCache _cache;

    public async Task<AuthResult> ValidateCredentials(
        string email, 
        string password)
    {
        // Check cache first
        var cacheKey = $"user:email:{email}";
        if (_cache.TryGetValue(cacheKey, out User cachedUser))
        {
            if (BCrypt.Verify(password, cachedUser.PasswordHash))
                return AuthResult.Success(cachedUser);
            
            return AuthResult.Failed("Invalid password");
        }

        // Cache miss - query database
        var user = await _db.Users
            .FirstOrDefaultAsync(u => u.Email == email);

        if (user == null)
            return AuthResult.Failed("User not found");

        // Cache user for 5 minutes
        _cache.Set(cacheKey, user, TimeSpan.FromMinutes(5));

        if (!BCrypt.Verify(password, user.PasswordHash))
            return AuthResult.Failed("Invalid password");

        return AuthResult.Success(user);
    }
}
```

---

### Hands-On Exercise 3.9: Validate Refactoring

**Task:** Run tests to ensure refactoring didn't break anything

**Commands to Try:**
```
run tests
```

**Expected Output:**
```
✅ All tests still passing (6/6)
✅ Performance improved:
   • ValidateCredentials: 145ms → 48ms (67% faster)
   • Total test time: 3.20s → 1.85s (42% faster)

✅ REFACTOR phase complete
✅ Ready for session completion
```

---

### Hands-On Exercise 3.10: Create Git Checkpoint

**Task:** Save your work with SKULL Rule #8 compliance

**Commands to Try:**
```
git checkpoint
```

**Expected Output:**
```
✅ Git checkpoint created
   Commit SHA: a1b2c3d4
   Message: "feat: Add user authentication with caching optimization"
   
✅ SKULL Rule #8 compliance verified
✅ Work state preserved
```

---

## ✅ Module 4: Testing & Validation (5-7 min)

### What You'll Learn
- Code quality validation
- Lint checking
- Session completion reports
- Deployment readiness

### Hands-On Exercise 4.1: Validate Code Quality

**Task:** Run lint validation before completion

**Commands to Try:**
```
validate lint
```

**Expected Output:**
```
🔍 Running code quality checks...

✅ No critical violations found
⚠️ 2 warnings (non-blocking):
   • Line 45: Consider using async/await pattern
   • Line 67: Variable name could be more descriptive

✅ Ready to proceed to session completion
```

---

### Hands-On Exercise 4.2: Complete TDD Session

**Task:** Generate session completion report

**Commands to Try:**
```
complete session
```

**Expected Output:**
```
📊 TDD Session Completion Report

Session ID: tdd-20251125-123456
Duration: 18 minutes 32 seconds

**Before Session:**
• Tests: 0 passing
• Code coverage: 0%
• Performance baseline: N/A

**After Session:**
• Tests: 6 passing (100% pass rate)
• Code coverage: 87%
• Performance: 42% improvement

**Accomplishments:**
✅ Implemented user authentication
✅ Added password validation
✅ Optimized with caching (67% faster)
✅ Created 6 comprehensive tests
✅ Zero critical lint violations

**Files Modified:**
• Controllers/AuthController.cs (created)
• Services/AuthenticationService.cs (created)
• Views/Login.cshtml (modified)
• tests/test_login_validation.py (created)

Report saved: cortex-brain/documents/reports/TDD-SESSION-20251125-123456.md
```

---

### Hands-On Exercise 4.3: Generate Feedback Report

**Task:** Share performance metrics with team

**Commands to Try:**
```
generate feedback report
```

**Expected Output:**
```
📊 Generating comprehensive feedback report...

**8-Category Metrics Collected:**

1. Performance Metrics
   • Response time: 48ms (excellent)
   • Memory usage: 125MB (normal)

2. Reliability Metrics
   • Success rate: 100%
   • Error rate: 0%

3. Usage Patterns
   • TDD workflow: Used
   • Planning: Completed
   • View discovery: Utilized

4. Context Quality
   • Relevance score: 0.92 (high)
   • Retrieval accuracy: 95%

5. User Satisfaction
   • Workflow completion: 100%
   • No errors encountered

6. Brain Health
   • Database size: 45MB
   • Last cleanup: 2 days ago

7. Integration Depth
   • Feature completeness: 95%
   • All modules wired

8. Platform Stability
   • OS: macOS
   • No platform-specific issues

✅ Report created: cortex-brain/feedback/reports/FEEDBACK-20251125-123456.md
✅ Uploaded to GitHub Gist (private)
✅ Gist URL: https://gist.github.com/[your-gist-id]
```

---

## 🎓 Tutorial Completion

### What You've Learned

✅ **CORTEX Basics**
- Help system navigation
- Brain memory system
- Health checking

✅ **Planning Workflow**
- DoR validation process
- Security review (OWASP)
- Acceptance criteria writing
- Plan approval workflow

✅ **TDD Development**
- RED→GREEN→REFACTOR cycle
- View discovery automation
- Test generation with real IDs
- Performance-based refactoring
- Auto-debug on failures

✅ **Testing & Validation**
- Lint validation
- Session completion reports
- Feedback generation
- Git checkpoints

---

### Next Steps

**🚀 Practice More:**
1. Plan another feature using `plan [feature name]`
2. Try TDD workflow on your own code
3. Explore view discovery in different file types
4. Generate feedback reports regularly

**📚 Learn Advanced Features:**
1. System alignment (`align report`)
2. Upgrade system (`upgrade cortex`)
3. Brain export/import (`export brain`)
4. Admin operations (`admin help`)

**🤝 Join Community:**
1. Share feedback reports with team
2. Report issues (`feedback bug`)
3. Suggest improvements (`feedback improvement`)
4. Review documentation in `.github/prompts/modules/`

---

## 🏛️ Module 5: Architecture Intelligence (5-7 min)

### What You'll Learn
- Strategic architecture health analysis
- Trend tracking and forecasting
- Technical debt estimation
- Using reports for sprint planning

### Hands-On Exercise 5.1: Run Architecture Review

**Task:** Generate comprehensive architecture health report

**Commands to Try:**
```
review architecture
```

**Expected Output:**
```
🏛️ Architecture Review Complete

Overall Health: 78/100 (Warning)

Layer Breakdown:
- Discovery: 95% (19 features) ✅
- Import: 90% (18 features) ✅
- Instantiation: 85% (17 features) ✅
- Documentation: 75% (15 features) ⚠️
- Testing: 70% (14 features) ⚠️
- Wiring: 80% (16 features) ✅
- Optimization: 65% (13 features) ❌

Feature Status:
- Healthy (90-100%): 13 features
- Warning (70-89%): 5 features
- Critical (<70%): 1 feature

Report saved: cortex-brain/documents/analysis/architecture-review-20251127-143022.md
```

**Understanding Check:**
- ✅ What's the overall health score?
- ✅ Which layer has the lowest score?
- ✅ How many features need attention (Warning + Critical)?

---

### Hands-On Exercise 5.2: Interpret Health Report

**Task:** Open and analyze the generated report

**File Location:**
```
cortex-brain/documents/analysis/architecture-review-[timestamp].md
```

**What to Look For:**

**1. Executive Summary:**
```markdown
Current architecture health: 78% (Warning). System has improved 5% 
over the last 30 days, showing consistent upward trend. Primary 
recommendation: Address 12 features in Warning state (70-89%) to 
reach Healthy threshold.
```

**2. Trend Analysis (if historical data exists):**
```markdown
Trend Analysis (Last 30 Days):
- Velocity: +5.2% improvement
- Direction: Improving ↗️
- Volatility: 2.3 (Low - predictable changes)
```

**3. Technical Debt Forecast:**
```markdown
3-Month Projection:
- Predicted Score: 83% (↗️ +5% from current)
- Confidence: 0.85 (High)

6-Month Projection:
- Predicted Score: 88% (↗️ +10% from current)
- Confidence: 0.72 (Medium)

Current Debt Estimate: 14 hours
```

**4. CORTEX 4.0 Recommendations:**
```markdown
1. **Improve Testing Coverage** (HIGH Priority)
   Expected Impact: +5% overall health
   
2. **Complete Documentation** (MEDIUM Priority)
   Expected Impact: +3% overall health
   
3. **Optimize Benchmarks** (LOW Priority)
   Expected Impact: +2% overall health
```

**Understanding Check:**
- ✅ Is the system improving or degrading?
- ✅ What's the debt estimate in hours?
- ✅ What's the highest priority recommendation?

---

### Hands-On Exercise 5.3: Track Evolution Over Time

**Task:** Run multiple reviews to build historical data

**Workflow:**
```
Week 1: review architecture (baseline)
Week 2: review architecture (after improvements)
Week 3: review architecture (validate trend)
```

**Expected Progression:**
```
Week 1: 78% (Warning) - Baseline established
Week 2: 80% (Warning) - +2% improvement, velocity detected
Week 3: 82% (Warning) - +4% total, trend confirmed
```

**Commands to Check Trends:**
```
track architecture evolution
```

**Expected Output:**
```
Architecture Evolution Report

Historical Snapshots: 3
Date Range: 2025-11-20 to 2025-11-27 (7 days)

Health Progression:
- Week 1: 78% (Baseline)
- Week 2: 80% (+2%)
- Week 3: 82% (+2%)

Trend Metrics:
- Average Velocity: +2.0% per week
- Direction: Improving ↗️
- Volatility: 1.2 (Low - very consistent)

Insights:
✅ Consistent improvement maintained
✅ Low volatility indicates stable development practices
✅ On track to reach 85% (Warning → Healthy boundary) in 2 weeks
```

**Understanding Check:**
- ✅ What's the average velocity?
- ✅ Is the trend improving or degrading?
- ✅ When will system reach 85% if trend continues?

---

### Hands-On Exercise 5.4: Use Forecasts for Sprint Planning

**Task:** Plan remediation work based on debt forecast

**Scenario:**
Your architecture review shows:
- Current health: 78%
- Target: 90% (Healthy threshold)
- Debt estimate: 14 hours
- Sprint capacity: 2 hours/sprint for technical debt

**Commands to Try:**
```
forecast technical debt
```

**Expected Output:**
```
Technical Debt Forecast

Current State:
- Health: 78%
- Gap to Healthy (90%): 12%
- Estimated Work: 14 hours

3-Month Projection (Doing Nothing):
- Predicted Health: 81% (natural drift)
- Confidence: 0.88
- Still in Warning zone

3-Month Projection (With Remediation):
- Add 14 hours work over 7 sprints (2h per sprint)
- Predicted Health: 91% (Healthy threshold!)
- Confidence: 0.92

Sprint Plan Recommendation:
- Sprint 1-2: Address 5 testing gaps (4h)
- Sprint 3-4: Complete 3 documentation items (6h)
- Sprint 5-6: Optimize 1 performance benchmark (4h)
- Sprint 7: Validation and contingency

Expected Outcome: Healthy status in 7 sprints (14 weeks)
```

**Create Sprint Plan:**
```
Sprint 1 (This Week):
☐ Add tests for AuthenticationService (2h)

Sprint 2 (Next Week):
☐ Add tests for PaymentProcessor (2h)

Sprint 3:
☐ Write architecture-guide.md for API module (2h)

... (continue for remaining sprints)
```

**Understanding Check:**
- ✅ How many sprints to reach Healthy threshold?
- ✅ What's the first remediation task?
- ✅ Can you explain the confidence scores?

---

### Hands-On Exercise 5.5: Compare Strategic vs Tactical Analysis

**Task:** Understand difference between Architecture Intelligence and System Alignment

**Run Both:**
```
# Strategic (RIGHT BRAIN)
review architecture

# Tactical (LEFT BRAIN)
align report
```

**Compare Outputs:**

**Architecture Intelligence (Strategic):**
```
Focus: Where are we going?
Output:
- Trend analysis (velocity, direction, volatility)
- Debt forecasting (3-month, 6-month projections)
- ADR recommendations (prioritized improvements)
- Historical tracking (evolution over time)

Use Cases:
- Sprint planning (allocate technical debt time)
- Quarterly goals (set health targets)
- Team retrospectives (measure improvement)
- Leadership reporting (communicate architecture health)
```

**System Alignment (Tactical):**
```
Focus: What's broken right now?
Output:
- 7-layer integration validation
- Auto-remediation templates (wiring, tests, docs)
- Convention-based feature discovery
- Deployment readiness checks

Use Cases:
- Pre-deployment validation (block if <80% health)
- New feature validation (ensure fully wired)
- Template generation (auto-fix specific issues)
- CI/CD integration (automated quality gates)
```

**Understanding Check:**
- ✅ When would you use Architecture Intelligence vs System Alignment?
- ✅ Can they work together? How?
- ✅ Which one tells you "what to fix"? Which tells you "how to fix it"?

---

### Module 5 Completion Checklist

**You've mastered Architecture Intelligence when you can:**

✅ **Run architecture review** and interpret health scores  
✅ **Understand layer breakdown** (Discovery → Optimization)  
✅ **Read trend analysis** (velocity, direction, volatility)  
✅ **Use debt forecasts** for sprint planning  
✅ **Track evolution** over multiple reviews  
✅ **Apply ADR recommendations** to improve health  
✅ **Distinguish strategic vs tactical** analysis  
✅ **Combine both approaches** for comprehensive validation  

---

## 📖 Reference Commands

### Quick Command Reference

| Command | Purpose | Duration |
|---------|---------|----------|
| `help` | Show all commands | <1s |
| `plan [feature]` | Start planning | 3-5 min |
| `start tdd` | Begin TDD workflow | <1s |
| `discover views` | Find element IDs | <5 min |
| `run tests` | Execute tests | 1-5s |
| `suggest refactorings` | Get optimization ideas | <1s |
| `validate lint` | Check code quality | <1s |
| `complete session` | Generate report | <1s |
| `git checkpoint` | Save work | <1s |
| `feedback` | Share metrics | <1s |
| `review architecture` | Architecture health analysis | 1-2s |
| `track architecture evolution` | Historical trend tracking | <1s |
| `forecast technical debt` | 3/6-month projections | <1s |

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Plan approval failed - DoR incomplete"**
- **Cause:** Vague answers to clarifying questions
- **Fix:** Be specific with measurable criteria
- **Example:** "faster" → "response time < 500ms"

**Issue: "Tests not found"**
- **Cause:** Test file location not detected
- **Fix:** Ensure tests in correct directory (e.g., `tests/`)
- **Check:** `discover views` before test generation

**Issue: "View discovery returned 0 elements"**
- **Cause:** File path incorrect or file type not supported
- **Fix:** Check file exists, verify .razor/.cshtml extension
- **Supported:** Razor, Blazor, React, Vue, HTML

**Issue: "Refactoring suggestions not showing"**
- **Cause:** No performance data captured
- **Fix:** Run tests first to capture timing data
- **Note:** GREEN state required for refactoring

---

## 💡 Pro Tips

### Efficiency Tips

1. **Use Natural Language**
   - ✅ "plan authentication feature"
   - ❌ `/plan --feature auth --type security`

2. **Let CORTEX Discover**
   - ✅ `discover views` before writing tests
   - ❌ Manually inspect HTML for IDs

3. **Trust the RED State**
   - ✅ Let tests fail first (RED)
   - ❌ Don't implement before tests exist

4. **Review Refactoring Suggestions**
   - ✅ Consider performance impact
   - ❌ Don't blindly apply all suggestions

5. **Create Checkpoints Often**
   - ✅ After each GREEN state
   - ❌ Wait until end of day

---

## 🎯 Success Criteria

### Tutorial Complete When You Can:

✅ **Plan a feature** with zero ambiguity (DoR complete)  
✅ **Start TDD workflow** and understand RED/GREEN/REFACTOR  
✅ **Use view discovery** to auto-extract element IDs  
✅ **Generate tests** that use real element selectors  
✅ **Run tests** and interpret results  
✅ **Implement features** to pass tests (GREEN state)  
✅ **Apply refactorings** based on performance data  
✅ **Complete sessions** with comprehensive reports  
✅ **Share feedback** with team via GitHub Gist  
✅ **Run architecture reviews** and interpret health metrics  
✅ **Track architecture evolution** over time  
✅ **Use debt forecasts** for sprint planning  
✅ **Apply strategic and tactical analysis** together  

---

**Tutorial Version:** 2.0 (Added Module 5: Architecture Intelligence)  
**Last Updated:** November 27, 2025  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
