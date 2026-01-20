# CORTEX Builder - Issue Review & Remediation Pattern

**CRITICAL ENHANCEMENT - January 16, 2026**

This document defines how to review issues discovered in CORTEX and create concrete remediation plans.

## Issue Management Lifecycle

```yaml
issue_lifecycle:
  stage_1_discovery:
    description: "Issues identified via code review, testing, or architecture validation"
    output: "_workspaces/roadmap/issues/issue-report-NN.yaml"
    format: "YAML with executive summary, critical issues, evidence"
    examples:
      - "issue-report-01.yaml: AST scanning not used, Intent Router bypassed"
      - "issue-report-02.yaml: Domain Brain architecture gaps"
  
  stage_2_holistic_review:
    description: "Compare issue against LIVE IMPLEMENTATION (not sectional)"
    method: "Read roadmap holistically, verify against cortex-master.yaml"
    validation:
      - "Issue scope: Does it represent real gap or misunderstanding?"
      - "Roadmap coverage: Is this gap already planned in PHASE-XX?"
      - "Architecture alignment: Does issue conflict with approved decisions?"
      - "Dependency check: Will fixing this break other components?"
    output: "Clear DECISION: Remediation AC-ID OR Accept-as-Known-Limitation"
  
  stage_3_remediation_planning:
    description: "If remediation needed: Plan concrete ACs with audit evidence"
    steps:
      - "Create AC-ID(s) for the fix (AC-REM-XXX-XX format)"
      - "Add to existing phase YAML or create PHASE-REMEDIATION"
      - "Define testable acceptance criteria"
      - "Link to audit trail evidence (from analysis)"
      - "Plan implementation sequence"
    output: "Updated phase YAML with new remediation ACs"
  
  stage_4_implementation:
    description: "Execute remediation per standard phase workflow"
    approach: "Same as any phase: TDD, audit logging, governance enforcement"
    completion: "All remediation ACs passing tests with audit trail"
  
  stage_5_closure:
    description: "Mark issue resolved and rename issue file"
    action: "Rename issue-report-NN.yaml → issue-report-NN-done.yaml"
    verification: "Issue remediation referenced in phase completion summary"
```

## How to Conduct Holistic Issue Review

**MANDATORY: Review the ENTIRE roadmap and implementation, not just sections.**

```yaml
holistic_review_process:
  step_1_load_context:
    action: "Read full cortex-master.yaml (ALL sections)"
    verify:
      - "phase_tracker: Current status of all phases"
      - "architecture_decisions: Are approved ADs already addressing this?"
      - "governance: Are CORE rules covering this gap?"
      - "success_metrics: Does this issue affect metrics?"
    why: "Many 'issues' are actually already planned in different phases"
  
  step_2_issue_deep_dive:
    action: "Read issue-report-NN.yaml COMPLETELY"
    extract:
      - "executive_summary: Problem statement + recommendation"
      - "critical_issues: Root causes and evidence"
      - "impact: What breaks because of this?"
      - "required_implementation: What's the fix?"
    identify:
      - "Is this describing a REAL gap or a misunderstanding?"
      - "Is the evidence valid (code review) or speculative?"
      - "Are the recommendations realistic given architecture?"
  
  step_3_cross_reference_implementation:
    action: "Find mentioned components in codebase"
    verify:
      - "Does the component actually exist?"
      - "Is it implemented as described or differently?"
      - "Are there tests proving the implementation?"
      - "What does audit trail show?"
    examples:
      - Issue says "AST scanning never used" → grep for ASTIntelligenceEngine usage
      - Issue says "Intent Router only runs once" → Check orchestrator loop pattern
      - Issue says "Feature X missing" → Search for feature_x.py or feature-x in tests
  
  step_4_decision_matrix:
    decision_tree: |
      IF issue finding is based on misunderstanding:
        → DECISION: Accept-as-Known (document why it's not an issue)
      
      ELIF issue is real AND already planned in future phase:
        → DECISION: Cross-reference to PHASE-XX, ac_id: AC-YYY-YYY
      
      ELIF issue is real AND blocks current/near-term phases:
        → DECISION: Create remediation ACs in PHASE-REMEDIATION or current phase
      
      ELIF issue is real AND low-priority/cosmetic:
        → DECISION: Accept-as-Deferred-To-Phase-XX
      
      ELIF issue is real AND architectural:
        → DECISION: Create PHASE-ARCHITECTURE-FIX with detailed analysis
    
    output_template: |
      decision:
        issue_id: "[ISSUE-001]"
        finding: "[What the issue claimed]"
        verification: "[What we actually found]"
        decision: "REMEDIATION | ACCEPT-KNOWN | DEFER | ARCHITECTURE-FIX"
        if_remediation:
          phase: "PHASE-XX or PHASE-REMEDIATION"
          new_ac_ids:
            - "AC-REM-001-01: [Fix description]"
            - "AC-REM-001-02: [Fix description]"
        if_defer:
          target_phase: "PHASE-XX"
          reason: "[Why not fixing now]"
```

