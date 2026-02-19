# Chat Session vs Terminal Output Guide

**Authority:** CORE-049 + Response Format Standards  
**Updated:** 2026-02-18

## 🎯 Core Principle

**All user-facing feedback goes to Chat Session. Only long-running processes go to terminal.**

---

## ✅ CORRECT: Display in Chat Session

### Progress Bars
```markdown
<hr>

📋 **Phase 47 Stage 2: Memory Tier Clarification**

`████████░░` 80% Implementing GREEN phase

| # | Status | Task | Tests |
|---|--------|------|-------|
| 1 | ✅ | Directory rename | 6/6 |
| 2 | 🔵 | Path updates | 4/10 |
| 3 | ⚪ | Documentation | 0/4 |

<hr>
```

**Implementation:**
- Write directly in markdown response
- NO `run_in_terminal` with `cat` or `echo`
- Renders inline in Chat Session

### Stage Completions
```markdown
<hr>

✅ **STAGE 2 COMPLETE**

**Duration:** 45 minutes  
**Tests:** 10/19 passing (9 skipped - expected)

### Changes
- Renamed `tier1_learned/` → `learned_patterns/`
- Created backward-compatible symlinks
- 19 TDD tests created

<hr>
```

### Results Tables
```markdown
| Component | Before | After | Status |
|-----------|--------|-------|--------|
| Governance | tier2>tier1>tier0 | tier0>tier1>tier2 | ✅ |
| Memory | tier1_learned/ | learned_patterns/ | ✅ |
| Tests | 0 | 45 passing | ✅ |
```

---

## ❌ WRONG: Sending to Terminal

### DON'T Use `run_in_terminal` for Visual Feedback

**WRONG:**
```python
run_in_terminal(
    command='cat << "EOF"\n`████████░░` 80% Processing...\nEOF',
    explanation="Progress update"
)
```

**Why wrong:**
- Progress bars appear in **terminal window** (not chat)
- User sees output in wrong location
- Violates chat-first UX principle

### DON'T Use `echo` for Status Updates

**WRONG:**
```python
run_in_terminal(
    command='echo "✅ Stage complete"',
    explanation="Status update"
)
```

**Why wrong:**
- Status messages should be in **chat response**
- Terminal is for command output, not narrative

---

## ✅ CORRECT: Use Terminal For

### Long-Running Commands
```python
run_in_terminal(
    command='pytest tests/ -v --cov',
    explanation="Running full test suite (may take 2-3 minutes)",
    isBackground=False
)
```

**Why correct:**
- Command takes time to execute
- Output is command result (not narrative)
- User expects terminal for test output

### Build Processes
```python
run_in_terminal(
    command='npm run build',
    explanation="Building production bundle",
    isBackground=True
)
```

**Why correct:**
- Background process needs terminal monitoring
- Build logs belong in terminal
- Chat shows initiation message only

### Git Operations
```python
run_in_terminal(
    command='git log --oneline -20',
    explanation="Checking recent commits",
    isBackground=False
)
```

**Why correct:**
- Git output is data, not narrative
- Terminal shows raw command results
- Chat shows analysis/summary

---

## 🎨 Progress Bar Implementation

### In Chat Response (Correct)

**Template:**
```markdown
<hr>

📋 **{Phase Name} Stage {N}: {Stage Name}**

`{fill_chars}{empty_chars}` {pct}% {current_action}

{optional_table_if_multi_stage}

<hr>
```

**Example:**
```markdown
<hr>

📋 **Phase 47 Stage 3: Tier System Integration**

`██████████` 100% Updating BrainTierPusher paths

<hr>
```

**Rendering:**
- Single-line bar with emoji
- Percentage and action description
- Clean `<hr>` separators
- No overflow in narrow chat windows

### Progress Updates

**For multi-stage operations:**
```markdown
<hr>

📋 **Phase 47: All Stages**

| Stage | Progress | Status |
|-------|----------|--------|
| 1 | `██████████` 100% | ✅ Complete |
| 2 | `██████████` 100% | ✅ Complete |
| 3 | `████████░░` 80% | 🔵 In Progress |
| 4 | `░░░░░░░░░░` 0% | ⚪ Pending |

<hr>
```

---

## 🔧 Implementation Checklist

