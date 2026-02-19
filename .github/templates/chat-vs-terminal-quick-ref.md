# 🎯 Chat vs Terminal Quick Reference

**CRITICAL RULE:** Progress bars and status updates go in **Chat**, not Terminal!

---

## ✅ DO: Display in Chat Session

**SSOT:** `.github/templates/cortex-response-templates.md` § Silent Autonomous Mode — Golden Template

Output the golden template **directly as live markdown** in your chat response. Do NOT wrap it in a fenced code block — that converts it to preformatted text and breaks rendering.

**Write directly in markdown response body!**

---

## ❌ DON'T: Use Terminal for UI

```python
# ❌ WRONG - Progress bars should NOT go to terminal
run_in_terminal(
    command='cat << "EOF"\n`████░░░░░░` 40% Working...\nEOF'
)

# ❌ WRONG - Status should NOT go to terminal  
run_in_terminal(
    command='echo "✅ Complete"'
)
```

---

## ✅ DO: Use Terminal for Commands

```python
# ✅ CORRECT - Actual work commands
run_in_terminal(
    command='pytest tests/unit/brain/core/test_*.py -v',
    explanation="Running tests",
    isBackground=False
)

# ✅ CORRECT - File operations
run_in_terminal(
    command='mv old_dir new_dir',
    explanation="Renaming directory",
    isBackground=False
)
```

---

## 📋 Decision Tree

**Is this user-facing feedback?**

- **YES** → Put in **CHAT** (markdown)
  - Progress bar
  - Status update
  - Results table
  - Completion summary

- **NO** → Is this a command?
  - **YES** → Run in **TERMINAL**
    - pytest
    - git
    - mv/cp/mkdir
    - Long-running builds

---

## 🔧 Template Reference

**SSOT:** `.github/templates/cortex-response-templates.md` § Silent Autonomous Mode — Golden Template

> Output the golden template **directly as live markdown** — never inside a fenced code block.
> Stage status uses bullet lists (`- ✅ S1: ...`), NOT `├─ └─` tree characters.
> Then run actual commands via `run_in_terminal`.

---

**Full Guide:** `.github/templates/chat-vs-terminal-guide.md`
