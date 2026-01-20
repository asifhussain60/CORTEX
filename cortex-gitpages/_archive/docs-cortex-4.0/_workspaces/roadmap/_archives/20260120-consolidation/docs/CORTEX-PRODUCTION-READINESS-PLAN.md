## 🧠 CORTEX Production Readiness - 5-Week Implementation Plan
**Author:** Asif Hussain | **Phase:** PHASE-17-PRODUCTION | **Orchestrator:** MasterOrchestrator ✅

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

# CORTEX Master Orchestrator - Path to 100% Production Readiness

**Plan Created:** 2026-01-17  
**Target Completion:** 2026-02-21 (5 weeks)  
**Current Status:** 40% Ready (40 → 100%)  
**Team Capacity:** 1 Senior Developer OR 2-3 Junior Developers  

---

## Executive Summary

This plan details all work required to achieve **100% production readiness** for the CORTEX Master Orchestrator system. The plan is organized as 15 AC-IDs (Action Items) across 5 phases, with TDD approach and comprehensive testing.

**Key Metrics:**
- **Current Pass Rate:** 84% (38/45 Master tests passing)
- **Current Integration:** 60% (5/8 Master-Interaction tests passing)
- **Target:** 100% pass rate + all components integrated + production hardened

---

## Phase 1: Quick Wins & Foundation (Week 1)

### 🟢 AC-PROD-001-01: Fix Import Bugs & Get to 100% Test Pass Rate

**Status:** ✅ PARTIALLY DONE (Path import fixed)

**Remaining Work:**
- [ ] Run full test suite
- [ ] Fix any remaining import issues
- [ ] Achieve 100% pass rate on all MasterOrchestrator tests

**Files to Update:**
- ✅ `tests/integration/test_master_interaction_orchestration.py` (FIXED)
- Check for other missing imports

**Acceptance Tests:**
```gherkin
GIVEN all test files are syntactically correct
WHEN pytest runs tests/unit/core/orchestrator/
AND pytest runs tests/integration/test_master_*
THEN all tests PASS (100% pass rate)
AND no import errors occur
```

**Effort:** 1 hour  
**Dependencies:** None  
**Git Checkpoint:** `AC-PROD-001-01-import-fixes`

---

### 🔵 AC-PROD-001-02: Create Intent Router Class (Decision Tree)

**Status:** 🔴 NOT STARTED

**Description:**
Implement the Intent Router that routes canonicalized intents to appropriate orchestrators based on intent type and confidence.

**Files to Create:**
- `src/core/intent/intent_router.py` (new)

**Implementation:**

```python
# Intent types to orchestrator mapping
ROUTING_MAP = {
    # Code work → TDD
    IntentType.IMPLEMENT: "TDDOrchestrator",
    IntentType.FIX: "TDDOrchestrator",
    IntentType.REFACTOR: "TDDOrchestrator",
    IntentType.DEBUG: "TDDOrchestrator",
    IntentType.TEST: "TDDOrchestrator",
    
    # Planning work → Planning
    IntentType.PLANNING: "PlanningOrchestrator",
    IntentType.ADO_WORK: "PlanningOrchestrator",
    
    # Queries → Direct response (no delegation)
    IntentType.QUERY: "DirectResponse",
    IntentType.ANALYZE: "DirectResponse",
    IntentType.STATUS: "DirectResponse",
    
    # Unknown → Back to Interaction (clarification)
    IntentType.UNKNOWN: "InteractionOrchestrator",
}

class IntentRouter:
    """Route canonicalized intents to appropriate orchestrators."""
    
    def route(self, canonical_intent: CanonicalizedIntent) -> RoutingDecision:
        """
        Route intent based on type and confidence.
        
        High confidence (>= 0.85):
            Route to appropriate orchestrator immediately
            
        Medium confidence (0.70-0.84):
            Route to orchestrator with caution flag
            
        Low confidence (< 0.70):
            Return to Interaction for clarification
        """
        pass
```

**Acceptance Tests:**
- [ ] IMPLEMENT intent routes to TDDOrchestrator
- [ ] FIX intent routes to TDDOrchestrator
- [ ] QUERY intent routes to DirectResponse (no delegation)
- [ ] Confidence < 0.70 routes back to Interaction
- [ ] Routing decision logged with reasoning
- [ ] 20+ routing scenarios tested

**Test File:** `tests/unit/core/intent/test_intent_router.py`

