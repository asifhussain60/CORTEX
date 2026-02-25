# Pull Request Process

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Contributors

## PR Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Branch    │───▶│    Code     │───▶│     PR      │───▶│   Review    │
│   Create    │    │   + Tests   │    │   Submit    │    │  + Approve  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
                                      ┌─────────────┐    ┌─────────────┐
                                      │   Squash    │◀───│    Merge    │
                                      │   Commit    │    │   Approval  │
                                      └─────────────┘    └─────────────┘
```

## Branch Naming

```
{type}/{ticket}-{description}

Types:
- feature/  - New functionality
- fix/      - Bug fixes
- refactor/ - Code restructuring
- docs/     - Documentation
- test/     - Test additions

Examples:
- feature/CORTEX-123-intent-router
- fix/CORTEX-456-circular-import
- docs/CORTEX-789-api-reference
```

## Commit Messages

Follow conventional commits:

```
{type}({scope}): {description}

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Test additions |
| `chore` | Maintenance |

### Examples

```
feat(intent-router): add disambiguation module

- Implement Disambiguator class
- Add confidence threshold configuration
- Include 15 unit tests

AC-ID: AC-INT-003
Phase: impl-intent-router
```

## PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation
- [ ] Test

## AC-ID

AC-{DOMAIN}-{NUMBER}

## Checklist

- [ ] Tests added/updated
- [ ] Type hints on all functions (CORE-011)
- [ ] Docstrings on all functions (CORE-012)
- [ ] No bare except (CORE-013)
- [ ] Files ≤25 chars kebab-case (CORE-028)
- [ ] Documentation updated
- [ ] Self-reviewed code

## Testing

```bash
pytest tests/path/to/test_file.py -v
```

## Screenshots (if applicable)

N/A
```

## Review Checklist

Reviewers verify:

### Code Quality

- [ ] Type hints complete (CORE-011)
- [ ] Docstrings present (CORE-012)
- [ ] No bare except (CORE-013)
- [ ] File naming correct (CORE-028)
- [ ] Imports organized
- [ ] No hardcoded paths (CORE-005)

### Testing

- [ ] Tests included
- [ ] Tests pass locally
- [ ] Coverage maintained ≥80%
- [ ] AC-ID referenced in tests

### Documentation

- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Docstrings complete

### Architecture

- [ ] Follows package separation (ADR-004)
- [ ] Respects tier precedence (ADR-002)
- [ ] Uses ContinuationDecision pattern (ADR-005)

## CI Checks

PRs must pass:

| Check | Requirement |
|-------|-------------|
| Unit Tests | All pass |
| Integration Tests | All pass |
| Coverage | ≥80% |
| Lint (Ruff) | No errors |
| Type Check (mypy) | No errors |
| Security Scan | No high/critical |

## Merge Strategy

- **Squash merge** for feature/fix branches
- **Merge commit** for release branches
- **Rebase** never used on shared branches

## Post-Merge

1. Delete feature branch
2. Update `cortex-impl-map.yaml` if phase completed
3. Update documentation if needed
4. Notify in Slack/Teams

## Related

- [Development Setup](2-development-setup.md)
- [Testing Strategy](3-testing-strategy.md)
- [Code Style Guide](4-code-style-guide.md)
