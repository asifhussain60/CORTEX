"""
Publish documentation module for documentation deployment.

Part of the Documentation Update operation - deploys generated docs to MkDocs site.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class PublishDocumentationModule(BaseOperationModule):
    """
    Publish documentation to MkDocs site.
    
    Handles:
    - Copying generated API docs to MkDocs docs/ directory
    - Updating mkdocs.yml navigation
    - Building MkDocs site (optional)
    - Deployment to GitHub Pages (optional)
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="publish_documentation",
            name="Publish Documentation",
            description="Deploy documentation to MkDocs site",
            phase=OperationPhase.FINALIZATION,
            priority=30,
            dependencies=["build_documentation"]
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute documentation publishing.
        
        Args:
            context: Operation context with build output info
            
        Returns:
            OperationResult with publish status
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            api_docs_dir = project_root / "docs" / "api"
            mkdocs_docs_dir = project_root / "docs"
            
            self.log_info(f"Publishing documentation from {api_docs_dir}")
            
            # Verify API docs exist
            if not api_docs_dir.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="API documentation not found",
                    errors=[f"{api_docs_dir} does not exist"]
                )
            
            # Get publish options from context
            build_site = context.get("build_site", False)
            deploy = context.get("deploy", False)
            
            actions_performed = []
            
            # 1. Verify documentation structure
            self.log_info("Verifying documentation structure...")
            verification = self._verify_docs_structure(api_docs_dir)
            
            if not verification["valid"]:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Documentation structure invalid",
                    errors=verification["errors"]
                )
            
            actions_performed.append("Verified documentation structure")
            
            # 2. Update MkDocs navigation (if mkdocs.yml exists)
            mkdocs_yml = project_root / "mkdocs.yml"
            if mkdocs_yml.exists():
                self.log_info("Updating MkDocs navigation...")
                self._update_mkdocs_nav(mkdocs_yml, api_docs_dir)
                actions_performed.append("Updated mkdocs.yml navigation")
            else:
                self.log_warning("mkdocs.yml not found - skipping navigation update")
            
            # 3. Build MkDocs site (optional)
            if build_site:
                self.log_info("Building MkDocs site...")
                build_result = self._build_mkdocs_site(project_root)
                
                if build_result["success"]:
                    actions_performed.append(f"Built MkDocs site: {build_result['output_dir']}")
                else:
                    self.log_warning(f"MkDocs build failed: {build_result['error']}")
            
            # 4. Deploy to GitHub Pages (optional)
            if deploy:
                self.log_info("Deploying to GitHub Pages...")
                deploy_result = self._deploy_to_github_pages(project_root)
                
                if deploy_result["success"]:
                    actions_performed.append("Deployed to GitHub Pages")
                else:
                    self.log_warning(f"Deployment failed: {deploy_result['error']}")
            
            files_published = len(list(api_docs_dir.rglob("*.md")))
            
            self.log_info(
                f"Documentation published: {files_published} files, "
                f"{len(actions_performed)} actions completed"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Published {files_published} documentation files",
                data={
                    "files_published": files_published,
                    "actions_performed": actions_performed,
                    "docs_location": str(api_docs_dir),
                    "site_built": build_site,
                    "deployed": deploy
                }
            )
            
        except Exception as e:
            self.log_error(f"Failed to publish documentation: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Documentation publish failed",
                errors=[str(e)]
            )
    
    def _verify_docs_structure(self, docs_dir: Path) -> Dict[str, Any]:
        """
        Verify documentation directory structure.
        
        Args:
            docs_dir: Documentation directory
            
        Returns:
            Verification result dict
        """
        errors = []
        
        # Check for required files
        required_files = ["index.md"]
        for required_file in required_files:
            file_path = docs_dir / required_file
            if not file_path.exists():
                errors.append(f"Missing required file: {required_file}")
        
        # Check for required directories
        required_dirs = ["modules", "classes", "functions"]
        for required_dir in required_dirs:
            dir_path = docs_dir / required_dir
            if not dir_path.exists():
                errors.append(f"Missing required directory: {required_dir}")
            elif not any(dir_path.glob("*.md")):
                errors.append(f"Directory {required_dir} contains no markdown files")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _update_mkdocs_nav(self, mkdocs_yml: Path, api_docs_dir: Path) -> None:
        """
        Update MkDocs navigation to include API docs.
        
        Args:
            mkdocs_yml: Path to mkdocs.yml
            api_docs_dir: API documentation directory
        """
        try:
            # Read existing mkdocs.yml
            content = mkdocs_yml.read_text(encoding='utf-8')
            
            # Check if API Reference section already exists
            if "API Reference:" in content:
                self.log_info("API Reference section already exists in mkdocs.yml")
                return
            
            # Add API Reference to navigation
            api_nav_entry = """
  - API Reference:
    - Overview: api/index.md
    - Modules: api/modules/
    - Classes: api/classes/
    - Functions: api/functions/
"""
            
            # Find nav section and append
            if "nav:" in content:
                # Insert before the last line or at the end
                lines = content.split('\n')
                nav_index = next(i for i, line in enumerate(lines) if line.strip().startswith('nav:'))
                
                # Insert API Reference at the end of nav section
                lines.insert(len(lines) - 1, api_nav_entry)
                
                new_content = '\n'.join(lines)
                mkdocs_yml.write_text(new_content, encoding='utf-8')
                
                self.log_info("Added API Reference to mkdocs.yml navigation")
            else:
                self.log_warning("No 'nav:' section found in mkdocs.yml")
                
        except Exception as e:
            self.log_warning(f"Failed to update mkdocs.yml: {e}")
    
    def _build_mkdocs_site(self, project_root: Path) -> Dict[str, Any]:
        """
        Build MkDocs site.
        
        Args:
            project_root: Project root directory
            
        Returns:
            Build result dict
        """
        try:
            # Check if mkdocs is installed
            result = subprocess.run(
                ["mkdocs", "--version"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "MkDocs not installed. Install with: pip install mkdocs"
                }
            
            # Build site
            result = subprocess.run(
                ["mkdocs", "build", "--clean"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            output_dir = project_root / "site"
            
            return {
                "success": True,
                "output_dir": str(output_dir),
                "stdout": result.stdout
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": "mkdocs command not found. Install with: pip install mkdocs"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _deploy_to_github_pages(self, project_root: Path) -> Dict[str, Any]:
        """
        Deploy site to GitHub Pages using mkdocs gh-deploy.
        
        Args:
            project_root: Project root directory
            
        Returns:
            Deploy result dict
        """
        try:
            # Check if in git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Not in a git repository"
                }
            
            # Deploy using mkdocs
            result = subprocess.run(
                ["mkdocs", "gh-deploy", "--clean"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "stdout": result.stdout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
