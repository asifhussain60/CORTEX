---
title: Configuration Reference
description: Complete cortex.config.json configuration reference
author: 
generated: true
version: ""
last_updated: 
---

# Configuration Reference

**Purpose:** Complete reference for cortex.config.json settings  
**Audience:** System administrators, developers, power users  
**Version:**   
**Last Updated:** 

---

## Overview

CORTEX configuration is managed through `cortex.config.json` in the project root. This file controls all memory tiers, agent behavior, tracking methods, and performance settings.

---

## Core Configuration

```json
{
  "version": "2.0",
  "name": "CORTEX",
  "description": "Memory and context system for GitHub Copilot"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `version` | string | `"2.0"` | Configuration schema version |
| `name` | string | `"CORTEX"` | System name |
| `description` | string | - | System description |

---

## Tier 0: Governance

```json
"tier0": {
  "enabled": true,
  "governance_rules": "cortex-brain/brain-protection-rules.yaml",
  "immutable": true,
  "protection_layers": [...]
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Tier 0 (NEVER disable) |
| `governance_rules` | string | - | Path to rules YAML |
| `immutable` | boolean | `true` | Rules cannot change at runtime |
| `protection_layers` | array | 6 layers | Active protection layers |

---

## Tier 1: Working Memory

```json
"tier1": {
  "enabled": true,
  "database": "cortex-brain/tier1/conversations.db",
  "maxConversations": 20,
  "fifoMode": true,
  "autoArchive": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Tier 1 |
| `database` | string | - | SQLite database path |
| `maxConversations` | integer | `20` | FIFO queue limit |
| `fifoMode` | boolean | `true` | Auto-delete oldest |
| `autoArchive` | boolean | `true` | Archive before delete |

---

## Tier 2: Knowledge Graph

```json
"tier2": {
  "enabled": true,
  "database": "cortex-brain/tier2/knowledge-graph.db",
  "patternLearning": {
    "enabled": true,
    "minConfidence": 0.7,
    "decayRate": 0.05
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Tier 2 |
| `database` | string | - | SQLite database path |
| `minConfidence` | float | `0.7` | Min confidence for patterns |
| `decayRate` | float | `0.05` | Pattern decay rate |

---

## Tier 3: Context Intelligence

```json
"tier3": {
  "enabled": true,
  "database": "cortex-brain/tier3/context-intelligence.db",
  "gitAnalysis": {
    "enabled": true,
    "maxCommits": 1000
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Tier 3 |
| `database` | string | - | SQLite database path |
| `maxCommits` | integer | `1000` | Commits to analyze |

---

## Agent System

```json
"agents": {
  "enabled": true,
  "intentRouter": {
    "enabled": true,
    "confidenceThreshold": 0.75
  },
  "codeExecutor": {
    "enabled": true,
    "enforceTDD": true
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable all agents |
| `confidenceThreshold` | float | `0.75` | Min confidence for routing |
| `enforceTDD` | boolean | `true` | Require TDD workflow |

---

## Tracking Configuration

```json
"tracking": {
  "method": "ambient_daemon",
  "ambientDaemon": {
    "enabled": true,
    "autoStart": true,
    "idleThresholdSeconds": 30
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `method` | string | - | Tracking method: `ambient_daemon`, `python_cli`, `powershell` |
| `autoStart` | boolean | `true` | Auto-start with VS Code |
| `idleThresholdSeconds` | integer | `30` | Capture after N seconds idle |

---

## Machine Settings

```json
"machine": {
  "id": "DESKTOP-PRIMARY",
  "workspacePath": "d:\\PROJECTS\\CORTEX",
  "pythonPath": "python"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `id` | string | - | Unique machine ID |
| `workspacePath` | string | - | Absolute path to CORTEX |
| `pythonPath` | string | `"python"` | Python executable |

---

## Performance

```json
"performance": {
  "cacheEnabled": true,
  "cacheSizeMB": 100,
  "parallelProcessing": true,
  "maxWorkerThreads": 4
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `cacheEnabled` | boolean | `true` | Enable in-memory cache |
| `cacheSizeMB` | integer | `100` | Max cache size |
| `parallelProcessing` | boolean | `true` | Use multiple threads |
| `maxWorkerThreads` | integer | `4` | Max parallel threads |

---

## Configuration Validation

Validate your configuration:

```bash
cortex config validate
```

Export configuration:

```bash
cortex config export --output backup.json
```

Import configuration:

```bash
cortex config import --input backup.json
```

---

## Related Documentation

- **Setup Guide:** [Setup](../getting-started/installation.md)
- **API Reference:** [API](api-reference.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 