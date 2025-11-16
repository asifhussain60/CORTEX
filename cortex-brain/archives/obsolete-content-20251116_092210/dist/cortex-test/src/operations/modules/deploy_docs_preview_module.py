"""
Deploy documentation preview module.

Part of the Documentation Update operation - deploys or serves documentation preview.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class DeployDocsPreviewModule(BaseOperationModule):
    """
    Deploy documentation preview.
    
    Starts a local MkDocs server for documentation preview,
    or optionally deploys to GitHub Pages (if configured).
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="deploy_docs_preview",
            name="Deploy Documentation Preview",
            description="Deploy documentation to preview server",
            phase=OperationPhase.FINALIZATION,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute documentation preview deployment.
        
        Args:
            context: Operation context
            
        Returns:
            OperationResult with deployment status
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            mkdocs_config = project_root / "mkdocs.yml"
            
            if not mkdocs_config.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="mkdocs.yml not found",
                    error="Cannot deploy preview without MkDocs configuration"
                )
            
            # Check deployment mode from context
            deploy_mode = context.get("deploy_mode", "local")
            
            if deploy_mode == "local":
                result = self._start_local_server(project_root)
            elif deploy_mode == "github":
                result = self._deploy_to_github(project_root)
            else:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"Unknown deploy mode: {deploy_mode}",
                    error="Valid modes: local, github"
                )
            
            return result
            
        except Exception as e:
            self.log_error(f"Failed to deploy documentation preview: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Documentation preview deployment failed",
                errors=[str(e)]
            )
    
    def _start_local_server(self, project_root: Path) -> OperationResult:
        """
        Start local MkDocs server.
        
        Args:
            project_root: Project root directory
            
        Returns:
            OperationResult
        """
        try:
            self.log_info("Starting local documentation server...")
            
            # Check if mkdocs is installed
            try:
                subprocess.run(
                    ["mkdocs", "--version"],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="MkDocs not installed",
                    error="Install with: pip install mkdocs mkdocs-material"
                )
            
            # Note: mkdocs serve is a blocking operation
            # For automation, we just provide instructions
            self.log_info("To preview documentation, run: mkdocs serve")
            self.log_info("Then open: http://127.0.0.1:8000")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Documentation preview instructions provided",
                data={
                    "command": "mkdocs serve",
                    "url": "http://127.0.0.1:8000",
                    "note": "Run command manually to start server"
                }
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Failed to start local server",
                errors=[str(e)]
            )
    
    def _deploy_to_github(self, project_root: Path) -> OperationResult:
        """
        Deploy documentation to GitHub Pages.
        
        Args:
            project_root: Project root directory
            
        Returns:
            OperationResult
        """
        try:
            self.log_info("Deploying to GitHub Pages...")
            
            # Run mkdocs gh-deploy
            result = subprocess.run(
                ["mkdocs", "gh-deploy", "--clean", "--message", "Update documentation"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log_info("Documentation deployed to GitHub Pages")
                
                # Extract GitHub Pages URL from git config
                gh_pages_url = self._get_github_pages_url(project_root)
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Documentation deployed to GitHub Pages",
                    data={
                        "url": gh_pages_url,
                        "deployment_output": result.stdout
                    }
                )
            else:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="GitHub Pages deployment failed",
                    error=result.stderr or result.stdout
                )
            
        except subprocess.TimeoutExpired:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Deployment timeout (120 seconds)",
                error="GitHub Pages deployment took too long"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Failed to deploy to GitHub Pages",
                errors=[str(e)]
            )
    
    def _get_github_pages_url(self, project_root: Path) -> str:
        """
        Get GitHub Pages URL from git config.
        
        Args:
            project_root: Project root directory
            
        Returns:
            GitHub Pages URL or empty string
        """
        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
                # Parse GitHub repo from URL
                # Examples:
                # - https://github.com/user/repo.git
                # - git@github.com:user/repo.git
                if "github.com" in remote_url:
                    if remote_url.startswith("https://"):
                        # Extract user/repo from HTTPS URL
                        parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
                    else:
                        # Extract user/repo from SSH URL
                        parts = remote_url.split(":")[1].replace(".git", "").split("/")
                    
                    if len(parts) >= 2:
                        user, repo = parts[0], parts[1]
                        return f"https://{user}.github.io/{repo}/"
            
            return ""
            
        except Exception:
            return ""


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return DeployDocsPreviewModule()
