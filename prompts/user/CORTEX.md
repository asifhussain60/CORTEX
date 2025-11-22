# CORTEX Deploy - Production Package Publisher

**Purpose:** Deploy production-ready CORTEX 3.0 to `publish/CORTEX` folder with complete verification. This creates a clean, self-contained package that users can copy to their applications.

**Version:** 3.0  
**Status:** 🚀 ACTIVE  
**Commands:** `/CORTEX deploy` or `/CORTEX publish`

---

## 🎯 What This Does

This workflow:
1. ✅ Cleans `publish/CORTEX` folder
2. ✅ Copies complete CORTEX 3.0 source (407 files, ~4 MB)
3. ✅ Includes all core components (brain, agents, operations, prompts)
4. ✅ Creates SETUP-FOR-COPILOT.md user guide
5. ✅ Creates production README.md
6. ✅ **VERIFIES package integrity** (15+ verification checks)
7. ✅ Confirms package is production-ready

**📦 OUTPUT:** Verified production package in `publish/CORTEX/` ready for distribution.

---

## 📋 Prerequisites

Before deploying:
- ✅ In CORTEX root directory (D:\PROJECTS\CORTEX)
- ✅ All source files present and tested
- ✅ No uncommitted critical changes
- ✅ Version updated if needed

---

## 🚀 Quick Deploy

```powershell
# Run deployment with verification
.\scripts\publish-cortex.ps1 -Force

# Or use CORTEX command
/CORTEX deploy
/CORTEX publish
```

---

## 📦 What Gets Published

The `publish/CORTEX/` package includes:

**🔹 Entry Point:**
- `.github/prompts/CORTEX.prompt.md` - Copilot integration

**🔹 Brain System:**
- `cortex-brain/` - Brain rules, knowledge graph, capabilities, templates

**🔹 Source Code:**
- `src/` - Complete Python source (tier1, tier2, tier3, agents, operations)

**🔹 Prompts:**
- `prompts/shared/` - All shared prompt modules

**🔹 Scripts:**
- `scripts/cortex/` - Utility scripts for brain management

**🔹 Configuration:**
- `requirements.txt` - Python dependencies
- `cortex-operations.yaml` - Operations configuration
- `cortex.config.template.json` - Config template
- `setup.py` - Setup script

**🔹 Documentation:**
- `SETUP-FOR-COPILOT.md` - User setup guide
- `README.md` - Package overview

---

## ✅ Verification Checks

The script performs comprehensive verification:

### Critical Checks (Must Pass)
1. ✓ Directory structure (`.github/prompts`, `cortex-brain`, `src`, etc.)
2. ✓ Entry point exists (`.github/prompts/CORTEX.prompt.md`)
3. ✓ All required files present (SETUP, README, requirements.txt, etc.)
4. ✓ Files are not empty
5. ✓ No KDS-named files
6. ✓ File count in range (300-600 files)
7. ✓ Package size reasonable (1-10 MB)
8. ✓ Setup guide has correct instructions

### Quality Checks (Warnings if Failed)
- Source code presence (50+ Python files expected)
- No test/cache files included
- Package size optimization

### Verification Report

After deployment, you'll see:

```
╔════════════════════════════════════════════╗
║      PACKAGE VERIFICATION REPORT          ║
╚════════════════════════════════════════════╝

✅ Passed Checks (15):
   ✓ Directory: .github/prompts
   ✓ Directory: cortex-brain
   ✓ Entry Point: .github/prompts/CORTEX.prompt.md
   ✓ Setup Guide: SETUP-FOR-COPILOT.md
   ✓ Source code: 387 Python files
   ✓ No KDS-named files
   ✓ File count: 407 (expected range: 300-600)
   ✓ Package size: 3.95 MB (expected 1-10 MB)
   ... (and more)

╔════════════════════════════════════════════╗
║    ✅ PACKAGE READY FOR PRODUCTION        ║
╚════════════════════════════════════════════╝

📦 Package Details:
  Location:    publish/CORTEX/
  Files:       407
  Size:        3.95 MB
  Pass Rate:   100%

🚀 Deployment Instructions:
  1. Copy to target:
     xcopy /E /I /H /Y publish\CORTEX C:\target-app\cortex

  2. In target app, open VS Code Copilot Chat:
     'onboard this application'

✨ CORTEX preserves existing knowledge - upgrades are safe!
```

