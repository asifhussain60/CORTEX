# 🏗️ CORTEX Production Package Wiring - Architecture Review
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**Review Date:** December 16, 2025  
**Scope:** Unified Planning System Integration + Production Package Deployment  
**Status:** ⚠️ CRITICAL GAPS IDENTIFIED - Action Required

---

## 🎯 Executive Summary

**Problem:** When CORTEX is installed as a production package (`pip install cortex-ai`), several critical wiring components may break due to:
- Hardcoded development paths (`Path(__file__).parent.parent`)
- Missing entry point declarations
- Configuration files not included in package
- Import paths assuming development directory structure

**Impact:** 🔴 HIGH - Unified planning system components won't function in production installations

**Recommendation:** Implement 7-phase architecture hardening (48-56h effort)

---

## 📊 Current State Analysis

### 1. Package Configuration Status

#### **Setup.py Files Found:**
- ✅ `scripts/temp/setup.py` (v5.2.0) - Most recent
- ✅ `KASHKOLE/publish/cortex-files/setup.py` (v5.2.0) - Published version
- ❌ **NO ROOT-LEVEL setup.py** - Missing canonical package definition

#### **Configuration Issues:**

| Issue | Severity | Impact |
|-------|----------|--------|
| No root-level setup.py | 🔴 CRITICAL | Cannot install CORTEX from source |
| Entry points incomplete | 🔴 CRITICAL | CLI commands won't work |
| Package data partial | 🟡 MEDIUM | Config files may be missing |
| No MANIFEST.in | 🟡 MEDIUM | Non-Python files excluded |
| Hardcoded paths | 🔴 CRITICAL | Breaks in installed package |

---

### 2. Entry Points Analysis

#### **Current Entry Points (from scripts/temp/setup.py):**

```python
entry_points={
    "console_scripts": [
        "cortex=src.cortex_cli:main",  # Main CLI entry point
    ],
},
```

#### **Missing Entry Points for Unified Planning System:**

**Required but NOT declared:**

1. **Planning Gate** - `src.entry_point.planning_gate:PlanningGate`
   - ❌ Not exposed as entry point
   - ❌ No CLI command (`cortex plan`, `cortex approve`, `cortex reject`)

2. **Planning Orchestrator** - `src.orchestration_3_0.orchestrators.planning:PlanningOrchestrator`
   - ❌ Not exposed via entry point
   - ❌ No programmatic API for other packages

3. **Temporary Plan Manager** - `src.operations.modules.orchestration.temporary_plan_manager:TemporaryPlanManager`
   - ❌ Not exposed
   - ❌ No CLI command (`cortex temp-plan create`, `cortex temp-plan approve`)

4. **Plan Lifecycle Manager** - `src.planning.plan_lifecycle_manager:PlanLifecycleManager`
   - ❌ Not exposed
   - ❌ No state transition commands

5. **CORTEX LENS Integration**
   - ❌ Not exposed (if LENS is separate package, needs plugin interface)

**Gap Impact:** Users installing `pip install cortex-ai` cannot use planning system features.

---

### 3. Path Resolution Issues

#### **Hardcoded Path Patterns (🔴 BREAKS IN PRODUCTION):**

**Found 10+ instances of development-only path resolution:**

```python
# Example 1: TDD Workflow Orchestrator (line 316)
cortex_root = Path(__file__).parent.parent.parent.resolve()  # CORTEX root
# ❌ Assumes: /path/to/CORTEX/src/workflows/tdd_workflow_orchestrator.py
# ✅ Should use: importlib.resources or config.root_path

# Example 2: Documentation Validator (line 267)
schema_path = Path(__file__).parent.parent.parent / 'cortex-brain' / 'documents' / 'standards'
# ❌ Assumes: cortex-brain/ at repo root
# ✅ Should use: importlib.resources.files('cortex_brain').joinpath('documents/standards')

# Example 3: TDD Workflow Integrator (line 39)
self.brain_path = brain_path or Path(__file__).parent.parent.parent / "cortex-brain"
# ❌ Hardcoded relative path
# ✅ Should use: config.brain_path (already supports multi-machine)
```

**Why This Breaks:**

