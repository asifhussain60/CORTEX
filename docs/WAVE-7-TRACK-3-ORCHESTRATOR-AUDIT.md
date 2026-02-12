# Wave 7 Track 3: Support Layer Consolidation Analysis
**Generated:** 2026-02-11 | **Phase:** Orchestrator Inventory Audit (Track 3 Phase 1)  
**Status:** AUDIT COMPLETE | **Action:** Begin RED Phase

---

## Current Landscape (23 Registered + Additional Domain/Support)

### Core Orchestrators (8 - PROTECTED ✅)
```
✅ MasterOrchestrator       (priority 10)   - Central orchestration
✅ IntentRouter             (priority 20)   - Intent classification
✅ TDDOrchestrator          (priority 30)   - Test-driven execution
✅ WorkflowOrchestrator     (priority 40)   - Workflow execution
✅ InteractionOrchestrator  (priority 50)   - User interaction
✅ EnforcementOrchestrator  (priority ?)    - Governance + 7 agents
✅ LENSSynthesis            (priority ?)    - Code analysis (L.E.N.S.)
✅ IncrementalTaskDecomposer (priority ?)   - Task decomposition

CONSOLIDATION: NONE (core layer stable, protecting these 8)
```

### Domain Orchestrators (AFTER Track 2: 6 → Target 4)
```
✅ EnhancedRefactoringOrchestrator_v2  (NEW - Track 2)  - Unified refactoring
✅ DebuggerOrchestrator                (NEW - Track 2)  - Zero-friction debugging
⚪ PlanningOrchestrator                                  - Phase lifecycle
⚪ DocumentationOrchestrator                            - Knowledge synthesis
⚪ RefactoringOrchestrator              (OLD - deprecated in v2)
⚪ DomainKnowledgeMerger                                - Domain inference

CONSOLIDATION TARGET: Consolidate 2 of 6
  • Clarify: PlanningOrchestrator (domain) vs PlanOrchestrator (core)
  • Option 1: Merge into single unified phase manager
  • Option 2: Keep separate (business logic vs planning logic)
  • Decision: INVESTIGATE dependency structure first
```

### Support Orchestrators (12 candidates for consolidation)

**Group A: Onboarding (2 orchestrators)**
```
1. RepositoryOnboardingOrchestrator  (location: ?)     - Repository profiling
2. OnboardingOrchestrator            (support)          - User onboarding
3. SetupOrchestrator                 (support)          - Environment setup

TARGET: Merge into UnifiedOnboardingOrchestrator
PUBLIC API:
  • onboard_repository(path) → RepositoryProfile
  • onboard_user(config) → UserProfile
  • setup_environment(target) → SetupResult
  • validate_onboarding(profile) → ValidationResult

ESTIMATED IMPACT: 3 → 1 (67% reduction in group)
```

**Group B: Analysis & Discovery (3 orchestrators)**
```
1. LENSOrchestrator                  (location: ?)     - LENS analysis pipeline
2. ToolDiscoveryOrchestrator         (core)             - Tool catalog discovery
3. ToolDiscoveryEngine               (core)             - Tool engine

TARGET: Merge into UnifiedAnalysisOrchestrator
PUBLIC API:
  • analyze(code, scope) → LENSResult
  • discover_tools(query) → ToolList
  • analyze_dependencies(code) → DependencyGraph
  • validate_analysis(result) → QualityScore

ESTIMATED IMPACT: 3 → 1 (67% reduction in group)
```

**Group C: Quality Assurance (4 orchestrators)**
```
1. RecommendationGate               (location: ?)      - Challenge generation
2. ChallengeEngine                  (core)             - Challenge engine
3. MetaAuditOrchestrator            (location: ?)     - Holistic audit
4. CodeReviewOrchestrator (old)      (support)         - DEPRECATED (merged into Enhanced v2)

TARGET: Merge into UnifiedQualityAssuranceOrchestrator
PUBLIC API:
  • challenge_proposal(request) → ChallengeResult
  • generate_recommendations(code) → RecommendationList
  • audit_holistically(target) → AuditReport
  • validate_quality(code) → QualityResult

ESTIMATED IMPACT: 4 → 1 (75% reduction in group)
```

**Group D: Learning & Education (2 orchestrators)**
```
1. EducationalOrchestrator          (location: ?)     - Prompt engineering, learning
2. BusinessLanguageOrchestrator     (support)          - Business context

TARGET: Merge into UnifiedDiscoveryOrchestrator
PUBLIC API:
  • learn_feature(topic) → LearningModule
  • recommend_learning_path(goal) → CoursePath
  • synthesize_business_context(code) → BusinessInsight

ESTIMATED IMPACT: 2 → 1 (50% reduction in group)
```

