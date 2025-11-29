# Phase 3: SWAGGER Entry Point Module - Architecture Design

**Feature:** Scope-Driven Sprint Estimation  
**Version:** CORTEX 3.3.0  
**Status:** ARCHITECTURE DESIGN  
**Date:** 2025-11-28  
**Approach:** A - Scope Inference + Confirmation (APPROVED)

---

## Executive Summary

**Goal:** Reduce scope interrogation by 70% while maintaining DoR accuracy through intelligent inference from existing Planning System 2.0 data.

**Strategy:** Leverage DoR Questions 3 & 6 (functional scope + technical dependencies) to automatically infer feature boundaries, eliminating redundant questioning.

**Key Innovation:** **Zero new questions** for 80% of cases - scope extracted from requirements already collected during DoR validation.

---

## Architecture Components

### 1. Scope Inference Engine

**Purpose:** Auto-extract feature boundaries from Planning DoR answers  
**Target:** <5 seconds execution time  
**Input:** Planning DoR responses (Q3: functional scope, Q6: technical dependencies)  
**Output:** Structured scope object with confidence scores

**Component:** `src/agents/estimation/scope_inference_engine.py`

**Methods:**
```python
class ScopeInferenceEngine:
    def parse_dor_answers(self, dor_responses: Dict) -> Dict:
        """Extract raw text from Q3 and Q6"""
        
    def extract_entities(self, requirements_text: str) -> ScopeEntities:
        """Identify tables, files, services, dependencies"""
        # Entity types:
        # - Database tables (e.g., "Users table", "user_accounts")
        # - Files/classes (e.g., "UserService.cs", "authentication.py")
        # - External services (e.g., "Azure AD", "SendGrid API")
        # - Dependencies (e.g., "requires OAuth", "depends on payment service")
        
    def calculate_confidence(self, entities: ScopeEntities) -> float:
        """Score confidence based on entity clarity and completeness"""
        # Factors:
        # - Explicit entity names (high confidence)
        # - Vague references like "user stuff" (low confidence)
        # - Quantified scope "15 tables" (high confidence)
        # - Relative scope "some tables" (low confidence)
        
    def generate_scope_boundary(self, entities: ScopeEntities, confidence: float) -> ScopeBoundary:
        """Create boundary map with estimated counts"""
        # Boundaries:
        # - Maximum 50 tables (prevents Oracle 100K+ explosion)
        # - Maximum 100 files
        # - Maximum 2-hop dependency depth
        # - 30-second timeout per analysis phase
```

**Data Structures:**
```python
@dataclass
class ScopeEntities:
    tables: List[str]  # ["Users", "UserProfiles", "Sessions"]
    files: List[str]   # ["UserService.cs", "AuthController.cs"]
    services: List[str]  # ["Azure AD", "SendGrid"]
    dependencies: List[str]  # ["OAuth", "JWT", "SMTP"]
    confidence_scores: Dict[str, float]  # Per-entity confidence

@dataclass
class ScopeBoundary:
    table_count: int
    file_count: int
    service_count: int
    dependency_depth: int
    estimated_complexity: float  # 0-100 scale
    confidence: float  # 0-100 overall confidence
    gaps: List[str]  # Missing information for clarification
```

**Confidence Thresholds:**
- **>70%** - High confidence, auto-proceed to analysis
- **30-70%** - Medium confidence, show preview + ask confirmation
- **<30%** - Low confidence, trigger clarification questions

---

### 2. Scope Validator

**Purpose:** Generate scope preview for user confirmation (NOT interrogation)  
**Target:** <2 seconds execution time  
**Input:** ScopeBoundary object  
**Output:** Human-readable preview + yes/no prompt

**Component:** `src/agents/estimation/scope_validator.py`

**Methods:**
```python
class ScopeValidator:
    def generate_preview(self, boundary: ScopeBoundary) -> str:
        """Create human-readable scope summary"""
        # Example output:
        # "I detected the following scope for this feature:
        #  - 15 database tables (Users, UserProfiles, Sessions, ...)
        #  - 8 files (UserService.cs, AuthController.cs, ...)
        #  - 3 external services (Azure AD, SendGrid, Twilio)
        #  - 2-hop dependency depth
        #  
        #  Is this correct? (yes/no/partial)"
        
    def handle_confirmation(self, user_response: str, boundary: ScopeBoundary) -> ConfirmationResult:
        """Process user confirmation"""
        # Responses:
        # - "yes" → Proceed to analysis
        # - "no" → Trigger clarification questions
        # - "partial" → Show entity list for user to remove/add
```

