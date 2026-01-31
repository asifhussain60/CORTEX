================================================================================
🧠 CORTEX COMPREHENSIVE DUPLICATION AUDIT REPORT
================================================================================

📅 Generated: 2026-01-31T07:58:16.447319
📍 Repository: /Users/asifhussain/PROJECTS/CORTEX

================================================================================
📊 DUPLICATION SUMMARY
================================================================================

✅ Total Unique Classes: 606
✅ Total Unique Functions: 419
⚠️  CORE-035 Violations Found: 207
📈 Duplicate Items: 117

================================================================================
🔴 DETAILED VIOLATIONS (CORE-035 Enforcement)
================================================================================

❌ CLASS: AuditOperationType
   Locations: 2 implementations found
   [1] cortex/models/canonical_enums.py:117
   [2] cortex/brain/core/audit_required_validator.py:23

❌ CLASS: ChallengeType
   Locations: 2 implementations found
   [1] cortex/models/canonical_enums.py:149
   [2] cortex/orchestrators/core/challenge_engine.py:86

❌ CLASS: CircuitBreakerOpen
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:817
   [2] cortex_brain/tier2/resilience.py:900

❌ CLASS: CircuitBreakerState
   Locations: 2 implementations found
   [1] cortex/models/canonical_enums.py:240
   [2] cortex/brain/tier2/resilience/__init__.py:827

❌ CLASS: CleanerInterface
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/interface.py:160
   [2] cortex_brain/tier1/orchestrators/cleaners.py:98

❌ CLASS: ComplexityLevel
   Locations: 4 implementations found
   [1] cortex/core/orchestrator/complexity_assessment.py:14
   [2] cortex/models/canonical_enums.py:511
   [3] cortex/brain/core/observability/performance_profiler.py:37
   [4] cortex/interaction/bluf_system.py:27

❌ CLASS: ComplianceFramework
   Locations: 2 implementations found
   [1] cortex/brain/domain_orchestrators/business/base.py:18
   [2] cortex/infrastructure/compliance_marker.py:24

❌ CLASS: ComplianceLevel
   Locations: 3 implementations found
   [1] cortex/visualization/renderers/governance_heatmap_renderer.py:20
   [2] cortex/tools/governance_dashboard.py:27
   [3] cortex/mcp/compliance.py:14

❌ CLASS: ComponentFailure
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:52
   [2] cortex_brain/tier2/resilience.py:34

❌ CLASS: ComponentState
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:44
   [2] cortex/infrastructure/lifecycle_manager.py:29

❌ CLASS: ComponentType
   Locations: 3 implementations found
   [1] cortex/orchestrators/core/component_health.py:14
   [2] cortex/testing/discovery_scanner.py:44
   [3] cortex/infrastructure/bulkhead_manager.py:24

❌ CLASS: ConflictError
   Locations: 2 implementations found
   [1] cortex/domain_brain/optimistic_lock.py:12
   [2] cortex/core/state/optimistic_lock.py:58

❌ CLASS: CoverageGapDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:195
   [2] cortex/brain/core/knowledge/change_detection.py:418

❌ CLASS: CredentialStatus
   Locations: 3 implementations found
   [1] cortex/brain/tier2/credential_protection/__init__.py:26
   [2] cortex_brain/tier2/credential_protection.py:22
   [3] cortex_brain/tier2/credential_protection/__init__.py:38

❌ CLASS: DashboardSection
   Locations: 2 implementations found
   [1] cortex/devx/devx_dashboard.py:14
   [2] cortex/brain/devx/devx_dashboard.py:35

❌ CLASS: DashboardUpdateType
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:1362
   [2] cortex_brain/tier2/resilience.py:1359

❌ CLASS: DatabaseHealthCheck
   Locations: 2 implementations found
   [1] cortex/common/health_check.py:93
   [2] cortex/brain/observability/health_monitor.py:66

❌ CLASS: DecisionType
   Locations: 2 implementations found
   [1] cortex/execution/structured_decision.py:25
   [2] cortex/infrastructure/pre_commit_validator.py:99

❌ CLASS: DegradationLevel
   Locations: 3 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:36
   [2] cortex/infrastructure/graceful_degradation.py:22
   [3] cortex/infrastructure/degradation_manager.py:17

