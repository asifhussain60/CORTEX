# CORTEX Architecture Truth Document

**Version:** 1.0  
**Date:** 2026-02-10  
**Author:** Asif Hussain  
**Authority:** cortex-architect.prompt.md v15.3  
**Status:** AUTHORITATIVE — This document describes CORTEX as it actually exists

---

## 1. Vision and Design Philosophy

### 1.1 What Problem CORTEX Solves

CORTEX solves the fundamental failure mode of AI-assisted development: **unstructured, ungoverned, context-free code generation**.

Without CORTEX:
- AI assistants generate plausible but incorrect code
- No enforcement of TDD, security gates, or architectural standards
- Context is lost between sessions (no memory)
- No Definition of Ready (DoR) before implementation
- No audit trail of decisions
- No challenge mechanism when user requests suboptimal approaches

CORTEX provides:
1. **Governance Layer**: Enforces 29+ CORE rules before any code generation
2. **Intelligence Layer**: LENS protocol provides deep code understanding (Git history, AST, comments, patterns)
3. **Orchestration Layer**: Routes requests to specialized orchestrators (TDD, Refactoring, Planning)
4. **Challenge System**: Generates alternatives when detecting disagreement with user approach
5. **Definition of Ready Gate**: Requires explicit approval before implementation
6. **Audit Trail**: Every operation logged with AC markers (AC_START → AC_COMPLETE)

### 1.2 Why Normal AI Prompts Are Insufficient

Standard prompts fail because they are:
- **Stateless**: No memory between requests
- **Context-free**: No knowledge of codebase, patterns, or history
- **Ungoverned**: No enforcement of quality gates
- **Unstructured**: No workflow, just raw generation

CORTEX transforms prompts into a **governed intelligence pipeline**:

```
User Request → IntentRouter → LENS Analysis → DoR Gate → Orchestrator → Enforcement → Output
```

### 1.3 Core Design Principles

| Principle | Implementation | Enforcement |
|-----------|---------------|-------------|
| **TDD-First (CORE-008)** | Tests MUST exist before code | TDDOrchestrator blocks non-TDD flows |
| **MCP-First** | All functionality via MCP tools | Direct file operations blocked for IMPLEMENT/FIX |
| **Single Source of Truth (CORE-035)** | One canonical implementation per concern | HolisticValidationOrchestrator detects duplicates |
| **Git-Backed Registry** | wiring.yaml is authoritative | No SQLite, no runtime registration |
| **Lazy Loading** | Orchestrators instantiate on first use | Fast startup, low memory |
| **Graceful Degradation** | Fallback strategies when components fail | GracefulDegradationFramework in tier2/resilience.py |

### 1.4 How CORTEX Differs from Prompt Libraries

| Aspect | Prompt Library | CORTEX |
|--------|---------------|--------|
| **Execution** | Static text | Active orchestration with gates |
| **Intelligence** | None | LENS provides Git, AST, comment analysis |
| **Governance** | None | 29+ CORE rules with blocking enforcement |
| **Memory** | None | Registry tracks phases, state persists |
| **Challenge** | None | ChallengeGenerator proposes alternatives |
| **Audit** | None | AC markers in every operation |
| **Wiring** | None | Orchestrators wired via YAML specification |

---

## 2. High-Level Architecture (C4 Style)

### 2.1 System Context (Level 1)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CORTEX System                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   VS Code    │───▶│  MCP Server  │───▶│ Orchestrators│          │
│  │   Copilot    │    │  (Gateway)   │    │   (28 Total) │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Prompts    │    │   Registry   │    │ Intelligence │          │
│  │  & Agents    │    │ (wiring.yaml)│    │    (LENS)    │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  Knowledge   │    │  Governance  │    │   Templates  │          │
│  │  (45 YAMLs)  │    │  (CORE Rules)│    │  (Response)  │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Brain Tiers (Knowledge Hierarchy)

CORTEX organizes knowledge into 4 tiers with strict precedence:

| Tier | Location | Purpose | Precedence |
|------|----------|---------|------------|
| **Tier 0** | `cortex_brain/tier0/` | Immutable governance (CORE rules, response headers) | HIGHEST - Never overridden |
| **Tier 1** | `cortex_brain/tier1/` | Domain rules, acceptance criteria, orchestrator configs | High - Extends Tier 0 |
| **Tier 2** | `cortex_brain/tier2/` | Response templates, resilience, credential protection | Medium - Domain-specific |
| **Tier 3** | `cortex_brain/tier3/` | 35+ best practices YAMLs | Low - Guidance only |

**Loading Sequence** (defined in `cortex/brain/tier0/governance-loading-sequence.yaml`):
1. Phase 0 Bootstrap: core-rules.yaml (29 CORE rules)
2. Phase 1 Domain: tdd-rules.yaml, interaction-rules.yaml, planning-rules.yaml
3. Phase 2 Validation: ac-validation-checklist.yaml
4. Phase 3 Enforcement: phase-enforcement-map.yaml

### 2.3 Registry Architecture

**Source of Truth:** `cortex/wiring/specifications/wiring.yaml`

The registry defines ALL orchestrators, their dependencies, and capabilities:

```yaml
# wiring.yaml structure
version: '2.0'
orchestrators:
  core:      # Tier 1 - Framework orchestrators (11)
  domain:    # Tier 2 - Business domain orchestrators (8)
  support:   # Tier 3 - Infrastructure orchestrators (9)
analyzers:   # LENS analyzers (4)
config:      # Runtime configuration
```

