# PHASE 24 INTEGRATION GUIDE
## Architecture Integrity System — cortex-architect Holistic Integration
**Version:** 1.0 | **Created:** 2026-02-05 | **Status:** Implementation Guide

---

## 📋 EXECUTIVE SUMMARY

This guide details how **Phase 24: Architecture Integrity System** integrates with **cortex-architect** to create a holistic defense against:
- ❌ Architectural regression
- ❌ Master plan drift
- ❌ Brittleness accumulation
- ❌ Untracked changes

**Result:** Every change is validated against the master plan, preventing regression and ensuring architectural coherence.

---

## 🎯 INTEGRATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER REQUEST (DESIGN mode)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 0: cortex-architect.prompt.md (v13.0)                    │
│  - Mode Detection (PRE-FLIGHT → AUDIT → DESIGN → DIGEST)        │
│  - Delegates to cortex-architect.md agent                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: PRE-IMPLEMENTATION GATE (NEW - Phase 24)              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ArchitectureGuard.validate_request()                    │   │
│  │ - Load _cortex-master/index.yaml                        │   │
│  │ - Check active phases alignment                         │   │
│  │ - Check completed phases conflicts                      │   │
│  │ - Calculate regression risk score                       │   │
│  │ - Decision: PROCEED | CREATE_PHASE | BLOCK              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌───────────────────┬──────────────────┬───────────────────┐  │
│  │    [PROCEED]      │  [CREATE_PHASE]  │     [BLOCK]       │  │
│  │  Continue flow    │  Offer creation  │  Halt + explain   │  │
│  └───────────────────┴──────────────────┴───────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (if PROCEED)
┌─────────────────────────────────────────────────────────────────┐
│  EXISTING FLOW: LENS Context → Challenge → DoR → Approval       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: RUNTIME REGRESSION GUARD (NEW - Phase 24)             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TDDOrchestrator Hooks                                   │   │
│  │ - Pre-execution: RegressionMonitor.check_phases()       │   │
│  │ - During execution: BrittlenessScanner.scan()           │   │
│  │ - Log violations (non-blocking warnings)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  EXISTING: TDD Execution (RED → GREEN → REFACTOR)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (if all tests pass)
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: POST-COMPLETION SYNC (NEW - Phase 24)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PhaseCompletionOrchestrator.complete_phase()            │   │
│  │ - Update phase YAML (status: completed)                 │   │
│  │ - Regenerate index.yaml statistics                      │   │
│  │ - Trigger PlanRegistrySyncOrchestrator                  │   │
│  │ - Update enhancement-history.yaml                       │   │
│  │ - Dashboard auto-refresh (< 60 seconds)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: ARCHITECTURE EVOLUTION TRACKING (NEW - Phase 24)      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ DecisionJournal.record()                                │   │
│  │ - Decision: What architectural choice                   │   │
│  │ - Rationale: Why (evidence-based)                       │   │
│  │ - Alternatives: What was rejected                       │   │
│  │ - Impact: Affected phases/orchestrators                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 PROMPT MODIFICATIONS

### cortex-architect.prompt.md (Lines ~350-400)

**INSERT AFTER:** "LENS Context Gathering" section  
**BEFORE:** "MANDATORY CHALLENGE FIRST" section

```markdown
## 🛡️ Architecture Integrity Gate (Phase 24)

**CRITICAL:** This gate runs BEFORE Challenge to prevent wasted effort on invalid requests.

### Gate Execution Flow

```
User Request (DESIGN mode)
    ↓
PRE-FLIGHT CHECK (existing) ✅
    ↓
[NEW] ARCHITECTURE INTEGRITY GATE
    ↓
Load cortex-registry/_cortex-master/index.yaml
    ↓
Call: ArchitectureGuard.validate_request({
    request_description: {user_request},
    intent_type: {IMPLEMENT|REFACTOR|FIX|DESIGN},
    scope: {affected_files}
})
    ↓
Receive: {
    verdict: PROCEED | CREATE_PHASE | BLOCK,
    phase_alignment: {...},
    reasoning: "..."
}
    ↓
Display: Phase Alignment Table (MANDATORY)
    ↓
Decision Tree:
    ├─ [PROCEED] → Continue to LENS Context Gathering
    ├─ [CREATE_PHASE] → Offer phase creation flow
    └─ [BLOCK] → Display reasons + HALT execution
```

### Phase Alignment Table (MANDATORY DISPLAY)

**Format:**
```markdown
### 🛡️ Architecture Integrity Check

