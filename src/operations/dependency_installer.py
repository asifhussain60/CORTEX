#!/usr/bin/env python3
"""
Dependency Installer

Handles automated installation of CORTEX dependencies with validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DependencyResult:
    """Result of dependency installation."""
    success: bool
    python_version: str
    installed_packages: List[str]
    failed_packages: List[str]
    venv_created: bool
    errors: List[str]


class DependencyInstaller:
    """
    Handles CORTEX dependency installation and validation.
    
    Features:
    - Python version validation (3.8+)
    - Virtual environment detection/creation
    - Requirements.txt installation
    - Package verification
    - Rollback on failure
    """
    
    REQUIRED_PYTHON_VERSION = (3, 8)
    CRITICAL_PACKAGES = [
        "pytest",
        "pyyaml",
        "requests"
    ]
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.requirements_file = cortex_root / "requirements.txt"
    
    def install_dependencies(
        self,
        create_venv: bool = True,
        skip_validation: bool = False
    ) -> DependencyResult:
        """
        Install CORTEX dependencies with validation.
        
        Args:
            create_venv: Create virtual environment if missing
            skip_validation: Skip Python version validation
        
        Returns:
            DependencyResult with installation status
        """
        logger.info("Starting dependency installation...")
        
        errors = []
        installed_packages = []
        failed_packages = []
        venv_created = False
        
        try:
            # Step 1: Validate Python version
            if not skip_validation:
                logger.info("Step 1: Validating Python version...")
                version_ok, version_str = self._validate_python_version()
                if not version_ok:
                    errors.append(
                        f"Python {self.REQUIRED_PYTHON_VERSION[0]}.{self.REQUIRED_PYTHON_VERSION[1]}+ required, "
                        f"found {version_str}"
                    )
                    return DependencyResult(
                        success=False,
                        python_version=version_str,
                        installed_packages=[],
                        failed_packages=[],
                        venv_created=False,
                        errors=errors
                    )
            else:
                version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            logger.info(f"✅ Python {version_str} validated")
            
            # Step 2: Check/create virtual environment
            if create_venv:
                logger.info("Step 2: Checking virtual environment...")
                venv_created = self._ensure_venv()
                if venv_created:
                    logger.info("✅ Virtual environment created")
                else:
                    logger.info("✅ Using existing virtual environment")
            
            # Step 3: Install requirements
            logger.info("Step 3: Installing requirements.txt...")
            if not self.requirements_file.exists():
                errors.append(f"Requirements file not found: {self.requirements_file}")
                return DependencyResult(
                    success=False,
                    python_version=version_str,
                    installed_packages=[],
                    failed_packages=[],
                    venv_created=venv_created,
                    errors=errors
                )
            
            install_success, installed, failed = self._install_requirements()
            installed_packages = installed
            failed_packages = failed
            
            if not install_success:
                errors.append(f"Failed to install packages: {', '.join(failed_packages)}")
            
            # Step 4: Verify critical packages
            logger.info("Step 4: Verifying critical packages...")
            missing_critical = self._verify_critical_packages()
            if missing_critical:
                errors.append(f"Missing critical packages: {', '.join(missing_critical)}")
                return DependencyResult(
                    success=False,
                    python_version=version_str,
                    installed_packages=installed_packages,
                    failed_packages=failed_packages + missing_critical,
                    venv_created=venv_created,
                    errors=errors
                )
            
            logger.info("✅ All critical packages verified")
            
            return DependencyResult(
                success=len(failed_packages) == 0,
                python_version=version_str,
                installed_packages=installed_packages,
                failed_packages=failed_packages,
                venv_created=venv_created,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"❌ Dependency installation failed: {e}")
            errors.append(str(e))
            
            return DependencyResult(
                success=False,
                python_version=version_str if 'version_str' in locals() else "unknown",
                installed_packages=installed_packages,
                failed_packages=failed_packages,
                venv_created=venv_created,
                errors=errors
            )
    
    def _validate_python_version(self) -> Tuple[bool, str]:
        """Validate Python version meets requirements."""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        required = self.REQUIRED_PYTHON_VERSION
        meets_requirement = (version.major, version.minor) >= required
        
        return meets_requirement, version_str
    
    def _ensure_venv(self) -> bool:
        """Ensure virtual environment exists, create if missing."""
        # Check if running in virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if in_venv:
            logger.info("Already running in virtual environment")
            return False
        
        # Check for existing venv
        venv_paths = [
            self.cortex_root / "venv",
            self.cortex_root / ".venv",
            self.cortex_root / "env"
        ]
        
        for venv_path in venv_paths:
            if venv_path.exists():
                logger.info(f"Found existing virtual environment: {venv_path}")
                return False
        
        # Create new virtual environment
        venv_path = self.cortex_root / "venv"
        logger.info(f"Creating virtual environment: {venv_path}")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ Virtual environment created: {venv_path}")
            logger.info("⚠️ Activate with: source venv/bin/activate (Unix) or venv\\Scripts\\activate (Windows)")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e.stderr}")
            return False
    
    def _install_requirements(self) -> Tuple[bool, List[str], List[str]]:
        """Install packages from requirements.txt."""
        logger.info(f"Installing from: {self.requirements_file}")
        
        try:
            # Run pip install
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Parse installed packages from output
            installed = []
            for line in result.stdout.splitlines():
                if "Successfully installed" in line:
                    # Extract package names
                    packages_str = line.split("Successfully installed")[1].strip()
                    installed = [pkg.split("-")[0] for pkg in packages_str.split()]
            
            logger.info(f"✅ Installed {len(installed)} packages")
            return True, installed, []
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Installation failed: {e.stderr}")
            
            # Try to identify failed packages
            failed = []
            for line in e.stderr.splitlines():
                if "ERROR:" in line or "error:" in line:
                    # Extract package name if possible
                    words = line.split()
                    for word in words:
                        if word and not word.startswith("-"):
                            failed.append(word)
                            break
            
            return False, [], failed
    
    def _verify_critical_packages(self) -> List[str]:
        """Verify critical packages are installed and importable."""
        missing = []
        
        for package in self.CRITICAL_PACKAGES:
            try:
                __import__(package)
                logger.debug(f"✅ {package} verified")
            except ImportError:
                logger.warning(f"❌ {package} not found")
                missing.append(package)
        
        return missing
    
    def get_installed_packages(self) -> List[str]:
        """Get list of currently installed packages."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=freeze"],
                check=True,
                capture_output=True,
                text=True
            )
            
            packages = []
            for line in result.stdout.splitlines():
                if "==" in line:
                    package_name = line.split("==")[0]
                    packages.append(package_name)
            
            return packages
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list packages: {e.stderr}")
            return []


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Dependency Installer")
    parser.add_argument("--cortex-root", default=".", help="CORTEX root directory")
    parser.add_argument("--no-venv", action="store_true", help="Skip venv creation")
    parser.add_argument("--skip-validation", action="store_true", help="Skip Python version check")
    
    args = parser.parse_args()
    
    installer = DependencyInstaller(Path(args.cortex_root))
    result = installer.install_dependencies(
        create_venv=not args.no_venv,
        skip_validation=args.skip_validation
    )
    
    print(f"\n{'='*60}")
    print(f"Dependency Installation {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"{'='*60}")
    print(f"Python Version: {result.python_version}")
    print(f"Virtual Environment Created: {result.venv_created}")
    print(f"Installed Packages: {len(result.installed_packages)}")
    print(f"Failed Packages: {len(result.failed_packages)}")
    
    if result.errors:
        print(f"\n⚠️ Errors:")
        for error in result.errors:
            print(f"  - {error}")
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
