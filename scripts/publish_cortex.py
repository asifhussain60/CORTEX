#!/usr/bin/env python3
"""
CORTEX Simplified Publish Script

Creates a clean publish/CORTEX folder ready for manual copying to target applications.
Includes ONLY user-facing operations, excludes admin tools and development artifacts.

Usage:
    python scripts/publish_cortex.py
    python scripts/publish_cortex.py --dry-run

Key Differences from build_user_deployment.py:
- Simpler: Just copies to publish/ folder (no compression, no dist/)
- User operations only: Excludes design_sync, interactive_planning (admin)
- Manual deployment: User copies publish/CORTEX to their app manually
- Ultra-simple setup: SETUP-FOR-COPILOT.md is one-line instruction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import shutil
import yaml
import json
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Set, List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

VERSION = "2.0.0"

# User-facing operations (INCLUDE in publish package)
USER_OPERATIONS = {
    'environment_setup',
    'workspace_cleanup',
    'cortex_demo',
    'cortex_tutorial',
    'application_onboarding'  # NEW: Intelligent onboarding
}

# Admin-only operations (EXCLUDE from publish package)
ADMIN_OPERATIONS = {
    'design_sync',           # Admin development tool
    'interactive_planning',  # Not yet implemented
    'refresh_cortex_story'   # ❌ Admin-only: Updates CORTEX's own story documentation
}

# Patterns to EXCLUDE from publish (privacy & unnecessary files)
EXCLUDE_PATTERNS = {
    # Privacy: Machine-specific files with usernames/hostnames
    '**/.coverage.*',           # Coverage files with machine names (e.g., .coverage.AHHOME.12345)
    '**/coverage.*.xml',        # XML coverage reports with paths
    
    # Logs (contain machine-specific paths and timestamps)
    '**/logs/**',
    '**/*.log',
    
    # Health reports (development diagnostics only)
    '**/health-reports/**',
    
    # Test artifacts
    '**/__pycache__/**',
    '**/*.pyc',
    '**/*.pyo',
    '**/.pytest_cache/**',
    
    # Development documentation (not for end users)  - contains machine-specific paths
    '**/PHASE-*.md',            # Phase summaries
    '**/SESSION-[0-9]*.md',     # Session notes (not session-loader.md)
    '**/COVERAGE-*.md',         # Coverage analysis
    '**/CLEANUP-*.md',          # Cleanup reports
    '**/HOLISTIC-*.md',         # Review docs with machine paths
    '**/MACOS-*.md',            # Platform-specific docs with paths
    '**/NEXT-*.md',             # Next session planning
    '**/HARDCODED-*.md',        # Implementation docs
    
    # Simulations (development testing only)
    '**/simulations/**',
    
    # Version control
    '**/.git/**',
    '**/.gitignore',
    
    # IDE files
    '**/.vscode/**',
    '**/.idea/**',
    
    # Build artifacts
    '**/dist/**',
    '**/build/**',
    '**/*.egg-info/**',
}

# Critical files that MUST be included
CRITICAL_FILES = {
    # Brain Protection (Tier 0)
    'cortex-brain/brain-protection-rules.yaml',
    
    # Publish Configuration (CORTEX 3.0)
    'cortex-brain/publish-config.yaml',
    
    # Database Schema Code (Python-based initialization)
    'src/tier2/knowledge_graph/database/schema.py',
    'cortex-brain/migrate_brain_db.py',
    
    # CORTEX Entry Points
    '.github/prompts/CORTEX.prompt.md',
    
    # Core Configuration (TEMPLATE ONLY - not cortex.config.json with machine paths)
    'cortex.config.template.json',
    'cortex-operations.yaml',
    'requirements.txt',
    
    # User Documentation (essential only)
    'prompts/shared/story.md',
    'prompts/shared/setup-guide.md',
    'prompts/shared/tracking-guide.md',
    'prompts/shared/technical-reference.md',
    'prompts/shared/agents-guide.md',
    'prompts/shared/configuration-reference.md',
    'prompts/shared/plugin-system.md',
    'prompts/shared/operations-reference.md',
    
    # Response Templates (NEW - 2025-11-12: 13 intelligent question routing templates)
    'cortex-brain/response-templates.yaml',
    
    # User Tools (ESSENTIAL for conversation tracking & setup)
    'scripts/cortex/cortex_cli.py',  # Manual tracking
    'scripts/cortex/migrate-all-tiers.py',  # Database setup
    'scripts/launchers/run-cortex.sh',  # Unix/Mac setup
    
    # Legal & README
    'README.md',
    'LICENSE'
}

# Directories to include (allowlist)
INCLUDED_DIRS = {
    'src/tier0',
    'src/tier1',
    'src/tier2',
    'src/tier3',
    'src/cortex_agents',
    'src/operations',
    'src/plugins',
    'src/workflows',
    '.github/prompts',
    '.github',
    'cortex-brain/schemas',
    'prompts/shared'
}

# Directories to EXCLUDE completely
# ADMIN CONTENT EXCLUSIONS (CORTEX 3.0):
# - docs/ → Contains ALL admin documentation including:
#   - docs/images/system-design-prompts/ → Image generation prompts (admin tool)
#   - docs/images/system-design-prompts/narrative/ → PR narratives (admin workflow)
#   - Architecture diagrams, technical specs, development guides
# - cortex-brain/admin/ → Admin-only scripts and tools (NEW: documentation orchestrator)
# - cortex-brain/cortex-2.0-design/ → Design documents (admin planning)
# - cortex-brain/archives/ → Historical records (admin reference)
# - cortex-brain/simulations/ → Development testing data
# - scripts/ → Admin automation tools (except essential user scripts copied separately)
# - tests/ → Test suite (admin quality assurance)
# - workflow_checkpoints/ → Development state tracking
EXCLUDED_DIRS = {
    'tests',
    'workflow_checkpoints',
    'docs',  # ⭐ ADMIN CONTENT: All documentation, image prompts, narratives
    'cortex-brain/admin',  # ⭐ ADMIN-ONLY: Documentation orchestrator, admin scripts (NEW)
    'cortex-brain/cortex-2.0-design',  # Design docs (admin only)
    'cortex-brain/archives',
    'cortex-brain/simulations',  # Dev-only simulation data
    'scripts',  # Admin scripts (essential user tools copied separately below)
    'dist',
    'build',
    '.venv',
    'venv',
    '__pycache__',
    '.pytest_cache',
    '.git',
    'node_modules',
    'publish',  # Don't copy publish into itself!
    'archives'  # Exclude any 'archives' subdirectories (e.g., src/plugins/archives)
}

# Specific files to EXCLUDE (privacy leaks)
EXCLUDED_FILES = {
    'cortex.config.json',  # Contains machine-specific paths (AHHOME, /Users/asifhussain)
    'cortex.config.example.json',  # Same issue
    '.platform_state.json',  # Machine-specific state
    'NOOR-CANVAS-SETUP-SIMULATION.md',  # Dev simulation doc
    
    # Root-level dev/status files (not for end users)
    'ALPHA-READY-SUMMARY.md',
    'ALPHA-TESTER-GUIDE.md',
    'CHANGELOG.md',
    'KNOWN-ISSUES.md',
    'PHASE-2.1-COMPLETION-SUMMARY.md',
    'TEST-COVERAGE-IMPROVEMENT-REPORT.md',
    'package.json',  # Dev dependency (not needed for Python deployment)
    'tsconfig.json',  # TypeScript config (not needed)
    'mkdocs.yml',  # Docs build config (not needed)
    'pytest.ini',  # Test config (included in source, not needed at root)
}

# Admin scripts to EXCLUDE
ADMIN_SCRIPTS = {
    'sync_plugin_commands.py',
    'update_operations_status.py',
    'measure_token_reduction.py',
    'design_sync_orchestrator.py',
    'system_refactor_plugin.py'
}


def print_header():
    """Print publish header."""
    logger.info("=" * 80)
    logger.info("CORTEX Simplified Publish")
    logger.info("=" * 80)
    logger.info(f"Version: {VERSION}")
    logger.info(f"Author: Asif Hussain")
    logger.info(f"Copyright: © 2024-2025 Asif Hussain. All rights reserved.")
    logger.info("=" * 80)
    logger.info("")


def clear_publish_folder(publish_root: Path, dry_run: bool = False) -> bool:
    """
    Clear publish/ folder completely.
    
    Args:
        publish_root: Path to publish/ directory
        dry_run: If True, only preview changes
    
    Returns:
        True if successful
    """
    logger.info("Step 1/5: Clearing publish folder...")
    
    if not publish_root.exists():
        logger.info(f"Publish folder doesn't exist yet: {publish_root}")
        return True
    
    if dry_run:
        logger.info(f"[DRY RUN] Would delete all contents of: {publish_root}")
        return True
    
    try:
        # Remove entire directory and recreate
        shutil.rmtree(publish_root)
        publish_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Cleared publish folder: {publish_root}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear publish folder: {e}")
        return False


def filter_operations_by_tier(source_root: Path) -> Dict[str, Set[str]]:
    """
    Load cortex-operations.yaml and categorize operations by deployment tier.
    Also loads publish-config.yaml for CORTEX 3.0 admin/user separation.
    
    Returns:
        Dict with 'user' and 'admin' operation sets
    """
    logger.info("Loading operation definitions...")
    
    # Try loading from publish-config.yaml first (CORTEX 3.0)
    publish_config_file = source_root / 'cortex-brain' / 'publish-config.yaml'
    if publish_config_file.exists():
        try:
            with open(publish_config_file, 'r', encoding='utf-8') as f:
                publish_config = yaml.safe_load(f)
            
            user_ops = set(publish_config.get('user_content_patterns', {}).get('user_operations', []))
            admin_ops = set(publish_config.get('admin_content_patterns', {}).get('admin_operations', []))
            
            if user_ops or admin_ops:
                logger.info(f"✓ Loaded from publish-config.yaml: {len(user_ops)} user ops, {len(admin_ops)} admin ops")
                return {'user': user_ops, 'admin': admin_ops}
        except Exception as e:
            logger.warning(f"Failed to parse publish-config.yaml: {e}. Trying cortex-operations.yaml...")
    
    # Fallback to cortex-operations.yaml
    ops_file = source_root / 'cortex-operations.yaml'
    if not ops_file.exists():
        logger.warning(f"Operations file not found: {ops_file}")
        return {'user': USER_OPERATIONS, 'admin': ADMIN_OPERATIONS}
    
    try:
        with open(ops_file, 'r', encoding='utf-8') as f:
            ops_data = yaml.safe_load(f)
        
        user_ops = set()
        admin_ops = set()
        
        operations = ops_data.get('operations', {})
        for op_id, op_config in operations.items():
            tier = op_config.get('deployment_tier', 'user')  # Default to user
            
            if tier == 'admin':
                admin_ops.add(op_id)
            else:
                user_ops.add(op_id)
        
        logger.info(f"✓ Loaded from cortex-operations.yaml: {len(user_ops)} user ops, {len(admin_ops)} admin ops")
        return {'user': user_ops, 'admin': admin_ops}
    
    except Exception as e:
        logger.warning(f"Failed to parse operations file: {e}. Using defaults.")
        return {'user': USER_OPERATIONS, 'admin': ADMIN_OPERATIONS}


def should_include_file(file_path: Path, source_root: Path, admin_ops: Set[str]) -> bool:
    """
    Determine if a file should be included in publish package.
    
    Args:
        file_path: File to check
        source_root: CORTEX source root
        admin_ops: Set of admin operation IDs
    
    Returns:
        True if file should be included
    """
    from pathlib import PurePath
    
    relative_path = file_path.relative_to(source_root)
    relative_str = str(relative_path).replace('\\', '/')
    
    # Check EXCLUDED_FILES (specific filenames to skip)
    if file_path.name in EXCLUDED_FILES:
        return False
    
    # Check EXCLUDE_PATTERNS (privacy & unnecessary files)
    for pattern in EXCLUDE_PATTERNS:
        # Handle different pattern types
        if pattern.startswith('**/'):
            # Directory-level pattern like **/logs/**
            check_pattern = pattern[3:]  # Remove **/ prefix
            if check_pattern.endswith('/**'):
                # Match directory
                dir_name = check_pattern[:-3]
                if f'/{dir_name}/' in f'/{relative_str}/' or relative_str.startswith(f'{dir_name}/'):
                    return False
            elif check_pattern.startswith('.'):
                # Hidden file pattern like **/.coverage.*
                if file_path.name.startswith(check_pattern.rstrip('*')):
                    return False
            elif '*' in check_pattern:
                # Wildcard pattern like *.log
                if PurePath(file_path.name).match(check_pattern):
                    return False
        elif pattern.endswith('/**'):
            # Top-level directory pattern like logs/**
            dir_name = pattern[:-3]
            if relative_str.startswith(f'{dir_name}/'):
                return False
    
    # Check excluded directories
    for excluded_dir in EXCLUDED_DIRS:
        if relative_str.startswith(excluded_dir):
            return False
        # Also check if 'archives' appears anywhere in the path (e.g., src/plugins/archives)
        if 'archives' in relative_str.split('/'):
            return False
    
    # Exclude admin scripts
    if file_path.name in ADMIN_SCRIPTS:
        return False
    
    # Exclude admin operation modules
    for admin_op in admin_ops:
        if admin_op in file_path.name.lower():
            return False
    
    return True


def copy_essential_directories(
    source_root: Path,
    publish_cortex: Path,
    admin_ops: Set[str],
    dry_run: bool = False
) -> bool:
    """
    Copy ONLY essential directories needed for CORTEX operation.
    Much simpler than exclusion-based approach!
    
    Args:
        source_root: CORTEX source root
        publish_cortex: publish/CORTEX directory
        admin_ops: Set of admin operation IDs to exclude
        dry_run: If True, only preview changes
    
    Returns:
        True if successful
    """
    logger.info("Step 2/5: Copying essential CORTEX directories...")
    
    # Essential directories to include (ONLY what CORTEX needs)
    essential_dirs = [
        # Core Intelligence (Tier 0-3)
        'src/tier0',
        'src/tier1',
        'src/tier2',
        'src/tier3',
        
        # 10 Specialist Agents
        'src/cortex_agents',
        
        # Operations Framework
        'src/operations',
        
        # Plugin System
        'src/plugins',
        
        # Workflows
        'src/workflows',
        
        # Core Utilities
        'src/core',
        'src/utils',
        'src/brain',
        'src/crawlers',
        'src/llm',
        'src/response_templates',
        'src/setup',
        'src/entry_point',
        'src/migrations',
        
        # Entry Points & Configuration
        '.github',
        
        # User Documentation
        'prompts/shared',
        
        # User Tools & Scripts (ESSENTIAL for users)
        # Note: We copy scripts/ selectively below
        
        # Brain Files (YAML configs, templates)
        # Note: We'll copy cortex-brain/ selectively below
    ]
    
    if dry_run:
        logger.info("[DRY RUN] Would copy essential directories")
        return True
    
    copied_count = 0
    
    # Copy essential directories
    for dir_path in essential_dirs:
        source_dir = source_root / dir_path
        if not source_dir.exists():
            logger.warning(f"Essential directory not found: {dir_path}")
            continue
        
        target_dir = publish_cortex / dir_path
        
        # Copy entire directory tree, excluding admin operations and dev artifacts
        for item in source_dir.rglob('*'):
            if item.is_file():
                # Skip patterns
                if any([
                    '__pycache__' in str(item),
                    '.pyc' in item.suffix,
                    '.pyo' in item.suffix,
                    '.log' in item.suffix,
                    '.coverage' in item.name,
                    item.name.startswith('.pytest'),
                    'archives' in item.parts,  # Skip any file in an 'archives' directory
                ]):
                    continue
                
                # Skip admin operations
                skip_admin = False
                for admin_op in admin_ops:
                    if admin_op in str(item):
                        skip_admin = True
                        break
                if skip_admin:
                    continue
                
                # Copy file
                relative_path = item.relative_to(source_root)
                target_path = publish_cortex / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(item, target_path)
                    copied_count += 1
                except Exception as e:
                    logger.warning(f"Failed to copy {item}: {e}")
    
    # Copy cortex-brain/ files selectively (YAML configs only, no dev docs)
    cortex_brain_files = [
        'cortex-brain/brain-protection-rules.yaml',
        'cortex-brain/response-templates.yaml',
        'cortex-brain/knowledge-graph.yaml',
        'cortex-brain/development-context.yaml',
        'cortex-brain/capabilities.yaml',
        'cortex-brain/migrate_brain_db.py',
    ]
    
    for brain_file in cortex_brain_files:
        source_file = source_root / brain_file
        if source_file.exists():
            target_file = publish_cortex / brain_file
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            copied_count += 1
    
    # Copy essential user scripts/tools
    essential_scripts = [
        # Git Event Capture (tracking helper)
        'scripts/cortex/capture_git_event.py',
        
        # CLI Tools (manual conversation tracking)
        'scripts/cortex/cortex_cli.py',
        
        # Migration Scripts (database setup)
        'scripts/cortex/migrate-all-tiers.py',
        'scripts/cortex/migrate-tier1-to-sqlite.py',
        'scripts/cortex/migrate-tier2-to-sqlite.py',
        'scripts/cortex/migrate-tier3-to-sqlite.py',
        'scripts/cortex/validate-migrations.py',
        
        # Setup Scripts (easy installation)
        'setup-cortex-alpha.ps1',  # Windows
        'scripts/launchers/run-cortex.sh',  # Unix/Mac
    ]
    
    for script_file in essential_scripts:
        source_file = source_root / script_file
        if source_file.exists():
            target_file = publish_cortex / script_file
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            copied_count += 1
            logger.info(f"✓ Included user tool: {script_file}")
    
    # Copy example workflows (helpful for learning)
    workflows_dir = source_root / 'workflows'
    if workflows_dir.exists():
        target_workflows = publish_cortex / 'workflows'
        target_workflows.mkdir(parents=True, exist_ok=True)
        for workflow_file in workflows_dir.glob('*.yaml'):
            shutil.copy2(workflow_file, target_workflows / workflow_file.name)
            copied_count += 1
    
    # Exclude specific files with privacy leaks (example paths in documentation)
    privacy_leak_files = [
        '.github/CORTEX 2.0.md',  # Contains D:\\ and /Users/asif paths  
        '.github/CopilotChats.md',  # Contains AHHOME, D:\PROJECTS paths
        'src/migrations/README.md',  # Contains /Users/asifhussain
        'prompts/shared/test',  # Test excerpts with example paths
    ]
    
    # Remove any copied files that contain privacy leaks
    for leak_file in privacy_leak_files:
        target_file = publish_cortex / leak_file
        if target_file.exists():
            if target_file.is_dir():
                shutil.rmtree(target_file)
            else:
                target_file.unlink()
            logger.info(f"✓ Excluded privacy leak: {leak_file}")
    
    logger.info(f"✓ Copied {copied_count} essential files")
    return True


def copy_critical_files(
    source_root: Path,
    publish_cortex: Path,
    dry_run: bool = False
) -> bool:
    """
    Ensure all critical files are present in publish package.
    
    Args:
        source_root: CORTEX source root
        publish_cortex: publish/CORTEX directory
        dry_run: If True, only preview changes
    
    Returns:
        True if successful
    """
    logger.info("Step 3/5: Verifying critical files...")
    
    missing_files = []
    
    for critical_file in CRITICAL_FILES:
        source_file = source_root / critical_file
        target_file = publish_cortex / critical_file
        
        if not source_file.exists():
            logger.warning(f"Critical file not found in source: {critical_file}")
            missing_files.append(critical_file)
            continue
        
        if not target_file.exists():
            if dry_run:
                logger.info(f"[DRY RUN] Would copy critical file: {critical_file}")
            else:
                # Ensure directory exists
                target_file.parent.mkdir(parents=True, exist_ok=True)
                # Copy file
                try:
                    shutil.copy2(source_file, target_file)
                    logger.info(f"✓ Copied critical file: {critical_file}")
                except Exception as e:
                    logger.error(f"Failed to copy critical file {critical_file}: {e}")
                    missing_files.append(critical_file)
    
    if missing_files:
        logger.error(f"Missing {len(missing_files)} critical files!")
        return False
    
    logger.info(f"✓ All {len(CRITICAL_FILES)} critical files present")
    return True


def create_setup_for_copilot(
    publish_cortex: Path,
    dry_run: bool = False
) -> bool:
    """
    Create ultra-simple SETUP-FOR-COPILOT.md INSIDE publish/CORTEX folder.
    
    Args:
        publish_cortex: Path to publish/CORTEX directory
        dry_run: If True, only preview changes
    
    Returns:
        True if successful
    """
    logger.info("Step 4/5: Creating SETUP-FOR-COPILOT.md...")
    
    setup_content = """# CORTEX Setup for Your Application

