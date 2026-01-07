# Phase 11: VSCode Cache & Extension Optimization

**Part of:** CORTEX Maintenance System (Modular v2.0)  
**Sub-Plan:** C50-00D (VSCode Cache Optimization)  
**Duration:** ~5 minutes  
**Mode:** Autonomous

---

## Purpose

Deep clean VSCode/Copilot caches and validate extension health to maximize IDE performance during autonomous orchestrations.

**Why this matters:**
- Long-running autonomous operations (30-90 min) accumulate cache/state
- VSCode extension host can cause UI lag and slow responses
- Copilot Chat storage can grow to 100MB+ impacting performance
- Manual cache clearing interrupts workflow

---

## Execution

### Step 1: Pre-Cleanup Health Check

```python
from src.operations.utilities.vscode_cache_manager import VSCodeCacheManager

manager = VSCodeCacheManager()
health_before = manager.health_check()

print("## 🔍 Cache Health Assessment")
print(f"**Platform:** {health_before['platform']}")
print(f"**Overall Status:** {health_before['overall_status']}")
print(f"**Total Size:** {health_before['total_size_mb']:.2f} MB\n")

for cache_name, cache_info in health_before['caches'].items():
    if cache_info.get('exists', False):
        print(f"- **{cache_name}**: {cache_info['size_mb']:.2f} MB ({cache_info['status']})")
    else:
        print(f"- **{cache_name}**: {cache_info['status']}")
```

### Step 2: Full Cache Cleanup

```python
# Execute full cleanup (non-blocking, fail-safe)
results = manager.full_cleanup(dry_run=False)

if results['success']:
    print(f"\n## ✅ Cache Cleanup Complete")
    print(f"**Total Freed:** {results['total_freed_mb']:.2f} MB")
    print(f"**Timestamp:** {results['timestamp']}\n")
    
    print("### Cleared Caches:")
    for cache_name, cache_info in results['cache_cleared'].items():
        if cache_info.get('freed_mb', 0) > 0:
            print(f"- **{cache_name}**: {cache_info['freed_mb']:.2f} MB freed")
else:
    print(f"\n## ⚠️ Cache Cleanup Failed (Non-Critical)")
    print(f"**Errors:** {results.get('errors', [])}")
```

### Step 3: Post-Cleanup Validation

```python
health_after = manager.health_check()

print(f"\n## 📊 Post-Cleanup Status")
print(f"**Overall Status:** {health_after['overall_status']}")
print(f"**Total Size:** {health_after['total_size_mb']:.2f} MB")

# Calculate improvement
size_before = health_before.get('total_size_mb', 0)
size_after = health_after.get('total_size_mb', 0)
improvement_pct = ((size_before - size_after) / size_before * 100) if size_before > 0 else 0

print(f"**Improvement:** {improvement_pct:.1f}% reduction")
```

---

## Success Criteria

### Must Pass (🚨 Critical)
- [ ] ✅ Cache cleanup executes without fatal errors
- [ ] ✅ Post-cleanup health check succeeds
- [ ] ✅ No workspace files affected (brain isolation validated)

### Should Pass (⚠️ Warning)
- [ ] ✅ All caches below threshold sizes:
  - Copilot Chat < 100 MB
  - Extension VSIX < 500 MB
  - General Cache < 500 MB
  - Cached Data < 1000 MB
- [ ] ✅ Total freed space > 0 MB (if caches existed)
- [ ] ✅ Overall health status = "✅ Healthy" or "⚠️ Warning"

### Nice to Have (📋 Info)
- [ ] Freed space > 50 MB (significant cleanup)
- [ ] All cache directories clean (0 MB)
- [ ] Metrics logged to `logs/cache-optimization.jsonl`

---

## Error Handling

**Non-Blocking Failures:**
- Permission errors → Skip files, continue
- Path resolution failures → Use fallback paths
- Metrics logging failures → Log warning, continue

**Fatal Failures:**
- None (Phase 11 is designed to never fail)

---

## Output Template

```markdown
# Phase 11: VSCode Cache Optimization

## 🔍 Pre-Cleanup Assessment
- Platform: macOS
- Overall Status: ⚠️ Warning - Consider Cleanup
- Total Size: 287.45 MB

**Cache Breakdown:**
- copilot_chat: 142.30 MB (⚠️ Warning)
- extension_vsix: 89.15 MB (✅ Healthy)
- general_cache: 56.00 MB (✅ Healthy)
- cached_data: 0.00 MB (✅ Clean)

## 🧹 Cleanup Execution
✅ Cache Cleanup Complete
**Total Freed:** 198.45 MB
**Duration:** 2.3 seconds

**Cleared Caches:**
- copilot_chat: 142.30 MB freed
- extension_vsix: 56.15 MB freed

## 📊 Post-Cleanup Validation
- Overall Status: ✅ Healthy
- Total Size: 89.00 MB
- **Improvement:** 69.0% reduction

✅ All success criteria met
```

---

## Integration Points

**Called by:**
- Maintenance Orchestrator (`.github/prompts/maintenance/index.prompt.md`)
- Manual `/CORTEX maintenance` command

**Dependencies:**
- `src/operations/utilities/vscode_cache_manager.py` (VSCodeCacheManager)
- `cortex.config.json` (`cache_management` section)

**Outputs:**
- Metrics: `logs/cache-optimization.jsonl`
- Report: Console output (markdown formatted)

---

## Implementation Notes

1. **Non-Destructive:** Only clears VSCode cache directories, never workspace files
2. **Fail-Safe:** Permission errors and missing paths handled gracefully
3. **Cross-Platform:** Automatically detects Windows/macOS/Linux cache locations
4. **Metrics:** All operations logged for performance tracking
5. **Idempotent:** Safe to run multiple times, only clears what exists

---

**Implementation Status:** ✅ Complete (C50-00D Phase 4)  
**Last Updated:** January 4, 2026