| Check | Status | Details |
|-------|--------|---------|
| **Active Phase Match** | ✅/❌ | Aligns with: {phase-21, phase-22} |
| **Completed Phase Conflict** | ✅/❌ | No conflicts detected |
| **Regression Risk** | {0.00-1.00} | 🟢 Low / 🟡 Medium / 🔴 High |
| **Brittleness Risk** | {0.00-1.00} | Coupling/complexity analysis |
| **Verdict** | {icon} | {PROCEED / CREATE_PHASE / BLOCK} |

**Reasoning:** {detailed_explanation}
```

### Verdict-Specific Actions

#### PROCEED Verdict
```markdown
**✅ Request Approved**
- Aligns with active phase: {phase-id}
- Regression risk: {score} (acceptable)
- Proceeding to LENS Context Gathering...
```

#### CREATE_PHASE Verdict
```markdown
**📋 Phase Creation Recommended**

This change is significant enough to warrant a new phase in the master plan.

**Suggested Phase:**
- **ID:** phase-{N}
- **Title:** {auto_generated_title}
- **Priority:** {P0/P1/P2/P3}
- **Estimated Effort:** {auto_calculated}

**Options:**
1. Type **"create phase"** to auto-generate phase YAML (recommended)
2. Type **"skip"** to proceed without phase tracking (⚠️ not recommended)
3. Type **"manual"** to manually create phase first

**Note:** Creating a phase ensures this work is tracked in the master plan and dashboard.
```

#### BLOCK Verdict
```markdown
**🚫 Request Blocked**

This change conflicts with completed phase commitments and poses regression risk.

**Conflicts Detected:**
| Phase | Commitment | Conflict |
|-------|-----------|----------|
| phase-{N} | {commitment} | {how_request_violates} |

**Regression Risk Factors:**
- {factor_1}
- {factor_2}
- {factor_3}

**Recommended Actions:**
1. **Modify Request:** {suggested_modification}
2. **Update Phase:** Consider reopening phase-{N} if architecture needs evolution
3. **Architect Review:** Complex change may need architecture committee review

**⏸️ Execution HALTED** — Resolve conflicts before proceeding.
```

---

## 🔧 AGENT MODIFICATIONS

### cortex-architect.md (Lines ~85-120)

**UPDATE:** Master Mode Flow section

**REPLACE:**
```markdown
[DESIGN Mode] → cortex-designer (+ this agent orchestration)
    ↓
LENS Context (cortex_git_history, cortex_lens_analyze)
    ↓
🚨 MANDATORY CHALLENGE FIRST (Never skip!)
```

**WITH:**
```markdown
[DESIGN Mode] → cortex-designer (+ this agent orchestration)
    ↓
[NEW] 🛡️ ARCHITECTURE INTEGRITY GATE (Phase 24)
    ├─ MCP Call: cortex_validate_architecture(request, intent, scope)
    ├─ Display: Phase Alignment Table
    ├─ Verdict: PROCEED | CREATE_PHASE | BLOCK
    └─ If BLOCK: HALT (display remediation)
    ↓ (only if PROCEED)
LENS Context (cortex_git_history, cortex_lens_analyze)
    ↓
🚨 MANDATORY CHALLENGE FIRST (Never skip!)
```

---

## 💻 ORCHESTRATOR INTEGRATION

### TDDOrchestrator Modifications

**File:** `cortex/orchestrators/core/tdd_orchestrator.py`

#### Pre-Execution Hook (Line ~200, start of execute())

```python
def execute(self, context: Dict[str, Any]) -> Result[Any]:
    """
    Execute TDD workflow with Phase 24 integrity checks.
    """
    # [NEW] Phase 24: Pre-execution regression check
    regression_monitor = RegressionMonitor()
    regression_check = regression_monitor.check_completed_phases(
        context=context,
        proposed_changes=context.get('files_to_modify', [])
    )
    
    if regression_check.has_violations():
        self.logger.warning(
            f"⚠️ Regression warnings detected (non-blocking):\n"
            f"{regression_check.format_violations()}"
        )
        # Log to audit trail but don't block
        self.audit_logger.log_event(
            event_type="REGRESSION_WARNING",
            details=regression_check.violations
        )
    
    # [NEW] Phase 24: Initialize brittleness scanner
    brittleness_scanner = BrittlenessScanner()
    
    # ... existing TDD flow (RED → GREEN → REFACTOR) ...
