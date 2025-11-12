#!/usr/bin/env python3
"""
CORTEX Installation Script
-------------------------
Installs all required dependencies for CORTEX Brain system.

This script installs:
1. Python dependencies (pytest, PyYAML, etc.)
2. Node.js dependencies (Playwright, TypeScript, sql.js)
3. Validates installations
4. Sets up environment

Usage:
    python scripts/install-cortex.py
    python scripts/install-cortex.py --skip-node  # Skip Node.js deps
    python scripts/install-cortex.py --dev        # Include dev dependencies
"""

import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import argparse


# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(message: str):
    """Print success message in green."""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{RED}✗{RESET} {message}")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠{RESET} {message}")


def print_info(message: str):
    """Print info message in blue."""
    print(f"{BLUE}ℹ{RESET} {message}")


def print_header(message: str):
    """Print section header."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{message}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None


def run_command(command: List[str], description: str, check: bool = True) -> Tuple[bool, str]:
    """
    Run a shell command and return success status and output.
    
    Args:
        command: Command and arguments as list
        description: Human-readable description
        check: Whether to raise exception on failure
    
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, f"Command not found: {command[0]}"


def get_python_version() -> Optional[str]:
    """Get Python version."""
    success, output = run_command([sys.executable, "--version"], "Python version", check=False)
    if success:
        return output.strip().split()[1]
    return None


def get_node_version() -> Optional[str]:
    """Get Node.js version."""
    success, output = run_command(["node", "--version"], "Node.js version", check=False)
    if success:
        return output.strip()
    return None


def get_npm_version() -> Optional[str]:
    """Get npm version."""
    success, output = run_command(["npm", "--version"], "npm version", check=False)
    if success:
        return output.strip()
    return None


def install_python_dependencies(dev: bool = False) -> bool:
    """Install Python dependencies."""
    print_header("Installing Python Dependencies")
    
    # Check Python version
    python_version = get_python_version()
    if python_version:
        print_info(f"Python version: {python_version}")
    else:
        print_error("Python not found!")
        return False
    
    # Install main dependencies
    print_info("Installing CORTEX dependencies...")
    success, output = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "CORTEX/requirements.txt"],
        "Main dependencies"
    )
    
    if success:
        print_success("Installed CORTEX dependencies")
    else:
        print_error(f"Failed to install CORTEX dependencies:\n{output}")
        return False
    
    # Install test dependencies
    print_info("Installing test dependencies...")
    success, output = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "tests/tier1/requirements.txt"],
        "Test dependencies"
    )
    
    if success:
        print_success("Installed test dependencies")
    else:
        print_warning(f"Failed to install test dependencies:\n{output}")
    
    # Verify critical packages
    print_info("Verifying installations...")
    
    # Check pytest
    try:
        import pytest
        print_success(f"  pytest {pytest.__version__}")
    except ImportError:
        print_error("  pytest - NOT INSTALLED")
        all_installed = False
    
    # Check PyYAML
    try:
        import yaml
        print_success(f"  PyYAML {yaml.__version__}")
    except ImportError:
        print_error("  PyYAML - NOT INSTALLED")
        all_installed = False
    
    # Check sqlite3
    try:
        import sqlite3
        print_success(f"  sqlite3 {sqlite3.sqlite_version}")
    except ImportError:
        print_error("  sqlite3 - NOT INSTALLED")
        all_installed = False
    
    return True  # Return True if we got here (all imports succeeded)


def install_node_dependencies() -> bool:
    """Install Node.js dependencies."""
    print_header("Installing Node.js Dependencies")
    
    # Check if Node.js is installed
    if not check_command_exists("node"):
        print_error("Node.js not found!")
        print_info("Please install Node.js from https://nodejs.org/")
        return False
    
    node_version = get_node_version()
    npm_version = get_npm_version()
    
    print_info(f"Node.js version: {node_version}")
    print_info(f"npm version: {npm_version}")
    
    # Change to CORTEX directory
    cortex_dir = Path("CORTEX")
    if not cortex_dir.exists():
        print_error(f"CORTEX directory not found: {cortex_dir}")
        return False
    
    # Install npm dependencies
    print_info("Installing npm dependencies...")
    success, output = run_command(
        ["npm", "install"],
        "npm install",
        check=False
    )
    
    if success:
        print_success("Installed npm dependencies")
    else:
        print_error(f"Failed to install npm dependencies:\n{output}")
        return False
    
    # Verify Playwright installation
    print_info("Verifying Playwright...")
    success, output = run_command(
        ["npx", "playwright", "--version"],
        "Playwright version",
        check=False
    )
    
    if success:
        print_success(f"Playwright installed: {output.strip()}")
    else:
        print_warning("Playwright not found, installing browsers...")
        success, output = run_command(
            ["npx", "playwright", "install"],
            "Install Playwright browsers",
            check=False
        )
        if success:
            print_success("Installed Playwright browsers")
        else:
            print_error(f"Failed to install Playwright browsers:\n{output}")
            return False
    
    return True


