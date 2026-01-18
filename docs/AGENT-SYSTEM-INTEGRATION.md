# CORTEX Agent System Integration Guide

**Version**: 2.0 (2026-01-18)
**Status**: COMPREHENSIVE HOLISTIC INTEGRATION

---

## Executive Summary

CORTEX's agent system consists of **7 specialized agents** working with **15+ prompts** to deliver systematic governance-driven development. This document ensures all agents work cohesively to detect, prevent, and remediate issues.

---

## Agent Ecosystem Overview

### Core Agents (Execution)

| Agent | Purpose | Triggers | Outputs |
|-------|---------|----------|---------|
| **cortex-builder.md** | Implements AC-IDs with governance enforcement | Per AC-ID implementation | Code + Audit logs + Tests |
| **cortex-planner.md** | Plans next steps based on progress + governance | Phase transitions | Progress report + Recommendations |

### Review Agents (Analysis)

| Agent | Purpose | Triggers | Outputs |
|-------|---------|----------|---------|
| **cortex-review-governance.md** | Verify governance compliance & audit integrity | Phase completion | Compliance report + Violations |
| **cortex-review-brittleness.md** | Find structural weaknesses & edge cases | Code review stage | Brittleness findings |
| **cortex-review-hallucination.md** | Identify AI hallucination risks | Pre-release stage | Hallucination risks |
| **cortex-review-assumptions.md** | Validate methodology assumptions | Review start | Assumption verification report |
| **cortex-review-debt.md** | Identify technical debt & duplication | Mid-phase review | Debt analysis + Refactoring candidates |

### NEW: cortex-gap-detection.md (Integration Layer)

| Agent | Purpose | Triggers | Outputs |
|-------|---------|----------|---------|
| **cortex-gap-detection.md** | Detect design-build gaps systematically | Per-phase review | Gap inventory + Remediation ACs |

### Master Prompt (Orchestration)

| Prompt | Purpose | Usage |
|--------|---------|-------|
| **CORTEX.prompt.md** | Master orchestrator + intent router | System-wide coordination |

---

## Data & Control Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   cortex-master.yaml (SSOT)                 │
│                  Phase Tracker + AC Status                  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         v           v           v
    ┌────────┐  ┌─────────┐  ┌──────────────┐
    │Builder │  │ Planner │  │Gap Detection │
    └───┬────┘  └────┬────┘  └──────┬───────┘
        │            │               │
        └────┬───────┴───────┬───────┘
             │               │
             v               v
    ┌────────────────────────────────┐
    │  cortex-brain/ (Governance DB) │
    │  - governance.db (audit trail) │
    │  - tier0/governance/ (rules)   │
    └────────────────────────────────┘
             │               │
             └───┬───────┬───┘
                 │       │
    ┌────────────v─┐  ┌──v──────────────┐
    │Review Agents │  │cortex-review-   │
    │(5 agents)    │  │enhanced.prompt  │
    └──────────────┘  └─────────────────┘
```

---

## Integration Points

### Integration Point 1: Builder ↔ Governance

**cortex-builder.md requires cortex-brain/tier0/governance/**

```yaml
flow:
  before_implementing_ac:
    1. Load phase enforcement map
    2. Check applicable CORE rules
    3. Log AC_START to audit trail
    4. Display pre-start summary with rules
  
  during_implementation:
    1. Enforce CORE-011 (type hints)
    2. Enforce CORE-012 (docstrings)
    3. Enforce CORE-008 (TDD)
    4. Log AC_EXECUTE during tests
  
  after_completion:
    1. Verify all tests pass
    2. Log AC_COMPLETE to audit trail
    3. Create git checkpoint
    4. Move to next AC or phase
```

**Check**: cortex-builder.md lines 1-50 reference tier0 governance loading

---

### Integration Point 2: Builder ↔ Planner

**cortex-planner.md reads cortex-master.yaml written by cortex-builder.md**

```yaml
flow:
  planner_queries:
    - What's current phase status?
      source: cortex-master.yaml phase_tracker
    
    - What's governance compliance?
      source: governance.db audit logs
    
    - What's the next AC-ID to implement?
      source: phase YAML files + dependencies
    
    - Are any phases blocked by governance violations?
      source: cortex-review-governance findings