**Registry Implementation:** `cortex/wiring/registry/git_backed_registry.py`
- Parses wiring.yaml at startup
- Creates LazyOrchestrator proxies (no immediate instantiation)
- Validates circular dependencies, missing references, duplicate names

### 2.4 Orchestrator Categories

**Core Orchestrators (11)** - Priority 10-100:
| Name | Module | Purpose |
|------|--------|---------|
| InteractionOrchestrator | core.interaction_orchestrator | LENS protocol, comprehension |
| ArchitectureGuard | core.architecture_guard | Pre-implementation validation |
| IntentRouter | core.intent_router | Intent classification, routing |
| ComplexityClassifier | core.complexity_classifier | Task complexity assessment |
| LENSSynthesis | core.lens_synthesis | LENS Phase 4 synthesis |
| EnforcementOrchestrator | core.enforcement_orchestrator | Governance pre-gate |
| TDDOrchestrator | core.tdd_orchestrator | TDD workflow (RED→GREEN→REFACTOR) |
| IncrementalTaskDecomposer | planning.incremental_task_decomposer | Token-budget decomposition |
| WorkflowOrchestrator | core.workflow_orchestrator | Multi-step workflows |
| MasterOrchestrator | core.master_orchestrator | Coordination hub (priority 100) |
| ReviewOrchestrator | core.review_orchestrator | Holistic verification |

**Domain Orchestrators (8)** - Priority 48-55:
| Name | Module | Purpose |
|------|--------|---------|
| CodeLevelPlanner | domain.code_level_planner | Implementation planning |
| CoherenceValidator | domain.coherence_validator | Cross-layer alignment |
| RefactoringOrchestrator | domain.enhanced_refactoring_orchestrator | Code improvement |
| PlanningOrchestrator | domain.enhanced_planning_orchestrator | Phase management |
| DocumentationOrchestrator | domain.enhanced_documentation_orchestrator | Doc generation |
| PhaseExecutor | domain.phase_executor | Phase execution |
| AutonomousExecutionEngine | domain.autonomous_execution_engine | Multi-step autonomous |
| ConversationOrchestrator | conversation_orchestrator | Context tracking |

**Support Orchestrators (9)** - Priority 60-70:
| Name | Module | Purpose |
|------|--------|---------|
| OrchestratorEventBus | infrastructure.orchestrator_event_bus | Event backbone |
| OnboardingOrchestrator | onboarding.orchestrator | User onboarding |
| ToolDiscoveryOrchestrator | core.tool_discovery_orchestrator | MCP tool discovery |
| UpgradeOrchestrator | support.upgrade_orchestrator | Version upgrades |
| RollbackOrchestrator | support.rollback_orchestrator | Checkpoint restore |
| SetupOrchestrator | support.setup_orchestrator | Environment setup |
| GovernanceRegistry | brain.core.governance_registry | Rule management |
| KnowledgeRepository | brain.core.knowledge.knowledge_repository | Knowledge access |
| PlanOrchestrator | support.plan_orchestrator | PLAN MODE lifecycle |

### 2.5 Control Flow

```
User Request
     │
     ▼
┌────────────────────┐
│ MCP Server Gateway │ (cortex/mcp/server.py)
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   IntentRouter     │ Classifies: IMPLEMENT | FIX | REFACTOR | ANALYZE | PLAN
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  LENSSynthesis     │ Gathers: Git + AST + Comments + Domain knowledge
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ EnforcementOrch    │ Validates: 29 CORE rules, blocks violations
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ MasterOrchestrator │ Routes to domain orchestrator
└─────────┬──────────┘
          │
          ├── IMPLEMENT/FIX → TDDOrchestrator
          ├── REFACTOR → RefactoringOrchestrator
          ├── PLAN → PlanOrchestrator
          └── ANALYZE → LENSOrchestrator
                        │
                        ▼
                   ┌─────────┐
                   │ Output  │ Formatted via ResponseTemplate
                   └─────────┘
```

---

## 3. Intelligence Layer

### 3.1 What "Intelligence" Means in CORTEX

Intelligence in CORTEX is **contextual code understanding** derived from:
1. **Git History**: Commit patterns, authors, blame, change frequency
2. **AST Analysis**: Code structure, functions, classes, complexity
3. **Comment Extraction**: TODOs, FIXMEs, docstrings, intent markers
4. **Pattern Detection**: Architecture patterns, anti-patterns, code smells
5. **Domain Knowledge**: 45 best-practice YAMLs, tech stack mappings

Intelligence is NOT:
- LLM inference (CORTEX does not call OpenAI/Claude APIs)
- Semantic search (no embeddings)
- Machine learning (no trained models)

### 3.2 LENS Protocol (Language → Examination → Navigation → Synthesis)

**Implementation:** `cortex/lens/orchestrator.py` (LENSOrchestrator)

| Phase | Analyzer | Output |
|-------|----------|--------|
| **Language** | NLP intent parsing | Intent type, confidence score |
| **Examination** | GitHistoryAnalyzer, ASTAnalyzer, CommentExtractor | Structured code facts |
| **Navigation** | KnowledgeRepository, DomainBrain | Best practices, rules |
| **Synthesis** | LENSSynthesis | Recommendations, DoR |

