# 🎯 Interactive Planning Orchestrator v6.0 - Executive Summary

**Date:** 2026-01-09  
**Version:** 6.0.0 (Interactive Requirements-First Model)  
**Status:** ✅ DESIGN COMPLETE  
**Author:** Asif Hussain

---

## 🌟 Core Philosophy: Interactive → Zero Ambiguity → Autonomous

Planning Orchestrator v6.0 transforms planning from autonomous research into **collaborative requirements gathering** followed by **zero-ambiguity plan generation** and **autonomous execution**.

**Key Principle:** Work WITH user to achieve Definition of Ready (DoR) before generating detailed plans.

---

## 🔄 The 4-Phase Interactive Workflow

### **PHASE 1: Interactive Requirements Gathering (30-50% of time)**
**Mode:** INTERACTIVE - User collaboration required  
**Goal:** Achieve Definition of Ready (DoR) with zero assumptions

#### How It Works:

**1. Concise Introduction (When User Says "Plan")**

CORTEX presents a brief welcome message explaining:
- Planning orchestrator's role
- Interactive requirements gathering process
- Useful tips for providing context
- Expected outcome (zero-assumption requirements)

**2. Iterative Requirements Cycle**

The orchestrator enters an interactive loop that repeats until DoR is achieved:

**User Turn:**
- User describes work, requirements, constraints
- User provides context about what needs to be built

**CORTEX Turn:**
- **Analyzes context using CORTEX toolkit:**
  - Semantic Search: Find relevant code/docs in workspace
  - AST Parser: Parse files to understand code structure
  - Git History Analysis: Review commits and comments
  - Knowledge Graph Builder: Build entity-relationship graph
  - Pattern Detector: Identify reusable patterns
  - Dependency Mapper: Map dependencies and relationships

- **Explains understanding to user:**
  - What CORTEX discovered in codebase
  - Relevant patterns and components found
  - Assumptions made (to be validated)
  - Gaps or ambiguities identified
  - Questions to clarify requirements

- **Updates requirements incrementally:**
  - Saves draft to `requirements/requirements-draft-turn-{N}.yaml`
  - Builds knowledge graph incrementally

**Repeat Until DoR Achieved:**

Definition of Ready criteria:
- ✅ All user stories clearly defined
- ✅ Acceptance criteria specified
- ✅ Dependencies identified
- ✅ Constraints documented
- ✅ Assumptions validated (zero remaining)
- ✅ Technical approach agreed upon
- ✅ Risks identified and mitigated

**3. Requirements Approval Checkpoint**

Once DoR achieved:
- CORTEX presents final requirements summary
- Shows features, acceptance criteria, dependencies, risks
- Requests approval before generating detailed plan
- User can approve OR continue modifying requirements

**4. Complete Audit Trail**

Every interaction is logged:
- User inputs
- Tool analysis performed
- Understanding explanations
- Requirements updates
- DoR evaluation results
- Approval requests and responses

Saved to: `tracking/requirements-audit.jsonl` and `tracking/requirements-conversation.jsonl`

**5. Final Output: requirements.yaml**

Comprehensive YAML file capturing:
- User stories with acceptance criteria
- Features with dependencies
- Technical and business constraints
- Risks with mitigation strategies
- Discovered entities and reusable components
- Patterns identified during analysis

**NO MD FILES - Only structured YAML for autonomous consumption**

---

### **PHASE 2: Detailed Plan Generation (15-25% of time)**
**Mode:** AUTONOMOUS  
**Trigger:** After user approves requirements.yaml  
**Goal:** Convert requirements into zero-ambiguity execution plan

#### How It Works:

**1. Load Approved Requirements**
- Read `requirements/requirements.yaml`
- Validate DoR achieved flag is true

**2. Generate Feature Structure**

For each feature in requirements:
- Create `features/feat##-{name}/` folder
- Generate `feature.yaml` with metadata and phases list
- Create `context/{feature-name}-context.yaml` (NO MD files)
- Create `phases/` folder for phase files
- Create `tracking/progress-tracker.json`

**3. Generate Detailed Phase Files**

For each phase in each feature:
- Create `##-phase-{name-snake-case}.yaml` file
- Include **complete step-by-step instructions** for autonomous execution
- Specify objectives, deliverables, tasks, validation criteria
- Wire in dependencies and acceptance criteria references

