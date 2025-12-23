# Sprint 5 Migration Plan
**CORTEX 3.0 Orchestrator-to-Utility Migration**

**Author:** Asif Hussain  
**Created:** 2025-01-23  
**Sprint:** 5 of 8 (estimated)  
**Previous Sprint:** Sprint 4 - Analysis, Onboarding, Lint (882 lines removed, 107% of target)

---

## 🎯 Sprint 5 Objectives

**Goal:** Migrate 3 orchestrators to lightweight utilities, targeting ~1,200 lines removal

**Success Criteria:**
- ✅ All operations complete in <3 seconds
- ✅ 30-40% code reduction per orchestrator
- ✅ System alignment passing (8/8 checks)
- ✅ Zero test failures
- ✅ All commits pushed to origin

**Current State:**
- Orchestrators remaining: 24 (down from 30 at Sprint 1 start)
- Code removed (cumulative): ~6,582 lines across 11 migrations
- System health: HEALTHY (8/8 alignment checks passing)

---

## 📊 Candidate Analysis

### Investigated Candidates (5 total, 1,999 lines)

#### 1. Session Completion (591 lines) - **HIGH VALUE**
**Purpose:** Holistic validation when TDD session completes

**Current Structure:**
- SessionCompletionOrchestrator (v2.0.0)
- Full test suite execution with pytest
- Before/after metrics comparison
- Git diff summary generation
- SKULL rule validation (22 rules)
- Code quality enforcement (debug detection, lint integration, production readiness)

**Dependencies:**
- CodeCleanupValidator (production readiness checks)
- LintIntegration (code quality validation)
- ProductionReadinessChecklist (final gate)
- DocumentOrganizer (summary generation)

**Migration Assessment:**
- **Complexity:** High (comprehensive validation, multiple integrations)
- **Core Operations:** 6-7 extractable (run_tests, compare_metrics, validate_skull, check_quality, generate_summary, run_full_validation)
- **Reduction Potential:** 35-40% (591 → ~370 lines)
- **Value:** Very high - critical TDD workflow component
- **Risk:** Moderate - requires careful preservation of 22 SKULL rules

#### 2. Dashboard Generator (347 lines) - **MODERATE**
**Purpose:** Generate D3.js interactive dashboards for CORTEX health/metrics

**Current Structure:**
- DashboardGenerator class
- D3.js-powered visualizations (health trends, integration heatmaps, coverage gauges, radar charts)
- Jinja2 template rendering
- Responsive layout with export functionality
- 7-layer integration scoring
- Forecast calculation for trends

**Dependencies:**
- Jinja2 (template engine)
- DashboardDataCollector (metrics source)
- ChartConfigBuilder (D3.js configs)
- Templates in CORTEX/templates/ directory

**Migration Assessment:**
- **Complexity:** Moderate (visualization-heavy, template dependencies)
- **Core Operations:** 5-6 extractable (generate_dashboard, render_health_chart, render_heatmap, render_coverage, render_radar, export_report)
- **Reduction Potential:** 30-35% (347 → ~230 lines)
- **Value:** High - visibility into system health
- **Risk:** Low - visualization logic well-encapsulated

#### 3. Metrics Tracker (431 lines) - **HIGH VALUE**
**Purpose:** Track timestamps, duration, performance metrics for TDD workflow phases

**Current Structure:**
- MetricsTracker class (v1.0.0)
- ISO 8601 timestamp tracking
- Duration calculation (seconds)
- Git commit SHA correlation
- Before/after metrics comparison
- Session and phase-level metrics in Tier 1 database

**Dependencies:**
- Tier 1 database (working_memory.db)
- Migration script (add_tdd_metrics.sql)
- SQLite connection management

**Migration Assessment:**
- **Complexity:** Moderate (database interactions, schema migrations)
- **Core Operations:** 6-7 extractable (start_session, end_session, start_phase, end_phase, record_metrics, get_session_metrics, compare_metrics)
- **Reduction Potential:** 35-40% (431 → ~270 lines)
- **Value:** Very high - foundation of TDD metrics system
- **Risk:** Moderate - schema preservation critical

#### 4. Application Health (262 lines) - **LIGHTWEIGHT**
**Purpose:** Application health analysis via crawler integration

