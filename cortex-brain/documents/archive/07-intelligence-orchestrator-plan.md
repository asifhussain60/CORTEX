# Intelligence Orchestrator Sub-Plan

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 PHASE 4 - READY FOR IMPLEMENTATION

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [Documentation Orchestrator Plan](06-documentation-orchestrator-plan.md)
- **Next:** [Observability Orchestrator Plan](08-observability-orchestrator-plan.md)
- **Workflow YAML:** `src/orchestration_3_0/workflows/intelligence_workflow.yaml`

---

## 1️⃣ Existing State (Summarized)

### Current Files Being Consolidated

| File | LOC (Est.) | Purpose | Key Components |
|------|------------|---------|----------------|
| `src/orchestrators/test_intelligence.py` | ~400 | Test intelligence and debugging | Test result analysis, error diagnosis |
| `src/workflows/refactoring_intelligence.py` | ~600 | Multi-language refactoring coordination | Python/C#/JS/TS refactoring |
| `src/tier3/context_intelligence.py` | ~500 | Context extraction and analysis | Code pattern recognition |
| `src/tier1/narrative_intelligence.py` | ~400 | Natural language generation | Documentation narratives |
| `src/cortex_agents/strategic/architecture_intelligence_agent.py` | ~700 | Architectural guidance | SOLID principles, design patterns |

**Total LOC:** ~2,600 lines across 5 files

**Note:** Master plan estimates 5 files with 2,600 LOC consolidating to 1,000 LOC (62% reduction)

### Current Workflow (High-Level Steps)

1. **User Trigger:** Implicit (triggered by other orchestrators when AI assistance needed)
2. **Intelligence Type Detection:** Determine what kind of AI operation is needed
3. **Context Gathering:** Collect relevant code, documentation, patterns
4. **AI Processing:** 
   - Feature completion: Suggest implementations
   - Clarification: Extract missing requirements during execution
   - Refactoring: Multi-language code improvements
5. **Result Integration:** Feed AI insights back to calling orchestrator
6. **Learning Loop:** Update knowledge graph with patterns discovered

### Current Triggers

**Implicit Triggers (Called by Other Orchestrators):**
- Planning Orchestrator requests feature completion suggestions
- TDD Orchestrator requests test improvement recommendations
- Execution Orchestrator requests clarification during runtime
- DevOps Orchestrator requests optimization suggestions

**Direct Triggers (Future):**
- **Natural Language:** `"suggest implementation"`, `"clarify requirements"`, `"refactor this code"`
- **API Endpoint:** `/api/intelligence/complete`, `/api/intelligence/clarify`, `/api/intelligence/refactor`
- **Copilot Command:** `@cortex suggest`, `@cortex clarify`, `@cortex refactor`

### Current Issues & Pain Points

**Fragmentation:**
- 5 separate intelligence modules with overlapping capabilities
- No unified interface for AI operations
- Duplicated LLM call logic across files (~40% overlap)
- Context gathering repeated in each module

**Reliability:**
- No consistent prompt engineering patterns
- LLM responses not validated against schemas
- No fallback when AI confidence is low
- Error recovery: Manual intervention required

**Technical Debt:**
- Hard-coded prompts scattered across codebase
- No prompt template versioning
- No multi-language support (prompts in English only)
- No LLM provider abstraction (tightly coupled)

**Scalability:**
- Single-project focus (no cross-project learning)
- No RBAC (all users get same AI capabilities)
- No token budget management
- No caching of AI responses

**Intelligence Limitations:**
- Feature completion: Only suggests skeleton, not full implementation
- Clarification: Only asks questions, doesn't infer from context
- Refactoring: Limited to syntax changes, not architectural improvements
- No proactive suggestions (waits for explicit request)

---

## 2️⃣ New Structure

### Target Architecture

