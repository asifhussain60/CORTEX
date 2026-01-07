# CORTEX5 Epic Archive Directory

**Purpose:** Permanent storage for cortex5-epic backups and historical snapshots  
**Location:** `cortex-brain/archives/cortex5-epic/`  
**Created:** 2026-01-07

---

## 📚 Archive Contents

### Backup: 2026-01-07 08:34 AM (Pre-Restructuring)
**Folder:** `backup-20260107-083422/`  
**Manifest:** `backup-20260107-083422-manifest.yaml`  
**File Count:** 61 files  
**Size:** ~500KB  
**Purpose:** Pre-restructuring snapshot before Planning System v5 compliance

**Context:**
This backup captures the cortex5-epic state immediately before implementing:
- Root folder cleanup (only 3 files allowed at root)
- Feature-based architecture (features/{feature-name}/)
- Epic progress tracker (10 features, 3 tiers)
- Context folder for supporting documents

**Status:** ✅ All content verified and preserved in current epic

---

## 🎯 Archive Policy

### What Gets Archived
1. **Pre-migration backups** - State before major structural changes
2. **Milestone snapshots** - Epic state at key completion points
3. **Rollback checkpoints** - Known-good states for recovery
4. **Historical artifacts** - Old plan-viewers, obsolete structures

### Retention Policy
- **Critical backups:** Retain indefinitely (e.g., pre-restructuring)
- **Milestone snapshots:** Retain until epic completion + 6 months
- **Rollback checkpoints:** Retain until next stable release
- **Historical artifacts:** Review annually for archival or deletion

### Access Policy
- **Read access:** All CORTEX users
- **Write access:** Automated archival processes only
- **Deletion:** Requires manual approval + verification

---

## 📋 Archive Manifest Index

| Backup ID | Date | Purpose | File Count | Status |
|-----------|------|---------|------------|--------|
| backup-20260107-083422 | 2026-01-07 | Pre-restructuring snapshot | 61 | ✅ Verified |

---

## 🔍 How to Use This Archive

### Viewing Backup Contents
```bash
# List all backups
ls -la cortex-brain/archives/cortex5-epic/

# View specific backup
ls -R cortex-brain/archives/cortex5-epic/backup-20260107-083422/

# Read backup manifest
cat cortex-brain/archives/cortex5-epic/backup-20260107-083422-manifest.yaml
```

### Comparing Backup to Current Epic
```bash
# Full comparison
diff -rq cortex-brain/archives/cortex5-epic/backup-20260107-083422/ \
        cortex-brain/documents/planning/active/cortex5-epic/

# File count comparison
find cortex-brain/archives/cortex5-epic/backup-20260107-083422/ -type f | wc -l
find cortex-brain/documents/planning/active/cortex5-epic/ -type f | wc -l
```

### Restoring from Backup
```bash
# 1. Review backup manifest first
cat cortex-brain/archives/cortex5-epic/backup-20260107-083422-manifest.yaml

# 2. Backup current state (safety)
mv cortex-brain/documents/planning/active/cortex5-epic \
   cortex-brain/documents/planning/active/cortex5-epic-$(date +%Y%m%d-%H%M%S)

# 3. Restore from archive
cp -R cortex-brain/archives/cortex5-epic/backup-20260107-083422 \
      cortex-brain/documents/planning/active/cortex5-epic

# 4. Verify restoration
sha256sum -c backup-checksums.txt
```

---

## 🔐 Integrity & Security

### Checksum Verification
All backups include SHA256 checksums for integrity verification:
```bash
# Verify backup integrity
cd cortex-brain/archives/cortex5-epic/backup-20260107-083422/
sha256sum -c ../../backup-20260107-083422-manifest.yaml
```

### Access Control
- Archives are **read-only** after creation
- Modifications require **manual approval**
- Deletions logged in **audit trail**

---

## 📝 Related Documentation

**Epic Documentation:**
- `cortex5-epic/master-plan.md` - Epic overview and goals
- `cortex5-epic/reports/epic-restructuring-status.md` - Restructuring status
- `cortex5-epic/tracking/epic-progress-tracker.json` - Progress tracking

**Archive Plans:**
- `cortex5-epic/tracking/00-cortex5-epic-archive-and-viewer-plan.md` - Archive plan
- `cortex5-epic/reports/archive-and-viewer-executive-summary.md` - Executive summary

---

## 🚀 Future Backups

When creating new backups:
1. Generate unique backup ID: `backup-{YYYYMMDD}-{HHMMSS}`
2. Create manifest: `{backup-id}-manifest.yaml`
3. Include SHA256 checksums for all files
4. Document backup purpose and context
5. Update this README with new entry

---

**Archive Created:** 2026-01-07  
**Managed By:** CORTEX Planning System v5  
**Status:** ✅ ACTIVE
