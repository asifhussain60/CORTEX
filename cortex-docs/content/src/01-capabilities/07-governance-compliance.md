# Governance & Compliance Capabilities

---
title: CORTEX Governance & Compliance Architecture
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1800
last_verified: 2026-02-15
source_of_truth: cortex/governance/ + cortex/enforcement/ + cortex-registry/governance/
format: diátaxis-explanation
voice: third-person-blended
related_diagrams: [c4-container.md, governance-gate-flow.md]
order: 8
---

> **Notice:** Governance capabilities represent system design intentions. Actual violation detection rates, enforcement effectiveness, and audit completeness depend on rule configuration, codebase patterns, and team adherence to workflows. Organizations should validate governance policies against their specific compliance requirements and security standards.

---

## Overview: Four-Layer Defense Architecture

Organizations benefit from CORTEX's four-layer governance architecture that provides progressive defense against code quality, security, and compliance violations [Business Leaders]. Product teams rely on these governance gates to maintain consistent standards across distributed development teams and prevent technical debt accumulation [Product Owners]. The enforcement system validates 59 CORE rules through 7 specialized agents, blocking non-compliant operations with <150ms validation latency [Software Developers].

**Governance Defense Layers:**

1. **Pre-Execution Gate (Layer 1)** — EnforcementOrchestrator coordinates 7 agents performing blocking validation before any code modification. Prevents TDD violations (CORE-008), missing type hints (CORE-011), file naming issues (CORE-028), and architecture integrity breaches.

2. **Runtime Monitor (Layer 2)** — Real-time violation tracking with automatic rollback. Monitors execution for CORE rule violations with a 3-violation threshold trigger. Terminates operations immediately on critical security violations.

3. **Post-Execution Audit (Layer 3)** — Complete action logging with AC_START → AC_COMPLETE marker tracking. Detects bypass attempts, validates test results, generates compliance reports. All governance decisions stored in Git-backed registry for immutable audit trail.

4. **Production Gate (Layer 4)** — Pre-deployment validation with test coverage requirements, security scan results, and dependency vulnerability checks. Blocks deployments failing minimum quality thresholds.

**Coverage Statistics:**
- **Automated CORE Rules:** 26/59 (87% coverage across 7 agents)
- **Manual Review Rules:** 33/59 (13% requiring human judgment)
- **Validation Latency:** P50: 85ms, P95: 140ms, P99: 200ms
- **False Positive Rate:** ~5% (internal testing, varies by project)

---

## Governance Framework

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GOVERNANCE FRAMEWORK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: PRE-EXECUTION GATE                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               EnforcementOrchestrator                      │ │
│  │  (now part of UnifiedQualityAssuranceOrchestrator)         │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │ │
│  │  │Governance│ │Security │ │Compliance│ │ File   │        │ │
│  │  │  Agent  │ │  Agent  │ │  Agent  │ │ Agent  │        │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │ │
│  │  Status: BLOCKED | WARNING | PASS                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Layer 2: RUNTIME MONITOR                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Violation counter (threshold: 3)                       │ │
│  │  • Real-time rule evaluation                              │ │
│  │  • Automatic rollback on critical violations              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Layer 3: POST-EXECUTION AUDIT                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Complete action logging                                │ │
│  │  • AC marker tracking (START → COMPLETE)                  │ │
│  │  • Bypass detection                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Layer 4: PRODUCTION GATE                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Pre-deployment validation                              │ │
│  │  • Test coverage requirements                             │ │
│  │  • Security scan results                                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CORE Rules

CORTEX defines 50+ governance rules organized by category:

| Category | Rule Range | Purpose |
|----------|------------|---------|
| **CORE** | 001-049 | Core development practices |
| **ARCH** | 001-020 | Architecture standards |
| **LENS** | 001-010 | LENS intelligence rules |
| **ENH** | 001-050 | Enhancement guidelines |

### Key CORE Rules

| Rule | Name | Requirement |
|------|------|-------------|
| **CORE-002** | No Markdown Generation | No .md files in chat responses |
| **CORE-008** | TDD Mandatory | Tests BEFORE code |
| **CORE-011** | Type Hints | All functions must have type hints |
| **CORE-012** | Docstrings | Google-style docstrings required |
| **CORE-013** | No Bare Except | Specific exception handling only |
| **CORE-027** | Audit Trail | AC_START → AC_COMPLETE markers |
| **CORE-028** | File Naming | kebab-case, no SCREAMING_CASE |
| **CORE-035** | Single Implementation | No duplicate definitions |

