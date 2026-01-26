================================================================================
🧠 CORTEX COMPREHENSIVE DUPLICATION AUDIT REPORT
================================================================================

📅 Generated: 2026-01-25T18:24:03.029403
📍 Repository: /Users/asifhussain/PROJECTS/CORTEX

================================================================================
📊 DUPLICATION SUMMARY
================================================================================

✅ Total Unique Classes: 464
✅ Total Unique Functions: 382
⚠️  CORE-035 Violations Found: 267
📈 Duplicate Items: 154

================================================================================
🔴 DETAILED VIOLATIONS (CORE-035 Enforcement)
================================================================================

❌ CLASS: ActionType
   Locations: 2 implementations found
   [1] cortex/brain/core/knowledge/change_detection_integration.py:39
   [2] cortex_brain/tier2/hallucination_prevention/canonicalization_engine.py:133

❌ CLASS: AlertPriority
   Locations: 2 implementations found
   [1] cortex/brain/core/knowledge/alert_system.py:57
   [2] cortex/infrastructure/progress_tracker.py:48

❌ CLASS: AlertSeverity
   Locations: 4 implementations found
   [1] cortex/brain/core/observability/alerting.py:19
   [2] cortex/brain/tier2/resilience/__init__.py:1582
   [3] cortex/infrastructure/alert_manager.py:18
   [4] cortex_brain/tier2/resilience.py:1623

❌ CLASS: AlertState
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:1589
   [2] cortex/infrastructure/alert_manager.py:26

❌ CLASS: AnalysisHandler
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/domain_orchestrator.py:160
   [2] cortex/brain/domain_orchestrators/domain_orchestrator.py:80

❌ CLASS: ApprovalStatus
   Locations: 3 implementations found
   [1] cortex/orchestrators/core/comprehension_session.py:21
   [2] cortex/orchestrators/core/dor_approval_gate.py:27
   [3] cortex/brain/core/intent/comprehension_loop.py:60

❌ CLASS: AuditEventType
   Locations: 3 implementations found
   [1] cortex/confirmation/governance.py:15
   [2] cortex/orchestrators/core/planning_audit_trail.py:52
   [3] cortex/brain/observability/audit_trail.py:27

❌ CLASS: AuditOperationType
   Locations: 2 implementations found
   [1] cortex/brain/core/audit_required_validator.py:23
   [2] cortex_brain/domain_brain/models.py:28

❌ CLASS: BrainTier
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/comprehension_session.py:29
   [2] cortex/brain/core/intent/comprehension_loop.py:68

❌ CLASS: ChallengeCategory
   Locations: 3 implementations found
   [1] cortex/core/intent/challenge_generator.py:20
   [2] cortex/orchestrators/challenge_generator.py:15
   [3] cortex/brain/core/intent/challenge_generator.py:25

❌ CLASS: ChallengeType
   Locations: 4 implementations found
   [1] cortex/core/orchestrator/turn_response_with_challenges.py:13
   [2] cortex/orchestrators/core/planner_orchestrator.py:72
   [3] cortex/orchestrators/response/unified_response_composer.py:71
   [4] cortex/orchestrators/domain/planning_orchestrator.py:55

❌ CLASS: ChangeType
   Locations: 3 implementations found
   [1] cortex/core/knowledge/change_detection.py:29
   [2] cortex/devx/hot_reload.py:19
   [3] cortex/brain/devx/hot_reload.py:65

❌ CLASS: CheckpointStatus
   Locations: 2 implementations found
   [1] cortex/core/checkpoint_manager.py:14
   [2] cortex/brain/core/checkpoint_manager.py:32

❌ CLASS: CircuitBreakerOpen
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:817
   [2] cortex_brain/tier2/resilience.py:904

❌ CLASS: CircuitBreakerState
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:827
   [2] cortex_brain/tier2/resilience.py:897

❌ CLASS: CleanerInterface
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/interface.py:160
   [2] cortex_brain/tier1/orchestrators/cleaners.py:98

❌ CLASS: CleanerNotFoundError
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/registry.py:31
   [2] cortex_brain/tier1/orchestrators/cleaners.py:281

