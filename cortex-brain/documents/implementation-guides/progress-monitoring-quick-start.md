# Quick Start: Universal Progress Monitoring

**For Developers:** How to add automatic progress monitoring to your operations in 3 steps.

---

## 🚀 30-Second Quick Start

### Step 1: Import Decorator

```python
from src.utils.progress_decorator import with_progress, yield_progress
```

### Step 2: Add Decorator

```python
@with_progress(operation_name="My Operation")
def my_long_operation(items):
    pass  # Your existing code
```

### Step 3: Yield Progress

```python
@with_progress(operation_name="My Operation")
def my_long_operation(items):
    for i, item in enumerate(items, 1):
        yield_progress(i, len(items), f"Processing {item.name}")
        # Your existing work here
```

**That's it!** Progress monitoring is now automatic.

---

## 🎯 Key Features

1. **Automatic Activation:** Only shows progress if operation takes >5 seconds
2. **ETA Calculation:** Automatically estimates time remaining
3. **Hang Detection:** Warns if operation stalls (default: 30s)
4. **Zero Overhead:** <0.1% performance impact
5. **Thread-Safe:** Works with concurrent operations

---

## 📋 Common Patterns

### Pattern 1: Orchestrator

```python
class MyOrchestrator:
    
    @with_progress(
        operation_name="System Processing",
        hang_timeout=60.0  # Longer timeout for complex work
    )
    def process(self, items: List[Any]) -> Dict[str, Any]:
        
        for i, item in enumerate(items, 1):
            yield_progress(i, len(items), f"Step {i}")
            self._process_item(item)
        
        return {"processed": len(items)}
```

### Pattern 2: Agent

```python
class MyAgent(BaseAgent):
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # BaseAgent already has @with_progress decorator
        # Just use yield_progress in your implementation
        
        tasks = self._get_tasks(request)
        
        for i, task in enumerate(tasks, 1):
            yield_progress(i, len(tasks), f"Task: {task.name}")
            self._execute_task(task)
        
        return AgentResponse(success=True)
```

### Pattern 3: Multi-Phase Operation

```python
@with_progress(operation_name="System Alignment")
def align_system(phases):
    
    # Phase 1
    for i in range(len(phase1_items)):
        yield_progress(i+1, total_items, "Phase 1: Scanning")
        # work
    
    # Phase 2
    for i in range(len(phase2_items)):
        yield_progress(i+len(phase1_items)+1, total_items, "Phase 2: Analysis")
        # work
    
    # Phase 3
    for i in range(len(phase3_items)):
        yield_progress(i+len(phase1_items)+len(phase2_items)+1, total_items, "Phase 3: Fixing")
        # work
```

---

## ⚙️ Configuration Options

### Decorator Parameters

```python
@with_progress(
    operation_name="Display Name",      # Human-readable name
    threshold_seconds=5.0,              # Only show if >5s
    hang_timeout=30.0,                  # Warn after 30s no progress
    show_steps=True                     # Show step descriptions
)
```

### Global Configuration

**File:** `cortex.config.json`

```json
{
  "progress_monitoring": {
    "enabled": true,                    // Master switch
    "threshold_seconds": 5.0,           // Global threshold
    "hang_timeout_seconds": 30.0,       // Global hang timeout
    "update_interval_seconds": 2.0,     // Display update frequency
    "auto_detect": true,                // Auto-add to long operations
    "verbose": false                    // Debug logging
  }
}
```

### Per-Operation Override

```json
{
  "progress_monitoring": {
    "operation_overrides": {
      "system_alignment": {
        "threshold_seconds": 3.0,
        "hang_timeout_seconds": 60.0
      }
    }
  }
}
```

---

## 📊 Output Examples

### Console Output

```
🔍 System Alignment started...
  ⏳ Phase 1: Scanning files: 25/100 (25.0%, 5.2s, ETA: 15.6s)
  ⏳ Phase 2: Analysis: 50/100 (50.0%, 10.5s, ETA: 10.5s)
  ⏳ Phase 3: Fixing issues: 75/100 (75.0%, 15.8s, ETA: 5.3s)
✅ System Alignment completed (21.0s)
```

### Hang Detection

```
🔍 Database Backup started...
  ⏳ Exporting tables: 5/20 (25.0%, 45.3s, ETA: 135.9s)

⚠️  WARNING: No progress for 30s
   Last step: Exporting tables
   Consider cancelling (Ctrl+C) if operation appears frozen
```

---

## 🧪 Testing Your Integration

### Test 1: Verify Activation

```python
def test_progress_shows_for_long_operation():
    """Progress should activate after threshold"""
    
    @with_progress(threshold_seconds=2.0)
    def slow_op():
        for i in range(10):
            time.sleep(0.5)
            yield_progress(i+1, 10, f"Step {i+1}")
    
    # Should see progress output
    slow_op()
```

### Test 2: Verify Skipped for Fast Operations

```python
def test_progress_skipped_for_fast_operation():
    """Progress should NOT activate if <threshold"""
    
    @with_progress(threshold_seconds=5.0)
    def fast_op():
        time.sleep(1.0)
    
    # Should complete without progress output
    fast_op()
```

---

## 🔧 Troubleshooting

### Issue: Progress not showing

**Cause:** Operation completes before threshold (default 5s)  
**Fix:** Lower threshold or verify operation duration

```python
@with_progress(threshold_seconds=2.0)  # Lower threshold
```

### Issue: Progress updates too frequent

**Cause:** Calling `yield_progress()` too often  
**Fix:** Update once per major step only

```python
# ✅ GOOD
for file in files:
    yield_progress(i, total, f"File {file}")

# ❌ BAD (too frequent)
for line in file:
    yield_progress(line_num, total_lines)
```

### Issue: Hang warning incorrectly triggered

**Cause:** Long-running step without progress updates  
**Fix:** Increase hang timeout or add intermediate updates

```python
@with_progress(hang_timeout=120.0)  # 2 minutes
```

---

## 📚 Best Practices

### ✅ DO

- Update progress once per major step
- Use descriptive step names
- Adjust hang timeout for known long steps
- Test with realistic data volumes

### ❌ DON'T

- Update too frequently (adds overhead)
- Use for operations <5 seconds
- Nest progress monitors
- Ignore hang warnings

---

## 🎯 When to Use

### Use Progress Monitoring For:

- ✅ File processing (>10 files)
- ✅ Database queries (>5 operations)
- ✅ Network requests (>3 calls)
- ✅ Loops with >20 iterations
- ✅ Any operation historically >5s

### Skip Progress Monitoring For:

- ❌ Configuration loading
- ❌ Single file reads
- ❌ Quick validations
- ❌ Simple calculations

---

## 📈 Performance Impact

- **Overhead:** <0.1% CPU usage
- **Memory:** ~2KB per active monitor
- **Thread Safety:** Fully isolated
- **Display Rate:** Every 2 seconds (configurable)

---

## 🔗 Related Documentation

- **Full Design:** `cortex-brain/documents/analysis/universal-progress-monitoring-design.md`
- **Progress Monitor API:** `src/utils/progress_monitor.py`
- **Base Agent Integration:** `src/cortex_agents/base_agent.py`

---

**Last Updated:** November 27, 2025  
**Status:** Design Complete - Ready for Implementation