**Key Difference from Questionnaire:**
- **NOT**: "What tables will you modify?" (open-ended question)
- **IS**: "I detected these 15 tables. Correct?" (yes/no confirmation)
- **Benefit**: 90% faster than interrogation (5s vs 2-5 min)

---

### 3. Clarification Orchestrator

**Purpose:** Ask targeted questions ONLY when confidence <30%  
**Target:** 3-5 questions maximum, 2-5 minutes total  
**Activation:** Conditional - only for ambiguous requirements

**Component:** `src/agents/estimation/clarification_orchestrator.py`

**Methods:**
```python
class ClarificationOrchestrator:
    def identify_gaps(self, boundary: ScopeBoundary) -> List[str]:
        """Detect missing critical information"""
        # Gap types:
        # - No tables mentioned → "What database tables will be affected?"
        # - Vague service reference → "You mentioned UserService - does this include authentication or just CRUD?"
        # - Unclear dependencies → "Will this integrate with existing payment system?"
        
    def generate_targeted_questions(self, gaps: List[str]) -> List[Question]:
        """Create 3-5 specific questions to fill gaps"""
        # Question format:
        # - Short (single sentence)
        # - Specific (reference gap context)
        # - Closed-ended when possible
        
    def update_scope_from_answers(self, questions: List[Question], answers: List[str]) -> ScopeBoundary:
        """Merge clarification answers into scope boundary"""
```

**Clarification vs Full Questionnaire:**
- **Questionnaire**: 15-20 questions, 10-15 min, every time
- **Clarification**: 3-5 questions, 2-5 min, <20% cases
- **Savings**: 70% time reduction on average

---

### 4. Swagger Crawler (Boundary-Aware Analysis)

**Purpose:** Targeted codebase analysis respecting scope boundaries  
**Target:** <30 seconds per analysis phase  
**Input:** ScopeBoundary with confirmed entities  
**Output:** Complexity metrics for estimation

**Component:** `src/agents/estimation/swagger_crawler.py`

**Methods:**
```python
class SwaggerCrawler:
    def __init__(self, boundary: ScopeBoundary):
        self.boundary = boundary
        self.max_tables = 50
        self.max_files = 100
        self.max_dependency_depth = 2
        self.timeout_seconds = 30
        
    def analyze_codebase_structure(self, entities: ScopeEntities) -> ComplexityMetrics:
        """Crawl only confirmed entities (not entire codebase)"""
        # Respects boundaries:
        # - Only analyze tables in boundary.tables list
        # - Only scan files matching boundary.files patterns
        # - Only traverse dependencies to boundary.dependency_depth
        
    def find_similar_features(self, scope: ScopeBoundary) -> List[HistoricalFeature]:
        """Search Enhancement Catalog for similar scope patterns"""
        # Similarity factors:
        # - Table count match (±20%)
        # - File count match (±20%)
        # - Service overlap (>=50%)
        
    def calculate_complexity_score(self, metrics: ComplexityMetrics) -> float:
        """Weighted complexity calculation (0-100 scale)"""
        # Factors (from questionnaire - ALL selected):
        # - Technical debt score (weight: 7/10)
        # - Unknown dependencies (weight: 8/10)
        # - Stack unfamiliarity (weight: 6/10)
        # - Integration complexity (weight: 9/10)
        # - Data model changes (weight: 8/10)
        # - UI/UX complexity (weight: 5/10)
        # - Security requirements (weight: 7/10)
        # - Performance requirements (weight: 6/10)
        # - Testing complexity (weight: 7/10)
```

**Enterprise Monolith Protection:**
- **Before Scope Inference**: Would analyze entire 100K+ table database
- **After Scope Inference**: Only analyzes 15 tables mentioned in requirements
- **Benefit**: 99.98% reduction in analysis scope (15 vs 100,000 tables)

---

### 5. Swagger Estimator (Three-Point PERT)

**Purpose:** Calculate sprint estimation with confidence intervals  
**Target:** <5 seconds calculation time  
**Input:** ComplexityMetrics from crawler  
**Output:** Three-point estimate (Best/Most Likely/Worst)