## ⚡ Quick Start (One Command!)

### Step 1: Copy CORTEX to Your Project

**Copy this entire CORTEX folder to your application:**

```bash
# Navigate to your application
cd /path/to/your/application

# Copy CORTEX folder (creates your-app/cortex/)
cp -r /path/to/CORTEX ./cortex
```

**Result:** CORTEX now lives in `your-app/cortex/` (self-contained, ready to go!)

---

### Step 2: Open VS Code & Onboard

**Open your application in VS Code, then in Copilot Chat:**

```
onboard this application
```

**That's it!** CORTEX will:

1. ✅ Copy entry points from `cortex/.github/` to your app's `.github/` folder
2. ✅ Install required tooling (Python, Vision API, etc.)
3. ✅ Initialize brain databases (Tier 1, 2, 3)
4. ✅ Crawl and index your codebase
5. ✅ Analyze your project structure and tech stack
6. ✅ Ask intelligent questions about improvements:
   - "I see React but no test files - shall I help set up Jest + React Testing Library?"
   - "You have ESLint configured but not running on commit - want me to add pre-commit hooks?"
   - "No TypeScript detected - would you like me to migrate for better type safety?"

**Then just answer the questions** and CORTEX will implement everything with tests!

---

## 🏗️ What Happens Behind the Scenes

