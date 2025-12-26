# 3-Tier Manifest Architecture Design

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 22, 2025  
**Version:** 1.0.0  
**Status:** 🏗️ IN DESIGN

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [CoreManifest Schema](#coremanifest-schema)
4. [ConfigManifest Schema](#configmanifest-schema)
5. [IntegrationManifest Schema](#integrationmanifest-schema)
6. [Inheritance Model](#inheritance-model)
7. [Cross-Referencing Strategy](#cross-referencing-strategy)
8. [Migration Strategy](#migration-strategy)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Validation & Testing](#validation--testing)

---

## 🎯 Executive Summary

**Problem:**
- **37 YAML manifest files** totaling **21,594 lines**
- **60-70% redundancy** in metadata, rules, and configuration
- **Fragmented inheritance** (multiple base manifests)
- **Scattered configuration** (8+ separate rule files)

**Solution: 3-Tier Manifest Architecture**

| Tier | Purpose | Lines | Reduction |
|------|---------|-------|-----------|
| **CoreManifest** | Orchestrator registry & metadata | ~800 | -82% (from 4,700) |
| **ConfigManifest** | Runtime configuration & rules | ~1,200 | -73% (from 4,500) |
| **IntegrationManifest** | External system integrations | ~500 | -88% (from ~4,000) |
| **TOTAL** | All manifests | **~2,500** | **-88% (from 21,594)** |

**Key Features:**
- ✅ **Single source of truth** for each concern (orchestrators, config, integrations)
- ✅ **Inheritance model** with deep merge strategy
- ✅ **Cross-referencing** via namespaced IDs
- ✅ **JSON Schema validation** for all 3 manifests
- ✅ **Backward compatibility** via ManifestMigrationAdapter

---

## 🏗️ Architecture Overview

### Conceptual Model

```
┌─────────────────────────────────────────────────────────────┐
│                     3-TIER MANIFEST SYSTEM                   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │   ManifestLoader  │
                    │  (orchestrates)   │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ CoreManifest  │   │ConfigManifest │   │Integration    │
│               │   │               │   │Manifest       │
│ Orchestrators │   │ Rules & Config│   │ External APIs │
│ Metadata      │◄──┤ Behavior      │   │ Adapters      │
│ Relationships │   │ Overrides     │   │ Auth          │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Orchestrator   │
                    │   Instance      │
                    │  (uses merged   │
                    │   manifest)     │
                    └─────────────────┘
```

### Design Principles

1. **Separation of Concerns**
   - **CoreManifest:** WHO (orchestrators, versions, metadata)
   - **ConfigManifest:** HOW (rules, behaviors, thresholds)
   - **IntegrationManifest:** WHERE (external systems, APIs)

2. **Single Source of Truth**
   - Each manifest owns ONE domain
   - No duplication across manifests
   - Cross-references use namespaced IDs

3. **Inheritance Over Duplication**
   - Base schemas define common fields
   - Child manifests override/extend
   - Deep merge strategy (child overrides parent)

4. **Runtime Composition**
   - ManifestLoader resolves inheritance
   - Merges cross-references
   - Validates against JSON Schema
   - Caches resolved manifests

---

## 📦 CoreManifest Schema

### Purpose
Single registry for all orchestrators, their metadata, versions, and relationships.

### Schema Definition (YAML)

```yaml
schema_version: "2.0"
manifest_type: "core"
last_updated: "2025-12-22T00:00:00Z"

# ========================================
# Global Defaults (inherited by all)
# ========================================

defaults:
  schema_version: "1.0"
  deployment_tier: "user"  # cortex|user|admin|dual_context
  maintainer: "CORTEX Development Team"
  status: "active"  # draft|active|deprecated|archived
  logging:
    level: "INFO"
    format: "structured"
    destinations:
      - type: "console"
        enabled: true
      - type: "file"
        enabled: true
        path: "logs/{orchestrator_name}.log"

# ========================================
# Orchestrator Registry
# ========================================

orchestrators:
  
  # Example: Planning Orchestrator
  planning_orchestrator:
    # Metadata
    version: "4.0.1"
    status: "active"
    category: "planning"
    description: "Tiered planning system with intelligent routing (HIGH/MEDIUM/LOW complexity)"
    
    # Implementation
    source_file: "src/operations/modules/orchestration/planning_orchestrator.py"
    entry_point: "PlanningOrchestrator"
    
    # Documentation
    documentation_path: ".github/prompts/modules/planning-system-guide.md"
    changelog_path: "docs/orchestration/planning-system-changelog.md"
    
    # Relationships
    inherits_from: null  # Top-level orchestrator
    parent_orchestrator: null
    child_orchestrators:
      - "tdd_orchestrator"
      - "ado_planning_orchestrator"
      - "sanitization_orchestrator"
    related_orchestrators:
      - "maintenance_orchestrator"
      - "git_checkpoint_orchestrator"
    
    # Configuration References (cross-manifest)
    config_overrides:
      namespace: "config://planning"  # References ConfigManifest
      sections:
        - "refactoring.planning"
        - "token_optimization.planning"
        - "documentation.planning"
    
    # Integration References (cross-manifest)
    integrations:
      - "integration://github"  # References IntegrationManifest
      - "integration://file_system"
    
    # Deployment
    deployment_tier: "dual_context"  # Override default
    enabled: true
    auto_start: false
    
    # Quality Gates
    quality_gates:
      min_test_coverage: 80  # percentage
      max_complexity: 30     # cyclomatic complexity
      required_reviews: 1
      must_pass_linting: true
    
    # Versioning
    created_date: "2024-01-15"
    last_updated: "2025-12-20"
    deprecated_versions:
      - "3.0.0"
      - "2.0.0"
  
  # Example: TDD Orchestrator
  tdd_orchestrator:
    version: "4.0.0"
    status: "active"
    category: "tdd"
    description: "Unified TDD orchestrator with adaptive learning and RED→GREEN→REFACTOR enforcement"
    
    source_file: "src/orchestrators/tdd/tdd_orchestrator.py"
    entry_point: "TDDOrchestrator"
    documentation_path: ".github/prompts/modules/tdd-orchestrator-guide.md"
    
    # Inheritance
    inherits_from: "planning_orchestrator"  # Inherits config from parent
    parent_orchestrator: "planning_orchestrator"
    child_orchestrators: []
    
    # Config overrides
    config_overrides:
      namespace: "config://tdd"
      sections:
        - "refactoring.tdd"
        - "testing.tdd"
    
    integrations:
      - "integration://file_system"
      - "integration://github"
    
    quality_gates:
      min_test_coverage: 95  # TDD requires higher coverage
      max_complexity: 20     # TDD enforces lower complexity
      required_reviews: 2
    
    created_date: "2024-11-01"
    last_updated: "2025-12-15"
  
  # Example: ADO Planning Orchestrator
  ado_planning_orchestrator:
    version: "2.0.0"
    status: "active"
    category: "planning"
    description: "Azure DevOps work item generation from planning manifests"
    
    source_file: "src/orchestrators/ado/ado_planning_orchestrator.py"
    entry_point: "ADOPlanningOrchestrator"
    documentation_path: "docs/orchestration/ado-planning-guide.md"
    
    inherits_from: "planning_orchestrator"
    parent_orchestrator: "planning_orchestrator"
    
    config_overrides:
      namespace: "config://ado"
      sections:
        - "ado.work_items"
        - "ado.formatting"
    
    integrations:
      - "integration://azure_devops"  # ADO-specific integration
      - "integration://file_system"
    
    quality_gates:
      min_test_coverage: 75
      max_complexity: 25
    
    created_date: "2024-06-10"
    last_updated: "2025-12-18"
  
  # ... 13 more orchestrators ...

# ========================================
# Categories (taxonomy)
# ========================================

categories:
  planning:
    description: "Orchestrators that create execution plans and strategies"
    orchestrators:
      - "planning_orchestrator"
      - "ado_planning_orchestrator"
  
  tdd:
    description: "Test-driven development workflow orchestrators"
    orchestrators:
      - "tdd_orchestrator"
  
  execution:
    description: "Orchestrators that execute predefined workflows"
    orchestrators:
      - "sanitization_orchestrator"
      - "maintenance_orchestrator"
  
  analysis:
    description: "Code analysis and discovery orchestrators"
    orchestrators:
      - "cortex_lens_v3"
      - "debug_orchestrator"
  
  deployment:
    description: "Deployment and publishing orchestrators"
    orchestrators:
      - "publish_orchestrator"
  
  maintenance:
    description: "System health and cleanup orchestrators"
    orchestrators:
      - "maintenance_orchestrator"
      - "refactoring_orchestrator"

# ========================================
# Deprecation & Migration
# ========================================

deprecated:
  orchestrators:
    planning_orchestrator_v2:
      deprecated_date: "2024-11-01"
      replacement: "planning_orchestrator"
      removal_date: "2025-03-01"
      migration_guide: "docs/migration/planning-v2-to-v4.md"
  
  manifests:
    planning-system-manifest.yaml:
      deprecated_date: "2025-12-22"
      replacement: "core-manifest.yaml"
      removal_date: "2026-01-15"
      backward_compatible: true

# ========================================
# Validation Rules
# ========================================

validation:
  required_fields:
    - "orchestrators.*.version"
    - "orchestrators.*.status"
    - "orchestrators.*.category"
    - "orchestrators.*.description"
    - "orchestrators.*.source_file"
  
  allowed_statuses:
    - "draft"
    - "active"
    - "deprecated"
    - "archived"
  
  allowed_categories:
    - "planning"
    - "tdd"
    - "execution"
    - "analysis"
    - "deployment"
    - "maintenance"
  
  version_format: "semantic"  # x.y.z
```

### JSON Schema (for validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://cortex.dev/schemas/core-manifest-v2.json",
  "title": "CORTEX Core Manifest",
  "description": "Orchestrator registry and metadata",
  "type": "object",
  "required": ["schema_version", "manifest_type", "orchestrators"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Schema version (e.g., 2.0)"
    },
    "manifest_type": {
      "type": "string",
      "const": "core",
      "description": "Must be 'core'"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    },
    "defaults": {
      "type": "object",
      "properties": {
        "schema_version": {"type": "string"},
        "deployment_tier": {
          "type": "string",
          "enum": ["cortex", "user", "admin", "dual_context"]
        },
        "maintainer": {"type": "string"},
        "status": {
          "type": "string",
          "enum": ["draft", "active", "deprecated", "archived"]
        },
        "logging": {"type": "object"}
      }
    },
    "orchestrators": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "required": ["version", "status", "category", "description", "source_file"],
          "properties": {
            "version": {
              "type": "string",
              "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
              "description": "Semantic version (x.y.z)"
            },
            "status": {
              "type": "string",
              "enum": ["draft", "active", "deprecated", "archived"]
            },
            "category": {
              "type": "string",
              "enum": ["planning", "tdd", "execution", "analysis", "deployment", "maintenance"]
            },
            "description": {
              "type": "string",
              "minLength": 50,
              "description": "Minimum 50 characters"
            },
            "source_file": {
              "type": "string",
              "pattern": "^src/.*\\.py$"
            },
            "entry_point": {
              "type": "string",
              "description": "Class name of orchestrator"
            },
            "documentation_path": {"type": "string"},
            "changelog_path": {"type": "string"},
            "inherits_from": {
              "type": ["string", "null"],
              "description": "Parent orchestrator ID"
            },
            "parent_orchestrator": {
              "type": ["string", "null"]
            },
            "child_orchestrators": {
              "type": "array",
              "items": {"type": "string"}
            },
            "related_orchestrators": {
              "type": "array",
              "items": {"type": "string"}
            },
            "config_overrides": {
              "type": "object",
              "properties": {
                "namespace": {
                  "type": "string",
                  "pattern": "^config://.*$"
                },
                "sections": {
                  "type": "array",
                  "items": {"type": "string"}
                }
              }
            },
            "integrations": {
              "type": "array",
              "items": {
                "type": "string",
                "pattern": "^integration://.*$"
              }
            },
            "deployment_tier": {
              "type": "string",
              "enum": ["cortex", "user", "admin", "dual_context"]
            },
            "enabled": {"type": "boolean"},
            "auto_start": {"type": "boolean"},
            "quality_gates": {
              "type": "object",
              "properties": {
                "min_test_coverage": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 100
                },
                "max_complexity": {
                  "type": "number",
                  "minimum": 1
                },
                "required_reviews": {
                  "type": "number",
                  "minimum": 0
                },
                "must_pass_linting": {"type": "boolean"}
              }
            },
            "created_date": {
              "type": "string",
              "format": "date"
            },
            "last_updated": {
              "type": "string",
              "format": "date"
            },
            "deprecated_versions": {
              "type": "array",
              "items": {
                "type": "string",
                "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
              }
            }
          }
        }
      }
    },
    "categories": {
      "type": "object",
      "description": "Taxonomy of orchestrator categories"
    },
    "deprecated": {
      "type": "object",
      "description": "Deprecated orchestrators and manifests"
    },
    "validation": {
      "type": "object",
      "description": "Validation rules for the manifest"
    }
  }
}
```

### Example Usage

```python
from src.utils.manifest_loader import ManifestLoader