❌ CLASS: DisagreementType
   Locations: 3 implementations found
   [1] cortex/models/canonical_enums.py:536
   [2] cortex/orchestrators/core/challenge_engine.py:45
   [3] cortex/orchestrators/core/challenge_engine_plugins.py:21

❌ CLASS: EncryptionAlgorithm
   Locations: 3 implementations found
   [1] cortex/brain/tier2/credential_protection/__init__.py:20
   [2] cortex_brain/tier2/credential_protection.py:14
   [3] cortex_brain/tier2/credential_protection/__init__.py:17

❌ CLASS: EntityType
   Locations: 4 implementations found
   [1] cortex/models/canonical_enums.py:549
   [2] cortex/orchestrators/core/repository_scanner.py:37
   [3] cortex/orchestrators/core/relationship_analyzer.py:31
   [4] cortex_brain/domain_brain/models.py:16

❌ CLASS: ExecutionState
   Locations: 2 implementations found
   [1] cortex/mcp/executor.py:16
   [2] cortex_brain/tier2/hallucination_prevention/execution_sandbox.py:356

❌ CLASS: GateDecision
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/stage_2_5_gate.py:13
   [2] cortex/orchestrators/core/stage_2_5_gate.py:13

❌ CLASS: GovernanceViolationError
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/governance_registry.py:33
   [2] cortex/execution/exec_gateway_impl.py:35

❌ CLASS: HealthStatus
   Locations: 4 implementations found
   [1] cortex/core/registry/base_registry.py:53
   [2] cortex/models/canonical_enums.py:565
   [3] cortex/api/health_endpoints.py:23
   [4] cortex/brain/core/production_readiness_manager.py:33

❌ CLASS: IAuditLogger
   Locations: 2 implementations found
   [1] cortex/brain/core/interfaces.py:21
   [2] cortex/brain/core/interfaces/__init__.py:16

❌ CLASS: IExecutor
   Locations: 2 implementations found
   [1] cortex/core/interfaces.py:80
   [2] cortex/orchestrators/refactored_architecture.py:108

❌ CLASS: InputModality
   Locations: 2 implementations found
   [1] cortex/intent_router/multimodal_processor.py:17
   [2] cortex/brain/intent_router/multimodal_processor.py:28

❌ CLASS: IntegrationStatus
   Locations: 3 implementations found
   [1] cortex/testing/wiring_harness_inventory.py:34
   [2] cortex/devx/integration_validator.py:21
   [3] cortex/brain/devx/integration_validator.py:45

❌ CLASS: IntegrationTemplate
   Locations: 2 implementations found
   [1] cortex/tools/scaffolder_templates.py:568
   [2] cortex/orchestrators/domains/domain_templates.py:283

❌ CLASS: IntentCategory
   Locations: 3 implementations found
   [1] cortex/intent_router/classifier.py:16
   [2] cortex/brain/domain_brain/intent_classifier.py:7
   [3] cortex/brain/intent_router/classifier.py:33

❌ CLASS: IntentRouter
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/intent_router.py:236
   [2] cortex/brain/domain_brain/nlp_handler_router.py:24

❌ CLASS: IntentSignal
   Locations: 2 implementations found
   [1] cortex/intent_router/classifier.py:32
   [2] cortex/brain/intent_router/classifier.py:58

❌ CLASS: JourneyState
   Locations: 2 implementations found
   [1] cortex/config/unified_onboarding.py:21
   [2] cortex/orchestrators/onboarding/orchestrator.py:21

❌ CLASS: LogLevel
   Locations: 2 implementations found
   [1] cortex/infrastructure/tiered_logger.py:31
   [2] cortex/infrastructure/structured_logger.py:27

❌ CLASS: MDFileCategory
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/md_organizer.py:40
   [2] cortex_brain/tier1/orchestrators/cleaners/md_organizer.py:18

❌ CLASS: MDFileNamingIssue
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/md_organizer.py:56
   [2] cortex_brain/tier1/orchestrators/cleaners/md_organizer.py:33

❌ CLASS: MDOrganizerCleaner
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/md_organizer.py:71
   [2] cortex_brain/tier1/orchestrators/cleaners/md_organizer.py:42

❌ CLASS: MessageType
   Locations: 2 implementations found
   [1] cortex/mcp/protocol.py:178
   [2] cortex/knowledge/protocol/knowledge_protocol_spec.py:8

