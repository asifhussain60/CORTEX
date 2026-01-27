# CORTEX Component Inventory
## Complete List of Components to Cherry-Pick

**Document:** 01-COMPONENT-INVENTORY.md  
**Date:** 2026-01-27  
**Status:** KEEP = Cherry-pick | REMOVE = Do not include

---

## 1. Infrastructure Layer (Enterprise-Grade)

### ✅ KEEP: cortex/infrastructure/

| File | Purpose | Priority |
|------|---------|----------|
| `enhanced_audit_logger.py` | Enterprise audit logging with hash chains | CRITICAL |
| `audit_logger.py` | Base audit logging | CRITICAL |
| `audit_hash_chain.py` | Immutable audit trail | CRITICAL |
| `circuit_breaker.py` | Resilience pattern | HIGH |
| `retry_strategy.py` | Retry with backoff | HIGH |
| `bulkhead_manager.py` | Resource isolation | HIGH |
| `graceful_degradation.py` | Fault tolerance | HIGH |
| `prometheus_metrics.py` | Observability metrics | HIGH |
| `alert_manager.py` | Alerting infrastructure | HIGH |
| `telemetry_provider.py` | Distributed tracing | MEDIUM |
| `tracing.py` | Request tracing | MEDIUM |
| `structured_logger.py` | JSON structured logs | HIGH |
| `tiered_logger.py` | Log level management | HIGH |
| `evidence_bundle.py` | Compliance evidence | MEDIUM |
| `compliance_marker.py` | Compliance tracking | MEDIUM |
| `threshold_monitor.py` | Performance monitoring | MEDIUM |
| `progress_tracker.py` | Operation progress | MEDIUM |
| `progress_aggregator.py` | Multi-operation tracking | MEDIUM |
| `resource_tracker.py` | Resource usage | MEDIUM |
| `hash_verifier.py` | Integrity verification | HIGH |
| `config.py` | Infrastructure config | CRITICAL |
| `pre_commit_validator.py` | Pre-commit hooks | MEDIUM |
| `log_growth_monitor.py` | Log management | LOW |

### ✅ KEEP: cortex/infrastructure/security/

| File | Purpose | Priority |
|------|---------|----------|
| `security_auditor.py` | Security audit | HIGH |
| `rate_limiter.py` | Rate limiting | HIGH |
| `cors_handler.py` | CORS management | HIGH |
| `defense_orchestrator.py` | Security orchestration | HIGH |
| `secrets_filter.py` | Secret redaction | CRITICAL |
| `input_validator.py` | Input sanitization | CRITICAL |
| `crypto_provider.py` | Cryptographic ops | HIGH |
| `cross_repo_enforcer.py` | Cross-repo policies | MEDIUM |

### ❌ REMOVE: cortex/infrastructure/

| File | Reason |
|------|--------|
| `wiring_contract_manager.py` | Legacy wiring |
| `wiring_drift_detector.py` | Legacy wiring |
| `pre_op_enforcer.py` | Redundant |
| `core035_compliance_check.py` | Consolidate into governance |
| `database.py` | No database in new arch |

---

## 2. Orchestrators (23 Production-Ready)

### ✅ KEEP: cortex/orchestrators/core/ (6 Core)

| File | Purpose | Priority |
|------|---------|----------|
| `master_orchestrator.py` | Main orchestrator | CRITICAL |
| `interaction_orchestrator.py` | User interaction | CRITICAL |
| `intent_router.py` | Intent classification | CRITICAL |
| `tdd_orchestrator.py` | TDD workflow | HIGH |
| `workflow_orchestrator.py` | Workflow management | HIGH |
| `lens_synthesis.py` | LENS protocol | CRITICAL |
| `challenge_engine.py` | User challenges | HIGH |
| `fuzzy_intent_matcher.py` | Fuzzy matching | HIGH |
| `comprehension_session.py` | Session management | HIGH |
| `governance_registry.py` | Governance rules | CRITICAL |
| `repository_scanner.py` | Repo analysis | MEDIUM |
| `git_history_analyzer.py` | Git analysis | MEDIUM |
| `knowledge_graph.py` | Knowledge management | HIGH |
| `clarity_measurement.py` | Clarity scoring | MEDIUM |
| `batch_processor.py` | Batch operations | MEDIUM |
| `stage_2_5_gate.py` | Stage gates | HIGH |
| `solution_recommendation_engine.py` | Recommendations | MEDIUM |
| `advanced_features.py` | Enterprise features | MEDIUM |
| `enterprise_features.py` | Enterprise features | MEDIUM |
| `onboarding_orchestrator.py` | User onboarding | MEDIUM |
| `tool_discovery_orchestrator.py` | Tool discovery | MEDIUM |
| `wrapped_tdd_orchestrator.py` | TDD wrapper | MEDIUM |

