# Tool Categories

**Purpose:** Detailed documentation of CORTEX tool categories  
**Audience:** Developers, Architects  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Core Tools](#core-tools)
- [Analysis Tools](#analysis-tools)
- [Planning Tools](#planning-tools)
- [Governance Tools](#governance-tools)
- [Debug Tools](#debug-tools)
- [Discovery Tools](#discovery-tools)
- [Related Documents](#related-documents)

---

## Overview

CORTEX tools are organized into categories based on their primary function:

```python
class ToolCategory(Enum):
    """Tool category enumeration."""
    
    CORE = "core"           # Primary operations
    ANALYSIS = "analysis"   # Code intelligence
    PLANNING = "planning"   # Phase management
    GOVERNANCE = "governance"  # Compliance
    DEBUG = "debug"         # Troubleshooting
    DISCOVERY = "discovery" # Feature discovery
```

---

## Core Tools

Primary operations for implementing, fixing, and refactoring code.

### cortex_process_request

The main entry point for all operations.

```python
# Parameters
{
    "operation": "implement|fix|refactor|test",
    "target": "path/to/file.py",
    "request": "Description of what to do",
    "mode": "TDD|standard"
}

# Example
{
    "operation": "implement",
    "target": "src/auth/oauth.py",
    "request": "Add Google OAuth support",
    "mode": "TDD"
}
```

**Flow:**
1. Intent classification
2. LENS context enrichment
3. Governance validation
4. Orchestrator execution
5. Result delivery

### cortex_challenge

Generate decision challenges for verification.

```python
# Parameters
{
    "decision": "Description of decision to challenge",
    "context": {
        "alternatives": ["Option A", "Option B"],
        "constraints": ["Time", "Budget"]
    }
}

# Response
{
    "challenge": {
        "question": "Have you considered X?",
        "alternatives": [...],
        "risks": [...],
        "recommendation": "..."
    }
}
```

### cortex_total_recall

Feature discovery and implementation recall.

```python
# Parameters
{
    "query": "authentication implementation",
    "scope": "workspace|project|all"
}

# Response
{
    "features": [
        {
            "name": "OAuth Support",
            "location": "src/auth/oauth.py",
            "implemented": "2026-01-15",
            "related": [...]
        }
    ]
}
```

---

## Analysis Tools

Code intelligence and understanding tools.

### cortex_lens_analyze

Comprehensive LENS analysis.

```python
# Parameters
{
    "target": "src/",
    "analyzers": ["git", "ast", "comments", "patterns"],
    "depth": "shallow|deep"
}

# Response
{
    "git_insights": {...},
    "ast_analysis": {...},
    "comment_analysis": {...},
    "detected_patterns": [...]
}
```

### cortex_ast_analyze

AST-specific analysis.

```python
# Parameters
{
    "target": "src/service.py",
    "language": "python",
    "include": ["classes", "functions", "imports"]
}

# Response
{
    "classes": [
        {
            "name": "AuthService",
            "methods": ["login", "logout"],
            "line_start": 10,
            "line_end": 50
        }
    ],
    "functions": [...],
    "imports": [...]
}
```

### cortex_git_history

Git history analysis.

```python
# Parameters
{
    "path": "src/auth/",
    "hours": 24,
    "include_diffs": true
}

# Response
{
    "commits": [
        {
            "hash": "abc123",
            "author": "dev@example.com",
            "message": "Add OAuth support",
            "files": ["oauth.py", "config.py"]
        }
    ],
    "hot_files": ["oauth.py"],
    "active_authors": ["dev@example.com"]
}
```

### cortex_detect_duplicates

CORE-035 duplication detection.

```python
# Parameters
{
    "scope": "workspace|file",
    "threshold": 20,  # minimum lines
    "include_tests": false
}

# Response
{
    "duplicates": [
        {
            "locations": [
                {"file": "a.py", "lines": "10-30"},
                {"file": "b.py", "lines": "50-70"}
            ],
            "similarity": 0.95,
            "suggestion": "Extract to shared module"
        }
    ]
}
```

---

## Planning Tools

Phase lifecycle and roadmap management.

### cortex_plan_setup

Pre-implementation phase setup.

```python
# Parameters
{
    "phase_id": "phase-42",
    "metadata": {
        "title": "Authentication Refactor",
        "stages": 5
    }
}

# Response
{
    "setup_complete": true,
    "artifacts_created": ["phase-42.yaml"],
    "dashboard_updated": true
}
```

### cortex_plan_teardown

Post-completion cleanup.

```python
# Parameters
{
    "phase_id": "phase-42",
    "status": "completed|cancelled",
    "summary": "Successfully implemented OAuth"
}

# Response
{
    "teardown_complete": true,
    "artifacts_archived": ["phase-42.yaml"],
    "metrics_captured": true
}
```

### cortex_plan_resolve

Intelligent phase resolution.

```python
# Parameters
{
    "query": "What's the status of phase 42?"
}

# Response
{
    "phase": {
        "id": "phase-42",
        "title": "Authentication Refactor",
        "status": "in_progress",
        "progress": 0.6,
        "stages": [
            {"name": "Stage 1", "status": "completed"},
            {"name": "Stage 2", "status": "in_progress"}
        ]
    }
}
```

### cortex_plan_sync

Dashboard synchronization.

```python
# Parameters
{
    "force": false
}

# Response
{
    "synced": true,
    "phases_updated": 3,
    "dashboard_path": "cortex-registry/planning/dashboard.md"
}
```

---

## Governance Tools

Auditing and compliance tools.

### cortex_audit

Comprehensive codebase audit.

```python
# Parameters
{
    "scope": "workspace|directory",
    "path": "src/",
    "rules": ["CORE", "ARCH", "SECURITY"]
}

# Response
{
    "summary": {
        "passed": 45,
        "warnings": 10,
        "violations": 2
    },
    "violations": [
        {
            "rule": "CORE-008",
            "file": "untested.py",
            "message": "Missing tests"
        }
    ],
    "score": 0.87
}
```

### cortex_validate

Specific rule validation.

```python
# Parameters
{
    "target": "src/auth/",
    "rules": ["CORE-008", "CORE-011", "CORE-012"]
}

# Response
{
    "results": {
        "CORE-008": {"passed": true},
        "CORE-011": {"passed": false, "coverage": 0.85},
        "CORE-012": {"passed": true}
    }
}
```

### cortex_compliance_check

Standards compliance verification.

```python
# Parameters
{
    "standards": ["12-factor", "solid", "owasp"],
    "scope": "workspace"
}

# Response
{
    "compliance": {
        "12-factor": {"score": 0.9, "issues": [...]},
        "solid": {"score": 0.85, "issues": [...]},
        "owasp": {"score": 0.95, "issues": [...]}
    },
    "overall_score": 0.9
}
```

---

## Debug Tools

Troubleshooting and diagnostics.

### cortex_debug_inject

Inject debug markers.

```python
# Parameters
{
    "target": "src/problematic.py",
    "mode": "trace|log|breakpoint"
}

# Response
{
    "markers_injected": 5,
    "marker_ids": ["DBG-001", "DBG-002", ...]
}
```

### cortex_debug_cleanup

Remove debug markers.

```python
# Parameters
{
    "scope": "workspace|file",
    "target": "src/"
}

# Response
{
    "markers_removed": 5,
    "files_modified": ["problematic.py"]
}
```

### cortex_diagnose

System diagnostics.

```python
# Parameters
{
    "components": ["mcp", "lens", "orchestrators"]
}

# Response
{
    "health": {
        "mcp": {"status": "healthy", "latency_ms": 5},
        "lens": {"status": "healthy", "cache_hit_rate": 0.75},
        "orchestrators": {"status": "healthy", "count": 23}
    }
}
```

---

## Discovery Tools

Feature and capability discovery.

### cortex_tools_catalog

List available tools.

```python
# Parameters
{
    "category": "analysis|all",
    "include_deprecated": false
}

# Response
{
    "tools": [
        {
            "name": "cortex_lens_analyze",
            "category": "analysis",
            "description": "...",
            "version": "1.0.0"
        }
    ]
}
```

### cortex_onboard_repository

Repository onboarding.

```python
# Parameters
{
    "path": "/path/to/repo",
    "scan_security": true,
    "extract_knowledge": true
}

# Response
{
    "project_type": "python",
    "frameworks": ["fastapi", "pytest"],
    "security_findings": [...],
    "knowledge_extracted": true
}
```

### cortex_describe_tool

Get tool documentation.

```python
# Parameters
{
    "tool_name": "cortex_lens_analyze"
}

# Response
{
    "name": "cortex_lens_analyze",
    "description": "Perform comprehensive code analysis",
    "parameters": [...],
    "examples": [...],
    "related_tools": [...]
}
```

---

## Related Documents

- [Toolkit Overview](overview.md) — Introduction
- [Tool Registry](tool-registry.md) — Registration
- [Developer Guide](developer-guide.md) — Creating tools

---

*Part of CORTEX Architecture Documentation*
