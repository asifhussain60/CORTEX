PREVENT_DIRTY_STATE_WORK: Safety First Development

Working on branches with uncommitted changes is RISKY because:
- User changes can be accidentally overwritten
- Mixed authorship makes rollback ambiguous
- Unclear which changes are from CORTEX vs user
- Merge conflicts become harder to resolve

Why This Protection Matters:

1. Prevent Data Loss:
   User has uncommitted work in progress
   CORTEX operations might overwrite files
   No checkpoint of user's partial work
   Accidental loss of hours of work

2. Clear Attribution:
   User changes: Committed with user's name
   CORTEX changes: Committed with CORTEX checkpoint
   Clear separation of responsibility
   Easy to rollback specific changes

3. Merge Safety:
   Clean starting state = predictable merges
   Dirty state = unexpected interactions
   Checkpoint before CORTEX work = rollback capability
   Structured workflow reduces surprises

4. Debugging Clarity:
   "Did CORTEX break this or did I?"
   Clean checkpoints answer this instantly
   Mixed changes make debugging nightmare
   Structured commits = clear blame

Dirty State Detection:

A) Modified Files (Not Staged):
```bash
git status --porcelain | grep '^ M'
```
- Files changed but not staged
- User work in progress
- Require commit or stash

B) Staged Changes (Not Committed):
```bash
git status --porcelain | grep '^M'
```
- Changes staged for commit
- Almost ready but not finalized
- Should commit before CORTEX work

C) Untracked Files (In Scope):
```bash
git status --porcelain | grep '^??'
```
- New files not tracked by git
- May be intentional (experiments)
- Warn if in scope of CORTEX work

D) Merge/Rebase In Progress:
```bash
[ -f .git/MERGE_HEAD ] || [ -d .git/rebase-merge ]
```
- Git operation in progress
- Repository in unstable state
- BLOCK until resolved

User Consent Workflow:

1. Detect dirty state before work
2. Present clear options (A/B/C)
3. Wait for explicit user choice
4. Execute user's chosen action
5. Verify clean state
6. Proceed with CORTEX work
7. Create post-work checkpoint

Integration with Git Checkpoint:

If user chooses "Proceed anyway" (Option C):
1. CORTEX creates pre-work checkpoint
2. Checkpoint includes user's uncommitted changes
3. CORTEX performs requested work
4. Post-work checkpoint captures CORTEX changes
5. User can compare: pre-work vs post-work
6. Rollback options available for both

When to BLOCK vs WARN:

BLOCK (Severity: blocked):
- Merge conflict in progress
- Rebase in progress
- Cherry-pick in progress
- Repository corruption detected

WARN (Severity: warning):
- Uncommitted changes (user can consent)
- Untracked files in scope (user can ignore)
- Staged but not committed (user can commit)

Real Incident Patterns Prevented:

Scenario 1: Lost User Work
User: Has 2 hours of uncommitted changes
CORTEX: Overwrites files during implementation
Result: User work lost, hours wasted
Prevention: Dirty state warning → user commits first

Scenario 2: Attribution Confusion
User: Made changes, didn't commit
CORTEX: Made changes, created checkpoint
Result: "Who changed this file?"
Prevention: Separate commits = clear attribution

Scenario 3: Rollback Ambiguity
User: Want to undo CORTEX changes only
Reality: User + CORTEX changes mixed
Result: Can't cleanly separate
Prevention: Clean pre-work state = precise rollback

This rule WARNS and requires user consent before proceeding.
Exception: Clean working tree = no warning needed.
