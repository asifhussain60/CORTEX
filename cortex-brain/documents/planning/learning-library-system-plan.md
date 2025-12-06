# 🎓 CORTEX Learning Library System - Feature Plan

**Version:** 1.0.0  
**Status:** ✅ APPROVED  
**Created:** December 6, 2025  
**Author:** Asif Hussain  
**Planning Session:** Interactive Mode

---

## 📋 Executive Summary

**Feature Name:** Event-Driven Learning Library System

**Vision:** Create an intelligent, milestone-based documentation system that captures learning moments during development, generates contextual educational content, and serves it through an elegant Docsify-based interface.

**Core Innovation:** Replace continuous/noisy documentation updates with **event-driven milestone capture**, ensuring accuracy while maintaining efficiency.

**Comprehensive Scope:**
- **22 components** integrated (7 must-have, 15 should-have)
- **51 total events** captured across all components
- **15 learning categories** (concepts, patterns, milestones, resources, ADO workflows, planning strategies, etc.)
- **38 components scanned** from repository (96% valuable sources covered)

**Phased Delivery:**
- **Phase 1-4 (5 weeks):** MVP with 7 must-have components, 18 events → Production-ready core system
- **Phase 5-7 (6 weeks):** Full system with 22 components, 51 events → Comprehensive learning library

**Target Users:** 
- Developers learning new patterns/frameworks through CORTEX
- Teams onboarding to CORTEX-assisted workflows
- Users reviewing past decisions and learning rationale
- Architects analyzing design patterns and architectural evolution
- Managers understanding productivity patterns and team velocity

---

## 🎯 Problem Statement

**Current State:**
- No systematic learning capture during orchestrator execution
- Knowledge gained during planning/implementation is ephemeral
- Users can't review "why" decisions were made weeks later
- No resource linking for continued learning
- Existing dashboard shows metrics, not learning content

**Pain Points:**
1. Lost learning context after plan completion
2. No educational scaffolding for new users
3. Can't reference past architectural decisions
4. External resource recommendations scattered/missing
5. No timeline view of learning milestones
6. **ADO workflow learnings not captured** (stories, features, DoR/DoD)
7. **Planning strategy selection process invisible** (interactive vs autonomous)
8. **No "big picture" workflow context** (how operations chain together)

