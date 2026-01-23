# CORTEX Live Implementation Review System - Enhanced v4.1

## 8-Agent Comprehensive Flaw Detection & Analysis

**Version:** 4.1 (Jan 23, 2026) - ENHANCED WITH ARCHITECTURE & OPERATIONS AGENTS  

**Status:** PRODUCTION READY ✅  

**Workflow:** 2-3 hours (gap detection + 8-agent parallel analysis + consolidation)  

**Focus:** Identify implementation gaps, structural flaws, state/concurrency issues, architectural defects, integration failures, and observability gaps

---

## 🎯 PURPOSE

Compare LIVE implementation against `cortex-impl-map.yaml` roadmap and identify:

1. **Implementation Gaps** - Phases marked COMPLETED but code is missing/incomplete
2. **Brittleness Issues** - Code that works but breaks under load/edge cases
3. **Hallucination/AI Safety** - Unvalidated LLM output, prompt injection vectors
4. **Governance Violations** - CORE rule violations, audit trail issues
5. **Assumption Failures** - Hidden platform/environment dependencies
6. **Technical Debt** - Code duplication, deprecated patterns, missing abstractions
7. **State Management Flaws** - Race conditions, deadlocks, concurrency issues ⭐ NEW
8. **Architecture Defects** - SOLID violations, design pattern misuse, coupling issues ⭐ NEW
9. **Integration Failures** - System boundary issues, observability gaps ⭐ NEW

---

## 🚀 WORKFLOW OVERVIEW

### Pre-Execution: Create Timestamped Artifacts Directory

**MANDATORY FIRST STEP** before any analysis:

```bash
# Create timestamped directory for ALL review outputs
export REVIEW_TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
export REVIEW_ARTIFACTS="_workspaces/roadmap/issues/${REVIEW_TIMESTAMP}"
mkdir -p "${REVIEW_ARTIFACTS}"

# All findings, reports, diagnostics, and logs go here
# NO ephemeral output allowed - all results persisted to disk
```

**Directory structure for this execution:**
```
_workspaces/roadmap/issues/
├─ 2026-01-23_143022/                    ← This execution's timestamped folder
│  ├─ review-gap-inventory.yaml
│  ├─ review-stubs.yaml
│  ├─ Findings-BRIT.yaml
│  ├─ Findings-HALL.yaml
│  ├─ Findings-GOV.yaml
│  ├─ Findings-ASM.yaml
│  ├─ Findings-DEBT.yaml
│  ├─ Findings-STATE.yaml
│  ├─ Findings-ARCH.yaml
│  ├─ Findings-INTEG.yaml
│  ├─ audit-trace-validation.yaml
│  ├─ mcp-toolkit-audit.yaml
│  ├─ cortex-lens-ast-validation.yaml
│  └─ remediation-plan.yaml
└─ reports/
   ├─ requirements-analysis-2026-01-23_143022.yaml
   └─ review-findings-consolidated-2026-01-23_143022.yaml
```

---

### Phase 0: Pre-Review Validation (15 min)

Four mandatory data quality gates before ANY analysis:

```yaml
Gate 0A: Data Freshness (last entry < 24 hours) → Pass/Fail
Gate 0B: Audit Trail Completeness (≥ 2000 entries) → Pass/Fail
Gate 0C: Hash Chain Integrity (0 violations) → Pass/Fail
Gate 0D: Test Fixture Isolation (≤ 6 fixtures) → Pass/Fail

If ALL pass → Proceed to Phase 1
If ANY fail  → Go to Phase 0.5 (Surgical Investigation)
```

### Phase 0.5: Surgical Investigation (Optional, 30-45 min)

**Triggered by:** Hash chain failure or suspicious test data

**Purpose:** Root cause analysis before regenerating data

```sql
SELECT ac_id, operation, COUNT(*) as violation_count
FROM audit_log
WHERE [hash chain check fails]
GROUP BY ac_id, operation
ORDER BY violation_count DESC;
```

Classify defect type:
- TEST_ARTIFACT (not in TEST_FIXTURES)
- TIMING_ISSUE (entries from test execution window)
- IMPLEMENTATION_FLAW (code has TODO/NotImplementedError)
- HASH_CALC_BUG (hash calculation defect)

### Phase 1: Gap Inventory (15 min)

1. Read `cortex-impl-map.yaml` status distribution
2. For each COMPLETED phase, verify actual implementation exists
3. Find FALSE_COMPLETED phases (claimed done, actually partial/missing)
4. Create: `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/review-gap-inventory.yaml`

### Phase 2: Stub Detection (20 min)

1. Find all `raise NotImplementedError` in cortex/
2. Find all `pass` statements in function bodies
3. Find all `# TODO` blocking comments
4. Find all mock/hardcoded returns
5. Create: `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/review-stubs.yaml`

### Phase 3: 8-Agent Parallel Analysis (27 min)

**Batch 1: Core Quality (12 min parallel):**
- Agent 1: Brittleness (SPOFs, error handling, resource exhaustion)
- Agent 2: Hallucination (AI safety, injection vectors, LLM validation)
- Agent 3: Governance (CORE-008 through CORE-028 compliance)

**Batch 2: Architecture & Operations (15 min parallel):**
- Agent 4: Assumptions (platform, version, service dependencies)
- Agent 5: Debt (duplication, patterns, abstractions, test gaps)
- Agent 6: State Management (race conditions, deadlocks, atomicity, global state) ⭐ NEW
- Agent 7: Architecture (SOLID violations, design patterns, coupling) ⭐ NEW
- Agent 8: Integration/Observability (boundaries, monitoring, health checks) ⭐ NEW

Each agent produces: `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/Findings-{AGENT}.yaml`

### Phase 4: Requirements Validation (10 min)

1. Scan all imports in cortex/
2. Compare with requirements.txt
3. Identify missing packages
4. Create: `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/requirements-analysis.yaml`

### Phase 4.5: Instruction Alignment Validation (15 min) ⭐ NEW

**Purpose:** Verify copilot-instruction.md is synchronized with cortex-total-recall.prompt.md and production state.

**Step 4.5.1: Version Alignment Check**

```bash
# Extract versions from instruction files
TOTAL_RECALL_VERSION=$(grep "^\\*\\*Version:\\*\\*" .github/prompts/cortex-total-recall.prompt.md | head -1 | sed 's/.*Version:\*\* //' | cut -d' ' -f1)
COPILOT_INSTR_VERSION=$(grep "^\\*\\*Version:\\*\\*" .github/copilot-instruction.md | head -1 | sed 's/.*Version:\*\* //' | cut -d' ' -f1)
CORTEX_PROMPT_VERSION=$(grep "^\\*\\*Version:\\*\\*" .github/prompts/CORTEX.prompt.md | head -1 | sed 's/.*Version:\*\* //' | cut -d' ' -f1)

echo "Version Alignment Check:" > ${REVIEW_ARTIFACTS}/instruction-alignment.yaml
echo "  total_recall_version: $TOTAL_RECALL_VERSION" >> ${REVIEW_ARTIFACTS}/instruction-alignment.yaml
echo "  copilot_instruction_version: $COPILOT_INSTR_VERSION" >> ${REVIEW_ARTIFACTS}/instruction-alignment.yaml
echo "  cortex_prompt_version: $CORTEX_PROMPT_VERSION" >> ${REVIEW_ARTIFACTS}/instruction-alignment.yaml
```

