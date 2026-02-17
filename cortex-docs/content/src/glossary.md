# CORTEX Glossary

---
title: CORTEX Architecture Glossary  
type: reference  
audience: [Business Leaders, Product Owners, Software Developers]  
word_count: 1600  
last_verified: 2026-02-16  
source_of_truth: cortex/ + cortex-registry/ + .github/  
format: diátaxis-reference  
voice: third-person-neutral  
terms_count: 58  
alphabetical: true  
---

> **Notice:** Terminology definitions represent CORTEX system concepts as of February 2026. Terms may evolve as the platform matures. This glossary serves as a reference for understanding architecture documentation, code comments, and system operations.

---

## Overview

This glossary defines 58 key terms and concepts used throughout CORTEX architecture documentation (updated Feb 2026 with recent enhancements). Organizations benefit from understanding this terminology for effective communication with development teams, architecture reviews, and strategic planning discussions [Business Leaders]. Product teams use these definitions when planning features, reviewing technical proposals, and coordinating with engineering [Product Owners]. Developers reference this glossary for consistent vocabulary in code documentation, pull requests, and technical discussions [Software Developers].

**Glossary Organization:**
- **Alphabetical Index** — All terms organized A-Z for quick lookup
- **Category Tags** — Terms tagged by domain (Orchestration, Governance, Intelligence, Infrastructure, MCP)
- **Cross-References** — Related terms linked for contextual exploration
- **Examples** — Code snippets or usage examples where applicable