**Analyzer Implementations:**
- `cortex/lens/analyzers/git_history_analyzer.py`: Git log, blame, diff
- `cortex/brain/analysis/ast_analyzer.py`: Python AST parsing
- `cortex/brain/analysis/comment_extractor.py`: TODO/FIXME extraction
- `cortex/lens/analyzers/polyglot_analyzer.py`: Multi-language support

### 3.3 Intelligence Providers

**Base Contract:** `cortex/intelligence/base.py`

```python
class BaseIntelligenceEngine(ABC):
    @abstractmethod
    def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """Analyze code and return intelligence."""
        pass
    
    @abstractmethod
    def validate_context(self, context: AnalysisContext) -> bool:
        """Validate context suitability."""
        pass
```

**Current Implementations:**
- `RelationshipTraversalEngine`: Cross-file relationship analysis
- `PatternDetector`: Design pattern detection
- `CallGraphBuilder`: Function call relationships
- `DependencyMapper`: Import/dependency mapping

### 3.4 Context Maintenance Across Steps

CORTEX maintains context via:
1. **LENSContext dataclass**: Carries Git, AST, comment analysis between phases
2. **StateManager**: Persists operation state (`cortex/brain/core/state_manager.py`)
3. **UnifiedIntelligenceContext**: Aggregates all intelligence sources
4. **OrchestratorEventBus**: Publishes events for context propagation

**Context Flow:**
```
LENSOrchestrator.analyze_file()
       │
       ▼
LENSContext {
  git_analysis: {...},
  ast_analysis: {...},
  comment_analysis: {...},
  metadata: {timing, cache_hits}
}
       │
       ▼
IntentRouter.route(context=lens_context)
       │
       ▼
TDDOrchestrator.execute(context=lens_context)
```

### 3.5 Preventing Architectural Drift

**Mechanism:** HolisticValidationOrchestrator (`cortex/orchestrators/holistic/holistic_validation_orchestrator.py`)

Validates before implementation:
1. Registry consistency (index.yaml ↔ wiring.yaml)
2. Orchestrator dependency integrity
3. No circular dependencies
4. Architecture alignment with CORE rules
5. Risk scoring for proposed changes

**Enforcement:** CORE-048 requires HolisticValidation pass before any IMPLEMENT intent.

---

## 4. Orchestrators and Decision Making

### 4.1 MasterOrchestrator (Coordination Hub)

**Location:** `cortex/orchestrators/core/master_orchestrator.py`

**Purpose:** Routes operations to appropriate domain orchestrators, coordinates multi-step workflows.

**Inputs:**
- `operation_name`: String identifier (e.g., "process_request")
- `parameters`: Dict with request details, context
- `lens_context`: Optional pre-computed LENS analysis

**Outputs:**
- `Result[Dict, Error]`: Success with output dict or error

**Routing Logic:**
```python
def coordinate_operation(self, operation: str, params: Dict) -> Result:
    # 1. Classify intent
    intent = self.intent_router.classify_intent(params)
    
    # 2. Run enforcement gate
    enforcement_result = self.enforcement_orchestrator.validate(intent, params)
    if enforcement_result.is_blocked():
        return Err(enforcement_result.violations)
    
    # 3. Route to domain orchestrator
    target_orch = self.get_orchestrator_for_intent(intent)
    return target_orch.execute(params)
```

**Gates Enforced:**
- IntentRouter: Classifies with confidence threshold (0.75+)
- EnforcementOrchestrator: Blocks Tier 0 violations
- DoRApprovalGate: Requires user approval before execution

### 4.2 IntentRouter (Classification)

**Location:** `cortex/orchestrators/core/intent_router.py`

**Purpose:** Classifies user requests into canonical intent types.

**Intent Types (Exclusive):**
| Intent | Primary Orchestrator | Confidence Threshold |
|--------|---------------------|---------------------|
| IMPLEMENT | TDDOrchestrator | 0.85 |
| FIX | TDDOrchestrator | 0.85 |
| REFACTOR | RefactoringOrchestrator | 0.80 |
| ANALYZE | LENSOrchestrator | 0.75 |
| PLAN | PlanOrchestrator | 0.85 |
| AUDIT | HolisticValidationOrchestrator | 0.80 |

**Routing Rules (from `intent-routing.yaml`):**
```yaml
IMPLEMENT:
  aliases: ["implement", "create", "develop", "build", "add"]
  primary_orchestrator: "TDDOrchestrator"
  routing_rules:
    - rule: "keyword_based"
      keywords: ["implement", "create", "develop", "feature", "new"]
      priority: 100
    - rule: "context_based"
      context_signals: ["test_first", "tdd", "red_green_refactor"]
      priority: 90
```

### 4.3 TDDOrchestrator (Implementation)

**Location:** `cortex/orchestrators/core/tdd_orchestrator.py`

**Purpose:** Enforces TDD workflow for all IMPLEMENT/FIX intents.

**Workflow Phases:**
1. **RED**: Generate failing test
2. **GREEN**: Minimal code to pass
3. **REFACTOR**: Improve design (delegates to RefactoringOrchestrator)

**Gates:**
- CORE-008: Tests MUST exist before implementation code
- Coverage threshold: 80%+ required
- Type hints: 100% required

**Knowledge Integration:**
```python
class TDDKnowledgeLoader:
    """Loads TDD best practices from cortex_brain/tier3/knowledge/"""
    
    def get_guidance(self, module_path: str) -> TDDImplementationGuidance:
        # Load discipline rules from YAML
        # Return phase-specific guidance
```

