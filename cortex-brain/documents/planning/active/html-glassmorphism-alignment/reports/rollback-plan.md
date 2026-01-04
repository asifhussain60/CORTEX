# 🔄 Rollback Plan
## HTML Glassmorphism Alignment - Emergency Recovery Procedures

**Plan ID:** html-glassmorphism-alignment  
**Phase:** 11 - Deployment Validation  
**Created:** 2026-01-04  
**Version:** 1.0

---

## 🎯 Overview

This document provides comprehensive rollback procedures for the HTML Glassmorphism Alignment deployment. It covers all failure scenarios from minor issues to catastrophic site-wide failures, with step-by-step recovery instructions.

---

## 🚨 Rollback Scenarios

### Scenario Matrix

| Severity | Trigger Condition | Response Time | Rollback Method | Impact |
|----------|------------------|---------------|-----------------|--------|
| **P0 - Critical** | Site-wide 500 errors, security breach, complete layout failure | <5 minutes | Full git revert + backup restore | High (10-20 min downtime) |
| **P1 - High** | Major feature broken (navigation, search), >25% pages broken | <15 minutes | Partial revert or hotfix | Medium (specific features down) |
| **P2 - Medium** | Minor layout issues, broken links, CSS glitches | <2 hours | Hotfix deployment | Low (degraded UX) |
| **P3 - Low** | Non-critical cosmetic issues, documentation typos | <24 hours | Scheduled fix | Minimal |

---

## 🛡️ Pre-Rollback Validation

**Before executing ANY rollback, verify:**

1. **Confirm the Issue:**
   - [ ] Issue reproduced in 2+ browsers
   - [ ] Issue not caused by browser cache (test incognito)
   - [ ] Issue not caused by CDN propagation delay (wait 10 min)
   - [ ] Issue affects multiple users (not local)

2. **Assess Impact:**
   - [ ] Number of pages affected: ____
   - [ ] User-reported issues: ____
   - [ ] Critical path broken: YES / NO
   - [ ] Severity rating: P0 / P1 / P2 / P3

3. **Check Backup Availability:**
   ```powershell
   # Verify backups exist
   Get-ChildItem "backups\html-alignment-20260104_*" -Recurse -File | Measure-Object
   
   # Expected: 5+ files (T1 backups minimum)
   ```

4. **Verify Git History:**
   ```bash
   # Check last 5 commits
   git log --oneline -5
   
   # Ensure Phase 10 commit is present (last known good state)
   ```

---

## 🔴 P0 - Critical Rollback (Site-Wide Failure)

### Trigger Conditions

- **Site completely down:** All pages return 500/503 errors
- **Security vulnerability exposed:** XSS, data leak, unauthorized access
- **Complete layout failure:** All pages show broken HTML/CSS
- **Production database corruption** (if applicable)

### Immediate Actions (Execute in Order)

#### Step 1: Emergency Communication (0-2 minutes)

```bash
# Create incident ticket
touch reports/incident-P0-$(date +%Y%m%d_%H%M%S).md

# Alert team (if applicable)
# - Slack/Teams: "P0 INCIDENT: Site-wide failure. Rollback in progress."
# - GitHub Issues: Create P0 incident issue
```

#### Step 2: Full Git Revert (2-7 minutes)

```bash
# Navigate to repo
cd D:\PROJECTS\CORTEX

# Identify current commit (broken state)
BROKEN_COMMIT=$(git rev-parse HEAD)
echo "Broken commit: $BROKEN_COMMIT"

# Find last known good commit (Phase 10 completion)
GOOD_COMMIT=$(git log --oneline --grep="Phase 10 Complete" -1 --format="%H")
echo "Good commit: $GOOD_COMMIT"

# Create emergency rollback branch
git checkout -b emergency/rollback-$(date +%Y%m%d_%H%M%S)

# Revert to good commit
git revert $BROKEN_COMMIT --no-edit

# If revert fails due to conflicts, hard reset (DESTRUCTIVE)
# git reset --hard $GOOD_COMMIT

# Force push to production branch
git push origin CORTEX-5.0 --force

# Wait 5 minutes for GitHub Pages rebuild
```

**Expected Result:** Site restored to Phase 10 state (last known good).

#### Step 3: Backup Restoration (if git revert insufficient)

```powershell
# PowerShell - Execute if git revert didn't work

# Restore all HTML files from backup
$BackupPath = Get-ChildItem "backups\html-alignment-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Host "Restoring from: $($BackupPath.FullName)"

# Copy HTML files
Copy-Item "$($BackupPath.FullName)\*.html" "docs\" -Recurse -Force

# Verify restoration
$RestoredCount = (Get-ChildItem "docs\*.html" -Recurse).Count
Write-Host "Restored $RestoredCount HTML files"

# Commit restoration
git add docs/
git commit -m "P0 ROLLBACK: Restore HTML files from backup $($BackupPath.Name)"
git push origin CORTEX-5.0 --force
```

#### Step 4: Verify Rollback Success (7-12 minutes)

