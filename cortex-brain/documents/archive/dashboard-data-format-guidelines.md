# Dashboard Data Format Guidelines
**Version:** 1.0  
**Audience:** CORTEX Users  
**Purpose:** Generate compatible JSON data for CORTEX repository dashboards  
**Author:** Asif Hussain

---

## What This Document Is For

This guide is for **CORTEX users** who want to generate JSON data that works with the CORTEX repository dashboard. If you're building a repository scanner, code analyzer, or any tool that generates dashboard data, follow these specifications **exactly**.

**Not a developer guide:** This is runtime documentation shipped with CORTEX. Developers should see implementation guides in the CORTEX repository.

---

## File Requirements

### Required Files (7 files)

All files must be placed in the data source directory (e.g., `/cortex/`, `/noor-canvas/`):

1. **health-data.json** - Overall repository health metrics
2. **tech-stack.json** - Technology inventory (languages, frameworks, tools)
3. **security.json** - Security vulnerabilities and OWASP compliance
4. **architecture.json** - Code architecture and component structure
5. **code-organization.json** - Code complexity heatmap and hotspots
6. **team-metrics.json** - Git activity and contributor statistics
7. **vendors.json** - Third-party services and dependencies

---

## JSON Schemas

### 1. health-data.json

**Purpose:** Repository health overview and key metrics

```json
{
  "overall_health_score": 65,                    // Required: integer 0-100
  "status": "warning",                           // Required: "healthy" | "warning" | "critical"
  "last_scan": "2025-12-04T12:46:23.666759",    // Required: ISO 8601 timestamp
  "summary": {                                   // Required
    "total_files": 994,                          // Required: integer
    "total_loc": 45678,                          // Required: integer (lines of code)
    "test_coverage": 45.2,                       // Required: float (percentage)
    "critical_issues": 2,                        // Required: integer
    "warnings": 12,                              // Required: integer
    "maintainability_index": 58                  // Required: integer 0-100
  },
  "metrics": {                                   // Required
    "code_quality_score": 62,                    // Required: integer 0-100
    "security_score": 54,                        // Required: integer 0-100
    "test_score": 48,                            // Required: integer 0-100
    "documentation_score": 75                    // Required: integer 0-100
  },
  "trends": {                                    // Required
    "health_trend": "declining",                 // Required: "improving" | "stable" | "declining"
    "velocity_trend": "stable",                  // Required: "improving" | "stable" | "declining"
    "quality_trend": "declining"                 // Required: "improving" | "stable" | "declining"
  }
}
```

**Validation Rules:**
- All scores must be integers 0-100
- Timestamp must be valid ISO 8601 format
- Status values are restricted to: `healthy`, `warning`, `critical`
- Trend values are restricted to: `improving`, `stable`, `declining`

---

### 2. tech-stack.json

**Purpose:** Complete technology inventory with version tracking

```json
{
  "frontend": [                                  // Required: array (can be empty)
    {
      "name": "React",                           // Required: string
      "version": "18.2.0",                       // Required: string (semver format)
      "latest": "18.2.0",                        // Required: string (semver format)
      "status": "current",                       // Required: "current" | "outdated" | "deprecated" | "vulnerable"
      "category": "framework",                   // Required: "framework" | "language" | "build_tool" | "library"
      "cve_count": 0,                            // Required: integer (>=0)
      "eol_date": null                           // Optional: ISO 8601 date or null
    }
  ],
  "backend": [                                   // Required: array (can be empty)
    {
      "name": "Python",
      "version": "3.11.5",
      "latest": "3.12.0",
      "status": "current",
      "category": "language",
      "cve_count": 0,
      "eol_date": null
    }
  ],
  "database": [                                  // Required: array (can be empty)
    {
      "name": "SQLite",
      "version": "3.43.0",
      "latest": "3.44.0",
      "status": "current",
      "category": "database",
      "cve_count": 0,
      "eol_date": null
    }
  ],
  "devops": [                                    // Optional: array
    {
      "name": "Docker",
      "version": "24.0.5",
      "latest": "24.0.7",
      "status": "current",
      "category": "container",
      "cve_count": 0,
      "eol_date": null
    }
  ]
}
```

