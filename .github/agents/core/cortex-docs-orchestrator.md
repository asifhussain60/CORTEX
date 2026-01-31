# CortexDocsOrchestrator Agent

**Version:** 1.0  
**Updated:** 2026-01-31  
**Authority:** [cortex-architect.prompt.md](../../prompts/cortex-architect.prompt.md)  
**Status:** ACTIVE (Internal Tooling Only)

---

## 🎯 Agent Identity

**Name:** CortexDocsOrchestrator Agent  
**Orchestrator:** `CortexDocsOrchestrator` (`cortex.orchestrators.internal.cortex_docs_orchestrator`)  
**Mode:** Internal — NOT MCP-Exposed  
**Purpose:** Generate and maintain HTML documentation for CORTEX repository

---

## ⚠️ INTERNAL USE ONLY

**This orchestrator is NOT for production MCP deployment:**
- ❌ **NOT MCP-exposed** — Intentionally internal tooling
- ✅ **CORTEX-specific** — Generates `docs/index.html` and subfolder indexes
- ✅ **Approved design** — Dark blue glassmorphism theme from existing documentation

**For external repository documentation, use:**
- `DocumentationOrchestrator` (production, MCP-exposed)
- `EnhancedDocumentationOrchestrator` (domain orchestrator)

---

## 🏗️ Behavior Reference

**Agent implements instructions from:**
- [cortex-architect.prompt.md](../../prompts/cortex-architect.prompt.md) — Design governance
- [CORTEX.prompt.md](../../prompts/CORTEX.prompt.md) — Production behavior

**Key Behaviors:**
- **ARCH-011:** Execute to completion (no interim reports)
- **CORE-008:** TDD (tests before implementation) — ✅ 19/19 passing
- **CORE-011:** Type hints on all methods
- **CORE-012:** Google-style docstrings

---

## 🎼 Orchestrator Capabilities

```python
from cortex.orchestrators.internal import get_cortex_docs_orchestrator

orchestrator = get_cortex_docs_orchestrator()

# Available operations:
orchestrator.execute("extract_template")      # Extract Jinja2 from docs/index.html
orchestrator.execute("generate_main")         # Generate docs/index.html
orchestrator.execute("generate_subfolders")   # Generate docs/*/index.html
orchestrator.execute("generate_all")          # Full generation cycle
orchestrator.execute("validate")              # Validate HTML5 & accessibility
```

---

## 📁 Scope

**Target Documentation:**
- `docs/index.html` — Main landing page
- `docs/01-cortex-brain/index.html` — Subfolder indexes
- `docs/02-orchestrators/index.html`
- `docs/03-getting-started/index.html`
- (All numbered documentation subfolders)

**Assets:**
- `docs/assets/css/` — Glassmorphism design system (11,532 lines)
- `docs/assets/js/` — Interactive features
- `docs/assets/images/` — Logos and icons

---

## 🎨 Design System

**Approved from `docs/index.html`:**
- **Theme:** Dark blue glassmorphism
- **Colors:** 
  - `--bg-primary: #0a0e27` (dark navy)
  - `--accent-primary: #00d4ff` (cyan)
  - `--accent-secondary: #7b61ff` (purple)
- **Features:**
  - Backdrop blur glassmorphism cards
  - Responsive navigation with breadcrumbs
  - D3.js visualizations
  - Full accessibility (ARIA, keyboard nav, 44px tap targets)

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
1. **Extract:** Parse existing `docs/index.html` → Jinja2 templates
2. **Generate:** Render templates with dynamic content (navigation, docs list)
3. **Validate:** Check HTML5 structure, accessibility, broken links

---

## 🚀 Usage Examples

### Example 1: Full Documentation Regeneration

```python
from cortex.orchestrators.internal import get_cortex_docs_orchestrator

orchestrator = get_cortex_docs_orchestrator()

# Complete regeneration
result = orchestrator.execute("generate_all")

if result.is_ok():
    report = result.value
    print(f"✅ Generated {len(report.generated_files)} files")
    print(f"   Total size: {report.total_size_bytes // 1024} KB")
    print(f"   Time: {report.generation_time_seconds:.2f}s")
```

### Example 2: Extract Templates Only

```python
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
  version: "1.0"
  orchestrator: cortex.orchestrators.internal.cortex_docs_orchestrator
  mode: internal
  mcp_exposed: false
  test_coverage: 19/19 passing
  authority: cortex-architect.prompt.md
  
capabilities:
  - extract_template
  - generate_main_index
  - generate_subfolder_indexes
  - validate_html
  - optimize_assets

governance:
  - CORE-008  # TDD
  - CORE-011  # Type hints
  - CORE-012  # Docstrings
  - ARCH-011  # Execute to completion
  
separation:
  production: DocumentationOrchestrator
  internal: CortexDocsOrchestrator
  reason: "Clear boundary between CORTEX-internal tooling and production MCP features"
```

---

**Author:** Asif Hussain  
**Date:** 2026-01-31  
**Status:** Active — Internal tooling for CORTEX documentation generation
