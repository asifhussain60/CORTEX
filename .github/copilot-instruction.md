# CORTEX Implementation Instructions
**Version:** 3.0 | **Updated:** 2026-01-21 | **Authority:** cortex-impl-map.yaml v3.9

---

## Project Overview

You are working on **CORTEX** — a governance-first AI development platform with 3-tier architecture, autonomous orchestration, and full AC-ID driven development.

**Current Status:**
| Metric | Value |
|--------|-------|
| **Test Collection** | 7,540+ tests |
| **Intent Router** | 128/128 (100%) ✅ |
| **Governance Engine** | 348/368 (95%) ✅ |
| **Orchestrators** | 412/613 (67%) ⏳ |
| **Infrastructure** | 472/472 (100%) ✅ |
| **Domain Brain** | 213/353 (60%) ⏳ |
| **TIER 0 Rules** | 29/29 implemented ✅ |

---

## Architecture Summary

```
CORTEX: Governance-First AI Development Platform
├── Tier 0: Immutable SKULL Rules (29 rules)
│   └── cortex_brain/tier0/governance/core-rules.yaml
├── Tier 1: Domain-Specific Rules
│   └── cortex_brain/tier1/ (domain customizations)
├── Tier 2: Engineering Standards
│   └── cortex_brain/tier2/ (hallucination prevention, safety)
└── State Management
    └── cortex_brain/state/governance.db (257 production ACs)
```

---

## Key Implementation Principles

### 1. Response Header (CORE-029 — MANDATORY)

Every response MUST include:

```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
```

| Variable | Examples |
|----------|----------|
| `{operation}` | Implementation, Code Analysis, Review, Governance Evaluation |
| `{phase}` | PHASE-E-TDD-IMPLEMENTATION, PHASE-DOC-REMEDIATION |
| `{orchestrator}` | MasterOrchestrator, BuilderOrchestrator, GovernanceOrchestrator |

### 2. AC-ID Driven Development

- **Format:** `AC-{CATEGORY}-{NNN}` or `AC-{CATEGORY}-{NNN}-{NN}`
- **Categories:** AR, FR, NFR, VALIDATE, METRICS, COHERENCE, ENHANCE, REM, OB, DOM, MCP
- Every change tied to exactly ONE AC-ID
- No orphaned code commits without AC-ID

### 3. TDD Enforcement (CORE-008)

```
Write Tests → Run Tests (RED) → Implement Code → Run Tests (GREEN) → Refactor
```

- Every AC-ID MUST have ≥1 test before implementation
- Tests follow `tests/unit/test_*.py` or `tests/integration/test_*.py`
- Minimum coverage per AC: 80%

### 4. Communication Style (CORE-REM-003-01)

**Word Limits:**
- Maximum: 500 words
- Target: 200-400 words
- Exception: Technical specs (≤800)

**Prohibited Patterns:**
❌ "Let me analyze this"  
❌ "I will implement"  
❌ "I believe the best approach"  
❌ "just", "actually", "basically"

**Preferred Patterns:**
✅ Imperative voice: "Implement", "Execute", "Validate"  
✅ Direct: "This follows CORE-019"  
✅ Governance-cited: "Per CORE-008, tests precede implementation"

---

## Directory Organization

### Source Code
```
cortex/                          # Canonical package (ALL source)
├── api/                         # REST endpoints, health checks
├── brain/core/                  # Brain integration logic
├── core/                        # Result<T>, interfaces, utilities
├── infrastructure/              # DB, logging, metrics, tracing
├── intent_router/               # Intent classification + routing
├── mcp/                         # MCP server + 14 tools
│   ├── registry.py              # ToolRegistry
│   ├── server.py                # MCP server entry
│   └── tools/                   # Categorized tools
│       ├── governance/          # 5 tools
│       ├── orchestration/       # 4 tools
│       ├── knowledge/           # 3 tools
│       └── utility/             # 2 tools
└── orchestrators/               # Domain orchestrators
    ├── core/                    # MasterOrchestrator
    ├── domain/                  # ACOrchestrator, GovernanceOrchestrator
    └── registry/                # OrchestratorRegistry
```

### Governance & State
```
cortex_brain/                    # State management
├── tier0/governance/            # SKULL rules (immutable)
│   └── core-rules.yaml          # 29 rules
├── tier1/                       # Domain rules
├── tier2/                       # Engineering standards
└── state/
    └── governance.db            # Audit database
```

### Tests
```
tests/
├── unit/                        # Unit tests (~300 files)
│   ├── intent_router/           # 128 tests ✅
│   ├── orchestrators/           # 413 tests
│   └── governance/              # 368 tests
├── integration/                 # Integration tests (~80 files)
└── e2e/                         # End-to-end tests (~29 files)
```

