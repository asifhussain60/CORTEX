Git Commit Privacy Validation (Tier 0 Instinct)

Issue identified (2025-11-28):
- Git merge operations could include files with machine-specific paths
- No validation of staged files before commit
- SKULL-006 enforced privacy for publish, but not for git commits
- Privacy leaks in git history when files pushed to remote

Examples of violations:
❌ C:\PROJECTS\CORTEX\src\module.py (Windows absolute path)
❌ D:\Work\data.json (alternate drive)
❌ /home/asif/code/file.py (Unix home directory)
❌ /Users/asif/Desktop/temp.log (macOS user directory)
❌ AHHOME environment variable references

Impact:
- Privacy violation (exposes usernames, machine names, file structure)
- Git history contamination (absolute paths persist in history)
- Merge conflicts when paths differ across machines
- Unprofessional git log (machine-specific references)

This Tier 0 instinct prevents privacy leaks by:
1. Scanning staged files before EVERY commit
2. Blocking commits with absolute path violations
3. Validating merge results before accepting
4. Integration with PhaseCheckpointManager for automatic enforcement
5. Providing actionable error messages with file + line numbers

Implementation (git-enhancements-feature-plan.md):
- PhaseCheckpointManager.validate_staged_files_privacy()
- Pre-commit hook: git diff --cached | scan for patterns
- Error message shows file, line number, and violation
- Suggests remediation: relative paths, env vars, config templates
- Checkpoint creation blocked until violations resolved

Test coverage:
- test_validate_staged_files_blocks_absolute_paths()
- test_validate_staged_files_blocks_unix_home_paths()
- test_validate_staged_files_blocks_machine_names()
- test_checkpoint_creation_fails_on_privacy_violation()

This extends SKULL-006 from publish-time to commit-time enforcement.