❌ CLASS: MetricType
   Locations: 5 implementations found
   [1] cortex/tools/toolkit/generate-tdd-cycle-data.py:26
   [2] cortex/intent_router/observability.py:15
   [3] cortex/brain/core/health_metrics.py:22
   [4] cortex/infrastructure/metrics_exporter.py:23
   [5] cortex_brain/tier2/governance/core_030_baselines.py:27

❌ CLASS: MetricUnit
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:1038
   [2] cortex_brain/tier2/resilience.py:1154

❌ CLASS: MutationType
   Locations: 2 implementations found
   [1] cortex/brain/core/mutation_guard.py:35
   [2] cortex_brain/tier2/hallucination_prevention/mutation_tracking.py:14

❌ CLASS: Ok
   Locations: 2 implementations found
   [1] cortex/core/result.py:31
   [2] cortex/brain/core/result.py:47

❌ CLASS: OperationMode
   Locations: 2 implementations found
   [1] cortex/core/interfaces.py:16
   [2] cortex/brain/core/interfaces/i_orchestrator.py:19

❌ CLASS: PhaseState
   Locations: 4 implementations found
   [1] cortex/core/state/phase_state_machine.py:18
   [2] cortex/orchestrators/domain/enhanced_planning_orchestrator.py:49
   [3] cortex/orchestrators/domain/autonomous_execution_engine.py:43
   [4] cortex/brain/core/state_machine.py:36

❌ CLASS: PhaseType
   Locations: 2 implementations found
   [1] cortex/tools/toolkit/generate-tdd-cycle-data.py:18
   [2] cortex/core/orchestrator/phase_events.py:14

❌ CLASS: Priority
   Locations: 2 implementations found
   [1] cortex/tools/feedback_agent.py:76
   [2] cortex/brain/core/intent/recommendation_engine.py:29

❌ CLASS: QualityMetricType
   Locations: 2 implementations found
   [1] cortex/orchestrators/response/unified_response_composer.py:68
   [2] cortex/orchestrators/response/ux_optimizer.py:33

❌ CLASS: RecoveryStrategy
   Locations: 2 implementations found
   [1] cortex/brain/core/resumption_handler.py:30
   [2] cortex_brain/tier2/hallucination_prevention/detection_recovery.py:35

❌ CLASS: ReflectionStatus
   Locations: 2 implementations found
   [1] cortex/core/intent/intent_reflection_protocol.py:21
   [2] cortex/brain/core/intent/intent_reflection_protocol.py:32

❌ CLASS: RelationshipType
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/relationship_analyzer.py:50
   [2] cortex/sensory/synaptic_network.py:29

❌ CLASS: ReloadState
   Locations: 2 implementations found
   [1] cortex/devx/hot_reload.py:86
   [2] cortex/brain/devx/hot_reload.py:56

❌ CLASS: ResourceType
   Locations: 3 implementations found
   [1] cortex/core/recovery/orphan_cleaner.py:19
   [2] cortex/orchestrators/domain/enhanced_planning_orchestrator.py:63
   [3] cortex/infrastructure/resource_tracker.py:20

❌ CLASS: ResponseFormat
   Locations: 6 implementations found
   [1] cortex/core/intent/lens_response_formatter.py:15
   [2] cortex/core/orchestrator/turn_response_generator.py:13
   [3] cortex/models/canonical_enums.py:589
   [4] cortex/orchestrators/response_challenge_injector.py:13
   [5] cortex/brain/core/intent/lens_response_formatter.py:32
   [6] cortex/interaction/bluf_system.py:44

❌ CLASS: Result
   Locations: 2 implementations found
   [1] cortex/core/result.py:230
   [2] cortex/brain/core/result.py:41

❌ CLASS: RetryExhaustedError
   Locations: 2 implementations found
   [1] cortex/common/exceptions.py:60
   [2] cortex/infrastructure/retry_strategy.py:21

❌ CLASS: RiskLevel
   Locations: 6 implementations found
   [1] cortex/visualization/renderers/impact_analysis_renderer.py:22
   [2] cortex/models/canonical_enums.py:499
   [3] cortex/orchestrators/core/git_analysis_engine.py:29
   [4] cortex/orchestrators/domain/enhanced_planning_orchestrator.py:72
   [5] cortex/brain/domain_orchestrators/business/base.py:27
   [6] cortex/interaction/bluf_system.py:20

❌ CLASS: ScenarioCategory
   Locations: 2 implementations found
   [1] cortex/devx/scenario_library.py:16
   [2] cortex/brain/devx/scenario_library.py:38

