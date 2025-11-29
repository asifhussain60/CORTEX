# CORTEX Documentation System (Admin)

This folder contains the single, consolidated source of truth for all documentation-related configuration and generators.

- **config/** — YAML configs for pages, diagrams, validation, and source mapping
- **generators/** — 5 extensible documentation generators (see below)
- **templates/** — Templates used by generators (reserved for future use)
- **collectors/** — Data collectors (reserved for future use)

## Component Registry

**Location:** `src/operations/documentation_component_registry.py`

The registry manages 5 documentation components with dependency resolution:

### 1. Diagrams Generator
- **ID:** `diagrams`
- **Generator:** `DiagramsGenerator`
- **Output:** Mermaid diagram files (`.mmd`) in `docs/diagrams/`
- **Purpose:** Generate architecture, workflow, and system design diagrams
- **Natural Language:** "generate diagrams", "create diagrams", "regenerate diagrams"
- **Dependencies:** None

### 2. Feature List Generator
- **ID:** `feature_list`
- **Generator:** `FeatureListGenerator`
- **Output:** `docs/FEATURES.md`
- **Purpose:** Extract and document system capabilities, modules, and operations
- **Natural Language:** "generate feature list", "document features", "list capabilities"
- **Dependencies:** None
- **Data Sources:** 
  - `cortex-operations.yaml` (operations)
  - `cortex-brain/module-definitions.yaml` (modules)
  - `cortex-brain/capabilities.yaml` (capabilities)

### 3. MkDocs Site Generator
- **ID:** `mkdocs`
- **Generator:** `MkDocsGenerator`
- **Output:** `mkdocs.yml` + structured markdown pages in `docs/`
- **Purpose:** Generate complete static site configuration with navigation
- **Natural Language:** "generate mkdocs", "create documentation site", "build docs"
- **Dependencies:** None

### 4. Executive Summary Generator ✨ NEW
- **ID:** `executive_summary`
- **Generator:** `ExecutiveSummaryGenerator`
- **Output:** `docs/EXECUTIVE-SUMMARY.md`
- **Purpose:** High-level project overview with status, metrics, and architecture
- **Natural Language:** "executive summary", "generate summary", "project summary"
- **Dependencies:** None
- **Data Sources:**
  - `cortex.config.json` (project info)
  - `cortex-brain/capabilities.yaml` (capabilities)
  - `cortex-brain/TRUTH-SOURCES.yaml` (status)
  - Health reports (metrics)
- **Content:** Mission, architecture (4 tiers + agents), capabilities, status, metrics, milestones

### 5. Publish Documentation ✨ NEW
- **ID:** `publish`
- **Generator:** `PublishDocsGenerator`
- **Output:** Built site in `site/` directory, optionally deployed to GitHub Pages
- **Purpose:** Build MkDocs static site and deploy to GitHub Pages
- **Natural Language:** "publish to github pages", "deploy docs", "publish documentation"
- **Dependencies:** `mkdocs` (must run first)
- **Requires:** `mkdocs` command installed (`pip install mkdocs`)
- **Modes:**
  - **Dry-run:** `metadata={"deploy": False}` — builds but doesn't deploy
  - **Deploy:** `metadata={"deploy": True}` — builds and pushes to `gh-pages` branch
- **Workflow:**
  1. Validate `mkdocs.yml` configuration
  2. Run `mkdocs build` → generates `site/`
  3. Validate build output (checks for `index.html`)
  4. (Optional) Deploy via `mkdocs gh-deploy`

## Usage

### Programmatic (Python)

```python
from pathlib import Path
from src.operations.documentation_component_registry import create_default_registry

registry = create_default_registry(Path.cwd())

# Execute single component
result = registry.execute("executive_summary", output_path=Path("docs"))

# Execute multiple components (respects dependencies)
results = registry.execute_pipeline(
    ["diagrams", "feature_list", "mkdocs", "executive_summary"],
    output_path=Path("docs"),
    profile="standard"
)

# Execute publish with deployment
publish_result = registry.execute(
    "publish",
    metadata={"deploy": True}  # Dry-run: set to False
)
```

### Via Natural Language

Use natural language triggers in conversation:
- "generate diagrams"
- "generate executive summary"
- "publish to github pages"
- "generate all documentation"

### Via Orchestrator

```python
from src.operations.enterprise_documentation_orchestrator import execute_enterprise_documentation

# Full pipeline
execute_enterprise_documentation()

# Component-specific
execute_enterprise_documentation(stage="diagrams")  # diagrams only
execute_enterprise_documentation(stage="mkdocs")    # mkdocs only
execute_enterprise_documentation(stage="all")       # all components
```

## Component Architecture

Each generator:
- Extends `BaseDocumentationGenerator` (in `generators/base_generator.py`)
- Implements `generate()`, `collect_data()`, `validate()` methods
- Supports multiple generation profiles (minimal, standard, comprehensive)
- Tracks generated files, errors, warnings, and execution time
- Returns `GenerationResult` with success status and metadata

## Testing

Test suite validates:
- **Registry:** `tests/test_documentation_registry.py` (6 tests)
- **Structure:** `tests/test_documentation_structure_paths.py` (3 tests)
- **End-to-End:** `tests/test_documentation_e2e.py` (7 tests)

**Total:** 15 passing tests + 1 skipped (full deployment test)

Run tests:
```bash
pytest tests/test_documentation*.py -v
```

## Migration Notes

✅ **Migration Complete** — Legacy `cortex-brain/doc-generation-config/` removed  
✅ **Cleanup Complete** — Legacy root-level `DOCUMENTATION-GENERATION-*.md` files removed  
✅ **Tests Passing** — 15/16 tests passing (1 skipped: requires live deployment)

All generators now use `admin/documentation/config/` as primary source.