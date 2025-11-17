"""
Tooling Detection Module

Detects installed tooling on target machine (Python, Git, Node.js, pip, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ToolingDetector:
    """Detect installed development tooling."""
    
    def __init__(self):
        self.system = platform.system()
        self.detected_tools = {}
    
    def detect_all(self) -> Dict[str, Dict]:
        """Detect all required tooling."""
        logger.info("Detecting installed tooling...")
        
        tools = {
            'python': self.detect_python(),
            'pip': self.detect_pip(),
            'git': self.detect_git(),
            'node': self.detect_node(),
            'npm': self.detect_npm(),
            'sqlite': self.detect_sqlite(),
            'package_manager': self.detect_package_manager()
        }
        
        self.detected_tools = tools
        return tools
    
    def detect_python(self) -> Dict:
        """Detect Python installation."""
        return self._detect_command(
            name='Python',
            commands=['python', 'python3'],
            version_flag='--version',
            min_version='3.9.0'
        )
    
    def detect_pip(self) -> Dict:
        """Detect pip installation."""
        return self._detect_command(
            name='pip',
            commands=['pip', 'pip3'],
            version_flag='--version',
            min_version='21.0.0'
        )
    
    def detect_git(self) -> Dict:
        """Detect Git installation."""
        return self._detect_command(
            name='Git',
            commands=['git'],
            version_flag='--version',
            min_version='2.30.0'
        )
    
    def detect_node(self) -> Dict:
        """Detect Node.js installation."""
        return self._detect_command(
            name='Node.js',
            commands=['node'],
            version_flag='--version',
            min_version='16.0.0',
            required=False  # Node.js is optional for Vision API
        )
    
    def detect_npm(self) -> Dict:
        """Detect npm installation."""
        return self._detect_command(
            name='npm',
            commands=['npm'],
            version_flag='--version',
            min_version='8.0.0',
            required=False
        )
    
    def detect_sqlite(self) -> Dict:
        """Detect SQLite installation."""
        # First check if Python has sqlite3 module (usually included)
        try:
            import sqlite3
            return {
                'name': 'SQLite',
                'command': 'sqlite3 (Python module)',
                'installed': True,
                'path': 'Python built-in',
                'version': sqlite3.sqlite_version,
                'version_ok': True,
                'min_version': '3.35.0',
                'required': True
            }
        except ImportError:
            pass
        
        # Fallback to command-line sqlite3
        return self._detect_command(
            name='SQLite',
            commands=['sqlite3'],
            version_flag='--version',
            min_version='3.35.0'
        )
    
    def detect_package_manager(self) -> Dict:
        """Detect system package manager for automated installation."""
        if self.system == 'Windows':
            # Check for Chocolatey, winget
            for mgr in ['choco', 'winget']:
                result = self._check_command(mgr, ['--version'])
                if result['installed']:
                    return {
                        'name': mgr,
                        'installed': True,
                        'path': result['path']
                    }
            return {'name': 'none', 'installed': False}
        
        elif self.system == 'Darwin':
            # Check for Homebrew
            result = self._check_command('brew', ['--version'])
            if result['installed']:
                return {
                    'name': 'brew',
                    'installed': True,
                    'path': result['path']
                }
            return {'name': 'none', 'installed': False}
        
        elif self.system == 'Linux':
            # Check for apt, yum, dnf
            for mgr in ['apt-get', 'yum', 'dnf']:
                result = self._check_command(mgr, ['--version'])
                if result['installed']:
                    return {
                        'name': mgr,
                        'installed': True,
                        'path': result['path']
                    }
            return {'name': 'none', 'installed': False}
        
        return {'name': 'unknown', 'installed': False}
    
    def _detect_command(
        self,
        name: str,
        commands: list,
        version_flag: str,
        min_version: Optional[str] = None,
        required: bool = True
    ) -> Dict:
        """Generic command detection."""
        for cmd in commands:
            result = self._check_command(cmd, [version_flag])
            if result['installed']:
                version_ok = True
                if min_version and result['version']:
                    version_ok = self._compare_versions(
                        result['version'],
                        min_version
                    )
                
                return {
                    'name': name,
                    'command': cmd,
                    'installed': True,
                    'path': result['path'],
                    'version': result['version'],
                    'version_ok': version_ok,
                    'min_version': min_version,
                    'required': required
                }
        
        return {
            'name': name,
            'command': commands[0],
            'installed': False,
            'required': required
        }
    
    def _check_command(self, cmd: str, args: list) -> Dict:
        """Check if command exists and get version."""
        # First check if command is in PATH
        path = shutil.which(cmd)
        if not path:
            return {'installed': False, 'path': None, 'version': None}
        
        # Try to get version
        try:
            result = subprocess.run(
                [cmd] + args,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            version = self._extract_version(result.stdout + result.stderr)
            
            return {
                'installed': True,
                'path': path,
                'version': version
            }
        except Exception as e:
            logger.debug(f"Error checking {cmd}: {e}")
            return {'installed': False, 'path': None, 'version': None}
    
    def _extract_version(self, output: str) -> Optional[str]:
        """Extract version number from command output."""
        import re
        
        # Common version patterns
        patterns = [
            r'(\d+\.\d+\.\d+)',  # X.Y.Z
            r'(\d+\.\d+)',       # X.Y
            r'v(\d+\.\d+\.\d+)', # vX.Y.Z
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                return match.group(1)
        
        return None
    
    def _compare_versions(self, current: str, minimum: str) -> bool:
        """Compare version strings (X.Y.Z format)."""
        try:
            current_parts = [int(x) for x in current.split('.')]
            minimum_parts = [int(x) for x in minimum.split('.')]
            
            # Pad shorter version with zeros
            while len(current_parts) < len(minimum_parts):
                current_parts.append(0)
            while len(minimum_parts) < len(current_parts):
                minimum_parts.append(0)
            
            return current_parts >= minimum_parts
        except Exception:
            return False
    
    def get_missing_required(self) -> list:
        """Get list of missing required tools."""
        if not self.detected_tools:
            self.detect_all()
        
        missing = []
        for tool_name, tool_info in self.detected_tools.items():
            if tool_name == 'package_manager':
                continue
            
            if not tool_info.get('installed') and tool_info.get('required', True):
                missing.append(tool_name)
            elif tool_info.get('installed') and not tool_info.get('version_ok', True):
                missing.append(f"{tool_name} (version too old)")
        
        return missing
    
    def print_report(self):
        """Print detection report."""
        if not self.detected_tools:
            self.detect_all()
        
        logger.info("=" * 60)
        logger.info("TOOLING DETECTION REPORT")
        logger.info("=" * 60)
        
        for tool_name, info in self.detected_tools.items():
            if tool_name == 'package_manager':
                continue
            
            name = info.get('name', tool_name)
            installed = info.get('installed', False)
            required = info.get('required', True)
            
            status = '✅' if installed else '❌'
            req_label = 'REQUIRED' if required else 'OPTIONAL'
            
            logger.info(f"{status} {name:15} [{req_label}]")
            
            if installed:
                version = info.get('version', 'unknown')
                path = info.get('path', 'unknown')
                logger.info(f"   Version: {version}")
                logger.info(f"   Path: {path}")
                
                if 'version_ok' in info and not info['version_ok']:
                    min_ver = info.get('min_version', 'unknown')
                    logger.warning(f"   ⚠️  Version too old (need {min_ver}+)")
            else:
                logger.info(f"   Not installed")
        
        logger.info("")
        
        # Package manager
        pkg_mgr = self.detected_tools.get('package_manager', {})
        if pkg_mgr.get('installed'):
            logger.info(f"📦 Package Manager: {pkg_mgr['name']}")
        else:
            logger.warning("⚠️  No package manager detected (manual installation required)")
        
        logger.info("=" * 60)
        logger.info("")
        
        missing = self.get_missing_required()
        if missing:
            logger.warning(f"Missing required tools: {', '.join(missing)}")
            return False
        else:
            logger.info("✅ All required tooling detected!")
            return True


def execute(context: Dict = None) -> Dict:
    """Execute tooling detection."""
    detector = ToolingDetector()
    tools = detector.detect_all()
    all_ok = detector.print_report()
    
    return {
        'success': all_ok,
        'tools': tools,
        'missing': detector.get_missing_required()
    }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    result = execute()
    
    if not result['success']:
        print("\nTo install missing tools:")
        print("Windows: Use Chocolatey (choco install python git)")
        print("macOS: Use Homebrew (brew install python git)")
        print("Linux: Use apt/yum (sudo apt install python3 git)")
