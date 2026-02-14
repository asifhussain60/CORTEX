# CORTEX Universal Orchestration Agent

**Version:** 1.0 | **Updated:** 2026-02-14 | **Authority:** MCP-First Architecture | **Status:** ✅ ACTIVE

---

## 🎯 Purpose

**Single source of truth** for how CORTEX orchestrators work together across ALL modes (ARCHITECT, PRODUCTION, DESIGN, ANALYZE).

**Used by:**
- `cortex-architect.prompt.md` — CORTEX self-development
- `CORTEX.prompt.md` — Production repository operations
- WorkflowRuntime (future) — Dynamic workflow composition

**Why this exists:** Eliminates duplication between prompts, documents existing wiring, enables consistent orchestration across all CORTEX modes.

---

## 📐 4-Stage Orchestration Pipeline

**EVERY CORTEX operation flows through these stages:**

```
USER REQUEST
    ↓
STAGE 1: INTERACTION (Comprehension + Challenges)
    ↓
STAGE 2: INTENT (Classification + Routing)
    ↓
STAGE 3: INTELLIGENCE (LENS + Knowledge Synthesis)
    ↓
STAGE 4: EXECUTION (Domain Orchestrators)
```

---

## 🔄 STAGE 1: Interaction Layer

**Orchestrator:** `InteractionOrchestrator`  
**Location:** `cortex/brain/core/orchestrator/`  
**Wiring:** Already integrated in `MasterOrchestrator.__init__` (lines 555-641)

### Purpose
- **Comprehension:** Refines user request into structured intent
- **Challenge Generation:** Detects disagreements via `ChallengeGenerator`
- **User Approval:** Displays DoR (Definition of Ready) for user confirmation

### Integration Points

| Component | How It's Used |
|-----------|---------------|
| `ConversationProtocol` | Manages multi-turn conversation state |
| `ChallengeGenerator` | Generates counter-proposals (disagreement detection) |
| `UnifiedIntelligenceProvider` | Gets quick-tier intelligence (<200ms) |
| `DoRApprovalGate` | Displays intent reflection + waits for "proceed" |

### When It Runs
- **EVERY operation** (IMPLEMENT/FIX/REFACTOR/ANALYZE/PLAN/DESIGN)
- Runs BEFORE intent classification
- Skipped ONLY in autonomous mode after approval

### Event Emissions
```
INTERACTION_STARTED → COMPREHENSION_COMPLETE → CHALLENGE_GENERATED (if any) → DOR_DISPLAYED
```

---

## 🧭 STAGE 2: Intent Router

**Orchestrator:** `IntentRouter`  
**Location:** `cortex/orchestrators/core/intent_router.py`  
**Wiring:** Initialized in `MasterOrchestrator.__init__` (line 648)

### Purpose
- **Intent Classification:** Parses user request → IMPLEMENT/FIX/REFACTOR/ANALYZE/PLAN/DESIGN
- **LENS Context Injection:** Auto-fetches LENS analysis for IMPLEMENT/FIX/REFACTOR/ANALYZE
- **Orchestrator Selection:** Routes to appropriate domain orchestrator

### Classification Rules

| Keywords | Intent | Target Orchestrator |
|----------|--------|---------------------|
| implement, add, create, build | IMPLEMENT | TDDOrchestrator |
| fix, bug, error, broken | FIX | TDDOrchestrator |
| refactor, improve, optimize | REFACTOR | RefactoringOrchestrator |
| analyze, review, assess | ANALYZE | LENSSynthesis (via UnifiedIntelligenceProvider) |
| plan, wave, phase | PLAN | PlanOrchestrator |
| design, architect, structure | DESIGN | InteractionOrchestrator (challenge mode) |

### LENS Auto-Fetch Logic

**Triggered automatically for these intents:**
- IMPLEMENT → Full LENS (AST + Git + Comments)
- FIX → Full LENS (to understand bug context)
- REFACTOR → Full LENS (to assess complexity)
- ANALYZE → Full LENS (primary analysis data)

**NOT triggered for:**
- PLAN → No code analysis needed
- DESIGN → Pre-implementation phase

### Event Emissions
```
INTENT_CLASSIFICATION_STARTED → LENS_CONTEXT_FETCHED (if applicable) → INTENT_ROUTED
```

---

## 🧠 STAGE 3: Intelligence Layer

**Provider:** `UnifiedIntelligenceProvider`  
**Location:** `cortex/intelligence/provider.py`  
**Wiring:** Singleton initialized in `MasterOrchestrator.__init__` (line 273)

