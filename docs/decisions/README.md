# CORTEX Decision Log

**Purpose:** Track all significant architectural and design decisions  
**Format:** Architecture Decision Records (ADR)  
**Location:** `docs/decisions/`

---

## How to Use This Log

### Adding a Decision

1. Copy `template.md`
2. Name it: `YYYY-MM-DD-short-descriptive-title.md`
3. Fill in all sections (context, decision, alternatives, consequences)
4. Add to index below
5. Commit with tag: `decision/short-title`

### When to Document

Document decisions when:
- ✅ Choosing between multiple technical approaches
- ✅ Making architecture changes
- ✅ Selecting technologies or frameworks
- ✅ Establishing patterns or conventions
- ✅ Rejecting common approaches (explain why)

Don't document:
- ❌ Trivial implementation details
- ❌ Temporary workarounds
- ❌ Bug fixes (unless they reveal design flaw)

---

## Decision Index

### Active Decisions

#### Phase -1: Architecture Validation

- **[2025-11-06: Custom sql.js with FTS5](2025-11-06-fts5-custom-build.md)**
  - Status: ✅ Accepted, In Progress
  - Tags: #architecture #performance #fts5 #sql.js
  - Summary: Build custom sql.js with FTS5 extension support instead of using standard npm package or LIKE query fallback
  - Impact: +4-6 hours to Phase -1, prevents 20-40 hours future rework

- **[2025-11-06: Folder Structure & Decision Tracking](2025-11-06-folder-structure.md)**
  - Status: ✅ Accepted, In Progress
  - Tags: #organization #structure #governance
  - Summary: Implement hierarchical folder structure with strict placement rules and decision tracking system
  - Impact: 3.5 hours migration, permanent quality improvement

#### Phase 0: Governance (Pending)

- TBD: CI/CD pipeline design
- TBD: Pre-commit hook strategy
- TBD: Test coverage enforcement approach

#### Design Phase (Before Implementation)

- TBD: 4-tier BRAIN architecture rationale
- TBD: SQLite over YAML/JSONL decision
- TBD: React dashboard technology choice
- TBD: Browser-only vs server-side architecture

---

## Superseded Decisions

None yet.

---

## Rejected Decisions

None formally documented yet.

---

## Decision Statistics

- **Total Decisions:** 2
- **Active:** 2
- **Superseded:** 0
- **Rejected:** 0
- **First Decision:** 2025-11-06
- **Last Decision:** 2025-11-06

---

## Decision Timeline

```
2025-11-06
├── Custom sql.js with FTS5 (Phase -1 blocker resolution)
└── Folder Structure & Decision Tracking (governance)

[Future decisions will be added here]
```

---

## Tags

- `#architecture` - System architecture decisions
- `#performance` - Performance-related decisions
- `#tooling` - Tool and framework choices
- `#governance` - Process and quality decisions
- `#fts5` - FTS5 full-text search
- `#sql.js` - sql.js WebAssembly
- `#organization` - Project structure
- `#structure` - Folder/file organization

---

## Related Documents

- **Decision Template:** `template.md`
- **Folder Structure:** `../CORTEX-FOLDER-STRUCTURE.md`
- **Implementation Plan:** `../../cortex-design/IMPLEMENTATION-PLAN-V2.md`
- **Holistic Review:** `../../cortex-design/HOLISTIC-REVIEW-FINDINGS.md`

---

## Maintenance

### Monthly Review
- Review active decisions for evolution
- Update statuses (accepted → superseded)
- Archive old decisions if needed
- Update statistics

### Quarterly Review
- Analyze decision patterns
- Identify recurring themes
- Update decision template if needed
- Review decision tracking process

---

**Last Updated:** 2025-11-06  
**Next Review:** 2025-12-06

