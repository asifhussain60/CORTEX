# CORTEX 3.0 Repository Transition Plan

**Purpose:** Clean git-based transition from CORTEX 2.0 → 3.0 in same repository  
**Date:** November 13, 2025  
**Strategy:** Git branches/tags (NOT subfolders)  
**Working Directory:** `D:\PROJECTS\CORTEX` (always contains active version)

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

---

## 🎯 Core Principle

**"One repository, multiple versions via git branches. No subfolder pollution."**

- ✅ CORTEX 2.0 preserved in git history (accessible via tags/branches)
- ✅ CORTEX 3.0 becomes main development codebase
- ✅ Working directory clean (no `cortex-2.0/` or `cortex-3.0/` folders)
- ✅ Switch versions with `git checkout` (instant, no copying)

---

## 📋 Repository Structure Timeline

### Current State (Before Transition)

```
Repository: CORTEX
Branch: CORTEX-2.0
Working Directory: D:\PROJECTS\CORTEX\

D:\PROJECTS\CORTEX\
├── src/                    # CORTEX 2.0 code
├── tests/                  # CORTEX 2.0 tests
├── cortex-brain/           # Brain data (Tier 0-3)
├── prompts/                # Entry points and docs
├── .github/                # GitHub workflows
├── README.md               # CORTEX 2.0 README
└── ... (all 2.0 files)
```

### After Transition (CORTEX 3.0 Active)

```
Repository: CORTEX
Branch: main (or CORTEX-3.0)
Working Directory: D:\PROJECTS\CORTEX\

D:\PROJECTS\CORTEX\
├── src/                    # CORTEX 3.0 code (enhanced)
├── tests/                  # CORTEX 3.0 tests (580+ tests)
├── cortex-brain/           # Brain data (backward compatible + new features)
├── prompts/                # Entry points (3.0 enhanced)
├── .github/                # GitHub workflows (updated)
├── README.md               # CORTEX 3.0 README
└── ... (all 3.0 files)

# CORTEX 2.0 accessible via:
git checkout CORTEX-2.0-STABLE
# Working directory instantly becomes CORTEX 2.0 codebase
```

**Key Point:** No `cortex-2.0/` subfolder. Git manages versions transparently.

---

## 🔄 Transition Timeline

### Phase 0: Preparation (Before Any 3.0 Work)

**When:** Before starting Milestone 0 (test fixes)  
**Duration:** 30 minutes

#### Actions:

```bash
# 1. Ensure we're on CORTEX-2.0 branch with latest commits
git checkout CORTEX-2.0
git pull origin CORTEX-2.0

# 2. Create permanent CORTEX 2.0 tags
git tag -a v2.0.0 -m "CORTEX 2.0 Production Release - Token Optimization, 4-Tier Brain"
git tag -a CORTEX-2.0-STABLE -m "CORTEX 2.0 Stable Baseline (482/580 tests passing)"
git tag -a CORTEX-2.0-FINAL -m "CORTEX 2.0 Final Version (before 3.0 transition)"

# 3. Push tags to remote (GitHub)
git push origin v2.0.0
git push origin CORTEX-2.0-STABLE
git push origin CORTEX-2.0-FINAL

# 4. Create backup branch (optional extra safety)
git checkout -b CORTEX-2.0-archive
git push -u origin CORTEX-2.0-archive

# 5. Return to CORTEX-2.0
git checkout CORTEX-2.0
```

**Result:**
- CORTEX 2.0 permanently preserved with 3 tags
- Can always access via `git checkout v2.0.0` or `git checkout CORTEX-2.0-STABLE`
- Archive branch available as extra backup

---

### Phase 1: Create CORTEX 3.0 Development Branch

**When:** Ready to start Milestone 0 (test fixes)  
**Duration:** 5 minutes

#### Actions:

```bash
# 1. Branch from CORTEX-2.0 (3.0 starts as copy of 2.0)
git checkout CORTEX-2.0
git checkout -b CORTEX-3.0-dev

# 2. Push to remote
git push -u origin CORTEX-3.0-dev

# 3. Working directory is now CORTEX 3.0 development
# (but code is identical to 2.0 at this point)
```