### 4.4 EnforcementOrchestrator (Governance Gate)

**Location:** `cortex/orchestrators/core/enforcement_orchestrator.py`

**Purpose:** Pre-execution validation against 3-tier governance.

**Agents (3):**
1. **GovernanceEnforcementAgent**: CORE-008, 011, 012, 013, 029, 030, 035
2. **SecurityCheckpointAgent**: CORE-026, 025, 027
3. **ComplianceValidationAgent**: Tier 1 phase rules

**Enforcement Levels:**
| Level | Meaning | Action |
|-------|---------|--------|
| BLOCKED | Tier 0 violation | Stop execution, return error |
| WARNING | Tier 1 concern | Log warning, allow with escalation |
| PASS | No violations | Continue execution |

**Validation Flow:**
```python
def validate_operation(self, operation: Dict) -> EnforcementResult:
    # Run all agents in parallel
    with ThreadPoolExecutor() as executor:
        results = executor.map(
            lambda agent: agent.validate(operation),
            [self.governance_agent, self.security_agent, self.compliance_agent]
        )
    
    # Aggregate results
    violations = []
    warnings = []
    for result in results:
        violations.extend(result.violations)
        warnings.extend(result.warnings)
    
    # Determine level
    if violations:
        return EnforcementResult(level=BLOCKED, violations=violations)
    elif warnings:
        return EnforcementResult(level=WARNING, warnings=warnings)
    return EnforcementResult(level=PASS)
```

### 4.5 Is MasterOrchestrator Truly in Control?

**Answer: Partially.**

MasterOrchestrator coordinates but does NOT monopolize control:

**MasterOrchestrator Controls:**
- High-level routing (intent → orchestrator)
- State persistence across turns
- Response header injection
- Audit trail logging

**Delegated to Domain Orchestrators:**
- Actual execution logic
- Domain-specific validation
- Intermediate outputs

**Shared with EnforcementOrchestrator:**
- Governance gate (EnforcementOrchestrator can BLOCK regardless of MasterOrchestrator)

**Not Controlled by MasterOrchestrator:**
- MCP tool invocation (goes through MCP Server directly)
- LENS analysis (LENSOrchestrator owns this)
- Challenge generation (InteractionOrchestrator with ChallengeGenerator)

---

## 5. Governance and Definition of Ready Enforcement

### 5.1 DoR Enforcement Flow

**Definition of Ready (DoR)** = Structured validation BEFORE any planning or coding.

**Enforcement Points:**
1. **IntentRouter**: Classifies intent, requires confidence ≥0.75
2. **LENSSynthesis**: Gathers context, generates DoR display
3. **DoRApprovalGate**: Displays DoR table, waits for user "proceed"
4. **EnforcementOrchestrator**: Validates against CORE rules

**DoR Display Format:**
```markdown
## 🧠 CORTEX IMPLEMENT
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

### Definition of Ready
| Field | Value |
|-------|-------|
| Intent | IMPLEMENT |
| Confidence | 0.92 |
| Target | cortex/orchestrators/new_feature.py |
| Dependencies | TDDOrchestrator, LENSOrchestrator |
| CORE Rules | 008, 011, 012, 013 |
| Risk Score | 0.35 (LOW) |

Awaiting approval: "proceed" to continue
```

### 5.2 Acceptance Criteria Embedding

**AC Markers** track every operation:
```python
# AC_START: AC-PHASE48-S1-001
# Description: Implement holistic validation
# Expected: Pass/Fail status

# ... implementation code ...

# AC_COMPLETE: AC-PHASE48-S1-001 ✅ Tests passing
```

**Template-Driven AC:**
- Each phase YAML in `cortex-registry/_cortex-master/phases/` defines acceptance criteria
- AC-ID format: `AC-{PHASE}-{STAGE}-{NUMBER}` (e.g., `AC-PHASE48-S1-001`)
- Audit logger validates AC markers present

### 5.3 Risk Analysis Integration

**Risk Scoring** (HolisticValidationOrchestrator):
```python
def calculate_risk_score(self, target: str, operation: str) -> float:
    factors = {
        "affected_files": len(self.get_affected_files(target)),
        "dependency_depth": self.get_dependency_depth(target),
        "test_coverage": self.get_test_coverage(target),
        "change_frequency": self.get_change_frequency(target),
    }
    
    # Weighted sum (0.0 = no risk, 1.0 = critical)
    return (
        factors["affected_files"] * 0.2 +
        factors["dependency_depth"] * 0.3 +
        (1 - factors["test_coverage"]) * 0.3 +
        factors["change_frequency"] * 0.2
    )
```

**Risk Thresholds:**
- 0.0-0.3: LOW (proceed normally)
- 0.3-0.6: MEDIUM (additional review recommended)
- 0.6-0.8: HIGH (challenge gate mandatory)
- 0.8-1.0: CRITICAL (architect approval required)

### 5.4 Templates and YAML Driving Structured Thinking

**Template Location:** `cortex_brain/tier2/response-templates-index.yaml`

**Template Categories:**
- `success-response`: Completed operations
- `error-response`: Failed operations with remediation
- `warning-response`: Non-blocking concerns
- Domain templates for governance, planning, refactoring

