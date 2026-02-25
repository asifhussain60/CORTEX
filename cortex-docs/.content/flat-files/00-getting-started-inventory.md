---
title: CORTEX Component Inventory
description: One-stop reference for every orchestrator, MCP tool, LENS analyzer, knowledge YAML, workflow template, and governance rule in CORTEX.
generated: "2026-02-25"
version: "1.2.0"
source: live-scan
render_hint: inventory-page
---

# CORTEX Component Inventory

> **Generated:** 2026-02-25 · **Source:** Live codebase scan · **Version:** 1.2.0  
> One-stop reference for all CORTEX components. Designed to be consumed by HTML renderers in `cortex-docs`.

---

## 1. Orchestrators (27 Wired)

All 27 orchestrators satisfy `IOrchestrator` protocol via `OrchestratorProtocolMixin` (`cortex/core/orchestrator_protocol_mixin.py`). Wiring authority: `cortex-registry/core/specifications/`.

### 1.1 Core Tier (7)

| ID | Class | Path | Description |
|----|-------|------|-------------|
| master | MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` | Top-level coordinator — routes intents, manages 9-stage audit pipeline, wires all orchestrators |
| intent-router | IntentRouter | `cortex/orchestrators/core/intent_router_impl.py` | Classifies user intent and routes to appropriate orchestrator using LENS-aware semantic ranking |
| tdd | TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` | Enforces RED→GREEN→REFACTOR — CORE-008, test-first mandate, golden test validation |
| enforcement | EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` | Pre-commit governance — validates all 35 CORE rules, blocks violations, SQLite audit trail |
| workflow | WorkflowOrchestrator | `cortex/orchestrators/core/workflow_orchestrator.py` | YAML workflow template execution engine — detect-fix-rescan-loop and other primitives |
| conversation | ConversationOrchestrator | `cortex/orchestrators/core/conversation_orchestrator.py` | Multi-turn conversation — state persistence, context aggregation, response streaming |
| audit | AuditOrchestrator | `cortex/orchestrators/core/audit_orchestrator.py` | 19-point production readiness audit — P0/P1/P2 scanning, convergence loop, SQLite logging |

### 1.2 Domain Tier (6)

| ID | Class | Path | Description |
|----|-------|------|-------------|
| planning | PlanningOrchestrator | `cortex/orchestrators/domain/planning_orchestrator.py` | Structured planning — phase decomposition, gap catalogue, TDD sequence generation |
| domain | DomainOrchestrator | `cortex/orchestrators/domain/domain_orchestrator.py` | Domain-specific intelligence — LENS analysis with domain knowledge synthesis |
| refactoring | RefactoringOrchestrator | `cortex/orchestrators/domain/refactoring_orchestrator.py` | Intelligent refactoring — duplication detection, code smell remediation, CORE-035 |
| sdlc | SDLCWorkflowOrchestrator | `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py` | SDLC Intelligence Engine — template selection, knowledge hydration, FSM execution |
| dashboard | DashboardOrchestrator | `cortex/orchestrators/domain/dashboard_orchestrator.py` | Static dashboard generation — landing pages, per-repo dashboards, SQLite-backed metrics |
| enhanced-planning | EnhancedPlanningOrchestrator | `cortex/orchestrators/domain/enhanced_planning_orchestrator.py` | Advanced planning with ROI scoring, wave decomposition, and audit-driven auto-planning |

### 1.3 Support Tier (14)

| ID | Class | Path | Description |
|----|-------|------|-------------|
| health | HealthOrchestrator | `cortex/orchestrators/health/health_orchestrator.py` | All 22 orchestrator health endpoints — filesystem integrity, naming, duplicate detection |
| vacuum | VacuumOrchestrator | `cortex/orchestrators/health/vacuum_orchestrator.py` | Markdown sprawl cleanup — dry-run gate, 30-day retention, CORE-002 enforcement |
| upgrade | UpgradeOrchestrator | `cortex/orchestrators/support/upgrade_orchestrator.py` | Inflight upgrade — validate requirements, fetch origin/main, merge if ahead |
| bulk-digest | BulkDigestOrchestrator | `cortex/orchestrators/support/bulk_digest_orchestrator.py` | Batch content ingestion — 3-pipeline processing (extract, transform, load) |
| digest-session | DigestSessionOrchestrator | `cortex/orchestrators/support/digest_session_orchestrator.py` | Single-session content digestion with LENS analysis and knowledge persistence |
| sweep-catalogue | SweepCatalogueOrchestrator | `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` | CORE-064 sweep completeness — durable issue cataloguing, SQLite WAL persistence |
| setup | SetupOrchestrator | `cortex/orchestrators/support/setup_orchestrator.py` | Environment setup — MCP configuration, VS Code settings, dependency validation |
| onboarding | OnboardingOrchestrator | `cortex/orchestrators/support/orchestrator.py` | Repository onboarding — LENS analysis, security assessment P0/P1/P2, SQLite dashboard |
| repo-onboarding | RepositoryOnboardingOrchestrator | `cortex/orchestrators/support/repository_onboarding_orchestrator.py` | Full repository onboarding with LENS V3 — LLM business language + Phase 21 SQLite |
| debugger | DebuggerOrchestrator | `cortex/orchestrators/support/debugger_orchestrator.py` | Debug session management — log capture, governance violation detection, fix plans |
| cortex-docs | CortexDocsOrchestrator | `cortex/orchestrators/support/cortex_docs_orchestrator.py` | Documentation site orchestration — DOC-REFRESH-001 pipeline, JSON catalog generation |
| plan | PlanOrchestrator | `cortex/orchestrators/support/plan_orchestrator.py` | Plan execution coordinator — phase lifecycle planned→in_progress→complete |
| unified-quality | UnifiedQualityAssuranceOrchestrator | `cortex/orchestrators/support/unified_quality_orchestrator.py` | Unified quality assurance — test, governance, and LENS quality signal aggregation |
| auto-healing | AutoHealingMCPOrchestrator | `cortex/orchestrators/support/auto_healing_mcp_orchestrator.py` | Auto-healing MCP — detects failing tools and applies remediation plans autonomously |

### 1.4 Additional Wired Tiers (Phantom Tier Registrations — Phase 62-D/G)

| Tier | Class | Path | Description |
|------|-------|------|-------------|
| git | GitOrchestrator | `cortex/orchestrators/git/git_orchestrator.py` | Git workflow — commit, branch, merge, diff operations |
| git | GitPublishOrchestrator | `cortex/orchestrators/git/git_publish_orchestrator.py` | Structured commit + push + PR creation workflow |
| git | PreCommitEnforcementOrchestrator | `cortex/orchestrators/git/git_enforcement_orchestrator.py` | Pre-commit CORE rule validation and commit blocking |
| git | SanitizationOrchestrator | `cortex/orchestrators/git/sanitization_orchestrator.py` | Secret scanning, PII removal, branch hygiene |
| validation | HolisticValidationOrchestrator | `cortex/orchestrators/validation/holistic_validation_orchestrator.py` | CORE-048 pre-execution validation gate |
| validation | SOLIDOrchestrator | `cortex/orchestrators/validation/solid_orchestrator.py` | SOLID principles validation — SRP, OCP, LSP compliance |
| validation | SecurityVulnerabilityOrchestrator | `cortex/orchestrators/validation/security_vulnerability_orchestrator.py` | SAST, CVE scanning, remediation handler |
| intelligence | IntelligenceOrchestrator | `cortex/orchestrators/intelligence/intelligence_orchestrator.py` | LENS analysis + brain tier coordination for AI requests |
| synthesis | ContextAwareSynthesis | `cortex/orchestrators/synthesis/context_aware_synthesis.py` | Cross-orchestrator response synthesis and merging |
| workflow | ConvergenceLoopExecutor | `cortex/orchestrators/workflow/convergence_loop_executor.py` | Detect-fix-rescan loop primitive (CORE-064) |
| workflow | AutonomousWorkflowExecutor | `cortex/orchestrators/workflow/autonomous_workflow_executor.py` | Silent autonomous execution engine (CORE-049) |

---

## 2. MCP Tools (39 Total — 37 Active, 2 Deprecated)

Transport: Pylance-style stdio. Auto-starts via `.vscode/settings.json`. Server: `python3 -m cortex.mcp`.

### 2.1 Core & Routing

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_classify | `cortex/mcp/tools/core.py` | Intent classification — routes requests to correct orchestrator pipeline |
| cortex_orchestrator | `cortex/mcp/tools/core.py` | Direct orchestrator invocation — routes to any of the 27 wired orchestrators |
| cortex_request_lifecycle | `cortex/mcp/tools/core.py` | Full request lifecycle — classify → plan → execute → validate |

### 2.2 Governance & Compliance

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_governance | `cortex/mcp/tools/governance.py` | Execute governance actions — enforcement, blocking, remediation with audit logging |
| cortex_load | `cortex/mcp/tools/governance.py` | Load CORE governance rules — skull-rules, core-rules, audit checklist, response format |
| cortex_validate | `cortex/mcp/tools/toolkit/validate.py` | CORE rule compliance validation — op: compliance \| governance \| rules |
| cortex_check | `cortex/mcp/tools/toolkit/validate.py` | Dependency drift detection — checks requirements.txt vs installed packages |

### 2.3 Intelligence & LENS

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_brain_query | `cortex/mcp/tools/brain.py` | Domain brain query — synthesises knowledge from CORTEX's cognitive model |
| cortex_challenge | `cortex/mcp/tools/intelligence.py` | Generate ≥2 alternatives with trade-off analysis using LENS-driven reasoning |
| cortex_intelligence_matrix | `cortex/mcp/tools/intelligence.py` | Cross-cutting intelligence matrix — correlates LENS, governance, and metrics |
| cortex_refactor | `cortex/mcp/tools/intelligence.py` | Semantic refactoring — extract, rename, organize across Python, C#, TypeScript |
| cortex_vision | `cortex/mcp/tools/intelligence.py` | Vision API analysis — UI elements, URLs, issues, and structural mappings |
| cortex_knowledge | `cortex/mcp/tools/operations.py` | Knowledge synthesis from governance YAML registries into actionable insights |
| cortex_total_recall | `cortex/mcp/tools/core.py` | Discover and recall CORTEX features, components, and architecture |

### 2.4 Planning & Audit

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_master_plan | `cortex/mcp/tools/master_plan_tool.py` | Master plan management — cortex-master.yaml operations, phase lifecycle |
| cortex_plan | `cortex/mcp/tools/operations.py` | Structured remediation and project planning with audit-driven decomposition |
| cortex_onboard | `cortex/mcp/tools/onboard_repository.py` | Repository onboarding — LENS analysis, security assessment P0/P1/P2, SQLite dashboard |
| cortex_query_opj | `cortex/mcp/tools/opj_tool.py` | Operational Pattern Journal query — surfaces recurring patterns from execution history |

### 2.5 Testing & Quality

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_generate_tests | `cortex/mcp/tools/test_quality_tool.py` | TDD test generation — produces failing RED tests from specification (CORE-008) |
| cortex_score_tests | `cortex/mcp/tools/test_quality_tool.py` | Test quality gate — scores test suites against CORTEX quality thresholds |

### 2.6 Diagnostics & Health

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_health_scan | `cortex/mcp/tools/health_scan_tool.py` | All 22 orchestrator health endpoints — production readiness validation |
| cortex_verify | `cortex/mcp/tools/toolkit/verify.py` | Verify MCP server health, tool registry, environment, and CORTEX claims |
| cortex_debug | `cortex/mcp/tools/debug_tools.py` | Debug session capture — logs, error analysis, and fix plan generation |
| cortex_ask | `cortex/mcp/tools/core.py` | Educational questions about CORTEX architecture with truth-based verification |
| cortex_metrics | `cortex/mcp/tools/operations.py` | Record and report development metrics — TDD cycles, debug sessions, orchestrator invocations |

### 2.7 Automation & Workflows

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_workflow | `cortex/mcp/tools/workflow_tools.py` | YAML workflow template execution — list, load, and run workflow primitives |
| cortex_list_workflow_templates | `cortex/mcp/tools/list_workflow_templates.py` | List available YAML workflow templates from cortex-registry (Phase 23) |
| cortex_scaffold_files | `cortex/mcp/tools/scaffold_files_tool.py` | Write arbitrary-language source files to disk with governance validation |

### 2.8 Maintenance & Cleanup

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_vacuum | `cortex/mcp/tools/operations.py` | Markdown sprawl cleanup — archives stale files, removes root clutter (CORE-002) |
| cortex_vacuum_execute | `cortex/mcp/tools/vacuum_execute_tool.py` | Full lifecycle vacuum — kill processes, health check, launch |

### 2.9 VCS (Git)

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_git | `cortex/mcp/tools/git_orchestrator_tool.py` | Git operations — branching, committing, conflict resolution via GitOrchestrator |

### 2.10 Documentation

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_dashboard | `cortex/mcp/tools/operations.py` | Generate static dashboard suite — landing page + per-repo dashboards with embedded data |
| cortex_tools_catalog | `cortex/mcp/tools/core.py` | Discover all 39 MCP tools (37 active) with category and description |

### 2.11 Toolkit / Bulk Operations

| Tool ID | File | Description |
|---------|------|-------------|
| cortex_batch_transform | `cortex/mcp/tools/toolkit/analyze.py` | Batch data transformation across a collection |
| cortex_enrich | `cortex/mcp/tools/utilities.py` | Content enrichment — adds metadata and context to structured data |
| cortex_scan | `cortex/mcp/tools/toolkit/analyze.py` | Workspace scan — discovers files, patterns, and structures |
| cortex_bulk_digest_files | `cortex/mcp/tools/bulk_digest.py` | Bulk file digest — batch ingestion across 3 pipelines |
| cortex_sweep_status | `cortex/mcp/tools/sweep_status_tool.py` | Sweep catalogue status — CORE-064 completeness tracking |

### 2.12 Deprecated

| Tool ID | Replacement |
|---------|-------------|
| cortex_process_request | `cortex_request_lifecycle` |
| cortex_validate_request | `cortex_validate` |

---

## 3. LENS Analysis System

**Location:** `cortex/lens/`  
**Pipeline:** Language → Examination → Navigation → Synthesis

### 3.1 Language Adapters

| Adapter | File | Languages |
|---------|------|-----------|
| PythonAdapter | `cortex/lens/analyzers/python_analyzer.py` | Python 3.x |
| CSharpAdapter | `cortex/lens/adapters/csharp_adapter.py` | C# / .NET |
| TypeScriptAdapter | `cortex/lens/adapters/typescript_adapter.py` | TypeScript / JavaScript |
| JavaScriptAdapter | `cortex/lens/adapters/javascript_adapter.py` | JavaScript (legacy) |
| JavaAdapter | `cortex/lens/adapters/java_adapter.py` | Java |
| DotNetAnalyzer | `cortex/lens/dotnet_analyzer.py` | .NET solution-level |
| PolyglotAnalyzer | `cortex/lens/analyzers/polyglot_analyzer.py` | Multi-language repos |

### 3.2 Core Analyzers

| Analyzer | File | Purpose |
|----------|------|---------|
| ASTAnalyzer | `cortex/lens/analyzers/ast_analyzer.py` | Abstract syntax tree parsing and symbol extraction |
| DependencyAnalyzer | `cortex/lens/analyzers/dependency_analyzer.py` | Package dependency graph and drift detection |
| TechStackAnalyzer | `cortex/lens/analyzers/tech_stack_analyzer.py` | Tech stack fingerprinting and version detection |
| GitHistoryAnalyzer | `cortex/lens/analyzers/git_history_analyzer.py` | Commit history, change frequency, hotspot detection |
| APIAnalyzer | `cortex/lens/analyzers/api_analyzer.py` | REST/gRPC/GraphQL endpoint discovery |
| DatabaseAnalyzer | `cortex/lens/analyzers/database_analyzer.py` | ORM models, migration files, schema analysis |
| ConfigAnalyzer | `cortex/lens/analyzers/config_analyzer.py` | Configuration file scanning and secrets detection |
| EvolutionAnalyzer | `cortex/lens/analyzers/evolution_analyzer.py` | Codebase evolution tracking and trend analysis |
| VendorDetector | `cortex/lens/analyzers/vendor_detector.py` | Third-party library and vendor dependency detection |
| VisionAnalyzer | `cortex/lens/analysis/vision_analyzer.py` | UI screenshot analysis via Vision API |

### 3.3 Discovery Modules

| Module | File | Purpose |
|--------|------|---------|
| APIDiscovery | `cortex/lens/discovery/api_discovery.py` | Automatic REST/gRPC API mapping |
| DatabaseDiscovery | `cortex/lens/discovery/database_discovery.py` | Database schema and migration discovery |
| MicroservicesDiscovery | `cortex/lens/discovery/microservices_discovery.py` | Service topology and inter-service dependency mapping |
| SecurityDiscovery | `cortex/lens/discovery/security_discovery.py` | Vulnerability surface and security control discovery |
| TestingDiscovery | `cortex/lens/discovery/testing_discovery.py` | Test coverage gaps and test framework detection |
| ConfigDiscovery | `cortex/lens/discovery/config_discovery.py` | Configuration drift and environment variable mapping |

### 3.4 Cache Layer

| Component | File | Backend |
|-----------|------|---------|
| LensCache | `cortex/lens/cache/lens_cache.py` | Pluggable cache (memory or Redis) |
| MemoryBackend | `cortex/lens/cache/memory_backend.py` | In-process LRU cache |
| RedisBackend | `cortex/lens/cache/redis_backend.py` | Distributed Redis cache |
| CacheKeyBuilder | `cortex/lens/cache/cache_key_builder.py` | Deterministic cache key generation |

### 3.5 ML Pattern Recognition

| Component | File | Purpose |
|-----------|------|---------|
| PatternEmbedder | `cortex/lens/ml_patterns/pattern_embedder.py` | Embed code patterns for similarity search |
| RepositoryFingerprinting | `cortex/lens/ml_patterns/repository_fingerprinting.py` | Unique repo signature for cross-repo learning |
| SimilarityClustering | `cortex/lens/ml_patterns/similarity_clustering.py` | Cluster similar code patterns across files |

---

## 4. Governance Rules (35 CORE Active)

**Authority:** `cortex-registry/core/tier0-skull/skull-rules.yaml` (Tier 0 — immutable, highest precedence)

### 4.1 Tier 0 — Skull Rules (Immutable)

| Rule ID | Principle | Category | Description |
|---------|-----------|----------|-------------|
| CORE-001 | Flywheel Effect | orchestration_lifecycle | All orchestrators work in <500 line increments; state persists between turns |
| CORE-002 | Signal vs Noise | response_formatting | Suppress markdown reports unless explicitly requested; zero inline `style=` |
| CORE-004 | Clarity Through Brevity | response_formatting | Continuation prompts <500 tokens, ≤12 lines |
| CORE-005 | Write Once, Run Anywhere | portability | Never hardcode absolute paths; use `path_resolver` |
| CORE-006 | Fail Fast on Configuration Errors | development_workflow | Verify all dependencies before execution |
| CORE-008 | Red-Green-Refactor Discipline | development_workflow | Tests MUST exist before implementation — no exceptions |
| CORE-011 | Documentation as Code | development_workflow | All Python functions must have complete type hints |
| CORE-012 | Self-Documenting Systems | development_workflow | All public functions/classes must have Google-style docstrings |
| CORE-013 | Make Errors First-Class Citizens | development_workflow | No bare `except`; no catching generic `Exception` |
| CORE-017 | Culture of Discipline | governance | All rules enforced strictly; no overrides; all violations logged |
| CORE-018 | Machine-Readable First | architecture_integrity | Plans and configs use YAML not markdown |
| CORE-019 | Hedgehog Concept | orchestration_lifecycle | All implementation requests route to TDD-Master orchestrator |
| CORE-020 | Convention Over Configuration | architecture_integrity | `cortex/intelligence/` must be YAML/JSON only |
| CORE-024 | Right Tool for the Job | architecture_integrity | All MCP tools must use `@mcp_tool` decorator for registration |
| CORE-025 | Fail Fast, Fail Explicitly | development_workflow | Functions must return `Result[T]` for explicit error handling |
| CORE-026 | Always Have an Escape Route | auditability | Git checkpoint before every major action |
| CORE-027 | Radical Transparency | auditability | Phase completion validated by audit trail verification |
| CORE-028 | A Place for Everything | architecture_integrity | File naming: snake_case Python, kebab-case YAML/HTML/CSS |
| CORE-029 | Code Tells How, Docs Tell Why | response_formatting | User-facing features documented in prompts before phase close |
| CORE-030 | Trust But Verify | auditability | Validate claims against actual code before answering |
| CORE-031 | One Source of Truth | architecture_integrity | Declarative autowiring via wiring specs — no ad-hoc registration |
| CORE-032 | Clear Hierarchy Eliminates Confusion | orchestration_lifecycle | Every operation classified BEFORE execution |
| CORE-034 | Confront Brutal Facts | auditability | All operations log to AuditLogger |
| CORE-035 | Single Standard: Production | architecture_integrity | Each concept has exactly ONE canonical implementation |
| CORE-038 | Prevention Over Cure | architecture_integrity | All files stored in appropriate canonical directories |
| CORE-039 | Proactive Governance | response_formatting | Eliminate automatic MD file generation at phase end |
| CORE-040 | Design for Decay | architecture_integrity | Prevent documentation bloat via lifecycle management |
| CORE-041 | Same Input, Same Output | development_workflow | All event handlers must be idempotent |
| CORE-042 | Separation of Concerns | architecture_integrity | Planning responses use standardized 4-level hierarchy |
| CORE-048 | Built-In Quality | quality_gates | Holistic validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Graceful Degradation with Transparency | orchestration_lifecycle | Silent autonomous execution — progress bars only (CORE-049) |
| CORE-050 | Intelligence Depth Matches Tier | architecture_integrity | Never accept degraded execution or bypass MCP tools |
| CORE-051–054 | Make Invalid States Unrepresentable | quality_gates | AC marker AC_START/AC_COMPLETE integrity contracts |
| CORE-055 | Golden Test Tier Contract | quality_gates | Golden test paths defined by `GOLDEN_PATHS` constant |
| CORE-064 | No Partial Sweeps | quality_gates | Every FIX/REFACTOR/AUDIT must exhaust its full issue catalogue |
| CORE-065 | Measure What Matters | auditability | Pre-work snapshot persisted to SQLite; VS Code Copilot session tracking |
| CORE-066 | Holistic Duplicate Detection Prevention | architecture_integrity | Detect and prevent duplicate component registration |

### 4.2 Supporting Governance Files

| File | Purpose |
|------|---------|
| `cortex-registry/core/tier1-project/project-rules.yaml` | Project-level constraints (CORE-008, CORE-011, CORE-012, CORE-013) |
| `cortex-registry/core/tier2-engineering/engineering-standards.yaml` | Engineering standards (CORE-051) |
| `cortex-registry/core/governance/skull-rules.yaml` | Mirror + governance kernel config |
| `cortex-registry/core/governance/governance-kernel.yaml` | Runtime kernel config for enforcement |
| `cortex-registry/core/governance/violation_patterns.yaml` | Violation pattern registry for auto-detection |
| `cortex-registry/core/governance/duplicate_detection_schedule.yaml` | Scheduled duplicate scan policy |
| `cortex-registry/core/wiring/autonomous-execution-protocol.yaml` | CORE-049 execution protocol |
| `cortex-registry/core/wiring/quality-gate-specification.yaml` | Quality gate thresholds |
| `cortex-registry/core/wiring/mcp-priority-policy.yaml` | MCP tool priority resolution policy |
| `cortex-registry/core/wiring/neural-routing-specification.yaml` | Neural routing weights and fallback rules |

---

## 5. Knowledge YAML Registry (35+ Files)

**Location:** `cortex-registry/knowledge/`  
**Index:** `cortex-registry/knowledge/INDEX.yaml`

### 5.1 Architecture

| File | Topics |
|------|--------|
| `architecture/engineering-design-patterns.yaml` | GoF patterns, CQRS, Event Sourcing, Saga, Outbox |
| `architecture/engineering-anti-patterns.yaml` | Big Ball of Mud, God Object, Lava Flow, Cargo Cult |
| `architecture/engineering-solid-principles.yaml` | SRP, OCP, LSP, ISP, DIP with C# and Python examples |
| `architecture/refactoring-quality-standards.yaml` | Quality gates, refactoring thresholds, complexity limits |

### 5.2 Backend / Python

| File | Topics |
|------|--------|
| `backend-python/clean-code.yaml` | Naming, functions, classes, error handling, Pythonic patterns |
| `backend-python/code-review.yaml` | Code review checklist, reviewer guidelines, PR standards |
| `backend-python/refactoring.yaml` | Extract method, rename, move, simplify conditionals |

### 5.3 Migration Playbooks (12 Tracks)

| File | Migration Track |
|------|----------------|
| `migration/angularjs-to-angular.yaml` | AngularJS → Angular 17+ |
| `migration/aspnet-to-aspnet-core.yaml` | ASP.NET Framework → ASP.NET Core |
| `migration/dotnet-framework-to-dotnet8.yaml` | .NET Framework → .NET 8 |
| `migration/ef-to-efcore.yaml` | Entity Framework → EF Core |
| `migration/javascript-to-typescript.yaml` | JavaScript → TypeScript strict mode |
| `migration/jquery-to-modern-framework.yaml` | jQuery → React / Angular / Vue |
| `migration/monolith-to-microservices.yaml` | Monolith decomposition strategies |
| `migration/onprem-to-cloud.yaml` | On-premises → Azure cloud migration |
| `migration/selenium-to-playwright.yaml` | Selenium → Playwright E2E testing |
| `migration/soap-to-rest.yaml` | SOAP/WCF → REST API |
| `migration/sql-to-nosql.yaml` | SQL → NoSQL / MongoDB |
| `migration/wcf-to-api-microservice.yaml` | WCF services → API microservices |

### 5.4 SDLC Intelligence

| File | Topics |
|------|--------|
| `sdlc/analysis-design-patterns.yaml` | Requirements analysis, design pattern selection |
| `sdlc/code-review-checklist.yaml` | Multi-tier code review process |
| `sdlc/documentation-strategy.yaml` | Living documentation, ADRs, C4 diagrams |
| `sdlc/integration-strategy.yaml` | CI/CD integration patterns |
| `sdlc/security-by-design.yaml` | OWASP, threat modelling, secure defaults |
| `sdlc/test-strategy-selection.yaml` | Test pyramid, TDD vs BDD, E2E gate |

### 5.5 Stack-Specific

| File | Stack |
|------|-------|
| `sdlc/stack-specific/dotnet-stack.yaml` | .NET 8 / ASP.NET Core / EF Core |
| `sdlc/stack-specific/html-css-stack.yaml` | HTML5 / CSS3 / Web Components |
| `sdlc/stack-specific/python-stack.yaml` | Python 3.x / FastAPI / pytest |
| `sdlc/stack-specific/typescript-stack.yaml` | TypeScript / Angular / RxJS |

### 5.6 Security, DevOps, Performance, Best Practices, Testing

| File | Domain |
|------|--------|
| `security/secure-coding-practices.yaml` | Input validation, auth patterns, secrets management |
| `devops-infrastructure/monitoring-observability.yaml` | Prometheus, Grafana, OpenTelemetry |
| `performance-optimization/profiling-analysis.yaml` | CPU/memory profiling, bottleneck detection |
| `best-practices/technical/success-patterns.yaml` | Proven success patterns across CORTEX engagements |
| `best-practices/technical/failure-patterns.yaml` | Failure postmortems and lessons learned |
| `testing-validation/tdd-best-practices.yaml` | TDD cycle mastery, mocking strategy, test isolation |

---

## 6. Workflow Templates (60+ Templates)

**Location:** `cortex-registry/workflows/templates/`  
**Consumed by:** `SDLCWorkflowOrchestrator`, `cortex_workflow` (MCP), `cortex_list_workflow_templates` (MCP)

### 6.1 Audit

| Template | Path | Purpose |
|----------|------|---------|
| audit-fix-pipeline | `audit/audit-fix-pipeline.yaml` | 9-stage production readiness pipeline (canonical `/audit fix`) |

### 6.2 Backend

| Template | Path | Purpose |
|----------|------|---------|
| csharp-refactor-workflow | `backend/csharp-refactor-workflow.yaml` | C# codebase refactoring pipeline |
| csharp-security-workflow | `backend/csharp-security-workflow.yaml` | C# security hardening workflow |

### 6.3 Frontend

| Template | Path | Purpose |
|----------|------|---------|
| css-extraction-workflow | `frontend/css-extraction-workflow.yaml` | Inline style → CSS class extraction |
| css-zero-inline-workflow | `frontend/css-zero-inline-workflow.yaml` | CORE-002 zero-inline-style enforcement |
| html-refactor-validation | `frontend/html-refactor-validation.yaml` | HTML structural validation |
| typescript-refactor-workflow | `frontend/typescript-refactor-workflow.yaml` | TypeScript refactoring pipeline |

### 6.4 Governance

| Template | Path | Purpose |
|----------|------|---------|
| master-plan-phase-lifecycle | `governance/master-plan-phase-lifecycle.yaml` | THIN INDEX CONTRACT — phase create → complete lifecycle |
| golden-test-promotion | `governance/golden-test-promotion.yaml` | Test promotion from STANDARD → GOLDEN tier |
| holistic-file-review-gate | `governance/holistic-file-review-gate.yaml` | CORE-048 holistic validation gate |
| request-execution-plan-gate | `governance/request-execution-plan-gate.yaml` | DoR gate before execution |

### 6.5 SDLC

| Template | Path | Purpose |
|----------|------|---------|
| requirements-analysis | `sdlc/requirements-analysis.yaml` | Structured requirements capture |
| solution-design | `sdlc/solution-design.yaml` | Architecture design session |
| implementation-execution | `sdlc/implementation-execution.yaml` | TDD implementation workflow |
| code-review-gate | `sdlc/code-review-gate.yaml` | Multi-tier code review pipeline |
| integration-verification | `sdlc/integration-verification.yaml` | Integration test and verification |
| release-readiness | `sdlc/release-readiness.yaml` | Production release checklist |
| security-assessment | `sdlc/security-assessment.yaml` | Security scan and remediation |

### 6.6 TDD

| Template | Path | Purpose |
|----------|------|---------|
| tdd-feature-implementation | `tdd/tdd-feature-implementation.yaml` | Full RED→GREEN→REFACTOR cycle |
| tdd-api-service | `tdd/tdd-api-service.yaml` | API service TDD pipeline |
| tdd-frontend-visual | `tdd/tdd-frontend-visual.yaml` | Frontend visual component TDD |
| frontend-tdd-workflow | `tdd/frontend-tdd-workflow.yaml` | End-to-end frontend TDD |
| test-strategy-matrix | `tdd/test-strategy-matrix.yaml` | Test strategy selection matrix |

### 6.7 Security

| Template | Path | Purpose |
|----------|------|---------|
| security-hardening | `security/security-hardening.yaml` | Security hardening pipeline |
| security-compliance-audit | `security/security-compliance-audit.yaml` | Compliance audit (OWASP, CWE) |
| threat-model-analysis | `security/threat-model-analysis.yaml` | Structured threat modelling |

### 6.8 Quality

| Template | Path | Purpose |
|----------|------|---------|
| quality-uplift | `quality/quality-uplift.yaml` | Full quality uplift pipeline |
| quality-code-uplift | `quality/quality-code-uplift.yaml` | Code-specific quality gates |
| refactor-holistic-sweep | `quality/refactor-holistic-sweep.yaml` | CORE-064 holistic refactor sweep |
| duplicate-validation | `quality/duplicate-validation.yaml` | CORE-035 duplicate detection |

### 6.9 Lifecycle

| Template | Path | Purpose |
|----------|------|---------|
| migration-modernize | `lifecycle/migration-modernize.yaml` | Legacy codebase modernization |
| onboarding-repo-setup | `lifecycle/onboarding-repo-setup.yaml` | Repository onboarding setup |
| service-decomposition-workflow | `lifecycle/service-decomposition-workflow.yaml` | Monolith → microservices |
| legacy-rescue | `lifecycle/legacy-rescue.yaml` | Legacy codebase rescue pipeline |
| master-plan-execution | `lifecycle/master-plan-execution.yaml` | Master plan execution coordinator |

### 6.10 Maintenance

| Template | Path | Purpose |
|----------|------|---------|
| health-vacuum-unified-pipeline | `maintenance/health-vacuum-unified-pipeline.yaml` | Health + vacuum unified run |
| cleanup-deduplication | `maintenance/cleanup-deduplication.yaml` | Filesystem deduplication |
| doc-flat-file-sync | `maintenance/doc-flat-file-sync.yaml` | Documentation sync pipeline |

### 6.11 Primitives (Building Blocks)

| Primitive | Path | Purpose |
|-----------|------|---------|
| lens-ast-scan | `primitives/analysis/lens-ast-scan.yaml` | LENS AST analysis primitive |
| lens-vision-scan | `primitives/analysis/lens-vision-scan.yaml` | Vision analysis primitive |
| audit-trace | `primitives/execution/audit-trace.yaml` | AC_START/AC_COMPLETE emission |
| semantic-edit | `primitives/execution/semantic-edit.yaml` | Targeted semantic file edit |
| file-extraction | `primitives/execution/file-extraction.yaml` | Safe file extraction primitive |
| detect-fix-rescan-loop | `primitives/validation/detect-fix-rescan-loop.yaml` | CORE-064 convergence loop |
| css-zero-inline | `primitives/validation/css-zero-inline.yaml` | Inline style gate primitive |
| dom-validation | `primitives/validation/dom-validation.yaml` | HTML DOM structural validation |
| duplicate-detection | `primitives/validation/duplicate-detection.yaml` | CORE-035 duplicate check |
| regression-test | `primitives/validation/regression-test.yaml` | Regression test gate primitive |
| sweep-catalogue-open | `primitives/governance/sweep-catalogue-open.yaml` | Open CORE-064 sweep catalogue |
| sweep-catalogue-close | `primitives/governance/sweep-catalogue-close.yaml` | Close and assert exhaustion |
| intelligence-injection | `primitives/intelligence/intelligence-injection.yaml` | Inject LENS context into workflow |
| master-plan-decomposition-check | `primitives/validation/master-plan-decomposition-check.yaml` | THIN INDEX CONTRACT gate |
| dependency-guard-migration | `primitives/governance/dependency-guard-migration.yaml` | Dependency guard for migrations |

---

## 7. Core Framework Components

**Package root:** `cortex/`

### 7.1 Base Classes & Protocols

| Component | File | Purpose |
|-----------|------|---------|
| OrchestratorProtocolMixin | `cortex/core/orchestrator_protocol_mixin.py` | Primary base — all 27 wired orchestrators (Phase 58) |
| OrchestratorBase | `cortex/core/orchestrator_base.py` | Legacy base — 2 orchestrators only |
| IOrchestrator | `cortex/core/interfaces/i_orchestrator.py` | Protocol interface for all orchestrators |
| FileFactory | `cortex/core/file_factory.py` | Canonical file creation with CORE-028 validation |
| WorkflowEngine | `cortex/core/workflow_engine.py` | YAML workflow template execution engine |
| ScaffoldWriter | `cortex/core/scaffold_writer.py` | Structured file scaffolding with governance |

### 7.2 Wiring & Registry

| Component | File | Purpose |
|-----------|------|---------|
| WiringBootstrap | `cortex/core/wiring/wiring_bootstrap.py` | Bootstraps all 27 wired orchestrators at startup |
| OrchestratorFactory | `cortex/core/wiring/orchestrator_factory.py` | Lazy-loaded orchestrator instantiation |
| RegistryBackedOrchestratorRegistry | `cortex/core/wiring/registry_backed_orchestrator_registry.py` | Git-backed orchestrator registry |
| DependencyInjection | `cortex/core/wiring/dependency_injection.py` | DI container for orchestrator dependencies |
| UnifiedRegistry | `cortex/core/registry/unified_registry.py` | Single registry for all CORTEX components |
| PlanRegistry | `cortex/core/registry/plan_registry.py` | Phase plan registry backed by YAML |

### 7.3 Knowledge System

| Component | File | Purpose |
|-----------|------|---------|
| UnifiedKnowledgeService | `cortex/core/knowledge/unified_service.py` | Unified knowledge query entry point |
| KnowledgeRepository | `cortex/core/knowledge/knowledge_repository.py` | YAML-backed knowledge persistence |
| KnowledgeGraph | `cortex/core/knowledge/knowledge_graph.py` | SQLite-backed knowledge graph |
| IngestionPipeline | `cortex/core/knowledge/ingestion_pipeline.py` | 3-stage knowledge ingestion |
| BulkIngestion | `cortex/core/knowledge/bulk_ingestion.py` | Batch YAML knowledge loading |
| CompanyKnowledgeLoader | `cortex/core/knowledge/company_knowledge_loader.py` | Company-specific domain knowledge |

### 7.4 Intelligence

| Component | File | Purpose |
|-----------|------|---------|
| IntelligenceProvider | `cortex/intelligence/base.py` | Base intelligence provider protocol |
| IntelligenceRoutingEngine | `cortex/core/intelligence_routing_engine.py` | Routes intelligence requests to correct provider |
| MLSummarizer | `cortex/core/ml_summarizer.py` | ML-based content summarization |
| CapabilityMatcher | `cortex/intelligence/capability_matcher.py` | Matches orchestrator capabilities to intents |
| CallGraphAnalyzer | `cortex/intelligence/call_graph.py` | Python call-graph analysis for LENS |

### 7.5 Governance Runtime

| Component | File | Purpose |
|-----------|------|---------|
| GovernanceAuditor | `cortex/governance/governance_auditor.py` | Runtime CORE rule enforcement |
| ViolationScanner | `cortex/governance/violation_scanner.py` | Pattern-based violation scanner |
| RuleWeightCalculator | `cortex/governance/rule_weight_calculator.py` | Weighted severity scoring for rules |
| GovernanceDatabase | `cortex/core/governance_database.py` | SQLite-backed governance state |
| AuditIntelligence | `cortex/governance/audit_intelligence.py` | AI-driven audit pattern detection |
| ResponseTemplateValidator | `cortex/governance/response_template_validator.py` | Validates response format compliance (CORE-029) |

### 7.6 MCP Server

| Component | File | Purpose |
|-----------|------|---------|
| MCP Server entry | `cortex/mcp/__init__.py` | Stdio transport server (Pylance-style) |
| MCPShared | `cortex/mcp/tools/_shared.py` | Shared utilities and `validate_orchestrator_context` guard |
| ToolHelpers | `cortex/mcp/tools/tool_helpers.py` | Common tool helper functions |

### 7.7 Testing Framework

| Component | File | Purpose |
|-----------|------|---------|
| CortexXdistPlugin | `cortex/testing/framework/` | Parallel test runner — `pytest-xdist` integration |
| Parallel Test Runner | `scripts/run_tests.py` | Cross-platform: smoke, unit, integration, golden, batch modes |
| TestQualityGate | `cortex-registry/core/test-quality-gate.yaml` | Test scoring thresholds (score ≥ 4 required) |

---

## 8. Testing Suite

| Metric | Value |
|--------|-------|
| Total test files | 994 |
| Golden test files | 91 |
| Test collection baseline | 8,688 collected (Phase 25 baseline) |
| Parallel runner | `pytest-xdist` (`-n auto --dist loadscope`) |
| Batch size | 500 tests/batch (`CORTEX_BATCH_SIZE=500`) |

### 8.1 Test Tiers

| Tier | Directory | Characteristics |
|------|-----------|-----------------|
| GOLDEN | `tests/golden/` | Truth-pinned, immutable, first to run |
| PHASE | `tests/orchestrators/` (phase-tagged) | Phase-specific acceptance tests |
| UNIT | `tests/core/`, `tests/governance/`, etc. | Fast, isolated, no I/O |
| INTEGRATION | `tests/integration/` | Cross-module, real dependencies |
| REGRESSION | `tests/regression/` | Prevent past bugs from resurfacing |

### 8.2 Run Commands

| Command | Mode |
|---------|------|
| `make test-smoke` | Fast smoke gate |
| `make test-batch` | Full batch (canonical) |
| `make test-all` | All tests including ignored |
| `python3 scripts/run_tests.py batch` | Cross-platform batch |
| `python3 scripts/run_tests.py golden` | Golden tier only |

---

## 9. Runtime Data & Persistence

**Canonical location:** `.cortex-runtime/`

| Path | Purpose |
|------|---------|
| `.cortex-runtime/traces/orchestrator-traces.db` | SQLite: audit_sessions, audit_stage_log, audit_violations, workflow_cycles, workflow_runs |
| `.cortex-runtime/sweeps/{sweep_id}.db` | SQLite WAL: sweep catalogue per CORE-064 session |
| `.cortex-runtime/traces/upgrade-manifest.json` | Inflight upgrade state |

### 9.1 SQLite Schema (orchestrator-traces.db)

| Table | Purpose |
|-------|---------|
| `audit_sessions` | 1 row per `/audit fix` run |
| `audit_stage_log` | 1 row per pipeline stage |
| `audit_violations` | 1 row per violation (P0/P1/P2) |
| `workflow_cycles` | 1 row per detect-fix-rescan iteration |
| `workflow_runs` | 1 row per convergence loop invocation |

---

## 10. Configuration Files

| File | Purpose |
|------|---------|
| `.vscode/settings.json` | MCP server config (`github.copilot.chat.mcpServers.cortex`) |
| `pytest.ini` | Canonical test config (`-n auto --dist loadscope`, xdist) |
| `pyproject.toml` | Package metadata and tool config |
| `requirements.txt` | Production dependencies |
| `Makefile` | Task shortcuts (`test-batch`, `test-smoke`, `test-all`) |
| `cortex-registry/core/config/system-configuration.yaml` | System-wide CORTEX config |
| `cortex-registry/core/config/feature-flags.yaml` | Feature flag registry |
| `cortex-registry/core/config/file-naming-rules.yaml` | CORE-028 naming conventions |
| `cortex-registry/core/specifications/` | 4 wiring specs (master, core, domain, support) |

---

## 11. Documentation Site (cortex-docs)

**Type:** Static HTML/CSS/JS — no build framework.  
**Data layer:** `cortex-docs/data/*.json` (consumed by JS renderers).

| File / Dir | Purpose |
|-----------|---------|
| `cortex-docs/index.html` | Role selector — 4 personas (Engineer, Leader, Product, Learner) |
| `cortex-docs/roles/software-engineer.html` | Engineer persona page |
| `cortex-docs/roles/business-leader.html` | Business leader persona page |
| `cortex-docs/roles/product-owner.html` | Product owner persona page |
| `cortex-docs/roles/learner.html` | Curious learner persona page |
| `cortex-docs/learning/` | Learning track pages (beginner/intermediate/advanced) |
| `cortex-docs/data/orchestrators.json` | Orchestrator catalog (v1.1.0 — 27 entries) |
| `cortex-docs/data/mcp-tools.json` | MCP tool catalog (v1.1.0 — 39 entries) |
| `cortex-docs/data/knowledge-catalog.json` | Knowledge domain catalog (v1.1.0 — 34 domains, 32 tech stacks) |
| `cortex-docs/data/learning-paths.json` | Learning track metadata |
| `cortex-docs/data/content.json` | Extracted markdown content |
| `cortex-docs/assets/css/intentional-classes.css` | CORE-002 CSS class registry (zero inline styles) |
| `cortex-docs/pipeline/discover.py` | Discovery pipeline script |
| `cortex-docs/pipeline/build.py` | Static site build script |
| `cortex-docs/pipeline/validate.py` | Quality gate validator |
| `cortex-docs/.content/` | Markdown source for content extraction |

---

## 12. Summary Metrics

| Metric | Value |
|--------|-------|
| Wired Orchestrators | 27 (7 core · 6 domain · 14 support) |
| Active MCP Tools | 37 (39 total, 2 deprecated) |
| CORE Governance Rules | 35 active (Tier 0 skull-rules) |
| LENS Analyzers | 10 core + 7 adapters |
| Knowledge YAML Files | 35+ across 9 domains |
| Workflow Templates | 60+ across 12 categories |
| Test Files | 994 (91 golden) |
| Package Directories | 16 canonical under `cortex/` |
| Orchestrator Tiers (extended) | 10 (core, domain, support, git, health, intelligence, strategies, synthesis, validation, workflow) |
| Knowledge Tech Stacks | 32 |

---

*Inventory generated from live codebase scan. Wiring authority: `cortex-registry/core/specifications/`. Governance authority: `cortex-registry/core/tier0-skull/skull-rules.yaml`.*
