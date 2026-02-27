---
title: CORTEX Capabilities
consolidates:
  - 01-capabilities-overview.md
  - 01-capabilities-core-platform.md
  - 01-capabilities-ai-intelligence.md
  - 01-capabilities-decisioning.md
  - 01-capabilities-extensibility.md
last_verified: 2026-02-27
source_of_truth: cortex/core/ + cortex/mcp/ + cortex/intelligence/ + cortex/lens/
audience: [Business Leaders, Product Owners, Software Developers]
---

# CORTEX Capabilities

CORTEX organises its capabilities into six domains, each modelled after a region of the human brain. Together they form a complete engineering intelligence platform — from code analysis to governance enforcement to extensible tool integration.

---

## 1. Core Platform — The Brainstem

The Core Platform is the foundational infrastructure that keeps everything alive. Like the brainstem controlling breathing and heartbeat, the Core Platform provides orchestration, MCP gateway, state management, and audit infrastructure that every other capability depends on.

### OrchestratorProtocolMixin — The Universal Protocol

Every one of the fifty-one wired orchestrators uses `OrchestratorProtocolMixin` combined with the `IOrchestrator` protocol and follows a five-step lifecycle:

- **setup** — initialise resources and load configuration
- **govern** — check governance rules via the pre-execution gate
- **execute** — perform the actual work
- **validate** — verify results against acceptance criteria
- **teardown** — record audit trail and clean up resources

The mixin automatically activates cross-cutting hooks for LENS intelligence, knowledge synthesis, and governance gates. Orchestrators that implement it receive all of these capabilities without additional code.

### CortexAuditDB — Unified Data Store

All orchestrators route audit data through `CortexAuditDB`, a SQLite database operating in Write-Ahead Logging mode. The database lives in `.cortex-runtime/` and provides concurrent read and write access. CORE-058 mandates WAL mode for all SQLite databases, enforced by the ExtendedGovernanceAgent.

Every operation is recorded with hash-chain integrity via `cortex/infrastructure/audit_hash_chain.py`, creating a tamper-evident trail of all orchestrator decisions, governance gate results, test execution outcomes, and strategy selection reasoning.

### MCP Server — The Spinal Cord

The MCP server runs as a Pylance-style stdio process that auto-starts when VS Code opens the workspace. It exposes registered MCP tools through JSON-RPC 2.0 transport, requiring no manual server startup and no exposed network ports in development mode.

### Key Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| OrchestratorProtocolMixin | `cortex/core/orchestrator_protocol_mixin.py` | Universal base for all wired orchestrators |
| FileFactory | `cortex/core/file_factory.py` | Canonical file creation with CORE-028 naming enforcement |
| WorkflowEngine | `cortex/core/workflow_engine.py` | Reads workflow YAML templates, executes phase sequences |
| CortexAuditDB | `cortex/infrastructure/audit_db.py` | Unified SQLite with WAL mode for all audit trails |
| MCP Server | `cortex/mcp/` | Pylance-style stdio server, registered tools |
| Bootstrap | `cortex/bootstrap.py` | System initialisation, wiring, service discovery |
| Config | `cortex/config/` | System configuration, feature flags |

### Infrastructure Services

| Service | Location | Purpose |
|---------|----------|---------|
| InfrastructureDetector | `cortex/intelligence/infrastructure/` | Detects FastAPI, Docker, Kubernetes, cloud configs |
| Health Check | `cortex/health_check_service.py` | System health monitoring |
| OpenTelemetry | `cortex/opentelemetry_tracing.py` | Distributed tracing |
| Prometheus | `cortex/prometheus_metrics.py` | Metrics collection |

---

## 2. LENS Intelligence — The Sensory Cortex

LENS (Language → Examination → Navigation → Synthesis) is CORTEX's code intelligence engine. It processes raw source code into structured intelligence the same way the visual cortex processes photons into edges, shapes, and objects.

Nine specialised analyzers run in parallel against any codebase:

| Analyzer | What It Detects | Speed |
|----------|----------------|-------|
| AST | Code structure — classes, functions, imports, decorators | under 100 milliseconds |
| Git History | Change patterns — hot spots, author frequency, recent edits | under 200 milliseconds |
| Comment | Documentation quality — docstring coverage, TODO and FIXME density | under 50 milliseconds |
| Import | Dependency graph — circular imports, stale imports, depth | under 100 milliseconds |
| Security | Vulnerabilities — SQL injection, XSS, credentials, CVE patterns | under 200 milliseconds |
| Pattern | Architecture — framework signatures, design pattern usage | under 150 milliseconds |
| Metrics | Complexity — cyclomatic complexity, coupling, lines of code | under 100 milliseconds |
| Domain | Business context — industry classification, regulatory context | under 100 milliseconds |
| TechStack | Framework detection — runtime versions, dependency stacks, build tools | under 80 milliseconds |

