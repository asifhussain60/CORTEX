# 🔍 CORTEX Search - Holistic Gap Detection & Discrepancy Discovery

**Version:** 1.2.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Analysis  
**Author:** Asif Hussain | **AC Reference:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**ACTIVE DISCREPANCY HUNTER** - Systematically searches the codebase for:
1. **Discrepancies** between implementation and Acceptance Criteria (AC)
2. **Conflicts** in routing, governance, or orchestrator behavior
3. **Violations** of SKULL rules, architecture patterns, or coding standards
4. **Brittleness sources** (hardcoded paths, missing error handling, race conditions)
5. **Audit log gaps** that would fail AC validation
6. **Improvement opportunities** for performance, security, or maintainability

**OUTPUT:** JSON/YAML findings file consumed by `cortex-align.prompt.md`

---

## 🔀 Intent Routing

**Patterns:**
- `^(search|find gaps|find violations|find brittleness|find issues).*$`
- `^(discrepancy check|scan for issues|detect problems).*$`

**Priority:** 8 (High - Discovery phase)  
**Mode:** Autonomous  
**Confidence:** 1.0

---

## 📋 Analysis Categories

### Category 1: AC Implementation Gaps
**Source of Truth:** `00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`

| AC Section | Risk Level | Criteria Count |
|------------|------------|----------------|
| `governance_compliance` (AC-GOV-*) | 🔴 CRITICAL | 10 |
| `architecture_cleanliness` (AC-ARCH-*) | 🔴 CRITICAL | 5 |
| `foundation_layer` (AC-F01-*) | 🔴 CRITICAL | 6 |
| `todo_orchestrator` (AC-F02-*) | 🔴 CRITICAL | 7 |
| `orchestrator_capabilities` (AC-ORC-*) | 🟠 HIGH | 10+ |
| `concurrency_safety` (AC-RACE-*) | 🔴 CRITICAL | 3 |
| `security_compliance` (AC-SEC-*) | 🔴 CRITICAL | 8 |
| `multi_repo_registry` (AC-REPO-*) | 🔴 CRITICAL | 3 |

### Category 2: SKULL Rule Violations

| Rule | Detection Pattern | Severity |
|------|-------------------|----------|
| TDD_ENFORCEMENT | Code without failing test first | 🔴 BLOCKED |
| HOLISTIC_DISCOVERY | File creation without workspace search | 🔴 BLOCKED |
| GIT_ISOLATION | CORTEX commits to user repos | 🔴 BLOCKED |
| PLANNING_ISOLATION | Plans implement code | 🔴 BLOCKED |
| YAML_SAFE_LOADER | `yaml.load()` without SafeLoader | 🔴 CRITICAL |

### Category 3: Architecture Anti-Patterns

| Anti-Pattern | Detection Regex | Risk |
|--------------|-----------------|------|
| Hardcoded paths | `hardcoded.*=.*["\']\/` | 🔴 HIGH |
| Direct file writes | `open\([^,]+,\s*["\']w` | 🟠 MEDIUM |
| Bare except | `except\s*:` | 🟠 HIGH |
| Type ignore | `# type:\s*ignore` | 🟡 MEDIUM |

### Category 4: Security Vulnerabilities

| Vulnerability | Detection Pattern | Risk |
|---------------|-------------------|------|
| Code injection | `eval\(|exec\(` | 🔴 CRITICAL |
| Shell injection | `subprocess.*shell=True` | 🔴 CRITICAL |
| Hardcoded secrets | `password\s*=\s*["\']` | 🔴 CRITICAL |
| YAML injection | `yaml\.load\(` | 🔴 CRITICAL |

---

## 🔬 Discovery Pipeline (5 Phases)

### Phase 0: AC Document Loading
**Duration:** <10 seconds

**Actions:**
1. Load `00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`
2. Parse all 340+ acceptance criteria
3. Build validation checklist by category
4. Identify blocking vs non-blocking criteria

---

### Phase 1: Implementation Inventory
**Duration:** 2-3 minutes

**Scan Targets:**
```
src/orchestrators/       → Orchestrator implementations
src/cortex_agents/       → Agent implementations
src/database/            → StateManager, DAG
src/infrastructure/      → AuditLogger, utilities
tests/                   → Test coverage
cortex-brain/manifests/  → Orchestrator configs
cortex-brain/tier0/      → Governance rules
```

