# Quick Reference

## __init__



## base_orchestrator

### `BaseOrchestrator`
 (inherits: ABC)


- `execute(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`
- `get_status(self) -> Dict[str, Any]`




## error_handler

### `ErrorSeverity`
 (inherits: Enum)




### `RecoveryStrategy`
 (inherits: Enum)




### `OrchestratorError`




### `ErrorHandler`


- `handle_error(self, phase: str, exception: Exception, severity: ErrorSeverity, recovery_strategy: Optional[RecoveryStrategy], context: Optional[Dict[str, Any]]) -> OrchestratorError`
- `can_retry(self, phase: str) -> bool`
- `record_retry(self, phase: str) -> int`
- `reset_retries(self, phase: str) -> None`
- `get_error_summary(self) -> Dict[str, Any]`
- `has_critical_errors(self) -> bool`
- `clear_errors(self) -> None`




## phase_manager

### `PhaseStatus`
 (inherits: Enum)




### `Phase`




### `PhaseTransition`




### `PhaseManager`


- `register_phase(self, name: str, description: str, required: bool, validation: Optional[Callable[[], bool]], cleanup: Optional[Callable[[], None]]) -> Phase`
- `start_phase(self, phase_name: str) -> None`
- `complete_phase(self, phase_name: str, result: Optional[Dict[str, Any]]) -> None`
- `fail_phase(self, phase_name: str, error: str) -> None`
- `skip_phase(self, phase_name: str, reason: str) -> None`
- `get_progress(self) -> Dict[str, Any]`
- `get_phase_status(self, phase_name: str) -> PhaseStatus`
- `reset(self) -> None`




## __init__



## __init__



## documentation_orchestrator

### `DocumentationConfig`




### `DocumentationResult`




### `DocumentationOrchestrator`
 (inherits: BaseOrchestrator)






## __init__



## execution_orchestrator

### `ExecutionOrchestrator`
 (inherits: BaseOrchestrator)


- `register_sub_orchestrator(self, name: str, orchestrator: Any) -> None`
- `register_validator(self, name: str, validator: Callable) -> None`




## __init__



## code_analyzer

### `MethodInfo`




### `ClassInfo`




### `FunctionInfo`




### `ModuleInfo`




### `CodeAnalyzer`


- `analyze_file(self, file_path: Path) -> ModuleInfo`




## type_extractor

### `TypeExtractor`


- `extract_type_info(self, annotation: Optional[ast.expr]) -> Dict[str, Any]`
- `format_type_for_docs(self, type_info: Dict[str, Any]) -> str`
- `extract_return_type_description(self, docstring: Optional[str]) -> Optional[str]`
- `extract_param_descriptions(self, docstring: Optional[str]) -> Dict[str, str]`




## __init__



## api_doc_generator

### `APIDocGenerator`


- `generate_module_docs(self, module_info: ModuleInfo, output_path: Path, include_private: bool) -> Path`
- `generate_multi_module_docs(self, modules: List[ModuleInfo], output_dir: Path, index_name: str) -> Path`
- `generate_quick_reference(self, modules: List[ModuleInfo], output_path: Path) -> Path`




## diagram_generator

### `DiagramGenerator`


- `generate_class_hierarchy(self, modules: List[ModuleInfo], output_path: Path, title: str) -> Path`
- `generate_phase_flow_diagram(self, phase_data: List[Dict[str, Any]], output_path: Path, title: str) -> Path`
- `generate_sequence_diagram(self, sequences: List[Dict[str, Any]], output_path: Path, title: str) -> Path`




## __init__



## ado

- `format_work_item_result(result: WorkItemResult, json_output: bool) -> str`
- `format_validation_result(result: ValidationResult, json_output: bool) -> str`
- `cmd_create(args: argparse.Namespace) -> int`
- `cmd_load(args: argparse.Namespace) -> int`
- `cmd_update(args: argparse.Namespace) -> int`
- `cmd_summary(args: argparse.Namespace) -> int`
- `cmd_validate_dor(args: argparse.Namespace) -> int`
- `cmd_validate_dod(args: argparse.Namespace) -> int`
- `cmd_list(args: argparse.Namespace) -> int`
- `main()`


## align

- `run_align(auto_fix: bool, dry_run: bool, force_full: bool, quick_mode: bool) -> Dict[str, Any]`
- `run_governance_tokens(command: str) -> Dict[str, Any]`
- `main()`


## application_onboarding_operation

### `ApplicationOnboardingOperation`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]`


- `create_application_onboarding_operation() -> ApplicationOnboardingOperation`


## architecture_graph_builder

### `ArchitectureNode`




### `ArchitectureEdge`




### `ArchitectureGraphBuilder`


- `build_graph(self, file_paths: List[Path]) -> Dict[str, Any]`


- `generate_architecture_json(project_path: Path, output_path: Path) -> Dict[str, Any]`


## base_operation_module

### `OperationPhase`
 (inherits: Enum)


- `order(self) -> int`


### `ExecutionMode`
 (inherits: Enum)




### `OperationStatus`
 (inherits: Enum)




### `OperationResult`




### `OperationModuleMetadata`




### `BaseOperationModule`
 (inherits: ABC)


- `metadata(self) -> OperationModuleMetadata`
- `execution_mode(self) -> ExecutionMode`
- `execution_mode(self, mode: ExecutionMode) -> None`
- `is_dry_run(self) -> bool`
- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`
- `log_info(self, message: str) -> None`
- `log_error(self, message: str) -> None`
- `log_warning(self, message: str) -> None`
- `log_debug(self, message: str) -> None`
- `resolve_plan_file(self, user_reference: str, brain_path: Optional[Path]) -> Dict[str, Any]`




## cache_commands

- `cache_status_command(args: Dict[str, Any]) -> str`
- `cache_clear_command(args: Dict[str, Any]) -> str`
- `cache_invalidate_command(args: Dict[str, Any]) -> str`
- `register_cache_commands(command_router)`


## cache_dashboard

### `CacheMetrics`




### `CacheDashboard`


- `show_dashboard(self, detailed: bool)`


- `main()`


## cleanup

### `CleanupCategory`
 (inherits: Enum)




### `CleanupResult`


- `add_file(self, path: str, size: int)`
- `add_directory(self, path: str, size: int)`
- `add_error(self, message: str)`
- `add_skip(self, path: str, reason: str)`
- `total_items_removed(self) -> int`
- `space_freed_mb(self) -> float`


- `is_safe_to_delete(path: Path, project_root: Path) -> Tuple[bool, str]`
- `find_temp_files(project_root: Path, cache_instance) -> List[Path]`
- `find_old_logs(project_root: Path, days_old: int, cache_instance) -> List[Path]`
- `find_large_cache_files(project_root: Path, min_size_mb: int, cache_instance) -> List[Path]`
- `get_size(path: Path) -> int`
- `cleanup_workspace(project_root: Path, dry_run: bool, categories: List[CleanupCategory], confirm: bool) -> Dict[str, Any]`
- `main()`


## commit

- `run_commit(**kwargs)`
- `main()`
- `run_commit(project_root: Path, auto_add_untracked: bool, rebase: bool, commit_message: str) -> Dict[str, Any]`
- `main()`


## commit_and_push

### `CommitAndPushOrchestrator`


- `execute(self, commit_message: Optional[str]) -> Dict`


- `main()`


## dashboard_data_adapter

### `DashboardMetadata`




### `QualityIssue`




### `SecurityVulnerability`




### `PerformanceMetric`




### `DashboardDataAdapter`


- `transform_metadata(self, project_info: Dict[str, Any]) -> Dict[str, Any]`
- `transform_quality_data(self, quality_issues: List[Any], quality_score: float) -> Dict[str, Any]`
- `transform_security_data(self, vulnerabilities: List[Any]) -> Dict[str, Any]`
- `transform_performance_data(self, metrics: List[Any]) -> Dict[str, Any]`
- `save_dashboard_data(self, metadata: Dict[str, Any], quality: Dict[str, Any], security: Dict[str, Any], performance: Dict[str, Any], architecture: Optional[Dict[str, Any]]) -> None`
- `generate_full_dashboard_data(self, project_info: Dict[str, Any], quality_issues: List[Any], quality_score: float, vulnerabilities: List[Any], metrics: List[Any], architecture_graph: Optional[Dict[str, Any]]) -> None`




## dashboard_generator

### `DashboardGenerator`


- `generate(self, output_path: Path, title: str, project_info: Dict[str, Any], quality_data: Dict[str, Any], security_data: Dict[str, Any], architecture_data: Dict[str, Any], techstack_data: Dict[str, Any], recommendations_data: list, uml_diagram: str) -> Path`


- `generate_dashboard_html(template_path: Path, output_path: Path, title: str, project_info: Dict[str, Any], quality_data: Dict[str, Any], security_data: Dict[str, Any], architecture_data: Dict[str, Any], techstack_data: Dict[str, Any], recommendations_data: list, uml_diagram: str) -> Path`


## dashboard_validator

### `ValidationTest`




### `ValidationResult`


- `issues(self) -> List[str]`
- `warnings(self) -> List[str]`


### `DashboardValidator`


- `validate_all(self) -> Tuple[bool, Dict[str, Any]]`
- `generate_report(self) -> str`


- `validate_dashboard(output_dir: Path) -> Tuple[bool, Dict[str, Any], str]`


## dashboard_validator_v2

### `ValidationTest`




### `TabValidation`


- `passed(self) -> bool`
- `errors(self) -> List[ValidationTest]`
- `warnings(self) -> List[ValidationTest]`
- `passed_count(self) -> int`


### `DashboardValidator`


- `validate_all(self) -> Tuple[bool, Dict[str, Any]]`
- `print_report(self)`


- `validate_dashboard(output_dir: Path, dashboard_path: Optional[Path]) -> Tuple[bool, Dict[str, Any]]`


## dependency_installer

### `DependencyResult`




### `DependencyInstaller`


- `install_dependencies(self, create_venv: bool, skip_validation: bool) -> DependencyResult`
- `get_installed_packages(self) -> List[str]`


- `main()`


## deploy

- `run_deploy(dry_run: bool, branch: str, skip_align: bool)`
- `main()`


## documentation_component_registry

### `DocumentationComponent`




### `DocumentationComponentRegistry`


- `register(self, component: DocumentationComponent)`
- `list_components(self) -> List[Dict[str, Any]]`
- `get_dependents(self, component_id: str) -> List[str]`
- `execute(self, component_id: str, output_path: Optional[Path], profile: str, force_regenerate: bool, validate_output: bool, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]`
- `execute_pipeline(self, component_ids: List[str], output_path: Optional[Path], profile: str, stop_on_failure: bool) -> Dict[str, Any]`


- `create_default_registry(workspace_root: Optional[Path]) -> DocumentationComponentRegistry`


## environment_setup

### `SetupResult`


- `to_dict(self) -> Dict[str, Any]`


### `EnvironmentSetup`


- `run(self, profile: str) -> SetupResult`


- `run_setup(profile: str, project_root: Optional[Path]) -> SetupResult`


## environment_setup_module

### `EnvironmentSetupModule`
 (inherits: BaseOperationModule)


- `validate(self, context: Dict[str, Any]) -> tuple[bool, str]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `cleanup(self) -> None`


- `register() -> BaseOperationModule`


## git_checkpoint

- `run_checkpoint(**kwargs) -> dict`
- `main()`


## header_formatter

### `HeaderFormatter`


- `format_minimalist(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: datetime) -> str`
- `format_banner(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: datetime) -> str`
- `format_completion(success: bool, duration_seconds: float, summary: str) -> str`




## header_utils

- `format_minimalist_header(operation_name: str, version: str, profile: str, mode: str, purpose: Optional[str]) -> str`
- `print_minimalist_header(operation_name: str, version: str, profile: str, mode: str, purpose: Optional[str]) -> None`
- `print_banner_header(operation_name: str, version: str, profile: str) -> None`
- `format_completion_footer(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[list]) -> str`
- `print_completion_footer(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[list]) -> None`


## healthcheck

- `run_healthcheck()`
- `main()`


## healthcheck_operation

### `HealthCheckOperation`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate(self) -> OperationResult`
- `execute(self, context: Optional[Dict[str, Any]]) -> OperationResult`
- `rollback(self) -> OperationResult`




## help_command

### `HelpCommand`


- `generate_help(self, format: str) -> str`
- `get_operation_by_command(self, command: str) -> Dict[str, Any]`


- `show_help(format: str) -> str`
- `find_command(command: str) -> Dict[str, Any]`


## onboarding_orchestrator

### `OnboardingResult`




### `OnboardingOrchestrator`


- `onboard_application(self, project_path: Path, project_name: Optional[str]) -> OnboardingResult`


- `main()`


## operations_orchestrator

### `OperationExecutionReport`




### `OperationsOrchestrator`


- `execute_operation(self, context: Optional[Dict[str, Any]]) -> OperationExecutionReport`
- `get_module_execution_order(self) -> List[str]`




## operation_factory

### `OperationFactory`


- `get_available_operations(self) -> List[str]`
- `get_operation_info(self, operation_id: str) -> Optional[Dict[str, Any]]`
- `create_operation(self, operation_id: str, profile: str, context: Optional[Dict[str, Any]]) -> Optional[OperationsOrchestrator]`
- `list_operation_modules(self, operation_id: str, profile: str) -> List[str]`
- `get_natural_language_mappings(self) -> Dict[str, str]`
- `find_operation_by_input(self, user_input: str) -> Optional[str]`




## operation_header_formatter

### `OperationHeaderFormatter`


- `format_minimalist(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime], purpose: Optional[str]) -> str`
- `format_banner(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime]) -> str`
- `format_completion(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[List[str]]) -> str`
- `print_minimalist(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime], purpose: Optional[str]) -> None`
- `print_banner(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime]) -> None`
- `print_completion(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[List[str]]) -> None`




## optimize

- `run_optimize(target: str, aggressive: bool, dry_run: bool, skip_skull_tests: bool)`
- `run_token_optimization(command: str)`
- `main()`


## optimize_operation

### `OptimizeOperation`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate(self) -> OperationResult`
- `execute(self, **kwargs) -> OperationResult`
- `rollback(self) -> OperationResult`




## optimize_tokens

### `OptimizationResult`




### `TokenOptimizer`


- `create_backup(self, label: str) -> Path`
- `restore_backup(self, backup_path: Path) -> bool`
- `validate_yaml_syntax(self, yaml_path: Path) -> Tuple[bool, Optional[str]]`
- `get_current_tokens(self) -> Dict[str, int]`
- `optimize_quick(self) -> OptimizationResult`
- `optimize_full(self) -> OptimizationResult`
- `optimize_auto(self) -> OptimizationResult`
- `show_status(self) -> None`
- `rollback_last(self) -> bool`


- `safe_print(message: str) -> None`
- `main()`


## planning

- `run_planning(**kwargs) -> dict`
- `main()`


## policy_scanner

### `PolicyFormat`
 (inherits: Enum)




### `PolicyDocument`




### `PolicyScanner`


- `scan_for_policies(self) -> List[PolicyDocument]`
- `has_policies(self) -> bool`
- `create_starter_policies(self, output_path: Optional[Path]) -> Path`




## realtime_dashboard_auth

### `TokenStatus`
 (inherits: Enum)




### `AuthToken`




### `AuditLogEntry`




### `RealtimeDashboardAuth`


- `generate_token(self, user_id: str, is_admin: bool, metadata: Optional[Dict[str, Any]]) -> str`
- `validate_token(self, token: str) -> Optional[Dict[str, Any]]`
- `revoke_token(self, token: str) -> bool`
- `cleanup_expired_tokens(self) -> int`
- `get_active_sessions(self) -> List[Dict[str, Any]]`
- `get_audit_log(self, user_id: Optional[str], limit: int) -> List[Dict[str, Any]]`




## realtime_dashboard_server

### `WebSocketConnection`


- `is_rate_limited(self, max_messages: int, window_seconds: int) -> bool`
- `increment_message_count(self)`
- `update_heartbeat(self)`
- `is_stale(self, timeout_seconds: int) -> bool`


### `RealtimeDashboardServer`


- `generate_auth_token(self, user_id: str, is_admin: bool) -> str`
- `validate_token(self, token: str) -> Optional[Dict[str, Any]]`
- `handle_connection(self, websocket: WebSocketServerProtocol, path: str)`
- `handle_message(self, connection: WebSocketConnection, message: str)`
- `broadcast(self, message: Dict[str, Any], admin_only: bool)`
- `send_to_connection(self, connection_id: str, message: Dict[str, Any])`
- `heartbeat_monitor(self)`
- `start(self)`
- `stop(self)`
- `get_stats(self) -> Dict[str, Any]`


- `main()`


## realtime_metrics_publisher

### `PublishChannel`
 (inherits: Enum)




### `OperationProgress`




### `MetricsUpdate`




### `RealtimeMetricsPublisher`


- `start(self)`
- `stop(self)`
- `publish_operation_progress(self, operation: str, progress: float, status: str, total: Optional[int], current: Optional[int], metadata: Optional[Dict[str, Any]])`
- `publish_alert(self, severity: MetricSeverity, component: str, metric: str, value: Any, threshold: Any, message: str, action_required: bool)`
- `publish_health_update(self, health_score: float, components: Dict[str, Any])`
- `get_active_operations(self) -> Dict[str, OperationProgress]`
- `clear_completed_operation(self, operation: str)`


- `main()`


## recommendations_engine

### `Recommendation`




### `RecommendationsEngine`


- `generate_recommendations(self, security_issues: List[Any], quality_issues: List[Any], tech_stack: Dict[str, Any], architecture: Dict[str, Any]) -> List[Dict[str, Any]]`


- `generate_recommendations_json(security_issues: List[Any], quality_issues: List[Any], tech_stack: Dict[str, Any], architecture: Dict[str, Any], output_path) -> List[Dict[str, Any]]`


## response_formatter

### `ResponseFormatter`


- `format_operation_result(operation_name: str, result: Any, context: Dict[str, Any], is_help: bool) -> str`
- `reset_session()`


- `format_for_copilot(operation_name: str, result: Any, context: Dict[str, Any]) -> str`


## resume_conversation

### `ResumeConversationOperation`


- `execute(self, user_query: str) -> Dict[str, Any]`
- `resume_by_id(self, conversation_id: str) -> Dict[str, Any]`




## review

- `format_output(result, json_output: bool)`
- `cmd_create(args)`
- `cmd_load(args)`
- `cmd_analyze(args)`
- `cmd_report(args)`
- `cmd_list(args)`
- `main()`


## rollback

- `run_rollback(**kwargs) -> dict`
- `main()`


## setup

### `Platform`
 (inherits: Enum)




### `SetupResult`


- `add_error(self, message: str)`
- `add_warning(self, message: str)`
- `to_dict(self) -> Dict[str, Any]`


- `detect_platform() -> Platform`
- `validate_python() -> Tuple[bool, str]`
- `validate_git() -> Tuple[bool, str]`
- `validate_vscode() -> bool`
- `create_virtual_environment(project_root: Path) -> Tuple[bool, str]`
- `install_dependencies(project_root: Path) -> Tuple[bool, int, str]`
- `configure_gitignore(project_root: Path) -> Tuple[bool, str]`
- `initialize_brain_databases(project_root: Path) -> Tuple[bool, str]`
- `setup_environment(profile: str, project_root: Path) -> Dict[str, Any]`


## tdd

- `format_result(result: TDDResult, json_output: bool) -> str`
- `cmd_start(args: argparse.Namespace) -> int`
- `cmd_test(args: argparse.Namespace) -> int`
- `cmd_pass(args: argparse.Namespace) -> int`
- `cmd_refactor(args: argparse.Namespace) -> int`
- `cmd_complete(args: argparse.Namespace) -> int`
- `cmd_status(args: argparse.Namespace) -> int`
- `cmd_skeleton(args: argparse.Namespace) -> int`
- `main()`


## techstack_analyzer

### `TechStackAnalyzer`


- `analyze(self) -> Dict[str, Any]`


- `generate_techstack_json(project_path: Path, output_path: Path) -> Dict[str, Any]`


## user_consent_manager

### `ConsentAction`
 (inherits: Enum)




### `ConsentResult`




### `UserConsentManager`


- `request_onboarding_consent(self, detected_info: Dict[str, Any]) -> ConsentResult`
- `request_dashboard_consent(self) -> bool`
- `request_policy_validation_consent(self, policy_path: str) -> bool`
- `confirm_action(self, action: str, consequences: List[str], default: bool) -> bool`
- `request_policy_validation_consent(self, policy_path: Optional[Path]) -> bool`


- `main()`


## user_onboarding_operation

### `UserOnboardingOperation`
 (inherits: BaseOperationModule)


- `execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]`


- `create_user_onboarding_operation() -> UserOnboardingOperation`


## __init__

- `execute_operation(operation_id_or_input: str, profile: str, project_root: Optional[Path], **kwargs) -> OperationExecutionReport`
- `list_operations() -> Dict[str, Dict[str, Any]]`
- `get_operation_modules(operation_id: str, profile: str) -> list[str]`
- `create_orchestrator(operation_id: str, profile: str, context: Optional[Dict[str, Any]]) -> Optional[OperationsOrchestrator]`
- `show_help(format: str) -> str`


## base_crawler

### `BaseCrawler`
 (inherits: ABC)


- `crawl(self) -> Dict[str, Any]`
- `get_name(self) -> str`
- `execute(self) -> Dict[str, Any]`
- `handle_error(self, error: Exception, execution_time: float) -> Dict[str, Any]`
- `log_warning(self, message: str)`
- `log_info(self, message: str)`
- `log_error(self, message: str)`




## brain_inspector

### `BrainInspectorCrawler`
 (inherits: BaseCrawler)


- `get_name(self) -> str`
- `crawl(self) -> Dict[str, Any]`




## doc_mapper

### `DocMapperCrawler`
 (inherits: BaseCrawler)


- `get_name(self) -> str`
- `crawl(self) -> Dict[str, Any]`




## file_scanner

### `FileScannerCrawler`
 (inherits: BaseCrawler)


- `get_name(self) -> str`
- `crawl(self) -> Dict[str, Any]`




## git_analyzer

### `GitAnalyzerCrawler`
 (inherits: BaseCrawler)


- `get_name(self) -> str`
- `crawl(self) -> Dict[str, Any]`




## health_assessor

### `HealthAssessorCrawler`
 (inherits: BaseCrawler)


- `get_name(self) -> str`
- `crawl(self) -> Dict[str, Any]`




## plugin_registry

### `PluginRegistryCrawler`
 (inherits: BaseCrawler)


- `get_name(self) -> str`
- `crawl(self) -> Dict[str, Any]`




## __init__



## real_time_collectors

### `CollectorResult`




### `BaseDataCollector`
 (inherits: ABC)


- `collect(self) -> Dict[str, Any]`
- `collect_with_cache(self, force_refresh: bool) -> CollectorResult`


### `BrainMetricsCollector`
 (inherits: BaseDataCollector)


- `collect(self) -> Dict[str, Any]`


### `WorkspaceHealthCollector`
 (inherits: BaseDataCollector)


- `collect(self) -> Dict[str, Any]`


### `PerformanceCollector`
 (inherits: BaseDataCollector)


- `collect(self) -> Dict[str, Any]`


### `TokenUsageCollector`
 (inherits: BaseDataCollector)


- `collect(self) -> Dict[str, Any]`


### `ConversationQualityCollector`
 (inherits: BaseDataCollector)


- `collect(self) -> Dict[str, Any]`


### `DataCollectionCoordinator`


- `collect_all(self, force_refresh: bool) -> Dict[str, CollectorResult]`
- `collect_for_template(self, template_name: str, force_refresh: bool) -> Dict[str, Any]`
- `get_health_summary(self) -> Dict[str, Any]`


- `main()`


## scheduler

### `SchedulerStats`




### `DataCollectionScheduler`


- `tick(self, force_refresh: bool)`
- `run_forever(self, force_refresh: bool)`




## admin_dashboard_launcher_module

### `AdminDashboardLauncherModule`


- `execute(self, context: Dict[str, Any]) -> Dict[str, Any]`


- `execute(context: Dict[str, Any]) -> Dict[str, Any]`


## application_onboarding_steps

### `CopyEntryPointsStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


### `InstallToolingStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


### `InitializeBrainTiersStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


### `CrawlApplicationStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


### `AnalyzeDiscoveriesStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


### `GenerateSmartQuestionsStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


### `PresentOnboardingSummaryStep`
 (inherits: OnboardingStep)


- `validate_prerequisites(self, context: Dict[str, Any]) -> bool`
- `execute(self, context: Dict[str, Any]) -> StepResult`


- `register_application_onboarding_steps(registry: StepRegistry)`


## apply_narrator_voice_module

### `ApplyNarratorVoiceModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`




## brain_initialization_module

### `BrainInitializationModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## brain_tests_module