**Zero ambiguity means:**
- Every phase has detailed instructions
- Every task has clear action steps
- Every deliverable has validation criteria
- No assumptions about implementation

**4. Generate Acceptance Criteria File**

Create `acceptance-criteria.yaml` per feature:
- Break down acceptance criteria from requirements
- Map criteria to specific phases
- Define validation methods (automated test, manual review, integration test)
- Set priority levels (must_have, should_have, nice_to_have)

**5. Add Refactor Phase (Automatically)**

For EVERY feature, add `99-phase-refactor.yaml` as the final phase:

**Purpose:** Holistic review of feature work

**Instructions include:**
- Review acceptance criteria (validate all met)
- Code quality review (check for smells, naming, error handling)
- Test coverage review (ensure critical paths tested)
- Documentation review (validate completeness)
- Identify refactoring opportunities (reduce duplication, improve readability)
- Final validation (run full test suite, check for regressions)

**Deliverables:**
- Refactor report (summary of improvements)
- Quality metrics (code quality scores, test coverage)

**6. Generate Master Plan File**

Create `{PLAN-ID}-{NAME}-MASTER-SOURCE-OF-TRUTH.yaml`:
- References requirements.yaml
- Lists all features with phase counts
- Records DoR achievement
- Includes governance settings

**7. Validate Plan Completeness**

Before presenting to user, validate:
- ✅ All phases have detailed instructions
- ✅ All acceptance criteria defined
- ✅ All dependencies mapped
- ✅ All deliverables specified
- ✅ Refactor phase added to all features
- ✅ NO MD files (only YAML/JSON)
- ✅ File naming conventions followed

If validation fails, pause and report missing elements.

**Output:**
- Complete plan folder structure
- All features and phases with zero ambiguity
- Acceptance criteria mapped to phases
- Refactor phases included
- Ready for autonomous execution

---

### **PHASE 3: Plan Approval for Autonomous Execution (Variable time)**
**Mode:** INTERACTIVE - User approval required  
**Goal:** Get user approval to begin autonomous execution

#### How It Works:

**1. Generate HTML Plan Viewer**

Create `plan-viewer.html` - interactive dashboard showing:
- Visual feature/phase structure
- Acceptance criteria checklist
- Dependency graph visualization
- Estimated timeline
- Risk summary

**2. Present Plan Summary**

Show user:
- Total features and phases
- Estimated effort (hours)
- Dependencies identified
- Acceptance criteria count
- Refactor phases included (one per feature)
- Zero ambiguity validation passed ✅

**3. Request Approval for Autonomous Execution**

Prompt: "Plan generation complete. Zero ambiguity validated. Review plan-viewer.html and approve to begin autonomous execution."

**4. Handle User Response**

**If user approves:**
- Record approval in master YAML
- Log approval event to audit trail
- Set execution mode to 'autonomous'
- Proceed to Phase 4

**If user requests modifications:**
- Stay in interactive mode
- User can request changes to plan structure
- Loop back to Phase 2 (regenerate affected parts)

**If user rejects:**
- Pause planning
- Document rejection reason
- Exit planning workflow

**Audit Trail:**
All approval interactions logged to `tracking/plan-approval-audit.jsonl`

---

### **PHASE 4: Autonomous Execution (50-70% of time)**
**Mode:** AUTONOMOUS - NO stopping unless error  
**Trigger:** After user approves autonomous execution  
**Goal:** Execute entire plan with zero human intervention

#### How It Works:

**Execution Loop: For Each Feature**

**1. Feature Introduction (3 lines max)**

Display to user:
```
## 🎯 Feature 01: OAuth2 Integration

Integrates OAuth2 authentication with JWT token management and session handling.
Reuses existing OAuth2Provider class and SecurityPolicy.

Phases: 4 | Estimated Time: 12h | Includes Refactor Phase
```

**2. Execute All Phases Sequentially**

**For Each Phase (Including Refactor Phase):**

**2.1. Phase Introduction (3 lines max)**
```
### ⚙️ Phase 01: OAuth2 Provider Setup

Configures OAuth2Provider with client credentials, redirect URIs, and token
expiration policies. Integrates with existing SecurityPolicy.
```

