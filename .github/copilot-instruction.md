# CORTEX Master Orchestrator: Unified Implementation Guide
**Version:** 4.0 | **Updated:** 2026-01-23 | **Authority:** cortex-impl-map.yaml v2.0  
**Single Entry Point:** Use this with CORTEX.prompt.md for complete context

---

## ⚡ Quick Start: Use CORTEX.prompt.md First

This file is a **companion reference**. For complete context, start with:

**Primary:** `.github/prompts/CORTEX.prompt.md` (v6.0 — Master Orchestrator System Prompt)  
**Companion:** `.github/copilot-instruction.md` (this file — Practical workflow guide)

Both files are **unified and synchronized** for seamless master orchestrator operation.

---

## Project Identity

**CORTEX** — Governance-first AI development platform with 4-stage intent routing, domain orchestration, and AC-ID driven development.

### Current Operational Status (2026-01-23)

| Component | Status | Notes |
|-----------|--------|-------|
| **Intent Router** | ✅ 100% READY | 128/128 tests, production-ready |
| **Governance** | ✅ 95% READY | 29 TIER 0 rules locked |
| **Infrastructure** | ✅ 100% READY | Fault tolerance, pooling, tracing verified |
| **Orchestrators** | ⏳ 67% IN-PROGRESS | Core logic complete, domain handlers developing |
| **Domain Brain** | ⏳ 60% IN-PROGRESS | Query engines ready, synthesis pending |
| **MCP Tools** | ✅ 100% REGISTERED | 14 tools active (governance, orchestration, knowledge, utility) |

### Critical Status: PRODUCTION HARDENING

- **Status:** NOT PRODUCTION READY — 10 CRITICAL findings block deployment
- **Remediation:** 3 phases (47 hours), Mac track: Phases 1-2 COMPLETED
- **Blocking Issues:** Race conditions, external API timeouts, bare excepts, global state
- **Target Completion:** 2026-02-22

---

## Response Header Mandate (CORE-029)

**EVERY RESPONSE MUST START WITH THIS:**

```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
```

**Examples:**
- `## 🧠 CORTEX Implementation` | Phase: PHASE-GOVERNANCE-HARDENING
- `## 🧠 CORTEX Code Review` | Phase: PHASE-3-ARCHITECTURE-REFACTORING
- `## 🧠 CORTEX Testing` | Orchestrator: BuilderOrchestrator

---

## TIER 0 Governance: 9 Critical Rules

| Rule | Category | Enforcement |
|------|----------|-------------|
| **CORE-001** | Incremental | ≤500 lines per response |
| **CORE-002** | Artifacts | No `*-summary.md` files |
| **CORE-003** | UI Sanitization | No progress bars (█████░░░) |
| **CORE-005** | Security | No hardcoded paths |
| **CORE-008** | TDD | Tests BEFORE implementation (RED→GREEN→REFACTOR) |
| **CORE-011** | Type Safety | ALL functions: type hints on params + returns |
| **CORE-012** | Documentation | Google-style docstrings (mandatory) |
| **CORE-013** | Error Handling | NO bare `except:` clauses (CRITICAL BLOCKER) |
| **CORE-029** | Response Format | Response header format (see above) |

---

## AC-ID Driven Development Workflow

### Format
```
AC-{CATEGORY}-{NNN}[-{NN}]
Examples: AC-CORE-001, AC-FR-042, AC-REM-CRIT-003, AC-ENH-002-01
```

### Categories
- **CORE** (29) — Governance rules
- **FR** (~150) — Functional requirements
- **NFR** (~80) — Non-functional requirements
- **AR** (~60) — Architecture
- **REM** (37) — Remediation items (CRITICAL path)
- **ENH** (~40) — Enhancements
- **OB** (~25) — Observability
- **MCP** (14) — MCP tool definitions

### Implementation Checklist

