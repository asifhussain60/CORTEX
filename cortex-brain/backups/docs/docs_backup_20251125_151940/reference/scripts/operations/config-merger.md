# Config Merger

**Author:** Asif Hussain  

CORTEX Config Merger Module

---

**Source:** `scripts/operations/config_merger.py`

## Classes

### `ConfigMerger`

Intelligently merges YAML configuration files during upgrades.

**Methods:**

- **`merge_yaml_files(base_file, local_file, upgrade_file, output_file)`**
  Perform 3-way merge of YAML files.

- **`merge_response_templates(local_file, upgrade_file, output_file)`**
  Merge response-templates.yaml with special handling for template arrays.

- **`merge_capabilities(local_file, upgrade_file, output_file)`**
  Merge capabilities.yaml with special handling for operation arrays.

- **`detect_conflicts(base_data, local_data, upgrade_data)`**
  Detect merge conflicts.

- **`generate_merge_report(output_file)`**
  Generate detailed merge report.

## Functions

### `main()`

CLI entry point for testing config merger.