**Step 4.5.2: Component Coverage Check**

Verify copilot-instruction.md includes all production components from cortex-total-recall.prompt.md:

```bash
# Check for critical component references
python3 << 'EOF'
import yaml
import re

critical_components = [
    "Brain Tier Architecture",
    "Intelligence Layer",
    "Todo Manager",
    "Knowledge Composer",
    "Domain Brain",
    "Multi-Repo Governance",
    "Conversation Protocol",
    "Git Sync.*domain knowledge protection"
]

with open('.github/copilot-instruction.md', 'r') as f:
    content = f.read()

missing = []
found = []

for component in critical_components:
    if re.search(component, content, re.IGNORECASE):
        found.append(component)
    else:
        missing.append(component)

result = {
    'instruction_alignment_validation': {
        'total_components_checked': len(critical_components),
        'found_components': len(found),
        'missing_components': len(missing),
        'found': found,
        'missing': missing,
        'status': 'PASSED' if len(missing) == 0 else 'FAILED'
    }
}

with open('${REVIEW_ARTIFACTS}/instruction-alignment.yaml', 'a') as f:
    yaml.dump(result, f)
EOF

cat ${REVIEW_ARTIFACTS}/instruction-alignment.yaml
```

**Step 4.5.3: Governance Rule Count Verification**

```bash
# Verify governance rule counts match across documents
python3 << 'EOF'
import yaml
import re

# Extract rule counts from copilot-instruction.md
with open('.github/copilot-instruction.md', 'r') as f:
    content = f.read()

# Look for tier rule counts in table
tier0_match = re.search(r'Tier 0.*?\| (\d+) \|', content)
tier1_match = re.search(r'Tier 1.*?\| (\d+) \|', content)
tier2_match = re.search(r'Tier 2.*?\| (\d+) \|', content)
tier3_match = re.search(r'Tier 3.*?\| (\d+) \|', content)

tier_counts = {
    'tier0': int(tier0_match.group(1)) if tier0_match else 0,
    'tier1': int(tier1_match.group(1)) if tier1_match else 0,
    'tier2': int(tier2_match.group(1)) if tier2_match else 0,
    'tier3': int(tier3_match.group(1)) if tier3_match else 0
}

# Expected counts from cortex-total-recall.prompt.md
expected = {
    'tier0': 29,
    'tier1': 47,
    'tier2': 38,
    'tier3': 13
}

mismatches = []
for tier, count in tier_counts.items():
    if count != expected[tier]:
        mismatches.append({
            'tier': tier,
            'expected': expected[tier],
            'actual': count
        })

result = {
    'governance_rule_count_verification': {
        'tier_counts': tier_counts,
        'expected_counts': expected,
        'mismatches': mismatches,
        'status': 'PASSED' if len(mismatches) == 0 else 'FAILED'
    }
}

with open('${REVIEW_ARTIFACTS}/instruction-alignment.yaml', 'a') as f:
    yaml.dump(result, f)
EOF
```

**Step 4.5.4: Outdated Instruction Detection**

```bash
# Check for outdated patterns in copilot-instruction.md
grep -n "CRITICAL.*Production Hardening" .github/copilot-instruction.md || echo "✓ No outdated production hardening references"
grep -n "NOT PRODUCTION READY" .github/copilot-instruction.md || echo "✓ No 'NOT PRODUCTION READY' flags"
grep -n "IN-PROGRESS.*Orchestrators" .github/copilot-instruction.md || echo "✓ No outdated orchestrator status"
grep -n "14 tools" .github/copilot-instruction.md && echo "⚠️  Outdated MCP tool count (should be 15)" || echo "✓ MCP tool count current"
```

**Pass Criteria:**
- ✅ All critical components referenced in copilot-instruction.md
- ✅ Governance rule counts match (29/47/38/13)
- ✅ No outdated "NOT PRODUCTION READY" or "IN-PROGRESS" flags
- ✅ MCP tool count is current (15 tools)
- ✅ Version alignment documented

**Output:** `${REVIEW_ARTIFACTS}/instruction-alignment.yaml`

### Phase 5: Consolidated Report (20 min)

1. Merge all 8 agent findings
2. Classify by severity: CRITICAL / HIGH / MEDIUM / LOW
3. Include instruction alignment results
4. Create: `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/review-findings-consolidated.yaml`
5. Ready for cortex-builder.prompt.md

### Phase 6: Audit Trace & End-to-End Validation (25 min) ⭐ MANDATORY

**Purpose:** Verify CORTEX is truly functional via runtime audit logs + database inspection

**Step 6.1: Runtime Audit Trace Inspection (12 min)**

```bash
# Identify audit trace logs for this execution window
find cortex/ -name "*audit*.log" -o -name "*trace*.log" | sort -r | head -20

# Analyze trace completeness
grep -E "MCP_INTERFACE|CORE_LOGIC|TOOLKIT|LENS_OPERATION" *.log \
  | wc -l > ${REVIEW_ARTIFACTS}/audit-trace-count.txt

# Verify traces span all critical execution paths
# Must find evidence of:
# - AC_START → AC_INITIALIZE → AC_CONFIGURE
# - AC_EXECUTE → MCP call → TOOLKIT operation → LENS validation
# - AC_COMPLETE → AC_CLEANUP → AUDIT_LOG_WRITE
```

**Step 6.2: Database Audit Log Query (10 min)**

```sql
-- Query persisted audit logs
SELECT 
  ac_id,
  operation,
  timestamp,
  component,
  status,
  error_message,
  execution_time_ms
FROM audit_log
WHERE execution_date >= DATE(NOW())
  AND status IN ('EXECUTED', 'FAILED', 'TIMEOUT')
  AND component IN ('MCP_INTERFACE', 'CORE_LOGIC', 'TOOLKIT', 'LENS')
ORDER BY timestamp ASC;

-- Verify trace continuity (no gaps > 1 second)
SELECT 
  ac_id,
  LEAD(timestamp) OVER (PARTITION BY ac_id ORDER BY timestamp) - timestamp as gap_seconds
FROM audit_log
WHERE execution_date >= DATE(NOW())
HAVING gap_seconds > INTERVAL 1 SECOND;

-- Confirm log completeness (every operation logged)
SELECT 
  operation,
  COUNT(*) as count,
  MAX(timestamp) as latest
FROM audit_log
WHERE execution_date >= DATE(NOW())
GROUP BY operation
ORDER BY count DESC;
```

**Step 6.3: Validation Rules**

