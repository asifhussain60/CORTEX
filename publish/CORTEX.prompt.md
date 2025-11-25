# CORTEX AI Assistant - Quick Start

**Purpose:** Bootstrap CORTEX installation and enable `/CORTEX` commands  
**Version:** 3.2.0  
**Status:** ✅ Bootstrap File (Will be replaced after installation)

---

## 🚀 First Time Setup

**CORTEX is not yet installed in this repository. Follow these steps:**

### Installation Method 1: Download Latest Release (Recommended)

**Windows (PowerShell):**
```powershell
# Navigate to your project root
cd "d:\PROJECTS\YOUR-REPO"

# Download and extract latest CORTEX release
$latestRelease = "https://github.com/asifhussain60/CORTEX/releases/latest/download/CORTEX.zip"
Invoke-WebRequest -Uri $latestRelease -OutFile "CORTEX.zip"
Expand-Archive -Path "CORTEX.zip" -DestinationPath "CORTEX" -Force
Remove-Item "CORTEX.zip"

# Copy this bootstrap file to activate /CORTEX commands
Copy-Item "CORTEX\CORTEX.prompt.md" ".github\prompts\CORTEX.prompt.md" -Force

Write-Host "✅ CORTEX installed! Reload VS Code and use: /CORTEX setup environment"
```

**macOS/Linux (Bash):**
```bash
# Navigate to your project root
cd ~/projects/YOUR-REPO

# Download and extract latest CORTEX release
curl -L -o CORTEX.zip https://github.com/asifhussain60/CORTEX/releases/latest/download/CORTEX.zip
unzip CORTEX.zip -d CORTEX
rm CORTEX.zip

# Copy bootstrap file to activate /CORTEX commands
mkdir -p .github/prompts
cp CORTEX/CORTEX.prompt.md .github/prompts/CORTEX.prompt.md

echo "✅ CORTEX installed! Reload VS Code and use: /CORTEX setup environment"
```

### Installation Method 2: Manual Download

1. Visit: https://github.com/asifhussain60/CORTEX/releases/latest
2. Download `CORTEX.zip`
3. Extract to your project root (creates `CORTEX/` folder)
4. Copy `CORTEX/CORTEX.prompt.md` to `.github/prompts/CORTEX.prompt.md`
5. Reload VS Code
6. Run: `/CORTEX setup environment`

### Post-Installation Setup

Once downloaded, CORTEX will auto-detect this is an embedded installation and configure itself.

**In GitHub Copilot Chat:**
```
/CORTEX setup environment
```

This will:
- ✅ Detect embedded installation in your repo
- ✅ Add `CORTEX/` to `.gitignore` (keeps CORTEX local only)
- ✅ Initialize brain storage
- ✅ Replace this bootstrap file with full CORTEX.prompt.md
- ✅ Enable all CORTEX features

### Start Using CORTEX

After setup completes, use natural language commands:
```
/CORTEX help
plan authentication feature
start tdd workflow
discover views in project
```

---

## 🔄 Already Have CORTEX? Upgrade It

If CORTEX is already installed in `CORTEX/` folder:

```
/CORTEX upgrade
```

This will:
- ✅ Auto-detect embedded installation
- ✅ Download latest release from GitHub
- ✅ Backup your brain data
- ✅ Apply updates safely
- ✅ Run post-upgrade validation
- ✅ Update this prompt file with full documentation

**Note:** The upgrade command works for both standalone and embedded CORTEX installations.

---

## 📋 Quick Commands (After Setup)

Once CORTEX is installed, you'll have access to:

**Planning & Development:**
- `plan [feature]` - Interactive feature planning with DoR/DoD
- `start tdd` - TDD workflow with RED→GREEN→REFACTOR automation
- `discover views` - Auto-extract element IDs for testing

**System Management:**
- `help` - Show all available commands
- `upgrade cortex` - Update to latest version
- `optimize` - Clean brain data, vacuum databases
- `healthcheck` - System health validation

**Context & Memory:**
- `show context` - View what CORTEX remembers
- `capture conversation` - Import conversation to brain
- `resume plan [name]` - Continue existing work

---

## 📚 What is CORTEX?

**CORTEX** is an AI-powered development assistant that provides:

✅ **Feature Planning** - Interactive planning with Vision API, DoR/DoD enforcement  
✅ **TDD Workflow** - Automated test-driven development with auto-debug  
✅ **View Discovery** - Auto-extract element IDs from Razor/Blazor files  
✅ **Conversation Memory** - Persistent context across sessions  
✅ **Brain System** - Learns from your patterns and preferences  
✅ **Feedback System** - Structured issue reporting with auto-upload

**Key Benefits:**
- 92% time savings on test generation (60+ min → <5 min)
- 95%+ test accuracy with real element IDs
- Zero-ambiguity planning with security review
- Local-first privacy (all data stored on your machine)

---

## 🔒 Privacy & Local Storage

**CORTEX is 100% local-first:**
- All data stored in `CORTEX/cortex-brain/` directory
- No cloud dependencies (except GitHub for downloads)
- `CORTEX/` folder excluded from git (local only)
- Optional: Configure cloud sync for documents (databases stay local)

---

## 🆘 Troubleshooting

**Issue: "Command not found" or CORTEX doesn't respond**
- **Cause:** CORTEX not yet downloaded or setup incomplete
- **Fix:** Follow Step 1-3 above to download and setup CORTEX

**Issue: "CORTEX folder already exists"**
- **Cause:** Previous partial installation
- **Fix:** Delete `CORTEX/` folder and re-download, or run `/CORTEX upgrade`

**Issue: "Can't download from GitHub"**
- **Cause:** Network restrictions or proxy
- **Fix:** Manual download from https://github.com/asifhussain60/CORTEX/releases

**Issue: After upgrade, still seeing bootstrap instructions**
- **Cause:** Upgrade did not replace this file
- **Fix:** Manually copy `CORTEX/.github/prompts/CORTEX.prompt.md` to `.github/prompts/CORTEX.prompt.md`

---

## 📖 Full Documentation

After installation, full documentation will be available:
- `.github/prompts/CORTEX.prompt.md` - Complete feature reference
- `CORTEX/.github/prompts/modules/` - Detailed guides
- `CORTEX/cortex-brain/response-templates.yaml` - Response templates
- `CORTEX/README.md` - Project overview

---

## 🎓 Copyright & License

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**This is a bootstrap file.** After CORTEX installation, it will be replaced with the full `CORTEX.prompt.md` containing complete documentation and module references.

---

**Last Updated:** 2025-11-25 | Version 3.2.0 (Bootstrap)