**Before onboarding:**
```
your-app/
├── cortex/                          # CORTEX installation (self-contained)
│   ├── .github/                     # Entry points HERE initially
│   │   ├── prompts/
│   │   │   └── CORTEX.prompt.md     # Copilot reads this
│   ├── cortex-brain/
│   ├── src/
│   └── ...
├── src/                             # Your app code
└── package.json
```

**After "onboard this application":**
```
your-app/
├── .github/                         # ✅ Entry points copied here by Module 1
│   ├── prompts/
│   │   └── CORTEX.prompt.md         # For convenience (app root location)
├── cortex/                          # CORTEX installation (unchanged)
│   ├── .github/                     # Original entry points (backup)
│   ├── cortex-brain/                # Brain initialized
│   └── ...
├── src/                             # Your app code
└── ...
```

---

## 📋 Manual Setup (If Onboarding Fails)

If automatic onboarding fails, run these steps manually:

```bash
# 1. Copy CORTEX folder to your project (if not done already)
cd /path/to/your/application
cp -r /path/to/publish/CORTEX ./cortex

# 2. Copy entry points to app root
mkdir -p .github/prompts
cp cortex/.github/prompts/CORTEX.prompt.md .github/prompts/

# 3. Install dependencies
cd cortex
pip install -r requirements.txt

# 4. Initialize brain
python -c "from src.tier1.conversation_manager import ConversationManager; ConversationManager()"

# 5. In VS Code Copilot Chat
# Type: analyze my codebase
```

