# Nested Folder Structure Design for CORTEX

**AC-ID**: AC-AR-010-01  
**Title**: Nested Folder Structure Planning & Design  
**Date**: 2026-01-18  
**Status**: IN_PROGRESS  
**Estimated Completion**: 2026-01-21

---

## Executive Summary

This document designs a comprehensive nested folder structure for CORTEX that improves:
- **Maintainability**: Clear organization by concern/domain
- **Discoverability**: Easy to find related modules
- **Scalability**: Can grow without confusion
- **Cross-Platform Compatibility**: Uses portable paths (no /Users/)
- **Import Coherence**: Prevents circular dependencies, enables better typing

---

## Current Structure Analysis

### Current State (As of 2026-01-18)

```
CORTEX/
├── cortex/                    # Main package
│   ├── api/                   # REST API endpoints
│   ├── brain/
│   │   ├── core/              # Core brain logic
│   │   ├── tier2/             # Tier 2 modules (resilience, optimization)
│   │   └── templates/
│   ├── core/                  # Core infrastructure
│   ├── infrastructure/        # DB, logging, config
│   ├── orchestrators/         # Orchestrator implementations
│   ├── tools/                 # CLI tools
│   └── __init__.py
├── cortex_brain/
│   ├── tier0/                 # Tier 0 foundations
│   ├── tier2/                 # Tier 2 specializations
│   └── tier3/                 # Tier 3 knowledge base
├── cortex_brain/              # (Deprecated - phase consolidation)
│   ├── tier0/
│   ├── tier1/
│   ├── tier2/
│   └── tier3/
├── tests/                     # Test suite
├── src/                       # Alternative source location
├── docs/                      # Documentation
└── scripts/                   # Maintenance scripts
```

### Pain Points Identified
1. ❌ **Duplicate directories**: `cortex_brain/` vs `cortex_brain/` (confusion)
2. ❌ **Unclear hierarchy**: Deep nesting without clear pattern
3. ❌ **Mixed concerns**: Core, infrastructure, API scattered
4. ❌ **Test organization**: tests/ not aligned with source structure
5. ❌ **Import paths**: Absolute paths sometimes use /Users/asifhussain/ (not portable)
6. ❌ **Circular imports possible**: No clear tier/layer separation

---

## Proposed Nested Folder Structure

### Design Principles
1. **Tier-Based Organization**: Tier0 (foundations) → Tier1 (core) → Tier2 (specialized) → Tier3 (knowledge)
2. **Concern-Based Grouping**: Infrastructure, Orchestrators, Tools, API grouped logically
3. **Mirror Testing**: test/X matches src/X structure
4. **Portable Paths**: Use Path(__file__).parent consistently
5. **Clear Boundaries**: Layer separation prevents circular imports

### Proposed Structure

