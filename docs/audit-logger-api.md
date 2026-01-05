# CORTEX Audit Logger - API Documentation

**Version:** 1.0.0  
**Last Updated:** 2026-01-05  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Configuration](#configuration)
4. [Integration Examples](#integration-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The CORTEX Audit Logger provides enterprise-grade logging with self-healing capabilities, feature flags, graceful degradation, and comprehensive monitoring.

**Key Features:**
- Structured JSON logging (JSONL format)
- Async writes with buffering
- Self-healing with circuit breaker
- Feature flags with runtime reload
- Graceful degradation (5 operational modes)
- Prometheus metrics + Grafana dashboards
- Multi-environment support (dev/staging/prod)

---

## Core Classes

### AuditLogger

**Location:** `src/logging/audit_logger.py`

Main audit logging interface with singleton pattern.

#### Methods

##### `get_instance() -> AuditLogger`
Get singleton instance of audit logger.

```python
from src.logging.audit_logger import AuditLogger

logger = AuditLogger.get_instance()
```

##### `configure(config_path: str) -> None`
Load configuration from YAML file.

```python
logger.configure("cortex-brain/config/audit-logging-prod.yaml")
```

##### `log(level: str, message: str, context: Dict[str, Any] = None) -> None`
Log a message with optional context.

**Parameters:**
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL, AUDIT)
- `message`: Log message
- `context`: Additional context dictionary

```python
logger.log("INFO", "User authentication successful", {
    "user_id": "user123",
    "session_id": "sess456",
    "ip_address": "192.168.1.1"
})
```

##### `log_orchestrator_start(orchestrator: str, request: str) -> str`
Log orchestrator start and return operation ID.

```python
operation_id = logger.log_orchestrator_start(
    orchestrator="planning_v5",
    request="Create OAuth2 authentication plan"
)
```

##### `log_orchestrator_complete(operation_id: str, result: Dict[str, Any]) -> None`
Log orchestrator completion.

```python
logger.log_orchestrator_complete(operation_id, {
    "status": "success",
    "duration_ms": 1250,
    "files_created": 8
})
```

##### `log_error(error: Exception, context: Dict[str, Any] = None) -> None`
Log an error with stack trace.

```python
try:
    # ... operation
except Exception as e:
    logger.log_error(e, {"operation": "file_write", "path": "/logs/audit/..."})
```

##### `flush() -> None`
Flush buffer to disk immediately.

```python
logger.flush()
```

---

### FeatureFlagManager

**Location:** `src/logging/feature_flags.py`

Manages feature flags with runtime reload.

#### Methods

##### `get_feature_flags() -> FeatureFlagManager`
Get singleton instance.

```python
from src.logging.feature_flags import get_feature_flags

flags = get_feature_flags()
```

##### `load_from_config(config_path: str) -> None`
Load feature flags from configuration.

```python
flags.load_from_config("cortex-brain/config/feature-flags.yaml")
```

##### `is_enabled(feature_name: str, orchestrator: str = None) -> bool`
Check if feature is enabled.

```python
if flags.is_enabled("detailed_logging", orchestrator="planning_v5"):
    # Feature-specific code
    pass
```

##### `enable_feature(feature_name: str) -> None`
Enable a feature flag at runtime.

```python
flags.enable_feature("performance_monitoring")
```

##### `disable_feature(feature_name: str) -> None`
Disable a feature flag at runtime.

```python
flags.disable_feature("verbose_tracing")
```

##### `start_auto_reload(interval: int = 60) -> None`
Start automatic configuration reload.

```python
flags.start_auto_reload(interval=30)  # Reload every 30 seconds
```

---

### DegradationHandler

**Location:** `src/logging/degradation_handler.py`

Handles graceful degradation with circuit breaker.

#### Methods

##### `DegradationHandler(config: Dict[str, Any] = None)`
Initialize degradation handler.

```python
from src.logging.degradation_handler import DegradationHandler

handler = DegradationHandler({
    "circuit_breaker_threshold": 50,
    "circuit_breaker_timeout_seconds": 60,
    "error_threshold_per_minute": 100
})
```

##### `handle_write_failure(error: Exception, log_entry: Dict[str, Any]) -> bool`
Handle log write failure with fallback.

```python
success = handler.handle_write_failure(error, log_entry)
if not success:
    # Ultimate fallback
    print(f"CRITICAL: Failed to log: {log_entry}", file=sys.stderr)
```

##### `attempt_recovery() -> bool`
Attempt to recover to normal operational mode.

```python
if handler.attempt_recovery():
    logger.info("Successfully recovered to normal mode")
```

##### `get_health_check() -> Dict[str, Any]`
Get health check status.

```python
health = handler.get_health_check()
print(f"Status: {health['status']}")
print(f"Mode: {health['operational_mode']}")
```

---

### AlertManager

**Location:** `src/logging/monitoring/alert_manager.py`

Monitoring and alerting with Grafana integration.

#### Methods

##### `get_alert_manager() -> AlertManager`
Get singleton instance.

```python
from src.logging.monitoring.alert_manager import get_alert_manager

alerts = get_alert_manager()
```

##### `record_metric(name: str, value: float, labels: Dict[str, str] = None) -> None`
Record a metric value.

```python
alerts.record_metric("audit_log_entries_total", 1)
alerts.record_metric("audit_write_latency_ms", 2.5, {"orchestrator": "planning_v5"})
```

##### `evaluate_alerts() -> List[Alert]`
Evaluate alert rules and return new alerts.

```python
new_alerts = alerts.evaluate_alerts()
for alert in new_alerts:
    print(f"ALERT: {alert.message}")
```

##### `start_monitoring(interval: int = 30) -> None`
Start background monitoring thread.

```python
alerts.start_monitoring(interval=30)  # Evaluate every 30 seconds
```

##### `export_prometheus_metrics() -> str`
Export metrics in Prometheus format.

```python
metrics = alerts.export_prometheus_metrics()
print(metrics)
```

##### `export_grafana_dashboard(output_path: str) -> None`
Export Grafana dashboard JSON.

```python
alerts.export_grafana_dashboard("dashboards/audit-logger.json")
```

---

## Configuration

### Environment-Specific Configs

**Development:** `cortex-brain/config/audit-logging-dev.yaml`
- Log level: DEBUG
- Encryption: Disabled
- Console output: Enabled

**Staging:** `cortex-brain/config/audit-logging-staging.yaml`
- Log level: INFO
- Encryption: Enabled (test mode)
- Console output: Disabled

**Production:** `cortex-brain/config/audit-logging-prod.yaml`
- Log level: WARNING
- Encryption: Enabled (full)
- Console output: Disabled

### Configuration Structure

```yaml
audit_logging:
  enabled: true
  environment: "production"
  log_level: "WARNING"
  
  file:
    base_path: "/var/log/cortex/audit"
    format: "jsonl"
    rotation:
      max_size_mb: 500
      max_files: 200
      
  buffer:
    size: 10000
    flush_interval_seconds: 1
    
  security:
    encryption_enabled: true
    sanitize_pii: true
    
  self_healing:
    enabled: true
    max_retry_attempts: 5
```

---

## Integration Examples

### Basic Integration

```python
from src.logging.audit_logger import AuditLogger

# Initialize logger
logger = AuditLogger.get_instance()
logger.configure("cortex-brain/config/audit-logging-prod.yaml")

# Log operation
logger.log("INFO", "Processing user request", {
    "user_id": "user123",
    "operation": "create_plan"
})
```

### Orchestrator Integration

```python
from src.logging.audit_logger import AuditLogger

class PlanningOrchestrator:
    def __init__(self):
        self.logger = AuditLogger.get_instance()
        
    def execute(self, request: str) -> Dict[str, Any]:
        # Log start
        op_id = self.logger.log_orchestrator_start(
            orchestrator="planning_v5",
            request=request
        )
        
        try:
            # Execute orchestrator logic
            result = self._create_plan(request)
            
            # Log completion
            self.logger.log_orchestrator_complete(op_id, {
                "status": "success",
                "plan_id": result["plan_id"],
                "files_created": result["file_count"]
            })
            
            return result
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation_id": op_id,
                "orchestrator": "planning_v5"
            })
            raise
```

### Feature Flag Integration

```python
from src.logging.feature_flags import is_feature_enabled

class MyOrchestrator:
    def process(self, data):
        # Check feature flag
        if is_feature_enabled("detailed_logging", orchestrator="my_orchestrator"):
            self.log_detailed_context(data)
        
        # Process data
        result = self._process(data)
        
        # Conditional monitoring
        if is_feature_enabled("performance_monitoring"):
            self.record_performance_metrics(result)
            
        return result
```

### Alert Handler Integration

```python
from src.logging.monitoring.alert_manager import get_alert_manager

def send_slack_notification(alert):
    # Send alert to Slack
    requests.post(SLACK_WEBHOOK_URL, json={
        "text": f"🚨 {alert.severity.upper()}: {alert.message}"
    })

# Register notification handler
alerts = get_alert_manager()
alerts.add_notification_handler(send_slack_notification)
alerts.start_monitoring(interval=30)
```

---

## Best Practices

### 1. Configuration Management

✅ **DO:**
- Use environment-specific configs
- Store sensitive keys in environment variables
- Version control config templates (not production configs)

❌ **DON'T:**
- Hardcode configuration in code
- Commit production credentials
- Use same config across environments

### 2. Logging Levels

**DEBUG:** Development only, verbose details  
**INFO:** Normal operations, user actions  
**WARNING:** Unexpected but handled situations  
**ERROR:** Errors that need attention  
**CRITICAL:** System-critical failures  
**AUDIT:** Security-relevant events

### 3. Context Data

✅ **DO:**
- Include operation IDs for tracing
- Add user/session context
- Log timestamps (auto-added)

❌ **DON'T:**
- Log PII without sanitization
- Log passwords or tokens
- Log entire request bodies

### 4. Performance

✅ **DO:**
- Use async writes
- Enable buffering
- Set appropriate flush intervals

❌ **DON'T:**
- Call `flush()` after every log
- Log in tight loops
- Disable buffering in production

### 5. Error Handling

✅ **DO:**
- Always catch and log exceptions
- Include context in error logs
- Use structured error data

❌ **DON'T:**
- Silently swallow errors
- Log and re-raise without context
- Assume logging will never fail

---

## Troubleshooting

### Issue: Logs not appearing

**Symptoms:** No log files created

**Solutions:**
1. Check if logging is enabled: `audit_logging.enabled: true`
2. Verify directory permissions: `chmod 0750 logs/audit/`
3. Check disk space: `df -h`
4. Review degradation handler status

### Issue: High latency

**Symptoms:** P95 latency >100ms

**Solutions:**
1. Increase buffer size: `buffer.size: 10000`
2. Reduce flush interval: `buffer.flush_interval_seconds: 1`
3. Enable compression: `file.compression.enabled: true`
4. Check disk I/O performance

### Issue: Feature flags not updating

**Symptoms:** Runtime config changes not applied

**Solutions:**
1. Verify auto-reload is enabled: `flags.start_auto_reload()`
2. Check config file syntax: `yaml.safe_load(config_file)`
3. Review reload interval
4. Check file permissions

### Issue: Alerts not firing

**Symptoms:** No alerts despite high error rate

**Solutions:**
1. Start monitoring: `alerts.start_monitoring()`
2. Check alert rules configuration
3. Verify metrics are being recorded
4. Review threshold values

---

## API Reference Summary

| Class | Primary Methods | Purpose |
|-------|----------------|---------|
| `AuditLogger` | `log()`, `log_orchestrator_start()`, `flush()` | Main logging interface |
| `FeatureFlagManager` | `is_enabled()`, `enable_feature()`, `start_auto_reload()` | Feature flag control |
| `DegradationHandler` | `handle_write_failure()`, `attempt_recovery()`, `get_health_check()` | Graceful degradation |
| `AlertManager` | `record_metric()`, `evaluate_alerts()`, `export_prometheus_metrics()` | Monitoring & alerting |

---

**Version:** 1.0.0  
**Support:** See operations guide for troubleshooting  
**Contributing:** See developer guide for contribution guidelines
