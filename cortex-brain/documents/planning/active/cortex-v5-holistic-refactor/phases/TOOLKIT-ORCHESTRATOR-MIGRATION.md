# 🧰 Toolkit Orchestrator Migration Plan

**Feature:** Convert scripts/ toolkit manager → intelligent Toolkit Orchestrator  
**Created:** January 3, 2026  
**Status:** Phase 6.6 - Toolkit Infrastructure Enhancement  
**Priority:** HIGH (Foundation for all tool operations)  
**Complexity:** TIER 3 (INFRASTRUCTURE)

---

## 📊 Migration Progress

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| # | Phase | Progress | Duration | Status |
|---|-------|----------|----------|--------|
| 1 | Discovery & Analysis | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 2 | Manifest Generation | `░░░░░░░░░░` | 3h | ⏸️ Not Started |
| 3 | Folder Structure | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 4 | Orchestrator Implementation | `░░░░░░░░░░` | 6h | ⏸️ Not Started |
| 5 | Tool Migration | `░░░░░░░░░░` | 8h | ⏸️ Not Started |
| 6 | Import Path Updates | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 7 | CLI Integration | `░░░░░░░░░░` | 3h | ⏸️ Not Started |
| 8 | Testing & Validation | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 9 | Documentation | `░░░░░░░░░░` | 2h | ⏸️ Not Started |

**Total Estimated Time:** 38 hours (~5 days)

---

## 🎯 Objectives

**Primary Goals:**
1. **Organize 470+ scripts** into logical folder structure (7 categories)
2. **Create manifest index** for tool discovery and self-documentation
3. **Prevent duplication** through intelligent detection and consolidation suggestions
4. **Maximize utility** via CLI integration and usage tracking
5. **Enable lifecycle management** (active/deprecated/experimental states)

**Strategic Benefits:**
- **Discoverability:** Developers can find the right tool instantly (`cortex toolkit search`)
- **Maintainability:** Clear categorization reduces cognitive load
- **Quality:** Duplication detection prevents redundant implementations
- **Self-Documentation:** Manifest serves as living documentation
- **Automation:** Orchestrator enables intelligent tool selection

---

## 📋 Current State Analysis

### Scripts Directory Inventory (470+ files)

**Discovered Categories:**

| Category | Count | Pattern | Examples |
|----------|-------|---------|----------|
| **Maintenance** | 68 | `cleanup_*`, `fix_*`, `repair_*` | cleanup_temp_files.py, fix_html_issues.py, repair_html_structure.py |
| **Generation** | 42 | `generate_*`, `create_*` | generate_docs_from_code.py, create_deploy_package.sh, generate_uml_standalone.py |
| **Validation** | 38 | `validate_*`, `check_*`, `verify_*` | validate_deployment.py, check_wiring_integrity.py, verify_import.py |
| **Analysis** | 31 | `analyze_*`, `audit_*`, `scan_*` | analyze_critical.py, audit_cleanup_safety.py, scan_external_repos.py |
| **Migration** | 24 | `migrate_*`, `execute_phase*` | migrate_brain_db.py, migrate_planning_root_files.py, execute_phase6_migration.py |
| **Documentation** | 19 | `regenerate_*_docs`, `*_documentation` | regenerate_all_docs.py, generate_documentation.py, epm_documentation_orchestrator.py |
| **Orchestrators** | 12 | `*_orchestrator*`, `cortex-*` | cortex-cli.py, ado_orchestrator_v2.py (in src/), planning_orchestrator_v5.py (in src/) |
| **Utilities** | 236 | Everything else | deploy_cortex.py, version_manager.py, token_pricing_calculator.py |

**Total:** 470 files

### Problem Patterns

