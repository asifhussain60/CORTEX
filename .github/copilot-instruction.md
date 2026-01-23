# CORTEX Master Orchestrator: Unified Implementation Guide
**Version:** 5.0 | **Updated:** 2026-01-23 | **Authority:** cortex-impl-map.yaml v3.9 + cortex-total-recall.prompt.md v2.0  
**Single Entry Point:** Use this with cortex-total-recall.prompt.md for complete context

---

## ⚡ Quick Start: Use cortex-total-recall.prompt.md First

This file is a **companion reference**. For complete context, start with:

**Primary:** `.github/prompts/cortex-total-recall.prompt.md` (v2.0 — Production Ready Functionality Reference)  
**Companion:** `.github/copilot-instruction.md` (this file — Practical workflow guide)  
**System Prompt:** `.github/prompts/CORTEX.prompt.md` (v6.0 — Master Orchestrator System Prompt)

All three files are **unified and synchronized** for seamless master orchestrator operation.

---

## Project Identity

**CORTEX** — Governance-first AI development platform with 4-tier brain architecture, intelligence layer, todo manager, knowledge composition engine, and multi-domain orchestration.

### Current Operational Status (2026-01-23)

| Component | Status | Notes |
|-----------|--------|-------|
| **Intent Router** | ✅ 100% READY | 128/128 tests, production-ready, LENS protocol active |
| **Governance Engine** | ✅ 95% READY | 29 TIER 0 rules + 4-tier brain architecture (127 total rules) |
| **Brain Tier Architecture** | ✅ 100% ACTIVE | Tier 0-3 composition with intelligence layer |
| **Infrastructure** | ✅ 100% READY | Circuit breaker, resilience, fault tolerance verified |
| **MasterOrchestrator** | ✅ 67% READY | 4-stage pipeline with intelligence layer wired |
| **Intelligence Layer** | ✅ 100% ACTIVE | Governance + Duration + Error + Routing intelligence |
| **Knowledge Composer** | ✅ 100% ACTIVE | YAML composition + domain overlay operational |
| **Todo Manager** | ✅ 100% ACTIVE | Phase tracking, rollback, governance validation |
| **Domain Brain** | ✅ 100% ACTIVE | 5 domain orchestrators operational |
| **Multi-Repo Governance** | ✅ 100% ACTIVE | CORE-020 enforcement with sync strategies |
| **MCP Tools** | ✅ 100% REGISTERED | 15 tools active (governance, orchestration, knowledge, utility) |
| **Conversation Protocol** | ✅ 100% ACTIVE | Multi-turn orchestration with token tracking |

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

## Brain Tier Architecture (4-Tier Governance Hierarchy)

**Tier Structure:** SKULL → SPINE → ORGANS → FUNCTIONS

| Tier | Location | Purpose | Rule Count | Override |
|------|----------|---------|------------|----------|
| **Tier 0 (SKULL)** | `cortex_brain/tier0/governance/core-rules.yaml` | Immutable core rules (CORTEX operational boundaries) | 29 | NEVER |
| **Tier 1 (SPINE)** | `cortex_brain/tier1/governance/*.yaml` | Domain-specific rules (security, operations, development, data, compliance) | 47 | By Tier 0 only |
| **Tier 2 (ORGANS)** | `cortex_brain/tier2/governance/*.yaml` | Context-aware rules (production, sensitive-data, high-risk-ops, audit-critical) | 38 | By Tier 0-1 |
| **Tier 3 (FUNCTIONS)** | `cortex_brain/tier3/knowledge/*.yaml` | Knowledge governance, domain registry, business profiles | 13 | By Tier 0-2 |

### Intelligence Layer Components

| Component | Purpose | Entry Point |
|-----------|---------|-------------|
| **GovernanceIntelligence** | Context analysis, rule selection, tier composition | `cortex.brain.core.governance_intelligence.GovernanceIntelligence` |
| **KnowledgeComposer** | YAML composition, domain overlay, prompt generation | `cortex.brain.core.knowledge_composer.KnowledgeComposer` |
| **TierComposer** | Multi-tier rule merging with precedence enforcement | `cortex.brain.core.tier_composer.TierComposer` |
| **DomainOverlay** | Business domain + CORTEX practice integration | `cortex.brain.core.domain_overlay.DomainOverlay` |
| **TodoManager** | Phase tracking, progress monitoring, rollback | `cortex.orchestrators.tools.todo_manager.TodoManager` |

### Governance Rule Composition

```python
from cortex.brain.core.tier_composer import TierComposer

# Compose applicable rules from all tiers
applicable_rules = TierComposer().compose_rules(
    tier0_rules=True,  # Always included (SKULL)
    tier1_domains=["security", "compliance"],  # SPINE
    tier2_contexts=["production", "sensitive-data"],  # ORGANS
    tier3_profiles=["healthcare-v1.0"]  # FUNCTIONS
)
```

### Knowledge YAML Composition

```python
from cortex.brain.core.knowledge_composer import KnowledgeComposer

# Compose business domain YAMLs with CORTEX best practices
composer = KnowledgeComposer()
composed = composer.compose(
    business_domain="healthcare-v1.0",  # From tier1/profiles/
    cortex_tiers=[0, 1, 2, 3],  # All tier governance
    merge_strategy="tier_priority"  # Tier 0 > Tier 1 > Tier 2 > Tier 3
)
```

