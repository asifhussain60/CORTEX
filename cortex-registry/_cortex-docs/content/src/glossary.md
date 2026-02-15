# CORTEX Glossary# CORTEX Glossary



**Version:** 3.0.0 | **Updated:** 2026-02-14**A comprehensive reference for CORTEX-specific terminology**



This glossary defines key terms and concepts used throughout the CORTEX architecture documentation.**Terms:** 50+ | **Updated:** 2026-02-14 | **Audience:** Technical and non-technical users



------



## A## Quick Navigation



### AC Markers[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w)

**Definition:** Audit Commit markers used to track governance-gated work.

---

**Format:**

```python## A

# AC_START: AC-{CATEGORY}-{NNN}

# Description: {what and why}### AC Markers

# ... code ...**Definition:** Audit Compliance markers that track the start and completion of governance-gated work.

# AC_COMPLETE: AC-{CATEGORY}-{NNN} ✅ {N}/{N} tests passing

```**Format:** `AC_START: AC-{PHASE}-{ID}` and `AC_COMPLETE: AC-{PHASE}-{ID}`



**Purpose:** Ensures traceability and audit trail compliance.**Example:**

```python

**Related:** [Audit Trail](#audit-trail), [Governance](#governance)# AC_START: AC-PHASE48.0-001

# Description: Implement holistic validation gate

---class HolisticValidationGate:

    ...

### Architect Mode# AC_COMPLETE: AC-PHASE48.0-001 ✅ 15/15 passing

**Definition:** The operational mode used when working on the CORTEX repository itself (internal development).```



