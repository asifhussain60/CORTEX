# CORTEX Production Deployment Guide

**Version:** 1.0  
**Last Updated:** 2025-11-22  
**Status:** ✅ READY FOR USE

---

## 🎯 Overview

This guide documents the new `/CORTEX deploy` command that deploys the production version of CORTEX documentation to the main branch.

### What This Does

The deployment workflow:
1. ✅ Builds the documentation site using MkDocs
2. ✅ **DELETES all files and folders** from the main branch
3. ✅ Publishes **ONLY** the contents of the `site/` folder (user-facing features)
4. ✅ Commits and pushes to main branch with deployment tags
5. ✅ Returns to your original working branch

### Key Benefits

- **Simple Command:** Just use `/CORTEX deploy`
- **Clean Deployment:** No source code in production, only built documentation
- **Version Tracking:** Every deployment is tagged for easy rollback
- **Safety Measures:** Dry-run mode, confirmations, automatic stashing

---

## 🚀 Quick Start

### Method 1: GitHub Copilot Command (Recommended)

```bash
/CORTEX deploy
```

This will:
- Load `#file:prompts/user/CORTEX.md`
- Guide you through the deployment process
- Run the deployment script with safety checks

### Method 2: PowerShell Script Directly

```powershell
# Interactive deployment with confirmations
.\scripts\deploy-production.ps1

# Deploy with specific version
.\scripts\deploy-production.ps1 -Version "1.1"

# Dry run (preview without changes)
.\scripts\deploy-production.ps1 -DryRun

# Skip confirmations
.\scripts\deploy-production.ps1 -Force

# Skip build step (use existing site/)
.\scripts\deploy-production.ps1 -SkipBuild
```

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version number incremented in `cortex-design/CORTEX-DNA.md`
- [ ] MkDocs build succeeds: `mkdocs build --clean`
- [ ] Site content reviewed in local browser
- [ ] No admin-only content in `site/` folder
- [ ] Current branch changes committed
- [ ] Team notified of deployment (if applicable)

---

## 🔧 Deployment Process

### Step-by-Step

1. **Pre-Deployment Validation**
   - Checks git repository status
   - Verifies site folder exists
   - Extracts version from CORTEX-DNA.md

2. **Build Production Site**
   - Runs `mkdocs build --clean`
   - Validates build success
   - Confirms site/index.html exists

3. **Confirmation Prompt** (unless `-Force`)
   - ⚠️ WARNING: Destructive operation
   - Requires typing "yes" to proceed

4. **Prepare Deployment**
   - Stashes uncommitted changes (if any)
   - Checks out main branch
   - Pulls latest changes

5. **Delete All Files** (Nuclear Option)
   - Removes all tracked files from main
   - Cleans working directory
   - **This is the point of no return**

6. **Copy Production Site**
   - Copies all `site/*` contents to root
   - Stages all new files

7. **Commit and Tag**
   - Creates deployment commit with metadata
   - Tags with format: `v{version}-deploy-{timestamp}`
   - Example: `v1.0-deploy-20251122-143022`

8. **Push to Remote**
   - Force pushes main branch
   - Pushes deployment tag

9. **Cleanup**
   - Returns to original branch
   - Restores stashed changes (if any)

---

## 📊 Example Deployment

```powershell
PS D:\PROJECTS\CORTEX> .\scripts\deploy-production.ps1 -DryRun -Force

╔════════════════════════════════════════════╗
║     🚀 CORTEX PRODUCTION DEPLOYMENT       ║
╚════════════════════════════════════════════╝

🔍 DRY RUN MODE - No changes will be made

📋 Step 1/8: Pre-Deployment Validation
  Current branch: main
  Extracted version: 1.0
✅ Validation complete

🔨 Step 2/8: Building Production Site
  [DRY RUN] Would run: mkdocs build --clean
✅ Build complete

🔄 Step 3/8: Preparing Deployment
  [DRY RUN] Would checkout main and pull latest
  Deployment tag: v1.0-deploy-20251122-094331
✅ Ready for deployment

🗑️  Step 4/8: Deleting All Files from Main Branch
  This is the point of no return...
  [DRY RUN] Would delete all files from main branch
✅ Main branch cleaned

📦 Step 5/8: Copying Production Site
  [DRY RUN] Would copy site/* to root and stage
✅ Production site copied

💾 Step 6/8: Committing Deployment
  [DRY RUN] Would commit with message:
🚀 Deploy CORTEX v1.0 to production
...
✅ Changes committed and tagged

🚀 Step 7/8: Pushing to Remote
  [DRY RUN] Would force push main branch
  [DRY RUN] Would push tag: v1.0-deploy-20251122-094331
✅ Pushed to remote

🔄 Step 8/8: Cleanup
  [DRY RUN] Would return to branch: main
✅ Cleanup complete

╔════════════════════════════════════════════╗
║      ✅ DEPLOYMENT SUCCESSFUL              ║
╚════════════════════════════════════════════╝

  Branch:  main
  Version: v1.0
  Tag:     v1.0-deploy-20251122-094331
  URL:     https://github.com/asifhussain60/CORTEX
```

---

## 🛡️ Safety Features

### Dry Run Mode

Test the deployment without making any changes:

```powershell
.\scripts\deploy-production.ps1 -DryRun
```

This shows you exactly what would happen without modifying anything.

### Confirmation Prompts

By default, the script asks for confirmation:
1. Before starting (if uncommitted changes exist)
2. Before destructive operation (deleting main branch files)

Skip confirmations with `-Force` flag (use carefully!).

### Automatic Stashing

If you have uncommitted changes:
- Script stashes them before deployment
- Restores them after returning to your branch
- Stash message includes timestamp for tracking

