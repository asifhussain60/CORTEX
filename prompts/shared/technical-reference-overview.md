# CORTEX Technical Reference - Overview

**Purpose:** High-level technical overview with links to detailed specifications  
**Audience:** Developers, technical users, system architects, plugin developers  
**Version:** 2.0 (Modular)  
**Status:** Production Ready

---

## 📐 Architecture Overview

CORTEX implements a **five-tier cognitive architecture** inspired by human brain structure:

```
TIER 0: INSTINCT (Immutable Core Rules)
       ↓
TIER 1: WORKING MEMORY (Last 20 Conversations) 
       ↓
TIER 2: LONG-TERM MEMORY (Knowledge Graph)
       ↓  
TIER 3: CONTEXT INTELLIGENCE (Git Analysis)
       ↓
TIER 4: REAL-TIME EVENTS (Session Activity)
```

**Detailed Specifications:**
- [Tier 0 API](../../cortex-brain/reference/tier0-api.yaml) - Governance & Protection
- [Tier 1 API](../../cortex-brain/reference/tier1-api.yaml) - Working Memory 
- [Tier 2 API](../../cortex-brain/reference/tier2-api.yaml) - Knowledge Graph
- [Tier 3 API](../../cortex-brain/reference/tier3-api.yaml) - Context Intelligence
- [Agent System](../../cortex-brain/reference/agent-system.yaml) - 10 Specialist Agents
- [Plugin Development](../../cortex-brain/reference/plugin-development.yaml) - Extension Framework

## 🧠 Agent Architecture

**Dual Hemisphere Design:**
- **Left Brain (Tactical):** Code Executor, Test Generator, Error Corrector, Health Validator, Commit Handler
- **Right Brain (Strategic):** Intent Router, Work Planner, Screenshot Analyzer, Change Governor, Brain Protector

**Coordination:** Corpus Callosum message queue system

## 🔌 Key APIs

**Entry Point:**
```python
from src.entry_point.cortex_entry import CortexEntry
cortex = CortexEntry()
result = cortex.process("Add authentication to login page")
```

**Tier 1 Working Memory:**
```python
from src.tier1.working_memory import WorkingMemory
memory = WorkingMemory()
memory.store_conversation(user_msg, assistant_response, intent)
```

**Tier 2 Knowledge Graph:**
```python
from src.tier2.knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph()
patterns = kg.search_patterns("authentication workflow")
```

## ⚙️ Configuration

**Main Config:** `cortex.config.json`
**Detailed Reference:** [Configuration Guide](../../cortex-brain/reference/configuration.yaml)

## 🧪 Testing & Performance

**Testing Protocols:** [Test Strategy](../../cortex-brain/reference/testing-protocols.yaml)  
**Performance Benchmarks:** [Performance Metrics](../../cortex-brain/reference/performance-benchmarks.yaml)

## 📚 Developer Resources

- **Setup Guide:** [Getting Started](../setup-guide.md)
- **Plugin Development:** [Plugin Framework](../../cortex-brain/reference/plugin-development.yaml) 
- **Agent Creation:** [Agent Development](../../cortex-brain/reference/agent-development.yaml)
- **API Examples:** [Code Examples](../../cortex-brain/reference/api-examples.yaml)

## 🎯 Quick Start

1. **Install:** Follow [Setup Guide](../setup-guide.md)
2. **Configure:** Edit `cortex.config.json` 
3. **Test:** `python scripts/cortex_cli.py --status`
4. **Develop:** See [API Examples](../../cortex-brain/reference/api-examples.yaml)

---

**For detailed technical specifications, see the YAML reference files in `cortex-brain/reference/`**

**Version:** 2.0 (Modular)  
**Last Updated:** November 16, 2025  
**Architecture:** Modular reference system