---
title: CORTEX Capabilities
consolidates:
  - 01-capabilities-overview.md
  - 01-capabilities-core-platform.md
  - 01-capabilities-ai-intelligence.md
  - 01-capabilities-decisioning.md
  - 01-capabilities-extensibility.md
last_verified: 2026-02-26
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

The MCP server runs as a Pylance-style stdio process that auto-starts when VS Code opens the workspace. It exposes twenty-eight registered MCP tools (39 target) through JSON-RPC 2.0 transport, requiring no manual server startup and no exposed network ports in development mode.

### Key Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| OrchestratorProtocolMixin | `cortex/core/orchestrator_protocol_mixin.py` | Universal base for all 51 wired orchestrators |
| FileFactory | `cortex/core/file_factory.py` | Canonical file creation with CORE-028 naming enforcement |
| WorkflowEngine | `cortex/core/workflow_engine.py` | Reads workflow YAML templates, executes phase sequences |
| CortexAuditDB | `cortex/infrastructure/audit_db.py` | Unified SQLite with WAL mode for all audit trails |
| MCP Server | `cortex/mcp/` | Pylance-style stdio server, 28 registered tools (39 target) |
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

*All paths and counts verified against live codebase — 26 February 2026*
