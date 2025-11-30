# Sprint 1: Rulebook Visibility Enhancement

**Sprint Duration:** December 2-6, 2025 (1 week)  
**Sprint Goal:** Implement governance rulebook visibility at all CORTEX entry points  
**Priority:** HIGH (User awareness of governance system)  
**Status:** ≡ƒƒó ACTIVE

---

## ≡ƒôï Executive Summary

**Problem Statement:**
Users interact with CORTEX without knowing 27 governance rules exist. Brain protection operates invisibly, leading to confusion when operations are blocked. Need proactive rule visibility to build user trust and understanding.

**Solution:**
Implement 4-layer visibility strategy: welcome banner, help enhancement, first-time acknowledgment flow, and compliance dashboard integration.

**Success Metrics:**
- 100% users see rulebook reference on first interaction
- Help command includes dedicated rulebook section
- Compliance dashboard accessible via natural language
- Zero confusion about blocked operations (users know why)

---

## ≡ƒÄ» User Stories

### Story 1: Welcome Banner (Priority: CRITICAL)

**As a** CORTEX user  
**I want** to see rulebook information when I start  
**So that** I know governance rules exist and where to find them

**Acceptance Criteria:**
- [ ] Banner displays on first CORTEX interaction per session
- [ ] Contains link to THE-RULEBOOK.md with #file: syntax
- [ ] Shows rule count (27 rules) and purpose (brain protection)
- [ ] Dismissible (doesn't repeat within same session)
- [ ] Professional tone (informative, not overwhelming)

**Technical Tasks:**
- [ ] Create WelcomeBannerAgent in src/cortex_agents/
- [ ] Add session tracking to Tier 1 (banner_shown flag)
- [ ] Integrate with UnifiedEntryPointOrchestrator
- [ ] Add rulebook_welcome_banner template to response-templates.yaml
- [ ] Write unit tests (15 tests: display logic, session tracking, dismissal)

**Estimated Effort:** 4 hours

---

### Story 2: Help Command Enhancement (Priority: HIGH)

**As a** CORTEX user  
**I want** dedicated rulebook section in help command  
**So that** I can access governance rules anytime

**Acceptance Criteria:**
- [ ] Help command shows "≡ƒ¢í∩╕Å Governance & Rules" section
- [ ] Lists 5 quick commands: show rules, explain rule [name], my compliance, rulebook, show compliance
- [ ] Brief description of brain protection purpose
- [ ] Link to full rulebook documentation
- [ ] Integrated with existing help_table template

**Technical Tasks:**
- [ ] Update help_table template in response-templates.yaml
- [ ] Add governance section between "Core Operations" and "Admin Operations"
- [ ] Create rulebook command triggers (5 commands)
- [ ] Update HelpAgent to include governance section
- [ ] Write unit tests (10 tests: section display, command routing)

**Estimated Effort:** 3 hours

---

### Story 3: First-Time Acknowledgment (Priority: MEDIUM)

**As a** first-time CORTEX user  
**I want** acknowledgment flow explaining governance  
**So that** I understand rules before starting work

**Acceptance Criteria:**
- [ ] Triggers only for brand new users (no prior onboarding)
- [ ] Shows during onboarding flow (after profile setup)
- [ ] Displays 3-step governance intro:
  - Step 1: "What is the Rulebook?" (purpose explanation)
  - Step 2: "Key Principles" (TDD, brain protection, SOLID)
  - Step 3: "Quick Commands" (show rules, my compliance)
- [ ] User confirms "I acknowledge" before proceeding
- [ ] Stored in user profile (acknowledged_rulebook flag)

**Technical Tasks:**
- [ ] Extend OnboardingOrchestrator with governance step
- [ ] Add acknowledged_rulebook field to user_profile table
- [ ] Create 3-step governance intro template
- [ ] Add confirmation dialog with Yes/Learn More/Skip options
- [ ] Write unit tests (12 tests: flow logic, storage, skip handling)

**Estimated Effort:** 5 hours

---

### Story 4: Compliance Dashboard Integration (Priority: MEDIUM)

**As a** CORTEX user  
**I want** natural language access to compliance dashboard  
**So that** I can see my rulebook compliance anytime

**Acceptance Criteria:**
- [ ] Commands: "show compliance", "compliance dashboard", "my compliance"
- [ ] Opens compliance dashboard in VS Code Simple Browser
- [ ] Shows real-time rule compliance (27 rules with status)
- [ ] Displays recent protection events (last 10)
- [ ] Auto-refresh enabled (30-second interval)

**Technical Tasks:**
- [ ] Add compliance_dashboard_triggers to response-templates.yaml (3 triggers)
- [ ] Create ComplianceDashboardAgent in src/cortex_agents/
- [ ] Integrate with existing dashboard HTML generator (Tier 1)
- [ ] Add open_simple_browser tool integration
- [ ] Update compliance dashboard HTML with auto-refresh meta tag
- [ ] Write unit tests (8 tests: command routing, browser open, HTML validation)

**Estimated Effort:** 3 hours

---

## ≡ƒÅù∩╕Å Technical Architecture

### Component Structure

```
Sprint 1 Components:
Γö£ΓöÇΓöÇ WelcomeBannerAgent (NEW)
Γöé   Γö£ΓöÇΓöÇ Checks session state (Tier 1)
Γöé   Γö£ΓöÇΓöÇ Displays banner once per session
Γöé   ΓööΓöÇΓöÇ Provides rulebook link
Γö£ΓöÇΓöÇ HelpAgent (ENHANCED)
Γöé   Γö£ΓöÇΓöÇ Existing help functionality
Γöé   ΓööΓöÇΓöÇ + Governance section (5 commands)
Γö£ΓöÇΓöÇ OnboardingOrchestrator (ENHANCED)
Γöé   Γö£ΓöÇΓöÇ Existing profile setup (3 questions)
Γöé   ΓööΓöÇΓöÇ + Governance acknowledgment (3 steps)
Γö£ΓöÇΓöÇ ComplianceDashboardAgent (NEW)
Γöé   Γö£ΓöÇΓöÇ Fetches compliance data from Tier 1
Γöé   Γö£ΓöÇΓöÇ Opens dashboard in Simple Browser
Γöé   ΓööΓöÇΓöÇ Real-time refresh integration
ΓööΓöÇΓöÇ Response Templates (ENHANCED)
    Γö£ΓöÇΓöÇ rulebook_welcome_banner
    Γö£ΓöÇΓöÇ help_table (updated)
    Γö£ΓöÇΓöÇ onboarding_governance_intro
    ΓööΓöÇΓöÇ compliance_dashboard_triggers
```

### Data Flow

```
User: First CORTEX interaction
   Γåô
UnifiedEntryPointOrchestrator
   Γåô
WelcomeBannerAgent.should_display()
   Γö£ΓöÇ Check Tier 1 session state
   ΓööΓöÇ If first interaction ΓåÆ Display banner
   Γåô
User: "help"
   Γåô
HelpAgent.execute()
   Γö£ΓöÇ Load help_table template
   ΓööΓöÇ Include governance section
   Γåô
User: "show compliance"
   Γåô
ComplianceDashboardAgent.execute()
   Γö£ΓöÇ Fetch compliance from Tier 1
   Γö£ΓöÇ Generate dashboard HTML
   ΓööΓöÇ Open in Simple Browser
```

### Database Schema Changes

**Tier 1: working_memory.db**

```sql
-- Add to user_profile table (if not exists)
ALTER TABLE user_profile 
ADD COLUMN acknowledged_rulebook INTEGER DEFAULT 0;

-- Add session tracking table
CREATE TABLE IF NOT EXISTS session_state (
    session_id TEXT PRIMARY KEY,
    banner_shown INTEGER DEFAULT 0,
    started_at TEXT NOT NULL,
    last_activity TEXT NOT NULL
);
```

---

## ≡ƒôè Implementation Plan

### Phase 1: Welcome Banner (Day 1 - Monday)

**Morning (2 hours):**
- [ ] Create WelcomeBannerAgent class
- [ ] Implement session state tracking (Tier 1)
- [ ] Add rulebook_welcome_banner template

**Afternoon (2 hours):**
- [ ] Integrate with UnifiedEntryPointOrchestrator
- [ ] Write unit tests (15 tests)
- [ ] Manual testing (verify banner shows once per session)

**Deliverables:**
- WelcomeBannerAgent operational
- 15/15 tests passing
- Banner displays on first interaction

---

### Phase 2: Help Enhancement (Day 2 - Tuesday)

**Morning (1.5 hours):**
- [ ] Update help_table template with governance section
- [ ] Add 5 rulebook command triggers
- [ ] Update HelpAgent to include new section

**Afternoon (1.5 hours):**
- [ ] Write unit tests (10 tests)
- [ ] Integration test with existing help command
- [ ] Validate all 5 commands route correctly

**Deliverables:**
- Help command shows governance section
- 10/10 tests passing
- 5 commands functional

---

### Phase 3: First-Time Acknowledgment (Day 3-4 - Wednesday-Thursday)

**Day 3 Morning (2 hours):**
- [ ] Extend OnboardingOrchestrator with governance step
- [ ] Create 3-step governance intro template
- [ ] Add acknowledged_rulebook field to database

**Day 3 Afternoon (2 hours):**
- [ ] Implement confirmation dialog logic
- [ ] Handle Yes/Learn More/Skip options
- [ ] Store acknowledgment in user profile

**Day 4 Morning (1 hour):**
- [ ] Write unit tests (12 tests)
- [ ] End-to-end onboarding test (new user flow)

**Deliverables:**
- Onboarding includes governance step
- 12/12 tests passing
- User profile tracks acknowledgment

---

### Phase 4: Compliance Dashboard (Day 5 - Friday)

**Morning (1.5 hours):**
- [ ] Create ComplianceDashboardAgent
- [ ] Add compliance_dashboard_triggers (3 triggers)
- [ ] Integrate with Simple Browser tool

**Afternoon (1.5 hours):**
- [ ] Update compliance dashboard HTML (auto-refresh)
- [ ] Write unit tests (8 tests)
- [ ] Manual testing (verify dashboard opens, refreshes)

**Deliverables:**
- Compliance dashboard accessible via natural language
- 8/8 tests passing
- Auto-refresh working

---

## Γ£à Definition of Done (DoD)

**Code Quality:**
- [ ] All 45 unit tests passing (15+10+12+8)
- [ ] Code coverage ΓëÑ80% for new components
- [ ] Lint validation passing (no critical violations)
- [ ] Integration tests passing

**Documentation:**
- [ ] User-facing: Update CORTEX.prompt.md with new commands
- [ ] Developer-facing: Create sprint-1-implementation-guide.md
- [ ] API docs: Document WelcomeBannerAgent, ComplianceDashboardAgent
- [ ] Response templates: All 4 templates documented

**User Experience:**
- [ ] Banner displays correctly on first interaction
- [ ] Help command shows governance section clearly
- [ ] Onboarding flow intuitive (3 steps, <2 min)
- [ ] Compliance dashboard accessible via 3 natural commands

**System Health:**
- [ ] System alignment run after sprint (validate health)
- [ ] No regressions (all existing tests still pass)
- [ ] Performance acceptable (banner <100ms, dashboard <2s)

**Deployment:**
- [ ] All commits tagged with "sprint-1" label
- [ ] Change log updated
- [ ] Version bumped to 3.3.0 (if warranted)
- [ ] Sprint retrospective completed

---

## ≡ƒÄ» Success Metrics

**Quantitative:**
- 100% users see rulebook reference (banner tracking)
- 100% governance section in help (template validation)
- 100% new users acknowledge rulebook (profile tracking)
- 3 compliance dashboard commands operational

**Qualitative:**
- Zero confusion about blocked operations (user feedback)
- Positive sentiment on governance visibility (survey)
- Reduced support requests about "why was X blocked?"

**Technical:**
- 45/45 tests passing
- 0 critical lint violations
- 0 test regressions
- <5 min deployment time

---

## ≡ƒÜ¿ Risk Assessment

### Risk 1: User Overwhelm (MEDIUM)

**Description:** Welcome banner + onboarding step may feel like too much governance messaging

**Mitigation:**
- Make banner dismissible
- Onboarding step optional ("Skip" button)
- Tone: Informative, not preachy
- Keep messages <3 sentences

**Contingency:** If user feedback negative, make banner opt-out via profile setting

---

### Risk 2: Simple Browser Not Available (LOW)

**Description:** VS Code Simple Browser may not work in all environments

**Mitigation:**
- Fallback: Generate HTML file and provide file path
- Check Simple Browser availability before opening
- Graceful degradation message

**Contingency:** Create CLI-based compliance display (table format)

---

### Risk 3: Session Tracking Complexity (LOW)

**Description:** Session state tracking may have edge cases (crashes, restarts)

**Mitigation:**
- Use session ID (timestamp-based)
- Expire sessions after 4 hours of inactivity
- Clear session state on explicit logout

**Contingency:** Default to showing banner if session state unclear (better to over-show than miss)

---

## ≡ƒôà Sprint Schedule

| Day | Date | Focus | Deliverable |
|-----|------|-------|-------------|
| **Day 1** | Dec 2 (Mon) | Welcome Banner | WelcomeBannerAgent + 15 tests |
| **Day 2** | Dec 3 (Tue) | Help Enhancement | Governance section + 10 tests |
| **Day 3** | Dec 4 (Wed) | Acknowledgment (Part 1) | Onboarding extension + DB schema |
| **Day 4** | Dec 5 (Thu) | Acknowledgment (Part 2) | Confirmation flow + 12 tests |
| **Day 5** | Dec 6 (Fri) | Compliance Dashboard | ComplianceDashboardAgent + 8 tests |

**Total Estimated Hours:** 15 hours (3 hours/day ├ù 5 days)

---

## ≡ƒöä Next Steps

**Immediate Actions:**
1. Create feature branches: `feature/sprint-1-welcome-banner`, `feature/sprint-1-help-enhancement`, etc.
2. Set up sprint tracking in Option B plan (update current_sprint section)
3. Begin Day 1: WelcomeBannerAgent implementation

**Sprint Kickoff Checklist:**
- [x] Sprint plan created and reviewed
- [ ] Feature branches created
- [ ] Option B plan updated with Sprint 1 status
- [ ] Team notified (if applicable)
- [ ] Development environment ready

**Say "start day 1" or "implement welcome banner" to begin development.**

---

**Created:** 2025-11-28 18:30  
**Sprint Start:** 2025-12-02  
**Sprint End:** 2025-12-06  
**Author:** Asif Hussain  
**Status:** Ready for Implementation