**Result:**
- `CORTEX-3.0-dev` branch created
- Working directory (`D:\PROJECTS\CORTEX`) contains code ready for 3.0 enhancements
- Can switch back to 2.0 anytime: `git checkout CORTEX-2.0`

---

### Phase 2: CORTEX 3.0 Development (28 Weeks)

**When:** Milestone 0 through Milestone 5  
**Branch:** `CORTEX-3.0-dev`

#### Development Workflow:

```bash
# For each feature/milestone, create feature branch
git checkout CORTEX-3.0-dev
git pull origin CORTEX-3.0-dev

# Create feature branch
git checkout -b feature/3.0-dual-channel-memory

# Develop, test, commit
git add .
git commit -m "feat: Implement dual-channel memory import"

# Push feature branch
git push origin feature/3.0-dual-channel-memory

# Create PR: feature/3.0-dual-channel-memory → CORTEX-3.0-dev
# After review and merge, delete feature branch

# Repeat for all features
```

**Feature Branches (28 weeks):**

```
Milestone 0 (2 weeks):
  - feature/3.0-test-fixes-yaml
  - feature/3.0-test-fixes-plugins
  - feature/3.0-test-fixes-ambient

Milestone 1 (4 weeks):
  - feature/3.0-simplified-operations
  - feature/3.0-template-integration

Milestone 2 (14 weeks):
  - feature/3.0-conversation-import
  - feature/3.0-fusion-layer
  - feature/3.0-narrative-generation

Milestone 3 (6 weeks, parallel):
  - feature/3.0-complexity-analyzer
  - feature/3.0-debt-detector
  - feature/3.0-impact-predictor

Milestone 4 (4 weeks):
  - feature/3.0-multi-agent-workflows
  - feature/3.0-agent-sub-specialization

Milestone 5 (4 weeks):
  - feature/3.0-documentation
  - feature/3.0-performance-optimization
```

**Throughout Development:**

Working directory is always `D:\PROJECTS\CORTEX` containing latest 3.0 code.

**To see CORTEX 2.0 during development:**

```bash
# Switch to 2.0 to reference old code
git checkout CORTEX-2.0-STABLE

# Working directory instantly becomes 2.0 codebase
# (all 3.0 files hidden, 2.0 files visible)

# Return to 3.0 development
git checkout CORTEX-3.0-dev

# Working directory back to 3.0 codebase
```

---

### Phase 3: CORTEX 3.0 Beta Release

**When:** After Milestone 5 (all features complete, tests passing)  
**Duration:** 1 day

#### Actions:

```bash
# 1. Ensure CORTEX-3.0-dev is stable
git checkout CORTEX-3.0-dev
pytest  # All tests passing (580+ tests)

# 2. Create beta tag
git tag -a v3.0.0-beta -m "CORTEX 3.0 Beta - Dual-Channel Memory, Intelligent Context"
git push origin v3.0.0-beta

# 3. Optional: Create beta release branch
git checkout -b CORTEX-3.0-beta
git push -u origin CORTEX-3.0-beta
```

**Result:**
- CORTEX 3.0 beta available for testing
- Still on development branch (can iterate based on feedback)

---

### Phase 4: CORTEX 3.0 Production Release (THE TRANSITION)

**When:** After beta testing, all issues resolved  
**Duration:** 30 minutes

#### Actions:

```bash
# 1. Final validation on CORTEX-3.0-dev
git checkout CORTEX-3.0-dev
pytest  # All 700+ tests passing
# Manual testing, user acceptance, etc.

# 2. Create production tag
git tag -a v3.0.0 -m "CORTEX 3.0 Production Release - Dual-Channel Memory, Intelligent Context, Enhanced Agents"
git push origin v3.0.0

# 3. THE TRANSITION: Make CORTEX 3.0 the default branch
# Option A: Update 'main' branch to point to 3.0
git checkout main
git merge --ff-only CORTEX-3.0-dev  # Fast-forward merge
git push origin main

# Option B: Rename CORTEX-3.0-dev to main
git branch -m CORTEX-3.0-dev main
git push origin main
git push origin --delete CORTEX-3.0-dev

# 4. Update default branch on GitHub
# GitHub → Settings → Branches → Default branch → Change to 'main'

# 5. Update README badges, documentation to reflect 3.0
# Commit and push
```

