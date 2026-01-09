# 🎯 CORTEX 6.0 Planning Orchestrator Workflow

**Version:** 6.0.0  
**Date:** 2026-01-09  
**Author:** Asif Hussain  
**Status:** ✅ DESIGN COMPLETE

---

## 📋 Executive Summary

The Planning Orchestrator v6.0 implements a **4-phase interactive workflow** that collaborates with users to achieve Definition of Ready (DoR), generates zero-ambiguity execution plans, and executes autonomously with config-based approval enforcement.

**Key Innovation:** Acceptance criteria are gathered interactively during Phase 1 and enforced throughout execution via plan configuration.

---

## 🎯 Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 PLANNING ORCHESTRATOR v6.0                      │
│                    Interactive → Zero Ambiguity → Autonomous    │
└─────────────────────────────────────────────────────────────────┘

Phase 1: Interactive Requirements Gathering (30-50%)
    ↓
    [DoR Checkpoint: Includes Acceptance Criteria]
    ↓
Phase 2: Detailed Plan Generation (15-25%)
    ↓
    [Zero Ambiguity Validation]
    ↓
Phase 3: Plan Approval & Config Creation (Variable)
    ↓
    [config.yaml: approval_granted = true]
    ↓
Phase 4: Autonomous Execution (50-70%)
    ↓
    [Master Orchestrator: Validates config.yaml]
    ↓
[Plan Complete]
```

---

## 📊 Phase 1: Interactive Requirements Gathering

### **Objective:** Achieve Definition of Ready with zero assumptions

**Duration:** 30-50% of planning time  
**Mode:** INTERACTIVE (User collaboration required)

---

### **Visual Flow:**

```
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 1: Interactive Requirements Gathering (DoR Achievement)   │
└──────────────────────────────────────────────────────────────────┘

User: "plan user authentication"
    ↓
┌─────────────────────────────────────┐
│ CORTEX: Concise Introduction        │
│ - Role of planning orchestrator     │
│ - Interactive process explanation   │
│ - Tips for providing context        │
│ - Expected outcome (zero assumptions)│
└─────────────────────────────────────┘
    ↓
╔═══════════════════════════════════════════════════════════════╗
║              ITERATIVE REQUIREMENTS CYCLE                     ║
║  (Repeat until Definition of Ready achieved)                  ║
╚═══════════════════════════════════════════════════════════════╝
    │
    ├─► 1. User Provides Context
    │       - Describes work
    │       - States requirements
    │       - Mentions constraints
    │
    ├─► 2. CORTEX Analyzes (Using Toolkit)
    │       ┌─────────────────────────────┐
    │       │ Tools Used:                 │
    │       │ • Semantic Search           │
    │       │ • AST Parser                │
    │       │ • Git History Analysis      │
    │       │ • Knowledge Graph Builder   │
    │       │ • Pattern Detector          │
    │       │ • Dependency Mapper         │
    │       └─────────────────────────────┘
    │
    ├─► 3. CORTEX Explains Understanding
    │       - What was discovered
    │       - Relevant patterns found
    │       - Assumptions made (to validate)
    │       - Gaps/ambiguities identified
    │       - Questions to clarify
    │
    ├─► 4. 🆕 CORTEX Asks for Acceptance Criteria
    │       "For user story: {story_description}"
    │       "What are the acceptance criteria?"
    │       
    │       User provides criteria:
    │       - "User can log in with email/password"
    │       - "JWT token generated on successful login"
    │       - "Token expires after 24 hours"
    │       
    │       CORTEX validates SMART criteria:
    │       ✓ Specific
    │       ✓ Measurable
    │       ✓ Achievable
    │       ✓ Relevant
    │       ✓ Testable
    │
    ├─► 5. User Responds with Clarifications
    │
    ├─► 6. Update requirements.yaml (Incremental)
    │       - Add user stories
    │       - Add acceptance criteria
    │       - Update dependencies
    │
    └─► 7. Check DoR Achievement
            ┌──────────────────────────────────┐
            │ Definition of Ready Criteria:    │
            │ ✓ All user stories defined       │
            │ ✓ Acceptance criteria specified  │
            │ ✓ Dependencies identified        │
            │ ✓ Constraints documented         │
            │ ✓ Assumptions validated (zero)   │
            │ ✓ Technical approach agreed      │
            │ ✓ Risks identified & mitigated   │
            └──────────────────────────────────┘
            
            DoR Achieved? ──No──► Continue Cycle
                │
                Yes
                ↓
        ┌───────────────────────────────┐
        │  Approval Checkpoint          │
        │  Present requirements summary │
        │  Request user approval        │
        └───────────────────────────────┘
                ↓
        User Approves? ──No──► Continue Modifications
                │
                Yes
                ↓
        [Proceed to Phase 2]