Development structure:
```
/path/to/CORTEX/
├── src/
│   └── workflows/
│       └── tdd_workflow_orchestrator.py  # <-- __file__ here
├── cortex-brain/
└── setup.py
```

Production structure (after `pip install`):
```
/usr/local/lib/python3.9/site-packages/
├── cortex_ai/           # <-- Package root (renamed)
│   ├── src/
│   │   └── workflows/
│   │       └── tdd_workflow_orchestrator.py  # <-- __file__ here
│   └── cortex_brain/   # <-- May be here or separate package
└── cortex_ai-5.2.0.dist-info/
```

**Result:** `Path(__file__).parent.parent.parent` points to `site-packages/`, not CORTEX root!

---

### 4. Configuration File Inclusion

#### **Current package_data (from setup.py):**

```python
package_data={
    "": [
        "*.yaml",
        "*.yml",
        "*.json",
        "*.jsonl",
        "*.md",
        "*.txt",
        "*.prompt.md",
    ],
    "cortex_brain": [  # ⚠️ Assumes cortex_brain is a Python package
        "**/*.yaml",
        "**/*.yml",
        "**/*.json",
        "**/*.jsonl",
        "**/*.md",
    ],
},
```

#### **Missing Critical Files:**

**Unified Planning System Requirements:**

1. ❌ **Master Plan Templates** - `cortex-brain/documents/planning/active/cortex-rearchitecture-v1/00-master-plan.md`
   - Required by: `UnifiedPlanGenerator`
   - Not included: `cortex-brain/documents/` not in `package_data`

2. ❌ **Planning Manifests** - `planning-system-2.0-manifest.yaml`, `ado-planning-manifest.yaml`
   - Required by: Planning orchestrators for DoR/DoD validation
   - Not included: Root-level YAML files not packaged

3. ❌ **Brain Protection Rules** - `cortex-brain/brain-protection-rules.yaml`
   - Required by: SKULL enforcement
   - Not included: May be in `cortex_brain` package but path resolution breaks

4. ❌ **Response Templates** - `cortex-brain/response-templates.yaml`
   - Required by: All CORTEX responses
   - Not included: Same issue

5. ❌ **Operation Definitions** - `cortex-operations.yaml`
   - Required by: Entry point routing
   - Not included: Root-level file

**Impact:** Planning system cannot load templates → crashes on execution.

---

### 5. Import Path Compatibility

#### **Current Import Patterns:**

**✅ GOOD (Absolute imports from src):**
```python
from src.config import config
from src.entry_point.planning_gate import PlanningGate
from src.orchestration_3_0.orchestrators.planning import PlanningOrchestrator
```

**⚠️ POTENTIALLY BROKEN (Relative imports):**
```python
from ..core.base_orchestrator import BaseOrchestrator  # May work
from ...session.session_manager import SessionManager  # Fragile
```

**🔴 DEFINITELY BROKEN (Direct file references):**
```python
manifest_path = Path(__file__).parent.parent / "planning-system-2.0-manifest.yaml"
# ❌ Breaks when installed
```

**Why This Matters:**

When installed via pip, Python package structure may change:
- `src/` might become `cortex_ai/src/` or flattened
- `cortex-brain/` might become separate package `cortex_brain`
- Relative imports may break if package structure reorganized

---

### 6. CORTEX Config System (✅ MOSTLY GOOD)

#### **Current Implementation: `src/config.py`**

**Strengths:**
- ✅ Multi-machine path resolution
- ✅ Environment variable fallback (`CORTEX_ROOT`)
- ✅ Hostname-based detection
- ✅ Searches up directory tree for `cortex.config.json`

**Production Compatibility:**
- ✅ Works if `cortex.config.json` in user's project
- ✅ Falls back to environment variables
- ⚠️ But doesn't handle installed package resources

**Gap:** No fallback to package resources when config not found:

```python
# Current (line 115-130):
def _determine_root_path(self) -> Path:
    # 1. Environment variable
    # 2. Machine-specific path in config
    # 3. Default rootPath in config
    # 4. Relative path from this file  # <-- BREAKS IN PRODUCTION
    
    return Path(__file__).parent.parent  # ❌ Points to site-packages

# Should add:
    # 5. Package resources (if installed)
    try:
        import importlib.resources
        return importlib.resources.files('cortex_ai')
    except:
        # Final fallback
        return Path.cwd()
```

