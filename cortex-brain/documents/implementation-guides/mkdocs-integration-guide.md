# MkDocs Integration Guide - Backend Hooks Ready

**Purpose:** Guide for future MkDocs view enhancements  
**Status:** Backend hooks prepared, view modifications deferred  
**Phase:** 1 Complete (Incremental Generation), MkDocs integration pending  
**Author:** Asif Hussain

---

## 🎯 Overview

This guide documents the backend integration points prepared for future MkDocs view enhancements. **All backend logic is implemented and production-ready.** View modifications (templates, navigation, page generation) are explicitly deferred per user request.

---

## 🔌 Available Backend Hooks

### Hook 1: Component Change Detection

**Backend Method:** `_should_regenerate_component(component_type, last_review)`

**What It Provides:** Boolean flag indicating if a component needs regeneration

**Data Structure:**
```python
{
    'component_type': str,          # 'diagrams', 'prompts', 'narratives', etc.
    'needs_regeneration': bool,     # True if changed, False if unchanged
    'reason': str,                  # 'first_run' | 'changes_detected' | 'no_changes'
    'changed_features': List[Dict], # Features that triggered regeneration
    'last_review': datetime         # Last review timestamp
}
```

**MkDocs Use Cases:**
- **Incremental Page Updates** - Regenerate only changed documentation pages
- **Navigation Updates** - Update nav.yml only for modified sections
- **Index Refreshes** - Update feature indexes incrementally
- **Cache Invalidation** - Clear page cache for changed components

**Integration Example (Future):**
```python
# In MkDocs build hook
orchestrator = EnterpriseDocumentationOrchestrator()
last_review = catalog.get_last_review_timestamp('documentation.mkdocs')

# Check which pages need update
pages_to_update = []
for page in mkdocs_pages:
    if orchestrator._should_regenerate_component(page.component_type, last_review):
        pages_to_update.append(page)

# Regenerate only changed pages
for page in pages_to_update:
    render_template(page.template, page.data)
```

---

### Hook 2: Incremental Execution Results

**Backend Method:** `execute_incremental(profile, dry_run, options)`

**What It Provides:** Detailed incremental generation report

**Data Structure:**
```python
{
    'execution_summary': {
        'mode': 'incremental',
        'profile': str,                    # 'quick' | 'standard' | 'comprehensive'
        'duration_seconds': float,
        'time_saved_percent': int,
        'full_duration_estimate': int      # What full regen would have taken
    },
    'components': {
        'regenerated': List[str],          # ['diagrams', 'prompts']
        'skipped': List[str],              # ['narratives', 'story']
        'regenerated_count': int,
        'skipped_count': int
    },
    'discovery': {
        'features_total': int,
        'features_new': int,
        'last_review_days_ago': int
    },
    'generation_results': {
        'diagrams': {...},                 # Per-component generation details
        'prompts': {...}
    },
    'mkdocs_integration_note': str         # Reminder that view mods deferred
}
```

**MkDocs Use Cases:**
- **Build Performance Dashboard** - Show time saved by incremental builds
- **Change Logs** - Display which components were updated
- **User Notifications** - Alert users to new features in updated components
- **Cache Statistics** - Show cache hit/miss rates per component

**Integration Example (Future):**
```python
# In MkDocs build script
result = orchestrator.execute_incremental(profile='standard', dry_run=False)

# Display build statistics in footer
build_stats = {
    'duration': result.data['execution_summary']['duration_seconds'],
    'time_saved': result.data['execution_summary']['time_saved_percent'],
    'components_updated': result.data['components']['regenerated_count']
}

# Render footer template with stats
render_footer_template(build_stats)
```

---

### Hook 3: Component-to-Feature-Type Mapping

**Backend Data:** Hardcoded mapping in `_should_regenerate_component()`

**Available Mappings:**
```python
{
    'diagrams': {FeatureType.ORCHESTRATOR, FeatureType.WORKFLOW},
    'prompts': {FeatureType.OPERATION, FeatureType.AGENT},
    'narratives': {FeatureType.OPERATION, FeatureType.AGENT},
    'story': {FeatureType.TEMPLATE, FeatureType.DOCUMENTATION, FeatureType.OPERATION},
    'cortex_vs_copilot': {FeatureType.INTEGRATION},
    'image_guidance': {FeatureType.DOCUMENTATION},
    'doc_integration': {FeatureType.DOCUMENTATION},
    'mkdocs': {FeatureType.DOCUMENTATION},
    'architecture': None,  # All features relevant
    'technical': {FeatureType.OPERATION, FeatureType.AGENT, FeatureType.ORCHESTRATOR},
    'getting_started': {FeatureType.WORKFLOW, FeatureType.INTEGRATION}
}
```

**MkDocs Use Cases:**
- **Smart Navigation** - Group pages by feature type
- **Filtered Views** - Show only operations/agents/workflows
- **Search Optimization** - Index pages by feature type
- **Breadcrumb Generation** - Build hierarchical navigation

