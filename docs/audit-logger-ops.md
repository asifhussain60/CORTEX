# CORTEX Audit Logger - Operations Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-05  
**Audience:** DevOps, SRE, Operations Teams

---

## Table of Contents

1. [Deployment](#deployment)
2. [Configuration Management](#configuration-management)
3. [Monitoring & Health Checks](#monitoring--health-checks)
4. [Troubleshooting](#troubleshooting)
5. [Performance Tuning](#performance-tuning)
6. [Disaster Recovery](#disaster-recovery)
7. [Maintenance](#maintenance)

---

## Deployment

### Prerequisites

**System Requirements:**
- Python 3.9+
- 100 MB disk space (minimum)
- 256 MB RAM (per instance)
- Read/write permissions to `/var/log/cortex/audit` (or custom path)

**Dependencies:**
```bash
pip install pyyaml cryptography
```

### Quick Deployment

**Development:**
```bash
cd /path/to/CORTEX
./scripts/deploy_audit_logger.sh
```

**Staging:**
```bash
./scripts/deploy_audit_logger.sh --environment staging
```

**Production:**
```bash
./scripts/deploy_audit_logger.sh --environment production
```

### Deployment Steps (Manual)

#### 1. Create Directory Structure

```bash
# Base directory
sudo mkdir -p /var/log/cortex/audit

# Orchestrator subdirectories
for orchestrator in planning_v5 ado_v2 vacuum_v2 cleanup_v2 \
                    investigation_v2 tdd_v4 debug_v2 refinement_v2 \
                    maintenance_v2 sanitization_v2 master_orchestrator; do
    sudo mkdir -p /var/log/cortex/audit/$orchestrator
done

# Archives directory
sudo mkdir -p /var/log/cortex/audit/archives
```

#### 2. Set Permissions

```bash
# Directory permissions (rwxr-x---)
sudo find /var/log/cortex/audit -type d -exec chmod 0750 {} \;

# Set owner
sudo chown -R cortex:cortex /var/log/cortex/audit
```

#### 3. Copy Configuration

```bash
# Development
sudo cp cortex-brain/config/audit-logging-dev.yaml /etc/cortex/audit-logging.yaml

# Production
sudo cp cortex-brain/config/audit-logging-prod.yaml /etc/cortex/audit-logging.yaml
```

#### 4. Initialize Database (Optional)

```bash
python3 -c "
from src.logging.audit_logger import AuditLogger
logger = AuditLogger.get_instance()
logger.configure('/etc/cortex/audit-logging.yaml')
"
```

#### 5. Restart Service

```bash
# If using systemd
sudo systemctl restart cortex

# Or restart application manually
```

### Verification

```bash
# Check directory creation
ls -la /var/log/cortex/audit/

# Check permissions
stat -c "%a %n" /var/log/cortex/audit

# Test write access
touch /var/log/cortex/audit/.write_test && rm /var/log/cortex/audit/.write_test

# Check service status
systemctl status cortex
```

---

## Configuration Management

### Environment Variables

```bash
# Enable/disable audit logging
export CORTEX_AUDIT_ENABLED=true

# Set environment
export CORTEX_ENV=production

# Set log path
export CORTEX_AUDIT_PATH=/var/log/cortex/audit

# Set log level
export CORTEX_AUDIT_LEVEL=WARNING

# Encryption key (production)
export CORTEX_AUDIT_ENCRYPTION_KEY="<base64-encoded-key>"
```

### Configuration File Location

**Development:** `cortex-brain/config/audit-logging-dev.yaml`  
**Staging:** `cortex-brain/config/audit-logging-staging.yaml`  
**Production:** `/etc/cortex/audit-logging.yaml`

### Runtime Configuration Reload

```python
# Python API
from src.logging.feature_flags import get_feature_flags

flags = get_feature_flags()
flags.reload_config()
```

```bash
# Or send SIGHUP to process
kill -HUP $(pgrep -f cortex)
```

### Configuration Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('/etc/cortex/audit-logging.yaml'))"

# Validate with deployment script
./scripts/deploy_audit_logger.sh --dry-run --config /etc/cortex/audit-logging.yaml
```

### Backup Configuration

```bash
# Create backup
sudo cp /etc/cortex/audit-logging.yaml /etc/cortex/audit-logging.yaml.backup.$(date +%Y%m%d)

# Restore from backup
sudo cp /etc/cortex/audit-logging.yaml.backup.20260105 /etc/cortex/audit-logging.yaml
```

---

## Monitoring & Health Checks

### Health Check Endpoint

```python
from src.logging.degradation_handler import DegradationHandler

handler = DegradationHandler()
health = handler.get_health_check()

print(f"Status: {health['status']}")
print(f"Mode: {health['operational_mode']}")
print(f"Errors: {health['recent_error_count']}")
```

**Expected Output:**
```json
{
  "status": "healthy",
  "operational_mode": "normal",
  "degradation_reasons": [],
  "recent_error_count": 0,
  "circuit_breaker_state": "CLOSED",
  "memory_buffer_size": 0,
  "timestamp": "2026-01-05T08:00:00"
}
```

### Prometheus Metrics

**Expose metrics endpoint:**
```python
from src.logging.monitoring.alert_manager import get_alert_manager

alerts = get_alert_manager()
metrics = alerts.export_prometheus_metrics()

# Serve on HTTP endpoint
from http.server import HTTPServer, BaseHTTPRequestHandler

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(metrics.encode())

server = HTTPServer(('0.0.0.0', 9090), MetricsHandler)
server.serve_forever()
```

**Key Metrics:**
- `audit_log_entries_total` - Total log entries
- `audit_error_rate_per_minute` - Error rate
- `audit_write_latency_p95` - P95 write latency
- `audit_self_healing_success_rate` - Self-healing success %
- `audit_operational_mode` - Current mode (0=normal, 4=disabled)

### Grafana Dashboard

**Import dashboard:**
```bash
# Export dashboard JSON
python3 -c "
from src.logging.monitoring.alert_manager import get_alert_manager
alerts = get_alert_manager()
alerts.export_grafana_dashboard('dashboards/audit-logger.json')
"

# Import to Grafana
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/audit-logger.json
```

**Dashboard Panels:**
1. Log Volume (rate over 5min)
2. Error Rate (errors/min)
3. Write Latency (P50, P95, P99)
4. Self-Healing Success Rate (gauge)
5. Buffer Utilization (graph)
6. Operational Mode (stat)

### Alerting Rules

**Configure PagerDuty:**
```yaml
monitoring:
  pagerduty_integration: true
  pagerduty_key: "your-integration-key"
  alert_threshold_errors_per_minute: 10
```

**Configure Slack:**
```python
from src.logging.monitoring.alert_manager import get_alert_manager
import requests

def send_slack_alert(alert):
    requests.post(
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        json={"text": f"🚨 {alert.severity.upper()}: {alert.message}"}
    )

alerts = get_alert_manager()
alerts.add_notification_handler(send_slack_alert)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: No Logs Being Written

**Symptoms:**
- No files in `/var/log/cortex/audit/`
- Application running normally

**Diagnosis:**
```bash
# Check if logging is enabled
grep "enabled:" /etc/cortex/audit-logging.yaml

# Check permissions
ls -la /var/log/cortex/audit/

# Check disk space
df -h /var/log/cortex/

# Check application logs
journalctl -u cortex -n 100 | grep audit
```

**Solutions:**
1. Enable in config: `audit_logging.enabled: true`
2. Fix permissions: `sudo chmod 0750 /var/log/cortex/audit/`
3. Free disk space: Run cleanup/archival
4. Check degradation mode: May be in DISABLED mode

#### Issue 2: High Latency

**Symptoms:**
- P95 latency >100ms
- Application slowdown
- Buffer overflow alerts

**Diagnosis:**
```bash
# Check Prometheus metrics
curl http://localhost:9090/metrics | grep audit_write_latency

# Check buffer size
curl http://localhost:9090/metrics | grep audit_buffer_size

# Check disk I/O
iostat -x 1 10
```

**Solutions:**
1. Increase buffer size: `buffer.size: 10000`
2. Reduce flush interval: `buffer.flush_interval_seconds: 1`
3. Enable compression: `file.compression.enabled: true`
4. Check disk performance (SSD recommended)
5. Consider log rotation/cleanup

#### Issue 3: Degraded Mode

**Symptoms:**
- `audit_operational_mode` > 0
- Health check shows "degraded"
- Logs to stderr instead of file

**Diagnosis:**
```python
from src.logging.degradation_handler import DegradationHandler

handler = DegradationHandler()
health = handler.get_health_check()
print("Reasons:", health['degradation_reasons'])
```

**Solutions:**
1. **DISK_FULL:** Free disk space, enable archival
2. **PERMISSION_DENIED:** Fix directory permissions
3. **HIGH_ERROR_RATE:** Investigate underlying errors
4. **CIRCUIT_BREAKER_OPEN:** Wait for timeout, then attempt recovery

```python
# Force recovery attempt
handler.attempt_recovery()
```

#### Issue 4: Encryption Errors

**Symptoms:**
- "Encryption failed" errors
- `cryptography` module errors
- Cannot read encrypted logs

**Diagnosis:**
```bash
# Check if cryptography is installed
python3 -c "import cryptography; print(cryptography.__version__)"

# Check encryption key
echo $CORTEX_AUDIT_ENCRYPTION_KEY

# Test encryption
python3 -c "
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b'test')
print('Encryption working')
"
```

**Solutions:**
1. Install cryptography: `pip install cryptography`
2. Generate key: `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
3. Set environment variable: `export CORTEX_AUDIT_ENCRYPTION_KEY="<key>"`
4. Disable encryption temporarily (dev only): `security.encryption_enabled: false`

#### Issue 5: Feature Flags Not Updating

**Symptoms:**
- Configuration changes not applied
- Features remain disabled/enabled

**Diagnosis:**
```python
from src.logging.feature_flags import get_feature_flags

flags = get_feature_flags()
print("Auto-reload:", flags.auto_reload)
print("Enabled features:", flags.get_enabled_features())
```

**Solutions:**
1. Enable auto-reload: `flags.start_auto_reload(interval=30)`
2. Manual reload: `flags.reload_config()`
3. Check config file permissions
4. Verify YAML syntax

---

## Performance Tuning

### Optimization Guidelines

| Workload | Buffer Size | Flush Interval | Batch Size | Compression |
|----------|-------------|----------------|------------|-------------|
| **Low** (<100 logs/min) | 1,000 | 5s | 50 | Level 6 |
| **Medium** (100-1,000 logs/min) | 5,000 | 3s | 100 | Level 6 |
| **High** (1,000-10,000 logs/min) | 10,000 | 1s | 200 | Level 9 |
| **Very High** (>10,000 logs/min) | 20,000 | 500ms | 500 | Disabled |

### Configuration Examples

**Low Latency (< 5ms P95):**
```yaml
buffer:
  size: 10000
  flush_interval_seconds: 1

performance:
  async_writes: true
  batch_size: 200
  max_latency_ms: 5

file:
  compression:
    enabled: false  # Trade space for speed
```

**High Throughput (>10,000 logs/sec):**
```yaml
buffer:
  size: 20000
  flush_interval_seconds: 0.5

performance:
  async_writes: true
  batch_size: 500
  adaptive_batching: true

file:
  compression:
    enabled: true
    algorithm: "gzip"
    level: 6  # Lower level for speed
```

**Balanced:**
```yaml
buffer:
  size: 10000
  flush_interval_seconds: 1

performance:
  async_writes: true
  batch_size: 200
  max_latency_ms: 10

file:
  compression:
    enabled: true
    algorithm: "gzip"
    level: 9  # Higher compression
```

### Benchmarking

```bash
# Run performance tests
python3 -m pytest tests/logging/performance/ -v

# Load test
python3 -m pytest tests/load/ --load-test --count=10000

# Monitor during test
watch -n 1 'curl -s http://localhost:9090/metrics | grep audit_write_latency'
```

---

## Disaster Recovery

### Backup Strategy

**Automated Backups:**
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR=/backup/cortex/audit
DATE=$(date +%Y%m%d)

# Backup logs
tar -czf $BACKUP_DIR/logs-$DATE.tar.gz /var/log/cortex/audit/

# Backup config
cp /etc/cortex/audit-logging.yaml $BACKUP_DIR/config-$DATE.yaml

# Retention (30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

**Add to crontab:**
```bash
0 2 * * * /usr/local/bin/backup-audit-logs.sh
```

### Recovery Procedures

**Restore Logs:**
```bash
# Stop service
sudo systemctl stop cortex

# Restore from backup
tar -xzf /backup/cortex/audit/logs-20260105.tar.gz -C /

# Fix permissions
sudo chown -R cortex:cortex /var/log/cortex/audit/

# Start service
sudo systemctl start cortex
```

**Restore Configuration:**
```bash
sudo cp /backup/cortex/audit/config-20260105.yaml /etc/cortex/audit-logging.yaml
sudo systemctl restart cortex
```

### Data Corruption Recovery

```bash
# Check file integrity
python3 <<EOF
from src.logging.security.integrity_checker import IntegrityChecker

checker = IntegrityChecker()
corrupted = checker.verify_directory('/var/log/cortex/audit/')

if corrupted:
    print(f"Corrupted files: {corrupted}")
    # Restore from backup
EOF
```

---

## Maintenance

### Log Rotation

**Manual Rotation:**
```bash
# Rotate logs
python3 -c "
from src.logging.audit_logger import AuditLogger
logger = AuditLogger.get_instance()
logger.rotate_logs()
"
```

**Automated Rotation (logrotate):**
```bash
# /etc/logrotate.d/cortex-audit
/var/log/cortex/audit/*/*.jsonl {
    daily
    rotate 90
    compress
    delaycompress
    notifempty
    create 0600 cortex cortex
    postrotate
        killall -HUP cortex
    endscript
}
```

### Archival

```bash
# Archive old logs to S3
aws s3 sync /var/log/cortex/audit/archives/ s3://cortex-audit-archives/ \
  --storage-class GLACIER \
  --exclude "*" --include "*.gz"

# Delete after upload
find /var/log/cortex/audit/archives/ -name "*.gz" -mtime +90 -delete
```

### Cleanup

```bash
# Run cleanup script
./scripts/cleanup_audit_logs.sh --older-than 30

# Or use configuration
# cleanup.retention_days: 30
```

### Health Checks (Scheduled)

```bash
# Add to crontab (every 5 minutes)
*/5 * * * * /usr/local/bin/check-audit-health.sh

# /usr/local/bin/check-audit-health.sh
#!/bin/bash
HEALTH=$(python3 -c "
from src.logging.degradation_handler import DegradationHandler
h = DegradationHandler()
print(h.get_health_check()['status'])
")

if [ "$HEALTH" != "healthy" ]; then
    echo "Audit logger unhealthy: $HEALTH" | mail -s "Alert" ops@example.com
fi
```

---

## Runbook

### Daily Operations

- [ ] Check health dashboard (Grafana)
- [ ] Review error rate alerts
- [ ] Verify disk space (>10% free)
- [ ] Check P95 latency (<10ms)

### Weekly Operations

- [ ] Review self-healing success rate (>95%)
- [ ] Check log rotation functioning
- [ ] Verify backup completion
- [ ] Review degradation events

### Monthly Operations

- [ ] Rotate encryption keys (if enabled)
- [ ] Review and update alert thresholds
- [ ] Performance tuning review
- [ ] Capacity planning (disk, memory)

---

**Version:** 1.0.0  
**Support:** Contact DevOps team  
**Emergency:** See disaster recovery section
