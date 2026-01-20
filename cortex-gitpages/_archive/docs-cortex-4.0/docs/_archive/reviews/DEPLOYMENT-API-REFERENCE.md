# CORTEX MCP Hub API Reference

**AC-DEPLOY-ENHANCED-005-01: Comprehensive Deployment Documentation**

## API Overview

The CORTEX MCP Hub exposes governance and registry operations via HTTP endpoints (implementing MCP). All requests use JSON and include proper error handling.

### Base URL
```
http://127.0.0.1:8000  (default)
```

### Authentication
Currently no authentication required. In production, implement API key or JWT.

### Response Format
All responses return JSON with standard structure:
```json
{
  "status": "success|error|warning",
  "data": {},
  "timestamp": "2026-01-19T14:00:00Z",
  "request_id": "abc-123"
}
```

---

## Health & Status Endpoints

### `GET /health`

Check hub health status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T14:00:00Z",
  "components": {
    "database": "ok",
    "governance": "ok",
    "registry": "ok"
  },
  "response_time_ms": 5
}
```

**Status Codes**:
- `200`: Healthy
- `503`: Unhealthy (check logs)

---

### `GET /status`

Detailed hub status including version and configuration.

**Response**:
```json
{
  "status": "success",
  "data": {
    "version": "1.0.0",
    "uptime_seconds": 3600,
    "repositories": {
      "connected": 3,
      "offline": 0
    },
    "governance": {
      "rules_count": 42,
      "last_update": "2026-01-19T13:00:00Z"
    }
  }
}
```

---

## Registry Endpoints

### `GET /registry/repos`

List all registered repositories.

**Query Parameters**:
- `filter`: Optional filter by type (source, orchestrator, tool, knowledge)
- `status`: Optional filter by status (connected, offline, error)

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "repo_id": "frontend",
      "repo_name": "Frontend",
      "repo_type": "source",
      "path": "/Users/dev/projects/frontend",
      "status": "connected",
      "last_seen": "2026-01-19T14:00:00Z",
      "version": "1.0.0"
    },
    {
      "repo_id": "backend",
      "repo_name": "Backend",
      "repo_type": "source",
      "path": "/Users/dev/projects/backend",
      "status": "connected",
      "last_seen": "2026-01-19T13:59:00Z",
      "version": "1.0.0"
    }
  ]
}
```

---

### `POST /registry/repos`

Register a new repository.

**Request Body**:
```json
{
  "repo_id": "mobile",
  "repo_name": "Mobile App",
  "repo_type": "source",
  "path": "/Users/dev/projects/mobile",
  "version": "1.0.0"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "repo_id": "mobile",
    "registered_at": "2026-01-19T14:00:00Z"
  }
}
```

**Status Codes**:
- `201`: Registered successfully
- `409`: Repo already exists
- `400`: Invalid request

---

### `GET /registry/repos/{repo_id}`

Get details for specific repository.

**Response**:
```json
{
  "status": "success",
  "data": {
    "repo_id": "frontend",
    "repo_name": "Frontend",
    "repo_type": "source",
    "path": "/Users/dev/projects/frontend",
    "status": "connected",
    "isolation_mode": "strict",
    "version": "1.0.0",
    "min_hub_version": "1.0.0",
    "registered_at": "2026-01-18T10:00:00Z",
    "last_activity": "2026-01-19T14:00:00Z"
  }
}
```

---

### `DELETE /registry/repos/{repo_id}`

Unregister a repository.

**Response**:
```json
{
  "status": "success",
  "data": {
    "repo_id": "frontend",
    "unregistered_at": "2026-01-19T14:00:00Z"
  }
}
```

---

## Governance Endpoints

### `POST /governance/validate`

Validate a file against governance rules.

**Request Body**:
```json
{
  "repo_id": "frontend",
  "file": "src/main.ts",
  "content": "optional file content for deep validation"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "repo_id": "frontend",
    "file": "src/main.ts",
    "violations": [
      {
        "rule_id": "RULE_001",
        "severity": "warning",
        "message": "TypeScript file detected",
        "line": 1,
        "column": 1,
        "quick_fix": "Check TypeScript configuration"
      }
    ],
    "validation_time_ms": 45
  }
}
```

---

### `GET /governance/rules`

List all active governance rules.

