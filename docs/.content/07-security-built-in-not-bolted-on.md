# Security — Built In, Not Bolted On

---
title: Security-First Development — How CORTEX Embeds Security Into Every Stage
type: explanation
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-07
order: 7
---

> **The central idea:** Security vulnerabilities found during development cost minutes to fix. The same vulnerability found in production costs days, damages reputation, and in regulated industries, carries regulatory consequences. CORTEX treats security as infrastructure — enforced automatically at every stage of development — not as a phase that happens before release.

---

## Five Security Layers

CORTEX implements security at five distinct layers, so that a vulnerability missed by one layer is caught by the next. This defence-in-depth approach means no single point of failure can allow a security issue to reach production.

**Layer 1 — Before Commit** — A dedicated sanitisation engine scans every proposed commit for secrets (API keys, credentials, private keys, tokens), personally identifiable information, and branch hygiene issues. A commit containing any detected secret is blocked before it reaches version control. No sensitive data ever enters the git history.

**Layer 2 — Governance Rules** — Mandatory governance rules enforce security practices at the code level. Error handling must be explicit — no bare exception catches that silently swallow failures. All databases must use write-ahead logging to prevent corruption. Plan-first requirements apply to complex operations, reducing the risk of partially-applied changes.

**Layer 3 — Code Intelligence** — The security analyzer runs as one of nine parallel analysis tools whenever CORTEX examines code. It detects SQL injection patterns, cross-site scripting vulnerabilities, credential exposure in code, hardcoded secrets, and known vulnerability patterns. Findings are prioritised by severity — critical, high, medium, low — and each finding includes the specific line, the nature of the vulnerability, and a remediation suggestion.

**Layer 4 — Static Analysis and CVE Scanning** — Before implementation begins on security-sensitive changes, a dedicated security orchestrator performs static application security testing and checks dependencies against known vulnerability databases. New vulnerabilities in dependencies are flagged as they are published, not just when the next audit runs.

**Layer 5 — Release Gate** — Before any production release, a security assessment workflow runs automatically, including a full OWASP Top 10 check and a threat model review for the specific change being released.

---

## Security Knowledge — The Rules CORTEX Enforces

Security in CORTEX is not a collection of warnings — it is structured knowledge applied consistently. The security knowledge base covers:

**OWASP Top 10** — The ten most critical web application security risks, including injection attacks, broken authentication, sensitive data exposure, XML external entities, broken access control, security misconfiguration, cross-site scripting, insecure deserialisation, vulnerable components, and insufficient logging.

**Credential Detection Patterns** — Hundreds of patterns for detecting API keys, tokens, passwords, and private keys across all supported programming languages and configuration formats.

**Pipeline Security** — Security hardening standards for continuous integration and continuous deployment pipelines — preventing pipeline injection attacks, securing secrets in build environments, and validating deployment configurations.

**Secure Coding Rules** — Language-specific rules for Python, TypeScript, C#, and frontend technologies covering input validation, output encoding, cryptography usage, session management, and access control.

**Security-by-Design** — Principles for incorporating security considerations into architectural decisions before implementation begins — covering threat surface analysis, least privilege, defence in depth, and secure defaults.

---

## Security Throughout the Delivery Lifecycle

Security is not a phase in CORTEX's delivery lifecycle. It is a gate at every phase.

**Requirements** — When a new feature is scoped, CORTEX identifies the threat surface automatically. What data does this feature handle? What external systems does it connect to? What access controls are needed? These questions are answered during requirements analysis, not after implementation.

**Design** — Architecture and design decisions are validated against security patterns. A proposed design that introduces unnecessary data exposure or bypasses access controls is flagged before any code is written.

**Implementation** — The security analyzer runs on the code being written. Findings are surfaced immediately — not in the next audit, but during the current development session, while the context is still fresh and the fix is trivial.

**Code Review** — Secrets and PII are scanned again at the commit boundary. Dependencies are checked for newly published vulnerabilities. Branch hygiene is enforced.

**Integration** — Security integration tests verify that security controls work correctly in the integrated system, not just in unit isolation.

**Security Audit** — A full security audit can be triggered at any time, running the complete threat model analysis and OWASP Top 10 check against the current codebase state.

**Release** — The release security checklist validates that all security gates have passed, secrets have been rotated as required, and the deployment configuration is hardened.

---

## What "Shift Left" Means in Practice

"Shift left" is the principle of moving security earlier in the development process. In most teams, shift left means running security scanners in CI/CD — still late in the process, after code is written, reviewed, and merged.

In CORTEX, shift left means security analysis runs before the first line of implementation is written — during code intelligence analysis, before the execution plan is constructed, and before the governance gate approves the operation. A security finding during intelligence analysis changes the execution plan before any code is touched.

The practical effect: security issues are caught when they require the least effort to fix. A missing input validation caught during analysis is a two-minute addition to the test cases. The same missing validation caught in a production security audit is a regression fix with test coverage, a deployment, and potentially a customer notification.

---

## Infrastructure Resilience — Security at the Platform Level

Beyond application security, CORTEX implements security-oriented resilience patterns in its own infrastructure.

**Circuit Breakers** stop calls to failing services after a configurable threshold, preventing cascade failures where one failing component pulls down the entire system.

**Bulkheads** partition resources so that a failure in one component cannot consume resources needed by others — the same principle used in ship compartment design.

**Tamper-Evident Audit Trail** — every audit record includes a cryptographic link to the previous record. Any modification to historical records breaks the chain, providing proof of tampering.

**Evidence Bundles** package validation evidence — test results, audit traces, governance checks — into verifiable packages that can be produced for compliance reviews. Each bundle is hash-verified to prove it has not been modified after creation.

**Secret Redaction** — all logging infrastructure runs through a secret redactor that strips credentials and sensitive values before they are written to any log. Sensitive data cannot accidentally appear in debug output.

**MCP API Key Authentication** — the HTTP transport layer for CORTEX's MCP gateway enforces API key authentication on all tool-invocation endpoints. Keys are generated, validated, and revoked through a dedicated secrets management system (`cortex/secrets/`). Validation uses constant-time comparison to prevent timing attacks. Public endpoints (health checks) require no key; all tool calls require a valid key.

---

## For Business Leaders

Security compliance is not a checkbox in CORTEX — it is a continuously enforced constraint. When your auditor asks "how do you ensure no secrets are committed to source control?", the answer is: CORTEX blocks secret-containing commits before they reach version control, and the audit trail proves it. When your auditor asks "how do you ensure OWASP Top 10 vulnerabilities are addressed?", the answer is: every release passes a complete OWASP check, and the evidence bundle is available for review.

Security governance that runs automatically at every commit, every build, and every release is security governance that can be demonstrated — not just asserted.

---

*Security layers verified against live implementation · OWASP knowledge verified against registry*
