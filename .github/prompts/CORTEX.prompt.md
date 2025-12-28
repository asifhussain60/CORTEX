# 🎯 CORTEX Universal Entry Point

**Version:** 4.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Website:** https://asifhussain60.github.io/CORTEX/  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## ⚠️ Parse User Request FIRST

Remove meta-directives before intent classification:
- `Follow instructions in...` → REMOVE
- `Use *.prompt.md...` → REMOVE  
- `Reference file:///...` → REMOVE

---

## 🔀 Intent Router

| Command | Orchestrator | Manifest | Output |
|---------|--------------|----------|--------|
| `plan [x]`, `create a plan`, `make a plan` | Planning System | `planning-system-4.0-manifest.yaml` | `planning/active/{NAME}/` + 4 subfolders |
| `start tdd`, `run tests`, `tdd [x]` | TDD Mastery | `tdd-orchestrator-v4-manifest.yaml` | Tests in `tests/` |
| `plan ado`, `ado story`, `ado feature` | ADO Operations | `ado-planning-manifest.yaml` | ADO work items |
| `sanitize`, `make generic`, `anonymize` | Sanitization | `code-sanitization-manifest.yaml` | Sanitized codebase |
| `refine`, `improve cortex` | Refinement | `refinement-orchestrator-manifest.yaml` | 7-phase improvement |
| `system maintenance` | Maintenance | Via `cortex-maintenance.prompt.md` | Health reports |
| `align`, `optimize`, `cleanup`, `healthcheck` | System Ops | CLI wrappers in `scripts/` | Operation output |
| `help` | Help | Template-based | Command list |

**Manifest Path:** `cortex-brain/manifests/orchestrators/{manifest-file}`

### Planning System Output Structure

All plans MUST create:
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md    # Main plan
├── context/             # Context artifacts
├── reports/             # Progress reports
├── artifacts/           # Supporting files
└── tracking/            # progress-tracker.json
```

---

## 📋 Response Format (v4.0)

**Header (ALWAYS):**
```markdown
## 🧠 CORTEX {Title}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
```

**Body (Adaptive):**

| Tier | Tokens | Structure |
|------|--------|-----------|
| INSTANT | <50 | `{answer}` |
| FOCUSED | 50-200 | `{explanation}` + `**Next:**` |
| STRUCTURED | 200-600 | `**Context:**` + `**Changes:**` + `**Next:**` |
| COMPREHENSIVE | 600+ | Multiple `### {Sections}` |

**Next Steps:** EXACTLY ONE action OR `✅ All work complete!`

**Completion (when ALL work done):**
```markdown
# 🎉 CONGRATULATIONS
## 🧠 CORTEX {Operation}
...
✅ **All work complete!** No further action required.
```

---

## 🛡️ Brain Protection (SKULL)

| Rule | Enforcement |
|------|-------------|
| **TDD_ENFORCEMENT** | RED→GREEN→REFACTOR mandatory |
| **HOLISTIC_DISCOVERY** | Search before create (prevent duplication) |
| **REFACTOR_CLEANUP** | Remove orphaned/duplicate code |
| **GIT_ISOLATION** | CORTEX code never in user repos |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{category}/`

Categories: `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

```
cortex-brain/                    src/
├── tier0/ (Governance)          ├── tier0-3/ (Brain tiers)
├── tier1/ (Working memory)      ├── cortex_agents/ (2 agents)
├── tier2/ (Knowledge graph)     ├── orchestrators/ (8 workflows)
├── tier3/ (Dev context)         └── response_templates/
└── manifests/orchestrators/
```

---

## 📋 Quick Reference

| Command | Description |
|---------|-------------|
| `plan [feature]` | Create planning folder with TDD |
| `start tdd` | RED→GREEN→REFACTOR workflow |
| `system maintenance` | 6-phase health pipeline |
| `sanitize [dir]` | Remove company data |
| `refine` | 7-phase system improvement |
| `align` / `optimize` | System operations |
| `help` | Show all commands |

---

## 📚 Resources

- **Learning:** `cortex-brain/documents/learning-paths/`
- **Templates:** `cortex-brain/response-templates-v4.yaml`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Maintenance:** `.github/prompts/cortex-maintenance.prompt.md`

---

**Quick Start:** Say `help` to see all operations.

**Anti-Bloat:** This file MUST stay under 200 lines.
