"""
Admin Dashboard Launcher Module

Purpose: Launch enhanced CORTEX dashboard with repository selector dropdown.
         ADMIN ONLY - not included in production builds.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

SECURITY: This module is admin-only and blocked from production by:
- deployment_tier: admin in cortex-operations.yaml
- Listed in publish-config.yaml admin_operations exclusion
- Validation gate in deployment pipeline
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AdminDashboardLauncherModule:
    """
    Launch CORTEX dashboard with repository selector.
    
    Admin Features:
    - Lists all available dashboard data directories
    - Provides dropdown selector UI
    - Remembers last selected repository
    - Auto-detects new repositories
    """
    
    def __init__(self):
        """Initialize admin dashboard launcher."""
        self.logger = logging.getLogger(__name__)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute admin dashboard launch.
        
        Args:
            context: Execution context with options
        
        Returns:
            Result dictionary
        """
        try:
            # Validate this is admin repository
            if not self._is_admin_repo():
                return {
                    "success": False,
                    "error": "admin_only_feature",
                    "message": (
                        "❌ Admin Dashboard is only available in CORTEX development repository.\n\n"
                        "This feature is admin-only and not available in user installations.\n"
                        "Use 'load dashboard' for standard dashboard functionality."
                    )
                }
            
            # Get all available repositories
            repos = self._discover_repositories()
            
            if not repos:
                return {
                    "success": False,
                    "error": "no_repositories",
                    "message": (
                        "❌ No dashboard data found.\n\n"
                        "Generate dashboard data first:\n"
                        "  python -m src.orchestrators.dashboard_collector --path \"C:\\Path\\To\\Repo\""
                    )
                }
            
            # Get last selected or default repository
            default_repo = self._get_last_selected_repo() or repos[0]
            
            # Launch dashboard in persistent terminal window
            import subprocess
            import sys
            import os
            
            port = context.get('port', 8080)
            auto_open = context.get('auto_open', True)
            source = default_repo['name']
            
            # Get current working directory
            cortex_root = Path(__file__).parent.parent.parent.parent
            
            # Build command for dashboard launcher
            python_cmd = f"python -m src.orchestrators.dashboard_launcher --port {port} --source {source}"
            if not auto_open:
                python_cmd += " --no-browser"
            
            # Launch in new terminal window (platform-specific)
            try:
                if sys.platform == "win32":
                    # Windows: Use PowerShell Start-Process with -NoExit
                    ps_cmd = [
                        "powershell",
                        "-Command",
                        f"Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd {cortex_root}; {python_cmd}'"
                    ]
                    
                    process = subprocess.Popen(
                        ps_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL
                    )
                else:
                    # Unix: Use terminal emulator
                    term_cmd = f"cd {cortex_root} && {python_cmd}"
                    process = subprocess.Popen(
                        ["x-terminal-emulator", "-e", "bash", "-c", term_cmd],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True
                    )
                
                # Wait for server to start
                import time
                time.sleep(3)
                
                # Build repository selector info
                repo_list = "\n".join([
                    f"  • {repo['name']} ({repo['type']}) - {repo['files']} files"
                    for repo in repos
                ])
                
                url = f"http://localhost:{port}/ui/index.html?source={source}"
                
                message = (
                    f"✅ Admin Dashboard launched in new terminal window!\n\n"
                    f"🌐 URL: {url}\n"
                    f"🔌 Port: {port}\n"
                    f"📊 Currently viewing: {default_repo['name']}\n\n"
                    f"📁 Available Repositories ({len(repos)}):\n{repo_list}\n\n"
                    f"💡 To switch repositories:\n"
                    f"  1. Use the dropdown selector in the dashboard UI\n"
                    f"  2. Or close the terminal and relaunch with different source\n\n"
                    f"🛑 To stop server:\n"
                    f"  • Close the PowerShell window running the dashboard\n"
                    f"  • Or press Ctrl+C in that window\n"
                )
                
                # Save last selected
                self._save_last_selected_repo(default_repo)
                
                # Return serializable result
                return {
                    "success": True,
                    "port": port,
                    "url": url,
                    "message": message
                }
                
            except Exception as e:
                self.logger.error(f"Failed to launch background process: {e}")
                return {
                    "success": False,
                    "error": "process_launch_failed",
                    "message": f"❌ Failed to start dashboard process: {e}"
                }
            
        except Exception as e:
            self.logger.error(f"Admin dashboard launch failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "launch_failed",
                "message": f"❌ Failed to launch admin dashboard: {e}"
            }
    
    def _is_admin_repo(self) -> bool:
        """
        Check if running in CORTEX development repository.
        
        Returns:
            True if admin repo, False otherwise
        """
        try:
            # Check for admin markers
            cortex_root = Path(__file__).parent.parent.parent.parent
            
            admin_markers = [
                cortex_root / "cortex-brain" / "admin",
                cortex_root / "cortex-brain" / "cortex-3.0-design",
                cortex_root / "tests",
                cortex_root / "docs" / "architecture"
            ]
            
            # At least 2 admin markers must exist
            existing = sum(1 for marker in admin_markers if marker.exists())
            return existing >= 2
            
        except Exception as e:
            self.logger.warning(f"Admin repo check failed: {e}")
            return False
    
    def _discover_repositories(self) -> list:
        """
        Discover all available dashboard data directories.
        
        Returns:
            List of repository info dicts
        """
        try:
            cortex_root = Path(__file__).parent.parent.parent.parent
            dashboards_dir = cortex_root / "cortex-brain" / "dashboards"
            
            if not dashboards_dir.exists():
                return []
            
            repos = []
            
            # Scan for data directories
            for item in dashboards_dir.iterdir():
                if not item.is_dir():
                    continue
                
                # Skip special directories
                if item.name in ['ui', 'schema', '.git']:
                    continue
                
                # Check for health-data.json (indicates valid dashboard data)
                health_file = item / "health-data.json"
                metadata_file = item / "metadata.json"
                
                if health_file.exists():
                    repo_info = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'Unknown',
                        'files': 0
                    }
                    
                    # Load metadata if available
                    if metadata_file.exists():
                        try:
                            import json
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                repo_info['type'] = metadata.get('repository_name', item.name)
                                
                            # Load health data for file count
                            with open(health_file, 'r') as f:
                                health = json.load(f)
                                if 'summary' in health:
                                    repo_info['files'] = health['summary'].get('total_files', 0)
                        except Exception as e:
                            self.logger.warning(f"Failed to load metadata for {item.name}: {e}")
                    
                    repos.append(repo_info)
            
            # Sort by name
            repos.sort(key=lambda x: x['name'])
            return repos
            
        except Exception as e:
            self.logger.error(f"Repository discovery failed: {e}")
            return []
    
    def _get_last_selected_repo(self) -> Optional[Dict[str, Any]]:
        """
        Get last selected repository from cache.
        
        Returns:
            Repository info or None
        """
        try:
            cortex_root = Path(__file__).parent.parent.parent.parent
            cache_file = cortex_root / "cortex-brain" / "cache" / "admin_dashboard_last_repo.json"
            
            if cache_file.exists():
                import json
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.debug(f"Could not load last selected repo: {e}")
        
        return None
    
    def _save_last_selected_repo(self, repo_info: Dict[str, Any]) -> None:
        """
        Save last selected repository to cache.
        
        Args:
            repo_info: Repository information
        """
        try:
            cortex_root = Path(__file__).parent.parent.parent.parent
            cache_dir = cortex_root / "cortex-brain" / "cache"
            cache_dir.mkdir(exist_ok=True)
            
            cache_file = cache_dir / "admin_dashboard_last_repo.json"
            
            import json
            with open(cache_file, 'w') as f:
                json.dump(repo_info, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Could not save last selected repo: {e}")


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Module entry point.
    
    Args:
        context: Execution context
    
    Returns:
        Result dictionary
    """
    module = AdminDashboardLauncherModule()
    return module.execute(context)
