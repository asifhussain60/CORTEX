# CORTEX 2.0: Feature Planning System

**Version:** 2.1.0  
**Design Date:** 2025-11-13  
**Status:** 🎯 Design Phase - Priority Addition to CORTEX 2.0  
**Purpose:** Interactive feature planning with Work Planner agent

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

---

## 🎯 Executive Summary

**Problem:** Users struggle to break down complex features into actionable tasks. Current CORTEX requires detailed specifications before execution, creating friction for exploratory work.

**Solution:** Implement **interactive feature planning** that collaborates with users to:
- Understand feature intent through questions
- Break down requirements into phases/tasks
- Identify dependencies and risks
- Generate actionable roadmaps
- Store plans for future execution tracking

**Impact:** 
- Faster feature kickoff (idea → executable plan in minutes)
- Better planning quality (structured approach prevents missed requirements)
- Seamless execution (plans feed directly into Executor agent)
- Learning accumulation (successful patterns stored in Knowledge Graph)

**Integration Point:** CORTEX 2.0 (current release) - uses existing Work Planner agent, no new architecture needed

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│              CORTEX 2.0 FEATURE PLANNING FLOW                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  USER INPUT: "Let's plan a feature"                          │
│              ↓                                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  INTENT DETECTOR (Right Brain)                         │ │
│  │  ─────────────────────────────────────────────────────│ │
│  │  • Detects: PLAN operation                            │ │
│  │  • Activates: Work Planner agent                      │ │
│  │  • Mode: Interactive (not batch)                      │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               ↓                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  WORK PLANNER AGENT (Right Brain)                      │ │
│  │  ─────────────────────────────────────────────────────│ │
│  │                                                        │ │
│  │  Phase 1: Discovery                                   │ │
│  │  • Ask clarifying questions                           │ │
│  │  • Understand scope and constraints                   │ │
│  │  • Identify similar past features (Pattern Matcher)   │ │
│  │                                                        │ │
│  │  Phase 2: Breakdown                                   │ │
│  │  • Decompose into phases/milestones                   │ │
│  │  • Identify tasks within each phase                   │ │
│  │  • Map dependencies                                   │ │
│  │  • Estimate complexity                                │ │
│  │                                                        │ │
│  │  Phase 3: Risk Analysis                               │ │
│  │  • Identify technical risks                           │ │
│  │  • Suggest mitigation strategies                      │ │
│  │  • Flag unknown unknowns                              │ │
│  │                                                        │ │
│  │  Phase 4: Roadmap Generation                          │ │
│  │  • Generate phase-based roadmap                       │ │
│  │  • Add acceptance criteria                            │ │
│  │  • Create markdown document                           │ │
│  │  • Store to cortex-brain/feature-plans/              │ │
│  │                                                        │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               ↓                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TIER 1 WORKING MEMORY (Storage)                       │ │
│  │  ─────────────────────────────────────────────────────│ │
│  │  • Feature plan saved to database                     │ │
│  │  • Linked to current conversation                     │ │
│  │  • Metadata: feature name, phases, status             │ │
│  │  • Markdown file: cortex-brain/feature-plans/         │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               ↓                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  EXECUTOR AGENT (Left Brain) - Ready for execution    │ │
│  │  ─────────────────────────────────────────────────────│ │
│  │  • User says: "start Phase 1" or "continue"           │ │
│  │  • Loads feature plan from Tier 1                     │ │
│  │  • Executes tasks with full context                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Agent Coordination

**Work Planner (Primary):**
- Leads interactive planning session
- Asks clarifying questions
- Breaks down requirements
- Generates structured plans

**Pattern Matcher (Supporting):**
- Searches Tier 2 Knowledge Graph for similar past features
- Suggests proven approaches
- Warns about common pitfalls

**Architect (Supporting):**
- Reviews technical feasibility
- Identifies system impact
- Suggests architectural patterns

**Corpus Callosum (Coordination):**
- Manages agent collaboration
- Ensures Work Planner gets Pattern Matcher + Architect input
- Synthesizes multi-agent insights

---

## 🎯 User Experience Flow

### Example Session

**User:** "Let's plan a feature"