### ✅ KEEP: cortex/orchestrators/domain/ (6 Domain)

| File | Purpose | Priority |
|------|---------|----------|
| `refactoring_orchestrator.py` | Code refactoring | HIGH |
| `planning_orchestrator.py` | Planning | HIGH |
| `enhanced_refactoring_orchestrator.py` | Enhanced refactoring | HIGH |
| `enhanced_planning_orchestrator.py` | Enhanced planning | HIGH |
| `enhanced_documentation_orchestrator.py` | Documentation | MEDIUM |
| `phase_executor.py` | Phase execution | MEDIUM |
| `autonomous_execution_engine.py` | Autonomous exec | MEDIUM |
| `plan_pause_manager.py` | Plan management | LOW |
| `visual_progress_renderer.py` | Progress UI | LOW |
| `viewer_artifact_orchestrator.py` | Artifact viewing | LOW |
| `planning_registry_loader.py` | Registry loading | LOW |

### ❌ REMOVE: cortex/orchestrators/core/ (Legacy Wiring)

| File | Reason |
|------|--------|
| `database_registry.py` | Legacy DB wiring |
| `orchestrator_registry.py` | Legacy registry |
| `orchestrator_bootstrap.py` | Legacy bootstrap |
| `permanent_wiring_state.py` | Legacy state |
| `db_wiring_init.py` | Legacy DB init |
| `intent_router_factory.py` | Redundant |
| `master_orchestrator_stage_1.py` | Consolidated |
| `master_orchestrator_stage_4.py` | Consolidated |

---

## 3. Intent Router (Complete Module)

### ✅ KEEP: cortex/intent_router/

| File | Purpose | Priority |
|------|---------|----------|
| `classifier.py` | Intent classification | CRITICAL |
| `confidence_scorer.py` | Confidence scoring | HIGH |
| `context_manager.py` | Context management | HIGH |
| `disambiguator.py` | Ambiguity resolution | HIGH |
| `edge_case_handler.py` | Edge cases | HIGH |
| `fallback_strategy.py` | Fallback handling | HIGH |
| `intent_learner.py` | Learning | MEDIUM |
| `multimodal_processor.py` | Multi-modal | MEDIUM |
| `observability.py` | Monitoring | HIGH |
| `orchestration_integrator.py` | Integration | HIGH |
| `performance_metrics.py` | Metrics | MEDIUM |
| `routing_engine.py` | Routing | CRITICAL |
| `test_framework.py` | Testing | MEDIUM |
| `documentation.py` | Documentation | LOW |
| `documentation_manager.py` | Doc management | LOW |

---

## 4. MCP Server (Enhanced)

### ✅ KEEP: cortex/mcp/

| File | Purpose | Priority |
|------|---------|----------|
| `__init__.py` | Module init | CRITICAL |
| `__main__.py` | Entry point | CRITICAL |
| `orchestrator_mcp_server.py` | MCP server | CRITICAL |
| `cortex_tools.py` | Tool definitions | CRITICAL |
| `mcp_tools_catalog.py` | Tool catalog | CRITICAL |
| `compliance.py` | MCP compliance | HIGH |
| `decorator.py` | MCP decorators | HIGH |
| `decorators.py` | Tool decorators | HIGH |
| `discovery.py` | Tool discovery | HIGH |
| `domain_operations.py` | Domain ops | HIGH |
| `endpoints.py` | API endpoints | CRITICAL |
| `error_handler.py` | Error handling | HIGH |
| `executor.py` | Tool execution | CRITICAL |
| `input_validator.py` | Input validation | HIGH |
| `adapters/` | All 23 adapters | HIGH |
| `config/` | MCP configuration | HIGH |
| `models/` | MCP models | HIGH |

---

## 5. Core Module

### ✅ KEEP: cortex/core/

| File | Purpose | Priority |
|------|---------|----------|
| `interfaces.py` | Core interfaces | CRITICAL |
| `mode_controller.py` | Mode control | HIGH |
| `dependency_validator.py` | Dependency validation | HIGH |
| `feature_registry.py` | Feature registry | HIGH |
| `feature_audit.py` | Feature auditing | MEDIUM |
| `response_header_config.py` | Response headers | HIGH |
| `provenance_tracker.py` | Provenance tracking | MEDIUM |
| `brain_populator.py` | Brain population | MEDIUM |

