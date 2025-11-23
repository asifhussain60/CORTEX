#!/usr/bin/env python3
"""
CORTEX Application Deployment Script

Deploys CORTEX to a target application repository with full configuration.

Usage:
    python scripts/deploy_to_app.py --target D:\\PROJECTS\\KSESSIONS
    python scripts/deploy_to_app.py --target D:\\PROJECTS\\KSESSIONS --dry-run

This script:
1. Validates target application structure
2. Builds user deployment package
3. Copies CORTEX files to target
4. Configures paths for target app
5. Installs entry point in .github/prompts/
6. Initializes brain database
7. Runs crawlers to index codebase (optional)
8. Verifies deployment

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import argparse
import shutil
import json
import platform
import socket
from pathlib import Path
from typing import Dict, Tuple, List
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DEPLOYMENT_VERSION = "1.0.0"


def print_header():
    """Print deployment header."""
    logger.info("=" * 80)
    logger.info("CORTEX Application Deployment")
    logger.info("=" * 80)
    logger.info(f"Version: {DEPLOYMENT_VERSION}")
    logger.info(f"Author: Asif Hussain")
    logger.info(f"Copyright: © 2024-2025 Asif Hussain. All rights reserved.")
    logger.info("=" * 80)
    logger.info("")


def validate_target_app(target_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate target application structure.
    
    Checks:
    1. Target directory exists
    2. Is a git repository (has .git)
    3. Has write permissions
    4. Not already has CORTEX (warn if exists)
    """
    issues = []
    
    if not target_path.exists():
        issues.append(f"Target path does not exist: {target_path}")
        return False, issues
    
    if not target_path.is_dir():
        issues.append(f"Target path is not a directory: {target_path}")
        return False, issues
    
    # Check for git repository
    git_dir = target_path / '.git'
    if not git_dir.exists():
        logger.warning(f"Target is not a git repository (no .git folder). Continuing anyway...")
    
    # Check write permissions
    if not os.access(target_path, os.W_OK):
        issues.append(f"No write permission to target directory: {target_path}")
        return False, issues
    
    # Check if CORTEX already exists
    cortex_marker = target_path / '.github' / 'prompts' / 'CORTEX.prompt.md'
    if cortex_marker.exists():
        logger.warning(f"CORTEX already deployed to {target_path}. Will overwrite.")
    
    return True, []


def detect_target_platform() -> Dict[str, str]:
    """Detect target platform and return configuration."""
    system = platform.system()
    hostname = socket.gethostname()
    
    if system == 'Darwin':
        platform_name = 'macOS'
        shell = 'zsh'
        path_sep = '/'
    elif system == 'Windows':
        platform_name = 'Windows'
        shell = 'powershell'
        path_sep = '\\'
    elif system == 'Linux':
        platform_name = 'Linux'
        shell = 'bash'
        path_sep = '/'
    else:
        platform_name = 'Unknown'
        shell = 'sh'
        path_sep = '/'
    
    return {
        'system': system,
        'platform_name': platform_name,
        'hostname': hostname,
        'shell': shell,
        'path_sep': path_sep
    }


def build_deployment_package(source_root: Path, build_dir: Path, dry_run: bool = False) -> bool:
    """Build user deployment package."""
    logger.info("Building CORTEX user deployment package...")
    
    build_script = source_root / 'scripts' / 'build_user_deployment.py'
    if not build_script.exists():
        logger.error(f"Build script not found: {build_script}")
        return False
    
    output_dir = build_dir / 'cortex-user-v1.0.0'
    
    if dry_run:
        logger.info(f"[DRY RUN] Would build package to: {output_dir}")
        return True
    
    # Run build script
    cmd = [
        'python',
        str(build_script),
        '--output', str(output_dir)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(source_root))
        if result.returncode != 0:
            logger.error(f"Build failed: {result.stderr}")
            return False
        logger.info("Build complete")
        return True
    except Exception as e:
        logger.error(f"Build error: {e}")
        return False


