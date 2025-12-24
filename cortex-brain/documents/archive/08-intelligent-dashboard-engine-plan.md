# 🧠 Intelligent Dashboard Engine - Sub-Plan

**Purpose:** Tree-sitter AST-powered reverse engineering for dashboard auto-population  
**Complexity:** HIGH (AST analysis + multi-language support + specialized extractors)  
**LOC:** 2,800 (NEW capability - no legacy code)  
**Test Strategy:** SMOKE TEST ONLY (2 tests: initialization + AST extraction workflow)

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Scaffolding Orchestrator Plan](10-scaffolding-orchestrator-plan.md)
- **Next:** [Observability Orchestrator Plan](08-observability-orchestrator-plan.md)
- **Related:** [intelligent-dashboard-enhancement-plan.md](../intelligent-dashboard-enhancement-plan.md)
- **Workflow YAML:** `src/orchestration_3_0/workflows/intelligent_dashboard_workflow.yaml`

---

## 1️⃣ Existing State (Current Dashboard System)

### Current Dashboard Pain Points

| Issue | Impact | Manual Effort |
|-------|--------|---------------|
| **Manual Use Case Collection** | Incomplete coverage (10-20% of actual use cases) | 2-3 hours per project |
| **Template-Based Executive Summary** | Generic, low value to stakeholders | 1-2 hours per project |
| **File Scanning Redundancy** | Parse file → scan again → analyze again = 3x I/O | 5-10 minutes for 1k+ files |
| **No Business Logic Detection** | Misses financial calculations, formulas, compliance code | N/A (not attempted) |
| **No Semantic Analysis** | Regex patterns only, no AST-level understanding | N/A (not possible) |

### Current Collectors (To Be Enhanced)

| Collector | Current Method | LOC | Enhancement Opportunity |
|-----------|----------------|-----|-------------------------|
| `use_case_collector.py` | Regex pattern matching | 180 | Replace with AST inference → 4x coverage |
| `executive_summary_aggregator.py` | Template filling | 220 | Replace with narrative generation → 95% automated |
| `recommendation_aggregator.py` | Pattern-based | 150 | Enhance with code smell → recommendation mapping |
| `tech_stack_collector.py` | File extension scanning | 160 | Enhance with AST framework detection |

**Total Current LOC:** ~700 lines (inefficient, low accuracy)

### Current Workflow (High-Level)

1. **Scan File System:** Enumerate files by extension
2. **Pattern Matching:** Regex search for endpoints, classes, methods
3. **Template Filling:** Insert matched patterns into predefined templates
4. **Manual Review:** User corrects 40-60% of generated content
5. **Output:** Dashboard JSON with low confidence scores (0.50-0.65)

### Current Issues & Technical Debt

**Accuracy Problems:**
- **Use Cases:** 10-20% coverage (misses 80-90% of actual functionality)
- **Executive Summary:** Generic narratives that don't capture unique business value
- **Recommendations:** Surface-level (e.g., "Add tests") without specific actionable steps

**Performance Problems:**
- **File Scanning:** Read file 3x (scan → parse → analyze) = redundant I/O
- **No Incremental Analysis:** Full rescan even if only 1 file changed
- **No Caching:** Reparse same files on every dashboard refresh

**Scalability Problems:**
- **Large Repos (10k+ files):** 5-15 minutes for full scan (unacceptable UX)
- **No Parallel Processing:** Single-threaded file enumeration
- **Memory Limits:** Load entire file into memory for regex scanning

---

## 2️⃣ New Structure: Intelligent Dashboard Engine

### Target Architecture

