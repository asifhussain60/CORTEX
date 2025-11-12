````prompt
# CORTEX Installation Guide for GitHub Copilot

**Purpose:** Step-by-step instructions for GitHub Copilot to properly install CORTEX on a target machine.

**Target:** Fresh installation on Windows, macOS, or Linux  
**Source Package:** `CORTEX/` folder in this directory  
**Version:** 5.2.0

---

## 📋 Installation Checklist

### Phase 1: Pre-Installation Verification

**Before starting, verify:**

1. **Python 3.8+ installed**
   ```powershell
   # Windows
   python --version
   
   # macOS/Linux
   python3 --version
   ```
   
2. **Git installed and configured**
   ```bash
   git --version
   git config --global user.name
   git config --global user.email
   ```

3. **pip available**
   ```bash
   pip --version
   ```

4. **Target installation directory determined**
   - Windows: `C:\Users\<username>\CORTEX` or custom path
   - macOS/Linux: `~/CORTEX` or custom path

---

### Phase 2: File Structure Setup

**CRITICAL:** The CORTEX package must be copied with proper structure.

**Required directory structure:**
```
<INSTALL_PATH>/
├── .github/
│   ├── prompts/
│   │   └── CORTEX.prompt.md         # Main entry point
│   └── copilot-instructions.md      # Baseline context
├── cortex-brain/                     # Cognitive storage
│   ├── brain-protection-rules.yaml
│   ├── knowledge-graph.yaml
│   ├── response-templates.yaml
│   └── ... (other brain files)
├── prompts/                          # Modular documentation
│   ├── shared/
│   │   ├── story.md
│   │   ├── setup-guide.md
│   │   ├── technical-reference.md
│   │   └── ... (other modules)
│   └── user/
├── src/                              # Python source code
│   ├── cortex_agents/
│   ├── plugins/
│   ├── tier0/
│   ├── tier1/
│   ├── tier2/
│   ├── tier3/
│   └── ... (other modules)
├── scripts/                          # Automation scripts
│   ├── cortex/
│   │   ├── auto_capture_daemon.py
│   │   └── cortex-capture.ps1
│   └── ... (other scripts)
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package installer
├── pytest.ini                        # Test configuration
├── README.md                         # Documentation
└── LICENSE                           # License file
```

**Installation Steps:**

```powershell
# Step 1: Copy the CORTEX folder to target location
Copy-Item -Path ".\CORTEX" -Destination "<INSTALL_PATH>" -Recurse -Force

# Step 2: Navigate to installation directory
cd "<INSTALL_PATH>"

# Step 3: Verify structure
Get-ChildItem -Recurse -Depth 1
```

---

### Phase 3: Python Environment Setup

**Option A: Virtual Environment (Recommended)**

```powershell
# Windows PowerShell
cd <INSTALL_PATH>
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
cd <INSTALL_PATH>
python3 -m venv venv
source venv/bin/activate
```

**Option B: System-wide Installation**

```bash
# Use system Python (not recommended for production)
cd <INSTALL_PATH>
```

---

### Phase 4: Dependency Installation

**Install Python dependencies:**

```bash
# Ensure you're in the CORTEX directory
cd <INSTALL_PATH>

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "pytest|PyYAML|mkdocs|watchdog|scikit-learn"
```

**Expected packages:**
- pytest>=7.4.0
- PyYAML>=6.0.1
- mkdocs>=1.5.0
- mkdocs-material>=9.4.0
- watchdog>=3.0.0
- scikit-learn>=1.3.0
- numpy>=1.24.0

---

### Phase 5: Configuration Setup

**Create configuration file:**

```bash
# Copy template to create machine-specific config
cp cortex.config.template.json cortex.config.json
```

**Edit `cortex.config.json` with machine paths:**