---

## Enforcement Agents

### Agent Architecture

The UnifiedQualityAssuranceOrchestrator (quality control cortex — error detection) coordinates eight specialized enforcement agents:

```
┌─────────────────────────────────────────────────────────────────┐
│                   ENFORCEMENT ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              GovernanceEnforcementAgent                  │   │
│  │  Rules: CORE-008, 011, 012, 013, 029, 030               │   │
│  │  Focus: TDD, type hints, docstrings, headers            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              SecurityCheckpointAgent                     │   │
│  │  Rules: CORE-025, 026, 027                              │   │
│  │  Focus: Git discipline, audit trail integrity           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ComplianceValidationAgent                   │   │
│  │  Rules: Tier 1 domain rules                             │   │
│  │  Focus: Domain-specific compliance                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FileNamingEnforcementAgent                  │   │
│  │  Rules: CORE-028                                        │   │
│  │  Focus: Naming conventions, path validation             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              IncrementalExecutionAgent                   │   │
│  │  Rules: CORE-001, 004                                   │   │
│  │  Focus: <500 LOC increments, continuation limits        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MarkdownSuppressionAgent                    │   │
│  │  Rules: CORE-002                                        │   │
│  │  Focus: Block report/summary file generation            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ArchitectureIntegrityAgent                  │   │
│  │  Rules: CORE-017-020, 032, 034, 035, 038-041           │   │
│  │  Focus: Architecture patterns, performance              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              EnvironmentIntegrityAgent                   │   │
│  │  Rules: MCP-FIRST, CORE-050                             │   │
│  │  Focus: MCP availability, environment validation        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Response Types

| Response | Meaning | Action |
|----------|---------|--------|
| **BLOCKED** | Critical violation | Stop operation |
| **WARNING** | Non-critical issue | Log and continue |
| **PASS** | No violations | Proceed normally |

### Coverage Statistics

- **Total CORE Rules:** 49
- **Automated Rules:** 43 (87.8%)
- **Validation Time:** < 150ms
- **False Positive Rate:** < 2%

---

### Detailed Enforcement Agent Matrix

The 8-agent enforcement system provides comprehensive pre-execution validation with specific trigger conditions and blocking criteria.

| # | Agent | CORE Rules Enforced | Trigger Conditions | Block Conditions | Performance |
|---|-------|-------------------|-------------------|------------------|-------------|
| **1** | **GovernanceEnforcementAgent** | CORE-008, 011, 012, 013, 029, 030 | Every IMPLEMENT, FIX, REFACTOR intent | ❌ Missing tests<br>❌ No type hints<br>❌ Missing docstrings<br>❌ Bare except clauses<br>❌ Missing response header | <50ms |
| **2** | **SecurityCheckpointAgent** | CORE-025, 026, 027 | Pre-commit, PR creation, deployment | ❌ Uncommitted sensitive files<br>❌ Missing AC markers<br>❌ Audit trail gaps<br>❌ Non-atomic commits | <30ms |
| **3** | **ComplianceValidationAgent** | Tier 1 domain rules (industry-specific) | Domain operations (finance, healthcare, etc.) | ❌ GDPR violations<br>❌ HIPAA non-compliance<br>❌ SOC 2 gaps<br>❌ PCI DSS failures | <100ms |
| **4** | **FileNamingEnforcementAgent** | CORE-028 | File creation, file rename | ❌ SCREAMING_CASE detected<br>❌ Plan files >40 chars<br>❌ Non-kebab-case production files | <10ms |
| **5** | **IncrementalExecutionAgent** | CORE-001, 004 | Code generation >200 LOC | ❌ Single commit >500 LOC<br>❌ Silent errors<br>❌ Exceeded continuation limit | <20ms |
| **6** | **MarkdownSuppressionAgent** | CORE-002 | File creation with `.md` extension | ❌ `.md` file outside `.github/prompts/`<br>❌ `.md` file outside `.github/agents/`<br>❌ Any `README.md` except root | <5ms |
| **7** | **ArchitectureIntegrityAgent** | CORE-017-020, 032, 034, 035, 038-041 | Design review, architecture changes | ❌ Versioned filenames<br>❌ Performance violations<br>❌ Duplicate implementations (CORE-035)<br>❌ Turn budget exceeded | <80ms |
| **8** | **EnvironmentIntegrityAgent** | MCP-FIRST, CORE-050, CORE-051 + Phase 89 Auto-Healing | IMPLEMENT/FIX/REFACTOR intents | ❌ MCP tools unavailable (after auto-healing attempts)<br>❌ Python version <3.9<br>❌ Virtual env not activated<br>❌ settings.json tracked in git | <40ms (detection)<br>+2-5s (auto-healing) |

**Total Validation Time:** <335ms (worst case with all 8 agents triggered)

---

### Enforcement Flow Diagram

```
User Request → IntentRouter
      ↓