---

## 🎯 What CORTEX Can Do

After onboarding, CORTEX can help you with:

- **Feature Implementation:** "Add authentication with JWT"
- **Testing:** "Create comprehensive tests for the UserService"
- **Refactoring:** "Improve code quality in src/utils/"
- **Documentation:** "Generate API documentation"
- **Architecture:** "Design a microservices architecture"

And it remembers everything from past conversations! 🧠

---

## 🔍 How Copilot Finds CORTEX

**The Magic:** When you say "onboard this application", Copilot searches your workspace for prompt files and finds `cortex/.github/prompts/CORTEX.prompt.md`. CORTEX loads, Intent Router activates, and onboarding begins!

**After Module 1 (copy_cortex_entry_points):** Entry points are also in your app's `.github/` folder for standard location convenience. Both locations work!

---

## 🆘 Troubleshooting

**Onboarding fails:**
- Check Python 3.10+ installed: `python --version`
- Check Git installed: `git --version`
- Verify CORTEX copied to `cortex/` folder: `ls cortex/`
- Try manual setup above

**Copilot doesn't recognize CORTEX:**
- Ensure `cortex/.github/prompts/CORTEX.prompt.md` exists
- Restart VS Code
- Try: `help` to see available commands

**Entry points not found:**
- Check workspace root: VS Code should be opened at application root, not inside `cortex/`
- Copilot searches recursively, will find `cortex/.github/prompts/CORTEX.prompt.md`