**1. Duplication Hotspots:**
- **Cleanup tools (12 duplicates):** `cleanup_temp_files.py`, `cleanup_unnecessary_files.py`, `master_cleanup.py`, `cleanup_and_sweep.py`, `final_cleanup.py`, `cleanup_pre_commit.py`
- **HTML repair tools (8 duplicates):** `fix_html_issues.py`, `repair_html_structure.py`, `fix_broken_internal_links.py`, `repair_html_beautifulsoup.py`, `repair_html_lxml.py`
- **Doc generators (6 duplicates):** `generate_docs_from_code.py`, `regenerate_all_docs.py`, `generate_documentation.py`, `generate_missing_docs.py`, `generate_knowledge_docs.py`
- **Validation tools (9 duplicates):** `validate_deployment.py`, `validate_cortex_3_0.py`, `validate_cortex_4_foundation.py`, `validate_gates_post_deployment.py`

**2. Naming Inconsistencies:**
- Mixed conventions: `cleanup_temp_files.py` vs `cleanup-pre-commit.py`
- Unclear versioning: `validate_cortex_3_0.py`, `validate_cortex_4_foundation.py`
- Generic names: `final_cleanup.py`, `quick_fix_tests.py`

**3. Import Path Complexity:**
- Flat imports: `from scripts.cleanup_temp_files import cleanup`
- No namespace organization
- Circular dependency risk

**4. Lifecycle Chaos:**
- Obsolete tools not removed: `cleanup_legacy_3_0.py`
- Experimental tools mixed with production: `simulate_hybrid_capture.py`
- No deprecation tracking

---

## 🏗️ Target Architecture

### Folder Structure

```
scripts/
├── toolkit-manifest.yaml              # Master index (800+ lines)
├── __init__.py                        # Import aliasing
├── cortex-cli.py                      # Main CLI entry point
│
├── orchestrators/                     # 🛡️ Autonomous orchestrators (moved from src/)
│   ├── __init__.py
│   ├── planning/
│   │   ├── __init__.py
│   │   └── planning_orchestrator_v5.py
│   ├── ado/
│   │   ├── __init__.py
│   │   └── ado_orchestrator_v2.py
│   ├── tdd/
│   │   ├── __init__.py
│   │   └── tdd_orchestrator_v2.py
│   ├── cleanup/
│   │   ├── __init__.py
│   │   └── cleanup_orchestrator_v2.py
│   ├── vacuum/
│   │   ├── __init__.py
│   │   └── vacuum_orchestrator_v2.py
│   └── toolkit/                       # NEW: Toolkit Orchestrator
│       ├── __init__.py
│       └── toolkit_orchestrator.py
│
├── maintenance/                       # Cleanup, repair, health (68 tools)
│   ├── __init__.py
│   ├── cleanup/
│   │   ├── __init__.py
│   │   ├── cleanup_temp_files.py
│   │   ├── cleanup_inline_styles.py
│   │   ├── cleanup_pre_commit.py
│   │   └── master_cleanup.py         # Consolidated cleanup orchestrator
│   ├── repair/
│   │   ├── __init__.py
│   │   ├── fix_html_issues.py
│   │   ├── repair_html_structure.py
│   │   └── fix_yaml_comprehensive.py
│   └── health/
│       ├── __init__.py
│       ├── monitor_brain_health.py
│       └── check_wiring_integrity.py
│
├── generators/                        # Code/doc generation (42 tools)
│   ├── __init__.py
│   ├── documentation/
│   │   ├── __init__.py
│   │   ├── generate_docs_from_code.py
│   │   ├── regenerate_all_docs.py
│   │   └── generate_knowledge_docs.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── generate_test_templates.py
│   │   └── generate_performance_tests.py
│   ├── diagrams/
│   │   ├── __init__.py
│   │   ├── generate_uml_standalone.py
│   │   └── dependency_graph_generator.py
│   └── prompts/
│       ├── __init__.py
│       ├── generate_prompt_templates.py
│       └── regenerate_cortex_prompts.py
│
├── validators/                        # Validation, verification (38 tools)
│   ├── __init__.py
│   ├── deployment/
│   │   ├── __init__.py
│   │   ├── validate_deployment.py
│   │   └── post_deployment_check.py
│   ├── configuration/
│   │   ├── __init__.py
│   │   ├── validate_orchestrator_config.py
│   │   └── validate_manifests.py
│   └── quality/
│       ├── __init__.py
│       ├── validate_templates.py
│       └── check_commit_score.py
│
├── analyzers/                         # Analysis, auditing (31 tools)
│   ├── __init__.py
│   ├── code/
│   │   ├── __init__.py
│   │   ├── analyze_critical.py
│   │   └── analyze_unwired_components.py
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── measure_prompt_tokens.py
│   │   └── token_pricing_calculator.py
│   └── patterns/
│       ├── __init__.py
│       ├── search_patterns.py
│       └── detect_duplicates.py
│
├── migrations/                        # Database/schema migrations (24 tools)
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── migrate_brain_db.py
│   │   └── init_ado_database.py
│   └── schema/
│       ├── __init__.py
│       ├── migrate_tier1_schema.py
│       └── migrate_enhancement_catalog_schema.py
│
├── utilities/                         # General utilities (236 tools)
│   ├── __init__.py
│   ├── file_ops/
│   │   ├── __init__.py
│   │   ├── process_includes.py
│   │   └── batch_path_hardening.py
│   ├── git_ops/
│   │   ├── __init__.py
│   │   ├── git-sync.sh
│   │   └── install_git_hooks.py
│   └── deployment/
│       ├── __init__.py
│       ├── deploy_cortex.py
│       └── build_package.py
│
├── cli_wrappers/                      # CLI integration
│   ├── cortex-bug
│   ├── cortex-capture
│   ├── cortex-feature
│   └── cortex-resume
│
├── launchers/                         # Launch scripts
│   ├── launch_docs.sh
│   └── launch_dashboard.ps1
│
└── admin/                             # Administrative tools
    └── cortex_system_doctor.py
```