[1] Classify Intent (IMPLEMENT | FIX | REFACTOR | ANALYZE)
      ↓
[2] Load EnforcementOrchestrator (UnifiedQualityAssuranceOrchestrator)
      ↓
[3] Parallel Agent Execution (8 agents, <335ms total)
      ↓
      ├─→ Agent 1: GovernanceEnforcementAgent → PASS/WARNING/BLOCKED
      ├─→ Agent 2: SecurityCheckpointAgent → PASS/WARNING/BLOCKED
      ├─→ Agent 3: ComplianceValidationAgent → PASS/WARNING/BLOCKED
      ├─→ Agent 4: FileNamingEnforcementAgent → PASS/WARNING/BLOCKED
      ├─→ Agent 5: IncrementalExecutionAgent → PASS/WARNING/BLOCKED
      ├─→ Agent 6: MarkdownSuppressionAgent → PASS/WARNING/BLOCKED
      ├─→ Agent 7: ArchitectureIntegrityAgent → PASS/WARNING/BLOCKED
      └─→ Agent 8: EnvironmentIntegrityAgent → PASS/WARNING/BLOCKED
      ↓
[4] Aggregate Results
      ↓
      ├─→ ANY BLOCKED → HALT execution, display violations
      ├─→ WARNINGS only → LOG warnings, display to user, continue
      └─→ ALL PASS → Proceed to orchestrator
      ↓
[5] Execute Request (TDDOrchestrator, RefactoringOrchestrator, etc.)
      ↓
[6] Post-Execution Audit (verify compliance maintained)
      ↓
[7] AC_COMPLETE marker (audit trail closure)
```

---

### Agent-Specific Behavior

#### GovernanceEnforcementAgent (Agent 1)
**Purpose:** Enforce core development practices  
**Activation:** Every code-modifying operation  
**Blocking Threshold:** Any violation = BLOCKED

**Validation Checklist:**
- ✅ Tests exist before code (CORE-008)
- ✅ All function parameters have type hints (CORE-011)
- ✅ All function returns have type hints (CORE-011)
- ✅ Google-style docstrings present (CORE-012)
- ✅ No bare `except:` clauses (CORE-013)
- ✅ Response header present (CORE-029)

**Example Block Message:**
```
❌ BLOCKED: GovernanceEnforcementAgent

Violations:
  • CORE-008: No tests found for new code in src/auth/login.py
  • CORE-011: Missing type hints in function authenticate_user()
  • CORE-012: Missing docstring in class UserSession

Resolution:
  1. Write failing tests first (TDD)
  2. Add type hints: def authenticate_user(username: str, password: str) -> bool:
  3. Add Google-style docstring with Args, Returns, Raises sections

Retry after fixing violations.
```

#### SecurityCheckpointAgent (Agent 2)
**Purpose:** Git discipline and audit trail integrity  
**Activation:** Pre-commit, PR creation, deployment gates  
**Blocking Threshold:** Critical violations only

**Validation Checklist:**
- ✅ No uncommitted files with sensitive data (CORE-025)
- ✅ Atomic commits (CORE-026)
- ✅ AC_START marker present (CORE-027)
- ✅ AC_COMPLETE marker present after completion (CORE-027)
- ✅ Commit message follows format

**Example Block Message:**
```
❌ BLOCKED: SecurityCheckpointAgent

Violations:
  • CORE-027: Missing AC_START marker in modified file src/auth/token.py
  • CORE-025: Uncommitted file .env contains potential secrets

Resolution:
  1. Add AC marker: # AC_START: AC-FEATURE-AUTH-001
  2. Remove .env from git: git rm --cached .env
  3. Add .env to .gitignore
  4. Retry operation

