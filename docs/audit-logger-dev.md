# CORTEX Audit Logger - Developer Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-05  
**Audience:** Developers, Contributors

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Guide](#integration-guide)
3. [Code Examples](#code-examples)
4. [Testing Guidelines](#testing-guidelines)
5. [Contributing](#contributing)
6. [Code Style](#code-style)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/cortex/audit-logger.git
cd audit-logger

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Basic Usage

```python
from src.logging.audit_logger import AuditLogger

# Initialize logger
logger = AuditLogger.get_instance()
logger.configure("cortex-brain/config/audit-logging-dev.yaml")

# Log a message
logger.log("INFO", "Application started", {
    "version": "1.0.0",
    "environment": "development"
})

# Flush on shutdown
logger.flush()
```

---

## Integration Guide

### 1. Orchestrator Integration

**Step 1: Import AuditLogger**
```python
from src.logging.audit_logger import AuditLogger

class MyOrchestrator:
    def __init__(self):
        self.logger = AuditLogger.get_instance()
```

**Step 2: Log Orchestrator Start**
```python
def execute(self, request: str) -> Dict[str, Any]:
    operation_id = self.logger.log_orchestrator_start(
        orchestrator="my_orchestrator_v1",
        request=request
    )
```

**Step 3: Log Operations**
```python
    try:
        # Your orchestrator logic
        result = self._process(request)
        
        # Log important operations
        self.logger.log("INFO", "Plan created", {
            "operation_id": operation_id,
            "plan_id": result["plan_id"]
        })
```

**Step 4: Log Completion or Errors**
```python
        # On success
        self.logger.log_orchestrator_complete(operation_id, {
            "status": "success",
            "duration_ms": (datetime.now() - start).total_seconds() * 1000,
            "result": result
        })
        
        return result
        
    except Exception as e:
        # On error
        self.logger.log_error(e, {
            "operation_id": operation_id,
            "orchestrator": "my_orchestrator_v1"
        })
        raise
```

### 2. Feature Flag Integration

```python
from src.logging.feature_flags import is_feature_enabled

class MyOrchestrator:
    def process(self, data):
        # Conditional logging
        if is_feature_enabled("verbose_logging", orchestrator="my_orchestrator"):
            self.logger.log("DEBUG", "Processing data", {
                "data_size": len(data),
                "data_type": type(data).__name__
            })
        
        # Feature-specific behavior
        if is_feature_enabled("advanced_validation"):
            self._validate_advanced(data)
        else:
            self._validate_basic(data)
```

### 3. Monitoring Integration

```python
from src.logging.monitoring.alert_manager import get_alert_manager

class MyOrchestrator:
    def __init__(self):
        self.alerts = get_alert_manager()
        
    def execute(self, request):
        start = time.time()
        
        try:
            result = self._process(request)
            
            # Record success metrics
            duration_ms = (time.time() - start) * 1000
            self.alerts.record_metric(
                "my_orchestrator_duration_ms",
                duration_ms,
                labels={"status": "success"}
            )
            
            return result
            
        except Exception as e:
            # Record error metrics
            self.alerts.record_metric(
                "my_orchestrator_errors_total",
                1,
                labels={"error_type": type(e).__name__}
            )
            raise
```

---

## Code Examples

### Example 1: Simple Logging

```python
from src.logging.audit_logger import AuditLogger

logger = AuditLogger.get_instance()

# Log with different levels
logger.log("DEBUG", "Detailed debugging information")
logger.log("INFO", "User logged in", {"user_id": "user123"})
logger.log("WARNING", "Rate limit approaching", {"current": 95, "max": 100})
logger.log("ERROR", "Database connection failed", {"database": "primary"})
logger.log("CRITICAL", "System out of memory", {"available_mb": 10})
```

### Example 2: Error Handling

```python
def risky_operation():
    try:
        # Operation that might fail
        result = external_api_call()
        return result
        
    except ConnectionError as e:
        logger.log_error(e, {
            "operation": "external_api_call",
            "retry_count": 3,
            "last_attempt": datetime.now().isoformat()
        })
        
        # Attempt recovery
        return fallback_operation()
        
    except Exception as e:
        logger.log_error(e, {
            "operation": "risky_operation",
            "unexpected": True
        })
        raise
```

### Example 3: Feature Flags

```python
from src.logging.feature_flags import get_feature_flags

# Load configuration
flags = get_feature_flags()
flags.load_from_config("config/feature-flags.yaml")

# Check feature
if flags.is_enabled("new_algorithm", orchestrator="planning_v5"):
    result = new_algorithm(data)
else:
    result = legacy_algorithm(data)

# Runtime enable/disable
flags.enable_feature("beta_feature")
flags.disable_feature("deprecated_feature")

# Auto-reload configuration
flags.start_auto_reload(interval=60)
```

### Example 4: Custom Metrics

```python
from src.logging.monitoring.alert_manager import get_alert_manager, MetricType

alerts = get_alert_manager()

# Register custom metric
alerts.register_metric(
    "my_custom_metric",
    MetricType.GAUGE,
    "Description of my metric"
)

# Record values
alerts.record_metric("my_custom_metric", 42.5)
alerts.record_metric("my_custom_metric", 38.2, labels={"region": "us-east"})

# Get latest value
metric = alerts.get_metric("my_custom_metric")
latest = metric.get_latest()
average = metric.get_average(window_seconds=60)
p95 = metric.get_percentile(95, window_seconds=60)
```

### Example 5: Custom Alert Handler

```python
from src.logging.monitoring.alert_manager import get_alert_manager

def send_email_alert(alert):
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(f"""
    Alert: {alert.name}
    Severity: {alert.severity.value}
    Message: {alert.message}
    Metric: {alert.metric_name}
    Current Value: {alert.current_value}
    Threshold: {alert.threshold}
    Timestamp: {alert.timestamp}
    """)
    
    msg['Subject'] = f"[{alert.severity.value.upper()}] CORTEX Alert: {alert.name}"
    msg['From'] = "alerts@cortex.io"
    msg['To'] = "ops@cortex.io"
    
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

# Register handler
alerts = get_alert_manager()
alerts.add_notification_handler(send_email_alert)
alerts.start_monitoring(interval=30)
```

### Example 6: Graceful Degradation

```python
from src.logging.degradation_handler import DegradationHandler, OperationalMode

handler = DegradationHandler({
    "circuit_breaker_threshold": 50,
    "error_threshold_per_minute": 100
})

def write_log(entry):
    try:
        # Normal write
        write_to_file(entry)
        
    except IOError as e:
        # Handle failure with degradation
        success = handler.handle_write_failure(e, entry)
        
        if not success:
            # Ultimate fallback
            print(f"CRITICAL: Log entry lost: {entry}", file=sys.stderr)

# Check current mode
current_mode = handler.get_current_mode()

if current_mode != OperationalMode.NORMAL:
    print(f"WARNING: Operating in {current_mode.value} mode")
    
# Attempt recovery
if handler.attempt_recovery():
    print("Successfully recovered to normal mode")
```

---

## Testing Guidelines

### Unit Tests

**Test Structure:**
```
tests/
├── logging/
│   ├── test_audit_logger.py
│   ├── test_log_buffer.py
│   ├── test_log_writer.py
│   ├── test_feature_flags.py
│   ├── test_degradation_handler.py
│   └── test_alert_manager.py
```

**Example Unit Test:**
```python
import pytest
from src.logging.audit_logger import AuditLogger

class TestAuditLogger:
    def setup_method(self):
        self.logger = AuditLogger.get_instance()
        self.logger.configure("tests/fixtures/test-config.yaml")
        
    def test_log_entry_created(self):
        """Test that log entry is created with correct structure"""
        self.logger.log("INFO", "Test message", {"key": "value"})
        
        # Verify log file created
        assert os.path.exists("logs/audit/test/operations.jsonl")
        
        # Verify log structure
        with open("logs/audit/test/operations.jsonl") as f:
            entry = json.loads(f.readline())
            
        assert entry["level"] == "INFO"
        assert entry["message"] == "Test message"
        assert entry["context"]["key"] == "value"
        assert "timestamp" in entry
        
    def test_error_logging(self):
        """Test that errors are logged with stack traces"""
        try:
            raise ValueError("Test error")
        except Exception as e:
            self.logger.log_error(e, {"test": True})
            
        # Verify error logged
        with open("logs/audit/test/errors.jsonl") as f:
            entry = json.loads(f.readline())
            
        assert entry["error_type"] == "ValueError"
        assert "stack_trace" in entry
        assert entry["context"]["test"] is True
```

### Integration Tests

**Example Integration Test:**
```python
@pytest.mark.integration
class TestOrchestratorIntegration:
    def test_full_orchestrator_lifecycle(self):
        """Test complete orchestrator execution with logging"""
        from src.orchestrators.planning import PlanningOrchestrator
        
        orchestrator = PlanningOrchestrator()
        result = orchestrator.execute("Create OAuth2 plan")
        
        # Verify logs created
        assert os.path.exists("logs/audit/planning_v5/")
        
        # Verify operation logged
        with open("logs/audit/planning_v5/operations.jsonl") as f:
            logs = [json.loads(line) for line in f]
            
        start_log = next(l for l in logs if l["operation"] == "orchestrator_start")
        complete_log = next(l for l in logs if l["operation"] == "orchestrator_complete")
        
        assert start_log["orchestrator"] == "planning_v5"
        assert complete_log["result"]["status"] == "success"
```

### Load Tests

**Example Load Test:**
```python
import pytest
import time
import concurrent.futures

@pytest.mark.load
def test_high_volume_logging():
    """Test logging performance under high volume"""
    logger = AuditLogger.get_instance()
    
    def log_entry(i):
        logger.log("INFO", f"Load test entry {i}", {"index": i})
    
    # Log 10,000 entries concurrently
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(log_entry, i) for i in range(10000)]
        concurrent.futures.wait(futures)
    duration = time.time() - start
    
    # Verify performance
    assert duration < 60  # Should complete in under 60 seconds
    assert logger.get_buffer_size() < 10000  # Buffer should flush
```

### Chaos Tests

**Example Chaos Test:**
```python
@pytest.mark.chaos
def test_disk_full_scenario():
    """Test behavior when disk is full"""
    from src.logging.degradation_handler import DegradationHandler, OperationalMode
    
    handler = DegradationHandler()
    logger = AuditLogger.get_instance()
    
    # Simulate disk full
    with patch('shutil.disk_usage', return_value=(100, 95, 5)):
        # Attempt to log
        logger.log("INFO", "Test entry")
        
        # Verify degradation
        health = handler.get_health_check()
        assert health['operational_mode'] != OperationalMode.NORMAL.value
        assert 'disk_full' in health['degradation_reasons']
```

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/logging/ -m "not integration and not load"

# Integration tests
pytest tests/ -m integration

# Load tests
pytest tests/ -m load

# With coverage
pytest tests/ --cov=src/logging --cov-report=html

# Verbose
pytest tests/ -v -s
```

---

## Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/cortex.git
cd cortex

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create feature branch
git checkout -b feature/my-feature
```

### Contribution Workflow

1. **Create Issue:** Describe feature/bug
2. **Fork & Branch:** Create feature branch
3. **Implement:** Write code + tests
4. **Test:** Run full test suite
5. **Document:** Update docs if needed
6. **Commit:** Follow commit message format
7. **Push:** Push to your fork
8. **PR:** Create pull request

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

**Example:**
```
feat(alert-manager): Add PagerDuty integration

- Implement PagerDuty notification handler
- Add configuration options
- Update tests and documentation

Closes #123
```

### Pull Request Guidelines

**PR Title:** Clear, descriptive (50 chars max)

**PR Description:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact assessed
```

### Code Review Process

1. **Automated Checks:** CI/CD pipeline must pass
2. **Peer Review:** 2 approvals required
3. **Documentation:** Must be updated
4. **Tests:** Coverage must not decrease
5. **Performance:** No significant degradation

---

## Code Style

### Python Style Guide

**Follow PEP 8:**
```python
# Good
def calculate_total_cost(items: List[Item]) -> Decimal:
    """Calculate total cost of items including tax."""
    subtotal = sum(item.price for item in items)
    tax = subtotal * Decimal('0.1')
    return subtotal + tax

# Bad
def calc(x):
    return x*1.1
```

### Type Hints

```python
from typing import Dict, List, Optional, Any

def process_data(
    data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Process data with optional configuration."""
    if options is None:
        options = []
    # ...
```

### Docstrings

```python
def log_orchestrator_start(
    self,
    orchestrator: str,
    request: str
) -> str:
    """
    Log orchestrator start and return operation ID.
    
    Args:
        orchestrator: Name of orchestrator (e.g., "planning_v5")
        request: User request being processed
        
    Returns:
        Unique operation ID for tracking
        
    Raises:
        ValueError: If orchestrator name is invalid
        IOError: If log write fails
        
    Example:
        >>> logger = AuditLogger.get_instance()
        >>> op_id = logger.log_orchestrator_start("planning_v5", "Create plan")
        >>> print(op_id)
        "op-123e4567-e89b-12d3-a456-426614174000"
    """
```

### Error Handling

```python
# Good - Specific exceptions
try:
    data = read_config(path)
except FileNotFoundError:
    logger.error(f"Config file not found: {path}")
    data = get_default_config()
except yaml.YAMLError as e:
    logger.error(f"Invalid YAML: {e}")
    raise ConfigurationError(f"Failed to parse config: {e}")

# Bad - Catch all
try:
    data = read_config(path)
except Exception:
    pass
```

### Naming Conventions

```python
# Constants
MAX_BUFFER_SIZE = 10000
DEFAULT_LOG_LEVEL = "INFO"

# Classes
class AuditLogger:
    pass

# Functions
def calculate_average():
    pass

# Variables
user_count = 0
is_enabled = True
```

---

## Additional Resources

- **API Documentation:** `docs/audit-logger-api.md`
- **Architecture:** `docs/audit-logger-architecture.md`
- **Operations Guide:** `docs/audit-logger-ops.md`
- **GitHub Issues:** https://github.com/cortex/audit-logger/issues
- **Slack Channel:** #audit-logger

---

**Version:** 1.0.0  
**Maintainers:** CORTEX Core Team  
**License:** MIT