**CORTEX (Work Planner):**
```
🧠 CORTEX Feature Planning

📝 Your Request: Start interactive feature planning session

🎯 MY Understanding: You want to plan a new feature and need help 
breaking it down into actionable tasks

⚠️ Challenge: ✓ Accept
   Feature planning is most effective when we understand requirements 
   before diving into implementation.

💬 Response: I'll guide you through planning this feature with a 
structured approach. We'll identify requirements, break down the work, 
and create an executable roadmap.

Let me start with some questions:

1. **What is the feature?** (Brief description of what you want to build)
2. **Why do you need it?** (Problem it solves or value it provides)
3. **Who is it for?** (End users, developers, internal tools, etc.)
4. **Any constraints?** (Time, technology, compatibility requirements)

Please answer these questions, or say "skip discovery" if you want to 
provide a detailed spec upfront.
```

**User:** "Add authentication to the dashboard so only authorized users can access it. It's for end users. We need it to protect sensitive data. Must work with existing user service."

**CORTEX (Work Planner with Pattern Matcher):**
```
🧠 CORTEX Feature Analysis

📝 Your Request: Add authentication to dashboard with user service integration

🎯 MY Understanding: Implement access control using existing user service 
to prevent unauthorized dashboard access

⚠️ Challenge: ✓ Accept
   This is a critical security feature. I found 2 similar features in 
   your history that we can learn from.

💬 Response: I've analyzed similar authentication implementations in your 
past work. Here's what I recommend:

**Pattern Match:** Your "Admin Panel Auth" feature (2024-08-15)
- Used route guards + JWT tokens
- Took 3 phases, 2 weeks total
- Success rate: 100% (no security issues found)

**Suggested Approach:**

☐ **Phase 1: Authentication Core** (3-5 days)
   • Integrate with existing user service API
   • Implement login UI (form, validation, error handling)
   • Add session management (JWT or session cookies)
   • Create auth service layer (login, logout, session check)

☐ **Phase 2: Route Protection** (2-3 days)
   • Add route guards to all dashboard pages
   • Implement redirect logic (unauthorized → login page)
   • Handle edge cases (expired sessions, invalid tokens)
   • Add "Remember me" functionality (optional)

☐ **Phase 3: Testing & Security** (2-3 days)
   • Unit tests for auth service
   • Integration tests for protected routes
   • Security audit (SQL injection, XSS, CSRF protection)
   • Edge case testing (concurrent logins, session timeout)

☐ **Phase 4: Production Readiness** (1-2 days)
   • Error handling and user feedback
   • Logging (login attempts, failures)
   • Documentation (API, user guide)
   • Deployment checklist

**Dependencies Identified:**
- User service must expose `/api/auth/login` and `/api/auth/verify`
- Dashboard routing system must support guards/middleware
- Frontend state management for auth state

**Risks & Mitigations:**
- ⚠️ **Risk:** Session management conflicts with existing state
  - **Mitigation:** Use isolated auth state, test integration early
- ⚠️ **Risk:** Breaking existing dashboard functionality
  - **Mitigation:** Feature flag for auth, gradual rollout

**Acceptance Criteria:**
- ✅ Only authenticated users can access dashboard
- ✅ Login UI is intuitive and handles errors gracefully
- ✅ Sessions persist across page refreshes
- ✅ Security audit passes (no vulnerabilities)
- ✅ All tests pass (unit + integration)

🔍 Next Steps:
   1. Review and approve this plan
   2. Make adjustments (add/remove phases, change scope)
   3. Start Phase 1 implementation
   4. Save plan and execute later

Which would you like to do?
```

**User:** "Looks good, start Phase 1"

**CORTEX (Executor with Work Planner context):**
```
🧠 CORTEX Phase 1 Execution

📝 Your Request: Begin Phase 1 (Authentication Core) of dashboard auth feature

🎯 MY Understanding: Implement user service integration, login UI, and 
session management as planned

⚠️ Challenge: ✓ Accept
   All prerequisites met (user service exists, plan approved). Ready to execute.

💬 Response: Starting Phase 1 with full context from feature plan. I'll 
implement the 4 tasks in sequence and validate each before proceeding.

[Executor proceeds with implementation...]
```

---

## 🎯 Feature Specification

### FR-2.1.1: Interactive Planning Workflow

**Priority:** High  
**Effort:** Medium (2-3 weeks)