```

---

### **Key Elements:**

**1. Acceptance Criteria Integration:**
- For each user story identified, CORTEX asks: "What are the acceptance criteria?"
- User provides specific, testable criteria
- CORTEX validates criteria are SMART (Specific, Measurable, Achievable, Relevant, Testable)
- Criteria recorded in requirements.yaml under each user story

**2. Definition of Ready (Enhanced):**
- All user stories clearly defined ✅
- **Acceptance criteria specified for ALL stories** 🆕 ✅
- **All acceptance criteria are testable** 🆕 ✅
- Dependencies identified ✅
- Constraints documented ✅
- Assumptions validated (zero remaining) ✅
- Technical approach agreed upon ✅
- Risks identified and mitigated ✅

**3. Outputs:**
- `requirements/requirements.yaml` - Comprehensive requirements with acceptance criteria
- `analysis/domain-knowledge-final.json` - Knowledge graph built during analysis
- `tracking/requirements-audit.jsonl` - Complete audit trail
- `tracking/requirements-conversation.jsonl` - Interactive session log

---

## 📊 Phase 2: Detailed Plan Generation

### **Objective:** Convert requirements into zero-ambiguity execution plan

**Duration:** 15-25% of planning time  
**Mode:** AUTONOMOUS  
**Trigger:** After user approves requirements.yaml

---

### **Visual Flow:**

```
┌──────────────────────────────────────────────────────────────────┐
│        PHASE 2: Detailed Plan Generation (Zero Ambiguity)        │
└──────────────────────────────────────────────────────────────────┘

[requirements.yaml approved]
    ↓
┌─────────────────────────────────┐
│ 1. Load Approved Requirements   │
│    - Read requirements.yaml     │
│    - Validate DoR flag = true   │
│    - Validate config.yaml       │
│      requirements_approved=true │
└─────────────────────────────────┘
    ↓
┌────────────────────────────────────────┐
│ 2. Generate Feature Structure         │
│    For each feature in requirements:  │
│    ┌──────────────────────────┐       │
│    │ features/feat01-{name}/  │       │
│    │ ├─ feature.yaml          │       │
│    │ ├─ context/              │       │
│    │ │  └─ {name}-context.yaml│       │
│    │ ├─ phases/               │       │
│    │ └─ tracking/             │       │
│    │    └─ progress-tracker.json      │
│    └──────────────────────────┘       │
└────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│ 3. Generate Acceptance Criteria File      │
│    Create acceptance-criteria.yaml:       │
│    ┌──────────────────────────────┐       │
│    │ From requirements.yaml:      │       │
│    │ • Extract acceptance criteria│       │
│    │ • Map to specific phases     │       │
│    │ • Define validation methods  │       │
│    │ • Set priority levels        │       │
│    │ • Add SMART validation flags │       │
│    └──────────────────────────────┘       │
└────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│ 4. Generate Phase Files (Detailed)        │
│    For each phase:                         │
│    Create ##-phase-{name}.yaml with:       │
│    • Complete step-by-step instructions   │
│    • Objectives and deliverables          │
│    • Tasks with validation criteria       │
│    • Acceptance criteria references       │
│    • Dependencies (phases + external)     │
│    • Estimated effort per task            │
└────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│ 5. Add Refactor Phase (Automatic)         │
│    Create 99-phase-refactor.yaml:         │
│    • Holistic review instructions         │
│    • Validate acceptance criteria met     │
│    • Code quality checks                  │
│    • Test coverage validation             │
│    • Refactoring guidelines               │
│    • Documentation review                 │
└────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│ 6. Generate Master Plan File              │
│    {PLAN-ID}-{NAME}-MASTER.yaml:          │
│    • Plan metadata (ID, type, version)    │
│    • Features list with dependencies      │
│    • References to requirements.yaml      │
│    • References to config.yaml            │
│    • Governance rules reference           │
│    • Execution mode (autonomous)          │
└────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ 7. 🆕 GENERATE PLAN VIEWER DASHBOARD (plan-viewer.html) │
│    Comprehensive interactive development dashboard:     │
│    ┌────────────────────────────────────┐              │
│    │ DATA EXTRACTION:                   │              │
│    │ • Read progress-tracker.json       │              │
│    │ • Read acceptance-criteria.yaml    │              │
│    │ • Read all phase YAML files        │              │
│    │ • Read feature.yaml files          │              │
│    │ • Calculate metrics                │              │
│    │   - Total/completed/blocked tasks  │              │
│    │   - AC coverage percentage         │              │
│    │   - Estimated hours remaining      │              │
│    │   - Phase completion percentages   │              │
│    │                                    │              │
│    │ DASHBOARD COMPONENTS:              │              │
│    │ • Header with CORTEX logo & stats  │              │
│    │ • Overall progress visualization   │              │
│    │ • Phase grid with status cards     │              │
│    │ • Task list (detailed per phase)   │              │
│    │ • AC fulfillment tracker           │              │
│    │ • Metrics sidebar                  │              │
│    │ • Timeline visualization           │              │
│    │                                    │              │
│    │ DESIGN SPECIFICATIONS:             │              │
│    │ • Dark Blue Glassmorphism theme    │              │
│    │ • Material Design 3 aesthetic      │              │
│    │ • CSS-only (no backdrop-filter)    │              │
│    │ • Embedded JSON data               │              │
│    │ • file:// protocol compatible      │              │
│    │ • Zero external dependencies       │              │
│    │ • Single self-contained HTML file  │              │
│    │                                    │              │
│    │ COLOR PALETTE:                     │              │
│    │ • Primary: #1a237e (Dark Indigo)  │              │
│    │ • Accent: #7c4dff (Deep Purple)   │              │
│    │ • Background: #0a1628 (Very Dark) │              │
│    │ • Surface: rgba(26,35,126,0.7)    │              │
│    │ • Success: #00e676 (Green)        │              │
│    │ • Warning: #ffab00 (Amber)        │              │
│    │ • Error: #ff5252 (Red)            │              │
│    │ • Info: #40c4ff (Cyan)            │              │
│    └────────────────────────────────────┘              │
│                                                         │
│    OUTPUT: plan-viewer.html (root of plan folder)      │
│    REFERENCE: plan-viewer-dashboard-requirements.yaml  │
└──────────────────────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│ 8. Validate Plan Completeness             │
│    ✓ All phases have instructions         │
│    ✓ All acceptance criteria defined      │
│    ✓ All dependencies mapped               │
│    ✓ Refactor phases added (99-phase-*)   │
│    ✓ NO MD files (YAML/JSON only)         │
│    ✓ Naming conventions followed           │
│    ✓ plan-viewer.html generated            │
│    ✓ All required root files created      │
└────────────────────────────────────────────┘
    │
    Validation Passed?
    │
    Yes ──► [Proceed to Phase 3]
    No  ──► [Pause & Report Issues]
