# 📚 Documentation Orchestrator - Sub-Plan

**Purpose:** Unified documentation generation with GitHub Pages, API docs, reports, and multi-language docstrings  
**Complexity:** MEDIUM (consolidates 3 orchestrators + GitHub Pages integration)  
**LOC:** 1,229 → 700 (simplification + GitHub Pages replaces enterprise doc system)  
**Test Strategy:** SMOKE TEST ONLY (2 tests: initialization + GitHub Pages site generation)

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Observability Orchestrator Plan](09-observability-orchestrator-plan.md)
- **Next:** [Intelligence Orchestrator Plan](07-intelligence-orchestrator-plan.md)
- **Workflow YAML:** `src/orchestration_3_0/workflows/documentation_workflow.yaml`
- **Related:** [enterprise-doc-orchestrator-enhancement-plan.md](../enterprise-doc-orchestrator-enhancement-plan.md)

---

## 1️⃣ Existing State (Summarized)

### Current Files Being Consolidated

| File | LOC | Purpose | Key Components |
|------|-----|---------|----------------|
| `src/orchestrators/documentation_orchestrator.py` | 478 | Learning library docs | Phase completion, architecture docs |
| `src/intelligence/multi_language_docstring_orchestrator.py` | 267 | Multi-language docstrings | Python, C#, JS/TS extraction |
| `src/tier3/visualization/report_generator.py` | 484 | Report generation | Executive summary, metrics visualization |

**Total LOC:** 1,229 lines across 3 files

**Note:** Enterprise Documentation Orchestrator (4,668 LOC) is being REPLACED by GitHub Pages site (active implementation on separate machine), NOT consolidated into this orchestrator.

### Current Workflow (High-Level Steps)

**Learning Library Documentation Flow:**
1. **Phase Completion:** Document refactoring phases
2. **Architecture Docs:** Generate architecture diagrams
3. **Decision Records:** Track architectural decisions
4. **Refactoring Patterns:** Document code patterns

**Multi-Language Docstring Flow:**
1. **File Discovery:** Scan for Python, C#, JS/TS files
2. **Docstring Extraction:** Parse function/class docstrings
3. **Validation:** Check completeness, informativeness
4. **Enhancement:** Auto-generate missing docstrings (optional)

**Report Generation Flow:**
1. **Data Collection:** Gather metrics, health status
2. **Executive Summary:** Generate high-level narrative
3. **Detailed Analysis:** Breakdown by layer/component
4. **Export:** Markdown, HTML, PDF formats

### Current Triggers

- **Natural Language:** `"generate docs"`, `"create documentation"`, `"generate report"`, `"extract docstrings"`
- **CLI Command:** `cortex generate-docs`, `cortex report`
- **Copilot Command:** `@cortex generate documentation`

### Current Issues & Pain Points

**Fragmentation:**
- 3 separate documentation generators with no shared infrastructure
- Learning library docs disconnected from API documentation
- Report generation separate from dashboard system

**Reliability:**
- Documentation generation: 70-80% success rate (file I/O errors, missing templates)
- Docstring extraction: Limited to single language per run
- Reports: Manual updates required for changing metrics

**GitHub Pages Integration:**
- Enterprise Documentation Orchestrator (4,668 LOC) being replaced by GitHub Pages site
- Active implementation on separate machine (Phase 1-2 complete)
- Glassmorphism design, drill-down architecture
- Autonomous regeneration on git push

**Technical Debt:**
- Hard-coded file paths and templates
- No state persistence (regenerate everything)
- No multi-tenant support
- No GitHub Pages integration in legacy orchestrators

**Scalability:**
- Large codebases (10k+ files): 5-10 minutes for docstring extraction
- No parallel processing
- No incremental updates (full regeneration)

---

## 2️⃣ New Structure: Documentation Orchestrator

### Target Architecture

```
src/orchestration_3_0/orchestrators/documentation/
├── __init__.py
├── documentation_orchestrator.py           # Main orchestrator (200 LOC)
├── github_pages_generator.py               # GitHub Pages site generation (200 LOC)
├── api_doc_generator.py                    # API documentation (150 LOC)
├── report_builder.py                       # Reports and summaries (150 LOC)
└── multi_language_docstring_extractor.py   # Enhanced docstring extraction (200 LOC - reuse existing)

TOTAL: 700 LOC (core orchestrator) + 200 LOC (reused docstring extractor) = 900 LOC
```

**Note:** GitHub Pages implementation (separate machine) remains independent but integrated via triggers.

