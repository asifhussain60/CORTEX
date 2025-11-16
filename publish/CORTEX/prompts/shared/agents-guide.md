# CORTEX Agents Guide - How CORTEX Thinks

**Purpose:** Complete guide to the CORTEX agent system and workflow orchestration  
**Audience:** Developers, users wanting to understand how CORTEX makes decisions  
**Version:** 2.0 (Full Module)  
**Status:** Production Ready

---

## 🤖 Overview

CORTEX uses a **dual-hemisphere agent architecture** inspired by the human brain. Ten specialist agents work together, divided between tactical execution (left brain) and strategic planning (right brain), coordinated through a corpus callosum message system.

```
RIGHT BRAIN (Strategic)        CORPUS CALLOSUM         LEFT BRAIN (Tactical)
┌─────────────────────┐       ┌──────────────┐        ┌────────────────────┐
│ 1. Intent Router    │──────▶│  Coordination │◀──────│ 6. Code Executor   │
│ 2. Work Planner     │       │  Message Queue│       │ 7. Test Generator  │
│ 3. Screenshot       │       │               │       │ 8. Error Corrector │
│    Analyzer         │       │  Tasks →      │       │ 9. Health          │
│ 4. Change Governor  │       │  ← Results    │       │    Validator       │
│ 5. Brain Protector  │       │               │       │ 10. Commit Handler │
└─────────────────────┘       └──────────────┘        └────────────────────┘
  Strategy & Planning           Coordination            Execution & Testing
```

---

## 🧭 Intent Detection & Routing

### The Intent Router (Agent #1)

**Location:** `src/agents/intent_router.py`  
**Hemisphere:** Right Brain  
**Purpose:** Understand natural language and route to appropriate specialist

#### How It Works

1. **Parse User Request** - Extract keywords, entities, context
2. **Match Intent Pattern** - Compare against learned patterns (Tier 2)
3. **Calculate Confidence** - Score based on keyword matches and context
4. **Route to Agent** - Direct to specialist if confidence > threshold
5. **Request Clarification** - If ambiguous, ask user for more detail

#### Intent Types & Routing

| Intent | Agent | Trigger Words | Example Requests |
|--------|-------|---------------|------------------|
| **PLAN** | Work Planner | "create plan", "design", "architecture", "how should I" | "Create a plan to add authentication" |
| **EXECUTE** | Code Executor | "add", "create", "implement", "build", "modify" | "Add a purple button to the panel" |
| **TEST** | Test Generator | "test", "verify", "validate", "check behavior" | "Test the login functionality" |
| **FIX** | Error Corrector | "fix", "bug", "error", "broken", "not working" | "Fix the null reference error" |
| **VALIDATE** | Health Validator | "check health", "validate system", "run all tests" | "Validate the system is working" |
| **ANALYZE** | Screenshot Analyzer | "analyze image", "what's in this", "screenshot" | "Analyze this UI screenshot" |
| **PROTECT** | Brain Protector | "modify tier0", "change rules", "delete" | "Delete all brain data" (challenged!) |
| **CONTINUE** | (resume) | "continue", "next", "keep going", "proceed" | "Continue with the next phase" |
| **STATUS** | (system) | "status", "health", "how is", "show me" | "Show me the system status" |

#### Example: Intent Detection

**User Input:**
```
"Add authentication to the login page"
```

**Intent Router Processing:**
```python
{
  "parsed_request": {
    "action": "add",
    "feature": "authentication",
    "location": "login page"
  },
  "intent": "EXECUTE",
  "confidence": 0.88,
  "reasoning": [
    "Keyword 'add' matches EXECUTE (0.9)",
    "No planning keywords detected",
    "Specific implementation requested"
  ],
  "routed_to": "code-executor",
  "suggested_workflow": "feature_development",
  "context_check": "No active session found - will create new"
}
```

---

## 🎯 Right Brain Agents (Strategic Planning)

### Agent #1: Intent Router

**Already covered above** ↑

---

### Agent #2: Work Planner

