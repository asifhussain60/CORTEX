# CORTEX Architecture Contract v5.0

**Document Type:** Architecture Specification (BINDING)  
**Version:** 5.0.0  
**Status:** ✅ ACTIVE  
**Author:** Asif Hussain  
**Last Updated:** 2026-01-05  
**Audit Compliance:** 95%+ Required

---

## 🎯 Purpose

This document defines the **mandatory** architecture contract for CORTEX v5.0. All components, orchestrators, and documentation MUST comply with these principles to ensure:

1. **No textual ambiguity** in work coordination
2. **Structured execution** via Python + YAML + Tooling
3. **Tool-based invocation** (not text-based handoffs)
4. **Audit compliance** (≥95% score required for production)

**VIOLATION SEVERITY:** Any violation of this contract is considered a P0 architectural defect requiring immediate remediation.

---

## 📐 Core Architecture Principles

### Principle 1: Master Orchestrator is Python-Based

**REQUIREMENT:** Master orchestration logic MUST be implemented in Python scripts.

**Compliant Implementation:**
```
src/entry_point/cortex_entry.py       # Entry point
src/orchestrators/master_orchestrator.py  # Routing logic
src/cortex_agents/llm_intent_classifier.py  # Intent classification
```

**Anti-Patterns (FORBIDDEN):**
- ❌ Text-based routing in prompt files
- ❌ GitHub Copilot executing orchestrator logic
- ❌ Manual orchestration based on documentation

**Verification:** Python files MUST exist and contain executable orchestration logic.

---

### Principle 2: Work Definition is 100% YAML-Based

**REQUIREMENT:** ALL work (plans, phases, tasks, routing, priority) MUST be defined in YAML files with structured schemas. NO textual ambiguity permitted.

**Compliant Implementation:**
```yaml
# cortex-brain/config/master-orchestrator.yaml
routing_rules:
  - pattern: "^(plan|create a plan)"
    orchestrator: "planning_v5"
    priority: 10
    mode: "autonomous"

# cortex-brain/documents/planning/active/c150-remediation-plan/00-master-plan.yaml
phases:
  - id: "phase1"
    name: "Discovery"
    tasks:
      - id: "task1"
        description: "Analyze codebase"
        acceptance_criteria:
          - "All Python files scanned"
```

**Anti-Patterns (FORBIDDEN):**
- ❌ Work definition in markdown prose
- ❌ Routing rules in natural language
- ❌ Priority management via text descriptions
- ❌ Task definitions without structured schema

**Verification:** All configuration and planning files MUST be valid YAML with schema validation.

---

### Principle 3: Invocation via `run_in_terminal` Tool

**REQUIREMENT:** ALL orchestrator invocations MUST use the `run_in_terminal` tool to execute Python scripts. NO text-based "handoff" messages.

**Compliant Implementation:**
```python
# GitHub Copilot invokes orchestrator:
run_in_terminal(
    command="python3 -m src.main 'plan user authentication' --format markdown",
    explanation="Invoking Planning v5 orchestrator via terminal",
    isBackground=False
)
```

**Invocation Flow:**
```
[1] GitHub Copilot receives user request
[2] GitHub Copilot matches routing pattern (YAML)
[3] GitHub Copilot transforms request (adds context)
[4] GitHub Copilot invokes Python via run_in_terminal
[5] Python MasterOrchestrator loads YAML configs
[6] Python routes to specific orchestrator
[7] Python orchestrator executes and returns results
[8] GitHub Copilot displays orchestrator output
```

**Anti-Patterns (FORBIDDEN):**
- ❌ Displaying "HAND-OFF COMPLETE" without terminal invocation
- ❌ Text-based handoff messages ("Python orchestrator executing...")
- ❌ Assuming orchestrator runs based on documentation alone
- ❌ GitHub Copilot executing orchestrator logic internally

**Verification:** All orchestrator engagements MUST show `run_in_terminal` command execution in terminal output.

---

### Principle 4: Epic/Feature/Phase Plans via Scripts

**REQUIREMENT:** ALL plan types (Epic, Feature, Phased) MUST be:
1. Defined in YAML files (structured schema)
2. Loaded by Python scripts
3. Executed by Python orchestrators
4. State tracked in SQLite databases

**Compliant Implementation:**
```
Plan Lifecycle:
1. Plan defined: cortex-brain/documents/planning/active/{plan-id}/00-master-plan.yaml
2. Plan loaded: src/orchestrators/planning/planning_orchestrator_v5.py loads YAML
3. Plan executed: Python orchestrator executes phases sequentially
4. State persisted: src/database/planning_state_db.py stores progress in SQLite
```

