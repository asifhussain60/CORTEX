# Repository Onboarding → Dashboard Workflow

**Last Updated:** 2026-02-08 | **Authority:** CORTEX Architect Review | **Status:** Integration Guide

---

## Overview

This guide documents the integrated workflow for onboarding external repositories and automatically generating their dashboards. This workflow combines Phase-28 (Repository Onboarding System) and Phase-53 (Dashboard Orchestrator) into a seamless operation.

---

## Architecture Diagram

```
User Issues Command
        ↓
    /onboard /path/to/repo
        ↓
MCP Gateway (cortex_onboard_repository)
        ↓
RepositoryOnboardingOrchestrator
    ├─ Scans directory structure
    ├─ Detects tech stack
    ├─ Analyzes security baseline
    └─ Generates Profile YAML
        ↓
   Profile Saved
   cortex_brain/onboarded_repos/{repo_name}.yaml
        ↓
[NEW - Phase-28 S5] Dashboard Auto-Generation Hook
        ↓
MCP Compound Tool (cortex_onboard_and_dashboard)
        ↓
DashboardOrchestrator
    ├─ Reads Profile Metadata
    ├─ Generates Dashboard JSON
    └─ Validates Schema Compliance
        ↓
    Dashboard Saved
    company/dashboards/data/{repo_name}.json
        ↓
Registry Updated (index.yaml)
    ├─ dashboard_generated: true
    └─ dashboard: "company/dashboards/data/{repo_name}.json"
        ↓
✅ COMPLETE
- Profile available: cortex_brain/onboarded_repos/
- Dashboard available: company/dashboards/data/
- Both registered in: cortex-registry/_cortex-master/index.yaml
```

---

## Workflow Stages

### Stage 1: Repository Onboarding (Phase-28)

**Trigger:** `/onboard /path/to/repository`

**MCP Tool:** `cortex_onboard_repository`

**Orchestrator:** RepositoryOnboardingOrchestrator

**What Happens:**
1. Validate repository path exists
2. Scan repository structure:
   - File count and organization
   - Programming languages detected
   - Test framework presence
   - Documentation structure
3. Analyze tech stack:
   - Primary language(s)
   - Frameworks and dependencies
   - Build/deployment tools
4. Security baseline assessment:
   - Vulnerability scan
   - Secrets detection
   - OWASP compliance check
5. Generate profile YAML with all metadata

**Output:** `cortex_brain/onboarded_repos/{repo_name}.yaml`

**Example Profile:**
```yaml
repository:
  name: "ksessions"
  path: "/path/to/KSESSIONS"
  onboarded_at: "2026-02-08T10:30:00Z"
  exists: true

tech_stack:
  primary_language: "Python"
  languages: ["Python", "YAML"]
  frameworks: ["FastAPI", "Pydantic"]
  dependencies:
    - "pyyaml>=6.0"
    - "pydantic>=2.0"

structure:
  has_tests: true
  test_framework: "pytest"
  test_coverage: "85%"

standards:
  coding_style: "black + mypy"
  security_baseline: "OWASP compliant"
  test_patterns: "TDD with pytest"

security:
  vulnerabilities_detected: 1
  last_scan: "2026-02-08T10:30:00Z"
```

**Validation:**
- Profile schema valid (Pydantic models)
- All required fields present
- No corruption during serialization

**Audit Trail:**
```
AC_START: AC-PHASE28-001
Repository onboarding initiated for ksessions
Path: /path/to/KSESSIONS
Scanning: 29,993 files
...
AC_COMPLETE: AC-PHASE28-001 ✅
Profile saved: cortex_brain/onboarded_repos/ksessions.yaml
```

---

### Stage 2: Dashboard Auto-Generation Hook (Phase-28 S5) — **NEW**

**Trigger:** Automatic, immediately after profile saved