## Creating Remediation Phases in YAML

**When issue remediation is needed, create concrete ACs that are testable and auditable.**

```yaml
# Example: PHASE-ISSUE-001-REMEDIATION.yaml
# Issue: AST Scanning not used in Intent Router

phase:
  id: "PHASE-ISSUE-001-REMEDIATION"
  title: "AST Scanning Integration into Intent Router"
  source_issue: "issue-report-01.yaml / CRITICAL-ISSUE-1"
  priority: "P0 - CRITICAL"
  
  description: |
    Issue stated: "Intent Router bypasses AST scanning completely"
    
    Fix: Integrate ASTIntelligenceEngine into InteractionOrchestrator.comprehend_request()
    - Parse target files using AST
    - Build call graphs
    - Create impact maps
    - Present holistic context before execution
  
  acceptance_criteria:
    - ac_id: "AC-REM-001-01"
      description: "ASTIntelligenceEngine instantiated on every Intent Router request"
      test: |
        test_intent_router_ast_integration:
          - Create mock user request
          - Call InteractionOrchestrator.comprehend_request()
          - Verify engine.parse_file() was called for identified targets
          - Verify CallGraphBuilder.build_from_parse_result() was called
          - Verify audit log contains START → EXECUTE → COMPLETE
      success_criteria:
        - "AST parsing attempted for all identified target files"
        - "Call graph built from parse results"
        - "Dependency map created"
        - "Pattern detection run"
        - "Context YAML presented before execution"
    
    - ac_id: "AC-REM-001-02"
      description: "Intent Router runs on EVERY request (not just first)"
      test: |
        test_intent_router_continuous_execution:
          - Send multiple sequential requests
          - Verify Intent Router.comprehend_request() called N times
          - Verify LENS protocol executed fully on each turn
          - Verify no state carries over between turns (fresh context)
      success_criteria:
        - "Intent Router active on turns 1-N"
        - "LENS protocol 4 stages executed each turn"
        - "User approval gate enforced each turn"
        - "No silent bypass to executor"
    
    - ac_id: "AC-REM-001-03"
      description: "Audit trail shows complete LENS execution per turn"
      test: |
        test_audit_trail_intent_router:
          - Query governance.db for Intent Router AC-IDs
          - Verify START entry (before comprehension)
          - Verify EXECUTE entries (per LENS stage: Language, Examination, Navigation, Synthesis)
          - Verify COMPLETE entry (after comprehension+routing decision)
          - Verify timestamps show sequential execution
      success_criteria:
        - "3+ audit entries per turn per AC"
        - "Hash chain unbroken"
        - "Timestamps monotonic"
        - "No retroactive entries (would break hash chain)"
  
  files_to_modify:
    - "src/orchestrators/interaction_orchestrator.py"
      change: "Integrate ASTIntelligenceEngine.parse_file() in comprehend_request()"
    - "src/core/intelligence/call_graph.py"
      change: "Ensure public API exposed for orchestrator usage"
    - "src/core/intelligence/pattern_detector.py"
      change: "Ensure public API exposed for orchestrator usage"
  
  files_to_create:
    - "tests/integration/test_intent_router_ast_integration.py"
    - "tests/integration/test_intent_router_continuous_execution.py"
    - "tests/unit/governance/test_audit_trail_intent_router.py"
  
  dependencies:
    - "PHASE-07-INTENT-ROUTER"  # Must exist (IR-004 already complete)
    - "CORE-019"  # Governance rule: TDD-Master routing includes comprehension
  
  risks:
    - severity: "MEDIUM"
      description: "AST parsing might be slow on large files"
      mitigation: "Cache results, benchmark performance, profile"
    - severity: "LOW"
      description: "IR-004 BrainTierPusher incomplete (referenced but not done)"
      mitigation: "Complete BrainTierPusher as pre-requisite"
  
  audit_verification:
    expected_entries: "9"  # 3 ACs × 3 entries each (START/EXECUTE/COMPLETE)
    queries:
      - "SELECT ac_id, operation, COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-REM-001%' GROUP BY ac_id, operation"
      - "SELECT COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-REM-001%' AND operation='AC_COMPLETE'"
    expected_result: "3 rows with 3 AC_COMPLETE entries"
```

## Audit Log Evidence Requirements for Remediation ACs

