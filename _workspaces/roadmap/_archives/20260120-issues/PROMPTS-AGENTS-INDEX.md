# CORTEX Prompts & Agents - Complete Index

**Location:** `.github/prompts/` and `.github/agents/`  
**Updated:** 2026-01-19  
**Status:** All refactored to minimum verbosity + executive summary format

---

## Prompts (`.github/prompts/`)

### Core Implementation

| Prompt | Lines | Purpose | Format |
|--------|-------|---------|--------|
| **cortex-builder.prompt.md** | 96 | AC-ID implementation | Quick ref + checklist |
| **cortex-builder-continuation.prompt.md** | 84 | Session resumption | 5-sec status table |
| **cortex-planner.prompt.md** | 60 | Phase planning | Status tables |
| **cortex-gap-detection.prompt.md** | 50 | Design-build gaps | Category matrix |

### Governance & Review

| Prompt | Lines | Purpose | Format |
|--------|-------|---------|--------|
| **cortex-governance.prompt.md** | 95 | Compliance verification | Rules table + SQL |
| **cortex-review-assumptions.prompt.md** | 92 | Hidden assumptions | Category matrix |
| **cortex-review-brittleness.prompt.md** | 100 | Structural weaknesses | Risk matrix |
| **cortex-review-debt.prompt.md** | 108 | Technical debt | Priority matrix |
| **cortex-review-hallucination.prompt.md** | 129 | False claims | Verification matrix |

### Legacy (Reference Only)

| Prompt | Status | Note |
|--------|--------|------|
| cortex-git-commit.prompt.md | Reference | Old commit convention |
| cortex-review.prompt.md | Archive | Consolidated into individual review prompts |
| CORTEX.prompt.md | Archive | Master orchestrator (superseded by builders) |

---

## Agents (`.github/agents/`)

### Active Agents

| Agent | Lines | Purpose | Commands |
|-------|-------|---------|----------|
| **cortex-builder.md** | 45 | AC implementation | Build protocol, governance integration |
| **cortex-planner.md** | 40 | Phase analysis | Status, readiness, blockers |
| **cortex-gap-detection.md** | 35 | Gap analysis | Gap detection, remediation |
| **cortex-review.md** | 40 | Quality verification | Compliance, brittleness, debt, assumptions, hallucinations |

### Legacy

| Agent | Status |
|-------|--------|
| cortex-agents-update-phase-consolidation.md | Reference |
| cortex-review-assumptions.md | Consolidated → cortex-review.md |
| cortex-review-brittleness.md | Consolidated → cortex-review.md |
| cortex-review-debt.md | Consolidated → cortex-review.md |
| cortex-review-governance.md | Consolidated → cortex-review.md |
| cortex-review-hallucination.md | Consolidated → cortex-review.md |

---

## Quick Start

### For Implementation
```bash
# Start new AC-ID
→ Use: .github/prompts/cortex-builder.prompt.md

# Resume from previous session
→ Use: .github/prompts/cortex-builder-continuation.prompt.md

# Plan next phase
→ Use: .github/prompts/cortex-planner.prompt.md
```

### For Quality Reviews
```bash
# Check governance compliance
→ Use: .github/prompts/cortex-governance.prompt.md

# Find all quality issues
→ Use: .github/prompts/cortex-review-{assumptions|brittleness|debt|hallucination}.prompt.md

# Detect design-build gaps
→ Use: .github/prompts/cortex-gap-detection.prompt.md
```

### For Copilot Chats
```bash
# CORTEX Builder Agent
→ Use: .github/agents/cortex-builder.md

# CORTEX Planner Agent
→ Use: .github/agents/cortex-planner.md

# CORTEX Gap Detection Agent
→ Use: .github/agents/cortex-gap-detection.md

# CORTEX Review Agent
→ Use: .github/agents/cortex-review.md
```

---

## Key Improvements Summary

✅ **Minimum Verbosity**
- Removed repetitive policy sections
- Consolidated rules into single tables
- Prompts now 50-130 lines (vs. 400-500 before)