### Purpose
- **LENS Analysis:** Code intelligence (AST, Git, Comments)
- **Knowledge Synthesis:** Merges company domains + CORTEX best practices
- **Context Assembly:** Builds `UnifiedIntelligenceContext` for execution

### Tiered Execution

| Tier | Latency | What's Included | When Used |
|------|---------|-----------------|-----------|
| **Quick** | <200ms | Cached core rules only | Stage 1 (Interaction) |
| **Targeted** | <2s | LENS + relevant YAMLs | IMPLEMENT/FIX/REFACTOR |
| **Full** | <10s | LENS + KG + Profiles + tier3 cross-domain | ANALYZE (deep analysis) |

### LENS Integration

**LENSOrchestrator** provides 4-phase analysis:

1. **Language:** Detects frameworks, languages, patterns
2. **Examination:** Complexity, test coverage, code quality
3. **Navigation:** Entry points, dependencies, call graph
4. **Synthesis:** Summary, recommendations, risks

**Exposed via MCP:** `cortex_lens_analyze(target, depth, operation)`

### Knowledge Synthesis Flow

```
UnifiedIntelligenceProvider.get_context()
    ↓
1. Get LENS Analysis (if file_path provided)
    - LENSOrchestrator.analyze_file()
    - Returns: {ast_analysis, git_history, comments}
    ↓
2. Get Company Knowledge
    - Loads: company/domains/{repo}/*.yaml
    - Precedence: OVERRIDE (company rules beat CORTEX)
    ↓
3. Get CORTEX Knowledge
    - Loads: cortex_brain/tier0-3/knowledge/*.yaml
    - Filters by intent (45+ best practices YAMLs)
    ↓
4. Synthesize via KnowledgeSynthesisEngine
    - Merges all sources
    - Generates: UnifiedIntelligenceContext
    - Includes: merged_rules, citations, violations, guidance
```

### Event Emissions
```
INTELLIGENCE_FETCH_STARTED → LENS_ANALYSIS_COMPLETE → KNOWLEDGE_SYNTHESIS_COMPLETE → CONTEXT_READY
```

---

## ⚙️ STAGE 4: Execution Layer

**Coordinator:** `MasterOrchestrator.execute_operation()`  
**Location:** `cortex/orchestrators/core/master_orchestrator.py`  
**Strategy:** Delegates to domain orchestrators based on intent

### Domain Orchestrators

| Orchestrator | Intent(s) | Purpose | MCP Tool |
|--------------|-----------|---------|----------|
| **TDDOrchestrator** | IMPLEMENT, FIX | RED→GREEN→REFACTOR cycle | `cortex_process_request` |
| **RefactoringOrchestrator** | REFACTOR | Safe code improvement | `cortex_process_request` |
| **PlanOrchestrator** | PLAN | Phase/wave management | `cortex_plan_setup`, `cortex_plan_resolve` |
| **LENSSynthesis** | ANALYZE | Code intelligence | `cortex_lens_analyze` |
| **EnforcementOrchestrator** | ALL (pre-exec) | Governance validation | N/A (internal) |
| **CoherenceValidator** | ALL (post-exec) | Post-edit validation | N/A (internal) |
| **UniversalLearningLoop** | ALL (post-exec) | Pattern capture | N/A (internal) |

### TDD Workflow (IMPLEMENT/FIX)

```
TDDOrchestrator.execute()
    ↓
1. RED: Write failing tests
    - TestValueScorer validates test quality
    - Ensure tests fail before implementation
    ↓
2. GREEN: Implement to pass tests
    - Write minimal code to pass
    - Re-run tests to verify
    ↓
3. REFACTOR: Clean up code
    - Improve design without changing behavior
    - Re-run tests to ensure no regression
    ↓
4. CoherenceValidator: Post-edit check
    - Verify no broken imports
    - Check file structure integrity
    ↓
5. UniversalLearningLoop: Capture patterns
    - Extract patterns from operation
    - Score confidence (0.0-1.0)
    - Promote high-value patterns to tier3
```

### Governance Integration

**EnforcementOrchestrator (7 agents):**

1. **GovernanceEnforcementAgent** — CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
2. **SecurityCheckpointAgent** — CORE-025 (git discipline), CORE-027 (audit trail)
3. **ComplianceValidationAgent** — Tier 1 domain rules
4. **FileNamingEnforcementAgent** — CORE-028 (kebab-case, no SCREAMING_CASE)
5. **IncrementalExecutionAgent** — CORE-001 (<500 LOC increments)
6. **MarkdownSuppressionAgent** — CORE-002 (no markdown file generation)
7. **ArchitectureIntegrityAgent** — CORE-035 (single canonical implementation)