❌ CLASS: CleanerRegistrationError
   Locations: 2 implementations found
   [1] cortex/brain/tier1/orchestrators/cleaners/registry.py:25
   [2] cortex_brain/tier1/orchestrators/cleaners.py:276

❌ CLASS: CoherenceType
   Locations: 2 implementations found
   [1] cortex/brain/tier2/coherence/__init__.py:24
   [2] cortex_brain/tier2/coherence/__init__.py:16

❌ CLASS: CommandType
   Locations: 2 implementations found
   [1] cortex/governance_tools/governance_cli.py:14
   [2] cortex/cli/commands/documentation.py:28

❌ CLASS: ComplexityLevel
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/complexity_assessment.py:14
   [2] cortex/brain/core/observability/performance_profiler.py:37

❌ CLASS: ComplianceFramework
   Locations: 2 implementations found
   [1] cortex/brain/domain_orchestrators/business/base.py:18
   [2] cortex/infrastructure/compliance_marker.py:24

❌ CLASS: ComplianceLevel
   Locations: 2 implementations found
   [1] cortex/tools/governance_dashboard.py:27
   [2] cortex/mcp/compliance.py:14

❌ CLASS: ComponentFailure
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:52
   [2] cortex_brain/tier2/resilience.py:34

❌ CLASS: ComponentState
   Locations: 2 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:44
   [2] cortex/infrastructure/lifecycle_manager.py:29

❌ CLASS: ComponentStatus
   Locations: 2 implementations found
   [1] cortex/tools/unwired_component_detector.py:35
   [2] cortex/tools/wiring_validation_agent.py:30

❌ CLASS: ComponentType
   Locations: 3 implementations found
   [1] cortex/orchestrators/core/component_health.py:14
   [2] cortex/testing/discovery_scanner.py:44
   [3] cortex/infrastructure/bulkhead_manager.py:23

❌ CLASS: ConflictError
   Locations: 2 implementations found
   [1] cortex/domain_brain/optimistic_lock.py:12
   [2] cortex/core/state/optimistic_lock.py:58

❌ CLASS: ContinuationReason
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/continuation_decision.py:20
   [2] cortex/brain/core/orchestrator/continuation_decision.py:16

❌ CLASS: CoverageGapDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:202
   [2] cortex/brain/core/knowledge/change_detection.py:418

❌ CLASS: CreateHandler
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/domain_orchestrator.py:67
   [2] cortex/brain/domain_orchestrators/domain_orchestrator.py:44

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
   [2] cortex_brain/tier2/resilience.py:1363

❌ CLASS: DatabaseHealthCheck
   Locations: 2 implementations found
   [1] cortex/common/health_check.py:93
   [2] cortex/brain/observability/health_monitor.py:66

❌ CLASS: DegradationLevel
   Locations: 3 implementations found
   [1] cortex/brain/tier2/resilience/__init__.py:36
   [2] cortex/infrastructure/graceful_degradation.py:22
   [3] cortex/infrastructure/degradation_manager.py:17

❌ CLASS: DomainPlugin
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/business/plugins.py:11
   [2] cortex/brain/domain_orchestrators/business/plugins.py:26

❌ CLASS: EdgeType
   Locations: 2 implementations found
   [1] cortex/core/knowledge/knowledge_graph.py:36
   [2] cortex/brain/core/knowledge/knowledge_graph.py:102

❌ CLASS: EncryptionAlgorithm
   Locations: 3 implementations found
   [1] cortex/brain/tier2/credential_protection/__init__.py:20
   [2] cortex_brain/tier2/credential_protection.py:14
   [3] cortex_brain/tier2/credential_protection/__init__.py:17

❌ CLASS: EntityType
   Locations: 3 implementations found
   [1] cortex/orchestrators/core/repository_scanner.py:37
   [2] cortex/orchestrators/core/relationship_analyzer.py:31
   [3] cortex_brain/domain_brain/models.py:15

❌ CLASS: ErrorOccurredEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:68
   [2] cortex/brain/core/orchestrator/terminal_events.py:85

