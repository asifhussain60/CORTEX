# CORTEX AI Assistant for Visual Studio

**Version:** 4.0.0 | **Author:** Asif Hussain  
**Website:** https://asifhussain60.github.io/CORTEX/

AI Assistant with long-term memory, context awareness, and strategic planning capabilities for Visual Studio 2022.

---

## 🎯 Overview

CORTEX is a powerful AI assistant that brings GitHub Copilot's capabilities to the next level with:
- **Long-term memory** across sessions and projects
- **Strategic planning** with 4-tier complexity classification
- **TDD mastery** with RED→GREEN→REFACTOR workflows
- **System maintenance** with 6-phase health pipelines
- **Multi-repo architecture** - one CORTEX installation for unlimited workspaces

---

## ✨ Features

### 🧠 Core Capabilities

1. **Planning System**
   - Create comprehensive project plans
   - TDD integration with DoR/DoD enforcement
   - Progress tracking and reporting

2. **TDD Workflows**
   - RED→GREEN→REFACTOR enforcement
   - Automatic test generation
   - Coverage tracking

3. **System Maintenance**
   - 7-phase health pipeline
   - Automated cleanup and optimization
   - Performance monitoring

4. **Azure DevOps Integration**
   - Create stories, features, tasks, bugs
   - DoR/DoD quality gates
   - Work item hierarchy management

5. **Code Sanitization**
   - Remove sensitive data and company information
   - Make code generic and shareable
   - 5-phase sanitization workflow

6. **System Refinement**
   - 7-phase improvement process
   - SOLID principle enforcement
   - Code quality analysis

### 🖥️ Tool Windows

- **CORTEX Dashboard** - System status and quick actions
- **Planning Viewer** - Interactive plan visualization

---

## 📋 Requirements

- **Visual Studio:** 2022 (17.0 or later)
- **Platform:** Windows (amd64)
- **.NET Framework:** 4.8
- **CORTEX Installation:** Required (see Installation below)
- **Python:** 3.8+ (for CORTEX backend)

---

## 🚀 Installation

### 1. Install CORTEX Backend

```bash
# Clone CORTEX repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Install Python dependencies
pip install -r requirements.txt

# Set environment variable (optional but recommended)
setx CORTEX_HOME "C:\path\to\CORTEX"
```

### 2. Install Visual Studio Extension

1. Download `CortexVSExtension.vsix` from [Releases](https://github.com/asifhussain60/CORTEX/releases)
2. Double-click the `.vsix` file to install
3. Restart Visual Studio

---

## 📖 Usage

### Access CORTEX Commands

**Menu:** `Tools` → `CORTEX` → `[Command]`

### Available Commands

| Command | Description | Shortcut |
|---------|-------------|----------|
| **Create Plan** | Start planning workflow | - |
| **Start TDD Workflow** | Begin RED→GREEN→REFACTOR cycle | - |
| **System Maintenance** | Run 6-phase health check | - |
| **Create ADO Story** | Create Azure DevOps work item | - |
| **Sanitize Code** | Remove sensitive data | - |
| **Refine System** | 7-phase improvement | - |
| **CORTEX Help** | Show help documentation | - |

### Open Tool Windows

**Menu:** `Tools` → `CORTEX` → `[Tool Window]`

- **CORTEX Dashboard** - System overview
- **Planning Viewer** - Plan visualization

---

## 🔧 Configuration

### Workspace Detection

CORTEX automatically detects:
1. Current solution path
2. CORTEX installation (via `CORTEX_HOME` or search)
3. Multi-repo context (user workspace vs CORTEX repo)

### Python Environment

Searches for Python in order:
1. `python3`
2. `python`
3. `py`
4. CORTEX venv (`<CORTEX_HOME>/venv/Scripts/python.exe`)

---

## 📚 Examples

### Create a Plan

```
1. Click "Tools" → "CORTEX" → "Create Plan"
2. Enter plan name (e.g., "user-authentication")
3. CORTEX creates: planning/active/user-authentication/
   - 00-master-plan.md
   - context/ reports/ artifacts/ tracking/
```

### Start TDD Workflow

```
1. Click "Tools" → "CORTEX" → "Start TDD Workflow"
2. Follow RED→GREEN→REFACTOR cycle
3. View test results in Output window
```

### System Maintenance

```
1. Click "Tools" → "CORTEX" → "System Maintenance"
2. CORTEX runs 7-phase pipeline:
   - Pre-healthcheck → Align → Cleanup → Optimize
   - Vacuum → Refresh → Post-healthcheck
3. View health report in cortex-brain/health-reports/
```

---

## 🐛 Troubleshooting

### CORTEX Not Found

**Error:** "CORTEX installation not found"

**Solutions:**
1. Set `CORTEX_HOME` environment variable
2. Open a solution in the same parent directory as CORTEX
3. Verify CORTEX installation: `cortex-brain/` folder exists

### Python Not Found

**Error:** "Python interpreter not found"

**Solutions:**
1. Install Python 3.8+ from https://www.python.org/
2. Ensure Python is in PATH
3. Create CORTEX venv: `python -m venv venv`

### Command Fails

**Error:** Command execution fails

**Solutions:**
1. Check Output window (View → Output → CORTEX)
2. Verify CORTEX backend is installed correctly
3. Run command manually in terminal to diagnose

---

## 🔗 Resources

- **Website:** https://asifhussain60.github.io/CORTEX/
- **Repository:** https://github.com/asifhussain60/CORTEX
- **Documentation:** https://asifhussain60.github.io/CORTEX/docs/
- **Issues:** https://github.com/asifhussain60/CORTEX/issues

---

## 📄 License

MIT License - Copyright © 2025 Asif Hussain

---

## 🙏 Acknowledgments

Built with ❤️ by Asif Hussain for the developer community.

**Support:** If you find CORTEX helpful, please star the repository and share with others!
