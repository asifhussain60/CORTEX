# 3-Tier Manifest JSON Schemas

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Version:** 2.0.0  
**Created:** December 22, 2025

---

## 📋 Overview

This directory contains JSON Schema definitions for validating CORTEX's 3-Tier Manifest Architecture:

1. **CoreManifest Schema** - Orchestrator registry and metadata
2. **ConfigManifest Schema** - Runtime configuration and rules
3. **IntegrationManifest Schema** - External system integrations

All schemas follow **JSON Schema Draft-07** specification.

---

## 📁 Files

| Schema | File | Purpose |
|--------|------|---------|
| **CoreManifest** | `core-manifest-schema-v2.json` | Validate orchestrator registry |
| **ConfigManifest** | `config-manifest-schema-v2.json` | Validate runtime configuration |
| **IntegrationManifest** | `integration-manifest-schema-v2.json` | Validate external integrations |

---

## 🚀 Usage

### Python (jsonschema library)

```python
import json
import yaml
from jsonschema import validate, ValidationError
from pathlib import Path

# Load schema
schema_path = Path("cortex-brain/manifests/schemas/core-manifest-schema-v2.json")
with open(schema_path, 'r') as f:
    schema = json.load(f)

# Load manifest
manifest_path = Path("cortex-brain/manifests/core-manifest.yaml")
with open(manifest_path, 'r') as f:
    manifest = yaml.safe_load(f)

# Validate
try:
    validate(instance=manifest, schema=schema)
    print("✅ Manifest is valid")
except ValidationError as e:
    print(f"❌ Validation failed: {e.message}")
    print(f"   Path: {'.'.join(str(p) for p in e.path)}")
```

### Command Line (ajv-cli)

```bash
# Install ajv-cli
npm install -g ajv-cli

# Validate CoreManifest
ajv validate \
  -s cortex-brain/manifests/schemas/core-manifest-schema-v2.json \
  -d cortex-brain/manifests/core-manifest.yaml \
  --spec=draft7

# Validate ConfigManifest
ajv validate \
  -s cortex-brain/manifests/schemas/config-manifest-schema-v2.json \
  -d cortex-brain/manifests/config-manifest.yaml \
  --spec=draft7

# Validate IntegrationManifest
ajv validate \
  -s cortex-brain/manifests/schemas/integration-manifest-schema-v2.json \
  -d cortex-brain/manifests/integration-manifest.yaml \
  --spec=draft7
```

### VS Code Integration

Add to `.vscode/settings.json`:

```json
{
  "yaml.schemas": {
    "cortex-brain/manifests/schemas/core-manifest-schema-v2.json": [
      "cortex-brain/manifests/core-manifest.yaml"
    ],
    "cortex-brain/manifests/schemas/config-manifest-schema-v2.json": [
      "cortex-brain/manifests/config-manifest.yaml"
    ],
    "cortex-brain/manifests/schemas/integration-manifest-schema-v2.json": [
      "cortex-brain/manifests/integration-manifest.yaml"
    ]
  }
}
```

---

## 📐 Schema Design

### CoreManifest Schema

**Required Fields:**
- `schema_version` - Schema version (e.g., "2.0")
- `manifest_type` - Must be "core"
- `orchestrators` - Registry of orchestrators (min 1)

**Orchestrator Requirements:**
- `version` - Semantic version (x.y.z)
- `status` - One of: draft, active, deprecated, archived
- `category` - One of: planning, tdd, execution, analysis, deployment, maintenance
- `description` - Minimum 50 characters
- `source_file` - Path matching `src/**/*.py`

**Key Validations:**
- Version format: `^[0-9]+\.[0-9]+\.[0-9]+$`
- Orchestrator ID: `^[a-z_]+$` (lowercase, underscores only)
- Config references: `^config://.*$`
- Integration references: `^integration://.*$`

### ConfigManifest Schema

**Required Fields:**
- `schema_version` - Schema version
- `manifest_type` - Must be "config"
- `categories` - Must include: cleanup, refactoring, testing

**Key Validations:**
- Enforcement levels: strict, warning, disabled
- Test coverage: 0-100 (percentage)
- Feature flags: Must start with `enable_`

### IntegrationManifest Schema

**Required Fields:**
- `schema_version` - Schema version
- `manifest_type` - Must be "integration"
- `integrations` - Registry of integrations (min 1)

**Integration Requirements:**
- `id` - Pattern: `^integration://.*$`
- `name` - Minimum 3 characters
- `adapter.class_name` - Pattern: `^[A-Z][a-zA-Z0-9]+Adapter$`
- `adapter.module_path` - Pattern: `^src\..*`
- `adapter.version` - Semantic version

