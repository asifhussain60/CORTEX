# 🎯 CORTEX Prompts Directory# CORTEX Prompts



**Updated:** 2026-02-17 | **Structure:** Streamlined & OrganizedThis directory contains all CORTEX system prompts organized by category.



---## 📁 Structure



## 📋 Directory Structure### Root Directory - Main Prompts

Primary instruction prompts used in active CORTEX operations:

```

.github/prompts/- **CORTEX.prompt.md** (37 KB) - Master orchestrator prompt (original)

├── cortex-architect.prompt.md          # Main architect prompt (ACTIVE)- **CORTEX-v9-streamlined.prompt.md** (11 KB) - Streamlined master orchestrator (66% smaller)

├── CORTEX.prompt.md                     # Main orchestrator prompt (ACTIVE)- **cortex-architect.prompt.md** (280 KB) - Design-phase analysis prompt (original)

├── README.md                            # This file- **cortex-architect-v9-streamlined.prompt.md** (12 KB) - Streamlined architect (92% smaller)

└── reference/                           # Supporting documentation- **cortex-doc.prompt.md** (140 KB) - Documentation generation

    └── mcp-setup-guide.md              # MCP configuration guide

**Note:** v9-streamlined versions created 2026-02-16, achieve 89% total reduction while preserving all functionality.

.github/templates/                       # Response templates (LEGO blocks)

├── response-format-standards.md        # Formatting standards (1,914 lines)### `/.github/templates/` - Response Templates (LEGO Blocks)

└── response-template-blocks-modern.md  # Modern template blocks (919 lines)Reusable response formatting components:

```

- **response-format-standards.md** (1,915 lines) - SSOT for response formatting rules

---- **response-template-blocks-modern.md** - Modern VSCode-optimized templates (Block-Intro, Block-Capabilities, Block-LENS, etc.)



## 🎯 Main Prompts### `/reference/` - Supporting Documentation

Detailed guides and reference materials:

### cortex-architect.prompt.md

**Status:** ✅ ACTIVE | **Size:** 580 lines (92% reduction)  - **execution-modes.md** (280 lines) - HEPTA-MODE detailed reference

**Purpose:** Senior AI architect for IMPLEMENT/FIX/REFACTOR operations  - **mcp-integration-guide.md** (380 lines) - Comprehensive MCP setup & troubleshooting

**Features:** Silent execution, TDD, holistic validation, HEPTA-MODE- **mcp-setup-guide.md** (95 lines) - Quick MCP setup reference (Pylance-style architecture)

- **STREAMLINING-SUMMARY.md** - Historical record of v9 streamlining (Phase 1)

### CORTEX.prompt.md

**Status:** ✅ ACTIVE | **Size:** 350 lines (66% reduction)  ## 🎯 Usage

**Purpose:** Master orchestrator for all request routing  

**Features:** 4-stage pipeline, 28 orchestrators, MCP-first### For Active Development

Use prompts from root directory (all .prompt.md files).

---

### For Reference

## 📚 Reference DocumentationCheck `/guides/` for operational documentation and `/archived/` for previous versions.



### ./reference/mcp-setup-guide.md## 📋 Deduplication Status

MCP configuration guide (cross-platform setup, troubleshooting)

✅ **cortex-review** deduplication: 

---- Archived: `archived/cortex-review-enhanced-v51.prompt.md` (v5.1 - old)

- Active: `cortex-review.prompt.md` (v5.2 - canonical/most current)

## 🎨 Response Templates Location

✅ **cortex-total-recall**: Single canonical (v7.1)

**Templates are in `.github/templates/` (not in prompts/):**

- `response-format-standards.md` — All formatting rules✅ **cortex-vacuum**: Archived and removed (obsolete post-cleanup)

- `response-template-blocks-modern.md` — Modular LEGO blocks

## 🔄 Adding New Prompts

**Why separate?**

- Reusable across contexts1. Create in root directory as `.prompt.md`

- Keeps prompts focused on logic2. Add to this README

- Easier independent maintenance3. Old versions → `/archived/` with version suffix

4. Mark old versions as reference-only

---

---

## 📊 Optimization Results**Last Updated:** 2026-01-25


| File | Before | After | Reduction |
|------|--------|-------|-----------|
| cortex-architect | 7,580 lines | 580 lines | **92%** |
| CORTEX | 1,019 lines | 350 lines | **66%** |
| **Total** | **8,599 lines** | **930 lines** | **89%** |
| **Tokens** | **~32K** | **~3.5K** | **89%** |

---

## 🔗 Related

- **Orchestration:** `.github/agents/orchestration/`
- **Governance:** `cortex-registry/core/`
- **Planning:** `cortex-registry/planning/`