❌ **CRITICAL FAILURES (abort review if any found):**
- Runtime logs missing for executed ACs
- Database audit logs incomplete (< 80% of expected operations)
- Gaps > 2 seconds between operations in same AC
- Missing error messages for FAILED operations
- Operations logged but no corresponding database record
- Timestamps out of order within AC execution
- No correlation IDs linking MCP → TOOLKIT → LENS operations

✅ **PASS CRITERIA:**
- All executed ACs have continuous audit trail (100% operation logging)
- Database logs match runtime traces (≥ 95% correlation)
- No gaps > 1 second in critical execution paths
- Error messages present for all FAILED operations
- Correlation IDs successfully link all cross-component calls
- Audit logs reflect REAL executions (not stubs, mocks, or test data)

**Output:** `${REVIEW_ARTIFACTS}/audit-trace-validation.yaml`

```yaml
audit_trace_validation:
  execution_window: "2026-01-23 14:30:22 - 2026-01-23 14:55:18"
  status: "PASSED" | "FAILED"
  
  runtime_traces:
    files_found: 12
    total_operations_logged: 847
    mcp_operations: 124
    toolkit_operations: 156
    lens_operations: 89
    completeness: "98.7%"
  
  database_audit_logs:
    total_records: 823
    executed_operations: 789
    failed_operations: 18
    timeout_operations: 16
    correlation_failures: 0
    timestamp_violations: 0
  
  critical_paths:
    ac_start_to_complete: "TRACED ✅"
    mcp_interface_coverage: "100% ✅"
    toolkit_integration: "VERIFIED ✅"
    lens_validation: "VERIFIED ✅"
    error_visibility: "100% logged ✅"
  
  failures: []
```

### Phase 6.5: MCP Toolkit & LENS Audit (15 min) ⭐ MANDATORY

**Purpose:** Verify MCP exposure and CORTEX LENS/AST validation

**Step 6.5.1: MCP Interface Audit**

```bash
# Identify MCP server exposure violations
# Check for:
# - Unintended exports in __all__
# - Public functions that should be private
# - Missing capability declarations
# - Incorrect authentication/authorization setup

find cortex/mcp/ -name "*.py" -exec grep -l "^__all__" {} \;
grep -r "def _.*(" cortex/mcp/ | grep -v "^#" | wc -l > ${REVIEW_ARTIFACTS}/mcp-private-methods.txt

# Verify MCP toolkit file audit
ls -la cortex/tools/*.py | wc -l > ${REVIEW_ARTIFACTS}/toolkit-file-count.txt

# Cross-reference with cortex-impl-map.yaml
python3 << 'EOF'
import yaml

# Load current toolkit files
import os
toolkit_files = set(os.listdir('cortex/tools/'))

# Load declared toolkit files from impl-map
with open('cortex-impl-map.yaml', 'r') as f:
    impl_map = yaml.safe_load(f)
    declared_tools = set([t.get('file') for t in impl_map.get('toolkit', [])])

# Find undeclared toolkit files (deletion candidates)
undeclared = toolkit_files - declared_tools
with open('${REVIEW_ARTIFACTS}/mcp-toolkit-audit.yaml', 'w') as f:
    yaml.dump({
        'mcp_toolkit_audit': {
            'total_files': len(toolkit_files),
            'declared_in_impl_map': len(declared_tools),
            'undeclared_files': list(undeclared),
            'undeclared_count': len(undeclared),
            'action_required': 'DELETE or DECLARE' if undeclared else 'NONE'
        }
    }, f)
EOF

# Report findings
cat ${REVIEW_ARTIFACTS}/mcp-toolkit-audit.yaml
```

**Step 6.5.2: CORTEX LENS & AST Graphing Validation**

```bash
# Validate LENS protocol implementation
grep -r "cortex.lens" cortex/ | head -20

# Check AST generation correctness
python3 << 'EOF'
import ast
import os

results = {
    'cortex_lens_files': 0,
    'ast_generation_errors': [],
    'missing_lens_validators': 0
}

for root, dirs, files in os.walk('cortex/knowledge'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    ast.parse(f.read())
                results['cortex_lens_files'] += 1
            except SyntaxError as e:
                results['ast_generation_errors'].append({
                    'file': filepath,
                    'error': str(e)
                })

import yaml
with open('${REVIEW_ARTIFACTS}/cortex-lens-ast-validation.yaml', 'w') as f:
    yaml.dump({'cortex_lens_ast_validation': results}, f)
EOF

cat ${REVIEW_ARTIFACTS}/cortex-lens-ast-validation.yaml
```

**Output:** `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/cortex-lens-ast-validation.yaml` and `_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}/mcp-toolkit-audit.yaml`

**Pass Criteria:**
- ✅ No MCP exposure violations
- ✅ All toolkit files declared in impl-map
- ✅ No undeclared toolkit files (or documented justification)
- ✅ LENS validators present in all knowledge components
- ✅ AST generation succeeds for 100% of LENS files

---

### Phase 7: Mandatory Remediation Planning (20 min) ⭐ MANDATORY

**Purpose:** Create executable remediation phases in `_workspaces/roadmap/phases/` and update `cortex-impl-map.yaml`

**Step 7.1: Enumerate All Findings**

Aggregate ALL findings from all phases and agents:
- Phase 1 gaps: FALSE_COMPLETED phases
- Phase 2 stubs: NotImplementedError, TODO comments
- Phase 3 agent findings: All 8 agents (BRIT, HALL, GOV, ASM, DEBT, STATE, ARCH, INTEG)
- Phase 6 audit failures: Any trace/database inconsistencies
- Phase 6.5 MCP violations: Exposure or toolkit issues

**Step 7.2: Create Remediation Phases**

Create separate remediation phase files in `_workspaces/roadmap/phases/`:

