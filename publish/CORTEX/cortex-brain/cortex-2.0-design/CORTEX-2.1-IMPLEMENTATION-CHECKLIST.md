# CORTEX 2.1 Implementation Checklist

**Document:** CORTEX-2.1-IMPLEMENTATION-CHECKLIST.md  
**Created:** 2025-11-09  
**Status:** 🎯 READY FOR IMPLEMENTATION  
**Priority:** HIGH (Required before Week 19)  
**Timeline:** 6 weeks (Week 19-24, parallel with CORTEX 2.0 Phase 6-7)

---

## 📋 Executive Summary

**Purpose:** Detailed task-by-task checklist for implementing CORTEX 2.1 features (Interactive Planning + Command Discovery) during CORTEX 2.0 Phases 6-7.

**Approach:** Parallel hybrid implementation
- Week 19-24: CORTEX 2.1 implementation (6 weeks)
- Week 19-20: Overlaps with 2.0 Phase 6 (Performance)
- Week 21-24: Overlaps with 2.0 Phase 7 (Documentation)

**Gap Analysis Completed:** ✅ See `CORTEX-2.0-2.1-INTEGRATION-ANALYSIS.md`  
**Operations Registry Updated:** ✅ See `cortex-operations.yaml` v2.1  
**STATUS.md Updated:** ✅ See 2.1 Integration section

---

## 🎯 Integration with CORTEX 2.0 Phases

### Phase 6 Coordination (Week 19-20)

**CORTEX 2.0 Phase 6 Activities:**
- Performance optimization (query tuning, caching, benchmarks)
- Tier 1 database index optimization
- Tier 2 knowledge graph performance tuning
- Memory profiling and optimization
- **Resource requirement:** 1-2 developers

**CORTEX 2.1 Week 1-2 Activities (Parallel):**
- Interactive Planning foundation (agent, utilities, Tier 1 schema)
- Command Discovery Phase 1 (HelpAgent, basic /help)
- **Resource requirement:** 2 developers

**Resource Allocation:**
- Developer 1: CORTEX 2.1 Interactive Planning (full-time)
- Developer 2: CORTEX 2.1 Command Discovery (full-time)
- Developer 3: CORTEX 2.0 Performance optimization (shared with QA)
- QA Engineer: Testing both tracks
- **Total:** 3 developers + 1 QA (manageable with shared resources)

**Conflict Risk:** 🟢 LOW (different codebases, minimal overlap)

---

### Phase 7 Coordination (Week 21-24)

**CORTEX 2.0 Phase 7 Activities:**
- Documentation generation system
- API documentation automation
- User guides and tutorials
- **Resource requirement:** 1 developer + UX

**CORTEX 2.1 Week 3-6 Activities (Parallel):**
- Advanced planning (Week 3-4): Tier 2 learning, command registration
- Integration & Polish (Week 5-6): Full system integration, testing
- **Resource requirement:** 2 developers + UX

**Resource Allocation:**
- Developer 1: CORTEX 2.1 Advanced Planning (full-time)
- Developer 2: CORTEX 2.1 Command Discovery Phase 2-3 (full-time)
- Developer 3: CORTEX 2.0 Documentation + 2.1 Integration (shared)
- UX Designer: Visual enhancements for command discovery + 2.0 docs
- QA Engineer: Comprehensive testing both tracks
- **Total:** 3 developers + 1 UX + 1 QA

**Synergy Opportunity:** 🟢 HIGH
- 2.1 Command Discovery enhances 2.0 documentation discoverability
- 2.1 Interactive Planning can document itself via 2.0 doc system
- Test 2.1 features by documenting them via 2.0 doc generation

**Conflict Risk:** 🟢 LOW (complementary work, natural synergy)

---

## 📅 Week-by-Week Task Breakdown

### 🚀 Week 19-20: Foundation (CORTEX 2.1 Week 1-2)

**Parallel with:** CORTEX 2.0 Phase 6 (Performance Optimization)

#### Week 19: Interactive Planning Infrastructure

**Priority:** 🔴 CRITICAL (Foundation for all planning features)

##### Day 1-2: InteractivePlannerAgent Core

- [ ] **Task 1.1:** Create `InteractivePlannerAgent` class
  - **File:** `src/cortex_agents/right_brain/interactive_planner.py`
  - **LOC:** ~200 lines
  - **Owner:** Developer 1
  - **Dependencies:** None (can start immediately)
  - **Deliverables:**
    - [ ] Agent class inheriting from `BaseAgent`
    - [ ] Ambiguity detection algorithm (keyword analysis + pattern matching)
    - [ ] State machine skeleton (INIT → QUESTION → ANSWER → SYNTHESIZE → APPROVAL)
    - [ ] Basic error handling
  - **Tests:**
    - [ ] `test_interactive_planner_initialization` (unit)
    - [ ] `test_ambiguity_detection_basic` (unit)
    - [ ] `test_state_machine_transitions` (unit)
  - **Completion Criteria:** Agent initializes, detects basic ambiguity, transitions states
  - **Gap Analysis:** ✅ No gaps - design complete in `CORTEX-2.1-INTERACTIVE-PLANNING.md`

- [ ] **Task 1.2:** Build `QuestionGenerator` utility
  - **File:** `src/cortex_agents/right_brain/question_generator.py`
  - **LOC:** ~150 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 1.1 complete
  - **Deliverables:**
    - [ ] Question types: multiple choice, yes/no, free text
    - [ ] Priority system (1-5 scale)
    - [ ] Context-aware generation
    - [ ] Max 5 questions enforcement
  - **Tests:**
    - [ ] `test_generate_multiple_choice_question` (unit)
    - [ ] `test_generate_yes_no_question` (unit)
    - [ ] `test_prioritize_questions` (unit)
    - [ ] `test_max_5_questions_enforcement` (unit)
  - **Completion Criteria:** Generates well-formed questions, prioritizes correctly
  - **Gap Analysis:** ⚠️ **GAP FOUND** - Need question templates in Tier 2
    - **Fix:** Add `question_templates.yaml` to Tier 2 schema (see Task 1.5)

