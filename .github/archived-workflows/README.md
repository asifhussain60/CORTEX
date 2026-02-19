# Archived GitHub Actions Workflows — Retired by GitOrchestrator Pipeline

These workflows were **retired** on 2026-02-19 and replaced by
`cortex/orchestrators/git/` orchestrators running fully in-process.

## Reason for Retirement

These workflows were flagged by **Arnica** as security surface area.
The CORTEX orchestration pipeline eliminates the need for:
- GitHub Actions runners with elevated permissions
- Shell-based secret scanning tools
- External SAST/dependency scanners (absorbed into SanitizationOrchestrator)

## Absorption Map

| Workflow | Replaced By |
|----------|-------------|
| `security-gate.yml` | `SanitizationOrchestrator` (Stage 2 of GitOrchestrator) |
| `tdd-gate.yml` | `EnforcementOrchestrator._check_tdd_gate()` (Stage 1) |
| `governance-alignment.yml` | `EnforcementOrchestrator._check_file_naming()` (Stage 1) |

## Workflows Kept (Not Retired)

| Workflow | Reason |
|----------|--------|
| `e2e.yml` | End-to-end test suite — not absorbed |
| `golden-tests.yml` | Golden test gate — not absorbed |
| `health-check.yml` | Scheduled nightly health — not absorbed |
| `readiness-verification.yml` | Release readiness — not absorbed |
| `rollback.yml` | Emergency rollback — not absorbed |
| `core-097-duplicate-detection.yml` | Duplicate detection — not absorbed |
| `test-rephrase-mode.yml` | Rephrase mode tests — not absorbed |

## Replacement Usage

```python
# Replaces security-gate.yml + tdd-gate.yml + governance-alignment.yml
from cortex.orchestrators.git import GitOrchestrator

result = await GitOrchestrator().execute(
    repo_path="/path/to/repo",
    branch="main",
    message="feat: your commit message",
)
```

Or via MCP tool: `cortex_git_push`