```yaml
# _workspaces/roadmap/phases/phase-001-critical-blockers.yaml
# Generated from review: {REVIEW_TIMESTAMP}

phase:
  id: "phase-001"
  name: "Critical Blockers - Production Readiness"
  priority: 1
  blocking_deployment: true
  source_review: "{REVIEW_TIMESTAMP}"
  source_artifacts: "_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}"
  
  items:
    - id: "REM-CRIT-001"
      source_finding: "BRIT-SPOF-003"
      issue: "Race condition in AC_START lifecycle"
      description: "Multiple concurrent AC_START calls can corrupt state"
      remediation: "Add mutex lock around AC state transition"
      responsible_component: "cortex/orchestrators/orchestrator.py"
      priority: 1
      depends_on: []
      estimated_effort_hours: 4
      completion_criterion: "Unit test + integration test passing"
      status: "PENDING"
    
    - id: "REM-CRIT-002"
      source_finding: "INTEG-TIMEOUT-001"
      issue: "External API calls missing timeout"
      description: "No timeout on external API calls can hang indefinitely"
      remediation: "Add 30s timeout + retry logic to all external calls"
      responsible_component: "cortex/api/external_service_client.py"
      priority: 2
      depends_on: ["REM-CRIT-001"]
      estimated_effort_hours: 3
      completion_criterion: "All calls have timeout, no silent failures"
      status: "PENDING"
  
  completion_checklist:
    - [ ] All items in this phase completed
    - [ ] All tests passing (unit + integration)
    - [ ] Code review approved
    - [ ] Audit trace validation passed
    - [ ] Ready for deployment
  
  total_effort_hours: 7
  blocking_deployment: true

# _workspaces/roadmap/phases/phase-002-architecture-refactoring.yaml
# Generated from review: {REVIEW_TIMESTAMP}

phase:
  id: "phase-002"
  name: "Architecture Refactoring - SOLID Principles"
  priority: 2
  blocking_deployment: false
  source_review: "{REVIEW_TIMESTAMP}"
  source_artifacts: "_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}"
  
  items:
    - id: "REM-HIGH-001"
      source_finding: "ARCH-SRP-002"
      issue: "Orchestrator class violates SRP (850 lines, 4 concerns)"
      description: |
        The Orchestrator class handles scheduling, execution, logging, and persistence.
        This violates Single Responsibility Principle and makes testing difficult.
      remediation: "Split into Orchestrator, Scheduler, Logger, PersistenceManager"
      responsible_component: "cortex/orchestrators/orchestrator.py"
      priority: 3
      depends_on: ["REM-CRIT-001"]
      estimated_effort_hours: 16
      completion_criterion: "Class max 200 lines, 1 concern each"
      status: "PENDING"
  
  completion_checklist:
    - [ ] All items in this phase completed
    - [ ] All tests passing (unit + integration)
    - [ ] Code review approved
    - [ ] Performance metrics unchanged or improved
    - [ ] Ready for next phase
  
  total_effort_hours: 16
  blocking_deployment: false

# _workspaces/roadmap/phases/phase-003-technical-debt.yaml
# Generated from review: {REVIEW_TIMESTAMP}

phase:
  id: "phase-003"
  name: "Technical Debt Remediation"
  priority: 3
  blocking_deployment: false
  source_review: "{REVIEW_TIMESTAMP}"
  source_artifacts: "_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}"
  
  items:
    - id: "REM-MED-001"
      source_finding: "DEBT-DUP-015"
      issue: "Error handling duplicated in 8 locations"
      description: "Error handling logic repeated instead of abstracted"
      remediation: "Extract to ErrorHandler utility class"
      responsible_component: "cortex/common/error_handler.py"
      priority: 5
      depends_on: ["REM-CRIT-001", "REM-CRIT-002"]
      estimated_effort_hours: 6
      completion_criterion: "DRY principle applied, tests passing"
      status: "PENDING"
  
  completion_checklist:
    - [ ] All items in this phase completed
    - [ ] Code duplication reduced by ≥ 50%
    - [ ] All tests passing
    - [ ] Code review approved
  
  total_effort_hours: 6
  blocking_deployment: false
```

Also update `cortex-impl-map.yaml` with reference to phases:

```yaml
# Add to cortex-impl-map.yaml

remediation:
  version: "2.0"
  created: "{REVIEW_TIMESTAMP}"
  review_artifacts: "_workspaces/roadmap/issues/{REVIEW_TIMESTAMP}"
  phases_directory: "_workspaces/roadmap/phases"
  
  # Reference to individual phase files
  phase_references:
    - file: "_workspaces/roadmap/phases/phase-001-critical-blockers.yaml"
      priority: 1
      blocking_deployment: true
    
    - file: "_workspaces/roadmap/phases/phase-002-architecture-refactoring.yaml"
      priority: 2
      blocking_deployment: false
    
    - file: "_workspaces/roadmap/phases/phase-003-technical-debt.yaml"
      priority: 3
      blocking_deployment: false
  
  execution_roadmap:
    phase_1_blockers:
      name: "Fix Critical Blockers (Week 1)"
      file: "_workspaces/roadmap/phases/phase-001-critical-blockers.yaml"
      total_effort_hours: 7
      blocking_deployment: true
    
    phase_2_architecture:
      name: "Refactor Architecture (Week 2-3)"
      file: "_workspaces/roadmap/phases/phase-002-architecture-refactoring.yaml"
      total_effort_hours: 28
      blocking_deployment: false
    
    phase_3_technical_debt:
      name: "Address Technical Debt (Week 4)"
      file: "_workspaces/roadmap/phases/phase-003-technical-debt.yaml"
      total_effort_hours: 18
      blocking_deployment: false
  
  completion_checklist:
    - [ ] All CRITICAL items in phase_001 completed and tested
    - [ ] All HIGH items in phase_002 completed and tested
    - [ ] All MEDIUM items in phase_003 addressed
    - [ ] Re-run audit trace validation after each CRITICAL fix
    - [ ] Update phase YAML files weekly with progress
    - [ ] Obtain approval before closing any remediation item
```

**Step 7.3: Validation Before Completion**

```bash
# Verify remediation phases exist and are valid
python3 << 'EOF'
import yaml
import os
from pathlib import Path

phases_dir = Path("_workspaces/roadmap/phases")
impl_map_file = Path("cortex-impl-map.yaml")

# Check 1: phases directory exists
if not phases_dir.exists():
    print("❌ FAILURE: phases directory not found")
    exit(1)

# Check 2: phase files exist
phase_files = list(phases_dir.glob("phase-*.yaml"))
if len(phase_files) == 0:
    print("❌ FAILURE: No phase YAML files found")
    exit(1)

print(f"✅ Found {len(phase_files)} remediation phase files:")
for phase_file in sorted(phase_files):
    with open(phase_file) as f:
        phase = yaml.safe_load(f)
    if 'phase' in phase:
        p = phase['phase']
        print(f"   - {phase_file.name}")
        print(f"     ID: {p.get('id')}, Priority: {p.get('priority')}")
        print(f"     Items: {len(p.get('items', []))}")
        print(f"     Effort: {p.get('total_effort_hours')} hours")

# Check 3: impl-map references phases
if impl_map_file.exists():
    with open(impl_map_file) as f:
        impl_map = yaml.safe_load(f)
    
    if 'remediation' in impl_map:
        remediation = impl_map['remediation']
        if 'phase_references' in remediation:
            print(f"\n✅ cortex-impl-map.yaml references {len(remediation['phase_references'])} phases")
        else:
            print("\n⚠ cortex-impl-map.yaml remediation section found but no phase_references")
else:
    print("\n⚠ cortex-impl-map.yaml not found")

print("\n✅ REMEDIATION PHASES VALID")
EOF
```

**Output:** 
- Multiple phase files: `_workspaces/roadmap/phases/phase-{number}-{name}.yaml`
- Updated `cortex-impl-map.yaml` with `remediation.phase_references`
- Each phase file is independent and can be executed separately
- Phases reference source findings via review timestamp

---

**Total Time: 2.5-3 hours** (includes audit trace + remediation planning)

---

## 📊 AGENT EXECUTION QUICK START

### Full Review Execution (2.5-3 hours total)