❌ CLASS: ExecutionGateType
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/planner_orchestrator.py:81
   [2] cortex/orchestrators/domain/planning_orchestrator.py:64

❌ CLASS: ExecutionMode
   Locations: 4 implementations found
   [1] cortex/scripts-root-archive/create_stubs.py:17
   [2] cortex/orchestrators/adaptive/execution_modes.py:18
   [3] cortex/orchestrators/adaptive/unified_adaptive_layer.py:37
   [4] cortex_brain/tier2/hallucination_prevention/execution_sandbox.py:253

❌ CLASS: ExecutionState
   Locations: 3 implementations found
   [1] cortex/scripts-root-archive/create_stubs.py:24
   [2] cortex/mcp/executor.py:16
   [3] cortex_brain/tier2/hallucination_prevention/execution_sandbox.py:264

❌ CLASS: ExecutionStrategy
   Locations: 2 implementations found
   [1] cortex/tools/toolkit/test_optimization_suite.py:35
   [2] cortex/execution/adaptive_execution_engine.py:15

❌ CLASS: FixHandler
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/domain_orchestrator.py:129
   [2] cortex/brain/domain_orchestrators/domain_orchestrator.py:68

❌ CLASS: GateDecision
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/stage_2_5_gate.py:13
   [2] cortex/orchestrators/core/stage_2_5_gate.py:13

❌ CLASS: GovernanceViolationEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:86
   [2] cortex/brain/core/orchestrator/terminal_events.py:119

❌ CLASS: HallucinationPattern
   Locations: 2 implementations found
   [1] cortex/scripts-root-archive/create_stubs.py:119
   [2] cortex_brain/tier2/hallucination_prevention/detection_recovery.py:13

❌ CLASS: IExecutor
   Locations: 2 implementations found
   [1] cortex/core/interfaces.py:178
   [2] cortex/orchestrators/refactored_architecture.py:108

❌ CLASS: IOrchestrator
   Locations: 3 implementations found
   [1] cortex/core/interfaces.py:68
   [2] cortex/brain/core/interfaces.py:85
   [3] cortex/brain/core/interfaces/i_orchestrator.py:27

❌ CLASS: InputModality
   Locations: 2 implementations found
   [1] cortex/intent_router/multimodal_processor.py:17
   [2] cortex/brain/intent_router/multimodal_processor.py:28

❌ CLASS: IntegrationHandler
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/domain_orchestrator.py:230
   [2] cortex/brain/domain_orchestrators/domain_orchestrator.py:104

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
   [1] cortex/orchestrators/core/intent_router.py:92
   [2] cortex/brain/domain_brain/nlp_handler_router.py:24

❌ CLASS: IntentSignal
   Locations: 2 implementations found
   [1] cortex/intent_router/classifier.py:32
   [2] cortex/brain/intent_router/classifier.py:58

❌ CLASS: IntentType
   Locations: 4 implementations found
   [1] cortex/core/intent/intent_canonicalizer.py:12
   [2] cortex/orchestrators/core/intent_router.py:34
   [3] cortex/brain/core/governance_enforcer.py:23
   [4] cortex/brain/core/intent/intent_canonicalizer.py:23

❌ CLASS: JourneyState
   Locations: 2 implementations found
   [1] cortex/config/unified_onboarding.py:21
   [2] cortex/orchestrators/onboarding/orchestrator.py:17

❌ CLASS: LogLevel
   Locations: 2 implementations found
   [1] cortex/infrastructure/tiered_logger.py:32
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

❌ CLASS: MaxTurnsReachedEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:54
   [2] cortex/brain/core/orchestrator/terminal_events.py:68

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
   [2] cortex_brain/tier2/resilience.py:1158

❌ CLASS: ModifyHandler
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/domain_orchestrator.py:98
   [2] cortex/brain/domain_orchestrators/domain_orchestrator.py:56

❌ CLASS: MutationType
   Locations: 2 implementations found
   [1] cortex/brain/core/mutation_guard.py:35
   [2] cortex_brain/tier2/hallucination_prevention/mutation_tracking.py:153