### ✅ KEEP: cortex/core/intelligence/

| File | Purpose | Priority |
|------|---------|----------|
| `ast_intelligence.py` | AST analysis | HIGH |
| `dependency_mapper.py` | Dependency mapping | HIGH |
| `pattern_detector.py` | Pattern detection | HIGH |
| `call_graph.py` | Call graph analysis | MEDIUM |
| `routing_intelligence.py` | Routing intelligence | HIGH |
| `error_intelligence.py` | Error analysis | MEDIUM |
| `duration_intelligence.py` | Duration analysis | LOW |

### ✅ KEEP: cortex/core/hallucination_prevention/

| File | Purpose | Priority |
|------|---------|----------|
| `hallucination_detection.py` | Hallucination detection | HIGH |
| `output_validator.py` | Output validation | HIGH |
| `confidence_scoring.py` | Confidence scoring | HIGH |
| `vision_mutations.py` | Vision handling | MEDIUM |

### ✅ KEEP: cortex/core/security/

| File | Purpose | Priority |
|------|---------|----------|
| `isolation.py` | Security isolation | HIGH |

### ✅ KEEP: cortex/core/decorators/

| File | Purpose | Priority |
|------|---------|----------|
| `orchestrator_decorator.py` | Orchestrator decorators | HIGH |
| `governance_decorator.py` | Governance decorators | HIGH |

### ✅ KEEP: cortex/core/config/

| File | Purpose | Priority |
|------|---------|----------|
| `timeout_profiles.py` | Timeout configuration | HIGH |

---

## 6. Brain Module

### ✅ KEEP: cortex/brain/core/

| File | Purpose | Priority |
|------|---------|----------|
| `state_manager.py` | State management | HIGH |
| `distributed_lock.py` | Distributed locking | HIGH |
| `dependency_validator.py` | Dependency validation | HIGH |
| `mode_controller.py` | Mode control | HIGH |
| `interfaces.py` | Core interfaces | HIGH |
| `orchestrator_base.py` | Base orchestrator | HIGH |

### ✅ KEEP: cortex/brain/domain_brain/

| File | Purpose | Priority |
|------|---------|----------|
| `intent_classifier.py` | Intent classification | HIGH |
| `intent_parser.py` | Intent parsing | HIGH |
| `intent_router_interface.py` | Router interface | HIGH |
| `nlp_handler_router.py` | NLP handling | HIGH |
| `kg_querier.py` | Knowledge graph query | MEDIUM |
| `kg_indexer.py` | KG indexing | MEDIUM |
| `kg_inference.py` | KG inference | MEDIUM |
| `kg_validation.py` | KG validation | MEDIUM |
| `kg_deduplicator.py` | KG deduplication | MEDIUM |
| `kg_exchange.py` | KG exchange | MEDIUM |
| `kg_query_layer.py` | KG query layer | MEDIUM |
| `kg_query_interface.py` | KG query interface | MEDIUM |
| `kg_routing_optimizer.py` | KG routing | MEDIUM |
| `kg_ingest_adapter.py` | KG ingestion | MEDIUM |
| `kg_sync_orchestrator.py` | KG sync | MEDIUM |

### ✅ KEEP: cortex/brain/ide/

| File | Purpose | Priority |
|------|---------|----------|
| `vscode_integration.py` | VS Code integration | MEDIUM |

### ✅ KEEP: cortex/brain/governance_tools/

| File | Purpose | Priority |
|------|---------|----------|
| `governance_cli.py` | Governance CLI | MEDIUM |
| `batch_audit_logger.py` | Batch audit | MEDIUM |

---

## 7. Domain Brain

### ✅ KEEP: cortex/domain_brain/

| File | Purpose | Priority |
|------|---------|----------|
| `business_knowledge_repository.py` | Business knowledge | HIGH |
| `validator.py` | Validation | HIGH |
| `conflict_resolver.py` | Conflict resolution | HIGH |
| `bkio_orchestrator.py` | BKIO orchestrator | MEDIUM |
| `version_manager.py` | Version management | MEDIUM |
| `models.py` | Data models | HIGH |
| `audit_log_manager.py` | Audit management | HIGH |
| `deduplication.py` | Deduplication | MEDIUM |
| `lens_integration.py` | LENS integration | HIGH |
| `api.py` | API layer | HIGH |
| `orphan_detector.py` | Orphan detection | MEDIUM |
| `audit_logger.py` | Audit logging | HIGH |
| `optimistic_lock.py` | Optimistic locking | HIGH |
| `adapters.py` | Adapters | HIGH |

