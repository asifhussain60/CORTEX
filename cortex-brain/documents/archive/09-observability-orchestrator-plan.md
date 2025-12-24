# 📊 Observability Orchestrator - Sub-Plan

**Purpose:** Unified dashboard generation, health monitoring, and analytics with AST-powered intelligence  
**Complexity:** HIGH (consolidates 10 files + integrates Intelligent Dashboard Engine)  
**LOC:** 4,263 → 1,800 (4 core components + AST integration)  
**Test Strategy:** SMOKE TEST ONLY (2 tests: initialization + dashboard generation workflow)

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Intelligent Dashboard Engine Plan](08-intelligent-dashboard-engine-plan.md)
- **Next:** [Documentation Orchestrator Plan](06-documentation-orchestrator-plan.md)
- **Workflow YAML:** `src/orchestration_3_0/workflows/observability_workflow.yaml`

---

## 1️⃣ Existing State (Summarized)

### Current Files Being Consolidated

| File | LOC | Purpose | Key Components |
|------|-----|---------|----------------|
| `src/orchestrators/dashboard_launcher.py` | 508 | HTTP server + browser launch | Port detection, CORS, auto-open |
| `src/orchestrators/dashboard_generator.py` | 347 | Dashboard JSON generation | Aggregate collectors, template rendering |
| `src/orchestrators/dashboard_collector.py` | 744 | Data collection orchestration | Multi-collector coordination, validation |
| `src/orchestrators/dashboard_validation.py` | 213 | Ground truth validation | Accuracy checks, confidence scoring |
| `src/orchestrators/application_health_orchestrator.py` | 262 | Health monitoring | Metrics collection, alert generation |
| `src/tier3/orchestrators/adoption_analytics_orchestrator.py` | 499 | Adoption analytics | Usage tracking, team metrics |
| `src/operations/crawlers/base_crawler.py` | 146 | Crawler framework | Abstract base, plugin system |
| `src/operations/crawlers/health_assessor.py` | 416 | Health assessment | System checks, resource monitoring |
| `src/operations/crawlers/git_analyzer.py` | 268 | Git analysis | Commit patterns, contributor analysis |
| `src/operations/crawlers/file_scanner.py` | 206 | File enumeration | Tech stack detection, file inventory |

**Total LOC:** 4,263 lines across 10 files

### Current Workflow (High-Level Steps)

**Dashboard Generation Flow:**
1. **Data Collection:** `dashboard_collector.py` orchestrates 20+ collectors
2. **Aggregation:** `dashboard_generator.py` merges collector outputs
3. **Validation:** `dashboard_validation.py` checks accuracy against ground truth
4. **Launch:** `dashboard_launcher.py` starts HTTP server + opens browser

**Health Monitoring Flow:**
1. **Metrics Collection:** `application_health_orchestrator.py` gathers system metrics
2. **Assessment:** `health_assessor.py` evaluates resource usage, errors
3. **Alerts:** Generate warnings for critical thresholds

**Analytics Flow:**
1. **Usage Tracking:** `adoption_analytics_orchestrator.py` monitors CORTEX usage
2. **Team Metrics:** Track commands, operations, success rates
3. **Reporting:** Generate adoption reports

### Current Triggers

- **Natural Language:** `"load dashboard"`, `"launch dashboard"`, `"open dashboard"`, `"healthcheck"`, `"system health"`, `"adoption analytics"`
- **CLI Command:** `cortex dashboard`, `cortex healthcheck`
- **Copilot Command:** `@cortex load dashboard`, `@cortex healthcheck`

### Current Issues & Pain Points

**Fragmentation:**
- 5 separate dashboard files doing overlapping work
- 10 crawler modules with inconsistent interfaces
- No unified orchestration (collectors called directly)

**Reliability:**
- Dashboard generation: 75-85% success rate (file I/O errors, missing data)
- Health checks: Manual interpretation required
- Analytics: Siloed per team (no org-level view)

