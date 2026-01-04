# 🚀 QUICK-START: VSCode Cache Manager Integration

**Status:** ⚡ IMMEDIATE ACTION  
**Updated:** January 4, 2026  
**Phase:** 2-4 (Integration & Testing)  
**Duration:** 1.5 hours remaining  

---

## ✅ PHASE 1 COMPLETE

**Core Utility:** `src/operations/utilities/vscode_cache_manager.py` (557 lines)

✅ **Fully Implemented:**
- `VSCodeCacheManager` class with cross-platform support (Windows, macOS, Linux)
- `pre_flight_optimize()` - Lightweight cache clearing (< 100 MB target)
- `full_cleanup()` - Aggressive cleanup for maintenance workflows
- `health_check()` - Diagnostics and metrics
- Error handling with graceful fallback
- Dry-run mode for safe testing

---

## ⏳ PHASE 2: Orchestrator Integration (45 minutes)

### Target Orchestrators

1. **Planning Orchestrator v5** (`src/orchestrators/planning_orchestrator_v5.py`)
2. **Investigation Orchestrator** (`src/orchestrators/investigation_orchestrator.py`)
3. **Vacuum Orchestrator** (`src/orchestrators/vacuum_orchestrator.py`)
4. **Maintenance Orchestrator** (`src/orchestrators/maintenance_orchestrator.py`)

### Integration Pattern

**Add to each orchestrator's main execution method:**

```python
from src.operations.utilities.vscode_cache_manager import VSCodeCacheManager

class PlanningOrchestratorV5:
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning workflow with pre-flight cache optimization."""
        
        # ========== PHASE 0.5: PRE-FLIGHT CACHE OPTIMIZATION ==========
        try:
            cache_mgr = VSCodeCacheManager()
            cache_result = cache_mgr.pre_flight_optimize(
                dry_run=False,
                log_metrics=True,
                fail_silently=True  # Don't block execution on cache errors
            )
            
            if cache_result.get('success'):
                freed_mb = cache_result.get('freed_mb', 0)
                logger.info(f"Pre-flight cache optimization: {freed_mb:.2f} MB freed")
            else:
                logger.warning(f"Pre-flight cache optimization skipped: {cache_result.get('error', 'Unknown')}")
        
        except Exception as e:
            logger.warning(f"Pre-flight cache optimization failed (non-critical): {e}")
        # ==============================================================
        
        # Continue with normal execution
        logger.info("Starting Phase 1: Discovery...")
        # ... existing code ...
```

### Integration Checklist

For **each orchestrator**:

- [ ] Import `VSCodeCacheManager` at top of file
- [ ] Add pre-flight block at start of main execution method
- [ ] Set `fail_silently=True` (never block execution)
- [ ] Log results at INFO level (success) or WARNING level (failure)
- [ ] Test dry-run mode first (`dry_run=True`)
- [ ] Verify no disruption to existing workflow

**Estimated Time:** 10-12 minutes per orchestrator × 4 = 45 minutes

---

## ⏳ PHASE 3: Configuration Schema (30 minutes)

### Target File: `cortex.config.json`

**Add new section:**

```json
{
  "cache_management": {
    "enabled": true,
    "pre_flight": {
      "enabled": true,
      "threshold_mb": 100,
      "log_metrics": true,
      "orchestrators": {
        "planning_v5": true,
        "investigation": true,
        "vacuum": true,
        "maintenance": true
      }
    },
    "maintenance": {
      "full_cleanup": true,
      "reload_window_threshold_mb": 500,
      "preserve_extensions": true
    },
    "paths": {
      "log_file": "logs/cache-optimization.jsonl"
    }
  }
}
```

### Template File: `cortex.config.template.json`

Add same structure with comments:

```json
{
  "cache_management": {
    "_comment": "VSCode/Copilot cache management for optimal CORTEX performance",
    "enabled": true,
    "pre_flight": {
      "_comment": "Lightweight cache optimization before autonomous operations",
      "enabled": true,
      "threshold_mb": 100,
      "log_metrics": true,
      "orchestrators": {
        "_comment": "Enable/disable per orchestrator",
        "planning_v5": true,
        "investigation": true,
        "vacuum": true,
        "maintenance": true
      }
    }
  }
}
```

### Schema Validation

**File:** `cortex-brain/operations-config.yaml`

Add validation rules:

```yaml
vscode_cache:
  type: object
  properties:
    enabled:
      type: boolean
      default: true
    pre_flight:
      type: object
      properties:
        threshold_mb:
          type: integer
          minimum: 50
          maximum: 1000
          default: 100
```

**Estimated Time:** 30 minutes

---

## ⏳ PHASE 4: Maintenance Integration (30 minutes)

### Target: Maintenance Orchestrator Phase 11

**File:** `.github/prompts/maintenance/phase-11-completion.prompt.md`

**Update Phase 11 content:**

