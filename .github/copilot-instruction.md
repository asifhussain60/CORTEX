# CORTEX 7.0 Implementation Instructions (Updated 2026-01-19)# CORTEX 7.0 Implementation Instructions (Updated 2026-01-19)



## Project Overview## Project Overview



You are working on **CORTEX 7.0**, a governance-first audit system with 3-tier architecture and full AC-ID driven development. The system is currently at **72.5% completion** (74 of 102 ACs locked, 331 tests passing).You are working on **CORTEX 7.0**, a governance-first audit system with 3-tier architecture and full AC-ID driven development. The system is currently at **72.5% completion** (74 of 102 ACs locked, 331 tests passing).



## Current Status## Current Status



| Metric | Value || Metric | Value |

|--------|-------||--------|-------|

| **Overall Completion** | 72.5% (74/102 ACs complete) || **Overall Completion** | 72.5% (74/102 ACs complete) |

| **Locked Phases** | 6 (PHASE-01 through PHASE-04, PHASE-21, PHASE-22) || **Locked Phases** | 6 (PHASE-01 through PHASE-04, PHASE-21, PHASE-22) |

| **Total Tests Passing** | 331 / 331 (100%) || **Total Tests Passing** | 331 / 331 (100%) |

| **Code Coverage** | 95%+ (CORE modules) || **Code Coverage** | 95%+ (CORE modules) |

| **Governance Rules** | 29/29 CORE rules implemented ✅ || **Governance Rules** | 29/29 CORE rules implemented |

| **Audit Trail Status** | VERIFIED ✅ (5040 entries, unbroken hash chain) || **Audit Trail Status** | VERIFIED ✅ (5040 entries, unbroken hash chain) |

| **Production Ready** | 257 ACs with complete audit lifecycle || **Production Ready** | 257 ACs with complete audit lifecycle |



## Architecture Summary## Architecture Summary



``````

CORTEX 7.0: Governance-First AI Development PlatformCORTEX 7.0: Governance-First AI Development Platform

├── Tier 0: Immutable SKULL Rules (29 rules)├── Tier 0: Immutable SKULL Rules (29 rules)

│   └── cortex/core/governance/core-rules.yaml│   └── cortex/core/governance/core-rules.yaml

│   └── Includes: lifecycle, response formatting, portability, quality gates│   └── Includes: lifecycle, response formatting, portability, quality gates

├── Tier 1: Project Governance (YAML + SQLite)├── Tier 1: Project Governance (YAML + SQLite)

│   ├── cortex_brain/tier1/ (domain-specific rules)│   ├── cortex_brain/tier1/ (domain-specific rules)

│   └── Includes: enforcement maps, validation checklists│   └── Includes: enforcement maps, validation checklists

└── Tier 2: Engineering Standards└── Tier 2: Engineering Standards

    ├── cortex_brain/tier2/ (domain implementations)    ├── cortex_brain/tier2/ (domain implementations)

    └── Includes: domain brains, governance evaluation frameworks    └── Includes: domain brains, governance evaluation frameworks

``````



## Key Implementation Principles## Key Implementation Principles



### 1. Audit-First Pattern### 1. Audit-First Pattern

Every operation MUST follow:Every operation MUST follow:

``````

AC_START (log intent) → EXECUTE → AC_COMPLETE (log result) → Verify hash chainAC_START (log intent) → EXECUTE → AC_COMPLETE (log result) → Verify hash chain

``````



### 2. AC-ID Driven Development### 2. AC-ID Driven Development

- **Format:** `AC-{CATEGORY}-{NNN}` or `AC-{CATEGORY}-{NNN}-{NN}`- **Format:** `AC-{CATEGORY}-{NNN}` or `AC-{CATEGORY}-{NNN}-{NN}`

- **Categories:** AR, FR, NFR, VALIDATE, METRICS, COHERENCE, EXPLAIN, BRITTLE, ENHANCE, REM, OB, DOM, MCP- **Categories:** 

- Every change tied to exactly ONE AC-ID  - AR (Architecture), FR (Functional), NFR (Non-Functional)

- No orphaned code commits  - VALIDATE, METRICS, COHERENCE, EXPLAIN, BRITTLE

  - ENHANCE (Enhancements), REM (Remediation)

### 3. Response Format Standards (CORE-029 - IMMUTABLE)  - OB (Observability), DOM (Domain), MCP (Protocol)

- Every change tied to exactly ONE AC-ID

