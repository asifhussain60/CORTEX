# Unified Planning System Workflow Demonstration

**Purpose:** Interactive demonstration of Planning System 3.0 lifecycle  
**Version:** 3.0.0  
**Author:** Asif Hussain  
**Date:** December 17, 2025

---

## 🎯 Overview

This document demonstrates the complete unified planning workflow from user request through temporary plan creation, interactive refinement, DoR validation, and final plan promotion.

**Key Components:**
- **TemporaryPlanManager**: Interactive refinement orchestrator
- **SessionContextManager**: Context continuity across iterations
- **PlanLifecycleManager**: State machine (TEMP → ACTIVE → COMPLETED)
- **UnifiedPlanGenerator**: Token-optimized plan rendering
- **ComplexityAnalyzer**: 4-tier classification
- **PlanManifestTracker**: Manifest versioning

---

## 📋 Scenario: Add User Authentication Feature

**User Request:** *"I need to add user authentication with JWT tokens to my API. Include login, logout, password reset, and role-based access control."*

---

## Phase 1: Request Triage (PlanningGate)

### Step 1.1: Parse User Request

```python
# PlanningGate.triage_request()
user_request = "I need to add user authentication with JWT tokens..."

# Extract key components
feature_keywords = ["authentication", "JWT", "login", "logout", "password reset", "RBAC"]
complexity_indicators = ["JWT tokens", "role-based access control", "security"]
```

### Step 1.2: Complexity Analysis

```python
# ComplexityAnalyzer.analyze()
dimensions = {
    "code_impact": 8,      # Multiple files (controllers, middleware, models)
    "risk_level": 9,       # Security-critical feature
    "domain_complexity": 7,# Crypto, token management, RBAC logic
    "integration_scope": 6 # Database, potentially OAuth providers
}

# Weighted score: (8*3 + 9*3 + 7*2 + 6*2) / 10 = 7.7
complexity_tier = 3  # DOCUMENTED (10-60 min)
```

**Result:** Tier 3 (DOCUMENTED) - Single markdown plan with sub-sections

### Step 1.3: Pre-Planning Discovery

```python
# Check for existing plans
active_plans = search_folder("cortex-brain/documents/planning/active/", "authentication")
# Found: None

temp_plans = search_folder("cortex-brain/documents/planning/temp-plans/", "authentication")
# Found: None

completed_plans = search_folder("cortex-brain/documents/planning/completed/", "authentication", last_180_days=True)
# Found: "user-auth-oauth-2023" (180 days old)
```

**Recommendation:** No active conflicts. Completed plan found for context reuse.

---

## Phase 2: Temporary Plan Creation

### Step 2.1: Start Refinement Session

```python
# TemporaryPlanManager.start_refinement_session()
session = InteractiveRefinementSession(
    session_id="session-20251217-143022",
    plan_id="user-auth-jwt",
    user_request="I need to add user authentication with JWT tokens...",
    created_at="2025-12-17T14:30:22Z",
    complexity_tier=3,
    iterations=[],
    current_dor_score=0.0,
    status="drafting"
)

# Create folder structure
temp-plans/
└── user-auth-jwt/
    ├── 00-temp-plan.md (Initial draft)
    ├── context/
    │   ├── ast-analysis.json
    │   └── lens-dependencies.json
    └── session-metadata.json
```

**Audit Log Entry:**
```json
{
  "timestamp": "2025-12-17T14:30:22Z",
  "event_type": "temp_plan_created",
  "session_id": "session-20251217-143022",
  "plan_id": "user-auth-jwt",
  "orchestrator": "TemporaryPlanManager",
  "phase": "initialization",
  "metadata": {
    "folder": "cortex-brain/documents/planning/temp-plans/user-auth-jwt",
    "complexity_tier": 3,
    "dor_score": 0.0,
    "ambiguity_score": 1.0,
    "iteration": 0
  },
  "duration_ms": 1850
}
```

### Step 2.2: Generate Initial Draft

```python
# UnifiedPlanGenerator.generate_plan()
plan_content = generate_tier3_plan(
    feature_name="User Authentication (JWT)",
    user_request=session.user_request,
    complexity_tier=3,
    ast_context=None,  # First iteration - no AST yet
    lens_context=None   # No Lens analysis yet
)
```

**Generated: `00-temp-plan.md`**

