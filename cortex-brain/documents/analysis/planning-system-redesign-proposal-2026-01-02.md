# Planning System Redesign Proposal - Robust Architecture Foundation

**Date:** January 2, 2026  
**Scope:** Complete Planning System Redesign (CORTEX 4.0 → 5.0)  
**Author:** CORTEX Development Team  
**Priority:** 🔴 CRITICAL - Current System Fragile & Non-Compliant  
**Status:** PROPOSAL - Awaiting Review

---

## 🎯 Executive Summary

The current Planning System (4.0) is **fundamentally fragile** due to:

1. **Broken Hand-Off Protocol** - CORTEX interprets 🛡️ AUTONOMOUS directives instead of delegating to orchestrator
2. **Governance Bypasses** - Manual plans skip Phase -1, comprehensive REFACTOR, and validation
3. **Split Responsibility** - Unclear boundaries between CORTEX (router) and Orchestrator (executor)
4. **Template Ambiguity** - `autonomous_execution_progress` template not properly enforced
5. **No Fail-Safe Mechanisms** - System degrades silently when violations occur

**Compliance Score:** 6.8/10 (FAIL - requires ≥8.0)

**Recommendation:** Complete redesign with **Autonomous Orchestrator Pattern** that eliminates CORTEX from execution loop.

---

## 🔍 Root Cause Analysis

### 1. Hand-Off Protocol Failure

**Current Behavior:**
```yaml
User: "/CORTEX Plan user authentication"
Expected: 🛡️ Orchestrator takes over → Creates plan autonomously
Actual: CORTEX reads CORTEX.prompt.md → Creates plan manually → Bypasses orchestrator
```

**Root Causes:**

#### A. Ambiguous "STOP" Directive
**Source:** `.github/prompts/CORTEX.prompt.md:82-93`

```markdown
**FORBIDDEN Behaviors for 🛡️ AUTONOMOUS Orchestrators:**
1. ❌ Do NOT read the manifest and execute instructions yourself
2. ❌ Do NOT provide guidance based on manifest content
3. ❌ Do NOT implement features after detecting planning intent
4. ❌ Do NOT continue after loading the orchestrator
5. ❌ Do NOT summarize what the orchestrator will do

**REQUIRED Behaviors for 🛡️ AUTONOMOUS Orchestrators:**
1. ✅ Load manifest/orchestrator reference ONLY
2. ✅ Use specified response template (e.g., `autonomous_execution_progress`)
3. ✅ STOP immediately after hand-off header
4. ✅ Let orchestrator Python code execute autonomously
```

**Problem:** LLM interprets "STOP" as "stop providing guidance" NOT "invoke Python orchestrator". There's **no mechanism to actually call the orchestrator**.

#### B. Missing Invocation Bridge

**Current Architecture (BROKEN):**
```
User Intent → CORTEX.prompt.md → Template Selection → ??? → Orchestrator
                                                        ↑
                                                   MISSING LINK
```

**Expected Architecture:**
```
User Intent → CORTEX.prompt.md → Invocation Tool → planning_orchestrator.py → Autonomous Execution
```

**The Problem:** There is no "Invocation Tool" - CORTEX can't actually call Python orchestrators. It can only:
- Read files
- Search codebase
- Edit files
- Run terminal commands

**Solution Required:** Add orchestrator invocation mechanism (MCP tool, API endpoint, or terminal wrapper).

#### C. Template Confusion

**Source:** `cortex-brain/response-templates-v4.yaml:1449-1510`

```yaml
autonomous_execution_progress:
  description: "Enhanced progress template for autonomous plan execution with visual Unicode progress bars"
  orchestrator_engaged: true
  format: |
    ## 🛡️🧠 CORTEX Plan Execution
    **Author:** Asif Hussain | **Plan:** {{plan_name}} | **Orchestrator:** Planning System 4.0 ✅
    
    ### 📊 Execution Progress
    
    **Overall Progress:** `{{overall_bar}}` **{{overall_percentage}}%** {{status_emoji}}
```

**Problem:** Template expects `{{plan_name}}`, `{{overall_bar}}`, etc. from orchestrator execution context, but CORTEX doesn't have access to these variables because **orchestrator never ran**.