```

**Check**: cortex-planner.md `/progress` command reads phase_tracker

---

### Integration Point 3: Gap Detection ↔ All Agents

**cortex-gap-detection.md identifies design-build gaps that cortex-review-enhanced.prompt.md should find**

```yaml
gap_detection_flow:
  phase_1_design_check:
    - Look for component in phase YAML
    - Check AC-IDs marked COMPLETED
    - Verify tests pass 100%
  
  phase_2_implementation_check:
    - Is code implemented (not stubbed)?
    - Does it match design?
    - Any blocking TODOs?
  
  phase_3_exposure_check:
    - Is @mcp_tool decorator present? (if tool-eligible)
    - Is component exported in __all__?
    - Is it registered in MCPServer?
  
  phase_4_governance_check:
    - Is audit trail complete (AC_START/EXECUTE/COMPLETE)?
    - Are CORE rules enforced?
    - Is compliance validated?
  
  output: GAP FINDINGS → fed to cortex-review-enhanced.prompt
```

**Check**: Both files reference same components and AC-IDs

---

### Integration Point 4: Review Agents ↔ cortex-review-enhanced.prompt

**cortex-review-enhanced.prompt orchestrates all review agents**

```yaml
review_orchestration:
  pre_review:
    - Run cortex-review-assumptions (Gate 0C)
    - Run cortex-gap-detection (NEW)
    - Validate data freshness (Gate 0A)
    - Filter test fixtures (Gate 0B)
  
  core_review:
    - cortex-review-governance (audit trail)
    - cortex-review-brittleness (edge cases)
    - cortex-review-hallucination (AI risks)
    - cortex-review-debt (refactoring)
  
  post_review:
    - Consolidate findings
    - Grade evidence (A/B/C)
    - Perform root cause analysis
    - Generate remediation ACs
```

**Check**: cortex-review-enhanced.prompt includes section for each review agent

---

## Cohesion Patterns

### Pattern 1: Evidence Grading

**All agents use same evidence grading system** (from cortex-review-enhanced.prompt.md):

```yaml
evidence_grades:
  grade_a: "95-100% confidence - Direct, reproducible evidence"
  grade_b: "80-95% confidence - Corroborated by multiple sources"
  grade_c: "60-80% confidence - Indirect evidence, needs verification"
  grade_d: "❌ NOT ALLOWED - Speculation only"

rule: "CRITICAL findings MUST have Grade A or B evidence"
```

**How agents use this**:
- cortex-review-brittleness finds issue → grades evidence
- cortex-review-governance checks audit trail → grades confidence
- cortex-gap-detection identifies gap → assigns grade
- cortex-review-enhanced.prompt validates all grades

---

### Pattern 2: Root Cause Analysis

**All agents explain root cause** (from cortex-review-enhanced.prompt.md):

```yaml
root_cause_types:
  1. IMPLEMENTATION_FLAW: "Code logic is incorrect"
  2. INTEGRATION_ISSUE: "Components don't work together"
  3. TEST_ARTIFACT: "Test data corrupts analysis"
  4. METHODOLOGY_ERROR: "Review checked at wrong time"
  5. ENVIRONMENT_PROBLEM: "System misconfigured"
  6. DESIGN_BUILD_GAP: "NEW - Designed but not exposed/integrated"
```

**How agents use this**:
- cortex-builder catches IMPLEMENTATION_FLAW during coding
- cortex-gap-detection catches DESIGN_BUILD_GAP during exposure check
- cortex-review-brittleness finds INTEGRATION_ISSUE
- cortex-review-enhanced validates root cause

---

### Pattern 3: Governance Enforcement

**All agents verify CORE rules** (from cortex-brain/tier0/governance/core-rules.yaml):

```yaml
enforced_by:
  CORE-001: "cortex-builder (incremental execution)"
  CORE-008: "cortex-builder (TDD enforcement)"
  CORE-011: "cortex-builder (type hints)"
  CORE-012: "cortex-builder (docstrings)"
  CORE-024: "cortex-gap-detection (NEW - @mcp_tool Required)"
  CORE-027: "cortex-builder + cortex-review-governance (audit trail)"
```

---

### Pattern 4: Audit Trail

**All agents log to governance.db**:

```yaml
logging_pattern:
  cortex-builder:
    events: AC_START, AC_EXECUTE, AC_COMPLETE
    
  cortex-gap-detection:
    events: GAP_DETECTED, GAP_REMEDIATION_SCHEDULED
    
  cortex-review-agents:
    events: REVIEW_STARTED, REVIEW_FINDING, REVIEW_COMPLETE
