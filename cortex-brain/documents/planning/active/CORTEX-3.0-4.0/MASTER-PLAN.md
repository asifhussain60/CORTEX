# CORTEX 3.0 → 4.0 Migration Master Plan

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 17, 2025  
**Status:** 🟡 AWAITING APPROVAL  
**Branch Strategy:** CORTEX-3.0 (source) → CORTEX-4.0 (target)

---

## 📋 Executive Summary

Comprehensive migration plan to transform CORTEX from current 3.0 architecture to next-generation 4.0 system with:

- **MCP Server Architecture** - Pluggable tool ecosystem replacing hardcoded wrappers
- **Enhanced Brain** - Hybrid centralization (SQLite + shared templates)
- **Bloat Reduction** - Permanent wiring via dependency injection, eliminate manifest bloat
- **Clean Orchestrator Structure** - Co-located tests, TDD-first development
- **Unified Operations** - Consolidate 28+ orchestrators into 13 total (11 core + 2 specialized)
- **Agent Integration** - Streamline 18 agents into 12 active (7 independent + 4 brain integrations + 1 deprecated)
- **Technical Documentation System** - Auto-generated docs with 60+ interactive D3.js diagrams

**Timeline:** 18 weeks (4.5 months including Phase 0 cleanup + documentation)  
**Risk Level:** 🟡 MEDIUM  
**Test Coverage Target:** 85%+ all orchestrators  
**Documentation Target:** 200+ technical documents with 60+ interactive D3.js diagrams  

**Architecture References:**
- **Planning Orchestrator Redesign** - See analysis in `.github/copilot/copilot-chats/chat01.md`
- **TDD Mastery Orchestrator Redesign** - See `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/TDD-ORCHESTRATOR-REDESIGN.md`

**Critical Path to First Orchestrator Migration:**
1. **Week 0:** Phase 0 cleanup + technical documentation structure setup
2. **Weeks 1-3:** Phase 1 foundation (10 prerequisites MUST be complete)
3. **Week 3 End:** Run validation script - MUST pass before Phase 3
4. **Week 7:** Begin orchestrator migration (ExecutionOrchestrator first, TDD second with redesign)

**Key Phases:**
- **Phase 0 (Week 0):** Pre-Migration Cleanup - Eliminate bloat + Technical documentation structure  
- **Phase 1 (Weeks 1-3):** Foundation - Base orchestrator, brain, DI, templates, testing (CRITICAL)
- **Phase 1.5 (Week 3):** Documentation & Visualization Framework - Auto-generation tool  
- **Phase 2 (Weeks 4-6):** Brain Enhancement - Hybrid centralization
- **Phase 3 (Weeks 7-11):** Orchestrator Consolidation - Migrate 13 orchestrators (11 core + 2 specialized) (requires Phase 1 complete)
- **Phase 4 (Weeks 12-14):** Operations Simplification - DI container and manifest reduction
- **Phase 5 (Weeks 15-17):** Testing & Validation - Comprehensive testing and quality gates
- **Phase 6 (Week 18):** Documentation Finalization - Complete technical documentation generation  

---

## 🚨 CRITICAL: Foundation Prerequisites Summary

**Before ANY orchestrator can be migrated, these 10 components MUST be complete on CORTEX-4.0 branch:**

1. ✅ **Branch Setup** - CORTEX-4.0 branch with new directory structure
2. ✅ **Base Orchestrator Framework** - BaseOrchestrator, PhaseManager, ErrorHandler (3 classes)
3. ✅ **Brain Tiers** - All 4 tiers migrated with BrainInterface
4. ✅ **Response Template System** - TemplateManager + templates migrated
5. ✅ **Configuration System** - cortex.config.json updated + ConfigManager
6. ✅ **Testing Infrastructure** - pytest + fixtures + conftest.py (CORTEX INTERNAL TESTS ONLY)
7. ✅ **Dependency Injection** - CortexContainer + @orchestrator decorator
8. ✅ **Logging & Monitoring** - Standardized logger setup
9. ✅ **MCP Gateway Stub** - Minimal stub (full implementation later)
10. ✅ **Validation Script** - Foundation validation passing

**Validation Command:**
```bash
python scripts/validate_cortex_4_foundation.py
```

**Expected Output:**
```
✅ Base orchestrator framework: PASS
✅ Brain interface: PASS
✅ Template manager: PASS
✅ Configuration system: PASS
✅ DI container: PASS
✅ Pytest infrastructure: PASS
✅ Logging system: PASS
✅ MCP Gateway stub: PASS (minimal)
✅ Foundation validation: ALL CHECKS PASSED
✅ CORTEX 4.0 foundation ready for orchestrator migration!
```

**If ANY check fails:** DO NOT proceed to Phase 3. Fix the failing component first.

