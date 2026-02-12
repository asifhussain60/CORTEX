#!/usr/bin/env python3
"""
CORTEX Cross-Platform Setup Verification

Tests that CORTEX MCP setup works correctly on current platform.
Run this script after setup to verify all components.

Usage:
    python .cortex/verify-setup.py

Authority: Phase 53 - Cross-Platform Architecture
"""

import json
import platform
import sys
from pathlib import Path
from typing import List, Tuple

# Add cortex to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
    from cortex.common.file_utils import (
        IS_WINDOWS,
        IS_MACOS,
        IS_LINUX,
        get_venv_python_path,
        get_absolute_venv_python,
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


class SetupVerifier:
    """Verify CORTEX setup on current platform."""
    
    def __init__(self):
        self.checks: List[Tuple[str, bool, str]] = []
        self.workspace = Path.cwd()
    
    def add_check(self, name: str, passed: bool, message: str):
        """Add verification check result."""
        self.checks.append((name, passed, message))
        icon = "✅" if passed else "❌"
        print(f"{icon} {name}: {message}")
    
    def verify_platform_detection(self) -> bool:
        """Verify platform detection works."""
        system = platform.system()
        detected = "Windows" if IS_WINDOWS else "macOS" if IS_MACOS else "Linux"
        
        self.add_check(
            "Platform Detection",
            True,
            f"{system} detected as {detected}"
        )
        return True
    
    def verify_venv_paths(self) -> bool:
        """Verify virtual environment path utilities."""
        try:
            vscode_path = get_venv_python_path()
            expected = (
                "${workspaceFolder}/.venv/Scripts/python.exe" if IS_WINDOWS
                else "${workspaceFolder}/.venv/bin/python"
            )
            
            if vscode_path != expected:
                self.add_check(
                    "VS Code Python Path",
                    False,
                    f"Got {vscode_path}, expected {expected}"
                )
                return False
            
            self.add_check(
                "VS Code Python Path",
                True,
                vscode_path
            )
            
            # Test absolute path resolution
            try:
                abs_python = get_absolute_venv_python()
                self.add_check(
                    "Virtual Environment Python",
                    True,
                    str(abs_python)
                )
            except FileNotFoundError as e:
                self.add_check(
                    "Virtual Environment Python",
                    False,
                    str(e)
                )
                return False
            
            return True
            
        except Exception as e:
            self.add_check("Virtual Environment Paths", False, str(e))
            return False
    
    def verify_vscode_settings(self) -> bool:
        """Verify VS Code MCP configuration."""
        settings_path = self.workspace / ".vscode" / "settings.json"
        
        if not settings_path.exists():
            self.add_check(
                "VS Code Settings",
                False,
                ".vscode/settings.json not found"
            )
            return False
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Strip JSONC comments (simple version)
                lines = [
                    line for line in content.splitlines()
                    if not line.strip().startswith('//')
                ]
                clean_content = '\n'.join(lines)
                settings = json.loads(clean_content)
            
            # Check MCP server configuration
            mcp_servers = settings.get("github.copilot.chat.mcpServers", {})
            cortex_config = mcp_servers.get("cortex")
            
            if not cortex_config:
                self.add_check(
                    "MCP Server Config",
                    False,
                    "cortex server not configured"
                )
                return False
            
            # Verify command uses correct path
            command = cortex_config.get("command", "")
            expected_python = get_venv_python_path()
            
            if command != expected_python:
                self.add_check(
                    "MCP Server Command",
                    False,
                    f"Command is '{command}', expected '{expected_python}'"
                )
                return False
            
            self.add_check(
                "MCP Server Config",
                True,
                f"CORTEX configured with {command}"
            )
            return True
            
        except json.JSONDecodeError as e:
            self.add_check(
                "VS Code Settings",
                False,
                f"Invalid JSON: {e}"
            )
            return False
        except Exception as e:
            self.add_check(
                "VS Code Settings",
                False,
                str(e)
            )
            return False
    
    def verify_mcp_module(self) -> bool:
        """Verify MCP module exists and imports."""
        try:
            from cortex.mcp.server import MCPServer
            
            server = MCPServer()
            tools = server.list_tools()
            
            self.add_check(
                "MCP Module",
                True,
                f"Server initialized with {len(tools)} tools"
            )
            return True
            
        except ImportError as e:
            self.add_check(
                "MCP Module",
                False,
                f"Import failed: {e}"
            )
            return False
        except Exception as e:
            self.add_check(
                "MCP Module",
                False,
                f"Initialization failed: {e}"
            )
            return False
    
    def verify_utf8_encoding(self) -> bool:
        """Verify UTF-8 encoding in critical files."""
        try:
            from cortex.wiring.registry.git_backed_registry import GitBackedRegistry
            
            # This will fail if UTF-8 encoding is not set on Windows
            registry = GitBackedRegistry()
            
            self.add_check(
                "UTF-8 Encoding",
                True,
                "git_backed_registry.py loads successfully"
            )
            return True
            
        except UnicodeDecodeError as e:
            self.add_check(
                "UTF-8 Encoding",
                False,
                f"Encoding error: {e}"
            )
            return False
        except Exception as e:
            self.add_check(
                "UTF-8 Encoding",
                False,
                str(e)
            )
            return False
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("=" * 80)
        print("CORTEX Cross-Platform Setup Verification")
        print("=" * 80)
        print()
        
        # Run checks
        self.verify_platform_detection()
        self.verify_venv_paths()
        self.verify_vscode_settings()
        self.verify_mcp_module()
        self.verify_utf8_encoding()
        
        print()
        print("=" * 80)
        
        # Summary
        passed = sum(1 for _, p, _ in self.checks if p)
        total = len(self.checks)
        
        if passed == total:
            print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
            print("=" * 80)
            print()
            print("🎉 CORTEX setup verified successfully!")
            print("   Next: Reload VS Code to activate MCP integration")
            print()
            return True
        else:
            failed = total - passed
            print(f"❌ {failed}/{total} CHECKS FAILED")
            print("=" * 80)
            print()
            print("Failed checks:")
            for name, passed, message in self.checks:
                if not passed:
                    print(f"  • {name}: {message}")
            print()
            print("Fix: Review .github/CROSS-PLATFORM-SETUP.md")
            print()
            return False


def main() -> int:
    """Main entry point."""
    verifier = SetupVerifier()
    success = verifier.run_all_checks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