```

#### Post-Execution Hook (Line ~500, after all tests pass)

```python
    # All tests passed ✅
    if test_results.all_passed():
        # [NEW] Phase 24: Run final brittleness scan
        brittleness_result = brittleness_scanner.scan(
            scope=context.get('files_modified', [])
        )
        
        if brittleness_result.score > 0.7:
            self.logger.warning(
                f"⚠️ High brittleness detected (score: {brittleness_result.score:.2f})\n"
                f"Violations: {brittleness_result.violations}"
            )
        
        # [NEW] Phase 24: Trigger phase completion if applicable
        phase_id = context.get('phase_id')
        if phase_id:
            phase_completion = PhaseCompletionOrchestrator()
            completion_result = phase_completion.complete_phase(
                phase_id=phase_id,
                completion_data={
                    'files_modified': context.get('files_modified', []),
                    'tests_passed': test_results.count,
                    'brittleness_score': brittleness_result.score,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            if completion_result.is_ok():
                self.logger.info(
                    f"✅ Phase {phase_id} marked completed\n"
                    f"📊 Dashboard sync triggered\n"
                    f"🔄 Master plan updated"
                )
            else:
                self.logger.error(
                    f"❌ Failed to complete phase {phase_id}: "
                    f"{completion_result.unwrap_err()}"
                )
        
        return Ok({
            'status': 'success',
            'tests_passed': test_results.count,
            'brittleness_score': brittleness_result.score,
            'phase_completed': phase_id is not None
        })
```

---

## 🔌 WIRING INTEGRATION

### wiring.yaml Additions

**File:** `cortex/wiring/specifications/wiring.yaml`

**ADD TO:** Core Orchestrators section

```yaml
# ============================================================================
# PHASE 24: ARCHITECTURE INTEGRITY SYSTEM
# ============================================================================

- name: "ArchitectureGuard"
  path: "cortex.orchestrators.core.architecture_guard"
  class: "ArchitectureGuard"
  version: "1.0.0"
  priority: 900  # High priority (runs before DESIGN)
  category: "core"
  description: "Pre-implementation validation against master plan to prevent regression"
  capabilities:
    - "phase_alignment_validation"
    - "regression_risk_calculation"
    - "completed_phase_conflict_detection"
  mcp_tools:
    - name: "cortex_validate_architecture"
      description: "Validate request against master plan"
      parameters:
        - "request_description"
        - "intent_type"
        - "scope"
  dependencies:
    - "PlanRegistrySyncOrchestrator"
  health_check:
    method: "validate_registry_access"
    timeout_seconds: 5

- name: "BrittlenessScanner"
  path: "cortex.orchestrators.support.brittleness_scanner"
  class: "BrittlenessScanner"
  version: "1.0.0"
  priority: 500
  category: "support"
  description: "Runtime brittleness detection (circular deps, tight coupling)"
  capabilities:
    - "circular_dependency_detection"
    - "coupling_analysis"
    - "abstraction_layer_validation"
  mcp_tools:
    - name: "cortex_scan_brittleness"
      description: "Scan codebase for brittleness patterns"
      parameters:
        - "scope"
  dependencies: []
  health_check:
    method: "check_ast_parser"
    timeout_seconds: 3

- name: "PhaseCompletionOrchestrator"
  path: "cortex.orchestrators.support.phase_completion_orchestrator"
  class: "PhaseCompletionOrchestrator"
  version: "1.0.0"
  priority: 100  # Low priority (runs after TDD)
  category: "support"
  description: "Post-completion master plan sync and dashboard update"
  capabilities:
    - "phase_status_update"
    - "dashboard_sync_trigger"
    - "enhancement_history_recording"
  mcp_tools:
    - name: "cortex_complete_phase"
      description: "Mark phase as completed and sync dashboard"
      parameters:
        - "phase_id"
        - "completion_data"
  dependencies:
    - "PlanRegistrySyncOrchestrator"
  health_check:
    method: "validate_registry_write_access"
    timeout_seconds: 5

- name: "DecisionJournal"
  path: "cortex.orchestrators.support.decision_journal"
  class: "DecisionJournal"
  version: "1.0.0"
  priority: 200
  category: "support"
  description: "Architecture decision recording and tracking"
  capabilities:
    - "decision_recording"
    - "rationale_capture"
    - "impact_tracking"
  mcp_tools:
    - name: "cortex_record_decision"
      description: "Record architectural decision with rationale"
      parameters:
        - "decision"
        - "rationale"
        - "alternatives"
        - "impact"
  dependencies: []
  health_check:
    method: "validate_journal_directory"
    timeout_seconds: 2
```

---

## 📊 MCP TOOL SPECIFICATIONS

### cortex_validate_architecture

**Purpose:** Pre-implementation validation against master plan

**Parameters:**
```typescript
{
  request_description: string;  // User's change request
  intent_type: "IMPLEMENT" | "REFACTOR" | "FIX" | "DESIGN";
  scope?: string[];  // Affected files (optional)
}
```

**Returns:**
```typescript
{
  verdict: "PROCEED" | "CREATE_PHASE" | "BLOCK";
  phase_alignment: {
    active_phases: string[];  // e.g., ["phase-21", "phase-22"]
    conflicts: string[];      // e.g., ["phase-15: No SCREAMING_CASE"]
    regression_risk: number;  // 0.0-1.0
    brittleness_risk: number; // 0.0-1.0
  };
  reasoning: string;
  suggested_phase?: {         // Only if verdict = CREATE_PHASE
    id: string;
    title: string;
    priority: string;
    estimated_effort: string;
  };
}
```

**Example:**
```json
{
  "verdict": "BLOCK",
  "phase_alignment": {
    "active_phases": ["phase-21", "phase-22"],
    "conflicts": [
      "phase-15: Committed to kebab-case filenames, request uses SCREAMING_CASE"
    ],
    "regression_risk": 0.85,
    "brittleness_risk": 0.45
  },
  "reasoning": "Request introduces SCREAMING_CASE files, violating phase-15 commitment to kebab-case naming convention. High regression risk.",
  "suggested_phase": null
}
```

---

## 🧪 TESTING STRATEGY

### Unit Tests

**File:** `tests/unit/orchestrators/core/test_architecture_guard.py`

```python
def test_architecture_guard_allows_aligned_request():
    """Test that ArchitectureGuard allows requests aligned with active phases."""
    guard = ArchitectureGuard()
    result = guard.validate_request(
        request_description="Add JSON serialization to phase-21 data layer",
        intent_type="IMPLEMENT",
        scope=["cortex/visualization/json_data_generator.py"]
    )
    assert result.verdict == "PROCEED"
    assert result.phase_alignment.regression_risk < 0.3

def test_architecture_guard_blocks_contradictory_request():
    """Test that ArchitectureGuard blocks requests contradicting completed phases."""
    guard = ArchitectureGuard()
    result = guard.validate_request(
        request_description="Use SCREAMING_CASE for new config file",
        intent_type="IMPLEMENT",
        scope=["cortex/config/NEW_CONFIG.py"]
    )
    assert result.verdict == "BLOCK"
    assert len(result.phase_alignment.conflicts) > 0
    assert "phase-15" in str(result.phase_alignment.conflicts)  # Naming convention phase

def test_architecture_guard_suggests_phase_creation():
    """Test that ArchitectureGuard suggests phase creation for significant changes."""
    guard = ArchitectureGuard()
    result = guard.validate_request(
        request_description="Convert entire orchestrator system to async/await",
        intent_type="REFACTOR",
        scope=["cortex/orchestrators/**/*.py"]
    )
    assert result.verdict == "CREATE_PHASE"
    assert result.suggested_phase is not None
    assert result.suggested_phase.priority in ["P0", "P1"]
```

### Integration Tests

**File:** `tests/integration/test_architecture_integrity_flow.py`

```python
def test_design_mode_calls_architecture_guard():
    """Test that cortex-architect DESIGN mode calls ArchitectureGuard."""
    # Simulate DESIGN mode entry
    context = {
        'mode': 'DESIGN',
        'request': 'Refactor MasterOrchestrator',
        'intent': 'REFACTOR'
    }
    
    # Mock ArchitectureGuard
    with patch('cortex.orchestrators.core.architecture_guard.ArchitectureGuard') as MockGuard:
        mock_guard = MockGuard.return_value
        mock_guard.validate_request.return_value = {
            'verdict': 'PROCEED',
            'phase_alignment': {...}
        }
        
        # Execute design flow
        result = cortex_architect_execute(context)
        
        # Verify ArchitectureGuard was called
        mock_guard.validate_request.assert_called_once()
        assert result['phase_alignment_checked'] is True

def test_blocked_request_halts_execution():
    """Test that BLOCK verdict prevents execution."""
    context = {
        'mode': 'DESIGN',
        'request': 'Use SCREAMING_CASE for files',
        'intent': 'IMPLEMENT'
    }
    
    result = cortex_architect_execute(context)
    
    assert result['status'] == 'BLOCKED'
    assert 'reasoning' in result
    assert result['execution_started'] is False
```

---

## ✅ VALIDATION CHECKLIST

Before considering Phase 24 complete, verify:

### Core Functionality
- [ ] ArchitectureGuard validates against index.yaml
- [ ] Regression risk calculation accurate (< 5% false positives)
- [ ] BLOCK verdict prevents execution
- [ ] CREATE_PHASE offers auto-generation
- [ ] BrittlenessScanner detects circular dependencies
- [ ] TDDOrchestrator calls pre/post hooks
- [ ] PhaseCompletionOrchestrator updates phase YAML
- [ ] Dashboard reflects completed phases (< 60s)

### Integration Points
- [ ] cortex-architect.prompt.md updated with gate flow
- [ ] cortex-architect.md agent routes correctly
- [ ] Phase Alignment Table displays properly
- [ ] MCP tools registered in wiring.yaml
- [ ] All 4 orchestrators wired correctly

### Testing
- [ ] 100% test coverage for ArchitectureGuard
- [ ] Integration tests pass
- [ ] E2E test: DESIGN → Block → Remediate → Success
- [ ] Performance: ArchitectureGuard < 100ms

### Documentation
- [ ] Phase 24 YAML complete
- [ ] Integration guide (this doc) finalized
- [ ] MCP tool specs documented
- [ ] Architecture decision recorded

---

## 🚀 ROLLOUT SEQUENCE

### Day 1: Layer 1 (Pre-Implementation Gate)
1. Implement ArchitectureGuard orchestrator
2. Add unit tests
3. Update cortex-architect.prompt.md (gate section)
4. Update cortex-architect.md (routing logic)
5. Test manually with sample requests

### Day 2: Layer 1 Completion
1. Implement MCP tool: cortex_validate_architecture
2. Wire ArchitectureGuard in wiring.yaml
3. Integration tests
4. Document MCP tool

### Day 3: Layer 2 (Runtime Regression Guard)
1. Implement BrittlenessScanner orchestrator
2. Implement RegressionMonitor
3. Add TDDOrchestrator pre-execution hook
4. Unit tests

### Day 4: Layer 2 Completion
1. Wire BrittlenessScanner
2. Integration tests with TDD flow
3. Validate brittleness detection accuracy

### Day 5: Layer 3 (Post-Completion Sync)
1. Implement PhaseCompletionOrchestrator
2. Add TDDOrchestrator post-completion hook
3. Test dashboard sync

### Day 6: Layer 4 (Decision Journal)
1. Implement DecisionJournal
2. Add cortex-architect decision capture
3. Test end-to-end

### Day 7: Final Testing & Documentation
1. E2E tests
2. Performance validation
3. Update all documentation
4. Prepare merge to main

---

## 📈 SUCCESS METRICS

### Functional Metrics
- **Regression Prevention:** 0 regressions in 30 days post-deployment
- **Phase Sync Accuracy:** 100% (master plan matches implementation)
- **Dashboard Latency:** < 60 seconds from completion to dashboard update
- **False Positive Rate:** < 5% (ArchitectureGuard blocks valid requests)

### Performance Metrics
- **ArchitectureGuard Latency:** < 100ms per validation
- **BrittlenessScanner Latency:** < 500ms per scan
- **Phase Completion Latency:** < 2 seconds

### User Experience Metrics
- **Gate Clarity:** > 90% user understanding of block reasons
- **Remediation Success:** > 80% blocked requests successfully remediated
- **Phase Creation Adoption:** > 70% CREATE_PHASE verdicts result in phase creation

---

## 🔮 FUTURE ENHANCEMENTS

### Phase 24.1: AI-Powered Regression Prediction
- Train ML model on historical changes → regression outcomes
- Improve regression risk calculation accuracy to > 99%

### Phase 24.2: Visual Architecture Diff
- Before/after component diagrams
- Dependency graph visualization

### Phase 24.3: Multi-Phase Impact Analysis
- Show downstream phase impacts
- Dependency chain visualization

---

**Status:** ✅ INTEGRATION GUIDE COMPLETE  
**Next:** Begin Phase 24 implementation (Day 1: ArchitectureGuard)  
**Approval:** Awaiting user confirmation to proceed