---

## 🎯 How Users Deploy

Once published, users follow these simple steps:

### Step 1: Copy CORTEX Folder

```powershell
# Windows
xcopy /E /I /H /Y D:\PROJECTS\CORTEX\publish\CORTEX C:\their-app\cortex

# Mac/Linux
cp -r /path/to/publish/CORTEX ./cortex
```

### Step 2: Onboard with Copilot

Open their application in VS Code, then in Copilot Chat:

```
onboard this application
```

**That's it!** CORTEX will:
- Detect existing installations and preserve knowledge
- Copy entry points to their app's `.github/` folder
- Initialize brain databases (if needed)
- Configure for their application
- Start helping immediately

---

## 🔍 Troubleshooting

**Verification fails:**
- Review failed checks in the report
- Fix issues in source files
- Re-run publish script

**Package size too small:**
- Check if source files copied correctly
- Verify `src/` directory has Python files

**Missing files:**
- Check source directory structure
- Ensure all required files exist in workspace

---

## 📝 After Publishing

1. **Test the package locally**
   ```powershell
   cd publish/CORTEX
   ls  # Verify structure
   ```

2. **Deploy to test application**
   - Copy to a test app
   - Run onboarding
   - Verify functionality

3. **Commit to repository**
   ```bash
   git add publish/CORTEX
   git commit -m "Publish CORTEX 3.0 - Verified production package"
   git push
   ```

---

## ✨ Key Benefits

- **Single Command:** `/CORTEX deploy` does everything
- **Verified:** 15+ checks ensure package integrity
- **Safe:** Preserves existing knowledge during upgrades
- **Complete:** All components included (407 files)
- **Ready:** Production-verified and tested
   - Copies README.md

6. **Copy Configuration**
   - Copies kds.config.json

7. **Create Production README**
   - Generates comprehensive quick start guide
   - Includes all commands and examples
   - Documents architecture and features
   - Adds deployment metadata

8. **Create Git Tag**
   - Tags with format: `v{version}-release-{timestamp}`
   - Example: `v1.0-release-20251122-095533`

---

## 🔧 Usage Examples

### Example 1: Simple Deployment

```powershell
PS D:\PROJECTS\CORTEX> .\scripts\deploy-cortex-prompts.ps1

# Output:
# ╔════════════════════════════════════════════╗
# ║     📦 CORTEX PRODUCTION DEPLOYMENT       ║
# ╚════════════════════════════════════════════╝
# 
# ✅ Copied 8 prompt files
# ✅ Copied 2 documentation files
# ✅ Configuration copied
# ✅ Production README created
# 
# 🎉 CORTEX v1.0 is ready for production use!
# 📦 Package location: publish/
```

### Example 2: Dry Run

```powershell
PS D:\PROJECTS\CORTEX> .\scripts\deploy-cortex-prompts.ps1 -DryRun -Force

# Shows what would be deployed without making changes
# Files: 12
# Version: v1.0
# Tag: v1.0-release-20251122-095533
```

### Example 3: Custom Version

```powershell
PS D:\PROJECTS\CORTEX> .\scripts\deploy-cortex-prompts.ps1 -Version "1.1" -Force

# Deploys as v1.1 regardless of CORTEX-DNA.md version
```

---

## 📦 Deployment Output

After deployment, the `publish/` folder structure:

```
publish/
├── README.md                    # Production quick start guide
├── kds.config.json              # System configuration
├── prompts/                     # User-facing prompts
│   ├── kds.md                  # Master command
│   ├── plan.md                 # Planning
│   ├── execute.md              # Execution
│   ├── test.md                 # Testing
│   ├── validate.md             # Validation
│   ├── resume.md               # Resume work
│   ├── correct.md              # Fix issues
│   └── govern.md               # Governance
├── docs/                        # Documentation
│   ├── CORTEX-DNA.md           # Core principles
│   └── README.md               # Project overview
└── templates/                   # Empty (for future use)
```

---

## 🎯 Post-Deployment

### Verify Deployment