**Validation Rules:**
- At least one of `frontend`, `backend`, `database` must be present
- Status values: `current`, `outdated`, `deprecated`, `vulnerable`
- Category values: `framework`, `language`, `build_tool`, `library`, `database`, `container`, `orchestration`
- Versions must follow semver format (X.Y.Z)
- `cve_count` must be non-negative integer

---

### 3. security.json

**Purpose:** Security vulnerabilities and OWASP Top 10 compliance

**⚠️ CRITICAL:** The `owasp_top_10` field is an **OBJECT** with a `categories` array, NOT a direct array.

```json
{
  "overall_score": 72,                           // Required: integer 0-100
  "last_scan": "2025-12-04T12:46:23.666770",    // Required: ISO 8601 timestamp
  "vulnerabilities": {                           // Required
    "total": 24,                                 // Required: integer
    "critical": 1,                               // Required: integer
    "high": 3,                                   // Required: integer
    "medium": 8,                                 // Required: integer
    "low": 12,                                   // Required: integer
    "by_package": [                              // Optional: array
      {
        "package": "lodash",                     // Required: string
        "version": "4.17.19",                    // Required: string
        "severity": "medium",                    // Required: "critical" | "high" | "medium" | "low"
        "cve": "CVE-2020-8203"                   // Required: string
      }
    ]
  },
  "owasp_top_10": {                              // ⚠️ OBJECT (not array!)
    "pass_count": 6,                             // Required: integer
    "warn_count": 3,                             // Required: integer
    "fail_count": 1,                             // Required: integer
    "categories": [                              // ⚠️ ARRAY inside object
      {
        "id": "A01",                             // Required: string (A01-A10)
        "name": "Broken Access Control",         // Required: string
        "status": "pass",                        // Required: "pass" | "warn" | "fail"
        "score": 95                              // Required: integer 0-100
      },
      {
        "id": "A02",
        "name": "Cryptographic Failures",
        "status": "pass",
        "score": 92
      },
      {
        "id": "A03",
        "name": "Injection",
        "status": "pass",
        "score": 98
      },
      {
        "id": "A04",
        "name": "Insecure Design",
        "status": "pass",
        "score": 88
      },
      {
        "id": "A05",
        "name": "Security Misconfiguration",
        "status": "warn",
        "score": 78
      },
      {
        "id": "A06",
        "name": "Vulnerable Components",
        "status": "pass",
        "score": 90
      },
      {
        "id": "A07",
        "name": "Authentication Failures",
        "status": "pass",
        "score": 94
      },
      {
        "id": "A08",
        "name": "Data Integrity Failures",
        "status": "pass",
        "score": 96
      },
      {
        "id": "A09",
        "name": "Logging Failures",
        "status": "pass",
        "score": 85
      },
      {
        "id": "A10",
        "name": "SSRF",
        "status": "pass",
        "score": 100
      }
    ]
  },
  "compliance": {                                // Required
    "gdpr_ready": false,                         // Required: boolean
    "soc2_ready": false,                         // Required: boolean
    "hipaa_ready": false,                        // Required: boolean
    "pci_dss_ready": false                       // Required: boolean
  },
  "summary": {                                   // Required
    "total_issues": 24,                          // Required: integer
    "high_priority": 4,                          // Required: integer
    "hardcoded_secrets": 2,                      // Required: integer
    "weak_crypto": 1                             // Required: integer
  }
}
```

**⚠️ CRITICAL NOTES:**
- **OWASP structure:** `owasp_top_10` is an object containing:
  - `pass_count`, `warn_count`, `fail_count` (integers)
  - `categories` array (10 items for OWASP Top 10 2021)
- **Legacy format NOT supported:** Direct array like `"owasp_top_10": [...]` will cause errors
- **Category IDs:** Must be A01-A10 (OWASP 2021 standard)
- **Status values:** `pass`, `warn`, `fail` only
- **Severity values:** `critical`, `high`, `medium`, `low` only

---

### 4. architecture.json

