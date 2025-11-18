---
title: CORTEX Tier System
description: Complete documentation of CORTEX's 4-tier memory architecture
author: 
generated: true
version: ""
last_updated: 
---

# CORTEX Tier System

**Purpose:** Comprehensive documentation of the 4-tier memory and intelligence architecture  
**Audience:** Developers, architects, advanced users  
**Version:**   
**Last Updated:** 

---

## Overview

CORTEX implements a **4-tier cognitive architecture** inspired by human brain structure:

```
┌─────────────────────────────────────────────────┐
│  TIER 0: INSTINCT (Immutable Core Rules)       │
│  Governance, protection, foundational rules     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 1: WORKING MEMORY (Last 20 Conversations)│
│  Short-term context, recent interactions        │
│  Storage: SQLite + JSONL                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 2: KNOWLEDGE GRAPH (Long-term Learning)  │
│  Patterns, relationships, workflows             │
│  Storage: SQLite + YAML                         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  TIER 3: CONTEXT INTELLIGENCE (Project Metrics)│
│  Git analysis, code health, session analytics   │
│  Storage: SQLite + JSONL                        │
└─────────────────────────────────────────────────┘
```

---

## Tier 0: Instinct (Protection Layer)

### Purpose

Tier 0 contains **immutable governance rules** that protect CORTEX's architectural integrity and enforce development best practices.

### Key Capabilities





### Protection Layers

1. **Instinct Immutability** - Core rules cannot be bypassed
2. **Critical Path Protection** - Essential files protected from modification
3. **Application Separation** - User code stays out of CORTEX core
4. **Brain State Protection** - Memory files excluded from git commits
5. **Namespace Isolation** - Scope boundaries enforced
6. **Architectural Integrity** - Design principles maintained

### File Locations

- **Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Implementation:** `src/tier0/brain_protector.py`
- **Tests:** `tests/tier0/test_brain_protector.py`

### Usage Example

```python
from src.tier0.brain_protector import BrainProtector

protector = BrainProtector()

# Validate proposed change
result = protector.validate_change(
    intent="Modify tier0 rules",
    description="Add new governance rule",
    affected_files=["cortex-brain/brain-protection-rules.yaml"],
    scope="cortex"
)

if not result.allowed:
    print(f"Blocked: {result.severity}")
    print(f"Alternatives: {result.alternatives}")
```

---

## Tier 1: Working Memory

### Purpose

Tier 1 provides **short-term conversation memory** using a FIFO queue (last 20 conversations). This solves the "amnesia problem" where GitHub Copilot forgets context between sessions.

### Key Capabilities





### Data Storage

**Database:** `cortex-brain/tier1/conversations.db` (SQLite)

**Tables:**
- `conversations` - Conversation metadata and summaries
- `messages` - Individual messages within conversations
- `entities` - Tracked entities (files, classes, functions)

**Performance:** <50ms average query time ⚡

### FIFO Queue Management

Tier 1 maintains the **last 20 conversations** automatically:

- When conversation #21 starts, conversation #1 is archived
- Current active conversation never deleted (protected)
- Archived conversations moved to `cortex-brain/tier1/archive/`

### Usage Example

```python
from src.tier1.working_memory import WorkingMemory

memory = WorkingMemory()

# Store conversation
conv_id = memory.store_conversation(
    user_message="Add authentication to dashboard",
    assistant_response="I'll implement JWT authentication...",
    intent="EXECUTE",
    context={
        "files_modified": ["AuthService.cs"],
        "entities": ["authentication", "dashboard", "JWT"]
    }
)

# Retrieve recent conversations
recent = memory.get_recent_conversations(limit=5)

# Search by entity
auth_convos = memory.search_by_entity(
    entity_type="file",
    entity_value="AuthService.cs"
)
```

---

## Tier 2: Knowledge Graph

### Purpose

Tier 2 provides **long-term pattern learning** and workflow templates. CORTEX gets smarter with every interaction by learning from successful approaches.

### Key Capabilities





### Data Storage

**Database:** `cortex-brain/tier2/knowledge-graph.db` (SQLite)

**Tables:**
- `patterns` - Learned intent patterns and solutions
- `relationships` - File co-modification relationships
- `workflows` - Successful workflow templates
- `patterns_fts` - Full-text search index (FTS5)

**Performance:** <150ms average search time ⚡

### Pattern Learning

CORTEX learns from past interactions:

**Example Learning Flow:**
```
Day 1: User: "Add invoice export feature"
       → CORTEX creates workflow, stores pattern
       → Confidence: 0.85

Day 30: User: "Add receipt export feature"
        → CORTEX: "This is similar to invoice export (85% match)"
        → Reuses proven pattern
        → 60% faster delivery ⚡
```

### Pattern Decay

Unused patterns decay over time to keep knowledge fresh:
- Decay rate: 5% confidence drop per 30 days
- Pruning threshold: <30% confidence
- Reinforcement: +5% confidence boost when successfully reused

