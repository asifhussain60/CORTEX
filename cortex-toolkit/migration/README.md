# CORTEX Toolkit - Migration Tools

Database and schema migration utilities.

## Tools

### schema-migrate (`cortex-schema-migrate`)

**Purpose:** Migrate database schemas across versions.

**File:** `schema_migrator.py`

**Usage:**
```bash
python cortex-toolkit/migration/schema_migrator.py
```

**Features:**
- Schema version detection
- Incremental migrations
- Rollback support
- Migration history tracking

**Supported Databases:**
- SQLite (Tier 1, Tier 2, Tier 3)
- Planning database
- ADO database

---

### version-detect (`cortex-version-detect`)

**Purpose:** Detect CORTEX version and component versions.

**File:** `version_detector.py`

**Usage:**
```bash
python cortex-toolkit/migration/version_detector.py
```

**Features:**
- CORTEX version detection
- Component version tracking
- Compatibility checking
- Upgrade path determination

---

## Migration Process

1. **Detect Current Version:**
   ```bash
   python cortex-toolkit/migration/version_detector.py
   ```

2. **Run Migration:**
   ```bash
   python cortex-toolkit/migration/schema_migrator.py
   ```

3. **Verify Migration:**
   - Check logs in `logs/toolkit/`
   - Run validation tests
   - Confirm database integrity

## Safety

- **Always backup before migration**
- Migrations are logged to `logs/toolkit/`
- Rollback available for failed migrations
- Test migrations on copy first

## Integration

Migration tools integrate with:
- **Brain Tiers:** Tier 1, 2, 3 databases
- **Version Manager:** Component version tracking
- **Upgrade Orchestrator:** Automated upgrades