**Every remediation AC must have concrete audit trail evidence linking to fix.**

```yaml
audit_evidence_format:
  requirement: |
    When remediation AC is COMPLETED, audit log must contain:
    1. AC_START: Timestamp when fix implementation began
    2. AC_EXECUTE: Multiple entries showing:
       - Test execution (RED → GREEN transitions)
       - Code modifications (if tracked)
       - Governance validation steps
    3. AC_COMPLETE: Timestamp when fix verified
  
  hash_chain: "All entries must form unbroken SHA-256 hash chain"
  
  query_example: |
    SELECT 
      ac_id,
      operation,
      timestamp,
      previous_hash,
      current_hash,
      payload_summary
    FROM audit_log
    WHERE ac_id = 'AC-REM-001-01'
    ORDER BY timestamp
    
    Expected output (3 rows):
    AC-REM-001-01 | AC_START    | 2026-01-16T14:00:00 | NULL | abc123... | "Remediation started"
    AC-REM-001-01 | AC_EXECUTE  | 2026-01-16T14:15:00 | abc123... | def456... | "Tests passing: 12/12"
    AC-REM-001-01 | AC_COMPLETE | 2026-01-16T14:30:00 | def456... | ghi789... | "Fix verified"
```

## Agent Creation for Issue Resolution

**If remediation is complex or new domain, create dedicated agent.**

```yaml
agent_creation_pattern:
  when_needed: |
    - Issue remediation requires new orchestrator
    - Issue analysis revealed new capability gap
    - Remediation spans 3+ phases
    - Issue needs specialized expertise (security, performance, etc.)
  
  new_agent_template:
    # Copy from existing agent, modify for new domain
    name: ".github/agents/cortex-XXXX.md"  # kebab-case, ≤25 chars
    sections:
      - purpose: "What specific issues does this agent resolve?"
      - scope: "Which phases/components does it touch?"
      - responsibilities: "What decisions does it make?"
      - limitations: "What is out of scope?"
      - integration: "How does it interact with other agents?"
    reference_examples:
      - ".github/agents/cortex-review-governance.md"
      - ".github/agents/cortex-review-hallucination.md"
      - ".github/agents/cortex-builder.md"
```

## Issue Closure Workflow

```yaml
closure_workflow:
  step_1_verify_remediation_complete:
    checklist:
      - "All remediation ACs have status: COMPLETED"
      - "All tests passing (100% pass rate)"
      - "Audit trail entries verified (START/EXECUTE/COMPLETE)"
      - "Hash chain integrity confirmed"
      - "Governance violations: 0"
      - "Phase dependencies not broken"
  
  step_2_update_phase_yaml:
    action: "Add reference to issue in phase completion summary"
    template: |
      phase_completion:
        resolved_issues:
          - "ISSUE-001: AST Scanning Integration"
            remediation_acs: ["AC-REM-001-01", "AC-REM-001-02", "AC-REM-001-03"]
            status: "RESOLVED"
            verification_date: "2026-01-16T14:30:00Z"
  
  step_3_rename_issue_file:
    action: "Rename to mark as done"
    from: "_workspaces/roadmap/issues/issue-report-01.yaml"
    to: "_workspaces/roadmap/issues/issue-report-01-done.yaml"
    reason: "Clearly marks issue as resolved and processed"
  
  step_4_update_master_yaml:
    location: "cortex-master.yaml"
    section: "issue_resolutions (new section)"
    entry: |
      resolved_issues:
        - issue_id: "ISSUE-001"
          title: "AST Scanning Integration"
          remediation_phase: "PHASE-ISSUE-001-REMEDIATION"
          remediation_acs: 3
          tests_passing: 12
          status: "RESOLVED"
          resolution_date: "2026-01-16"
```

## Quick Reference: Issue Review Checklist

**Before deciding on remediation:**

- [ ] Read entire cortex-master.yaml (not just sections)
- [ ] Read entire issue-report-NN.yaml (not just executive summary)
- [ ] Verify issue findings against live codebase (grep, file_search, read_file)
- [ ] Check if issue is already addressed in approved architecture decisions
- [ ] Check if issue is already planned in future phases
- [ ] Determine root cause (misunderstanding, real gap, design decision)
- [ ] Document decision clearly (REMEDIATION | ACCEPT-KNOWN | DEFER | ARCHITECTURE-FIX)
- [ ] If remediation: Create concrete AC-IDs with testable criteria
- [ ] Link remediation to audit trail evidence
- [ ] Add to phase YAML with dependencies and risks
- [ ] Execute remediation per standard phase workflow
- [ ] Rename issue file to -done when complete
- [ ] Update cortex-master.yaml with resolution tracking
