# Build User Deployment

**Author:** Asif Hussain  

CORTEX User Deployment Package Builder

---

**Source:** `scripts/build_user_deployment.py`

## Functions

Reference documentation for functions. See related guides for practical examples.

### `load_operations_config(project_root)`

Load operations configuration from YAML.

### `get_user_modules(operations_config, user_ops)`

Extract all modules needed for user operations.

### `filter_operations_yaml(operations_config, user_ops)`

Create filtered operations YAML with only user operations.

### `should_include_path(path, project_root)`

Check if path should be INCLUDED in deployment (strict allowlist).

### `copy_project_structure(project_root, output_dir, user_modules, dry_run)`

Copy project structure with filtering.

### `create_user_requirements(project_root, output_dir, dry_run)`

Create filtered requirements.txt for user package.

### `create_user_readme(output_dir, dry_run)`

Create user-focused README.

### `copy_bootstrap_prompt(project_root, output_dir, dry_run)`

Copy bootstrap CORTEX.prompt.md to package root for user repos.

### `build_deployment_package(project_root, output_dir, dry_run)`

Build complete user deployment package.

### `main()`

Main entry point.