# Load CoreManifest
loader = ManifestLoader(cortex_root="/path/to/CORTEX")
core = loader.load_core_manifest()

# Get orchestrator metadata
planning = core.get_orchestrator("planning_orchestrator")
print(planning["version"])  # "4.0.1"
print(planning["child_orchestrators"])  # ["tdd_orchestrator", ...]

# Get all orchestrators in category
tdd_orchestrators = core.get_orchestrators_by_category("tdd")
for orch in tdd_orchestrators:
    print(f"{orch['name']}: {orch['description']}")

# Check if orchestrator is active
if core.is_active("planning_orchestrator"):
    print("Planning Orchestrator is active")
```

---

## ⚙️ ConfigManifest Schema

### Purpose
Centralized runtime configuration for all orchestrators, rules, behaviors, and thresholds.

### Schema Definition (YAML)

```yaml
schema_version: "2.0"
manifest_type: "config"
last_updated: "2025-12-22T00:00:00Z"

# ========================================
# Global Configuration
# ========================================

global:
  timezone: "UTC"
  date_format: "ISO8601"
  encoding: "utf-8"
  
  # Timeouts
  timeouts:
    default_operation: 300  # seconds
    long_operation: 3600
    network_request: 30
  
  # Performance
  performance:
    max_parallel_operations: 4
    cache_ttl: 300  # seconds
    enable_profiling: false

