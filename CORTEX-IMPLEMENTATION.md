# CORTEX - Cognitive Intelligence System

**Version:** 1.0.0-alpha  
**Status:** 🚧 **IN DEVELOPMENT** (Phase 0: Instinct Layer)  
**Branch:** `cortex-migration`

---

## What is CORTEX?

CORTEX is the next-generation evolution of KDS - a **concise, intelligent assistant** that provides summary-first responses with comprehensive documentation maintained separately.

**Key Improvements over KDS v8:**
- 🎯 **5x more concise** responses (<10 lines vs 30-50)
- ⚡ **10-100x faster** queries (<100ms vs 500-1000ms)
- 🧪 **95%+ test coverage** vs 15% (370 permanent tests)
- 🏗️ **33% simpler** architecture (4 tiers vs 6)
- 📦 **47% smaller** storage (<270 KB vs 380-570 KB)
- 🧠 **SQLite cognitive database** vs YAML files

---

## Architecture

### 4-Tier BRAIN System

```
Tier 0: Instinct (Governance)     → YAML (22 rules, ~20 KB)
Tier 1: Working Memory (STM)      → SQLite (last 20 conversations, <100 KB)
Tier 2: Long-Term Knowledge (LTM) → SQLite + FTS5 (patterns, <120 KB)
Tier 3: Context Intelligence      → JSON (git/test metrics, <50 KB)
```

**Total Storage:** <270 KB (vs KDS 380-570 KB)

---

## Development Status

### Phase 0: Instinct Layer ✅ (Current)
**Duration:** 1 day  
**Deliverables:**
- [ ] Tier 0 governance rules (YAML)
- [ ] Rule validation system
- [ ] 15 unit tests
- [ ] Documentation

### Phase 1: Working Memory (STM)
**Duration:** 2-3 days  
**Status:** 📋 Planned

### Phase 2: Long-Term Knowledge (LTM)
**Duration:** 3-4 days  
**Status:** 📋 Planned

### Phase 3: Context Intelligence
**Duration:** 2-3 days  
**Status:** 📋 Planned

### Phase 4: Specialist Agents
**Duration:** 4-5 days  
**Status:** 📋 Planned

### Phase 5: Entry Point & Workflows
**Duration:** 2-3 days  
**Status:** 📋 Planned

### Phase 6: Feature Parity Validation
**Duration:** 1-2 days  
**Status:** 📋 Planned

**Total Timeline:** 15-23 days (3-5 weeks)

---

## Project Structure

```
CORTEX/
├── src/                          # Core implementation
│   ├── tier0/                    # Instinct layer
│   ├── tier1/                    # Working memory
│   ├── tier2/                    # Long-term knowledge
│   └── tier3/                    # Context intelligence
├── tests/                        # 370 permanent tests
│   ├── tier0/                    # 15 tests
│   ├── tier1/                    # 58 tests
│   ├── tier2/                    # 79 tests
│   ├── tier3/                    # 44 tests
│   ├── agents/                   # 125 tests
│   ├── workflows/                # 45 tests
│   └── regression/               # 30 tests
├── cortex-agents/                # Refactored agents
│   ├── user/                     # User-facing entry points
│   ├── internal/                 # Specialist agents
│   └── shared/                   # Shared utilities
├── docs/                         # CORTEX-specific docs
└── README.md                     # This file
```

---

## Running CORTEX

**Not yet functional** - In development

Once Phase 6 complete:
```bash
# Entry point (replaces #file:KDS/prompts/user/kds.md)
#file:CORTEX/cortex-agents/user/cortex.md

Your request here
```

---

## Testing

**Target:** 95%+ coverage (370 tests)

```bash
# Run all tests (once implemented)
pytest CORTEX/tests/

# Run specific tier
pytest CORTEX/tests/tier0/

# Run with coverage
pytest --cov=CORTEX/src --cov-report=html
```

---

## KDS Compatibility

**During Migration:**
- KDS v8 remains on `main` branch (fully functional)
- CORTEX development isolated on `cortex-migration` branch
- Both systems coexist until Phase 6 validation complete

**After Migration:**
- CORTEX replaces KDS on `main` branch
- KDS preserved with Git tag `v8-final-kds-version`
- 100% feature parity guaranteed (370 regression tests)

---

## Documentation

- **Design:** `/cortex-design/CORTEX-DNA.md` (single source of truth)
- **Migration:** `/cortex-design/MIGRATION-STRATEGY.md`
- **Comparison:** `/cortex-design/WHY-CORTEX-IS-BETTER.md`
- **Feature Inventory:** `/cortex-design/feature-inventory/KDS-FEATURE-INVENTORY.md`

---

## Contributing

**Phase 0 (Current):**
1. Implement Tier 0 governance rules
2. Write 15 unit tests
3. Document instinct layer behavior
4. Validate against KDS Rule #22 (Brain Protection)

**See:** `/cortex-design/phase-plans/phase-0-instinct.md`

---

## Success Criteria

CORTEX v1.0 is complete when:
- ✅ All 6 phases implemented
- ✅ 370 tests passing (95%+ coverage)
- ✅ 100% KDS feature parity
- ✅ Performance targets met:
  - Query latency: <100ms
  - Storage size: <270 KB
  - Response length: <10 lines
  - Learning cycle: <2 minutes

---

## License

Same as KDS (inherits from parent project)

---

**Last Updated:** 2025-11-05  
**Current Phase:** Phase 0 (Instinct Layer)  
**Next Milestone:** Tier 0 governance implementation
