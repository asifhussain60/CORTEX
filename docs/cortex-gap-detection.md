# CORTEX Gap Detection & Enforcement Agent

**Purpose:** Systematically identify and track "Design-Build Gaps" where functionality is designed in YAML but NOT properly implemented, exposed, or integrated.

**Version**: 1.0 (2026-01-18)
**Status**: ACTIVE - Review-Enhanced v2.0 Integration

---

## CRITICAL GAP PATTERN ANALYSIS

### Pattern Definition: Design-Build Gap

A **Design-Build Gap** exists when:

1. **Component is DESIGNED** in phase YAML with clear AC-IDs
2. **AC-IDs are COMPLETED** (100% test pass rate)
3. **BUT** the component is NOT:
   - Properly exposed via MCP (if tool-eligible)
   - Integrated with governance enforcement
   - Accessible to downstream consumers
   - Discoverable via standard interfaces
   - Documented for external consumption

### Evidence: MCP Gap as Case Study

**MCP Gap Finding**: FINDING-MCP-001 (CRITICAL)

| Aspect | Status | Gap |
|--------|--------|-----|
| **Design** | ✅ PHASE-02 AC-AR-007-01/02/03 defined | 0% |
| **Implementation** | ✅ 17 MCP tools implemented + server created | 0% |
| **AC Completion** | ✅ 100% tests passing | 0% |
| **SDK Integration** | ❌ mcp package NOT in requirements.txt | **CRITICAL** |
| **Transport Protocol** | ❌ Custom HTTP not MCP JSON-RPC stdio | **CRITICAL** |
| **Tool Exposure** | ⚠️ 17/40+ tools decorated (42% coverage) | **HIGH** |
| **Configuration Files** | ❌ No claude_desktop_config.json | **HIGH** |
| **External Accessibility** | ❌ Cannot be used via Claude/VS Code | **CRITICAL** |

**Root Cause**: Infrastructure designed but last-mile integration missing.

---

## SIMILAR GAPS DETECTED

### Gap Category 1: Infrastructure Designed, Not Exposed

| Component | Phase | Status | Gap |
|-----------|-------|--------|-----|
| **MCP Server** | PHASE-02 | ✅ Built | ❌ Not spec-compliant |
| **Governance Enforcement** | PHASE-01 | ✅ Built | ⚠️ Partially enforced |
| **Audit Trail** | PHASE-01 | ✅ Database exists | ⚠️ Not auto-logged in tests |
| **CORTEX LENS** | PHASE-16 | ✅ Implemented | ⚠️ Not exposed as tool |
| **Knowledge Router** | PHASE-21 | 🟡 Designed | ❌ Not implemented |

### Gap Category 2: Tools Designed, Not Exposed via MCP

| Tool | Location | Status | MCP-Exposed? |
|------|----------|--------|-------------|
| OrchestratorScaffolder | `src/tools/orchestrator_scaffolder.py` | ✅ Implemented | ❌ NO @mcp_tool |
| PhaseReadinessChecker | `src/tools/phase_readiness_checker.py` | ✅ Implemented | ❌ NO @mcp_tool |
| BKIOOrchestrator | `src/domain_brain/bkio_orchestrator.py` | ✅ Implemented | ❌ NO @mcp_tool |
| DependencyValidator | `src/core/dependency_validator.py` | ✅ Implemented | ❌ NO @mcp_tool |
| LensSynthesis | `src/orchestrators/core/lens_synthesis.py` | ✅ Implemented | ❌ NO @mcp_tool |
| IntentRouter | `src/orchestrators/core/intent_router.py` | ✅ Implemented | ❌ NO @mcp_tool |
| RelationshipAnalyzer | `src/orchestrators/core/relationship_analyzer.py` | ✅ Implemented | ❌ NO @mcp_tool |
| DomainClassifier | `src/orchestrators/domains/domain_classifier.py` | ✅ Implemented | ❌ NO @mcp_tool |

### Gap Category 3: Governance Rules Designed, Not Enforced

| Rule | Phase | Status | Enforced? |
|------|-------|--------|-----------|
| CORE-024: @mcp_tool Required | PHASE-02 | ✅ Defined | ⚠️ Not validated |
| CORE-027: Audit Trail Required | PHASE-01 | ✅ Defined | ⚠️ Inconsistent |
| CORE-008: TDD Enforcement | PHASE-01 | ✅ Defined | ✅ Yes |

### Gap Category 4: Configuration Designed, Not Generated

| Config | Location | Status | Auto-Generated? |
|--------|----------|--------|-----------------|
| claude_desktop_config.json | Not created | ❌ Missing | NO |
| vscode-mcp-settings.json | Not created | ❌ Missing | NO |
| MCP Tool Reference Docs | Not created | ❌ Missing | NO |