```json
{
  "machine": {
    "name": "<MACHINE_NAME>",
    "os": "windows|darwin|linux",
    "paths": {
      "cortex_root": "<INSTALL_PATH>",
      "brain_storage": "<INSTALL_PATH>/cortex-brain",
      "python": "<PATH_TO_PYTHON_EXECUTABLE>"
    }
  },
  "tier1": {
    "enabled": true,
    "conversation_tracking": true,
    "max_conversations": 20
  },
  "tier2": {
    "enabled": true,
    "knowledge_graph_path": "<INSTALL_PATH>/cortex-brain/knowledge-graph.yaml"
  },
  "tier3": {
    "enabled": true,
    "git_enabled": true
  }
}
```

**Determine paths:**

```powershell
# Windows - Get current directory
$pwd.Path

# Windows - Get Python path
(Get-Command python).Source

# macOS/Linux - Get current directory
pwd

# macOS/Linux - Get Python path
which python3
```

---

### Phase 6: Brain Initialization

**Initialize the CORTEX brain storage:**

```bash
# Verify brain files exist
ls cortex-brain/

# Expected files:
# - brain-protection-rules.yaml
# - knowledge-graph.yaml
# - response-templates.yaml
# - conversation-history.jsonl (will be created)
# - conversation-context.jsonl (will be created)
```

**Create empty tracking files if missing:**

```bash
# Create conversation tracking files
touch cortex-brain/conversation-history.jsonl
touch cortex-brain/conversation-context.jsonl
```

---

### Phase 7: VS Code Integration

**Enable CORTEX in VS Code:**

1. **Verify .github structure exists:**
   ```bash
   ls .github/prompts/CORTEX.prompt.md
   ls .github/copilot-instructions.md
   ```

2. **Open workspace in VS Code:**
   ```bash
   code .
   ```

3. **Verify Copilot loads baseline context:**
   - Open any file
   - Open GitHub Copilot Chat
   - Type: `what is cortex?`
   - Expected: Copilot should reference CORTEX cognitive framework

4. **Test entry point:**
   - In Copilot Chat, type: `/CORTEX help`
   - Expected: CORTEX help menu displays

---

### Phase 8: Conversation Tracking Setup

**Enable automatic conversation tracking (Optional but Recommended):**

**Method 1: Ambient Daemon (Recommended)**

```powershell
# Windows - Start daemon
python scripts/cortex/auto_capture_daemon.py

# Verify daemon is running
Get-Process | Where-Object { $_.ProcessName -like "*python*" }
```

**Method 2: Manual Capture (PowerShell)**

```powershell
# Run after each Copilot session
.\scripts\cortex\cortex-capture.ps1
```

**Method 3: Python CLI**

```bash
# Capture specific conversation
python -m src.tier1.cli capture-conversation "<conversation_id>"
```

**Verify tracking works:**

```bash
# Check conversation history
cat cortex-brain/conversation-history.jsonl

# Should see JSON lines with conversation data
```

---

### Phase 9: Verification & Testing

**Run verification tests:**

```bash
# Test Tier 0 (Brain Protection)
pytest tests/tier0/test_brain_protector.py -v

# Test Tier 1 (Conversation Memory)
pytest tests/tier1/ -v

# Test Plugin System
pytest tests/plugins/ -v

# Run all tests
pytest -v
```

**Expected results:**
- All Tier 0 tests passing (22/22)
- All Tier 1 tests passing
- All plugin tests passing
- Total: 80+ tests passing

**Test CORTEX operations:**

```bash
# In VS Code Copilot Chat:
/CORTEX help                    # Show help menu
setup environment               # Platform detection
tell me the cortex story        # Load story module
show me implementation status   # Check system status
```

---

### Phase 10: Post-Installation Configuration

**Optional enhancements:**

1. **Enable ambient tracking on startup:**
   - Create VS Code task in `.vscode/tasks.json`
   - Auto-start daemon when workspace opens

2. **Configure git hooks:**
   ```bash
   # Link conversation to commits
   python scripts/cortex/associate-commit.py
   ```

3. **Enable mkdocs documentation:**
   ```bash
   mkdocs serve
   # Opens documentation at http://localhost:8000
   ```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:**
```bash
# Ensure you're running from CORTEX root
cd <INSTALL_PATH>

# Install in development mode
pip install -e .
```

### Issue: ".github/prompts/CORTEX.prompt.md not found"

