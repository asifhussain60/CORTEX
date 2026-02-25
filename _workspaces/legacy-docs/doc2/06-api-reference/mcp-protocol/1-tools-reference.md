# MCP Tools Reference

**Last Updated:** 2026-01-20  
**Status:** 14 tools registered as stubs (Phase B registry work)  
**Phase Status:** Awaiting Phase B (Create registry + implement tool logic)

---

## Overview

CORTEX exposes 14 MCP tools through a centralized registry that enables:
- **Tool discovery:** Enumerate all available tools by category
- **Tool metadata:** Inspect tool signatures, parameters, authentication requirements
- **Tool execution:** Call tools with automatic parameter validation
- **Tool categorization:** Organize tools by governance, orchestration, knowledge, utility
- **Tool authentication:** Enforce auth requirements for sensitive tools

### Tool Categories

```
14 Total Tools
├─ Governance (5 tools) ──── governance/
│  ├─ Query governance state
│  ├─ Validate compliance
│  ├─ Execute governance action
│  ├─ Analyze governance effectiveness
│  └─ Generate governance reports
│
├─ Orchestration (4 tools) ── orchestration/
│  ├─ Orchestrator status
│  ├─ Monitor orchestration metrics
│  ├─ Optimize orchestration
│  └─ Diagnose issues
│
├─ Knowledge (3 tools) ────── knowledge/
│  ├─ Search knowledge graph
│  ├─ Analyze knowledge base
│  └─ Generate knowledge recommendations
│
└─ Utility (2 tools) ──────── utility/
   ├─ Echo test (connectivity)
   └─ Transform data (format conversion)
```

---

## Governance Tools (5)

### 1. Query Governance State

**Tool ID:** `query-governance`  
**Category:** Governance  
**Requires Auth:** ✅ YES  
**Status:** Stub (returns mock data)

**Description:**
Query the current governance state and view which rules apply to a given context.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `context` | string | ✅ | Governance context type: `conversation`, `domain`, `operation`, or custom |
| `rule_id` | string | ❌ | Optional: Query specific rule by ID (e.g., `CORE-001`) |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "query-governance",
    "arguments": {
      "context": "conversation",
      "rule_id": "CORE-001"
    }
  },
  "id": 100
}
```

**Example Response (Stub):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"context\": \"conversation\",\n  \"rule_id\": \"CORE-001\",\n  \"name\": \"No Unvetted External Data\",\n  \"status\": \"ACTIVE\",\n  \"tier\": 0,\n  \"description\": \"All external data sources must be vetted before use\"\n}"
      }
    ]
  },
  "id": 100
}
```

**Real Implementation (Phase 2):**
Will query `cortex_brain/state/governance.db` to return:
- Active rules in context
- Rule precedence/tier
- Applicability conditions
- Last evaluation timestamp
- Affected operations

---

### 2. Validate Compliance

**Tool ID:** `validate-compliance`  
**Category:** Governance  
**Requires Auth:** ✅ YES  
**Status:** Stub (returns mock data)

**Description:**
Check if a proposed action complies with governance rules.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | string | ✅ | Action to validate (e.g., `respond_to_user`, `access_credential`) |
| `context` | object | ✅ | Context data: `{domain, user_id, operation, data}` |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "validate-compliance",
    "arguments": {
      "action": "respond_to_user",
      "context": {
        "domain": "healthcare",
        "user_id": "user-123",
        "operation": "diagnosis_query",
        "data": "patient_age=45"
      }
    }
  },
  "id": 101
}
```

**Example Response (Stub):**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"compliant\": true,\n  \"violations\": [],\n  \"warnings\": [],\n  \"rules_applied\": [\"CORE-001\", \"CORE-005\"],\n  \"decision\": \"APPROVED\"\n}"
      }
    ]
  },
  "id": 101
}
```

**Real Implementation (Phase 2):**
Will:
- Evaluate all applicable governance rules
- Check rule preconditions against context
- Return compliance status (APPROVED/REJECTED/NEEDS_REVIEW)
- List violated rules with explanations
- Suggest remediation if violations found

---

### 3. Execute Governance Action

**Tool ID:** `execute-governance`  
**Category:** Governance  
**Requires Auth:** ✅ YES  
**Status:** Stub (returns mock data)

