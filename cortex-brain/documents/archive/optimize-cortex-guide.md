# Optimize Cortex Orchestrator

**Purpose:** System optimization and maintenance - clean brain data, vacuum databases, improve performance

**Version:** 3.2.0  
**Status:** ✅ PRODUCTION

---

## Commands

- `optimize` or `optimize cortex` - Run all optimizations
- `optimize code` - Code optimization suggestions
- `optimize cache` - Clear and rebuild YAML cache

---

## What It Does

1. **Cleanup:** Removes old conversation captures (>30 days), temporary crawler files, debug logs
2. **Database Optimization:** Vacuums SQLite databases to reclaim space
3. **Cache Management:** Clears and rebuilds YAML cache for optimal performance
4. **Code Analysis:** Provides code optimization suggestions

---

## Results

**Typical Outcomes:**
- Space saved: 50-200 MB
- Performance improvement: 10-30% faster operations
- Database size reduction: 20-40%
- Improved query response times

---

## How It Works

1. **Discovery:** Scans cortex-brain folder for old files
2. **Analysis:** Identifies candidates for cleanup (age, size, usage patterns)
3. **Cleanup:** Safely removes temporary/old files
4. **Vacuum:** Optimizes database files (VACUUM command)
5. **Cache Rebuild:** Clears YAML cache, forces reload
6. **Report:** Generates summary of space saved and improvements

---

## Safety Features

- **Automatic Backup:** Creates backup before major operations
- **Dry Run Mode:** Preview changes without making them
- **Smart Preservation:** Never deletes active planning documents, knowledge graph data, user configurations
- **Rollback:** Can restore from backup if needed

---

## Configuration

**Configurable via cortex.config.json:**
```json
{
  "optimize": {
    "cleanup_age_days": 30,
    "enable_auto_backup": true,
    "vacuum_threshold_mb": 50,
    "cache_rebuild_frequency": "on_demand"
  }
}
```

---

## Integration Points

- **CleanupOrchestrator:** Shares cleanup logic
- **HealthCheckOrchestrator:** Validates system after optimization
- **Brain Databases:** Direct access to tier1-working-memory.db, tier2-knowledge-graph.db
- **YAML Cache:** Manages response-templates cache

---

## Natural Language Examples

- "optimize cortex"
- "clean up and optimize the system"
- "how much space can I save?"
- "optimize databases"

---

## Output

**Console:**
```
🔧 CORTEX System Optimization

✅ Cleanup Results:
   Old files removed: 47 files
   Space saved: 142 MB

✅ Database Optimization:
   Tier 1: 18% size reduction (45 MB → 37 MB)
   Tier 2: 22% size reduction (120 MB → 94 MB)

✅ Cache Management:
   YAML cache cleared and rebuilt
   Cache size: 2.3 MB

⚡ Performance: 18% faster query response times
```

**Files Created:**
- `cortex-brain/documents/reports/OPTIMIZATION-[timestamp].md`

---

## Testing

**Test File:** `tests/operations/modules/test_optimize_cortex_orchestrator.py`

**Coverage:** >70% required for deployment

---

## See Also

- Cleanup Orchestrator: `cortex-brain/documents/implementation-guides/cleanup-orchestrator.md`
- Health Check: `cortex-brain/documents/implementation-guides/healthcheck-orchestrator.md`
- System Alignment: `.github/prompts/modules/system-alignment-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