### Component Responsibilities

#### 1. Documentation Orchestrator (`documentation_orchestrator.py` - 200 LOC)

**Purpose:** Unified entry point for all documentation operations

**Key Features:**
- **State Machine Integration:** FSM for doc generation, API docs, reports
- **Multi-Tenant Support:** Org → Team → Project documentation
- **GitHub Pages Trigger:** Auto-trigger site regeneration on doc updates
- **Incremental Updates:** Git diff detection → only update changed docs
- **Template Management:** Unified template system for all doc types

**API Contract:**
```python
class DocumentationOrchestrator(BaseOrchestrator):
    def __init__(
        self,
        fsm: FiniteStateMachine,
        session_manager: SessionManager,
        container: DependencyContainer
    ):
        """Initialize with core infrastructure."""
        super().__init__(fsm, session_manager, container)
        self.github_pages_gen = container.resolve(GitHubPagesGenerator)
        self.api_doc_gen = container.resolve(ApiDocGenerator)
        self.report_builder = container.resolve(ReportBuilder)
        self.docstring_extractor = container.resolve(MultiLanguageDocstringExtractor)
    
    def generate_documentation(
        self,
        tenant_id: str,
        project_id: str,
        doc_type: str = "all",  # "all", "api", "github-pages", "report", "docstrings"
        incremental: bool = True
    ) -> OrchestratorResult:
        """
        Generate documentation with multi-type support.
        
        Returns:
            OrchestratorResult with doc paths, generation metrics
        """
        pass
    
    def generate_github_pages_site(
        self,
        tenant_id: str,
        project_id: str,
        auto_deploy: bool = True
    ) -> OrchestratorResult:
        """Generate GitHub Pages site with glassmorphism design."""
        pass
```

#### 2. GitHub Pages Generator (`github_pages_generator.py` - 200 LOC)

**Purpose:** Generate GitHub Pages site with glassmorphism design

**Key Features:**
- **Integration with Existing Implementation:** Coordinate with active GitHub Pages work (Phase 1-2 complete)
- **Glassmorphism Design:** Modern UI with translucent cards, gradients
- **Drill-Down Architecture:** 
  - Landing page: Project overview
  - Feature pages: Detailed capability docs
  - API reference: Auto-generated from code
- **Autonomous Regeneration:** Git hook triggers site rebuild
- **MkDocs Integration:** Use MkDocs Material theme
- **Multi-Language Support:** EN/ES/FR documentation

**API Contract:**
```python
class GitHubPagesGenerator:
    def generate_site(
        self,
        project_path: str,
        output_path: str = "docs/",
        theme: str = "material"
    ) -> SiteGenerationResult:
        """
        Generate GitHub Pages site structure.
        
        Returns:
            SiteGenerationResult with:
            - site_url: GitHub Pages URL
            - pages_generated: Count of pages
            - build_time: Generation duration
        """
        pass
    
    def trigger_deployment(self, branch: str = "gh-pages") -> DeploymentResult:
        """Trigger GitHub Pages deployment via git push."""
        pass
```

**Note:** This component COORDINATES with existing GitHub Pages implementation (separate machine), does NOT replace it.

#### 3. API Doc Generator (`api_doc_generator.py` - 150 LOC)

**Purpose:** Auto-generate API documentation from code

**Key Features:**
- **Multi-Language Support:** Python (docstrings), C# (XML comments), JS/TS (JSDoc)
- **Reuse Docstring Extractor:** Leverage existing `multi_language_docstring_orchestrator.py` (267 LOC)
- **OpenAPI Integration:** Generate OpenAPI/Swagger specs for REST APIs
- **Interactive Docs:** Swagger UI, ReDoc integration
- **Code Examples:** Extract usage examples from tests

**API Contract:**
```python
class ApiDocGenerator:
    def __init__(self, docstring_extractor: MultiLanguageDocstringExtractor):
        """Initialize with reused docstring extractor."""
        self.docstring_extractor = docstring_extractor
    
    def generate_api_docs(
        self,
        source_paths: List[str],
        output_format: str = "markdown"  # "markdown", "html", "openapi"
    ) -> ApiDocsResult:
        """
        Generate API documentation from source code.
        
        Returns:
            ApiDocsResult with:
            - docs_path: Path to generated docs
            - endpoints_count: Number of documented APIs
            - coverage: % of functions with docstrings
        """
        pass
```

#### 4. Report Builder (`report_builder.py` - 150 LOC)

**Purpose:** Generate reports and executive summaries