**How It Works:**
1. Post-profile hook fires in RepositoryOnboardingOrchestrator
2. Hook calls dashboard auto-generation
3. User receives notification: "Dashboard generating..."
4. Process continues without blocking

**Error Handling:**
- If dashboard generation fails: Profile retained, error logged
- User can manually retry via `cortex_generate_dashboard`
- No profile corruption

---

### Stage 3: Dashboard Generation (Phase-53)

**Trigger:** Automatic (via Phase-28 S5 hook) OR manual `cortex_generate_dashboard`

**MCP Tool:** `cortex_generate_dashboard`

**Orchestrator:** DashboardOrchestrator

**What Happens:**
1. Read profile from `cortex_brain/onboarded_repos/{repo_name}.yaml`
2. Extract metadata:
   - Repository name
   - Tech stack info
   - Test coverage
   - Security baseline
   - Standards compliance
3. Generate SPA-compatible JSON:
   - Overview tab (repo summary)
   - Tech Stack tab (languages, frameworks)
   - Structure tab (file organization)
   - Testing tab (coverage, frameworks)
   - Standards tab (code style, patterns)
   - Security tab (vulnerabilities, compliance)
4. Validate JSON against schema
5. Write to disk

**Output:** `company/dashboards/data/{repo_name}.json`

**Example Dashboard JSON (Abbreviated):**
```json
{
  "repo_name": "ksessions",
  "generated_at": "2026-02-08T10:32:00Z",
  "metadata": {
    "file_count": 29993,
    "primary_language": "Python",
    "test_coverage": "85%"
  },
  "tabs": {
    "overview": {
      "repo_name": "KSESSIONS",
      "description": "Enterprise session management",
      "file_count": 29993
    },
    "tech_stack": {
      "languages": ["Python", "YAML"],
      "frameworks": ["FastAPI", "Pydantic"],
      "dependencies_count": 12
    },
    "testing": {
      "framework": "pytest",
      "coverage": "85%",
      "test_count": 1240
    },
    "security": {
      "vulnerabilities": 1,
      "severity": "P1",
      "owasp_compliant": true
    }
  }
}
```

**Validation:**
- JSON Schema Draft 7 compliance
- All required tabs present
- No null/undefined values
- File size reasonable (<5MB)

**Audit Trail:**
```
AC_START: AC-PHASE53-G001
Dashboard generation for ksessions
Reading profile: cortex_brain/onboarded_repos/ksessions.yaml
Generating tabs: overview, tech_stack, structure, testing, standards, security
...
AC_COMPLETE: AC-PHASE53-G001 ✅
Dashboard saved: company/dashboards/data/ksessions.json (152KB)
```

---

### Stage 4: Registry Synchronization

**Trigger:** Automatic, after successful dashboard save

**What Happens:**
1. Update `cortex-registry/_cortex-master/index.yaml`
2. Set `dashboard_generated: true` for repo
3. Set `dashboard: "company/dashboards/data/{repo_name}.json"`
4. Set `spa_ready: true`

**Before:**
```yaml
- id: "ksessions"
  name: "KSESSIONS"
  status: "active"
  onboarded_date: "2026-02-08"
  file_count: 29993
  # dashboard fields missing
```

**After:**
```yaml
- id: "ksessions"
  name: "KSESSIONS"
  status: "active"
  onboarded_date: "2026-02-08"
  file_count: 29993
  dashboard: "company/dashboards/data/ksessions.json"
  dashboard_generated: true
  spa_ready: true
```

---

## Single Operation: Compound MCP Tool

**Phase-28 S5** introduces `cortex_onboard_and_dashboard` — a compound MCP tool combining both operations.

### Usage

**Via MCP Tool (Recommended):**
```python
result = cortex_onboard_and_dashboard(
    repo_path="/path/to/repository",
    auto_dashboard=True  # default: true
)

# Returns:
# {
#   "profile": {path_to_profile_yaml},
#   "dashboard": {path_to_dashboard_json},
#   "registry_updated": true,
#   "status": "success",
#   "audit_trail": [AC markers]
# }
```