**Performance:**
- Dashboard generation: 10-20 seconds (file scanning redundancy)
- Health checks: 5-10 seconds (sequential execution)
- No incremental updates (full regeneration every time)

**Technical Debt:**
- Hard-coded collector list (no plugin discovery)
- No caching (reparse same files)
- No AST intelligence (regex patterns only)
- No multi-tenant support (single-project focus)

**Scalability:**
- Large repos (10k+ files): 5-15 minutes for dashboard
- No parallel processing
- Memory limits (load entire files for scanning)

---

## 2️⃣ New Structure: Observability Orchestrator

### Target Architecture

```
src/orchestration_3_0/orchestrators/observability/
├── __init__.py
├── observability_orchestrator.py           # Main orchestrator (400 LOC)
├── dashboard_engine.py                     # Dashboard generation (500 LOC)
├── health_monitor.py                       # Health monitoring (400 LOC)
├── analytics_collector.py                  # Adoption analytics (500 LOC)
└── intelligent_dashboard/                  # AST-powered intelligence (2,800 LOC - from Phase 3)
    ├── dashboard_ast_engine.py             # Core AST engine (600 LOC)
    ├── business_logic_extractor.py         # Financial calculations (400 LOC)
    ├── financial_data_detector.py          # PCI/SOX patterns (350 LOC)
    ├── use_case_inference.py               # API → use case (400 LOC)
    ├── executive_summary_generator.py      # Narrative synthesis (350 LOC)
    ├── recommendation_intelligence.py      # Code smell → recommendation (250 LOC)
    └── onboarding_generator.py             # 6-stage onboarding (450 LOC)

TOTAL: 1,800 LOC (core orchestrator) + 2,800 LOC (AST intelligence) = 4,600 LOC
```

**Note:** Intelligent Dashboard Engine (2,800 LOC) built in parallel during Phase 3 Week 4-5.

### Component Responsibilities

#### 1. Observability Orchestrator (`observability_orchestrator.py` - 400 LOC)

**Purpose:** Unified entry point for all observability operations

**Key Features:**
- **State Machine Integration:** FSM for dashboard generation, health checks, analytics
- **Multi-Tenant Support:** Org → Team → Project dashboards
- **Plugin Discovery:** Auto-detect collectors via registry pattern
- **Parallel Execution:** ProcessPoolExecutor for concurrent collectors
- **Incremental Updates:** Git diff detection → only update changed data

**API Contract:**
```python
class ObservabilityOrchestrator(BaseOrchestrator):
    def __init__(
        self,
        fsm: FiniteStateMachine,
        session_manager: SessionManager,
        container: DependencyContainer
    ):
        """Initialize with core infrastructure."""
        super().__init__(fsm, session_manager, container)
        self.dashboard_engine = container.resolve(DashboardEngine)
        self.health_monitor = container.resolve(HealthMonitor)
        self.analytics_collector = container.resolve(AnalyticsCollector)
    
    def generate_dashboard(
        self,
        tenant_id: str,
        project_id: str,
        source: str = "auto",
        incremental: bool = True
    ) -> OrchestratorResult:
        """
        Generate dashboard with AST intelligence.
        
        Args:
            tenant_id: Organization/tenant identifier
            project_id: Project identifier
            source: Data source ("auto", "repo-id", "mock")
            incremental: Use Git diff for incremental updates
        
        Returns:
            OrchestratorResult with dashboard JSON path, metrics
        """
        pass
    
    def monitor_health(
        self,
        tenant_id: str,
        project_id: str,
        threshold: str = "warning"
    ) -> OrchestratorResult:
        """Run health checks and generate alert report."""
        pass
    
    def collect_analytics(
        self,
        tenant_id: str,
        scope: str = "project"  # "project", "team", "org"
    ) -> OrchestratorResult:
        """Collect adoption analytics at specified scope."""
        pass
```