❌ CLASS: ScenarioStatus
   Locations: 2 implementations found
   [1] cortex/devx/scenario_library.py:25
   [2] cortex/brain/devx/scenario_library.py:49

❌ CLASS: SchemaDriftDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:153
   [2] cortex/brain/core/knowledge/change_detection.py:216

❌ CLASS: SecurityViolation
   Locations: 2 implementations found
   [1] cortex/brain/tier2/security/__init__.py:18
   [2] cortex_brain/tier2/security/__init__.py:271

❌ CLASS: SeverityColor
   Locations: 2 implementations found
   [1] cortex/core/intent/lens_response_formatter.py:23
   [2] cortex/brain/core/intent/lens_response_formatter.py:39

❌ CLASS: SeverityLevel
   Locations: 7 implementations found
   [1] cortex/core/knowledge/alert_pipeline.py:25
   [2] cortex/orchestrators/support/duplication_detector_orchestrator.py:50
   [3] cortex/orchestrators/support/duplication_registry.py:43
   [4] cortex/orchestrators/domain/enhanced_refactoring_orchestrator.py:58
   [5] cortex/brain/core/input_validator.py:25
   [6] cortex/brain/core/observability/performance_profiler.py:28
   [7] cortex/brain/core/knowledge/change_detection.py:53

❌ CLASS: StalenessDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:235
   [2] cortex/brain/core/knowledge/change_detection.py:510

❌ CLASS: StrategyType
   Locations: 2 implementations found
   [1] cortex/orchestrators/adaptive/unified_adaptive_layer.py:40
   [2] cortex/orchestrators/adaptive/strategy_selector.py:23

❌ CLASS: TierLevel
   Locations: 2 implementations found
   [1] cortex/core/orchestrator_dependency_registry.py:23
   [2] cortex/brain/core/knowledge_guidance_engine.py:49

❌ CLASS: ToolCategory
   Locations: 4 implementations found
   [1] cortex/mcp/unified_tool_discovery.py:27
   [2] cortex/mcp/tool_governance.py:16
   [3] cortex/orchestrators/mcp_tools_registry.py:21
   [4] cortex/orchestrators/core/tool_discovery_orchestrator.py:52

❌ CLASS: TransitionType
   Locations: 2 implementations found
   [1] cortex/core/state_machine.py:8
   [2] cortex/brain/core/state_machine.py:44

❌ CLASS: UserPreferenceMode
   Locations: 2 implementations found
   [1] cortex/models/canonical_enums.py:600
   [2] cortex/interaction/bluf_system.py:51

❌ CLASS: ValidationError
   Locations: 2 implementations found
   [1] cortex/common/validators.py:19
   [2] cortex/common/exceptions.py:267

❌ CLASS: ValidationLevel
   Locations: 2 implementations found
   [1] cortex/tools/template_validator.py:22
   [2] cortex/models/canonical_enums.py:260

❌ CLASS: ValidationResult
   Locations: 2 implementations found
   [1] cortex/templates/content_strategy.py:15
   [2] cortex/templates/knowledge_schema.py:13

❌ CLASS: ValidationSeverity
   Locations: 5 implementations found
   [1] cortex/core/safety/output_validator.py:18
   [2] cortex/domain_orchestrators/business/validation.py:11
   [3] cortex/devx/integration_validator.py:13
   [4] cortex/brain/domain_orchestrators/business/validation.py:15
   [5] cortex/brain/devx/integration_validator.py:37

❌ CLASS: VariableType
   Locations: 3 implementations found
   [1] cortex/orchestrators/response/response_templates.py:17
   [2] cortex/orchestrators/response/unified_response_composer.py:57
   [3] cortex/templates/knowledge_schema.py:20

❌ CLASS: ViolationType
   Locations: 7 implementations found
   [1] cortex/tools/naming_violation_detector.py:19
   [2] cortex/ci_cd/enforce_core_035.py:26
   [3] cortex/orchestrators/domain/enhanced_refactoring_orchestrator.py:48
   [4] cortex/testing/tdd_enhancement_layer1_precommit.py:19
   [5] cortex/execution/spec_validator_ci_cd.py:26
   [6] cortex_brain/tier2/security/__init__.py:16
   [7] cortex_brain/tier2/hallucination_prevention/boundary_rules.py:15