**Description:** Implement conversational feature planning that guides users through requirements discovery, breakdown, and roadmap generation.

**Acceptance Criteria:**
1. ✅ User can initiate planning with "let's plan a feature"
2. ✅ Work Planner asks clarifying questions (what, why, who, constraints)
3. ✅ Pattern Matcher searches for similar past features
4. ✅ System breaks down feature into phases with tasks
5. ✅ Generates dependency graph and risk analysis
6. ✅ Creates markdown roadmap with acceptance criteria
7. ✅ Saves plan to Tier 1 + feature-plans/ directory
8. ✅ Plan is immediately executable via "start Phase X"

### FR-2.1.2: Plan Storage & Retrieval

**Priority:** High  
**Effort:** Low (3-5 days)

**Description:** Store feature plans in Tier 1 database and markdown files for future reference and execution.

**Acceptance Criteria:**
1. ✅ Plans stored in SQLite with metadata (name, status, phases)
2. ✅ Markdown files saved to `cortex-brain/feature-plans/`
3. ✅ Plans linked to conversations (traceability)
4. ✅ User can list all plans: "show my feature plans"
5. ✅ User can load plan: "continue dashboard auth feature"
6. ✅ Plans include timestamps (created, last updated, completed)

### FR-2.1.3: Pattern-Based Suggestions

**Priority:** Medium  
**Effort:** Medium (1-2 weeks)

**Description:** Leverage Pattern Matcher to suggest approaches based on successful past features.

**Acceptance Criteria:**
1. ✅ Pattern Matcher searches Tier 2 Knowledge Graph during planning
2. ✅ Finds similar features by keywords, technologies, patterns
3. ✅ Surfaces success metrics (completion time, quality scores)
4. ✅ Suggests proven approaches with references
5. ✅ Warns about past failures/pitfalls
6. ✅ User can accept/reject suggestions

### FR-2.1.4: Dependency & Risk Analysis

**Priority:** Medium  
**Effort:** Medium (1-2 weeks)

**Description:** Automatically identify technical dependencies and risks during planning.

**Acceptance Criteria:**
1. ✅ Detects dependencies between phases (Phase 2 requires Phase 1)
2. ✅ Identifies external dependencies (APIs, services, libraries)
3. ✅ Flags technical risks (new technology, complex integration)
4. ✅ Suggests mitigation strategies for each risk
5. ✅ Generates dependency diagram (text-based for MVP)
6. ✅ Updates plan as dependencies are resolved

### FR-2.1.5: Plan Execution Tracking

**Priority:** High  
**Effort:** Low (3-5 days)

**Description:** Track feature plan execution progress and update status automatically.

**Acceptance Criteria:**
1. ✅ Plan status: DRAFT → IN_PROGRESS → COMPLETED → ABANDONED
2. ✅ Phase status tracked independently (NOT_STARTED → IN_PROGRESS → DONE)
3. ✅ Daemon events auto-update phase status (file created → phase progress)
4. ✅ User can manually mark phases complete
5. ✅ "Continue" command resumes from last incomplete phase
6. ✅ Completion metrics stored for learning (time, quality, issues)

---

## 🗂️ Data Model

### Feature Plan Schema (Tier 1 Database)

```sql
CREATE TABLE feature_plans (
    plan_id TEXT PRIMARY KEY,
    conversation_id TEXT,  -- Link to originating conversation
    feature_name TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_phases INTEGER,
    completed_phases INTEGER DEFAULT 0,
    markdown_path TEXT,  -- Path to feature-plans/*.md file
    metadata JSON,  -- {tags, technologies, dependencies, risks}
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

CREATE TABLE feature_phases (
    phase_id TEXT PRIMARY KEY,
    plan_id TEXT,
    phase_number INTEGER,
    phase_name TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_days INTEGER,
    actual_days INTEGER,
    tasks JSON,  -- [{name, status, acceptance_criteria}]
    dependencies JSON,  -- [phase_id, phase_id]
    FOREIGN KEY (plan_id) REFERENCES feature_plans(plan_id)
);

CREATE TABLE feature_risks (
    risk_id TEXT PRIMARY KEY,
    plan_id TEXT,
    risk_type TEXT,  -- TECHNICAL, TIMELINE, DEPENDENCY, UNKNOWN
    description TEXT,
    severity TEXT CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    mitigation TEXT,
    status TEXT CHECK(status IN ('IDENTIFIED', 'MITIGATED', 'ACCEPTED', 'RESOLVED')),
    FOREIGN KEY (plan_id) REFERENCES feature_plans(plan_id)
);
```