#### 2. Dashboard Engine (`dashboard_engine.py` - 500 LOC)

**Purpose:** Dashboard JSON generation with AST-powered intelligence

**Key Features:**
- **Collector Orchestration:** Coordinate 20+ dashboard collectors
- **AST Integration:** Call `DashboardASTEngine` for intelligent use cases, executive summary, recommendations
- **Template Rendering:** Generate glassmorphism HTML + JSON data
- **Multi-Level Dashboards:**
  - **Project Level:** Single repo analysis
  - **Team Level:** Aggregate 5-10 projects
  - **Org Level:** Cross-team rollup with consolidated metrics
- **Caching:** LRU cache for collector outputs (avoid redundant I/O)
- **Streaming:** Render-as-you-go (progressive enhancement)

**API Contract:**
```python
class DashboardEngine:
    def __init__(self, ast_engine: DashboardASTEngine):
        """Initialize with AST engine for intelligence."""
        self.ast_engine = ast_engine
        self.collectors = self._discover_collectors()
    
    def generate_dashboard(
        self,
        repo_path: str,
        output_path: str,
        incremental: bool = True
    ) -> DashboardResult:
        """
        Generate dashboard JSON with AST intelligence.
        
        Returns:
            DashboardResult with:
            - dashboard_json_path: Path to generated JSON
            - metrics: Generation time, collector count, data points
            - intelligence_scores: Confidence for use cases, summary, recommendations
        """
        pass
    
    def _discover_collectors(self) -> List[CollectorPlugin]:
        """Auto-discover collectors via plugin registry."""
        pass
    
    def _aggregate_collectors(self, collector_outputs: List[Dict]) -> Dict:
        """Merge collector outputs into unified dashboard JSON."""
        pass
```

**Integration with AST Engine:**
```python
# Enhanced use case collection
use_cases_basic = use_case_collector.collect()  # Regex patterns (10-20% coverage)
use_cases_ast = ast_engine.infer_use_cases()    # AST inference (80-90% coverage)
dashboard_data["useCases"] = use_cases_basic + use_cases_ast

# Enhanced executive summary
exec_summary_template = exec_summary_aggregator.generate()  # Template-based
exec_summary_ast = ast_engine.generate_executive_summary()  # Narrative synthesis
dashboard_data["executiveSummary"] = exec_summary_ast  # Replace with AST version

# Enhanced recommendations
recommendations_basic = recommendation_aggregator.generate()  # Pattern-based
recommendations_ast = ast_engine.generate_recommendations()   # Code smell mapping
dashboard_data["recommendations"] = recommendations_ast
```

#### 3. Health Monitor (`health_monitor.py` - 400 LOC)

**Purpose:** System health checks and alert generation

**Key Features:**
- **Resource Monitoring:** CPU, memory, disk usage
- **Error Tracking:** Parse logs for error patterns
- **Performance Metrics:** Response times, throughput
- **Alert Generation:** Threshold-based warnings (critical/warning/info)
- **Historical Tracking:** Store health snapshots for trend analysis

**API Contract:**
```python
class HealthMonitor:
    def check_health(
        self,
        project_id: str,
        threshold: str = "warning"
    ) -> HealthReport:
        """
        Run comprehensive health checks.
        
        Returns:
            HealthReport with:
            - overall_status: "healthy", "degraded", "critical"
            - resource_usage: CPU/memory/disk percentages
            - error_count: Recent errors by severity
            - alerts: List of generated alerts
            - recommendations: Actions to resolve issues
        """
        pass
    
    def get_health_history(
        self,
        project_id: str,
        days: int = 7
    ) -> List[HealthSnapshot]:
        """Retrieve historical health data for trend analysis."""
        pass
```

#### 4. Analytics Collector (`analytics_collector.py` - 500 LOC)

**Purpose:** Adoption analytics at project/team/org levels