**Effort:** 2 days  
**Dependencies:** IntentCanonicalizer (done)  
**Git Checkpoint:** `AC-PROD-001-02-intent-router`

---

### 🔵 AC-PROD-001-03: Integrate Intent Router into Master Orchestrator

**Status:** 🔴 NOT STARTED

**Description:**
Connect the Intent Router to MasterOrchestrator so routing decisions are made automatically.

**Files to Modify:**
- `src/orchestrators/core/master_orchestrator.py`

**Changes:**
```python
class MasterOrchestrator(IOrchestrator):
    def __init__(self):
        # ... existing code ...
        self.intent_router = IntentRouter()  # NEW
    
    def coordinate_operation(
        self, 
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[RoutingDecision]:
        """
        Main entry point for Master Orchestrator.
        
        Stage 2: Route intent to appropriate orchestrator.
        (Stage 1 comprehension done by caller)
        """
        # STAGE 2: Route based on canonical intent
        routing_decision = self.intent_router.route(canonical_intent)
        
        # Log routing decision
        self._log_routing_decision(routing_decision)
        
        return Ok(routing_decision)
```

**Acceptance Tests:**
- [ ] IntentRouter is initialized in Master.__init__()
- [ ] coordinate_operation() uses intent_router.route()
- [ ] Routing decisions are logged to audit trail
- [ ] Correct orchestrator selected for each intent type

**Test File:** `tests/integration/test_master_router_integration.py` (new)

**Effort:** 1 day  
**Dependencies:** AC-PROD-001-02  
**Git Checkpoint:** `AC-PROD-001-03-master-router-integration`

---

## Phase 2: LENS Protocol Integration (Week 2)

### 🔵 AC-PROD-002-01: Real LENS Synthesis - Aggregate AST + Git + Comments

**Status:** ⚠️ PARTIALLY STARTED

**Description:**
Replace simulated context gathering with real integration of AST, Git, and Comment analysis.

**Files to Modify:**
- `src/core/intent/lens_context_builder.py` (enhance)
- `src/core/intent/intent_reflection_protocol.py` (update reflect() method)

**Current State (Simulated):**
```python
def _gather_context_sources(self, request: ReflectionRequest) -> List[str]:
    """SIMULATED context gathering."""
    return ["AST", "Git", "Comments", "Relationships"]  # ← STUB!
```

**New Implementation:**
```python
def _gather_context_sources(self, request: ReflectionRequest) -> Dict[str, Any]:
    """Real context gathering from multiple sources."""
    
    from src.core.intelligence.ast_intelligence import ASTIntelligenceEngine
    from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
    
    context_sources = {}
    
    # 1. AST Analysis
    if request.context.get("file_path"):
        ast_engine = ASTIntelligenceEngine(request.context["project_root"])
        context_sources["AST"] = ast_engine.parse_file(request.context["file_path"])
    
    # 2. Git History
    if request.context.get("project_root"):
        git_analyzer = GitHistoryAnalyzer(request.context["project_root"])
        context_sources["GIT"] = git_analyzer.get_file_history(
            request.context.get("file_path"), 
            max_commits=50
        )
    
    # 3. Comments & Intent Markers
    if request.context.get("file_path"):
        from src.core.intelligence.comment_analyzer import CommentAnalyzer
        comment_engine = CommentAnalyzer(request.context["project_root"])
        context_sources["COMMENTS"] = comment_engine.extract_docstrings(
            request.context["file_path"]
        )
    
    return context_sources
```

**Acceptance Tests:**
- [ ] AST analysis returns real function/class definitions
- [ ] Git history shows real commits and authors
- [ ] Comments are extracted from actual files
- [ ] Context aggregated correctly in LENSContext
- [ ] Performance: < 2 seconds for small files, < 5 seconds for large files
- [ ] 15+ integration tests verify real data gathering

**Test File:** `tests/integration/test_lens_real_synthesis.py` (new)

**Effort:** 2 days  
**Dependencies:** AC-PROD-001-01  
**Git Checkpoint:** `AC-PROD-002-01-lens-real-synthesis`

---

### 🔵 AC-PROD-002-02: Implement Relationship Traversal Engine

**Status:** 🔴 NOT STARTED

**Description:**
Build the missing Relationship Analysis component that identifies API relationships, database relationships, and impact analysis.

**Files to Create:**
- `src/core/intelligence/relationship_traversal.py` (new)

**Implementation:**