---

## 8. Governance

### ✅ KEEP: cortex/governance/

| File | Purpose | Priority |
|------|---------|----------|
| `policy_enforcer.py` | Policy enforcement | CRITICAL |
| `governance_analyzer.py` | Governance analysis | HIGH |
| `compliance_reporter.py` | Compliance reporting | HIGH |
| `filename_factory.py` | Filename policies | HIGH |
| `filename_factory_mcp.py` | MCP filename policies | MEDIUM |
| `audit_navigator.py` | Audit navigation | MEDIUM |

---

## 9. Knowledge Module

### ✅ KEEP: cortex/knowledge/

| File | Purpose | Priority |
|------|---------|----------|
| `__init__.py` | Module init | HIGH |
| `protocol/` | All protocol files | HIGH |

---

## 10. Tools Module

### ✅ KEEP: cortex/tools/

| File | Purpose | Priority |
|------|---------|----------|
| `total_recall_agent.py` | Feature discovery | HIGH |
| `git_history_analyzer.py` | Git analysis | HIGH |
| `duplicate_detector.py` | Duplicate detection | HIGH |
| `feedback_agent.py` | Feedback collection | MEDIUM |
| `governance_dashboard.py` | Governance UI | MEDIUM |
| `governance-cli.py` | Governance CLI | MEDIUM |
| `testing_framework.py` | Test framework | HIGH |
| `template_validator.py` | Template validation | MEDIUM |
| `template_parser.py` | Template parsing | MEDIUM |
| `toolkit.py` | Tool utilities | MEDIUM |
| `toolkit/` | Toolkit modules | MEDIUM |

### ❌ REMOVE: cortex/tools/

| File | Reason |
|------|--------|
| `wiring_*.py` | Legacy wiring tools |
| `guided_wiring_orchestrator.py` | Legacy wiring |
| `manual_registry_eliminator.py` | Legacy wiring |
| `unwired_component_detector.py` | Legacy wiring |
| `verify_registry.py` | Legacy registry |
| `cortex-vacuum.py` | Empty file |
| `ac_populator.py` | AC-specific |
| `phase_readiness_checker.py` | Legacy phasing |
| `orchestrator_scaffolder.py` | Legacy scaffolding |
| `scaffolder_templates.py` | Legacy templates |
| `tool_generator.py` | Legacy generation |
| `vscode-diagnostics-provider.py` | Consolidate |

---

## 11. Models

### ✅ KEEP: cortex/models/

| File | Purpose | Priority |
|------|---------|----------|
| `__init__.py` | Module init | CRITICAL |
| `canonical_enums.py` | Canonical enums (SSOT) | CRITICAL |
| `dashboard_models.py` | Dashboard models | MEDIUM |

---

## 12. Common Utilities

### ✅ KEEP: cortex/common/

| File | Purpose | Priority |
|------|---------|----------|
| `__init__.py` | Module init | CRITICAL |
| `exceptions.py` | Exception classes | CRITICAL |
| `validators.py` | Validators | HIGH |
| `file_utils.py` | File utilities | HIGH |
| `health_check.py` | Health checks | HIGH |
| `connection_utils.py` | Connection utils | MEDIUM |

---

## 13. CLI Module

### ✅ KEEP: cortex/cli/

| File | Purpose | Priority |
|------|---------|----------|
| `__init__.py` | Module init | HIGH |
| `health_check.py` | Health CLI | HIGH |
| `commands/` | CLI commands | MEDIUM |

---

## 14. cortex_brain (Governance Layer)

### ✅ KEEP: cortex_brain/tier0/governance/

| File | Purpose | Priority |
|------|---------|----------|
| `core-rules.yaml` | CORE-001 to CORE-040 | CRITICAL |
| All other .yaml files | Governance rules | CRITICAL |

### ✅ KEEP: cortex_brain/tier3/knowledge/

| File | Purpose | Priority |
|------|---------|----------|
| All 35+ YAML files | Best practices | HIGH |
| `ARCHITECTURE/` | Architecture patterns | HIGH |
| `SECURITY/` | Security patterns | HIGH |
| `DATA-MANAGEMENT/` | Data patterns | MEDIUM |
| `DOCUMENTATION/` | Doc standards | MEDIUM |

### ✅ KEEP: cortex_brain/tier0/

| File | Purpose | Priority |
|------|---------|----------|
| `path_abstraction.py` | Path handling | HIGH |
| `macos_path_compat.py` | macOS compatibility | MEDIUM |
| `windows_path_compat.py` | Windows compatibility | MEDIUM |
| `linux_path_compat.py` | Linux compatibility | MEDIUM |
| `import_resolver.py` | Import resolution | HIGH |