**Key Features:**
- **Usage Tracking:** Commands executed, operations invoked, success rates
- **Team Metrics:** User activity, collaboration patterns
- **Org Rollup:** Cross-team aggregation, comparative analysis
- **Trend Analysis:** Usage over time, adoption velocity
- **Engagement Scoring:** Active users, command diversity

**API Contract:**
```python
class AnalyticsCollector:
    def collect_analytics(
        self,
        scope: str,  # "project", "team", "org"
        scope_id: str,
        timeframe: str = "7d"
    ) -> AnalyticsReport:
        """
        Collect adoption analytics at specified scope.
        
        Returns:
            AnalyticsReport with:
            - total_commands: Count by operation type
            - success_rate: % successful operations
            - active_users: Unique user count
            - engagement_score: 0-100 metric
            - trends: Usage over time (daily/weekly)
        """
        pass
    
    def compare_teams(
        self,
        org_id: str,
        team_ids: List[str]
    ) -> ComparisonReport:
        """Compare adoption metrics across teams."""
        pass
```

---

## 3️⃣ Migration Strategy (5 Phases with TDD)

### Phase 1: RED (Tests First) - Week 5, Day 1

**Objective:** Write 2 smoke tests

**Smoke Tests (2 tests):**
- [ ] **Test 1: Initialization**
  - Initialize ObservabilityOrchestrator with FSM, SessionManager, DI Container
  - Verify DashboardEngine, HealthMonitor, AnalyticsCollector resolved
  - Verify plugin discovery found collectors
  
- [ ] **Test 2: Dashboard Generation Workflow**
  - Generate dashboard for test repository (50 files)
  - Verify dashboard JSON created
  - Verify AST intelligence integrated (use cases > 0, exec summary present)
  - Verify execution time < 10 seconds

**Validation:** Both tests RED (no implementation yet)

**Timeline:** 1 day (December 16, 2025)

### Phase 2: GREEN (Core Implementation) - Week 5, Day 2-4

**Objective:** Implement 4 core components + AST integration

**Day 2: Observability Orchestrator + Dashboard Engine**
- [ ] Implement `ObservabilityOrchestrator` (400 LOC)
  - State machine integration
  - Multi-tenant routing
  - Plugin discovery
- [ ] Implement `DashboardEngine` (500 LOC)
  - Collector orchestration
  - AST engine integration
  - Template rendering

**Day 3: Health Monitor + Analytics Collector**
- [ ] Implement `HealthMonitor` (400 LOC)
  - Resource monitoring
  - Alert generation
  - Historical tracking
- [ ] Implement `AnalyticsCollector` (500 LOC)
  - Usage tracking
  - Team metrics
  - Org rollup

**Day 4: Integration + Testing**
- [ ] Wire AST engine into DashboardEngine
- [ ] Integrate with existing collectors (20+ modules)
- [ ] Run smoke tests (expect GREEN)

**Validation:** 2/2 smoke tests GREEN, dashboard generated with AST intelligence

**Timeline:** 3 days (December 17-19, 2025)

### Phase 3: REFACTOR (Performance + Multi-Level Dashboards) - Week 6, Day 1-2

**Objective:** Optimize performance + add multi-level dashboard support

**Performance Optimizations:**
- [ ] Parallel collector execution (ProcessPoolExecutor)
- [ ] Incremental updates (Git diff detection)
- [ ] LRU caching for collector outputs
- [ ] Streaming results (render-as-you-go)

**Multi-Level Dashboard Support:**
- [ ] **Project Dashboard:** Single repo analysis (existing)
- [ ] **Team Dashboard:** Aggregate 5-10 projects (NEW)
  - Rollup metrics: Total LOC, use case count, tech stack diversity
  - Comparative analysis: Project health scores
  - Cross-project dependencies
- [ ] **Org Dashboard:** Cross-team rollup (NEW)
  - Executive summary: Org-wide capabilities
  - Adoption analytics: Teams by engagement score
  - Health trends: Critical projects flagged