❌ CLASS: VolumeAnomalyDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:288
   [2] cortex/brain/core/knowledge/change_detection.py:591

❌ CLASS: WiringStatus
   Locations: 2 implementations found
   [1] cortex/tools/guided_wiring_orchestrator.py:30
   [2] cortex/orchestrators/wiring_harness_integration.py:13

❌ FUNCTION: analyze_knowledge_gap
   Locations: 2 implementations found
   [1] cortex/mcp/tools/knowledge/__init__.py:47
   [2] cortex/brain/mcp/tools/knowledge_tools.py:74

❌ FUNCTION: bundle_dependencies
   Locations: 2 implementations found
   [1] cortex/visualization/spa/dependency_bundler.py:293
   [2] cortex/visualization/scripts/bundle_dependencies.py:293

❌ FUNCTION: clear_orchestrator_registry
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:145
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:127

❌ FUNCTION: clear_tools
   Locations: 2 implementations found
   [1] cortex/mcp/decorator.py:150
   [2] cortex/mcp/decorators.py:83

❌ FUNCTION: dashboard
   Locations: 2 implementations found
   [1] cortex/cli/lens_dashboard.py:27
   [2] cortex/cli/commands/lens_dashboard.py:24

❌ FUNCTION: diagnose_orchestrator_issues
   Locations: 2 implementations found
   [1] cortex/mcp/tools/orchestration/__init__.py:93
   [2] cortex/brain/mcp/tools/orchestrator_tools.py:116

❌ FUNCTION: echo_tool
   Locations: 2 implementations found
   [1] cortex/mcp/tools/utility/__init__.py:22
   [2] cortex/brain/mcp/tools/utility_tools.py:28

❌ FUNCTION: generate
   Locations: 2 implementations found
   [1] cortex/cli/lens_dashboard.py:56
   [2] cortex/cli/commands/lens_dashboard.py:111

❌ FUNCTION: generate_knowledge_summary
   Locations: 2 implementations found
   [1] cortex/mcp/tools/knowledge/__init__.py:71
   [2] cortex/brain/mcp/tools/knowledge_tools.py:115

❌ FUNCTION: get_documentation_orchestrator
   Locations: 2 implementations found
   [1] cortex/orchestrators/documentation/orchestrator.py:926
   [2] cortex/orchestrators/domain/enhanced_documentation_orchestrator.py:708

❌ FUNCTION: get_governance_pregate
   Locations: 2 implementations found
   [1] cortex/core/governance_pregate.py:125
   [2] cortex/brain/core/governance_pregate.py:448

❌ FUNCTION: get_metrics_collector
   Locations: 2 implementations found
   [1] cortex/mcp/metrics.py:209
   [2] cortex/mcp/metrics_collector.py:123

❌ FUNCTION: get_operation_status
   Locations: 2 implementations found
   [1] cortex/mcp/tools/orchestration/__init__.py:22
   [2] cortex/brain/mcp/tools/orchestrator_tools.py:30

❌ FUNCTION: get_orchestrator_by_domain
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:112
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:105

❌ FUNCTION: get_orchestrators_by_domain
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:128
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:113

❌ FUNCTION: get_platform
   Locations: 2 implementations found
   [1] cortex/brain/dashboard/launch.py:29
   [2] cortex/brain/dashboard/serve-cortex-dashboard.py:71

❌ FUNCTION: get_project_root
   Locations: 2 implementations found
   [1] cortex/core/path_resolver.py:13
   [2] cortex/brain/core/path_resolver.py:27

❌ FUNCTION: get_recommendation_engine
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/solution_recommendation_engine.py:328
   [2] cortex/orchestrators/support/recommendation_engine.py:415

❌ FUNCTION: get_registered_orchestrators
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:102
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:100

❌ FUNCTION: get_registered_tools
   Locations: 3 implementations found
   [1] cortex/mcp/decorator.py:141
   [2] cortex/mcp/decorators.py:74
   [3] cortex/brain/mcp/decorator.py:80

❌ FUNCTION: get_registry
   Locations: 2 implementations found
   [1] cortex/wiring/registry/git_backed_registry.py:274
   [2] cortex/execution/spec_registry_impl.py:333

❌ FUNCTION: get_thread_join_timeout
   Locations: 2 implementations found
   [1] cortex/core/config/timeout_profiles.py:161
   [2] cortex/infrastructure/config.py:108

