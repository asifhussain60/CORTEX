# CORTEX Extension - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install the Extension
```powershell
# Navigate to cortex-extension directory
cd D:\PROJECTS\CORTEX\cortex-extension

# Install the extension
code --install-extension cortex-1.0.0.vsix
```

### Step 2: Configure Brain Connection
1. Open VS Code Settings: `Ctrl+,`
2. Search for "cortex"
3. Set **CORTEX: Cortex Root** = `D:\PROJECTS\CORTEX`
4. (Optional) Set **CORTEX: Python Path** if not auto-detected

### Step 3: Reload VS Code
- Press `Ctrl+Shift+P`
- Type "Developer: Reload Window"
- Press Enter

### Step 4: Verify Brain Connection
1. Open GitHub Copilot Chat (View → Open View → Chat)
2. Type: `@cortex hello`
3. You should see:

```
🧠 CORTEX activated!

✅ Status: Connected to CORTEX Brain (Online Mode)
- Persistent memory: ✅ Active
- Tier 1/2/3 integration: ✅ Connected
- Auto-capture: ✅ Enabled
```

---

## ✅ You're Connected!

CORTEX is now connected to the full brain system with:
- ✅ **Persistent Memory** - Never forgets conversations
- ✅ **All Commands** - `/resume`, `/checkpoint`, `/history`, `/optimize`, `/instruct`
- ✅ **Auto-Capture** - All chats saved to brain database
- ✅ **Token Optimization** - ML-powered efficiency

---

## 💡 Common Commands

Try these in chat:

```
@cortex /resume       # Resume last conversation with full context
@cortex /checkpoint   # Save conversation state
@cortex /history      # View conversation history
@cortex /optimize     # Optimize token usage
@cortex /instruct Use Python type hints everywhere
                      # Give permanent instructions
```

---

## ⚠️ Offline Mode?

If you see "Offline Mode" instead of "Connected":

### Fix 1: Check Settings
```
Ctrl+, → Search "cortex"
Verify: cortex.cortexRoot = D:\PROJECTS\CORTEX
```

### Fix 2: Check Python
```powershell
python --version    # Should show Python 3.x
```

### Fix 3: Reload VS Code
```
Ctrl+Shift+P → "Developer: Reload Window"
```

---

## 🐛 Troubleshooting

### Can't see @cortex in chat?
```powershell
# Check if installed
code --list-extensions | Select-String cortex

# Reinstall if needed
code --install-extension cortex-1.0.0.vsix
```

### Extension shows "Offline Mode"?
- Verify `cortex.cortexRoot` is set correctly in settings
- Ensure Python is installed: `python --version`
- Check CORTEX root directory exists
- Reload VS Code

### Commands not working?
- Only work in **Online Mode** (brain connected)
- Check connection status: `@cortex hello`
- See setup steps above to enable brain connection

---

## 📚 Learn More

- Full documentation: See `README.md`
- Architecture: See `docs/architecture/`
- Development: See `NEXT-STEPS.md`
