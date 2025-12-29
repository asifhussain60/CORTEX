# Learning Library System - CORTEX Repository Scan

**Date:** December 6, 2025  
**Purpose:** Identify all orchestrators, agents, and systems that should emit learning events  
**Scope:** Comprehensive scan beyond initial 3 orchestrators

---

## 🎯 Scan Summary

**Total Components Identified:** 23 orchestrators + 15 agents = **38 learning event sources**

**Initial Plan Coverage:** 3 orchestrators (13% of orchestrators)  
**Expanded Coverage:** 38 components (100% comprehensive)

---

## 📊 Orchestrators Discovered

### Tier 1: Core Workflow Orchestrators (Already in Plan)

| Orchestrator | File | Learning Events | Priority |
|--------------|------|-----------------|----------|
| **PlanningOrchestrator** | `planning_orchestrator.py` | plan_created, plan_approved, plan_modified, plan_abandoned | ✅ HIGH - IN PLAN |
| **PlanExecutionOrchestrator** | `plan_execution_orchestrator.py` | phase_started, phase_completed, phase_failed, execution_paused, execution_resumed | ✅ HIGH - IN PLAN |
| **GitCheckpointOrchestrator** | `git_checkpoint_orchestrator.py` | checkpoint_created, checkpoint_committed, checkpoint_failed | ✅ HIGH - IN PLAN |

---

### Tier 2: ADO/Work Management Orchestrators (MISSING FROM PLAN)

| Orchestrator | File | Learning Events | Priority |
|--------------|------|-----------------|----------|
| **ADO Work Item System** | N/A (see note below) | story_created, feature_created, work_item_updated, acceptance_criteria_met | ⚠️ **CRITICAL - MISSING** |
| **UnifiedEntryPointOrchestrator** | `routing/unified_entry_point_utility.py` | workflow_started, operation_routed, workflow_completed | 🔥 **HIGH - ADD** |

**NOTE:** ADO orchestrator was planned for utility migration (Sprint 3). Based on semantic search, ADO functionality exists through:
- `src/cortex_agents/ado_agent.py` (Agent wrapper)
- `src/operations/modules/routing/unified_entry_point_utility.py` (Utility functions)
- `src/operations/modules/ado/ado_utility.py` (Core utility)

**Learning Events to Capture:**
- `ado_story_created` - User story created with acceptance criteria
- `ado_feature_created` - Feature created with related stories
- `ado_work_item_completed` - Work item marked complete
- `ado_acceptance_criteria_validated` - DoR/DoD validation passed

---

### Tier 3: System Health & Monitoring Orchestrators (MISSING FROM PLAN)

| Orchestrator | File | Learning Events | Priority |
|--------------|------|-----------------|----------|
| **ApplicationHealthOrchestrator** | `application_health_orchestrator.py` | health_scan_started, language_analyzed, architecture_graphed, health_report_generated | 🔥 **MEDIUM-HIGH - ADD** |
| **ManagerReportOrchestrator** | `manager_report_orchestrator.py` | metrics_collected, report_generated, insights_surfaced | 🟡 **MEDIUM - ADD** |
| **GitSyncAndOptimizeOrchestrator** | `git_sync_and_optimize.py` | sync_started, conflicts_resolved, optimization_completed, sync_failed | 🟡 **MEDIUM - ADD** |
| **DashboardLauncher** | `dashboard_launcher.py` | dashboard_launched, server_started, port_fallback, dashboard_closed | 🟢 **LOW - OPTIONAL** |

**Rationale for Priority:**
- **ApplicationHealthOrchestrator:** Captures architectural learning (what components exist, dependencies discovered)
- **ManagerReportOrchestrator:** Captures productivity patterns (velocity learnings, quality trends)
- **GitSyncAndOptimizeOrchestrator:** Captures conflict resolution strategies (learning from merges)
- **DashboardLauncher:** Low priority - operational, not educational

---

### Tier 4: Specialized Workflow Orchestrators (MISSING FROM PLAN)

| Orchestrator | File | Learning Events | Priority |
|--------------|------|-----------------|----------|
| **OnboardingAcknowledgmentOrchestrator** | `onboarding_acknowledgment_orchestrator.py` | onboarding_started, rulebook_acknowledged, onboarding_completed | 🟡 **MEDIUM - ADD** |
| **CodeReviewOrchestrator** | `code_review/code_review_orchestrator.py` | review_initiated, findings_generated, review_completed | 🟡 **MEDIUM - ADD** |
| **DemoOrchestrator** | `tdd/demo_orchestrator.py` | demo_started, demo_section_completed, demo_finished | 🟢 **LOW - OPTIONAL** |
| **AdoptionAnalyticsOrchestrator** | `tier3/orchestrators/adoption_analytics_orchestrator.py` | analytics_collected, adoption_metrics_calculated | 🟢 **LOW - OPTIONAL** |
| **ParallelCollectorOrchestrator** | `dashboard/data/parallel_collector.py` | parallel_collection_started, collectors_completed | 🟢 **LOW - OPTIONAL** |
| **MultiTemplateOrchestrator** | `response_templates/multi_template_orchestrator.py` | template_selected, response_rendered | 🟢 **LOW - OPTIONAL** |