# ========================================
# Category-Based Rules
# ========================================

categories:
  
  # ──────────────────────────────────
  # Cleanup Rules
  # ──────────────────────────────────
  
  cleanup:
    # Standard Mode (default)
    standard:
      enabled: true
      description: "Safe cleanup with user confirmation"
      
      rules:
        orphaned_files:
          enabled: true
          threshold_days: 90
          safe_mode: true
          patterns:
            - "**/*.tmp"
            - "**/*.bak"
            - "**/__pycache__/**"
        
        duplicate_detection:
          enabled: true
          similarity_threshold: 0.95
          ignore_patterns:
            - "**/tests/**"
            - "**/examples/**"
        
        empty_directories:
          enabled: true
          exclude_paths:
            - ".git"
            - "node_modules"
            - "__pycache__"
    
    # Aggressive Mode
    aggressive:
      enabled: false
      description: "Deep cleanup with minimal confirmation"
      
      rules:
        orphaned_files:
          enabled: true
          threshold_days: 30
          safe_mode: false
        
        unused_imports:
          enabled: true
          auto_fix: true
        
        dead_code:
          enabled: true
          confidence_threshold: 0.85
  
  # ──────────────────────────────────
  # Refactoring Rules
  # ──────────────────────────────────
  
  refactoring:
    # Base rules (inherited by all)
    base:
      enabled: true
      
      complexity:
        max_function_complexity: 15
        max_class_complexity: 50
        max_file_complexity: 100
      
      naming:
        enforce_pep8: true
        min_variable_name_length: 2
        max_variable_name_length: 50
      
      structure:
        max_function_lines: 50
        max_class_lines: 300
        max_file_lines: 500
    
    # Planning-specific overrides
    planning:
      enabled: true
      inherits_from: "refactoring.base"
      
      complexity:
        max_function_complexity: 30  # Override (planning is complex)
        max_class_complexity: 75
      
      structure:
        max_function_lines: 100  # Override
    
    # TDD-specific overrides
    tdd:
      enabled: true
      inherits_from: "refactoring.base"
      
      complexity:
        max_function_complexity: 10  # Stricter for TDD
      
      testing:
        require_docstrings: true
        require_type_hints: true
  
  # ──────────────────────────────────
  # Token Optimization Rules
  # ──────────────────────────────────
  
  token_optimization:
    # Global settings
    global:
      enabled: true
      target_reduction: 95  # percentage
      preserve_semantics: true
      
      strategies:
        - name: "remove_comments"
          enabled: true
          preserve_docstrings: true
        
        - name: "minify_whitespace"
          enabled: true
          preserve_readability: true
        
        - name: "abbreviate_identifiers"
          enabled: false  # Risky, keep disabled
    
    # Planning-specific
    planning:
      enabled: true
      inherits_from: "token_optimization.global"
      target_reduction: 98  # More aggressive for plans
      
      strategies:
        - name: "pseudo_code_conversion"
          enabled: true
          detail_level: "medium"
    
    # TDD-specific
    tdd:
      enabled: false  # TDD doesn't need token optimization
  
  # ──────────────────────────────────
  # Documentation Rules
  # ──────────────────────────────────
  
  documentation:
    # Base rules
    base:
      enabled: true
      
      generation:
        format: "markdown"
        include_examples: true
        include_diagrams: false
        auto_toc: true
      
      validation:
        require_module_docstring: true
        require_class_docstring: true
        require_function_docstring: true
        min_docstring_length: 20
    
    # Planning-specific
    planning:
      enabled: true
      inherits_from: "documentation.base"
      
      generation:
        include_diagrams: true  # Override (planning benefits from diagrams)
        diagram_format: "mermaid"
  
  # ──────────────────────────────────
  # Git Checkpoint Rules
  # ──────────────────────────────────
  
  git:
    checkpoints:
      enabled: true
      
      frequency:
        per_phase: true
        per_major_change: true
        on_test_pass: true
      
      commit_message_format: "feat({{orchestrator}}): {{phase_name}}"
      
      validation:
        require_clean_working_dir: true
        require_tests_passing: true
        require_no_conflicts: true
  
  # ──────────────────────────────────
  # Testing Rules
  # ──────────────────────────────────
  
  testing:
    # Global settings
    global:
      enabled: true
      framework: "pytest"
      
      coverage:
        min_coverage: 80
        exclude_patterns:
          - "**/tests/**"
          - "**/examples/**"
      
      execution:
        parallel: true
        max_workers: 4
        timeout: 300
    
    # TDD-specific
    tdd:
      enabled: true
      inherits_from: "testing.global"
      
      coverage:
        min_coverage: 95  # Stricter for TDD
      
      workflow:
        enforce_red_green_refactor: true
        require_test_first: true