```markdown
# Feature Plan: User Authentication (JWT)

**Plan ID:** user-auth-jwt  
**Status:** 🟡 TEMP (Awaiting Approval)  
**Complexity:** Tier 3 (DOCUMENTED)  
**Created:** 2025-12-17 14:30:22  
**DoR Score:** 0% (Incomplete)

---

## 🎯 Feature Overview

Add JWT-based user authentication with login, logout, password reset, and role-based access control (RBAC).

**User Request:**
> "I need to add user authentication with JWT tokens to my API. Include login, logout, password reset, and role-based access control."

---

## 📊 Complexity Analysis

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Code Impact | 8/10 | Multiple files (controllers, middleware, models, config) |
| Risk Level | 9/10 | Security-critical feature (authentication, token management) |
| Domain Complexity | 7/10 | JWT tokens, password hashing, RBAC logic |
| Integration Scope | 6/10 | Database models, potentially OAuth providers |

**Tier:** 3 (DOCUMENTED) - Feature plan with sub-sections

---

## 🚧 Ambiguities & Missing Information

**The following information is needed before implementation:**

1. **Database Backend**  
   ❓ Which database? (PostgreSQL, MySQL, MongoDB, etc.)  
   ❓ Existing user model or new schema?

2. **Password Reset Mechanism**  
   ❓ Email-based or SMS?  
   ❓ Token expiration time? (default: 1 hour)

3. **JWT Configuration**  
   ❓ Token lifetime? (access: 15min, refresh: 7 days?)  
   ❓ Secret key management? (environment variable, vault?)

4. **RBAC Requirements**  
   ❓ Roles defined? (admin, user, guest?)  
   ❓ Permissions granularity? (endpoint-level, resource-level?)

5. **Testing Strategy**  
   ❓ TDD required?  
   ❓ Coverage target? (default: 80%)

**⚠️ DoR Status: 0% - Cannot proceed without clarification**

---

## 📝 Proposed Implementation Phases

### Phase 1: Database Models & Migrations (3 days)
- User model (id, email, password_hash, role, created_at, updated_at)
- PasswordResetToken model (token, user_id, expires_at)
- RefreshToken model (token, user_id, expires_at)
- Migrations for database setup

**Deliverables:**
- ✅ `models/user.py`
- ✅ `models/password_reset_token.py`
- ✅ `models/refresh_token.py`
- ✅ Database migrations

### Phase 2: Authentication Controllers (4 days)
- `/auth/register` endpoint
- `/auth/login` endpoint (JWT generation)
- `/auth/logout` endpoint (token invalidation)
- `/auth/password-reset` endpoint
- `/auth/refresh-token` endpoint

**Deliverables:**
- ✅ `controllers/auth_controller.py`
- ✅ JWT utility functions
- ✅ Password hashing utilities

### Phase 3: RBAC Middleware (3 days)
- Role-based permission decorator
- Permission validation middleware
- Role management endpoints (admin only)

**Deliverables:**
- ✅ `middleware/rbac.py`
- ✅ `decorators/require_role.py`
- ✅ `controllers/role_controller.py`

### Phase 4: Testing & Validation (2 days)
- Unit tests (models, utilities)
- Integration tests (API endpoints)
- Security tests (token validation, RBAC)

**Deliverables:**
- ✅ `tests/test_auth.py`
- ✅ `tests/test_rbac.py`
- ✅ Coverage report

**Total Estimate:** 12 days

---

## 🔄 Next Steps

**User Actions Required:**
1. Answer ambiguity questions above
2. Provide database schema (if existing)
3. Confirm RBAC roles and permissions
4. Approve or request changes

**Orchestrator Actions:**
- Run AST analysis on existing codebase
- Run Lens dependency mapping
- Update DoR score based on user input
- Refine plan iteratively

---

**Session ID:** session-20251217-143022  
**Iteration:** 0 (Initial Draft)  
**Status:** Awaiting user feedback
```

---

## Phase 3: Interactive Refinement (Back-and-Forth)

### Iteration 1: User Provides Clarifications

**User Response:**
> "We're using PostgreSQL. Existing User model at `models/user.py` but no roles column yet. Email-based password reset with 1-hour expiration. JWT: 15min access, 7 days refresh. Roles: admin, editor, viewer. Endpoint-level permissions. TDD required, 85% coverage."

