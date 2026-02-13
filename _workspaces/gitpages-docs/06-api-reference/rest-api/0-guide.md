# REST API Guide

**Last Updated:** 2026-01-20  
**Audience:** Developers, Integrators  
**Prerequisites:** [System Overview](../../02-architecture/1-system-overview.md)

## Overview

CORTEX exposes a REST API for orchestrator execution, domain knowledge management, and governance queries. The API follows RESTful principles with JSON request/response bodies and standard HTTP status codes.

## Base URL

| Environment | Base URL |
|-------------|----------|
| Local Development | `http://localhost:8000/api/v1` |
| Staging | `https://cortex-staging.example.com/api/v1` |
| Production | `https://cortex.example.com/api/v1` |

## Authentication

### API Key Authentication

```http
Authorization: Bearer <api_key>
```

### Request Headers

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <api_key>
X-Request-ID: <unique_request_id>
```

## API Endpoints

### Orchestrators

#### Execute Orchestrator

**POST** `/orchestrators/{name}/execute`

Execute a named orchestrator with context.

**Request:**
```json
{
  "context": {
    "intent": "create_feature",
    "parameters": {
      "feature_name": "user_authentication",
      "complexity": "moderate"
    }
  },
  "options": {
    "timeout_seconds": 300,
    "retry_on_failure": true
  }
}
```

**Response (200 OK):**
```json
{
  "execution_id": "exec-12345",
  "orchestrator": "planning",
  "status": "completed",
  "result": {
    "plan": {
      "steps": [
        {"id": 1, "action": "analyze_requirements"},
        {"id": 2, "action": "design_architecture"},
        {"id": 3, "action": "implement_feature"}
      ]
    }
  },
  "audit": {
    "ac_id": "AC-PLAN-001",
    "started_at": "2026-01-20T10:00:00Z",
    "completed_at": "2026-01-20T10:00:05Z",
    "duration_ms": 5000
  }
}
```

#### List Orchestrators

**GET** `/orchestrators`

List all available orchestrators.

**Response (200 OK):**
```json
{
  "orchestrators": [
    {
      "name": "planning",
      "domain": "planning",
      "description": "Workflow coordination and planning",
      "status": "active"
    },
    {
      "name": "complexity_assessment",
      "domain": "analysis",
      "description": "Assess operation complexity",
      "status": "active"
    }
  ],
  "total": 15
}
```

#### Get Orchestrator Status

**GET** `/orchestrators/{name}/status`

Get status of a specific orchestrator.

**Response (200 OK):**
```json
{
  "name": "planning",
  "domain": "planning",
  "status": "active",
  "health": {
    "circuit_breaker": "closed",
    "last_execution": "2026-01-20T09:55:00Z",
    "success_rate": 0.98
  },
  "metrics": {
    "total_executions": 1250,
    "avg_duration_ms": 3200,
    "error_rate": 0.02
  }
}
```

### Domain Brain

#### Query Knowledge

**POST** `/knowledge/query`

Query the Domain Brain for knowledge.

**Request:**
```json
{
  "domains": ["financial", "compliance"],
  "keywords": ["transaction", "audit"],
  "filters": {
    "entity_type": "rule",
    "severity": "critical"
  },
  "max_results": 10,
  "include_relationships": true
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "rule-001",
      "type": "rule",
      "domain": "compliance",
      "name": "CORE-027",
      "content": "All operations must generate audit trail entries",
      "severity": "critical",
      "relationships": [
        {
          "target": "audit_logger",
          "type": "enforced_by"
        }
      ]
    }
  ],
  "total": 1,
  "query_time_ms": 45
}
```

#### Ingest Knowledge

**POST** `/knowledge/ingest`

Ingest new knowledge into the Domain Brain.

**Request:**
```json
{
  "source": "business_document",
  "format": "yaml",
  "content": "rules:\n  - id: BUS-001\n    description: Transaction limit rule",
  "metadata": {
    "author": "compliance_team",
    "version": "1.0.0"
  }
}
```

**Response (201 Created):**
```json
{
  "ingestion_id": "ing-12345",
  "status": "completed",
  "entities_created": 1,
  "conflicts_detected": 0,
  "audit": {
    "ac_id": "AC-BKIO-001",
    "timestamp": "2026-01-20T10:05:00Z"
  }
}
```

### Governance

#### Validate Against Rules

**POST** `/governance/validate`

Validate an entity against governance rules.

**Request:**
```json
{
  "entity_type": "orchestrator",
  "entity_data": {
    "name": "custom_orchestrator",
    "domain": "planning",
    "has_tests": true,
    "has_docstrings": true
  },
  "rules": ["CORE-008", "CORE-011", "CORE-012"]
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "results": [
    {
      "rule": "CORE-008",
      "status": "pass",
      "message": "TDD requirement satisfied"
    },
    {
      "rule": "CORE-011",
      "status": "pass",
      "message": "Type hints present"
    },
    {
      "rule": "CORE-012",
      "status": "pass",
      "message": "Docstrings present"
    }
  ]
}
```

#### Query Audit Trail

**GET** `/governance/audit`

Query the audit trail.

**Query Parameters:**
- `ac_id` - Filter by AC-ID
- `start_date` - Start date (ISO 8601)
- `end_date` - End date (ISO 8601)
- `operation` - Filter by operation type
- `limit` - Max results (default: 100)

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 7831,
      "ac_id": "AC-PLAN-001",
      "operation": "AC_COMPLETE",
      "timestamp": "2026-01-20T10:00:05Z",
      "hash": "a1b2c3d4e5f6...",
      "previous_hash": "9z8y7x6w5v...",
      "metadata": {
        "duration_ms": 5000,
        "result": "success"
      }
    }
  ],
  "total": 1,
  "hash_chain_valid": true
}
```