---

## 🔧 Required Architectural Changes

### Phase 1: Root-Level Setup.py (CRITICAL)

**Action:** Create canonical `setup.py` at CORTEX root

**Location:** `D:\PROJECTS\CORTEX\setup.py` (currently missing)

**Template:**
```python
"""
CORTEX AI - Production Package Setup
Author: Asif Hussain
Version: 5.3.0 (Unified Planning System)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="cortex-ai",
    version="5.3.0",
    author="Asif Hussain",
    author_email="asif@cortexai.dev",
    description="AI enhancement system with unified planning, long-term memory, and strategic execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asifhussain60/CORTEX",
    
    # Package discovery
    packages=find_packages(
        include=["src", "src.*", "cortex_brain", "cortex_brain.*"],
        exclude=["tests", "tests.*", "docs", "examples", "scripts.temp"]
    ),
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            # Main CLI
            "cortex=src.main:main",
            
            # Planning System Commands
            "cortex-plan=src.entry_point.planning_gate:cli_entry",
            "cortex-approve=src.planning.plan_lifecycle_manager:approve_cli",
            "cortex-reject=src.planning.plan_lifecycle_manager:reject_cli",
            
            # Setup & Maintenance
            "cortex-setup=scripts.setup_cortex:main",
            "cortex-align=src.operations.align:main",
            "cortex-healthcheck=src.operations.healthcheck:main",
        ],
    },
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "": [
            "*.yaml",
            "*.yml",
            "*.json",
            "*.jsonl",
            "*.md",
            "*.txt",
            "*.prompt.md",
        ],
        "cortex_brain": [
            "**/*.yaml",
            "**/*.yml",
            "**/*.json",
            "**/*.jsonl",
            "**/*.md",
        ],
        "src": [
            "**/*.yaml",
            "**/*.yml",
            "**/*.json",
        ],
    },
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=requirements,
    
    extras_require={
        "dev": [
            "pytest>=8.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "optional": [
            # Lazy-loaded dependencies
            "tree-sitter>=0.20.0",
            "scikit-learn>=1.3.0",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    
    zip_safe=False,
    license="Proprietary",
    keywords="ai copilot memory context planning assistant cognitive-framework",
)
```

**Estimated Effort:** 2-4 hours

---

### Phase 2: MANIFEST.in Creation (HIGH PRIORITY)

**Action:** Create `MANIFEST.in` to include non-Python files

**Location:** `D:\PROJECTS\CORTEX\MANIFEST.in` (currently missing)

**Content:**
```manifest
# CORTEX AI - Package Manifest
# Includes critical non-Python files for production deployment

# Configuration files
include cortex.config.template.json
include cortex-operations.yaml
include deployment-manifest.yaml
include requirements*.txt
include LICENSE
include README.md
include CHANGELOG.md

# Prompt files
recursive-include .github/prompts *.md
recursive-include .github/prompts *.prompt.md

# Brain files
recursive-include cortex-brain *.yaml
recursive-include cortex-brain *.yml
recursive-include cortex-brain *.json
recursive-include cortex-brain *.jsonl
recursive-include cortex-brain *.md
recursive-include cortex-brain *.txt

# Planning templates
recursive-include cortex-brain/documents/planning *.md
recursive-include cortex-brain/documents/planning *.yaml

# Source configurations
recursive-include src *.yaml
recursive-include src *.yml
recursive-include src *.json

# Scripts (CLI wrappers)
recursive-include scripts *.py
recursive-include scripts *.sh
recursive-include scripts *.ps1

# Templates
recursive-include templates *.html
recursive-include templates *.md
recursive-include templates *.yaml

# Exclude
exclude .env
exclude .gitignore
exclude pytest.ini
recursive-exclude tests *
recursive-exclude docs *
recursive-exclude examples *
recursive-exclude .venv *
recursive-exclude __pycache__ *
recursive-exclude *.pyc
recursive-exclude .pytest_cache *
```

**Why This Matters:**
- Ensures all YAML, JSON, Markdown files included in package
- Planning templates available at runtime
- Configuration files accessible