**Location:** `src/agents/work_planner.py`  
**Hemisphere:** Right Brain  
**Purpose:** Create multi-phase strategic implementation plans

#### Responsibilities

1. **Analyze Requirements** - Extract what needs to be done
2. **Break Into Phases** - Divide work into logical stages
3. **Create Tasks** - Define specific, actionable tasks per phase
4. **Estimate Effort** - Predict time/complexity for each phase
5. **Assess Risks** - Identify potential issues or blockers
6. **Define Success Criteria** - Clear "Definition of Done" per phase

#### Planning Process

```
User Request: "Add user authentication"
                    ↓
┌─────────────────────────────────────────────┐
│ Phase 1: Requirements Analysis              │
│ ✓ Define authentication requirements        │
│ ✓ Identify affected layers (UI, API, DB)    │
│ ✓ Check for existing auth patterns          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Phase 2: Test Creation                      │
│ ✓ Write failing login tests (RED)           │
│ ✓ Write failing registration tests (RED)    │
│ ✓ Write failing authorization tests (RED)   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Phase 3: Implementation                     │
│ ✓ Implement User model                      │
│ ✓ Implement AuthService                     │
│ ✓ Implement LoginController                 │
│ ✓ Make all tests pass (GREEN)               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Phase 4: Refactoring & Validation           │
│ ✓ Refactor code for clarity (REFACTOR)      │
│ ✓ Run full test suite                       │
│ ✓ Validate zero errors/warnings (DoD)       │
└─────────────────────────────────────────────┘
```

#### Example Output

```yaml
plan:
  feature: "User Authentication"
  complexity: "medium"
  estimated_hours: 4.5
  
  phases:
    - phase: 1
      name: "Requirements & Design"
      agent: "work-planner"
      duration_minutes: 30
      tasks:
        - "Define authentication requirements"
        - "Review existing user model"
        - "Identify security considerations"
      success_criteria:
        - "Clear requirements documented"
        - "Architecture sketch created"
    
    - phase: 2
      name: "Test Creation (RED)"
      agent: "test-generator"
      duration_minutes: 60
      tasks:
        - "Write login tests (expect fail)"
        - "Write registration tests (expect fail)"
        - "Write authorization tests (expect fail)"
      success_criteria:
        - "All tests written"
        - "All tests fail as expected (RED phase)"
    
    - phase: 3
      name: "Implementation (GREEN)"
      agent: "code-executor"
      duration_minutes: 120
      tasks:
        - "Create User model with password hashing"
        - "Implement AuthService"
        - "Implement LoginController"
        - "Make all tests pass"
      success_criteria:
        - "All tests passing (GREEN phase)"
        - "No errors or warnings"
    
    - phase: 4
      name: "Refactor & Validate"
      agent: "health-validator"
      duration_minutes: 60
      tasks:
        - "Refactor for clarity and SOLID principles"
        - "Run full test suite"
        - "Security audit"
      success_criteria:
        - "Code is clean and maintainable (REFACTOR phase)"
        - "All tests passing"
        - "Zero errors, zero warnings (DoD)"
  
  risks:
    - "Password hashing library may need installation"
    - "Session management complexity"
    - "Security best practices must be followed"
  
  dependencies:
    - "Database with Users table"
    - "Session storage mechanism"
```

---

### Agent #3: Screenshot Analyzer

**Location:** `src/agents/screenshot_analyzer.py`  
**Hemisphere:** Right Brain  
**Purpose:** Extract technical requirements from UI screenshots/mockups

#### Capabilities

1. **Component Identification** - Recognize UI elements (buttons, inputs, etc.)
2. **Layout Analysis** - Understand spatial relationships
3. **Style Extraction** - Detect colors, fonts, spacing
4. **Behavior Inference** - Deduce expected interactions
5. **Technical Specification** - Generate implementation requirements

#### Analysis Process

**User provides screenshot:**
```
"Analyze this login page design"
[image: login-mockup.png]
```

