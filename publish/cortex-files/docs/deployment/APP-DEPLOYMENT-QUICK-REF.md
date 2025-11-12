# CORTEX Application Deployment - Quick Reference

**Purpose:** Deploy CORTEX to any target application with automatic bootstrapping  
**Version:** 1.1 (Bootstrap Edition)  
**Updated:** 2025-11-11

---

## 🚀 One-Command Deployment

**CORTEX now bootstraps itself!** No prerequisites needed - the deployment script automatically installs Python, Git, Node.js, and all dependencies.

### Basic Deployment

```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS
```

**What it does automatically:**
1. ✅ **Detects missing tools** (Python, Git, Node.js, SQLite)
2. ✅ **Installs missing tools** (asks permission first)
3. ✅ **Installs Python dependencies** (pip packages)
4. ✅ **Builds user package** (filters admin operations)
5. ✅ **Copies files** to target
6. ✅ **Configures paths** for target app
7. ✅ **Installs entry point** in .github/prompts/
8. ✅ **Initializes brain** database
9. ✅ **Sets up Vision API** (if full profile)

---

## 📋 Prerequisites (Auto-Installed!)

**Nothing required!** The script handles everything:

### Windows
- **Package Manager:** Chocolatey or winget (auto-detected)
- If none found, provides installation instructions

### macOS
- **Package Manager:** Homebrew (auto-detected)
- If not found, provides installation link

### Linux
- **Package Manager:** apt/yum/dnf (auto-detected)
- Uses sudo for system packages

---

## 🎯 Deployment Profiles

### Quick (Files Only)
```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --profile quick
```
- Copies CORTEX files only
- No brain initialization
- No crawlers
- **Use for:** Minimal setup, testing

### Standard (Recommended)
```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --profile standard
```
- Full file deployment
- Brain initialization
- Python dependencies installed
- **Use for:** Normal deployment

### Full (Everything)
```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --profile full
```
- Everything from Standard +
- Vision API setup
- Codebase crawlers
- **Use for:** Complete deployment

---

## 🧪 Dry Run (Preview Mode)

Test deployment without making changes:

```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --dry-run
```

**Shows:**
- What tools would be installed
- What files would be copied
- What configuration would change
- Estimated deployment size

---

## 🛠️ Automatic Tooling Installation

### Detected & Installed Automatically

| Tool | Windows | macOS | Linux | Required |
|------|---------|-------|-------|----------|
| **Python** | Choco/winget | Homebrew | apt/yum | ✅ YES |
| **pip** | With Python | With Python | apt/yum | ✅ YES |
| **Git** | Choco/winget | Homebrew | apt/yum | ✅ YES |
| **SQLite** | Choco/winget | Homebrew | apt/yum | ✅ YES |
| **Node.js** | Choco/winget | Homebrew | apt/yum | ⚠️ Optional |
| **npm** | With Node.js | With Node.js | With Node.js | ⚠️ Optional |

### Installation Flow

1. **Detection Phase:**
   ```
   Checking required tooling...
   ❌ Python      [REQUIRED]  Not installed
   ❌ Git         [REQUIRED]  Not installed
   ✅ SQLite      [REQUIRED]  Version 3.39.0
   📦 Package Manager: choco
   ```

2. **Permission Prompt:**
   ```
   Missing required tools: python, git
   
   CORTEX can automatically install missing tools.
   Install missing tools now? (y/n):
   ```

3. **Installation:**
   ```
   Installing Python...
   Running: choco install python -y
   ✅ Installed successfully: python
   
   Installing Git...
   Running: choco install git -y
   ✅ Installed successfully: git
   ```

4. **Verification:**
   ```
   Verifying installations...
   ✅ Python      [REQUIRED]  Version 3.11.5
   ✅ Git         [REQUIRED]  Version 2.42.0
   ✅ All required tooling detected!
   ```

---

## 📦 Deployment Package Contents

### ✅ USER PACKAGE (Included)

**3 Operations:**
- `cortex_tutorial` - Interactive demo
- `environment_setup` - Environment configuration
- `workspace_cleanup` - Workspace maintenance

**18 Modules:**
- Demo modules (introduction, help, story, cleanup, conversation, completion)
- Setup modules (platform detection, git sync, virtual env, dependencies, vision API)
- Cleanup module (workspace cleanup orchestrator)

**Core Architecture:**
- Tier 0 (Brain protection)
- Tier 1 (Conversation memory)
- Tier 2 (Knowledge graph)
- Tier 3 (Development context)
- All 10 specialist agents

