# CORTEX Migration Tools

## Overview

This directory contains migration scripts for converting CORTEX brain data from legacy formats (YAML/JSONL) to the new V3 architecture (SQLite with FTS5 + JSON).

**Sub-Group 3A: Phase 0.5 - Migration Tools (Test Early)**

## Migration Scripts

### 1. Tier 1 Migration (`tier1/migrate_tier1.py`)
- **Source:** `cortex-brain/conversation-history.jsonl`
- **Target:** `cortex-brain/left-hemisphere/tier1/conversations.db` (SQLite)
- **Duration:** 1-1.5 hours
- **What it migrates:**
  - Conversations with metadata
  - Messages with timestamps and intent
  - Entities discussed
  - Files modified
- **Features:**
  - Full schema creation with indexes
  - CRUD operation support
  - Foreign key constraints
  - Automatic timestamps

### 2. Tier 2 Migration (`tier2/migrate_tier2.py`)
- **Source:** `cortex-brain/knowledge-graph.yaml`
- **Target:** `cortex-brain/right-hemisphere/tier2/patterns.db` (SQLite + FTS5)
- **Duration:** 1-1.5 hours
- **What it migrates:**
  - Validation insights
  - Workflow patterns
  - Intent patterns
  - File relationships
- **Features:**
  - FTS5 full-text search integration
  - Confidence scoring
  - Pattern details in JSON format
  - Automatic FTS5 sync triggers

### 3. Tier 3 Migration (`tier3/migrate_tier3.py`)
- **Source:** `cortex-brain/development-context.yaml`
- **Target:** `cortex-brain/corpus-callosum/tier3/development-context.json`
- **Duration:** 30-45 minutes
- **What it migrates:**
  - Git activity metrics
  - Code change velocity
  - CORTEX usage patterns
  - Project health data
  - Correlations and insights
- **Features:**
  - Direct YAML to JSON conversion
  - Optimized structure for fast reads
  - Migration metadata included

### 4. End-to-End Validation (`migrations/test_migration.py`)
- **Duration:** 30-45 minutes
- **What it validates:**
  - All database schemas created correctly
  - Data migrated successfully
  - FTS5 search operational
  - Required sections present
- **Features:**
  - Comprehensive health checks
  - Data count verification
  - Index validation
  - Full-text search testing

### 5. Master Runner (`migrations/run_all_migrations.py`)
- **Duration:** 3.5-4.5 hours total
- **What it does:**
  - Orchestrates all three migrations
  - Runs validation automatically
  - Provides detailed progress reporting
  - Exit codes for CI/CD integration

## Usage

### Quick Start (Recommended)

Run all migrations with validation:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX/CORTEX/src/migrations
python3 run_all_migrations.py
```

### Individual Migrations

Run specific tier migrations:

```bash
# Tier 1 only
python3 ../tier1/migrate_tier1.py

# Tier 2 only
python3 ../tier2/migrate_tier2.py

# Tier 3 only
python3 ../tier3/migrate_tier3.py

# Validation only
python3 test_migration.py
```

### Advanced Options

Skip specific tiers:

```bash
# Skip Tier 1 (already migrated)
python3 run_all_migrations.py --skip-tier1

# Skip validation (migration only)
python3 run_all_migrations.py --skip-validation

# Custom brain directory
python3 run_all_migrations.py --brain-dir /path/to/cortex-brain
```

Custom source/target paths:

```bash
# Tier 1 with custom paths
python3 ../tier1/migrate_tier1.py \
  --source /path/to/conversation-history.jsonl \
  --target /path/to/conversations.db

# Tier 2 with custom paths
python3 ../tier2/migrate_tier2.py \
  --source /path/to/knowledge-graph.yaml \
  --target /path/to/patterns.db

# Tier 3 with custom paths
python3 ../tier3/migrate_tier3.py \
  --source /path/to/development-context.yaml \
  --target /path/to/development-context.json
```

## Expected Output

### Successful Migration

```
============================================================
CORTEX BRAIN MIGRATION
============================================================
Start time: 2025-11-06 14:30:00
Brain directory: /Users/asifhussain/PROJECTS/CORTEX/cortex-brain

============================================================
Tier 1 Migration (Working Memory - JSONL to SQLite)
============================================================
Creating database schema...
Reading from conversation-history.jsonl...

Migration complete!
Conversations: 14
Messages: 87
Entities: 45
Files: 28

✅ Tier 1 Migration completed successfully

============================================================
Tier 2 Migration (Knowledge Graph - YAML to SQLite with FTS5)
============================================================
Creating database schema with FTS5...
Reading from knowledge-graph.yaml...
Migrating validation insights...
Migrating workflow patterns...
Migrating intent patterns...

Migration complete!
Validation insights: 12
Workflow patterns: 8
Intent patterns: 15
File relationships: 6
Total patterns: 41

✅ Tier 2 Migration completed successfully

============================================================
Tier 3 Migration (Development Context - YAML to JSON)
============================================================
Reading from development-context.yaml...
Writing to development-context.json...

Migration complete!
Sections migrated: 8

