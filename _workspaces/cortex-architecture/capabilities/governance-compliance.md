# Governance & Compliance Capabilities

**Purpose:** Detailed documentation of CORTEX security, audit, and compliance features  
**Audience:** Security Teams, Compliance Officers, Architects  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Governance Framework](#governance-framework)
- [Enforcement Agents](#enforcement-agents)
- [TDD Enforcement](#tdd-enforcement)
- [Audit Trail System](#audit-trail-system)
- [Security Gates](#security-gates)
- [Compliance Reporting](#compliance-reporting)
- [Related Documents](#related-documents)

---

## Overview

CORTEX implements a comprehensive governance framework that ensures code quality, security, and compliance through automated enforcement. The governance layer operates at four levels:

1. **Pre-Execution Gate** — Blocks violations before operations begin
2. **Runtime Monitor** — Detects violations during execution
3. **Post-Execution Audit** — Captures all actions for review
4. **Production Gate** — Prevents non-compliant deployments

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

The EnforcementOrchestrator coordinates seven specialized agents:

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

## TDD Enforcement

### CORE-008: TDD Mandatory

Test-Driven Development is enforced for all IMPLEMENT, FIX, and REFACTOR operations.

### TDD Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                       TDD WORKFLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 1: RED                                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. Write failing test                                    │ │
│  │  2. Verify test fails for expected reason                 │ │
│  │  3. Commit test (checkpoint)                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Phase 2: GREEN                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. Write minimal code to pass test                       │ │
│  │  2. Run test suite                                        │ │
│  │  3. Verify all tests pass                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  Phase 3: REFACTOR                                              │
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

- [TDDOrchestrator](../orchestration/tdd-orchestrator.md) — TDD workflow
- [Security Model](../toolkit/security-model.md) — Security architecture
- [Observability](../infrastructure/observability.md) — Monitoring

---

*Part of CORTEX Architecture Documentation*
