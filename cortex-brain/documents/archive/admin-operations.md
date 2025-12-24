# 🔧 Admin Operations (CORTEX Repo Only)

**Context Detection:** Admin operations only available in CORTEX development repository (detects `cortex-brain/admin/`)

## System Validation

- `align` - Full system alignment with intelligent maintenance (v2.0)
- `align validate-registrations` - Check for unregistered features
- `align discover-features` - Scan and display unregistered features
- `align register-features` - Interactive registration workflow
- `align register-features --auto` - Auto-register all discovered features
- `align detect-obsolete` - Scan for obsolete code
- `align cleanup --dry-run` - Preview cleanup plan
- `align cleanup --execute` - Execute cleanup with safety checks
- `align migrate-tests --dry-run` - Preview test migrations
- `align migrate-tests --execute` - Execute test migrations with backup
- `align full-maintenance` - Run all checks + auto-fix
- `align full-maintenance --dry-run` - Preview all changes
- `align report` - Detailed report with auto-remediation templates
- **Guide:** #file:system-alignment-guide.md

## Architecture Health

- `review architecture` - Strategic health analysis with trend tracking and debt forecasting
- **Guide:** #file:architecture-intelligence-guide.md

## Repository Maintenance

- `cleanup` - Holistic cleanup (50-200 MB savings typical)
- `cleanup with tests` - Surgical cleanup with zero-break guarantee (test harness)
- `consolidate markdown` - Intelligent consolidation of 600+ markdown files (64% reduction)
- `design sync` - Synchronize design docs with implementation

## Deployment

- `deploy cortex` - Build production package
- `generate docs` - Build MkDocs documentation

## Setup & Configuration

- `setup copilot instructions` - Generate entry point module for user repositories
- **Guide:** #file:setup-epm-guide.md

## Planning

- `plan ado` - Create ADO work items (stories, features, bugs, tasks, epics)

**All admin commands accessible via:** `admin help`