### `BrainTestsModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## build_story_preview_module

### `BuildStoryPreviewModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`




## clear_python_cache_module

### `ClearPythonCacheModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## context_control_module

### `ContextControlModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, operation_data: Dict[str, Any]) -> OperationResult`
- `can_handle(self, operation_type: str) -> bool`
- `detect_trigger(self, user_request: str) -> bool`




## context_display_module

### `ContextDisplayModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, operation_data: Dict[str, Any]) -> OperationResult`
- `can_handle(self, operation_type: str) -> bool`




## conversation_capture_module

### `ConversationCaptureModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `should_capture(self, user_request: str) -> bool`
- `detect_intent(self, conversation_text: str) -> str`
- `extract_entities(self, conversation_text: str) -> Dict[str, List[str]]`
- `create_conversation_summary(self, conversation_history: List[Dict[str, str]], max_length: int) -> str`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `capture_conversation(user_request: str, conversation_history: List[Dict[str, str]], project_root: Optional[Path]) -> Dict[str, Any]`


## conversation_tracking_module

### `ConversationTrackingModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## dashboard_launcher_module

### `DashboardLauncherModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## deploy_docs_preview_module

### `DeployDocsPreviewModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `get_github_config()`
- `register() -> BaseOperationModule`


## evaluate_cortex_architecture_module

### `EvaluateCortexArchitectureModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> BaseOperationModule`


## generate_cleanup_report_module

### `GenerateCleanupReportModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## generate_image_prompts_module

### `GenerateImagePromptsModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`




## generate_story_chapters_module

### `GenerateStoryChaptersModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> BaseOperationModule`


## git_checkpoint_module

### `CheckpointType`




### `CheckpointViolation`
 (inherits: Exception)




### `GitCheckpointModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `get_module()`


## git_sync_module

### `GitSyncModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## hands_on_tutorial_orchestrator

### `TutorialProfile`
 (inherits: Enum)




### `ModuleStatus`
 (inherits: Enum)




### `TutorialModule`




### `TutorialProgress`




### `HandsOnTutorialOrchestrator`


- `start_tutorial(self, profile: TutorialProfile) -> Dict[str, Any]`
- `next_exercise(self, session_id: str) -> Dict[str, Any]`
- `get_progress(self, session_id: str) -> Dict[str, Any]`


- `main()`


## load_protection_rules_module

### `LoadProtectionRulesModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> BaseOperationModule`


## load_story_template_module

### `LoadStoryTemplateModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`




## platform_detection_module

### `PlatformDetectionModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## project_validation_module

### `ProjectValidationModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## python_dependencies_module

### `PythonDependenciesModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## refresh_design_docs_module

### `RefreshDesignDocsModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> BaseOperationModule`


## relocate_story_files_module

### `RelocateStoryFilesModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate(self, context: Dict[str, Any]) -> OperationResult`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`


- `register() -> BaseOperationModule`


## remove_old_logs_module

### `RemoveOldLogsModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## remove_orphaned_files_module

### `RemoveOrphanedFilesModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## save_story_markdown_module

### `SaveStoryMarkdownModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`




## scan_docstrings_module

### `DocstringInfo`




### `ScanDocstringsModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> BaseOperationModule`


## scan_temporary_files_module

### `ScanTemporaryFilesModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## setup_completion_module

### `SetupCompletionModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## tooling_detection_module

### `ToolingDetector`


- `detect_all(self) -> Dict[str, Dict]`
- `detect_python(self) -> Dict`
- `detect_pip(self) -> Dict`
- `detect_git(self) -> Dict`
- `detect_node(self) -> Dict`
- `detect_npm(self) -> Dict`
- `detect_sqlite(self) -> Dict`
- `detect_package_manager(self) -> Dict`
- `get_missing_required(self) -> list`
- `print_report(self)`


- `execute(context: Dict) -> Dict`


## tooling_installer_module

### `ToolingInstaller`


- `install_python(self) -> Tuple[bool, str]`
- `install_git(self) -> Tuple[bool, str]`
- `install_node(self) -> Tuple[bool, str]`
- `install_sqlite(self) -> Tuple[bool, str]`
- `install_pip_packages(self, requirements_file: Path) -> Tuple[bool, str]`
- `install_missing_tools(self, missing: list) -> Dict`
- `print_install_report(self, results: Dict)`


### `VisionAPIInstaller`


- `install(self, cortex_root: Path) -> Tuple[bool, str]`
- `configure_credentials(self, api_key: str) -> Tuple[bool, str]`


- `get_download_urls()`
- `execute(context: Dict) -> Dict`


## tooling_verification_module

### `ToolingVerificationModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## tutorial_validator

### `TutorialValidator`


- `validate_ado_planning_exercise(self, work_item_id: str) -> Dict[str, Any]`
- `validate_all_exercises(self, session_id: str) -> Dict[str, Any]`
- `generate_validation_report(self, validation_results: Dict[str, Any]) -> str`


- `validate_ado_exercise(cortex_root: Path, work_item_id: str) -> Dict[str, Any]`


## user_onboarding_steps

### `CortexIntroductionStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


### `EnvironmentDetectionStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


### `InstallationValidationStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


### `MemoryDemonstrationStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


### `FirstInteractionStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


### `ConversationTrackingStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


### `OnboardingGraduationStep`
 (inherits: OnboardingStep)


- `execute(self, context: Dict[str, Any]) -> StepResult`


- `register_user_onboarding_steps(registry: StepRegistry)`


## vacuum_sqlite_databases_module

### `VacuumSQLiteDatabasesModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## validate_story_structure_module

### `ValidateStoryStructureModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`
- `get_progress_message(self) -> str`




## virtual_environment_module

### `VirtualEnvironmentModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## vision_api_module

### `VisionAPIModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`
- `should_run(self, context: Dict[str, Any]) -> bool`




## __init__



## code_quality_orchestrator

### `CodeReviewReport`




### `ComplexityReport`




### `QualityScorecard`




### `CodeQualityOrchestrator`


- `run_code_review(self, source_code: str) -> CodeReviewReport`
- `analyze_complexity(self, source_code: str) -> ComplexityReport`
- `generate_scorecard(self, source_code: str) -> QualityScorecard`




## code_review_suggester

### `CodeReviewSuggester`


- `check_should_suggest(self, context: Dict[str, Any]) -> bool`
- `format_suggestion_message(self, context: Dict[str, Any]) -> str`
- `parse_user_response(self, response: str) -> str`
- `track_skip_decision(self, context: Dict[str, Any], reason: str) -> bool`
- `get_deployment_reminder(self, context: Dict[str, Any]) -> Optional[str]`
- `get_trigger_rules(self) -> Dict[str, Any]`


- `suggest_code_review(context: Dict[str, Any], brain_path: Optional[Path]) -> Optional[str]`


## deployment_orchestrator

### `EnvironmentConfig`




### `DeploymentResult`




### `DeploymentOrchestrator`


- `execute_deployment(self, config: EnvironmentConfig) -> DeploymentResult`
- `validate_environment(self, config: EnvironmentConfig) -> bool`
- `rollback(self, checkpoint: str) -> DeploymentResult`




## documentation_generation_orchestrator

### `DocstringInfo`




### `APIReference`




### `UsageGuide`




### `DocumentationGenerationOrchestrator`


- `extract_docstrings(self, source_code: str) -> List[DocstringInfo]`
- `generate_api_reference(self, docstrings: List[DocstringInfo], module_name: str) -> APIReference`
- `create_usage_guide(self, module_name: str, examples: List[Dict[str, str]], description: str) -> UsageGuide`




## error_recovery_orchestrator

### `ErrorRecoveryOrchestrator`


- `calculate_backoff(self, attempt: int) -> float`
- `retry_with_backoff(self, operation: Callable, max_attempts: Optional[int], operation_name: Optional[str]) -> Any`
- `record_failure(self, operation_name: str) -> None`
- `record_success(self, operation_name: str) -> None`
- `is_circuit_open(self, operation_name: str) -> bool`
- `execute_with_fallback(self, strategies: List[Callable], operation_name: Optional[str]) -> Any`
- `classify_error(self, error: Exception) -> str`
- `is_retryable(self, error: Exception) -> bool`
- `track_recovery_attempt(self, operation: str, attempt: int, success: bool, error_type: Optional[str]) -> None`
- `get_recovery_stats(self, operation: str) -> Optional[Dict]`
- `get_global_stats(self) -> Dict`
- `reset_circuit(self, operation_name: str) -> None`
- `reset_all_circuits(self) -> None`
- `get_circuit_state(self, operation_name: str) -> str`




## git_checkpoint_utility

### `GitCheckpointUtility`


- `create_phase_checkpoint(self, phase_number: int, total_phases: int, phase_name: str, duration_hours: float, test_coverage: float, files_changed: int, deliverables: List[str], dor_met: bool, dod_met: bool, tests_passed: int, tests_total: int) -> Dict[str, Any]`
- `rollback_to_phase(self, phase_number: int) -> Dict[str, Any]`
- `list_phase_checkpoints(self) -> List[Dict[str, Any]]`




## holistic_review_orchestrator

### `QualityGate`




### `ReviewResult`


- `failed_gates(self) -> List[QualityGate]`


### `HolisticReviewOrchestrator`


- `evaluate_code_quality(self, context: Dict[str, Any]) -> QualityGate`
- `evaluate_test_coverage(self, context: Dict[str, Any]) -> QualityGate`
- `evaluate_documentation(self, context: Dict[str, Any]) -> QualityGate`
- `run_holistic_review(self, context: Dict[str, Any]) -> ReviewResult`
- `document_lessons_learned(self, result: ReviewResult) -> Dict[str, Any]`
- `document_lessons_learned_from_gates(self, gates: List[QualityGate], context: Dict[str, Any]) -> Dict[str, Any]`
- `extract_patterns(self, context: Dict[str, Any]) -> List[str]`




## image_context_middleware

### `ImageContextMiddleware`


- `detect_images_in_context(self, user_message: str, attachments: Optional[List[Dict]], context: Optional[Dict]) -> Dict[str, Any]`
- `infer_analysis_context(self, user_message: str) -> str`
- `process_context(self, user_message: str, attachments: Optional[List[Dict]], context: Optional[Dict], force_engage: bool) -> Dict[str, Any]`
- `get_metrics(self) -> Dict[str, Any]`


- `get_middleware(config: Optional[Dict]) -> ImageContextMiddleware`


## integration_testing_orchestrator

### `TestEnvironment`




### `TestResult`




### `IntegrationTestingOrchestrator`


- `setup_environment(self, name: str) -> TestEnvironment`
- `execute_tests(self, env: TestEnvironment, tests: List[str]) -> TestResult`
- `teardown_environment(self, env: TestEnvironment) -> bool`
- `aggregate_results(self, results: List[TestResult]) -> Dict[str, int]`




## knowledge_graph_auto_updater

### `UpdateResult`




### `PatternExtractor`


- `extract_from_context(context: Dict[str, Any]) -> List[Dict[str, Any]]`


### `KnowledgeGraphAutoUpdater`


- `acquire_lock(self) -> bool`
- `release_lock(self) -> bool`
- `create_backup(self) -> Optional[Path]`
- `restore_from_backup(self, backup_path: Path) -> bool`
- `extract_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]`
- `update_knowledge_graph(self, context: Dict[str, Any]) -> UpdateResult`




## orchestration_analytics_dashboard

### `OrchestrationAnalyticsDashboard`


- `aggregate_metrics(self, days: int) -> Dict[str, Any]`
- `compare_orchestrators(self, days: int, sort_by: str) -> List[Dict[str, Any]]`
- `generate_performance_trend(self, days: int, orchestrator_filter: Optional[str]) -> Dict[str, Any]`
- `generate_duration_chart(self, trend_data: Dict[str, Any]) -> Optional[Path]`
- `calculate_success_metrics(self, days: int) -> Dict[str, Any]`
- `generate_success_pie_chart(self, success_metrics: Dict[str, Any]) -> Optional[Path]`
- `calculate_success_metrics_by_orchestrator(self, days: int) -> List[Dict[str, Any]]`
- `generate_html_report(self, days: int) -> Path`
- `create_flask_app(self)`
- `start_server(self, host: str, port: Optional[int])`




## orchestration_checkpoint_manager

### `CheckpointNotFoundError`
 (inherits: Exception)




### `CheckpointCorruptedError`
 (inherits: Exception)




### `OrchestrationCheckpointManager`


- `save_checkpoint(self, orchestrator_name: str, state: Dict[str, Any], phase: Optional[str]) -> str`
- `restore_checkpoint(self, orchestrator_name: str, checkpoint_id: str) -> Dict[str, Any]`
- `rollback(self, orchestrator_name: str, checkpoint_id: str) -> Dict[str, Any]`
- `list_checkpoints(self, orchestrator_name: str) -> List[Dict[str, Any]]`
- `cleanup_old_checkpoints(self, retention_days: int) -> int`
- `get_latest_checkpoint(self, orchestrator_name: str) -> Optional[str]`
- `delete_checkpoint(self, orchestrator_name: str, checkpoint_id: str) -> bool`




## orchestration_metrics_collector

### `OrchestrationMetricsCollector`


- `log_engagement_start(self, orchestrator_name: str, operation_type: str, event_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> str`
- `log_engagement_complete(self, event_id: str, status: str, result_summary: Optional[str], error_message: Optional[str], duration_ms: Optional[float], metadata: Optional[Dict[str, Any]]) -> bool`
- `generate_report(self, days: int) -> Dict[str, Any]`
- `apply_retention_policy(self, days: int) -> int`


- `with_orchestration_metrics(orchestrator_name: str)`


## parallel_orchestration_coordinator

### `DependencyError`
 (inherits: Exception)




### `ResourceLockError`
 (inherits: Exception)




### `PhaseDefinition`




### `ParallelOrchestrationCoordinator`


- `execute_parallel_phases(self, phases: List[PhaseDefinition], max_concurrent: Optional[int]) -> Dict[str, Any]`
- `acquire_resource_lock(self, resource: str)`




## path_translator

### `PathTranslator`


- `is_windows_absolute(path: str) -> bool`
- `is_unix_absolute(path: str) -> bool`
- `is_unc_path(path: str) -> bool`
- `translate(path: str, target_os: str) -> str`




## performance_profiling_orchestrator

### `ProfileResult`




### `BottleneckReport`




### `RegressionReport`




### `PerformanceProfilingOrchestrator`


- `profile_execution(self, func: Callable, args: Tuple, kwargs: Optional[Dict], runs: int) -> ProfileResult`
- `generate_profile_data(self, result: ProfileResult) -> Dict[str, Dict[str, Any]]`
- `identify_bottlenecks(self, profile_data: Dict[str, Dict[str, Any]], threshold: float) -> BottleneckReport`
- `detect_regression(self, baseline: Dict[str, float], current: Dict[str, float], threshold: float) -> RegressionReport`




## progress_renderer

### `ProgressRenderer`


- `render_task_progress(self, current: int, total: int, phase_name: str, current_phase: int, total_phases: int, task_name: str, elapsed_time: str, bar_width: Optional[int]) -> str`
- `render_phase_transition(self, from_phase: str, to_phase: str, completed_tasks: int, duration: str, checkpoint_created: bool, checkpoint_name: str) -> str`
- `render_checkpoint_status(self, success: bool, checkpoint_name: str, error_message: str) -> str`
- `render_completion_summary(self, total_phases: int, total_tasks: int, total_duration: str, checkpoints_created: int) -> str`


- `format_elapsed_time(seconds: float) -> str`


## progress_synchronizer

### `PhaseStatus`
 (inherits: str, Enum)




### `PhaseInfo`




### `ProgressTrackerInfo`




### `MarkdownParser`


- `load(self) -> bool`
- `extract_progress_tracker(self) -> Optional[ProgressTrackerInfo]`


### `ASCIIArtGenerator`


- `generate_progress_bar(percent: int, width: int) -> str`
- `generate_overall_progress_bar(percent: int, width: int) -> str`
- `format_status_emoji(status: PhaseStatus) -> str`


### `TrackerUpdateEngine`


- `update_phase_status(self, phase_number: int, new_status: PhaseStatus, start_date: Optional[datetime], completion_date: Optional[datetime]) -> bool`
- `get_next_phase(self) -> Optional[PhaseInfo]`


### `PhaseSummaryBuilder`


- `build_summary(phase: PhaseInfo, metrics: Optional[Dict]) -> str`


### `ProgressSynchronizer`


- `load(self) -> bool`
- `update_phase(self, phase_number: int, status: PhaseStatus, start_date: Optional[datetime], completion_date: Optional[datetime], metrics: Optional[Dict]) -> bool`
- `get_current_status(self) -> Optional[ProgressTrackerInfo]`
- `get_next_phase(self) -> Optional[PhaseInfo]`


- `update_master_plan_phase(phase_number: int, status: PhaseStatus, master_plan_path: Optional[Path], metrics: Optional[Dict]) -> bool`
- `update_sub_plan_phase(sub_plan_path: Path, phase_number: int, status: PhaseStatus, metrics: Optional[Dict]) -> bool`


## regeneration_tracker

### `RegenerationTracker`


- `compute_file_hash(self, file_path: Path) -> str`
- `compute_combined_hash(self, file_paths: List[Path]) -> str`
- `should_regenerate(self, output_file: str, source_dependencies: List[str], category: str) -> Tuple[bool, str]`
- `mark_regenerated(self, output_file: str, source_dependencies: List[str], category: str, additional_metadata: Optional[Dict])`
- `mark_full_regeneration(self)`
- `finalize(self) -> Dict`
- `get_statistics(self) -> Dict`
- `clear_manifest(self)`
- `get_tracked_files(self, category: Optional[str]) -> List[str]`
- `print_summary(self)`




## resource_management_orchestrator

### `ResourceManagementOrchestrator`


- `get_cpu_usage(self) -> float`
- `record_cpu_usage(self)`
- `get_cpu_history(self, limit: Optional[int]) -> List[Dict[str, Any]]`
- `check_cpu_threshold(self) -> Optional[Dict[str, Any]]`
- `get_memory_usage(self) -> Dict[str, Any]`
- `detect_memory_leak(self, readings: List[Dict[str, Any]]) -> bool`
- `check_memory_threshold(self) -> Optional[Dict[str, Any]]`
- `get_disk_usage(self, path: str) -> Dict[str, Any]`
- `get_disk_usage_multiple(self, paths: List[str]) -> Dict[str, Dict[str, Any]]`
- `check_disk_threshold(self, path: str) -> Optional[Dict[str, Any]]`
- `allocate_resources(self, orchestrator_name: str, cpu_weight: Optional[float], memory_weight: Optional[float], priority: str) -> Dict[str, Any]`
- `deallocate_resources(self, orchestrator_name: str) -> bool`
- `get_active_allocations(self) -> Dict[str, Dict[str, Any]]`
- `analyze_bottlenecks(self) -> List[Dict[str, Any]]`
- `generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
- `should_auto_scale(self, load_history: List[Dict[str, Any]]) -> bool`
- `start_monitoring_session(self, orchestrator_name: str, interval: float) -> str`
- `stop_monitoring_session(self, session_id: str) -> Optional[Dict[str, Any]]`
- `get_resource_summary(self) -> Dict[str, Any]`
- `create_alert(self, resource: str, current_value: float, threshold: float, severity: str) -> Dict[str, Any]`
- `get_alert_history(self) -> List[Dict[str, Any]]`
- `get_active_alerts(self) -> List[Dict[str, Any]]`
- `clear_alert(self, alert_id: str) -> bool`
- `configure_thresholds(self, cpu_threshold: Optional[float], memory_threshold: Optional[float], disk_threshold: Optional[float])`
- `configure_monitoring(self, interval: float, enabled: bool)`
- `export_configuration(self) -> Dict[str, Any]`




## shell_adapter

### `ShellAdapter`


- `adapt_command(command: str, target_shell: str) -> str`
- `format_env_var(var_name: str, shell: str) -> str`
- `get_line_continuation(shell: str) -> str`
- `get_path_separator(shell: str) -> str`




## task_injection_manager

### `TaskPriority`
 (inherits: Enum)




### `TaskStatus`
 (inherits: Enum)




### `TaskInjectionManager`


- `inject_task(self, description: str, priority: str, metadata: Optional[Dict[str, Any]]) -> str`
- `get_next_task(self) -> Optional[Dict[str, Any]]`
- `mark_complete(self, task_id: str, result: Optional[str], metadata: Optional[Dict[str, Any]]) -> bool`
- `get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]`
- `get_all_tasks(self) -> List[Dict[str, Any]]`
- `render_task_list_for_progress(self, renderer: Any) -> str`
- `handle_keyboard_injection(self) -> Optional[str]`




## vision_context_middleware

### `VisionContextMiddleware`


- `detect_images_in_context(self, context: Dict[str, Any]) -> List[Dict[str, Any]]`
- `process_context(self, context: Dict[str, Any]) -> Dict[str, Any]`


### `GPT4VisionClient`


- `analyze_image(self, image_path: str) -> Dict[str, Any]`


- `with_vision_context_middleware(func: Callable) -> Callable`


## __init__



## sync_visualizer

### `SyncVisualizer`


- `track_file_change(self, file_path: str, change_type: str, size_bytes: int, status: str) -> None`
- `track_operation(self, operation_name: str, status: str, duration_ms: float, message: str) -> None`
- `track_conflict(self, file_path: str, conflict_type: str, resolution: Optional[str]) -> None`
- `generate_network_diagram_data(self) -> Dict[str, Any]`
- `generate_file_flow_data(self) -> Dict[str, Any]`
- `generate_operations_timeline(self) -> List[Dict[str, Any]]`
- `generate_conflicts_summary(self) -> Dict[str, Any]`
- `generate_websocket_message(self, event_type: str) -> Dict[str, Any]`
- `generate_html_dashboard(self, output_path: Path) -> str`




## copyright_updater

### `BulkCopyrightUpdater`


- `execute(self, file_pattern: str) -> Dict[str, Any]`
- `scan_missing_headers(self, file_pattern: str) -> List[Path]`


### `PlanningDocumentRealigner`


- `realign_all(self) -> Dict[str, Any]`


- `main()`


## __init__



## code_analyzer

### `CodeAnalyzer`


- `scan_file_structure(self) -> Dict[str, Any]`
- `extract_domain_terminology(self) -> Dict[str, Any]`
- `extract_namespaces(self) -> Dict[str, List[str]]`
- `detect_sensitive_data(self) -> Dict[str, Any]`
- `generate_dependency_graph(self) -> Dict[str, List[str]]`




## mapping_engine

### `MappingEngine`


- `generate_mappings(self, domain_terms: Dict[str, Any], namespaces: Dict[str, List[str]]) -> Dict[str, str]`
- `detect_conflicts(self, mappings: Dict[str, str]) -> List[Dict[str, Any]]`
- `resolve_conflicts(self, mappings: Dict[str, str], conflicts: List[Dict[str, Any]]) -> Dict[str, str]`
- `generate_preview(self, mappings: Dict[str, str]) -> Dict[str, str]`




## report_generator

### `ReportGenerator`


- `generate_audit_report(self, results: Dict[str, Any]) -> str`
- `generate_mapping_reference(self, mappings: Dict[str, str]) -> str`




## transformer

### `CodeTransformer`


- `transform_codebase(self, source_directory: str, output_directory: str, mappings: Dict[str, str]) -> Dict[str, Any]`




## validator

### `BuildValidator`


- `detect_build_system(self, directory: str) -> str`
- `execute_build(self, directory: str, build_system: str) -> Dict[str, Any]`
- `run_tests(self, directory: str, build_system: str) -> Dict[str, Any]`




## __init__



## alignment_models

### `IntegrationScore`


- `score(self) -> int`
- `status(self) -> str`
- `issues(self) -> List[str]`


### `RemediationSuggestion`




### `AlignmentReport`


- `is_healthy(self) -> bool`
- `has_warnings(self) -> bool`
- `has_errors(self) -> bool`
- `issues_found(self) -> int`




## alignment_state

### `FileChecksum`


- `from_file(cls, file_path: Path) -> 'FileChecksum'`


### `FeatureScore`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'FeatureScore'`


### `ChangesSummary`


- `has_changes(self) -> bool`
- `to_dict(self) -> Dict[str, Any]`


### `PerformanceMetrics`


- `to_dict(self) -> Dict[str, Any]`


### `AlignmentState`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'AlignmentState'`
- `should_run_full_scan(self) -> bool`
- `is_stale(self, hours: int) -> bool`
- `add_to_history(self, health: int, total_features: int, critical_issues: int, warnings: int) -> None`


### `AlignmentStateManager`