```
src/
└── intelligence/
    ├── dashboard_ast_engine.py                  # Core AST engine (600 LOC)
    ├── business_logic_extractor.py              # Financial calculations, formulas (400 LOC)
    ├── financial_data_detector.py               # Currency, PCI/SOX patterns (350 LOC)
    ├── use_case_inference.py                    # API → use case mapping (400 LOC)
    ├── executive_summary_generator.py           # Narrative synthesis (350 LOC)
    ├── recommendation_intelligence.py           # Code smell → recommendation (250 LOC)
    ├── onboarding_generator.py                  # 6-stage onboarding (450 LOC)
    └── tree_sitter_parser.py                    # Multi-language parser (280 LOC - EXISTING)

TOTAL: 2,800 LOC (NEW) + 280 LOC (EXISTING) = 3,080 LOC
```

### Component Responsibilities

#### 1. Dashboard AST Engine (`dashboard_ast_engine.py` - 600 LOC)

**Purpose:** Orchestrate AST-powered dashboard data collection

**Key Features:**
- **Reuse TreeSitterParser:** Leverage existing `src/intelligence/tree_sitter_parser.py` (280 LOC)
- **Parallel Processing:** ProcessPoolExecutor for 100k+ LOC codebases (worker pools)
- **Incremental Analysis:** Git diff detection → only reparse changed files
- **3-Tier Caching:**
  - **AST Cache:** LRU cache for parsed trees (in-memory)
  - **Result Cache:** Extracted insights (in-memory)
  - **SQLite Cache:** Long-term storage for 10k+ files
- **Streaming Results:** Render-as-you-go (no blocking on full scan)

**API Contract:**
```python
class DashboardASTEngine:
    def __init__(
        self, 
        repo_path: str, 
        cache_enabled: bool = True,
        parallel_workers: int = 4
    ):
        """Initialize AST engine with Tree-sitter parser."""
        self.parser = TreeSitterParser()  # Reuse existing parser
        self.cache = ASTCache() if cache_enabled else None
        self.workers = parallel_workers
    
    def analyze_repository(self) -> DashboardInsights:
        """
        Full repository analysis (parallel processing).
        
        Returns:
            DashboardInsights with use cases, business logic, 
            executive summary, recommendations
        """
        pass
    
    def analyze_incremental(self, changed_files: List[str]) -> DashboardInsights:
        """Incremental analysis (Git diff detection)."""
        pass
```

**Performance Targets:**
- Small repos (<100 files): <2 seconds
- Medium repos (100-1k files): <10 seconds
- Large repos (1k-10k files): <60 seconds
- Extra-large repos (10k-100k files): <5 minutes (with distributed option)

#### 2. Business Logic Extractor (`business_logic_extractor.py` - 400 LOC)

**Purpose:** Detect financial calculations, formulas, business rules

**Key Features:**
- **Formula Detection:** Tree-sitter AST node analysis for:
  - Mathematical operations (multiply, divide, power, modulo)
  - Complex calculations (nested expressions)
  - Financial patterns (interest, tax, currency conversion)
- **Business Rules Extraction:** 
  - Conditionals encoding business decisions (if/switch statements with business terms)
  - Validation logic (credit checks, eligibility rules)
- **Confidence Scoring:** 0.88 (high - based on AST node types)

**API Contract:**
```python
class BusinessLogicExtractor:
    def extract_formulas(self, ast_tree: Tree, source_code: str) -> List[Formula]:
        """
        Extract mathematical formulas from AST.
        
        Returns:
            List of Formula objects with:
            - formula_text: Original expression
            - location: File path + line number
            - complexity: Low/Medium/High
            - confidence: 0.0-1.0
        """
        pass
    
    def extract_business_rules(self, ast_tree: Tree, source_code: str) -> List[BusinessRule]:
        """Extract conditionals encoding business logic."""
        pass
```

**Example Output:**
```json
{
  "formulas": [
    {
      "formula_text": "principal * (1 + interest_rate) ** years",
      "location": "finance/calculator.py:45",
      "complexity": "medium",
      "confidence": 0.92,
      "category": "interest_calculation"
    }
  ],
  "business_rules": [
    {
      "rule_text": "if credit_score > 700 and income > 50000",
      "location": "credit/eligibility.py:28",
      "confidence": 0.88,
      "category": "credit_approval"
    }
  ]
}
```

