"""
Build MkDocs site module for automated documentation.

Part of the Documentation Update operation - builds the documentation site using MkDocs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class BuildMkDocsSiteModule(BaseOperationModule):
    """
    Build documentation site with MkDocs.
    
    Executes `mkdocs build` to generate static HTML documentation
    from Markdown source files. Validates that MkDocs is installed
    and handles build errors gracefully.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="build_mkdocs_site",
            name="Build MkDocs Site",
            description="Build documentation site with MkDocs",
            phase=OperationPhase.PROCESSING,
            priority=20
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute MkDocs build.
        
        Args:
            context: Operation context
            
        Returns:
            OperationResult with build status
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            mkdocs_config = project_root / "mkdocs.yml"
            
            # Check if mkdocs.yml exists
            if not mkdocs_config.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="mkdocs.yml not found",
                    errors=[f"Configuration file not found at {mkdocs_config}"]
                )
            
            self.log_info("Building MkDocs site...")
            
            # Check if mkdocs is installed
            if not self._check_mkdocs_installed():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="MkDocs not installed",
                    errors=["Install with: pip install mkdocs mkdocs-material"]
                )
            
            # Build site
            build_result = self._build_site(project_root)
            
            if build_result["success"]:
                self.log_info(f"MkDocs site built successfully")
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Documentation site built successfully",
                    data={
                        "site_directory": str(project_root / "site"),
                        "build_time": build_result.get("build_time", 0),
                        "pages_built": build_result.get("pages_built", 0)
                    }
                )
            else:
                self.log_error(f"MkDocs build failed: {build_result['error']}")
                
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="MkDocs build failed",
                    errors=[build_result.get("error", "Build failed")]
                )
            
        except Exception as e:
            self.log_error(f"Failed to build MkDocs site: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="MkDocs build failed",
                errors=[str(e)]
            )
    
    def _check_mkdocs_installed(self) -> bool:
        """
        Check if MkDocs is installed.
        
        Returns:
            True if MkDocs is available
        """
        try:
            # Try using Python module first (more reliable)
            result = subprocess.run(
                ["python3", "-m", "mkdocs", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
            
            # Fallback to command-line mkdocs
            result = subprocess.run(
                ["mkdocs", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _build_site(self, project_root: Path) -> Dict[str, Any]:
        """
        Build the MkDocs site.
        
        Args:
            project_root: Project root directory
            
        Returns:
            Build result with success status and details
        """
        try:
            # Run mkdocs build using Python module (more reliable)
            result = subprocess.run(
                ["python3", "-m", "mkdocs", "build", "--strict"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse output for statistics
                output_lines = result.stdout.split('\n')
                pages_built = self._count_built_pages(output_lines)
                
                return {
                    "success": True,
                    "pages_built": pages_built,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "returncode": result.returncode
                }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Build timeout exceeded (60 seconds)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _count_built_pages(self, output_lines: List[str]) -> int:
        """
        Count number of pages built from output.
        
        Args:
            output_lines: Build output lines
            
        Returns:
            Number of pages built
        """
        count = 0
        for line in output_lines:
            if "Building" in line or "INFO" in line and ".md" in line:
                count += 1
        return count


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return BuildMkDocsSiteModule()
