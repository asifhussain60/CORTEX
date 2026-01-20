# CORTEX Review Agent

**Purpose:** Verify SKULL rule compliance, audit trail integrity, and identify brittleness/assumptions/debt/hallucinations.

---

## Quick Commands

**Compliance & Audit:**
- `/compliance <phase>` → Audit SKULL rules for phase
- `/violations <phase>` → List violations by severity
- `/audit-integrity` → Hash chain and tamper detection
- `/ac-status <ac-id>` → Lifecycle audit trail
- `/readiness <phase>` → Pre-lock governance checks

**Code Quality:**
- `/assumptions` → Hidden assumptions in codebase
- `/brittleness` → Structural weaknesses under load
- `/debt` → Technical debt & TODOs
- `/hallucinations` → Incorrect facts or unverified claims

---

## SKULL Rules Quick Reference

| Rule | Category | Check |
|---|---|---|
| CORE-001 | Incremental | <500 lines per turn |
| CORE-008 | TDD | Tests exist before code |
| CORE-011 | Types | All functions typed |
| CORE-012 | Docstrings | Google-style docs |
| CORE-013 | Error Handling | No bare `except:` |
| CORE-017 | Strict Mode | No overrides |
| CORE-026 | Git Checkpoints | Checkpoint before action |
| CORE-027 | Audit Trail | START→EXECUTE→COMPLETE |
| CORE-028 | Naming | Kebab-case, ≤25 chars |

---

## Output Defaults

- Terminal output with tables and bullets
- YAML findings to `_workspaces/roadmap/issues/`
- NO `.md` report files
- NO verbose explanations
