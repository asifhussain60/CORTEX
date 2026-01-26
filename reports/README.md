# CORTEX Reports Directory
**Authority:** AC-REPORTS-CONSOLIDATION-001 | **Version:** 1.0 | **Updated:** 2026-01-25

---

## 📋 Overview

This directory serves as the **canonical location** for all operational reports, analyses, and documentation generated during CORTEX development and operations.

**Key Policy:**
- ✅ **User-facing documentation** lives in `docs/` (guides, tutorials, API reference)
- ✅ **Operational reports** live in `reports/` (analysis, metrics, tracking)
- ✅ **Structured data** uses YAML format (queryable, version-controlled)
- ✅ **Narrative documents** use markdown format (readable, searchable)

---

## 📁 Directory Structure

```
reports/
├── analysis/                 # Code analysis, research, investigations
│   ├── architecture-*
│   ├── code-quality-*
│   ├── dependency-*
│   └── performance-*
│
├── governance/              # Governance, compliance, rule enforcement
│   ├── core-rule-*
│   ├── compliance-*
│   ├── audit-*
│   └── violation-*
│
├── orchestrators/           # Orchestrator-specific reports
│   ├── planning-*
│   ├── tdd-*
│   ├── refactoring-*
│   ├── wiring-*
│   └── health-*
│
├── phase-tracking/          # Phase progress, milestones, deliverables
│   ├── phase-*.md
│   ├── milestone-*.md
│   ├── deliverable-*.md
│   └── completion-*.yaml
│
├── operations/              # Operational reports (deployments, incidents)
│   ├── deployment-*
│   ├── incident-*
│   ├── health-check-*
│   └── performance-*
│
├── implementation/          # Implementation work, AC-IDs, execution
│   ├── ac-*.md
│   ├── feature-implementation-*
│   ├── bug-fix-*
│   └── refactoring-*
│
└── README.md               # This file
```

---

## 🏷️ Naming Conventions

### Kebab-Case Format
All files follow **kebab-case** (lowercase, hyphens, no spaces):

**GOOD:**
- `planning-orchestrator-consolidation-2026-01-25.md`
- `core-rule-enforcement-audit.yaml`
- `phase-tracking-completion.md`

**BAD (DO NOT USE):**
- `Planning Orchestrator Consolidation Report.md` (spaces, capitalization)
- `Planning_Orchestrator_Consolidation.md` (underscores)
- `planningOrchestratorConsolidation.md` (camelCase)

### Meaningful Short Names
File names should be:
- **Specific:** Describe the content clearly
- **Concise:** Use abbreviations where appropriate
- **Dated:** Include dates for time-series reports (YYYY-MM-DD format)

**Examples:**
- `planning-orch-v2-complete-2026-01-25.md` (clear, specific, dated)
- `tdd-orchestrator-health-check-daily.md` (role + metric + frequency)
- `phase-15-deliverables.md` (clear milestone)
- `core-030-enforcement-results.md` (rule + topic)

---

## 📂 Subfolder Usage Guide

### `analysis/`
**Purpose:** Code analysis, research findings, investigations

**Types of Reports:**
- Architecture analysis and reviews
- Code quality metrics and assessments
- Dependency mapping and analysis
- Performance profiling and analysis
- Risk assessment and mitigation

**Example Files:**
- `architecture-orchestrator-wiring-2026-01-25.md`
- `code-quality-metrics-planning-orch.md`
- `dependency-graph-core-modules.yaml`
- `performance-baseline-cortex-6.0.md`

---

### `governance/`
**Purpose:** Governance, compliance, and rule enforcement

**Types of Reports:**
- CORE rule enforcement results
- Governance compliance status
- Audit trails and logs
- Violation tracking and remediation
- Policy implementation status

**Example Files:**
- `core-030-implementation-truth-audit.md`
- `core-035-duplicate-detection-results.md`
- `compliance-tier0-enforcement.yaml`
- `ac-permanent-fix-status.md`
- `violation-tracking-q1-2026.yaml`

---

### `orchestrators/`
**Purpose:** Orchestrator-specific reports and metrics

**Types of Reports:**
- Orchestrator health and status
- Registry wiring validation
- MCP tool integration status
- Orchestrator performance metrics
- Feature implementation tracking per orchestrator

**Example Files:**
- `planning-orchestrator-v2-status.md`
- `tdd-orchestrator-test-coverage.yaml`
- `orchestrator-registry-wiring-status.md`
- `orchestrator-health-check-daily.yaml`
- `mcp-tools-availability-matrix.md`

---

### `phase-tracking/`
**Purpose:** Phase progress, milestones, and deliverables

**Types of Reports:**
- Phase completion status
- Milestone tracking and ETA
- Deliverable checklists
- Phase-to-phase transition reports
- Acceptance criteria validation

**Example Files:**
- `phase-15-deliverables.md`
- `phase-15-completion-checklist.yaml`
- `milestone-cortex-6-release.md`
- `deliverable-planning-orchestrator-v2.yaml`

---

### `operations/`
**Purpose:** Operational and deployment reports

**Types of Reports:**
- Deployment logs and status
- Incident response reports
- Health check results
- Performance and monitoring data
- Operational SLA tracking

**Example Files:**
- `deployment-cortex-6.0-prod-2026-01-25.md`
- `incident-registry-database-failure-2026-01-25.md`
- `health-check-daily-2026-01-25.yaml`
- `performance-monitoring-weekly-2026-01-25.md`

---

### `implementation/`
**Purpose:** Implementation work, AC-IDs, and execution tracking

**Types of Reports:**
- AC-ID execution status and results
- Feature implementation documentation
- Bug fix verification and testing
- Refactoring completion reports
- Technical debt tracking