### Usage Example

```python
from src.tier2.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()

# Store pattern
pattern_id = kg.store_pattern(
    title="Invoice Export Workflow",
    pattern_type="workflow",
    confidence=0.85,
    context={
        "files": ["InvoiceService.cs", "ExportController.cs"],
        "steps": ["validate", "format", "generate", "download"],
        "success_rate": 0.94
    }
)

# Search for similar patterns
patterns = kg.search_patterns(
    query="export feature",
    min_confidence=0.7
)

# Track file relationships
kg.track_relationship(
    file_a="HostControlPanel.razor",
    file_b="noor-canvas.css",
    relationship_type="co_modification",
    strength=0.75
)
```

---

## Tier 3: Context Intelligence

### Purpose

Tier 3 provides **holistic project understanding** through git analysis, code health metrics, and session analytics. It gives CORTEX the "balcony view" of your development process.

### Key Capabilities





### Data Storage

**Database:** `cortex-brain/tier3/context-intelligence.db` (SQLite)

**Tables:**
- `git_commits` - Commit history analysis
- `file_metrics` - File stability and churn rates
- `session_analytics` - Developer productivity patterns
- `code_health` - Test coverage and build metrics

**Performance:** <200ms average analysis time ⚡

### Git Analysis

CORTEX analyzes your commit history to identify:

- **Commit velocity:** Tracks productivity trends
- **File hotspots:** Files with high churn rate (>10% unstable)
- **Change patterns:** Small commits (<200 lines) have higher success rates
- **Contributor activity:** Identifies knowledge silos

### Proactive Warnings

Tier 3 provides early warnings:

```
⚠️ File Alert: HostControlPanel.razor is a hotspot (28% churn rate)
   Recommendation: Add extra testing before changes
                  Consider smaller, incremental modifications

✅ Optimal Time: 10am-12pm sessions have 94% success rate
   Current Time: 2:30pm (81% success rate historically)
   Suggestion: Consider scheduling complex work for morning
```

### Usage Example

```python
from src.tier3.context_intelligence import ContextIntelligence

ci = ContextIntelligence()

# Analyze git activity
analysis = ci.analyze_git_activity(
    lookback_days=30,
    include_hotspots=True
)

# Get file stability
stability = ci.get_file_stability("AuthService.cs")
# Returns: "stable" | "unstable" | "volatile"

# Get proactive warnings
warnings = ci.get_file_warnings("HostControlPanel.razor")

# Get session timing recommendations
timing = ci.get_optimal_session_timing()
```

---

## Tier Interactions

### How Tiers Work Together

**Example: "Make it purple" request**

```
1. User: "Make it purple"
   ↓
2. Tier 1 checks: What was discussed recently?
   → Found: "added button to dashboard" (5 minutes ago)
   ↓
3. Tier 2 checks: Similar past requests?
   → Found: "make button purple" pattern (confidence: 0.88)
   ↓
4. Tier 3 checks: File stability?
   → dashboard.css: stable (low churn rate)
   ↓
5. CORTEX: "Applying purple color to dashboard button"
   → Uses Tier 1 context + Tier 2 pattern + Tier 3 safety check
```

### Data Flow

```
Tier 0 (Governance)
    ↓ (Validates all operations)
Tier 1 (Working Memory)
    ↓ (Provides recent context)
Tier 2 (Knowledge Graph)
    ↓ (Suggests patterns and workflows)
Tier 3 (Context Intelligence)
    ↓ (Adds project-specific insights)
Agent System
    ↓ (Executes with full context)
User Receives Response
```

---

## Performance Metrics

| Tier | Target | Actual | Status |
|------|--------|--------|--------|
| **Tier 1: Store** | <30ms | 12ms | ⚡ Excellent |
| **Tier 1: Query** | <50ms | 18ms | ⚡ Excellent |
| **Tier 2: Pattern Search** | <150ms | 92ms | ⚡ Excellent |
| **Tier 2: Store Pattern** | <80ms | 56ms | ⚡ Excellent |
| **Tier 3: Git Analysis** | <200ms | 156ms | ⚡ Excellent |
| **Tier 3: File Stability** | <100ms | 67ms | ⚡ Excellent |

---

## Configuration

### Tier Configuration

Edit `cortex.config.json`:

```json
{
  "tier1": {
    "enabled": true,
    "maxConversations": 20,
    "fifoMode": true,
    "autoArchive": true
  },
  
  "tier2": {
    "enabled": true,
    "patternDecay": 0.05,
    "minConfidence": 0.7
  },
  
  "tier3": {
    "enabled": true,
    "gitAnalysisLookback": 30
  }
}
```

---

## Related Documentation

- **Architecture Overview:** [Overview](overview.md)
- **Agent System:** [Agents](agents.md)
- **Operations:** [Operations Overview](../operations/overview.md)
- **API Reference:** [API](../reference/api.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 