##### Day 3: Answer Parsing & Context Tracking

- [ ] **Task 1.3:** Build `AnswerParser` utility
  - **File:** `src/cortex_agents/right_brain/answer_parser.py`
  - **LOC:** ~180 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 1.2 complete
  - **Deliverables:**
    - [ ] Extract direct answers from natural language
    - [ ] Extract additional context/keywords
    - [ ] Map context to potential question topics
    - [ ] Generate confidence scores (0-100%)
  - **Tests:**
    - [ ] `test_extract_direct_answer` (unit)
    - [ ] `test_extract_context_keywords` (unit)
    - [ ] `test_confidence_scoring` (unit)
    - [ ] `test_multi_topic_extraction` (integration)
  - **Completion Criteria:** Parses answers, extracts context, scores confidence ≥85%
  - **Gap Analysis:** ✅ No gaps - context tracking design in `CORTEX-2.1-CONTEXT-TRACKING-UPDATE.md`

- [ ] **Task 1.4:** Build `QuestionFilter` utility
  - **File:** `src/cortex_agents/right_brain/question_filter.py`
  - **LOC:** ~120 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 1.3 complete
  - **Deliverables:**
    - [ ] Filter redundant questions based on extracted context
    - [ ] Check direct answers, implied answers, user preferences
    - [ ] Apply confidence threshold (default 85%)
    - [ ] Log skipped questions for transparency
  - **Tests:**
    - [ ] `test_skip_redundant_question` (unit)
    - [ ] `test_confidence_threshold_filtering` (unit)
    - [ ] `test_preference_based_filtering` (unit)
    - [ ] `test_skip_logging` (integration)
  - **Completion Criteria:** Skips >40% of redundant questions in test scenarios
  - **Gap Analysis:** ✅ No gaps - smart skipping designed in CORTEX 2.1 docs

##### Day 4: Database Schema Extension

- [ ] **Task 1.5:** Extend Tier 1 memory schema
  - **File:** `src/tier1/schema/migrations/004_interactive_planning.sql`
  - **LOC:** ~80 lines SQL
  - **Owner:** Developer 1
  - **Dependencies:** Tasks 1.1-1.4 complete
  - **Deliverables:**
    - [ ] New table: `interactive_planning_sessions`
      - Columns: session_id, conversation_id, questions_asked, answers_received, extracted_context, confidence_scores, final_plan, created_at
    - [ ] New table: `question_templates` (fix for Gap in Task 1.2)
      - Columns: template_id, question_type, template_text, priority, tags
    - [ ] Migration script with rollback
    - [ ] Database indices for performance
  - **Tests:**
    - [ ] `test_create_planning_session` (integration)
    - [ ] `test_store_questions_answers` (integration)
    - [ ] `test_query_session_history` (integration)
    - [ ] `test_migration_rollback` (unit)
  - **Completion Criteria:** Tables created, migration works, queries <20ms
  - **Gap Analysis:** ⚠️ **GAP FOUND** - `question_templates` table not in original design
    - **Fix:** Added to this task (80 lines → 120 lines SQL)

##### Day 5: Unit Testing & Documentation

- [ ] **Task 1.6:** Comprehensive unit tests for Week 1
  - **Files:** `tests/cortex_agents/right_brain/test_interactive_planner*.py`
  - **LOC:** ~300 lines tests
  - **Owner:** Developer 1 + QA
  - **Dependencies:** Tasks 1.1-1.5 complete
  - **Deliverables:**
    - [ ] 85%+ code coverage for all Week 1 components
    - [ ] All unit tests passing (RED → GREEN → REFACTOR)
    - [ ] Integration test: Full question-answer cycle
  - **Tests:**
    - [ ] All subtasks 1.1-1.5 tests passing (20+ tests)
    - [ ] `test_end_to_end_planning_session` (integration)
    - [ ] `test_error_recovery` (integration)
  - **Completion Criteria:** 85%+ coverage, 0 test failures
  - **Gap Analysis:** ✅ No gaps - TDD approach consistent with CORTEX 2.0

- [ ] **Task 1.7:** Update documentation
  - **Files:** `docs/agents/interactive-planner.md`, `docs/api/interactive-planning-api.md`
  - **LOC:** ~150 lines markdown
  - **Owner:** Developer 1
  - **Dependencies:** Task 1.6 complete
  - **Deliverables:**
    - [ ] Agent documentation with examples
    - [ ] API reference for planning utilities
    - [ ] Usage guide for developers
  - **Completion Criteria:** Docs published, examples working
  - **Gap Analysis:** ⚠️ **GAP FOUND** - Need to integrate with 2.0 doc generation system
    - **Fix:** Use 2.0 Phase 7 doc generation (Week 21-24) to auto-generate
    - **Action:** Manual docs for now, auto-generate in Phase 7

#### Week 19: Command Discovery Phase 1 (Parallel)

**Priority:** 🟡 HIGH (Enables feature discoverability)

##### Day 1-2: HelpAgent Core

- [ ] **Task 2.1:** Build `HelpAgent`
  - **File:** `src/cortex_agents/corpus_callosum/help_agent.py`
  - **LOC:** ~180 lines
  - **Owner:** Developer 2
  - **Dependencies:** None (can start immediately)
  - **Deliverables:**
    - [ ] `/help` basic command (list all commands)
    - [ ] `/help all` show detailed info
    - [ ] `/help search <keyword>` functionality
    - [ ] `/help <command>` show specific command help
  - **Tests:**
    - [ ] `test_help_command_basic` (unit)
    - [ ] `test_help_all` (unit)
    - [ ] `test_help_search` (unit)
    - [ ] `test_help_specific_command` (unit)
  - **Completion Criteria:** All help commands functional, search works
  - **Gap Analysis:** ✅ No gaps - design in `CORTEX-COMMAND-DISCOVERY-SYSTEM.md`

