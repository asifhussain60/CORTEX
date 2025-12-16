# Phase 9 Production Deployment - Complete Guide

**Project:** PaymentProcessor Transaction Invoices Modernization  
**Phase:** 9 - Production Gradual Rollout  
**Status:** 🟢 **READY FOR EXECUTION**  
**Date:** December 12, 2025  
**Author:** Asif Hussain  

---

## 🎯 Executive Summary

Phase 9 delivers complete production deployment infrastructure for zero-downtime migration:

✅ **Azure Infrastructure as Code** (Bicep templates)  
✅ **Automated Deployment Scripts** (PowerShell + Azure CLI)  
✅ **CI/CD Pipeline** (Azure DevOps multi-stage)  
✅ **Gradual Rollout Automation** (0% → 100% orchestration)  
✅ **Emergency Rollback Capability** (<30 second response)  
✅ **Real-Time Monitoring** (Application Insights + Kusto queries)  

---

## 📦 Deliverables

### Infrastructure as Code
| File | Purpose | Lines |
|------|---------|-------|
| `deploy-azure-resources.bicep` | Azure resources (App Config, App Insights, Key Vault) | 250 |
| `parameters.dev.json` | Dev environment configuration | 25 |
| `parameters.staging.json` | Staging environment configuration | 25 |
| `parameters.prod.json` | Production environment configuration | 27 |

### Deployment Scripts
| File | Purpose | Lines |
|------|---------|-------|
| `deploy.ps1` | Azure resource deployment automation | 150 |
| `gradual-rollout.ps1` | Traffic percentage orchestration with monitoring | 280 |
| `emergency-rollback.ps1` | Instant rollback to 0% (Mock only) | 95 |

### CI/CD Pipeline
| File | Purpose | Lines |
|------|---------|-------|
| `azure-pipelines.yml` | Multi-stage pipeline (Build → Test → Deploy) | 280 |

### Monitoring & Documentation
| File | Purpose | Lines |
|------|---------|-------|
| `kusto-queries.md` | 40+ pre-built Application Insights queries | 520 |
| `README.md` (deploy/azure/) | Deployment guide and troubleshooting | 350 |

**Total:** 9 files, 2,002 lines of deployment automation

---

## 🚀 Deployment Workflow

### Step 1: Azure Resource Provisioning

#### Dev Environment
```powershell
cd deploy/azure
.\deploy.ps1 -Environment dev
```

**Creates:**
- Azure App Configuration: `ra-transaction-invoices-config-dev`
- Application Insights: `ra-transaction-invoices-insights-dev`
- Azure Key Vault: `ra-transaction-invoices-kv-dev`
- Encryption Key: `ra-transaction-encryption-key` (2048-bit RSA)

**Duration:** ~5 minutes

#### Staging Environment
```powershell
.\deploy.ps1 -Environment staging
```

#### Production Environment
```powershell
.\deploy.ps1 -Environment prod
```

**Note:** Production includes purge protection and soft delete (7-day retention).

---

### Step 2: CI/CD Pipeline Setup

#### Create Service Connections (Azure DevOps)
1. Navigate to Project Settings → Service connections
2. Create 3 Azure Resource Manager connections:
   - `Azure-ServiceConnection-Dev`
   - `Azure-ServiceConnection-Staging`
   - `Azure-ServiceConnection-Production`
3. Grant Contributor access to respective subscriptions

#### Create Environments (Azure DevOps)
1. Navigate to Pipelines → Environments
2. Create 3 environments:
   - `PaymentProcessor-TransactionInvoices-Dev` (no approval)
   - `PaymentProcessor-TransactionInvoices-Staging` (optional approval)
   - `PaymentProcessor-TransactionInvoices-Production` (required approval + security checks)

#### Configure Pipeline
1. Navigate to Pipelines → New pipeline
2. Select Azure Repos Git
3. Choose `cortex/ra-modernized/deploy/azure-pipelines.yml`
4. Save and run

**Pipeline Stages:**
1. **Build & Test** - Restore, build, unit tests (61), integration tests (69)
2. **Deploy Dev** - Auto-deploy on `develop` branch commits
3. **Deploy Staging** - Auto-deploy after Dev success
4. **Deploy Production** - Manual approval required, blue-green deployment

---

### Step 3: Gradual Rollout (5-Week Plan)

#### Week 1: 0% → 10%
```powershell
.\gradual-rollout.ps1 `
    -Environment prod `
    -TargetPercentage 10 `
    -MonitoringDurationMinutes 30 `
    -AutoRollbackOnFailure
```

**Monitoring:**
- 30-minute continuous monitoring
- Checks every 60 seconds
- Auto-rollback if:
  - Error rate > 0.1%
  - Latency > 200ms
  - Success rate < 99.9%