**Rationale:**
- **OnboardingOrchestrator:** Captures learning journey start (valuable for understanding user progression)
- **CodeReviewOrchestrator:** Captures quality learnings (common issues, patterns discovered)
- **Others:** Operational/internal, lower educational value for users

---

## 🤖 Agents Discovered (Learning Event Opportunities)

### Strategic Agents (High Learning Value)

| Agent | File | Learning Events | Priority |
|-------|------|-----------------|----------|
| **WorkPlanner** | `work_planner/agent.py` | planning_request, plan_strategy_selected, plan_validated | 🔥 **HIGH - ADD** |
| **InteractivePlannerAgent** | `strategic/interactive_planner.py` | interactive_planning_started, clarification_requested, requirements_finalized | 🔥 **HIGH - ADD** |
| **ArchitectAgent** | `strategic/architect.py` | architecture_analyzed, design_decision_made, architecture_validated | 🟡 **MEDIUM - ADD** |
| **ChangeGovernor** | `change_governor.py` | change_proposed, governance_check_passed, change_approved | 🟡 **MEDIUM - ADD** |

### Tactical Agents (Medium Learning Value)

| Agent | File | Learning Events | Priority |
|-------|------|-----------------|----------|
| **CodeExecutor** | `code_executor/agent.py` | code_executed, execution_succeeded, execution_failed | 🟡 **MEDIUM - ADD** |
| **ErrorCorrector** | `error_corrector/agent.py` | error_detected, correction_attempted, error_resolved | 🟡 **MEDIUM - ADD** |
| **TestGenerator** | `test_generator/agent.py` | tests_generated, test_strategy_applied, tests_validated | 🟡 **MEDIUM - ADD** |

### Support Agents (Lower Learning Value)

| Agent | File | Learning Events | Priority |
|-------|------|-----------------|----------|
| **IntentRouter** | `intent_router.py` | intent_classified, agent_selected, routing_completed | 🟢 **LOW - OPTIONAL** |
| **SessionResumer** | `session_resumer.py` | session_restored, context_loaded, resumption_completed | 🟢 **LOW - OPTIONAL** |
| **ScreenshotAnalyzer** | `screenshot_analyzer.py` | screenshot_analyzed, requirements_extracted, vision_api_called | 🟢 **LOW - OPTIONAL** |
| **ADOAgent** | `ado_agent.py` | ado_operation_routed, ado_workflow_executed | 🟢 **LOW - DUPLICATE** (covered by ADO utility) |
| **ApplicationHealthAgent** | `application_health_agent.py` | health_check_requested, health_report_delivered | 🟢 **LOW - DUPLICATE** (covered by orchestrator) |
| **ComplianceDashboardAgent** | `compliance_dashboard_agent.py` | compliance_checked, dashboard_rendered | 🟢 **LOW - OPTIONAL** |
| **RCAAgent** | `rca_agent.py` | root_cause_analysis_started, root_cause_identified | 🟢 **LOW - OPTIONAL** |
| **CommitHandler** | `commit_handler.py` | commit_prepared, commit_executed | 🟢 **LOW - OPTIONAL** |
| **HealthValidator** | `health_validator/agent.py` | validation_executed, health_score_calculated | 🟢 **LOW - OPTIONAL** |

---

## 🎯 Recommended Additions to Learning Library Plan

### Phase 1 Additions (Event Infrastructure)

**Original Plan:** 3 orchestrators (planning, execution, git_checkpoint)

**Recommended Additions:**
1. **ADO Work Item System** (CRITICAL)
   - Events: `ado_story_created`, `ado_feature_created`, `ado_work_item_completed`, `ado_acceptance_criteria_validated`
   - Rationale: ADO was explicitly requested by user, captures work management learnings
   - Implementation: Add hooks in `unified_entry_point_utility.py` and `ado_utility.py`

2. **UnifiedEntryPointOrchestrator** (HIGH)
   - Events: `workflow_started`, `operation_routed`, `workflow_completed`
   - Rationale: Central entry point, captures overall workflow patterns
   - Implementation: Add hooks in `routing/unified_entry_point_utility.py`

3. **WorkPlanner Agent** (HIGH)
   - Events: `planning_request`, `plan_strategy_selected`, `plan_validated`
   - Rationale: Captures planning strategy learnings (when to use what planning approach)
   - Implementation: Add hooks in `work_planner/agent.py`