```

---

## Agent Responsibility Matrix

| Responsibility | Builder | Planner | Gap Detection | Governance | Brittleness | Hallucination | Debt | Assumptions |
|----------------|---------|---------|---------------|------------|------------|---------------|------|------------|
| Implement code | ✅ | | | | | | | |
| Enforce CORE rules | ✅ | | | ✅ | | | | |
| Log audit trail | ✅ | | | ✅ | | | | |
| Plan next steps | | ✅ | ✅ | | | | | |
| Detect gaps | | | ✅ | | | | | |
| Find brittleness | | | | | ✅ | | | |
| Find hallucination | | | | | | ✅ | | |
| Find debt | | | | | | | ✅ | |
| Verify assumptions | | | | | | | | ✅ |

---

## Communication Protocol

### Agent-to-Agent Messages

**Builder → Planner**: "AC-001-01 completed, moving to AC-001-02"
- Format: Git commit message with AC-ID
- Triggers: Planner updates progress report

**Builder → Gap Detection**: "Component X implemented in src/tools/"
- Format: File path + AC-ID reference
- Triggers: Gap detection checks exposure

**Gap Detection → Reviewers**: "Design-build gap found: MCP server not spec-compliant"
- Format: Finding with evidence grade + root cause
- Triggers: Review agents investigate

**Reviewers → Planner**: "5 findings, recommend Phase-22 for remediation"
- Format: Finding list + suggested new phase
- Triggers: Planner creates remediation schedule

---

## Success Criteria for Cohesion

### Criterion 1: No Duplicate Checking

✅ **Each aspect checked by exactly ONE agent**:
- Implementation by cortex-builder
- Governance compliance by cortex-review-governance
- Brittleness by cortex-review-brittleness
- Debt by cortex-review-debt
- Design-build gaps by cortex-gap-detection

### Criterion 2: All Findings Have Root Cause

✅ **Every finding includes**:
- Evidence grade (A/B/C)
- Root cause type (from 6-type taxonomy)
- Actionable remediation
- AC-ID reference

### Criterion 3: All Agents Use Same Data

✅ **Single source of truth**:
- cortex-master.yaml for phase status
- governance.db for audit trail
- tier0/governance/ for rules
- phase-XX.yaml for AC definitions

### Criterion 4: Governance Enforced Everywhere

✅ **CORE rules enforced by**:
- cortex-builder during coding
- cortex-gap-detection during exposure check
- cortex-review-governance during audit
- cortex-review-brittleness during analysis

### Criterion 5: New Gaps Trigger New Phases

✅ **Gap flow**:
- Gap detected → Create AC-MCP-XXX-XX
- AC created → Add to cortex-master.yaml
- Phase created → phase-22-mcp-protocol-compliance.yaml
- Ready for cortex-builder to implement

---

## Testing Agent Cohesion

### Test 1: Data Flow

```bash
# Verify all agents read from same SSOT
grep -r "cortex-master.yaml" .github/agents/ .github/prompts/
grep -r "governance.db" .github/agents/ .github/prompts/
```

**Expected**: 14+ files reference SSOT files

### Test 2: Evidence Grading

```bash
# Verify all agents use same grading system
grep -r "grade_a\|grade_b\|grade_c\|evidence" .github/agents/
```

**Expected**: All 7 agents reference evidence grades

### Test 3: Root Cause

```bash
# Verify all agents use root cause taxonomy
grep -r "IMPLEMENTATION_FLAW\|INTEGRATION_ISSUE\|TEST_ARTIFACT" .github/agents/
```

**Expected**: All agents reference root cause types

### Test 4: Governance

```bash
# Verify CORE rules referenced
grep -r "CORE-0[0-9][0-9]" .github/agents/
```

**Expected**: 25+ CORE rule references across agents

---

## MCP Integration Checklist (New Focus)

- [ ] cortex-builder enforces @mcp_tool requirement (CORE-024)
- [ ] cortex-gap-detection checks MCP exposure (new)
- [ ] cortex-review-enhanced includes MCP gap check (new)
- [ ] cortex-review-governance verifies MCP audit logging
- [ ] cortex-planner tracks MCP readiness score
- [ ] Phase-22 created for MCP protocol compliance remediation

---

## Document Updates (This Refactoring)

| Document | Change | Impact |
|----------|--------|--------|
| cortex-review-enhanced.prompt.md | Added design-build gap section | Review agents now detect 6th gap type |
| cortex-gap-detection.md | NEW agent | Systematic gap detection + remediation |
| This document | NEW integration guide | Ensures all agents work cohesively |
| cortex-master.yaml | Phase-22 added | MCP remediation scheduled |

---

## Next Steps

1. **Validate agent cohesion** (run tests from "Testing Agent Cohesion" section)
2. **Deploy cortex-gap-detection.md** to production review process
3. **Implement Phase-22** per cortex-master.yaml roadmap
4. **Quarterly gap audits** using gap detection script
5. **Update all agents** to reference this integration guide

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
