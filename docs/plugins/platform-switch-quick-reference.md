# Platform Switch Plugin - Quick Reference

**Version:** 1.0.0  
**Plugin Type:** Pre-Execution  
**File:** `src/plugins/platform_switch_plugin.py`

---

## ⚡ Quick Commands

```markdown
#file:prompts/user/cortex.md

switched to mac
```

```markdown
#file:prompts/user/cortex.md

working on windows
```

```markdown
#file:prompts/user/cortex.md

using linux
```

---

## 🔄 What Happens Automatically

### 1. Git Pull (5-30 sec)
- Detects current branch
- Pulls latest changes from origin
- Reports files changed

### 2. Environment Setup (1-5 sec)
- Detects Python version
- Creates/verifies virtual environment
- Configures platform-specific paths

### 3. Dependencies (5-15 sec)
- Checks installed packages
- Installs missing:
  - pytest, pytest-cov
  - PyYAML
  - numpy, scikit-learn
  - watchdog
  - mkdocs, mkdocs-material
  - black, flake8, mypy

### 4. Brain Tests (1-2 sec)
- Runs 82 tests across all tiers
- Validates path compatibility
- Reports pass/fail

### 5. Tooling (1-2 sec)
- Verifies Git
- Verifies Python
- Checks platform tools

**Total Time:** ~15-60 seconds

---

## ✅ Success Output

```
🔄 Platform Switch: Configuring for macOS
============================================================
✅ Git Pull: SUCCESS (454 files changed)
✅ Environment Configuration: SUCCESS
✅ Dependency Verification: SUCCESS
✅ Brain Tests: SUCCESS (82 passed, 0 failed)
✅ Tooling Verification: SUCCESS
============================================================
✅ macOS environment is ready!
   All systems operational for CORTEX 2.0
============================================================
```

---

## ❌ Common Errors

### "Git pull failed"
**Cause:** Network issue or not in git repo  
**Fix:** Check internet connection

### "Virtual environment creation failed"
**Cause:** Python not found or permissions issue  
**Fix:** Ensure Python 3.9+ installed

### "Tests failed"
**Cause:** Missing dependencies or platform incompatibility  
**Fix:** Check test output, reinstall dependencies

### "Tooling not found"
**Cause:** Git or Python not in PATH  
**Fix:** Install missing tool, add to PATH

---

## 🎯 Platform Differences

| Feature | macOS | Windows | Linux |
|---------|-------|---------|-------|
| Path Sep | `/` | `\` | `/` |
| Python | `python3` | `python` | `python3` |
| Shell | zsh | PowerShell | bash |
| Venv Path | `.venv/bin/python` | `.venv\Scripts\python.exe` | `.venv/bin/python` |
| Line End | LF | CRLF | LF |

---

## 📦 Required Software

### All Platforms
- Git 2.0+
- Python 3.9+
- Internet connection

### Platform-Specific
- **macOS:** Homebrew (optional)
- **Windows:** PowerShell 5.0+
- **Linux:** bash

---

## 🧪 Testing

Run plugin tests:
```bash
pytest tests/plugins/test_platform_switch_plugin.py -v
```

### Test Coverage
- ✅ Platform detection
- ✅ Trigger matching
- ✅ Git operations
- ✅ Environment config
- ✅ Dependency verification
- ✅ Test execution
- ✅ Tool verification

---

## 📚 Full Documentation

See: `docs/plugins/platform-switch-plugin.md`

---

## 🔧 Troubleshooting

### Check Plugin Registration
```python
from src.plugins.platform_switch_plugin import register
plugin = register()
print(plugin.metadata.triggers)
```

### Manual Execution
```python
from src.plugins.platform_switch_plugin import PlatformSwitchPlugin

plugin = PlatformSwitchPlugin()
result = plugin.execute("switched to mac")
print(result["summary"])
```

### Verify Platform Detection
```python
from src.plugins.platform_switch_plugin import Platform

print(f"Current: {Platform.current().display_name}")
```

---

## 🚀 Integration

### With CORTEX Entry Point

Automatically triggered by:
- "switched to mac/windows/linux"
- "working on mac/windows/linux"
- "using mac/windows/linux"
- "setup environment"
- "configure platform"

### Manual Trigger

```python
# In cortex_entry.py
from src.plugins.platform_switch_plugin import PlatformSwitchPlugin

plugin = PlatformSwitchPlugin()
if plugin.can_handle(user_request):
    result = plugin.execute(user_request)
```

---

## 💡 Tips

1. **First time on new machine:** Run platform switch immediately
2. **After OS update:** Re-run to verify tooling
3. **Before major work:** Ensure tests pass on your platform
4. **Switching machines:** Single command sets up everything

---

## 📊 Performance

**Typical execution times:**
- Fast: 15-20 seconds (no installs, already updated)
- Medium: 30-45 seconds (few packages to install)
- Slow: 45-60 seconds (many packages, large git pull)

**Optimization tips:**
- Keep dependencies updated manually
- Pull code separately if working offline
- Use fast internet connection for installs

---

## 🔐 Security

- ✅ No credentials stored
- ✅ Validates project directory
- ✅ Subprocess timeout protection
- ✅ No shell injection vulnerabilities
- ✅ Read-only operations except venv/pip

---

**Created:** November 9, 2025  
**Status:** Production Ready ✅  
**Last Tested:** macOS (82/82 tests passing)
