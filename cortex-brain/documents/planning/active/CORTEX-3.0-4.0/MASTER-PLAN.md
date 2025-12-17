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
- **Unified Operations** - Consolidate overlapping functionality

**Timeline:** 17 weeks (4 months + 1 week pre-cleanup)  
**Risk Level:** 🟡 MEDIUM  
**Test Coverage Target:** 85%+ all orchestrators  
**Phase 0 (Week 0):** Pre-Migration Cleanup - Eliminate bloat  

---

## 🔍 CORTEX 3.0 Feature Discovery

### Core Orchestrators (10)

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
└── onboarding/
    └── onboarding_orchestrator.py        # Developer onboarding automation
```

**Legacy Orchestrators (Refactor Candidates):**
```
src/operations/modules/
├── cleanup/
│   ├── cleanup_orchestrator.py           # Workspace cleanup
│   ├── holistic_cleanup_orchestrator.py  # Deep cleanup with AST
│   └── user_cleanup_orchestrator.py      # User-initiated cleanup
├── optimization/
│   └── optimize_cortex_orchestrator.py   # System optimization
├── system/
│   └── optimize_system_orchestrator.py   # Legacy system optimization
├── utilities/
│   ├── code_quality_orchestrator.py      # Code quality checks
│   ├── deployment_orchestrator.py        # Deployment automation
│   ├── documentation_generation_orchestrator.py  # Doc generation
│   ├── error_recovery_orchestrator.py    # Error handling
│   ├── holistic_review_orchestrator.py   # Code review automation
│   ├── integration_testing_orchestrator.py  # Integration tests
│   ├── performance_profiling_orchestrator.py  # Performance analysis
│   └── resource_management_orchestrator.py  # Resource tracking
├── brain/
│   └── brain_tuning_orchestrator.py      # Brain optimization
├── demo/
│   └── demo_orchestrator.py              # Interactive demos
└── architectural/
    └── review_orchestrator.py            # Architecture review
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

### Agents (8)

```
src/cortex_agents/
├── intent_router.py                      # Route user intent to appropriate agent
├── planning_agent.py                     # Feature planning workflows
├── ado_agent.py                          # Azure DevOps integration
├── story_intelligence_agent.py           # Story analysis and enhancement
├── cross_repository_learning_agent.py    # Multi-repo pattern learning
├── orchestrator_agent.py                 # Orchestrator management
└── brain_ingestion_agent_impl.py         # Brain tier 2/3 ingestion
```

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

**Deliverables:**
- ✅ 67 root files → 8 essential files (88% reduction)
- ✅ All CORTEX 4.0 docs in single location
- ✅ Clear directory structure
- ✅ Documented file organization rules (below)

**Total Time:** 8 hours (1 day)

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

### Phase 1: Foundation (Weeks 1-3) - MCP Gateway + DI Container

**Goal:** Establish core infrastructure without breaking existing functionality

**Deliverables:**
1. MCP Gateway implementation
2. Dependency Injection container
3. Dev Tools MCP Server (Git, Docker, pytest)
4. Backward compatibility layer (old wrappers → MCP)

**Tasks:**
- [ ] Design MCP protocol schemas (JSON-RPC 2.0)
- [ ] Implement `MCPGateway` with routing + auth
- [ ] Create `dev_tools_server.py` (Git, Docker, pytest)
- [ ] Build `CortexContainer` with DI wiring
- [ ] Create compatibility shim: `old_git_wrapper()` → `mcp_gateway.invoke("git", ...)`
- [ ] Write 40 tests for MCP gateway, circuit breaker, auth
- [ ] Document MCP server development guide

**Migration Approach:** **Non-breaking** - Old code continues working via compatibility layer

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

### Phase 3: Orchestrator Consolidation (Weeks 7-11) - Clean Structure + TDD

**Goal:** Migrate orchestrators to clean structure with co-located tests

**Migration Order (Dependency-First):**

#### Week 7: Core Orchestrators
1. **ExecutionOrchestrator** (Foundation - all others depend on it)
   - Migrate to `src/orchestrators/execution/`
   - Add co-located tests
   - 85%+ coverage
   
2. **TDDOrchestrator** (Critical path - used by all feature work)
   - Consolidate 5 files: orchestrator, test_generator, implementation_engine, refactoring_engine, phase_validator
   - Migrate to `src/orchestrators/tdd/`
   - Add comprehensive test suite
   - 90%+ coverage (TDD for TDD!)

#### Week 8: Planning System
3. **PlanningOrchestrator** (High complexity, well-tested)
   - Already 1,599 LOC - refactor into 4 modules
   - Migrate to `src/orchestrators/planning/`
   - Split: orchestrator (800), complexity_analyzer (300), dor_validator (200), plan_generator (400)
   - Migrate 4 existing test files
   - 85%+ coverage

4. **ScaffoldingOrchestrator** (Complex, 5 support modules)
   - Consolidate architecture_intelligence, code_analyzer, migration_strategist, orchestrator_chain
   - Migrate to `src/orchestrators/scaffolding/`
   - 80%+ coverage

#### Week 9: Domain-Specific Orchestrators
5. **ADOOrchestrator** (Consolidate all ADO operations)
   - Combine: ado_agent, ado work item operations, ado_planning
   - Migrate to `src/orchestrators/ado/`
   - 80%+ coverage

6. **DocumentationOrchestrator** (Consolidate 2 implementations)
   - Merge: documentation_orchestrator + documentation_generation_orchestrator
   - Migrate to `src/orchestrators/documentation/`
   - 75%+ coverage

#### Week 10: Operations Orchestrators
7. **MaintenanceOrchestrator** (Consolidate cleanup + optimization)
   - Merge: cleanup_orchestrator, holistic_cleanup, user_cleanup, optimize_cortex, optimize_system
   - Migrate to `src/orchestrators/maintenance/`
   - Split: orchestrator, cleanup_engine, optimization_engine
   - 80%+ coverage

8. **QAOrchestrator** (Quality automation)
   - Already in orchestration_3_0, migrate to new structure
   - Add code_quality_orchestrator, holistic_review_orchestrator
   - 75%+ coverage

9. **DevOpsOrchestrator** (CI/CD automation)
   - Add deployment_orchestrator, integration_testing_orchestrator
   - 75%+ coverage

#### Week 11: Supporting Orchestrators
10. **ObservabilityOrchestrator** (Monitoring + health)
    - Add performance_profiling_orchestrator, resource_management_orchestrator
    - 70%+ coverage

11. **IntelligenceOrchestrator** (Pattern learning)
    - Already in orchestration_3_0
    - 70%+ coverage

12. **OnboardingOrchestrator** (Developer experience)
    - Consolidate onboarding_orchestrator + demo_orchestrator
    - 75%+ coverage

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

**Note:** Phase 0 (Pre-Migration Cleanup) adds 1 week to timeline but is CRITICAL to prevent carrying forward 67 files of bloat into CORTEX 4.0.

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

1. **Timeline:** Is 17 weeks (1 week cleanup + 16 weeks migration) acceptable?
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

### Appendix B: MCP Server Specifications

*(See "06-mcp-server-architecture.md" for detailed MCP design)*

### Appendix C: Brain Architecture Details

*(See "17-brain-architecture-storage-options.md" for storage options)*

### Appendix D: Test Coverage Requirements

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
