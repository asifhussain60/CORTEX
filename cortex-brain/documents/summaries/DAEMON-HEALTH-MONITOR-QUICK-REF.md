# Daemon Health Monitor - Quick Reference

**Status:** Production Ready ✅  
**Integration:** 1-line setup  
**Performance:** <1ms per request

---

## 🚀 Quick Integration

```python
from src.daemon_health_monitor import ensure_daemon_active

# Add this ONE LINE at CORTEX startup
ensure_daemon_active()  # Done!
```

---

## 📊 At a Glance

| Metric | Value |
|--------|-------|
| **Startup overhead** | ~5ms (one-time) |
| **Per-request overhead** | <1ms (cached) |
| **Background checks** | Every 5 minutes |
| **Auto-recovery** | Yes |
| **Cross-platform** | Windows/Mac/Linux |
| **Test coverage** | 21/21 tests ✅ |

---

## 🎯 What It Does

1. **Checks** if daemon is running (fast PID file check)
2. **Auto-starts** if not running (~2s, one-time)
3. **Caches** status for 5 minutes (zero overhead)
4. **Monitors** health in background thread (every 5min)
5. **Auto-recovers** if daemon crashes

---

## 📝 Usage Examples

### Basic (Recommended)

```python
from src.daemon_health_monitor import ensure_daemon_active

ensure_daemon_active()  # That's it!
```

### With Status Feedback

```python
from src.daemon_health_monitor import ensure_daemon_active

if ensure_daemon_active():
    print("Daemon ready ✓")
else:
    print("Warning: Daemon not active")
```

### Detailed Status (Debugging)

```python
from src.daemon_health_monitor import get_daemon_status

status = get_daemon_status()
print(f"Running: {status['running']}")
print(f"PID: {status.get('pid', 'N/A')}")
print(f"Last Check: {status['last_check']}")
```

---

## 🔧 Files

| File | Purpose |
|------|---------|
| `src/daemon_health_monitor.py` | Core implementation |
| `tests/test_daemon_health_monitor.py` | Test suite (21 tests) |
| `cortex-brain/documents/implementation-guides/DAEMON-HEALTH-MONITOR-INTEGRATION.md` | Full guide |
| `cortex-brain/documents/reports/DAEMON-HEALTH-MONITOR-IMPLEMENTATION-COMPLETE.md` | Implementation report |

---

## ✅ Verification

```bash
# Run tests
pytest tests/test_daemon_health_monitor.py -v

# Expected: 21 passed ✅
```

---

## 🐛 Troubleshooting

**Daemon won't start?**
- Check: `logs/ambient_daemon.log`
- Verify: `scripts/cortex/auto_capture_daemon.py` exists
- Ensure: Write access to `logs/` directory

**Multiple instances?**
- Daemon has built-in single-instance enforcement
- If duplicates exist, delete `logs/ambient_daemon.pid` and restart

---

## 📚 Learn More

- Full guide: `cortex-brain/documents/implementation-guides/DAEMON-HEALTH-MONITOR-INTEGRATION.md`
- Setup guide: `prompts/shared/setup-guide.md` (Option 3)

---

*Last Updated: 2025-11-15*