### Manifest Schema: `toolkit-manifest.yaml`

```yaml
version: "1.0.0"
description: "CORTEX Toolkit Manifest - Indexed tool registry"
last_updated: "2026-01-03T10:30:00Z"
total_tools: 470

# Category definitions
categories:
  orchestrators:
    description: "Autonomous orchestrators with Python implementations"
    count: 12
    path: "scripts/orchestrators/"
    tools:
      - id: "planning_v5"
        name: "Planning Orchestrator v5"
        path: "scripts/orchestrators/planning/planning_orchestrator_v5.py"
        type: "autonomous"
        purpose: "Create structured plans with 4-folder structure and context gathering"
        entry_point: "python3 scripts/cortex-cli.py planning_system"
        options:
          - name: "--phase"
            type: "string"
            description: "Specify phase to execute"
          - name: "--resume"
            type: "flag"
            description: "Resume from last checkpoint"
        dependencies: []
        response_template: "autonomous_planning_progress"
        status: "active"
        version: "5.0.0"
        last_modified: "2026-01-02"
        author: "Asif Hussain"
        tests: "tests/orchestrators/planning/test_planning_v5.py"
  
  maintenance:
    description: "System maintenance, cleanup, and repair tools"
    count: 68
    path: "scripts/maintenance/"
    subcategories: ["cleanup", "repair", "health"]
    tools:
      - id: "cleanup_temp_files"
        name: "Cleanup Temp Files"
        path: "scripts/maintenance/cleanup/cleanup_temp_files.py"
        purpose: "Remove temporary files from cortex-brain/ directories"
        entry_point: "python3 scripts/maintenance/cleanup/cleanup_temp_files.py"
        options:
          - name: "--dry-run"
            type: "flag"
            description: "Preview changes without executing"
          - name: "--aggressive"
            type: "flag"
            description: "Remove all temp files including caches"
        dependencies: []
        status: "active"
        similar_tools:
          - id: "cleanup_unnecessary_files"
            similarity_score: 0.85
            reason: "Overlapping functionality for file cleanup"
          - id: "master_cleanup"
            similarity_score: 0.92
            reason: "Broader cleanup scope, includes temp files"
        consolidation_candidate: true
        consolidation_target: "master_cleanup"
  
  generators:
    description: "Code, documentation, and artifact generation"
    count: 42
    path: "scripts/generators/"
    subcategories: ["documentation", "tests", "diagrams", "prompts"]
    tools:
      - id: "generate_docs_from_code"
        name: "Generate Docs from Code"
        path: "scripts/generators/documentation/generate_docs_from_code.py"
        purpose: "Generate markdown documentation from Python docstrings"
        entry_point: "python3 scripts/generators/documentation/generate_docs_from_code.py"
        options:
          - name: "--module"
            type: "string"
            description: "Module to document"
          - name: "--output"
            type: "path"
            description: "Output directory"
        dependencies: ["ast"]
        status: "active"

# Duplication detection rules
duplication_rules:
  - category: "maintenance"
    pattern: "cleanup_*"
    check_purpose: true
    check_options: ["--dry-run", "--aggressive"]
    similarity_threshold: 0.80
    suggest_consolidation: true
  
  - category: "validators"
    pattern: "validate_*"
    check_options: ["--strict", "--dry-run"]
    similarity_threshold: 0.75
    suggest_consolidation: true
  
  - category: "generators"
    pattern: "generate_*_docs*"
    check_dependencies: true
    similarity_threshold: 0.85
    suggest_consolidation: true

# Lifecycle management
lifecycle:
  deprecated:
    - id: "cleanup_legacy_3_0"
      path: "scripts/maintenance/cleanup/cleanup_legacy_3_0.py"
      reason: "Replaced by cleanup_orchestrator_v2"
      deprecated_date: "2025-12-15"
      removal_date: "2026-02-01"
      replacement: "cleanup_orchestrator_v2"
  
  experimental:
    - id: "simulate_hybrid_capture"
      path: "scripts/utilities/simulate_hybrid_capture.py"
      status: "testing"
      target_release: "v4.1.0"
      stability: "alpha"

# Search index (for fast tool discovery)
search_index:
  keywords:
    "cleanup":
      - cleanup_temp_files
      - master_cleanup
      - cleanup_inline_styles
    "validation":
      - validate_deployment
      - validate_orchestrator_config
      - validate_manifests
    "documentation":
      - generate_docs_from_code
      - regenerate_all_docs
      - generate_knowledge_docs
    "testing":
      - generate_test_templates
      - generate_performance_tests
      - run_tests_with_progress

# Usage tracking (optional, for analytics)
usage_stats:
  most_used:
    - tool: "cortex-cli.py"
      count: 1247
    - tool: "validate_deployment.py"
      count: 523
    - tool: "cleanup_temp_files.py"
      count: 412
```