**Screenshot Analyzer Output:**
```yaml
analysis:
  identified_components:
    - type: "text_input"
      label: "Username"
      id_suggestion: "input-username"
      properties:
        placeholder: "Enter username"
        required: true
    
    - type: "password_input"
      label: "Password"
      id_suggestion: "input-password"
      properties:
        placeholder: "Enter password"
        required: true
    
    - type: "button"
      label: "Login"
      id_suggestion: "btn-login"
      properties:
        color: "#4A90E2" (primary blue)
        action: "submit_form"
    
    - type: "link"
      label: "Forgot Password?"
      id_suggestion: "link-forgot-password"
      properties:
        destination: "/forgot-password"
  
  layout:
    structure: "centered_card"
    width: "400px"
    padding: "32px"
    background: "white with shadow"
  
  technical_requirements:
    - "Create LoginForm component"
    - "Implement form validation (client-side)"
    - "Add submit handler with API call"
    - "Display error messages inline"
    - "Responsive design for mobile"
  
  suggested_tests:
    - "Test valid login submission"
    - "Test invalid credentials handling"
    - "Test empty field validation"
    - "Test 'forgot password' link navigation"
```

---

### Agent #4: Change Governor

**Location:** `src/agents/change_governor.py`  
**Hemisphere:** Right Brain  
**Purpose:** Protect CORTEX architectural integrity from degradation

#### Protection Responsibilities

1. **Application Separation** - Keep application code out of CORTEX core
2. **Scope Enforcement** - Prevent mixing of application and CORTEX concerns
3. **Architectural Compliance** - Enforce layered architecture
4. **Namespace Isolation** - Prevent cross-contamination
5. **Creeping Bloat Prevention** - Challenge unnecessary complexity

#### Example: Preventing Degradation

**User Request:**
```
"Add SignalR hub to CORTEX brain for real-time updates"
```

**Change Governor Response:**
```
⚠️ ARCHITECTURAL CONCERN DETECTED

Issue: Application-specific technology (SignalR) proposed for CORTEX core

Analysis:
  - SignalR is application-specific (KSESSIONS project)
  - CORTEX core should remain technology-agnostic
  - Violates Local-First principle (external dependency)
  - Creates tight coupling to specific application

Recommendation:
  ✅ Create SignalR hub in your application layer (KSESSIONS/)
  ✅ Use CORTEX as data source via API
  ✅ Keep CORTEX core pure and reusable

Alternative Architecture:
  Application Layer (KSESSIONS/)
    └─ SignalRHub.cs (your specific technology)
        └─ Calls CORTEX API
            └─ CORTEX Brain (technology-agnostic)

This maintains CORTEX portability and reusability.
Proceed with application-layer implementation?
```

---

### Agent #5: Brain Protector

**Location:** `src/agents/brain_protector.py`  
**Hemisphere:** Right Brain  
**Purpose:** Enforce Rule #22 - Challenge risky changes to CORTEX brain

#### Protection Layers (6 Total)

1. **Instinct Immutability** - Tier 0 rules cannot be bypassed
2. **Critical Path Protection** - Core files protected
3. **Application Separation** - No app code in CORTEX core
4. **Brain State Protection** - Conversation history not committed
5. **Namespace Isolation** - Scope boundaries enforced
6. **Architectural Integrity** - Design principles maintained

#### Challenge Workflow

**User Request:**
```
"Delete conversation history to save space"
```

**Brain Protector Challenge:**
```
🛡️ BRAIN PROTECTION TRIGGERED (Rule #22)

Severity: BLOCKED
Layer: Brain State Protection
Rule: brain_state_files

Detected Action:
  - Attempting to delete conversation history
  - Files: cortex-brain/tier1/conversations.db

Why This Is Risky:
  ❌ Permanently destroys conversation memory
  ❌ Breaks Tier 1 short-term memory system
  ❌ Cannot be undone - data loss is permanent
  ❌ Impacts "Make it purple" context continuity

Safer Alternatives:
  ✅ Use FIFO queue cleanup (automatically deletes oldest 20)
     Command: memory.cleanup_old_conversations()
  
  ✅ Export old conversations before deletion
     Command: python scripts/brain_export.py --output backup.zip
  
  ✅ Adjust FIFO limit in config (reduce from 20 to 10)
     File: cortex.config.json → tier1.maxConversations

  ✅ Archive conversations to long-term storage
     Command: memory.archive_conversations(older_than_days=90)

Do you want to proceed with one of these alternatives instead?
```

