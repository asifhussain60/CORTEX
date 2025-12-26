# Phase 7.2 - 3-Tier Manifest Schema Design

**Operation:** CORTEX 4.0 Manifest Schema Design  
**Author:** Asif Hussain  
**Date:** December 23, 2025  
**Version:** 1.0.0  
**Status:** ✅ Complete - Ready for Phase 7.3 (Implementation)  
**Dependencies:** Phase 7.1 (Analysis) complete ✅

---

## Executive Summary

**Purpose:** Define comprehensive schema specifications for 3-tier manifest consolidation.

**Deliverables:**
1. **CoreManifest Schema** - Orchestrator registry (671 lines → 800 lines with 16 orchestrators)
2. **ConfigManifest Schema** - Runtime configuration (811 lines → 1,200 lines with 8 rule consolidations)
3. **IntegrationManifest Schema** - External systems (675 lines → 500 lines with adapter factory)
4. **Inheritance Model** - YAML anchors + cross-referencing strategy
5. **Migration Path** - Backward compatibility with legacy manifests

**Design Principles:**
- ✅ **DRY (Don't Repeat Yourself)** - Zero redundancy via inheritance
- ✅ **Single Source of Truth** - Each config appears once
- ✅ **Cross-Referencing** - URI-based linking (e.g., `config://cleanup.standard`)
- ✅ **Backward Compatible** - Legacy manifests supported during migration
- ✅ **Schema Validation** - JSON Schema for all 3 manifests

---

## 1. CoreManifest Schema v2.0

### 1.1 Purpose & Scope

**What:** Single orchestrator registry for all 16 CORTEX orchestrators  
**Why:** Eliminate 60% metadata redundancy (4,700 lines → 800 lines)  
**How:** Inheritance-based registry with relationship mapping

### 1.2 Schema Definition

```yaml
# CORTEX Core Manifest v2.0
# File: cortex-brain/manifests/core-manifest.yaml

schema_version: "2.0"
manifest_type: "core"
last_updated: "2025-12-23T00:00:00Z"

# ========================================
# SECTION 1: Global Defaults
# ========================================
# Inherited by ALL orchestrators unless overridden

defaults:
  schema_version: "1.0"
  deployment_tier: "user"              # cortex|user|admin|dual_context
  maintainer: "CORTEX Development Team"
  status: "active"                     # draft|active|deprecated|archived
  
  # Logging configuration
  logging:
    level: "INFO"                      # DEBUG|INFO|WARNING|ERROR|CRITICAL
    format: "structured"               # structured|json|plain
    destinations:
      - type: "console"
        enabled: true
      - type: "file"
        enabled: true
        path: "logs/{orchestrator_name}.log"  # {orchestrator_name} auto-replaced
        rotation: "daily"
        retention_days: 30
  
  # Error handling
  error_handling:
    strategy: "fail_fast"              # fail_fast|continue_on_error|retry
    retry_enabled: false
    max_retries: 3
    backoff_multiplier: 2              # Exponential backoff (2^n seconds)
    rollback_enabled: true             # Auto-rollback on failure
  
  # Quality gates (TDD enforcement)
  quality_gates:
    min_test_coverage: 80              # Minimum coverage %
    max_complexity: 30                 # Cyclomatic complexity threshold
    required_reviews: 1                # Human reviews before merge
    must_pass_linting: true            # Block merge on lint failures
    tdd_enforcement: true              # RED→GREEN→REFACTOR mandatory

# ========================================
# SECTION 2: Orchestrator Registry
# ========================================
# All 16 CORTEX orchestrators

orchestrators:
  
  # ──────────────────────────────────────────────────
  # PLANNING ORCHESTRATORS (3 orchestrators)
  # ──────────────────────────────────────────────────
  
  planning_orchestrator:
    # Metadata
    version: "4.0.1"
    status: "active"
    category: "planning"
    description: "Tiered planning system with intelligent routing (HIGH/MEDIUM/LOW complexity)"
    
    # Implementation
    source_file: "src/orchestrators/planning/planning_orchestrator.py"
    entry_point: "PlanningOrchestrator"
    
    # Documentation
    documentation_path: ".github/prompts/modules/planning-system-guide.md"
    changelog_path: "docs/orchestration/planning-system-changelog.md"
    
    # Relationships
    inherits_from: null                # Top-level orchestrator
    parent_orchestrator: null
    child_orchestrators:
      - "tdd_orchestrator"
      - "ado_orchestrator"
      - "sanitization_orchestrator"
    related_orchestrators:
      - "maintenance_orchestrator"
      - "git_checkpoint_orchestrator"
    
    # Configuration (cross-references)
    config_overrides:
      namespace: "config://planning"   # Points to ConfigManifest
      sections:
        - "refactoring.planning"
        - "token_optimization.planning"
        - "documentation.planning"
    
    # Integrations (cross-references)
    integrations:
      - "integration://github"         # Points to IntegrationManifest
      - "integration://file_system"
    
    # Feature flags
    features:
      pre_planning_discovery: true     # Check for existing plans
      visual_progress_tracking: true   # Auto-update status docs
      autonomous_execution: true       # E2E without user input
      tiered_routing: true             # INSTANT/LIGHTWEIGHT/DOCUMENTED/COMPLEX
      agentic_enhancements: true       # Multi-agent collaboration
    
    # Metadata for manifest migration
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml"
    migration_status: "migrated"       # not_started|in_progress|migrated
    migration_date: "2025-12-23"
  
  tdd_orchestrator:
    version: "4.0.0"
    status: "active"
    category: "tdd"
    description: "Unified TDD orchestrator with adaptive learning and clean code enforcement"
    
    source_file: "src/orchestrators/tdd/tdd_orchestrator.py"
    entry_point: "TDDOrchestrator"
    
    documentation_path: ".github/prompts/modules/tdd-orchestrator-guide.md"
    changelog_path: "docs/orchestration/tdd-orchestrator-changelog.md"
    
    inherits_from: "planning_orchestrator"  # Inherits config/logging/quality_gates
    parent_orchestrator: "planning_orchestrator"
    child_orchestrators: []
    related_orchestrators:
      - "planning_orchestrator"
      - "maintenance_orchestrator"
      - "code_sanitization_orchestrator"
    
    config_overrides:
      namespace: "config://tdd"
      sections:
        - "refactoring.tdd"
        - "clean_code.enforcement"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
      - "integration://mcp_gateway"    # For tool execution
    
    features:
      technology_discovery: true       # Auto-detect languages/frameworks
      ai_driven_generation: true       # AI test/code generation
      clean_code_enforcement: true     # SOLID/DRY/KISS/YAGNI
      adaptive_learning: true          # Learn from patterns (Tier 2)
      vision_api_integration: true     # Image-based test generation
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  ado_orchestrator:
    version: "2.1.0"
    status: "active"
    category: "planning"
    description: "Azure DevOps work item creation and management"
    
    source_file: "src/orchestrators/ado/ado_orchestrator.py"
    entry_point: "ADOOrchestrator"
    
    documentation_path: ".github/prompts/modules/ado-orchestrator-guide.md"
    
    inherits_from: "planning_orchestrator"
    parent_orchestrator: "planning_orchestrator"
    
    config_overrides:
      namespace: "config://ado"
      sections:
        - "work_items.creation"
        - "formatting.ado_specific"
    
    integrations:
      - "integration://azure_devops"   # Primary integration
      - "integration://file_system"
    
    features:
      story_creation: true
      feature_creation: true
      task_creation: true
      completion_summaries: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  # ──────────────────────────────────────────────────
  # EXECUTION ORCHESTRATORS (3 orchestrators)
  # ──────────────────────────────────────────────────
  
  execution_orchestrator:
    version: "4.0.0"
    status: "active"
    category: "execution"
    description: "Autonomous plan execution with self-healing and validation"
    
    source_file: "src/orchestrators/execution/execution_orchestrator.py"
    entry_point: "ExecutionOrchestrator"
    
    documentation_path: "docs/orchestration_4_0/execution-orchestrator.md"
    
    config_overrides:
      namespace: "config://execution"
      sections:
        - "validation.pre_execution"
        - "checkpoints.auto_save"
        - "rollback.strategies"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
    
    features:
      autonomous_execution: true
      self_healing: true
      checkpoint_system: true
      failure_escalation: true
      validation_framework: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/execution-orchestrator-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  devops_orchestrator:
    version: "2.0.0"
    status: "active"
    category: "execution"
    description: "CI/CD pipeline management (Azure DevOps + GitHub Actions)"
    
    source_file: "src/orchestrators/devops/devops_orchestrator.py"
    entry_point: "DevOpsOrchestrator"
    
    documentation_path: "docs/orchestration_4_0/devops-orchestrator.md"
    
    config_overrides:
      namespace: "config://devops"
      sections:
        - "pipelines.azure_devops"
        - "pipelines.github_actions"
    
    integrations:
      - "integration://azure_devops"
      - "integration://github"
    
    features:
      azure_devops_pipelines: true
      github_actions: true
      pipeline_validation: true
      deployment_tracking: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/devops-orchestrator-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  ci_cd_self_healing_orchestrator:
    version: "1.0.0"
    status: "active"
    category: "execution"
    description: "Intelligent CI/CD failure analysis and auto-healing"
    
    source_file: "src/orchestrators/cicd/ci_cd_self_healing_orchestrator.py"
    entry_point: "CICDSelfHealingOrchestrator"
    
    documentation_path: "docs/orchestration_4_0/cicd-self-healing-orchestrator.md"
    
    config_overrides:
      namespace: "config://cicd_healing"
      sections:
        - "failure_analysis.patterns"
        - "healing_strategies.auto_fix"
    
    integrations:
      - "integration://azure_devops"
      - "integration://github"
      - "integration://brain_tier2"    # Pattern learning
    
    features:
      failure_pattern_detection: true
      intelligent_analysis: true
      auto_fix_strategies: true
      learning_from_failures: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/cicd-self-healing-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  # ──────────────────────────────────────────────────
  # ANALYSIS ORCHESTRATORS (3 orchestrators)
  # ──────────────────────────────────────────────────
  
  documentation_orchestrator:
    version: "4.0.0"
    status: "active"
    category: "analysis"
    description: "Automated technical documentation generation and maintenance"
    
    source_file: "src/orchestrators/documentation/documentation_orchestrator.py"
    entry_point: "DocumentationOrchestrator"
    
    documentation_path: "docs/orchestration_4_0/documentation-orchestrator.md"
    
    config_overrides:
      namespace: "config://documentation"
      sections:
        - "generation.rules"
        - "templates.formats"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
    
    features:
      automated_generation: true
      markdown_formatting: true
      api_documentation: true
      architecture_diagrams: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/technical-documentation-orchestrator-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  sanitization_orchestrator:
    version: "3.0.0"
    status: "active"
    category: "analysis"
    description: "Code sanitization for public sharing (remove company data)"
    
    source_file: "src/orchestrators/sanitization/sanitization_orchestrator.py"
    entry_point: "SanitizationOrchestrator"
    
    documentation_path: "cortex-brain/CODE-SANITIZATION-QUICK-REF.md"
    
    config_overrides:
      namespace: "config://sanitization"
      sections:
        - "mapping.terminology"
        - "validation.build_test"
    
    integrations:
      - "integration://file_system"
      - "integration://github"
    
    features:
      company_data_removal: true
      domain_terminology_transform: true
      build_validation: true
      audit_reporting: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  contextual_review_orchestrator:
    version: "3.0.0"
    status: "active"
    category: "analysis"
    description: "6-phase architectural review with 0-100 scoring"
    
    source_file: "src/operations/modules/orchestration/contextual_review_orchestrator.py"
    entry_point: "ContextualReviewOrchestrator"
    
    config_overrides:
      namespace: "config://review"
      sections:
        - "scoring.criteria"
        - "git_protection.rules"
    
    integrations:
      - "integration://file_system"
      - "integration://github"
    
    features:
      architectural_analysis: true
      scoring_system: true
      git_protection: true
      report_generation: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/contextual-review-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  # ──────────────────────────────────────────────────
  # MAINTENANCE ORCHESTRATORS (4 orchestrators)
  # ──────────────────────────────────────────────────
  
  maintenance_orchestrator:
    version: "4.0.0"
    status: "active"
    category: "maintenance"
    description: "7-phase system maintenance (healthcheck → align → cleanup → optimize → vacuum → refresh → healthcheck)"
    
    source_file: "src/operations/modules/orchestration/maintenance_orchestrator.py"
    entry_point: "MaintenanceOrchestrator"
    
    documentation_path: "docs/orchestration_4_0/maintenance-orchestrator.md"
    
    config_overrides:
      namespace: "config://maintenance"
      sections:
        - "cleanup.aggressive"
        - "optimization.strategies"
    
    integrations:
      - "integration://file_system"
      - "integration://github"
    
    features:
      tiered_routing: true
      auto_fix: true
      ast_powered_cleanup: true
      version_management: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/maintenance-orchestrator-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  refinement_orchestrator:
    version: "1.0.0"
    status: "active"
    category: "maintenance"
    description: "Holistic system refinement (7 phases: discovery → SKULL → docs → quality → architecture → performance → validation)"
    
    source_file: "src/operations/modules/orchestration/refinement_orchestrator_v1.py"
    entry_point: "RefinementOrchestratorV1"
    
    config_overrides:
      namespace: "config://refinement"
      sections:
        - "skull.optimization"
        - "documentation.refinement"
    
    integrations:
      - "integration://file_system"
      - "integration://github"
    
    features:
      ast_based_analysis: true
      skull_test_optimization: true
      documentation_refinement: true
      rollback_safety: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  git_checkpoint_orchestrator:
    version: "2.0.0"
    status: "active"
    category: "maintenance"
    description: "Git checkpoint management with intelligent commit messages"
    
    source_file: "src/operations/modules/orchestration/git_checkpoint_orchestrator.py"
    entry_point: "GitCheckpointOrchestrator"
    
    config_overrides:
      namespace: "config://git_checkpoint"
      sections:
        - "commit.message_templates"
        - "safety.pre_commit_checks"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
    
    features:
      auto_commit_messages: true
      pre_commit_validation: true
      rollback_points: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/git-checkpoint-rules.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  upgrade_orchestrator:
    version: "2.0.0"
    status: "active"
    category: "maintenance"
    description: "CORTEX version upgrades with migration support"
    
    source_file: "src/operations/modules/orchestration/upgrade_orchestrator.py"
    entry_point: "UpgradeOrchestrator"
    
    config_overrides:
      namespace: "config://upgrade"
      sections:
        - "migration.strategies"
        - "validation.post_upgrade"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
    
    features:
      version_detection: true
      migration_scripts: true
      rollback_support: true
      validation_suite: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/upgrade-orchestrator-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  # ──────────────────────────────────────────────────
  # DEPLOYMENT ORCHESTRATORS (2 orchestrators)
  # ──────────────────────────────────────────────────
  
  publish_orchestrator:
    version: "1.0.0"
    status: "active"
    category: "deployment"
    description: "Publish CORTEX artifacts to PyPI, GitHub Pages"
    
    source_file: "src/operations/modules/orchestration/publish_orchestrator.py"
    entry_point: "PublishOrchestrator"
    
    config_overrides:
      namespace: "config://publish"
      sections:
        - "pypi.configuration"
        - "github_pages.build"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
    
    features:
      pypi_publishing: true
      github_pages: true
      pre_publish_validation: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/publish-config.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  intelligent_dashboard_orchestrator:
    version: "1.0.0"
    status: "active"
    category: "deployment"
    description: "Interactive D3.js dashboards for system metrics"
    
    source_file: "src/orchestrators/dashboard/intelligent_dashboard_orchestrator.py"
    entry_point: "IntelligentDashboardOrchestrator"
    
    config_overrides:
      namespace: "config://dashboard"
      sections:
        - "visualization.d3js"
        - "metrics.collectors"
    
    integrations:
      - "integration://file_system"
    
    features:
      d3js_visualizations: true
      real_time_metrics: true
      interactive_charts: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/intelligent-dashboard-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"
  
  # ──────────────────────────────────────────────────
  # SPECIALIZED ORCHESTRATORS (1 orchestrator)
  # ──────────────────────────────────────────────────
  
  cortex_lens_orchestrator:
    version: "3.0.0"
    status: "active"
    category: "specialized"
    description: "Interactive code visualization and exploration"
    
    source_file: "src/orchestrators/cortex_lens/cortex_lens_orchestrator.py"
    entry_point: "CortexLensOrchestrator"
    
    config_overrides:
      namespace: "config://cortex_lens"
      sections:
        - "visualization.settings"
        - "exploration.modes"
    
    integrations:
      - "integration://file_system"
    
    features:
      code_visualization: true
      ast_analysis: true
      interactive_exploration: true
    
    legacy_manifests:
      - "cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml"
    migration_status: "migrated"
    migration_date: "2025-12-23"

# ========================================
# SECTION 3: Validation Rules
# ========================================
# JSON Schema validation for orchestrator registry

validation:
  json_schema_path: "cortex-brain/manifests/schemas/core-manifest-schema.json"
  
  required_fields:
    - version
    - status
    - category
    - description
    - source_file
    - entry_point
  
  allowed_categories:
    - planning
    - execution
    - analysis
    - maintenance
    - deployment
    - specialized
  
  allowed_statuses:
    - draft
    - active
    - deprecated
    - archived
  
  allowed_deployment_tiers:
    - cortex
    - user
    - admin
    - dual_context

# ========================================
# SECTION 4: Migration Support
# ========================================
# Backward compatibility with legacy manifests

migration:
  enabled: true
  strategy: "parallel_validation"  # Run old + new manifests in parallel
  
  legacy_manifest_directory: "cortex-brain/manifests/orchestrators/"
  deprecation_warnings: true
  deprecation_period_days: 90  # Keep legacy manifests for 90 days
  
  adapter:
    class_name: "ManifestMigrationAdapter"
    module_path: "src.orchestration_4_0.manifests.migration_adapter"
    features:
      - "Legacy manifest parsing"
      - "Format translation (old → new)"
      - "Validation comparison (old vs new)"
      - "Rollback on mismatch"

# ========================================
# SECTION 5: Cross-Referencing
# ========================================
# URI-based linking to ConfigManifest and IntegrationManifest

cross_references:
  config_manifest: "cortex-brain/manifests/config-manifest.yaml"
  integration_manifest: "cortex-brain/manifests/integration-manifest.yaml"
  
  uri_patterns:
    config: "config://{namespace}.{section}"
    integration: "integration://{system_name}"
  
  examples:
    - "config://planning.refactoring"
    - "config://tdd.clean_code.enforcement"
    - "integration://azure_devops"
    - "integration://github"
```

### 1.3 Schema Benefits

| Benefit | Before | After | Improvement |
|---------|--------|-------|-------------|
| Lines of Code | 4,700 (11 files) | 800 (1 file) | -83% |
| Duplicate Metadata | 60% redundancy | 0% redundancy | -100% |
| Maintenance Time | 30 min/change | 5 min/change | -83% |
| Onboarding Time | 4 hours | 2 hours | -50% |

---

## 2. ConfigManifest Schema v2.0

### 2.1 Purpose & Scope

**What:** Unified runtime configuration consolidating 8 rule files  
**Why:** Eliminate 40% rule redundancy (4,500 lines → 1,200 lines)  
**How:** Category-based organization with orchestrator-specific overrides

### 2.2 Schema Definition

```yaml
# CORTEX Config Manifest v2.0
# File: cortex-brain/manifests/config-manifest.yaml

schema_version: "2.0"
manifest_type: "config"
last_updated: "2025-12-23T00:00:00Z"

# ========================================
# SECTION 1: Global Configuration
# ========================================

global:
  timezone: "UTC"
  date_format: "ISO8601"
  encoding: "utf-8"
  
  timeouts:
    default_operation: 300      # 5 minutes
    long_operation: 3600        # 1 hour
    network_request: 30         # 30 seconds
    test_execution: 600         # 10 minutes
  
  performance:
    max_parallel_operations: 4
    cache_ttl: 300              # 5 minutes
    enable_profiling: false
    memory_limit_mb: 2048
  
  file_system:
    max_file_size_mb: 100
    allowed_extensions:
      - ".py"
      - ".md"
      - ".yaml"
      - ".json"
      - ".txt"
      - ".cs"
      - ".js"
      - ".ts"
    ignore_patterns:
      - "**/__pycache__/**"
      - "**/.git/**"
      - "**/node_modules/**"
      - "**/.venv/**"
      - "**/.pytest_cache/**"
      - "**/bin/**"
      - "**/obj/**"

# ========================================
# SECTION 2: Cleanup Rules
# Consolidated from cleanup-rules.yaml + aggressive-cleanup-rules.yaml
# ========================================

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
        dry_run_first: true
        patterns:
          - "**/*.tmp"
          - "**/*.bak"
          - "**/*.pyc"
          - "**/__pycache__/**"
          - "**/*.log"
        exclude_paths:
          - "logs/important/**"
          - "cortex-brain/**"
      
      duplicate_detection:
        enabled: true
        similarity_threshold: 0.95
        min_file_size: 1024
        ignore_patterns:
          - "**/tests/**"
          - "**/examples/**"
        actions:
          - "report"
      
      empty_directories:
        enabled: true
        safe_mode: true
        exclude_patterns:
          - ".git"
          - "__pycache__"
  
  # Aggressive Mode (admin only)
  aggressive:
    enabled: false
    description: "Aggressive cleanup without confirmation (DANGEROUS)"
    
    rules:
      orphaned_files:
        enabled: true
        threshold_days: 30    # More aggressive threshold
        safe_mode: false
        dry_run_first: false
        patterns:
          - "**/*.tmp"
          - "**/*.bak"
          - "**/*.pyc"
          - "**/__pycache__/**"
          - "**/*.log"
          - "**/*.cache"
        exclude_paths:
          - "cortex-brain/**"
      
      stale_backups:
        enabled: true
        threshold_days: 7
        patterns:
          - "**/*.backup"
          - "**/.backups/**"
      
      comment_cleanup:
        enabled: true
        patterns:
          - "# TODO:"
          - "# FIXME:"
          - "# HACK:"
        action: "report_only"  # Don't delete, just report

# ========================================
# SECTION 3: Refactoring Rules
# Consolidated from refactoring-rules.yaml
# ========================================

refactoring:
  # Planning-specific refactoring
  planning:
    enabled: true
    strategies:
      complexity_reduction:
        enabled: true
        threshold: 30
        actions:
          - "extract_function"
          - "decompose_class"
      
      duplicate_elimination:
        enabled: true
        similarity_threshold: 0.90
        actions:
          - "extract_to_utility"
      
      naming_conventions:
        enabled: true
        patterns:
          functions: "snake_case"
          classes: "PascalCase"
          constants: "UPPER_SNAKE_CASE"
  
  # TDD-specific refactoring
  tdd:
    enabled: true
    strategies:
      clean_code_enforcement:
        enabled: true
        rules:
          - name: "SOLID_principles"
            enforcement: "strict"
          - name: "DRY_principle"
            enforcement: "strict"
          - name: "KISS_principle"
            enforcement: "moderate"
          - name: "YAGNI_principle"
            enforcement: "moderate"
      
      test_organization:
        enabled: true
        rules:
          - name: "arrange_act_assert"
            enforcement: "strict"
          - name: "one_assertion_per_test"
            enforcement: "moderate"
      
      code_smell_detection:
        enabled: true
        patterns:
          - "god_object"
          - "long_method"
          - "duplicate_code"
          - "dead_code"
  
  # General refactoring rules
  general:
    enabled: true
    strategies:
      code_smell_detection:
        enabled: true
        patterns:
          - name: "long_function"
            threshold_lines: 50
          - name: "too_many_parameters"
            threshold_count: 5
          - name: "nested_conditionals"
            threshold_depth: 3

# ========================================
# SECTION 4: Token Optimization Rules
# Consolidated from token-optimization-rules.yaml
# ========================================

token_optimization:
  # Planning-specific optimization
  planning:
    enabled: true
    target_reduction_percent: 95
    strategies:
      hierarchical_structure:
        enabled: true
        pattern: "master_hub_worker_plans"
      
      status_only_documents:
        enabled: true
        max_tokens: 400
      
      phase_separation:
        enabled: true
        max_tokens_per_phase: 2500
  
  # Documentation-specific optimization
  documentation:
    enabled: true
    target_reduction_percent: 80
    strategies:
      remove_examples:
        enabled: true
        keep_count: 2
      
      compress_tables:
        enabled: true
        max_rows: 20
      
      link_to_source:
        enabled: true
        pattern: "See {file}:{line}"

# ========================================
# SECTION 5: Documentation Generation Rules
# Consolidated from doc-generation-rules.yaml
# ========================================

documentation:
  # Planning documentation
  planning:
    enabled: true
    templates:
      master_plan: "cortex-brain/templates/master-plan-template.md"
      phase_plan: "cortex-brain/templates/phase-plan-template.md"
      status_doc: "cortex-brain/templates/status-doc-template.md"
    
    auto_generation:
      enabled: true
      triggers:
        - "phase_completion"
        - "milestone_achievement"
  
  # API documentation
  api:
    enabled: true
    formats:
      - "markdown"
      - "html"
    include_examples: true
    include_schemas: true
  
  # Architecture documentation
  architecture:
    enabled: true
    diagrams:
      format: "mermaid"
      auto_generate: true
      types:
        - "sequence"
        - "class"
        - "component"

# ========================================
# SECTION 6: Git Checkpoint Rules
# Consolidated from git-checkpoint-rules.yaml
# ========================================

git_checkpoint:
  commit:
    message_templates:
      feature: "feat({scope}): {message}"
      bugfix: "fix({scope}): {message}"
      refactor: "refactor({scope}): {message}"
      docs: "docs({scope}): {message}"
      test: "test({scope}): {message}"
    
    auto_commit:
      enabled: false
      triggers:
        - "test_pass"
        - "phase_completion"
  
  safety:
    pre_commit_checks:
      - "git_clean_working_directory"
      - "tests_passing"
      - "lint_passing"
    
    rollback:
      enabled: true
      create_backup_branch: true

# ========================================
# SECTION 7: Publishing Configuration
# Consolidated from publish-config.yaml
# ========================================

publish:
  pypi:
    enabled: true
    repository: "https://upload.pypi.org/legacy/"
    test_repository: "https://test.pypi.org/legacy/"
    
    validation:
      - "tests_passing"
      - "lint_passing"
      - "version_bump"
      - "changelog_updated"
  
  github_pages:
    enabled: true
    build_directory: "docs/"
    branch: "gh-pages"
    
    pre_build:
      - "run_mkdocs_build"
      - "validate_links"

# ========================================
# SECTION 8: Orchestrator-Specific Overrides
# ========================================

orchestrator_overrides:
  # TDD Orchestrator overrides
  tdd_orchestrator:
    refactoring:
      enabled: true
      enforcement_level: "strict"
    
    token_optimization:
      enabled: false  # TDD doesn't need token optimization
    
    cleanup:
      mode: "standard"  # Never aggressive
  
  # Planning Orchestrator overrides
  planning_orchestrator:
    token_optimization:
      enabled: true
      target_reduction: 95
    
    documentation:
      auto_generation: true
  
  # Maintenance Orchestrator overrides
  maintenance_orchestrator:
    cleanup:
      mode: "aggressive"  # Can use aggressive mode
      safe_mode: true     # But with safety enabled
    
    refactoring:
      enabled: true
      enforcement_level: "moderate"

# ========================================
# SECTION 9: Validation
# ========================================

validation:
  json_schema_path: "cortex-brain/manifests/schemas/config-manifest-schema.json"
  
  required_sections:
    - "global"
    - "cleanup"
    - "refactoring"
  
  allowed_modes:
    cleanup:
      - "standard"
      - "aggressive"
    enforcement_level:
      - "strict"
      - "moderate"
      - "lenient"
```

### 2.3 Schema Benefits

| Benefit | Before | After | Improvement |
|---------|--------|-------|-------------|
| Lines of Code | 4,500 (8 files) | 1,200 (1 file) | -73% |
| Duplicate Rules | 40% redundancy | 0% redundancy | -100% |
| Config Lookups | 8 files | 1 file | -88% |
| Override Complexity | Manual editing | Namespace overrides | Simple |

---

## 3. IntegrationManifest Schema v2.0

### 3.1 Purpose & Scope

**What:** External system integrations with unified adapter specifications  
**Why:** Centralize API configurations, auth, retry policies  
**How:** Adapter factory with auto-detection and middleware

### 3.2 Schema Definition

```yaml
# CORTEX Integration Manifest v2.0
# File: cortex-brain/manifests/integration-manifest.yaml

schema_version: "2.0"
manifest_type: "integration"
last_updated: "2025-12-23T00:00:00Z"

# ========================================
# SECTION 1: Integration Definitions
# ========================================

integrations:
  
  # ──────────────────────────────────
  # Azure DevOps Integration
  # ──────────────────────────────────
  
  azure_devops:
    id: "integration://azure_devops"
    name: "Azure DevOps"
    description: "Work item management, pipelines, repos"
    version: "2.1.0"
    status: "active"
    
    adapter:
      class_name: "AzureDevOpsAdapter"
      module_path: "src.orchestration_4_0.adapters.azure_devops_adapter"
      version: "2.0.0"
      fallback_adapter: "file_system"
    
    authentication:
      method: "PAT"
      env_var: "AZURE_DEVOPS_PAT"
      required_scopes:
        - "vso.work_write"
        - "vso.project"
        - "vso.build"
      validation:
        test_endpoint: "/_apis/projects"
        expected_status: 200
        timeout: 10
    
    api:
      base_url: "https://dev.azure.com"
      version: "7.1"
      endpoints:
        work_items:
          path: "/{organization}/_apis/wit/workitems"
          methods: ["GET", "POST", "PATCH", "DELETE"]
        projects:
          path: "/{organization}/_apis/projects"
          methods: ["GET"]
        pipelines:
          path: "/{organization}/{project}/_apis/pipelines"
          methods: ["GET", "POST"]
    
    rate_limiting:
      enabled: true
      requests_per_second: 10
      burst: 20
      strategy: "token_bucket"
      backoff:
        enabled: true
        initial_delay: 1
        multiplier: 2
        max_delay: 60
    
    retry_policy:
      max_retries: 3
      backoff_multiplier: 2
      retryable_status_codes: [429, 500, 502, 503, 504]
    
    middleware:
      - name: "caching"
        enabled: true
        ttl: 300
      - name: "logging"
        enabled: true
        level: "INFO"
      - name: "metrics"
        enabled: true
  
  # ──────────────────────────────────
  # GitHub Integration
  # ──────────────────────────────────
  
  github:
    id: "integration://github"
    name: "GitHub"
    description: "Issues, PRs, Actions, repos"
    version: "2.0.0"
    status: "active"
    
    adapter:
      class_name: "GitHubAdapter"
      module_path: "src.orchestration_4_0.adapters.github_adapter"
      version: "2.0.0"
      fallback_adapter: "file_system"
    
    authentication:
      method: "PAT"
      env_var: "GITHUB_PAT"
      required_scopes:
        - "repo"
        - "workflow"
      validation:
        test_endpoint: "/user"
        expected_status: 200
        timeout: 10
    
    api:
      base_url: "https://api.github.com"
      version: "2022-11-28"
      endpoints:
        issues:
          path: "/repos/{owner}/{repo}/issues"
          methods: ["GET", "POST", "PATCH"]
        actions:
          path: "/repos/{owner}/{repo}/actions"
          methods: ["GET"]
        pulls:
          path: "/repos/{owner}/{repo}/pulls"
          methods: ["GET", "POST", "PATCH"]
    
    rate_limiting:
      enabled: true
      requests_per_second: 60
      burst: 100
      strategy: "token_bucket"
      backoff:
        enabled: true
        initial_delay: 1
        multiplier: 2
        max_delay: 60
    
    retry_policy:
      max_retries: 3
      backoff_multiplier: 2
      retryable_status_codes: [429, 500, 502, 503, 504]
    
    middleware:
      - name: "caching"
        enabled: true
        ttl: 300
      - name: "logging"
        enabled: true
        level: "INFO"
      - name: "metrics"
        enabled: true
  
  # ──────────────────────────────────
  # File System Integration
  # ──────────────────────────────────
  
  file_system:
    id: "integration://file_system"
    name: "File System"
    description: "Local and network file operations"
    version: "1.0.0"
    status: "active"
    
    adapter:
      class_name: "FileSystemAdapter"
      module_path: "src.orchestration_4_0.adapters.filesystem_adapter"
      version: "1.0.0"
      fallback_adapter: null
    
    local:
      base_path: "."
      allowed_operations:
        - "read"
        - "write"
        - "delete"
        - "list"
    
    network:
      enabled: false
      base_path: null
      authentication:
        method: null
    
    middleware:
      - name: "logging"
        enabled: true
        level: "INFO"
      - name: "validation"
        enabled: true
  
  # ──────────────────────────────────
  # Brain Tier 2 Integration
  # ──────────────────────────────────
  
  brain_tier2:
    id: "integration://brain_tier2"
    name: "Brain Tier 2 Knowledge Graph"
    description: "Pattern learning and retrieval"
    version: "1.0.0"
    status: "active"
    
    adapter:
      class_name: "BrainTier2Adapter"
      module_path: "src.tier2.brain_tier2_adapter"
      version: "1.0.0"
      fallback_adapter: null
    
    operations:
      - "store_pattern"
      - "retrieve_pattern"
      - "update_confidence"
      - "query_knowledge_graph"
    
    middleware:
      - name: "caching"
        enabled: true
        ttl: 600
      - name: "logging"
        enabled: true
        level: "DEBUG"
  
  # ──────────────────────────────────
  # MCP Gateway Integration
  # ──────────────────────────────────
  
  mcp_gateway:
    id: "integration://mcp_gateway"
    name: "MCP Gateway"
    description: "Tool execution via Model Context Protocol"
    version: "1.0.0"
    status: "active"
    
    adapter:
      class_name: "MCPGatewayAdapter"
      module_path: "src.mcp.gateway_adapter"
      version: "1.0.0"
      fallback_adapter: null
    
    tools:
      - "file_operations"
      - "git_operations"
      - "test_execution"
      - "code_analysis"
    
    middleware:
      - name: "logging"
        enabled: true
        level: "INFO"
      - name: "timeout"
        enabled: true
        default_timeout: 30

# ========================================
# SECTION 2: Adapter Factory
# ========================================

adapter_factory:
  auto_detection: true
  fallback_adapter: "file_system"
  cache_ttl: 300
  
  detection_rules:
    - pattern: "https://dev.azure.com"
      adapter: "azure_devops"
    - pattern: "https://api.github.com"
      adapter: "github"
    - pattern: "file://"
      adapter: "file_system"
  
  middleware_pipeline:
    - stage: "pre_request"
      handlers:
        - "authentication"
        - "rate_limiting"
        - "caching"
    - stage: "request"
      handlers:
        - "retry"
        - "timeout"
    - stage: "post_request"
      handlers:
        - "logging"
        - "metrics"

# ========================================
# SECTION 3: Validation
# ========================================

validation:
  json_schema_path: "cortex-brain/manifests/schemas/integration-manifest-schema.json"
  
  required_fields:
    - id
    - name
    - version
    - status
    - adapter
  
  allowed_statuses:
    - "active"
    - "deprecated"
    - "experimental"
```

### 3.3 Schema Benefits

| Benefit | Before | After | Improvement |
|---------|--------|-------|-------------|
| Lines of Code | ~4,000 (scattered) | 500 (1 file) | -88% |
| API Configs | Duplicated | Centralized | Unified |
| Auth Strategies | Inconsistent | Standardized | Consistent |
| Retry Policies | Per-orchestrator | Global | Reusable |

---

## 4. Inheritance Model

### 4.1 YAML Anchors & Aliases

**Pattern:** Use YAML anchors (`&`) and aliases (`*`) for reusable blocks

**Example:**
```yaml
# Define reusable logging config
logging_defaults: &logging_defaults
  level: "INFO"
  format: "structured"
  destinations:
    - type: "console"
      enabled: true

# Reference in orchestrator
orchestrators:
  planning_orchestrator:
    logging: *logging_defaults  # Inherits all defaults
```

### 4.2 Cross-Referencing via URIs

**Pattern:** Use URI-based references for config/integration lookups

**Syntax:**
- Config: `config://{namespace}.{section}`
- Integration: `integration://{system_name}`

**Examples:**
```yaml
orchestrators:
  tdd_orchestrator:
    config_overrides:
      namespace: "config://tdd"
      sections:
        - "refactoring.tdd"
        - "clean_code.enforcement"
    
    integrations:
      - "integration://github"
      - "integration://file_system"
```

**Loader Logic:**
```python
def resolve_config_reference(uri: str) -> Dict:
    """Resolve config:// URI to ConfigManifest section"""
    namespace, section = uri.replace("config://", "").split(".", 1)
    config = load_config_manifest()
    return config[namespace][section]

def resolve_integration_reference(uri: str) -> Dict:
    """Resolve integration:// URI to IntegrationManifest"""
    system_name = uri.replace("integration://", "")
    integrations = load_integration_manifest()
    return integrations["integrations"][system_name]
```

### 4.3 Inheritance Hierarchy

```
BaseOrchestrator (defaults)
  ├─ PlanningOrchestrator
  │    ├─ TDDOrchestrator (inherits planning config)
  │    ├─ ADOOrchestrator (inherits planning config)
  │    └─ SanitizationOrchestrator
  ├─ ExecutionOrchestrator
  │    ├─ DevOpsOrchestrator
  │    └─ CICDSelfHealingOrchestrator
  ├─ AnalysisOrchestrator
  │    ├─ DocumentationOrchestrator
  │    ├─ SanitizationOrchestrator
  │    └─ ContextualReviewOrchestrator
  └─ MaintenanceOrchestrator
       ├─ RefinementOrchestrator
       ├─ GitCheckpointOrchestrator
       └─ UpgradeOrchestrator
```

---

## 5. Migration Path

### 5.1 Parallel Validation Strategy

**Phase 1: Parallel Execution (Days 1-5)**
- Load both old and new manifests
- Execute orchestrators with new manifests
- Compare results with old manifest baseline
- Log discrepancies

**Phase 2: Deprecation Warnings (Days 6-95)**
- New manifests PRIMARY
- Old manifests SECONDARY (fallback)
- Warning logs on old manifest usage

**Phase 3: Legacy Removal (Day 96+)**
- Delete old manifest files
- Remove ManifestMigrationAdapter
- Update all documentation

### 5.2 ManifestMigrationAdapter

```python
class ManifestMigrationAdapter:
    """Translate legacy manifests to v2.0 format"""
    
    def load_legacy_manifest(self, path: str) -> Dict:
        """Load old manifest format"""
        pass
    
    def translate_to_v2(self, legacy_data: Dict) -> Dict:
        """Convert to v2.0 schema"""
        pass
    
    def validate_equivalence(self, old: Dict, new: Dict) -> bool:
        """Ensure old and new are functionally equivalent"""
        pass
    
    def rollback_on_failure(self):
        """Revert to legacy manifests if validation fails"""
        pass
```

### 5.3 Migration Checklist

- [ ] CoreManifest schema implemented
- [ ] ConfigManifest schema implemented
- [ ] IntegrationManifest schema implemented
- [ ] ManifestLoader supports v2.0
- [ ] ManifestMigrationAdapter implemented
- [ ] All 16 orchestrators migrated
- [ ] Parallel validation passing (100%)
- [ ] Performance impact < 5%
- [ ] Documentation updated

---

## 6. JSON Schema Validation

### 6.1 CoreManifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CORTEX Core Manifest v2.0",
  "type": "object",
  "required": ["schema_version", "manifest_type", "orchestrators"],
  "properties": {
    "schema_version": {
      "type": "string",
      "enum": ["2.0"]
    },
    "manifest_type": {
      "type": "string",
      "enum": ["core"]
    },
    "orchestrators": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "required": ["version", "status", "category", "description", "source_file"],
          "properties": {
            "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
            "status": { "enum": ["draft", "active", "deprecated", "archived"] },
            "category": { "enum": ["planning", "execution", "analysis", "maintenance", "deployment", "specialized"] },
            "description": { "type": "string", "minLength": 50 },
            "source_file": { "type": "string", "pattern": "^src/" }
          }
        }
      }
    }
  }
}
```

### 6.2 ConfigManifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CORTEX Config Manifest v2.0",
  "type": "object",
  "required": ["schema_version", "manifest_type", "cleanup", "refactoring"],
  "properties": {
    "schema_version": { "enum": ["2.0"] },
    "manifest_type": { "enum": ["config"] },
    "cleanup": {
      "type": "object",
      "required": ["standard"],
      "properties": {
        "standard": { "$ref": "#/definitions/cleanup_mode" },
        "aggressive": { "$ref": "#/definitions/cleanup_mode" }
      }
    }
  },
  "definitions": {
    "cleanup_mode": {
      "type": "object",
      "required": ["enabled", "rules"],
      "properties": {
        "enabled": { "type": "boolean" },
        "rules": { "type": "object" }
      }
    }
  }
}
```

