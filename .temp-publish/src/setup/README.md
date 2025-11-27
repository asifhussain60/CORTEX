# CORTEX Setup System - Modular Architecture

**Version:** 2.0  
**Status:** ✅ Production Ready  
**Design:** SOLID Principles

---

## 🎯 Overview

The CORTEX Setup System uses a modular, plugin-based architecture following SOLID design principles. Each setup responsibility is isolated into independent, reusable modules that are orchestrated via YAML configuration.

### Key Benefits

- ✅ **Single Responsibility:** Each module handles ONE setup task
- ✅ **Open/Closed:** Add new modules without modifying orchestrator
- ✅ **Dependency Injection:** Modules receive context, don't create dependencies
- ✅ **Extensible:** Plugin-based architecture via YAML configuration
- ✅ **Testable:** Each module can be tested in isolation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Plugin Command Layer                       │
│          (platform_switch_plugin.py)                     │
│                                                          │
│  Handles: /setup command, natural language routing      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│             Setup Orchestrator                           │
│          (setup_orchestrator.py)                         │
│                                                          │
│  • Discovers modules from YAML                          │
│  • Resolves dependencies                                │
│  • Executes in phase/priority order                     │
│  • Handles failures & rollback                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          Module Factory (YAML-Driven)                    │
│            (module_factory.py)                           │
│                                                          │
│  • Loads setup_modules.yaml configuration               │
│  • Instantiates concrete modules                        │
│  • Supports profiles (minimal, standard, full)          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│        Base Setup Module (Abstract Interface)            │
│          (base_setup_module.py)                          │
│                                                          │
│  • get_metadata() → SetupModuleMetadata                 │
│  • validate_prerequisites(context) → bool, issues       │
│  • execute(context) → SetupResult                       │
│  • rollback(context) → bool                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           Concrete Setup Modules                         │
│         (src/setup/modules/*.py)                         │
│                                                          │
│  • VisionAPIModule - Enable Vision API                  │
│  • PlatformDetectionModule - Platform config            │
│  • BrainInitializationModule - Init databases           │
│  • PythonDependenciesModule - Install packages          │
│  • ... (easily extensible)                              │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Module Structure

### Base Module Interface

Every setup module implements `BaseSetupModule`:

```python
from src.setup import BaseSetupModule, SetupModuleMetadata, SetupResult

class MyCustomModule(BaseSetupModule):
    def get_metadata(self) -> SetupModuleMetadata:
        """Define module identity and dependencies."""
        return SetupModuleMetadata(
            module_id="my_custom",
            name="My Custom Setup",
            description="What this does",
            phase=SetupPhase.FEATURES,
            priority=10,
            dependencies=["other_module"],  # Run after these
            optional=True
        )
    
    def validate_prerequisites(self, context) -> Tuple[bool, List[str]]:
        """Check if prerequisites are met."""
        issues = []
        if not context.get('required_value'):
            issues.append("Missing required_value")
        return len(issues) == 0, issues
    
    def execute(self, context) -> SetupResult:
        """Perform setup tasks."""
        try:
            # Do setup work
            result = self._do_setup()
            
            # Update context for downstream modules
            context['my_custom_done'] = True
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message="Setup complete",
                details={'result': result}
            )
        except Exception as e:
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=str(e),
                errors=[str(e)]
            )
    
    def rollback(self, context) -> bool:
        """Undo changes if needed."""
        # Optional - implement if rollback possible
        return True
```

### Execution Phases

Modules run in phases with priorities:

1. **PRE_VALIDATION (10)** - Validate environment before setup
2. **ENVIRONMENT (20)** - Platform detection and configuration
3. **DEPENDENCIES (30)** - Install and verify dependencies
4. **FEATURES (40)** - Activate optional features (Vision API, etc.)
5. **VALIDATION (50)** - Validate setup completed successfully
6. **POST_SETUP (60)** - Final tasks and cleanup

Within each phase, modules run by:
- **Priority** (lower number = earlier)
- **Dependencies** (topological sort)

---

## 🎛️ YAML Configuration

### setup_modules.yaml Structure

```yaml
modules:
  - module_id: vision_api
    name: Vision API Activation
    description: Enable GitHub Copilot Vision API
    phase: FEATURES
    priority: 10
    dependencies: [python_dependencies]
    optional: true
    enabled_by_default: false
    config:
      max_tokens_per_image: 500
      cache_results: true

profiles:
  standard:
    description: Recommended for most users
    modules:
      - project_validation
      - platform_detection
      - python_dependencies
      - brain_initialization
      
  full:
    description: All features including Vision API
    modules:
      - project_validation
      - platform_detection
      - python_dependencies
      - vision_api          # ← Vision API enabled in full profile
      - brain_initialization

default_profile: standard
```

---

## 🚀 Usage

### 1. Quick Setup (via Plugin)

```bash
# Use /setup command or natural language
/setup
setup environment
configure cortex
```

The platform_switch_plugin delegates to the setup orchestrator automatically.

### 2. Programmatic Usage

```python
from src.setup import run_setup, create_setup_orchestrator

# Quick setup
report = run_setup(profile='standard')
if report.overall_success:
    print("✅ Setup complete!")

# Full setup with Vision API
report = run_setup(profile='full')

# Custom orchestrator
orchestrator = create_setup_orchestrator(profile='full')
context = {'project_root': Path('/path/to/cortex')}
report = orchestrator.execute_setup(context)

# Check specific module results
vision_result = report.get_module_result('vision_api')
if vision_result.success:
    print(f"Vision API: {vision_result.message}")
```

### 3. Adding New Modules

**Step 1:** Create module class

```python
# src/setup/modules/my_new_module.py
from src.setup import BaseSetupModule, SetupModuleMetadata, SetupResult

class MyNewModule(BaseSetupModule):
    # Implement required methods
    pass
```

**Step 2:** Register in factory

```python
# src/setup/module_factory.py
from .modules.my_new_module import MyNewModule

def _auto_register_modules():
    register_module_class('my_new', MyNewModule)
```

**Step 3:** Add to YAML

```yaml
# src/setup/setup_modules.yaml
modules:
  - module_id: my_new
    name: My New Feature
    description: What it does
    phase: FEATURES
    priority: 20
    dependencies: []
    optional: true
    enabled_by_default: false
```

That's it! Module is now available in all setups.

---

## 🎨 Existing Modules

### Current Modules

| Module ID | Name | Phase | Description |
|-----------|------|-------|-------------|
| `vision_api` | Vision API Activation | FEATURES | Enable GitHub Copilot Vision API for screenshot analysis |
| `project_validation` | Project Structure Validation | PRE_VALIDATION | Verify CORTEX directories exist |
| `platform_detection` | Platform Detection | ENVIRONMENT | Detect Mac/Windows/Linux |
| `git_sync` | Git Repository Sync | ENVIRONMENT | Pull latest code |
| `virtual_environment` | Virtual Environment Setup | ENVIRONMENT | Create/activate venv |
| `python_dependencies` | Python Dependencies | DEPENDENCIES | Install from requirements.txt |
| `brain_initialization` | Brain Database Init | FEATURES | Initialize Tier 1, 2, 3 |
| `brain_tests` | Brain Tests Validation | VALIDATION | Run core brain tests |
| `tooling_verification` | Tooling Verification | VALIDATION | Verify Git, Python, etc. |
| `setup_completion` | Setup Completion | POST_SETUP | Mark setup complete |

### Vision API Module

**What it does:**
- Enables `vision_api.enabled` in `cortex.config.json`
- Sets default configuration (token budgets, caching, etc.)
- Verifies Pillow/PIL for image preprocessing
- Updates context for downstream modules

**When it runs:**
- Included in `full` profile
- User requests with "vision" or "screenshot" keywords
- Can be explicitly enabled in custom profiles

**Configuration:**
```json
{
  "vision_api": {
    "enabled": true,
    "max_tokens_per_image": 500,
    "max_image_size_bytes": 2000000,
    "downscale_threshold": 1920,
    "jpeg_quality": 85,
    "cache_analysis_results": true,
    "cache_ttl_hours": 24,
    "warn_threshold_tokens": 400
  }
}
```

---

## 🧪 Testing

### Test Individual Modules

```python
# tests/setup/test_vision_api_module.py
from src.setup.modules.vision_api_module import VisionAPIModule

def test_vision_api_activation():
    module = VisionAPIModule()
    
    context = {'project_root': Path('/test/cortex')}
    
    # Validate prerequisites
    is_valid, issues = module.validate_prerequisites(context)
    assert is_valid
    
    # Execute module
    result = module.execute(context)
    assert result.success
    assert context['vision_api_enabled'] is True
```

### Test Orchestrator

```python
from src.setup import create_setup_orchestrator

def test_orchestrator_execution_order():
    orchestrator = create_setup_orchestrator(profile='minimal')
    
    context = {'project_root': Path('/test')}
    report = orchestrator.execute_setup(context)
    
    # Check execution order respects dependencies
    module_ids = [r.module_id for r in report.results]
    assert module_ids.index('virtual_environment') < module_ids.index('python_dependencies')
```

---

## 📊 Profiles

### Minimal Profile
- Only required modules
- Fastest setup (~30 seconds)
- For CI/CD environments

### Standard Profile (Default)
- Recommended for most users
- Core features + validation
- Setup time: ~2-3 minutes

### Full Profile
- All modules including optional features
- Vision API, conversation tracking, MkDocs
- Setup time: ~5-8 minutes

---

## 🔄 Migration from Old System

**Old:** Monolithic `_configure_environment()`, `_verify_dependencies()` methods in plugin

**New:** Modular setup orchestrator with YAML-configured modules

### Benefits

1. **Separation of Concerns:** Each module has ONE job
2. **Reusability:** Modules can be reused across different contexts
3. **Testability:** Test each module in isolation
4. **Extensibility:** Add modules without modifying orchestrator
5. **Configuration:** Change behavior via YAML, not code

### Backwards Compatibility

The platform_switch_plugin maintains the same `/setup` command and natural language interface. Users see no difference - the implementation is cleaner under the hood.

---

## 📚 Related Documentation

- `src/setup/base_setup_module.py` - Base interface and data classes
- `src/setup/setup_orchestrator.py` - Orchestration logic
- `src/setup/module_factory.py` - YAML loading and instantiation
- `src/setup/setup_modules.yaml` - Module configuration
- `src/setup/modules/` - Concrete module implementations

---

## 🎯 Future Enhancements

- [ ] Module CLI for testing individual modules
- [ ] Setup dry-run mode (validate without executing)
- [ ] Module marketplace (community-contributed modules)
- [ ] Conditional module execution based on environment
- [ ] Parallel module execution where dependencies allow
- [ ] Setup undo/rollback improvements

---

**Author:** Asif Hussain  
**Last Updated:** 2025-11-09  
**Version:** 2.0 (Modular SOLID Architecture)
