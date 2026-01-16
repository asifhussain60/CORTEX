# CORTEX Builder Enhancement Summary

**Date**: January 16, 2026  
**Change**: Enhanced cortex-builder.prompt.md with Issue Review & Remediation Pattern  
**Impact**: Provides structured, efficient approach to address discovered issues before production

## What Was Enhanced

### 1. **New Document Created**
- **File**: `.github/prompts/cortex-builder-issue-remediation-pattern.md`
- **Purpose**: Defines complete pattern for reviewing, planning, and resolving discovered issues
- **Sections**:
  - Issue Management Lifecycle (5 stages)
  - Holistic Issue Review Process (4 steps)
  - Creating Remediation Phases (YAML template with examples)
  - Audit Log Evidence Requirements
  - Agent Creation Guidelines
  - Issue Closure Workflow (4 steps)
  - Quick Reference Checklist

### 2. **cortex-builder.prompt.md Updated**
- Added reference section pointing to new remediation pattern
- Added commands documentation
- Integrated issue workflow into existing prompt structure

## The Pattern (Overview)

### Issue Lifecycle: 5 Stages

```
DISCOVERY → HOLISTIC REVIEW → REMEDIATION PLANNING → IMPLEMENTATION → CLOSURE
   ↓              ↓                    ↓                    ↓              ↓
Issues in    Compare vs       Create AC-REM-XXX-XX    Execute phase    Rename
.github/     full roadmap    with audit evidence      per TDD pattern   -done.yaml
roadmap/
```

### Key Principle: HOLISTIC Review (Not Sectional)

**Problem**: Issues often claim gaps that are actually:
- Already planned in future phases
- Already addressed by approved architecture decisions
- Based on misunderstandings of implementation
- Cosmetic/low-priority

**Solution**: 
1. Read entire `cortex-master.yaml` (not just relevant sections)
2. Read entire issue-report-NN.yaml (not just executive summary)
3. Cross-reference against live codebase (grep, audit logs, tests)
4. Make clear decision: REMEDIATION | ACCEPT-KNOWN | DEFER | ARCHITECTURE-FIX

### Creating Remediation ACs

When issue is real and needs fixing:

```yaml
AC-REM-001-01: [Brief description]
  - Testable acceptance criteria
  - Audit trail: START → EXECUTE → COMPLETE
  - Hash chain verification

AC-REM-001-02: [Fix aspect 2]
  - Tests: All passing
  - Audit entries: 3+ per AC

AC-REM-001-03: [Validation]
  - Evidence from governance.db query
  - Link to previous ACs
```

### Issue Closure

```yaml
step_1_verify: All ACs COMPLETED, 100% tests passing, audit verified
step_2_update: Add to phase completion summary with AC references
step_3_rename: issue-report-01.yaml → issue-report-01-done.yaml
step_4_track: Update cortex-master.yaml resolved_issues section
```

## Agent Creation

If remediation requires new capability:

```
.github/agents/cortex-new-domain.md  # kebab-case, ≤25 chars
  - Purpose: What issues does it resolve?
  - Scope: Which phases/components?
  - Responsibilities: What decisions?
  - Integration: How with other agents?
```

Examples:
- `.github/agents/cortex-review-governance.md`
- `.github/agents/cortex-review-hallucination.md`
- `.github/agents/cortex-builder.md`

## Benefits

1. **Efficiency**: Distinguishes real issues from misunderstandings quickly
2. **Holistic**: Views entire roadmap, not isolated sections
3. **Trackable**: Every remediation has concrete AC-IDs with audit trail
4. **Reproducible**: Pattern is documented and reusable
5. **Closure**: Clear "done" marker on resolved issues (file rename)
6. **Scalable**: Can create specialized agents for complex remediation domains

## How to Use

### When You Find an Issue

1. **Conduct Holistic Review**:
   ```bash
   # Read full context
   read_file cortex-master.yaml  # All sections
   read_file .github/roadmap/issues/issue-report-01.yaml  # Complete
   ```

