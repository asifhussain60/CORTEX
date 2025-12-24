# Phase 1 Discovery Report - Universal Health Data Schema Design

**Phase:** Phase 1 - Repository Data Discovery & Schema Design  
**Plan ID:** unified-dashboard-2025-12-04  
**Started:** December 4, 2025  
**Status:** 🔄 IN PROGRESS

---

## 📋 Discovery Approach - Adjusted Strategy

### Original Plan
Scan NOOR CANVAS, ALIST, KSESSIONS repositories to extract real-world data patterns.

### Adjusted Approach (Mock-First Philosophy)
**Reason for Adjustment:** External repositories not available locally at `/Users/asifhussain/PROJECTS/`

**New Strategy:**
1. ✅ Design universal schema based on industry-standard application health metrics
2. ✅ Reference CORTEX's existing health metrics as baseline
3. ✅ Create extensible schema that accommodates application-specific metrics
4. ✅ Generate realistic mock data based on typical application patterns
5. ⏭️ Validate with actual repos when available (future enhancement)

**Benefits of Mock-First:**
- Schema design independent of repository availability
- Faster iteration on dashboard UI/UX
- Schema becomes the contract for future integrations
- Can proceed immediately without blocking on external dependencies

---

## 🎯 Universal Health Metrics (Industry Standard)

### Core Metrics (All Applications Must Provide)

#### 1. **Repository Overview**
- `repo_name` (string) - Application/repository name
- `repo_url` (string, optional) - GitHub/GitLab URL
- `branch` (string) - Current branch (dev, main, develop, etc.)
- `commit_hash` (string) - Latest commit SHA
- `commit_date` (ISO 8601 timestamp) - Last commit timestamp
- `last_scan` (ISO 8601 timestamp) - When health data was generated

#### 2. **Overall Health Score**
- `overall_health_score` (0-100) - Composite health indicator
- `health_trend` (enum: improving, stable, degrading) - Direction of health change
- `health_status` (enum: healthy, warning, critical) - Traffic light indicator
  - healthy: 80-100
  - warning: 50-79
  - critical: 0-49

#### 3. **Code Metrics**
- `lines_of_code` (integer) - Total LOC (excluding comments/blanks)
- `file_count` (integer) - Total number of files
- `directory_count` (integer) - Total number of directories
- `language_breakdown` (object) - Lines per language
  ```json
  {
    "Python": 15000,
    "TypeScript": 8500,
    "C#": 12000,
    "HTML/CSS": 3000
  }
  ```

#### 4. **Code Quality**
- `complexity_score` (0-100) - Inverse of complexity (100=simple, 0=complex)
- `maintainability_index` (0-100) - Code maintainability (Microsoft metric)
- `cyclomatic_complexity_avg` (float) - Average complexity per function
- `cognitive_complexity_avg` (float) - Average cognitive load
- `code_duplication_pct` (0-100) - Percentage of duplicated code
- `comment_ratio_pct` (0-100) - Comments / total lines

#### 5. **Test Coverage**
- `test_coverage_pct` (0-100) - Overall test coverage percentage
- `unit_test_count` (integer) - Number of unit tests
- `integration_test_count` (integer) - Number of integration tests
- `test_pass_rate_pct` (0-100) - Percentage of passing tests

#### 6. **Issues & Technical Debt**
- `open_issues_count` (integer) - Total open issues
- `critical_issues_count` (integer) - P0/Critical severity
- `high_issues_count` (integer) - P1/High severity
- `medium_issues_count` (integer) - P2/Medium severity
- `low_issues_count` (integer) - P3/Low severity
- `technical_debt_days` (float) - Estimated days to resolve debt
- `code_smells_count` (integer) - Anti-patterns detected