Audit trail integrity is mandatory for all governance-gated work.
```

#### EnvironmentIntegrityAgent (Agent 8) — Enhanced with Auto-Healing (Phase 89)
**Purpose:** MCP-FIRST enforcement and environment validation with intelligent auto-recovery  
**Activation:** IMPLEMENT/FIX/REFACTOR intents (BLOCKING), ANALYZE intent (non-blocking)  
**Blocking Threshold:** MCP unavailable for code-modifying operations (after auto-healing attempts)

Organizations benefit from the EnvironmentIntegrityAgent's enhanced capabilities that validate development environment prerequisites before code-modifying operations [Business Leaders]. The agent performs comprehensive validation of MCP server availability, Python environment configuration, and virtual environment setup, with new auto-healing features that attempt automated recovery before blocking operations [Product Owners]. The multi-method detection cascade uses environment variables, settings.json validation, and network health checks to ensure MCP tools are accessible, while Phase 89 enhancements add OS-aware diagnosis and automatic remediation for common configuration issues [Software Developers].

**3-Method MCP Detection Cascade:**
1. **Environment Variables:** Check `MCP_SERVER_URL`, `CORTEX_MCP_ENABLED`
2. **Settings.json:** Validate `.vscode/settings.json` exists with Python path
3. **Network Port:** Health check on localhost:9000 (fallback)

**Validation Checklist:**
- ✅ MCP tools available in registry (cortex_* tools detected)
- ✅ Python ≥ 3.9.0
- ✅ Virtual environment activated
- ✅ `.vscode/settings.json` NOT tracked in git (CORE-051)
- ✅ Setup log shows "✅ SETUP COMPLETE"

**Phase 89 Enhancement: Auto-Healing Capabilities**

When MCP unavailability is detected, the agent now attempts OS-aware diagnosis and automatic remediation before blocking operations. Organizations may experience reduced workflow interruptions through intelligent auto-recovery mechanisms that resolve common environment issues without manual intervention [Business Leaders].

**Auto-Healing Decision Flow:**

```
EnvironmentIntegrityAgent.validate_pre_flight(IMPLEMENT)
    ↓
MCP Available? 
    ↓
    NO → Initiate Auto-Healing (Phase 89)
         ↓
         [1] OS-Aware Diagnosis
         │   ├─ Windows: Check %APPDATA%\Code\User\settings.json
         │   ├─ macOS: Check ~/Library/Application Support/Code/User/
         │   └─ Linux: Check ~/.config/Code/User/settings.json
         ↓
         [2] Common Issue Detection
         │   ├─ Missing dependencies in requirements.txt?
         │   ├─ Virtual environment not activated?
         │   ├─ Invalid Python path in settings?
         │   └─ Corrupted MCP server configuration?
         ↓
         [3] Auto-Fix Attempts
         │   ├─ Install missing dependencies (pip install -r requirements.txt)
         │   ├─ Activate virtual environment (.venv/Scripts/activate)
         │   ├─ Run setup script (python .cortex/setup-mcp.py)
         │   └─ Repair settings.json configuration
         ↓
         [4] Validation Retry
         │   └─ MCP Available Now?
                 ├─ YES → ✅ PASS (auto-healed, operation proceeds)
                 └─ NO → ❌ BLOCK (manual intervention required)
    ↓
    YES → ✅ PASS (operation proceeds)
```

**Auto-Healing Performance (Internal Testing):**

Organizations using auto-healing capabilities may experience successful issue resolution in 60-75% of MCP unavailability scenarios based on internal testing during Phase 89 development [Business Leaders]. Common issues like missing dependencies or inactive virtual environments can potentially be detected and resolved within 2-5 seconds [Product Owners]. The system maintains detailed healing logs for post-incident analysis and continuous improvement [Software Developers].

| Issue Type | Auto-Fix Success Rate (Internal) | Typical Resolution Time | Fallback Action |
|------------|----------------------------------|-------------------------|-----------------|
| **Missing Dependencies** | ~85% | 2-4 seconds | Block with pip install guidance |
| **Inactive Virtual Env** | ~90% | 1-2 seconds | Block with activation instructions |
| **Invalid Python Path** | ~70% | 3-5 seconds | Block with path correction guidance |
| **Corrupted Config** | ~65% | 3-6 seconds | Block with manual repair steps |
| **Network Issues** | ~20% | 5-10 seconds | Block with connectivity troubleshooting |

> **Notice:** Auto-healing capabilities represent best-effort automated recovery mechanisms. Success rates shown reflect internal testing environments and may vary significantly based on system configuration, permissions, operating system version, and specific error conditions. Organizations should not rely exclusively on auto-healing for production environments and should implement proper environment validation as part of deployment pipelines. The system maintains audit logs of all auto-healing attempts for compliance and troubleshooting purposes.

**Phase 50 Enhancement: MCP Policy Enforcement**

The EnvironmentIntegrityAgent includes MCP policy enforcement to prevent conflicts with competing MCP servers. Organizations benefit from automatic detection of Pylance, GitKraken, and other MCP implementations that may interfere with CORTEX operations [Business Leaders]. When competing servers are detected, the agent can automatically trigger setup scripts to establish CORTEX-only MCP policies [Product Owners].

**Example Block Message (MCP Unavailable with Auto-Healing Attempted):**
```
❌ BLOCKED: EnvironmentIntegrityAgent (Auto-Healing Attempted)

