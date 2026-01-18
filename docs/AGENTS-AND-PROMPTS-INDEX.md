# CORTEX Agents & Prompts Index

**Version**: 2.0 (2026-01-18)  
**Purpose**: Complete reference for all agents and prompts, their responsibilities, and inter-dependencies

---

## Overview

CORTEX's intelligent system consists of:
- **7 Specialized Agents** (planning, implementation, review)
- **15+ Prompts** (system-level orchestration and task-specific execution)
- **Single Source of Truth** (cortex-master.yaml + governance.db)

---

## Agent Directory

### Execution Agents

#### 1. cortex-builder.md (Implementation Agent)

**Purpose**: Implement AC-IDs with strict governance enforcement  
**Location**: `.github/agents/cortex-builder.md` (258 lines)  
**Triggers**: `/implement` command, phase start, AC-ID assignment

**Responsibilities**:
- Load governance rules from tier0
- Implement code with TDD (tests first)
- Enforce type hints, docstrings, error handling
- Log audit trail (AC_START, AC_EXECUTE, AC_COMPLETE)
- Create git checkpoints
- Verify phase lock readiness

**Key Features** (v2.0+):
- Governance integration (28 CORE rules)
- Audit remediation mode for PHASE-01 through PHASE-13
- Design-build gap detection (NEW Phase 1.5)
- Phase enforcement map loading
- Compliance reporting

**Governance Rules Enforced**:
- CORE-001 (Incremental execution)
- CORE-008 (TDD)
- CORE-011 (Type hints)
- CORE-012 (Docstrings)
- CORE-013 (Error handling)
- CORE-024 (MCP exposure - NEW)
- CORE-026 (Git checkpoints)
- CORE-027 (Audit trail)
- CORE-028 (Naming convention)

**Data Sources**:
- Reads: `cortex-master.yaml` (phase_tracker)
- Reads: `tier0/governance/core-rules.yaml`
- Writes: `governance.db` (audit events)
- Reads: `phase-XX.yaml` files

**Commands**:
```
/implement          - Next AC-ID
/status             - Phase status + compliance
/phase N            - Show phase + rules
/lock PHASE-XX      - Lock phase
/compliance <ph>    - Compliance report
/audit-trail <ac>   - Audit events
/violations <ph>    - Show violations
```

---

#### 2. cortex-planner.md (Planning Agent)

**Purpose**: Plan next steps based on progress and governance compliance  
**Location**: `.github/agents/cortex-planner.md` (188 lines)  
**Triggers**: `/plan` command, phase completion, progress queries

**Responsibilities**:
- Analyze phase_tracker status
- Query governance compliance
- Recommend next AC-IDs
- Generate progress reports
- Track phase readiness
- Analyze modification impacts
- Track design-build gaps (NEW)

**Key Features** (v2.0+):
- Governance compliance reporting
- Audit trail tracking (AC count, compliance %)
- Modification impact analysis
- Phase readiness multi-stage verification
- Gap inventory & remediation tracking (NEW Phase-22)
- Quarterly gap audit capability (NEW)

**Data Sources**:
- Reads: `cortex-master.yaml` (phase_tracker)
- Reads: `governance.db` (audit logs, compliance)
- Reads: `tier0/governance/phase-enforcement-map.yaml`
- Reads: `phase-XX.yaml` files
- Reads: `cortex-gap-detection.md` findings (NEW)

**Commands**:
```
/plan                    - Implementation plan
/progress                - Completion + compliance
/next                    - Next AC-ID recommendation
/audit-status            - Audit trail status
/governance-report <ph>  - Full governance analysis
/governance-status       - Current compliance
/governance-violations   - Violations by severity
/compliance-trends       - Trending
/phase-readiness <ph>    - Multi-stage verification
/gaps                    - All design-build gaps (NEW)
/gaps <phase>            - Gaps in phase (NEW)
/gap-status <ac>         - Exposure status (NEW)
/gap-remediation         - Recommended remediations (NEW)
```

---

### Review Agents

#### 3. cortex-review-governance.md (Governance Compliance Agent)

**Purpose**: Verify governance compliance and audit trail integrity  
**Location**: `.github/agents/cortex-review-governance.md` (520+ lines)  
**Triggers**: Phase review, audit verification, compliance checking

**Responsibilities**:
- Verify CORE rules compliance
- Audit hash chain integrity
- Check AC-ID audit trail completeness
- Validate phase readiness
- Detect governance violations
- Detect design-build gaps (NEW)
- Generate compliance reports

