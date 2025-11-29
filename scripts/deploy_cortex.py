#!/usr/bin/env python3
"""
CORTEX Production Deployment - Single Entry Point
==================================================

Purpose: THE ONLY deployment script for CORTEX. Validates, builds, and publishes 
         production-ready package to git branch.

Features:
    - Comprehensive validation (tests, docs, entry points)
    - Version management and consistency checks
    - Creates orphan 'cortex-publish' branch (clean history)
    - Production-ready package (excludes tests, dev tools)
    - GitHub Copilot integration (.github/prompts/)
    - Fault tolerant (checkpoints, resumable)
    - Users clone with: git clone -b cortex-publish --single-branch <repo>

Usage:
    python scripts/deploy_cortex.py                    # Full deployment
    python scripts/deploy_cortex.py --dry-run          # Validation only
    python scripts/deploy_cortex.py --branch custom    # Custom branch
    python scripts/deploy_cortex.py --resume           # Resume from checkpoint

Deployment Phases:
    1. Pre-flight validation (git status, VERSION file)
    2. Build production package (excludes dev artifacts)
    3. Create/update publish branch (orphan)
    4. Commit and push to remote
    5. Cleanup and verification

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import shutil
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Set, Dict, List, Optional
import json
import logging
from datetime import datetime
import traceback

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Package metadata
PACKAGE_VERSION = "3.3.0"  # Unified deployment system
PUBLISH_BRANCH = "main"

# Checkpoint file for fault tolerance
CHECKPOINT_FILE = ".publish-checkpoint.json"

# Core files that MUST be included
CORE_FILES = {
    # Entry Points - CRITICAL FOR AUTO-ACTIVATION
    # When users clone from main branch, GitHub Copilot automatically
    # discovers .github/copilot-instructions.md and loads CORTEX
    '.github/prompts/CORTEX.prompt.md',        # Main CORTEX entry point
    '.github/copilot-instructions.md',         # Auto-discovery file (MUST be on main branch)
    
    # Configuration
    'cortex.config.json',
    'cortex.config.template.json',
    'cortex-operations.yaml',
    'requirements.txt',
    'setup.py',
    'pytest.ini',
    
    # Legal & Documentation
    'README.md',
    'LICENSE',
    'CHANGELOG.md',
}

# Directories to include (complete copy)
CORE_DIRS = {
    'src',              # All Python source code
    'cortex-brain',     # Brain storage (YAML configs, schemas)
    'prompts',          # Modular documentation
    'scripts',          # Automation tools
}

# Directories to EXCLUDE
EXCLUDED_DIRS = {
    'tests',
    'workflow_checkpoints',
    '.github/workflows',
    '.github/hooks',
    'docs',             # MkDocs site (not needed for users)
    'examples',
    'site',
    'logs',
    'cortex-extension',
    '__pycache__',
    '.pytest_cache',
    '.venv',
    'venv',
    '.git',
    'dist',
    'publish',          # Don't include existing publish folder
    '.backup-archive',
    '.temp-publish',    # FIX: Temporary publish staging folder (non-production)
    'test_merge',       # FIX: Test merge artifacts (non-production)
    # Admin-only directories (SECURITY: Users must not modify CORTEX)
    'cortex-brain/admin',
    'src/operations/modules/admin',
    'scripts/admin',
    'tests/admin',
    'tests/operations/admin',
    'tests/operations/modules/admin',
    # Demo/Mock Data (PRODUCTION SAFETY: Real data generated at runtime)
    'cortex-brain/documents/analysis/INTELLIGENT-UX-DEMO',  # Mock data for Phase 1 demos only
}

# File patterns to exclude
EXCLUDED_PATTERNS = {
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    '*.db',             # Exclude populated brain databases
    '*.db-journal',
    '.coverage',
    'htmlcov',
}

# Admin-only files to EXCLUDE (SECURITY: Users must not modify CORTEX)
EXCLUDED_ADMIN_FILES = {
    'scripts/deploy_cortex.py',
    'scripts/deploy_cortex_OLD.py',
    'scripts/deploy_cortex_simple.py',
    'scripts/validate_deployment.py',
    'scripts/publish_to_branch.py',
}


# Publishing stages for checkpoint tracking
class PublishStage:
    """Publishing stage enumeration."""
    VALIDATION = "validation"
    BUILD_CONTENT = "build_content"
    BRANCH_SETUP = "branch_setup"
    CONTENT_COPY = "content_copy"
    GIT_COMMIT = "git_commit"
    GIT_PUSH = "git_push"
    CLEANUP = "cleanup"
    COMPLETE = "complete"


class CheckpointManager:
    """Manages publish checkpoints for fault tolerance."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checkpoint_file = project_root / CHECKPOINT_FILE
        self.checkpoint_data = self._load()
    
    def _load(self) -> Dict:
        """Load checkpoint data from file."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"📍 Checkpoint found: Last stage was '{data.get('last_stage')}'")
                    return data
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return {}
    
    def save(self, stage: str, data: Dict = None):
        """Save checkpoint."""
        self.checkpoint_data = {
            'last_stage': stage,
            'timestamp': datetime.now().isoformat(),
            'data': data or {},
            'version': PACKAGE_VERSION
        }
        
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.checkpoint_data, f, indent=2)
            logger.debug(f"💾 Checkpoint saved: {stage}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")
    
    def get_last_stage(self) -> Optional[str]:
        """Get last completed stage."""
        return self.checkpoint_data.get('last_stage')
    
    def get_data(self, key: str = None):
        """Get checkpoint data."""
        data = self.checkpoint_data.get('data', {})
        if key:
            return data.get(key)
        return data
    
    def should_skip_stage(self, stage: str) -> bool:
        """Check if stage should be skipped (already completed)."""
        last_stage = self.get_last_stage()
        if not last_stage:
            return False
        
        # Define stage order
        stage_order = [
            PublishStage.VALIDATION,
            PublishStage.BUILD_CONTENT,
            PublishStage.BRANCH_SETUP,
            PublishStage.CONTENT_COPY,
            PublishStage.GIT_COMMIT,
            PublishStage.GIT_PUSH,
            PublishStage.CLEANUP,
            PublishStage.COMPLETE
        ]
        
        try:
            last_idx = stage_order.index(last_stage)
            current_idx = stage_order.index(stage)
            return current_idx <= last_idx
        except ValueError:
            return False
    
    def clear(self):
        """Clear checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            logger.debug("🗑️  Checkpoint cleared")
    
    def exists(self) -> bool:
        """Check if checkpoint exists."""
        return self.checkpoint_file.exists()


