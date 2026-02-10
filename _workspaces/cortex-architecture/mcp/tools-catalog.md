# MCP Tools Catalog

**Purpose:** Complete catalog of CORTEX MCP tools  
**Audience:** Developers, Integrators  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Core Tools](#core-tools)
- [Analysis Tools](#analysis-tools)
- [Planning Tools](#planning-tools)
- [Governance Tools](#governance-tools)
- [Discovery Tools](#discovery-tools)
- [Debug Tools](#debug-tools)
- [Related Documents](#related-documents)

---

## Overview

CORTEX exposes **35+ MCP tools** organized by category. Each tool follows a consistent naming convention: `cortex_{category}_{action}`.

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOOLS BY CATEGORY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Core (10)       │  Analysis (8)    │  Planning (5)             │
│  ─────────────── │  ─────────────── │  ───────────────          │
│  process_request │  lens_analyze    │  plan_setup               │
│  challenge       │  ast_analyze     │  plan_teardown            │
│  total_recall    │  git_history     │  plan_resolve             │
│  implement       │  detect_dupes    │  plan_sync                │
│  fix             │  pattern_detect  │  plan_status              │
│  refactor        │  comment_analyze │                           │
│  test            │  config_analyze  │                           │
│  validate        │  api_analyze     │                           │
│  format          │                  │                           │
│  lint            │                  │                           │
│                                                                  │
│  Governance (4)  │  Discovery (5)   │  Debug (3)                │
│  ─────────────── │  ─────────────── │  ───────────────          │
│  audit           │  tools_catalog   │  debug_inject             │
│  compliance      │  describe_tool   │  debug_cleanup            │
│  security_scan   │  onboard_repo    │  diagnose                 │
│  rule_check      │  discover_feats  │                           │
│                  │  search_code     │                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Tools

### cortex_process_request

Main entry point for all operations.

```json
{
    "name": "cortex_process_request",
    "description": "Process an implementation, fix, or refactor request",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["implement", "fix", "refactor", "test"],
                "description": "Type of operation"
            },
            "target": {
                "type": "string",
                "description": "Target file or feature"
            },
            "request": {
                "type": "string",
                "description": "Description of what to do"
            },
            "mode": {
                "type": "string",
                "enum": ["TDD", "standard"],
                "default": "TDD"
            }
        },
        "required": ["operation", "request"]
    }
}
```

**Example:**
```json
{
    "name": "cortex_process_request",
    "arguments": {
        "operation": "implement",
        "target": "src/auth/oauth.py",
        "request": "Add Google OAuth support with PKCE flow",
        "mode": "TDD"
    }
}
```

### cortex_challenge

Generate decision challenges.

```json
{
    "name": "cortex_challenge",
    "description": "Generate challenges for a design decision",
    "inputSchema": {
        "type": "object",
        "properties": {
            "decision": {
                "type": "string",
                "description": "The decision to challenge"
            },
            "context": {
                "type": "object",
                "description": "Additional context"
            }
        },
        "required": ["decision"]
    }
}
```

### cortex_total_recall

Feature discovery and implementation recall.

```json
{
    "name": "cortex_total_recall",
    "description": "Discover features and implementations",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "scope": {
                "type": "string",
                "enum": ["workspace", "project", "all"],
                "default": "workspace"
            }
        },
        "required": ["query"]
    }
}
```

---

## Analysis Tools

### cortex_lens_analyze

Comprehensive LENS analysis.

```json
{
    "name": "cortex_lens_analyze",
    "description": "Perform comprehensive code analysis using LENS",
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "File or directory to analyze"
            },
            "analyzers": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["git", "ast", "comments", "patterns", "config", "api", "all"]
                },
                "default": ["all"]
            },
            "depth": {
                "type": "string",
                "enum": ["shallow", "deep"],
                "default": "deep"
            }
        },
        "required": ["target"]
    }
}
```

**Example:**
```json
{
    "name": "cortex_lens_analyze",
    "arguments": {
        "target": "src/auth/",
        "analyzers": ["git", "ast", "patterns"],
        "depth": "deep"
    }
}
```

### cortex_ast_analyze

AST-specific analysis.

```json
{
    "name": "cortex_ast_analyze",
    "description": "Analyze code structure using AST",
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "File to analyze"
            },
            "language": {
                "type": "string",
                "enum": ["python", "typescript", "java", "csharp"],
                "default": "python"
            },
            "include": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["classes", "functions", "imports", "decorators", "types"]
                },
                "default": ["classes", "functions"]
            }
        },
        "required": ["target"]
    }
}
```

### cortex_git_history

Git history analysis.

```json
{
    "name": "cortex_git_history",
    "description": "Analyze git history for context",
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File or directory path"
            },
            "hours": {
                "type": "number",
                "default": 24,
                "description": "Hours of history"
            },
            "include_diffs": {
                "type": "boolean",
                "default": false
            }
        },
        "required": ["path"]
    }
}
```

### cortex_detect_duplicates

CORE-035 duplication detection.

```json
{
    "name": "cortex_detect_duplicates",
    "description": "Detect code duplication (CORE-035)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "scope": {
                "type": "string",
                "enum": ["workspace", "file", "directory"],
                "default": "workspace"
            },
            "threshold": {
                "type": "number",
                "default": 20,
                "description": "Minimum lines for duplicate detection"
            },
            "include_tests": {
                "type": "boolean",
                "default": false
            }
        }
    }
}
```

---

## Planning Tools

### cortex_plan_setup

Pre-implementation phase setup.

```json
{
    "name": "cortex_plan_setup",
    "description": "Set up a new implementation phase",
    "inputSchema": {
        "type": "object",
        "properties": {
            "phase_id": {
                "type": "string",
                "description": "Phase identifier"
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "stages": {"type": "number"},
                    "priority": {"type": "string", "enum": ["P0", "P1", "P2"]}
                }
            }
        },
        "required": ["phase_id"]
    }
}
```

### cortex_plan_resolve

Intelligent phase resolution.

```json
{
    "name": "cortex_plan_resolve",
    "description": "Resolve and query phase information",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Phase query (e.g., 'phase 42 status')"
            }
        },
        "required": ["query"]
    }
}
```

### cortex_plan_sync

Dashboard synchronization.

```json
{
    "name": "cortex_plan_sync",
    "description": "Synchronize planning dashboard",
    "inputSchema": {
        "type": "object",
        "properties": {
            "force": {
                "type": "boolean",
                "default": false,
                "description": "Force full refresh"
            }
        }
    }
}
```

---

## Governance Tools

### cortex_audit

Codebase health audit.

```json
{
    "name": "cortex_audit",
    "description": "Perform comprehensive codebase audit",
    "inputSchema": {
        "type": "object",
        "properties": {
            "scope": {
                "type": "string",
                "enum": ["workspace", "directory", "file"],
                "default": "workspace"
            },
            "path": {
                "type": "string",
                "description": "Path for directory/file scope"
            },
            "rules": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["CORE", "ARCH", "LENS", "SECURITY", "ALL"]
                },
                "default": ["ALL"]
            }
        }
    }
}
```

### cortex_compliance_check

Standards compliance verification.

```json
{
    "name": "cortex_compliance_check",
    "description": "Check compliance with standards",
    "inputSchema": {
        "type": "object",
        "properties": {
            "standards": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["12-factor", "solid", "owasp", "clean-code"]
                }
            },
            "scope": {
                "type": "string",
                "default": "workspace"
            }
        },
        "required": ["standards"]
    }
}
```

### cortex_security_scan

Security vulnerability scanning.

```json
{
    "name": "cortex_security_scan",
    "description": "Scan for security vulnerabilities",
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target path"
            },
            "checks": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["secrets", "dependencies", "injection", "auth"]
                },
                "default": ["secrets", "dependencies"]
            }
        },
        "required": ["target"]
    }
}
```

---

## Discovery Tools

### cortex_tools_catalog

List available tools.

```json
{
    "name": "cortex_tools_catalog",
    "description": "List all available CORTEX tools",
    "inputSchema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["core", "analysis", "planning", "governance", "discovery", "debug", "all"],
                "default": "all"
            },
            "include_deprecated": {
                "type": "boolean",
                "default": false
            }
        }
    }
}
```

### cortex_onboard_repository

Repository onboarding.

```json
{
    "name": "cortex_onboard_repository",
    "description": "Onboard a new repository",
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Repository path"
            },
            "scan_security": {
                "type": "boolean",
                "default": true
            },
            "extract_knowledge": {
                "type": "boolean",
                "default": true
            }
        },
        "required": ["path"]
    }
}
```

---

## Debug Tools

### cortex_debug_inject

Inject debug markers.

```json
{
    "name": "cortex_debug_inject",
    "description": "Inject debug markers into code",
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target file"
            },
            "mode": {
                "type": "string",
                "enum": ["trace", "log", "breakpoint"],
                "default": "log"
            }
        },
        "required": ["target"]
    }
}
```

### cortex_debug_cleanup

Remove debug markers.

```json
{
    "name": "cortex_debug_cleanup",
    "description": "Remove all debug markers",
    "inputSchema": {
        "type": "object",
        "properties": {
            "scope": {
                "type": "string",
                "enum": ["workspace", "file"],
                "default": "workspace"
            },
            "target": {
                "type": "string",
                "description": "Target for file scope"
            }
        }
    }
}
```

---

## Related Documents

- [MCP Overview](overview.md) — Introduction
- [MCP Protocol](protocol.md) — Protocol details
- [Integration Guide](integration.md) — Client integration

---

*Part of CORTEX Architecture Documentation*
