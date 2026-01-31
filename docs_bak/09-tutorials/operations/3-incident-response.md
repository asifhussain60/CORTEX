# Tutorial: Incident Response

**Time:** 30 minutes | **Level:** Advanced  
**Goal:** Handle production incidents effectively

## Overview

Production incidents require swift, systematic response. This tutorial covers incident response procedures, debugging, and recovery.

## Prerequisites

- [Monitoring Dashboard](2-monitoring-dashboard.md) completed
- Production experience

## Step 1: Incident Detection and Classification

```python
from enum import Enum
from datetime import datetime

class IncidentSeverity(Enum):
    P1_CRITICAL = "P1-Critical"
    P2_HIGH = "P2-High"
    P3_MEDIUM = "P3-Medium"
    P4_LOW = "P4-Low"

class Incident:
    def __init__(
        self,
        id: str,
        title: str,
        severity: IncidentSeverity,
        description: str
    ):
        self.id = id
        self.title = title
        self.severity = severity
        self.description = description
        self.created_at = datetime.utcnow()
        self.status = "open"
        self.logs = []
    
    def log_action(self, action: str):
        """Log incident action."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action
        })
        print(f"[{self.id}] {action}")

# Detection
def detect_incidents(metrics: dict) -> list:
    """Detect incidents from metrics."""
    incidents = []
    
    if metrics["api_error_rate"] > 50:
        incidents.append(Incident(
            id="INC-001",
            title="Critical API failures",
            severity=IncidentSeverity.P1_CRITICAL,
            description="API error rate exceeds 50%"
        ))
    
    if metrics["orchestrator_errors"] > 100:
        incidents.append(Incident(
            id="INC-002",
            title="High orchestrator error rate",
            severity=IncidentSeverity.P2_HIGH,
            description="Orchestrator errors exceed threshold"
        ))
    
    return incidents
```

## Step 2: Incident Runbooks

```python
class IncidentRunbook:
    """Runbook for specific incident types."""
    
    @staticmethod
    def api_failures():
        """Runbook for API failures."""
        return {
            "title": "API Failures",
            "steps": [
                "Check API server status",
                "Review recent deployments",
                "Check database connectivity",
                "Review error logs for patterns",
                "Restart API service if needed",
                "Monitor error rate for 5 minutes",
                "Escalate if not resolved"
            ],
            "commands": [
                "cortex api status",
                "cortex logs --service api --lines 100",
                "cortex db health-check",
                "cortex api restart"
            ]
        }
    
    @staticmethod
    def database_issues():
        """Runbook for database issues."""
        return {
            "title": "Database Issues",
            "steps": [
                "Check database connection status",
                "Check available disk space",
                "Review slow query logs",
                "Check for long-running transactions",
                "Consider query optimization",
                "Check backup status",
                "Restart if needed"
            ],
            "commands": [
                "cortex db status",
                "cortex db check-space",
                "cortex db slow-queries",
                "cortex db long-transactions"
            ]
        }
    
    @staticmethod
    def high_latency():
        """Runbook for high latency."""
        return {
            "title": "High Latency",
            "steps": [
                "Identify slow endpoints",
                "Check CPU and memory usage",
                "Review recent deployments",
                "Check orchestrator query times",
                "Scale up if needed",
                "Enable query caching",
                "Profile application"
            ],
            "commands": [
                "cortex metrics --endpoint latency",
                "cortex system resources",
                "cortex orchestrator profile",
                "cortex scale up --replicas 2"
            ]
        }
```

## Step 3: Incident Response Workflow

```python
class IncidentResponse:
    def __init__(self, incident: Incident):
        self.incident = incident
        self.runbook = self._get_runbook()
    
    def _get_runbook(self) -> dict:
        """Get runbook for incident type."""
        if "API" in self.incident.title:
            return IncidentRunbook.api_failures()
        elif "database" in self.incident.description.lower():
            return IncidentRunbook.database_issues()
        elif "latency" in self.incident.description.lower():
            return IncidentRunbook.high_latency()
        return {}
    
    def execute(self):
        """Execute incident response."""
        self.incident.log_action(f"Starting response: {self.runbook.get('title')}")
        
        steps = self.runbook.get("steps", [])
        for i, step in enumerate(steps, 1):
            self.incident.log_action(f"Step {i}: {step}")
        
        commands = self.runbook.get("commands", [])
        for cmd in commands:
            self.incident.log_action(f"Execute: {cmd}")
        
        self.incident.status = "investigating"
```

## Step 4: Logging and Diagnostics

```python
class DiagnosticCollector:
    @staticmethod
    def collect_diagnostics():
        """Collect diagnostic information."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": "45.2%",
                "memory_percent": "62.1%",
                "disk_percent": "78.5%"
            },
            "services": {
                "api": "running",
                "orchestrator": "running",
                "database": "running"
            },
            "recent_errors": [
                "ConnectionError: Database connection timeout",
                "TimeoutError: Orchestrator execution exceeded 30s"
            ],
            "active_requests": 45,
            "queued_requests": 12
        }
    
    @staticmethod
    def collect_logs(service: str, lines: int = 50):
        """Collect service logs."""
        return {
            "service": service,
            "lines": lines,
            "log_entries": [
                "2026-01-21 10:15:30 ERROR Connection pool exhausted",
                "2026-01-21 10:15:45 WARNING Slow query detected"
            ]
        }

# Usage
diagnostics = DiagnosticCollector.collect_diagnostics()
print("System Status:", diagnostics)
```

## Step 5: Post-Incident Review

```python
class PostIncidentReview:
    def __init__(self, incident: Incident):
        self.incident = incident
    
    def conduct_review(self) -> dict:
        """Conduct post-incident review."""
        return {
            "incident_id": self.incident.id,
            "title": self.incident.title,
            "severity": self.incident.severity.value,
            "duration_minutes": self._calculate_duration(),
            "root_cause": "Database connection pool misconfiguration",
            "resolution": "Increased connection pool size from 10 to 50",
            "prevention": [
                "Add monitoring for connection pool usage",
                "Implement auto-scaling for connections",
                "Update runbook with early warning signs"
            ],
            "action_items": [
                {
                    "item": "Update connection pool monitoring",
                    "owner": "DevOps",
                    "due_date": "2026-01-23"
                },
                {
                    "item": "Review capacity planning",
                    "owner": "Architecture",
                    "due_date": "2026-01-25"
                }
            ]
        }
    
    def _calculate_duration(self) -> int:
        """Calculate incident duration."""
        # Implementation
        return 45
```

## Incident Response Checklist

- [ ] Acknowledge incident
- [ ] Classify severity
- [ ] Get runbook
- [ ] Execute steps
- [ ] Monitor progress
- [ ] Communicate updates
- [ ] Resolve issue
- [ ] Document resolution
- [ ] Conduct post-review

## Communication Template

```
INCIDENT: [ID] - [Title]
SEVERITY: [P1-P4]
STATUS: [Open/Investigating/Resolved]
IMPACT: [Description of user impact]
ETA: [Estimated resolution time]
UPDATES: [Latest status]
```

## Next Steps

- [Performance Analysis](4-performance-analysis.md) - Optimize performance
- [Troubleshooting](../../04-guides/operations/4-troubleshooting.md) - Common issues