Intent: IMPLEMENT
Status: MCP tools not available after auto-recovery attempts

Auto-Healing Actions Attempted:
  ✅ Detected OS: Windows 10
  ✅ Diagnosed Issue: Virtual environment not activated
  ⚠️  Attempted Fix: Activate .venv\Scripts\Activate.ps1
  ❌ Fix Result: Permission denied (ExecutionPolicy=Restricted)

MCP Detection Results:
  • Method 1 (env vars): FAIL - MCP_SERVER_URL not set
  • Method 2 (settings.json): FAIL - File not found
  • Method 3 (network): FAIL - localhost:9000 not responding

Manual Resolution Required:
  1. Update PowerShell execution policy: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  2. Activate virtual environment: .\.venv\Scripts\Activate.ps1
  3. Run MCP setup: python .cortex/setup-mcp.py
  4. Reload VS Code (Command Palette → Developer: Reload Window)
  5. Retry your request

Auto-Healing Log: .cortex/logs/auto-healing-2026-02-17T14-32-18.log

CORTEX operates at ONE quality level: Production.
Fix infrastructure. No bypasses allowed.
```

**Example Success Message (Auto-Healed):**
```
✅ PASS: EnvironmentIntegrityAgent (Auto-Healed)

Intent: IMPLEMENT
Status: MCP tools available (issue auto-resolved)

Auto-Healing Actions Performed:
  ✅ Detected OS: macOS Sonoma 14.3
  ✅ Diagnosed Issue: Missing package 'requests' in requirements.txt
  ✅ Attempted Fix: pip install requests
  ✅ Fix Result: Package installed successfully
  ✅ Validation Retry: MCP tools now available

Operation proceeding with validated environment.
Auto-Healing Log: .cortex/logs/auto-healing-2026-02-17T14-28-45.log
```

**Example Warning (ANALYZE Intent):**
```
⚠️ WARNING: EnvironmentIntegrityAgent

Intent: ANALYZE (read-only operation allowed without MCP)
Status: MCP tools not detected, but operation can proceed

Note: For IMPLEMENT/FIX/REFACTOR operations, MCP setup is required.
To enable full CORTEX capabilities: python .cortex/setup-mcp.py
```

---

###TDD Enforcement

### CORE-008: TDD Mandatory

Test-Driven Development is enforced for all IMPLEMENT, FIX, and REFACTOR operations.

### TDD Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                       TDD WORKFLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Current: RED                                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. Write failing test                                    │ │
│  │  2. Verify test fails for expected reason                 │ │
│  │  3. Commit test (checkpoint)                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Current: GREEN                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. Write minimal code to pass test                       │ │
│  │  2. Run test suite                                        │ │
│  │  3. Verify all tests pass                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Current: REFACTOR                                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. Improve code quality                                  │ │
│  │  2. Maintain test coverage                                │ │
│  │  3. Verify tests still pass                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### TDD Enforcement Points

| Checkpoint | Validation | Failure Action |
|------------|------------|----------------|
| **Pre-Implementation** | Test file exists | Block operation |
| **Post-Test-Write** | Test fails correctly | Block proceed |
| **Post-Implementation** | Tests pass | Block merge |
| **Post-Refactor** | Tests still pass | Rollback changes |

### Forbidden Bypasses

CORTEX explicitly blocks TDD bypass attempts:

- ❌ `--ignore` flags to skip tests
- ❌ Renaming test files to `_skip_*`
- ❌ Deleting test files
- ❌ Mocking test failures

---

## Audit Trail System

### CORE-027: Audit Trail

Every operation generates comprehensive audit records with AC (Audit Checkpoint) markers.

### AC Marker Format

```python
# AC_START: AC-{PHASE}-{SEQUENCE}
# Description: {operation_description}

# ... operation code ...

# AC_COMPLETE: AC-{PHASE}-{SEQUENCE} ✅ {result_summary}
```

### Example Audit Trail

```python
# AC_START: AC-PHASE48-001
# Description: Implement user authentication module