#### 7. **Dependencies**
- `total_dependencies` (integer) - All dependencies
- `direct_dependencies` (integer) - Top-level dependencies
- `transitive_dependencies` (integer) - Nested dependencies
- `outdated_dependencies` (integer) - Dependencies with updates available
- `vulnerable_dependencies` (integer) - Dependencies with known CVEs
- `dependency_health_score` (0-100) - Overall dependency health

#### 8. **Security**
- `security_score` (0-100) - Overall security posture
- `vulnerabilities_critical` (integer) - Critical CVEs
- `vulnerabilities_high` (integer) - High severity CVEs
- `vulnerabilities_medium` (integer) - Medium severity CVEs
- `vulnerabilities_low` (integer) - Low severity CVEs
- `secrets_exposed` (integer) - Exposed API keys/passwords
- `last_security_scan` (ISO 8601 timestamp)

#### 9. **Performance Indicators**
- `build_time_seconds` (float) - Average build duration
- `test_execution_time_seconds` (float) - Average test suite runtime
- `deployment_frequency` (string) - "daily", "weekly", "monthly"
- `mean_time_to_recovery_hours` (float) - MTTR for incidents

#### 10. **Activity Metrics**
- `commits_last_30_days` (integer) - Recent commit count
- `contributors_active` (integer) - Active contributors (last 90 days)
- `pull_requests_open` (integer) - Open PRs
- `pull_requests_merged_last_30_days` (integer) - Recently merged PRs

---

## 🗂️ Tab Structure (Multi-Tab Dashboard)

### Tab 1: Overview
**Purpose:** At-a-glance health status

**Displays:**
- Overall health score (large, color-coded)
- Health trend indicator (↑ improving, → stable, ↓ degrading)
- Key metrics cards (LOC, files, test coverage, issues)
- Last scan timestamp
- Quick action buttons (Refresh, Export, Share)

### Tab 2: Metrics
**Purpose:** Detailed code and activity metrics

**Displays:**
- Code metrics (LOC breakdown by language, file counts)
- Activity metrics (commits, contributors, PR velocity)
- Performance metrics (build time, test time, deployment frequency)
- Charts: Language breakdown (pie chart), Commit activity (line chart)

### Tab 3: Code Quality
**Purpose:** Quality and technical debt analysis

**Displays:**
- Complexity metrics (cyclomatic, cognitive)
- Maintainability index
- Code duplication percentage
- Test coverage percentage with trend
- Technical debt estimation (days)
- Code smells list (top 10 with severity)

### Tab 4: Dependencies
**Purpose:** Dependency health and security

**Displays:**
- Dependency counts (total, direct, transitive)
- Outdated dependencies list
- Vulnerable dependencies with CVE details
- Dependency health score
- Update recommendations
- License compliance (if available)

### Tab 5: Security (Optional, High-Value Apps)
**Purpose:** Security posture and vulnerabilities

**Displays:**
- Security score
- Vulnerability breakdown by severity
- Exposed secrets count (with redacted examples)
- Security scan history
- Remediation recommendations

---

## 📐 Universal Schema JSON Structure

