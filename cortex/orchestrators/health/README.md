# Phase 95: Health Agent Architecture - Quick Start Guide

## 🎯 Status: IN PROGRESS (2/12 hours complete)

### ✅ Completed (Stage 1-2)
- ✅ VacuumOrchestrator consolidated (eliminated 2 duplicates)
- ✅ Health architecture foundation
- ✅ BaseHealthAgent abstract interface
- ✅ HealthOrchestrator coordinator
- ✅ HealthReport + HealthMetrics
- ✅ DuplicateDetectionAgent (CORE-035 detection)

### ⚪ Remaining (10 hours)

#### Stage 3: Implement 5 Remaining Agents (3 hours)
1. **StubDetectionAgent** (45 min) - Detect weak implementations
2. **PathIntegrityAgent** (30 min) - Detect import path drift
3. **VersionCleanupAgent** (20 min) - Detect version artifacts
4. **TestCoverageAgent** (30 min) - Detect missing tests
5. **RegistryConsistencyAgent** (30 min) - Detect misplaced config
6. **Integration Tests** (30 min) - Test all agents together

#### Stage 4: Hooks (1 hour)
- **pre_commit.py** - Block bad commits (versioned files, backups)
- **pre_push.py** - Warn on push (duplicates, stubs, low health score)

#### Stage 5: MCP Tool (1 hour)
- **cortex_health_check** - MCP tool for health checks
- Register in MCP server

#### Stage 6: CI Integration (1 hour)
- **health-check.yml** - Nightly GitHub Actions workflow
- **CLI tool** - `python -m cortex.cli.health`

#### Stage 7: Dashboard (2 hours)
- **dashboard_exporter.py** - Export metrics to dashboard
- **Health section** - Add to dashboard UI

#### Stage 8: Golden Tests (1 hour)
- **test_duplicate_detection.py** - Golden test for duplicates
- **test_stub_detection.py** - Golden test for stubs
- **test_integration.py** - End-to-end workflow test

#### Stage 9: Validation (30 min)
- Run full health check on CORTEX
- Validate health score > 90
- Update documentation

---

## 🚀 Quick Implementation Commands

### Install Dependencies
```bash
pip install radon  # For McCabe complexity calculation
pip install rope   # For safe import refactoring
```

### Test Current Implementation
```python
from pathlib import Path
from cortex.orchestrators.health import HealthOrchestrator
from cortex.orchestrators.health.agents.duplicate_detection_agent import DuplicateDetectionAgent

# Create orchestrator
orchestrator = HealthOrchestrator(Path.cwd())

# Register duplicate detection agent
orchestrator.register_agent(DuplicateDetectionAgent())

# Run health check
report = orchestrator.run_health_check()

# Print markdown report
print(report.to_markdown())

# Get health score
print(f"Health Score: {report.metrics.health_score}/100")
```

---

## 📋 Implementation Templates

All implementation templates are in the main blueprint:
`cortex-registry/_cortex-master/phases/active/phase-95-health-agent-architecture.yaml`

Key sections:
- **implementation_guide**: Code templates for each agent
- **testing_strategy**: Test structure and coverage targets
- **external_dependencies**: Required libraries with ROI analysis

---

## 🎯 Next Session Priority

**Start with:** Stage 3, Task 3.1 - StubDetectionAgent

**Estimated time:** 45 minutes

**File to create:** `cortex/orchestrators/health/agents/stub_detection_agent.py`

**Algorithm:**
1. Scan all .py files
2. Count LOC (exclude comments/blank lines)
3. Calculate McCabe complexity using radon
4. Check for docstrings
5. Check for corresponding test file
6. Flag if < 200 LOC + low complexity + no tests

---

## 📊 Success Criteria

**Code:**
- [ ] All 6 agents implemented
- [ ] Health score calculation accurate
- [ ] Reports generate correctly

**Integration:**
- [ ] Pre-commit blocks bad commits
- [ ] MCP tool works
- [ ] CI runs nightly
- [ ] Dashboard shows metrics

**Quality:**
- [ ] Unit test coverage > 95%
- [ ] All golden tests pass
- [ ] CORTEX health score > 90

---

## 🔗 Related Documentation

- **Main Blueprint:** `cortex-registry/_cortex-master/phases/active/phase-95-health-agent-architecture.yaml`
- **Completed Work:** Phase 91 (CORE-035 remediation)
- **Architecture:** `cortex/orchestrators/health/`

---

## 💡 Key Design Decisions

1. **Agent-Based Architecture** - Each health check is a specialized agent
2. **Health Score Formula** - Critical=-20, High=-10, Medium=-5, Low=-2
3. **SSOT for Duplicates** - Prefer registry location, then largest file
4. **Non-Breaking Warnings** - Pre-push warns but doesn't block
5. **CI Nightly** - Run full health check every night
6. **Dashboard Integration** - Export metrics for visualization

---

**Ready to continue?** Start with Stage 3, Task 3.1 (StubDetectionAgent)
