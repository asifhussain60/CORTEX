# Publish Branch Orchestrator Guide

**Purpose:** Admin-only deployment orchestrator for publishing clean CORTEX packages to production branch.

**Version:** 1.0 | **Author:** Asif Hussain | **Copyright:** © 2024-2025 | **Status:** ✅ PRODUCTION (Admin Only)

## 🎯 Overview

PublishBranchOrchestrator automates CORTEX production deployment by creating clean, tested packages and publishing to `cortex-publish` branch. Ensures zero development artifacts reach users.

### Key Features:
- **Clean Package Building** - Strips development files, tests, internal tools
- **Automated Testing** - Runs full test suite before publish
- **Version Management** - Auto-increments versions, creates tags
- **Safety Checks** - Validates package integrity, prevents broken deployments

## 🏗️ Architecture

```
CORTEX Development (CORTEX-3.0 branch)
    ↓ Build Clean Package
Clean Package (dist/cortex-user-v3.2.0/)
    ↓ Run Tests
Validated Package ✅
    ↓ Publish
cortex-publish Branch (Production)
    ↓ Download
User Installations
```

## 🔧 Core Operations

### 1. Build Clean Package
- Remove: tests/, scripts/, .github/workflows/, internal tools
- Keep: src/, cortex-brain/ (templates only), docs/, README, LICENSE
- Result: 80% smaller package (development → production)

### 2. Run Validation Tests
- Package integrity checks
- Import validation
- Feature availability tests
- Cross-platform compatibility

### 3. Publish to Branch
- Commit to `cortex-publish` branch
- Create version tag (v3.2.0)
- Update CHANGELOG
- Push to remote

## 🎯 Usage (Admin Only)

```python
from src.operations.modules.admin.publish_branch_orchestrator import PublishBranchOrchestrator

# Initialize
orchestrator = PublishBranchOrchestrator()

# Publish clean package
result = orchestrator.execute({
    "version": "3.2.0",
    "dry_run": False
})

# Output:
# {
#     "success": True,
#     "package_size_mb": 12.3,
#     "tests_passed": 834,
#     "publish_branch": "cortex-publish",
#     "tag": "v3.2.0"
# }
```

## 🚨 Safety Features

### Pre-Publish Checks
- ✅ All tests passing (834/834)
- ✅ No uncommitted changes
- ✅ Version number incremented
- ✅ CHANGELOG updated
- ✅ Package builds successfully

### Dry-Run Mode
- Simulates entire publish process
- Shows what would be published
- Validates without actual deployment
- Safe for testing publish pipeline

## 📊 Package Comparison

| Aspect | Development | Production |
|--------|-------------|-----------|
| Size | 61.2 MB | 12.3 MB |
| Files | 1,247 | 243 |
| Tests | Included | Excluded |
| Internal Tools | Included | Excluded |
| Documentation | Full | User-facing only |

## 🔗 Related Components

- **DeploymentOrchestrator** - Creates downloadable releases
- **VersionDetector** - Manages version numbers
- **CleanupOrchestrator** - Pre-publish cleanup

## 🎯 Summary

**PublishBranchOrchestrator automates production deployment with clean packages, automated testing, and safety checks. Admin-only tool ensuring users receive optimized, tested CORTEX releases.**

---
**Version:** 1.0 | **Updated:** November 25, 2025 | **Repository:** https://github.com/asifhussain60/CORTEX
