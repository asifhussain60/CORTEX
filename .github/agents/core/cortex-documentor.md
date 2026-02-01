# CortexDocsOrchestrator Agent

**Version:** 3.0  
**Updated:** 2026-02-01  
**Authority:** [cortex-documentor.prompt.md](../../prompts/cortex-documentor.prompt.md)  
**Status:** ACTIVE (Internal Tooling Only)  
**New in v3.0:** 3-Tier HTML Link Integrity Auditing System

---

## 🎯 Agent Identity

**Name:** CortexDocsOrchestrator Agent  
**Orchestrator:** `CortexDocsOrchestrator` (`cortex.orchestrators.internal.cortex_docs_orchestrator`)  
**Mode:** Internal — NOT MCP-Exposed  
**Purpose:** **Advisor + Generator** for CORTEX documentation site

---

## 🧠 TWO MODES OF OPERATION

### 1. ADVISORY MODE (Consult First)
**Purpose:** Get intelligent recommendations BEFORE generating HTML

| Operation | Description |
|-----------|-------------|
| `advise_section` | Get diagram, content, and feature recommendations for L2 section |
| `advise_page` | Get page-specific recommendations for L3 detail page |
| `compare_approaches` | Compare D3.js vs SVG vs Mermaid for a visualization |
| `list_sections` | List all sections with status and advisory availability |
| `audit_documentation_links` | **NEW:** 3-tier (L1→L2→L3) HTML link integrity verification |
| `fix_broken_links` | **NEW:** Automated remediation suggestions for broken links |
| `cleanup_orphaned_files` | **NEW:** Safe removal of unreferenced documentation files |

### 2. GENERATION MODE (Execute)
**Purpose:** Generate HTML from templates and content

