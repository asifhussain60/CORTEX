# CORTEX Configuration Reference

**Purpose:** Complete reference for cortex.config.json settings and advanced configuration  
**Audience:** Developers, system administrators, power users  
**Version:** 2.0 (Full Module)  
**Status:** Production Ready

---

## 📋 Overview

CORTEX is configured through `cortex.config.json` in your project root. This file controls all memory tiers, agent behavior, tracking methods, and machine-specific settings.

**Configuration Hierarchy:**
```
cortex.config.json (main configuration)
├── tier0: Governance rules (references YAML files)
├── tier1: Working memory settings
├── tier2: Knowledge graph settings
├── tier3: Context intelligence settings
├── agents: Agent system configuration
├── tracking: Conversation capture settings
└── machine: Machine-specific paths and settings
```

---

## 🔧 Full Configuration Schema

### Complete cortex.config.json Example

```json
{
  "version": "2.0",
  "name": "CORTEX",
  "description": "Memory and context system for GitHub Copilot",
  
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
  },
  
  "tier1": {
    "enabled": true,
    "database": "cortex-brain/tier1/conversations.db",
    "maxConversations": 20,
    "fifoMode": true,
    "autoArchive": true,
    "archivePath": "cortex-brain/tier1/archive/",
    "archiveAfterDays": 30,
    "entityExtraction": {
      "enabled": true,
      "extractFiles": true,
      "extractClasses": true,
      "extractFunctions": true,
      "extractVariables": false
    },
    "storage": {
      "maxSizeMB": 50,
      "compressionEnabled": true
    }
  },
  
  "tier2": {
    "enabled": true,
    "database": "cortex-brain/tier2/knowledge-graph.db",
    "patternLearning": {
      "enabled": true,
      "minConfidence": 0.7,
      "decayRate": 0.05,
      "decayAfterDays": 90
    },
    "workflows": {
      "storageEnabled": true,
      "templatesPath": "cortex-brain/tier2/workflows/"
    },
    "fileRelationships": {
      "enabled": true,
      "trackImports": true,
      "trackUsages": true,
      "trackTests": true
    }
  },
  
  "tier3": {
    "enabled": true,
    "database": "cortex-brain/tier3/context-intelligence.db",
    "gitAnalysis": {
      "enabled": true,
      "maxCommits": 1000,
      "excludeBranches": ["temp/*", "experimental/*"]
    },
    "sessionAnalytics": {
      "enabled": true,
      "trackWorkSessions": true,
      "idleThresholdMinutes": 15
    },
    "fileStability": {
      "enabled": true,
      "calculateChurn": true,
      "warnThreshold": 10
    },
    "codeHealth": {
      "enabled": true,
      "trackComplexity": true,
      "trackCoverage": true
    }
  },
  
  "agents": {
    "enabled": true,
    "intentRouter": {
      "enabled": true,
      "confidenceThreshold": 0.75,
      "fallbackToAmbiguityHandler": true
    },
    "workPlanner": {
      "enabled": true,
      "autoCreatePlans": true,
      "minComplexityForPlan": "medium"
    },
    "codeExecutor": {
      "enabled": true,
      "enforceTDD": true,
      "maxFileChunkSize": 100
    },
    "testGenerator": {
      "enabled": true,
      "framework": "auto-detect",
      "coverageTarget": 80
    },
    "errorCorrector": {
      "enabled": true,
      "preventWrongFile": true,
      "useTier2History": true
    },
    "healthValidator": {
      "enabled": true,
      "enforceDoD": true,
      "zeroWarnings": true
    },
    "screenshotAnalyzer": {
      "enabled": true,
      "ocrEngine": "tesseract"
    },
    "changeGovernor": {
      "enabled": true,
      "enforceApplicationSeparation": true,
      "warnOnArchitecturalViolations": true
    },
    "brainProtector": {
      "enabled": true,
      "blockSeverity": "blocked",
      "challengeSeverity": "warning"
    },
    "commitHandler": {
      "enabled": true,
      "enforceSemanticCommits": true,
      "autoSignOff": false
    }
  },
  
  "tracking": {
    "method": "ambient_daemon",
    "powerShellCapture": {
      "enabled": false,
      "scriptPath": "scripts/capture-copilot-chat.ps1"
    },
    "pythonCLI": {
      "enabled": false,
      "commandAlias": "cortex remember"
    },
    "ambientDaemon": {
      "enabled": true,
      "autoStart": true,
      "idleThresholdSeconds": 30,
      "captureIntervalSeconds": 5,
      "maxConversationSizeKB": 500,
      "excludedPatterns": [
        "test conversation",
        "ignore this"
      ]
    }
  },
  
  "machine": {
    "id": "DESKTOP-PRIMARY",
    "workspacePath": "/path/to/projects\\CORTEX",
    "pythonPath": "python",
    "gitPath": "git",
    "vscodePath": "code"
  },
  
  "logging": {
    "level": "INFO",
    "logPath": "logs/",
    "rotateDaily": true,
    "maxLogSizeMB": 10
  },
  
  "performance": {
    "cacheEnabled": true,
    "cacheSizeMB": 100,
    "parallelProcessing": true,
    "maxWorkerThreads": 4
  },
  
  "security": {
    "encryptionEnabled": false,
    "secretsPath": ".env",
    "preventCommitSecrets": true
  }
}
```