**Detailed breakdown:** See [Foundation Prerequisites](#-critical-foundation-prerequisites-for-orchestrator-migration) in Phase 1.

**Quick Reference - When Can I Start?**

| I want to... | Required Prerequisites | Validation |
|--------------|------------------------|------------|
| Start Phase 0 cleanup | None | Manual review |
| Start Phase 1 foundation | Phase 0 complete | Directory structure exists |
| Start Phase 2 brain work | Phase 1 items 1-8 | Brain interface tests pass |
| **Start Phase 3 orchestrator migration** | **ALL 10 Phase 1 prerequisites** | **`validate_cortex_4_foundation.py` = 100% PASS** |
| Start Phase 4 operations | 6+ orchestrators migrated | DI container operational |
| Start Phase 5 testing | All 12 orchestrators migrated | Full test suite ready |
| Start Phase 6 documentation | Phase 5 complete | Documentation tool tested |

---

## 🔍 CORTEX 3.0 Feature Discovery

### Core Orchestrators (11)

**Planning System 3.0:**
```
src/orchestration_3_0/orchestrators/
├── planning/
│   └── planning_orchestrator.py           # 1,599 LOC - Feature planning with DoR/DoD
├── execution/
│   └── execution_orchestrator.py          # Phase execution, multi-orchestrator routing
├── tdd/
│   ├── tdd_orchestrator.py               # RED→GREEN→REFACTOR enforcement
│   ├── test_generator.py                 # Auto-generate test boilerplate
│   ├── implementation_engine.py          # Code generation from tests
│   ├── refactoring_engine.py             # Safe refactoring after GREEN
│   └── phase_validator.py                # Phase transition validation
├── scaffolding/
│   ├── scaffolding_orchestrator.py       # Project structure generation
│   ├── architecture_intelligence.py      # Pattern recognition (Clean/DDD/Microservices)
│   ├── code_analyzer.py                  # AST-based codebase analysis
│   ├── migration_strategist.py           # Migration path planning
│   └── orchestrator_chain.py             # Chain multiple scaffolding operations
├── documentation/
│   └── documentation_orchestrator.py     # Auto-doc generation
├── qa/
│   └── qa_orchestrator.py                # Quality assurance automation
├── devops/
│   └── devops_orchestrator.py            # CI/CD automation
├── intelligence/
│   └── intelligence_orchestrator.py      # Pattern learning and recommendations
├── observability/
│   └── observability_orchestrator.py     # System health monitoring
├── onboarding/
│   └── onboarding_orchestrator.py        # Developer onboarding automation
└── sanitization/
    └── (LEGACY: scripts/cli_wrappers/sanitize_wrapper.py + cortex-toolkit/core/operations/sanitize.py)
    # 5-phase workflow: analyze → mapping → transform → validate → report
    # Removes company-specific data while preserving functionality
    # Manifest: cortex-brain/orchestrator-manifests/code-sanitization-manifest.yaml
```

**Legacy Orchestrators (Consolidation Required):**

**Maintenance & Optimization (5):**
```
src/operations/modules/
├── cleanup/
│   ├── cleanup_orchestrator.py           # Workspace cleanup → MaintenanceOrchestrator
│   ├── holistic_cleanup_orchestrator.py  # Deep cleanup with AST → MaintenanceOrchestrator
│   └── user_cleanup_orchestrator.py      # User-initiated cleanup → MaintenanceOrchestrator
├── optimization/
│   └── optimize_cortex_orchestrator.py   # System optimization → MaintenanceOrchestrator
└── system/
    └── optimize_system_orchestrator.py   # Legacy system optimization → MaintenanceOrchestrator
```

**Quality Assurance & Testing (5):**
```
src/operations/utilities/
├── code_quality_orchestrator.py          # Code quality checks → QAOrchestrator
├── holistic_review_orchestrator.py       # Code review automation → QAOrchestrator
├── integration_testing_orchestrator.py   # Integration tests → TDDOrchestrator
├── performance_profiling_orchestrator.py # Performance analysis → ObservabilityOrchestrator
└── error_recovery_orchestrator.py        # Error handling → NEW: ErrorRecoveryOrchestrator (keep separate)
```

**DevOps & Deployment (1):**
```
src/operations/utilities/
└── deployment_orchestrator.py            # Deployment automation → DevOpsOrchestrator
```

**Documentation (1):**
```
src/operations/utilities/
└── documentation_generation_orchestrator.py  # Doc generation → DocumentationOrchestrator
```

**Infrastructure (4):**
```
src/operations/
├── brain/
│   └── brain_tuning_orchestrator.py      # Brain optimization → BrainOrchestrator (keep internal)
├── demo/
│   └── demo_orchestrator.py              # Interactive demos → OnboardingOrchestrator
├── architectural/
│   └── review_orchestrator.py            # Architecture review → QAOrchestrator
└── utilities/
    └── resource_management_orchestrator.py  # Resource tracking → NEW: ResourceOrchestrator (keep separate)
```

**Operations-Level Orchestrators:**
```
src/operations/
├── operations_orchestrator.py            # Main operations router (6,760 LOC cortex-operations.yaml)
├── onboarding_orchestrator.py            # User onboarding
└── commit_and_push.py                    # Git operations
```

**Workflow Orchestrators:**
```
src/workflows/
├── tdd_workflow_orchestrator.py          # TDD workflow automation
├── workflow_pipeline.py                  # Generic workflow pipelines
└── workflow_engine.py                    # Workflow execution engine
```

**Support Orchestrators:**
```
src/
├── response_templates/multi_template_orchestrator.py  # Response template management
├── tier1/vision_orchestrator.py                       # Vision and roadmap planning
├── tier3/orchestrators/adoption_analytics_orchestrator.py  # Adoption metrics
├── llm/orchestrator.py                                # LLM interaction management
├── setup/setup_orchestrator.py                        # Initial setup
├── orchestrators/git_checkpoint_orchestrator.py       # Git checkpoint automation
└── dashboard/orchestrator.py                          # Dashboard data orchestration
```

### Agents (12)

**Primary Agents (8):**
```
src/cortex_agents/
├── intent_router.py                      # Route user intent to appropriate agent
├── planning_agent.py                     # Feature planning workflows
├── ado_agent.py                          # Azure DevOps integration
├── story_intelligence_agent.py           # Story analysis and enhancement
├── cross_repository_learning_agent.py    # Multi-repo pattern learning
├── orchestrator_agent.py                 # Orchestrator management
├── brain_ingestion_agent_impl.py         # Brain tier 2/3 ingestion
└── llm_intent_router.py                  # LLM-based intent classification
```

**Specialized Agents (9):**
```
src/cortex_agents/
├── application_health_agent.py           # Application health monitoring → ObservabilityOrchestrator
├── rca_agent.py                          # Root Cause Analysis automation → IntelligenceOrchestrator
├── learning_capture_agent.py             # Capture learning patterns from sessions → Tier 2 Brain
├── learning_librarian_agent.py           # Organize and retrieve learned patterns → Tier 2 Brain
├── screenshot_analyzer.py                # Visual analysis for UI/UX workflows → IntelligenceOrchestrator
├── session_resumer.py                    # Resume interrupted sessions with context → Tier 1 Brain
├── profile_agent.py                      # User profile and preferences management → Tier 3 Brain
├── compliance_dashboard_agent.py         # Compliance tracking and reporting → ObservabilityOrchestrator
└── welcome_banner_agent.py               # User onboarding and welcome experience → OnboardingOrchestrator
```

**Security Agents (1):**
```
src/agents/security/
└── threat_modeler_agent.py               # Security threat modeling and analysis → QAOrchestrator (security phase)
```

**Migration Strategy:**
- **Tier Integration:** learning_capture, learning_librarian, session_resumer, profile_agent → Brain tier enhancements
- **Orchestrator Integration:** Remaining agents become specialized phases within orchestrators
- **Keep Separate:** intent_router, llm_intent_router (routing infrastructure)

### Brain Tiers (Current - SQLite Per-Repo)

```
cortex-brain/
├── schema.sql                            # 735 LOC - All 4 tiers in single DB
├── tier0/ (Governance)
│   ├── rules_engine.py
│   └── skull_protector.py
├── tier1/ (Working Memory)
│   ├── conversation_manager.py
│   ├── context_resolver.py
│   └── fifo_queue.py                     # 20-conversation rolling window
├── tier2/ (Knowledge Graph)
│   ├── pattern_storage.py
│   ├── knowledge_graph_builder.py
│   └── cross_project_insights.py
└── tier3/ (Dev Context)
    ├── git_metrics_collector.py
    └── repository_context.py
```

### Key Operations (27 from cortex-operations.yaml)

| Operation | Category | Orchestrator | Status |
|-----------|----------|--------------|--------|
| `refine` | System | RefinementOrchestrator | ✅ Ready |
| `upgrade` | System | UpgradeUtility | ✅ Ready |
| `plan` | Planning | PlanningOrchestrator | ✅ Ready |
| `plan ado` | Planning | ADOPlanningOrchestrator | ✅ Ready |
| `tdd` | Development | TDDOrchestrator | ✅ Ready |
| `sanitize` | Code Quality | SanitizationOrchestrator | ✅ Ready |
| `align` | Brain | AlignmentChecker | ✅ Ready |
| `healthcheck` | Brain | HealthCheckOrchestrator | ✅ Ready |
| `cleanup` | Maintenance | CleanupOrchestrator | ✅ Ready |
| `optimize` | Maintenance | OptimizeOrchestrator | ✅ Ready |
| `review` | Code Quality | CodeReviewOrchestrator | ✅ Ready |
| `deploy` | Operations | DeploymentOrchestrator | ✅ Ready |
| `docs-generate` | Documentation | DocGenerationOrchestrator | ✅ Ready |
| `demo` | Tutorial | DemoOrchestrator | ✅ Ready |

---

## 🏗️ CORTEX 4.0 Architecture Vision

### 1. MCP Server Architecture

**Current (3.0):** Hardcoded tool wrappers → 100+ wrapper scripts scattered across codebase

**Target (4.0):** MCP Protocol-based pluggable tools

```
CORTEX 4.0 Core
       ↓
┌──────────────────┐
│   MCP Gateway    │  ← Single entry point for all tools
│  (Router + Auth) │
└────────┬─────────┘
         │
    ┌────┴─────┬──────────┬──────────┐
    ↓          ↓          ↓          ↓
┌─────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
│Dev Tools│ │ ADO  │ │Enterprise│ │Security│
│  MCP    │ │ MCP  │ │   MCP    │ │  MCP   │
└────┬────┘ └──┬───┘ └────┬─────┘ └───┬────┘
     │         │          │            │
  Git/Docker  Boards   Jira/Teams   SAST/Vault
```

**Implementation:**
```
src/mcp/
├── gateway/
│   ├── mcp_gateway.py                # Main router
│   ├── auth_manager.py               # Tool-level authorization
│   ├── circuit_breaker.py            # Fault tolerance
│   └── load_balancer.py              # Multi-server distribution
├── servers/
│   ├── dev_tools_server.py           # Git, Docker, pytest, etc.
│   ├── ado_server.py                 # Azure DevOps
│   ├── enterprise_server.py          # Jira, Confluence, Teams
│   └── security_server.py            # SAST, secret scanning
├── registry/
│   ├── server_registry.py            # Tool discovery
│   ├── capability_advertiser.py      # What each server can do
│   └── version_manager.py            # API versioning
└── protocol/
    ├── mcp_protocol.py               # JSON-RPC 2.0 implementation
    ├── tool_schema.py                # Tool definition schemas
    └── request_validator.py          # Input validation
```

**Benefits:**
- ✅ Add new tool in <1 day (just config, no code)
- ✅ Loose coupling (swap implementations without CORTEX changes)
- ✅ Centralized governance (audit all tool calls)
- ✅ Consistent error handling
- ✅ Easy to test (mock MCP servers)

### 2. Enhanced Brain Architecture (Hybrid Centralization)

**Current (3.0):** Per-repository SQLite (`{repo}/.cortex/brain.db`)

**Target (4.0):** Hybrid model

```
~/.cortex/shared/                         # CENTRALIZED
├── response-templates.yaml               # Single source of truth
├── capabilities.yaml                     # Unified capability definitions
├── tier2/
│   └── knowledge_graph.db                # Cross-repo pattern sharing
│       ├── patterns (with namespace)     # Patterns tagged by repo
│       ├── recommendations               # AI-driven insights
│       └── cross_repo_insights           # "Similar projects" analysis
└── tier0/
    └── skull_rules.yaml                  # Immutable governance

{repo}/cortex-brain/                      # PER-REPOSITORY (ISOLATED)
├── tier1/
│   └── conversations.db                  # Conversation history (FIFO)
└── tier3/
    └── git_metrics.db                    # Repository-specific metrics
```

**Implementation Plan:**
1. **Phase 1:** Shared templates (~/.cortex/shared/response-templates.yaml)
2. **Phase 2:** Centralized Tier 2 with namespace isolation
3. **Phase 3:** Cross-repo pattern discovery
4. **Phase 4:** (Future) Evaluate full centralization

**Storage:** **KEEP SQLite** (lightweight, zero infrastructure cost, perfect for dev tools)

**Why SQLite:**
- ✅ Zero setup (no server required)
- ✅ ACID compliant
- ✅ FTS5 full-text search built-in
- ✅ Cross-platform (Windows/Linux/macOS)
- ✅ Easy backup (just copy files)
- ✅ Perfect for single-machine dev workflows
- ✅ Scales to 100GB+ databases
- ❌ Enterprise (50+ devs) → PostgreSQL/SQL Server

### 3. Bloat Reduction Strategy: Dependency Injection

**Current Problem:** Manifest files explode with config

```yaml
# cortex-operations.yaml - 6,760 lines!
operations:
  refine:
    modules: [refinement_orchestrator_v1]
    profiles:
      standard: {...}
      discovery_only: {...}
    implementation_status: {...}
    examples: [...]
```

**Target (4.0):** **Permanent Wiring via Dependency Injection Container**

```python
# src/di/container.py
from dependency_injector import containers, providers

class CortexContainer(containers.DeclarativeContainer):
    """
    Dependency Injection Container - PERMANENT WIRING
    
    Benefits:
    - NO manifest files for wiring
    - Auto-discovery of orchestrators
    - Type-safe dependencies
    - Easy testing (mock injection)
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Brain Tiers
    tier0_rules_engine = providers.Singleton(Tier0RulesEngine)
    tier1_conversation_manager = providers.Singleton(Tier1ConversationManager)
    tier2_knowledge_graph = providers.Singleton(Tier2KnowledgeGraph)
    tier3_git_metrics = providers.Singleton(Tier3GitMetrics)
    
    # MCP Gateway
    mcp_gateway = providers.Singleton(
        MCPGateway,
        auth_manager=providers.Factory(AuthManager),
        circuit_breaker=providers.Factory(CircuitBreaker),
    )
    
    # Orchestrators (auto-discovered via @orchestrator decorator)
    planning_orchestrator = providers.Factory(
        PlanningOrchestrator,
        session_manager=providers.Dependency(SessionManager),
        mcp_gateway=mcp_gateway,
    )
    
    tdd_orchestrator = providers.Factory(
        TDDOrchestrator,
        test_runner=providers.Factory(TestRunner),
        coverage_analyzer=providers.Factory(CoverageAnalyzer),
    )
    
    # ... auto-register all @orchestrator decorated classes


# src/di/decorators.py
def orchestrator(name: str, category: str):
    """
    Decorator for auto-registration.
    
    @orchestrator(name="planning", category="feature_development")
    class PlanningOrchestrator(BaseOrchestrator):
        pass
    """
    def decorator(cls):
        # Auto-register in container
        ORCHESTRATOR_REGISTRY[name] = cls
        cls._cortex_metadata = {
            "name": name,
            "category": category,
            "auto_discovered": True
        }
        return cls
    return decorator
```

**Manifest Reduction:**
```
Before (3.0): 6,760 lines of YAML config
After (4.0):  500 lines of metadata ONLY
              - Operation descriptions
              - User-facing examples
              - DoR/DoD definitions
              Wiring → Dependency Injection Container
```

### 4. Clean Orchestrator Structure

**Current (3.0):** Tests scattered, no co-location

```
src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py
tests/orchestrators/test_planning_orchestrator_v3_1.py  ← Far away!
tests/orchestrators/test_planning_orchestrator_phase6.py
tests/orchestrators/test_planning_orchestrator_observer.py
tests/orchestrators/test_planning_orchestrator_folder_integration.py  ← 4 test files!
```

**Target (4.0):** **Tests co-located, TDD-first**

```
src/orchestrators/
├── planning/
│   ├── __init__.py
│   ├── planning_orchestrator.py          # 800 LOC max
│   ├── complexity_analyzer.py            # 300 LOC
│   ├── dor_validator.py                  # 200 LOC
│   ├── plan_generator.py                 # 400 LOC
│   └── tests/                            # ← CO-LOCATED!
│       ├── __init__.py
│       ├── test_planning_orchestrator.py
│       ├── test_complexity_analyzer.py
│       ├── test_dor_validator.py
│       └── test_plan_generator.py
├── tdd/
│   ├── __init__.py
│   ├── tdd_orchestrator.py
│   ├── test_generator.py
│   ├── implementation_engine.py
│   ├── refactoring_engine.py
│   └── tests/
│       ├── test_tdd_orchestrator.py
│       ├── test_test_generator.py
│       ├── test_implementation_engine.py
│       └── test_refactoring_engine.py
├── execution/
│   ├── __init__.py
│   ├── execution_orchestrator.py
│   └── tests/
│       └── test_execution_orchestrator.py
├── ado/
│   ├── __init__.py
│   ├── ado_orchestrator.py               # Consolidate ADO operations
│   ├── work_item_generator.py
│   └── tests/
│       └── test_ado_orchestrator.py
└── maintenance/
    ├── __init__.py
    ├── maintenance_orchestrator.py        # Consolidate cleanup/optimize
    ├── cleanup_engine.py
    ├── optimization_engine.py
    └── tests/
        └── test_maintenance_orchestrator.py
```

**Rules:**
1. ✅ Every orchestrator has `tests/` subfolder
2. ✅ Test file names match source: `foo.py` → `test_foo.py`
3. ✅ TDD mandatory: Write test first, then implementation
4. ✅ 85%+ coverage per orchestrator
5. ✅ Max 800 LOC per file (split if larger)
6. ✅ **CORTEX tests ONLY** - Application tests belong in user repos (SKULL: TEST_LOCATION_SEPARATION)

---

## 📋 CORTEX 3.0 → 4.0 Consolidation Mapping

### Utility Orchestrator Migration Strategy

**Goal:** Consolidate 16 utility orchestrators into 11 core orchestrators + 2 new specialized orchestrators

| 3.0 Utility Orchestrator | 4.0 Target | Migration Strategy | LOC | Notes |
|--------------------------|------------|-------------------|-----|-------|
| **Maintenance & Cleanup (5 → 1)** |
| `cleanup_orchestrator.py` | MaintenanceOrchestrator | Merge as cleanup phase | 800 | Basic workspace cleanup |
| `holistic_cleanup_orchestrator.py` | MaintenanceOrchestrator | Merge as advanced cleanup phase | 1,200 | AST-powered deep cleanup |
| `user_cleanup_orchestrator.py` | MaintenanceOrchestrator | Merge as user-triggered cleanup | 600 | Interactive cleanup |
| `optimize_cortex_orchestrator.py` | MaintenanceOrchestrator | Merge as optimization phase | 900 | System optimization |
| `optimize_system_orchestrator.py` | MaintenanceOrchestrator | Merge as legacy optimization phase | 1,100 | Deprecated, consolidate logic |
| **QA & Testing (5 → 3)** |
| `code_quality_orchestrator.py` | QAOrchestrator | Merge as code quality phase | 700 | Linting, formatting, metrics |
| `holistic_review_orchestrator.py` | QAOrchestrator | Merge as code review phase | 800 | Automated PR review |
| `architectural/review_orchestrator.py` | QAOrchestrator | Merge as architecture review phase | 1,000 | 6-phase architectural analysis |
| `integration_testing_orchestrator.py` | TDDOrchestrator | Merge as integration test phase | 500 | Multi-layer integration tests |
| `performance_profiling_orchestrator.py` | ObservabilityOrchestrator | Merge as performance phase | 900 | Profiling, benchmarking |
| **DevOps (1 → 1)** |
| `deployment_orchestrator.py` | DevOpsOrchestrator | Merge as deployment phase | 600 | CI/CD, deployment automation |
| **Documentation (1 → 1)** |
| `documentation_generation_orchestrator.py` | DocumentationOrchestrator | Replace main logic | 800 | Doc generation engine |
| **Infrastructure (3 → 2)** |
| `brain_tuning_orchestrator.py` | BrainOrchestrator | Keep as internal orchestrator | 500 | Brain memory optimization |
| `demo_orchestrator.py` | OnboardingOrchestrator | Merge as interactive demo phase | 400 | Tutorial workflows |
| **NEW: Specialized Orchestrators (2)** |
| `error_recovery_orchestrator.py` | **NEW: ErrorRecoveryOrchestrator** | Keep separate - critical infrastructure | 600 | Fault tolerance, rollback |
| `resource_management_orchestrator.py` | **NEW: ResourceOrchestrator** | Keep separate - system-level tracking | 700 | Memory, CPU, disk monitoring |
| **Observability Consolidation (3 → 1)** |
| `orchestration_metrics_collector.py` | ObservabilityOrchestrator | Metrics subsystem | 800 | Collect orchestrator metrics |
| `orchestration_analytics_dashboard.py` | ObservabilityOrchestrator | Intelligent Dashboard | 1,200 | Visualize metrics, analytics |
| `parallel_orchestration_coordinator.py` | BaseOrchestrator | Core framework feature | 500 | Built into base orchestrator |

**Totals:**
- **3.0 Utility Orchestrators:** 16 (12,700 LOC)
- **4.0 Core Orchestrators:** 11 (Planning, TDD, Execution, Scaffolding, Documentation, QA, DevOps, Observability, Intelligence, Onboarding, ADO)
- **4.0 Specialized Orchestrators:** 2 (ErrorRecovery, Resource)
- **4.0 Total:** 13 orchestrators
- **Consolidation Ratio:** 28+ orchestrators → 13 orchestrators (54% reduction)
- **Code Reuse:** 85% of logic preserved, 15% eliminated as duplication

---

### Observability Orchestrator Enhanced Features

**Goal:** Consolidate 5 disparate dashboard/monitoring systems into unified ObservabilityOrchestrator

**Current 3.0 Implementation (Scattered):**
```
src/orchestration_3_0/orchestrators/observability/
├── observability_orchestrator.py         # Main orchestrator (500 LOC)
└── intelligent_dashboard/                # AST-powered dashboard (2,800 LOC)
    ├── ast_analyzer.py
    ├── call_graph_builder.py
    └── dashboard_generator.py

src/dashboard/
├── orchestrator.py                       # Dashboard HTTP server (400 LOC)
└── orchestrators/
    └── scalable_collector_orchestrator.py  # Data collection (600 LOC)

src/orchestrators/
└── application_health_orchestrator.py    # Health monitoring (500 LOC)

src/operations/utilities/
├── orchestration_metrics_collector.py    # Metrics collection (800 LOC)
└── orchestration_analytics_dashboard.py  # Analytics dashboard (1,200 LOC)
```

**Target 4.0 Unified Structure:**
```
src/orchestrators/observability/
├── __init__.py
├── observability_orchestrator.py         # Main coordinator (600 LOC)
├── health_monitor.py                     # System health checks (400 LOC)
├── metrics_collector.py                  # Unified metrics collection (800 LOC)
├── intelligent_dashboard/                # AST-powered visualization (2,800 LOC)
│   ├── ast_analyzer.py
│   ├── call_graph_builder.py
│   ├── dashboard_generator.py
│   └── http_server.py                    # Dashboard HTTP server
├── analytics_engine.py                   # Data analysis (1,000 LOC)
├── performance_profiler.py               # Performance analysis (900 LOC)
└── tests/
    ├── test_observability_orchestrator.py
    ├── test_health_monitor.py
    ├── test_metrics_collector.py
    ├── test_intelligent_dashboard.py
    ├── test_analytics_engine.py
    └── test_performance_profiler.py
```

**Consolidation Strategy:**
1. **Merge `dashboard/orchestrator.py` → `intelligent_dashboard/http_server.py`**
   - HTTP server logic + dashboard generation
   
2. **Merge `scalable_collector_orchestrator.py` + `orchestration_metrics_collector.py` → `metrics_collector.py`**
   - Unified metrics collection pipeline
   
3. **Merge `application_health_orchestrator.py` → `health_monitor.py`**
   - Application health checks + system health
   
4. **Merge `orchestration_analytics_dashboard.py` → `analytics_engine.py`**
   - Analytics processing + visualization data prep
   
5. **Merge `performance_profiling_orchestrator.py` → `performance_profiler.py`**
   - Profiling, benchmarking, performance analysis

**Features Preserved:**
- ✅ AST-powered code visualization (intelligent_dashboard)
- ✅ Real-time metrics collection
- ✅ Historical analytics
- ✅ Health monitoring
- ✅ Performance profiling
- ✅ HTTP dashboard server
- ✅ Cross-orchestrator tracking

---

### Scaffolding Orchestrator Sub-Component Migration

**Current 3.0 Implementation:**
```
src/orchestration_3_0/orchestrators/scaffolding/
├── scaffolding_orchestrator.py           # Main orchestrator (800 LOC)
├── architecture_intelligence.py          # Pattern recognition (600 LOC)
├── code_analyzer.py                      # AST-based analysis (700 LOC)
├── migration_strategist.py               # Migration planning (500 LOC)
└── orchestrator_chain.py                 # Chain operations (400 LOC)
```

**Target 4.0 Structure:**
```
src/orchestrators/scaffolding/
├── __init__.py
├── scaffolding_orchestrator.py           # Main coordinator (600 LOC)
├── architecture_intelligence.py          # Pattern recognition (Clean/DDD/Microservices) (600 LOC)
├── code_analyzer.py                      # AST-based codebase analysis (700 LOC)
├── migration_strategist.py               # Migration path planning (500 LOC)
├── project_generator.py                  # Project structure generation (400 LOC)
└── tests/
    ├── test_scaffolding_orchestrator.py
    ├── test_architecture_intelligence.py
    ├── test_code_analyzer.py
    ├── test_migration_strategist.py
    └── test_project_generator.py
```

**Migration Strategy:**
1. **Migrate all 4 sub-components AS-IS** - No refactoring needed
2. **Replace `orchestrator_chain.py`** → Built into `scaffolding_orchestrator.py`
3. **Add co-located tests** - Currently scattered in `tests/orchestrators/`

**Key Features Preserved:**
- ✅ Architecture pattern recognition (Clean Architecture, DDD, Microservices)
- ✅ AST-based codebase analysis
- ✅ Migration strategy generation
- ✅ Orchestrator chaining capability
- ✅ Project structure generation

---

### Agent Migration Strategy

**Decision:** Agents remain **INDEPENDENT** from orchestrators but integrate more deeply.

**Rationale:**
1. **Separation of Concerns:** Agents handle intelligent routing/analysis, orchestrators handle workflows
2. **Reusability:** Multiple orchestrators can call the same agent
3. **Testing:** Easier to test agents independently
4. **Brain Integration:** Some agents (learning_capture, session_resumer) belong in brain tiers

**Migration Plan:**

| Agent | 3.0 Location | 4.0 Target | Integration |
|-------|-------------|------------|-------------|
| **Keep as Agents (7)** |
| `intent_router.py` | `src/cortex_agents/` | `src/agents/` | Entry point for all requests |
| `llm_intent_router.py` | `src/cortex_agents/` | `src/agents/` | LLM-based classification |
| `planning_agent.py` | `src/cortex_agents/` | `src/agents/` | Called by PlanningOrchestrator |
| `ado_agent.py` | `src/cortex_agents/` | `src/agents/` | Called by ADOOrchestrator |
| `story_intelligence_agent.py` | `src/cortex_agents/` | `src/agents/` | Called by PlanningOrchestrator |
| `orchestrator_agent.py` | `src/cortex_agents/` | `src/agents/` | Orchestrator management |
| `screenshot_analyzer.py` | `src/cortex_agents/` | `src/agents/` | Called by IntelligenceOrchestrator |
| **Integrate into Brain (4)** |
| `learning_capture_agent.py` | `src/cortex_agents/` | `src/brain/tier2/learning_capture.py` | Tier 2 enhancement |
| `learning_librarian_agent.py` | `src/cortex_agents/` | `src/brain/tier2/learning_librarian.py` | Tier 2 enhancement |
| `session_resumer.py` | `src/cortex_agents/` | `src/brain/tier1/session_resumer.py` | Tier 1 enhancement |
| `profile_agent.py` | `src/cortex_agents/` | `src/brain/tier3/profile_manager.py` | Tier 3 enhancement |
| **Integrate into Orchestrators (6)** |
| `application_health_agent.py` | `src/cortex_agents/` | `src/orchestrators/observability/health_monitor.py` | ObservabilityOrchestrator phase |
| `rca_agent.py` | `src/cortex_agents/` | `src/orchestrators/intelligence/rca_engine.py` | IntelligenceOrchestrator phase |
| `compliance_dashboard_agent.py` | `src/cortex_agents/` | `src/orchestrators/observability/compliance_tracker.py` | ObservabilityOrchestrator phase |
| `welcome_banner_agent.py` | `src/cortex_agents/` | `src/orchestrators/onboarding/welcome_experience.py` | OnboardingOrchestrator phase |
| `brain_ingestion_agent_impl.py` | `src/cortex_agents/` | `src/brain/tier2/ingestion_pipeline.py` | Tier 2 enhancement |
| `threat_modeler_agent.py` | `src/agents/security/` | `src/orchestrators/qa/security_analyzer.py` | QAOrchestrator security phase |

**Result:**
- **3.0 Agents:** 18 total
- **4.0 Agents:** 7 independent agents + 4 brain integrations + 6 orchestrator phases + 1 deprecated = 12 active
- **Consolidation:** 33% reduction, clearer boundaries

---

## 🔄 Migration Order & Strategy

### Phase 0: Pre-Migration Cleanup (Week 0) - Organize Bloat

**Goal:** Clean up CORTEX 3.0 bloat BEFORE starting migration to prevent carrying it forward

**Current Problem:**
```
cortex-brain/
├── 67 files at root level (YAML, MD, SQL mixed)
├── documents/planning/
│   ├── active/ (mixed plans)
│   ├── archived/ (old plans)
│   ├── cortex-4.0/ (NEW - consolidate here)
│   ├── temp-plans/ (scattered)
│   ├── ado/ (separate)
│   └── 12 loose planning files at documents/planning/
├── orchestrator-manifests/ (20+ YAML files)
└── 15+ *-QUICK-REF.md at root
```

**Target (4.0):**
```
cortex-brain/
├── core/ (ONLY essential configs)
│   ├── brain-protection-rules.yaml
│   ├── response-templates.yaml
│   ├── schema.sql
│   └── operations-config.yaml
├── documents/
│   ├── planning/
│   │   └── cortex-4.0/ (ALL migration docs consolidated)
│   ├── guides/ (all *-QUICK-REF.md moved here)
│   ├── reports/
│   └── analysis/
├── manifests/ (orchestrator + operation manifests)
├── tier1/, tier2/, tier3/ (brain tiers - unchanged)
└── admin/ (admin-only operations)
```

**Tasks:**

**Step 1: Consolidate CORTEX 4.0 Planning (1 hour)**
- [ ] Create `cortex-brain/documents/planning/cortex-4.0/archive/` for old migrations
- [ ] Move scattered migration files to archive:
  - [ ] `documents/planning/archived/migrations/*` → `cortex-4.0/archive/`
  - [ ] `documents/analysis/*migration*.md` → `cortex-4.0/archive/`
  - [ ] `documents/reports/*migration*.md` → `cortex-4.0/archive/`
  - [ ] `documents/implementation-guides/*migration*.md` → `cortex-4.0/archive/`
- [ ] Keep only active CORTEX 4.0 docs at top level:
  - ✅ `CORTEX-3-TO-4-MIGRATION-MASTER-PLAN.md`
  - ✅ `MIGRATION-VISUAL-ROADMAP.md`
  - ✅ `MIGRATION-QUICK-REFERENCE.md`
  - ✅ All numbered docs (00-20)

**Step 2: Reorganize Root-Level Files (2 hours)**
- [ ] Create `cortex-brain/core/` for essential configs
- [ ] Move to `core/`:
  - [ ] `brain-protection-rules.yaml`
  - [ ] `response-templates.yaml`
  - [ ] `schema.sql`
  - [ ] `operations-config.yaml`
- [ ] Create `cortex-brain/documents/guides/quick-reference/`
- [ ] Move all *-QUICK-REF.md to guides:
  - [ ] `CLEANUP-QUICK-REF.md`
  - [ ] `CODE-SANITIZATION-QUICK-REF.md`
  - [ ] `HOLISTIC-DISCOVERY-QUICK-REF.md`
  - [ ] `INTELLIGENT-TDD-QUICK-REF.md`
  - [ ] `LAYER-8-QUICK-REF.md`
  - [ ] `MASTER-PLANNER-VISUAL-TRACKER-QUICK-REF.md`
  - [ ] `PLAN-FILE-RESOLVER-QUICK-REF.md`
  - [ ] `UPGRADE-QUICK-REF.md`
  - [ ] `DOCUMENT-CONVERTER-QUICK-REF.md`
  - [ ] `INLINE-CSS-PROHIBITION-QUICK-REF.md`
- [ ] Move `PLANNING-SYSTEM-3.0-GUIDE.md` → `documents/guides/`

**Step 3: Consolidate Manifests (1 hour)**
- [ ] Create `cortex-brain/manifests/orchestrators/`
- [ ] Move `orchestrator-manifests/*` → `manifests/orchestrators/`
- [ ] Create `cortex-brain/manifests/operations/`
- [ ] Move operation YAMLs:
  - [ ] `cleanup-rules.yaml`
  - [ ] `aggressive-cleanup-rules.yaml`
  - [ ] `refactoring-rules.yaml`
  - [ ] `doc-generation-rules.yaml`
  - [ ] `git-checkpoint-rules.yaml`
  - [ ] `token-optimization-rules.yaml`

**Step 4: Consolidate Planning Directories (1 hour)**
- [ ] Merge `documents/planning/temp-plans/` → `documents/planning/active/`
- [ ] Archive completed plans: `documents/planning/completed/` → `documents/planning/archived/`
- [ ] Single active plans location: `documents/planning/active/`

**Step 5: Update Path References (2 hours)**
- [ ] Update all imports in Python code:
  - [ ] `cortex-brain/response-templates.yaml` → `cortex-brain/core/response-templates.yaml`
  - [ ] `cortex-brain/brain-protection-rules.yaml` → `cortex-brain/core/brain-protection-rules.yaml`
  - [ ] `cortex-brain/schema.sql` → `cortex-brain/core/schema.sql`
- [ ] Update references in documentation
- [ ] Update `cortex.config.json` paths
- [ ] Update CLI wrapper paths

**Step 6: Delete Obsolete Files (1 hour)**
- [ ] Review and delete:
  - [ ] Old YAML locks (`.yaml.lock`)
  - [ ] Obsolete tests manifests
  - [ ] Duplicate/outdated guides
  - [ ] Empty directories

**Step 7: Create CORTEX-4.0 Branch Structure (1 hour)**
**Purpose:** Prepare directory structure for Phase 1 foundation work

- [ ] Create `CORTEX-4.0` branch from `CORTEX-3.0`
- [ ] Create Phase 1 directory structure (empty, ready for Phase 1):
  ```
  src/
  ├── orchestrators/
  │   └── base/                 # Phase 1 will populate this
  ├── brain/                     # Phase 1 will migrate brain tiers here
  ├── templates/                 # Phase 1 will migrate templates here
  ├── config/                    # Phase 1 will create ConfigManager here
  ├── di/                        # Phase 1 will create DI container here
  ├── mcp/                       # Phase 1 will create MCP Gateway here
  └── logging/                   # Phase 1 will create logger here
  
  tests/
  ├── fixtures/                  # Phase 1 will create test fixtures here
  └── orchestrators/
      └── base/                  # Phase 1 will create base tests here
  
  scripts/
  └── validate_cortex_4_foundation.py  # Phase 1 will create this
  ```

- [ ] Update `.gitignore` for new structure:
  ```
  # CORTEX 4.0
  src/orchestrators/*/tests/__pycache__/
  logs/*.log
  .cortex/
  ```

- [ ] Create placeholder README files:
  - [ ] `src/orchestrators/README.md` - "Phase 1: Will contain base orchestrator framework"
  - [ ] `src/brain/README.md` - "Phase 1: Will contain brain tier implementations"
  - [ ] `src/templates/README.md` - "Phase 1: Will contain response templates"

**Deliverables:**
- ✅ 67 root files → 8 essential files (88% reduction)
- ✅ All CORTEX 4.0 docs in single location
- ✅ CORTEX-4.0 branch created with directory structure ready
- ✅ Clear directory structure
- ✅ Documented file organization rules (below)

**Total Time:** 11 hours (1.4 days)

---

### Migration Phase Prerequisites Matrix

**This table shows what MUST be complete before starting each phase:**

| Phase | Prerequisites | Validation | Can Start When... |
|-------|--------------|------------|-------------------|
| **Phase 0** (Week 0) | None - starting point | Manual review of file organization | Immediately |
| **Phase 1** (Weeks 1-3) | Phase 0 complete | Directory structure exists | Phase 0 deliverables verified |
| **Phase 1.5** (Week 3) | Phase 1 foundation items 1-8 complete | `pytest tests/` passes | Foundation validation script passes |
| **Phase 2** (Weeks 4-6) | Phase 1 complete | Brain interface tests pass | Full Phase 1 validation |
| **Phase 3** (Weeks 7-11) | **CRITICAL:** All 10 Phase 1 prerequisites | `validate_cortex_4_foundation.py` passes ✅ | Foundation validation = 100% pass |
| **Phase 4** (Weeks 12-14) | At least 6 orchestrators migrated | DI container tests pass | Half of Phase 3 complete |
| **Phase 5** (Weeks 15-17) | All orchestrators migrated | Full test suite 85%+ coverage | Phase 3 complete |
| **Phase 6** (Week 18) | Phase 5 complete + docs tool ready | Documentation generator tests pass | All code migrated |

**Critical Blockers:**
- 🚨 **Phase 3 is blocked** until ALL 10 Phase 1 prerequisites are complete and validated
- 🚨 **No orchestrator migration** without passing foundation validation
- 🚨 **Phase 5 cannot start** until all 13 orchestrators are migrated (11 core + 2 specialized)

**Validation Strategy:**
```bash
# Before Phase 3 (MANDATORY)
python scripts/validate_cortex_4_foundation.py

# Before Phase 5 (MANDATORY)
pytest tests/ --cov=src --cov-report=term-missing

# Before Phase 6 (MANDATORY)
pytest tests/cortex-toolkit/documentation/ -v
```

---

### CORTEX 4.0 File Organization Rules (Enforce in Phase 0+)

**Rule 1: Root-Level Restrictions**
- ❌ **FORBIDDEN:** Loose files at `cortex-brain/` root
- ✅ **ALLOWED:** Only these subdirectories:
  - `core/` - Essential configs (4 files max)
  - `documents/` - All documentation
  - `manifests/` - Orchestrator/operation manifests
  - `tier1/`, `tier2/`, `tier3/` - Brain tiers
  - `admin/` - Admin operations
  - `templates/` - Response templates (if split from core)

**Rule 2: Planning Document Organization**
- ✅ **Active Planning:** `documents/planning/active/{project-name}/`
- ✅ **CORTEX 4.0:** `documents/planning/cortex-4.0/` (all migration docs)
- ✅ **Archived:** `documents/planning/archived/{year}/{project-name}/`
- ❌ **FORBIDDEN:** Loose planning docs at `documents/planning/`

**Rule 3: Guide Organization**
- ✅ **Quick Refs:** `documents/guides/quick-reference/{name}-quick-ref.md`
- ✅ **System Guides:** `documents/guides/system/{name}-guide.md`
- ✅ **Implementation Guides:** `documents/implementation-guides/{name}.md`
- ❌ **FORBIDDEN:** *-QUICK-REF.md at root

**Rule 4: Manifest Organization**
- ✅ **Orchestrators:** `manifests/orchestrators/{name}-manifest.yaml`
- ✅ **Operations:** `manifests/operations/{category}-rules.yaml`
- ❌ **FORBIDDEN:** Loose YAML at root (except `core/`)

**Rule 5: Maximum Files Per Directory**
- Root (`cortex-brain/`): 0 files, 8 directories max
- `core/`: 8 files max (brain-protection, response-templates, schema, operations-config, + 4 reserves)
- `documents/planning/`: 0 loose files, subdirectories only
- `documents/guides/quick-reference/`: Unlimited (but organized)

**Rule 6: File Naming Conventions**
- Quick refs: `{domain}-quick-ref.md` (lowercase-with-dashes)
- Guides: `{name}-guide.md`
- Plans: `{feature}-plan.md` or numbered `00-{title}.md`
- Manifests: `{orchestrator}-manifest.yaml`
- Reports: `{topic}-report-{date}.md`

**Rule 7: Deprecation Policy**
- Plans older than 6 months → Move to `archived/{year}/`
- Completed plans → Move to `documents/planning/completed/`
- Obsolete guides → Move to `documents/archived/obsolete/`
- Never delete - always archive with date

**Enforcement:**
- [ ] Pre-commit hook: Check root file count (max 0)
- [ ] CI check: Validate directory structure
- [ ] Monthly audit: Move old plans to archive
- [ ] Documentation: Update `.github/prompts/CORTEX.prompt.md` with rules

---

## 🧠 CORTEX 4.0: Autonomous Documentation Intelligence System

### Vision: Documentation as a First-Class Citizen

**Current Problem (3.0):** Documentation is reactive, manual, and lags behind code changes.

**Target (4.0):** **Autonomous, continuous documentation** that:
- Generates/updates/deletes documentation automatically during implementation
- Extracts knowledge graphs from code changes to feed Tier 2 brain
- Operates without user intervention as standard part of every operation
- Handles edge cases (stale docs, conflicts, drift) gracefully
- **Performance:** <0.5s overhead per commit (imperceptible to users)

### Documentation Intelligence Engine (DIE) Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Documentation Intelligence Engine (DIE)             │
│                      NEW IN 4.0                             │
└─────────────┬───────────────────────────────────────────────┘
              │
    ┌─────────┼─────────┬──────────┬──────────────┐
    ↓         ↓         ↓          ↓              ↓
┌─────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│Continuous│ │Knowledge│ │Lifecycle│ │Brain T2│ │Performance│
│Doc Mgr  │ │Graph   │ │Manager │ │Feeder  │ │Monitor   │
│         │ │Extractor│ │        │ │        │ │          │
└─────────┘ └────────┘ └────────┘ └────────┘ └──────────┘
    │            │          │          │            │
    │            │          │          │            │
Pre-commit   AST/Call   CREATE/     Pattern    <0.5s
Post-commit   Graph    UPDATE/     Storage    overhead
Scheduled    Analysis  DELETE/    Tier 2     tracking
             Patterns  VALIDATE   Brain
```

### Trigger Points (Automatic Documentation Updates)

**1. Code Commit (Pre-commit hook)**
- **Detect:** New/modified/deleted files
- **Extract:** Function signatures, class definitions, docstrings
- **Generate:** API docs, usage examples (TIER_INSTANT - 0.1s)
- **Feed Brain:** Code patterns → Tier 2 knowledge graph
- **Performance:** <0.5s overhead (non-blocking async processing)

**2. Phase Completion (Orchestrator callback)**
- **Summarize:** What was implemented, tests added, metrics
- **Update:** Architecture diagrams, README sections
- **Archive:** Old implementation notes
- **Feed Brain:** Phase success patterns

**3. Test Execution (Post-test hook)**
- **Extract:** Test names, coverage deltas, failure patterns
- **Update:** Test documentation, coverage reports
- **Feed Brain:** Test quality patterns, failure modes

**4. Scheduled Maintenance (Daily/Weekly)**
- **Detect:** Stale docs (code changed, docs didn't)
- **Identify:** Orphaned docs (code deleted, docs remain)
- **Validate:** Doc-code consistency (signatures match)
- **Feed Brain:** Documentation drift patterns

### Tiered Documentation Levels (Performance Optimization)

Progressive documentation generation based on urgency:

| Tier | Speed | When | What |
|------|-------|------|------|
| **INSTANT** | <0.1s | Every commit | Docstring extraction only |
| **FAST** | <1s | Merge request | Signatures + basic examples |
| **FULL** | <5s | Release | AST analysis + diagrams |
| **DEEP** | <30s | Nightly build | Cross-reference + call graphs |

**Strategy:** Users get 90% of documentation value at 10% of cost.

### Knowledge Graph Extraction Pipeline

**What Gets Extracted:**

1. **Code Structure Patterns**
   - Class hierarchies and inheritance
   - Function call graphs and dependencies
   - Module import relationships

2. **Implementation Patterns**
   - Authentication patterns (e.g., "JWT with bcrypt")
   - Error handling patterns
   - Data access patterns (repository, active record, etc.)

3. **Anti-Patterns Detection**
   - Hardcoded secrets
   - Missing error handling
   - Circular dependencies
   - Code smells (long methods, god classes)

4. **Success Patterns**
   - High-coverage modules (>85%)
   - Well-tested integrations
   - Clean architecture examples

5. **Integration Patterns**
   - External library usage examples
   - API integration patterns
   - Database query patterns

**Storage:** Tier 2 knowledge graph with namespace isolation:
```sql
-- Tier 2 Brain Schema (Enhanced)
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    pattern_type TEXT,          -- 'authentication', 'error_handling', etc.
    pattern_name TEXT,          -- 'JWT with bcrypt'
    namespace TEXT,             -- Repository identifier
    context JSON,               -- Code examples, libraries used
    success_rate REAL,          -- Historical success %
    usage_count INTEGER,        -- How often pattern seen
    last_seen TIMESTAMP,
    metadata JSON
);

