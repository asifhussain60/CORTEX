# Silent Execution Response Template (GENERIC)

**Authority:** CORE-049 Silent Autonomous Execution  
**Version:** 1.0  
**Use Case:** Autonomous plan execution with progress tracking

---

## Generic Template (Copy & Adapt)

Use this template for ANY autonomous wave/plan completion report. Replace bracketed variables with actual values.

### Format

```markdown
---

📋 **[WAVE/PLAN NAME] [STAGE NUMBER]: [STAGE TITLE]**

`██████████` [COMPLETION %]% [STAGE NAME] Complete

| # | Status | Component | Detail |
|---|--------|-----------|--------|
| 1 | [STATUS_ICON] | [COMPONENT_1] | [RESULT_1] |
| 2 | [STATUS_ICON] | [COMPONENT_2] | [RESULT_2] |
| 3 | [STATUS_ICON] | [COMPONENT_3] | [RESULT_3] |
| 4 | [STATUS_ICON] | [COMPONENT_4] | [RESULT_4] |
| 5 | [STATUS_ICON] | [COMPONENT_5] | [PENDING/RESULT_5] |

**Tests:** [PASSED]/[TOTAL] | **Coverage:** [COVERAGE_PCT]%
**Fixed:** [KEY_FIX_SUMMARY]

---
```

---

## Variable Guide

| Variable | Description | Examples |
|----------|-------------|----------|
| `[WAVE/PLAN NAME]` | Plan or wave identifier | `WAVE-R`, `PHASE-52`, `MASTER-PLAN-V5` |
| `[STAGE NUMBER]` | Numeric stage identifier | `4`, `Stage 2`, `S3` |
| `[STAGE TITLE]` | Descriptive stage name | `Integration Testing`, `Schema Migration`, `Auth Implementation` |
| `[COMPLETION %]` | Percentage (0-100) | `100`, `75`, `50` |
| `[COMPONENT_N]` | Feature/component name | `DebuggerOrchestrator`, `AuthService`, `EventBus` |
| `[STATUS_ICON]` | Status indicator | `✅` (done), `🟡` (in progress), `⚪` (pending), `🔴` (failed) |
| `[RESULT_N]` | Specific outcome | `24 tests`, `3 endpoints`, `8 tests ← FIXED` |
| `[PASSED]/[TOTAL]` | Test counts | `58/69`, `100/100`, `42/50` |
| `[COVERAGE_PCT]` | Coverage percentage | `84`, `95`, `72` |
| `[KEY_FIX_SUMMARY]` | Main accomplishment | `Session ID timestamp collision (microseconds)`, `Memory leak in event handler`, `Cache invalidation logic` |

---

## Real-World Examples

### Example 1: Wave Completion

```markdown
---

📋 **WAVE-R Stage 4: Integration Testing**

`██████████` 100% Stage 4 Complete

| # | Status | Component | Detail |
|---|--------|-----------|--------|
| 1 | ✅ | DebuggerOrchestrator | 24 tests |
| 2 | ✅ | MarkerInjectionEngine | 17 tests |
| 3 | ✅ | AutoCleanupManager | 9 tests |
| 4 | ✅ | Integration | 8 tests ← FIXED |
| 5 | ⚪ | MCP Tools | pending |

**Tests:** 58/69 | **Coverage:** 84%
**Fixed:** Session ID timestamp collision (microseconds)

---
```

### Example 2: Phase Mid-Stage

```markdown
---

📋 **PHASE-52 Stage 2: Event Bus Debugger Implementation**

`██████████████░░░░░░` 75% Stage 2 In Progress

| # | Status | Component | Detail |
|---|--------|-----------|--------|
| 1 | ✅ | EventBusCore | 42 tests passing |
| 2 | ✅ | MessageTracing | 18 tests passing |
| 3 | 🟡 | DebugUI | 12/15 tests passing ← FIXING |
| 4 | ⚪ | Integration | pending |
| 5 | ⚪ | E2E Tests | pending |

**Tests:** 72/85 | **Coverage:** 81%
**In Progress:** Dashboard state reconstruction logic

---
```

### Example 3: Master Plan Multi-Wave