```python
# TemporaryPlanManager.refine_plan()
user_feedback = "We're using PostgreSQL. Existing User model..."

# Step 3.1: AST Analysis
ast_context = ast_engine.analyze_codebase(
    target_files=["models/user.py"],
    analysis_depth="full"
)

# Result:
ast_context = {
    "files": [
        {
            "path": "models/user.py",
            "classes": [
                {
                    "name": "User",
                    "methods": ["__init__", "save", "delete"],
                    "attributes": ["id", "email", "password_hash", "created_at"],
                    "missing_attributes": ["role", "updated_at"]
                }
            ],
            "imports": ["sqlalchemy", "bcrypt"]
        }
    ],
    "recommendations": [
        "Add 'role' column to User model (ENUM: admin, editor, viewer)",
        "Add 'updated_at' timestamp column",
        "Add migration for schema change"
    ]
}

# Step 3.2: Lens Dependency Mapping
lens_context = cortex_lens.analyze_dependencies(
    target_modules=["models", "controllers"],
    dependency_depth=2
)

# Result:
lens_context = {
    "dependencies": {
        "models/user.py": {
            "imports": ["sqlalchemy", "bcrypt"],
            "imported_by": ["controllers/user_controller.py", "services/auth_service.py"],
            "impact_score": 8  # High impact (widely used)
        }
    },
    "recommendations": [
        "Create migration before modifying User model",
        "Update auth_service.py to handle new role attribute",
        "Add RBAC middleware before existing routes"
    ]
}

# Step 3.3: Calculate DoR Score
dor_score = calculate_dor_score(
    ambiguities_resolved=5,  # All 5 questions answered
    total_ambiguities=5,
    ast_coverage=1,          # 1 file analyzed
    lens_coverage=2          # 2 modules mapped
)
# DoR Score: 90% (5/5 questions * 0.6 + 1/1 AST * 0.2 + 2/2 Lens * 0.2)

ambiguity_score = 10%  # Only 10% ambiguity remains (implementation details)

# Step 3.4: Update Plan
plan_version = update_plan(
    session=session,
    iteration_num=1,
    user_feedback=user_feedback,
    ast_context=ast_context,
    lens_context=lens_context,
    dor_score=90.0,
    ambiguity_score=10.0
)
```

**Generated: `01-temp-plan-refined.md`**

