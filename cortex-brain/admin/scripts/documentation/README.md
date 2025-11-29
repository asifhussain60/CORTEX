# CORTEX Enterprise Documentation Orchestrator

**⚠️ ADMIN-ONLY FEATURE - NOT PACKAGED FOR PRODUCTION**

## Overview

This is the **SINGLE ENTRY POINT** for ALL CORTEX documentation generation.

**Location:** `cortex-brain/admin/scripts/documentation/`  
**Status:** Phase 2 COMPLETE  
**Packaging:** Excluded from production (see `scripts/publish_cortex.py`)

## What It Generates

1. **14+ Mermaid Diagrams** (`docs/diagrams/mermaid/`)
2. **10+ DALL-E Prompts** (`docs/diagrams/prompts/`)  
   - Sophisticated image generation prompts
   - Designed for ChatGPT's DALL-E capabilities
3. **14+ Narratives** (`docs/narratives/`)  
   - High-level explanations of images (1:1 with prompts)
4. **"The Awakening of CORTEX" Story** (`docs/narratives/THE-AWAKENING-OF-CORTEX.md`)  
   - Hilarious technical narrative
   - Features "Asif Codenstein", Copilot, and his wife
5. **Executive Summary** (`docs/EXECUTIVE-SUMMARY.md`)  
   - Lists ALL discovered features
6. **Complete MkDocs Site** (`docs/diagrams/mkdocs.yml` + `docs/diagrams/docs/`)  
   - Material theme with dark mode
   - Mermaid diagram support
   - Full navigation

**Total Files:** 45+ files generated fresh on every run

## How It Works

### Phase 1: Discovery Engine
Automatically discovers features from:
- Git history (last 2 days)
- YAML configuration files (`capabilities.yaml`, `operations-config.yaml`)
- Codebase scanning (modules, agents)

### Phase 2: Generation Pipeline
Generates all documentation components:
- Mermaid diagrams with technical architecture
- DALL-E prompts with sophisticated visual descriptions
- Narratives explaining what the images show
- Story documentation with humor and technical depth
- Executive summary with complete feature list
- MkDocs configuration and site structure

## Usage

### Command Line

```bash
# From repository root
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py

# With options
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py --dry-run
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py --profile comprehensive
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py --component diagrams
```

### Natural Language (via CORTEX)

```
generate documentation
generate cortex docs
update documentation
refresh docs
```

CORTEX automatically routes these commands to the orchestrator.

### Programmatic

```python
from cortex_brain.admin.scripts.documentation.enterprise_documentation_orchestrator import execute_enterprise_documentation

result = execute_enterprise_documentation(
    workspace_root=Path("/path/to/CORTEX"),
    profile="standard",
    dry_run=False
)

print(f"Generated {result.data['execution_summary']['total_files_generated']} files")
```

## Output Structure

```
docs/
├── diagrams/
│   ├── mermaid/
│   │   ├── 01-tier-architecture.mmd
│   │   ├── 02-agent-coordination.mmd
│   │   └── ... (14 total)
│   ├── prompts/
│   │   ├── 01-tier-architecture-prompt.md
│   │   ├── 02-agent-coordination-prompt.md
│   │   └── ... (14 total)
│   ├── mkdocs.yml
│   └── docs/
│       └── index.md
├── narratives/
│   ├── 01-tier-architecture-narrative.md
│   ├── 02-agent-coordination-narrative.md
│   ├── THE-AWAKENING-OF-CORTEX.md
│   └── ... (14+ total)
└── EXECUTIVE-SUMMARY.md
```

## Production Packaging

**This orchestrator is NOT included in production packages.**

### Verification

```bash
# Run publish script
python scripts/publish_cortex.py

# Check that cortex-brain/admin is excluded
ls publish/CORTEX/cortex-brain/  # Should NOT show 'admin/' folder
```

### Exclusion Configuration

See `scripts/publish_cortex.py` line 172:
```python
EXCLUDED_DIRS = {
    'cortex-brain/admin',  # ⭐ ADMIN-ONLY: Documentation orchestrator
    ...
}
```