| Operation | Description |
|-----------|-------------|
| `extract_template` | Extract Jinja2 from docs/index.html |
| `generate_main` | Generate docs/index.html |
| `generate_subfolders` | Generate docs/*/index.html |
| `generate_l2_page` | Generate specific L2 page |
| `validate` | Validate HTML5 & accessibility |

---

## ⚠️ INTERNAL USE ONLY

**This orchestrator is NOT for production MCP deployment:**
- ❌ **NOT MCP-exposed** — Intentionally internal tooling
- ✅ **CORTEX-specific** — Generates `docs/index.html` and subfolder indexes
- ✅ **Approved design** — Dark blue glassmorphism theme from existing documentation
- ✅ **Advisory intelligence** — Suggests diagrams, content, unique features

**For external repository documentation, use:**
- `DocumentationOrchestrator` (production, MCP-exposed)
- `EnhancedDocumentationOrchestrator` (domain orchestrator)

---

## 🏗️ 3-Level Documentation Hierarchy

```
Level 1: docs/index.html                    ← Landing page (APPROVED, DO NOT MODIFY)
Level 2: docs/{section}/index.html          ← Section landing (unique per section)
Level 3: docs/{section}/{page}.html         ← Detail pages
```

**Design Principles:**
- L1: 512px logo centered, hero section, section cards
- L2: 300x300 logo left-justified, NO hero, D3.js visualization, glass cards
- L3: Breadcrumbs, sidebar navigation, full-width content

---

## 🎼 Advisory Knowledge Base

The orchestrator has built-in intelligence for these sections:

| Section | Recommended Diagrams | Unique Features |
|---------|---------------------|-----------------|
| **01-cortex-brain** | Tier Pyramid (D3-hierarchy), Brain Network (D3-force), Pipeline (SVG) | Tier rule hover cards, governance explorer |
| **02-orchestrators** | Orchestrator Network (D3-force), Request Flow (SVG), Wiring (SVG) | Category filtering, MCP badges |
| **03-getting-started** | Installation Flow (SVG-steps), Decision Tree (D3-decision) | Animated code blocks, copy-to-clipboard |
| **04-architecture** | Data Flow Sankey (D3-sankey), Interaction Matrix (D3-matrix) | Layer zoom, hover responsibilities |
| **05-lens-protocol** | LENS Pipeline (SVG), AST Tree (D3-tree), Timeline (D3-timeline) | Live code analysis demo |
| **11-mcp-tools** | Tool Graph (D3-force), API Map (SVG), Capability Radar (D3-radar) | Try-it-now playground |

---

## 🚀 Usage Examples

### Example 1: Get Advisory Before Building

```python
from cortex.orchestrators.internal import get_cortex_docs_orchestrator

orch = get_cortex_docs_orchestrator()

# Ask for recommendations before generating
result = orch.execute("advise_section", section_id="01-cortex-brain")

if result.is_ok():
    advisory = result.value
    print(f"Section: {advisory.section_title}")
    print(f"Theme: {advisory.theme_accent}")
    print(f"Effort: {advisory.effort_estimate_hours}h")
    print(f"\nRecommended Diagrams:")
    for d in advisory.recommended_diagrams:
        print(f"  - {d.name} ({d.diagram_type}): {d.description[:50]}...")
```

### Example 2: Compare Visualization Approaches

```python
# Should I use D3.js, SVG, or Mermaid for a network diagram?
result = orch.execute(
    "compare_approaches",
    visualization_type="network",
    data_complexity="high"
)

if result.is_ok():
    comparison = result.value
    print(f"Verdict: {comparison['verdict'].upper()}")
    print(f"Reason: {comparison['verdict_reason']}")
```

### Example 3: List All Sections with Status

```python
result = orch.execute("list_sections")

if result.is_ok():
    data = result.value
    for section in data["sections"]:
        status_icon = "✅" if section["status"] == "COMPLETE" else "⏳"
        print(f"{status_icon} {section['section_id']}: {section['title']}")
```

### Example 4: Full Generation (After Advisory)

```python
result = orch.execute("generate_all")

if result.is_ok():
    report = result.value
    print(f"✅ Generated {len(report.generated_files)} files")
```

### Example 5: Audit Documentation Links (3-Tier)

```python
# Comprehensive link integrity check
result = orch.execute(
    "audit_documentation_links",
    entry_point="docs/index.html",
    mode="full",  # "full", "l1-only", "l2-only", "l3-only"
    skip_external=True,  # Skip slow external URL checks
    dry_run=True  # Report only, no deletions
)

if result.is_ok():
    audit = result.value
    
    # Summary
    print(f"Links Checked: {audit['summary']['total_links_checked']}")
    print(f"P0 Broken (Navigation): {audit['summary']['broken_links_by_severity']['p0_navigation']}")
    print(f"P1 Broken (Assets): {audit['summary']['broken_links_by_severity']['p1_assets']}")
    print(f"P2 Issues (External): {audit['summary']['broken_links_by_severity']['p2_external']}")
    print(f"Circular References: {audit['summary']['circular_references']}")
    print(f"Orphaned Files: {audit['summary']['orphaned_files']}")
    
    # Detailed issues
    for phase in ["phase_1_l1", "phase_2_l2", "phase_3_l3"]:
        if phase in audit["detailed_report"]:
            print(f"\n{phase.upper()}:")
            for link in audit["detailed_report"][phase].get("broken_links", []):
                print(f"  ❌ {link['href']} → {link['issue']}")
```

### Example 6: Fix Broken Links (Automated Suggestions)

```python
# Get remediation suggestions
result = orch.execute(
    "fix_broken_links",
    audit_report=audit_result,  # From previous audit
    mode="suggest",  # "suggest" or "auto-fix"
    dry_run=True
)

if result.is_ok():
    fixes = result.value
    
    print("Suggested Fixes:")
    for fix in fixes["suggested_fixes"]:
        print(f"\nOriginal: {fix['original_link']}")
        print(f"Issue: {fix['issue']}")
        for suggestion in fix["suggestions"]:
            confidence_icon = "🟢" if suggestion['confidence'] == "high" else "🟡" if suggestion['confidence'] == "medium" else "🔴"
            print(f"  {confidence_icon} {suggestion['fix']}")
            print(f"     Reason: {suggestion['reason']}")
```

### Example 7: Cleanup Orphaned Files (Safe Archival)

```python
# Remove unreferenced documentation files
result = orch.execute(
    "cleanup_orphaned_files",
    audit_report=audit_result,  # From link audit Phase 4
    mode="archive",  # "archive" (safe) or "delete" (risky)
    confirm=False  # Require explicit approval for HIGH RISK files
)

if result.is_ok():
    cleanup = result.value
    
    print(f"Archived: {len(cleanup['archived'])} files")
    print(f"Deleted: {len(cleanup['deleted'])} files")
    print(f"Preserved: {len(cleanup['preserved'])} files")
    print(f"\nManifest: {cleanup['manifest_location']}")
    
    # Review HIGH RISK files
    for orphan in audit_result["detailed_report"]["phase_4_cleanup"]["orphans_by_category"]["html"]:
        if orphan["risk"] == "HIGH":
            print(f"⚠️ HIGH RISK: {orphan['path']} ({orphan['size']} KB)")
            print(f"   Recommended: {orphan['action']}")
```

### Example 8: Audit Responsive Design (Mobile-First)

```python
# Comprehensive responsive design audit
result = orch.execute(
    "audit_responsive_design",
    entry_point="docs/index.html",
    mode="full",  # "full", "l1-only", "l2-only", "l3-only"
    breakpoints=[320, 768, 1024, 1440],  # Mobile, tablet, desktop, wide
    include_screenshots=False  # Requires headless browser
)

if result.is_ok():
    audit = result.value
    
    # Summary
    print(f"Pages Audited: {audit['summary']['pages_audited']}")
    print(f"Pages Passed: {audit['summary']['pages_passed']} ({audit['summary']['pass_percentage']}%)")
    print(f"Critical Issues: {audit['summary']['critical_issues']}")
    
    # Detailed results
    for page in audit["pages"]:
        status_icon = "✅" if page["passed"] else "❌"
        print(f"\n{status_icon} {page['path']}")
        
        if page["has_viewport"]:
            print(f"   ✅ Viewport meta tag present")
        else:
            print(f"   ❌ CRITICAL: Missing viewport meta tag")
        
        if page["has_responsive_css"]:
            print(f"   ✅ Responsive CSS (media queries: {page['media_query_count']})")
        else:
            print(f"   ⚠️ No media queries detected")
        
        if page["issues"]:
            print(f"   Issues ({len(page['issues'])}):")
            for issue in page["issues"]:
                print(f"      - {issue}")
```

---

## 🔧 Template System

**Templates Location:** `cortex/templates/docs/`

| Template | Purpose |
|----------|---------|
| `base.html.jinja2` | Base layout with header/footer |
| `index.html.jinja2` | Main landing page structure |
| `subfolder.html.jinja2` | Subfolder index template |
| `components/header.html.jinja2` | Header component |
| `components/footer.html.jinja2` | Footer component |

**Generation Flow:**
1. **Advise:** Get recommendations for diagrams, content, features
2. **Review:** Human reviews and approves approach
3. **Extract:** Parse existing `docs/index.html` → Jinja2 templates
4. **Generate:** Render templates with dynamic content
5. **Validate:** Check HTML5 structure, accessibility
# Extract Jinja2 templates from existing HTML
result = orchestrator.execute("extract_template")

if result.is_ok():
    templates = result.value
    print(f"Templates created: {templates['templates_created']}")
```

### Example 3: Validate HTML

```python
# Validate generated HTML
result = orchestrator.execute("validate")

if result.is_ok():
    validation = result.value
    if validation["valid"]:
        print("✅ All HTML valid")
    else:
        print(f"⚠️ Issues: {validation['issues']}")
```

---

## 📊 Governance Compliance

| Rule | Status | Evidence |
|------|--------|----------|
| **CORE-008** | ✅ | 19 tests before implementation |
| **CORE-011** | ✅ | Type hints on all public methods |
| **CORE-012** | ✅ | Google-style docstrings |
| **CORE-035** | ✅ | Single canonical implementation |
| **ARCH-007** | ✅ | NOT MCP-exposed (intentional, internal) |
| **ARCH-011** | ✅ | Execute to completion (no phases) |

---

## 🧪 Test Coverage

**Location:** `tests/unit/orchestrators/internal/test_cortex_docs_orchestrator.py`  
**Status:** ✅ 19/19 tests passing

**Test Classes:**
1. `TestCortexDocsOrchestratorInitialization` — Instance, singleton, metadata
2. `TestTemplateExtraction` — Extract from HTML, component creation
3. `TestHTMLGeneration` — Main index, subfolder indexes, full generation
4. `TestNavigationBuilding` — Navigation structure, hierarchy
5. `TestValidation` — HTML5 structure, DOCTYPE, ARIA
6. `TestMCPExposure` — Confirms NOT MCP-exposed
7. `TestSubfolderMetadata` — Title extraction, breadcrumbs
8. `TestExecuteOperation` — Operation routing, error handling

---

## 🚫 Limitations

**NOT for:**
- ❌ External repository documentation
- ❌ Production MCP tool usage
- ❌ Real-time documentation generation
- ❌ Multi-tenant documentation

**Use Instead:**
- `DocumentationOrchestrator` — For production MCP documentation
- `EnhancedDocumentationOrchestrator` — For advanced doc features

---

## 🔗 Related Documentation

- **Implementation:** `cortex/orchestrators/internal/cortex_docs_orchestrator.py`
- **Tests:** `tests/unit/orchestrators/internal/test_cortex_docs_orchestrator.py`
- **README:** `cortex/orchestrators/internal/README.md`
- **Prompt:** [cortex-architect.prompt.md](../../prompts/cortex-architect.prompt.md)

---

## 📋 Agent Metadata

```yaml
agent:
  name: CortexDocsOrchestrator Agent
  version: "3.0"
  orchestrator: cortex.orchestrators.internal.cortex_docs_orchestrator
  mode: internal
  mcp_exposed: false
  test_coverage: 19/19 passing (core) + audit methods
  authority: cortex-architect.prompt.md
  
capabilities:
  # Core Operations
  - extract_template
  - generate_main_index
  - generate_subfolder_indexes
  - validate_html
  - optimize_assets
  - list_sections
  - advise_section
  - compare_approaches
  - generate_all
  # Link Integrity (v3.0)
  - audit_documentation_links
  - fix_broken_links
  - cleanup_orphaned_files
  # Responsive Design (v3.0)
  - audit_responsive_design

governance:
  - CORE-008  # TDD
  - CORE-011  # Type hints
  - CORE-012  # Docstrings
  - ARCH-011  # Execute to completion
  - DOC-013   # 3-Tier link validation mandatory
  - DOC-014   # Phase 1 L1 entry validation
  - DOC-015   # Phase 2 L2 recursive validation  
  - DOC-016   # Phase 3 L3 exhaustive validation
  - DOC-017   # Phase 4 orphan detection
  - DOC-018   # Broken link remediation
  - DOC-019   # Safe cleanup protocol
  - DOC-020   # Security link validation
  - DOC-021   # Viewport meta mandatory
  - DOC-022   # Media query verification
  - DOC-023   # Fluid typography check
  - DOC-024   # Touch target sizing
  - DOC-025   # Responsive images
  - DOC-026   # SVG/D3 responsiveness
  - DOC-027   # Container queries
  - DOC-028   # Mobile navigation
  
separation:
  production: DocumentationOrchestrator
  internal: CortexDocsOrchestrator
  reason: "Clear boundary between CORTEX-internal tooling and production MCP features"
```

---

**Author:** Asif Hussain  
**Date:** 2026-02-01  
**Version:** 3.0 — Added link auditing + responsive design audit capabilities
**Status:** Active — Internal tooling for CORTEX documentation generation