---

## 🛡️ Tier 0: Governance Rules

**Purpose:** Immutable rules that protect CORTEX architectural integrity

```json
"tier0": {
  "enabled": true,
  "governance_rules": "cortex-brain/brain-protection-rules.yaml",
  "immutable": true,
  "protection_layers": [...]
}
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Tier 0 protection (NEVER disable) |
| `governance_rules` | string | `brain-protection-rules.yaml` | Path to YAML rules file |
| `immutable` | boolean | `true` | Rules cannot be changed at runtime |
| `protection_layers` | array | 6 layers | List of active protection layers |

### Protection Layers

```json
"protection_layers": [
  "instinct_immutability",        // Tier 0 rules cannot be bypassed
  "critical_path_protection",     // Core CORTEX files protected
  "application_separation",       // App code stays out of CORTEX
  "brain_state_protection",       // Memory files not committed to git
  "namespace_isolation",          // Scope boundaries enforced
  "architectural_integrity"       // Design principles maintained
]
```

**DO NOT disable protection layers unless you absolutely know what you're doing.**

---

## 🧠 Tier 1: Working Memory

**Purpose:** Short-term conversation memory (last 20 conversations)

```json
"tier1": {
  "enabled": true,
  "database": "cortex-brain/tier1/conversations.db",
  "maxConversations": 20,
  "fifoMode": true,
  "autoArchive": true,
  ...
}
```

### Core Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Tier 1 memory |
| `database` | string | `conversations.db` | SQLite database path |
| `maxConversations` | integer | `20` | FIFO queue limit (keep most recent N) |
| `fifoMode` | boolean | `true` | Automatically delete oldest when limit reached |
| `autoArchive` | boolean | `true` | Archive before deletion (vs. permanent delete) |
| `archivePath` | string | `tier1/archive/` | Where to store archived conversations |
| `archiveAfterDays` | integer | `30` | Archive conversations older than N days |

### Entity Extraction

```json
"entityExtraction": {
  "enabled": true,
  "extractFiles": true,
  "extractClasses": true,
  "extractFunctions": true,
  "extractVariables": false
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable entity extraction from conversations |
| `extractFiles` | boolean | `true` | Track file mentions (e.g., "AuthService.cs") |
| `extractClasses` | boolean | `true` | Track class names |
| `extractFunctions` | boolean | `true` | Track function/method names |
| `extractVariables` | boolean | `false` | Track variable names (often noisy) |

### Storage

```json
"storage": {
  "maxSizeMB": 50,
  "compressionEnabled": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `maxSizeMB` | integer | `50` | Maximum Tier 1 database size (triggers cleanup) |
| `compressionEnabled` | boolean | `true` | Compress archived conversations |

---

## 📊 Tier 2: Knowledge Graph

**Purpose:** Long-term pattern learning and workflow templates

```json
"tier2": {
  "enabled": true,
  "database": "cortex-brain/tier2/knowledge-graph.db",
  "patternLearning": {...},
  "workflows": {...},
  "fileRelationships": {...}
}
```

### Pattern Learning

```json
"patternLearning": {
  "enabled": true,
  "minConfidence": 0.7,
  "decayRate": 0.05,
  "decayAfterDays": 90
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Learn from past conversations |
| `minConfidence` | float | `0.7` | Minimum confidence to store pattern (0.0-1.0) |
| `decayRate` | float | `0.05` | Pattern confidence decay per period (0.0-1.0) |
| `decayAfterDays` | integer | `90` | Start decaying patterns after N days unused |

**Example:** If you frequently ask "add button" → EXECUTE intent, CORTEX learns this pattern. After 90 days without similar requests, confidence slowly decays from 0.92 → 0.87 → 0.82...

### Workflows

```json
"workflows": {
  "storageEnabled": true,
  "templatesPath": "cortex-brain/tier2/workflows/"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `storageEnabled` | boolean | `true` | Store successful workflows as templates |
| `templatesPath` | string | `tier2/workflows/` | Where to save workflow YAML files |

**Example Workflow Storage:**
```
cortex-brain/tier2/workflows/
  ├── feature_development.yaml
  ├── bug_fix.yaml
  └── refactoring.yaml
```

### File Relationships

```json
"fileRelationships": {
  "enabled": true,
  "trackImports": true,
  "trackUsages": true,
  "trackTests": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Track relationships between files |
| `trackImports` | boolean | `true` | Track import/using statements |
| `trackUsages` | boolean | `true` | Track where classes/functions are used |
| `trackTests` | boolean | `true` | Link production code to test files |

---

## 🎯 Tier 3: Context Intelligence

**Purpose:** Git analysis, file stability, session analytics

```json
"tier3": {
  "enabled": true,
  "database": "cortex-brain/tier3/context-intelligence.db",
  "gitAnalysis": {...},
  "sessionAnalytics": {...},
  "fileStability": {...},
  "codeHealth": {...}
}
```

### Git Analysis

```json
"gitAnalysis": {
  "enabled": true,
  "maxCommits": 1000,
  "excludeBranches": ["temp/*", "experimental/*"]
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Analyze git commit history |
| `maxCommits` | integer | `1000` | Analyze last N commits (performance limit) |
| `excludeBranches` | array | `[]` | Branch patterns to ignore (glob syntax) |

**Example:** Analyze last 1000 commits, but skip anything in `temp/` or `experimental/` branches.

### Session Analytics

```json
"sessionAnalytics": {
  "enabled": true,
  "trackWorkSessions": true,
  "idleThresholdMinutes": 15
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Track coding sessions (time-on-task) |
| `trackWorkSessions` | boolean | `true` | Group conversations into work sessions |
| `idleThresholdMinutes` | integer | `15` | Idle time before session ends |

**Example:** If you stop coding for 15 minutes, CORTEX closes the current session and starts a new one when you resume.

### File Stability

```json
"fileStability": {
  "enabled": true,
  "calculateChurn": true,
  "warnThreshold": 10
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Track file modification frequency |
| `calculateChurn` | boolean | `true` | Calculate lines added/deleted per file |
| `warnThreshold` | integer | `10` | Warn if file modified N+ times in short period |

**Example:** If `AuthService.cs` is modified 10 times in one day, CORTEX warns: "⚠️ High churn detected. Consider refactoring."

### Code Health

```json
"codeHealth": {
  "enabled": true,
  "trackComplexity": true,
  "trackCoverage": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Monitor code health metrics |
| `trackComplexity` | boolean | `true` | Track cyclomatic complexity |
| `trackCoverage` | boolean | `true` | Track test coverage percentage |

---

## 🤖 Agents Configuration

**Purpose:** Configure the 10 specialist agents

```json
"agents": {
  "enabled": true,
  "intentRouter": {...},
  "workPlanner": {...},
  "codeExecutor": {...},
  ...
}
```

### Intent Router

```json
"intentRouter": {
  "enabled": true,
  "confidenceThreshold": 0.75,
  "fallbackToAmbiguityHandler": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable intent detection |
| `confidenceThreshold` | float | `0.75` | Minimum confidence to route (0.0-1.0) |
| `fallbackToAmbiguityHandler` | boolean | `true` | Ask user if confidence < threshold |

**Example:** Request "make it purple" matches EXECUTE with 0.88 confidence (> 0.75) → routes to Code Executor. Request "do something" matches with 0.40 confidence (< 0.75) → asks user for clarification.

### Work Planner

```json
"workPlanner": {
  "enabled": true,
  "autoCreatePlans": true,
  "minComplexityForPlan": "medium"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Work Planner agent |
| `autoCreatePlans` | boolean | `true` | Automatically create plans for complex tasks |
| `minComplexityForPlan` | string | `"medium"` | Complexity threshold: `"low"`, `"medium"`, `"high"` |

**Example:** "Add authentication" = high complexity → auto-creates plan. "Make button purple" = low complexity → skips planning.

### Code Executor

```json
"codeExecutor": {
  "enabled": true,
  "enforceTDD": true,
  "maxFileChunkSize": 100
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Code Executor agent |
| `enforceTDD` | boolean | `true` | Require RED → GREEN → REFACTOR workflow |
| `maxFileChunkSize` | integer | `100` | Max lines to create at once (prevents errors) |

### Test Generator

```json
"testGenerator": {
  "enabled": true,
  "framework": "auto-detect",
  "coverageTarget": 80
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Test Generator agent |
| `framework` | string | `"auto-detect"` | Test framework: `"auto-detect"`, `"nunit"`, `"xunit"`, `"pytest"`, etc. |
| `coverageTarget` | integer | `80` | Target test coverage percentage |

### Error Corrector

```json
"errorCorrector": {
  "enabled": true,
  "preventWrongFile": true,
  "useTier2History": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Error Corrector agent |
| `preventWrongFile` | boolean | `true` | Use Tier 2 to prevent "wrong file" mistakes |
| `useTier2History` | boolean | `true` | Learn from past corrections |

### Health Validator

```json
"healthValidator": {
  "enabled": true,
  "enforceDoD": true,
  "zeroWarnings": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Health Validator agent |
| `enforceDoD` | boolean | `true` | Enforce Definition of Done (all tests pass, zero errors) |
| `zeroWarnings` | boolean | `true` | Treat warnings as errors (strict mode) |

**Set `zeroWarnings: false` if you want to allow warnings.**

### Screenshot Analyzer

```json
"screenshotAnalyzer": {
  "enabled": true,
  "ocrEngine": "tesseract"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Screenshot Analyzer agent |
| `ocrEngine` | string | `"tesseract"` | OCR engine: `"tesseract"`, `"azure"`, `"google"` |

### Change Governor

```json
"changeGovernor": {
  "enabled": true,
  "enforceApplicationSeparation": true,
  "warnOnArchitecturalViolations": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Change Governor agent |
| `enforceApplicationSeparation` | boolean | `true` | Keep app code out of CORTEX core |
| `warnOnArchitecturalViolations` | boolean | `true` | Alert when architectural principles violated |

### Brain Protector

```json
"brainProtector": {
  "enabled": true,
  "blockSeverity": "blocked",
  "challengeSeverity": "warning"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Brain Protector agent |
| `blockSeverity` | string | `"blocked"` | Severity for blocking actions: `"blocked"`, `"warning"`, `"allow"` |
| `challengeSeverity` | string | `"warning"` | Severity for challenging (not blocking): `"warning"`, `"info"` |

### Commit Handler

```json
"commitHandler": {
  "enabled": true,
  "enforceSemanticCommits": true,
  "autoSignOff": false
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable Commit Handler agent |
| `enforceSemanticCommits` | boolean | `true` | Require `feat(scope): subject` format |
| `autoSignOff` | boolean | `false` | Add `Signed-off-by` to commits |

---

## 📡 Conversation Tracking

**Purpose:** Configure how conversations are captured

```json
"tracking": {
  "method": "ambient_daemon",
  "powerShellCapture": {...},
  "pythonCLI": {...},
  "ambientDaemon": {...}
}
```

### Primary Method

```json
"tracking": {
  "method": "ambient_daemon"
}
```

| Value | Description |
|-------|-------------|
| `"ambient_daemon"` | Automatic background capture (recommended) |
| `"python_cli"` | Manual `cortex remember` command |
| `"powershell"` | Manual PowerShell script execution |
| `"disabled"` | No tracking (NOT RECOMMENDED) |

### PowerShell Capture

```json
"powerShellCapture": {
  "enabled": false,
  "scriptPath": "scripts/capture-copilot-chat.ps1"
}
```

### Python CLI

```json
"pythonCLI": {
  "enabled": false,
  "commandAlias": "cortex remember"
}
```

### Ambient Daemon (Recommended)

```json
"ambientDaemon": {
  "enabled": true,
  "autoStart": true,
  "idleThresholdSeconds": 30,
  "captureIntervalSeconds": 5,
  "maxConversationSizeKB": 500,
  "excludedPatterns": [
    "test conversation",
    "ignore this"
  ]
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable ambient daemon |
| `autoStart` | boolean | `true` | Start with VS Code (requires tasks.json) |
| `idleThresholdSeconds` | integer | `30` | Capture after N seconds of idle time |
| `captureIntervalSeconds` | integer | `5` | Check for activity every N seconds |
| `maxConversationSizeKB` | integer | `500` | Skip conversations larger than N KB |
| `excludedPatterns` | array | `[]` | Don't capture conversations containing these phrases |

---

## 💻 Machine-Specific Settings

**Purpose:** Configure paths and settings unique to each machine

```json
"machine": {
  "id": "DESKTOP-PRIMARY",
  "workspacePath": "/path/to/projects\\CORTEX",
  "pythonPath": "python",
  "gitPath": "git",
  "vscodePath": "code"
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `id` | string | `"MACHINE-1"` | Unique machine identifier |
| `workspacePath` | string | (auto-detected) | Absolute path to CORTEX workspace |
| `pythonPath` | string | `"python"` | Python executable path or command |
| `gitPath` | string | `"git"` | Git executable path or command |
| `vscodePath` | string | `"code"` | VS Code executable path or command |

**Multi-Machine Setup:**
```json
// Machine 1 (Windows Desktop)
"machine": {
  "id": "DESKTOP-PRIMARY",
  "workspacePath": "/path/to/projects\\CORTEX",
  "pythonPath": "C:/Python39\\python.exe"
}

// Machine 2 (Linux Laptop)
"machine": {
  "id": "LAPTOP-LINUX",
  "workspacePath": "/home/user/projects/cortex",
  "pythonPath": "/usr/bin/python3"
}
```

---

## 📝 Logging

```json
"logging": {
  "level": "INFO",
  "logPath": "logs/",
  "rotateDaily": true,
  "maxLogSizeMB": 10
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `level` | string | `"INFO"` | Log level: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"` |
| `logPath` | string | `"logs/"` | Directory for log files |
| `rotateDaily` | boolean | `true` | Create new log file each day |
| `maxLogSizeMB` | integer | `10` | Max log file size before rotation |

**Log Levels:**
- `DEBUG`: Verbose output (all operations)
- `INFO`: Normal operations (default)
- `WARNING`: Potential issues
- `ERROR`: Errors only

---

## ⚡ Performance

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
| `cacheEnabled` | boolean | `true` | Enable in-memory caching |
| `cacheSizeMB` | integer | `100` | Max cache size in memory |
| `parallelProcessing` | boolean | `true` | Use multiple threads for operations |
| `maxWorkerThreads` | integer | `4` | Max parallel worker threads |

**Performance Tuning:**
- **Low RAM (< 8GB):** Set `cacheSizeMB: 50`, `maxWorkerThreads: 2`
- **High RAM (16GB+):** Set `cacheSizeMB: 200`, `maxWorkerThreads: 8`
- **SSD:** Keep `parallelProcessing: true`
- **HDD:** Consider `parallelProcessing: false` to reduce disk thrashing

---

## 🔒 Security

```json
"security": {
  "encryptionEnabled": false,
  "secretsPath": ".env",
  "preventCommitSecrets": true
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `encryptionEnabled` | boolean | `false` | Encrypt conversation database (requires setup) |
| `secretsPath` | string | `".env"` | Path to secrets file (excluded from git) |
| `preventCommitSecrets` | boolean | `true` | Block commits containing API keys/secrets |

**Encryption Setup:**
```bash
# Generate encryption key
python scripts/security/generate_key.py

# Enable encryption
cortex encrypt --enable
```

---

## 🛠️ Configuration Validation

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

Warnings:
  ⚠️  Tier 1 maxConversations is low (10). Consider 20 for better context.
  ⚠️  Encryption is disabled. Conversations stored in plaintext.
```

### Export Configuration

```bash
cortex config export --output my-config-backup.json
```

### Import Configuration

```bash
cortex config import --input my-config-backup.json
```

---

## 🔄 Migration: v1.0 to v2.0

If upgrading from CORTEX 1.0:

```bash
python scripts/migrate_config_v1_to_v2.py
```

**Changes in v2.0:**
- Added `tier0` section (governance rules)
- Added `agents` section (10 specialist agents)
- Added `tracking.ambientDaemon` (automatic capture)
- Renamed `memory` → `tier1`, `patterns` → `tier2`, `context` → `tier3`

---

## 📚 For More Information

**Related Documentation:**
- **Setup Guide:** `#file:prompts/shared/setup-guide.md` (Initial installation)
- **Technical Reference:** `#file:prompts/shared/technical-reference.md` (API details)
- **Tracking Guide:** `#file:prompts/shared/tracking-guide.md` (Conversation capture setup)
- **Agents Guide:** `#file:prompts/shared/agents-guide.md` (Agent system configuration)

---

**Version:** 2.0  
**Last Updated:** November 8, 2025  
**Phase:** 3.7 Complete - Full Modular Architecture  
**Configuration Schema:** v2.0
