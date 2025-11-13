# CORTEX 2.0 - Universal Operations Architecture

**Migration Complete: Setup System → Universal Operations System**

---

## 🎯 What Changed?

### Before (CORTEX 2.0 - Setup Only)
```
src/setup/                    # Setup-specific system
  ├── base_setup_module.py    # Setup-only interface
  ├── setup_orchestrator.py   # Setup-only orchestrator
  └── setup_modules.yaml      # Setup modules only
```

### After (CORTEX 2.0 - Universal)
```
src/operations/                      # Universal system for ALL commands
  ├── base_operation_module.py       # Universal interface
  ├── operations_orchestrator.py     # Universal orchestrator
  └── modules/
      ├── [setup modules]            # Setup: platform, vision API, brain
      ├── [story modules]            # Story: load, transform, save
      ├── [cleanup modules]          # Cleanup: scan, remove, vacuum
      └── [docs modules]             # Docs: scan, build, deploy

cortex-operations.yaml               # Universal registry of ALL operations
```

---

## 🔄 What This Enables

### 1. **Setup Command** (Already Working)
```bash
/setup full
# or
"setup environment"
```

**Modules:** platform_detection → virtual_environment → python_dependencies → vision_api → brain_initialization → ...

---

### 2. **Story Refresh** (NEW!)
```bash
/CORTEX, refresh cortex story
# or
"refresh the story"
```

**Modules:** load_story_template → apply_narrator_voice → validate_story_structure → save_story_markdown → update_mkdocs_index

---

### 3. **Workspace Cleanup** (NEW!)
```bash
/CORTEX, cleanup
# or
"clean up my workspace"
```

**Modules:** scan_temporary_files → remove_old_logs → clear_python_cache → vacuum_sqlite_databases → generate_cleanup_report

---

### 4. **Feature Planning** (NEW!)
```bash
/CORTEX, let's plan a feature
# or
"plan a feature"
```

**Modules:** gather_requirements → search_similar_features → break_down_phases → identify_dependencies → analyze_risks → generate_roadmap → save_feature_plan → create_execution_context

---

### 5. **Documentation Update** (Planned)
```bash
/CORTEX, generate documentation
# or
"update the docs"
```

**Modules:** scan_docstrings → generate_api_docs → build_mkdocs_site → validate_doc_links → deploy_docs_preview

---

## 📋 Operations Registry

All operations defined in **`cortex-operations.yaml`**:

| Operation ID | Command | Category | Modules |
|-------------|---------|----------|---------|
| `environment_setup` | `/setup` | Environment | 11 modules |
| `refresh_cortex_story` | `/CORTEX, refresh cortex story` | Documentation | 6 modules |
| `workspace_cleanup` | `/CORTEX, cleanup` | Maintenance | 6 modules |
| `feature_planning` | `/CORTEX, let's plan a feature` | Planning | 8 modules |
| `update_documentation` | `/CORTEX, generate documentation` | Documentation | 6 modules |
| `brain_protection_check` | `/CORTEX, run brain protection` | Validation | 6 modules |
| `run_tests` | `/CORTEX, run tests` | Testing | 5 modules |

**Total:** 8 operations, 56 modules

---

## 🏗️ Architecture Benefits

### ✅ Universal
Same orchestration for ALL commands (not just setup)

### ✅ Modular
Each module has ONE responsibility (SOLID principles)

### ✅ Reusable
Modules can be shared across operations (e.g., `brain_initialization` used by setup AND brain_protection_check)

### ✅ Testable
Test modules in isolation with mock context

### ✅ Discoverable
YAML defines all operations and modules (no code diving)

### ✅ Extensible
Add new operations by editing YAML + creating modules (no orchestrator changes)

### ✅ Consistent
Same execution flow: PRE_VALIDATION → PREPARATION → ENVIRONMENT → DEPENDENCIES → PROCESSING → FEATURES → VALIDATION → FINALIZATION

---

## 🔧 Adding New Operations

### Step 1: Define Operation in YAML

```yaml
# cortex-operations.yaml
operations:
  my_custom_operation:
    name: "My Custom Operation"
    description: "Does something amazing"
    natural_language:
      - "do amazing thing"
      - "amaze me"
    slash_command: "/CORTEX, amaze"
    category: "custom"
    modules:
      - prepare_amazement
      - execute_amazement
      - verify_amazement
```

### Step 2: Define Modules

```yaml
# cortex-operations.yaml
modules:
  prepare_amazement:
    name: "Prepare Amazement"
    phase: PREPARATION
    priority: 10
    class: "PrepareAmazementModule"
    file: "prepare_amazement_module.py"
```

### Step 3: Implement Module

```python
# src/operations/modules/prepare_amazement_module.py
from src.operations import BaseOperationModule

class PrepareAmazementModule(BaseOperationModule):
    def get_metadata(self):
        return OperationModuleMetadata(
            module_id="prepare_amazement",
            name="Prepare Amazement",
            phase=OperationPhase.PREPARATION
        )
    
    def execute(self, context):
        # Do work
        return OperationResult(success=True, message="Amazing!")
```

### Step 4: Use It!

```python
result = execute_operation("my_custom_operation")
# or
result = execute_operation("do amazing thing")
```

**That's it!** No changes to orchestrator needed.

---

## 📊 Implementation Status

### ✅ Core Architecture (Complete)
- [x] `base_operation_module.py` - Universal abstract interface
- [x] `operations_orchestrator.py` - Universal orchestrator
- [x] `cortex-operations.yaml` - Universal registry (7 operations, 48 modules defined)
- [x] `README.md` - Comprehensive documentation

