# CORTEX Prompts & Agents Organization

**Last Updated:** January 19, 2026  
**Status:** ✅ Organized & Ready

---

## 📋 Overview

All CORTEX prompts are organized in `.github/prompts/` with the following structure:

- **Root level:** 4 main entry-point prompts
- **Subdirectories:** Specialized prompts organized by function
- **Cross-references:** All prompts include "Related Prompts" sections

---

## 📌 Root Level Prompts (Main Entry Points)

These are the primary prompts you load based on what you need to do:

### 1. **CORTEX.prompt.md**
**Master Orchestrator & Intent Router System Prompt**
- Purpose: System-level architecture, governance foundation, LENS protocol
- Load when: Setting up the CORTEX system context
- Role: Explains how CORTEX works, governance rules, master orchestrator pattern
- Links to: All specialized prompts in subdirectories

### 2. **cortex-builder.prompt.md**
**Implementation Prompt with TDD & Governance**
- Purpose: Implement AC-IDs from cortex-master.yaml
- Load when: Ready to code acceptance criteria
- Role: TDD-first implementation, governance enforcement, audit trail
- Pre-implements: Phase checking, tests before code, strict CORE rules
- Links to: Continuation prompt (session resumption), Review prompts

### 3. **cortex-review.prompt.md**
**Complete Code Review System**
- Purpose: Surgical code review with parallel agent analysis
- Load when: Need to find issues, gaps, debt, or verify quality
- Role: 5-phase investigation → gap detection → implementation support
- Includes: Data validation, investigation protocol, specialized review agents
- Links to: Specialized review prompts in `review/` subfolder

### 4. **cortex-git-commit.prompt.md**
**Multi-Machine Development & Merge Protocol**
- Purpose: Safe git workflows, absolute path prevention, database sync
- Load when: Merging code, syncing across machines, or committing
- Role: Pre-commit verification, merge conflict resolution, audit enforcement
- Includes: Pre-push checklist, merge protocols, post-merge sync
- Links to: Builder and governance prompts

---

## 📁 Organized Subdirectories

### `builder/` - Session Management
**Location:** `.github/prompts/builder/`

| File | Purpose |
|------|---------|
| `cortex-builder-continuation.prompt.md` | Resume sessions without context dumps - 5-second status table |

**Use case:** When switching between sessions or continuing work from previous chat

---

### `planning/` - Planning & Governance
**Location:** `.github/prompts/planning/`

| File | Purpose |
|------|---------|
| `cortex-planner.prompt.md` | Phase readiness assessment, next steps, status queries |
| `cortex-governance.prompt.md` | SKULL rules verification, audit trail validation, compliance reports |

**Use case:** Before starting new phases or verifying governance compliance

---

### `review/` - Specialized Quality Reviews
**Location:** `.github/prompts/review/`

| File | Purpose |
|------|---------|
| `cortex-review-assumptions.prompt.md` | Detect platform/environment assumptions |
| `cortex-review-brittleness.prompt.md` | Identify fragile error handling & state management issues |
| `cortex-review-debt.prompt.md` | Find TODOs, skipped tests, type stubs, duplication |
| `cortex-review-hallucination.prompt.md` | Verify claims and detect contradictions |

**Use case:** Deep-dive quality checks for specific quality dimensions

---

### `utilities/` - Tools & Analysis
**Location:** `.github/prompts/utilities/`

| File | Purpose |
|------|---------|
| `cortex-gap-detection.prompt.md` | Analyze design-build gaps systematically |

**Use case:** Identify gaps between design specifications and actual implementation

---

## 🔗 Reference Map

### By Role/Task

**If you want to...** → **Load this prompt:**

| Task | Prompt | Location |
|------|--------|----------|
| Understand CORTEX architecture | `CORTEX.prompt.md` | Root |
| Implement AC-IDs | `cortex-builder.prompt.md` | Root |
| Continue from previous session | `builder/cortex-builder-continuation.prompt.md` | `builder/` |
| Check phase readiness | `planning/cortex-planner.prompt.md` | `planning/` |
| Review code quality | `cortex-review.prompt.md` | Root |
| Deep-dive: assumptions | `review/cortex-review-assumptions.prompt.md` | `review/` |
| Deep-dive: brittleness | `review/cortex-review-brittleness.prompt.md` | `review/` |
| Deep-dive: technical debt | `review/cortex-review-debt.prompt.md` | `review/` |
| Deep-dive: hallucinations | `review/cortex-review-hallucination.prompt.md` | `review/` |
| Detect design gaps | `utilities/cortex-gap-detection.prompt.md` | `utilities/` |
| Multi-machine merge | `cortex-git-commit.prompt.md` | Root |
| Governance compliance | `planning/cortex-governance.prompt.md` | `planning/` |

