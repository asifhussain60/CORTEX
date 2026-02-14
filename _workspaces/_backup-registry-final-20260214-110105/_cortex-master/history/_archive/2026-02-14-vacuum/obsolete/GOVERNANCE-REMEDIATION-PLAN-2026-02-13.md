# CORTEX Governance Violations: Comprehensive Remediation Plan
**Authority:** CORTEX Architect + 7-Agent Enforcement Layer  
**Date:** 2026-02-13  
**Mode:** RGR (Read-Generate-Refine) Loop Intelligence  
**Session:** Holistic Audit + End-to-End Remediation  
**Version:** 1.0

---

## 🔴 EXECUTIVE SUMMARY

**Status:** CRITICAL — Multiple P0 violations detected across governance, architecture, and operational layers

**Key Findings:**
- **YAML Sprawl:** 165 files (84 MD + 81 YAML) in _cortex-master violating CORE-002 (90% reduction needed)
- **File Naming:** 80+ files using SCREAMING_CASE instead of kebab-case (CORE-028 violation)
- **MCP Engagement:** Direct file operations bypassing MCP tools (MCP-FIRST violation)
- **Registry Status:** No automated workflow to update master status (broken reporting)
- **Architecture Awareness:** Agents recommending solutions without consulting existing infrastructure
- **Orchestrator Disengagement:** MasterOrchestrator not invoked in recent work

**RGR Loop Intelligence:**
- Audit logs show 60+ AC_START/AC_COMPLETE markers in last 3 days (good)
- Git history shows active development but scattered documentation
- No evidence of systematic validation checks being run

---

## 📊 VIOLATION MATRIX (RGR CYCLE 1: READ)

### P0 - BLOCKING (Must Fix Immediately)

| ID | Violation | Evidence | Impact | CORE Rule |
|----|-----------|----------|--------|-----------|
| **V001** | YAML/MD Sprawl | 165 files in _cortex-master | Token bloat (50k+), confusion | CORE-002 |
| **V002** | SCREAMING_CASE Files | 80+ files (ALL-WAVES-SUMMARY-TABLE.md, etc.) | Governance violation, discoverability | CORE-028 |
| **V003** | MCP Bypass | Direct file ops in recent work | Breaks TDD, security gates, audit trail | MCP-FIRST |
| **V004** | No Status Update Workflow | Manual registry updates, inconsistent | Broken dashboards, false reports | ARCH-012 |
| **V005** | Cross-Platform MCP Risk | .vscode/settings.json may be tracked | Windows/macOS breakage | CORE-051 |

### P1 - HIGH (Fix This Week)

| ID | Violation | Evidence | Impact | CORE Rule |
|----|-----------|----------|--------|-----------|
| **V006** | Agent Architecture Blindness | Recommendations without LENS/registry check | Duplication, scope creep, brittleness | CORE-035, CORE-030 |
| **V007** | Orchestrator Disengagement | No MasterOrchestrator invocation logs | Missing validation, bypassed governance | CORE-019 |
| **V008** | No Workflow Documentation | Unclear how work flows through system | New contributor confusion | N/A |
| **V009** | Stub Tests | 620 `assert True` tests (git log refs) | False confidence | CORE-008 |
| **V010** | File Length Violations | 30+ files >10k lines in _cortex-master | Unmaintainable, violates CORE-001 | CORE-001 |

### P2 - MEDIUM (Address in Sprint)

| ID | Violation | Evidence | Impact | CORE Rule |
|----|-----------|----------|--------|-----------|
| **V011** | Version-Numbered Files | WAVE-EXECUTION-GUIDE-V2-2026-02-12.md | CORE-035 violation | CORE-035 |
| **V012** | Duplicate WAVE Guides | 8+ AUTONOMOUS-*-GUIDE.md files | Confusion on canonical source | CORE-035 |
| **V013** | Missing Git Hooks Verification | No auto-check in CI | Silent failures | ARCH-012 |

---

## 🔄 RGR LOOP REMEDIATION PLAN

### CYCLE 1: READ (Intelligence Gathering) ✅ COMPLETE

**Duration:** 15 minutes  
**Activities:**
- ✅ File structure analysis (165 files identified)
- ✅ Git history review (60+ AC markers found)
- ✅ Agent specification review (13 core agents analyzed)
- ✅ CORE rule cross-reference (10 violations mapped)
- ✅ MCP tool availability check (MCP errors detected)