**2.2. Execute Phase Instructions (From YAML)**
- Read phase YAML file
- Follow step-by-step instructions sequentially
- Execute each task with validation
- Follow TDD workflow (RED→GREEN→REFACTOR) if enabled

**2.3. Validate Phase Completion**
- Check all deliverables created and validated
- Run tests (if TDD enabled)
- Verify acceptance criteria met (from acceptance-criteria.yaml)
- Validate phase-specific criteria

If validation fails:
- Pause and notify user
- Attempt automatic retry (up to 3 times)

If validation passes:
- Mark phase complete
- Proceed to next phase

**2.4. Special: Refactor Phase Execution**

When reaching `99-phase-refactor.yaml`:
- Conduct holistic review of all feature work
- Validate ALL acceptance criteria met
- Check code quality standards
- Verify test coverage adequate
- Review documentation completeness
- Implement refactoring improvements
- Run full feature test suite

**2.5. Update Progress**

After each phase:
```
## 📊 Progress Update

Feature: OAuth2 Integration (25%)
Phase: OAuth2 Provider Setup ✅ COMPLETED
Duration: 2.8h (Est: 3h)

Deliverables:
- ✅ OAuth2 configuration
- ✅ SecurityPolicy integration
- ✅ Unit tests (95% coverage)

Acceptance Criteria: 3/12 met
Next: Phase 02: JWT Token Manager
```

Update files:
- `features/feat##-{name}/tracking/progress-tracker.json`
- `tracking/progress-tracker.json` (epic-level)
- `tracking/execution-audit.jsonl`
- `plan-viewer.html` (auto-refreshes)

**3. Validate Feature Completion**

After all phases (including refactor):
- Run feature-level tests
- Check all acceptance criteria met
- Verify no regressions introduced
- Validate quality metrics

**4. Generate Feature Completion Report**

Create `reports/completion-reports/feat##-{name}-complete.yaml`:
- Feature completion date
- Phases completed count
- Acceptance criteria met (X/Y)
- Test coverage percentage
- Code quality score
- Maintainability index
- Refactoring improvements summary

**5. Move to Next Feature**

Repeat entire process for next feature until all features complete.

**NO STOPPING POLICY:**

Execution continues without user intervention EXCEPT:
- ❌ Validation failure after max retries
- ❌ Critical error encountered
- ❌ Governance rule violation detected

On exception: Pause and notify user with error details, retry attempts, and recommended resolution.

**User Experience:**
- Informational updates only (3-line intros, concise progress)
- NO code snippets in updates
- NO "Do you want to continue?" prompts
- HTML viewer shows real-time progress (polling every 5s)

---

## 🎯 Key Workflow Enhancements (Built-In)

### **1. Iterative Requirements Refinement**

Instead of autonomous research, CORTEX collaborates with user:
- User provides context → CORTEX analyzes → CORTEX explains → User clarifies
- Repeat until perfect understanding achieved
- Eliminates assumptions through validation cycle

### **2. Tool-Assisted Context Discovery**

During interactive cycle, CORTEX uses toolkit:
- AST parsing for code structure understanding
- Git history for project evolution context
- Semantic search for relevant component discovery
- Knowledge graph for relationship mapping

### **3. Zero-Assumption Requirements**

Definition of Ready ensures:
- Every requirement clearly stated
- Every constraint documented
- Every dependency identified
- Every risk assessed
- Technical approach agreed upon

### **4. Acceptance Criteria-Driven Development**

Requirements converted to acceptance criteria:
- Mapped to specific phases
- Validation methods defined
- Priority levels set
- Tracked throughout execution

### **5. Mandatory Refactor Phase**

Every feature gets automatic refactor phase:
- Holistic review of feature work
- Code quality validation
- Test coverage verification
- Documentation completeness check
- Refactoring for maintainability

### **6. Structured Data Only (NO MD Files)**

Governance policy enforced:
- Requirements: YAML format
- Features: YAML format
- Phases: YAML format
- Context: YAML format
- Acceptance criteria: YAML format
- Reports: YAML format

Why? Structured data enables autonomous consumption and validation.

### **7. Complete Audit Trail**