**Anti-Patterns (FORBIDDEN):**
- ❌ Plan execution based on markdown instructions
- ❌ Manual phase progression via text commands
- ❌ State tracking in text files or logs
- ❌ Plan logic in GitHub Copilot responses

**Verification:** Plan execution MUST write to `planning_state_db.db` SQLite database.

---

### Principle 5: Structured State Management

**REQUIREMENT:** ALL critical state MUST be stored in structured databases (SQLite). NO critical state in text files, logs, or markdown.

**Compliant Implementation:**
```python
# src/database/tier0_governance.py
class GovernanceDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        
# src/database/tier1_working_memory.py
class WorkingMemoryDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        
# src/database/planning_state_db.py
class PlanningStateDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
```

**Anti-Patterns (FORBIDDEN):**
- ❌ Storing plan state in JSON files
- ❌ Tracking progress in markdown documents
- ❌ Using logs as source of truth
- ❌ Relying on file timestamps for state

**Verification:** All databases MUST be SQLite files with schema-validated tables.

---

### Principle 6: YAML-Based Routing and Priority

**REQUIREMENT:** ALL routing rules and priority management MUST be defined in YAML configuration files.

**Compliant Implementation:**
```yaml
# cortex-brain/config/master-orchestrator.yaml
routing_rules:
  - pattern: "^(plan|create a plan)"
    orchestrator: "planning_v5"
    priority: 10
    mode: "autonomous"
    confidence_threshold: 0.8
```

**Anti-Patterns (FORBIDDEN):**
- ❌ Routing logic in Python if/else statements (must load from YAML)
- ❌ Priority hardcoded in code
- ❌ Pattern matching without YAML definition

**Verification:** `cortex-brain/config/master-orchestrator.yaml` MUST contain all routing rules with priority values.

---

## 🚫 Prohibited Terminology

The following terms are **BANNED** from all CORTEX documentation due to misleading implications:

| BANNED Term | Reason | Correct Term |
|-------------|--------|--------------|
| "hand-off complete" | Implies text-based coordination | "Invoking Python via terminal" |
| "autonomous execution" | Ambiguous mechanism | "Python script execution via run_in_terminal" |
| "orchestrator executing" | Passive voice, unclear actor | "Python orchestrator invoked via run_in_terminal" |
| "taking control" | Anthropomorphic, unclear mechanism | "Executing via terminal invocation" |
| "engaging orchestrator" | Vague activation | "Calling run_in_terminal with python3 -m src.main" |

**Rationale:** These terms suggest text-based or magical activation rather than explicit tool-based invocation.

---

## ✅ Compliant Language Examples

### Good: Tool-Based Invocation
```markdown
## 🛡️ Planning v5 → Invoking via terminal

**Pattern:** `^(plan|create a plan)` | **Confidence:** 1.0

✅ **INVOKING PYTHON** - `python3 -m src.main "plan user authentication" --format markdown`
```

### Bad: Text-Based Handoff (FORBIDDEN)
```markdown
## 🛡️ Planning v5 → Autonomous Execution

**Pattern:** `^(plan|create a plan)` | **Confidence:** 1.0

⚠️ **HAND-OFF COMPLETE** - Python orchestrator executing...
```

**Difference:** The compliant version explicitly shows the terminal command. The non-compliant version uses passive voice and misleading "hand-off" language.

---

## 📊 Audit Requirements

### Mandatory Compliance Checks

All CORTEX deployments MUST pass these audit checks:

| Check # | Requirement | Passing Score | Critical? |
|---------|-------------|---------------|-----------|
| 1 | Master orchestrator is Python-based | 100% | ✅ YES |
| 2 | Work defined in YAML (no textual ambiguity) | 100% | ✅ YES |
| 3 | No text-based handoffs | 100% | ✅ YES |
| 4 | Epic/Feature/Phase plans use scripts | 100% | ✅ YES |
| 5 | Structured state management (SQLite) | 100% | ⚠️ High |
| 6 | YAML-based routing | 100% | ⚠️ High |
| 7 | YAML-defined priority | 100% | ⚠️ High |
| 8 | Handoff mechanism verification | 100% | ✅ YES |

**OVERALL SCORE REQUIREMENT:** ≥95%  
**PRODUCTION GATE:** <95% = BLOCKS deployment

**Audit Script:** `scripts/audit_master_orchestrator_architecture.py`

**Run Audit:**
```bash
python3 scripts/audit_master_orchestrator_architecture.py
```

---

## 🛡️ Enforcement Mechanisms

### Pre-Commit Hooks (Required)

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running CORTEX architecture audit..."
python3 scripts/audit_master_orchestrator_architecture.py

if [ $? -ne 0 ]; then
    echo "❌ ARCHITECTURE AUDIT FAILED - Commit blocked"
    echo "Run audit manually: python3 scripts/audit_master_orchestrator_architecture.py"
    exit 1