**YAML-Driven Workflow:**
```yaml
# Phase specification drives entire workflow
id: "phase-48"
name: "Holistic Validation & Challenge Gate"
stages:
  - id: "S1"
    name: "HolisticValidationOrchestrator"
    tests: 12
    coverage_target: 90
    acceptance_criteria:
      - "AC-PHASE48-S1-001: Registry validation passes"
      - "AC-PHASE48-S1-002: Dependency check passes"
```

---

## 6. CORTEX LENS

### 6.1 Architectural Position

LENS is the **intelligence substrate** for all CORTEX operations. It provides:
- Code understanding (not generation)
- Pattern detection (not execution)
- Context enrichment (not decision)

**NOT a standalone tool** — LENS is consumed by orchestrators:
```
IntentRouter ← LENSContext
TDDOrchestrator ← LENSContext
RefactoringOrchestrator ← LENSContext
```

### 6.2 LENS Consumption Pattern

```python
# Orchestrator consumes LENS
class TDDOrchestrator:
    def execute(self, request: Dict, lens_context: LENSContext) -> Result:
        # Use LENS for test generation guidance
        existing_tests = lens_context.ast_analysis.get("test_functions", [])
        code_complexity = lens_context.ast_analysis.get("complexity", 0)
        
        # Generate tests informed by LENS
        tests = self.generate_tests(
            target=request["target"],
            complexity=code_complexity,
            existing=existing_tests
        )
```

### 6.3 LENS → Visual Intelligence Conversion

**LENS Dashboard** (`cortex/lens/dashboard_data_aggregator.py`):
- Aggregates LENS analysis into dashboard-ready JSON
- Powers HTML dashboards (plan-viewer.html, etc.)
- Provides metrics: complexity, coverage, dependencies

**Visual Output:**
```json
{
  "overview": {
    "total_files": 156,
    "total_functions": 892,
    "average_complexity": 4.2
  },
  "hotspots": [
    {"file": "master_orchestrator.py", "complexity": 12.5},
    {"file": "intent_router.py", "complexity": 8.3}
  ],
  "dependencies": {
    "MasterOrchestrator": ["IntentRouter", "LENSSynthesis", "TDDOrchestrator"]
  }
}
```

### 6.4 LENS Integration with Registry and Wiring

**LENS Analyzers in wiring.yaml:**
```yaml
analyzers:
  - name: GitHistoryAnalyzer
    module: cortex.lens.analyzers.git_history_analyzer
    class: GitHistoryAnalyzer
    purpose: Extract commit history, blame, author patterns
    priority: 1
  
  - name: ASTAnalyzer
    module: cortex.brain.analysis.ast_analyzer
    class: ASTAnalyzer
    purpose: Extract code structure, functions, classes, imports
    priority: 2
  
  - name: CommentExtractor
    module: cortex.brain.analysis.comment_extractor
    class: CommentExtractor
    purpose: Extract TODOs, FIXMEs, intent hints from comments
    priority: 3
  
  - name: SecurityThreatAnalyzer
    module: cortex.brain.analysis.security_threat_analyzer
    class: SecurityThreatAnalyzer
    purpose: Detect CWE vulnerabilities
    priority: 4
```

---

## 7. Workflow Lifecycle

### 7.1 Foundation Phase (Request Parsing)

**Input:** User natural language request  
**Output:** Classified intent with confidence

```
"implement a new TDD orchestrator test"
            │
            ▼
IntentRouter.classify_intent()
            │
            ▼
RoutingDecision {
  intent_type: IMPLEMENT,
  confidence_score: 0.92,
  target_handler: "TDDOrchestrator",
  reasoning: "Keywords: implement, TDD, test"
}
```

### 7.2 Core Phase (Intelligence Gathering)

**Input:** Classified intent  
**Output:** LENS context with analysis

```
RoutingDecision
       │
       ▼
LENSOrchestrator.analyze_file(target)
       │
       ├── GitHistoryAnalyzer.analyze()
       ├── ASTAnalyzer.analyze()
       └── CommentExtractor.analyze()
       │
       ▼
LENSContext {
  git_analysis: {
    commits: 15,
    last_author: "Asif Hussain",
    change_frequency: "HIGH"
  },
  ast_analysis: {
    functions: 23,
    classes: 4,
    complexity: 6.2
  },
  comment_analysis: {
    todos: 3,
    fixmes: 1
  }
}
```

### 7.3 Validation Phase (Gates)

**Input:** LENS context + Intent  
**Output:** Enforcement result (PASS/WARN/BLOCK)

```
LENSContext + Intent
        │
        ▼
EnforcementOrchestrator.validate_operation()
        │
        ├── GovernanceEnforcementAgent.validate()
        ├── SecurityCheckpointAgent.validate()
        └── ComplianceValidationAgent.validate()
        │
        ▼
EnforcementResult {
  level: PASS,
  violations: [],
  warnings: ["CORE-012: Docstring missing in 2 functions"]
}
```

### 7.4 Example: IMPLEMENT Request

**User:** "implement a new health check endpoint for the MCP server"

**Step 1: Intent Classification**
```
IntentRouter → IMPLEMENT (0.94 confidence)
Keywords matched: implement, new, endpoint
```

**Step 2: LENS Analysis**
```
Target: cortex/mcp/server.py
Git: 45 commits, last modified 2 days ago
AST: 15 functions, 3 classes, complexity 4.8
Comments: 2 TODOs related to health checks
```