### ✅ Example Modules (Proof of Concept)
- [x] `load_story_template_module.py` - Story refresh operation module

### ⏸️ Module Migration (In Progress)
**Existing modules (in `src/setup/`) need moving to `src/operations/`:**
- [ ] Move `platform_detection_module.py`
- [ ] Move `vision_api_module.py`
- [ ] Move `python_dependencies_module.py`
- [ ] Move `brain_initialization_module.py`
- [ ] Update imports from `src.setup` → `src.operations`

### ❌ New Operation Modules (Pending)
**Story Refresh:**
- [ ] `apply_narrator_voice_module.py`
- [ ] `validate_story_structure_module.py`
- [ ] `save_story_markdown_module.py`
- [ ] `update_mkdocs_index_module.py`
- [ ] `build_story_preview_module.py`

**Cleanup:**
- [ ] `scan_temporary_files_module.py`
- [ ] `remove_old_logs_module.py`
- [ ] `clear_python_cache_module.py`
- [ ] `vacuum_sqlite_databases_module.py`
- [ ] `remove_orphaned_files_module.py`
- [ ] `generate_cleanup_report_module.py`

**Feature Planning:**
- [ ] `gather_requirements_module.py`
- [ ] `search_similar_features_module.py`
- [ ] `break_down_phases_module.py`
- [ ] `identify_dependencies_module.py`
- [ ] `analyze_risks_module.py`
- [ ] `generate_roadmap_module.py`
- [ ] `save_feature_plan_module.py`
- [ ] `create_execution_context_module.py`

**Documentation:**
- [ ] `scan_docstrings_module.py`
- [ ] `generate_api_docs_module.py`
- [ ] `refresh_design_docs_module.py`
- [ ] `build_mkdocs_site_module.py`
- [ ] `validate_doc_links_module.py`
- [ ] `deploy_docs_preview_module.py`

### ❌ Command Router (Pending)
- [ ] Create universal command router
- [ ] Integrate with entry point (`.github/prompts/CORTEX.prompt.md`)
- [ ] Natural language → operation ID mapping
- [ ] Slash command → operation ID mapping

### ❌ Documentation Updates (Pending)
- [ ] Update `.github/prompts/CORTEX.prompt.md` (entry point)
- [ ] Update `.github/copilot-instructions.md` (baseline context)
- [ ] Update design documents (CORTEX 2.0 docs)
- [ ] Update phase checklists

---

## 🎯 Next Steps

### Phase 1: Module Migration (HIGH PRIORITY)
1. Move existing setup modules from `src/setup/` → `src/operations/modules/`
2. Update imports in all modules
3. Update module factory to use new paths
4. Test setup command still works

### Phase 2: Story Refresh Implementation (HIGH PRIORITY)
1. Implement story refresh modules
2. Test story refresh operation end-to-end
3. Validate narrator voice transformation

### Phase 3: Cleanup & Docs (MEDIUM PRIORITY)
1. Implement cleanup modules
2. Implement documentation modules
3. Test all new operations

### Phase 4: Command Router (HIGH PRIORITY)
1. Create universal router
2. Map natural language → operations
3. Map slash commands → operations
4. Integrate with CORTEX entry point

### Phase 5: Documentation (MEDIUM PRIORITY)
1. Update entry point prompt
2. Update baseline instructions
3. Update design docs
4. Update checklists

---

## 💡 Key Design Decisions

### 1. **Universal Base Class**
`BaseOperationModule` works for ALL operations (not just setup). This ensures consistency and allows module reuse.

### 2. **YAML-Driven Registry**
`cortex-operations.yaml` defines all operations and modules. This provides:
- Single source of truth
- Easy discoverability
- Non-code extensibility

### 3. **Phase-Based Execution**
8 universal phases work for all operations:
```
PRE_VALIDATION → PREPARATION → ENVIRONMENT → DEPENDENCIES → 
PROCESSING → FEATURES → VALIDATION → FINALIZATION
```

### 4. **Same Orchestrator for Everything**
`OperationsOrchestrator` handles ALL operations. No special-case logic per command.

### 5. **Module Reusability**
Modules can be shared across operations:
- `brain_initialization` used by `environment_setup` AND `brain_protection_check`
- `platform_detection` used by multiple operations
- `validate_doc_links` used by `refresh_cortex_story` AND `update_documentation`

---

## 🔥 Breaking Changes

### For Developers

**OLD:**
```python
from src.setup import run_setup
report = run_setup(profile='full')
```

**NEW:**
```python
from src.operations import execute_operation
report = execute_operation('environment_setup', profile='full')
```

### For Plugin Authors

**OLD:**
```python
from src.setup.base_setup_module import BaseSetupModule
class MyModule(BaseSetupModule): ...
```

**NEW:**
```python
from src.operations.base_operation_module import BaseOperationModule
class MyModule(BaseOperationModule): ...
```

### For Users

**No breaking changes!** Commands work the same:
```
/setup full                          # Still works
/CORTEX, refresh cortex story        # NEW!
/CORTEX, cleanup                     # NEW!
```

---

## 📚 Documentation

- **Overview:** `src/operations/README.md` (this file)
- **Base Module:** `src/operations/base_operation_module.py` (docstrings)
- **Orchestrator:** `src/operations/operations_orchestrator.py` (docstrings)
- **Registry:** `cortex-operations.yaml` (inline comments)
- **Example Module:** `src/operations/modules/load_story_template_module.py`

---

**Author:** Asif Hussain  
**Version:** 2.0 (Universal Operations Architecture)  
**Date:** 2025-11-09  
**Status:** 🚧 In Progress (Core Complete, Modules Pending)