```python
class RelationshipTraversalEngine:
    """Traverse code relationships to understand impact."""
    
    def get_api_relationships(self, function_name: str) -> List[APIRelationship]:
        """Find which API endpoints call this function."""
        pass
    
    def get_database_relationships(self, table_name: str) -> List[DBRelationship]:
        """Find database relationships and foreign keys."""
        pass
    
    def calculate_change_impact(
        self, 
        function_name: str, 
        depth: int = 3
    ) -> ImpactAnalysis:
        """
        Calculate impact if this function is changed.
        
        Returns:
            - Affected functions
            - Affected endpoints
            - Affected database tables
            - Affected tests
            - Required documentation updates
        """
        pass
```

**Key Methods:**
1. `traverse_call_graph()` - Find callers/callees
2. `find_api_endpoints()` - Map to REST/GraphQL endpoints
3. `find_affected_tests()` - Which tests would break?
4. `calculate_impact_scope()` - Full blast radius analysis

**Acceptance Tests:**
- [ ] Identify all callers of a function
- [ ] Find endpoints that use a function
- [ ] Map database table changes to affected code
- [ ] Calculate test impact (how many tests might break)
- [ ] Generate impact report YAML
- [ ] 20+ relationship traversal tests

**Test File:** `tests/unit/core/intelligence/test_relationship_traversal.py` (new)

**Effort:** 3 days  
**Dependencies:** AC-PROD-001-01, AST intelligence  
**Git Checkpoint:** `AC-PROD-002-02-relationship-traversal`

---

### 🔵 AC-PROD-002-03: Integrate Relationship Analysis into LENS Synthesis

**Status:** 🔴 NOT STARTED

**Description:**
Add the Relationship (R) component to LENS protocol synthesis.

**Files to Modify:**
- `src/core/intent/lens_context_builder.py`
- `src/core/intent/intent_reflection_protocol.py`

**Update:**
```python
def _gather_context_sources(self, request: ReflectionRequest) -> Dict[str, Any]:
    """Real context gathering with relationship analysis."""
    
    context_sources = {}
    
    # ... existing AST, Git, Comments code ...
    
    # 4. Relationship Analysis (NEW)
    if request.context.get("focal_point"):
        rel_engine = RelationshipTraversalEngine(request.context["project_root"])
        context_sources["RELATIONSHIPS"] = rel_engine.calculate_change_impact(
            request.context["focal_point"],
            depth=3
        )
    
    return context_sources
```

**Update Comprehension YAML:**
Add "Impact Analysis" section showing:
- What functions call this?
- What endpoints use this?
- What tests cover this?
- What will break if changed?

**Acceptance Tests:**
- [ ] Relationship data included in comprehension YAML
- [ ] Impact analysis section populated
- [ ] Test coverage gaps identified
- [ ] Breaking change warnings generated
- [ ] 10+ tests verify impact analysis in YAML

**Test File:** `tests/integration/test_lens_with_relationships.py` (new)

**Effort:** 2 days  
**Dependencies:** AC-PROD-002-02  
**Git Checkpoint:** `AC-PROD-002-03-lens-relationships-integration`

---

## Phase 3: Master Orchestrator 4-Stage Workflow (Week 3)

### 🔵 AC-PROD-003-01: Implement Stage 1 - Comprehension via LENS

**Status:** 🔴 NOT STARTED

**Description:**
Implement Stage 1 of Master Orchestrator workflow: invoke LENS protocol to build holistic context.

**Files to Modify:**
- `src/orchestrators/core/master_orchestrator.py`

**Implementation:**