**MANDATORY:** All responses MUST include the CORTEX header format:- No orphaned code commits without AC-ID



```markdown### 3. Response Format Standards (CORE-029 - IMMUTABLE)

## 🧠 CORTEX {operation}

**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅**MANDATORY:** All responses MUST include the CORTEX header format:



---```markdown

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**## 🧠 CORTEX {operation}

**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

[Response content here]

```---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

**Automatic Implementation:** ResponseHeaderInjector in orchestrators

[Response content here]

### 4. Governance Rules & Compliance```

- **29 CORE Rules** (Tier 0 - immutable, fully implemented)

- **Loading Sequence:** TIER_0_CORE → TIER_0_DOMAIN → TIER_0_VALIDATION → TIER_1_ENFORCEMENT**Variable Substitution:**

- **Enforcement Mode:** STRICT- `{operation}` - Current task (Code Analysis, Implementation Plan, Governance Evaluation, etc.)

- **Validation Database:** `cortex_brain/state/governance.db` (257 production AC-IDs)- `{phase}` - Current phase (PHASE-XX, PHASE-DOC-REMEDIATION, etc.)

- `{orchestrator}` - Active orchestrator (MasterOrchestrator, PlanningOrchestrator, etc.)

### 5. Test-Driven Development (TDD Pattern)

- Every AC-ID MUST have ≥1 test before implementation**Rule:** CORE-029 (Response Header Injection)

- Tests follow `tests/unit/test_*.py` or `tests/integration/test_*.py`- Located: `cortex/core/governance/core-rules.yaml` (lines 500-620)

- Minimum coverage per AC: 80%- Status: IMMUTABLE (Tier 0)

- Enforcement: Automatic via `ResponseHeaderInjector` in orchestrators

## Directory Organization- Validation: Pre-response check in `get_response_with_headers()` methods



### Source Code### 4. Governance Rules & Compliance

```- **29 CORE Rules** (Tier 0 - immutable)

src/- **Loading Sequence:** TIER_0_CORE → TIER_0_DOMAIN → TIER_0_VALIDATION → TIER_1_ENFORCEMENT

├── core/                          # Core business logic- **Enforcement Mode:** STRICT

│   ├── governance_registry.py    # Governance rules registry- **Validation Database:** `cortex_brain/state/governance.db` (257 production AC-IDs)

│   ├── result.py                 # Result<T> pattern

│   ├── response_header_config.py # Header configuration### 5. Test-Driven Development (TDD Pattern)

│   ├── response_header_injector.py # Header injection engine- Every AC-ID MUST have ≥1 test

│   └── interfaces.py             # Core interfaces- Tests follow `tests/unit/test_*.py` or `tests/integration/test_*.py` patterns

├── infrastructure/               # Infrastructure- Governance rule: CORE-008 (TDD Enforcement)

│   ├── audit_logger.py           # Audit trail logging- Minimum coverage: 80%

│   └── database_manager.py       # SQLite operations

├── mcp/                          # MCP Server## Implementation Roadmap Location

│   ├── tools/                    # MCP-exposed tools

│   ├── utilities/                # Helper utilitiesAll implementation details are in YAML format:

│   └── registry.py               # Tool registry```

└── orchestrators/                # Orchestration_workspaces/roadmap/

    ├── core/                     # Core orchestrators├── cortex-master.yaml          # Master plan with all requirements (SSOT)

    ├── domain/                   # Domain orchestrators├── phases/

    ├── response/                 # Response generation│   ├── phase-01.yaml           # Foundation (36 ACs)

    └── deployment/               # Deployment│   ├── phase-02.yaml           # Orchestration Core (27 ACs)

```│   ├── phase-03.yaml           # Safety & Observability (6 ACs)

│   ├── phase-04.yaml           # Production Hardening (12 ACs)

### Governance & Tiers│   ├── phase-05.yaml           # Brittleness Fixes (17 ACs)

```│   └── phase-parallel.yaml     # Folder Migration (3 ACs)

cortex_brain/├── _archives/

├── tier0/                        # Immutable rules (29 SKULL rules)│   └── cortex-master-v1.yaml   # Historical reference (258+ ACs)

├── tier1/                        # Project governance└── reports/                    # Phase completion reports

├── tier2/                        # Engineering standards```

└── state/

    └── governance.db            # Audit database (257 production ACs)## Code Organization

```

```

### Testssrc/

