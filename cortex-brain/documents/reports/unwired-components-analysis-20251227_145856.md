# CORTEX Unwired Components Analysis

**Generated:** 2025-12-27 14:58:56

**Author:** Asif Hussain

---

## 📊 Executive Summary

**Total Components:** 119

**Wired:** 104 (87.4%)

**Unwired:** 15

### By Category

| Category | Total | Wired | Unwired | % Wired |
|----------|-------|-------|---------|----------|
| Orchestrators | 46 | 44 | 2 | 95.7% |
| Agents | 10 | 10 | 0 | 100.0% |
| Operation Modules | 40 | 40 | 0 | 100.0% |
| Setup Modules | 10 | 10 | 0 | 100.0% |
| Plugins | 13 | 0 | 13 | 0.0% |

---

## Orchestrators

### ❌ Unwired (2)

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

### ✅ Wired (44)

- UpgradeOrchestrator
- MasterSetupOrchestrator
- SetupEPMOrchestrator
- RollbackOrchestrator
- GitCheckpointOrchestrator
- ApplicationHealthOrchestrator
- AlignmentOrchestrator
- OnboardingAcknowledgmentOrchestrator
- UpgradeOrchestratorV2
- PlanningOrchestrator

... and 34 more


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