**Key Validations:**
- Auth methods: PAT, OAuth2, API_KEY, none
- HTTP methods: GET, POST, PUT, PATCH, DELETE
- Backoff strategies: linear, exponential, fixed

---

## 🔍 Validation Examples

### Valid CoreManifest Example

```yaml
schema_version: "2.0"
manifest_type: "core"
last_updated: "2025-12-22T00:00:00Z"

orchestrators:
  planning_orchestrator:
    version: "4.0.1"
    status: "active"
    category: "planning"
    description: "Tiered planning system with intelligent routing for HIGH/MEDIUM/LOW complexity features"
    source_file: "src/operations/modules/orchestration/planning_orchestrator.py"
    entry_point: "PlanningOrchestrator"
    config_overrides:
      namespace: "config://planning"
      sections:
        - "refactoring.planning"
    integrations:
      - "integration://github"
```

### Invalid CoreManifest Examples

```yaml
# ❌ Missing required field
orchestrators:
  planning_orchestrator:
    version: "4.0.1"
    status: "active"
    # Missing: category, description, source_file

# ❌ Invalid version format
orchestrators:
  planning_orchestrator:
    version: "v4.0.1"  # Should be "4.0.1"

# ❌ Invalid category
orchestrators:
  planning_orchestrator:
    category: "custom"  # Must be one of: planning, tdd, execution, etc.

# ❌ Invalid config reference
orchestrators:
  planning_orchestrator:
    config_overrides:
      namespace: "planning"  # Should be "config://planning"
```

---

## 🛠️ Schema Development

### Adding New Fields

1. Update JSON Schema file
2. Add validation rules
3. Update examples in schema
4. Test with valid/invalid manifests
5. Update this README

### Testing Schemas

```python
import pytest
from jsonschema import validate, ValidationError

def test_core_manifest_valid():
    """Test valid CoreManifest"""
    manifest = {
        "schema_version": "2.0",
        "manifest_type": "core",
        "orchestrators": {
            "test_orch": {
                "version": "1.0.0",
                "status": "active",
                "category": "planning",
                "description": "Test orchestrator with minimum required fields for validation testing",
                "source_file": "src/test_orch.py"
            }
        }
    }
    validate(instance=manifest, schema=core_schema)
    # Should not raise ValidationError

def test_core_manifest_invalid_version():
    """Test invalid version format"""
    manifest = {
        "schema_version": "2.0",
        "manifest_type": "core",
        "orchestrators": {
            "test_orch": {
                "version": "v1.0.0",  # Invalid format
                "status": "active",
                "category": "planning",
                "description": "Test orchestrator",
                "source_file": "src/test_orch.py"
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=manifest, schema=core_schema)
```

---

## 📊 Validation Coverage

| Schema | Total Rules | Required Fields | Pattern Validations | Enum Validations |
|--------|-------------|-----------------|---------------------|------------------|
| **CoreManifest** | 45+ | 5 | 8 | 4 |
| **ConfigManifest** | 30+ | 3 | 2 | 2 |
| **IntegrationManifest** | 40+ | 4 | 6 | 5 |

---

## 🔗 Related Documentation

- [3-Tier Manifest Architecture](../../../documents/architecture/3-tier-manifest-architecture.md)
- [Manifest Consolidation Analysis](../../../documents/analysis/phase-7-manifest-consolidation-analysis.md)
- [JSON Schema Specification](https://json-schema.org/draft-07/schema)
- [YAML 1.2 Specification](https://yaml.org/spec/1.2/spec.html)

---

## 🚨 Common Validation Errors

### Error: "Additional properties are not allowed"

```yaml
# ❌ Typo in field name
orchestrators:
  test_orch:
    versoin: "1.0.0"  # Typo: should be "version"
```

**Fix:** Check field names match schema exactly

### Error: "'version' does not match pattern"

```yaml
# ❌ Invalid version format
version: "v4.0.1"  # Should be "4.0.1"
version: "4.0"     # Should be "4.0.0"
```

**Fix:** Use semantic versioning (x.y.z)

### Error: "'description' is too short"

```yaml
# ❌ Description under 50 characters
description: "Planning orchestrator"  # Only 22 characters
```

**Fix:** Provide detailed description (min 50 characters)

### Error: "'config_overrides.namespace' does not match pattern"

```yaml
# ❌ Missing namespace prefix
config_overrides:
  namespace: "planning"  # Should be "config://planning"
```

**Fix:** Use `config://` prefix for config references

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0.0** | 2025-12-22 | Initial 3-Tier Manifest Schema release |
| | | - CoreManifest schema with orchestrator registry |
| | | - ConfigManifest schema with runtime config |
| | | - IntegrationManifest schema with external systems |

---

**Status:** ✅ Production Ready  
**Maintenance:** Active (aligned with manifest architecture)