- `load(self) -> Optional[AlignmentState]`
- `save(self, state: AlignmentState) -> bool`
- `backup(self) -> bool`
- `detect_context_type(self, project_root: Path) -> str`
- `compute_file_checksums(self, file_paths: List[Path]) -> Dict[str, Dict[str, Any]]`
- `detect_file_changes(self, current_checksums: Dict[str, Dict[str, Any]], previous_state: AlignmentState) -> ChangesSummary`
- `map_files_to_features(self, file_paths: List[str], feature_scores: Dict[str, Dict[str, Any]]) -> Set[str]`




## alignment_validators

### `FullValidationRunner`


- `run(self, monitor: Optional[ProgressMonitor]) -> AlignmentReport`




## align_utility

### `ValidationResult`




### `AlignmentReport`


- `passed_count(self) -> int`
- `total_count(self) -> int`
- `is_healthy(self) -> bool`
- `status_text(self) -> str`
- `format_console(self) -> str`


### `AlignUtility`


- `validate_prompt_sync(self) -> ValidationResult`
- `validate_brain_structure(self) -> ValidationResult`
- `validate_protection_rules(self) -> ValidationResult`
- `validate_response_templates(self) -> ValidationResult`
- `validate_database(self, db_name: str, tier: int, friendly_name: str) -> ValidationResult`
- `validate_core_modules(self) -> ValidationResult`
- `validate_configuration(self) -> ValidationResult`
- `validate_feature_discovery(self) -> ValidationResult`
- `validate_code_quality(self) -> ValidationResult`
- `validate_feature_wiring(self) -> ValidationResult`
- `scan_directory(self, directory_path: str, pattern: str, exclude: List[str]) -> List[Path]`
- `scan_yaml(self, yaml_path: str) -> Dict[str, Any]`
- `discover_python_modules(self) -> Tuple[List[Path], List[Path]]`
- `discover_all_features(self) -> Dict[str, Any]`
- `check_wiring_in_templates(self, module_name: str) -> bool`
- `check_plugin_registration(self, plugin_name: str) -> bool`
- `check_operation_module_linkage(self, module_name: str) -> bool`
- `check_workflow_triggers(self, workflow_name: str) -> bool`
- `check_dashboard_accessibility(self, dashboard_name: str) -> bool`
- `validate_manifest_compliance(self) -> ValidationResult`
- `check_script_operation_linkage(self, script_name: str) -> bool`
- `compute_file_checksums(self, file_paths: List[Path]) -> Dict[str, Dict[str, Any]]`
- `detect_changes(self, previous_state: Optional[AlignmentState]) -> ChangesSummary`
- `run_alignment(self) -> AlignmentReport`


- `safe_print(message: str) -> None`
- `run_align_utility(force_full: bool, quick_mode: bool) -> Dict[str, Any]`


## documentation_governance_validator

### `DocumentationGovernanceValidator`


- `validate(self) -> Dict[str, Any]`




## gap_remediation_validator

### `GapRemediationValidator`


- `validate(self, report: AlignmentReport) -> None`




## governance_tokens

### `GovernanceFile`


- `is_compliant(self) -> bool`
- `overage_tokens(self) -> int`
- `overage_percent(self) -> float`
- `reduction_needed(self) -> float`


### `TokenValidationReport`


- `total_current_tokens(self) -> int`
- `total_budget_tokens(self) -> int`
- `total_overage_tokens(self) -> int`
- `is_compliant(self) -> bool`
- `compliant_count(self) -> int`
- `total_count(self) -> int`
- `format_console(self) -> str`


### `GovernanceTokenValidator`


- `estimate_tokens(self, text: str) -> int`
- `count_lines(self, text: str) -> int`
- `validate_file(self, name: str, config: Dict[str, Any]) -> GovernanceFile`
- `validate_all(self) -> TokenValidationReport`


- `safe_print(message: str) -> None`
- `validate_token_budgets(silent: bool) -> Dict[str, Any]`
- `main()`


## healthcheck_utility

### `HealthCheckResult`




### `HealthReport`


- `passed_count(self) -> int`
- `total_count(self) -> int`
- `is_healthy(self) -> bool`
- `status_text(self) -> str`
- `format_console(self) -> str`


### `HealthCheckUtility`


- `validate_system_resources(self) -> HealthCheckResult`
- `validate_brain_structure(self) -> HealthCheckResult`
- `validate_database(self, db_name: str, tier: int, display_name: str) -> HealthCheckResult`
- `validate_protection_rules(self) -> HealthCheckResult`
- `validate_response_templates(self) -> HealthCheckResult`
- `validate_core_modules(self) -> HealthCheckResult`
- `validate_configuration(self) -> HealthCheckResult`
- `run_healthcheck(self) -> HealthReport`


- `safe_print(message: str) -> None`
- `run_healthcheck_utility() -> Dict[str, Any]`


## remediation_suggestions_generator

### `RemediationSuggestionsGenerator`


- `generate(self, report: AlignmentReport, orchestrators: Dict[str, Dict[str, Any]], agents: Dict[str, Dict[str, Any]]) -> None`




## ado_utility

### `WorkItemType`
 (inherits: Enum)




### `WorkItemStatus`
 (inherits: Enum)




### `WorkItemMetadata`




### `WorkItemSummary`




### `ValidationResult`




### `WorkItemResult`




- `create_work_item(work_item_type: WorkItemType, title: str, description: str, **kwargs) -> WorkItemResult`
- `load_work_item(work_item_id: str) -> WorkItemResult`
- `update_work_item(work_item_id: str, **updates) -> WorkItemResult`
- `generate_summary(work_item_id: str, **summary_data) -> WorkItemResult`
- `validate_dor(metadata: WorkItemMetadata, ambiguity_score: int) -> ValidationResult`
- `validate_dod(summary: WorkItemSummary) -> ValidationResult`
- `list_work_items(status: Optional[WorkItemStatus]) -> WorkItemResult`


## analysis_utility

### `IssueSeverity`
 (inherits: Enum)




### `IssueCategory`
 (inherits: Enum)




### `CodeIssue`




### `AnalysisResult`


- `critical_count(self) -> int`
- `high_count(self) -> int`
- `medium_count(self) -> int`
- `low_count(self) -> int`
- `total_count(self) -> int`


- `analyze_file(file_path: Path, analyzers: Optional[List[str]]) -> AnalysisResult`
- `get_breaking_changes(file_path: Path) -> List[CodeIssue]`
- `check_security(file_path: Path) -> List[CodeIssue]`
- `check_performance(file_path: Path) -> List[CodeIssue]`
- `check_code_quality(file_path: Path) -> List[CodeIssue]`
- `generate_analysis_report(results: List[AnalysisResult], output_path: Path) -> bool`


## architecture_debt_analyzer

### `ArchitectureViolation`




### `ArchitectureDebtAnalyzer`


- `analyze(self) -> Dict[str, Any]`




## ast_engine

### `ASTEngine`


- `find_semantic_duplicates(self, similarity_threshold: float, min_lines: int) -> List[Dict[str, Any]]`
- `find_orphaned_tests(self, test_patterns: List[str]) -> List[Path]`
- `analyze_test_gaps(self, target_file: Path) -> Dict[str, Any]`
- `find_unused_imports(self, target_files: List[Path]) -> List[Dict[str, Any]]`
- `detect_dead_code(self, target_paths: List[Path]) -> List[Dict[str, Any]]`
- `get_architecture_insights(self) -> Dict[str, Any]`
- `is_available(self) -> bool`




## code_smell_analyzer

### `CodeSmell`




### `CodeSmellAnalyzer`


- `analyze(self, target_path: Path) -> Dict[str, Any]`




## deduplication_analyzer

### `DuplicateGroup`




### `DeduplicationAnalyzer`


- `analyze(self, target_path: Path) -> Dict[str, Any]`




## __init__



## review_orchestrator

### `ReviewFinding`




### `ReviewSection`




### `ReviewOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## __init__



## brain_performance_integration

### `BrainPerformanceSnapshot`




### `IntegratedBrainPerformanceSystem`


- `start_monitoring(self)`
- `stop_monitoring(self)`
- `execute_optimized_query(self, query: str, tier: str, execute_func, *args, **kwargs) -> Any`
- `allocate_optimized_memory(self, zone: MemoryZone, size_bytes: int, description: str) -> Optional[str]`
- `get_unified_performance_snapshot(self) -> BrainPerformanceSnapshot`
- `trigger_comprehensive_optimization(self) -> Dict[str, Any]`
- `get_performance_trends(self, hours: int) -> Dict[str, Any]`


- `create_optimized_brain_system(brain_path: str, config: Dict[str, Any]) -> IntegratedBrainPerformanceSystem`


## brain_tuning_orchestrator

### `BrainTuningOrchestrator`


- `execute(self) -> Dict[str, Any]`




## memory_manager

### `MemoryZone`
 (inherits: Enum)




### `MemoryPressure`
 (inherits: Enum)




### `MemoryAllocation`




### `MemoryMetrics`




### `MemoryPool`


- `allocate(self, size_bytes: int, description: str) -> Optional[str]`
- `deallocate(self, allocation_id: str) -> bool`
- `cleanup_inactive_allocations(self) -> int`
- `get_utilization(self) -> float`
- `get_fragmentation_level(self) -> float`


### `BrainMemoryManager`


- `start_monitoring(self)`
- `stop_monitoring(self)`
- `allocate_memory(self, zone: MemoryZone, size_bytes: int, description: str) -> Optional[str]`
- `deallocate_memory(self, allocation_id: str) -> bool`
- `get_memory_pressure(self) -> MemoryPressure`
- `get_memory_metrics(self) -> MemoryMetrics`
- `optimize_memory_usage(self) -> Dict[str, Any]`
- `emergency_cleanup(self) -> Dict[str, Any]`
- `get_memory_summary(self) -> Dict[str, Any]`




## optimization_engine

### `PerformanceMetric`
 (inherits: NamedTuple)




### `OptimizationResult`




### `TierPerformanceMonitor`


- `record_operation(self, operation: str, duration_ms: float, query_size: int, result_count: int)`
- `get_average_performance(self, window_size: int) -> float`
- `get_performance_trend(self) -> str`
- `needs_optimization(self) -> bool`


### `BrainOptimizationEngine`


- `start_optimization_monitoring(self)`
- `stop_optimization_monitoring(self)`
- `record_tier_operation(self, tier: str, operation: str, duration_ms: float, query_size: int, result_count: int)`
- `optimize_tier_performance(self, tier: str) -> OptimizationResult`
- `get_performance_summary(self) -> Dict[str, Any]`
- `run_comprehensive_optimization(self) -> Dict[str, OptimizationResult]`




## query_cache

### `CacheStrategy`
 (inherits: Enum)




### `QueryType`
 (inherits: Enum)




### `CacheEntry`




### `CacheMetrics`




### `QueryCacheEngine`


- `get(self, query: str, query_type: QueryType) -> Optional[Any]`
- `put(self, query: str, result: Any, query_type: QueryType, execution_time_ms: float) -> bool`
- `invalidate(self, query: str, query_type: QueryType) -> int`
- `cleanup_expired(self) -> int`
- `get_metrics(self) -> CacheMetrics`
- `get_top_queries(self, limit: int) -> List[Tuple[str, int]]`
- `optimize_cache(self) -> Dict[str, Any]`


### `SmartQueryCache`


- `cached_query(self, query: str, execute_func, *args, **kwargs) -> Any`
- `get_cache_stats(self) -> Dict[str, Any]`




## backup_archiver

### `BackupArchiver`


- `archive_to_github(self, backup_files: List[Path]) -> Dict[str, Any]`




## cleanup_models

### `CleanupMetrics`


- `space_freed_mb(self) -> float`
- `space_freed_gb(self) -> float`
- `to_dict(self) -> Dict[str, Any]`




## cleanup_orchestrator

### `CleanupOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `check_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]`
- `execute_enhanced(self, context: Dict[str, Any]) -> OperationResult`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## cleanup_test_harness

### `TestBaseline`


- `to_dict(self) -> Dict`
- `from_dict(cls, data: Dict) -> 'TestBaseline'`


### `ValidationResult`


- `has_failures(self) -> bool`


### `CleanupTestHarness`


- `capture_baseline(self) -> TestBaseline`
- `validate_category(self, category_name: str) -> ValidationResult`
- `backup_files(self, file_paths: List[Path]) -> Path`
- `rollback_category(self, backup_path: Path) -> bool`
- `generate_validation_report(self) -> str`




## cleanup_utility

- `get_cleanup_strategy(profile: str) -> Dict[str, Any]`
- `detect_quick_files(brain_path: Path) -> List[Path]`
- `detect_standard_files(brain_path: Path, cutoff_days: int) -> List[Path]`
- `detect_comprehensive_files(brain_path: Path, cutoff_days: int) -> List[Path]`
- `execute_cleanup(files: List[Path], dry_run: bool) -> Dict[str, Any]`


## cleanup_validator

### `ValidationError`




### `ValidationResult`


- `critical_errors(self) -> List[ValidationError]`
- `has_critical_errors(self) -> bool`


### `CleanupValidator`


- `validate_proposed_cleanup(self, manifest: Dict[str, Any]) -> ValidationResult`




## cleanup_verifier

### `VerificationResult`




### `CleanupVerifier`


- `verify_cleanup(self, use_health_validator: bool) -> VerificationResult`




## critical_file_detector

### `ImportInfo`




### `CriticalFileDetector`


- `detect_critical_files(self) -> Set[Path]`
- `trace_imports(self, file_path: Path, visited: Set[Path]) -> Set[Path]`
- `is_critical(self, file_path: Path, critical_files: Set[Path]) -> bool`
- `find_importers(self, file_path: Path) -> List[ImportInfo]`




## doc_archive_cleaner

### `DocumentArchiveCleaner`


- `cleanup(self, dry_run: bool) -> None`




## file_reorganization_engine

### `ReorganizationRule`




### `FileMove`


- `to_dict(self) -> Dict[str, Any]`


### `FileReorganizationEngine`


- `add_rule(self, rule: ReorganizationRule) -> None`
- `analyze_reorganization(self, files: Dict[str, FileMetadata]) -> Dict[str, str]`
- `execute_reorganization(self, reorganization_plan: Dict[str, str], dry_run: bool) -> Dict[str, Any]`
- `generate_move_manifest(self, output_path: Optional[Path]) -> Path`
- `get_statistics(self) -> Dict[str, Any]`




## file_scanner

### `FileCategory`
 (inherits: Enum)




### `FilePurpose`
 (inherits: Enum)




### `FileMetadata`


- `to_dict(self) -> Dict[str, Any]`


### `FileScanner`


- `scan(self, path: Optional[Path]) -> Dict[str, FileMetadata]`
- `get_files_by_category(self, category: FileCategory) -> List[FileMetadata]`
- `get_files_by_purpose(self, purpose: FilePurpose) -> List[FileMetadata]`
- `get_statistics(self) -> Dict[str, Any]`




## git_recovery_manifest

### `GitRecoveryManifest`


- `create_deletion_manifest(self, files_to_delete: List[Path], operation_type: str, dry_run: bool) -> Path`
- `create_reorganization_manifest(self, file_moves: List[Tuple[Path, Path]], dry_run: bool) -> Path`
- `load_manifest(self, manifest_path: Path) -> Dict[str, Any]`
- `recover_from_manifest(self, manifest_path: Path, file_paths: Optional[List[str]], dry_run: bool) -> Dict[str, Any]`




## holistic_cleanup_orchestrator

### `FileInfo`




### `CleanupManifest`


- `to_dict(self) -> Dict[str, Any]`


### `FileCategorizationEngine`


- `categorize_file(self, file_path: Path) -> FileInfo`


### `ProductionReadinessValidator`


- `validate_file(self, file_path: Path) -> FileInfo`


### `HolisticRepositoryScanner`


- `scan_repository(self) -> Dict[str, Any]`


### `CleanupManifestGenerator`


- `generate_manifest(self, scan_results: Dict[str, Any]) -> CleanupManifest`


### `HolisticCleanupOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `execute_markdown_consolidation(self, documents_root: Optional[Path], dry_run: bool) -> OperationResult`




## legacy_kds_cleaner

### `LegacyKDSCleaner`


- `cleanup(self, dry_run: bool) -> int`




## markdown_consolidation_engine

### `MarkdownFile`


- `to_dict(self) -> Dict`


### `ConsolidationRule`


- `to_dict(self) -> Dict`


### `ConsolidationReport`


- `to_dict(self) -> Dict`


### `MarkdownConsolidationEngine`


- `discover_files(self) -> Dict[str, MarkdownFile]`
- `analyze_consolidation_opportunities(self) -> List[ConsolidationRule]`
- `execute_consolidation(self, rules: Optional[List[ConsolidationRule]], dry_run: bool) -> ConsolidationReport`
- `cleanup_old_archives(self) -> int`




## reference_checker

### `ReferenceChecker`


- `scan_references(self, old_path: str) -> List[Tuple[Path, int, str, str]]`
- `update_references(self, old_path: str, new_path: str, references: List[Tuple[Path, int, str, str]], dry_run: bool) -> Dict[str, int]`
- `generate_reference_report(self, old_path: str, references: List[Tuple[Path, int, str, str]]) -> str`




## reference_tracker

### `FileReference`




### `ReferenceTracker`


- `scan(self, files: Dict[str, Any]) -> List[FileReference]`
- `get_dependents(self, file_path: str) -> Set[str]`
- `get_dependencies(self, file_path: str) -> Set[str]`
- `get_update_instructions(self, old_path: str, new_path: str) -> List[Dict[str, Any]]`
- `get_statistics(self) -> Dict[str, Any]`




## remove_obsolete_tests_module

### `RemoveObsoleteTestsModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict) -> OperationResult`




## report_consolidation_engine

### `ReportConsolidationEngine`


- `discover_reports(self) -> Dict[str, List[Path]]`
- `analyze_consolidation_opportunities(self, report_groups: Dict[str, List[Path]], keep_count: int) -> Dict[str, Dict]`
- `execute_consolidation(self, recommendations: Dict[str, Dict], dry_run: bool) -> Dict[str, int]`
- `generate_consolidation_summary(self, report_groups: Dict[str, List[Path]], recommendations: Dict[str, Dict]) -> str`




## smart_deletion_engine

### `DeletionReason`
 (inherits: Enum)




### `DeletionRisk`
 (inherits: Enum)




### `DeletionCandidate`


- `to_dict(self) -> Dict[str, Any]`


### `SmartDeletionEngine`


- `analyze(self, files: Dict[str, FileMetadata], dependency_graph: Dict[str, Set[str]]) -> List[DeletionCandidate]`
- `generate_manifest(self, output_path: Optional[Path]) -> Path`
- `execute_deletions(self, dry_run: bool, risk_filter: Optional[Set[DeletionRisk]]) -> Dict[str, Any]`
- `get_candidates_by_risk(self, risk: DeletionRisk) -> List[DeletionCandidate]`
- `get_candidates_by_reason(self, reason: DeletionReason) -> List[DeletionCandidate]`
- `get_statistics(self) -> Dict[str, Any]`




## user_cleanup_orchestrator

### `CleanupCategory`




### `UserCleanupReport`


- `to_dict(self) -> Dict`


### `UserCleanupOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `execute(self, context: Dict) -> OperationResult`




## __init__



## execution_mode_detector

### `ExecutionModeDetector`


- `detect(self, user_message: str) -> ExecutionMode`
- `is_autonomous_mode(self, user_message: str) -> bool`
- `is_continuation_mode(self, user_message: str) -> bool`
- `should_auto_progress(self, user_message: str) -> bool`




## direct_import

### `DirectConversationImport`


- `import_from_file_reference(self, user_request: str, project_root: Optional[Path], file_content: Optional[str]) -> Dict[str, Any]`
- `import_from_content(self, content: str, source_description: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]`




## import_handler

### `ConversationImportHandler`


- `import_conversation(self, file_path: Optional[str], auto_detect: bool) -> Dict[str, Any]`




## quality_monitor

### `ConversationTurn`




### `MonitoringSession`




### `QualityMonitor`


- `start_session(self, session_id: Optional[str]) -> str`
- `add_turn(self, user_message: str, assistant_response: str) -> Dict[str, Any]`
- `record_user_response(self, response: str) -> None`
- `end_session(self) -> Optional[MonitoringSession]`
- `get_current_quality(self) -> Optional[QualityScore]`
- `get_session_stats(self) -> Dict[str, Any]`


- `create_monitor(config: Optional[Dict[str, Any]]) -> QualityMonitor`


## smart_auto_detection

### `SmartAutoDetection`


- `start_conversation_monitoring(self, session_id: Optional[str]) -> str`
- `process_conversation_turn(self, user_message: str, assistant_response: str) -> Dict[str, Any]`
- `record_user_feedback(self, feedback: str, session_id: Optional[str]) -> Dict[str, Any]`
- `end_conversation_monitoring(self) -> Optional[Dict[str, Any]]`
- `get_statistics(self) -> Dict[str, Any]`


- `create_smart_auto_detection(config: Optional[Dict[str, Any]]) -> SmartAutoDetection`


## smart_hint_generator

### `SmartHint`




### `SmartHintGenerator`


- `generate_hint(self, quality_score: QualityScore, hint_already_shown: bool) -> SmartHint`
- `generate_dismissal_response(self) -> str`


- `create_hint_generator(config: Optional[Dict[str, Any]]) -> SmartHintGenerator`


## tier2_learning

### `UserResponse`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'UserResponse'`


### `ThresholdRecommendation`




### `Tier2LearningIntegration`


- `record_response(self, session_id: str, response: str, quality_score: int, quality_level: str) -> None`
- `get_acceptance_rate(self, quality_level: Optional[str]) -> float`
- `get_response_stats(self) -> Dict[str, Any]`
- `recommend_threshold_adjustment(self, current_threshold: str) -> Optional[ThresholdRecommendation]`
- `should_adjust_threshold(self, current_threshold: str) -> bool`
- `get_quality_level_preferences(self) -> Dict[str, float]`
- `reset_learning_data(self) -> None`


- `create_tier2_learning(config: Optional[Dict[str, Any]]) -> Tier2LearningIntegration`


## __init__



## repository_discovery_service

### `RepoMetadata`




### `RepositoryDiscoveryService`


- `scan_repositories(self) -> List[RepoMetadata]`
- `validate_repository(self, repo_path: Path) -> bool`
- `register_repositories(self, repositories: List[RepoMetadata]) -> None`
- `remove_missing_repositories(self) -> List[str]`
- `get_repository_count(self) -> int`
- `get_repository_by_id(self, repo_id: str) -> Optional[Dict[str, Any]]`


- `discover_and_register_repositories() -> List[RepoMetadata]`


## __init__



## sqlite_optimizer

### `SQLiteOptimizer`


- `optimize_all(self) -> Dict[str, Any]`
- `optimize_database(self, db_path: Path, tier_name: str) -> Dict[str, Any]`
- `generate_report(self, results: Dict[str, Any], output_path: Optional[Path]) -> str`




## brain_health_monitor

### `HealthStatus`
 (inherits: Enum)




### `HealthTrend`
 (inherits: Enum)




### `HealthPrediction`




### `AutoHealingAction`




### `BrainHealthMonitor`


- `start_health_monitoring(self)`
- `stop_health_monitoring(self)`
- `get_comprehensive_health_assessment(self) -> Dict[str, Any]`


- `create_brain_health_monitor(dashboard: RealTimeMetricsDashboard, brain_system, config: Dict[str, Any]) -> BrainHealthMonitor`
- `get_health_summary(monitor: BrainHealthMonitor) -> Dict[str, Any]`


## data_collection_integration

### `DataCollectionIntegrationSystem`


- `get_system_status(self) -> Dict[str, Any]`
- `get_comprehensive_metrics(self) -> Dict[str, Any]`
- `trigger_optimization(self) -> Dict[str, Any]`
- `shutdown(self) -> Dict[str, Any]`


- `create_data_collection_integration(brain_path: str, workspace_path: str, config: Dict[str, Any]) -> DataCollectionIntegrationSystem`
- `get_integration_summary(system: DataCollectionIntegrationSystem) -> Dict[str, Any]`
- `get_full_metrics(system: DataCollectionIntegrationSystem) -> Dict[str, Any]`


## real_time_metrics_dashboard

### `DashboardStatus`
 (inherits: Enum)




### `MetricSeverity`
 (inherits: Enum)




### `DashboardAlert`




### `UnifiedMetricsSnapshot`




### `RealTimeMetricsDashboard`


- `start_monitoring(self)`
- `stop_monitoring(self)`
- `get_current_dashboard_state(self) -> Dict[str, Any]`
- `get_unified_metrics_snapshot(self) -> Optional[UnifiedMetricsSnapshot]`


- `create_real_time_dashboard(brain_path: str, workspace_path: str, config: Dict[str, Any]) -> RealTimeMetricsDashboard`
- `get_dashboard_summary(dashboard: RealTimeMetricsDashboard) -> Dict[str, Any]`


## ado_planning_demo

### `ADOPlanningDemo`


- `run_demo(self) -> Dict[str, Any]`


