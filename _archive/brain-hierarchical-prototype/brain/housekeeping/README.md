# Tier 5: Housekeeping

**Purpose:** Automatic background maintenance and optimization.

## 📂 Services

- \cleanup-service.ps1\ - Remove unused patterns
- \organizer-service.ps1\ - Consolidate patterns
- \optimizer-service.ps1\ - Performance tuning
- \indexer-service.ps1\ - Rebuild indices
- \alidator-service.ps1\ - Integrity checks
- \rchiver-service.ps1\ - Archive old data

## 📅 Schedules

- **Daily (2am):** cleanup, validator
- **Weekly (Sunday):** organizer
- **Monthly (1st):** optimizer, archiver

## 🎯 Orchestration

\orchestrator.ps1\ manages all services and schedules.

## 📖 See Also

- KDS-V6-HOLISTIC-PLAN.md - Housekeeping design