```bash
# Step 0: Create timestamped artifacts directory
export REVIEW_TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
export REVIEW_ARTIFACTS="_workspaces/roadmap/issues/${REVIEW_TIMESTAMP}"
mkdir -p "${REVIEW_ARTIFACTS}"
echo "Review artifacts: ${REVIEW_ARTIFACTS}"

# Phase 0: Pre-Review Validation (15 min)
/review validate --output ${REVIEW_ARTIFACTS}/

# Phase 1-2: Gap and Stub Detection (35 min)
/review gaps --output ${REVIEW_ARTIFACTS}/
/review stubs --output ${REVIEW_ARTIFACTS}/

# Phase 3: BATCH 1 - Core Quality Checks (run in parallel - 12 min)
/review agent --name brittleness --output ${REVIEW_ARTIFACTS}/ &
/review agent --name hallucination --output ${REVIEW_ARTIFACTS}/ &
/review agent --name governance --output ${REVIEW_ARTIFACTS}/ &
wait

# Phase 3: BATCH 2 - Architecture & Operations (run in parallel - 15 min)
/review agent --name assumptions --output ${REVIEW_ARTIFACTS}/ &
/review agent --name debt --output ${REVIEW_ARTIFACTS}/ &
/review agent --name state-concurrency --output ${REVIEW_ARTIFACTS}/ &
/review agent --name architecture --output ${REVIEW_ARTIFACTS}/ &
/review agent --name integration-observability --output ${REVIEW_ARTIFACTS}/ &
wait

# Phase 4: Requirements Analysis (10 min)
/review requirements --output ${REVIEW_ARTIFACTS}/

# Phase 4.5: Instruction Alignment Validation (15 min) ⭐ NEW
/review instruction-alignment --output ${REVIEW_ARTIFACTS}/

# Phase 5: Consolidate all findings (20 min)
/review consolidate --from ${REVIEW_ARTIFACTS}/Findings-*.yaml \
                   --include ${REVIEW_ARTIFACTS}/instruction-alignment.yaml \
                   --output ${REVIEW_ARTIFACTS}/review-findings-consolidated.yaml

# Phase 6: Audit Trace & End-to-End Validation (25 min) ⭐ MANDATORY
/review audit-trace --output ${REVIEW_ARTIFACTS}/
/review mcp-audit --output ${REVIEW_ARTIFACTS}/
/review lens-validation --output ${REVIEW_ARTIFACTS}/

# Phase 7: Mandatory Remediation Planning (20 min) ⭐ MANDATORY
/review remediation-plan --output ${REVIEW_ARTIFACTS}/ \
                        --update-impl-map cortex-impl-map.yaml

# Final Summary
echo "=========================================="
echo "REVIEW COMPLETE"
echo "=========================================="
ls -la ${REVIEW_ARTIFACTS}/
echo ""
echo "Key files:"
echo "  - Gap Analysis: ${REVIEW_ARTIFACTS}/review-gap-inventory.yaml"
echo "  - Consolidated Findings: ${REVIEW_ARTIFACTS}/review-findings-consolidated.yaml"
echo "  - Audit Trace Report: ${REVIEW_ARTIFACTS}/audit-trace-validation.yaml"
echo "  - Remediation Plan: cortex-impl-map.yaml (remediation track)"
echo "=========================================="
```

### Parallel Agent Execution (27 min total)

```bash
# BATCH 1: Core Quality Checks (run in parallel - 12 min)
/review agent --name brittleness &
/review agent --name hallucination &
/review agent --name governance &
wait

# BATCH 2: Architecture & Operations (run in parallel - 15 min)
/review agent --name assumptions &
/review agent --name debt &
/review agent --name state-concurrency &
/review agent --name architecture &
/review agent --name integration-observability &
wait

# Results: 8 YAML files in _workspaces/roadmap/issues/${REVIEW_TIMESTAMP}/
ls -la _workspaces/roadmap/issues/${REVIEW_TIMESTAMP}/Findings-*.yaml
```

### Individual Agent Execution

```bash
# Run single agent
/review agent --name brittleness --output _workspaces/roadmap/issues/${REVIEW_TIMESTAMP}/

# Run full review workflow with artifact persistence
/review full --output _workspaces/roadmap/issues/${REVIEW_TIMESTAMP}/

# Show consolidated findings
/review consolidate --from _workspaces/roadmap/issues/${REVIEW_TIMESTAMP}/Findings-*.yaml

# Validate audit traces
/review audit-trace --output _workspaces/roadmap/issues/${REVIEW_TIMESTAMP}/
```

---

## 🆕 NEW AGENTS (v4.1 Enhancement)

### Agent 6: STATE MANAGEMENT & CONCURRENCY ⭐ NEW

**File:** `.github/agents/cortex-review-state-concurrency.md`

**Checks:**
- Race conditions (check-then-act patterns)
- Deadlock risks (lock ordering, nested acquisition)
- Atomicity violations (multi-step operations)
- Memory visibility issues (cached values, thread-local)
- Global state contamination (module-level mutable state)
- Async/await pitfalls (missing await, blocking in async)
- Event ordering bugs (synchronization gaps)

**Why Critical:** State bugs are invisible during unit testing but catastrophic under concurrent load.

**Output:** `Findings-STATE-YYYYMMDD.yaml`

**Example Findings:**
```yaml
state_management_findings:
  race_conditions:
    - component: "cortex/knowledge/cache.py"
      issue: "Check-then-act race condition on cache.get_or_compute()"
      severity: "CRITICAL"
      affected_ac_ids: ["AC-CACHE-001"]
  
  deadlock_risks:
    - component: "cortex/orchestrators/coordinator.py"
      issue: "Nested lock acquisition without timeout"
      severity: "HIGH"
```

### Agent 7: ARCHITECTURE & DESIGN PATTERNS ⭐ NEW

**File:** `.github/agents/cortex-review-architecture.md`

**Checks:**
- SOLID principle violations (SRP, OCP, LSP, ISP, DIP)
- Coupling anti-patterns (feature envy, Law of Demeter, circular deps)
- Inheritance misuse (deep hierarchies, wrong "is-a" relationships)
- Abstraction failures (missing abstractions, leaky abstractions)
- Design pattern misuse (singleton unsafe, factory for one, observer leaks)

**Why Critical:** Architectural flaws multiply across entire codebase. One bad design choice creates 10 instances of brittleness.

**Output:** `Findings-ARCH-YYYYMMDD.yaml`

**Example Findings:**
```yaml
architecture_findings:
  srp_violations:
    - component: "cortex/orchestrators/orchestrator.py"
      issue: "850-line class handles scheduling, execution, logging, persistence"
      severity: "HIGH"
      concerns_count: 4
  
  dependency_inversions:
    - component: "cortex/execution/executor.py"
      issue: "Hard-coded dependencies instead of injection"
      hard_coded_instantiations: 12
      severity: "HIGH"
```

### Agent 8: INTEGRATION, OBSERVABILITY & OPERATIONS ⭐ NEW

**File:** `.github/agents/cortex-review-integration-observability.md`