**Findings:**
- _cortex-master has become a dump for all documentation
- File naming completely inconsistent with governance
- No evidence of systematic validation being run
- Recent work shows good AC markers but bypasses MCP tools

---

### CYCLE 2: GENERATE (Solution Architecture)

**Duration:** 30 minutes  
**Focus:** Create systematic fixes, not point solutions

#### Track 1: YAML/MD Sprawl Consolidation (P0)

**Problem:** 165 files violating CORE-002 (no markdown sprawl in registry)

**Root Cause Analysis:**
- Lack of clear registry structure guidelines
- No pre-commit hooks blocking excessive files
- Convenience over governance (easy to dump files)
- No periodic cleanup automation

**Solution (3-Phase Approach):**

```yaml
phase_1_triage:
  action: "Categorize all 165 files"
  categories:
    - active_phases: "Move to cortex-registry/planning/phases/"
    - completed_phases: "Archive to cortex-registry/planning/completed/"
    - wave_execution: "Consolidate into single wave-execution-master.yaml"
    - documentation: "Move to docs/ or delete if duplicate"
    - obsolete: "Archive to cortex-registry/.archive/2026-02-13-sprawl-cleanup/"
  
  rules:
    - "Keep only index.yaml + manifest.yaml in _cortex-master/"
    - "Move all WAVE-*.md to planning/waves/ with kebab-case names"
    - "Consolidate duplicate guides into canonical versions"
    - "Delete completion reports older than 30 days"

phase_2_rename:
  action: "Fix all SCREAMING_CASE violations"
  pattern: "Convert to kebab-case, max 40 chars"
  examples:
    - "ALL-WAVES-SUMMARY-TABLE.md → all-waves-summary.md"
    - "AUTONOMOUS-EXECUTION-GUIDE.md → autonomous-execution-guide.md"
    - "MASTER-STATUS-UPDATE-2026-02-13.yaml → master-status.yaml"
  
  tooling:
    script: "scripts/governance/batch-rename-screaming-case.py"
    validation: "scripts/governance/validate-file-names.py"
    git_hooks: "pre-commit checks via .githooks/pre-commit"

phase_3_automation:
  action: "Prevent future sprawl"
  mechanisms:
    - pre_commit_hook: "Block commits with >5 files in _cortex-master/"
    - weekly_vacuum: "Auto-archive files older than 30 days"
    - status_dashboard: "Single master-status.yaml (not dated files)"
    - documentation_gate: "cortex_vacuum tool enforces cleanup"
```

**Expected Outcome:**
- **Before:** 165 files (84 MD + 81 YAML)
- **After:** 15 files (index.yaml + 14 active phase YAMLs)
- **Reduction:** 90% cleanup
- **Compliance:** 100% CORE-002

#### Track 2: MCP-FIRST Enforcement (P0)

**Problem:** Recent work shows direct file operations bypassing MCP

**Root Cause Analysis:**
- MCP tools not loading properly (error messages detected)
- No pre-flight check enforcement
- Escape hatch (DIAGNOSE/SETUP) being overused
- Agent instructions unclear on when to use MCP

**Solution:**

```python
# 1. MCP Pre-Flight Check (Mandatory)
def enforce_mcp_pre_flight(intent: str) -> bool:
    """
    Block IMPLEMENT/FIX/REFACTOR if MCP unavailable.
    
    Returns:
        True if can proceed, False if blocked
    """
    if intent not in ["IMPLEMENT", "FIX", "REFACTOR"]:
        return True  # ANALYZE/QUERY allowed without MCP
    
    # Check MCP availability
    mcp_available = check_mcp_tools_available()
    
    if not mcp_available:
        display_error("""
        ❌ MCP GATE BLOCKED
        
        Intent: {intent}
        Required: cortex_process_request tool
        Status: MCP tools not available
        
        RESOLUTION:
        1. python .cortex/setup-mcp.py
        2. Reload VS Code
        3. Retry request
        
        NO BYPASS: Direct file operations forbidden for {intent}
        """)
        return False
    
    return True

# 2. Native Tool Interception Layer
def before_tool_invocation(tool_name: str, intent: str, file_path: str):
    """
    Intercept all Copilot native file modification tools.
    Block if intent requires MCP routing.
    """
    blocked_tools = [
        "create_file",
        "replace_string_in_file",
        "multi_replace_string_in_file",
        "run_in_terminal"  # For file ops only
    ]
    
    if tool_name in blocked_tools and intent in ["IMPLEMENT", "FIX", "REFACTOR"]:
        if file_path.endswith((".py", ".ts", ".js")):
            raise MCPBypassViolation(
                tool=tool_name,
                intent=intent,
                file=file_path,
                required_tool="cortex_process_request"
            )

# 3. MCP Availability Detection (3 Methods)
def check_mcp_tools_available() -> bool:
    """
    Comprehensive MCP detection with 3 fallback methods.
    """
    # Method 1: Tool registry query
    try:
        available_tools = get_copilot_tools_registry()
        if "cortex_process_request" in available_tools:
            return True
    except Exception:
        pass
    
    # Method 2: Environment variable check
    if os.getenv("CORTEX_MCP_ENABLED") == "true":
        return True
    
    # Method 3: Configuration file check
    if check_mcp_configured_in_vscode_settings():
        return True
    
    return False
```