**Estimated Effort:** 1-2 hours

---

### Phase 3: Path Resolution Hardening (CRITICAL)

**Action:** Replace all hardcoded paths with package-aware resolution

**Affected Files (10+ files):**

1. `src/workflows/tdd_workflow_orchestrator.py` (line 316, 981)
2. `src/workflows/tdd_workflow_integrator.py` (line 39)
3. `src/validators/documentation_format_validator.py` (line 267)
4. `src/validation/post_deployment_validator.py` (line 26, 40)
5. `src/utils/report_dashboard_generator.py` (line 36)
6. `src/operations/modules/planning/unified_plan_generator.py` (if using hardcoded paths)
7. All orchestrators in `src/orchestration_3_0/`

**Solution Pattern:**

```python
# ❌ OLD (Development only):
cortex_root = Path(__file__).parent.parent.parent.resolve()
brain_path = cortex_root / "cortex-brain"
template_path = brain_path / "documents" / "planning" / "templates" / "master.md"

# ✅ NEW (Production compatible):
from src.config import config
from src.utils.resource_resolver import resolve_resource

cortex_root = config.root_path
brain_path = config.brain_path
template_path = resolve_resource(
    "cortex_brain.documents.planning.templates",
    "master.md"
)
```

**Create New Utility: `src/utils/resource_resolver.py`**

```python
"""
Resource Resolver for Production Package Compatibility

Handles resource loading in both development and production environments.
"""

from pathlib import Path
from typing import Union
import importlib.resources
import sys

def resolve_resource(
    package: str,
    resource: str,
    fallback_path: Union[str, Path] = None
) -> Path:
    """
    Resolve resource path in development or production.
    
    Args:
        package: Package name (e.g., "cortex_brain.documents.planning")
        resource: Resource filename (e.g., "master-plan.md")
        fallback_path: Development fallback path
        
    Returns:
        Path to resource
        
    Examples:
        # Production (installed package):
        resolve_resource("cortex_brain.documents.planning", "master-plan.md")
        # Returns: /usr/local/lib/python3.9/site-packages/cortex_brain/documents/planning/master-plan.md
        
        # Development (source tree):
        resolve_resource("cortex_brain.documents.planning", "master-plan.md",
                        fallback_path="cortex-brain/documents/planning/master-plan.md")
        # Returns: /path/to/CORTEX/cortex-brain/documents/planning/master-plan.md
    """
    # Try importlib.resources first (production)
    if sys.version_info >= (3, 9):
        try:
            files = importlib.resources.files(package)
            resource_path = files / resource
            if resource_path.is_file():
                return Path(str(resource_path))
        except (ImportError, FileNotFoundError, AttributeError):
            pass
    
    # Fallback to development path
    if fallback_path:
        from src.config import config
        full_path = config.root_path / fallback_path
        if full_path.exists():
            return full_path
    
    # Last resort: search from config root
    from src.config import config
    package_parts = package.replace(".", "/")
    search_path = config.root_path / package_parts / resource
    if search_path.exists():
        return search_path
    
    raise FileNotFoundError(
        f"Resource not found: {package}::{resource}\n"
        f"Searched:\n"
        f"  - Package resources: {package}\n"
        f"  - Fallback: {fallback_path}\n"
        f"  - Config root: {config.root_path}"
    )


def resolve_brain_resource(relative_path: str) -> Path:
    """
    Resolve cortex-brain resource.
    
    Args:
        relative_path: Path relative to cortex-brain/ (e.g., "documents/planning/master.md")
        
    Returns:
        Absolute path to resource
    """
    return resolve_resource(
        "cortex_brain",
        relative_path,
        fallback_path=f"cortex-brain/{relative_path}"
    )
```

**Migration Example:**

```python
# Before (in tdd_workflow_orchestrator.py):
cortex_root = Path(__file__).parent.parent.parent.resolve()

# After:
from src.utils.resource_resolver import resolve_brain_resource
from src.config import config

cortex_root = config.root_path
```

**Estimated Effort:** 12-16 hours (10+ files to update)

---

### Phase 4: Entry Point CLI Wrappers (HIGH PRIORITY)

