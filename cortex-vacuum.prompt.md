# CORTEX Vacuum - Repository Standardization Prompt

**Version:** 1.0  
**Date:** 2026-01-15  
**Purpose:** Define the specification and operational guidelines for the CORTEX repository structure standardization initiative.

---

## Executive Summary

The CORTEX Vacuum system is a three-phase repository reorganization framework that transforms the CORTEX codebase into a production-grade, standardized structure. It ensures:

- **Consistency**: All files follow kebab-case naming (≤20 characters)
- **Organization**: Files are distributed to appropriate tier folders based on function
- **Cleanliness**: Redundant, backup, and duplicate files are removed
- **Integrity**: All cross-file references are maintained and updated
- **Traceability**: Every change is logged and reversible

---

## Phase Architecture

### Phase 1: Analysis & Planning (Non-Destructive)
- **Goal**: Generate a complete migration plan without modifying files
- **Output**: `migration-plan.json`, `reference-map.json`, `analysis-report.md`
- **Safety**: 100% read-only; can be run unlimited times
- **Tool**: `cortex_vacuum_analyzer.py`

### Phase 2: Execution & Reference Updating (Controlled)
- **Goal**: Apply changes in dependency order with rollback capability
- **Output**: Modified files, rollback snapshots, execution log
- **Safety**: Generates snapshots before each operation
- **Tool**: `cortex_vacuum_executor.py`

### Phase 3: Verification & Reporting
- **Goal**: Validate that all references were updated correctly
- **Output**: Verification report, statistics, recommendations
- **Safety**: Read-only validation pass

---

## File Classification Rules

### Root-Level Files → Destination Mapping

#### Documentation Files
- **Pattern**: `*.md` files that are high-level or organizational
- **Destination**: `docs/`
- **Examples**:
  - `README.md` → stays in root (project-level)
  - `EXECUTIVE-*.md` → `docs/executive/`
  - `PHASE-*.md` → `docs/phases/`
  - `REVIEW-*.md` → `docs/reviews/`
  - `CURRENT-STATUS.md` → `docs/status.md`

#### Reports & Analysis
- **Pattern**: `*-REPORT.md`, `*-ANALYSIS.md`, `*-COMPLETION.md`
- **Destination**: `reports/` (consolidated by category)
- **Strategy**:
  - Group by prefix (AR-013, AR-014, etc.)
  - Create index files for related reports
  - Keep separate if they cover distinct phases/topics

#### Configuration & Infrastructure
- **Pattern**: `pytest.ini`, `requirements.txt`, `.env*`, config files
- **Destination**: `config/` or stay in root if project-critical
- **Rule**: Only `pytest.ini` and `requirements.txt` stay in root

#### Database Files
- **Pattern**: `*.db`, `*.db-shm`, `*.db-wal`
- **Destination**: `cortex-brain/state/` (already correct)
- **Action**: Verify and leave in place

#### Temporary/Archive Files
- **Pattern**: `*.bak`, `*-old*`, `*-new*`, `*-fixed*`, `*-enhanced*`, `*-backup*`
- **Action**: **DELETE** (no exceptions)

#### History & Metadata
- **Pattern**: `rollback_history.json`, `*.log`, `*.lock`
- **Destination**: `cortex-brain/audit-logs/`
- **Action**: Move and archive

#### Scripts
- **Pattern**: `*.py` files in root (except src/)
- **Destination**: `scripts/` (already exists)
- **Examples**: `verify_phases.py`, `init_db.py` → stay in scripts/

---

## File Naming Rules

### Convention: Kebab-Case (max 25 chars)

**Format**: `subject-descriptor-action` (meaningful, readable, complete)

**Examples**:
```
❌ ac-ar-013-03-status-report.md (too many prefixes)
✅ ar-013-status-report.md (19 chars) - Clear and complete

❌ CORTEX-MASTER-COMPLETION-ANALYSIS.md (36 chars, truncates badly)
✅ cortex-completion-analysis.md (25 chars) - Precise

❌ PHASE-CHAT-VERIFICATION-REPORT.md (too long, unclear abbreviation)
✅ phase-chat-verification.md (25 chars) - Complete meaning

❌ EXECUTIVE-BRIEF-FOR-DECISION.md (truncates to "exec-brief-for-de...")
✅ exec-decision-brief.md (19 chars) - Meaningful and readable

❌ IMPLEMENTATION-STATUS-BRIEF.md (loses meaning when abbreviated)
✅ implementation-status.md (24 chars) - Full semantic meaning
```

### Naming Principles