**Group E: Deprecated/Duplicate (3 orchestrators)**
```
1. CodeReviewOrchestrator (old)      - DEPRECATED (moved to Enhanced v2)
2. SecurityReviewEngine (old)        - DEPRECATED (moved to Enhanced v2)
3. RefactoringOrchestrator (old)     - DEPRECATED (moved to Enhanced v2)

ACTION: Create deprecation notices, move to cortex/orchestrators/deprecated/
Update imports in wiring contract
Document migration paths

ESTIMATED IMPACT: 3 → 0 (complete removal)
```

### Support Orchestrators Not in Scope (Keep/Refactor Later)
```
⚪ BrainFlushOrchestrator            - Domain-specific (CORTEX_Brain management)
⚪ BrainHealthOrchestrator           - Domain-specific (health monitoring)
⚪ BulkDigestOrchestrator            - Specialized (batch operations)
⚪ CodeReviewRulesOrchestrator       - Specialized (rule-based review)
⚪ UpgradeOrchestrator               - Infrastructure (version management)
⚪ RollbackOrchestrator              - Infrastructure (recovery)
⚪ ComposedOrchestrator              - Infrastructure (composition)

DECISION: Focus Track 3 on Groups A-E consolidations
Move others to Track 4 (Orphan Cleanup) if time permits
```

---

## Consolidation Timeline (Track 3)

### Phase 1: Analysis (COMPLETE ✅)
- [x] Inventory audit completed
- [x] Consolidation groups identified
- [x] Dependency analysis ready
- [x] Behavioral contract templates prepared

### Phase 2: Group A - UnifiedOnboardingOrchestrator (1 day)
```
Status: ⏳ PENDING
RED: Write 12 behavioral contract tests
GREEN: Implement UnifiedOnboardingOrchestrator
REFACTOR: Optimize + add 8 edge case tests
Coverage Target: 85%+
```

### Phase 3: Group B - UnifiedAnalysisOrchestrator (1 day)
```
Status: ⏳ PENDING
RED: Write 14 behavioral contract tests
GREEN: Implement UnifiedAnalysisOrchestrator
REFACTOR: Optimize + add 10 edge case tests
Coverage Target: 85%+
```

### Phase 4: Group C - UnifiedQualityAssuranceOrchestrator (1-2 days)
```
Status: ⏳ PENDING
RED: Write 16 behavioral contract tests
GREEN: Implement UnifiedQualityAssuranceOrchestrator
REFACTOR: Optimize + add 12 edge case tests
Coverage Target: 85%+
```

### Phase 5: Group D - UnifiedDiscoveryOrchestrator (1 day)
```
Status: ⏳ PENDING
RED: Write 10 behavioral contract tests
GREEN: Implement UnifiedDiscoveryOrchestrator
REFACTOR: Optimize + add 8 edge case tests
Coverage Target: 85%+
```

### Phase 6: Deprecations (0.5 days)
```
Status: ⏳ PENDING
Move old orchestrators to deprecated/ folder
Add __all__ override in old locations (compatibility)
Update wiring contract
Document migration guide
```

### Phase 7: Validation & Commit (0.5 days)
```
Status: ⏳ PENDING
Run combined test suite (Track 1-3)
Verify no regressions
Commit with comprehensive message
Prepare Track 4 execution plan
```

---

## Estimated Reduction

### Before Track 3
```
Core:    8 orchestrators
Domain:  6 orchestrators
Support: 12+ orchestrators
Others:  7+ specialized
━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:   ~33 orchestrators
```

### After Track 3 (Target)
```
Core:    8 orchestrators (unchanged)
Domain:  4 orchestrators (PlanningOrchestrator, DocumentationOrchestrator, Enhanced Refactoring, Debugger)
Support: 4 orchestrators (Onboarding, Analysis, QA, Discovery)
Others:  7+ specialized (unchanged)
━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:   ~23 orchestrators (30% reduction)
```

**vs Wave 7 Start (26 registered):**
```
Before: 26
After:  15-16
REDUCTION: 42%
```

---

## Next Steps

### Immediate (Next Execution)
1. ✅ Audit complete
2. ⏳ Start Phase 2: UnifiedOnboardingOrchestrator (RED phase)
3. ⏳ Write 12 behavioral contract tests (TDD-first)
4. ⏳ Implement orchestrator from test spec
5. ⏳ Achieve 100% test pass rate

### Key Decision Points
- [ ] Clarify: PlanningOrchestrator vs PlanOrchestrator (domain vs core)
- [ ] Location: Find exact files for RepositoryOnboardingOrchestrator, LENSOrchestrator, etc.
- [ ] Dependency: Map all imports before consolidation begins
- [ ] Wiring: Update registration in __wiring_contract__.yaml for each consolidation

### Quality Gates
✅ TDD (tests before code)
✅ Type hints (100%)
✅ Docstrings (100%)
✅ Exception handling (specific)
✅ Git checkpoints (atomic commits)
✅ Governance compliance (CORE-008/011/012/013/026/027/030/035)
✅ Coverage target (85%+)

---

**Status:** READY FOR PHASE 2 EXECUTION  
**Next Command:** Start RED phase for Group A (UnifiedOnboardingOrchestrator)
