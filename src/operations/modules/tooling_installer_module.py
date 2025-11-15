"""
Tooling Installer Module

Automatically installs missing development tooling (Python, Git, Node.js, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import platform
import logging
import os
from pathlib import Path
from typing import Dict, Tuple

# Configurable download URLs for tool installation
def get_download_urls():
    """Get tool download URLs with proper URL construction."""
    from urllib.parse import urlunparse
    
    python_protocol = os.getenv('CORTEX_PYTHON_DOWNLOAD_PROTOCOL', os.getenv('CORTEX_DEFAULT_HTTPS_PROTOCOL', 'https'))
    python_domain = os.getenv('CORTEX_PYTHON_DOWNLOAD_DOMAIN', os.getenv('CORTEX_PYTHON_DEFAULT_DOMAIN', 'www.python.org'))
    python_url = urlunparse((python_protocol, python_domain, '/downloads/', '', '', ''))
    
    choco_protocol = os.getenv('CORTEX_CHOCOLATEY_PROTOCOL', os.getenv('CORTEX_DEFAULT_HTTPS_PROTOCOL', 'https'))
    choco_domain = os.getenv('CORTEX_CHOCOLATEY_DOMAIN', os.getenv('CORTEX_CHOCOLATEY_DEFAULT_DOMAIN', 'chocolatey.org'))
    choco_url = urlunparse((choco_protocol, choco_domain, '/install', '', '', ''))
    
    # Homebrew URL construction
    homebrew_protocol = os.getenv('CORTEX_HOMEBREW_PROTOCOL', os.getenv('CORTEX_DEFAULT_HTTPS_PROTOCOL', 'https'))
    homebrew_domain = os.getenv('CORTEX_HOMEBREW_DOMAIN', os.getenv('CORTEX_HOMEBREW_DEFAULT_DOMAIN', 'raw.githubusercontent.com'))
    homebrew_path = os.getenv('CORTEX_HOMEBREW_INSTALL_PATH', os.getenv('CORTEX_HOMEBREW_DEFAULT_PATH', 'Homebrew/install/HEAD/install.sh'))
    homebrew_url = urlunparse((homebrew_protocol, homebrew_domain, f'/{homebrew_path}', '', '', ''))
    
    return {
        'python': python_url,
        'chocolatey': choco_url,
        'homebrew': homebrew_url
    }

DOWNLOAD_URLS = get_download_urls()

logger = logging.getLogger(__name__)


class ToolingInstaller:
    """Automated tooling installation."""
    
    def __init__(self, package_manager: Dict):
        self.system = platform.system()
        self.package_manager = package_manager
        self.install_log = []
    
    def install_python(self) -> Tuple[bool, str]:
        """Install Python."""
        logger.info("Installing Python...")
        
        if self.system == 'Windows':
            return self._install_windows_python()
        elif self.system == 'Darwin':
            return self._install_mac_python()
        elif self.system == 'Linux':
            return self._install_linux_python()
        else:
            return False, f"Unsupported system: {self.system}"
    
    def install_git(self) -> Tuple[bool, str]:
        """Install Git."""
        logger.info("Installing Git...")
        
        if self.system == 'Windows':
            return self._install_with_package_manager('git')
        elif self.system == 'Darwin':
            return self._install_with_package_manager('git')
        elif self.system == 'Linux':
            return self._install_with_package_manager('git')
        else:
            return False, f"Unsupported system: {self.system}"
    
    def install_node(self) -> Tuple[bool, str]:
        """Install Node.js (for Vision API)."""
        logger.info("Installing Node.js...")
        
        if self.system == 'Windows':
            return self._install_with_package_manager('nodejs')
        elif self.system == 'Darwin':
            return self._install_with_package_manager('node')
        elif self.system == 'Linux':
            return self._install_with_package_manager('nodejs')
        else:
            return False, f"Unsupported system: {self.system}"
    
    def install_sqlite(self) -> Tuple[bool, str]:
        """Install SQLite."""
        logger.info("Installing SQLite...")
        
        if self.system == 'Windows':
            return self._install_with_package_manager('sqlite')
        elif self.system == 'Darwin':
            return self._install_with_package_manager('sqlite')
        elif self.system == 'Linux':
            return self._install_with_package_manager('sqlite3')
        else:
            return False, f"Unsupported system: {self.system}"
    
    def install_pip_packages(self, requirements_file: Path) -> Tuple[bool, str]:
        """Install Python packages from requirements.txt."""
        logger.info("Installing Python packages...")
        
        if not requirements_file.exists():
            return False, f"Requirements file not found: {requirements_file}"
        
        try:
            cmd = ['pip', 'install', '-r', str(requirements_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return True, "Python packages installed"
            else:
                return False, f"pip install failed: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            return False, "pip install timed out (5 minutes)"
        except Exception as e:
            return False, f"pip install error: {e}"
    
    def _install_windows_python(self) -> Tuple[bool, str]:
        """Install Python on Windows."""
        mgr = self.package_manager.get('name')
        
        if mgr == 'choco':
            return self._run_install(['choco', 'install', 'python', '-y'])
        elif mgr == 'winget':
            return self._run_install(['winget', 'install', 'Python.Python.3.11'])
        else:
            return False, (
                "No package manager found. Install manually:\n"
                f"Download from: {DOWNLOAD_URLS['python']}\n"
                f"Or install Chocolatey: {DOWNLOAD_URLS['chocolatey']}"
            )
    
    def _install_mac_python(self) -> Tuple[bool, str]:
        """Install Python on macOS."""
        if self.package_manager.get('name') == 'brew':
            return self._run_install(['brew', 'install', 'python@3.11'])
        else:
            homebrew_url = DOWNLOAD_URLS['homebrew']
            return False, (
                "Homebrew not found. Install it first:\n"
                f'/bin/bash -c "$(curl -fsSL {homebrew_url})"'
            )
    
    def _install_linux_python(self) -> Tuple[bool, str]:
        """Install Python on Linux."""
        mgr = self.package_manager.get('name')
        
        if mgr in ['apt-get', 'apt']:
            return self._run_install(['sudo', 'apt-get', 'install', '-y', 'python3', 'python3-pip'])
        elif mgr == 'yum':
            return self._run_install(['sudo', 'yum', 'install', '-y', 'python3', 'python3-pip'])
        elif mgr == 'dnf':
            return self._run_install(['sudo', 'dnf', 'install', '-y', 'python3', 'python3-pip'])
        else:
            return False, (
                "No package manager found. Install manually:\n"
                "sudo apt-get install python3 python3-pip"
            )
    
    def _install_with_package_manager(self, package: str) -> Tuple[bool, str]:
        """Generic package installation."""
        mgr = self.package_manager.get('name')
        
        if not self.package_manager.get('installed'):
            return False, f"No package manager available to install {package}"
        
        if self.system == 'Windows':
            if mgr == 'choco':
                return self._run_install(['choco', 'install', package, '-y'])
            elif mgr == 'winget':
                return self._run_install(['winget', 'install', package])
        
        elif self.system == 'Darwin':
            if mgr == 'brew':
                return self._run_install(['brew', 'install', package])
        
        elif self.system == 'Linux':
            if mgr in ['apt-get', 'apt']:
                return self._run_install(['sudo', 'apt-get', 'install', '-y', package])
            elif mgr == 'yum':
                return self._run_install(['sudo', 'yum', 'install', '-y', package])
            elif mgr == 'dnf':
                return self._run_install(['sudo', 'dnf', 'install', '-y', package])
        
        return False, f"Unsupported package manager: {mgr}"
    
    def _run_install(self, cmd: list) -> Tuple[bool, str]:
        """Run installation command."""
        try:
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for large installs
            )
            
            log_entry = {
                'command': ' '.join(cmd),
                'returncode': result.returncode,
                'stdout': result.stdout[:500],  # Truncate
                'stderr': result.stderr[:500]
            }
            self.install_log.append(log_entry)
            
            if result.returncode == 0:
                return True, f"Installed successfully: {cmd[2]}"
            else:
                return False, f"Installation failed: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            return False, "Installation timed out (10 minutes)"
        except Exception as e:
            return False, f"Installation error: {e}"
    
    def install_missing_tools(self, missing: list) -> Dict:
        """Install all missing tools."""
        results = {}
        
        for tool in missing:
            if 'python' in tool.lower():
                success, msg = self.install_python()
                results['python'] = {'success': success, 'message': msg}
            
            elif 'git' in tool.lower():
                success, msg = self.install_git()
                results['git'] = {'success': success, 'message': msg}
            
            elif 'node' in tool.lower() or 'npm' in tool.lower():
                success, msg = self.install_node()
                results['node'] = {'success': success, 'message': msg}
            
            elif 'sqlite' in tool.lower():
                success, msg = self.install_sqlite()
                results['sqlite'] = {'success': success, 'message': msg}
        
        return results
    
    def print_install_report(self, results: Dict):
        """Print installation report."""
        logger.info("=" * 60)
        logger.info("INSTALLATION REPORT")
        logger.info("=" * 60)
        
        for tool, result in results.items():
            status = '✅' if result['success'] else '❌'
            logger.info(f"{status} {tool}: {result['message']}")
        
        logger.info("=" * 60)
        logger.info("")


class VisionAPIInstaller:
    """Install Vision API dependencies."""
    
    def __init__(self):
        self.system = platform.system()
    
    def install(self, cortex_root: Path) -> Tuple[bool, str]:
        """Install Vision API dependencies."""
        logger.info("Installing Vision API dependencies...")
        
        # Vision API is currently mock implementation
        # When real Vision API is implemented, install dependencies here
        
        # For now, just verify Node.js is available
        import shutil
        if not shutil.which('node'):
            return False, (
                "Node.js required for Vision API. Install with:\n"
                "Windows: choco install nodejs\n"
                "macOS: brew install node\n"
                "Linux: sudo apt-get install nodejs"
            )
        
        logger.info("✅ Vision API dependencies ready (mock implementation)")
        return True, "Vision API ready"
    
    def configure_credentials(self, api_key: str = None) -> Tuple[bool, str]:
        """Configure Vision API credentials."""
        # Placeholder for real Vision API setup
        logger.info("Vision API credentials configured (mock)")
        return True, "Credentials configured"


def execute(context: Dict = None) -> Dict:
    """Execute tooling installation."""
    context = context or {}
    
    # Get detection results
    detected_tools = context.get('detected_tools', {})
    missing = context.get('missing_tools', [])
    package_manager = detected_tools.get('package_manager', {})
    
    if not missing:
        logger.info("✅ No missing tools to install")
        return {'success': True, 'results': {}}
    
    # Install missing tools
    installer = ToolingInstaller(package_manager)
    results = installer.install_missing_tools(missing)
    installer.print_install_report(results)
    
    # Check if all succeeded
    all_success = all(r['success'] for r in results.values())
    
    return {
        'success': all_success,
        'results': results,
        'install_log': installer.install_log
    }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    context = {
        'detected_tools': {
            'package_manager': {'name': 'choco', 'installed': True}
        },
        'missing_tools': ['python', 'git']
    }
    
    result = execute(context)
    print(f"\nInstallation {'succeeded' if result['success'] else 'failed'}")