**Result:** CORTEX substitutes template variables with placeholder text or empty values, creating illusion of progress without actual execution.

---

### 2. Governance Rule Bypasses

**SKULL Rules Violated:**

#### A. KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
**Rule Definition:** `cortex-brain/brain-protection-rules.yaml:2485`

```yaml
- rule_id: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
  name: Knowledge Library Integration (Phase -1 Consultation)
  severity: blocked
  description: "Before planning, consult knowledge library for best practices/patterns"
```

**Current Behavior:**
- ✅ Rule defined in brain-protection-rules.yaml
- ❌ Rule NOT checked in CORTEX.prompt.md intent router
- ❌ Rule NOT validated in planning_orchestrator.py
- ❌ Phase -1 section NOT added to manual plans

**Why Bypassed:** Manual plans (created via CORTEX prompt interpretation) skip orchestrator validation pipeline entirely.

#### B. REFACTOR_CODE_CLEANUP_ENFORCEMENT
**Rule Definition:** `cortex-brain/brain-protection-rules.yaml:319`

```yaml
- rule_id: REFACTOR_CODE_CLEANUP_ENFORCEMENT
  name: REFACTOR Phase Code Cleanup (Remove Orphaned/Duplicate Code)
  severity: blocked
  description: "REFACTOR phase must clean up orphaned functions, duplicate code, and unused imports"
```

**Current Behavior:**
- ✅ Rule defined with comprehensive 5-category checklist
- ❌ Orchestrator doesn't enforce ≥15 REFACTOR tasks
- ❌ Manual plans use narrow scope ("Animation Cleanup" = 6 tasks)
- ❌ No validation against task count threshold

**Why Bypassed:** No enforcement layer between plan approval and execution.

---

### 3. Architectural Fragmentation

**Current System Components (Scattered):**

| Component | Location | Responsibility | Issues |
|-----------|----------|----------------|--------|
| Intent Router | `.github/prompts/CORTEX.prompt.md` | Detect planning commands | ✅ Works correctly |
| Hand-Off Protocol | `.github/prompts/CORTEX.prompt.md:80-93` | Delegate to orchestrator | ❌ No invocation mechanism |
| Orchestrator Entry | `src/orchestrators/planning/planning_orchestrator.py:238` | Execute planning workflow | ❌ Never invoked |
| Manifest | `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` | Define governance rules | ❌ Not enforced |
| Response Template | `cortex-brain/response-templates-v4.yaml:1449` | Format output | ❌ Variables unpopulated |
| SKULL Rules | `cortex-brain/brain-protection-rules.yaml` | Governance enforcement | ❌ Bypassed entirely |

**Problem:** 6 separate components with no clear orchestration or fail-safe connections.

---

## 🏗️ Proposed Architecture - Autonomous Orchestrator Pattern

### Design Principles

1. **Single Responsibility** - CORTEX routes, Orchestrator executes
2. **Fail-Safe Hand-Off** - Invocation mechanism that guarantees orchestrator engagement
3. **Embedded Governance** - Validation checks built into orchestrator execution pipeline
4. **Self-Healing** - Orchestrator detects and corrects non-compliant plans
5. **Observable Execution** - Real-time progress visible to user and CORTEX

