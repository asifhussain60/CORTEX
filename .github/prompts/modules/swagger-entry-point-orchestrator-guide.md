# SWAGGER Entry Point Orchestrator Guide

**Purpose:** Definition of Ready (DoR) enforcement with ADO work item decomposition and time estimation  
**Version:** 1.1.0  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The SWAGGER Entry Point Orchestrator enforces Definition of Ready through interactive questioning before providing estimates. It decomposes large work items into Features and Stories with ADO-ready output and enhanced time estimates with parallel track analysis.

**Key Principle:** CORTEX should NEVER provide estimates if DoR is not complete.

**Features:**
- Interactive DoR validation (requirements, dependencies, technical, security, testing)
- Work item decomposition (Epics → Features → Stories → Tasks)
- Modified Fibonacci story point estimation (1, 2, 3, 5, 8, 13)
- TimeframeEstimator integration for parallel track analysis
- ADO-formatted markdown output (copy-paste ready)
- OWASP security review integration

---

## 🚀 Commands

**Natural Language Triggers:**
- `plan ado`
- `create ado work item`
- `ado story`
- `ado feature`
- `plan feature with ado format`
- `estimate work item`

**Use Cases:**
- Planning new features with ADO tracking
- Breaking down large epics into stories
- Estimating development timeframes
- Ensuring requirements are well-defined
- Creating sprint-ready work items

---

## 📊 Workflow Steps

### Phase 1: DoR Validation (5-10 min)
```
Interactive questioning across 5 categories:

1. Requirements - What are we building? For whom? Why?
2. Dependencies - External APIs? Third-party libs? Team dependencies?
3. Technical - Architecture constraints? Performance targets? Scale requirements?
4. Security - Authentication? Authorization? Data sensitivity?
5. Testing - Test strategy? Coverage targets? QA requirements?

Scoring:
- 100% = COMPLETE (can estimate)
- 80-99% = IN_PROGRESS (missing 1-2 answers)
- 50-79% = INCOMPLETE (significant gaps)
- <50% = NOT_STARTED (cannot estimate)
```

### Phase 2: Work Item Decomposition (15-20 min)
```
Hierarchical breakdown:

Epic (13+ story points)
  ├─ Feature 1 (5-8 story points)
  │   ├─ User Story 1.1 (2-3 points)
  │   │   ├─ Task 1.1.1 (implementation)
  │   │   ├─ Task 1.1.2 (testing)
  │   │   └─ Task 1.1.3 (documentation)
  │   └─ User Story 1.2 (2-3 points)
  └─ Feature 2 (5-8 story points)

Rules:
- Stories >8 points: Break down further
- Stories 1-8 points: Sprint-ready
- Tasks <1 day: Concrete, actionable
```

### Phase 3: Story Point Estimation (5-10 min)
```
Modified Fibonacci Scale:
- 1 point (XS): Trivial change, <2 hours
- 2 points (S): Small, 2-4 hours
- 3 points (M): Medium, 4-8 hours (1 day)
- 5 points (L): Large, 1-2 days
- 8 points (XL): Extra large, 2-3 days
- 13 points (XXL): Very large, 3-5 days (should break down)

Estimation Factors:
• Complexity (algorithmic, integration, UI)
• Uncertainty (unknowns, research needed)
• Dependencies (external services, team coordination)
• Risk (security, performance, compliance)
```

### Phase 4: Timeframe Analysis (5-10 min)
```
TimeframeEstimator Integration (NEW in v1.1.0):

1. Calculate total story points
2. Identify parallel tracks (independent work)
3. Calculate critical path
4. Generate team size scenarios (1, 2, 3, 5+ devs)
5. Produce ASCII + HTML timelines

Output:
- Single developer: X sprints (2 weeks each)
- Team of 2: Y sprints (50% faster with parallelization)
- Team of 5: Z sprints (critical path constraint)
- Cost projections at hourly rate
```

### Phase 5: ADO Output Generation (2-5 min)
```
Generate ADO-formatted markdown:

For each Story:
1. Title: Clear, actionable
2. Description: User context, value proposition
3. Acceptance Criteria: Testable, specific
4. Story Points: Modified Fibonacci
5. Tags: Technology, domain, sprint
6. Implementation Plan: Step-by-step technical approach
7. Technical Notes: Architecture, dependencies, risks

Output Format:
---
# User Story: [Title]
**Story Points:** X | **Priority:** High | **Tags:** backend, authentication

## Description
As a [user type], I want [feature] so that [business value].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Implementation Plan
1. Step 1
2. Step 2

## Technical Notes
Architecture considerations, dependencies, security review.
---
```

---

## 🔧 Configuration