```
src/orchestration_3_0/orchestrators/intelligence/
├── __init__.py
├── intelligence_orchestrator.py           # Main orchestrator (300 LOC)
├── feature_completion_engine.py           # Auto-complete features (200 LOC)
├── clarification_engine.py                # Runtime requirement extraction (150 LOC)
├── refactoring_coordinator.py             # Multi-language refactoring (200 LOC)
├── llm_provider_abstraction.py            # LLM provider interface (100 LOC)
└── prompt_template_manager.py             # Versioned prompt templates (50 LOC)
```

**Total Target LOC:** 1,000 lines (62% reduction from 2,600)

### Component Responsibilities

**Main Orchestrator (`intelligence_orchestrator.py` - 300 LOC)**
- State machine integration (FSM states for AI operations)
- Workflow coordination (route to appropriate AI engine)
- DI container registration (inject LLM provider, prompt manager)
- Multi-tenant isolation (tenant_id for AI usage tracking)
- Session management (cache AI responses per session)
- Token budget enforcement (prevent runaway LLM costs)

**Feature Completion Engine (`feature_completion_engine.py` - 200 LOC)**
- **Input:** Partial feature description, codebase context
- **Output:** Completed implementation with code, tests, docs
- **Capabilities:**
  - Analyze existing patterns in codebase
  - Generate complete implementation (not just skeleton)
  - Suggest test cases based on business logic
  - Auto-generate API documentation
- **Dependencies:** LLM provider, prompt templates, code analyzer

**Clarification Engine (`clarification_engine.py` - 150 LOC)**
- **Input:** Ambiguous user request, current workflow context
- **Output:** Structured questions OR inferred requirements
- **Capabilities:**
  - Extract missing details during orchestrator execution (NOT upfront)
  - Infer requirements from context (reduce back-and-forth)
  - Ask targeted questions when inference fails
  - Validate answers against workflow constraints
- **Dependencies:** LLM provider, context intelligence
- **Note:** Works WITH Requirements Gathering Engine (upfront) - this handles RUNTIME clarification

