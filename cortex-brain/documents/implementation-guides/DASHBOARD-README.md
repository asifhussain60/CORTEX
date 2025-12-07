# CORTEX Dashboard System - README

**Quick Start:** See [`dashboard-operation-guide.md`](./dashboard-operation-guide.md) for complete documentation.

---

## 🚀 Quick Launch

```bash
# Launch with mock data
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock

# Launch with specific repository
python3 -m src.orchestrators.dashboard_launcher --port 8080 --source my-repo-id

# Launch in background
nohup python3 -m src.orchestrators.dashboard_launcher --port 8080 --source mock > /tmp/cortex-dashboard.log 2>&1 &
```

**Dashboard URL:** `http://localhost:8080/ui/index.html?source=mock&tab=executive`

---

## 📖 Full Documentation

**Primary Guide:** [`dashboard-operation-guide.md`](./dashboard-operation-guide.md)

Contains:
- ✅ Complete launch instructions
- ✅ Data structure reference
- ✅ Server configuration details
- ✅ Troubleshooting guide
- ✅ Maintenance procedures

---

## 🔧 Common Issues

### Dashboard Shows Empty Data

**Fix:** Ensure server serves from `dashboards/` parent directory
- See `dashboard-operation-guide.md` → Troubleshooting → Issue 1

### Port Already in Use

```bash
lsof -ti:8080 | xargs kill -9
```

### Browser Shows Old Content

**Mac:** Cmd + Shift + R  
**Windows/Linux:** Ctrl + Shift + R

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `dashboard-operation-guide.md` | Complete operational documentation |
| `dashboard-launcher-quick-ref.md` | Legacy quick reference |
| `src/orchestrators/dashboard_launcher.py` | Server orchestrator |
| `cortex-brain/dashboards/ui/` | Frontend application |
| `cortex-brain/dashboards/data/` | Data files |

---

## 🎯 Next Steps

1. **Read the full guide:** [`dashboard-operation-guide.md`](./dashboard-operation-guide.md)
2. **Launch dashboard:** Follow Quick Launch above
3. **Add new repository:** See "Adding a New Repository" in operation guide
4. **Troubleshoot issues:** Check browser console + operation guide

---

**For all operational questions, refer to [`dashboard-operation-guide.md`](./dashboard-operation-guide.md)**