**Component:** `src/agents/estimation/swagger_estimator.py`

**Methods:**
```python
class SwaggerEstimator:
    def estimate_feature(self, metrics: ComplexityMetrics, team_capacity: TeamCapacity) -> Estimation:
        """Calculate three-point estimate using PERT formula"""
        
    def calculate_base_estimate(self, complexity_score: float, historical_data: List[HistoricalFeature]) -> float:
        """Base estimate from complexity + similar features"""
        # Sources:
        # 1. Historical data (if available) - 70% weight
        # 2. Industry defaults (bootstrap) - 30% weight
        
    def apply_pert_formula(self, base_estimate: float) -> ThreePointEstimate:
        """PERT formula for uncertainty"""
        # Best case = base_estimate * 0.7
        # Most likely = base_estimate
        # Worst case = base_estimate * 1.5
        # 
        # Weighted average: (best + 4*most_likely + worst) / 6
        
    def calculate_confidence(self, metrics: ComplexityMetrics, team_capacity: TeamCapacity) -> float:
        """Confidence score (0-100%)"""
        # Factors:
        # - Historical data available (30% weight)
        # - Complexity score (20% weight)
        # - Team velocity known (25% weight)
        # - Similar features found (15% weight)
        # - Scope confidence (10% weight)
```

**Data Structures:**
```python
@dataclass
class ThreePointEstimate:
    best_case: float  # Sprints
    most_likely: float
    worst_case: float
    weighted_average: float  # PERT calculation
    confidence: float  # 0-100%
    complexity_factors: Dict[str, float]  # Breakdown for transparency

@dataclass
class TeamCapacity:
    team_size: int
    velocity: float  # Story points/sprint
    sprint_length_days: int
    capacity_percentage: int  # 70% default (SAFe)
    methodology: str  # SAFe, Scrum, Kanban
```

**Confidence Color Coding (from questionnaire):**
- 🟢 **High (70-100%)**: Strong historical data + clear scope
- 🟡 **Medium (40-69%)**: Some historical data or moderate complexity
- 🔴 **Low (0-39%)**: No historical data or high uncertainty

---

## Workflow Integration

### Planning System 2.0 Integration Point

**Location:** `PlanningOrchestrator.generate_plan()`  
**Trigger:** After DoR validation, before implementation planning

```python
# In PlanningOrchestrator.generate_plan()
async def generate_plan(self, requirements: str, enable_estimation: bool = True):
    # Step 1: DoR Validation (existing)
    dor_responses = await self.validate_dor(requirements)
    
    # Step 2: SWAGGER Estimation (NEW)
    if enable_estimation:
        # Initialize SWAGGER components
        scope_engine = ScopeInferenceEngine()
        validator = ScopeValidator()
        
        # Extract scope from DoR
        entities = scope_engine.extract_entities(dor_responses['Q3'] + dor_responses['Q6'])
        boundary = scope_engine.generate_scope_boundary(entities)
        
        # Confidence check
        if boundary.confidence > 0.70:
            # High confidence - auto-proceed
            logger.info("High confidence scope, proceeding to analysis")
        elif boundary.confidence > 0.30:
            # Medium confidence - preview confirmation
            preview = validator.generate_preview(boundary)
            user_confirmation = await self.prompt_user(preview)
            if user_confirmation == "no":
                clarifier = ClarificationOrchestrator()
                boundary = await clarifier.clarify_scope(boundary)
        else:
            # Low confidence - clarification required
            clarifier = ClarificationOrchestrator()
            boundary = await clarifier.clarify_scope(boundary)
        
        # Crawl and analyze
        crawler = SwaggerCrawler(boundary)
        metrics = await crawler.analyze_codebase_structure(entities)
        
        # Estimate
        estimator = SwaggerEstimator()
        team_capacity = self.load_team_capacity()
        estimation = estimator.estimate_feature(metrics, team_capacity)
        
        # Add to planning document
        dor_responses['estimation'] = {
            'best_case': estimation.best_case,
            'most_likely': estimation.most_likely,
            'worst_case': estimation.worst_case,
            'confidence': estimation.confidence,
            'complexity_factors': estimation.complexity_factors
        }
    
    # Step 3: Implementation Planning (existing)
    plan = await self.generate_implementation_phases(dor_responses)
    return plan
```