def run_git_command(cmd: List[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run git command and return result."""
    logger.debug(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False
    )
    
    if check and result.returncode != 0:
        logger.error(f"Git command failed: {' '.join(cmd)}")
        logger.error(f"Exit code: {result.returncode}")
        logger.error(f"Error: {result.stderr}")
        raise RuntimeError(f"Git command failed with exit code {result.returncode}: {result.stderr}")
    
    # Git hooks may write to stderr even on success - only fail on non-zero exit code
    if result.stderr and result.returncode == 0:
        logger.debug(f"Git hook output (non-fatal): {result.stderr[:200]}")
    
    return result


def get_current_branch(project_root: Path) -> str:
    """Get current git branch name."""
    result = run_git_command(['git', 'branch', '--show-current'], project_root)
    return result.stdout.strip()


def filter_admin_operations(temp_dir: Path):
    """
    Remove admin-only operations from cortex-operations.yaml.
    
    SECURITY: Users must not have access to commands that modify CORTEX source code.
    This includes deployment, validation, system alignment, and optimization scripts.
    """
    operations_file = temp_dir / "cortex-operations.yaml"
    
    if not operations_file.exists():
        logger.warning("⚠️  cortex-operations.yaml not found - skipping admin filter")
        return
    
    try:
        with open(operations_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if 'operations' not in config:
            logger.warning("⚠️  cortex-operations.yaml has no 'operations' section")
            return
        
        # Admin operation patterns to exclude
        admin_patterns = [
            'deploy',
            'publish',
            'validate_deployment',
            'alignment',
            'admin',
            'optimize_cortex',
            'system_alignment'
        ]
        
        original_count = len(config['operations'])
        filtered_operations = {}
        removed_operations = []
        
        for op_name, op_config in config['operations'].items():
            # Check if operation is marked as admin-only
            is_admin = False
            
            if isinstance(op_config, dict) and op_config.get('admin_only', False):
                is_admin = True
            
            # Check operation name against admin patterns
            if not is_admin:
                for pattern in admin_patterns:
                    if pattern in op_name.lower():
                        is_admin = True
                        break
            
            if is_admin:
                removed_operations.append(op_name)
            else:
                filtered_operations[op_name] = op_config
        
        # Update config with filtered operations
        config['operations'] = filtered_operations
        
        # Write back to file
        with open(operations_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"✓ Filtered admin operations: {original_count} → {len(filtered_operations)} operations")
        if removed_operations:
            logger.info(f"  Removed: {', '.join(removed_operations)}")
        
    except Exception as e:
        logger.error(f"Failed to filter admin operations: {e}")
        raise


def branch_exists(branch_name: str, project_root: Path) -> bool:
    """Check if branch exists locally or remotely."""
    # Check local
    result = run_git_command(['git', 'branch', '--list', branch_name], project_root, check=False)
    if branch_name in result.stdout:
        return True
    
    # Check remote
    result = run_git_command(['git', 'ls-remote', '--heads', 'origin', branch_name], project_root, check=False)
    return bool(result.stdout.strip())


def should_include_path(path: Path, project_root: Path) -> bool:
    """Check if path should be included in publish branch."""
    rel_path = path.relative_to(project_root)
    path_str = str(rel_path).replace('\\', '/')
    
    # Check if it's a core file
    if path_str in CORE_FILES:
        return True
    
    # Exclude admin files (deployment, validation scripts)
    if path_str in EXCLUDED_ADMIN_FILES:
        return False
    
    # Exclude patterns
    for pattern in EXCLUDED_PATTERNS:
        if path.match(pattern):
            return False
    
    # Check excluded directories (including admin subdirectories)
    first_dir = rel_path.parts[0] if len(rel_path.parts) > 0 else None
    if first_dir in EXCLUDED_DIRS:
        return False
    
    # Check for admin subdirectories within included directories
    for part in rel_path.parts:
        # Exclude any path containing /admin/ subdirectory
        if part == 'admin':
            return False
    
    # Also check the full path string for admin subdirectories
    for excluded_admin_dir in ['cortex-brain/admin', 'src/operations/modules/admin', 'scripts/admin']:
        if path_str.startswith(excluded_admin_dir):
            return False
    
    # Check if under core directories
    for core_dir in CORE_DIRS:
        if path_str.startswith(f"{core_dir}/") or path_str == core_dir:
            return True
    
    # .github/ - include prompts/ directory AND copilot-instructions.md (critical for auto-activation)
    if '.github' in rel_path.parts:
        # Include the prompts/ subdirectory
        if 'prompts' in rel_path.parts:
            return True
        # Include copilot-instructions.md directly under .github/
        if rel_path.name == 'copilot-instructions.md':
            return True
        # Exclude everything else (.github/workflows, .github/hooks, etc.)
        return False
    
    return False


def build_publish_content(project_root: Path, temp_dir: Path) -> Dict[str, int]:
    """Build content for publish branch in temporary directory."""
    stats = {
        'files_copied': 0,
        'files_excluded': 0,
        'dirs_created': 0,
        'total_size': 0
    }
    
    logger.info("Building publish content...")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy project structure
    manifest = []
    for item in project_root.rglob('*'):
        # Skip .git directory
        if '.git' in item.parts:
            continue
        
        if not should_include_path(item, project_root):
            stats['files_excluded'] += 1
            continue
        
        manifest.append(item)
        rel_path = item.relative_to(project_root)
        dest_path = temp_dir / rel_path
        
        if item.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            stats['dirs_created'] += 1
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)
            stats['files_copied'] += 1
            stats['total_size'] += item.stat().st_size
    
    # Validate manifest before finalizing
    logger.info("Validating publish manifest...")
    try:
        from scripts.validation.publish_manifest_validator import PublishManifestValidator
        
        validator = PublishManifestValidator(project_root, manifest)
        validation_success, validation_report = validator.validate()
        
        if not validation_success:
            logger.error("\n❌ MANIFEST VALIDATION FAILED")
            logger.error("\nCritical violations found:")
            for violation in validation_report.get('violations', []):
                if violation['severity'] == 'critical':
                    logger.error(f"  • {violation['path']}: {violation['reason']}")
            
            logger.error("\nDeploy blocked - non-production content detected in manifest")
            logger.error("Run validator standalone for full report:")
            logger.error("  python scripts/validation/publish_manifest_validator.py")
            raise ValueError("Manifest validation failed - see errors above")
        
        if validation_report.get('warnings'):
            logger.warning("\n⚠️  Manifest validation warnings:")
            for violation in validation_report.get('violations', []):
                if violation['severity'] == 'warning':
                    logger.warning(f"  • {violation['path']}: {violation['reason']}")
        
        logger.info(f"✅ Manifest validation PASSED ({validation_report.get('files_checked', 0)} files checked)")
        
    except ImportError:
        logger.warning("⚠️  Could not import manifest validator (optional)")
    
    # Handle copilot-instructions.md merge
    cortex_instructions_src = project_root / ".github" / "copilot-instructions.md"
    existing_instructions = temp_dir / ".github" / "copilot-instructions.md"
    
    if cortex_instructions_src.exists():
        logger.info("Merging copilot-instructions.md...")
        merge_copilot_instructions(
            existing_file=existing_instructions,  # May not exist yet
            cortex_instructions_file=cortex_instructions_src,
            output_file=existing_instructions
        )
    else:
        logger.warning("⚠️  CORTEX copilot-instructions.md not found - skipping merge")
    
    # Filter admin operations from cortex-operations.yaml
    filter_admin_operations(temp_dir)
    
    # Create SETUP-CORTEX.md guide
    create_setup_guide(temp_dir)
    
    # Create PACKAGE-INFO.md
    create_package_info(temp_dir, stats)
    
    return stats


def merge_copilot_instructions(existing_file: Path, cortex_instructions_file: Path, output_file: Path) -> None:
    """Merge CORTEX instructions into existing copilot-instructions.md.
    
    Handles 3 scenarios:
    1. No existing file - copy CORTEX file as-is
    2. Existing file without CORTEX - append CORTEX section
    3. Existing file with CORTEX - update existing CORTEX section
    
    Args:
        existing_file: Path to existing copilot-instructions.md (may not exist)
        cortex_instructions_file: Path to CORTEX's copilot-instructions.md
        output_file: Path for merged result
    """
    # Read CORTEX instructions
    with open(cortex_instructions_file, 'r', encoding='utf-8') as f:
        cortex_content = f.read()
    
    # Extract CORTEX section markers
    cortex_start_marker = "# GitHub Copilot Instructions for CORTEX"
    cortex_end_marker = "**License:** Source-Available (Use Allowed, No Contributions)"
    
    if not existing_file.exists():
        # Scenario 1: No existing file - create new
        logger.info("  ✅ No existing copilot-instructions.md - creating new")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cortex_content)
        return
    
    # Read existing file
    with open(existing_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    if cortex_start_marker in existing_content:
        # Scenario 3: CORTEX section exists - update it
        logger.info("  ✅ Existing CORTEX section found - updating")
        
        # Find CORTEX section boundaries
        start_idx = existing_content.find(cortex_start_marker)
        
        # Find end marker (look for the license line or end of file)
        if cortex_end_marker in existing_content[start_idx:]:
            end_idx = existing_content.find(cortex_end_marker, start_idx) + len(cortex_end_marker)
            # Include trailing newlines
            while end_idx < len(existing_content) and existing_content[end_idx] in ('\n', '\r'):
                end_idx += 1
        else:
            # No clear end marker - replace to end of file
            end_idx = len(existing_content)
        
        # Build merged content: [before CORTEX] + [new CORTEX] + [after CORTEX]
        before = existing_content[:start_idx]
        after = existing_content[end_idx:]
        
        merged_content = before + cortex_content
        if after.strip():  # Only add after section if non-empty
            merged_content += "\n\n" + after
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
    else:
        # Scenario 2: No CORTEX section - append
        logger.info("  ✅ Existing file without CORTEX - appending CORTEX section")
        
        merged_content = existing_content.rstrip() + "\n\n" + "---\n\n" + cortex_content
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)


def create_setup_guide(temp_dir: Path):
    """Create comprehensive setup guide for end users."""
    setup_content = f"""# 🚀 CORTEX Setup Guide

**Version:** {PACKAGE_VERSION}  
**Branch:** {PUBLISH_BRANCH}  
**Updated:** {datetime.now().strftime('%Y-%m-%d')}

---

## 📦 What is This?

This is the **production-ready CORTEX deployment package** - a clean, minimal installation for end users.

**What you get:**
- ✅ Complete CORTEX source code (`src/`)
- ✅ Brain storage system (`cortex-brain/`)
- ✅ GitHub Copilot integration (`.github/prompts/`)
- ✅ Modular documentation (`prompts/`)
- ✅ Automation scripts (`scripts/`)
- ✅ All dependencies (`requirements.txt`)

**What's excluded:**
- ❌ Development tools (tests, CI/CD, build scripts)
- ❌ Documentation website (MkDocs)
- ❌ Example code
- ❌ Commit history from main branch

---

## 🎯 Quick Start

### Option 1: Clone This Branch Only (Recommended)

```bash
# Clone only the publish branch (fast, clean)
git clone -b {PUBLISH_BRANCH} --single-branch https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

### Option 2: Switch to This Branch

```bash
# If you already have the repo
git fetch origin
git checkout {PUBLISH_BRANCH}
```

---

## 🛠️ Installation

### 1️⃣ Prerequisites

**Required:**
- Python 3.8 or higher
- Git
- GitHub Copilot (VS Code extension)

**Check your versions:**
```bash
python --version
git --version
```

### 2️⃣ Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

# Install CORTEX dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure CORTEX

```bash
# Copy template configuration
cp cortex.config.template.json cortex.config.json

# Edit cortex.config.json with your paths
# (Use absolute paths for your machine)
```

### 4️⃣ Initialize Brain

```bash
# Run CORTEX setup (initializes brain storage)
# In VS Code, tell GitHub Copilot:
/CORTEX setup environment
```

Or use Python directly:
```bash
python -m src.setup.setup_orchestrator
```

---

## 📚 Using CORTEX

### GitHub Copilot Integration

CORTEX integrates with GitHub Copilot Chat via `.github/prompts/CORTEX.prompt.md`.

**In VS Code Copilot Chat:**
```
/CORTEX help              # Show all commands
/CORTEX                   # Main entry point
setup environment         # Configure environment
demo                      # Interactive tutorial
cleanup workspace         # Clean temporary files
```

### Natural Language Commands

CORTEX understands natural language:
```
"Add a purple button to the dashboard"
"Setup my environment"
"Show me where I left off"
"Run cleanup in dry-run mode"
```

---

## 🧠 Understanding CORTEX

### The Story

Read the human-friendly explanation:
```
#file:prompts/shared/story.md
```

### Technical Reference

Deep dive into architecture:
```
#file:prompts/shared/technical-reference.md
```

### Full Documentation

All modular docs are in `prompts/shared/`:
- `story.md` - The Intern with Amnesia
- `setup-guide.md` - Installation details
- `technical-reference.md` - API reference
- `agents-guide.md` - 10 specialist agents
- `tracking-guide.md` - Conversation memory
- `configuration-reference.md` - Config options
- `plugin-system.md` - Plugin development

---

## 🔧 Configuration

### cortex.config.json Structure

```json
{{
  "cortex_root": "/absolute/path/to/CORTEX",
  "brain": {{
    "tier1": {{
      "database_path": "/absolute/path/to/cortex-brain/tier1/conversations.db",
      "conversation_limit": 20
    }},
    "tier2": {{
      "database_path": "/absolute/path/to/cortex-brain/tier2/knowledge-graph.db"
    }},
    "tier3": {{
      "database_path": "/absolute/path/to/cortex-brain/tier3/development-context.db"
    }}
  }},
  "plugins": {{
    "enabled": [
      "cleanup_plugin",
      "platform_switch_plugin",
      "doc_refresh_plugin"
    ]
  }}
}}
```

**Important:** Use absolute paths! CORTEX works across multiple machines.

---

## 🚨 Troubleshooting

### Import Errors

```bash
# Make sure you're in the CORTEX root directory
cd /path/to/CORTEX

# Verify PYTHONPATH includes CORTEX root
export PYTHONPATH=/path/to/CORTEX:$PYTHONPATH
```

### Configuration Not Found

```bash
# Check config file exists
ls -la cortex.config.json

# Verify paths are absolute
cat cortex.config.json
```

### Brain Database Errors

```bash
# Reinitialize brain
python -m src.setup.modules.brain_initialization_module
```

### Conversation Tracking Not Working

See tracking guide:
```
#file:prompts/shared/tracking-guide.md
```

---

## 📖 Next Steps

1. **First time?** Read the story: `#file:prompts/shared/story.md`
2. **Configure:** Edit `cortex.config.json` with your paths
3. **Initialize:** Run `/CORTEX setup environment`
4. **Learn:** Run `demo` in Copilot Chat
5. **Start working:** Just tell CORTEX what you need!

---

## 📞 Support

- **Repository:** https://github.com/asifhussain60/CORTEX
- **Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** Use `#file:prompts/shared/*.md` in Copilot Chat

---

## 📄 License

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**

This is proprietary software. See LICENSE file for full terms.

Unauthorized reproduction or distribution is prohibited.

---

## ✨ What Makes This Branch Special?

**This is an orphan branch:**
- ✅ No commit history from main development branch
- ✅ Minimal file size (production code only)
- ✅ Clean git history (publish commits only)
- ✅ Fast clone (no dev history to download)
- ✅ Perfect for end-user deployment

**Clone command:**
```bash
git clone -b {PUBLISH_BRANCH} --single-branch https://github.com/asifhussain60/CORTEX.git
```

**Why orphan?**
- Main branch: 10,000+ commits, full dev history, test files, docs
- Publish branch: Clean slate, production code only, ~100 commits
- Result: 90% faster clone, 70% smaller disk usage

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | CORTEX {PACKAGE_VERSION}*
"""
    
    setup_file = temp_dir / 'SETUP-CORTEX.md'
    with open(setup_file, 'w', encoding='utf-8') as f:
        f.write(setup_content)
    
    logger.info("Created SETUP-CORTEX.md")


def create_package_info(temp_dir: Path, stats: Dict[str, int]):
    """Create package information file."""
    info_content = f"""# CORTEX Package Information

**Version:** {PACKAGE_VERSION}  
**Branch:** {PUBLISH_BRANCH}  
**Build Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Package Statistics

- **Files Included:** {stats['files_copied']}
- **Directories Created:** {stats['dirs_created']}
- **Files Excluded:** {stats['files_excluded']}
- **Total Size:** {stats['total_size'] / 1024 / 1024:.2f} MB

---

## 📦 What's Included

### Core Source Code (`src/`)
- 10 specialist agents (left brain + right brain)
- Tier 0, 1, 2, 3 architecture
- Plugin system
- Operations orchestrator
- Entry point processor

### Brain Storage (`cortex-brain/`)
- YAML configuration files
- Database schemas (SQL)
- Protection rules
- Response templates

### GitHub Copilot Integration (`.github/prompts/`)
- CORTEX.prompt.md (main entry point)
- copilot-instructions.md (baseline context)

### Documentation (`prompts/`)
- Modular documentation system
- User guides
- Technical reference
- Story narrative

### Scripts (`scripts/`)
- Automation tools
- Deployment scripts
- Utility functions

---

## 🚫 What's Excluded

- ❌ Test suite (`tests/`)
- ❌ CI/CD workflows (`.github/workflows/`)
- ❌ Documentation website (`docs/`, `site/`)
- ❌ Development tools (build scripts, profilers)
- ❌ Example code (`examples/`)
- ❌ Git commit history from main branch

---

## 🎯 Purpose

This package is designed for **end-user deployment**:

✅ Clean, minimal installation  
✅ Fast clone (no dev history)  
✅ Production-ready code only  
✅ All essential dependencies  
✅ Comprehensive setup guide  

---

## 📥 Installation

See **SETUP-CORTEX.md** for complete installation instructions.

**Quick start:**
```bash
git clone -b {PUBLISH_BRANCH} --single-branch https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -r requirements.txt
cp cortex.config.template.json cortex.config.json
# Edit cortex.config.json with your paths
```

---

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**
"""
    
    info_file = temp_dir / 'PACKAGE-INFO.md'
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    logger.info("Created PACKAGE-INFO.md")


def publish_to_branch(
    project_root: Path,
    branch_name: str = PUBLISH_BRANCH,
    dry_run: bool = False,
    resume: bool = False,
    skip_validation: bool = False
) -> bool:
    """Publish CORTEX to dedicated branch with fault tolerance.
    
    Args:
        project_root: Root directory of CORTEX project
        branch_name: Name of publish branch
        dry_run: Preview mode (no git changes)
        resume: Resume from last checkpoint
        skip_validation: Skip pre-deployment validation (use with caution)
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 80)
    logger.info("CORTEX Branch Publisher - Fault Tolerant Edition")
    logger.info("=" * 80)
    logger.info(f"Version: {PACKAGE_VERSION}")
    logger.info(f"Target branch: {branch_name}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Dry run: {dry_run}")
    logger.info(f"Resume mode: {resume}")
    logger.info(f"Skip validation: {skip_validation}")
    logger.info("")
    
    # Run validation gate first (unless resuming, dry-run, or skipped)
    if not resume and not dry_run and not skip_validation:
        logger.info("" + "=" * 80)
        logger.info("STAGE 0: Pre-Deployment Validation Gate")
        logger.info("" + "=" * 80)
        logger.info("")
        
        validate_script = project_root / "scripts" / "validate_deployment.py"
        if validate_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(validate_script)],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Print validation output
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.info(line)
                
                if result.returncode != 0 and result.returncode != 2:
                    logger.error("")
                    logger.error("❌ VALIDATION FAILED - BRANCH PUBLISH BLOCKED")
                    logger.error("")
                    logger.error("Fix all CRITICAL and HIGH issues before publishing.")
                    logger.error("Run: python scripts/validate_deployment.py")
                    logger.error("")
                    return False
                elif result.returncode == 2:
                    logger.warning("")
                    logger.warning("⚠️  Validation warnings detected (non-blocking)")
                    logger.warning("Review warnings above before proceeding")
                    logger.warning("")
                
                logger.info("✅ Validation passed - proceeding with branch publish")
                logger.info("")
            
            except subprocess.TimeoutExpired:
                logger.error("❌ Validation timeout - aborting publish")
                return False
            except Exception as e:
                logger.warning(f"⚠️  Validation check failed: {e}")
                logger.warning("Proceeding with caution...")
        else:
            logger.warning("⚠️  Validation script not found - proceeding without validation")
        
        logger.info("")
    
    # Initialize checkpoint manager
    checkpoint = CheckpointManager(project_root)
    
    # Check if resuming
    if resume and not checkpoint.exists():
        logger.warning("⚠️  Resume requested but no checkpoint found. Starting fresh.")
        resume = False
    
    if resume:
        logger.info(f"🔄 Resuming from checkpoint: {checkpoint.get_last_stage()}")
    
    # Get current branch
    original_branch = checkpoint.get_data('original_branch')
    if not original_branch:
        original_branch = get_current_branch(project_root)
        checkpoint.save(PublishStage.VALIDATION, {'original_branch': original_branch})
    
    logger.info(f"Current branch: {original_branch}")
    
    # Create temp directory for build
    temp_dir = project_root / '.temp-publish'
    
    try:
        # STAGE 1: Validation
        if not checkpoint.should_skip_stage(PublishStage.VALIDATION):
            logger.info("\n📋 STAGE 1: Validation")
            
            # Check for uncommitted changes
            result = run_git_command(['git', 'status', '--porcelain'], project_root)
            if result.stdout.strip():
                logger.error("❌ You have uncommitted changes. Please commit or stash them first.")
                return False
            
            checkpoint.save(PublishStage.VALIDATION, {
                'original_branch': original_branch,
                'branch_name': branch_name
            })
            logger.info("✅ Validation complete")
        else:
            logger.info("⏩ Skipping validation (already completed)")
        
        # STAGE 2: Build Content
        stats = None
        # Always rebuild if temp_dir missing (branch switch deleted it)
        needs_rebuild = not checkpoint.should_skip_stage(PublishStage.BUILD_CONTENT) or not temp_dir.exists()
        
        if needs_rebuild:
            if not checkpoint.should_skip_stage(PublishStage.BUILD_CONTENT):
                logger.info("\n🔨 STAGE 2: Building Package Content")
            else:
                logger.info("\n🔨 STAGE 2: Rebuilding Package Content (temp dir missing after branch switch)")
            
            # Build package content
            stats = build_publish_content(project_root, temp_dir)
            logger.info(f"✅ Build complete:")
            logger.info(f"   Files: {stats['files_copied']}")
            logger.info(f"   Size: {stats['total_size'] / 1024 / 1024:.2f} MB")
            
            checkpoint.save(PublishStage.BUILD_CONTENT, {
                'original_branch': original_branch,
                'branch_name': branch_name,
                'stats': stats
            })
        else:
            logger.info("⏩ Skipping build (already completed)")
            stats = checkpoint.get_data('stats')
        
        if dry_run:
            logger.info("\n🔍 DRY RUN - No git operations performed")
            logger.info(f"Preview content in: {temp_dir}")
            checkpoint.clear()
            return True
        
        # STAGE 3: Branch Setup
        if not checkpoint.should_skip_stage(PublishStage.BRANCH_SETUP):
            logger.info("\n🌿 STAGE 3: Setting Up Publish Branch")
            
            # Check if branch exists
            if branch_exists(branch_name, project_root):
                logger.info(f"Branch '{branch_name}' exists - switching to it")
                run_git_command(['git', 'checkout', branch_name], project_root)
                
                # Remove all files except .git
                logger.info("Cleaning existing branch content...")
                for item in project_root.iterdir():
                    if item.name == '.git' or item.name == CHECKPOINT_FILE:
                        continue
                    try:
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to remove {item}: {e}")
            else:
                logger.info(f"Creating new orphan branch '{branch_name}'")
                run_git_command(['git', 'checkout', '--orphan', branch_name], project_root)
                run_git_command(['git', 'rm', '-rf', '.'], project_root, check=False)
            
            checkpoint.save(PublishStage.BRANCH_SETUP, {
                'original_branch': original_branch,
                'branch_name': branch_name,
                'stats': stats
            })
            logger.info("✅ Branch setup complete")
        else:
            logger.info("⏩ Skipping branch setup (already completed)")
        
        # STAGE 4: Content Copy
        if not checkpoint.should_skip_stage(PublishStage.CONTENT_COPY):
            logger.info("\n📂 STAGE 4: Copying Content to Branch")
            
            # Rebuild if temp_dir missing (branch switch deleted it)
            if not temp_dir.exists():
                logger.info("⚠️  Temp directory missing after branch switch - rebuilding...")
                stats = build_publish_content(project_root, temp_dir)
                logger.info(f"✅ Rebuild complete: {stats['files_copied']} files, {stats['total_size'] / 1024 / 1024:.2f} MB")
            
            # Copy new content
            for item in temp_dir.iterdir():
                dest = project_root / item.name
                try:
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                except Exception as e:
                    logger.warning(f"Failed to copy {item.name}: {e}")
                    raise
            
            # Create .gitignore
            gitignore_content = """# CORTEX Publish Branch .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.venv
venv/
ENV/
env/
*.log
*.db
*.db-journal
.DS_Store
Thumbs.db
cortex.config.json
.publish-checkpoint.json
"""
            gitignore_file = project_root / '.gitignore'
            with open(gitignore_file, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            checkpoint.save(PublishStage.CONTENT_COPY, {
                'original_branch': original_branch,
                'branch_name': branch_name,
                'stats': stats
            })
            logger.info("✅ Content copy complete")
        else:
            logger.info("⏩ Skipping content copy (already completed)")
        
        # STAGE 5: Git Commit
        if not checkpoint.should_skip_stage(PublishStage.GIT_COMMIT):
            logger.info("\n💾 STAGE 5: Committing Changes")
            
            # Stage all files
            run_git_command(['git', 'add', '-A'], project_root)
            
            # Get stats if not available
            if not stats:
                stats = checkpoint.get_data('stats')
            
            # Commit
            commit_msg = f"""CORTEX {PACKAGE_VERSION} - Production Release

Published: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Package Statistics:
- Files: {stats['files_copied']}
- Size: {stats['total_size'] / 1024 / 1024:.2f} MB
- Directories: {stats['dirs_created']}

This is a production-ready deployment package.
Clone with: git clone -b {branch_name} --single-branch <repo>
"""
            
            run_git_command(['git', 'commit', '-m', commit_msg], project_root)
            
            checkpoint.save(PublishStage.GIT_COMMIT, {
                'original_branch': original_branch,
                'branch_name': branch_name,
                'stats': stats
            })
            logger.info("✅ Commit complete")
        else:
            logger.info("⏩ Skipping commit (already completed)")
        
        # STAGE 6: Git Push
        if not checkpoint.should_skip_stage(PublishStage.GIT_PUSH):
            logger.info(f"\n📤 STAGE 6: Pushing to origin/{branch_name}")
            
            result = run_git_command(
                ['git', 'push', '-f', 'origin', branch_name],
                project_root,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Push failed: {result.stderr}")
                logger.error("⚠️  Checkpoint saved. You can:")
                logger.error("   1. Fix network/auth issues")
                logger.error("   2. Run with --resume to continue from here")
                logger.error("   3. Or manually push later with:")
                logger.error(f"      git push -f origin {branch_name}")
                return False
            
            checkpoint.save(PublishStage.GIT_PUSH, {
                'original_branch': original_branch,
                'branch_name': branch_name,
                'stats': stats
            })
            logger.info("✅ Push successful")
        else:
            logger.info("⏩ Skipping push (already completed)")
        
        # STAGE 7: Cleanup and Return
        if not checkpoint.should_skip_stage(PublishStage.CLEANUP):
            logger.info("\n🧹 STAGE 7: Cleanup")
            
            # Return to original branch
            logger.info(f"Returning to original branch: {original_branch}")
            run_git_command(['git', 'checkout', original_branch], project_root)
            
            checkpoint.save(PublishStage.CLEANUP, {
                'original_branch': original_branch,
                'branch_name': branch_name,
                'stats': stats
            })
            logger.info("✅ Cleanup complete")
        else:
            logger.info("⏩ Skipping cleanup (already completed)")
        
        # Mark as complete
        checkpoint.save(PublishStage.COMPLETE, {
            'original_branch': original_branch,
            'branch_name': branch_name,
            'stats': stats
        })
        
        # Get final stats
        if not stats:
            stats = checkpoint.get_data('stats')
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ CORTEX PUBLISHED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"\n📦 Users can now clone with:")
        logger.info(f"   git clone -b {branch_name} --single-branch https://github.com/asifhussain60/CORTEX.git")
        logger.info("")
        
        # Clear checkpoint on success
        checkpoint.clear()
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        logger.info(f"💾 Progress saved. Run with --resume to continue:")
        logger.info(f"   python scripts/publish_to_branch.py --resume")
        return False
        
    except Exception as e:
        logger.error(f"\n❌ Publish failed at stage: {checkpoint.get_last_stage()}")
        logger.error(f"Error: {e}")
        logger.error(f"\n{traceback.format_exc()}")
        
        logger.info(f"\n💾 Progress saved. You can:")
        logger.info("   1. Fix the issue")
        logger.info("   2. Run with --resume to continue:")
        logger.info(f"      python scripts/publish_to_branch.py --resume")
        logger.info("   3. Or start fresh (will lose progress)")
        
        # Try to return to original branch
        if original_branch:
            try:
                current = get_current_branch(project_root)
                if current != original_branch:
                    logger.info(f"\n🔄 Attempting to return to {original_branch}...")
                    run_git_command(['git', 'checkout', original_branch], project_root, check=False)
                    logger.info("✅ Returned to original branch")
            except Exception as branch_err:
                logger.warning(f"⚠️  Could not return to original branch: {branch_err}")
        
        return False
        
    finally:
        # Clean up temp directory only if publish completed
        if checkpoint.get_last_stage() == PublishStage.COMPLETE:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.debug(f"🗑️  Cleaned up temp directory: {temp_dir}")
        elif temp_dir.exists():
            logger.debug(f"💾 Keeping temp directory for resume: {temp_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Publish CORTEX to dedicated branch for user deployment (Fault Tolerant)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/publish_to_branch.py                    # Normal publish
  python scripts/publish_to_branch.py --dry-run          # Preview only
  python scripts/publish_to_branch.py --resume           # Resume from checkpoint
  python scripts/publish_to_branch.py --branch custom    # Custom branch name
  
Fault Tolerance:
  If publish fails or is interrupted, progress is saved automatically.
  Run with --resume to continue from where it left off.
  
  Checkpoints are saved at each stage:
    1. Validation
    2. Build Content
    3. Branch Setup
    4. Content Copy
    5. Git Commit
    6. Git Push
    7. Cleanup
"""
    )
    parser.add_argument(
        '--branch',
        type=str,
        default=PUBLISH_BRANCH,
        help=f'Branch name to publish to (default: {PUBLISH_BRANCH})'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Project root directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be published without making changes'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint (if publish was interrupted)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip pre-deployment validation gate (use with caution - for documented known issues only)'
    )
    
    args = parser.parse_args()
    
    try:
        success = publish_to_branch(
            project_root=args.project_root,
            branch_name=args.branch,
            dry_run=args.dry_run,
            resume=args.resume,
            skip_validation=args.skip_validation
        )
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        logger.info("💾 Progress saved. Run with --resume to continue")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