❌ FUNCTION: get_tool
   Locations: 2 implementations found
   [1] cortex/mcp/decorator.py:129
   [2] cortex/brain/mcp/decorator.py:86

❌ FUNCTION: invalidate_cache
   Locations: 2 implementations found
   [1] cortex/api/endpoints/lens_dashboard_routes.py:419
   [2] cortex/brain/observability/dashboard_extensibility.py:83

❌ FUNCTION: is_orchestrator
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:90
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:122

❌ FUNCTION: main
   Locations: 44 implementations found
   [1] cortex/visualization/scripts/bundle_vendor_assets.py:390
   [2] cortex/documentation/discovery_agent.py:350
   [3] cortex/tools/audit_md_generation.py:248
   [4] cortex/tools/guided_wiring_orchestrator.py:579
   [5] cortex/tools/toolkit.py:68
   [6] cortex/tools/verify_production_readiness.py:10
   [7] cortex/tools/safe_file_rename.py:270
   [8] cortex/tools/governance_dashboard.py:455
   [9] cortex/tools/vscode-diagnostics-provider.py:241
   [10] cortex/tools/phase_readiness_checker.py:512
   [11] cortex/tools/duplicate_detector.py:200
   [12] cortex/tools/generate-naming-inventory.py:74
   [13] cortex/tools/naming_violation_detector.py:235
   [14] cortex/tools/toolkit/copilot-request-generator.py:180
   [15] cortex/tools/toolkit/duplication_audit.py:251
   [16] cortex/tools/toolkit/run_integration_tests_with_timeout.py:97
   [17] cortex/tools/toolkit/update_imports.py:229
   [18] cortex/tools/toolkit/execute-track-eval-silent.py:295
   [19] cortex/tools/toolkit/generate-governance-data.py:149
   [20] cortex/tools/toolkit/generate-lifecycle-data.py:162
   [21] cortex/tools/toolkit/generate-tdd-cycle-data.py:280
   [22] cortex/ci_cd/enforce_core_035.py:278
   [23] cortex/mcp/__main__.py:28
   [24] cortex/cli/__main__.py:145
   [25] cortex/cli/commands/inquiry.py:209
   [26] cortex/orchestrators/onboarding/mcp_bootstrapper.py:269
   [27] cortex/orchestrators/onboarding/toolchain_validator.py:248
   [28] cortex/orchestrators/onboarding/dependency_resolver.py:276
   [29] cortex/orchestrators/onboarding/vscode_configurator.py:231
   [30] cortex/testing/routing_health_dashboard.py:330
   [31] cortex/testing/violation_detector.py:238
   [32] cortex/scripts/verify_environment.py:280
   [33] cortex/scripts/autonomous_phases_4_7.py:400
   [34] cortex/scripts/verify-cortex-installation.py:181
   [35] cortex/brain/ci_cd/compliance_gate.py:205
   [36] cortex/brain/mcp/tools/validate_consolidation.py:506
   [37] cortex/brain/mcp/tools/consolidate.py:557
   [38] cortex/brain/cli/governance_cli.py:396
   [39] cortex/brain/dashboard/launch.py:113
   [40] cortex/brain/dashboard/serve-cortex-dashboard.py:391
   [41] cortex/brain/knowledge/cache_builder.py:54
   [42] cortex/brain/governance/zero_breaking_changes_verifier.py:341
   [43] cortex/brain/production/readiness_assessment.py:438
   [44] cortex/infrastructure/database_log_rotation.py:313

❌ FUNCTION: mcp_tool
   Locations: 3 implementations found
   [1] cortex/mcp/decorator.py:77
   [2] cortex/mcp/decorators.py:11
   [3] cortex/brain/mcp/decorator.py:27

❌ FUNCTION: monitor_orchestrator_health
   Locations: 2 implementations found
   [1] cortex/mcp/tools/orchestration/__init__.py:45
   [2] cortex/brain/mcp/tools/orchestrator_tools.py:52

❌ FUNCTION: optimize_orchestrator_config
   Locations: 2 implementations found
   [1] cortex/mcp/tools/orchestration/__init__.py:69
   [2] cortex/brain/mcp/tools/orchestrator_tools.py:85

❌ FUNCTION: orchestrator
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:33
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:35

❌ FUNCTION: pytest_configure
   Locations: 2 implementations found
   [1] cortex/testing/pytest_plugin_audit.py:144
   [2] cortex/devx/pytest_progress_plugin.py:90