**Size:** ~2-3 MB (vs 15-20 MB full repo)

### ❌ ADMIN-ONLY (Excluded)

**9 Operations:**
- `refresh_cortex_story` - Updates CORTEX docs
- `update_documentation` - MkDocs site builder
- `brain_protection_check` - Internal validation
- `brain_health_check` - System diagnostics
- Plus 5 more admin operations

**68 Modules:**
- Design sync, optimization, self-review
- Admin scripts, test suites, development tools

---

## 🎯 Post-Deployment Testing

### In Target Application

```powershell
cd D:\PROJECTS\KSESSIONS
```

### Test in GitHub Copilot Chat

```
demo
```
Should show interactive tutorial

```
setup environment
```
Should detect platform and configure

```
cleanup workspace
```
Should show cleanup options

### Verify Installation

```powershell
# Check CORTEX files
ls cortex/

# Check entry point
ls .github/prompts/CORTEX.prompt.md

# Check brain
ls cortex/cortex-brain/cortex-brain.db

# Verify config
cat cortex/cortex.config.json
```

---

## 🔧 Troubleshooting

### "No package manager found"

**Windows:**
```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

**macOS:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Linux:**
```bash
# Package manager should be pre-installed
# Use: apt-get, yum, or dnf depending on distro
```

### "Installation failed"

1. Run with admin/sudo privileges
2. Check internet connection
3. Manually install failed tool
4. Re-run deployment

### "Brain initialization failed"

Non-fatal - brain will auto-create on first use:
```
cortex/cortex-brain/cortex-brain.db
```

---

## 📊 Deployment Statistics

**Typical deployment:**
- Duration: 5-10 minutes (first time with tool installation)
- Duration: 2-3 minutes (subsequent deployments)
- Package size: 2-3 MB
- Files copied: ~11,000
- Files excluded: ~42,000 (79% reduction)

**With bootstrapping:**
- +3-5 minutes for Python installation
- +1-2 minutes for Git installation
- +2-3 minutes for pip dependencies
- Total: 10-20 minutes on clean machine

---

## 🎓 Advanced Usage

### Custom Source Path

```powershell
python scripts/deploy_to_app.py `
  --source D:\CUSTOM\CORTEX `
  --target D:\PROJECTS\KSESSIONS
