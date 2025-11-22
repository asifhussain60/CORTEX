# CORTEX Deploy - Production Deployment Workflow

**Purpose:** Deploy production-ready CORTEX user prompts to the `publish/` folder. This command packages ONLY user-facing prompt files and essential documentation for clean distribution.

**Version:** 1.0  
**Status:** 🚀 ACTIVE  
**Command:** `/CORTEX deploy`

---

## 🎯 What This Does

This workflow:
1. ✅ Creates a clean `publish/` folder structure
2. ✅ Copies ONLY user-facing prompt files (8 prompts)
3. ✅ Includes essential documentation (CORTEX-DNA.md, README.md)
4. ✅ Includes configuration (kds.config.json)
5. ✅ Creates a production README with quick start guide
6. ✅ Tags the deployment for version tracking

**📦 OUTPUT:** Clean production package in `publish/` folder ready for distribution.

---

## 📋 Prerequisites

Before deploying, ensure:
- ✅ All user prompt files are complete in `prompts/user/`
- ✅ CORTEX-DNA.md is up to date with current version
- ✅ Configuration file (kds.config.json) is correct
- ✅ All prompts are tested and working
- ✅ README.md reflects current features

---

## 🚀 Deployment Process

### Quick Deploy

```powershell
# Simple deployment (recommended)
.\scripts\deploy-cortex-prompts.ps1

# Deploy with specific version
.\scripts\deploy-cortex-prompts.ps1 -Version "1.1"

# Preview without changes (dry run)
.\scripts\deploy-cortex-prompts.ps1 -DryRun

# Skip confirmations
.\scripts\deploy-cortex-prompts.ps1 -Force

# Custom output path
.\scripts\deploy-cortex-prompts.ps1 -OutputPath "release"
```

### What Gets Deployed

The script creates a clean `publish/` folder with:

**📦 User Prompts (publish/prompts/):**
- `kds.md` - Master command (one command for everything)
- `plan.md` - Create multi-phase implementation plans
- `execute.md` - Execute tasks from plans
- `test.md` - Generate and run Playwright tests
- `validate.md` - System health checks
- `resume.md` - Resume interrupted work
- `correct.md` - Fix issues and errors
- `govern.md` - Enforce governance rules

**📄 Documentation (publish/docs/):**
- `CORTEX-DNA.md` - Core design principles
- `README.md` - Project overview

**⚙️ Configuration (publish/):**
- `kds.config.json` - System configuration
- `README.md` - Production quick start guide

### Step-by-Step Process

1. **Pre-Deployment Validation**
   - Verifies CORTEX root directory
   - Extracts version from CORTEX-DNA.md
   - Validates required directories exist
   - Shows deployment plan

2. **Confirmation** (unless `-Force`)
   - Displays deployment summary
   - Requires "yes" to proceed

3. **Clean Output Directory**
   - Removes existing `publish/` folder (if exists)
   - Creates clean directory structure
   - Creates subdirectories: `prompts/`, `docs/`, `templates/`

4. **Copy User Prompts**
   - Copies 8 user-facing prompt files
   - Shows progress for each file

5. **Copy Documentation**
   - Copies CORTEX-DNA.md
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
