# CORTEX Migration Validation Checklist
## Final Verification Steps

**Document:** 07-VALIDATION-CHECKLIST.md  
**Date:** 2026-01-27  

---

## 🎯 Validation Overview

| Phase | Description | Duration |
|-------|-------------|----------|
| **Pre-Migration** | Backup & preparation | 10 min |
| **Post-Migration** | File structure verification | 15 min |
| **Wiring Validation** | Wiring system tests | 20 min |
| **Integration Testing** | Full system tests | 30 min |
| **Docker Validation** | Container verification | 15 min |
| **Production Readiness** | Final checks | 10 min |
| **TOTAL** | | ~1.5 hours |

---

## 1. Pre-Migration Checklist

### 1.1 Backup Verification
```bash
# Verify backup exists
ls -la _backups/

# Should see:
# - pre-docker-migration-YYYYMMDD_HHMMSS/
```

| Check | Command | Expected |
|-------|---------|----------|
| Backup directory exists | `ls _backups/` | Directory present |
| Git stash saved | `git stash list` | Contains pre-migration stash |
| Main branch unchanged | `git log main -1` | Same as before migration |

### 1.2 Environment Verification
```bash
# Check Python version
python --version
# Expected: Python 3.11.x

# Check required packages
pip list | grep -E "pyyaml|fastapi|uvicorn|pytest"
```

| Check | Command | Expected |
|-------|---------|----------|
| Python 3.11+ | `python --version` | 3.11.x |
| PyYAML installed | `pip show pyyaml` | Installed |
| FastAPI installed | `pip show fastapi` | Installed |
| Pytest installed | `pip show pytest` | Installed |

---

## 2. Post-Migration File Structure Verification

### 2.1 Directory Structure
```bash
# Verify clean structure
tree -L 2 cortex/

# Expected directories:
# cortex/
# ├── __init__.py
# ├── api/
# ├── brain/
# ├── cli/
# ├── common/
# ├── config/
# ├── core/
# ├── infrastructure/
# ├── intent_router/
# ├── mcp/
# ├── models/
# ├── orchestrators/
# ├── tools/
# └── wiring/          # NEW - Single wiring location
```

### 2.2 Wiring Directory
```bash
# Verify wiring structure
tree cortex/wiring/

# Expected:
# cortex/wiring/
# ├── __init__.py
# ├── bootstrap.py
# ├── registry/
# │   ├── __init__.py
# │   ├── git_backed_registry.py
# │   └── lazy_orchestrator.py
# └── specifications/
#     ├── core-wiring.yaml
#     ├── domain-wiring.yaml
#     └── support-wiring.yaml
```

### 2.3 File Count Verification
```bash
# Count Python files
find cortex -name "*.py" | wc -l
# Expected: ~450 (±50)

# Count test files
find tests -name "test_*.py" | wc -l
# Expected: ~150 (±20)

# Count YAML specs
find cortex/wiring/specifications -name "*.yaml" | wc -l
# Expected: 3
```

| Check | Command | Expected |
|-------|---------|----------|
| Python files | `find cortex -name "*.py" \| wc -l` | 400-500 |
| Test files | `find tests -name "test_*.py" \| wc -l` | 130-170 |
| YAML specs | `find cortex/wiring/specifications -name "*.yaml" \| wc -l` | 3 |
| No .db files | `find . -name "*.db" \| wc -l` | 0 |

---

## 3. Forbidden Files Check

### 3.1 Legacy Wiring Files
```bash
# These files should NOT exist
ls cortex/orchestrators/core/database_registry.py 2>/dev/null && echo "FAIL" || echo "PASS"
ls cortex/orchestrators/core/orchestrator_registry.py 2>/dev/null && echo "FAIL" || echo "PASS"
ls cortex/orchestrators/bootstrap.py 2>/dev/null && echo "FAIL" || echo "PASS"
ls cortex/orchestrators/core/db_wiring_init.py 2>/dev/null && echo "FAIL" || echo "PASS"
ls cortex/orchestrators/core/permanent_wiring_state.py 2>/dev/null && echo "FAIL" || echo "PASS"
```

| File | Status |
|------|--------|
| `database_registry.py` | ❌ Should NOT exist |
| `orchestrator_registry.py` | ❌ Should NOT exist |
| `orchestrators/bootstrap.py` | ❌ Should NOT exist |
| `db_wiring_init.py` | ❌ Should NOT exist |
| `permanent_wiring_state.py` | ❌ Should NOT exist |