---

## 📋 Phase 1: Discovery & Analysis

**Duration:** 4 hours

### Tasks

**1.1 Complete Script Inventory (1 hour)**
- Scan all 470 files in `scripts/` directory
- Extract metadata:
  - Entry points (`if __name__ == "__main__"`)
  - Dependencies (`import` statements)
  - Command-line options (argparse, click)
  - Docstrings (purpose description)
- Generate inventory report: `context/script-inventory-report.json`

**1.2 Categorization Analysis (1.5 hours)**
- Group scripts by naming patterns:
  - `cleanup_*`, `fix_*`, `repair_*` → Maintenance
  - `generate_*`, `create_*` → Generators
  - `validate_*`, `check_*`, `verify_*` → Validators
  - `analyze_*`, `audit_*`, `scan_*` → Analyzers
  - `migrate_*` → Migrations
- Manual review of 236 uncategorized utilities
- Create category mapping: `context/category-mapping.yaml`

**1.3 Duplication Detection (1 hour)**
- Semantic analysis of tool purposes
- Compare command-line options across similar tools
- Identify consolidation opportunities
- Generate duplication report: `context/duplication-report.md`

**1.4 Import Path Analysis (0.5 hours)**
- Scan codebase for `from scripts.*` imports
- Identify affected files (orchestrators, tests, other scripts)
- Generate import dependency graph: `context/import-dependency-graph.json`