**Validation:**
- Dashboard generation < 10 seconds for medium repos (1k files) ✅
- Team dashboard aggregates 5 projects < 15 seconds ✅
- Org dashboard aggregates 3 teams < 30 seconds ✅

**Timeline:** 2 days (December 20-23, 2025)

### Phase 4: CUTOVER (Parallel Run + Migration) - Week 6, Day 3

**Objective:** Run old and new orchestrators in parallel

**Parallel Run:**
- [ ] Generate dashboards with both old and new orchestrators
- [ ] Compare outputs for equivalence:
  - Use case count (expect 4x increase with AST)
  - Executive summary confidence (expect 0.95+ with AST)
  - Recommendations actionability (qualitative review)
- [ ] Performance comparison (expect 50-80% faster)

**Migration Steps:**
- [ ] Update `cortex-operations.yaml` with new triggers
- [ ] Archive old orchestrator files (10 files)
- [ ] 30-day grace period begins

**Validation:**
- New orchestrator produces 4x more use cases ✅
- Executive summary confidence > 0.95 ✅
- Performance 50-80% faster ✅
- No critical errors in parallel run ✅

**Timeline:** 1 day (December 24, 2025)

### Phase 5: CLEANUP (Documentation + Legacy Deletion) - Week 6, Day 4-5

**Objective:** Document observability capabilities + archive legacy code

**Documentation:**
- [ ] Create `observability-orchestrator-guide.md` (usage guide)
- [ ] Update `orchestration-master-plan.md` with Phase 3 completion
- [ ] Generate API documentation for 4 core components
- [ ] Create multi-level dashboard guide

**Legacy Deletion (After 30-day grace period):**
- [ ] Delete `src/orchestrators/dashboard_launcher.py` (508 LOC)
- [ ] Delete `src/orchestrators/dashboard_generator.py` (347 LOC)
- [ ] Delete `src/orchestrators/dashboard_collector.py` (744 LOC)
- [ ] Delete `src/orchestrators/dashboard_validation.py` (213 LOC)
- [ ] Delete `src/orchestrators/application_health_orchestrator.py` (262 LOC)
- [ ] Delete `src/tier3/orchestrators/adoption_analytics_orchestrator.py` (499 LOC)
- [ ] Delete crawler modules (4 files, 1,690 LOC)

**Archive Location:** `cortex-brain/archives/orchestrators-legacy/observability/`

**Validation:** Documentation complete, legacy code archived

**Timeline:** 2 days (December 26-27, 2025)

---

## 4️⃣ Test Coverage Requirements (PRAGMATIC - SMOKE TEST)

### Smoke Tests (2 tests)

| Test | Purpose | Expected Outcome |
|------|---------|------------------|
| **Test 1: Initialization** | Verify ObservabilityOrchestrator initializes correctly | DashboardEngine, HealthMonitor, AnalyticsCollector resolved, plugins discovered |
| **Test 2: Dashboard Generation** | Verify end-to-end workflow (generate dashboard → AST intelligence integrated) | Dashboard JSON created, use cases > 0, exec summary present, time < 10s |

**No comprehensive unit tests:** Observability Orchestrator is integration-heavy (collectors + AST engine + HTTP server). Real-world validation more valuable than mocked scenarios.

**Coverage Target:** N/A (smoke tests validate critical workflows only)

---

## 5️⃣ Wiring Validation Checklist

### Integration Points

- [ ] **State Machine Integration**
  - ObservabilityOrchestrator extends BaseOrchestrator
  - FSM states: INITIALIZED → COLLECTING_DATA → GENERATING_INTELLIGENCE → RENDERING → COMPLETED
  - Guard conditions: DoR (repo_path exists), DoD (dashboard JSON valid)

- [ ] **DI Container Integration**
  - Register DashboardEngine (singleton)
  - Register HealthMonitor (singleton)
  - Register AnalyticsCollector (singleton)
  - Register DashboardASTEngine (singleton - from Phase 3)