```markdown
---

📋 **MASTER-PLAN-V5 Wave A: Foundation Infrastructure**

`██████████` 100% Foundation Complete

| # | Status | Component | Detail |
|---|--------|-----------|--------|
| 1 | ✅ | Orchestrator Registry | 34 tests |
| 2 | ✅ | MCP Gateway | 28 tests |
| 3 | ✅ | Error Handling | 19 tests |
| 4 | ✅ | Validation Agents | 22 tests ← FIXED |
| 5 | ✅ | Documentation | complete |

**Tests:** 103/103 | **Coverage:** 94%
**Fixed:** Cross-platform settings path resolution

---
```

---

## Rendering Rules

### Separator Format
- Use markdown horizontal rule: `---` (three dashes)
- **CRITICAL:** Always add blank line AFTER `---` before content
- Place BEFORE and AFTER stage results
- **WHY:** HTML `<hr>` tags cause rendering conflicts with markdown headers in VS Code Copilot Chat

### Progress Bar
- Use backticks: `` `██████████` `` (inline code prevents parsing)
- Percentage value matches completion (100% = all filled, 50% = half filled)
- Pattern: `██` (filled) + `░░` (empty)

### Status Icons (MANDATORY)
- `✅` — Completed successfully
- `🟡` — In progress / being fixed
- `⚪` — Pending / not yet started
- `🔴` — Failed (use sparingly)

### Table Format
- **Always use markdown tables** (not bullet lists or text)
- Columns: `# | Status | Component | Detail`
- Max 5-6 rows per table (keep compact)

### Metrics Line
- **Tests:** `[PASSED]/[TOTAL]`
- **Coverage:** `[PCT]%`
- **Fixed:** One-line summary of key accomplishment

---

## Do's ✅

- ✅ Use markdown `---` (three dashes) for separators
- ✅ Always add blank line after `---` before content
- ✅ Include exact test counts and coverage %
- ✅ Keep stage names under 30 characters
- ✅ Use status icons consistently
- ✅ Add single-line "← FIXED" note for completed fixes
- ✅ Update table row count based on actual components

## Don'ts ❌

- ❌ Text paragraphs ("I'm now implementing...")
- ❌ Bullet lists of actions taken
- ❌ Detailed file change descriptions
- ❌ Code snippets or examples
- ❌ Tree-drawing characters (`├─ └─`) — they collapse into one line
- ❌ Box-drawing characters `────` (renders too wide)

---

## Integration Points

### When to Use This Template

1. **Autonomous Wave Completion** — After `/implement phase X` completes
2. **Plan Stage Completion** — After `/plan resolve X` finishes
3. **Multi-Stage Progress** — Showing interim results during long operations
4. **Master Plan Waves** — Reporting Phase-N completion status

### How to Generate Dynamically

```python
# Example in MCP tool or orchestrator
def format_completion_report(wave_name, stage_num, stage_title, components, tests_passed, tests_total, coverage, fix_summary):
    progress_bar = "█" * (coverage // 10) + "░" * (10 - coverage // 10)
    
    rows = "\n".join([
        f"| {i+1} | {comp['status']} | {comp['name']} | {comp['detail']} |"
        for i, comp in enumerate(components)
    ])
    
    return f"""---

📋 **{wave_name} Stage {stage_num}: {stage_title}**

`{progress_bar}` {coverage}% Stage Complete

| # | Status | Component | Detail |
|---|--------|-----------|--------|
{rows}

**Tests:** {tests_passed}/{tests_total} | **Coverage:** {coverage}%
**Fixed:** {fix_summary}

---"""
```

---

## Validation Checklist

Before emitting response:

- [ ] `---` separators present (top and bottom)
- [ ] Blank line after opening `---`
- [ ] Blank line before closing `---`
- [ ] Progress bar matches completion percentage
- [ ] All status icons are consistent (✅/🟡/⚪/🔴)
- [ ] Test counts are accurate (`N/M` format)
- [ ] Coverage percentage is included
- [ ] Key fix summary is single line (≤80 chars)
- [ ] No tree-drawing characters or boxes
- [ ] Table renders correctly in markdown

---

## Related Docs

- Parent: `.github/copilot-instructions.md` § Silent Autonomous Execution
- Architecture: `.github/prompts/AUTONOMOUS-EXECUTION-GUIDE.md`
- Policy: CORE-049 Silent Autonomous Execution