#### 3. Financial Data Detector (`financial_data_detector.py` - 350 LOC)

**Purpose:** Identify financial code patterns, PCI/SOX compliance markers

**Key Features:**
- **Pattern Matching:** Regex + AST for:
  - Currency symbols ($, €, £, ¥)
  - Decimal patterns (money amounts)
  - Financial terms (payment, invoice, transaction, account)
- **Entity Recognition:** Tree-sitter class node queries for:
  - Account, Transaction, Payment, Invoice classes
  - Financial service layers (*PaymentService, *BillingManager)
- **Calculation Flows:** Trace data through financial pipelines (AST traversal)
- **Compliance Markers:** Detect PCI/SOX-sensitive code (credit card, SSN patterns)

**API Contract:**
```python
class FinancialDataDetector:
    def detect_financial_entities(self, ast_tree: Tree, source_code: str) -> List[FinancialEntity]:
        """Detect financial domain classes."""
        pass
    
    def detect_compliance_markers(self, ast_tree: Tree, source_code: str) -> List[ComplianceMarker]:
        """Identify PCI/SOX-sensitive code."""
        pass
```

#### 4. Use Case Inference Engine (`use_case_inference.py` - 400 LOC)

**Purpose:** Infer use cases from API endpoints, controller actions, service methods

**Key Features:**
- **API Endpoint Analysis:** Tree-sitter queries for:
  - Python: `@app.route('/users', methods=['POST'])` → "Create new user account"
  - C#: `[HttpGet("/orders/{id}")]` → "Retrieve order details"
  - JS/TS: `express.Router().post('/payments')` → "Process payment"
- **Controller Actions:** Analyze method signatures + docstrings
- **Service Layer Detection:** `*Service`, `*Manager`, `*Repository` patterns
- **Confidence Scoring:**
  - API endpoint → 0.95
  - Controller action → 0.90
  - Service method → 0.85
  - Inferred from class name → 0.70

**API Contract:**
```python
class UseCaseInferenceEngine:
    def infer_from_api_endpoints(self, ast_tree: Tree, source_code: str) -> List[UseCase]:
        """Extract use cases from API route decorators."""
        pass
    
    def infer_from_controller_actions(self, ast_tree: Tree, source_code: str) -> List[UseCase]:
        """Extract use cases from controller method names."""
        pass
```

**Expected Impact:** 10-20% coverage → 80-90% coverage (4x improvement)

#### 5. Executive Summary Generator (`executive_summary_generator.py` - 350 LOC)

**Purpose:** Auto-generate "What It Does" narratives from AST

**Key Features:**
- **Narrative Synthesis:** Combine insights:
  - Entry points (from EPMO parser)
  - API endpoints (from AST)
  - Key business entities (from class names)
  - Service methods (from AST)
  - Generate natural language summary
- **Architecture Detection:** AST structural analysis for:
  - Layered (presentation → business → data)
  - Microservices (multiple entry points, separate databases)
  - MVC (models, views, controllers)
  - Clean Architecture (domain entities, use cases, adapters)
- **Capability Extraction:** Public APIs, workflows, integrations
- **Output:** Executive summary JSON (95%+ automated, 5% manual review)

**API Contract:**
```python
class ExecutiveSummaryGenerator:
    def generate_what_it_does(self, ast_insights: DashboardInsights) -> ExecutiveSummary:
        """
        Generate natural language summary.
        
        Returns:
            ExecutiveSummary with:
            - project_name
            - description (2-3 paragraphs)
            - key_highlights (top 5 capabilities)
            - confidence_score (0.0-1.0)
        """
        pass
    
    def detect_architecture(self, ast_insights: DashboardInsights) -> ArchitecturePattern:
        """Detect architecture pattern from code structure."""
        pass
```

#### 6. Recommendation Intelligence (`recommendation_intelligence.py` - 250 LOC)

**Purpose:** Transform code smells → actionable recommendations