**Example Files:**
- `ac-doc-sync-001-planning-orch-wiring.md`
- `ac-planning-consolidated-001-complete.md`
- `feature-implementation-orch-bootstrap.md`
- `bug-fix-race-condition-state-manager.md`
- `refactoring-knowledge-repository-2026-01-25.md`

---

## 📊 File Format Guidelines

### Markdown (.md)
**Use for:** Narrative reports, analyses, documentation

**When to use:**
- Analysis and research findings
- Phase progress reports
- Implementation status and completion reports
- Operational summaries
- Human-readable documentation

**Structure:**
```markdown
# Report Title
**Date:** YYYY-MM-DD | **Authority:** AC-ID | **Status:** STATUS

## Executive Summary
Brief overview of findings/status.

## Key Findings
1. Finding 1
2. Finding 2

## Details
Detailed information and context.

## Recommendations
What should be done next.

## References
Links to related reports, code, etc.
```

### YAML (.yaml)
**Use for:** Structured data, metrics, queryable information

**When to use:**
- Status tracking and metrics
- Compliance checklists
- Configuration snapshots
- Data-driven reports
- System state documentation

**Structure:**
```yaml
# Report Name
date: "2026-01-25"
authority: "AC-ID"
status: "COMPLETE"

metrics:
  key_metric_1: value
  key_metric_2: value

items:
  - name: "Item 1"
    status: "COMPLETE"
    notes: "Details"
  - name: "Item 2"
    status: "IN_PROGRESS"
    notes: "Details"
```

---

## ✅ Quality Standards

### Before Committing a Report

- [ ] **Naming:** Follows kebab-case convention
- [ ] **Clarity:** Title clearly describes content
- [ ] **Authority:** AC-ID or CORE rule referenced
- [ ] **Dating:** Current date included (if time-sensitive)
- [ ] **Structure:** Markdown uses standard structure or YAML is valid
- [ ] **Context:** Links to related files, code, or documentation
- [ ] **Completeness:** All key sections included (summary, findings, next steps)
- [ ] **Accuracy:** Facts verified against implementation (CORE-030)

### File Size Guidelines

- **Small reports:** < 2 KB (single metric, quick update)
- **Medium reports:** 2-50 KB (analysis, phase tracking)
- **Large reports:** 50-500 KB (comprehensive analysis, audit)
- **Very large reports:** > 500 KB (break into smaller files, consider database)

---

## 🔗 Integration with Other Directories

### Relationship to `docs/`
- **docs/** = User-facing, long-term, educational
- **reports/** = Internal, operational, time-sensitive
- ✅ Reports can reference docs for background
- ❌ Reports should not duplicate docs content
- ❌ Docs should not contain operational reports

### Relationship to `_workspaces/roadmap/`
- **_workspaces/roadmap/phases/*.yaml** = Master plan, specifications
- **reports/phase-tracking/** = Execution status, milestone tracking
- ✅ Reports track progress against roadmap specs
- ✅ Roadmap specs define what reports should track
- ❌ Reports should not redefine phase requirements

### Relationship to `cortex-registry/`
- **cortex-registry/** = Live configuration, SSOT for wiring
- **reports/orchestrators/** = Analysis of registry state
- ✅ Orchestrator reports verify registry consistency
- ✅ Registry is source of truth, reports are analysis

---

## 🚀 Getting Started

### Creating a New Report

1. **Choose Category:** Which subfolder? (analysis, governance, orchestrators, etc.)
2. **Choose Format:** Markdown (.md) or YAML (.yaml)?
3. **Follow Naming:** `subcategory-description-date.md`
4. **Add Header:** Authority, date, status
5. **Write Content:** Follow structure for your format
6. **Commit:** Add to git with clear message

### Example Workflow

```bash
# Create a new analysis report
cd reports/analysis
cat > architecture-new-module-2026-01-25.md << 'EOF'
# Architecture Analysis: New Module Design
**Date:** 2026-01-25 | **Authority:** AC-ARCH-001 | **Status:** DRAFT

## Executive Summary
Analysis of proposed module architecture.

## Key Findings
1. Module design aligns with CORTEX principles
2. Integration points identified
3. Testing strategy defined

## Recommendations
1. Proceed with implementation
2. Include in Phase 16
3. Review with RefactoringOrchestrator

EOF

# Commit the report
git add architecture-new-module-2026-01-25.md
git commit -m "analysis: Architecture review for new module"
```

---

## 📋 Current Migration Status

**Reports to Migrate:** 5 high-priority reports from various locations

| Report | Current Location | Target Location | Status |
|--------|------------------|-----------------|--------|
| Planning Orchestrator Consolidation | `_workspaces/reports/` | `reports/orchestrators/` | ⏳ TO DO |
| Documentation Sync Report | `_workspaces/reports/` | `reports/implementation/` | ⏳ TO DO |
| Phase Tracking | `_workspaces/roadmap/reports/` | `reports/phase-tracking/` | ⏳ TO DO |
| Analysis Reports | Various | `reports/analysis/` | ⏳ TO DO |
| Governance Audits | Various | `reports/governance/` | ⏳ TO DO |

---

## 🔐 Governance

**Authority:** AC-REPORTS-CONSOLIDATION-001  
**CORE Rules Applied:**
- CORE-029: Response header enforcement
- CORE-035: Single canonical implementation
- File placement policy (no .md files outside canonical locations)

**Enforcement:**
- Pre-commit hooks will validate report naming and placement
- DocumentationOrchestrator will track report directory
- Total Recall Agent can discover reports via this README

---

## 📞 Support

Questions about report placement or naming?
1. Check this README's directory structure
2. Review the naming conventions section
3. Look at similar reports as examples
4. Refer to the AC-ID authority for specific reports

---

**Last Updated:** 2026-01-25 | **Next Review:** 2026-02-25
