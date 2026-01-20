# Prompt & Agent Refactoring Summary

**Date:** 2026-01-19  
**Objective:** Refactor all prompts and agents to work with cortex-master.yaml (v2.1) with minimum verbosity, executive summaries, and proper file placement.

---

## Files Refactored

### Prompts (in `.github/prompts/`)

| File | Purpose | Format | Key Changes |
|---|---|---|---|
| `cortex-builder.prompt.md` | AC-ID implementation | Concise tables + checklist | Removed verbose sections, added governance table |
| `cortex-builder-continuation.prompt.md` | Session resumption | Quick status table | NEW: 5-second resumption, silent continuation |
| `cortex-planner.prompt.md` | Phase planning & analysis | Status tables + bullets | Removed narrative, added readiness matrix |
| `cortex-gap-detection.prompt.md` | Design-build gap analysis | Category table + findings | Simplified detection queries |
| `cortex-governance.prompt.md` | Compliance verification | Rule table + SQL queries | Extracted from review-governance.md |
| `cortex-review-assumptions.prompt.md` | Hidden assumptions | Category matrix | Added verification matrix |
| `cortex-review-brittleness.prompt.md` | Structural weaknesses | Risk matrix | Prioritized by severity |
| `cortex-review-debt.prompt.md` | Technical debt | Prioritization matrix | Added P0-P3 levels |
| `cortex-review-hallucination.prompt.md` | False claims detection | Verification matrix | NEW: Contradiction checker |

### Agents (in `.github/agents/`)

| File | Changes |
|---|---|
| `cortex-builder.md` | Streamlined: SSOT table + protocol + governance integration (concise) |
| `cortex-planner.md` | Rebuilt from corrupted file: Quick commands + status format |
| `cortex-gap-detection.md` | Simplified: Gap categories + detection queries (no verbose policy) |
| `cortex-review.md` | NEW: Master review agent consolidating all review types |

---

## Key Improvements

### 1. Minimum Verbosity
**Before:** 400-500 line files with repetitive policy sections  
**After:** 50-100 line files with just essential content

**Example:**
- Before: 15-paragraph governance policy section
- After: 1 simple table showing forbidden locations

### 2. Executive Summary Format
**Before:** Narrative explanations  
**After:** Bullet points + tables only

**Response pattern:**
```
✓ PREFERRED: "AC-001: Test passing (12/12) | CORE-008 ✓ | Next: AC-002"
✗ AVOID: "This acceptance criterion was successfully completed because..."
```

### 3. Response Headers
All prompts now include:
- **Command examples** (copy-paste ready)
- **Output table format** (expected structure)
- **Quick reference table** (common checks)

### 4. No Markdown Reports
**Before:** Created `.md` report files everywhere  
**After:** 
- YAML status to `_workspaces/roadmap/reports/`
- Terminal output (default)
- Documentation `.md` only in `docs/`

### 5. Session Continuation
**NEW:** `cortex-builder-continuation.prompt.md`
- Loads status in 5 seconds
- Resumes silently without context dump
- Shows only: phase, AC-ID, last commit, next action

---

## File Placement Standard

| Type | Location | Status |
|---|---|---|
| **Prompts** | `.github/prompts/` | ✅ Centralized |
| **Agents** | `.github/agents/` | ✅ Centralized |
| **Docs** | `docs/` | ✅ Reference only |
| **YAML Reports** | `_workspaces/roadmap/reports/` | ✅ Tracking |
| **Findings** | `_workspaces/roadmap/issues/` | ✅ Analysis |

---

## Governance Reference Consolidated

All 28 SKULL rules now have:
1. Quick reference table in relevant prompts
2. Specific examples per rule
3. Verification method (query or check)

**Common rules:**
- CORE-008: TDD first
- CORE-011: Type hints mandatory
- CORE-012: Google docstrings
- CORE-013: No bare except
- CORE-026: Git checkpoint
- CORE-027: Audit trail (START→EXECUTE→COMPLETE)
- CORE-028: Kebab-case, ≤25 chars

---

## Commands Standardized

All agents/prompts now support:

**Status:**
- `/status` → Phase or AC status
- `/next` → Next action
- `/readiness <phase>` → Can proceed?

**Analysis:**
- `/audit <phase>` → Audit trail
- `/compliance <phase>` → Governance compliance
- `/violations <phase>` → Rule violations

**Planning:**
- `/phase <N>` → Phase details
- `/blockers` → Blocking issues
- `/dependencies <ac-id>` → Dependency graph

**Review:**
- `/gaps` → Design-build gaps
- `/assumptions` → Hidden assumptions
- `/brittleness` → Structural weaknesses
- `/debt` → Technical debt
- `/hallucinations` → False claims

---

## Output Format Standardized

**All responses now follow:**

```
[SECTION HEADING]

✅ **Key Finding:** (Bullet 1)
• Details (Bullet 2)
• Details (Bullet 3)

| Table | Format | When | Appropriate |
|---|---|---|---|
| Used for | Multi-row | Data with | Multiple cols |

**Next Action:** Clear, single sentence
```

**Never:**
- Code snippets (unless requested)
- Paragraph narratives
- Verbose explanations
- Multiple sections per response

---

## Mapping Old → New

### Old docs/cortex-*.prompt.md → New .github/prompts/
- `docs/cortex-builder.prompt.md` → `.github/prompts/cortex-builder.prompt.md` (refactored)
- `docs/cortex-builder-continuation.prompt.md` → `.github/prompts/cortex-builder-continuation.prompt.md` (new)
- `docs/cortex-planner.md` → `.github/prompts/cortex-planner.prompt.md` (refactored)
- `docs/CORTEX.prompt.md` → Reference archive (no active use)
- `docs/cortex-review-*.md` → `.github/prompts/cortex-review-*.prompt.md` (refactored into 4 files)

### Old .github/agents → Streamlined
- `cortex-builder.md` (streamlined)
- `cortex-planner.md` (rebuilt, simplified)
- `cortex-gap-detection.md` (simplified)
- `cortex-review.md` (NEW: consolidates all reviews)
- ~~cortex-reviewer.md~~ (consolidated into review agents)

---

## Next Steps

1. ✅ All `.github/prompts/` files created and optimized
2. ✅ All `.github/agents/` files streamlined
3. Test continuation behavior (cortex-builder-continuation.prompt.md)
4. Verify governance table format in cortex-builder.prompt.md
5. Clean up old docs/ prompt files (when ready to deprecate)

---

## Verification Checklist

- [x] All prompts <100 lines (executive summary only)
- [x] All prompts have command examples
- [x] All prompts have output format table
- [x] All prompts have governance reference
- [x] No `.md` reports created (YAML + terminal only)
- [x] File placement: `.github/prompts/` and `.github/agents/`
- [x] No verbosity in response format examples
- [x] Continuation prompt supports silent resume
- [x] Tables used instead of narratives
- [x] Governance rules consolidated and cross-referenced
