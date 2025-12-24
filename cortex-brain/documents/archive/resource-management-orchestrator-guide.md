# Resource Management Orchestrator - User Guide

**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 16  
**Version:** 3.8.1  
**Author:** Asif Hussain

---

## Overview

The Resource Management Orchestrator provides centralized monitoring and optimization of system resources (CPU, memory, disk) across all orchestrator operations. It enables proactive resource management with threshold-based alerting, allocation policies, and optimization recommendations.

---

## Features

### 1. CPU Monitoring
- **Real-time tracking:** Get current CPU usage percentage
- **History recording:** Track CPU usage over time (up to 1000 records)
- **Threshold alerts:** Automatic alerts when CPU exceeds configurable threshold
- **Performance:** <10ms per reading with `psutil.cpu_percent()`

### 2. Memory Tracking
- **Usage statistics:** Total, available, used, and percentage metrics
- **Leak detection:** Identify sustained memory increase patterns (>10% over period)
- **Threshold alerts:** Warning/critical alerts based on memory usage
- **Virtual memory:** Uses `psutil.virtual_memory()` for accurate readings

### 3. Disk Usage Monitoring
- **Multi-path support:** Monitor multiple mount points simultaneously
- **Storage metrics:** Total, used, free space, and percentage
- **Threshold alerts:** Configurable per-path disk usage alerts
- **Cross-platform:** Works on Linux, macOS, Windows

### 4. Resource Allocation
- **Priority-based:** Low/Medium/High priority levels
- **Weight configuration:** Custom CPU and memory weights per orchestrator
- **Active tracking:** Monitor all active resource allocations
- **Deallocation:** Automatic resource release after orchestrator completion

### 5. Performance Optimization
- **Bottleneck analysis:** Identify CPU, memory, or disk bottlenecks
- **Recommendations:** Actionable suggestions for optimization
- **Auto-scaling:** Detect when additional resources needed
- **Proactive alerts:** Prevent resource exhaustion before it happens

### 6. Monitoring Sessions
- **Per-orchestrator tracking:** Dedicated monitoring for specific orchestrators
- **Statistical reports:** Min/max/avg CPU and memory during session
- **Duration tracking:** Measure total execution time
- **Export reports:** JSON-formatted session summaries

---

## Usage

### Python API

```python
from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator

# Initialize with custom thresholds
manager = ResourceManagementOrchestrator(
    cpu_threshold=85.0,      # Alert if CPU > 85%
    memory_threshold=80.0,   # Alert if memory > 80%
    disk_threshold=90.0,     # Alert if disk > 90%
    monitoring_interval=1.0  # Check every 1 second
)

# Get current resource usage
cpu_usage = manager.get_cpu_usage()
memory_info = manager.get_memory_usage()
disk_info = manager.get_disk_usage(path="/")

print(f"CPU: {cpu_usage:.1f}%")
print(f"Memory: {memory_info['percent']:.1f}%")
print(f"Disk: {disk_info['percent']:.1f}%")

# Record CPU history for trending
for _ in range(10):
    manager.record_cpu_usage()
    time.sleep(1)

history = manager.get_cpu_history(limit=10)
print(f"Recorded {len(history)} CPU readings")

# Allocate resources to orchestrator
allocation = manager.allocate_resources(
    orchestrator_name="PlanningOrchestrator",
    priority="high"  # Gives CPU=0.5, Memory=0.4 weights
)

# Check for threshold breaches
cpu_alert = manager.check_cpu_threshold()
memory_alert = manager.check_memory_threshold()
disk_alert = manager.check_disk_threshold(path="/")

if cpu_alert:
    print(f"⚠️  {cpu_alert['message']}")

# Analyze bottlenecks and get recommendations
bottlenecks = manager.analyze_bottlenecks()
if bottlenecks:
    recommendations = manager.generate_recommendations(bottlenecks)
    for rec in recommendations:
        print(f"💡 {rec['resource']}: {rec['action']}")
        print(f"   Details: {rec['details']}")

# Start monitoring session for orchestrator
session_id = manager.start_monitoring_session(
    orchestrator_name="TDDOrchestrator",
    interval=0.5
)

# ... orchestrator runs ...

# Stop session and get report
report = manager.stop_monitoring_session(session_id)
print(f"Session duration: {report['duration_seconds']:.2f}s")
print(f"Avg CPU: {report['cpu_stats']['avg']:.1f}%")
print(f"Max memory: {report['memory_stats']['max']:.1f}%")

# Get resource summary
summary = manager.get_resource_summary()
print(f"Active allocations: {summary['active_allocations']}")
print(f"Active alerts: {summary['alerts']}")

# Deallocate resources after completion
manager.deallocate_resources("PlanningOrchestrator")
```

### Alert Management

```python
# Create custom alert
alert = manager.create_alert(
    resource="cpu",
    current_value=92.0,
    threshold=80.0,
    severity="critical"
)

# Get all alerts
all_alerts = manager.get_alert_history()

# Get only active (uncleared) alerts
active_alerts = manager.get_active_alerts()

# Clear resolved alert
manager.clear_alert(alert["alert_id"])
```

### Memory Leak Detection

