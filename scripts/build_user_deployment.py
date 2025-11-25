#!/usr/bin/env python3
"""
CORTEX User Deployment Package Builder

Creates a lightweight distribution package containing only user-facing operations.
Admin-only operations, development tools, and internal documentation are excluded.

Usage:
    python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0
    python scripts/build_user_deployment.py --output ./dist/cortex-user-v1.0.0 --dry-run

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import argparse
import shutil
import yaml
from pathlib import Path
from typing import Set, Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Package metadata
PACKAGE_VERSION = "3.2.0"  # Updated for TDD Mastery integration
PACKAGE_NAME = f"cortex-user-v{PACKAGE_VERSION}"

# Operations to include in user package
USER_OPERATIONS = {
    'cortex_tutorial',
    'environment_setup',
    'workspace_cleanup',
    'cortex_demo',           # Demo/tutorial operation
    'design_sync'            # Keep brain aligned with reality
}

# Admin-only scripts (exclude from user package)
ADMIN_SCRIPTS = {
    'sync_plugin_commands.py',
    'update_operations_status.py',
    'measure_token_reduction.py',
    'phase3_token_measurement.py',
    'remove_slash_commands.py',
    'migrate_knowledge_patterns.py',
    'generate_performance_tests.py',
    'profile_performance.py',
    'plan_cli.py'
}

# Directories to INCLUDE (allowlist approach - cleaner production package)
INCLUDED_DIRS = {
    'src',                      # Core source code
    'cortex-brain',             # Brain configuration (YAML, schemas)
    '.github/prompts',          # Entry point prompts
    '.github'                   # For copilot-instructions.md
}

# CRITICAL files that MUST be included (brain protection, schemas, etc.)
CRITICAL_FILES = {
    # Brain Protection (Tier 0)
    'cortex-brain/brain-protection-rules.yaml',
    
    # Database Schemas
    'cortex-brain/schemas/tier1-schema.sql',
    'cortex-brain/schemas/tier2-schema.sql',
    'cortex-brain/schemas/tier3-schema.sql',
    
    # CORTEX Entry Point
    '.github/prompts/CORTEX.prompt.md',
    '.github/copilot-instructions.md',
    
    # Core Configuration
    'cortex.config.json',
    'cortex.config.template.json',
    'cortex-operations.yaml',
    'requirements.txt',
    
    # Essential Documentation (user-facing only)
    'prompts/shared/story.md',
    'prompts/shared/setup-guide.md',
    'prompts/shared/tracking-guide.md',
    'prompts/shared/technical-reference.md',
    'prompts/shared/agents-guide.md',
    'prompts/shared/configuration-reference.md',
    'prompts/shared/plugin-system.md',
    'prompts/shared/operations-reference.md',
    
    # TDD Mastery Components (CRITICAL - v3.2.0)
    'cortex-brain/documents/implementation-guides/test-strategy.yaml',
    'cortex-brain/documents/implementation-guides/TDD-MASTERY-INTEGRATION-PLAN.md',
    'cortex-brain/documents/implementation-guides/TDD-MASTERY-QUICKSTART.md',
    'cortex-brain/documents/reports/TDD-MASTERY-PHASE1-2-COMPLETE.md',
    'cortex-brain/documents/reports/TDD-MASTERY-PHASE4-COMPLETE.md',
    'cortex-brain/documents/reports/TDD-MASTERY-PHASE5-COMPLETE.md',
    'cortex-brain/capabilities.yaml',
    'cortex-brain/response-templates.yaml',
    '.github/prompts/modules/template-guide.md',
    '.github/prompts/modules/response-format.md',
    '.github/prompts/modules/planning-system-guide.md',
    
    # TDD Mastery - Source Files (v3.2.0)
    'src/workflows/tdd_workflow_orchestrator.py',
    'src/workflows/tdd_state_machine.py',
    'src/workflows/refactoring_intelligence.py',
    'src/agents/view_discovery_agent.py',
    'src/agents/feedback_agent.py',
    'cortex-brain/agents/debug_agent.py',
    'cortex-brain/agents/debug_session_manager.py',
    
    # TDD Mastery - Integration Tests (v3.2.0)
    'tests/test_tdd_phase4_integration.py',
    
    # Issue #3 Fixes (v3.1.0) - CRITICAL
    'src/agents/feedback_agent.py',
    'src/agents/view_discovery_agent.py',
    'src/workflows/tdd_workflow_integrator.py',
    'cortex-brain/tier2/schema/element_mappings.sql',
    'cortex-brain/agents/intent-patterns.yaml',
    'apply_element_mappings_schema.py',
    'validate_issue3_phase4.py',
    
    # Legal
    'README.md',
    'LICENSE',
    'CHANGELOG.md'
}

# Directories to EXCLUDE entirely
EXCLUDED_DIRS = {
    'tests',
    'workflow_checkpoints',
    '.github/workflows',        # GitHub Actions
    '.github/hooks',            # Git hooks
    'docs',                     # All documentation (user has entry point)
    'examples',                 # Example code
    'site',                     # mkdocs site
    'logs',                     # Log files
    'scripts',                  # Build/admin scripts (except deployment)
    'cortex-extension',         # VS Code extension (separate deployment)
    '__pycache__',
    '.pytest_cache',
    '.venv',
    'venv',
    '.git',
    'dist',
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
    '*.db',                     # Exclude brain database
    '*.db-journal',
    '.coverage',
    'htmlcov',
    '*IMPLEMENTATION*.md',      # Implementation docs
    '*STATUS*.md',              # Status reports  
    '*PLAN*.md',                # Planning docs
    '*SESSION*.md',             # Session notes
    '*REPORT*.md',              # Reports
    '*COMPLETE*.md',            # Completion reports
    '*DESIGN*.md'               # Design docs
}


def load_operations_config(project_root: Path) -> Dict:
    """Load operations configuration from YAML."""
    config_path = project_root / 'cortex-operations.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Operations config not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_user_modules(operations_config: Dict, user_ops: Set[str]) -> Set[str]:
    """Extract all modules needed for user operations."""
    user_modules = set()
    
    for op_id, op_config in operations_config.get('operations', {}).items():
        if op_id not in user_ops:
            continue
        
        # Get all modules for this operation
        modules = op_config.get('modules', [])
        user_modules.update(modules)
        
        # Get modules from all profiles
        for profile_config in op_config.get('profiles', {}).values():
            profile_modules = profile_config.get('modules', [])
            user_modules.update(profile_modules)
    
    return user_modules


def filter_operations_yaml(operations_config: Dict, user_ops: Set[str]) -> Dict:
    """Create filtered operations YAML with only user operations."""
    filtered = {'operations': {}}
    
    for op_id, op_config in operations_config.get('operations', {}).items():
        if op_id in user_ops:
            filtered['operations'][op_id] = op_config
    
    # Include modules section if it exists
    if 'modules' in operations_config:
        user_modules = get_user_modules(operations_config, user_ops)
        filtered['modules'] = {
            mod_id: mod_config 
            for mod_id, mod_config in operations_config['modules'].items()
            if mod_id in user_modules
        }
    
    return filtered


def should_include_path(path: Path, project_root: Path) -> bool:
    """Check if path should be INCLUDED in deployment (strict allowlist)."""
    rel_path = path.relative_to(project_root)
    path_str = str(rel_path).replace('\\', '/')
    
    # STEP 0: Critical files override (highest priority)
    # These MUST be included regardless of other rules
    if path_str in CRITICAL_FILES:
        return True
    
    # Root-level essential files (allowlist)
    root_essential = {
        'cortex.config.json',
        'cortex.config.template.json',
        'cortex-operations.yaml',
        'requirements.txt',
        'README.md',
        'LICENSE',
        'CHANGELOG.md'
    }
    
    # STEP 1: Check root files (high priority)
    if len(rel_path.parts) == 1 and rel_path.name in root_essential:
        return True
    
    # STEP 2: Exclude patterns (before directory checks)
    for pattern in EXCLUDED_PATTERNS:
        if path.match(pattern):
            return False
    
    # STEP 3: Explicit exclusions (docs, examples, workflows, etc.)
    first_dir = rel_path.parts[0] if len(rel_path.parts) > 0 else None
    if first_dir in EXCLUDED_DIRS:
        return False
    
    # STEP 4: Check if path is under allowed directories
    # NOTE: .github/ is NOT included in cortex package - deployed separately
    allowed_paths = {
        'src',                  # Core source code
        'cortex-brain',         # Brain YAML only
    }
    
    # src/ - include all
    if path_str.startswith('src/') or path_str == 'src':
        return True
    
    # cortex-brain/ - YAML files + SQL schemas + specific directories
    if 'cortex-brain' in rel_path.parts:
        if path.is_dir():
            # Include essential brain directories
            allowed_brain_dirs = {'schemas', 'tier1', 'tier2', 'tier3', 'corpus-callosum'}
            if any(d in rel_path.parts for d in allowed_brain_dirs):
                return True
            # Include root cortex-brain dir
            if len(rel_path.parts) == 1:
                return True
        # Include YAML configs and SQL schemas
        return path.suffix in {'.yaml', '.yml', '.sql'}
    
    # prompts/shared/ - user-facing documentation only
    if 'prompts' in rel_path.parts and 'shared' in rel_path.parts:
        if path.is_dir():
            return True
        # Only include essential user docs (listed in CRITICAL_FILES)
        return path_str in CRITICAL_FILES
    
    # .github/ - EXCLUDED from cortex package (deployed separately to target root)
    if '.github' in rel_path.parts:
        return False
    
    # Everything else is excluded
    return False


def copy_project_structure(
    project_root: Path,
    output_dir: Path,
    user_modules: Set[str],
    dry_run: bool = False
) -> Dict[str, int]:
    """Copy project structure with filtering."""
    stats = {
        'files_copied': 0,
        'files_excluded': 0,
        'dirs_created': 0
    }
    
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    for item in project_root.rglob('*'):
        if not should_include_path(item, project_root):
            stats['files_excluded'] += 1
            continue
        
        rel_path = item.relative_to(project_root)
        dest_path = output_dir / rel_path
        
        if item.is_dir():
            if not dry_run:
                dest_path.mkdir(parents=True, exist_ok=True)
            stats['dirs_created'] += 1
        else:
            # Special handling for module files
            if 'src/operations/modules' in str(rel_path):
                module_name = item.stem.replace('_module', '')
                if module_name not in user_modules and item.stem != '__init__':
                    logger.debug(f"Excluding module: {rel_path}")
                    stats['files_excluded'] += 1
                    continue
            
            # Special handling for scripts
            if 'scripts' in str(rel_path) and item.name in ADMIN_SCRIPTS:
                logger.debug(f"Excluding admin script: {rel_path}")
                stats['files_excluded'] += 1
                continue
            
            if not dry_run:
                try:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
                except Exception as e:
                    logger.warning(f"Failed to copy {rel_path}: {e}")
                    stats['files_excluded'] += 1
                    continue
            stats['files_copied'] += 1
    
    return stats


def create_user_requirements(project_root: Path, output_dir: Path, dry_run: bool = False):
    """Create filtered requirements.txt for user package."""
    req_file = project_root / 'requirements.txt'
    
    if not req_file.exists():
        logger.warning("requirements.txt not found")
        return
    
    with open(req_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter out dev-only dependencies
    dev_keywords = ['pytest', 'coverage', 'black', 'flake8', 'mypy', 'sphinx']
    user_lines = [
        line for line in lines 
        if not any(keyword in line.lower() for keyword in dev_keywords)
    ]
    
    if not dry_run:
        output_file = output_dir / 'requirements.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(user_lines)
        logger.info(f"Created filtered requirements.txt ({len(user_lines)} dependencies)")


def create_user_readme(output_dir: Path, dry_run: bool = False):
    """Create user-focused README."""
    readme_content = f"""# CORTEX v{PACKAGE_VERSION} - User Package

