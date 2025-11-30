# CORTEX 3.3 Minor Upgrade - DoR Validation Questionnaire

**Feature:** CORTEX Next Minor Upgrade (v3.3.0)  
**Date:** 2025-11-28  
**Status:** DoR Validation In Progress

---

## Feature 1: SWAGGER Entry Point Module

### Q1: Information Sources & Crawling Strategy

**Question:** What specific information sources should SWAGGER crawl to gather estimation data?

**Options (check all that apply):**
- [X ] Codebase structure (file count, complexity metrics)
- [ X] Existing similar features (for comparison)
- [x] Documentation files (README, design docs)
- [x] Test coverage data
- [x] Git history (velocity, change patterns)
- [x] External dependencies (package.json, requirements.txt)
- [ ] Technical debt indicators
- [ ] Other: _________________________________

**Your Answer:**



---

### Q2: Integration with Planning System

**Question:** Should SWAGGER integrate with existing Planning System 2.0 or operate independently?

**Options:**
- [] **Integrate with Planning System 2.0** - Reuse DoR/DoD, security review, phase breakdown
- [ ] **Operate independently** - Separate lightweight workflow for quick estimates
- [x] **Hybrid approach** - Quick mode (independent) + Detailed mode (integrated)

**Your Answer:**



**If Integrated:** Which Planning System components to reuse?
- [x] DoR/DoD validation
- [x] Security review (OWASP)
- [x] Phase breakdown generation
- [x] Risk analysis
- [x] Dependency mapping
- [ ] Other: _________________________________

---

### Q3: Complexity Factors

**Question:** What factors should SWAGGER consider when calculating complexity?

**Options (check all that apply):**
ALL
- [ ] Technical debt score (from healthcheck)
- [ ] Unknown dependencies (new libraries/APIs)
- [ ] Technology stack unfamiliarity (team experience level)
- [ ] Integration points (number of services affected)
- [ ] Data model changes (schema migrations)
- [ ] UI/UX complexity (new components vs existing)
- [ ] Security requirements (authentication, encryption)
- [ ] Performance requirements (optimization needed)
- [ ] Testing complexity (unit, integration, E2E)
- [ ] Other: _________________________________

**Your Answer:**
ALL


**Weighting:** How should these factors be weighted? (1-10 scale)
- Technical debt impact: ___/10
- Unknown dependencies: ___/10
- Stack unfamiliarity: ___/10
- Integration complexity: ___/10
- Data model changes: ___/10

---

### Q4: Output Format & Confidence

**Question:** What format should SWAGGER use for sprint estimates?

**Options:**
- [ ] **Single number** - "3 sprints"
- [ ] **Range** - "3-5 sprints"
- [ ] **Confidence intervals** - "3 sprints ±20% confidence"
- [x] **Three-point estimate** - "Best: 2, Most Likely: 3, Worst: 5" **← RECOMMENDED** (Industry standard, captures uncertainty)
- [ ] **Story points + sprints** - "45 story points = 3 sprints @ 15 velocity"

**Your Answer:**
Three-point estimate selected (CORTEX recommendation accepted)



**Confidence Display:**
- [ ] Percentage (e.g., "75% confident")
- [x] Color-coded (🟢 High, 🟡 Medium, 🔴 Low)
- [ ] Qualitative (High/Medium/Low/Very Low)

---

### Q5: Acceptance Criteria for SWAGGER

**Question:** Review and modify proposed acceptance criteria:

**Proposed Criteria:**
1. SWAG generation completes in <30 seconds
2. Estimation accuracy within ±30% of actual (validated against historical data)
3. Integrates with existing ADO workflow (single command trigger)
4. Stores estimation history in Tier 3 for learning
5. Provides confidence score (0-100%) based on available information

**Your Modifications/Additions:**



---

### Q6: Dependencies & Historical Data

**Question:** How should SWAGGER handle missing historical data?

**Scenario:** New CORTEX installation with no past estimations

**Options:**
- [x] **Bootstrap with defaults** - Use industry averages (e.g., 2 weeks per feature)
- [ ] **User calibration** - Ask user for 2-3 past features + actual time
- [ ] **Team velocity only** - Base solely on team capacity + complexity score
- [x] **Gradual learning** - Start conservative, improve with each estimation

**Your Answer:**



---

### Q7: Security Considerations

**Question:** Are there additional security concerns for SWAGGER?

**Proposed Security Measures:**
- ✅ User can only access their own team's capacity data (A01 - Access Control)
- ✅ Profile data validation - team size must be positive integer (A07)
- ✅ Data privacy - stored locally, never transmitted

**Additional Concerns:**



---

## Feature 2: Enhanced User Profile (Team Capacity)