1. **Prioritize Readability**: Never truncate words mid-syllable; create abbreviated filenames that are still pronounceable and meaningful
2. **Selective Abbreviations**: Only abbreviate when necessary:
   - `executive` → `exec` (widely understood)
   - `implementation` → can stay full (24 chars is acceptable)
   - `analysis` → can stay full (8 chars)
   - `completion` → can stay full (10 chars)
   - Do NOT abbreviate domain-specific terms
3. **Remove Only Nonsemantic Words**: Remove "old", "new", "fixed", "enhanced", "current", "latest", "draft", "final", "updated"
4. **Maintain Complete Meaning**: A filename should convey its content without additional context
5. **Lowercase throughout**: All kebab-case, never MixedCase or SCREAMING_SNAKE_CASE
6. **Type suffix**: Include when helpful for clarity
   - `*-report.md` for reports
   - `*-config.yaml` for configs
   - `*-analysis.md` for analysis
   - Omit if name is already clear

### Folder Naming Rules

Same as files: kebab-case, max 25 chars, no nonsemantic adjectives. Prioritize readability and complete meaning.

**Examples**:
```
❌ acceptance-criteria (18 chars) → Keep as-is ✓
✅ ac-criteria (11 chars) - Good abbreviation

❌ response-templates (19 chars) → Keep as-is ✓
✅ response-templates (19 chars) - Clear and descriptive

✅ governance (10 chars) ✓ OK as-is - Concise and clear

✅ audit-logs (10 chars) ✓ OK as-is - Semantic and complete
```

---

## Reference Update Strategy

### Step 1: Pre-Flight Scan
Before ANY file movement, identify all references:
- **Markdown links**: `[text](path/to/file.md)`
- **Python imports**: `from path import file`
- **YAML references**: `- file: path/to/file`
- **Code comments**: `# See: path/to/file`

### Step 2: Build Reference Map
Create `reference-map.json`:
```json
{
  "old_path/file.md": {
    "new_path": "new_path/file-name.md",
    "references": [
      {
        "file": "src/core/module.py",
        "line": 42,
        "type": "import",
        "old_ref": "from old_path import file",
        "new_ref": "from new_path import file_name"
      }
    ]
  }
}
```

### Step 3: Update References
For each file being moved/renamed:
1. Move/rename the file
2. Update all references in order of dependency
3. Verify no broken links remain
4. Log each change with timestamp

### Step 4: Verification Pass
Run a second scan to ensure:
- ✅ No broken imports
- ✅ No broken markdown links
- ✅ All references updated
- ✅ No old paths referenced

---

## Deletion Rules

**Files MUST be deleted if:**
- Backup files: `*.bak`, `*.backup`, `*-backup.*`
- Redundant patterns: `*-old*`, `*-new*`, `*-fixed*`, `*-enhanced*`, `*-temp*`
- Duplicates: Identical content as another file (keep newer, delete older)
- Obsolete: Clearly superseded by newer version (check with timestamps)
- Test artifacts: `*.pyc`, `__pycache__`, `.pytest_cache` (Git ignores anyway)

**Files MUST NOT be deleted:**
- Active configuration: `pytest.ini`, `requirements.txt`
- Database files: `*.db` and companion files
- Active code: Any `.py` in `src/`, `tests/`, `scripts/`
- Current documentation: Non-redundant `.md` files

---

## Report Consolidation Strategy

### Identification Phase
Scan for report files with similar characteristics:
- Same prefix (e.g., `AR-013-*`, `AC-AR-013-*`)
- Same category (completion, status, analysis)
- Related timestamps

### Consolidation Logic
```
IF files cover same topic AND created close in time:
  → Merge into single index document
  → Archive old files to reports/archive/
  → Create redirect/reference in old location

ELSE IF files are snapshots of evolving topic:
  → Keep in versioned subdirectory
  → Create index with changelog
  → Link from main reports/

ELSE:
  → Keep separate, organize by category
  → Ensure consistent naming
```

### Example Consolidation
```
BEFORE:
├── reports/
│   ├── AC-AR-014-01-STATUS-REPORT.md
│   ├── AR-014-COMPLETION-REPORT.md
│   └── AR-013-TRILOGY-COMPLETION-REPORT.md

AFTER:
├── reports/
│   ├── index.md (links to all)
│   ├── ar-013-trilogy-completion.md (merged)
│   ├── ar-014-completion.md (merged)
│   └── archive/
│       ├── ac-ar-014-01-status.md
│       └── ar-013-trilogy-completion-v1.md
```

---

## Target Structure

