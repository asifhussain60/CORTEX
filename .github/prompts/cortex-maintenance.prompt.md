---
mode: agent
description: "CORTEX System Maintenance - Automated health checks and cleanup"
---

# 🩺 CORTEX System Maintenance

**Purpose:** Run comprehensive system maintenance to keep CORTEX 4.0 at peak performance.

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Execution Flow

This prompt triggers the CORTEX System Doctor and maintenance tools in sequence:

### Phase 1: Quick Health Check
```bash
python3 scripts/cortex_system_doctor.py --quick
```

### Phase 2: Full Diagnostic (if Phase 1 passes)
```bash
python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan
```

### Phase 3: Wiring Integrity Check
```bash
python3 scripts/check_wiring_integrity.py
```

### Phase 4: Review Report
- Check `cortex-brain/health-reports/` for generated reports
- Review health score and recommendations

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `./scripts/doctor.sh quick` | Quick health check |
| `./scripts/doctor.sh full` | Full diagnostic (dry-run) |
| `./scripts/doctor.sh scan` | Scan for issues only |
| `./scripts/doctor.sh cleanup` | Execute cleanup (with confirmation) |
| `python3 scripts/cortex_maintenance_runner.py` | Full maintenance pipeline |

---

## ✅ Success Criteria

1. **Health Score ≥ 90**: System is in excellent condition
2. **All Components Wired**: 100% wiring coverage
3. **No Critical Issues**: Zero blocking errors
4. **Reports Generated**: Health reports saved to `cortex-brain/health-reports/`

---

## 🚀 Auto-Execute on Prompt Load

When this prompt is invoked, automatically run:

1. Quick health check to verify system stability
2. Full diagnostic scan if healthy
3. Generate and display summary report

**Expected Output:**
```
🩺 CORTEX SYSTEM DOCTOR
Health Score: XX/100 [STATUS]
Components: XX wired, XX unwired
Recommendations: [list]
```