### 3.2 Database Files
```bash
# No database files should exist
find . -name "*.db" -type f
find . -name "*.db-journal" -type f
find . -name "*.db-wal" -type f
find . -name "*.db-shm" -type f

# All should return empty
```

### 3.3 Hidden Directories
```bash
# .cortex/ should NOT exist
ls -la .cortex/ 2>/dev/null && echo "FAIL: .cortex/ exists" || echo "PASS"
```

---

## 4. Wiring System Validation

### 4.1 Import Tests
```python
# Run in Python REPL or script
from cortex.wiring import bootstrap_cortex, get_cortex, is_wired, get_wiring_hash

# All should import without error
print("✓ Wiring module imports successfully")
```

### 4.2 Bootstrap Test
```python
from cortex.wiring import bootstrap_cortex

cortex = bootstrap_cortex()

assert cortex is not None
assert cortex.wiring_hash
assert cortex.orchestrator_count >= 23
print(f"✓ Bootstrap successful: {cortex.orchestrator_count} orchestrators, hash={cortex.wiring_hash}")
```

### 4.3 Singleton Test
```python
from cortex.wiring import bootstrap_cortex, get_cortex

c1 = bootstrap_cortex()
c2 = bootstrap_cortex()
c3 = get_cortex()

assert c1 is c2 is c3
print("✓ Singleton pattern working correctly")
```

### 4.4 YAML Parsing Test
```python
from cortex.wiring import bootstrap_cortex

cortex = bootstrap_cortex()
specs = cortex.registry.get_all_specs()

# Check required orchestrators
required = [
    "MasterOrchestrator",
    "InteractionOrchestrator", 
    "IntentRouter",
    "TDDOrchestrator",
    "RefactoringOrchestrator",
    "PlanningOrchestrator"
]

for name in required:
    assert name in specs, f"Missing: {name}"
    print(f"✓ {name} defined")

print(f"\n✓ All {len(specs)} orchestrators defined in YAML")
```

### 4.5 Wiring Order Test
```python
from cortex.wiring import bootstrap_cortex

cortex = bootstrap_cortex()
order = cortex.registry.get_wiring_order()

# Verify MasterOrchestrator is first
assert order[0] == "MasterOrchestrator", "MasterOrchestrator should be first"

# Verify dependencies come before dependents
specs = cortex.registry.get_all_specs()
order_index = {name: i for i, name in enumerate(order)}

for name, spec in specs.items():
    for dep in spec.dependencies:
        assert order_index[dep] < order_index[name], f"{name} before dependency {dep}"

print("✓ Wiring order respects all dependencies")
```

---

## 5. Test Suite Validation

### 5.1 Run Wiring Tests
```bash
# Run all wiring tests
pytest tests/wiring/ -v --tb=short

# Expected: All PASS
```

### 5.2 Run Core Tests
```bash
# Run orchestrator tests
pytest tests/orchestrators/ -v --tb=short

# Run infrastructure tests
pytest tests/infrastructure/ -v --tb=short
```

### 5.3 Test Coverage
```bash
# Run with coverage
pytest tests/wiring/ --cov=cortex.wiring --cov-report=term-missing

# Expected: >90% coverage on wiring module
```

| Test Category | Expected Outcome |
|---------------|------------------|
| Wiring tests | 65/65 PASS |
| Orchestrator tests | All PASS |
| Infrastructure tests | All PASS |
| Coverage | >90% on wiring |

---

## 6. Lazy Orchestrator Validation

### 6.1 Lazy Loading Test
```python
from cortex.wiring import bootstrap_cortex

cortex = bootstrap_cortex()

# Get lazy orchestrator
lazy = cortex.registry.get_orchestrator("IntentRouter")

# Should not be wired yet
assert not lazy.is_wired, "Should not be wired yet"

# Force wire
lazy.force_wire()

# Now should be wired
assert lazy.is_wired, "Should be wired after force_wire()"
print("✓ Lazy orchestrator loading works correctly")
```

### 6.2 Parameter Resolution Test
```python
from cortex.wiring import bootstrap_cortex

cortex = bootstrap_cortex()

# InteractionOrchestrator requires conversation_protocol
lazy = cortex.registry.get_orchestrator("InteractionOrchestrator")
lazy.force_wire()

# Should have wired successfully with parameter
assert lazy.is_wired
print("✓ Parameter resolution works correctly")
```

---

## 7. Docker Validation

### 7.1 Build Test
```bash
# Build Docker image
docker-compose build

# Expected: Successful build
```

### 7.2 Container Startup Test
```bash
# Start container
docker-compose up -d

# Wait for startup
sleep 10

# Check container is running
docker-compose ps
# Expected: Status = Up
```