**Key Features:**
- **Code Smell Mapping:** AST-detected anti-patterns → recommendations
  - God object (500+ LOC) → "Refactor into 3-5 smaller classes"
  - High complexity (CCN > 40) → "Extract 2-3 helper methods"
  - Tight coupling → "Introduce dependency injection"
- **Prioritization:** High/Medium/Low impact + effort estimation
- **Actionable Steps:** Specific refactoring guidance (not generic "fix this")

**API Contract:**
```python
class RecommendationIntelligence:
    def generate_recommendations(self, code_smells: List[CodeSmell]) -> List[Recommendation]:
        """
        Transform code smells into actionable recommendations.
        
        Returns:
            List of Recommendation objects with:
            - title: "Refactor UserController (God Object)"
            - priority: High/Medium/Low
            - effort: 2-4 hours
            - steps: ["Extract authentication logic", "Create UserValidator"]
        """
        pass
```

#### 7. Onboarding Generator (`onboarding_generator.py` - 450 LOC)

**Purpose:** Auto-create 6-stage onboarding with Mermaid diagrams

**Key Features:**
- **6-Stage Onboarding:** Setup → Architecture → Core Features → Advanced → Testing → Deployment
- **Auto-Generated Diagrams:** Mermaid flowcharts from AST analysis
- **Role-Based Paths:** Developer, QA, DevOps, Manager
- **Confidence Scoring:** 0.85 (based on AST completeness)

---

## 3️⃣ Migration Strategy (5 Phases with TDD)

### Phase 1: RED (Tests First) - Week 4, Day 1-2

**Objective:** Write 2 smoke tests (initialization + AST extraction workflow)

**Smoke Tests (2 tests):**
- [ ] **Test 1: Initialization**
  - Initialize DashboardASTEngine with repo path
  - Verify TreeSitterParser loaded
  - Verify cache enabled
  - Verify parallel workers configured
  
- [ ] **Test 2: AST Extraction Workflow**
  - Analyze small test repository (50 files)
  - Verify use cases extracted (>0 results)
  - Verify executive summary generated
  - Verify recommendations produced
  - Execution time < 5 seconds

**Validation:** Both tests RED (no implementation yet)

**Timeline:** 1 day (December 10, 2025)

### Phase 2: GREEN (Core Implementation) - Week 4, Day 3-5

**Objective:** Implement 7 components + make tests pass

**Day 3: Core Engine + Business Logic Extractor**
- [ ] Implement `DashboardASTEngine` (600 LOC)
  - Parallel processing with ProcessPoolExecutor
  - Incremental analysis (Git diff detection)
  - 3-tier caching (LRU + SQLite)
- [ ] Implement `BusinessLogicExtractor` (400 LOC)
  - Formula detection via AST node analysis
  - Business rules extraction

**Day 4: Financial + Use Case + Executive Summary**
- [ ] Implement `FinancialDataDetector` (350 LOC)
  - Currency pattern detection
  - Compliance marker identification
- [ ] Implement `UseCaseInferenceEngine` (400 LOC)
  - API endpoint → use case mapping
  - Controller action analysis
- [ ] Implement `ExecutiveSummaryGenerator` (350 LOC)
  - Narrative synthesis from AST insights
  - Architecture pattern detection

**Day 5: Recommendations + Onboarding + Integration**
- [ ] Implement `RecommendationIntelligence` (250 LOC)
  - Code smell → recommendation mapping
- [ ] Implement `OnboardingGenerator` (450 LOC)
  - 6-stage onboarding with Mermaid diagrams
- [ ] Integration: Wire all components into DashboardASTEngine

**Validation:** 2/2 smoke tests GREEN, execution time < 5 seconds

**Timeline:** 3 days (December 11-13, 2025)

### Phase 3: REFACTOR (Performance + Scalability) - Week 5, Day 1-2

**Objective:** Optimize for large repos (10k+ files)

