# CORTEX Extension Installation Guide

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

## 📦 Extension Package Location

The CORTEX extension has been compiled and packaged at:

```
d:\PROJECTS\CORTEX\cortex-extension\cortex-1.0.0.vsix
```

## 🔧 Installation Steps

### Step 1: Install Python Dependencies

The extension requires Flask to run the Python bridge server:

```powershell
# Navigate to CORTEX root
cd d:\PROJECTS\CORTEX

# Install Flask (if not already installed)
pip install flask flask-cors
```

### Step 2: Set Environment Variables (Optional but Recommended)

Set the CORTEX_ROOT environment variable for automatic detection:

```powershell
# Set for current user (run in PowerShell as Administrator)
[Environment]::SetEnvironmentVariable("CORTEX_ROOT", "D:\PROJECTS\CORTEX", "User")

# Restart VS Code after setting environment variables
```

### Step 3: Install the Extension

**Option A: Install via VS Code UI (Recommended)**

1. Open VS Code
2. Press `Ctrl+Shift+X` to open Extensions view
3. Click the `...` menu (three dots) at the top right
4. Select `Install from VSIX...`
5. Navigate to: `d:\PROJECTS\CORTEX\cortex-extension\cortex-1.0.0.vsix`
6. Click `Install`
7. **Reload VS Code** when prompted

**Option B: Install via Command Line**

```powershell
# Install using code command
code --install-extension d:\PROJECTS\CORTEX\cortex-extension\cortex-1.0.0.vsix

# Reload VS Code after installation
```

### Step 4: Configure Extension Settings (Optional)

Open VS Code Settings (`Ctrl+,`) and configure:

```json
{
  "cortex.cortexRoot": "D:\\PROJECTS\\CORTEX",
  "cortex.pythonPath": "python",  // or full path to python.exe
  "cortex.autoCapture": true,
  "cortex.monitorCopilot": true,
  "cortex.resumePrompt": true
}
```

If you set `CORTEX_ROOT` environment variable in Step 2, you can skip `cortex.cortexRoot`.

### Step 5: Verify Installation

1. **Check Extension is Active:**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Type "CORTEX"
   - You should see commands like:
     - `CORTEX: Resume Last Conversation`
     - `CORTEX: Save Checkpoint`
     - `CORTEX: Show Conversation History`

2. **Test Chat Participant:**
   - Open GitHub Copilot Chat panel
   - Type: `@cortex hello`
   - You should see CORTEX respond with connection status

3. **Check Output Panel:**
   - Open Output panel (`Ctrl+Shift+U`)
   - Select "CORTEX" from dropdown
   - Should see: `✅ CORTEX Brain Bridge connected!`

## 🧠 How It Works

### Architecture

```
VS Code Extension (TypeScript)
    ↓
    HTTP (localhost:5555)
    ↓
Python Bridge Server (bridge_server.py)
    ↓
CORTEX 2.0 Brain (src/)
    ├── Tier 1: Working Memory
    ├── Tier 2: Knowledge Graph
    └── Tier 3: Context Intelligence
```

### Folder Structure

```
d:\PROJECTS\CORTEX\
├── cortex-extension\              # VS Code Extension
│   ├── src\                       # TypeScript source
│   │   ├── extension.ts           # Main entry point
│   │   └── cortex\
│   │       ├── brainBridge.ts     # Python bridge client
│   │       ├── chatParticipant.ts # @cortex handler
│   │       └── ...
│   ├── python\
│   │   └── bridge_server.py       # HTTP server for brain
│   ├── out\                       # Compiled JavaScript
│   └── cortex-1.0.0.vsix         # Packaged extension
│
└── src\                           # CORTEX 2.0 Brain
    ├── tier1\                     # Working Memory
    ├── tier2\                     # Knowledge Graph
    ├── tier3\                     # Context Intelligence
    └── entry_point\               # CORTEX Entry
```

## 🎯 Using the Extension

### Basic Usage

**In Chat Panel:**

```
@cortex hello
@cortex /resume
@cortex /checkpoint
@cortex /history
@cortex /optimize
@cortex /instruct Always use TypeScript strict mode
```

**Via Commands (Ctrl+Shift+P):**

- `CORTEX: Resume Last Conversation`
- `CORTEX: Save Checkpoint`
- `CORTEX: Show Conversation History`
- `CORTEX: Optimize Token Usage`
- `CORTEX: Show Token Dashboard`
- `CORTEX: Clear Conversation Cache`

### Automatic Features

Once installed, CORTEX automatically:
- ✅ Captures all `@cortex` conversations to Tier 1
- ✅ Monitors external `@copilot` chats (if enabled)
- ✅ Creates checkpoints when VS Code loses focus
- ✅ Offers to resume on startup (if configured)
- ✅ Tracks token usage in real-time

## 🔍 Troubleshooting

### Extension Not Activating

1. Check extension is installed:
   ```powershell
   code --list-extensions | Select-String cortex
   ```

2. Check VS Code version:
   ```
   Required: VS Code 1.95.0 or higher
   ```

### Brain Bridge Not Connecting

1. Check Python is installed:
   ```powershell
   python --version
   # Should output: Python 3.8 or higher
   ```

2. Check Flask is installed:
   ```powershell
   python -c "import flask; print(flask.__version__)"
   ```

3. Check CORTEX_ROOT environment variable:
   ```powershell
   $env:CORTEX_ROOT
   # Should output: D:\PROJECTS\CORTEX
   ```

4. Check bridge server logs in VS Code Output panel (`Ctrl+Shift+U` → select "CORTEX")

### Chat Participant Not Appearing

1. Reload VS Code window:
   - `Ctrl+Shift+P` → `Developer: Reload Window`

2. Check if GitHub Copilot Chat is enabled:
   - Extension must be activated for chat participants to work

3. Check extension output for errors:
   - View → Output → select "CORTEX"

## 🔄 Rebuilding the Extension

If you make changes to the extension code:

```powershell
cd d:\PROJECTS\CORTEX\cortex-extension

# 1. Compile TypeScript
npm run compile

# 2. Package extension
npm run package

# 3. Uninstall old version
code --uninstall-extension cortex-team.cortex

# 4. Install new version
code --install-extension cortex-1.0.0.vsix

# 5. Reload VS Code
# Ctrl+Shift+P → Developer: Reload Window
```

## 📝 Notes

- **Offline Mode:** If brain bridge fails to connect, extension runs in offline mode (limited features)
- **Port Conflicts:** If port 5555 is in use, bridge server will fail. Close other applications using that port.
- **Python Path:** Extension auto-detects Python, but you can specify exact path in settings
- **Cross-Platform:** Extension works on Windows, macOS, and Linux with appropriate paths

## 🆘 Support

If you encounter issues:

1. Check Output panel for error messages
2. Check Python bridge server is running (Task Manager → python.exe)
3. Verify Flask is installed: `pip list | Select-String flask`
4. Check CORTEX root is correct: `Test-Path "D:\PROJECTS\CORTEX\src"`

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ Extension shows in Extensions list
2. ✅ `@cortex hello` responds in chat
3. ✅ Output shows: `✅ CORTEX Brain Bridge connected!`
4. ✅ Commands appear in Command Palette
5. ✅ Resume prompt appears on startup (if enabled)

---

**Installation Complete!** You can now use `@cortex` in VS Code Chat with full brain integration.