### 7.3 Health Endpoint Test
```bash
# Test health endpoint
curl -s http://localhost:8443/health | jq

# Expected:
# {
#   "status": "healthy",
#   "wired": true,
#   "orchestrator_count": 23,
#   "wiring_hash": "abc123..."
# }
```

### 7.4 Wiring Hash Consistency
```bash
# Get hash from multiple requests
HASH1=$(curl -s http://localhost:8443/health | jq -r '.wiring_hash')
HASH2=$(curl -s http://localhost:8443/health | jq -r '.wiring_hash')
HASH3=$(curl -s http://localhost:8443/health | jq -r '.wiring_hash')

# All should be same
[ "$HASH1" = "$HASH2" ] && [ "$HASH2" = "$HASH3" ] && echo "✓ Hash consistent" || echo "✗ Hash inconsistent"
```

### 7.5 No Database Files in Container
```bash
# Check for .db files inside container
docker exec cortex-mcp-server find /app -name "*.db" -type f

# Expected: Empty output
```

### 7.6 Container Logs
```bash
# Check logs for errors
docker-compose logs | grep -E "ERROR|FAIL|Exception"

# Expected: No errors
```

| Docker Check | Command | Expected |
|--------------|---------|----------|
| Build | `docker-compose build` | Success |
| Container up | `docker-compose ps` | Status: Up |
| Health endpoint | `curl localhost:8443/health` | 200 OK |
| No .db files | `find /app -name "*.db"` | Empty |
| No errors | `logs \| grep ERROR` | Empty |

---

## 8. Multi-Container Validation

### 8.1 Start Multiple Containers
```bash
# Scale to 3 containers
docker-compose up -d --scale cortex-mcp=3
```

### 8.2 Hash Consistency Across Containers
```bash
# Get hash from each container
for port in 8443 8444 8445; do
    curl -s http://localhost:$port/health | jq -r '.wiring_hash'
done

# All should be identical
```

---

## 9. Production Readiness Checklist

### 9.1 Code Quality
- [ ] No `import sqlite` in `cortex/wiring/`
- [ ] No hardcoded paths
- [ ] All functions have docstrings
- [ ] Type hints on public APIs
- [ ] No print statements (use logging)

### 9.2 Security
- [ ] No secrets in code
- [ ] No debug endpoints exposed
- [ ] Health check doesn't expose sensitive data

### 9.3 Performance
- [ ] Lazy loading works correctly
- [ ] No N+1 import patterns
- [ ] Wiring completes in <5 seconds

### 9.4 Documentation
- [ ] README.md updated
- [ ] API documentation current
- [ ] YAML specs documented

---

## 10. Final Sign-Off

### 10.1 Summary Report
```bash
# Generate summary
echo "=== CORTEX Docker-Clean Migration Summary ==="
echo "Date: $(date)"
echo ""
echo "File Counts:"
echo "  Python files: $(find cortex -name '*.py' | wc -l)"
echo "  Test files: $(find tests -name 'test_*.py' | wc -l)"
echo "  YAML specs: $(find cortex/wiring/specifications -name '*.yaml' | wc -l)"
echo ""
echo "Wiring Status:"
python -c "from cortex.wiring import bootstrap_cortex; c = bootstrap_cortex(); print(f'  Orchestrators: {c.orchestrator_count}'); print(f'  Hash: {c.wiring_hash}')"
echo ""
echo "Docker Status:"
docker-compose ps
```

### 10.2 Sign-Off Checklist

| Category | Status | Verified By |
|----------|--------|-------------|
| Pre-migration backup | ☐ | |
| File structure correct | ☐ | |
| No legacy wiring files | ☐ | |
| No database files | ☐ | |
| Wiring tests pass | ☐ | |
| Docker build successful | ☐ | |
| Health endpoint working | ☐ | |
| Multi-container consistent | ☐ | |

---

## 🚨 Rollback Procedure

If validation fails:

```bash
# 1. Stop Docker
docker-compose down

# 2. Switch back to main
git checkout main

# 3. Restore stash if needed
git stash pop

# 4. Delete failed branch (optional)
git branch -D docker-clean-v1
```

---

## 📊 Expected Final State

| Metric | Target | Actual |
|--------|--------|--------|
| Python files | 400-500 | _____ |
| Test files | 130-170 | _____ |
| Wiring systems | 1 | _____ |
| Database files | 0 | _____ |
| Orchestrators | 23+ | _____ |
| Wiring tests | 65 pass | _____ |
| Docker health | OK | _____ |
