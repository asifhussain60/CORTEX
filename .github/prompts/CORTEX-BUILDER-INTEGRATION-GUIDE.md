# Issue Remediation Pattern - Integration Guide

## How This Pattern Fits Into CORTEX Workflow

### 1. Issue Discovery → Phase Planning

```
User finds issue in codebase
      ↓
Issue-report-NN.yaml created in .github/roadmap/issues/
      ↓
Run holistic review (cortex-builder-issue-remediation-pattern.md)
      ↓
Decision made: REMEDIATION | ACCEPT-KNOWN | DEFER | ARCHITECTURE-FIX
      ↓
IF REMEDIATION:
  ├─ Create AC-REM-XXX-XX IDs
  ├─ Add to cortex-master.yaml phase_tracker
  ├─ Create phase YAML with ACs
  └─ Follow standard implementation workflow
      ↓
Issue resolved → Rename issue-report-NN-done.yaml
      ↓
Update cortex-master.yaml resolved_issues tracking
```

### 2. File Structure

```
.github/
├── prompts/
│   ├── cortex-builder.prompt.md                      (MAIN - updated)
│   ├── cortex-builder-issue-remediation-pattern.md   (NEW - complete pattern)
│   ├── CORTEX-BUILDER-ENHANCEMENT-SUMMARY.md         (NEW - this file)
│   └── CORTEX-BUILDER-INTEGRATION-GUIDE.md           (NEW - you're reading this)
│
├── roadmap/
│   ├── cortex-master.yaml (updated with resolved_issues section)
│   ├── issues/
│   │   ├── issue-report-01.yaml
│   │   ├── issue-report-02.yaml
│   │   ├── issue-report-01-done.yaml  (renamed when closed)
│   │   └── issue-report-02-done.yaml  (renamed when closed)
│   │
│   └── phases/
│       ├── phase-13.yaml  (existing)
│       ├── phase-issue-001-remediation.yaml  (NEW if needed)
│       └── phase-issue-002-remediation.yaml  (NEW if needed)
│
├── agents/
│   ├── cortex-builder.md                (existing)
│   ├── cortex-review-governance.md      (existing)
│   └── cortex-issue-resolver-XX.md      (NEW if complex remediation)
```

### 3. YAML Integration Points

#### 3.1 In cortex-master.yaml

**Add new section** (if not present):

```yaml
# NEW SECTION: Issue Resolution Tracking
issue_resolutions:
  status: "ACTIVE - 4 issues discovered, 2 under remediation"
  
  resolved_issues:
    - issue_id: "ISSUE-001"
      title: "AST Scanning Integration"
      source_file: "issue-report-01.yaml"
      severity: "CRITICAL"
      remediation_phase: "PHASE-ISSUE-001-REMEDIATION"
      remediation_acs: ["AC-REM-001-01", "AC-REM-001-02", "AC-REM-001-03"]
      status: "RESOLVED"
      resolution_date: "2026-01-16"
      verification:
        tests_passing: 12
        audit_entries: 9
        hash_chain_valid: true
  
  pending_issues:
    - issue_id: "ISSUE-002"
      title: "Domain Brain Architecture"
      source_file: "issue-report-02.yaml"
      severity: "HIGH"
      status: "UNDER_REVIEW"
      decision: "DEFERRED to PHASE-17-DOMAIN-BRAIN"
      reason: "Aligns with strategic domain knowledge architecture"
    
    - issue_id: "ISSUE-003"
      title: "Response Header Undocumented"
      source_file: "issue-report-03.yaml"
      severity: "MEDIUM"
      status: "REMEDIATION_PLANNED"
      remediation_phase: "PHASE-DOC-REMEDIATION"
      remediation_acs: ["AC-DOC-001-01", "AC-DOC-001-02"]
  
  deferred_issues:
    - issue_id: "ISSUE-004"
      title: "Performance Optimization"
      source_file: "issue-report-04.yaml"
      severity: "LOW"
      target_phase: "PHASE-20-OPTIMIZATION"
      reason: "Not blocking production; deferred to optimization phase"

  issue_review_stats:
    total_discovered: 4
    total_resolved: 1
    total_under_remediation: 1
    total_deferred: 1
    total_accept_as_known: 1
    holistic_review_completion: "75% (3/4 issues reviewed)"
```

#### 3.2 Phase YAML Structure (for remediation)

**Create**: `.github/roadmap/phases/phase-issue-001-remediation.yaml`

```yaml
phase:
  id: "PHASE-ISSUE-001-REMEDIATION"
  title: "AST Scanning Integration into Intent Router"
  source_issue: "issue-report-01.yaml - CRITICAL-ISSUE-1"
  priority: "P0-CRITICAL"
  type: "REMEDIATION"
  
  # Link back to issue
  resolution_context:
    issue_id: "ISSUE-001"
    finding: "Intent Router bypasses AST scanning, no deep comprehension"
    verification_method: "Holistic review against cortex-master.yaml + live codebase"
    audit_evidence: "governance.db queries showing missing AST operations"
  
  acceptance_criteria:
    - ac_id: "AC-REM-001-01"
      description: "[Full AC description from remediation pattern]"
      # ... rest of AC structure
    - ac_id: "AC-REM-001-02"
      # ...
    - ac_id: "AC-REM-001-03"
      # ...
  
  # Standard phase fields
  status: "COMPLETED"
  locked: true
  requires: "PHASE-07-INTENT-ROUTER"
  completed_at: "2026-01-16T14:30:00Z"
  
  audit_verification:
    verified: true
    entry_count: 9  # 3 ACs × 3 entries each
    hash_chain_valid: true
    verified_at: "2026-01-16T14:30:00Z"
  
  git_checkpoint: "[commit-hash]"
```