```├── core/                       # Core business logic

tests/│   ├── config.py

├── unit/                         # Unit tests│   ├── interfaces.py

│   └── test_*.py│   ├── result.py

├── integration/                  # Integration tests│   ├── governance_registry.py  # To be created

│   ├── test_orchestrator_header*.py (header injection)│   ├── tier_resolver.py        # To be created

│   ├── test_audit_trail_integrity.py│   └── decorators/             # To be created

│   └── test_*.py├── infrastructure/             # Infrastructure components

└── performance/                  # Performance tests│   ├── audit_logger.py

    └── test_*.py│   └── database_manager.py     # To be created

```├── mcp/                        # MCP Server integration

│   ├── decorator.py

### Roadmap & Documentation│   └── registry.py

```├── orchestrators/              # Orchestration layer

_workspaces/roadmap/│   ├── core/

├── cortex-master.yaml           # SSOT: Master plan (updated 2026-01-19)│   ├── domain/

├── phases/                      # Phase specifications│   └── custom/

│   ├── phase-01.yaml through phase-25.yaml└── tools/

│   ├── phase-remediation-11.yaml    └── toolkit.py

│   └── phase-deployment-enhanced.yaml```

└── reports/                     # Completion reports & dashboards

    ├── PHASE-XX-COMPLETION-REPORT.md## Testing Standards

    ├── LEADERSHIP-DASHBOARD.md

    └── INDEX.md- All tests in `tests/` directory

```- Unit tests: `tests/unit/test_*.py`

- Integration tests: `tests/integration/test_*.py`

## Critical Governance Rules (Quick Reference)- Performance tests: `tests/performance/test_*.py`

- Each AC-ID should have corresponding test(s)

| Rule | Purpose | Enforcement |

|------|---------|-------------|## Performance Targets

| **CORE-001** | Incremental execution (<500 lines/turn) | STRICT |

| **CORE-002/003** | Response formatting (no summary files, visual bars) | STRICT || Operation | Target |

| **CORE-005** | Path portability (no hardcoded paths) | STRICT ||-----------|--------|

| **CORE-008** | TDD enforcement (tests before code) | STRICT || Governance evaluation | <5ms per rule |

| **CORE-011** | Type hints (all functions typed) | STRICT || SQLite query | <1ms |

| **CORE-012** | Docstrings (all classes/functions) | STRICT || State transition | <10ms |

| **CORE-029** | Response headers (CORTEX format) | IMMUTABLE || Evidence capture | <500ms |

| **CORE-REM-003-01** | Verbosity control (<500 words) | STRICT || Audit logging | <5ms |



## File Organization Rules## Quality Targets



### ✅ CORRECT| Metric | Target |

- Python source: `src/`|--------|--------|

- Unit tests: `tests/unit/`| Test pass rate | ≥98% |

- Integration tests: `tests/integration/`| Code coverage | ≥80% |

- MCP tools: `src/mcp/tools/`| Verification rate | ≥80% |

- Tier modules: `cortex_brain/tierX/`

- Documentation: `docs/`## Response Format Standards

- Phase reports: `_workspaces/roadmap/reports/`

### MANDATORY: All CORTEX Responses Must Include Headers (CORE-030)

### ❌ FORBIDDEN

- ❌ Root `.py` filesEvery response generated by CORTEX agents MUST begin with the standard header format. This is a Tier 0 governance requirement (CORE-030 - Immutable).

- ❌ `_workspaces/roadmap/tools/` (use `src/mcp/tools/`)

- ❌ `docs_md/` folder (use `docs/`)**NO EXCEPTIONS. NO VARIATIONS. This is enforceable.**

- ❌ `.github/` for source code

- ❌ Summary/report `.md` files outside designated dirs### Standard Response Format (Exact Pattern Required)



## Implementation Workflow```

## 🧠 CORTEX {operation}

### When Starting a New AC-ID**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅



1. **Read AC-ID** from `_workspaces/roadmap/phases/phase-NN.yaml`---

2. **Check dependencies** - Read `requires` field**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

3. **Create test file FIRST** (TDD pattern)

4. **Write failing tests** (RED phase)[Response content here]

5. **Implement feature** (GREEN phase)```

6. **Add type hints** - CORE-011 compliance

7. **Add docstrings** - CORE-012 compliance### Header Validation (CORE-030 Enforcement)

8. **Verify audit trail** - check `governance.db`

9. **Update phase YAML** - mark AC as COMPLETEDEvery response is validated before return:

10. **Document evidence** - git diff, test output- ✅ Header present on line 1

- ✅ Format matches exactly (emoji, bold, separator, copyright)

### Test File Template- ✅ Operation type from allowed list

- ✅ Phase format matches PHASE-NN

```python- ✅ Orchestrator matches active orchestrator