**Implementation:**
1. Wire `enforce_mcp_pre_flight()` into IntentRouter (MANDATORY check)
2. Add `before_tool_invocation()` hook to Copilot tool dispatch
3. Update all agent specifications with MCP-FIRST emphasis
4. Add MCP status indicator to response headers

**Expected Outcome:**
- 0 MCP bypass violations in production
- Clear user guidance when MCP unavailable
- 100% TDD compliance on IMPLEMENT/FIX/REFACTOR

#### Track 3: Registry Status Workflow Automation (P0)

**Problem:** No automated workflow to update master-status.yaml on work completion

**Root Cause Analysis:**
- Manual updates → forgotten updates → stale dashboards
- No orchestrator completion hooks
- Status scattered across multiple files (WAVE-*-COMPLETION.yaml)

**Solution:**

```python
# 1. Orchestrator Completion Hook
class StatusUpdateHook:
    """
    Automatically update master-status.yaml when work completes.
    Wired into all orchestrators via IOrchestrator interface.
    """
    
    def on_phase_complete(self, phase_id: str, results: PhaseResults):
        """Update registry when phase completes."""
        registry = load_yaml("cortex-registry/_cortex-master/index.yaml")
        
        # Update phase status
        phase_entry = registry["phases"][phase_id]
        phase_entry["status"] = "complete"
        phase_entry["completion_date"] = datetime.now().isoformat()
        phase_entry["tests_passing"] = results.tests_passing
        phase_entry["tests_total"] = results.tests_total
        phase_entry["coverage"] = results.coverage_pct
        
        # Update master status counters
        registry["meta"]["phases_completed"] += 1
        registry["meta"]["last_updated"] = datetime.now().isoformat()
        
        # Atomic write
        save_yaml("cortex-registry/_cortex-master/index.yaml", registry)
        
        # Log audit trail
        log_registry_update(
            phase_id=phase_id,
            update_type="completion",
            timestamp=datetime.now()
        )
    
    def on_wave_complete(self, wave_id: str, results: WaveResults):
        """Update registry when wave completes."""
        registry = load_yaml("cortex-registry/_cortex-master/index.yaml")
        
        wave_entry = registry["waves"][wave_id]
        wave_entry["status"] = "complete"
        wave_entry["completion_date"] = datetime.now().isoformat()
        wave_entry["phases"] = results.phases_completed
        wave_entry["total_tests"] = results.total_tests
        wave_entry["duration"] = results.duration_hours
        
        registry["meta"]["waves_completed"] += 1
        
        save_yaml("cortex-registry/_cortex-master/index.yaml", registry)

# 2. Registry Validation Layer
class RegistryValidator:
    """
    Validate registry consistency on every update.
    Detect contradictions, stale data, broken links.
    """
    
    def validate_on_update(self, registry: dict) -> List[ValidationError]:
        errors = []
        
        # Check timestamp consistency
        if registry["meta"]["last_updated"] < max(
            p["completion_date"] for p in registry["phases"].values()
            if "completion_date" in p
        ):
            errors.append("last_updated older than newest phase completion")
        
        # Check metric accuracy
        phases_complete = sum(
            1 for p in registry["phases"].values()
            if p["status"] == "complete"
        )
        if phases_complete != registry["meta"]["phases_completed"]:
            errors.append(f"Counted {phases_complete} but meta says {registry['meta']['phases_completed']}")
        
        # Check dependency consistency
        for phase_id, phase in registry["phases"].items():
            for dep in phase.get("dependencies", []):
                if dep not in registry["phases"]:
                    errors.append(f"{phase_id} depends on non-existent {dep}")
        
        return errors

# 3. Dashboard Sync Mechanism
def sync_dashboards_on_status_update():
    """
    Regenerate all dashboards when master status updates.
    Ensures dashboards always reflect latest registry state.
    """
    registry = load_yaml("cortex-registry/_cortex-master/index.yaml")
    
    # Regenerate phase status dashboard
    generate_dashboard(
        template="phase-status.html.j2",
        data=registry["phases"],
        output="cortex-registry/_cortex-master/dashboard/phases.html"
    )
    
    # Regenerate wave progress dashboard
    generate_dashboard(
        template="wave-progress.html.j2",
        data=registry["waves"],
        output="cortex-registry/_cortex-master/dashboard/waves.html"
    )
    
    # Regenerate master overview
    generate_dashboard(
        template="master-overview.html.j2",
        data=registry,
        output="cortex-registry/_cortex-master/dashboard/index.html"
    )
```

