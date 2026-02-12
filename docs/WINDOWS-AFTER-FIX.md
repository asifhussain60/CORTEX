# What Happens on Windows After This Fix

## Current State (BEFORE git pull)
- Windows machine has `.vscode/settings.json` with: `Scripts/python.exe`
- MCP works fine on Windows

## After git pull (AUTOMATIC FIX)

### Step 1: Git Pull
```powershell
PS C:\Users\...\CORTEX> git pull origin CORTEX
```

### Step 2: Post-Checkout Hook Runs Automatically
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 CORTEX Post-Checkout: MCP Environment Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Regenerating platform-specific MCP configuration...
✅ CORTEX MCP server: Configured (platform-specific paths)
✅ Virtual environment: Ready
✅ MCP Environment: CORTEX-only policy enforced
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: `.vscode/settings.json` Regenerated
**Automatically created with Windows paths:**
```jsonc
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "${workspaceFolder}/.venv/Scripts/python.exe",  // ✅ Windows path
      "args": ["-m", "cortex.mcp"],
      "env": {
        "CORTEX_ENV": "development",
        "CORTEX_MCP_ENABLED": "true",
        "PYTHONPATH": "${workspaceFolder}",
        "CORTEX_WORKSPACE": "${workspaceFolder}"
      }
    }
  }
}
```

### Step 4: Reload VS Code
1. Open VS Code
2. Command Palette → **Developer: Reload Window**
3. MCP tools available again!

## Result
✅ Windows continues to work (no breakage)
✅ Mac continues to work (no breakage)
✅ No manual intervention needed
✅ Each platform has correct paths

## Git Status on Windows (After Pull)
```powershell
PS C:\Users\...\CORTEX> git status
On branch CORTEX
Your branch is up to date with 'origin/CORTEX'.

nothing to commit, working tree clean
```

**Why clean?** `.vscode/settings.json` is NOT tracked in git anymore, so changes to it don't show in `git status`.

## Verification on Windows
```powershell
# Check settings.json has Windows paths
PS C:\Users\...\CORTEX> Select-String -Path .vscode\settings.json -Pattern "command"

# Should show:
# "command": "${workspaceFolder}/.venv/Scripts/python.exe"
```

## Summary
**No action required on Windows!**
The fix is designed to work automatically on both platforms.

---

**Authority:** Phase 53 (Cross-Platform MCP)  
**Date:** 2026-02-12