"""- ❌ Missing any element → Response rejected (BLOCKED)

Tests for {module_name}

AC-IDs tested: {AC-ID-1}, {AC-ID-2}### Governance Reference

"""

- **Rule:** CORE-030 (Mandatory CORTEX Response Headers)

import pytest- **Source:** `cortex_brain/tier0/governance/core-rules.yaml` (lines 630-720)

from src.{module_path} import {ClassName}- **Validator:** `src.core.response_header_injector.ResponseHeaderValidator`

- **Loading:** Enforced at governance startup + pre-response validation

@pytest.mark.ac("{AC-ID}")

class Test{ClassName}:### Variable Substitution

    """Tests for {ClassName} - Implements {AC-ID}"""

    | Variable | Description | Example Values |

    def test_basic_functionality(self):|----------|-------------|----------------|

        """Test AC-ID: {AC-ID}"""| `{operation}` | What you're doing | "Code Analysis", "Implementation", "Governance Evaluation" |

        # Arrange| `{phase}` | Current roadmap phase | "PHASE-13", "PHASE-DOC-REMEDIATION" |

        # Act  | `{orchestrator}` | Active orchestrator | "MasterOrchestrator", "PlanningOrchestrator" |

        # Assert

        pass### Response Examples

```

**Example 1: Implementing an AC-ID**

### Source Module Template```

## 🧠 CORTEX AC Execution

```python**Author:** Asif Hussain | **Phase:** PHASE-13 | **Orchestrator:** MasterOrchestrator ✅

"""

Module: {module_name}---

AC-ID: {ac_id}**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

Purpose: {description}

"""### Implementing OB-001-01



from typing import TYPE_CHECKINGCreating OpenTelemetry integration module...

if TYPE_CHECKING:```

    from typing import Optional

**Example 2: Code Review**

class {ClassName}:```

    """## 🧠 CORTEX Code Review

    {Description}**Author:** Asif Hussain | **Phase:** PHASE-DOC-REMEDIATION | **Orchestrator:** PlanningOrchestrator ✅

    

    Implements: {AC-ID}---

    """**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

    

    def authenticate(self, request: Request) -> Result[Token]:### Review Results

        """

        Authenticate request.The code follows governance rules CORE-011 and CORE-012...

        ```

        Implements: AC-AR-005-02

        ### Configuration Source

        Args:

            request: HTTP requestHeaders are configured in: `cortex_brain/tier0/response-headers.yaml`

        

        Returns:```yaml

            Result[Token]: Success or error# Key values (DO NOT modify without governance approval):

        """author:

```  name: "Asif Hussain"

copyright:

## Performance & Quality Targets  notice: "Copyright © 2025-2026 Asif Hussain. All rights reserved."

```

| Metric | Target | Current |

|--------|--------|---------|### Rules

| Test pass rate | ≥98% | ✅ 100% (331/331) |

| Code coverage | ≥80% | ✅ 95%+ (CORE) |1. **Always include header** - Every response starts with the 🧠 CORTEX header

| Governance evaluation | <5ms/rule | ✅ Met |2. **Use correct phase** - Reference the current phase from cortex-master.yaml

| Response generation | <200ms | ✅ Met |3. **Enforce verbosity limits** - All responses <500 words (CORE-REM-003-01)

| Type hint coverage | ≥90% | ✅ Met |4. **Direct communication style** - No "Let me", "I will", conversational filler

| Docstring coverage | ≥90% | ✅ Met |5. **Copyright on every response** - "Copyright © 2025-2026 Asif Hussain"



## Command Reference### MANDATORY: Verbosity Control & Communication Style (AC-REM-003-01)



```bashAll CORTEX responses MUST follow strict verbosity guidelines:

# Run all tests

pytest#### Word Count Limits

- **Maximum:** <500 words per response

# Run specific test file- **Target:** 200-400 words (concise, focused)

pytest tests/unit/test_orchestrator.py -v- **Exception:** Detailed technical specifications (≤800 words with context)



# Run with coverage#### Communication Style Requirements

pytest --cov=src --cov-report=html- **Avoid:** Phrases like "Let me", "I will", "Let's", "I think", "I believe", "just"

- **Use:** Direct, imperative phrasing: "Implement", "Deploy", "Execute", "Complete"