```

---

### **Key Elements:**

**1. Acceptance Criteria Mapping:**
- Extract acceptance criteria from requirements.yaml
- Create dedicated acceptance-criteria.yaml per feature
- Map each criterion to specific phase(s)
- Define validation methods for each criterion
- Add SMART validation flags (Specific, Measurable, Achievable, Relevant, Testable)

**2. Zero-Ambiguity Instructions:**
- Every phase has complete step-by-step instructions
- Every task has clear action steps with validation
- Every deliverable has validation criteria
- Every acceptance criterion has phase mapping
- Dependencies clearly documented (phase + external)

**3. 🆕 Plan Viewer Dashboard Generation:**

The plan-viewer.html is a **comprehensive interactive development dashboard** with:

**Data Integration:**
- Extracts data from progress-tracker.json
- Extracts AC data from acceptance-criteria.yaml  
- Reads all phase YAML files for task details
- Reads feature.yaml files for feature metadata
- Calculates real-time metrics:
  - Total tasks / Completed / In Progress / Blocked
  - AC coverage percentage
  - Estimated hours remaining
  - Phase completion percentages

**Dashboard Components:**
- **Header**: CORTEX logo, plan title, overall progress, quick stats
- **Progress Panel**: Overall progress bar, phase breakdown, task distribution
- **Phase Grid**: Interactive phase cards with expand/collapse, status indicators
- **Task List**: Detailed tasks per phase with status, dependencies, AC links
- **AC Panel**: Acceptance Criteria fulfillment tracker with coverage gaps
- **Metrics Sidebar**: Key metrics (tasks, AC coverage, blocked count, hours)
- **Timeline**: Visual timeline showing phase progression

**Technical Specifications:**
- **Design**: Dark Blue Glassmorphism + Material Design 3
- **Compatibility**: file:// protocol (no CDN, no external resources)
- **Dependencies**: Zero external dependencies
- **Format**: Single self-contained HTML file
- **Styling**: Inline CSS only (CSS-only glassmorphism, no backdrop-filter)
- **Data**: Embedded JSON in `<script type='application/json'>`
- **Interactivity**: Vanilla JavaScript (no frameworks)
- **Colors**: 
  - Primary: #1a237e (Dark Indigo)
  - Accent: #7c4dff (Deep Purple)
  - Background: #0a1628 (Very Dark Blue)
  - Success: #00e676 | Warning: #ffab00 | Error: #ff5252

**Reference Document:**  
`plan-viewer-dashboard-requirements.yaml` (365 lines) - Complete UI/UX specifications

**4. Outputs:**
- Complete feature/phase structure (features/feat##-{name}/)
- acceptance-criteria.yaml per feature (with SMART validation)
- 99-phase-refactor.yaml per feature (mandatory quality phase)
- Master plan YAML with metadata ({PLAN-ID}-{NAME}-MASTER.yaml)
- **plan-viewer.html** (interactive dashboard at plan root)
- progress-tracker.json (epic + per-feature tracking)
- All required root files (epic.yaml, README.md, EXECUTION-GUIDE.yaml, config.yaml)

---

## 📊 Phase 3: Plan Approval & Config Creation

### **Objective:** Get approval and create execution config

**Duration:** Variable (user-dependent)  
**Mode:** INTERACTIVE  
**Trigger:** After plan generation completes

---

### **Visual Flow:**

```
┌──────────────────────────────────────────────────────────────────┐
│      PHASE 3: Plan Approval & Config Creation                    │
└──────────────────────────────────────────────────────────────────┘

[Plan generated with zero ambiguity + plan-viewer.html created]
    ↓