CREATE TABLE anti_patterns (
    id INTEGER PRIMARY KEY,
    anti_pattern_type TEXT,
    severity TEXT,              -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    file_path TEXT,
    line_number INTEGER,
    recommendation TEXT,
    detected_at TIMESTAMP
);
```

### Edge Cases & Resolution Strategies

#### Edge Case 1: Stale Documentation
**Detection:** File modification timestamp > documentation timestamp  
**Resolution:**
- Re-run AST analysis
- Diff old vs. new
- If changes >20%: Auto-update
- If changes >50%: Flag for manual review
- Commit: `docs: Update stale {module} documentation [AUTO]`

#### Edge Case 2: Orphaned Documentation
**Detection:** Documented file no longer exists in codebase  
**Resolution:**
- Move to `docs/archive/deleted/{date}/`
- Update parent docs (remove links)
- Add tombstone: `<!-- File removed on {date} -->`
- Commit: `docs: Archive orphaned documentation [AUTO]`

#### Edge Case 3: Documentation Conflicts (Merge)
**Detection:** Git merge conflict in `.md` files  
**Resolution:**
- Parse conflict markers
- Run semantic similarity check
- If semantically equivalent: Auto-merge
- If conflicting: Flag with diff preview
- Preserve both: `docs/conflicts/{module}-conflict-{date}.md`

#### Edge Case 4: Documentation Drift
**Detection:** Code examples in docs don't match actual behavior  
**Resolution (Automated):**
- Parse code examples from documentation
- Run examples against actual codebase
- Validate signatures match
- If 90%+ confident: Auto-fix
- Otherwise: Manual review flag

#### Edge Case 5: AST Parse Errors
**Detection:** Syntax error prevents AST analysis  
**Resolution (Graceful Degradation):**
- Skip AST-based docs for that file
- Fallback: Docstring-only extraction
- Log error: `warnings/doc-generation-failures.log`
- Add notice: `<!-- Auto-docs unavailable due to parse error -->`
- Retry after next commit

#### Edge Case 6: Over-Documentation (Performance)
**Detection:** >1000 doc files, generation time >30s per commit  
**Resolution (Optimization):**
- Incremental documentation (only changed files)
- Content-based caching (skip if hash unchanged)
- Parallel processing (multiple files concurrently)
- Archive old documentation to `.tar.gz`

#### Edge Case 7: Brain Tier 2 Unavailable
**Detection:** Database connection fails, knowledge extraction throws exception  
**Resolution (Graceful Degradation):**
- Continue doc generation without brain feeding
- Queue patterns: `cortex-brain/tier2/pending-patterns.json`
- Retry every 5 minutes
- Alert if unavailable >1 hour

#### Edge Case 8: Circular Documentation Dependencies
**Detection:** Doc A references Doc B, Doc B references Doc A  
**Resolution:**
- Build dependency graph, detect cycles (DFS)
- Identify weakest link
- Replace with forward declaration
- Generate in topological order
- Log resolution: `docs/maintenance/circular-ref-resolutions.log`

#### Edge Case 9: Large Bulk Updates
**Detection:** >100 files require documentation update  
**Resolution (Batched Processing):**
- Split into batches of 20 files
- Process sequentially (avoid overwhelming system)
- Progress bar: `Updating documentation: [####------] 40%`
- Incremental commits per batch

#### Edge Case 10: Template Schema Changes
**Detection:** Documentation template version < current schema version  
**Resolution (Auto-Migration):**
- Run template migration script
- Transform old → new schema
- Validate transformed template
- Update all docs using old template
- Commit: `docs: Migrate to schema v2.0 [AUTO]`

### Performance Optimization Strategies

#### Strategy 1: Async-First Architecture (95% non-blocking)

**Before (Blocking):**
```python
def pre_commit_hook():
    analyze_code()           # 2s - USER WAITS
    generate_docs()          # 2s - USER WAITS
    extract_knowledge()      # 1s - USER WAITS
    # Total: 5s blocking
```

**After (Non-Blocking):**
```python
def pre_commit_hook():
    validate_syntax()        # 0.3s - Critical validation only
    check_skull_rules()      # 0.2s - Critical validation only
    queue_doc_work()         # 0.001s - Queue for async
    return ALLOW_COMMIT      # User continues (0.5s total)

async def documentation_worker():
    # Runs in background, user never waits
    await analyze_code()
    await generate_docs()
    await extract_knowledge()
```

**Result:** 5s → 0.5s (90% reduction in user-facing latency)

#### Strategy 2: Incremental Processing (Delta-based)

**Problem:** Re-analyzing entire codebase on every commit (slow)

**Solution:**
```python
# Before: 500 files × 2s = 1000s (16 minutes!)
for file in all_files:
    analyze(file)

# After: 3 files × 2s = 6s (only changed)
changed_files = git_diff()
for file in changed_files:
    analyze(file)
```

**Result:** 99.4% faster for typical commits (3 changed files)

#### Strategy 3: Smart Caching (80%+ hit rate)

```python
class DocumentationCache:
    def should_regenerate(self, file_path: str) -> bool:
        file_hash = hash_file(file_path)
        cached_hash = cache.get(file_path)
        return file_hash != cached_hash  # Skip if unchanged

# Performance:
# - Cache hit: 0.001s (read hash)
# - Cache miss: 2s (full analysis)
# - Hit rate: 80% typical
# - Effective time: 0.2 × 2s + 0.8 × 0.001s = 0.4s per file
```

#### Strategy 4: Parallel Processing (8x speedup)

```python
# Before (Sequential): 10 files × 2s = 20s
for file in changed_files:
    analyze(file)

# After (Parallel): 10 files ÷ 8 cores = 2.5s
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(analyze, f) for f in changed_files]
    results = [f.result() for f in futures]
```

**Result:** 8x faster on multi-core systems

#### Strategy 5: Batched Brain Ingestion (100x speedup)

```python
# Bad: 1000 individual inserts = 10s
for pattern in patterns:
    db.insert(pattern)  # 1000 × 10ms

# Good: 1 bulk insert = 0.1s
db.bulk_insert(patterns)  # 100x faster
```

### Performance Benchmarks

**Small Commit (80% of commits):**
- Files changed: 3
- Before optimization: 6s
- After optimization: 0.3s
- **User perception:** Imperceptible ✅

**Medium Commit (15% of commits):**
- Files changed: 15
- Before optimization: 30s
- After optimization: 1.5s
- **User perception:** Acceptable ✅

**Large Refactor (5% of commits):**
- Files changed: 100
- Before optimization: 200s (3.3 min)
- After optimization: 10s
- **User perception:** "Coffee break" commit ✅

### Performance SLAs & Graceful Degradation

| Condition | Action | User Impact |
|-----------|--------|-------------|
| Doc gen <2s | Normal operation | Full docs |
| Doc gen 2-5s | Skip diagrams | Minor reduction |
| Doc gen 5-10s | Docstrings only | Noticeable reduction |
| Doc gen >10s | Disable auto-docs | Manual doc only |
| System load >80% | Queue for later | Zero impact (async) |

### ROI Analysis

**Cost:** +0.3s per commit × 100 commits/day = 30s/day overhead

**Benefit:** 5 min saved per API lookup × 20 lookups/day = 100 min/day saved

**Net Gain:** 99.5 minutes/day per developer (**200x ROI**)

### Performance Validation Tests

```python
# tests/performance/test_documentation_performance.py

def test_small_commit_under_500ms():
    """Small commits must complete in <500ms"""
    with PerformanceTimer() as timer:
        commit_with_docs(changed_files=3)
    assert timer.elapsed < 0.5

def test_cache_hit_rate_above_80_percent():
    """Cache must be effective (80%+ hit rate)"""
    stats = run_commits(count=100)
    hit_rate = stats.cache_hits / stats.total_requests
    assert hit_rate > 0.80

def test_async_queue_no_blocking():
    """Async queue must not block main thread"""
    with ThreadMonitor() as monitor:
        commit_with_docs(changed_files=50)
    assert monitor.main_thread_blocked_ms < 100
```

### Implementation Timeline

**Phase 1.5: Documentation & Visualization Framework (Week 3)**

**Prerequisites:** Phase 1 foundation items 1-8 complete

**Deliverables:**
1. [ ] Continuous Documentation Manager implementation
2. [ ] Knowledge Graph Extractor (AST + call graph analysis)
3. [ ] Documentation Lifecycle Manager (CREATE/UPDATE/DELETE/VALIDATE)
4. [ ] Brain Tier 2 Feeder integration
5. [ ] Performance monitoring & auto-tuning
6. [ ] Edge case handlers (all 10 scenarios)
7. [ ] Git hooks (pre-commit, post-commit, post-test)
8. [ ] Scheduled maintenance jobs (daily/weekly)
9. [ ] Documentation performance test suite
10. [ ] Documentation generation tool validation

**Performance Target:** <0.5s overhead per commit

**Test Coverage Target:** 85%+ for documentation engine

**Phase 6: Documentation Finalization (Week 17-18)**

**Prerequisites:** Phase 5 complete (all code migrated)

**Deliverables:**
1. [ ] Complete technical documentation generation (200+ docs)
2. [ ] 60+ interactive D3.js diagrams (architecture, flows, dependencies)
3. [ ] API documentation for all orchestrators
4. [ ] Knowledge graph validation (Tier 2 patterns)
5. [ ] Documentation coverage report (85%+ target)
6. [ ] Documentation freshness report (stale doc detection)
7. [ ] Final performance validation (<0.5s per commit)
8. [ ] User guide for documentation system

**Timeline Adjustment:** 17 weeks → **18 weeks** (added 1 week for documentation finalization)

### Documentation Intelligence Benefits

**Quantifiable Improvements:**

| Metric | Without DIE | With DIE | Delta |
|--------|-------------|----------|-------|
| Commit time | 1.0s | 1.3s | +0.3s (30%) |
| Doc coverage | 20% | 85% | +65% |
| API lookup time | 5 min | 10s | 30x faster |
| Stale docs | 50/month | 2/month | 96% reduction |
| Onboarding time | 2 weeks | 3 days | 79% faster |

**Qualitative Improvements:**
- ✅ Documentation always current with code
- ✅ Knowledge sharing across projects (Tier 2)
- ✅ Pattern recommendations from historical success
- ✅ Anti-pattern detection prevents issues
- ✅ Zero manual documentation burden
- ✅ Architectural insights from code analysis

### Configuration

**cortex.config.json additions:**
```json
{
  "documentation": {
    "enabled": true,
    "tier": "FAST",
    "async_processing": true,
    "cache_enabled": true,
    "max_workers": 8,
    "performance": {
      "max_commit_overhead_ms": 500,
      "cache_ttl_hours": 24,
      "batch_size": 20
    },
    "brain_feeding": {
      "enabled": true,
      "batch_size": 100,
      "retry_interval_seconds": 300
    },
    "validation": {
      "stale_threshold_days": 7,
      "orphan_detection": "weekly",
      "drift_detection": "daily"
    }
  }
}
```

### YAML Format Assessment

**Question:** Is YAML still the best path forward for efficient execution of plans?

**Analysis:**

**✅ YAML Strengths:**
1. **Human-readable** - Easy for Copilot to parse and generate
2. **Hierarchical** - Natural for nested phase structures
3. **Comments supported** - In-line documentation
4. **Standardized** - Universal parsing libraries
5. **Diff-friendly** - Git tracks changes clearly
6. **No code execution** - Safe, declarative format

**❌ YAML Weaknesses:**
1. **Verbose** - Indentation overhead (6,760 lines in cortex-operations.yaml)
2. **No validation** - Easy to create invalid structures
3. **Limited types** - Strings/numbers/bools only
4. **Anchors complex** - YAML anchors hard to maintain
5. **Whitespace sensitive** - Indentation errors cause failures

**🎯 Recommendation for CORTEX 4.0:**

**HYBRID APPROACH:**

1. **Use YAML for:**
   - ✅ **Orchestrator manifests** (metadata, DoR/DoD, examples)
   - ✅ **Operation definitions** (user-facing commands, descriptions)
   - ✅ **Brain rules** (governance, SKULL policies)
   - ✅ **Response templates** (user-facing content)

2. **Use Python Dataclasses for:**
   - ✅ **Runtime configuration** (DI container, type-safe)
   - ✅ **Phase execution plans** (generated programmatically)
   - ✅ **Internal orchestrator state** (not user-facing)

3. **Use JSON for:**
   - ✅ **Knowledge graph storage** (Tier 2 brain - efficient querying)
   - ✅ **Checkpoint data** (serializable phase state)
   - ✅ **API responses** (MCP protocol)

**Example: Planning Manifest (YAML)**
```yaml
# cortex-brain/manifests/orchestrators/planning-manifest.yaml
name: "planning"
category: "feature_development"
description: "AI-driven feature planning with DoR/DoD validation"

metadata:
  version: "4.0"
  complexity_tiers: [1, 2, 3, 4]
  auto_tdd: true

phases:
  - name: "Discovery"
    dor: ["User story defined", "Tech stack identified"]
    dod: ["Architecture diagram", "Complexity score"]
  - name: "Implementation"
    dor: ["Tests written (RED)", "Design approved"]
    dod: ["Tests passing (GREEN)", "Code reviewed"]
```

**Example: Runtime Execution (Python Dataclass)**
```python
# src/orchestrators/planning/models.py
from dataclasses import dataclass
from enum import Enum

@dataclass
class PhaseExecution:
    phase_id: str
    status: PhaseStatus
    start_time: datetime
    dependencies: List[str]
    git_commits: List[str]
    tests_passing: int
    checkpoint_data: Dict[str, Any]
```

**Verdict:** **YAML remains optimal for CORTEX 4.0** with these constraints:

1. **Size limit:** Max 1000 lines per YAML file
2. **Schema validation:** Use JSON Schema to validate YAML
3. **Generation over editing:** Programmatically generate YAML, minimize manual editing
4. **Runtime conversion:** Parse YAML → Python dataclasses for type safety

**Migration Action Items:**
- [ ] Add JSON Schema validation for all YAML manifests
- [ ] Split cortex-operations.yaml (6,760 lines) into per-operation files
- [ ] Convert runtime state from YAML to Python dataclasses
- [ ] Add YAML linting to pre-commit hooks

---

### Phase 1: Foundation (Weeks 1-3) - MCP Gateway + DI Container + Documentation Engine

**Goal:** Establish core infrastructure without breaking existing functionality

**Deliverables:**
1. MCP Gateway implementation
2. Dependency Injection container
3. Dev Tools MCP Server (Git, Docker, pytest)
4. Backward compatibility layer (old wrappers → MCP)
5. **CRITICAL:** Minimum foundation for Phase 3 orchestrator migration

---

#### 🚨 CRITICAL: Foundation Prerequisites for Orchestrator Migration

**Before ANY orchestrator can be migrated to CORTEX-4.0 branch, these MUST be completed and operational:**

##### 1. Branch Setup (Week 1, Day 1)
- [ ] Create `CORTEX-4.0` branch from `CORTEX-3.0`
- [ ] Update `.gitignore` for new structure
- [ ] Create new directory structure:
  ```
  src/
  ├── orchestrators/          # New home for all orchestrators
  │   └── base/               # Base orchestrator classes
  │       ├── __init__.py
  │       ├── base_orchestrator.py
  │       ├── phase_manager.py
  │       └── error_handler.py
  ├── di/                     # Dependency injection
  │   ├── __init__.py
  │   ├── container.py
  │   └── decorators.py
  └── mcp/                    # MCP Gateway (can be minimal stub initially)
      └── __init__.py
  ```

##### 2. Base Orchestrator Framework (Week 1, Days 2-3)
**MUST HAVE** - All orchestrators inherit from these:

- [ ] Create `src/orchestrators/base/base_orchestrator.py`:
  ```python
  class BaseOrchestrator:
      """Base class for all CORTEX 4.0 orchestrators."""
      def __init__(self, config: Dict[str, Any]):
          self.config = config
          self.logger = setup_logger(self.__class__.__name__)
          self.brain = BrainInterface()
          self.template_manager = TemplateManager()
      
      def execute(self) -> OrchestratorResult:
          """Main execution method - override in subclasses."""
          raise NotImplementedError
      
      def validate_input(self, params: Dict) -> ValidationResult:
          """Validate orchestrator input."""
          pass
      
      def handle_error(self, error: Exception) -> ErrorResult:
          """Standardized error handling."""
          pass
  ```

- [ ] Create `src/orchestrators/base/phase_manager.py`:
  ```python
  class PhaseManager:
      """Manages orchestrator phases and transitions."""
      def register_phase(self, phase_name: str, phase_func: Callable)
      def execute_phase(self, phase_name: str) -> PhaseResult
      def transition(self, from_phase: str, to_phase: str) -> bool
      def get_current_phase() -> str
      def rollback_phase() -> bool
  ```

- [ ] Create `src/orchestrators/base/error_handler.py`:
  ```python
  class OrchestratorErrorHandler:
      """Centralized error handling for orchestrators."""
      def handle_exception(self, exc: Exception) -> ErrorResponse
      def log_error(self, error: Error) -> None
      def should_retry(self, error: Error) -> bool
      def get_recovery_strategy(self, error: Error) -> RecoveryStrategy
  ```

##### 3. Brain Tiers (Week 1, Days 4-5)
**MUST HAVE** - Orchestrators depend on brain for context and storage:

- [ ] Migrate brain tiers to CORTEX-4.0 structure:
  ```
  src/brain/
  ├── __init__.py
  ├── brain_interface.py      # Unified interface to all tiers
  ├── tier0/                  # Governance (SKULL)
  │   ├── __init__.py
  │   ├── rules_engine.py
  │   └── skull_protector.py
  ├── tier1/                  # Working memory
  │   ├── __init__.py
  │   ├── conversation_manager.py
  │   └── context_resolver.py
  ├── tier2/                  # Knowledge graph
  │   ├── __init__.py
  │   ├── pattern_storage.py
  │   └── knowledge_graph_builder.py
  └── tier3/                  # Dev context
      ├── __init__.py
      ├── git_metrics_collector.py
      └── repository_context.py
  ```

- [ ] Create `src/brain/brain_interface.py`:
  ```python
  class BrainInterface:
      """Unified interface to all 4 brain tiers."""
      def __init__(self):
          self.tier0 = Tier0GovernanceEngine()
          self.tier1 = Tier1WorkingMemory()
          self.tier2 = Tier2KnowledgeGraph()
          self.tier3 = Tier3DevContext()
      
      def query_tier1(self, conversation_id: str) -> Conversation
      def store_pattern_tier2(self, pattern: Pattern) -> bool
      def get_git_metrics_tier3(self, repo: str) -> Metrics
      def check_skull_rule_tier0(self, rule: str) -> RuleResult
  ```

##### 4. Response Template System (Week 2, Days 1-2)
**MUST HAVE** - Orchestrators use templates for user feedback:

- [ ] Migrate response templates:
  ```
  src/templates/
  ├── __init__.py
  ├── template_manager.py
  ├── template_renderer.py
  └── templates/
      └── response-templates.yaml  # Copy from cortex-brain/
  ```

- [ ] Create `src/templates/template_manager.py`:
  ```python
  class TemplateManager:
      """Manages response templates."""
      def __init__(self, template_path: str = None):
          self.templates = self._load_templates(template_path)
      
      def get_template(self, template_name: str) -> str
      def render_template(self, name: str, context: Dict) -> str
      def list_templates() -> List[str]
  ```

##### 5. Configuration System (Week 2, Day 3)
**MUST HAVE** - Orchestrators need configuration:

- [ ] Update `cortex.config.json` for CORTEX-4.0 structure:
  ```json
  {
    "version": "4.0",
    "paths": {
      "orchestrators": "src/orchestrators",
      "brain": "src/brain",
      "templates": "src/templates",
      "mcp_gateway": "src/mcp"
    },
    "brain": {
      "tier1_db": "{repo}/cortex-brain/tier1/conversations.db",
      "tier2_db": "~/.cortex/shared/tier2/knowledge_graph.db",
      "tier3_db": "{repo}/cortex-brain/tier3/git_metrics.db"
    }
  }
  ```

- [ ] Create `src/config/config_manager.py`:
  ```python
  class ConfigManager:
      """Manages CORTEX configuration."""
      def __init__(self, config_path: str = "cortex.config.json"):
          self.config = self._load_config(config_path)
      
      def get(self, key: str, default: Any = None) -> Any
      def get_path(self, path_key: str) -> Path
      def validate_config() -> ValidationResult
  ```

##### 6. Testing Infrastructure (Week 2, Days 4-5)
**MUST HAVE** - Orchestrators need test framework:

**🚨 CRITICAL TEST LOCATION POLICY (SKULL ENFORCEMENT):**

**CORTEX Repository (`tests/` directory):**
- ✅ CORTEX orchestrator tests (ExecutionOrchestrator, TDDOrchestrator, etc.)
- ✅ CORTEX agent tests (intent_router, planning_agent, etc.)
- ✅ CORTEX brain tier tests (tier0, tier1, tier2, tier3)
- ✅ CORTEX toolkit tests (documentation generator, CLI wrappers)
- ✅ CORTEX infrastructure tests (MCP Gateway, DI Container, TemplateManager)
- ✅ CORTEX utility tests (ConfigManager, logger, validators)

**User/Application Repository (e.g., `MyApp/tests/`):**
- ✅ Application unit tests (services, controllers, models)
- ✅ Application integration tests (API endpoints, database)
- ✅ Application e2e tests (user workflows)
- ✅ Application-specific test fixtures

**❌ FORBIDDEN:**
- ❌ Application tests in CORTEX `tests/` directory
- ❌ CORTEX tests in application repositories
- ❌ Mixing CORTEX and application test fixtures

**Enforcement:** Brain Protector (Tier 0) will reject PRs violating this separation.

**Reference:** `cortex-brain/brain-protection-rules.yaml` → `TEST_LOCATION_SEPARATION`, `GIT_ISOLATION_ENFORCEMENT`

**Visual Boundary:**
```
┌─────────────────────────────────────────────────────────────┐
│ CORTEX Repository (github.com/asifhussain60/CORTEX)         │
│                                                             │
│ tests/                                                      │
│ ├── orchestrators/                                          │
│ │   ├── planning/test_planning_orchestrator.py     ✅      │
│ │   ├── tdd/test_tdd_orchestrator.py               ✅      │
│ │   └── execution/test_execution_orchestrator.py   ✅      │
│ ├── agents/                                                │
│ │   └── test_intent_router.py                      ✅      │
│ ├── brain/                                                 │
│ │   └── test_brain_interface.py                    ✅      │
│ └── toolkit/                                               │
│     └── documentation/test_doc_generator.py        ✅      │
│                                                             │
│ ❌ NO APPLICATION TESTS HERE                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ User Repository (e.g., github.com/company/EcommerceApp)     │
│                                                             │
│ tests/                                                      │
│ ├── unit/                                                   │
│ │   ├── test_user_service.py                      ✅      │
│ │   ├── test_order_service.py                     ✅      │
│ │   └── test_product_repository.py                ✅      │
│ ├── integration/                                            │
│ │   └── test_checkout_flow.py                     ✅      │
│ └── e2e/                                                    │
│     └── test_user_journey.py                      ✅      │
│                                                             │
│ ❌ NO CORTEX TESTS HERE                                     │
└─────────────────────────────────────────────────────────────┘
```

- [ ] Set up pytest infrastructure:
  ```
  pytest.ini                  # Pytest configuration
  conftest.py                 # Global fixtures
  
  tests/
  ├── __init__.py
  ├── conftest.py             # Test fixtures
  ├── fixtures/
  │   ├── __init__.py
  │   ├── orchestrator_fixtures.py
  │   ├── brain_fixtures.py
  │   └── mock_data.py
  └── orchestrators/
      └── base/
          └── test_base_orchestrator.py  # Test base classes work
  ```

- [ ] Create `tests/fixtures/orchestrator_fixtures.py`:
  ```python
  # NOTE: These fixtures are for CORTEX INTERNAL TESTS ONLY
  # Application tests should create their own fixtures in {app_repo}/tests/fixtures/
  
  @pytest.fixture
  def mock_brain():
      """Mock brain interface for testing CORTEX orchestrators."""
      return MagicMock(spec=BrainInterface)
  
  @pytest.fixture
  def mock_template_manager():
      """Mock template manager."""
      return MagicMock(spec=TemplateManager)
  
  @pytest.fixture
  def base_orchestrator_config():
      """Standard orchestrator config."""
      return {
          "name": "test_orchestrator",
          "version": "4.0",
          "debug": True
      }
  ```

- [ ] Update `pytest.ini`:
  ```ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = 
      --verbose
      --strict-markers
      --cov=src
      --cov-report=html
      --cov-report=term-missing
  markers =
      unit: Unit tests
      integration: Integration tests
      slow: Slow-running tests
      orchestrator: Orchestrator tests
  ```

##### 7. Dependency Injection Container (Week 3, Days 1-2)
**MUST HAVE** - Orchestrators registered via DI:

- [ ] Create `src/di/container.py`:
  ```python
  from dependency_injector import containers, providers
  
  class CortexContainer(containers.DeclarativeContainer):
      config = providers.Configuration()
      
      # Brain tiers
      brain_interface = providers.Singleton(BrainInterface)
      
      # Template system
      template_manager = providers.Singleton(
          TemplateManager,
          template_path=config.paths.templates
      )
      
      # Base orchestrator (factory)
      base_orchestrator = providers.Factory(
          BaseOrchestrator,
          config=config,
          brain=brain_interface,
          template_manager=template_manager
      )
  ```

- [ ] Create `src/di/decorators.py`:
  ```python
  def orchestrator(name: str, category: str):
      """Decorator for auto-registering orchestrators."""
      def decorator(cls):
          cls._cortex_metadata = {
              "name": name,
              "category": category,
              "type": "orchestrator"
          }
          # Auto-register in container
          CortexContainer.orchestrators[name] = providers.Factory(cls)
          return cls
      return decorator
  ```

##### 8. Logging & Monitoring (Week 3, Day 3)
**MUST HAVE** - Orchestrators need logging:

- [ ] Create `src/logging/logger.py`:
  ```python
  def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
      """Set up standardized logger."""
      logger = logging.getLogger(name)
      logger.setLevel(getattr(logging, level))
      
      # Console handler
      console_handler = logging.StreamHandler()
      console_handler.setFormatter(
          logging.Formatter(
              '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
          )
      )
      logger.addHandler(console_handler)
      
      # File handler (orchestrator-specific)
      file_handler = logging.FileHandler(f'logs/{name}.log')
      file_handler.setFormatter(
          logging.Formatter(
              '%(asctime)s - %(levelname)s - %(message)s'
          )
      )
      logger.addHandler(file_handler)
      
      return logger
  ```

##### 9. Minimal MCP Gateway Stub (Week 3, Day 4)
**OPTIONAL for Phase 3** - Can be basic stub initially:

- [ ] Create `src/mcp/__init__.py`:
  ```python
  # Minimal stub - full implementation in Phase 1
  class MCPGatewayStub:
      """Temporary stub until full MCP Gateway implemented."""
      def invoke_tool(self, tool: str, params: dict) -> dict:
          # Delegate to old wrappers for now
          return legacy_tool_wrapper(tool, params)
  ```

##### 10. Validation Script (Week 3, Day 5)
**MUST HAVE** - Verify foundation ready:

- [ ] Create `scripts/validate_cortex_4_foundation.py`:
  ```python
  def validate_foundation():
      """Validate CORTEX 4.0 foundation ready for orchestrator migration."""
      checks = [
          check_base_orchestrator_exists(),
          check_brain_interface_works(),
          check_template_manager_loads(),
          check_config_valid(),
          check_di_container_initializes(),
          check_pytest_runs(),
          check_logging_works()
      ]
      
      if all(checks):
          print("✅ CORTEX 4.0 foundation ready for orchestrator migration!")
          return True
      else:
          print("❌ Foundation incomplete. Fix issues before migrating orchestrators.")
          return False
  ```

- [ ] Run validation:
  ```bash
  python scripts/validate_cortex_4_foundation.py
  ```

---

#### Foundation Completion Checklist

**Week 1:**
- [ ] CORTEX-4.0 branch created
- [ ] Base orchestrator framework complete (3 classes)
- [ ] Brain tiers migrated and operational

**Week 2:**
- [ ] Response template system migrated
- [ ] Configuration system updated
- [ ] Testing infrastructure complete (pytest + fixtures for CORTEX internal tests only)

**Week 3:**
- [ ] DI container implemented
- [ ] Logging system operational
- [ ] MCP Gateway stub (minimal)
- [ ] Foundation validation passing

**Ready for Phase 3:** Only when ALL above checkboxes complete + validation script passes ✅

---

**Tasks (Remaining Phase 1 Work):**
- [ ] Design MCP protocol schemas (JSON-RPC 2.0)
- [ ] Implement `MCPGateway` with routing + auth
- [ ] Create `dev_tools_server.py` (Git, Docker, pytest)
- [ ] Build `CortexContainer` with DI wiring
- [ ] Create compatibility shim: `old_git_wrapper()` → `mcp_gateway.invoke("git", ...)`
- [ ] Write 40 tests for MCP gateway, circuit breaker, auth
- [ ] Document MCP server development guide

**Migration Approach:** **Non-breaking** - Old code continues working via compatibility layer

### Phase 1.5: Documentation & Visualization Framework (Week 3) - Technical Documentation Tool

**Goal:** Create automated documentation generation system with D3.js visualizations

**Deliverables:**
1. Documentation generator tool in CORTEX 4.0 Toolkit
2. D3.js visualization framework
3. Template system for orchestrator documentation
4. Auto-generation from code annotations
5. Interactive HTML documentation site

**Tasks:**

#### Documentation Generator Tool
- [ ] Create `cortex-toolkit/documentation/generator/`
- [ ] Implement `doc_generator.py` - Main orchestration
  - [ ] `generate_orchestrator_docs(orchestrator_path)` - Per-orchestrator generation
  - [ ] `generate_feature_docs(feature_name)` - Feature documentation
  - [ ] `generate_api_docs(module_path)` - API reference
  - [ ] `generate_architecture_docs()` - System architecture
- [ ] Implement `code_parser.py` - Extract documentation from code
  - [ ] Parse docstrings (Google/NumPy/Sphinx formats)
  - [ ] Extract class/method signatures
  - [ ] Identify dependencies and relationships
  - [ ] Extract workflow annotations (`@workflow_step`, `@phase`)
- [ ] Implement `template_engine.py` - Template-based generation
  - [ ] Jinja2 templates for Markdown/HTML/D3.js
  - [ ] Custom filters for code formatting
  - [ ] Diagram template selection (flowchart/sequence/class)
- [ ] Implement `diagram_generator.py` - D3.js diagram creation
  - [ ] Workflow → Flowchart (D3-graphviz)
  - [ ] Interactions → Sequence diagram (D3-sequence)
  - [ ] Architecture → Component diagram (D3-hierarchy)
  - [ ] Data flow → Sankey/Network diagram
- [ ] Implement `markdown_renderer.py` - Markdown output
- [ ] Implement `html_renderer.py` - Interactive HTML output

#### D3.js Visualization Framework
- [ ] Create `cortex-toolkit/documentation/visualizations/`
- [ ] Implement `d3_flowchart.js` - Workflow flowcharts
  - [ ] Node types: start, process, decision, end
  - [ ] Edge styles: sequential, conditional, loop
  - [ ] Interactive: zoom, pan, node expansion
- [ ] Implement `d3_sequence.js` - Sequence diagrams
  - [ ] Participants: orchestrators, agents, brain tiers
  - [ ] Messages: sync, async, return
  - [ ] Lifelines and activation boxes
- [ ] Implement `d3_architecture.js` - Component diagrams
  - [ ] Components: orchestrators, modules, tools
  - [ ] Relationships: depends-on, uses, extends
  - [ ] Layers: presentation, orchestration, infrastructure
- [ ] Implement `d3_dataflow.js` - Data flow diagrams
  - [ ] Sources: user input, brain tiers, external APIs
  - [ ] Transformations: orchestrators, agents
  - [ ] Sinks: brain tiers, output, external systems
- [ ] Create `visualization_config.yaml` - Diagram styling
  - [ ] Color schemes per orchestrator
  - [ ] Icon mappings (orchestrator types)
  - [ ] Layout algorithms (force-directed, hierarchical, layered)

#### Documentation Templates
- [ ] Create `cortex-toolkit/documentation/templates/`
- [ ] Create `orchestrator_template.md.j2`
  - [ ] Overview section
  - [ ] Architecture diagram (auto-select type)
  - [ ] Workflow/phases section with flowchart
  - [ ] API reference
  - [ ] Configuration options
  - [ ] Examples
  - [ ] Testing guide
- [ ] Create `feature_template.md.j2`
  - [ ] Feature description
  - [ ] Use cases
  - [ ] Architecture integration
  - [ ] Configuration
  - [ ] Examples
- [ ] Create `api_template.md.j2`
  - [ ] Module overview
  - [ ] Class/function reference
  - [ ] Parameters and return types
  - [ ] Examples

#### Code Annotations for Auto-Generation
- [ ] Define documentation decorators:
  - [ ] `@workflow_step(name, description, diagram_type)` - Document workflow steps
  - [ ] `@phase(name, order, dependencies)` - Document orchestrator phases
  - [ ] `@diagram(type, layout)` - Specify diagram type (flowchart/sequence/class)
  - [ ] `@interaction(from, to, message)` - Document component interactions
- [ ] Example usage:
```python
@orchestrator(name="planning", category="Planning System 3.0")
@diagram(type="flowchart", layout="hierarchical")
class PlanningOrchestrator:
    """Planning System 3.0 orchestrator.
    
    Generates feature implementation plans with DoR/DoD compliance.
    Supports incremental, conditional, and skeleton plan types.
    """
    
    @phase(name="analyze_complexity", order=1)
    @workflow_step("Complexity Analysis", "Analyze feature complexity and select plan type")
    def analyze_complexity(self, feature: str) -> ComplexityLevel:
        """Analyze feature complexity.
        
        Args:
            feature: Feature description
            
        Returns:
            ComplexityLevel: HIGH, MEDIUM, or LOW
        """
        pass
```

#### Interactive Documentation Site
- [ ] Create `cortex-toolkit/documentation/site/`
- [ ] Implement `site_generator.py` - Static site generation
  - [ ] Generate index.html with navigation
  - [ ] Per-orchestrator pages with embedded D3.js
  - [ ] Search functionality (Lunr.js)
  - [ ] Dark/light theme toggle
- [ ] Create `site_template.html.j2` - HTML template
  - [ ] Sidebar navigation (orchestrators, features, toolkit)
  - [ ] Content area with Markdown rendering
  - [ ] D3.js diagram containers
  - [ ] Code syntax highlighting (Prism.js)

#### Documentation Standards
- [ ] Create `DOCUMENTATION-STANDARDS.md`
  - [ ] Docstring format (Google style)
  - [ ] Annotation requirements
  - [ ] Diagram type selection guide
  - [ ] Update frequency (on code change)
- [ ] Create pre-commit hook: validate docstrings
- [ ] CI check: regenerate docs on PR

**Per-Orchestrator Documentation Requirements:**

| Orchestrator | Primary Diagram | Secondary Diagrams | Key Sections |
|--------------|-----------------|--------------------|--------------|
| Planning | Flowchart (phases) | Sequence (complexity analysis) | DoR/DoD, Plan types, TDD integration |
| TDD | Flowchart (RED→GREEN→REFACTOR) | Sequence (test generation) | Phase validation, Coverage requirements |
| Execution | Flowchart (phase execution) | Architecture (multi-orchestrator routing) | Phase management, Error handling |
| ADO | Flowchart (work item creation) | Sequence (API interactions) | Work item types, Completion summaries |
| Maintenance | Flowchart (7 phases) | Data flow (health metrics) | Phase sequence, Optimization strategies |
| Scaffolding | Flowchart (generation steps) | Architecture (pattern recognition) | Architecture patterns, Migration strategies |
| Documentation | Flowchart (doc generation) | Data flow (code → docs) | Auto-generation, Template system |
| QA | Flowchart (quality checks) | Sequence (analysis pipeline) | Code quality metrics, Remediation |
| DevOps | Flowchart (CI/CD pipeline) | Sequence (deployment) | Pipeline stages, Environment config |
| Observability | Architecture (monitoring) | Data flow (metrics collection) | Health metrics, Alerting |
| Intelligence | Architecture (learning system) | Data flow (pattern extraction) | Pattern learning, Recommendations |
| Onboarding | Flowchart (onboarding steps) | Sequence (user interaction) | Setup guides, Interactive demos |

**Tests:**
- [ ] `test_doc_generator.py` (15 tests)
- [ ] `test_code_parser.py` (12 tests)
- [ ] `test_diagram_generator.py` (10 tests)
- [ ] `test_template_engine.py` (8 tests)
- [ ] Integration: `test_full_doc_generation.py` (5 tests)

**CLI Integration:**
```bash
# Generate all documentation
cortex-toolkit docs generate --all

# Generate orchestrator-specific docs
cortex-toolkit docs generate --orchestrator planning

# Generate with specific diagram type
cortex-toolkit docs generate --orchestrator tdd --diagram flowchart

# Serve interactive documentation site
cortex-toolkit docs serve --port 8000

# Export to PDF
cortex-toolkit docs export --format pdf --output cortex-4.0-technical-docs.pdf
```

**Migration Approach:** **Incremental** - Generate docs per orchestrator as they're migrated in Phase 3

---

### Phase 2: Brain Enhancement (Weeks 4-6) - Hybrid Centralization

**Goal:** Implement shared templates + Tier 2 centralization

**Deliverables:**
1. `~/.cortex/shared/` directory structure
2. Centralized response templates
3. Tier 2 knowledge graph with namespace isolation
4. Migration tool for existing repos

**Tasks:**
- [ ] Create `~/.cortex/shared/` folder structure
- [ ] Migrate `response-templates.yaml` to shared location
- [ ] Update `TemplateManager` to load from `~/.cortex/shared/`
- [ ] Implement namespace isolation in Tier 2 (`repository_id` column)
- [ ] Build migration script: `python migrate_brain.py --repo <path>`
- [ ] Add privacy controls (private-by-default patterns)
- [ ] Cross-repo pattern discovery API
- [ ] Write 35 tests for namespace isolation, template loading, migration
- [ ] Update documentation

**Migration Approach:** **Opt-in** - Users manually run migration script per repo

### Phase 3: Orchestrator Consolidation (Weeks 7-11) - Clean Structure + TDD + Documentation

**Goal:** Migrate orchestrators to clean structure with co-located tests + auto-generated technical documentation

**⚠️ PREREQUISITE:** Phase 1 foundation validation MUST pass before starting Phase 3. See [Foundation Prerequisites](#-critical-foundation-prerequisites-for-orchestrator-migration) section.

**🚨 TEST LOCATION POLICY FOR PHASE 3:**

During orchestrator migration, you will create TWO types of tests:

1. **CORTEX Orchestrator Tests** (in CORTEX repository)
   - Location: `src/orchestrators/{orchestrator_name}/tests/`
   - Purpose: Test the orchestrator logic itself
   - Example: `src/orchestrators/planning/tests/test_planning_orchestrator.py`
   - Coverage: Orchestrator methods, phase management, error handling

2. **Application Tests** (in USER repository - if orchestrator generates them)
   - Location: `{user_repo}/tests/`
   - Purpose: Test the application code generated by orchestrator
   - Example: If PlanningOrchestrator generates `UserService.cs`, tests go in `{user_repo}/tests/UserServiceTests.cs`
   - Coverage: Application business logic, NOT orchestrator logic

**Example Scenario - Planning Orchestrator:**
```
CORTEX Repository:
  src/orchestrators/planning/tests/
    ├── test_planning_orchestrator.py      # Tests PlanningOrchestrator.generate_plan()
    ├── test_complexity_analyzer.py        # Tests complexity detection logic
    └── test_plan_generator.py             # Tests plan generation logic

User Repository (e.g., EcommerceApp):
  tests/
    ├── test_user_service.py               # Tests UserService generated by orchestrator
    ├── test_order_controller.py           # Tests OrderController generated by orchestrator
    └── integration/
        └── test_checkout_flow.py          # Tests checkout flow implemented from plan
```

**Rule of Thumb:** If the test validates CORTEX orchestrator behavior → CORTEX repo. If the test validates application code → User repo.

---

#### Foundation Dependency Matrix

**Before migrating ANY orchestrator, verify these are complete on CORTEX-4.0 branch:**

| Component | Required For | Validation Test |
|-----------|-------------|-----------------|
| BaseOrchestrator | All orchestrators inherit from this | `test_base_orchestrator.py` passes |
| PhaseManager | ExecutionOrchestrator, TDDOrchestrator, PlanningOrchestrator | `test_phase_manager.py` passes |
| BrainInterface | All orchestrators (context/storage) | `test_brain_interface.py` passes |
| TemplateManager | All orchestrators (user feedback) | `test_template_manager.py` passes |
| ConfigManager | All orchestrators (configuration) | `test_config_manager.py` passes |
| DI Container | Orchestrator registration | `test_di_container.py` passes |
| Pytest Infrastructure | All orchestrator tests | `pytest tests/orchestrators/base/` passes |
| Logging System | All orchestrators (observability) | `test_logger.py` passes |

**Validation Command:**
```bash
# Run BEFORE starting Phase 3
python scripts/validate_cortex_4_foundation.py

# Expected output:
# ✅ Base orchestrator framework: PASS
# ✅ Brain interface: PASS
# ✅ Template manager: PASS
# ✅ Configuration system: PASS
# ✅ DI container: PASS
# ✅ Pytest infrastructure: PASS
# ✅ Logging system: PASS
# ✅ Foundation ready for orchestrator migration!
```

**If validation fails:** DO NOT proceed with orchestrator migration. Fix foundation issues first.

---

**Documentation Requirements (Per Orchestrator):**
- ✅ Architecture diagram (auto-selected type based on orchestrator purpose)
- ✅ Workflow flowchart (if orchestrator has phases/steps)
- ✅ Sequence diagram (if orchestrator interacts with multiple components)
- ✅ API reference (generated from docstrings)
- ✅ Configuration guide
- ✅ Usage examples
- ✅ Testing guide

**Migration Order (Dependency-First):**

#### Week 7: Core Orchestrators
1. **ExecutionOrchestrator** (Foundation - all others depend on it)
   - Migrate to `src/orchestrators/execution/`
   - Add co-located tests
   - 85%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (phase execution logic)
     - Secondary: Architecture diagram (multi-orchestrator routing)
     - Sections: Phase management, Error handling, Routing strategy
   
2. **TDDOrchestrator** (Critical path - used by all feature work)
   - **Architecture Design:** See [TDD-ORCHESTRATOR-REDESIGN.md](./TDD-ORCHESTRATOR-REDESIGN.md) for complete redesign
   - Consolidate 2 implementations (orchestration_3_0 + workflows) into unified strategy-pattern orchestrator
   - Migrate to `src/orchestrators/tdd/` with strategy pattern (RED/GREEN/REFACTOR strategies)
   - Add comprehensive test suite
   - 90%+ coverage (TDD for TDD!)
   - **Key innovations:** AI-driven code generation, LLM refactoring, rollback safety, continuous monitoring
   - **Generate documentation:**
     - Primary: Flowchart (RED→GREEN→REFACTOR cycle)
     - Secondary: Sequence diagram (test generation flow)
     - Sections: Phase validation, Coverage requirements, Implementation strategies, Strategy pattern

#### Week 8: Planning System
3. **PlanningOrchestrator** (High complexity, well-tested)
   - Already 1,599 LOC - refactor into 4 modules
   - Migrate to `src/orchestrators/planning/`
   - Split: orchestrator (800), complexity_analyzer (300), dor_validator (200), plan_generator (400)
   - Migrate 4 existing test files
   - 85%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (planning phases)
     - Secondary: Sequence diagram (complexity analysis interaction)
     - Sections: DoR/DoD requirements, Plan types (incremental/conditional/skeleton), TDD integration, Acceptance criteria

4. **ScaffoldingOrchestrator** (Complex, 5 support modules)
   - Consolidate architecture_intelligence, code_analyzer, migration_strategist, orchestrator_chain
   - Migrate to `src/orchestrators/scaffolding/`
   - 80%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (scaffolding generation steps)
     - Secondary: Architecture diagram (pattern recognition engine)
     - Sections: Architecture patterns (Clean/DDD/Microservices), Migration strategies, Code analysis

#### Week 9: Domain-Specific Orchestrators
5. **ADOOrchestrator** (Consolidate all ADO operations)
   - Combine: ado_agent, ado work item operations, ado_planning
   - Migrate to `src/orchestrators/ado/`
   - 80%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (work item creation flow)
     - Secondary: Sequence diagram (ADO API interactions)
     - Sections: Work item types (Story/Feature/Task), Completion summaries, Code review integration

6. **DocumentationOrchestrator** (Consolidate 2 implementations)
   - Merge: documentation_orchestrator + documentation_generation_orchestrator
   - Migrate to `src/orchestrators/documentation/`
   - 75%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (documentation generation pipeline)
     - Secondary: Data flow diagram (code → documentation transformation)
     - Sections: Auto-generation strategies, Template system, D3.js integration

#### Week 10: Operations Orchestrators
7. **MaintenanceOrchestrator** (Consolidate cleanup + optimization)
   - Merge: cleanup_orchestrator, holistic_cleanup, user_cleanup, optimize_cortex, optimize_system
   - Migrate to `src/orchestrators/maintenance/`
   - Split: orchestrator, cleanup_engine, optimization_engine
   - 80%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (7-phase maintenance workflow)
     - Secondary: Data flow diagram (health metrics collection)
     - Sections: Phase sequence, Optimization strategies, Cleanup rules, Health monitoring

8. **QAOrchestrator** (Quality automation)
   - Already in orchestration_3_0, migrate to new structure
   - Add code_quality_orchestrator, holistic_review_orchestrator
   - 75%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (quality check pipeline)
     - Secondary: Sequence diagram (analysis workflow)
     - Sections: Code quality metrics, Review automation, Remediation strategies

9. **DevOpsOrchestrator** (CI/CD automation)
   - Add deployment_orchestrator, integration_testing_orchestrator
   - 75%+ coverage
   - **Generate documentation:**
     - Primary: Flowchart (CI/CD pipeline stages)
     - Secondary: Sequence diagram (deployment process)
     - Sections: Pipeline configuration, Environment management, Integration testing

#### Week 11: Supporting Orchestrators
10. **ObservabilityOrchestrator** (Monitoring + health)
    - Add performance_profiling_orchestrator, resource_management_orchestrator
    - 70%+ coverage
    - **Generate documentation:**
      - Primary: Architecture diagram (monitoring system components)
      - Secondary: Data flow diagram (metrics collection and aggregation)
      - Sections: Health metrics, Performance profiling, Alerting system, Resource tracking

11. **IntelligenceOrchestrator** (Pattern learning)
    - Already in orchestration_3_0
    - 70%+ coverage
    - **Generate documentation:**
      - Primary: Architecture diagram (learning system architecture)
      - Secondary: Data flow diagram (pattern extraction pipeline)
      - Sections: Pattern learning, Cross-repo insights, Recommendation engine

12. **OnboardingOrchestrator** (Developer experience)
    - Consolidate onboarding_orchestrator + demo_orchestrator
    - 75%+ coverage
    - **Generate documentation:**
      - Primary: Flowchart (onboarding steps)
      - Secondary: Sequence diagram (user interaction flow)
      - Sections: Setup guides, Interactive demos, Developer tutorials

**Consolidation Strategy:**

| New Orchestrator | Consolidates (Old) | Reduction |
|-----------------|-------------------|-----------|
| MaintenanceOrchestrator | cleanup_orchestrator, holistic_cleanup_orchestrator, user_cleanup_orchestrator, optimize_cortex_orchestrator, optimize_system_orchestrator | 5 → 1 |
| DocumentationOrchestrator | documentation_orchestrator, documentation_generation_orchestrator | 2 → 1 |
| ADOOrchestrator | ado_agent, ado work item operations, ado_planning_orchestrator | 3 → 1 |
| QAOrchestrator | qa_orchestrator, code_quality_orchestrator, holistic_review_orchestrator | 3 → 1 |
| DevOpsOrchestrator | devops_orchestrator, deployment_orchestrator, integration_testing_orchestrator | 3 → 1 |
| OnboardingOrchestrator | onboarding_orchestrator, demo_orchestrator | 2 → 1 |

**Result:** 28 orchestrators → 12 consolidated orchestrators (57% reduction)

### Phase 4: Operations Simplification (Weeks 12-14) - Manifest Reduction

**Goal:** Replace cortex-operations.yaml with DI container auto-discovery

**Deliverables:**
1. `@orchestrator` decorator for auto-registration
2. Metadata-only YAML (500 lines vs 6,760)
3. Dynamic operation routing via DI container
4. Backward compatibility for natural language commands

**Tasks:**
- [ ] Implement `@orchestrator` decorator
- [ ] Auto-discovery system for decorated classes
- [ ] Reduce `cortex-operations.yaml` to metadata only
- [ ] Update `OperationsOrchestrator` to use DI container
- [ ] Create operation alias system (natural language → orchestrator)
- [ ] Write 30 tests for auto-discovery, routing
- [ ] Migration guide for custom operations

**Reduction:**
```
Before: 6,760 lines (operations + modules + wiring + profiles)
After:  500 lines (descriptions + examples only)
        Wiring → DI Container (code)
```

### Phase 5: Testing & Validation (Weeks 15-16) - Quality Gates

**Goal:** Ensure 85%+ coverage, all orchestrators tested

**Deliverables:**
1. Comprehensive test suite (500+ tests)
2. Integration tests (orchestrator interactions)
3. Performance benchmarks
4. Migration validation report

**Tasks:**
- [ ] Run full test suite: `pytest tests/`
- [ ] Measure coverage: `pytest --cov=src tests/`
- [ ] Fix coverage gaps (target 85%+)
- [ ] Integration tests (10 critical paths)
- [ ] Performance benchmarks (ensure <10% regression)
- [ ] Test backward compatibility (old operations still work)
- [ ] Load testing (100 concurrent operations)
- [ ] Document test strategy

**Quality Gates:**
- ✅ 85%+ code coverage
- ✅ 0 critical bugs
- ✅ All smoke tests passing
- ✅ <10% performance regression
- ✅ Backward compatibility verified

### Phase 6: Documentation Finalization (Week 18) - Complete Technical Documentation

**Goal:** Generate complete technical documentation for all CORTEX 4.0 components

**Deliverables:**
1. Interactive documentation website (HTML + D3.js)
2. PDF export of complete technical documentation
3. Per-orchestrator documentation with diagrams (12 orchestrators)
4. Feature documentation (5 major features)
5. API reference documentation
6. Architecture overview documentation
7. CORTEX Lens documentation

**Tasks:**

#### Generate All Documentation
- [ ] Run documentation generator for all orchestrators:
  ```bash
  cortex-toolkit docs generate --all
  ```
- [ ] Verify all D3.js diagrams render correctly:
  - [ ] 12 orchestrator flowcharts
  - [ ] 12 sequence diagrams (where applicable)
  - [ ] 8 architecture diagrams
  - [ ] 5 data flow diagrams
- [ ] Generate feature documentation:
  - [ ] Planning System 3.0
  - [ ] TDD Mastery
  - [ ] Code Sanitization
  - [ ] ADO Integration
  - [ ] System Maintenance
- [ ] Generate API reference documentation:
  - [ ] MCP Protocol API
  - [ ] Orchestrator API
  - [ ] Brain Tier API
  - [ ] Agent API
- [ ] Generate toolkit documentation:
  - [ ] CLI commands reference
  - [ ] Documentation generator guide
  - [ ] Testing framework guide
  - [ ] Migration utilities guide
- [ ] Generate CORTEX Lens documentation:
  - [ ] Landing page generator
  - [ ] Comparison engine
  - [ ] Visualization engine

#### Build Interactive Documentation Site
- [ ] Generate static site:
  ```bash
  cortex-toolkit docs build --output docs/cortex-4.0
  ```
- [ ] Test interactive features:
  - [ ] Navigation sidebar
  - [ ] Search functionality
  - [ ] Dark/light theme toggle
  - [ ] D3.js diagram interactivity (zoom, pan, expand)
  - [ ] Code syntax highlighting
- [ ] Serve locally for review:
  ```bash
  cortex-toolkit docs serve --port 8000
  ```
- [ ] Deploy to GitHub Pages:
  ```bash
  cortex-toolkit docs deploy --github-pages
  ```

#### Export to PDF
- [ ] Generate comprehensive PDF:
  ```bash
  cortex-toolkit docs export --format pdf --output CORTEX-4.0-Technical-Documentation.pdf
  ```
- [ ] Include all sections:
  - [ ] Table of contents with page numbers
  - [ ] Architecture overview
  - [ ] All orchestrator documentation
  - [ ] Feature documentation
  - [ ] API reference
  - [ ] Appendices (glossary, references)

#### Documentation Review & Quality Check
- [ ] Peer review by technical team
- [ ] Validate all code examples compile
- [ ] Verify all diagrams match implementation
- [ ] Check for broken links
- [ ] Spelling and grammar check
- [ ] Ensure consistent formatting
- [ ] Verify all screenshots are up-to-date

#### Documentation Maintenance Plan
- [ ] Create `DOCUMENTATION-MAINTENANCE.md`:
  - [ ] Update frequency (per release)
  - [ ] CI/CD integration (auto-generate on merge)
  - [ ] Review process
  - [ ] Diagram update process
- [ ] Set up GitHub Actions workflow:
  - [ ] Auto-generate docs on PR
  - [ ] Validate docs build successfully
  - [ ] Deploy to GitHub Pages on main branch merge

**Quality Gates:**
- ✅ All 12 orchestrators have complete documentation
- ✅ All D3.js diagrams render without errors
- ✅ Interactive documentation site functional
- ✅ PDF export complete (<50MB)
- ✅ 100% of public APIs documented
- ✅ All code examples validated

**Total Time:** 40 hours (1 week)

---

## 📂 CORTEX 4.0 Technical Documentation Structure

**Location:** `cortex-brain/documents/technical/cortex-4.0/`

```
cortex-brain/documents/technical/cortex-4.0/
├── README.md                                 # Overview and navigation guide
├── GETTING-STARTED.md                        # Quick start for new developers
├── ARCHITECTURE-OVERVIEW.md                  # High-level system architecture
│
├── architecture/                             # System architecture documentation
│   ├── overview.md                           # Complete system architecture
│   ├── mcp-gateway.md                        # MCP Gateway design and implementation
│   ├── brain-enhancement.md                  # Brain tier architecture (Tier 0-3)
│   ├── dependency-injection.md               # DI container design
│   ├── orchestrator-framework.md             # Orchestrator base architecture
│   ├── agent-framework.md                    # Agent architecture
│   └── diagrams/                             # Architecture diagrams
│       ├── system-overview.svg               # Complete system diagram
│       ├── mcp-gateway-flow.svg              # MCP request flow
│       ├── brain-tiers.svg                   # Brain tier interactions
│       └── orchestrator-lifecycle.svg        # Orchestrator execution lifecycle
│
├── orchestrators/                            # Per-orchestrator technical docs
│   ├── README.md                             # Orchestrator index
│   ├── planning/
│   │   ├── README.md                         # Planning orchestrator overview
│   │   ├── architecture.md                   # Component architecture
│   │   ├── workflows.md                      # Planning workflows (DoR/DoD)
│   │   ├── api-reference.md                  # API documentation
│   │   ├── configuration.md                  # Configuration options
│   │   ├── examples.md                       # Usage examples
│   │   ├── testing.md                        # Testing guide
│   │   └── diagrams/
│   │       ├── planning-workflow.html        # D3.js flowchart (interactive)
│   │       ├── complexity-analysis.html      # D3.js sequence diagram
│   │       └── components.html               # D3.js architecture diagram
│   ├── tdd/
│   │   ├── README.md
│   │   ├── architecture.md
│   │   ├── workflows.md                      # RED→GREEN→REFACTOR workflow
│   │   ├── api-reference.md
│   │   ├── configuration.md
│   │   ├── examples.md
│   │   ├── testing.md
│   │   └── diagrams/
│   │       ├── tdd-cycle.html                # D3.js flowchart
│   │       ├── test-generation.html          # D3.js sequence diagram
│   │       └── phase-validation.html         # D3.js state diagram
│   ├── execution/
│   │   └── [same structure as above]
│   ├── ado/
│   │   └── [same structure as above]
│   ├── maintenance/
│   │   └── [same structure as above]
│   ├── scaffolding/
│   │   └── [same structure as above]
│   ├── documentation/
│   │   └── [same structure as above]
│   ├── qa/
│   │   └── [same structure as above]
│   ├── devops/
│   │   └── [same structure as above]
│   ├── observability/
│   │   └── [same structure as above]
│   ├── intelligence/
│   │   └── [same structure as above]
│   └── onboarding/
│       └── [same structure as above]
│
├── features/                                 # Feature-specific documentation
│   ├── README.md                             # Feature index
│   ├── planning-system-3.0/
│   │   ├── overview.md                       # Feature overview
│   │   ├── user-guide.md                     # End-user guide
│   │   ├── technical-design.md               # Technical implementation
│   │   ├── configuration.md                  # Configuration options
│   │   ├── examples.md                       # Usage examples
│   │   └── diagrams/
│   │       ├── feature-flow.html             # D3.js workflow
│   │       └── integration-points.html       # D3.js integration diagram
│   ├── tdd-mastery/
│   │   └── [same structure as above]
│   ├── code-sanitization/
│   │   └── [same structure as above]
│   ├── ado-integration/
│   │   └── [same structure as above]
│   └── system-maintenance/
│       └── [same structure as above]
│
├── toolkit/                                  # CORTEX 4.0 Toolkit documentation
│   ├── README.md                             # Toolkit overview
│   ├── cli-commands/
│   │   ├── overview.md                       # CLI architecture
│   │   ├── command-reference.md              # Complete command reference
│   │   └── examples.md                       # CLI usage examples
│   ├── documentation-generator/
│   │   ├── overview.md                       # Doc generator architecture
│   │   ├── usage-guide.md                    # How to use doc generator
│   │   ├── templates.md                      # Template customization
│   │   ├── d3js-diagrams.md                  # D3.js diagram types
│   │   └── extending.md                      # Adding new diagram types
│   ├── testing-framework/
│   │   ├── overview.md                       # Testing framework architecture
│   │   ├── writing-tests.md                  # Test authoring guide
│   │   ├── fixtures.md                       # Test fixtures and mocks
│   │   └── coverage.md                       # Coverage requirements
│   └── migration-utilities/
│       ├── overview.md                       # Migration tools overview
│       ├── brain-migration.md                # Brain tier migration
│       ├── orchestrator-migration.md         # Orchestrator migration
│       └── operation-migration.md            # Operation migration
│
├── cortex-lens/                              # CORTEX Lens documentation
│   ├── README.md                             # CORTEX Lens overview
│   ├── landing-page-generator/
│   │   ├── architecture.md                   # Generator architecture
│   │   ├── templates.md                      # Page templates
│   │   ├── customization.md                  # Customization options
│   │   └── diagrams/
│   │       └── generation-flow.html          # D3.js workflow
│   ├── comparison-engine/
│   │   ├── architecture.md                   # Comparison engine design
│   │   ├── algorithms.md                     # Comparison algorithms
│   │   ├── visualization.md                  # Visualization options
│   │   └── diagrams/
│   │       └── comparison-pipeline.html      # D3.js data flow
│   └── visualization-engine/
│       ├── architecture.md                   # Visualization architecture
│       ├── d3js-integration.md               # D3.js integration
│       ├── chart-types.md                    # Available chart types
│       └── diagrams/
│           └── rendering-pipeline.html       # D3.js rendering flow
│
├── api/                                      # API reference documentation
│   ├── README.md                             # API overview
│   ├── mcp-protocol/
│   │   ├── specification.md                  # MCP protocol spec
│   │   ├── request-response.md               # Request/response formats
│   │   ├── authentication.md                 # Auth mechanisms
│   │   └── error-codes.md                    # Error code reference
│   ├── orchestrator-api/
│   │   ├── base-orchestrator.md              # BaseOrchestrator API
│   │   ├── lifecycle-methods.md              # Lifecycle methods
│   │   ├── phase-management.md               # Phase management API
│   │   └── error-handling.md                 # Error handling API
│   ├── brain-api/
│   │   ├── tier0-api.md                      # Tier 0 (Governance) API
│   │   ├── tier1-api.md                      # Tier 1 (Working Memory) API
│   │   ├── tier2-api.md                      # Tier 2 (Knowledge Graph) API
│   │   └── tier3-api.md                      # Tier 3 (Dev Context) API
│   └── agent-api/
│       ├── base-agent.md                     # BaseAgent API
│       ├── intent-routing.md                 # Intent routing API
│       └── learning-api.md                   # Learning API
│
├── diagrams/                                 # Shared diagrams
│   ├── README.md                             # Diagram index
│   ├── flowcharts/                           # Workflow diagrams
│   │   └── [generated D3.js flowcharts]
│   ├── sequence/                             # Interaction diagrams
│   │   └── [generated D3.js sequence diagrams]
│   ├── architecture/                         # Component diagrams
│   │   └── [generated D3.js architecture diagrams]
│   └── data-flow/                            # Data flow diagrams
│       └── [generated D3.js data flow diagrams]
│
├── guides/                                   # Technical guides
│   ├── contributing.md                       # Contribution guide
│   ├── coding-standards.md                   # Coding standards
│   ├── documentation-standards.md            # Documentation standards
│   ├── testing-standards.md                  # Testing standards
│   └── release-process.md                    # Release process
│
└── appendices/                               # Additional resources
    ├── glossary.md                           # Technical glossary
    ├── references.md                         # External references
    ├── changelog.md                          # Version changelog
    └── migration-guide-3.0-to-4.0.md         # Migration guide from 3.0
```

**Documentation Format Standards:**

1. **README.md (Each Directory):**
   - Overview of the component/feature
   - Quick navigation to subdocuments
   - Key concepts and terminology
   - Links to related documentation

2. **architecture.md (Each Component):**
   - Component purpose and responsibilities
   - High-level architecture diagram (D3.js)
   - Key design decisions and rationale
   - Dependencies and relationships
   - Extension points

3. **workflows.md (Orchestrators/Features):**
   - Step-by-step workflow descriptions
   - Interactive D3.js flowcharts
   - Decision points and branching logic
   - Error handling and recovery
   - Performance considerations

4. **api-reference.md (All Components):**
   - Complete API documentation (auto-generated from docstrings)
   - Class/method signatures
   - Parameters and return types
   - Exceptions raised
   - Code examples for each method

5. **configuration.md (Configurable Components):**
   - All configuration options
   - Default values
   - Environment-specific configurations
   - Configuration validation rules
   - Migration notes for config changes

6. **examples.md (All Components):**
   - Basic usage examples
   - Advanced use cases
   - Common patterns
   - Anti-patterns to avoid
   - Integration examples

7. **testing.md (All Components):**
   - Test structure and organization
   - How to run tests
   - Writing new tests
   - Mocking and fixtures
   - Coverage requirements

**Total Documentation Estimate:**
- **Pages:** ~200 Markdown documents
- **Interactive Diagrams:** ~60 D3.js visualizations
- **Code Examples:** ~300 examples
- **Size:** ~500KB Markdown + ~2MB HTML (with D3.js) + ~10MB PDF

---

## 📊 Implementation Checklist

### Phase 1: Foundation (Weeks 1-3)

#### MCP Gateway
- [ ] Define MCP protocol schemas (JSON-RPC 2.0)
- [ ] Implement `MCPGateway` class
  - [ ] `invoke_tool(tool_name, params, context)` method
  - [ ] Route to appropriate MCP server
  - [ ] Authentication and authorization
  - [ ] Request/response transformation
- [ ] Implement `AuthManager`
  - [ ] User-level permissions
  - [ ] Tool-level access control
  - [ ] Audit logging
- [ ] Implement `CircuitBreaker`
  - [ ] Failure detection
  - [ ] Automatic fallback
  - [ ] Recovery strategy
- [ ] Implement `LoadBalancer`
  - [ ] Multi-server distribution
  - [ ] Health checks
  - [ ] Weighted routing

#### Dev Tools MCP Server
- [ ] Create `dev_tools_server.py`
- [ ] Implement Git operations
  - [ ] `git_commit(message, files)`
  - [ ] `git_push(remote, branch)`
  - [ ] `git_checkout(branch)`
  - [ ] `git_status()`
- [ ] Implement Docker operations
  - [ ] `docker_build(context, tag)`
  - [ ] `docker_run(image, args)`
  - [ ] `docker_stop(container_id)`
- [ ] Implement Test operations
  - [ ] `pytest_run(tests, coverage)`
  - [ ] `coverage_report()`

#### Dependency Injection Container
- [ ] Install `dependency-injector` package
- [ ] Create `src/di/container.py`
- [ ] Implement `CortexContainer`
  - [ ] Configuration providers
  - [ ] Singleton providers (Brain tiers, MCP gateway)
  - [ ] Factory providers (Orchestrators)
- [ ] Create `@orchestrator` decorator
- [ ] Implement auto-discovery system
- [ ] Create compatibility shim for old wrappers

#### Tests
- [ ] `test_mcp_gateway.py` (15 tests)
- [ ] `test_auth_manager.py` (10 tests)
- [ ] `test_circuit_breaker.py` (8 tests)
- [ ] `test_dev_tools_server.py` (12 tests)
- [ ] `test_di_container.py` (10 tests)
- [ ] Integration: `test_mcp_e2e.py` (5 tests)

### Phase 2: Brain Enhancement (Weeks 4-6)

#### Shared Templates
- [ ] Create `~/.cortex/shared/` directory
- [ ] Move `response-templates.yaml` to shared location
- [ ] Update `TemplateManager` to load from shared path
- [ ] Implement fallback (shared → local)
- [ ] Add version compatibility check

#### Tier 2 Centralization
- [ ] Design namespace isolation schema
  - [ ] Add `repository_id` column to patterns table
  - [ ] Add `is_private` flag
  - [ ] Add `shared_with` JSON array
- [ ] Migrate `knowledge_graph.db` to `~/.cortex/shared/tier2/`
- [ ] Update all Tier 2 queries with namespace parameter
- [ ] Implement privacy controls
  - [ ] Private-by-default patterns
  - [ ] Explicit sharing API
  - [ ] Namespace permissions
- [ ] Cross-repo pattern discovery
  - [ ] `find_similar_patterns(current_pattern, other_repos)`
  - [ ] Confidence scoring
  - [ ] Recommendation engine

#### Migration Tool
- [ ] Create `scripts/migrate_brain.py`
- [ ] Backup existing brain files
- [ ] Copy Tier 2 data to shared location
- [ ] Add namespace tags
- [ ] Validate migration
- [ ] Rollback capability

#### Tests
- [ ] `test_shared_templates.py` (10 tests)
- [ ] `test_namespace_isolation.py` (12 tests)
- [ ] `test_privacy_controls.py` (8 tests)
- [ ] `test_cross_repo_discovery.py` (10 tests)
- [ ] `test_brain_migration.py` (8 tests)

### Phase 3: Orchestrator Consolidation (Weeks 7-11)

#### Week 7: Core Orchestrators

**ExecutionOrchestrator:**
- [ ] Create `src/orchestrators/execution/`
- [ ] Migrate `execution_orchestrator.py`
- [ ] Create `tests/test_execution_orchestrator.py`
- [ ] Refactor phase execution logic
- [ ] Add error handling
- [ ] Achieve 85%+ coverage

**TDDOrchestrator:**
- [ ] Create `src/orchestrators/tdd/`
- [ ] Consolidate 5 files into module
  - [ ] `tdd_orchestrator.py` (main)
  - [ ] `test_generator.py`
  - [ ] `implementation_engine.py`
  - [ ] `refactoring_engine.py`
  - [ ] `phase_validator.py`
- [ ] Create comprehensive test suite
  - [ ] `tests/test_tdd_orchestrator.py`
  - [ ] `tests/test_test_generator.py`
  - [ ] `tests/test_implementation_engine.py`
  - [ ] `tests/test_refactoring_engine.py`
- [ ] Achieve 90%+ coverage (TDD for TDD!)

#### Week 8: Planning System

**PlanningOrchestrator:**
- [ ] Create `src/orchestrators/planning/`
- [ ] Split 1,599 LOC into 4 modules:
  - [ ] `planning_orchestrator.py` (800 LOC)
  - [ ] `complexity_analyzer.py` (300 LOC)
  - [ ] `dor_validator.py` (200 LOC)
  - [ ] `plan_generator.py` (400 LOC)
- [ ] Migrate 4 existing test files
  - [ ] `tests/test_planning_orchestrator.py`
  - [ ] `tests/test_complexity_analyzer.py`
  - [ ] `tests/test_dor_validator.py`
  - [ ] `tests/test_plan_generator.py`
- [ ] Achieve 85%+ coverage

**ScaffoldingOrchestrator:**
- [ ] Create `src/orchestrators/scaffolding/`
- [ ] Consolidate modules:
  - [ ] `scaffolding_orchestrator.py`
  - [ ] `architecture_intelligence.py`
  - [ ] `code_analyzer.py`
  - [ ] `migration_strategist.py`
  - [ ] `orchestrator_chain.py`
- [ ] Create test suite
- [ ] Achieve 80%+ coverage

#### Week 9: Domain-Specific

**ADOOrchestrator:**
- [ ] Create `src/orchestrators/ado/`
- [ ] Consolidate:
  - [ ] `ado_orchestrator.py` (main)
  - [ ] `work_item_generator.py` (story/feature/task)
  - [ ] `completion_summary_generator.py`
- [ ] Migrate ADO agent logic
- [ ] Create test suite
- [ ] Achieve 80%+ coverage

**DocumentationOrchestrator:**
- [ ] Create `src/orchestrators/documentation/`
- [ ] Merge 2 implementations
- [ ] Create test suite
- [ ] Achieve 75%+ coverage

#### Week 10: Operations

**MaintenanceOrchestrator:**
- [ ] Create `src/orchestrators/maintenance/`
- [ ] Consolidate 5 orchestrators:
  - [ ] `maintenance_orchestrator.py` (main)
  - [ ] `cleanup_engine.py`
  - [ ] `optimization_engine.py`
- [ ] Create comprehensive test suite
- [ ] Achieve 80%+ coverage

**QAOrchestrator:**
- [ ] Create `src/orchestrators/qa/`
- [ ] Add code quality + review logic
- [ ] Create test suite
- [ ] Achieve 75%+ coverage

**DevOpsOrchestrator:**
- [ ] Create `src/orchestrators/devops/`
- [ ] Add deployment + integration testing
- [ ] Create test suite
- [ ] Achieve 75%+ coverage

#### Week 11: Supporting

**ObservabilityOrchestrator:**
- [ ] Create `src/orchestrators/observability/`
- [ ] Add performance profiling + resource management
- [ ] Create test suite
- [ ] Achieve 70%+ coverage

**IntelligenceOrchestrator:**
- [ ] Migrate from orchestration_3_0
- [ ] Create test suite
- [ ] Achieve 70%+ coverage

**OnboardingOrchestrator:**
- [ ] Create `src/orchestrators/onboarding/`
- [ ] Consolidate onboarding + demo
- [ ] Create test suite
- [ ] Achieve 75%+ coverage

### Phase 4: Operations Simplification (Weeks 12-14)

#### Auto-Discovery System
- [ ] Implement `@orchestrator` decorator
  - [ ] Metadata: name, category, description
  - [ ] Auto-registration in DI container
  - [ ] Validation (duplicate names)
- [ ] Implement orchestrator scanner
  - [ ] Scan `src/orchestrators/`
  - [ ] Load all `@orchestrator` classes
  - [ ] Build operation registry
- [ ] Update DI container
  - [ ] Auto-wire discovered orchestrators
  - [ ] Inject dependencies
  - [ ] Lifecycle management

#### Manifest Reduction
- [ ] Create new `cortex-operations.yaml` (500 lines)
  - [ ] Operation descriptions
  - [ ] User-facing examples
  - [ ] Natural language aliases
  - [ ] DoR/DoD definitions (metadata only)
- [ ] Remove wiring config (now in DI container)
- [ ] Remove module lists (auto-discovered)
- [ ] Remove profiles (handled by orchestrator config)

#### Routing Update
- [ ] Update `OperationsOrchestrator`
  - [ ] Use DI container for orchestrator lookup
  - [ ] Natural language → orchestrator name mapping
  - [ ] Dynamic routing (no hardcoded if/else)
- [ ] Add operation alias system
  - [ ] "plan" → PlanningOrchestrator
  - [ ] "plan ado" → ADOOrchestrator
  - [ ] "refine" → MaintenanceOrchestrator (refine mode)
- [ ] Backward compatibility
  - [ ] Old operation names still work
  - [ ] Deprecation warnings for legacy paths

#### Tests
- [ ] `test_orchestrator_decorator.py` (8 tests)
- [ ] `test_auto_discovery.py` (10 tests)
- [ ] `test_di_auto_wiring.py` (12 tests)
- [ ] `test_dynamic_routing.py` (10 tests)
- [ ] `test_operation_aliases.py` (8 tests)
- [ ] Integration: `test_operations_e2e.py` (5 tests)

### Phase 5: Testing & Validation (Weeks 15-16)

#### Test Suite Execution
- [ ] Run full test suite: `pytest tests/`
- [ ] Measure coverage: `pytest --cov=src tests/`
- [ ] Generate HTML coverage report
- [ ] Identify coverage gaps
- [ ] Write tests for uncovered code

#### Coverage Targets
- [ ] Core orchestrators: 90%+ coverage
- [ ] Domain orchestrators: 85%+ coverage
- [ ] Supporting orchestrators: 75%+ coverage
- [ ] MCP Gateway: 90%+ coverage
- [ ] DI Container: 95%+ coverage
- [ ] Brain tiers: 80%+ coverage

#### Integration Tests
- [ ] Test critical user workflows:
  1. [ ] Planning → Execution → TDD → Deployment
  2. [ ] ADO Story → Implementation → Testing → Review
  3. [ ] Cleanup → Optimization → Healthcheck
  4. [ ] Onboarding → Demo → First Feature
  5. [ ] Error → Recovery → Retry
  6. [ ] MCP Tool Invocation → Retry → Circuit Breaker
  7. [ ] Cross-repo pattern learning → Recommendation
  8. [ ] Tier 2 namespace isolation → Privacy enforcement
  9. [ ] DI auto-discovery → Orchestrator routing
  10. [ ] Backward compatibility (old operations)

#### Performance Benchmarks
- [ ] Baseline measurements (3.0)
  - [ ] Operation execution time
  - [ ] Memory usage
  - [ ] Brain query performance
  - [ ] Test suite duration
- [ ] Target measurements (4.0)
  - [ ] Same operations (should be <10% slower)
  - [ ] Memory usage (should be similar or better)
  - [ ] Brain query performance (should be same or faster)
  - [ ] Test suite duration (more tests, but optimized)
- [ ] Load testing
  - [ ] 100 concurrent operations
  - [ ] Sustained load (1 hour)
  - [ ] Stress test (until failure)

#### Backward Compatibility
- [ ] Test all 27 operations from 3.0
- [ ] Verify natural language commands work
- [ ] Check response template compatibility
- [ ] Validate brain data migration
- [ ] Test old wrappers via compatibility layer

#### Migration Validation
- [ ] Create validation report
  - [ ] All orchestrators migrated (12/12)
  - [ ] Test coverage (85%+)
  - [ ] Performance benchmarks (pass/fail)
  - [ ] Backward compatibility (verified)
  - [ ] Bloat reduction (6,760 → 500 lines)
- [ ] User acceptance testing
  - [ ] Run on 3 sample repositories
  - [ ] Test all operations
  - [ ] Collect feedback
- [ ] Final go/no-go decision

---

## 📈 Success Metrics

| Metric | Current (3.0) | Target (4.0) | Measurement |
|--------|---------------|--------------|-------------|
| **Orchestrator Count** | 28+ scattered | 12 consolidated | 57% reduction |
| **Manifest Size** | 6,760 lines YAML | 500 lines YAML | 93% reduction |
| **Test Coverage** | ~60% | 85%+ | pytest --cov |
| **Tests Co-located** | 0% | 100% | All orchestrators have tests/ |
| **Tool Integration Time** | 2-4 weeks | <1 day | MCP server config |
| **Cross-Repo Learning** | None | Tier 2 patterns | Namespace isolation working |
| **Storage (3 repos)** | 150-300 MB | 100-200 MB | 33% reduction |
| **Setup Complexity** | Manual config | Auto-discovery | DI container wiring |

**Note:** Phase 0 (Week 0 cleanup) is CRITICAL foundation work. Total timeline: 18 weeks (1 week Phase 0 + 17 weeks Phases 1-6).

---

## ⚠️ Risks & Mitigation

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **Breaking Changes** | HIGH | MEDIUM | Comprehensive backward compatibility layer + 100+ tests |
| **Performance Regression** | MEDIUM | LOW | Benchmarking suite + <10% regression gate |
| **Brain Data Loss** | HIGH | LOW | Backup before migration + rollback capability |
| **Incomplete Coverage** | MEDIUM | MEDIUM | TDD-first approach + 85%+ coverage requirement |
| **DI Complexity** | MEDIUM | MEDIUM | Clear documentation + examples + gradual adoption |
| **MCP Server Downtime** | MEDIUM | MEDIUM | Circuit breaker + fallback + retry logic |
| **Namespace Collision** | LOW | LOW | UUID-based keys + collision detection |
| **Test Suite Duration** | LOW | MEDIUM | Parallel test execution + selective testing |

---

## 🔄 Rollback Strategy

**If Migration Fails at Any Phase:**

1. **Immediate Rollback:**
   ```bash
   git checkout CORTEX-3.0
   git branch -D CORTEX-4.0-migration-failed
   ```

2. **Restore Brain Data:**
   ```bash
   # Restore from backup
   cp ~/.cortex/backup/brain.db.backup cortex-brain/brain.db
   ```

3. **Document Failure:**
   - Log failure reason in `cortex-brain/migration-failures.log`
   - Create incident report
   - Analyze root cause

4. **Communicate:**
   - Notify all users of rollback
   - Explain what happened
   - Provide timeline for retry

**Phase-Specific Rollback:**
- **Phase 1:** MCP compatibility layer allows old code to work
- **Phase 2:** Brain migration is opt-in, no forced changes
- **Phase 3:** Orchestrators migrate one-by-one, old ones still work
- **Phase 4:** Operations YAML reduction doesn't affect functionality
- **Phase 5:** Testing phase, no production impact

---

## 📚 Documentation Updates Required

1. **User-Facing:**
   - [ ] CORTEX 4.0 Migration Guide
   - [ ] MCP Server Developer Guide
   - [ ] Brain Centralization Guide
   - [ ] Operation Reference (updated)
   - [ ] Troubleshooting Guide

2. **Developer-Facing:**
   - [ ] Orchestrator Development Guide
   - [ ] DI Container Usage Guide
   - [ ] Test Writing Guide (co-located tests)
   - [ ] MCP Protocol Specification
   - [ ] Architecture Decision Records (ADRs)

3. **Internal:**
   - [ ] Code Review Checklist (updated for 4.0)
   - [ ] Deployment Runbook (updated)
   - [ ] Incident Response Plan (updated)

---

## ✅ Approval Checklist

Before starting migration, confirm:

- [ ] **User Approval:** User has reviewed and approved this plan
- [ ] **Resource Allocation:** 16 weeks allocated for migration
- [ ] **Backup Strategy:** Brain backup procedures in place
- [ ] **Rollback Plan:** Rollback strategy documented and understood
- [ ] **Testing Strategy:** 85%+ coverage target agreed upon
- [ ] **Risk Acceptance:** All risks reviewed and accepted
- [ ] **Documentation:** Commitment to update all documentation
- [ ] **Team Training:** Team trained on DI container, MCP architecture

---

## 🎯 Next Steps

**Immediate Actions:**

1. **Review & Approve:** User reviews this plan and provides approval
2. **Create Branch:** `git checkout -b CORTEX-4.0` from `CORTEX-3.0`
3. **Set Milestones:** Create GitHub milestones for each phase
4. **Backup Brain:** Run `python scripts/backup_brain.py --all-repos`
5. **Start Phase 1:** Begin MCP Gateway + DI Container implementation

**Weekly Cadence:**

- **Monday:** Plan week's work from checklist
- **Daily:** Implement + write tests (TDD)
- **Friday:** Review progress, update checklist, commit work
- **Week End:** Phase retrospective (if phase complete)

**Communication:**

- Weekly progress reports to user
- Blocker escalation within 24 hours
- Risk assessment updates as needed

---

## 📞 Questions for User

Before proceeding, please answer:

1. **Timeline:** Is 18 weeks (1 week Phase 0 cleanup + 17 weeks Phases 1-6 migration) acceptable?
2. **Phase 0 Approval:** Approve bloat cleanup before migration starts?
3. **File Organization:** Approve strict root-level file restrictions (0 files at root)?
4. **Testing:** Agree with 85%+ coverage target?
5. **Brain Centralization:** Approve hybrid model (shared Tier 2, isolated Tier 1/3)?
6. **MCP Priority:** Prioritize specific MCP servers beyond Dev Tools (e.g., ADO)?
7. **Bloat Reduction:** Approve DI container over manifest?
8. **Backward Compatibility:** Must ALL old operations work?
9. **Rollback Trigger:** >10% perf regression = rollback?
10. **Documentation:** Who reviews updated docs?

---

**END OF MIGRATION PLAN**

---

## Appendices

### Appendix A: Detailed Orchestrator Inventory

*(See full orchestrator list in "CORTEX 3.0 Feature Discovery" section)*

### Appendix B: Orchestrator Redesign Documents

- **TDD Orchestrator:** [TDD-ORCHESTRATOR-REDESIGN.md](./TDD-ORCHESTRATOR-REDESIGN.md) - Complete architectural redesign with strategy pattern, AI-driven code generation/refactoring, and unified orchestration
- **Planning Orchestrator:** See chat01.md for architectural analysis and CORTEX 4.0 redesign

### Appendix C: MCP Server Specifications

*(See "06-mcp-server-architecture.md" for detailed MCP design)*

### Appendix D: Brain Architecture Details

*(See "17-brain-architecture-storage-options.md" for storage options)*

### Appendix E: Test Coverage Requirements

| Component | Minimum Coverage | Rationale |
|-----------|-----------------|-----------|
| Core Orchestrators | 90% | Critical path, high usage |
| Domain Orchestrators | 85% | Important features |
| Supporting Orchestrators | 75% | Lower risk |
| MCP Gateway | 90% | Infrastructure |
| DI Container | 95% | Foundation |
| Brain Tiers | 80% | Data integrity |
| Agents | 75% | Higher-level logic |
| Utilities | 70% | Helper functions |

---

**Author:** Asif Hussain  
**Contact:** github.com/asifhussain60/CORTEX  
**Date:** December 17, 2025  
**Version:** 1.0  