### Deliverables

- `context/script-inventory-report.json` (470+ entries)
- `context/category-mapping.yaml` (7 categories + subcategories)
- `context/duplication-report.md` (consolidation recommendations)
- `context/import-dependency-graph.json` (import relationships)

### Acceptance Criteria

- [ ] All 470 scripts inventoried with metadata
- [ ] Categorization complete (100% coverage)
- [ ] Duplication hotspots identified (12+ cleanup, 8+ repair, 6+ generators)
- [ ] Import dependencies mapped

---

## 📋 Phase 2: Manifest Generation

**Duration:** 3 hours

### Tasks

**2.1 Manifest Schema Design (0.5 hours)**
- Define YAML structure (categories, tools, duplication_rules, lifecycle)
- Specify tool metadata fields (id, name, path, purpose, entry_point, options, dependencies)
- Design search index structure

**2.2 Automated Manifest Generation (1.5 hours)**
- Create `scripts/generators/manifest/generate_toolkit_manifest.py`
- Parse script inventory report
- Extract metadata from source files (docstrings, argparse)
- Generate toolkit-manifest.yaml

**2.3 Manual Enrichment (1 hour)**
- Add purpose descriptions for unclear tools
- Define duplication rules per category
- Populate lifecycle states (deprecated, experimental)
- Add search keywords
- Validate manifest structure

### Deliverables

- `scripts/toolkit-manifest.yaml` (800+ lines)
- `scripts/generators/manifest/generate_toolkit_manifest.py` (300+ lines)

### Acceptance Criteria

- [ ] Manifest covers all 470 tools
- [ ] All required fields populated (id, name, path, purpose, entry_point)
- [ ] Duplication rules defined for 3+ categories
- [ ] Lifecycle tracking for deprecated/experimental tools
- [ ] Manifest validates against schema

---

## 📋 Phase 3: Folder Structure Creation

**Duration:** 4 hours

### Tasks

**3.1 Create Category Folders (0.5 hours)**
```bash
mkdir -p scripts/{orchestrators,maintenance,generators,validators,analyzers,migrations,utilities}/{cleanup,repair,health,documentation,tests,diagrams,prompts,deployment,configuration,quality,code,metrics,patterns,database,schema,file_ops,git_ops,deployment}
```

**3.2 Tool Migration Dry Run (1 hour)**
- Generate migration plan: old path → new path mapping
- Identify conflicts (duplicate names, circular dependencies)
- Create rollback script
- Generate migration report: `context/migration-plan.md`

**3.3 Automated Tool Migration (1.5 hours)**
- Create `scripts/migrations/toolkit/migrate_toolkit_structure.py`
- Move scripts to new category folders
- Preserve Git history (`git mv`)
- Update __init__.py files with imports

**3.4 Verify Migration (1 hour)**
- Check all files moved correctly
- Validate folder structure
- Run smoke tests (import all tools)
- Generate migration summary: `reports/toolkit-migration-summary.md`

### Deliverables

- Organized folder structure (7 categories + 24 subcategories)
- `scripts/migrations/toolkit/migrate_toolkit_structure.py` (400+ lines)
- `context/migration-plan.md` (470+ entries)
- `reports/toolkit-migration-summary.md` (migration results)

### Acceptance Criteria

- [ ] All category folders created
- [ ] All 470 tools migrated to new structure
- [ ] Git history preserved
- [ ] __init__.py files generated for all folders
- [ ] Zero file losses

---

## 📋 Phase 4: Toolkit Orchestrator Implementation

**Duration:** 6 hours

### Tasks

**4.1 Core Orchestrator Class (2 hours)**