```python
class MasterOrchestrator(IOrchestrator):
    
    def coordinate_operation(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[ComprehensionYAML]:
        """
        Main entry point for Master Orchestrator.
        
        Executes 4-stage workflow:
        1. COMPREHENSION: Build holistic context via LENS
        2. ROUTING: Route to appropriate orchestrator
        3. KNOWLEDGE: Merge governance context
        4. APPROVAL: Present for user confirmation
        """
        try:
            # ===== STAGE 1: COMPREHENSION =====
            comprehension = self._stage_1_comprehension(user_request, context)
            if comprehension.is_err():
                return comprehension
            
            # Continue to Stage 2
            return self._execute_stages_2_3_4(comprehension.unwrap())
            
        except Exception as e:
            return Err(f"Master orchestrator error: {str(e)}")
    
    def _stage_1_comprehension(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[ComprehensionYAML]:
        """
        STAGE 1: Build holistic context via LENS protocol.
        
        Steps:
        1. Create ReflectionRequest from user input
        2. Invoke IntentReflectionEngine.reflect()
        3. Generate comprehension YAML
        4. Log to audit trail
        
        Returns:
            ComprehensionYAML with challenges, recommendations, intent
        """
        try:
            # Log stage start
            self.logger.log_operation_start(
                ac_id="AC-PROD-003-01",
                operation="STAGE_1_COMPREHENSION",
                details={"user_request_length": len(user_request)}
            )
            
            # Determine focal point
            focal_point = self._determine_focal_point(user_request, context)
            
            # Create reflection request
            reflection_request = ReflectionRequest(
                user_request=user_request,
                focal_point=focal_point,
                target_scope="auto",  # Will be determined
                target_name=focal_point,
                context=context or {},
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            # Invoke LENS protocol
            reflection_engine = IntentReflectionEngine()
            reflection_response = reflection_engine.reflect(reflection_request)
            
            if reflection_response.status == ReflectionStatus.ERROR:
                self.logger.log_operation_complete(
                    ac_id="AC-PROD-003-01",
                    operation="STAGE_1_COMPREHENSION",
                    success=False,
                    details={"error": "Reflection failed"}
                )
                return Err("Comprehension failed")
            
            # Log stage complete
            self.logger.log_operation_complete(
                ac_id="AC-PROD-003-01",
                operation="STAGE_1_COMPREHENSION",
                success=True,
                details={
                    "intent_type": reflection_response.canonicalized_intent.get("type"),
                    "intent_confidence": reflection_response.canonicalized_intent.get("confidence"),
                    "challenges_identified": len(reflection_response.challenges),
                    "recommendations_generated": len(reflection_response.recommendations)
                }
            )
            
            return Ok(reflection_response.comprehension_yaml)
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-003-01",
                operation="STAGE_1_COMPREHENSION",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Stage 1 error: {str(e)}")
```

**Acceptance Tests:**
- [ ] IntentReflectionEngine.reflect() invoked automatically
- [ ] Comprehension YAML generated for user review
- [ ] Challenges identified and included in YAML
- [ ] Recommendations generated and prioritized
- [ ] Audit trail created with AC_START, AC_EXECUTE, AC_COMPLETE
- [ ] Performance: < 2 seconds for simple intents
- [ ] 15+ tests verify Stage 1 execution

**Test File:** `tests/integration/test_master_stage_1_comprehension.py` (new)

**Effort:** 2 days  
**Dependencies:** AC-PROD-002-01, AC-PROD-002-03  
**Git Checkpoint:** `AC-PROD-003-01-stage-1-comprehension`

---

### 🔵 AC-PROD-003-02: Implement Stage 2 - Intent Routing

**Status:** ⚠️ PARTIALLY DONE

**Description:**
Route comprehension to appropriate orchestrator based on intent.

**Files to Modify:**
- `src/orchestrators/core/master_orchestrator.py`

**Implementation:**

```python
def _stage_2_routing(
    self,
    comprehension_yaml: ComprehensionYAML
) -> Result[RoutingDecision]:
    """
    STAGE 2: Route to appropriate orchestrator.
    
    Extracts canonical intent from comprehension
    Uses IntentRouter to make routing decision
    Handles confidence threshold
    """
    try:
        self.logger.log_operation_start(
            ac_id="AC-PROD-003-02",
            operation="STAGE_2_ROUTING"
        )
        
        # Extract canonical intent from comprehension
        canonical_intent = self._extract_canonical_intent(comprehension_yaml)
        
        # Check confidence threshold
        if canonical_intent.confidence < 0.70:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-003-02",
                operation="STAGE_2_ROUTING",
                success=False,
                details={"reason": "Low confidence", "confidence": canonical_intent.confidence}
            )
            return Err("Confidence too low, returning to Interaction")
        
        # Route using IntentRouter
        routing_decision = self.intent_router.route(canonical_intent)
        
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-02",
            operation="STAGE_2_ROUTING",
            success=True,
            details={
                "intent_type": canonical_intent.intent_type,
                "selected_orchestrator": routing_decision.selected_orchestrator,
                "confidence": canonical_intent.confidence
            }
        )
        
        return Ok(routing_decision)
        
    except Exception as e:
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-02",
            operation="STAGE_2_ROUTING",
            success=False,
            details={"error": str(e)}
        )
        return Err(f"Stage 2 error: {str(e)}")
```