- `run_ado_planning_demo(cortex_root: Path) -> Dict[str, Any]`


## demo_orchestrator

### `DemoOrchestrator`


- `handle_discovery(self, user_request: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`


- `handle_discovery_request(user_request: str, brain_path: Optional[Path]) -> Dict[str, Any]`


## __init__



## deploy_utility

- `execute_deployment(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`
- `validate_pre_deployment(cortex_root: Path) -> Dict[str, Any]`
- `sync_architecture_docs(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`
- `bump_version(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`
- `deploy_to_production(cortex_root: Path, dry_run: bool) -> Dict[str, Any]`


## __init__



## design_sync_helpers

### `RecentUpdatesGenerator`


- `generate(self, project_root: Path, lookback_days: int) -> List[str]`


### `CommitReporter`


- `commit_and_report(self, impl_state: ImplementationState, design_state: DesignState, gaps: GapAnalysis, optimizations: Dict[str, Any], transformations: Dict[str, Any], project_root: Path, metrics: SyncMetrics, profile: str) -> Dict[str, Any]`




## design_sync_models

### `ImplementationState`




### `DesignState`




### `GapAnalysis`




### `SyncMetrics`






## design_sync_orchestrator

### `DesignSyncOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`




## implementation_discovery

### `ImplementationDiscovery`


- `discover(self, project_root: Path, metrics: SyncMetrics) -> ImplementationState`




## progress_helpers

### `PhaseProgressCalculator`


- `calculate(self, content: str) -> tuple[Dict[str, int], List[str]]`


### `ProgressBarGenerator`


- `generate(self, percentage: int, width: int) -> str`


### `SyncContextGenerator`


- `generate(self, updates: List[str], impl_state: ImplementationState, transformations: Dict[str, Any]) -> str`




## status_file_consolidator

### `StatusFileConsolidator`


- `consolidate(self, status_files: List[Path], impl_state: ImplementationState, design_state: DesignState, gaps: GapAnalysis, project_root: Path, metrics: SyncMetrics) -> Optional[Path]`




## track_config

### `TrackMetrics`


- `completion_percentage(self) -> float`
- `status_emoji(self) -> str`


### `MachineTrack`




### `MultiTrackConfig`


- `is_multi_track(self) -> bool`
- `get_track_for_machine(self, machine_name: str) -> Optional[MachineTrack]`
- `get_leader(self) -> Optional[MachineTrack]`


### `TrackNameGenerator`


- `generate(machine_name: str, index: int) -> tuple[str, str, str]`


### `PhaseDistributor`


- `distribute(cls, modules: Dict[str, Dict], num_tracks: int, track_names: List[str]) -> Dict[str, List[str]]`


### `TrackConfigManager`


- `load_from_config(config_path: Path) -> MultiTrackConfig`
- `save_to_config(config: MultiTrackConfig, config_path: Path) -> None`
- `create_multi_track_config(machines: List[str], modules: Dict[str, Dict], config_path: Path) -> MultiTrackConfig`




## track_templates

### `TrackDocumentTemplates`


- `generate_race_dashboard(config: MultiTrackConfig) -> str`
- `generate_track_section(track: MachineTrack, modules: Dict[str, Dict]) -> str`
- `generate_split_document(config: MultiTrackConfig, modules: Dict[str, Dict], version: str) -> str`
- `generate_consolidated_document(config: MultiTrackConfig, modules: Dict[str, Dict], version: str) -> str`




## __init__



## diagram_regeneration_orchestrator

### `DiagramStatus`


- `completion_percentage(self) -> int`
- `status(self) -> str`


### `DiagramRegenerationReport`


- `overall_completion(self) -> float`


### `DiagramRegenerationOrchestrator`


- `execute(self) -> DiagramRegenerationReport`




## __init__



## ast_parser

### `ASTParser`
 (inherits: ABC)


- `parse(self, file_path: Path, content: str) -> Optional[ASTNode]`
- `extract_elements(self, ast: ASTNode, file_path: Path) -> List[CodeElement]`
- `calculate_complexity(self, ast: ASTNode) -> ComplexityMetrics`
- `supports_language(self, language: str) -> bool`




## complexity_analyzer

### `ComplexityAnalyzer`


- `calculate_cyclomatic_complexity(self, ast: ASTNode) -> int`
- `calculate_cognitive_complexity(self, ast: ASTNode) -> int`
- `calculate_maintainability_index(self, metrics: Dict[str, Any]) -> float`
- `analyze(self, ast: ASTNode) -> ComplexityMetrics`




## csharp_ast_parser

### `CSharpASTParser`
 (inherits: ASTParser)


- `parse(self, file_path: Path, content: str) -> Optional[ASTNode]`
- `extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]`
- `calculate_complexity(self, ast_node: ASTNode) -> ComplexityMetrics`




## dependency_graph_builder

### `DependencyGraphBuilder`


- `build_graph(self, elements: List[CodeElement]) -> DependencyGraph`
- `find_dependencies(self, element: CodeElement, all_elements: List[CodeElement]) -> List[str]`
- `detect_cycles(self, graph: DependencyGraph) -> List[List[str]]`




## exclusion_engine

### `ExclusionEngine`


- `should_exclude(self, path: Path, relative_path: Path) -> bool`
- `add_pattern(self, pattern: str) -> None`
- `add_patterns(self, patterns: List[str]) -> None`
- `get_patterns(self) -> List[str]`




## file_discovery_engine

### `FileDiscoveryEngine`


- `discover(self, scope: DiscoveryScope) -> FileInventory`




## javascript_ast_parser

### `JavaScriptASTParser`
 (inherits: ASTParser)


- `parse(self, file_path: Path, content: str) -> Optional[ASTNode]`
- `extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]`
- `calculate_complexity(self, ast_node: ASTNode) -> ComplexityMetrics`




## language_detector

### `LanguageDetector`


- `detect(self, file_path: Path) -> str`




## models

### `DiscoveryDepth`
 (inherits: Enum)




### `DiscoveryScope`




### `FileInfo`




### `FileInventory`




### `CodeElement`




### `CodeAnalysisResult`




### `SemanticIndex`




### `GitHistory`




### `DiscoveryReport`




### `ASTNode`




### `ComplexityMetrics`




### `DependencyGraph`






## python_ast_parser

### `PythonASTParser`
 (inherits: ASTParser)


- `parse(self, file_path: Path, content: str) -> Optional[ASTNode]`
- `extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]`
- `calculate_complexity(self, ast_node: ASTNode) -> ComplexityMetrics`




## scope_resolver

### `ScopeResolver`


- `resolve(self, scope_input: str | Path | Dict[str, Any], depth: str) -> DiscoveryScope`
- `validate_scope(self, scope: DiscoveryScope) -> bool`
- `estimate_file_count(self, scope: DiscoveryScope) -> int`




## semantic_index_builder

### `SemanticIndexBuilder`


- `build_index(self, elements: List[CodeElement]) -> dict`
- `index_element(self, element: CodeElement) -> None`
- `update_element(self, element: CodeElement) -> None`
- `remove_element(self, element_id: str) -> None`
- `close(self) -> None`




## semantic_search_engine

### `SearchResult`




### `SemanticSearchEngine`


- `search(self, query: str, limit: int) -> List[SearchResult]`
- `search_by_type(self, query: str, element_type: str, limit: int) -> List[SearchResult]`
- `find_symbol(self, symbol_name: str) -> Optional[SearchResult]`
- `find_references(self, symbol_name: str) -> List[SearchResult]`
- `close(self) -> None`




## snippet_extractor

### `CodeSnippet`




### `SnippetExtractor`


- `extract_snippet(self, element: CodeElement, context_lines: int) -> Optional[CodeSnippet]`
- `highlight_matches(self, snippet: str, query: str) -> str`
- `get_surrounding_context(self, file_path: Path, line_number: int, context_lines: int) -> str`




## __init__



## auto_documentation_generator

### `DocumentationSet`




### `AutoDocumentationGenerator`


- `generate_documentation(self, component_name: str, category: str, context: Dict[str, Any]) -> DocumentationSet`
- `validate_structure(self) -> bool`
- `list_documented_components(self, category: str) -> List[Dict[str, str]]`




## __init__



## auto_registration_orchestrator

### `RegistrationEntry`




### `AutoRegistrationOrchestrator`


- `extract_natural_language_triggers(self, docstring: str, operation_name: str) -> List[str]`
- `infer_deployment_tier(self, module_path: str, docstring: str) -> str`
- `infer_category(self, operation_name: str, module_path: str) -> str`
- `generate_registration_entry(self, discovered_feature: Dict) -> RegistrationEntry`
- `format_yaml_entry(self, entry: RegistrationEntry) -> str`
- `register_features(self, unregistered_features: List[Dict], dry_run: bool, require_approval: bool) -> Dict`


- `main()`


## setup_epm_utility

### `ProjectDetection`


- `to_dict(self) -> Dict[str, Any]`


### `CortexCapabilities`


- `to_dict(self) -> Dict[str, Any]`


### `EPMResult`


- `to_dict(self) -> Dict[str, Any]`


- `detect_language(repo_path: Path) -> str`
- `detect_framework(repo_path: Path, language: str) -> str`
- `detect_build_system(repo_path: Path, language: str) -> str`
- `detect_test_framework(repo_path: Path, language: str) -> str`
- `detect_project_structure(repo_path: Path) -> ProjectDetection`
- `generate_build_command(detection: ProjectDetection) -> str`
- `generate_test_command(detection: ProjectDetection) -> str`
- `review_cortex_enhancements(cortex_root: Optional[Path]) -> Optional[CortexCapabilities]`
- `render_template(detection: ProjectDetection, namespace: str, tier3_enabled: bool, cortex_capabilities: Optional[CortexCapabilities]) -> str`
- `schedule_brain_learning(detection: ProjectDetection, namespace: str, tier3_db_path: Optional[str]) -> bool`
- `handle_existing_file(file_path: Path, detection: ProjectDetection) -> EPMResult`
- `validate_installation(repo_path: Path, cortex_root: Optional[Path]) -> Dict[str, Any]`
- `execute_epm_setup(repo_path: Path, tier3_db_path: Optional[str], cortex_root: Optional[Path], force: bool) -> EPMResult`


## documentation_cli

### `EPMDocumentationCLI`


- `run(self, args: Optional[List[str]]) -> int`


- `main()`


## documentation_generator

### `DocumentationConfig`




### `DocumentSection`




### `DocumentationGenerator`


- `generate_from_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, str]`




## template_engine

### `TemplateConfig`




### `TemplateContext`




### `TemplateEngine`


- `render_template(self, template_name: str, context: Union[TemplateContext, Dict[str, Any]]) -> str`
- `render_string(self, template_string: str, context: Union[TemplateContext, Dict[str, Any]]) -> str`
- `list_templates(self, pattern: Optional[str]) -> List[str]`
- `validate_template(self, template_name: str) -> Dict[str, Any]`
- `create_template(self, template_name: str, content: str, overwrite: bool) -> bool`




## swagger_estimation_utility

### `DoRStatus`
 (inherits: Enum)




### `WorkItemType`
 (inherits: Enum)




### `StoryPointScale`
 (inherits: Enum)




### `DoRQuestion`




### `DoRValidationResult`




### `ADOStory`




### `ADOFeature`




### `WorkDecompositionResult`




- `initialize_dor_questions() -> List[DoRQuestion]`
- `get_next_unanswered_question(questions: List[DoRQuestion]) -> Optional[DoRQuestion]`
- `get_questions_by_category(questions: List[DoRQuestion], category: str) -> List[DoRQuestion]`
- `validate_answer(question: DoRQuestion, answer: str) -> Tuple[bool, List[str]]`
- `submit_dor_answer(questions: List[DoRQuestion], question_id: str, answer: str) -> Tuple[bool, List[str]]`
- `validate_dor(questions: List[DoRQuestion]) -> DoRValidationResult`
- `generate_dor_progress_summary(questions: List[DoRQuestion]) -> str`
- `get_dor_answers_dict(questions: List[DoRQuestion]) -> Dict[str, str]`
- `extract_requirements_from_dor(dor_answers: Dict[str, str]) -> Dict[str, Any]`
- `is_feature_relevant(feature_name: str, requirements: Dict[str, Any]) -> bool`
- `generate_feature_acceptance_criteria(feature_name: str) -> List[str]`
- `calculate_feature_priority(feature_name: str, risk: str) -> int`
- `estimate_story_points(complexity: str) -> int`
- `recommend_team_size(total_story_points: int, target_sprints: int) -> str`
- `generate_ado_export_json(features: List[ADOFeature]) -> str`
- `generate_markdown_summary(features: List[ADOFeature], work_description: str) -> str`
- `decompose_work(work_description: str, dor_answers: Dict[str, str], max_features: int) -> WorkDecompositionResult`
- `check_dor_before_estimation(questions: List[DoRQuestion]) -> Dict[str, Any]`
- `generate_estimation(work_description: str, questions: List[DoRQuestion]) -> Dict[str, Any]`
- `get_enhanced_estimation(work_description: str, questions: List[DoRQuestion], complexity_score: float, team_size: int) -> Dict[str, Any]`


## enhanced_feedback_module

### `EnhancedFeedbackModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> BaseOperationModule`


## privacy

### `PrivacySanitizer`


- `sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]`
- `redact_file_paths(self, text: str) -> str`
- `anonymize_user_identifier(self, user_id: str) -> str`




## __init__



## legacy_spec_generator

### `MethodInfo`




### `BusinessRule`




### `ValidationRule`




### `DatabaseOperation`




### `OpenAPIEndpoint`




### `PropertySchema`




### `LegacySpecGenerator`


- `analyze(self)`
- `generate_openapi_spec(self) -> str`
- `generate_openapi_json(self) -> str`
- `generate_cross_check_fixtures(self) -> Dict[str, Any]`
- `generate_business_spec(self) -> str`
- `generate_test_scenarios(self) -> str`
- `generate_traceability_matrix(self) -> str`
- `generate_flow_diagram(self) -> str`
- `generate_sequence_diagram(self) -> str`
- `generate_dependency_diagram(self) -> str`
- `generate_all(self)`


- `main()`


## commit_utility

### `CommitResult`




- `run_commit_utility(auto_add: bool, create_checkpoint: bool) -> Dict[str, Any]`


## git_checkpoint_utility

### `CheckpointResult`




- `run_checkpoint_utility(action: str, session_id: Optional[str], phase: Optional[str], message: Optional[str], list_all: bool) -> CheckpointResult`


## rollback_utility

### `RollbackResult`




- `run_rollback_utility(checkpoint_id: str, dry_run: bool, force: bool, skip_confirmation: bool) -> RollbackResult`


## alignment_state_tracker

### `FileAlignmentState`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'FileAlignmentState'`


### `AlignmentStateTracker`


- `mark_aligned(self, file_path: Path, operation: str, issues_fixed: int, score: Optional[int]) -> None`
- `is_aligned(self, file_path: Path) -> bool`
- `get_aligned_files(self) -> List[Path]`
- `get_modified_aligned_files(self) -> List[Path]`
- `get_alignment_info(self, file_path: Path) -> Optional[FileAlignmentState]`
- `clear_state(self, file_path: Optional[Path]) -> None`
- `get_statistics(self) -> Dict[str, Any]`




## git_pull_protector

### `GitPullProtector`


- `check_pull_safety(self) -> Tuple[bool, Dict[str, Any]]`
- `protect_and_pull(self, auto_stash: bool, preserve_alignment: bool) -> Dict[str, Any]`
- `get_protection_status(self) -> Dict[str, Any]`




## __init__



## context_linker

### `ContextLink`




### `ContextMetadata`




### `ConversationContextAnalyzer`


- `find_relevant_conversations(self, idea: IdeaCapture, limit: int) -> List[ContextLink]`


### `KnowledgeGraphLinker`


- `find_knowledge_links(self, idea: IdeaCapture, limit: int) -> List[ContextLink]`


### `OperationLinker`


- `find_operation_links(self, idea: IdeaCapture, limit: int) -> List[ContextLink]`


### `IdeaContextLinker`


- `link_idea_to_context(self, idea: IdeaCapture) -> List[ContextLink]`
- `get_idea_contexts(self, idea_id: str) -> List[ContextLink]`
- `get_context_insights(self, idea_id: str) -> Dict[str, any]`


- `create_context_linker(cortex_root: str) -> IdeaContextLinker`
- `demo_context_linking()`


## idea_organizer

### `IdeaCategory`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'IdeaCategory'`


### `IdeaTag`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'IdeaTag'`


### `IdeaCluster`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'IdeaCluster'`


### `CategoryManager`


- `categorize_idea(self, idea: IdeaCapture) -> List[IdeaCategory]`
- `detect_component(self, idea: IdeaCapture) -> Optional[str]`


### `TagSystem`


- `add_tag(self, idea_id: str, tag: IdeaTag) -> bool`
- `get_tags(self, idea_id: str) -> List[IdeaTag]`
- `auto_tag_idea(self, idea: IdeaCapture) -> List[IdeaTag]`


### `PriorityEngine`


- `calculate_priority_score(self, idea: IdeaCapture) -> float`
- `get_priority_label(self, score: float) -> str`


### `ClusteringEngine`


- `calculate_similarity(self, idea1: IdeaCapture, idea2: IdeaCapture) -> float`
- `find_clusters(self, ideas: List[IdeaCapture]) -> List[IdeaCluster]`


### `IdeaOrganizer`


- `organize_idea(self, idea: IdeaCapture, async_processing: bool) -> Dict[str, Any]`
- `batch_organize_ideas(self, ideas: List[IdeaCapture]) -> Dict[str, Any]`
- `get_organization_stats(self) -> Dict[str, Any]`
- `shutdown(self)`


- `create_idea_organizer(db_path: str, enable_clustering: bool) -> IdeaOrganizer`


## idea_queue

### `IdeaCapture`




### `IdeaQueue`


- `capture(self, raw_text: str, context: Optional[Dict[str, Any]]) -> str`
- `get_all_ideas(self, status_filter: Optional[str], limit: Optional[int]) -> List[IdeaCapture]`
- `filter_by_component(self, component: str) -> List[IdeaCapture]`
- `filter_by_project(self, project: str) -> List[IdeaCapture]`
- `get_idea(self, idea_id: str) -> Optional[IdeaCapture]`
- `complete_idea(self, idea_id: str) -> bool`
- `archive_idea(self, idea_id: str) -> bool`
- `update_priority(self, idea_id: str, priority: str) -> bool`
- `get_performance_stats(self) -> Dict[str, Any]`


- `create_idea_queue(config: Optional[Dict[str, Any]]) -> IdeaQueue`


## natural_language_interface

### `IdeaCommand`




### `IdeaNaturalLanguageInterface`


- `process_input(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`


- `create_idea_interface(config: Optional[Dict[str, Any]]) -> IdeaNaturalLanguageInterface`


## __init__

- `create_complete_idea_system(db_path: str, cortex_root: str)`


## base_incremental_utility

### `WorkChunk`


- `to_dict(self) -> Dict[str, Any]`


### `WorkCheckpoint`


- `to_dict(self) -> Dict[str, Any]`


### `IncrementalExecutionContext`


- `to_dict(self) -> Dict[str, Any]`


- `create_work_chunk(chunk_id: str, chunk_type: str, description: str, estimated_tokens: int, dependencies: Optional[List[str]], status: str, output_path: Optional[str], metadata: Optional[Dict[str, Any]]) -> WorkChunk`
- `create_checkpoint(checkpoint_id: str, completed_chunks: List[WorkChunk], results: List[Dict[str, Any]], approval_required: bool) -> WorkCheckpoint`
- `check_dependencies(chunk: WorkChunk, completed_chunk_ids: List[str]) -> Tuple[bool, List[str]]`
- `is_checkpoint_boundary(chunk: WorkChunk, all_chunks: List[WorkChunk], checkpoint_interval: int) -> Tuple[bool, str]`
- `validate_chunk(chunk: WorkChunk) -> Tuple[bool, List[str]]`
- `monitor_response_size(output: str, response_monitor: ResponseSizeMonitor, chunk_id: str) -> Dict[str, Any]`
- `get_execution_summary(context: IncrementalExecutionContext) -> Dict[str, Any]`
- `execute_incremental_workflow(chunks: List[WorkChunk], chunk_executor: Callable[[WorkChunk], Dict[str, Any]], brain_path: Optional[Path], checkpoint_callback: Optional[Callable[[WorkCheckpoint], bool]], checkpoint_interval: int, max_chunk_tokens: int) -> Dict[str, Any]`


## domain_classifier

### `Criticality`
 (inherits: Enum)




### `DomainClassification`




### `DomainClassifier`


- `classify(self, file_path: Path) -> DomainClassification`
- `classify_bulk(self, file_paths: List[Path]) -> List[DomainClassification]`
- `get_critical_files(self, file_paths: List[Path]) -> List[Path]`




## market_intelligence_engine

### `ResearchValue`
 (inherits: Enum)




### `MarketInsight`




### `ResearchReport`




### `MarketIntelligenceEngine`


- `should_research(self, user_request: str, codebase_context: str) -> ResearchReport`




## narrative_generator

### `CodeNarrative`




### `NarrativeGenerator`


- `generate_narrative(self, narrative_type: str, context: Dict[str, Any], depth: str) -> CodeNarrative`
- `format_for_master_plan(self, ast_context: Dict[str, Any], lens_context: Dict[str, Any]) -> str`
- `format_for_worker_plan(self, phase_context: Dict[str, Any], ast_context: Dict[str, Any]) -> str`




## proactive_advisor

### `ProactiveRecommendation`




### `ProactiveAdvisor`


- `generate_recommendations(self, context: Optional[Dict[str, Any]]) -> List[ProactiveRecommendation]`
- `format_recommendations(self, recommendations: List[ProactiveRecommendation]) -> str`




## risk_assessor

### `RiskLevel`
 (inherits: Enum)




### `RiskAssessment`




### `RiskAssessor`


- `assess_risk(self, operation: str, context: Dict[str, Any]) -> List[RiskAssessment]`
- `should_block_execution(self, risks: List[RiskAssessment]) -> bool`
- `format_risk_report(self, risks: List[RiskAssessment]) -> str`




## __init__



## commit_filter

### `Candidate`




### `CommitFilter`


- `filter_learning_candidates(self, commits: List[CommitMetadata]) -> List[Candidate]`


- `filter_learning_candidates(commits: List[CommitMetadata], config_path: Optional[Path]) -> List[Candidate]`


## duplication_detector

### `DuplicateMatch`




### `DuplicationDetector`


- `find_duplicates(self, lesson: CapturedLesson, threshold: float, max_results: int) -> List[DuplicateMatch]`


- `extract_keywords(lesson: CapturedLesson) -> List[str]`


## git_history_scanner

### `CommitMetadata`




### `GitHistoryScanner`


- `scan_commits(self, since_hours: int, use_cache: bool) -> List[CommitMetadata]`


- `scan_commits(repo_path: Optional[Path], since_hours: int) -> List[CommitMetadata]`


## lesson_capture

### `ValidationError`
 (inherits: Exception)




### `CapturedLesson`




### `LessonCapture`


- `capture_lesson(self, candidate: Candidate) -> Optional[CapturedLesson]`




## planning_learner

### `RoutingDecision`




### `PlanningLearner`


- `record_decision(self, request: str, tier: int, complexity: float)`
- `provide_feedback(self, request: str, correct_tier: int, reason: str)`
- `get_accuracy_metrics(self) -> Dict[str, Any]`
- `get_calibration_summary(self) -> str`




## yaml_writer

### `SchemaValidationError`
 (inherits: Exception)




### `YAMLWriter`


- `append_lesson(self, lesson: CapturedLesson) -> str`


- `generate_lesson_id(existing_ids: List[str]) -> str`


## __init__



## lint_utility

### `ViolationSeverity`
 (inherits: Enum)




### `Violation`


- `to_dict(self) -> Dict`


### `LintResult`


- `critical_count(self) -> int`
- `warning_count(self) -> int`
- `info_count(self) -> int`
- `total_count(self) -> int`


- `lint_file(file_path: Path) -> LintResult`
- `lint_directory(dir_path: Path, pattern: str) -> List[LintResult]`
- `check_violations(results: List[LintResult], severity: ViolationSeverity) -> Dict`
- `generate_lint_report(results: List[LintResult], output_path: Path) -> bool`
- `list_violations(results: List[LintResult], severity: Optional[ViolationSeverity]) -> List[Violation]`


## onboarding_utility

### `UserProfile`




### `ProfileResult`




- `create_profile(user_id: str, experience_level: str, interaction_mode: str, tech_stack: Optional[str]) -> ProfileResult`
- `load_profile(user_id: str) -> ProfileResult`
- `update_profile(user_id: str, experience_level: Optional[str], interaction_mode: Optional[str], tech_stack: Optional[str]) -> ProfileResult`
- `run_onboarding(user_id: str) -> ProfileResult`
- `validate_profile(user_id: str) -> ProfileResult`