**Action:** Create CLI entry points for planning system commands

**New Files Required:**

1. **`src/entry_point/planning_gate.py`** - Add CLI function:
```python
def cli_entry():
    """CLI entry point for cortex-plan command."""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="CORTEX Planning Gate")
    parser.add_argument("request", help="User request to plan")
    parser.add_argument("--approve", action="store_true", help="Auto-approve plan")
    args = parser.parse_args()
    
    gate = PlanningGate()
    result = gate.process_request(args.request)
    
    print(json.dumps(result, indent=2))
```

2. **`src/planning/plan_lifecycle_manager.py`** - Add CLI functions:
```python
def approve_cli():
    """CLI entry point for cortex-approve command."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Approve CORTEX plan")
    parser.add_argument("plan_id", help="Plan ID to approve")
    parser.add_argument("--user", default="cli", help="Approver name")
    args = parser.parse_args()
    
    manager = PlanLifecycleManager()
    result = manager.approve_plan(args.plan_id, approved_by=args.user)
    
    print(f"✅ Plan {args.plan_id} approved" if result.approved else f"❌ Approval failed")

def reject_cli():
    """CLI entry point for cortex-reject command."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reject CORTEX plan")
    parser.add_argument("plan_id", help="Plan ID to reject")
    parser.add_argument("--reason", default="User rejected", help="Rejection reason")
    args = parser.parse_args()
    
    manager = PlanLifecycleManager()
    manager.reject_plan(args.plan_id, reason=args.reason)
    
    print(f"❌ Plan {args.plan_id} rejected and deleted")
```

**Usage After Install:**
```bash
pip install cortex-ai

# Create plan
cortex-plan "implement authentication system"

# Approve plan
cortex-approve TEMP-PLAN-20251216_104530-implement-authentication

# Reject plan
cortex-reject TEMP-PLAN-20251216_104530-implement-authentication --reason "requirements changed"
```

**Estimated Effort:** 6-8 hours

---

### Phase 5: Configuration File Deployment (MEDIUM PRIORITY)

**Action:** Ensure config files accessible in production

**Options:**

**Option A: Include in Package (Recommended)**
```python
# In setup.py:
package_data={
    "": [
        "cortex.config.template.json",  # Template for users
        "cortex-operations.yaml",       # Operation definitions
    ],
}
```

Users must create `cortex.config.json` in their project:
```bash
cortex-setup --init  # Copies template to current directory
```

**Option B: User's Home Directory**
```python
# In config.py, add fallback:
def _find_config_file(self) -> Optional[Path]:
    # 1. Search up from current directory
    # 2. Check user's home directory
    home_config = Path.home() / ".cortex" / "cortex.config.json"
    if home_config.exists():
        return home_config
    # 3. Package resources (installed template)
```

**Option C: Environment Variables Only**
```bash
export CORTEX_ROOT=/path/to/cortex
export CORTEX_BRAIN=/path/to/cortex/cortex-brain
```

**Recommended:** Option A + B (package template + home fallback)

**Estimated Effort:** 4-6 hours

---

### Phase 6: Integration Testing (CRITICAL)

**Action:** Test production package installation on clean environment

**Test Matrix:**

| Platform | Python | Install Method | Test Cases |
|----------|--------|---------------|------------|
| Windows | 3.9 | `pip install dist/cortex-ai-5.3.0.tar.gz` | CLI, Planning, Paths |
| Windows | 3.11 | `pip install dist/cortex-ai-5.3.0-py3-none-any.whl` | CLI, Planning, Paths |
| macOS | 3.10 | `pip install cortex-ai` | CLI, Planning, Paths |
| Linux | 3.12 | `pip install cortex-ai` | CLI, Planning, Paths |

**Test Script: `tests/integration/test_production_install.py`**