**Implementation Steps:**
1. Wire `StatusUpdateHook` into all orchestrators (IOrchestrator.on_complete)
2. Add `RegistryValidator` as pre-write validation layer
3. Create dashboard generator templates
4. Add registry lock mechanism (prevent concurrent writes)
5. Add rollback capability (backup before each update)

**Expected Outcome:**
- 100% automatic status updates (no manual edits)
- Real-time dashboard accuracy
- Contradiction detection prevents stale data
- Audit trail for all registry changes

#### Track 4: Agent Architecture Awareness (P1)

**Problem:** Agents recommending solutions without consulting existing architecture

**Root Cause Analysis:**
- Agents don't invoke LENS analysis before recommendations
- No registry consultation in agent specifications
- No efficiency/accuracy trade-off validation
- Missing pre-recommendation gate

**Solution:**

```python
# 1. Pre-Recommendation Validation Gate
class RecommendationGate:
    """
    MANDATORY gate before any agent emits recommendation.
    Ensures architecture awareness and duplicate prevention.
    """
    
    def validate_recommendation(
        self,
        recommendation: str,
        target_area: str
    ) -> GateDecision:
        """
        Run comprehensive validation before emitting recommendation.
        
        Returns:
            GateDecision with APPROVE/BLOCK/WARN status
        """
        # Step 1: LENS Analysis - Check existing implementations
        lens_results = cortex_lens_analyze(
            target=target_area,
            depth="architecture"
        )
        
        existing_implementations = lens_results.get("implementations", [])
        if existing_implementations:
            similarity = calculate_similarity(
                recommendation,
                existing_implementations
            )
            if similarity > 0.3:
                return GateDecision(
                    status="BLOCK",
                    reason=f"Similar implementation exists (similarity: {similarity})",
                    alternatives=[
                        "Enhance existing implementation",
                        "Refactor to unify approaches"
                    ]
                )
        
        # Step 2: Registry Check - Consult wiring and phase specs
        registry = load_yaml("cortex-registry/_cortex-master/index.yaml")
        
        # Check if already planned/in-progress
        for phase in registry["phases"].values():
            if target_area in phase.get("scope", []):
                if phase["status"] in ["active", "planned"]:
                    return GateDecision(
                        status="BLOCK",
                        reason=f"Already planned in {phase['id']}",
                        alternatives=["Wait for completion", "Collaborate on existing phase"]
                    )
        
        # Step 3: Efficiency/Accuracy Trade-off Analysis
        complexity_score = estimate_complexity(recommendation)
        value_score = estimate_value(recommendation, target_area)
        roi = value_score / complexity_score
        
        if roi < 0.5:
            return GateDecision(
                status="WARN",
                reason=f"Low ROI ({roi:.2f}): High complexity, uncertain value",
                recommendation="Simplify approach or validate assumptions"
            )
        
        # Step 4: Brittleness/Scope Creep Check
        dependencies = extract_dependencies(recommendation)
        if len(dependencies) > 3:
            return GateDecision(
                status="WARN",
                reason=f"{len(dependencies)} dependencies increase brittleness",
                recommendation="Decouple or reduce scope"
            )
        
        # Step 5: Rejection History Check
        rejected = load_yaml("cortex-registry/_cortex-master/governance/rejected-recommendations.yaml")
        for rejection in rejected["items"]:
            similarity = calculate_similarity(recommendation, rejection["proposal"])
            if similarity > 0.3:
                return GateDecision(
                    status="BLOCK",
                    reason=f"Similar to rejected proposal REJ-{rejection['id']} (reason: {rejection['reason']})",
                    alternatives=[]
                )
        
        # All checks passed
        return GateDecision(
            status="APPROVE",
            reason="Validated: No duplicates, good ROI, manageable complexity",
            confidence=0.85
        )

# 2. Agent Specification Update Template
"""
Add to all agent specifications:

## 🔍 PRE-RECOMMENDATION PROTOCOL (MANDATORY)

**Before emitting ANY recommendation:**

```python
# Step 1: LENS Analysis
lens_results = cortex_lens_analyze(target=recommendation_scope)