---

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER REQUEST                              │
│              "/CORTEX Plan user authentication"                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CORTEX INTENT CLASSIFIER                       │
│  (.github/prompts/CORTEX.prompt.md + LLMIntentClassifier)     │
│                                                                 │
│  Detects: "Planning System" intent                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              🛡️ HAND-OFF INVOCATION BRIDGE (NEW)               │
│                                                                 │
│  Options:                                                       │
│  1. MCP Tool: `invoke_orchestrator(name, params)`             │
│  2. Terminal: `cortex-orchestrate plan --feature="auth"`      │
│  3. API Endpoint: POST /orchestrators/planning/run            │
│                                                                 │
│  CRITICAL: This layer GUARANTEES orchestrator execution       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           PLANNING ORCHESTRATOR (AUTONOMOUS MODE)               │
│         (src/orchestrators/planning/planning_orchestrator.py)   │
│                                                                 │
│  Phase -1: Knowledge Library Consultation (MANDATORY)          │
│    ├─ Load planning-system-4.0-manifest.yaml                  │
│    ├─ Detect domains from feature description                 │
│    ├─ Query knowledge library (cortex-brain/knowledge-library/)│
│    └─ Inject context into plan structure                       │
│                                                                 │
│  Phase 0: Discovery & Validation                               │
│    ├─ Pre-planning discovery (existing plans)                 │
│    ├─ Complexity analysis (TIER 2-4)                          │
│    ├─ SKULL rule validation (all 8 rules)                     │
│    └─ Generate governance checklist                            │
│                                                                 │
│  Phase 1-9: Plan Generation                                    │
│    ├─ Create folder structure                                 │
│    ├─ Generate 00-master-plan.md                              │
│    ├─ Add Phase -1 section (5 tasks)                          │
│    ├─ Add Phase 0-9 sections (feature-specific)               │
│    ├─ Add Phase 10 (REFACTOR) with ≥15 tasks across 5 cats    │
│    └─ Embed copilot_instructions block                         │
│                                                                 │
│  Phase 10: Validation & Approval                               │
│    ├─ Run validate_plan_governance.py                         │
│    ├─ Compliance scoring (require ≥8.0/10)                    │
│    ├─ Self-healing: Auto-fix non-compliant sections           │
│    └─ Final approval gate                                      │
│                                                                 │
│  Output: Real-time progress via autonomous_execution_progress  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXECUTION COMPLETE                            │
│                                                                 │
│  Deliverables:                                                  │
│  ✅ Plan folder created in cortex-brain/documents/planning/    │
│  ✅ 00-master-plan.md with all governance requirements         │
│  ✅ progress-tracker.json (execution metadata)                 │
│  ✅ Compliance report (10.0/10 score)                          │
│  ✅ Knowledge library references embedded                       │
│                                                                 │
│  User sees: Visual progress bar + plan file link               │
│  CORTEX sees: Orchestrator completed successfully              │
└─────────────────────────────────────────────────────────────────┘
```

---

### Component Specifications

#### 1. Invocation Bridge (NEW COMPONENT)

**Purpose:** Guarantee orchestrator execution when 🛡️ AUTONOMOUS intent detected.

**Implementation Options:**

##### Option A: MCP Tool (RECOMMENDED)
```python
# src/mcp/tools/orchestrator_invocation.py

@mcp_tool
def invoke_orchestrator(
    name: str,  # "planning", "ado", "vacuum", etc.
    params: dict  # Feature description, complexity, etc.
) -> dict:
    """
    Invoke autonomous orchestrator and return execution result.
    
    This tool GUARANTEES orchestrator execution by:
    1. Validating orchestrator exists
    2. Loading manifest
    3. Initializing orchestrator with params
    4. Executing orchestrator.run()
    5. Streaming progress back to user
    6. Returning final result
    
    Returns:
        {
            "status": "success" | "failure",
            "plan_path": "cortex-brain/documents/planning/active/...",
            "compliance_score": 10.0,
            "execution_time": "2m 34s",
            "violations": []
        }
    """
    # Implementation loads orchestrator and executes
    pass
```

**Usage in CORTEX.prompt.md:**
```markdown
### Planning System (🛡️ AUTONOMOUS)

When planning intent detected:

1. Use `invoke_orchestrator` tool:
   ```
   invoke_orchestrator(
       name="planning",
       params={
           "feature": "user authentication",
           "complexity": "TIER 3"
       }
   )
   ```

2. Display header: `## 🛡️🧠 CORTEX Plan Execution`

3. Stream orchestrator progress to user

4. Display completion message with plan link
```

**Benefits:**
- ✅ Guaranteed execution (tool call vs. prompt interpretation)
- ✅ Type-safe parameters (validated by MCP schema)
- ✅ Observable progress (tool returns structured data)
- ✅ Error handling (tool catches orchestrator failures)

##### Option B: Terminal Wrapper
```bash
# cortex-brain/scripts/cortex-orchestrate.sh

#!/bin/bash
# Wrapper script for orchestrator invocation

ORCHESTRATOR=$1
shift  # Remove orchestrator name from args