**Performance Optimizations:**
- [ ] Benchmark with 1k, 5k, 10k file repos
- [ ] Tune ProcessPoolExecutor worker count (4 → 8 → 16)
- [ ] Implement streaming results (render-as-you-go)
- [ ] Add distributed processing option (Celery for 50k+ files)

**Scalability Enhancements:**
- [ ] LRU cache size tuning (100 → 500 → 1000 entries)
- [ ] SQLite cache indexing (file_path, timestamp)
- [ ] Memory profiling (ensure <2GB for 10k files)

**Validation:** 
- Small repos (<100 files): <2 seconds ✅
- Medium repos (100-1k files): <10 seconds ✅
- Large repos (1k-10k files): <60 seconds ✅

**Timeline:** 2 days (December 16-17, 2025)

### Phase 4: CUTOVER (Integration with Observability Orchestrator) - Week 5, Day 3

**Objective:** Integrate with Observability Orchestrator

**Integration Steps:**
- [ ] Update `cortex-operations.yaml` with intelligent dashboard triggers
- [ ] Wire DashboardASTEngine into Observability Orchestrator
- [ ] Update dashboard collectors to use AST engine
- [ ] Parallel run: Old collectors + new AST engine (compare outputs)

**Validation:**
- New AST engine produces 4x more use cases ✅
- Executive summary confidence > 0.95 ✅
- Recommendations actionable (manual review) ✅
- Performance < 60 seconds for 10k files ✅

**Timeline:** 1 day (December 18, 2025)

### Phase 5: CLEANUP (Documentation + Handoff) - Week 5, Day 4-5

**Objective:** Document AST engine capabilities

**Documentation:**
- [ ] Create `intelligent-dashboard-ast-engine.md` (usage guide)
- [ ] Update `orchestration-master-plan.md` with Phase 3 completion
- [ ] Generate API documentation for all 7 components
- [ ] Create performance benchmarking report

**Handoff:**
- [ ] Train team on AST engine capabilities
- [ ] Demonstrate 4x use case coverage improvement
- [ ] Show 95%+ automated executive summary

**Validation:** Documentation complete, team trained

**Timeline:** 2 days (December 19-20, 2025)

---

## 4️⃣ Test Coverage Requirements (PRAGMATIC - SMOKE TEST)

### Smoke Tests (2 tests)

| Test | Purpose | Expected Outcome |
|------|---------|------------------|
| **Test 1: Initialization** | Verify DashboardASTEngine initializes correctly | TreeSitterParser loaded, cache enabled, workers configured |
| **Test 2: AST Extraction** | Verify end-to-end workflow (analyze repo → generate insights) | Use cases > 0, executive summary generated, recommendations produced, time < 5s |

**No comprehensive unit tests:** AST engine is integration-heavy (Tree-sitter + parallel processing + caching). Real-world validation more valuable than mocked scenarios.

**Coverage Target:** N/A (smoke tests validate critical workflows only)

---

## 5️⃣ Wiring Validation Checklist

### Integration Points