**AI Enhancement System for GitHub Copilot**

This package provides the essential CORTEX operations for end-users:
- Interactive tutorial and onboarding
- Environment setup and configuration  
- Workspace cleanup and maintenance

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp cortex.config.template.json cortex.config.json
   # Edit cortex.config.json with your paths
   ```

3. **Run interactive demo:**
   ```
   Tell GitHub Copilot: "demo"
   ```

4. **Setup your environment:**
   ```
   Tell GitHub Copilot: "setup environment"
   ```

## Documentation

- **Story:** `prompts/shared/story.md` - Understanding CORTEX
- **Setup Guide:** `prompts/shared/setup-guide.md` - Installation details
- **Tracking Guide:** `prompts/shared/tracking-guide.md` - Conversation memory

## Support

- Repository: https://github.com/asifhussain60/CORTEX
- Issues: https://github.com/asifhussain60/CORTEX/issues

## Copyright

© 2024-2025 Asif Hussain. All rights reserved.  
Proprietary software - See LICENSE file for terms.
"""
    
    if not dry_run:
        readme_file = output_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.info("Created user README.md")


def copy_bootstrap_prompt(project_root: Path, output_dir: Path, dry_run: bool = False):
    """Copy bootstrap CORTEX.prompt.md to package root for user repos."""
    bootstrap_source = project_root / 'publish' / 'CORTEX.prompt.md'
    
    if not bootstrap_source.exists():
        logger.warning(f"Bootstrap prompt not found: {bootstrap_source}")
        logger.warning("Users will need to manually create .github/prompts/CORTEX.prompt.md")
        return
    
    if not dry_run:
        bootstrap_dest = output_dir / 'CORTEX.prompt.md'
        shutil.copy2(bootstrap_source, bootstrap_dest)
        logger.info(f"Copied bootstrap CORTEX.prompt.md to package root")
        logger.info("  Users can copy this to .github/prompts/ in their repo")
    else:
        logger.info(f"Would copy: {bootstrap_source} -> {output_dir / 'CORTEX.prompt.md'}")



def build_deployment_package(
    project_root: Path,
    output_dir: Path,
    dry_run: bool = False
) -> bool:
    """Build complete user deployment package."""
    logger.info("=" * 80)
    logger.info("CORTEX User Deployment Package Builder")
    logger.info("=" * 80)
    logger.info(f"Version: {PACKAGE_VERSION}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("")
    
    # Load operations config
    logger.info("Loading operations configuration...")
    operations_config = load_operations_config(project_root)
    
    # Get user modules
    logger.info("Extracting user modules...")
    user_modules = get_user_modules(operations_config, USER_OPERATIONS)
    logger.info(f"User operations: {len(USER_OPERATIONS)}")
    logger.info(f"User modules: {len(user_modules)}")
    
    # Create filtered operations YAML
    logger.info("\nCreating filtered operations config...")
    filtered_ops = filter_operations_yaml(operations_config, USER_OPERATIONS)
    
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_yaml = output_dir / 'cortex-operations.yaml'
        with open(output_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(filtered_ops, f, sort_keys=False, allow_unicode=True)
        logger.info(f"Created: {output_yaml}")
    
    # Copy project structure
    logger.info("\nCopying project files...")
    stats = copy_project_structure(project_root, output_dir, user_modules, dry_run)
    logger.info(f"Files copied: {stats['files_copied']}")
    logger.info(f"Files excluded: {stats['files_excluded']}")
    logger.info(f"Directories created: {stats['dirs_created']}")
    
    # Create user-specific files
    logger.info("\nCreating user-specific files...")
    create_user_requirements(project_root, output_dir, dry_run)
    create_user_readme(output_dir, dry_run)
    copy_bootstrap_prompt(project_root, output_dir, dry_run)
    
    # Calculate package size
    if not dry_run:
        total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
        logger.info(f"\nPackage size: {total_size / 1024 / 1024:.2f} MB")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Deployment package build complete!")
    logger.info("=" * 80)
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build CORTEX user deployment package'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('./dist') / PACKAGE_NAME,
        help='Output directory for deployment package'
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
        help='Preview what would be built without creating files'
    )
    
    args = parser.parse_args()
    
    try:
        success = build_deployment_package(
            project_root=args.project_root,
            output_dir=args.output,
            dry_run=args.dry_run
        )
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