**Result:**
- `main` branch is now CORTEX 3.0
- Cloning repo gives CORTEX 3.0 by default
- CORTEX 2.0 still accessible via tags: `git checkout v2.0.0`
- Working directory is clean CORTEX 3.0 codebase (no subfolders)

---

### Phase 5: Post-Transition (Ongoing)

**When:** After v3.0.0 production release

#### Branch Cleanup:

```bash
# Delete old CORTEX-2.0 branch (preserved in tags)
git branch -d CORTEX-2.0  # Local
git push origin --delete CORTEX-2.0  # Remote

# Optional: Keep CORTEX-2.0-archive branch for extra safety
# (can delete after 6 months if confident in 3.0)

# Delete merged feature branches
git branch -d feature/3.0-dual-channel-memory
git push origin --delete feature/3.0-dual-channel-memory
# ... repeat for all merged features
```

#### Accessing CORTEX 2.0:

```bash
# Users who need 2.0 can still access it
git checkout v2.0.0  # By tag
# or
git checkout CORTEX-2.0-archive  # By archive branch

# Working directory becomes CORTEX 2.0
# No subfolders, clean git checkout
```

---

## 📊 Repository State at Each Phase

### Phase 0 (Current - CORTEX 2.0)

```yaml
branches:
  - CORTEX-2.0 (active, current)
tags:
  - v2.0.0
  - CORTEX-2.0-STABLE
  - CORTEX-2.0-FINAL
working_directory: "CORTEX 2.0 codebase"
```

### Phase 1-2 (Development - 28 Weeks)

```yaml
branches:
  - CORTEX-2.0 (frozen, reference only)
  - CORTEX-3.0-dev (active development)
  - feature/* (temporary feature branches)
tags:
  - v2.0.0, CORTEX-2.0-STABLE, CORTEX-2.0-FINAL (2.0 tags)
working_directory: "CORTEX 3.0 development codebase"
default_checkout: "CORTEX-3.0-dev"
```

### Phase 3 (Beta Testing)

```yaml
branches:
  - CORTEX-2.0 (frozen)
  - CORTEX-3.0-dev (active)
  - CORTEX-3.0-beta (beta release)
tags:
  - v2.0.0, CORTEX-2.0-STABLE, CORTEX-2.0-FINAL (2.0)
  - v3.0.0-beta (3.0 beta)
working_directory: "CORTEX 3.0 beta codebase"
default_checkout: "CORTEX-3.0-beta"
```

### Phase 4+ (Production - CORTEX 3.0)

```yaml
branches:
  - main (CORTEX 3.0 production)
  - CORTEX-2.0-archive (optional, 2.0 backup)
tags:
  - v2.0.0, CORTEX-2.0-STABLE, CORTEX-2.0-FINAL (2.0)
  - v3.0.0-beta, v3.0.0 (3.0)
working_directory: "CORTEX 3.0 production codebase"
default_checkout: "main"
retired_branches:
  - CORTEX-2.0 (deleted, preserved in tags)
  - CORTEX-3.0-dev (merged to main, deleted)
```

---

## 🛡️ Safety Mechanisms

### 1. CORTEX 2.0 Never Lost

```yaml
preservation_methods:
  tags:
    - "v2.0.0 (semantic version)"
    - "CORTEX-2.0-STABLE (baseline for 3.0)"
    - "CORTEX-2.0-FINAL (last 2.0 commit)"
  
  archive_branch:
    - "CORTEX-2.0-archive (optional extra backup)"
  
  git_reflog:
    - "Git reflog preserves all commits for 90+ days"
  
  github_history:
    - "GitHub preserves all commits forever"

access_cortex_2_0_anytime:
  by_tag: "git checkout v2.0.0"
  by_branch: "git checkout CORTEX-2.0-archive"
  by_commit: "git checkout <commit-hash>"
```