```python
"""
Integration tests for production package installation.

Run on clean virtual environment:
    python -m venv test-env
    test-env/bin/pip install dist/cortex-ai-5.3.0.tar.gz
    test-env/bin/python tests/integration/test_production_install.py
"""

import subprocess
import sys
from pathlib import Path


def test_cli_commands():
    """Test CLI commands work after install."""
    commands = [
        ["cortex", "--version"],
        ["cortex", "help"],
        ["cortex-plan", "--help"],
        ["cortex-approve", "--help"],
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {cmd}\n{result.stderr}"
        print(f"✅ {' '.join(cmd)}")


def test_resource_loading():
    """Test resources load correctly."""
    from src.utils.resource_resolver import resolve_brain_resource
    
    # Test brain protection rules
    rules_path = resolve_brain_resource("brain-protection-rules.yaml")
    assert rules_path.exists(), f"Brain protection rules not found: {rules_path}"
    print(f"✅ Brain protection rules: {rules_path}")
    
    # Test response templates
    templates_path = resolve_brain_resource("response-templates.yaml")
    assert templates_path.exists(), f"Response templates not found: {templates_path}"
    print(f"✅ Response templates: {templates_path}")


def test_planning_system():
    """Test planning system functions."""
    from src.entry_point.planning_gate import PlanningGate
    
    gate = PlanningGate()
    result = gate.process_request("simple test request")
    
    assert "complexity_tier" in result
    assert "requires_planning" in result
    print(f"✅ Planning gate: {result}")


if __name__ == "__main__":
    print("Testing CORTEX production installation...")
    test_cli_commands()
    test_resource_loading()
    test_planning_system()
    print("\n✅ All production tests passed!")
```

**Estimated Effort:** 8-12 hours

---

### Phase 7: Documentation & Deployment Guide (LOW PRIORITY)

**Action:** Create deployment documentation for users

**New Document: `docs/deployment/production-install-guide.md`**

**Contents:**
1. Installation instructions
2. Configuration setup
3. Troubleshooting common issues
4. Platform-specific notes
5. Uninstallation

**Estimated Effort:** 4-6 hours

---

## 📊 Implementation Roadmap

### Quick Wins (High ROI, Low Effort)

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| Phase 1: Root setup.py | 🔴 CRITICAL | 2-4h | Enables installation |
| Phase 2: MANIFEST.in | 🔴 CRITICAL | 1-2h | Includes all files |
| Phase 4: Entry point CLI | 🟡 HIGH | 6-8h | User-facing commands |

**Total Quick Wins:** 9-14 hours → Makes package installable

---

### Foundation (Medium Effort, High Impact)

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| Phase 3: Path hardening | 🔴 CRITICAL | 12-16h | Fixes runtime errors |
| Phase 5: Config deployment | 🟡 MEDIUM | 4-6h | Multi-user support |

**Total Foundation:** 16-22 hours → Makes package functional

---

### Validation (High Effort, Critical Quality)

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| Phase 6: Integration testing | 🔴 CRITICAL | 8-12h | Prevents regressions |
| Phase 7: Documentation | 🟢 LOW | 4-6h | User enablement |

**Total Validation:** 12-18 hours → Ensures quality

---

### Total Effort: 37-54 hours (5-7 days @ 1 sr engineer)

**Phased Rollout:**
- **Week 1:** Phases 1-2 (Quick Wins) → Installable package
- **Week 2:** Phase 3 (Path Hardening) → Functional package
- **Week 3:** Phases 4-6 (CLI + Testing) → Production-ready package

---

## 🚨 Risk Assessment

### High Risks (Blocking Production)

1. **Path Resolution Breaks**
   - **Probability:** 🔴 90% (hardcoded paths everywhere)
   - **Impact:** 🔴 CRITICAL (Planning system crashes)
   - **Mitigation:** Phase 3 must complete before any production release

2. **Missing Configuration Files**
   - **Probability:** 🔴 80% (no MANIFEST.in)
   - **Impact:** 🔴 CRITICAL (Cannot load templates, rules)
   - **Mitigation:** Phase 2 required