**Checks:**
- Integration boundary failures (missing timeouts, no retry logic, silent errors)
- Observability gaps (missing logging, no structured logging, no metrics)
- Error propagation failures (error suppression, no graceful degradation, no circuit breakers)
- Data consistency issues (no validation at boundaries, partial updates, referential integrity)
- Deployment safety (no backward compatibility, missing health checks)
- Configuration management (hard-coded values, secrets in logs)
- Production readiness (no monitoring, no shutdown handling, no rate limiting)

**Why Critical:** Integration and observability failures are invisible during dev but catastrophic in production.

**Output:** `Findings-INTEG-YYYYMMDD.yaml`

**Example Findings:**
```yaml
integration_observability_findings:
  integration_boundary_failures:
    - component: "cortex/api/external_service_client.py"
      issue: "No timeout on external API calls"
      severity: "CRITICAL"
      affected_ac_ids: ["AC-API-001"]
  
  observability_gaps:
    - component: "cortex/orchestrators/orchestrator.py"
      issue: "Missing structured logging at critical points"
      severity: "HIGH"
      critical_points_unlogged: 8
```

---

## 📋 ENHANCED FLAW COVERAGE

**Original v4.0 Coverage:**
- ✅ Implementation gaps
- ✅ Brittleness (load/concurrency basics)
- ✅ Hallucination/AI safety
- ✅ Governance compliance
- ✅ Assumptions/dependencies
- ✅ Technical debt

**New v4.1 Coverage (3 additional agents):**
- ✅ State management & concurrency (deep dive)
- ✅ Architecture & design patterns (structural issues)
- ✅ Integration & observability (system boundaries + operations)

**Combined Flaw Detection:**
- 61+ flaw categories covered across 8 agents
- Race conditions, deadlocks, atomicity
- SOLID violations, design pattern misuse, coupling
- Integration boundary issues, observability gaps
- Production readiness assessment

---

## 🎯 EVIDENCE GRADING

**A-Grade (95%+ confidence):** Direct verification
- Code inspection (grep, read file)
- Test failure/success
- Compile/type error
- SQL query results

**B-Grade (80-95% confidence):** Strong inference
- Multiple corroborating data points
- Pattern observed in multiple places
- High probability but not 100% certain

**C-Grade (70-80% confidence):** REJECTED
- Speculation without evidence
- No C-grade findings allowed in reports
- Upgrade to A/B or don't report

---

## 📊 SEVERITY CLASSIFICATION

```
CRITICAL (Blocks Deployment)
├─ Race conditions in AC lifecycle
├─ Type hints missing (CORE-011)
├─ AI safety vulnerabilities
├─ No timeout on external calls
├─ Silent failure patterns
└─ Dead locks without timeout

HIGH (Should Fix Before Deployment)
├─ Bare except clauses
├─ Uncovered code paths (< 85%)
├─ Unvalidated LLM output
├─ Performance anti-patterns
├─ Missing logging/metrics
└─ Hard-coded dependencies

MEDIUM (Fix in Next Phase)
├─ Code duplication
├─ Documentation gaps
├─ Deprecated patterns
├─ SOLID principle violations
└─ Architectural coupling

LOW (Nice-to-Have)
├─ Code style improvements
├─ Non-critical optimizations
├─ Minor refactoring opportunities
```

---

## 📁 OUTPUT STRUCTURE - PERSISTENT ARTIFACTS ⭐ MANDATORY

**Gap Reports persisted to timestamped issue directory:**
```
_workspaces/roadmap/
├─ issues/
│  ├─ 2026-01-23_143022/                    ← Review execution #{timestamp}
│  │  ├─ review-gap-inventory.yaml          ⭐ Phase 1 output
│  │  ├─ review-stubs.yaml                  ⭐ Phase 2 output
│  │  ├─ Findings-BRIT.yaml                 ⭐ Agent 1
│  │  ├─ Findings-HALL.yaml                 ⭐ Agent 2
│  │  ├─ Findings-GOV.yaml                  ⭐ Agent 3
│  │  ├─ Findings-ASM.yaml                  ⭐ Agent 4
│  │  ├─ Findings-DEBT.yaml                 ⭐ Agent 5
│  │  ├─ Findings-STATE.yaml                ⭐ Agent 6
│  │  ├─ Findings-ARCH.yaml                 ⭐ Agent 7
│  │  ├─ Findings-INTEG.yaml                ⭐ Agent 8
│  │  ├─ requirements-analysis.yaml         ⭐ Phase 4
│  │  ├─ instruction-alignment.yaml         ⭐ Phase 4.5 (NEW)
│  │  ├─ review-findings-consolidated.yaml  ⭐ Phase 5
│  │  ├─ audit-trace-validation.yaml        ⭐ Phase 6
│  │  ├─ mcp-toolkit-audit.yaml             ⭐ Phase 6.5
│  │  └─ cortex-lens-ast-validation.yaml    ⭐ Phase 6.5
│  ├─ 2026-01-22_102015/                    ← Previous review
│  │  └─ [all artifacts from that execution]
│  └─ [archive of all previous executions]
│
├─ phases/                                   ← NEW: Remediation phases
│  ├─ phase-001-critical-blockers.yaml       ⭐ Generated from 2026-01-23_143022 review
│  ├─ phase-002-architecture-refactoring.yaml ⭐ Generated from 2026-01-23_143022 review
│  ├─ phase-003-technical-debt.yaml          ⭐ Generated from 2026-01-23_143022 review
│  └─ [future phases from subsequent reviews]
│
└─ reports/                                  ← Summary reports (optional)
   └─ [summary reports cross-linking issues and phases]
```

**Remediation tracking in cortex-impl-map.yaml:**
```yaml
cortex-impl-map.yaml
└─ remediation:
   ├─ version: "2.0"
   ├─ created: "2026-01-23T14:55:18Z"
   ├─ review_artifacts: "_workspaces/roadmap/issues/2026-01-23_143022"
   ├─ phases_directory: "_workspaces/roadmap/phases"
   ├─ phase_references:
   │  ├─ file: "_workspaces/roadmap/phases/phase-001-critical-blockers.yaml"
   │  ├─ file: "_workspaces/roadmap/phases/phase-002-architecture-refactoring.yaml"
   │  └─ file: "_workspaces/roadmap/phases/phase-003-technical-debt.yaml"
   └─ execution_roadmap: [references to phases]
```

---

**PERSISTENCE GUARANTEES:**

❌ **FORBIDDEN:**
- Ephemeral output (printed to console only)
- Temporary files not saved to disk
- Report loss after execution
- Console-only error messages
- Stdout-only logging
- Test artifacts not preserved

**✅ REQUIRED:**
- All gap reports written to `_workspaces/roadmap/issues/<timestamp>/`
- All remediation phases written to `_workspaces/roadmap/phases/`
- Each phase file is independent and traceable to source review
- Remediation plan persisted to `cortex-impl-map.yaml` with phase references
- All findings correlated back to source files/locations
- Execution metadata (timestamp, status, duration) in every report
- Historical archive of all previous executions preserved
- Phase files reference source review via review timestamp

---

