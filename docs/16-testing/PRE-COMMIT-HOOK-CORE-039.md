# Pre-Commit Hook: CORE-039 Unnecessary Markdown Prevention

**Status:** ✅ Active & Tested  
**Last Updated:** January 29, 2026  
**Authority:** CORE-039 - Documentation Lifecycle Management

---

## Overview

The pre-commit hook has been enhanced with a CORE-039 check that prevents committing unnecessary markdown files to the repository. This prevents bloat from informational, summary, and reference documents that shouldn't be version-controlled.

## What Gets Blocked

The hook prevents committing the following types of markdown files (case-insensitive, recursive scan):

### Summary Files
- `*FINAL*SUMMARY*.md` - Phase/session final summaries
- `*COMPLETE*SUMMARY*.md` - Completion summaries
- `*SESSION*SUMMARY*.md` - Session summary reports

### Report Files
- `*STATUS*REPORT*.md` - Status reports (informational only)
- `*COMPLETION*REPORT*.md` - Completion reports (reference only)
- `*PROGRESS*REPORT*.md` - Progress tracking reports

### Reference Files
- `*QUICK*REFERENCE*.md` - Quick reference guides
- `*QUICK*REF*.md` - Quick reference documents
- `*CHEATSHEET*.md` - Quick reference sheets

### Temporary Files
- `*SNAPSHOT*.md` - Snapshots of system state
- `*BACKUP*.md` - Backup documents
- `*TEMP*.md` - Temporary documentation
- `*ARCHIVE*.md` - Archived documents
- `*DEPRECATED*.md` - Deprecated documentation
- `*LEGACY*.md` - Legacy documentation
- `*MIGRATION*INVENTORY*.md` - Migration tracking

### Index/Tracker Files
- `INDEX.md` - Index documents
- `*TRACKER*.md` - Tracking documents
- `*PLAN*.md` - Planning documents

## What's Allowed

The following markdown files ARE allowed and will pass the check:

### Documentation Folders
- Any `.md` file in `docs/` subdirectories
- Any `.md` file in `_workspaces/docs/` subdirectories

### Root-Level Documentation
- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE.md` - License document
- `CODE_OF_CONDUCT.md` - Community standards

## Hook Behavior

When an unnecessary markdown file is detected in staged changes:

### 1. Error Message
```
❌ UNNECESSARY MARKDOWN FILES DETECTED (CORE-039)
These files are informational/summary and should not be committed to repo

Staged files to remove:
  ✗ TEST-SESSION-SUMMARY.md
```

### 2. Explanation
The hook lists all file patterns that are not permitted.

### 3. Remediation Guidance
The hook provides three options:

#### Option 1: Move to Proper Documentation
If the content is genuinely needed as documentation:
```bash
# Move to docs/ with proper structure
mv TEST-SESSION-SUMMARY.md docs/16-testing/test-session-guide.md
git add docs/16-testing/test-session-guide.md
```

#### Option 2: Remove from Staging (Default)
If the file is temporary or informational:
```bash
git reset HEAD <file>  # Remove from staging
rm <file>              # Delete the file
```

#### Option 3: Add to .gitignore (Exceptional Cases)
Only if absolutely necessary and team-approved:
```bash
echo "<pattern>" >> .gitignore
git add .gitignore
# Discuss with team before doing this
```

## Hook Configuration

### Location
`.git/hooks/pre-commit`

### Patterns (Regex-based)
```bash
UNNECESSARY_MD_PATTERNS=(
    "FINAL.*SUMMARY"
    "COMPLETE.*SUMMARY"
    "STATUS.*REPORT"
    "SESSION.*SUMMARY"
    "PROGRESS.*REPORT"
    "COMPLETION.*REPORT"
    "QUICK.*REFERENCE"
    "CHEATSHEET"
    "MIGRATION.*INVENTORY"
    "QUICK.*REF"
    "SNAPSHOT"
    "BACKUP"
    "TEMP"
    "ARCHIVE"
    "DEPRECATED"
    "^OLD"
    "LEGACY"
    "PHASE.*COMPLETE"
    "PLAN\\.MD"
    "TRACKER\\.MD"
    "INDEX\\.MD"
)
```

### Scope
- **Recursive:** Yes - scans all folders and subfolders
- **Case-sensitive:** No - matches `Test-Session-Summary.md`, `TEST-SESSION-SUMMARY.MD`, etc.
- **Exclusions:** 
  - `docs/` folder (all subdirectories)
  - `_workspaces/docs/` folder (all subdirectories)
  - Root-level allowlisted files (README.md, CHANGELOG.md, etc.)

## Testing the Hook

### Create Test File
```bash
cat > TEST-SESSION-SUMMARY.md << EOF
# Test Session Summary

