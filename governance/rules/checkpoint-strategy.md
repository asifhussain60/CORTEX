# Rule 19: Checkpoint Strategy (Tier 0 - PERMANENT)

**Priority:** CRITICAL  
**Tier:** 0 (Instinct)  
**Applies To:** All development work  
**Override:** NOT ALLOWED

---

## Rule Statement

**BEFORE ANY development work (phase/task/feature), create a checkpoint with clear rollback strategy.**

---

## Purpose

- Enable safe experimentation
- Allow rollback after multiple commits
- Provide clear recovery points
- Maintain clean build state history
- Support user's need to undo complex changes

---

## Implementation

### Before Starting Work

```powershell
# Automatic checkpoint creation by KDS

BEFORE starting phase/task/feature:
  1. Verify current build is clean (0 errors, 0 warnings)
  2. Create git tag with clear naming
  3. Document checkpoint in session state
  4. Verify checkpoint created successfully

Command:
  git tag -a checkpoint-[feature-name]-start -m "[Feature] Starting [description]"

Example:
  git tag -a checkpoint-invoice-export-start -m "Invoice Export: Starting implementation"
```

### Checkpoint Naming Convention

```
Format: checkpoint-[feature-name]-[stage]

Stages:
  - start: Before any work begins
  - phase-complete: After each phase
  - done: After validation (0 errors, 0 warnings)

Examples:
  checkpoint-invoice-export-start
  checkpoint-invoice-export-phase-1-complete
  checkpoint-invoice-export-done
```

### Session State Documentation

```yaml
# KDS/sessions/session-[id].yaml

checkpoints:
  - tag: checkpoint-invoice-export-start
    timestamp: 2025-11-04T10:00:00Z
    commit: abc123def456
    feature: Invoice Export
    build_state:
      errors: 0
      warnings: 0
      tests_passing: true
    rollback_command: git reset --hard abc123def456
    
  - tag: checkpoint-invoice-export-phase-1-complete
    timestamp: 2025-11-04T10:30:00Z
    commit: def456abc789
    feature: Invoice Export - Phase 1
    build_state:
      errors: 0
      warnings: 0
      tests_passing: true
    rollback_command: git reset --hard def456abc789
```

---

## Rollback Discovery

### User Command

```markdown
#file:KDS/prompts/user/kds.md

Show me rollback points
```

Or:

```markdown
#file:KDS/prompts/user/kds.md

What checkpoints are available?
```

### KDS Response Format

```
📍 Available Checkpoints (Last 10)

Recent First:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] checkpoint-invoice-export-start
    📅 2025-11-04 10:00:00
    🎯 Feature: Invoice Export
    📝 Commit: abc123def (Starting implementation)
    ✅ Build: Clean (0 errors, 0 warnings)
    📊 Tests: 147 passing
    🔄 Rollback: git reset --hard abc123def
    
[2] checkpoint-pdf-feature-done
    📅 2025-11-03 14:30:00
    🎯 Feature: PDF Export
    📝 Commit: def456abc (Completed with validation)
    ✅ Build: Clean (0 errors, 0 warnings)
    📊 Tests: 145 passing
    🔄 Rollback: git reset --hard def456abc
    
[3] checkpoint-fab-animation-start
    📅 2025-11-02 09:15:00
    🎯 Feature: FAB Button Animation
    📝 Commit: 789abcdef (Starting implementation)
    ✅ Build: Clean (0 errors, 0 warnings)
    📊 Tests: 142 passing
    🔄 Rollback: git reset --hard 789abcdef

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 To rollback: Copy the rollback command or select checkpoint number

Which checkpoint to rollback to? [1-10 or 'cancel']:
```

### Rollback Execution

```markdown
User selects: 2

⚠️  ROLLBACK CONFIRMATION

You are about to rollback to:
  Checkpoint: checkpoint-pdf-feature-done
  Date: 2025-11-03 14:30:00
  Feature: PDF Export (Completed)
  
This will:
  ❌ DISCARD all commits after def456abc
  ❌ RESET working directory to checkpoint state
  ✅ PRESERVE untracked files (stash them first)
  
Commits that will be lost: 8 commits
  - abc123: feat: Add invoice service
  - def789: feat: Add invoice UI
  - ... (6 more)

Create backup branch before rollback? [Y/n]: Y

Creating backup: backup-before-rollback-2025-11-04
Stashing untracked files...
Rolling back to def456abc...

✅ Rollback complete!

Restored state:
  ✅ Build: Clean (0 errors, 0 warnings)
  ✅ Tests: 145 passing
  ✅ Backup branch: backup-before-rollback-2025-11-04
  ✅ Stash: stash@{0} (untracked files)
  
If you need to undo this rollback:
  git checkout backup-before-rollback-2025-11-04
```

---

## Enforcement

### Automatic Checkpoint Creation

```
WHEN user requests: "Plan: Add [feature]"

BEFORE creating plan:
  1. Check for checkpoint in last 5 commits
  2. IF no checkpoint found:
     → Create checkpoint-[feature]-start automatically
     → Verify clean build (Rule 20)
     → Document in session state
  3. PROCEED with planning

Message:
  📍 Checkpoint created: checkpoint-invoice-export-start
  ✅ Build verified: Clean (0 errors, 0 warnings)
  ✅ Ready for development
```

### Phase Completion Checkpoints

