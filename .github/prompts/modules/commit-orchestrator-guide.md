# Commit Orchestrator Guide

**Module:** `CommitOrchestrator`  
**Location:** `src/operations/modules/git/commit_orchestrator.py`  
**Purpose:** Intelligent Git commit operations with automatic staging and validation  
**Status:** ✅ Production  
**Version:** 3.3.0

---

## Overview

The Commit Orchestrator provides intelligent Git commit operations with automatic file staging, commit message generation, and validation. It ensures clean commit history and proper Git workflow practices.

**Key Capabilities:**
- Automatic file staging based on context
- Commit message generation following conventions
- Pre-commit validation and checks
- Integration with Brain Protector for compliance
- Support for conventional commits format
- Dry-run mode for safety

---

## Natural Language Triggers

**Primary Commands:**
- `commit`
- `commit [message]`
- `commit changes`
- `git commit`

**Context Variations:**
- "Commit my changes"
- "Commit with message [text]"
- "Save changes to Git"

---

## Architecture & Integration

**Dependencies:**
- Git CLI (command-line interface)
- `BrainProtector` - Validates commits don't violate rules
- `GitCheckpointOrchestrator` - Creates rollback points
- `.gitignore` - Respects exclusion rules

**Integration Points:**
- Unified Entry Point Orchestrator for command routing
- Response template system for user feedback
- Git checkpoint system for safety

---

## Usage Examples

### Basic Commit

```
User: "commit"
CORTEX: Stages all changes → Generates message → Creates commit
```

### Commit with Message

```
User: "commit Add user authentication feature"
CORTEX: Stages changes → Uses provided message → Commits
```

### Dry Run

```
User: "commit --dry-run"
CORTEX: Shows what would be committed without making actual commit
```

---

## Commit Message Conventions

**Format:** `<type>: <description>`

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

**Examples:**
- `feat: Add user authentication system`
- `fix: Resolve login validation bug`
- `docs: Update API documentation`

---

## Safety Features

**Pre-Commit Checks:**
1. ✅ No Brain Protector rule violations
2. ✅ No staged files in `.gitignore`
3. ✅ No merge conflicts present
4. ✅ Valid commit message format
5. ✅ No empty commits

**Rollback Protection:**
- Automatically creates Git checkpoint before commit
- Allows easy rollback if issues discovered
- Preserves uncommitted changes

---

## Configuration

**Git Configuration (Respects):**
- `.gitignore` - File exclusion rules
- `.git/config` - Repository settings
- User name and email from Git config

**CORTEX Settings:**
- Auto-staging: Enabled by default
- Commit message generation: Enabled
- Pre-commit validation: Enabled
- Checkpoint creation: Enabled

---

## Implementation Details

**Class:** `CommitOrchestrator`

**Key Methods:**
- `execute(context)` - Main commit orchestration
- `_stage_files(files)` - Stage specified files
- `_generate_commit_message(changes)` - Auto-generate message
- `_validate_commit()` - Pre-commit validation
- `_create_checkpoint()` - Safety checkpoint
- `_perform_commit(message)` - Execute Git commit

---

## Error Handling

**Common Issues:**
1. **No changes to commit** → Informs user, exits gracefully
2. **Brain Protector violation** → Blocks commit, explains rule
3. **Git not configured** → Guides user to configure name/email
4. **Merge conflict** → Instructs resolution before commit

---

## Testing

**Test Coverage:** 60% (needs improvement)

**Test Files:**
- `tests/operations/test_commit_orchestrator.py` (planned)

**Manual Validation:**
1. Make file changes
2. Run `commit`
3. Verify files staged correctly
4. Check commit message quality
5. Validate checkpoint created

---

## Related Modules

- **GitCheckpointOrchestrator** - Creates rollback points
- **RollbackOrchestrator** - Undoes commits if needed
- **BrainProtector** - Validates compliance before commit

---

## Troubleshooting

**Issue:** Commit blocked by Brain Protector  
**Solution:** Review violation message, fix issue, retry commit

**Issue:** Wrong files staged  
**Solution:** Use `git reset` to unstage, specify files explicitly

**Issue:** Commit message rejected  
**Solution:** Follow conventional commits format, provide clear description

---

## Future Enhancements

**Planned (CORTEX 4.0):**
- AI-powered commit message generation from diffs
- Automatic issue linking (GitHub/ADO integration)
- Co-author attribution for pair programming
- Semantic versioning bump detection
- Commit template customization

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Last Updated:** November 28, 2025  
**Guide Version:** 1.0.0