# Run integration tests- **Voice:** Professional, technical, CORTEX-aligned (never casual/conversational)

pytest tests/integration/ -v- **Tone:** Confident, authoritative, governance-backed statements



# Check specific AC-ID#### Prohibited Patterns

pytest -k "ac-ar-005-02" -v❌ "Let me analyze this for you"  

❌ "I will implement the following"  

# Validate governance❌ "I believe the best approach is"  

python -m src.core.governance_registry --validate❌ Filler: "just", "actually", "apparently", "basically"  

❌ Over-explanation of basic concepts

# Generate audit report

python -m src.infrastructure.audit_logger --phase PHASE-15#### Preferred Patterns  

✅ "Analyze the following"  

# Check path portability✅ "Implement these components"  

python scripts/validate_paths.py src/✅ "This follows CORE-019 governance"  

```✅ Brief, specific, actionable language



## Response Header Implementation (PHASES 01-04 LOCKED ✅)#### Verification Checklist

- [ ] Response <500 words

- **PlanningOrchestrator:** ✅ Integrated (AC-ENH-001-01, AC-ENH-001-02)- [ ] No "Let me" / "I will" phrases

- **MasterOrchestrator:** ✅ Integrated (AC-ENH-002-01, AC-ENH-002-02)- [ ] Uses imperative voice

- **Header Consistency:** ✅ Verified (AC-ENH-003-01)- [ ] Includes copyright notice

- **Test Coverage:** ✅ 331 tests passing (100%)- [ ] Response header present

- **Graceful Degradation:** ✅ Implemented- [ ] Links governance rules when relevant

3. **Bold copyright** - Copyright line must be bold (`**...**`)

## Critical File References4. **Separator required** - `---` between header/author line and copyright

5. **No footer needed** - Footer is disabled by default

| Document | Purpose | Location |

|----------|---------|----------|## Implementation Workflow

| **Master Roadmap** | SSOT for all phases | `_workspaces/roadmap/cortex-master.yaml` |

| **Governance Rules** | All 29 CORE rules | `cortex/core/governance/core-rules.yaml` |When implementing any feature:

| **Phase Enforcement** | Rules per phase | `cortex/core/governance/phase-enforcement-map.yaml` |

| **AC Validation** | Completion criteria | `cortex/core/governance/ac-validation-checklist.yaml` |1. **Read the AC-ID** from the phase YAML file

| **Phase Specs** | AC requirements | `_workspaces/roadmap/phases/phase-{NN}.yaml` |2. **Check dependencies** are completed

| **Audit Database** | Evidence trails | `cortex_brain/state/governance.db` |3. **Create/modify files** as specified

| **Builder Prompt** | Implementation guide | `.github/prompts/cortex-builder.prompt.md` |4. **Write tests** that verify acceptance criteria

| **Git Protocol** | Multi-machine dev | `.github/prompts/cortex-git-commit.prompt.md` |5. **Run tests** to verify implementation

6. **Update status** in the phase YAML file

## Current Phase Context7. **Generate evidence** bundle



**Completed & Locked:**## File Creation Patterns

- PHASE-01 through PHASE-04 (Foundation): 80 ACs ✅

- PHASE-21 (Intelligent Knowledge): 15 ACs ✅### New Python Module

- PHASE-22 (Response Composition): 10 ACs ✅```python

"""

**Next:** PHASE-23-COMPLEXITY-AWARE-CONFIRMATION (4 ACs)Module: {module_name}

AC-ID: {ac_id}

## Documentation Maintenance (CRITICAL)Purpose: {description}

"""

After completing a phase:

from typing import TYPE_CHECKING

1. Holistically review phase implementation

2. Evaluate `.github/prompts/CORTEX.prompt.md` for updatesif TYPE_CHECKING:

3. Evaluate `.github/copilot-instruction.md` (this file) for updates    # Type imports here

4. Update sections to reflect new capabilities    pass

5. Ensure prompts match actual implementation

6. Document prompt changes

class {ClassName}:

**Enforcement:** Phase cannot be locked until prompt evaluation complete.    """

    {Description}

## Response Header Variable Reference    

    Implements: {AC-ID}

| Variable | Source | Examples |    """

|----------|--------|----------|    

| `{operation}` | Current task | "Code Analysis", "Implementation Plan", "Governance Evaluation" |    def __init__(self):

| `{phase}` | Current phase | "PHASE-23", "PHASE-DOC-REMEDIATION" |        pass