##### Day 3: Intent Router Enhancement

- [ ] **Task 2.2:** Enhance `IntentRouter` for command suggestions
  - **File:** `src/cortex_agents/left_brain/intent_router.py` (modify existing)
  - **LOC:** +100 lines (extension)
  - **Owner:** Developer 2
  - **Dependencies:** Task 2.1 complete
  - **Deliverables:**
    - [ ] Detect natural language requests
    - [ ] Suggest command equivalent
    - [ ] Progressive learning (reduce tips over time)
    - [ ] User preference tracking
  - **Tests:**
    - [ ] `test_suggest_command_from_natural_language` (unit)
    - [ ] `test_progressive_tip_reduction` (unit)
    - [ ] `test_preference_respect` (integration)
  - **Completion Criteria:** Suggests relevant commands, respects preferences
  - **Gap Analysis:** ⚠️ **GAP FOUND** - IntentRouter needs Tier 2 integration for learning
    - **Fix:** See Task 2.3 (Tier 2 extension)

##### Day 4: Tier 2 Knowledge Graph Extension

- [ ] **Task 2.3:** Extend Tier 2 knowledge graph for command analytics
  - **File:** `cortex-brain/knowledge-graph.yaml` (modify existing)
  - **LOC:** +50 lines YAML
  - **Owner:** Developer 2
  - **Dependencies:** Task 2.2 complete
  - **Deliverables:**
    - [ ] New section: `command_usage_analytics`
    - [ ] Track usage frequency per command
    - [ ] Track discovery method (natural language, /help, suggestion, etc.)
    - [ ] Track last used timestamp
    - [ ] User preference flags (show_tips, suggestion_frequency)
  - **Tests:**
    - [ ] `test_track_command_usage` (integration)
    - [ ] `test_query_usage_analytics` (unit)
    - [ ] `test_update_preferences` (unit)
  - **Completion Criteria:** Usage tracked in Tier 2, queries <100ms
  - **Gap Analysis:** ✅ No gaps - analytics designed in Command Discovery docs

##### Day 5: Unit Testing & Integration

- [ ] **Task 2.4:** Comprehensive testing for Command Discovery Phase 1
  - **Files:** `tests/cortex_agents/corpus_callosum/test_help_agent.py`, etc.
  - **LOC:** ~200 lines tests
  - **Owner:** Developer 2 + QA
  - **Dependencies:** Tasks 2.1-2.3 complete
  - **Deliverables:**
    - [ ] 85%+ code coverage
    - [ ] All unit tests passing
    - [ ] Integration test: Natural language → command suggestion → help lookup
  - **Tests:**
    - [ ] All subtasks 2.1-2.3 tests passing (15+ tests)
    - [ ] `test_full_discovery_flow` (integration)
  - **Completion Criteria:** 85%+ coverage, 0 test failures
  - **Gap Analysis:** ✅ No gaps - consistent with CORTEX 2.0 testing standards

#### Week 20: Conversation Flow & Context Awareness

##### Day 1-2: State Machine Implementation

- [ ] **Task 3.1:** Implement Interactive Planning state machine
  - **File:** `src/cortex_agents/right_brain/interactive_planner.py` (extend Task 1.1)
  - **LOC:** +150 lines
  - **Owner:** Developer 1
  - **Dependencies:** Week 19 Task 1.1-1.5 complete
  - **Deliverables:**
    - [ ] Question → Answer → Next Question loop
    - [ ] User controls: skip, done, back, abort
    - [ ] Max 5 questions enforcement
    - [ ] Early termination handling
  - **Tests:**
    - [ ] `test_question_answer_loop` (integration)
    - [ ] `test_user_skip_command` (unit)
    - [ ] `test_early_termination` (integration)
    - [ ] `test_max_questions_enforced` (unit)
  - **Completion Criteria:** State machine runs full cycle, user controls work
  - **Gap Analysis:** ✅ No gaps - state machine designed in Interactive Planning docs

##### Day 3: Plan Generation

- [ ] **Task 3.2:** Build plan generation logic
  - **File:** `src/cortex_agents/right_brain/plan_generator.py`
  - **LOC:** ~200 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 3.1 complete
  - **Deliverables:**
    - [ ] Synthesize answers into context
    - [ ] Generate detailed implementation plan
    - [ ] Include time estimates
    - [ ] Phase breakdown (Plan → Execute → Test → Document)
  - **Tests:**
    - [ ] `test_synthesize_answers` (unit)
    - [ ] `test_generate_plan_with_phases` (unit)
    - [ ] `test_time_estimation` (unit)
  - **Completion Criteria:** Generates quality plans with realistic estimates
  - **Gap Analysis:** ⚠️ **GAP FOUND** - Plan templates not defined
    - **Fix:** Create `plan_templates.yaml` in Tier 2 (see Task 3.4)

- [ ] **Task 3.3:** Add user approval workflow
  - **File:** `src/cortex_agents/right_brain/interactive_planner.py` (extend)
  - **LOC:** +100 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 3.2 complete
  - **Deliverables:**
    - [ ] Present plan for review
    - [ ] Handle modifications (user edits plan)
    - [ ] Save for later option
    - [ ] Begin implementation handoff to Executor agent
  - **Tests:**
    - [ ] `test_plan_approval` (integration)
    - [ ] `test_plan_modification` (unit)
    - [ ] `test_save_for_later` (integration)
    - [ ] `test_handoff_to_executor` (integration)
  - **Completion Criteria:** Approval workflow functional, handoff works
  - **Gap Analysis:** ✅ No gaps - workflow designed

