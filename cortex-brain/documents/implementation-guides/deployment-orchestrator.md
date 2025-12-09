# CORTEX Deployment Orchestrator - Complete Implementation Guide

**Version:** 3.0  
**Date:** December 9, 2025  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Deployment Workflow](#deployment-workflow)
3. [Components Reference](#components-reference)
4. [CLI Usage Guide](#cli-usage-guide)
5. [Deployment Strategies](#deployment-strategies)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Metrics & Monitoring](#metrics--monitoring)
8. [CI/CD Integration](#cicd-integration)
9. [Audit & Compliance](#audit--compliance)

---

## 🏗️ Architecture Overview

### State Machine Flow

```
IDLE → VALIDATING → BUILDING → DEPLOYING → VERIFYING → COMPLETE
                                     ↓
                              FAILED/ROLLED_BACK
```

### Component Hierarchy

```
DeploymentCLI (Entry Point)
    ├── DeployOrchestrator (Core Logic)
    │   ├── HolisticDiscovery (Component Scanning)
    │   ├── GateValidator (Pre-flight Checks)
    │   ├── DeploymentStrategyManager (Progressive Rollout)
    │   ├── DeploymentRollbackManager (Safety Net)
    │   ├── DeploymentMetricsCollector (Observability)
    │   └── State Machine (Checkpoint Management)
    └── Notification System (Event Broadcasting)
```

### File Structure

```
src/
├── deployment/
│   ├── deployment_cli.py (580 lines) - Unified CLI
│   ├── gate_validator.py (385 lines) - 19 validation gates
│   ├── deployment_rollback.py (650 lines) - Phase snapshots
│   ├── deployment_metrics.py (560 lines) - Health monitoring
│   ├── deployment_strategy.py (700 lines) - Canary/Blue-Green
│   └── holistic_discovery.py (350 lines) - Component scanner
├── orchestrators/
│   └── deploy_orchestrator.py (524 lines) - Core orchestrator
└── operations/
    └── deploy.py - Entry point integration

cortex-brain/
├── config/
│   └── deployment-strategies.yaml - Strategy configuration
├── orchestrator-manifests/
│   └── deploy-orchestrator-manifest.yaml (427 lines) - Deployment blueprint
├── deployments/
│   ├── strategies/ - Strategy execution states
│   └── rollback-points/ - Phase snapshots
├── metrics/deployments/ - Deployment analytics
└── audit/deployments/ - Immutable audit logs
```

---

## 🚀 Deployment Workflow

### Phase 1: PRE_FLIGHT (Validation)

**Duration:** ~30 seconds  
**Gates:** 19 critical validations

```bash
# Manual validation
python -m src.deployment.deployment_cli validate-gates

# Output:
✅ ALL GATES PASSED
Gates Passed: 19/19

Critical Gates:
  ✓ Git Repository Clean
  ✓ Test Coverage >80%
  ✓ No Broken Imports
  ✓ Brain Schema Compatible
  ✓ Dependencies Resolved
  ✓ No Security Vulnerabilities
```

**Gate Categories:**

1. **Critical (BLOCK deployment):**
   - git_clean, tests_passing, imports_valid
   - brain_schema_compatible, dependencies_resolved
   - security_scan_passed

2. **Warning (LOG only):**
   - documentation_updated, changelog_updated
   - test_coverage_acceptable

3. **Info (METRICS):**
   - code_complexity_acceptable, performance_benchmarks

**Holistic Discovery:**
- Scans: `src/orchestrators/`, `src/operations/modules/`, `src/cortex_agents/`, `src/dashboard/`
- Verifies: cortex-operations.yaml entry points, test files, documentation
- Generates: `cortex-brain/documents/reports/deployment-discovery-{timestamp}.md`

### Phase 2: BUILD (Package Creation)

**Duration:** ~60 seconds  
**Artifacts Generated:**

```
deploy-packages/
└── cortex-v3.0-{timestamp}/
    ├── src/ (complete source code)
    ├── cortex-brain/ (brain state snapshot)
    ├── requirements.txt
    ├── VERSION
    └── deployment-manifest.json
```

**Rollback Point Created:** `PRE_BUILD` snapshot (CODE + BRAIN + CONFIG)

### Phase 3: DEPLOY (Strategy Execution)

**Duration:** Variable (depends on strategy)

#### Direct Deployment (Low Risk)
```bash
python -m src.deployment.deployment_cli deploy --strategy direct
```
**Duration:** ~60 seconds  
**Process:** Single-step deployment with smoke tests

#### Canary Deployment (High Risk/Production)
```bash
python -m src.deployment.deployment_cli deploy --strategy canary
```
**Duration:** ~15 minutes (5 min per stage)  
**Process:**
1. Deploy to 10% → Smoke tests → Health monitoring (5 min)
2. Deploy to 50% → Smoke tests → Health monitoring (5 min)
3. Deploy to 100% → Smoke tests → Health monitoring (5 min)

**Auto-rollback triggers:**
- Smoke test failures
- Error rate >5%
- Success rate <95%
- Response time >500ms

#### Blue-Green Deployment (Zero-Downtime)
```bash
python -m src.deployment.deployment_cli deploy --strategy blue-green
```
**Duration:** ~7 minutes  
**Process:**
1. Deploy to Green environment (inactive)
2. Warm up Green (2 min) - cache priming, connection pooling
3. Run smoke tests on Green
4. Switch traffic Blue → Green (instant)
5. Monitor Green health (10 min)
6. Schedule Blue cleanup (24h later)

**Auto-rollback:** If Green health degrades after switch

### Phase 4: VERIFY (Post-Deployment)

**Duration:** ~30 seconds  
**Smoke Tests:**

```python
Critical Features:
✓ TDD Workflow (create test, run, validate)
✓ Planning System 2.0 (plan creation, phase execution)
✓ ADO Operations (story/feature/summary generation)
✓ Response Templates (62 templates rendering)
✓ Agent Instantiation (Brain Protector, Strategic Advisor)
✓ Database Queries (brain DB, conversation context, knowledge graph)
✓ API Endpoints (health checks, metrics)
```

**Auto-rollback:** If critical feature verification fails

**Verification Report:** `cortex-brain/documents/reports/deployment-verification-{timestamp}.md`

---

## 🛠️ Components Reference

### 1. Deploy Orchestrator
**File:** `src/orchestrators/deploy_orchestrator.py`  
**Purpose:** Core deployment workflow coordination

**Key Methods:**
```python
orchestrator = DeployOrchestrator(workspace_root)

# Full deployment
result = orchestrator.deploy(strategy='canary')

# Dry-run validation
validation = orchestrator.validate_deployment()

# Resume from checkpoint
result = orchestrator.resume_from_checkpoint(checkpoint_id)

# Get status
status = orchestrator.get_status()
```

### 2. Gate Validator
**File:** `src/deployment/gate_validator.py`  
**Purpose:** Pre-deployment validation with 19 gates

**Key Methods:**
```python
validator = GateValidator(workspace_root)

# Validate all gates
result = validator.validate_all_gates()

# Validate specific category
result = validator.validate_category('critical')

# Get gate report
report = validator.generate_gate_report()
```

### 3. Rollback Manager
**File:** `src/deployment/deployment_rollback.py`  
**Purpose:** Phase-level snapshots and rollback

**Key Methods:**
```python
rollback = DeploymentRollbackManager(workspace_root)

# Create snapshot
snapshot = rollback.create_snapshot(
    deployment_id='deploy-123',
    phase='BUILD'
)

# Rollback to latest
result = rollback.rollback_latest()

# Rollback to specific phase
result = rollback.rollback_to_phase('BUILD')

# List snapshots
snapshots = rollback.list_snapshots()
```

**Rollback Types:**
- `CODE_ONLY`: Git revert only
- `BRAIN_ONLY`: Brain state restore only
- `FULL`: Complete system rollback

### 4. Metrics Collector
**File:** `src/deployment/deployment_metrics.py`  
**Purpose:** Deployment analytics and health monitoring

**Key Methods:**
```python
metrics = DeploymentMetricsCollector(workspace_root)

# Record metric
metrics.record_metric(
    MetricType.DEPLOYMENT_DURATION,
    value=180.5,
    deployment_id='deploy-123'
)

# Get statistics
avg_duration = metrics.get_average_duration(days=7)
success_rate = metrics.get_success_rate(days=7)

# Generate report
report = metrics.generate_report(days=7)

# Health score (0-100)
score = metrics.calculate_health_score(days=7)

# Check alerts
alerts = metrics.check_health_thresholds(days=7)
```

### 5. Strategy Manager
**File:** `src/deployment/deployment_strategy.py`  
**Purpose:** Progressive deployment strategies

**Key Methods:**
```python
strategy_mgr = DeploymentStrategyManager(workspace_root)

# Create strategy
strategy = strategy_mgr.create_strategy(
    StrategyType.CANARY,
    deployment_id='deploy-123'
)

# Execute canary
result = strategy_mgr.execute_canary_deployment(
    deployment_id='deploy-123'
)

# Execute blue-green
result = strategy_mgr.execute_blue_green_deployment(
    deployment_id='deploy-123'
)

# Get recommendation
recommendation = recommend_strategy(
    deployment_size='large',
    risk_level='high',
    criticality='production'
)
```

### 6. Holistic Discovery
**File:** `src/deployment/holistic_discovery.py`  
**Purpose:** Component scanning and wiring validation

**Key Methods:**
```python
discovery = HolisticDiscoveryScanner(workspace_root)

# Scan all components
components = discovery.scan_all_components()

# Generate report
report = discovery.generate_discovery_report()

# Validate wiring
validation = discovery.validate_component_wiring()
```

---

## 💻 CLI Usage Guide

### Installation
```bash
cd /path/to/CORTEX
pip install -r requirements.txt
```

### Basic Commands

#### 1. Validate Gates (Pre-flight Check)
```bash
# Validate all gates
python -m src.deployment.deployment_cli validate-gates

# Validate critical gates only
python -m src.deployment.deployment_cli validate-gates --category critical
```

#### 2. Deploy
```bash
# Deploy with auto-selected strategy
python -m src.deployment.deployment_cli deploy

# Deploy with canary strategy
python -m src.deployment.deployment_cli deploy --strategy canary

# Deploy with blue-green strategy
python -m src.deployment.deployment_cli deploy --strategy blue-green

# Dry-run (validation only, no deployment)
python -m src.deployment.deployment_cli deploy --dry-run

# Skip gates (admin only - use with caution!)
python -m src.deployment.deployment_cli deploy --skip-gates

# Resume from checkpoint
python -m src.deployment.deployment_cli deploy --checkpoint-id checkpoint-abc123
```

#### 3. Rollback
```bash
# Rollback to latest snapshot
python -m src.deployment.deployment_cli rollback

# Rollback to specific phase
python -m src.deployment.deployment_cli rollback --phase BUILD
```

#### 4. Status
```bash
# Check current deployment status
python -m src.deployment.deployment_cli status

# Output:
📊 ACTIVE DEPLOYMENT
Deployment ID: deploy-123
Current Phase: DEPLOY
Progress: 60%
Started: 2025-12-09T18:00:00
```

#### 5. History
```bash
# View last 10 deployments
python -m src.deployment.deployment_cli history

# View last 20 deployments
python -m src.deployment.deployment_cli history --limit 20

# Filter by status
python -m src.deployment.deployment_cli history --status FAILED
```

#### 6. Metrics
```bash
# View 7-day metrics
python -m src.deployment.deployment_cli metrics

# View 30-day metrics
python -m src.deployment.deployment_cli metrics --days 30

# Output:
📈 DEPLOYMENT METRICS
Average Duration: 175.5 seconds
Success Rate: 95.0%
Total Deployments: 20
Rollback Count: 1
Health Score: 85/100 (🟢 Healthy)
```

---

## 🎯 Deployment Strategies

### When to Use Each Strategy

#### Direct Deployment
**Use for:**
- Development environment
- Low-risk changes (bug fixes, documentation)
- Small refactors
- Non-production deployments

**Characteristics:**
- ✓ Fast (~2 minutes)
- ✓ Simple workflow
- ✗ No progressive validation
- ✗ Higher risk if issues occur

#### Canary Deployment
**Use for:**
- Production deployments
- High-risk changes (major features, breaking changes)
- Large deployments (many files changed)
- First-time deployments

**Characteristics:**
- ✓ Progressive validation (10% → 50% → 100%)
- ✓ Early failure detection
- ✓ Minimized impact radius
- ✓ Health monitoring per stage
- ✗ Slower (~15 minutes)

**Configuration:**
```yaml
# cortex-brain/config/deployment-strategies.yaml
canary:
  stages: [10, 50, 100]
  stage_duration_minutes: 5
  health_check_interval_seconds: 30
  smoke_tests_required: true
  auto_rollback_on_failure: true
```

#### Blue-Green Deployment
**Use for:**
- Zero-downtime requirement
- Service availability critical
- Production with active users
- Database schema changes

**Characteristics:**
- ✓ Zero downtime
- ✓ Instant rollback capability
- ✓ Full environment validation before switch
- ✗ Requires 2x resources temporarily
- ✗ Moderate speed (~7 minutes)

**Configuration:**
```yaml
# cortex-brain/config/deployment-strategies.yaml
blue_green:
  warmup_duration_minutes: 2
  smoke_tests_required: true
  auto_switch_on_success: true
  keep_old_environment_hours: 24
  monitor_duration_after_switch_minutes: 10
```

### Strategy Recommendation Engine

```python
from src.deployment.deployment_strategy import recommend_strategy

# Get recommendation
rec = recommend_strategy(
    deployment_size='large',      # small/medium/large
    risk_level='high',            # low/medium/high
    criticality='production',     # development/staging/production
    requires_zero_downtime=True   # True/False
)

print(rec['strategy'])  # StrategyType.BLUE_GREEN
print(rec['reason'])    # "zero_downtime requirement..."
print(rec['confidence'])  # 0.95
```

---

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: Gate Validation Failures

**Symptom:**
```
❌ GATE VALIDATION FAILED
Gates Passed: 17/19
Gates Failed: 2

Failures:
  • test_coverage: Coverage below 80% (current: 75%)
    Remediation: pytest --cov=src tests/
  • brain_schema: Schema mismatch detected
    Remediation: python -m src.tier0.brain_schema_validator --fix
```

**Solution:**
1. Run recommended remediation commands
2. Re-run validation: `python -m src.deployment.deployment_cli validate-gates`
3. If persistent, review gate logs in `cortex-brain/documents/reports/deployment-gates-{timestamp}.md`

#### Issue 2: Deployment Stuck in BUILDING Phase

**Symptom:**
```
📊 ACTIVE DEPLOYMENT
Current Phase: BUILDING
Progress: 45%
Started: 30 minutes ago
```

**Solution:**
1. Check logs: `logs/deployment-{deployment_id}.log`
2. Verify disk space: `df -h`
3. Kill stuck process: `lsof -ti:PORT | xargs kill -9`
4. Resume or rollback:
   ```bash
   # Try resume
   python -m src.deployment.deployment_cli deploy --checkpoint-id <checkpoint>
   
   # Or rollback
   python -m src.deployment.deployment_cli rollback --phase PRE_BUILD
   ```

#### Issue 3: Canary Rollback at 50% Stage

**Symptom:**
```
⚠️ Smoke tests failed at 50% - triggering rollback
Failures:
  - Health check timeout
  - API error rate high (8% > 5% threshold)
```

**Solution:**
1. Review metrics: `python -m src.deployment.deployment_cli metrics`
2. Check smoke test logs: `cortex-brain/deployments/strategies/deploy-{id}-strategy.json`
3. Fix underlying issues (API performance, dependencies)
4. Re-deploy with longer stage duration:
   ```yaml
   # Adjust in deployment-strategies.yaml
   canary:
     stage_duration_minutes: 10  # Increase from 5
   ```

#### Issue 4: Blue-Green Switch Failure

**Symptom:**
```
❌ DEPLOYMENT FAILED
Stage: switch
Reason: switch_failed
```

**Solution:**
1. Verify green environment health:
   ```bash
   # Check green environment status
   curl http://localhost:8080/health  # Green port
   ```
2. Manual traffic switch if needed (contact DevOps)
3. Rollback to blue:
   ```bash
   python -m src.deployment.deployment_cli rollback
   ```

#### Issue 5: Post-Deployment Verification Failures

**Symptom:**
```
❌ Critical feature verification failed:
  × TDD Workflow: Test execution timeout
  × Planning System: Phase creation error
```

**Solution:**
1. Check verification report: `cortex-brain/documents/reports/deployment-verification-{timestamp}.md`
2. Auto-rollback should trigger automatically
3. If not, manual rollback:
   ```bash
   python -m src.deployment.deployment_cli rollback --phase PRE_DEPLOY
   ```
4. Fix failing features before next deployment

### Debug Mode

Enable verbose logging:
```bash
export CORTEX_DEBUG=1
export LOG_LEVEL=DEBUG

python -m src.deployment.deployment_cli deploy --strategy canary
```

Logs location: `logs/deployment-{deployment_id}.log`

---

## 📊 Metrics & Monitoring

### Health Score Calculation

**Formula:** `(success_rate * 40) + (speed_score * 30) + (rollback_score * 30)`

**Score Ranges:**
- 80-100: 🟢 Healthy
- 60-79: 🟡 Degraded
- 0-59: 🔴 Unhealthy

### Key Metrics

1. **Deployment Duration**
   - Target: <300 seconds (5 minutes)
   - Alert: >300 seconds

2. **Success Rate**
   - Target: >95%
   - Alert: <95%

3. **Rollback Frequency**
   - Target: <2 per week
   - Alert: ≥2 per week

4. **Gate Pass Rate**
   - Target: >75%
   - Alert: <75%

### Metrics Dashboard

```bash
python -m src.deployment.deployment_cli metrics --days 30

# Output:
📈 DEPLOYMENT METRICS (30 days)
===============================================
Average Duration: 175.5 seconds
Success Rate: 95.0%
Total Deployments: 20
Rollback Count: 1
Health Score: 85/100 (🟢 Healthy)

⚠️  ALERTS:
  🟡 Average duration trending upward (↑12% vs previous period)
```

### Metrics Storage

**Location:** `cortex-brain/metrics/deployments/`

**Files:**
- `deployment-metrics.jsonl` - Append-only metrics log
- `deployment-metrics-report-{timestamp}.json` - Periodic reports

**Query Metrics:**
```python
from src.deployment.deployment_metrics import DeploymentMetricsCollector

collector = DeploymentMetricsCollector()

# Get metrics for last 7 days
metrics = collector.get_metrics(start_time=datetime.now() - timedelta(days=7))

# Filter by type
durations = collector.get_metrics(metric_type=MetricType.DEPLOYMENT_DURATION)

# Aggregate statistics
avg_duration = collector.get_average_duration(days=7)
success_rate = collector.get_success_rate(days=7)
```

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/deploy.yml`

```yaml
name: CORTEX Deployment

on:
  push:
    tags:
      - 'v*.*.*'  # Trigger on version tags (e.g., v3.0.0)

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run gate validation
        run: |
          python -m src.deployment.deployment_cli validate-gates
      
      - name: Upload validation report
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: cortex-brain/documents/reports/deployment-gates-*.md

  deploy-staging:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        run: |
          python -m src.deployment.deployment_cli deploy --strategy direct
        env:
          CORTEX_ENV: staging
      
      - name: Run smoke tests
        run: |
          pytest tests/smoke/ -v

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production (canary)
        run: |
          python -m src.deployment.deployment_cli deploy --strategy canary
        env:
          CORTEX_ENV: production
      
      - name: Upload deployment metrics
        uses: actions/upload-artifact@v3
        with:
          name: deployment-metrics
          path: cortex-brain/metrics/deployments/
```

### Local Testing

```bash
# Dry-run before pushing tag
python -m src.deployment.deployment_cli deploy --dry-run

# Create tag
git tag -a v3.0.0 -m "Release v3.0.0"
git push origin v3.0.0
```

---

## 🔐 Audit & Compliance

### Audit Trail

**Location:** `cortex-brain/audit/deployments/`

**File Format:** `deployment-{deployment_id}-audit.json`

**Contents:**
```json
{
  "deployment_id": "deploy-123",
  "timestamp": "2025-12-09T18:00:00Z",
  "triggered_by": "user@example.com",
  "strategy": "canary",
  "phases": [
    {
      "phase": "PRE_FLIGHT",
      "started_at": "2025-12-09T18:00:00Z",
      "completed_at": "2025-12-09T18:00:30Z",
      "gates_passed": 19,
      "gates_failed": 0
    }
  ],
  "changes": {
    "files_modified": 15,
    "lines_added": 1200,
    "lines_deleted": 450
  },
  "rollback_events": [],
  "verification_result": {
    "passed": true,
    "critical_features_verified": 7
  },
  "signature": "sha256:abc123..."
}
```

### Query Audit Logs

```python
from src.deployment.deployment_audit import DeploymentAuditLogger

audit = DeploymentAuditLogger()

# Query by date range
logs = audit.query_deployments(
    start_date=datetime(2025, 12, 1),
    end_date=datetime(2025, 12, 31)
)

# Query by status
failed = audit.query_deployments(status='FAILED')

# Query by user
user_deploys = audit.query_deployments(user='user@example.com')

# Verify signature
valid = audit.verify_signature(deployment_id='deploy-123')
```

### Compliance Reports

**Generate compliance report:**
```bash
python -m src.deployment.deployment_audit generate-report \
  --start-date 2025-12-01 \
  --end-date 2025-12-31 \
  --output cortex-brain/audit/reports/compliance-december-2025.pdf
```

---

## 📚 Additional Resources

### Configuration Files
- `cortex-brain/config/deployment-strategies.yaml` - Strategy configuration
- `cortex-brain/orchestrator-manifests/deploy-orchestrator-manifest.yaml` - Deployment blueprint
- `cortex.config.json` - Machine-specific settings

### Documentation
- `CHANGELOG.md` - Version history and breaking changes
- `README.md` - Project overview and quick start
- `.github/copilot-instructions.md` - AI assistant guidelines

### Support
- **Issues:** Create ticket with deployment-{id} and error logs
- **Logs:** `logs/deployment-{id}.log`
- **Metrics:** `python -m src.deployment.deployment_cli metrics`

---

**Last Updated:** December 9, 2025  
**Version:** 3.0  
**Maintainer:** CORTEX Development Team