**Acceptance Tests:**
- [ ] Correct orchestrator selected for IMPLEMENT intent
- [ ] Correct orchestrator selected for QUERY intent
- [ ] Low confidence returns to Interaction
- [ ] Routing decision logged with reasoning
- [ ] 15+ routing scenarios tested

**Test File:** `tests/integration/test_master_stage_2_routing.py` (new)

**Effort:** 1 day  
**Dependencies:** AC-PROD-001-02, AC-PROD-001-03  
**Git Checkpoint:** `AC-PROD-003-02-stage-2-routing`

---

### 🔵 AC-PROD-003-03: Implement Stage 3 - Knowledge Integration

**Status:** 🔴 NOT STARTED

**Description:**
Merge governance rules and company knowledge context into comprehension.

**Files to Modify:**
- `src/orchestrators/core/master_orchestrator.py`

**Implementation:**

```python
def _stage_3_knowledge_integration(
    self,
    comprehension_yaml: ComprehensionYAML,
    routing_decision: RoutingDecision
) -> Result[EnrichedContext]:
    """
    STAGE 3: Merge governance + company context.
    
    1. Load Tier 0 rules from cortex_brain/tier0/
    2. Load domain-specific rules
    3. Validate against governance
    4. Add relevant company context
    5. Generate merged knowledge context
    """
    try:
        self.logger.log_operation_start(
            ac_id="AC-PROD-003-03",
            operation="STAGE_3_KNOWLEDGE_INTEGRATION"
        )
        
        # 1. Load governance rules
        governance_rules = self._load_governance_rules()
        
        # 2. Validate comprehension against rules
        validation_result = self._validate_against_governance(
            comprehension_yaml,
            governance_rules
        )
        
        if not validation_result.is_compliant:
            # Add governance violations as challenges
            comprehension_yaml = self._add_governance_violations_as_challenges(
                comprehension_yaml,
                validation_result.violations
            )
        
        # 3. Load company context for this domain
        company_context = self._load_company_context(
            routing_decision.selected_orchestrator
        )
        
        # 4. Merge contexts
        enriched_context = EnrichedContext(
            comprehension=comprehension_yaml,
            governance_rules=governance_rules,
            company_context=company_context,
            validation_result=validation_result,
            knowledge_graph=self._build_knowledge_graph(comprehension_yaml)
        )
        
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-03",
            operation="STAGE_3_KNOWLEDGE_INTEGRATION",
            success=True,
            details={
                "governance_rules_count": len(governance_rules),
                "violations_found": len(validation_result.violations),
                "company_context_loaded": company_context is not None
            }
        )
        
        return Ok(enriched_context)
        
    except Exception as e:
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-03",
            operation="STAGE_3_KNOWLEDGE_INTEGRATION",
            success=False,
            details={"error": str(e)}
        )
        return Err(f"Stage 3 error: {str(e)}")
```

**Acceptance Tests:**
- [ ] Governance rules loaded from cortex_brain/tier0/
- [ ] Violations detected and added as challenges
- [ ] Company context merged into comprehension
- [ ] Knowledge graph generated
- [ ] Validation results included
- [ ] 12+ tests verify knowledge integration

**Test File:** `tests/integration/test_master_stage_3_knowledge.py` (new)

**Effort:** 2 days  
**Dependencies:** AC-PROD-003-02, GovernanceRegistry (exists)  
**Git Checkpoint:** `AC-PROD-003-03-stage-3-knowledge-integration`

---

### 🔵 AC-PROD-003-04: Implement Stage 4 - Approval Gate

**Status:** 🔴 NOT STARTED

**Description:**
Enforce user confirmation before execution.

**Files to Modify:**
- `src/orchestrators/core/master_orchestrator.py`

**Implementation:**