### Markdown File Format

```markdown
# Feature Plan: Dashboard Authentication

**Status:** IN_PROGRESS  
**Created:** 2025-11-13  
**Updated:** 2025-11-13  
**Phases:** 4  
**Completed:** 1/4

---

## 📋 Overview

**Feature Name:** Dashboard Authentication  
**Description:** Add authentication to dashboard so only authorized users can access it

**Why:** Protect sensitive data from unauthorized access  
**Who:** End users  
**Constraints:** Must work with existing user service

---

## 🎯 Phases

### ☑ Phase 1: Authentication Core (COMPLETED)
**Status:** ✅ COMPLETED  
**Started:** 2025-11-13 10:00  
**Completed:** 2025-11-13 14:30  
**Estimated:** 3-5 days  
**Actual:** 0.5 days

**Tasks:**
- ✅ Integrate with user service API
- ✅ Implement login UI
- ✅ Add session management
- ✅ Create auth service layer

**Acceptance Criteria:**
- ✅ User can log in with valid credentials
- ✅ Sessions persist across refreshes
- ✅ Auth service handles errors gracefully

---

### ☐ Phase 2: Route Protection (IN_PROGRESS)
**Status:** 🔄 IN_PROGRESS  
**Started:** 2025-11-13 15:00  
**Estimated:** 2-3 days

**Tasks:**
- ✅ Add route guards
- 🔄 Implement redirect logic (current)
- ☐ Handle edge cases
- ☐ Add "Remember me"

**Dependencies:**
- Phase 1 (Authentication Core) ✅

**Acceptance Criteria:**
- ☐ All dashboard routes protected
- ☐ Unauthorized users redirect to login
- ☐ Sessions handle timeout gracefully

---

### ☐ Phase 3: Testing & Security (NOT_STARTED)
**Dependencies:**
- Phase 2 (Route Protection)

---

### ☐ Phase 4: Production Readiness (NOT_STARTED)
**Dependencies:**
- Phase 3 (Testing & Security)

---

## ⚠️ Risks

### Technical Risks

**MEDIUM: Session management conflicts**
- **Mitigation:** Use isolated auth state, test integration early
- **Status:** MITIGATED (implemented isolated state)

**HIGH: Breaking existing functionality**
- **Mitigation:** Feature flag for auth, gradual rollout
- **Status:** IDENTIFIED

---

## 📊 Pattern Insights

**Similar Features:**
- Admin Panel Auth (2024-08-15) - 100% success, 2 weeks
- User Profile Auth (2024-06-20) - 90% success, 3 weeks

**Lessons Learned:**
- Route guards easier than middleware for frontend
- JWT tokens better than session cookies for SPAs
- Test session timeout early (common bug)

---

## 📈 Progress

**Overall:** 25% complete (1/4 phases)  
**Current Phase:** Phase 2 - Route Protection (50% complete)  
**Next Milestone:** Complete Phase 2 by EOD 2025-11-15

---

*Generated by CORTEX 2.0 Work Planner*  
*Plan ID: plan-20251113-143022*  
*Conversation ID: conv-20251113-095530*
```

---

## 🚀 Implementation Plan

### Phase 1: Core Planning Workflow (Week 1-2)

**Tasks:**

1. **Enhance Work Planner Agent** (5 days)
   - Add interactive questioning logic
   - Implement requirement gathering prompts
   - Create phase breakdown algorithm
   - Add roadmap generation

2. **Integrate Pattern Matcher** (3 days)
   - Search Tier 2 for similar features
   - Extract success metrics
   - Format suggestions for Work Planner

3. **Storage Implementation** (2 days)
   - Create Tier 1 schema (feature_plans, feature_phases, feature_risks)
   - Implement markdown file generation
   - Add CRUD operations for plans

**Deliverables:**
- ✅ Interactive planning works end-to-end
- ✅ Plans stored in database + markdown
- ✅ Pattern-based suggestions working

### Phase 2: Execution Integration (Week 3)

**Tasks:**