**Output:** Implementation matrix mapping AC → code

---

### Phase 2: Discrepancy Detection
**Duration:** 2-3 minutes

**Discrepancy Types:**
- **MISSING** - AC criterion exists, no code found
- **PARTIAL** - Code exists but incomplete
- **STALE** - Code outdated vs spec
- **CONFLICT** - Code differs from AC
- **OVER** - Code exceeds AC scope

---

### Phase 3: Violation & Brittleness Scan
**Duration:** 2-3 minutes

**Scans for:**
- SKULL rule violations
- Architecture anti-patterns
- Security vulnerabilities
- Missing error handling
- Race condition risks
- Global state mutations

---

### Phase 4: Audit Gap Analysis
**Duration:** 1-2 minutes

**Per AC-INT-006:** Verify every criterion has audit log coverage

---

## 📊 Output Format

**Primary Output:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/search-findings-{timestamp}.yaml`

```yaml
search_findings:
  generated_at: '2026-01-09T10:30:00Z'
  ac_version: '7.5.0'
  ac_location: 'cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml'
  
  summary:
    total_issues: 68
    critical: 18
    high: 29
    medium: 17
    low: 4
    
  discrepancies:
    - id: AC-GOV-001
      type: PARTIAL
      description: "SKULL rule migration incomplete"
      evidence_found: ["cortex-brain/tier0/governance/"]
      evidence_missing: ["tests/governance/test_skull_migration.py"]
      severity: CRITICAL
      blocking: true
      
  violations:
    - rule: YAML_SAFE_LOADER
      file: "src/utils/config_loader.py"
      line: 45
      pattern: "yaml.load(f)"
      fix: "yaml.safe_load(f)"
      severity: CRITICAL
      
  brittleness:
    - type: RACE_CONDITION
      file: "src/database/state_manager.py"
      description: "Concurrent writes without locking"
      severity: CRITICAL
      
  audit_gaps:
    - criterion: AC-F02-006
      gap_type: NO_AUDIT_COVERAGE
      recommendation: "Add audit logging for TODO state integration"
```

---

## 📁 File Locations (Canonical)

| Artifact | Location |
|----------|----------|
| **AC Source of Truth** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml` |
| **Search Findings** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/search-findings-{timestamp}.yaml` |
| **Remediation Plan** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/remediation-plan.yaml` |
| **Snowball Strategy** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/snowball-strategy.yaml` |
| **Archive** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/archive/` |

---

## ⚡ Execution Protocol

**Invocation:**
```
/CORTEX search
/CORTEX search --scope governance
/CORTEX search --scope security
```

**Full scan:**
```
/CORTEX search --full
```

**Output consumed by:** `cortex-align.prompt.md`

---

## � MCP Tool Validation (Pre-Requisite Check)

**⚠️ CRITICAL: Before completing Phase 4, validate MCP tool exists:**

| Check | File | Status |
|-------|------|--------|
| **MCP Tool Implementation** | `src/mcp/align_plan_sync.py` | Required |
| **Capability Registration** | `src/mcp/capability_registry.py` → `cortex_align_plan_sync` | Required |
| **MCP Export** | `src/mcp/__init__.py` → `AlignPlanSyncTool` | Required |

**Validation Command:**
```bash
python3 -c "from src.mcp.align_plan_sync import AlignPlanSyncTool; print('✅ MCP tool ready')"
```

**If validation fails:** Add to findings as CRITICAL blocking issue:
```yaml
mcp_gaps:
  - tool: cortex_align_plan_sync
    gap_type: MISSING_IMPLEMENTATION
    required_file: src/mcp/align_plan_sync.py
    severity: CRITICAL
    blocking: true
    reason: "Phase 7 of cortex-align requires this MCP tool for holistic plan synchronization"
```

---

## �🛡️ Brain Protection Compliance

| SKULL Rule | Compliance |
|------------|------------|
| **HOLISTIC_DISCOVERY** | ✅ Searches entire workspace |
| **PLANNING_ISOLATION** | ✅ Generates findings, no code changes |
| **GIT_ISOLATION** | ✅ Does not modify any files |
| **MCP_VALIDATION** | ✅ Validates MCP tools exist before align phase |

---

**Next Step:** Run `/CORTEX align` to generate prioritized fix plan with visual progress tracking.

