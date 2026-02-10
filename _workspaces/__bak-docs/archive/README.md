# CORTEX Archive Index
**Created:** 2026-02-03 | **Purpose:** Consolidated archive of historical documentation

---

## 📋 Archive Structure

This directory contains historical markdown documents moved from the repository root and workspace directories to maintain CORE-002 compliance (no markdown generation outside docs/).

### Directory Organization

```
docs/archive/
├── phases/              # Phase completion reports, progress summaries
├── testing/             # Test documentation and completion summaries  
├── workspaces/          # Workspace planning docs and chat logs
└── reports/             # Analysis reports, governance docs, implementation summaries
```

---

## 📊 Archive Statistics

**Total Archived:** 33+ documents  
**Cleanup Date:** 2026-02-03  
**Reason:** P3 markdown sprawl cleanup (AUDIT finding)

### Archived Categories

| Category | Count | Location | Examples |
|----------|-------|----------|----------|
| **Phase Reports** | 15+ | `phases/` | PHASE-22-P0-COMPLETE.md, PRODUCTION_READINESS_REPORT.md |
| **Test Docs** | 3 | `testing/` | QUICK-REFERENCE.md, COMPLETION-SUMMARY.md |
| **Workspace Docs** | 10+ | `workspaces/` | chat logs, implementation reports, status docs |
| **Analysis Reports** | 12+ | `reports/` | duplication audits, governance reports, cleanup reports |

---

## 🔍 Finding Archived Documents

### By Date
Most documents have timestamps in filenames or git history. Use:
```bash
git log --follow -- docs/archive/<category>/<filename>
```

### By Topic
| Topic | Search Pattern | Location |
|-------|----------------|----------|
| Phase 22 | `PHASE-22-*` | `phases/` |
| Phase 20 | `PHASE-20-*` | `phases/` |
| Dashboard | `dashboard`, `FIX-*` | `reports/`, `workspaces/` |
| Cleanup | `CLEANUP-*`, `ROOT-*` | `reports/` |
| Duplication | `duplication-audit-*` | `reports/` |
| Governance | `CORE-*`, `ac-*`, `core-*` | `reports/` |

---

## 🚫 Exclusions (Not Archived)

The following were intentionally **kept in original locations**:

| Location | Files | Reason |
|----------|-------|--------|
| `README.md` | Root and subdirs | Essential project documentation |
| `docs/**/*.md` | All files | Canonical documentation location |
| `.github/**/*.md` | Agents, prompts | GitHub configuration |
| `company/_archive/` | All files | Already archived (low priority) |
| `_workspaces/cortex-plan/.archive/` | All files | Workspace-level archives |

---

## 📚 Active Documentation

For current documentation, see:

- **Architecture:** `docs/04-architecture/`
- **Guides:** `docs/07-guides/`
- **API Reference:** `docs/06-api-reference/`
- **MCP Tools:** `docs/11-mcp-tools/`
- **Getting Started:** `docs/03-getting-started/`

---

## 🔄 Restoration

To restore archived documents (if needed):

```bash
# Copy file back to original location
cp docs/archive/<category>/<filename> <original-path>/

# Or move permanently
mv docs/archive/<category>/<filename> <original-path>/
```

**Note:** Check git history for original locations:
```bash
git log --all --full-history -- "*/<filename>"
```

---

## 🎯 Cleanup Compliance

**CORE-002:** ✅ No markdown files outside docs/.github (except README.md)  
**Audit Status:** P3 markdown sprawl resolved  
**Archive Retention:** Indefinite (recovery possible)

---

*Archive maintained by CORTEX Vacuum Agent | See `.github/agents/support/cortex-vacuum.md`*