##### Day 4: Context Analyzer

- [ ] **Task 3.4:** Build `ContextAnalyzer`
  - **File:** `src/cortex_agents/right_brain/context_analyzer.py`
  - **LOC:** ~220 lines
  - **Owner:** Developer 2
  - **Dependencies:** Week 19 Task 2.1-2.4 complete
  - **Deliverables:**
    - [ ] File-based suggestions (test.py → `/run-tests`)
    - [ ] Time-based suggestions (24h idle → `/resume`)
    - [ ] Git activity analysis (recent commits → suggest relevant commands)
    - [ ] Current task status (in progress → suggest related commands)
    - [ ] Create `plan_templates.yaml` in Tier 2 (fix for Task 3.2 gap)
  - **Tests:**
    - [ ] `test_file_based_suggestions` (unit)
    - [ ] `test_time_based_suggestions` (unit)
    - [ ] `test_git_activity_analysis` (integration)
    - [ ] `test_task_status_suggestions` (integration)
  - **Completion Criteria:** Context detection 85%+ accurate, suggestions relevant
  - **Gap Analysis:** ✅ No gaps - context analysis designed

##### Day 5: Integration Testing

- [ ] **Task 3.5:** Week 20 integration tests
  - **Files:** `tests/integration/test_interactive_planning_e2e.py`
  - **LOC:** ~250 lines tests
  - **Owner:** Developer 1 + Developer 2 + QA
  - **Dependencies:** Tasks 3.1-3.4 complete
  - **Deliverables:**
    - [ ] Full planning session (question → answer → plan → approval)
    - [ ] Context-aware command suggestions during planning
    - [ ] Error recovery scenarios
    - [ ] Performance validation (<2s response time)
  - **Tests:**
    - [ ] `test_full_planning_session_e2e` (integration)
    - [ ] `test_context_suggestions_during_planning` (integration)
    - [ ] `test_error_recovery` (integration)
    - [ ] `test_performance_under_load` (performance)
  - **Completion Criteria:** E2E tests passing, performance targets met
  - **Gap Analysis:** ✅ No gaps

---

### 🔧 Week 21-22: Command Integration & Learning (CORTEX 2.1 Week 3-4)

**Parallel with:** CORTEX 2.0 Phase 7 (Documentation Generation)

#### Week 21: Command Registration & Natural Language

##### Day 1-2: Command Router Integration

- [ ] **Task 4.1:** Register 7 new commands in universal operations system
  - **File:** `cortex-operations.yaml` (modify existing)
  - **LOC:** +200 lines YAML (already done in previous increment!)
  - **Owner:** Developer 1
  - **Dependencies:** Week 20 complete
  - **Status:** ✅ **COMPLETE** (done in integration analysis increment)
  - **Deliverables:**
    - [x] `/CORTEX, refresh cortex story`
    - [x] `/CORTEX, let's plan a feature` ⭐
    - [x] `/CORTEX, architect a solution`
    - [x] `/CORTEX, refactor this module`
    - [x] `/CORTEX, run brain protection`
    - [x] `/CORTEX, run tests`
    - [x] `/CORTEX, generate documentation`
  - **Tests:**
    - [ ] `test_all_commands_registered` (unit)
    - [ ] `test_command_discovery_via_help` (integration)
  - **Completion Criteria:** All commands functional via `/help` and natural language
  - **Gap Analysis:** ✅ No gaps - operations registry already updated

- [ ] **Task 4.2:** Add natural language equivalents
  - **File:** `src/cortex_agents/left_brain/intent_router.py` (extend)
  - **LOC:** +80 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 4.1 complete
  - **Deliverables:**
    - [ ] Map natural phrases to commands
      - "plan a feature" → `/CORTEX, let's plan a feature`
      - "design architecture" → `/CORTEX, architect a solution`
      - "refactor code" → `/CORTEX, refactor this module`
    - [ ] Context-aware expansion (use conversation history)
    - [ ] Alias support (multiple phrases → same command)
  - **Tests:**
    - [ ] `test_natural_language_to_command_mapping` (unit)
    - [ ] `test_context_aware_expansion` (integration)
    - [ ] `test_alias_support` (unit)
  - **Completion Criteria:** Natural language correctly maps to commands 95%+ accuracy
  - **Gap Analysis:** ✅ No gaps

##### Day 3: Tier 2 Learning System

- [ ] **Task 4.3:** Implement preference extraction
  - **File:** `src/tier2/preference_extractor.py`
  - **LOC:** ~180 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 4.2 complete
  - **Deliverables:**
    - [ ] Extract patterns from planning sessions
    - [ ] Identify user preferences (auth type, schema changes, testing style)
    - [ ] Build confidence scores for preferences
    - [ ] Store in Tier 2 knowledge graph
  - **Tests:**
    - [ ] `test_extract_auth_preference` (unit)
    - [ ] `test_confidence_scoring` (unit)
    - [ ] `test_store_in_tier2` (integration)
  - **Completion Criteria:** Extracts preferences with 85%+ confidence after 3+ sessions
  - **Gap Analysis:** ⚠️ **GAP FOUND** - Preference storage schema not defined in Tier 2
    - **Fix:** Add `user_preferences` section to `knowledge-graph.yaml` (see Task 4.4)