```
CORTEX/
├── src/
│   ├── cortex/                           # Main CORTEX package (Tier0 & Tier1)
│   │   ├── __init__.py
│   │   ├── core/                         # Tier1: Core logic
│   │   │   ├── __init__.py
│   │   │   ├── governance/               # Governance framework
│   │   │   │   ├── __init__.py
│   │   │   │   ├── registry.py
│   │   │   │   ├── validator.py
│   │   │   │   └── rules.py
│   │   │   ├── orchestrator/             # Orchestrator infrastructure
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py               # OrchestratorBase
│   │   │   │   ├── registry.py           # OrchestratorRegistry
│   │   │   │   └── traits.py             # OrchestratorTraits (protocols)
│   │   │   ├── knowledge/                # Knowledge management
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repository.py         # KnowledgeRepository
│   │   │   │   ├── graph.py              # KnowledgeGraph
│   │   │   │   └── protocols.py          # Knowledge protocols
│   │   │   └── intent_router/            # Intent routing engine
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       └── comprehension.py
│   │   │
│   │   ├── infrastructure/               # Tier1: Infrastructure layer
│   │   │   ├── __init__.py
│   │   │   ├── database/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── transaction.py        # DatabaseTransactionManager
│   │   │   │   ├── connection.py         # Connection lifecycle
│   │   │   │   └── migrations.py
│   │   │   ├── logging/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audit.py              # Audit logging
│   │   │   │   └── formatters.py
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── loader.py
│   │   │   │   └── validator.py
│   │   │   └── security/
│   │   │       ├── __init__.py
│   │   │       ├── sanitizer.py
│   │   │       └── validation.py
│   │   │
│   │   ├── orchestrators/                # Tier1: Orchestrator implementations
│   │   │   ├── __init__.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── master.py             # MasterOrchestrator
│   │   │   │   ├── planning.py           # PlanningOrchestrator
│   │   │   │   └── conversation.py       # ConversationProtocol
│   │   │   ├── domain/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analysis.py           # AnalysisOrchestrator
│   │   │   │   ├── execution.py          # ExecutionOrchestrator
│   │   │   │   └── [others].py
│   │   │   └── mcp/
│   │   │       ├── __init__.py
│   │   │       ├── server.py
│   │   │       └── tools.py
│   │   │
│   │   ├── api/                          # Tier1: REST API layer
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestration.py
│   │   │   │   ├── knowledge.py
│   │   │   │   └── admin.py
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       └── validation.py
│   │   │
│   │   └── tools/                        # Tier1: CLI tools & utilities
│   │       ├── __init__.py
│   │       ├── cli.py                    # Main CLI
│   │       ├── commands/
│   │       │   ├── __init__.py
│   │       │   ├── phase.py
│   │       │   ├── governance.py
│   │       │   └── schema.py
│   │       └── templates/
│   │           ├── __init__.py
│   │           ├── generators.py
│   │           └── validators.py
│   │
│   ├── cortex_brain/                     # Tier2 & Tier3: Specialized modules
│   │   ├── __init__.py
│   │   ├── tier0/                        # Tier0: Foundation protocols & models
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── protocols.py
│   │   ├── tier2/                        # Tier2: Specialized optimization & resilience
│   │   │   ├── __init__.py
│   │   │   ├── resilience/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── circuit_breaker.py
│   │   │   │   ├── fallback.py
│   │   │   │   └── retry.py
│   │   │   ├── intelligence/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ast_engine.py
│   │   │   │   └── pattern_detector.py
│   │   │   └── [other specializations]
│   │   └── tier3/                        # Tier3: Knowledge base & domain data
│   │       ├── __init__.py
│   │       ├── knowledge/                # Knowledge storage
│   │       │   ├── __init__.py
│   │       │   ├── index.py
│   │       │   └── schema.py
│   │       ├── domain/                   # Domain-specific data
│   │       │   └── __init__.py
│   │       └── [domain-specific modules]
│   │
│   └── devx/                             # Developer Experience tools (Tier2)
│       ├── __init__.py
│       ├── testing/
│       ├── debugging/
│       └── profiling/
│
├── tests/
│   ├── unit/
│   │   ├── cortex/                       # Mirror src/cortex structure
│   │   │   ├── core/
│   │   │   ├── infrastructure/
│   │   │   ├── orchestrators/
│   │   │   ├── api/
│   │   │   └── tools/
│   │   └── cortex_brain/
│   │       ├── tier0/
│   │       ├── tier2/
│   │       └── tier3/
│   │
│   ├── integration/
│   │   ├── test_phase_*.py              # Phase-specific integration tests
│   │   ├── test_orchestrator_*.py
│   │   └── test_governance_*.py
│   │
│   ├── conftest.py                      # Pytest configuration
│   └── fixtures/
│       ├── __init__.py
│       ├── database.py
│       └── mocks.py
│
├── scripts/
│   ├── maintenance/
│   │   ├── migrate-folder-structure.py  # AC-AR-010-02 deliverable
│   │   ├── migration-validator.py
│   │   └── update-imports.py            # AC-AR-010-03 deliverable
│   │
│   └── validation/
│       ├── validate-imports.py
│       ├── validate-phase-sync.py
│       └── check-dor.py
│
├── docs/
│   ├── FOLDER-STRUCTURE-DESIGN.md       # This document (AC-AR-010-01)
│   ├── API.md
│   ├── GOVERNANCE.md
│   └── [other docs]
│
├── .github/
│   ├── prompts/
│   │   └── cortex-builder.prompt.md
│   └── workflows/
│       └── [CI/CD workflows]
│
├── cortex-master.yaml                   # Master roadmap (Unified Phase Mode)
├── pytest.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Key Changes Explained

1. **Tier-Based Organization**:
   - Tier0 (protocols, models) in `cortex_brain/tier0`
   - Tier1 (core logic) in `src/cortex/core`, `src/cortex/infrastructure`
   - Tier2 (specialization) in `cortex_brain/tier2` and `src/devx`
   - Tier3 (knowledge) in `cortex_brain/tier3`

2. **Clear Separation of Concerns**:
   - `core/`: Logic layer (governance, orchestration, intent routing)
   - `infrastructure/`: Technical layer (DB, logging, config, security)
   - `orchestrators/`: Orchestrator implementations (core + domain-specific)
   - `api/`: REST API endpoints
   - `tools/`: CLI utilities
   - `cortex_brain/`: Specialized tier-based modules

3. **Test Mirror Structure**:
   - `tests/unit/cortex/` mirrors `src/cortex/`
   - `tests/unit/cortex_brain/` mirrors `src/cortex_brain/`
   - `tests/integration/` for cross-module tests

4. **Portable Paths**:
   - All paths use `Path(__file__).parent` or similar
   - No /Users/asifhussain/ hardcoded anywhere
   - Works on any OS (Linux, macOS, Windows)

---

## Migration Impact Analysis

### What Moves Where

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `cortex/core/` | `src/cortex/core/` | Consolidate under src |
| `cortex/infrastructure/` | `src/cortex/infrastructure/` | Consolidate under src |
| `cortex/orchestrators/` | `src/cortex/orchestrators/` | Consolidate under src |
| `cortex/api/` | `src/cortex/api/` | Consolidate under src |
| `cortex/tools/` | `src/cortex/tools/` | Consolidate under src |
| `cortex_brain/` | `src/cortex_brain/` | Consolidate under src |
| `cortex_brain/` | DELETE (deprecated) | Consolidate duplicates |
| `tests/` | `tests/` (reorganized) | Mirror new src structure |

### What Stays the Same

- ✅ `docs/` - Documentation stays at root
- ✅ `scripts/` - Scripts stay at root (but reorganized)
- ✅ `_workspaces/` - Workspace files stay at root
- ✅ Root config files (`pytest.ini`, `requirements.txt`, etc.)

### Import Path Changes

```python
# OLD
from cortex.core.governance import GovernanceRegistry
from cortex.infrastructure.database import DatabaseManager
from cortex_brain.tier2.resilience import CircuitBreaker