**Step 3: DoR Display**
```markdown
## 🧠 CORTEX IMPLEMENT
| Field | Value |
|-------|-------|
| Intent | IMPLEMENT |
| Target | cortex/mcp/server.py |
| Complexity | MODERATE |
| Dependencies | MCPServer, HealthCheckExecutor |
| CORE Rules | 008 (TDD), 011 (Types), 012 (Docstrings) |

Awaiting approval: "proceed" to continue
```

**Step 4: User Approves** → "proceed"

**Step 5: TDD Execution**
```
TDDOrchestrator.execute()
  │
  ├── RED: Generate test_health_check_endpoint()
  │       → tests/mcp/test_health_check.py
  │       → Run: FAIL (endpoint not implemented)
  │
  ├── GREEN: Implement /health endpoint
  │       → cortex/mcp/server.py
  │       → Run: PASS
  │
  └── REFACTOR: Optimize if needed
          → No refactoring required
```

**Step 6: Completion**
```
# AC_COMPLETE: AC-IMPLEMENT-MCP-HEALTH-001 ✅
# Tests: 5/5 passing
# Coverage: 92%
```

---

## 8. Team Collaboration Model

### 8.1 Role-Based Access

| Role | CORTEX Usage | Key Commands |
|------|--------------|--------------|
| **Product Owner** | Define requirements, review DoR | `/plan`, `/audit` |
| **Architect** | Design decisions, governance | `/analyze`, `/audit`, `/design` |
| **Engineer** | Implementation, fixes | `/implement`, `/fix`, `/refactor` |
| **Contractor** | Scoped implementation | `/implement` (with strict governance) |
| **AI Agent** | Automated tasks | MCP tools (cortex_process_request) |

### 8.2 Shared Intelligence Layer

CORTEX provides **team-wide intelligence**:

1. **Knowledge Repository** (`cortex/knowledge/best-practices/`)
   - 40+ best practice guides
   - Tech-stack specific patterns
   - Security checklists

2. **Phase Registry** (`cortex-registry/_cortex-master/`)
   - 60+ phases tracked
   - Status: planned/in_progress/completed
   - Dependencies mapped

3. **Audit Trail** (`cortex_brain/audit-logs/`)
   - Every operation logged
   - AC markers preserved
   - Searchable history

### 8.3 Governance Consistency

All team members get **identical governance**:
- Same CORE rules
- Same DoR requirements
- Same approval gates
- Same audit trail

**No bypasses** for any role (CORE rules are Tier 0 = immutable).

---

## 9. Extensibility Model

### 9.1 Adding New Orchestrators

**Step 1:** Create orchestrator class in `cortex/orchestrators/{category}/`
```python
class NewOrchestrator:
    def __init__(self):
        self.name = "NewOrchestrator"
    
    def health_check(self) -> bool:
        return True
    
    def execute(self, params: Dict) -> Result:
        # Implementation
        pass
```

**Step 2:** Add to `wiring.yaml`
```yaml
orchestrators:
  domain:
    - name: NewOrchestrator
      module: cortex.orchestrators.domain.new_orchestrator
      class: NewOrchestrator
      tier: 2
      priority: 56
      dependencies: [MasterOrchestrator]
      capabilities: [new_capability]
      health_check: health_check
```

**Step 3:** Run validation
```bash
python -c "from cortex.wiring import bootstrap_cortex; bootstrap_cortex()"
```

### 9.2 Adding New Templates

**Location:** `cortex_brain/tier2/response-templates/`

**Step 1:** Create template YAML
```yaml
id: "new-template"
name: "New Template"
sections:
  - header: "Result"
  - body: "{{content}}"
  - footer: "Generated by CORTEX"
```

**Step 2:** Register in `response-templates-index.yaml`
```yaml
domain_templates:
  new_domain:
    templates:
      - id: "new-template"
        path: "domains/new_domain/new-template.yaml"
```

### 9.3 Adding New Knowledge

**Location:** `cortex/knowledge/best-practices/{category}/`

**Step 1:** Create YAML file
```yaml
metadata:
  title: "New Best Practice"
  version: "1.0"
  keywords: [keyword1, keyword2]

practices:
  - id: "PRACTICE-001"
    description: "Description"
    guidance: "How to apply"
    examples:
      - "Example 1"
```

**Step 2:** Register in `INDEX.yaml`
```yaml
new_category:
  description: "New category"
  guides:
    - path: "new_category/new-best-practice.yaml"
      title: "New Best Practice"
```

### 9.4 Adding New Phases

**Location:** `cortex-registry/_cortex-master/phases/active/`

**Step 1:** Create phase YAML
```yaml
id: "phase-71"
name: "New Phase"
status: "planned"
priority: "P1"
stages:
  - id: "S1"
    name: "Stage 1"
    tests: 20
    coverage_target: 90
```

**Step 2:** Register in `index.yaml`
```yaml
active_phases:
  - id: "phase-71"
    name: "New Phase"
    file: "phases/active/phase-71-new-phase.yaml"
    status: "planned"
```

### 9.5 Enterprise Scaling

**Multi-Repo Support:**
- Each repo can have `.cortex/` directory with local overrides
- Company-wide rules in `cortex-registry/company/`
- Domain-specific rules in `cortex-registry/domains/`

**CI/CD Integration:**
- MCP server runs as container (see Dockerfile)
- Health check endpoint: `/health`
- Prometheus metrics: `/metrics`

---

## 10. Known Gaps, Risks, and Blind Spots

### 10.1 Partially Implemented