```bash
# Wait 5 minutes for GitHub Pages rebuild
sleep 300

# Test critical paths
echo "Testing critical paths..."

# Home page
curl -I https://<username>.github.io/<repo>/index.html | grep "200 OK"

# Architecture hub
curl -I https://<username>.github.io/<repo>/architecture/index.html | grep "200 OK"

# Orchestrators hub
curl -I https://<username>.github.io/<repo>/orchestrators/index.html | grep "200 OK"

# All tests should return "200 OK"
```

**Manual Verification:**
1. Open 3 critical pages in browser
2. Verify layout renders correctly
3. Check console for 0 JavaScript errors
4. Test navigation links

#### Step 5: Post-Rollback Actions (12-30 minutes)

1. **Communicate Status:**
   - Update incident ticket: "Site restored. Root cause analysis in progress."
   - Notify stakeholders of resolution

2. **Root Cause Analysis:**
   - What triggered the failure?
   - What code/config caused it?
   - Why did testing miss it?

3. **Create Incident Report:**
   ```markdown
   # P0 Incident Report - [Date]
   
   ## Summary
   - **Incident ID:** P0-20260104-001
   - **Duration:** [start time] - [end time] (X minutes)
   - **Impact:** Site-wide failure, all pages affected
   - **Root Cause:** [describe]
   
   ## Timeline
   - [HH:MM] Issue detected
   - [HH:MM] Rollback initiated
   - [HH:MM] Git revert completed
   - [HH:MM] Site restored
   - [HH:MM] Verification complete
   
   ## Root Cause
   [Detailed analysis]
   
   ## Prevention Measures
   - [ ] Add test case: [specific test]
   - [ ] Update deployment checklist: [item]
   - [ ] Improve monitoring: [metric]
   ```

4. **Update Deployment Checklist:**
   - Add new validation step to prevent recurrence
   - Update rollback time estimates based on actual

---

## 🟠 P1 - High Severity Rollback (Major Feature Broken)

### Trigger Conditions

- **Navigation broken:** Menu not functional, users can't navigate
- **Search broken:** Search feature returns errors
- **25%+ pages broken:** Quarter of site affected
- **Critical orchestrator docs inaccessible:** Planning, ADO, etc.

### Rollback Options

#### Option A: Partial File Revert (Faster, Lower Risk)

**Use When:** Issue isolated to specific files (1-5 files).

```bash
# Identify broken files
BROKEN_FILES=(
    "docs/orchestrators/index.html"
    "docs/orchestrators/planning-v5.html"
)

# Restore from git history (last known good commit)
GOOD_COMMIT=$(git log --oneline --grep="Phase 10 Complete" -1 --format="%H")

for file in "${BROKEN_FILES[@]}"; do
    echo "Restoring $file from $GOOD_COMMIT"
    git checkout $GOOD_COMMIT -- $file
done

# Commit restoration
git add "${BROKEN_FILES[@]}"
git commit -m "P1 ROLLBACK: Restore ${#BROKEN_FILES[@]} broken files"
git push origin CORTEX-5.0
```

#### Option B: Hotfix Deployment (If Issue Easily Fixable)

**Use When:** Root cause identified, fix takes <30 minutes.

```bash
# Create hotfix branch
git checkout -b hotfix/nav-fix

# Apply fix (example: restore navigation HTML)
# [Manual: Edit file, fix issue]

# Test locally
python -m http.server 8000
# Open http://localhost:8000/docs/index.html
# Verify fix works

# Commit and deploy
git add .
git commit -m "HOTFIX: Restore navigation functionality"
git push origin hotfix/nav-fix

# Merge to main (or create PR if time permits)
git checkout CORTEX-5.0
git merge hotfix/nav-fix
git push origin CORTEX-5.0
```

#### Option C: Full Rollback (If Issue Widespread)

Follow **P0 Critical Rollback** procedure above.

### Verification

```bash
# Test affected feature
# Example: Navigation
curl https://<username>.github.io/<repo>/index.html | grep '<nav'

# Manual: Load page, test feature
```

---

## 🟡 P2 - Medium Severity Rollback (Minor Issues)

### Trigger Conditions

- **Broken links:** <25% of links return 404
- **CSS glitches:** Minor visual issues (spacing, colors)
- **Icon-title spacing regressed:** Icons not aligned
- **Mobile responsive issues:** Layout breaks on some breakpoints

### Rollback Strategy

**Priority:** Fix-forward (hotfix) rather than rollback.

#### Hotfix Workflow

```bash
# Create hotfix branch
git checkout -b hotfix/css-glitch

# Identify issue
# Example: Icon-title spacing broken on 2 pages

# Restore affected files from backup
Copy-Item "backups\html-alignment-20260104_*\architecture\index.html" "docs\architecture\" -Force

# OR: Apply manual fix
# [Edit file, fix CSS class]

# Test locally
python -m http.server 8000

# Commit and deploy
git add .
git commit -m "HOTFIX: Fix icon-title spacing on architecture pages"
git push origin CORTEX-5.0
```

### Decision Matrix