### 4. Issue File Naming Convention

#### Active Issue
```
.github/roadmap/issues/issue-report-01.yaml
```

#### Resolved Issue
```
.github/roadmap/issues/issue-report-01-done.yaml
```

**Why**: 
- Clear visual indicator of completion
- Easy to distinguish active vs resolved
- Preserves history without clutter
- Enables automation (e.g., `ls issues/*-done.yaml` to list all resolved)

### 5. Decision Reference Matrix

| Issue Finding | Verification | Decision | Action | Tracking |
|---|---|---|---|---|
| "Feature X not implemented" | Find in cortex-master.yaml architecture_decisions | Already planned | DEFER to PHASE-XX | Cross-reference only |
| "Rule not enforced" | Check governance.db test audit logs | Implemented differently | ACCEPT-KNOWN | Document why |
| "AST scanning not used" | Grep source, check tests, audit trail | Real gap blocking core flow | REMEDIATION | Create AC-REM-XXX-XX |
| "Performance slow" | Benchmark real vs claimed | Low-priority | DEFER | Track in PHASE-20+ |
| "Architecture flaw" | Deep analysis against design principles | Fundamental issue | ARCHITECTURE-FIX | PHASE-ARCHITECTURE-FIX |

### 6. Agent Integration

#### When to Create New Agent

| Condition | Agent Action |
|---|---|
| Single issue, simple fix | No agent needed (cortex-builder handles) |
| Issue spans 2-3 phases | No agent needed (phase coordination) |
| Issue span 3+ phases + new domain | Create cortex-issue-domain-XX.md |
| Issue requires specialized expertise | Create cortex-expert-domain.md |
| Multiple related issues, complex interaction | Create cortex-issue-coordinator.md |

#### Agent Template

```yaml
name: .github/agents/cortex-issue-resolver-ast.md
meta:
  domain: "AST Scanning & Deep Analysis"
  issues_handled: ["ISSUE-001"]
  scope: ["Intent Router", "AST Intelligence", "Governance"]

responsibilities:
  - Review AST scanning issue holistically
  - Plan AC-REM-001-01/02/03 ACs
  - Execute implementation per phase workflow
  - Verify audit trail and closure

integration:
  - Coordinates with cortex-builder for phase workflow
  - Reports to cortex-planner for tracking
  - Closes when issue-report-01-done.yaml renamed
```

### 7. Workflow Example: Issue-001 Resolution

**Week 1: Review & Planning**
```
1. Holistic review of issue-report-01.yaml
2. Decision: REMEDIATION (AST scanning real gap)
3. Create PHASE-ISSUE-001-REMEDIATION.yaml with 3 ACs
4. Add to cortex-master.yaml phase_tracker
5. Create 3 test files (RED state)
```

**Week 2: Implementation**
```
1. Implement ASTIntelligenceEngine integration (GREEN tests)
2. Audit logging: AC_START → AC_EXECUTE → AC_COMPLETE
3. Hash chain verification
4. All 12 tests passing (3 ACs × 4 tests each)
```

**Week 3: Closure**
```
1. Verify phase complete: AC-REM-001-01, 02, 03 all COMPLETED
2. Rename issue-report-01.yaml → issue-report-01-done.yaml
3. Update cortex-master.yaml:
   - Move from pending_issues to resolved_issues
   - Add resolution metadata
4. Reference in phase completion summary
```

### 8. Automation Opportunities

**Scripts that could automate this pattern:**

```bash
# Find unresolved issues
find .github/roadmap/issues -name "issue-report-*.yaml" ! -name "*-done.yaml"

# Count resolved vs pending
ls .github/roadmap/issues/*-done.yaml | wc -l

# Check issue resolution status
grep "status.*RESOLVED" cortex-master.yaml

# List all remediation ACs
grep "AC-REM-" .github/roadmap/phases/*.yaml

# Validate issue → resolution linking
# (ensure every issue has tracking in cortex-master.yaml)
```

### 9. Integration Checklist

When using this pattern:

- [ ] Read complete cortex-builder-issue-remediation-pattern.md
- [ ] Understand 5-stage lifecycle (Discovery → Closure)
- [ ] Use holistic review (ALL of cortex-master.yaml + issue file)
- [ ] Cross-reference implementation (grep, audit logs, tests)
- [ ] Make clear decision (REMEDIATION | ACCEPT-KNOWN | DEFER | ARCHITECTURE-FIX)
- [ ] If remediation: Create AC-REM-XXX-XX acceptance criteria
- [ ] Execute per standard phase workflow (TDD, audit logging, governance)
- [ ] Rename issue file to -done.yaml when resolved
- [ ] Update cortex-master.yaml tracking
- [ ] Create specialized agent if remediation > 3 phases

---

**This pattern provides**:
- Systematic issue review (not ad-hoc)
- Clear decision criteria
- Concrete remediation tracking (AC-IDs)
- Audit trail integration
- Closure markers (file renaming)
- Agent coordination (if complex)
