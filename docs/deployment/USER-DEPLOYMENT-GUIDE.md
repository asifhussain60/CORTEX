# CORTEX User Deployment Guide

**Purpose:** Build lightweight user packages from the admin repository

**Author:** Asif Hussain  
**Version:** 1.0  
**Date:** 2025-11-11

---

## 📦 Deployment Architecture

### Two-Tier System

**ADMIN (You):** Full repository with all operations, dev tools, and tests  
**USER:** Curated package with only 3 essential operations

### Why This Matters

| Metric | Admin Repo | User Package | Reduction |
|--------|-----------|--------------|-----------|
| **Size** | 15-20 MB | 2-3 MB | 85-90% |
| **Operations** | 12 | 3 | 75% |
| **Modules** | 86 | ~20 | 77% |
| **Scripts** | 25 | 5 | 80% |
| **Install Time** | 45-60 sec | 10-15 sec | 75% |

**Benefits:**
- ✅ Faster installation
- ✅ Cleaner user experience
- ✅ No admin tools exposed
- ✅ Smaller attack surface
- ✅ Simpler documentation

---

## 🎯 User Operations

### Included (3 Operations)

1. **`cortex_tutorial`** - Interactive onboarding demo
   - 6 modules (intro, help, story refresh, cleanup, conversation, completion)
   - 2-6 minute walkthrough depending on profile
   
2. **`environment_setup`** - Environment configuration
   - 11 modules (validation, platform detect, git sync, venv, deps, etc.)
   - 3 profiles: minimal, standard, full
   
3. **`workspace_cleanup`** - Workspace maintenance
   - 1 orchestrator (coordinates all cleanup operations)
   - 3 profiles: quick, standard, comprehensive

### Excluded (Admin-Only)

- ❌ `refresh_cortex_story` - Updates CORTEX's own docs
- ❌ `update_documentation` - Builds CORTEX's MkDocs site
- ❌ `brain_protection_check` - Internal validation
- ❌ `brain_health_check` - System diagnostics
- ❌ `comprehensive_self_review` - Dev validation
- ❌ `design_sync` - Architecture maintenance
- ❌ `optimize_cortex` - Performance tuning

---

## 🛠️ Building User Package

### Quick Build

```bash
python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0
```

### Preview (Dry Run)

```bash
python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0 --dry-run
```

### Custom Output

```bash
python scripts/build_user_deployment.py \
  --output /path/to/custom/location \
  --project-root /path/to/CORTEX
```

---

## 📋 Build Process

### 1. Load Configuration

Reads `cortex-operations.yaml` and filters based on `deployment_tier`:

```yaml
cortex_tutorial:
  deployment_tier: user  # ✅ Included

refresh_cortex_story:
  deployment_tier: admin  # ❌ Excluded
```

### 2. Extract User Modules

Identifies all modules needed by user operations:
- `demo_introduction_module.py`
- `demo_help_system_module.py`
- `platform_detection_module.py`
- `cleanup_orchestrator.py`
- etc.

### 3. Copy Filtered Files

**Includes:**
- ✅ `src/` (filtered modules only)
- ✅ `prompts/shared/` (user docs)
- ✅ `.github/copilot-instructions.md`
- ✅ `cortex-brain/` (structure only, no admin docs)
- ✅ `requirements.txt` (production deps only)
- ✅ `LICENSE`

**Excludes:**
- ❌ `tests/` (development only)
- ❌ `docs/architecture/` (admin reference)
- ❌ `scripts/` (admin scripts, keeps user-facing ones)
- ❌ `cortex-brain/*.md` (design docs)
- ❌ `workflow_checkpoints/`
- ❌ `.github/workflows/` (CI/CD)
- ❌ Admin operation modules

### 4. Create User Files

- **`README.md`** - User-focused quick start
- **`requirements.txt`** - Production dependencies only
- **`cortex-operations.yaml`** - 3 operations only

### 5. Generate Statistics

Reports:
- Files copied vs excluded
- Package size
- Module count
- Operation count

---

## 📦 Package Structure

```
cortex-user-v1.0.0/
├── src/
│   ├── tier0/              # Brain protection
│   ├── tier1/              # Conversation memory
│   ├── tier2/              # Knowledge graph
│   ├── tier3/              # Dev context
│   ├── cortex_agents/      # All 10 agents
│   └── operations/
│       └── modules/        # 20 user modules only
├── prompts/
│   └── shared/             # User docs only
├── .github/
│   ├── copilot-instructions.md
│   └── prompts/
│       └── CORTEX.prompt.md
├── cortex-brain/           # Structure only
├── requirements.txt        # Production deps
├── cortex-operations.yaml  # 3 operations
├── cortex.config.template.json
├── LICENSE
└── README.md               # User quick start
```

---

## 🚀 Distribution

### Option 1: GitHub Releases

1. Build package
2. Zip it
3. Upload to GitHub releases
4. Users download and extract

```bash
python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0
cd dist
zip -r cortex-user-v1.0.0.zip cortex-user-v1.0.0/
# Upload to GitHub releases
```

### Option 2: Python Package (PyPI)

Future: Create `setup.py` and publish to PyPI

```bash
pip install cortex-ai
```

### Option 3: VS Code Extension Bundle

Package with VS Code extension for one-click install

---

## 🔧 Maintenance

### Adding New User Operation

1. Create operation in `cortex-operations.yaml`
2. Set `deployment_tier: user`
3. Implement modules
4. Run build script
5. Test user package

### Removing User Operation

1. Change `deployment_tier: admin` in YAML
2. Run build script
3. Operation excluded automatically

### Updating User Package

1. Make changes to user operations/modules
2. Run build script
3. Increment version in `build_user_deployment.py`
4. Create new GitHub release

---

## ✅ Testing User Package

### 1. Build Package

```bash
python scripts/build_user_deployment.py --output ./test-package
```

### 2. Test Installation

```bash
cd test-package
cp cortex.config.template.json cortex.config.json
# Edit cortex.config.json
pip install -r requirements.txt
```

### 3. Test Operations

In GitHub Copilot Chat:
```
demo
setup environment
cleanup workspace
```

### 4. Verify Exclusions

Confirm admin operations NOT available:
```
refresh cortex story          # Should fail gracefully
brain health check            # Should fail gracefully
```

---

## 📊 Validation Checklist

Before releasing user package:

- [ ] Build completes without errors
- [ ] Package size < 5 MB
- [ ] Only 3 operations in `cortex-operations.yaml`
- [ ] No admin scripts in `scripts/`
- [ ] No test files in package
- [ ] `requirements.txt` has production deps only
- [ ] User README.md is clear and concise
- [ ] All 3 user operations work end-to-end
- [ ] Admin operations not accessible
- [ ] LICENSE file included
- [ ] Copyright headers present

---

## 🎯 Future Enhancements

### Phase 1 (Current)
- ✅ Deployment tier flags in YAML
- ✅ Build script for user package
- ✅ Filtered operations config
- ✅ User-focused documentation

### Phase 2 (Next)
- [ ] Automated testing of user package
- [ ] Version management system
- [ ] Changelog generation
- [ ] Release notes automation

### Phase 3 (Future)
- [ ] PyPI package publishing
- [ ] VS Code extension integration
- [ ] Auto-update mechanism
- [ ] Telemetry (opt-in) for user feedback

---

## 📚 Related Documentation

- **Operations Reference:** `prompts/shared/operations-reference.md`
- **Build Script:** `scripts/build_user_deployment.py`
- **Configuration:** `cortex-operations.yaml`

---

**Questions?** See `docs/deployment/FAQ.md` (coming soon)

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