```
1. ✓ Find AC-ID in _workspaces/roadmap/phases/*.yaml
2. ✓ Read requirements & check dependencies (requires: field)
3. ✓ Create tests FIRST (RED phase)
   └─ File: tests/unit/test_{module}_{ac_id}.py
   └─ Minimum: 80% coverage target
4. ✓ Run tests (verify RED)
5. ✓ Implement code (GREEN phase)
   └─ Add type hints (CORE-011)
   └─ Add docstrings (CORE-012)
   └─ Use specific exceptions, never bare except (CORE-013)
6. ✓ Run tests (verify GREEN)
7. ✓ Update phase YAML (mark AC-ID COMPLETED)
8. ✓ Commit: git commit -m "AC-{ID}: {description}"
```

### Test Template

```python
"""Tests for {module_name}
AC-IDs: {AC-ID-1}, {AC-ID-2}
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""
import pytest
from cortex.{module_path} import {ClassName}

class Test{ClassName}:
    """Tests for {ClassName} - Implements {AC-ID}"""
    
    @pytest.fixture
    def instance(self) -> {ClassName}:
        return {ClassName}()
    
    def test_ac_id_requirement(self, instance: {ClassName}) -> None:
        """Test AC-ID: {AC-ID}"""
        # Arrange
        # Act
        # Assert
```

### Implementation Template

```python
"""Module: {name}
AC-ID: {ac_id}
Purpose: {description}
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""
from typing import Optional
from cortex.core.result import Result, Ok, Err

class {ClassName}:
    """
    {Description}
    
    Implements: {AC-ID}
    Requires: {dependencies}
    """
    
    def method(self, param: str) -> Result[str]:
        """
        {Method description}
        
        Args:
            param: {Description}
            
        Returns:
            Result[str]: Success with value or Err on failure
        """
        try:
            # Implementation
            return Ok(result)
        except ValueError as e:
            return Err(f"Invalid: {e}")
        except Exception as e:  # CORE-013: Never bare except
            return Err(f"Error: {e}")
```

---

## Directory Structure (Canonical)

### Source Code
```
cortex/
├── api/                              # REST + health checks
│   └── external_service_client.py   # ⚠️ CRITICAL: needs timeout
├── brain/core/
│   ├── governance_registry.py       # TIER 0 enforcement
│   ├── state_manager.py             # State persistence
│   └── knowledge_repository.py      # Pattern database
├── core/
│   ├── result.py                    # Result<T> monad
│   ├── orchestrator_base.py         # ⚠️ CRITICAL: needs lock
│   └── utilities.py
├── infrastructure/
│   ├── enhanced_audit_logger.py     # Structured logging
│   ├── database.py                  # DB manager
│   ├── circuit_breaker.py           # Fault tolerance
│   └── connection_pool.py           # Connection mgmt
├── intent_router/
│   ├── classifier.py                # IntentClassifier (✅ 128/128)
│   ├── routing_engine.py            # Routing logic
│   └── disambiguator.py             # Ambiguity resolution
├── mcp/
│   ├── registry.py                  # ToolRegistry (14 tools)
│   └── tools/{governance,orchestration,knowledge,utility}/
├── orchestrators/
│   ├── core/master_orchestrator.py  # ⚠️ CRITICAL: SPOF fix needed
│   ├── domain/
│   └── registry/
└── tools/
    ├── cortex_brain_integration.py  # ⚠️ CRITICAL: bare except
    └── toolkit.py                   # ⚠️ CRITICAL: global state
```

### Governance & State
```
cortex_brain/
├── tier0/governance/core-rules.yaml # 29 SKULL rules (immutable)
├── tier1/                           # Domain-specific rules
├── tier2/hallucination_prevention/  # Safety rules
└── state/governance.db              # Audit database
```

### Tests
```
tests/
├── unit/
│   ├── intent_router/               # 128 tests ✅
│   ├── governance/                  # 368 tests ✅
│   ├── orchestrators/               # 412 tests ⏳
│   └── infrastructure/              # 472 tests ✅
├── integration/
└── e2e/
```

---

## Critical Remediation Path (IMMEDIATE)

### Phase 1: COMPLETED ✅
- **REM-CRIT-001:** Race conditions (core/orchestrator_base.py:36-45) — Threading.Lock() + atomic state
- **REM-CRIT-002:** No timeout on external API calls — 30s timeout + exponential backoff + circuit breaker

