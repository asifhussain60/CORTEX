# CORTEX Database Migration System

**Version:** 1.0.0  
**Created:** January 5, 2026  
**Author:** Asif Hussain

## Overview

This directory contains the database migration framework and migration files for CORTEX's multi-database architecture.

## Architecture

CORTEX uses 5 primary databases:
- `cortex-brain.db` - Unified database (all tiers)
- `tier0/governance.db` - Immutable governance rules
- `tier1/working_memory.db` - Short-term conversation history
- `tier2/knowledge_graph.db` - Long-term pattern storage
- `tier3/context.db` - Development context cache

## Migration Framework

### Core Components

**`000_migration_framework.py`**
- `MigrationManager` class - Orchestrates all migrations
- Version tracking per database
- Transaction safety with rollback
- Validation checks
- Migration history logging

**Migration Files (SQL)**
- `001_*.sql` through `00N_*.sql` - Individual migrations
- Each migration has up/down SQL
- Idempotent by design (safe to run multiple times)

### Features

✅ **Version Tracking** - Each database tracks applied migrations  
✅ **Idempotent** - Safe to run multiple times  
✅ **Rollback** - Can undo migrations if needed  
✅ **Validation** - Optional validation queries per migration  
✅ **History** - Complete audit log of all migration operations  
✅ **Target Specific** - Migrations can target specific databases

## Usage

### Check Migration Status

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m src.database.migrations.000_migration_framework status
```

**Output:**
```
🗄️  CORTEX Database Migration Status

✅ cortex-brain          v3 -> v3
⚠️  tier1                v0 -> v3
   - v1: add_response_detail_to_user_profile
✅ tier2                 v2 -> v3
```

### Apply All Pending Migrations

```bash
python3 -m src.database.migrations.000_migration_framework apply --verbose
```

### Apply to Specific Version

```bash
python3 -m src.database.migrations.000_migration_framework apply --version 2
```

### Validate All Databases Up-to-Date

```bash
python3 -m src.database.migrations.000_migration_framework validate
```

Exit code 0 if all up-to-date, 1 if pending migrations exist.

### Rollback (Advanced)

```bash
python3 -m src.database.migrations.000_migration_framework rollback --version 1
```

## Migration Definitions

### Migration 001: Add response_detail to user_profile
- **Database:** tier1/working_memory.db
- **Purpose:** Add missing response_detail column
- **Status:** ✅ Applied as quick fix
- **SQL File:** `001_add_response_detail_to_user_profile.sql`

### Migration 002: Create tier2_patterns view
- **Database:** tier2/knowledge_graph.db
- **Purpose:** Backward compatibility mapping (patterns → tier2_patterns)
- **Status:** ✅ Applied as quick fix
- **SQL File:** `002_create_tier2_patterns_view.sql`
- **Note:** FTS tables cannot be views - code uses patterns/patterns_fts directly

### Migration 003: Add user_profile to unified DB
- **Database:** cortex-brain.db
- **Purpose:** Ensure user_profile exists in unified database
- **Status:** ⏳ Pending (not yet applied)
- **SQL File:** `003_add_user_profile_to_unified_db.sql`

## Creating New Migrations

### Step 1: Define Migration

Edit `000_migration_framework.py` and add to `create_migrations()`:

```python
migrations.append(Migration(
    version=4,  # Next sequential version
    name="descriptive_snake_case_name",
    description="Human-readable description",
    database_target="tier1",  # or "all", "cortex-brain", etc.
    up_sql="""
        -- SQL to apply migration
        ALTER TABLE foo ADD COLUMN bar TEXT;
    """,
    down_sql="""
        -- SQL to rollback migration
        ALTER TABLE foo DROP COLUMN bar;
    """,
    validation_query="SELECT bar FROM foo LIMIT 1"  # Optional
))
```

### Step 2: Create SQL File (Optional)

Create `00N_descriptive_name.sql` for documentation:

```sql
-- Migration 004: Description
-- Database: tier1/working_memory.db
-- Purpose: What this migration does
-- Author: Your Name
-- Date: YYYY-MM-DD