**Integration Example (Future):**
```python
# In navigation builder
def build_navigation_by_feature_type():
    nav_items = {}
    
    for component, feature_types in component_feature_map.items():
        if feature_types:
            for ftype in feature_types:
                if ftype not in nav_items:
                    nav_items[ftype] = []
                nav_items[ftype].append(component)
    
    return render_nav_template(nav_items)
```

---

### Hook 4: Enhancement Catalog Queries

**Backend Methods (via EnhancementCatalog):**
- `get_features_since(since=datetime)` - Features modified after timestamp
- `get_all_features(status=AcceptanceStatus)` - All features with status filter
- `get_catalog_stats()` - Feature counts by type/status

**Data Structures:**
```python
# Feature object
{
    'id': int,
    'name': str,
    'type': str,                    # 'operation' | 'agent' | 'orchestrator' | etc.
    'description': str,
    'source': str,                  # 'git' | 'yaml' | 'codebase'
    'added_at': datetime,
    'last_updated': datetime,
    'acceptance_status': str,       # 'discovered' | 'accepted'
    'metadata': Dict                # Additional feature-specific data
}

# Catalog stats
{
    'total_features': int,
    'by_type': {
        'operation': int,
        'agent': int,
        'orchestrator': int,
        ...
    },
    'by_status': {
        'discovered': int,
        'accepted': int
    }
}
```

**MkDocs Use Cases:**
- **"What's New" Page** - Display features added since last version
- **Feature Index** - Searchable list of all CORTEX features
- **Statistics Dashboard** - Show feature growth over time
- **Feature Status Badges** - Display accepted/discovered/deprecated status

**Integration Example (Future):**
```python
# In "What's New" page generator
catalog = EnhancementCatalog()
last_major_version = get_last_major_version_date()  # e.g., v3.2.0 release date

new_features = catalog.get_features_since(since=last_major_version)

# Group by type
features_by_type = {}
for feature in new_features:
    ftype = feature['type']
    if ftype not in features_by_type:
        features_by_type[ftype] = []
    features_by_type[ftype].append(feature)

# Render template
render_whats_new_template(features_by_type, version='3.2.1')
```

---

## 📊 Data Export Formats (Prepared for Views)

### JSON Exports (Future Phase 2)

**Prepared Structure:**
```json
{
  "component_type": "diagrams",
  "last_generated": "2025-11-29T14:30:00Z",
  "features_included": [
    {
      "name": "code_review",
      "type": "operation",
      "description": "Pull request analysis",
      "usage_examples": ["code review", "review pr 1234"],
      "related_features": ["view_discovery", "tdd_workflow"]
    }
  ],
  "metadata": {
    "diagram_count": 14,
    "generation_duration_seconds": 8.5,
    "template_version": "2.0"
  }
}
```

**Export Locations (Future):**
- `cortex-brain/admin/scripts/documentation/exports/{component}_data.json`
- `docs/data/{component}_features.json` (for MkDocs consumption)

---

### Markdown Reports (Prepared)

**Prepared Structure:**
```markdown
# Component: Diagrams

**Last Generated:** 2025-11-29 14:30:00  
**Features Included:** 15 (8 operations, 4 agents, 3 workflows)

## Feature List

### Operations (8)
- **code_review** - Pull request analysis with dependency-driven crawling
  - Usage: `code review`, `review pr 1234`
  - Related: view_discovery, tdd_workflow

### Agents (4)
- **FeedbackAgent** - Structured issue reporting with privacy protection
  - Usage: `feedback bug`, `report issue`
  - Related: github_gist_upload
```

**Export Locations (Future):**
- `cortex-brain/documents/components/{component}_report.md`
- `docs/components/{component}.md` (for MkDocs inclusion)

---

## 🔧 Configuration for MkDocs (Future)

### Component-Level Review Timestamps

**Current:** Single `'documentation'` review type  
**Future Enhancement:** Component-specific review types

**Implementation (Future Phase 2):**
```python
# In _discover_features_from_catalog()
catalog.log_review(
    review_type='documentation.diagrams',  # Component-specific
    features_reviewed=len(diagrams_features),
    new_features_found=new_diagrams_count,
    notes="Diagram generation for orchestrators/workflows"
)

# Query last review
last_diagrams_review = catalog.get_last_review_timestamp('documentation.diagrams')
```

**Benefit:** Finer-grained incremental updates (regenerate diagrams but skip prompts)

---

### Profile-Based Page Filtering

**Current:** Profile parameter exists but not fully utilized  
**Future Enhancement:** Filter MkDocs pages by profile

**Implementation (Future Phase 3):**
```python
# In MkDocs build hook
profile = os.getenv('CORTEX_DOC_PROFILE', 'standard')

if profile == 'quick':
    pages_to_build = ['index', 'quick-start', 'api-reference']
elif profile == 'comprehensive':
    pages_to_build = None  # Build all pages
else:  # standard
    pages_to_build = ['index', 'quick-start', 'features', 'api-reference']

# Build only selected pages
for page in mkdocs_pages:
    if pages_to_build is None or page.name in pages_to_build:
        build_page(page)
```

**Benefit:** Faster documentation builds for CI/CD pipelines

---

## 🎯 Recommended MkDocs Enhancements (Deferred)

### Enhancement 1: Incremental Page Regeneration

