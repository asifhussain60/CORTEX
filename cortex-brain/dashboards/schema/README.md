# Universal Health Data Schema

**Version:** 1.0.0  
**Created:** December 4, 2025  
**Schema File:** `health-data-schema.json`  
**Purpose:** Standardized health data format for unified dashboard supporting multiple applications

---

## 📋 Overview

The Universal Health Data Schema defines a standardized format for application health metrics that works across different applications (CORTEX, NOOR CANVAS, ALIST, KSESSIONS, etc.). All applications generate data conforming to this schema, enabling a single dashboard UI to display health information for any application.

---

## 🎯 Design Principles

1. **Universal Core:** All apps must provide core metrics (metadata, health, code_metrics, code_quality)
2. **Optional Enhancements:** Advanced sections (testing, security, performance) are optional
3. **Extensibility:** `custom_metrics` object allows app-specific fields
4. **Type Safety:** JSON Schema validation ensures data integrity
5. **Versioning:** Schema version field enables evolution without breaking changes
6. **Standards-Compliant:** Uses ISO 8601 for timestamps, 0-100 for percentages and scores

---

## 📐 Schema Structure

### Required Sections

#### 1. `metadata` (REQUIRED)
Repository and scan information.

**Required Fields:**
- `repo_name` (string) - Application name
- `branch` (string) - Current branch
- `commit_hash` (string) - Latest commit SHA (7-40 hex chars)
- `commit_date` (ISO 8601) - Commit timestamp
- `last_scan` (ISO 8601) - Scan timestamp

**Optional Fields:**
- `repo_url` (URI) - Repository URL
- `scan_duration_seconds` (number) - Scan execution time
- `scanner_version` (string) - Scanner tool version

#### 2. `health` (REQUIRED)
Overall health indicators.

**Required Fields:**
- `overall_score` (0-100 integer) - Composite health score
- `trend` (enum) - `improving`, `stable`, or `degrading`
- `status` (enum) - `healthy` (80-100), `warning` (50-79), or `critical` (0-49)

#### 3. `code_metrics` (REQUIRED)
Code size and composition.

**Required Fields:**
- `lines_of_code` (integer) - Total LOC (excluding comments/blanks)
- `file_count` (integer) - Total files
- `directory_count` (integer) - Total directories

**Optional Fields:**
- `language_breakdown` (object) - LOC by language (e.g., `{"Python": 15000}`)

#### 4. `code_quality` (REQUIRED)
Quality and maintainability metrics.

**Required Fields:**
- `complexity_score` (0-100 integer) - Inverse complexity (100=simple)
- `maintainability_index` (0-100 integer) - Microsoft MI metric

**Optional Fields:**
- `cyclomatic_complexity_avg` (number) - Average cyclomatic complexity
- `cognitive_complexity_avg` (number) - Average cognitive load
- `code_duplication_pct` (0-100) - Duplication percentage
- `comment_ratio_pct` (0-100) - Comment ratio

### Optional Sections

#### 5. `testing` (OPTIONAL)
Test coverage and execution.

**Fields:**
- `coverage_pct` (0-100) - Overall test coverage
- `unit_test_count` (integer) - Unit test count
- `integration_test_count` (integer) - Integration test count
- `test_pass_rate_pct` (0-100) - Passing test percentage

#### 6. `issues` (OPTIONAL)
Open issues and technical debt.

**Fields:**
- `total_count` (integer) - Total open issues
- `by_severity` (object) - Breakdown: `critical`, `high`, `medium`, `low`
- `technical_debt_days` (number) - Estimated debt resolution time
- `code_smells_count` (integer) - Anti-patterns detected

#### 7. `dependencies` (OPTIONAL)
Dependency health and security.

**Fields:**
- `total` (integer) - Total dependencies
- `direct` (integer) - Direct dependencies
- `transitive` (integer) - Nested dependencies
- `outdated` (integer) - Dependencies needing updates
- `vulnerable` (integer) - Dependencies with CVEs
- `health_score` (0-100) - Overall dependency health