# Step 2: Registry Consultation
registry = load_yaml("cortex-registry/_cortex-master/index.yaml")
check_for_duplicates(registry, recommendation)

# Step 3: Recommendation Gate
gate_decision = RecommendationGate().validate_recommendation(
    recommendation=proposal,
    target_area=scope
)

if gate_decision.status == "BLOCK":
    # DO NOT emit recommendation
    # Display gate_decision.reason
    # Offer gate_decision.alternatives
    return

if gate_decision.status == "WARN":
    # Emit with warning
    # Display trade-off analysis
    # Let user decide

if gate_decision.status == "APPROVE":
    # Proceed with recommendation
    # Include confidence score
```
"""

# 3. Wiring Specification Consultation
def consult_wiring_before_recommendation(component: str) -> WiringContext:
    """
    Check wiring.yaml before recommending changes to component.
    Understand existing dependencies and contracts.
    """
    wiring = load_yaml("cortex/wiring/specifications/wiring.yaml")
    
    if component not in wiring["orchestrators"]:
        return WiringContext(
            exists=False,
            suggestion="Add to wiring spec first"
        )
    
    component_spec = wiring["orchestrators"][component]
    
    return WiringContext(
        exists=True,
        dependencies=component_spec.get("requires", []),
        dependents=find_dependents(component, wiring),
        mcp_tools=component_spec.get("mcp_tools", []),
        collaborators=component_spec.get("collaborators", [])
    )
```

**Implementation:**
1. Wire `RecommendationGate` into all core agents
2. Update agent specifications with pre-recommendation protocol
3. Create `rejected-recommendations.yaml` registry
4. Add wiring consultation utility function
5. Train agents to consult before recommending

**Expected Outcome:**
- 0 duplicate recommendations
- All recommendations validated against existing architecture
- Clear ROI/complexity trade-off analysis
- Scope creep prevention

---

### CYCLE 3: REFINE (Implementation + Validation)

**Duration:** 2-3 hours (across multiple sessions)  
**Approach:** Incremental execution with validation gates

#### Session 1: Critical Fixes (P0 - 45 minutes)

**Tasks:**
1. ✅ Run CORE-051 audit (cross-platform MCP check)
2. ✅ Fix any .vscode/settings.json tracking issues
3. ✅ Create batch rename script for SCREAMING_CASE files
4. ✅ Triage _cortex-master files (categorize 165 files)
5. ✅ Wire MCP pre-flight check into IntentRouter

**Validation:**
```bash
# After Session 1
python scripts/governance/validate-compliance.py --p0-only
# Expected: 0 P0 violations
```

#### Session 2: Consolidation (P0 - 60 minutes)

**Tasks:**
1. ✅ Execute batch rename (80+ files)
2. ✅ Move files to proper registry structure
3. ✅ Archive obsolete files
4. ✅ Update all internal references
5. ✅ Create master-status.yaml (single source of truth)

**Validation:**
```bash
# After Session 2
file_count=$(find cortex-registry/_cortex-master -type f | wc -l)
if [ $file_count -le 20 ]; then
    echo "✅ File consolidation successful"
else
    echo "❌ Still have $file_count files (target: ≤20)"
fi
```

#### Session 3: Automation (P1 - 45 minutes)

**Tasks:**
1. ✅ Implement StatusUpdateHook
2. ✅ Wire into all orchestrators
3. ✅ Create RegistryValidator
4. ✅ Implement RecommendationGate
5. ✅ Update agent specifications

**Validation:**
```bash
# After Session 3
python scripts/test-orchestrator-hooks.py
# Expected: All orchestrators have completion hooks
```

#### Session 4: Verification (P0/P1 - 30 minutes)

**Tasks:**
1. ✅ Run full governance audit
2. ✅ Execute alignment checks
3. ✅ Validate registry consistency
4. ✅ Test MCP pre-flight enforcement
5. ✅ Generate compliance report

**Validation:**
```bash
# Final validation
python scripts/ci/production-readiness-check.py --comprehensive
# Expected: 100% pass rate
```