**Purpose:** Code architecture layers, components, and database schema

```json
{
  "style": "clean_architecture",                 // Required: string
  "score": 75,                                   // Required: integer 0-100
  "last_scan": "2025-12-04T12:46:23.666774",    // Required: ISO 8601 timestamp
  "tiers": [                                     // Required: array
    {
      "name": "presentation",                    // Required: string
      "component_count": 12,                     // Required: integer
      "loc": 8450,                               // Required: integer
      "description": "UI components, views"      // Required: string
    },
    {
      "name": "application",
      "component_count": 28,
      "loc": 15230,
      "description": "Business logic, use cases"
    },
    {
      "name": "domain",
      "component_count": 8,
      "loc": 4560,
      "description": "Core entities, domain models"
    },
    {
      "name": "infrastructure",
      "component_count": 7,
      "loc": 5890,
      "description": "Data access, external services"
    }
  ],
  "components": [                                // Required: array
    {
      "name": "UserFeature",                     // Required: string
      "tier": "application",                     // Required: string (matches tier name)
      "loc": 1250,                               // Required: integer
      "complexity": 42,                          // Required: integer
      "dependencies": [                          // Required: array (can be empty)
        "UserRepository",
        "ValidationService"
      ]
    }
  ],
  "database_schema": {                           // Optional: object
    "tables": [
      {
        "name": "users",                         // Required: string
        "columns": 12,                           // Required: integer
        "relationships": [                       // Optional: array
          {
            "table": "sessions",                 // Required: string
            "type": "one_to_many"                // Required: "one_to_one" | "one_to_many" | "many_to_many"
          }
        ]
      }
    ]
  }
}
```

**Validation Rules:**
- `tiers` must have at least 1 tier
- `components` must have at least 1 component
- Each component's `tier` must match a tier `name`
- Relationship types: `one_to_one`, `one_to_many`, `many_to_many`

---

### 5. code-organization.json

**Purpose:** Code complexity heatmap and problem hotspots

```json
{
  "heatmap": [                                   // Required: array
    {
      "directory": "src/entry_point/",           // Required: string (with trailing /)
      "file_count": 8,                           // Required: integer
      "total_loc": 3450,                         // Required: integer
      "avg_complexity": 68,                      // Required: integer
      "max_complexity": 163,                     // Required: integer
      "files": [                                 // Optional: array (top files)
        {
          "name": "cortex_entry.py",             // Required: string
          "loc": 825,                            // Required: integer
          "complexity": 91                       // Required: integer
        }
      ]
    }
  ],
  "hotspots": [                                  // Required: array
    {
      "file": "src/entry_point/cortex_entry.py",// Required: string (full path)
      "loc": 825,                                // Required: integer
      "complexity": 91,                          // Required: integer
      "change_frequency": 18,                    // Required: integer (commits touching file)
      "risk_score": 100,                         // Required: integer 0-100
      "recommendation": "Split into modules"     // Required: string
    }
  ],
  "complexity_distribution": {                   // Required: object
    "low": 526,                                  // Required: integer (files with low complexity)
    "medium": 350,                               // Required: integer
    "high": 100,                                 // Required: integer
    "very_high": 18                              // Required: integer
  }
}
```

**Validation Rules:**
- Directory paths should end with `/`
- Risk scores must be 0-100
- Complexity categories: `low`, `medium`, `high`, `very_high`
- Hotspots should be sorted by `risk_score` (descending)

---

### 6. team-metrics.json

**Purpose:** Git activity, contributors, and development velocity

