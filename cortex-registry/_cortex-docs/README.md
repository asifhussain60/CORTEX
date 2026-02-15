# CORTEX Documentation System

**Version:** 1.0 | **Created:** 2026-02-15 | **Authority:** Documentation Pipeline Architecture

---

## 🎯 Purpose

**Standalone documentation generation system for CORTEX with:**
- Multi-role content (Business Leaders, Product Owners, Software Developers)
- Build-time extraction pipeline (JAMstack pattern)
- Verbosity-preservation architecture
- SPA rendering (Astro framework)

**Key Principle:** Documentation system is ISOLATED from CORTEX core runtime. CORTEX tools may be leveraged for discovery/analysis, but the documentation pipeline operates independently.

---

## 📁 Structure

```
cortex-registry/_cortex-docs/
├── README.md                    # This file
├── phase-plan.yaml              # 5-phase implementation roadmap
│
├── content/                     # Generated documentation content
│   ├── architecture/            # Architecture guides (800-2000 words)
│   ├── capabilities/            # Feature documentation (800-1500 words)
│   ├── business-guides/         # BLUF guides for CTOs (1200-1500 words)
│   ├── tutorials/               # Step-by-step guides (1000-1800 words)
│   └── reference/               # API/tool reference (400-800 words)
│
├── templates/                   # Multi-role content templates
│   ├── business-leader.yaml     # BLUF template (decision-focused)
│   ├── product-owner.yaml       # Analogy-rich template
│   ├── developer.yaml           # Technical depth template
│   └── diagram-standards.yaml   # Mermaid/D3.js rules
│
├── pipeline/                    # Build-time extraction scripts
│   ├── discover.py              # LENS + git analysis
│   ├── extract.py               # MD → JSON converter
│   ├── validate.py              # Link/metric/quality checks
│   └── build.py                 # SPA build orchestration
│
├── site/                        # Astro SPA framework
│   ├── src/
│   │   ├── pages/               # Route-based rendering
│   │   ├── components/          # Diagram renderers
│   │   ├── layouts/             # Page templates
│   │   └── lib/                 # Content API
│   ├── public/
│   │   └── data/                # Extracted JSON (build artifacts)
│   └── astro.config.mjs
│
└── discovery/                   # Analysis workspace (temporary)
    ├── baseline.yaml            # Git + LENS analysis output
    └── curation-config.yaml     # Manual review decisions
```

---

## 🔄 Workflow

### Discovery Cycle (Automated)
```
LENS Analysis + Git History → YAML Baseline → Manual Review Gate
```

### Content Generation (Hybrid)
```
Templates + Baseline → Rich MD Content → Verbosity Validation → Commit
```

### Build Pipeline (Automated)
```
MD Source → Extract Metadata → Generate JSON → Astro Build → Static Site
```

---

## 📐 Governance

| Rule | Requirement |
|------|-------------|
| **Separation** | NO imports from cortex/ (use MCP tools only) |
| **File Naming** | kebab-case, no SCREAMING_CASE |
| **Word Counts** | Business: 1200-1500, PO: 800-1500, Dev: 800-2000 |
| **Voice** | Third-person neutral professional |
| **Claims** | Evidence-backed or qualified language only |
| **Diagrams** | Mermaid-first (text-based, git-friendly) |

---

## 🚀 Implementation

**See:** [phase-plan.yaml](phase-plan.yaml) for 5-phase roadmap (18 stages, 47 tasks)

**Execution:** Each phase uses CORTEX tools (cortex_lens_analyze, cortex_git_history) for discovery but generates documentation artifacts in this isolated structure.

---

## 🔗 Integration Points

**CORTEX Tools Used (via MCP):**
- `cortex_lens_analyze` → Code intelligence discovery
- `cortex_git_history` → Development timeline extraction
- `cortex_detect_duplicates` → Content deduplication

**No Direct Imports:** Documentation system does NOT import from cortex/ package. Tool invocation only.

---

**Status:** Phase 1 ready for execution  
**Next:** Run discovery cycle to generate baseline.yaml
