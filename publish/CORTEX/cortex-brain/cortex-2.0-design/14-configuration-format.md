# CORTEX 2.0 Configuration Format (cortex.config.json v2)

**Document:** 14-configuration-format.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose
Define the v2 configuration format that is:
- Explicit (typed), minimal, and environment-agnostic
- Plugin-first and safely overrideable per project
- Backwards-aware (v1 → v2 migration guidance)
- Validated at startup with clear errors and defaults

---

## 🧱 Principles
- Paths are relative to workspace root; resolved via PathResolver
- No hard-coded OS-specific paths or separators
- Separate core defaults from project overrides
- Strict schema validation; fail fast on invalid keys/types

---

## 🗂️ File Layout

Recommended files:
- `cortex.config.json` (project overrides)
- `cortex.config.template.json` (starter template)
- `cortex.config.example.json` (full example with comments)

---

## 🧩 Top-Level Structure (v2)

```json
{
  "$schema": "./schemas/cortex.config.v2.schema.json",
  "version": "2.0",
  "environment": {
    "platform": "auto",                // auto|windows|linux|macos
    "workspaceRoot": "./"              // relative root
  },
  "paths": {
    "brainRoot": "cortex-brain/",
    "docsRoot": "docs/",
    "scriptsRoot": "scripts/",
    "tempRoot": "cortex-brain/crawler-temp/",
    "backupsRoot": "cortex-brain/backups/",
    "coldStorageRoot": "cortex-brain/cold_storage/"
  },
  "databases": {
    "tier1": { "path": "cortex-brain/left-hemisphere/tier1.db" },
    "tier2": { "path": "cortex-brain/right-hemisphere/tier2.db" },
    "tier3": { "path": "cortex-brain/brain-archives/tier3.db" }
  },
  "plugins": {
    "enabled": [
      "self_review_plugin",
      "db_maintenance_plugin",
      "incremental_creation_plugin"
    ],
    "disabled": [],
    "config": {
      "self_review_plugin": {
        "auto_fix": true,
        "schedule": "daily@02:00"
      },
      "db_maintenance_plugin": {
        "auto_vacuum_enabled": true,
        "auto_archival_enabled": true,
        "maintenance_schedule": "weekly@Sun-03:00"
      }
    }
  },
  "databaseMaintenance": {
    "fragmentationThreshold": 0.2,
    "vacuumThreshold": 0.15,
    "analyzeDays": 7,
    "retentionPolicies": {
      "tier1": { "maxAgeDays": 30, "maxRecords": 20, "archiveDestination": "tier3" },
      "tier2": { "maxAgeDays": 180, "maxRecords": 10000, "archiveDestination": "tier3", "pruneLowConfidence": true, "confidenceThreshold": 0.3 },
      "tier3": { "maxAgeDays": 730, "maxRecords": -1, "archiveDestination": "cold_storage", "compressionEnabled": true }
    }
  },
  "incrementalCreation": {
    "enabled": true,
    "maxChunkLines": 200,
    "maxChunkTokens": 4000,
    "progressDir": ".cortex/creation-progress"
  },
  "workflows": {
    "conversation": { "contextInjection": "targeted", "maxTier1Conversations": 20, "autoArchiveDays": 30 },
    "ops": { "selfReviewDaily": true, "dbMaintenanceWeekly": true }
  },
  "telemetry": {
    "healthReportPath": "cortex-brain/corpus-callosum/health-report.txt",
    "logLevel": "info"
  }
}
```

---

## 🧪 JSON Schema (excerpt)

`schemas/cortex.config.v2.schema.json`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/cortex.config.v2.schema.json",
  "title": "CORTEX v2 Config",
  "type": "object",
  "required": ["version", "paths", "databases", "plugins"],
  "properties": {
    "version": { "type": "string", "const": "2.0" },
    "environment": {
      "type": "object",
      "properties": {
        "platform": { "enum": ["auto", "windows", "linux", "macos"] },
        "workspaceRoot": { "type": "string" }
      },
      "additionalProperties": false
    },
    "paths": {
      "type": "object",
      "required": ["brainRoot", "docsRoot"],
      "properties": {
        "brainRoot": { "type": "string" },
        "docsRoot": { "type": "string" },
        "scriptsRoot": { "type": "string" },
        "tempRoot": { "type": "string" },
        "backupsRoot": { "type": "string" },
        "coldStorageRoot": { "type": "string" }
      },
      "additionalProperties": false
    },
    "databases": {
      "type": "object",
      "required": ["tier1", "tier2", "tier3"],
      "properties": {
        "tier1": { "type": "object", "required": ["path"], "properties": { "path": { "type": "string" } }, "additionalProperties": false },
        "tier2": { "type": "object", "required": ["path"], "properties": { "path": { "type": "string" } }, "additionalProperties": false },
        "tier3": { "type": "object", "required": ["path"], "properties": { "path": { "type": "string" } }, "additionalProperties": false }
      },
      "additionalProperties": false
    },
    "plugins": {
      "type": "object",
      "required": ["enabled", "config"],
      "properties": {
        "enabled": { "type": "array", "items": { "type": "string" } },
        "disabled": { "type": "array", "items": { "type": "string" } },
        "config": { "type": "object" }
      }
    }
  },
  "additionalProperties": false
}
```

---

## 🔄 v1 → v2 Migration Mapping

Common v1 keys and their v2 equivalents:

| v1 Key | v2 Path | Notes |
|-------|---------|-------|
| `brain.path` | `paths.brainRoot` | Ensure relative path |
| `docs.path` | `paths.docsRoot` | Clean trailing slashes |
| `db.tier1` | `databases.tier1.path` | Convert to string if object |
| `db.tier2` | `databases.tier2.path` |  |
| `db.tier3` | `databases.tier3.path` |  |
| `plugins` (flat list) | `plugins.enabled` | Move per-plugin options into `plugins.config` |
| `maintenance.*` | `databaseMaintenance.*` | Rename + camelCase |
| `incremental.*` | `incrementalCreation.*` | Rename section |

Provide a small Python migrator script (see Doc 12) to transform config files with safety backups.

---

## ✅ Validation at Startup

- Load config JSON
- Validate against JSON Schema
- Resolve relative paths using PathResolver
- Verify DB files exist or can be created
- Verify enabled plugins are known; unknown → warning (not fatal)
- Emit normalized config for downstream components

---

## 🧪 Examples

### Minimal Project Config
```json
{
  "version": "2.0",
  "paths": { "brainRoot": "cortex-brain/", "docsRoot": "docs/" },
  "databases": {
    "tier1": { "path": "cortex-brain/tier1.db" },
    "tier2": { "path": "cortex-brain/tier2.db" },
    "tier3": { "path": "cortex-brain/tier3.db" }
  },
  "plugins": { "enabled": ["self_review_plugin"], "disabled": [], "config": {} }
}
```

### Full Example (Project)
Reference: `cortex.config.example.json` updated to v2 format (see PR checklist below).

---

## 📋 PR Checklist for Config Changes

- Update `cortex.config.example.json` to v2
- Add `schemas/cortex.config.v2.schema.json`
- Backwards-compat migration script (optional helper)
- Update PathResolver to honor v2 keys
- Add tests for schema validation + path resolution

---

**Next:** 15-api-changes.md (Agent interfaces and new abstractions)