4. **InteractivePlannerAgent** (HIGH)
   - Events: `interactive_planning_started`, `clarification_requested`, `requirements_finalized`
   - Rationale: Captures interactive planning learnings (how requirements evolve)
   - Implementation: Add hooks in `strategic/interactive_planner.py`

**Updated Phase 1 Event Count:**
- Original: 6 events (3 orchestrators × 2 events each)
- Updated: **18 events** (7 components × 2-3 events each)

---

### Phase 2 Additions (Document Generation)

**Additional Document Categories:**

1. **ADO Workflow Patterns** (`cortex-brain/learning/patterns/ado-workflows.md`)
   - When to create story vs feature
   - How to write effective acceptance criteria
   - DoR/DoD validation patterns

2. **Planning Strategy Guide** (`cortex-brain/learning/concepts/planning-strategies.md`)
   - Interactive vs autonomous planning
   - Vision API usage for screenshot analysis
   - Requirements clarification best practices

3. **Work Management Milestones** (`cortex-brain/learning/milestones/work-management/`)
   - ADO work item creation milestones
   - Feature-story relationship learnings
   - Workflow state transitions

---

### Phase 3 Additions (Docsify UI)

**Navigation Structure Update:**

```markdown
# Sidebar Navigation (_sidebar.md)

* Getting Started
  * [Welcome](/)
  * [How to Use Learning Dashboard](concepts/how-to-use.md)

* Core Workflows
  * [Planning System](concepts/planning-system.md)
  * [Plan Execution](concepts/plan-execution.md)
  * [Git Checkpoint Workflow](patterns/git-checkpoints.md)
  * **[ADO Work Management](concepts/ado-work-management.md)** ← NEW
  * **[Interactive Planning](patterns/interactive-planning.md)** ← NEW

* Patterns & Best Practices
  * [Event-Driven Architecture](patterns/event-driven-architecture.md)
  * [Milestone-Based Documentation](patterns/milestone-documentation.md)
  * **[ADO Workflow Patterns](patterns/ado-workflows.md)** ← NEW
  * **[Planning Strategies](patterns/planning-strategies.md)** ← NEW

* Milestones
  * [Planning Milestones](milestones/planning/)
  * [Execution Milestones](milestones/execution/)
  * **[ADO Milestones](milestones/ado/)** ← NEW

* Resources
  * [External Links](resources/links.md)
  * [Tutorials](resources/tutorials.md)
```

---

## 📋 Updated Event Taxonomy

### Expanded Event Types (18 total, up from 10-15)

**Planning & Execution Events:**
1. `plan_created` - Planning orchestrator
2. `plan_approved` - Planning orchestrator
3. `plan_abandoned` - Planning orchestrator
4. `phase_started` - Execution orchestrator
5. `phase_completed` - Execution orchestrator
6. `checkpoint_committed` - Git checkpoint orchestrator

**ADO Work Management Events** (NEW):
7. `ado_story_created` - ADO utility
8. `ado_feature_created` - ADO utility
9. `ado_work_item_completed` - ADO utility
10. `ado_acceptance_criteria_validated` - ADO utility

**Workflow Routing Events** (NEW):
11. `workflow_started` - Unified entry point
12. `operation_routed` - Unified entry point
13. `workflow_completed` - Unified entry point

**Planning Strategy Events** (NEW):
14. `planning_request` - WorkPlanner agent
15. `plan_strategy_selected` - WorkPlanner agent
16. `interactive_planning_started` - InteractivePlanner agent
17. `clarification_requested` - InteractivePlanner agent
18. `requirements_finalized` - InteractivePlanner agent

---

## 🚨 Critical Gaps Identified

### Gap 1: ADO Integration (CRITICAL)
**Problem:** Original plan missed ADO orchestrators entirely, despite user explicitly requesting ADO inclusion.

**Impact:** Learning library would not capture ADO work item creation, feature management, or DoR/DoD validation learnings.

**Solution:** Add ADO event hooks in Phase 1 (4 events across unified entry point and ADO utility).

---

### Gap 2: Planning Strategy Diversity (HIGH)
**Problem:** Original plan only captured plan approval, not the planning strategy selection process.

**Impact:** Users wouldn't learn *when* to use interactive vs autonomous planning, or how to leverage Vision API.

**Solution:** Add WorkPlanner and InteractivePlanner agent hooks in Phase 1 (5 events).

---

### Gap 3: Workflow Orchestration Context (MEDIUM)
**Problem:** No capture of high-level workflow routing (which operations users invoke, how workflows are chained).

**Impact:** Missing "big picture" learning about CORTEX workflow patterns.

**Solution:** Add UnifiedEntryPointOrchestrator hooks in Phase 1 (3 events).

