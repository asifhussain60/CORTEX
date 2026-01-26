---
created_at: 2026-01-26T15:30:00Z
expires_at: 2026-02-25T15:30:00Z
lifetime_days: 30
category: governance
---

# CORE-040 Implementation: Documentation Lifecycle Management

## Objective
Implement prevention-first documentation bloat management through lifecycle metadata enforcement (CORE-040) and migrate relevant files to the `reports/` folder structure.

## Implementation Status

### ✅ Complete
- **CORE-040 Rule**: Added to tier0/governance/core-rules.yaml (28 rules total)
- **Lifecycle Validator**: cortex/governance/validators/lifecycle-validator.py
- **Metadata Schema**: Defined in CORE-040 specification

### 📋 Next Steps

#### 1. File Migration Strategy

**Source → Target Mapping:**

```
docs/*/filename.md                    → reports/documentation/{filename}.md
reports/*-report.md                   → DELETE (unless user-archived)
reports/*-status.md                   → DELETE (unless user-archived)
reports/*-summary.md                  → DELETE (unless user-archived)
reports/session-*.md                  → reports/session/{date}-{name}.md
reports/analysis/*.md                 → reports/analysis/{date}-{name}.md
reports/phase-*.md                    → reports/phase/{phase}-{name}.md
```

#### 2. Lifecycle Metadata Template

For files migrated to `reports/`, add YAML front-matter:

```yaml
---
created_at: 2026-01-26T15:30:00Z
expires_at: 2026-02-25T15:30:00Z
lifetime_days: 30
category: session|analysis|phase|test|tool
auto_delete_on_expiry: true
---

# File content here...
```

**Category Lifetimes:**
- `session`: 7 days (work artifacts)
- `analysis`: 30 days (analysis outputs)
- `phase`: 90 days (phase documentation)
- `test`: 14 days (test outputs)
- `tool`: 30 days (generic tool outputs)

#### 3. Folder Structure

Create or verify these folders exist:

```
reports/
├── documentation/        # Permanent user documentation
├── session/             # 7-day session artifacts
├── analysis/            # 30-day analysis outputs
├── phase/               # 90-day phase documentation
├── test/                # 14-day test artifacts
├── tool/                # 30-day tool outputs
└── lifecycle-registry.yaml  # Optional: central metadata
```

#### 4. File Cleanup Strategy

**DO NOT run cleanup during checks process.** Instead:

1. **Option A - Manual Cleanup** (Recommended for now)
   ```bash
   python -m cortex.governance.validators.lifecycle-validator check_expired_files
   ```
   Review results manually, then delete.

2. **Option B - Background Daemon** (Future)
   - Create optional daemon that runs on schedule
   - Reads lifecycle-registry.yaml or file metadata
   - Deletes expired files with auto_delete_on_expiry=true
   - Logs all deletions to audit trail

3. **Option C - Git Pre-Push Hook** (Alternative)
   - Warn about files expiring in next 7 days
   - Allow user to archive or exempt before push
   - Don't auto-delete (respects user intent)

#### 5. Naming Convention (CORE-028)

All files MUST use kebab-case naming with max 25 characters:

```
✅ VALID:
  analysis-2026-01-26-xyz.md     (26 chars - just over, rename to: ana-2026-01-26-xyz.md)
  session-phase-001-summary.md   (26 chars - rename to: phase-001-session.md)

❌ INVALID:
  Analysis Report 2026-01-26.md  (spaces)
  analysis_report_2026.md        (underscores)
  Phase 1 Completion Report.md   (spaces + camelCase)
```

#### 6. Exemptions

Files EXEMPT from lifecycle management:

```
docs/*/README.md                (permanent documentation)
docs/**/*.md                    (all docs/ content)
reports/*.yaml                  (data storage files)
reports/*/README.md             (structural docs)
```

## Execution Plan

### Phase 1: Assessment
```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Find files requiring migration
find reports/ -name "*.md" -o -name "*.txt" | head -20
find docs/ -name "*.md" -o -name "*.txt" | head -20

# List deprecated patterns (to delete)
find reports/ -name "*-report.md"
find reports/ -name "*-status.md"
find reports/ -name "*-summary.md"
```

### Phase 2: Migration
1. Review each file manually
2. Categorize into: keep (docs/), archive (reports/{category}/), delete
3. Add lifecycle metadata to kept files
4. Use kebab-case naming per CORE-028
5. Move/delete files
6. Update .gitignore if needed

### Phase 3: Validation
```bash
# Validate metadata on all reports files
python -c "
from pathlib import Path
from cortex.governance.validators.lifecycle-validator import LifecycleMetadataValidator
validator = LifecycleMetadataValidator()
for f in Path('reports').rglob('*.md'):
    is_valid, result = validator.validate_file(f)
    print(f'{f}: {\"VALID\" if is_valid else \"INVALID\"} - {result}')
"
```

### Phase 4: Documentation
- Update CORTEX.prompt.md with CORE-040 enforcement
- Add to pre-commit hook (warn-only for now)
- Document lifecycle metadata in contributor guide

## Key Principles

1. **Prevention > Cleanup**: Never accumulate, expire naturally
2. **Metadata-Driven**: Decisions based on file properties, not patterns
3. **Non-Blocking**: Cleanup doesn't interrupt core checks process
4. **User-Intent**: Archive mechanisms respect user wishes
5. **Governance-Aligned**: Fits CORTEX 4-tier architecture

## Success Criteria

✅ All `.md`, `.txt`, `.bak` files in `reports/` have lifecycle metadata
✅ `docs/` folder contains only permanent documentation
✅ Naming complies with CORE-028 (kebab-case, ≤25 chars)
✅ Lifecycle validator runs successfully with zero failures
✅ No files generated after this date without expires_at timestamp
✅ Pre-commit hook warns on missing lifecycle metadata

## Rollback Plan

If issues arise:
1. Git revert commits that moved/deleted files
2. Restore from backup
3. Re-migrate more carefully
4. Tag files with `no_auto_delete: true` for exceptions

---

**Next Review:** 2026-02-25
**Owner:** Asif Hussain
**Status:** Implementation Ready
