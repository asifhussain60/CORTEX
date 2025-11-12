# CORTEX Command Quick Reference

**Fast reference for CORTEX slash commands**

## 💬 Remember: Natural Language Works Everywhere!

Commands are **optional shortcuts**. You can always use natural language:
- "switched to mac" = `/mac`
- "setup environment" = `/setup`
- "show progress" = `/status`

---

# CORTEX Command Quick Reference

**Fast reference for CORTEX slash commands**

## 💬 Remember: Natural Language Works Everywhere!

Commands are **optional shortcuts**. You can always use natural language:
- "setup environment" = `/setup`
- "show progress" = `/status`

---

## ⚡ Platform & Environment

| Command | Aliases | Natural Language | What It Does |
|---------|---------|------------------|--------------|
| `/setup` | `/env`, `/environment`, `/configure` | "setup environment" | Setup/configure environment (auto-detects Mac/Windows/Linux) |

**Note:** Platform detection is **automatic**! CORTEX detects Mac/Windows/Linux on startup and auto-configures when you switch machines.

**What happens:**
1. ✅ Auto-detect current platform
2. ✅ Git pull latest code
3. ✅ Configure platform-specific environment
4. ✅ Quick dependency check
5. ✅ Validate tooling

---

## 💾 Session Commands

| Command | Aliases | Natural Language | What It Does |
|---------|---------|------------------|--------------|
| `/resume` | `/continue` | "resume work" | Resume from where you left off |
| `/status` | `/progress` | "show progress" | Show current work status |
| `/help` | `/h`, `/?` | "show available commands" | Display all commands |

---

## 🔧 VS Code Extension Only

**Use in VS Code Chat (`@cortex`):**

| Command | What It Does |
|---------|--------------|
| `/resume` | Resume last conversation |
| `/checkpoint` | Save conversation state |
| `/history` | View conversation history |
| `/optimize` | Optimize token usage |
| `/instruct` | Give CORTEX new instructions |

---

## 📚 Documentation Access

| What to Load | Command |
|--------------|---------|
| Story | `#file:prompts/shared/story.md` |
| Setup Guide | `#file:prompts/shared/setup-guide.md` |
| Technical Docs | `#file:prompts/shared/technical-reference.md` |
| Agent Guide | `#file:prompts/shared/agents-guide.md` |
| Tracking Guide | `#file:prompts/shared/tracking-guide.md` |

---

## 🎯 Usage Examples

### Quick Setup
```markdown
#file:prompts/user/cortex.md

/setup
```

### Natural Language (Same Result)
```markdown
#file:prompts/user/cortex.md

setup environment
```

### VS Code Extension
```
@cortex /setup
@cortex /resume
@cortex /help
```

### Automatic Detection (No Command Needed!)
```
# Just open CORTEX on a different machine
# Platform change is detected automatically
# Auto-configuration runs in background
```

---

## 💡 Tips

### When to Use Commands
- ✅ Quick, single actions
- ✅ You know exactly what you want
- ✅ Muscle memory (power users)

### When to Use Natural Language
- ✅ Complex requests
- ✅ Multiple actions
- ✅ Adding context
- ✅ You're unsure
- ✅ First time using CORTEX

### Best Practice
**Mix both!** Use commands for speed, natural language for precision.

---

## 🆘 Getting Help

### Show All Commands
```markdown
@cortex /help
```

### Show This File
```markdown
#file:docs/COMMAND-QUICK-REFERENCE.md
```

### Full Documentation
```markdown
#file:docs/plugins/command-system.md
```

---

## 🔌 For Plugin Developers

Want to add your own commands?

1. Override `register_commands()` in your plugin
2. Return list of `CommandMetadata` objects
3. Commands auto-register on init

See: `docs/plugins/command-system.md` for full guide

---

**Version:** 1.0  
**Date:** November 9, 2025  
**Author:** Asif Hussain