case "$ORCHESTRATOR" in
    "plan"|"planning")
        python -m src.orchestrators.planning.planning_orchestrator "$@"
        ;;
    "ado")
        python -m src.orchestrators.ado.ado_orchestrator "$@"
        ;;
    *)
        echo "Unknown orchestrator: $ORCHESTRATOR"
        exit 1
        ;;
esac
```

**Usage in CORTEX.prompt.md:**
```markdown
When planning intent detected, run:

```bash
./cortex-brain/scripts/cortex-orchestrate.sh plan \
    --feature="user authentication" \
    --complexity="TIER 3"
```
```

**Benefits:**
- ✅ Simple implementation (bash script)
- ✅ Works with existing terminal tools
- ❌ Less observable progress (CORTEX can't parse output easily)

##### Option C: API Endpoint (Future)
```python
# src/api/orchestrator_endpoints.py

@app.post("/orchestrators/{orchestrator_name}/run")
async def run_orchestrator(
    orchestrator_name: str,
    params: OrchestratorParams
) -> OrchestratorResult:
    """REST API endpoint for orchestrator invocation."""
    pass
```

**Benefits:**
- ✅ Best observability (structured JSON responses)
- ✅ Web UI integration potential
- ❌ Requires API server infrastructure

---

#### 2. Orchestrator Self-Validation (ENHANCED)

**Integrate governance validation INTO orchestrator execution pipeline:**

```python
# src/orchestrators/planning/planning_orchestrator.py

class PlanningOrchestrator(BaseOrchestrator):
    
    def _execute_autonomous_mode(self, **kwargs) -> OrchestratorResult:
        """
        Enhanced autonomous execution with embedded governance validation.
        """
        # Phase -1: Knowledge Library Consultation (MANDATORY)
        self._phase_minus_one_knowledge_consultation(kwargs)
        
        # Phase 0: Validation Gate
        validation_result = self._validate_governance_rules()
        if not validation_result.passed:
            # AUTO-HEALING: Fix violations instead of failing
            self._auto_heal_governance_violations(validation_result)
        
        # Phase 1-9: Plan Generation
        plan = self._generate_plan_with_governance(**kwargs)
        
        # Phase 10: REFACTOR Validation
        refactor_validation = self._validate_refactor_comprehensiveness(plan)
        if refactor_validation.task_count < 15:
            # AUTO-HEALING: Add missing REFACTOR categories
            self._expand_refactor_phase(plan, target_tasks=18)
        
        # Final Validation
        compliance_score = self._calculate_compliance_score(plan)
        if compliance_score < 8.0:
            raise GovernanceViolationError(f"Plan compliance: {compliance_score}/10")
        
        return OrchestratorResult(
            status=OrchestratorStatus.SUCCESS,
            plan=plan,
            compliance_score=compliance_score
        )
    
    def _phase_minus_one_knowledge_consultation(self, params: dict) -> None:
        """
        Phase -1: Query knowledge library for applicable patterns/templates.
        
        SKULL Rule: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
        """
        # Load manifest knowledge_library_integration section
        manifest = self._load_manifest()
        kl_config = manifest["knowledge_library_integration"]
        
        # Detect domains from feature description
        feature_desc = params.get("feature", "")
        domains = self._detect_domains(feature_desc, kl_config)
        
        # Query knowledge library for each domain
        kl_context = {}
        for domain in domains:
            library_files = kl_config["domain_detection"]["classifiers"][domain]["library_files"]
            for file_path in library_files:
                content = self._read_knowledge_library_file(file_path)
                kl_context[file_path] = content
        
        # Inject into plan context
        self.knowledge_library_context = kl_context
        self.logger.info(f"✅ Phase -1: Loaded {len(kl_context)} knowledge library files")
    
    def _validate_refactor_comprehensiveness(self, plan: PlanData) -> RefactorValidation:
        """
        Validate REFACTOR phase has ≥15 tasks across 5 categories.
        
        SKULL Rule: REFACTOR_CODE_CLEANUP_ENFORCEMENT
        """
        refactor_phase = self._find_phase_by_name(plan, "REFACTOR")
        if not refactor_phase:
            return RefactorValidation(passed=False, reason="REFACTOR phase missing")
        
        task_count = len(refactor_phase.tasks)
        categories = self._detect_refactor_categories(refactor_phase)
        
        return RefactorValidation(
            passed=(task_count >= 15 and len(categories) >= 5),
            task_count=task_count,
            categories=categories,
            threshold=15
        )
    
    def _auto_heal_governance_violations(self, validation_result: ValidationResult) -> None:
        """
        Automatically fix governance violations instead of failing.
        
        Examples:
        - Missing Phase -1 → Add Phase -1 section with 5 tasks
        - Incomplete REFACTOR → Expand to 18 tasks across 5 categories
        - Missing copilot_instructions → Add template block
        """
        for violation in validation_result.violations:
            if violation.rule_id == "KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT":
                self._add_phase_minus_one_section()
            elif violation.rule_id == "REFACTOR_CODE_CLEANUP_ENFORCEMENT":
                self._expand_refactor_phase(target_tasks=18)
            elif violation.rule_id == "PLANNING_ISOLATION":
                self._add_copilot_instructions_block()
        
        self.logger.info(f"✅ Auto-healed {len(validation_result.violations)} violations")