```python
def _stage_4_approval_gate(
    self,
    enriched_context: EnrichedContext
) -> Result[ApprovalDecision]:
    """
    STAGE 4: Present for user confirmation before execution.
    
    1. Generate final comprehension document for user review
    2. Present challenges and recommendations
    3. Wait for user approval/rejection/clarification
    4. Log approval decision
    5. Return control to user or orchestrator
    """
    try:
        self.logger.log_operation_start(
            ac_id="AC-PROD-003-04",
            operation="STAGE_4_APPROVAL_GATE"
        )
        
        # Generate final review document
        review_document = self._generate_review_document(enriched_context)
        
        # Create approval request
        approval_request = ApprovalRequest(
            comprehension_yaml=review_document,
            challenges=enriched_context.comprehension.challenges,
            recommendations=enriched_context.comprehension.recommendations,
            governance_violations=enriched_context.validation_result.violations,
            target_orchestrator=enriched_context.routing_decision.selected_orchestrator
        )
        
        # Present to user (in actual system, this would be interactive)
        approval_decision = self._present_for_approval(approval_request)
        
        # Log decision
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-04",
            operation="STAGE_4_APPROVAL_GATE",
            success=approval_decision.status == ApprovalStatus.APPROVED,
            details={
                "status": approval_decision.status.value,
                "user": approval_decision.user,
                "timestamp": approval_decision.timestamp
            }
        )
        
        return Ok(approval_decision)
        
    except Exception as e:
        self.logger.log_operation_complete(
            ac_id="AC-PROD-003-04",
            operation="STAGE_4_APPROVAL_GATE",
            success=False,
            details={"error": str(e)}
        )
        return Err(f"Stage 4 error: {str(e)}")
```

**Approval Outcomes:**
- `APPROVED` → Proceed to orchestrator execution
- `REJECTED` → Log rejection, return to user
- `CLARIFICATION` → Return to Interaction for refinement
- `MODIFICATIONS` → User modified request, re-run LENS

**Acceptance Tests:**
- [ ] Comprehension document formatted for user review
- [ ] All challenges and recommendations included
- [ ] Governance violations highlighted
- [ ] User can approve/reject/request clarification
- [ ] Approval logged to audit trail
- [ ] Rejection reasons captured
- [ ] 15+ tests verify approval gate logic

**Test File:** `tests/integration/test_master_stage_4_approval.py` (new)

**Effort:** 2 days  
**Dependencies:** AC-PROD-003-03  
**Git Checkpoint:** `AC-PROD-003-04-stage-4-approval-gate`

---

## Phase 4: Repository Analysis & Advanced Features (Week 4)

### 🔵 AC-PROD-004-01: Implement Repository Scanner

**Status:** 🔴 NOT STARTED

**Description:**
Build batch repository analysis capability.

**Files to Create:**
- `src/core/intelligence/repository_scanner.py` (new)

**Implementation:**

```python
class RepositoryScanner:
    """Scan entire repository for holistic analysis."""
    
    def scan_repository(
        self,
        repo_path: str,
        depth: int = 3,
        timeout: int = 30
    ) -> RepositoryProfile:
        """
        Scan repository in phases.
        
        Phase 1 (0-5 sec): Quick scan
            - Language detection
            - Key files identification
            - Directory structure
            
        Phase 2 (5-15 sec): AST Analysis
            - Parse all Python files
            - Extract functions/classes
            - Build call graph
            
        Phase 3 (15-30 sec): Git Analysis
            - Recent commit history
            - Author patterns
            - Change frequency hotspots
        """
        pass
```

**Output:** RepositoryProfile containing:
- Language(s) detected
- Key files and directories
- Functions and classes
- Call graph
- Git history summary
- Hotspot analysis

**Acceptance Tests:**
- [ ] Detect Python, TypeScript, JavaScript repos
- [ ] Extract function signatures
- [ ] Build call graph
- [ ] Analyze change patterns
- [ ] Performance: 30 seconds max for 1000-file repo
- [ ] 20+ tests verify scanning accuracy

**Test File:** `tests/unit/core/intelligence/test_repository_scanner.py` (new)

**Effort:** 3 days  
**Dependencies:** AST Intelligence, Git Analyzer  
**Git Checkpoint:** `AC-PROD-004-01-repository-scanner`

---

### 🔵 AC-PROD-004-02: Implement Full Workflow Integration

**Status:** 🔴 NOT STARTED

**Description:**
Connect all 4 stages into one unified workflow that orchestrates automatically.

**Files to Modify:**
- `src/orchestrators/core/master_orchestrator.py`

**Implementation:**