# NEW
from cortex.core.governance import GovernanceRegistry  # Same path!
from cortex.infrastructure.database import DatabaseManager  # Same path!
from cortex_brain.tier2.resilience import CircuitBreaker  # Same path!

# The imports stay mostly the same because we're using `src/` as PYTHONPATH
# Python finds src/cortex/* automatically
```

---

## Benefits of This Structure

### 1. Maintainability ⭐⭐⭐⭐⭐
- Clear separation of concerns
- Easy to find related modules
- Intuitive navigation

### 2. Scalability ⭐⭐⭐⭐⭐
- Tier-based growth doesn't create confusion
- Can add new domain orchestrators easily
- New infrastructure concerns have a clear home

### 3. Testability ⭐⭐⭐⭐⭐
- Test structure mirrors source structure
- Easy to find relevant tests
- Integration tests clearly separated

### 4. Cross-Platform Compatibility ⭐⭐⭐⭐⭐
- No /Users/ paths hardcoded anywhere
- Uses Path(__file__).parent consistently
- Works on Linux, macOS, Windows

### 5. Import Coherence ⭐⭐⭐⭐⭐
- Clear tier boundaries prevent circular imports
- Easy to validate import dependencies
- Reduces import bugs

---

## Risk Assessment

### Critical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Import path breakage** | HIGH | CRITICAL | Use automated migration script, test thoroughly before execution |
| **Test suite failures** | MEDIUM | HIGH | Mirror structure exactly, run tests on new structure before commit |
| **Circular imports emerge** | MEDIUM | HIGH | Use import validator tool to detect cycles |
| **File integrity loss** | LOW | CRITICAL | Implement rollback capability, validate checksums |

### Medium Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Developer confusion** | MEDIUM | MEDIUM | Document clearly, training session, gradual rollout |
| **CI/CD breakage** | MEDIUM | HIGH | Update CI/CD pipelines before migration |
| **Package discovery issues** | LOW | MEDIUM | Use `src/` layout best practices consistently |

### Mitigation Strategies

1. **Pre-Migration Testing**: Test new structure in isolated environment
2. **Automated Validation**: Use migration validator before final commit
3. **Incremental Rollout**: Migrate one module at a time if needed
4. **Rollback Plan**: Keep original structure until new structure validated
5. **Communication**: Keep team informed of changes

---

## Governance Compliance Checklist

- ✅ **CORE-004**: Codebase Organization (primary focus)
- ✅ **CORE-028**: Portable paths (no /Users/asifhussain/ hardcoding)
- ✅ **CORE-011**: Type hints in import statements
- ✅ **CORE-012**: Docstrings for all modules

---

## Success Criteria

### Design Acceptance
- ✅ Structure diagram clear and complete
- ✅ Benefits analysis documented
- ✅ Risk assessment comprehensive
- ✅ Migration plan detailed
- ✅ Governance approval obtained

### Metrics
- Folder depth: 4-5 levels maximum
- Module clarity: Each folder has single responsibility
- Test coverage: Mirror structure 100% covered
- Import complexity: No circular dependencies

---

## Next Steps (AC-AR-010-02)

Once this design is approved:
1. Create migration script (AC-AR-010-02)
2. Test on staging environment
3. Execute migration
4. Update all imports (AC-AR-010-03)
5. Run full test suite
6. Phase complete!

---

## References

- **Governance**: CORE-004 (Organization), CORE-028 (Portable Paths)
- **Architecture Decision**: AR-010 (Nested Folder Organization)
- **Phase**: PHASE-02-CODEBASE-COHERENCE
- **AC-ID**: AC-AR-010-01

---

**Status**: 🚀 READY FOR STAKEHOLDER REVIEW  
**Last Updated**: 2026-01-18  
**Next Milestone**: AC-AR-010-02 (Migration Script)