### Q8: Team Profile Fields

**Question:** Review and modify proposed team profile fields:

**Proposed Fields:**

| Field | Type | Default | Required |
|-------|------|---------|----------|
| Team Size | Integer (1-20) | None | Yes |
| Team Velocity | Real (story points/sprint) | Auto-calculate or user input | Yes |
| Sprint Length | Integer (days) | 14 (SAFe) | Yes |
| Methodology | Enum (SAFe, Scrum, Kanban, Scrumban) | SAFe | Yes |
| Capacity % | Integer (0-100) | 70% | Yes |
| Skill Matrix | JSON (optional) | None | No |

**Your Modifications:**



**Skill Matrix Format (if enabled):**
```json
{
  "frontend": 40,
  "backend": 40,
  "qa": 20
}
```
Should this be included? [ ] Yes [ ] No

---

### Q9: Profile Collection Timing

**Question:** When should team profile be collected?

**Options:**
- [ ] **During initial onboarding** - Add as questions 4-7 after tech stack
- [ ] **Separate command** - `setup team profile` or `configure team`
- [ ] **Lazy initialization** - Prompt when SWAGGER first used
- [x] **Hybrid** - Ask during onboarding with "skip for now" option **← RECOMMENDED** (Best UX, no blocking)

**Your Answer:**
Hybrid approach selected (CORTEX recommendation accepted)



**If Hybrid:** Onboarding flow would become:
1. Experience level (Junior/Mid/Senior/Expert)
2. Interaction mode (Autonomous/Guided/Educational/Pair)
3. Tech stack (Azure/AWS/GCP/None/Custom)
4. **NEW:** Team size
5. **NEW:** Sprint length
6. **NEW:** Methodology
7. **NEW:** Team velocity (or skip to auto-calculate)

**Acceptable? [ ] Yes [ ] No [ ] Modify (explain below)**



---

### Q10: Profile Update Mechanism

**Question:** How should team profile updates work?

**Options:**
- [x] **Integrated with existing** - `update profile` shows team section **← RECOMMENDED** (Consistency, easy to find)
- [ ] **Separate command** - `update team profile` for focused updates
- [x] **Auto-detect from ADO** - Read team velocity from historical sprints (if ADO integrated) **← RECOMMENDED** (Reduces manual entry)
- [ ] **All of the above** - Multiple update paths

**Your Answer:**
Integrated + Auto-detect selected (CORTEX recommendations accepted)



**Auto-calculation preference:**
- [x] Calculate velocity from last 3 sprints average **← RECOMMENDED** (Balance: recent + stable)
- [ ] Calculate velocity from last 6 sprints average
- [ ] Calculate velocity from last sprint only
- [ ] Manual entry only (no auto-calculation)

---

### Q11: Database Schema Extension

**Question:** Review proposed schema changes:

**Proposed SQL:**
```sql
ALTER TABLE cortex_user_profile ADD COLUMN team_size INTEGER;
ALTER TABLE cortex_user_profile ADD COLUMN team_velocity REAL;
ALTER TABLE cortex_user_profile ADD COLUMN sprint_length_days INTEGER DEFAULT 14;
ALTER TABLE cortex_user_profile ADD COLUMN methodology TEXT DEFAULT 'SAFe';
ALTER TABLE cortex_user_profile ADD COLUMN capacity_percentage INTEGER DEFAULT 70;
ALTER TABLE cortex_user_profile ADD COLUMN skill_matrix TEXT; -- JSON string
```

**Acceptable? [ ] Yes [ ] No**

**If No, explain modifications:**



---

## Feature 3: Questionnaire Orchestrator (NEW)

### Q12: Questionnaire Orchestrator Functionality

**Question:** What should the Questionnaire Orchestrator do?

**Proposed Capabilities:**
- [ ] Generate interactive questionnaires from planning templates
- [ ] Support multiple question types (single choice, multiple choice, text, scale)
- [ ] Validate responses (required fields, data types, ranges)
- [ ] Store responses in Tier 1 for DoR completion tracking
- [ ] Resume incomplete questionnaires
- [ ] Export/import questionnaires for team collaboration

**Your Answer:**



---

### Q13: Question Types Support

**Question:** Which question types should be supported?

**Options:**
- [x] Single choice (radio buttons) **← RECOMMENDED**
- [x] Multiple choice (checkboxes) **← RECOMMENDED**
- [x] Free text (short answer) **← RECOMMENDED**
- [x] Long text (paragraph) **← RECOMMENDED**
- [x] Scale (1-10 rating) **← RECOMMENDED**
- [x] Yes/No (boolean) **← RECOMMENDED**
- [ ] File upload (attach screenshots/docs) - Phase 2
- [ ] Date picker - Phase 2
- [ ] Other: _________________________________