❌ CLASS: NodeType
   Locations: 2 implementations found
   [1] cortex/core/knowledge/knowledge_graph.py:14
   [2] cortex/brain/core/knowledge/knowledge_graph.py:69

❌ CLASS: Ok
   Locations: 2 implementations found
   [1] cortex/core/result.py:31
   [2] cortex/brain/core/result.py:47

❌ CLASS: OperationMode
   Locations: 2 implementations found
   [1] cortex/core/interfaces.py:14
   [2] cortex/brain/core/interfaces/i_orchestrator.py:19

❌ CLASS: OptimizationHandler
   Locations: 2 implementations found
   [1] cortex/domain_orchestrators/domain_orchestrator.py:195
   [2] cortex/brain/domain_orchestrators/domain_orchestrator.py:92

❌ CLASS: PhaseCompletedEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:34
   [2] cortex/brain/core/orchestrator/terminal_events.py:37

❌ CLASS: PhaseState
   Locations: 2 implementations found
   [1] cortex/core/state/phase_state_machine.py:18
   [2] cortex/brain/core/state_machine.py:37

❌ CLASS: PhaseType
   Locations: 2 implementations found
   [1] cortex/tools/toolkit/generate-tdd-cycle-data.py:18
   [2] cortex/core/orchestrator/phase_events.py:14

❌ CLASS: Priority
   Locations: 2 implementations found
   [1] cortex/tools/feedback_agent.py:76
   [2] cortex/brain/core/intent/recommendation_engine.py:30

❌ CLASS: QualityMetricType
   Locations: 2 implementations found
   [1] cortex/orchestrators/response/unified_response_composer.py:79
   [2] cortex/orchestrators/response/ux_optimizer.py:33

❌ CLASS: RecoveryStrategy
   Locations: 2 implementations found
   [1] cortex/brain/core/resumption_handler.py:30
   [2] cortex_brain/tier2/hallucination_prevention/detection_recovery.py:201

❌ CLASS: ReflectionStatus
   Locations: 2 implementations found
   [1] cortex/core/intent/intent_reflection_protocol.py:21
   [2] cortex/brain/core/intent/intent_reflection_protocol.py:32

❌ CLASS: ReloadState
   Locations: 2 implementations found
   [1] cortex/devx/hot_reload.py:90
   [2] cortex/brain/devx/hot_reload.py:56

❌ CLASS: ResourceType
   Locations: 2 implementations found
   [1] cortex/core/recovery/orphan_cleaner.py:19
   [2] cortex/infrastructure/resource_tracker.py:20

❌ CLASS: ResponseFormat
   Locations: 4 implementations found
   [1] cortex/core/intent/lens_response_formatter.py:15
   [2] cortex/core/orchestrator/turn_response_generator.py:13
   [3] cortex/orchestrators/response_challenge_injector.py:13
   [4] cortex/brain/core/intent/lens_response_formatter.py:32

❌ CLASS: ResponseType
   Locations: 2 implementations found
   [1] cortex/orchestrators/response/response_templates.py:86
   [2] cortex/orchestrators/response/unified_response_composer.py:54

❌ CLASS: Result
   Locations: 2 implementations found
   [1] cortex/core/result.py:230
   [2] cortex/brain/core/result.py:41

❌ CLASS: RetryExhaustedError
   Locations: 2 implementations found
   [1] cortex/common/exceptions.py:60
   [2] cortex/infrastructure/retry_strategy.py:21

❌ CLASS: RiskLevel
   Locations: 2 implementations found
   [1] cortex/orchestrators/core/git_analysis_engine.py:29
   [2] cortex/brain/domain_orchestrators/business/base.py:27

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
   [1] cortex/core/knowledge/change_detection.py:160
   [2] cortex/brain/core/knowledge/change_detection.py:216

❌ CLASS: SecurityViolation
   Locations: 2 implementations found
   [1] cortex/brain/tier2/security/__init__.py:18
   [2] cortex_brain/tier2/security/__init__.py:271

❌ CLASS: Severity
   Locations: 3 implementations found
   [1] cortex/core/knowledge/change_detection.py:40
   [2] cortex/orchestrators/challenge_generator.py:26
   [3] cortex/brain/core/intent/challenge_generator.py:35

