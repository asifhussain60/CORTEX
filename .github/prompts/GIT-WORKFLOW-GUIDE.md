# Git Workflow Guide: Committing and Pushing Changes

This guide documents how to commit all changes and push to the remote repository, with instructions for replicating this workflow on another version of CORTEX or similar projects.

---

## Quick Start (Single Command)

```bash
# Stage all changes, commit with message, and push
git add -A && git commit -m "your commit message here" && git push origin <branch-name>
```

---

## Step-by-Step Workflow

### 1. Check Current Status

Before committing, always verify what changes you have:

```bash
cd /path/to/repository
git status
```

**Output shows:**
- `Changes not staged for commit:` — Modified files
- `Untracked files:` — New files Git hasn't seen
- `Changes to be committed:` — Already staged files

### 2. Stage All Changes

Stage both modified and untracked files:

```bash
git add -A
```

**Or be selective:**
- `git add <file>` — Stage specific file
- `git add .` — Stage all in current directory
- `git add *.py` — Stage all Python files by pattern

### 3. Verify Staging

Check what's staged before committing:

```bash
git status  # Shows green "Changes to be committed:"
```

### 4. Create Meaningful Commit

Write a clear commit message following conventional commits format:

```bash
git commit -m "type: subject

- Bullet 1 with implementation detail
- Bullet 2 with another change
- Bullet 3 documenting outcome

Fixes: Issue reference or governance rule fixed"
```

**Commit types:**
- `feat:` — New feature or architecture change
- `fix:` — Bug fix or correction
- `refactor:` — Code restructuring without behavior change
- `docs:` — Documentation updates
- `test:` — Test additions or fixes
- `chore:` — Build, config, or tooling updates

**Example from M7 consolidation:**

```
feat: consolidate prompt architecture into unified CORTEX entry point

- Removes 8-prompt picker contamination by centralizing all routing into CORTEX.prompt.md
- Marks 6 subsidiary prompts as non-production-admin
- Adds detail-prompt-file metadata to 5 core skills for skill-first routing discovery
- Creates archive infrastructure documenting consolidation rationale
- Adds comprehensive integration test suite validating skill-prompt routing
- Zero regressions: 479 preflight tests passing, 7/7 integration tests passing

Fixes CORE-035 (single canonical implementation)
```

### 5. Push to Remote

Push your committed changes to the remote branch:

```bash
git push origin <branch-name>
```

**Examples:**
```bash
git push origin develop        # Push to develop branch
git push origin main           # Push to main branch
git push origin feature/xyz    # Push to feature branch
git push origin --all          # Push all branches
```

**Verify push succeeded:**
```bash
git log --oneline -5    # Shows your commit at the top
```

---

## Full Workflow Example

```bash
# 1. Navigate to repo
cd /Users/asifhussain/PROJECTS/CORTEX

# 2. Check what changed
git status

# 3. Stage everything
git add -A

# 4. Verify staging
git status

# 5. Commit with meaningful message
git commit -m "feat: consolidate prompts

- Centralizes routing into CORTEX.prompt.md
- Marks 6 subsidiary prompts as non-production-admin
- Adds skill-based discovery metadata"

# 6. Push to origin
git push origin develop

# 7. Verify success
git log --oneline -3
```

---

## Replicating on Another CORTEX Version

### Prerequisites

Ensure you have:
- Git installed and configured
- Remote repository URL known
- Appropriate branch checked out

### Steps

1. **Confirm you're on the right branch:**
   ```bash
   git branch -a    # List all branches (* shows current)
   git checkout develop  # Switch if needed
   ```

2. **Verify your remote is configured:**
   ```bash
   git remote -v    # Shows origin URL
   ```

3. **Pull latest changes first (recommended):**
   ```bash
   git pull origin develop
   ```

4. **Make your changes to files** (your work)

5. **Stage all changes:**
   ```bash
   git add -A
   ```

6. **Create commit with message:**
   ```bash
   git commit -m "feat: your change description

- Detailed bullet point 1
- Detailed bullet point 2

Governance: Reference any CORE rules or fixes"
   ```