## code_quality_analyzer

### `CodeQualityAnalyzer`


- `analyze(self) -> Dict[str, Any]`




## cortex_optimization_models

### `OptimizationMetrics`






## doc_deduplicator

### `DocumentDeduplicator`


- `deduplicate(self, metrics: OptimizationMetrics) -> Dict[str, Any]`




## hardcoded_data_analyzer

### `HardcodedDataAnalyzer`


- `analyze(self) -> Dict[str, Any]`




## hardcoded_data_cleaner_module

### `HardcodedViolation`




### `HardcodedDataMetrics`




### `HardcodedDataCleanerModule`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`


- `register() -> BaseOperationModule`


## optimize_cortex_orchestrator

### `OptimizeCortexOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `rollback(self, context: Dict[str, Any]) -> bool`


- `register() -> BaseOperationModule`


## __init__



## audit_logger

### `AuditEvent`


- `to_dict(self) -> dict`


### `AuditLogger`


- `log_event(self, event_type: str, session_id: str, plan_id: str, orchestrator: str, user_request: Optional[str], phase: str, metadata: Optional[Dict[str, Any]], outcome: str, duration_ms: Optional[int], error_message: Optional[str]) -> None`
- `query_events(self, plan_id: Optional[str], session_id: Optional[str], event_type: Optional[str], orchestrator: Optional[str], since: Optional[datetime], until: Optional[datetime], outcome: Optional[str], limit: Optional[int]) -> List[Dict[str, Any]]`
- `get_plan_history(self, plan_id: str) -> List[Dict[str, Any]]`
- `get_session_timeline(self, session_id: str) -> List[Dict[str, Any]]`
- `export_to_csv(self, events: List[Dict[str, Any]], output_path: str) -> None`
- `generate_stats(self, since: Optional[datetime]) -> Dict[str, Any]`
- `archive_old_logs(self, days_threshold: int) -> Dict[str, Any]`


- `get_audit_logger(base_path: Optional[Path]) -> AuditLogger`


## session_context_manager

### `PlanningSession`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'PlanningSession'`


### `SessionContextManager`


- `create_session(self, plan_id: str, user_request: str, complexity_tier: int, temp_plan_path: Path) -> PlanningSession`
- `get_active_session_for_plan(self, plan_id: str) -> Optional[PlanningSession]`
- `update_session(self, session_id: str, status: Optional[str], iteration_count: Optional[int])`
- `close_session(self, session_id: str)`
- `get_all_active_sessions(self) -> Dict[str, PlanningSession]`
- `load_context_for_request(self, user_request: str) -> Optional[PlanningSession]`




## temporary_plan_manager

### `RefinementIteration`




### `InteractiveRefinementSession`


- `add_iteration(self, iteration: RefinementIteration)`


### `TemporaryPlanManager`


- `start_refinement_session(self, user_request: str, complexity_tier: int) -> InteractiveRefinementSession`
- `refine_plan(self, session_id: str, user_feedback: str) -> Dict[str, Any]`
- `request_approval(self, session_id: str) -> ApprovalResult`
- `approve_plan(self, session_id: str, approved_by: str) -> Dict[str, Any]`
- `reject_plan(self, session_id: str, reason: str) -> Dict[str, Any]`




## phase8_utility

- `calculate_cleanup_metrics(files: List[Path]) -> Dict[str, Any]`
- `generate_completion_report() -> str`
- `handle_integration_cleanup(brain_path: str, dry_run: bool, profile: str) -> Dict[str, Any]`
- `handle_completion_report(brain_path: str, output_path: str) -> Dict[str, Any]`
- `handle_phase8_status() -> Dict[str, Any]`


## complexity_analyzer

### `ComplexityAnalysis`




### `ComplexityAnalyzer`


- `analyze(self, plan_data: Dict[str, Any]) -> ComplexityAnalysis`




## format_selector

### `PlanFormatSelector`


- `select_format(self, plan_metadata: Dict[str, Any]) -> Dict[str, Any]`
- `get_format_requirements(self, format_type: Literal['single-file', 'master-plan']) -> Dict[str, Any]`
- `generate_master_plan(self, plan_metadata: Dict[str, Any], output_path) -> str`




## master_plan_template

### `MasterPlanSection`
 (inherits: Enum)




### `MasterPlanTemplate`


- `get_required_sections(cls) -> List[MasterPlanSection]`
- `get_optional_sections(cls, tier: str) -> List[MasterPlanSection]`
- `get_section_order(cls, complexity_tier: int) -> List[MasterPlanSection]`
- `validate_section_order(cls, actual_sections: List[str]) -> Dict[str, Any]`
- `get_cortex_header() -> str`




## migration_utility

- `migrate_documents(planning_path: str, dry_run: bool, create_backup: bool) -> Dict`
- `detect_status(plan_path: str) -> str`
- `backup_planning_dir(planning_dir: Path, plans: List[Path]) -> Path`
- `validate_migration(planning_dir: Path, original_plans: List[Path], migrations: List[Dict]) -> bool`
- `organize_by_status(planning_path: str, document_path: str) -> Optional[str]`


## phase_lifecycle_manager

### `PhaseLifecycleManager`


- `start_phase(self, master_plan_path: Path, phase_number: int) -> Dict[str, Any]`
- `complete_phase(self, master_plan_path: Path, phase_number: int, duration: timedelta, tokens_saved: int, metrics: Optional[Dict]) -> Dict[str, Any]`
- `get_next_phase(self, master_plan_path: Path) -> Optional[int]`




## planning_utility

### `PlanResult`




### `ValidationResult`




- `detect_execution_mode(user_input: str) -> str`
- `analyze_risks(plan_data: Dict[str, Any]) -> List[Dict[str, str]]`
- `detect_plan_complexity(feature_name: str, description: str, user_input: str) -> Tuple[str, bool, str]`
- `create_plan(feature_name: str, description: str, author: str, complexity: str, user_input: str) -> PlanResult`
- `load_plan(plan_path: Path) -> PlanResult`
- `save_plan(plan_data: Dict[str, Any], plan_path: Optional[Path]) -> PlanResult`
- `validate_plan(plan_data: Dict[str, Any]) -> ValidationResult`
- `generate_markdown(plan_data: Dict[str, Any]) -> str`
- `approve_plan(plan_filename: str) -> PlanResult`
- `complete_plan(plan_filename: str) -> PlanResult`


## plan_manifest_tracker

### `PlanManifestTracker`


- `register_plan(self, plan_id: str, title: str, status: str, complexity_tier: int, created_date: str, approved_date: str, folder: str, phases: int, estimated_days: float, metadata: Optional[Dict[str, Any]])`
- `update_plan_status(self, plan_id: str, status: str)`
- `get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]`
- `get_all_plans(self) -> List[Dict[str, Any]]`
- `get_plans_by_status(self, status: str) -> List[Dict[str, Any]]`
- `remove_plan(self, plan_id: str)`




## plan_sync_manager

### `PlanningFileWatcher`
 (inherits: FileSystemEventHandler)


- `on_modified(self, event: FileModifiedEvent)`


### `PlanSyncManager`


- `start_file_watcher(self)`
- `stop_file_watcher(self)`
- `sync_file_to_database(self, file_path: Path) -> Dict[str, Any]`
- `sync_database_to_file(self, plan_id: str) -> Dict[str, Any]`
- `resolve_plan_by_name(self, plan_name: str) -> Optional[Dict[str, Any]]`
- `validate_sync_integrity(self) -> Dict[str, Any]`




## task_injector

### `StandardTask`




### `TaskInjector`


- `inject_standard_tasks(self, phase_tasks: List[Dict[str, Any]], phase_number: int, phase_name: str) -> List[Dict[str, Any]]`
- `get_standard_task_checklist(self, phase_number: int) -> List[str]`
- `validate_standard_tasks_present(self, phase_tasks: List[Dict[str, Any]]) -> tuple[bool, List[str]]`




## token_reduction_tracker

### `TokenBaseline`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'TokenBaseline'`


### `PhaseReduction`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'PhaseReduction'`


### `TokenReductionTracker`


- `establish_baseline(self, plan_id: str, token_count: int, file_count: int, measurement_date: datetime)`
- `record_reduction(self, plan_id: str, phase_number: int, tokens_saved: int, files_modified: List[str])`
- `get_plan_metrics(self, plan_id: str) -> Dict`
- `calculate_percentage(self, baseline: int, current: int) -> float`
- `format_tokens(self, tokens: int, include_label: bool) -> str`




## unified_plan_generator

### `UnifiedPlanGenerator`


- `standardize_hours(self, hours_value: str) -> str`
- `compress_phase_name(self, phase_name: str, compressed: bool) -> str`
- `generate_master_plan(self, plan_id: str, phases: List[Dict], metadata: Dict, include_token_tracking: bool, include_visual_tracker: bool, include_continuation_prompt: bool, compressed: bool, manifest_path: Optional[str]) -> str`
- `generate_progress_tracker(self, phases: List[Dict], baseline_tokens: int, current_tokens: int, total_files: int, compressed: bool, include_detailed_tracker: bool) -> str`
- `generate_continuation_prompt(self, plan_id: str, completed_phases: int, total_phases: int, next_phase_number: Optional[int], next_phase_name: Optional[str], progress_percentage: int, manifest_path: Optional[str]) -> str`
- `update_phase_status(self, master_plan_content: str, phase_number: int, new_status: str, actual_time: Optional[str], tokens_saved: Optional[int], master_plan_path: Optional[Path], auto_commit: bool, commit_message_prefix: Optional[str]) -> str`
- `generate_worker_plan(self, plan_id: str, phase_number: int, phase_name: str, phase_data: Dict[str, Any], inject_standard_tasks: bool) -> str`




## __init__



## pr_context_utility

### `Language`
 (inherits: Enum)




### `FileNode`




### `DependencyGraph`




- `detect_language(filepath: str) -> Language`
- `extract_imports(filepath: str, content: str) -> List[str]`
- `is_test_file(filepath: str) -> bool`
- `estimate_tokens(content: Optional[str], filepath: Optional[str]) -> int`
- `resolve_import_path(source_file: str, import_name: str, workspace_root: str) -> Optional[str]`
- `find_test_files(changed_files: List[str], workspace_root: str) -> List[str]`
- `build_pr_context(changed_files: List[str], workspace_root: str, max_files: int, token_budget: int, include_tests: bool, include_indirect: bool) -> DependencyGraph`


## publish_branch_orchestrator

### `PublishBranchOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]`
- `execute(self, context: Dict[str, Any]) -> OperationResult`
- `cleanup(self, context: Dict[str, Any]) -> None`




## __init__



## bloat_detector

### `FileType`
 (inherits: Enum)




### `BloatThreshold`




### `BloatReport`




### `BloatDetector`


- `scan_codebase(self) -> List[BloatReport]`
- `scan_staged_files(self) -> List[BloatReport]`
- `generate_report(self, bloated_files: List[BloatReport]) -> str`


- `main()`


## context_renderer

### `RenderResult`




### `ContextRenderer`


- `render(self, template_result: TemplateSelectionResult, context: Dict[str, Any]) -> RenderResult`


- `render_response_for_question(question: str, context: Dict[str, Any], brain_path: str) -> RenderResult`


## question_router

### `QuestionRoutingResult`




### `RoutingResult`




### `IntelligentQuestionRouter`


- `route_question(self, user_message: str, conversation_history: Optional[List[str]], current_files: Optional[List[str]]) -> QuestionRoutingResult`
- `route(self, message: str, context: Dict) -> 'RoutingResult'`


### `QuestionRouter`


- `route(self, message: str, context: Dict) -> 'RoutingResult'`




## template_engine_integration

### `TemplateEngine`


- `render_template(self, template_name: str, user_message: str, context: Dict[str, Any], force_refresh: bool) -> Dict[str, Any]`


### `EnhancedQuestionHandler`


- `handle_question(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]`


- `test_integration()`
- `demo_live_template_rendering()`


## rca_utility

### `RCAStatus`
 (inherits: Enum)




### `WhyDepth`
 (inherits: Enum)




### `IncidentDetails`




### `WhyQuestion`




### `RootCause`




### `CorrectiveAction`




### `RCAAnalysis`




### `RCAResult`




- `create_rca(incident_id: str, title: str, description: str, occurred_at: str, detected_at: str, **kwargs) -> RCAResult`
- `load_rca(analysis_id: str) -> RCAResult`
- `update_rca(analysis_id: str, **updates) -> RCAResult`
- `add_why_question(analysis_id: str, question: str, answer: Optional[str], evidence: Optional[List[str]]) -> RCAResult`
- `generate_report(analysis_id: str) -> RCAResult`
- `list_rcas(status: Optional[RCAStatus]) -> RCAResult`


## autonomous_execution_wiring_checker

### `AutonomousExecutionWiringChecker`


- `check_autonomous_execution_wiring(self) -> Tuple[bool, List[str], List[str]]`


- `check_autonomous_execution_wiring(cortex_root: Path) -> Dict[str, any]`


## component_discovery_scanner

### `DiscoveredComponent`




### `ComponentDiscoveryScanner`


- `discover_components(self, cortex_root: Path) -> List[DiscoveredComponent]`


- `format_discovery_report(components: List[DiscoveredComponent]) -> Dict`


## feature_auto_registrar

### `OperationMetadata`




### `RegistrationResult`




### `FeatureAutoRegistrar`


- `extract_module_docstring(self, content: str) -> str`
- `extract_natural_language_triggers(self, content: str, docstring: str) -> List[str]`
- `infer_deployment_tier(self, file_path: Path, content: str) -> str`
- `infer_category(self, file_path: Path) -> str`
- `extract_usage_examples(self, docstring: str) -> List[str]`
- `find_related_modules(self, operation_name: str) -> List[str]`
- `analyze_operation_file(self, file_path: Path) -> OperationMetadata`
- `format_triggers(self, triggers: List[str]) -> str`
- `format_examples(self, examples: List[str]) -> str`
- `generate_yaml_entry(self, metadata: OperationMetadata) -> str`
- `insert_yaml_entry(self, yaml_entry: str) -> None`
- `update_statistics(self) -> None`
- `add_changelog_entry(self, operation_name: str) -> None`
- `register_feature(self, operation_name: str, dry_run: bool) -> RegistrationResult`
- `batch_register(self, operation_names: List[str], dry_run: bool) -> Dict[str, RegistrationResult]`


- `main()`


## feature_registration_validator

### `ValidationResult`


- `unregistered_count(self) -> int`
- `registration_percentage(self) -> float`


### `FeatureRegistrationValidator`


- `scan_operations_directory(self) -> List[str]`
- `scan_operation_modules(self) -> List[Dict[str, str]]`
- `load_registered_operations(self) -> Dict[str, Any]`
- `is_module_registered(self, module_info: Dict[str, str], registered_ops: Dict[str, Any]) -> bool`
- `identify_unregistered(self) -> Dict[str, Any]`
- `validate(self) -> ValidationResult`
- `generate_report(self, result: ValidationResult) -> str`


- `main()`


## fix_template_structure

- `fix_template_structure(templates_file: Path) -> dict`


## intent_router_auto_fixer

### `IntentRouterFix`




### `IntentRouterAutoFixer`


- `extract_triggers_from_operation(self, operation_name: str) -> List[str]`
- `add_to_intent_router(self, operation_name: str, triggers: Optional[List[str]], dry_run: bool) -> IntentRouterFix`
- `fix_missing_operations(self, missing_operations: List[str], dry_run: bool) -> List[IntentRouterFix]`




## obsolete_code_auto_cleaner

### `CleanupResult`




### `ObsoleteCodeAutoCleaner`


- `create_backup_dir(self) -> Path`
- `is_safe_to_delete(self, file_path: Path) -> tuple[bool, str]`
- `backup_file(self, file_path: Path, backup_dir: Path) -> Optional[Path]`
- `delete_file(self, file_path: Path) -> bool`
- `cleanup_files(self, files_to_remove: List[Path], dry_run: bool) -> CleanupResult`
- `cleanup_obsolete_tests(self, obsolete_tests: List[Path], dry_run: bool) -> CleanupResult`
- `cleanup_obsolete_scripts(self, obsolete_scripts: List[Path], dry_run: bool) -> CleanupResult`
- `cleanup_obsolete_orchestrators(self, obsolete_orchestrators: List[Path], dry_run: bool) -> CleanupResult`
- `rollback_cleanup(self, backup_dir: Path) -> bool`




## obsolete_code_detector

### `ImportAnalysis`




### `CleanupPlan`


- `get_all_files(self) -> List[Path]`


### `ObsoleteCodeDetector`


- `has_migrated_utility(self, orchestrator_name: str) -> bool`
- `scan_for_obsolete_orchestrators(self) -> List[Path]`
- `scan_for_obsolete_tests(self) -> List[Path]`
- `scan_for_obsolete_scripts(self) -> List[Path]`
- `analyze_import_usage(self, file_path: Path) -> ImportAnalysis`
- `scan_all_for_deprecated_imports(self) -> List[ImportAnalysis]`
- `calculate_total_size(self, files: List[Path]) -> float`
- `detect_all(self) -> Dict[str, List[Path]]`
- `generate_cleanup_plan(self) -> CleanupPlan`
- `generate_report(self, plan: CleanupPlan) -> str`


- `main()`


## realignment_utility

### `RealignmentAction`




### `RealignmentResult`




- `realign(project_root: Path, cortex_root: Path, interactive: bool) -> RealignmentResult`
- `generate_actions(violations: List) -> List[RealignmentAction]`
- `create_naming_action(violation) -> Optional[RealignmentAction]`
- `create_security_action(violation) -> Optional[RealignmentAction]`
- `create_standards_action(violation) -> Optional[RealignmentAction]`
- `create_architecture_action(violation) -> Optional[RealignmentAction]`
- `apply_action(action: RealignmentAction) -> bool`
- `generate_report(cortex_root: Path, project_root: Path, applied: List[RealignmentAction], skipped: List[RealignmentAction], errors: List[str], before: float, after: float) -> Path`
- `align_system_v2(project_root: Path, cortex_root: Path, auto_fix: bool, dry_run: bool) -> Dict[str, Any]`


## response_template_auto_generator

### `TemplateGenerationResult`




### `ResponseTemplateAutoGenerator`


- `extract_operation_metadata(self, operation_name: str) -> Dict[str, str]`
- `generate_template(self, operation_name: str) -> str`
- `add_template(self, operation_name: str, dry_run: bool) -> TemplateGenerationResult`
- `generate_missing_templates(self, missing_operations: List[str], dry_run: bool) -> List[TemplateGenerationResult]`




## safe_cleanup_executor

### `CleanupCategory`
 (inherits: Enum)




### `CleanupResult`


- `success(self) -> bool`


### `ExecutionReport`


- `success(self) -> bool`


### `SafeCleanupExecutor`


- `check_git_status(self) -> bool`
- `run_tests(self) -> bool`
- `create_backup(self, files: List[Path]) -> Path`
- `remove_files(self, files: List[Path]) -> tuple[List[Path], List[Path]]`
- `restore_backup(self, backup_path: Path, files: List[Path]) -> bool`
- `cleanup_category(self, category: CleanupCategory, files: List[Path], run_tests_after: bool) -> CleanupResult`
- `execute_cleanup(self, plan: CleanupPlan, dry_run: bool, skip_git_check: bool, skip_tests: bool) -> ExecutionReport`
- `generate_report(self, report: ExecutionReport, dry_run: bool) -> str`


- `main()`


## specialist_router_wiring_checker

### `SpecialistRouter`




### `WiringIssue`




### `SpecialistRouterWiringChecker`


- `check_wiring(self) -> Dict[str, Any]`
- `fix_wiring(self, dry_run: bool) -> Dict[str, Any]`




## dashboard_utility

- `generate_dashboard(output_filename: Optional[str], days: int, include_charts: Optional[List[str]]) -> Dict[str, Any]`
- `render_health_chart(health_data: List[Dict]) -> Dict`
- `render_heatmap(health_data: List[Dict]) -> Dict`
- `render_coverage(test_results: List[Dict]) -> Dict`
- `render_radar(code_metrics: List[Dict]) -> Dict`
- `export_dashboard(html_path: str, format: str) -> Dict[str, Any]`


## review_utility

### `ReviewDepth`
 (inherits: Enum)




### `ReviewStatus`
 (inherits: Enum)




### `CodeIssue`




### `QualityMetrics`




### `ReviewSession`




### `ReviewResult`




- `create_review(title: str, description: str, depth: ReviewDepth, **kwargs) -> ReviewResult`
- `load_review(review_id: str) -> ReviewResult`
- `analyze_file(review_id: str, file_path: Path, content: Optional[str]) -> ReviewResult`
- `generate_report(review_id: str) -> ReviewResult`
- `list_reviews(status: Optional[ReviewStatus]) -> ReviewResult`


## complexity_analyzer

### `ComplexityTier`
 (inherits: Enum)




### `ComplexityScore`


- `to_dict(self) -> Dict`


### `ComplexityAnalyzer`


- `analyze(self, user_request: str, codebase_context: Optional[Dict]) -> ComplexityScore`




## domain_classifier

### `DomainCriticality`
 (inherits: Enum)




### `DomainClassification`


- `to_dict(self) -> Dict`


### `DomainClassifier`


- `classify(self, user_request: str, file_paths: Optional[List[str]], codebase_context: Optional[Dict]) -> DomainClassification`
- `get_analysis_depth_config(self, classification: DomainClassification) -> Dict[str, any]`




## planning_intelligence_coordinator

### `PlanningMode`
 (inherits: Enum)




### `TestStrategy`
 (inherits: Enum)




### `PlanningDecision`


- `to_dict(self) -> Dict`


### `PlanningIntelligenceCoordinator`


- `analyze_request(self, user_request: str, codebase_context: Optional[Dict], target_files: Optional[List[Path]]) -> PlanningDecision`




## tiered_router

### `OperationTier`
 (inherits: Enum)




### `RoutingDecision`




### `RoutingFeedback`




### `RegexFallback`


- `classify(self, operation: str) -> int`


### `RoutingTelemetry`


- `record_decision(self, decision: RoutingDecision)`
- `record_feedback(self, operation: str, expected_tier: int, actual_tier: int)`
- `calculate_accuracy(self, last_n: int) -> float`
- `get_metrics(self) -> Dict[str, Any]`


### `TieredRouter`


- `route(self, operation: str, context: Dict[str, Any]) -> RoutingDecision`
- `get_telemetry(self) -> Dict[str, Any]`
- `provide_feedback(self, operation: str, expected_tier: int, actual_tier: int)`




## unified_entry_point_utility

### `OperationType`
 (inherits: Enum)




### `WorkflowResult`


- `to_dict(self) -> Dict[str, Any]`


### `OrchestratorRegistry`


- `is_available(self, operation_type: OperationType) -> bool`


- `initialize_orchestrators(cortex_root: Path) -> OrchestratorRegistry`
- `execute_code_review(cortex_root: Path, registry: OrchestratorRegistry, pr_info: str, depth: str, focus_areas: Optional[List[str]]) -> WorkflowResult`
- `execute_ado_story(cortex_root: Path, registry: OrchestratorRegistry, title: str, description: str, acceptance_criteria: Optional[List[str]], **kwargs) -> WorkflowResult`
- `execute_ado_feature(cortex_root: Path, registry: OrchestratorRegistry, title: str, description: str, related_stories: Optional[List[str]], **kwargs) -> WorkflowResult`
- `generate_work_summary(registry: OrchestratorRegistry, work_item_id: str) -> Tuple[bool, str, Optional[str]]`
- `perform_code_review(code_review_orch: Any, pr_info: str, depth: str, focus_areas: Optional[List[str]]) -> Dict[str, Any]`
- `generate_code_review_summary(result: WorkflowResult) -> str`
- `generate_story_summary(result: WorkflowResult, metadata: Any) -> str`
- `generate_feature_summary(result: WorkflowResult, metadata: Any) -> str`
- `save_summary(cortex_root: Path, result: WorkflowResult, category: str) -> bool`
- `format_priority(priority: int) -> str`
- `review_pr(pr_info: str, cortex_root: Path, depth: str, focus_areas: Optional[List[str]]) -> Dict[str, Any]`
- `create_user_story(title: str, description: str, cortex_root: Path, **kwargs) -> Dict[str, Any]`
- `create_feature(title: str, description: str, cortex_root: Path, **kwargs) -> Dict[str, Any]`
- `check_planning_gate(user_request: str, operation_id: str) -> Dict[str, Any]`
- `route_operation(operation_id: str, cortex_root: Path, operation_config: Dict[str, Any], **kwargs) -> Dict[str, Any]`
- `invoke_cli_wrapper(operation_id: str, cortex_root: Path, cli_script: str, output_format: str, verbose: bool, **kwargs) -> Dict[str, Any]`


## __init__



