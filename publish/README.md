# CORTEX Deployment Package

**Version:** 5.2.0  
**Package Date:** 2025-11-12  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 📦 Package Contents

This directory contains a production-ready CORTEX deployment package.

```
publish/
├── CORTEX/                    # Complete CORTEX system (copy this folder to target machine)
│   ├── .github/
│   │   ├── prompts/
│   │   │   └── CORTEX.prompt.md       # Main entry point (/CORTEX command)
│   │   └── copilot-instructions.md    # Baseline context for all chats
│   ├── cortex-brain/                  # Cognitive storage (Tier 0-3)
│   ├── prompts/                       # Modular documentation
│   ├── src/                           # Python source code
│   ├── scripts/                       # Automation tools
│   ├── requirements.txt               # Python dependencies
│   ├── setup.py                       # Package installer
│   ├── pytest.ini                     # Test configuration
│   ├── README.md                      # Main documentation
│   └── LICENSE                        # License file
│
├── SETUP-CORTEX.md            # Installation guide for GitHub Copilot
└── README.md                  # This file

```

---

## 🚀 Installation

### For GitHub Copilot (Recommended)

1. **Copy this folder to target machine**
2. **Open `SETUP-CORTEX.md` in VS Code**
3. **Open GitHub Copilot Chat**
4. **Reference the setup file:**
   ```
   @workspace #file:SETUP-CORTEX.md please install CORTEX following these instructions
   ```
5. **Copilot will execute all installation steps automatically**

### For Manual Installation

1. **Copy CORTEX folder to target location:**
   ```powershell
   # Windows
   Copy-Item -Path "CORTEX" -Destination "C:\Users\<username>\CORTEX" -Recurse
   
   # macOS/Linux
   cp -r CORTEX ~/CORTEX
   ```

2. **Navigate to installation directory:**
   ```bash
   cd ~/CORTEX  # or C:\Users\<username>\CORTEX
   ```

3. **Install dependencies:**
   ```bash
   # Create virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   .\venv\Scripts\Activate.ps1  # Windows
   
   # Install requirements
   pip install -r requirements.txt
   ```

4. **Configure machine paths:**
   ```bash
   # Copy template
   cp cortex.config.template.json cortex.config.json
   
   # Edit cortex.config.json with your machine paths
   # (see SETUP-CORTEX.md for detailed instructions)
   ```

5. **Verify installation:**
   ```bash
   # Run tests
   pytest -v
   
   # Open workspace in VS Code
   code .
   ```

6. **Test in VS Code:**
   - Open GitHub Copilot Chat
   - Type: `/CORTEX help`
   - Expected: Help menu displays

---

## ✅ What's Included

### Essential Components

- ✅ **Full source code** (`src/`)
  - 10 specialist agents (left + right brain)
  - Plugin system (extensible architecture)
  - Tier 0, 1, 2, 3 cognitive layers
  - Operations orchestrators

- ✅ **Brain storage** (`cortex-brain/`)
  - Brain protection rules (SKULL protection layer)
  - Knowledge graph (learned patterns)
  - Response templates (quick help)
  - Conversation tracking (last 20 conversations)

- ✅ **Documentation** (`prompts/`)
  - Story: "The Intern with Amnesia"
  - Setup guide
  - Technical reference
  - Agents guide
  - All modular documentation

- ✅ **GitHub Copilot Integration**
  - `.github/prompts/CORTEX.prompt.md` - Entry point
  - `.github/copilot-instructions.md` - Baseline context
  - Both required for `/CORTEX` command to work

- ✅ **Automation scripts** (`scripts/`)
  - Conversation capture
  - Platform detection
  - Cleanup orchestrator
  - Deployment tools

- ✅ **Tests** (82 tests - NOT included in package to reduce size)
  - Available in source repository
  - Can be copied separately if needed

---

## 🔧 Prerequisites

**Before installation, ensure:**

- Python 3.8 or higher
- Git installed and configured
- pip package manager
- VS Code with GitHub Copilot extension

**Platform support:**
- ✅ Windows 10/11
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)