❌ CLASS: SeverityColor
   Locations: 2 implementations found
   [1] cortex/core/intent/lens_response_formatter.py:23
   [2] cortex/brain/core/intent/lens_response_formatter.py:39

❌ CLASS: SeverityLevel
   Locations: 4 implementations found
   [1] cortex/core/knowledge/alert_pipeline.py:25
   [2] cortex/brain/core/input_validator.py:25
   [3] cortex/brain/core/observability/performance_profiler.py:28
   [4] cortex/brain/core/knowledge/change_detection.py:53

❌ CLASS: StalenessDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:242
   [2] cortex/brain/core/knowledge/change_detection.py:510

❌ CLASS: StrategyType
   Locations: 2 implementations found
   [1] cortex/orchestrators/adaptive/unified_adaptive_layer.py:44
   [2] cortex/orchestrators/adaptive/strategy_selector.py:23

❌ CLASS: TierLevel
   Locations: 2 implementations found
   [1] cortex/brain/core/orchestrator_dependency_registry.py:23
   [2] cortex/brain/core/knowledge_guidance_engine.py:50

❌ CLASS: TokenLimitEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:77
   [2] cortex/brain/core/orchestrator/terminal_events.py:102

❌ CLASS: ToolCategory
   Locations: 3 implementations found
   [1] cortex/mcp/registry.py:21
   [2] cortex/mcp/tool_governance.py:16
   [3] cortex/orchestrators/mcp_tools_registry.py:21

❌ CLASS: TransitionType
   Locations: 2 implementations found
   [1] cortex/core/state_machine.py:8
   [2] cortex/brain/core/state_machine.py:45

❌ CLASS: UserApprovalRejectedEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:94
   [2] cortex/brain/core/orchestrator/terminal_events.py:135

❌ CLASS: UserCancelledEvent
   Locations: 2 implementations found
   [1] cortex/core/orchestrator/terminal_events.py:47
   [2] cortex/brain/core/orchestrator/terminal_events.py:53

❌ CLASS: ValidationError
   Locations: 2 implementations found
   [1] cortex/common/validators.py:19
   [2] cortex/common/exceptions.py:267

❌ CLASS: ValidationLevel
   Locations: 3 implementations found
   [1] cortex/tools/template_validator.py:22
   [2] cortex/core/hallucination_prevention/output_validator.py:16
   [3] cortex/brain/governance_tools/governance_cli.py:12

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
   [1] cortex/orchestrators/response/response_templates.py:16
   [2] cortex/orchestrators/response/unified_response_composer.py:62
   [3] cortex/templates/knowledge_schema.py:20

❌ CLASS: ViolationType
   Locations: 3 implementations found
   [1] cortex/testing/tdd_enhancement_layer1_precommit.py:19
   [2] cortex_brain/tier2/security/__init__.py:16
   [3] cortex_brain/tier2/hallucination_prevention/boundary_rules.py:15

❌ CLASS: VolumeAnomalyDetector
   Locations: 2 implementations found
   [1] cortex/core/knowledge/change_detection.py:295
   [2] cortex/brain/core/knowledge/change_detection.py:591

❌ CLASS: WiringStatus
   Locations: 2 implementations found
   [1] cortex/tools/guided_wiring_orchestrator.py:30
   [2] cortex/orchestrators/wiring_harness_integration.py:13

❌ FUNCTION: analyze_knowledge_gap
   Locations: 2 implementations found
   [1] cortex/mcp/tools/knowledge/__init__.py:47
   [2] cortex/brain/mcp/tools/knowledge_tools.py:74

❌ FUNCTION: check_domain_health
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:248
   [2] cortex/brain/observability/dashboard_extensibility.py:248

❌ FUNCTION: clear_orchestrator_registry
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:145
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:129

❌ FUNCTION: clear_tools
   Locations: 2 implementations found
   [1] cortex/mcp/decorator.py:150
   [2] cortex/mcp/decorators.py:83

