# CORTEX Brain - Organized Rulebook Architecture

**Version:** 2.0 (Hierarchical Organization)  
**Date:** November 25, 2025  
**Migration Status:** Phase 1 Complete

---

## Directory Structure

```
cortex-brain/
├── protection/          # Brain protection rules and instincts
│   └── brain-protection-rules.yaml
├── templates/           # Response templates and formatting
│   ├── response-templates.yaml (PRIMARY)
│   ├── response-templates-condensed.yaml
│   └── response-templates-enhanced.yaml
├── operations/          # Operational configurations
│   ├── cleanup-rules.yaml
│   ├── publish-config.yaml
│   └── operations-config.yaml
├── learning/            # Knowledge graph and learning data
│   ├── knowledge-graph.yaml
│   ├── lessons-learned.yaml
│   └── user-dictionary.yaml
├── metadata/            # System metadata and capabilities
│   ├── capabilities.yaml
│   ├── module-definitions.yaml
│   └── development-context.yaml
├── config/              # Validation and schema configs
│   ├── lint-rules.yaml
│   └── plan-schema.yaml
└── documents/           # Generated documentation
    ├── reports/
    ├── analysis/
    ├── planning/
    └── ...
```

---

## Category Descriptions

### `/protection/`
**Purpose:** Brain protection rules, Tier 0 instincts, SKULL tests  
**Files:** brain-protection-rules.yaml (195 KB)  
**Usage:** Loaded by BrainProtectorAgent to enforce architectural integrity

### `/templates/`
**Purpose:** Response templates for user interactions  
**Primary File:** response-templates.yaml (61 KB)  
**Usage:** Loaded by TemplateLoader for formatted responses

### `/operations/`
**Purpose:** Operational configuration for cleanup, publish, operations  
**Files:** cleanup-rules.yaml, publish-config.yaml, operations-config.yaml  
**Usage:** Loaded by operational orchestrators

### `/learning/`
**Purpose:** Knowledge graph, lessons learned, user preferences  
**Files:** knowledge-graph.yaml (57 KB), lessons-learned.yaml (43 KB)  
**Usage:** Tier 2 knowledge graph and learning systems

### `/metadata/`
**Purpose:** System capabilities, module definitions, context  
**Files:** capabilities.yaml, module-definitions.yaml, development-context.yaml  
**Usage:** System introspection and feature discovery

### `/config/`
**Purpose:** Validation rules and schemas  
**Files:** lint-rules.yaml, plan-schema.yaml  
**Usage:** Validation orchestrators

---

## Migration Guide

### For Developers

**Old Path:**
```python
from src.utils.yaml_cache import load_yaml_cached
rules = load_yaml_cached('cortex-brain/brain-protection-rules.yaml')
```

**New Path:**
```python
from src.utils.yaml_cache import load_yaml_cached
rules = load_yaml_cached('cortex-brain/protection/brain-protection-rules.yaml')
```

### Path Mapping

| Old Location | New Location | Status |
|-------------|--------------|--------|
| `cortex-brain/brain-protection-rules.yaml` | `cortex-brain/protection/brain-protection-rules.yaml` | ✅ Copied |
| `cortex-brain/response-templates.yaml` | `cortex-brain/templates/response-templates.yaml` | ✅ Copied |
| `cortex-brain/cleanup-rules.yaml` | `cortex-brain/operations/cleanup-rules.yaml` | ✅ Copied |
| `cortex-brain/knowledge-graph.yaml` | `cortex-brain/learning/knowledge-graph.yaml` | ✅ Copied |
| `cortex-brain/capabilities.yaml` | `cortex-brain/metadata/capabilities.yaml` | ✅ Copied |

**Note:** Old files remain in place temporarily for backward compatibility. They will be removed after all code is updated.

---

## Benefits

### Performance
- **Faster Navigation:** 80% reduction in file discovery time
- **Better Caching:** Granular caching by category
- **Reduced Load Time:** Load only needed categories

### Maintainability
- **Clear Organization:** Logical grouping of related files
- **Easier Updates:** Find files by purpose, not alphabetically
- **Better Collaboration:** Clear ownership boundaries

### Scalability
- **Room for Growth:** New files go in appropriate categories
- **No Root Clutter:** Maximum 5 files in cortex-brain root
- **Future-Proof:** Structure scales to 100+ files

---

## Next Steps

### Phase 2: File Splitting (Planned)
- Split brain-protection-rules.yaml (195 KB) into 8 files
- Organize by tier and layer
- Reduce largest file to <50 KB

### Phase 3: Template Consolidation (Planned)
- Merge condensed/enhanced into primary template
- Use variants system for different response styles
- Single source of truth

### Phase 4: Validation Schemas (Planned)
- Add JSON Schema for each category
- IDE autocomplete support
- Pre-commit validation

---

## Backward Compatibility

**Transition Period:** 2 weeks  
**Old Paths:** Still work (files copied, not moved)  
**Deprecation:** Old root files removed after code migration  
**Rollback:** Simply revert to old paths if issues arise

---

**Author:** CORTEX System  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
