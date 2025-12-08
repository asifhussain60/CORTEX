# Version Detector

**Author:** Asif Hussain  

CORTEX Version Detection Module

---

**Source:** `scripts/operations/version_detector.py`

## Classes

Reference documentation for classes. See related guides for practical examples.

### `VersionDetector`

Detects CORTEX deployment type and manages version tracking.

**Methods:**

- **`detect_deployment_type()`**
  Detect if this is a fresh setup or existing installation.

- **`get_current_version()`**
  Read current installed version from VERSION file.

- **`get_latest_version()`**
  Get latest available CORTEX version from VERSION file.

- **`create_version_file(version, deployment_type, workspace_id, customizations)`**
  Create .cortex-version file for tracking.

- **`update_version_file(updates)`**
  Update specific fields in version file.

- **`validate_version_file()`**
  Validate .cortex-version file structure and contents.

- **`compare_versions(version1, version2)`**
  Compare two semantic version strings.

- **`is_upgrade_available()`**
  Check if an upgrade is available.

- **`get_upgrade_info()`**
  Get comprehensive upgrade information.

## Functions

Reference documentation for functions. See related guides for practical examples.

### `main()`

CLI entry point for testing version detection.