┌─────────────────────────────────────────┐
│ 1. Plan Viewer Already Generated        │
│    plan-viewer.html created in Phase 2: │
│    • Feature/phase structure            │
│    • Acceptance criteria tracker        │
│    • Dependency graph                   │
│    • Timeline estimates                 │
│    • Real-time progress metrics         │
│    • Interactive dashboard (file://)    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. Present Plan Summary to User        │
│    Summary includes:                    │
│    • Features: 3                        │
│    • Phases: 14 (incl. 3 refactor)     │
│    • Tasks: 42                          │
│    • Acceptance Criteria: 24           │
│    • Estimated: 28 hours                │
│    • Zero Ambiguity: ✅ Validated      │
│    • Dashboard: ✅ plan-viewer.html    │
└─────────────────────────────────────────┘
    ↓
┌────────────────────────────────────────────┐
│ 3. Request Approval for Execution         │
│    "Review plan-viewer.html and approve   │
│     to begin autonomous execution."       │
│                                           │
│    User can:                              │
│    • Open file:// plan-viewer.html       │
│    • Review all features, phases, tasks  │
│    • Check acceptance criteria coverage  │
│    • Validate dependencies               │
│    • See timeline estimates              │
└────────────────────────────────────────────┘
    ↓
    User Response?
    │
    ├─► Approve ──────────────────────┐
    │                                  │
    ├─► Request Modifications ────┐   │
    │   ↓                          │   │
    │   Loop back to Phase 2       │   │
    │   (regenerate affected)      │   │
    │   - Update phase files       │   │
    │   - Regenerate plan-viewer   │   │
    │                              │   │
    └─► Reject ──────────────┐    │   │
        ↓                    │    │   │
        Pause & Exit         │    │   │
                             │    │   │
┌────────────────────────────┘    │   │
│ Modifications Applied           │   │
│ - Phase files updated           │   │
│ - plan-viewer.html regenerated  │   │
└─────────────────────────────────┘   │
                                      │
┌─────────────────────────────────────┴───────────────┐
│ 4. 🆕 CREATE/UPDATE PLAN CONFIG FILE (config.yaml)  │
│    ┌──────────────────────────────────┐             │
│    │ governance:                      │             │
│    │   approval_granted: true  🔒     │             │
│    │   approved_by: "Asif Hussain"    │             │
│    │   approval_date: "2026-01-09"    │             │
│    │   approval_scope: "full"         │             │
│    │   approval_expires: null         │             │
│    │                                  │             │
│    │ execution:                       │             │
│    │   autonomous_mode: true          │             │
│    │   pause_on_error: true           │             │
│    │   max_retries: 3                 │             │
│    │                                  │             │
│    │ acceptance_criteria:             │             │
│    │   enforcement: "strict"          │             │
│    │   validation_required: true      │             │
│    │   min_criteria_met: 100          │             │
│    │                                  │             │
│    │ presentation:                    │             │
│    │   feature_intro_max_lines: 3     │             │
│    │   phase_intro_max_lines: 3       │             │
│    │   show_progress_bars: true       │             │
│    │   html_viewer_enabled: true      │             │
│    └──────────────────────────────────┘             │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 5. Update Master Plan                   │
│    Reference config.yaml in master:     │
│    config_file: "config.yaml"           │
│    dashboard_file: "plan-viewer.html"   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 6. Log Approval Event                   │
│    tracking/plan-approval-audit.jsonl   │
│    • Timestamp                          │
│    • Approved by                        │
│    • Approval scope                     │
│    • Features/phases approved           │
│    • Dashboard URL                      │
└─────────────────────────────────────────┘
    ↓
[Proceed to Phase 4]
```

---

### **Key Elements:**

**1. 🆕 Plan Configuration File (config.yaml):**

Created/updated automatically when user approves plan. Contains:

**Governance Section:**
- `approval_granted: true` 🔒 (Master Orchestrator checks this)
- `approved_by:` User name who approved
- `approval_date:` Timestamp of approval
- `approval_scope:` "full", "feature-by-feature", or "phase-by-phase"
- `approval_expires:` Optional expiration date (null = no expiration)

**Execution Settings:**
- `autonomous_mode:` true/false
- `pause_on_error:` true/false
- `max_retries:` 3 (default)

**Acceptance Criteria Enforcement:**
- `enforcement:` "strict", "moderate", "relaxed"
- `validation_required:` true/false
- `min_criteria_met:` percentage threshold (0-100)

**Presentation Settings:**
- `feature_intro_max_lines:` 3 (cognitive load management)
- `phase_intro_max_lines:` 3 (concise introductions)
- `show_progress_bars:` true (visual progress indicators)
- `html_viewer_enabled:` true (plan-viewer.html available)

**2. Config-Based Approval Enforcement:**
- Master Orchestrator MUST check config.yaml before execution
- If `approval_granted != true`, reject execution
- If config.yaml missing, reject execution
- If approval expired (optional timeout), reject execution

**3. Plan Viewer Dashboard (Already Generated in Phase 2):**
- plan-viewer.html created during plan generation
- Interactive dashboard opened via file:// protocol
- User reviews features, phases, tasks, AC coverage
- Dashboard auto-refreshes during execution (via progress-tracker.json polling)

**4. Modification Workflow:**
- If user requests changes, loop back to Phase 2
- Regenerate affected phase files
- **Regenerate plan-viewer.html** with updated data
- Re-present for approval

**5. Outputs:**
- config.yaml (plan configuration with approval status)
- Updated master YAML (with config + dashboard references)
- Approval audit log (tracking/plan-approval-audit.jsonl)
- plan-viewer.html (already created in Phase 2, ready for review)

---

## 📊 Phase 4: Autonomous Execution with Config Validation

### **Objective:** Execute plan autonomously with config-based approval check

**Duration:** 50-70% of total time  
**Mode:** AUTONOMOUS  
**Trigger:** After approval granted in config.yaml

---

### **Visual Flow:**

```
┌──────────────────────────────────────────────────────────────────┐
│        PHASE 4: Autonomous Execution (Config-Validated)          │
└──────────────────────────────────────────────────────────────────┘

[User initiates execution OR continuation]
    ↓
┌────────────────────────────────────────────────────────────┐
│ 🆕 MASTER ORCHESTRATOR: PRE-EXECUTION VALIDATION           │
│                                                            │
│ 1. Check config.yaml exists                               │
│    ✓ File found                                           │
│                                                            │
│ 2. Validate approval_granted = true                       │
│    ✓ Approval confirmed                                   │
│                                                            │
│ 3. Check approved_by and approval_date                    │
│    ✓ Valid approval metadata                              │
│                                                            │
│ 4. Validate acceptance_criteria enforcement               │
│    ✓ Enforcement level: "strict"                          │
│                                                            │
│ IF ANY CHECK FAILS:                                       │
│    ❌ REJECT EXECUTION                                    │
│    ❌ Display: "Plan not approved. Check config.yaml"    │
│    ❌ Exit                                                │
│                                                            │
│ IF ALL CHECKS PASS:                                       │
│    ✅ PROCEED TO EXECUTION                                │
└────────────────────────────────────────────────────────────┘
    ↓
╔═══════════════════════════════════════════════════════════════╗
║              AUTONOMOUS EXECUTION LOOP                        ║
║  (For Each Feature, For Each Phase)                          ║
╚═══════════════════════════════════════════════════════════════╝
    │
    FOR EACH FEATURE:
    │
    ├─► 1. Feature Introduction (3 lines)
    │       "## 🎯 Feature 01: OAuth2 Integration"
    │       "Integrates OAuth2 with JWT tokens..."
    │       "Phases: 5 | Estimated: 12h | Refactor: Yes"
    │
    │   FOR EACH PHASE:
    │   │
    │   ├─► 2.1. Phase Introduction (3 lines)
    │   │       "### ⚙️ Phase 01: OAuth2 Provider Setup"
    │   │       "Configures OAuth2Provider with credentials..."
    │   │
    │   ├─► 2.2. Execute Phase Instructions
    │   │       Read phase YAML file
    │   │       Follow step-by-step instructions
    │   │       Execute tasks sequentially
    │   │
    │   ├─► 2.3. Validate Phase Completion
    │   │       ┌────────────────────────────────┐
    │   │       │ Validation Checks:             │
    │   │       │ ✓ All deliverables created     │
    │   │       │ ✓ Tests pass (if TDD enabled)  │
    │   │       │ ✓ Acceptance criteria met      │
    │   │       │ ✓ Phase criteria validated     │
    │   │       └────────────────────────────────┘
    │   │       │
    │   │       Validation Failed?
    │   │       ├─► Yes: Retry (up to 3x)
    │   │       │       Still failing? Pause & notify
    │   │       │
    │   │       └─► No: Mark complete, proceed
    │   │
    │   ├─► 2.4. IF Phase = 99-phase-refactor.yaml
    │   │       Execute holistic review:
    │   │       ┌────────────────────────────────┐
    │   │       │ • Review acceptance criteria   │
    │   │       │ • Validate ALL criteria met    │
    │   │       │ • Check code quality           │
    │   │       │ • Verify test coverage         │
    │   │       │ • Review documentation         │
    │   │       │ • Implement refactoring        │
    │   │       │ • Run full test suite          │
    │   │       └────────────────────────────────┘
    │   │
    │   └─► 2.5. Update Progress
    │           ┌────────────────────────────────┐
    │           │ 📊 Progress Update             │
    │           │ Feature: OAuth2 (25%)          │
    │           │ Phase: Setup ✅ COMPLETED      │
    │           │ Duration: 2.8h (Est: 3h)       │
    │           │ Acceptance Criteria: 2/8       │
    │           │ Next: Phase 02                 │
    │           └────────────────────────────────┘
    │           Update files:
    │           • progress-tracker.json
    │           • execution-audit.jsonl
    │           • plan-viewer.html (refresh)
    │
    ├─► 3. Validate Feature Completion
    │       ┌────────────────────────────────────┐
    │       │ Feature-Level Validation:          │
    │       │ ✓ All phases completed             │
    │       │ ✓ Refactor phase completed         │
    │       │ ✓ ALL acceptance criteria met      │
    │       │ ✓ Feature tests pass               │
    │       │ ✓ No regressions                   │
    │       └────────────────────────────────────┘
    │
    ├─► 4. Generate Completion Report
    │       Create feat01-{name}-complete.yaml:
    │       • Completion date
    │       • Phases completed: 5/5
    │       • Acceptance criteria: 8/8 ✅
    │       • Test coverage: 94%
    │       • Quality metrics
    │       • Refactor improvements
    │
    └─► 5. Move to Next Feature
            Repeat until all features complete
    
    ↓
┌────────────────────────────────────────┐
│ EXECUTION COMPLETE                     │
│ • All features: ✅                     │
│ • All acceptance criteria: ✅          │
│ • Final report generated               │
└────────────────────────────────────────┘
```

---

### **Key Elements:**

**1. 🆕 Pre-Execution Config Validation:**

Master Orchestrator checks config.yaml BEFORE execution:

**Validation Steps:**
1. ✅ config.yaml exists in plan folder
2. ✅ `governance.approval_granted = true`
3. ✅ `approved_by` and `approval_date` present
4. ✅ Acceptance criteria enforcement configured

**If ANY check fails:**
- ❌ **REJECT EXECUTION**
- Display error: "Plan not approved. Check config.yaml"
- Exit without executing

**If ALL checks pass:**
- ✅ **PROCEED TO EXECUTION**
- Log validation success to audit trail

**2. Acceptance Criteria Validation:**
- During phase execution, check acceptance-criteria.yaml
- Validate criteria met before marking phase complete
- Refactor phase validates ALL feature criteria
- Report criteria status in progress updates

**3. No-Stopping Policy:**
- Execute continuously after config validation
- Only stop on validation failure or critical error
- Informational updates only (3-line intros, concise progress)

**4. Outputs:**
- Implemented features and phases
- Test files with coverage reports
- Feature completion reports (YAML: feat##-{name}-complete.yaml)
- Updated progress trackers (progress-tracker.json - epic + per-feature)
- Complete execution audit trail (execution-audit.jsonl)
- **Auto-refreshing plan-viewer.html** (polling progress-tracker.json every 5s)
- Quality metrics (per-feature tracking/quality-metrics.json)
- Refactor reports (per-feature tracking/refactor-report.yaml)

---

## 🎨 Plan Viewer Dashboard - Live Progress Tracking

### **Dashboard Auto-Refresh Mechanism:**

```
┌────────────────────────────────────────────────────┐
│    PLAN VIEWER DASHBOARD - LIVE PROGRESS          │
└────────────────────────────────────────────────────┘

plan-viewer.html (opened in browser)
    ↓
┌─────────────────────────────────────┐
│ JavaScript Polling (Every 5s)       │
│ • Read progress-tracker.json        │
│ • Read acceptance-criteria.yaml     │
│ • Calculate updated metrics         │
│ • Update UI components              │
└─────────────────────────────────────┘
    ↓
Phase 4 Execution Updates Files:
    ↓
progress-tracker.json modified
    ↓
Dashboard auto-detects change (file timestamp)
    ↓
UI refreshes with new data:
    • Progress bars update
    • Phase cards update status
    • Task list shows completion
    • AC panel shows fulfilled criteria
    • Metrics sidebar updates counts
```

**Implementation:**
- Embedded JavaScript checks file modification timestamps
- Polls progress-tracker.json every 5 seconds
- Updates only changed components (efficient DOM updates)
- No page reload required (smooth user experience)
- Works with file:// protocol (no server required)

**Visual Feedback:**
- ✅ Green checkmarks for completed tasks
- 🔄 Amber spinner for in-progress tasks
- ⏸️ Gray icons for pending tasks
- ❌ Red indicators for blocked tasks
- Progress bars animate on value change

---

## 🔒 Config-Based Approval Enforcement

### **Security Model:**

```
┌─────────────────────────────────────────────────────────────┐
│         CONFIG-BASED APPROVAL ENFORCEMENT MODEL             │
└─────────────────────────────────────────────────────────────┘

Master Orchestrator receives execution request
    ↓
┌──────────────────────────────────┐
│ Load plan config.yaml            │
└──────────────────────────────────┘
    ↓
    ┌─────────────────────────────────────┐
    │ governance.approval_granted ?       │
    └─────────────────────────────────────┘
         │           │
         Yes         No
         │           ↓
         │      ┌──────────────────────────┐
         │      │ ❌ REJECT EXECUTION      │
         │      │ Display error message    │
         │      │ Exit                     │
         │      └──────────────────────────┘
         │
         ├─► Valid approved_by?
         │      Yes → Continue
         │      No  → Reject
         │
         ├─► Valid approval_date?
         │      Yes → Continue
         │      No  → Reject
         │
         ├─► Valid approval_scope?
         │      Yes → Continue
         │      No  → Reject
         │
         └─► ✅ ALL CHECKS PASS
                 ↓
            [PROCEED TO EXECUTION]
```

---

### **Config File Structure:**

```
config.yaml
├─ governance:
│  ├─ approval_granted: true/false  🔒 CRITICAL
│  ├─ approved_by: "User Name"
│  ├─ approval_date: "YYYY-MM-DD"
│  ├─ approval_scope: "full"
│  └─ approval_expires: "YYYY-MM-DD" (optional)
│
├─ execution:
│  ├─ autonomous_mode: true/false
│  ├─ pause_on_error: true/false
│  └─ max_retries: 3
│
├─ acceptance_criteria:
│  ├─ enforcement: "strict"/"moderate"/"relaxed"
│  ├─ validation_required: true/false
│  └─ min_criteria_met: 100 (percentage)
│
└─ governance_rules:
   ├─ tdd_enforcement: true/false
   ├─ holistic_discovery: true/false
   └─ git_isolation: true/false
```

**🔒 The `approval_granted` flag is the master switch for execution.**

---

## �️ CORTEX Toolkit - Phase 1 Analysis Tools

During Phase 1 (Interactive Requirements Gathering), the Master Orchestrator uses the **CORTEX Toolkit** to analyze workspace context:

### **Toolkit Components:**

| Tool | Purpose | Output |
|------|---------|--------|
| **Semantic Search** | Search workspace for relevant code/docs | Context matches with relevance scores |
| **AST Parser** | Parse files to understand structure | Entity-relationship data (classes, functions, methods) |
| **Git History Analysis** | Review commits, comments for context | Historical patterns, author insights, change frequency |
| **Knowledge Graph Builder** | Build entity-relationship graph | domain-knowledge-incremental.json |
| **Pattern Detector** | Identify reusable patterns | Common patterns, architectural styles |
| **Dependency Mapper** | Map dependencies and relationships | dependencies-discovered.yaml |

### **Analysis Workflow:**

```
User: "plan user authentication with OAuth2"
    ↓
┌────────────────────────────────────────┐
│ CORTEX Toolkit Activates               │
└────────────────────────────────────────┘
    │
    ├─► Semantic Search
    │   • Search for "oauth2", "authentication", "jwt", "tokens"
    │   • Find existing auth implementations
    │   • Identify reusable components
    │
    ├─► AST Parser
    │   • Parse relevant auth files
    │   • Extract class structures (AuthService, JWTProvider, etc.)
    │   • Identify methods (login, logout, refresh_token)
    │
    ├─► Git History Analysis
    │   • Review auth-related commits
    │   • Identify security patches
    │   • Find test patterns
    │
    ├─► Knowledge Graph Builder
    │   • Build entity graph (User → AuthService → JWTProvider)
    │   • Map relationships (uses, depends_on, inherits)
    │
    ├─► Pattern Detector
    │   • Detect patterns (OAuth2, JWT, Refresh Token)
    │   • Identify architectural style (microservices, monolith)
    │
    └─► Dependency Mapper
        • Map external dependencies (oauth2-provider, pyjwt)
        • Map internal dependencies (UserService, DatabaseService)
    ↓
CORTEX Explains Understanding to User:
"Found existing OAuth2 implementation in src/auth/.
Detected JWT token generation with 24h expiration.
Identified reusable UserService and RoleService.
Missing: Refresh token rotation, MFA support.
Questions: Should we add MFA? Token expiration policy?"
```

### **Outputs:**

- `analysis/context-analysis-turn-{N}.yaml` - Per-iteration analysis
- `analysis/knowledge-graph-incremental.json` - Entity-relationship graph
- `analysis/dependencies-discovered.yaml` - Dependency mapping
- `analysis/domain-knowledge-final.json` - Final consolidated knowledge graph

---

## �📋 Complete Workflow Summary

### **Phase 1: Interactive Requirements (30-50%)**

**User Action:** Provide requirements and acceptance criteria  
**CORTEX Action:** Analyze with Toolkit, explain understanding, validate SMART criteria, update requirements  
**Tools Used:** Semantic Search, AST Parser, Git History, Knowledge Graph, Pattern Detector, Dependency Mapper  
**Output:** requirements.yaml with acceptance criteria, domain-knowledge-final.json, config.yaml (with requirements approval)  
**Gate:** DoR achievement + user approval

---

### **Phase 2: Plan Generation (15-25%)**

**Trigger:** Requirements approved (config.yaml: requirements_approved = true)  
**CORTEX Action:** Generate features, phases, acceptance-criteria.yaml, refactor phases, **plan-viewer.html**  
**Output:** Complete zero-ambiguity plan with interactive dashboard  
**Gate:** Zero ambiguity validation + plan-viewer.html generated

---

### **Phase 3: Plan Approval & Config (Variable)**

**User Action:** Review plan-viewer.html (already generated in Phase 2) and approve  
**CORTEX Action:** Update config.yaml with `approval_granted: true`, log approval  
**Output:** config.yaml (with execution approval), approval audit log  
**Gate:** User approval recorded in config (approval_granted = true)

---

### **Phase 4: Autonomous Execution (50-70%)**

**Trigger:** Execution requested  
**Master Orchestrator:** Validates config.yaml (approval_granted = true)  
**If Valid:** Execute autonomously with acceptance criteria validation, **update progress-tracker.json** (dashboard auto-refreshes)  
**If Invalid:** REJECT execution with error message  
**Output:** Implemented features, completion reports, audit trail, **live dashboard updates**

---

## 🎯 Key Workflow Enhancements

### **1. Acceptance Criteria in Interactive Phase**
- User provides criteria during requirements gathering
- Criteria validated as SMART (Specific, Measurable, Achievable, Relevant, Testable)
- Included in Definition of Ready
- Mapped to phases during plan generation

### **2. Config-Based Approval Enforcement**
- config.yaml created when plan approved
- `approval_granted: true` is master execution switch
- Master Orchestrator validates config BEFORE execution
- Execution rejected if approval not present

### **3. Acceptance Criteria Tracking**
- acceptance-criteria.yaml per feature
- Criteria validated during phase execution
- Refactor phase validates ALL criteria met
- Progress updates show criteria completion

### **4. Two-Gate Approval**
- Gate 1: Requirements approval (Phase 1 → Phase 2)
- Gate 2: Plan approval (Phase 3 → Phase 4)
- Both gates recorded in audit trail

### **5. Zero-Stopping Execution**
- After config validation, execute autonomously
- Only stop on validation failure or error
- Acceptance criteria checked automatically

---

## 📊 Visual Decision Tree

```
User says "plan X"
    ↓
┌────────────────────────┐
│ Phase 1: Interactive   │
│ • Gather requirements  │
│ • Ask for AC           │ ←──┐
│ • Validate SMART       │    │
│ • Analyze workspace    │    │
└────────────────────────┘    │
    ↓                         │
    DoR Achieved?             │
    ├─ No ────────────────────┘
    └─ Yes
        ↓
    User Approves Requirements?
    ├─ No ────────────────────┐
    │                         │
    └─ Yes                    │
        ↓                     │
┌────────────────────────┐   │
│ Phase 2: Generate Plan │   │
│ • Create features      │   │
│ • Create AC file       │   │
│ • Add refactor phases  │   │
│ • Validate zero ambig  │   │
└────────────────────────┘   │
    ↓                        │
    Validation Passed?       │
    ├─ No → Fix Issues ──────┤
    └─ Yes                   │
        ↓                    │
┌────────────────────────┐  │
│ Phase 3: Get Approval  │  │
│ • Show plan-viewer     │  │
│ • Request approval     │  │
│ • Create config.yaml   │  │
└────────────────────────┘  │
    ↓                       │
    User Approves Plan?     │
    ├─ No → Modify ─────────┘
    └─ Yes
        ↓
    config.yaml created
    approval_granted: true
        ↓
┌────────────────────────┐
│ Phase 4: Execute       │
│ • Validate config      │ ←── Master Orchestrator
│ • Execute autonomously │      checks approval
│ • Validate AC          │
│ • Generate reports     │
└────────────────────────┘
    ↓
[COMPLETE]
```

---

## ✅ Summary: What Makes This Workflow Effective

**1. Interactive Requirements Gathering with CORTEX Toolkit**
- Collaborative approach with AI-powered workspace analysis
- **6 specialized tools** (Semantic Search, AST Parser, Git History, Knowledge Graph, Pattern Detector, Dependency Mapper)
- Acceptance criteria gathered upfront with SMART validation
- Definition of Ready ensures zero assumptions
- Iterative cycle until DoR achieved

**2. Zero-Ambiguity Plan Generation with Live Dashboard**
- Complete step-by-step instructions for autonomous execution
- Acceptance criteria mapped to specific phases
- Refactor phases ensure quality (99-phase-refactor.yaml)
- **plan-viewer.html** generated automatically with:
  - Dark Blue Glassmorphism + Material Design 3
  - Interactive progress tracking
  - Acceptance criteria fulfillment visualization
  - Real-time metrics dashboard
  - file:// protocol compatible (zero dependencies)

**3. Config-Based Approval Enforcement**
- Clear approval state in config.yaml (approval_granted flag)
- Master Orchestrator validates config before execution
- Comprehensive approval metadata (approved_by, date, scope, expiration)
- Audit trail for compliance (plan-approval-audit.jsonl)
- Presentation settings (intro line limits, progress display)

**4. Autonomous Execution with Live Dashboard Updates**
- Config-validated before execution (rejects if not approved)
- Acceptance criteria validated during each phase
- Continuous execution with concise updates (3-line intros)
- **Live dashboard** auto-refreshes every 5s (progress-tracker.json polling)
- Visual feedback: ✅ Complete | 🔄 In Progress | ⏸️ Pending | ❌ Blocked

**5. Complete Traceability & Audit**
- Requirements → Plan → Execution → Completion (full lifecycle)
- Every interaction logged (JSONL audit trails)
- Acceptance criteria tracked throughout (requirements → plan → execution)
- Knowledge graph preserved (domain-knowledge-final.json)
- Quality metrics tracked (test coverage, code quality, refactor improvements)

**6. Governance Integration**
- SKULL rules enforcement (TDD, holistic discovery, git isolation)
- NO MD files policy (YAML/JSON only for autonomous consumption)
- Structured data enables AI orchestration
- Master Orchestrator coordination layer
- 61 brain protection rules + 64 governance patterns

---

**The workflow ensures collaborative requirements gathering with AI-powered analysis, zero-ambiguity planning with interactive dashboards, config-enforced approval with comprehensive governance, and autonomous acceptance-driven execution with live progress visualization.** 🚀

---

## 📚 Reference Documents

**Planning Structure:**
- `INTELLIGENT-PLANNING-STRUCTURE-V6.yaml` (1,456 lines) - Complete technical specification
- `INTERACTIVE-PLANNING-WORKFLOW-V6-EXECUTIVE-SUMMARY.md` - Detailed workflow overview
- `EXECUTIVE-SUMMARY-V6-UPDATED.md` - Folder structure and naming conventions

**Dashboard Specifications:**
- `plan-viewer-dashboard-requirements.yaml` (365 lines) - Complete UI/UX requirements
- Design: Dark Blue Glassmorphism + Material Design 3
- Components: Header, Progress Panel, Phase Grid, Task List, AC Panel, Metrics Sidebar, Timeline

**Acceptance Criteria:**
- `CX6-acceptance-criteria.yaml` (4,319 lines) - 390+ acceptance criteria
- `CX6-requirements.yaml` (338 lines) - Active remediation plan
- `CX6-completion-criteria.yaml` (550 lines) - 20 automated gates

**Governance:**
- `CX6-GOVERNANCE.yaml` (573 lines) - Machine-readable governance rules
- `brain-protection-rules.yaml` - 61 SKULL rules
- `cortex-operations.yaml` - 64+ governance patterns

---

**Document Version:** 2.0  
**Last Updated:** 2026-01-09  
**Author:** Asif Hussain  
**Status:** ✅ COMPREHENSIVE - All Context Integrated

**Related Files:**
- `INTELLIGENT-PLANNING-STRUCTURE-V6.yaml` - Technical specification (1,456 lines)
- `INTERACTIVE-PLANNING-WORKFLOW-V6-EXECUTIVE-SUMMARY.md` - Detailed overview
- `plan-viewer-dashboard-requirements.yaml` - Dashboard specs (365 lines)
- `CX6-acceptance-criteria.yaml` - 390+ acceptance criteria (4,319 lines)
- `CX6-requirements.yaml` - Active remediation plan (338 lines)
- `CX6-GOVERNANCE.yaml` - Governance rules (573 lines)

**Changelog:**
- v2.0 (2026-01-09): 
  - ✅ Added plan-viewer.html generation in Phase 2
  - ✅ Added CORTEX Toolkit section (6 analysis tools)
  - ✅ Added live dashboard auto-refresh mechanism
  - ✅ Enhanced config.yaml with presentation settings
  - ✅ Added comprehensive reference documentation
  - ✅ Added visual feedback indicators
  - ✅ Integrated all missing context from acceptance-criteria/ folder
- v1.0 (2026-01-09): Initial comprehensive workflow with visual diagrams

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