```

**Key Enhancements:**

1. **Phase -1 Mandatory** - Always runs before plan generation
2. **REFACTOR Validation** - Checks task count ≥15 across 5 categories
3. **Auto-Healing** - Fixes violations instead of failing (graceful degradation)
4. **Compliance Scoring** - Enforces ≥8.0/10 threshold before approval

---

#### 3. Response Template Integration

**Fix template variable population:**

```python
# src/response_templates/template_renderer.py

class TemplateRenderer:
    
    @staticmethod
    def render_autonomous_progress(
        plan_name: str,
        phases: List[PhaseProgress],
        dor_passed: bool,
        dod_passed: bool,
        plan_path: str
    ) -> str:
        """
        Render autonomous_execution_progress template with real data.
        
        This method populates ALL template variables with orchestrator execution context.
        """
        # Load template
        template = TemplateRenderer._load_template("autonomous_execution_progress")
        
        # Calculate overall progress
        overall_percentage = sum(p.percentage for p in phases) / len(phases)
        overall_bar = TemplateRenderer.generate_progress_bar(overall_percentage)
        
        # Generate phase rows
        phase_rows = []
        for i, phase in enumerate(phases, start=1):
            phase_rows.append({
                "phase_num": i,
                "phase_name": phase.name,
                "completed": phase.status == "completed",
                "in_progress": phase.status == "in_progress",
                "phase_bar": TemplateRenderer.generate_progress_bar(phase.percentage),
                "percentage": phase.percentage,
                "completed_tasks": phase.completed_tasks,
                "total_tasks": phase.total_tasks,
                "elapsed_time": phase.elapsed_time
            })
        
        # Populate template
        return template.format(
            plan_name=plan_name,
            overall_bar=overall_bar,
            overall_percentage=overall_percentage,
            phases=phase_rows,
            dor_passed=dor_passed,
            dod_passed=dod_passed,
            plan_path=plan_path,
            next_action="Review plan and begin implementation"
        )
```

**Integration with Orchestrator:**

```python
# src/orchestrators/planning/planning_orchestrator.py

class PlanningOrchestrator(BaseOrchestrator):
    
    def _execute_autonomous_mode(self, **kwargs) -> OrchestratorResult:
        # ... existing execution logic ...
        
        # After plan generation completes
        progress_report = TemplateRenderer.render_autonomous_progress(
            plan_name=plan.metadata.title,
            phases=self.session.get_phase_progress(),
            dor_passed=True,
            dod_passed=False,  # Plan created, not yet executed
            plan_path=plan_file_path
        )
        
        # Return with populated template
        return OrchestratorResult(
            status=OrchestratorStatus.SUCCESS,
            message=progress_report,  # Pre-rendered template
            artifacts={"plan_path": plan_file_path}
        )
```

---

### 4. Validation Enforcement

**New validation script integration:**

```python
# cortex-toolkit/validate_plan_governance.py (ENHANCED)