### 2. Rollback from CORTEX 3.0 to 2.0

```bash
# If CORTEX 3.0 has critical issues, rollback to 2.0

# Option A: Temporary rollback (working directory only)
git checkout v2.0.0
# Working directory is now CORTEX 2.0
# No commits made, just viewing 2.0

# Option B: Revert main branch to 2.0 (destructive, creates new commit)
git checkout main
git revert <3.0-commits>...  # Revert 3.0 changes
git push origin main

# Option C: Force main to 2.0 (DANGER - rewrites history)
git checkout main
git reset --hard v2.0.0
git push --force origin main
# WARNING: Only if absolutely necessary, loses 3.0 history

# Recommended: Option A for temporary, Option B for permanent
```

### 3. Parallel 2.0 Maintenance (If Needed)

```bash
# If users still need 2.0 bug fixes during 3.0 development

# Create maintenance branch
git checkout v2.0.0
git checkout -b CORTEX-2.0-maintenance

# Fix bugs in 2.0
git commit -m "fix: Critical bug in Tier 1 (2.0)"

# Tag maintenance release
git tag -a v2.0.1 -m "CORTEX 2.0.1 Maintenance Release"
git push origin v2.0.1

# CORTEX 3.0 development continues independently
```

---

## 📋 Migration Checklist

### Before Transition (Phase 0)

- [ ] All CORTEX 2.0 changes committed
- [ ] All tests passing (fix to 580/580 first)
- [ ] Create tags: `v2.0.0`, `CORTEX-2.0-STABLE`, `CORTEX-2.0-FINAL`
- [ ] Push tags to GitHub
- [ ] Create archive branch: `CORTEX-2.0-archive`
- [ ] Backup brain data: `cortex-brain/backups/pre-3.0-migration/`

### During Development (Phase 1-2)

- [ ] CORTEX-3.0-dev branch created
- [ ] Feature branches for each milestone
- [ ] Regular commits and pushes
- [ ] No commits to CORTEX-2.0 (frozen)
- [ ] Test regression checks after each feature

### Before Production Release (Phase 3-4)

- [ ] All 700+ tests passing
- [ ] Beta testing complete
- [ ] Documentation updated (README, guides)
- [ ] Performance benchmarks met
- [ ] User acceptance testing passed
- [ ] Create tag: `v3.0.0`
- [ ] Merge to `main` branch
- [ ] Update GitHub default branch to `main`

### After Transition (Phase 5)

- [ ] Verify `main` is CORTEX 3.0
- [ ] Delete old branches (CORTEX-2.0, CORTEX-3.0-dev)
- [ ] Delete merged feature branches
- [ ] Update CI/CD to build from `main`
- [ ] Monitor for issues
- [ ] Keep CORTEX-2.0-archive for 6 months (optional)

---

## 🎯 Key Benefits of This Approach

### 1. Clean Working Directory

```
D:\PROJECTS\CORTEX\  ← Always contains active version
├── No cortex-2.0/ subfolder
├── No cortex-3.0/ subfolder
└── Just clean CORTEX code
```

### 2. Instant Version Switching

```bash
# Work on CORTEX 3.0
git checkout CORTEX-3.0-dev

# Reference CORTEX 2.0 code
git checkout v2.0.0

# Back to 3.0
git checkout CORTEX-3.0-dev

# Each checkout takes <1 second
# No copying, no subfolders
```

### 3. Git History Preserves Everything

```bash
# See all CORTEX 2.0 commits
git log v2.0.0

# See all CORTEX 3.0 commits
git log CORTEX-3.0-dev

# Compare versions
git diff v2.0.0..CORTEX-3.0-dev

# Cherry-pick specific 2.0 fixes to 3.0
git cherry-pick <commit-hash>
```

### 4. Professional Version Management