❌ FUNCTION: compute_hash
   Locations: 2 implementations found
   [1] cortex/brain/governance_tools/batch_audit_logger.py:11
   [2] cortex/brain/domain_orchestrators/batch_audit_logger.py:11

❌ FUNCTION: diagnose_orchestrator_issues
   Locations: 2 implementations found
   [1] cortex/mcp/tools/orchestration/__init__.py:93
   [2] cortex/brain/mcp/tools/orchestrator_tools.py:116

❌ FUNCTION: echo_tool
   Locations: 2 implementations found
   [1] cortex/mcp/tools/utility/__init__.py:22
   [2] cortex/brain/mcp/tools/utility_tools.py:28

❌ FUNCTION: enrich_batch_context
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:196
   [2] cortex/brain/observability/dashboard_extensibility.py:196

❌ FUNCTION: enrich_dashboard_context
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:139
   [2] cortex/brain/observability/dashboard_extensibility.py:139

❌ FUNCTION: generate_knowledge_summary
   Locations: 2 implementations found
   [1] cortex/mcp/tools/knowledge/__init__.py:71
   [2] cortex/brain/mcp/tools/knowledge_tools.py:115

❌ FUNCTION: get_business_context
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:92
   [2] cortex/brain/observability/dashboard_extensibility.py:92

❌ FUNCTION: get_cache_status
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:64
   [2] cortex/brain/observability/dashboard_extensibility.py:64

❌ FUNCTION: get_documentation
   Locations: 2 implementations found
   [1] cortex/intent_router/documentation.py:61
   [2] cortex/brain/intent_router/documentation.py:45

❌ FUNCTION: get_governance_pregate
   Locations: 2 implementations found
   [1] cortex/core/governance_pregate.py:125
   [2] cortex/brain/core/governance_pregate.py:448

❌ FUNCTION: get_operation_status
   Locations: 2 implementations found
   [1] cortex/mcp/tools/orchestration/__init__.py:22
   [2] cortex/brain/mcp/tools/orchestrator_tools.py:30

❌ FUNCTION: get_orchestrator_by_domain
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:112
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:107

❌ FUNCTION: get_orchestrators_by_domain
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:128
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:115

❌ FUNCTION: get_platform
   Locations: 3 implementations found
   [1] cortex/scripts-root-archive/utilities/launch-dashboard.py:37
   [2] cortex/brain/dashboard/launch.py:29
   [3] cortex/brain/dashboard/serve-cortex-dashboard.py:71

❌ FUNCTION: get_project_root
   Locations: 2 implementations found
   [1] cortex/core/path_resolver.py:13
   [2] cortex/brain/core/path_resolver.py:27

❌ FUNCTION: get_registered_orchestrators
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:102
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:102

❌ FUNCTION: get_registered_tools
   Locations: 3 implementations found
   [1] cortex/mcp/decorator.py:141
   [2] cortex/mcp/decorators.py:74
   [3] cortex/brain/mcp/decorator.py:80

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
   [1] cortex/observability/dashboard_extensibility.py:83
   [2] cortex/brain/observability/dashboard_extensibility.py:83

❌ FUNCTION: is_domain_available
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:54
   [2] cortex/brain/observability/dashboard_extensibility.py:54

❌ FUNCTION: is_orchestrator
   Locations: 2 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:90
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:124

❌ FUNCTION: learning_path
   Locations: 2 implementations found
   [1] cortex/knowledge/best_practices_discovery.py:273
   [2] cortex/knowledge/knowledge_repository_integration.py:226

❌ FUNCTION: log_ac_audit_trail
   Locations: 2 implementations found
   [1] cortex/scripts-root-archive/maintenance/log_phase_remediation_07_audit.py:18
   [2] cortex/scripts-root-archive/maintenance/log_phase_03_audit.py:19

❌ FUNCTION: log_ac_lifecycle
   Locations: 2 implementations found
   [1] cortex/brain/intent_router/batch_audit_logger.py:14
   [2] cortex/brain/intent_router/audit_logger.py:24