Combined latency ranges from three hundred to eight hundred milliseconds for a full nine-analyzer scan. The `CachedLENSOrchestrator` stores results with configurable time-to-live, reducing repeat analysis to under fifty milliseconds on cache hit.

LENS supports Python, TypeScript and JavaScript, C# and .NET, Angular, React, and Vue — with language-specific adapters in `cortex/lens/adapters/`.

---

## 3. Brain Tiers — The Decision System

After LENS processes raw data, the `UnifiedIntelligenceProvider` at `cortex/intelligence/provider.py` synthesises it through three cognitive tiers:

| Tier | Method | Company Knowledge | Latency |
|------|--------|------------------|---------|
| Quick | `provider.quick()` | No | under 10 milliseconds |
| Targeted | `provider.targeted()` | Yes — domain profiles loaded | under 100 milliseconds |
| Full | `provider.full()` | Yes, plus ADO sprint context and knowledge graph indexing | 300–800 milliseconds |

The three-tier brain architecture in `cortex/intelligence/` mirrors human cognition:

- **Perception** at `cortex/intelligence/perception/` — pattern matching against nine enterprise patterns (mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, command)
- **Reasoning** at `cortex/intelligence/reasoning/` — strategy selection ranked by historical success rate
- **Action** at `cortex/intelligence/action/` — step-by-step execution plan with TDD gates and rollback checkpoints

The brain learns continuously. Pattern confidence scores and strategy success rates update after every execution through the Unified Reinforcement Signal system. Patterns that consistently produce successful outcomes are promoted to high-confidence knowledge; patterns that consistently fail are quarantined and excluded from future guidance.

---

## 4. Decisioning — The Thalamus

Decisioning is the relay station at the centre of CORTEX that routes every request to the correct processing region.

### IntentRouter

`cortex/orchestrators/core/intent_router.py` classifies every request into one of twelve or more intent types using LENS-based classification in twenty to forty milliseconds:

| Intent | Routed To | What Happens |
|--------|-----------|-------------|
| IMPLEMENT | TDDOrchestrator | RED, GREEN, REFACTOR cycle for new features |
| FIX | TDDOrchestrator | RED, GREEN, REFACTOR cycle for bug repair |
| REFACTOR | RefactoringOrchestrator | Semantic code improvement |
| ANALYZE | LENS Synthesis | Ten-analyzer parallel scan |
| PLAN | PlanningOrchestrator | Development roadmap creation |
| AUDIT | EnforcementOrchestrator | Governance compliance check |
| DESIGN | Design coordination | Architecture decisions |
| DEBUG | DebuggerOrchestrator | Problem diagnosis |
| INVESTIGATE | IntelligenceOrchestrator | Deep analysis |
| QUERY | Context-dependent | Information retrieval |
| DIGEST | Digest Coordinator | Topic summarisation |
| REPHRASE | RequestRephraseOrchestrator | Request refinement |

### TDD Workflow Enforcement

Every IMPLEMENT and FIX operation follows mandatory RED then GREEN then REFACTOR as mandated by CORE-008. TDDOrchestrator writes a failing test first, implements minimum code to pass, then prompts refactoring while keeping all tests green. This is not optional — CORE-008 is enforced at the architecture level by EnforcementOrchestrator, and attempts to implement without a failing test are blocked before any files change.

### Challenge Engine

Before high-impact operations, the Challenge Engine performs a LENS analysis to assess the risk of the proposed change, identify potential breaking changes, surface governance considerations, and recommend whether to proceed, review, or abort. The MCP tool `cortex_challenge` is callable from any IDE.

---

## 5. Governance — The Immune System

Governance is CORTEX's immune system — it detects and blocks rule violations automatically, without conscious effort.

CORTEX enforces governance at three levels: pre-commit (before code enters Git via EnforcementOrchestrator and ten agents), CI pipeline (during continuous integration via automated validation), and runtime (during orchestrator execution via the governance gate in the orchestrator lifecycle).

Thirty-eight CORE rules plus two AC rules are defined in `cortex-registry/core/tier0-skull/skull-rules.yaml`. Key rules include:

| Rule | Name | Description |
|------|------|-------------|
| CORE-001 | Flywheel Effect | Operations work in bounded increments; state persists between turns |
| CORE-002 | Markdown Suppression | Never create report files; all output delivered inline |
| CORE-008 | TDD Mandatory | Write failing test first; blocked if skipped |
| CORE-011 | Type Hints | All functions must have type annotations |
| CORE-012 | Docstrings | All public APIs must have docstrings |
| CORE-028 | File Naming | snake_case only, enforced by FileFactory |
| CORE-035 | Single Canonical | No duplicate implementations anywhere |
| CORE-048 | Holistic Validation | Full validation gate before implementation |
| CORE-049 | Silent Execution | Progress bars only; no verbose output |
| CORE-055 | Golden Test Contract | Golden tests must always pass with zero regressions |
| CORE-064 | Sweep Completeness | No partial sweeps; every operation exhausts its catalogue |