**Your Answer:**
All 6 core types selected (CORTEX recommendations - sufficient for 95% of use cases)



---

### Q14: Integration with Planning System

**Question:** How should Questionnaire Orchestrator integrate with planning workflow?

**Proposed Flow:**
```
User: "plan [feature]"
↓
CORTEX: Detects feature type (authentication, API, UI, etc.)
↓
Questionnaire Orchestrator: Generates tailored questionnaire
↓
User: Fills out questionnaire (this file format)
↓
User: "import questionnaire responses"
↓
Planning Orchestrator: Validates DoR, generates plan
```

**Acceptable? [ ] Yes [ ] No [ ] Modify (explain below)**



---

### Q15: Questionnaire Storage & Format

**Question:** What format should questionnaires use?

**Options:**
- [ ] **Markdown (current)** - Human-readable, easy to edit
- [ ] **YAML** - Structured, machine-parseable
- [ ] **JSON** - Standard, easy to validate
- [ ] **Hybrid** - Markdown for display, YAML/JSON for parsing

**Your Answer:**



**Storage Location:**
- [ ] `cortex-brain/documents/planning/questionnaires/`
- [ ] `cortex-brain/questionnaires/`
- [ ] Other: _________________________________

---

## Feature 4: Entry Point Module Updates

### Q16: Affected Entry Point Modules

**Question:** Which orchestrators need updates to support these features?

**Identified Orchestrators:**
- [ ] `PlanningOrchestrator` - Integrate with Questionnaire Orchestrator
- [ ] `ADOWorkItemOrchestrator` - Add SWAGGER integration
- [ ] `SetupEPMOrchestrator` - Add team profile to onboarding
- [ ] `OnboardingOrchestrator` - Extend with team questions
- [ ] `ProfileOrchestrator` (NEW?) - Manage team profile CRUD
- [ ] `QuestionnaireOrchestrator` (NEW) - Generate/parse questionnaires

**Your Additions:**



---

## Implementation Preferences

### Q17: Development Approach

**Question:** Preferred implementation strategy?

**Options:**
- [x] **Incremental** - Implement features one at a time (SWAGGER → Profile → Questionnaire) **← RECOMMENDED** (Lower risk, steady progress)
- [ ] **Parallel** - Develop features simultaneously (faster, more risk)
- [ ] **MVP First** - Basic SWAGGER + minimal profile, iterate later
- [ ] **Full Featured** - Complete all features with all options

**Your Answer:**
Incremental selected (CORTEX recommendation - proven delivery method)



---

### Q18: Testing Strategy

**Question:** Testing requirements?

**Options:**
- [x] Unit tests (80%+ coverage) **← RECOMMENDED**
- [x] Integration tests (end-to-end workflows) **← RECOMMENDED**
- [ ] Manual testing (with test plan)
- [x] User acceptance testing (beta users) **← RECOMMENDED**
- [x] Performance testing (estimation speed) **← RECOMMENDED**

**Your Answer:**
Comprehensive strategy selected (CORTEX recommendations - TDD Mastery compliant)



---

## Priority & Timeline

### Q19: Feature Priority

**Question:** Rank features by priority (1 = highest):

- SWAGGER Entry Point: Priority **2** ← RECOMMENDED (High value, depends on Profile)
- Enhanced User Profile: Priority **1** ← RECOMMENDED (Foundation for SWAGGER)
- Questionnaire Orchestrator: Priority **3** ← RECOMMENDED (Supports future planning)
- Entry Point Updates: Priority **4** ← RECOMMENDED (Follows naturally)

---

### Q20: Target Release

**Question:** When should this ship?

**Options:**
- [x] **CORTEX 3.3.0** - Next minor version (6-9 weeks with git enhancements) **← RECOMMENDED** (Combined release)
- [ ] **CORTEX 3.4.0** - Future minor version (4-6 weeks)
- [ ] **CORTEX 4.0.0** - Major version (3+ months)
- [ ] **Incremental releases** - Ship features as ready

**Your Answer:**
CORTEX 3.3.0 selected (CORTEX recommendation - aligns with git enhancements timeline)



---

## Next Steps

**After completing this questionnaire:**

1. Save this file
2. Run: `import questionnaire responses` (when implemented)
3. CORTEX validates your answers
4. DoR completion verified
5. Comprehensive plan generated

**Current Status:** Awaiting your responses to questions Q1-Q20

---

**Instructions:**
- Fill in answers using [ ] checkboxes (replace [ ] with [x])
- Provide text responses in "Your Answer:" sections
- Add comments/clarifications as needed
- Save file when complete
- Notify CORTEX when ready for import