```python
# scripts/orchestrators/toolkit/toolkit_orchestrator.py

class ToolkitOrchestrator:
    """
    Intelligent toolkit manager with manifest-based indexing.
    """
    
    def __init__(self, manifest_path: str = "scripts/toolkit-manifest.yaml"):
        self.manifest = self._load_manifest(manifest_path)
        self.search_index = self._build_search_index()
    
    def search_tools(
        self, 
        query: str, 
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ToolInfo]:
        """
        Search tools by purpose, name, keywords, or dependencies.
        
        Args:
            query: Search query (purpose keywords)
            category: Filter by category (maintenance, generators, etc.)
            status: Filter by status (active, deprecated, experimental)
        
        Returns:
            List of matching tools with relevance scores
        """
        pass
    
    def get_tool_info(self, tool_id: str) -> ToolInfo:
        """Get detailed information about a specific tool."""
        pass
    
    def detect_duplicates(
        self, 
        category: Optional[str] = None
    ) -> List[DuplicationReport]:
        """
        Find tools with similar purposes/functionality.
        
        Args:
            category: Limit search to specific category
        
        Returns:
            List of duplication reports with similarity scores
        """
        pass
    
    def suggest_consolidation(
        self, 
        tool_ids: List[str]
    ) -> ConsolidationPlan:
        """
        Generate plan to consolidate duplicate tools.
        
        Args:
            tool_ids: Tools to consolidate
        
        Returns:
            Consolidation plan with migration strategy
        """
        pass
    
    def list_deprecated(self) -> List[DeprecatedTool]:
        """List tools scheduled for removal."""
        pass
    
    def validate_manifest(self) -> ValidationReport:
        """
        Validate manifest against actual filesystem.
        
        Checks:
        - All manifest paths exist
        - All scripts have manifest entries
        - No orphaned entries
        - Entry points are valid
        """
        pass
```

**4.2 Search & Discovery (1.5 hours)**
- Implement keyword-based search
- Add fuzzy matching for typos
- Build relevance scoring
- Support category filtering

**4.3 Duplication Detection (1.5 hours)**
- Semantic similarity analysis (purpose descriptions)
- Option overlap detection (same CLI flags)
- Dependency similarity
- Generate similarity scores (0.0-1.0)

**4.4 Validation & Health (1 hour)**
- Manifest consistency checks
- Filesystem validation
- Entry point verification
- Orphaned file detection

### Deliverables

- `scripts/orchestrators/toolkit/toolkit_orchestrator.py` (600+ lines)
- `tests/orchestrators/toolkit/test_toolkit_orchestrator.py` (400+ lines)

### Acceptance Criteria

- [ ] ToolkitOrchestrator class implemented
- [ ] search_tools() working with keyword matching
- [ ] detect_duplicates() identifies 30+ duplication hotspots
- [ ] validate_manifest() catches inconsistencies
- [ ] 100% test coverage

---

## 📋 Phase 5: Tool Migration

**Duration:** 8 hours

### Tasks

**5.1 Execute Filesystem Migration (2 hours)**
- Run `migrate_toolkit_structure.py`
- Move all 470 tools to new folders
- Create __init__.py files
- Update Git tracking

**5.2 Update Internal Imports (3 hours)**
- Scan codebase for `from scripts.*` imports
- Update to new paths:
  - `from scripts.cleanup_temp_files` → `from scripts.maintenance.cleanup.cleanup_temp_files`
  - `from scripts.generate_docs_from_code` → `from scripts.generators.documentation.generate_docs_from_code`
- Update orchestrator imports in `src/`
- Update test imports in `tests/`

**5.3 Update Documentation References (1 hour)**
- Update README.md
- Update CORTEX.prompt.md
- Update guide documents
- Update manifest paths

**5.4 Consolidate Duplicate Tools (2 hours)**
- Merge 12 cleanup tools → `master_cleanup.py`
- Merge 8 HTML repair tools → `repair_html_comprehensive.py`
- Merge 6 doc generators → `generate_docs_unified.py`
- Update manifest with deprecation notices

### Deliverables

- All 470 tools in new locations
- Updated imports (100+ files)
- Consolidated tools (3 new unified tools)
- Updated documentation