### Version Tracking

Every deployment creates a git tag:
- **Format:** `v{version}-deploy-{timestamp}`
- **Example:** `v1.0-deploy-20251122-143022`

View deployment history:
```powershell
git tag -l "v*-deploy-*" | Sort-Object -Descending
```

---

## 🔄 Rollback Procedure

If deployment fails or issues are found:

### Step 1: Find Previous Deployment

```powershell
# List recent deployments
git tag -l "v*-deploy-*" | Sort-Object -Descending | Select-Object -First 5
```

### Step 2: Rollback to Previous Version

```powershell
# Checkout main branch
git checkout main

# Reset to previous deployment tag
git reset --hard v1.0-deploy-20251122-120000

# Force push to remote
git push origin main --force
```

### Step 3: Tag the Rollback

```powershell
# Create rollback tag for tracking
$rollbackTag = "v1.0-rollback-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
git tag -a $rollbackTag -m "Rollback to v1.0-deploy-20251122-120000"
git push origin $rollbackTag
```

---

## 📝 Post-Deployment Verification

After deployment, verify:

1. **Site Accessible**
   - Visit: https://asifhussain60.github.io/CORTEX
   - Check homepage loads correctly

2. **Navigation Works**
   - Test all menu links
   - Verify internal links work
   - Check breadcrumbs

3. **Search Functions**
   - Test search functionality
   - Verify results are accurate

4. **Images Load**
   - Check all images display
   - Verify diagrams render

5. **No 404s**
   - Click through major pages
   - Test external links

---

## 🏗️ Branch Strategy

### Development Workflow

```
feature-branch or develop
  ├── All source files
  ├── prompts/
  ├── scripts/
  ├── docs/
  ├── src/
  ├── tests/
  └── tooling/
      │
      ├── mkdocs build --clean
      │
      └── site/ (generated, gitignored)
          │
          └── /CORTEX deploy
              │
              └── main branch
                  └── ONLY site/ contents (production)
```

### Source of Truth

- **Development:** Feature branches contain all source files
- **Production:** Main branch contains ONLY built site
- **Version:** CORTEX-DNA.md defines the official version number

### What Gets Deployed

**✅ INCLUDED (User Features):**
- Built documentation site (`site/` folder)
- User guides
- Feature reference
- Getting started guides
- Public API documentation

**❌ EXCLUDED (Admin/Dev Only):**
- Source code (`src/`, `prompts/`, `scripts/`)
- Development tools (`tooling/`)
- Test files (`tests/`)
- Internal documentation (`cortex-design/`, `cortex-brain/`)
- Configuration files (`.vscode/`, `.github/`)

---

## ⚙️ Configuration

### Version Number

The script automatically extracts the version from `cortex-design/CORTEX-DNA.md`:

```markdown
**Version:** 1.0
```

Override with `-Version` parameter:

```powershell
.\scripts\deploy-production.ps1 -Version "1.1"
```

### MkDocs Configuration

Ensure your `mkdocs.yml` (if it exists) is configured correctly for production builds.

### Git Remote

The script pushes to `origin/main`. Verify your remote:

```powershell
git remote -v
```

---

## 🚨 Troubleshooting

### Build Fails

**Problem:** `mkdocs build --clean` fails

**Solution:**
1. Check if MkDocs is installed: `mkdocs --version`
2. Install if missing: `pip install mkdocs-material`
3. Review build errors in terminal
4. Fix documentation issues
5. Re-run deployment

### Push Rejected

**Problem:** `git push origin main --force` rejected

**Solution:**
1. Verify you have push access to the repository
2. Check if branch protection rules block force push
3. Contact repository administrator if needed

### Site Folder Missing

**Problem:** `site/index.html` not found

**Solution:**
1. Run `mkdocs build --clean` manually
2. Verify no errors during build
3. Check if `site/` folder was created
4. Re-run deployment with `-SkipBuild` if site exists

### Wrong Branch After Deployment

**Problem:** Not on original branch after deployment

**Solution:**
```powershell
git checkout <your-branch-name>
git stash pop  # If you had stashed changes
```

---

## 📚 Related Documentation

- **[CORTEX.md](prompts/user/CORTEX.md)** - Full deployment workflow documentation
- **[deploy-production.ps1](scripts/deploy-production.ps1)** - Deployment script source
- **[CORTEX-DNA.md](cortex-design/CORTEX-DNA.md)** - CORTEX design principles

---

## 🎯 Success Criteria

Deployment is successful when:

- ✅ Main branch contains ONLY `site/` contents
- ✅ Site builds without errors
- ✅ All links work correctly
- ✅ Search functionality operational
- ✅ Deployment tagged correctly
- ✅ Original branch restored
- ✅ No source code exposed in production
- ✅ Site accessible at GitHub Pages URL

---

## 📞 Support

If you encounter issues:

1. Check deployment logs in terminal
2. Review this troubleshooting section
3. Use `-DryRun` to preview without changes
4. Verify prerequisites in checklist
5. Use rollback procedure if needed

---

## 🎉 Summary

The `/CORTEX deploy` command provides a simple, safe, and repeatable way to deploy your production documentation:

- **One command:** `/CORTEX deploy` or `.\scripts\deploy-production.ps1`
- **Safety first:** Dry-run mode, confirmations, automatic stashing
- **Version tracking:** Every deployment tagged for easy rollback
- **Clean production:** Only user-facing content, no source code

**Ready to deploy?** Run `/CORTEX deploy` and follow the prompts!

---

**Last Updated:** 2025-11-22  
**Version:** 1.0  
**Status:** ✅ PRODUCTION READY