**Key Features:**
- **Executive Summary:** High-level narratives (reuse from Observability)
- **Metrics Visualization:** Charts, graphs, dashboards
- **Multi-Format Export:** Markdown, HTML, PDF
- **Template System:** Customizable report templates
- **Scheduled Reports:** Cron-triggered report generation

**API Contract:**
```python
class ReportBuilder:
    def generate_report(
        self,
        report_type: str,  # "executive", "metrics", "health", "adoption"
        data: Dict[str, Any],
        output_format: str = "markdown"
    ) -> ReportResult:
        """
        Generate report from data.
        
        Returns:
            ReportResult with:
            - report_path: Path to generated report
            - sections_count: Number of report sections
            - generation_time: Duration
        """
        pass
```

---

## 3️⃣ Migration Strategy (5 Phases with TDD)

### Phase 1: RED (Tests First) - Week 5, Day 1

**Objective:** Write 2 smoke tests

**Smoke Tests (2 tests):**
- [ ] **Test 1: Initialization**
  - Initialize DocumentationOrchestrator with FSM, SessionManager, DI Container
  - Verify GitHubPagesGenerator, ApiDocGenerator, ReportBuilder, DocstringExtractor resolved
  
- [ ] **Test 2: GitHub Pages Site Generation**
  - Generate GitHub Pages site for test project
  - Verify MkDocs configuration created
  - Verify site structure (landing page, feature pages, API reference)
  - Verify execution time < 5 seconds

**Validation:** Both tests RED (no implementation yet)

**Timeline:** 1 day (December 16, 2025)

### Phase 2: GREEN (Core Implementation) - Week 5, Day 2-3

**Objective:** Implement 4 core components

**Day 2: Core Orchestrator + GitHub Pages Generator**
- [ ] Implement `DocumentationOrchestrator` (200 LOC)
  - State machine integration
  - Multi-tenant routing
  - Incremental updates
- [ ] Implement `GitHubPagesGenerator` (200 LOC)
  - MkDocs integration
  - Glassmorphism design templates
  - Git hook triggers

**Day 3: API Doc Generator + Report Builder**
- [ ] Implement `ApiDocGenerator` (150 LOC)
  - Reuse existing `MultiLanguageDocstringExtractor` (267 LOC)
  - OpenAPI spec generation
  - Swagger UI integration
- [ ] Implement `ReportBuilder` (150 LOC)
  - Executive summary templates
  - Multi-format export (Markdown, HTML, PDF)
  - Metrics visualization

**Validation:** 2/2 smoke tests GREEN, GitHub Pages site generated

**Timeline:** 2 days (December 17-18, 2025)

### Phase 3: REFACTOR (GitHub Pages Integration + Performance) - Week 5, Day 4

**Objective:** Integrate with existing GitHub Pages work + optimize

