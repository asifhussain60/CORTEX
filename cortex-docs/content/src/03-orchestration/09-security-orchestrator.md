# SecurityOrchestrator

## Overview

The **SecurityOrchestrator** provides pre-DoR (Definition of Ready) security scanning to catch vulnerabilities before external tools like Arnica, Veracode, or Snyk. It integrates SAST, SCA, secrets detection, and CI/CD hardening into a unified security gate.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SecurityOrchestrator                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐       │
│  │   SAST   │ │   SCA    │ │ Secrets  │ │   CI/CD      │       │
│  │ Scanner  │ │ Scanner  │ │ Detector │ │  Hardening   │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘       │
│       │            │            │              │                │
│       └────────────┴────────────┴──────────────┘                │
│                           │                                     │
│                    ┌──────▼──────┐                             │
│                    │Security Gate│                             │
│                    │ (Pass/Fail) │                             │
│                    └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Key Capabilities

| Capability | Description | OWASP Coverage |
|------------|-------------|----------------|
| **SAST Scanning** | Static analysis for injection, XSS, path traversal | A03, A07 |
| **Secrets Detection** | Pattern + entropy-based secret detection | A07 |
| **SCA Scanning** | Dependency vulnerability scanning | A06 |
| **CI/CD Hardening** | Workflow security (action pinning, expression injection) | A08 |
| **Configuration Audit** | Debug mode, CORS, session settings | A05 |
| **Security Gate** | Pass/fail decision with remediation guidance | All |

## Usage

### Basic Security Scan

```python
from cortex.orchestrators.core.security_orchestrator import SecurityOrchestrator

orchestrator = SecurityOrchestrator()

# Full security scan
code = '''
import os
API_KEY = "sk_live_1234567890"
os.system(f"echo {user_input}")
'''

result = orchestrator.full_security_scan(code)
if result.is_ok():
    report = result.value
    print(f"Total findings: {report['total_findings']}")
    print(f"Critical: {report['severity_breakdown']['CRITICAL']}")
```

### Security Gate Evaluation

```python
# Evaluate against security gate criteria
gate_result = orchestrator.evaluate_security_gate(code)

if gate_result.is_ok():
    decision = gate_result.value
    if decision["passed"]:
        print("✅ Security gate passed")
    else:
        print(f"❌ Blocked: {decision['reason']}")
        for finding in decision["remediation_guidance"]:
            print(f"  - {finding}")
```

### Scan Types

```python
# Secrets-only scan
secrets = orchestrator.scan_for_secrets(code)

# Injection vulnerabilities
injections = orchestrator.scan_for_injection(code)

# CI/CD workflow hardening
workflow_issues = orchestrator.scan_workflow(workflow_yaml)

# Dependency scanning
dependencies = orchestrator.scan_dependencies(Path("./"))
```

## Knowledge Base Integration

The SecurityOrchestrator loads patterns from YAML knowledge bases:

| File | Purpose |
|------|---------|
| `owasp-top10.yaml` | OWASP Top 10 2021 patterns with CWE mappings |
| `secrets-patterns.yaml` | 30+ secret detection patterns (AWS, GitHub, Stripe, etc.) |
| `cicd-hardening.yaml` | CI/CD security rules and workflow templates |

### OWASP Pattern Example

```yaml
categories:
  - id: "A03:2021"
    name: "Injection"
    patterns:
      - pattern: "f\".*SELECT.*{.*}.*FROM"
        severity: "CRITICAL"
        description: "SQL Injection via f-string"
```

## MCP Tools

The SecurityOrchestrator exposes these MCP tools:

| Tool | Description |
|------|-------------|
| `cortex_security_scan` | Comprehensive security scan on code or repository |
| `cortex_validate_security` | Validate code against security gate criteria |
| `cortex_generate_sbom` | Generate Software Bill of Materials |

## CI/CD Integration

### GitHub Actions Workflow

The SecurityOrchestrator integrates with CI/CD via `.github/workflows/security-gate.yml`:

```yaml
name: Security Gate
on:
  pull_request:
    branches: [main, develop]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run CORTEX Security Gate
        run: |
          python -m cortex.cli security-scan --format sarif
```

### Pre-commit Hook

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: cortex-security
        name: CORTEX Security Check
        entry: python -m cortex.cli security-scan
        language: python
```

## Security Gate Thresholds

Default thresholds that cause the security gate to fail:

| Severity | Threshold | Action |
|----------|-----------|--------|
| CRITICAL | 0 | Block merge |
| HIGH | 3 | Block merge |
| MEDIUM | 10 | Warning |
| LOW | Unlimited | Info only |

## Audit Trail

All scans are logged for compliance:

```python
audit = orchestrator.get_audit_trail()
# Returns:
# [
#   {
#     "timestamp": "2024-02-18T10:30:00Z",
#     "action": "security_scan",
#     "scan_type": "full_scan",
#     "finding_count": 5,
#     "findings_hash": "abc123..."
#   }
# ]
```

## Interface Compliance

SecurityOrchestrator implements `IOrchestrator`:

```python
from cortex.brain.core.interfaces import IOrchestrator

class SecurityOrchestrator(IOrchestrator):
    def get_name(self) -> str
    def get_version(self) -> str
    def initialize(self) -> Result
    def get_mode(self) -> OperationMode
    def execute_operation(self, request: str) -> Result
    def get_mcp_tools(self) -> Result[Dict]
    def get_audit_trail(self, limit: int = 100) -> Result[list]
```

## Related Components

- **SecurityAuditor** (`cortex/infrastructure/security/`) - Low-level security checks
- **CrossRepoEnforcer** - Cross-repository security enforcement
- **DefenseOrchestrator** - Active defense mechanisms

## See Also

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE Database](https://cwe.mitre.org/)
- [GitHub Action Security Best Practices](https://docs.github.com/en/actions/security-guides)