fi

echo "✅ Architecture audit passed"
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/architecture-audit.yml
name: CORTEX Architecture Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Architecture Audit
        run: |
          python3 scripts/audit_master_orchestrator_architecture.py
          if [ $? -ne 0 ]; then
            echo "::error::Architecture audit failed - see report"
            exit 1
          fi
```

### Documentation Review Checklist

Before merging documentation changes:

- [ ] No "hand-off" language used
- [ ] No "autonomous execution" without `run_in_terminal` context
- [ ] All orchestrator invocations show terminal commands
- [ ] YAML-first approach for all work definition
- [ ] Python-first approach for all logic execution

---

## 📚 Reference Implementation

### Compliant Orchestrator

```python
# src/orchestrators/planning/planning_orchestrator_v5.py
class PlanningOrchestratorV5:
    def __init__(self, state_db: PlanningStateDB):
        # Load configuration from YAML (Principle 2)
        self.config = self._load_config("cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml")
        self.state_db = state_db  # Structured state (Principle 5)
        
    def execute(self, user_request: str) -> ExecutionResult:
        # Parse user request
        plan_spec = self._parse_request(user_request)
        
        # Load YAML schemas
        master_plan = self._load_yaml(f"{plan_spec.folder}/00-master-plan.yaml")
        
        # Execute phases
        for phase in master_plan['phases']:
            result = self._execute_phase(phase)
            self.state_db.save_phase_result(result)  # SQLite state
            
        return ExecutionResult(success=True)
```

### Compliant Invocation (GitHub Copilot)

```python
# GitHub Copilot receives: "plan user authentication"

# Step 1: Match pattern from YAML
routing_rule = load_yaml("cortex-brain/config/master-orchestrator.yaml")
matched_rule = match_pattern("plan user authentication", routing_rule['routing_rules'])
# Result: pattern="^(plan|create a plan)", orchestrator="planning_v5"

# Step 2: Transform request
transformed = transform_request("plan user authentication")
# Result: "plan user authentication with OAuth2, JWT, database (users, roles), API (login, logout), testing (unit, integration)"

# Step 3: Invoke via terminal (Principle 3)
run_in_terminal(
    command=f"python3 -m src.main \"{transformed}\" --format markdown",
    explanation="Invoking Planning v5 orchestrator via terminal",
    isBackground=False
)
```

---

## 🔄 Version History

| Version | Date | Changes | Audit Score |
|---------|------|---------|-------------|
| 5.0.0 | 2026-01-05 | Initial architecture contract | 95%+ target |

---

## 📝 Amendment Process

To amend this contract:

1. **Propose Change:** Create issue with `architecture-contract` label
2. **Impact Analysis:** Audit existing implementations for breaking changes
3. **Approval Required:** Architecture owner (Asif Hussain) must approve
4. **Version Bump:** Increment contract version (semantic versioning)
5. **Update Audit:** Modify `scripts/audit_master_orchestrator_architecture.py` to reflect new requirements
6. **Re-Audit All:** Run audit against all existing code
7. **Document Migration:** Create migration guide for non-compliant code

---

## 🚨 Violation Remediation

If architecture audit fails (<95%):

### Step 1: Run Audit
```bash
python3 scripts/audit_master_orchestrator_architecture.py
```

### Step 2: Review Report
```bash
cat cortex-brain/documents/reports/master-orchestrator-architecture-audit-$(date +%Y-%m-%d).json
```

### Step 3: Fix Issues
Prioritize by check number:
- **CHECK 3 (Text-based handoffs):** P0 - Fix immediately
- **CHECK 1 (Python-based):** P0 - Add missing files
- **CHECK 6-7 (YAML routing/priority):** P1 - Fix configuration

### Step 4: Re-Audit
```bash
python3 scripts/audit_master_orchestrator_architecture.py
```

### Step 5: Verify ≥95%
```bash
# Expected output:
# Overall Score: 95.00%+
# Grade: EXCELLENT
# Status: ✅ FULLY COMPLIANT
```

---

## ✅ Certification

**I certify that this architecture contract represents the mandatory design principles for CORTEX v5.0 and all components MUST comply to ensure structured, unambiguous orchestration.**

**Signed:** Asif Hussain  
**Date:** 2026-01-05  
**Role:** CORTEX Architect

---

**ENFORCEMENT:** This contract is BINDING. Non-compliance discovered in code review or audit MUST be remediated before merge/deployment.

**AUDIT FREQUENCY:** Run architecture audit on every commit (pre-commit hook) and in CI/CD pipeline.

**NEXT REVIEW:** 2026-04-05 (quarterly review cycle)