- [ ] **TreeSitterParser Integration**
  - DashboardASTEngine imports `src/intelligence/tree_sitter_parser.py`
  - Verify all language grammars available (Python, JS, C#)
  - Verify v0.25 API compatibility (Query, QueryCursor)

- [ ] **Observability Orchestrator Integration**
  - DashboardASTEngine registered in ObservabilityOrchestrator
  - Dashboard collectors call AST engine for enhanced data
  - Streaming results integrated with dashboard UI

- [ ] **Caching Integration**
  - LRU cache for AST trees (in-memory)
  - SQLite cache for extracted insights (persistent)
  - Git diff detection for incremental analysis

- [ ] **Parallel Processing**
  - ProcessPoolExecutor with 4-16 workers
  - Worker pool creation/cleanup
  - Error handling in parallel execution

- [ ] **cortex-operations.yaml**
  - Natural language triggers: "intelligent dashboard", "AST analysis", "auto-generate executive summary"
  - Module path: `intelligence.dashboard_ast_engine`

---

## 6️⃣ Complete Removal Strategy

**No Legacy Code to Remove:** Intelligent Dashboard Engine is a NEW capability (no existing implementation).

**Enhanced Collectors:** Following collectors will be **enhanced** (not deleted):
- `use_case_collector.py` → Calls `UseCaseInferenceEngine` for AST-powered inference
- `executive_summary_aggregator.py` → Calls `ExecutiveSummaryGenerator` for narrative synthesis
- `recommendation_aggregator.py` → Calls `RecommendationIntelligence` for code smell mapping

**Archive Location:** N/A (no legacy code)

**Grace Period:** N/A (new capability)

**Rollback Script:** N/A (no legacy code to roll back to)

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

| Metric | Before (File Scan) | After (AST Engine) | Improvement |
|--------|-------------------|-------------------|-------------|
| Small repos (<100 files) | 10-15 seconds | <2 seconds | **85% faster** |
| Medium repos (100-1k files) | 2-5 minutes | <10 seconds | **95% faster** |
| Large repos (1k-10k files) | 10-20 minutes | <60 seconds | **95% faster** |
| Manual Effort | 60% manual review | 5% manual review | **91% automation** |

### Code Quality

| Metric | Target | Status |
|--------|--------|--------|
| Total LOC | 2,800 (new) | To be implemented |
| Smoke Tests | 2 tests | To be implemented |
| Performance Targets | <60s for 10k files | To be validated |
| Confidence Scoring | 0.85-0.95 | To be validated |

---

## 8️⃣ Implementation Timeline

**Week 4 (December 10-13, 2025):**
- Day 1-2: Phase 1 (RED - 2 smoke tests)
- Day 3-5: Phase 2 (GREEN - implement 7 components)

**Week 5 (December 16-20, 2025):**
- Day 1-2: Phase 3 (REFACTOR - performance optimization)
- Day 3: Phase 4 (CUTOVER - integrate with Observability Orchestrator)
- Day 4-5: Phase 5 (CLEANUP - documentation + handoff)

**Total Duration:** 8 days

---

## 9️⃣ Risk Mitigation

### Risk: Tree-sitter Language Grammar Compatibility

**Likelihood:** Low (already verified in dev environment)  
**Impact:** High (blocks AST parsing)  
**Mitigation:**
- Tree-sitter v0.25 API already working (Query, QueryCursor)
- All language grammars installed (tree-sitter-python, tree-sitter-javascript, tree-sitter-c-sharp)
- Test suite validates parser functionality

### Risk: Performance Degradation on Large Repos (50k+ files)

**Likelihood:** Medium  
**Impact:** Medium (slow dashboard generation)  
**Mitigation:**
- Incremental analysis (Git diff detection)
- 3-tier caching (LRU + SQLite)
- Distributed processing option (Celery)
- Streaming results (render-as-you-go)

### Risk: Confidence Scoring Accuracy

**Likelihood:** Medium  
**Impact:** Low (users can override)  
**Mitigation:**
- Conservative confidence thresholds (0.70 min)
- Manual review for low-confidence insights (<0.85)
- Feedback loop to improve scoring algorithm

---

## 🎯 Next Steps

1. **Create YAML Workflow:** `src/orchestration_3_0/workflows/intelligent_dashboard_workflow.yaml`
2. **Create Component Folders:** `src/intelligence/` (already exists)
3. **Write Smoke Tests:** `tests/intelligence/test_dashboard_ast_engine.py`
4. **Implement Core Engine:** `dashboard_ast_engine.py` (600 LOC)
5. **Implement Extractors:** 6 specialized modules (2,200 LOC)
6. **Integrate with Observability Orchestrator:** Wire AST engine into dashboard collectors
7. **Performance Validation:** Benchmark with 1k, 5k, 10k file repos
8. **Documentation:** Usage guide + API docs

---

**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 SUB-PLAN COMPLETE - Ready for Phase 3 Implementation  
**Estimated Completion:** December 20, 2025