**Quick Navigation:**  
[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [L](#l) · [M](#m) · [O](#o) · [P](#p) · [R](#r) · [S](#s) · [T](#t) · [W](#w)

---

## A

### AC Markers

**Category:** Governance | **Full Name:** Audit Compliance Markers

**Definition:** Comment-based markers that track the start and completion of governance-gated development work. AC markers create an immutable audit trail in source code linking commits to specific governance requirements, enabling traceability for compliance reviews and quality audits.

**Format:**
```python
# AC_START: AC-{CATEGORY}-{ID}
# Description: {what is being implemented and why}
# ... implementation code ...
# AC_COMPLETE: AC-{CATEGORY}-{ID} ✅ {passed}/{total} tests passing
```

**Example:**
```python
# AC_START: AC-PHASE48-001
# Description: Holistic validation gate for pre-execution checks
class HolisticValidationGate:
    def validate(self, context: RequestContext) -> ValidationResult:
        # Implementation with multi-factor analysis
        pass
# AC_COMPLETE: AC-PHASE48-001 ✅ 18/18 tests passing
```

**Usage Context:** Required for all IMPLEMENT, FIX, and REFACTOR operations. EnforcementOrchestrator validates AC marker presence during post-execution audit (Layer 3). Missing markers trigger governance violations (CORE-027).

**Related:** [Audit Trail](#audit-trail), [Governance](#governance), [CORE Rules](#core-rules)

---

### Architect Mode

**Category:** Operational Mode | **Full Name:** CORTEX Architect Development Mode

**Definition:** An operational mode activated when developing the CORTEX platform itself (internal system development). Uses specialized prompt file (`cortex-architect.prompt.md`) and provides access to CORTEX-internal context including registry structure, wiring specifications, and phase definitions.

**Detection Logic:** Mode activates when repository contains `.cortex/` directory, `cortex-registry/` directory, or `cortex/__init__.py` file.

**Header Format:** `🏛️ CORTEX Architect {MODE}` (e.g., "🏛️ CORTEX Architect IMPLEMENT")

**Differences from Production Mode:**
- **Context Loading:** CORTEX-internal specifications (registry, wiring, phases) vs user domain knowledge
- **Prompt File:** `cortex-architect.prompt.md` vs `CORTEX.prompt.md`
- **Header Icon:** 🏛️ (building) vs 🧠 (brain)
- **Purpose:** Build/enhance CORTEX system vs implement user features

**Orchestrators:** Same orchestration layer (MasterOrchestrator, TDDOrchestrator, etc.) — only context differs.

**Related:** [Production Mode](#production-mode), [Intelligent Prompt Routing](#intelligent-prompt-routing)

---

### AST Analysis

**Category:** Intelligence | **Full Name:** Abstract Syntax Tree Analysis

**Definition:** Static code analysis technique that parses source code into a hierarchical tree structure representing syntactic elements (functions, classes, methods, variables, control flow). CORTEX uses tree-sitter for multi-language AST generation, enabling code intelligence without code execution.

**Supported Languages:** Python, TypeScript, JavaScript, C#, Java, Go (via tree-sitter parsers)

**What AST Provides:**
- **Structure:** Functions, classes, methods, parameters, return types
- **Complexity:** Cyclomatic complexity, nesting depth, branching factor
- **Patterns:** Design pattern detection (Singleton, Factory, Observer)
- **Metrics:** Lines of code, comment density, maintainability index

**Performance:** AST parsing completes in 50-150ms for typical files (100-500 LOC). Results cached in SQLite with 60-70% cache hit rate.

**LENS Integration:** AST Analyzer is Phase 1 (Language) component executing in parallel with Git History and Comment analyzers.

**Related:** [LENS](#lens), [Code Intelligence](#code-intelligence), [Static Analysis](#static-analysis)

---

### Audit Trail

**Category:** Governance | **Full Name:** Governance Audit Trail

**Definition:** Comprehensive record of all governance-gated operations tracked via AC markers, timestamps, orchestrator decisions, and enforcement actions. Enables compliance verification, quality audits, and post-incident analysis.

**Storage:** `cortex_intelligence/governance.db` (SQLite database) with indexed queries for fast retrieval

**Components:**
- **AC Markers:** Start/complete timestamps with test results
- **Orchestrator Decisions:** Intent classification, routing paths, validation results
- **Enforcement Actions:** Violations detected, rules triggered, blocking decisions
- **Performance Metrics:** Request duration, validation latency, test execution time

**Retention:** Tier 2 knowledge (session-scoped, 7-day default retention, configurable per deployment)

**Rule Enforcement:** CORE-027 mandates audit trail for all governance-gated work

**Related:** [AC Markers](#ac-markers), [Governance](#governance), [CORE Rules](#core-rules)

---

## B

### Brain (CORTEX Brain)

**Category:** Architecture | **Full Name:** CORTEX Knowledge Storage Layer

**Definition:** Tiered knowledge storage system organizing information by permanence and volatility. Provides the "memory" layer for orchestrators, agents, and intelligence systems to store and retrieve context across sessions.

**Tier Structure:**
- **Tier 0:** Immutable principles, CORE rules, security mandates (never changes)
- **Tier 1:** Stable knowledge, industry best practices, design patterns (annual updates)
- **Tier 2:** Session context, recent learnings, project-specific patterns (7-day retention)
- **Tier 3:** Volatile state, temporary caches, in-progress computations (session-scoped)

**Storage Location:** `cortex_intelligence/` directory with subdirectories: `tier0/`, `tier1/`, `tier2/`, `tier3/`, `governance/`, `domain/`, `state/`

**Access Pattern:** Orchestrators query highest tier first (0→1→2→3) for authority precedence. Domain Brain extends with company-specific knowledge.

**Performance:** Tier 0/1 loaded at startup (200ms). Tier 2/3 lazy-loaded per request (10-30ms).

**Related:** [Knowledge Tiers](#knowledge-tiers), [Domain Brain](#domain-brain), [Orchestrators](#orchestrators)

---

## C

### CCL (Context Crystallization Layer)

**Category:** Performance | **Full Name:** Context Crystallization Layer

**Definition:** Asynchronous context pre-warming system introduced in Phase 49 that loads rules cache, LENS state, and infrastructure detection before request processing begins. Reduces Stage 2 latency by ~15% through parallel context preparation.

**Process:**
1. **Async Load Rules Cache** — Company > Tier1 > Tier0 (100ms parallel)
2. **Warm LENS** — AST, git history, comments (150ms parallel)
3. **Detect Infrastructure** — Python env, git config, MCP health (50ms parallel)
4. **Merge Context** — Combine pre-warmed data into Stage 2 request processing

**Performance Targets:**
- **SLA:** 300ms target, 500ms fallback maximum
- **Cache Hit Rate:** 70%+ target (rules cache reuse)
- **Latency Improvement:** -15% Stage 2 (from ~700ms to ~600ms)

**Timeout Behavior:**
- **≤300ms:** Full context merged into Stage 2
- **301-500ms:** Partial context merged, remaining loaded on-demand
- **>500ms:** Fallback to synchronous loading (no penalty vs baseline)

**Related:** [Performance Optimization](#performance-optimization), [LENS](#lens), [Stage Architecture](#stage-architecture)

---

### Challenge Gate

**Category:** Governance | **Full Name:** Design Challenge Gate

**Definition:** Mandatory design review step that presents alternative approaches before implementation, ensuring the best solution is chosen (not just the first solution). Part of Holistic Validation Gate (CORE-048).

**Format:**
```
### Challenge Gate

**Your Approach:**
- Pros: {list benefits}
- Cons: {list drawbacks}
- ROI: {effort vs value analysis}

**Alternative A:**
- Pros: {list benefits}
- Cons: {list drawbacks}
- ROI: {effort vs value analysis}

**Decision Required:** User must choose or provide reason to override
```

**When Triggered:** All IMPLEMENT intents after DoR (Definition of Ready) approval, before TDD workflow begins

**Purpose:**
- Prevent premature optimization
- Surface overlooked alternatives
- Validate architectural assumptions
- Build consensus on approach

**MCP Tool:** `cortex_challenge` generates challenges using disagreement detection algorithms

**Related:** [Holistic Validation Gate](#holistic-validation-gate), [CORE-048](#core-rules), [DoR](#dor)

---

### Code Intelligence

**Category:** Intelligence | **Full Name:** Multi-Layer Code Intelligence System

**Definition:** Unified code analysis capability combining AST parsing, git history, comment analysis, import resolution, security scanning, pattern detection, metrics collection, and domain inference. Powers LENS synthesis and orchestrator decision-making.

**Intelligence Layers:**
1. **Syntactic:** AST structure, function signatures, class hierarchies
2. **Semantic:** Variable relationships, data flow, control flow
3. **Historical:** Git blame, change patterns, contributor context
4. **Social:** Code comments, documentation, team knowledge
5. **Security:** Vulnerability patterns, injection risks, secrets detection
6. **Architectural:** Design patterns, layer boundaries, coupling metrics

**Performance:** Full intelligence scan completes in 300-800ms for small repos (100-500 files), 1200-2000ms for large repos (2000+ files). Cache hit rates: 60-85% depending on change frequency.

**Related:** [LENS](#lens), [AST Analysis](#ast-analysis), [Static Analysis](#static-analysis)

---

### CORE Rules

**Category:** Governance | **Full Name:** CORE Governance Rules

**Definition:** 59 foundational rules defining CORTEX quality standards, development practices, and architectural principles. Rules categorized as Tier 0 (immutable), Tier 1 (stable), or Tier 2 (evolving). 26/59 rules automated by EnforcementOrchestrator (87% coverage).

**Key Rules:**
- **CORE-002:** NO markdown file generation in chat responses (inline only)
- **CORE-008:** TDD MANDATORY (tests BEFORE code, no test bypass)
- **CORE-011:** Type hints mandatory on all parameters + returns
- **CORE-012:** Google-style docstrings required
- **CORE-027:** Audit trail (AC_START → AC_COMPLETE markers)
- **CORE-030:** Implementation Truth (verify code, not docs)
- **CORE-035:** Single canonical implementation (no duplication)
- **CORE-048:** Holistic Validation Gate (pre-implementation validation)
- **CORE-049:** MCP-FIRST (all functionality via MCP tools)
- **CORE-052:** Single Branch Policy (all work on CORTEX branch)

**Enforcement:** 7 enforcement agents (GovernanceEnforcement, SecurityCheckpoint, ComplianceValidation, FileNaming, IncrementalExecution, MarkdownSuppression, ArchitectureIntegrity)

**Validation Latency:** P50: 85ms, P95: 140ms, P99: 200ms

**Related:** [Governance](#governance), [Enforcement Orchestrator](#enforcement-orchestrator), [AC Markers](#ac-markers)

---

## D

### DoR (Definition of Ready)

**Category:** Process | **Full Name:** Definition of Ready

**Definition:** Pre-execution approval gate displaying intent classification table to user before work begins. Ensures user understands what will happen and explicitly approves the plan.

**Display Format:**
```markdown
| Intent | Orchestrator | MCP Tool | Estimated Effort |
|--------|--------------|----------|------------------|
| IMPLEMENT | TDDOrchestrator | cortex_process_request | 15-30 minutes |
```

**Approval Keywords:** "proceed", "yes", "approve", "continue", "implement"

**Required Elements:**
- **Intent Classification:** IMPLEMENT, FIX, REFACTOR, ANALYZE, AUDIT, DESIGN, PLAN
- **Orchestrator Assignment:** Which orchestrator will handle request
- **MCP Tool Mapping:** Which tool will be invoked
- **Effort Estimate:** Expected duration based on LENS analysis

**Related:** [Intent Classification](#intent-classification), [LENS](#lens), [Challenge Gate](#challenge-gate)

---

### Domain Brain

**Category:** Architecture | **Full Name:** Company-Specific Knowledge Layer

**Definition:** Extension of CORTEX Brain storing company-specific domain knowledge, business rules, architectural patterns, and team conventions. Precedence over CORTEX defaults (company > tier1 > tier0).

**Storage Location:** `company/domains/` directory with YAML/markdown files

**Content Types:**
- **Domain Models:** Business entities, relationships, constraints
- **Architectural Standards:** Company-specific patterns, technology choices
- **Governance Extensions:** Additional rules beyond CORE (e.g., PCI-DSS, HIPAA)
- **Team Conventions:** Naming standards, code review checklists

**Loading Priority:** Domain Brain consulted first, CORTEX fills gaps for unspecified areas

**Related:** [Brain](#brain-cortex-brain), [Knowledge Tiers](#knowledge-tiers), [Best Practices Layering](#best-practices-layering)

---

## E

### Enforcement Orchestrator

**Category:** Orchestration | **Full Name:** EnforcementOrchestrator

**Definition:** Core orchestrator responsible for 4-layer governance defense (Pre-Execution → Runtime → Post-Audit → Production). Coordinates 7 enforcement agents validating 26/59 CORE rules with 87% automation coverage.

**7 Enforcement Agents:**
1. **GovernanceEnforcementAgent** — TDD-first, type hints, docstrings (CORE-008, 011, 012, 013, 029, 030)
2. **SecurityCheckpointAgent** — Git discipline, audit trail integrity (CORE-025, 026, 027)
3. **ComplianceValidationAgent** — Domain-specific compliance (Tier 1 rules)
4. **FileNamingEnforcementAgent** — SCREAMING_CASE blocking (CORE-028)
5. **IncrementalExecutionAgent** — <500 LOC increments, continuation limits (CORE-001, 004)
6. **MarkdownSuppressionAgent** — Block *-summary.md, *-report.md generation (CORE-002)
7. **ArchitectureIntegrityAgent** — Versioned filenames, performance, turn budgets (CORE-017-020, 032, 034, 035, 038-041)

**Performance:** Validation completes in P50: 85ms, P95: 140ms, P99: 200ms. False positive rate ~5%.

**Blocking Behavior:** Violations with severity ≥ CRITICAL block execution. 3+ violations trigger runtime halt.

**Related:** [Governance](#governance), [CORE Rules](#core-rules), [Orchestrators](#orchestrators)

---

## G

### Git-Backed Registry

**Category:** Infrastructure | **Full Name:** Git-Backed Configuration Registry

**Definition:** File-based configuration system using Git as the storage backend. Eliminates need for PostgreSQL/MongoDB in production, providing version-controlled, auditable configuration with zero runtime database dependencies.

**Registry Structure:** (cortex-registry/)
- **_cortex-master/** — Master indices, phase definitions, enhancements
- **domains/** — Domain-specific knowledge graphs
- **governance/** — Compliance rules, audit policies
- **interaction/** — Content blocks, response templates
- **master/** — Wiring specifications, tool catalog
- **planning/** — Phase management, wave definitions

**File Formats:** YAML (configuration), Markdown (documentation), JSON (metrics)

**Loading:** Registry files loaded at startup (200-400ms) with lazy-loading for large datasets

**Benefits:**
- **Version Control:** All configuration changes tracked via Git
- **Zero Runtime DB:** No PostgreSQL/MongoDB operational overhead
- **Auditability:** Full history of configuration changes
- **Simplicity:** Standard file operations, no ORM complexity

**Related:** [Infrastructure](#infrastructure), [Configuration Management](#configuration-management)

---

### Governance

**Category:** Architecture | **Full Name:** Multi-Layer Governance System

**Definition:** 4-layer defense-in-depth architecture ensuring code quality, security, and compliance. Layers: Pre-Execution Gate → Runtime Monitor → Post-Execution Audit → Production Gate.

**Layer 1: Pre-Execution Gate**
- **Agent:** EnforcementOrchestrator with 7 agents
- **Rules:** 26/59 CORE rules automated (87% coverage)
- **Latency:** P50: 85ms, P95: 140ms, P99: 200ms
- **Action:** BLOCKS violations before code generation

**Layer 2: Runtime Monitor**
- **Agent:** Real-time violation tracking during execution
- **Rules:** Continuous monitoring of CORE-004, 008, 013
- **Action:** STOPS execution at 3+ violations

**Layer 3: Post-Execution Audit**
- **Agent:** Code analysis after generation, before commit
- **Rules:** AC markers, test results, coverage verification
- **Action:** DETECTS bypasses, missing audit trail

**Layer 4: Production Gate**
- **Agent:** Pre-deployment validation via git hooks
- **Rules:** All P0/P1/P2 issues must be resolved
- **Action:** PREVENTS broken deployment to production

**Related:** [Enforcement Orchestrator](#enforcement-orchestrator), [CORE Rules](#core-rules), [AC Markers](#ac-markers)

---

## H

### Holistic Validation Gate

**Category:** Governance | **Full Name:** Phase 48 Holistic Validation Gate

**Definition:** Mandatory pre-implementation validation combining Challenge Gate, DoR confidence scoring, and multi-factor analysis. Introduced in Phase 48 as CORE-048 requirement.

**Components:**
1. **Challenge Gate** — Present alternative approaches (mandatory)
2. **DoR Confidence** — Score 0.0-1.0 based on requirements clarity
3. **Impact Analysis** — Affected files, test coverage, regression risk
4. **Resource Estimate** — LOC, effort hours, test count

**Validation Criteria:**
- **DoR Confidence ≥ 0.7** — Requirements sufficiently clear
- **Regression Risk < 0.3** — Low risk of breaking existing features
- **Test Coverage ≥ 80%** — Adequate test protection
- **Challenge Reviewed** — User explicitly chose approach

**Blocking:** DoR confidence <0.5 OR regression risk >0.7 blocks execution

**Related:** [Challenge Gate](#challenge-gate), [DoR](#dor), [CORE-048](#core-rules)

---

## I

### Intelligent Prompt Routing

**Category:** Architecture | **Full Name:** Auto-Detect Prompt Mode Selection

**Definition:** Strategy pattern that automatically selects appropriate prompt file based on repository context. Architect Mode vs Production Mode determined by presence of CORTEX-internal markers.

**Detection Logic:**
```python
workspace_root = Path(os.getcwd())
if (workspace_root / ".cortex").exists() or \
   (workspace_root / "cortex-registry").exists() or \
   (workspace_root / "cortex" / "__init__.py").exists():
    mode = "ARCHITECT"  # CORTEX internal development
    prompt = "cortex-architect.prompt.md"
else:
    mode = "PRODUCTION"  # User's production repository
    prompt = "CORTEX.prompt.md"
```

**Mode Differences:**
- **Context Loading:** CORTEX-internal vs user domain
- **Header Icon:** 🏛️ (Architect) vs 🧠 (Production)
- **Orchestrators:** Same (only context differs)

**Related:** [Architect Mode](#architect-mode), [Production Mode](#production-mode)

---

### Intent Classification

**Category:** Intelligence | **Full Name:** LENS Intent Classification

**Definition:** Multi-stage analysis determining user request intent (IMPLEMENT, FIX, REFACTOR, ANALYZE, AUDIT, DESIGN, PLAN, DEBUG, DIGEST, QUERY, LIST, RECALL). Powers orchestrator routing and tool selection.

**Classification Process:**
1. **Language (L)** — Parse user request syntax, extract keywords
2. **Examination (E)** — Analyze repository context, affected files
3. **Navigation (N)** — Map intent to available capabilities
4. **Synthesis (S)** — Recommend orchestrator + tool + effort

**Performance:** Classification completes in 20-40ms with 95%+ accuracy

**Intent → Orchestrator Mapping:**
- **IMPLEMENT** → TDDOrchestrator → `cortex_process_request`
- **FIX** → TDDOrchestrator → `cortex_process_request`
- **REFACTOR** → RefactoringOrchestrator → `cortex_process_request`
- **ANALYZE** → LENSSynthesis → `cortex_lens_analyze`
- **AUDIT** → EnforcementOrchestrator → `cortex_audit`
- **PLAN** → PlanOrchestrator → `cortex_plan_setup/resolve`

**Related:** [LENS](#lens), [DoR](#dor), [Orchestrators](#orchestrators)

---

## L

### LENS

**Category:** Intelligence | **Full Name:** Language → Examination → Navigation → Synthesis

**Definition:** Four-phase cognitive cycle providing unified code intelligence. LENS powers intent classification, context analysis, capability navigation, and recommendation synthesis across all orchestrators.

**Four Phases:**

**Phase 1: Language (L)** — Parse input, extract keywords, classify intent (50-150ms)
- **Analyzers:** AST, Git History, Comment (parallel execution)
- **Output:** Syntactic structure, change context, semantic hints

**Phase 2: Examination (E)** — Deep code analysis, pattern detection (100-300ms)
- **Analyzers:** Import, Security, Pattern, Metrics (parallel execution)
- **Output:** Dependencies, vulnerabilities, design patterns, complexity metrics

**Phase 3: Navigation (N)** — Map capabilities, generate options (80-200ms)
- **Analyzers:** Domain inference, orchestrator matching
- **Output:** Available tools, orchestrator candidates, effort estimates

**Phase 4: Synthesis (S)** — Recommend action, build DoR (70-150ms)
- **Analyzers:** Confidence scoring, challenge generation
- **Output:** Final recommendation, DoR table, challenge alternatives

**Total Latency:** 300-800ms (small repos), 1200-2000ms (large repos)

**Cache Hit Rate:** 60-85% depending on file change frequency

**Related:** [Code Intelligence](#code-intelligence), [Intent Classification](#intent-classification), [AST Analysis](#ast-analysis)

---

## M

### MCP (Model Context Protocol)

**Category:** Protocol | **Full Name:** Model Context Protocol

**Definition:** JSON-RPC 2.0-based protocol for communication between AI assistants (Claude, GPT) and CORTEX backend. Standardizes tool invocation, parameter passing, and result serialization.

**Architecture:** Pylance-style local integration (auto-started by VS Code, no manual server management)

**Transport Modes:**
- **stdio (Development):** JSON-RPC over stdin/stdout (<5ms latency)
- **HTTP (Production Phase 11):** JSON-RPC over HTTP with Nginx gateway

**10 Core MCP Tools:**
1. `cortex_process_request` — Main implementation workflow
2. `cortex_lens_analyze` — Code intelligence
3. `cortex_plan_setup` — Pre-implementation hook
4. `cortex_plan_resolve` — Phase resolution
5. `cortex_challenge` — Design challenges
6. `cortex_audit` — Health scans
7. `cortex_digest_session` — Learning extraction
8. `cortex_total_recall` — Feature discovery
9. `cortex_git_history` — 24h context
10. `cortex_detect_duplicates` — CORE-035 detection

**Performance:** P50: 5ms (stdio), P95: 15ms (stdio), P99: 25ms (stdio)

**Related:** [MCP Gateway](#mcp-gateway), [JSON-RPC](#json-rpc), [Tools](#tools)

---

### MCP Gateway

**Category:** Infrastructure | **Full Name:** MCP Protocol Gateway

**Definition:** Entry point for all AI assistant requests. Performs request validation, authentication (Phase 11), routing to orchestrators, and response serialization.

**Responsibilities:**
- **Request Validation:** Schema validation, parameter checking (5-15ms)
- **Authentication:** JWT token validation (Phase 11 production)
- **Intent Classification:** Route to IntentRouter for LENS analysis
- **Response Formatting:** Serialize orchestrator results to JSON-RPC
- **Error Handling:** Standardized error codes + messages

**Performance:** Gateway overhead P50: 10ms, P95: 20ms, P99: 30ms

**Health Check:** `/health` endpoint returns MCP server status, orchestrator count, tool availability

**Related:** [MCP](#mcp-model-context-protocol), [IntentRouter](#intentrouter)

---

## O

### Orchestrators

**Category:** Architecture | **Full Name:** Hierarchical Orchestrator Network

**Definition:** 20+ specialized components coordinating CORTEX capabilities. Orchestrators implement specific workflows (TDD, refactoring, planning) and coordinate agents, tools, and intelligence systems.

**Orchestrator Categories:**

**Core (8):**
- MasterOrchestrator — Top-level coordination + pre-flight validation
- InteractionOrchestrator — User interaction patterns
- IntentRouter — LENS-based intent classification → routing
- LENSSynthesis — Code intelligence synthesis
- EnforcementOrchestrator — 4-layer governance defense
- TDDOrchestrator — RED→GREEN→REFACTOR workflow
- IncrementalTaskDecomposer — <500 LOC task breakdown
- WorkflowOrchestrator — Multi-stage workflow coordination

**Domain (6):**
- RefactoringOrchestrator — Code improvement workflows
- PlanningOrchestrator — Feature planning lifecycle
- DomainOrchestrator — Domain-specific logic
- ConversationOrchestrator — Multi-turn dialogue
- DocumentationOrchestrator — Doc generation
- ChallengeEngine — Design challenge generation

**Support (6+):**
- OnboardingOrchestrator — Repository onboarding
- ToolDiscoveryOrchestrator — MCP tool catalog
- RecommendationGate — REJ-* validation
- EducationalOrchestrator — Learning content
- PlanOrchestrator — Phase lifecycle management
- ContextSynthesisGateway — Cost-aware context (EXIT GATE)

**Wiring:** Auto-discovered via `cortex-registry/master/__wiring_contract__.yaml`

**Related:** [MasterOrchestrator](#masterorchestrator), [TDDOrchestrator](#tddorchestrator), [EnforcementOrchestrator](#enforcement-orchestrator)

---

## P

### Production Mode

**Category:** Operational Mode | **Full Name:** CORTEX Production Mode

**Definition:** Default operational mode for user production repositories. Uses standard prompt file (`CORTEX.prompt.md`) and loads user domain knowledge (not CORTEX-internal context).

**Detection Logic:** Activated when repository does NOT contain `.cortex/`, `cortex-registry/`, or `cortex/__init__.py`

**Header Format:** `🧠 CORTEX {MODE}` (e.g., "🧠 CORTEX IMPLEMENT")

**Context Loading:** User domain knowledge (business logic, APIs, architecture patterns) from company/domains/ and repository content

**Related:** [Architect Mode](#architect-mode), [Intelligent Prompt Routing](#intelligent-prompt-routing)

---

## R

### RED-GREEN-REFACTOR

**Category:** Process | **Full Name:** TDD Cycle

**Definition:** Three-phase Test-Driven Development workflow enforced by TDDOrchestrator. CORE-008 mandates this cycle for all IMPLEMENT/FIX operations.

**Phase 1: RED (Write Failing Test)**
- Write test that fails (demonstrates missing functionality)
- Verify test execution (confirms test framework works)
- Commit test: `git commit -m "RED: test_{feature_name}"`

**Phase 2: GREEN (Make Test Pass)**
- Implement minimal code to pass test
- Run tests to verify (no skipping, no mocking failures)
- Commit implementation: `git commit -m "GREEN: {feature_name}"`

**Phase 3: REFACTOR (Improve Code Quality)**
- Enhance code quality (DRY, SOLID, Clean Code)
- Run tests to verify (ensure no regressions)
- Commit refactoring: `git commit -m "REFACTOR: {feature_name}"`

**Test Bypass Prevention:** CORE-008-SUB forbids `--ignore` flags, `_skip_*` renaming, test deletion, or mocking failures

**Related:** [TDDOrchestrator](#tddorchestrator), [CORE-008](#core-rules)

---

## S

### Single Branch Policy

**Category:** Governance | **Full Name:** CORE-052 Single Branch Policy

**Definition:** All development work must be performed on the `CORTEX` branch. No feature branches, backup branches, or wave branches allowed. Use `git commit` for checkpoints, `git tag` for releases, `git stash` for temporary saves.

**Rationale:**
- **Simplicity:** One branch = no merge conflicts
- **Auditability:** Linear history easier to audit
- **Discipline:** Forces small, frequent commits

**Forbidden Operations:**
```bash
❌ git checkout -b feature/new-thing
❌ git switch -c backup/save-point
❌ git branch wave-2/phase-10
```

**Allowed Operations:**
```bash
✅ git commit -m "Checkpoint: Stage 2 complete"
✅ git tag v8.1-release
✅ git stash save "WIP: Testing approach"
```

**Violation:** Creating any new local branch = CORE-052 governance violation

**Related:** [CORE Rules](#core-rules), [Git Discipline](#git-discipline)

---

### Stage Architecture

**Category:** Architecture | **Full Name:** Multi-Stage Request Processing

**Definition:** Request processing broken into discrete stages with clear responsibilities, performance SLAs, and failure isolation.

**Stage Breakdown:**

**Stage 1: Initiation (5-10ms)**
- Receive MCP tool invocation
- Parse JSON-RPC parameters
- Route to IntentRouter

**Stage 2: Pre-Flight Checks (150-300ms)**
- Context Crystallization Layer (CCL) async prefetch
- MCP availability validation
- Environment integrity check
- Rules cache loading

**Stage 3: Intent Classification (20-40ms)**
- LENS four-phase cycle
- DoR confidence scoring
- Orchestrator selection

**Stage 4: Execution (500-2000ms)**
- Orchestrator workflow (TDD, LENS, Plan, etc.)
- Agent coordination
- Tool invocations

**Stage 5: Response Delivery (10-20ms)**
- Serialize results to JSON-RPC
- Format response per standards
- Return to AI assistant

**Total Latency:** P50: 700ms, P95: 2400ms, P99: 3500ms

**Related:** [MCP Gateway](#mcp-gateway), [CCL](#ccl-context-crystallization-layer), [Performance](#performance-optimization)

---

### Static Analysis

**Category:** Intelligence | **Full Name:** Static Code Analysis

**Definition:** Code analysis performed without execution. CORTEX combines AST parsing, pattern matching, security scanning, and metrics collection for comprehensive static analysis.

**Analysis Types:**
- **Syntactic:** AST structure, function signatures, class hierarchies
- **Semantic:** Variable relationships, data flow, control flow
- **Security:** Vulnerability patterns, injection risks, secrets detection
- **Complexity:** Cyclomatic complexity, cognitive complexity, maintainability index
- **Style:** PEP 8, ESLint, code formatting violations

**Tools Used:** tree-sitter (AST), Bandit (Python security), semgrep (pattern matching), radon (complexity metrics)

**Related:** [AST Analysis](#ast-analysis), [LENS](#lens), [Code Intelligence](#code-intelligence)

---

## T

### TDDOrchestrator

**Category:** Orchestration | **Full Name:** Test-Driven Development Orchestrator

**Definition:** Core orchestrator implementing RED→GREEN→REFACTOR workflow for IMPLEMENT/FIX operations. Enforces CORE-008 (TDD mandatory) with test-bypass prevention.

**Workflow:**
1. **Pre-Execution Gate** — EnforcementOrchestrator validation (7 agents)
2. **Challenge Gate** — Present alternatives before implementation
3. **RED Phase** — Write failing test, verify execution, commit
4. **GREEN Phase** — Implement code, pass test, commit
5. **REFACTOR Phase** — Improve quality, verify tests, commit
6. **Post-Execution Audit** — Verify AC markers, test results, coverage

**Test Bypass Prevention:**
- Detect `--ignore` flags in test commands
- Block `_skip_*` file renaming
- Prevent test deletion during execution
- Validate test output for genuine pass/fail

**Performance:** Average TDD cycle 500-2000ms depending on test complexity

**Related:** [RED-GREEN-REFACTOR](#red-green-refactor), [CORE-008](#core-rules), [Orchestrators](#orchestrators)

---

### Tools

**Category:** Infrastructure | **Full Name:** MCP Tool Catalog

**Definition:** 10 core MCP tools exposing 90+ operations across orchestrators, agents, and intelligence systems. All CORTEX functionality exposed via MCP-FIRST architecture.

**Tool Categories:**

**Implementation (3 tools):**
- `cortex_process_request` — IMPLEMENT, FIX, REFACTOR operations

**Intelligence (2 tools):**
- `cortex_lens_analyze` — Code intelligence synthesis
- `cortex_detect_duplicates` — CORE-035 violation detection

**Planning (2 tools):**
- `cortex_plan_setup` — Pre-implementation hook
- `cortex_plan_resolve` — Intelligent phase resolution

**Governance (1 tool):**
- `cortex_audit` — Health scans, compliance checks

**Discovery (2 tools):**
- `cortex_total_recall` — Feature discovery
- `cortex_git_history` — 24h git context

**Design (1 tool):**
- `cortex_challenge` — Design challenge generation

**Learning (1 tool):**
- `cortex_digest_session` — Learning extraction from chat sessions

**Performance:** Tool invocation overhead <5ms (stdio), <20ms (HTTP Phase 11)

**Related:** [MCP](#mcp-model-context-protocol), [MCP Gateway](#mcp-gateway)

---

## W

### Wiring Contract

**Category:** Infrastructure | **Full Name:** __wiring_contract__.yaml

**Definition:** YAML specification defining orchestrator registration, capabilities, dependencies, and hot-reload behavior. Enables zero-downtime orchestrator updates via file-based configuration.

**File Location:** `cortex/__wiring_contract__.yaml` (root contract) + orchestrator-specific contracts in subdirectories

**Contract Structure:**
```yaml
orchestrator:
  name: TDDOrchestrator
  version: 8.1
  capabilities:
    - IMPLEMENT
    - FIX
    - TEST
  dependencies:
    - EnforcementOrchestrator
    - LENSSynthesis
  mcp_tools:
    - cortex_process_request
  reload: hot  # hot | cold | manual
```

**Hot Reload:** Change wiring contract → MasterOrchestrator detects → Orchestrator reloaded within 1 request cycle (no service restart)

**Discovery:** MasterOrchestrator scans `cortex-registry/master/` at startup, loading all wiring contracts in dependency order

**Related:** [Orchestrators](#orchestrators), [Git-Backed Registry](#git-backed-registry), [MasterOrchestrator](#masterorchestrator)

---

## Additional Resources

**Core Documentation:**
- [Architecture Overview](index.md) — System architecture and design principles
- [MCP Protocol](mcp/overview.md) — Model Context Protocol specifications
- [LENS Intelligence](lens/overview.md) — Code intelligence system
- [Orchestration](orchestration/overview.md) — Orchestrator network
- [Governance](capabilities/governance-compliance.md) — 4-layer defense architecture

**Diagrams:**
- [C4 Context Diagram](diagrams/c4-context.md) — System boundaries
- [C4 Container Diagram](diagrams/c4-container.md) — Runtime architecture
- [MCP Request Lifecycle](diagrams/mcp-request-lifecycle.md) — End-to-end request flow

**Guides:**
- [Developer Guide](toolkit/developer-guide.md) — Getting started with CORTEX
- [Tool Catalog](toolkit/overview.md) — MCP tool reference
- [Infrastructure Guide](infrastructure/overview.md) — Deployment and operations

---

**Last Updated:** 2026-02-16 | **Version:** 4.1 | **Maintainer:** CORTEX Documentation Team

---

## Recent Additions (Feb 2026)

### Intelligence Layer

**Category:** Intelligence | **Phase:** 96

**Definition:** Learning-enhanced capability layer that provides pattern recognition, adaptive optimization, and self-improvement to CORTEX orchestrators. Initially deployed in HealthOrchestrator and VacuumOrchestrator, the Intelligence Layer learns from 48-hour git history to reduce false positives, cache results, and improve accuracy over time.

**Core Components:**
- **Pattern Learner:** Extracts recurring patterns from git history
- **Smart Cache:** File hash-based caching (73% hit rate, 8.2x speedup)
- **False Positive Detector:** Suppresses known non-issues (85.2% → <5% FP rate)
- **Safety Analyzer:** Multi-layer validation for destructive operations
- **Confidence Scorer:** Pattern reliability assessment (0.0-1.0 scale)

**Performance Gains:**
- Health checks: 920ms → 680ms (26% faster)
- False positive reduction: 80+ percentage points
- Path integrity warnings: 6,901 → 759 (89% reduction)

**Related:** [HealthOrchestrator](#healthorchestrator), [Phase 96](#phase-96), [Pattern Learning](#pattern-learning)

---

### RequestRephraseOrchestrator

**Category:** Orchestration | **Stage:** -1 (Pre-Processing)

**Definition:** Automatic request enhancement orchestrator that operates before the main orchestration pipeline (Stage -1). Every user request flows through RequestRephrase to inject governance context, architecture awareness, risk assessment, and challenge-first evaluation before reaching MasterOrchestrator.

**Enhancements Provided:**
1. **Intent Classification:** 9 types (IMPLEMENT, FIX, REFACTOR, ANALYZE, PLAN, DESIGN, QUERY, AUDIT, DIGEST)
2. **Governance Matching:** Auto-inject relevant CORE rules based on intent
3. **Risk Assessment:** Breaking risk levels (ZERO/LOW/MEDIUM/HIGH)
4. **Challenge Analysis:** 5 design pillar evaluation (Simplicity, Testability, Maintainability, Performance, Security)
5. **Architecture Context:** Relevant orchestrators, protocols, wiring patterns

**Performance:** P50: 18ms, P95: 28ms, P99: 42ms (1.1% overhead on typical workflows)

**Test Status:** 34/34 tests passing (GREEN phase)

**Related:** [MasterOrchestrator](#masterorchestrator), [Intent Classification](#intent-classification), [Stage -1](#stage--1)

---

### Semantic Blocks

**Category:** Content Assembly | **Enhancement:** ENH-089, ENH-090

**Definition:** Structured, personality-enforced response assembly framework that composes CORTEX responses from predefined semantic blocks with strict formatting guidelines, voice constraints, and anti-duplication rules. Replaces ad-hoc text generation with registry-driven composition.

**Block Categories (8):**
- **Explanation:** Technical concepts (800-1500 words)
- **Tutorial:** Step-by-step guides (1000-1800 words)
- **Reference:** API/tool specs (400-800 words)
- **How-To:** Task-oriented procedures (600-1000 words)
- **Status:** Operation results (200-400 words)
- **Error:** Failure messages (100-300 words)
- **Confirmation:** Approval prompts (50-150 words)
- **Summary:** Digest/recap (300-600 words)

**Personality Enforcement:**
- Voice: Third-person neutral technical
- Prohibited: Emojis, casual language, excessive exclamation, first-person
- Required: Technical precision, evidence-backed claims, code examples

**Registry:** `cortex-registry/interaction/` (content-blocks.yaml, personality-guidelines.yaml)

**Related:** [Response Formatting](#response-formatting), [Content Assembly](#content-assembly), [Personality Guidelines](#personality-guidelines)

---

### Toolkit Module

**Category:** Infrastructure | **Phase:** 90

**Definition:** Consolidated set of 5 production modules that replace 47 scattered Python scripts from `.cortex/` and `scripts/` directories. Provides unified interfaces for development utilities with comprehensive test coverage and MCP tool exposure.

**5 Modules:**
1. **Discovery** (19 tests) — Tool scanning and categorization
2. **Diagnostics** (19 tests) — MCP health checks and environment verification
3. **Setup** (28 tests) — Environment configuration and validation
4. **Cleanup** (38 tests) — Vacuum operations with intelligence layer
5. **Validation** (52 tests) — Governance and production readiness checks

**MCP Tools:** 5 tools (`cortex_toolkit_discovery`, `cortex_toolkit_diagnostics`, `cortex_toolkit_setup`, `cortex_toolkit_cleanup`, `cortex_toolkit_validate`)

**Consolidation Impact:**
- Script reduction: 47 → 5 (89.4%)
- Code reduction: 8,200 → 2,759 lines (66.4%)
- Test coverage: 0% → 95.4%
- Passing tests: 0 → 66

**Related:** [Phase 90](#phase-90), [MCP Tools](#mcp-tools), [Vacuum](#vacuum)

---

### Stage -1

**Category:** Request Pipeline | **Orchestrator:** RequestRephraseOrchestrator

**Definition:** Pre-processing stage that executes before the main orchestration pipeline (Stage 0+). Stage -1 automatically enhances every user request with governance context, risk assessment, and architecture awareness before it reaches MasterOrchestrator.

**Pipeline Order:**
- **Stage -1:** RequestRephrase (auto-enhancement)
- **Stage 0:** MasterOrchestrator entry + pre-flight checks
- **Stage 1:** IntentRouter classification
- **Stage 2:** LENS context synthesis
- **Stage 3+:** Specialized orchestrator execution

**Latency:** 18ms P50 (minimal overhead for significant value)

**Related:** [RequestRephraseOrchestrator](#requestrephraseorchestrator), [MasterOrchestrator](#masterorchestrator), [Pre-Processing](#pre-processing)

---

### Pattern Learning

**Category:** Intelligence | **Technique:** Git History Analysis

**Definition:** Automated learning technique that analyzes recent git history (48-hour window) to extract recurring patterns, identify false positives, and improve algorithmic accuracy over time. Core capability of the Intelligence Layer (Phase 96).

**Learning Sources:**
- Recent commits (intent, changes, fixes)
- Bug fix patterns (what was fixed and why)
- File renames (consolidation patterns)
- Code patterns (common module structures)

**Pattern Types:**
- **False Positive:** Known non-issues to suppress
- **Genuine Issue:** Validated problems to surface
- **Resolved:** Previously flagged issues that are now fixed

**Confidence Scoring:** 0.0-1.0 scale based on occurrence frequency and validation accuracy

**Applications:**
- Health check false positive suppression (85.2% → <5%)
- Vacuum safety analysis (100% accuracy)
- Adaptive rule tuning

**Related:** [Intelligence Layer](#intelligence-layer), [Git History](#git-history), [HealthOrchestrator](#healthorchestrator)

---

**Last Updated:** 2026-02-16 | **Version:** 4.1 | **Maintainer:** CORTEX Documentation Team
