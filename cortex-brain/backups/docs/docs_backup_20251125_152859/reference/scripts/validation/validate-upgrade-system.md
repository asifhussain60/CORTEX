# Validate Upgrade System

**Author:** Asif Hussain  

CORTEX Upgrade System Validator

---

**Source:** `scripts/validation/validate_upgrade_system.py`

## Classes

Reference documentation for classes. See related guides for practical examples.

### `Colors`

### `UpgradeSystemValidator`

Validates upgrade system functionality

**Methods:**

- **`run_all_tests()`**
  Run all upgrade system validation tests

- **`test_version_file_plain_text()`**
  Test VERSION file reading (plain text format)

- **`test_version_file_legacy_json()`**
  Test VERSION file reading (legacy JSON format)

- **`test_version_file_missing()`**
  Test VERSION file missing scenario

- **`test_version_strip_prefix()`**
  Test version prefix stripping

- **`test_version_comparison()`**
  Test version comparison logic

- **`test_config_merger_dict_templates()`**
  Test config merger handles dictionary template format

- **`test_config_merger_none_values()`**
  Test config merger handles None values gracefully

- **`test_config_merger_type_safety()`**
  Test config merger handles non-dict values

- **`test_upgrade_info_string_version()`**
  Test get_upgrade_info handles string version format

- **`test_upgrade_info_dict_version()`**
  Test get_upgrade_info handles dict version format (legacy)

- **`print_summary()`**
  Print validation summary

## Functions

Reference documentation for functions. See related guides for practical examples.

### `main()`

Run upgrade system validation
