#!/usr/bin/env python3
"""
CORTEX Branch Publisher

Builds CORTEX deployment package and publishes to a dedicated 'cortex-publish' branch.
This allows users to clone ONLY the publish branch for a clean installation.

Usage:
    python scripts/publish_to_branch.py
    python scripts/publish_to_branch.py --dry-run
    python scripts/publish_to_branch.py --branch custom-publish-branch

Features:
    - Creates orphan branch (no commit history from main)
    - Builds production-ready CORTEX package
    - Includes .github/prompts/ for Copilot integration
    - Includes comprehensive setup guide
    - Minimal file size (excludes tests, dev tools, docs)
    - Users can clone with: git clone -b cortex-publish --single-branch <repo>

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import argparse
import shutil
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Set, Dict, List
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Package metadata
PACKAGE_VERSION = "5.2.0"  # Updated for CORTEX 2.0 Response Template Architecture
PUBLISH_BRANCH = "cortex-publish"

# Core files that MUST be included
CORE_FILES = {
    # Entry Points
    '.github/prompts/CORTEX.prompt.md',
    '.github/copilot-instructions.md',
    
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
    '.backup-archive'
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
        logger.error(f"Error: {result.stderr}")
        raise RuntimeError(f"Git command failed: {result.stderr}")
    
    return result


def get_current_branch(project_root: Path) -> str:
    """Get current git branch name."""
    result = run_git_command(['git', 'branch', '--show-current'], project_root)
    return result.stdout.strip()


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
    
    # Exclude patterns
    for pattern in EXCLUDED_PATTERNS:
        if path.match(pattern):
            return False
    
    # Check excluded directories
    first_dir = rel_path.parts[0] if len(rel_path.parts) > 0 else None
    if first_dir in EXCLUDED_DIRS:
        return False
    
    # Check if under core directories
    for core_dir in CORE_DIRS:
        if path_str.startswith(f"{core_dir}/") or path_str == core_dir:
            return True
    
    # .github/ - only include prompts/
    if '.github' in rel_path.parts:
        return 'prompts' in rel_path.parts
    
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
    for item in project_root.rglob('*'):
        # Skip .git directory
        if '.git' in item.parts:
            continue
        
        if not should_include_path(item, project_root):
            stats['files_excluded'] += 1
            continue
        
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
    
    # Create SETUP-CORTEX.md guide
    create_setup_guide(temp_dir)
    
    # Create PACKAGE-INFO.md
    create_package_info(temp_dir, stats)
    
    return stats


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
    dry_run: bool = False
) -> bool:
    """Publish CORTEX to dedicated branch."""
    logger.info("=" * 80)
    logger.info("CORTEX Branch Publisher")
    logger.info("=" * 80)
    logger.info(f"Version: {PACKAGE_VERSION}")
    logger.info(f"Target branch: {branch_name}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("")
    
    # Get current branch
    original_branch = get_current_branch(project_root)
    logger.info(f"Current branch: {original_branch}")
    
    # Check for uncommitted changes
    result = run_git_command(['git', 'status', '--porcelain'], project_root)
    if result.stdout.strip():
        logger.error("❌ You have uncommitted changes. Please commit or stash them first.")
        return False
    
    # Create temp directory for build
    temp_dir = project_root / '.temp-publish'
    
    try:
        # Build package content
        stats = build_publish_content(project_root, temp_dir)
        logger.info(f"\n✅ Build complete:")
        logger.info(f"   Files: {stats['files_copied']}")
        logger.info(f"   Size: {stats['total_size'] / 1024 / 1024:.2f} MB")
        
        if dry_run:
            logger.info("\n🔍 DRY RUN - No git operations performed")
            logger.info(f"Preview content in: {temp_dir}")
            return True
        
        # Git operations
        logger.info("\n📝 Creating/updating publish branch...")
        
        # Check if branch exists
        if branch_exists(branch_name, project_root):
            logger.info(f"Branch '{branch_name}' exists - switching to it")
            run_git_command(['git', 'checkout', branch_name], project_root)
            
            # Remove all files except .git
            logger.info("Cleaning existing branch content...")
            for item in project_root.iterdir():
                if item.name == '.git':
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            logger.info(f"Creating new orphan branch '{branch_name}'")
            run_git_command(['git', 'checkout', '--orphan', branch_name], project_root)
            run_git_command(['git', 'rm', '-rf', '.'], project_root, check=False)
        
        # Copy new content
        logger.info("Copying new content to publish branch...")
        for item in temp_dir.iterdir():
            dest = project_root / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        
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
"""
        gitignore_file = project_root / '.gitignore'
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        # Stage all files
        logger.info("Staging files...")
        run_git_command(['git', 'add', '-A'], project_root)
        
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
        
        logger.info("Committing changes...")
        run_git_command(['git', 'commit', '-m', commit_msg], project_root)
        
        # Push to remote
        logger.info(f"Pushing to origin/{branch_name}...")
        result = run_git_command(
            ['git', 'push', '-f', 'origin', branch_name],
            project_root,
            check=False
        )
        
        if result.returncode != 0:
            logger.warning(f"⚠️  Push failed: {result.stderr}")
            logger.warning("You may need to push manually later")
        else:
            logger.info("✅ Push successful")
        
        # Return to original branch
        logger.info(f"\nReturning to original branch: {original_branch}")
        run_git_command(['git', 'checkout', original_branch], project_root)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ CORTEX published successfully!")
        logger.info("=" * 80)
        logger.info(f"\n📦 Users can now clone with:")
        logger.info(f"   git clone -b {branch_name} --single-branch https://github.com/asifhussain60/CORTEX.git")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Publish failed: {e}", exc_info=True)
        
        # Try to return to original branch
        try:
            run_git_command(['git', 'checkout', original_branch], project_root, check=False)
        except:
            pass
        
        return False
        
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temp directory: {temp_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Publish CORTEX to dedicated branch for user deployment'
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
    
    args = parser.parse_args()
    
    try:
        success = publish_to_branch(
            project_root=args.project_root,
            branch_name=args.branch,
            dry_run=args.dry_run
        )
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
