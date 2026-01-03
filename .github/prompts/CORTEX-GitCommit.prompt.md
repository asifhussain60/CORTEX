# ⚡ CORTEX Git Commit v3.0# 🔄 CORTEX Git Commit & Sync Automation



**Purpose:** Lightning-fast git operations  **Version:** 2.0.0 | **Status:** ✅ PRODUCTION  

**Author:** Asif Hussain | **Copyright © 2025-2026****Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**



------



## 🎯 Commands## 🎯 Purpose



| User Says | Execute | Target |Intelligent git workflow automation with **multi-machine sync verification**, rename/move detection, and force-sync recovery.

|-----------|---------|--------|

| `commit`, `save` | Stage all + commit | 3s |---

| `commit and push`, `push` | Stage + commit + push | 8s |

| `status`, `changes` | Show status | 1s |## ⚠️ CRITICAL RULES



---| Rule | Command Pattern |

|------|-----------------|

## 🚀 Execution Protocol| **Editor Suspension Prevention** | Always use `GIT_EDITOR=true` prefix |

| **Multi-Machine Sync** | Use `git reset --hard origin/BRANCH` after pull |

### 1. Parse Intent (instant)| **Rename Detection** | Git tracks renames as delete+add (requires `git add -A`) |

- Extract: operation + optional message| **Clean State Verification** | Always verify with `git status` after sync |

- No confirmation needed for safe operations

---

### 2. Execute (3-8s)

## 📋 Git Commit & Sync Workflow (7 Phases)

**Commit Only:**

```bash### **Phase 1: Pre-Flight Checks**

git add -A && git commit -m "<message>"

``````bash

git status

**Commit + Push:**git branch --show-current

```bashgit fetch origin

git add -A && git commit -m "<message>" && git pushgit log --oneline -3

``````



**Status:**### **Phase 2: Stage Changes**

```bash

git status --short```bash

```git add -A

git status --short

### 3. Report (instant)```

```

✅ Committed & pushed (8 files)**Status codes:** `M` = Modified | `A` = Added | `D` = Deleted | `R` = Renamed

```

### **Phase 3: Commit Locally**

---

```bash

## 🛡️ Safety Rulesgit commit -m "type(scope): Brief description



1. **Status check first** - Quick `git status --short` before operations- Detailed change 1

2. **Never force push** - Unless user explicitly says "force push"- Detailed change 2"

3. **Handle divergence** - If push fails, offer rebase (don't auto-execute)```

4. **No editor suspension** - Use `GIT_EDITOR=true` for non-interactive commits

**Commit types:** `feat` | `fix` | `docs` | `refactor` | `test` | `chore`

---

### **Phase 4: Pull & Merge (Non-Interactive)**

## 📝 Message Strategy

```bash

**Auto-generate when user doesn't specify:**GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase

``````

"chore: update <N> files"

```**If merge needed:**

```bash

**User-specified:**GIT_EDITOR=true git merge --continue

Use verbatim from user request```



---### **Phase 5: Conflict Resolution**



## ⚠️ Error Handling```bash

git status | grep "both modified"    # Identify conflicts

| Error | Response |git add <resolved-file>              # Stage after resolving

|-------|----------|GIT_EDITOR=true git merge --continue # Complete merge

| Push rejected (diverged) | "Branch diverged. Say 'pull and push' or 'force push'" |```

| Merge conflict | Show conflicted files, stop |

| No changes | "No changes to commit" |### **Phase 6: Push to Origin**



---```bash

git push origin CORTEX-4.0

## 🚫 Anti-Bloat Rules```



❌ No multi-phase explanations during execution  ### **Phase 7: Multi-Machine Verification** ⭐ NEW

❌ No verbose output unless error  

❌ No confirmation prompts for safe ops  **On other machines after push:**

❌ No redundant status checks  

❌ No explanatory tables during execution```bash

git fetch origin

---git reset --hard origin/CORTEX-4.0

git clean -fd

## 📊 Output Format```



**Success:****Why this matters:**

```- `git pull` may not update working tree for renames/moves

✅ Committed (5 files)- `git reset --hard` forces working tree to match remote exactly

✅ Pushed to origin/branch-name- `git clean -fd` removes untracked files blocking renamed paths

```

---

**Error:**

```## 🔄 Force-Sync Commands (Multi-Machine)

⚠️ Push rejected: branch diverged

Say: 'pull and push' or 'rebase and push'```bash

```# Hard reset to remote (RECOMMENDED)

git fetch origin

---git reset --hard origin/CORTEX-4.0

git clean -fd

## 🔧 Quick Reference

# Preserve local changes first

**Standard workflow:**git stash && git reset --hard origin/CORTEX-4.0 && git stash pop

```bash```

git add -A && git commit -m "msg" && git push

```---



**Handle divergence:**## 🛡️ Common Issues & Solutions

```bash

GIT_EDITOR=true git pull --rebase && git push| Issue | Symptom | Solution |

```|-------|---------|----------|

| **Renamed files not appearing** | Old folders still exist | `git reset --hard origin/BRANCH && git clean -fd` |

**Force push (with safety):**| **Editor suspension** | `zsh: suspended` | Use `GIT_EDITOR=true` prefix |

```bash| **Divergent branches** | `have diverged` | `GIT_EDITOR=true git pull --no-rebase` |

git push --force-with-lease| **Untracked blocking** | `would be overwritten` | `git clean -fd` then pull |

```| **Pre-commit hook** | `Found marker(s)` | Auto-handled, no action needed |



**Multi-machine sync:**---

```bash

git fetch origin && git reset --hard origin/BRANCH && git clean -fd## 🎯 GitKraken MCP Tool Commands

```

```python

---mcp_gitkraken_git_add_or_commit(action="add", directory="/path/to/repo")

mcp_gitkraken_git_add_or_commit(action="commit", directory="/path/to/repo", message="feat: message")

## 🎯 GitKraken MCP Integrationmcp_gitkraken_git_push(directory="/path/to/repo")

mcp_gitkraken_git_status(directory="/path/to/repo")

```python# Pull: use run_in_terminal with GIT_EDITOR=true

# Stage + Commit```

mcp_gitkraken_git_add_or_commit(action="commit", directory=".", message="msg")

---

# Push

mcp_gitkraken_git_push(directory=".")## 📚 Quick Reference



# Status| Action | Command |

mcp_gitkraken_git_status(directory=".")|--------|---------|

```| Stage all | `git add -A` |

| Commit | `git commit -m "message"` |

---| Pull (non-interactive) | `GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase` |

| Push | `git push origin CORTEX-4.0` |

**Performance Target:** < 10 seconds total for commit+push| **Force-sync (multi-machine)** | `git fetch origin && git reset --hard origin/CORTEX-4.0` |

| Clean untracked | `git clean -fd` |

**End of Prompt**| Status | `git status` |


---

## 🚨 Emergency Recovery

```bash
git merge --abort                              # Abort merge
git fetch origin && git reset --hard origin/CORTEX-4.0  # Reset to remote
fg && Ctrl+C                                   # Recover suspended process
```

---

## ✅ Success Criteria

After successful sync on ALL machines:

1. ✅ `git status` → "nothing to commit, working tree clean"
2. ✅ `git status` → "Your branch is up to date with 'origin/...'"
3. ✅ Working tree matches remote exactly (renamed files in correct locations)
4. ✅ `git log --oneline -3` shows same commits on all machines

---

**Anti-Bloat:** This file is ~150 lines. Max 200 lines.