---

## 🔧 Left Brain Agents (Tactical Execution)

### Agent #6: Code Executor

**Location:** `src/agents/code_executor.py`  
**Hemisphere:** Left Brain  
**Purpose:** Implement features with surgical precision using TDD

#### Responsibilities

1. **Execute Plans** - Implement tasks from Work Planner
2. **Enforce TDD** - Always RED → GREEN → REFACTOR
3. **Precise Edits** - Exact file modifications, no guessing
4. **Incremental Creation** - Large files created in chunks (<100 lines at a time)
5. **Validate Changes** - Ensure syntax correctness

#### TDD Workflow

```
Phase 1: RED (Write Failing Test)
┌──────────────────────────────────────────┐
│ Create test file: LoginTests.cs         │
│                                          │
│ [Test]                                   │
│ public void Login_ValidCredentials()     │
│ {                                        │
│     var result = auth.Login("user", "pw");│
│     Assert.IsTrue(result.Success);       │
│ }                                        │
│                                          │
│ Status: ❌ Test FAILS (expected)         │
└──────────────────────────────────────────┘
                ↓
Phase 2: GREEN (Make It Pass)
┌──────────────────────────────────────────┐
│ Create implementation: AuthService.cs    │
│                                          │
│ public LoginResult Login(string username,│
│                          string password)│
│ {                                        │
│     // Minimal implementation            │
│     return new LoginResult { Success = true };│
│ }                                        │
│                                          │
│ Status: ✅ Test PASSES                   │
└──────────────────────────────────────────┘
                ↓
Phase 3: REFACTOR (Clean Up)
┌──────────────────────────────────────────┐
│ Refactor: Extract validation, add error │
│           handling, improve naming       │
│                                          │
│ public LoginResult Login(...)            │
│ {                                        │
│     ValidateCredentials(username, password);│
│     var user = _repo.FindByUsername(username);│
│     if (user == null || !user.VerifyPassword(password))│
│         return LoginResult.Failed;       │
│     return LoginResult.Success(user);    │
│ }                                        │
│                                          │
│ Status: ✅ All tests still pass          │
└──────────────────────────────────────────┘
```

#### File Validation

Before modifying any file, Code Executor:
1. ✅ Confirms file exists
2. ✅ Checks file is in correct layer
3. ✅ Validates write permissions
4. ✅ Prevents "wrong file" mistakes (learned from Tier 2)

---

### Agent #7: Test Generator

**Location:** `src/agents/test_generator.py`  
**Hemisphere:** Left Brain  
**Purpose:** Create comprehensive test suites (always RED phase first)

#### Test Creation Strategy

1. **Happy Path Tests** - Verify expected behavior
2. **Edge Case Tests** - Boundary conditions, limits
3. **Error Handling Tests** - Invalid inputs, exceptions
4. **Integration Tests** - Component interactions
5. **Regression Tests** - Prevent known bugs from returning

#### Example: Login Feature Tests

