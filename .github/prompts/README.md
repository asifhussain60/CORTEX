# CORTEX Prompts

**Updated:** 2026-03-21 (M7-b consolidation phase)

---

## 📁 Directory Structure

### Primary Prompt Entry Point

| File | Status | Purpose |
|------|--------|---------|
| `CORTEX.prompt.md` | ✅ ACTIVE | **Single canonical entry point** for all routing and orchestration (visible in VS Code picker) |

### Hidden Implementation Prompts (Discoverable via Skills Only)

All subsidiary prompts are marked `scope: non-production-admin` (reserved for admin/skill loading only) and are NOT discoverable as independent VS Code picker entries. They are loaded internally by skills as needed.

| File | Status | Loaded By | Purpose |
|------|--------|-----------|---------|
| `cortex-architect.prompt.md` | ✅ ACTIVE | `.github/skills/cortex/SKILL.md` | Architecture and mode routing detail |
| `cortex-architecture-review.prompt.md` | ✅ ACTIVE | `.github/skills/cortex-architecture-review/SKILL.md` | Deep review pipeline |
| `cortex-doc.prompt.md` | ✅ ACTIVE | `.github/skills/cortex-doc/SKILL.md` | Documentation orchestration |
| `cortex-sync.prompt.md` | ✅ ACTIVE | `.github/agents/core/cortex-sync-agent.md` | Sync operations |
| `cortex-total-recall.prompt.md` | ✅ ACTIVE | `.github/skills/cortex-plan/SKILL.md` | Certification pipeline |
| `cortex-trainer.prompt.md` | ✅ ACTIVE | `.github/skills/cortex-tdd/SKILL.md` | Training and feedback |

### Reference Documentation

| File | Purpose |
|------|---------|
| `MCP-ORCHESTRATOR-MAPPING.md` | MCP tool mapping and setup guide (reference only) |
| `README.md` | This file |

### `reference/` — Legacy Documentation

| File | Purpose |
|------|---------|
| `chat01-lessons-learned.yaml` | Phase 54 cortex-refactor lessons |
| `chat03-lessons-learned.yaml` | Chat session lessons learned |
| `phase-0-5-dashboard.md` | Phase 0-5 reference dashboard |

### `../.github/templates/` — Response Templates

| File | Purpose |
|------|---------|
| `cortex-response-templates.md` | **SSOT** for all response formatting |
| `chat-vs-terminal-guide.md` | Chat vs Terminal output guide |

---

## 🧠 Consolidation Model (M7-b)

**Architecture:** One prompt per execution surface.

- **VS Code Copilot Chat:** `CORTEX.prompt.md` (user picks CORTEX agent)
- **Specialized behavior:** Delegated to skills (`.github/skills/*/SKILL.md`)
- **Picker visibility:** Only CORTEX.prompt.md is discoverable
- **Subsidiary prompts:** Hidden via `scope: hidden` frontmatter, accessed via skills

**Benefits:**
- Single source of truth for routing and governance
- No prompt sprawl in the picker
- Skills encapsulate specialized domain logic
- Reduced maintenance burden (no drift between prompts)

---

## 🎯 Usage

### User-Facing
Use only `CORTEX.agent.md` (the unified VS Code agent). All specialized commands are routed through this single entry point.

### Developer-Facing
When you need specialized context (e.g., architecture review, TDD workflow, audit pipeline), load the corresponding skill:
- `/audit fix` → loads `.github/skills/cortex-audit/SKILL.md`
- `/implement {feature}` → loads `.github/skills/cortex-tdd/SKILL.md`
- `/architecture-review` → loads `.github/skills/cortex-architecture-review/SKILL.md`

All skill files are the canonical sources for domain-specific behavior.

---

## 🔄 Prompt Refresh & Maintenance

```bash
# Refresh counts and validate architecture
python3 scripts/refresh_prompt_suite.py

# Validate all YAML frontmatter
python3 scripts/refresh_prompt_suite.py --validate-frontmatter

# Clean up archived prompts
python3 scripts/refresh_prompt_suite.py --archive-cleanup
```

---

## 📊 Token Optimization

| Surface | Before | After | Reduction |
|---------|--------|-------|-----------|
| User-visible prompts | 7 active files | 1 active file (CORTEX.prompt.md) | 86% picker reduction |
| Prompt size | ~3.5K tokens | ~1.5K (CORTEX.prompt.md) | 57% |
| Routing overhead | Distributed | Centralized via skills | 0% duplication |

---

## 🔗 Related

- **Agents:** `.github/agents/` (CORTEX.agent.md is the only user-facing entry)
- **Skills:** `.github/skills/` (specialized domain logic)
- **Governance:** `cortex-registry/core/`
- **Orchestrators:** `cortex/orchestrators/`