### Configuration

#### Get Configuration

**GET** `/config`

Get current CORTEX configuration.

**Response (200 OK):**
```json
{
  "version": "1.0.0",
  "environment": "development",
  "features": {
    "complexity_gate": true,
    "response_composition": true,
    "domain_brain": true
  },
  "thresholds": {
    "complexity": {
      "trivial": 0.15,
      "simple": 0.35,
      "moderate": 0.60,
      "complex": 0.85
    }
  }
}
```

#### Update Configuration

**PATCH** `/config`

Update CORTEX configuration (requires admin privileges).

**Request:**
```json
{
  "thresholds": {
    "complexity": {
      "trivial": 0.10
    }
  }
}
```

**Response (200 OK):**
```json
{
  "updated": true,
  "changes": [
    {
      "path": "thresholds.complexity.trivial",
      "old_value": 0.15,
      "new_value": 0.10
    }
  ]
}
```

## Error Responses

### Error Structure

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "orchestrator_name",
        "error": "Orchestrator 'unknown' not found"
      }
    ],
    "request_id": "req-12345",
    "timestamp": "2026-01-20T10:00:00Z"
  }
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request parameters |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource conflict (e.g., duplicate) |
| 422 | `GOVERNANCE_VIOLATION` | Governance rule violated |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

## Rate Limiting

| Endpoint | Rate Limit |
|----------|------------|
| `/orchestrators/*/execute` | 100 req/min |
| `/knowledge/query` | 500 req/min |
| `/knowledge/ingest` | 50 req/min |
| `/governance/*` | 200 req/min |
| `/config` | 10 req/min |

Headers included in response:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705750800
```

## Pagination

For list endpoints, use cursor-based pagination:

**Request:**
```http
GET /orchestrators?limit=10&cursor=abc123
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "limit": 10,
    "has_more": true,
    "next_cursor": "def456"
  }
}
```

## Webhooks

### Configure Webhook

**POST** `/webhooks`

```json
{
  "url": "https://example.com/cortex-webhook",
  "events": ["orchestrator.completed", "governance.violation"],
  "secret": "webhook_secret_123"
}
```

### Webhook Payload

```json
{
  "event": "orchestrator.completed",
  "timestamp": "2026-01-20T10:00:05Z",
  "data": {
    "execution_id": "exec-12345",
    "orchestrator": "planning",
    "status": "completed"
  },
  "signature": "sha256=abc123..."
}
```

## SDK Examples

### Python

```python
import requests

class CORTEXClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def execute_orchestrator(self, name: str, context: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/orchestrators/{name}/execute",
            headers=self.headers,
            json={"context": context}
        )
        response.raise_for_status()
        return response.json()
    
    def query_knowledge(self, domains: list, keywords: list) -> dict:
        response = requests.post(
            f"{self.base_url}/knowledge/query",
            headers=self.headers,
            json={"domains": domains, "keywords": keywords}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = CORTEXClient("http://localhost:8000/api/v1", "your_api_key")
result = client.execute_orchestrator("planning", {"intent": "create_feature"})
```

### JavaScript/TypeScript

```typescript
class CORTEXClient {
  constructor(private baseUrl: string, private apiKey: string) {}

  async executeOrchestrator(name: string, context: object): Promise<any> {
    const response = await fetch(`${this.baseUrl}/orchestrators/${name}/execute`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ context })
    });
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

// Usage
const client = new CORTEXClient('http://localhost:8000/api/v1', 'your_api_key');
const result = await client.executeOrchestrator('planning', { intent: 'create_feature' });
```

## Related Documentation

- [MCP Protocol](../mcp-protocol/0-specification.md) - Alternative AI-native protocol
- [CLI Reference](../cli/0-guide.md) - Command-line interface
- [Authentication](../../04-guides/integration/authentication.md) - Auth configuration
- [Troubleshooting](../../04-guides/operations/4-troubleshooting.md) - Common issues
