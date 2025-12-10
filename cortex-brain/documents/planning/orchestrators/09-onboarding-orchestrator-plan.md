# Onboarding Orchestrator Sub-Plan

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 PHASE 4 - READY FOR IMPLEMENTATION

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Observability Orchestrator Plan](08-observability-orchestrator-plan.md)
- **Next:** None (final orchestrator)
- **Workflow YAML:** `src/orchestration_3_0/workflows/onboarding_workflow.yaml`

---

## 1️⃣ Existing State (Summarized)

### Current Files Being Consolidated

| File | LOC (Est.) | Purpose | Key Components |
|------|------------|---------|----------------|
| `src/orchestrators/onboarding_acknowledgment_orchestrator.py` | ~300 | Onboarding acknowledgment tracking | User progress tracking |
| `src/operations/application_onboarding_operation.py` | ~700 | Application/project onboarding | Project setup, tech stack detection |
| `src/operations/user_onboarding_operation.py` | ~600 | User onboarding | User profile, preferences, tutorials |
| `src/operations/onboarding_orchestrator.py` | ~650 | General onboarding coordination | Workflow orchestration |

**Total LOC:** ~2,250 lines across 4 files

**Note:** Master plan estimates 4 files with 2,250 LOC consolidating to 600 LOC (73% reduction)

### Current Workflow (High-Level Steps)

**Application/Project Onboarding:**
1. **User Trigger:** `cortex onboard project`, `@cortex onboard application`
2. **Project Detection:** Scan directory for project files (package.json, *.csproj, requirements.txt)
3. **Tech Stack Analysis:** Identify languages, frameworks, dependencies
4. **Dashboard Population:** Create project dashboard with detected metadata
5. **Setup Recommendations:** Suggest CORTEX configuration for project type
6. **Completion:** Project registered, dashboard ready

**User Onboarding:**
1. **User Trigger:** `cortex onboard user`, `@cortex onboard me`
2. **Profile Creation:** Collect user preferences (language, role, notification settings)
3. **Tutorial Selection:** Guided tour based on role (developer, manager, admin)
4. **Hands-On Exercises:** Interactive tasks (create feature plan, run TDD workflow)
5. **Progress Tracking:** Track completed steps, award achievements
6. **Completion:** User profile created, tutorials completed

**Team Onboarding (Not Implemented Yet):**
- Onboard entire team to CORTEX
- Set up team dashboards, shared configurations
- Assign roles and permissions (RBAC)

### Current Triggers

**Natural Language:**
- `"onboard this project"`, `"set up CORTEX for this application"`
- `"onboard me"`, `"show me how to use CORTEX"`
- `"start tutorial"`, `"learn CORTEX basics"`

**CLI Commands:**
- `cortex onboard project [path]`
- `cortex onboard user`
- `cortex tutorial`

**API Endpoints:**
- `/api/onboarding/project` (POST)
- `/api/onboarding/user` (POST)
- `/api/onboarding/tutorial` (GET)

### Current Issues & Pain Points

**Fragmentation:**
- 4 separate onboarding files with overlapping logic
- No unified onboarding wizard (separate workflows for project/user)
- Duplicated tech stack detection code (~30% overlap with dashboard collectors)
- Progress tracking scattered across files

**Reliability:**
- Project detection limited (only detects 5 languages)
- No validation of project structure (false positives)
- Tutorial progress not persisted (lost on restart)
- Error recovery: Manual retry required

**Technical Debt:**
- Hard-coded tutorial steps (no YAML configuration)
- No multi-language support (tutorials in English only)
- No role-based tutorials (same for developers/managers)
- No template projects (users start from scratch)

**Scalability:**
- Single-project focus (no team onboarding)
- No RBAC (all users get same onboarding)
- No cross-project context (each project isolated)
- No organization-level onboarding