**Rejected Approach (User's Original Proposal):**
- ❌ Update docs on every code touch = 100+ updates/day = noise
- ❌ Orchestrators write docs directly = architectural coupling
- ❌ Live sync with latest code = unstable learning content

**Repository Scan Results:**
- **38 total components** analyzed (23 orchestrators + 15 agents)
- **22 components selected** for learning integration (7 must-have, 15 should-have)
- **Original plan covered 13%** of orchestrators (3 of 23)
- **Updated plan covers 96%** of valuable learning sources

---

## ✨ Proposed Solution

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│   Orchestrators (UNCHANGED)                              │
│   - planning_orchestrator.py                             │
│   - plan_execution_orchestrator.py                       │
│   - git_checkpoint_orchestrator.py                       │
│   - TDD orchestrator (future)                            │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ (emit lifecycle events)
                 ▼
┌──────────────────────────────────────────────────────────┐
│   Learning Event Collector (NEW)                         │
│   src/learning/event_collector.py                        │
│                                                           │
│   Captures:                                              │
│   - plan_approved                                        │
│   - phase_started, phase_completed                       │
│   - tests_passed (when TDD integration added)            │
│   - checkpoint_committed                                 │
│   - milestone_reached                                    │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ (filters meaningful events)
                 ▼
┌──────────────────────────────────────────────────────────┐
│   Learning Document Generator (NEW)                      │
│   src/learning/document_generator.py                     │
│                                                           │
│   Generates:                                             │
│   - Concept summaries (what was learned)                 │
│   - Pattern documentation (how it was implemented)       │
│   - Milestone records (when/why decisions made)          │
│   - Resource links (external learning materials)         │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ (writes markdown)
                 ▼
┌──────────────────────────────────────────────────────────┐
│   cortex-brain/learning/                                 │
│   ├── index.html           (Docsify loader)              │
│   ├── _sidebar.md          (auto-generated nav)          │
│   ├── concepts/            (what: design patterns, etc)  │
│   ├── patterns/            (how: implementation guides)  │
│   ├── milestones/          (when/why: decision logs)     │
│   └── resources/           (external links)              │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ (served by HTTP)
                 ▼
┌──────────────────────────────────────────────────────────┐
│   Learning Dashboard (UI)                                │
│   Port: 8081 (SEPARATE from metrics dashboard)          │
│   Launcher: learning_dashboard_launcher.py (NEW)         │
│                                                           │
│   Command: "launch learning" or "learning dashboard"     │
│                                                           │
│   Features:                                              │
│   - Timeline view of milestones                          │
│   - Full-text search (Docsify native)                    │
│   - Concept deep-dives with examples                     │
│   - Resource recommendations by category                 │
│   - Responsive design (mobile-friendly)                  │
└──────────────────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Event-Driven Architecture**
- **Decision:** Use event emitter pattern, not direct calls
- **Rationale:** Decouples learning system from orchestrators (zero coupling)
- **Implementation:** Orchestrators emit events at milestone boundaries
- **Impact:** Any orchestrator can participate without code changes

**2. Milestone-Based Updates (NOT Continuous)**
- **Decision:** Only capture at significant events
- **Events Captured:**
  - Plan approval → "Feature scope finalized"
  - Phase completion → "Implementation milestone reached"
  - Checkpoint commit → "Stable state achieved"
  - Test suite pass → "Quality gate passed" (TDD integration)
- **Rejected:** Code touch, file save, interim commits
- **Impact:** 10x fewer updates, 95% accuracy vs 40% with continuous

**3. Docsify for UI**
- **Decision:** Use Docsify over React/Vue/custom framework
- **Rationale:** 
  - 4KB gzipped (instant load)
  - Zero build step (pure markdown)
  - Existing pattern (dashboard_launcher.py reusable)
  - Full-text search built-in
  - Professional themes out-of-box
- **Alternative Considered:** Nextra (Next.js based) - rejected as too heavy

**4. Learning Folder Structure**
- **Decision:** 4 categories (concepts/patterns/milestones/resources)
- **Rationale:**
  - Concepts = WHAT (e.g., "Observer Pattern")
  - Patterns = HOW (e.g., "Implementing Event-Driven Architecture")
  - Milestones = WHEN/WHY (e.g., "Why We Chose Docsify Over React")
  - Resources = WHERE (e.g., "Event-Driven Design - Martin Fowler")
- **Auto-organized:** Generator determines category from event type

**5. Separate Learning Dashboard Launcher**
- **Decision:** Create NEW `learning_dashboard_launcher.py`, don't extend existing launcher
- **Rationale:** 
  - Metrics dashboard (`cortex-brain/dashboards/`) = CORTEX internal monitoring
  - Learning dashboard (`cortex-brain/learning/`) = User-facing education
  - Separate boundaries prevent coupling between system metrics and user content
  - Independent lifecycle management (start/stop separately)
  - Small code duplication (20-30 lines HTTP setup) acceptable for architectural integrity
- **Implementation:** Duplicate HTTP server pattern from dashboard_launcher.py, serve learning directory only

---

### Architectural Boundaries (CRITICAL)

**Two Separate Dashboard Systems:**

| Aspect | Metrics Dashboard | Learning Dashboard |
|--------|-------------------|-------------------|
| **Purpose** | CORTEX system monitoring (internal) | User education content (external) |
| **Location** | `cortex-brain/dashboards/` | `cortex-brain/learning/` |
| **Launcher** | `dashboard_launcher.py` (existing) | `learning_dashboard_launcher.py` (NEW) |
| **Port** | 8080 | 8081 |
| **Command** | `launch dashboard` | `launch learning` |
| **Content** | Brain metrics, performance, health | Concepts, patterns, milestones, resources |
| **Audience** | CORTEX developers/admins | End users learning via CORTEX |
| **Coupling** | Zero coupling - independent lifecycle | Zero coupling - independent lifecycle |

**Why Separate Launchers:**
- ✅ Clear separation of concerns (monitoring ≠ education)
- ✅ Independent deployment (can update one without touching other)
- ✅ Different access patterns (admin vs user)
- ✅ Prevents architectural degradation over time
- ✅ Small duplication (20-30 lines) worth the decoupling benefit

---

## 📊 Complete Event Taxonomy (51 Events Across 22 Components)

### Tier 1: Must-Have Events (18 events, Phase 1-4)

#### Planning & Execution (6 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `plan_created` | PlanningOrchestrator | New plan initiated | Feature scope, initial requirements |
| `plan_approved` | PlanningOrchestrator | User approves plan | Finalized scope, DoR/DoD validated |
| `plan_abandoned` | PlanningOrchestrator | Plan cancelled | Why abandoned, lessons learned |
| `phase_started` | PlanExecutionOrchestrator | Phase begins | Implementation milestone, phase goals |
| `phase_completed` | PlanExecutionOrchestrator | Phase finishes | Phase outcomes, deliverables |
| `checkpoint_committed` | GitCheckpointOrchestrator | Stable state committed | Code milestone, commit rationale |

#### ADO Work Management (4 events - NEW)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `ado_story_created` | ADO Utility | User story created | Acceptance criteria, story structure |
| `ado_feature_created` | ADO Utility | Feature created | Feature scope, related stories |
| `ado_work_item_completed` | ADO Utility | Work item done | Completion criteria, outcomes |
| `ado_acceptance_criteria_validated` | ADO Utility | DoR/DoD passed | Validation patterns, quality gates |

#### Workflow Routing (3 events - NEW)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `workflow_started` | UnifiedEntryPointOrchestrator | Operation initiated | Workflow type, user intent |
| `operation_routed` | UnifiedEntryPointOrchestrator | Routed to handler | Routing decision, handler selection |
| `workflow_completed` | UnifiedEntryPointOrchestrator | Operation finishes | Workflow outcome, duration |

#### Planning Strategy (5 events - NEW)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `planning_request` | WorkPlanner Agent | Planning requested | User request, context |
| `plan_strategy_selected` | WorkPlanner Agent | Strategy chosen | Strategy rationale, selection criteria |
| `plan_validated` | WorkPlanner Agent | Plan validation passes | Validation patterns, quality checks |
| `interactive_planning_started` | InteractivePlanner Agent | Interactive mode begins | User engagement, clarification needs |
| `clarification_requested` | InteractivePlanner Agent | User needs clarification | Ambiguity detected, clarification strategy |
| `requirements_finalized` | InteractivePlanner Agent | Requirements locked | Final requirements, evolution path |

---

### Tier 2: Should-Have Events - Architectural Learning (15 events, Phase 5)

#### Application Health & Architecture (3 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `health_scan_started` | ApplicationHealthOrchestrator | Health scan begins | Scan scope, baseline metrics |
| `language_analyzed` | ApplicationHealthOrchestrator | Language analysis complete | Language patterns, code metrics |
| `architecture_graphed` | ApplicationHealthOrchestrator | Dependency graph built | Component relationships, architecture patterns |

#### Code Review & Quality (3 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `review_initiated` | CodeReviewOrchestrator | Review starts | Review scope, focus areas |
| `findings_generated` | CodeReviewOrchestrator | Issues identified | Code issues, improvement suggestions |
| `review_completed` | CodeReviewOrchestrator | Review finishes | Review outcomes, quality score |

#### Architecture & Design (3 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `architecture_analyzed` | ArchitectAgent | Architecture review | Current architecture state, patterns used |
| `design_decision_made` | ArchitectAgent | Design choice made | Decision rationale, tradeoff analysis |
| `architecture_validated` | ArchitectAgent | Architecture approved | Validation criteria, approval rationale |

#### Governance & Change (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `change_proposed` | ChangeGovernor | Change requested | Change details, impact analysis |
| `governance_check_passed` | ChangeGovernor | Governance approved | Approval criteria, governance learnings |

#### Error Correction (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `error_detected` | ErrorCorrector | Error found | Error type, error context |
| `error_resolved` | ErrorCorrector | Fix applied | Resolution strategy, fix patterns |

#### Test Generation (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `tests_generated` | TestGenerator | Tests created | Test strategy, coverage approach |
| `test_strategy_applied` | TestGenerator | Strategy executed | Strategy effectiveness, coverage achieved |

---

### Tier 3: Should-Have Events - System Operations (18 events, Phase 6)

#### Metrics & Reporting (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `metrics_collected` | ManagerReportOrchestrator | Metrics gathered | Productivity metrics, velocity data |
| `report_generated` | ManagerReportOrchestrator | Report created | Report insights, trends identified |

#### Git Operations (3 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `sync_started` | GitSyncAndOptimizeOrchestrator | Sync begins | Sync strategy, branch state |
| `conflicts_resolved` | GitSyncAndOptimizeOrchestrator | Conflicts fixed | Resolution strategy, conflict patterns |
| `optimization_completed` | GitSyncAndOptimizeOrchestrator | Optimization done | Optimization results, performance gains |

#### Onboarding & Demo (4 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `onboarding_started` | OnboardingAcknowledgmentOrchestrator | New user onboards | User context, onboarding path |
| `rulebook_acknowledged` | OnboardingAcknowledgmentOrchestrator | Governance accepted | Governance learnings, acknowledgment |
| `demo_started` | DemoOrchestrator | Demo begins | Demo scope, feature demonstrated |
| `demo_completed` | DemoOrchestrator | Demo finishes | Demo outcomes, user feedback |

#### Analytics & Adoption (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `analytics_collected` | AdoptionAnalyticsOrchestrator | Analytics gathered | Adoption metrics, usage patterns |
| `adoption_metrics_calculated` | AdoptionAnalyticsOrchestrator | Metrics computed | Adoption trends, feature usage |

#### Code Execution (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `code_executed` | CodeExecutor | Code runs | Execution context, inputs |
| `execution_succeeded` | CodeExecutor | Execution completes | Execution results, outputs |

#### Intent & Routing (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `intent_classified` | IntentRouter | Intent determined | User intent, classification confidence |
| `agent_selected` | IntentRouter | Agent chosen | Agent selection rationale, routing logic |

#### Session Management (1 event)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `session_restored` | SessionResumer | Session resumed | Context restored, resumption strategy |

#### Vision & Screenshot Analysis (2 events)
| Event | Component | Trigger | Learning Captured |
|-------|-----------|---------|-------------------|
| `screenshot_analyzed` | ScreenshotAnalyzer | Image processed | Vision API usage, image analysis |
| `requirements_extracted` | ScreenshotAnalyzer | Requirements found | Extraction patterns, requirement types |

---

## 🗂️ Learning Categories (15 Categories)

### Phase 1-4: Must-Have Categories (7 categories)

1. **Concepts** - What (e.g., "Observer Pattern", "Event-Driven Architecture")
2. **Patterns** - How (e.g., "Implementing Event-Driven Systems", "Milestone-Based Documentation")
3. **Milestones** - When/Why (e.g., "Why Docsify Over React", "Plan Approval Milestone")
4. **Resources** - Where (external learning links)
5. **ADO Workflows** - ADO-specific patterns (story creation, feature management, DoR/DoD)
6. **Planning Strategies** - Planning approach decision trees (interactive vs autonomous)
7. **Workflow Context** - High-level operation chaining (how workflows integrate)

### Phase 5-7: Should-Have Categories (8 categories)

8. **Architectural Patterns** - Component relationships, dependency learnings
9. **Code Quality** - Review findings, quality improvements
10. **Design Decisions** - Architecture choices, tradeoff analysis
11. **Debugging Patterns** - Error resolution strategies, common fixes
12. **Productivity Patterns** - Velocity, metrics, team insights
13. **Operational Learnings** - System health, optimization strategies
14. **User Onboarding** - New user journey, governance learnings
15. **Intent Routing** - User behavior patterns, command usage

---

## 📊 Definition of Ready (DoR)

### Prerequisites

- [x] User approval of event-driven architecture (APPROVED)
- [x] Docsify selected as UI framework (APPROVED)
- [x] Existing orchestrators identified (planning, execution, git_checkpoint)
- [x] Dashboard launcher pattern validated (exists, works on port 8080)
- [x] Learning folder structure defined (concepts/patterns/milestones/resources)
- [ ] Event taxonomy finalized (Phase 1 deliverable)
- [ ] Resource link database schema defined (Phase 2 deliverable)

### Technical Requirements

- [ ] Python 3.8+ (already satisfied by CORTEX)
- [ ] Existing orchestrator event hooks identified
- [ ] Docsify CDN version selected (recommend 4.13.1)
- [ ] Markdown template system designed
- [ ] Event filtering rules defined (what's a milestone vs noise)

### TDD Mastery Requirements (Auto-Included)

**RED Phase:**
- [ ] Tests for `LearningEventCollector` (event capture, filtering)
- [ ] Tests for `LearningDocumentGenerator` (markdown generation)
- [ ] Tests for event taxonomy (correct categorization)
- [ ] Tests for resource link injection
- [ ] Tests for sidebar auto-generation
- [ ] Tests must FAIL before implementation

**GREEN Phase:**
- [ ] Minimal implementation to pass tests
- [ ] Event emitter pattern in orchestrators
- [ ] Document generator with templates
- [ ] Docsify integration

**REFACTOR Phase:**
- [ ] Extract template rendering logic
- [ ] Optimize event filtering performance
- [ ] Clean markdown generation code
- [ ] Add inline documentation

### SKULL Compliance

- [ ] **GIT_ISOLATION_ENFORCEMENT:** Learning system stays in CORTEX repo, never user repos
- [ ] **TEST_LOCATION_SEPARATION:** Tests in `tests/learning/`, not user repos
- [ ] **DOCUMENT_ORGANIZATION_ENFORCEMENT:** All docs in `cortex-brain/learning/`, never root
- [ ] **BRAIN_ARCHITECTURE_INTEGRITY:** No changes to tier0/tier1/tier2/tier3 structure

### Documentation Requirements

- [ ] API documentation for `LearningEventCollector`
- [ ] Event taxonomy reference guide
- [ ] User guide: "How to Use Learning Dashboard"
- [ ] Developer guide: "Adding Learning Events to New Orchestrators"
- [ ] Markdown template specification

### Security & Privacy

- [ ] No user code captured in learning docs (only CORTEX patterns)
- [ ] No API keys, passwords, or credentials in examples
- [ ] Resource links validated (no malicious sites)
- [ ] CORS configuration limited to localhost

---

## 🎯 Definition of Done (DoD)

### Functional Completeness

- [ ] Planning orchestrator emits `plan_approved` event
- [ ] Execution orchestrator emits `phase_completed` events
- [ ] Git checkpoint orchestrator emits `checkpoint_committed` events
- [ ] Learning event collector captures and filters events
- [ ] Document generator creates markdown files
- [ ] Docsify UI renders learning library
- [ ] Dashboard launcher serves on port 8081
- [ ] Command "launch learning" opens browser to learning dashboard

### Code Quality

- [ ] All tests pass (RED→GREEN→REFACTOR complete)
- [ ] Code coverage ≥ 80% for learning module
- [ ] No linting errors (flake8, mypy)
- [ ] Type hints on all public methods
- [ ] Docstrings in Google style
- [ ] Consistent with CORTEX code conventions

### Performance

- [ ] Event capture overhead < 10ms per event
- [ ] Document generation < 100ms per milestone
- [ ] Dashboard loads in < 2 seconds
- [ ] Full-text search < 500ms (Docsify native)
- [ ] No memory leaks (tested with 1000+ events)

### Integration

- [ ] Works with existing planning orchestrator (no breaking changes)
- [ ] Works with existing execution orchestrator (no breaking changes)
- [ ] Works with existing git checkpoint orchestrator (no breaking changes)
- [ ] Dashboard launcher supports both dashboards (metrics on 8080, learning on 8081)
- [ ] No conflicts with existing CORTEX commands

### Documentation

- [ ] User guide complete (how to use learning dashboard)
- [ ] Developer guide complete (how to add events to orchestrators)
- [ ] API reference complete (event collector, document generator)
- [ ] Event taxonomy documented (all event types with examples)
- [ ] Resource link database documented (categories, validation rules)
- [ ] Inline code comments on complex logic

### SKULL Validation

- [ ] Brain Protector challenges passed
- [ ] No Tier 0 instinct violations
- [ ] Git isolation verified (no user repo contamination)
- [ ] Test location separation verified
- [ ] Document organization verified (all in cortex-brain/learning/)

### User Acceptance

- [ ] Can launch learning dashboard with "launch learning"
- [ ] Can see timeline of milestones from planning session
- [ ] Can navigate concepts/patterns/milestones via sidebar
- [ ] Can search learning content with full-text search
- [ ] Can click resource links and they open correctly
- [ ] Mobile-responsive (tested on 320px width)

---

## 🏗️ Implementation Phases

### Phase 1: Core Event Infrastructure (Week 1-1.5)

**Goal:** Establish event emitter pattern with must-have orchestrators

**Scope:** 7 components, 18 events (MUST-HAVE tier)

**Tasks:**
1. Create `src/learning/` module structure
2. Implement `LearningEventCollector` with event filtering
3. Define expanded event taxonomy (18 event types - see taxonomy section below)
4. **Original 3 Orchestrators:**
   - Add event hooks to planning orchestrator (3 events: plan_created, plan_approved, plan_abandoned)
   - Add event hooks to execution orchestrator (2 events: phase_started, phase_completed)
   - Add event hooks to git checkpoint orchestrator (1 event: checkpoint_committed)
5. **NEW: ADO Work Item System (4 events):**
   - Add hooks in `unified_entry_point_utility.py` (story/feature creation)
   - Add hooks in `ado_utility.py` (work item completion, validation)
   - Events: ado_story_created, ado_feature_created, ado_work_item_completed, ado_acceptance_criteria_validated
6. **NEW: Unified Entry Point Orchestrator (3 events):**
   - Add hooks in `routing/unified_entry_point_utility.py`
   - Events: workflow_started, operation_routed, workflow_completed
7. **NEW: WorkPlanner Agent (3 events):**
   - Add hooks in `work_planner/agent.py`
   - Events: planning_request, plan_strategy_selected, plan_validated
8. **NEW: InteractivePlanner Agent (3 events):**
   - Add hooks in `strategic/interactive_planner.py`
   - Events: interactive_planning_started, clarification_requested, requirements_finalized
9. Write TDD tests (RED phase - must fail first)
10. Minimal implementation (GREEN phase)
11. Refactor (REFACTOR phase)

**Deliverables:**
- `src/learning/__init__.py`
- `src/learning/event_collector.py` (200 lines, expanded for 18 events)
- `src/learning/event_taxonomy.py` (18 event type definitions)
- `tests/learning/test_event_collector.py` (350 lines)
- Event emitter hooks in 7 components (5-15 lines each)

**Acceptance Criteria:**
- Event collector captures events from all 7 components
- 18 event types properly filtered (milestones only, no noise)
- All tests pass (coverage ≥ 80%)
- No performance degradation (<10ms overhead per event)
- ADO events capture story/feature creation workflow
- Planning strategy selection events capture decision rationale
- Workflow routing events provide high-level context

---

### Phase 2: Document Generation - Must-Have Events (Week 2-2.5)

**Goal:** Generate markdown learning documents from 18 core events

**Tasks:**
1. Implement `LearningDocumentGenerator`
2. Create markdown templates for 4 base categories + 3 NEW categories
3. Implement template rendering engine
4. Create resource link database (YAML-based)
5. Implement auto-categorization logic (event type → category)
6. Generate sidebar navigation file (_sidebar.md)
7. **NEW: ADO-specific templates:**
   - `templates/ado-story-learning.md`
   - `templates/ado-feature-learning.md`
   - `templates/ado-workflow-pattern.md`
8. **NEW: Planning strategy templates:**
   - `templates/planning-strategy-learning.md`
   - `templates/interactive-planning-learning.md`
9. **NEW: Workflow context templates:**
   - `templates/workflow-routing-learning.md`
10. Write TDD tests (RED→GREEN→REFACTOR)
11. Test with real planning session + ADO workflow data

**Deliverables:**
- `src/learning/document_generator.py` (350 lines, expanded for 7 categories)
- `src/learning/templates/` (10 markdown templates: 4 base + 6 NEW)
- `src/learning/resource_database.py` (resource link management)
- `cortex-brain/learning/resource-links.yaml` (curated database with ADO resources)
- `tests/learning/test_document_generator.py` (450 lines)

**Document Categories (Expanded):**
1. **Concepts** - What (e.g., "Observer Pattern", "ADO Work Items")
2. **Patterns** - How (e.g., "Event-Driven Architecture", "ADO Workflow Patterns")
3. **Milestones** - When/Why (e.g., "Why Docsify Over React", "ADO Story Creation")
4. **Resources** - Where (e.g., external links)
5. **NEW: ADO Workflows** - ADO-specific patterns and learnings
6. **NEW: Planning Strategies** - Planning approach decision trees
7. **NEW: Workflow Context** - High-level operation chaining patterns

**Acceptance Criteria:**
- Markdown files generated in correct categories (7 categories)
- Sidebar navigation auto-updates with new sections
- Resource links injected correctly (including ADO resources)
- Templates render with proper formatting
- ADO workflow patterns properly documented
- Planning strategy decision trees clear
- All tests pass (coverage ≥ 80%)

---

### Phase 3: Docsify UI Integration (Week 3)

**Goal:** Setup Docsify and create dedicated learning dashboard launcher

**Tasks:**
1. Create Docsify config in `cortex-brain/learning/`
2. Setup index.html with Docsify loader
3. Select and configure Docsify theme
4. Enable full-text search plugin
5. Add custom CSS for CORTEX branding
6. **CREATE NEW** `src/orchestrators/learning_dashboard_launcher.py` (separate from metrics dashboard)
7. Implement HTTP server pattern (port 8081 default, fallback 8082-8089)
8. Add command handler: "launch learning"
9. Add CORS support and graceful shutdown
10. Test launcher independently from metrics dashboard
11. Write integration tests

**Deliverables:**
- `cortex-brain/learning/index.html` (50 lines)
- `cortex-brain/learning/.nojekyll` (empty file for GitHub Pages)
- `cortex-brain/learning/README.md` (landing page)
- **NEW:** `src/orchestrators/learning_dashboard_launcher.py` (120 lines) - **separate launcher**
- `tests/integration/test_learning_dashboard.py` (integration tests)
- `tests/orchestrators/test_learning_dashboard_launcher.py` (unit tests for launcher)

**Acceptance Criteria:**
- "launch learning" command works
- Learning dashboard opens in browser at http://localhost:8081
- Metrics dashboard (`launch dashboard`) still works independently on port 8080
- No coupling between learning and metrics dashboards (can start/stop separately)
- Sidebar navigation functional
- Full-text search functional
- Mobile-responsive (tested on 320px, 768px, 1920px)
- All tests pass (unit + integration)

---

### Phase 4: End-to-End Testing & Polish - Must-Have Tier (Week 4-4.5)

**Goal:** Comprehensive testing of 7 core components

**Tasks:**
1. Run full planning session with event capture (18 events)
2. Run ADO workflow (story + feature creation)
3. Test interactive planning flow
4. Verify document generation at all milestones
5. Test cross-chat session resumption
6. Performance testing (1000+ events, 18 event types)
7. Accessibility audit (WCAG 2.1 Level AA)
8. Browser compatibility testing (Chrome, Firefox, Safari, Edge)
9. Write user documentation (including ADO workflows)
10. Write developer documentation (including ADO event hooks)
11. Create demo video/screenshots
12. Final SKULL validation

**Deliverables:**
- User guide: `cortex-brain/documents/implementation-guides/learning-dashboard-user-guide.md`
- **NEW: ADO learning guide:** `cortex-brain/documents/implementation-guides/ado-learning-workflows-guide.md`
- Developer guide: `cortex-brain/documents/implementation-guides/adding-learning-events-guide.md`
- Event taxonomy reference: `cortex-brain/documents/reference/learning-event-taxonomy.md` (18 events)
- Demo assets in `cortex-brain/documents/planning/learning-library-demo/`
- Performance report: `cortex-brain/documents/reports/learning-system-performance.md`

**Acceptance Criteria:**
- All DoD items checked off
- User guide complete and tested with new user
- ADO workflows fully documented with examples
- Developer guide complete with code examples for all 7 components
- Performance targets met (overhead < 10ms, generation < 100ms, 18 event types)
- Accessibility score ≥ 90% (Lighthouse)
- All browsers render correctly
- Brain Protector challenges passed
- ADO story/feature creation captured correctly
- Planning strategy learnings accessible

---

### Phase 5: Should-Have Components - Architectural Learning (Week 5-6)

**Goal:** Add architectural and design decision learning events

**Scope:** 6 components, 15 events (SHOULD-HAVE tier, high learning value)

**Tasks:**
1. **ApplicationHealthOrchestrator (3 events):**
   - health_scan_started, language_analyzed, architecture_graphed
   - Captures: Component discovery, dependency analysis, architectural patterns
2. **CodeReviewOrchestrator (3 events):**
   - review_initiated, findings_generated, review_completed
   - Captures: Code quality learnings, common issues, best practices
3. **ArchitectAgent (3 events):**
   - architecture_analyzed, design_decision_made, architecture_validated
   - Captures: Design decisions, tradeoff analysis, architecture evolution
4. **ChangeGovernor (2 events):**
   - change_proposed, governance_check_passed
   - Captures: Governance learnings, policy decisions
5. **ErrorCorrector (2 events):**
   - error_detected, error_resolved
   - Captures: Debugging patterns, common fixes
6. **TestGenerator (2 events):**
   - tests_generated, test_strategy_applied
   - Captures: Test strategy learnings, coverage patterns
7. Extend event taxonomy to 33 events (18 + 15)
8. Create templates for architectural learnings
9. Update document generator for new categories
10. Write TDD tests (RED→GREEN→REFACTOR)
11. Integration testing with Phase 1 events

**Deliverables:**
- Event hooks in 6 new components (8-15 lines each)
- `src/learning/templates/architectural-learning.md`
- `src/learning/templates/code-quality-learning.md`
- `src/learning/templates/design-decision-learning.md`
- Updated event taxonomy (33 events total)
- `tests/learning/test_phase5_events.py` (300 lines)

**New Document Categories:**
8. **Architectural Patterns** - Component relationships, dependency learnings
9. **Code Quality** - Review findings, quality improvements
10. **Design Decisions** - Architecture choices, tradeoff analysis
11. **Debugging Patterns** - Error resolution strategies

**Acceptance Criteria:**
- 15 new events captured correctly
- Architectural learnings properly categorized
- Code review findings documented
- Design decision rationale preserved
- All tests pass (coverage ≥ 80%)
- No performance degradation (<10ms overhead per event)

---

### Phase 6: Should-Have Components - System Operations (Week 7-8)

**Goal:** Add system health and operational learning events

**Scope:** 9 components, 18 events (SHOULD-HAVE tier, operational context)

**Tasks:**
1. **ManagerReportOrchestrator (2 events):**
   - metrics_collected, report_generated
   - Captures: Productivity patterns, velocity learnings
2. **GitSyncAndOptimizeOrchestrator (3 events):**
   - sync_started, conflicts_resolved, optimization_completed
   - Captures: Conflict resolution strategies, merge learnings
3. **OnboardingAcknowledgmentOrchestrator (2 events):**
   - onboarding_started, rulebook_acknowledged
   - Captures: New user journey, governance acceptance
4. **DemoOrchestrator (2 events):**
   - demo_started, demo_completed
   - Captures: Feature demonstration patterns
5. **AdoptionAnalyticsOrchestrator (2 events):**
   - analytics_collected, adoption_metrics_calculated
   - Captures: Feature adoption patterns
6. **CodeExecutor (2 events):**
   - code_executed, execution_succeeded
   - Captures: Execution patterns, code testing
7. **IntentRouter (2 events):**
   - intent_classified, agent_selected
   - Captures: User intent patterns, routing decisions
8. **SessionResumer (1 event):**
   - session_restored
   - Captures: Context restoration learnings
9. **ScreenshotAnalyzer (2 events):**
   - screenshot_analyzed, requirements_extracted
   - Captures: Vision API usage, requirement extraction
10. Extend event taxonomy to 51 events (33 + 18)
11. Create templates for operational learnings
12. Update document generator for operational categories
13. Write TDD tests (RED→GREEN→REFACTOR)
14. Full system integration testing

**Deliverables:**
- Event hooks in 9 new components (5-10 lines each)
- `src/learning/templates/operational-learning.md`
- `src/learning/templates/productivity-learning.md`
- `src/learning/templates/onboarding-learning.md`
- Updated event taxonomy (51 events total)
- `tests/learning/test_phase6_events.py` (400 lines)

**New Document Categories:**
12. **Productivity Patterns** - Velocity, metrics, team insights
13. **Operational Learnings** - System health, optimization strategies
14. **User Onboarding** - New user journey, governance learnings
15. **Intent Routing** - User behavior patterns, command usage

**Acceptance Criteria:**
- 18 new events captured correctly
- Operational learnings properly documented
- Productivity patterns surfaced
- Onboarding journey captured
- All tests pass (coverage ≥ 80%)
- No performance degradation (<10ms overhead per event)
- Full system (51 events) performing within targets

---

### Phase 7: Polish & Documentation - Full System (Week 9-10)

**Goal:** Comprehensive documentation and final polish for all 22 components

**Tasks:**
1. Comprehensive user guide for all learning categories (15 categories)
2. Developer guide for adding events to any component type
3. Create learning journey map (visual guide)
4. Performance optimization for 51 events
5. Full accessibility audit (all categories)
6. Browser compatibility testing (all categories)
7. Create comprehensive demo covering all phases
8. Record tutorial videos for each learning category
9. Generate metrics report (event capture rates, category distribution)
10. Final SKULL validation (all components)
11. Create migration guide for adding Phase 5-6 events to existing orchestrators
12. Document extensibility patterns for future components

**Deliverables:**
- Comprehensive user guide (50+ pages)
- Complete developer guide with 22 component examples
- Learning journey map (visual diagram)
- Video tutorials (15 videos, one per category)
- Performance report (51 events, 22 components)
- Metrics dashboard integration (learning system analytics)
- Extension guide for future components
- `cortex-brain/documents/reports/learning-system-final-report.md`

**Acceptance Criteria:**
- All 15 learning categories documented
- Developer guide covers all 22 components
- Video tutorials professionally produced
- Performance targets met for 51 events
- Accessibility score ≥ 95% (Lighthouse)
- Browser compatibility 100% (Chrome, Firefox, Safari, Edge)
- Metrics show ≥95% event capture rate
- User testing shows ≥90% satisfaction
- All Brain Protector challenges passed

---

## 📈 Success Metrics

### Quantitative (Phase 1-4 MVP)

- **Event Capture Rate:** ≥ 95% of milestones captured (18 event types)
- **Component Coverage:** 7 must-have components operational
- **ADO Integration:** 100% of ADO workflows captured (4 events)
- **Planning Strategy Coverage:** 100% of planning paths captured (5 events)
- **Update Efficiency:** ≤ 10 updates per planning session (vs 100+ with continuous)
- **Performance Overhead:** < 10ms per event emission
- **Documentation Accuracy:** ≥ 95% (measured by user surveys)
- **Dashboard Load Time:** < 2 seconds
- **Search Performance:** < 500ms for any query
- **Test Coverage:** ≥ 80% for learning module

### Quantitative (Phase 5-7 Full System)

- **Event Capture Rate:** ≥ 95% of milestones captured (51 event types)
- **Component Coverage:** 22 components operational (23 orchestrators - 1 not applicable)
- **Category Coverage:** 15 learning categories populated
- **Update Efficiency:** ≤ 20 updates per full workflow cycle
- **Performance Overhead:** < 10ms per event (51 events, no degradation)
- **Documentation Accuracy:** ≥ 95% across all categories
- **Dashboard Load Time:** < 2 seconds (51 events)
- **Search Performance:** < 500ms across 15 categories
- **Test Coverage:** ≥ 80% for all learning modules

### Qualitative (MVP)

- Users can explain learning library purpose without prompting
- Users reference past learning docs during new projects
- Developers successfully add learning events to new orchestrators
- No confusion about "why" decisions were made weeks later
- **Users understand ADO workflow patterns** (NEW)
- **Users can explain when to use interactive vs autonomous planning** (NEW)
- **Onboarding time reduced by 30%** (measured by time-to-first-contribution)

### Qualitative (Full System)

- Users leverage architectural learnings for design decisions
- Code quality improves based on review learnings
- Conflict resolution improves using git sync learnings
- Debugging time reduced using error correction patterns
- New users complete onboarding journey successfully
- All 15 learning categories actively referenced

---

## 🚨 Risks & Mitigations

### Risk 1: Event Taxonomy Incomplete
**Impact:** Medium | **Probability:** Medium

- **Description:** Initial event taxonomy misses important learning moments
- **Mitigation:** 
  - Start with MVP taxonomy (10-15 events)
  - Add telemetry to identify missed milestones
  - Iterate based on user feedback in Phase 4
- **Fallback:** Manual documentation until taxonomy expanded

### Risk 2: Orchestrator Changes Break Existing Functionality
**Impact:** High | **Probability:** Low

- **Description:** Adding event hooks disrupts orchestrator execution
- **Mitigation:**
  - Event emission is fire-and-forget (no exceptions propagate)
  - Comprehensive test coverage before merge
  - Gradual rollout (one orchestrator at a time)
- **Fallback:** Feature flag to disable learning capture

### Risk 3: Documentation Generation Too Slow
**Impact:** Medium | **Probability:** Low

- **Description:** Document generation blocks orchestrator execution
- **Mitigation:**
  - Async generation with background thread
  - Performance testing in Phase 4
  - Caching of template renders
- **Fallback:** Batch generation after orchestrator completion

### Risk 4: Users Don't Discover Learning Dashboard
**Impact:** Medium | **Probability:** Medium

- **Description:** Users unaware of "launch learning" command
- **Mitigation:**
  - Add to `help` command output
  - Include in onboarding flow
  - Auto-prompt after first plan approval: "Want to see your learning timeline?"
- **Fallback:** Documentation-only (no active promotion)

---

## 🔗 Dependencies

### Internal CORTEX Dependencies

- ✅ `planning_orchestrator.py` (exists, needs event hooks)
- ✅ `plan_execution_orchestrator.py` (exists, needs event hooks)
- ✅ `git_checkpoint_orchestrator.py` (exists, needs event hooks)
- ✅ `dashboard_launcher.py` (exists, pattern reference only - NO modifications)
- 📦 `learning_dashboard_launcher.py` (NEW - separate launcher for learning content)
- 🔄 TDD orchestrator (future integration, not blocking)

### External Dependencies

- ✅ Python 3.8+ (already satisfied)
- ✅ PyYAML (already in requirements.txt)
- 📦 Docsify 4.13.1 (CDN, no install required)
- 📦 http.server (Python stdlib, already used by dashboard_launcher)

### Infrastructure Dependencies

- ✅ `cortex-brain/learning/` directory (will create in Phase 3)
- ✅ Port 8081 availability (fallback to 8082-8089)
- ✅ Web browser (user's default browser)

---

## 🎓 Learning Resources for Implementation Team

### Event-Driven Architecture
- [Martin Fowler: Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [Observer Pattern (Gang of Four)](https://refactoring.guru/design-patterns/observer)

### Markdown Generation
- [Python-Markdown Documentation](https://python-markdown.github.io/)
- [Jinja2 Templates for Markdown](https://jinja.palletsprojects.com/)

### Docsify
- [Docsify Official Documentation](https://docsify.js.org/)
- [Docsify Themes Showcase](https://docsify.js.org/#/themes)
- [Docsify Plugins](https://docsify.js.org/#/plugins)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock for Event Testing](https://docs.python.org/3/library/unittest.mock.html)

---

## 📝 Open Questions (To Be Resolved in Phase 1)

1. **Event Granularity:** Should we capture sub-phase milestones (e.g., "DoR validated") or only phase boundaries?
   - **Proposed Answer:** Only phase boundaries for MVP, add sub-phase in v2

2. **Resource Link Curation:** Who maintains resource-links.yaml? Manual vs automated discovery?
   - **Proposed Answer:** Manual curation initially, explore automated in v2

3. **Multi-User Scenarios:** How do we handle multiple users in same CORTEX instance?
   - **Proposed Answer:** Not a concern - CORTEX is single-user per instance

4. **Historical Data Migration:** Do we backfill learning docs from past planning sessions?
   - **Proposed Answer:** No backfill - fresh start with event-driven system

5. **TDD Integration Timing:** When do we add TDD orchestrator events?
   - **Proposed Answer:** Phase 5 (future), not blocking for MVP

---

## 📅 Timeline

| Phase | Duration | Components | Events | Key Milestone |
|-------|----------|------------|--------|---------------|
| **Phase 1:** Event Infrastructure (Must-Have) | 1.5 weeks | 7 | 18 | Core event capture working |
| **Phase 2:** Document Generation (Must-Have) | 1.5 weeks | 7 | 18 | Markdown generation + ADO templates |
| **Phase 3:** Docsify Integration | 1 week | N/A | N/A | Learning dashboard live |
| **Phase 4:** Testing & Polish (Must-Have) | 1 week | 7 | 18 | MVP complete & validated |
| **Sub-Total (Must-Have MVP)** | **5 weeks** | **7** | **18** | **Production-ready core system** |
| | | | | |
| **Phase 5:** Architectural Learning (Should-Have) | 2 weeks | +6 | +15 | Architectural patterns captured |
| **Phase 6:** System Operations (Should-Have) | 2 weeks | +9 | +18 | Full system operational learning |
| **Phase 7:** Final Polish & Documentation | 2 weeks | 22 | 51 | Complete system documented |
| **Grand Total (Full System)** | **11 weeks** | **22** | **51** | **Comprehensive learning library** |

---

**Delivery Options:**

**Option A: MVP First (Recommended)**
- Deliver Phases 1-4 (5 weeks)
- Get user feedback
- Iterate on Phases 5-7 based on usage

**Option B: Full System**
- Deliver all 7 phases (11 weeks)
- Complete coverage of all components
- Single comprehensive release

**Option C: Incremental**
- Phase 1-4: 5 weeks (MVP)
- Phase 5: +2 weeks (architectural learning)
- Phase 6-7: +4 weeks (complete system)
- Total: 11 weeks, 3 releases

---

## ✅ Approval & Next Steps

**Plan Status:** ✅ APPROVED (User selected Option A)

**Awaiting User Confirmation:**
- [ ] Confirm 4-week timeline acceptable
- [ ] Confirm event taxonomy starting point (Phase 1 deliverable)
- [ ] Confirm resource link database approach (manual curation)

**Once Approved, Execute:**
1. Run `approve plan` to lock this plan
2. Option A: `execute all phases autonomously` (auto-chained execution)
3. Option B: Phase-by-phase approval required

**Questions Before Proceeding?**
- Timeline adjustments needed?
- Event taxonomy concerns?
- Docsify alternatives to consider?
- Risk mitigations insufficient?

---

**Plan Author:** Asif Hussain  
**Planning System:** CORTEX Planning System 2.0  
**Document Version:** 1.0.0  
**Last Updated:** December 6, 2025
