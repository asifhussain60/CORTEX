---
title: Security-First Development — Shift-Left Security Architecture
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/validation/security_vulnerability_orchestrator.py + cortex/orchestrators/git/sanitization_orchestrator.py + cortex-registry/workflows/templates/security/
order: 20
---

# Security-First Development — Shift-Left Security Architecture

> **In CORTEX, security is not a phase — it is infrastructure.** Every request passes through security gates before, during, and after execution. Credentials are scanned before commits. Vulnerabilities are detected during analysis. Threat models are generated as part of design.

---

## The Security Architecture

CORTEX implements security at five layers:

```
Layer 1: Pre-Commit Gate        ← SanitizationOrchestrator — secrets, PII, branch hygiene
Layer 2: Governance Rules       ← CORE-013 (error handling), CORE-058 (SQLite WAL)
Layer 3: LENS Analysis          ← Security analyzer — vulnerability patterns, credential detection
Layer 4: Execution Validation   ← SecurityVulnerabilityOrchestrator — SAST, CVE scanning
Layer 5: Release Gate           ← Security assessment workflow template
```

### Key Security Orchestrators

| Orchestrator | Location | Purpose |
|-------------|----------|---------|
| **SecurityVulnerabilityOrchestrator** | `cortex/orchestrators/validation/security_vulnerability_orchestrator.py` | SAST scanning, CVE detection, remediation handler |
| **SanitizationOrchestrator** | `cortex/orchestrators/git/sanitization_orchestrator.py` | Secret scanning, PII removal, branch hygiene |
| **PreCommitEnforcementOrchestrator** | `cortex/orchestrators/git/git_enforcement_orchestrator.py` | Pre-commit CORE rule validation |
| **SecurityCheckpointAgent** | `cortex/enforcement/` | Enforcement agent for security rules |

---

## Security Throughout the SDLC

| SDLC Phase | Security Gate | Automated By |
|-----------|--------------|-------------|
| **Requirements** | Threat surface identification | `sdlc/security-by-design.yaml` knowledge injection |
| **Design** | Security-by-design pattern validation | SecurityVulnerabilityOrchestrator |
| **Implementation** | Credential scan, SAST analysis | LENS Security Analyzer + SanitizationOrchestrator |
| **Code Review** | Dependency CVE scanning, PII detection | PreCommitEnforcementOrchestrator |
| **Integration** | Security integration tests | SecurityVulnerabilityOrchestrator |
| **Security Audit** | Full OWASP Top 10, threat model | `security/threat-model-analysis.yaml` template |
| **Release** | Release security checklist | `sdlc/release-readiness.yaml` with security gate |

---

## Security Workflow Templates

Three dedicated security templates in `cortex-registry/workflows/templates/security/`:

| Template | Purpose | Trigger |
|----------|---------|---------|
| `security-compliance-audit.yaml` | Full compliance audit against security standards | `/audit`, security review |
| `security-hardening.yaml` | Systematic hardening of identified vulnerabilities | Post-audit remediation |
| `threat-model-analysis.yaml` | Structured threat modeling using STRIDE methodology | Design phase, `/security` |

---

## Knowledge-Driven Security

Security knowledge is maintained at multiple levels:

| Knowledge Source | Location | Content |
|-----------------|----------|---------|
| OWASP Top 10 | `cortex-registry/knowledge-base/security/owasp-top10.yaml` | Top 10 web application vulnerabilities |
| Secrets Patterns | `cortex-registry/knowledge-base/security/secrets-patterns.yaml` | Regex patterns for credential detection |
| CI/CD Hardening | `cortex-registry/knowledge-base/security/cicd-hardening.yaml` | Pipeline security best practices |
| Secure Coding | `cortex-registry/knowledge/security/secure-coding-practices.yaml` | Language-specific secure coding rules |
| Security-by-Design | `cortex-registry/knowledge/sdlc/security-by-design.yaml` | Design-phase security principles |

---

## Resilience Infrastructure

Beyond application security, CORTEX implements infrastructure resilience patterns:

| Pattern | Module | Purpose |
|---------|--------|---------|
| **Circuit Breaker** | `cortex/infrastructure/circuit_breaker.py` | Stops calls to failing services (Closed → Open → Half-Open) |
| **Bulkhead** | `cortex/infrastructure/bulkhead_manager.py` | Partitions resources to prevent cascade failures |
| **Graceful Degradation** | `cortex/infrastructure/graceful_degradation.py` | Returns partial results when non-critical services fail |
| **Retry Handler** | `cortex/infrastructure/` | Exponential backoff with jitter for transient failures |
| **Audit Hash Chain** | `cortex/infrastructure/audit_hash_chain.py` | Tamper-evident cryptographic chain for audit entries |
| **Evidence Bundle** | `cortex/infrastructure/evidence_bundle.py` | Compliance proof packaging |

---

## Security Governance Rules

| Rule | Name | Enforcement |
|------|------|------------|
| CORE-013 | Error Handling | Proper exception handling required — no bare `except:` |
| CORE-058 | SQLite WAL Mode | All SQLite databases must use Write-Ahead Logging (prevents corruption) |
| CORE-062 | Plan-First | Plan before execution for complex operations (reduces risk of partial changes) |

---

## For Business Leaders

Security is not a cost centre in CORTEX — it is a quality accelerator. Every commit is scanned for credentials before it reaches Git. Every design is validated against security patterns before implementation begins. Every release passes through a security gate before deployment.

The result: security issues are caught when they are cheapest to fix — during development, not after production incidents.
