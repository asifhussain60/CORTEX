# CORTEX Architecture — Refactored Structure
## Phase 08: Registry & Docs Alignment

**Version:** 2.0 | **Updated:** 2026-02-20 | **Authority:** Phase 08

---

## Directory Structure

### Top-Level Directories (16 Canonical)

| Directory | Purpose | Ownership |
|-----------|---------|-----------|
| `cortex/` | Production source code (all domains) | Core Architecture |
| `cortex-registry/` | Configuration, governance, metadata YAML | Governance Orchestrator |
| `cortex-docs/` | User-facing documentation | Documentation Orchestrator |
| `tests/` | Test suite (mirrors cortex structure) | Testing Orchestrator |
| `.github/` | CI/CD, automation, copilot instructions | DevOps |
| `deployment/` | Deployment configs, manifests, health checks | Infrastructure Orchestrator |
| `scripts/` | Utility scripts for analysis & automation | Maintenance |
| `_archive/` | Deprecated components (phases 1-7) | Archive Manager |

### cortex/ (16 Canonical Subdirectories)

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **core/** | Core orchestration, lifecycle, audit | orchestrator_base.py, workflow_engine.py, audit_db.py |
| **orchestrators/** | 44+ active orchestrators (canonical implementations) | domain/, support/, master_orchestrators/ |
| **mcp/** | Model Context Protocol tools (22 tools) | tools/, interfaces/ |
| **intelligence/** | LENS analysis, domain brain, memory | lens/, domain_brain/, memory/ |
| **governance/** | Rules, enforcement, compliance gates | rules/, enforcement/, validation/ |
| **infrastructure/** | Infrastructure detection, catalog management | infrastructure_detector.py, topology_manager.py |
| **observability/** | Tracing, metrics, logging | opentelemetry/, prometheus/, dashboards/ |
| **models/** | Data models, schemas, pydantic validators | orchestrator_models.py, registry_models.py |
| **templates/** | YAML templates, workflow specs | orchestrator_templates/, workflow_specs/ |
| **testing/** | Testing frameworks, TDD support | tdd_orchestrator.py, test_framework.py |
| **api/** | REST API endpoints (if applicable) | fastapi_routes.py, health_checks.py |
| **cli/** | Command-line interface | commands/, main.py |
| **config/** | Configuration management | env_config.py, settings.py |
| **dashboards/** | Dashboard generation | dashboard_generator.py, templates/ |
| **tools/** | Utility tools, helpers | file_tools.py, validators.py |
| **lens/** | Workspace analysis (legacy, moved to intelligence/) | — |

---

## Orchestrator Catalog

### Phase 05 Active Orchestrators (44 Total)

**Canonical Locations:** `cortex/orchestrators/`

#### Core Orchestrators (6)
- **MasterOrchestrator** — Entry point, request classification, challenge gates
- **CortexMasterPlanOrchestrator** — Phase execution coordination
- **MasterPlanExecution** — 11-phase workflow execution loop
- **PhaseExecutor** — RED→GREEN→REFACTOR→CLEANUP lifecycle
- **EnforcementOrchestrator** — Governance rule validation
- **AuditCoordinator** — Registry & compliance audits

#### Domain Orchestrators (28)
- **SecurityDomainOrchestrator** — Security scanning, compliance
- **DataPipelineOrchestrator** — Data integration orchestration
- **MLOpsOrchestrator** — ML model lifecycle management
- **DevOpsOrchestrator** — Infrastructure automation
- **APIGatewayOrchestrator** — API lifecycle management
- *(+ 23 more domain-specific orchestrators)*

#### Support Orchestrators (8)
- **TDDOrchestrator** — Test-driven development coordination
- **RefactoringOrchestrator** — Code refactoring automation
- **DocumentationOrchestrator** — Documentation generation
- **MetricsOrchestrator** — Metrics collection & reporting
- **HealthCheckOrchestrator** — System health validation
- **RollbackOrchestrator** — Change rollback management
- **CiCdOrchestrator** — CI/CD pipeline orchestration (NEW in Phase 08)
- **DesignOrchestrator** — Architecture design coordination (NEW in Phase 08)

---

## MCP Tools Reference (22 Tools)

### Core Tools (5)
| Tool | Purpose | Parameters |
|------|---------|-----------|
| `cortex_process_request` | Entry point for all requests | request_type, context, data |
| `cortex_validate_compliance` | CORE rules validation | code_path, rule_set |
| `cortex_challenge` | Generate challenge gates | request, alternatives |
| `cortex_onboard_repository` | Repository onboarding (LENS analysis) | repo_path, language |
| `cortex_metrics_report` | Governance metrics export | format, filters |

### Intelligence Tools (4)
| Tool | Purpose | Parameters |
|------|---------|-----------|
| `cortex_lens` | Workspace analysis (semantic search, imports) | query, scope, depth |
| `cortex_query` | Knowledge base queries | question, context |
| `cortex_knowledge` | Knowledge management | operation, entity_type |
| `cortex_refactor` | Semantic code refactoring | language, operation, target |

### Governance Tools (3)
| Tool | Purpose | Parameters |
|------|---------|-----------|
| `cortex_execute_governance` | Enforcement actions | rule_id, entity, action |
| `cortex_load_core_rules` | Load CORE rules registry | — |
| `cortex_audit_remediation_plan` | Auto-plan from audit results | audit_results |

### Infrastructure Tools (2 + 1 NEW)
| Tool | Purpose | Parameters |
|------|---------|-----------|
| `cortex_onboard_infrastructure` | Register infrastructure entities | entity_type, name, data, link_to_repo |
| `cortex_dashboard_full_cycle` | Dashboard lifecycle management | operation, config |
| `cortex_check_dependency_drift` | Dependency analysis | — |

### Dashboard & Reporting Tools (3)
| Tool | Purpose | Parameters |
|------|---------|-----------|
| `cortex_generate_repo_dashboard` | Single repository dashboard | repo_path, metrics |
| `cortex_generate_dashboard_suite` | Multi-repo dashboards (GPT spec) | repos, template |
| `cortex_generate_landing_page` | Dashboard suite landing page | dashboard_config |

### Utility Tools (4)
| Tool | Purpose | Parameters |
|------|---------|-----------|
| `cortex_load_modes` | HEPTA-MODE definitions | — |
| `cortex_load_response_format` | Response format standards | — |
| `cortex_total_recall` | Feature discovery (semantic) | feature_query |
| `cortex_vacuum` | Markdown cleanup & archival | scope, filters |

---

## Governance Rules (11 Core Rules + 8 New)

**Registry Location:** `cortex-registry/core/`

### CORE Rules (Tier 0 - Immutable)
| Rule | Title | Authority | Impact |
|------|-------|-----------|--------|
| CORE-002 | No markdown generation via bash | Requirement | Blocks commits |
| CORE-008 | Test-first development (TDD) | Requirement | Blocks commits |
| CORE-011 | Type hints on all functions | Code quality | Enforcement check |
| CORE-012 | Docstrings on all public APIs | Documentation | Enforcement check |
| CORE-027 | Audit integration | Compliance | Enforcement check |
| CORE-028 | File naming (snake_case) | Code quality | Enforcement check |
| CORE-035 | Single canonical implementation | Architecture | Blocks commits |
| CORE-048 | Holistic validation gate | Process | Blocks execution |
| CORE-049 | Silent autonomous execution | Process | Default behavior |
| CORE-050 | Intent-based MCP blocking | Security | Blocks unsafe intents |
| CORE-051 | Cross-platform audit | Compliance | Validation check |

### New Phase 08 Rules (Tier 1)
| Rule | Title | Authority | Purpose |
|------|-------|-----------|---------|
| CORE-058 | SQLite WAL mode | Infrastructure | Data integrity |
| CORE-059 | MCP footprint limit | Performance | <200ms p95 latency |
| CORE-060 | SDLC brain wiring | Process | Domain orchestration |
| CORE-061 | CCL integration | Governance | Crystal integration |
| CORE-062 | Plan-first execution | Process | Design before build |
| CORE-063 | Challenge-first gates | Process | Alternatives before action |

---

## Registry Structure

**Location:** `cortex-registry/`

```
cortex-registry/
├── core/                          # Governance rules (CORE-xxx)
├── governance/                    # Enforcement policies
├── knowledge-base/                # Industry profiles, security knowledge
│   ├── governance/                # 5 governance rule profiles
│   ├── profiles/                  # 6 industry profiles
│   └── security/                  # Security knowledge
├── company/
│   └── infrastructure/            # Infrastructure catalog (NEW Phase 08)
│       ├── _schema.yaml           # Platform/API/Application schema
│       ├── platforms/             # Platform manifests
│       ├── apis/                  # API definitions
│       ├── applications/          # Application manifests
│       └── topology.yaml          # Dependency graph
├── patterns/                      # 9 enterprise patterns
├── planning/
│   └── phases/                    # Phase specs & status
├── workflows/
│   └── templates/                 # YAML workflow templates
└── cortex-master.yaml             # Master plan index
```

---

## Infrastructure Catalog (NEW)

**Authority:** Phase 08  
**Schema:** `cortex-registry/company/infrastructure/_schema.yaml`

### Supported Entities

#### Platform
- Name, type (kubernetes, docker, ec2, lambda, etc.)
- Provider (aws, gcp, azure, on-prem)
- Networking, observability, SLA
- Hosted applications (references)

#### API
- Name, type (rest, graphql, grpc)
- Version, base URL, endpoints
- Owner repository, consumers
- Authentication, SLA
- Rate limits, deprecation status

#### Application
- Name, type (backend-service, frontend-app, worker, etc.)
- Repository, platform (reference)
- Tech stack, dependencies
- APIs consumed/exposed
- Owner team, deployment method

### Auto-Generation
- **Topology.yaml** — Regenerated after each onboarding
- **Dependency Graph** — Built from application/API relationships
- **Detection** — InfrastructureDetector infers platforms from repo contents

---

## Workflow Templates

**Location:** `cortex-registry/workflows/templates/`

### Required Lifecycle
All templates must include:
- **Setup** — Pre-execution preparation
- **Execute** — Main orchestration step
- **Teardown** — Cleanup & audit logging

### Template Categories
| Category | Purpose | Count |
|----------|---------|-------|
| **lifecycle/** | CORTEX phase execution | 3 templates |
| **governance/** | Compliance & enforcement | 2 templates |
| **quality/** | Testing & validation | 2 templates |
| **security/** | Security scanning | 2 templates |
| **maintenance/** | System maintenance | 2 templates |
| **tdd/** | Test-driven development | 1 template |

---

## Testing Structure

**Location:** `tests/`

Mirrors `cortex/` structure with 27 canonical directories:

```
tests/
├── unit/
│   ├── core/
│   ├── orchestrators/
│   ├── mcp/
│   ├── intelligence/
│   ├── governance/
│   └── ...
├── integration/
├── golden/                        # Golden test suite (428+ tests)
└── phases/
    └── refactor/                  # Phase RED specs
```

---

## Key Architecture Changes (Phase 08)

### ✅ COMPLETED
1. **Registry Audit** — All workflow templates validated
2. **Stale YAML Removal** — Cleaned references to archived dirs
3. **Documentation Updates** — Architecture docs reflect new structure
4. **Infrastructure Catalog** — Schema + detection + topology
5. **MCP Tool Addition** — `cortex_onboard_infrastructure`
6. **New Orchestrators** — CiCdOrchestrator, DesignOrchestrator

### 🔵 IN PROGRESS
7. Documentation gap analysis
8. Diagram generation (package structure, orchestrator hierarchy, MCP mapping)

### ➡️ NEXT PHASES
- Phase 09: Final Verification & Archive Deletion
- Phase 10: Production Readiness & Go-Live

---

## Migration Guide

### For Users
1. **Old Imports** → **New Imports**
   ```python
   # OLD (archived)
   from cortex_intelligence.memory import MemoryOrchestrator
   
   # NEW (canonical)
   from cortex.intelligence.memory import MemoryOrchestrator
   ```

2. **Old Orchestrators** → **Active Orchestrators**
   - 120 → 44 active orchestrators
   - All documented in `cortex-docs/architecture/orchestrator-catalog.md`

3. **Infrastructure Onboarding**
   ```python
   from cortex.mcp.tools import cortex_onboard_infrastructure
   
   cortex_onboard_infrastructure(
       entity_type="api",
       name="my-api",
       data={"type": "rest", "version": "1.0"},
   )
   ```

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Top-level dirs | 16 canonical | ✅ Complete |
| Orchestrators | 44 active | ✅ Complete (Phase 05) |
| MCP tools | 22 (consolidated) | ✅ 21 active + 1 NEW |
| Test coverage | ≥95% | ✅ 1,035 tests passing |
| Golden tests | 428+ passing | ✅ Maintained |
| Registry references | 100% resolve | 🔄 In progress (Phase 08) |
| Documentation | 95%+ coverage | 🔄 In progress (Phase 08) |

---

**Next:** See [Orchestrator Catalog](orchestrator-catalog.md) for complete list of 44 active orchestrators.