## 🚨 CRITICAL BLOCKERS (Must Fix Before Production)

**State Management:**
- Race conditions in AC_START/EXECUTE/COMPLETE
- Deadlocks in orchestrator coordination
- Global state contamination

**Architecture:**
- Dependency injection missing (hard-coded dependencies)
- SOLID violations in core components
- Circular dependencies

**Integration:**
- External calls without timeout → CRITICAL
- Silent failures (bare except) → CRITICAL
- Missing health check endpoints

**Observability:**
- No structured logging → HIGH
- No correlation IDs → HIGH
- No circuit breakers → CRITICAL

---

## ✅ COMPLETION CRITERIA - MANDATORY GATES ⭐

**The review is NOT complete unless ALL criteria are met:**

### Gate 1: Persistent Artifact Storage ⭐ MANDATORY
```yaml
artifacts_persisted:
  - [ ] Timestamped directory created: _workspaces/roadmap/issues/<YYYY-MM-DD_HHMMSS>/
  - [ ] All 8 agent findings written to disk
  - [ ] Gap inventory persisted
  - [ ] Stub detection results persisted
  - [ ] Requirements analysis persisted
  - [ ] Consolidated report persisted
  - [ ] No ephemeral-only output
  - [ ] All files readable post-execution
```

### Gate 2: End-to-End Audit Trace Validation ⭐ MANDATORY
```yaml
audit_trace_validation:
  - [ ] Runtime audit logs inspected (found ≥ 1 trace file)
  - [ ] Database audit logs queried (found ≥ 100 records)
  - [ ] Trace continuity verified (gaps < 2 seconds)
  - [ ] All critical paths traced:
      - [ ] AC_START → AC_COMPLETE traced
      - [ ] MCP interface operations logged
      - [ ] TOOLKIT operations logged
      - [ ] LENS validation operations logged
  - [ ] Error visibility confirmed (all errors logged)
  - [ ] No missing operations (100% operation logging)
  - [ ] Audit trace validation report written: audit-trace-validation.yaml
  - [ ] Status: PASSED (not WARNING, not UNKNOWN)
```

### Gate 3: MCP Exposure & Toolkit Audit ⭐ MANDATORY
```yaml
mcp_toolkit_audit:
  - [ ] MCP interface audit performed
  - [ ] Toolkit file inventory created
  - [ ] Undeclared toolkit files identified
  - [ ] Toolkit audit report written: mcp-toolkit-audit.yaml
  - [ ] LENS/AST validation performed: cortex-lens-ast-validation.yaml
  - [ ] No unintended MCP exposures found
  - [ ] All toolkit files accounted for (no orphaned files)
```

### Gate 4: Mandatory Remediation Planning ⭐ MANDATORY
```yaml
remediation_planning:
  - [ ] Remediation phases directory created: _workspaces/roadmap/phases/
  - [ ] Phase files created for each priority level
  - [ ] remediation.phase_references populated in cortex-impl-map.yaml
  - [ ] Each phase file has execution_roadmap entry
  - [ ] All findings from phases 1-6 mapped to remediation items
  - [ ] Dependency ordering correct (uses depends_on)
  - [ ] Priority levels assigned (1-10)
  - [ ] Effort estimates provided for all items
  - [ ] Responsible components assigned
  - [ ] Completion criteria defined for each item
  - [ ] Phase files are independent and self-contained
  - [ ] Source review timestamp included in all phase files
```

### Gate 5: Review Pass/Fail Declaration ⭐ MANDATORY
```yaml
final_declaration:
  - [ ] Review completion status documented
  - [ ] CORTEX passes or CORTEX fails (explicit statement)
  - [ ] All mandatory gates passed before declaring PASS
  - [ ] Any failed gate → Review FAILS (not warning)
  - [ ] Final report: review-findings-consolidated.yaml includes:
      - [ ] Pass/fail status (explicit)
      - [ ] Artifacts location (timestamped path)
      - [ ] Audit trace status (PASSED or FAILED)
      - [ ] MCP audit status (PASSED or FAILED)
      - [ ] Remediation plan location (cortex-impl-map.yaml)
      - [ ] Summary of critical blockers
      - [ ] Next steps (remediation phase link)
```

---

### Example Final Declaration (in review-findings-consolidated.yaml)

```yaml
review_completion:
  status: "PASSED" | "FAILED"
  timestamp: "2026-01-23T14:55:18Z"
  review_artifacts: "_workspaces/roadmap/issues/2026-01-23_143022"
  
  mandatory_gates:
    persistent_artifacts: "PASSED ✅"
    audit_trace_validation: "PASSED ✅"
    mcp_toolkit_audit: "PASSED ✅"
    remediation_planning: "PASSED ✅"
  
  if_any_gate_failed:
    status: "FAILED ❌"
    blocker_details: "Audit trace validation failed: gaps > 2 seconds detected"
    action_required: "Investigate and fix trace gaps before retry"
  
  cortex_production_readiness:
    declaration: "CORTEX PASSES review - ready for deployment"
    or_declaration: "CORTEX FAILS review - critical blockers must be fixed"
    
  remediation_phases:
    location: "_workspaces/roadmap/phases/"
    phases_created: 3
    critical_phase: "_workspaces/roadmap/phases/phase-001-critical-blockers.yaml"
    link: "Execute phases in priority order before next deployment"
    tracking: "cortex-impl-map.yaml :: remediation.phase_references"
  
  audit_trail_summary:
    runtime_logs_found: 12
    database_records: 847
    trace_completeness: "98.7%"
    critical_paths_traced: "✅ ALL"
  
  next_steps:
    - "Review remediation phases in _workspaces/roadmap/phases/"
    - "Start with phase-001-critical-blockers.yaml"
    - "Follow dependency ordering in each phase"
    - "Update phase YAML files as work progresses"
    - "Re-run audit trace validation after critical blockers fixed"
    - "Schedule next review cycle (weekly recommended)"
```

---

## ✅ VALIDATION CHECKLIST (Previous Version - Retained for Reference)

Before shipping to production:

```yaml
gate_checks:
  data_quality:
    - [ ] Phase 0 all gates passed
    - [ ] No test artifacts in production audit log
    - [ ] Hash chain integrity verified
  
  implementation:
    - [ ] No FALSE_COMPLETED phases
    - [ ] All CRITICAL stubs remediated
    - [ ] Test coverage >= 85%
  
  code_quality:
    - [ ] No bare except clauses
    - [ ] No unhandled exceptions
    - [ ] No memory leaks (finally blocks)
  
  safety:
    - [ ] LLM outputs validated
    - [ ] Prompt injection prevented
    - [ ] Type hints 100% (CORE-011)
  
  architecture:
    - [ ] Dependencies injected (no hard-coded)
    - [ ] SOLID principles followed
    - [ ] No circular dependencies
  
  integration:
    - [ ] All external calls have timeout
    - [ ] No silent failures
    - [ ] Health checks implemented
  
  observability:
    - [ ] Structured logging in place
    - [ ] Correlation IDs tracked
    - [ ] Metrics collection enabled
  
  operations:
    - [ ] Graceful shutdown implemented
    - [ ] Rate limiting configured
    - [ ] Circuit breakers in place
```