```

### Multiple Deployments

```powershell
# Deploy to multiple apps
python scripts/deploy_to_app.py --target D:\PROJECTS\APP1
python scripts/deploy_to_app.py --target D:\PROJECTS\APP2
python scripts/deploy_to_app.py --target D:\PROJECTS\APP3
```

### Update Existing Deployment

```powershell
# Just re-run deployment (will overwrite)
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS
```

---

## 📚 Related Documentation

- **Deployment Implementation:** `cortex-brain/USER-DEPLOYMENT-IMPLEMENTATION.md`
- **User Deployment Guide:** `docs/deployment/USER-DEPLOYMENT-GUIDE.md`
- **Tooling Detection:** `src/operations/modules/tooling_detection_module.py`
- **Tooling Installation:** `src/operations/modules/tooling_installer_module.py`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary

*Last Updated: 2025-11-11 | Bootstrap Edition*

**Deploy CORTEX to any target application with one command**

---

## 🚀 Quick Deploy

### To KSESSIONS (or any app):

```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS
```

**That's it!** This single command:
1. ✅ Validates target app
2. ✅ Builds user package
3. ✅ Copies CORTEX files
4. ✅ Configures paths
5. ✅ Installs entry point in `.github/prompts/`
6. ✅ Initializes brain database
7. ✅ Ready to use!

---

## 📋 Deployment Profiles

### Quick (Files Only)
```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --profile quick
```
- Copies files
- Configures paths
- Installs entry point
- **No brain initialization**
- **No crawlers**
- Fast: ~30 seconds

### Standard (Default - Recommended)
```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --profile standard
```
- Everything in Quick
- **+ Brain initialization**
- **+ Deployment verification**
- Medium: ~1-2 minutes

### Full (Complete Setup)
```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --profile full
```
- Everything in Standard
- **+ Runs crawlers** (indexes codebase)
- **+ Full knowledge graph**
- Slow: ~5-10 minutes

---

## 🔍 Dry Run (Preview)

**See what would happen without making changes:**

```powershell
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --dry-run
```

---

## 📁 What Gets Deployed

### Target Application Structure After Deployment

```
KSESSIONS/                          # Your target app
├── .github/
│   ├── prompts/
│   │   └── CORTEX.prompt.md       # ✅ Entry point installed
│   └── copilot-instructions.md    # ✅ Baseline context
├── cortex/                         # ✅ CORTEX package
│   ├── src/                        # Core systems
│   ├── cortex-brain/               # Brain storage
│   │   └── cortex-brain.db        # ✅ Initialized
│   ├── prompts/                    # Documentation
│   ├── cortex.config.json          # ✅ Configured for KSESSIONS
│   ├── cortex-operations.yaml      # Operations registry
│   └── requirements.txt            # Dependencies
└── [your application files]
```

---

## ✅ Post-Deployment

### 1. Install Dependencies

```powershell
cd D:\PROJECTS\KSESSIONS
pip install -r cortex/requirements.txt
```

### 2. Test CORTEX

Open GitHub Copilot Chat and try:

```
demo
```

Should run interactive CORTEX demo.

```
setup environment
```

Should detect KSESSIONS as the target app.

```
cleanup workspace
```

Should scan KSESSIONS workspace.

---

## 🔧 Configuration

### Automatic Configuration

The deployment script automatically:
- ✅ Detects your platform (Windows/Mac/Linux)
- ✅ Detects your hostname
- ✅ Configures paths for KSESSIONS
- ✅ Updates `cortex/cortex.config.json`

### Manual Tweaks (Optional)

Edit `cortex/cortex.config.json`:

```json
{
  "application": {
    "name": "KSESSIONS",
    "rootPath": "D:\\PROJECTS\\KSESSIONS"
  },
  "machines": {
    "YOURHOSTNAME": {
      "rootPath": "D:\\PROJECTS\\KSESSIONS\\cortex",
      "brainPath": "D:\\PROJECTS\\KSESSIONS\\cortex\\cortex-brain"
    }
  }
}
```

---

## 🐛 Troubleshooting

### Deployment Failed?

```powershell
# Check logs
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS --dry-run
```

### Common Issues

**Issue:** `Target path does not exist`  
**Fix:** Verify KSESSIONS path is correct

**Issue:** `No write permission`  
**Fix:** Run as administrator or check folder permissions

**Issue:** `Build script not found`  
**Fix:** Ensure you're running from CORTEX root directory

**Issue:** `Entry point not found in package`  
**Fix:** Rebuild user package first:
```powershell
python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0
```

---

## 🔄 Redeployment

**To update CORTEX in target app:**

```powershell
# Will overwrite existing CORTEX installation
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS
```

Preserves brain data and configuration by default.

---

## 🗑️ Uninstall

**To remove CORTEX from target app:**

```powershell
cd D:\PROJECTS\KSESSIONS
Remove-Item -Path cortex -Recurse -Force
Remove-Item -Path .github\prompts\CORTEX.prompt.md
Remove-Item -Path .github\copilot-instructions.md
```

---

## 📊 Deployment Comparison

| Aspect | Manual Copy | Deploy Script |
|--------|-------------|---------------|
| **Time** | 15-20 min | 1-2 min |
| **Errors** | High risk | Validated |
| **Configuration** | Manual | Automatic |
| **Entry Point** | Manual | Automatic |
| **Brain Init** | Manual | Automatic |
| **Crawlers** | Manual | Automatic |
| **Verification** | Manual | Automatic |

---

## 🎯 Multiple Applications

**Deploy to multiple apps:**

```powershell
# Deploy to KSESSIONS
python scripts/deploy_to_app.py --target D:\PROJECTS\KSESSIONS

# Deploy to another app
python scripts/deploy_to_app.py --target D:\PROJECTS\MYAPP

# Deploy to third app
python scripts/deploy_to_app.py --target D:\PROJECTS\WEBAPP
```

Each gets independent:
- ✅ Brain database
- ✅ Configuration
- ✅ Knowledge graph

---

## 💡 Pro Tips

1. **Use Standard profile** for most cases (balances speed & completeness)
2. **Run dry-run first** on production apps
3. **Commit before deployment** (easy rollback)
4. **Test with 'demo'** immediately after deployment
5. **Let crawlers run overnight** for large codebases (full profile)

---

## 📚 Related Documentation

- **User Package Builder:** `scripts/build_user_deployment.py`
- **Deployment Guide:** `docs/deployment/USER-DEPLOYMENT-GUIDE.md`
- **Operations Registry:** `cortex-operations.yaml` (deploy_to_app operation)

---

**Questions?** See full deployment documentation or deployment script source code.

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