- [ ] **AST Engine Integration**
  - DashboardEngine imports `DashboardASTEngine` from `src/intelligence/`
  - Call AST engine for use cases, executive summary, recommendations
  - Merge AST results with collector outputs

- [ ] **Collector Plugin System**
  - Auto-discover collectors via registry pattern
  - Support for 20+ existing collectors
  - Backward compatibility (collectors work without modification)

- [ ] **Multi-Tenant Support**
  - All operations accept `tenant_id`, `project_id`
  - Org/Team/Project dashboard variants
  - Isolation between tenants

- [ ] **cortex-operations.yaml**
  - Natural language triggers: "load dashboard", "healthcheck", "analytics"
  - Module path: `orchestration_3_0.orchestrators.observability.observability_orchestrator`
  - Execution method: `cli_wrapper` (dashboard launcher), `copilot_chat` (health/analytics)

---

## 6️⃣ Complete Removal Strategy

### Legacy Files to Remove (After 30-day grace period)

| Batch | Files | LOC | Archive Date | Grace Period Ends | Deletion Date |
|-------|-------|-----|--------------|-------------------|---------------|
| **Batch 3: Observability** | 10 files | 4,263 | Dec 27, 2025 | Jan 26, 2026 | Jan 26, 2026 |

**Files:**
1. `src/orchestrators/dashboard_launcher.py` (508 LOC)
2. `src/orchestrators/dashboard_generator.py` (347 LOC)
3. `src/orchestrators/dashboard_collector.py` (744 LOC)
4. `src/orchestrators/dashboard_validation.py` (213 LOC)
5. `src/orchestrators/application_health_orchestrator.py` (262 LOC)
6. `src/tier3/orchestrators/adoption_analytics_orchestrator.py` (499 LOC)
7. `src/operations/crawlers/base_crawler.py` (146 LOC)
8. `src/operations/crawlers/health_assessor.py` (416 LOC)
9. `src/operations/crawlers/git_analyzer.py` (268 LOC)
10. `src/operations/crawlers/file_scanner.py` (206 LOC)

**Archive Location:** `cortex-brain/archives/orchestrators-legacy/observability/`

**Rollback Script:** `scripts/rollback/rollback_observability_orchestrator.py`

**Deletion Checklist:**
- ✅ Week 1-2: Archive to `cortex-brain/archives/orchestrators-legacy/observability/`
- ✅ Week 2: Update all imports to new orchestrator
- ✅ Week 2-4: Run full test suite (2 smoke tests)
- ✅ Week 3-4: Production monitoring (error rate < 0.1%)
- ✅ Week 4: User feedback collection
- ✅ Grace period end (Jan 26, 2026): Final validation
- ❌ Permanent deletion: Remove archive, delete rollback scripts

---

## 7️⃣ Success Metrics

### Accuracy Improvements

| Metric | Before (Current) | After (AST Engine) | Improvement |
|--------|------------------|-------------------|-------------|
| Use Case Coverage | 10-20% | 80-90% | **4x coverage** |
| Executive Summary Confidence | 0.50-0.65 | 0.95+ | **+46% confidence** |
| Recommendation Actionability | Generic | Specific steps | **Qualitative improvement** |
| Business Logic Detection | 0% | 85% | **New capability** |

### Performance Improvements

| Metric | Before (File Scan) | After (AST + Optimization) | Improvement |
|--------|-------------------|----------------------------|-------------|
| Small repos (<100 files) | 10-15 seconds | 5-8 seconds | **40-50% faster** |
| Medium repos (100-1k files) | 2-5 minutes | 30-60 seconds | **75-85% faster** |
| Large repos (1k-10k files) | 10-20 minutes | 2-5 minutes | **80-90% faster** |

### Code Quality

