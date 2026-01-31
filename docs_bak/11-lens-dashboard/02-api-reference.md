# LENS Dashboard API Reference

**Version:** 1.0.0  
**Base URL:** `/api/dashboard`  
**Phase:** 14 - LENS Dashboard Implementation

---

## Overview

The LENS Dashboard API provides programmatic access to code intelligence analysis. All endpoints return JSON data suitable for frontend visualization or programmatic consumption.

---

## Authentication

Currently no authentication required (local development only).

For production deployment, implement:
- API keys
- JWT tokens
- OAuth 2.0

---

## Endpoints

### 1. Analyze Repository

Performs complete analysis of a repository, returning all 8 tabs of data.

**Endpoint:** `GET /api/dashboard/analyze`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_path` | string | Yes | Absolute path to repository |
| `timeout` | float | No | Analysis timeout in seconds |

**Response:** `200 OK`

```json
{
  "overview": {
    "total_files": 150,
    "lines_of_code": 45000,
    "contributors": 8,
    "modules": 25,
    "business_summary": "<p>Repository analysis complete.</p>",
    "key_components": [],
    "health": {
      "documentation": 75,
      "test_coverage": 80,
      "type_hints": 90
    },
    "tech_stack": [
      {
        "name": "Python",
        "version": "3.9+",
        "icon": "🐍",
        "category": "language"
      }
    ],
    "activity": {
      "commits": 1500,
      "pull_requests": 0,
      "active_contributors": 8,
      "files_changed": 0
    },
    "is_cortex": false
  },
  "dependencies": {
    "nodes": [
      {
        "id": "author1",
        "size": 150,
        "type": "internal"
      }
    ],
    "links": [
      {
        "source": "author1",
        "target": "author2",
        "strength": 0.8
      }
    ],
    "stats": {
      "total_authors": 8,
      "total_connections": 24,
      "avg_commits_per_author": 187.5
    }
  },
  "classes": {
    "packages": ["cortex", "tests"],
    "current_diagram": "graph LR\n  A[Class1] --> B[Class2]",
    "class_details": [],
    "stats": {
      "total_classes": 45,
      "total_methods": 230
    }
  },
  "timeline": {
    "timeline_data": [
      {
        "date": "2026-01-29",
        "value": 150
      }
    ],
    "authors": ["dev1", "dev2"],
    "stats": {
      "total_commits": 1500,
      "total_contributors": 8,
      "lines_added": 50000,
      "lines_removed": 5000,
      "net_change": 45000,
      "files_changed": 150
    }
  },
  "impact": {
    "blast_radius": 12,
    "affected_components": ["module1", "module2"],
    "test_requirements": {
      "unit_tests": 45,
      "integration_tests": 12
    }
  },
  "brain": null,
  "governance": null,
  "orchestrators": null,
  "_metadata": {
    "analysis_time_ms": 1234,
    "timestamp": "2026-01-29T10:30:00.000000+00:00",
    "repo_path": "/path/to/repo",
    "is_cortex": false,
    "warnings": null
  }
}
```

**CORTEX Repository Response:**

For CORTEX repositories, additional tabs are populated:

```json
{
  "brain": {
    "tiers": {
      "tier0": {
        "rule_count": 28,
        "rules": []
      },
      "tier1": {
        "ac_count": 0,
        "phases": []
      },
      "tier2": {
        "template_count": 0,
        "templates": []
      },
      "tier3": {
        "knowledge_count": 35,
        "categories": []
      }
    },
    "health": {
      "governance_compliance": 100,
      "ac_completion": 95,
      "template_coverage": 90,
      "knowledge_freshness": 85
    }
  },
  "governance": {
    "stats": {
      "total_rules": 28,
      "compliant_rules": 25,
      "partial_compliance": 2,
      "violations": 1,
      "overall_compliance": 95
    },
    "rules": []
  },
  "orchestrators": {
    "stats": {
      "total": 23,
      "active": 23,
      "connections": 45,
      "invocations": 1000
    },
    "categories": {
      "core": [],
      "domain": [],
      "support": []
    }
  }
}
```

**Error Responses:**

- `404 Not Found` - Repository path doesn't exist
- `403 Forbidden` - Permission denied
- `400 Bad Request` - Invalid parameters
- `500 Internal Server Error` - Analysis failed

**Example:**

```bash
curl "http://localhost:8888/api/dashboard/analyze?repo_path=/Users/dev/myproject"
```

---

### 2. Get Tab Data

Returns data for a specific dashboard tab.

**Endpoint:** `GET /api/dashboard/tab/{tab_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tab_id` | string | Yes | Tab identifier |

**Valid Tab IDs:**
- `overview`
- `dependencies`
- `classes`
- `timeline`
- `impact`
- `brain` (CORTEX only)
- `governance` (CORTEX only)
- `orchestrators` (CORTEX only)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_path` | string | Yes | Absolute path to repository |

**Response:** `200 OK`

Returns the specific tab data structure (see Analyze Repository for schemas).

**Error Responses:**

- `404 Not Found` - Invalid tab_id or repository not found
- `500 Internal Server Error` - Tab generation failed

**Example:**

```bash
curl "http://localhost:8888/api/dashboard/tab/overview?repo_path=/path/to/repo"
```

---

### 3. Get Overlay Data

Returns overlay visualization data for security, performance, or compliance.

**Endpoint:** `GET /api/dashboard/overlay/{type}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Overlay type |

**Valid Overlay Types:**
- `security` - Security analysis
- `performance` - Performance hotspots
- `compliance` - CORE rule compliance

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_path` | string | Yes | Absolute path to repository |

**Response: Performance Overlay**

```json
{
  "bottlenecks": [
    {
      "function": "complex_function",
      "file": "module.py",
      "complexity": 45,
      "recommendation": "Consider refactoring"
    }
  ],
  "complexity_hotspots": [
    {
      "x": 150,
      "y": 45,
      "size": 20,
      "label": "module.complex_function"
    }
  ]
}
```

**Response: Security Overlay**

```json
{
  "vulnerabilities": [],
  "security_score": 95
}
```

**Response: Compliance Overlay**

```json
{
  "core_rules": [
    {
      "id": "CORE-008",
      "name": "TDD",
      "status": "compliant"
    }
  ],
  "compliance_percentage": 95,
  "violations": [
    {
      "rule": "CORE-013",
      "file": "module.py",
      "line": 45
    }
  ]
}
```

**Error Responses:**

- `404 Not Found` - Invalid overlay type or repository not found

**Example:**

```bash
curl "http://localhost:8888/api/dashboard/overlay/performance?repo_path=/path/to/repo"
```

---

### 4. WebSocket Real-Time Updates

Real-time dashboard updates via WebSocket.

**Endpoint:** `WebSocket /api/dashboard/ws`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_path` | string | Yes | Absolute path to repository |
| `interval` | integer | No | Update interval in seconds (default: 5) |

**Message Format:**

Server sends periodic updates:

```json
{
  "type": "update",
  "timestamp": "2026-01-29T10:30:00Z",
  "data": {
    "overview": {...},
    "dependencies": {...}
  }
}
```

**Client Messages:**

Client can send control messages:

```json
{
  "type": "pause"
}
```

```json
{
  "type": "resume"
}
```

**Example (JavaScript):**

```javascript
const ws = new WebSocket('ws://localhost:8888/api/dashboard/ws?repo_path=/path/to/repo&interval=5');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Dashboard update:', update);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Data Models

### Overview Data

```typescript
interface OverviewData {
  total_files: number;
  lines_of_code: number;
  contributors: number;
  modules: number;
  business_summary: string;
  key_components: string[];
  health: {
    documentation: number;
    test_coverage: number;
    type_hints: number;
  };
  tech_stack: TechStackItem[];
  activity: ActivityMetrics;
  is_cortex: boolean;
}

interface TechStackItem {
  name: string;
  version: string;
  icon: string;
  category: string;
}

interface ActivityMetrics {
  commits: number;
  pull_requests: number;
  active_contributors: number;
  files_changed: number;
}
```

### Dependencies Data

```typescript
interface DependenciesData {
  nodes: NetworkNode[];
  links: NetworkLink[];
  stats: NetworkStats;
}

interface NetworkNode {
  id: string;
  size: number;
  type: "internal" | "external";
}

interface NetworkLink {
  source: string;
  target: string;
  strength: number;
}

interface NetworkStats {
  total_authors: number;
  total_connections: number;
  avg_commits_per_author: number;
}
```

### Classes Data

```typescript
interface ClassesData {
  packages: string[];
  current_diagram: string; // Mermaid diagram
  class_details: ClassDetail[];
  stats: ClassStats;
}

interface ClassDetail {
  name: string;
  methods: string[];
  file: string;
  line: number;
}

interface ClassStats {
  total_classes: number;
  total_methods: number;
}
```

### Timeline Data

```typescript
interface TimelineData {
  timeline_data: TimelinePoint[];
  authors: string[];
  stats: TimelineStats;
}

interface TimelinePoint {
  date: string; // ISO 8601
  value: number;
}

interface TimelineStats {
  total_commits: number;
  total_contributors: number;
  lines_added: number;
  lines_removed: number;
  net_change: number;
  files_changed: number;
}
```

### Impact Data

```typescript
interface ImpactData {
  blast_radius: number;
  affected_components: string[];
  test_requirements: TestRequirements;
}

interface TestRequirements {
  unit_tests: number;
  integration_tests: number;
}
```

### Metadata

```typescript
interface Metadata {
  analysis_time_ms: number;
  timestamp: string; // ISO 8601
  repo_path: string;
  is_cortex: boolean;
  warnings: string[] | null;
}
```

---

## Rate Limiting

Currently no rate limiting (local development).

For production:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## Caching

Analysis results are cached for 5 minutes by default.

To invalidate cache:
```bash
# Not yet implemented
curl -X DELETE "http://localhost:8888/api/dashboard/cache?repo_path=/path/to/repo"
```

---

## Error Handling

All errors follow consistent format:

```json
{
  "detail": "Error message",
  "status_code": 404
}
```

Common error codes:
- `400` - Bad request (invalid parameters)
- `403` - Forbidden (permission denied)
- `404` - Not found (repository or resource)
- `422` - Validation error (invalid data)
- `500` - Internal server error

---

## Best Practices

1. **Use specific tab endpoints** for faster response times
2. **Cache results** for static repositories
3. **Handle timeouts** gracefully
4. **Monitor analysis_time_ms** to detect performance issues
5. **Check warnings field** in metadata for analysis issues

---

## Examples

### Python Client

```python
import requests

class LENSDashboardClient:
    def __init__(self, base_url="http://localhost:8888"):
        self.base_url = base_url
    
    def analyze_repository(self, repo_path: str) -> dict:
        """Get full dashboard analysis."""
        response = requests.get(
            f"{self.base_url}/api/dashboard/analyze",
            params={"repo_path": repo_path}
        )
        response.raise_for_status()
        return response.json()
    
    def get_tab(self, tab_id: str, repo_path: str) -> dict:
        """Get specific tab data."""
        response = requests.get(
            f"{self.base_url}/api/dashboard/tab/{tab_id}",
            params={"repo_path": repo_path}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = LENSDashboardClient()
data = client.analyze_repository("/path/to/repo")
print(f"Total files: {data['overview']['total_files']}")
```

### JavaScript Client

```javascript
class LENSDashboardClient {
  constructor(baseUrl = 'http://localhost:8888') {
    this.baseUrl = baseUrl;
  }

  async analyzeRepository(repoPath) {
    const response = await fetch(
      `${this.baseUrl}/api/dashboard/analyze?repo_path=${encodeURIComponent(repoPath)}`
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    return response.json();
  }

  async getTab(tabId, repoPath) {
    const response = await fetch(
      `${this.baseUrl}/api/dashboard/tab/${tabId}?repo_path=${encodeURIComponent(repoPath)}`
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    return response.json();
  }
}

// Usage
const client = new LENSDashboardClient();
const data = await client.analyzeRepository('/path/to/repo');
console.log(`Total files: ${data.overview.total_files}`);
```

---

## Version History

### v1.0.0 (2026-01-29)
- Initial API release
- 4 endpoints
- WebSocket support
- CORTEX repository detection