### Acceptance Criteria

- [ ] All tools migrated successfully
- [ ] All imports updated (zero import errors)
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Deprecated tools marked in manifest

---

## 📋 Phase 6: Import Path Updates

**Duration:** 4 hours

### Tasks

**6.1 Automated Import Rewriting (2 hours)**
- Create `scripts/migrations/toolkit/rewrite_imports.py`
- Parse Python files for `import scripts.*` statements
- Rewrite to new paths
- Handle edge cases (aliased imports, from...import *)

**6.2 Test Import Paths (1 hour)**
- Run test suite: `pytest tests/`
- Verify all imports resolve
- Fix any broken imports manually

**6.3 CLI Wrapper Updates (1 hour)**
- Update `cortex-cli.py` imports
- Update CLI wrappers (cortex-bug, cortex-capture, etc.)
- Test all CLI commands

### Deliverables

- `scripts/migrations/toolkit/rewrite_imports.py` (250+ lines)
- Updated import paths (100+ files)
- All tests passing

### Acceptance Criteria

- [ ] All imports rewritten automatically
- [ ] Test suite passes (100%)
- [ ] CLI commands working
- [ ] Zero import errors

---

## 📋 Phase 7: CLI Integration

**Duration:** 3 hours

### Tasks

**7.1 CLI Command Implementation (2 hours)**

```python
# scripts/cortex-cli.py additions

@cli.group()
def toolkit():
    """Toolkit management commands."""
    pass

@toolkit.command()
@click.argument('query')
@click.option('--category', help='Filter by category')
@click.option('--status', help='Filter by status (active/deprecated/experimental)')
def search(query, category, status):
    """Search for tools by purpose or keywords."""
    orchestrator = ToolkitOrchestrator()
    results = orchestrator.search_tools(query, category, status)
    display_search_results(results)

@toolkit.command()
@click.argument('tool_id')
def info(tool_id):
    """Get detailed information about a tool."""
    orchestrator = ToolkitOrchestrator()
    tool_info = orchestrator.get_tool_info(tool_id)
    display_tool_info(tool_info)

@toolkit.command()
@click.option('--category', help='Limit to specific category')
def duplicates(category):
    """Find duplicate tools."""
    orchestrator = ToolkitOrchestrator()
    duplication_reports = orchestrator.detect_duplicates(category)
    display_duplication_reports(duplication_reports)

@toolkit.command()
def deprecated():
    """List deprecated tools."""
    orchestrator = ToolkitOrchestrator()
    deprecated_tools = orchestrator.list_deprecated()
    display_deprecated_tools(deprecated_tools)

@toolkit.command()
@click.option('--fix', is_flag=True, help='Auto-fix inconsistencies')
def validate(fix):
    """Validate toolkit manifest."""
    orchestrator = ToolkitOrchestrator()
    validation_report = orchestrator.validate_manifest()
    display_validation_report(validation_report)
    
    if fix and validation_report.has_fixable_issues():
        orchestrator.fix_manifest_issues()
```

**7.2 Output Formatting (1 hour)**
- Colorized terminal output (rich library)
- Table formatting for search results
- Progress bars for validation
- Interactive mode for consolidation

### Deliverables

- CLI commands implemented in `cortex-cli.py`
- Rich terminal formatting

### Acceptance Criteria

- [ ] All 5 CLI commands working (search, info, duplicates, deprecated, validate)
- [ ] Output formatted with tables and colors
- [ ] Help text complete
- [ ] Interactive mode functional

---

## 📋 Phase 8: Testing & Validation

**Duration:** 4 hours

### Tasks

**8.1 Unit Tests (2 hours)**
- Test ToolkitOrchestrator methods
- Test search functionality
- Test duplication detection
- Test validation logic
- Target: 100% coverage

**8.2 Integration Tests (1 hour)**
- Test CLI commands end-to-end
- Test tool discovery workflow
- Test consolidation suggestions
- Test manifest validation

