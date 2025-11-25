# CORTEX Operations System - Universal Modular Architecture

**Version:** 2.0  
**Status:** ✅ Production Ready  
**Design:** SOLID Principles + Universal Command Orchestration

---

## 🎯 Overview

The CORTEX Operations System provides a **universal, modular architecture** for ALL CORTEX commands. Every operation (`/setup`, `/CORTEX refresh story`, `/CORTEX cleanup`, etc.) is composed of pluggable, reusable modules orchestrated via YAML configuration.

### Key Innovation

**Before:** Each command had its own monolithic implementation  
**After:** Every command is composed of reusable, testable modules

---

## 🏗️ Universal Architecture

```
User Request: "/CORTEX refresh cortex story" or "cleanup my workspace"
                              ↓
┌───────────────────────────────────────────────────────────┐
│            Command Router (Intent Detection)              │
│                                                           │
│  Maps natural language → Operation ID                    │
│  "refresh story" → operation: refresh_cortex_story       │
│  "cleanup" → operation: workspace_cleanup                │
│  "/setup" → operation: environment_setup                 │
└────────────────────────┬──────────────────────────────────┘
                         ↓
┌───────────────────────────────────────────────────────────┐
│           Operation Orchestrator (Universal)               │
│         (operations_orchestrator.py)                       │
│                                                           │
│  • Loads operation definition from YAML                   │
│  • Discovers required modules                             │
│  • Resolves dependencies                                  │
│  • Executes modules in order                             │
│  • Handles failures & rollback                            │
└────────────────────────┬──────────────────────────────────┘
                         ↓
┌───────────────────────────────────────────────────────────┐
│         Operation Registry (YAML-Driven)                   │
│       (cortex-operations.yaml)                             │
│                                                           │
│  operations:                                              │
│    refresh_cortex_story:                                  │
│      modules: [load_story, transform_voice, save_story]  │
│    workspace_cleanup:                                     │
│      modules: [scan_temp, remove_old, vacuum_db]         │
│    environment_setup:                                     │
│      modules: [platform_detect, install_deps, init_brain]│
└────────────────────────┬──────────────────────────────────┘
                         ↓
┌───────────────────────────────────────────────────────────┐
│      Base Operation Module (Abstract Interface)            │
│         (base_operation_module.py)                         │
│                                                           │
│  • get_metadata() → ModuleMetadata                        │
│  • validate_prerequisites(context) → bool, issues        │
│  • execute(context) → OperationResult                    │
│  • rollback(context) → bool                              │
└────────────────────────┬──────────────────────────────────┘
                         ↓
┌───────────────────────────────────────────────────────────┐
│           Concrete Operation Modules                       │
│         (src/operations/modules/*.py)                      │
│                                                           │
│  SETUP:                                                   │
│    • PlatformDetectionModule                              │
│    • VisionAPIModule                                      │
│    • BrainInitializationModule                            │
│                                                           │
│  STORY REFRESH:                                           │
│    • LoadStoryModule                                      │
│    • TransformNarratorVoiceModule                         │
│    • SaveStoryModule                                      │
│                                                           │
│  CLEANUP:                                                 │
│    • ScanTemporaryFilesModule                            │
│    • RemoveOldArtifactsModule                            │
│    • VacuumDatabaseModule                                │
│                                                           │
│  DOCUMENTATION:                                           │
│    • RefreshDocsModule                                    │
│    • BuildMkDocsModule                                    │
│    • ValidateLinksModule                                  │
└───────────────────────────────────────────────────────────┘
```

---

## 📋 Example: Universal Operation Definition

### cortex-operations.yaml

```yaml
# Universal registry of ALL CORTEX operations

operations:
  # ENVIRONMENT SETUP
  environment_setup:
    name: "Environment Setup"
    description: "Configure CORTEX development environment"
    natural_language: ["setup", "configure", "initialize environment"]
    slash_command: "/setup"
    modules:
      - platform_detection
      - git_sync
      - virtual_environment
      - python_dependencies
      - vision_api
      - brain_initialization
      - brain_tests
      - tooling_verification
      - setup_completion
    
  # STORY REFRESH (ADMIN-ONLY - NOT IN USER DEPLOYMENT)
  refresh_cortex_story:
    name: "Refresh CORTEX Story"
    description: "[DEPRECATED] Admin-only operation - updates CORTEX's own story documentation"
    deployment_tier: admin
    status: deprecated
    consolidation_target: document_cortex
    natural_language: ["refresh story", "update story", "regenerate story"]
    slash_command: "/CORTEX, refresh cortex story"
    note: "Use 'document_cortex' instead for documentation updates"
    modules:
      - load_story_template
      - apply_narrator_voice
      - validate_story_structure
      - save_story_markdown
      - update_mkdocs_index
  
  # WORKSPACE CLEANUP
  workspace_cleanup:
    name: "Workspace Cleanup"
    description: "Clean temporary files and optimize databases"
    natural_language: ["cleanup", "clean workspace", "tidy up"]
    slash_command: "/CORTEX, cleanup"
    modules:
      - scan_temporary_files
      - remove_old_logs
      - vacuum_sqlite_databases
      - clear_python_cache
      - remove_orphaned_files
      - generate_cleanup_report
  
  # DOCUMENTATION UPDATE
  update_documentation:
    name: "Update Documentation"
    description: "Refresh and build documentation site"
    natural_language: ["update docs", "refresh documentation", "build docs"]
    slash_command: "/CORTEX, generate documentation"
    modules:
      - scan_docstrings
      - generate_api_docs
      - refresh_design_docs
      - build_mkdocs_site
      - validate_doc_links
      - deploy_docs
  
  # BRAIN PROTECTION CHECK
  brain_protection_check:
    name: "Brain Protection Validation"
    description: "Validate brain protection rules"
    natural_language: ["check brain", "validate brain", "brain protection"]
    slash_command: "/CORTEX, run brain protection"
    modules:
      - load_protection_rules
      - validate_tier0_immutability
      - check_brain_integrity
      - generate_protection_report
  
  # TEST EXECUTION
  run_tests:
    name: "Test Suite Execution"
    description: "Run CORTEX test suite"
    natural_language: ["run tests", "test this", "execute tests"]
    slash_command: "/CORTEX, run tests"
    modules:
      - discover_tests
      - run_unit_tests
      - run_integration_tests
      - generate_coverage_report
      - validate_test_quality

# Module definitions
modules:
  # (Same module definitions as before, but now shared across operations)
  
  platform_detection:
    phase: ENVIRONMENT
    priority: 10
    class: "PlatformDetectionModule"
  
  vision_api:
    phase: FEATURES
    priority: 10
    class: "VisionAPIModule"
  
  load_story_template:
    phase: PREPARATION
    priority: 10
    class: "LoadStoryTemplateModule"
  
  apply_narrator_voice:
    phase: PROCESSING
    priority: 20
    class: "ApplyNarratorVoiceModule"
  
  scan_temporary_files:
    phase: ANALYSIS
    priority: 10
    class: "ScanTemporaryFilesModule"
  
  # ... etc.
```