### Ten Enforcement Agents

EnforcementOrchestrator at `cortex/orchestrators/core/enforcement_orchestrator.py` coordinates ten agents that each check a category of rules. Gate results are PASS (operation proceeds), WARNING (operation proceeds with logged advisory), or BLOCKED (operation stops immediately with no files changed).

### TestQualityGate

Every test is scored zero to nine using the formula: Impact (zero to three) plus Likelihood (zero to two) plus Detection (zero to two) plus Efficiency (zero to two) minus Maintenance (zero to two). Tests scoring seven or above are kept as golden tier candidates. Tests scoring four to six are flagged for review. Tests scoring below four are candidates for deletion.

---

## 6. Extensibility — Neuroplasticity

CORTEX is designed to grow new capabilities without modifying the core, the same way the brain forms new neural connections throughout life.

| Extension Point | Where to Add | Discovery |
|----------------|-------------|-----------|
| MCP Tools | `cortex/mcp/tools/` | Auto-discovered by MCP server |
| Domain Orchestrators | `cortex/orchestrators/domain/` | Registered in wiring contract |
| Workflow Templates | `cortex-registry/workflows/templates/` | Read by WorkflowEngine |
| Enterprise Patterns | `cortex-registry/patterns/` | Used by Perception tier |
| Knowledge Base | `cortex-registry/knowledge-base/` | Used by intelligence layer |
| Infrastructure Catalog | `cortex-registry/company/` | Platform, API, application definitions |
| Governance Rules | `cortex-registry/core/tier0-skull/` | Enforced by EnforcementOrchestrator |

All extensions are hot-reload — no core code changes required.

### Adding a New MCP Tool

Create a file in `cortex/mcp/tools/`, implement the tool function inheriting from `ConsolidatedTool`, add type hints and a docstring, write a test first per CORE-008, and the MCP server discovers it automatically on next startup.

### Adding a Domain Orchestrator

Create a file in `cortex/orchestrators/domain/`, inherit from `OrchestratorProtocolMixin`, implement `execute_operation()` (cross-cutting hooks for LENS, knowledge synthesis, and governance gates fire automatically), register in the wiring contract, and write tests first per CORE-008.

### Adding Enterprise Patterns

Create a YAML file in `cortex-registry/patterns/` defining pattern signatures, success rates, and associated strategies. The Perception tier picks them up automatically. Current patterns include mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, and command.

---

## 7. Multi-Stack Debugging — The Diagnostic Layer (PLANNED)

CORTEX's debugging capability extends well beyond Python. The `DebuggerOrchestrator` uses a **Strategy Pattern** so that the same inject → capture → analyze → fix-plan → cleanup workflow applies universally to any language or runtime.

**Business Leader:** "When any part of a system breaks — JavaScript UI, REST API, SQL query, or C# service — CORTEX injects traceable markers, captures runtime output, and produces a prioritized fix plan. No manual log trawling."

**Product Owner:** "Eight debugging strategies cover the entire modern stack. Three Python strategies are live today. Five multi-language strategies (JavaScript/TypeScript, HTML/Vision, API tracing, SQL, C#/.NET) are planned."

**Developer:** "Each strategy implements `AbstractInjectionStrategy`. The `MarkerInjectionEngine` selects strategies by detected stack. Markers are unique per session, fully reversible via `AutoCleanupManager`, and emit structured output captured by the analyze phase."

### Strategies (Live + Planned)

| Strategy | Stack | Status |
|----------|-------|--------|
| TestFailureStrategy | Python — pytest/unittest | ✅ Live |
| RefactorRegressionStrategy | Python — refactor sessions | ✅ Live |
| GovernanceViolationStrategy | Python — CORE rule checks | ✅ Live |
| FrontendConsoleStrategy | JavaScript/TypeScript/React/Angular/Vue | ⚪ Planned |
| HtmlVisionMappingStrategy | HTML + Vision API screenshot → DOM | ⚪ Planned |
| ApiTraceStrategy | REST/GraphQL/gRPC middleware | ⚪ Planned |
| SqlTraceStrategy | SQL Server/Oracle/PostgreSQL query plans | ⚪ Planned |
| DotNetTraceStrategy | C#/.NET ILogger entry/exit | ⚪ Planned |

### Commands