```
WHEN phase completes:
  1. Verify Definition of DONE (Rule 20)
  2. Create checkpoint-[feature]-phase-[N]-complete
  3. Document in session state
  4. Enable rollback to this phase

Message:
  📍 Phase 1 checkpoint created
  ✅ Build: Clean (0 errors, 0 warnings)
  ✅ Tests: All passing
  🔄 Can rollback to this point if needed
```

### Feature Completion Checkpoints

```
WHEN feature marked DONE:
  1. Verify Definition of DONE (Rule 20)
  2. Create checkpoint-[feature]-done
  3. Document final state
  4. Mark as stable rollback point

Message:
  📍 Feature checkpoint created: checkpoint-invoice-export-done
  ✅ Build: Clean (0 errors, 0 warnings)
  ✅ Tests: All passing
  ✅ Health: All checks passing
  🎯 Stable rollback point established
```

---

## Integration with Other Rules

### With Rule 20 (Definition of DONE)

Checkpoints are ONLY created when build is clean:
- 0 errors
- 0 warnings
- All tests passing

IF build is not clean:
  → FIX issues first
  → THEN create checkpoint
  → NO exceptions

### With TDD Workflow

```
Checkpoint Strategy + TDD:

1. checkpoint-[feature]-start (before TDD)
   ✅ Clean build
   
2. TDD RED phase
   ❌ Tests fail (expected)
   ❌ NO checkpoint (not clean build)
   
3. TDD GREEN phase
   ✅ Tests pass
   ✅ Build clean
   📍 Optional checkpoint-[feature]-green
   
4. TDD REFACTOR phase
   ✅ Tests still pass
   ✅ Build clean
   📍 checkpoint-[feature]-phase-complete
   
5. Feature complete
   ✅ All validation passes
   📍 checkpoint-[feature]-done
```

### With Brain Amnesia

Checkpoints are PRESERVED during amnesia:
- Git tags remain
- Session checkpoint history archived
- Rollback capability maintained

---

## Validation

### Health Check

```yaml
# health-validator.md checks

checkpoint_strategy:
  - Recent work has checkpoint? (within 10 commits)
  - Checkpoint at clean build state?
  - Session state documents checkpoints?
  - Rollback commands valid?
  
Warnings:
  ⚠️  No checkpoint in last 10 commits
  ⚠️  Checkpoint created at dirty build state
  ⚠️  Missing rollback documentation
```

### Session Review

```markdown
At end of session:

📊 Session Checkpoint Report

Checkpoints Created: 3
  ✅ checkpoint-invoice-export-start
  ✅ checkpoint-invoice-export-phase-1-complete
  ✅ checkpoint-invoice-export-done

Rollback Points Available: 3
All checkpoints at clean build: ✅

Next session can safely rollback to any checkpoint.
```

---

## Examples

### Example 1: Starting New Feature

```markdown
User: Plan: Add invoice export

KDS (automatic):
  📍 Creating checkpoint before planning...
  
  Running build validation...
  ✅ Build: Success (0 errors, 0 warnings)
  ✅ Tests: 147 passing
  
  Creating checkpoint: checkpoint-invoice-export-start
  Commit: abc123def
  Tag created: ✅
  
  📍 Checkpoint ready! Safe to proceed.
  
  Now creating plan for invoice export...
```

### Example 2: Multi-Commit Rollback

```markdown
User: I need to rollback the last 15 commits to before invoice export

KDS:
  📍 Finding checkpoint before invoice export...
  
  Found: checkpoint-pdf-feature-done (2025-11-03)
  - 15 commits before current HEAD
  - Last stable state before invoice work
  
  Rollback preview:
    From: abc123 (current) - Invoice export phase 3
    To: def456 (checkpoint) - PDF feature complete
    
  Commits to discard: 15
  Features affected: Invoice Export
  
  Create backup branch? [Y/n]: Y
  
  ✅ Backup created: backup-before-rollback-2025-11-04
  ✅ Rolling back...
  ✅ Rollback complete!
  
  Current state: PDF feature complete (clean build)
```

### Example 3: Checkpoint Discovery

```markdown
User: What are my recent checkpoints?

KDS:
  📍 Checkpoint History (Last 10)
  
  [1] checkpoint-invoice-export-phase-2-complete (2 hours ago)
  [2] checkpoint-invoice-export-phase-1-complete (4 hours ago)
  [3] checkpoint-invoice-export-start (6 hours ago)
  [4] checkpoint-pdf-feature-done (1 day ago)
  [5] checkpoint-fab-animation-done (2 days ago)
  
  All checkpoints at clean build state ✅
  
  Need to rollback? Select checkpoint number.
```

---

## Benefits

1. ✅ **Safe Experimentation** - Always have known-good state to return to
2. ✅ **Easy Recovery** - Find exact rollback point in complex commit history
3. ✅ **Clear History** - Checkpoints mark feature boundaries
4. ✅ **Clean States** - Every checkpoint is validated clean build
5. ✅ **User Confidence** - Know you can always undo complex changes
6. ✅ **Session Continuity** - Resume sessions with clear checkpoint reference

---

## Related Rules

- **Rule 20:** Definition of DONE (checkpoints only at clean builds)
- **Rule 18:** Challenge User Changes (protects checkpoint integrity)
- **Rule 16:** Brain Update Protocol (checkpoints trigger brain learning)

---

**Status:** ✅ ACTIVE (Tier 0 - Permanent)  
**Enforcement:** Automatic  
**Override:** NOT ALLOWED  
**Applies:** All development work starting v6.0
