⚠️  DIRTY STATE DETECTED - USER CONSENT REQUIRED

Attempted: '{operation}'
Git Status:
{git_status}

Uncommitted Changes Detected:
{modified_files}

⚠️  WARNING:
You have uncommitted changes that could be lost or overwritten.

OPTIONS:

A) Commit your changes first (RECOMMENDED):
   git add .
   git commit -m "WIP: [describe your changes]"
   
B) Stash changes and continue:
   git stash save "WIP: saved before CORTEX work"
   (restore later with: git stash pop)
   
C) Proceed anyway:
   CORTEX will create a checkpoint of current state
   You can rollback if needed

Please choose an option:
- Type "A" to commit first
- Type "B" to stash changes
- Type "C" to proceed with checkpoint
- Type "cancel" to abort operation
