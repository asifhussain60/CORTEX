#!/usr/bin/env python3
"""
CORTEX MCP Setup Automation - Production Readiness Script

Automatically configures VS Code, MCP server, and validates environment
for 100% production readiness. Fixes GAP-001 (MCP Server Setup).

Author: CORTEX Framework
Version: 1.0.0
"""

import json
import os
import sys
import subprocess
import socket
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SetupResult:
    """Result of setup operation."""
    success: bool
    message: str
    details: Dict[str, Any]
    

class CORTEXMCPSetup:
    """Automated CORTEX MCP setup for production readiness."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize MCP setup manager.
        
        Args:
            workspace_root: Root of CORTEX workspace (auto-detected if None)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.vscode_dir = self.workspace_root / ".vscode"
        self.settings_file = self.vscode_dir / "settings.json"
        self.setup_log = self.workspace_root / ".cortex" / "setup.log"
        
        # Ensure directories exist
        self.vscode_dir.mkdir(exist_ok=True)
        (self.workspace_root / ".cortex").mkdir(exist_ok=True)
    
    def run_full_setup(self) -> SetupResult:
        """Run complete MCP setup process.
        
        Returns:
            SetupResult with overall success/failure
        """
        logger.info("🚀 Starting CORTEX MCP Setup...")
        
        steps = [
            ("Validate Environment", self._validate_environment),
            ("Configure VS Code Settings", self._configure_vscode),
            ("Start MCP Server", self._start_mcp_server),
            ("Validate MCP Tools", self._validate_mcp_tools),
            ("Test Health Endpoint", self._test_health_endpoint),
        ]
        
        results = {}
        overall_success = True
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            try:
                result = step_func()
                results[step_name] = result
                
                if result.success:
                    logger.info(f"✅ {step_name}: {result.message}")
                else:
                    logger.error(f"❌ {step_name}: {result.message}")
                    overall_success = False
                    break
                    
            except Exception as e:
                error_msg = f"Exception in {step_name}: {str(e)}"
                logger.error(f"💥 {error_msg}")
                results[step_name] = SetupResult(False, error_msg, {})
                overall_success = False
                break
        
        # Log final status
        status = "✅ SETUP COMPLETE" if overall_success else "❌ SETUP FAILED"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp}: {status}\n"
        try:
            with open(self.setup_log, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            logger.warning(f"Failed to write setup log: {e}")
        
        return SetupResult(
            success=overall_success,
            message=status,
            details=results
        )
    
    def _validate_environment(self) -> SetupResult:
        """Validate Python and dependencies."""
        # Check Python version
        if sys.version_info < (3, 9):
            return SetupResult(
                False, 
                f"Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}",
                {"python_version": sys.version}
            )
        
        # Check critical dependencies
        required_packages = [
            "fastapi", "uvicorn", "pydantic", "pyyaml"
        ]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return SetupResult(
                False,
                f"Missing packages: {', '.join(missing_packages)}. Run: pip install -r requirements.txt",
                {"missing_packages": missing_packages}
            )
        
        return SetupResult(
            True,
            f"Environment validated: Python {sys.version_info.major}.{sys.version_info.minor}",
            {"python_version": sys.version, "packages_ok": True}
        )
    
    def _configure_vscode(self) -> SetupResult:
        """Configure VS Code settings for MCP."""
        mcp_config = {
            "github.copilot.chat.mcpServers": {
                "cortex": {
                    "command": "python",
                    "args": [
                        "-m", "cortex.mcp.server"
                    ],
                    "env": {
                        "CORTEX_MCP_ENABLED": "true",
                        "CORTEX_ENV": "development"
                    }
                }
            }
        }
        
        # Load existing settings or create new
        existing_settings = {}
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    existing_settings = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Could not read existing settings: {e}")
        
        # Merge MCP config
        existing_settings.update(mcp_config)
        
        # Write updated settings
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(existing_settings, f, indent=2)
            
            return SetupResult(
                True,
                f"VS Code settings configured: {self.settings_file}",
                {"settings_path": str(self.settings_file), "config": mcp_config}
            )
        except Exception as e:
            return SetupResult(
                False,
                f"Failed to write VS Code settings: {e}",
                {"error": str(e)}
            )
    
    def _start_mcp_server(self) -> SetupResult:
        """Start MCP server in background."""
        # Check if server is already running
        if self._is_port_open(8000):
            return SetupResult(
                True,
                "MCP server already running on port 8000",
                {"port": 8000, "status": "already_running"}
            )
        
        # Start server
        try:
            cmd = [sys.executable, "-m", "cortex.mcp.server"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.workspace_root
            )
            
            # Wait for server to start
            max_retries = 10
            for i in range(max_retries):
                time.sleep(1)
                if self._is_port_open(8000):
                    return SetupResult(
                        True,
                        f"MCP server started successfully (PID: {process.pid})",
                        {"port": 8000, "pid": process.pid, "status": "started"}
                    )
            
            return SetupResult(
                False,
                "MCP server did not start within 10 seconds",
                {"timeout": True}
            )
            
        except Exception as e:
            return SetupResult(
                False,
                f"Failed to start MCP server: {e}",
                {"error": str(e)}
            )
    
    def _validate_mcp_tools(self) -> SetupResult:
        """Validate that core MCP tools are available."""
        try:
            # Import and test tool discovery
            from cortex.mcp.server import MCPServer
            
            server = MCPServer()
            tools = server.list_tools()
            
            # Check for core tools
            required_tools = [
                "cortex_process_request",
                "cortex_lens_analyze", 
                "cortex_challenge",
                "cortex_total_recall"
            ]
            
            available_tools = {tool['name'] for tool in tools}
            missing_tools = set(required_tools) - available_tools
            
            if missing_tools:
                return SetupResult(
                    False,
                    f"Missing core MCP tools: {', '.join(missing_tools)}",
                    {"missing_tools": list(missing_tools), "available_count": len(tools)}
                )
            
            return SetupResult(
                True,
                f"All {len(required_tools)} core MCP tools available ({len(tools)} total)",
                {"core_tools": required_tools, "total_tools": len(tools)}
            )
            
        except Exception as e:
            return SetupResult(
                False,
                f"Failed to validate MCP tools: {e}",
                {"error": str(e)}
            )
    
    def _test_health_endpoint(self) -> SetupResult:
        """Test MCP server health endpoint."""
        try:
            import urllib.request
            import urllib.error
            
            url = "http://localhost:8000/health"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode('utf-8')
                health_data = json.loads(data)
                
                if health_data.get('status') in ['healthy', 'ok']:
                    return SetupResult(
                        True,
                        f"Health endpoint responding: {health_data.get('status')}",
                        {"health_data": health_data, "url": url}
                    )
                else:
                    return SetupResult(
                        False,
                        f"Health endpoint unhealthy: {health_data}",
                        {"health_data": health_data}
                    )
                    
        except Exception as e:
            return SetupResult(
                False,
                f"Health endpoint not accessible: {e}",
                {"error": str(e), "url": url}
            )
    
    def _is_port_open(self, port: int, host: str = "localhost") -> bool:
        """Check if port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False


def main():
    """Main entry point."""
    print("🧠 CORTEX MCP Setup - Production Readiness")
    print("=" * 50)
    
    # Find workspace root
    workspace_root = Path.cwd()
    if not (workspace_root / "cortex" / "__init__.py").exists():
        print("❌ Not in CORTEX workspace. Run from project root.")
        sys.exit(1)
    
    # Run setup
    setup = CORTEXMCPSetup(workspace_root)
    result = setup.run_full_setup()
    
    print("=" * 50)
    if result.success:
        print("✅ CORTEX MCP Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Restart VS Code: Ctrl+Shift+P → Developer: Reload Window")
        print("2. Verify in Copilot Chat: Ask 'list cortex tools'")
        print("3. Test with: 'cortex audit this repository'")
    else:
        print("❌ CORTEX MCP Setup Failed!")
        print(f"\n💡 Error: {result.message}")
        print("\n🔧 Troubleshooting:")
        print("- Ensure you're in the CORTEX workspace root")
        print("- Run: pip install -r requirements.txt")
        print("- Check Python version: python --version (need 3.9+)")
        sys.exit(1)


if __name__ == "__main__":
    main()