```python
# Simulate increasing memory usage
readings = [
    {"percent": 50.0, "timestamp": "2025-12-13T10:00:00"},
    {"percent": 55.0, "timestamp": "2025-12-13T10:01:00"},
    {"percent": 60.0, "timestamp": "2025-12-13T10:02:00"},
    {"percent": 65.0, "timestamp": "2025-12-13T10:03:00"},
    {"percent": 70.0, "timestamp": "2025-12-13T10:04:00"}
]

leak_detected = manager.detect_memory_leak(readings)
if leak_detected:
    print("⚠️  Potential memory leak detected!")
```

### Configuration

```python
# Reconfigure thresholds at runtime
manager.configure_thresholds(
    cpu_threshold=90.0,
    memory_threshold=85.0,
    disk_threshold=95.0
)

# Configure monitoring settings
manager.configure_monitoring(
    interval=2.0,
    enabled=True
)

# Export current configuration
config = manager.export_configuration()
print(json.dumps(config, indent=2))
```

---

## Resource Allocation Policies

### Priority Levels

| Priority | CPU Weight | Memory Weight | Use Case |
|----------|-----------|---------------|----------|
| **Low** | 0.1 (10%) | 0.1 (10%) | Background tasks, cleanup jobs |
| **Medium** | 0.3 (30%) | 0.2 (20%) | Regular orchestrators, scheduled tasks |
| **High** | 0.5 (50%) | 0.4 (40%) | Critical operations, user-facing features |

### Custom Weights

```python
# Override defaults with custom weights
allocation = manager.allocate_resources(
    orchestrator_name="CustomOrchestrator",
    cpu_weight=0.35,    # 35% CPU allocation
    memory_weight=0.25, # 25% memory allocation
    priority="medium"   # For reference only
)
```

---

## Threshold Configuration

### Default Thresholds
- **CPU:** 80.0% (warning at >80%, critical at >95%)
- **Memory:** 75.0% (warning at >75%, critical at >90%)
- **Disk:** 85.0% (warning at >85%, critical at >95%)

### Severity Levels
- **Warning:** Resource approaching limit, action recommended
- **Critical:** Resource critically high, immediate action required

---

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| `get_cpu_usage()` | <10ms | With `interval=0.1` |
| `get_memory_usage()` | <5ms | Direct `psutil` call |
| `get_disk_usage()` | <20ms | Per path |
| `record_cpu_usage()` | <15ms | Includes history append |
| `analyze_bottlenecks()` | <50ms | All resources checked |
| `generate_recommendations()` | <5ms | Rule-based logic |

---

## Integration Examples

### With OrchestrationMetricsCollector

```python
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics
from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator

resource_manager = ResourceManagementOrchestrator()

@with_orchestration_metrics
async def my_orchestrator(request):
    # Allocate resources
    allocation = resource_manager.allocate_resources(
        orchestrator_name="MyOrchestrator",
        priority="high"
    )
    
    # Start monitoring session
    session_id = resource_manager.start_monitoring_session(
        orchestrator_name="MyOrchestrator",
        interval=1.0
    )
    
    try:
        # Your orchestrator logic
        result = await execute_logic(request)
        return result
    finally:
        # Stop monitoring and get report
        report = resource_manager.stop_monitoring_session(session_id)
        logger.info(f"Resource usage: CPU avg={report['cpu_stats']['avg']:.1f}%")
        
        # Deallocate resources
        resource_manager.deallocate_resources("MyOrchestrator")
```

### Auto-Scaling Detection

```python
# Collect load over time
load_history = []

for _ in range(5):
    cpu_usage = manager.get_cpu_usage()
    memory_info = manager.get_memory_usage()
    
    load_history.append({
        "cpu_percent": cpu_usage,
        "memory_percent": memory_info["percent"]
    })
    
    time.sleep(60)  # Sample every minute

# Check if scaling needed
if manager.should_auto_scale(load_history):
    print("📈 Auto-scaling recommended - sustained high load detected")
```

---

## Troubleshooting

### Issue: Inaccurate CPU readings
**Solution:** Increase `interval` parameter in `get_cpu_usage()`. Default 0.1s may be too short for stable readings.

### Issue: Memory leak not detected
**Solution:** Ensure at least 3 readings with sustained increase >10%. Verify `timestamp` field in readings.

### Issue: Disk usage shows 0%
**Solution:** Verify path exists and is accessible. Use absolute paths. Check file system permissions.

### Issue: Alerts not generated
**Solution:** Verify thresholds are configured correctly. Check that monitoring is enabled via `configure_monitoring()`.

---

## Dependencies

```python
psutil>=6.1.1  # Already in CORTEX requirements.txt
```

---

## Future Enhancements

- [ ] GPU monitoring support (NVIDIA, AMD)
- [ ] Network bandwidth tracking
- [ ] Container resource limits (Docker, Kubernetes)
- [ ] Historical trending with SQLite storage
- [ ] Predictive resource forecasting (ML-based)
- [ ] Integration with cloud auto-scaling APIs

---

## Copyright

© 2024-2025 Asif Hussain. All rights reserved.

**License:** Proprietary - CORTEX Enhancement Plan v2.0