```json
{
  "$schema": "https://cortex.ai/schemas/health-data-v1.json",
  "version": "1.0.0",
  "metadata": {
    "repo_name": "string",
    "repo_url": "string (optional)",
    "branch": "string",
    "commit_hash": "string",
    "commit_date": "ISO8601",
    "last_scan": "ISO8601",
    "scan_duration_seconds": "float (optional)",
    "scanner_version": "string (optional)"
  },
  "health": {
    "overall_score": "integer (0-100)",
    "trend": "enum (improving|stable|degrading)",
    "status": "enum (healthy|warning|critical)"
  },
  "code_metrics": {
    "lines_of_code": "integer",
    "file_count": "integer",
    "directory_count": "integer",
    "language_breakdown": {
      "LanguageName": "integer (LOC)"
    }
  },
  "code_quality": {
    "complexity_score": "integer (0-100)",
    "maintainability_index": "integer (0-100)",
    "cyclomatic_complexity_avg": "float",
    "cognitive_complexity_avg": "float",
    "code_duplication_pct": "float (0-100)",
    "comment_ratio_pct": "float (0-100)"
  },
  "testing": {
    "coverage_pct": "float (0-100)",
    "unit_test_count": "integer",
    "integration_test_count": "integer",
    "test_pass_rate_pct": "float (0-100)"
  },
  "issues": {
    "total_count": "integer",
    "by_severity": {
      "critical": "integer",
      "high": "integer",
      "medium": "integer",
      "low": "integer"
    },
    "technical_debt_days": "float",
    "code_smells_count": "integer"
  },
  "dependencies": {
    "total": "integer",
    "direct": "integer",
    "transitive": "integer",
    "outdated": "integer",
    "vulnerable": "integer",
    "health_score": "integer (0-100)"
  },
  "security": {
    "score": "integer (0-100)",
    "vulnerabilities": {
      "critical": "integer",
      "high": "integer",
      "medium": "integer",
      "low": "integer"
    },
    "secrets_exposed": "integer",
    "last_scan": "ISO8601"
  },
  "performance": {
    "build_time_seconds": "float",
    "test_execution_time_seconds": "float",
    "deployment_frequency": "string",
    "mean_time_to_recovery_hours": "float"
  },
  "activity": {
    "commits_last_30_days": "integer",
    "contributors_active": "integer",
    "pull_requests_open": "integer",
    "pull_requests_merged_last_30_days": "integer"
  }
}
```

---

## 🔧 Schema Extensibility

### Application-Specific Metrics (Optional Fields)

Applications can extend the schema with custom metrics:

```json
{
  "custom_metrics": {
    "app_specific_field_1": "value",
    "app_specific_field_2": "value"
  }
}
```

**Examples:**
- **CORTEX:** brain_tier_sizes, conversation_count, orchestrator_executions
- **NOOR CANVAS:** canvas_templates, user_sessions, feature_usage
- **ALIST:** list_operations, api_response_time, cache_hit_rate
- **KSESSIONS:** session_count, session_duration_avg, knowledge_entries

---

## ✅ Schema Design Principles

1. **Universal Core:** All apps must provide core metrics (health, code, quality, dependencies)
2. **Optional Enhancements:** Security, performance, custom metrics are optional
3. **Type Safety:** Each field has explicit type (integer, float, string, enum)
4. **Validation-Ready:** Schema can be used with JSON Schema validation
5. **Versioned:** Schema version field allows evolution without breaking changes
6. **ISO Standards:** Timestamps use ISO 8601 format
7. **Percentage Fields:** All percentages are 0-100 floats (not 0.0-1.0)
8. **Score Normalization:** All scores are 0-100 integers for consistency

---

## 📊 CORTEX Baseline Reference

**Using CORTEX as reference for realistic metric ranges:**

Based on CORTEX repository analysis:
- LOC: ~15,000-20,000 (medium-sized project)
- Files: 200-300
- Test coverage: 60-70% (good coverage)
- Complexity: Medium (cyclomatic ~5-8 avg)
- Dependencies: 25-30 direct, 80-100 total
- Issues: 10-20 open (mostly enhancements)
- Security: High score (no known vulnerabilities)

**These ranges inform mock data generation for realistic scenarios.**

---

## 🎯 Next Steps

1. ✅ Universal schema designed (core + optional fields)
2. ✅ Tab structure defined (5 tabs: Overview, Metrics, Quality, Dependencies, Security)
3. ⏭️ Create JSON Schema file for validation
4. ⏭️ Document schema with examples
5. ⏭️ Generate mock data files (Phase 2)

---

**Report Status:** 🔄 IN PROGRESS  
**Schema Design:** ✅ COMPLETE  
**Tab Structure:** ✅ COMPLETE  
**Validation Schema:** ⏭️ NEXT  
**Last Updated:** December 4, 2025