**Questions?**
- Check documentation: `cortex/prompts/shared/`
- GitHub: https://github.com/asifhussain60/CORTEX

---

**Version:** 2.0.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary
"""
    
    setup_file = publish_cortex / 'SETUP-FOR-COPILOT.md'
    
    if dry_run:
        logger.info(f"[DRY RUN] Would create {setup_file}")
        return True
    
    try:
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        logger.info(f"✓ Created {setup_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create setup file: {e}")
        return False


def sanitize_privacy_leaks(
    publish_cortex: Path,
    dry_run: bool = False
) -> bool:
    """
    Remove privacy leaks (absolute paths, usernames, hostnames) from published files.
    
    Args:
        publish_cortex: Path to publish/CORTEX directory
        dry_run: If True, only preview changes
    
    Returns:
        True if successful
    """
    logger.info("Step 5/6: Sanitizing privacy leaks...")
    
    import re
    
    # Privacy patterns to replace
    privacy_patterns = [
        (r'D:\\\\PROJECTS', '/path/to/projects'),
        (r'D:\\PROJECTS', '/path/to/projects'),
        (r'C:\\\\Users\\\\[a-zA-Z0-9]+', '/home/user'),
        (r'C:\\Users\\[a-zA-Z0-9]+', '/home/user'),
        (r'/Users/asifhussain', '/Users/username'),
        (r'/home/[a-z]+', '/home/user'),
        (r'AHHOME', 'HOSTNAME'),
        # Windows drive letters
        (r'C:\\\\\\\\', 'C:/'),
        (r'D:\\\\\\\\', 'D:/'),
        (r'C:\\\\', 'C:/'),
        (r'D:\\\\', 'D:/'),
    ]
    
    sanitized_count = 0
    
    # Files to sanitize (text files only)
    text_extensions = {'.py', '.md', '.yaml', '.yml', '.json', '.txt', '.sh', '.ps1'}
    
    for file_path in publish_cortex.rglob('*'):
        if not file_path.is_file():
            continue
        
        if file_path.suffix not in text_extensions:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all privacy pattern replacements
            for pattern, replacement in privacy_patterns:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # If content changed, write it back
            if content != original_content:
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    sanitized_count += 1
                    logger.info(f"✓ Sanitized: {file_path.relative_to(publish_cortex)}")
                else:
                    logger.info(f"[DRY RUN] Would sanitize: {file_path.relative_to(publish_cortex)}")
        
        except (UnicodeDecodeError, PermissionError):
            # Skip binary files or files we can't read
            continue
        except Exception as e:
            logger.warning(f"Failed to sanitize {file_path}: {e}")
    
    logger.info(f"✓ Sanitized {sanitized_count} files")
    return True


def run_validation_tests(source_root: Path) -> Tuple[bool, int, int]:
    """
    Run publish validation tests to ensure package integrity.
    
    Args:
        source_root: CORTEX repository root
    
    Returns:
        Tuple of (success, passed_count, total_count)
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("Step 6/7: Running Validation Tests")
    logger.info("=" * 80)
    logger.info("")
    
    test_files = [
        'tests/tier0/test_publish_privacy.py',
        'tests/tier0/test_publish_faculties.py',
        'tests/integration/test_publish_simulation.py',
    ]
    
    # Build pytest command
    cmd = [
        sys.executable,
        '-m',
        'pytest',
        *test_files,
        '-v',
        '--tb=line',
        '-q',  # Quiet mode for cleaner output
    ]
    
    logger.info("Running publish validation tests...")
    logger.info("")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=source_root,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # Parse output for test counts
        output_lines = result.stdout.split('\n')
        
        # Print test output
        for line in output_lines:
            if line.strip():
                logger.info(f"  {line}")
        
        # Check if tests passed
        if result.returncode == 0:
            # Extract test counts from pytest output
            for line in output_lines:
                if 'passed' in line.lower():
                    # Parse format like "43 passed in 4.75s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'passed' in part and i > 0:
                            try:
                                passed = int(parts[i-1])
                                logger.info("")
                                logger.info(f"✅ All {passed} validation tests PASSED!")
                                return True, passed, passed
                            except (ValueError, IndexError):
                                pass
            
            logger.info("")
            logger.info("✅ All validation tests PASSED!")
            return True, 0, 0
        else:
            logger.error("")
            logger.error("❌ Validation tests FAILED!")
            logger.error("Review test output above for details.")
            
            # Show stderr if available
            if result.stderr:
                logger.error("")
                logger.error("Error output:")
                for line in result.stderr.split('\n'):
                    if line.strip():
                        logger.error(f"  {line}")
            
            return False, 0, 0
            
    except subprocess.TimeoutExpired:
        logger.error("")
        logger.error("❌ Validation tests TIMED OUT (>2 minutes)")
        return False, 0, 0
    except Exception as e:
        logger.error("")
        logger.error(f"❌ Failed to run validation tests: {e}")
        return False, 0, 0


