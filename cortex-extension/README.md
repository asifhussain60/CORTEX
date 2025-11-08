# CORTEX VS Code Extension

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

## Overview

CORTEX is a VS Code extension that provides persistent memory and context awareness for AI-assisted development. Unlike traditional AI assistants that forget conversations, CORTEX remembers everything and helps you resume work seamlessly.

## Features

### 🧠 Persistent Memory
- **Zero Amnesia**: CORTEX never forgets your conversations
- **Automatic Capture**: All @cortex chats are automatically saved to the brain
- **Cross-Session Context**: Resume work exactly where you left off

### 💬 @cortex Chat Participant
- Type `@cortex` in VS Code chat to interact
- Built-in commands:
  - `/resume` - Resume your last conversation
  - `/checkpoint` - Save current conversation state
  - `/history` - View conversation history
  - `/optimize` - Optimize token usage

### 📊 Token Dashboard
- Real-time token usage tracking
- Cache health monitoring
- ML-powered optimization metrics
- One-click token optimization

### 🔄 Lifecycle Management
- **Auto-Checkpoint**: Saves state when you lose focus
- **Resume Prompts**: Offers to resume after breaks
- **Crash Recovery**: Never lose work again

### 🎯 External Monitoring
- Monitor GitHub Copilot conversations (optional)
- Unified conversation timeline
- Context injection from all sources

## Installation & Setup

### Step 1: Install Extension
1. Locate `cortex-1.0.0.vsix` in the `cortex-extension` directory
2. Open terminal in that directory
3. Run:
   ```bash
   code --install-extension cortex-1.0.0.vsix
   ```

### Step 2: Configure CORTEX Brain Connection
1. Open VS Code Settings: `Ctrl+,`
2. Search for "cortex"
3. Set **CORTEX: Cortex Root** to your CORTEX installation path
   - Example: `D:\PROJECTS\CORTEX`
4. (Optional) Set **CORTEX: Python Path** if not auto-detected
   - Example: `python` or `C:\Python311\python.exe`

### Step 3: Reload VS Code
- Press `Ctrl+Shift+P`
- Type "Developer: Reload Window"
- Press Enter

### Step 4: Verify Connection
1. Open GitHub Copilot Chat (View → Open View → Chat)
2. Type: `@cortex hello`
3. You should see:
   - ✅ **Status:** Connected to CORTEX Brain (Online Mode)
   - All features enabled

**If you see "Offline Mode":** Check your `cortex.cortexRoot` setting and ensure Python is installed.

## Configuration

### Required Setup
1. **Python Path**: Set `cortex.pythonPath` if Python is not in PATH
2. **CORTEX Root**: Set `cortex.cortexRoot` to your CORTEX installation directory

### Optional Settings
- `cortex.autoCapture`: Auto-capture conversations (default: true)
- `cortex.monitorCopilot`: Monitor Copilot chats (default: true)
- `cortex.autoCheckpoint`: Auto-checkpoint on focus loss (default: true)
- `cortex.resumePrompt`: Show resume prompts (default: true)
- `cortex.tokenOptimization`: Enable ML token optimization (default: true)
- `cortex.tokenDashboard.refreshInterval`: Dashboard refresh interval in seconds (default: 10)

## How to Use

### Check Connection Status
Type `@cortex hello` to see your connection status:
- ✅ **Online Mode**: Connected to CORTEX Brain with full features
- ⚠️  **Offline Mode**: Basic chat only (configure brain connection in settings)

### Basic Chat
```
@cortex how do I refactor this code?
```
CORTEX processes your request using the full brain (Tier 1/2/3 integration).

### Commands

#### Resume Last Conversation
```
@cortex /resume
```
Resumes your last conversation with full context from brain memory.

#### Create Checkpoint
```
@cortex /checkpoint
```
Saves current conversation state (also auto-saves on window focus loss).

#### View History
```
@cortex /history
```
Shows your recent conversations from brain database.

#### Optimize Tokens
```
@cortex /optimize
```
Runs ML-powered token optimization.

#### Give Instructions
```
@cortex /instruct Always use TypeScript strict mode
```
Saves instructions to CORTEX instinct layer for all future interactions.

## Architecture

### Components
- **BrainBridge**: Python ↔ TypeScript communication via HTTP
- **ChatParticipant**: @cortex handler
- **TokenDashboard**: Real-time metrics UI
- **LifecycleManager**: Window state monitoring
- **CheckpointManager**: Conversation state persistence
- **ExternalMonitor**: Copilot chat monitoring

### Data Flow
```
User → @cortex Chat → ChatParticipant → BrainBridge → Python API → CORTEX Brain (Tier 1/2/3)
                                                                    ↓
                                                              Token Metrics
                                                                    ↓
                                                           Token Dashboard UI
```

## Development

### Build
```bash
npm install
npm run compile
```

### Watch Mode
```bash
npm run watch
```

### Run Tests
```bash
npm test
```

### Package Extension
```bash
npm run package
```

### Publish to Marketplace
```bash
npm run publish
```

## Troubleshooting

### "I can't see @cortex in chat"
**Check:**
- Is the extension installed? Run: `code --list-extensions | Select-String cortex`
- Did you reload VS Code after installation?
- Are you in the correct window?
  - **Development mode**: Must be in the "[Extension Development Host]" window
  - **Installed mode**: Should work in any window

**Fix:**
1. Reinstall: `code --install-extension cortex-1.0.0.vsix`
2. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"

### Extension shows "offline mode" warning
**Cause:** Python bridge couldn't connect to CORTEX brain

**Fix:**
1. Check Python is installed: `python --version`
2. Set Python path in VS Code settings:
   - `Ctrl+,` → Search "cortex python"
   - Set `cortex.pythonPath` if needed
3. Set CORTEX root directory:
   - Set `cortex.cortexRoot` to your CORTEX installation path (e.g., `D:\PROJECTS\CORTEX`)
4. Reload VS Code

### Extension won't activate
**Check:**
- View → Output → Select "Extension Host" to see error logs
- Try uninstalling and reinstalling the extension

### Python bridge fails to start
**Check:**
- Python dependencies installed? Run: `pip install -r requirements.txt` in CORTEX root
- Port 5555 not in use? Run: `netstat -ano | findstr :5555`
- CORTEX_ROOT environment variable set?

## Roadmap

### Phase 3 (Current) - Week 11-16
- ✅ Extension scaffold complete
- 🔄 Chat participant implementation
- 🔄 Token dashboard integration
- 📋 Lifecycle hooks
- 📋 External monitoring
- 📋 Proactive resume system

### Phase 4 - Week 17-18
- Comprehensive testing
- Performance optimization
- Stability improvements

### Phase 7 - Week 23-24
- Marketplace publication
- General availability release

## License

Copyright © 2024-2025 Asif Hussain. All rights reserved.

This software is proprietary. See LICENSE file for terms.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Contact: asifhussain60@gmail.com

## Acknowledgments

Built with ❤️ by Asif Hussain as part of the CORTEX Cognitive Development System.