❌ FUNCTION: reset_registry
   Locations: 2 implementations found
   [1] cortex/wiring/registry/git_backed_registry.py:288
   [2] cortex/execution/spec_registry_impl.py:349

❌ FUNCTION: resolve_path
   Locations: 2 implementations found
   [1] cortex/core/path_resolver.py:33
   [2] cortex/brain/core/path_resolver.py:62

❌ FUNCTION: search_knowledge_base
   Locations: 2 implementations found
   [1] cortex/mcp/tools/knowledge/__init__.py:23
   [2] cortex/brain/mcp/tools/knowledge_tools.py:34

❌ FUNCTION: serve
   Locations: 4 implementations found
   [1] cortex/visualization/spa/static_server.py:238
   [2] cortex/cli/lens_dashboard.py:152
   [3] cortex/cli/lens_dashboard.py:258
   [4] cortex/cli/commands/lens_dashboard.py:38

❌ FUNCTION: transform_tool
   Locations: 2 implementations found
   [1] cortex/mcp/tools/utility/__init__.py:63
   [2] cortex/brain/mcp/tools/utility_tools.py:65

❌ FUNCTION: validate_ac_id
   Locations: 2 implementations found
   [1] cortex/brain/core/response_header_injector.py:70
   [2] cortex/brain/mcp/tools/governance_tools.py:111

❌ FUNCTION: validate_llm_output
   Locations: 2 implementations found
   [1] cortex/core/hallucination_prevention/output_validator.py:222
   [2] cortex/core/safety/output_validator.py:298

❌ FUNCTION: validate_schema
   Locations: 2 implementations found
   [1] cortex/mcp/domain_operations.py:83
   [2] cortex/common/validators.py:213

================================================================================
🎯 PRIORITY CONSOLIDATION TARGETS (CONS-Pattern)
================================================================================

1. HealthStatus
   Violations: 3
   Pattern: Use CONS-style composition pattern
   Action: Consolidate to UnifiedXXX class

2. ValidationResult
   Violations: 1
   Pattern: Use CONS-style composition pattern
   Action: Consolidate to UnifiedXXX class

3. Result
   Violations: 1
   Pattern: Use CONS-style composition pattern
   Action: Consolidate to UnifiedXXX class

================================================================================
📋 CORE-035 COMPLIANCE STATUS
================================================================================

⚠️  NON-COMPLIANT - 207 violations
❌ Duplication detected - consolidation required
🔒 DEPLOYMENT BLOCKED until duplicates resolved

================================================================================
📝 CONSOLIDATION PATTERN TEMPLATE (from CONS-003-009)
================================================================================

# Template for consolidation (100% backward compatible)

class UnifiedXXXComponent:
    '''Single canonical implementation (CORE-035 compliant).'''
    
    def __init__(self):
        # Delegate to existing implementations
        self._impl_a = ExistingImplementationA()
        self._impl_b = ExistingImplementationB()
    
    def execute(self, context):
        # Route to appropriate canonical handler
        if context.requires_implementation_a:
            return self._impl_a.execute(context)
        return self._impl_b.execute(context)

# Benefits:
# - Zero breaking changes (composition pattern)
# - Single entry point (CORE-035)
# - 85%+ consolidation value (proven in CONS-003-009)
# - Backward compatible (all existing code works)


================================================================================
✅ RECOMMENDATIONS FOR ZERO-DUPLICATION IMPLEMENTATION
================================================================================

1. BEFORE CODING (Implementation Truth - CORE-030):
   - Run this audit to detect existing implementations
   - Check cortex/ and cortex_brain/ for your class/function name
   - If found: use consolidation pattern instead of creating new

2. DURING IMPLEMENTATION (CORE-035 Enforcement):
   - Use composition pattern (proven in CONS-002-009)
   - Maintain 100% backward compatibility
   - Document as "Unified" canonical entry point
   - Add AC-ID tracking for governance audit

3. AFTER IMPLEMENTATION (Validation):
   - Re-run this audit to confirm zero new duplicates
   - Add tests for consolidation composition pattern
   - Log to governance audit trail with AC_ID
   - Update core-rules.yaml tracking

4. TESTING:
   - Run: pytest tests/ -k consolidation
   - Verify: 100% backward compatibility
   - Benchmark: Time savings from consolidation
   - Report: Update TRANSFORM-002 progress