```
CORTEX/
├── cortex-vacuum.prompt.md          ← This file
├── README.md
├── requirements.txt
├── pytest.ini
├── config/
│   ├── cortex.yaml
│   └── governance.yaml
├── docs/
│   ├── executive/
│   │   ├── executive-brief.md
│   │   ├── decision-summary.md
│   │   └── strategy.md
│   ├── phases/
│   │   ├── phase-chat-verify.md
│   │   ├── phase-vision-core.md
│   │   └── phase-vision-adv.md
│   ├── reviews/
│   │   └── review-index.md
│   └── status.md
├── reports/
│   ├── index.md
│   ├── ar-013-trilogy.md
│   ├── ar-014-completion.md
│   ├── ar-015-handoff.md
│   └── archive/
├── scripts/
│   ├── init-db.py
│   ├── check-dor.py
│   ├── verify-phases.py
│   ├── run-cortex-vacuum.py
│   └── cortex-vacuum/
│       ├── analyzer.py
│       └── executor.py
├── cortex-brain/
│   ├── tier0/
│   ├── tier1/
│   ├── tier2/
│   ├── tier3/
│   ├── audit-logs/
│   │   └── vacuum-logs/
│   └── state/
├── src/
│   ├── core/
│   ├── infrastructure/
│   ├── orchestrators/
│   ├── mcp/
│   │   └── tools/
│   │       ├── cortex_vacuum_analyzer.py
│   │       ├── cortex_vacuum_executor.py
│   │       └── cortex_vacuum_registration.py
│   └── tools/
├── tests/
│   ├── unit/
│   │   └── cortex_vacuum/
│   ├── integration/
│   └── fixtures/
└── .github/
    └── roadmap/
```

---

## Execution Workflow

### Step 1: Dry Run (Analysis Only)
```bash
python scripts/run-cortex-vacuum.py analyze --output-dir cortex-brain/vacuum/
```
**Output**: Review `migration-plan.json` and `analysis-report.md`

### Step 2: Review & Approve
1. Inspect the analysis report
2. Validate proposed changes
3. Check reference map for accuracy
4. Approve or adjust classification rules

### Step 3: Execute
```bash
python scripts/run-cortex-vacuum.py execute \
  --plan cortex-brain/vacuum/migration-plan.json \
  --dry-run  # Optional: first time only
```

### Step 4: Verify
```bash
python scripts/run-cortex-vacuum.py verify --fix-issues
```

### Step 5: Rollback (If Needed)
```bash
python scripts/run-cortex-vacuum.py rollback \
  --snapshot cortex-brain/snapshots/backup-2026-01-15T10-30-45.json
```

---

## Safety Guarantees

### Non-Destructive Analysis
- ✅ Phase 1 never modifies anything
- ✅ Can run unlimited times
- ✅ Zero side effects

### Controlled Execution
- ✅ Snapshots created before each phase
- ✅ Rollback capability built-in
- ✅ Reference updates verified before commit

### Audit Trail
- ✅ Every change logged with timestamp
- ✅ Reason for each deletion documented
- ✅ Before/after reference maps saved

---

## Special Cases & Exceptions

### Case 1: Files Referenced by External Systems
**Rule**: If a file is referenced by CI/CD or external tools, add to `PROTECTED_PATHS.yaml`
```yaml
protected:
  - pytest.ini
  - requirements.txt
  - .github/workflows/*
```

### Case 2: Database Relationships
**Rule**: If database structure depends on file paths, document in `cortex-brain/state/schema-references.yaml`

### Case 3: Ambiguous Files
**Rule**: Files that could go in multiple locations:
1. Check file content
2. Determine primary purpose
3. Create symlinks or cross-references for discoverability

---

## Success Criteria

After vacuum execution:

- ✅ All files follow kebab-case (≤20 chars)
- ✅ All folders follow kebab-case (≤20 chars)
- ✅ Zero backup/temp files remain
- ✅ Zero broken references
- ✅ All reports consolidated and indexed
- ✅ Rollback snapshot available
- ✅ Change log complete and auditable
- ✅ Repository clean and maintainable

---

## Future Maintenance

### Quarterly Reviews
Review structure quarterly to ensure continued compliance:
```bash
python scripts/run-cortex-vacuum.py analyze --check-compliance
```

### Pre-Merge Checks
Before merging to main:
```bash
python scripts/run-cortex-vacuum.py verify --fail-on-violations
```

### New File Guidelines
Document in `CONTRIBUTING.md`:
- All new files must follow naming convention
- Place in correct tier/folder before creating
- Update index files after creation

---

## References

- **Analysis Tool**: `src/mcp/tools/cortex_vacuum_analyzer.py`
- **Execution Tool**: `src/mcp/tools/cortex_vacuum_executor.py`
- **CLI Wrapper**: `scripts/run-cortex-vacuum.py`
- **Configuration**: `cortex-brain/vacuum/config.yaml`

---

**Document Control**  
Last Updated: 2026-01-15  
Maintained By: Asif Hussain  
Status: Production Ready