| Feature | Status | Gap |
|---------|--------|-----|
| **Phase 70 Alignment** | Planned | 25 wired-not-implemented orchestrators |
| **LENS .NET Support** | Phase 67 | Only Python deep analysis currently |
| **Runtime Correlation** | Phase 69 | No live APM integration |
| **Knowledge Graph** | Phase 66 S2 | Only architecture patterns, no full graph |

### 10.2 Convention vs Enforcement

| Convention | Enforcement Status |
|------------|-------------------|
| AC marker format | **NOT ENFORCED** - Relies on developer discipline |
| File naming (kebab-case) | **PARTIAL** - FileNamingEnforcementAgent exists but not all paths covered |
| Docstring presence | **WARNING ONLY** - Not blocking |
| Response header | **ENFORCED** - ResponseHeaderInjector injects automatically |

### 10.3 Architectural Drift Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| wiring.yaml out of sync with implementations | MEDIUM | HIGH | Phase 70 alignment remediation |
| New orchestrators added without wiring | LOW | MEDIUM | Bootstrap validation catches this |
| Knowledge YAMLs outdated | MEDIUM | LOW | Manual review quarterly |
| CORE rules inconsistent with code | LOW | HIGH | EnforcementOrchestrator validates |

### 10.4 Intelligence Not Fully Wired

| Intelligence Source | Wiring Status |
|--------------------|---------------|
| Git history | ✅ Wired via GitHistoryAnalyzer |
| AST analysis | ✅ Wired via ASTAnalyzer |
| Comment extraction | ✅ Wired via CommentExtractor |
| Security analysis | ✅ Wired via SecurityThreatAnalyzer |
| Pattern detection | ⚠️ PatternDetector exists but not in wiring.yaml |
| Call graph | ⚠️ CallGraphBuilder exists but not in wiring.yaml |
| Dependency mapper | ⚠️ DependencyMapper exists but not in wiring.yaml |

### 10.5 Remaining Phase Work

| Phase | Status | Blocking |
|-------|--------|----------|
| Phase 65 | 1/9 stages | LENS intelligence gaps |
| Phase 66 | 1/4 stages | Knowledge graph not complete |
| Phase 67 | 0/4 stages | .NET Roslyn integration |
| Phase 68 | 0/4 stages | Angular deep analysis |
| Phase 69 | 0/4 stages | Runtime correlation |
| Phase 70 | 0/4 stages | P0 alignment remediation |

---

## 11. Example End-to-End Trace

### Request: `/implement user authentication middleware`

**T+0ms: MCP Gateway**
```python
# cortex/mcp/server.py
request = MCPRequest(
    method="tools/call",
    params={"name": "cortex_process_request", "arguments": {...}}
)
```

**T+5ms: IntentRouter**
```python
# cortex/orchestrators/core/intent_router.py
decision = RoutingDecision(
    intent_type=IntentType.IMPLEMENT,
    confidence_score=0.91,
    target_handler="TDDOrchestrator",
    keyword_matches=["implement", "middleware"]
)
```

**T+50ms: LENSOrchestrator**
```python
# cortex/lens/orchestrator.py
context = LENSContext(
    git_analysis={"commits": 12, "authors": ["Asif"]},
    ast_analysis={"functions": 8, "complexity": 3.2},
    comment_analysis={"todos": 1}
)
```

**T+80ms: EnforcementOrchestrator**
```python
# cortex/orchestrators/core/enforcement_orchestrator.py
result = EnforcementResult(
    level=EnforcementLevel.PASS,
    violations=[],
    warnings=[]
)
```

**T+100ms: DoR Display**
```markdown
## 🧠 CORTEX IMPLEMENT
| Intent | IMPLEMENT |
| Target | cortex/api/middleware/auth.py |
| TDD Required | ✅ |
```

**T+100ms+: User "proceed"**

**T+150ms: TDDOrchestrator RED Phase**
```python
# Generate test first
# tests/api/middleware/test_auth.py
def test_auth_middleware_validates_token():
    ...
```

**T+500ms: TDDOrchestrator GREEN Phase**
```python
# Implement minimal code
# cortex/api/middleware/auth.py
class AuthMiddleware:
    def validate_token(self, token: str) -> bool:
        ...
```

**T+800ms: Tests Pass**
```
PASSED tests/api/middleware/test_auth.py::test_auth_middleware_validates_token
```

**T+850ms: Completion**
```python
# AC_COMPLETE: AC-IMPLEMENT-AUTH-001 ✅
return {
    "status": "success",
    "tests_passing": 5,
    "coverage": 94,
    "files_created": ["cortex/api/middleware/auth.py", "tests/api/middleware/test_auth.py"]
}
```

---

## 12. File/Folder Map

### Core Structure

| Path | Purpose |
|------|---------|
| `cortex/` | Main Python package |
| `cortex/orchestrators/` | All 28 orchestrators |
| `cortex/orchestrators/core/` | Tier 1 core orchestrators |
| `cortex/orchestrators/domain/` | Tier 2 domain orchestrators |
| `cortex/orchestrators/support/` | Tier 3 support orchestrators |
| `cortex/mcp/` | MCP server and tools |
| `cortex/mcp/server.py` | JSON-RPC MCP server |
| `cortex/mcp/tools/` | Individual MCP tools |
| `cortex/lens/` | LENS intelligence layer |
| `cortex/lens/analyzers/` | Git, AST, comment analyzers |
| `cortex/wiring/` | Orchestrator wiring system |
| `cortex/wiring/specifications/wiring.yaml` | **SOURCE OF TRUTH** |
| `cortex/wiring/registry/` | GitBackedRegistry |
| `cortex/governance/` | Governance enforcement |
| `cortex/intelligence/` | Intelligence engines |
| `cortex/knowledge/` | Best practices (40+ YAMLs) |