**GitHub Pages Integration:**
- [ ] Coordinate with active GitHub Pages implementation (separate machine)
- [ ] Ensure no duplication (orchestrator TRIGGERS site generation, doesn't replace it)
- [ ] Git hooks for autonomous regeneration
- [ ] Multi-language support (EN/ES/FR)

**Performance Optimizations:**
- [ ] Incremental docstring extraction (Git diff detection)
- [ ] Parallel processing for multi-language docs
- [ ] Template caching (avoid redundant renders)

**Validation:**
- GitHub Pages site generated < 5 seconds ✅
- API docs generated < 10 seconds (1k files) ✅
- Reports generated < 3 seconds ✅

**Timeline:** 1 day (December 19, 2025)

### Phase 4: CUTOVER (Parallel Run + Migration) - Week 5, Day 5

**Objective:** Run old and new orchestrators in parallel

**Parallel Run:**
- [ ] Generate docs with both old and new orchestrators
- [ ] Compare outputs for equivalence:
  - GitHub Pages site structure
  - API documentation coverage
  - Report accuracy
- [ ] Performance comparison (expect 30-50% faster)

**Migration Steps:**
- [ ] Update `cortex-operations.yaml` with new triggers
- [ ] Archive old orchestrator files (3 files)
- [ ] 30-day grace period begins

**Validation:**
- New orchestrator produces equivalent docs ✅
- GitHub Pages site matches existing quality ✅
- Performance 30-50% faster ✅
- No critical errors in parallel run ✅

**Timeline:** 1 day (December 20, 2025)

### Phase 5: CLEANUP (Documentation + Legacy Deletion) - Week 6, Day 1

**Objective:** Document capabilities + archive legacy code

**Documentation:**
- [ ] Create `documentation-orchestrator-guide.md` (usage guide)
- [ ] Update `orchestration-master-plan.md` with Phase 3 completion
- [ ] Generate API documentation for 4 core components
- [ ] GitHub Pages integration guide

**Legacy Deletion (After 30-day grace period):**
- [ ] Delete `src/orchestrators/documentation_orchestrator.py` (478 LOC)
- [ ] Archive `src/intelligence/multi_language_docstring_orchestrator.py` (267 LOC - REUSED, not deleted)
- [ ] Delete `src/tier3/visualization/report_generator.py` (484 LOC)

**Archive Location:** `cortex-brain/archives/orchestrators-legacy/documentation/`

**Validation:** Documentation complete, legacy code archived

**Timeline:** 1 day (December 23, 2025)

---

## 4️⃣ Test Coverage Requirements (PRAGMATIC - SMOKE TEST)

### Smoke Tests (2 tests)

| Test | Purpose | Expected Outcome |
|------|---------|------------------|
| **Test 1: Initialization** | Verify DocumentationOrchestrator initializes correctly | All components resolved, GitHub Pages integration configured |
| **Test 2: GitHub Pages Generation** | Verify end-to-end workflow (generate site → MkDocs build → deploy) | Site structure created, landing page + feature pages + API reference, time < 5s |

**No comprehensive unit tests:** Documentation Orchestrator is integration-heavy (MkDocs + Git + file I/O). Real-world validation more valuable than mocked scenarios.

**Coverage Target:** N/A (smoke tests validate critical workflows only)

---

## 5️⃣ Wiring Validation Checklist

### Integration Points

- [ ] **State Machine Integration**
  - DocumentationOrchestrator extends BaseOrchestrator
  - FSM states: INITIALIZED → COLLECTING_DOCS → GENERATING → DEPLOYING → COMPLETED
  - Guard conditions: DoR (project_path exists), DoD (docs generated)

- [ ] **DI Container Integration**
  - Register GitHubPagesGenerator (singleton)
  - Register ApiDocGenerator (singleton)
  - Register ReportBuilder (singleton)
  - Register MultiLanguageDocstringExtractor (singleton - REUSED)

- [ ] **GitHub Pages Integration**
  - Coordinate with active implementation (separate machine)
  - Git hooks trigger site regeneration
  - MkDocs Material theme integration
  - Autonomous deployment on push to gh-pages branch

- [ ] **Multi-Tenant Support**
  - All operations accept `tenant_id`, `project_id`
  - Org/Team/Project documentation variants
  - Isolation between tenants

- [ ] **cortex-operations.yaml**
  - Natural language triggers: "generate docs", "github pages", "api docs", "generate report"
  - Module path: `orchestration_3_0.orchestrators.documentation.documentation_orchestrator`
  - Execution method: `copilot_chat` (interactive workflow)

---

## 6️⃣ Complete Removal Strategy

### Legacy Files to Remove (After 30-day grace period)

| Batch | Files | LOC | Archive Date | Grace Period Ends | Deletion Date |
|-------|-------|-----|--------------|-------------------|---------------|
| **Batch 3: Documentation** | 2 files | 962 | Dec 23, 2025 | Jan 22, 2026 | Jan 22, 2026 |

**Files:**
1. `src/orchestrators/documentation_orchestrator.py` (478 LOC)
2. `src/tier3/visualization/report_generator.py` (484 LOC)

**Files REUSED (Not Deleted):**
- `src/intelligence/multi_language_docstring_orchestrator.py` (267 LOC) - Enhanced and integrated

**Archive Location:** `cortex-brain/archives/orchestrators-legacy/documentation/`

**Rollback Script:** `scripts/rollback/rollback_documentation_orchestrator.py`

**Deletion Checklist:**
- ✅ Week 1-2: Archive to `cortex-brain/archives/orchestrators-legacy/documentation/`
- ✅ Week 2: Update all imports to new orchestrator
- ✅ Week 2-4: Run full test suite (2 smoke tests)
- ✅ Week 3-4: Production monitoring (error rate < 0.1%)
- ✅ Week 4: User feedback collection
- ✅ Grace period end (Jan 22, 2026): Final validation
- ❌ Permanent deletion: Remove archive, delete rollback scripts

---

## 7️⃣ Success Metrics

### Code Quality

| Metric | Before (Fragmented) | After (Unified) | Improvement |
|--------|---------------------|-----------------|-------------|
| Total LOC | 1,229 (3 files) | 700 (4 files + 1 reused) | **43% reduction** |
| File Count | 3 separate files | 1 orchestrator + 3 components | Unified |
| Duplication | 20-30% | <5% | **75% reduction** |

### Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| GitHub Pages generation | 10-15 seconds | <5 seconds | **50-70% faster** |
| API docs (1k files) | 15-20 seconds | <10 seconds | **40-50% faster** |
| Reports | 5-8 seconds | <3 seconds | **40-60% faster** |

### Capabilities

| Capability | Before | After | Status |
|------------|--------|-------|--------|
| GitHub Pages | ❌ Not integrated | ✅ Integrated | NEW |
| API Documentation | ✅ Single language | ✅ Multi-language (Python/C#/JS/TS) | Enhanced |
| Executive Reports | ✅ Manual | ✅ Automated | Enhanced |
| Incremental Updates | ❌ Not supported | ✅ Git diff detection | NEW |
| Multi-Tenant | ❌ Not supported | ✅ Org/Team/Project | NEW |

---

## 8️⃣ Implementation Timeline

**Week 5 (December 16-20, 2025):**
- Day 1: Phase 1 (RED - 2 smoke tests)
- Day 2-3: Phase 2 (GREEN - implement 4 components)
- Day 4: Phase 3 (REFACTOR - GitHub Pages integration + performance)
- Day 5: Phase 4 (CUTOVER - parallel run + migration)

**Week 6 (December 23, 2025):**
- Day 1: Phase 5 (CLEANUP - documentation + legacy deletion preparation)

**Grace Period (December 23, 2025 - January 22, 2026):**
- Monitor production stability (error rate < 0.1%)
- User feedback collection
- Rollback capability maintained

**Permanent Deletion (January 22, 2026):**
- Remove archived files (2 files, 962 LOC)
- Delete rollback scripts
- Final validation

**Total Duration:** 5 days (implementation) + 30 days (grace period)

---

## 9️⃣ Risk Mitigation

### Risk: GitHub Pages Implementation Conflict

**Likelihood:** Medium (active implementation on separate machine)  
**Impact:** Medium (duplication of effort)  
**Mitigation:**
- Documentation Orchestrator COORDINATES with GitHub Pages work, doesn't replace it
- Orchestrator triggers site generation, GitHub Pages implementation handles rendering
- Clear separation: Orchestrator = data prep, GitHub Pages = presentation
- Regular sync meetings with GitHub Pages implementation team

### Risk: MkDocs Configuration Complexity

**Likelihood:** Medium (complex theme customization)  
**Impact:** Low (fallback to default theme)  
**Mitigation:**
- Start with MkDocs Material default theme
- Incremental customization (glassmorphism design added progressively)
- Template override system for advanced customization
- Documentation for theme configuration

### Risk: Multi-Language Docstring Extraction Accuracy

**Likelihood:** Medium (varies by language)  
**Impact:** Low (manual review available)  
**Mitigation:**
- Python: 95% accuracy (mature docstring support)
- C#: 85% accuracy (XML comments well-structured)
- JS/TS: 80% accuracy (JSDoc less standardized)
- Confidence scoring for low-quality docstrings
- Manual review for <0.85 confidence

---

## 🎯 Next Steps

1. **Create YAML Workflow:** `src/orchestration_3_0/workflows/documentation_workflow.yaml`
2. **Create Component Folders:** `src/orchestration_3_0/orchestrators/documentation/`
3. **Write Smoke Tests:** `tests/orchestration_3_0/orchestrators/test_documentation_orchestrator.py`
4. **Implement Core Orchestrator:** `documentation_orchestrator.py` (200 LOC)
5. **Implement GitHub Pages Generator:** `github_pages_generator.py` (200 LOC)
6. **Implement API Doc Generator:** `api_doc_generator.py` (150 LOC)
7. **Implement Report Builder:** `report_builder.py` (150 LOC)
8. **Integrate with Existing GitHub Pages Work:** Coordination meetings
9. **Performance Validation:** Benchmark generation times
10. **Documentation:** Usage guide + API docs

---

**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 SUB-PLAN COMPLETE - Ready for Phase 3 Implementation  
**Estimated Completion:** December 23, 2025 (implementation) + 30-day grace period

**Note:** This orchestrator COORDINATES with existing GitHub Pages implementation (separate machine), does NOT replace it. Enterprise Documentation Orchestrator (4,668 LOC) being replaced by GitHub Pages site is independent of this consolidation effort.