---

## GAP DETECTION METHODOLOGY

### Stage 1: Design Phase Analysis

```yaml
design_phase_check:
  question_1: "Is component defined in YAML phase file?"
  action: "Query _workspaces/roadmap/phases/phase-XX.yaml"
  expected: "AC-IDs present with clear deliverables"
  
  question_2: "Are AC-IDs marked COMPLETED?"
  action: "Query _workspaces/roadmap/cortex-master.yaml phase_tracker"
  expected: "status: COMPLETED, completed_ac_ids: N/N"
  
  question_3: "Do tests pass 100%?"
  action: "Run relevant test suite"
  expected: "All tests passing, 0 failures"
```

### Stage 2: Implementation Status Check

```yaml
implementation_check:
  question_1: "Is code actually implemented (not stubbed)?"
  action: "Search for NotImplementedError, pass # TODO"
  expected: "No unimplemented methods"
  
  question_2: "Is implementation complete?"
  action: "Check for FIXME, TODO comments"
  expected: "No blocking TODOs"
  
  question_3: "Does implementation match design?"
  action: "Compare YAML AC description vs code"
  expected: "Feature parity with design"
```

### Stage 3: Exposure & Integration Check

```yaml
exposure_check:
  question_1: "Is component MCP-exposable?"
  action: "Check if tool-eligible (query interface, execute, analyze)"
  expected: "Tool-eligible components identified"
  
  question_2: "Does it have @mcp_tool decorator?"
  action: "grep -n '@mcp_tool' file.py"
  expected: "@mcp_tool decorator present"
  
  question_3: "Is it in __all__ exports?"
  action: "Check __init__.py files"
  expected: "Component exported from module"
  
  question_4: "Can downstream consumers discover it?"
  action: "Check if listed in MCPServer.get_tools()"
  expected: "Tool appears in MCP tool list"
```

### Stage 4: Governance Enforcement Check

```yaml
governance_check:
  question_1: "Does component have audit trail?"
  action: "Query audit_log for AC-IDs"
  expected: "AC_START, AC_EXECUTE, AC_COMPLETE entries"
  
  question_2: "Does component follow CORE rules?"
  action: "Check CORE-011 (types), CORE-012 (docs), etc."
  expected: "All applicable CORE rules satisfied"
  
  question_3: "Is compliance validated?"
  action: "Check if governance_enforcer validates"
  expected: "Validation logic present"
```

---

## CRITICAL GAPS TO CHECK (QUARTERLY REVIEW)

### Gap Checklist: MCP Ecosystem

- [ ] **MCP SDK Integration** - Is `mcp>=0.9.0` in requirements.txt?
- [ ] **Protocol Compliance** - Does server use stdio JSON-RPC transport?
- [ ] **Configuration Files** - Do `claude_desktop_config.json` and `vscode-mcp.json` exist?
- [ ] **Tool Coverage** - Are 40+ tools @mcp_tool decorated?
- [ ] **Tool Discovery** - Do MCP clients see all tools via `tools/list`?

### Gap Checklist: Governance Enforcement

- [ ] **Audit Logging** - Are AC_START/EXECUTE/COMPLETE logged for all ACs?
- [ ] **Rule Validation** - Is governance_enforcer called before all operations?
- [ ] **Compliance Report** - Can we generate governance compliance per phase?
- [ ] **Violation Detection** - Are CORE rule violations caught and blocked?

### Gap Checklist: Tool Exposure

- [ ] **OrchestratorScaffolder** - @mcp_tool decorated?
- [ ] **PhaseReadinessChecker** - @mcp_tool decorated?
- [ ] **BKIOOrchestrator** - @mcp_tool decorated?
- [ ] **All 40+ tools** - 100% of tool-eligible components exposed?

---

## AUTOMATED GAP DETECTION

### SQL Queries for Gap Detection

```sql
-- Query 1: Find implemented components without @mcp_tool
-- (Run against codebase search, not database)
-- SELECT files with executable functions but no @mcp_tool decorator

-- Query 2: Identify AC-IDs with no audit trail (CORE-027 violation)
SELECT ac_id, COUNT(*) as entry_count
FROM audit_log
WHERE operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
GROUP BY ac_id
HAVING entry_count < 3;

-- Query 3: Find governance rule violations
SELECT 
  phase,
  COUNT(CASE WHEN rule_status = 'FAIL' THEN 1 END) as violations
FROM governance_validation_log
GROUP BY phase
HAVING violations > 0;

-- Query 4: Tool exposure coverage
SELECT 
  'MCP-Exposed' as status,
  COUNT(*) as count
FROM orchestrator_registry
WHERE mcp_exposed = true
UNION ALL
SELECT 
  'NOT MCP-Exposed',
  COUNT(*)
FROM orchestrator_registry
WHERE mcp_exposed = false;
```