def generate_report(
    publish_root: Path,
    user_ops: Set[str],
    admin_ops: Set[str],
    tests_passed: bool = False,
    test_count: int = 0
) -> None:
    """
    Generate publish summary report.
    
    Args:
        publish_root: Path to publish/ directory
        user_ops: Set of user operation IDs
        admin_ops: Set of admin operation IDs
        tests_passed: Whether validation tests passed
        test_count: Number of tests that passed
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("Step 7/7: Generating Summary Report")
    logger.info("=" * 80)
    logger.info("")
    
    publish_cortex = publish_root / 'CORTEX'
    
    # Count files
    total_files = sum(1 for _ in publish_cortex.rglob('*') if _.is_file())
    
    # Calculate size
    total_size = sum(f.stat().st_size for f in publish_cortex.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ PUBLISH COMPLETE!" if tests_passed else "⚠️  PUBLISH COMPLETE (with warnings)")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"📦 Package Location: {publish_cortex}")
    logger.info(f"📊 Total Files: {total_files}")
    logger.info(f"💾 Package Size: {size_mb:.1f} MB")
    
    if tests_passed and test_count > 0:
        logger.info(f"✅ Validation: {test_count} tests passed")
    elif not tests_passed:
        logger.warning("⚠️  Validation: Some tests failed - review output above")
    
    logger.info("")
    logger.info(f"✅ User Operations Included ({len(user_ops)}):")
    for op in sorted(user_ops):
        logger.info(f"   - {op}")
    logger.info("")
    logger.info(f"❌ Admin Operations Excluded ({len(admin_ops)}):")
    for op in sorted(admin_ops):
        logger.info(f"   - {op}")
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("1. Manually copy publish/CORTEX to your target application")
    logger.info("2. Follow instructions in publish/CORTEX/SETUP-FOR-COPILOT.md")
    logger.info("3. In Copilot Chat: 'onboard this application'")
    logger.info("")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Publish CORTEX to publish/ folder for manual deployment'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip validation tests (not recommended)'
    )
    parser.add_argument(
        '--fail-on-test-error',
        action='store_true',
        help='Exit with error code if tests fail (default: warn but continue)'
    )
    parser.add_argument(
        '--admin-mode',
        action='store_true',
        help='⚠️  ADMIN MODE: Publish ALL content including admin tools (internal testing only)'
    )
    
    args = parser.parse_args()
    
    # Setup paths
    source_root = Path(__file__).parent.parent
    publish_root = source_root / 'publish'
    publish_cortex = publish_root / 'CORTEX'
    
    print_header()
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
        logger.info("")
    
    if args.admin_mode:
        logger.warning("")
        logger.warning("=" * 80)
        logger.warning("⚠️  ADMIN MODE ENABLED")
        logger.warning("=" * 80)
        logger.warning("Publishing ALL content including admin tools and development artifacts.")
        logger.warning("This is for internal testing ONLY - do NOT distribute to end users.")
        logger.warning("=" * 80)
        logger.warning("")
        
        # In admin mode, we don't exclude admin operations
        # (Implementation note: could modify filtering logic if needed)
    
    # Load operations and filter by tier
    ops = filter_operations_by_tier(source_root)
    user_ops = ops['user']
    admin_ops = ops['admin']
    
    # Execute publish workflow
    if not clear_publish_folder(publish_root, args.dry_run):
        logger.error("Failed to clear publish folder")
        return 1
    
    if not copy_essential_directories(source_root, publish_cortex, admin_ops, args.dry_run):
        logger.error("Failed to copy source files")
        return 1
    
    if not copy_critical_files(source_root, publish_cortex, args.dry_run):
        logger.error("Failed to copy critical files")
        return 1
    
    if not create_setup_for_copilot(publish_cortex, args.dry_run):
        logger.error("Failed to create setup file")
        return 1
    
    if not sanitize_privacy_leaks(publish_cortex, args.dry_run):
        logger.error("Failed to sanitize privacy leaks")
        return 1
    
    # Run validation tests (unless dry-run or explicitly skipped)
    tests_passed = False
    test_count = 0
    
    if not args.dry_run and not args.skip_tests:
        tests_passed, test_count, _ = run_validation_tests(source_root)
        
        if not tests_passed and args.fail_on_test_error:
            logger.error("")
            logger.error("❌ PUBLISH FAILED: Validation tests did not pass")
            logger.error("Fix test failures or use --skip-tests to bypass (not recommended)")
            return 1
    
    if not args.dry_run:
        generate_report(publish_root, user_ops, admin_ops, tests_passed, test_count)
    else:
        logger.info("")
        logger.info("🔍 DRY RUN COMPLETE - No changes made")
    
    return 0


if __name__ == '__main__':
    exit(main())