## code_pattern_detector

### `DomainPatterns`


- `to_dict(self) -> Dict`
- `pattern_count(self) -> int`


### `PatternCache`


- `get_cache_path(self, project_root: Path) -> Path`
- `load(self, project_root: Path) -> Optional[DomainPatterns]`
- `save(self, project_root: Path, patterns: DomainPatterns)`


- `detect_patterns(project_root: Path, language: str, use_cache: bool) -> DomainPatterns`
- `detect_python_patterns(project_root: Path) -> DomainPatterns`
- `detect_typescript_patterns(project_root: Path) -> DomainPatterns`
- `detect_csharp_patterns(project_root: Path) -> DomainPatterns`
- `detect_java_patterns(project_root: Path) -> DomainPatterns`
- `detect_generic_patterns(project_root: Path) -> DomainPatterns`


## copilot_instructions_merger

### `MergeResult`


- `to_dict(self) -> Dict`


- `is_cortex_managed_section(header: str, content: str) -> bool`
- `classify_section(header: str, content: str) -> str`
- `parse_markdown_sections(content: str) -> Dict[str, str]`
- `render_markdown(sections: Dict[str, str]) -> str`
- `generate_cortex_sections(project_name: str, language: str, framework: str, domain_patterns: Optional[object]) -> Dict[str, str]`
- `merge_with_existing(existing_path: Path, project_name: str, language: str, framework: str, domain_patterns: Optional[object]) -> MergeResult`
- `generate_new_instructions(project_name: str, language: str, framework: str, build_system: str, test_framework: str, domain_patterns: Optional[object]) -> str`


## master_setup_utility

### `ProjectDetection`


- `to_dict(self) -> Dict[str, Any]`


### `UserConsent`


- `is_step_approved(self, step_id: str) -> bool`
- `to_dict(self) -> Dict[str, Any]`


### `DependencyInstallation`


- `to_dict(self) -> Dict[str, Any]`


### `PolicyValidation`


- `to_dict(self) -> Dict[str, Any]`


### `GitIgnoreSetup`


- `to_dict(self) -> Dict[str, Any]`


### `SetupResult`


- `to_dict(self) -> Dict[str, Any]`


- `detect_project_structure(project_root: Path, deep_scan: bool) -> ProjectDetection`
- `request_user_consent(project_name: str, detection: ProjectDetection, interactive: bool, available_steps: Optional[List[str]]) -> UserConsent`
- `install_dependencies(cortex_root: Path, force_reinstall: bool) -> DependencyInstallation`
- `validate_policies(project_root: Path, cortex_root: Path, create_starter: bool) -> PolicyValidation`
- `setup_gitignore(project_root: Path, patterns: Optional[List[str]]) -> GitIgnoreSetup`
- `generate_copilot_instructions(project_root: Path, project_name: str, detection: ProjectDetection, force: bool, enable_code_analysis: bool) -> Dict[str, Any]`
- `create_completion_report(project_name: str, cortex_root: Path, phase_results: Dict[str, Any], start_time: datetime, setup_success: bool) -> str`


## setup_utility

- `create_versioned_shared_venv(python_version: Optional[str], home_dir: Optional[Path]) -> Dict[str, Any]`
- `create_shared_venv(home_dir: Optional[Path]) -> Dict[str, Any]`
- `install_cortex_tooling(venv_path: Path) -> Dict[str, Any]`
- `link_project(project_dir: Path, venv_path: Path) -> Dict[str, Any]`
- `install_project_deps(project_dir: Path, python_path: Path) -> Dict[str, Any]`
- `get_python_path(venv_path: Path) -> Path`
- `get_project_env_vars(project_dir: Path) -> Dict[str, str]`


## governance_drift_checker

### `GovernanceDriftChecker`


- `check(self) -> Dict[str, Any]`




## optimization_models

### `OptimizationMetrics`




### `SystemHealthReport`


- `to_dict(self) -> Dict[str, Any]`




## optimize_system_orchestrator

### `OptimizeSystemOrchestrator`
 (inherits: BaseOperationModule)


- `get_metadata(self) -> OperationModuleMetadata`
- `validate_prerequisites(self, context: Dict[str, Any]) -> OperationResult`
- `execute(self, context: Dict[str, Any]) -> OperationResult`


- `register() -> OptimizeSystemOrchestrator`


## __init__



## tdd_utility

### `TDDPhase`
 (inherits: Enum)




### `TDDResult`




### `TDDSession`




- `start_tdd_session(feature_name: str, test_file: Path, impl_file: Path) -> TDDResult`
- `run_tests(test_file: Path, test_name: Optional[str]) -> TDDResult`
- `transition_phase(session_id: str, target_phase: TDDPhase, validation: bool) -> TDDResult`
- `get_session_status(session_id: str) -> TDDResult`
- `generate_test_skeleton(feature_name: str, test_file: Path, impl_file: Path) -> TDDResult`
- `update_session_metrics(session_id: str, tests_written: Optional[int], tests_passing: Optional[int]) -> TDDResult`
- `complete_session(session_id: str) -> TDDResult`


## cortex_header

- `generate_cortex_header(document_title: str, document_type: str, status: str, version: Optional[str], additional_metadata: Optional[Dict[str, str]]) -> str`
- `generate_sub_plan_header(phase_id: str, phase_name: str, master_plan_path: str, status: str, version: Optional[str]) -> str`
- `generate_report_header(report_title: str, report_type: str, project_name: Optional[str]) -> str`
- `generate_ado_header(feature_title: str, feature_type: str, priority: str, area_path: Optional[str]) -> str`
- `extract_document_title(content: str) -> Optional[str]`
- `has_cortex_header(content: str) -> bool`
- `inject_cortex_header(content: str, header_type: str, **kwargs) -> str`


## __init__



## upgrade_utility

### `VersionInfo`


- `to_dict(self) -> Dict[str, Any]`


### `BackupMetadata`


- `to_dict(self) -> Dict[str, Any]`


### `UpgradeResult`


- `to_dict(self) -> Dict[str, Any]`


- `get_current_version(cortex_root: Path) -> str`
- `get_remote_version(cortex_root: Path) -> str`
- `compare_versions(v1: str, v2: str) -> int`
- `check_for_updates(cortex_root: Path) -> VersionInfo`
- `create_backup(cortex_root: Path) -> Optional[BackupMetadata]`
- `verify_backup(cortex_root: Path, backup_id: str) -> bool`
- `restore_backup(cortex_root: Path, backup_id: str) -> bool`
- `list_backups(cortex_root: Path) -> List[BackupMetadata]`
- `run_migrations(cortex_root: Path) -> Tuple[bool, int]`
- `uninstall_unused_packages(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]`
- `validate_dependencies(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]`
- `validate_operational_readiness(cortex_root: Path) -> Tuple[bool, Dict[str, Any]]`
- `execute_upgrade(cortex_root: Path, backup: bool, auto_migrate: bool, force: bool) -> UpgradeResult`


## ux_enhancement_utility

- `analyze_and_generate_dashboard(cortex_root: Path, codebase_path: str, user_request: str, skip_explanation: bool) -> Dict[str, Any]`
- `validate_codebase(codebase_path: str) -> Dict[str, Any]`
- `analyze_quality(codebase_path: str) -> Dict[str, Any]`
- `analyze_architecture(codebase_path: str) -> Dict[str, Any]`
- `analyze_performance(codebase_path: str) -> Dict[str, Any]`
- `analyze_security(codebase_path: str) -> Dict[str, Any]`
- `apply_discovery_patterns(quality: Dict, architecture: Dict, performance: Dict, security: Dict) -> Dict[str, Any]`
- `export_to_dashboard_format(codebase_info: Dict, quality: Dict, architecture: Dict, performance: Dict, security: Dict, discovery: Dict) -> Dict[str, Any]`
- `generate_dashboard_html(brain_path: Path, dashboard_data: Dict, user_request: str) -> Path`


## planning_rules_validator

### `ValidationIssue`




### `PlanningValidationReport`


- `has_blocking_issues(self) -> bool`
- `compliance_rate(self) -> float`


### `PlanningRulesValidator`


- `validate_all_plans(self) -> PlanningValidationReport`
- `generate_recommendations(self, report: PlanningValidationReport) -> List[str]`


- `validate_planning_rules(project_root: Path) -> PlanningValidationReport`


## ast_completeness_checker

### `ASTCompletenessChecker`


- `extract_public_methods(self) -> List[Dict[str, any]]`
- `extract_if_statements(self) -> List[Dict[str, any]]`
- `extract_validation_rules(self) -> List[Dict[str, any]]`
- `extract_database_operations(self) -> List[Dict[str, any]]`
- `extract_external_service_calls(self) -> List[Dict[str, any]]`
- `extract_spec_operations(self) -> Set[str]`
- `extract_spec_business_rules(self) -> List[str]`
- `extract_spec_line_references(self) -> Set[int]`
- `validate_method_coverage(self) -> Tuple[bool, List[str]]`
- `validate_business_rule_coverage(self) -> Tuple[bool, List[str]]`
- `validate_validation_coverage(self) -> Tuple[bool, List[str]]`
- `validate_database_operations_coverage(self) -> Tuple[bool, List[str]]`
- `run_all_checks(self) -> Dict[str, any]`
- `print_report(self, results: Dict[str, any])`


- `main()`


## data_flow_validator

### `DataFlowValidator`


- `parse_mermaid_sequence(self) -> List[Dict[str, str]]`
- `extract_documented_paths(self) -> Set[str]`
- `parse_trace_log(self) -> List[Dict[str, str]]`
- `extract_components(self) -> Set[str]`
- `extract_alt_paths(self) -> List[Dict[str, any]]`
- `validate_diagram_syntax(self) -> Tuple[bool, List[str]]`
- `validate_completeness(self) -> Tuple[bool, List[str]]`
- `validate_against_trace(self) -> Tuple[bool, List[str]]`
- `calculate_coverage_score(self) -> float`
- `run_all_checks(self) -> Dict[str, any]`
- `print_report(self, results: Dict[str, any])`


- `main()`


## domain_boundary_checker

### `ViolationType`
 (inherits: Enum)




### `Violation`




### `DomainBoundaryChecker`


- `check_file(self, file_path: Path) -> List[Violation]`
- `check_project(self, project_path: Path) -> List[Violation]`
- `check_solution(self, solution_path: Path) -> List[Violation]`
- `generate_report(self) -> str`


- `main()`


## mermaid_diagram_validator

### `DiagramValidationError`




### `DiagramValidationResult`




### `MermaidDiagramValidator`


- `validate_markdown_file(self, md_file_path: Path) -> DiagramValidationResult`


- `validate_spec_file(spec_file_path: Path) -> DiagramValidationResult`
- `print_validation_report(result: DiagramValidationResult, file_path: Path)`


## project_reference_validator

### `LayerType`
 (inherits: Enum)




### `ProjectReference`




### `ReferenceViolation`




### `ProjectReferenceValidator`


- `validate_project(self, csproj_path: Path) -> List[ReferenceViolation]`
- `validate_solution(self, solution_path: Path, domain_filter: str) -> List[ReferenceViolation]`
- `generate_report(self) -> str`


- `main()`


## traceability_calculator

### `TraceabilityCalculator`


- `count_logic_lines(self) -> int`
- `extract_spec_line_references(self) -> Set[int]`
- `extract_matrix_mappings(self) -> List[Dict[str, str]]`
- `calculate_spec_coverage(self) -> Tuple[float, Dict[str, any]]`
- `calculate_matrix_coverage(self) -> Tuple[float, Dict[str, any]]`
- `validate_bidirectional_traceability(self) -> Tuple[bool, List[str]]`
- `extract_spec_sections(self) -> Set[str]`
- `validate_spec_section_coverage(self) -> Tuple[bool, List[str]]`
- `calculate_overall_score(self) -> float`
- `run_all_checks(self) -> Dict[str, any]`
- `print_report(self, results: Dict[str, any])`


- `main()`


## validation_suite

### `ValidationSuite`


- `validate_prerequisites(self) -> bool`
- `run_ast_validation(self) -> Dict[str, any]`
- `run_data_flow_validation(self) -> Dict[str, any]`
- `run_traceability_validation(self) -> Dict[str, any]`
- `run_layer_mapping_validation(self) -> Dict[str, any]`
- `print_final_report(self)`
- `run_all(self, legacy_file: Path) -> bool`


- `main()`


## version_manager

### `VersionInfo`




### `VersionManager`


- `get_cortex_version(self) -> str`
- `get_planning_system_version(self) -> str`
- `get_orchestrator_version(self, orchestrator_name: str) -> str`
- `register_orchestrator_version(self, orchestrator_name: str, version: str) -> None`
- `get_version_info(self) -> VersionInfo`
- `refresh(self) -> None`
- `validate_consistency(self) -> Dict[str, Any]`
- `get_version_string(self, include_orchestrators: bool) -> str`


- `get_version_manager(config_path: Optional[Path]) -> VersionManager`
- `get_cortex_version() -> str`
- `get_planning_system_version() -> str`


## __init__



## architecture_diagram_generator

### `ArchitectureDiagramGenerator`


- `generate_layer_diagram(self) -> str`
- `generate_component_diagram(self, component: str) -> str`




## dependency_graph_generator

### `DependencyNode`




### `DependencyGraphGenerator`


- `generate_module_graph(self, target_path: Path, format: str) -> str`
- `detect_circular_dependencies(self) -> str`




## progress_visualizer

### `ProgressVisualizer`


- `generate_progress_bar(self, current: int, total: int, width: int) -> str`
- `generate_phase_timeline(self, phases: List[Dict[str, Any]]) -> str`
- `generate_metrics_chart(self, metrics: Dict[str, Any]) -> str`
- `generate_completion_summary(self, total_phases: int, completed_phases: int, in_progress_phases: int, pending_phases: int) -> str`




## __init__



## application_metrics

### `ApplicationMetricsCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## commit_metrics

### `CommitMetricsCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## cortex_performance

### `CortexPerformanceCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## crawler_performance

### `CrawlerPerformanceCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## development_hygiene

### `DevelopmentHygieneCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## knowledge_graph

### `KnowledgeGraphCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## tdd_mastery

### `TDDMasteryCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## velocity_metrics

### `VelocityMetricsCollector`


- `collect(self, project_root: Path) -> Dict[str, Any]`




## __init__



## base_agent

### `AgentMetrics`


- `average_execution_time(self) -> float`
- `success_rate(self) -> float`


### `BaseAgent`
 (inherits: ABC)


- `execute_with_metrics(self, operation_name: str, operation_func, *args, **kwargs)`
- `get_health_status(self) -> Dict[str, Any]`
- `process(self, *args, **kwargs)`


### `MetricsCollector`


- `register_agent(self, agent: BaseAgent)`
- `get_aggregate_metrics(self) -> Dict[str, Any]`




## brain_ingestion_adapter_agent

### `BrainIngestionAdapterAgent`
 (inherits: BrainIngestionAgent)


- `ingest_feature(self, feature_description: str) -> BrainData`




## brain_ingestion_agent

### `BrainIngestionAgentImpl`
 (inherits: BrainIngestionAgent)


- `ingest_feature(self, feature_description: str) -> BrainData`


- `create_brain_ingestion_agent(cortex_root: str) -> BrainIngestionAgentImpl`
- `test_brain_ingestion()`


## documentation_intelligence_system

### `DocumentationGap`




### `DocumentationUpdate`




### `CrossReference`




### `DocumentationUpdates`




### `DocumentationGapAnalyzer`


- `analyze_gaps(self, implementation_data: ImplementationData) -> List[DocumentationGap]`


### `ContentGenerator`


- `generate_api_documentation(self, endpoints: List[APIEndpoint]) -> Dict[str, str]`
- `generate_class_documentation(self, classes: List[CodeElement]) -> Dict[str, str]`
- `generate_example_code(self, implementation_data: ImplementationData) -> List[str]`


### `CrossReferenceManager`


- `update_cross_references(self, implementation_data: ImplementationData) -> Tuple[List[CrossReference], List[CrossReference]]`


### `DocumentationIntelligenceSystem`


- `generate_documentation_updates(self, implementation_data: ImplementationData) -> DocumentationUpdates`




## feature_completion_orchestrator

### `Entity`




### `Pattern`




### `ContextUpdate`




### `ImplementationScan`




### `BrainData`


- `get_feature_fingerprint(self) -> str`


### `CodeChange`




### `APIChange`




### `TestAnalysis`




### `GitAnalysis`




### `ImplementationData`


- `change_impact_score(self) -> float`


### `DocumentationGap`




### `ContentUpdate`




### `CrossRefUpdate`




### `DocumentationUpdates`




### `MermaidDiagram`




### `ArchitectureDiagram`




### `ImagePrompt`




### `VisualAssets`




### `PerformanceAnalysis`




### `ArchitectureReview`




### `SecurityReview`




### `OptimizationRecommendation`




### `HealthReport`




### `AlignmentReport`


- `generate_summary(self) -> str`


### `BrainIngestionAgent`
 (inherits: ABC)


- `ingest_feature(self, feature_description: str) -> BrainData`


### `ImplementationDiscoveryEngine`
 (inherits: ABC)


- `scan_implementation(self, brain_data: BrainData) -> ImplementationData`


### `DocumentationIntelligenceSystem`
 (inherits: ABC)


- `analyze_and_update(self, brain_data: BrainData, implementation_data: ImplementationData) -> DocumentationUpdates`


### `VisualAssetGenerator`
 (inherits: ABC)


- `create_assets(self, brain_data: BrainData, implementation_data: ImplementationData, doc_updates: DocumentationUpdates) -> VisualAssets`


### `OptimizationHealthMonitor`
 (inherits: ABC)


- `validate_system(self, brain_data: BrainData, implementation_data: ImplementationData) -> HealthReport`


### `FeatureCompletionOrchestrator`
 (inherits: BaseAgent)


- `detect_feature_completion(self, user_input: str) -> Optional[str]`
- `orchestrate_feature_completion(self, feature_description: str) -> AlignmentReport`


- `integrate_with_intent_router()`
- `create_fco_instance() -> FeatureCompletionOrchestrator`
- `create_mock_fco_for_testing() -> FeatureCompletionOrchestrator`


## feature_completion_orchestrator_concrete

### `ImplementationDiscoveryAdapterEngine`
 (inherits: AbstractImplementationDiscoveryEngine)


- `scan_implementation(self, brain_data: BrainData) -> ImplementationData`


### `DocumentationIntelligenceAdapterSystem`
 (inherits: AbstractDocumentationIntelligenceSystem)


- `analyze_and_update(self, brain_data: BrainData, implementation_data: ImplementationData) -> DocumentationUpdates`


### `VisualAssetAdapterGenerator`
 (inherits: AbstractVisualAssetGenerator)


- `create_assets(self, brain_data: BrainData, implementation_data: ImplementationData, doc_updates: DocumentationUpdates) -> VisualAssets`


### `OptimizationHealthAdapterMonitor`
 (inherits: AbstractOptimizationHealthMonitor)


- `validate_system(self, brain_data: BrainData, implementation_data: ImplementationData) -> HealthReport`


### `ConcreteFeatureCompletionOrchestrator`
 (inherits: FeatureCompletionOrchestrator)


- `quick_feature_completion(self, feature_description: str) -> AlignmentReport`
- `health_check(self) -> dict`


### `FeatureCompletionOrchestratorFactory`


- `create_orchestrator(workspace_path: str, orchestrator_type: str) -> FeatureCompletionOrchestrator`
- `create_for_workspace(workspace_path: str) -> FeatureCompletionOrchestrator`


### `MockFeatureCompletionOrchestrator`
 (inherits: FeatureCompletionOrchestrator)


- `orchestrate_feature_completion(self, feature_description: str) -> AlignmentReport`


- `main()`


## feedback_agent

### `FeedbackAgent`


- `create_feedback_report(self, user_input: str, feedback_type: str, severity: str, context: Optional[Dict[str, Any]], auto_upload: bool) -> Dict[str, Any]`


- `handle_feedback_command(user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`


## implementation_discovery_engine

### `CodeElement`




### `FileChange`




### `APIEndpoint`




### `TestCase`




### `ImplementationData`




### `CodeScanner`


- `scan_python_files(self, file_paths: List[str]) -> List[CodeElement]`
- `scan_csharp_files(self, file_paths: List[str]) -> List[CodeElement]`


### `GitAnalyzer`


- `get_recent_changes(self, days_back: int) -> List[FileChange]`
- `get_files_changed_recently(self, days_back: int) -> List[str]`


### `TestAnalyzer`


- `discover_test_files(self) -> List[str]`
- `analyze_test_files(self, test_files: List[str]) -> List[TestCase]`


### `APIDiscoverer`


- `discover_endpoints(self, source_files: List[str]) -> List[APIEndpoint]`


### `ImplementationDiscoveryEngine`


- `discover_implementation(self, feature_name: str) -> ImplementationData`




## namespace_detector

### `NamespaceType`
 (inherits: Enum)




### `ContextCue`




### `NamespaceDetectionResult`




### `NamespaceDetector`


- `detect_namespace(self, user_message: str, conversation_history: Optional[List[str]], current_files: Optional[List[str]]) -> NamespaceDetectionResult`
- `detect(self, user_message: str, context: Dict) -> 'NamespaceResult'`


### `NamespaceResult`






## optimization_health_monitor

### `CodeQualityIssue`




### `PerformanceMetric`




### `SecurityFinding`




### `OptimizationRecommendation`




### `HealthReport`




### `CodeQualityAnalyzer`


- `analyze_quality(self, implementation_data: ImplementationData) -> Tuple[float, List[CodeQualityIssue]]`


### `PerformanceAnalyzer`


- `analyze_performance(self, implementation_data: ImplementationData) -> Tuple[float, List[PerformanceMetric]]`


### `SecurityAnalyzer`


- `analyze_security(self, implementation_data: ImplementationData) -> Tuple[float, List[SecurityFinding]]`


### `OptimizationRecommendationEngine`


- `generate_recommendations(self, quality_issues: List[CodeQualityIssue], performance_metrics: List[PerformanceMetric], security_findings: List[SecurityFinding]) -> List[OptimizationRecommendation]`


### `OptimizationHealthMonitor`


- `generate_health_report(self, implementation_data: ImplementationData) -> HealthReport`




## view_discovery_agent

### `ElementMapping`


- `to_dict(self) -> Dict[str, Any]`


### `NavigationFlow`




### `ViewDiscoveryAgent`


- `discover_views(self, view_paths: List[Path], output_path: Optional[Path], save_to_db: bool, project_name: Optional[str]) -> Dict[str, Any]`
- `save_to_database(self, project_name: str, elements: List[Dict[str, Any]]) -> bool`
- `load_from_database(self, project_name: str, component_path: Optional[str]) -> List[Dict[str, Any]]`


- `discover_views_for_testing(view_directory: Path, pattern: str, output_file: Optional[Path]) -> Dict[str, Any]`


## visual_asset_generator

### `MermaidDiagram`




### `ImagePrompt`




### `VisualAssets`




### `MermaidDiagramGenerator`


- `generate_class_diagrams(self, classes: List[CodeElement]) -> List[MermaidDiagram]`
- `generate_api_sequence_diagrams(self, endpoints: List[APIEndpoint]) -> List[MermaidDiagram]`
- `generate_architecture_diagrams(self, implementation_data: ImplementationData) -> List[MermaidDiagram]`


### `ImagePromptGenerator`


- `generate_architecture_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]`
- `generate_ui_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]`
- `generate_concept_prompts(self, implementation_data: ImplementationData) -> List[ImagePrompt]`


### `VisualAssetGenerator`


- `generate_visual_assets(self, implementation_data: ImplementationData) -> VisualAssets`




## clarification_orchestrator

### `ClarificationOrchestrator`


- `should_clarify(self, validator_result: Dict[str, Any]) -> bool`
- `generate_clarification_prompt(self, validator_result: Dict[str, Any]) -> str`
- `parse_user_response(self, user_response: str) -> Dict[str, Any]`
- `increment_round(self)`
- `get_current_round(self) -> int`
- `can_continue_clarification(self) -> bool`
- `should_stop_clarification(self, validator_result: Dict[str, Any]) -> bool`
- `reset(self)`
- `run_clarification_workflow(self, initial_requirements: str, initial_validation: Dict[str, Any], max_iterations: Optional[int]) -> Dict[str, Any]`




## dor_validator

### `DoRStatus`
 (inherits: Enum)




### `DoRCriterion`
 (inherits: Enum)




### `DoRCriterionStatus`




### `DoRValidationResult`


- `completion_percentage(self) -> float`
- `to_dict(self) -> Dict[str, Any]`


### `DoRValidator`


