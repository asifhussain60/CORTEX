"""
Environment Setup Operation - CORTEX 3.0 Phase 1.1
Monolithic MVP Implementation (~350 lines)

Detects platform, validates dependencies, creates virtual environment,
installs packages, initializes CORTEX brain databases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
import os
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, Any, Tuple
from enum import Enum


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    MAC = "mac"
    LINUX = "linux"
    UNKNOWN = "unknown"


class SetupResult:
    """Result of setup operation."""
    
    def __init__(self):
        self.success = True
        self.platform = None
        self.python_version = None
        self.git_version = None
        self.vscode_found = False
        self.venv_created = False
        self.dependencies_installed = 0
        self.brain_initialized = False
        self.errors = []
        self.warnings = []
    
    def add_error(self, message: str):
        """Add error message."""
        self.errors.append(message)
        self.success = False
    
    def add_warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'platform': self.platform.value if self.platform else None,
            'python_version': self.python_version,
            'git_version': self.git_version,
            'vscode_found': self.vscode_found,
            'venv_created': self.venv_created,
            'dependencies_installed': self.dependencies_installed,
            'brain_initialized': self.brain_initialized,
            'errors': self.errors,
            'warnings': self.warnings
        }


def detect_platform() -> Platform:
    """
    Detect current operating system platform.
    
    Returns:
        Platform enum value
    """
    system = sys.platform.lower()
    
    if system.startswith('win'):
        return Platform.WINDOWS
    elif system.startswith('darwin'):
        return Platform.MAC
    elif system.startswith('linux'):
        return Platform.LINUX
    else:
        return Platform.UNKNOWN


def validate_python() -> Tuple[bool, str]:
    """
    Validate Python installation and version.
    
    Returns:
        (is_valid, version_string)
    """
    try:
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        # Require Python 3.9+
        if version.major >= 3 and version.minor >= 9:
            return True, version_str
        else:
            return False, f"{version_str} (requires 3.9+)"
    except Exception as e:
        return False, f"Error: {e}"


def validate_git() -> Tuple[bool, str]:
    """
    Validate Git installation.
    
    Returns:
        (is_installed, version_string)
    """
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Parse version from "git version 2.42.0"
            version = result.stdout.strip().split()[-1]
            return True, version
        else:
            return False, "Not found"
    except Exception as e:
        return False, f"Error: {e}"


def validate_vscode() -> bool:
    """
    Check if VS Code is installed.
    
    Returns:
        True if VS Code found
    """
    try:
        result = subprocess.run(
            ['code', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def create_virtual_environment(project_root: Path) -> Tuple[bool, str]:
    """
    Create Python virtual environment if it doesn't exist.
    
    Args:
        project_root: CORTEX project root directory
    
    Returns:
        (success, message)
    """
    venv_path = project_root / '.venv'
    
    # Check if already exists
    if venv_path.exists():
        return True, f"Virtual environment already exists at {venv_path}"
    
    try:
        # Create venv
        subprocess.run(
            [sys.executable, '-m', 'venv', str(venv_path)],
            check=True,
            capture_output=True,
            text=True
        )
        return True, f"Created virtual environment at {venv_path}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to create venv: {e.stderr}"
    except Exception as e:
        return False, f"Error creating venv: {e}"


def install_dependencies(project_root: Path) -> Tuple[bool, int, str]:
    """
    Install Python dependencies from requirements.txt.
    
    Args:
        project_root: CORTEX project root directory
    
    Returns:
        (success, packages_installed, message)
    """
    requirements_file = project_root / 'requirements.txt'
    
    if not requirements_file.exists():
        return False, 0, f"requirements.txt not found at {requirements_file}"
    
    try:
        # Use pip to install
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Count installed packages (rough estimate from output)
            lines = result.stdout.split('\n')
            installed = sum(1 for line in lines if 'Successfully installed' in line or 'Requirement already satisfied' in line)
            return True, max(installed, 1), "Dependencies installed successfully"
        else:
            return False, 0, f"pip install failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, 0, "Installation timed out (>5 minutes)"
    except Exception as e:
        return False, 0, f"Error installing dependencies: {e}"


def configure_gitignore(project_root: Path) -> Tuple[bool, str]:
    """
    Add CORTEX folder to .gitignore to prevent committing CORTEX internals.
    
    Creates .gitignore if it doesn't exist, or appends CORTEX exclusion if missing.
    
    Args:
        project_root: CORTEX project root directory
    
    Returns:
        (success, message)
    """
    gitignore_path = project_root / '.gitignore'
    
    cortex_entry = "CORTEX/"
    cortex_section = f"""