| `{orchestrator}` | Active orchestrator | "MasterOrchestrator", "PlanningOrchestrator" |```



## Common Patterns & Best Practices### New Test File

```python

### ✅ DO"""

- Use `Result<T>` pattern for all operationsTests for {module_name}

- Type hint all function parameters and returnsAC-IDs tested: {list of AC-IDs}

- Include AC-ID in docstrings"""

- Create tests BEFORE implementation

- Use visual progress bars in responsesimport pytest

- Include copyright notice in ALL responses

- Validate governance rules before executionfrom src.{module_path} import {ClassName}



### ❌ DON'T

- Create temporary `.py` files in rootclass Test{ClassName}:

- Use hardcoded absolute paths    """Tests for {ClassName}"""

- Write responses without headers    

- Skip type hints on public APIs    def test_{ac_id_snake_case}(self):

- Create `.md` files outside `docs/`        """Test AC-ID: {AC-ID}"""

- Use conversational filler ("Let me", "I will", "I think")        # Arrange

- Implement without corresponding test        # Act

        # Assert

## Response Style Guidelines (CORE-REM-003-01)        pass

```

**Word Count:** <500 words (target: 200-400)

## Common Commands

**Communication Style:**

- ✅ Direct, imperative: "Implement", "Deploy", "Execute"```bash

- ✅ Professional, technical, governance-backed# Run all tests

- ❌ Avoid: "Let me", "I will", "I believe", "just", "actually"pytest



**Verification Checklist:**# Run specific test file

- [ ] Response <500 wordspytest tests/unit/test_governance_registry.py

- [ ] No "Let me" / "I will" phrases

- [ ] Imperative voice throughout# Run with coverage

- [ ] Copyright notice presentpytest --cov=src --cov-report=html

- [ ] Response header present

- [ ] Governance rules cited when relevant# Check test collection

pytest --co -q

## Support & Escalation```



- **Governance Q:** Check `cortex/core/governance/core-rules.yaml`## Current Status

- **Path Issues:** Use `src.core.path_resolver` functions

- **Test Failures:** Check `tests/integration/test_audit_trail_integrity.py`Check `_workspaces/roadmap/cortex-master.yaml` for:

- **Headers:** Check orchestrator integration tests- `phase_tracker` section - Current implementation phase and status

- **Audit Trail:** Query `cortex_brain/state/governance.db`- `metadata.completion_percentage` - Overall progress

- `phase_tracker.PHASE-XX.locked` - Whether phase is complete

---

## Important Files to Reference

**Last Updated:** 2026-01-19  

**Version:** v2.1 (Updated for phases 21-22 completion + latest roadmap)  1. **Master Plan**: `_workspaces/roadmap/cortex-master.yaml` (SSOT - Single Source of Truth)

**Status:** ✅ Current & Compliant2. **Phase Specifications**: `_workspaces/roadmap/phases/phase-NN.yaml` (detailed AC specs)

3. **Governance Rules**: `cortex_brain/tier0/governance/core-rules.yaml` (Tier 0 immutable)
4. **Phase Enforcement**: `cortex_brain/tier0/governance/phase-enforcement-map.yaml`
5. **Builder Prompt**: `.github/prompts/cortex-builder.prompt.md`
6. **Git Commit Protocol**: `.github/prompts/cortex-git-commit.prompt.md`
7. **Builder Agent**: `.github/agents/cortex-builder.md`
8. **Planner Agent**: `.github/agents/cortex-planner.md`

## Current Phase Context (2026-01-15)

**Current Phase:** PHASE-13-OBSERVABILITY-MATURITY  
**Status:** NOT_STARTED (Ready to begin)

| Phase | Title | ACs | Status | Locked |
|-------|-------|-----|--------|--------|
| 12 | Knowledge Ecosystem | 7 | COMPLETED | ✅ |
| **13** | **Observability & Telemetry** | **5** | **NOT_STARTED** | ❌ |
| 14 | Production Migration | 4 | NOT_STARTED | ❌ |

**PHASE-13 Details:**
- **AC-IDs:** OB-001-01, OB-001-02, OB-002-01, OB-002-02, OB-003-01
- **Governance Rules:** CORE-008 (TDD), CORE-011 (types), CORE-012 (docs), CORE-024 (obs logs)
- **Estimated:** 20 hours (2.5 days)
- **Requires:** PHASE-10-ADAPTIVE-EXECUTION (locked ✅)
- **Command:** Check status with: `grep "PHASE-13" .github/roadmap/cortex-master.yaml`