```csharp
public class LoginTests
{
    // Happy path
    [Test]
    public void Login_WithValidCredentials_ReturnsSuccess()
    {
        var result = _authService.Login("validuser", "correctpassword");
        Assert.IsTrue(result.Success);
        Assert.IsNotNull(result.User);
    }
    
    // Edge cases
    [Test]
    public void Login_WithEmptyUsername_ReturnsValidationError()
    {
        var result = _authService.Login("", "password");
        Assert.IsFalse(result.Success);
        Assert.AreEqual("Username required", result.Error);
    }
    
    [Test]
    public void Login_WithEmptyPassword_ReturnsValidationError()
    {
        var result = _authService.Login("user", "");
        Assert.IsFalse(result.Success);
        Assert.AreEqual("Password required", result.Error);
    }
    
    // Error handling
    [Test]
    public void Login_WithInvalidCredentials_ReturnsFailed()
    {
        var result = _authService.Login("user", "wrongpassword");
        Assert.IsFalse(result.Success);
        Assert.AreEqual("Invalid credentials", result.Error);
    }
    
    [Test]
    public void Login_WithNonexistentUser_ReturnsFailed()
    {
        var result = _authService.Login("nosuchuser", "password");
        Assert.IsFalse(result.Success);
    }
    
    // Security
    [Test]
    public void Login_FailedAttempt_DoesNotRevealUserExistence()
    {
        var result1 = _authService.Login("validuser", "wrongpassword");
        var result2 = _authService.Login("nosuchuser", "password");
        Assert.AreEqual(result1.Error, result2.Error); // Same generic message
    }
}
```

---

### Agent #8: Error Corrector

**Location:** `src/agents/error_corrector.py`  
**Hemisphere:** Left Brain  
**Purpose:** Fix bugs, syntax errors, and "wrong file" mistakes

#### Error Detection & Correction

1. **Syntax Errors** - Missing semicolons, brackets, typos
2. **Wrong File Errors** - Catches confusion (learned from Tier 2)
3. **Logic Errors** - Unexpected behavior, test failures
4. **Build Errors** - Compilation issues, missing dependencies
5. **Runtime Errors** - Null references, exceptions

#### Example: Wrong File Prevention

**Tier 2 Correction History shows:**
```
User asked to modify "HostControlPanel"
Copilot modified "HostControlPanelContent.razor" (WRONG)
Correction: Should have been "HostControlPanel.razor"
Pattern stored: Prevent confusion between similar names
```

**Next time:**
```
User: "Modify HostControlPanel"

Error Corrector checks Tier 2:
⚠️ WARNING: Similar file names detected
  - HostControlPanel.razor (likely correct)
  - HostControlPanelContent.razor (commonly confused)

Based on past corrections, I'll modify HostControlPanel.razor.
Proceed? (yes/no)
```

---

### Agent #9: Health Validator

**Location:** `src/agents/health_validator.py`  
**Hemisphere:** Left Brain  
**Purpose:** Enforce Definition of Done - zero errors, zero warnings

#### Validation Checks

1. **All Tests Pass** - No red tests allowed
2. **Zero Errors** - Compilation/syntax errors = FAIL
3. **Zero Warnings** - Even warnings must be fixed
4. **Build Succeeds** - Project builds cleanly
5. **No Regressions** - Existing features still work

#### Validation Report

```yaml
health_check:
  status: "FAIL" # or "PASS"
  timestamp: "2025-11-08T15:30:00Z"
  
  tests:
    total: 47
    passed: 45
    failed: 2
    skipped: 0
    status: "❌ FAIL"
  
  build:
    succeeded: false
    errors: 0
    warnings: 3
    status: "⚠️ WARNINGS"
  
  issues:
    - type: "test_failure"
      test: "LoginTests.Login_InvalidCredentials"
      message: "Expected 'Invalid credentials', got 'Login failed'"
    
    - type: "test_failure"
      test: "LoginTests.Login_EmptyPassword"
      message: "NullReferenceException thrown"
    
    - type: "warning"
      file: "AuthService.cs"
      line: 42
      message: "Variable 'user' is never used"
  
  definition_of_done:
    all_tests_pass: false # ❌
    zero_errors: true     # ✅
    zero_warnings: false  # ❌
    build_succeeds: true  # ✅
    
  verdict: "NOT DONE - Fix 2 test failures and 3 warnings"
```

---

### Agent #10: Commit Handler

**Location:** `src/agents/commit_handler.py`  
**Hemisphere:** Left Brain  
**Purpose:** Create semantic commits with meaningful messages

#### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Add/modify tests
- `docs`: Documentation
- `style`: Formatting
- `chore`: Maintenance

#### Example Commits

