# 🧠 CORTEX - Brain Tier Organization

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Plan ID:** cortex-rearchitecture-v1 / Phase 11  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED | **Phase 2 Start:** Q1 2026

---

## 🎯 Objectives

Reorganize brain tier structure to eliminate redundancy between `cortex-brain/tierN/` and `src/tierN/` directories, establish clear separation of data vs code.

**Key Deliverables:**
1. Consolidated tier structure (data in cortex-brain, code in src)
2. Eliminated duplicate tier directories
3. Clear data/code separation guidelines
4. Updated all tier references in codebase
5. Migration documentation

**Duration:** 16h (2 days)  
**Dependencies:** Phase 10 (Cleanup Orchestrator Enhancement) complete

---

## 📋 Key Tasks

### Task 11.1: Tier Structure Analysis
- Audit current tier directory usage
- Identify overlaps between cortex-brain/tierN and src/tierN
- Document current data/code distribution
- Define target architecture

### Task 11.2: Target Architecture Design
**Proposed Structure:**
```
cortex-brain/
├── tier0/  # Governance data (rules, configs)
├── tier1/  # Working memory data (conversations, sessions)
├── tier2/  # Knowledge graph data (patterns, lessons)
├── tier3/  # Dev context data (metrics, hotspots)

src/
├── tier0/  # Governance code (validators, enforcers)
├── tier1/  # Working memory code (managers, persistence)
├── tier2/  # Knowledge graph code (query engine, pattern matching)
├── tier3/  # Dev context code (metric collectors, analyzers)
```

### Task 11.3: Migration Execution
- Move data files to cortex-brain/tierN/
- Move code files to src/tierN/
- Update all imports and references
- Run full test suite after migration
- Update documentation

### Task 11.4: Validation & Documentation
- Verify no duplicate functionality
- Document tier responsibilities
- Update developer guides
- Add tier organization to brain-protection-rules.yaml

---

## 🧪 Testing Strategy

- Test all tier imports after migration
- Verify data file access patterns
- Run full test suite (must pass 100%)
- Integration tests for tier interactions

---

## 📊 Success Criteria

- No duplicate tier directories (one source of truth)
- Clear data/code separation
- All tests passing after migration
- Documentation updated
- Zero import errors
- 100% test coverage maintained

---

**Duration:** 16h (2 days)  
**Next Phase:** [Phase 12: Realignment Phase](12-realignment-phase.md)