```powershell
# Check published files
Get-ChildItem publish -Recurse

# Review production README
code publish/README.md

# Test a prompt
@workspace #file:publish/prompts/kds.md request="help"
```

### Share with Team

```powershell
# Option 1: Compress and share
Compress-Archive -Path publish/* -DestinationPath CORTEX-v1.0.zip

# Option 2: Push tag to remote
git push origin v1.0-release-20251122-095533

# Option 3: Copy to shared location
Copy-Item publish/* -Destination "\\network\share\CORTEX" -Recurse
```

### Version Tracking

View all releases:

```powershell
git tag -l "v*-release-*" | Sort-Object -Descending
```

---

## 🛡️ Safety Features

### Dry Run Mode

Always test first:

```powershell
.\scripts\deploy-cortex-prompts.ps1 -DryRun
```

### Confirmation Prompts

By default, script asks for confirmation before deploying. Skip with `-Force`.

### Version Tracking

Every deployment creates a git tag:

- **Format:** `v{version}-release-{timestamp}`
- **Example:** `v1.0-release-20251122-095533`

### Non-Destructive

- ✅ Creates new `publish/` folder (doesn't modify source)
- ✅ No git branch changes
- ✅ No remote pushes (only local tags)
- ✅ Easy to re-run and update

---

## 📋 Deployment Checklist

Before deploying:

- [ ] All prompt files tested and working
- [ ] CORTEX-DNA.md version number updated
- [ ] README.md reflects current features
- [ ] Configuration file (kds.config.json) is correct
- [ ] No work-in-progress code in prompts
- [ ] Documentation is up to date

After deploying:

- [ ] Review files in `publish/` folder
- [ ] Test prompts work from publish folder
- [ ] Verify README.md is accurate
- [ ] Share with team or push tag to remote
- [ ] Document any breaking changes

---

## 🆘 Troubleshooting

### Issue: Version Not Extracted

**Problem:** Script uses default version 1.0

**Solution:** Update `cortex-design/CORTEX-DNA.md`:

```markdown
**Version:** 1.1
```

### Issue: Files Missing

**Problem:** Some prompt files not copied

**Solution:** Check file names match expected patterns in script:

```powershell
# Expected files
prompts/user/kds.md
prompts/user/plan.md
prompts/user/execute.md
# etc.
```

### Issue: Permission Denied

**Problem:** Can't create publish folder

**Solution:** Run PowerShell as Administrator or choose different output path:

```powershell
.\scripts\deploy-cortex-prompts.ps1 -OutputPath "C:\Temp\cortex-release"
```

---

## 📚 Related Documentation

- **[CORTEX-DNA.md](../../cortex-design/CORTEX-DNA.md)** - Core design principles
- **[README.md](../../README.md)** - Project overview
- **[DEPLOYMENT-GUIDE.md](../../DEPLOYMENT-GUIDE.md)** - This deployment documentation

---

## 🎯 Success Criteria

Deployment is successful when:

- ✅ `publish/` folder created with 12 files
- ✅ All 8 prompt files present
- ✅ Production README generated
- ✅ Git tag created
- ✅ Files work when referenced from publish folder
- ✅ No source code or dev tools included

---

## 🎉 Summary

The `/CORTEX deploy` command provides a simple way to package production-ready CORTEX:

- **One command:** `.\scripts\deploy-cortex-prompts.ps1`
- **Clean output:** Only user-facing files, no dev tools
- **Version tracking:** Every deployment tagged
- **Non-destructive:** Safe to re-run anytime
- **Fast:** Deploys in seconds

**Ready to deploy?** Run the script and start using CORTEX in production!

---

**Last Updated:** 2025-11-22  
**Version:** 1.0  
**Status:** ✅ PRODUCTION READY

---

## 💡 Quick Reference

**Deploy CORTEX:**
```powershell
.\scripts\deploy-cortex-prompts.ps1
```

**Dry run:**
```powershell
.\scripts\deploy-cortex-prompts.ps1 -DryRun
```

**Skip prompts:**
```powershell
.\scripts\deploy-cortex-prompts.ps1 -Force
```

**Custom version:**
```powershell
.\scripts\deploy-cortex-prompts.ps1 -Version "1.1"
```

---

**End of CORTEX Deployment Guide**
