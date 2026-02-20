# CORTEX Prompts

**Version:** 11.0 | **Updated:** 2026-02-20 | **Post-Refactor:** v2.0.0-cohesive-brain

---

## 📁 Directory Structure

### Root Directory — Main Prompts

| File | Status | Size | Purpose |
|------|--------|------|---------|
| `cortex-architect.prompt.md` | ✅ ACTIVE | 580 lines | Senior AI architect for IMPLEMENT/FIX/REFACTOR |
| `cortex.prompt.md` | ✅ ACTIVE | 350 lines | Master orchestrator for all request routing |
| `README.md` | — | — | This file |

### `reference/` — Supporting Documentation

| File | Purpose |
|------|---------|
| `mcp-setup-guide.md` | Quick MCP setup reference (Pylance-style architecture) |
| `execution-modes.md` | HEPTA-MODE detailed reference |
| `mcp-integration-guide.md` | Comprehensive MCP setup & troubleshooting |

### `../.github/templates/` — Response Templates

| File | Purpose |
|------|---------|
| `cortex-response-templates.md` | **SSOT** for all response formatting — templates, blocks, rendering rules, personality |
| `chat-vs-terminal-guide.md` | Chat vs Terminal output guide |
| `chat-vs-terminal-quick-ref.md` | Quick reference for chat/terminal decisions |

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