### Phase 2: COMPLETED ✅
- **REM-HIGH-001:** MasterOrchestrator SPOF — Backup + failover
- **REM-HIGH-002:** MasterOrchestrator SRP violation — Split into handlers

### Phase 3: PENDING ⏳ (Due 2026-02-22)
- **REM-CRIT-003:** Bare except clauses (5 instances) — Remove, use specific exceptions
- **REM-CRIT-004:** Module-level mutable global state (18 files) — Use thread-local storage
- **Domain Brain:** Synthesis module completion
- **Logging:** Add structured logging to 443 critical paths

---

## Communication Style (CORE-REM-003-01)

### Word Targets
- **Standard:** 200-400 words (Maximum: 500)
- **Technical:** ≤800 words
- **Analysis:** ≤600 words

### Prohibited (Never Use)
❌ "Let me analyze..."  
❌ "I will implement..."  
❌ Filler: "just", "actually", "basically", "apparently"  
❌ Apologetic: "Sorry, but..."  
❌ Hedging: "might", "could potentially"

### Preferred (Always Use)
✅ Imperative: "Implement X", "Execute Y", "Validate Z"  
✅ Direct: "This violates CORE-013"  
✅ Citations: "Per CORE-008, tests precede implementation"  
✅ Action-oriented: "Configure timeout at api/external_service_client.py:line"

---

## Operational Commands

```bash
# Test Collection (expect 7540+)
pytest tests/ --co -q | wc -l

# Component Tests
pytest tests/unit/intent_router/ -v          # 128/128 ✅
pytest tests/unit/governance/ -v             # 348/368 ✅
pytest tests/unit/orchestrators/ -v          # 412/613 ⏳
pytest tests/unit/infrastructure/ -v         # 472/472 ✅

# Coverage
pytest --cov=cortex --cov-report=html

# Governance Validation
python -m cortex.brain.core.governance_registry --validate

# MCP Server
python -m cortex.mcp.server

# Full Test Suite
pytest tests/ -v --tb=short | tee test-results.log
```

---

## Do's & Don'ts Summary

### ✅ DO
- Type hint ALL functions (params + returns)
- Include Google-style docstrings
- Use `Result<T>` pattern
- **Write tests FIRST (CORE-008)**
- Cite TIER 0 rules
- Include response header on EVERY interaction
- Mark AC-IDs in commits
- Use specific exceptions (CORE-013)
- Validate governance before executing

### ❌ DON'T
- Create `.py` files in workspace root
- Hardcode paths (CORE-005)
- Skip response headers (CORE-029)
- Skip type hints on public APIs (CORE-011)
- Use bare `except:` (CORE-013 — BLOCKS DEPLOYMENT)
- Create `.md` outside `docs/` (except roadmap)
- Skip AC-ID in commits
- Use conversational filler
- Create summary files

---

## Phase Tracker (Current)

| Track | Status | Phase | Progress |
|-------|--------|-------|----------|
| **Mac** | ⏳ IN-PROGRESS | Phase 3 (Architecture) | 1-2 DONE ✅ |
| **Win** | ✅ COMPLETE | All phases | Ready |

**Production Milestone:** 2026-02-22 (Phases 1-3 complete)

---

## Key References

| Document | Purpose | Path |
|----------|---------|------|
| **Master Prompt** | System prompt + complete reference | `.github/prompts/CORTEX.prompt.md` |
| **This Guide** | Practical workflow reference | `.github/copilot-instruction.md` |
| **Implementation Map** | SSOT for phases & AC-IDs | `_workspaces/roadmap/cortex-impl-map.yaml` |
| **Governance Rules** | 29 SKULL rules | `cortex_brain/tier0/governance/core-rules.yaml` |
| **Phase Specs** | AC requirements & dependencies | `_workspaces/roadmap/phases/*.yaml` |

---

**Last Updated:** 2026-01-23 | **Status:** Production hardening | **Alignment:** ✅ Unified with CORTEX.prompt.md