| Metric | Before (Fragmented) | After (Unified) | Improvement |
|--------|---------------------|-----------------|-------------|
| Total LOC | 4,263 (10 files) | 1,800 (4 files) | **58% reduction** |
| File Count | 10 separate files | 1 orchestrator + 3 components | **60% reduction** |
| Duplication | 30-40% | <5% | **85% reduction** |

### Multi-Tenant Capabilities

| Capability | Before | After | Status |
|------------|--------|-------|--------|
| Project Dashboard | ✅ Supported | ✅ Enhanced with AST | Improved |
| Team Dashboard | ❌ Not supported | ✅ NEW | New |
| Org Dashboard | ❌ Not supported | ✅ NEW | New |
| Cross-Project Dependencies | ❌ Not supported | ✅ NEW | New |

---

## 8️⃣ Implementation Timeline

**Week 5 (December 16-19, 2025):**
- Day 1: Phase 1 (RED - 2 smoke tests)
- Day 2-4: Phase 2 (GREEN - implement 4 components + AST integration)

**Week 6 (December 20-27, 2025):**
- Day 1-2: Phase 3 (REFACTOR - performance + multi-level dashboards)
- Day 3: Phase 4 (CUTOVER - parallel run + migration)
- Day 4-5: Phase 5 (CLEANUP - documentation + legacy deletion preparation)

**Grace Period (December 27, 2025 - January 26, 2026):**
- Monitor production stability (error rate < 0.1%)
- User feedback collection
- Rollback capability maintained

**Permanent Deletion (January 26, 2026):**
- Remove archived files (10 files, 4,263 LOC)
- Delete rollback scripts
- Final validation

**Total Duration:** 10 days (implementation) + 30 days (grace period)

---

## 9️⃣ Risk Mitigation

### Risk: AST Engine Not Ready by Week 5

**Likelihood:** Low (Intelligent Dashboard Engine in parallel development Week 4-5)  
**Impact:** High (blocks dashboard intelligence)  
**Mitigation:**
- Intelligent Dashboard Engine has 8-day timeline (December 10-20)
- ObservabilityOrchestrator starts December 16 (6-day overlap)
- Fallback: Use basic collectors without AST (degrade gracefully)

### Risk: Collector Backward Compatibility

**Likelihood:** Medium (20+ existing collectors)  
**Impact:** Medium (missing data in dashboards)  
**Mitigation:**
- Plugin registry pattern maintains interface compatibility
- Collectors work without modification (no breaking changes)
- Comprehensive integration testing with existing collectors

### Risk: Multi-Level Dashboard Performance

**Likelihood:** Medium (aggregating 10+ projects)  
**Impact:** Medium (slow org dashboard generation)  
**Mitigation:**
- Parallel processing (ProcessPoolExecutor)
- Incremental updates (Git diff detection)
- Caching (LRU + SQLite)
- Streaming results (render-as-you-go)

---

## 🎯 Next Steps

1. **Create YAML Workflow:** `src/orchestration_3_0/workflows/observability_workflow.yaml`
2. **Create Component Folders:** `src/orchestration_3_0/orchestrators/observability/`
3. **Write Smoke Tests:** `tests/orchestration_3_0/orchestrators/test_observability_orchestrator.py`
4. **Implement Core Orchestrator:** `observability_orchestrator.py` (400 LOC)
5. **Implement Dashboard Engine:** `dashboard_engine.py` (500 LOC) + AST integration
6. **Implement Health Monitor:** `health_monitor.py` (400 LOC)
7. **Implement Analytics Collector:** `analytics_collector.py` (500 LOC)
8. **Multi-Level Dashboards:** Team + Org variants
9. **Performance Validation:** Benchmark with 1k, 5k, 10k file repos
10. **Documentation:** Usage guide + API docs

---

**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 SUB-PLAN COMPLETE - Ready for Phase 3 Implementation  
**Estimated Completion:** December 27, 2025 (implementation) + 30-day grace period