This is a test file to verify the pre-commit hook detects unnecessary markdown.
EOF
```

### Stage and Test
```bash
git add TEST-SESSION-SUMMARY.md
git commit -m "test"  # Will fail with CORE-039 error
```

### Verify Hook Works
Hook output:
```
❌ UNNECESSARY MARKDOWN FILES DETECTED (CORE-039)
These files are informational/summary and should not be committed to repo

Staged files to remove:
  ✗ TEST-SESSION-SUMMARY.md

These file types are not permitted:
  • *FINAL*SUMMARY* - Phase/session summaries (temporary documentation)
  • ...
```

### Clean Up
```bash
git reset HEAD TEST-SESSION-SUMMARY.md
rm TEST-SESSION-SUMMARY.md
```

## Integration with Other Checks

The CORE-039 check runs as part of the pre-commit hook pipeline:

1. **Copyright Statement Check** - Prevents copyright in .py files
2. **Bare Except Clause Check** - CORE-013 enforcement
3. **Type Hints Check** - CORE-011 enforcement (warning)
4. **File Placement Check** - CORE-038 enforcement
5. **File Naming Check** - CORE-028 enforcement
6. **CORE-035 Check** - Single implementation enforcement
7. **CORE-039 Check** - Unnecessary markdown prevention ← NEW

## Why This Matters

### Problem
Without this check, the repository accumulates many markdown files that are:
- Temporary documentation (session summaries, status reports)
- Informational only (quick references, cheatsheets)
- Redundant with tracked documentation in `docs/`
- Not part of the source code functionality

### Solution
The pre-commit hook enforces a clean documentation structure:
- Functional documentation lives in `docs/` with proper organization
- Temporary/informational files are kept local or in `.gitignore`
- Repository remains focused on code and design documentation
- Makes it easy to find official documentation vs. temporary notes

## Best Practices

### Creating Documentation
1. **If it's permanent technical docs:** Put it in `docs/{topic}/` with kebab-case naming
2. **If it's temporary/reference:** Keep it local, don't commit
3. **If it's a status report:** Don't commit at all, use separate tracking
4. **If it's a guide:** Move to `docs/` with proper structure

### File Naming
- Permanent docs: `kebab-case-title.md` in `docs/`
- Examples: `docs/07-guides/redis-setup-guide.md`, `docs/16-testing/e2e-testing.md`
- Avoid: `PHASE-8-COMPLETE-SUMMARY.md`, `SESSION-SUMMARY.md`, `STATUS-REPORT.md`

### Moving Files to Documentation
```bash
# Before (wrong)
PHASE-8-COMPLETE-FINAL-SUMMARY.md  # Gets blocked

# After (correct)
docs/phases/phase-8-consolidation-guide.md  # Gets committed
```

## Troubleshooting

### "Hook rejected my file!"
**Solution:** Check if it matches the unnecessary patterns. If it's meant to be documentation, move to `docs/`.

### "I need to commit this summary temporarily"
**Solution:** Add to `.gitignore` or a `_local/` directory that's gitignored.

### "This pattern is too broad"
**Solution:** Contact the team to discuss if the pattern should be adjusted (requires CORE-039 spec change).

### "I want to bypass the hook"
**NOT RECOMMENDED, but possible:**
```bash
git commit --no-verify  # Bypasses pre-commit hook
```
Only use if absolutely necessary and discuss with team.

## Related Rules

- **CORE-035:** Single Canonical Implementation
- **CORE-038:** File Placement Policy
- **CORE-028:** File Naming Policy
- **CORE-039:** Documentation Lifecycle Management ← This check

---

**Authority:** CORTEX Development Team  
**Last Verified:** January 29, 2026  
**Status:** ✅ Production Ready