---

## Rollback Integration

### Three Checkpoint Levels

**Checkpoints Created:**
1. **pre-scope-analysis** - Before scope inference runs
2. **post-complexity-analysis** - After complexity calculated
3. **post-estimation** - After final estimation generated

**Auto-Rollback Triggers:**
- Scope exceeds boundaries (>50 tables, >100 files)
- Analysis timeout (>30 seconds per phase)
- Confidence <30% without clarification
- Missing team capacity data (hard dependency)

**Rollback Command:** `rollback to pre-scope-analysis`

---

## Success Metrics

### Quantitative Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Inference Accuracy | >80% | Validate against Planning DoR |
| Clarification Rate | <20% | % of cases triggering clarification |
| Scope Report Time | <5s | Execution time for scope inference |
| Redundant Questions | 0% | Leverage existing DoR answers |
| Estimation Time | <30s | Total time from DoR to estimation |
| Estimation Accuracy | ±30% | Compare to actual time (historical validation) |

### Qualitative Targets

- ✅ Zero user frustration from redundant questions
- ✅ Transparent scope boundary (user can review/modify)
- ✅ Confidence scoring visible (user understands certainty)
- ✅ Graceful degradation (works without historical data)

---

## Implementation Phases

### Phase 3.1: Requirements Refinement ✅
**Status:** COMPLETE (this document)  
**Duration:** 1 day  
**Deliverables:**
- ✅ Architecture design document
- ✅ Component specifications
- ✅ Data structure definitions
- ✅ Integration points identified

### Phase 3.2: Scope Inference Engine
**Status:** NEXT (TDD RED → GREEN)  
**Duration:** 2 days  
**Deliverables:**
- [ ] RED: Failing tests for scope extraction
- [ ] GREEN: Working ScopeInferenceEngine
- [ ] REFACTOR: Optimize entity detection

### Phase 3.3: Scope Validator + Clarification
**Status:** PENDING  
**Duration:** 1 day  
**Deliverables:**
- [ ] ScopeValidator with preview generation
- [ ] ClarificationOrchestrator with gap detection
- [ ] User interaction flows

### Phase 3.4: Swagger Crawler
**Status:** PENDING  
**Duration:** 2 days  
**Deliverables:**
- [ ] Boundary-aware codebase analysis
- [ ] Enhancement Catalog integration
- [ ] Complexity scoring with all factors

### Phase 3.5: Swagger Estimator
**Status:** PENDING  
**Duration:** 2 days  
**Deliverables:**
- [ ] Three-point PERT estimation
- [ ] Confidence scoring
- [ ] Historical data learning

### Phase 3.6: Planning Integration
**Status:** PENDING  
**Duration:** 1 day  
**Deliverables:**
- [ ] Wire into PlanningOrchestrator
- [ ] Add to planning template
- [ ] Store history in Tier 3

### Phase 3.7: Testing & Validation
**Status:** PENDING  
**Duration:** 1 day  
**Deliverables:**
- [ ] Validate against historical data
- [ ] Performance testing (<30s target)
- [ ] User acceptance testing

---

## File Structure

```
src/agents/estimation/
├── __init__.py
├── scope_inference_engine.py  # Phase 3.2
├── scope_validator.py         # Phase 3.3
├── clarification_orchestrator.py  # Phase 3.3
├── swagger_crawler.py         # Phase 3.4
└── swagger_estimator.py       # Phase 3.5

tests/
├── test_scope_inference.py    # Phase 3.2
├── test_scope_validation.py   # Phase 3.3
├── test_swagger_crawler.py    # Phase 3.4
├── test_swagger_estimator.py  # Phase 3.5
└── test_swagger_integration.py  # Phase 3.6
```

---

## Next Steps

1. ✅ Review and approve architecture design
2. ⏳ Start Phase 3.2: Scope Inference Engine (TDD RED phase)
3. ⏳ Write failing tests for scope extraction from DoR
4. ⏳ Implement ScopeInferenceEngine (TDD GREEN phase)
5. ⏳ Proceed through remaining phases sequentially

---

**Document Status:** READY FOR IMPLEMENTATION  
**Approval Required:** Architecture review complete, proceed to Phase 3.2  
**Last Updated:** 2025-11-28 10:30 AM PST