3. **Entry Points Not Declared**
   - **Probability:** 🟡 60% (current setup.py incomplete)
   - **Impact:** 🟡 HIGH (CLI commands don't work)
   - **Mitigation:** Phase 4 adds wrappers

---

### Medium Risks (Degraded Functionality)

4. **Config File Discovery**
   - **Probability:** 🟡 50% (multi-machine logic complex)
   - **Impact:** 🟡 MEDIUM (Users need manual config)
   - **Mitigation:** Phase 5 adds fallbacks

5. **Import Path Changes**
   - **Probability:** 🟢 30% (mostly absolute imports)
   - **Impact:** 🟡 MEDIUM (Some features break)
   - **Mitigation:** Integration testing (Phase 6)

---

### Low Risks (Minor Issues)

6. **Platform-Specific Bugs**
   - **Probability:** 🟢 20% (config.py handles platforms)
   - **Impact:** 🟢 LOW (Affects subset of users)
   - **Mitigation:** Cross-platform testing

---

## ✅ Validation Checklist

Before releasing production package, verify:

### Installation
- [ ] `pip install cortex-ai` succeeds on clean venv
- [ ] `pip install -e .` works for development
- [ ] All dependencies install correctly
- [ ] No missing files warnings during install

### CLI Commands
- [ ] `cortex --version` returns correct version
- [ ] `cortex help` shows all commands
- [ ] `cortex-plan "test"` creates plan
- [ ] `cortex-approve <plan-id>` approves plan
- [ ] `cortex-reject <plan-id>` deletes plan

### Resource Loading
- [ ] Brain protection rules load
- [ ] Response templates load
- [ ] Master plan template loads
- [ ] Operation definitions load
- [ ] Manifests load

### Planning System
- [ ] Planning gate triages requests
- [ ] Temporary plans created
- [ ] Clarification mode works
- [ ] Plan approval transitions state
- [ ] Plan rejection deletes folder
- [ ] Master plans generated

### Cross-Platform
- [ ] Works on Windows
- [ ] Works on macOS
- [ ] Works on Linux
- [ ] Config resolution works on all platforms

### Documentation
- [ ] README installation instructions accurate
- [ ] Deployment guide complete
- [ ] Troubleshooting section helpful
- [ ] Examples work

---

## 🔄 Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/package-test.yml`:

```yaml
name: Production Package Test

on:
  push:
    branches: [ main, CORTEX-3.0 ]
  pull_request:
    branches: [ main ]

jobs:
  test-package:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Build package
      run: |
        python -m pip install --upgrade pip setuptools wheel
        python setup.py sdist bdist_wheel
    
    - name: Test installation
      run: |
        python -m venv test-env
        test-env/bin/pip install dist/*.whl
        test-env/bin/cortex --version
        test-env/bin/cortex-plan --help
    
    - name: Run integration tests
      run: |
        test-env/bin/python tests/integration/test_production_install.py
```

---

## 📚 References

**Related Documents:**
- Gap Analysis: `cortex-brain/documents/analysis/unified-planning-system-gap-analysis.md`
- Master Plan Template: `cortex-brain/documents/planning/active/cortex-rearchitecture-v1/00-master-plan.md`
- CORTEX Entry Point: `.github/prompts/CORTEX.prompt.md`

**Key Files to Modify:**
- `setup.py` (create at root)
- `MANIFEST.in` (create at root)
- `src/config.py` (add package resource fallback)
- `src/utils/resource_resolver.py` (create new)
- `src/entry_point/planning_gate.py` (add CLI entry)
- `src/planning/plan_lifecycle_manager.py` (add CLI entries)
- 10+ files with hardcoded paths

**Testing:**
- `tests/integration/test_production_install.py` (create new)
- `.github/workflows/package-test.yml` (create new)

---

## 🎯 Recommended Next Steps

1. **Immediate Action (Today):**
   - Create root-level `setup.py` (Phase 1)
   - Create `MANIFEST.in` (Phase 2)
   - Test local installation: `pip install -e .`

2. **This Week:**
   - Start path hardening (Phase 3)
   - Create `resource_resolver.py` utility
   - Update 3-5 critical files with path resolution

3. **Next Week:**
   - Complete path hardening
   - Add CLI entry points (Phase 4)
   - Write integration tests (Phase 6)

4. **Week 3:**
   - Cross-platform testing
   - Documentation
   - Production release

**Success Criteria:**
- ✅ Package installs on clean venv
- ✅ Planning system creates and approves plans
- ✅ All paths resolve correctly
- ✅ Tests pass on Windows, macOS, Linux

---

**Architecture Review Complete:** December 16, 2025  
**Next Action:** Approve implementation plan → Execute Phase 1-2 (Quick Wins)
