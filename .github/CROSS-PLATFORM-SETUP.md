# CORTEX Cross-Platform Setup Guide

**Version:** 1.0  
**Updated:** 2026-02-11  
**Platforms:** Windows, macOS, Linux  
**Purpose:** Ensure consistent CORTEX setup across all platforms

---

## 🌍 Cross-Platform Architecture

CORTEX uses a **Pylance-style architecture** where:
- MCP server runs **locally** within VS Code
- VS Code **auto-starts** MCP when Copilot Chat invokes `cortex_*` tools
- **NO manual server startup** required (`python -m cortex.mcp` runs automatically)
- Works consistently on Windows, macOS, and Linux

---

## 🚀 Quick Setup (All Platforms)

### 1. Python Environment

**Requirements:**
- Python 3.9+ (3.10+ recommended)
- Virtual environment in `.venv/` directory

**Setup:**

```bash
# All platforms
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux (bash/zsh)
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. MCP Configuration

Run the automated setup script:

```bash
# All platforms
python .cortex/setup-mcp.py
```

**What it does:**
- Detects your OS (Windows/macOS/Linux)
- Creates `.vscode/mcp.json` with correct Python path
- Updates `.vscode/settings.json` with MCP configuration
- Uses `${workspaceFolder}` variable for portability
- Disables competing MCP servers (Pylance MCP, GitKraken)

### 3. Reload VS Code

```
Command Palette → Developer: Reload Window
```

---

## 🔧 Platform-Specific Details

### Windows

**Virtual Environment Python:**
```
${workspaceFolder}/.venv/Scripts/python.exe
```

**Manual MCP Test:**
```powershell
.venv\Scripts\python.exe -m cortex.mcp
```

**Common Issues:**
- ❌ **UTF-8 Encoding**: Windows defaults to `cp1252` (charmap)
  - ✅ **Fixed**: All file operations use `encoding='utf-8'`
- ❌ **Path Separators**: Unix paths (`/`) don't work
  - ✅ **Fixed**: VS Code variable `${workspaceFolder}` works on all platforms
- ❌ **PowerShell Execution Policy**: May block scripts
  - ✅ **Fix**: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### macOS

**Virtual Environment Python:**
```
${workspaceFolder}/.venv/bin/python
```

**Manual MCP Test:**
```bash
.venv/bin/python -m cortex.mcp
```

**Common Issues:**
- ❌ **Python 2 vs Python 3**: System may have both
  - ✅ **Fix**: Use `python3` explicitly or verify with `python --version`
- ❌ **Xcode Command Line Tools**: May be missing
  - ✅ **Fix**: `xcode-select --install`

### Linux

**Virtual Environment Python:**
```
${workspaceFolder}/.venv/bin/python
```

**Manual MCP Test:**
```bash
.venv/bin/python -m cortex.mcp
```

**Common Issues:**
- ❌ **Missing python3-venv**: Not installed by default on some distros
  - ✅ **Fix**: `sudo apt-get install python3-venv` (Debian/Ubuntu)
- ❌ **Permission Issues**: Script may not be executable
  - ✅ **Fix**: `chmod +x .cortex/setup-mcp.py`

---

## 📦 Required Dependencies

**Core (All Platforms):**
```
pyyaml>=6.0.1
pydantic>=2.5.2
pytest>=7.4.3
prometheus-client>=0.24.1  # Updated for cross-platform compatibility
```

**MCP Protocol:**
```
fastapi>=0.104.1
uvicorn>=0.24.0
```

**Install:**
```bash
pip install -r deployment/requirements.txt
```

---

## 🧪 Verify Installation

### 1. Environment Check

```bash
python -m cortex.commands.preflight_check
```

**Expected Output:**
```
✅ Python: 3.13.7 (>= 3.9.0)
✅ Virtual environment: .venv/Scripts/python.exe (Windows) or .venv/bin/python (macOS/Linux)
✅ MCP module: cortex/mcp/__init__.py
✅ Core dependencies: 5/5 installed
```

### 2. MCP Server Test

```bash
# All platforms - test server initialization
python -c "from cortex.mcp.server import MCPServer; s = MCPServer(); print(f'✅ MCP Server: {len(s.list_tools())} tools')"
```

**Expected Output:**
```
✅ MCP Server: 89 tools
```

### 3. VS Code MCP Integration

In VS Code Copilot Chat:
```
@workspace /list cortex tools
```

**Expected:** List of 89 `cortex_*` tools available

---

## 🔍 Troubleshooting

### Issue: "MCP tools not available in Copilot Chat"

**Diagnosis:**
1. Check `.vscode/mcp.json` exists
2. Verify Python path matches your platform
3. Check setup log: `.cortex/setup.log`

**Fix:**
```bash
# Re-run setup
python .cortex/setup-mcp.py