**Refactoring Coordinator (`refactoring_coordinator.py` - 200 LOC)**
- **Input:** Code files (Python/C#/JS/TS), refactoring goals
- **Output:** Refactored code with architectural improvements
- **Capabilities:**
  - Multi-language support (Python, C#, JavaScript, TypeScript)
  - SOLID principles enforcement
  - Design pattern suggestions
  - Performance optimizations
  - Code smell detection and removal
- **Dependencies:** LLM provider, AST parsers, code analyzers

**LLM Provider Abstraction (`llm_provider_abstraction.py` - 100 LOC)**
- **Purpose:** Decouple from specific LLM (OpenAI, Anthropic, local models)
- **Interface:**
  ```python
  class LLMProvider(ABC):
      def complete(self, prompt: str, max_tokens: int) -> LLMResponse
      def stream(self, prompt: str) -> Iterator[str]
      def validate_response(self, response: str, schema: dict) -> bool
  ```
- **Implementations:** OpenAIProvider, AnthropicProvider, LocalModelProvider
- **Dependencies:** Provider-specific SDKs

**Prompt Template Manager (`prompt_template_manager.py` - 50 LOC)**
- **Purpose:** Versioned, multi-language prompt templates
- **Storage:** `cortex-brain/manifests/orchestrators/intelligence-prompts.yaml`
- **Capabilities:**
  - Load prompt by name and version
  - Multi-language support (English, Spanish, French, etc.)
  - Variable substitution (inject context into prompts)
  - Template validation (ensure required placeholders present)
- **Dependencies:** YAML parser

### API Contracts (Public Interfaces)

```python
# Main orchestrator interface
class IntelligenceOrchestrator(BaseOrchestrator):
    """AI-powered operations orchestrator."""
    
    def complete_feature(
        self, 
        tenant_id: str,
        project_id: str,
        feature_description: str,
        codebase_context: dict,
        **kwargs
    ) -> FeatureCompletionResult:
        """Generate complete feature implementation from partial description."""
        pass
    
    def clarify_requirements(
        self,
        tenant_id: str,
        project_id: str,
        ambiguous_request: str,
        workflow_context: dict,
        **kwargs
    ) -> ClarificationResult:
        """Extract missing requirements during orchestrator execution."""
        pass
    
    def refactor_code(
        self,
        tenant_id: str,
        project_id: str,
        file_paths: List[str],
        language: str,
        refactoring_goals: List[str],
        **kwargs
    ) -> RefactoringResult:
        """Refactor code with architectural improvements."""
        pass
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """Validate AI operation prerequisites (LLM available, token budget)."""
        pass
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """Validate AI operation completion (response quality, schema compliance)."""
        pass

# Feature completion result
@dataclass
class FeatureCompletionResult:
    success: bool
    implementation_code: str
    test_code: str
    documentation: str
    confidence_score: float  # 0.0-1.0
    suggested_improvements: List[str]

# Clarification result
@dataclass
class ClarificationResult:
    success: bool
    inferred_requirements: dict  # Requirements extracted from context
    clarification_questions: List[str]  # Questions to ask user (if inference fails)
    confidence_score: float  # 0.0-1.0

# Refactoring result
@dataclass
class RefactoringResult:
    success: bool
    refactored_files: dict  # file_path -> new_content
    changes_summary: str
    architectural_improvements: List[str]
    code_smells_removed: List[str]
```

### State Machine Integration

**FSM States:**
1. `INITIALIZED` - Orchestrator ready
2. `VALIDATING_DOR` - Checking prerequisites (LLM available, token budget)
3. `GATHERING_CONTEXT` - Collecting codebase patterns, documentation
4. `INVOKING_AI` - Calling LLM with prompt
5. `VALIDATING_RESPONSE` - Schema validation, confidence check
6. `INTEGRATING_RESULT` - Feed insights back to caller
7. `VALIDATING_DOD` - Checking completion criteria (response quality)
8. `COMPLETED` - AI operation finished
9. `FAILED` - Error state (LLM timeout, low confidence)

**Transitions:**
- `INITIALIZED → VALIDATING_DOR` (on execute)
- `VALIDATING_DOR → GATHERING_CONTEXT` (DoR passed: LLM available)
- `VALIDATING_DOR → FAILED` (DoR failed: no LLM, budget exceeded)
- `GATHERING_CONTEXT → INVOKING_AI` (context collected)
- `INVOKING_AI → VALIDATING_RESPONSE` (LLM responded)
- `INVOKING_AI → FAILED` (LLM timeout/error)
- `VALIDATING_RESPONSE → INTEGRATING_RESULT` (response valid, confidence >0.7)
- `VALIDATING_RESPONSE → FAILED` (response invalid, confidence <0.5)
- `INTEGRATING_RESULT → VALIDATING_DOD` (result integrated)
- `VALIDATING_DOD → COMPLETED` (DoD passed: quality met)
- `VALIDATING_DOD → FAILED` (DoD failed: quality insufficient)

**Guard Conditions:**
- DoR gates:
  - LLM provider configured and available
  - Token budget not exceeded (tenant quota)
  - Sufficient context available (codebase analyzed)
  - User has AI operations permission (RBAC)
- DoD gates:
  - AI response validated against schema
  - Confidence score ≥ 0.7 (70%+ confidence)
  - Response not hallucinated (verified against codebase)
  - Token usage within budget

### YAML Workflow Definition

**File:** `src/orchestration_3_0/workflows/intelligence_workflow.yaml`

```yaml
workflow:
  name: "Intelligence Orchestrator Workflow"
  version: "1.0.0"
  orchestrator: "IntelligenceOrchestrator"
  description: "AI-powered operations for feature completion, clarification, refactoring"
  
  phases:
    - id: "dor_validation"
      name: "Validate AI Operation Prerequisites"
      gates:
        - llm_provider_available
        - token_budget_not_exceeded
        - context_available
        - user_has_ai_permission
      actions:
        - check_llm_health
        - verify_token_quota
        - validate_context
    
    - id: "context_gathering"
      name: "Gather Codebase Context"
      tasks:
        - analyze_existing_patterns
        - extract_relevant_documentation
        - identify_similar_implementations
      timeout: 30s
    
    - id: "ai_invocation"
      name: "Invoke LLM"
      tasks:
        - load_prompt_template
        - substitute_context_variables
        - call_llm_provider
        - stream_response
      timeout: 60s
      retry:
        max_attempts: 3
        backoff: exponential
    
    - id: "response_validation"
      name: "Validate AI Response"
      tasks:
        - validate_response_schema
        - calculate_confidence_score
        - check_hallucination
      gates:
        - confidence_score_gte_0_7
        - response_not_hallucinated
    
    - id: "result_integration"
      name: "Integrate AI Insights"
      tasks:
        - format_result
        - update_knowledge_graph
        - log_ai_usage
    
    - id: "dod_validation"
      name: "Validate AI Operation Completion"
      gates:
        - response_quality_sufficient
        - token_usage_within_budget
      actions:
        - verify_response_quality
        - update_tenant_quota
  
  rollback:
    on_failure:
      - revert_knowledge_graph_updates
      - refund_token_budget
      - notify_caller

  monitoring:
    metrics:
      - ai_operation_success_rate
      - average_confidence_score
      - token_usage_per_tenant
      - llm_response_time
    alerts:
      - confidence_score_below_0_5
      - token_budget_80_percent_used
      - llm_timeout_rate_above_10_percent
```

---

## 3️⃣ Migration Strategy (5 Phases with TDD)

### Phase 1: RED (Tests First) - Week 6, Day 1-2

**Objective:** Write comprehensive failing tests

**Integration Tests (30 tests):**
- [ ] Test feature completion end-to-end (description → full implementation)
- [ ] Test clarification workflow (ambiguous request → questions/inferred requirements)
- [ ] Test refactoring workflow (code → improved code)
- [ ] Test DoR validation (LLM unavailable, budget exceeded)
- [ ] Test DoD validation (low confidence, hallucination detected)
- [ ] Test multi-tenant isolation (separate token quotas per tenant)
- [ ] Test error handling and rollback (LLM timeout, invalid response)
- [ ] Test session persistence (cache AI responses)

**Unit Tests (50 tests):**
- [ ] Test main orchestrator initialization
- [ ] Test feature completion engine (pattern analysis, code generation)
- [ ] Test clarification engine (inference, question generation)
- [ ] Test refactoring coordinator (multi-language support, SOLID enforcement)
- [ ] Test LLM provider abstraction (OpenAI, Anthropic, local models)
- [ ] Test prompt template manager (versioning, multi-language, substitution)
- [ ] Test confidence score calculation
- [ ] Test hallucination detection
- [ ] Test token budget enforcement
- [ ] Test knowledge graph updates

**Migration Tests (0 tests - New orchestrator, no legacy behavior to preserve)**

**Total Tests:** 80 tests (30 integration + 50 unit)

**Validation:** All tests RED (fail because orchestrator doesn't exist yet)

### Phase 2: GREEN (Core Implementation) - Week 6, Day 3-4

**Objective:** Implement minimal orchestrator to pass tests

**Day 3: Core Infrastructure**
- Implement `intelligence_orchestrator.py` (FSM integration, DI registration)
- Implement `llm_provider_abstraction.py` (interface + OpenAI provider)
- Implement `prompt_template_manager.py` (load/substitute templates)
- Register in DI container
- Integrate with state machine

**Day 4: AI Engines**
- Implement `feature_completion_engine.py` (pattern analysis, code generation)
- Implement `clarification_engine.py` (inference, question generation)
- Implement `refactoring_coordinator.py` (multi-language refactoring)
- Wire engines into main orchestrator

**Validation:** 
- All 80 tests pass
- Feature completion generates skeleton code
- Clarification asks basic questions
- Refactoring improves syntax
- Old intelligence modules still active (parallel operation)

### Phase 3: REFACTOR (Parallel Operation) - Week 6, Day 5

**Objective:** Run old and new orchestrators in parallel, compare outputs

**Comparison Tests:**
- [ ] Compare feature completion quality (old vs new)
- [ ] Compare clarification effectiveness (fewer questions)
- [ ] Compare refactoring improvements (architectural vs syntax-only)
- [ ] Compare AI response times
- [ ] Compare token usage

**Performance Benchmarks:**
- Feature completion: <60s for typical feature
- Clarification: <10s for inference, <30s for questions
- Refactoring: <120s for 1000 LOC
- Token usage: <5000 tokens per operation

**Enhancements (REFACTOR phase):**
- Optimize prompt templates for clarity
- Add caching for similar AI requests
- Improve context gathering (analyze more patterns)
- Add multi-language prompt support
- Implement advanced refactoring (architectural improvements)

**Validation:**
- New orchestrator matches or exceeds old quality
- Performance within benchmarks
- Token usage optimized

### Phase 4: CUTOVER (Switch to New) - Week 6, End

**Objective:** Route all AI operations to new orchestrator

**Update Orchestrator Integration:**
- [ ] Update Planning Orchestrator to call `IntelligenceOrchestrator.complete_feature()`
- [ ] Update TDD Orchestrator to call `IntelligenceOrchestrator.clarify_requirements()`
- [ ] Update DevOps Orchestrator to call `IntelligenceOrchestrator.refactor_code()`
- [ ] Remove imports of old intelligence modules

**Update cortex-operations.yaml:**
```yaml
- operation: suggest_implementation
  natural_language_triggers:
    - "suggest implementation"
    - "complete this feature"
    - "generate code for"
  orchestrator: intelligence_orchestrator
  execution_method: copilot_chat
  requires_admin: false

- operation: clarify_requirements
  natural_language_triggers:
    - "clarify requirements"
    - "what do you need to know"
    - "ask me questions"
  orchestrator: intelligence_orchestrator
  execution_method: copilot_chat
  requires_admin: false

- operation: refactor_code
  natural_language_triggers:
    - "refactor this code"
    - "improve code quality"
    - "apply design patterns"
  orchestrator: intelligence_orchestrator
  execution_method: copilot_chat
  requires_admin: false
```

**Archive Old Files:**
- Move old intelligence files to `cortex-brain/archives/orchestrators-legacy/intelligence/`
- Create rollback script: `scripts/rollback/rollback_intelligence_orchestrator.py`
- 30-day grace period begins

**Validation:**
- Production monitoring (AI operation success rate ≥90%)
- Confidence score tracking (average ≥0.8)
- Token usage within budget
- No increase in error rate

### Phase 5: CLEANUP (Remove Old) - Week 10, End

**Objective:** Delete archived orchestrator files after grace period

**Deletion Checklist:**
- ✅ Week 6-7: Archive old files
- ✅ Week 6: Update all orchestrator integrations
- ✅ Week 6-7: Run full test suite (80 tests pass)
- ✅ Week 7-9: Monitor production (AI success rate ≥90%, confidence ≥0.8)
- ✅ Week 8-9: User feedback collection (AI suggestions helpful)
- ✅ Week 10: Final validation checks (30 days stable)
- ❌ Week 10, End: Permanent deletion

**Grace Period Metrics:**
- AI operation success rate: Target ≥90%
- Average confidence score: Target ≥0.8
- Token usage: Target <10% increase
- User satisfaction: Target ≥8/10

**Permanent Deletion (After Grace Period):**
- Delete `cortex-brain/archives/orchestrators-legacy/intelligence/`
- Delete `scripts/rollback/rollback_intelligence_orchestrator.py`
- Remove rollback capability

**Validation:** System stable for 30+ days, all metrics met

---

## 4️⃣ Test Coverage Requirements

### Test Distribution

| Test Type | Count | Coverage Target | Purpose |
|-----------|-------|-----------------|---------|
| Unit Tests | 50 | 100% | Test each component in isolation |
| Integration Tests | 30 | 95% | Test AI operations end-to-end |
| Migration Tests | 0 | N/A | New orchestrator, no legacy behavior |
| Performance Tests | 3 | N/A | Benchmark AI response times |
| **TOTAL** | **83 tests** | **98%** | Comprehensive validation |

### Unit Test Breakdown (50 tests)

**Main Orchestrator (10 tests):**
- [ ] Orchestrator initialization with DI container
- [ ] State machine integration (FSM states)
- [ ] DoR validation (LLM available, token budget)
- [ ] DoD validation (confidence score, quality)
- [ ] Multi-tenant isolation (tenant_id)
- [ ] Session management (cache responses)
- [ ] Token budget enforcement
- [ ] Error handling (LLM timeout)
- [ ] Rollback capability
- [ ] Monitoring instrumentation

**Feature Completion Engine (12 tests):**
- [ ] Pattern analysis (extract similar code)
- [ ] Code generation (complete implementation)
- [ ] Test case suggestion
- [ ] API documentation generation
- [ ] Confidence score calculation
- [ ] Context gathering
- [ ] Prompt template loading
- [ ] LLM response parsing
- [ ] Schema validation
- [ ] Hallucination detection
- [ ] Knowledge graph updates
- [ ] Multi-language support (Python, C#, JS, TS)

**Clarification Engine (10 tests):**
- [ ] Requirement inference from context
- [ ] Question generation (targeted, not generic)
- [ ] Confidence score for inference
- [ ] Validation of user answers
- [ ] Context extraction
- [ ] Ambiguity detection
- [ ] Multi-language prompts
- [ ] Integration with Requirements Gathering Engine
- [ ] Runtime clarification (vs upfront)
- [ ] Knowledge graph updates

**Refactoring Coordinator (10 tests):**
- [ ] Multi-language support (Python, C#, JS, TS)
- [ ] SOLID principles enforcement
- [ ] Design pattern suggestions
- [ ] Code smell detection
- [ ] Performance optimizations
- [ ] AST parsing for each language
- [ ] Refactoring confidence score
- [ ] Architectural improvements (not just syntax)
- [ ] Test preservation (refactored code passes existing tests)
- [ ] Documentation updates

**LLM Provider Abstraction (5 tests):**
- [ ] OpenAI provider implementation
- [ ] Anthropic provider implementation (future)
- [ ] Local model provider (future)
- [ ] Response streaming
- [ ] Schema validation

**Prompt Template Manager (3 tests):**
- [ ] Template loading from YAML
- [ ] Variable substitution
- [ ] Multi-language support
- [ ] Template validation

### Integration Test Breakdown (30 tests)

**Feature Completion Workflow (10 tests):**
- [ ] Complete feature from partial description
- [ ] Generate tests for feature
- [ ] Generate API documentation
- [ ] Handle low confidence (ask for more details)
- [ ] Multi-tenant isolation
- [ ] Session persistence
- [ ] Token budget enforcement
- [ ] Error recovery (LLM timeout)
- [ ] Rollback on failure
- [ ] Monitoring metrics collected

**Clarification Workflow (10 tests):**
- [ ] Infer requirements from context
- [ ] Generate targeted questions
- [ ] Validate user answers
- [ ] Handle ambiguous requests
- [ ] Multi-tenant isolation
- [ ] Runtime clarification during orchestrator execution
- [ ] Integration with Requirements Gathering Engine
- [ ] Error recovery
- [ ] Rollback on failure
- [ ] Monitoring metrics collected

**Refactoring Workflow (10 tests):**
- [ ] Refactor Python code (SOLID, patterns)
- [ ] Refactor C# code
- [ ] Refactor JavaScript code
- [ ] Refactor TypeScript code
- [ ] Preserve existing tests
- [ ] Multi-tenant isolation
- [ ] Token budget enforcement
- [ ] Error recovery
- [ ] Rollback on failure
- [ ] Monitoring metrics collected

### Performance Test Breakdown (3 tests)

- [ ] Feature completion performance (<60s for typical feature)
- [ ] Clarification performance (<10s inference, <30s questions)
- [ ] Refactoring performance (<120s for 1000 LOC)

---

## 5️⃣ Wiring Validation Checklist

### Infrastructure Wiring
- ✅ State machine transitions registered (9 states, 11 transitions)
- ✅ DI container bindings configured:
  - `IntelligenceOrchestrator` (singleton)
  - `FeatureCompletionEngine` (transient)
  - `ClarificationEngine` (transient)
  - `RefactoringCoordinator` (transient)
  - `LLMProvider` (singleton per tenant)
  - `PromptTemplateManager` (singleton)
- ✅ cortex-operations.yaml updated with 3 new operations (suggest_implementation, clarify_requirements, refactor_code)
- ✅ YAML workflow definition created (`intelligence_workflow.yaml`)
- ✅ Session manager integration complete (cache AI responses)

### Multi-Tenant Wiring
- ✅ Multi-tenant isolation verified (tenant_id in all AI operations)
- ✅ RBAC permissions configured:
  - `ai.feature_completion` - Generate feature implementations
  - `ai.clarification` - Request requirement clarification
  - `ai.refactoring` - Refactor code with AI
  - Admin-only: `ai.token_management` - Adjust token quotas
- ✅ Token quota enforcement (per-tenant limits)
- ✅ Cross-tenant data isolation (AI responses not shared)

### Observability Wiring
- ✅ Logging instrumented (INFO: AI operation start/complete, ERROR: LLM failures)
- ✅ Monitoring metrics:
  - `ai_operation_success_rate` - Percentage of successful AI operations
  - `average_confidence_score` - Mean confidence across operations
  - `token_usage_per_tenant` - Tokens consumed by each tenant
  - `llm_response_time` - Average LLM call duration
- ✅ Alerts configured:
  - Confidence score below 0.5 (low quality)
  - Token budget 80% used (quota warning)
  - LLM timeout rate >10% (provider issues)

### Quality Wiring
- ✅ Error handling and rollback tested (revert knowledge graph, refund tokens)
- ✅ DoR/DoD validation enforced (LLM available, confidence ≥0.7)
- ✅ Test coverage: 83 tests (50 unit + 30 integration + 3 performance) = **98% coverage**
- ✅ Documentation generated (API docs, workflow diagrams)

### Integration Wiring
- ✅ Planning Orchestrator integration (feature completion)
- ✅ TDD Orchestrator integration (clarification, test suggestions)
- ✅ DevOps Orchestrator integration (refactoring, optimization)
- ✅ Requirements Gathering Engine coordination (upfront vs runtime clarification)
- ✅ Knowledge graph updates (learn from AI operations)

---

## 6️⃣ Complete Removal Strategy

### Archive Location
`cortex-brain/archives/orchestrators-legacy/intelligence/`

**Archived Files:**
- `test_intelligence.py` (~400 LOC)
- `refactoring_intelligence.py` (~600 LOC)
- `context_intelligence.py` (~500 LOC)
- `narrative_intelligence.py` (~400 LOC)
- `architecture_intelligence_agent.py` (~700 LOC)

**Total Archived:** ~2,600 LOC

### Grace Period: 30 Days (Week 6 - Week 10)

**Monitoring Schedule:**
- **Week 6-7:** Daily monitoring (AI success rate, confidence score)
- **Week 7-8:** Every 3 days (token usage trends)
- **Week 8-9:** Weekly checks (user feedback)
- **Week 9-10:** Final validation (30-day stability)

**Success Metrics:**
- AI operation success rate: ≥90% (target: 95%)
- Average confidence score: ≥0.8 (target: 0.85)
- Token usage increase: <10% (target: 5%)
- User satisfaction: ≥8/10 (target: 9/10)

### Rollback Script
`scripts/rollback/rollback_intelligence_orchestrator.py`

**Rollback Capabilities:**
- Restore old intelligence modules from archive
- Revert orchestrator integrations
- Restore old cortex-operations.yaml triggers
- Clear new orchestrator's DI registrations
- Revert knowledge graph updates (if needed)

**Rollback Trigger Conditions:**
- AI success rate drops below 80%
- Average confidence score below 0.6
- Token usage exceeds 150% of baseline
- Critical bug discovered (data loss, security issue)

### Deletion Checklist

- ✅ **Week 6-7:** Archive old files to `cortex-brain/archives/orchestrators-legacy/intelligence/`
- ✅ **Week 6:** Update orchestrator integrations (Planning, TDD, DevOps)
- ✅ **Week 6-7:** Run full test suite (83 tests pass)
- ✅ **Week 7-9:** Monitor production (success rate ≥90%, confidence ≥0.8, token usage <10% increase)
- ✅ **Week 8-9:** User feedback collection (AI suggestions helpful, satisfaction ≥8/10)
- ✅ **Week 10:** Final validation checks (30 days stable, all metrics met)
- ❌ **Week 10, End:** Permanent deletion (remove archive, delete rollback scripts)

### Permanent Deletion (After 30 Days)

**Actions:**
1. Delete `cortex-brain/archives/orchestrators-legacy/intelligence/` directory
2. Delete `scripts/rollback/rollback_intelligence_orchestrator.py`
3. Remove rollback capability from monitoring dashboard
4. Update documentation (remove references to old modules)
5. Archive grace period reports to `cortex-brain/documents/reports/intelligence-migration-complete.md`

**Validation:**
- System stable for 30+ days
- All success metrics met
- No rollback requests from users
- Stakeholder approval obtained

---

## 📊 Success Metrics Summary

| Metric | Current (Baseline) | Target | Validation Method |
|--------|-------------------|--------|-------------------|
| **Code Consolidation** | 2,600 LOC (5 files) | 1,000 LOC (6 files) | LOC count after implementation |
| **AI Success Rate** | N/A (new capability) | ≥90% | Monitor for 30 days |
| **Confidence Score** | N/A | ≥0.8 | Average across operations |
| **Token Usage** | N/A | <10% increase | Compare to baseline |
| **Response Time** | N/A | <60s feature, <30s clarify, <120s refactor | Performance tests |
| **Test Coverage** | 0% (no tests) | 98% | 83 tests (50 unit + 30 integration + 3 perf) |
| **User Satisfaction** | N/A | ≥8/10 | Survey after 30 days |

---

## 🎯 Phase 4 Integration Notes

**Intelligence Orchestrator is part of Phase 4: Intelligence & Onboarding (Week 6)**

**Dependencies:**
- **Requires:** Core infrastructure (Phase 1), Planning/Execution orchestrators (Phase 2)
- **Used by:** All other orchestrators (feature completion, clarification, refactoring)
- **Complements:** Requirements Gathering Engine (upfront clarification)

**Parallel Work:**
- Intelligence Orchestrator (Week 6, Day 1-5)
- Onboarding Orchestrator (Week 6, Day 1-5)
- Both can be developed in parallel (no dependencies between them)

**Deliverable:** AI-powered operations for feature completion, runtime clarification, multi-language refactoring

---

**Next Steps:** Proceed to [Onboarding Orchestrator Plan](09-onboarding-orchestrator-plan.md)