**Key Features** (v2.0+):
- 11 CORE rule checkers
- Mandatory audit queries
- Hash chain verification
- Phase tracker cross-reference validation
- Quick compliance check script
- Design-build gap detection (NEW with MCP focus)

**Governance Rules Verified**:
- CORE-005 (Path portability)
- CORE-008 (TDD)
- CORE-011 (Type hints)
- CORE-012 (Docstrings)
- CORE-013 (Error handling)
- CORE-026 (Git checkpoints)
- CORE-027 (Audit trail)
- CORE-028 (Naming convention)

**Data Sources**:
- Reads: `cortex-master.yaml` (phase_tracker)
- Reads: `governance.db` (audit logs)
- Reads: `tier0/governance/core-rules.yaml`
- Reads: Python source files (static analysis)

**Commands**:
```
/governance-status           - Current compliance
/governance-violations <ph>  - Violations
/compliance-check            - Full check
/audit-verify <phase>        - Audit verification
/design-build-gaps           - Gap detection (NEW)
```

---

#### 4. cortex-review-brittleness.md (Brittleness Detection Agent)

**Purpose**: Find structural weaknesses and edge cases  
**Location**: `.github/agents/cortex-review-brittleness.md`  
**Triggers**: Code review, pre-release verification

**Responsibilities**:
- Identify structural weaknesses
- Find edge case handling gaps
- Detect error handling issues
- Suggest robustness improvements
- Find integration brittleness

**Data Sources**:
- Reads: Python source code
- Reads: Test suites
- Reads: Error logs

---

#### 5. cortex-review-hallucination.md (Hallucination Risk Detection Agent)

**Purpose**: Identify AI hallucination and reliability risks  
**Location**: `.github/agents/cortex-review-hallucination.md`  
**Triggers**: Pre-release, model update, output verification

**Responsibilities**:
- Identify hallucination risks
- Verify output reliability
- Check prompt injection vulnerabilities
- Find unvalidated assumptions

**Data Sources**:
- Reads: Prompt definitions
- Reads: Model outputs
- Reads: User feedback logs

---

#### 6. cortex-review-debt.md (Technical Debt Detection Agent)

**Purpose**: Identify technical debt and optimization opportunities  
**Location**: `.github/agents/cortex-review-debt.md`  
**Triggers**: Mid-phase review, refactoring planning

**Responsibilities**:
- Identify duplicated code
- Find optimization opportunities
- Detect unused components
- Suggest abstraction improvements
- Track debt metrics

**Data Sources**:
- Reads: Python source code
- Reads: Code metrics
- Reads: Dependency graph

---

#### 7. cortex-review-assumptions.md (Assumption Validation Agent)

**Purpose**: Validate methodology and design assumptions  
**Location**: `.github/agents/cortex-review-assumptions.md`  
**Triggers**: Review start, phase transition, major change

**Responsibilities**:
- Validate methodology assumptions
- Check design assumptions
- Verify prerequisite conditions
- Test assumption dependencies

**Data Sources**:
- Reads: Phase definitions
- Reads: Design documents
- Reads: cortex-brain/ assumptions

---

#### 8. cortex-gap-detection.md (Design-Build Gap Detection - NEW)

**Purpose**: Systematically detect and track design-build gaps  
**Location**: `.github/agents/cortex-gap-detection.md` (286 lines - NEW)  
**Triggers**: Phase completion, AC completion, quarterly audit

**Responsibilities**:
- Detect design-build gaps (components designed/tested but not exposed)
- Track MCP exposure gaps
- Track integration gaps
- Generate gap inventory
- Recommend remediation ACs
- Provide quarterly audit capability

**Key Features**:
- Design-Build Gap pattern definition
- 4-phase detection methodology
- MCP exposure verification
- 6 similar gaps identified
- SQL queries for automated detection
- Quarterly audit checklist

**Data Sources**:
- Reads: `cortex-master.yaml` (AC status)
- Reads: `governance.db` (audit trail)
- Reads: Python source code (@mcp_tool decorators)
- Reads: `phase-XX.yaml` files

**Commands**:
```
/detect-gaps                 - Run gap detection
/gap-inventory               - Show all gaps
/gap-remediation-schedule    - Suggest new phases/ACs
```

---

## Prompt Directory

### System Orchestration Prompts

#### CORTEX.prompt.md (Master Orchestrator)

**Purpose**: Master orchestration and intent routing  
**Location**: `.github/prompts/CORTEX.prompt.md` (46KB)  
**Type**: System-level orchestrator

