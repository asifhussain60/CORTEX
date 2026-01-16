# CORTEX Orchestrator - Plan Health & Implementation Accuracy (LOCAL PROMPT ROUTING)

**CRITICAL:** This orchestrator is **NOT a CORTEX code component**. It exists **ONLY** as routing logic within this prompt to guide phase-by-phase execution while maintaining plan integrity.

---

## Table of Contents

1. [Orchestrator Purpose](#orchestrator-purpose)
2. [Holistic YAML Review Protocol](#holistic-yaml-review-protocol)
3. [SOLID & DRY Architecture Validation](#solid--dry-architecture-validation)
4. [Lock-Then-Execute Pattern](#lock-then-execute-pattern)
5. [Pre-Lock Prompt Sync](#pre-lock-prompt-sync)
6. [Decision Trees](#decision-trees)
7. [Status Monitoring](#status-monitoring)

---

## Orchestrator Purpose

**Goal:** Keep the implementation plan healthy and execution accurate through 20+ phases.

**Scope:** Local prompt-based orchestration (NOT code-level orchestrator registration, NOT MCP tools, NOT auto-discovery).

**Authority:** The single source of truth is `.github/roadmap/cortex-master.yaml` → `phase_tracker` section.

**Discipline:** Never modify the plan without holistic verification of gaps, contradictions, and ripple effects.

---

## Holistic YAML Review Protocol

**Before any implementation or phase lock, perform comprehensive YAML review:**

### Step 1: Load Complete YAML Context

```
Files to load ENTIRELY (not sections):
├── .github/roadmap/cortex-master.yaml (SSOT)
│   ├── metadata section (DoR score, total_ac_ids)
│   ├── phase_tracker (ALL phases)
│   ├── architecture_decisions (AR-001 through AR-015)
│   ├── functional_requirements (FR-001 through FR-009)
│   ├── non_functional_requirements (NFR-001 through NFR-006)
│   └── governance_rules (all 25 SKULL rules)
│
├── .github/roadmap/phases/phase-XX.yaml (current + next phases)
├── cortex-brain/tier0/governance/core-rules.yaml (Tier 0 rules)
├── cortex-brain/tier0/governance/phase-enforcement-map.yaml
└── cortex-brain/tier0/response-headers.yaml (header config)
```

### Step 2: Gap Analysis (Identify Missing Pieces)

#### Gap Category: Definition Gaps

```yaml
definition_gaps:
  missing_ac_descriptions:
    check: "Every AC-ID has detailed description explaining WHAT and WHY"
    example_pass: "AC-REM-001-01: ASTIntelligenceEngine integrated into Interaction Orchestrator LENS comprehension phase"
    example_fail: "AC-001: Implement feature"
    action: "IF missing → ADD detailed description BEFORE implementation"
  
  missing_acceptance_criteria:
    check: "Every AC-ID has testable acceptance criteria (not vague goals)"
    example_pass: "ASTIntelligenceEngine.parse_file() called for every target file identified"
    example_fail: "Make AST integration better"
    action: "IF vague → CLARIFY with measurable test criteria"
  
  missing_phase_coherence:
    check: "All ACs in a phase are thematically related (no scattered random ACs)"
    example_pass: "PHASE-07: All IR-001 through IR-004 (all Intent Router)"
    example_fail: "PHASE-XX has IR-001, FR-002, AR-003, NFR-004 (random mix)"
    action: "IF incoherent → REORGANIZE to group by theme"
  
  missing_dependency_clarity:
    check: "Every 'requires' reference points to valid preceding phase"
    example_pass: "PHASE-16 requires: PHASE-07"
    example_fail: "PHASE-16 requires: PHASE-99 (doesn't exist)"
    action: "IF invalid → CORRECT to valid phase or REMOVE if not needed"
```

#### Gap Category: Brittleness Gaps

```yaml
brittleness_gaps:
  hardcoded_assumptions:
    check: "Phase hours/days estimates match velocity and buffer"
    example_gap: "PHASE-17: estimated_hours: 140 but no contingency for unknowns"
    action: "IF no buffer → ADD 20-30% contingency or CLARIFY why exact"
  
  missing_milestone_clarity:
    check: "Large phases broken into week/day milestones"
    example_pass: "PHASE-17 has week_1, week_2, week_3, week_4 breakdown"
    example_fail: "PHASE-17: estimated_hours: 140 (no sub-breakdown)"
    action: "IF no breakdown → ADD weekly milestones"
  
  floating_ac_ids:
    check: "Every AC-ID referenced in phase_tracker appears in a phase YAML"
    example_gap: "cortex-master.yaml lists 'AC-REM-001-01' but phase-remediation-01.yaml has no implementation details"
    action: "IF floating → VERIFY in phase YAML or MOVE to correct phase"
  
  vague_status_values:
    check: "Status values are standardized (NOT_STARTED, IN_PROGRESS, COMPLETED, READY_FOR_IMPLEMENTATION)"
    example_gap: "status: 'PENDING' or status: 'TODO' (non-standard)"
    action: "IF non-standard → STANDARDIZE to canonical values"
```

#### Gap Category: Logical Gaps

```yaml
logical_gaps:
  circular_dependencies:
    check: "Phase dependencies form valid DAG (no cycles)"
    example_gap: |
      PHASE-16 requires: PHASE-17
      PHASE-17 requires: PHASE-16 ← CIRCULAR!
    action: "IF circular → BREAK cycle by moving AC-ID or CLARIFY which comes first"
  
  missing_prerequisites:
    check: "Every phase with 'requires' has that prerequisite complete (locked: true)"
    example_gap: |
      PHASE-16 requires: PHASE-07
      But PHASE-07: locked: false ← Cannot start PHASE-16!
    action: "IF prerequisite incomplete → DEFER phase start or VERIFY complete status"
  
  orphaned_ac_ids:
    check: "Every AC-ID is assigned to exactly ONE phase"
    example_gap: |
      AC-AR-001-01 appears in PHASE-01 AND PHASE-02
      AC-FR-002-01 appears in NO phase
    action: "IF orphaned → ASSIGN to correct phase or REMOVE if no longer needed"
  
  inconsistent_counts:
    check: "ac_ids count in phase_tracker matches actual AC-IDs in phase YAML"
    example_gap: |
      phase_tracker.PHASE-01.ac_ids: 36
      phase-01.yaml has only 35 ACs defined
    action: "IF inconsistent → RECOUNT and UPDATE phase_tracker OR add missing AC-IDs"
```

#### Gap Category: Governance Gaps

```yaml
governance_gaps:
  missing_rule_applicability:
    check: "Every phase has applicable rules defined in phase-enforcement-map.yaml"
    example_gap: "PHASE-16: No rules listed in enforcement map"
    action: "IF missing → IDENTIFY which CORE/SKULL rules apply and ADD to enforcement map"
  
  conflicting_rules:
    check: "No two SKULL rules contradict each other"
    example_gap: |
      CORE-008: "Tests MUST exist before code"
      CORE-019: "Code can exist before tests (production mode)" ← CONFLICT
    action: "IF conflict → CLARIFY exception case and DOCUMENT in rule"
  
  missing_audit_requirements:
    check: "Phase enforcement map specifies required audit entries (START, EXECUTE, COMPLETE)"
    example_gap: "PHASE-16 enforcement has no audit_requirements section"
    action: "IF missing → ADD required audit entry types"
  
  missing_prompt_sync_requirements:
    check: "Every feature AC has companion prompt update requirement"
    example_gap: "AC-ENH-001-01 (Response Header Injection) has no CORTEX.prompt.md sync requirement"
    action: "IF missing → ADD prompt_sync_required: true and list sections to update"
```

### Step 3: Brittleness Analysis (Identify Fragile Points)

```yaml
brittleness_analysis:
  point_1_phase_transitions:
    risk: "When unlocking PHASE-XX, downstream PHASE-XX+1 may have stale context"
    check: "PHASE-XX+1 'requires' field correctly references PHASE-XX"
    examples:
      - "PHASE-10 requires: PHASE-09 ✓"
      - "PHASE-11 requires: PHASE-09 ✓"
      - "PHASE-REMEDIATION-01 requires: PHASE-16 ✓"
    mitigation: "Before lock: VERIFY all downstream requires are correct"
  
  point_2_ac_completion_verification:
    risk: "AC-IDs marked complete without proper audit trail"
    check: "completed_ac_ids <= ac_ids (can't complete more than total)"
    examples:
      - "PHASE-01: ac_ids: 36, completed_ac_ids: 36 ✓"
      - "PHASE-16: ac_ids: 8, completed_ac_ids: 12 ✗ IMPOSSIBLE"
    mitigation: "Before lock: Query audit_log, verify AC_COMPLETE entries exist"
  
  point_3_governance_tier_mixing:
    risk: "Code accessing TIER-0 immutable rules might try to modify them"
    check: "All TIER-0 access is read-only (no modifications)"
    examples:
      - "TierResolver.resolve_rules() reads TIER-0 ✓"
      - "GovernanceRegistry.update_tier_0_rules() tries to modify TIER-0 ✗ BLOCKED"
    mitigation: "Code review: GREP for tier0/ write operations, MUST find none"
  
  point_4_phase_yaml_sync:
    risk: "cortex-master.yaml and phase-XX.yaml diverge over time"
    check: "ac_ids count in cortex-master.yaml matches phase-XX.yaml"
    examples:
      - "cortex-master.yaml → PHASE-01.ac_ids: 36"
      - "phase-01.yaml defines exactly 36 AC-IDs ✓"
      - "phase-01.yaml defines 35 AC-IDs ✗ DESYNC"
    mitigation: "Before lock: RECOUNT from phase YAML file, UPDATE master if needed"
  
  point_5_locked_phase_immutability:
    risk: "Locked phase accidentally modified (violates hallucination prevention)"
    check: "If phase.locked: true, then no AC changes, no requirement changes"
    examples:
      - "PHASE-01: locked: true, ac_ids: 36 (unchanged from lock) ✓"
      - "PHASE-01: locked: true, ac_ids: 37 (added AC after lock) ✗ VIOLATION"
    mitigation: "Before lock: CREATE git checkpoint, DOCUMENT lock reason"
  
  point_6_prompt_desync:
    risk: "Features implemented but prompts not updated (agents don't know about features)"
    check: "If AC implemented, then corresponding prompt sections exist"
    examples:
      - "AC-ENH-001-01 (Response Headers) implemented, CORTEX.prompt.md has 'Response Header Integration' section ✓"
      - "AC-ENH-001-01 implemented, CORTEX.prompt.md has NO header info ✗ DESYNC"
    mitigation: "Before lock: VERIFY prompt sections match implemented features"
```

### Step 4: Contradiction Detection

```yaml
contradiction_detection:
  type_1_version_conflicts:
    description: "Phase requires version X but previous phase locked at version Y"
    check: "PHASE-XX.requires_version must be <= PHASE-XX-1.completed_version"
    remediation: "Update requires_version OR revert phase lock"
  
  type_2_scope_conflicts:
    description: "AC-ID scope in PHASE-XX contradicts acceptance criteria in PHASE-YY"
    check: "No AC-ID claims to do Y when another AC-ID in different phase already does Y"
    remediation: "Merge ACs OR clarify which phase owns responsibility"
  
  type_3_governance_conflicts:
    description: "PHASE-XX enforcement rules contradict PHASE-YY enforcement rules"
    check: "No SKULL rule contradicts another"
    remediation: "Clarify exception case OR separate concerns"
  
  type_4_timeline_conflicts:
    description: "Estimated hours > buffer hours (will overrun)"
    check: "total_estimated_hours + total_buffer_hours <= reasonable calendar"
    remediation: "Reduce scope OR extend timeline OR increase buffer"
```

### Step 5: Hallucination Potential Identification

```yaml
hallucination_risks:
  risk_1_ac_completion_without_audit:
    description: "AC marked completed but no audit entries exist"
    detection: "SELECT ac_id FROM cortex-master.yaml WHERE completed_ac_ids > 0 
               AND ac_id NOT IN (SELECT ac_id FROM audit_log)"
    prevention: "CORE-027: Require AC_START, AC_EXECUTE, AC_COMPLETE before completion"
  
  risk_2_phase_lock_without_verification:
    description: "Phase locked without verifying all ACs are actually done"
    detection: "locked: true but audit_verification.verified: false"
    prevention: "Before lock: QUERY audit_log, VERIFY all AC_COMPLETE entries exist"
  
  risk_3_prompt_instruction_mismatch:
    description: "CORTEX.prompt.md or copilot-instruction.md doesn't document implemented features"
    detection: "Grep prompt files for mentions of response headers, tier2 templates, etc."
    prevention: "Pre-lock: UPDATE prompts with all new features from phase"
  
  risk_4_governance_bypass:
    description: "Code attempts to bypass TIER-0 rules or modify immutable configs"
    detection: "GREP for 'tier0' writes, bypass attempts, 'CORE-017' violations"
    prevention: "Code review: No modifications to TIER-0, all rule evaluations read-only"
  
  risk_5_circular_dependency_creation:
    description: "Modification creates cycle in phase dependency graph"
    detection: "If PHASE-XX requires PHASE-YY, verify PHASE-YY does NOT require PHASE-XX"
    prevention: "Before modification: Run DAG validation, show dependency chain"
```

---

## SOLID & DRY Architecture Validation

**Before implementing or locking any phase, validate compliance with SOLID and DRY principles.**

### Single Responsibility Principle (SRP)

```yaml
srp_validation:
  check_1_phase_focus:
    description: "Each phase has single, well-defined focus"
    pass_example: |
      PHASE-07: "Holistic Intent Router Intelligence"
      - Focus: Intent Router (IR-001 through IR-004)
      - All ACs related to routing and comprehension
    fail_example: |
      PHASE-XX: "Misc Improvements"
      - AC-AR-001-01: Governance
      - AC-FR-002-01: Features
      - AC-NFR-003-01: Security
      - (scattered, no coherent focus)
    action: "IF scattered → REORGANIZE by theme"
  
  check_2_ac_responsibility:
    description: "Each AC-ID has ONE clear responsibility (not multiple)"
    pass_example: "AC-AR-012-01: Base Orchestrator abstract class (single responsibility)"
    fail_example: "AC-AR-012-01: Base Orchestrator + MCP exposure + Audit logging + ... (too many)"
    action: "IF overloaded → SPLIT into multiple ACs"
  
  check_3_orchestrator_focus:
    description: "This prompt orchestrator has single focus: keep plan healthy"
    check: "Does it verify DAG? Check governance? Detect hallucinations?"
    action: "Keep focused on plan health, NOT on code implementation"
```

### Open/Closed Principle (OCP)

```yaml
ocp_validation:
  check_1_extensibility:
    description: "Plan can accommodate new phases without modifying locked phases"
    pass_example: |
      PHASE-REMEDIATION-01 added after PHASE-16 without changing locked phases
      ✓ Open to extension, closed to modification
    fail_example: |
      Add PHASE-20, but must modify PHASE-10's acceptance criteria
      ✗ Breaks OCP (must modify existing phase)
    action: "New phases must NOT require changes to locked phases"
  
  check_2_plugin_pattern:
    description: "Orchestrators can be added without modifying core orchestrator registry"
    check: "Review AR-012 (Orchestrator Plugin Framework)"
    action: "Verify decorator-based auto-registration, not hardcoded registration"
```

### Liskov Substitution Principle (LSP)

```yaml
lsp_validation:
  check_1_interface_consistency:
    description: "All orchestrators implement same IOrchestrator interface"
    pass_example: |
      MasterOrchestrator, PlanningOrchestrator, ADOOrchestrator
      All implement: execute(), get_status(), get_mcp_tools()
    fail_example: |
      MasterOrchestrator has execute()
      PlanningOrchestrator has perform() instead
      (inconsistent interface)
    action: "Verify all orchestrators in AR-012 define consistent interface"
  
  check_2_substitutability:
    description: "Can swap one orchestrator for another without breaking code"
    check: "Review MasterOrchestrator delegation to sub-orchestrators"
    action: "Verify Master doesn't depend on internal details of sub-orchestrators"
```

### Interface Segregation Principle (ISP)

```yaml
isp_validation:
  check_1_tier_separation:
    description: "TIER-0, TIER-1, TIER-2, TIER-3 have separate interfaces (not one monolithic governance object)"
    pass_example: |
      TIER-0: CoreRulesRegistry (immutable rules)
      TIER-1: ProjectGovernance (project-specific)
      TIER-2: EngineeringStandards (team conventions)
      TIER-3: KnowledgeLibrary (examples, patterns)
    action: "Verify each tier has separate, focused interface"
  
  check_2_prompt_separation:
    description: "CORTEX.prompt.md, copilot-instruction.md, cortex-builder.prompt.md have focused scopes"
    pass_example: |
      cortex-builder.prompt.md: Implementation guidance
      CORTEX.prompt.md: Intent routing and comprehension
      copilot-instruction.md: Copilot-specific instructions
    action: "Verify prompts don't overlap, each has clear focus"
```

### Dependency Inversion Principle (DIP)

```yaml
dip_validation:
  check_1_governance_abstraction:
    description: "Code depends on governance abstractions, not hardcoded rules"
    pass_example: |
      GovernanceRegistry.evaluate_rules() is abstract
      Code calls evaluate_rules(), doesn't know which rules are loaded
    fail_example: |
      Code has: if CORE_008_REQUIRED: ...
      (hardcoded rule, breaks on rule changes)
    action: "Verify governance dependencies are inverted (abstract)"
  
  check_2_tier_abstraction:
    description: "Code depends on tier abstractions, not specific tier implementations"
    pass_example: |
      Code calls: TierResolver.get_applicable_rules(tier_level)
      Returns abstracted RuleSet
    fail_example: |
      Code directly accesses: tier0/governance/core-rules.yaml
      (hardcoded tier location)
    action: "Verify tier dependencies are abstracted"
```

### DRY (Don't Repeat Yourself)

```yaml
dry_validation:
  check_1_duplicate_rules:
    description: "No governance rule defined twice"
    check: "GREP core-rules.yaml for duplicate rule IDs"
    example_violation: |
      CORE-008: Tests first (rule 1)
      CORE-008: Tests first (rule 2) ← DUPLICATE
    action: "IF duplicate → CONSOLIDATE into single rule"
  
  check_2_duplicate_ac_ids:
    description: "No AC-ID appears in multiple phases"
    check: "Every AC-ID assigned to exactly one phase"
    example_violation: |
      PHASE-01 contains: AC-AR-001-01
      PHASE-02 contains: AC-AR-001-01 ← DUPLICATE
    action: "IF duplicate → MOVE to one phase or RENAME if they're different"
  
  check_3_duplicate_phase_yaml:
    description: "No phase YAML duplicates information from cortex-master.yaml"
    check: "AC-ID descriptions in phase-XX.yaml should reference, not duplicate"
    example_violation: |
      cortex-master.yaml:
        AC-AR-001-01: "Tier 0 rules loaded..."
      phase-01.yaml:
        AC-AR-001-01: "Tier 0 rules loaded..." (DUPLICATE)
    action: "IF duplicate → Use single source (cortex-master.yaml), phase YAML references only"
  
  check_4_pattern_reuse:
    description: "Orchestrator patterns used consistently (not reimplemented)"
    check: "Review AR-012: @orchestrator decorator used for ALL orchestrators"
    action: "Verify pattern reuse, no custom registration code"
```

---

## Lock-Then-Execute Pattern

**This is the core orchestration workflow. Execute this pattern for EVERY phase transition.**

### Phase 1: Pre-Lock Review (BEFORE Implementation)

```
GOAL: Verify the phase YAML is ready for implementation
INPUT: cortex-master.yaml + phases/phase-XX.yaml
OUTPUT: Approval to proceed OR list of gaps to fix

STEPS:

1. HOLISTIC REVIEW (Step 1-5 from YAML Review Protocol above)
   ├─ Load entire YAML files (not sections)
   ├─ Check for definition gaps
   ├─ Check for brittleness gaps
   ├─ Check for logical gaps
   ├─ Check for governance gaps
   └─ Document any gaps found → CANNOT PROCEED if gaps exist

2. SOLID/DRY VALIDATION (from Architecture Validation above)
   ├─ SRP: Phase has single, coherent focus
   ├─ OCP: Phase additions don't require modifying other phases
   ├─ LSP: Orchestrator interfaces consistent
   ├─ ISP: Concerns properly separated
   ├─ DIP: Dependencies abstracted
   ├─ DRY: No duplication across phases
   └─ Document any violations → CANNOT PROCEED if violations exist

3. GOVERNANCE TIER VALIDATION
   ├─ Check phase-enforcement-map.yaml for this phase's rules
   ├─ Verify all SKULL rules in enforcement map are in core-rules.yaml
   ├─ Check for conflicting rules
   ├─ Verify audit requirements defined
   └─ Document rules that will be enforced

4. DEPENDENCY VALIDATION
   ├─ Verify all 'requires' phases have locked: true
   ├─ Verify no circular dependencies
   ├─ Verify all AC-IDs in phase YAML exist in cortex-master.yaml
   └─ If dependencies fail → CANNOT PROCEED

5. CONSISTENCY CHECK
   ├─ ac_ids count = actual ACs in phase YAML
   ├─ AC descriptions are detailed (not vague)
   ├─ Acceptance criteria are testable (not subjective)
   ├─ No AC appears in multiple phases
   └─ If inconsistencies found → CANNOT PROCEED

6. APPROVAL GATE
   ├─ IF all checks pass → Output: "✅ READY TO IMPLEMENT"
   ├─ IF any checks fail → Output list of gaps + prevention steps
   └─ Recommend fixes before proceeding
```

**Example Pre-Lock Review Output:**

```yaml
pre_lock_review:
  phase: "PHASE-16-ORCHESTRATOR-CONTINUATION"
  timestamp: "2026-01-16T10:00:00Z"
  
  holistic_review:
    status: "PASS ✅"
    definition_gaps: 0
    brittleness_gaps: 0
    logical_gaps: 0
    governance_gaps: 0
  
  solid_dry_validation:
    status: "PASS ✅"
    srp: "PASS - Phase has clear focus (ConversationProtocol)"
    ocp: "PASS - Doesn't require modifying PHASE-07"
    lsp: "PASS - Orchestrator interfaces consistent"
    isp: "PASS - Concerns properly separated"
    dip: "PASS - Dependencies abstracted"
    dry: "PASS - No duplication"
  
  governance_validation:
    status: "PASS ✅"
    rules_enforced: ["CORE-008", "CORE-011", "CORE-012", "CORE-019", "CORE-027"]
    audit_requirements: ["AC_START", "AC_EXECUTE", "AC_COMPLETE"]
    conflicts_detected: 0
  
  dependency_validation:
    status: "PASS ✅"
    requires_phase: "PHASE-07-INTENT-ROUTER"
    prerequisite_locked: true
    circular_deps: 0
  
  consistency_check:
    status: "PASS ✅"
    ac_ids_defined: 8
    ac_ids_in_phase_yaml: 8
    ac_descriptions: "all detailed"
    acceptance_criteria: "all testable"
    duplicates: 0
  
  DECISION: "✅ READY TO IMPLEMENT PHASE-16"
  RECOMMENDATION: "Proceed with implementation. All governance rules loaded. Unlock only one AC-ID at a time."
```

### Phase 2: Implementation (During execution)

```
GOAL: Implement phase while maintaining audit trail and governance compliance
WORKFLOW: (Implemented in cortex-builder.prompt.md, NOT changed here)

KEY POINTS:
- Implement ONE AC-ID at a time
- Each AC-ID gets AC_START, AC_EXECUTE, AC_COMPLETE audit entries
- Governance rules enforced continuously
- Tests RED → GREEN pattern (CORE-008)
- Git checkpoints before major actions (CORE-026)
- No modifications to locked phases
```

### Phase 3: Pre-Lock Prompt Sync (BEFORE setting locked: true)

```
GOAL: Ensure prompts (CORTEX.prompt.md, copilot-instruction.md) document all implemented features
INPUT: All AC-IDs in phase just completed
OUTPUT: Prompts updated + readiness for lock

STEPS:

1. IDENTIFY NEW FEATURES
   ├─ Read completed phase YAML
   ├─ List all AC-IDs that shipped
   ├─ Identify features that affect CORTEX orchestration behavior
   └─ Example: AC-ENH-001-01 = Response Header Injection → affects all responses

2. AUDIT CURRENT PROMPTS
   ├─ Read CORTEX.prompt.md completely
   ├─ Read copilot-instruction.md completely
   ├─ Search for existing mentions of new features
   ├─ Identify gaps where features should be documented
   └─ Example: CORTEX.prompt.md has NO section on Response Headers after AC-ENH-001-01

3. UPDATE CORTEX.prompt.md (if needed)
   ├─ IF feature affects intent routing → Update "Intent Router" section
   ├─ IF feature affects response format → Update "Response Header Integration" section
   ├─ IF feature affects governance → Update "Governance Integration" section
   ├─ IF feature affects tier system → Update "Tier Integration" section
   ├─ Add new sections only if truly necessary
   ├─ Keep prompt focused (no bloat)
   └─ Example: Response Header Injection → 1 short section explaining headers

4. UPDATE copilot-instruction.md (if needed)
   ├─ IF feature affects response format → Update "Response Format Standards" section
   ├─ IF feature affects copyright handling → Update existing copyright section
   ├─ IF feature affects prompt instructions → Update "Instructions" section
   ├─ Keep edits minimal and focused
   └─ Example: Response Header Injection → 1 sentence explaining headers appear in all responses

5. VERIFICATION
   ├─ Read updated prompts cover all new features
   ├─ Search for feature names in prompts → should find references
   ├─ Verify no contradictions with old sections
   ├─ Verify prompts are still focused (not bloated)
   └─ IF updates needed → make them now

6. LOCK READINESS
   ├─ IF prompts adequately updated → Ready to lock phase
   ├─ IF prompts insufficient → Continue phase in development state
   └─ NEVER lock phase with outdated prompts
```

**Example Prompt Sync Checklist:**

```yaml
prompt_sync_checklist:
  phase: "PHASE-ENHANCEMENT-01"
  completion_date: "2026-01-15"
  
  new_features_shipped:
    - "AC-ENH-001-01: ResponseHeaderInjector in PlanningOrchestrator"
    - "AC-ENH-001-02: Headers appear in responses"
    - "AC-ENH-001-03: Documentation pattern defined"
    - "AC-ENH-001-04: Zero test regressions"
  
  prompt_audit:
    cortex_prompt_md:
      current_coverage: "Response Header Integration section exists ✓"
      coverage_depth: "Adequate - explains headers, variables, config"
      action_needed: "NONE - already documented in AC-ENH-001-03"
    
    copilot_instruction_md:
      current_coverage: "Response Format Standards section exists ✓"
      coverage_depth: "Covers header format and copyright"
      action_needed: "NONE - adequate coverage"
  
  prompt_updates:
    - file: "CORTEX.prompt.md"
      action: "VERIFY existing section covers all 4 ACs"
      result: "✓ Section already covers ResponseHeaderInjector, variables, templates, regression testing"
      changes_needed: 0
    
    - file: "copilot-instruction.md"
      action: "VERIFY format standards cover headers"
      result: "✓ Section describes standard format with headers"
      changes_needed: 0
  
  verification:
    features_mentioned_in_prompts: 4/4 ✓
    contradictions_detected: 0 ✓
    prompt_length_acceptable: ✓
    new_agents_needed: none
  
  LOCK_READY: "✅ YES - Prompts adequate, phase ready to lock"
```

### Phase 4: Lock & Update Master (AFTER prompt sync approved)

```
GOAL: Finalize phase and unlock next phase
WORKFLOW:

STEPS:

1. FINAL AUDIT VERIFICATION
   ├─ Query governance.db for this phase
   ├─ Verify every AC-ID has AC_START, AC_EXECUTE, AC_COMPLETE
   ├─ Verify hash chain unbroken
   ├─ Verify completion percentage = 100% (all ACs done)
   └─ IF not all entries present → CANNOT LOCK

2. UPDATE cortex-master.yaml
   ├─ Set phase.status: "COMPLETED"
   ├─ Set phase.locked: true
   ├─ Update phase.completed_at timestamp
   ├─ Set audit_verification.verified: true
   ├─ Update audit_verification.entry_count (actual count from query)
   ├─ Set audit_verification.hash_chain_valid: true
   └─ Commit: "phase-XX: locked - audit verified, cleanup done"

3. CLEAN UP DOCUMENTATION
   ├─ Delete any phase-specific .md files from repo root
   ├─ Move any reports to .github/roadmap/reports/
   ├─ Ensure no files_to_create are .gitkeep only (empty directories)
   └─ Commit: "cleanup: phase-XX documentation"

4. UNLOCK NEXT PHASE
   ├─ Identify next phase in sequence
   ├─ Verify its 'requires' field matches THIS phase (just locked)
   ├─ Run Pre-Lock Review (Phase 1 above) on next phase
   ├─ IF review passes → Next phase ready for implementation
   ├─ IF review fails → Report gaps before proceeding
   └─ Commit: "checkpoint: ready for PHASE-XX"

5. SUMMARY UPDATE
   ├─ Update phase_tracker in cortex-master.yaml
   ├─ Note: progress_percentage, completed_at, lock status
   ├─ Commit: "progress: PHASE-XX locked, PHASE-XX+1 ready"
   └─ Communicate readiness to implementation team
```

---

## Pre-Lock Prompt Sync

**CRITICAL:** Before locking ANY phase, ensure prompts document all new features.

### Prompt Sync Workflow

```yaml
pre_lock_prompt_sync:
  trigger: "When phase AC_COMPLETE audit entries verified"
  scope: "Only phases that shipped NEW orchestrator/governance features"
  
  prompts_to_review:
    - ".github/prompts/CORTEX.prompt.md"
    - ".github/copilot-instruction.md"
    - ".github/prompts/cortex-builder.prompt.md" (if builder rules changed)
  
  sync_rules:
    rule_1_orchestrator_features:
      description: "If phase implemented new orchestrator type/pattern, CORTEX.prompt.md must document"
      example: "PHASE-16 implements ConversationProtocol → CORTEX.prompt.md must explain turn-by-turn execution"
      enforcement: "Search CORTEX.prompt.md for 'ConversationProtocol' → MUST find reference"
    
    rule_2_response_format_changes:
      description: "If phase changed response format, copilot-instruction.md must document"
      example: "PHASE-ENH-01 adds response headers → copilot-instruction.md must show header format"
      enforcement: "Search copilot-instruction.md for 'header' → MUST find references"
    
    rule_3_governance_rule_changes:
      description: "If phase affects governance evaluation, CORTEX.prompt.md must document"
      example: "PHASE-09 adds GV-003 (Pre-Commit Hook) → CORTEX.prompt.md must explain hook"
      enforcement: "Search CORTEX.prompt.md for governance tools → MUST have section"
    
    rule_4_prompt_efficiency:
      description: "Keep prompts efficient - don't duplicate information"
      enforcement: "Each prompt focused on its purpose, no massive bloat, <2000 lines per prompt"
    
    rule_5_no_stale_sections:
      description: "Remove outdated sections if feature deprecated"
      enforcement: "If PHASE-XX removes feature, search prompts for old mentions → DELETE outdated info"
```

### Sync Validation Checklist

```yaml
sync_validation:
  phase: "PHASE-XX"
  
  step_1_identify_features:
    action: "List all AC-IDs that shipped"
    output: ["AC-XXX-XX", "AC-YYY-YY", ...]
  
  step_2_categorize_features:
    orchestrator_features: ["AC-REM-001-05", ...]
    response_features: ["AC-ENH-001-01", ...]
    governance_features: ["AC-REM-003-01", ...]
    tier_features: ["AC-DB-001-01", ...]
  
  step_3_search_cortex_prompt_md:
    search_terms: ["feature name 1", "feature name 2", ...]
    expected: "All feature names should have >= 1 mention"
    action: "If feature not mentioned → ADD section to CORTEX.prompt.md"
  
  step_4_search_copilot_instruction_md:
    search_terms: ["response format changes", "header changes", ...]
    expected: "All response format changes should be documented"
    action: "If change not documented → UPDATE copilot-instruction.md"
  
  step_5_verify_coherence:
    check: "New sections don't contradict old sections"
    check: "Prompts still focused on their purpose"
    check: "No massive duplication"
    action: "If issues found → EDIT for coherence"
  
  step_6_approval:
    gate: "Are all features documented?"
    gate: "Are prompts still efficient?"
    gate: "Are there contradictions?"
    if_yes: "✅ READY TO LOCK PHASE"
    if_no: "❌ Continue updating prompts, retry step 1-5"
```

---

## Decision Trees

**Use these decision trees to route orchestration decisions.**

### Decision Tree 1: Can We Start Phase X?

```
DECISION: Can we start implementing PHASE-X?

  START
    │
    ├─ Is PHASE-X in cortex-master.yaml?
    │  NO → Cannot start (phase doesn't exist)
    │  YES → Continue
    │
    ├─ Does PHASE-X have 'requires' field?
    │  NO → Can start anytime
    │  YES → Continue
    │
    ├─ Is the required phase's 'locked' field = true?
    │  NO → Cannot start (prerequisite incomplete)
    │  YES → Continue
    │
    ├─ Does PHASE-X already have locked: true?
    │  YES → Cannot start (phase already complete)
    │  NO → Continue
    │
    ├─ Run Pre-Lock Review (YAML Review Protocol steps 1-5)
    │  GAPS FOUND → Cannot start (fix gaps first)
    │  NO GAPS → Continue
    │
    ├─ Run SOLID/DRY Validation
    │  VIOLATIONS FOUND → Cannot start (resolve violations)
    │  NO VIOLATIONS → Continue
    │
    └─ ✅ DECISION: Can start PHASE-X
       ACTION: Execute Phase 1: Pre-Lock Review formally
               Then execute Phase 2: Implementation
```

### Decision Tree 2: Should We Lock Phase X?

```
DECISION: Is PHASE-X ready to lock?

  START
    │
    ├─ Are all AC-IDs in PHASE-X completed?
    │  (completed_ac_ids == ac_ids in cortex-master.yaml)
    │  NO → Cannot lock (incomplete ACs)
    │  YES → Continue
    │
    ├─ Query governance.db: Do all AC-IDs have audit entries?
    │  (AC_START, AC_EXECUTE, AC_COMPLETE for each AC-ID)
    │  NO → Cannot lock (missing audit trail)
    │  YES → Continue
    │
    ├─ Is hash chain integrity verified?
    │  NO → Cannot lock (potential tamper detected)
    │  YES → Continue
    │
    ├─ Run Pre-Lock Prompt Sync (from "Pre-Lock Prompt Sync" section)
    │  OUTDATED PROMPTS → Continue to prompts updates
    │  PROMPTS CURRENT → Continue
    │
    ├─ Have prompts been updated (if needed)?
    │  NO → Cannot lock (prompts outdated)
    │  YES → Continue
    │
    ├─ Are all documentation reports in .github/roadmap/reports/?
    │  NO → Cannot lock (reports in wrong location)
    │  YES → Continue
    │
    └─ ✅ DECISION: PHASE-X is ready to lock
       ACTION: Execute Phase 4: Lock & Update Master
               Update cortex-master.yaml
               Commit changes
               Notify team of next phase
```

### Decision Tree 3: What If There's a Gap?

```
DECISION: How to handle discovered gap?

  START (gap discovered)
    │
    ├─ Is this a DEFINITION GAP?
    │  (AC-ID missing description, acceptance criteria vague, etc.)
    │  NO → Skip to next check
    │  YES → Continue
    │    ├─ Severity: Blocking or Minor?
    │    │  BLOCKING → Cannot proceed (define clearly first)
    │    │  MINOR → Proceed with note
    │    └─ FIX: Add detailed description/criteria before implementation
    │
    ├─ Is this a BRITTLENESS GAP?
    │  (Missing milestone breakdown, hardcoded assumptions, etc.)
    │  NO → Skip to next check
    │  YES → Continue
    │    ├─ Severity: Blocking or Minor?
    │    │  BLOCKING → Cannot proceed (add clarity first)
    │    │  MINOR → Proceed with contingency plan
    │    └─ FIX: Add milestones/contingency/clarification
    │
    ├─ Is this a LOGICAL GAP?
    │  (Circular dependencies, missing prerequisites, orphaned ACs, etc.)
    │  NO → Skip to next check
    │  YES → Continue
    │    ├─ Severity: Blocking or Minor?
    │    │  BLOCKING → Cannot proceed (resolve logic first)
    │    │  MINOR → Proceed with documented assumption
    │    └─ FIX: Resolve dependency/assignment/contradiction
    │
    ├─ Is this a GOVERNANCE GAP?
    │  (Missing rule applicability, conflicting rules, etc.)
    │  NO → Skip to next check
    │  YES → Continue
    │    ├─ Severity: Blocking or Minor?
    │    │  BLOCKING → Cannot proceed (clarify governance first)
    │    │  MINOR → Proceed with governance note
    │    └─ FIX: Identify/clarify/document governance requirement
    │
    └─ ✅ DECISION: Gap has been categorized
       ACTION: Fix gap OR document assumption OR defer to later phase
               Update cortex-master.yaml if change needed
               Commit with clear message
```

---

## Status Monitoring

**Monitor these metrics to keep CORTEX healthy.**

### Metric 1: Plan Integrity Score (DoR)

```yaml
plan_integrity_score:
  formula: "(100 - (total_gaps + total_brittleness + total_contradictions))"
  current: "100/100 (in cortex-master.yaml metadata.dor_score)"
  threshold: ">90 to proceed"
  
  components:
    definition_gaps:
      weight: 5 points per gap
      current: 0
    
    brittleness_gaps:
      weight: 3 points per gap
      current: 0
    
    logical_gaps:
      weight: 10 points per gap
      current: 0
    
    governance_gaps:
      weight: 8 points per gap
      current: 0
    
    contradictions:
      weight: 10 points per contradiction
      current: 0
  
  check_frequency: "Before every phase lock"
  action_if_low: "Stop implementation, fix gaps, recompute DoR"
```

### Metric 2: Governance Compliance Rate

```yaml
governance_compliance_rate:
  formula: "(phases_compliant / total_phases) × 100"
  
  calculation:
    phases_with_all_rules_passed: 12 (PHASE-01 through PHASE-12, PHASE-10, etc.)
    total_phases: 16
    rate: "75%"
  
  per_phase: "Each phase tracks which SKULL rules passed/failed"
  
  check_frequency: "After every AC-ID completion"
  action_if_low: "Identify rule violations, fix before next phase lock"
```

### Metric 3: Audit Trail Completeness

```yaml
audit_trail_completeness:
  formula: "(ac_ids_with_complete_audit / total_ac_ids) × 100"
  
  complete_audit: "AC has AC_START, AC_EXECUTE, AC_COMPLETE entries"
  
  calculation:
    ac_ids_fully_audited: 240 (PHASE-01 through PHASE-12, enhancements, PHASE-15, PHASE-16)
    total_ac_ids: 246
    rate: "97.6%"
  
  incomplete: ["AC-REM-001-01", "AC-REM-001-02", ... (PHASE-REMEDIATION not yet executed)]
  
  check_frequency: "Before every phase lock"
  action_if_low: "Complete audit trail before locking"
```

### Metric 4: Prompt Synchronization

```yaml
prompt_synchronization:
  definition: "Prompts document all implemented features"
  
  check:
    cortex_prompt_md: "Mentions Response Headers? ✓ SYNCED"
    cortex_prompt_md: "Explains ConversationProtocol? ✓ SYNCED"
    cortex_prompt_md: "Covers Domain Brain (if PHASE-17 done)? TBD"
    
    copilot_instruction_md: "Shows header format? ✓ SYNCED"
    copilot_instruction_md: "Covers new features? ✓ SYNCED"
  
  check_frequency: "Before every phase lock"
  action_if_desync: "Update prompts before locking phase"
```

### Metric 5: Phase Dependency Health

```yaml
phase_dependency_health:
  definition: "Phase dependency graph is valid DAG with no cycles"
  
  check:
    circular_dependencies: 0 ✓
    broken_requires: 0 ✓ (all 'requires' phases exist and are locked/unlocked correctly)
    orphaned_ac_ids: 0 ✓
    duplicate_ac_ids: 0 ✓
  
  check_frequency: "Before every new phase addition"
  action_if_unhealthy: "Fix dependency chain before proceeding"
```

---

## Summary: Complete Orchestration Workflow

```
LOOP FOR EACH PHASE {

  1. PRE-LOCK REVIEW
     └─ Holistic YAML review
     └─ SOLID/DRY validation
     └─ Governance tier validation
     └─ Dependency validation
     └─ Consistency checks
     └─ IF all pass → APPROVED, else → FIX GAPS
  
  2. IMPLEMENTATION (via cortex-builder.prompt.md)
     └─ Implement AC-IDs one at a time
     └─ Each AC-ID: AC_START → tests (RED→GREEN) → AC_EXECUTE → AC_COMPLETE
     └─ Governance rules enforced continuously
     └─ Git checkpoints at each AC completion
     └─ Tests 100% passing, all ACs done
  
  3. PRE-LOCK PROMPT SYNC
     └─ Identify new features from phase
     └─ Search prompts for mentions
     └─ Update CORTEX.prompt.md (if needed)
     └─ Update copilot-instruction.md (if needed)
     └─ Verify no contradictions
     └─ IF prompts adequate → APPROVED, else → UPDATE PROMPTS
  
  4. LOCK & UPDATE MASTER
     └─ Verify audit trail complete
     └─ Set phase.locked: true in cortex-master.yaml
     └─ Update audit_verification fields
     └─ Clean up documentation
     └─ Unlock next phase
     └─ Commit changes
  
  NEXT PHASE → repeat

}

GOAL: Every phase locked with confidence that:
  ✓ YAML is well-formed and consistent
  ✓ SOLID/DRY principles maintained
  ✓ Governance rules enforced
  ✓ Audit trail complete
  ✓ Prompts document all features
  ✓ Ready for production
```

---

## Maintenance Notes

This orchestrator lives **ONLY in this prompt** and guides decision-making at each phase transition. It does **NOT**:

- ❌ Become a code-level orchestrator in CORTEX
- ❌ Get registered with OrchestratorRegistry
- ❌ Expose MCP tools
- ❌ Require database tables
- ❌ Create additional files

It **ONLY**:

- ✅ Provides phase-by-phase guidance in natural language
- ✅ References cortex-master.yaml as single source of truth
- ✅ Routes decisions through decision trees
- ✅ Validates SOLID/DRY compliance
- ✅ Ensures prompts stay synchronized
- ✅ Prevents hallucination through holistic review

**Execution:** Follow this prompt whenever a phase is ready for lock or when planning next steps.
