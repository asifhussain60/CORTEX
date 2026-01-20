# CORTEX Prompts & Agents - Quick Start Guide

**Status:** ✅ All refactored and ready to use  
**Date:** January 19, 2026  
**Location:** `.github/prompts/` and `.github/agents/`

---

## 🚀 Quick Access

### Implementation (Building ACs)
- **New AC-ID:** Use `.github/prompts/cortex-builder.prompt.md`
- **Resume Session:** Use `.github/prompts/cortex-builder-continuation.prompt.md`
- **Agent:** Use `.github/agents/cortex-builder.md`

### Planning (Phases & Roadmap)
- **Phase Planning:** Use `.github/prompts/cortex-planner.prompt.md`
- **Agent:** Use `.github/agents/cortex-planner.md`

### Quality Reviews (Testing & Validation)
- **Governance Compliance:** Use `.github/prompts/cortex-governance.prompt.md`
- **Assumptions:** Use `.github/prompts/cortex-review-assumptions.prompt.md`
- **Brittleness:** Use `.github/prompts/cortex-review-brittleness.prompt.md`
- **Technical Debt:** Use `.github/prompts/cortex-review-debt.prompt.md`
- **Hallucinations:** Use `.github/prompts/cortex-review-hallucination.prompt.md`
- **Agent (all reviews):** Use `.github/agents/cortex-review.md`

### Gap Analysis
- **Design-Build Gaps:** Use `.github/prompts/cortex-gap-detection.prompt.md`
- **Agent:** Use `.github/agents/cortex-gap-detection.md`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `.github/PROMPTS-AGENTS-INDEX.md` | Complete index & file listing |
| `.github/ARCHITECTURE-MAP.md` | Visual data flow & architecture |
| `.github/REFACTORING-SUMMARY-20260119.md` | What changed & improvements |

---

## ⚡ Response Format

All responses follow this pattern:

```
## Section Title

✅ **Finding 1** (one-liner)
• Detail (bullet)
• Detail (bullet)

| Table | When | Format | Appropriate |
|-------|------|--------|-------------|

**Next Action:** Clear sentence
```

**Key principle:** NO narratives, NO code snippets, tables + bullets only

---

## 🎯 Common Commands

```
/status <phase>              → Show phase status
/next                        → Show next action
/readiness <phase>           → Check prerequisites
/audit <ac-id|phase>         → Audit trail
/compliance <phase>          → Governance check
/blockers                    → Show blocking issues
/governance-check <phase>    → Full compliance
```

---

## ✅ File Locations

| Type | Location | Example |
|------|----------|---------|
| **Prompts** | `.github/prompts/` | cortex-builder.prompt.md |
| **Agents** | `.github/agents/` | cortex-builder.md |
| **Docs** | `docs/` | Architecture guides (reference) |
| **Reports** | `_workspaces/roadmap/reports/` | YAML status files |

---

## 🔧 Key Features

✅ **Minimum Verbosity** - All files <130 lines  
✅ **Executive Summary Format** - Tables + bullets only  
✅ **Session Continuation** - 5-second resumption protocol  
✅ **Governance Integration** - SKULL rules in every prompt  
✅ **Standardized Commands** - Same `/status`, `/next`, etc across all  
✅ **No Markdown Reports** - Terminal + YAML only  

---

## 🚫 What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **File Size** | 400-500 lines | 50-130 lines |
| **Format** | Narrative | Tables + bullets |
| **Location** | Various (`docs/`, root, etc) | `.github/prompts/` & `.github/agents/` |
| **Reports** | `.md` files everywhere | YAML + terminal |
| **Continuation** | Full context dump | 5-second status table |
| **Governance** | Scattered policy | Consolidated table |

---

## 🎓 Example Session

### Start New AC

```
1. Open: .github/prompts/cortex-builder.prompt.md
2. See: Governance quick table + 4-step implementation checklist
3. Follow: Git checkpoint → Test → Implement → Audit → Commit
4. Response format: AC status table (no narratives)
```

### Resume Next Day

```
1. Open: .github/prompts/cortex-builder-continuation.prompt.md
2. See: 5-second status (phase, progress, last commit, next AC)
3. Act: Start implementing next AC immediately
4. Result: No context dump, silent resume mode
```

### Check Phase Readiness

```
1. Open: .github/prompts/cortex-planner.prompt.md
2. Command: /readiness phase-15
3. See: Table with dependencies, prerequisites, audit, governance, workspace
4. Response: PROCEED or WAIT (clear recommendation)
```

### Find Quality Issues

```
1. Open: .github/prompts/cortex-review-{type}.prompt.md
2. Command: /brittleness or /assumptions or /debt
3. See: Priority matrix with severity, effort, payoff
4. Response: Actionable findings with fixes
```

---

## 🔗 Integration Points

All prompts/agents integrate with:

- **cortex-master.yaml** (v2.1 SSOT)
- **phases/phase-XX.yaml** (AC specifications)
- **core-rules.yaml** (28 SKULL governance rules)
- **governance.db** (Audit trail)

---

## ⚙️ Configuration

No configuration needed. All files are ready to use as-is.

**SSOT:** `_workspaces/roadmap/cortex-master.yaml`  
**Governance:** `cortex_brain/tier0/governance/core-rules.yaml`  
**Audit Trail:** `cortex_brain/state/governance.db`

---

## 📞 Getting Help

- **What file do I use?** → See "Quick Access" above
- **Response format unclear?** → See "Response Format" section
- **Command syntax?** → See "Common Commands" or prompt file
- **Architecture?** → Read `.github/ARCHITECTURE-MAP.md`
- **What changed?** → Read `.github/REFACTORING-SUMMARY-20260119.md`

---

**Version:** 2.1 (Refactored for Conciseness)  
**Status:** ✅ Ready to use  
**All tests:** ✅ Passing  
**Governance:** ✅ Compliant
