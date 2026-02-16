# Wiring Cleanup Plan

**Generated:** 2026-02-16  
**Purpose:** Document deprecated wiring entries for cleanup

## Summary

- **Total Entries:** 71
- **Operational:** 24 (34%)
- **Planned:** 22 (31%) - Future implementations
- **Deprecated:** 25 (35%) - **CLEANUP REQUIRED**

---

## ✅ Operational (24) - Keep

These are implemented and working:

### Analyzers (2)
- GitHistoryAnalyzer
- SecurityThreatAnalyzer

### Core Orchestrators (6)
- InteractionOrchestrator
- IntentRouter
- EnforcementOrchestrator
- TDDOrchestrator
- MasterOrchestrator

### Domain Orchestrators (2)
- PlanningOrchestrator
- ConversationOrchestrator

### Support (14)
- LifecycleHookSystem
- TenantContext
- RegistryHealthMonitor
- AgentMetadataParser
- HealthCheckService
- PrometheusMetrics
- OrchestratorEventBus
- OnboardingOrchestrator
- UpgradeOrchestrator
- RollbackOrchestrator
- SetupOrchestrator
- KnowledgeRepository
- DebuggerOrchestrator
- DashboardOrchestrator
- IntelligenceEngineOrchestrator

---

## 🔵 Planned (22) - Keep

These are intentional placeholders for future phases:

### Support Orchestrators (22)
- OpenTelemetryTracing (needs class implementation)
- HolisticValidationOrchestrator (2 entries - Phase 48+)
- ContextCrystallizationLayer (3 entries - Phase 49)
- EducationalOrchestrator (future)
- VacuumOrchestrator (future)
- InstrumentationOrchestrator (future)
- OrchestratorVisibility (future)
- TechIntelligenceOrchestrator (future)
- DigestEnhancementOrchestrator (future)
- DependencyGraphGenerator (future)
- ChallengeGateOrchestrator (future)
- CortexBrainIntegrationOrchestrator (future)
- PromptEnhancementOrchestrator (future)
- GitHubClientOrchestrator (Phase 52)
- SecurityAnalyzerOrchestrator (Phase 52)
- ReviewEngineOrchestrator (Phase 52)
- IntegrationOrchestrator (Phase 52)
- CCLIntelligenceWarmingOrchestrator (Phase 49)
- CCLIntegrationOrchestrator (Phase 49)

---

## ❌ Deprecated (25) - REMOVE

These entries reference non-existent modules and should be cleaned up:

### Core Orchestrators (7)
1. **ArchitectureGuard** - `cortex.orchestrators.core.architecture_guard`
2. **ComplexityClassifier** - `cortex.orchestrators.core.complexity_classifier`
3. **LENSSynthesis** - `cortex.orchestrators.core.lens_synthesis`
4. **IncrementalTaskDecomposer** - `cortex.orchestrators.planning.incremental_task_decomposer`
5. **WorkflowOrchestrator** - `cortex.orchestrators.core.master_orchestrator_stage_1`
6. **ReviewOrchestrator** - `cortex.orchestrators.core.review_orchestrator`

### Domain Orchestrators (6)
7. **CodeLevelPlanner** - `cortex.orchestrators.domain.code_level_planner`
8. **CoherenceValidator** - `cortex.orchestrators.domain.coherence_validator`
9. **RefactoringOrchestrator** - `cortex.orchestrators.domain.enhanced_refactoring_orchestrator`
10. **DocumentationOrchestrator** - `cortex.orchestrators.domain.enhanced_documentation_orchestrator`
11. **PhaseExecutor** - `cortex.orchestrators.domain.phase_executor`
12. **AutonomousExecutionEngine** - `cortex.orchestrators.domain.autonomous_execution_engine`

### Support Orchestrators (10)
13. **InteractionOrchestratorEnhancement** - `cortex.orchestrators.core.interaction_orchestrator_enhancement`
14. **ToolDiscoveryOrchestrator** - `cortex.orchestrators.core.tool_discovery_orchestrator`
15. **WrappedTDDOrchestrator** - `cortex.orchestrators.core.wrapped_tdd_orchestrator`
16. **FuzzyIntentMatcher** - `cortex.orchestrators.core.fuzzy_intent_matcher`
17. **ComprehensionSession** - `cortex.orchestrators.core.comprehension_session`
18. **DoRApprovalGate** - `cortex.orchestrators.core.dor_approval_gate`
19. **PlanOrchestrator** - `cortex.orchestrators.support.plan_orchestrator`
20. **ChallengeEngine** - `cortex.orchestrators.core.challenge_engine`
21. **DuplicationDetector** - `cortex.orchestrators.support.duplication_detector_orchestrator`
22. **RecommendationEngine** - `cortex.orchestrators.support.recommendation_engine`
23. **RecommendationGate** - `cortex.orchestrators.core.recommendation_gate`

### Analyzers (2)
24. **ASTAnalyzer** - `cortex.brain.analysis.ast_analyzer`
25. **CommentExtractor** - `cortex.brain.analysis.comment_extractor`

---

## 🎯 Action Items

### Phase 26: Wiring Cleanup
1. **Remove 25 deprecated entries** from `cortex-registry/_cortex-master/core/wiring/wiring.yaml`
2. **Update health report** to show 46/46 (100% operational + planned)
3. **Document planned entries** with phase numbers in comments
4. **Validate** all remaining entries are importable

### Expected Result
- **Operational:** 24 (52%)
- **Planned:** 22 (48%)
- **Deprecated:** 0 (0%)
- **Health Score:** 100% (all entries accounted for)

---

## 📊 Current vs Target

| Metric | Current | Target |
|--------|---------|--------|
| Total Entries | 71 | 46 |
| Operational | 24 (34%) | 24 (52%) |
| Planned | 22 (31%) | 22 (48%) |
| Deprecated | 25 (35%) | 0 (0%) |
| Health Score | 65% | 100% |

---

## ✅ Resolution

**Status:** Documented, ready for Phase 26 cleanup  
**Priority:** P2 (non-blocking, improves maintainability)  
**Effort:** 30 minutes (remove 25 YAML entries + test)
