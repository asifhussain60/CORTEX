# KDS Deprecation List (Candidates for Archive/Delete)

Purpose: Track legacy KDS artifacts that should be archived or removed as we migrate to CORTEX. Use scripts/archive-kds.ps1 to safely move items into the dated _archive folder; do not permanently delete outside of Git until Phase -2 success criteria are met.

Status legend:
- KEEP = still needed for migration reference
- ARCHIVE = move to `_archive/20251106-kds-deprecated/`
- REMOVE = safe to delete (generated or redundant)

## Top-level items

| Path | Status | Rationale |
|------|--------|-----------|
| kds-dashboard.html | ARCHIVE | KDS UI replaced by future CORTEX dashboard |
| dashboard/ | ARCHIVE | Old HTML dashboard docs |
| dashboard-wpf/ | ARCHIVE | KDS-specific WPF app |
| update-kds-story.ps1 | ARCHIVE | KDS-only helper |
| tests/*.ps1 (dashboard*) | ARCHIVE | Tightly coupled to KDS UI |
| scripts/open-dashboard.ps1 | ARCHIVE | KDS dashboard launcher |
| scripts/launch-dashboard.ps1 | ARCHIVE | KDS dashboard launcher |
| scripts/dashboard-api-server.ps1 | ARCHIVE | KDS API helper |
| scripts/validate-kds-references.ps1 | ARCHIVE | Historical validation script |
| tests/KDS-*.md | ARCHIVE | KDS testing prompts |
| prompts/user/kds.md | ARCHIVE | Deprecated entry point (too large) |
| sessions/ | REMOVE | Runtime artifacts, not needed in Git |
| reports/ | REMOVE | Generated data, re-create as needed |
| backups/ | REMOVE | Redundant; Git is source of truth |
| _archive/ | ARCHIVE | Keep, but nest KDS-specific subfolder |

Notes:
- Many files across `scripts/`, `tests/`, and `reports/` reference `KDS/prompts/user/kds.md`. After archiving, remaining live code must not reference it (enforced by the Sharpener and CI grep checks).
- Anything not explicitly listed here remains under review; default action is KEEP until verified.

## Follow-ups
- After archival, run a repo-wide search for `KDS/prompts/user/kds.md` and update references to `CORTEX/cortex.md` where applicable.
- Add a short notice at the top of the old KDS entry point directing users to the new CORTEX entry point (optional if the file is archived immediately).