#### 8. `security` (OPTIONAL)
Security posture and vulnerabilities.

**Fields:**
- `score` (0-100) - Overall security score
- `vulnerabilities` (object) - Breakdown: `critical`, `high`, `medium`, `low`
- `secrets_exposed` (integer) - Exposed API keys/passwords
- `last_scan` (ISO 8601) - Last security scan timestamp

#### 9. `performance` (OPTIONAL)
Performance and deployment metrics.

**Fields:**
- `build_time_seconds` (number) - Average build duration
- `test_execution_time_seconds` (number) - Test suite runtime
- `deployment_frequency` (enum) - `multiple_per_day`, `daily`, `weekly`, `monthly`, etc.
- `mean_time_to_recovery_hours` (number) - MTTR for incidents

#### 10. `activity` (OPTIONAL)
Development activity metrics.

**Fields:**
- `commits_last_30_days` (integer) - Recent commits
- `contributors_active` (integer) - Active contributors (90 days)
- `pull_requests_open` (integer) - Open PRs
- `pull_requests_merged_last_30_days` (integer) - Recently merged PRs

#### 11. `custom_metrics` (OPTIONAL)
Application-specific metrics.

**Examples:**
- **CORTEX:** `brain_tier_sizes`, `conversation_count`, `orchestrator_executions`
- **NOOR CANVAS:** `canvas_templates`, `user_sessions`, `feature_usage`
- **ALIST:** `list_operations`, `api_response_time`, `cache_hit_rate`
- **KSESSIONS:** `session_count`, `session_duration_avg`, `knowledge_entries`

---

## 📊 Example: Minimal Valid Data

```json
{
  "metadata": {
    "repo_name": "My-App",
    "branch": "main",
    "commit_hash": "abc1234",
    "commit_date": "2025-12-04T10:00:00-05:00",
    "last_scan": "2025-12-04T10:05:00-05:00"
  },
  "health": {
    "overall_score": 85,
    "trend": "stable",
    "status": "healthy"
  },
  "code_metrics": {
    "lines_of_code": 10000,
    "file_count": 150,
    "directory_count": 30
  },
  "code_quality": {
    "complexity_score": 75,
    "maintainability_index": 80
  }
}
```

---

## 📊 Example: Complete Data

```json
{
  "metadata": {
    "repo_name": "CORTEX",
    "repo_url": "https://github.com/asifhussain60/CORTEX",
    "branch": "CORTEX-3.0",
    "commit_hash": "994eb319",
    "commit_date": "2025-12-04T09:44:28-05:00",
    "last_scan": "2025-12-04T10:00:00-05:00",
    "scan_duration_seconds": 42.5,
    "scanner_version": "CORTEX-3.5.5"
  },
  "health": {
    "overall_score": 88,
    "trend": "improving",
    "status": "healthy"
  },
  "code_metrics": {
    "lines_of_code": 18500,
    "file_count": 275,
    "directory_count": 85,
    "language_breakdown": {
      "Python": 15000,
      "YAML": 2500,
      "Markdown": 1000
    }
  },
  "code_quality": {
    "complexity_score": 82,
    "maintainability_index": 78,
    "cyclomatic_complexity_avg": 6.2,
    "cognitive_complexity_avg": 4.8,
    "code_duplication_pct": 3.5,
    "comment_ratio_pct": 18.0
  },
  "testing": {
    "coverage_pct": 68.5,
    "unit_test_count": 125,
    "integration_test_count": 45,
    "test_pass_rate_pct": 97.8
  },
  "issues": {
    "total_count": 15,
    "by_severity": {
      "critical": 0,
      "high": 2,
      "medium": 8,
      "low": 5
    },
    "technical_debt_days": 4.2,
    "code_smells_count": 12
  },
  "dependencies": {
    "total": 98,
    "direct": 28,
    "transitive": 70,
    "outdated": 5,
    "vulnerable": 0,
    "health_score": 92
  },
  "security": {
    "score": 95,
    "vulnerabilities": {
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 1
    },
    "secrets_exposed": 0,
    "last_scan": "2025-12-04T09:00:00-05:00"
  },
  "performance": {
    "build_time_seconds": 0,
    "test_execution_time_seconds": 15.3,
    "deployment_frequency": "weekly",
    "mean_time_to_recovery_hours": 2.5
  },
  "activity": {
    "commits_last_30_days": 145,
    "contributors_active": 1,
    "pull_requests_open": 0,
    "pull_requests_merged_last_30_days": 0
  },
  "custom_metrics": {
    "brain_tier_sizes_mb": {
      "tier1": 2.5,
      "tier2": 8.3,
      "tier3": 5.1
    },
    "conversation_count": 250,
    "orchestrator_executions_last_week": 42
  }
}
```