✅ **Executive Summary Format**
- Bullets + tables ONLY
- No narratives or examples in body
- Clear command reference at top

✅ **Proper File Placement**
- All prompts in `.github/prompts/`
- All agents in `.github/agents/`
- Documentation in `docs/` only
- YAML reports in `_workspaces/roadmap/reports/`

✅ **Response Format Standardized**
- Status tables for phase/AC info
- Governance rule tables
- Priority/risk matrices
- Verification checklists

✅ **Session Continuation**
- NEW: cortex-builder-continuation.prompt.md
- 5-second resumption
- Silent continuation (no context dump)
- Last commit + next action only

✅ **Commands Consistent**
- `/status` → Phase/AC status
- `/next` → Next action
- `/audit` → Verification
- `/readiness` → Prerequisites met?

---

## Usage Examples

### Example: Check Phase Readiness
```
Command: /readiness phase-15

Expected Output:
PHASE-15 READINESS
├─ Dependencies: PHASE-06 ✓ (locked)
├─ Prerequisites: ✓ (all components exist)
├─ Audit Trail: ✓ (verified)
├─ Governance: ✓ (28 rules loaded)
├─ Workspace: ✓ (git clean)
└─ Recommendation: PROCEED
```

### Example: Identify Violations
```
Command: /violations phase-07

Expected Output:
PHASE-07 GOVERNANCE VIOLATIONS
├─ CRITICAL: 0
├─ HIGH: 1 (CORE-028 in AC-XXX-XX-05)
├─ MEDIUM: 0
└─ LOW: 0

Recommendation: Fix AC-XXX-XX-05 before phase lock
```

### Example: Resume Session
```
On session start with continuation prompt:

═══════════════════════════════════════════════════════════════
║ SESSION RESUMPTION STATUS                                    ║
╠═══════════════════════════════════════════════════════════════╣
║ Current Phase: PHASE-XX                                      ║
║ Status: IN_PROGRESS | 5/14 ACs completed (36%)              ║
║ Last Activity: AC-XXX-XX-05 (12h ago)                       ║
║ Next Action: AC-XXX-XX-06 (Ready to start)                  ║
╚═══════════════════════════════════════════════════════════════╝

→ Immediately start AC-XXX-XX-06 (no context dump)
```

---

## Governance Rules Quick Reference

**All 9 critical SKULL rules in every prompt:**

| Rule | Requirement | Severity |
|------|---|---|
| CORE-008 | Tests BEFORE code | CRITICAL |
| CORE-011 | Type hints on all functions | CRITICAL |
| CORE-012 | Google docstrings (public APIs) | CRITICAL |
| CORE-013 | No bare `except:` | CRITICAL |
| CORE-026 | Git checkpoint before major action | CRITICAL |
| CORE-027 | Audit trail: START→EXECUTE→COMPLETE | CRITICAL |
| CORE-028 | Kebab-case, ≤25 chars | CRITICAL |
| CORE-017 | Strict governance (no overrides) | CRITICAL |
| CORE-001 | <500 lines per turn | CRITICAL |

---

## Response Format Standard

**All responses follow this pattern:**

```
## [Section Title]

✅ **Finding 1** (one-liner)
• Details (bullet 1)
• Details (bullet 2)

| Column | Format | When | Use |
|--------|--------|------|-----|

**Next Action:** Single, clear sentence
```

**Never:**
- Code snippets in body
- Paragraph narratives
- Verbose explanations
- Multiple disconnected sections

---

## Troubleshooting

**Q: Prompt seems outdated?**  
A: Check `.github/prompts/` not `docs/` (old location)

**Q: Agent not responding?**  
A: Verify `.github/agents/` file exists and is referenced

**Q: Response too verbose?**  
A: Prompt should have "NO verbosity" or "executive summary" rule

**Q: Missing governance rules?**  
A: All prompts should have SKULL rules table at top

**Q: File in wrong location?**  
A: Prompts → `.github/prompts/`, Agents → `.github/agents/`

---

**Last Updated:** 2026-01-19  
**Version:** v2.1 (Refactored for conciseness)  
**Status:** All prompts operational with new format