```git
feat(auth): Add user authentication system

- Implement AuthService with password hashing
- Add login endpoint to API
- Create comprehensive test suite (47 tests)
- All tests passing, zero errors/warnings

Closes #123
```

```git
fix(auth): Prevent null reference in login validation

- Add null checks for username and password
- Return validation error instead of throwing exception
- Add test coverage for null inputs

Fixes #125
```

---

## 🌉 Corpus Callosum (Coordination)

### Message Queue System

**Location:** `cortex-brain/corpus-callosum/coordination-queue.jsonl`  
**Purpose:** Coordinate communication between left and right hemispheres

#### Message Flow

```
Right Brain (Planner) creates plan
        ↓
Corpus Callosum: Post message
        {
          "type": "task_assignment",
          "from": "work-planner",
          "to": "code-executor",
          "task": {
            "phase": 2,
            "description": "Implement AuthService",
            "success_criteria": ["All tests pass"]
          }
        }
        ↓
Left Brain (Executor) receives task
        ↓
Left Brain executes with TDD
        ↓
Corpus Callosum: Post result
        {
          "type": "task_completion",
          "from": "code-executor",
          "to": "work-planner",
          "result": {
            "status": "complete",
            "tests_passing": 47,
            "files_modified": ["AuthService.cs"]
          }
        }
        ↓
Right Brain updates knowledge graph (Tier 2)
```

---

## 🎭 Agent Coordination Examples

### Example 1: Simple Feature Request

**User:** "Add a logout button"

```
1. Intent Router (Right)
   ↓ Detects: EXECUTE intent
   ↓ Routes to: Code Executor

2. Code Executor (Left)
   ↓ Checks: No plan exists
   ↓ Requests: Work Planner assistance

3. Work Planner (Right)
   ↓ Creates: Quick 2-phase plan
   ↓ Sends to: Code Executor via Corpus Callosum

4. Test Generator (Left)
   ↓ Creates: Button click test (RED)
   ↓ Confirms: Test fails

5. Code Executor (Left)
   ↓ Implements: Logout button
   ↓ Confirms: Test passes (GREEN)
   ↓ Refactors: Clean up code

6. Health Validator (Left)
   ↓ Validates: Zero errors, zero warnings
   ↓ Confirms: Definition of Done met

7. Commit Handler (Left)
   ↓ Creates: "feat(ui): Add logout button"
   ↓ Commits: Changes to git

8. Knowledge Graph (Right - Tier 2)
   ↓ Learns: "add button" → EXECUTE pattern
   ↓ Stores: button_creation_workflow
```

---

### Example 2: Complex Feature with Challenges

**User:** "Delete all CORTEX brain data"

```
1. Intent Router (Right)
   ↓ Detects: PROTECT intent (high severity keyword)
   ↓ Routes to: Brain Protector

2. Brain Protector (Right)
   ↓ Analyzes: Proposed deletion of brain state
   ↓ Triggers: Layer 4 (Brain State Protection)
   ↓ Blocks: Action with severity "blocked"
   ↓ Suggests: Safer alternatives

3. User Response: "I want to clean up old conversations"

4. Intent Router (Right)
   ↓ Re-detects: VALIDATE intent (cleanup)
   ↓ Routes to: Health Validator

5. Health Validator (Left)
   ↓ Recommends: FIFO queue cleanup method
   ↓ Executes: memory.cleanup_old_conversations()
   ↓ Reports: "5 old conversations archived, memory freed"

Result: Risk prevented, safe alternative executed
```

---

## 📚 For More Information

**Related Documentation:**
- **Technical API:** `#file:prompts/shared/technical-reference.md`
- **Setup Guide:** `#file:prompts/shared/setup-guide.md`
- **CORTEX Story:** `#file:prompts/shared/story.md`
- **Tracking Guide:** `#file:prompts/shared/tracking-guide.md`

---

**Version:** 2.0  
**Last Updated:** November 8, 2025  
**Phase:** 3.7 Complete - Full Modular Architecture  
**Agents:** 10 specialist agents operational