**Responsibilities**:
- Route user intents to appropriate agents
- Coordinate multi-agent workflows
- Maintain system coherence
- Handle cross-agent conflicts

**Key Components**:
- Intent classification system
- Agent capability matrix
- Workflow definitions
- Escalation procedures

---

### Task-Specific Prompts

#### cortex-builder.prompt.md

**Purpose**: Execution context for cortex-builder agent  
**Location**: `.github/prompts/cortex-builder.prompt.md` (37KB)  
**Type**: Builder execution

**Usage**: Called by cortex-builder.md during implementation

---

#### cortex-orchestrator.prompt.md

**Purpose**: Multi-agent coordination  
**Location**: `.github/prompts/cortex-orchestrator.prompt.md` (40KB)  
**Type**: Coordination

**Usage**: Called by CORTEX.prompt.md for workflow orchestration

---

#### cortex-review-enhanced.prompt.md

**Purpose**: Enhanced review methodology with gap detection  
**Location**: `.github/prompts/cortex-review-enhanced.prompt.md` (30KB, UPDATED v2.1)  
**Type**: Review execution

**Key Features** (v2.1):
- Design-Build Gap Detection section (NEW - 87 lines)
- Pre-review validation gates (0A, 0B, 0C)
- Evidence grading (A/B/C)
- Root cause analysis taxonomy
- 6 critical gap types
- Mandatory gap checks for every finding

**Used By**: cortex-review-enhanced.prompt system calls

---

#### cortex-vacuum.prompt.md

**Purpose**: Comprehensive analysis and cleanup  
**Location**: `.github/prompts/cortex-vacuum.prompt.md` (14KB)  
**Type**: Analysis/cleanup

---

#### cortex-git-commit.prompt.md

**Purpose**: Git workflow automation  
**Location**: `.github/prompts/cortex-git-commit.prompt.md` (14KB)  
**Type**: Git workflow

---

### Reference & Documentation Prompts

- `cortex-builder.md` - Agent definition
- `cortex-planner.md` - Agent definition
- `cortex-review-*.md` - Agent definitions (5 review agents)
- `cortex-gap-detection.md` - Gap detection agent (NEW)

---

## Data Flow Architecture

```
                    ┌──────────────────────┐
                    │ cortex-master.yaml   │
                    │ (SSOT - Phase status)│
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              v                v                v
         ┌────────┐      ┌──────────┐     ┌─────────────┐
         │Builder │      │ Planner  │     │Gap Detection│
         └────┬───┘      └────┬─────┘     └──────┬──────┘
              │               │                  │
              └───────┬───────┴──────┬───────────┘
                      │              │
                      v              v
            ┌──────────────────────────────┐
            │  cortex-brain/               │
            │  - governance.db (audit)     │
            │  - tier0/ (rules)            │
            └──────────────────────────────┘
                      │              │
        ┌─────────────┴──────┬───────┴─────────┐
        │                    │                 │
        v                    v                 v
    ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐
    │Review Agents│  │cortex-review │  │cortex-gap-      │
    │(5 types)    │  │-enhanced.    │  │detection.md     │
    │             │  │prompt        │  │(NEW)            │
    └─────────────┘  └──────────────┘  └─────────────────┘
```

---

## Integration Points Matrix

| From → To | Purpose | Trigger | Data |
|-----------|---------|---------|------|
| Builder → Planner | Progress tracking | AC_COMPLETE | Git commit message |
| Builder → Governance.db | Audit trail | AC implementation | AC_START/EXECUTE/COMPLETE |
| Planner → Master YAML | Roadmap updates | Phase progress | phase_tracker |
| Gap Detection → Planner | Gap inventory | Phase completion | Gap findings |
| Gap Detection → Builder | Exposure checks | Pre-phase-lock | Component status |
| Reviewers → Master YAML | Finding tracking | Review complete | Finding severity |
| Governance → All | Rule enforcement | On-demand | CORE rules |

---

## Cohesion Verification Checklist

### ✅ Single Source of Truth
- [x] All agents read from cortex-master.yaml
- [x] All agents write to governance.db
- [x] No conflicting data sources
- [x] All agents reference same tier0 rules

### ✅ Evidence Grading
- [x] All agents use Grade A/B/C system
- [x] CRITICAL findings require Grade A or B
- [x] Evidence grading documented in cortex-review-enhanced.prompt
- [x] Gap detection includes evidence grading

### ✅ Root Cause Analysis
- [x] All agents categorize findings
- [x] 6-type taxonomy defined
- [x] Gap detection adds DESIGN_BUILD_GAP type
- [x] Root causes traced to CORE rules