```markdown
# Feature Plan: User Authentication (JWT) [REFINED v1]

**Plan ID:** user-auth-jwt  
**Status:** 🟢 TEMP (Ready for Approval)  
**Complexity:** Tier 3 (DOCUMENTED)  
**Created:** 2025-12-17 14:30:22  
**Updated:** 2025-12-17 14:42:15  
**DoR Score:** 90% (Ready)  
**Ambiguity:** 10% (Minor details)

---

## 🎯 Feature Overview

Add JWT-based user authentication with login, logout, email-based password reset, and endpoint-level RBAC (admin, editor, viewer).

**Clarifications Provided:**
- ✅ Database: PostgreSQL
- ✅ Existing User model: `models/user.py` (needs role column)
- ✅ Password reset: Email-based, 1-hour token expiration
- ✅ JWT: 15min access, 7-day refresh tokens
- ✅ RBAC: admin, editor, viewer (endpoint-level)
- ✅ TDD: Required, 85% coverage target

---

## 📊 AST Analysis Results

**Files Analyzed:** 1

### `models/user.py`
- **Current Attributes:** id, email, password_hash, created_at
- **Missing:** role, updated_at
- **Migration Required:** YES (add role ENUM, updated_at timestamp)

**Recommendations:**
1. Add `role` column: ENUM('admin', 'editor', 'viewer'), default='viewer'
2. Add `updated_at` timestamp with auto-update trigger
3. Create migration: `migrations/add_user_role.sql`

---

## 🔗 Lens Dependency Analysis

**Modules Analyzed:** 2

### Dependency Graph
```
models/user.py
├── controllers/user_controller.py (imports User)
└── services/auth_service.py (imports User)
```

**Impact Score:** 8/10 (High - User model widely used)

**Recommendations:**
1. Create migration BEFORE modifying User model
2. Update `auth_service.py` to handle new `role` attribute
3. Add RBAC middleware decorator before existing routes

---

## 📝 Refined Implementation Phases

### Phase 1: Database Schema Update (2 days)
- **Migration:** Add role column to User table
- **Models:** Update User model with role attribute
- **Models:** Create PasswordResetToken model
- **Models:** Create RefreshToken model

**Deliverables:**
- ✅ `migrations/20251217_add_user_role.sql`
- ✅ `models/user.py` (updated)
- ✅ `models/password_reset_token.py`
- ✅ `models/refresh_token.py`

**Tests:**
- ✅ `tests/models/test_user_role.py`
- ✅ Coverage: 90%+

### Phase 2: JWT Authentication (3 days)
- **Controllers:** `/auth/register`, `/auth/login`, `/auth/logout`
- **Utilities:** JWT generation/validation, password hashing
- **Services:** AuthService refactoring for role support

**Deliverables:**
- ✅ `controllers/auth_controller.py`
- ✅ `utils/jwt_utils.py`
- ✅ `utils/password_utils.py`
- ✅ `services/auth_service.py` (updated)
- ✅ `config/jwt_config.py` (15min access, 7-day refresh)

**Tests:**
- ✅ `tests/controllers/test_auth_controller.py`
- ✅ `tests/utils/test_jwt_utils.py`
- ✅ Coverage: 85%+

### Phase 3: Password Reset (2 days)
- **Controllers:** `/auth/password-reset`, `/auth/reset-token-validate`
- **Services:** Email service integration (Sendgrid/SES)
- **Templates:** Password reset email template

**Deliverables:**
- ✅ `controllers/password_reset_controller.py`
- ✅ `services/email_service.py`
- ✅ `templates/password_reset_email.html`

**Tests:**
- ✅ `tests/controllers/test_password_reset.py`
- ✅ `tests/services/test_email_service.py`
- ✅ Coverage: 85%+

### Phase 4: RBAC Implementation (3 days)
- **Middleware:** Role validation decorator
- **Decorators:** `@require_role('admin')`, `@require_permission('user:edit')`
- **Controllers:** Role management endpoints (admin only)

**Deliverables:**
- ✅ `middleware/rbac_middleware.py`
- ✅ `decorators/require_role.py`
- ✅ `controllers/role_controller.py`
- ✅ Applied to existing endpoints

**Tests:**
- ✅ `tests/middleware/test_rbac.py`
- ✅ `tests/decorators/test_require_role.py`
- ✅ Coverage: 90%+

### Phase 5: Integration & Security Testing (2 days)
- **Integration Tests:** Full auth flow (register → login → protected endpoint)
- **Security Tests:** JWT validation, RBAC enforcement, password reset security
- **Load Tests:** Token refresh performance

**Deliverables:**
- ✅ `tests/integration/test_auth_flow.py`
- ✅ `tests/security/test_jwt_security.py`
- ✅ `tests/security/test_rbac_security.py`
- ✅ Security audit report

**Tests:**
- ✅ Overall coverage: 85%+

**Total Estimate:** 12 days (unchanged)

---

## 🎯 Definition of Ready (DoR) Checklist

| Criteria | Status | Notes |
|----------|--------|-------|
| Feature clearly defined | ✅ | JWT auth with RBAC |
| Acceptance criteria provided | ✅ | 5 criteria specified |
| Database backend specified | ✅ | PostgreSQL |
| Existing codebase analyzed | ✅ | AST + Lens complete |
| Dependencies identified | ✅ | User model impact mapped |
| RBAC roles defined | ✅ | admin, editor, viewer |
| Test strategy approved | ✅ | TDD, 85% coverage |
| Timeline agreed | ✅ | 12 days |

**DoR Score:** 90% ✅ READY FOR APPROVAL

---

## 🔄 Approval Options

**Option 1: Approve & Execute**
- Move plan to `active/` folder
- Create master plan: `active/user-auth-jwt/00-master-plan.md`
- Begin Phase 1 autonomously

**Option 2: Request Changes**
- Provide feedback on phases/estimates
- Orchestrator will refine (Iteration 2)

**Option 3: Reject**
- Cancel plan
- Archive to `rejected/` folder

---

**Session ID:** session-20251217-143022  
**Iteration:** 1  
**Status:** Ready for approval
```

**Audit Log Entry:**
```json
{
  "timestamp": "2025-12-17T14:42:15Z",
  "event_type": "plan_refined",
  "session_id": "session-20251217-143022",
  "plan_id": "user-auth-jwt",
  "orchestrator": "TemporaryPlanManager",
  "phase": "refinement",
  "metadata": {
    "iteration": 1,
    "user_feedback": "We're using PostgreSQL. Existing User model...",
    "dor_score": 0.9,
    "ambiguity_score": 0.1,
    "dor_ready": true,
    "ast_files_analyzed": 1
  },
  "duration_ms": 4250
}
```