**Runs:** BEFORE execution (pre-flight validation)  
**Performance:** <150ms validation time  
**Coverage:** 25/29 CORE rules (86%)

### Event Emissions
```
EXECUTION_STARTED → TDD_RED_COMPLETE → TDD_GREEN_COMPLETE → TDD_REFACTOR_COMPLETE → COHERENCE_VALIDATED → LEARNING_CAPTURED → OPERATION_COMPLETE
```

---

## 🔧 MCP Tool Mapping

**All operations exposed via MCP Server (localhost:9000)**

| MCP Tool | Orchestrator | Stage | Purpose |
|----------|--------------|-------|---------|
| `cortex_process_request` | TDDOrchestrator | Stage 4 | IMPLEMENT/FIX/REFACTOR operations |
| `cortex_lens_analyze` | LENSSynthesis | Stage 3/4 | Code intelligence analysis |
| `cortex_challenge` | ChallengeGenerator | Stage 1 | Generate counter-proposals |
| `cortex_plan_setup` | PlanOrchestrator | Stage 4 | Pre-implementation hook |
| `cortex_plan_resolve` | PlanOrchestrator | Stage 4 | Intelligent phase resolution |
| `cortex_plan_sync` | PlanOrchestrator | Stage 4 | Dashboard synchronization |
| `cortex_audit` | EnforcementOrchestrator | Stage 4 | Health scans |
| `cortex_total_recall` | RegistryIntelligenceAgent | Stage 3 | Feature discovery |
| `cortex_git_history` | LENSOrchestrator | Stage 3 | 24h git context |
| `cortex_detect_duplicates` | LENSOrchestrator | Stage 3/4 | CORE-035 violation detection |

---

## 📊 Event-Driven Communication

**All orchestrators communicate via `OrchestratorEventBus`**

### Event Flow Example

```
User: "implement authentication feature"
    ↓
EVENT: REQUEST_RECEIVED
    ↓
STAGE 1: InteractionOrchestrator
    EVENT: INTERACTION_STARTED
    EVENT: COMPREHENSION_COMPLETE
    EVENT: CHALLENGE_GENERATED (if any)
    EVENT: DOR_DISPLAYED
    ↓
STAGE 2: IntentRouter
    EVENT: INTENT_CLASSIFICATION_STARTED
    EVENT: LENS_CONTEXT_FETCHED
    EVENT: INTENT_ROUTED (intent=IMPLEMENT)
    ↓
STAGE 3: UnifiedIntelligenceProvider
    EVENT: INTELLIGENCE_FETCH_STARTED
    EVENT: LENS_ANALYSIS_COMPLETE
    EVENT: KNOWLEDGE_SYNTHESIS_COMPLETE
    EVENT: CONTEXT_READY
    ↓
STAGE 4: TDDOrchestrator
    EVENT: EXECUTION_STARTED
    EVENT: TDD_RED_COMPLETE (tests written)
    EVENT: TDD_GREEN_COMPLETE (tests passing)
    EVENT: TDD_REFACTOR_COMPLETE (code cleaned)
    EVENT: COHERENCE_VALIDATED
    EVENT: LEARNING_CAPTURED (patterns stored)
    EVENT: OPERATION_COMPLETE
```

### Audit Log Correlation

**Every event includes:**
- `correlation_id` — Unique per user request
- `timestamp` — ISO 8601 format
- `orchestrator` — Which orchestrator emitted
- `status` — SUCCESS/FAILED/WARNING
- `payload` — Event-specific data

**Used for:**
- E2E path verification (sunshine/rainy day)
- Debugging orchestrator interactions
- Performance analysis
- Learning pattern extraction

---

## 🌊 Workflow Runtime Integration (Future)

**When WorkflowRuntime is implemented (WAVE-V), it will:**

1. **Read this agent** to discover available orchestrators
2. **Compose workflows dynamically** using Stage 1-4 pipeline
3. **Inject RGR gates** based on file type:
   - `.py/.ts/.js` → RGR=YES (TDD enforced)
   - `.yaml/.json` → RGR=NO (config files)
   - `.md` → RGR=NO (docs)
4. **Use EventBus** for audit-verified E2E testing
5. **Leverage existing strategies:**
   - `PhaseExecutionStrategy` (sequential)
   - `WaveOrchestrationStrategy` (multi-phase)
   - `TrackParallelizationStrategy` (parallel)