# ========================================
# Orchestrator-Specific Overrides
# ========================================

orchestrator_overrides:
  
  planning_orchestrator:
    refactoring:
      enabled: true
      enforcement_level: "warning"  # Don't block on violations
    
    token_optimization:
      enabled: true
      target_reduction: 98
    
    documentation:
      enabled: true
      generation:
        include_diagrams: true
  
  tdd_orchestrator:
    refactoring:
      enabled: true
      enforcement_level: "strict"  # Block on violations
    
    token_optimization:
      enabled: false  # TDD doesn't need it
    
    testing:
      enabled: true
      coverage:
        min_coverage: 95
      workflow:
        enforce_red_green_refactor: true
  
  ado_planning_orchestrator:
    refactoring:
      enabled: true
    
    documentation:
      enabled: true
      generation:
        format: "ado_markdown"  # ADO-specific format

# ========================================
# Feature Flags
# ========================================

feature_flags:
  enable_experimental_features: false
  enable_parallel_orchestration: true
  enable_adaptive_complexity: true
  enable_auto_refactoring: false

# ========================================
# Validation Rules
# ========================================

validation:
  required_fields:
    - "categories.cleanup.standard"
    - "categories.refactoring.base"
    - "categories.testing.global"
  
  allowed_enforcement_levels:
    - "strict"
    - "warning"
    - "disabled"
```

### JSON Schema (for validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://cortex.dev/schemas/config-manifest-v2.json",
  "title": "CORTEX Config Manifest",
  "description": "Runtime configuration and operational rules",
  "type": "object",
  "required": ["schema_version", "manifest_type", "categories"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$"
    },
    "manifest_type": {
      "type": "string",
      "const": "config"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "global": {
      "type": "object",
      "properties": {
        "timezone": {"type": "string"},
        "date_format": {"type": "string"},
        "encoding": {"type": "string"},
        "timeouts": {
          "type": "object",
          "properties": {
            "default_operation": {"type": "number"},
            "long_operation": {"type": "number"},
            "network_request": {"type": "number"}
          }
        },
        "performance": {
          "type": "object",
          "properties": {
            "max_parallel_operations": {"type": "number"},
            "cache_ttl": {"type": "number"},
            "enable_profiling": {"type": "boolean"}
          }
        }
      }
    },
    "categories": {
      "type": "object",
      "properties": {
        "cleanup": {"type": "object"},
        "refactoring": {"type": "object"},
        "token_optimization": {"type": "object"},
        "documentation": {"type": "object"},
        "git": {"type": "object"},
        "testing": {"type": "object"}
      },
      "required": ["cleanup", "refactoring", "testing"]
    },
    "orchestrator_overrides": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "description": "Orchestrator-specific configuration overrides"
        }
      }
    },
    "feature_flags": {
      "type": "object",
      "patternProperties": {
        "^enable_.*$": {
          "type": "boolean"
        }
      }
    },
    "validation": {
      "type": "object"
    }
  }
}
```

### Example Usage

```python
# Load ConfigManifest
config = loader.load_config_manifest()

# Get refactoring rules for planning orchestrator
planning_refactoring = config.get_config(
    orchestrator_id="planning_orchestrator",
    category="refactoring"
)
print(planning_refactoring["complexity"]["max_function_complexity"])  # 30

# Get TDD testing config
tdd_testing = config.get_config(
    orchestrator_id="tdd_orchestrator",
    category="testing"
)
print(tdd_testing["coverage"]["min_coverage"])  # 95

# Check feature flag
if config.is_feature_enabled("enable_parallel_orchestration"):
    print("Parallel orchestration is enabled")
```

---

## 🔌 IntegrationManifest Schema

### Purpose
External system integrations, API configurations, authentication, and adapter specifications.

### Schema Definition (YAML)