- [ ] **Task 4.4:** Build pattern recognition system
  - **File:** `src/tier2/pattern_recognizer.py`
  - **LOC:** ~150 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 4.3 complete
  - **Deliverables:**
    - [ ] Detect recurring preferences across sessions
    - [ ] Learn typical question count needed per user
    - [ ] Track success rates of planning sessions
    - [ ] Adapt questioning strategy based on patterns
    - [ ] Add `user_preferences` section to `knowledge-graph.yaml` (fix for Task 4.3)
  - **Tests:**
    - [ ] `test_detect_recurring_preference` (integration)
    - [ ] `test_adapt_question_count` (unit)
    - [ ] `test_success_rate_tracking` (unit)
  - **Completion Criteria:** Adapts behavior after 5+ sessions, improves accuracy 10%+
  - **Gap Analysis:** ✅ No gaps (after fix applied)

##### Day 4-5: Adaptive Questioning

- [ ] **Task 4.5:** Implement adaptive questioning logic
  - **File:** `src/cortex_agents/right_brain/interactive_planner.py` (extend)
  - **LOC:** +120 lines
  - **Owner:** Developer 1
  - **Dependencies:** Task 4.4 complete
  - **Deliverables:**
    - [ ] Use learned preferences as defaults
    - [ ] Skip questions if pattern confidence >90%
    - [ ] Adjust question count based on user feedback
    - [ ] Improve over time (machine learning mindset)
  - **Tests:**
    - [ ] `test_use_preference_as_default` (integration)
    - [ ] `test_skip_high_confidence_questions` (unit)
    - [ ] `test_adapt_to_feedback` (integration)
    - [ ] `test_improvement_over_time` (long-term simulation)
  - **Completion Criteria:** Skips 40%+ questions after 10+ sessions, maintains 90%+ accuracy
  - **Gap Analysis:** ✅ No gaps

#### Week 22: Visual Enhancements & Polish

##### Day 1-2: Quick Reference Sidebar (VS Code Extension)

- [ ] **Task 5.1:** Build quick reference sidebar widget
  - **File:** `cortex-extension/src/views/quickReference.ts`
  - **LOC:** ~300 lines TypeScript
  - **Owner:** Developer 2 + UX Designer
  - **Dependencies:** Week 21 complete
  - **Deliverables:**
    - [ ] Searchable command list
    - [ ] Favorites system (star commands)
    - [ ] Collapsible categories (Planning, Execution, Testing, etc.)
    - [ ] Click to insert command in chat
    - [ ] Daily tips (random tip on open)
  - **Tests:**
    - [ ] `test_sidebar_renders` (E2E)
    - [ ] `test_search_functionality` (unit)
    - [ ] `test_favorites_system` (integration)
    - [ ] `test_click_to_insert` (E2E)
  - **Completion Criteria:** Sidebar functional, search works, favorites save
  - **Gap Analysis:** ⚠️ **GAP FOUND** - VS Code extension architecture not defined
    - **Fix:** Create extension architecture doc (see Task 5.5)

- [ ] **Task 5.2:** Status bar integration
  - **File:** `cortex-extension/src/statusBar.ts`
  - **LOC:** ~100 lines TypeScript
  - **Owner:** Developer 2
  - **Dependencies:** Task 5.1 complete
  - **Deliverables:**
    - [ ] Show last command used
    - [ ] Quick command palette trigger (click to open)
    - [ ] Usage statistics tooltip
  - **Tests:**
    - [ ] `test_status_bar_shows_last_command` (E2E)
    - [ ] `test_click_opens_palette` (E2E)
    - [ ] `test_usage_stats_tooltip` (unit)
  - **Completion Criteria:** Status bar functional, updates correctly
  - **Gap Analysis:** ✅ No gaps

##### Day 3: Onboarding Tour

- [ ] **Task 5.3:** Create onboarding tour for first-time users
  - **File:** `cortex-extension/src/onboarding/tour.ts`
  - **LOC:** ~200 lines TypeScript
  - **Owner:** Developer 2 + UX Designer
  - **Dependencies:** Task 5.2 complete
  - **Deliverables:**
    - [ ] Interactive tutorial (5-step walkthrough)
    - [ ] Milestone-based education (unlock tips after achievements)
    - [ ] Skip/dismiss options
    - [ ] Progress tracking
  - **Tests:**
    - [ ] `test_tour_starts_for_new_users` (E2E)
    - [ ] `test_skip_functionality` (E2E)
    - [ ] `test_milestone_unlocks` (integration)
  - **Completion Criteria:** Tour engaging, completion rate >60%
  - **Gap Analysis:** ✅ No gaps

##### Day 4: Visual Polish

- [ ] **Task 5.4:** Visual design and polish
  - **Files:** `cortex-extension/src/styles/*.css`
  - **LOC:** ~150 lines CSS
  - **Owner:** UX Designer + Developer 2
  - **Dependencies:** Tasks 5.1-5.3 complete
  - **Deliverables:**
    - [ ] Icons and styling (consistent with VS Code theme)
    - [ ] Animations (subtle, professional)
    - [ ] Responsive design (works on all screen sizes)
    - [ ] Accessibility (WCAG 2.1 AA compliant)
  - **Tests:**
    - [ ] `test_accessibility_compliance` (automated scan)
    - [ ] `test_responsive_design` (visual regression)
  - **Completion Criteria:** Polished UI, accessibility compliant
  - **Gap Analysis:** ✅ No gaps

##### Day 5: Error Handling & Performance

- [ ] **Task 5.5:** Error handling and performance optimization
  - **Files:** Multiple (error boundaries, caching, optimization)
  - **LOC:** ~150 lines
  - **Owner:** Developer 1 + Developer 2
  - **Dependencies:** Tasks 5.1-5.4 complete
  - **Deliverables:**
    - [ ] Graceful failure recovery
    - [ ] Clear error messages
    - [ ] Retry mechanisms
    - [ ] Fallback to standard planning (if interactive fails)
    - [ ] Response time <2 seconds
    - [ ] Memory efficiency
    - [ ] Create `CORTEX-EXTENSION-ARCHITECTURE.md` (fix for Task 5.1 gap)
  - **Tests:**
    - [ ] `test_error_recovery` (integration)
    - [ ] `test_fallback_to_standard_planning` (integration)
    - [ ] `test_response_time` (performance)
    - [ ] `test_memory_usage` (performance)
  - **Completion Criteria:** Errors handled gracefully, performance targets met
  - **Gap Analysis:** ⚠️ **GAP FOUND** - Extension architecture doc missing
    - **Fix:** Added to this task deliverables

