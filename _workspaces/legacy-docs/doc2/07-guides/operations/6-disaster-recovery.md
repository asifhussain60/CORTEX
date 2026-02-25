# Disaster Recovery

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Operations, SRE

## Overview

This document covers disaster recovery procedures for CORTEX, including backup strategies, recovery procedures, and business continuity planning.

## Recovery Objectives

| Metric | Target | Description |
|--------|--------|-------------|
| **RTO** | 4 hours | Recovery Time Objective |
| **RPO** | 1 hour | Recovery Point Objective |
| **MTTR** | 2 hours | Mean Time To Recovery |

## Backup Strategy

### What to Backup

| Component | Location | Frequency | Retention |
|-----------|----------|-----------|-----------|
| Governance DB | `cortex_brain/state/governance.db` | Hourly | 30 days |
| Tier 0 Rules | `cortex_brain/tier0/governance/` | On change | Forever |
| Configuration | `cortex-config.yaml` | On change | 90 days |
| Logs | `logs/` | Daily | 7 days |

### Backup Commands

```powershell
# Backup governance database
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item cortex_brain/state/governance.db "backups/governance-$timestamp.db"

# Backup tier rules
Compress-Archive -Path cortex_brain/tier0 -DestinationPath "backups/tier0-$timestamp.zip"

# Verify backup integrity
python -c "
import sqlite3
conn = sqlite3.connect('backups/governance-$timestamp.db')
tables = conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()
print(f'Backup valid: {len(tables)} tables')
"
```

### Automated Backup Script

```powershell
# backup.ps1
param(
    [string]$BackupDir = "backups",
    [int]$RetentionDays = 30
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Create backup directory
New-Item -ItemType Directory -Force -Path $BackupDir

# Backup database
Copy-Item cortex_brain/state/governance.db "$BackupDir/governance-$timestamp.db"

# Backup configuration
Copy-Item cortex-config.yaml "$BackupDir/config-$timestamp.yaml"

# Clean old backups
Get-ChildItem $BackupDir -Recurse | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
    Remove-Item -Force

Write-Host "Backup complete: $timestamp"
```

## Recovery Procedures

### Scenario 1: Database Corruption

**Symptoms:**
- `sqlite3.DatabaseError: database disk image is malformed`
- Governance queries fail

**Recovery:**

```powershell
# 1. Stop all services
Get-Process python | Stop-Process -Force

# 2. Find latest good backup
$latestBackup = Get-ChildItem backups/governance-*.db | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

# 3. Restore database
Copy-Item $latestBackup.FullName cortex_brain/state/governance.db -Force

# 4. Verify integrity
python -c "
import sqlite3
conn = sqlite3.connect('cortex_brain/state/governance.db')
conn.execute('PRAGMA integrity_check')
print('Integrity check passed')
"

# 5. Restart services
python -m cortex.mcp.server
```

### Scenario 2: Complete System Loss

**Recovery:**

```powershell
# 1. Provision new infrastructure
# (Use IaC - Terraform/Ansible)

# 2. Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 3. Restore configuration
Copy-Item backups/config-latest.yaml cortex-config.yaml

# 4. Restore database
Copy-Item backups/governance-latest.db cortex_brain/state/governance.db

# 5. Install dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 6. Verify system
pytest tests/e2e/smoke/ -v

# 7. Start services
python -m cortex.mcp.server
```

### Scenario 3: Tier 0 Rules Corruption

**Recovery:**

```powershell
# 1. Stop services
Get-Process python | Stop-Process -Force

# 2. Restore from backup
Expand-Archive -Path backups/tier0-latest.zip -DestinationPath cortex_brain/tier0 -Force

# 3. Verify rules load
python -c "
from cortex_brain.tier0.governance import load_rules
rules = load_rules()
print(f'Loaded {len(rules)} rules')
"

# 4. Restart services
python -m cortex.mcp.server
```

## Business Continuity

### Failover Strategy

```
┌─────────────┐         ┌─────────────┐
│   Primary   │────────▶│  Secondary  │
│   Region    │ Failover│   Region    │
└─────────────┘         └─────────────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│   DB Sync   │◀───────▶│   DB Sync   │
│   (Hourly)  │         │   (Hourly)  │
└─────────────┘         └─────────────┘
```

### Failover Trigger

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Health check fails | 5 consecutive | Alert |
| Health check fails | 10 consecutive | Auto-failover |
| Manual trigger | N/A | Immediate failover |

### Failover Procedure

```powershell
# 1. Verify primary is down
Test-Connection primary.cortex.local -Count 3

# 2. Promote secondary
# Update DNS/Load balancer to point to secondary

# 3. Verify secondary health
Invoke-WebRequest http://secondary.cortex.local/health

# 4. Notify stakeholders
Send-MailMessage -Subject "CORTEX Failover Executed" -Body "..."
```

## Recovery Testing

### Monthly DR Drill

| Step | Description | Duration |
|------|-------------|----------|
| 1 | Simulate primary failure | 5 min |
| 2 | Execute failover | 15 min |
| 3 | Verify secondary | 10 min |
| 4 | Restore primary | 30 min |
| 5 | Document results | 15 min |

### Recovery Validation Checklist

- [ ] Database restored successfully
- [ ] All tier rules loading
- [ ] MCP server responding
- [ ] Smoke tests passing
- [ ] Logs being written
- [ ] Metrics being scraped

## Related

- [Runbook](5-runbook.md)
- [Scaling Guide](7-scaling-guide.md)
- [Error Recovery Flow](../../_diagrams/error-recovery-flow.mmd)