class PlanGovernanceValidator:
    """
    Validates plan compliance with CORTEX governance standards.
    
    Usage:
    1. Standalone: python validate_plan_governance.py <plan_path>
    2. Library: from cortex_toolkit import validate_plan
    3. Orchestrator: Called automatically in Phase 10
    """
    
    def validate(self, plan_path: str) -> ValidationReport:
        """
        Run all 8 validation checks and generate compliance score.
        
        Checks:
        1. Phase -1 exists (5 tasks)
        2. REFACTOR phase comprehensive (≥15 tasks, 5 categories)
        3. copilot_instructions block present
        4. Knowledge library references present
        5. Visual progress tracker included
        6. Response template reference present
        7. DoR/DoD sections present
        8. Git checkpoint strategy defined
        
        Returns:
            ValidationReport with compliance score (0-10)
        """
        report = ValidationReport()
        
        # Check 1: Phase -1 (CRITICAL)
        phase_minus_one = self._check_phase_minus_one(plan_path)
        report.add_check("phase_minus_one", phase_minus_one, weight=2.0)
        
        # Check 2: REFACTOR comprehensiveness (CRITICAL)
        refactor = self._check_refactor_comprehensive(plan_path)
        report.add_check("refactor_comprehensive", refactor, weight=2.0)
        
        # ... other checks (weight=1.0 each) ...
        
        report.calculate_compliance_score()
        return report
    
    def _check_phase_minus_one(self, plan_path: str) -> CheckResult:
        """Verify Phase -1 section exists with ≥5 tasks."""
        content = Path(plan_path).read_text()
        
        # Check for Phase -1 heading
        if "## Phase -1:" not in content:
            return CheckResult(
                passed=False,
                message="Phase -1 (Knowledge Library Consultation) missing",
                severity="CRITICAL"
            )
        
        # Extract Phase -1 section
        phase_section = self._extract_phase_section(content, "-1")
        
        # Count tasks
        tasks = re.findall(r"^\| -1\.\d+ \|", phase_section, re.MULTILINE)
        if len(tasks) < 5:
            return CheckResult(
                passed=False,
                message=f"Phase -1 has {len(tasks)} tasks (need ≥5)",
                severity="WARNING"
            )
        
        return CheckResult(passed=True, message=f"Phase -1 compliant ({len(tasks)} tasks)")
```

**Integration Point:**

```python
# src/orchestrators/planning/planning_orchestrator.py

class PlanningOrchestrator(BaseOrchestrator):
    
    def _execute_autonomous_mode(self, **kwargs) -> OrchestratorResult:
        # ... plan generation ...
        
        # Phase 10: Validation
        validator = PlanGovernanceValidator()
        validation_report = validator.validate(plan_file_path)
        
        if validation_report.compliance_score < 8.0:
            # Auto-healing attempt
            self.logger.warning(f"⚠️ Plan compliance: {validation_report.compliance_score}/10")
            self._auto_heal_governance_violations(validation_report)
            
            # Re-validate after healing
            validation_report = validator.validate(plan_file_path)
            
            if validation_report.compliance_score < 8.0:
                raise GovernanceViolationError(
                    f"Plan failed governance validation: {validation_report.compliance_score}/10\n"
                    f"Violations: {validation_report.format_violations()}"
                )
        
        self.logger.info(f"✅ Plan compliance: {validation_report.compliance_score}/10")
        return OrchestratorResult(...)