def copy_cortex_files(
    source_package: Path,
    target_root: Path,
    dry_run: bool = False
) -> bool:
    """Copy CORTEX files to target application."""
    logger.info("Copying CORTEX files to target application...")
    
    target_cortex = target_root / 'cortex'
    
    if dry_run:
        logger.info(f"[DRY RUN] Would copy {source_package} to {target_cortex}")
        return True
    
    # CRITICAL: Remove old cortex directory first to ensure clean deployment
    if target_cortex.exists():
        logger.info(f"Removing old CORTEX installation at {target_cortex}")
        shutil.rmtree(target_cortex)
    
    # Create fresh target directory
    target_cortex.mkdir(parents=True, exist_ok=True)
    
    # Copy all files from clean package
    try:
        shutil.copytree(source_package, target_cortex, dirs_exist_ok=True)
        logger.info(f"Copied clean CORTEX package to {target_cortex}")
        return True
    except Exception as e:
        logger.error(f"Copy failed: {e}")
        return False


def configure_target_paths(
    target_root: Path,
    platform_info: Dict[str, str],
    dry_run: bool = False
) -> bool:
    """Configure cortex.config.json for target application."""
    logger.info("Configuring CORTEX paths for target application...")
    
    config_file = target_root / 'cortex' / 'cortex.config.json'
    
    if not config_file.exists():
        logger.error(f"Config file not found: {config_file}")
        return False
    
    if dry_run:
        logger.info(f"[DRY RUN] Would configure {config_file}")
        return True
    
    # Load config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return False
    
    # Update paths for this machine
    hostname = platform_info['hostname']
    cortex_root = str(target_root / 'cortex')
    brain_path = str(target_root / 'cortex' / 'cortex-brain')
    
    if hostname not in config['machines']:
        config['machines'][hostname] = {}
    
    config['machines'][hostname]['rootPath'] = cortex_root
    config['machines'][hostname]['brainPath'] = brain_path
    
    # Update application info
    config['application']['name'] = target_root.name
    config['application']['rootPath'] = str(target_root)
    
    # Save config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configured paths for machine: {hostname}")
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


