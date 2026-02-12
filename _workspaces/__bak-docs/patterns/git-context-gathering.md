# Git Context-First Analysis Pattern

**Pattern ID:** PATTERN-GIT-001  
**Created:** 2026-02-04  
**Source:** chat01.md DIGEST analysis  
**Status:** ✅ Active  
**Context:** LENS Protocol (Stage 0)

---

## Context

CORTEX follows the LENS Protocol (Language → Examination → Navigation → Synthesis). Before analyzing any request, gathering **git context** provides:
1. **Recent work** — What changed in last 24-48h?
2. **Developer intent** — Commit messages reveal goals
3. **Patterns** — File clusters show architectural decisions
4. **Evidence** — Concrete proof for Implementation Truth (CORE-030)

---

## Problem

**Analysis Without Git Context:**
- ❌ Recommendations contradict recent decisions
- ❌ No awareness of in-progress work
- ❌ Miss patterns only visible in commit history
- ❌ Lack evidence for challenge generation
- ❌ Suggest already-tried approaches

**Example (Anti-Pattern):**
```
User: "Implement caching for dashboard"
CORTEX (no git): "Add Redis caching"
Reality: User tried Redis 2 days ago, reverted due to file:// protocol
```

---

## Solution

**Always start DESIGN/AUDIT mode with git context gathering:**

```bash
git log --since="48 hours ago" --oneline --name-status --all
```

**What This Reveals:**
- Modified files (M), Added files (A), Deleted files (D)
- Commit messages (developer intent)
- File clusters (modules being worked on)
- Timestamps (velocity, activity patterns)

---

## Implementation

### Stage 0: Git Context (Before Challenge)

```markdown
0. LENS Context (cortex_git_history) — Always first
      ↓
   Extract:
   - Commits (last 48h)
   - Active files
   - Commit messages
   - Author patterns
      ↓
1. MANDATORY Challenge (with evidence from git)
```

### Command Invocation

```python
# In DESIGN/AUDIT mode, always run first:
result = run_terminal_command(
    command="git log --since='48 hours ago' --oneline --name-status --all 2>/dev/null | head -200",
    explanation="Gather git context for evidence-based analysis"
)

# Parse output:
commits = parse_git_log(result.output)
active_files = extract_file_paths(commits)
patterns = detect_file_clusters(active_files)
```

### Duration Selection

| Duration | Use Case |
|----------|----------|
| **24 hours** | Daily standup, quick fixes |
| **48 hours** | Standard analysis (default) |
| **7 days** | Weekly review, refactoring planning |
| **30 days** | Architecture review, tech debt assessment |

**Default:** 48 hours (balances recency with completeness)

---

## Output Format

### Git Context Table

```markdown
### 🔍 Git Context (48 Hours)

| Metric | Value |
|--------|-------|
| Commits | {count} commits |
| Recent Work | {summary} |
| Key Patterns | {file clusters, themes} |
| Active Files | {primary modules} |
```

**Example:**
```markdown
### 🔍 Git Context (48 Hours)

| Metric | Value |
|--------|-------|
| Commits | 35+ commits |
| Recent Work | SDLC Phases 0-9 complete, Debug Orchestrator, Dashboard SPA enhancements |
| Key Patterns | TDD enforcement, JSON-first architecture, DeferredRenderer pattern |
| Active Files | company/dashboards/spa/*, cortex/orchestrators/*, _workspaces/cortex-plan/* |
```

---

## Benefits

| Benefit | Impact |
|---------|--------|
| **Evidence-Based** | Challenges cite specific commits, files, LOC |
| **Context-Aware** | Recommendations align with recent decisions |
| **Pattern Detection** | Spot architectural trends (TDD, JSON-first) |
| **Conflict Prevention** | Don't suggest already-tried solutions |
| **Implementation Truth** | Concrete proof (CORE-030 compliance) |

---

## When to Use

| Trigger | Action |
|---------|--------|
| **DESIGN mode** | ✅ Always run git context first |
| **AUDIT mode** | ✅ Run for baseline understanding |
| **IMPLEMENT intent** | ✅ Check for conflicting work |
| **REFACTOR intent** | ✅ Identify recent changes to preserve |
| **META-AUDIT** | ⚠️ Optional (focus on prompts/agents) |

---

## Examples

### Example 1: Dashboard Enhancement (chat01.md)