### By Workflow

**Phase Implementation Workflow:**
1. Check readiness → `planning/cortex-planner.prompt.md`
2. Implement ACs → `cortex-builder.prompt.md`
3. Continue next session → `builder/cortex-builder-continuation.prompt.md`
4. Review code → `cortex-review.prompt.md` + deep-dives as needed
5. Verify governance → `planning/cortex-governance.prompt.md`
6. Commit safely → `cortex-git-commit.prompt.md`

**Quality Review Workflow:**
1. Full code review → `cortex-review.prompt.md`
2. Specialized reviews → `review/cortex-review-*.prompt.md` (any combination)
3. Gap analysis → `utilities/cortex-gap-detection.prompt.md`
4. Implement fixes → `cortex-builder.prompt.md`

---

## 🔄 Cross-References

All prompts include a **"📚 Related Prompts"** section at the end that references:
- Where to go next
- What to load for specific tasks
- Related tools and utilities

Example:
```markdown
## 📚 Related Prompts

**Planning & Governance:**
- `planning/cortex-planner.prompt.md` - Phase readiness assessment
- `planning/cortex-governance.prompt.md` - Compliance verification
```

---

## 📊 Statistics

| Category | Count | Total Lines |
|----------|-------|------------|
| **Root prompts** | 4 | ~3,300 |
| **Builder subfolder** | 1 | ~96 |
| **Planning subfolder** | 2 | ~155 |
| **Review subfolder** | 4 | ~500 |
| **Utilities subfolder** | 1 | ~50 |
| **TOTAL** | 12 | ~4,100 |

---

## 🎯 Quick Access Guide

### For New Sessions
```
→ Load: CORTEX.prompt.md (system context)
→ Then: cortex-builder.prompt.md OR cortex-review.prompt.md (your task)
```

### For Continuing Sessions
```
→ Load: builder/cortex-builder-continuation.prompt.md (5-second status)
→ Resume: Where you left off
```

### For Planning Phases
```
→ Load: planning/cortex-planner.prompt.md (check readiness)
→ Then: cortex-builder.prompt.md (implement)
```

### For Quality Deep-Dives
```
→ Load: cortex-review.prompt.md (full analysis)
→ Specialize: review/cortex-review-X.prompt.md (specific issue)
```

---

## 📝 File Placement Rules

**NEVER create prompts outside these locations:**
- ❌ NOT in `docs/` folder (prompts stay in `.github/prompts/`)
- ❌ NOT scattered across root or other directories
- ✅ Only in `.github/prompts/` and its subdirectories

**IF you need to add a new prompt:**
1. Determine its category (builder, planning, review, utilities, or new category)
2. Create subdirectory if needed: `.github/prompts/new-category/`
3. Create prompt file: `.github/prompts/category/cortex-XXX.prompt.md`
4. Add "📚 Related Prompts" section referencing main prompts
5. Update root prompt (CORTEX.prompt.md) with link
6. Update this README.md

---

## ✅ Success Criteria

A well-organized prompts folder meets ALL of these:

- ☐ **4 main prompts** in root (`CORTEX.prompt.md`, `cortex-builder.prompt.md`, `cortex-review.prompt.md`, `cortex-git-commit.prompt.md`)
- ☐ **Specialized prompts** in organized subdirectories (`builder/`, `planning/`, `review/`, `utilities/`)
- ☐ **NO duplicate files** in root AND subdirectories
- ☐ **All prompts have** "📚 Related Prompts" sections with cross-references
- ☐ **README.md** documents the structure and how to use it
- ☐ **No unorganized files** in root beyond the 4 main prompts

---

## 🔧 Maintenance

### When Adding New Prompts
1. Create in appropriate subfolder
2. Add "📚 Related Prompts" section
3. Update all related prompts with backlinks
4. Update this README.md with new entry

### When Updating Prompts
1. Keep references in "📚 Related Prompts" sections current
2. Update README.md if structure changes
3. Verify no absolute paths leak into prompts

### When Reorganizing
1. Move files to new locations
2. Update ALL cross-references in existing prompts
3. Update README.md
4. Verify no broken references

---

**Status:** ✅ Complete & Ready to Use  
**Organization:** Hierarchical with clear category structure  
**Discoverability:** All prompts cross-referenced with "📚 Related Prompts"  
**Maintainability:** README.md + cross-references ensure easy updates