def authenticate_user(username: str, password: str) -> AuthResult:
    """
    Authenticate user with credentials.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        AuthResult with success status and token
    """
    # Implementation...
    pass

# AC_COMPLETE: AC-PHASE48-001 ✅ 15/15 tests passing
```

### Audit Log Structure

```python
@dataclass
class AuditRecord:
    """Comprehensive audit record."""
    
    # Identification
    ac_id: str                    # AC-PHASE48-001
    timestamp: datetime           # When action occurred
    session_id: str              # Session identifier
    
    # Operation
    operation: str               # implement, fix, refactor
    target: str                  # Target file/module
    description: str             # What was done
    
    # Context
    user_request: str            # Original user request
    orchestrator: str            # Handling orchestrator
    lens_context: Dict           # LENS analysis snapshot
    
    # Outcome
    status: str                  # started, completed, failed
    result: Dict                 # Operation result
    artifacts: List[str]         # Created/modified files
    
    # Governance
    rules_applied: List[str]     # CORE rules checked
    violations: List[str]        # Any violations detected
    warnings: List[str]          # Warnings generated
```

### Audit Retention

| Data Type | Retention | Storage |
|-----------|-----------|---------|
| **Audit Logs** | 90 days | Database |
| **AC Markers** | Permanent | Source code |
| **Metrics** | 30 days | Prometheus |
| **Artifacts** | 7 days | File system |

---

## Security Gates

### ARCH-012: OWASP Compliance

CORTEX enforces OWASP Top 10 compliance:

| OWASP Category | CORTEX Control |
|----------------|----------------|
| **A01: Broken Access Control** | Authentication validation |
| **A02: Cryptographic Failures** | Secret detection |
| **A03: Injection** | Input validation |
| **A04: Insecure Design** | Architecture review |
| **A05: Security Misconfiguration** | Config validation |
| **A06: Vulnerable Components** | Dependency scanning |
| **A07: Authentication Failures** | Auth pattern enforcement |
| **A08: Software Integrity** | Checksum validation |
| **A09: Logging Failures** | Audit trail enforcement |
| **A10: Server-Side Request Forgery** | URL validation |

### Security Validation Flow

```
Code Change
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SECURITY GATES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Gate 1: INPUT VALIDATION                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Parameter type checking                                │ │
│  │  • SQL injection patterns                                 │ │
│  │  • XSS patterns                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Gate 2: SECRET DETECTION                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • API keys                                               │ │
│  │  • Passwords                                              │ │
│  │  • Private keys                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Gate 3: DEPENDENCY SCAN                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Known vulnerabilities (CVE)                            │ │
│  │  • Outdated packages                                      │ │
│  │  • License compliance                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Gate 4: CODE PATTERNS                                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Insecure functions                                     │ │
│  │  • Hardcoded credentials                                  │ │
│  │  • Unsafe deserialization                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
PASS / BLOCKED
```

---

## Compliance Reporting

### Report Types

| Report | Frequency | Audience |
|--------|-----------|----------|
| **Governance Summary** | Daily | Team leads |
| **Security Posture** | Weekly | Security team |
| **Compliance Audit** | Monthly | Compliance officers |
| **Executive Dashboard** | Quarterly | Leadership |

### Metrics Tracked

| Category | Metrics |
|----------|---------|
| **Quality** | Test coverage, code complexity, duplication |
| **Security** | Vulnerabilities, secret exposures, scan results |
| **Compliance** | Rule violations, bypass attempts, audit gaps |
| **Performance** | Enforcement latency, false positives |

### Compliance Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                   COMPLIANCE DASHBOARD                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Governance Health: ████████████████████ 98%                    │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   TDD       │  │  Security   │  │   Audit     │             │
│  │   100%      │  │    95%      │  │    100%     │             │
│  │  Compliant  │  │  Compliant  │  │  Compliant  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  Recent Violations:                                              │
│  • 2 CORE-011 warnings (missing type hints)                     │
│  • 1 CORE-028 warning (file naming)                             │
│                                                                  │
│  Last Audit: 2026-02-10 14:30:00                                │
│  Next Scheduled: 2026-02-10 15:30:00                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [TDDOrchestrator](../03-orchestration/tdd-orchestrator.md) — TDD workflow
- [Security Model](../06-toolkit/security-model.md) — Security architecture
- [Observability](../05-infrastructure/observability.md) — Monitoring

---

*Part of CORTEX Architecture Documentation*