**Expected Traffic:**
- 10% of requests routed to EF Core
- 90% routed to Mock (safe fallback)
- Deterministic routing (same user always same layer)

#### Week 2: 10% → 25%
```powershell
.\gradual-rollout.ps1 -Environment prod -TargetPercentage 25 -AutoRollbackOnFailure
```

#### Week 3: 25% → 50%
```powershell
.\gradual-rollout.ps1 -Environment prod -TargetPercentage 50 -AutoRollbackOnFailure
```

**Milestone:** Majority validation point (50/50 split)

#### Week 4: 50% → 75%
```powershell
.\gradual-rollout.ps1 -Environment prod -TargetPercentage 75 -AutoRollbackOnFailure
```

#### Week 5: 75% → 100%
```powershell
.\gradual-rollout.ps1 -Environment prod -TargetPercentage 100 -AutoRollbackOnFailure
```

**Milestone:** Full migration complete! 🎉

---

### Step 4: Emergency Rollback (If Needed)

#### Instant Rollback to Mock
```powershell
.\emergency-rollback.ps1 `
    -Environment prod `
    -Reason "High error rate detected (2.5%)"
```

**Effect:**
- Feature flag instantly set to 0%
- 100% traffic routed to Mock within 30 seconds
- Incident logged to `rollback-incidents.log`
- Critical alerts sent to PagerDuty

**Recovery Time Objective (RTO):** <30 seconds

---

## 📊 Monitoring Dashboard

### Application Insights Queries (Pre-Built)

**Real-Time Metrics (5-minute window):**
1. Current error rate
2. Current success rate
3. Current latency (Avg, P50, P95, P99)
4. Traffic distribution (Mock vs EF Core)

**Alerts:**
- Error rate > 0.1%
- Latency > 200ms
- Success rate < 99.9%

**Diagnostic Queries:**
- Top 10 errors
- Slow requests (>500ms)
- Failed operations
- Exception stack traces

**Location:** `deploy/azure/kusto-queries.md` (40+ queries)

### Create Application Insights Workbook

1. Navigate to Application Insights → Workbooks
2. Click "New"
3. Add query visualizations from `kusto-queries.md`:
   - Success Rate Trend (last 24 hours)
   - Traffic Distribution (Mock vs EF Core)
   - Latency P95 Trend
   - Error Count by Operation
4. Save as "PaymentProcessor Transaction Invoices - Production Dashboard"

---

## ✅ Production Readiness Checklist

### Infrastructure
- [ ] Azure resources deployed (App Config, App Insights, Key Vault)
- [ ] Key Vault access granted to API managed identity
- [ ] Encryption key created and accessible
- [ ] Connection strings stored in Key Vault
- [ ] Feature flag configured (DataLayerRollout, 0% initial)

### Application
- [ ] API deployed to all environments (Dev, Staging, Prod)
- [ ] Health endpoints responding (200 OK)
- [ ] Application Insights telemetry flowing
- [ ] Logs appearing in Log Analytics workspace
- [ ] Error tracking operational

### Testing
- [ ] 130 automated tests passing (100% pass rate)
- [ ] Schema validation tests passing (38/38)
- [ ] Phase 6 infrastructure tests passing (45/45)
- [ ] Integration tests passing in production (smoke tests)

### Monitoring
- [ ] Application Insights queries tested
- [ ] Dashboards created and accessible
- [ ] Alert rules configured (error rate, latency, success rate)
- [ ] PagerDuty integration configured
- [ ] On-call rotation established

### Runbooks
- [ ] Deployment runbook reviewed
- [ ] Rollback procedure documented
- [ ] Incident response plan reviewed
- [ ] Stakeholder communication plan ready

### Security & Compliance
- [ ] GDPR compliance verified (PII encryption, audit logging)
- [ ] ISO27001 controls validated
- [ ] Key rotation procedures documented
- [ ] Access control reviewed (RBAC)

### Sign-Off
- [ ] Technical lead approval
- [ ] Product owner approval
- [ ] Security team approval
- [ ] Operations team approval

---

## 🚨 Incident Response

### Scenario 1: High Error Rate (>0.1%)

**Detection:**
- Automated monitoring detects threshold violation
- Auto-rollback triggered (if enabled)
- PagerDuty alert sent

**Response:**
1. Review Application Insights exception traces
2. Identify root cause (query: Top 10 Errors)
3. If auto-rollback not enabled, execute manual rollback
4. Fix underlying issue in non-production environment
5. Re-deploy after validation

### Scenario 2: High Latency (>200ms)

**Detection:**
- P95 latency exceeds 200ms threshold
- Alert triggered

