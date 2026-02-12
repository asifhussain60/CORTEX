# Phase Creation Templates

This directory contains YAML templates for creating standardized phase specifications.

## Templates Available

1. **standard.yaml** - Basic phase template
2. **enhancement.yaml** - Complex enhancement with waves
3. **wave.yaml** - Session-scoped wave template

## Usage

```bash
# Create new phase from template
python -m cortex.cli.phase_creator create --template standard --id ENH-XXX --title "Feature Name"

# Validate existing phase spec
python -m cortex.cli.phase_creator validate path/to/phase.yaml

# Run comprehensive linting
python -m cortex.cli.phase_creator lint path/to/phase.yaml
```

## Validation Rules

The CLI enforces 50+ validation rules including:
- CORE-028 naming conventions (kebab-case, ≤40 chars)
- Minimum 80% test coverage requirement
- ROI justification for scores >9.0
- Wave structure requirements
- Dependency validation
- Deliverables completeness

## Authority

- ENH-084: Standard Phase Creation Practices
- WAVE-6-COMPREHENSIVE-CLEANUP-REFACTORING.yaml