---

## REMEDIATION STRATEGY

### For Each Gap Identified

1. **Classify the Gap**
   - Type: MCP Exposure | Governance Enforcement | Config Generation | Tool Missing
   - Severity: CRITICAL | HIGH | MEDIUM | LOW
   - Root Cause: Design incomplete | Implementation missing | Integration missing | Discovery missing

2. **Create Remediation AC-ID**
   - Format: `AC-GAP-XXX-01` (e.g., `AC-GAP-001-01` for MCP SDK gap)
   - Link to original PHASE AC-ID
   - Add to cortex-master.yaml

3. **Track Remediation**
   - Add to next appropriate phase
   - Mark governance enforcement requirements
   - Set completion criteria

### Example: MCP Gap Remediation

```yaml
remediation_ac:
  ac_id: "AC-MCP-001-01"
  title: "MCP SDK Integration"
  root_cause: "Design-Build Gap: MCP infrastructure designed and built, but SDK not integrated"
  original_phase: "PHASE-02"
  related_acs: ["AC-AR-007-01", "AC-AR-007-02", "AC-AR-007-03"]
  
  acceptance_criteria:
    - "mcp>=0.9.0 added to requirements.txt"
    - "MCPServer refactored to use MCP SDK"
    - "stdio transport implemented"
    - "Claude Desktop configuration created"
    - "Protocol compliance tests added (103 tests)"
  
  governance_requirements:
    - "CORE-008: TDD (tests before implementation)"
    - "CORE-011: Type hints"
    - "CORE-024: @mcp_tool decorator where applicable"
    - "CORE-027: Audit trail logging"
```

---

## AGENT INTEGRATION POINTS

### Used by cortex-builder.md

- **Before starting new phase**: Run gap detection for current phase
- **During implementation**: Flag components that should be MCP-exposed
- **Before phase lock**: Verify all components properly exposed

### Used by cortex-review-enhanced.prompt.md

- **Pre-review validation**: Check for design-build gaps
- **Finding documentation**: Include gap root cause analysis
- **Recommendation**: Suggest gap remediation as new ACs

### Used by cortex-planner.md

- **Progress reporting**: Include gap status per phase
- **Roadmap planning**: Schedule remediation ACs
- **Risk assessment**: Flag phaseswith gaps as higher risk

---

## DETECTION AUTOMATION

### Quarterly Gap Audit

```bash
#!/bin/bash
# Run quarterly to detect new design-build gaps

echo "=== QUARTERLY DESIGN-BUILD GAP AUDIT ==="
date

# 1. Check MCP ecosystem gaps
echo "1. MCP Ecosystem Check..."
if ! grep -q "mcp>=" requirements.txt; then
  echo "  ⚠️  GAP: mcp package not in requirements.txt"
fi

# 2. Check tool exposure gaps
echo "2. Tool Exposure Check..."
TOOL_COUNT=$(grep -r "@mcp_tool" src --include="*.py" | wc -l)
echo "  MCP tools exposed: $TOOL_COUNT"
if [ $TOOL_COUNT -lt 40 ]; then
  echo "  ⚠️  GAP: Only $TOOL_COUNT of 40+ tools exposed"
fi

# 3. Check governance gaps
echo "3. Governance Check..."
VIOLATIONS=$(sqlite3 cortex_brain/state/governance.db \
  "SELECT COUNT(*) FROM audit_log WHERE ac_id IS NOT NULL AND operation NOT IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')")
if [ $VIOLATIONS -gt 0 ]; then
  echo "  ⚠️  GAP: $VIOLATIONS governance violations detected"
fi

# 4. Check config gaps
echo "4. Configuration Check..."
for config in "mcp-config/claude-desktop.json" "mcp-config/vscode-mcp.json"; do
  if [ ! -f "$config" ]; then
    echo "  ⚠️  GAP: Missing $config"
  fi
done

echo "=== END AUDIT ==="
```

---

## SUCCESS CRITERIA

A component has **NO gap** when:

- ✅ Designed in YAML phase with clear ACs
- ✅ Implemented with 100% passing tests
- ✅ MCP-exposed (if tool-eligible)
- ✅ @mcp_tool decorator present (if exposed)
- ✅ Audit trail logged (AC_START/EXECUTE/COMPLETE)
- ✅ Governance rules enforced
- ✅ Documented and discoverable
- ✅ Accessible to downstream consumers

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
