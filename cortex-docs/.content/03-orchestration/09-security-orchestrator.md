# SecurityOrchestrator

---
title: SecurityOrchestrator — Security-First Development
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/core/security_orchestrator.py
order: 9
---

## Purpose

SecurityOrchestrator (`cortex/orchestrators/core/security_orchestrator.py`) handles security-focused operations:

- Security vulnerability scanning (via LENS Security Analyzer)
- Credential exposure detection
- SQL injection pattern identification
- SAST (Static Application Security Testing) integration
- CVE pattern matching

**Implements:** `IOrchestrator`

## Integration Points

| Input From | What It Provides |
|-----------|-----------------|
| LENS Security Analyzer | Vulnerability findings with severity |
| EnforcementOrchestrator | Security agent validation |
| Bandit SAST | Python-specific security analysis |
| Requirements audit | Dependency CVE scanning |

## Phase 10 Production Readiness

During Phase 10, security hardening tests validated:
- SQL injection audit across all infrastructure layers
- Credential scan (no hardcoded secrets)
- Bandit SAST integration
- requirements.txt parsing and CVE checking

All 25 production readiness tests pass (including 5 security-specific tests).

---

*Verified against security_orchestrator.py · 25 February 2026*