❌ FUNCTION: main
   Locations: 74 implementations found
   [1] cortex/documentation/discovery_agent.py:350
   [2] cortex/tools/unwired_component_detector.py:529
   [3] cortex/tools/guided_wiring_orchestrator.py:579
   [4] cortex/tools/toolkit.py:68
   [5] cortex/tools/verify_production_readiness.py:10
   [6] cortex/tools/governance_dashboard.py:455
   [7] cortex/tools/vscode-diagnostics-provider.py:241
   [8] cortex/tools/phase_readiness_checker.py:512
   [9] cortex/tools/governance-cli.py:312
   [10] cortex/tools/duplicate_detector.py:200
   [11] cortex/tools/wiring_validation_agent.py:688
   [12] cortex/tools/toolkit/test_optimization_suite.py:263
   [13] cortex/tools/toolkit/copilot-request-generator.py:180
   [14] cortex/tools/toolkit/duplication_audit.py:251
   [15] cortex/tools/toolkit/run_integration_tests_with_timeout.py:97
   [16] cortex/tools/toolkit/update_imports.py:229
   [17] cortex/tools/toolkit/transform_002_redundancy_analyzer.py:286
   [18] cortex/tools/toolkit/execute-track-eval-silent.py:295
   [19] cortex/tools/toolkit/generate-governance-data.py:149
   [20] cortex/tools/toolkit/generate-lifecycle-data.py:162
   [21] cortex/tools/toolkit/generate-tdd-cycle-data.py:280
   [22] cortex/scripts-root-archive/fix_12_issues.py:237
   [23] cortex/scripts-root-archive/tdd_gap_analysis.py:49
   [24] cortex/scripts-root-archive/validate_mcp.py:29
   [25] cortex/scripts-root-archive/ac_fix_db_persist_001.py:290
   [26] cortex/scripts-root-archive/update_imports.py:394
   [27] cortex/scripts-root-archive/migration-validator.py:183
   [28] cortex/scripts-root-archive/test-performance-auditor.py:438
   [29] cortex/scripts-root-archive/migrate_folder_structure.py:354
   [30] cortex/scripts-root-archive/regenerate_audit_log.py:128
   [31] cortex/scripts-root-archive/test-analytics.py:240
   [32] cortex/scripts-root-archive/setup_cortex_hub.py:516
   [33] cortex/scripts-root-archive/validate_imports.py:195
   [34] cortex/scripts-root-archive/detect_hanging_tests.py:57
   [35] cortex/scripts-root-archive/utilities/phase_b1_update.py:39
   [36] cortex/scripts-root-archive/utilities/launch-dashboard.py:48
   [37] cortex/scripts-root-archive/utilities/phase_b3_update.py:76
   [38] cortex/scripts-root-archive/utilities/phase_b2_update.py:63
   [39] cortex/scripts-root-archive/utilities/run-cortex-vacuum.py:222
   [40] cortex/scripts-root-archive/deployment/sanitize_governance_db.py:229
   [41] cortex/scripts-root-archive/deployment/generate_templates.py:226
   [42] cortex/scripts-root-archive/deployment/track_sanitize_state.py:351
   [43] cortex/scripts-root-archive/deployment/validate_sanitization.py:211
   [44] cortex/scripts-root-archive/maintenance/phase_14_completion.py:393
   [45] cortex/scripts-root-archive/maintenance/log_phase_remediation_07_audit.py:80
   [46] cortex/scripts-root-archive/maintenance/update_imports.py:284
   [47] cortex/scripts-root-archive/maintenance/phase_13_domain_completion.py:494
   [48] cortex/scripts-root-archive/maintenance/migrate_folder_structure.py:503
   [49] cortex/scripts-root-archive/maintenance/migrate_knowledge_to_tier3.py:176
   [50] cortex/scripts-root-archive/maintenance/rebuild_phase_yaml_with_evidence.py:267
   [51] cortex/scripts-root-archive/maintenance/consolidate_phases.py:175
   [52] cortex/scripts-root-archive/maintenance/record_phase10_audit.py:10
   [53] cortex/scripts-root-archive/maintenance/log_phase_03_audit.py:80
   [54] cortex/scripts-root-archive/maintenance/init_db.py:127
   [55] cortex/scripts-root-archive/validation/validate_phase_deliverables.py:332
   [56] cortex/scripts-root-archive/validation/validate_phase_sync.py:313
   [57] cortex/mcp/__main__.py:28
   [58] cortex/orchestrators/onboarding/mcp_bootstrapper.py:269
   [59] cortex/orchestrators/onboarding/toolchain_validator.py:248
   [60] cortex/orchestrators/onboarding/setup_orchestrator.py:360
   [61] cortex/orchestrators/onboarding/dependency_resolver.py:276
   [62] cortex/orchestrators/onboarding/vscode_configurator.py:231
   [63] cortex/testing/violation_detector.py:238
   [64] cortex/scripts/verify_environment.py:280
   [65] cortex/scripts/autonomous_phases_4_7.py:400
   [66] cortex/scripts/verify-cortex-installation.py:181
   [67] cortex/brain/ci_cd/compliance_gate.py:205
   [68] cortex/brain/mcp/tools/validate_consolidation.py:506
   [69] cortex/brain/mcp/tools/consolidate.py:557
   [70] cortex/brain/cli/governance_cli.py:396
   [71] cortex/brain/dashboard/launch.py:113
   [72] cortex/brain/dashboard/serve-cortex-dashboard.py:391
   [73] cortex/brain/governance/zero_breaking_changes_verifier.py:341
   [74] cortex/infrastructure/test_isolation.py:187

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
   Locations: 3 implementations found
   [1] cortex/core/decorators/orchestrator_decorator.py:33
   [2] cortex/brain/core/decorators/orchestrator_decorator.py:37
   [3] cortex/brain/core/decorators/orchestrator.py:174