---

### 🧪 Week 23-24: Integration & Polish (CORTEX 2.1 Week 5-6)

**Parallel with:** Complete CORTEX 2.0 Phase 7 (Documentation)

#### Week 23: Full System Integration

##### Day 1-2: Integration Testing

- [ ] **Task 6.1:** Comprehensive integration testing
  - **Files:** `tests/integration/test_cortex_2.1_full_system.py`
  - **LOC:** ~400 lines tests
  - **Owner:** QA Engineer + All Developers
  - **Dependencies:** Week 22 complete
  - **Deliverables:**
    - [ ] Interactive planning + command discovery (combined workflow)
    - [ ] End-to-end workflows (10 scenarios)
    - [ ] Cross-component communication
    - [ ] Performance under load (100 concurrent users)
  - **Tests:**
    - [ ] `test_combined_planning_discovery` (E2E)
    - [ ] `test_scenario_add_authentication` (E2E)
    - [ ] `test_scenario_refactor_module` (E2E)
    - [ ] `test_scenario_debug_issue` (E2E)
    - [ ] `test_performance_under_load` (performance)
    - [ ] 6 more scenario tests (see design docs)
  - **Completion Criteria:** All scenarios pass, performance meets targets
  - **Gap Analysis:** ✅ No gaps

##### Day 3: Brain Protection Validation

- [ ] **Task 6.2:** Brain protection validation
  - **Files:** `tests/tier0/test_brain_protection_2.1.py`
  - **LOC:** ~150 lines tests
  - **Owner:** QA Engineer
  - **Dependencies:** Task 6.1 complete
  - **Deliverables:**
    - [ ] Validate all Tier 0 rules enforced
    - [ ] No brain data corruption
    - [ ] Schema integrity checks
    - [ ] Rollback testing
  - **Tests:**
    - [ ] `test_tier0_rules_enforced` (integration)
    - [ ] `test_no_data_corruption` (integration)
    - [ ] `test_schema_integrity` (unit)
    - [ ] `test_migration_rollback` (integration)
  - **Completion Criteria:** All brain protection tests pass, 0 vulnerabilities
  - **Gap Analysis:** ✅ No gaps - brain protection is CORTEX 2.0 foundation

##### Day 4: Migration Testing

- [ ] **Task 6.3:** Test database migrations
  - **Files:** `tests/tier1/test_migrations_2.1.py`
  - **LOC:** ~100 lines tests
  - **Owner:** Developer 1
  - **Dependencies:** Task 6.2 complete
  - **Deliverables:**
    - [ ] Test fresh install (no existing brain)
    - [ ] Test upgrade from CORTEX 2.0 (existing brain)
    - [ ] Test rollback scenarios
    - [ ] Data integrity validation
  - **Tests:**
    - [ ] `test_fresh_install` (integration)
    - [ ] `test_upgrade_from_2.0` (integration)
    - [ ] `test_rollback_to_2.0` (integration)
    - [ ] `test_data_integrity` (integration)
  - **Completion Criteria:** Migrations work both directions, no data loss
  - **Gap Analysis:** ⚠️ **GAP FOUND** - Migration strategy not documented
    - **Fix:** See Task 6.5 (migration guide)

##### Day 5: User Acceptance Testing (UAT)

- [ ] **Task 6.4:** Internal UAT with team
  - **Files:** `docs/testing/UAT-CORTEX-2.1.md`
  - **LOC:** ~50 lines markdown (test plan)
  - **Owner:** QA Engineer + Product Manager
  - **Dependencies:** Task 6.3 complete
  - **Deliverables:**
    - [ ] UAT test plan (10 scenarios)
    - [ ] Internal team testing (5 users)
    - [ ] Feedback collection
    - [ ] Bug triage and prioritization
  - **Tests:**
    - [ ] Execute all 10 UAT scenarios
    - [ ] Collect feedback forms
    - [ ] Document all issues found
  - **Completion Criteria:** UAT complete, issues documented, P1/P2 bugs fixed
  - **Gap Analysis:** ✅ No gaps

#### Week 24: Documentation & Beta Testing

##### Day 1-2: User Documentation

- [ ] **Task 6.5:** Complete user documentation
  - **Files:** `docs/user/interactive-planning-guide.md`, `docs/user/command-discovery-guide.md`
  - **LOC:** ~300 lines markdown
  - **Owner:** Developer 1 + UX Designer
  - **Dependencies:** Task 6.4 complete
  - **Deliverables:**
    - [ ] Interactive planning user guide
    - [ ] Command discovery user guide
    - [ ] Tutorial videos (3x 5-min videos)
    - [ ] FAQ (20+ questions)
    - [ ] Migration guide 2.0 → 2.1 (fix for Task 6.3 gap)
  - **Tests:**
    - [ ] Documentation review (peer review)
    - [ ] Link validation
    - [ ] Example code tested
  - **Completion Criteria:** Docs published, videos uploaded, FAQ complete
  - **Gap Analysis:** ✅ No gaps (after fix applied)

##### Day 3-4: Beta Testing