2. **Verify Against Implementation**:
   ```bash
   grep_search for mentioned components
   read_file to verify claims
   check audit_log for evidence
   ```

3. **Decide**:
   - REMEDIATION: Create AC-REM-XXX-XX (new AC-IDs in phase)
   - ACCEPT-KNOWN: Document why it's not an issue
   - DEFER: Cross-reference to future phase
   - ARCHITECTURE-FIX: Create PHASE-ARCHITECTURE-FIX

4. **Execute**:
   - Follow standard phase workflow (TDD, audit logging, governance)
   - Create tests first (RED → GREEN)
   - Verify audit trail (START/EXECUTE/COMPLETE)

5. **Close**:
   - Rename issue-report-NN.yaml → issue-report-NN-done.yaml
   - Update cortex-master.yaml
   - Reference in phase completion summary

### When Remediation is Complex

1. Identify new domain/capability needed
2. Create `.github/agents/cortex-domain-name.md`
3. Define agent responsibilities and scope
4. Agent conducts remediation across multiple phases
5. Agent closes when all issues in domain resolved

## Example: AST Scanning Issue (from issue-report-01.yaml)

### Holistic Review
```
FINDING: "Intent Router bypasses AST scanning"
VERIFICATION: Check IR-004-02 comprehend_request() implementation
DECISION: REMEDIATION (real gap, blocks Intent Router functionality)
```

### Remediation ACs
```
AC-REM-001-01: ASTIntelligenceEngine on every request
AC-REM-001-02: Intent Router runs on every turn (not cached)
AC-REM-001-03: Audit trail shows LENS execution per turn
```

### Closure
```
phase_completion:
  resolved_issues:
    - ISSUE-001: AST Scanning Integration
      remediation_acs: [AC-REM-001-01, AC-REM-001-02, AC-REM-001-03]
      status: RESOLVED

# File renamed
issue-report-01.yaml → issue-report-01-done.yaml
```

## Files Modified

1. **Created**: `.github/prompts/cortex-builder-issue-remediation-pattern.md` (300 lines)
   - Complete pattern documentation
   - YAML templates with examples
   - Lifecycle visualization
   - Checklists

2. **Updated**: `.github/prompts/cortex-builder.prompt.md`
   - Added section reference to new pattern
   - Integrated issue workflow into existing prompt
   - Updated commands section

## Integration with Existing Workflow

### Before This Enhancement
- Issues discovered but no systematic review process
- Unclear whether to remediate, defer, or accept
- Remediation ACs mixed with other work
- No clear "done" marker on resolved issues

### After This Enhancement
- Structured 5-stage lifecycle for every issue
- Clear decision matrix for remediation choice
- Concrete AC-ID format (AC-REM-XXX-XX) for fixes
- File naming convention marks closure (-done.yaml)
- Tracking in cortex-master.yaml
- Optional specialized agents for complex domains

## Next Steps

1. **Review Outstanding Issues**:
   - Apply holistic review pattern to issue-report-01.yaml, 02, 03, 04
   - Document decisions in each issue file
   - Create remediation ACs for real gaps

2. **Create Remediation Phases** (if needed):
   - Add PHASE-ISSUE-XXX-REMEDIATION to cortex-master.yaml
   - Create phase YAML files
   - Execute per standard workflow

3. **Track Resolutions**:
   - Rename -done.yaml files as issues complete
   - Update cortex-master.yaml resolved_issues section
   - Reference in phase completion summaries

4. **Create Specialized Agents** (as needed):
   - If remediation domain spans 3+ phases
   - If requires specialized expertise
   - Document in `.github/agents/cortex-domain.md`

---

**Pattern Efficiency**: Issue review and remediation now has structured, repeatable workflow with clear decision criteria and audit trail requirements. Prevents scope creep and ensures all fixes are concrete, testable, and traceable.