```json
{
  "contributors": [                              // Required: array
    {
      "name": "Asif Hussain",                    // Required: string
      "email": "asif@example.com",               // Required: string
      "commits": 856,                            // Required: integer
      "lines_added": 125430,                     // Required: integer
      "lines_deleted": 45230,                    // Required: integer
      "active_days": 145,                        // Required: integer
      "first_commit": "2025-06-07T12:46:23Z",   // Required: ISO 8601 timestamp
      "last_commit": "2025-12-04T12:46:23Z"     // Required: ISO 8601 timestamp
    }
  ],
  "velocity": {                                  // Required: object
    "commits_per_week": [                        // Required: array (last 5-10 weeks)
      {
        "week": "2025-W48",                      // Required: ISO week format (YYYY-WNN)
        "commits": 42                            // Required: integer
      }
    ],
    "trend": "stable",                           // Required: "increasing" | "stable" | "decreasing"
    "avg_commits_per_week": 43                   // Required: integer
  },
  "commit_trends": {                             // Optional: object
    "by_hour": {                                 // Optional: object (24-hour keys)
      "09": 45,                                  // Key: 2-digit hour, Value: commit count
      "10": 78,
      "14": 67
    },
    "by_day": {                                  // Optional: object (day names)
      "Monday": 234,
      "Tuesday": 267,
      "Wednesday": 289
    }
  },
  "summary": {                                   // Required: object
    "total_contributors": 4,                     // Required: integer
    "total_commits": 1236,                       // Required: integer
    "active_contributors": 4,                    // Required: integer (active in last 30 days)
    "bus_factor": 1,                             // Required: integer (contributors with >50% commits)
    "avg_commits_per_contributor": 309,          // Required: integer
    "avg_commits_per_week": 43,                  // Required: integer
    "last_scan": "2025-12-04T12:46:23Z"         // Required: ISO 8601 timestamp
  }
}
```

**Validation Rules:**
- Contributors must be sorted by commit count (descending)
- Week format: `YYYY-WNN` (ISO 8601 week numbers)
- Hour keys: 2-digit strings `"00"` to `"23"`
- Day keys: Full day names (Monday-Sunday)
- Trend values: `increasing`, `stable`, `decreasing`

---

### 7. vendors.json

**Purpose:** Third-party services, APIs, and external dependencies

```json
{
  "vendors": [                                   // Required: array
    {
      "name": "Stripe",                          // Required: string
      "category": "payment",                     // Required: string
      "status": "active",                        // Required: "active" | "configured" | "inactive" | "deprecated"
      "cost_tier": "$$$",                        // Required: "$" | "$$" | "$$$" | "$$$$" | "free"
      "detection_method": "sdk_import",          // Required: "sdk_import" | "env_var" | "config_file" | "api_call"
      "files_using": [                           // Required: array (can be empty)
        "src/payments/stripe_client.py",
        "src/api/checkout.py"
      ],
      "env_vars": [                              // Optional: array
        "STRIPE_API_KEY",
        "STRIPE_WEBHOOK_SECRET"
      ],
      "compliance": [                            // Optional: array
        "PCI_DSS",
        "GDPR"
      ],
      "security_notes": "API keys in env vars"   // Optional: string
    }
  ],
  "summary": {                                   // Required: object
    "total_vendors": 5,                          // Required: integer
    "active_vendors": 4,                         // Required: integer
    "configured_vendors": 1,                     // Required: integer
    "total_cost_estimate": "$$$$",               // Required: "$" to "$$$$" or "unknown"
    "categories": {                              // Required: object
      "payment": 1,                              // Key: category name, Value: count
      "authentication": 1,
      "storage": 1,
      "email": 1,
      "monitoring": 1
    }
  }
}
```

**Validation Rules:**
- Status values: `active`, `configured`, `inactive`, `deprecated`
- Cost tier values: `$`, `$$`, `$$$`, `$$$$`, `free`
- Detection methods: `sdk_import`, `env_var`, `config_file`, `api_call`
- Compliance values: `PCI_DSS`, `GDPR`, `HIPAA`, `SOC2`, `ISO27001`

---

## Data Generation Workflow

### 1. Pre-Generation Checklist
- [ ] Identify target repository path
- [ ] Determine data source name (e.g., `cortex`, `noor-canvas`)
- [ ] Create output directory: `cortex-brain/dashboards/{source}/`
- [ ] Verify Python environment and dependencies

