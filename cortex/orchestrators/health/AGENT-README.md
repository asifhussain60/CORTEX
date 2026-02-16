# CORTEX Health Orchestrator

Autonomous repository health scanning and issue detection.

## Quick Start

```bash
# Run all agents
python -m cortex.orchestrators.health.cli

# Run specific agent
python -m cortex.orchestrators.health.cli --agents DuplicateDetection

# Export to dashboard
python -m cortex.orchestrators.health.cli --export-dashboard

# JSON output
python -m cortex.orchestrators.health.cli --json > health_report.json
```

## Agents

| Agent | Purpose | Issues Detected |
|-------|---------|-----------------|
| **DuplicateDetectionAgent** | CORE-035 violations | Exact duplicates, basename conflicts |
| **StubDetectionAgent** | Weak implementations | Low LOC + complexity + missing tests |
| **PathIntegrityAgent** | Import/path issues | Broken imports, deprecated paths |
| **VersionCleanupAgent** | Versioned files | Files with _v1, _old, _legacy suffixes |
| **TestCoverageAgent** | Missing tests | Source files without corresponding tests |
| **RegistryConsistencyAgent** | Registry issues | YAML syntax, schema validation |
| **MCPAutoHealingAgent** | MCP health | Dependencies, configuration issues |

## Configuration

Health agents use tuned defaults from [health_config.py](health_config.py) to minimize false positives.

### Key Settings

- **Stub Detection:** Requires 3+ indicators (low LOC, complexity, no tests, etc.)
- **Duplicate Detection:** Excludes common module names (`models.py`, `config.py`)
- **Path Integrity:** Only checks project-specific imports (not stdlib/third-party)

## Health Score

Score calculated as: `100 - (Critical×10 + High×5 + Medium×2 + Low×1)`

| Score | Status |
|-------|--------|
| 90-100 | Excellent |
| 70-89 | Good |
| 50-69 | Fair |
| 30-49 | Poor |
| 0-29 | Critical |

## Integration

### Pre-Commit Hook

```bash
python -m cortex.orchestrators.health.cli --agents DuplicateDetection,PathIntegrity
```

### CI/CD Pipeline

```yaml
- name: Health Check
  run: python -m cortex.orchestrators.health.cli --export-dashboard
```

### Dashboard Export

Results automatically exported to `cortex_brain/governance.db` when `--export-dashboard` flag used.

## Phase History

- **PHASE-92:** Initial implementation
- **PHASE-95:** False positive reduction (87% improvement)
  - Fixed duplicate detection (2,047 → 119 issues)
  - Fixed path integrity (6,901 → 759 issues)
  - Added health_score calculation
  - Created tuned configuration

## Authority

- CORE-008: TDD mandatory
- CORE-011: Type hints required
- CORE-012: Google-style docstrings
- CORE-035: Single canonical implementation