# CORTEX AI Assistant (local only, not committed)
# This folder contains CORTEX's internal code, brain databases, and configuration.
# Excluding it prevents accidental commits to your application repository.
{cortex_entry}
"""
    
    try:
        # Read existing .gitignore if it exists
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Check if CORTEX is already excluded
            if cortex_entry in existing_content or "CORTEX/" in existing_content:
                return True, ".gitignore already contains CORTEX exclusion"
            
            # Append to existing file
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                # Add newline if file doesn't end with one
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write(cortex_section)
            
            return True, "Added CORTEX/ to existing .gitignore"
        else:
            # Create new .gitignore with CORTEX exclusion
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(cortex_section.lstrip())
            
            return True, "Created .gitignore with CORTEX/ exclusion"
    
    except Exception as e:
        return False, f"Failed to configure .gitignore: {e}"


def initialize_brain_databases(project_root: Path) -> Tuple[bool, str]:
    """
    Initialize CORTEX brain SQLite databases.
    
    Creates:
        - cortex-brain/tier1/conversations.db
        - cortex-brain/tier2/knowledge-graph.db
        - cortex-brain/tier3/context-intelligence.db
    
    Args:
        project_root: CORTEX project root directory
    
    Returns:
        (success, message)
    """
    brain_path = project_root / 'cortex-brain'
    
    databases = [
        ('tier1', 'conversations.db'),
        ('tier2', 'knowledge-graph.db'),
        ('tier3', 'context-intelligence.db')
    ]
    
    created_count = 0
    errors = []
    
    for tier, db_name in databases:
        tier_path = brain_path / tier
        db_path = tier_path / db_name
        
        # Create tier directory if needed
        tier_path.mkdir(parents=True, exist_ok=True)
        
        # Create database if it doesn't exist
        if not db_path.exists():
            try:
                # Create empty database with basic table
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Create metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert initialization marker
                cursor.execute(
                    "INSERT INTO metadata (key, value) VALUES (?, ?)",
                    ('initialized', 'true')
                )
                
                conn.commit()
                conn.close()
                
                created_count += 1
            except Exception as e:
                errors.append(f"Failed to create {db_name}: {e}")
    
    if errors:
        return False, f"Brain initialization errors: {'; '.join(errors)}"
    
    if created_count > 0:
        return True, f"Initialized {created_count} brain database(s)"
    else:
        return True, "Brain databases already initialized"


def setup_environment(
    profile: str = 'standard',
    project_root: Path = None
) -> Dict[str, Any]:
    """
    Main setup operation - configures CORTEX development environment.
    
    Steps:
        1. Detect platform (Windows/Mac/Linux)
        2. Validate dependencies (Python 3.9+, Git, VS Code)
        3. Create virtual environment
        4. Install Python packages from requirements.txt
        5. Initialize brain databases (Tier 1-3)
        6. Validate setup completion
    
    Args:
        profile: Setup profile ('minimal', 'standard', 'full')
        project_root: Project root path (auto-detected if None)
    
    Returns:
        Result dictionary with success status and details
    """
    result = SetupResult()
    
    # Auto-detect project root if not provided
    if project_root is None:
        project_root = Path.cwd()
        # Look for cortex-operations.yaml to confirm we're in CORTEX root
        if not (project_root / 'cortex-operations.yaml').exists():
            # Try parent directories
            for parent in project_root.parents:
                if (parent / 'cortex-operations.yaml').exists():
                    project_root = parent
                    break
    
    print(f"\n🔧 CORTEX Environment Setup")
    print(f"   Profile: {profile}")
    print(f"   Project root: {project_root}")
    print()
    
    # 1. Platform Detection
    print("📍 Step 1: Detecting platform...")
    result.platform = detect_platform()
    
    if result.platform == Platform.UNKNOWN:
        result.add_error("Unknown platform - only Windows/Mac/Linux supported")
        return result.to_dict()
    
    print(f"   ✅ Platform detected: {result.platform.value}")
    
    # 2. Validate Python
    print("\n🐍 Step 2: Validating Python installation...")
    python_valid, python_version = validate_python()
    result.python_version = python_version
    
    if not python_valid:
        result.add_error(f"Python validation failed: {python_version}")
        return result.to_dict()
    
    print(f"   ✅ Python {python_version} found")
    
    # 3. Validate Git
    print("\n📦 Step 3: Validating Git installation...")
    git_installed, git_version = validate_git()
    result.git_version = git_version
    
    if not git_installed:
        result.add_warning(f"Git not found: {git_version}")
        print(f"   ⚠️  Git not found (optional but recommended)")
    else:
        print(f"   ✅ Git {git_version} found")
    
    # 4. Check VS Code (optional)
    print("\n💻 Step 4: Checking VS Code installation...")
    result.vscode_found = validate_vscode()
    
    if result.vscode_found:
        print(f"   ✅ VS Code found")
    else:
        result.add_warning("VS Code not found (optional)")
        print(f"   ⚠️  VS Code not found (optional)")
    
    # 5. Create Virtual Environment
    if profile in ['standard', 'full']:
        print("\n🔨 Step 5: Creating virtual environment...")
        venv_success, venv_message = create_virtual_environment(project_root)
        result.venv_created = venv_success
        
        if not venv_success:
            result.add_error(venv_message)
            return result.to_dict()
        
        print(f"   ✅ {venv_message}")
    
    # 6. Install Dependencies
    if profile in ['standard', 'full']:
        print("\n📥 Step 6: Installing dependencies...")
        deps_success, deps_count, deps_message = install_dependencies(project_root)
        result.dependencies_installed = deps_count
        
        if not deps_success:
            result.add_error(deps_message)
            return result.to_dict()
        
        print(f"   ✅ {deps_message} ({deps_count} package(s))")
    
    # 7. Initialize Brain
    if profile in ['standard', 'full']:
        print("\n🧠 Step 7: Initializing CORTEX brain...")
        brain_success, brain_message = initialize_brain_databases(project_root)
        result.brain_initialized = brain_success
        
        if not brain_success:
            result.add_error(brain_message)
            return result.to_dict()
        
        print(f"   ✅ {brain_message}")
    
    # 8. Configure .gitignore
    if profile in ['standard', 'full']:
        print("\n🔒 Step 8: Configuring .gitignore...")
        gitignore_success, gitignore_message = configure_gitignore(project_root)
        
        if not gitignore_success:
            result.add_warning(gitignore_message)
            print(f"   ⚠️  {gitignore_message}")
        else:
            print(f"   ✅ {gitignore_message}")
    
    # 9. Final Validation
    print("\n✅ Step 9: Final validation...")
    
    if profile == 'full':
        # Additional checks for full profile
        checks = [
            (result.platform != Platform.UNKNOWN, "Platform detected"),
            (python_valid, "Python valid"),
            (result.venv_created, "Virtual environment created"),
            (result.dependencies_installed > 0, "Dependencies installed"),
            (result.brain_initialized, "Brain initialized")
        ]
        
        all_passed = all(check[0] for check in checks)
        
        if all_passed:
            print("   ✅ All validation checks passed")
        else:
            failed = [check[1] for check in checks if not check[0]]
            result.add_error(f"Validation failed: {', '.join(failed)}")
    
    # Success summary
    print(f"\n{'='*60}")
    print(f"✅ CORTEX Environment Setup Complete!")
    print(f"{'='*60}")
    print(f"\nPlatform: {result.platform.value}")
    print(f"Python: {result.python_version}")
    if git_installed:
        print(f"Git: {result.git_version}")
    if result.venv_created:
        print(f"Virtual environment: ✅ Created")
    if result.dependencies_installed > 0:
        print(f"Dependencies: ✅ {result.dependencies_installed} installed")
    if result.brain_initialized:
        print(f"Brain: ✅ Initialized")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    print(f"\nCORTEX is ready to use!")
    print(f"{'='*60}\n")
    
    return result.to_dict()


# Natural language registration
if __name__ == '__main__':
    # CLI entry point for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX Environment Setup')
    parser.add_argument('--profile', choices=['minimal', 'standard', 'full'], 
                       default='standard', help='Setup profile')
    parser.add_argument('--project-root', type=Path, help='Project root path')
    
    args = parser.parse_args()
    
    result = setup_environment(
        profile=args.profile,
        project_root=args.project_root
    )
    
    sys.exit(0 if result['success'] else 1)
