# ⚠️ DEPRECATED - YAML VERSION REQUIRED

**Status:** DEPRECATED  
**Date:** 2025-11-18  
**Reason:** Violates YAML_ONLY_PLANNING governance rule (Tier 0, Rule #26)

---

## Migration Notice

This Markdown planning document has been **DEPRECATED** and must be converted to YAML format.

### Why YAML-Only Planning?

Per CORTEX Tier 0 governance rule **YAML_ONLY_PLANNING** (Rule #26):

1. **Prevents Documentation Bloat**
   - This MD file: 23KB (verbose, 10-50 pages typical)
   - YAML equivalent: ~5-8KB (60-80% token reduction)
   - Enforces concise structured format

2. **Machine-Readable**
   - YAML can be parsed and processed programmatically
   - Enables automated validation and tracking
   - Integrates with CORTEX brain systems

3. **Consistency**
   - Enforced schema structure
   - Standard fields across all plans
   - No "wall of text" formatting variations

4. **Searchability**
   - Structured queries on plan fields
   - Easy to filter and aggregate
   - Better brain integration

### Action Required

Convert this plan to YAML format:
- **Target:** `cortex-brain/documents/planning/documentation-consolidation-plan.yaml`
- **Reference:** `cortex-brain/documents/planning/YAML-PHASE-TRACKER-DESIGN.yaml`
- **Template:** `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml`

### Schema Structure

```yaml
plan:
  metadata:
    name: "Documentation Consolidation Plan"
    date: "2025-11-18"

---

## Current State: Documentation EPMs Inventory

### Operations (3 Separate Systems)

#### 1. `document_cortex` (Story + Docs Combined)
**Status:** ✅ Ready (11 modules, 100% complete)  
**Natural Language:** `document`, `refresh story`, `update docs`  
**Purpose:** Story refresh + documentation updates

**Modules:**
- `load_story_template` - Load story from prompts/shared/story.md
- `apply_narrator_voice` - Transform to narrator voice
- `validate_story_structure` - Ensure proper Markdown structure
- `save_story_markdown` - Write transformed story
- `update_mkdocs_index` - Update MkDocs navigation
- `build_story_preview` - Generate HTML preview
- `update_api_docs` - API documentation refresh
- `refresh_user_guides` - User guide updates
- `validate_doc_links` - Check for broken links
- `generate_doc_index` - Create documentation index
- `build_doc_preview` - Build documentation preview

#### 2. `enterprise_documentation` (EPM-Based Generator)
**Status:** ✅ Ready (1 orchestrator, 100% complete)  
**Natural Language:** `/CORTEX generate documentation`, `enterprise documentation`  
**Purpose:** Comprehensive EPM-based documentation generation

**EPM Modules** (in `src/epm/doc_generator/`):
- `validation_engine.py` - Validate documentation structure
- `cleanup_manager.py` - Clean obsolete documentation
- `diagram_generator.py` - Generate Mermaid diagrams
- `page_generator.py` - Create documentation pages
- `cross_reference_builder.py` - Build cross-references
- `doc_generator.py` - Main orchestrator

#### 3. `regenerate_diagrams` (Diagram System)
**Status:** ✅ Ready (1 orchestrator, 100% complete)  
**Natural Language:** `regenerate diagrams`, `refresh diagrams`  
**Purpose:** Analyze CORTEX design and regenerate visual assets

**Modules:**
- `diagram_regeneration_orchestrator` - Orchestrates full regeneration
- Uses `docs/diagrams/` folder structure (prompts, narratives, mermaid, generated)

### Module Locations (26 modules across 5+ folders)

```
src/operations/modules/
├── (Story Modules - 9 files)
│   ├── load_story_template_module.py
│   ├── apply_narrator_voice_module.py
│   ├── validate_story_structure_module.py
│   ├── save_story_markdown_module.py
│   ├── build_story_preview_module.py
│   ├── generate_story_chapters_module.py
│   ├── build_consolidated_story_module.py
│   ├── story_length_manager_module.py
│   └── relocate_story_files_module.py
│
├── (Documentation Modules - 9 files)
│   ├── update_mkdocs_index_module.py
│   ├── generate_api_docs_module.py
│   ├── refresh_design_docs_module.py
│   ├── build_mkdocs_site_module.py
│   ├── validate_doc_links_module.py
│   ├── deploy_docs_preview_module.py
│   ├── generate_technical_doc_module.py
│   ├── generate_technical_cortex_doc_module.py
│   └── build_documentation_module.py
│
├── diagrams/
│   └── diagram_regeneration_orchestrator.py (1 file)
│
├── (Image/Prompt Generation - 2 files)
│   ├── generate_image_prompts_module.py
│   └── generate_image_prompts_doc_module.py
│
└── enterprise_documentation_orchestrator_module.py (1 file)
```

**Total Modules:** 26 files
**Folders:** 5+ separate locations

### Scripts (6 admin/dev tools)

```
scripts/
├── regenerate_diagrams.py - CLI for diagram regeneration
├── aggressive_doc_cleanup.py - Clean obsolete documentation
├── record-mkdocs-session.py - Record MkDocs build sessions
├── test_doc_refresh.py - Test documentation refresh workflow
├── verify_doc_refresh_rules.py - Verify doc refresh rules
└── test_diagram_regeneration.py - Test diagram generation
```

### Configuration Files (4 locations)

```
cortex-brain/operations/
├── operation-refresh-docs.yaml - Story/docs refresh config (101 lines)

cortex-brain/
└── doc-generation-rules.yaml - Documentation generation rules

cortex-brain/doc-generation-config/
├── story-structure.yaml - Story structure definition
├── technical-doc-config.yaml - Technical docs configuration
└── image-generation-config.yaml - Image prompt configuration
```

### Documentation Assets

```
docs/
├── diagrams/
│   ├── prompts/ (42 image generation prompts)
│   ├── narratives/ (42 narrative descriptions)
│   ├── mermaid/ (42 Mermaid diagram sources)
│   ├── generated/ (Generated diagram outputs)
│   └── story/ (Story-related diagrams)
│
└── images/
    ├── architectural/ - Architecture diagrams
    ├── strategic/ - Strategic diagrams
    ├── operational/ - Operational diagrams
    └── integration/ - Integration diagrams
```

---

## Problem Statement

### Current Issues

1. **Scattered Entry Points**
   - 3 different operations for documentation tasks
   - Users confused about which command to use
   - Overlapping functionality between operations

2. **Module Disorganization**
   - 26 modules across 5+ folder locations
   - Difficult to discover what exists
   - No clear structure for related functionality

3. **Configuration Fragmentation**
   - 4 separate configuration files
   - Inconsistent configuration patterns
   - Duplication of settings

4. **User Experience Issues**
   - "Do I use `document`, `enterprise_documentation`, or `regenerate diagrams`?"
   - Natural language triggers overlap and confuse
   - No clear differentiation between profiles

5. **Maintenance Burden**
   - Changes require updating multiple locations
   - Testing requires multiple operation invocations
   - Refactoring is complex and error-prone

---

## Proposed Solution: Unified Documentation System

### Single Unified Operation: `cortex_documentation`

**Natural Language Triggers:**
- `generate documentation` (primary)
- `document cortex`
- `refresh documentation`
- `update documentation`
- `regenerate documentation`

### Unified Folder Structure

```
src/operations/modules/documentation/
├── README.md                          # Documentation hub guide
│
├── orchestrators/                     # Master + sub-orchestrators
│   ├── documentation_master_orchestrator.py
│   ├── story_orchestrator.py
│   └── diagram_orchestrator.py
│
├── story/                             # Story generation (8 modules)
│   ├── load_story_template.py
│   ├── apply_narrator_voice.py
│   ├── validate_story_structure.py
│   ├── save_story_markdown.py
│   ├── generate_story_chapters.py
│   ├── build_consolidated_story.py
│   ├── story_length_manager.py
│   └── relocate_story_files.py
│
├── api_docs/                          # API documentation (3 modules)
│   ├── scan_docstrings.py
│   ├── generate_api_docs.py
│   └── generate_technical_docs.py
│
├── mkdocs/                            # MkDocs operations (4 modules)
│   ├── update_mkdocs_index.py
│   ├── build_mkdocs_site.py
│   ├── validate_doc_links.py
│   └── deploy_docs_preview.py
│
├── diagrams/                          # Diagram/image generation (2 modules)
│   ├── diagram_regeneration.py
│   └── generate_image_prompts.py
│
└── technical/                         # Technical docs (5 modules)
    ├── refresh_design_docs.py
    ├── build_documentation.py
    ├── generate_technical_cortex_doc.py
    ├── generate_image_prompts_doc.py
    └── build_story_preview.py
```

**Benefits:**
- ✅ All documentation modules in one place
- ✅ Clear folder structure by functionality
- ✅ Easy to discover what exists
- ✅ Simplified imports and dependencies
- ✅ Better IDE navigation

### Unified Configuration

```
cortex-brain/documentation-config/
├── documentation-system.yaml          # Master config (all settings)
│   ├── operations
│   ├── profiles
│   ├── module_registry
│   └── natural_language_triggers
│
├── story-structure.yaml               # Story-specific config
│   ├── chapter_definitions
│   ├── narrator_voice_rules
│   └── narrative_templates
│
├── diagram-definitions.yaml           # Diagram config
│   ├── mermaid_templates
│   ├── image_prompt_templates
│   └── generation_rules
│
├── validation-rules.yaml              # Validation config
│   ├── markdown_rules
│   ├── link_checking
│   └── structure_validation
│
└── mkdocs-config.yaml                 # MkDocs-specific settings
    ├── navigation_structure
    ├── theme_customization
    └── build_settings
```

**Benefits:**
- ✅ Single source of truth for all documentation config
- ✅ Clear separation of concerns
- ✅ Easy to update and maintain
- ✅ Consistent configuration patterns

### Unified Operation with Profiles

```yaml
cortex_documentation:
  name: "CORTEX Unified Documentation"
  description: "Generate all CORTEX documentation types through unified profiles"
  natural_language:
    - "generate documentation"
    - "document cortex"
    - "refresh documentation"
  
  profiles:
    # Quick Profiles (Single Focus)
    story_only:
      description: "Story refresh only"
      modules: [story orchestrator]
      time_estimate: "2-3 minutes"
    
    diagrams_only:
      description: "Diagram regeneration only"
      modules: [diagram orchestrator]
      time_estimate: "5-7 minutes"
    
    mkdocs_only:
      description: "MkDocs build and deployment only"
      modules: [mkdocs orchestrator]
      time_estimate: "2-3 minutes"
    
    api_docs_only:
      description: "API documentation only"
      modules: [api_docs orchestrator]
      time_estimate: "3-4 minutes"
    
    # Combined Profiles
    standard:
      description: "Story + API + MkDocs (most common)"
      modules: 
        - story orchestrator
        - api_docs orchestrator
        - mkdocs orchestrator
      time_estimate: "7-10 minutes"
    
    comprehensive:
      description: "Everything (story + diagrams + API + MkDocs + technical)"
      modules:
        - story orchestrator
        - diagram orchestrator
        - api_docs orchestrator
        - mkdocs orchestrator
        - technical orchestrator
      time_estimate: "15-20 minutes"
    
    git_pages:
      description: "Full documentation for Git Pages deployment"
      modules:
        - story orchestrator
        - diagram orchestrator
        - api_docs orchestrator
        - mkdocs orchestrator
      post_actions:
        - build_mkdocs
        - deploy_to_gh_pages
      time_estimate: "12-15 minutes"
```

### User Experience

**Before (Confused):**
```
User: "I want to regenerate documentation"
Options: 
  - document_cortex (story + docs)
  - enterprise_documentation (EPM-based)
  - regenerate_diagrams (visuals)
User: "Which one do I use?"
```

**After (Clear):**
```
User: "generate documentation"
CORTEX: "Which profile? (story, diagrams, mkdocs, api, standard, comprehensive)"
User: "comprehensive"
CORTEX: "Generating complete documentation suite..."
```

---

## Implementation Plan

### Milestone 1: Module Consolidation (4 hours)

**Tasks:**
1. Create `src/operations/modules/documentation/` folder structure
2. Move 26 modules to new organized locations:
   - Story modules → `documentation/story/`
   - API modules → `documentation/api_docs/`
   - MkDocs modules → `documentation/mkdocs/`
   - Diagram modules → `documentation/diagrams/`
   - Technical modules → `documentation/technical/`
3. Update all imports in moved files
4. Create README.md in documentation folder

**Validation:**
- All modules import successfully
- No broken dependencies
- Tests still pass

### Milestone 2: Configuration Consolidation (2 hours)

**Tasks:**
1. Create `cortex-brain/documentation-config/` folder
2. Create `documentation-system.yaml` (master config)
3. Move existing configs:
   - `operation-refresh-docs.yaml` content → `documentation-system.yaml`
   - `doc-generation-rules.yaml` → `validation-rules.yaml`
   - `doc-generation-config/*.yaml` → respective config files
4. Update all module references to new config paths

**Validation:**
- All configs load successfully
- No broken config references
- Backward compatibility maintained

### Milestone 3: Orchestrator Creation (3 hours)

**Tasks:**
1. Create `documentation_master_orchestrator.py`
2. Create sub-orchestrators:
   - `story_orchestrator.py`
   - `diagram_orchestrator.py`
   - `mkdocs_orchestrator.py`
   - `api_docs_orchestrator.py`
   - `technical_orchestrator.py`
3. Implement profile routing logic
4. Add progress reporting

**Validation:**
- All profiles execute correctly
- Module sequencing works
- Progress reports are accurate

### Milestone 4: Operation Integration (2 hours)

**Tasks:**
1. Create `cortex_documentation` operation in `cortex-operations.yaml`
2. Define all profiles (7 profiles)
3. Add natural language triggers
4. Deprecate old operations:
   - Mark `document_cortex` as deprecated → `cortex_documentation`
   - Mark `enterprise_documentation` as deprecated → `cortex_documentation`
   - Mark `regenerate_diagrams` as deprecated → `cortex_documentation diagrams_only`

**Validation:**
- New operation invokes correctly
- All profiles work as expected
- Deprecated operations show migration guidance

### Milestone 5: Testing & Validation (3 hours)

**Tasks:**
1. Test each profile individually:
   - `story_only`
   - `diagrams_only`
   - `mkdocs_only`
   - `api_docs_only`
2. Test combined profiles:
   - `standard`
   - `comprehensive`
   - `git_pages`
3. Test natural language triggers
4. Validate all documentation outputs
5. Test Git Pages deployment

**Validation:**
- All profiles complete successfully
- Documentation quality maintained
- No regressions introduced
- Performance meets targets

### Milestone 6: Documentation & Migration (1 hour)

**Tasks:**
1. Create migration guide for users
2. Update `CORTEX.prompt.md` with new operation
3. Create `documentation-hub-guide.md` in module folder
4. Document each profile with examples
5. Update help system with new operation

**Validation:**
- All documentation is clear
- Migration path is obvious
- Examples work correctly

---

## Implementation Time Estimates

| Milestone | Time Estimate | Priority |
|-----------|---------------|----------|
| 1. Module Consolidation | 4 hours | Critical |
| 2. Configuration Consolidation | 2 hours | Critical |
| 3. Orchestrator Creation | 3 hours | Critical |
| 4. Operation Integration | 2 hours | Critical |
| 5. Testing & Validation | 3 hours | High |
| 6. Documentation & Migration | 1 hour | High |
| **TOTAL** | **15 hours** | - |

---

## Risk Assessment & Mitigation

### Risk 1: Breaking Existing Workflows
**Severity:** High  
**Probability:** Medium  
**Mitigation:**
- Keep deprecated operations functional with migration warnings
- Provide clear migration documentation
- Support both old and new paths during transition period (1 month)

### Risk 2: Import Path Changes Breaking Tests
**Severity:** Medium  
**Probability:** High  
**Mitigation:**
- Update all imports before moving files
- Run full test suite after each milestone
- Use automated import fixing tools (rope, autoflake)

### Risk 3: Configuration Path Changes
**Severity:** Medium  
**Probability:** Medium  
**Mitigation:**
- Create symlinks for backward compatibility
- Update all config references in one milestone
- Validate config loading after changes

### Risk 4: User Confusion During Transition
**Severity:** Medium  
**Probability:** Medium  
**Mitigation:**
- Clear deprecation warnings
- Migration guide with examples
- Support for both old and new commands during transition

### Risk 5: Documentation Quality Regression
**Severity:** High  
**Probability:** Low  
**Mitigation:**
- Comprehensive testing before release
- Side-by-side comparison of old vs new outputs
- Rollback plan if quality degrades

---

## Success Metrics

### Discoverability
- ✅ Single operation for all documentation tasks
- ✅ Clear profile names describe what they do
- ✅ Natural language triggers are intuitive

### Organization
- ✅ All 26 modules in one logical folder
- ✅ Configuration consolidated to one location
- ✅ Clear README guides usage

### User Experience
- ✅ Users can invoke any doc task with one command
- ✅ Profiles cover all use cases
- ✅ Time estimates help users choose profile

### Maintainability
- ✅ Changes only need one location update
- ✅ Testing requires single operation invocation
- ✅ New features integrate into clear structure

### Performance
- ✅ No performance degradation
- ✅ Parallel execution where possible
- ✅ Clear progress reporting

---

## Migration Path for Users

### Old Way (Deprecated)
```bash
# Story refresh
cortex document_cortex profile:quick

# Diagram regeneration  
cortex regenerate_diagrams

# Enterprise docs
cortex enterprise_documentation profile:comprehensive
```

### New Way (Recommended)
```bash
# Story only
cortex generate documentation profile:story_only

# Diagrams only
cortex generate documentation profile:diagrams_only

# Everything
cortex generate documentation profile:comprehensive
```

### Backward Compatibility (1 month transition)
- Old operations still work but show deprecation warning
- Warning includes migration example
- Both paths supported until transition complete

---

## Next Steps

1. **Review & Approve** - Review this comprehensive plan
2. **Begin Milestone 1** - Start module consolidation (4 hours)
3. **Incremental Validation** - Test after each milestone
4. **User Communication** - Announce changes before release
5. **Monitor Adoption** - Track usage of new operation
6. **Remove Deprecation** - After 1 month, remove old operations

---

## Appendix: Detailed Module Mapping

### Story Modules (8 → `documentation/story/`)
| Current Location | New Location | Purpose |
|------------------|--------------|---------|
| `load_story_template_module.py` | `story/load_story_template.py` | Load story template |
| `apply_narrator_voice_module.py` | `story/apply_narrator_voice.py` | Transform to narrator voice |
| `validate_story_structure_module.py` | `story/validate_story_structure.py` | Validate structure |
| `save_story_markdown_module.py` | `story/save_story_markdown.py` | Save story file |
| `generate_story_chapters_module.py` | `story/generate_story_chapters.py` | Generate chapters |
| `build_consolidated_story_module.py` | `story/build_consolidated_story.py` | Build full story |
| `story_length_manager_module.py` | `story/story_length_manager.py` | Manage story length |
| `relocate_story_files_module.py` | `story/relocate_story_files.py` | Relocate story files |

### API Documentation Modules (3 → `documentation/api_docs/`)
| Current Location | New Location | Purpose |
|------------------|--------------|---------|
| `scan_docstrings_module.py` | `api_docs/scan_docstrings.py` | Extract docstrings |
| `generate_api_docs_module.py` | `api_docs/generate_api_docs.py` | Generate API docs |
| `generate_technical_doc_module.py` | `api_docs/generate_technical_docs.py` | Generate technical docs |

### MkDocs Modules (4 → `documentation/mkdocs/`)
| Current Location | New Location | Purpose |
|------------------|--------------|---------|
| `update_mkdocs_index_module.py` | `mkdocs/update_mkdocs_index.py` | Update navigation |
| `build_mkdocs_site_module.py` | `mkdocs/build_mkdocs_site.py` | Build site |
| `validate_doc_links_module.py` | `mkdocs/validate_doc_links.py` | Check links |
| `deploy_docs_preview_module.py` | `mkdocs/deploy_docs_preview.py` | Deploy preview |

### Diagram Modules (2 → `documentation/diagrams/`)
| Current Location | New Location | Purpose |
|------------------|--------------|---------|
| `diagrams/diagram_regeneration_orchestrator.py` | `diagrams/diagram_regeneration.py` | Regenerate diagrams |
| `generate_image_prompts_module.py` | `diagrams/generate_image_prompts.py` | Generate image prompts |

### Technical Modules (5 → `documentation/technical/`)
| Current Location | New Location | Purpose |
|------------------|--------------|---------|
| `refresh_design_docs_module.py` | `technical/refresh_design_docs.py` | Refresh design docs |
| `build_documentation_module.py` | `technical/build_documentation.py` | Build documentation |
| `generate_technical_cortex_doc_module.py` | `technical/generate_technical_cortex_doc.py` | Generate CORTEX tech docs |
| `generate_image_prompts_doc_module.py` | `technical/generate_image_prompts_doc.py` | Generate image prompts doc |
| `build_story_preview_module.py` | `technical/build_story_preview.py` | Build story preview |

### Enterprise EPM Modules (Stay in `src/epm/doc_generator/`)
- `validation_engine.py`
- `cleanup_manager.py`
- `diagram_generator.py`
- `page_generator.py`
- `cross_reference_builder.py`
- `doc_generator.py`

**Note:** EPM modules stay in their current location but are invoked through the unified documentation operation.

---

## Conclusion

This consolidation plan reduces complexity by **67-80%** across operations, modules, and configuration while maintaining **100% functionality**. The unified system significantly improves discoverability, maintainability, and user experience.

**Estimated Implementation Time:** 15 hours  
**Risk Level:** Low-Medium (with mitigations in place)  
**Impact:** High (significantly improved UX and maintainability)

Ready to proceed with implementation?