def install_entry_point(
    source_root: Path,
    target_root: Path,
    dry_run: bool = False
) -> bool:
    """Install CORTEX entry point in target's .github/prompts/ folder.
    
    NON-DESTRUCTIVE: Backs up and merges with existing Copilot instructions.
    """
    logger.info("Installing CORTEX entry point...")
    
    # Source files from CORTEX repo (NOT from cortex package)
    source_entry = source_root / '.github' / 'prompts' / 'CORTEX.prompt.md'
    source_instructions = source_root / '.github' / 'copilot-instructions.md'
    
    # Target files in application's .github folder
    target_github = target_root / '.github'
    target_prompts = target_github / 'prompts'
    target_entry = target_prompts / 'CORTEX.prompt.md'
    target_instructions = target_github / 'copilot-instructions.md'
    
    if not source_entry.exists():
        logger.error(f"Entry point not found: {source_entry}")
        return False
    
    if dry_run:
        logger.info(f"[DRY RUN] Would install entry point to {target_entry}")
        if target_instructions.exists():
            logger.info(f"[DRY RUN] Would merge with existing: {target_instructions}")
        return True
    
    # Ensure target .github/prompts/ exists
    target_prompts.mkdir(parents=True, exist_ok=True)
    
    try:
        # CORTEX.prompt.md - Always safe to copy (CORTEX-specific file)
        shutil.copy2(source_entry, target_entry)
        logger.info(f"✓ Installed entry point: {target_entry}")
        
        # copilot-instructions.md - MERGE with existing to preserve user configs
        if source_instructions.exists():
            if target_instructions.exists():
                # Backup existing file
                backup_path = target_github / 'copilot-instructions.md.backup'
                shutil.copy2(target_instructions, backup_path)
                logger.info(f"✓ Backed up existing instructions: {backup_path}")
                
                # Read existing content
                with open(target_instructions, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Check if CORTEX already referenced
                if 'CORTEX' in existing_content and '.github/prompts/CORTEX.prompt.md' in existing_content:
                    logger.info(f"✓ CORTEX already referenced in {target_instructions}")
                else:
                    # Append CORTEX reference to existing instructions
                    with open(source_instructions, 'r', encoding='utf-8') as f:
                        cortex_instructions = f.read()
                    
                    merged_content = existing_content.rstrip() + "\n\n" + \
                        "# CORTEX AI Assistant\n\n" + \
                        "CORTEX entry point added during onboarding. See .github/prompts/CORTEX.prompt.md\n\n" + \
                        cortex_instructions
                    
                    with open(target_instructions, 'w', encoding='utf-8') as f:
                        f.write(merged_content)
                    
                    logger.info(f"✓ Merged CORTEX instructions into existing file: {target_instructions}")
                    logger.info(f"   Original preserved in: {backup_path}")
            else:
                # No existing file, safe to copy
                shutil.copy2(source_instructions, target_instructions)
                logger.info(f"✓ Installed instructions: {target_instructions}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to install entry point: {e}")
        return False


def initialize_target_brain(
    target_root: Path,
    dry_run: bool = False
) -> bool:
    """Initialize CORTEX brain database for target application."""
    logger.info("Initializing CORTEX brain tier databases...")
    
    brain_dir = target_root / 'cortex' / 'cortex-brain'
    
    # Define tier-specific databases
    tier_dbs = {
        'tier1': ['conversations.db', 'working_memory.db'],
        'tier2': ['knowledge_graph.db'],
        'tier3': ['context.db']
    }
    
    if dry_run:
        logger.info(f"[DRY RUN] Would initialize brain tiers at {brain_dir}")
        for tier, dbs in tier_dbs.items():
            logger.info(f"  - {tier}: {', '.join(dbs)}")
        return True
    
    # Check if any tier databases already exist
    all_exist = True
    for tier, db_names in tier_dbs.items():
        tier_path = brain_dir / tier
        for db_name in db_names:
            db_path = tier_path / db_name
            if not db_path.exists():
                all_exist = False
                break
    
    if all_exist:
        logger.warning("Brain tier databases already exist. Skipping initialization.")
        return True
    
    # Initialize will happen automatically on first use of each tier
    logger.info("Brain tier databases will be auto-created on first use.")
    return True


def run_target_crawlers(
    target_root: Path,
    dry_run: bool = False
) -> bool:
    """Run crawlers to index target application codebase."""
    logger.info("Running crawlers to index codebase...")
    
    if dry_run:
        logger.info("[DRY RUN] Would run crawlers")
        return True
    
    crawler_script = target_root / 'cortex' / 'src' / 'crawlers' / 'orchestrator.py'
    
    if not crawler_script.exists():
        logger.warning("Crawler not found. Skipping indexing.")
        return True  # Non-fatal
    
    try:
        # Run crawler
        cmd = [
            'python',
            str(crawler_script),
            '--target', str(target_root)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.warning(f"Crawler completed with warnings: {result.stderr}")
        else:
            logger.info("Codebase indexed successfully")
        
        return True
    except subprocess.TimeoutExpired:
        logger.warning("Crawler timed out after 5 minutes. Continuing anyway.")
        return True
    except Exception as e:
        logger.warning(f"Crawler error (non-fatal): {e}")
        return True


def verify_deployment(
    target_root: Path,
    dry_run: bool = False
) -> Tuple[bool, List[str]]:
    """Verify CORTEX deployment is complete and functional."""
    logger.info("Verifying deployment...")
    
    issues = []
    
    if dry_run:
        logger.info("[DRY RUN] Would verify deployment")
        return True, []
    
    # Check critical files exist
    critical_files = [
        'cortex/cortex.config.json',
        'cortex/cortex-operations.yaml',
        'cortex/requirements.txt',
        '.github/prompts/CORTEX.prompt.md',
        '.github/copilot-instructions.md',  # CRITICAL: Copilot entry point
        'cortex/src/tier1/conversation_manager.py',
        'cortex/src/tier2/__init__.py',
        'cortex/src/cortex_agents/__init__.py'
    ]
    
    for file_path in critical_files:
        full_path = target_root / file_path
        if not full_path.exists():
            issues.append(f"Missing critical file: {file_path}")
    
    # Validate GitHub Copilot instruction files content
    copilot_instructions = target_root / '.github' / 'copilot-instructions.md'
    cortex_prompt = target_root / '.github' / 'prompts' / 'CORTEX.prompt.md'
    backup_instructions = target_root / '.github' / 'copilot-instructions.md.backup'
    
    # Check if backup exists (indicates merge happened)
    if backup_instructions.exists():
        logger.info(f"ℹ️  Existing instructions were merged (backup: {backup_instructions.name})")
    
    if copilot_instructions.exists():
        try:
            with open(copilot_instructions, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate references to CORTEX.prompt.md
            if 'CORTEX.prompt.md' not in content:
                issues.append("copilot-instructions.md does not reference CORTEX.prompt.md")
            
            if '.github/prompts/CORTEX.prompt.md' not in content:
                issues.append("copilot-instructions.md missing correct path to main prompt")
                
        except Exception as e:
            issues.append(f"Failed to validate copilot-instructions.md: {e}")
    
    if cortex_prompt.exists():
        try:
            with open(cortex_prompt, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            # Validate essential CORTEX sections
            required_sections = [
                'CORTEX Universal Entry Point',
                'RESPONSE TEMPLATES',
                'Quick Start'
            ]
            
            missing_sections = [s for s in required_sections if s not in prompt_content]
            if missing_sections:
                issues.append(f"CORTEX.prompt.md missing sections: {', '.join(missing_sections)}")
                
        except Exception as e:
            issues.append(f"Failed to validate CORTEX.prompt.md: {e}")
    
    if issues:
        return False, issues
    
    logger.info("✅ Deployment verified successfully!")
    return True, []


def install_python_dependencies(
    target_root: Path,
    dry_run: bool = False
) -> bool:
    """Install Python dependencies from requirements.txt."""
    logger.info("Installing Python dependencies...")
    
    requirements = target_root / 'cortex' / 'requirements.txt'
    
    if not requirements.exists():
        logger.error(f"Requirements file not found: {requirements}")
        return False
    
    if dry_run:
        logger.info(f"[DRY RUN] Would install from {requirements}")
        return True
    
    try:
        cmd = ['pip', 'install', '-r', str(requirements)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.error(f"pip install failed: {result.stderr}")
            return False
        
        logger.info("Python dependencies installed")
        return True
    except subprocess.TimeoutExpired:
        logger.error("pip install timed out (5 minutes)")
        return False
    except Exception as e:
        logger.error(f"pip install error: {e}")
        return False


def setup_vision_api(
    target_root: Path,
    dry_run: bool = False
) -> bool:
    """Setup Vision API dependencies."""
    logger.info("Setting up Vision API...")
    
    if dry_run:
        logger.info("[DRY RUN] Would setup Vision API")
        return True
    
    try:
        import sys
        sys.path.insert(0, str(target_root / 'cortex'))
        
        from src.operations.modules.tooling_installer_module import VisionAPIInstaller
        
        installer = VisionAPIInstaller()
        success, msg = installer.install(target_root / 'cortex')
        
        if success:
            logger.info(msg)
            return True
        else:
            logger.error(msg)
            return False
    
    except Exception as e:
        logger.error(f"Vision API setup error: {e}")
        return False


def check_and_install_tooling(
    source_root: Path,
    dry_run: bool = False
) -> Tuple[bool, Dict]:
    """Check for required tooling and install if missing."""
    logger.info("Checking required tooling...")
    
    if dry_run:
        logger.info("[DRY RUN] Would check and install missing tooling")
        return True, {}
    
    # Import tooling modules
    import sys
    sys.path.insert(0, str(source_root))
    
    try:
        from src.operations.modules.tooling_detection_module import ToolingDetector
        from src.operations.modules.tooling_installer_module import ToolingInstaller, VisionAPIInstaller
        
        # Detect installed tooling
        detector = ToolingDetector()
        tools = detector.detect_all()
        detector.print_report()
        
        missing = detector.get_missing_required()
        
        if not missing:
            logger.info("✅ All required tooling installed!")
            return True, tools
        
        # Ask user for permission to install
        logger.warning(f"Missing required tools: {', '.join(missing)}")
        logger.info("")
        logger.info("CORTEX can automatically install missing tools.")
        
        response = input("Install missing tools now? (y/n): ").strip().lower()
        
        if response != 'y':
            logger.warning("Deployment cancelled. Please install missing tools manually.")
            return False, tools
        
        # Install missing tools
        package_manager = tools.get('package_manager', {})
        installer = ToolingInstaller(package_manager)
        
        results = installer.install_missing_tools(missing)
        installer.print_install_report(results)
        
        # Check if installation succeeded
        all_success = all(r['success'] for r in results.values())
        
        if not all_success:
            logger.error("Some installations failed. Please install manually.")
            return False, tools
        
        # Re-detect to verify
        logger.info("Verifying installations...")
        detector = ToolingDetector()
        tools = detector.detect_all()
        
        if detector.get_missing_required():
            logger.error("Installation verification failed")
            return False, tools
        
        logger.info("✅ All tools successfully installed!")
        return True, tools
    
    except Exception as e:
        logger.error(f"Tooling check failed: {e}")
        return False, {}


def deploy_cortex(
    source_root: Path,
    target_root: Path,
    profile: str = 'standard',
    dry_run: bool = False
) -> bool:
    """Main deployment workflow."""
    print_header()
    
    logger.info(f"Source: {source_root}")
    logger.info(f"Target: {target_root}")
    logger.info(f"Profile: {profile}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("")
    
    # Step 0: Check and install tooling (BOOTSTRAP)
    logger.info("Step 0/9: Checking required tooling...")
    tooling_ok, detected_tools = check_and_install_tooling(source_root, dry_run)
    if not tooling_ok:
        logger.error("Tooling check failed. Cannot proceed with deployment.")
        return False
    logger.info("✓ Tooling ready")
    logger.info("")
    
    # Step 1: Validate target
    logger.info("Step 1/9: Validating target application...")
    valid, issues = validate_target_app(target_root)
    if not valid:
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    logger.info("✓ Target validated")
    logger.info("")
    
    # Step 2: Detect platform
    logger.info("Step 2/9: Detecting platform...")
    platform_info = detect_target_platform()
    logger.info(f"✓ Detected: {platform_info['platform_name']} ({platform_info['hostname']})")
    logger.info("")
    
    # Step 3: Build package
    logger.info("Step 3/9: Building deployment package...")
    build_dir = source_root / 'dist'
    if not build_deployment_package(source_root, build_dir, dry_run):
        return False
    logger.info("✓ Package built")
    logger.info("")
    
    # Step 4: Copy files
    logger.info("Step 4/9: Copying CORTEX files...")
    source_package = build_dir / 'cortex-user-v1.0.0'
    if not copy_cortex_files(source_package, target_root, dry_run):
        return False
    logger.info("✓ Files copied")
    logger.info("")
    
    # Step 5: Install Python dependencies
    logger.info("Step 5/9: Installing Python dependencies...")
    if not install_python_dependencies(target_root, dry_run):
        logger.warning("Dependency installation failed (non-fatal)")
    else:
        logger.info("✓ Dependencies installed")
    logger.info("")
    
    # Step 6: Configure paths
    logger.info("Step 6/9: Configuring paths...")
    if not configure_target_paths(target_root, platform_info, dry_run):
        return False
    logger.info("✓ Paths configured")
    logger.info("")
    
    # Step 7: Install entry point
    logger.info("Step 7/9: Installing entry point...")
    if not install_entry_point(source_root, target_root, dry_run):
        return False
    logger.info("✓ Entry point installed")
    logger.info("")
    
    # Profile-specific steps
    if profile in ['standard', 'full']:
        # Step 8: Initialize brain
        logger.info("Step 8/9: Initializing brain...")
        if not initialize_target_brain(target_root, dry_run):
            logger.warning("Brain initialization failed (non-fatal)")
        else:
            logger.info("✓ Brain initialized")
        logger.info("")
    
    if profile == 'full':
        # Step 9: Setup Vision API
        logger.info("Step 9/9: Setting up Vision API...")
        if not setup_vision_api(target_root, dry_run):
            logger.warning("Vision API setup failed (non-fatal)")
        else:
            logger.info("✓ Vision API ready")
        logger.info("")
    
    # Verify deployment
    logger.info("Final verification...")
    verified, issues = verify_deployment(target_root, dry_run)
    if not verified:
        logger.error("Deployment verification failed:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ CORTEX DEPLOYMENT COMPLETE!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. cd to target application")
    logger.info("2. Test in GitHub Copilot Chat:")
    logger.info("   - 'demo'")
    logger.info("   - 'setup environment'")
    logger.info("   - 'cleanup workspace'")
    logger.info("")
    logger.info("Note: Python dependencies already installed during deployment")
    logger.info("")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Deploy CORTEX to target application'
    )
    parser.add_argument(
        '--target',
        type=Path,
        required=True,
        help='Target application root directory (e.g., D:\\PROJECTS\\KSESSIONS)'
    )
    parser.add_argument(
        '--source',
        type=Path,
        default=Path(__file__).parent.parent,
        help='CORTEX source root directory'
    )
    parser.add_argument(
        '--profile',
        choices=['quick', 'standard', 'full'],
        default='standard',
        help='Deployment profile (quick=files only, standard=+brain, full=+crawlers)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview deployment without making changes'
    )
    
    args = parser.parse_args()
    
    try:
        success = deploy_cortex(
            source_root=args.source,
            target_root=args.target,
            profile=args.profile,
            dry_run=args.dry_run
        )
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    import os
    exit(main())
