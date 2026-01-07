# CORTEX System Maintenance Tools

**Version:** 1.0.0 | **Author:** Asif Hussain | **Updated:** December 2025

---

## 🩺 Overview

This document describes the batch maintenance tools for keeping CORTEX 4.0 operating at peak performance. These tools chain existing scripts in optimal order to:

- **Diagnose** system health and detect issues
- **Scan** for duplicates, unnecessary files, and redundant folders
- **Cleanup** safe deletables with automatic backup
- **Validate** system integrity post-maintenance
- **Report** comprehensive health status

---

## 📦 Available Tools

### 1. System Doctor (`cortex_system_doctor.py`)

The primary diagnostic and maintenance tool. Runs comprehensive health checks.

```bash
# Quick health check
python3 scripts/cortex_system_doctor.py --quick

# Full diagnostic (dry-run - no changes)
python3 scripts/cortex_system_doctor.py

# Run specific phases
python3 scripts/cortex_system_doctor.py --phase diagnose
python3 scripts/cortex_system_doctor.py --phase scan
python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan

# Execute cleanup (makes changes)
python3 scripts/cortex_system_doctor.py --execute
```

**Phases:**
| Phase | Description |
|-------|-------------|
| `diagnose` | Analyze unwired components, entry points, manifests |
| `scan` | Detect duplicates, unnecessary files, redundant folders |
| `cleanup` | Remove safe deletions with backup |
| `validate` | Verify system integrity |
| `report` | Generate comprehensive health report |

---

### 2. Maintenance Runner (`cortex_maintenance_runner.py`)

Automated maintenance pipeline for scheduled runs.

```bash
# Full maintenance pipeline (dry-run)
python3 scripts/cortex_maintenance_runner.py

# Execute all stages
python3 scripts/cortex_maintenance_runner.py --execute

# Run specific stages
python3 scripts/cortex_maintenance_runner.py --stage preflight
python3 scripts/cortex_maintenance_runner.py --stage analysis

# Show cron schedule suggestions
python3 scripts/cortex_maintenance_runner.py --schedule
```

**Stages:**
| Stage | Description |
|-------|-------------|
| `preflight` | Quick health check (abort if critical issues) |
| `analysis` | Deep system analysis |
| `optimization` | Deduplicate and organize |
| `cleanup` | Remove unnecessary files |
| `validation` | Post-maintenance verification |
| `reporting` | Generate maintenance report |

---

### 3. Wiring Integrity Checker (`check_wiring_integrity.py`)

Ensures all components remain properly wired to the system.

```bash
# Check all components
python3 scripts/check_wiring_integrity.py

# Generate wiring suggestions
python3 scripts/check_wiring_integrity.py --fix

# Pre-commit hook mode (strict)
python3 scripts/check_wiring_integrity.py --pre-commit
```

---

### 4. Shell Helper (`doctor.sh`)

Quick command wrapper for common operations.

```bash
# Quick health check (default)
./scripts/doctor.sh quick

# Full diagnostic
./scripts/doctor.sh full

# Scan for issues
./scripts/doctor.sh scan

# Execute cleanup (with confirmation)
./scripts/doctor.sh cleanup

# Generate report
./scripts/doctor.sh report

# Show help
./scripts/doctor.sh help
```

---

## 📊 Output & Reports

All tools generate reports in `cortex-brain/health-reports/`:

- `doctor-report-YYYYMMDD_HHMMSS.md` - Markdown health report
- `doctor-report-YYYYMMDD_HHMMSS.json` - JSON data
- `maintenance-YYYYMMDD_HHMMSS.json` - Maintenance run results
- `wiring-report-YYYYMMDD_HHMMSS.json` - Wiring integrity data

---

## 🔄 Recommended Maintenance Schedule

### Daily (Quick Check)
```bash
python3 scripts/cortex_system_doctor.py --quick
```

### Weekly (Full Diagnostic)
```bash
python3 scripts/cortex_system_doctor.py
```

### Monthly (Execute Cleanup)
```bash
python3 scripts/cortex_system_doctor.py --execute
```

### Cron Examples
```bash
# Daily quick check at 6 AM
0 6 * * * cd /path/to/CORTEX && python3 scripts/cortex_system_doctor.py --quick >> logs/health.log 2>&1

# Weekly full scan on Sunday at 2 AM
0 2 * * 0 cd /path/to/CORTEX && python3 scripts/cortex_maintenance_runner.py >> logs/maintenance.log 2>&1
```

---

## 🔌 Component Scripts (Chained by Tools Above)

These scripts are chained by the batch tools:

| Script | Purpose |
|--------|---------|
| `analyze_unwired_components.py` | Find unwired orchestrators, agents, modules |
| `detect_duplicates.py` | Find duplicate content between files |
| `scan_unnecessary_files.py` | Find temporary/summary files |
| `cleanup_unnecessary_files.py` | Remove unnecessary files |
| `validate_entry_points.py` | Validate entry point modules exist |
| `validate_manifests.py` | Validate YAML manifests |
| `monitor_brain_health.py` | Check brain tier health |

---

## 🎯 Health Score Interpretation

| Score | Status | Meaning |
|-------|--------|---------|
| 90-100 | 🟢 EXCELLENT | System is healthy, no action needed |
| 70-89 | 🟡 GOOD | Minor issues, cleanup recommended |
| 50-69 | 🟠 FAIR | Several issues, maintenance required |
| 0-49 | 🔴 POOR | Critical issues, immediate attention |

---

## 🛡️ Safety Features

1. **Dry-Run by Default**: All tools preview changes without executing
2. **Automatic Backup**: Backups created before any cleanup
3. **Pre-Flight Checks**: Critical health verification before maintenance
4. **Recycle Bin Mode**: Deleted files recoverable from OS
5. **Protected Files**: Critical files never deleted

---

## 🚀 Quick Start

```bash
# 1. Quick health check
./scripts/doctor.sh quick

# 2. If healthy, run full scan
./scripts/doctor.sh scan

# 3. Review report in cortex-brain/health-reports/

# 4. If cleanup needed, execute (with backup)
./scripts/doctor.sh cleanup
```

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
