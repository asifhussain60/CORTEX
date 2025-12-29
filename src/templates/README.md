# CORTEX 4.0 Response Templates

**Status:** Phase 1 - Directory structure created, awaiting v4.0 implementation

## Purpose

This directory will contain the Response Template System v4.0 with adaptive minimalism.

## Phase 1 Implementation (Week 2)

The following components will be implemented:

### Core System
- **template_manager.py** - Main template manager (<500 lines)
- **tier_selector.py** - Select appropriate response tier
- **section_selector.py** - Dynamically choose sections
- **renderer.py** - Render templates to markdown

### Template Storage
- **templates-v4.yaml** - Single template file (<500 lines)
  - 4 tiers: INSTANT, FOCUSED, STRUCTURED, COMPREHENSIVE
  - Reusable components library
  - Dynamic section mapping

## Template Tiers

**TIER 1: INSTANT** (0-50 tokens) - Direct answers  
**TIER 2: FOCUSED** (50-200 tokens) - Single-concept explanations  
**TIER 3: STRUCTURED** (200-600 tokens) - Multi-faceted responses  
**TIER 4: COMPREHENSIVE** (600+ tokens) - Complex operations  

## Token Efficiency Goal

- Overall: ~60% token savings vs v3.0
- Simple queries: 80-90% reduction
- Medium queries: 50-60% reduction
- Complex queries: 20-30% reduction

## Migration Strategy

1. **Week 2, Days 4-5:** Deploy v4.0 alongside v3.0 (20% traffic)
2. **Week 3, Days 1-2:** Increase to 50% traffic, tune boundaries
3. **Week 3, Day 3:** Full deployment to 100%
4. **Week 3, Days 4-5:** Optimization and documentation

## Migration Prerequisites

Before implementing v4.0:
1. ✅ CORTEX-4.0 branch created
2. ☐ Template tier design finalized
3. ☐ Routing logic implemented
4. ☐ A/B testing infrastructure ready

See: `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md` (Response Template System Redesign section)