```yaml
schema_version: "2.0"
manifest_type: "integration"
last_updated: "2025-12-22T00:00:00Z"

# ========================================
# Integration Definitions
# ========================================

integrations:
  
  # ──────────────────────────────────
  # Azure DevOps Integration
  # ──────────────────────────────────
  
  azure_devops:
    id: "integration://azure_devops"
    name: "Azure DevOps"
    description: "Integration with Azure DevOps for work item management"
    
    # Adapter
    adapter:
      class_name: "AzureDevOpsAdapter"
      module_path: "src.orchestration_4_0.adapters.azure_devops_adapter"
      version: "2.0.0"
    
    # Authentication
    authentication:
      method: "PAT"  # Personal Access Token
      env_var: "AZURE_DEVOPS_PAT"
      required_scopes:
        - "vso.work_write"
        - "vso.project"
      validation:
        test_endpoint: "/_apis/projects"
        expected_status: 200
    
    # API Configuration
    api:
      base_url: "https://dev.azure.com"
      version: "7.1"
      
      endpoints:
        work_items:
          path: "/{organization}/_apis/wit/workitems"
          methods: ["GET", "POST", "PATCH"]
        
        projects:
          path: "/{organization}/_apis/projects"
          methods: ["GET"]
        
        pipelines:
          path: "/{organization}/{project}/_apis/pipelines"
          methods: ["GET", "POST"]
    
    # Rate Limiting
    rate_limiting:
      enabled: true
      requests_per_second: 10
      burst: 20
      strategy: "token_bucket"
    
    # Retry Policy
    retry:
      enabled: true
      max_retries: 3
      backoff_strategy: "exponential"
      initial_delay: 1  # seconds
      max_delay: 30
      retry_on_status:
        - 429  # Too Many Requests
        - 500  # Internal Server Error
        - 502  # Bad Gateway
        - 503  # Service Unavailable
    
    # Caching
    caching:
      enabled: true
      ttl: 300  # seconds
      cache_key_prefix: "ado"
    
    # Used By
    orchestrators:
      - "ado_planning_orchestrator"
  
  # ──────────────────────────────────
  # GitHub Integration
  # ──────────────────────────────────
  
  github:
    id: "integration://github"
    name: "GitHub"
    description: "Integration with GitHub for issues, PRs, and actions"
    
    adapter:
      class_name: "GitHubAdapter"
      module_path: "src.orchestration_4_0.adapters.github_adapter"
      version: "2.0.0"
    
    authentication:
      method: "PAT"
      env_var: "GITHUB_PAT"
      required_scopes:
        - "repo"
        - "workflow"
    
    api:
      base_url: "https://api.github.com"
      version: "2022-11-28"
      
      endpoints:
        issues:
          path: "/repos/{owner}/{repo}/issues"
          methods: ["GET", "POST", "PATCH"]
        
        pull_requests:
          path: "/repos/{owner}/{repo}/pulls"
          methods: ["GET", "POST"]
        
        actions:
          path: "/repos/{owner}/{repo}/actions"
          methods: ["GET", "POST"]
    
    rate_limiting:
      enabled: true
      requests_per_second: 60
      burst: 100
      strategy: "sliding_window"
    
    retry:
      enabled: true
      max_retries: 3
      backoff_strategy: "exponential"
      initial_delay: 1
      max_delay: 30
    
    caching:
      enabled: true
      ttl: 180
      cache_key_prefix: "github"
    
    orchestrators:
      - "planning_orchestrator"
      - "git_checkpoint_orchestrator"
  
  # ──────────────────────────────────
  # File System Integration
  # ──────────────────────────────────
  
  file_system:
    id: "integration://file_system"
    name: "File System"
    description: "Local and network file system access"
    
    adapter:
      class_name: "FileSystemAdapter"
      module_path: "src.orchestration_4_0.adapters.filesystem_adapter"
      version: "1.0.0"
    
    configuration:
      local:
        enabled: true
        base_path: null  # Set at runtime
        permissions:
          read: true
          write: true
          execute: false
      
      network:
        enabled: false
        base_path: null
        protocol: "smb"  # smb|nfs|ftp
    
    # No authentication for local, required for network
    authentication:
      method: "none"  # local only
    
    rate_limiting:
      enabled: false
    
    retry:
      enabled: true
      max_retries: 2
      backoff_strategy: "linear"
    
    orchestrators:
      - "planning_orchestrator"
      - "tdd_orchestrator"
      - "sanitization_orchestrator"
      - "maintenance_orchestrator"

# ========================================
# Adapter Factory Configuration
# ========================================

adapter_factory:
  auto_detection: true
  fallback_adapter: "file_system"
  cache_ttl: 300
  
  # Middleware (applied to all adapters)
  middleware:
    - name: "caching"
      enabled: true
      priority: 1
      config:
        backend: "memory"  # memory|redis|disk
        max_size: 1000
    
    - name: "retry"
      enabled: true
      priority: 2
    
    - name: "rate_limiting"
      enabled: true
      priority: 3
    
    - name: "logging"
      enabled: true
      priority: 4
      config:
        log_requests: true
        log_responses: false
        log_errors: true

# ========================================
# Connection Pooling
# ========================================

connection_pooling:
  enabled: true
  max_connections: 10
  min_connections: 2
  connection_timeout: 30
  idle_timeout: 300

# ========================================
# Health Checks
# ========================================

health_checks:
  enabled: true
  interval: 60  # seconds
  timeout: 10
  
  checks:
    - integration: "azure_devops"
      endpoint: "/_apis/projects"
      expected_status: 200
    
    - integration: "github"
      endpoint: "/user"
      expected_status: 200
    
    - integration: "file_system"
      method: "write_test_file"

# ========================================
# Validation Rules
# ========================================

validation:
  required_fields:
    - "integrations.*.adapter.class_name"
    - "integrations.*.adapter.module_path"
  
  allowed_auth_methods:
    - "PAT"
    - "OAuth2"
    - "API_KEY"
    - "none"
```

