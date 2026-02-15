# Tutorial: Monitoring Dashboard

**Time:** 30 minutes | **Level:** Intermediate  
**Goal:** Build monitoring dashboards for CORTEX

## Overview

Monitoring dashboards provide visibility into CORTEX health, performance, and user activity. This tutorial covers building effective dashboards.

## Prerequisites

- [Local Setup](1-local-setup.md) completed
- Grafana or similar dashboard tool (optional)
- Understanding of metrics and telemetry

## Step 1: Metrics Collection

```python
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "orchestrator_calls": 0,
            "orchestrator_errors": 0,
            "orchestrator_latency": [],
            "knowledge_queries": 0,
            "governance_checks": 0,
            "api_requests": 0,
            "api_errors": 0
        }
    
    def record_orchestrator_call(self, duration: float, success: bool):
        """Record orchestrator execution."""
        self.metrics["orchestrator_calls"] += 1
        if success:
            self.metrics["orchestrator_latency"].append(duration)
        else:
            self.metrics["orchestrator_errors"] += 1
    
    def record_knowledge_query(self):
        """Record knowledge query."""
        self.metrics["knowledge_queries"] += 1
    
    def record_governance_check(self):
        """Record governance check."""
        self.metrics["governance_checks"] += 1
    
    def record_api_request(self, success: bool):
        """Record API request."""
        self.metrics["api_requests"] += 1
        if not success:
            self.metrics["api_errors"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        latencies = self.metrics["orchestrator_latency"]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return {
            "orchestrator_calls": self.metrics["orchestrator_calls"],
            "orchestrator_success_rate": (
                (self.metrics["orchestrator_calls"] - self.metrics["orchestrator_errors"]) 
                / max(1, self.metrics["orchestrator_calls"]) * 100
            ),
            "avg_latency_ms": avg_latency * 1000,
            "knowledge_queries": self.metrics["knowledge_queries"],
            "governance_checks": self.metrics["governance_checks"],
            "api_error_rate": (
                self.metrics["api_errors"] / max(1, self.metrics["api_requests"]) * 100
            )
        }
```

## Step 2: Dashboard API

```python
from flask import Flask, jsonify

app = Flask(__name__)
collector = MetricsCollector()

@app.route("/metrics/summary")
def metrics_summary():
    """Get metrics summary."""
    return jsonify(collector.get_summary())

@app.route("/metrics/health")
def health():
    """Get system health status."""
    summary = collector.get_summary()
    
    health_status = "healthy"
    if summary["api_error_rate"] > 5:
        health_status = "degraded"
    if summary["api_error_rate"] > 20:
        health_status = "unhealthy"
    
    return jsonify({
        "status": health_status,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": summary
    })

@app.route("/metrics/orchestrators")
def orchestrator_metrics():
    """Get per-orchestrator metrics."""
    return jsonify({
        "hello_world": {
            "calls": 1234,
            "errors": 12,
            "avg_latency_ms": 45.3
        },
        "multi_step": {
            "calls": 567,
            "errors": 5,
            "avg_latency_ms": 234.1
        }
    })
```

## Step 3: HTML Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric {
            font-size: 32px;
            font-weight: bold;
            color: #0d6efd;
        }
        .label {
            color: #666;
            font-size: 14px;
            margin-top: 8px;
        }
        .status-healthy {
            color: green;
        }
        .status-degraded {
            color: orange;
        }
        .status-unhealthy {
            color: red;
        }
    </style>
</head>
<body>
    <h1>CORTEX Monitoring Dashboard</h1>
    
    <div class="dashboard">
        <div class="card">
            <h3>System Health</h3>
            <div class="metric" id="health-status">--</div>
            <div class="label">Last updated: <span id="last-update">--</span></div>
        </div>
        
        <div class="card">
            <h3>Orchestrator Calls</h3>
            <div class="metric" id="orchestrator-calls">--</div>
            <div class="label">Success rate: <span id="success-rate">--</span>%</div>
        </div>
        
        <div class="card">
            <h3>Average Latency</h3>
            <div class="metric" id="avg-latency">--</div>
            <div class="label">ms</div>
        </div>
        
        <div class="card">
            <h3>API Error Rate</h3>
            <div class="metric" id="error-rate">--</div>
            <div class="label">%</div>
        </div>
    </div>
    
    <script>
        async function updateMetrics() {
            const response = await fetch('/metrics/health');
            const data = await response.json();
            
            document.getElementById('health-status').textContent = data.status;
            document.getElementById('health-status').className = 'metric status-' + data.status;
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            document.getElementById('orchestrator-calls').textContent = data.metrics.orchestrator_calls;
            document.getElementById('success-rate').textContent = data.metrics.orchestrator_success_rate.toFixed(1);
            document.getElementById('avg-latency').textContent = data.metrics.avg_latency_ms.toFixed(1);
            document.getElementById('error-rate').textContent = data.metrics.api_error_rate.toFixed(1);
        }
        
        // Update every 5 seconds
        updateMetrics();
        setInterval(updateMetrics, 5000);
    </script>
</body>
</html>
```

## Step 4: Alerting

```python
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertManager:
    def __init__(self):
        self.alerts = []
    
    def check_health(self, summary: Dict[str, Any]):
        """Check metrics and create alerts."""
        if summary["api_error_rate"] > 20:
            self.create_alert(
                level=AlertLevel.CRITICAL,
                message=f"API error rate critical: {summary['api_error_rate']:.1f}%"
            )
        
        if summary["avg_latency_ms"] > 1000:
            self.create_alert(
                level=AlertLevel.WARNING,
                message=f"High latency detected: {summary['avg_latency_ms']:.1f}ms"
            )
    
    def create_alert(self, level: AlertLevel, message: str):
        """Create alert."""
        alert = {
            "level": level.value,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.alerts.append(alert)
        print(f"[{level.value.upper()}] {message}")
```

## Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| API Error Rate | > 5% | Check logs |
| API Error Rate | > 20% | Alert |
| Orchestrator Latency | > 1s | Investigate |
| Orchestrator Errors | > 2% | Review |
| Memory Usage | > 80% | Scale up |

## Next Steps

- [Incident Response](3-incident-response.md) - Handle incidents
- [Operations Guide](../../04-guides/operations/0-overview.md) - Full ops guide