### 2. Generation Process
```python
# Example structure for repo scanner
class RepositoryScanner:
    def scan_repository(self, repo_path: str, output_dir: str):
        """Scan repository and generate all 7 JSON files"""
        
        # Generate each file
        health_data = self.generate_health_data(repo_path)
        tech_stack = self.generate_tech_stack(repo_path)
        security = self.generate_security(repo_path)
        architecture = self.generate_architecture(repo_path)
        code_org = self.generate_code_organization(repo_path)
        team_metrics = self.generate_team_metrics(repo_path)
        vendors = self.generate_vendors(repo_path)
        
        # Write to files
        self.write_json(output_dir, 'health-data.json', health_data)
        self.write_json(output_dir, 'tech-stack.json', tech_stack)
        self.write_json(output_dir, 'security.json', security)
        self.write_json(output_dir, 'architecture.json', architecture)
        self.write_json(output_dir, 'code-organization.json', code_org)
        self.write_json(output_dir, 'team-metrics.json', team_metrics)
        self.write_json(output_dir, 'vendors.json', vendors)
    
    def write_json(self, output_dir: str, filename: str, data: dict):
        """Write JSON with proper formatting"""
        import json
        from pathlib import Path
        
        output_path = Path(output_dir) / filename
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
```

### 3. Validation
After generation, validate each file:

```python
import json
from pathlib import Path

def validate_data_files(output_dir: str) -> list[str]:
    """Validate all 7 required JSON files exist and are valid"""
    required_files = [
        'health-data.json',
        'tech-stack.json',
        'security.json',
        'architecture.json',
        'code-organization.json',
        'team-metrics.json',
        'vendors.json'
    ]
    
    errors = []
    for filename in required_files:
        filepath = Path(output_dir) / filename
        
        # Check file exists
        if not filepath.exists():
            errors.append(f"Missing file: {filename}")
            continue
        
        # Check valid JSON
        try:
            with filepath.open('r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {filename}: {e}")
            continue
        
        # Check required top-level keys
        if filename == 'health-data.json':
            required_keys = ['overall_health_score', 'status', 'last_scan', 'summary', 'metrics', 'trends']
            missing = [k for k in required_keys if k not in data]
            if missing:
                errors.append(f"{filename} missing keys: {missing}")
        
        # Add more validation for other files...
    
    return errors
```

---

## Common Mistakes to Avoid

### ❌ WRONG: Direct OWASP array
```json
{
  "owasp_top_10": [
    {"id": "A01", "name": "Broken Access Control", "status": "pass"}
  ]
}
```

### ✅ CORRECT: OWASP as object with categories
```json
{
  "owasp_top_10": {
    "pass_count": 6,
    "warn_count": 3,
    "fail_count": 1,
    "categories": [
      {"id": "A01", "name": "Broken Access Control", "status": "pass", "score": 95}
    ]
  }
}
```

---

### ❌ WRONG: Incomplete timestamp
```json
{
  "last_scan": "2025-12-04"
}
```

### ✅ CORRECT: Full ISO 8601 timestamp
```json
{
  "last_scan": "2025-12-04T12:46:23.666770"
}
```

---

### ❌ WRONG: Invalid status value
```json
{
  "status": "ok"  // Not a valid value
}
```

### ✅ CORRECT: Valid status value
```json
{
  "status": "healthy"  // Must be: healthy, warning, or critical
}
```

---

### ❌ WRONG: Missing required fields
```json
{
  "frontend": [
    {
      "name": "React",
      "version": "18.2.0"
      // Missing: latest, status, category, cve_count, eol_date
    }
  ]
}
```

### ✅ CORRECT: All required fields
```json
{
  "frontend": [
    {
      "name": "React",
      "version": "18.2.0",
      "latest": "18.2.0",
      "status": "current",
      "category": "framework",
      "cve_count": 0,
      "eol_date": null
    }
  ]
}
```

---

## Testing Generated Data

### Manual Test
1. Copy generated files to `cortex-brain/dashboards/mock/`
2. Start HTTP server: `cd cortex-brain/dashboards/ && python -m http.server 8080`
3. Open browser: `http://localhost:8080/ui/index.html?source=mock`
4. Check browser console for errors
5. Verify all 7 tabs load correctly

