# Plan Management Guide

**CORTEX 3.6.0** - Comprehensive plan registry, tracking, and organization system

---

## 🎯 Overview

CORTEX Plan Management System provides SQLite-backed plan tracking, automatic status organization, full-text search, and auto-generated INDEX.md for all feature plans.

**Benefits:**
- 📊 **SQLite registry** with 100ms query performance
- 🔍 **Full-text search** (FTS5) across all plan documents
- 📁 **Auto-organization** by status (proposed, approved, in-progress, completed)
- 📝 **Auto-indexing** with generated INDEX.md
- 🔗 **Dependency tracking** for complex feature workflows

---

## 📋 Plan Structure

### Plan Metadata (YAML Frontmatter)

All plans require YAML frontmatter with required fields:

```markdown
---
plan_id: CORTEX-AUTH-001
title: User Authentication System
status: proposed
priority: high
created_date: 2025-01-29
estimated_hours: 40
assigned_to: Backend Team
tags:
  - authentication
  - security
  - backend
dependencies:
  - CORTEX-DB-001
---

# User Authentication System

## Description

Implement JWT-based authentication with OAuth2 support...

## Requirements

1. JWT token generation
2. OAuth2 providers (Google, GitHub)
3. Session management
4. Role-based access control (RBAC)

## Implementation Plan

### Phase 1: JWT Infrastructure
- Token generation
- Token validation
- Refresh token flow

### Phase 2: OAuth2 Integration
- Provider configuration
- Callback handlers
- User linking

## Testing Strategy

- Unit tests: 50+ tests
- Integration tests: 20+ scenarios
- Load testing: 1000 req/s

## Success Criteria

- [ ] All tests passing
- [ ] Security audit complete
- [ ] Documentation updated
- [ ] Performance targets met
```

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `plan_id` | string | Unique identifier | CORTEX-AUTH-001 |
| `title` | string | Human-readable title | User Authentication System |
| `status` | enum | Plan status | proposed, approved, in-progress, completed, cancelled |
| `priority` | enum | Priority level | low, medium, high, critical |
| `created_date` | date | Creation date | 2025-01-29 |
| `estimated_hours` | int | Time estimate | 40 |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `updated_date` | date | Last modification |
| `actual_hours` | int | Actual time spent |
| `completion_percentage` | int | Progress (0-100) |
| `assigned_to` | string | Person/team |
| `tags` | list | Categorization tags |
| `dependencies` | list | Required plan IDs |
| `blocked_by` | list | Blocking plan IDs |
| `related_plans` | list | Related plan IDs |

---

## 🗂️ Directory Structure

### Status-Based Organization

```
cortex-brain/documents/planning/
├── INDEX.md                    # Auto-generated index
├── planning-registry.db        # SQLite database
├── proposed/                   # Awaiting approval
│   ├── CORTEX-AUTH-001-user-auth.md
│   └── CORTEX-CACHE-002-redis-cache.md
├── approved/                   # Ready for implementation
│   ├── CORTEX-API-001-rest-api.md
│   └── CORTEX-DB-001-database-schema.md
├── in-progress/                # Currently being worked on
│   ├── CORTEX-UI-001-dashboard.md
│   └── CORTEX-TEST-001-test-framework.md
├── completed/                  # Finished plans
│   ├── CORTEX-SETUP-001-setup-wizard.md
│   └── CORTEX-PLAN-001-plan-registry.md
└── cancelled/                  # Cancelled plans
    └── CORTEX-OLD-001-deprecated-feature.md
```

### Automatic File Movement

When status changes, files automatically move:

```bash
# Change status
cortex plan status CORTEX-AUTH-001 approved

# File moves:
# FROM: planning/proposed/CORTEX-AUTH-001-user-auth.md
# TO:   planning/approved/CORTEX-AUTH-001-user-auth.md

# Registry updates automatically
# INDEX.md regenerates
```

---

## 🚀 Creating Plans

### Interactive CLI

```bash
# Create new plan (interactive)
cortex plan create

# Prompts:
# 1. Plan ID? → CORTEX-AUTH-001
# 2. Title? → User Authentication System
# 3. Priority? (low/medium/high/critical) → high
# 4. Estimated hours? → 40
# 5. Description? → [Opens editor]

# Creates: planning/proposed/CORTEX-AUTH-001-user-auth.md
# Registers: In planning-registry.db
# Updates: INDEX.md
```

### Template-Based Creation

```bash
# Create from template
cortex plan create --template feature

# Available templates:
# - feature: Standard feature plan
# - bugfix: Bug fix investigation
# - refactor: Code refactoring plan
# - spike: Technical research spike
```

### Programmatic Creation