**8.3 Regression Testing (1 hour)**
- Run full test suite: `pytest tests/`
- Verify all orchestrators still work
- Test all scripts in new locations
- Smoke test all CLI commands

### Deliverables

- `tests/orchestrators/toolkit/test_toolkit_orchestrator.py` (400+ lines)
- `tests/orchestrators/toolkit/test_toolkit_cli.py` (200+ lines)
- All tests passing

### Acceptance Criteria

- [ ] 100% test coverage for ToolkitOrchestrator
- [ ] All integration tests passing
- [ ] Zero regressions in existing functionality
- [ ] All 470 tools verified working

---

## 📋 Phase 9: Documentation

**Duration:** 2 hours

### Tasks

**9.1 Developer Guide (1 hour)**
- Document new folder structure
- Explain categorization logic
- Show how to add new tools
- Provide consolidation guidelines

**9.2 Migration Guide (0.5 hours)**
- Old path → new path reference table (470 entries)
- Import rewrite examples
- Rollback procedure
- FAQ section

**9.3 Manifest Reference (0.5 hours)**
- Manifest schema documentation
- Field descriptions
- Example entries
- Duplication rule syntax

### Deliverables

- `cortex-brain/documents/guides/toolkit-developer-guide.md` (400+ lines)
- `cortex-brain/documents/guides/toolkit-migration-guide.md` (600+ lines)
- `cortex-brain/documents/reference/toolkit-manifest-reference.md` (300+ lines)

### Acceptance Criteria

- [ ] All 3 documentation files complete
- [ ] Path migration table covers all 470 tools
- [ ] Examples tested and working
- [ ] FAQ addresses common issues

---

## 🎯 Success Criteria

Migration complete when:

1. ✅ All 470 scripts categorized and moved to organized structure
2. ✅ toolkit-manifest.yaml complete with full tool index
3. ✅ ToolkitOrchestrator implemented with search/duplication/validation
4. ✅ CLI commands working (search, info, duplicates, deprecated, validate)
5. ✅ All imports updated (zero import errors)
6. ✅ All tests passing (100% success rate)
7. ✅ Documentation complete (3 comprehensive guides)
8. ✅ Duplication hotspots identified and consolidated

---

## 📦 Deliverables Summary

**Infrastructure:**
- Organized folder structure (7 categories + 24 subcategories)
- toolkit-manifest.yaml (800+ lines)
- ToolkitOrchestrator (600+ lines)

**Migration Tools:**
- migrate_toolkit_structure.py (400+ lines)
- rewrite_imports.py (250+ lines)
- generate_toolkit_manifest.py (300+ lines)

**CLI Integration:**
- 5 new commands in cortex-cli.py
- Rich terminal output formatting

**Tests:**
- test_toolkit_orchestrator.py (400+ lines)
- test_toolkit_cli.py (200+ lines)
- 100% coverage

**Documentation:**
- toolkit-developer-guide.md (400+ lines)
- toolkit-migration-guide.md (600+ lines)
- toolkit-manifest-reference.md (300+ lines)

---

## 🔗 Integration with CORTEX v5 Refactor

**Phase Alignment:** Phase 6.6 - Toolkit Infrastructure Enhancement

**Dependencies:**
- **Upstream:** Phase 6.5 (TDD v2 Migration) must be complete
- **Downstream:** Phase 7 (Master Orchestrator Integration) will use Toolkit Orchestrator

**Cross-References:**
- **Response Template System:** Toolkit Orchestrator uses `toolkit_execution_progress` template
- **CLI Bridge:** Toolkit commands invoked via `python3 scripts/cortex-cli.py toolkit <command>`
- **Brain Protection:** HOLISTIC_DISCOVERY rule enforced by duplication detection

**Timeline Impact:** +5 days to v5 refactor (Phase 6.6 parallel to Phase 7)

---

**Author:** Asif Hussain  
**Created:** January 3, 2026  
**Status:** Planning Complete - Awaiting Execution  
**Estimated Duration:** 38 hours (~5 days)