### Roadmap
```
_workspaces/roadmap/
├── cortex-impl-map.yaml         # SSOT: Implementation status
├── phases/                      # Phase specifications
│   └── PHASE-E-TDD-IMPLEMENTATION.yaml
└── reports/                     # Phase reports
```

---

## TIER 0 Governance Rules (Critical)

| Rule | Purpose | Severity |
|------|---------|----------|
| **CORE-001** | Incremental execution (<500 lines/turn) | BLOCKED |
| **CORE-002** | No *-summary.md files | BLOCKED |
| **CORE-003** | Visual progress bars (█████░░░) | BLOCKED |
| **CORE-005** | No hardcoded paths | BLOCKED |
| **CORE-008** | TDD (tests before code) | STRICT |
| **CORE-011** | Type hints ALL functions | STRICT |
| **CORE-012** | Google docstrings | STRICT |
| **CORE-013** | No bare `except:` | STRICT |
| **CORE-029** | Response headers | BLOCKED |

---

## Implementation Workflow

### When Starting a New AC-ID

1. **Read AC-ID** from `_workspaces/roadmap/phases/phase-*.yaml`
2. **Check dependencies** - Read `requires` field
3. **Create test file FIRST** (TDD pattern)
4. **Write failing tests** (RED phase)
5. **Implement feature** (GREEN phase)
6. **Add type hints** - CORE-011 compliance
7. **Add docstrings** - CORE-012 compliance
8. **Verify tests pass**
9. **Update phase YAML** - mark AC as COMPLETED

### Test File Template

```python
"""
Tests for {module_name}
AC-IDs tested: {AC-ID-1}, {AC-ID-2}

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.{module_path} import {ClassName}


class Test{ClassName}:
    """Tests for {ClassName} - Implements {AC-ID}"""
    
    @pytest.fixture
    def instance(self) -> {ClassName}:
        """Create test instance."""
        return {ClassName}()
    
    def test_{ac_id_snake_case}(self, instance: {ClassName}) -> None:
        """Test AC-ID: {AC-ID}"""
        # Arrange
        expected = "expected_value"
        
        # Act
        result = instance.method_name("input")
        
        # Assert
        assert result.is_ok()
```

### Source Module Template

```python
"""
Module: {module_name}
AC-ID: {ac_id}
Purpose: {description}

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Optional, Dict, Any
from cortex.core.result import Result, Ok, Err


class {ClassName}:
    """
    {Description}
    
    Implements: {AC-ID}
    """
    
    def method_name(self, param: str) -> Result[str]:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Result[str]: Success with value or error
        """
        pass
```

---

## Common Commands

```bash
# Run all tests
pytest tests/ -v

# Test collection (expect 7540+)
pytest tests/ --co -q | wc -l

# Run specific module
pytest tests/unit/intent_router/ -v

# Coverage report
pytest --cov=cortex --cov-report=html

# Governance validation
python -m cortex.brain.core.governance_registry --validate

# MCP server
python -m cortex.mcp.server

# Detect hanging tests
python scripts/detect_hanging_tests.py --threshold 5.0
```

---

## Key File References

| Document | Purpose | Location |
|----------|---------|----------|
| **Implementation Map** | SSOT for all phases | `_workspaces/roadmap/cortex-impl-map.yaml` |
| **Governance Rules** | 29 SKULL rules | `cortex_brain/tier0/governance/core-rules.yaml` |
| **Master Prompt** | System prompt | `.github/prompts/CORTEX.prompt.md` |
| **Copilot Instructions** | Standalone reference | `.github/prompts/copilot-instruction.md` |
| **Builder Prompt** | AC implementation | `.github/prompts/cortex-builder.prompt.md` |
| **Phase Specs** | AC requirements | `_workspaces/roadmap/phases/*.yaml` |

---

## Current Phase Context

**Machine Tracks:**
- **Mac:** ⏳ PHASE-E-TDD-IMPLEMENTATION (Day 1 of 15-20)
- **Win:** ✅ COMPLETE (5/5 phases, 48 tests)

**Test Summary:**
```
Intent Router:    128/128 (100%) ✅
Governance:       348/368 (95%)  ✅
Orchestrators:    412/613 (67%)  ⏳
Domain Brain:     213/353 (60%)  ⏳
Infrastructure:   472/472 (100%) ✅
```

---

## DO / DON'T Quick Reference

### ✅ DO
- Use `Result<T>` pattern for operations
- Type hint all function parameters AND returns
- Include AC-ID in all docstrings
- Create tests BEFORE implementation
- Validate governance before execution
- Cite TIER 0 rules in decisions

### ❌ DON'T
- Create .py files in root
- Use hardcoded absolute paths
- Skip response headers
- Skip type hints on public APIs
- Create .md outside `docs/`
- Use conversational filler language
- Implement without corresponding tests

---

**Last Updated:** 2026-01-21  
**Version:** 3.0  
**Status:** ✅ Aligned with cortex-impl-map.yaml v3.9