**Via Command Line:**
```bash
# Single operation
/onboard /path/to/repository

# Behind the scenes:
# 1. cortex_onboard_repository invoked
# 2. Profile saved
# 3. Auto-generation hook fires
# 4. cortex_generate_dashboard invoked
# 5. Dashboard saved
# 6. Registry updated
# 7. Complete!
```

### Benefits

| Aspect | Before (Manual) | After (Compound Tool) |
|--------|-----------------|----------------------|
| **Steps** | 2 separate operations | 1 command |
| **Time** | 2-3 minutes | 1-2 minutes |
| **Error Handling** | Manual retry | Atomic transaction |
| **Audit Trail** | Separate logs | Unified audit trail |
| **Consistency** | Manual verification | Automatic validation |

---

## Initial Dashboard Seeding (Phase-54)

**After** Phase-28 S5 is operational, Phase-54 seeds dashboards for all existing onboarded repos.

### One-Time Operation

```bash
# Discover all profiles in cortex_brain/onboarded_repos/
# Generate dashboard for each
# Validate and store
# Update registry
# Generate report
```

**Expected Output:**
```
Seeding Dashboard for All Onboarded Repositories
═══════════════════════════════════════════════════

Discovered Profiles: 5
  1. alist (540 files)
  2. cortex (12,500 files)
  3. kashkole (890 files)
  4. ksessions (29,993 files)
  5. noor-canvas (1,200 files)

Generating Dashboards...
  [████████░░] 80% Processing kashkole...
  ✅ alist (2.1s)
  ✅ cortex (3.5s)
  ✅ kashkole (1.8s)
  🔵 ksessions (generating...)

Validation:
  ✅ All 5 JSON files schema-compliant
  ✅ File sizes reasonable (100-200KB each)

Registry Synchronized:
  ✅ index.yaml updated
  ✅ All repos marked dashboard_generated: true

Total Time: 3m 24s
Report: cortex-registry/_cortex-master/reports/seeding-2026-02-08.json

Audit Trail: 10 AC markers logged ✅
```

**Result:**
- All 5 repos have dashboards
- All dashboards visible in SPA plan viewer
- Foundation set for Phase-55+ enhancements

---

## Error Handling

### Scenario 1: Profile Generation Fails
```
/onboard /invalid/path
  → Error: Path does not exist
  → Action: Graceful failure, no partial state
```

### Scenario 2: Dashboard Generation Fails (After Profile Saved)
```
Profile saved ✅
→ Dashboard generation attempted
  → Error: Tech stack detection failed (rare)
  → Action: Profile retained, error logged
  → User can retry: cortex_generate_dashboard
```

### Scenario 3: Schema Validation Fails
```
Dashboard JSON generated
→ Schema validation attempted
  → Error: Missing required field 'tech_stack'
  → Action: Rollback (no file write), error logged
  → User notified: Dashboard generation incomplete
```

---

## Data Consistency

### Single Source of Truth

```
cortex_brain/onboarded_repos/ ← Profile SSOT
        ↓ (read-only)
Dashboard Generation
        ↓
company/dashboards/data/ ← Dashboard (derived)
        ↓ (registration only)
cortex-registry/_cortex-master/index.yaml ← Registry (metadata)
```

### Idempotency

Re-running any operation:
- **Profile onboarding:** Skipped if exists and unchanged
- **Dashboard generation:** Skipped if exists and unchanged (checksum comparison)
- **Registry update:** Overwrites with same values (idempotent)

---

## Integration Points

### With Plan Viewer (Phase-45)

Dashboard JSON immediately available in SPA:
```html
<!-- company/dashboards/spa/index.html -->
<script>
  // Load dashboard data
  const dashboard = await fetch('/data/ksessions.json')
  // Render in SPA
  renderDashboard(dashboard)
</script>
```

