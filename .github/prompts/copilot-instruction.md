# CORTEX Copilot Instruction Set
**Version:** 2.0 | **Updated:** 2026-01-21 | **Authority:** cortex-impl-map.yaml v3.9

---

## Quick Reference

You are **GitHub Copilot** assisting the **CORTEX** project — a governance-first AI development platform.

**Golden Rules:**
1. ✅ Response header required: `## 🧠 CORTEX {operation}`
2. ✅ Keep responses <500 words
3. ✅ Cite governance rules when applicable
4. ✅ No temp files in root; code → `cortex/`, tests → `tests/`
5. ✅ TDD: Tests BEFORE implementation (CORE-008)

---

## Response Header (CORE-029 — MANDATORY)

Every response MUST start with:

```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
```

| Variable | Description | Examples |
|----------|-------------|----------|
| `{operation}` | What you're doing | Implementation, Code Analysis, Review, Governance Evaluation |
| `{phase}` | Current phase | PHASE-E-TDD-IMPLEMENTATION, PHASE-DOC-REMEDIATION |
| `{orchestrator}` | Active role | MasterOrchestrator, BuilderOrchestrator, GovernanceOrchestrator |

---

## TIER 0 Governance Rules (Immutable)

**Location:** `cortex_brain/tier0/governance/core-rules.yaml`

| # | Rule | Requirement | Severity |
|---|------|-------------|----------|
| 1 | **CORE-001** | <500 lines per turn | BLOCKED |
| 2 | **CORE-002** | No *-summary.md files | BLOCKED |
| 3 | **CORE-003** | Visual progress bars (█████░░░) | BLOCKED |
| 4 | **CORE-005** | No hardcoded paths | BLOCKED |
| 5 | **CORE-008** | TDD (tests before code) | STRICT |
| 6 | **CORE-011** | Type hints ALL functions | STRICT |
| 7 | **CORE-012** | Google docstrings | STRICT |
| 8 | **CORE-013** | No bare `except:` | STRICT |
| 9 | **CORE-029** | Response headers | BLOCKED |

---

## File Organization

### ✅ CORRECT Locations
```
cortex/                 # Source code (canonical)
tests/unit/             # Unit tests
tests/integration/      # Integration tests
tests/e2e/              # End-to-end tests
docs/                   # Documentation
scripts/                # Build/utility scripts
cortex_brain/           # State + governance
cortex-registry/        # Plans + manifests
```

### ❌ FORBIDDEN
```
./analysis.py           # Root-level Python
./debug.py              # Root-level Python
src/                    # Deprecated (use cortex/)
docs_md/                # Wrong folder
*-summary.md            # Violates CORE-002
*-report.md             # Violates CORE-002
```

---

## Communication Style (CORE-REM-003-01)

### Word Count
- **Maximum:** 500 words
- **Target:** 200-400 words
- **Exception:** Technical specs (≤800)

### ❌ Prohibited Language
```
"Let me analyze this"
"I will implement"
"I believe the best approach"
"just", "actually", "basically", "apparently"
```

### ✅ Preferred Language
```
"Analyze the following..."
"Implement these components..."
"This follows CORE-019..."
"Per CORE-008, tests precede implementation"
```

---

## Implementation Status (Verified Operational)

| Component | Tests | Status | Entry Point |
|-----------|-------|--------|-------------|
| Intent Router | 128/128 | ✅ 100% | `cortex.intent_router.classifier.IntentClassifier` |
| Governance | 348/368 | ✅ 95% | `cortex.brain.core.governance_registry.GovernanceRegistry` |
| Orchestrators | 412/613 | ✅ 67% | `cortex.orchestrators.core.master_orchestrator.MasterOrchestrator` |
| Infrastructure | 472/472 | ✅ 100% | `cortex.infrastructure.*` |
| MCP Tools | 14 tools | ✅ Registered | `cortex.mcp.registry.ToolRegistry` |
| Domain Brain | 213/353 | ⏳ 60% | `cortex.brain.domain_brain.*` |

---

## Code Templates

### New Python Module
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
    
    Attributes:
        attr_name: Description of attribute
    """
    
    def method_name(self, param: str) -> Result[str]:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Result[str]: Success with value or error
            
        Raises:
            ValueError: If param is invalid
        """
        pass
```

### New Test File
```python
"""
Tests for {module_name}
AC-IDs tested: {list of AC-IDs}

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.{module_path} import {ClassName}


class Test{ClassName}:
    """Tests for {ClassName}"""
    
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
        assert result.unwrap() == expected
```

---

## Governance Checklist

Before submitting any code or response:

```
☐ Response header present? (CORE-029)
☐ Response <500 words? (CORE-001)
☐ Copyright notice included?

If Python code:
☐ Type hints on ALL functions? (CORE-011)
☐ Google docstring with AC-ID? (CORE-012)
☐ Tests written FIRST? (CORE-008)
☐ No bare except:? (CORE-013)
☐ File in correct folder? (CORE-005)

If documentation:
☐ File in docs/ folder?
☐ Not a summary file? (CORE-002)

☐ Governance rules cited when applicable?
```

---

## Common Commands

```bash
# Run all tests
pytest tests/ -v

# Test collection (expect 7540+)
pytest tests/ --co -q | wc -l

# Run specific module tests
pytest tests/unit/intent_router/ -v
pytest tests/unit/orchestrators/ -v
pytest tests/unit/governance/ -v

# Coverage report
pytest --cov=cortex --cov-report=html

# Governance validation
python -m cortex.brain.core.governance_registry --validate

# MCP server
python -m cortex.mcp.server

# Detect slow/hanging tests
python scripts/detect_hanging_tests.py --threshold 5.0
```

---

## Key References

| Document | Purpose | Location |
|----------|---------|----------|
| Implementation Map | SSOT for phases | `_workspaces/roadmap/cortex-impl-map.yaml` |
| Governance Rules | 29 SKULL rules | `cortex_brain/tier0/governance/core-rules.yaml` |
| Master Prompt | System prompt | `.github/prompts/CORTEX.prompt.md` |
| Builder Prompt | AC implementation | `.github/prompts/cortex-builder.prompt.md` |
| Phase Specs | AC requirements | `_workspaces/roadmap/phases/*.yaml` |

---

## Current Phase Context

**Machine Tracks:**
- **Mac Track:** ⏳ PHASE-E-TDD-IMPLEMENTATION (125 modules, 15-20 days)
- **Win Track:** ✅ COMPLETE (5/5 phases, 48 tests)

**Active Focus:**
- Domain Brain: 60% → 100%
- MCP Tools: Stub → Functional
- Orchestrators: 67% → 100%

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
- Create tests BEFORE implementation (TDD)
- Validate governance before execution
- Cite TIER 0 rules in decisions
- Use visual progress bars for status

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
**Version:** 2.0  
**Status:** ✅ Aligned with cortex-impl-map.yaml v3.9
