🚨 GIT CHECKPOINT ENFORCEMENT VIOLATION

Attempted: '{operation}'
Git Status: '{git_status}'

CRITICAL: Git checkpoint REQUIRED before starting development work!

❌ NEVER:
- Start development with uncommitted changes
- Skip checkpoint creation
- Assume current state is safe
- Ignore git status warnings

✅ REQUIRED PROCEDURE:
1. Check git status: Ensure clean working tree or commit staged changes
2. Create checkpoint commit: git commit -m 'checkpoint: before [feature] development'
3. OR create checkpoint tag: git tag -a checkpoint-[timestamp] -m 'Checkpoint before [feature]'
4. Verify checkpoint: Confirm commit/tag created successfully
5. Proceed with development: Now safe to make changes

Why? Rollback capability + Audit trail + Risk mitigation