---

## 🔧 Extending the Schema

### Adding Custom Metrics

Applications can add custom metrics in the `custom_metrics` object:

```json
{
  "custom_metrics": {
    "my_custom_metric": 123,
    "another_metric": "string value",
    "nested_metric": {
      "sub_field": 456
    }
  }
}
```

**Best Practices:**
- Use descriptive names (`user_session_count` not `usc`)
- Document custom metrics in app-specific documentation
- Use consistent units (seconds, bytes, percentages)
- Avoid duplication of core schema fields

---

## ✅ Validation

### Using JSON Schema Validator

```python
import json
import jsonschema

# Load schema
with open('health-data-schema.json', 'r') as f:
    schema = json.load(f)

# Load data
with open('health-data.json', 'r') as f:
    data = json.load(f)

# Validate
try:
    jsonschema.validate(data, schema)
    print("✓ Data is valid!")
except jsonschema.ValidationError as e:
    print(f"✗ Validation error: {e.message}")
```

### Common Validation Errors

1. **Missing required field:**
   ```
   'repo_name' is a required property in 'metadata'
   ```

2. **Invalid type:**
   ```
   85.5 is not of type 'integer' for 'overall_score'
   ```

3. **Out of range:**
   ```
   150 is greater than the maximum of 100 for 'complexity_score'
   ```

4. **Invalid enum value:**
   ```
   'excellent' is not one of ['improving', 'stable', 'degrading']
   ```

---

## 📁 File Organization

### Per-Application Data Structure

```
cortex-brain/dashboards/
├── schema/
│   ├── health-data-schema.json      # This schema
│   └── README.md                    # This documentation
├── mock/
│   └── health-data.json             # Mock data for development
├── cortex/
│   └── health-data.json             # CORTEX health data
├── noor-canvas/
│   └── health-data.json             # NOOR CANVAS health data
├── alist/
│   └── health-data.json             # ALIST health data
└── ksessions/
    └── health-data.json             # KSESSIONS health data
```

**Naming Convention:** Always `health-data.json` (consistent across all apps)

---

## 🎯 Dashboard Integration

### URL-Driven Routing

Dashboard loads data based on URL parameter:
- `/dashboard/mock` → Loads `dashboards/mock/health-data.json`
- `/dashboard/cortex` → Loads `dashboards/cortex/health-data.json`
- `/dashboard/noor-canvas` → Loads `dashboards/noor-canvas/health-data.json`

### Tab Rendering

Dashboard UI automatically adapts based on available data:
- **Required tabs:** Overview (always present)
- **Optional tabs:** Metrics, Quality, Dependencies, Security (only if data exists)

**Example:** If `security` section is missing, Security tab is hidden.

---

## 📚 Additional Resources

- **Schema File:** `health-data-schema.json`
- **Mock Data Examples:** `../mock/health-data.json` (Phase 2)
- **Schema Validator:** `schema-validator.py` (Phase 2)
- **Dashboard Consolidation Plan:** `../../documents/planning/dashboard-consolidation-plan.md`

---

**Schema Version:** 1.0.0  
**Last Updated:** December 4, 2025  
**Maintained By:** CORTEX Project  
**License:** Source-Available (Use Allowed, No Contributions)