## Deprecated Generators

The following generators are **DEPRECATED** and will be removed in v4.0:

1. **`src/operations/modules/epmo/documentation_generator.py`**  
   - Old EPM documentation generator
   - Added deprecation warning in Phase 2

2. **`src/plugins/story_generator_plugin.py`**  
   - Old story generator plugin
   - Added deprecation warning in Phase 2

**Migration:** All functionality consolidated into Enterprise Documentation Orchestrator.

## Validation

### Check No Other Entry Points

```bash
# Search for documentation generators
grep -r "class.*DocumentationGenerator" src/
grep -r "def generate.*documentation" src/operations/
```

**Expected:** Only deprecated generators with warnings.

### Test Documentation Generation

```bash
# Dry run (preview only)
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py --dry-run

# Full generation
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py

# Verify output
ls docs/diagrams/mermaid/  # Should have 14 .mmd files
ls docs/diagrams/prompts/  # Should have 14 .md files
ls docs/narratives/  # Should have 14+ .md files including THE-AWAKENING-OF-CORTEX.md
cat docs/EXECUTIVE-SUMMARY.md  # Should list all features
```

### Test MkDocs Site

```bash
cd docs/diagrams
mkdocs serve

# Visit http://localhost:8000
# Verify navigation, diagrams, story all render correctly
```

## Architecture Highlights

### Discovery Engine
- **Git History Scanning:** Analyzes recent commits for new features
- **YAML Parsing:** Extracts capabilities from configuration files
- **Codebase Analysis:** Discovers operation modules and agents
- **Feature Merging:** Deduplicates and consolidates feature list

### DALL-E Prompt Design
- **Sophisticated Visual Language:** Uses technical terminology for precision
- **Narrative Parity:** Each prompt has corresponding narrative explanation
- **Blueprint Style:** Professional, technical aesthetic with color coding
- **Component Placement:** Precise positioning and relationship arrows

### Story Generation
- **Hilarious Narrative:** Technical documentation as comedy
- **8 Chapters:** From "The Amnesia Problem" to "Transformation Complete"
- **Real Features:** Every scenario described is implemented
- **Character Development:** "Asif Codenstein", Copilot's awakening, wife's commentary

## Next Steps

After running the orchestrator:

1. **Review Generated Files** - Verify all 45+ files created correctly
2. **Test MkDocs Site** - Run `mkdocs serve` and check rendering
3. **Generate DALL-E Images** - Use prompts in `docs/diagrams/prompts/`
4. **Commit to Git** - Commit generated documentation to repository
5. **Verify Production Package** - Ensure admin folder excluded from publish

## Design Decisions

### Why Admin-Only?

- **Security:** File system writes, Git operations
- **Complexity:** Unnecessary for end users
- **Package Size:** Reduces production deployment size
- **Maintenance:** Easier to update without affecting user deployments

### Why Single Entry Point?

- **Consolidation:** All doc generation in one place
- **Consistency:** Uniform discovery and generation approach
- **Maintenance:** Easier to update and extend
- **Testing:** Single codepath to validate

### Why Discovery Engine?

- **Freshness:** Documentation stays current with codebase
- **Automation:** No manual feature inventory maintenance
- **Completeness:** Automatically finds new features from Git/YAML/code

## Files

- **`enterprise_documentation_orchestrator.py`** - Main orchestrator (1000+ lines)
- **`README.md`** - This file

## Status

✅ **Phase 2 COMPLETE**  
- Discovery Engine implemented
- All 6 generators complete (diagrams, prompts, narratives, story, executive, MkDocs)
- Deprecation warnings added to old generators
- Production packaging exclusions verified
- Documentation complete

## Support

For issues or questions about documentation generation:
1. Check this README
2. Review `cortex-brain/documents/planning/SINGLE-DOCUMENTATION-ORCHESTRATOR-PLAN.md`
3. Review conversation history in `.github/CopilotChats/docgen.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - ADMIN-ONLY  
**Last Updated:** 2025-11-19