```markdown
## Phase 11: VSCode Cache & Extension Optimization

**Objective:** Deep clean VSCode caches, validate extension health, optimize IDE performance

### Tasks

1. **Pre-Flight Summary Review**
   - Aggregate pre-flight metrics from current session
   - Identify high-cache-growth orchestrators
   - Report cumulative cache freed during session

2. **Full Cache Cleanup**
   ```python
   cache_mgr = VSCodeCacheManager()
   result = cache_mgr.full_cleanup(
       dry_run=False,
       include_extension_vsix=True,
       include_cached_data=True
   )
   ```

3. **Extension Health Check**
   ```python
   health = cache_mgr.health_check()
   # Report: cache sizes, stale entries, recommendations
   ```

4. **Conditional Reload**
   - If freed > 500 MB OR health issues detected
   - Prompt user: "Reload Window to apply optimization?"
   - Log decision for metrics

### Success Criteria
- Full cleanup report generated
- All cache directories validated
- Reload recommendation provided if needed
- Metrics logged to `logs/cache-optimization.jsonl`
```

**Estimated Time:** 30 minutes

---

## 🧪 Testing Checklist

### Unit Tests

**File:** `tests/operations/utilities/test_vscode_cache_manager.py`

- [ ] Test cross-platform path resolution
- [ ] Test `pre_flight_optimize()` in dry-run mode
- [ ] Test `full_cleanup()` with mocked filesystem
- [ ] Test `health_check()` diagnostics
- [ ] Test error handling (permission denied, missing paths)
- [ ] Test metrics logging

**Run tests:**
```bash
pytest tests/operations/utilities/test_vscode_cache_manager.py -v
```

### Integration Tests

**For each orchestrator:**

1. **Dry Run Test:**
   ```python
   # Set dry_run=True in pre-flight block
   # Verify: logs show "Would clear X MB"
   # Verify: no actual cache deletion
   ```

2. **Live Test:**
   ```python
   # Set dry_run=False
   # Run short orchestrator operation
   # Verify: cache freed (if threshold exceeded)
   # Verify: orchestrator completes successfully
   ```

3. **Error Simulation:**
   ```python
   # Make cache directory read-only (chmod)
   # Verify: orchestrator continues (fail_silently=True)
   # Verify: warning logged
   ```

---

## 📊 Success Metrics

### Immediate (Post-Integration)

- [ ] All 4 orchestrators have pre-flight integration
- [ ] Configuration schema added to both config files
- [ ] Maintenance Phase 11 updated
- [ ] All unit tests pass (80%+ coverage)
- [ ] Integration smoke tests pass

### Short-Term (1 week)

- [ ] Pre-flight metrics logged for 10+ autonomous sessions
- [ ] Average cache freed: 50-150 MB per session
- [ ] Zero orchestrator execution failures due to cache operations
- [ ] User feedback: "CORTEX feels faster"

### Long-Term (1 month)

- [ ] 30-50% reduction in extension host memory footprint
- [ ] Reduced UI lag during long operations
- [ ] Fewer "Reload Window" manual interventions
- [ ] Positive user sentiment in feedback

---

## 🚨 Rollback Plan

If integration causes issues:

1. **Emergency Disable:**
   ```json
   // cortex.config.json
   "cache_management": { "enabled": false }
   ```

2. **Remove Integration:**
   - Comment out pre-flight blocks in orchestrators
   - Keep utility module (no harm if unused)

3. **Revert Config:**
   - Remove `cache_management` section from configs
   - Restore previous versions via git

---

## 📚 Documentation Updates

### Required Updates

1. **User-Facing:**
   - README.md: Mention automatic cache optimization
   - docs/architecture.md: Add VSCodeCacheManager to utilities diagram
   - docs/troubleshooting.md: Add "Cache optimization errors" section

2. **Developer-Facing:**
   - CONTRIBUTING.md: Add note about pre-flight pattern
   - docs/orchestrator-guide.md: Document integration pattern
   - API reference: Add VSCodeCacheManager methods

---

## 🎯 Next Action

**IMMEDIATE:** Start Phase 2 integration

**Command:**
```bash
# Verify utility exists and works
python3 -c "from src.operations.utilities.vscode_cache_manager import VSCodeCacheManager; mgr = VSCodeCacheManager(); print(mgr.health_check())"

# Start with Planning Orchestrator v5
code src/orchestrators/planning_orchestrator_v5.py
```

**Estimated Total Time:** 1.5 hours (45m + 30m + 30m)

---

## ✅ Completion Criteria

- [ ] All 4 orchestrators integrated with pre-flight optimization
- [ ] Configuration schema added and documented
- [ ] Maintenance Phase 11 extended with full cleanup
- [ ] Unit tests pass (80%+ coverage)
- [ ] Integration tests pass (dry-run + live)
- [ ] Documentation updated (user + developer)
- [ ] Smoke test with real autonomous operation (Planning v5 or Maintenance)
- [ ] Metrics logged successfully to `logs/cache-optimization.jsonl`

**When complete:** Mark Sub-Plan 00D as ✅ COMPLETE in `epic-progress-tracker.json`

---

**Author:** GitHub Copilot  
**Plan:** CORTEX-5.0 Sub-Plan 00D  
**Reference:** `vscode-cache-optimization-enhancement.md` (original proposal)