```python
from src.workflows.plan_registry import PlanRegistry
from pathlib import Path

# Create plan file
plan_content = """---
plan_id: CORTEX-AUTH-001
title: User Authentication
status: proposed
priority: high
created_date: 2025-01-29
estimated_hours: 40
---

# User Authentication

## Description
JWT-based authentication system...
"""

# Write file
plan_file = Path("cortex-brain/documents/planning/proposed/CORTEX-AUTH-001-user-auth.md")
plan_file.write_text(plan_content)

# Register in database
registry = PlanRegistry(Path("cortex-brain"))
registry.scan_and_index()

# Verify registered
plan = registry.get_plan("CORTEX-AUTH-001")
print(f"Registered: {plan['title']}")
```

---

## 🔍 Plan Lookup & Search

### Get Plan by ID

```bash
# CLI lookup
cortex plan get CORTEX-AUTH-001

# Output:
# 📋 Plan: CORTEX-AUTH-001
# Title: User Authentication System
# Status: approved
# Priority: high
# Created: 2025-01-29
# Estimated: 40h
# Progress: 0%
#
# File: planning/approved/CORTEX-AUTH-001-user-auth.md
```

### List Plans by Status

```bash
# List all in-progress plans
cortex plan list --status in-progress

# Output:
# 🚧 In-Progress Plans (3)
# 1. CORTEX-UI-001: Dashboard UI (30% complete)
# 2. CORTEX-TEST-001: Test Framework (60% complete)
# 3. CORTEX-DOC-001: Documentation (15% complete)
```

### Full-Text Search

```bash
# Search across all plans
cortex plan search "authentication OAuth2"

# Output:
# 🔍 Search Results (2 matches)
#
# 1. CORTEX-AUTH-001: User Authentication System
#    Status: approved | Priority: high
#    Match: "Implement JWT-based authentication with OAuth2 support"
#
# 2. CORTEX-API-003: API Gateway
#    Status: proposed | Priority: medium
#    Match: "Support OAuth2 token validation for API requests"
```

### Programmatic Query

```python
from src.workflows.plan_registry import PlanRegistry
from pathlib import Path

registry = PlanRegistry(Path("cortex-brain"))

# Get single plan
plan = registry.get_plan("CORTEX-AUTH-001")

# List by status
approved_plans = registry.list_plans(status="approved")

# Full-text search
results = registry.search_plans("authentication OAuth2")

for plan in results:
    print(f"{plan['plan_id']}: {plan['title']}")
```

---

## 🔄 Status Workflow

### Status Lifecycle

```
proposed → approved → in-progress → completed
     ↓         ↓            ↓
  cancelled  cancelled  cancelled
```

### Status Transitions

```bash
# Propose new plan
cortex plan create  # Creates in 'proposed' status

# Approve for implementation
cortex plan status CORTEX-AUTH-001 approved

# Start work
cortex plan status CORTEX-AUTH-001 in-progress

# Complete
cortex plan status CORTEX-AUTH-001 completed

# Cancel (from any status)
cortex plan status CORTEX-AUTH-001 cancelled --reason "Requirements changed"
```

### Validation Rules

- **proposed → approved:** Requires DoR (Definition of Ready) checklist
- **approved → in-progress:** Must have assigned_to field
- **in-progress → completed:** Requires DoD (Definition of Done) checklist
- **Any → cancelled:** Requires cancellation reason

### Programmatic Status Change

```python
from src.workflows.plan_organizer import PlanOrganizer
from src.workflows.plan_registry import PlanRegistry
from pathlib import Path

organizer = PlanOrganizer(Path("cortex-brain"))
registry = PlanRegistry(Path("cortex-brain"))

# Get current plan file
plan = registry.get_plan("CORTEX-AUTH-001")
current_file = Path(plan["file_path"])

# Move to new status
new_path = organizer.move_to_status_dir(current_file, "in-progress")

# Re-index registry
registry.scan_and_index()

print(f"Moved to: {new_path}")
```

---

## 📊 Plan Analytics

### Progress Tracking

```bash
# View plan progress
cortex plan progress CORTEX-AUTH-001

# Output:
# 📊 Plan Progress: CORTEX-AUTH-001
#
# Title: User Authentication System
# Status: in-progress
# Progress: 45% complete
#
# Time Tracking:
# - Estimated: 40h
# - Actual: 18h
# - Remaining: 22h (est.)
#
# Completion:
# ✅ Phase 1: JWT Infrastructure (100%)
# 🚧 Phase 2: OAuth2 Integration (70%)
# ☐ Phase 3: RBAC Implementation (0%)
```

### Dependency Graph

