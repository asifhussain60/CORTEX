# src.setup.module_factory

Setup Module Factory

Discovers and instantiates setup modules from YAML configuration.
Implements Factory pattern for module creation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

## Functions

### `register_module_class(module_id, module_class)`

Register a module class for factory instantiation.

Args:
    module_id: Unique module identifier
    module_class: Class implementing BaseSetupModule

### `load_setup_config(config_path)`

Load setup configuration from YAML.

Args:
    config_path: Path to setup_modules.yaml (default: auto-detect)

Returns:
    Dictionary with modules configuration

### `create_orchestrator_from_yaml(config_path, profile)`

Create a fully configured SetupOrchestrator from YAML config.

Args:
    config_path: Path to setup_modules.yaml
    profile: Profile to use (minimal, standard, full)

Returns:
    SetupOrchestrator with registered modules

### `_auto_register_modules()`

Auto-register all known module classes.