### ✅ KEEP: cortex_brain/tier1/

| File | Purpose | Priority |
|------|---------|----------|
| `orchestrators/cleaners.py` | Cleaners | MEDIUM |
| `orchestrators/cleaners_base.py` | Cleaner base | MEDIUM |
| `orchestrators/vacuum.py` | Vacuum | MEDIUM |
| `governance/confirmation_gate_rules.py` | Gate rules | HIGH |

### ✅ KEEP: cortex_brain/tier3/knowledge/

| File | Purpose | Priority |
|------|---------|----------|
| `synthesis_engine.py` | Knowledge synthesis | HIGH |
| `knowledge_governance.py` | Knowledge governance | HIGH |
| `expert_registry.py` | Expert registry | MEDIUM |
| `knowledge_indexer.py` | Knowledge indexing | MEDIUM |
| `retrieval_optimizer.py` | Retrieval optimization | MEDIUM |
| `ai_curator.py` | AI curation | MEDIUM |

### ✅ KEEP: cortex_brain/domain/

| File | Purpose | Priority |
|------|---------|----------|
| `domain_models.py` | Domain models | HIGH |
| `domain_factory.py` | Domain factory | HIGH |
| `domain_introspection.py` | Introspection | MEDIUM |
| `implementations/` | Domain implementations | MEDIUM |

### ❌ REMOVE: cortex_brain/

| Directory/File | Reason |
|----------------|--------|
| `state/` | Database state files |
| `tier0/test_*.py` | Test files (consolidate) |

---

## 15. Tests to Keep

### ✅ KEEP: tests/ (Applicable Only)

| Directory | Purpose | Count |
|-----------|---------|-------|
| `unit/orchestrators/` | Orchestrator unit tests | ~50 |
| `unit/infrastructure/` | Infrastructure tests | ~30 |
| `unit/intent_router/` | Intent router tests | ~20 |
| `mcp/` | MCP tests | ~30 |
| `integration/` | Integration tests (subset) | ~20 |
| `fixtures/` | Test fixtures | ALL |
| `conftest.py` | Test configuration | 1 |

### ❌ REMOVE: tests/

| Pattern | Reason |
|---------|--------|
| `test_rem_*.py` | Remediation tests |
| `test_ac_*.py` | AC-specific tests |
| `test_governance_database_*.py` | Legacy DB tests |
| `test_registry_init.py` | Legacy registry |
| `test_phase_*.py` | Legacy phasing |

---

## 16. Documentation to Keep

### ✅ KEEP: docs/ (Essential Only)

| File | Purpose |
|------|---------|
| `00-README.md` | Main README |
| `01-getting-started/installation.md` | Installation guide |
| `02-architecture/overview.md` | Architecture overview |

### ❌ REMOVE: docs/

| Pattern | Reason |
|---------|--------|
| `AC-*.md` | AC documentation |
| `*COMPLETION*.md` | Completion reports |
| `*PERMANENT*.md` | Permanent fix docs |
| All others | Regenerate as needed |

---

## 17. Root Files

### ✅ KEEP:

| File | Purpose |
|------|---------|
| `.gitignore` | Git ignore (UPDATED) |
| `requirements.txt` | Dependencies (SIMPLIFIED) |
| `pyproject.toml` | Project config |
| `pytest.ini` | Pytest config |

### ❌ REMOVE:

| File | Reason |
|------|--------|
| `cortex-config.yaml` | Consolidate |
| `mkdocs.yml` | Regenerate |
| `pyrightconfig.json` | Regenerate |
| `START-HERE.md` | Regenerate |
| `PHASE_*.md` | Legacy phasing |
| All root .md files | Clean up |

---

## Summary Counts

| Category | Keep | Remove |
|----------|------|--------|
| Infrastructure | 30 files | 5 files |
| Orchestrators | 35 files | 8 files |
| Intent Router | 15 files | 0 files |
| MCP Server | 20 files | 0 files |
| Core Module | 25 files | 0 files |
| Brain Module | 25 files | 5 files |
| Domain Brain | 15 files | 0 files |
| Governance | 6 files | 0 files |
| Tools | 12 files | 12 files |
| cortex_brain | 40+ files | 10 files |
| Tests | ~150 files | ~350 files |
| Documentation | 5 files | ~750 files |
| **TOTAL** | ~450 files | ~1,150 files |

**Reduction: 72% fewer files, 100% essential functionality preserved**