```yaml
semantic_versioning:
  cortex_2_0: "v2.0.0, v2.0.1, v2.0.2..."
  cortex_3_0: "v3.0.0-beta, v3.0.0, v3.0.1..."

release_notes:
  - "GitHub Releases for each tag"
  - "Automatic changelog generation"
  - "Download specific versions"

ci_cd:
  - "Build and test on each branch"
  - "Deploy from tags"
  - "Version-specific artifacts"
```

---

## 📝 Example Commands Quick Reference

### Transition Commands

```bash
# PHASE 0: Prepare CORTEX 2.0
git tag -a v2.0.0 -m "CORTEX 2.0 Production"
git push origin v2.0.0

# PHASE 1: Start CORTEX 3.0
git checkout -b CORTEX-3.0-dev
git push -u origin CORTEX-3.0-dev

# PHASE 2: Develop features
git checkout -b feature/3.0-dual-channel
# ... develop ...
git push origin feature/3.0-dual-channel
# ... PR and merge ...

# PHASE 4: Release CORTEX 3.0
git tag -a v3.0.0 -m "CORTEX 3.0 Production"
git checkout main
git merge --ff-only CORTEX-3.0-dev
git push origin main

# PHASE 5: Cleanup
git branch -d CORTEX-2.0
git push origin --delete CORTEX-2.0
```

### Daily Development

```bash
# Work on CORTEX 3.0
git checkout CORTEX-3.0-dev
git pull origin CORTEX-3.0-dev

# Check CORTEX 2.0 for reference
git checkout v2.0.0

# Back to work
git checkout CORTEX-3.0-dev
```

### Version Access

```bash
# Clone repo (gets default branch - CORTEX 3.0 after transition)
git clone <repo-url>

# Access CORTEX 2.0
git checkout v2.0.0

# List all versions
git tag

# List all branches
git branch -a
```

---

## ✅ Decision Points

**When does transition happen?**

```yaml
trigger: "CORTEX 3.0 v3.0.0 production release (after Milestone 5)"
timeline: "~28 weeks from now (if starting development today)"

commit_to_3_0_as_main:
  - "After all 700+ tests passing"
  - "After beta testing successful"
  - "After user acceptance"
  - "After performance validation"

backwards_compatibility:
  - "CORTEX 2.0 always accessible via tags"
  - "Can rollback to 2.0 if critical issues"
  - "No data loss (backups + git history)"
```

**What if we need to maintain CORTEX 2.0 during 3.0 development?**

```yaml
solution: "Create CORTEX-2.0-maintenance branch"
use_case: "Critical bugs in 2.0 while 3.0 in beta"
approach:
  - "Branch from v2.0.0"
  - "Fix bugs, tag as v2.0.1, v2.0.2, etc."
  - "CORTEX 3.0 development continues independently"
  - "No interference between versions"
```

---

## 🎉 Summary

**Repository Strategy:**
- ✅ One repository: `CORTEX`
- ✅ Versions via git branches and tags (NOT subfolders)
- ✅ Working directory always clean: `D:\PROJECTS\CORTEX\`
- ✅ CORTEX 2.0 preserved in tags (accessible forever)
- ✅ CORTEX 3.0 becomes main codebase after production release
- ✅ Switch versions with `git checkout` (instant)

**Timeline:**
- **Now → Week 2:** Phase 0 (Prepare 2.0, create tags)
- **Week 2 → Week 30:** Phase 1-2 (Develop 3.0 in CORTEX-3.0-dev)
- **Week 30 → Week 32:** Phase 3 (Beta testing)
- **Week 32:** Phase 4 (Production release, THE TRANSITION)
- **Week 32+:** Phase 5 (CORTEX 3.0 is main, 2.0 in history)

**User Experience:**
```bash
# Clone CORTEX repo (after transition)
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Gets CORTEX 3.0 by default
ls  # All CORTEX 3.0 files

# Want CORTEX 2.0?
git checkout v2.0.0
ls  # All CORTEX 2.0 files (no subfolders, clean checkout)
```

---

**Planning Date:** November 13, 2025  
**Status:** Repository Transition Strategy  
**Priority:** CRITICAL (must execute before 3.0 development)

---

*"One codebase, multiple versions, zero confusion. Git manages versions, not folders."*
