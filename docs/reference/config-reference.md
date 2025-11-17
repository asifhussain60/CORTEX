---
title: Configuration Reference
description: Complete CORTEX configuration options and settings
author: CORTEX Documentation Generator
generated: true
version: "1.0"
last_updated: 2025-11-17
---

# Configuration Reference

**Purpose:** Complete reference for cortex.config.json settings  
**Audience:** Administrators, developers  
**Version:** 1.0  
**Last Updated:** November 17, 2025

---

## Overview

CORTEX is configured through `cortex.config.json` in your project root. This file controls memory tiers, agent behavior, tracking methods, and machine-specific settings.

---

## Quick Reference

### Configuration Structure

```json
{
  "version": "2.0",
  "tier0": {...},        // Governance rules
  "tier1": {...},        // Working memory
  "tier2": {...},        // Knowledge graph
  "tier3": {...},        // Context intelligence
  "agents": {...},       // Agent configuration
  "tracking": {...},     // Conversation capture
  "machine": {...},      // Machine-specific
  "logging": {...},      // Log settings
  "performance": {...},  // Performance tuning
  "security": {...}      // Security options
}
```

---

## Core Settings

### Tier 0: Governance Rules

```json
"tier0": {
  "enabled": true,
  "governance_rules": "cortex-brain/brain-protection-rules.yaml",
  "immutable": true,
  "protection_layers": [
    "instinct_immutability",
    "critical_path_protection",
    "application_separation",
    "brain_state_protection",
    "namespace_isolation",
    "architectural_integrity"
  ]
}
```

**⚠️ WARNING:** Never disable Tier 0 protection!

---

### Tier 1: Working Memory

```json
"tier1": {
  "enabled": true,
  "database": "cortex-brain/tier1/conversations.db",
  "maxConversations": 20,        // FIFO queue limit
  "fifoMode": true,              // Auto-delete oldest
  "autoArchive": true,           // Archive before delete
  "archiveAfterDays": 30,        // Archive threshold
  "entityExtraction": {
    "enabled": true,
    "extractFiles": true,
    "extractClasses": true,
    "extractFunctions": true
  }
}
```

**Key Settings:**
- `maxConversations`: How many recent conversations to keep (default: 20)
- `fifoMode`: Automatically manage queue (recommended: true)
- `entityExtraction`: Track mentioned files/classes/functions

---

### Tier 2: Knowledge Graph

```json
"tier2": {
  "enabled": true,
  "database": "cortex-brain/tier2/knowledge-graph.db",
  "patternLearning": {
    "enabled": true,
    "minConfidence": 0.7,        // Pattern storage threshold
    "decayRate": 0.05,           // 5% decay per period
    "decayAfterDays": 90         // Unused pattern decay
  },
  "workflows": {
    "storageEnabled": true,
    "templatesPath": "cortex-brain/tier2/workflows/"
  }
}
```

**Key Settings:**
- `minConfidence`: Minimum confidence to store learned patterns
- `decayRate`: How quickly unused patterns lose confidence
- `workflows`: Enable workflow template storage

---

### Tier 3: Context Intelligence

```json
"tier3": {
  "enabled": true,
  "database": "cortex-brain/tier3/context-intelligence.db",
  "gitAnalysis": {
    "enabled": true,
    "maxCommits": 1000,
    "excludeBranches": ["temp/*", "experimental/*"]
  },
  "fileStability": {
    "enabled": true,
    "warnThreshold": 10         // Warn if >10 changes
  }
}
```

**Key Settings:**
- `gitAnalysis`: Analyze commit history for patterns
- `fileStability`: Track file modification frequency
- `warnThreshold`: Alert on high-churn files

---

### Agent Configuration

```json
"agents": {
  "enabled": true,
  "intentRouter": {
    "confidenceThreshold": 0.75   // Min confidence to route
  },
  "codeExecutor": {
    "enforceTDD": true,           // Require RED→GREEN→REFACTOR
    "maxFileChunkSize": 100       // Lines per chunk
  },
  "brainProtector": {
    "enabled": true,
    "blockSeverity": "blocked"    // Protection level
  }
}
```

**Key Settings:**
- `intentRouter.confidenceThreshold`: Lower = more aggressive routing
- `codeExecutor.enforceTDD`: Always enforce test-driven development
- `brainProtector.enabled`: Never disable this!

---

### Conversation Tracking

```json
"tracking": {
  "method": "ambient_daemon",     // or "python_cli" or "powershell"
  "ambientDaemon": {
    "enabled": true,
    "autoStart": true,
    "idleThresholdSeconds": 30,   // Capture after 30s idle
    "captureIntervalSeconds": 5   // Check every 5s
  }
}
```

**Tracking Methods:**
- `ambient_daemon`: Automatic background capture (recommended)
- `python_cli`: Manual `cortex remember` command
- `powershell`: Manual PowerShell script (Windows)

---

## Configuration Validation

### Validate Your Config

```bash
cortex config validate
```

**Expected Output:**
```
✅ Configuration is valid

Tier 0: ✅ Enabled, 6 protection layers active
Tier 1: ✅ Enabled, database exists
Tier 2: ✅ Enabled, pattern learning active
Tier 3: ✅ Enabled, git analysis configured
Agents: ✅ All 10 agents enabled
Tracking: ✅ Ambient daemon configured
```

---

## Common Configuration Scenarios

### Scenario 1: Low Memory Machine (<8GB RAM)

```json
"tier1": {
  "maxConversations": 10        // Reduce from 20
},
"performance": {
  "cacheSizeMB": 50,            // Reduce from 100
  "maxWorkerThreads": 2         // Reduce from 4
}
```

### Scenario 2: Disable Ambient Tracking (Use Manual)

```json
"tracking": {
  "method": "python_cli",
  "ambientDaemon": {
    "enabled": false
  }
}
```

### Scenario 3: Aggressive Pattern Learning

```json
"tier2": {
  "patternLearning": {
    "minConfidence": 0.6,       // Lower threshold
    "decayRate": 0.03,          // Slower decay
    "decayAfterDays": 120       // Longer retention
  }
}
```

---

## Configuration Files

### Primary Configuration
- **cortex.config.json** - Main configuration file (this reference)
- **cortex-brain/brain-protection-rules.yaml** - Tier 0 governance rules

### Example Configurations
- **cortex.config.example.json** - Example with comments
- **cortex.config.template.json** - Template for new installations

---

## Migration Guide

### v1.0 to v2.0

```bash
python scripts/migrate_config_v1_to_v2.py
```

**Changes:**
- Added `tier0` section (governance)
- Renamed `memory` → `tier1`
- Added `agents` section
- Added `tracking.ambientDaemon`

---

## Environment Variables

```bash
# Required
export CORTEX_ROOT="/path/to/CORTEX"
export CORTEX_BRAIN_PATH="$CORTEX_ROOT/cortex-brain"

# Optional
export CORTEX_CONFIG_PATH="$CORTEX_ROOT/cortex.config.json"
export CORTEX_LOG_LEVEL="INFO"
```

---

## Additional Resources

### Quick Guides
- **[Troubleshooting](../guides/troubleshooting.md)** - Config issues and solutions
- **[Best Practices](../guides/best-practices.md)** - Configuration recommendations
- **[Admin Guide](../guides/admin-guide.md)** - System administration

---

**For questions or issues, see:** [Troubleshooting Guide](../guides/troubleshooting.md)

**Version:** 1.0  
**Last Updated:** November 17, 2025  
**Generated by:** CORTEX Documentation Generator v1.0.0