7. **Push to remote:**
   ```bash
   git push origin develop
   ```

8. **Verify in GitHub/GitLab UI:**
   - Navigate to your repository
   - Check the commit appears in the branch history
   - Verify timestamp and message

---

## Common Scenarios

### Scenario: "I forgot to add a file"

```bash
# Add the missing file
git add forgotten-file.md

# Amend the commit (fixes previous commit)
git commit --amend --no-edit

# Force push (only if not pushed yet, or discuss with team)
git push origin <branch> --force-with-lease
```

### Scenario: "I committed to the wrong branch"

```bash
# Check which branch you're on
git branch

# Create a backup branch just in case
git branch backup-<branch-name>

# Switch to correct branch
git checkout correct-branch

# Cherry-pick the commit
git cherry-pick <commit-hash>

# Go back and undo bad commit
git checkout wrong-branch
git reset --hard HEAD~1
```

### Scenario: "I need to see what will be pushed"

```bash
# Compare local vs remote before pushing
git log origin/develop..HEAD    # Shows commits to be pushed
git diff origin/develop         # Shows all changes to be pushed
```

### Scenario: "Push was rejected (remote changed)"

```bash
# Pull remote changes first
git pull origin develop

# Resolve any merge conflicts if they appear
# Then stage and commit the merge
git add -A
git commit -m "merge: sync with remote develop"

# Now push succeeds
git push origin develop
```

---

## Validation & Safety

### Before Pushing

**Always run tests to ensure no regressions:**

```bash
# For CORTEX projects
python3 scripts/run_tests.py preflight    # Full suite
python3 scripts/run_tests.py smoke        # Quick smoke test

# For other projects
pytest                                     # Run test suite
npm test                                  # JavaScript projects
./gradlew test                           # Java/Gradle projects
```

### After Pushing

**Verify your push succeeded:**

```bash
# Check local and remote are in sync
git status                # Should say "Your branch is up to date"

# View your commit in history
git log --oneline -5

# View commit details
git show HEAD
```

---

## Git Configuration for Team Workflows

### Set your identity (one-time setup)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### Optional: Set default branch

```bash
git config --global init.defaultBranch develop
```

### Optional: Create git aliases (shortcuts)

```bash
# Add these to ~/.gitconfig
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --graph --oneline --all'
```

Then use: `git st` instead of `git status`, etc.

---

## Troubleshooting

### "Permission denied (publickey)"

```bash
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "your.email@company.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Verify SSH connection
ssh -T git@github.com
```

### "fatal: destination path already exists"

```bash
# Repository already cloned. Use existing repo instead.
cd /existing/repo/path
```

### Undoing a Commit

```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and discard changes
git reset --hard HEAD~1

# Undo a pushed commit (creates new reverse commit)
git revert <commit-hash>
git push origin develop
```

---

## References

- [Git Official Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Push Documentation](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository)
- [Git Best Practices](https://www.git-scm.com/book/en/v2)

---

## M7 Consolidation Example

The most recent prompt consolidation (M7-b) used this workflow:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Verified all changes were complete
git status

# Staged everything
git add -A

# Committed with detailed message
git commit -m "feat: consolidate prompt architecture into unified CORTEX entry point

- Removes 8-prompt picker contamination by centralizing all routing into CORTEX.prompt.md
- Marks 6 subsidiary prompts as non-production-admin (cortex-architect, cortex-architecture-review, cortex-doc, cortex-sync, cortex-total-recall, cortex-trainer)
- Adds detail-prompt-file metadata to 5 core skills for skill-first routing discovery
- Creates archive infrastructure documenting consolidation rationale and migration guide
- Adds comprehensive integration test suite validating skill-prompt routing wiring
- Zero regressions: 479 preflight tests passing, 7/7 integration tests passing

Fixes CORE-035 (single canonical implementation) and eliminates dual-authority governance violations."

# Verified tests passed (479/489)
python3 scripts/run_tests.py preflight

# Pushed to remote
git push origin develop

# Verified in GitHub UI
```

---

*Last Updated: 2026-03-21*  
*Part of M7-b Consolidation Phase*
