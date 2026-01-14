# CORTEX 7.0 Implementation Instructions

## Project Overview

You are working on CORTEX 7.0, a governance-first audit system with a 3-tier architecture. The implementation follows a strict AC-ID (Acceptance Criteria ID) driven approach with full audit trails.

## Architecture Summary

```
CORTEX 7.0 Architecture
├── Tier 0: Immutable SKULL Rules (25 rules)
│   └── cortex-brain/tier0/governance/core-rules.yaml
├── Tier 1: Project Governance (YAML + SQLite)
│   └── cortex-brain/tier1/
└── Tier 2: Engineering Standards
    └── cortex-brain/tier2/
```

## Key Principles

### 1. Audit-First Pattern
Every operation must:
1. Log intent BEFORE execution
2. Execute the operation
3. Log result AFTER execution
4. Maintain hash chain integrity

### 2. AC-ID Driven Development
- Every change must be tied to an AC-ID
- AC-IDs follow format: `AC-{CATEGORY}-{NNN}` or `AC-{CATEGORY}-{NNN}-{NN}`
- Categories: AR (Architecture), FR (Functional), NFR (Non-Functional), VALIDATE, METRICS, COHERENCE, EXPLAIN, BRITTLE

### 3. Evidence-Based Verification
Every completed AC-ID requires:
- Code changes (git diff)
- Test results (pytest output)
- Audit logs (filtered by AC-ID)

## Implementation Roadmap Location

All implementation details are in YAML format:
```
.github/roadmap/
├── cortex-master.yaml          # Master plan with all requirements
├── phases/
│   ├── phase-01.yaml           # Foundation (5 days)
│   ├── phase-02.yaml           # Orchestration Core (5 days)
│   ├── phase-03.yaml           # Safety & Observability (5 days)
│   ├── phase-04.yaml           # Production Hardening (5 days)
│   ├── phase-05.yaml           # Brittleness Fixes (5 days)
│   └── phase-parallel.yaml     # Folder Migration (16 hours, non-blocking)
└── docs/                       # Documentation (reference only)
```

## Code Organization

```
src/
├── core/                       # Core business logic
│   ├── config.py
│   ├── interfaces.py
│   ├── result.py
│   ├── governance_registry.py  # To be created
│   ├── tier_resolver.py        # To be created
│   └── decorators/             # To be created
├── infrastructure/             # Infrastructure components
│   ├── audit_logger.py
│   └── database_manager.py     # To be created
├── mcp/                        # MCP Server integration
│   ├── decorator.py
│   └── registry.py
├── orchestrators/              # Orchestration layer
│   ├── core/
│   ├── domain/
│   └── custom/
└── tools/
    └── toolkit.py
```

## Testing Standards

- All tests in `tests/` directory
- Unit tests: `tests/unit/test_*.py`
- Integration tests: `tests/integration/test_*.py`
- Performance tests: `tests/performance/test_*.py`
- Each AC-ID should have corresponding test(s)

## Performance Targets

| Operation | Target |
|-----------|--------|
| Governance evaluation | <5ms per rule |
| SQLite query | <1ms |
| State transition | <10ms |
| Evidence capture | <500ms |
| Audit logging | <5ms |

## Quality Targets

| Metric | Target |
|--------|--------|
| Test pass rate | ≥98% |
| Code coverage | ≥80% |
| Verification rate | ≥80% |

## Implementation Workflow

When implementing any feature:

1. **Read the AC-ID** from the phase YAML file
2. **Check dependencies** are completed
3. **Create/modify files** as specified
4. **Write tests** that verify acceptance criteria
5. **Run tests** to verify implementation
6. **Update status** in the phase YAML file
7. **Generate evidence** bundle

## File Creation Patterns

### New Python Module
```python
"""
Module: {module_name}
AC-ID: {ac_id}
Purpose: {description}
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type imports here
    pass


class {ClassName}:
    """
    {Description}
    
    Implements: {AC-ID}
    """
    
    def __init__(self):
        pass
```

### New Test File
```python
"""
Tests for {module_name}
AC-IDs tested: {list of AC-IDs}
"""

import pytest

from src.{module_path} import {ClassName}


class Test{ClassName}:
    """Tests for {ClassName}"""
    
    def test_{ac_id_snake_case}(self):
        """Test AC-ID: {AC-ID}"""
        # Arrange
        # Act
        # Assert
        pass
```

## Common Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_governance_registry.py

# Run with coverage
pytest --cov=src --cov-report=html

# Check test collection
pytest --co -q
```

## Current Status

Check `.github/roadmap/cortex-master.yaml` for:
- `tracking.current_phase` - Current implementation phase
- `tracking.current_day` - Current day within phase
- `tracking.blockers` - Any blocking issues

## Important Files to Reference

1. **Master Plan**: `.github/roadmap/cortex-master.yaml`
2. **Current Phase**: `.github/roadmap/phases/phase-XX.yaml`
3. **Governance Rules**: `cortex-brain/tier0/governance/core-rules.yaml`
4. **Builder Prompt**: `.github/prompts/cortex-builder.prompt.md`

## Do NOT

- Create markdown files for the implementation plan (YAML only)
- Skip AC-ID verification
- Implement without corresponding tests
- Modify governance rules in Tier 0
- Bypass the audit-first pattern
- Mark AC-IDs complete without evidence

## Do

- Always read the relevant YAML files first
- Follow the day-by-day breakdown in phase files
- Update tracking sections after completing tasks
- Generate evidence bundles for completed AC-IDs
- Report blockers immediately
- Ask for clarification when requirements are unclear