### ✅ Governance Enforcement
- [x] All agents reference CORE rules
- [x] Builder enforces during implementation
- [x] Governance agent verifies compliance
- [x] Gap detection verifies exposure

### ✅ Audit Trail
- [x] All events logged to governance.db
- [x] Hash chain integrity maintained
- [x] Audit trail completeness verified
- [x] Retroactive entry detection in place

---

## New Additions (Phase-22 MCP Focus)

### New Agent: cortex-gap-detection.md
- **Purpose**: Systematic design-build gap detection
- **Status**: CREATED (2026-01-18)
- **Integration**: Ready to integrate with cortex-builder, cortex-planner, cortex-review-governance
- **Focus**: MCP exposure, tool integration, configuration files

### Updated Prompt: cortex-review-enhanced.prompt.md
- **Change**: Added design-build gap detection section (87 lines)
- **Status**: UPDATED v2.1 (2026-01-18)
- **Coverage**: Pattern definition, mandatory checks, critical gaps checklist

### Updated Agent: cortex-builder.md
- **Change**: Added Phase 1.5 gap detection checklist (NEW)
- **Status**: UPDATED (2026-01-18)
- **Coverage**: 5-point exposure check before phase lock

### Updated Agent: cortex-planner.md
- **Change**: Added gap tracking to commands and progress report
- **Status**: UPDATED (2026-01-18)
- **Coverage**: Gap inventory, remediation tracking, quarterly audit

### Updated Agent: cortex-review-governance.md
- **Change**: Added design-build gap verification section (100+ lines)
- **Status**: UPDATED (2026-01-18)
- **Coverage**: Gap detection queries, checklist, finding template

### New Document: AGENT-SYSTEM-INTEGRATION.md
- **Purpose**: Ensure all agents work cohesively
- **Status**: CREATED (2026-01-18)
- **Coverage**: Responsibility matrix, communication protocol, success criteria

---

## Testing Agent Cohesion

### Test 1: Data Flow
```bash
# Verify all agents read from SSOT
grep -r "cortex-master.yaml" .github/agents/ .github/prompts/
# Expected: 14+ references
```

### Test 2: Evidence Grading
```bash
# Verify all agents use grading system
grep -r "grade_a\|grade_b\|grade_c" .github/agents/
# Expected: All 7 agents
```

### Test 3: Governance References
```bash
# Verify CORE rule references
grep -r "CORE-0[0-9][0-9]" .github/agents/
# Expected: 25+ rule references
```

### Test 4: Gap Detection
```bash
# Verify gap detection integration
grep -r "cortex-gap-detection\|design_build_gap\|GAP-" .github/
# Expected: 5+ files
```

---

## Commands by Category

### Implementation
- `cortex-builder.md`: /implement, /status, /phase, /lock, /checkpoint, /rollback
- `cortex-planner.md`: /plan, /next

### Analysis & Reporting
- `cortex-planner.md`: /progress, /audit-status, /governance-report, /governance-status, /compliance-trends
- `cortex-review-governance.md`: /governance-violations, /phase-readiness, /governance-query

### Gap Management (NEW)
- `cortex-planner.md`: /gaps, /gaps <phase>, /gap-status, /gap-remediation
- `cortex-gap-detection.md`: /detect-gaps, /gap-inventory, /gap-remediation-schedule

### Governance & Audit
- `cortex-builder.md`: /compliance, /audit-trail, /violations, /enforce-rules
- `cortex-planner.md`: /governance-report, /governance-status, /governance-violations

---

## Version History

### v2.0 (2026-01-17)
- Added MCP gap analysis
- Created Phase-22 remediation plan
- Identified design-build gap pattern

### v2.1 (2026-01-18) - THIS UPDATE
- Created cortex-gap-detection.md agent
- Updated cortex-review-enhanced.prompt with gap detection
- Updated cortex-builder.md with Phase 1.5 gap checks
- Updated cortex-planner.md with gap tracking
- Updated cortex-review-governance.md with gap verification
- Created AGENT-SYSTEM-INTEGRATION.md coherence guide
- Created this comprehensive index

---

## Next Steps

1. ✅ All agents updated to reference gap detection
2. ⏳ Begin Phase-22 AC-MCP-001-01 (MCP SDK integration)
3. ⏳ Run cohesion tests from "Testing Agent Cohesion" section
4. ⏳ Execute quarterly gap audit
5. ⏳ Monitor cortex-master.yaml phase_tracker for Phase-22 progress

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