**Response:**
1. Review slow requests query (>500ms)
2. Check database connection pool metrics
3. Identify slow operations
4. If widespread, trigger rollback
5. Optimize slow queries or increase resources

### Scenario 3: Low Success Rate (<99.9%)

**Detection:**
- Success rate drops below 99.9%
- Alert triggered

**Response:**
1. Review failed requests by operation
2. Check dependency failures (database, external APIs)
3. Assess impact scope (specific operations vs all)
4. Trigger rollback if critical
5. Implement fixes and re-deploy

---

## 📈 Success Metrics

### Technical Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment Success Rate | 100% | All environments |
| Automated Test Pass Rate | 100% | 130 tests |
| Code Coverage | >95% | All production code |
| Zero-Downtime Deployment | 100% | Blue-green swaps |
| Rollback Time (RTO) | <30 seconds | Feature flag update |

### Business Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Production Error Rate | <0.1% | Last 24 hours |
| API Latency (P95) | <200ms | Last 24 hours |
| Success Rate | >99.9% | Last 24 hours |
| Uptime | >99.95% | Monthly |

### Migration Progress
| Week | Target % | Mock % | EF Core % | Status |
|------|----------|--------|-----------|--------|
| Baseline | 0% | 100% | 0% | ✅ Complete |
| Week 1 | 10% | 90% | 10% | 🟡 Pending |
| Week 2 | 25% | 75% | 25% | 🔵 Not Started |
| Week 3 | 50% | 50% | 50% | 🔵 Not Started |
| Week 4 | 75% | 25% | 75% | 🔵 Not Started |
| Week 5 | 100% | 0% | 100% | 🔵 Not Started |

---

## 🏆 Phase 9 Completion Criteria

### Infrastructure (100% Complete)
- [x] Bicep templates created (4 files)
- [x] Deployment scripts created (3 PowerShell scripts)
- [x] CI/CD pipeline configured (Azure DevOps YAML)
- [x] Monitoring queries created (40+ Kusto queries)

### Documentation (100% Complete)
- [x] Deployment guide (README.md)
- [x] Gradual rollout plan (this document)
- [x] Troubleshooting guide
- [x] Kusto query reference

### Automation (100% Complete)
- [x] Automated resource provisioning
- [x] Automated rollout orchestration
- [x] Automated rollback capability
- [x] Automated health checks

### Pending Execution
- [ ] Deploy to Dev environment
- [ ] Deploy to Staging environment
- [ ] Deploy to Production environment
- [ ] Execute Week 1 rollout (0% → 10%)
- [ ] Execute Week 2 rollout (10% → 25%)
- [ ] Execute Week 3 rollout (25% → 50%)
- [ ] Execute Week 4 rollout (50% → 75%)
- [ ] Execute Week 5 rollout (75% → 100%)
- [ ] Post-migration validation
- [ ] Decommission Mock data layer

---

## 📚 Related Documentation

- [Azure Resource Deployment Guide](README.md)
- [Kusto Query Reference](kusto-queries.md)
- [Phase 7a Automated Testing](../docs/phase-7a-automated-testing-completion-report.md)
- [Phase 6 Feature Flags](../docs/phase-6-feature-flags-completion-report.md)
- [Phase 8 Encryption](../docs/encryption-guide.md)

---

## 📞 Support Contacts

### On-Call Rotation
- **Primary:** Platform Engineering Team
- **Secondary:** DevOps Team
- **Escalation:** Engineering Leadership

### PagerDuty
- **Service:** PaymentProcessor Transaction Invoices Production
- **Escalation Policy:** Platform Engineering → DevOps → Leadership

### Incident Response
- **Slack Channel:** `#ra-transaction-invoices-prod`
- **Email:** platform-engineering@company.com

---

## 🎉 Migration Completion

Upon successful completion of all 5 weeks:

1. **Validate Metrics:**
   - Error rate <0.1% for 7 consecutive days
   - Latency <200ms for 7 consecutive days
   - Success rate >99.9% for 7 consecutive days

2. **Archive Mock Layer:**
   - Comment out Mock repository registrations
   - Keep code for historical reference
   - Update documentation

3. **Generate Completion Report:**
   - Executive summary
   - Migration timeline
   - Metrics and KPIs achieved
   - Lessons learned

4. **Celebrate! 🎉**
   - Team recognition
   - Retrospective meeting
   - Knowledge sharing session

---

**Phase 9 Status:** ✅ **INFPaymentProcessorSTRUCTURE COMPLETE - READY FOR GPaymentProcessorDUAL ROLLOUT**  
**Next Action:** Deploy to Dev environment and begin Week 1 rollout  
**Updated:** December 12, 2025  
**Author:** Asif Hussain | GitHub: github.com/asifhussain60/CORTEX
