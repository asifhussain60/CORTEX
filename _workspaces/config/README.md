# CORTEX Configuration Directory

This directory contains essential configuration files for CORTEX development and deployment.

## Files

### Pre-commit Hooks
- `.pre-commit-config.yaml` - Pre-commit framework configuration
- `.pre-commit-hooks.yaml` - Custom CORTEX pre-commit hooks

**Installation:**
```bash
cd /path/to/CORTEX
pre-commit install
```

**Manual Execution:**
```bash
pre-commit run --all-files
```

**Bypass (use with caution):**
```bash
git commit --no-verify
```

## Purpose

These configuration files are kept in `_workspaces/config/` to:
1. Keep the root directory clean and focused on core artifacts
2. Centralize all development configuration in one place
3. Make configuration management easier to maintain
4. Separate infrastructure concerns from application code

## Related Files

Other configuration files in the CORTEX root:
- `cortex-config.yaml` - Runtime configuration
- `cortex-impl-map.yaml` - Implementation status
- `mkdocs.yml` - Documentation generation
- `.knowledge-index.yaml` - Knowledge system registry
- `.knowledge-synthesis-rules.yaml` - Knowledge composition rules
