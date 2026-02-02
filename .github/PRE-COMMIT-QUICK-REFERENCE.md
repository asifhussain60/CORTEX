# Pre-Commit Validator Quick Reference

## Installation (One Command)
```bash
chmod +x scripts/install_pre_commit_hook.sh
./scripts/install_pre_commit_hook.sh
```

## How It Works (At a Glance)

### Fast Path (~100ms) - Most Commits
```
Health check OK? → Allow commit immediately
```

### Recovery Path (~2-3s) - If fast path fails
```
Health check failed → Run full validation → Allow or block
```

### What Gets Validated
- ✅ Registry initialized (23 orchestrators)
- ✅ All 23 orchestrators wired
- ✅ Database schema intact
- ✅ MCP adapters exposed
- ✅ No broken modules

## If Commit is Blocked

**You'll see remediation steps like:**
```
❌ Found 1 unwired orchestrators: BrokenOrch

Remediation Steps:
  → Run: python -m cortex.scripts.phase_3_database_registry_init
```

**Just run the suggested command and try again.**

## Skip Validation (If Needed)
```bash
git commit --no-verify
```

## View Audit Trail
```bash
# Latest 10 decisions
sqlite3 .cortex/pre_commit_audit.log \
  "SELECT * FROM pre_commit_audit ORDER BY created_at DESC LIMIT 10;"
```

## Testing
```bash
# Run test suite
pytest cortex/infrastructure/tests/test_pre_commit_validator.py -v

# Test hook directly
python3 .cortex/hooks/pre-commit-validator.py
```

## For Developers

### Extending for Future Orchestrators
Just update one line in `.cortex/pre-commit-config.yaml`:
```yaml
expected_orchestrator_count: 30  # Was 23 - no other changes needed!
```

### Performance Targets
- Stage 1: <200ms
- Stage 2: <3s
- Total: Usually <150ms

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Hook not running | `chmod +x .git/hooks/pre-commit` |
| Python not found | Ensure python3 in PATH |
| Database locked | Wait 1-2s, try again |
| Timeout errors | Check if system is overloaded |

## Architecture

```
COMMIT ATTEMPT
    ↓
STAGE 1: Quick Health Check (<200ms)
    ├─ Registry initialized?
    ├─ 23 orchestrators?
    ├─ All wired?
    ↓
    If ALL OK → ALLOW (fast path)
    If ANY FAIL → continue to Stage 2
    ↓
STAGE 2: Full Validation (<3s)
    ├─ Detailed wiring check
    ├─ Schema verification
    ├─ MCP adapters check
    ├─ Generate remediation
    ↓
    If PASS → ALLOW (fallback recovery)
    If FAIL → BLOCK + Show fixes
    ↓
AUDIT LOG → SQLite database
```

## Configuration

File: `.cortex/pre-commit-config.yaml`

```yaml
expected_orchestrator_count: 23        # Update for new orchestrators
stage_1_timeout_ms: 200                # Don't change unless needed
stage_2_timeout_ms: 3000               # Full validation timeout
health_check_cache_ttl_seconds: 5      # Cache duration
```

## CORTEX Integration

- **CORE-026:** Git checkpoint enforcement ✅
- **CORE-027:** Audit trail (SQLite) ✅
- **CORE-030:** Implementation Truth validation ✅
- **Orchestrators:** All 23/23 validated ✅

---

**See full details:** `docs/PRE-COMMIT-VALIDATOR-IMPLEMENTATION.md`