- `validate_dor(self, requirements: str, context: Optional[Dict[str, Any]]) -> DoRValidationResult`
- `get_dor_checklist_display(self, result: DoRValidationResult) -> str`
- `is_ready_for_estimation(self, result: DoRValidationResult) -> bool`
- `get_missing_criteria(self, result: DoRValidationResult) -> List[str]`
- `get_clarifying_questions(self, result: DoRValidationResult) -> List[str]`
- `update_criterion(self, criterion: DoRCriterion, satisfied: bool, evidence: str, notes: str) -> None`
- `revalidate(self) -> DoRValidationResult`




## scope_inference_engine

### `ScopeEntities`




### `ScopeBoundary`


- `approve_scope(self, method: str) -> None`
- `is_approval_required(self) -> bool`


### `ScopeInferenceEngine`


- `parse_dor_answers(self, dor_responses: Dict[str, str]) -> str`
- `extract_entities(self, requirements_text: str) -> ScopeEntities`
- `calculate_confidence(self, entities: ScopeEntities, requirements_text: str) -> float`
- `generate_scope_boundary(self, entities: ScopeEntities, confidence: float) -> ScopeBoundary`




## scope_validator

### `ValidationSeverity`
 (inherits: Enum)




### `ValidationRule`




### `ValidationResult`




### `ScopeValidator`


- `validate_scope(self, boundary: ScopeBoundary) -> ValidationResult`
- `generate_clarification_questions(self, validation_result: ValidationResult, boundary: ScopeBoundary) -> List[str]`




## timeframe_estimator

### `ParallelTrack`




### `TimeEstimate`




### `TimeframeEstimator`


- `estimate_timeframe(self, complexity: float, scope: Optional[Dict], team_size: int, velocity: Optional[float]) -> TimeEstimate`
- `generate_timeline_comparison(self, estimate: 'TimeEstimate', hourly_rate: float) -> Dict[str, any]`
- `generate_what_if_scenarios(self, complexity: float, scope: Optional[Dict], team_sizes: List[int], hourly_rate: float) -> Dict[str, any]`
- `format_professional_report(self, estimate: 'TimeEstimate', include_timeline: bool, include_cost: bool, hourly_rate: float) -> str`
- `estimate_three_point(self, complexity: float, scope: Optional[Dict], team_size: int) -> Dict[str, TimeEstimate]`
- `format_estimate_report(self, estimate: TimeEstimate, include_breakdown: bool) -> str`


- `quick_estimate(complexity: float, team_size: int) -> str`


## work_decomposer

### `WorkItemType`
 (inherits: Enum)




### `StoryPointScale`
 (inherits: Enum)




### `ADOWorkItem`


- `to_ado_dict(self) -> Dict[str, Any]`
- `to_markdown(self) -> str`


### `DecompositionResult`


- `to_dict(self) -> Dict[str, Any]`
- `to_markdown_report(self) -> str`


### `WorkDecomposer`


- `decompose_work(self, title: str, description: str, complexity_score: float, requirements: Optional[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> DecompositionResult`
- `format_for_ado_board(self, result: DecompositionResult, include_hierarchy: bool) -> str`




## __init__



## threat_modeler_agent

### `RiskRating`
 (inherits: Enum)




### `OWASPCategory`
 (inherits: Enum)




### `MitigationStrategy`




### `EnhancedThreat`


- `risk_score(self) -> int`


### `ThreatReport`


- `critical_threats(self) -> List[EnhancedThreat]`
- `high_threats(self) -> List[EnhancedThreat]`


### `ThreatModelerAgent`
 (inherits: BaseAgent)


- `can_handle(self, request: AgentRequest) -> bool`
- `execute(self, request: AgentRequest) -> AgentResponse`
- `process(self, feature_requirements: str, feature_type: str, context: Optional[Dict[str, Any]]) -> ThreatReport`


- `create_agent() -> ThreatModelerAgent`


## __init__



## brain_context_injector

### `BrainContextInjector`


- `inject_tier1_context(self, user_request: str, max_conversations: int) -> Dict[str, Any]`
- `inject_tier2_context(self, user_request: str, max_patterns: int) -> Dict[str, Any]`
- `inject_tier3_context(self, current_file: Optional[str]) -> Dict[str, Any]`
- `inject_full_context(self, user_request: str, current_file: Optional[str], max_tokens: int) -> Dict[str, Any]`




## brain_health_monitor

### `BrainHealthMonitor`


- `check_health(self) -> Dict[str, Any]`
- `check_tier1(self) -> Dict[str, Any]`
- `check_tier2(self) -> Dict[str, Any]`
- `check_tier3(self) -> Dict[str, Any]`
- `generate_report(self) -> str`
- `display_dashboard(self)`
- `get_performance_metrics(self) -> Dict[str, float]`




## brain_protection_loader

- `load_brain_protection_rules(rules_path: Optional[Path], force_reload: bool) -> Dict[str, Any]`
- `get_cache_stats() -> Dict[str, Any]`
- `clear_cache()`
- `reset_cache_stats()`
- `is_cached() -> bool`
- `get_cache_age_seconds() -> Optional[float]`
- `patch_brain_protector()`
- `unpatch_brain_protector()`


## brain_protector

### `Severity`
 (inherits: Enum)




### `ProtectionLayer`
 (inherits: Enum)




### `Violation`




### `ModificationRequest`




### `ProtectionResult`




### `Challenge`




### `BrainProtector`


- `analyze_request(self, request: ModificationRequest) -> ProtectionResult`
- `generate_challenge(self, violations: List[Violation]) -> Challenge`
- `log_event(self, challenge: Challenge, user_decision: str, override_justification: Optional[str])`




## cleanup_hook

### `ArchiveDecision`
 (inherits: str, Enum)




### `CleanupAction`




### `SmartCleanupHook`


- `enforce_structure(self) -> List[CleanupAction]`
- `analyze_file(self, file_path: Path) -> ArchiveDecision`
- `archive_file(self, file_path: Path) -> None`
- `move_with_reference_updates(self, src: Path, dst: Path) -> None`




## context_optimizer

### `ContextOptimizer`


- `optimize_context(self, intent: str, query: str, available_tiers: Dict[str, Any]) -> Dict[str, Any]`


### `PatternRelevanceScorer`


- `score_patterns(self, patterns: List[Dict], query: str, limit: int) -> List[Dict]`


### `ContextCompressor`


- `compress(self, context: Dict[str, Any], target_reduction: float) -> Tuple[Dict, Dict]`




## cortex_implants_integrator

### `CortexImplantsIntegrator`


- `has_implants(self) -> bool`
- `get_priority(self) -> str`
- `should_override_cortex(self) -> bool`
- `get_coding_standards(self) -> Optional[Dict[str, Any]]`
- `get_architecture_patterns(self) -> Optional[Dict[str, Any]]`
- `get_tech_stack_restrictions(self) -> Optional[Dict[str, Any]]`
- `get_business_rules(self) -> Optional[List[Dict[str, Any]]]`
- `get_security_requirements(self) -> Optional[Dict[str, Any]]`
- `validate_tech_stack(self, dependencies: List[str]) -> List[str]`
- `validate_architecture(self, plan: Dict[str, Any]) -> List[str]`
- `get_context_summary(self) -> str`


- `get_implants_integrator(repo_path: Optional[Path]) -> CortexImplantsIntegrator`
- `has_cortex_implants(repo_path: Optional[Path]) -> bool`


## cortex_implants_loader

### `EnforcementLevel`
 (inherits: Enum)




### `RepositoryType`
 (inherits: Enum)




### `ImplantGovernance`


- `is_rule_enabled(self, rule_name: str) -> bool`


### `CodingStandards`




### `ArchitecturePatterns`




### `BusinessRules`




### `TechStack`




### `SecurityPolicy`




### `CortexImplants`


- `is_rule_enabled(self, rule_name: str) -> bool`
- `get_priority(self) -> str`


### `CortexImplantsLoader`


- `load(self, repo_path: Path) -> Optional[CortexImplants]`
- `clear_cache(self, repo_path: Optional[Path]) -> None`
- `get_all_repos_with_cortex_implants(self, workspace_root: Path) -> List[CortexImplants]`


- `get_cortex_implants_loader() -> CortexImplantsLoader`
- `load_cortex_implants(repo_path: Path) -> Optional[CortexImplants]`


## coverage_reporter

### `CoverageStatus`
 (inherits: Enum)




### `CoverageMetrics`




### `CoverageReport`




### `CoverageReporter`


- `run_coverage(self, test_pattern: Optional[str], show_missing: bool) -> CoverageReport`
- `generate_markdown_report(self, report: CoverageReport) -> str`


- `run_coverage_analysis(test_pattern: Optional[str], threshold: float) -> bool`


## git_isolation

### `GitIsolationEnforcer`


- `install_hooks(self) -> bool`
- `check_staged_files(self) -> Tuple[bool, List[str]]`
- `uninstall_hooks(self) -> bool`


- `install_git_isolation_hooks(user_repo_path: Path) -> bool`
- `check_git_isolation(user_repo_path: Path) -> Tuple[bool, List[str]]`


## governance_engine

### `Severity`
 (inherits: Enum)




### `ViolationType`
 (inherits: Enum)




### `GovernanceEngine`


- `get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]`
- `get_all_rules(self) -> List[Dict[str, Any]]`
- `get_rules_by_severity(self, severity: Severity) -> List[Dict[str, Any]]`
- `check_tdd_violation(self, has_new_code: bool, has_new_test: bool, test_written_first: bool) -> Optional[Dict[str, Any]]`
- `validate_definition_of_done(self, compilation_clean: bool, tests_pass: bool, new_tests_created: bool, tdd_cycle_complete: bool, code_formatted: bool, no_lint_violations: bool, docs_updated: bool, app_runs: bool, no_exceptions: bool, functionality_verified: bool) -> Dict[str, Any]`
- `validate_definition_of_ready(self, user_story_clear: bool, acceptance_criteria_defined: bool, testable_outcomes: bool, scope_bounded: bool, dependencies_identified: bool, estimate_possible: bool, files_known: bool, architecture_clear: bool, no_blocking_dependencies: bool) -> Dict[str, Any]`
- `check_tier_boundary_violation(self, tier: int, data_type: str) -> Optional[Dict[str, Any]]`
- `create_challenge(self, proposed_change: str, risks: List[str], alternatives: Optional[List[str]]) -> Dict[str, Any]`
- `get_violations(self, severity: Optional[Severity], limit: Optional[int]) -> List[Dict[str, Any]]`
- `clear_violations(self) -> None`




## integrity_checker

### `IntegrityStatus`
 (inherits: Enum)




### `IntegrityIssue`




### `IntegrityReport`




### `IntegrityChecker`


- `check_all(self) -> IntegrityReport`
- `generate_report(self, integrity_report: IntegrityReport) -> str`


- `check_brain_integrity(auto_repair: bool) -> bool`


## optimized_context_loader

### `OptimizedContextLoader`


- `load_optimized_context(self, intent: str, query: str, available_tiers: Dict[str, Any], compression_enabled: bool) -> Dict[str, Any]`
- `get_metrics(self) -> Dict[str, Any]`
- `reset_metrics(self)`




## repo_boundary_enforcer

### `RepoBoundaryViolation`
 (inherits: Exception)




### `RepoBoundaryEnforcer`


- `get_repo_root(self, path: Path) -> Optional[Path]`
- `validate_operation(self, source_repo: Path, target_path: Path, operation: str) -> bool`
- `validate_import(self, source_file: Path, import_path: str) -> bool`
- `check_cortex_implants_leakage(self, source_repo: Path, search_path: Path) -> bool`
- `get_violations_report(self) -> str`
- `save_violations_log(self, output_file: Path) -> None`
- `get_repo_inventory(self) -> Dict[str, any]`
- `print_repo_inventory(self) -> None`


- `get_repo_boundary_enforcer(workspace_root: Path) -> RepoBoundaryEnforcer`
- `validate_cross_repo_operation(source_repo: Path, target_path: Path, operation: str) -> bool`


## schema_version_tracker

### `SchemaVersionTracker`


- `get_version(self, tier: str) -> int`
- `set_version(self, tier: str, version: int)`
- `needs_migration(self, tier: str, target_version: int) -> bool`
- `get_version_history(self, tier: str) -> List[Dict[str, Any]]`
- `record_migration(self, tier: str, from_version: int, to_version: int, description: str)`
- `get_applied_migrations(self, tier: str) -> List[Dict[str, Any]]`
- `get_latest_versions(self) -> Dict[str, int]`




## skull_protector

### `SkullRuleId`
 (inherits: Enum)




### `EnforcementLevel`
 (inherits: Enum)




### `SkullValidation`




### `FixValidationRequest`




### `SkullProtector`


- `validate_fix(self, request: FixValidationRequest) -> SkullValidation`


### `SkullProtectionError`
 (inherits: Exception)




- `enforce_skull(request: FixValidationRequest) -> SkullValidation`


## tier_validator

### `TierLevel`
 (inherits: Enum)




### `ValidationSeverity`
 (inherits: Enum)




### `TierViolation`




### `TierValidationResult`




### `TierValidator`


- `validate_all_tiers(self) -> Dict[TierLevel, TierValidationResult]`
- `validate_tier(self, tier: TierLevel) -> TierValidationResult`
- `generate_report(self, results: Dict[TierLevel, TierValidationResult]) -> str`


- `validate_brain_tiers() -> bool`


## __init__



## cache_monitor

### `CacheMonitor`


- `check_cache_health(self) -> Dict[str, Any]`
- `get_trim_recommendations(self) -> List[Dict[str, Any]]`
- `get_statistics(self) -> Dict[str, Any]`
- `reset_statistics(self) -> None`


### `CacheHealthReport`


- `generate_report(self) -> Dict[str, Any]`




## context_formatter

### `ContextFormatter`


- `format_recent_conversations(self, conversations: List[Dict]) -> str`
- `extract_active_entities(self, conversations: List[Dict]) -> Dict[str, Any]`
- `resolve_pronouns(self, user_request: str, active_entities: Dict) -> str`
- `format_context_summary(self, conversations: List[Dict], active_entities: Dict, include_header: bool) -> str`




## context_injection_helper

- `get_context_injector() -> ContextInjector`
- `inject_tier1_context(user_request: str, conversation_id: Optional[str]) -> Dict`
- `inject_full_context(user_request: str, conversation_id: Optional[str], current_file: Optional[str]) -> Dict`
- `resolve_pronoun_only(user_request: str) -> str`
- `get_context_display(user_request: str) -> str`
- `get_last_injection_time() -> float`
- `is_injection_performance_ok() -> bool`


## conversation_auto_capture

### `ConversationAutoCapture`


- `should_capture_conversation(self, messages: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Tuple[bool, float, str]`
- `capture_conversation(self, conversation_id: str, title: str, messages: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> bool`
- `get_capture_stats(self) -> Dict[str, Any]`




## conversation_manager

### `ConversationManager`


- `create_conversation(self, agent_id: str, goal: Optional[str], context: Optional[Dict]) -> str`
- `add_message(self, conversation_id: str, role: str, content: str) -> str`
- `add_entity(self, conversation_id: str, entity_type: str, entity_value: str)`
- `add_file(self, conversation_id: str, file_path: str, operation: str)`
- `end_conversation(self, conversation_id: str, outcome: Optional[str])`
- `get_conversation(self, conversation_id: str) -> Optional[Dict]`
- `get_active_conversation(self, agent_id: str) -> Optional[Dict]`
- `get_active_conversations(self) -> List[str]`
- `get_messages(self, conversation_id: str) -> List[Dict]`
- `get_entities(self, conversation_id: str, entity_type: Optional[str]) -> List[Dict]`
- `get_files(self, conversation_id: str) -> List[Dict]`
- `get_statistics(self) -> Dict`
- `get_recent_conversations(self, limit: int) -> List[Dict]`
- `search_conversations(self, agent_id: Optional[str], start_date: Optional[datetime], end_date: Optional[datetime], has_goal: Optional[bool]) -> List[Dict]`
- `get_conversation_count(self) -> int`
- `get_message_count(self, conversation_id: Optional[str]) -> int`
- `export_conversation_jsonl(self, conversation_id: str) -> str`
- `export_to_jsonl(self, conversation_id: str, output_path: Path)`
- `save_planning_session(self, session_data: Dict) -> bool`
- `load_planning_session(self, session_id: str) -> Optional[Dict]`
- `list_planning_sessions(self, state: Optional[str], limit: int) -> List[Dict]`




## conversation_memory

### `ConversationMemory`


- `store_conversation(self, user_message: str, assistant_response: str, intent: str, context: Dict[str, Any]) -> str`
- `get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]`
- `get_recent_conversations(self, limit: int) -> List[Dict[str, Any]]`
- `search_conversations(self, query: str, limit: int) -> List[Dict[str, Any]]`
- `track_entity(self, conversation_id: str, entity_type: str, entity_value: str, context: str)`
- `get_entities(self, conversation_id: str) -> List[Dict[str, Any]]`
- `get_queue_status(self) -> Dict[str, Any]`




## conversation_quality

### `SemanticElements`




### `QualityScore`




### `ConversationQualityAnalyzer`


- `analyze_conversation(self, user_prompt: str, assistant_response: str) -> QualityScore`
- `analyze_multi_turn_conversation(self, turns: List[Tuple[str, str]]) -> QualityScore`


- `create_analyzer(config: Dict) -> ConversationQualityAnalyzer`


## conversation_vault

### `ConversationMetadata`




### `ConversationTurn`




### `ConversationVaultManager`


- `create_conversation_file(self, metadata: ConversationMetadata, turns: List[ConversationTurn], filename: str) -> Path`
- `get_conversation_by_id(self, conv_id: str) -> Optional[Path]`
- `list_conversations(self, quality_filter: Optional[str], limit: int) -> List[Dict]`
- `get_vault_stats(self) -> Dict`


- `create_vault_manager(config: Dict) -> ConversationVaultManager`


## entity_extractor

### `EntityExtractor`


- `extract_all(self, text: str) -> Dict[str, List[str]]`
- `extract_files(self, text: str) -> List[str]`
- `extract_intents(self, text: str) -> List[str]`
- `extract_technical_terms(self, text: str) -> List[Dict[str, any]]`
- `extract_features(self, text: str) -> List[str]`
- `extract_entities_list(self, text: str) -> List[str]`
- `extract_from_messages(self, messages: List[Dict]) -> List[str]`
- `get_entity_frequency(self, text: str) -> Dict[str, int]`




## file_tracker

### `FileTracker`


- `extract_files_from_text(self, text: str) -> List[str]`
- `track_file_modifications(self, before_text: str, after_text: str) -> List[str]`
- `get_file_patterns(self, files: List[str]) -> Dict[str, List[str]]`
- `get_directory_hierarchy(self, files: List[str]) -> Dict[str, int]`
- `get_file_statistics(self, files: List[str]) -> Dict`
- `format_file_list(self, files: List[str], max_files: int) -> str`




## fusion_manager

### `FusionManager`


- `correlate_imported_conversation(self, conversation_id: str, auto_correlate: bool) -> Dict[str, Any]`
- `get_conversation_development_story(self, conversation_id: str) -> Dict[str, Any]`
- `get_fusion_insights(self, conversation_id: str, include_recommendations: bool) -> Dict[str, Any]`




## image_detector

### `ImageAttachment`




### `ImageDetector`


- `detect(self, user_request: str, attachments: Optional[List[Dict]]) -> List[ImageAttachment]`
- `has_images(self, user_request: str, attachments: Optional[List[Dict]]) -> bool`
- `get_image_context_summary(self, images: List[ImageAttachment]) -> str`




## migrate_tier1

### `Tier1Migrator`


- `create_schema(self, conn: sqlite3.Connection)`
- `migrate_conversation(self, conn: sqlite3.Connection, conv_data: Dict) -> bool`
- `migrate(self) -> Dict`


- `main()`


## migration_add_conversation_import

- `migrate_add_conversation_import(db_path: str)`
- `verify_migration(db_path: str)`


## migration_add_sessions

- `migrate_tier1_add_sessions(db_path: Path) -> bool`
- `main()`


## ml_context_optimizer

### `MLContextOptimizer`


- `optimize_conversation_context(self, conversations: List[Dict[str, Any]], current_intent: str, min_conversations: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]`
- `optimize_pattern_context(self, patterns: List[Dict[str, Any]], query: str, max_patterns: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]`
- `get_statistics(self) -> Dict[str, Any]`




## narrative_intelligence

### `StoryType`
 (inherits: Enum)




### `NarrativeStyle`
 (inherits: Enum)




### `StoryElement`




### `DevelopmentNarrative`




### `NarrativeIntelligence`


- `add_story_element(self, element: StoryElement) -> bool`
- `generate_development_story(self, time_range: Tuple[datetime, datetime], story_type: StoryType, narrative_style: NarrativeStyle, focus_files: List[str]) -> DevelopmentNarrative`
- `get_recent_narratives(self, limit: int) -> List[DevelopmentNarrative]`
- `get_narrative_statistics(self) -> Dict[str, Any]`
- `import_conversation_data(self, conversation_data: Dict[str, Any]) -> bool`




## pattern_learning_engine

### `PatternType`
 (inherits: Enum)




### `CorrelationPattern`




### `LearningSession`




### `PatternLearningEngine`


- `learn_from_correlation(self, correlation_result: Dict[str, Any]) -> LearningSession`
- `suggest_files_for_conversation(self, conversation_text: str, conversation_metadata: Dict[str, Any]) -> List[Dict[str, Any]]`
- `boost_confidence_from_patterns(self, correlation_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]`
- `get_learning_statistics(self) -> Dict[str, Any]`
- `export_patterns(self, output_file: str) -> bool`




## planning_doc_sync

### `PlanningDocSyncEngine`


- `sync_planning_doc(self, conversation_id: str, conversation_manager, force: bool) -> Optional[Path]`




## relevance_scorer

### `RelevanceScorer`


- `score_conversation_relevance(self, conversation: Dict, current_request: str, current_file: Optional[str], active_entities: Optional[Dict[str, List[str]]]) -> float`
- `rank_conversations(self, conversations: List[Dict], current_request: str, current_file: Optional[str], active_entities: Optional[Dict[str, List[str]]], top_n: int) -> List[tuple]`




## request_logger

### `RequestLogger`


- `log_request(self, request_text: str, conversation_id: Optional[str], intent: Optional[str], metadata: Optional[Dict]) -> str`
- `log_response(self, request_id: str, response_text: str, conversation_id: Optional[str], status: str, metadata: Optional[Dict])`
- `log_error(self, request_id: str, error_message: str, conversation_id: Optional[str], error_type: Optional[str], metadata: Optional[Dict])`
- `get_recent_requests(self, limit: int) -> list`
- `get_request_response_pair(self, request_id: str) -> Dict`
- `get_conversation_requests(self, conversation_id: str) -> list`
- `get_statistics(self) -> Dict`




## response_context_integration

### `ResponseContextIntegration`


- `inject_context_summary(response: str, context_data: Optional[Dict[str, Any]]) -> str`
- `should_show_context(context_data: Optional[Dict[str, Any]]) -> bool`




## schema_migrations

### `SchemaMigration`




### `MigrationManager`


- `register_migration(self, migration: SchemaMigration)`
- `apply_migration(self, version: str) -> bool`
- `rollback_migration(self, version: str) -> bool`
- `get_current_version(self) -> str`
- `list_applied_migrations(self) -> List[Dict[str, Any]]`
- `list_pending_migrations(self) -> List[SchemaMigration]`
- `apply_all_pending(self) -> Dict[str, bool]`
- `get_migration_history(self) -> List[Dict[str, Any]]`




## session_correlation

### `SessionAmbientCorrelator`


- `log_ambient_event(self, session_id: str, event_type: str, file_path: Optional[str], pattern: Optional[str], score: Optional[int], summary: Optional[str], conversation_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> int`
- `get_session_events(self, session_id: str, event_type: Optional[str], min_score: Optional[int]) -> List[Dict[str, Any]]`
- `get_conversation_events(self, conversation_id: str) -> List[Dict[str, Any]]`
- `generate_session_narrative(self, session_id: str) -> str`




## session_token

### `SessionStatus`
 (inherits: Enum)




### `Session`


- `to_dict(self) -> Dict[str, Any]`
- `is_stale(self, hours: int) -> bool`
- `age_hours(self) -> float`


### `SessionTokenManager`


- `create_session(self, description: str, conversation_id: Optional[str], work_session_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> str`
- `get_session(self, token: str) -> Optional[Session]`
- `get_active_session(self) -> Optional[Session]`
- `associate_conversation(self, token: str, conversation_id: str) -> None`
- `associate_work_session(self, token: str, work_session_id: str) -> None`
- `update_activity(self, token: str) -> None`
- `pause_session(self, token: str) -> None`
- `resume_session(self, token: str) -> None`
- `complete_session(self, token: str) -> None`
- `expire_session(self, token: str) -> None`
- `get_all_active_sessions(self) -> List[Session]`
- `cleanup_stale_sessions(self, hours: int) -> int`
- `find_by_conversation(self, conversation_id: str) -> Optional[Session]`
- `find_by_work_session(self, work_session_id: str) -> Optional[Session]`
- `get_statistics(self) -> Dict[str, Any]`




