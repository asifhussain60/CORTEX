# 🎯 Chat vs Terminal Quick Reference

**CRITICAL RULE:** Progress bars and status updates go in **Chat**, not Terminal!

---

## ✅ DO: Display in Chat Session

```markdown
<hr>

📋 **Phase 47 Stage 2: Memory Tier Clarification**

`████████░░` 80% Implementing GREEN phase

| # | Status | Task | Tests |
|---|--------|------|-------|
| 1 | ✅ | Rename dirs | 6/6 |
| 2 | 🔵 | Update paths | 4/10 |

<hr>
```

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

```
Is this user-facing feedback?
├─ YES → Put in CHAT (markdown)
│   ├─ Progress bar
│   ├─ Status update
│   ├─ Results table
│   └─ Completion summary
│
└─ NO → Is this a command?
    └─ YES → Run in TERMINAL
        ├─ pytest
        ├─ git
        ├─ mv/cp/mkdir
        └─ Long-running builds
```

---

## 🔧 Template

```markdown
## ⚡ CORTEX IMPLEMENT

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {PHASE_NAME} Stage {N}: {STAGE_TITLE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[██████████] 100% All Stages Complete

├─ ✅ S1: {name} ({n} tests)
└─ ✅ S2: {name} ({n} tests)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then run commands:
```python
run_in_terminal(command='actual work here')
```

Then show results:
```markdown
<hr>

✅ **COMPLETE**

| Metric | Value |
|--------|-------|
| Tests | 45/45 |

<hr>
```

---

**Full Guide:** `.github/templates/chat-vs-terminal-guide.md`
