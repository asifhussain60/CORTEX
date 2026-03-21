# Archived Prompts — Phase M7-b Consolidation

**Date:** 2026-03-21 | **Consolidation:** Prompt sprawl elimination

---

## Why These Prompts Are Here

All prompts in this directory were consolidated into **unified CORTEX.prompt.md** during Consolidation Phase M7-b. They are preserved for reference and historical purposes, but are NO LONGER used in production.

---

## Migration Guide

| Archived Prompt | Use Case | Replacement |
|---|---|---|
| `cortex-architect.prompt.md` | Architecture routing detail | Load `.github/skills/cortex-tdd/SKILL.md` or `.github/skills/cortex-audit/SKILL.md` |
| `cortex-architecture-review.prompt.md` | Deep architecture review | Load `.github/skills/cortex-architecture-review/SKILL.md` |
| `cortex-doc.prompt.md` | Documentation orchestration | (Integrated into doc agents directly) |
| `cortex-sync.prompt.md` | Sync operations | `.github/agents/core/cortex-sync-agent.md` |
| `cortex-total-recall.prompt.md` | Production certification | Load `.github/skills/cortex-plan/SKILL.md` |
| `cortex-trainer.prompt.md` | Training and feedback | (Integrated into trainer agents directly) |

---

## Unified Routing

All routing now happens through:
- **Entry Point:** `CORTEX.agent.md` (only user-facing picker entry)
- **System Prompt:** `CORTEX.prompt.md` (master orchestration)
- **Specialized Behavior:** `.github/skills/*/SKILL.md` (skill-provided context)

---

## Accessing Archived Prompts

These files are marked `scope: non-production-admin` and exist for:
- **Reference:** Understanding prior design decisions
- **Debugging:** Comparing historical vs current routing
- **Governance:** Tracking architectural evolution

Do NOT use these prompts directly for new work. Always route through CORTEX.agent.md.

---

## Archive Status

| File | Status | Reason |
|---|---|---|
| `cortex-architect.prompt.md` | ✅ Preserved | Production-detail reference |
| `cortex-architecture-review.prompt.md` | ✅ Preserved | Skill detail reference |
| `cortex-doc.prompt.md` | ✅ Preserved | Documentation reference |
| `cortex-sync.prompt.md` | ✅ Preserved | Sync reference |
| `cortex-total-recall.prompt.md` | ✅ Preserved | Certification reference |
| `cortex-trainer.prompt.md` | ✅ Preserved | Training reference |

**These files are NOT deleted — they remain as versioned history.**