1. **Plan Execution Tracking** (3 days)
   - Link Executor to feature plans
   - Update phase status on execution
   - Track completion metrics

2. **Daemon Integration** (2 days)
   - Ambient daemon updates phase progress
   - File creation → task completion detection
   - Auto-status updates based on events

**Deliverables:**
- ✅ "Start Phase X" executes with plan context
- ✅ Progress tracked automatically
- ✅ Daemon events update plan status

### Phase 3: Advanced Features (Week 4)

**Tasks:**

1. **Dependency Analysis** (2 days)
   - Detect phase dependencies
   - Identify external dependencies
   - Generate dependency visualization

2. **Risk Analysis** (2 days)
   - Identify technical risks automatically
   - Suggest mitigations
   - Track risk status

3. **Polish & Testing** (1 day)
   - UX improvements
   - Error handling
   - Documentation

**Deliverables:**
- ✅ Dependency tracking working
- ✅ Risk analysis integrated
- ✅ System production-ready

**Total Timeline:** 4 weeks

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Planning Time** | <5 minutes from idea to executable plan | User surveys |
| **Plan Quality** | 90% of plans include all required phases | Manual review |
| **Execution Success** | 85% of planned phases completed | Database metrics |
| **User Adoption** | 70% of features start with planning | Telemetry |
| **Pattern Reuse** | 50% of plans use past feature insights | Pattern Matcher logs |

---

## 🔧 Technical Considerations

### Work Planner Agent Enhancements

**Current Capabilities:**
- Task breakdown (basic)
- Dependency mapping (manual)
- Acceptance criteria generation (template-based)

**New Capabilities Needed:**
- Interactive questioning (conversational flow)
- Multi-turn discovery (handle clarifications)
- Pattern matching integration (Tier 2 search)
- Risk identification (heuristic-based)
- Roadmap formatting (markdown generation)

### Database Schema Changes

**New Tables:**
- `feature_plans` (plan metadata)
- `feature_phases` (phase breakdown)
- `feature_risks` (risk tracking)

**New Relationships:**
- Plans ↔ Conversations (traceability)
- Phases ↔ Daemon Events (execution proof)
- Plans ↔ Knowledge Graph (pattern learning)

### File System Structure

```
cortex-brain/
├── feature-plans/
│   ├── 2025-11-13-dashboard-auth.md
│   ├── 2025-11-10-cleanup-system.md
│   └── 2025-11-05-dual-channel-memory.md
```

---

## 📚 User Documentation

### Quick Start

**Planning a Feature:**

1. Say: "Let's plan a feature"
2. Answer CORTEX questions (what, why, who, constraints)
3. Review generated plan
4. Approve or adjust
5. Start execution: "Start Phase 1"

**Managing Plans:**

- List plans: "Show my feature plans"
- Continue plan: "Continue dashboard auth"
- Check progress: "What's the status of cleanup system?"
- Abandon plan: "Abandon dual-channel memory plan"

### Best Practices

**Good Planning Inputs:**
- Clear problem statement
- Defined scope (what's in/out)
- Known constraints (time, tech, compatibility)
- End user identified

**Bad Planning Inputs:**
- "Make it better" (too vague)
- "Do everything" (scope too large)
- No constraints (leads to over-engineering)

---

## 🎯 Next Steps

### Immediate

1. ☐ Approve this design document
2. ☐ Review Work Planner agent current code
3. ☐ Create Tier 1 schema migration script
4. ☐ Set up feature-plans/ directory

### Short-term (Week 1-2)

1. ☐ Implement interactive questioning in Work Planner
2. ☐ Add Pattern Matcher integration
3. ☐ Build storage layer (database + markdown)
4. ☐ Test with real features

### Medium-term (Week 3-4)

1. ☐ Integrate with Executor agent
2. ☐ Add daemon event tracking
3. ☐ Implement dependency and risk analysis
4. ☐ Polish and document

---

## ✅ Approval

**Design Reviewed By:** [Pending]  
**Approved By:** [Pending]  
**Approval Date:** [Pending]

**Next Action:** Present to stakeholder for approval and priority confirmation.

---

*Design Date: 2025-11-13*  
*CORTEX Version: 2.1.0*  
*Design Status: Awaiting Approval*  
*Estimated Timeline: 4 weeks*