### Before Writing Response

- [ ] Is this user-facing feedback? → **Chat**
- [ ] Is this a long-running command? → **Terminal**
- [ ] Is this progress indication? → **Chat**
- [ ] Is this command output? → **Terminal**

### Response Structure

```markdown
## {mode_icon} CORTEX Architect {MODE}
---

{brief_context_if_needed}

<hr>

📋 **{Phase/Task Name}**

`{progress_bar}` {pct}% {action}

<hr>

{run_terminal_commands_here_for_actual_work}

<hr>

✅ **{COMPLETION_TITLE}**

{summary_table}

<hr>
```

### Key Points

1. **Header once** at top (per prompt standards)
2. **Progress in chat** using markdown bars
3. **Commands in terminal** using `run_in_terminal`
4. **Results in chat** using markdown tables
5. **Separators** use `<hr>` HTML tag

---

## 📊 Decision Matrix

| Content Type | Location | Tool |
|--------------|----------|------|
| Progress bar | Chat | Markdown `\`bar\`` |
| Status update | Chat | Markdown text |
| Stage completion | Chat | Markdown table |
| Test command | Terminal | `run_in_terminal` |
| Build command | Terminal | `run_in_terminal` |
| Git command | Terminal | `run_in_terminal` |
| File operation | Terminal | `run_in_terminal` |
| Summary table | Chat | Markdown table |
| Metrics | Chat | Markdown table |
| Error details | Chat | Markdown code block |
| Fix suggestion | Chat | Markdown list |

---

## 🐛 Common Mistakes

### Mistake 1: Progress Bars in Terminal
```python
# ❌ WRONG
run_in_terminal(
    command='cat << "EOF"\n`████░░░░░░` 40% Working...\nEOF'
)
```

**Fix:** Write directly in markdown response
```markdown
<hr>
📋 **Task Name**
`████░░░░░░` 40% Working...
<hr>
```

### Mistake 2: Status Messages in Terminal
```python
# ❌ WRONG
run_in_terminal(
    command='echo "✅ Complete"'
)
```

**Fix:** Include in chat response
```markdown
<hr>
✅ **COMPLETE**
Details here
<hr>
```

### Mistake 3: Tables in Terminal
```python
# ❌ WRONG
run_in_terminal(
    command='cat << "EOF"\n| Col | Val |\n|-----|-----|\nEOF'
)
```

**Fix:** Use markdown tables in chat
```markdown
| Col | Val |
|-----|-----|
| A | 1 |
```

---

## ✅ Correct Implementation Example

**Scenario:** Multi-stage phase execution

**Response:**
```markdown
## ⚡ CORTEX IMPLEMENT

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Phase 47 Stage 2: Memory Tier Rename
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████░░░░░░] 40% Stage 2 In Progress

├─ ✅ S1: Brain Architecture (20 tests)
├─ 🔵 S2: Memory Tier Rename (in progress)
├─ ⚪ S3: Integration Tests (pending)
└─ ⚪ S4: Cleanup (pending)

<hr>
```

**Then run actual commands:**
```python
run_in_terminal(
    command='mv cortex_intelligence/memory/tier1_learned cortex_intelligence/memory/learned_patterns',
    explanation="Renaming memory directory",
    isBackground=False
)

run_in_terminal(
    command='python3 -m pytest tests/unit/brain/core/test_memory_tier_paths.py -v',
    explanation="Running memory tier tests",
    isBackground=False
)
```

**Then show results in chat:**
```markdown
<hr>

✅ **STAGE 2 COMPLETE**

**Duration:** 45 minutes  
**Tests:** 10/19 passing (9 skipped)

### Changes
- ✅ Directories renamed
- ✅ Symlinks created
- ✅ Tests passing

<hr>
```

---

## 📝 Summary

| Principle | Implementation |
|-----------|----------------|
| User feedback | → Chat (markdown) |
| Command output | → Terminal (`run_in_terminal`) |
| Progress bars | → Chat (markdown) |
| Status updates | → Chat (markdown) |
| Test results | → Chat (markdown table) |
| Long commands | → Terminal (actual execution) |

**Golden Rule:** If the user needs to **see it immediately**, put it in **chat**. If it's **command output**, run in **terminal**.
