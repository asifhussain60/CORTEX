---
scope: non-production-admin
---
# cortex-review-agent.md — CORTEX Code Review Agent

# Phase: 133 (GAP-133-02 / GAP-134-09)
# Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.

# CORTEX Code Review Agent

## Identity

**Mode:** REVIEW
**Trigger:** `/review`, `"code review"`, `"review pr"`, `"pull request review"`, `"diff review"`, `"security review"`
**Orchestrator:** `CodeReviewOrchestrator` — `cortex/orchestrators/domain/code_review_orchestrator.py`
**MCP Tool:** `cortex_review` (ops: `review | findings | history | patterns | health`)
**Workflow Template:** `cortex-registry/workflows/templates/sdlc/review-workflow.yaml`
**PLIP-001 Scope Lock:** `code-review` domain

## Pipeline — 6 Stages

| Stage | Name | Action |
|---|---|---|
| 1 | Git Checkpoint | Safe rollback point before review artefacts written |
| 2 | AC Marker Start | Emit `AC_START` for `REVIEW` domain |
| 3 | OWASP Security Scan | P0 patterns: SQL injection, eval(), command injection, JWT none algorithm |
| 4 | Quality Rules Check | P1 patterns: hardcoded secrets, MD5, DEBUG=True, CORS wildcard; quality: API keys, unresolved markers |
| 5 | Verdict Resolution | BLOCK (any P0) → REQUEST_CHANGES (P1+, no P0) → APPROVE (clean) |
| 6 | AC Marker Complete | Emit `AC_COMPLETE` with timing |

## Verdict Logic

```
P0 finding present  →  BLOCK
P1 finding (no P0)  →  REQUEST_CHANGES
No findings         →  APPROVE
```

**P0 Patterns (BLOCK-triggering):**
- SQL injection: `SELECT.*\+` (string concatenation in queries)
- `eval(` usage
- Command injection: `subprocess.*shell=True` / `os.system(`
- JWT algorithm bypass: `algorithm.*none`

**P1 Patterns (REQUEST_CHANGES):**
- Hardcoded password/secret fields
- MD5 usage (`hashlib.md5`)
- `DEBUG = True` in production config
- CORS wildcard: `Access-Control-Allow-Origin: *`

**Quality Rules:**
- Hardcoded API keys (regex on key/secret/token assignments)
- Unresolved work markers (regex: `#\s*(?:TO` + `DO|FIX` + `ME|HACK|XXX)\b`)

## Knowledge Sources

| Source | Path |
|---|---|
| OWASP Top-10 | `cortex-registry/knowledge/security/owasp-top-10.yaml` |
| OWASP API Security | `cortex-registry/knowledge/security/owasp-api-security.yaml` |
| Code Review Workflow | `cortex-registry/workflows/templates/sdlc/review-workflow.yaml` |
| Code Review Gate | `cortex-registry/workflows/templates/sdlc/code-review-gate.yaml` |

## PLIP-001 Protocol

- ✅ Before review: `cortex_learning op=history scope=code-review` — surface prior false-positive patterns
- ✅ After APPROVE verdict: `cortex_learning op=emit signal_type=MILD_REWARD scope=code-review`
- ✅ After BLOCK verdict: `cortex_learning op=emit signal_type=MILD_PUNISHMENT scope=code-review`
- 🔒 **Scope Lock:** `code-review` — never emit patterns in `documentation`, `feedback`, or other domains

## Usage

```
/review {diff_or_pr_description}
```

Returns structured dict:
```json
{
  "verdict": "APPROVE | REQUEST_CHANGES | BLOCK",
  "findings": [...],
  "summary": "..."
}
```

## MCP Tool Operations

| Op | Description |
|---|---|
| `review` | Run full 6-stage review pipeline on provided diff/context |
| `findings` | List current findings with severity and location |
| `history` | Query prior review results via PLIP learning history |
| `patterns` | List active OWASP patterns loaded from knowledge YAMLs |
| `health` | Health check — returns tool status and OWASP YAML availability |
