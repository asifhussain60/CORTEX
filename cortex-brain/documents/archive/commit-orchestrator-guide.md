# Commit Orchestrator Guide

**Purpose:** Intelligent git commit and sync workflow with untracked file handling and merge conflict resolution  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The Commit Orchestrator provides a safe, intelligent workflow for syncing local repository changes with remote origin:
- Pull from origin and merge (preserving local work)
- Ensure zero untracked files (prompt user to add/ignore)
- Push merged result to origin
- Create git checkpoints for rollback safety
- Handle merge conflicts with clear guidance

---

## 🚀 Commands

**Natural Language Triggers:**
- `commit`
- `commit and push`
- `sync with origin`
- `commit sync`
- `push changes`
- `sync repository`
- `commit and sync`
- `pull and push`
- `sync repo`

**Use Cases:**
- Syncing local changes with team
- Preparing for deployment
- Collaborating on feature branches
- Resolving merge conflicts safely

---

## 📊 Workflow Steps

### Phase 1: Pre-Flight Validation (5s)
```
Check current repository state:
- Is working tree clean? (no uncommitted changes)
- Are there untracked files? (prompt user to add/ignore)
- Is branch up-to-date with remote?
- Are there merge conflicts? (must resolve first)
```

### Phase 2: Untracked File Handling (10-30s)
```
If untracked files found:
1. List all untracked files
2. Prompt user: Add, Ignore, or Cancel
3. If Add: Stage files with git add
4. If Ignore: Add to .gitignore
5. If Cancel: Abort sync operation
```

### Phase 3: Commit Local Changes (5s)
```
If working tree dirty:
1. Stage all changes (git add .)
2. Create commit with auto-generated or custom message
3. Verify commit success
```

### Phase 4: Create Safety Checkpoint (2s)
```
Create git checkpoint before pull:
- Tag: pre-sync-YYYYMMDD-HHMMSS
- Purpose: Rollback point if merge fails
- Retention: 30 days
```

### Phase 5: Pull from Origin (10-30s)
```
Fetch and merge remote changes:
1. git fetch origin
2. git merge origin/<branch> --no-ff
3. Detect merge conflicts (if any)
4. If conflicts: Provide resolution guidance
5. If success: Continue to push
```

### Phase 6: Push to Origin (10-30s)
```
Upload merged changes:
1. git push origin <branch>
2. Verify push success
3. Create post-sync checkpoint
4. Report sync status
```

---

## 🔧 Configuration

**Config File:** `cortex.config.json`

```json
{
  "commit_orchestrator": {
    "auto_stage_untracked": false,
    "commit_message_template": "feat: {description}",
    "merge_strategy": "merge",
    "checkpoint_before_sync": true,
    "verify_push": true,
    "conflict_resolution_mode": "interactive"
  }
}
```

**Options:**
- `auto_stage_untracked` - Auto-add untracked files without prompting (default: `false`)
- `commit_message_template` - Commit message format (default: `"feat: {description}"`)
- `merge_strategy` - Merge method: `merge`, `rebase` (default: `merge`)
- `checkpoint_before_sync` - Create safety checkpoint (default: `true`)
- `verify_push` - Verify push completed (default: `true`)
- `conflict_resolution_mode` - How to handle conflicts: `interactive`, `abort` (default: `interactive`)

---

## 📈 Examples

### Example 1: Clean Sync (No Conflicts)
```
User: "commit and push"

CORTEX:
  🔍 Checking repository state...
  ✅ Working tree clean
  ✅ No untracked files
  
  📸 Creating safety checkpoint: pre-sync-20251127-143000
  
  ⬇️  Pulling from origin/main...
  ✅ Merged 3 commits (no conflicts)
  
  ⬆️  Pushing to origin/main...
  ✅ Push successful
  
  📸 Creating post-sync checkpoint: post-sync-20251127-143045
  
  ✅ Sync complete!
  
  Summary:
  • 3 commits pulled from origin
  • 0 conflicts
  • 0 untracked files
  • 2 checkpoints created
```

### Example 2: Untracked Files Found
```
User: "sync repository"

CORTEX:
  🔍 Checking repository state...
  ⚠️  UNTRACKED FILES DETECTED (3 files)
  
  Untracked files:
  • src/new_feature.py
  • tests/test_new_feature.py
  • docs/new_feature_guide.md
  
  OPTIONS:
    A) Add all to git (recommended)
    I) Ignore in .gitignore
    C) Cancel sync
  
  Your choice (A/I/C): A
  
  ✅ Staged 3 files
  📝 Creating commit: "feat: Add new feature files"
  
  📸 Creating safety checkpoint: pre-sync-20251127-143500
  
  ⬇️  Pulling from origin/main...
  ✅ Merged 2 commits (no conflicts)
  
  ⬆️  Pushing to origin/main...
  ✅ Push successful (4 commits total)
  
  ✅ Sync complete with 3 new files added!
```

### Example 3: Merge Conflict Detected
```
User: "commit sync"

CORTEX:
  🔍 Checking repository state...
  ✅ Working tree clean
  
  📸 Creating safety checkpoint: pre-sync-20251127-144000
  
  ⬇️  Pulling from origin/main...
  ❌ MERGE CONFLICT DETECTED
  
  Conflicting files:
  • src/auth.py (lines 45-60)
  • config/settings.py (lines 12-18)
  
  CONFLICT RESOLUTION STEPS:
  1. Open conflicting files
  2. Resolve conflict markers (<<<<<<, ======, >>>>>>)
  3. Stage resolved files: git add <file>
  4. Complete merge: git commit
  5. Re-run sync: "commit sync"
  
  ROLLBACK OPTION:
  To undo sync attempt: "rollback to pre-sync-20251127-144000"
  
  Sync paused - resolve conflicts to continue.
```

---

## 🐛 Troubleshooting

### Issue: "Push rejected - non-fast-forward"

**Cause:** Remote has commits not in local branch

**Solution:**
```pwsh
# Pull first, then try again
git pull origin main
# Re-run sync
"commit sync"
```

### Issue: "Untracked files blocking sync"

**Cause:** Untracked files present, user must decide to add or ignore

**Solution:**
- Choose option A (Add) to include files in commit
- Choose option I (Ignore) to add to .gitignore
- Choose option C (Cancel) to abort sync

### Issue: "Merge conflict unresolved"

**Cause:** Conflicting changes in same file lines

**Solution:**
1. Open conflicting files
2. Search for conflict markers: `<<<<<<<`
3. Resolve conflicts (keep yours, theirs, or merge both)
4. Remove conflict markers
5. Stage files: `git add <file>`
6. Complete merge: `git commit`
7. Re-run sync

---

## 🔒 Safety Features

### Git Checkpoint Integration
- **Before sync:** Create `pre-sync-YYYYMMDD-HHMMSS` checkpoint
- **After sync:** Create `post-sync-YYYYMMDD-HHMMSS` checkpoint
- **Rollback:** Use `rollback to <checkpoint>` if sync causes issues

### Untracked File Protection
- Never auto-add without user consent
- Clear options: Add, Ignore, Cancel
- Zero surprise commits

### Merge Conflict Guidance
- Clear conflict markers shown
- Step-by-step resolution steps
- Rollback option always available

---

## 📚 Related Documentation

- **Git Checkpoint Guide:** `.github/prompts/modules/git-checkpoint-orchestrator-guide.md`
- **TDD Workflow:** `.github/prompts/modules/tdd-workflow-orchestrator-guide.md`
- **System Alignment:** `.github/prompts/modules/system-alignment-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
