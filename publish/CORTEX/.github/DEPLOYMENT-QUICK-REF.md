# CORTEX Deployment Quick Reference

**Purpose:** Fast lookup for deployment distinctions

---

## 🎯 Operations Classification

### USER TIER (Include in Deployment)

| Operation | Purpose | Modules | Why User? |
|-----------|---------|---------|-----------|
| `cortex_tutorial` | Interactive demo | 6 | Onboarding essential |
| `environment_setup` | Configuration | 11 | First-time setup |
| `workspace_cleanup` | Maintenance | 1 | Keep workspace clean |

**Total:** 3 operations, 18 modules

---

### ADMIN TIER (Exclude from Deployment)

| Operation | Purpose | Why Admin? |
|-----------|---------|------------|
| `refresh_cortex_story` | Update CORTEX docs | Updates framework docs, not user docs |
| `update_documentation` | Build MkDocs site | Internal documentation system |
| `brain_protection_check` | Validate protections | Development validation |
| `brain_health_check` | System diagnostics | Internal health monitoring |
| `comprehensive_self_review` | Code validation | Development quality checks |
| `design_sync` | Architecture sync | Framework architecture maintenance |
| `optimize_cortex` | Performance tuning | Framework optimization |

**Total:** 9 operations, 68 modules

---

## 📦 Build Commands

### Preview Build (Dry Run)
```bash
python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0 --dry-run
```

### Build Package
```bash
python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0
```

### Create ZIP for Distribution
```powershell
Compress-Archive -Path dist/cortex-user-v1.0.0 -DestinationPath cortex-user-v1.0.0.zip
```

---

## 📊 Size Comparison

| Metric | Admin Repo | User Package | Reduction |
|--------|-----------|--------------|-----------|
| Size | 15-20 MB | 2-3 MB | 85-90% |
| Files | ~51,000 | ~19,000 | 62% |
| Operations | 12 | 3 | 75% |
| Modules | 86 | 18 | 79% |

---

## ✅ Pre-Release Checklist

- [ ] Build completes successfully
- [ ] Package size < 5 MB
- [ ] Only 3 operations in YAML
- [ ] No admin scripts present
- [ ] No test files included
- [ ] User README clear
- [ ] All 3 operations work
- [ ] Admin ops not accessible
- [ ] LICENSE included
- [ ] Copyright headers present

---

## 🚀 Quick Distribution

1. **Build:** `python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0`
2. **Test:** Validate on clean environment
3. **Zip:** `Compress-Archive dist/cortex-user-v1.0.0 cortex-user-v1.0.0.zip`
4. **Upload:** GitHub Releases

---

**Documentation:** `docs/deployment/USER-DEPLOYMENT-GUIDE.md`  
**Implementation:** `cortex-brain/USER-DEPLOYMENT-IMPLEMENTATION.md`
