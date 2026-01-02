# Migration Analysis: Existing Tools

**Document:** Context - Migration & Cleanup Analysis  
**Created:** December 31, 2025  
**Author:** Asif Hussain

---

## 📊 Current Tool Inventory Summary

| Category | Tool Count | Status |
|----------|------------|--------|
| Brain Operations | 4 | Active |
| Operations | 3 | Active |
| Planning | 3 | Active |
| Analytics | 4 | Active |
| Documentation | 7 | Active |
| Testing | 3 | Active |
| Migration | 2 | Active |
| Maintenance | 6 | **Review Needed** |
| Generators | 5 | Active |
| Utilities | 6 | Active |
| **Total** | **43** | Mixed |

---

## 🔴 Redundancy Analysis

### Group 1: Cleanup Tools (HIGH OVERLAP)

```
├── core/brain/cleanup.py           → Brain-specific cleanup
├── maintenance/cleanup_temp_files.py → Temp file removal
├── maintenance/clear_caches.py     → Cache clearing
├── maintenance/full_cleanup.py     → Orchestrates all above
└── maintenance/remove_legacy_refs.py → Legacy reference removal
```

**Overlap Score:** 85%

**Issue:** 5 tools doing variations of "cleanup"

**Consolidation Strategy:**
```yaml
# Unified cleanup tool
cleanup:
  modes:
    brain:     # From cleanup.py
    temp:      # From cleanup_temp_files.py
    cache:     # From clear_caches.py
    legacy:    # From remove_legacy_refs.py
    full:      # From full_cleanup.py (orchestrates all)
```

**Migration Path:**
| Old Tool | New Command | Status |
|----------|-------------|--------|
| `cleanup.py` | `cortex-cleanup --mode=brain` | Deprecated |
| `cleanup_temp_files.py` | `cortex-cleanup --mode=temp` | Deprecated |
| `clear_caches.py` | `cortex-cleanup --mode=cache` | Deprecated |
| `remove_legacy_refs.py` | `cortex-cleanup --mode=legacy` | Deprecated |
| `full_cleanup.py` | `cortex-cleanup --mode=full` | Primary |

---

### Group 2: Validation Tools (MODERATE OVERLAP)

```
├── testing/validate_deployment.py    → Deployment integrity
├── maintenance/validate_templates.py → Template validation
├── validate_templates.py (root)      → DUPLICATE!
└── testing/verify_no_mocks.py        → Test verification
```

**Overlap Score:** 45%

**Issue:** `validate_templates.py` exists in two locations

**Consolidation Strategy:**
- Remove root-level duplicate
- Keep specialized validators separate (different domains)

---

### Group 3: Schema/Generation Tools (MODERATE OVERLAP)

```
├── core/generators/schema_extractor.py      → Extract schemas from C#
├── core/generators/openapi_generator_v4.py  → Generate OpenAPI specs
├── core/generators/legacy_spec_generator.py → Legacy C# → OpenAPI
├── core/generators/schema_registry.py       → Schema deduplication
└── core/generators/narrative_validator.py   → Validate spec quality
```

**Overlap Score:** 60%

**Issue:** Schema extraction and OpenAPI generation could be unified

**Consolidation Strategy:**
```yaml
schema-tools:
  subcommands:
    extract:   # From schema_extractor.py
    generate:  # From openapi_generator_v4.py
    legacy:    # From legacy_spec_generator.py
    validate:  # From narrative_validator.py
  registry: schema_registry.py  # Keep separate (different purpose)
```

---

### Group 4: Documentation Tools (LOW OVERLAP)

```
├── documentation/generate_docs_from_code.py
├── documentation/generate_quick_reference.py
├── documentation/generate_sitemap.py
├── documentation/regenerate_prompts.py
├── html-tools/generator.py
├── html-tools/validator.py
└── documentation/docgen_discovery.py
```

**Overlap Score:** 20%

**Recommendation:** Keep separate - complementary functions

---

## 🟡 Duplicate Detection

### Exact Duplicates Found

| File 1 | File 2 | Action |
|--------|--------|--------|
| `cortex-toolkit/validate_templates.py` | `cortex-toolkit/maintenance/validate_templates.py` | Remove root copy |

### Near-Duplicates (Similar Code)

| Tool 1 | Tool 2 | Similarity | Action |
|--------|--------|------------|--------|
| `progress_bar.py` | Functions in `full_cleanup.py` | 70% | Extract to shared |
| `version_detector.py` | `version_manager.py` | 55% | Review for merge |

---

## 📦 Proposed Tool Inventory Structure

### Why Enhanced Manifest Benefits

| Current (`toolkit-manifest.yaml`) | Proposed (`tool-inventory.yaml`) |
|-----------------------------------|----------------------------------|
| Lists tools by category | Adds semantic capabilities |
| Basic metadata only | Rich metadata (lifecycle, deps) |
| No overlap detection | `conflicts_with` field |
| No deprecation tracking | `lifecycle` field |
| Manual discovery | Auto-discoverable by RequestAnalyzer |

### Enhanced Manifest Fields

```yaml
tools:
  - id: cleanup                    # Unique identifier
    name: "Unified Cleanup Tool"   # Human-friendly name
    version: "2.0.0"               # Semantic version
    category: maintenance
    
    # NEW: Lifecycle tracking
    lifecycle: active              # active|beta|deprecated|removed
    deprecated_date: null
    removal_date: null
    replacement: null
    
    # NEW: Semantic capabilities for RequestAnalyzer
    capabilities:
      - cleanup
      - cache-management
      - temp-file-removal
      - maintenance
    
    # NEW: Natural language descriptions
    can_do:
      - "clean up temporary files"
      - "clear VS Code cache"
      - "remove Python bytecode"
      - "cleanup obsolete artifacts"
    
    # NEW: Conflict detection
    conflicts_with:
      - full-maintenance          # Cannot run simultaneously
    
    # NEW: Explicit dependencies
    depends_on: []
    
    # NEW: What this replaces (migration tracking)
    replaces:
      - cleanup.py
      - cleanup_temp_files.py
      - clear_caches.py
    
    # NEW: Execution characteristics
    execution:
      idempotent: true
      destructive: true
      rollback_supported: true
      requires_confirmation: true
      average_duration_seconds: 30
```

---

## 🎯 Migration Phases

### Phase 8.1: Audit (Day 1 - Morning)
1. Run `ToolAuditor.audit_all_tools()`
2. Generate overlap report
3. Identify exact duplicates
4. Map tool dependencies

### Phase 8.2: Consolidate (Day 1 - Afternoon)
1. Create unified `cleanup` tool
2. Migrate cleanup subcommands
3. Update manifest entries
4. Add deprecation notices

### Phase 8.3: Inventory (Day 2 - Morning)
1. Generate `tool-inventory.yaml`
2. Add capability keywords to all tools
3. Define lifecycle for each tool
4. Create dependency graph

### Phase 8.4: Governance (Day 2 - Afternoon)
1. Write governance documentation
2. Define tool creation rules
3. Define deprecation process
4. Archive legacy tools

---

## 📊 Expected Outcomes

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Tools | 43 | ~35 | -19% |
| Cleanup Tools | 5 | 1 | -80% |
| Duplicates | 2 | 0 | -100% |
| With Capabilities | 0 | 35 | +100% |
| With Lifecycle | 0 | 35 | +100% |

---

## 🔗 Related Documents
- [Master Plan](../00-master-plan.md)
- [Current Architecture](./current-architecture.md)
- [Gap Analysis](./gap-analysis.md)