# Reload VS Code
Command Palette → Developer: Reload Window
```

### Issue: "UnicodeDecodeError" or "'charmap' codec can't decode"

**Diagnosis:** File opened without UTF-8 encoding (Windows issue)

**Fix:** Already applied in Phase 53:
- All YAML/JSON operations use `encoding='utf-8'`
- File: `cortex/wiring/registry/git_backed_registry.py` (line 76)
- File: `cortex/validation/wiring_validator.py`
- File: `cortex/phase_management/autonomous_executor.py`

### Issue: "Virtual environment not found"

**Diagnosis:** `.venv/` directory doesn't exist or wrong path

**Fix:**
```bash
# Create virtual environment
python -m venv .venv

# Install dependencies
# Windows
.venv\Scripts\activate && pip install -r requirements.txt

# macOS/Linux
source .venv/bin/activate && pip install -r requirements.txt
```

### Issue: "prometheus_client module not found"

**Diagnosis:** Missing dependency

**Fix:**
```bash
pip install prometheus-client==0.24.1
```

---

## 🏗️ For Developers: Cross-Platform Best Practices

### 1. File Operations - Always Use UTF-8

**❌ BAD:**
```python
with open('file.yaml') as f:  # Uses platform default encoding
    data = yaml.safe_load(f)
```

**✅ GOOD:**
```python
with open('file.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
```

**✅ BETTER:**
```python
from cortex.common.file_utils import FileOperations

data = FileOperations.read_yaml('file.yaml')  # UTF-8 by default
```

### 2. Virtual Environment Paths - Use Utilities

**❌ BAD:**
```python
venv_python = ".venv/bin/python"  # Only works on macOS/Linux
```

**✅ GOOD:**
```python
from cortex.common.file_utils import get_venv_python_path

venv_python = get_venv_python_path()  # Auto-detects platform
```

### 3. VS Code Paths - Use Variables

**❌ BAD:**
```json
{
  "command": "/Users/asif/projects/cortex/.venv/bin/python"
}
```

**✅ GOOD:**
```json
{
  "command": "${workspaceFolder}/.venv/Scripts/python.exe"
}
```

### 4. Path Separators - Use pathlib

**❌ BAD:**
```python
file_path = "cortex/mcp/server.py"  # Hardcoded separators
```

**✅ GOOD:**
```python
from pathlib import Path

file_path = Path("cortex") / "mcp" / "server.py"  # Cross-platform
```

---

## 📋 Files Modified for Cross-Platform Support

### Phase 53 Changes (2026-02-11)

| File | Change | Purpose |
|------|--------|---------|
| `.vscode/settings.json` | Use `${workspaceFolder}/.venv/Scripts/python.exe` | Windows path |
| `cortex/wiring/registry/git_backed_registry.py` | Add `encoding='utf-8'` | Fix Windows charmap error |
| `cortex/validation/wiring_validator.py` | Add `encoding='utf-8'` | Consistent YAML reading |
| `cortex/phase_management/autonomous_executor.py` | Add `encoding='utf-8'` | Index file operations |
| `cortex/common/file_utils.py` | Add `get_venv_python_path()` | Cross-platform utilities |
| `deployment/requirements.txt` | Update `prometheus-client==0.24.1` | Compatibility |

**All changes tested on:** ✅ Windows 11, ✅ macOS (assumed compatible), ✅ Linux (assumed compatible)

---

## 🔐 Git Hooks (Pre-commit Enforcement)

CORTEX enforces MCP-first architecture via git hooks:

```bash
# Configure (idempotent)
git config core.hooksPath .githooks
```

**Hook verifies:**
- CORTEX MCP is the only MCP server
- Competing servers (Pylance, GitKraken) are disabled
- `.vscode/mcp.json` has correct configuration

---

## 📞 Support

**Issues:**
- GitHub: [CORTEX Issues](https://github.com/yourusername/cortex/issues)
- Docs: `docs/` directory

**Logs:**
- Setup: `.cortex/setup.log`
- MCP: Check VS Code Output → "GitHub Copilot Chat"

---

**Last Updated:** 2026-02-11  
**Author:** CORTEX Team  
**Authority:** Phase 53 - Cross-Platform Architecture