| Command | What It Does |
|---------|-------------|
| `/debug {path}` | Full cycle: inject → capture → analyze → fix-plan |
| `/debug-inject {path}` | Insert CORTEX_DEBUG markers only |
| `/debug-cleanup` | Remove all markers, leave code production-ready |

### Unified Intelligence Wiring (PLANNED)

The debug pipeline will also wire `DebuggerOrchestrator` into the cross-cutting intelligence layer it was missing:
- **OPJMixin** — persists debug session outcomes for learning
- **URS signals** — fix rates and time-to-resolve feed the reinforcement loop
- **IntelligenceMatrix cells** (CC-021/IC-021) — debugger becomes queryable by other orchestrators
- **Bidirectional EventBus** — debug insights and fix patterns published to the event mesh
- **KnowledgeSynthesisEngine** — recurring error signatures captured for cross-session knowledge

---

## 8. Response Templates and Orchestrator Engagement (PLANNED)

CORTEX's response format is not cosmetic — it is a governance contract. Every response must follow the canonical template defined in `.github/templates/cortex-response-templates.md`.

**Business Leader:** "Every CORTEX response shows which orchestrators handled the request, how long each step took, and where in the overall journey you are. No black-box responses."

**Product Owner:** "Three engagement visibility tiers ensure developers can see routing without being overwhelmed. The breadcrumb is always visible; the timeline is collapsible; the roadmap appears at the start of long operations."

**Developer:** "Use `BLOCK-ENGAGEMENT-BREADCRUMB` for the routing chain, `BLOCK-ENGAGEMENT-TIMELINE` for collapsible timing, and `BLOCK-PHASE-ROADMAP` for multi-phase overview. Progress bars always use the phase-list+bar format (not bar-only)."

### Engagement Block System (PLANNED)

| Block | When Rendered | Content |
|-------|--------------|---------|
| `BLOCK-ENGAGEMENT-BREADCRUMB` | Every response | `Route: IR → MasterOrchestrator → {Orchestrator}` |
| `BLOCK-ENGAGEMENT-TIMELINE` | Multi-step operations | Collapsible `<details>` with per-orchestrator timing |
| `BLOCK-PHASE-ROADMAP` | Start of `/audit fix`, `/totalrecall`, multi-phase ops | Full phase list with ✅/🔵/⚪ status |

### Progress Format (Canonical)

All progress displays use **phase-list + bar**, not bar-only:

```
⚙️ [████████░░] 80% — Stage 4 of 5

1. ✅ Environment check       (1.2s)
2. ✅ Governance pre-flight   (3.4s)
3. ✅ LENS analysis           (0.8s)
4. 🔵 Wiring validation       (running…)
5. ⚪ Test gate               —
```

**SSOT:** `.github/templates/cortex-response-templates.md` — all orchestrators reference this single file. Never duplicate progress bar rules inline.

---

## 9. RCA Memory Engine — Structured Root Cause Analysis (PLANNED)

The RCA Memory Engine transforms CORTEX's learning system from passive pattern capture into active root-cause prevention. Where the OPJ records *what* failed, the RCA Engine answers *why* — and then ensures it doesn't happen again.

**Business Leader:** "Engineering teams repeat the same class of mistake for years because root cause knowledge is locked inside individual incident reviews and never made institutional. CORTEX's RCA Engine turns every failure into a prevention rule that fires automatically the next time."

**Product Owner:** "RCA is triggered via `cortex_learning` with `op='rca'`. It runs four methodologies (Five Whys, Fishbone, Fault Tree, Causal Chain), persists structured analyses to SQLite, and emits a prevention rule. No new tools, no new orchestrators — purely additive."

**Developer:** "The Prevention Gate watches for signature matches at runtime and warns (or blocks, for 3+ P0 recurrences). Query past analyses via `cortex_learning op='rca' action='query'`."

### Four Analysis Methodologies

| Methodology | Structure | Best For |
|-------------|-----------|----------|
| **Five Whys** | Linear `why → answer` chain | Sequential failures, missing null checks, unhandled exceptions |
| **Fishbone (Ishikawa)** | Category map: People · Process · Technology · Data | Multi-factor failures |
| **Fault Tree** | AND/OR gate probability tree | Complex failures with multiple contributing paths |
| **Causal Chain** | Time-ordered event sequence | Race conditions, async failures, cascade shutdowns |

### Integration Points

| Component | Change |
|-----------|--------|
| `OPJMixin` | `_opj_analyze_rca()` + `_opj_check_prevention_gate()` (2 new methods) |
| `cortex_learning` | New `op="rca"` operation (extends existing tool, no new MCP tool) |
| `CrossSessionPatternCache` | 4 new SQLite tables for RCA persistence |
| URS | P0 recurrences emit `STRONG_PUNISHMENT`; successful prevention emits `STRONG_REWARD` |

---

*All paths and counts verified against live codebase*