✅ Tier 3 Migration completed successfully

============================================================
Migration Validation (End-to-End)
============================================================

🎉 ALL VALIDATIONS PASSED - Migration successful!

============================================================
MIGRATION SUMMARY
============================================================
End time: 2025-11-06 14:35:00

Tier1: ✅ SUCCESS
Tier2: ✅ SUCCESS
Tier3: ✅ SUCCESS
Validation: ✅ SUCCESS

🎉 All migrations completed successfully!
```

## Dependencies

### Required Python Packages

```bash
# Install with pip
pip install pyyaml

# Or using requirements.txt
pip install -r ../../requirements.txt
```

### System Requirements

- Python 3.8+
- SQLite 3.24+ (for FTS5 support)
- 100MB free disk space (for databases)

## File Structure After Migration

```
cortex-brain/
├── conversation-history.jsonl          # Original (keep as backup)
├── knowledge-graph.yaml                # Original (keep as backup)
├── development-context.yaml            # Original (keep as backup)
│
├── left-hemisphere/
│   └── tier1/
│       └── conversations.db            # NEW: SQLite database
│
├── right-hemisphere/
│   └── tier2/
│       └── patterns.db                 # NEW: SQLite + FTS5
│
└── corpus-callosum/
    └── tier3/
        └── development-context.json    # NEW: Optimized JSON
```

## Troubleshooting

### Issue: "Source file not found"

**Cause:** Migration script can't find source YAML/JSONL files

**Solution:**
```bash
# Check file exists
ls -la /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/conversation-history.jsonl

# Use custom path
python3 run_all_migrations.py --brain-dir /path/to/cortex-brain
```

### Issue: "FTS5 not available"

**Cause:** SQLite compiled without FTS5 support

**Solution:**
```bash
# Check SQLite version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"

# Install newer SQLite (macOS)
brew install sqlite3

# Verify FTS5 support
python3 -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.execute('CREATE VIRTUAL TABLE test USING fts5(content)'); print('FTS5 available')"
```

### Issue: "Permission denied"

**Cause:** Scripts not executable or directory permissions

**Solution:**
```bash
# Make scripts executable
chmod +x *.py ../tier1/*.py ../tier2/*.py ../tier3/*.py

# Check directory permissions
ls -la /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/
```

### Issue: "JSON decode error"

**Cause:** Malformed JSONL in conversation-history.jsonl

**Solution:**
```bash
# Validate JSONL
python3 -c "
import json
with open('/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/conversation-history.jsonl') as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f'Error on line {i}: {e}')
"
```

## Safety & Rollback

### Pre-Migration Backup

```bash
# Create backup before migration
cd /Users/asifhussain/PROJECTS/CORTEX
git add cortex-brain/
git commit -m "Pre-migration backup: YAML/JSONL data"
git tag pre-sqlite-migration
```

### Rollback Procedure

```bash
# If migration fails, rollback to backup
git checkout pre-sqlite-migration -- cortex-brain/

# Remove failed databases
rm -f cortex-brain/left-hemisphere/tier1/conversations.db
rm -f cortex-brain/right-hemisphere/tier2/patterns.db
rm -f cortex-brain/corpus-callosum/tier3/development-context.json
```

## Performance Benchmarks

| Tier | Records | Migration Time | Database Size |
|------|---------|----------------|---------------|
| Tier 1 | ~20 conversations | ~15 seconds | ~500 KB |
| Tier 2 | ~50 patterns | ~20 seconds | ~300 KB |
| Tier 3 | ~8 sections | ~5 seconds | ~50 KB |
| **Total** | **~78 records** | **~45 seconds** | **~850 KB** |

## Next Steps

After successful migration:

1. ✅ **Backup originals:**
   ```bash
   mv cortex-brain/conversation-history.jsonl cortex-brain/backups/
   mv cortex-brain/knowledge-graph.yaml cortex-brain/backups/
   mv cortex-brain/development-context.yaml cortex-brain/backups/
   ```

2. ✅ **Test CORTEX functionality:**
   ```bash
   # Test conversation retrieval
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('cortex-brain/left-hemisphere/tier1/conversations.db')
   cursor = conn.cursor()
   cursor.execute('SELECT title, started FROM conversations ORDER BY started DESC LIMIT 5')
   for row in cursor.fetchall():
       print(f'{row[1]}: {row[0]}')
   "
   ```

3. ✅ **Update CORTEX code:**
   - Modify data access layer to use SQLite
   - Update query methods for FTS5
   - Test all agent operations

4. ✅ **Proceed to Sub-Group 3B:** Implement Tier 1 ConversationManager class

## Documentation

- **Implementation Plan:** `cortex-design/IMPLEMENTATION-PLAN-V3.md` (lines 237-241)
- **Architecture:** `docs/tiers/tier1-working-memory.md`
- **Test Strategy:** `CORTEX/tests/migrations/test_migration_strategy.md`

## Status

**✅ Sub-Group 3A Complete:** Migration tools ready for testing

**Next:** Sub-Group 3B - Tier 1 Working Memory implementation