### JSON Schema (for validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://cortex.dev/schemas/integration-manifest-v2.json",
  "title": "CORTEX Integration Manifest",
  "description": "External system integrations and adapters",
  "type": "object",
  "required": ["schema_version", "manifest_type", "integrations"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$"
    },
    "manifest_type": {
      "type": "string",
      "const": "integration"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "integrations": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "required": ["id", "name", "adapter"],
          "properties": {
            "id": {
              "type": "string",
              "pattern": "^integration://.*$"
            },
            "name": {"type": "string"},
            "description": {"type": "string"},
            "adapter": {
              "type": "object",
              "required": ["class_name", "module_path", "version"],
              "properties": {
                "class_name": {"type": "string"},
                "module_path": {"type": "string"},
                "version": {
                  "type": "string",
                  "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
                }
              }
            },
            "authentication": {
              "type": "object",
              "properties": {
                "method": {
                  "type": "string",
                  "enum": ["PAT", "OAuth2", "API_KEY", "none"]
                },
                "env_var": {"type": "string"},
                "required_scopes": {
                  "type": "array",
                  "items": {"type": "string"}
                }
              }
            },
            "api": {
              "type": "object",
              "properties": {
                "base_url": {"type": "string"},
                "version": {"type": "string"},
                "endpoints": {"type": "object"}
              }
            },
            "rate_limiting": {
              "type": "object",
              "properties": {
                "enabled": {"type": "boolean"},
                "requests_per_second": {"type": "number"},
                "burst": {"type": "number"},
                "strategy": {
                  "type": "string",
                  "enum": ["token_bucket", "sliding_window", "fixed_window"]
                }
              }
            },
            "retry": {
              "type": "object",
              "properties": {
                "enabled": {"type": "boolean"},
                "max_retries": {"type": "number"},
                "backoff_strategy": {
                  "type": "string",
                  "enum": ["linear", "exponential", "fixed"]
                }
              }
            },
            "caching": {
              "type": "object",
              "properties": {
                "enabled": {"type": "boolean"},
                "ttl": {"type": "number"}
              }
            },
            "orchestrators": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        }
      }
    },
    "adapter_factory": {
      "type": "object"
    },
    "connection_pooling": {
      "type": "object"
    },
    "health_checks": {
      "type": "object"
    }
  }
}
```

### Example Usage

```python
# Load IntegrationManifest
integration = loader.load_integration_manifest()

# Get Azure DevOps integration config
ado_config = integration.get_integration("azure_devops")
print(ado_config["api"]["base_url"])  # "https://dev.azure.com"

# Get adapter for orchestrator
adapter = integration.get_adapter_for_orchestrator("ado_planning_orchestrator")
print(adapter)  # AzureDevOpsAdapter instance

# Check health of integration
health = integration.check_health("azure_devops")
if health["status"] == "healthy":
    print("ADO integration is healthy")
```

---

## 🔗 Inheritance Model

### Inheritance Strategy

**Principle:** `child_overrides_parent` with deep merge for nested structures

**Inheritance Levels:**
1. **Manifest Level:** CoreManifest inherits from defaults
2. **Category Level:** ConfigManifest categories inherit from base
3. **Orchestrator Level:** Orchestrators inherit from parent orchestrators

### Inheritance Rules

```yaml
# Rule 1: Simple Override
parent:
  field_a: "value_a"
  field_b: "value_b"

child:
  inherits_from: "parent"
  field_b: "new_value_b"  # Overrides parent

# Result:
# field_a: "value_a" (inherited)
# field_b: "new_value_b" (overridden)

# Rule 2: Deep Merge (nested dicts)
parent:
  config:
    timeout: 300
    retry: 3

child:
  inherits_from: "parent"
  config:
    timeout: 600  # Override specific field

# Result:
# config:
#   timeout: 600 (overridden)
#   retry: 3 (inherited)

# Rule 3: List Append (default)
parent:
  orchestrators:
    - "orch_a"
    - "orch_b"

child:
  inherits_from: "parent"
  orchestrators:
    - "orch_c"

# Result:
# orchestrators:
#   - "orch_a"
#   - "orch_b"
#   - "orch_c"

# Rule 4: List Replace (explicit)
parent:
  orchestrators:
    - "orch_a"
    - "orch_b"

child:
  inherits_from: "parent"
  orchestrators:
    _merge_strategy: "replace"
    _values:
      - "orch_c"

# Result:
# orchestrators:
#   - "orch_c"
```

### Circular Dependency Detection

```python
# ManifestInheritanceResolver detects circular inheritance

# Example circular dependency:
# planning_orchestrator -> tdd_orchestrator -> planning_orchestrator

resolver = ManifestInheritanceResolver(base_dir)

try:
    resolved = resolver.resolve("planning_orchestrator")
except ValueError as e:
    print(f"Circular dependency: {e}")
    # Output: "Circular inheritance detected: planning_orchestrator → tdd_orchestrator → planning_orchestrator"
```

### Multi-Level Inheritance Example

```yaml
# Level 1: Base (Tier 1)
base-orchestrator-manifest.yaml:
  metadata:
    deployment_tier: "user"
    maintainer: "CORTEX Team"
  logging:
    level: "INFO"

# Level 2: Planning Base (Tier 2)
planning-base-manifest.yaml:
  inherits_from: "base-orchestrator-manifest.yaml"
  metadata:
    category: "planning"
  quality_gates:
    min_test_coverage: 80

# Level 3: Planning Orchestrator (Tier 3)
planning-orchestrator.yaml:
  inherits_from: "planning-base-manifest.yaml"
  metadata:
    orchestrator_name: "planning_orchestrator"
    version: "4.0.1"
  quality_gates:
    min_test_coverage: 85  # Override Tier 2

