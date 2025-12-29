# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant with long-term memory, context awareness, and strategic planning  
**Version:** 4.0.0 | **Author:** Asif Hussain

---

## 🎯 Entry Point

**Primary:** Load `.github/prompts/CORTEX.prompt.md` for all intent routing.

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 🔀 Intent Routing

All command routing is defined in `CORTEX.prompt.md`. Key orchestrators:

| Intent Pattern | Route To |
|----------------|----------|
| `plan`, `create a plan`, `make a plan` | Planning System → folder with 4 subfolders |
| `tdd`, `start tdd`, `run tests` | TDD Orchestrator → RED→GREEN→REFACTOR |
| `ado`, `ado story`, `ado feature` | ADO Operations → work items |
| `sanitize`, `make generic` | Sanitization → 5-phase cleanup |
| `maintenance`, `health check` | Maintenance → 6-phase pipeline |
| `refine`, `improve` | Refinement → 7-phase improvement |

**Manifest Location:** `cortex-brain/manifests/orchestrators/`

---

## 📋 Response Format

Defer to `CORTEX.prompt.md` for full spec. Summary:

- **Header:** Always include `## 🧠 CORTEX {Title}` + author line
- **Body:** Scales with complexity (INSTANT → COMPREHENSIVE)
- **Next Steps:** EXACTLY ONE action OR completion message
- **Completion:** Use `# 🎉 CONGRATULATIONS` when all work done

---

## 🛡️ Brain Protection (SKULL)

| Rule | Action |
|------|--------|
| TDD_ENFORCEMENT | Tests must fail before implementation |
| HOLISTIC_DISCOVERY | Search before create (prevent duplication) |
| GIT_ISOLATION | CORTEX code never commits to user repos |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs  
**✅ REQUIRED:** `cortex-brain/documents/{category}/`

Categories: `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

```
cortex-brain/           # Long-term memory (4-tier brain)
├── tier0/ (Governance) 
├── tier1/ (Working memory)
├── tier2/ (Knowledge graph)
├── tier3/ (Dev context)
└── manifests/orchestrators/

src/                    # Implementation
├── cortex_agents/      # 2 specialist agents
├── orchestrators/      # 8 workflow orchestrators
└── response_templates/ # Template rendering
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Intent router (source of truth) |
| `.github/prompts/cortex-maintenance.prompt.md` | 6-phase maintenance |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules |
| `cortex-brain/response-templates-v4.yaml` | Response templates |
| `cortex-brain/manifests/orchestrators/` | All orchestrator manifests |

---

## 🚀 Quick Start

Say `help` in Copilot Chat to see all operations.

**For maintenance:** Use `system maintenance` to run 6-phase health pipeline.

---

**Anti-Bloat:** This file MUST stay under 150 lines. All details defer to CORTEX.prompt.md.