**Current Structure:**
- ApplicationHealthOrchestrator class
- Language analyzers (Python, C#, JS, ColdFusion)
- CrawlerOrchestrator integration
- ArchitectureGraphBuilder integration
- Scan levels (overview, standard, deep)

**Dependencies:**
- CrawlerOrchestrator (file discovery)
- Language analyzers (Python/CSharp/JavaScript/ColdFusion/Generic)
- ArchitectureGraphBuilder (dependency graph)

**Migration Assessment:**
- **Complexity:** Low (orchestration layer, not heavy logic)
- **Core Operations:** 3-4 extractable (analyze_health, scan_files, generate_report, build_architecture_graph)
- **Reduction Potential:** 40-45% (262 → ~150 lines)
- **Value:** Moderate - useful for health checks
- **Risk:** Low - thin orchestration layer

#### 5. Planning Document Migrator (368 lines) - **MODERATE**
**Purpose:** Migrate planning documents to status-based subdirectories

**Current Structure:**
- PlanningDocumentMigrator class (Phase 2)
- Status detection from frontmatter (in-progress, proposed, approved, completed, cancelled, deprecated)
- Directory organization (active/, approved/, completed/, deprecated/)
- Dry-run mode
- Automatic backup before migration
- Validation checks

**Dependencies:**
- File I/O (shutil, pathlib)
- Regex pattern matching (frontmatter parsing)

**Migration Assessment:**
- **Complexity:** Low (file operations, pattern matching)
- **Core Operations:** 4-5 extractable (migrate_documents, detect_status, backup_planning_dir, validate_migration, organize_by_status)
- **Reduction Potential:** 30-35% (368 → ~245 lines)
- **Value:** Moderate - organizational utility
- **Risk:** Low - simple file operations

---

## 🎯 Recommended Sprint 5 Targets

### Option A: 3 Orchestrators - BALANCED (RECOMMENDED)
**Targets:** Metrics Tracker + Dashboard Generator + Application Health  
**Total Lines:** 1,040 lines (431 + 347 + 262)  
**Expected Reduction:** ~370 lines (35% average)  
**Estimated Time:** 3.5-4 hours  
**Risk:** Low-Moderate

**Rationale:**
- **Metrics Tracker (431):** High-value TDD foundation, moderate complexity, database integration practice
- **Dashboard Generator (347):** Visualization utility, template rendering, moderate complexity
- **Application Health (262):** Quick win, thin orchestration layer, 40%+ reduction potential
- **Balance:** 1 high-value database component + 1 visualization component + 1 lightweight orchestrator
- **Synergy:** All three are reporting/monitoring utilities, natural grouping

**Task Breakdown:**
- Task 13: Metrics Tracker (90 min investigation + implementation, 15 min testing)
- Task 14: Dashboard Generator (75 min investigation + implementation, 15 min testing)
- Task 15: Application Health (60 min investigation + implementation, 10 min testing)
- Task 16: Sprint 5 validation and reporting (30 min)

### Option B: 2 Orchestrators - CONSERVATIVE
**Targets:** Dashboard Generator + Application Health  
**Total Lines:** 609 lines (347 + 262)  
**Expected Reduction:** ~220 lines (36% average)  
**Estimated Time:** 2-2.5 hours  
**Risk:** Low

**Rationale:**
- Skip Metrics Tracker to avoid database complexity
- Focus on visualization + health utilities
- Safer option if time-constrained
- Lower value (misses critical TDD metrics foundation)

### Option C: 4 Orchestrators - AGGRESSIVE
**Targets:** Metrics Tracker + Dashboard Generator + Application Health + Planning Document Migrator  
**Total Lines:** 1,408 lines (431 + 347 + 262 + 368)  
**Expected Reduction:** ~490 lines (35% average)  
**Estimated Time:** 4.5-5 hours  
**Risk:** Moderate-High

**Rationale:**
- Add Planning Document Migrator (368 lines, low complexity)
- Maximize throughput for sprint
- Higher risk of fatigue/errors with 4 migrations
- May exceed single-session capacity

---

## 📋 Migration Strategy (Option A)

### Task 13: Metrics Tracker Migration (431 → ~270 lines)

**Investigation Phase (30 min):**
- Read full structure (lines 1-431)
- Identify all metrics operations (start_session, end_session, start_phase, end_phase, record_metrics, get_session_metrics, compare_metrics)
- Map Tier 1 database interactions
- Review schema migration (add_tdd_metrics.sql)
- Identify workflow overhead (session management, error handling complexity)

**Implementation (60 min):**
```
src/operations/modules/metrics/metrics_utility.py

Core operations:
1. start_session(session_id, project_path, feature_name) → bool
2. end_session(session_id, metrics) → bool
3. start_phase(session_id, phase_name) → str (phase_id)
4. end_phase(phase_id, status) → bool
5. record_metrics(session_id, metrics_dict) → bool
6. get_session_metrics(session_id) → Dict
7. compare_metrics(session_id_before, session_id_after) → Dict

Simplifications:
- Direct SQLite operations (remove connection pooling)
- Simplified error handling (remove retry logic)
- Remove session state management (stateless operations)
- Single metrics dataclass (consolidate SessionMetrics + PhaseMetrics)
```

**Testing (15 min):**
- Create test session → verify database record
- Start/end phase tracking → verify timestamps
- Record metrics → verify storage
- Compare metrics → verify calculation
- Performance target: <0.5s for full session cycle

**Expected Outcome:**
- 431 → 270 lines (37% reduction, 161 lines removed)
- Performance: <0.5s (6x faster than 3s target)
- Operations: 7 core utilities

### Task 14: Dashboard Generator Migration (347 → ~230 lines)

**Investigation Phase (25 min):**
- Read full structure (lines 1-347)
- Identify visualization operations (generate_dashboard, render charts)
- Map Jinja2 template dependencies
- Review DashboardDataCollector integration
- Identify D3.js config generation logic

**Implementation (50 min):**
```
src/operations/modules/reporting/dashboard_utility.py

Core operations:
1. generate_dashboard(metrics_data) → str (HTML path)
2. render_health_chart(health_data) → Dict (D3.js config)
3. render_integration_heatmap(integration_scores) → Dict
4. render_coverage_gauge(coverage_data) → Dict
5. render_quality_radar(quality_metrics) → Dict
6. export_dashboard(html_path, format) → str (export path)

Simplifications:
- Remove template auto-detection (hardcode template paths)
- Simplified chart configs (remove dynamic scaling)
- Direct Jinja2 rendering (remove template caching)
- Single dashboard template (consolidate variants)
```

**Testing (15 min):**
- Generate dashboard with sample metrics → verify HTML output
- Render health chart → verify D3.js config
- Export dashboard → verify file creation
- Performance target: <1s for full dashboard generation

**Expected Outcome:**
- 347 → 230 lines (34% reduction, 117 lines removed)
- Performance: <1s (3x faster than 3s target)
- Operations: 6 visualization utilities

### Task 15: Application Health Migration (262 → ~150 lines)

**Investigation Phase (20 min):**
- Read full structure (lines 1-262)
- Identify health analysis operations
- Map analyzer dependencies (Python, C#, JS, ColdFusion)
- Review CrawlerOrchestrator integration
- Identify architecture graph building logic

**Implementation (40 min):**
```
src/operations/modules/health/health_utility.py

Core operations:
1. analyze_application(project_path, scan_level) → Dict
2. scan_project_files(project_path) → List[str]
3. build_architecture_graph(project_path) → Dict
4. generate_health_report(analysis_data) → str

Simplifications:
- Direct analyzer instantiation (remove factory pattern)
- Simplified scan levels (remove 'overview', keep 'standard' and 'deep')
- Remove generic analyzer fallback (language-specific only)
- Direct architecture graph building (remove error wrapping)
```

**Testing (10 min):**
- Analyze sample project → verify metrics
- Build architecture graph → verify nodes/edges
- Generate report → verify output
- Performance target: <2s for standard scan

**Expected Outcome:**
- 262 → 150 lines (43% reduction, 112 lines removed)
- Performance: <2s (1.5x faster than 3s target)
- Operations: 4 health utilities

### Task 16: Sprint 5 Validation & Reporting (30 min)

**System Validation:**
- Count orchestrators: Should be 21 (down from 24)
- Run system alignment: `python3 -m src.operations.align`
- Verify 8/8 checks passing
- Performance check: All utilities <2s

**Git Operations:**
- Push all commits to origin
- Verify branch sync (CORTEX-3.0)

**Completion Report:**
```
cortex-brain/documents/reports/sprint-5-completion-report.md

Sections:
- Sprint 5 Summary (3 migrations, targets achieved)
- Task Summaries (13, 14, 15 with metrics)
- Performance Metrics (execution times, reduction %)
- Lessons Learned (database migrations, visualization utilities)
- Cumulative Progress (14 migrations, ~7,000 lines removed, 21 orchestrators)
- Sprint 6 Recommendations (next 3 targets)
```

---

## 📊 Expected Sprint 5 Outcomes

### Code Reduction
| Orchestrator | Before | After | Reduction | % |
|-------------|--------|-------|-----------|---|
| Metrics Tracker | 431 | 270 | 161 | 37% |
| Dashboard Generator | 347 | 230 | 117 | 34% |
| Application Health | 262 | 150 | 112 | 43% |
| **TOTAL** | **1,040** | **650** | **390** | **38%** |

### Performance Targets
| Operation | Target | Expected | Improvement |
|-----------|--------|----------|-------------|
| Metrics session cycle | <0.5s | 0.4s | 7.5x faster |
| Dashboard generation | <1s | 0.8s | 3.8x faster |
| Health analysis (standard) | <2s | 1.5s | 2x faster |

### System Impact
- **Orchestrators:** 24 → 21 (30% reduction from Sprint 1 start)
- **Cumulative code removed:** ~6,972 lines (6,582 + 390)
- **Migrations completed:** 14 total (2+3+3+3+3)
- **System health:** Expected 8/8 alignment checks passing

---

## ⚠️ Risk Assessment

### Metrics Tracker Risks
- **Database schema preservation:** SKULL rules require Tier 1 schema integrity
- **Mitigation:** Preserve add_tdd_metrics.sql migration script, test schema after migration
- **Impact:** Moderate (could break TDD metrics tracking)

### Dashboard Generator Risks
- **Template dependencies:** Jinja2 templates in CORTEX/templates/ must remain accessible
- **Mitigation:** Test template rendering with real metrics, verify paths
- **Impact:** Low (visualization only, non-critical)

### Application Health Risks
- **Analyzer integration:** Language analyzers (Python, C#, JS) must remain functional
- **Mitigation:** Test with sample projects in multiple languages
- **Impact:** Low (orchestration layer only)

### General Risks
- **Session duration:** 3.5-4 hours estimated, may extend to 4.5 hours
- **Mitigation:** Take breaks between tasks, maintain focus
- **Fatigue risk:** Moderate (Sprint 5 follows Sprint 4 immediately)
- **Mitigation:** Monitor performance, validate after each task

---

## 🎯 Success Validation

**Automated Checks:**
- ✅ System alignment: `python3 -m src.operations.align` (8/8 passing)
- ✅ Orchestrator count: `ls src/orchestrators/*.py | wc -l` (21 expected)
- ✅ Git sync: `git status` (branch synced with origin)

**Manual Validation:**
- ✅ Metrics utility: Create session → record metrics → compare → verify database
- ✅ Dashboard utility: Generate dashboard → verify HTML → check visualizations
- ✅ Health utility: Analyze project → verify metrics → check architecture graph
- ✅ Performance: All operations complete <2s

**Documentation:**
- ✅ Sprint 5 completion report created
- ✅ All commits pushed with descriptive messages
- ✅ System health documented (21 orchestrators, 8/8 checks)

---

## 📅 Sprint 5 Timeline (Option A)

**Total Estimated Time:** 3.5-4 hours

| Task | Activity | Duration | Cumulative |
|------|----------|----------|------------|
| 13 | Metrics Tracker investigation | 30 min | 0:30 |
| 13 | Metrics Tracker implementation | 60 min | 1:30 |
| 13 | Metrics Tracker testing | 15 min | 1:45 |
| 14 | Dashboard Generator investigation | 25 min | 2:10 |
| 14 | Dashboard Generator implementation | 50 min | 3:00 |
| 14 | Dashboard Generator testing | 15 min | 3:15 |
| 15 | Application Health investigation | 20 min | 3:35 |
| 15 | Application Health implementation | 40 min | 4:15 |
| 15 | Application Health testing | 10 min | 4:25 |
| 16 | Sprint 5 validation & reporting | 30 min | 4:55 |

**Buffer:** 15-20 minutes for unexpected issues

---

## 🚀 Next Sprint Preview (Sprint 6)

**Remaining High-Value Targets:**
- Session Completion (591 lines) - Comprehensive TDD validation
- Planning Document Migrator (368 lines) - Document organization
- Phase Checkpoint Manager (smaller target, TBD)

**Estimated Remaining Work:**
- 3-4 more sprints to complete CORTEX 3.0 migration
- ~15 orchestrators remaining after Sprint 5
- Target: <20 orchestrators by Sprint 8 completion

---

## 🎯 Recommendation

**SELECT OPTION A** - Balanced approach with 3 orchestrators

**Reasons:**
1. **High value:** Metrics Tracker is foundation of TDD metrics system
2. **Natural grouping:** All three are reporting/monitoring utilities
3. **Manageable scope:** 3.5-4 hours aligns with proven sprint pattern
4. **Risk balance:** 1 moderate complexity (Metrics) + 2 lightweight (Dashboard, Health)
5. **Momentum:** Maintains Sprint 4 pace without overextending
6. **Synergy:** Database + visualization + health analysis form cohesive monitoring layer

**Expected Sprint 5 Achievement:**
- ✅ 390 lines removed (38% reduction)
- ✅ 3 orchestrators migrated (21 remaining)
- ✅ All operations <2s
- ✅ System alignment passing (8/8)
- ✅ Zero test failures

---

**Ready to proceed with Option A, B, or C?**