```python
class MasterOrchestrator(IOrchestrator):
    
    def coordinate_operation(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[ExecutionResult]:
        """
        Complete 4-stage Master Orchestrator workflow.
        
        STAGE 1: Comprehension via LENS
        STAGE 2: Intent Routing
        STAGE 3: Knowledge Integration
        STAGE 4: Approval Gate
        
        Returns:
            ExecutionResult with status, orchestrator assignment, context
        """
        try:
            # ===== STAGE 1: COMPREHENSION =====
            comprehension = self._stage_1_comprehension(user_request, context)
            if comprehension.is_err():
                return comprehension
            
            # ===== STAGE 2: ROUTING =====
            routing = self._stage_2_routing(comprehension.unwrap())
            if routing.is_err():
                return routing
            
            # ===== STAGE 3: KNOWLEDGE INTEGRATION =====
            enriched = self._stage_3_knowledge_integration(
                comprehension.unwrap(),
                routing.unwrap()
            )
            if enriched.is_err():
                return enriched
            
            # ===== STAGE 4: APPROVAL GATE =====
            approval = self._stage_4_approval_gate(enriched.unwrap())
            if approval.is_err():
                return approval
            
            # Check approval status
            approval_decision = approval.unwrap()
            if approval_decision.status == ApprovalStatus.APPROVED:
                # Proceed to execution with target orchestrator
                execution_result = ExecutionResult(
                    status="APPROVED",
                    target_orchestrator=routing.unwrap().selected_orchestrator,
                    enriched_context=enriched.unwrap(),
                    ready_for_execution=True
                )
                return Ok(execution_result)
            else:
                # Return to interaction or user
                return Err(f"User {approval_decision.status.value}")
                
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-MASTER-WORKFLOW",
                operation="COMPLETE_WORKFLOW",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Master workflow error: {str(e)}")
```

**Acceptance Tests:**
- [ ] All 4 stages execute in sequence
- [ ] Each stage output feeds to next stage
- [ ] Approval gates enforce BEFORE execution
- [ ] Complete audit trail captured
- [ ] Performance: < 5 seconds end-to-end
- [ ] All 20+ workflow integration tests pass

**Test File:** `tests/integration/test_master_complete_workflow.py` (new)

**Effort:** 1 day  
**Dependencies:** All AC-PROD-003-xx  
**Git Checkpoint:** `AC-PROD-004-02-complete-workflow-integration`

---

## Phase 5: Testing, Hardening & Documentation (Week 5)

### 🔵 AC-PROD-005-01: E2E LENS Protocol Testing

**Status:** 🔴 NOT STARTED

**Description:**
Comprehensive end-to-end testing of entire LENS protocol.

**Test File:** `tests/integration/test_lens_e2e.py` (new)

**Test Scenarios:**
1. Simple intent on single file
2. Complex intent on module
3. Low confidence scenarios
4. High complexity code
5. Multiple languages
6. Large repositories

**Acceptance Tests:**
- [ ] 30+ E2E LENS tests
- [ ] All tests pass
- [ ] Performance benchmarks met
- [ ] Coverage > 90%

**Effort:** 2 days  
**Dependencies:** All AC-PROD-00X complete  
**Git Checkpoint:** `AC-PROD-005-01-lens-e2e-testing`

---

### 🔵 AC-PROD-005-02: Master Orchestrator Integration Tests

**Status:** ⚠️ PARTIALLY DONE

**Description:**
Comprehensive testing of Master Orchestrator all features.

**Test File:** `tests/integration/test_master_orchestrator_complete.py` (new)

**Acceptance Tests:**
- [ ] 40+ Master orchestrator tests
- [ ] All 4-stage workflow scenarios
- [ ] Error handling and recovery
- [ ] Audit trail verification
- [ ] Performance < 5 seconds
- [ ] 100% pass rate

**Effort:** 2 days  
**Dependencies:** All implementation complete  
**Git Checkpoint:** `AC-PROD-005-02-master-orchestrator-tests`

---

### 🔵 AC-PROD-005-03: Production Hardening

**Status:** 🔴 NOT STARTED

**Description:**
Prepare for production deployment.

**Tasks:**
- [ ] Performance optimization
  - LENS < 2 sec for simple requests
  - Repo scan < 30 sec
  - Master workflow < 5 sec
  
- [ ] Error handling
  - Graceful degradation
  - Fallback strategies
  - Error recovery
  
- [ ] Monitoring & Observability
  - Metrics collection
  - Performance tracking
  - Error alerting
  
- [ ] Security review
  - Input validation
  - Output sanitization
  - Governance enforcement

**Acceptance Tests:**
- [ ] All performance targets met
- [ ] Error scenarios handled
- [ ] Monitoring operational
- [ ] Security review passed