**Current State:** Full site rebuild on every change  
**Desired State:** Regenerate only changed pages

**Backend Support:** ✅ Ready - `_should_regenerate_component()` provides change detection

**Implementation Steps (Future):**
1. Add MkDocs build hook to check component changes
2. Map MkDocs pages to components (e.g., `diagrams.md` → `'diagrams'` component)
3. Skip unchanged pages in build process
4. Update navigation only for changed sections

**Estimated Time:** 2-3 hours

---

### Enhancement 2: Component-Level Caching

**Current State:** No caching, full generation every time  
**Desired State:** Cache component outputs, reuse if unchanged

**Backend Support:** ✅ Ready - `execute_incremental()` reports regenerated/skipped components

**Implementation Steps (Future):**
1. Create cache directory: `docs/.cache/{component}_{hash}.html`
2. Calculate content hash for each component
3. Check cache before generation
4. Copy cached HTML if unchanged
5. Invalidate cache when component regenerates

**Estimated Time:** 1-2 hours

---

### Enhancement 3: Real-Time Build Statistics

**Current State:** No build performance visibility  
**Desired State:** Dashboard showing time saved, components updated

**Backend Support:** ✅ Ready - `execute_incremental()` returns detailed statistics

**Implementation Steps (Future):**
1. Create build statistics template: `docs/build-stats.html`
2. Inject statistics from `execute_incremental()` result
3. Display time saved percentage
4. Show regenerated/skipped components
5. Add trend chart (build times over last 30 days)

**Estimated Time:** 2-3 hours

---

### Enhancement 4: Feature Index with Search

**Current State:** No searchable feature index  
**Desired State:** Interactive feature catalog with filters

**Backend Support:** ✅ Ready - Enhancement Catalog provides all features with metadata

**Implementation Steps (Future):**
1. Query Enhancement Catalog for all features
2. Export to JSON: `docs/data/feature-index.json`
3. Create search interface with filters (type, status, source)
4. Add feature detail pages with usage examples
5. Link to related features (when Phase 2 relationships available)

**Estimated Time:** 3-4 hours

---

## 🛠️ Development Workflow (Future)

### Step 1: Detect Changes
```bash
# Backend hook (already implemented)
python -c "
from enterprise_documentation_orchestrator import EnterpriseDocumentationOrchestrator
orchestrator = EnterpriseDocumentationOrchestrator()
result = orchestrator.execute_incremental(profile='standard', dry_run=True)
print(f\"Components to regenerate: {result.data['components']['regenerated']}\")
"
```

### Step 2: Build Only Changed Pages (Future)
```bash
# MkDocs hook (to be implemented)
mkdocs build --incremental --components "diagrams,prompts"
```

### Step 3: Verify Build Statistics (Future)
```bash
# View build performance (to be implemented)
open docs/build-stats.html
```

---

## 📝 Integration Checklist (Future Implementation)

- [ ] **Incremental Page Generation**
  - [ ] Add MkDocs build hook for change detection
  - [ ] Map pages to components
  - [ ] Skip unchanged pages
  - [ ] Update navigation incrementally

- [ ] **Component-Level Caching**
  - [ ] Create cache directory structure
  - [ ] Implement content hashing
  - [ ] Add cache hit/miss logic
  - [ ] Invalidate cache on regeneration

- [ ] **Build Statistics Dashboard**
  - [ ] Create statistics template
  - [ ] Inject incremental execution results
  - [ ] Display time saved percentage
  - [ ] Add trend visualization

- [ ] **Feature Index with Search**
  - [ ] Export Enhancement Catalog to JSON
  - [ ] Create search interface
  - [ ] Add filter controls (type, status)
  - [ ] Link to feature detail pages

- [ ] **Profile-Based Builds**
  - [ ] Define page sets per profile (quick/standard/comprehensive)
  - [ ] Implement profile filtering in build hook
  - [ ] Test profile selection
  - [ ] Document profile usage

---

## ⚠️ Important Notes

**Current Scope:** Backend logic complete, view modifications deferred

**What's Ready:**
- ✅ Component change detection (`_should_regenerate_component`)
- ✅ Incremental execution workflow (`execute_incremental`)
- ✅ Enhancement Catalog queries (all methods functional)
- ✅ Data structures documented
- ✅ Integration points identified

**What's Deferred:**
- ⏸️ MkDocs template modifications
- ⏸️ Navigation.yml updates
- ⏸️ Page regeneration logic
- ⏸️ Custom CSS/JavaScript for views
- ⏸️ Build hook implementation

**Why Deferred:** User explicitly requested "defer the site modifications for later" - backend groundwork laid, view integration is separate enhancement phase

---

## 📚 Additional Resources

**Phase 1 Completion Report:** `cortex-brain/documents/reports/PHASE-1-INCREMENTAL-GENERATION-COMPLETE.md`

**Test Script:** `test_incremental_generation.py`

**Orchestrator Code:** `cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py`

**Enhancement Catalog Guide:** `cortex-brain/documents/implementation-guides/enhancement-catalog-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Version:** 1.0 (Phase 1 Complete, MkDocs Integration Prepared)  
**Date:** 2025-11-29