---

## Phase 4: Plan Approval & Promotion

### User Approves Plan

**User:** *"Looks good! Approve and start Phase 1."*

```python
# TemporaryPlanManager.approve_plan()
approval_result = lifecycle_manager.approve_plan(
    plan_id="user-auth-jwt",
    approved_by="user",
    comments="Approved for implementation"
)

# Result:
approval_result = ApprovalResult(
    plan_id="user-auth-jwt",
    approved=True,
    moved_to="cortex-brain/documents/planning/active/user-auth-jwt",
    master_plan_path="cortex-brain/documents/planning/active/user-auth-jwt/00-master-plan.md"
)

# Folder structure created:
active/
└── user-auth-jwt/
    ├── 00-master-plan.md (promoted from temp-plans/)
    ├── sub-plans/
    │   ├── 01-database-schema.md
    │   ├── 02-jwt-authentication.md
    │   ├── 03-password-reset.md
    │   ├── 04-rbac-implementation.md
    │   └── 05-integration-testing.md
    ├── artifacts/
    │   ├── ast-analysis.json
    │   └── lens-dependencies.json
    ├── reports/
    ├── tests/
    └── checkpoints/
```

**Generated: `00-master-plan.md`**

```markdown
# Master Plan: User Authentication (JWT)

**Plan ID:** user-auth-jwt  
**Status:** 🚀 ACTIVE (In Progress)  
**Complexity:** Tier 3 (DOCUMENTED)  
**Created:** 2025-12-17 14:30:22  
**Approved:** 2025-12-17 14:48:30  
**DoR Score:** 90%  
**Estimated Duration:** 12 days

---

## 🎯 Feature Overview

Add JWT-based user authentication with login, logout, email-based password reset, and endpoint-level RBAC (admin, editor, viewer).

**Technical Stack:**
- Database: PostgreSQL
- Framework: Existing Python API
- Authentication: JWT (15min access, 7-day refresh)
- Password Reset: Email-based (1-hour token)
- RBAC: admin, editor, viewer (endpoint-level)

---

## 📊 Visual Progress Tracker

| Phase | Status | Progress | Duration | Tasks |
|-------|--------|----------|----------|-------|
| 1. Database Schema | ⏳ In Progress | 25% | 0.5d / 2d | 1/4 |
| 2. JWT Authentication | 🔲 Pending | 0% | 0d / 3d | 0/5 |
| 3. Password Reset | 🔲 Pending | 0% | 0d / 2d | 0/3 |
| 4. RBAC Implementation | 🔲 Pending | 0% | 0d / 3d | 0/4 |
| 5. Integration Testing | 🔲 Pending | 0% | 0d / 2d | 0/3 |

**Overall Progress:** 5% (1/19 tasks complete)  
**Time Elapsed:** 0.5 days  
**Time Remaining:** 11.5 days

---

## 📝 Implementation Phases

### ✅ Phase 1: Database Schema Update (2 days)
**Status:** ⏳ In Progress  
**Current Task:** Creating migration for role column  
**Plan:** `sub-plans/01-database-schema.md`

**Tasks:**
- [x] Design migration (add role ENUM, updated_at)
- [ ] Update User model with role attribute
- [ ] Create PasswordResetToken model
- [ ] Create RefreshToken model

**Progress:** 25% (1/4 complete)

---

### 🔲 Phase 2: JWT Authentication (3 days)
**Status:** Pending (blocked by Phase 1)  
**Plan:** `sub-plans/02-jwt-authentication.md`

**Tasks:**
- [ ] Create auth controller (register, login, logout)
- [ ] Implement JWT utilities (generate, validate, refresh)
- [ ] Create password hashing utilities
- [ ] Update AuthService for role support
- [ ] Add JWT config (15min/7day lifetimes)

**Dependencies:** Phase 1 (User model update)

---

### 🔲 Phase 3: Password Reset (2 days)
**Status:** Pending  
**Plan:** `sub-plans/03-password-reset.md`

**Tasks:**
- [ ] Create password reset controller
- [ ] Integrate email service (Sendgrid/SES)
- [ ] Design email template

**Dependencies:** Phase 2 (AuthService)

---

### 🔲 Phase 4: RBAC Implementation (3 days)
**Status:** Pending  
**Plan:** `sub-plans/04-rbac-implementation.md`

**Tasks:**
- [ ] Create RBAC middleware
- [ ] Implement role decorators (@require_role)
- [ ] Create role management controller
- [ ] Apply RBAC to existing endpoints

**Dependencies:** Phase 2 (User authentication)

---

### 🔲 Phase 5: Integration Testing (2 days)
**Status:** Pending  
**Plan:** `sub-plans/05-integration-testing.md`

**Tasks:**
- [ ] Full auth flow integration tests
- [ ] Security tests (JWT, RBAC)
- [ ] Load tests (token refresh)

**Dependencies:** Phase 4 (Complete implementation)

**Coverage Target:** 85%

---

## 🎯 Definition of Done (DoD) Checklist

| Criteria | Status |
|----------|--------|
| All 5 phases completed | ⏳ 1/5 |
| TDD coverage ≥85% | ⏳ Pending |
| Security audit passed | ⏳ Pending |
| Documentation complete | ⏳ Pending |
| Code review approved | ⏳ Pending |
| Deployed to staging | ⏳ Pending |

---

## 📁 Artifacts

- **AST Analysis:** `artifacts/ast-analysis.json`
- **Lens Dependencies:** `artifacts/lens-dependencies.json`
- **Session Metadata:** `artifacts/session-metadata.json`

---

**Session ID:** session-20251217-143022  
**Last Updated:** 2025-12-17 14:48:30  
**Next Review:** After Phase 1 completion
```

