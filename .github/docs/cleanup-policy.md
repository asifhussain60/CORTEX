# CORTEX Cleanup & Organization Policy

**Version:** 1.0  
**Status:** ACTIVE  
**Last Updated:** 2026-01-14

---

## Root Directory Organization

Root-level markdown files create clutter. All project documentation must follow this structure:

### File Categories & Storage Locations

| Category | Location | Example | Naming Convention |
|----------|----------|---------|-------------------|
| **Project Info** | `.github/docs/` | `project-overview.md` | kebab-case |
| **Status Tracking** | `.github/docs/` | `current-status.md` | kebab-case |
| **Implementation Plans** | `.github/roadmap/` | (already structured) | PHASE-XX-*.yaml |
| **Roadmap & Phases** | `.github/roadmap/` | cortex-master.yaml | existing structure |
| **Agent Instructions** | `.github/agents/` | cortex-builder.md | already organized |
| **Prompts** | `.github/prompts/` | cortex-builder.prompt.md | already organized |
| **Chat Transcripts** | `.github/.workspace/phase-copilot-chats/` | (auto-generated) | phase-XX.md |
| **Evidence Artifacts** | `.github/evidence/` | (phase completion reports) | {phase}-artifacts.yaml |

### Root Files Policy

**✅ ALLOWED in root:**
- `README.md` — Project overview only
- `pytest.ini` — Test configuration
- `requirements.txt` — Dependencies
- `.github/`, `src/`, `tests/`, `cortex-brain/`, `scripts/` — Folders
- `.gitignore`, `.env`, `.vscode/` — System config

**❌ NOT ALLOWED in root (must be moved):**
- `STATUS.md` → `.github/docs/current-status.md`
- `PHASE-*.md` → Archive or delete (redundant with YAML)
- `AC-*.md` → Delete (evidence captured in governance.db)
- `PLAN-VS-ACTUAL.md` → `.github/docs/plan-vs-actual.md`
- `EXECUTIVE-*.md` → `.github/docs/exec-reports/` (kebab-case names)
- `REVIEW-*.md` → `.github/docs/review-reports/` (kebab-case names)
- `ARTIFACTS-*.md` → `.github/evidence/phase-artifacts.yaml`
- `QUICK-SCORECARD.md` → `.github/docs/scorecard.md`

---

## Naming Conventions

### Kebab-Case Format
- **Pattern:** `lowercase-words-separated-by-hyphens`
- **Max Length:** 20 characters (excluding extension)
- **Examples:**
  - ✅ `current-status.md`
  - ✅ `plan-vs-actual.md`
  - ✅ `exec-report.md`
  - ❌ `CurrentStatusReport.md` (PascalCase)
  - ❌ `Current_Status_Report.md` (snake_case)
  - ❌ `current-status-report-updated.md` (too long)

### Directory Structure for `.github/docs/`
```
.github/docs/
├── current-status.md           # Status updates (replaces STATUS.md)
├── plan-vs-actual.md          # Comparison report
├── scorecard.md               # Quick scorecard (replaces QUICK-SCORECARD.md)
├── exec-reports/              # Executive reports
│   ├── implementation.md       # (replaces EXECUTIVE-IMPLEMENTATION-REVIEW.md)
│   ├── summary.md            # (replaces EXECUTIVE-SUMMARY.md)
│   └── review.md             # (replaces IMPLEMENTATION-REVIEW.md)
├── review-reports/            # Review documents
│   ├── index.md              # (replaces REVIEW-INDEX.md)
│   └── summary.md            # (replaces REVIEW-SUMMARY.md)
└── phase-lock-reports/        # Phase completion reports (avoid creating)
    └── phase-01-lock.yaml     # YAML preferred over MD
```

---

## Cleanup Process for Each Phase

### Before Locking a Phase

**Mandatory Cleanup Checklist:**

1. ✅ **No temporary files in root**
   - Verify no phase-specific `.md` files exist in root
   - Example: Delete `PHASE-02-PROGRESS.md`, `PHASE-02-STARTUP-CHECKLIST.md`

2. ✅ **Evidence captured in governance.db**
   - All AC-ID progress recorded in audit_log
   - Evidence bundles stored in evidence_bundle table
   - No standalone markdown AC reports in root

3. ✅ **Documentation consolidated**
   - If summary documents created, move to `.github/docs/`
   - Use kebab-case naming
   - Keep under 20 characters

4. ✅ **Status.md updated**
   - Single source for current project status
   - Updated via script, not manual file creation
   - Stored at `.github/docs/current-status.md` (after migration)

5. ✅ **Git cleanup**
   - All changes committed with clear messages
   - Phase checkpoint created: `git commit -m "phase-XX: COMPLETED - cleanup done"`

### Cleanup Automation (Optional)

Use `.github/prompts/tools/consolidate.py` to consolidate large documentation sets:

```bash
python .github/prompts/tools/consolidate.py \
  --folder .github/docs/exec-reports \
  --format yaml \
  --cleanup
```

Result: Creates `.github/docs/exec-reports.yaml` consolidation, deletes source `.md` files.

---

## Improvement Opportunities

### 1. Eliminate Redundant Documentation

**Problem:** Phase-02-PROGRESS.md is 579 lines but duplicates info already in:
- cortex-master.yaml (phase_tracker)
- governance.db (audit_log table)
- Git commit history

**Solution:**
- ❌ Don't create PHASE-XX-PROGRESS.md files
- ✅ Query governance.db for real-time progress
- ✅ Use git log for commit history
- ✅ Update phase_tracker status in cortex-master.yaml

### 2. Prefer YAML over Markdown for Structured Data

**Problem:** Phase completion reports in `.md` format are not machine-readable

**Solution:**
- Phase lock reports should be `.yaml` not `.md`
- Example: `phase-02-lock-report.yaml` containing:
  - AC-IDs completed
  - Test counts
  - Audit verification results
  - Git checkpoint hash

### 3. Chat Transcripts Auto-Archive

**Problem:** Phase chat transcripts in `.github/.workspace/phase-copilot-chats/` grow large

**Solution:**
- Keep only CURRENT phase transcript in workspace
- Archive completed phase transcripts to `.github/evidence/chat-archive/`
- Use consolidate.py to compress old transcripts into `.yaml` summaries

### 4. Make Status.md Generation Programmatic

**Problem:** STATUS.md manually updated after each phase

**Solution:**
- Create `scripts/generate-status.py` that:
  - Queries cortex-master.yaml
  - Queries governance.db for audit stats
  - Generates current-status.md automatically
  - Run as: `python scripts/generate-status.py`

---

## Action Items for This Session

1. ✅ Create `.github/docs/` folder
2. ✅ Create this cleanup policy document
3. ⏳ Move root `.md` files to appropriate locations with kebab-case names
4. ⏳ Delete redundant files
5. ⏳ Update `.github/prompts/cortex-builder.prompt.md` to include cleanup gate
6. ⏳ Update cortex-master.yaml phase definitions to add cleanup task
7. ⏳ Delete phase-specific progress markdown files (keep YAML evidence only)

---

## Key Principles

1. **Single Source of Truth:** cortex-master.yaml + governance.db
2. **No Duplication:** Evidence in governance.db, not separate files
3. **Machine-Readable:** Prefer YAML/JSON over Markdown for structured data
4. **Clean Root:** Only essential files (README, pytest.ini, requirements.txt)
5. **Kebab-Case:** All new files follow kebab-case convention
6. **20-Char Max:** Filenames concise and scannable
7. **Evidence Immutable:** Once locked, phase documentation is read-only

---
