# CORTEX Unwired Components Analysis

**Generated:** 2025-12-27 14:34:45

**Author:** Asif Hussain

---

## 📊 Executive Summary

**Total Components:** 119

**Wired:** 46 (38.7%)

**Unwired:** 73

### By Category

| Category | Total | Wired | Unwired | % Wired |
|----------|-------|-------|---------|----------|
| Orchestrators | 46 | 18 | 28 | 39.1% |
| Agents | 10 | 4 | 6 | 40.0% |
| Operation Modules | 40 | 17 | 23 | 42.5% |
| Setup Modules | 10 | 7 | 3 | 70.0% |
| Plugins | 13 | 0 | 13 | 0.0% |

---

## Orchestrators

### ❌ Unwired (28)

- **MasterSetupOrchestrator**
  - File: `src/orchestrators/master_setup_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **SetupEPMOrchestrator**
  - File: `src/orchestrators/setup_epm_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **GitCheckpointOrchestrator**
  - File: `src/orchestrators/git_checkpoint_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **ApplicationHealthOrchestrator**
  - File: `src/orchestrators/application_health_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **OnboardingAcknowledgmentOrchestrator**
  - File: `src/orchestrators/onboarding_acknowledgment_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **UpgradeOrchestratorV2**
  - File: `src/orchestrators/upgrade_orchestrator_v2.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **PreFlightOrchestrator**
  - File: `src/orchestrators/planning/pre_flight_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **IntelligenceOrchestrator**
  - File: `src/orchestrators/planning/intelligence/intelligence_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **SystemIntegrityOrchestrator**
  - File: `src/orchestrators/system/system_integrity_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **StoryEnhancementOrchestrator**
  - File: `src/orchestrators/story_enhancement/story_enhancement_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **SanitizationOrchestratorV2**
  - File: `src/orchestrators/sanitization/sanitization_orchestrator_v2_migrated_archived.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **OrchestratorResult**
  - File: `src/orchestrators/base/base_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **HandsOnTutorialOrchestrator**
  - File: `src/operations/modules/hands_on_tutorial_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **EnterpriseDocumentationOrchestratorModule**
  - File: `src/operations/modules/documentation/enterprise_documentation_orchestrator_module.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **AutoRegistrationOrchestrator**
  - File: `src/operations/modules/epm/auto_registration_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **VacuumOrchestrator**
  - File: `src/operations/modules/vacuum/vacuum_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **OptimizeCortexOrchestrator**
  - File: `src/operations/modules/optimization/optimize_cortex_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **DiagramRegenerationOrchestrator**
  - File: `src/operations/modules/diagrams/diagram_regeneration_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **OptimizeSystemOrchestrator**
  - File: `src/operations/modules/system/optimize_system_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **PublishBranchOrchestrator**
  - File: `src/operations/modules/publish/publish_branch_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **UserCleanupOrchestrator**
  - File: `src/operations/modules/cleanup/user_cleanup_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **HolisticCleanupOrchestrator**
  - File: `src/operations/modules/cleanup/holistic_cleanup_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **ADOValidationOrchestrator**
  - File: `src/operations/modules/orchestration/ado_validation_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **HolisticDiscoveryOrchestrator**
  - File: `src/operations/modules/orchestration/holistic_discovery_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **VisionAPIValidationOrchestrator**
  - File: `src/operations/modules/orchestration/vision_api_validation_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **ArchitecturalReviewOrchestrator**
  - File: `src/operations/modules/orchestration/architectural_review_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **BrainTuningOrchestrator**
  - File: `src/operations/modules/brain/brain_tuning_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

- **DesignSyncOrchestrator**
  - File: `src/operations/modules/design_sync/design_sync_orchestrator.py`
  - In operations.yaml: False
  - Has response template: False
  - Has triggers: False

### ✅ Wired (18)

- UpgradeOrchestrator
- RollbackOrchestrator
- AlignmentOrchestrator
- PlanningOrchestrator
- ADOOrchestrator
- PlanningOrchestrator
- OrchestratorConfig
- SanitizationOrchestrator
- TDDOrchestrator
- TDDOrchestrator

... and 8 more


---

## Agents

### ❌ Unwired (6)

- **ApplicationHealthAgent**
  - File: `src/cortex_agents/application_health_agent.py`
  - Wired in executor: True
  - Has AgentType enum: False

- **LearningCaptureAgent**
  - File: `src/cortex_agents/learning_capture_agent.py`
  - Wired in executor: False
  - Has AgentType enum: False

- **ComplianceDashboardAgent**
  - File: `src/cortex_agents/compliance_dashboard_agent.py`
  - Wired in executor: False
  - Has AgentType enum: False

- **WelcomeBannerAgent**
  - File: `src/cortex_agents/welcome_banner_agent.py`
  - Wired in executor: False
  - Has AgentType enum: False

- **LearningLibrarianAgent**
  - File: `src/cortex_agents/learning_librarian_agent.py`
  - Wired in executor: False
  - Has AgentType enum: False

- **ArchitectureIntelligenceAgent**
  - File: `src/cortex_agents/strategic/architecture_intelligence_agent.py`
  - Wired in executor: False
  - Has AgentType enum: False

### ✅ Wired (4)

- RCAAgent
- ProfileAgent
- ADOAgent
- RouterAgent


---

## Operation Modules

### ❌ Unwired (23)

- **GenerateStoryChaptersModule**
  - File: `src/operations/modules/generate_story_chapters_module.py`

- **ConversationCaptureModule**
  - File: `src/operations/modules/conversation_capture_module.py`

- **RefreshDesignDocsModule**
  - File: `src/operations/modules/refresh_design_docs_module.py`

- **VacuumSQLiteDatabasesModule**
  - File: `src/operations/modules/vacuum_sqlite_databases_module.py`

- **ContextDisplayModule**
  - File: `src/operations/modules/context_display_module.py`

- **GenerateCleanupReportModule**
  - File: `src/operations/modules/generate_cleanup_report_module.py`

- **ContextControlModule**
  - File: `src/operations/modules/context_control_module.py`

- **AdminDashboardLauncherModule**
  - File: `src/operations/modules/admin_dashboard_launcher_module.py`

- **ScanDocstringsModule**
  - File: `src/operations/modules/scan_docstrings_module.py`

- **GenerateImagePromptsModule**
  - File: `src/operations/modules/generate_image_prompts_module.py`

- **RelocateStoryFilesModule**
  - File: `src/operations/modules/relocate_story_files_module.py`

- **RemoveOrphanedFilesModule**
  - File: `src/operations/modules/remove_orphaned_files_module.py`

- **ClearPythonCacheModule**
  - File: `src/operations/modules/clear_python_cache_module.py`

- **EvaluateCortexArchitectureModule**
  - File: `src/operations/modules/evaluate_cortex_architecture_module.py`

- **DeployDocsPreviewModule**
  - File: `src/operations/modules/deploy_docs_preview_module.py`

- **RemoveOldLogsModule**
  - File: `src/operations/modules/remove_old_logs_module.py`

- **LoadProtectionRulesModule**
  - File: `src/operations/modules/load_protection_rules_module.py`

- **GitCheckpointModule**
  - File: `src/operations/modules/git_checkpoint_module.py`

- **ScanTemporaryFilesModule**
  - File: `src/operations/modules/scan_temporary_files_module.py`

- **EnterpriseDocumentationOrchestratorModule**
  - File: `src/operations/modules/documentation/enterprise_documentation_orchestrator_module.py`

- **HardcodedDataCleanerModule**
  - File: `src/operations/modules/optimization/hardcoded_data_cleaner_module.py`

- **EnhancedFeedbackModule**
  - File: `src/operations/modules/feedback/enhanced_feedback_module.py`

- **RemoveObsoleteTestsModule**
  - File: `src/operations/modules/cleanup/remove_obsolete_tests_module.py`

### ✅ Wired (17)

- DashboardLauncherModule
- SaveStoryMarkdownModule
- ToolingVerificationModule
- PlatformDetectionModule
- ConversationTrackingModule
- PythonDependenciesModule
- VirtualEnvironmentModule
- BrainTestsModule
- ValidateStoryStructureModule
- BuildStoryPreviewModule

... and 7 more


---

## Setup Modules

### ❌ Unwired (3)

- **UserProfileModule**
  - File: `src/setup/modules/user_profile_module.py`

- **PathConfigurationModule**
  - File: `src/setup/modules/path_configuration_module.py`

- **PythonEnvironmentModule**
  - File: `src/setup/modules/python_environment_module.py`

### ✅ Wired (7)

- PlatformDetectionModule
- GitIgnoreSetupModule
- PythonDependenciesModule
- RefactoringToolsModule
- OnboardingModule
- BrainInitializationModule
- VisionAPIModule


---

## Plugins

### ❌ Unwired (13)

- **Plugin**
  - File: `src/plugins/extension_scaffold_plugin.py`

- **ConversationImportPlugin**
  - File: `src/plugins/conversation_import_plugin.py`

- **InvestigationSecurityPlugin**
  - File: `src/plugins/investigation_security_plugin.py`

- **ConfigurationWizardPlugin**
  - File: `src/plugins/configuration_wizard_plugin.py`

- **SweeperPlugin**
  - File: `src/plugins/sweeper_plugin.py`

- **Plugin**
  - File: `src/plugins/cleanup_plugin.py`

- **InvestigationRefactoringPlugin**
  - File: `src/plugins/investigation_refactoring_plugin.py`

- **DocRefreshPlugin**
  - File: `src/plugins/doc_refresh_plugin.py`

- **PhaseTrackerPlugin**
  - File: `src/plugins/phase_tracker_plugin.py`

- **InvestigationHtmlIdMappingPlugin**
  - File: `src/plugins/investigation_html_id_mapping_plugin.py`

- **SystemRefactorPlugin**
  - File: `src/plugins/system_refactor_plugin.py`

- **PlatformSwitchPlugin**
  - File: `src/plugins/platform_switch_plugin.py`

- **CodeReviewPlugin**
  - File: `src/plugins/code_review_plugin.py`

### ✅ Wired (0)


---

## 🎯 Remediation Recommendations

### Priority Levels

1. **CRITICAL**: User-facing orchestrators without natural language triggers
2. **HIGH**: Core agents without executor wiring
3. **MEDIUM**: Operation modules not linked to operations
4. **LOW**: Setup modules and plugins (internal tooling)