---

## 📖 Quick Start After Installation

Once installed and configured:

1. **Read the story:**
   ```
   In Copilot Chat: tell me the cortex story
   ```

2. **Configure platform:**
   ```
   In Copilot Chat: setup environment
   ```

3. **Enable conversation tracking (optional but recommended):**
   ```bash
   # Start ambient daemon
   python scripts/cortex/auto_capture_daemon.py
   ```

4. **Start using CORTEX:**
   ```
   In Copilot Chat: add authentication to my app
   In Copilot Chat: create comprehensive tests
   In Copilot Chat: what did we work on yesterday?
   ```

---

## 🆘 Troubleshooting

**Common issues:**

### 1. `/CORTEX` command not recognized

**Solution:**
- Verify `.github/prompts/CORTEX.prompt.md` exists in workspace root
- Verify `.github/copilot-instructions.md` exists in workspace root
- Reload VS Code window (Ctrl+Shift+P → "Reload Window")

### 2. Python import errors

**Solution:**
```bash
# Install in development mode
pip install -e .
```

### 3. Conversation tracking not working

**Solution:**
```bash
# Verify tracking files exist
ls cortex-brain/conversation-history.jsonl
ls cortex-brain/conversation-context.jsonl

# If missing, create them:
touch cortex-brain/conversation-history.jsonl
touch cortex-brain/conversation-context.jsonl
```

### 4. Platform detection fails

**Solution:**
```
In Copilot Chat: setup environment
# This will re-detect platform and configure paths
```

---

## 📚 Documentation

**Full documentation available after installation:**

- **Story:** `prompts/shared/story.md`
- **Setup Guide:** `prompts/shared/setup-guide.md`
- **Technical Reference:** `prompts/shared/technical-reference.md`
- **Agents Guide:** `prompts/shared/agents-guide.md`
- **Tracking Guide:** `prompts/shared/tracking-guide.md`

**Access in Copilot Chat:**
```
#file:prompts/shared/story.md
#file:prompts/shared/setup-guide.md
```

---

## 🎯 What Makes This Package Different

**Traditional installation packages:**
- Provide files and expect user to figure it out
- Manual configuration required
- Error-prone setup process

**CORTEX deployment package:**
- ✅ Single `SETUP-CORTEX.md` file
- ✅ GitHub Copilot executes installation automatically
- ✅ Platform detection and auto-configuration
- ✅ Verification at each step
- ✅ Clear troubleshooting guidance

**Result:** 5-minute Copilot-assisted setup vs. 30-minute manual setup

---

## 📦 Package Integrity

**This package includes:**

| Component | Size | Status |
|-----------|------|--------|
| Source code (`src/`) | ~2 MB | ✅ Complete |
| Brain storage (`cortex-brain/`) | ~15 MB | ✅ Complete |
| Documentation (`prompts/`) | ~1 MB | ✅ Complete |
| Scripts (`scripts/`) | ~500 KB | ✅ Complete |
| GitHub integration (`.github/`) | ~100 KB | ✅ Complete |
| Dependencies (`requirements.txt`) | ~10 KB | ✅ Complete |
| **Total** | **~18 MB** | ✅ Production Ready |

**Not included (available in source repo):**
- Tests (`tests/`) - 82 tests, ~2 MB
- Development docs (`docs/`) - ~5 MB
- Examples (`examples/`) - ~1 MB
- Build artifacts (`publish/`, `workflow_checkpoints/`) - varies

---

## 🔐 License

**CORTEX is proprietary software.**

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** See LICENSE file in CORTEX folder

Unauthorized reproduction, distribution, or modification is prohibited.

---

## 📧 Support

For issues, questions, or feedback:

- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** https://github.com/asifhussain60/CORTEX/docs
- **Source Code:** https://github.com/asifhussain60/CORTEX

---

**Package Version:** 1.0  
**CORTEX Version:** 5.2.0  
**Last Updated:** 2025-11-12

---

*This package is designed for seamless deployment with minimal manual intervention. Use SETUP-CORTEX.md with GitHub Copilot for best results.*
