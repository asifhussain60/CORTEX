# PHASE 57 QUICK REFERENCE

## 🚀 Quick Start
```bash
# To resume Phase 57 in next session:
python cortex/execution/phase_57_kickoff.py

# Or use CORTEX command:
/plan phase-57
```

## 📋 Phase Overview
- **Name:** Architectural Pattern Detection & Classification
- **Duration:** 4 days
- **Tests:** 45 (target) | Coverage: 92%
- **Status:** APPROVED
- **ROI:** 0.82

## 🎯 5 Stages

| Stage | Name | Duration | Tests | Focus |
|-------|------|----------|-------|-------|
| S1 | Pattern Foundation | 1d | 9 | BasePatternDetector + 25+ patterns |
| S2 | Pattern Detectors | 1d | 12 | Creational/Structural/Behavioral/Concurrency |
| S3 | Architecture Classification | 1d | 10 | MVC, DDD, Layered, Microservices, CQRS |
| S4 | Anti-Patterns | 0.5d | 8 | GodClass, CircularDeps, ServiceLocator |
| S5 | LENS & MCP | 1d | 8 | Integration + 3 MCP tools |

## 🔑 Key Deliverables
- ✅ 40+ pattern detectors implemented
- ✅ 7+ architecture types recognized
- ✅ 8+ anti-patterns detected
- ✅ 3 MCP tools: detect_patterns, classify_architecture, detect_anti_patterns
- ✅ LENS integration via ArchitecturePatternSource

## 📍 File Locations
```
cortex/
  intelligence/
    patterns/              # NEW MODULE
      __init__.py
      base.py              # BasePatternDetector
      catalog.py           # PatternCatalog (25+ patterns)
      detectors/
        creational.py
        structural.py
        behavioral.py
        concurrency.py
      anti_patterns.py
      classification.py
  
  lens/
    sources/
      architecture.py      # LENS integration
  
  mcp/
    tools/
      pattern_tools.py     # 3 MCP tools
```

## ✅ Success Criteria
- [ ] 45+ tests passing
- [ ] 92%+ coverage
- [ ] Pattern detection > 85% accuracy
- [ ] Zero circular dependencies
- [ ] All CORE rules enforced

## 🔗 Dependencies
- ✅ Phase 56-A (LENS/Intelligence Hybrid)
- ✅ Phase 49 (Context Crystallization Layer)
- ✅ Phase 51 (MCP-First Enforcement)

## 📊 Unblocks
- Phase 58: Async Crawler Framework
- Phase 59: ML-Based Pattern Similarity
- Phase 60: Enterprise Pattern Registry

## 💾 Checkpoints (Auto-saved)
- S1 Complete: ~2026-02-10 12:00 UTC
- S2 Complete: ~2026-02-11 08:00 UTC
- S3 Complete: ~2026-02-11 20:00 UTC
- S4 Complete: ~2026-02-12 04:00 UTC
- S5 Complete: ~2026-02-13 00:00 UTC

## 🛡️ Enforcement
- TDD-First: ✅ (tests before code)
- MCP-First: ✅ (all tools via MCP)
- Holistic Validation: ✅ (Phase 48 gate)
- CORE Rules: ✅ (7 agents, 26 rules)

## 📖 Registry
- Spec: `cortex-registry/_cortex-master/phases/active/phase-57-architectural-pattern-detection.yaml`
- Index: `cortex-registry/_cortex-master/index.yaml`