```

---

## 📋 Implementation Roadmap

### Phase 1: Invocation Bridge (Week 1)
- [ ] Implement MCP tool `invoke_orchestrator`
- [ ] Update CORTEX.prompt.md with tool usage
- [ ] Add orchestrator registry (map name → Python class)
- [ ] Test planning orchestrator invocation
- [ ] Validate hand-off works for ADO, Vacuum orchestrators

### Phase 2: Orchestrator Self-Validation (Week 2)
- [ ] Implement `_phase_minus_one_knowledge_consultation()`
- [ ] Implement `_validate_refactor_comprehensiveness()`
- [ ] Implement `_auto_heal_governance_violations()`
- [ ] Add compliance scoring logic
- [ ] Integrate validation into execution pipeline

### Phase 3: Template Integration (Week 3)
- [ ] Enhance `TemplateRenderer.render_autonomous_progress()`
- [ ] Wire orchestrator progress to template variables
- [ ] Test template rendering with real execution data
- [ ] Update response-templates-v4.yaml documentation

### Phase 4: Validation Script Enhancement (Week 4)
- [ ] Enhance `cortex-toolkit/validate_plan_governance.py`
- [ ] Add 8 validation checks
- [ ] Implement compliance scoring
- [ ] Add auto-healing suggestions
- [ ] Integrate with orchestrator Phase 10

### Phase 5: Maintenance Template Standardization (Week 5)
- [ ] Extract maintenance visual progress pattern
- [ ] Create reusable progress bar component
- [ ] Update planning to use same pattern
- [ ] Standardize across all orchestrators (ADO, Vacuum, etc.)

### Phase 6: Testing & Validation (Week 6)
- [ ] Create test suite for hand-off protocol
- [ ] Test auto-healing scenarios
- [ ] Validate compliance scoring
- [ ] Performance testing (execution time)
- [ ] User acceptance testing

### Phase 7: Documentation & Migration (Week 7)
- [ ] Update CORTEX.prompt.md with new architecture
- [ ] Update copilot-instructions.md
- [ ] Create migration guide (4.0 → 5.0)
- [ ] Update planning-system-4.0-manifest.yaml → 5.0
- [ ] Archive old implementation

---

## 🎯 Success Criteria

### Functional Requirements
- [ ] 100% orchestrator engagement when 🛡️ AUTONOMOUS intent detected
- [ ] Phase -1 included in 100% of generated plans
- [ ] REFACTOR phase has ≥15 tasks in 100% of plans
- [ ] Compliance score ≥8.0/10 for all generated plans
- [ ] Auto-healing succeeds for 90% of violations

### Non-Functional Requirements
- [ ] Plan generation time <5 seconds (90th percentile)
- [ ] Zero manual plan bypasses (orchestrator always used)
- [ ] Template variables populated correctly 100% of time
- [ ] Governance violations detected in <1 second

### User Experience
- [ ] Clear visual progress bar during plan generation
- [ ] Plan link provided immediately after completion
- [ ] Compliance report included in final output
- [ ] Error messages actionable (not cryptic)

---

## 🔄 Backward Compatibility

### Migration Strategy

**Existing Plans:** Supported via validation script
```python
# Validate existing plan
validator = PlanGovernanceValidator()
report = validator.validate("cortex-brain/documents/planning/active/existing-plan/00-master-plan.md")

if report.compliance_score < 8.0:
    print(f"⚠️ Plan non-compliant: {report.compliance_score}/10")
    print("Run: cortex-orchestrate upgrade-plan --plan=<path>")
```

**Orchestrator Versions:** Side-by-side support
```
src/orchestrators/planning/
├── planning_orchestrator.py      # v5.0 (new)
├── planning_orchestrator_v4.py   # v4.0 (legacy, read-only)
└── version_router.py             # Auto-detect plan version
```

**Invocation:** Detect version and route
```python
def invoke_orchestrator(name, params):
    if name == "planning":
        # Detect if existing plan or new plan
        if params.get("existing_plan_path"):
            return PlanningOrchestratorV4().run(params)  # Legacy
        else:
            return PlanningOrchestrator().run(params)    # New
```

---

## 📊 Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **MCP tool performance** | MEDIUM | HIGH | Add timeout + fallback to terminal wrapper |
| **Auto-healing bugs** | HIGH | MEDIUM | Extensive testing + validation report review |
| **Template rendering errors** | LOW | MEDIUM | Comprehensive unit tests for all template paths |
| **Backward incompatibility** | LOW | HIGH | Version detection + side-by-side support |
| **User confusion** | MEDIUM | LOW | Clear error messages + migration guide |

---

## 🚀 Recommendation

**APPROVE** redesign and proceed with Phase 1 implementation.

**Rationale:**
1. Current system fundamentally broken (6.8/10 compliance)
2. Manual workarounds not sustainable
3. Redesign addresses root causes (invocation, validation, auto-healing)
4. Backward compatibility preserved
5. Clear migration path

**Next Steps:**
1. Review this proposal with stakeholders
2. Approve Phase 1 budget (1 week)
3. Begin MCP tool implementation
4. Update CORTEX.prompt.md with new hand-off protocol

---

**End of Proposal**