**Query Parameters**:
- `repo_id`: Optional filter by repository
- `severity`: Optional filter by severity (error, warning, info)

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 42,
    "rules": [
      {
        "rule_id": "RULE_001",
        "description": "Enforce TypeScript strict mode",
        "severity": "error",
        "pattern": "**/*.ts",
        "applies_to": ["frontend", "backend"],
        "enforcement": "block"
      }
    ]
  }
}
```

---

### `GET /governance/rules/{rule_id}`

Get details for specific rule.

**Response**:
```json
{
  "status": "success",
  "data": {
    "rule_id": "RULE_001",
    "description": "Enforce TypeScript strict mode",
    "severity": "error",
    "pattern": "**/*.ts",
    "applies_to": ["frontend", "backend"],
    "enforcement": "block",
    "created_at": "2026-01-01T00:00:00Z",
    "last_updated": "2026-01-10T10:00:00Z",
    "remediation": "Enable 'strict' in tsconfig.json"
  }
}
```

---

### `POST /governance/apply-fix`

Apply a quick fix to a file.

**Request Body**:
```json
{
  "repo_id": "frontend",
  "file": "src/main.ts",
  "fix_id": "RULE_001_FIX_1",
  "parameters": {}
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "repo_id": "frontend",
    "file": "src/main.ts",
    "fix_applied": true,
    "changes": {
      "lines_changed": 3,
      "diff": "..."
    }
  }
}
```

---

## Audit Trail Endpoints

### `GET /audit/trail`

Get audit trail entries.

**Query Parameters**:
- `limit`: Max entries to return (default: 100, max: 1000)
- `repo_id`: Optional filter by repository
- `operation`: Optional filter by operation type
- `since`: Optional ISO timestamp to get entries after

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 50,
    "entries": [
      {
        "id": "audit-001",
        "timestamp": "2026-01-19T14:00:00Z",
        "operation": "file_validated",
        "actor": "vs-code-extension",
        "repo_id": "frontend",
        "file": "src/main.ts",
        "details": {
          "violations": 2,
          "status": "failed"
        }
      },
      {
        "id": "audit-002",
        "timestamp": "2026-01-19T13:59:00Z",
        "operation": "repo_registered",
        "actor": "developer@company.com",
        "repo_id": "backend",
        "details": {
          "isolation_mode": "strict"
        }
      }
    ]
  }
}
```

---

### `GET /audit/trail/{audit_id}`

Get specific audit entry details.

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "audit-001",
    "timestamp": "2026-01-19T14:00:00Z",
    "operation": "file_validated",
    "actor": "vs-code-extension",
    "repo_id": "frontend",
    "file": "src/main.ts",
    "details": {
      "violations": 2,
      "rules_checked": 42,
      "validation_time_ms": 45,
      "status": "failed"
    },
    "session_id": "session-123"
  }
}
```

---

## Session Endpoints

### `GET /sessions`

List active sessions.

**Response**:
```json
{
  "status": "success",
  "data": {
    "count": 3,
    "sessions": [
      {
        "session_id": "session-001",
        "repo_id": "frontend",
        "created_at": "2026-01-19T14:00:00Z",
        "last_activity": "2026-01-19T14:00:00Z",
        "status": "active"
      }
    ]
  }
}
```

---

### `GET /sessions/{session_id}`

Get session details.

**Response**:
```json
{
  "status": "success",
  "data": {
    "session_id": "session-001",
    "repo_id": "frontend",
    "created_at": "2026-01-19T14:00:00Z",
    "last_activity": "2026-01-19T14:00:00Z",
    "age_seconds": 150,
    "metadata": {
      "tool": "vs-code-extension",
      "version": "1.0.0"
    }
  }
}
```

---

### `DELETE /sessions/{session_id}`

Close a session.

**Response**:
```json
{
  "status": "success",
  "data": {
    "session_id": "session-001",
    "closed_at": "2026-01-19T14:05:00Z"
  }
}
```

---

## Version Management Endpoints

### `GET /config/prompt-version`

Get current prompt version for repository.

**Query Parameters**:
- `repo_id`: Repository ID

**Response**:
```json
{
  "status": "success",
  "data": {
    "repo_id": "frontend",
    "version": "1.0.0",
    "compatible_versions": ["1.0.0", "1.0.1", "1.1.0"],
    "deprecated": false,
    "sha256": "abc123..."
  }
}
```

---

### `POST /config/negotiate-version`

Negotiate version compatibility.

**Request Body**:
```json
{
  "repo_id": "frontend",
  "requested_version": "1.0.0",
  "min_version": "0.9.0"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "negotiated_version": "1.0.0",
    "compatible": true,
    "reason": "exact_match",
    "alternative_versions": ["1.0.1", "1.1.0"]
  }
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "File does not meet governance rules",
    "details": "TypeScript strict mode is required"
  },
  "request_id": "abc-123"
}
```

### Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_REQUEST` | 400 | Invalid request body |
| `UNAUTHORIZED` | 401 | No/invalid authentication |
| `FORBIDDEN` | 403 | Access denied |
| `CONFLICT` | 409 | Resource already exists |
| `TIMEOUT` | 408 | Request timeout |
| `VALIDATION_FAILED` | 422 | Governance validation failed |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

**Current**: No rate limiting (add in production)

**Recommended**:
- 100 requests per minute per IP
- 1000 requests per minute per API key

---

## Pagination

Large result sets use pagination:

```json
{
  "status": "success",
  "data": [/* items */],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 150,
    "has_next": true
  }
}
```

---

## cURL Examples

### Validate a file
```bash
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "frontend",
    "file": "src/main.ts"
  }'
```

### Register a repository
```bash
curl -X POST http://127.0.0.1:8000/registry/repos \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "mobile",
    "repo_name": "Mobile App",
    "repo_type": "source",
    "path": "/path/to/mobile"
  }'
```

### Get audit trail
```bash
curl "http://127.0.0.1:8000/audit/trail?limit=50&repo_id=frontend"
```

### Check governance rules
```bash
curl "http://127.0.0.1:8000/governance/rules?repo_id=frontend"
```

---

## WebSocket Events (Future)

Planned for real-time updates:
- `governance.rule_updated` - Rule changed
- `repo.status_changed` - Repo went online/offline
- `validation.completed` - Async validation finished

---

**Last Updated**: January 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
