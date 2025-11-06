# CORTEX Brain Migration Tools

Complete data migration system for CORTEX Brain from file-based storage (JSONL/YAML) to SQLite database.

## Overview

The CORTEX Brain uses a 3-tier architecture for storing different types of intelligence:

- **Tier 1: Working Memory** - Last 20 conversations (FIFO queue)
- **Tier 2: Knowledge Graph** - Learned patterns and relationships
- **Tier 3: Development Context** - Holistic project metrics

This migration system converts all existing file-based data to a centralized SQLite database with FTS5 full-text search capabilities.

## Migration Scripts

### Complete Migration (Recommended)

Migrates all tiers in one go:

**PowerShell:**
```powershell
.\scripts\migrate-cortex-brain.ps1
```

**Python:**
```bash
python scripts/migrate-all-tiers.py
```

### Individual Tier Migration

Migrate specific tiers independently:

**Tier 1 (Conversations):**
```bash
python scripts/migrate-tier1-to-sqlite.py
```

**Tier 2 (Knowledge Graph):**
```bash
python scripts/migrate-tier2-to-sqlite.py
```

**Tier 3 (Development Context):**
```bash
python scripts/migrate-tier3-to-sqlite.py
```

**PowerShell (single tier):**
```powershell
.\scripts\migrate-cortex-brain.ps1 -TierOnly 1  # Or 2, or 3
```

## Prerequisites

### Required

- Python 3.7 or higher
- `pyyaml` Python package (auto-installed by PowerShell script)

### Installation

**Install Python dependencies:**
```bash
pip install pyyaml
```

**Or let PowerShell auto-install:**
```powershell
.\scripts\migrate-cortex-brain.ps1
# Will check and install pyyaml if needed
```

## What Gets Migrated

### Tier 1: Working Memory

**Source Files:**
- `cortex-brain/conversation-history.jsonl`
- `cortex-brain/conversation-context.jsonl`

**Database Tables:**
- `tier1_conversations` - Conversation metadata
- `tier1_messages` - Individual messages
- `tier1_conversations_fts` - Full-text search index

**Features:**
- FIFO queue maintained (keeps last 20 conversations)
- Message threading preserved
- Context resolution maintained
- Intent detection history

### Tier 2: Knowledge Graph

**Source Files:**
- `cortex-brain/knowledge-graph.yaml`
- `cortex-brain/architectural-patterns.yaml`
- `cortex-brain/test-patterns.yaml`
- `cortex-brain/file-relationships.yaml`
- `cortex-brain/industry-standards.yaml`

**Database Tables:**
- `tier2_patterns` - All pattern types
- `tier2_file_relationships` - Co-modification tracking
- `tier2_patterns_fts` - Full-text search index

**Pattern Types Migrated:**
- Intent patterns
- Workflow patterns
- Validation insights
- Correction history
- Architectural patterns
- File relationships

### Tier 3: Development Context

**Source Files:**
- `cortex-brain/development-context.yaml`

**Database Tables:**
- `tier3_metrics` - All metrics (flattened and complete JSON)

**Metric Categories:**
- Git activity (commits, contributors, velocity)
- Code changes (churn, hotspots, growth)
- CORTEX usage (sessions, success rates, patterns)
- Testing activity (coverage, pass rates, flaky tests)
- Project health (builds, deployments, quality)
- Work patterns (productive times, focus duration)
- Correlations (metric relationships)
- Proactive insights (warnings, recommendations)

## Migration Process

### Step 1: Schema Initialization

Creates database with complete schema including:
- All tier tables
- FTS5 full-text search indexes
- Proper constraints and relationships
- Optimized indexes

```bash
python cortex-brain/migrate_brain_db.py
```

### Step 2: Data Migration

Sequentially migrates each tier:

1. **Tier 1:** Loads JSONL, applies FIFO, inserts to SQLite
2. **Tier 2:** Parses YAML, converts patterns, inserts to SQLite
3. **Tier 3:** Flattens metrics, stores both detailed and complete JSON

### Step 3: Validation

Automatically validates:
- Row counts for all tables
- FTS5 index completeness
- Database integrity (PRAGMA integrity_check)
- No data loss

## Safety Features

### Automatic Backup

Before migration, existing database is backed up:

```
cortex-brain/cortex-brain.db
  ↓
cortex-brain/cortex-brain_backup_20251106_143022.db
```

**Skip backup:**
```powershell
.\scripts\migrate-cortex-brain.ps1 -SkipBackup
```

### Idempotent Operations

All migrations use `INSERT OR REPLACE`:
- Safe to run multiple times
- Updates existing records
- No duplicate data

### Rollback Support

If migration fails:
1. Restore from backup
2. Check error messages
3. Fix source data
4. Re-run migration

## Command-Line Options

### PowerShell Script

```powershell
.\scripts\migrate-cortex-brain.ps1 `
    -DbPath "custom/path/to/database.db" `
    -SourceDir "custom/cortex-brain" `
    -TierOnly 2 `
    -SkipBackup
```

