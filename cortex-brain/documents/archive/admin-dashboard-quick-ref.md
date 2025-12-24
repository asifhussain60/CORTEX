# Admin Dashboard - Quick Reference

**Purpose:** Launch enhanced CORTEX dashboard with repository selector dropdown

**Status:** ✅ ADMIN ONLY - Blocked from production deployment  
**Version:** 3.7.1+  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## ⚠️ SECURITY NOTICE

**THIS FEATURE IS ADMIN-ONLY AND NEVER PUBLISHED TO USERS**

Protected by:
- `deployment_tier: admin` in cortex-operations.yaml
- Listed in `publish-config.yaml` admin_operations exclusion
- **Gate 24** validation in deployment pipeline (BLOCKS deployment if leaked)
- Admin repository detection (won't work in user installations)

---

## 🚀 Usage

### Natural Language Triggers

```
load admin dashboard
launch admin dashboard
open admin dashboard
show admin dashboard
admin dashboard
```

### Direct Command

```bash
python -m src.orchestrators.dashboard_launcher --source "C:\Path\To\Repository"
```

---

## 📋 Features

### 1. Repository Discovery

Automatically scans `cortex-brain/dashboards/` for all available dashboard data:

- Lists all repositories with collected data
- Shows project type, file count, and metadata
- Sorts alphabetically for easy navigation

### 2. Smart Selection

- Remembers last selected repository
- Auto-opens to last viewed project
- Provides dropdown selector in UI
- Supports switching repositories without restart

### 3. Admin Validation

- Requires CORTEX development repository
- Checks for admin markers (tests/, docs/architecture/, etc.)
- Blocks execution in user installations
- Clear error messages guide proper usage

---

## 📊 Example Output

```
✅ Admin Dashboard launched successfully!

🌐 URL: http://localhost:8080/ui/index.html?source=v5-webservices-prevalidationws
🔌 Port: 8080
📊 Currently viewing: v5-webservices-prevalidationws

📁 Available Repositories (5):
  • alist (alist) - 1234 files
  • cortex (CORTEX) - 994 files
  • kashkole (kashkole) - 567 files
  • noor-canvas (noor-canvas) - 2456 files
  • v5-webservices-prevalidationws (V5.WebServices.PrevalidationWS) - 50 files

💡 To switch repositories:
  1. Use the dropdown selector in the dashboard UI
  2. Or stop server (Ctrl+C) and launch with:
     load admin dashboard --source "<repo-path>"
```

---

## 🔒 Deployment Protection

### Gate 24: Admin Operations Exclusion

**Validates:**
1. ✅ admin_dashboard listed in publish-config.yaml exclusions
2. ✅ admin_dashboard_launcher_module.py NOT in publish directory
3. ✅ admin_dashboard has `deployment_tier: admin` in cortex-operations.yaml
4. ✅ No admin markers leaked into user operations

**Result:** Deployment BLOCKS if any check fails

---

## 🧪 Testing

```bash
# Run admin dashboard tests
pytest tests/test_admin_dashboard.py -v

# Test admin repo detection
pytest tests/test_admin_dashboard.py::TestAdminDashboardLauncher::test_admin_repo_detection -v

# Test deployment gate
pytest tests/test_admin_dashboard.py::TestAdminOperationsExclusion::test_deployment_gate_24_exists -v
```

**Expected Results:**
- ✅ 8 tests pass
- ✅ Admin repo detected correctly
- ✅ Deployment gate validates exclusions
- ✅ Security markers present in module

---

## 📁 File Structure

```
cortex-operations.yaml
  └─ operations.admin_dashboard (deployment_tier: admin)

cortex-brain/
  ├─ publish-config.yaml
  │   └─ admin_operations: [admin_dashboard]
  └─ dashboards/
      ├─ ui/ (dashboard UI files)
      ├─ mock/ (sample data)
      ├─ cortex/ (CORTEX metrics)
      ├─ v5-webservices-prevalidationws/ (API data)
      └─ [other-repos]/ (discovered repositories)

src/
  ├─ operations/modules/
  │   └─ admin_dashboard_launcher_module.py (ADMIN ONLY)
  ├─ orchestrators/
  │   └─ dashboard_launcher.py (base launcher)
  └─ deployment/
      └─ deployment_gates.py (Gate 24)

tests/
  └─ test_admin_dashboard.py (8 tests)
```

---

## 🎯 When to Use

**Use Admin Dashboard When:**
- ✅ Working in CORTEX development repository
- ✅ Need to switch between multiple repository dashboards
- ✅ Want quick access to all available project data
- ✅ Testing dashboard with different project types
- ✅ Comparing metrics across multiple repositories

**Use Standard Dashboard When:**
- ✅ In user repository (not CORTEX dev repo)
- ✅ Only need to view single repository
- ✅ Working with users/clients
- ✅ In production environment

---

## 🚫 Error Messages

### "Admin Dashboard is only available in CORTEX development repository"

**Cause:** Running in user repository  
**Solution:** Use `load dashboard` instead (standard user command)

### "No dashboard data found"

**Cause:** No repositories have collected dashboard data  
**Solution:** Generate data first:

```bash
python -m src.orchestrators.dashboard_collector --path "C:\Path\To\Repo"
```

---

## 🔄 Workflow

1. **Generate Data** (if needed):
   ```bash
   python -m src.orchestrators.dashboard_collector --path "C:\PROJECTS\MyRepo"
   ```

2. **Launch Admin Dashboard**:
   ```
   /CORTEX load admin dashboard
   ```

3. **Select Repository**:
   - Dashboard opens with last selected repo
   - Use dropdown to switch repositories
   - Or restart with specific repo path

4. **Stop Server**:
   - Press `Ctrl+C` in terminal
   - Or close terminal window

---

## 📚 Related Documentation

- `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md` - Standard dashboard
- `cortex-brain/documents/planning/dashboard-enhancement-comprehensive-plan.md` - Enhancement plan
- `cortex-brain/publish-config.yaml` - Deployment exclusions
- `src/deployment/deployment_gates.py` - Gate 24 validation

---

## ✅ Verification Checklist

Before deployment, verify:

- [ ] admin_dashboard in cortex-operations.yaml has `deployment_tier: admin`
- [ ] admin_dashboard in publish-config.yaml admin_operations list
- [ ] admin_dashboard_launcher_module.py has ADMIN ONLY markers
- [ ] Gate 24 validation method exists in deployment_gates.py
- [ ] All 8 tests in test_admin_dashboard.py pass
- [ ] Module does NOT exist in publish/ directory after build

---

**End of Quick Reference**
