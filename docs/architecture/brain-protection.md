---
title: Brain Protection
description: CORTEX brain protection rules and enforcement
author: 
generated: true
version: ""
last_updated: 
---

# Brain Protection

**Purpose:** Documentation of CORTEX brain protection rules and enforcement  
**Audience:** Developers, administrators  
**Version:**   
**Last Updated:** 

---

## Overview

CORTEX implements **Rule #22: Challenge risky changes to the brain** through a 6-layer protection system. This prevents architectural degradation and data corruption.

---

## Protection Layers

### Layer 1: Instinct Immutability

**Purpose:** Core governance rules cannot be bypassed

**Protected Elements:**
- Tier 0 rules in `cortex-brain/brain-protection-rules.yaml`
- TDD enforcement (RED → GREEN → REFACTOR)
- Definition of Done (zero errors, zero warnings)

**Enforcement:** Brain Protector agent blocks modifications with severity "blocked"

---

### Layer 2: Critical Path Protection

**Purpose:** Essential CORTEX files protected from modification

**Protected Files:**
- `cortex-brain/brain-protection-rules.yaml`
- `src/tier0/brain_protector.py`
- Core orchestrator files

**Enforcement:** Change Governor challenges modifications, suggests alternatives

---

### Layer 3: Application Separation

**Purpose:** Keep user application code out of CORTEX core

**Protected Directories:**
- `src/cortex_agents/`
- `src/epm/`
- `cortex-brain/`

**Enforcement:** Change Governor detects application-specific code and redirects to application layer

---

### Layer 4: Brain State Protection

**Purpose:** Conversation history and brain state not committed to git

**Protected Files:**
- `cortex-brain/tier1/conversations.db`
- `cortex-brain/conversation-context.jsonl`
- `cortex-brain/tier2/knowledge-graph.db`
- `cortex-brain/tier3/context-intelligence.db`

**Enforcement:** `.gitignore` rules + Brain Protector validation

---

### Layer 5: Namespace Isolation

**Purpose:** Scope boundaries enforced between `cortex.*` and `workspace.*` namespaces

**Rules:**
- CORTEX knowledge stays in `cortex.*` namespace
- User workspace knowledge in `workspace.*` namespace
- No cross-contamination allowed

**Enforcement:** Tier 2 Knowledge Graph enforces namespace isolation

---

### Layer 6: Architectural Integrity

**Purpose:** Design principles maintained over time

**Principles Protected:**
- Local-First Architecture (no external dependencies)
- Modular Design (token optimization)
- Test-Driven Development
- SOLID Principles

**Enforcement:** Change Governor + Brain Protector coordinated validation

---

## Challenge Workflow

When risky change detected:

```
User Request
    ↓
Brain Protector Analysis
    ↓
Risk Detected → Challenge Issued
    ↓
Alternatives Suggested
    ↓
User Decision:
  - Accept alternative ✅
  - Override with justification (requires approval)
  - Cancel request
```

---

## Configuration

Edit `cortex.config.json`:

```json
{
  "tier0": {
    "enabled": true,
    "protection_layers": [
      "instinct_immutability",
      "critical_path_protection",
      "application_separation",
      "brain_state_protection",
      "namespace_isolation",
      "architectural_integrity"
    ]
  },
  
  "agents": {
    "brainProtector": {
      "enabled": true,
      "blockSeverity": "blocked",
      "challengeSeverity": "warning"
    }
  }
}
```

---

## Related Documentation

- **Agent Architecture:** [Agents](agents.md)
- **Tier System:** [Tier System](tier-system.md)
- **Configuration:** [Configuration Guide](../getting-started/configuration.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 