Every phase interaction logged:
- Phase 1: Requirements conversation (every turn)
- Phase 2: Plan generation (validation results)
- Phase 3: Approval workflow (user decisions)
- Phase 4: Execution (phase completion, validation results)

Format: JSONL (append-only for immutability)

### **8. HTML Viewer for Visual Clarity**

Interactive dashboard provides:
- Feature/phase structure visualization
- Progress bars (real-time updates)
- Acceptance criteria checklist
- Dependency graph
- Quality metrics display

---

## 📊 Example Complete Workflow

### **User Initiates Planning:**
```
User: "plan user authentication system"
```

### **Phase 1: Interactive Requirements (5-10 iterations)**

**Iteration 1:**
```
CORTEX: Welcome! Let's gather requirements for your plan.

Tips: Be specific, provide context, mention constraints.

What would you like to build? Please describe the authentication system requirements.
```

**User:** "OAuth2 authentication with JWT tokens, session management, user registration, password reset"

**CORTEX analyzes workspace:**
- Semantic search finds existing OAuth2Provider class
- AST parsing reveals session management patterns
- Git history shows security policy evolution
- Knowledge graph maps authentication components

**CORTEX responds:**
```
✅ Understanding Check - Turn 1

Discovered in workspace:
- ✨ OAuth2Provider class (src/auth/oauth2_provider.py) - can be reused
- ✨ SessionManager pattern (src/auth/session_manager.py) - established pattern
- ✨ SecurityPolicy (config/security_policy.yaml) - JWT requirements defined

Assumptions to validate:
- User registration includes email verification?
- Password reset via email or SMS?
- Session timeout duration?
- Token refresh strategy?

Requirements captured:
- OAuth2 authentication flow
- JWT token generation and validation
- Session management
- User registration workflow
- Password reset workflow

Please clarify the assumptions above.
```

**Iterations 2-5:** User clarifies, CORTEX updates requirements, asks follow-up questions

**Iteration 6:**
```
✅ Definition of Ready Achieved

Requirements complete:
- 3 features defined
- 12 user stories with acceptance criteria
- 8 dependencies identified
- 2 constraints documented
- 3 risks with mitigation
- Zero assumptions remaining

Review requirements.yaml and approve to generate detailed plan?
```

**User:** "Approve requirements"

### **Phase 2: Plan Generation (2-3 minutes)**

```
⚙️ Generating detailed plan from requirements...

Features Generated:
  ✅ feat01-oauth2-integration (4 phases + refactor)
  ✅ feat02-session-management (3 phases + refactor)
  ✅ feat03-user-workflows (4 phases + refactor)

Acceptance Criteria: 24 criteria mapped to phases
Refactor Phases: 3 (one per feature)
Zero Ambiguity Validation: ✅ PASSED

Plan location: cortex-brain/documents/planning/active/cx150-user-auth/
```

### **Phase 3: Plan Approval (User reviews)**

```
📊 Plan Summary:
- Features: 3
- Phases: 14 (including 3 refactor phases)
- Tasks: 42
- Estimated: 28 hours
- Acceptance Criteria: 24
- Zero Ambiguity: ✅ Validated

Review plan-viewer.html and approve to begin autonomous execution.
```

**User:** "Approve autonomous execution"

### **Phase 4: Autonomous Execution (28 hours)**