**Trigger:** Presence of `.cortex/`, `cortex-registry/`, or `cortex/__init__.py`**Related:** [Audit Trail](#audit-trail), [Governance](#governance)



**Prompt File:** `cortex-architect.prompt.md`---



**Header:** 🏛️ CORTEX Architect### Architect Mode

**Definition:** A CORTEX operational mode for system design and internal development. Uses `cortex-architect.prompt.md` and targets CORTEX repository enhancement.

**Related:** [Production Mode](#production-mode)

**When Used:** When developing CORTEX itself (detected by presence of `.cortex/` or `cortex-registry/` directories).

---

**Related:** [Production Mode](#production-mode), [HEXA-MODE](#hexa-mode)

### AST Analysis

**Definition:** Abstract Syntax Tree analysis for deep code structure understanding without execution.---



**Languages:** Python, C#, TypeScript, Java, JavaScript### AST Analysis

**Definition:** Abstract Syntax Tree analysis — parsing source code into a tree structure to understand code structure, complexity, and patterns without executing it.

**Related:** [LENS](#lens), [Static Analysis](#static-analysis)

**CORTEX Tool:** `cortex_ast_analyze`

---

**Related:** [LENS](#lens), [Static Analysis](#static-analysis)

### Audit Trail

**Definition:** Comprehensive logging of all governance decisions, violations, and actions.---



**Storage:** `cortex_brain/governance.db` (SQLite)### Audit Trail

**Definition:** A complete record of all governance-gated operations, tracked via AC markers and logged for compliance verification.

**Components:** AC markers, timestamps, orchestrator decisions, enforcement actions

**Rule:** CORE-027

**Related:** [AC Markers](#ac-markers), [Governance](#governance)

**Related:** [AC Markers](#ac-markers), [Governance](#governance)

---

---

## C

## B

### Challenge Gate

**Definition:** Mandatory design review step that presents alternative approaches before implementation.### Brain (CORTEX Brain)

**Definition:** The knowledge storage layer of CORTEX, organized in tiers from most permanent (tier0) to most volatile (tier3).

**Purpose:** Ensure best solution is chosen, not just first solution

**Structure:**

**Format:**- `tier0/` — Immutable principles, CORE rules

- **Your Approach:** Pros/Cons/ROI- `tier1/` — Stable knowledge, best practices

- **Alternative A:** Pros/Cons/ROI  - `tier2/` — Session context, recent learnings

- **Decision Required:** User must choose or provide reason to override- `tier3/` — Volatile state, temporary caches



**Rule:** Part of Holistic Validation Gate**Location:** `cortex_brain/`



**Related:** [Holistic Validation](#holistic-validation-gate), [CORE-048](#core-rules)**Related:** [Knowledge Tiers](#knowledge-tiers), [Domain Brain](#domain-brain)



------



### Consolidated Tools### Brain Analogy

**Definition:** The reorganized MCP tool structure grouping related operations under parent tools.**Definition:** CORTEX documentation uses human brain analogies to explain technical concepts. Orchestrators are like brain regions, MCP is the nervous system, LENS is the visual processor, etc.



**Before:** 86 flat tools  **Purpose:** Makes complex architecture accessible to non-technical users.

**After:** 26 parent tools with 90+ operations

---

**Example:** `cortex_process_request` with operations: implement, fix, refactor, test

## C

**Related:** [MCP](#mcp-model-context-protocol)

### CCL (Context Crystallization Layer)

---**Definition:** Current enhancement that pre-warms context asynchronously before request processing, reducing Stage 2 latency by ~15%.



### Context Crystallization Layer (CCL)**Process:**

**Definition:** Async context pre-warming system that loads rules, LENS state, and infrastructure before request processing.1. Async load rules cache (company > tier1 > tier0)

2. Warm LENS (AST, git, comments)

**Performance:** 3. Detect infrastructure

- **Target SLA:** 300ms normal, 500ms fallback4. Merge into request processing

- **Cache hit rate:** 70%+ target

- **Latency improvement:** -15% Stage 2 latency**SLA:** 300ms target, 500ms fallback max



**Timeout Behavior:****Related:** [Current](#phases), [LENS](#lens)

- ≤300ms: Full context merged into Stage 2

- 300-500ms: Partial context (rules only)---

- 500-1000ms: Minimal context, fresh fetch

- >1000ms: Skip CCL, fresh fetch (no penalty)### Challenge Gate

**Definition:** A mandatory design review checkpoint where CORTEX presents counter-proposals and alternative approaches before implementation.

**Related:** [Holistic Validation Gate](#holistic-validation-gate)

**Part of:** CORE-048 (Holistic Validation Gate)

---

**Output:** Agreement/disagreement, confidence score, counter-proposal if applicable.

### CORE Rules

**Definition:** The fundamental governance rules that govern all CORTEX operations.**Related:** [DoR](#dor), [Holistic Validation](#holistic-validation)



**Count:** 50+ rules total---



**Tiers:**### CORE Rules

- **Tier 0:** Immutable rules (cannot be overridden)**Definition:** The 30+ immutable governance rules that enforce quality, security, and consistency across CORTEX operations.

- **Tier 1:** Standard rules (minor exceptions allowed)

- **Tier 2:** Best practices (context-dependent)**Format:** CORE-{NNN}



**Key Examples:****Key Rules:**

- CORE-002: No markdown file generation in chat responses- CORE-002: No markdown file generation (inline only)

- CORE-008: TDD mandatory (tests before code)- CORE-008: TDD mandatory (tests before code)

- CORE-035: Single canonical implementation (no duplicates)- CORE-011: Type hints mandatory

- CORE-048: Holistic Validation Gate- CORE-035: Single canonical implementation (no duplicates)

- CORE-049: Silent Autonomous Execution

- CORE-050: MCP Circuit Breaker**Location:** `cortex-registry/registry/governance/core-rules.yaml`

- CORE-051: Cross-Platform MCP

- CORE-052: Single Branch Policy**Related:** [Governance](#governance), [Tier 0 Rules](#tier-0-rules)



**Location:** `cortex-registry/governance/core-rules.yaml`---



**Related:** [Governance](#governance), [Enforcement](#enforcement-orchestrator)### Consolidated Tools

**Definition:** The Consolidation reorganization that grouped 86+ flat MCP tools into 26 parent tools with multiple operations each.

---

**Example:** Instead of `cortex_lens_analyze`, `cortex_lens_diff`, `cortex_lens_validate` (3 tools), there's `cortex_lens` (1 tool with 3 operations).

## D

**Complete Tool List (26):**

### Deprecated Orchestrators`cortex_process_request`, `cortex_challenge`, `cortex_classify`, `cortex_request_lifecycle`, `cortex_lens`, `cortex_knowledge`, `cortex_git`, `cortex_governance`, `cortex_validate`, `cortex_load`, `cortex_validate_request`, `cortex_debug`, `cortex_refactor`, `cortex_plan`, `cortex_onboard`, `cortex_dashboard`, `cortex_generate_tests`, `cortex_verify`, `cortex_ask`, `cortex_vacuum`, `cortex_tools_catalog`, `cortex_total_recall`, `cortex_metrics`, `cortex_check`, `cortex_vision`, `cortex_orchestrator`

**Definition:** Orchestrators that have been consolidated into unified orchestrators and are scheduled for removal.

**Benefits:** Cognitive clarity, easier discovery, consistent patterns.

**Count:** 7 total

**Related:** [MCP](#mcp), [Consolidation](#current)

**Sunset Date:** 2026-03-31

---

**List:**

- LENSOrchestrator → UnifiedAnalysisOrchestrator## D

- ToolDiscoveryOrchestrator → UnifiedAnalysisOrchestrator

- DocumentationOrchestrator → UnifiedDiscoveryOrchestrator### DoR (Definition of Ready)

- ChallengeEngine → UnifiedQualityAssuranceOrchestrator**Definition:** The classification table shown before any implementation, confirming intent, handler, confidence, scope, and impact.

- OnboardingOrchestrator → UnifiedOnboardingOrchestrator

- EducationalOrchestrator → UnifiedDiscoveryOrchestrator**Format:**

- RecommendationGate → IntelligenceOrchestrator| Field | Value |

|-------|-------|

**Related:** [Unified Orchestrators](#unified-orchestrators), [Sunset Date](#sunset-date)| Intent | IMPLEMENT |

| Handler | TDDOrchestrator |

---| Confidence | 🟢 95% |

| Scope | cortex/mcp/ |

### DoR (Definition of Ready)| Impact | 🟡 Medium |

**Definition:** The intent classification table displayed before execution begins.

**Rule:** CORE-029

**Format:** Markdown table showing:

- Detected intent (IMPLEMENT, FIX, REFACTOR, etc.)**Related:** [Intent Router](#intent-router), [Challenge Gate](#challenge-gate)

- Confidence score

- Target orchestrator---

- Required context

### Domain Brain

**Purpose:** Transparency and user confirmation before proceeding**Definition:** Company-specific knowledge loaded from `company/domains/` that takes precedence over CORTEX's built-in best practices.



**Related:** [Intent Classification](#intent-classification), [Response Header](#response-header)**Priority:** Company knowledge > CORTEX knowledge



---**Related:** [Brain](#brain-cortex-brain), [Knowledge Layering](#knowledge-layering)



## E---



### Enforcement Orchestrator## E

**Definition:** Core orchestrator (Priority 50) that coordinates 8 enforcement agents for pre-execution governance validation.

### Enforcement Orchestrator

**Agents:****Definition:** The 8-agent pre-execution gate that validates all IMPLEMENT/FIX/REFACTOR requests against governance rules.

1. GovernanceEnforcementAgent

2. SecurityCheckpointAgent**Agents:**

3. ComplianceValidationAgent1. GovernanceEnforcementAgent (CORE-008, 011, 012, 013, 029, 030)

4. FileNamingEnforcementAgent2. SecurityCheckpointAgent (CORE-025, 026, 027)

5. IncrementalExecutionAgent3. ComplianceValidationAgent (Tier 1 rules)

6. MarkdownSuppressionAgent4. FileNamingEnforcementAgent (CORE-028)

7. ArchitectureIntegrityAgent5. IncrementalExecutionAgent (CORE-001, 004)

8. EnvironmentIntegrityAgent6. MarkdownSuppressionAgent (CORE-002)

7. ArchitectureIntegrityAgent (CORE-017-020, 032, 034, 035, 038-041)

**Coverage:** 26/30 CORE rules automated (87%)8. EnvironmentIntegrityAgent (MCP validation, Python version, venv checks)



**Performance:** <150ms validation time**Coverage:** 87% of CORE rules automated



**Related:** [CORE Rules](#core-rules), [Pre-Execution Gate](#pre-execution-gate)**Related:** [Governance](#governance), [Pre-Execution Gate](#pre-execution-gate)



------



## G## G



### Governance### Governance

**Definition:** The comprehensive system of rules, enforcement agents, and audit trails that ensure code quality and compliance.**Definition:** The 4-layer defense system that ensures quality, security, and compliance across all CORTEX operations.



**Components:****Layers:**

- 50+ CORE rules1. Pre-Execution Gate (blocks violations)

- 8 enforcement agents2. Runtime Monitor (stops at 3+ violations)

- Pre-execution validation gate3. Post-Execution Audit (detects bypasses)

- Post-execution audit trail4. Production Gate (prevents broken deployment)

- 4-layer defense system

**Related:** [CORE Rules](#core-rules), [Enforcement Orchestrator](#enforcement-orchestrator)

**Related:** [CORE Rules](#core-rules), [Enforcement Orchestrator](#enforcement-orchestrator)

---

---

## H

## H

### HEXA-MODE

### Holistic Validation Gate**Definition:** The 6 operational modes of CORTEX Architect: PRE-FLIGHT, AUDIT, META-AUDIT, DIGEST, PLAN, and DESIGN.

**Definition:** Pre-implementation validation system that runs comprehensive checks before any code generation.

**Trigger:** Auto-detected based on request keywords and file types.

**Steps:**

1. Registry consistency check**Related:** [Architect Mode](#architect-mode), [DIGEST](#digest)

2. Context pre-warming (async)

3. Dependency graph analysis---

4. Regression risk scoring (0.0-1.0)

5. Architecture drift detection### Holistic Validation

6. **Mandatory Challenge Gate** (alternatives)**Definition:** Current enhancement that runs comprehensive pre-implementation checks including registry validation, dependency analysis, risk scoring, and mandatory Challenge Gate.

7. CORTEX self-analysis (CORTEX repo only)

**Rule:** CORE-048

**Verdicts:**

- **PASS** (<0.4): Proceed normally**Related:** [Challenge Gate](#challenge-gate), [Pre-Execution Gate](#pre-execution-gate)

- **WARN** (0.4-0.7): Proceed with caution

- **BLOCK** (>0.7): User override required---



**MCP Tool:** `cortex_validate_holistically`## I



**Related:** [Challenge Gate](#challenge-gate), [Context Crystallization Layer](#context-crystallization-layer-ccl)### Incremental Execution

**Definition:** The requirement that all tasks stay ≤500 lines of code per commit with automatic subtask decomposition.

---

**Rule:** CORE-001

## I

**Process:** Large tasks → IncrementalTaskDecomposer → Subtasks (10K tokens each) → Sequential execution

### Incremental Execution

**Definition:** The practice of breaking work into small, deliverable chunks (≤500 LOC per commit).**Related:** [Token Budget](#token-budget), [TDD](#tdd)



**Rule:** CORE-001---



**Enforced by:** IncrementalExecutionAgent### Intent Router

**Definition:** The orchestrator that classifies user requests into intents (IMPLEMENT, FIX, REFACTOR, ANALYZE, etc.) and routes to appropriate handlers.

**Purpose:** Maintainable commits, easier code review, rollback safety

**Output:** Intent type, target orchestrator, confidence score.

**Related:** [Token Budget](#token-budget)

**Related:** [DoR](#dor), [Master Orchestrator](#master-orchestrator)

---

---

### Intent Classification

**Definition:** The process of analyzing user requests and routing them to the appropriate orchestrator.## K



**Orchestrator:** IntentRouter (Priority 20)### Knowledge Layering

**Definition:** The priority system for loading knowledge: Company standards (highest) → CORTEX best practices → Language defaults.

**Supported Intents:**

- IMPLEMENT, FIX, REFACTOR, ANALYZE, TEST, ONBOARD, PLAN, QUERY, CONVERSATION, WORKFLOW, QUALITY, UNKNOWN**Priority:** `company/domains/` > `cortex/knowledge/best-practices/`



**Accuracy:** 96.2%**Related:** [Domain Brain](#domain-brain), [Brain](#brain-cortex-brain)



**Latency:** ~15ms---



**Related:** [Intent Router](#intent-router), [DoR](#dor-definition-of-ready)### Knowledge Tiers

**Definition:** The 4-tier organization of CORTEX Brain knowledge by volatility.

---

| Tier | Content | Volatility |

### Intent Router|------|---------|------------|

**Definition:** Core orchestrator (Priority 20) that classifies user requests and routes them to specialist orchestrators.| tier0 | CORE rules, principles | Immutable |

| tier1 | Best practices, patterns | Stable |

**Real-World Analogy:** Airport security checkpoint routing passengers to correct terminals| tier2 | Session context | Session-scoped |

| tier3 | Caches, temporary state | Volatile |

**Routing Factors:**

- Keywords (30%)**Related:** [Brain](#brain-cortex-brain)

- LENS context (25%)

- Knowledge base (20%)---

- Historical accuracy (15%)

- Request clarity (10%)## L



**Related:** [Intent Classification](#intent-classification)### LENS

**Definition:** **L**anguage **E**xamination **N**avigation **S**ynthesis — CORTEX's unified code intelligence protocol.

---

**Process:**

## L1. **L**anguage: Detect language and framework

2. **E**xamination: AST parsing, complexity analysis

### LENS3. **N**avigation: Cross-file relationships, call graphs

**Definition:** **L**anguage **E**xamination, **N**avigation, and **S**ynthesis — the unified code intelligence system.4. **S**ynthesis: Merge findings into actionable insights



**Components:** 10 specialized analyzers**Tools:** `cortex_lens_analyze`, `cortex_lens_deep_analyze`



**Orchestrator:** LENSSynthesis (Priority 40)**Related:** [AST Analysis](#ast-analysis), [Static Analysis](#static-analysis)



**Analyzers:**---

1. AST Analyzer

2. Git History Analyzer## M

3. Comment Analyzer

4. Configuration Analyzer### Master Orchestrator

5. Database Analyzer**Definition:** The primary entry point orchestrator that receives all requests and coordinates with specialized orchestrators.

6. Dependency Analyzer

7. API Contract Analyzer**Role:** Like the executive center — executive function, decision-making, coordination.

8. Polyglot Detector

9. Plugin System**Related:** [Orchestrator](#orchestrator), [Intent Router](#intent-router)

10. Language Adapters

---

**Languages:** Python, C#, TypeScript, Java, JavaScript

### MCP (Model Context Protocol)

**Related:** [AST Analysis](#ast-analysis), [Static Analysis](#static-analysis)**Definition:** The standardized communication layer (JSON-RPC 2.0) that connects AI assistants (Copilot, Claude, Cursor) to CORTEX orchestrators.



---**Analogy:** CORTEX's nervous system.



## M**Tools:** 26 consolidated tools with 90+ operations.



### Master Orchestrator**Related:** [Consolidated Tools](#consolidated-tools), [Pylance-Style MCP](#pylance-style-mcp)

**Definition:** The top-level orchestrator (Priority 10) that coordinates all other orchestrators and manages request lifecycle.

---

**Real-World Analogy:** Executive director coordinating department managers

### MCP-FIRST

**Responsibilities:****Definition:** The architectural principle that ALL CORTEX functionality must be exposed via MCP tools. Direct Python imports are forbidden in production.

- Request lifecycle management

- Orchestrator coordination**Why:** Ensures consistent governance, audit trails, and client compatibility.

- Context synthesis

- Error handling**Related:** [MCP](#mcp-model-context-protocol)

- Audit logging

---

**Related:** [Orchestrator](#orchestrator)

## O

---

### Orchestrator

### MCP (Model Context Protocol)**Definition:** A specialized component that handles a specific domain of CORTEX functionality.

**Definition:** The API protocol through which all CORTEX functionality is exposed.

**Count:** 14 active + 4 super-orchestrators + 7 deprecated (21 total as of 2026-02-14)

**Architecture:** Auto-starting server (Pylance-style) — no manual startup required

**Examples:**

**Tools:** 26 consolidated parent tools with 90+ operations- `TDDOrchestrator` — Test-driven development workflow

- `LENSSynthesis` — Code intelligence analysis

**Port:** localhost:9000 (development)- `EnforcementOrchestrator` — Governance validation



**Protocol:** JSON-RPC 2.0 over stdio**Related:** [Master Orchestrator](#master-orchestrator), [Unified Orchestrators](#unified-orchestrators)



**Related:** [Consolidated Tools](#consolidated-tools), [Pylance-Style MCP](#pylance-style-mcp)---



---## P



### MCP-First### Pre-Execution Gate

**Definition:** The architectural principle that ALL CORTEX functionality must be exposed through MCP tools (no direct file operations).**Definition:** The first layer of governance that validates requests before any code is generated or modified.



**Rule:** Enforced by MCP Gate and EnvironmentIntegrityAgent**Enforcement:** BLOCKS violations (no partial execution)



**Exceptions:** Read-only operations (semantic_search, read_file, etc.)**Related:** [Enforcement Orchestrator](#enforcement-orchestrator), [Governance](#governance)



**Forbidden:** Direct file creation/modification for IMPLEMENT/FIX/REFACTOR intents---



**Related:** [MCP](#mcp-model-context-protocol)### Production Mode

**Definition:** The standard operational mode for user repositories. Uses `CORTEX.prompt.md` and targets user domain implementation.

---

**When Used:** When working on non-CORTEX repositories.

## O

**Related:** [Architect Mode](#architect-mode)

### Orchestrator

**Definition:** A specialized processing component that handles a specific category of requests or capabilities.---



**Count:** 21 active (8 core + 5 domain + 4 super + 4 infrastructure)### Pylance-Style MCP

**Definition:** Auto-starting MCP architecture where the server activates when tools are invoked (no manual startup required), similar to how Pylance language server works in VS Code.

**Contract:** Defined in `__wiring_contract__.yaml`

**Benefits:** Zero setup friction, on-demand lifecycle, automatic error recovery.

**Registration:** Git-backed registry with priority-based routing

**Related:** [MCP](#mcp-model-context-protocol)

**Related:** [Master Orchestrator](#master-orchestrator), [Orchestrator Registry](#orchestrator-registry)

---

---

## R

### Orchestrator Registry

**Definition:** The comprehensive catalog of all orchestrators, their capabilities, priorities, and relationships.### Response Header

**Definition:** The mandatory header that begins every CORTEX response.

**Location:** `cortex/wiring/specifications/` and `cortex-registry/`

**Format:**

**Format:** YAML with validation schema```markdown

## 🧠 CORTEX {operation}

**Validation:** ContractValidator (Priority 3) enforces 4-layer validation**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅



**Related:** [Orchestrator](#orchestrator)---

```

---

**Rule:** CORE-029

## P

**Related:** [DoR](#dor)

### Pre-Execution Gate

**Definition:** The first layer of governance that validates requests before any code is generated or modified.---



**Enforcement:** BLOCKS violations (no partial execution)## S



**Components:** EnforcementOrchestrator (8 agents) + Holistic Validation Gate### Silent Autonomous Execution

**Definition:** The default execution mode where CORTEX proceeds without narration, showing only progress bars and completion reports.

**Related:** [Enforcement Orchestrator](#enforcement-orchestrator), [Holistic Validation Gate](#holistic-validation-gate)

**Trigger Words:** "proceed", "implement", "continue", "yes"

---

**Rule:** CORE-049

### Production Mode

**Definition:** The standard operational mode for user repositories. Uses `CORTEX.prompt.md` and targets user domain implementation.**Format:** ASCII progress bars only (no text descriptions)



**When Used:** When working on non-CORTEX repositories.**Related:** [Progress Bars](#progress-bars)



**Header:** 🧠 CORTEX---



**Related:** [Architect Mode](#architect-mode)### Static Analysis

**Definition:** Code analysis without execution — examining source code for patterns, complexity, potential bugs, and style issues.

---

**Related:** [AST Analysis](#ast-analysis), [LENS](#lens)

### Progress Bars

**Definition:** ASCII-based visual feedback used during silent autonomous execution.---



**Format:** `` `██████████░░░░░` 70% Complete ``### Sunset Date

**Definition:** The deadline after which deprecated components will be removed.

**Purpose:** Visual progress indication without narration

**Current:** 2026-03-31 (for consolidated orchestrators)

**Rule:** Part of CORE-049 (Silent Autonomous Execution)

**Related:** [Deprecated Orchestrators](#deprecated-orchestrators), [Unified Orchestrators](#unified-orchestrators)

**Related:** [Silent Autonomous Execution](#silent-autonomous-execution)

---

---

## T

### Pylance-Style MCP

**Definition:** Auto-starting MCP architecture where the server activates when tools are invoked (no manual startup required), similar to how Pylance language server works in VS Code.### TDD (Test-Driven Development)

**Definition:** The mandatory development workflow: write tests first (RED), implement to pass (GREEN), then refactor.

**Benefits:** Zero setup friction, on-demand lifecycle, automatic error recovery.

**Rule:** CORE-008

**Implementation:** VS Code auto-starts MCP server on first tool invocation

**Process:** RED → GREEN → REFACTOR

**Related:** [MCP](#mcp-model-context-protocol)

**Related:** [TDD Orchestrator](#tdd-orchestrator)

---

---

## R

### TDD Orchestrator

### Response Header**Definition:** The orchestrator that enforces test-first development workflow for all IMPLEMENT/FIX intents.

**Definition:** The mandatory header that begins every CORTEX response.

**Related:** [TDD](#tdd-test-driven-development)

**Format:**

```markdown---

## 🧠 CORTEX {operation}

**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅### Tier 0 Rules

**Definition:** The immutable subset of CORE rules that cannot be overridden under any circumstances.

---

```**Examples:** CORE-002 (no markdown), CORE-008 (TDD), CORE-035 (no duplicates)



**Rule:** CORE-029**Related:** [CORE Rules](#core-rules)



**Variants:**---

- Production: 🧠 CORTEX

- Architect: 🏛️ CORTEX Architect### Token Budget

**Definition:** The constraint on context size (≤200K tokens) and per-turn context (≤20K) to prevent runaway costs and context overflow.

**Related:** [DoR](#dor-definition-of-ready)

**Related:** [Incremental Execution](#incremental-execution)

---

---

## S

## U

### Silent Autonomous Execution

**Definition:** The default execution mode where CORTEX proceeds without narration, showing only progress bars and completion reports.### Unified Orchestrators

**Definition:** The 4 consolidated orchestrators that replace multiple deprecated orchestrators.

**Trigger Words:** "proceed", "implement", "continue", "yes"

**List:**

**Rule:** CORE-0491. `UnifiedOnboardingOrchestrator`

2. `UnifiedAnalysisOrchestrator`

**Allowed Output:**3. `UnifiedQualityAssuranceOrchestrator`

- ASCII progress bars4. `UnifiedDiscoveryOrchestrator`

- Test counts and coverage

- Completion summary**Impact:** 37% reduction (27 → 21 active orchestrators including super-orchestrators)

- Error messages (if blocked)

**Related:** [Orchestrator](#orchestrator), [Super-Orchestrators](#super-orchestrators)

**Forbidden Output:**

- "I'm now creating..." narration---

- "Shall I proceed?" prompts

- Step-by-step descriptions## W

- Mid-execution status updates

### Workspace

**Related:** [Progress Bars](#progress-bars)**Definition:** A VS Code workspace folder where CORTEX operates, containing user code and CORTEX configuration.



---**Related:** [Repository](#repository)



### Static Analysis---

**Definition:** Code analysis without execution — examining source code for patterns, complexity, potential bugs, and style issues.

## See Also

**Related:** [AST Analysis](#ast-analysis), [LENS](#lens)

- [CORTEX Architecture Index](./index.md)

---- [MCP Tools Catalog](./mcp/tools-catalog.md)

- [Governance Compliance](./capabilities/governance-compliance.md)

### Sunset Date- [Orchestration Overview](./orchestration/overview.md)

**Definition:** The deadline after which deprecated components will be removed.

---

**Current:** 2026-03-31 (for consolidated orchestrators)

**Last Updated:** 2026-02-14

**Affects:** 7 deprecated orchestrators

**Related:** [Deprecated Orchestrators](#deprecated-orchestrators), [Unified Orchestrators](#unified-orchestrators)

---

### Super-Orchestrators
**Definition:** Advanced orchestrators that manage consolidated subsystems (3-6 components each).

**Count:** 4 total

**List:**
1. StateOrchestrator (Priority 180) — Memory & context management
2. ObservabilityOrchestrator (Priority 185) — System monitoring
3. IntelligenceOrchestrator (Priority 190) — Pattern recognition & learning
4. SOLIDOrchestrator (Priority 195) — Architectural integrity

**Purpose:** Provide advanced capabilities through unified coordination

**Related:** [Orchestrator](#orchestrator)

---

## T

### TDD (Test-Driven Development)
**Definition:** The mandatory development workflow: write tests first (RED), implement to pass (GREEN), then refactor.

**Rule:** CORE-008

**Process:** RED → GREEN → REFACTOR

**Enforced by:** TDDOrchestrator (Priority 55)

**No Exceptions:** Cannot skip tests, use `--ignore`, or rename test files

**Related:** [TDD Orchestrator](#tdd-orchestrator)

---

### TDD Orchestrator
**Definition:** Domain orchestrator (Priority 55) that enforces test-first development workflow for all IMPLEMENT/FIX intents.

**Workflow:**
1. **RED:** Generate failing test
2. **GREEN:** Implement minimal code to pass
3. **REFACTOR:** Improve structure while maintaining tests

**Related:** [TDD](#tdd-test-driven-development)

---

### Tier 0 Rules
**Definition:** The immutable subset of CORE rules that cannot be overridden under any circumstances.

**Examples:** CORE-002 (no markdown), CORE-008 (TDD), CORE-035 (no duplicates), CORE-049 (silent execution), CORE-050 (MCP gate)

**Count:** 9 immutable rules

**Related:** [CORE Rules](#core-rules)

---

### Token Budget
**Definition:** The constraint on context size (≤200K tokens) and per-turn context (≤20K) to prevent runaway costs and context overflow.

**Enforcement:** IncrementalExecutionAgent monitors token usage

**Continuation Protocol:** At 75% usage, generate continuation prompt and commit

**Related:** [Incremental Execution](#incremental-execution)

---

## U

### Unified Orchestrators
**Definition:** The 4 consolidated orchestrators that replace multiple deprecated orchestrators.

**List:**
1. `UnifiedOnboardingOrchestrator` (Priority 100)
2. `UnifiedAnalysisOrchestrator` (Priority 115)
3. `UnifiedQualityAssuranceOrchestrator` (Priority 120)
4. `UnifiedDiscoveryOrchestrator` (Priority 125)

**Impact:** 37% reduction (27 → 21 active orchestrators including super-orchestrators)

**Related:** [Orchestrator](#orchestrator), [Super-Orchestrators](#super-orchestrators)

---

## W

### Workspace
**Definition:** A VS Code workspace folder where CORTEX operates, containing user code and CORTEX configuration.

**Markers:**
- `.cortex/` — CORTEX internal files
- `cortex-registry/` — Configuration and governance
- `.vscode/settings.json` — MCP configuration (not in git)

**Related:** [Repository](#repository)

---

## See Also

- [CORTEX Architecture Index](./index.md)
- [Capabilities Overview](./capabilities/overview.md)
- [Orchestration Overview](./orchestration/overview.md)
- [LENS Overview](./lens/overview.md)
- [MCP Overview](./mcp/overview.md)

---

*Generated by CORTEX Architecture Team | Updated 2026-02-14*
