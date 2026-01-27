# CORTEX Clean Directory Structure
## New Branch Layout

**Document:** docker-structure-reference.md  
**Date:** 2026-01-27  

---

## Directory Tree

```
CORTEX-clean/
│
├── .github/
│   ├── copilot-instructions.md          # Updated for Docker
│   └── prompts/
│       └── CORTEX.prompt.md             # Updated for Docker
│
├── cortex/                              # Main source
│   ├── __init__.py                      # NEW: Single entry point
│   │
│   ├── common/                          # Shared utilities
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── validators.py
│   │   ├── file_utils.py
│   │   ├── health_check.py
│   │   └── connection_utils.py
│   │
│   ├── models/                          # Data models
│   │   ├── __init__.py
│   │   ├── canonical_enums.py           # SSOT for enums
│   │   └── dashboard_models.py
│   │
│   ├── config/                          # Configuration
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── core/                            # Core functionality
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   ├── mode_controller.py
│   │   ├── dependency_validator.py
│   │   ├── feature_registry.py
│   │   ├── response_header_config.py
│   │   ├── provenance_tracker.py
│   │   │
│   │   ├── intelligence/                # Intelligence modules
│   │   │   ├── __init__.py
│   │   │   ├── ast_intelligence.py
│   │   │   ├── dependency_mapper.py
│   │   │   ├── pattern_detector.py
│   │   │   ├── call_graph.py
│   │   │   └── routing_intelligence.py
│   │   │
│   │   ├── hallucination_prevention/    # Hallucination prevention
│   │   │   ├── __init__.py
│   │   │   ├── hallucination_detection.py
│   │   │   ├── output_validator.py
│   │   │   └── confidence_scoring.py
│   │   │
│   │   ├── security/                    # Security
│   │   │   ├── __init__.py
│   │   │   └── isolation.py
│   │   │
│   │   ├── decorators/                  # Decorators
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator_decorator.py
│   │   │   └── governance_decorator.py
│   │   │
│   │   └── config/                      # Core config
│   │       ├── __init__.py
│   │       └── timeout_profiles.py
│   │
│   ├── infrastructure/                  # Enterprise infrastructure
│   │   ├── __init__.py
│   │   │
│   │   ├── logging/                     # Logging subsystem
│   │   │   ├── __init__.py
│   │   │   ├── enhanced_audit_logger.py
│   │   │   ├── audit_logger.py
│   │   │   ├── audit_hash_chain.py
│   │   │   ├── structured_logger.py
│   │   │   └── tiered_logger.py
│   │   │
│   │   ├── resilience/                  # Resilience patterns
│   │   │   ├── __init__.py
│   │   │   ├── circuit_breaker.py
│   │   │   ├── retry_strategy.py
│   │   │   ├── bulkhead_manager.py
│   │   │   └── graceful_degradation.py
│   │   │
│   │   ├── observability/               # Observability
│   │   │   ├── __init__.py
│   │   │   ├── prometheus_metrics.py
│   │   │   ├── alert_manager.py
│   │   │   ├── telemetry_provider.py
│   │   │   └── tracing.py
│   │   │
│   │   ├── security/                    # Security infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── security_auditor.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── cors_handler.py
│   │   │   ├── secrets_filter.py
│   │   │   ├── input_validator.py
│   │   │   └── crypto_provider.py
│   │   │
│   │   ├── compliance/                  # Compliance
│   │   │   ├── __init__.py
│   │   │   ├── evidence_bundle.py
│   │   │   └── compliance_marker.py
│   │   │
│   │   └── monitoring/                  # Monitoring
│   │       ├── __init__.py
│   │       ├── threshold_monitor.py
│   │       ├── progress_tracker.py
│   │       └── resource_tracker.py
│   │
│   ├── orchestrators/                   # All orchestrators
│   │   ├── __init__.py                  # Clean exports only
│   │   ├── base.py                      # IOrchestrator
│   │   │
│   │   ├── core/                        # 6 Core orchestrators
│   │   │   ├── __init__.py
│   │   │   ├── master_orchestrator.py
│   │   │   ├── interaction_orchestrator.py
│   │   │   ├── intent_router.py
│   │   │   ├── tdd_orchestrator.py
│   │   │   ├── workflow_orchestrator.py
│   │   │   ├── lens_synthesis.py
│   │   │   ├── challenge_engine.py
│   │   │   ├── fuzzy_intent_matcher.py
│   │   │   ├── comprehension_session.py
│   │   │   ├── governance_registry.py
│   │   │   └── knowledge_graph.py
│   │   │
│   │   ├── domain/                      # 6 Domain orchestrators
│   │   │   ├── __init__.py
│   │   │   ├── refactoring_orchestrator.py
│   │   │   ├── planning_orchestrator.py
│   │   │   ├── documentation_orchestrator.py
│   │   │   ├── phase_executor.py
│   │   │   └── autonomous_execution_engine.py
│   │   │
│   │   └── support/                     # 11 Support orchestrators
│   │       ├── __init__.py
│   │       ├── onboarding_orchestrator.py
│   │       ├── tool_discovery_orchestrator.py
│   │       ├── upgrade_orchestrator.py
│   │       ├── rollback_orchestrator.py
│   │       └── ... (remaining support)
│   │
│   ├── wiring/                          # NEW: Git-backed wiring
│   │   ├── __init__.py
│   │   │
│   │   ├── specifications/              # YAML-based SSOT
│   │   │   ├── core-wiring.yaml
│   │   │   ├── domain-wiring.yaml
│   │   │   └── support-wiring.yaml
│   │   │
│   │   ├── registry/                    # Runtime registry
│   │   │   ├── __init__.py
│   │   │   ├── git_backed_registry.py
│   │   │   ├── lazy_orchestrator.py
│   │   │   └── wiring_validator.py
│   │   │
│   │   └── bootstrap.py                 # Single entry point
│   │
│   ├── intent_router/                   # Intent routing
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   ├── confidence_scorer.py
│   │   ├── context_manager.py
│   │   ├── disambiguator.py
│   │   ├── edge_case_handler.py
│   │   ├── fallback_strategy.py
│   │   ├── routing_engine.py
│   │   └── observability.py
│   │
│   ├── mcp/                             # MCP Server
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── server.py                    # NEW: Enhanced server
│   │   ├── cortex_tools.py
│   │   ├── mcp_tools_catalog.py
│   │   ├── endpoints.py
│   │   ├── executor.py
│   │   ├── error_handler.py
│   │   ├── input_validator.py
│   │   ├── health.py                    # NEW: Health endpoints
│   │   │
│   │   ├── adapters/                    # 23 MCP adapters
│   │   │   ├── __init__.py
│   │   │   └── ... (all adapters)
│   │   │
│   │   └── config/                      # MCP config
│   │       └── __init__.py
│   │
│   ├── brain/                           # Brain module
│   │   ├── __init__.py
│   │   │
│   │   ├── core/                        # Core brain
│   │   │   ├── __init__.py
│   │   │   ├── state_manager.py
│   │   │   ├── distributed_lock.py
│   │   │   ├── interfaces.py
│   │   │   └── orchestrator_base.py
│   │   │
│   │   ├── domain_brain/                # Domain brain
│   │   │   ├── __init__.py
│   │   │   ├── intent_classifier.py
│   │   │   ├── intent_parser.py
│   │   │   └── nlp_handler_router.py
│   │   │
│   │   └── ide/                         # IDE integration
│   │       ├── __init__.py
│   │       └── vscode_integration.py
│   │
│   ├── domain_brain/                    # Domain knowledge
│   │   ├── __init__.py
│   │   ├── business_knowledge_repository.py
│   │   ├── validator.py
│   │   ├── models.py
│   │   ├── api.py
│   │   ├── audit_logger.py
│   │   └── adapters.py
│   │
│   ├── governance/                      # Governance
│   │   ├── __init__.py
│   │   ├── policy_enforcer.py
│   │   ├── governance_analyzer.py
│   │   └── compliance_reporter.py
│   │
│   ├── knowledge/                       # Knowledge protocol
│   │   ├── __init__.py
│   │   └── protocol/
│   │       └── ... (protocol files)
│   │
│   ├── tools/                           # Essential tools
│   │   ├── __init__.py
│   │   ├── total_recall_agent.py
│   │   ├── git_history_analyzer.py
│   │   ├── duplicate_detector.py
│   │   ├── testing_framework.py
│   │   └── toolkit/
│   │
│   └── cli/                             # CLI
│       ├── __init__.py
│       ├── health_check.py
│       └── commands/
│
├── cortex_brain/                        # Governance layer
│   ├── __init__.py
│   │
│   ├── tier0/                           # Immutable governance
│   │   ├── __init__.py
│   │   ├── governance/
│   │   │   └── core-rules.yaml          # CORE-001 to CORE-040
│   │   └── path_abstraction.py
│   │
│   ├── tier1/                           # Acceptance criteria
│   │   ├── __init__.py
│   │   └── governance/
│   │       └── confirmation_gate_rules.py
│   │
│   ├── tier3/                           # Knowledge
│   │   ├── __init__.py
│   │   └── knowledge/
│   │       ├── synthesis_engine.py
│   │       ├── ARCHITECTURE/            # 10+ YAML files
│   │       ├── SECURITY/                # 3+ YAML files
│   │       └── ... (all knowledge YAMLs)
│   │
│   └── domain/                          # Domain models
│       ├── domain_models.py
│       └── domain_factory.py
│
├── deployment/                          # Docker deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── .dockerignore
│   │
│   └── k8s/                             # Kubernetes (future)
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
│
├── tests/                               # Essential tests only
│   ├── __init__.py
│   ├── conftest.py                      # Simplified
│   ├── pytest.ini
│   │
│   ├── unit/                            # Unit tests
│   │   ├── __init__.py
│   │   ├── orchestrators/               # ~50 tests
│   │   ├── infrastructure/              # ~30 tests
│   │   ├── intent_router/               # ~20 tests
│   │   └── wiring/                      # NEW: Wiring tests
│   │
│   ├── integration/                     # Integration tests
│   │   ├── __init__.py
│   │   ├── test_mcp_server.py
│   │   ├── test_orchestrator_wiring.py  # NEW
│   │   └── test_docker_deployment.py    # NEW
│   │
│   ├── wiring/                          # NEW: Extensive wiring tests
│   │   ├── __init__.py
│   │   ├── test_single_path_enforcement.py
│   │   ├── test_multi_user_scenarios.py
│   │   ├── test_git_backed_registry.py
│   │   ├── test_lazy_orchestrator.py
│   │   ├── test_wiring_determinism.py
│   │   ├── test_no_database_files.py
│   │   └── test_concurrent_wiring.py
│   │
│   └── fixtures/                        # Test fixtures
│       └── ...
│
├── docs/                                # Minimal documentation
│   ├── 00-README.md
│   ├── 01-getting-started/
│   │   └── installation.md              # Docker setup
│   └── 02-architecture/
│       └── overview.md
│
├── _workspaces/                         # Keep only roadmap
│   └── roadmap/
│       ├── cortex-impl-map.yaml
│       └── phases/
│
├── .gitignore                           # Updated
├── requirements.txt                     # Simplified
├── pyproject.toml
├── pytest.ini
├── Dockerfile                           # Root Dockerfile
├── docker-compose.yml                   # Root compose
└── README.md                            # NEW: Docker-first README
```

---

## Key Differences from Current Branch

| Aspect | Current | New Clean |
|--------|---------|-----------|
| **cortex/orchestrators/core/** | 30+ files | 12 files (essential only) |
| **Wiring system** | 7 directories | 1 directory (cortex/wiring/) |
| **Database files** | .cortex/, cortex_brain/state/ | None |
| **Infrastructure** | Flat structure | Organized by function |
| **Tests** | 500 files mixed | 150 files organized |
| **Documentation** | 750+ files | 5 essential files |
| **Root files** | 15+ | 6 essential |

---

## Entry Point: /CORTEX

The entry point remains `/CORTEX` for users:

```bash
# User runs:
/CORTEX analyze my-project

# Which resolves to:
docker exec cortex-mcp python -m cortex.cli analyze my-project

# Or via MCP:
POST https://cortex.company.local:8443/mcp/execute
{
  "tool": "analyze",
  "args": {"target": "my-project"}
}
```

Users configure VS Code:
```json
{
  "mcp.servers": {
    "cortex": {
      "url": "https://cortex.company.local:8443/mcp"
    }
  }
}
```

The MCP server handles `/CORTEX` commands internally.