---

## 🎯 Usage Examples

### 1. Environment Setup (Existing)

```python
from src.operations import execute_operation

# Natural language
result = execute_operation("setup environment")

# Slash command
result = execute_operation("/setup full")

# Programmatic
result = execute_operation("environment_setup", profile="full")
```

### 2. Story Refresh (NEW!)

```python
# Natural language
result = execute_operation("refresh the cortex story")

# Slash command
result = execute_operation("/CORTEX, refresh cortex story")

# Programmatic
result = execute_operation("refresh_cortex_story")
```

### 3. Workspace Cleanup (NEW!)

```python
# Natural language
result = execute_operation("clean up my workspace")

# Slash command
result = execute_operation("/CORTEX, cleanup")

# Programmatic
result = execute_operation("workspace_cleanup", aggressive=True)
```

### 4. Documentation Update (NEW!)

```python
# Natural language
result = execute_operation("update the documentation")

# Slash command
result = execute_operation("/CORTEX, generate documentation")

# Programmatic
result = execute_operation("update_documentation", deploy=False)
```

---

## 🔧 Creating New Operations

### Step 1: Define Operation in YAML

```yaml
# cortex-operations.yaml
operations:
  my_custom_operation:
    name: "My Custom Operation"
    description: "Does something amazing"
    natural_language: ["do amazing thing", "amaze me"]
    slash_command: "/CORTEX, amaze"
    modules:
      - prepare_amazement
      - execute_amazement
      - verify_amazement
```

### Step 2: Create Operation Modules

```python
# src/operations/modules/prepare_amazement_module.py
from src.operations import BaseOperationModule

class PrepareAmazementModule(BaseOperationModule):
    def get_metadata(self):
        return ModuleMetadata(
            module_id="prepare_amazement",
            name="Prepare Amazement",
            phase=OperationPhase.PREPARATION,
            priority=10
        )
    
    def execute(self, context):
        # Do preparation
        return OperationResult(...)
```

### Step 3: Register Module

```python
# src/operations/module_registry.py
register_module_class('prepare_amazement', PrepareAmazementModule)
```

### Step 4: Use It!

```python
result = execute_operation("do amazing thing")
# or
result = execute_operation("/CORTEX, amaze")
```

**That's it!** Your new operation is now available everywhere CORTEX is used.

---

## 🎨 Benefits

✅ **Universal:** Works for ALL commands, not just setup  
✅ **Modular:** Each module has ONE responsibility  
✅ **Reusable:** Modules can be shared across operations  
✅ **Testable:** Test modules in isolation  
✅ **Discoverable:** YAML defines all operations  
✅ **Extensible:** Add operations without code changes  
✅ **Consistent:** Same orchestration for everything  

---

## 📊 Operation Categories

| Category | Operations | Example Commands |
|----------|-----------|------------------|
| **Environment** | setup, configure, initialize | `/setup`, `configure environment` |
| **Documentation** | refresh_story, update_docs, build_site | `/CORTEX, refresh cortex story` |
| **Maintenance** | cleanup, vacuum, optimize | `/CORTEX, cleanup` |
| **Testing** | run_tests, coverage, validate | `/CORTEX, run tests` |
| **Brain** | brain_check, protection, integrity | `/CORTEX, run brain protection` |
| **Development** | refactor, architect, plan | `/CORTEX, let's plan a feature` |

---

## 🔄 Migration Path

**Phase 1:** Existing `/setup` command works as-is (already done)  
**Phase 2:** Add new operations (story, cleanup, docs)  
**Phase 3:** Migrate remaining commands to modular system  
**Phase 4:** Deprecate monolithic implementations  

---

**Author:** Asif Hussain  
**Last Updated:** 2025-11-09  
**Version:** 2.0 (Universal Modular Architecture)