```bash
# View plan dependencies
cortex plan deps CORTEX-AUTH-001

# Output:
# 🔗 Dependencies: CORTEX-AUTH-001
#
# Depends on:
# - CORTEX-DB-001: Database Schema (✅ completed)
# - CORTEX-CONFIG-001: Config System (🚧 in-progress)
#
# Blocks:
# - CORTEX-API-003: API Gateway (⏸ waiting)
# - CORTEX-ADMIN-001: Admin Panel (⏸ waiting)
```

### Velocity Metrics

```bash
# Team velocity
cortex plan velocity

# Output:
# ⚡ Team Velocity (Last 30 days)
#
# Plans Completed: 8
# Average Time: 32h per plan
# Estimation Accuracy: 87%
#
# By Priority:
# - Critical: 2 plans (avg 48h)
# - High: 3 plans (avg 35h)
# - Medium: 2 plans (avg 24h)
# - Low: 1 plan (avg 16h)
```

---

## 📝 INDEX.md Auto-Generation

### Generated Index Structure

INDEX.md is automatically generated and updated:

```markdown
# Planning Index

**Auto-generated:** 2025-01-29 14:32:15  
**Total Plans:** 18  
**Last Updated:** CORTEX-AUTH-001

---

## 🚧 In-Progress (3)

| Plan ID | Title | Priority | Progress | Assigned |
|---------|-------|----------|----------|----------|
| CORTEX-UI-001 | Dashboard UI | high | 30% | Frontend Team |
| CORTEX-TEST-001 | Test Framework | medium | 60% | QA Team |
| CORTEX-DOC-001 | Documentation | low | 15% | Tech Writer |

## ✅ Approved (4)

| Plan ID | Title | Priority | Est. Hours | Dependencies |
|---------|-------|----------|------------|--------------|
| CORTEX-AUTH-001 | User Authentication | high | 40h | CORTEX-DB-001 |
| CORTEX-API-003 | API Gateway | high | 32h | CORTEX-AUTH-001 |
| CORTEX-CACHE-002 | Redis Cache | medium | 16h | none |
| CORTEX-LOG-001 | Logging System | low | 12h | none |

## 📋 Proposed (5)

| Plan ID | Title | Priority | Est. Hours |
|---------|-------|----------|------------|
| CORTEX-SEARCH-001 | Full-Text Search | high | 24h |
| CORTEX-NOTIFY-001 | Notifications | medium | 20h |
| CORTEX-REPORT-001 | Reporting Dashboard | medium | 36h |
| CORTEX-BACKUP-001 | Backup System | low | 16h |
| CORTEX-METRICS-001 | Metrics Collection | low | 12h |

## ✅ Completed (6)

| Plan ID | Title | Completed | Actual Hours |
|---------|-------|-----------|--------------|
| CORTEX-SETUP-001 | Setup Wizard | 2025-01-15 | 12h |
| CORTEX-PLAN-001 | Plan Registry | 2025-01-20 | 18h |
| CORTEX-PROFILE-001 | User Profiles | 2025-01-22 | 8h |
| CORTEX-TEMPLATE-001 | Template System | 2025-01-25 | 14h |
| CORTEX-DB-001 | Database Schema | 2025-01-26 | 22h |
| CORTEX-CONFIG-001 | Config System | 2025-01-28 | 10h |
```

### Regeneration Triggers

INDEX.md auto-regenerates when:
- New plan created
- Status changed
- Plan metadata updated
- Manual trigger: `cortex plan index`

---

## 🛠️ Troubleshooting

### Registry Out of Sync

**Problem:** Changes not reflected in queries

**Solution:**
```bash
# Re-scan and rebuild registry
cortex plan rescan

# Or programmatically
registry = PlanRegistry(Path("cortex-brain"))
registry.scan_and_index()
```

### Missing Plans

**Problem:** Plan file exists but not in registry

**Solution:**
```bash
# Verify YAML frontmatter is valid
cortex plan validate CORTEX-AUTH-001

# Re-scan directory
cortex plan rescan
```

### Search Not Finding Plans

**Problem:** Full-text search returns no results

**Solution:**
```bash
# Rebuild FTS5 index
cortex plan reindex

# Verify SQLite FTS5 extension
sqlite3 cortex-brain/documents/planning/planning-registry.db
> PRAGMA compile_options;
> -- Should show ENABLE_FTS5
```

---

## 📚 Related Documentation

- **Shared Environment Setup:** `shared-environment-setup.md`
- **User Profiling Guide:** `user-profiling-guide.md`
- **Planning System:** `.github/prompts/modules/planning-system-guide.md`
- **DoR/DoD Checklists:** `cortex-brain/planning-checklists.yaml`

---

**Version:** 3.6.0  
**Last Updated:** 2025-01-29  
**Author:** Asif Hussain