**Audit Log Entry:**
```json
{
  "timestamp": "2025-12-17T14:48:30Z",
  "event_type": "plan_approved",
  "session_id": "session-20251217-143022",
  "plan_id": "user-auth-jwt",
  "orchestrator": "TemporaryPlanManager",
  "phase": "approval",
  "metadata": {
    "approved_by": "user",
    "dor_score": 0.9,
    "source_folder": "temp-plans/user-auth-jwt",
    "destination_folder": "active/user-auth-jwt",
    "sub_plans_created": 5,
    "artifacts_copied": 3
  },
  "duration_ms": 850
}
```

---

## Phase 5: Autonomous Execution

### Phase 1 Execution

```python
# PlanningOrchestrator.execute_workflow()
# Now working from active/user-auth-jwt/

# Sub-plan: 01-database-schema.md
execution_result = execute_phase(
    plan_id="user-auth-jwt",
    phase_number=1,
    autonomous=True  # No user confirmation needed
)

# Implementation:
# 1. Create migration file: migrations/20251217_add_user_role.sql
# 2. Update models/user.py (add role attribute)
# 3. Create models/password_reset_token.py
# 4. Create models/refresh_token.py
# 5. Run tests: tests/models/test_user_role.py
# 6. Validate coverage: 92% (target: 90%)

# Update progress tracker
update_progress(
    plan_id="user-auth-jwt",
    phase=1,
    status="completed",
    duration_days=1.5,  # Finished early
    tasks_completed=4,
    coverage_achieved=0.92
)
```

**Updated Progress Tracker:**

```markdown
| Phase | Status | Progress | Duration | Tasks |
|-------|--------|----------|----------|-------|
| 1. Database Schema | ✅ Complete | 100% | 1.5d / 2d | 4/4 |
| 2. JWT Authentication | ⏳ In Progress | 40% | 0.8d / 3d | 2/5 |
| 3. Password Reset | 🔲 Pending | 0% | 0d / 2d | 0/3 |
| 4. RBAC Implementation | 🔲 Pending | 0% | 0d / 3d | 0/4 |
| 5. Integration Testing | 🔲 Pending | 0% | 0d / 2d | 0/3 |

**Overall Progress:** 36% (8/19 tasks complete)  
**Time Elapsed:** 2.3 days  
**Time Remaining:** 9.7 days
```

---

## Phase 6: Plan Completion

### All Phases Complete

```python
# After Phase 5 completes
completion_result = lifecycle_manager.complete_plan(
    plan_id="user-auth-jwt",
    completion_notes="All 5 phases completed. Coverage: 87%. Security audit passed."
)

# Move to completed/
# active/user-auth-jwt → completed/user-auth-jwt-20251219/
```