# Resolved Result:
metadata:
  orchestrator_name: "planning_orchestrator"  # From Tier 3
  version: "4.0.1"  # From Tier 3
  category: "planning"  # From Tier 2
  deployment_tier: "user"  # From Tier 1
  maintainer: "CORTEX Team"  # From Tier 1
logging:
  level: "INFO"  # From Tier 1
quality_gates:
  min_test_coverage: 85  # From Tier 3 (override)
```

---

## 🔗 Cross-Referencing Strategy

### Namespace Convention

**Pattern:** `<manifest_type>://<path>`

**Examples:**
- `config://refactoring.planning` - ConfigManifest, refactoring category, planning section
- `integration://azure_devops` - IntegrationManifest, Azure DevOps integration
- `core://planning_orchestrator` - CoreManifest, planning orchestrator

### Cross-Reference Resolution

```yaml
# In CoreManifest
orchestrators:
  planning_orchestrator:
    config_overrides:
      namespace: "config://planning"
      sections:
        - "refactoring.planning"
        - "token_optimization.planning"
    
    integrations:
      - "integration://github"
      - "integration://file_system"

# In ConfigManifest
categories:
  refactoring:
    planning:
      complexity:
        max_function_complexity: 30

# Resolution Process:
# 1. Load CoreManifest
# 2. Parse config_overrides.namespace = "config://planning"
# 3. Load ConfigManifest
# 4. Find categories.refactoring.planning
# 5. Merge into orchestrator config
```

### Resolution Algorithm

```python
class ManifestLoader:
    def resolve_cross_references(self, orchestrator_id: str) -> Dict[str, Any]:
        """
        Resolve all cross-references for an orchestrator.
        
        Returns merged configuration from:
        - CoreManifest (orchestrator metadata)
        - ConfigManifest (runtime config)
        - IntegrationManifest (external systems)
        """
        # 1. Load orchestrator from CoreManifest
        orch = self.core.get_orchestrator(orchestrator_id)
        
        # 2. Resolve config overrides
        config = {}
        if "config_overrides" in orch:
            namespace = orch["config_overrides"]["namespace"]
            sections = orch["config_overrides"]["sections"]
            
            for section in sections:
                config[section] = self.config.get_section(section)
        
        # 3. Resolve integrations
        integrations = {}
        if "integrations" in orch:
            for integration_ref in orch["integrations"]:
                integration_id = integration_ref.replace("integration://", "")
                integrations[integration_id] = self.integration.get_integration(integration_id)
        
        # 4. Merge everything
        return {
            "metadata": orch,
            "config": config,
            "integrations": integrations
        }
```

### Lazy Loading Strategy

```python
class LazyManifestLoader:
    """Load manifests on-demand to minimize memory footprint"""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self._core = None
        self._config = None
        self._integration = None
    
    @property
    def core(self):
        if self._core is None:
            self._core = self._load_core_manifest()
        return self._core
    
    @property
    def config(self):
        if self._config is None:
            self._config = self._load_config_manifest()
        return self._config
    
    @property
    def integration(self):
        if self._integration is None:
            self._integration = self._load_integration_manifest()
        return self._integration
```

---

## 🚀 Migration Strategy

### Phase 1: Parallel Operation (Week 15, Day 3-4)

**Objective:** Run old + new manifests side-by-side with validation

**Steps:**
1. Create 3 new manifests (CoreManifest, ConfigManifest, IntegrationManifest)
2. Build ManifestLoader with backward compatibility
3. Update 1-2 orchestrators to use new manifests
4. Run tests with both old and new manifests
5. Compare results (must be identical)

**Code:**
```python
class ManifestMigrationAdapter:
    """Translate old manifest format to new format"""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.old_loader = OldManifestLoader(cortex_root)
        self.new_loader = ManifestLoader(cortex_root)
    
    def validate_equivalence(self, orchestrator_id: str) -> bool:
        """Validate that old and new manifests produce identical config"""
        old_config = self.old_loader.load(orchestrator_id)
        new_config = self.new_loader.load(orchestrator_id)
        
        return deep_equals(old_config, new_config)
```

### Phase 2: Gradual Migration (Week 15, Day 4-5)

**Objective:** Migrate orchestrators one-by-one with rollback capability

**Migration Order:**
1. File System Integration (simplest)
2. Planning Orchestrator (most stable)
3. TDD Orchestrator (depends on planning)
4. ADO Planning Orchestrator (depends on planning + ADO integration)
5. Remaining 12 orchestrators

### Phase 3: Deprecation (Week 16)

**Objective:** Mark old manifests as deprecated, remove in future release

**Actions:**
1. Add deprecation warnings to old manifest loaders
2. Update documentation to reference new manifests
3. Set removal date (e.g., 30 days)
4. Archive old manifests to `cortex-brain/archive/manifests/`

---

## 🛠️ Implementation Roadmap

### Task 7.3: Create 3 Manifests (Day 3)

**Deliverables:**
- [ ] `cortex-brain/manifests/core-manifest.yaml` (800 lines)
- [ ] `cortex-brain/manifests/config-manifest.yaml` (1,200 lines)
- [ ] `cortex-brain/manifests/integration-manifest.yaml` (500 lines)

### Task 7.4: Build ManifestLoader (Day 4)

**Deliverables:**
- [ ] `src/utils/manifest_loader.py` (ManifestLoader class)
- [ ] `src/utils/manifest_migration_adapter.py` (backward compatibility)
- [ ] `tests/test_manifest_loader.py` (65+ tests)

### Task 7.5: Update Orchestrators (Day 5)

**Deliverables:**
- [ ] Update 16 orchestrators to use ManifestLoader
- [ ] Run full test suite (164+ tests)
- [ ] Validate performance impact < 5%

### Task 7.6: Documentation & Validation (Day 5)

