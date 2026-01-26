# Implementation Reports
**Purpose:** Implementation work, AC-IDs, and execution tracking  
**Authority:** AC-REPORTS-CONSOLIDATION-001

## Report Types
- AC-ID execution status and results
- Feature implementation documentation
- Bug fix verification and testing
- Refactoring completion reports
- Technical debt tracking

## Naming Pattern
`{ac-id|category}-{description}-{date}.{md|yaml}`

**Examples:**
- `ac-doc-sync-001-planning-orch-wiring.md`
- `ac-planning-consolidated-001-complete.md`
- `feature-implementation-orch-bootstrap.md`
- `bug-fix-race-condition-state-manager.md`
- `refactoring-knowledge-repository-2026-01-25.md`

## Format Guide
- Use **Markdown (.md)** for implementation narratives and results
- Use **YAML (.yaml)** for structured tracking and checklists

## AC-ID Tracking
All AC-IDs should be documented with:
- Status (DRAFT, IN_PROGRESS, COMPLETE, BLOCKED)
- Authority and date
- Key deliverables
- Test results
- Git commit references

---

See `reports/README.md` for complete guidelines.