## smart_hint_generator

### `SmartHint`




### `SmartHintGenerator`


- `generate_hint(self, quality: QualityScore, user_prompt: str) -> SmartHint`
- `generate_compact_hint(self, quality: QualityScore) -> Optional[str]`


- `create_hint_generator(config: dict) -> SmartHintGenerator`


## smart_hint_integration

### `SmartHintSystem`


- `analyze_and_generate_hint(self, user_prompt: str, assistant_response: str) -> SmartHint`
- `capture_conversation(self, user_prompt: str, assistant_response: str, conversation_id: Optional[str]) -> Tuple[Path, ConversationMetadata]`
- `capture_multi_turn_conversation(self, turns: list[Tuple[str, str]], topic: str) -> Tuple[Path, ConversationMetadata]`
- `get_vault_stats(self) -> Dict`
- `list_recent_conversations(self, limit: int) -> list`


- `get_smart_hint_system(config: Dict) -> SmartHintSystem`
- `analyze_response_for_hint(user_prompt: str, assistant_response: str) -> Optional[str]`
- `capture_current_conversation(user_prompt: str, assistant_response: str) -> str`


## smart_recommendations

### `FileRecommendation`




### `RecommendationContext`




### `RecommendationFeedback`




### `SmartRecommendations`


- `get_recommendations(self, context: RecommendationContext, max_results: int) -> List[FileRecommendation]`
- `record_file_access(self, file_path: str, conversation_id: str, access_type: str, context: str)`
- `record_feedback(self, feedback: RecommendationFeedback)`
- `get_recommendation_analytics(self, days: int) -> Dict[str, Any]`
- `optimize_recommendations(self)`




## temporal_correlator

### `CorrelationResult`




### `ConversationTurn`




### `AmbientEvent`




### `TemporalCorrelator`


- `correlate_conversation(self, conversation_id: str, force_recalculate: bool) -> List[CorrelationResult]`
- `get_conversation_timeline(self, conversation_id: str) -> Dict[str, Any]`




## tier1_api

### `Tier1API`


- `start_conversation(self, agent_id: str, goal: Optional[str], context: Optional[Dict]) -> str`
- `process_message(self, conversation_id: str, role: str, content: str, extract_entities: bool, track_files: bool, log_request: bool) -> Dict`
- `end_conversation(self, conversation_id: str, outcome: Optional[str]) -> Dict`
- `get_active_conversation(self, agent_id: str) -> Optional[Dict]`
- `get_conversation_history(self, conversation_id: str, include_entities: bool, include_files: bool) -> Dict`
- `search_conversations(self, agent_id: Optional[str], start_date: Optional[datetime], end_date: Optional[datetime], has_goal: Optional[bool]) -> List[Dict]`
- `extract_entities_from_text(self, text: str) -> Dict`
- `get_entity_frequency(self, conversation_id: str, entity_type: Optional[str]) -> Dict`
- `track_file_modification(self, conversation_id: str, file_path: str, operation: str)`
- `get_file_patterns(self, conversation_id: str) -> Dict`
- `log_response(self, request_id: str, response_text: str, status: str)`
- `log_error(self, request_id: str, error_message: str, error_type: Optional[str])`
- `get_request_history(self, conversation_id: Optional[str], limit: int) -> List[Dict]`
- `export_conversation_to_jsonl(self, conversation_id: str, output_path: Path)`
- `get_tier1_statistics(self) -> Dict`




## token_metrics

### `TokenMetricsCollector`


- `record_request(self, original_tokens: int, optimized_tokens: int, optimization_method: str, quality_score: Optional[float]) -> None`
- `get_current_metrics(self, force_refresh: bool) -> Dict[str, Any]`
- `get_session_summary(self) -> Dict[str, Any]`
- `get_request_history(self, limit: Optional[int]) -> List[Dict[str, Any]]`
- `export_session_data(self, output_path: Optional[Path]) -> Path`
- `reset_session(self) -> None`


### `TokenMetricsFormatter`


- `format_tokens(token_count: int) -> str`
- `format_cost(cost_usd: float) -> str`
- `format_percentage(percentage: float) -> str`
- `format_filesize(bytes_count: int) -> str`
- `format_duration(seconds: float) -> str`
- `format_metrics_summary(metrics: Dict[str, Any]) -> str`




## user_profile_governance

### `UserProfileGovernance`


- `has_acknowledged_rulebook(self) -> bool`
- `mark_rulebook_acknowledged(self) -> bool`
- `get_acknowledgment_status(self) -> Dict[str, Any]`
- `mark_onboarding_completed(self) -> bool`
- `reset_acknowledgment(self) -> bool`




## user_profile_manager

### `TechStackPreset`
 (inherits: Enum)


- `get_configuration(cls, preset: 'TechStackPreset') -> Optional[Dict[str, str]]`


### `UserProfileManager`


- `set_tech_stack_preset(self, preset: TechStackPreset) -> bool`
- `set_tech_stack_custom(self, config: Dict[str, str]) -> bool`
- `get_tech_stack_preference(self) -> Optional[Dict[str, str]]`
- `update_tech_stack_preset(self, preset: TechStackPreset) -> bool`
- `clear_tech_stack_preference(self) -> bool`
- `get_profile(self) -> Optional[Dict[str, Any]]`
- `set_response_detail(self, detail_level: str) -> bool`
- `get_response_detail(self) -> Optional[str]`
- `infer_response_detail_from_mode(self, interaction_mode: str) -> str`
- `set_testing_frameworks(self, frameworks: Dict[str, str]) -> bool`
- `get_testing_frameworks(self) -> Optional[Dict[str, str]]`
- `update_testing_framework(self, test_type: str, framework: str) -> bool`




## vision_api

### `VisionAPI`


- `analyze_image(self, image_data: str, prompt: str) -> Dict`
- `get_metrics(self) -> Dict`
- `clear_cache(self)`




## vision_orchestrator

### `VisionOrchestrator`


- `process_request(self, user_request: str, attachments: Optional[List[Dict]], context_type: str, custom_prompt: Optional[str]) -> Dict`
- `quick_check(self, user_request: str, attachments: Optional[List[Dict]]) -> bool`
- `get_metrics(self) -> Dict`
- `analyze_specific_image(self, image_data: str, prompt: str, context_type: str) -> Dict`




## working_memory

### `WorkingMemory`


- `initialize(self) -> bool`
- `get_optimized_context(self, conversation_id: Optional[str], pattern_context: Optional[List[Dict[str, Any]]], target_reduction: Optional[float]) -> Dict[str, Any]`
- `get_token_metrics_summary(self) -> Dict[str, Any]`
- `get_cache_health_report(self) -> Dict[str, Any]`
- `add_conversation(self, conversation_id: str, title: str, messages: List[Dict[str, str]], tags: Optional[List[str]]) -> Conversation`
- `get_conversation(self, conversation_id: str) -> Optional[Conversation]`
- `get_recent_conversations(self, limit: int) -> List[Conversation]`
- `set_active_conversation(self, conversation_id: str) -> None`
- `get_active_conversation(self) -> Optional[Conversation]`
- `update_conversation(self, conversation_id: str, title: Optional[str], summary: Optional[str], tags: Optional[List[str]]) -> None`
- `get_conversation_count(self) -> int`
- `detect_or_create_session(self, workspace_path: str) -> Session`
- `get_active_session(self, workspace_path: str) -> Optional[Session]`
- `end_session(self, session_id: str, reason: str) -> None`
- `get_session(self, session_id: str) -> Optional[Session]`
- `get_recent_sessions(self, workspace_path: Optional[str], limit: int) -> List[Session]`
- `handle_user_request(self, user_request: str, workspace_path: str, assistant_response: Optional[str], context: Optional[Dict[str, Any]]) -> Dict[str, Any]`
- `get_conversation_lifecycle_history(self, conversation_id: str)`
- `get_session_lifecycle_history(self, session_id: str)`
- `log_ambient_event(self, session_id: str, event_type: str, file_path: Optional[str], pattern: Optional[str], score: Optional[int], summary: Optional[str], conversation_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> int`
- `get_session_events(self, session_id: str, event_type: Optional[str], min_score: Optional[int]) -> List[Dict[str, Any]]`
- `get_conversation_events(self, conversation_id: str) -> List[Dict[str, Any]]`
- `generate_session_narrative(self, session_id: str) -> str`
- `import_conversation(self, conversation_turns: List[Dict[str, str]], import_source: str, workspace_path: Optional[str], import_date: Optional[datetime]) -> Dict[str, Any]`
- `get_messages(self, conversation_id: str) -> List[Dict[str, Any]]`
- `add_messages(self, conversation_id: str, messages: List[Dict[str, str]]) -> None`
- `extract_entities(self, conversation_id: str) -> List[Entity]`
- `get_conversation_entities(self, conversation_id: str) -> List[Entity]`
- `get_entity_statistics(self) -> List[Dict[str, Any]]`
- `search_conversations(self, keyword: str) -> List[Conversation]`
- `find_conversations_with_entity(self, entity_type: EntityType, entity_name: str) -> List[Conversation]`
- `get_conversations_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Conversation]`
- `get_eviction_log(self) -> List[Dict[str, Any]]`
- `store_conversation(self, user_message: str, assistant_response: str, intent: str, context: Optional[Dict[str, Any]]) -> str`
- `close(self) -> None`
- `create_profile(self, interaction_mode: str, experience_level: str, tech_stack_preference: Optional[Dict[str, str]]) -> bool`
- `get_profile(self) -> Optional[Dict[str, Any]]`
- `update_profile(self, interaction_mode: Optional[str], experience_level: Optional[str], tech_stack_preference: Optional[Dict[str, str]]) -> bool`
- `profile_exists(self) -> bool`
- `delete_profile(self) -> bool`
- `store_application_name(self, name: str) -> bool`
- `get_application_name(self) -> Optional[str]`
- `store_swagger_context(self, context_id: str, context_data: Dict[str, Any]) -> bool`
- `retrieve_swagger_context(self, context_id: str) -> Optional[Dict[str, Any]]`
- `update_swagger_context_status(self, context_id: str, status: str) -> bool`
- `store_test_intent(self, feature_name: str, requirement: str, test_phase: str, edge_cases: List[str], metadata: Dict[str, Any]) -> bool`
- `get_recent_test_intents(self, limit: int) -> List[Dict[str, Any]]`
- `get_edge_cases_for_feature(self, feature_name: str) -> List[Dict[str, Any]]`
- `store_temp_context(self, key: str, value: Any, ttl_seconds: int, context_type: str, metadata: Optional[Dict[str, Any]]) -> bool`
- `get_temp_context(self, key: str) -> Optional[Dict[str, Any]]`
- `cleanup_expired_contexts(self) -> int`
- `list_active_contexts(self, context_type: Optional[str]) -> List[Dict[str, Any]]`
- `list_conversations(self, limit: Optional[int], include_inactive: bool) -> List[Dict[str, Any]]`
- `mark_conversation_inactive(self, conversation_id: str) -> bool`
- `archive_conversation_to_tier2(self, conversation_id: str, knowledge_graph: Any) -> bool`
- `pin_conversation(self, conversation_id: str) -> bool`
- `unpin_conversation(self, conversation_id: str) -> bool`
- `is_conversation_pinned(self, conversation_id: str) -> bool`
- `list_pinned_conversations(self) -> List[Dict[str, Any]]`




## work_state_manager

### `WorkStatus`
 (inherits: Enum)




### `WorkState`


- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> 'WorkState'`
- `is_stale(self, hours: int) -> bool`
- `duration_minutes(self) -> float`


### `WorkStateManager`


- `start_task(self, task_description: str, files: Optional[List[str]], metadata: Optional[Dict[str, Any]]) -> str`
- `update_progress(self, progress_note: str, files_touched: Optional[List[str]], session_id: Optional[str]) -> None`
- `complete_task(self, session_id: Optional[str]) -> None`
- `pause_task(self, session_id: Optional[str]) -> None`
- `abandon_task(self, session_id: Optional[str], reason: Optional[str]) -> None`
- `get_current_state(self) -> Optional[WorkState]`
- `get_state(self, session_id: str) -> Optional[WorkState]`
- `has_incomplete_work(self) -> bool`
- `get_incomplete_sessions(self, include_stale: bool) -> List[WorkState]`
- `cleanup_stale_sessions(self, hours: int) -> int`
- `get_recent_completed(self, limit: int) -> List[WorkState]`
- `get_statistics(self) -> Dict[str, Any]`




## __init__



## conversation_manager

### `Conversation`




### `ConversationManager`


- `add_conversation(self, conversation_id: str, title: str, message_count: int, tags: Optional[List[str]]) -> Conversation`
- `get_conversation(self, conversation_id: str) -> Optional[Conversation]`
- `get_recent_conversations(self, limit: int) -> List[Conversation]`
- `set_active_conversation(self, conversation_id: str) -> None`
- `get_active_conversation(self) -> Optional[Conversation]`
- `update_conversation(self, conversation_id: str, title: Optional[str], summary: Optional[str], tags: Optional[List[str]]) -> None`
- `increment_message_count(self, conversation_id: str, count: int) -> None`
- `get_conversation_count(self) -> int`
- `delete_conversation(self, conversation_id: str) -> None`




## conversation_search

### `ConversationSearch`


- `search_by_keyword(self, keyword: str) -> List[Conversation]`
- `search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Conversation]`
- `search_by_entity(self, entity_type: str, entity_name: str) -> List[Conversation]`




## __init__



## entity_extractor

### `EntityType`
 (inherits: Enum)




### `Entity`




### `EntityExtractor`


- `extract_entities(self, conversation_id: str, text: str) -> List[Entity]`
- `get_conversation_entities(self, conversation_id: str) -> List[Entity]`
- `get_entity_statistics(self) -> List[Dict[str, Any]]`




## __init__



## queue_manager

### `QueueManager`


- `enforce_fifo_limit(self, tier2_knowledge_graph) -> None`
- `get_eviction_log(self) -> List[Dict[str, Any]]`
- `get_queue_status(self) -> Dict[str, Any]`




## __init__



## conversation_lifecycle_manager

### `WorkflowState`
 (inherits: Enum)




### `ConversationLifecycleEvent`




### `ConversationLifecycleManager`


- `detect_command_intent(self, user_request: str) -> Tuple[str, float]`
- `infer_workflow_state(self, user_request: str, current_state: Optional[WorkflowState]) -> WorkflowState`
- `should_create_conversation(self, session_id: str, user_request: str, has_active_conversation: bool) -> Tuple[bool, str]`
- `should_close_conversation(self, conversation_id: str, current_state: WorkflowState, user_request: Optional[str]) -> Tuple[bool, str]`
- `update_workflow_state(self, conversation_id: str, session_id: str, new_state: WorkflowState, trigger: str) -> None`
- `close_conversation(self, conversation_id: str, session_id: str, reason: str, final_state: WorkflowState) -> None`
- `log_conversation_created(self, conversation_id: str, session_id: str, trigger: str, initial_state: WorkflowState) -> None`
- `get_conversation_history(self, conversation_id: str) -> List[ConversationLifecycleEvent]`
- `get_session_conversation_history(self, session_id: str) -> List[ConversationLifecycleEvent]`




## __init__



## message_store

### `MessageStore`


- `add_messages(self, conversation_id: str, messages: List[Dict[str, str]]) -> None`
- `get_messages(self, conversation_id: str) -> List[Dict[str, Any]]`
- `get_message_count(self, conversation_id: str) -> int`
- `delete_messages(self, conversation_id: str) -> None`




## __init__



## add_response_detail

- `migrate_add_response_detail(db_path: Optional[Path]) -> bool`
- `rollback_response_detail(db_path: Optional[Path]) -> bool`


## session_manager

### `Session`




### `SessionManager`


- `detect_or_create_session(self, workspace_path: str) -> Session`
- `get_active_session(self, workspace_path: str) -> Optional[Session]`
- `get_session(self, session_id: str) -> Optional[Session]`
- `end_session(self, session_id: str, reason: str) -> None`
- `increment_conversation_count(self, session_id: str) -> None`
- `get_recent_sessions(self, workspace_path: Optional[str], limit: int) -> List[Session]`
- `cleanup_old_sessions(self, retention_days: int) -> int`




## __init__



## amnesia

### `AmnesiaStats`




### `EnhancedAmnesia`


- `delete_by_namespace(self, namespace: str, require_confirmation: bool, dry_run: bool, bypass_safety: bool) -> AmnesiaStats`
- `delete_by_confidence(self, max_confidence: float, protect_generic: bool, namespace: Optional[str], dry_run: bool) -> AmnesiaStats`
- `delete_by_age(self, days_inactive: int, protect_generic: bool, namespace: Optional[str], dry_run: bool) -> AmnesiaStats`
- `clear_application_scope(self, confirmation_code: Optional[str], dry_run: bool) -> AmnesiaStats`
- `get_deletion_preview(self, namespace: Optional[str], max_confidence: Optional[float], days_inactive: Optional[int]) -> Dict[str, Any]`
- `export_deletion_log(self, output_path: Path) -> bool`




## knowledge_graph

### `KnowledgeGraph`


- `store_pattern(self, title: str, pattern_type: str, confidence: float, context: Dict[str, Any], scope: str, namespaces: List[str]) -> str`
- `search_patterns(self, query: str, pattern_type: Optional[str], min_confidence: float, scope: Optional[str], limit: int, include_confidence_metadata: bool) -> List[Dict[str, Any]]`
- `track_relationship(self, file_a: str, file_b: str, relationship_type: str, strength: float, context: str)`
- `get_file_relationships(self, file_path: str, min_strength: float) -> List[Dict[str, Any]]`
- `store_workflow_template(self, name: str, phases: List[Dict[str, Any]], success_rate: float, avg_duration_hours: float) -> str`
- `get_workflow_template(self, name: str) -> Optional[Dict[str, Any]]`
- `boost_pattern(self, pattern_id: str, boost_amount: float)`
- `apply_decay(self, decay_rate: float, min_confidence: float)`
- `store_tdd_cycle_pattern(self, feature: str, test_strategy: str, implementation_approach: str, refactoring_type: str, confidence: float) -> str`
- `get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]`
- `get_implementation_dependencies(self, feature: str) -> List[Dict[str, Any]]`
- `get_implementation_decisions(self, feature: str) -> List[Dict[str, Any]]`
- `suggest_patterns_for_feature(self, feature_name: str, limit: int) -> List[Dict[str, Any]]`
- `fts5_search(self, query: str, limit: int) -> List[Dict[str, Any]]`
- `store_relationship(self, relationship_id: str, file_a: str, file_b: str, relationship_type: str, strength: float, context: str) -> None`
- `get_relationships(self, file_a: Optional[str], file_b: Optional[str], relationship_type: Optional[str]) -> List[Dict[str, Any]]`




## legacy_knowledge_graph_adapter

### `LegacyKnowledgeGraphAdapter`


- `store_pattern(self, title: str, pattern_type: str, confidence: float, context: Dict[str, Any], scope: str, namespaces: List[str], pattern_id: str, content: str, metadata: Dict[str, Any], source: str, is_pinned: bool, is_cortex_internal: bool) -> Dict[str, Any]`
- `get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]`
- `search_patterns(self, query: str, pattern_type: Optional[str], min_confidence: float, scope: Optional[str], limit: int, include_confidence_metadata: bool) -> List[Dict[str, Any]]`
- `fts5_search(self, query: str, pattern_type: Optional[str], namespace_filter: Optional[str], limit: int) -> List[Dict[str, Any]]`
- `store_relationship(self, file_a: str, file_b: str, relationship_type: str, strength: float, context: Optional[Dict[str, Any]], relationship_id: Optional[str]) -> str`
- `get_relationships(self, file_path: Optional[str], file_a: Optional[str], relationship_type: Optional[str]) -> List[Dict[str, Any]]`




## migrate_add_boundaries

### `BoundaryMigration`


- `create_backup(self) -> Path`
- `classify_pattern(self, pattern_id: str, title: str, content: str, source: str) -> Tuple[str, List[str]]`
- `get_existing_patterns(self) -> List[Dict[str, Any]]`
- `execute_migration(self) -> Dict[str, Any]`
- `print_summary(self, stats: Dict[str, Any])`


- `main()`


## oracle_crawler

### `OracleTable`




### `OracleColumn`




### `OracleIndex`




### `OracleConstraint`




### `OracleCrawler`


- `connect(self) -> None`
- `disconnect(self) -> None`
- `extract_schema(self, owners: Optional[List[str]], include_system: bool) -> List[OracleTable]`
- `table_to_pattern(self, table: OracleTable) -> Dict[str, Any]`
- `store_patterns(self, tables: List[OracleTable], knowledge_graph: KnowledgeGraph) -> int`




## pattern_cleanup

### `CleanupStats`




### `PatternCleanup`


- `apply_automatic_decay(self, protect_generic: bool) -> CleanupStats`
- `consolidate_similar_patterns(self, namespace: Optional[str], dry_run: bool) -> CleanupStats`
- `remove_stale_patterns(self, stale_days: int, protect_generic: bool) -> CleanupStats`
- `optimize_database(self) -> bool`
- `get_cleanup_recommendations(self) -> Dict[str, Any]`




## pattern_suggestion_engine

### `PatternSuggestionEngine`


- `suggest_patterns(self, task_description: str, intent_type: Optional[str], current_namespace: Optional[str], min_confidence: float, limit: int) -> List[Dict[str, Any]]`
- `format_suggestion(self, pattern: Dict[str, Any]) -> str`
- `display_suggestions(self, task_description: str, intent_type: Optional[str], current_namespace: Optional[str]) -> str`
- `track_pattern_acceptance(self, pattern_id: str, accepted: bool, task_outcome: Optional[str]) -> bool`




## personal_knowledge_archive

### `ArchivedPattern`




### `ArchivedAntiPattern`




### `CortexKnowledgeArchive`


- `add_pattern(self, pattern: ArchivedPattern) -> bool`
- `add_antipattern(self, antipattern: ArchivedAntiPattern) -> bool`
- `search_patterns(self, query: str, pattern_type: Optional[str], limit: int) -> List[ArchivedPattern]`
- `get_pattern(self, pattern_id: str) -> Optional[ArchivedPattern]`
- `increment_pattern_usage(self, pattern_id: str, success: bool) -> bool`
- `get_archive_statistics(self) -> Dict[str, Any]`
- `add_project(self, project_id: str, project_name: str) -> bool`
- `update_project_stats(self, project_id: str) -> bool`




## plan_models

### `Meta`




### `Artifacts`




### `PlanLedgerEntry`




### `PlanLedger`




### `FeaturePlan`




### `ArchitecturePlan`




### `RefactorPlan`




### `ActivePlans`




### `Decision`




### `DecisionGraph`




### `ReasoningChainEntry`




### `RequiredTests`




### `TestAlignmentItem`




### `TestAlignment`




### `PlanForecast`




### `MetricsForecast`






## relationship_mapper

### `CodeRelationship`




### `RelationshipMapper`


- `extract_code_relationships(self, file_path: str, code_content: str) -> List[Dict[str, Any]]`
- `extract_import_relationships(self, file_path: str, code_content: str) -> List[Dict[str, Any]]`
- `build_feature_graph(self, feature_files: Dict[str, List[str]]) -> Dict[str, List[str]]`
- `store_relationship(self, source: str, target: str, relationship_type: str, strength: float, context: str) -> str`
- `get_related_files(self, file_path: str, relationship_type: Optional[str]) -> List[Dict[str, Any]]`




## relevance_scorer

### `RelevanceScorer`


- `calculate_text_similarity(self, query: str, pattern_content: str) -> float`
- `calculate_namespace_overlap(self, query_namespaces: List[str], pattern_namespaces: List[str]) -> float`
- `calculate_recency_score(self, last_used: Optional[str]) -> float`
- `calculate_relevance(self, query: str, pattern_id: str, context_namespaces: Optional[List[str]]) -> Dict[str, Any]`
- `rank_patterns(self, query: str, pattern_ids: List[str], context_namespaces: Optional[List[str]]) -> List[Dict[str, Any]]`




## semantic_search

### `SemanticSearch`


- `search(self, query: str, pattern_type: Optional[str], namespaces: Optional[List[str]], limit: int) -> List[Dict[str, Any]]`




## tdd_cycle_logger

### `TDDCycleLogger`


- `log_red_phase(self, test_file: str, test_name: str, test_content: str, intent: str) -> str`
- `log_green_phase(self, impl_file: str, impl_content: str, test_file: str, test_passed: bool) -> str`
- `log_refactor_phase(self, file_path: str, before_code: str, after_code: str, refactor_type: str, tests_still_passing: bool) -> str`
- `link_cycle(self, red_pattern_id: str, green_pattern_id: str, refactor_pattern_id: Optional[str], refactor_id: Optional[str]) -> str`




## __init__


