    Deployment without version tracking detected!

    Operation: '{operation}'

    CRITICAL: .cortex-version file is MANDATORY for:
    - Upgrade detection (setup vs upgrade)
    - Schema migration tracking
    - Rollback capability
    - Version compatibility checks

    Required file structure:
    ```json
    {
      "cortex_version": "5.2.0",
      "schema_version": "1.0",
      "installed_date": "2025-11-23T14:30:00Z",
      "last_upgrade": "2025-11-23T14:30:00Z",
      "workspace_id": "a7b3c4d5e6f7"
    }
    ```

    File location: CORTEX/.cortex-version

  rationale: |
    Version tracking enables intelligent upgrade/setup detection:
    - NO version file → Initial setup (create empty brain)
    - Version file exists → Upgrade (preserve brain, update core)
    - Version comparison → Determine upgrade path & migrations needed

- rule_id: "UPGRADE_BRAIN_PRESERVATION"
  name: "Brain Data Preservation During Upgrades"
  severity: "blocked"
  description: "Upgrade operations MUST NEVER overwrite brain data (conversations, patterns, documents)"

  detection:
    combined_keywords:
      upgrade_operation:
        - "upgrade cortex"
        - "update cortex"
        - "replace cortex"
      and_overwrite_risk:
        - "overwrite all"
        - "replace cortex-brain"
        - "delete CORTEX"
        - "rm -rf CORTEX"
        - "Remove-Item CORTEX"
    scope: ["operation", "command"]
    logic: "AND"

  alternatives:
    - "Use selective file replacement (core only, preserve brain)"
    - "Backup brain data before any upgrade"
    - "Use upgrade package (not full package)"
    - "Verify brain preservation in validation gates"

  evidence_template: |
    Brain data overwrite risk detected!

    Operation: '{operation}'
    Command: '{command}'

    CRITICAL: NEVER overwrite these directories during upgrades:
    - cortex-brain/tier1/*.db (conversations)
    - cortex-brain/tier2/*.db (patterns)
    - cortex-brain/tier3/*.db (development context)
    - cortex-brain/documents/ (user documents)
    - cortex-brain/user-dictionary.yaml (learned terms)
    - cortex.config.json (workspace configuration)

    SAFE upgrade procedure:
    1. Backup brain data first
    2. Replace ONLY: src/, scripts/, .github/
    3. Merge configs: response-templates.yaml, capabilities.yaml
    4. Preserve brain: All .db files, documents/, user-dictionary.yaml
    5. Apply schema migrations if needed
    6. Validate brain integrity

  rationale: |
    Brain data represents workspace-specific learning that cannot be regenerated:
    - Conversation history (127+ conversations typical)
    - Learned patterns (43+ patterns typical)
    - User documents (89+ files typical)
    - Custom configurations

    Loss of brain data = loss of CORTEX intelligence for that workspace.

- rule_id: "SCHEMA_MIGRATION_ENFORCEMENT"
  name: "Database Schema Migration Required"
  severity: "blocked"
  description: "Database schema changes MUST include migration files, never destructive updates"

  detection:
    combined_keywords:
      schema_change:
        - "alter table"
        - "drop table"
        - "change schema"
        - "modify database"
      without_migration:
        - "no migration"
        - "skip migration"
        - "direct schema change"
    scope: ["operation", "sql"]
    logic: "AND"

  alternatives:
    - "Create migration file in cortex-brain/migrations/"
    - "Use migration runner to apply changes"
    - "Write rollback SQL in migration"
    - "Test migration on backup database first"

  evidence_template: |
    Database schema change without migration detected!

    Operation: '{operation}'
    Schema change: '{schema_change}'

    CRITICAL: Schema changes MUST use migration files!

    Required migration structure:
    ```sql
    -- Migration: 003_add_deployment_tracking.sql
    -- Version: 5.3.0
    -- Date: 2025-11-23
    -- Description: Add deployment tracking to tier2

    BEGIN TRANSACTION;

    -- Forward migration
    CREATE TABLE IF NOT EXISTS tier2_deployments (
        deployment_id TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        deployed_at TEXT NOT NULL
    );

    -- Update schema version
    PRAGMA user_version = 3;

    COMMIT;

    -- Rollback migration (commented)
    -- DROP TABLE IF EXISTS tier2_deployments;
    -- PRAGMA user_version = 2;
    ```

    Migration location: cortex-brain/migrations/XXX_description.sql

    Why migrations matter:
    - Preserves data during schema changes
    - Provides rollback capability
    - Documents schema evolution
    - Enables automated upgrades

  rationale: |
    Schema migrations are MANDATORY for:
    1. Data preservation: No data loss during schema changes
    2. Upgrade automation: Apply migrations during upgrade workflow
    3. Rollback safety: Revert schema if upgrade fails
    4. Version tracking: PRAGMA user_version marks schema state
    5. Team coordination: All deployments use same schema version

- rule_id: "DEPLOYMENT_TYPE_DETECTION"
  name: "Intelligent Deployment Type Detection"
  severity: "warning"
  description: "Deployment operations should auto-detect setup vs upgrade mode"

  detection:
    keywords:
      - "manual deployment"
      - "copy folder"
      - "replace directory"
      - "user must choose"
    scope: ["operation", "workflow"]

  alternatives:
    - "Auto-detect: No CORTEX/ → Setup mode"
    - "Auto-detect: CORTEX/ exists → Upgrade mode"
    - "Check .cortex-version for version comparison"
    - "Provide dry-run mode for preview"

  evidence_template: |
    Manual deployment workflow detected: '{operation}'

    CORTEX should auto-detect deployment type:

    Detection Logic:
    ```python
    if not cortex_dir.exists():
        return DeploymentType.INITIAL_SETUP
    elif not version_file.exists():
        return DeploymentType.LEGACY_UPGRADE
    elif current_version < latest_version:
        return DeploymentType.UPGRADE
    else:
        return DeploymentType.UP_TO_DATE
    ```

    User Experience:
    - "setup cortex" → Auto-detects mode
    - "upgrade cortex" → Auto-detects mode
    - No manual decision needed

  rationale: |
    Intelligent detection improves user experience:
    - No "am I upgrading or setting up?" confusion
    - Automatic brain preservation in upgrade mode
    - Correct package download (full vs upgrade)
    - Reduced human error

- rule_id: "CONFIG_MERGE_INTELLIGENCE"
  name: "Config Files Require 3-Way Merge"
  severity: "blocked"
  description: "Config files (YAML) must use 3-way merge during upgrades, not overwrite"

  detection:
    combined_keywords:
      upgrade_operation:
        - "upgrade"
        - "update config"
      and_overwrite:
        - "overwrite yaml"
        - "replace config"
        - "copy config"
    scope: ["operation"]
    logic: "AND"

  alternatives:
    - "Use 3-way merge: Base + Local + Upgrade → Merged"
    - "Preserve user customizations (local changes)"
    - "Add new features from upgrade"
    - "Detect conflicts and offer resolution"

  evidence_template: |
    Config overwrite detected during upgrade!

    File: '{file_path}'
    Operation: '{operation}'

    CRITICAL: Config files need intelligent merging!

    3-Way Merge Process:
    ```
    Base Config (v5.1.0 - original)
        +
    Local Config (user customizations)
        +
    Upgrade Config (v5.2.0 - new features)
        =
    Merged Config (customizations + new features)
    ```

    Example - response-templates.yaml:
    Base: triggers: ["help"]
    Local: triggers: ["help", "cortex help"] ← User added
    Upgrade: triggers: ["help"], new_template: admin_help
    Merged: triggers: ["help", "cortex help"], new_template: admin_help

    Preserve:
    - User-added triggers
    - Custom templates
    - Modified capabilities

    Add:
    - New templates from upgrade
    - New capabilities
    - New operations

  rationale: |
    Config merging prevents loss of user customizations:
    - User spent time configuring CORTEX
    - Custom triggers, templates, operations
    - Should be preserved during upgrades
    - New features added alongside customizations

- rule_id: "PUBLISH_PACKAGE_VALIDATION"
  name: "Publish Package Content Validation"
  severity: "blocked"
  description: "Published packages MUST NOT contain brain data or machine-specific files"

  detection:
    combined_keywords:
      publish_operation:
        - "build package"
        - "create publish"
        - "generate release"
      privacy_risk:
        - "*.db included"
        - "brain data included"
        - "machine paths included"
    scope: ["operation", "validation"]
    logic: "AND"

  alternatives:
    - "Exclude all .db files from publish"
    - "Exclude cortex.config.json (machine-specific)"
    - "Exclude .platform_state.json"
    - "Use publish-config.yaml validation rules"

  evidence_template: |
    Privacy/data leak risk in publish package!

    Package: '{package_path}'
    Risk: '{risk_type}'

    CRITICAL: Published packages MUST NOT contain:
    - *.db files (brain data)
    - cortex.config.json (machine-specific paths)
    - .platform_state.json (hostname)
    - .coverage.* (machine names)
    - conversation-history.jsonl (private conversations)

    Validation checklist:
    ✅ No .db files
    ✅ No machine-specific configs
    ✅ No hostnames/usernames
    ✅ No conversation data
    ✅ Only core CORTEX code

    Use forbidden_patterns from publish-config.yaml

  rationale: |
    Privacy protection in published packages:
    - Brain data is workspace-specific (never shared)
    - Machine paths reveal private directory structure
    - Conversation history is confidential
    - Published packages = clean core only
