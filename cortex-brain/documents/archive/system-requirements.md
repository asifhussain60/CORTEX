# System Requirements - CORTEX Onboarding

**Purpose:** Define technical prerequisites and compatibility requirements.

---

## 💻 Minimum System Requirements

### Hardware
- **CPU:** Dual-core 2.0 GHz or faster
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk:** 500 MB free space for CORTEX
- **Network:** Internet connection for pip install

### Operating Systems

| OS | Minimum Version | Recommended | Status |
|----|-----------------|-------------|--------|
| **macOS** | 10.15 Catalina | 13.0 Ventura+ | ✅ Fully Supported |
| **Windows** | Windows 10 | Windows 11 | ✅ Fully Supported |
| **Linux** | Ubuntu 20.04 | Ubuntu 22.04+ | ✅ Fully Supported |
| **Other Unix** | Various | Latest | ⚠️ Community Supported |

---

## 🐍 Python Requirements

### Python Version
- **Minimum:** Python 3.9
- **Recommended:** Python 3.11+
- **Maximum:** Python 3.12 (tested)

**Check your version:**
```bash
python3 --version
```

### Python Packages (Auto-installed)
```
pyyaml>=6.0
sqlalchemy>=2.0
pytest>=7.0 (dev)
mypy>=1.0 (dev)
```

---

## 🛠️ Development Environment

### Required Tools

1. **Git**
   - Version: 2.30+
   - Purpose: Version control, checkpoints
   - Install: https://git-scm.com/

2. **GitHub Copilot**
   - Platform: VS Code extension
   - Purpose: Primary interface for CORTEX
   - Install: VS Code Extensions Marketplace

3. **VS Code**
   - Version: 1.80+
   - Purpose: Recommended IDE
   - Install: https://code.visualstudio.com/

### Optional Tools

- **Docker** (for containerized deployment)
- **Azure CLI** (for ADO integration)
- **pytest** (for TDD workflow validation)

---

## 🌐 Network Requirements

### Outbound Access
- **PyPI:** pip.pypi.org (package installation)
- **GitHub:** github.com (repository access)
- **Documentation:** asifhussain60.github.io (web docs)

### Firewall Considerations
- CORTEX runs locally, no inbound ports required
- Outbound HTTPS (443) for package updates

---

## 📦 Disk Space Breakdown

| Component | Size | Purpose |
|-----------|------|---------|
| CORTEX Core | 50 MB | Main codebase |
| Dependencies | 150 MB | Python packages |
| Brain Storage | 100 MB | Knowledge graph, context |
| Documentation | 50 MB | HTML docs, guides |
| Workspace Cache | 150 MB | Temporary files, logs |
| **Total** | **~500 MB** | Initial install |

**Growth over time:**
- Conversation context: +10 MB/month (70 convos)
- Knowledge graph: +5 MB/month
- Archived plans: +20 MB/month

---

## 🔐 Permissions Required

### Filesystem
- **Read/Write:** CORTEX installation directory
- **Read/Write:** `cortex-brain/` (knowledge storage)
- **Read:** User workspace/projects
- **Write:** Temporary directory for operations

### Git
- **Read:** Repository metadata
- **Write:** Git checkpoints (optional, can be disabled)

### Network
- **HTTPS:** Package downloads, documentation access

---

## ✅ Compatibility Matrix

### Editor Support

| Editor | Support Level | Notes |
|--------|---------------|-------|
| VS Code | ✅ Primary | Full GitHub Copilot integration |
| JetBrains IDEs | ⚠️ Limited | Copilot support varies |
| Vim/Neovim | ⚠️ Experimental | Command-line interface only |
| Emacs | ⚠️ Experimental | Command-line interface only |

### Terminal Support

| Terminal | Support Level | Notes |
|----------|---------------|-------|
| Bash | ✅ Full | Tested extensively |
| Zsh | ✅ Full | Tested extensively |
| PowerShell | ✅ Full | Windows support |
| Fish | ⚠️ Limited | Community supported |
| Cmd.exe | ⚠️ Limited | Basic support only |

---

## 🧪 Pre-Installation Checklist

Before installing CORTEX, verify:

- [ ] Python 3.9+ installed
- [ ] `pip` available and updated
- [ ] Git installed and configured
- [ ] VS Code with GitHub Copilot extension
- [ ] 500 MB free disk space
- [ ] Internet connection active
- [ ] Write permissions in install directory

**Verification Script:**
```bash
# Run this to check prerequisites
python3 --version     # Should be 3.9+
pip3 --version        # Should be 20.0+
git --version         # Should be 2.30+
code --version        # Should be 1.80+
df -h .               # Should show 500MB+ free
```

---

## 🚨 Known Compatibility Issues

### Issue 1: Python 3.8 and Earlier
**Problem:** CORTEX requires Python 3.9+ for type hints  
**Solution:** Upgrade Python or use Docker container

### Issue 2: Windows Long Paths
**Problem:** Windows path length limit (260 chars)  
**Solution:** Enable long path support:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Issue 3: macOS Gatekeeper
**Problem:** Unsigned binaries blocked by Gatekeeper  
**Solution:** Allow in System Preferences → Security & Privacy

### Issue 4: Linux Permission Errors
**Problem:** Insufficient permissions in install directory  
**Solution:** Use virtual environment or `--user` flag:
```bash
pip3 install --user cortex-ai
```

---

## 📞 Support Resources

If you encounter system compatibility issues:

1. **Documentation:** https://asifhussain60.github.io/CORTEX/getting-started/
2. **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
3. **Discussions:** https://github.com/asifhussain60/CORTEX/discussions

---

**Author:** CORTEX Onboarding Team  
**Created:** 2025-12-29  
**Version:** 1.0.0