```
✅ Approval granted. Beginning autonomous execution...

## 🎯 Feature 01: OAuth2 Integration

Integrates OAuth2 authentication with JWT tokens and token refresh flow.
Reuses OAuth2Provider class and SecurityPolicy configuration.

Phases: 5 | Estimated: 12h | Includes Refactor Phase

---

### ⚙️ Phase 01: OAuth2 Provider Setup

Configures OAuth2Provider with client credentials, redirect URIs, and
token expiration policies from SecurityPolicy.

[Executes autonomously...]

📊 Progress Update
Feature: OAuth2 Integration (20%)
Phase: OAuth2 Provider Setup ✅ COMPLETED
Duration: 2.2h (Est: 2.5h)

Deliverables:
- ✅ OAuth2 configuration
- ✅ Provider integration
- ✅ Unit tests (96% coverage)

Acceptance Criteria: 2/8 met
Next: Phase 02: JWT Token Manager

[Continues through all phases autonomously...]

### ⚙️ Phase 99: Feature Refactor & Quality Review

Conducts holistic review of OAuth2 Integration feature work to ensure
best practices followed and all acceptance criteria met.

[Refactor phase executes...]

📊 Feature Complete
Feature: OAuth2 Integration ✅ COMPLETED
Phases: 5/5 (including refactor)
Duration: 11.5h (Est: 12h)
Test Coverage: 94%
Acceptance Criteria: 8/8 met ✅

Quality Metrics:
- Code Quality: 8.5/10
- Maintainability: 85/100
- Technical Debt: Low

Next: Feature 02: Session Management

[Continues through all features...]

🎉 Plan Execution Complete

All Features: ✅ COMPLETED (3/3)
Total Duration: 26.5h (Est: 28h)
Overall Test Coverage: 93%
Acceptance Criteria: 24/24 met ✅

📊 Full Report: reports/completion-reports/cx150-user-auth-complete.yaml
```

---

## ✅ Key Benefits of Interactive Workflow

### **For Users:**

1. **Collaborative Requirements** - Work WITH CORTEX to define requirements (not handed generic plan)
2. **Zero Assumptions** - Everything validated before plan generation
3. **Clear Understanding** - CORTEX explains what it discovered and understands
4. **Approval Control** - Two approval gates (requirements, then plan)
5. **Transparent Process** - See what CORTEX finds in codebase
6. **Context Preservation** - Full audit trail of requirements conversation

### **For CORTEX:**

1. **Better Context** - Deep understanding from user collaboration
2. **Accurate Plans** - Requirements-driven vs assumption-based
3. **Reusability Discovery** - Finds existing components during analysis
4. **Risk Identification** - Surfaces risks early in requirements phase
5. **Validation Framework** - Acceptance criteria defined upfront
6. **Quality Assurance** - Mandatory refactor phase per feature

### **For Execution:**

1. **Zero Ambiguity** - Complete instructions for autonomous execution
2. **Structured Data** - YAML/JSON only (no MD files) for machine consumption
3. **Acceptance-Driven** - Clear success criteria per phase
4. **Quality Gates** - Refactor phase ensures best practices
5. **Full Audit Trail** - Complete traceability from requirements to completion
6. **Real-Time Tracking** - HTML viewer shows live progress

---

## 📋 Workflow Comparison: Old vs New

| Aspect | v5.0 (Autonomous Research) | v6.0 (Interactive Requirements) |
|--------|---------------------------|--------------------------------|
| **Phase 1** | Autonomous codebase scan | Interactive user collaboration |
| **Requirements** | Inferred from request | Explicitly gathered and validated |
| **DoR** | Not enforced | Mandatory before plan generation |
| **Assumptions** | Many (no validation) | Zero (all validated with user) |
| **Context Discovery** | Autonomous | Tool-assisted with user validation |
| **Plan Quality** | Generic templates | Zero-ambiguity execution plans |
| **Acceptance Criteria** | Not defined upfront | Defined in Phase 1, mapped in Phase 2 |
| **Refactor Phase** | Optional | Mandatory per feature |
| **Audit Trail** | Partial | Complete (all 4 phases) |
| **File Format** | MD + YAML mix | YAML/JSON only (governance) |
| **Approval Gates** | 1 (plan approval) | 2 (requirements + plan approval) |

---

## 🎯 Summary: The Interactive Planning Journey

**Step 1:** User says "plan X" → CORTEX introduces interactive process

**Step 2:** Interactive cycle begins:
- User describes → CORTEX analyzes → CORTEX explains → User clarifies
- Repeat until Definition of Ready achieved

**Step 3:** User approves requirements → CORTEX generates zero-ambiguity plan

**Step 4:** User reviews plan → User approves autonomous execution

**Step 5:** CORTEX executes autonomously with informational updates only

**Result:**
- Better requirements (collaborative)
- Better plans (zero ambiguity)
- Better execution (acceptance-driven)
- Better quality (mandatory refactor)
- Better traceability (complete audit trail)

---

**The workflow ensures perfect understanding before autonomous execution begins.** 🚀

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Author:** Asif Hussain