❌ FUNCTION: pytest_configure
   Locations: 2 implementations found
   [1] cortex/testing/pytest_plugin_audit.py:144
   [2] cortex/devx/pytest_progress_plugin.py:90

❌ FUNCTION: resolve_path
   Locations: 2 implementations found
   [1] cortex/core/path_resolver.py:31
   [2] cortex/brain/core/path_resolver.py:62

❌ FUNCTION: search_knowledge_base
   Locations: 2 implementations found
   [1] cortex/mcp/tools/knowledge/__init__.py:23
   [2] cortex/brain/mcp/tools/knowledge_tools.py:34

❌ FUNCTION: transform_tool
   Locations: 2 implementations found
   [1] cortex/mcp/tools/utility/__init__.py:63
   [2] cortex/brain/mcp/tools/utility_tools.py:65

❌ FUNCTION: update_file
   Locations: 3 implementations found
   [1] cortex/scripts-root-archive/utilities/phase_b1_update.py:19
   [2] cortex/scripts-root-archive/utilities/phase_b3_update.py:18
   [3] cortex/scripts-root-archive/utilities/phase_b2_update.py:19

❌ FUNCTION: validate_ac_id
   Locations: 2 implementations found
   [1] cortex/brain/core/response_header_injector.py:68
   [2] cortex/brain/mcp/tools/governance_tools.py:121

❌ FUNCTION: validate_llm_output
   Locations: 2 implementations found
   [1] cortex/core/hallucination_prevention/output_validator.py:225
   [2] cortex/core/safety/output_validator.py:298

❌ FUNCTION: validate_schema
   Locations: 2 implementations found
   [1] cortex/mcp/domain_operations.py:83
   [2] cortex/common/validators.py:213

❌ FUNCTION: with_business_context
   Locations: 2 implementations found
   [1] cortex/observability/dashboard_extensibility.py:221
   [2] cortex/brain/observability/dashboard_extensibility.py:221

================================================================================
🎯 PRIORITY CONSOLIDATION TARGETS (CONS-Pattern)
================================================================================

1. ValidationResult
   Violations: 1
   Pattern: Use CONS-style composition pattern
   Action: Consolidate to UnifiedXXX class

2. Result
   Violations: 1
   Pattern: Use CONS-style composition pattern
   Action: Consolidate to UnifiedXXX class

================================================================================
📋 CORE-035 COMPLIANCE STATUS
================================================================================

⚠️  NON-COMPLIANT - 267 violations
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
