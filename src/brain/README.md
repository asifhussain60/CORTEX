# CORTEX 4.0 Brain

**Status:** Phase 1 - Directory structure created, awaiting migration

## Purpose

This directory will contain the brain tier implementations for CORTEX 4.0, providing centralized intelligence and memory management.

## Phase 2 Implementation (Weeks 4-6)

The following brain tiers will be migrated here:

### Tier 0 - Governance
- **rules_engine.py** - Enforce SKULL brain protection rules
- **skull_protector.py** - Prevent harmful operations

### Tier 1 - Working Memory
- **conversation_manager.py** - Manage conversation context
- **context_resolver.py** - Resolve context references
- **fifo_queue.py** - 20-conversation rolling window

### Tier 2 - Knowledge Graph
- **pattern_storage.py** - Store learned patterns
- **knowledge_graph_builder.py** - Build knowledge relationships
- **cross_project_insights.py** - Multi-project learning

### Tier 3 - Development Context
- **git_metrics_collector.py** - Collect git metrics
- **repository_context.py** - Maintain repo context

## Brain Interface

A unified `BrainInterface` will provide consistent access to all tiers:

```python
from src.brain import BrainInterface

brain = BrainInterface(cortex_root)
brain.tier1.store_conversation(...)
brain.tier2.store_pattern(...)
brain.tier3.get_git_metrics(...)
```

## Migration Prerequisites

Before migrating brain tiers:
1. ✅ CORTEX-4.0 branch created
2. ☐ Brain interface design complete (Phase 1)
3. ☐ Tier schemas validated
4. ☐ Migration scripts ready

See: `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md`
