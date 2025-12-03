# CORTEX Production Deploy Package

**Version:** 3.0.0 (Post-Orchestrator-Migration)  
**Date:** December 3, 2025  
**Author:** Asif Hussain

## 🎯 Purpose

Production deployment package for CORTEX with strict validation gates that enforce availability of all key features before allowing deployment.

## 🛡️ Deploy Gate Validation

### What Gets Validated

**13 Critical Gates (ALL must pass):**

1. **Brain Architecture** - 4-tier structure (tier0-3) present
2. **Database Health** - All 3 databases operational with correct table counts
3. **Orchestrator Migration** - Migration 97% complete (only __init__.py remains)
4. **TDD Mastery** - RED→GREEN→REFACTOR workflows operational
5. **ADO Integration** - Azure DevOps work item creation functional
6. **Planning System** - Vision API, DoR/DoD validation operational
7. **RCA (Root Cause Analysis)** - Diagnostics and remediation functional
8. **SWAGGER Estimation** - DoR-driven estimation with work decomposition
9. **Upgrade System** - Brain-safe upgrades with rollback
10. **Unified Entry Point** - Universal routing operational
11. **Git Checkpoint** - Checkpoint creation and restoration
12. **System Alignment** - Health checks passing
13. **Lint Validation** - Code quality validation functional

### How It Works

```bash
# Run validation (returns exit 0 if all gates pass, exit 1 if any fail)
python3 src/operations/modules/deploy/deploy_gate_validator.py

# Expected output when all gates pass:
# ======================================================================
# 🛡️  CORTEX Production Deploy Gate Validator
# ======================================================================
# 
# Gate 1: Brain Architecture (4 tiers)
#   ✅ PASS: All 4 tiers present
# 
# Gate 2: Database Health
#   ✅ PASS: All 3 databases healthy
# 
# Gate 3: Orchestrator Migration Complete
#   ✅ PASS: Migration complete: Only __init__.py remains (97% reduction achieved)
# 
# Gate 4: TDD Mastery
#   Description: RED→GREEN→REFACTOR workflow with auto-debug
#   ✅ PASS: All 3 functions available
# 
# [... all other gates ...]
# 
# ======================================================================
# 📊 Validation Summary
# ======================================================================
# 
# Total Gates:  13
# Passed:       13 ✅
# Failed:       0 ❌
# Success Rate: 100.0%
# Execution:    0.45s
# 
# 🎉 ALL GATES PASSED - PRODUCTION DEPLOYMENT APPROVED!
```

### Integration with CI/CD

**GitHub Actions Example:**

```yaml
name: CORTEX Production Deploy

on:
  push:
    branches: [main, production]

jobs:
  validate-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run Deploy Gate Validation
        run: python3 src/operations/modules/deploy/deploy_gate_validator.py
      
      - name: Deploy to Production
        if: success()
        run: ./scripts/deploy_production.sh
```

**Exit Codes:**
- `0` = All gates passed, deployment APPROVED
- `1` = One or more gates failed, deployment BLOCKED

## 📦 Deploy Package Contents

### Core Components

```
CORTEX/
├── src/
│   ├── operations/
│   │   └── modules/
│   │       ├── tdd/              # TDD Mastery (18,618 lines)
│   │       ├── ado/              # ADO Integration (32,907 lines)
│   │       ├── planning/         # Planning System (3 utilities)
│   │       ├── rca/              # Root Cause Analysis (24,155 lines)
│   │       ├── estimation/       # SWAGGER Estimation
│   │       ├── upgrade/          # Upgrade System
│   │       ├── routing/          # Unified Entry Point
│   │       ├── git/              # Git Checkpoint
│   │       ├── lint/             # Lint Validation
│   │       └── deploy/           # Deploy Gate Validator (NEW)
│   ├── tier0/                    # Governance rules
│   ├── tier1/                    # Working memory
│   ├── tier2/                    # Knowledge graph
│   └── tier3/                    # Development context
├── cortex-brain/
│   ├── brain-protection-rules.yaml
│   ├── response-templates.yaml
│   ├── tier1-working-memory.db
│   ├── tier2-knowledge-graph.db (if exists)
│   └── tier3-development-context.db (if exists)
├── requirements.txt
├── VERSION
└── cortex.config.json
```

### Configuration Requirements

**cortex.config.json:**
```json
{
  "machines": {
    "PRODUCTION-SERVER": {
      "rootPath": "/path/to/CORTEX",
      "brainPath": "/path/to/CORTEX/cortex-brain"
    }
  },
  "production": {
    "environment": "production",
    "validation_required": true,
    "min_gates_passed": 13
  }
}
```

## 🚀 Deployment Process

### Pre-Deployment Checklist

- [ ] All code committed to `main` or `production` branch
- [ ] VERSION file updated to production version (e.g., `3.0.0`)
- [ ] cortex.config.json configured for production environment
- [ ] All databases backed up
- [ ] Deploy gate validator tested locally

### Step-by-Step Deployment

**1. Run Local Validation:**
```bash
# From CORTEX root
python3 src/operations/modules/deploy/deploy_gate_validator.py

# Verify all 13 gates pass
# Exit code 0 = APPROVED
```

**2. Create Deploy Package:**
```bash
# Create production package (exclude development files)
tar -czf cortex-3.0-production.tar.gz \
  --exclude='.git' \
  --exclude='tests/' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='logs/' \
  --exclude='cortex-brain/backups/' \
  --exclude='cortex-brain/cache/' \
  src/ \
  cortex-brain/ \
  requirements.txt \
  VERSION \
  cortex.config.template.json \
  README.md \
  LICENSE
```