### Brain Tiers

| Path | Purpose |
|------|---------|
| `cortex_brain/` | Knowledge and rules |
| `cortex_brain/tier0/` | Immutable governance (CORE rules) |
| `cortex_brain/tier0/governance/core-rules.yaml` | 29 CORE rules |
| `cortex_brain/tier1/` | Domain rules, profiles |
| `cortex_brain/tier2/` | Templates, resilience |
| `cortex_brain/tier3/` | Best practices knowledge |

### Registry

| Path | Purpose |
|------|---------|
| `cortex-registry/` | Phase tracking, planning |
| `cortex-registry/_cortex-master/` | CORTEX self-development |
| `cortex-registry/_cortex-master/index.yaml` | Phase index |
| `cortex-registry/_cortex-master/phases/` | Phase specifications |
| `cortex-registry/company/` | Company-wide overrides |
| `cortex-registry/domains/` | Domain-specific rules |

### Prompts and Agents

| Path | Purpose |
|------|---------|
| `.github/prompts/` | Prompt files for Copilot |
| `.github/prompts/cortex-architect.prompt.md` | ARCHITECT mode prompt |
| `.github/prompts/CORTEX.prompt.md` | PRODUCTION mode prompt |
| `.github/agents/core/` | Agent specifications |

### Tests

| Path | Purpose |
|------|---------|
| `tests/` | Test suite |
| `tests/unit/` | Unit tests |
| `tests/integration/` | Integration tests |
| `tests/wiring/` | Wiring validation tests |

---

## 13. How CORTEX Should Be Understood by a New Architect

### 13.1 Mental Model

Think of CORTEX as a **governed AI co-pilot factory**:

1. **Input**: Natural language requests from humans or AI agents
2. **Intelligence**: LENS provides deep code understanding (not generation)
3. **Governance**: CORE rules prevent bad outputs before they happen
4. **Orchestration**: Specialized orchestrators handle different intents
5. **Output**: High-quality, tested, governed code changes

### 13.2 Key Principles to Internalize

1. **MCP-First**: All functionality exposed via MCP tools. Never bypass.
2. **TDD-First**: Tests before code. Always.
3. **Git-Backed**: wiring.yaml is the source of truth. No runtime registration.
4. **Lazy Loading**: Orchestrators load on first use. Fast startup.
5. **Graceful Degradation**: Failures trigger fallbacks, not crashes.
6. **Audit Everything**: AC markers in every operation.

### 13.3 Where to Start

1. **Read wiring.yaml**: Understand what orchestrators exist and how they're wired
2. **Read MasterOrchestrator**: Understand the coordination hub
3. **Read IntentRouter**: Understand how requests are classified
4. **Read TDDOrchestrator**: Understand the core implementation workflow
5. **Read EnforcementOrchestrator**: Understand governance enforcement
6. **Run tests**: `pytest tests/wiring/` to verify wiring integrity

### 13.4 Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "CORTEX is a prompt library" | No — It's an active orchestration system with gates |
| "CORTEX calls LLM APIs" | No — CORTEX consumes Copilot; it doesn't invoke LLMs |
| "I can add orchestrators at runtime" | No — All orchestrators defined in wiring.yaml |
| "CORE rules are suggestions" | No — Tier 0 rules are BLOCKING, not optional |
| "LENS generates code" | No — LENS provides context; orchestrators generate |

### 13.5 Architecture Decision Records (ADRs)

Key decisions embedded in CORTEX:

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | Git-backed registry | Trackable, diff-able, no database drift |
| ADR-002 | Lazy orchestrator loading | Fast startup, low memory |
| ADR-003 | YAML-driven governance | Human-readable, Git-tracked |
| ADR-004 | MCP-first architecture | Tool-based integration, no direct imports |
| ADR-005 | TDD mandatory | Quality by design, not inspection |
| ADR-006 | Tiered brain | Clear precedence, conflict resolution |

---

## 14. Brittleness, Wiring Integrity, and Permanent Deployment Readiness

**See:** [CORTEX-ARCHITECTURE-TRUTH-DOCUMENT-SECTION-14.md](./CORTEX-ARCHITECTURE-TRUTH-DOCUMENT-SECTION-14.md)

This mandatory section covers:
- 14.1 Wiring Integrity Proof (Static) — Wiring Truth Table
- 14.2 Runtime Wiring & Deployability — Environment assumptions
- 14.3 Brittleness Hotspots — Magic strings, silent fallbacks, tight coupling
- 14.4 Invariants and Guarantees — Non-negotiable requirements
- 14.5 FMEA Table — Top 15 failure modes
- 14.6 Self-Healing and Safe Degradation — Graceful degradation framework
- 14.7 Security Brittleness — Threat model and mitigations
- 14.8 Observability and Diagnostic Readiness — Debug playbooks
- 14.9 Test Strategy for Brittleness — Schema, smoke, golden path, break-the-wiring tests
- 14.10 Minimal, High-Impact Fixes — Prioritized P0/P1/P2/P3 fixes

---

*This document is authoritative. All claims reference actual CORTEX files. Gaps are explicitly stated as "not implemented yet."*