### Automated Test
```python
def test_dashboard_compatibility(data_dir: str):
    """Test that generated data works with dashboard"""
    import requests
    import time
    
    # Start HTTP server (in background)
    # ...
    
    # Wait for server
    time.sleep(2)
    
    # Test each data file loads
    base_url = 'http://localhost:8080'
    files = [
        'health-data.json',
        'tech-stack.json',
        'security.json',
        'architecture.json',
        'code-organization.json',
        'team-metrics.json',
        'vendors.json'
    ]
    
    for file in files:
        url = f"{base_url}/mock/{file}"
        response = requests.get(url)
        assert response.status_code == 200, f"Failed to load {file}"
        
        # Validate JSON structure
        data = response.json()
        assert isinstance(data, dict), f"{file} must be a JSON object"
        
        # File-specific validation
        if file == 'security.json':
            assert 'owasp_top_10' in data, "Missing owasp_top_10"
            assert 'categories' in data['owasp_top_10'], "owasp_top_10 must have categories"
            assert isinstance(data['owasp_top_10']['categories'], list), "categories must be array"
```

---

## Timestamp Generation

**Always use ISO 8601 format with microseconds:**

```python
from datetime import datetime

# Current timestamp
timestamp = datetime.now().isoformat()
# Output: "2025-12-04T12:46:23.666770"

# UTC timestamp (recommended)
timestamp = datetime.utcnow().isoformat() + 'Z'
# Output: "2025-12-04T12:46:23.666770Z"
```

---

## Empty Data Handling

Some fields can be empty arrays or null:

```json
{
  "frontend": [],                    // ✅ OK: Empty array
  "devops": [],                      // ✅ OK: Empty array
  "files_using": [],                 // ✅ OK: Empty array
  "env_vars": [],                    // ✅ OK: Empty array
  "eol_date": null,                  // ✅ OK: Null value
  "database_schema": null            // ✅ OK: Null for optional field
}
```

**Never use:**
```json
{
  "frontend": null,                  // ❌ WRONG: Should be empty array []
  "tiers": [],                       // ❌ WRONG: Required field, must have at least 1 item
  "contributors": []                 // ❌ WRONG: Required field, must have at least 1 item
}
```

---

## Performance Considerations

### File Size Limits
- **Recommended:** Each JSON file <500KB
- **Maximum:** Each JSON file <2MB
- Large files slow dashboard loading

### Optimization Tips
1. **Limit array sizes:**
   - Tech stack: Top 50 packages per category
   - Hotspots: Top 20 files
   - Contributors: Top 50 contributors
   - Velocity: Last 12 weeks only

2. **Remove unnecessary fields:**
   - Omit optional fields if no data
   - Don't include empty objects

3. **Compress repeated data:**
   - Use references instead of duplicating large objects
   - Consider normalizing deeply nested structures

---

## Version Compatibility

**Current Version:** 1.0  
**Dashboard Version:** Compatible with cortex-brain/dashboards/ui/ (commit 35e1fc72+)

**Breaking Changes:**
- Version 1.0: Initial release
- Future versions will maintain backward compatibility

**Deprecation Policy:**
- Field deprecations announced 6 months in advance
- Legacy formats supported for 1 year

---

## Support & Questions

**Documentation Location:** `cortex-brain/documents/implementation-guides/`

**Reference Implementation:** See `cortex-brain/dashboards/mock/` for complete examples

**Validation Tools:**
- JSON schema validators (jsonschema library)
- Dashboard integration tests (`cortex-brain/dashboards/ui/tests/`)

---

## Summary Checklist

Before deploying generated data:

- [ ] All 7 JSON files exist
- [ ] All files are valid JSON (no syntax errors)
- [ ] All required fields present for each schema
- [ ] All timestamps in ISO 8601 format
- [ ] All enum values match allowed values
- [ ] All scores are integers 0-100
- [ ] OWASP structure is object with categories array
- [ ] All arrays contain proper objects (no primitives where objects expected)
- [ ] File sizes <2MB each
- [ ] Tested in dashboard (all tabs load without errors)

---

**Last Updated:** December 2025  
**Maintainer:** Asif Hussain  
**License:** Source-Available (CORTEX Project)