### Todo Manager Integration

```python
from cortex.orchestrators.tools.todo_manager import TodoManager

# Create multi-phase operation with governance validation
todo_manager = TodoManager()
task = todo_manager.create_task(
    task_id="IMPL-FEATURE-001",
    phases=[
        {"id": 1, "title": "Design", "dependencies": []},
        {"id": 2, "title": "Implementation", "dependencies": [1]},
        {"id": 3, "title": "Testing", "dependencies": [2]},
        {"id": 4, "title": "Governance Review", "dependencies": [3]}
    ]
)

# Execute with automatic phase tracking and rollback
for phase in task.phases:
    todo_manager.mark_phase(phase.id, "in-progress")
    result = execute_phase(phase)
    if result.success:
        todo_manager.mark_phase(phase.id, "completed")
    else:
        todo_manager.rollback_to_phase(phase.id - 1)
        break
```

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

### Domain Brain Orchestrators

**Architecture:** MasterOrchestrator → DomainOrchestrator → BusinessOrchestrator

| Domain | Entry Point | Capabilities |
|--------|-------------|-------------|
| **FinanceDomain** | `cortex.orchestrators.domains.finance.FinanceDomain` | Financial operations, SOX/GAAP compliance |
| **HRDomain** | `cortex.orchestrators.domains.hr.HRDomain` | Employee management, payroll, benefits |
| **EcommerceDomain** | `cortex.orchestrators.domains.ecommerce.EcommerceDomain` | Product catalog, orders, payments |
| **HealthcareDomain** | `cortex.orchestrators.domains.healthcare.HealthcareDomain` | Patient records, HIPAA compliance |
| **SupportDomain** | `cortex.orchestrators.domains.support.SupportDomain` | Ticket management, SLA tracking |

**Usage:**
```python
from cortex.brain.domain_brain import DomainBrain

# Multi-domain operation with governance overlay
domain_brain = DomainBrain()
result = domain_brain.execute_multi_domain(
    primary_domain="healthcare",
    cross_domain_dependencies=[
        {"domain": "finance", "operation": "generate_invoice"},
        {"domain": "hr", "operation": "assign_specialist"}
    ],
    governance_profiles=["healthcare-v1.0", "finops-v1.0"],
    compliance_requirements=["HIPAA", "SOX"]
)
```

### Multi-Repo Governance (CORE-020)

```python
from cortex.governance.multi_repo import MultiRepoGovernance

# Sync governance rules across repositories
multi_repo = MultiRepoGovernance()
multi_repo.sync_all_repos(
    primary_repo="cortex-main",
    sync_tiers=[0, 1, 2],  # Sync Tier 0-2 rules
    conflict_resolution="primary_wins"  # cortex-main is source of truth
)
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
# STEP 0: Git Sync with Domain Knowledge Protection (ALWAYS FIRST)
BACKUP_DIR="_backups/pre-sync-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r cortex_brain/tier{1,2,3} "$BACKUP_DIR/" 2>/dev/null || true
git add -A
git stash push --include-untracked -m "Pre-deployment-$(date +%Y%m%d_%H%M%S)"
git pull origin main --no-rebase --strategy-option=ours
git stash pop

# Protect domain YAMLs on conflicts (keep LOCAL version)
for file in cortex_brain/tier{1,2,3}/**/*.yaml; do
    if git status | grep -q "$file"; then
        git checkout --ours "$file"
        git add "$file"
    fi
done

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
| **Total Recall Prompt** | Production ready functionality reference | `.github/prompts/cortex-total-recall.prompt.md` |
| **Master Prompt** | System prompt + complete reference | `.github/prompts/CORTEX.prompt.md` |
| **This Guide** | Practical workflow reference | `.github/copilot-instruction.md` |
| **Implementation Map** | SSOT for phases & AC-IDs | `_workspaces/roadmap/cortex-impl-map.yaml` |
| **TIER 0 Governance** | 29 SKULL rules (immutable) | `cortex_brain/tier0/governance/core-rules.yaml` |
| **TIER 1 Governance** | 47 domain-specific rules | `cortex_brain/tier1/governance/*.yaml` |
| **TIER 2 Governance** | 38 context-aware rules | `cortex_brain/tier2/governance/*.yaml` |
| **TIER 3 Knowledge** | 13 knowledge governance + 6 domain profiles | `cortex_brain/tier3/knowledge/*.yaml` |
| **Phase Specs** | AC requirements & dependencies | `_workspaces/roadmap/phases/*.yaml` |

---

**Last Updated:** 2026-01-23 | **Status:** ✅ Production Ready | **Alignment:** ✅ Unified with cortex-total-recall.prompt.md v2.0 + CORTEX.prompt.md v6.0

**Production Enhancements (v5.0):**
- ✅ Brain Tier Architecture (Tier 0-3) with 127 total governance rules
- ✅ Intelligence Layer (GovernanceIntelligence, KnowledgeComposer, TierComposer, DomainOverlay)
- ✅ Todo Manager integration for phase tracking and rollback
- ✅ Knowledge YAML Composition Engine with domain overlay
- ✅ Multi-Repo Governance (CORE-020) with sync strategies
- ✅ Domain Brain Orchestrators (5 business domains)
- ✅ Conversation Protocol (multi-turn orchestration)
- ✅ Enhanced Git Sync (domain knowledge protection)
- ✅ 15 MCP Tools registered and operational