**Final Audit Log Entry:**
```json
{
  "timestamp": "2025-12-19T16:22:10Z",
  "event_type": "plan_completed",
  "session_id": "session-20251217-143022",
  "plan_id": "user-auth-jwt",
  "orchestrator": "PlanningOrchestrator",
  "phase": "completion",
  "metadata": {
    "total_phases": 5,
    "total_duration_days": 10.5,
    "estimated_duration_days": 12,
    "final_coverage": 0.87,
    "target_coverage": 0.85,
    "tasks_completed": 19,
    "dod_checklist_passed": true
  },
  "duration_ms": 9072000000
}
```

---

## 📊 Workflow Summary

### Lifecycle State Transitions

```
1. TEMP (temp-plans/)
   ├── Created: 2025-12-17 14:30:22
   ├── Iterations: 1 (1 refinement)
   └── Duration: 18 minutes
   
2. ACTIVE (active/)
   ├── Approved: 2025-12-17 14:48:30
   ├── Phases: 5
   ├── Tasks: 19
   └── Duration: 10.5 days
   
3. COMPLETED (completed/)
   ├── Completed: 2025-12-19 16:22:10
   ├── Coverage: 87%
   └── Archived: user-auth-jwt-20251219/
```

### Metrics

| Metric | Value |
|--------|-------|
| **Complexity Tier** | 3 (DOCUMENTED) |
| **DoR Score** | 90% |
| **Refinement Iterations** | 1 |
| **AST Files Analyzed** | 1 |
| **Lens Modules Analyzed** | 2 |
| **Total Phases** | 5 |
| **Total Tasks** | 19 |
| **Estimated Duration** | 12 days |
| **Actual Duration** | 10.5 days |
| **Variance** | -12.5% (under estimate) |
| **Final Coverage** | 87% |
| **Coverage Target** | 85% |
| **DoD Checklist** | ✅ All passed |

---

## 🎓 Key Takeaways

### 1. Temporary Plan Workflow
- **Purpose:** Interactive refinement before commitment
- **Location:** `temp-plans/` folder
- **Duration:** Minutes to hours (not days)
- **Output:** Refined plan ready for approval

### 2. Interactive Refinement
- **Back-and-Forth:** User provides feedback → Orchestrator refines
- **Context Accumulation:** AST + Lens analysis grows with each iteration
- **DoR Validation:** Score increases as ambiguities resolve
- **Token Optimization:** Context distilled to ≤3,000 tokens

### 3. Master Plan Creation
- **Trigger:** User approval
- **Structure:** Master plan + sub-plans (one per phase)
- **Artifacts:** AST/Lens JSON, session metadata
- **Progress Tracking:** Real-time visual table

### 4. Autonomous Execution
- **No Micro-Confirmations:** Executes all phases after approval
- **Sub-Plan Guidance:** Each phase has detailed implementation plan
- **Test-Driven:** TDD enforced at every phase
- **Coverage Validation:** Per-phase + overall coverage tracking

### 5. State Machine
- **TEMP:** Drafting, refinement, awaiting approval
- **ACTIVE:** Approved, executing phases
- **COMPLETED:** All phases done, archived
- **REJECTED:** User declined, archived

---

## 🔧 Developer Reference

### Start Refinement Session

```python
from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager

manager = TemporaryPlanManager(project_root=Path("."))
session = manager.start_refinement_session(
    user_request="Add user authentication with JWT",
    complexity_tier=3
)
```

### Refine Plan

```python
result = manager.refine_plan(
    session_id=session.session_id,
    user_feedback="Use PostgreSQL, email password reset, RBAC roles: admin, editor, viewer"
)
```

### Approve Plan

```python
from src.planning.plan_lifecycle_manager import PlanLifecycleManager

lifecycle = PlanLifecycleManager(project_root=Path("."))
approval = lifecycle.approve_plan(
    plan_id="user-auth-jwt",
    approved_by="user",
    comments="Approved"
)
```

### Execute Phase

```python
from src.orchestration_3_0.orchestrators.planning import PlanningOrchestrator

orchestrator = PlanningOrchestrator(session_manager=session_manager)
result = orchestrator.execute_workflow(context)
```

---

**End of Demonstration**

This document demonstrates the complete unified planning workflow from request to completion, showing temporary plan creation, interactive refinement, DoR validation, plan promotion, autonomous execution, and final archival.
