# Archived Git Hooks — Retired by EnforcementOrchestrator

These shell hooks were **retired** on 2026-02-19 and replaced by
`cortex/orchestrators/git/enforcement_orchestrator.py`.

## Why Archived (Not Deleted)

Kept for forensic reference only. The logic from each hook has been
absorbed into `EnforcementOrchestrator` checks:

| Hook | Absorbed Into |
|------|--------------|
| `pre-commit` | `_check_markdown_artifacts`, `_check_file_naming`, `_check_mcp_policy` |
| `pre-commit-health` | `_run_pre_commit_validator` |
| `pre-commit-wiring-validator` | `_run_pre_commit_validator` |
| `pre-commit-wave8-blacklist` | `_check_health_policy` |
| `pre-commit-golden-test-validator` | `_check_tdd_gate` |
| `pre-commit-test-naming` | `_check_file_naming` |
| `pre-push` | `GitPublishOrchestrator` |
| `pre-push-health` | `_run_pre_commit_validator` |
| `pre-push-wave8-blacklist` | `_check_health_policy` |
| `post-checkout` | Absorbed into wiring health check |
| `pre_commit_health.py` | `_run_pre_commit_validator` |
| `pre_push_health.py` | `_run_pre_commit_validator` |

## Replacement

Use `GitOrchestrator` (MCP tool: `cortex_git_push`) to enforce, sanitize, and push:

```python
from cortex.orchestrators.git import GitOrchestrator

result = await GitOrchestrator().execute(
    repo_path="/path/to/repo",
    branch="main",
    message="feat: your commit message",
)
```

Or via MCP: `cortex_git_push(repo_path=..., branch=..., message=...)`

## Do NOT Restore These Hooks

These hooks created Arnica security surface area. The Python orchestrator
is zero-surface: no shell execution, no GitHub tokens, no Actions runners.