**Config File:** `cortex.config.json`

```json
{
  "swagger_orchestrator": {
    "dor_threshold": 0.80,
    "max_story_points": 8,
    "sprint_length_days": 14,
    "team_velocity_points_per_sprint": 40,
    "enable_timeframe_estimator": true,
    "enable_owasp_security_review": true,
    "ado_output_format": "markdown"
  }
}
```

**Options:**
- `dor_threshold` - Minimum DoR score to provide estimates (default: `0.80` = 80%)
- `max_story_points` - Maximum points before forcing breakdown (default: `8`)
- `sprint_length_days` - Sprint duration for timeline calculation (default: `14`)
- `team_velocity_points_per_sprint` - Avg team velocity (default: `40`)
- `enable_timeframe_estimator` - Use advanced time analysis (default: `true`)
- `enable_owasp_security_review` - Run security checks (default: `true`)
- `ado_output_format` - Output format: `markdown`, `json`, `yaml` (default: `markdown`)

---

## 📈 Examples

### Example 1: Complete DoR Validation
```
User: "plan ado - user authentication feature"

CORTEX:
  📋 Definition of Ready Validation
  
  Let's ensure we have complete requirements before estimation.
  
  **Category 1: Requirements (5 questions)**
  Q1: Who are the primary users of this feature?
  A: Registered users, admins, guest users
  
  Q2: What problem does this feature solve?
  A: Secure access control, session management, role-based permissions
  
  Q3: What is the expected user flow?
  A: Login form → Credentials validation → JWT token → Dashboard redirect
  
  Q4: What are the success metrics?
  A: <2s login time, 99.9% availability, zero data breaches
  
  Q5: What is out of scope?
  A: Social login (OAuth), passwordless authentication, biometrics
  
  ✅ Requirements: 100% complete
  
  **Category 2: Dependencies (4 questions)**
  Q1: External services required?
  A: SQL database (user store), Redis (session cache), SendGrid (email)
  
  Q2: Third-party libraries?
  A: bcrypt (password hashing), jsonwebtoken (JWT), express-session
  
  Q3: Team dependencies?
  A: None - authentication is independent
  
  Q4: Infrastructure requirements?
  A: HTTPS endpoints, rate limiting (10 req/min), firewall rules
  
  ✅ Dependencies: 100% complete
  
  **DoR Score: 95% (COMPLETE) ✅**
  **Can Estimate:** YES
  
  Proceeding to work item decomposition...
```

### Example 2: Incomplete DoR (Cannot Estimate)
```
User: "estimate new dashboard feature"

CORTEX:
  📋 Definition of Ready Validation
  
  **Category 1: Requirements**
  Q1: Who are the primary users?
  A: [NO ANSWER]
  
  Q2: What problem does this solve?
  A: "Make the dashboard better"
  ⚠️ AMBIGUOUS - "Better" is subjective. Specify metrics (speed? UX? features?)
  
  **DoR Score: 35% (NOT_STARTED) ❌**
  **Can Estimate:** NO
  
  ⛔ Cannot proceed with estimation. DoR incomplete.
  
  **Missing Information:**
  • Primary user personas
  • Specific problems to solve (measurable)
  • Expected user workflows
  • Success metrics (load time, conversion rate)
  • Technical constraints (browser support, accessibility)
  
  **Recommendations:**
  1. Conduct user research to identify pain points
  2. Define success metrics (SMART goals)
  3. Create wireframes or mockups
  4. Document technical requirements
  
  Re-run "plan ado" when requirements are complete.
```

### Example 3: Work Item Decomposition
```
User: "plan ado - authentication feature" (after DoR validation)

CORTEX:
  📊 Work Item Decomposition
  
  **Epic: User Authentication System (21 story points)**
  Estimated: 3 sprints (6 weeks) for single developer
  
  **Feature 1: Login & Session Management (8 points)**
  ├─ Story 1.1: Implement login form (3 points)
  │   • Acceptance Criteria:
  │     - Email + password validation
  │     - Error messaging for invalid credentials
  │     - "Remember me" checkbox
  │   • Tasks:
  │     - Create React login component
  │     - Implement form validation
  │     - Add error handling
  │     - Write unit tests (80%+ coverage)
  │
  ├─ Story 1.2: JWT token generation (2 points)
  │   • Acceptance Criteria:
  │     - Generate JWT with user ID, role, expiry
  │     - Set HTTP-only cookie with token
  │     - Validate token signature
  │
  └─ Story 1.3: Session persistence (3 points)
      • Acceptance Criteria:
        - Store sessions in Redis
        - Handle session expiry (30 min idle)
        - Implement token refresh
  
  **Feature 2: Role-Based Access Control (8 points)**
  ├─ Story 2.1: Define roles & permissions (2 points)
  ├─ Story 2.2: Implement middleware (3 points)
  └─ Story 2.3: Add admin panel (3 points)
  
  **Feature 3: Password Security (5 points)**
  ├─ Story 3.1: Bcrypt hashing (2 points)
  └─ Story 3.2: Password reset flow (3 points)
  
  **Timeframe Analysis:**
  • Single developer: 3 sprints (6 weeks)
  • Team of 2: 2 sprints (4 weeks) - 33% faster
  • Team of 3: 1.5 sprints (3 weeks) - 50% faster
  
  **Critical Path:** Feature 1 → Feature 2 → Feature 3 (sequential)
  **Parallel Opportunities:** Story 1.1 + Story 3.1 (independent)
  
  Ready to export ADO-formatted markdown? Say "export ado format".
```

