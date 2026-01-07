"""
Publish Documentation Generator

Handles deployment of generated documentation to GitHub Pages and other platforms.
Builds MkDocs site, validates output, and pushes to deployment branch.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import subprocess
import shutil
import logging

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)

logger = logging.getLogger(__name__)


class PublishDocsGenerator(BaseDocumentationGenerator):
    """
    Publish documentation to GitHub Pages.
    
    Workflow:
    1. Validate all documentation is generated (diagrams, MkDocs, etc.)
    2. Build MkDocs static site
    3. Validate build output
    4. Deploy to gh-pages branch (or configured branch)
    5. Report deployment status and URL
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        super().__init__(config, workspace_root)
        self.docs_path = self.workspace_root / "docs"
        self.site_path = self.workspace_root / "site"
        self.mkdocs_yml = self.workspace_root / "mkdocs.yml"
        
        # Load publish config if available
        self.publish_config = self._load_publish_config()
        
    def get_component_name(self) -> str:
        return "Publish Documentation"
    
    def _load_publish_config(self) -> Dict[str, Any]:
        """Load publish configuration from cortex-brain/publish-config.yaml"""
        config = self.load_config_file("publish-config.yaml")
        if config:
            return config
        
        # Fallback defaults
        return {
            "deployment": {
                "method": "gh-pages",
                "branch": "gh-pages",
                "remote": "origin",
                "message": "Deploy documentation",
                "force": False
            },
            "build": {
                "clean": True,
                "strict": False,
                "site_dir": "site"
            },
            "validation": {
                "check_links": False,
                "check_images": True,
                "min_file_count": 10
            }
        }
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data for publish operation.
        
        Returns:
            Dictionary containing:
            - mkdocs_config: MkDocs configuration info
            - docs_inventory: List of documentation files
            - build_status: MkDocs build validation
            - deployment_target: Where docs will be published
        """
        data = {
            "generated_at": datetime.now().isoformat(),
            "mkdocs_config": self._validate_mkdocs_config(),
            "docs_inventory": self._inventory_docs(),
            "build_status": self._check_existing_build(),
            "deployment_target": self._get_deployment_target()
        }
        
        return data
    
    def _validate_mkdocs_config(self) -> Dict[str, Any]:
        """Validate mkdocs.yml configuration"""
        if not self.mkdocs_yml.exists():
            self.record_error("mkdocs.yml not found")
            return {"valid": False, "error": "mkdocs.yml not found"}
        
        try:
            import yaml
            with open(self.mkdocs_yml) as f:
                config = yaml.safe_load(f)
            
            # Only site_name is required; docs_dir defaults to "docs"
            required_fields = ["site_name"]
            missing = [f for f in required_fields if f not in config]
            
            if missing:
                self.record_error(f"mkdocs.yml missing fields: {missing}")
                return {"valid": False, "error": f"Missing fields: {missing}"}
            
            return {
                "valid": True,
                "site_name": config.get("site_name"),
                "theme": config.get("theme", {}).get("name", "unknown"),
                "docs_dir": config.get("docs_dir", "docs")  # Default value
            }
            
        except Exception as e:
            self.record_error(f"Failed to parse mkdocs.yml: {e}")
            return {"valid": False, "error": str(e)}
    
    def _inventory_docs(self) -> Dict[str, Any]:
        """Inventory documentation files"""
        if not self.docs_path.exists():
            return {"file_count": 0, "has_index": False}
        
        md_files = list(self.docs_path.glob("**/*.md"))
        has_index = (self.docs_path / "index.md").exists()
        
        return {
            "file_count": len(md_files),
            "has_index": has_index,
            "files": [str(f.relative_to(self.docs_path)) for f in md_files]
        }
    
    def _check_existing_build(self) -> Dict[str, Any]:
        """Check if MkDocs site is already built"""
        if not self.site_path.exists():
            return {"exists": False}
        
        html_files = list(self.site_path.glob("**/*.html"))
        
        return {
            "exists": True,
            "file_count": len(html_files),
            "has_index": (self.site_path / "index.html").exists()
        }
    
    def _get_deployment_target(self) -> Dict[str, Any]:
        """Get deployment target information"""
        deploy_config = self.publish_config.get("deployment", {})
        
        return {
            "method": deploy_config.get("method", "gh-pages"),
            "branch": deploy_config.get("branch", "gh-pages"),
            "remote": deploy_config.get("remote", "origin"),
            "url": self._determine_github_pages_url()
        }
    
    def _determine_github_pages_url(self) -> Optional[str]:
        """Determine GitHub Pages URL from git remote"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
                # Parse GitHub URL
                # https://github.com/user/repo.git -> https://user.github.io/repo
                # git@github.com:user/repo.git -> https://user.github.io/repo
                
                if "github.com" in remote_url:
                    # Extract user/repo
                    if remote_url.startswith("https://"):
                        parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
                    elif remote_url.startswith("git@"):
                        parts = remote_url.replace("git@github.com:", "").replace(".git", "").split("/")
                    else:
                        return None
                    
                    if len(parts) >= 2:
                        user, repo = parts[0], parts[1]
                        return f"https://{user}.github.io/{repo}"
            
        except Exception as e:
            self.record_warning(f"Failed to determine GitHub Pages URL: {e}")
        
        return None
    
    def generate(self) -> GenerationResult:
        """
        Build and publish documentation.
        
        Steps:
        1. Validate prerequisites
        2. Build MkDocs site
        3. Validate build output
        4. Deploy to GitHub Pages (if configured)
        """
        self.start_time = datetime.now()
        
        # Collect data and validate
        data = self.collect_data()
        
        # Check prerequisites
        if not data["mkdocs_config"]["valid"]:
            return self._create_failed_result("mkdocs.yml validation failed")
        
        # Get validation config with safe defaults
        validation = self.publish_config.get("validation", {})
        min_file_count = validation.get("min_file_count", 1)  # Default to 1
        
        if data["docs_inventory"]["file_count"] < min_file_count:
            return self._create_failed_result(
                f"Insufficient documentation files: {data['docs_inventory']['file_count']} "
                f"(minimum: {min_file_count})"
            )
        
        # Build MkDocs site
        logger.info("Building MkDocs site...")
        if not self._build_mkdocs():
            return self._create_failed_result("MkDocs build failed")
        
        # Validate build
        logger.info("Validating build output...")
        if not self._validate_build():
            return self._create_failed_result("Build validation failed")
        
        # Deploy (if configured and not dry-run)
        deployment_result = None
        if self.config.metadata and self.config.metadata.get("deploy", False):
            logger.info("Deploying to GitHub Pages...")
            deployment_result = self._deploy_to_github_pages()
        else:
            logger.info("Skipping deployment (dry-run mode)")
            deployment_result = {"deployed": False, "reason": "dry-run mode"}
        
        # Create result metadata
        metadata = {
            "site_built": True,
            "build_path": str(self.site_path),
            "deployment": deployment_result,
            "pages_url": data["deployment_target"]["url"]
        }
        
        return self._create_success_result(metadata)
    
    def _build_mkdocs(self) -> bool:
        """Build MkDocs static site"""
        try:
            # Clean existing build if configured
            if self.publish_config["build"]["clean"] and self.site_path.exists():
                logger.info("Cleaning existing site directory...")
                shutil.rmtree(self.site_path)
            
            # Run mkdocs build
            cmd = ["mkdocs", "build"]
            
            if self.publish_config["build"]["strict"]:
                cmd.append("--strict")
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.record_error(f"mkdocs build failed: {result.stderr}")
                return False
            
            logger.info("MkDocs build completed successfully")
            self.record_file_generated(self.site_path / "index.html")
            return True
            
        except subprocess.TimeoutExpired:
            self.record_error("mkdocs build timed out after 60 seconds")
            return False
        except FileNotFoundError:
            self.record_error("mkdocs command not found - install with: pip install mkdocs")
            return False
        except Exception as e:
            self.record_error(f"mkdocs build error: {e}")
            return False
    
    def _validate_build(self) -> bool:
        """Validate MkDocs build output"""
        if not self.site_path.exists():
            self.record_error("Site directory not found after build")
            return False
        
        # Check index.html exists
        if not (self.site_path / "index.html").exists():
            self.record_error("index.html not found in build output")
            return False
        
        # Count HTML files
        html_files = list(self.site_path.glob("**/*.html"))
        validation = self.publish_config.get("validation", {})
        min_file_count = validation.get("min_file_count", 1)
        
        if len(html_files) < min_file_count:
            self.record_warning(
                f"Build has only {len(html_files)} HTML files "
                f"(expected at least {min_file_count})"
            )
        
        # Check for images if configured
        check_images = validation.get("check_images", False)
        if check_images:
            img_files = list(self.site_path.glob("**/*.{png,jpg,jpeg,gif,svg}"))
            if len(img_files) == 0:
                self.record_warning("No image files found in build output")
        
        logger.info(f"Build validation passed: {len(html_files)} HTML files generated")
        return True
    
    def _deploy_to_github_pages(self) -> Dict[str, Any]:
        """Deploy to GitHub Pages using mkdocs gh-deploy"""
        deploy_config = self.publish_config["deployment"]
        
        try:
            cmd = [
                "mkdocs", "gh-deploy",
                "--remote-branch", deploy_config["branch"],
                "--remote-name", deploy_config["remote"],
                "--message", deploy_config["message"]
            ]
            
            if deploy_config.get("force", False):
                cmd.append("--force")
            
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                self.record_error(f"Deployment failed: {result.stderr}")
                return {
                    "deployed": False,
                    "error": result.stderr
                }
            
            logger.info("Deployment to GitHub Pages completed successfully")
            return {
                "deployed": True,
                "branch": deploy_config["branch"],
                "message": deploy_config["message"]
            }
            
        except subprocess.TimeoutExpired:
            self.record_error("Deployment timed out after 120 seconds")
            return {"deployed": False, "error": "timeout"}
        except Exception as e:
            self.record_error(f"Deployment error: {e}")
            return {"deployed": False, "error": str(e)}
    
    def validate(self) -> bool:
        """
        Validate published documentation.
        
        Checks:
        - MkDocs site built successfully
        - index.html exists
        - Minimum file count met
        """
        if not self.site_path.exists():
            self.record_error("Site directory not found")
            return False
        
        if not (self.site_path / "index.html").exists():
            self.record_error("index.html not found")
            return False
        
        html_files = list(self.site_path.glob("**/*.html"))
        if len(html_files) < self.publish_config["validation"]["min_file_count"]:
            self.record_error(f"Insufficient HTML files: {len(html_files)}")
            return False
        
        logger.info("Publish validation passed")
        return True