**Description:**
Execute a governance-controlled action (e.g., promote domain rule, escalate for review).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | string | ✅ | Action to execute: `promote_rule`, `demote_rule`, `escalate_review`, `apply_exception` |
| `parameters` | object | ✅ | Action-specific parameters (varies by action type) |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "execute-governance",
    "arguments": {
      "action": "promote_rule",
      "parameters": {
        "rule_id": "DOMAIN-042",
        "to_tier": 1,
        "reason": "Elevated security requirement discovered"
      }
    }
  },
  "id": 102
}
```

**Real Implementation (Phase 2):**
Will:
- Verify authorization for action
- Perform action with audit trail
- Update governance database
- Trigger affected orchestrator notifications
- Return success/failure with details

---

### 4. Analyze Governance

**Tool ID:** `analyze-governance`  
**Category:** Governance  
**Requires Auth:** ✅ YES  
**Status:** Stub (returns mock data)

**Description:**
Analyze governance rule effectiveness and coverage.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `time_range` | string | ✅ | Time range: `24h`, `7d`, `30d`, or ISO 8601 date range |
| `scope` | string | ❌ | Analysis scope: `all`, `domain`, `operation` (default: `all`) |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "analyze-governance",
    "arguments": {
      "time_range": "24h",
      "scope": "all"
    }
  },
  "id": 103
}
```

**Real Implementation (Phase 2):**
Will analyze:
- Rule evaluation frequency and coverage
- Violations detected and corrected
- Rule effectiveness (false positives/negatives)
- Coverage gaps
- Recommendations for new rules

---

### 5. Generate Governance Report

**Tool ID:** `report-governance`  
**Category:** Governance  
**Requires Auth:** ✅ YES  
**Status:** Stub (returns mock data)

**Description:**
Generate compliance and governance reports for audit/compliance purposes.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `report_type` | string | ✅ | Report type: `compliance`, `coverage`, `violations`, `audit_trail` |
| `date_range` | string | ✅ | Date range (ISO 8601 or `last_30_days`) |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "report-governance",
    "arguments": {
      "report_type": "compliance",
      "date_range": "last_30_days"
    }
  },
  "id": 104
}
```

---

## Orchestration Tools (4)

### 6. Orchestrator Status

**Tool ID:** `status-orchestrator`  
**Category:** Orchestration  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Check the current status of orchestrators (running, completed, failed, etc.).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `orchestrator_id` | string | ❌ | Specific orchestrator ID; omit to list all |
| `include_logs` | boolean | ❌ | Include execution logs in response (default: false) |

---

### 7. Monitor Orchestration

**Tool ID:** `monitor-orchestration`  
**Category:** Orchestration  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Monitor real-time orchestration metrics and health status.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `time_window` | string | ✅ | Time window: `5m`, `1h`, `24h` |
| `metric_types` | array | ❌ | Metrics to include: `throughput`, `latency`, `errors`, `resource_usage` |

---

### 8. Optimize Orchestration

**Tool ID:** `optimize-orchestration`  
**Category:** Orchestration  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Get optimization suggestions for orchestration performance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `analysis_type` | string | ✅ | `performance`, `resource_usage`, `throughput` |
| `performance_goal` | string | ❌ | Goal: `minimize_latency`, `maximize_throughput`, `optimize_cost` |

---

### 9. Diagnose Issues

**Tool ID:** `diagnose-issues`  
**Category:** Orchestration  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Diagnose orchestration problems and failures.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `orchestrator_id` | string | ❌ | Specific orchestrator to diagnose |
| `log_level` | string | ❌ | Log verbosity: `error`, `warning`, `info`, `debug` (default: `error`) |

---

## Knowledge Tools (3)

### 10. Search Knowledge

**Tool ID:** `search-knowledge`  
**Category:** Knowledge  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Search the knowledge graph and domain knowledge base.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | ✅ | Search query or semantic similarity query |
| `filters` | object | ❌ | Filter results: `{domain, category, date_range}` |
| `limit` | integer | ❌ | Max results to return (default: 10) |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search-knowledge",
    "arguments": {
      "query": "password reset workflow",
      "filters": {
        "domain": "user_management"
      },
      "limit": 5
    }
  },
  "id": 110
}
```

---

### 11. Analyze Knowledge

**Tool ID:** `analyze-knowledge`  
**Category:** Knowledge  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Extract insights and analyze the knowledge base.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `domain` | string | ✅ | Domain to analyze (e.g., `healthcare`, `finance`) |
| `analysis_type` | string | ✅ | Type: `coverage`, `quality`, `consistency`, `completeness` |

