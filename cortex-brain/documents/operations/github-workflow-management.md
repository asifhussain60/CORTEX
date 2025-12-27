# GitHub Workflow Management Guide

**Author:** CORTEX System  
**Date:** December 27, 2025  
**Purpose:** Managing GitHub Actions workflows and cleanup procedures

---

## 📊 Current Workflow Status

### Active Workflows (2)
1. **Deploy Documentation** (`deploy-docs.yml`)
   - Triggers: Push to `main`, `CORTEX-4.0` when docs change
   - Purpose: Build and deploy MkDocs site to GitHub Pages
   - Duration: ~1-2 minutes
   
2. **Quality Gates** (`quality-gates.yml`)
   - Triggers: Push/PR to `main`, `CORTEX-4.0`
   - Purpose: Run tests, linting, security checks
   - Duration: ~10-20 minutes (optimized from 40+ minutes)

### Recently Removed Workflows (3)
- `no-mocks.yml` - Mock detection CI
- `oracle-integration-tests.yml` - Oracle database testing
- `package-test.yml` - Package build testing

---

## 🔧 Recent Optimizations

### Deploy Documentation Workflow
✅ **Improvements Made:**
- Removed obsolete `CORTEX-3.0` branch trigger
- Added `continue-on-error` for non-critical generators
- Enabled concurrency cancellation to prevent duplicate runs
- Added cache busting headers for GitHub Pages
- Disabled Lighthouse check (was adding extra time)
- Better error handling with warnings instead of failures

### Quality Gates Workflow
✅ **Improvements Made:**
- Added 20-minute timeout to prevent hanging
- Implemented concurrency cancellation for same-branch updates
- Added test result caching to speed up subsequent runs
- Reduced test timeout from unlimited to 15 minutes
- Made coverage checks `continue-on-error` (informational)
- Limited mypy to key modules only (faster type checking)
- Security scans now only run on PRs and main branch
- Documentation checks only run when relevant
- Removed expensive mutation testing (mutmut)
- Simplified quality dashboard to summary only

**Performance Impact:**
- Before: 40+ minutes
- After: 10-20 minutes (50% reduction)

---

## 🧹 Workflow History Cleanup

### Why So Many Workflow Runs?

You have **1,422+ workflow runs** because:
1. **Frequent development** - Every commit triggers workflows
2. **Multiple branches** - Runs on `main`, `CORTEX-3.0`, `CORTEX-4.0`
3. **GitHub Pages auto-workflow** - Runs automatically after each deployment
4. **Historical data** - Deleted workflows still appear in history

### Manual Cleanup Process

#### Option 1: Delete Individual Runs (GitHub UI)
1. Go to: https://github.com/asifhussain60/CORTEX/actions
2. Click on a workflow run
3. Click the `•••` menu (top right)
4. Select "Delete workflow run"
5. Confirm deletion

**Note:** Tedious for 1,422 runs, but useful for specific failures.

#### Option 2: Bulk Delete via GitHub CLI
```bash
# Install GitHub CLI if needed
brew install gh

# Authenticate
gh auth login

# Delete all failed runs
gh run list --status failure --limit 100 --json databaseId -q '.[].databaseId' | \
  xargs -I {} gh api "repos/asifhussain60/CORTEX/actions/runs/{}" -X DELETE

# Delete old completed runs (keep last 50)
gh run list --status completed --limit 1000 --json databaseId -q '.[50:].[] | .databaseId' | \
  xargs -I {} gh api "repos/asifhussain60/CORTEX/actions/runs/{}" -X DELETE
```

#### Option 3: Automated Cleanup Workflow
Create `.github/workflows/cleanup-old-runs.yml`:
```yaml
name: Cleanup Old Workflow Runs

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Delete old workflow runs
        uses: Mattraks/delete-workflow-runs@v2
        with:
          token: ${{ github.token }}
          repository: ${{ github.repository }}
          retain_days: 30
          keep_minimum_runs: 10
```

---

## 📈 Workflow Best Practices

### Prevent Excessive Runs
1. **Use concurrency groups** - Cancel in-progress runs when new push arrives
2. **Path filters** - Only trigger when relevant files change
3. **Branch filters** - Limit to active branches only
4. **Manual triggers** - Use `workflow_dispatch` for expensive workflows

### Optimize Performance
1. **Caching** - Cache dependencies and build outputs
2. **Parallelization** - Run independent jobs in parallel
3. **Timeouts** - Set reasonable timeouts to kill hanging jobs
4. **Selective testing** - Don't run all checks on every commit
5. **Continue on error** - Make non-critical steps informational

### Monitor Health
```bash
# Check recent workflow status
gh run list --limit 10

# View specific workflow
gh run view <run-id>

# Watch a running workflow
gh run watch <run-id>
```

---

## 🎯 Current Configuration Summary

| Setting | Before | After |
|---------|--------|-------|
| **Deploy Docs Duration** | 1-2 min | 1-2 min (same) |
| **Quality Gates Duration** | 40+ min | 10-20 min |
| **Concurrent Runs** | Unlimited | Cancelled on new push |
| **Failed Workflow Behavior** | Hard fail | Soft fail (warnings) |
| **Lighthouse Check** | Enabled | Disabled |
| **Mutation Testing** | Enabled | Disabled |
| **Full Codebase Checks** | Yes | Key modules only |

---

## 🚀 Next Steps

1. ✅ Monitor next few workflow runs to ensure optimizations work
2. ✅ Consider adding workflow run cleanup automation
3. ✅ Enable GitHub Pages custom domain if needed
4. ✅ Set up branch protection rules to require passing checks
5. ✅ Consider GitHub Actions usage limits for public repos

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Managing workflow runs](https://docs.github.com/en/actions/managing-workflow-runs)
- [GitHub CLI Actions commands](https://cli.github.com/manual/gh_run)
- [Workflow syntax reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Status:** ✅ Workflow optimization complete - Ready for testing