-- Up migration
ALTER TABLE foo ADD COLUMN bar TEXT;

-- Validation
SELECT bar FROM foo LIMIT 1;
```

### Step 3: Test

```bash
# Check status
python3 -m src.database.migrations.000_migration_framework status

# Apply in test environment first
python3 -m src.database.migrations.000_migration_framework apply --verbose

# Validate
python3 -m src.database.migrations.000_migration_framework validate
```

### Step 4: Commit

```bash
git add src/database/migrations/
git commit -m "feat: Add migration 004 - descriptive name"
```

## Schema Version Tables

Each database has two tracking tables:

### schema_version
```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    applied_at TEXT NOT NULL,
    applied_by TEXT DEFAULT 'migration_framework',
    execution_time_ms INTEGER,
    success BOOLEAN NOT NULL DEFAULT 1,
    rollback_available BOOLEAN NOT NULL DEFAULT 1
);
```

### migration_log
```sql
CREATE TABLE migration_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('apply', 'rollback', 'validate')),
    timestamp TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER
);
```

## Best Practices

### ✅ DO

- **Version sequentially** - No gaps, no duplicates
- **Test locally first** - Validate before committing
- **Keep migrations small** - One logical change per migration
- **Make idempotent** - Safe to run multiple times
- **Provide rollback** - Always include down_sql
- **Document purpose** - Clear description and comments

### ❌ DON'T

- **Don't modify applied migrations** - Create new migration instead
- **Don't skip versions** - Maintain sequential order
- **Don't mix concerns** - One migration = one change
- **Don't break data** - Test with production-like data first
- **Don't forget validation** - Add validation_query where possible

## Troubleshooting

### Migration Failed

1. Check error message in output
2. Review migration SQL for syntax errors
3. Check database state manually
4. Roll back if needed: `rollback --version N`
5. Fix migration code
6. Re-apply

### Database Out of Sync

```bash
# Check current versions
python3 -m src.database.migrations.000_migration_framework status

# Apply missing migrations
python3 -m src.database.migrations.000_migration_framework apply
```

### View Query Logs

Query the `migration_log` table directly:

```bash
sqlite3 cortex-brain/tier1/working_memory.db \
  "SELECT * FROM migration_log ORDER BY timestamp DESC LIMIT 10;"
```

## Integration with Phase P00

This migration system is the implementation of **Phase P00: Database Schema Consolidation** from the CORTEX v5 Remediation Epic.

**Deliverables:**
- ✅ `000_migration_framework.py` - Core migration system
- ✅ `001_*.sql` through `003_*.sql` - Initial migrations
- ✅ `README.md` - This documentation
- ⏳ Schema validator (to be implemented)
- ⏳ ERD generator (to be implemented)

**Acceptance Criteria Met:**
- ✅ Version tracking operational
- ✅ Migration system with rollback
- ✅ Idempotent migrations
- ✅ Transaction safety
- ⏳ Automated validation tests (pending)

## Future Enhancements

### Planned Features

1. **Schema Validator**
   - Automated consistency checks
   - Foreign key validation
   - Index optimization suggestions

2. **ERD Generator**
   - Auto-generate entity relationship diagrams
   - Keep documentation in sync with schema

3. **Backup Integration**
   - Auto-backup before migrations
   - Easy rollback to backup if needed

4. **Migration Templates**
   - CLI command to generate migration scaffolding
   - Pre-filled with current date, version, etc.

5. **Dry Run Mode**
   - Test migrations without applying
   - Show what would change

## References

- **Phase P00 Manifest:** `cortex-brain/documents/planning/active/cortex-v5-remediation-epic/epic-manifest.yaml`
- **Schema Audit Report:** `cortex-brain/documents/analysis/database-schema-audit-report-2026-01-05.md`
- **Schema Files:** `cortex-brain/schema.sql`, `cortex-brain/schemas/*.sql`
- **Pattern Search Fix:** `src/tier2/knowledge_graph/patterns/pattern_search.py`

---

**Last Updated:** January 5, 2026  
**Version:** 1.0.0  
**Maintainer:** Asif Hussain