**Parameters:**
- `-DbPath` - Database path (default: `cortex-brain/cortex-brain.db`)
- `-SourceDir` - Source directory (default: `cortex-brain`)
- `-TierOnly` - Migrate only tier 1, 2, 3, or "all" (default: "all")
- `-SkipBackup` - Skip creating backup

### Python Scripts

All Python scripts support:

```bash
python scripts/migrate-tier1-to-sqlite.py \
    --db-path cortex-brain/cortex-brain.db \
    --source-dir cortex-brain
```

**Arguments:**
- `--db-path` - Database path
- `--source-dir` - Source directory

## Validation & Testing

### Validate Migration Success

Check database contents:

```bash
sqlite3 cortex-brain/cortex-brain.db

-- Count conversations
SELECT COUNT(*) FROM tier1_conversations;

-- Count patterns
SELECT COUNT(*) FROM tier2_patterns;

-- Count metrics
SELECT COUNT(*) FROM tier3_metrics;

-- Test FTS5 search
SELECT * FROM tier1_conversations_fts WHERE tier1_conversations_fts MATCH 'dashboard';

-- Integrity check
PRAGMA integrity_check;
```

### Expected Results

After successful migration:

```
📊 Summary:
  - Total conversations: 14
  - Total messages: 47
  - Total patterns: 156
  - Total file relationships: 23
  - Total metrics: 89
```

## Troubleshooting

### Python Not Found

**Error:** `Python not found!`

**Solution:**
```bash
# Install Python 3.7+
# macOS:
brew install python3

# Windows:
# Download from python.org
```

### Missing pyyaml Package

**Error:** `ModuleNotFoundError: No module named 'yaml'`

**Solution:**
```bash
pip install pyyaml
```

### Invalid JSON in JSONL

**Error:** `Line 5: Invalid JSON - Expecting property name...`

**Solution:**
1. Check `conversation-history.jsonl` line 5
2. Fix JSON syntax error
3. Re-run migration

### YAML Parse Error

**Error:** `Error loading knowledge-graph.yaml: ...`

**Solution:**
1. Validate YAML syntax
2. Fix indentation or special characters
3. Re-run migration

### Database Locked

**Error:** `database is locked`

**Solution:**
1. Close all connections to database
2. Stop any running CORTEX processes
3. Re-run migration

## Performance

### Migration Speed

Typical migration times:

- **Tier 1:** 2-5 seconds (20 conversations, 50-100 messages)
- **Tier 2:** 3-8 seconds (100-200 patterns)
- **Tier 3:** 1-3 seconds (flattened metrics)
- **Total:** ~10-20 seconds complete migration

### Database Size

Expected database sizes:

- **Tier 1:** ~50-100 KB (conversation history)
- **Tier 2:** ~100-200 KB (knowledge graph)
- **Tier 3:** ~50-100 KB (development metrics)
- **Total:** ~200-400 KB (compact and efficient)

### FTS5 Performance

Full-text search performance:

- **Query time:** <10ms for typical searches
- **Index size:** ~20-30% of table data
- **Rebuild time:** <1 second

## Post-Migration

### Verify Data Integrity

```powershell
# Run integrity tests
python cortex-brain/migrate_brain_db.py --db-path cortex-brain/cortex-brain.db

# Check FTS5 indexes
sqlite3 cortex-brain/cortex-brain.db "SELECT COUNT(*) FROM tier1_conversations_fts"
```

### Update CORTEX Agents

After migration, update agent prompts to use SQLite:

1. Update `intent-router.md` - Query tier1 for context
2. Update `work-planner.md` - Query tier2 for patterns
3. Update `brain-query.md` - Use SQL instead of file parsing

### Archive Old Files

Once migration validated:

```powershell
# Create archive
mkdir cortex-brain/archive
mv cortex-brain/*.yaml cortex-brain/archive/
mv cortex-brain/*.jsonl cortex-brain/archive/

# Keep .gitignore
git mv cortex-brain/archive/.gitignore cortex-brain/
```

## Architecture Benefits

### Why SQLite?

1. **Performance:** Sub-10ms queries vs 50-100ms file parsing
2. **Transactions:** Atomic updates, no file corruption
3. **Indexing:** FTS5 full-text search
4. **Relationships:** Proper foreign keys and joins
5. **Portability:** Single file, no external dependencies
6. **Reliability:** ACID compliant, battle-tested

### Schema Design

- **Normalized:** Proper table relationships
- **Indexed:** Fast lookups on common queries
- **Typed:** SQLite type affinity for data integrity
- **Searchable:** FTS5 indexes on all text content
- **Versioned:** Schema includes version tracking

## Future Enhancements

Planned improvements:

- [ ] Incremental migration (only new data)
- [ ] Migration rollback automation
- [ ] Data validation pre-migration
- [ ] Migration progress reporting
- [ ] Parallel tier migration
- [ ] Compressed archives post-migration

## Support

For issues or questions:

1. Check this README
2. Review error messages
3. Check database with `sqlite3` CLI
4. Create issue with error details

## License

Part of CORTEX Brain system - Internal use only