**Git Context Command:**
```bash
git log --since="48 hours ago" --oneline --name-status --all 2>/dev/null | head -200
```

**Output Snippet:**
```
a1b2c3d Add DeferredRenderer pattern for hidden panels
M company/dashboards/spa/js/app.js
M company/dashboards/spa/dashboard.html

d4e5f6g Complete SDLC Phase 0-9 implementation
A _workspaces/cortex-plan/CORTEX-SELF-IMPROVEMENT-SDLC.yaml
M cortex/orchestrators/planning/enhanced_planning_orchestrator.py
```

**Challenge Uses This:**
```markdown
### Critical Issues (High Confidence ✅)
1. **Missing SPA Framework** — evidence: `dashboard.html:1-1109` has 1,109 lines inline 
   (commit a1b2c3d added DeferredRenderer but monolithic HTML remains) | Impact: ...
```

**Why This Works:**
- Cites specific commit (a1b2c3d)
- References line count (1,109 LOC)
- Shows pattern (DeferredRenderer = progress, but partial)

---

### Example 2: Refactoring Orchestrator

**Git Context Reveals:**
```
10 commits in cortex/orchestrators/domain/
8 files modified in last 48h
Pattern: All orchestrators now import IncrementalTaskDecomposer
```

**Challenge Response:**
```markdown
### Critical Issues
1. **No Token Budget Enforcement** — evidence: git shows 8 orchestrators 
   modified to use IncrementalTaskDecomposer but only 3 implement token_budget 
   parameter (grep search: 3/8 files) | Impact: ...
```

**Why This Works:**
- Git pattern (8 orchestrators modified)
- Code search verifies implementation (3/8 complete)
- Evidence: commit history + grep results

---

## Advanced: Git Blame Integration

**For deeper analysis, use git blame:**

```python
# Identify who/when code was last modified
result = run_terminal_command(
    command=f"git blame -L {start_line},{end_line} {file_path}",
    explanation="Identify author/date of problematic code"
)

# Use in challenge:
# "Function XYZ (last modified 3 months ago by @author) has complexity 22..."
```

---

## Tools & MCP Integration

| Tool | Purpose |
|------|---------|
| `cortex_git_history` | MCP tool for git context (24h default) |
| `git log --since` | Terminal command for custom duration |
| `git blame` | Identify code authorship |
| `git diff` | Compare branches, commits |

**MCP Tool Example:**
```python
context = mcp.cortex_git_history(
    repository_path="/Users/asifhussain/PROJECTS/CORTEX",
    since_hours=48,
    include_blame=True
)
```

---

## Integration with LENS

**LENS Protocol Flow:**

```
0. Git Context (Evidence Layer)
   ↓
1. Language (Parse user request)
   ↓
2. Examination (Code inspection + git patterns)
   ↓
3. Navigation (Route to orchestrator, informed by git)
   ↓
4. Synthesis (Challenge generation with git evidence)
```

---

## Anti-Patterns

**Don't:**
- ❌ Skip git context in DESIGN/AUDIT mode
- ❌ Use only commit messages (need file paths too)
- ❌ Ignore commit patterns (TDD, JSON-first visible in history)
- ❌ Look at single commits (need temporal patterns)
- ❌ Query >30 days without justification (noise vs signal)

**Example (Bad):**
```markdown
## Challenge
**Problem:** Add caching

[No git context, generic recommendation]
```

**Example (Good):**
```markdown
## Challenge
**Problem:** Add caching

### Git Context (48h)
- 3 commits modified dashboard data loading
- Pattern: Shifted SQLite → JSON (commit a1b2c3d)
- Evidence: JSON-first architecture already chosen

**Recommendation:** Client-side JSON caching (aligns with recent architecture)
```

---

## Success Criteria

✅ Git context gathered before challenge  
✅ Duration specified (24h/48h/7d/30d)  
✅ Commits, files, patterns extracted  
✅ Evidence cited in challenge (commit hashes, file paths)  
✅ Recommendations align with recent work  
✅ Implementation Truth validated via git  

---

## Related Patterns

- [LENS Protocol](../05-lens-protocol/README.md)
- [Implementation Truth (CORE-030)](../05-reference/core-rules.md#core-030)
- [Evidence-Based Challenges](challenge-format-engineer.md)

---

**Status:** ✅ Active in production (LENS Stage 0, all DESIGN/AUDIT modes)