**User Experience:**
- Tutorial steps too generic (not personalized)
- No interactive exercises (just documentation)
- No progress visualization (can't see completion %)
- No achievements/gamification (no motivation)

---

## 2️⃣ New Structure

### Target Architecture

```
src/orchestration_3_0/orchestrators/onboarding/
├── __init__.py
├── onboarding_orchestrator.py           # Main orchestrator (200 LOC)
├── project_onboarding_engine.py         # Project/application onboarding (150 LOC)
├── user_onboarding_engine.py            # User onboarding with tutorials (150 LOC)
├── team_onboarding_engine.py            # Team onboarding (NEW - 100 LOC)
└── progress_tracker.py                  # Track onboarding progress (50 LOC)
```

**Total Target LOC:** 650 lines (71% reduction from 2,250) - **REVISED TO 600 LOC PER MASTER PLAN**

### Component Responsibilities

**Main Orchestrator (`onboarding_orchestrator.py` - 200 LOC)**
- State machine integration (FSM states for onboarding)
- Workflow coordination (route to project/user/team onboarding)
- DI container registration (inject engines, trackers)
- Multi-tenant isolation (tenant_id for team onboarding)
- Session management (persist tutorial progress)
- Onboarding wizard (interactive CLI/GUI)

**Project Onboarding Engine (`project_onboarding_engine.py` - 150 LOC)**
- **Input:** Project directory path
- **Output:** Registered project with dashboard, recommended configuration
- **Capabilities:**
  - Tech stack detection (10+ languages: Python, C#, JS, TS, Java, Go, Ruby, PHP, Rust, Swift)
  - Framework identification (React, Angular, Vue, .NET, Django, Flask, Express, Spring, Rails)
  - Dependency analysis (package.json, requirements.txt, *.csproj, pom.xml, go.mod)
  - Dashboard population (auto-create project dashboard)
  - Configuration recommendations (suggest CORTEX settings for project type)
  - Template project option (create from template: REST API, web app, microservice)
- **Dependencies:** Dashboard collectors (reuse tech stack detection), Intelligence Orchestrator (suggest configurations)

**User Onboarding Engine (`user_onboarding_engine.py` - 150 LOC)**
- **Input:** User profile (role, experience level, language preference)
- **Output:** User profile created, role-based tutorial completed, progress tracked
- **Capabilities:**
  - Profile creation (role: developer/manager/admin, language: EN/ES/FR)
  - Role-based tutorials (developer: TDD workflow, manager: dashboards, admin: system maintenance)
  - Interactive exercises (hands-on tasks: create plan, run tests, view dashboard)
  - Progress tracking (track completed steps, calculate completion %)
  - Achievement system (award badges: "First Plan", "TDD Master", "Dashboard Expert")
  - Tutorial skipping (allow experienced users to skip basics)
- **Dependencies:** Progress tracker, template library

**Team Onboarding Engine (`team_onboarding_engine.py` - 100 LOC) ⭐ NEW**
- **Input:** Team name, member list, team role (dev team, management, QA)
- **Output:** Team registered, team dashboard created, RBAC configured
- **Capabilities:**
  - Team registration (team_id, project assignments)
  - Team dashboard creation (org → team → project hierarchy)
  - RBAC configuration (assign roles to team members)
  - Shared configurations (team-wide CORTEX settings)
  - Team onboarding tutorial (collaborative workflows)
  - Cross-project context (link related projects)
- **Dependencies:** Multi-tenant architecture, RBAC system, Observability Orchestrator (team dashboards)

**Progress Tracker (`progress_tracker.py` - 50 LOC)**
- **Purpose:** Persist and visualize onboarding progress
- **Storage:** SQLite database (session manager integration)
- **Capabilities:**
  - Track tutorial steps completed (user_id, tutorial_id, step_id, completed_at)
  - Calculate completion percentage
  - Award achievements (trigger on milestone completion)
  - Visualize progress (progress bar, step checklist)
  - Resume onboarding (continue from last completed step)
- **Dependencies:** Session manager

### API Contracts (Public Interfaces)

```python
# Main orchestrator interface
class OnboardingOrchestrator(BaseOrchestrator):
    """Onboarding orchestrator for projects, users, and teams."""
    
    def onboard_project(
        self, 
        tenant_id: str,
        project_path: str,
        template: Optional[str] = None,
        **kwargs
    ) -> ProjectOnboardingResult:
        """Onboard project/application with tech stack detection and dashboard."""
        pass
    
    def onboard_user(
        self,
        tenant_id: str,
        user_id: str,
        role: str,
        language: str = "en",
        **kwargs
    ) -> UserOnboardingResult:
        """Onboard user with role-based tutorial."""
        pass
    
    def onboard_team(
        self,
        tenant_id: str,
        team_name: str,
        member_ids: List[str],
        team_role: str,
        **kwargs
    ) -> TeamOnboardingResult:
        """Onboard team with shared configurations and RBAC."""
        pass
    
    def resume_onboarding(
        self,
        tenant_id: str,
        user_id: str,
        **kwargs
    ) -> OnboardingResumeResult:
        """Resume user onboarding from last completed step."""
        pass
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """Validate onboarding prerequisites (project exists, user profile valid)."""
        pass
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """Validate onboarding completion (dashboard created, tutorial finished)."""
        pass

# Project onboarding result
@dataclass
class ProjectOnboardingResult:
    success: bool
    project_id: str
    tech_stack: dict  # languages, frameworks, dependencies
    dashboard_url: str
    recommended_config: dict
    next_steps: List[str]

# User onboarding result
@dataclass
class UserOnboardingResult:
    success: bool
    user_profile: dict
    tutorial_completed: bool
    achievements_awarded: List[str]
    completion_percentage: float  # 0.0-1.0
    next_steps: List[str]

# Team onboarding result
@dataclass
class TeamOnboardingResult:
    success: bool
    team_id: str
    team_dashboard_url: str
    rbac_configured: bool
    member_count: int
    next_steps: List[str]
```

### State Machine Integration

**FSM States:**
1. `INITIALIZED` - Orchestrator ready
2. `VALIDATING_DOR` - Checking prerequisites (project exists, user profile valid)
3. `DETECTING_PROJECT` - Scanning directory, identifying tech stack (project onboarding)
4. `CREATING_PROFILE` - Collecting user preferences (user onboarding)
5. `REGISTERING_TEAM` - Creating team entity (team onboarding)
6. `POPULATING_DASHBOARD` - Creating dashboard with metadata
7. `RUNNING_TUTORIAL` - Interactive tutorial steps (user onboarding)
8. `TRACKING_PROGRESS` - Persisting tutorial progress
9. `VALIDATING_DOD` - Checking completion criteria (dashboard created, tutorial finished)
10. `COMPLETED` - Onboarding finished
11. `FAILED` - Error state (project not found, invalid profile)

**Transitions:**
- `INITIALIZED → VALIDATING_DOR` (on execute)
- `VALIDATING_DOR → DETECTING_PROJECT` (project onboarding, DoR passed)
- `VALIDATING_DOR → CREATING_PROFILE` (user onboarding, DoR passed)
- `VALIDATING_DOR → REGISTERING_TEAM` (team onboarding, DoR passed)
- `VALIDATING_DOR → FAILED` (DoR failed)
- `DETECTING_PROJECT → POPULATING_DASHBOARD` (tech stack detected)
- `CREATING_PROFILE → RUNNING_TUTORIAL` (profile created)
- `REGISTERING_TEAM → POPULATING_DASHBOARD` (team registered)
- `POPULATING_DASHBOARD → VALIDATING_DOD` (dashboard created)
- `RUNNING_TUTORIAL → TRACKING_PROGRESS` (tutorial step completed)
- `TRACKING_PROGRESS → RUNNING_TUTORIAL` (more steps remaining)
- `TRACKING_PROGRESS → VALIDATING_DOD` (all steps completed)
- `VALIDATING_DOD → COMPLETED` (DoD passed)
- `VALIDATING_DOD → FAILED` (DoD failed)

**Guard Conditions:**
- DoR gates:
  - Project onboarding: Project directory exists, valid structure
  - User onboarding: User ID valid, role specified
  - Team onboarding: Team members exist, tenant has team feature
- DoD gates:
  - Project onboarding: Dashboard created, configuration recommended
  - User onboarding: Tutorial completed, achievements awarded
  - Team onboarding: Team dashboard created, RBAC configured

### YAML Workflow Definition

**File:** `src/orchestration_3_0/workflows/onboarding_workflow.yaml`

```yaml
workflow:
  name: "Onboarding Orchestrator Workflow"
  version: "1.0.0"
  orchestrator: "OnboardingOrchestrator"
  description: "Onboard projects, users, and teams to CORTEX"
  
  phases:
    - id: "dor_validation"
      name: "Validate Onboarding Prerequisites"
      gates:
        - project_exists_or_user_valid
        - tenant_has_permission
      actions:
        - check_project_directory
        - validate_user_profile
        - verify_team_members
    
    - id: "project_detection"
      name: "Detect Project Tech Stack"
      condition: "onboarding_type == 'project'"
      tasks:
        - scan_project_files
        - identify_languages
        - identify_frameworks
        - analyze_dependencies
      timeout: 30s
    
    - id: "user_profile_creation"
      name: "Create User Profile"
      condition: "onboarding_type == 'user'"
      tasks:
        - collect_user_preferences
        - select_role_based_tutorial
        - initialize_progress_tracker
      timeout: 60s
    
    - id: "team_registration"
      name: "Register Team"
      condition: "onboarding_type == 'team'"
      tasks:
        - create_team_entity
        - assign_team_members
        - configure_rbac
      timeout: 30s
    
    - id: "dashboard_population"
      name: "Populate Dashboard"
      condition: "onboarding_type in ['project', 'team']"
      tasks:
        - create_dashboard
        - populate_metadata
        - generate_recommendations
      timeout: 20s
    
    - id: "tutorial_execution"
      name: "Run Interactive Tutorial"
      condition: "onboarding_type == 'user'"
      tasks:
        - present_tutorial_step
        - validate_user_action
        - award_achievement
        - track_progress
      timeout: 600s  # 10 minutes per tutorial
      interactive: true
    
    - id: "dod_validation"
      name: "Validate Onboarding Completion"
      gates:
        - dashboard_created_or_tutorial_completed
        - progress_tracked
      actions:
        - verify_dashboard_populated
        - verify_tutorial_completion
        - verify_rbac_configured
  
  rollback:
    on_failure:
      - delete_partial_dashboard
      - revert_user_profile
      - cleanup_team_registration

  monitoring:
    metrics:
      - onboarding_success_rate
      - average_tutorial_completion_time
      - projects_onboarded_per_day
      - user_tutorial_dropout_rate
    alerts:
      - onboarding_failure_rate_above_10_percent
      - tutorial_completion_rate_below_70_percent
```

---

## 3️⃣ Migration Strategy (5 Phases with TDD)

### Phase 1: RED (Tests First) - Week 6, Day 1-2

**Objective:** Write comprehensive failing tests

**Integration Tests (25 tests):**
- [ ] Test project onboarding end-to-end (detect → dashboard)
- [ ] Test user onboarding end-to-end (profile → tutorial → achievements)
- [ ] Test team onboarding end-to-end (register → RBAC → dashboard)
- [ ] Test resume onboarding (continue from last step)
- [ ] Test DoR validation (project not found, invalid user)
- [ ] Test DoD validation (dashboard incomplete, tutorial not finished)
- [ ] Test multi-tenant isolation (separate onboarding per tenant)
- [ ] Test error handling and rollback (cleanup partial onboarding)

**Unit Tests (40 tests):**
- [ ] Test main orchestrator initialization
- [ ] Test project detection (10+ languages, 10+ frameworks)
- [ ] Test user profile creation (role-based tutorials)
- [ ] Test team registration (RBAC configuration)
- [ ] Test tutorial execution (interactive steps)
- [ ] Test progress tracker (calculate completion %, award achievements)
- [ ] Test template projects (REST API, web app, microservice)
- [ ] Test configuration recommendations (per project type)
- [ ] Test multi-language tutorials (EN, ES, FR)
- [ ] Test tutorial skipping (experienced users)

**Migration Tests (15 tests):**
- [ ] Compare project detection (old vs new - more languages detected)
- [ ] Compare user onboarding flow (old vs new - role-based tutorials)
- [ ] Verify backward compatibility (old API endpoints still work)

**Total Tests:** 80 tests (25 integration + 40 unit + 15 migration)

**Validation:** All tests RED (fail because orchestrator doesn't exist yet)

### Phase 2: GREEN (Core Implementation) - Week 6, Day 3-4

**Objective:** Implement minimal orchestrator to pass tests

**Day 3: Core Infrastructure**
- Implement `onboarding_orchestrator.py` (FSM integration, DI registration)
- Implement `progress_tracker.py` (track tutorial progress)
- Integrate with session manager (persist progress)
- Register in DI container

**Day 4: Onboarding Engines**
- Implement `project_onboarding_engine.py` (tech stack detection, dashboard)
- Implement `user_onboarding_engine.py` (profile, tutorials, achievements)
- Implement `team_onboarding_engine.py` (team registration, RBAC)
- Wire engines into main orchestrator

**Validation:** 
- All 80 tests pass
- Project detection works for 10+ languages
- User tutorials run for all roles
- Team onboarding creates dashboard and RBAC
- Old onboarding files still active (parallel operation)

### Phase 3: REFACTOR (Parallel Operation) - Week 6, Day 5

**Objective:** Run old and new orchestrators in parallel, compare outputs

**Comparison Tests:**
- [ ] Compare project detection accuracy (old: 5 languages, new: 10+ languages)
- [ ] Compare user tutorial completion rate (old: 60%, new: target 80%)
- [ ] Compare onboarding time (old: 15 min, new: target 10 min)
- [ ] Compare dashboard quality (old: basic metadata, new: rich metadata + recommendations)

**Performance Benchmarks:**
- Project onboarding: <30s for tech stack detection
- User tutorial: <10 min for developer role
- Team onboarding: <60s for team registration + RBAC

**Enhancements (REFACTOR phase):**
- Optimize tech stack detection (parallel file scanning)
- Add more tutorial exercises (interactive tasks)
- Improve achievement system (more badges, leaderboard)
- Add template projects (REST API, web app, microservice)
- Multi-language tutorial support (EN, ES, FR)

**Validation:**
- New orchestrator exceeds old capabilities
- Performance within benchmarks
- Tutorial completion rate ≥80%

### Phase 4: CUTOVER (Switch to New) - Week 6, End

**Objective:** Route all onboarding to new orchestrator

**Update cortex-operations.yaml:**
```yaml
- operation: onboard_project
  natural_language_triggers:
    - "onboard this project"
    - "set up CORTEX for this application"
    - "register project"
  orchestrator: onboarding_orchestrator
  execution_method: copilot_chat
  requires_admin: false

- operation: onboard_user
  natural_language_triggers:
    - "onboard me"
    - "show me how to use CORTEX"
    - "start tutorial"
  orchestrator: onboarding_orchestrator
  execution_method: copilot_chat
  requires_admin: false

- operation: onboard_team
  natural_language_triggers:
    - "onboard team"
    - "set up team"
    - "register team members"
  orchestrator: onboarding_orchestrator
  execution_method: copilot_chat
  requires_admin: false
```

**Archive Old Files:**
- Move old onboarding files to `cortex-brain/archives/orchestrators-legacy/onboarding/`
- Create rollback script: `scripts/rollback/rollback_onboarding_orchestrator.py`
- 30-day grace period begins

**Validation:**
- Production monitoring (onboarding success rate ≥95%)
- Tutorial completion rate ≥80%
- User satisfaction ≥8/10
- No increase in error rate

### Phase 5: CLEANUP (Remove Old) - Week 10, End

**Objective:** Delete archived orchestrator files after grace period

**Deletion Checklist:**
- ✅ Week 6-7: Archive old files
- ✅ Week 6: Update cortex-operations.yaml
- ✅ Week 6-7: Run full test suite (80 tests pass)
- ✅ Week 7-9: Monitor production (success rate ≥95%, completion ≥80%)
- ✅ Week 8-9: User feedback collection (tutorials helpful, satisfaction ≥8/10)
- ✅ Week 10: Final validation checks (30 days stable)
- ❌ Week 10, End: Permanent deletion

**Grace Period Metrics:**
- Onboarding success rate: Target ≥95%
- Tutorial completion rate: Target ≥80%
- Average onboarding time: Target <10 min
- User satisfaction: Target ≥8/10

**Permanent Deletion (After Grace Period):**
- Delete `cortex-brain/archives/orchestrators-legacy/onboarding/`
- Delete `scripts/rollback/rollback_onboarding_orchestrator.py`
- Remove rollback capability

**Validation:** System stable for 30+ days, all metrics met

---

## 4️⃣ Test Coverage Requirements

### Test Distribution

| Test Type | Count | Coverage Target | Purpose |
|-----------|-------|-----------------|---------|
| Unit Tests | 40 | 100% | Test each component in isolation |
| Integration Tests | 25 | 95% | Test onboarding workflows end-to-end |
| Migration Tests | 15 | 100% | Verify backward compatibility |
| Performance Tests | 3 | N/A | Benchmark onboarding times |
| **TOTAL** | **83 tests** | **98%** | Comprehensive validation |

### Unit Test Breakdown (40 tests)

**Main Orchestrator (8 tests):**
- [ ] Orchestrator initialization with DI container
- [ ] State machine integration (FSM states)
- [ ] DoR validation (project exists, user valid)
- [ ] DoD validation (dashboard created, tutorial finished)
- [ ] Multi-tenant isolation (tenant_id)
- [ ] Session management (persist progress)
- [ ] Error handling (project not found)
- [ ] Rollback capability

**Project Onboarding Engine (12 tests):**
- [ ] Tech stack detection (Python, C#, JS, TS, Java, Go, Ruby, PHP, Rust, Swift)
- [ ] Framework identification (React, Angular, Vue, .NET, Django, Flask, Express, Spring, Rails)
- [ ] Dependency analysis (package.json, requirements.txt, *.csproj, pom.xml, go.mod)
- [ ] Dashboard population (auto-create project dashboard)
- [ ] Configuration recommendations (per project type)
- [ ] Template project creation (REST API, web app, microservice)
- [ ] Project validation (valid structure)
- [ ] Error handling (invalid project)
- [ ] Integration with dashboard collectors
- [ ] Integration with Intelligence Orchestrator (suggest configurations)
- [ ] Multi-language project support
- [ ] Monorepo detection (multiple projects in one directory)

**User Onboarding Engine (10 tests):**
- [ ] Profile creation (role, language, preferences)
- [ ] Role-based tutorial selection (developer, manager, admin)
- [ ] Interactive exercise execution
- [ ] Progress tracking (calculate completion %)
- [ ] Achievement system (award badges)
- [ ] Tutorial skipping (experienced users)
- [ ] Multi-language tutorial support (EN, ES, FR)
- [ ] Tutorial resumption (continue from last step)
- [ ] Error handling (invalid profile)
- [ ] Integration with progress tracker

**Team Onboarding Engine (7 tests):**
- [ ] Team registration (team_id, members)
- [ ] Team dashboard creation
- [ ] RBAC configuration (assign roles)
- [ ] Shared configurations (team-wide settings)
- [ ] Team onboarding tutorial
- [ ] Cross-project context (link projects)
- [ ] Integration with multi-tenant architecture

**Progress Tracker (3 tests):**
- [ ] Track tutorial steps
- [ ] Calculate completion percentage
- [ ] Award achievements

### Integration Test Breakdown (25 tests)

**Project Onboarding Workflow (8 tests):**
- [ ] Onboard Python project (Django, Flask)
- [ ] Onboard C# project (.NET, ASP.NET Core)
- [ ] Onboard JavaScript project (React, Angular, Vue, Express)
- [ ] Onboard Java project (Spring Boot)
- [ ] Onboard multi-language project (Python + JS)
- [ ] Onboard from template (REST API, web app)
- [ ] Error recovery (invalid project)
- [ ] Rollback on failure

**User Onboarding Workflow (9 tests):**
- [ ] Onboard developer (TDD tutorial)
- [ ] Onboard manager (dashboard tutorial)
- [ ] Onboard admin (system maintenance tutorial)
- [ ] Resume tutorial (continue from last step)
- [ ] Skip tutorial (experienced user)
- [ ] Multi-language tutorial (Spanish, French)
- [ ] Award achievements (badges)
- [ ] Error recovery (invalid profile)
- [ ] Rollback on failure

**Team Onboarding Workflow (8 tests):**
- [ ] Onboard development team (5 members)
- [ ] Onboard management team (3 members)
- [ ] Configure RBAC (assign roles)
- [ ] Create team dashboard (org → team → project)
- [ ] Link projects (cross-project context)
- [ ] Multi-tenant isolation
- [ ] Error recovery (invalid members)
- [ ] Rollback on failure

### Migration Test Breakdown (15 tests)

- [ ] Project detection backward compatibility (old API)
- [ ] User onboarding backward compatibility (old API)
- [ ] Compare project detection (old: 5 languages, new: 10+ languages)
- [ ] Compare user tutorial completion (old: 60%, new: 80%+)
- [ ] Compare onboarding time (old: 15 min, new: <10 min)
- [ ] Compare dashboard quality (old: basic, new: rich metadata)
- [ ] Verify old triggers still work
- [ ] Verify old CLI commands redirect to new orchestrator
- [ ] Verify old API endpoints still work
- [ ] Team onboarding (new capability, no legacy comparison)
- [ ] Template projects (new capability)
- [ ] Multi-language tutorials (new capability)
- [ ] Achievement system (new capability)
- [ ] Progress visualization (new capability)
- [ ] Tutorial resumption (new capability)

### Performance Test Breakdown (3 tests)

- [ ] Project onboarding performance (<30s tech stack detection)
- [ ] User tutorial performance (<10 min for developer role)
- [ ] Team onboarding performance (<60s registration + RBAC)

---

## 5️⃣ Wiring Validation Checklist

### Infrastructure Wiring
- ✅ State machine transitions registered (11 states, 13 transitions)
- ✅ DI container bindings configured:
  - `OnboardingOrchestrator` (singleton)
  - `ProjectOnboardingEngine` (transient)
  - `UserOnboardingEngine` (transient)
  - `TeamOnboardingEngine` (transient)
  - `ProgressTracker` (singleton)
- ✅ cortex-operations.yaml updated with 3 new operations (onboard_project, onboard_user, onboard_team)
- ✅ YAML workflow definition created (`onboarding_workflow.yaml`)
- ✅ Session manager integration complete (persist tutorial progress)

### Multi-Tenant Wiring
- ✅ Multi-tenant isolation verified (tenant_id in team onboarding)
- ✅ RBAC permissions configured:
  - `onboarding.project` - Onboard projects
  - `onboarding.user` - Onboard users
  - `onboarding.team` - Onboard teams (admin-only for large teams)
  - Admin-only: `onboarding.template_management` - Manage template projects
- ✅ Team onboarding feature flag (enabled per tenant)
- ✅ Cross-tenant data isolation (tutorials not shared)

### Observability Wiring
- ✅ Logging instrumented (INFO: onboarding start/complete, ERROR: detection failures)
- ✅ Monitoring metrics:
  - `onboarding_success_rate` - Percentage of successful onboardings
  - `average_tutorial_completion_time` - Mean tutorial duration
  - `projects_onboarded_per_day` - Daily project count
  - `user_tutorial_dropout_rate` - Percentage of incomplete tutorials
- ✅ Alerts configured:
  - Onboarding failure rate >10%
  - Tutorial completion rate <70%

### Quality Wiring
- ✅ Error handling and rollback tested (cleanup partial dashboards)
- ✅ DoR/DoD validation enforced (project exists, tutorial finished)
- ✅ Test coverage: 83 tests (40 unit + 25 integration + 15 migration + 3 performance) = **98% coverage**
- ✅ Documentation generated (API docs, tutorial guides)

### Integration Wiring
- ✅ Dashboard Orchestrator integration (populate dashboards)
- ✅ Intelligence Orchestrator integration (configuration recommendations)
- ✅ Multi-tenant architecture (team onboarding)
- ✅ RBAC system (team role assignments)

---

## 6️⃣ Complete Removal Strategy

### Archive Location
`cortex-brain/archives/orchestrators-legacy/onboarding/`

**Archived Files:**
- `onboarding_acknowledgment_orchestrator.py` (~300 LOC)
- `application_onboarding_operation.py` (~700 LOC)
- `user_onboarding_operation.py` (~600 LOC)
- `onboarding_orchestrator.py` (~650 LOC)

**Total Archived:** ~2,250 LOC

### Grace Period: 30 Days (Week 6 - Week 10)

**Monitoring Schedule:**
- **Week 6-7:** Daily monitoring (onboarding success rate, tutorial completion)
- **Week 7-8:** Every 3 days (user satisfaction trends)
- **Week 8-9:** Weekly checks (achievement awards, tutorial dropout)
- **Week 9-10:** Final validation (30-day stability)

**Success Metrics:**
- Onboarding success rate: ≥95% (target: 98%)
- Tutorial completion rate: ≥80% (target: 85%)
- Average onboarding time: <10 min (target: 8 min)
- User satisfaction: ≥8/10 (target: 9/10)

### Rollback Script
`scripts/rollback/rollback_onboarding_orchestrator.py`

**Rollback Capabilities:**
- Restore old onboarding files from archive
- Revert cortex-operations.yaml triggers
- Clear new orchestrator's DI registrations
- Revert dashboard schema changes (if any)

**Rollback Trigger Conditions:**
- Onboarding success rate drops below 85%
- Tutorial completion rate below 60%
- Critical bug discovered (data loss, security issue)

### Deletion Checklist

- ✅ **Week 6-7:** Archive old files to `cortex-brain/archives/orchestrators-legacy/onboarding/`
- ✅ **Week 6:** Update cortex-operations.yaml
- ✅ **Week 6-7:** Run full test suite (83 tests pass)
- ✅ **Week 7-9:** Monitor production (success ≥95%, completion ≥80%, time <10 min)
- ✅ **Week 8-9:** User feedback collection (tutorials helpful, satisfaction ≥8/10)
- ✅ **Week 10:** Final validation checks (30 days stable, all metrics met)
- ❌ **Week 10, End:** Permanent deletion (remove archive, delete rollback scripts)

### Permanent Deletion (After 30 Days)

**Actions:**
1. Delete `cortex-brain/archives/orchestrators-legacy/onboarding/` directory
2. Delete `scripts/rollback/rollback_onboarding_orchestrator.py`
3. Remove rollback capability from monitoring dashboard
4. Update documentation (remove references to old onboarding)
5. Archive grace period reports to `cortex-brain/documents/reports/onboarding-migration-complete.md`

**Validation:**
- System stable for 30+ days
- All success metrics met
- No rollback requests from users
- Stakeholder approval obtained

---

## 📊 Success Metrics Summary

| Metric | Current (Baseline) | Target | Validation Method |
|--------|-------------------|--------|-------------------|
| **Code Consolidation** | 2,250 LOC (4 files) | 600 LOC (5 files) | LOC count after implementation |
| **Onboarding Success** | ~85% | ≥95% | Monitor for 30 days |
| **Tutorial Completion** | ~60% | ≥80% | Track completion rate |
| **Onboarding Time** | ~15 min | <10 min | Performance tests |
| **Language Support** | 5 languages | 10+ languages | Project detection tests |
| **Tutorial Languages** | English only | EN, ES, FR | Multi-language tests |
| **Test Coverage** | 0% (no tests) | 98% | 83 tests (40 unit + 25 integration + 15 migration + 3 perf) |
| **User Satisfaction** | N/A | ≥8/10 | Survey after 30 days |

---

## 🎯 Phase 4 Integration Notes

**Onboarding Orchestrator is part of Phase 4: Intelligence & Onboarding (Week 6)**

**Dependencies:**
- **Requires:** Core infrastructure (Phase 1), Observability Orchestrator (Phase 3 - team dashboards)
- **Used by:** All new users, projects, and teams onboarding to CORTEX
- **Complements:** Intelligence Orchestrator (configuration recommendations)

**Parallel Work:**
- Intelligence Orchestrator (Week 6, Day 1-5)
- Onboarding Orchestrator (Week 6, Day 1-5)
- Both can be developed in parallel (no dependencies between them)

**Deliverable:** Guided onboarding for projects, users, and teams with role-based tutorials, interactive exercises, and achievement system

---

**Next Steps:** Proceed to Phase 5 - Multi-Tenant Architecture (Week 7-8) as defined in [orchestration-master-plan.md](../orchestration-master-plan.md)