| Issue Type | Fix-Forward? | Rollback? | Rationale |
|------------|--------------|-----------|-----------|
| Broken links | ✅ Yes | ❌ No | Links can be fixed individually |
| CSS glitches | ✅ Yes | ❌ No | Visual only, no functionality impact |
| Icon spacing | ✅ Yes | ❌ No | Localized issue, easy fix |
| Mobile layout | ✅ Yes | ⚠️ If critical | Depends on severity |

---

## 🟢 P3 - Low Severity (Scheduled Fix)

### Trigger Conditions

- **Documentation typos:** Spelling errors, grammar issues
- **Non-critical cosmetic issues:** Minor color variations
- **Accessibility warnings:** WCAG AA still met, but AAA violations

### Strategy

**No rollback required.** Create GitHub Issue, fix in next deployment cycle.

```bash
# Create issue
gh issue create --title "Fix typo in orchestrators/planning-v5.html" --label "P3,documentation"

# Schedule fix for next sprint
```

---

## 📊 Rollback Success Criteria

### P0 Critical Rollback

**Success When:**
- [ ] All 6 critical paths return 200 OK
- [ ] Home page renders correctly in 3 browsers
- [ ] Navigation functional
- [ ] Console shows 0 critical JavaScript errors
- [ ] Site downtime <20 minutes

### P1 High Severity Rollback

**Success When:**
- [ ] Affected feature restored (navigation, search, etc.)
- [ ] 10 sample pages render correctly
- [ ] User-reported issues resolved
- [ ] Downtime <30 minutes (for rollback) or <2 hours (for hotfix)

### P2 Medium Severity Hotfix

**Success When:**
- [ ] Visual issues resolved
- [ ] Links functional
- [ ] Mobile layout restored
- [ ] Fix deployed within 4 hours

---

## 🛠️ Rollback Tools & Scripts

### Quick Reference

| Tool | Purpose | Command |
|------|---------|---------|
| **Git Revert** | Undo last commit | `git revert HEAD` |
| **Git Reset** | Hard reset (DESTRUCTIVE) | `git reset --hard $GOOD_COMMIT` |
| **Backup Restore** | Restore from timestamped backup | `Copy-Item backups\*.html docs\ -Force` |
| **Verification** | Test critical paths | `curl -I <URL>` |
| **Rollback Script** | Automated rollback | `.\cortex-toolkit\rollback-transformation.ps1` |

### Pre-Configured Rollback Script

**File:** `cortex-toolkit/rollback-transformation.ps1`

```powershell
# Emergency Rollback Script
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("P0","P1","P2")]
    [string]$Severity,
    
    [string]$BackupPath = "backups\html-alignment-20260104_*",
    [string]$TargetBranch = "CORTEX-5.0"
)

Write-Host "🔄 EMERGENCY ROLLBACK - Severity: $Severity" -ForegroundColor Red

# P0: Full rollback
if ($Severity -eq "P0") {
    Write-Host "Executing full git revert..."
    git revert HEAD --no-edit
    git push origin $TargetBranch --force
    
    Write-Host "Restoring from backup..."
    $Backup = Get-ChildItem $BackupPath | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Copy-Item "$($Backup.FullName)\*.html" "docs\" -Recurse -Force
    
    git add docs/
    git commit -m "P0 ROLLBACK: Full restoration from backup"
    git push origin $TargetBranch
}

# P1: Partial rollback (restore specific files)
if ($Severity -eq "P1") {
    Write-Host "Executing partial rollback..."
    # [User must specify files to restore]
    Write-Host "Manual intervention required: Specify broken files"
}

# P2: No automated rollback (hotfix recommended)
if ($Severity -eq "P2") {
    Write-Host "P2 severity: Hotfix recommended over rollback"
}

Write-Host "✅ Rollback complete. Verify site functionality." -ForegroundColor Green
```

---

## 📋 Post-Rollback Checklist

### Immediate (0-30 minutes)

- [ ] Verify site functionality (6 critical paths)
- [ ] Communicate status to stakeholders
- [ ] Update incident ticket with resolution
- [ ] Document timeline in incident report

### Short-Term (1-4 hours)

- [ ] Complete root cause analysis
- [ ] Create GitHub Issues for fixes
- [ ] Update deployment checklist with new validations
- [ ] Test fix in staging environment

### Long-Term (1-7 days)

- [ ] Re-deploy fixed version
- [ ] Conduct post-mortem meeting
- [ ] Update rollback procedures based on lessons learned
- [ ] Improve monitoring/alerting

---

## 🔗 Related Documentation

- **Deployment Checklist:** `deployment-checklist.md`
- **Deployment Validation Report:** `deployment-validation-report.md`
- **Acceptance Criteria:** `tracking/acceptance-criteria.yaml` (AC-13)
- **Phase 11 Plan:** `00-html-view-standardization.md` (lines 1500-1580)

---

**Status:** ✅ ROLLBACK PLAN COMPLETE  
**Next Review:** After first production deployment  
**Owner:** CORTEX Planning System  
**Last Updated:** 2026-01-04