**3. Transfer to Production:**
```bash
# SCP to production server
scp cortex-3.0-production.tar.gz user@production-server:/opt/cortex/

# SSH and extract
ssh user@production-server
cd /opt/cortex
tar -xzf cortex-3.0-production.tar.gz
```

**4. Production Configuration:**
```bash
# Configure for production environment
cd /opt/cortex
cp cortex.config.template.json cortex.config.json

# Edit cortex.config.json with production paths
nano cortex.config.json
```

**5. Install Dependencies:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import src; print('✅ CORTEX imports successful')"
```

**6. Run Production Validation:**
```bash
# CRITICAL: Run deploy gate validator on production server
python3 src/operations/modules/deploy/deploy_gate_validator.py

# Must see: "🎉 ALL GATES PASSED - PRODUCTION DEPLOYMENT APPROVED!"
# If any gates fail, DO NOT PROCEED - troubleshoot failed gates
```

**7. Initialize CORTEX:**
```bash
# Run system alignment check
python3 -m src.operations.align

# Expected: 8/8 HEALTHY checks passing
```

**8. Production Smoke Tests:**
```bash
# Test critical operations
python3 -c "from src.operations.modules.tdd.tdd_utility import execute_red_phase; print('✅ TDD Mastery')"
python3 -c "from src.operations.modules.ado.ado_utility import create_user_story; print('✅ ADO Integration')"
python3 -c "from src.operations.modules.estimation.swagger_estimation_utility import validate_dor; print('✅ SWAGGER Estimation')"
```

## 🔒 Security Considerations

### Production Hardening

**1. File Permissions:**
```bash
# Restrict access to CORTEX directories
chmod 750 /opt/cortex
chmod 640 /opt/cortex/cortex.config.json
chmod 600 /opt/cortex/cortex-brain/*.db
```

**2. Environment Variables:**
```bash
# Set production environment
export CORTEX_ENV=production
export CORTEX_ROOT=/opt/cortex
export CORTEX_BRAIN=/opt/cortex/cortex-brain
```

**3. Database Backups:**
```bash
# Automated daily backups
0 2 * * * /opt/cortex/scripts/backup_brain_databases.sh
```

## 📊 Monitoring

### Production Health Checks

**Automated Monitoring:**
```bash
# Add to crontab for hourly health checks
0 * * * * cd /opt/cortex && python3 -m src.operations.align --quiet >> /var/log/cortex/health.log 2>&1
```

**Health Check Script:**
```bash
#!/bin/bash
# /opt/cortex/scripts/health_check.sh

cd /opt/cortex

# Run alignment check
python3 -m src.operations.align --quiet

if [ $? -eq 0 ]; then
    echo "$(date): ✅ HEALTHY" >> /var/log/cortex/health.log
else
    echo "$(date): ❌ UNHEALTHY - ALERT REQUIRED" >> /var/log/cortex/health.log
    # Send alert (email, Slack, PagerDuty, etc.)
fi
```

## 🆘 Rollback Procedure

If production deployment fails validation:

**1. Stop CORTEX Services:**
```bash
systemctl stop cortex  # If running as service
```

**2. Restore Previous Version:**
```bash
cd /opt/cortex
rm -rf src/ cortex-brain/
tar -xzf /opt/cortex/backups/cortex-previous-version.tar.gz
```

**3. Verify Rollback:**
```bash
python3 src/operations/modules/deploy/deploy_gate_validator.py
```

**4. Restart Services:**
```bash
systemctl start cortex
```

## 📝 Version History

### v3.0.0 (December 3, 2025)
- Orchestrator migration complete (97% reduction)
- All 29 orchestrators migrated to utilities
- Deploy gate validator created
- Production validation enforced
- Zero functional regressions

### Migration Achievements
- **30 orchestrators** → **1 orchestrator** (97% reduction)
- **~4,500 lines** net reduction
- **13 sprints** (November-December 2025)
- **8/8 HEALTHY** system alignment
- **100%** test coverage maintained
- **Zero** functional impact

## 🎓 Best Practices

### Before Each Deployment

1. ✅ Run deploy gate validator locally
2. ✅ Review VERSION file for correct version
3. ✅ Backup production databases
4. ✅ Test rollback procedure in staging
5. ✅ Document deployment in change log
6. ✅ Schedule deployment during low-traffic window

### After Each Deployment

1. ✅ Run deploy gate validator on production
2. ✅ Verify system alignment (8/8 HEALTHY)
3. ✅ Run production smoke tests
4. ✅ Monitor logs for 24 hours
5. ✅ Update production documentation
6. ✅ Notify team of successful deployment

## 📚 Additional Resources

- **Migration Documentation:** `cortex-brain/documents/reports/sprint-13b-completion-report.md`
- **Architecture Analysis:** `cortex-brain/documents/reports/ORCHESTRATOR-MIGRATION-COMPLETE-ANALYSIS.md`
- **System Alignment Guide:** `src/operations/align.py`
- **Feature Documentation:** `.github/prompts/CORTEX.prompt.md`

## 🤝 Support

For deployment issues:
1. Check deploy gate validator output
2. Review system alignment results
3. Verify all 13 gates pass
4. Consult migration documentation
5. Contact: Asif Hussain (github.com/asifhussain60)

---

**CORTEX 3.0 - Production Ready with Confidence** 🎉
