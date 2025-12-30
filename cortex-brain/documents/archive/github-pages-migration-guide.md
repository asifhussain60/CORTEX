# GitHub Pages Migration: CORTEX 3.0 → CORTEX 4.0

**Author:** CORTEX System  
**Date:** December 27, 2025  
**Purpose:** Replace CORTEX 3.0 with CORTEX 4.0 on GitHub Pages

---

## 🎯 Objective

Ensure GitHub Pages serves documentation from **CORTEX-4.0** branch instead of CORTEX-3.0.

---

## ✅ Current Status

### Deployment Workflow Configuration
The `deploy-docs.yml` workflow has been updated to:
- ✅ Deploy from `CORTEX-4.0` branch
- ✅ Deploy from `main` branch
- ❌ **REMOVED** CORTEX-3.0 trigger

### Branch Status
```
Active Branches:
- CORTEX-4.0 ← Current development (DEPLOYING)
- CORTEX-3.0 ← Legacy (NO LONGER DEPLOYING)
- main        ← Stable (DEPLOYING)
```

---

## 🔧 GitHub Pages Configuration Steps

### Step 1: Verify Repository Settings (Manual Action Required)

⚠️ **You must complete this step manually in GitHub UI:**

1. Go to: https://github.com/asifhussain60/CORTEX/settings/pages

2. Under **"Build and deployment"**, verify:
   - **Source:** Deploy from a branch
   - **Branch:** `gh-pages` / `root`

3. **No changes needed** - the workflow automatically updates `gh-pages` branch

### Step 2: Workflow Will Handle Deployment

The optimized `deploy-docs.yml` workflow now:
- ✅ Triggers on push to `CORTEX-4.0` or `main`
- ✅ Does NOT trigger on `CORTEX-3.0` (removed)
- ✅ Deploys to `gh-pages` branch automatically
- ✅ Uses `force_orphan: true` (clean history)

---

## 🚀 Migration Process

### Automatic Migration (Happening Now)

When you push to `CORTEX-4.0`:
1. Workflow builds docs from `CORTEX-4.0` branch
2. Deploys to `gh-pages` branch (overwrites previous content)
3. GitHub Pages serves new content within 1-2 minutes

### Verify Deployment

After the current workflow completes:
```bash
# Check workflow status
curl -s "https://api.github.com/repos/asifhussain60/CORTEX/actions/runs?per_page=1" | \
  python3 -c "import sys, json; r = json.load(sys.stdin)['workflow_runs'][0]; print(f\"{r['name']}: {r['status']} - {r['conclusion']}\")"

# Visit your GitHub Pages site
open https://asifhussain60.github.io/CORTEX/
```

---

## 🧹 Clean Up CORTEX 3.0 (Optional)

### Option 1: Archive the Branch (Recommended)
```bash
# Create archive tag
git tag -a archive/CORTEX-3.0-$(date +%Y%m%d) CORTEX-3.0 -m "Archive CORTEX 3.0"
git push origin archive/CORTEX-3.0-$(date +%Y%m%d)

# Delete remote branch (keeps in history)
git push origin --delete CORTEX-3.0
```

### Option 2: Keep for Reference
Leave `CORTEX-3.0` branch intact but inactive (no deployments).

---

## 📊 What Changed

### Before (CORTEX 3.0 Active)
```yaml
# deploy-docs.yml
branches:
  - CORTEX-3.0  ← Deploying from here
  - CORTEX-4.0
  - main
```

### After (CORTEX 4.0 Active)
```yaml
# deploy-docs.yml
branches:
  - CORTEX-4.0  ← Now deploying from here
  - main
  # CORTEX-3.0 removed ← No longer deploys
```

---

## 🔍 Troubleshooting

### Issue: Old CORTEX 3.0 content still showing

**Solution:**
```bash
# Force redeploy from CORTEX-4.0
git commit --allow-empty -m "trigger: Force GitHub Pages redeploy from CORTEX-4.0"
git push origin CORTEX-4.0

# Wait 2-3 minutes, then hard refresh browser (Cmd+Shift+R)
```

### Issue: 404 errors on GitHub Pages

**Check:**
1. Repository settings → Pages → Source is set to `gh-pages`
2. Workflow completed successfully
3. `gh-pages` branch exists and has recent content

### Issue: Workflow failing

**Check:**
1. Recent workflow runs: https://github.com/asifhussain60/CORTEX/actions
2. Look for error messages in logs
3. Verify MkDocs builds locally: `mkdocs build`

---

## ✅ Verification Checklist

- [ ] Workflow completes successfully on CORTEX-4.0 push
- [ ] GitHub Pages URL loads without errors
- [ ] Documentation shows CORTEX 4.0 content
- [ ] Navigation works correctly
- [ ] Images and assets load properly
- [ ] No references to CORTEX 3.0 in deployed content

---

## 📝 Timeline

| Time | Event |
|------|-------|
| T+0  | Push to CORTEX-4.0 triggers workflow |
| T+1-2m | Workflow builds and deploys |
| T+2-3m | GitHub Pages updates (cache propagation) |
| T+3m | New content visible at https://asifhussain60.github.io/CORTEX/ |

---

## 🎉 Success Indicators

✅ **Workflow Success:**
- Deploy Documentation workflow shows green checkmark
- Quality Gates workflow completes (tests pass)

✅ **GitHub Pages Success:**
- Site loads at https://asifhussain60.github.io/CORTEX/
- Shows current CORTEX 4.0 content
- No 404 errors or broken links

✅ **CORTEX 3.0 Inactive:**
- Pushes to CORTEX-3.0 do NOT trigger deployments
- Only CORTEX-4.0 and main trigger deployments

---

## 📚 Related Documentation

- **Workflow Management:** `github-workflow-management.md`
- **Optimization Report:** `workflow-optimization-report.md`
- **MkDocs Config:** `mkdocs.yml` (root)

---

**Status:** 🟢 Migration in progress - workflow deploying CORTEX 4.0 content now