### 6.3 IntegrationManifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CORTEX Integration Manifest v2.0",
  "type": "object",
  "required": ["schema_version", "manifest_type", "integrations"],
  "properties": {
    "schema_version": { "enum": ["2.0"] },
    "manifest_type": { "enum": ["integration"] },
    "integrations": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "required": ["id", "name", "version", "status", "adapter"],
          "properties": {
            "id": { "type": "string", "pattern": "^integration://" },
            "name": { "type": "string" },
            "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
            "status": { "enum": ["active", "deprecated", "experimental"] },
            "adapter": {
              "type": "object",
              "required": ["class_name", "module_path"],
              "properties": {
                "class_name": { "type": "string" },
                "module_path": { "type": "string", "pattern": "^src\\." }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 7. Implementation Timeline

### Week 15: Day 2-5 (Phase 7.2-7.5)

| Day | Task | Deliverables |
|-----|------|--------------|
| Day 2 | Schema design (THIS DOCUMENT) | 3 schema specs, inheritance model, migration path |
| Day 3 | Implement CoreManifest | core-manifest.yaml (800 lines), JSON schema, tests |
| Day 4 | Implement ConfigManifest | config-manifest.yaml (1,200 lines), JSON schema, tests |
| Day 5 | Implement IntegrationManifest | integration-manifest.yaml (500 lines), JSON schema, tests |

---

## 8. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Files Reduced** | 40 → 3 (-92%) | File count in manifests/ |
| **Lines Reduced** | 23,144 → 2,500 (-88%) | Total LOC across manifests |
| **Redundancy Eliminated** | 0% | Duplicate key-value pairs |
| **Manifest Load Time** | < 100ms | Performance benchmark |
| **Orchestrator Onboarding** | < 2 hours | Time to add new orchestrator |
| **Test Pass Rate** | 100% | All 164+ tests passing |

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Breaking changes** | HIGH | HIGH | Parallel validation, 90-day deprecation |
| **Performance regression** | MEDIUM | MEDIUM | Caching, lazy loading |
| **Migration complexity** | MEDIUM | HIGH | ManifestMigrationAdapter, rollback |
| **Orchestrator failures** | LOW | HIGH | Comprehensive testing, fallback to legacy |
| **Schema validation overhead** | LOW | LOW | Validate once at startup |

---

## 10. Next Steps

### Task 7.3: Implement CoreManifest (Week 15, Day 3)
1. Create `cortex-brain/manifests/core-manifest.yaml` (800 lines)
2. Create JSON schema `core-manifest-schema.json`
3. Implement ManifestLoader for CoreManifest
4. Write 20 tests for manifest loading/validation
5. Update all 16 orchestrators to reference CoreManifest

### Task 7.4: Implement ConfigManifest (Week 15, Day 4)
1. Create `cortex-brain/manifests/config-manifest.yaml` (1,200 lines)
2. Create JSON schema `config-manifest-schema.json`
3. Implement config resolution (URI → actual config)
4. Write 15 tests for config overrides
5. Consolidate 8 rule files into ConfigManifest

### Task 7.5: Implement IntegrationManifest (Week 15, Day 5)
1. Create `cortex-brain/manifests/integration-manifest.yaml` (500 lines)
2. Create JSON schema `integration-manifest-schema.json`
3. Implement adapter factory with auto-detection
4. Write 10 tests for adapter loading
5. Update orchestrators to use integration URIs

---

**Status:** ✅ Complete - Ready for Phase 7.3 (Implementation)  
**Next:** Task 7.3 - Implement CoreManifest with 16 orchestrator registrations