- [ ] **Task 6.6:** Beta testing with external users
  - **Files:** `docs/testing/BETA-TEST-CORTEX-2.1.md`
  - **LOC:** ~100 lines markdown (beta plan)
  - **Owner:** QA Engineer + Product Manager
  - **Dependencies:** Task 6.5 complete
  - **Deliverables:**
    - [ ] Beta user recruitment (10 users)
    - [ ] Beta test plan (20 scenarios)
    - [ ] Feedback surveys
    - [ ] Bug tracking and fixes
    - [ ] Daily check-ins with beta users
  - **Tests:**
    - [ ] Execute 20 beta scenarios
    - [ ] Monitor error rates
    - [ ] Collect satisfaction scores
  - **Completion Criteria:** Beta complete, satisfaction >4.0/5, P1/P2 bugs fixed
  - **Gap Analysis:** ✅ No gaps

##### Day 5: Final Polish & Release Prep

- [ ] **Task 6.7:** Final polish and release preparation
  - **Files:** Multiple (bug fixes, performance tuning, release notes)
  - **LOC:** Variable (bug fixes)
  - **Owner:** All team members
  - **Dependencies:** Task 6.6 complete
  - **Deliverables:**
    - [ ] Fix all P1 bugs from beta testing
    - [ ] Performance tuning based on beta feedback
    - [ ] Release notes (what's new, breaking changes, migration guide)
    - [ ] Deployment runbook
    - [ ] Support playbook
  - **Tests:**
    - [ ] Final regression test suite (all 400+ tests)
    - [ ] Performance benchmarks
    - [ ] Smoke tests on staging
  - **Completion Criteria:** All P1 bugs fixed, performance targets met, ready to ship
  - **Gap Analysis:** ✅ No gaps

---

## 📊 Completion Criteria & Success Metrics

### Feature Completeness

- [ ] **Interactive Planning:** 100% of design implemented
  - [ ] InteractivePlannerAgent functional
  - [ ] QuestionGenerator, AnswerParser, QuestionFilter working
  - [ ] Tier 1 schema extended
  - [ ] State machine operational
  - [ ] Plan generation and approval working
  - [ ] Tier 2 learning implemented
  - [ ] Adaptive questioning functional

- [ ] **Command Discovery:** 100% of design implemented
  - [ ] HelpAgent functional
  - [ ] Intent router enhanced
  - [ ] Context analyzer working
  - [ ] Quick reference sidebar operational
  - [ ] Status bar integration complete
  - [ ] Onboarding tour functional
  - [ ] Visual polish complete

- [ ] **Operations Integration:** All commands registered and functional
  - [ ] 7 new commands in `cortex-operations.yaml`
  - [ ] Natural language equivalents working
  - [ ] Command discovery via `/help` functional

### Quality Metrics

- [ ] **Test Coverage:** ≥85% code coverage
  - [ ] Unit tests: 150+ tests passing
  - [ ] Integration tests: 50+ tests passing
  - [ ] E2E tests: 20+ scenarios passing
  - [ ] Performance tests: All benchmarks met

- [ ] **Performance:**
  - [ ] Question generation: <2 seconds
  - [ ] Plan generation: <3 seconds
  - [ ] Command search: <500ms
  - [ ] Sidebar load: <200ms
  - [ ] Memory usage: <100MB additional

- [ ] **User Satisfaction:**
  - [ ] Internal UAT satisfaction: >4.0/5
  - [ ] Beta user satisfaction: >4.0/5
  - [ ] Plan accuracy: >90% (vs 70% baseline)
  - [ ] Command discovery rate: >90% within 1 week
  - [ ] Question efficiency: <60% questions asked (vs 100% without filtering)

### Integration Success

- [ ] **CORTEX 2.0 Compatibility:**
  - [ ] No breaking changes to 2.0 features
  - [ ] Backward compatible with existing brains
  - [ ] Migration path documented and tested
  - [ ] 2.0 performance not degraded

- [ ] **Phase 6-7 Coordination:**
  - [ ] No conflicts with 2.0 Phase 6 work (performance optimization)
  - [ ] 2.1 command discovery enhances 2.0 Phase 7 (documentation)
  - [ ] Shared resources managed effectively
  - [ ] Timeline met (Week 19-24)

### Documentation Complete

- [ ] **Technical Docs:**
  - [ ] Architecture docs updated
  - [ ] API reference complete
  - [ ] Plugin development guide updated
  - [ ] Migration guide 2.0 → 2.1 complete

- [ ] **User Docs:**
  - [ ] Interactive planning guide published
  - [ ] Command discovery guide published
  - [ ] Tutorial videos (3x) published
  - [ ] FAQ (20+ questions) complete

- [ ] **Internal Docs:**
  - [ ] Deployment runbook complete
  - [ ] Support playbook complete
  - [ ] Beta test results documented

---

## 🚨 Risk Management

### Identified Risks

#### Risk 1: Resource Conflicts with Phase 6-7 🟡 MEDIUM

**Mitigation:**
- Clear separation of work (2.1 = new code, 2.0 Phase 6 = optimization of existing)
- Shared Developer 3 focuses on non-conflicting tasks
- Daily standups to coordinate
- **Contingency:** Delay 2.1 by 1 week if conflicts arise

#### Risk 2: Tier 1 Schema Migration Issues 🟡 MEDIUM

**Mitigation:**
- Comprehensive migration testing (fresh install + upgrade)
- Rollback plan tested
- Data integrity validation
- **Contingency:** Rollback to 2.0, fix migrations, retry

#### Risk 3: VS Code Extension Complexity 🟢 LOW

**Mitigation:**
- UX designer dedicated to extension work
- Incremental development (sidebar → status bar → onboarding)
- E2E testing throughout
- **Contingency:** Ship with basic extension, enhance in 2.2

#### Risk 4: User Adoption (Feature Discovery) 🟢 LOW

**Mitigation:**
- Command discovery system ensures discoverability
- Onboarding tour for new users
- In-app tips and education
- **Contingency:** Enhanced marketing, more tutorials

#### Risk 5: Performance Degradation 🟢 LOW

**Mitigation:**
- Performance testing throughout (Week 23)
- Database query optimization
- Caching strategies
- **Contingency:** Feature flags to disable if performance issues

### Monitoring & Early Warning

- [ ] **Daily Metrics:**
  - [ ] Test pass rate (target: >95%)
  - [ ] Code coverage (target: >85%)
  - [ ] Bugs found vs fixed (target: fix rate > find rate by Week 24)
  - [ ] Response time benchmarks (target: all <2s)

- [ ] **Weekly Reviews:**
  - [ ] Progress vs timeline (target: on track)
  - [ ] Resource utilization (target: no overload)
  - [ ] Risk register review (target: no new HIGH risks)
  - [ ] Stakeholder updates

---

## 🎯 Next Steps (Before Week 19)

### Immediate Actions (Week 11-18)

1. **Week 11-12:** Complete CORTEX 2.0 Phase 5 (Testing)
   - [ ] Finish Phase 5.1-5.5 (12-15 hours remaining)
   - [ ] Achieve 100% test pass rate
   - [ ] Document Phase 5 completion

2. **Week 13-16:** Complete CORTEX 2.0 Phase 4 Alternative Work
   - [ ] Complete any remaining Phase 4 work pulled forward
   - [ ] Finalize ambient capture enhancements
   - [ ] Validate "continue" success rate (target: 92%+)

3. **Week 17-18:** CORTEX 2.1 Preparation
   - [ ] Review all CORTEX 2.1 design documents
   - [ ] Set up development environment for 2.1
   - [ ] Recruit beta testers (10 users)
   - [ ] Finalize resource allocation
   - [ ] Create detailed sprint plans for Week 19-24

### Team Preparation

- [ ] **Developers:**
  - [ ] Review `CORTEX-2.1-INTERACTIVE-PLANNING.md` (Developer 1)
  - [ ] Review `CORTEX-COMMAND-DISCOVERY-SYSTEM.md` (Developer 2)
  - [ ] Review `CORTEX-2.1-IMPLEMENTATION-ROADMAP.md` (all)
  - [ ] Set up local development environments
  - [ ] Practice TDD workflow

- [ ] **QA Engineer:**
  - [ ] Review test strategy for 2.1
  - [ ] Set up test automation tools
  - [ ] Create test data sets
  - [ ] Prepare UAT and beta test plans

- [ ] **UX Designer:**
  - [ ] Finalize visual designs for sidebar, status bar, onboarding
  - [ ] Create icon assets
  - [ ] Prepare tutorial video scripts
  - [ ] Review accessibility guidelines

---

## 📝 Gap Summary & Fixes Applied

### Gaps Identified During Checklist Creation

1. ⚠️ **Gap: Question Templates Missing from Tier 2**
   - **Found in:** Task 1.2 (Question Generator)
   - **Fix:** Added `question_templates` table to Task 1.5 (Tier 1 schema extension)
   - **Status:** ✅ Fixed

2. ⚠️ **Gap: Plan Templates Not Defined**
   - **Found in:** Task 3.2 (Plan Generation)
   - **Fix:** Added `plan_templates.yaml` creation to Task 3.4 (Context Analyzer)
   - **Status:** ✅ Fixed

3. ⚠️ **Gap: IntentRouter Needs Tier 2 Integration**
   - **Found in:** Task 2.2 (Intent Router Enhancement)
   - **Fix:** Created Task 2.3 (Tier 2 Knowledge Graph Extension)
   - **Status:** ✅ Fixed

4. ⚠️ **Gap: Preference Storage Schema Not Defined**
   - **Found in:** Task 4.3 (Preference Extraction)
   - **Fix:** Added `user_preferences` section to Task 4.4 (Pattern Recognition)
   - **Status:** ✅ Fixed

5. ⚠️ **Gap: VS Code Extension Architecture Not Defined**
   - **Found in:** Task 5.1 (Quick Reference Sidebar)
   - **Fix:** Added `CORTEX-EXTENSION-ARCHITECTURE.md` to Task 5.5 deliverables
   - **Status:** ✅ Fixed

6. ⚠️ **Gap: Migration Strategy Not Documented**
   - **Found in:** Task 6.3 (Migration Testing)
   - **Fix:** Added migration guide to Task 6.5 (User Documentation)
   - **Status:** ✅ Fixed

7. ⚠️ **Gap: Documentation Integration with 2.0 System**
   - **Found in:** Task 1.7 (Update Documentation)
   - **Fix:** Manual docs for Week 19-20, auto-generate via 2.0 Phase 7 (Week 21-24)
   - **Status:** ✅ Fixed

### All Gaps Resolved ✅

**Total Gaps Found:** 7  
**Total Gaps Fixed:** 7  
**Gap Resolution Rate:** 100%

---

## 🎉 Checklist Summary

**Total Tasks:** 35 tasks across 6 weeks  
**Total Estimated LOC:** ~5,500 lines production code + ~2,000 lines tests  
**Total Tests:** 200+ new tests  
**Resource Requirements:** 3 developers + 1 QA + 1 UX = 24 person-weeks  
**Timeline:** Week 19-24 (6 weeks, parallel with CORTEX 2.0 Phase 6-7)  
**Risk Level:** 🟢 LOW (all risks mitigated, no blockers)

**Readiness:** ✅ READY TO START WEEK 19

---

*Last Updated: 2025-11-09 | Created for CORTEX 2.1 Implementation*  
*Companion Documents: CORTEX-2.0-2.1-INTEGRATION-ANALYSIS.md, cortex-operations.yaml, STATUS.md*  
*Next Review: Week 18 (before implementation starts)*