### With Company Domains (Phase-27)

Dashboard includes standards from repo's company/domains/ (if present):
```json
{
  "standards": {
    "coding_style": "black + mypy + pylint",  // from company/domains/
    "test_patterns": "TDD with pytest",        // from company/domains/
    "api_patterns": "RESTful + OpenAPI 3.0"    // from company/domains/
  }
}
```

### With Security Checkpoint (Phase-28)

Security baseline in dashboard:
```json
{
  "security": {
    "vulnerabilities_detected": 1,
    "security_issues_severity": "P1",
    "owasp_compliant": true,
    "last_scan": "2026-02-08T10:30:00Z"
  }
}
```

---

## Troubleshooting

### Dashboard Not Generated After Onboarding

**Symptom:** Profile exists but no dashboard JSON

**Diagnosis:**
1. Check if Phase-28 S5 auto-generation hook is enabled
2. Check logs for dashboard generation errors
3. Verify DashboardOrchestrator is accessible

**Resolution:**
```bash
# Manual retry
cortex_generate_dashboard --repo-name ksessions

# Or via compound tool
cortex_onboard_and_dashboard --repo-path /path/to/ksessions
```

### Dashboard JSON Invalid After Generation

**Symptom:** Schema validation fails

**Diagnosis:**
1. Check if all required fields present in profile
2. Verify JSON schema version matches
3. Check for null/undefined values

**Resolution:**
```bash
# Regenerate with verbose logging
cortex_generate_dashboard --repo-name ksessions --verbose

# Check schema compliance
cortex_validate_dashboard_json --file company/dashboards/data/ksessions.json
```

### Registry Out of Sync

**Symptom:** index.yaml doesn't reflect dashboard existence

**Diagnosis:**
1. Check if registry update completed
2. Verify file permissions on index.yaml
3. Check git status (uncommitted changes?)

**Resolution:**
```bash
# Re-sync registry
cortex_sync_dashboard_registry

# Or re-run full seeding (idempotent)
cortex_seed_all_dashboards
```

---

## Performance Characteristics

| Operation | Typical Time | P95 Time | Notes |
|-----------|-------------|----------|-------|
| Profile generation | 2-5 seconds | 10s | Depends on repo size |
| Dashboard generation | 1-3 seconds | 5s | JSON creation + validation |
| Registry update | <500ms | 1s | YAML file update |
| **Total (onboard + dashboard)** | **3-8 seconds** | **15s** | Typical end-to-end |
| Batch seeding (5 repos) | 15-40 seconds | 60s | Sequential processing |

---

## Future Enhancements (Phase-55+)

### Phase-55: Dashboard Customization
- User-defined dashboard tabs
- Custom metrics per tab
- Theme selection (glassmorphism variants)

### Phase-56: Cross-Repo Metrics
- Aggregate metrics across all repos
- Comparative analysis
- Trend tracking

### Phase-57: Real-Time Dashboard Updates
- Auto-refresh on code changes
- Webhook integration
- Live metrics streaming

---

## References

- **Phase-28:** [Repository Onboarding System](../phases/completed/2026/phase-28-repository-onboarding-system.yaml)
- **Phase-28 S5:** [Dashboard Auto-Generation Hook](../phases/completed/2026/phase-28-repository-onboarding-system.yaml#enhancement_s5_dashboard_integration)
- **Phase-53:** [Dashboard Orchestrator](../phases/completed/2026/phase-53-dashboard-orchestrator.yaml)
- **Phase-54:** [Initial Dashboard Seeding](../phases/active/phase-54-initial-dashboard-seeding.yaml)
- **JSON Schema:** [Repository Dashboard Schema](../dashboard/schema/repo-dashboard-schema.json)
- **SPA:** [Dashboard SPA](../../company/dashboards/spa/index.html)

---

**Last Updated:** 2026-02-08  
**Next Review:** 2026-02-09 (after Phase-28 S5 implementation)