**Solution:**
```bash
# Verify file exists
ls .github/prompts/CORTEX.prompt.md

# If missing, copy from package
cp <PACKAGE_SOURCE>/.github/prompts/CORTEX.prompt.md .github/prompts/
```

### Issue: "Copilot doesn't recognize CORTEX commands"

**Solution:**
1. Ensure `.github/copilot-instructions.md` exists in workspace root
2. Reload VS Code window (Ctrl+Shift+P → "Reload Window")
3. Open a file and try again

### Issue: "Conversation tracking not working"

**Solution:**
```bash
# Check tracking files exist
ls cortex-brain/conversation-history.jsonl

# Verify daemon is running
Get-Process python

# Restart daemon
python scripts/cortex/auto_capture_daemon.py
```

### Issue: "Python version conflict"

**Solution:**
```bash
# Use virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

## ✅ Installation Complete Checklist

**Verify all steps:**

- [ ] Python 3.8+ installed and accessible
- [ ] Git configured
- [ ] CORTEX folder copied to target location with full structure
- [ ] `.github/prompts/CORTEX.prompt.md` exists
- [ ] `.github/copilot-instructions.md` exists
- [ ] Virtual environment created (recommended)
- [ ] Dependencies installed (`requirements.txt`)
- [ ] `cortex.config.json` created with machine paths
- [ ] Brain files initialized (`cortex-brain/`)
- [ ] Conversation tracking files created
- [ ] VS Code workspace opened
- [ ] Copilot recognizes CORTEX commands
- [ ] `/CORTEX help` works in Copilot Chat
- [ ] Tests passing (`pytest -v`)
- [ ] Conversation tracking enabled (optional)

---

## 📖 Next Steps

**After successful installation:**

1. **Read the story:**
   ```
   In Copilot Chat: tell me the cortex story
   ```

2. **Understand architecture:**
   ```
   In Copilot Chat: #file:prompts/shared/technical-reference.md
   ```

3. **Configure platform:**
   ```
   In Copilot Chat: setup environment
   ```

4. **Start using CORTEX:**
   ```
   In Copilot Chat: add authentication to my app
   ```

---

## 🆘 Support

**If installation fails:**

1. Check `KNOWN-ISSUES.md` in CORTEX folder
2. Verify all file paths are correct
3. Ensure no files are missing from package
4. Check Python/Git versions
5. Review error messages carefully

**Common paths to check:**
- `.github/prompts/CORTEX.prompt.md` (MUST exist)
- `.github/copilot-instructions.md` (MUST exist)
- `cortex-brain/brain-protection-rules.yaml` (MUST exist)
- `src/` folder (MUST exist with all Python modules)
- `requirements.txt` (MUST exist)

---

## 📦 Package Contents Verification

**The CORTEX package should contain:**

```
CORTEX/
├── .github/prompts/CORTEX.prompt.md     ✅ Entry point
├── .github/copilot-instructions.md      ✅ Baseline context
├── cortex-brain/                        ✅ Brain storage
├── prompts/shared/                      ✅ Documentation modules
├── src/                                 ✅ Python source
├── scripts/                             ✅ Automation tools
├── requirements.txt                     ✅ Dependencies
├── setup.py                             ✅ Package installer
├── pytest.ini                           ✅ Test config
├── README.md                            ✅ Documentation
└── LICENSE                              ✅ License
```

**Verify package integrity:**
```bash
# Count critical files
ls .github/prompts/CORTEX.prompt.md && echo "✅ Entry point OK"
ls .github/copilot-instructions.md && echo "✅ Baseline context OK"
ls cortex-brain/brain-protection-rules.yaml && echo "✅ Brain rules OK"
ls src/plugins/base_plugin.py && echo "✅ Source code OK"
ls requirements.txt && echo "✅ Dependencies OK"
```

---

**Installation Script Version:** 1.0  
**Last Updated:** 2025-11-12  
**CORTEX Version:** 5.2.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

*This installation guide is designed for GitHub Copilot to execute reliably across different platforms and environments.*
````