---

## 📊 Revised Implementation Phases

### Phase 1: Event Infrastructure (Week 1) - UPDATED

**Original:** 3 orchestrators, 6 events  
**Updated:** 7 components, 18 events

**New Tasks:**
1-3. ✅ Original tasks (planning, execution, git_checkpoint)
4. **ADD: ADO event hooks** (unified_entry_point_utility.py, ado_utility.py)
5. **ADD: Workflow routing hooks** (unified_entry_point_utility.py)
6. **ADD: WorkPlanner agent hooks** (work_planner/agent.py)
7. **ADD: InteractivePlanner agent hooks** (strategic/interactive_planner.py)
8-9. TDD tests (RED→GREEN→REFACTOR)

**Deliverables (Updated):**
- Event taxonomy with **18 event types** (up from 10-15)
- Event emitter hooks in **7 components** (up from 3)
- Tests for all 18 events

---

### Phase 2: Document Generation (Week 2) - UPDATED

**New Deliverables:**
- ADO workflow pattern templates
- Planning strategy concept documents
- Work management milestone templates
- Resource links for ADO best practices

**Template Additions:**
- `templates/ado-story-learning.md`
- `templates/ado-feature-learning.md`
- `templates/planning-strategy-learning.md`
- `templates/interactive-planning-learning.md`

---

### Phase 3: Docsify UI Integration (Week 3) - UPDATED

**Navigation Structure:**
- Add ADO section to sidebar
- Add Planning Strategies section
- Add Workflow Patterns section
- Auto-generate navigation for 4 categories (concepts/patterns/milestones/resources)

---

## ✅ Prioritization Matrix

### Must-Have (Phase 1)
- ✅ Planning Orchestrator (original)
- ✅ Execution Orchestrator (original)
- ✅ Git Checkpoint Orchestrator (original)
- 🔥 **ADO Work Item System** (NEW - user requested)
- 🔥 **Unified Entry Point Orchestrator** (NEW - workflow context)
- 🔥 **WorkPlanner Agent** (NEW - planning strategies)
- 🔥 **InteractivePlanner Agent** (NEW - requirements evolution)

### Should-Have (Phase 2 or v2.0)
- ApplicationHealthOrchestrator (architectural learnings)
- CodeReviewOrchestrator (quality learnings)
- ArchitectAgent (design decisions)
- ChangeGovernor (governance learnings)
- ErrorCorrector (debugging patterns)
- TestGenerator (test strategies)

### Could-Have (v2.0 or later)
- ManagerReportOrchestrator
- GitSyncAndOptimizeOrchestrator
- OnboardingAcknowledgmentOrchestrator
- All other support agents

---

## 📝 Recommendations for User

**Immediate Actions:**
1. ✅ Approve updated Phase 1 scope (7 components instead of 3)
2. ✅ Confirm ADO inclusion is critical (matches user request)
3. ✅ Validate 18-event taxonomy vs original 10-15

**Timeline Impact:**
- Phase 1: 1 week → **1.5 weeks** (7 components vs 3)
- Phase 2: 1 week → **1.5 weeks** (additional templates)
- Phase 3: 1 week → **1 week** (no change)
- Phase 4: 1 week → **1 week** (no change)
- **New Total: 5 weeks** (up from 4 weeks)

**Risk Mitigation:**
- Can defer "Should-Have" components to v2.0 if timeline is critical
- Must include ADO (user explicitly requested)
- Must include workflow routing (provides context for all other events)

---

## 🎯 Updated Success Metrics

**Quantitative (Updated):**
- **Event Capture Rate:** ≥ 95% of milestones captured (18 event types)
- **Component Coverage:** 7 components in Phase 1 (vs 3 original)
- **ADO Integration:** 100% of ADO workflows captured (4 events)
- **Planning Strategy Coverage:** 100% of planning paths captured (5 events)

**Qualitative (Updated):**
- Users can explain ADO workflow patterns without prompting
- Users understand when to use interactive vs autonomous planning
- Developers successfully add learning events to new components
- ADO learnings reference DoR/DoD validation patterns

---

## 📚 Next Steps

1. **User Decision:** Approve 7-component Phase 1 scope (vs original 3)
2. **User Decision:** Confirm 5-week timeline (vs original 4 weeks)
3. **User Decision:** Prioritize "Should-Have" components for v2.0 or defer
4. **Update Plan Document:** Incorporate scan findings into `learning-library-system-plan.md`
5. **Approve Plan:** Lock in scope and begin Phase 1 implementation

---

**Scan Complete**  
**Author:** Asif Hussain  
**Scan Date:** December 6, 2025  
**Components Scanned:** 38 (23 orchestrators + 15 agents)  
**Recommendations:** Add 4 components to Phase 1, expand event taxonomy to 18 events