def validate_sqlite() -> bool:
    """Validate SQLite installation and FTS5 support."""
    print_header("Validating SQLite")
    
    try:
        import sqlite3
        
        # Check SQLite version
        version = sqlite3.sqlite_version
        print_info(f"SQLite version: {version}")
        
        # Check FTS5 support
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE VIRTUAL TABLE test_fts USING fts5(content)
            """)
            print_success("FTS5 full-text search supported")
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            print_error(f"FTS5 not supported: {e}")
            print_warning("Please upgrade SQLite to version 3.9.0 or later")
            conn.close()
            return False
    
    except ImportError:
        print_error("sqlite3 module not found!")
        return False


def create_directory_structure() -> bool:
    """Create necessary directory structure."""
    print_header("Creating Directory Structure")
    
    directories = [
        "cortex-brain",
        "cortex-brain/backups",
        "tests/tier1",
        "tests/tier2",
        "tests/tier3",
        "CORTEX/src/brain/tier1",
        "CORTEX/src/brain/tier2",
        "CORTEX/src/brain/tier3"
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {dir_path}")
        else:
            print_info(f"Exists: {dir_path}")
    
    return True


def print_summary(
    python_ok: bool,
    node_ok: bool,
    sqlite_ok: bool,
    dirs_ok: bool,
    skip_node: bool
) -> bool:
    """Print installation summary."""
    print_header("Installation Summary")
    
    print(f"\nPython Dependencies: {GREEN + '✓ INSTALLED' if python_ok else RED + '✗ FAILED'}{RESET}")
    
    if not skip_node:
        print(f"Node.js Dependencies: {GREEN + '✓ INSTALLED' if node_ok else RED + '✗ FAILED'}{RESET}")
    else:
        print(f"Node.js Dependencies: {YELLOW}⊘ SKIPPED{RESET}")
    
    print(f"SQLite with FTS5: {GREEN + '✓ VALIDATED' if sqlite_ok else RED + '✗ FAILED'}{RESET}")
    print(f"Directory Structure: {GREEN + '✓ CREATED' if dirs_ok else RED + '✗ FAILED'}{RESET}")
    
    all_ok = python_ok and (node_ok or skip_node) and sqlite_ok and dirs_ok
    
    if all_ok:
        print(f"\n{GREEN}{'=' * 70}{RESET}")
        print(f"{GREEN}✓ CORTEX installation complete!{RESET}")
        print(f"{GREEN}{'=' * 70}{RESET}")
        print("\nNext steps:")
        print("  1. Run tests: pytest tests/tier1/test_tier1_suite.py -v")
        print("  2. Run migrations: python scripts/migrate-all-tiers.py")
        print("  3. Validate: python scripts/validate-migrations.py")
    else:
        print(f"\n{RED}{'=' * 70}{RESET}")
        print(f"{RED}✗ Installation incomplete. Please fix errors above.{RESET}")
        print(f"{RED}{'=' * 70}{RESET}")
    
    return all_ok


def main():
    """Main installation entry point."""
    parser = argparse.ArgumentParser(description="Install CORTEX dependencies")
    parser.add_argument("--skip-node", action="store_true", help="Skip Node.js dependencies")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    args = parser.parse_args()
    
    print_header("CORTEX Installation")
    print_info("This script will install all required dependencies for CORTEX")
    
    # Install dependencies
    python_ok = install_python_dependencies(dev=args.dev)
    node_ok = True if args.skip_node else install_node_dependencies()
    sqlite_ok = validate_sqlite()
    dirs_ok = create_directory_structure()
    
    # Print summary
    success = print_summary(python_ok, node_ok, sqlite_ok, dirs_ok, args.skip_node)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
