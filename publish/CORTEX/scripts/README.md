# CORTEX Scripts

This directory contains utility scripts for CORTEX operations.

## Directory Structure

```
scripts/
├── cortex/          → Active CORTEX 1.0 scripts
└── _archive/        → Legacy KDS scripts (preserved for history)
```

## Active Scripts (`cortex/`)

### Migration Scripts
- **`migrate-all-tiers.py`** - Runs all tier migrations
- **`migrate-tier1-to-sqlite.py`** - Migrates Tier 1 (Working Memory) to SQLite
- **`migrate-tier2-to-sqlite.py`** - Migrates Tier 2 (Knowledge Graph) to SQLite  
- **`migrate-tier3-to-sqlite.py`** - Migrates Tier 3 (Context Intelligence) to SQLite
- **`validate-migrations.py`** - Validates migration integrity

### Setup & Configuration
- **`install-cortex.py`** - Installs CORTEX dependencies
- **`init-mind-palace-brain.py`** - Initializes brain structure

### Development Tools
- **`cortex-capture.ps1`** - Captures work sessions
- **`cortex_cli.py`** - CLI interface for CORTEX operations
- **`record-mkdocs-session.py`** - Records documentation sessions
- **`test-conversation-tracking.py`** - Tests conversation tracking

## Usage

### Run a migration
```bash
python scripts/cortex/migrate-all-tiers.py
```

### Initialize brain
```bash
python scripts/cortex/init-mind-palace-brain.py
```

### Capture work session
```powershell
.\scripts\cortex\cortex-capture.ps1
```

## Archive

Legacy KDS scripts are preserved in `_archive/kds-legacy/` for reference but are not used in CORTEX 1.0.