---

## 🔒 Governance Rules

**CORE rules enforced across all stages:**

| Rule | Stage | Enforcement | Orchestrator |
|------|-------|-------------|--------------|
| CORE-008 (TDD) | Stage 4 | Pre-execution | EnforcementOrchestrator |
| CORE-011 (Type hints) | Stage 4 | Pre-execution | EnforcementOrchestrator |
| CORE-012 (Docstrings) | Stage 4 | Pre-execution | EnforcementOrchestrator |
| CORE-025 (Git discipline) | Stage 4 | Pre-execution | EnforcementOrchestrator |
| CORE-027 (Audit trail) | ALL | Post-execution | AuditLogger |
| CORE-028 (File naming) | Stage 4 | Pre-execution | EnforcementOrchestrator |
| CORE-035 (Single source) | Stage 3/4 | Runtime | LENSOrchestrator |
| CORE-049 (Silent exec) | ALL | Runtime | MasterOrchestrator |
| CORE-050 (MCP gate) | Stage 0 | Pre-flight | EnvironmentIntegrityAgent |

---

## 🎭 Mode-Specific Behavior

**This orchestration applies to BOTH modes:**

### ARCHITECT Mode (cortex-architect.prompt.md)
- **Context:** CORTEX internal development
- **Registry:** `cortex-registry/_cortex-master/`
- **Focus:** System self-improvement
- **Same orchestrators:** Uses identical Stage 1-4 pipeline

### PRODUCTION Mode (CORTEX.prompt.md)
- **Context:** User's production repository
- **Registry:** `cortex_brain/onboarded_repos/{repo}/`
- **Focus:** Feature implementation, bug fixes
- **Same orchestrators:** Uses identical Stage 1-4 pipeline

**Key Insight:** Only context changes (registry location), orchestration stays the same.

---

## 📋 Quick Reference

### "Which orchestrator handles my request?"

| User Says | Intent | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|-----------|--------|---------|---------|---------|---------|
| "implement auth" | IMPLEMENT | Interaction | IntentRouter | UnifiedIntelProvider | TDDOrchestrator |
| "fix this bug" | FIX | Interaction | IntentRouter | UnifiedIntelProvider | TDDOrchestrator |
| "refactor service" | REFACTOR | Interaction | IntentRouter | UnifiedIntelProvider | RefactoringOrchestrator |
| "analyze codebase" | ANALYZE | Interaction | IntentRouter | UnifiedIntelProvider | LENSSynthesis |
| "plan new feature" | PLAN | Interaction | IntentRouter | UnifiedIntelProvider | PlanOrchestrator |

### "When does LENS run?"

| Situation | LENS Execution | Tier |
|-----------|---------------|------|
| Stage 1 (Interaction) | YES (cached rules only) | Quick (<200ms) |
| IMPLEMENT intent | YES (full analysis) | Targeted (<2s) |
| FIX intent | YES (full analysis) | Targeted (<2s) |
| REFACTOR intent | YES (full analysis) | Targeted (<2s) |
| ANALYZE intent | YES (deep analysis) | Full (<10s) |
| PLAN intent | NO | N/A |
| DESIGN intent | NO | N/A |

### "Is InteractionOrchestrator always used?"

**YES.** Every operation starts with InteractionOrchestrator (Stage 1) for:
- Request comprehension
- Challenge generation (disagreement detection)
- DoR display + user approval

**Only skipped:** After user approval in silent autonomous mode (no re-confirmation needed).

---

## 🔗 Related Documentation

| Document | Purpose |
|----------|---------|
| `.github/prompts/cortex-architect.prompt.md` | ARCHITECT mode prompt (references this agent) |
| `.github/prompts/CORTEX.prompt.md` | PRODUCTION mode prompt (references this agent) |
| `.github/agents/core/CORTEX.md` | Master agent spec (complementary) |
| `cortex/orchestrators/core/master_orchestrator.py` | Implementation details |
| `cortex/intelligence/provider.py` | UnifiedIntelligenceProvider implementation |
| `cortex/orchestrators/core/intent_router.py` | IntentRouter implementation |
| `cortex/brain/core/orchestrator/` | InteractionOrchestrator implementation |

---

**Authority:** CORE-035 (Single Source of Truth)  
**Maintainer:** Asif Hussain  
**Status:** ✅ PRODUCTION ACTIVE

---

*This agent documents existing orchestration. No code changes required. Used by both prompts for consistent behavior.*
