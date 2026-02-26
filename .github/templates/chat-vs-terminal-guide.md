# Chat Session vs Terminal Output Guide

**Authority:** CORE-049 + Response Format Standards  
**Updated:** 2026-02-18

## 🎯 Core Principle

**All user-facing feedback goes to Chat Session. Only long-running processes go to terminal.**

---

## ✅ CORRECT: Display in Chat Session

### Progress Bars & Stage Lists

**SSOT:** `.github/templates/cortex-response-templates.md` § Silent Autonomous Mode — Golden Template

**Output the golden template directly in the chat markdown response** — NOT inside a fenced code block, NOT via `run_in_terminal`. The `━━━` separators, `[██████████]` progress bar, and stage bullet list must render as live markdown characters in the chat panel.

**Implementation:**
- Write the template content directly in your markdown response (no surrounding backticks)
- NO `run_in_terminal` with `cat` or `echo`
- Renders inline in Chat Session as formatted text

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
    command='python3 scripts/run_tests.py smoke',
    explanation="Running smoke tests (< 60 seconds)",
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

## 🎨 Progress Bar & Stage List Implementation

**SSOT:** `.github/templates/cortex-response-templates.md` § Silent Autonomous Mode — Golden Template

> ⚠️ **Do NOT define a progress template here.** The ONLY correct format is the golden template in the SSOT above. Output it **directly** in the chat markdown response — never inside a fenced code block, never via `run_in_terminal`.

---

## 🔧 Implementation Checklist

### Before Writing Response

- [ ] Is this user-facing feedback? → **Chat** (write as live markdown)
- [ ] Is this a long-running command? → **Terminal** (`run_in_terminal`)
- [ ] Is this progress/stage update? → **Chat** (use SSOT golden template directly)
- [ ] Is this command output? → **Terminal**

### Key Points

1. **Header once** at top (per prompt standards)
2. **Progress in chat** using the SSOT golden template (`━━━` + bar + bullet list) written directly as markdown
3. **Commands in terminal** using `run_in_terminal`
4. **Results in chat** using markdown tables
5. **Never wrap** the golden template in a fenced code block — that makes it render as preformatted text

---

## 📊 Decision Matrix

| Content Type | Location | Format |
|--------------|----------|--------|
| Progress bar + stage list | Chat | SSOT golden template (live markdown) |
| Status update | Chat | Markdown text |
| Stage completion | Chat | SSOT completion template (live markdown) |
| Test command | Terminal | `run_in_terminal` |
| Build command | Terminal | `run_in_terminal` |
| Git command | Terminal | `run_in_terminal` |
| File operation | Terminal | `run_in_terminal` |
| Summary table | Chat | Markdown table |

---

## 🐛 Common Mistakes

### Mistake 1: Progress Bars in Terminal
```python
# ❌ WRONG — progress bars should NOT go to terminal
run_in_terminal(command='cat << "EOF"\n`████░░░░░░` 40% Working...\nEOF')
```
**Fix:** Write the SSOT golden template directly in your chat response.

### Mistake 2: Wrapping golden template in a fenced code block
```
# ❌ WRONG — fenced block causes raw preformatted text, not rendered markdown
\`\`\`
---
📋 Phase N Stage N: Title
...
\`\`\`
```
**Fix:** Output the `---` separator, progress bar, and stage bullet list **directly** in your markdown — no surrounding backticks.

### Mistake 3: Using long horizontal lines that wrap badly
```
# ❌ WRONG — long lines wrap and break on narrow panels
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Phase Title
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
**Fix:** Use `---` (standard Markdown HR) and bold titles — never long `━` lines.

---

## 📝 Summary

| Principle | Implementation |
|-----------|----------------|
| User feedback | → Chat (live markdown) |
| Command output | → Terminal (`run_in_terminal`) |
| Progress/stage updates | → Chat (SSOT golden template, no code block) |
| Test results | → Chat (markdown table) |
| Long commands | → Terminal (actual execution) |

**Golden Rule:** If the user needs to **see it**, put it in **chat as live markdown**. If it's a **command to run**, use `run_in_terminal`.

**Template Reference:** `.github/templates/cortex-response-templates.md` § Silent Autonomous Mode — Golden Template
