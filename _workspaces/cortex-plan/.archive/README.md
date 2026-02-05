# cortex-plan Archive

**Purpose:** Historical records of completed phases, deprecated scripts, and archived reports  
**Updated:** 2026-02-05  
**Maintenance:** Documents moved here are reference-only, not for active development

---

## 📁 Archive Structure

```
.archive/
├── README.md                    # This file
├── completed-phases/            # Phase YAMLs marked COMPLETE
├── shell-scripts/               # Deprecated shell scripts (migrated to Python/MCP)
├── enhancements/                # Individual enhancement phase reports
└── completed-reports/           # Historical completion reports (pre-existing)
```

---

## 📋 Archive Categories

### completed-phases/
**Purpose:** Phase YAML specifications that have been fully implemented and verified

**Criteria for archival:**
- Phase status = COMPLETE in cortex-plan-index.md
- Implementation verified in production
- Tests passing
- Documentation updated

**Note:** These files remain searchable for reference but are not part of active planning.

---

### shell-scripts/
**Purpose:** Shell scripts that have been migrated to Python or MCP tools

**Criteria for archival:**
- Functionality replicated in Python/MCP
- No active usage in workflows
- Documented deprecation plan

**Migration path:** Shell → Python → MCP tools (for production automation)

---

### enhancements/
**Purpose:** Individual enhancement phase completion reports (consolidated into progress trackers)

**Criteria for archival:**
- Phase completion report created
- Consolidated into main progress tracker (e.g., ENH-017-PROGRESS.md)
- Details preserved for historical reference

**Example:** ENH-017-PHASE-{1,2,3}-COMPLETION.md → Consolidated into ENH-017-PROGRESS.md

---

### completed-reports/
**Purpose:** Historical execution reports from early phases (pre-existing archive)

**Contents:** Phase execution reports, migration summaries, status updates from phases 0-15

---

## 🔍 Finding Archived Content

### By Phase Number
```bash
# Find all artifacts for Phase 10
find .archive -name "*PHASE-10*" -o -name "*phase-10*"
```

### By Enhancement ID
```bash
# Find all ENH-017 artifacts
find .archive -name "*ENH-017*"
```

### By Date Range
```bash
# Find files archived in February 2026
find .archive -type f -newermt "2026-02-01" ! -newermt "2026-03-01"
```

---

## 📊 Archive Metrics

| Category | Count | Last Updated |
|----------|-------|--------------|
| Completed Phases | 0 | 2026-02-05 |
| Shell Scripts | 0 | 2026-02-05 |
| Enhancement Reports | 3 | 2026-02-05 |
| Historical Reports | ~20 | 2026-02-02 |

**Total Archive Size:** ~500KB (mostly markdown)

---

## 🚫 What NOT to Archive

**Active development artifacts:**
- Phase YAMLs with status = PLANNED or IN PROGRESS
- Current progress trackers (ENH-*-PROGRESS.md)
- Active shell scripts (if any)
- README.md, cortex-plan-index.md (always active)

**System files:**
- .gitignore
- Directory READMEs
- Archive metadata (this file)

---

## 🔄 Archive Maintenance

**Frequency:** Ad-hoc when phases complete or files obsolete  
**Process:**
1. Verify phase/enhancement completion
2. Update cortex-plan-index.md status
3. Move files to appropriate archive subdirectory
4. Update this README with metrics
5. Commit with message: "archive: Move Phase X artifacts"

**Retention:** Indefinite (git history provides full lineage)

---

## 📝 Archive History

### 2026-02-05
- Created organized archive structure
- Moved ENH-017 phase reports to enhancements/
- Established archival criteria documentation

### 2026-02-02
- Pre-existing completed-reports/ archive maintained
- Historical phase execution reports preserved

---

**Note:** This archive follows CORE-040 (Documentation Lifecycle) and CORE-038 (File Placement) principles.