**Effort:** 1 day  
**Dependencies:** All tests passing  
**Git Checkpoint:** `AC-PROD-005-03-production-hardening`

---

### 🔵 AC-PROD-005-04: Documentation & Deployment Guide

**Status:** 🔴 NOT STARTED

**Description:**
Create comprehensive documentation for operations and development.

**Files to Create:**
- `docs/MASTER_ORCHESTRATOR_GUIDE.md` - Architecture & design
- `docs/LENS_PROTOCOL_GUIDE.md` - LENS protocol details
- `docs/DEPLOYMENT_GUIDE.md` - Deployment steps
- `docs/TROUBLESHOOTING.md` - Common issues & solutions

**Content:**
- Architecture diagrams
- Component relationships
- Deployment instructions
- Monitoring setup
- Troubleshooting guide
- Performance tuning

**Acceptance Criteria:**
- [ ] All components documented
- [ ] Deployment steps clear
- [ ] Troubleshooting guide complete
- [ ] Architecture diagrams included

**Effort:** 1 day  
**Dependencies:** All implementation complete  
**Git Checkpoint:** `AC-PROD-005-04-documentation`

---

## Summary: AC-IDs by Phase

### Phase 1 (Week 1): Quick Wins
- **AC-PROD-001-01** ✅ Fix import bugs → 100% test pass (DONE)
- **AC-PROD-001-02** 🔵 Create Intent Router (2 days)
- **AC-PROD-001-03** 🔵 Integrate router into Master (1 day)

### Phase 2 (Week 2): LENS Integration
- **AC-PROD-002-01** 🔵 Real LENS synthesis (2 days)
- **AC-PROD-002-02** 🔵 Relationship traversal (3 days)
- **AC-PROD-002-03** 🔵 LENS relationships integration (2 days)

### Phase 3 (Week 3): 4-Stage Workflow
- **AC-PROD-003-01** 🔵 Stage 1: Comprehension (2 days)
- **AC-PROD-003-02** 🔵 Stage 2: Routing (1 day)
- **AC-PROD-003-03** 🔵 Stage 3: Knowledge integration (2 days)
- **AC-PROD-003-04** 🔵 Stage 4: Approval gate (2 days)

### Phase 4 (Week 4): Advanced Features
- **AC-PROD-004-01** 🔵 Repository scanner (3 days)
- **AC-PROD-004-02** 🔵 Complete workflow integration (1 day)

### Phase 5 (Week 5): Testing & Hardening
- **AC-PROD-005-01** 🔵 E2E LENS testing (2 days)
- **AC-PROD-005-02** 🔵 Master orchestrator tests (2 days)
- **AC-PROD-005-03** 🔵 Production hardening (1 day)
- **AC-PROD-005-04** 🔵 Documentation (1 day)

---

## Implementation Timeline

```
Week 1  [===    ] 20% - Routers & fixes
Week 2  [=====  ] 40% - LENS integration
Week 3  [======== ] 60% - 4-stage workflow
Week 4  [========= ] 80% - Advanced features
Week 5  [===========] 100% - Testing & production ready
```

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test Pass Rate | 84% | 100% |
| Components Integrated | 60% | 100% |
| LENS Protocol | 40% | 100% |
| Documentation | 30% | 100% |
| Production Ready | 0% | 100% |

---

## Risk Assessment

### Low Risk
- ✅ Building on stable foundation
- ✅ Components mostly exist
- ✅ Strong test coverage planned

### Medium Risk
- ⚠️ Relationship analysis is new
- ⚠️ Repository scanning at scale
- ⚠️ Performance optimization

### Mitigation
- Incremental implementation
- Early performance testing
- Fallback strategies

---

## Resource Requirements

**Developer Skills Needed:**
- Python (advanced)
- AST parsing
- Git operations
- Test-driven development
- Systems thinking

**Estimated Effort:**
- **1 Senior Developer:** 5 weeks (40 hours/week = 200 hours)
- **2-3 Junior Developers:** 3 weeks (60 hours/week = 180 hours)
- **Team of 3:** 2.5 weeks (intensive)

---

## Next Steps

1. **Review this plan** with team
2. **Prioritize phases** if needed
3. **Assign AC-IDs** to developers
4. **Start Week 1** with AC-PROD-001-02 (Intent Router)
5. **Track progress** via AC completion
6. **Weekly sync** to adjust timeline

---

**Plan Created:** 2026-01-17  
**Status:** Ready for implementation  
**Contact:** Asif Hussain