---

## 🔄 COMPLETE WORKFLOW SUMMARY

```
PRE-EXECUTION: Create timestamped artifacts directory
    ↓
Phase 0: Validation (15 min)
    ↓ (gates pass)
Phase 1: Gap Inventory (15 min)
    ↓
Phase 2: Stub Detection (20 min)
    ↓
Phase 3: 8-Agent Analysis (Parallel - 27 min)
    ├─ Batch 1: Brittleness, Hallucination, Governance (12 min)
    └─ Batch 2: Assumptions, Debt, State, Architecture, Integration (15 min)
    ↓
Phase 4: Requirements Analysis (10 min)
    ↓
Phase 4.5: Instruction Alignment Validation ⭐ NEW (15 min)
    ├── Version alignment check
    ├── Component coverage verification
    ├── Governance rule count validation
    └── Outdated instruction detection
    ↓
Phase 5: Consolidated Report (20 min)
    ↓
Phase 6: Audit Trace & E2E Validation ⭐ MANDATORY (25 min)
    ├─ Runtime audit trace inspection
    ├─ Database audit log queries
    ├─ MCP interface audit
    └─ LENS/AST validation
    ↓
Phase 7: Mandatory Remediation Planning ⭐ MANDATORY (20 min)
    ├─ Enumerate all findings
    ├─ Create remediation track
    ├─ Define execution roadmap
    └─ Update cortex-impl-map.yaml
    ↓
COMPLETION: All 5 mandatory gates passed
    ├─ Persistent artifacts persisted ✅
    ├─ Audit trace validated ✅
    ├─ MCP/Toolkit audited ✅
    ├─ Remediation plan created ✅
    └─ Pass/Fail declared ✅
    ↓
Handoff to cortex-builder.prompt.md for remediation execution
```

**Total Workflow Time: 2.5-3 hours**

---

## 📞 AGENT FILE LOCATIONS

All agents available in: `.github/agents/`

```
cortex-review-brittleness.md              (12 KB, original)
cortex-review-hallucination.md            (8 KB, original)
cortex-review-governance.md               (8 KB, original)
cortex-review-assumptions.md              (9 KB, original)
cortex-review-debt.md                     (10 KB, original)
cortex-review-state-concurrency.md        (15 KB, NEW)
cortex-review-architecture.md             (14 KB, NEW)
cortex-review-integration-observability.md (16 KB, NEW)
```

---

## 🎓 KEY PRINCIPLES

1. **Never speculate** - Only A/B grade evidence allowed
2. **No silent failures** - All errors must be logged with context
3. **Evidence first** - Every finding must cite specific code locations
4. **Production safety** - All CRITICAL findings must be remediated
5. **Observability required** - All operations must be visible
6. **Testing required** - Code coverage >= 85% minimum
7. **Architecture matters** - Design flaws multiply across codebase
8. **Integration safety** - All external calls must have timeout + retry

---

## ✨ SUMMARY OF ENHANCEMENTS (v4.1)

**v4.0 → v4.1 CORE ENHANCEMENTS:**

### New Phases (Mandatory):
- ✅ **Phase 6:** Audit Trace & End-to-End Validation
  - Runtime audit log inspection
  - Database audit log verification
  - MCP toolkit audit
  - CORTEX LENS/AST validation
  
- ✅ **Phase 7:** Mandatory Remediation Planning
  - Remediation track in cortex-impl-map.yaml
  - Executive remediation roadmap
  - Priority + dependency ordering

### New Persistence Requirements:
- ✅ All outputs written to timestamped directories
- ✅ Historical archive of all executions preserved
- ✅ No ephemeral-only output allowed
- ✅ All artifacts discoverable and auditable

### New Completion Gates (Mandatory):
- ✅ **Gate 1:** Persistent artifact storage verified
- ✅ **Gate 2:** End-to-end audit trace validation passed
- ✅ **Gate 3:** MCP exposure & toolkit audit passed
- ✅ **Gate 4:** Remediation planning complete
- ✅ **Gate 5:** Pass/fail explicitly declared

### New Agents (v4.1):
- ✅ Agent 6: State Management & Concurrency
- ✅ Agent 7: Architecture & Design Patterns
- ✅ Agent 8: Integration, Observability & Operations

### Combined Coverage:
- 8 agents vs 5 agents
- 61+ flaw categories detectable
- 5 mandatory completion gates (vs 1 simple checklist)
- Full end-to-end trace validation
- Executable remediation roadmap
- 2.5-3 hours total workflow (includes audit + remediation)
- 95% confidence findings (A/B grade evidence only)

---

## 🎯 KEY PRINCIPLES FOR v4.1

1. **Never speculate** - Only A/B grade evidence allowed
2. **No ephemeral output** - All artifacts persisted to disk
3. **End-to-end validated** - Audit traces verify true functionality
4. **Remediable** - Every finding has concrete remediation plan
5. **Executable** - Remediation roadmap prioritized + sequenced
6. **Non-brittle** - Audit logs prove robustness, not just test passage
7. **Production-ready** - All CRITICAL findings must be fixed
8. **Auditable** - Every execution timestamped + archived
9. **Traceable** - All findings correlated to source code locations
10. **Mandatory completion gates** - No workarounds, no warnings

---

**Status:** ✅ ENHANCED WITH MANDATORY AUDIT & REMEDIATION (v4.1.1)  
**Version:** 4.1.1 (Comprehensive Flaw Detection + Persistent Reporting + End-to-End Validation)  
**Date:** January 23, 2026  

**Key Enhancements in v4.1.1:**
- ✅ **Persistent Reporting:** All outputs to timestamped directories (_workspaces/roadmap/issues/<YYYY-MM-DD_HHMMSS>/)
- ✅ **End-to-End Validation:** Runtime + database audit trace verification (Phase 6 - MANDATORY)
- ✅ **Mandatory Remediation Planning:** Executable roadmap in cortex-impl-map.yaml (Phase 7 - MANDATORY)
- ✅ **5 Mandatory Completion Gates:** All must pass before review complete (no exceptions)
- ✅ **MCP Toolkit Audit:** Exposure violations + undeclared file detection
- ✅ **CORTEX LENS/AST Validation:** Knowledge component AST parsing verification
- ✅ **Non-Brittle Production Readiness:** Proven via real audit traces (not just unit tests)

**Workflow Time:** 2.5-3 hours (includes audit trace validation + remediation planning)

**Critical Changes:**
- All review findings are NOW PERMANENTLY PERSISTED with execution timestamp
- End-to-end functionality MUST be validated via runtime audit logs + database queries
- Remediation planning is NO LONGER OPTIONAL - executes as final phase
- Pass/Fail decision CANNOT be made until all 5 gates pass
- Review artifacts are ARCHIVED for historical audit trail
- No ephemeral-only output allowed under any circumstances  