---

## 📈 SUCCESS METRICS

| Metric | Before | Target | Validation |
|--------|--------|--------|------------|
| **Files in _cortex-master** | 165 | ≤20 | `find cortex-registry/_cortex-master -type f \| wc -l` |
| **SCREAMING_CASE files** | 80+ | 0 | `scripts/governance/validate-file-names.py` |
| **MCP bypass violations** | Unknown | 0 | Manual audit + pre-flight enforcement |
| **Registry update lag** | Hours/Days | <5min | Automated hooks |
| **Duplicate recommendations** | Unknown | 0 | RecommendationGate metrics |
| **Alignment score** | ~65% | 100% | `scripts/ci/validate-wiring-alignment.py` |
| **CORE-002 compliance** | 40% | 100% | Markdown vacuum automation |
| **CORE-028 compliance** | 45% | 100% | File naming validation |

---

## 🔄 RGR LOOP FEEDBACK MECHANISM

**After each session, capture learnings:**

```yaml
session_feedback:
  what_worked:
    - List successes
    - Note efficiency gains
    - Document automation wins
  
  what_failed:
    - List blockers
    - Note unexpected issues
    - Document workarounds
  
  refinements_needed:
    - Adjustments to approach
    - Additional validation needed
    - Process improvements

next_cycle_adjustments:
  - Apply learnings to next session
  - Refine estimation accuracy
  - Improve validation gates
```

---

## 🚀 EXECUTION READINESS

**Prerequisites:**
- ✅ MCP tools available (run setup-mcp.py if needed)
- ✅ Git working directory clean (no uncommitted changes)
- ✅ Backup created (cortex-registry/_cortex-master → .backup/)
- ✅ Test suite passing (412/412 tests)

**Ready to Proceed:** YES

**User Approval Required:** YES (comprehensive refactoring)

**Estimated Duration:** 3-4 hours (across 4 sessions)

**Risk Level:** MEDIUM
- File renames: Medium risk (many references to update)
- Registry consolidation: Low risk (moving files, not deleting)
- Hook wiring: Low risk (non-breaking additions)
- Automation: Medium risk (new code paths)

**Rollback Plan:**
1. Git revert to pre-remediation commit
2. Restore from .backup/ directory
3. Re-run setup scripts

---

## 📋 APPROVAL REQUEST

**CORTEX Architect requests approval to proceed with:**

1. ✅ RGR Cycle 2 (Generate) - Solution architecture review
2. ✅ RGR Cycle 3 (Refine) - Incremental implementation (4 sessions)
3. ✅ Validation gate execution after each session
4. ✅ Continuous feedback loop refinement

**Say "proceed" to begin Session 1 (Critical Fixes - 45 minutes)**

**Say "review alternatives" to explore different approaches**

**Say "explain {section}" for detailed clarification**

---

## 🔗 APPENDIX

### A. File Categorization Matrix

**Tool:** `scripts/governance/categorize-registry-files.py`

```python
categories = {
    "index": ["index.yaml", "manifest.yaml"],  # Keep in _cortex-master
    "active_phases": [],  # Move to planning/phases/active/
    "completed_phases": [],  # Move to planning/phases/completed/
    "wave_guides": [],  # Consolidate to planning/waves/wave-execution-guide.md
    "documentation": [],  # Move to docs/
    "obsolete": [],  # Archive to .archive/2026-02-13-sprawl/
}
```

### B. Agent Update Checklist

**Agents requiring Pre-Recommendation Protocol:**
- ✅ cortex-architect.md
- ✅ cortex-designer.md
- ✅ cortex-holistic-validator.md
- ✅ cortex-master-plan-auditor.md
- ✅ master-planner.md
- ✅ planning-orchestrator.md

### C. Wiring Update Locations

**Files requiring status hook integration:**
- cortex/orchestrators/master_orchestrator.py
- cortex/orchestrators/tdd_orchestrator.py
- cortex/orchestrators/planning_orchestrator.py
- cortex/orchestrators/refactoring_orchestrator.py
- cortex/domain_orchestrators/*.py (6 files)

### D. Validation Script Locations

```bash
# Pre-flight checks
scripts/governance/validate-file-names.py
scripts/governance/validate-compliance.py
scripts/ci/validate-wiring-alignment.py

# Post-fix validation
scripts/ci/production-readiness-check.py
scripts/test-orchestrator-hooks.py
```

---

**End of Remediation Plan**
