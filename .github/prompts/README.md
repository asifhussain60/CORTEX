# CORTEX Prompts

**Updated:** 2026-02-23

---

## 📁 Directory Structure

### Root Directory — Main Prompts

| File | Status | Size | Purpose |
|------|--------|------|---------|
| `cortex-architect.prompt.md` | ✅ ACTIVE | ~700 lines | Senior AI architect for IMPLEMENT/FIX/REFACTOR/AUDIT |
| `CORTEX.prompt.md` | ✅ ACTIVE | ~200 lines | Master orchestrator for all request routing |
| `cortex-doc.prompt.md` | ✅ ACTIVE | ~1,370 lines | Documentation orchestration (discovery → generation → build) |
| `MCP-ORCHESTRATOR-MAPPING.md` | ✅ ACTIVE | ~300 lines | Orchestrator → MCP tool mapping for SaaS/external repos |
| `MCP-SETUP-GUIDE.md` | ✅ ACTIVE | ~120 lines | Pylance-style MCP setup (stdio, auto-starts) |
| `README.md` | — | — | This file |

### `reference/` — Supporting Documentation

| File | Purpose |
|------|---------|
| `chat01-lessons-learned.yaml` | Phase 54 cortex-refactor — ghost dir removal, audit alignment |
| `chat03-lessons-learned.yaml` | Chat session lessons learned — tolerance bands, config auto-loading |
| `phase-0-5-dashboard.md` | Phase 0-5 dashboard reference |

### `../.github/templates/` — Response Templates

| File | Purpose |
|------|---------|
| `cortex-response-templates.md` | **SSOT** for all response formatting — templates, blocks, rendering rules, personality |
| `chat-vs-terminal-guide.md` | Chat vs Terminal output guide |

---

## 🎯 Usage

### For Active Development

Use prompts from root directory (all `.prompt.md` files).

### For Reference

Check `reference/` for operational documentation.

---

## 📊 Optimization Results

| File | Before | After | Reduction |
|------|--------|-------|-----------|
| cortex-architect | 7,580 lines | 580 lines | **92%** |
| CORTEX | 1,019 lines | 350 lines | **66%** |
| **Total** | **8,599 lines** | **930 lines** | **89%** |
| **Tokens** | **~32K** | **~3.5K** | **89%** |

---

## 🔄 Adding New Prompts

1. Create in root directory as `.prompt.md`
2. Add to this README
3. Old versions → archived with version suffix
4. Mark old versions as reference-only

---

## 🔗 Related

- **Orchestration:** `.github/agents/orchestration/`
- **Governance:** `cortex-registry/core/`
- **Planning:** `cortex-registry/planning/`
- **Templates:** `.github/templates/`