**Deliverables:**
- [ ] `docs/architecture/3-tier-manifest-guide.md`
- [ ] Migration guide for orchestrator developers
- [ ] Validation report (old vs new manifests)

---

## ✅ Validation & Testing

### Unit Tests

```python
class TestCoreManifest:
    def test_load_core_manifest(self):
        loader = ManifestLoader(cortex_root)
        core = loader.load_core_manifest()
        assert core["schema_version"] == "2.0"
        assert "orchestrators" in core
    
    def test_get_orchestrator(self):
        loader = ManifestLoader(cortex_root)
        core = loader.load_core_manifest()
        planning = core.get_orchestrator("planning_orchestrator")
        assert planning["version"] == "4.0.1"
        assert planning["category"] == "planning"
    
    def test_inheritance_resolution(self):
        loader = ManifestLoader(cortex_root)
        core = loader.load_core_manifest()
        tdd = core.get_orchestrator("tdd_orchestrator")
        # Should inherit from planning_orchestrator
        assert tdd["inherits_from"] == "planning_orchestrator"

class TestConfigManifest:
    def test_load_config_manifest(self):
        loader = ManifestLoader(cortex_root)
        config = loader.load_config_manifest()
        assert config["schema_version"] == "2.0"
        assert "categories" in config
    
    def test_get_config_with_override(self):
        loader = ManifestLoader(cortex_root)
        config = loader.load_config_manifest()
        # Planning orchestrator overrides max_complexity
        planning_config = config.get_config("planning_orchestrator", "refactoring")
        assert planning_config["complexity"]["max_function_complexity"] == 30
        
        # TDD orchestrator uses stricter default
        tdd_config = config.get_config("tdd_orchestrator", "refactoring")
        assert tdd_config["complexity"]["max_function_complexity"] == 10

class TestIntegrationManifest:
    def test_load_integration_manifest(self):
        loader = ManifestLoader(cortex_root)
        integration = loader.load_integration_manifest()
        assert integration["schema_version"] == "2.0"
        assert "integrations" in integration
    
    def test_get_adapter(self):
        loader = ManifestLoader(cortex_root)
        integration = loader.load_integration_manifest()
        ado = integration.get_integration("azure_devops")
        assert ado["adapter"]["class_name"] == "AzureDevOpsAdapter"

class TestCrossReferencing:
    def test_resolve_config_overrides(self):
        loader = ManifestLoader(cortex_root)
        resolved = loader.resolve_cross_references("planning_orchestrator")
        
        # Should have config from ConfigManifest
        assert "config" in resolved
        assert "refactoring.planning" in resolved["config"]
    
    def test_resolve_integrations(self):
        loader = ManifestLoader(cortex_root)
        resolved = loader.resolve_cross_references("ado_planning_orchestrator")
        
        # Should have ADO integration
        assert "integrations" in resolved
        assert "azure_devops" in resolved["integrations"]

class TestBackwardCompatibility:
    def test_migration_adapter(self):
        adapter = ManifestMigrationAdapter(cortex_root)
        
        # Load with old loader
        old_config = adapter.old_loader.load("planning_orchestrator")
        
        # Load with new loader
        new_config = adapter.new_loader.load("planning_orchestrator")
        
        # Should be identical
        assert deep_equals(old_config, new_config)
```

### Integration Tests

```python
class TestOrchestratorWithNewManifests:
    def test_planning_orchestrator_loads_correctly(self):
        loader = ManifestLoader(cortex_root)
        orch = PlanningOrchestrator(cortex_root, manifest_loader=loader)
        
        assert orch.version == "4.0.1"
        assert orch.config["refactoring"]["complexity"]["max_function_complexity"] == 30
    
    def test_tdd_orchestrator_inherits_from_planning(self):
        loader = ManifestLoader(cortex_root)
        orch = TDDOrchestrator(cortex_root, manifest_loader=loader)
        
        # Should inherit config from planning
        assert orch.parent_orchestrator == "planning_orchestrator"
    
    def test_ado_orchestrator_has_correct_integration(self):
        loader = ManifestLoader(cortex_root)
        orch = ADOPlanningOrchestrator(cortex_root, manifest_loader=loader)
        
        # Should have ADO integration
        assert "azure_devops" in orch.integrations
```

### Performance Tests

```python
class TestManifestLoaderPerformance:
    def test_cold_load_performance(self):
        """First load (no cache)"""
        start = time.time()
        loader = ManifestLoader(cortex_root)
        loader.load_all()
        elapsed = time.time() - start
        
        # Should load in < 100ms
        assert elapsed < 0.1
    
    def test_cached_load_performance(self):
        """Subsequent loads (with cache)"""
        loader = ManifestLoader(cortex_root)
        loader.load_all()  # Warm cache
        
        start = time.time()
        loader.load_all()
        elapsed = time.time() - start
        
        # Should load in < 10ms
        assert elapsed < 0.01
```

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Line Reduction** | -88% | 21,594 → 2,500 lines |
| **File Reduction** | -92% | 37 → 3 files |
| **Redundancy Elimination** | 100% | Zero duplicate metadata/rules |
| **Performance Impact** | < 5% | Manifest load time increase |
| **Test Pass Rate** | 100% | All 164+ tests passing |
| **Backward Compatibility** | 100% | Old manifests work during migration |

---

## 📚 References

- [Phase 7 Manifest Consolidation Analysis](phase-7-manifest-consolidation-analysis.md)
- [Manifest Inheritance Resolver](../../../src/utils/manifest_inheritance_resolver.py)
- [JSON Schema Documentation](https://json-schema.org/draft-07/schema)
- [YAML 1.2 Specification](https://yaml.org/spec/1.2/spec.html)

---

**Status:** 🏗️ Design Complete | Ready for Implementation (Task 7.3-7.6)  
**Next:** Create 3 manifests (CoreManifest, ConfigManifest, IntegrationManifest)
