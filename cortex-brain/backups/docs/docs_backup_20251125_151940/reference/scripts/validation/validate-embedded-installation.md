# Validate Embedded Installation

**Author:** Asif Hussain  

CORTEX Embedded Installation Validator

---

**Source:** `scripts/validation/validate_embedded_installation.py`

## Classes

### `Colors`

### `EmbeddedInstallationValidator`

Validates embedded CORTEX installations for upgrade readiness

**Methods:**

- **`validate_all()`**
  Run all validation checks

- **`check_installation_structure()`**
  Check basic CORTEX directory structure

- **`check_version_file()`**
  Check VERSION file exists and is readable

- **`check_brain_databases()`**
  Check brain databases exist and are accessible

- **`check_config_files()`**
  Check configuration files

- **`check_response_templates()`**
  Check response-templates.yaml

- **`check_dependencies()`**
  Check Python requirements

- **`check_embedded_marker()`**
  Check for embedded installation marker

- **`check_parent_project()`**
  Check parent project structure

- **`check_upgrade_system()`**
  Check upgrade system files

- **`print_summary()`**
  Print validation summary

## Functions

### `main()`

CLI entry point