---

### 12. Generate Knowledge

**Tool ID:** `generate-knowledge`  
**Category:** Knowledge  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Generate knowledge recommendations based on context.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `context` | string | ✅ | Context for generation (e.g., current operation) |
| `intent` | string | ✅ | Intent: `predict`, `recommend`, `explain` |

---

## Utility Tools (2)

### 13. Echo Test

**Tool ID:** `echo-test`  
**Category:** Utility  
**Requires Auth:** ❌ NO  
**Status:** Working

**Description:**
Simple echo tool for connectivity testing and MCP protocol verification.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `message` | string | ✅ | Message to echo back |

**Example Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "echo-test",
    "arguments": {
      "message": "Hello CORTEX"
    }
  },
  "id": 120
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Echo: Hello CORTEX"
      }
    ]
  },
  "id": 120
}
```

---

### 14. Transform Data

**Tool ID:** `transform-data`  
**Category:** Utility  
**Requires Auth:** ❌ NO  
**Status:** Stub

**Description:**
Transform data between different formats.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `input` | string | ✅ | Input data to transform |
| `format` | string | ✅ | Source format: `json`, `yaml`, `csv`, `xml` |
| `target_format` | string | ✅ | Target format: `json`, `yaml`, `csv`, `xml` |

---

## Tool Implementation Status

### Current Status (2026-01-20)

| Tool | Category | Status | Implementation |
|------|----------|--------|-----------------|
| **query-governance** | Governance | Stub | Returns mock JSON response |
| **validate-compliance** | Governance | Stub | Returns mock validation result |
| **execute-governance** | Governance | Stub | Returns mock execution result |
| **analyze-governance** | Governance | Stub | Returns mock analysis metrics |
| **report-governance** | Governance | Stub | Returns mock report data |
| **status-orchestrator** | Orchestration | Stub | Returns mock status |
| **monitor-orchestration** | Orchestration | Stub | Returns mock metrics |
| **optimize-orchestration** | Orchestration | Stub | Returns mock suggestions |
| **diagnose-issues** | Orchestration | Stub | Returns mock diagnostics |
| **search-knowledge** | Knowledge | Stub | Returns mock search results |
| **analyze-knowledge** | Knowledge | Stub | Returns mock analysis |
| **generate-knowledge** | Knowledge | Stub | Returns mock recommendations |
| **echo-test** | Utility | ✅ Working | Echoes input message |
| **transform-data** | Utility | Stub | Returns mock transformation |

**Legend:**
- **Working:** Real implementation, fully functional
- **Stub:** Registered but returns mock data
- **Blocked:** Awaiting dependency

### Phase Timeline

| Phase | Work | Tools | Timeline |
|-------|------|-------|----------|
| **Phase B** | Create registry, reorganize by category, update server discovery | All 14 | 2 days |
| **Phase 2** | Implement real tool logic (currently mock data) | All 14 | 3-4 days |
| **Phase 3** | Add tool versioning, deprecation, composition | All 14 | 2-3 days |

---

## Using Tools in Claude Desktop

### 1. Verify Tool Discovery

Test that Claude can discover tools:

```
User: @cortex-mcp what tools are available?
Claude: [Calls tools/list method]
Response: Shows 14 tools in 4 categories
```

### 2. Call a Tool

```
User: @cortex-mcp query governance state for conversation context
Claude: [Calls query-governance with context=conversation]
Response: Shows active governance rules
```

### 3. Validate Compliance

```
User: @cortex-mcp validate that responding to user query complies with governance
Claude: [Calls validate-compliance]
Response: APPROVED or VIOLATIONS list
```

---

## References

- **MCP Specification:** [0-specification.md](./0-specification.md)
- **Server Implementation:** `cortex/mcp/server.py`
- **Registry (Phase B):** `cortex/mcp/registry.py` (to be created)
- **Tool Directories:** `cortex/mcp/tools/{governance,orchestration,knowledge,utility}/`
- **Governance Rules:** `cortex_brain/tier0/governance/core-rules.yaml`

---

**Authority:** cortex-impl-map.yaml v3.1  
**Status:** Phase B: Create registry (2 days), Phase 2: Implement tools (3-4 days)  
**Last Updated:** 2026-01-20
