# CORTEX Unwired Components Analysis

**Generated:** 2025-12-27 14:56:24

**Author:** Asif Hussain

---

## 📊 Executive Summary

**Total Components:** 119

**Wired:** 79 (66.4%)

**Unwired:** 40

### By Category

| Category | Total | Wired | Unwired | % Wired |
|----------|-------|-------|---------|----------|
| Orchestrators | 46 | 19 | 27 | 41.3% |
| Agents | 10 | 10 | 0 | 100.0% |
| Operation Modules | 40 | 40 | 0 | 100.0% |
| Setup Modules | 10 | 10 | 0 | 100.0% |
| Plugins | 13 | 0 | 13 | 0.0% |

---

## Orchestrators

### ❌ Unwired (27)

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

### ✅ Wired (19)

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

... and 9 more


---

## Agents

### ❌ Unwired (0)

✅ All components wired!

### ✅ Wired (10)

- ApplicationHealthAgent
- RCAAgent
- LearningCaptureAgent
- ComplianceDashboardAgent
- WelcomeBannerAgent
- ProfileAgent
- LearningLibrarianAgent
- ADOAgent
- ArchitectureIntelligenceAgent
- RouterAgent


---

## Operation Modules

### ❌ Unwired (0)

✅ All components wired!

### ✅ Wired (40)

- GenerateStoryChaptersModule
- ConversationCaptureModule
- RefreshDesignDocsModule
- VacuumSQLiteDatabasesModule
- DashboardLauncherModule
- ContextDisplayModule
- SaveStoryMarkdownModule
- ToolingVerificationModule
- PlatformDetectionModule
- GenerateCleanupReportModule

... and 30 more


---

## Setup Modules

### ❌ Unwired (0)

✅ All components wired!

### ✅ Wired (10)

- UserProfileModule
- PathConfigurationModule
- PlatformDetectionModule
- GitIgnoreSetupModule
- PythonEnvironmentModule
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