---

## 🎓 Key Concepts

### Definition of Ready (DoR)
**5 Categories:**
1. **Requirements** - What, who, why, success metrics, scope boundaries
2. **Dependencies** - External services, libraries, team coordination
3. **Technical** - Architecture, performance, scalability, constraints
4. **Security** - OWASP review, authentication, data protection
5. **Testing** - Strategy, coverage targets, QA process

**Scoring:**
- Each question: 20 points
- Partial answer: 10 points
- No answer: 0 points
- Ambiguous answer: -5 points (penalty)

**Threshold:** 80% minimum to proceed with estimation

### Modified Fibonacci Scale
**Why Fibonacci?**
- Reflects increasing uncertainty at higher estimates
- Forces conversations about complexity
- Natural breakpoints for story decomposition

**Adjustment from Standard:**
- Standard: 1, 2, 3, 5, 8, 13, 21, 34...
- Modified: 1, 2, 3, 5, 8, 13 (cap at 13)
- Rationale: Stories >13 points too large for sprint, must break down

### Parallel Track Analysis
**TimeframeEstimator identifies:**
- Stories with zero dependencies (can run parallel)
- Critical path (longest sequential chain)
- Team size sweet spot (diminishing returns after N devs)
- Cost-benefit analysis (time vs developer hours)

---

## 🔍 Troubleshooting

### Issue: "DoR score too low - cannot estimate"
**Cause:** Missing answers in 1+ categories  
**Solution:** Complete all questions, ensure answers are specific (not "TBD" or "Maybe")

### Issue: "Story points too high - break down further"
**Cause:** Story >8 points (exceeds sprint capacity)  
**Solution:** Decompose into smaller stories (target 2-5 points each)

### Issue: "Ambiguous acceptance criteria"
**Cause:** Criteria not testable ("should be fast" vs "<2s load time")  
**Solution:** Use SMART format (Specific, Measurable, Achievable, Relevant, Time-bound)

### Issue: "TimeframeEstimator not available"
**Cause:** Module not installed or import failed  
**Solution:** Check `src/agents/estimation/timeframe_estimator.py` exists, install dependencies

---

## 🧪 Testing

**Test Files:**
- `tests/test_swagger_entry_point_orchestrator.py` - DoR validation, decomposition
- `tests/test_timeframe_estimator.py` - Time analysis, parallel tracks

**Key Test Scenarios:**
1. DoR validation with complete/incomplete answers
2. Work item decomposition (Epic → Feature → Story)
3. Story point estimation with Fibonacci scale
4. Timeframe analysis with team size variations
5. ADO markdown output formatting

**Run Tests:**
```bash
pytest tests/test_swagger_entry_point_orchestrator.py -v
pytest tests/test_timeframe_estimator.py -v
```

---

## 🔗 Integration

**Dependencies:**
- `TimeframeEstimator` - Enhanced time estimation with parallel track analysis
- `ADOClient` - Azure DevOps API communication (work item creation)
- `OWASPValidator` - Security review integration
- `PlanningOrchestrator` - Shared planning core

**Called By:**
- ADO planning workflows ("plan ado", "create ado work item")
- Feature estimation requests
- Sprint planning sessions

**Calls:**
- `TimeframeEstimator.estimate()` - Calculate development timeframes
- `ADOClient.create_work_item()` - Create ADO stories/features
- `OWASPValidator.review()` - Security assessment

---

## 📚 Related Documentation

- **Planning Orchestrator Guide** - General feature planning workflow
- **TimeframeEstimator Guide** - Time estimation and team sizing
- **ADO Work Item Guide** - Azure DevOps integration details
- **OWASP Security Review** - Security validation process

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions) - See LICENSE  
**Repository:** https://github.com/asifhussain60/CORTEX
