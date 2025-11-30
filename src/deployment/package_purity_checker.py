"""
Package Purity Checker - Admin Module Leak Prevention

Ensures no admin-only modules leak into user packages:
- Scans package contents for admin directories
- Validates admin command removal from prompts
- Checks for admin triggers in response templates
- Monitors file additions during build

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)


class PackagePurityChecker:
    """
    Package purity validator for deployments.
    
    Ensures admin-only code doesn't leak into user packages.
    """
    
    # Admin-only paths that should NEVER be in user packages
    ADMIN_EXCLUSIONS = [
        "cortex-brain/admin/",
        "src/operations/modules/admin/",
        "src/deployment/",
        "tests/admin/",
        "scripts/validate_alignment.py",
        "scripts/deploy_cortex.py",
        ".github/workflows/deploy.yml"
    ]
    
    # Admin commands that should be stripped from prompts
    ADMIN_COMMANDS = [
        "align",
        "system alignment",
        "deploy cortex",
        "validate alignment"
    ]
    
    def __init__(self, package_root: Path, project_root: Path):
        """
        Initialize package purity checker.
        
        Args:
            package_root: Root of built package (e.g., dist/)
            project_root: Root of source project
        """
        self.package_root = Path(package_root)
        self.project_root = Path(project_root)
    
    def validate_purity(self) -> Dict[str, Any]:
        """
        Validate package purity.
        
        Returns:
            Validation results with detected leaks
        """
        results = {
            "is_pure": True,
            "admin_leaks": [],
            "prompt_leaks": [],
            "template_leaks": [],
            "unexpected_files": []
        }
        
        # Check for admin directory leaks
        admin_leaks = self._check_admin_directories()
        if admin_leaks:
            results["is_pure"] = False
            results["admin_leaks"] = admin_leaks
        
        # Check for admin commands in prompts
        prompt_leaks = self._check_prompt_sanitization()
        if prompt_leaks:
            results["is_pure"] = False
            results["prompt_leaks"] = prompt_leaks
        
        # Check for admin triggers in templates
        template_leaks = self._check_template_sanitization()
        if template_leaks:
            results["is_pure"] = False
            results["template_leaks"] = template_leaks
        
        # Check for unexpected file additions
        unexpected = self._check_unexpected_files()
        if unexpected:
            results["unexpected_files"] = unexpected
        
        return results
    
    def _check_admin_directories(self) -> List[str]:
        """
        Check for admin directories in package.
        
        Returns:
            List of admin paths found in package
        """
        leaks = []
        
        for admin_path in self.ADMIN_EXCLUSIONS:
            full_path = self.package_root / admin_path
            if full_path.exists():
                leaks.append(str(full_path.relative_to(self.package_root)))
        
        return leaks
    
    def _check_prompt_sanitization(self) -> List[str]:
        """
        Check if admin commands removed from prompts.
        
        Returns:
            List of admin commands still in prompts
        """
        leaks = []
        
        # Check main prompt
        prompt_path = self.package_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if not prompt_path.exists():
            return leaks
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            
            for command in self.ADMIN_COMMANDS:
                if command.lower() in content:
                    leaks.append(f"Command '{command}' found in CORTEX.prompt.md")
        
        except Exception as e:
            logger.warning(f"Failed to check prompt sanitization: {e}")
        
        return leaks
    
    def _check_template_sanitization(self) -> List[str]:
        """
        Check if admin triggers removed from templates.
        
        Returns:
            List of admin triggers still in templates
        """
        leaks = []
        
        templates_path = self.package_root / "cortex-brain" / "response-templates.yaml"
        if not templates_path.exists():
            return leaks
        
        try:
            with open(templates_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            templates = data.get("templates", {})
            
            for template_name, template_data in templates.items():
                triggers = template_data.get("triggers", [])
                
                for trigger in triggers:
                    if any(cmd.lower() in trigger.lower() for cmd in self.ADMIN_COMMANDS):
                        leaks.append(f"Admin trigger '{trigger}' in template '{template_name}'")
        
        except Exception as e:
            logger.warning(f"Failed to check template sanitization: {e}")
        
        return leaks
    
    def _check_unexpected_files(self) -> List[Dict[str, Any]]:
        """
        Check for unexpected file additions.
        
        Returns:
            List of unexpected files with metadata
        """
        unexpected = []
        
        # Common files that should exist
        expected_patterns = {
            ".github/prompts/*.md",
            "cortex-brain/**/*.yaml",
            "cortex-brain/**/*.db",
            "src/**/*.py",
            "tests/**/*.py",
            "*.md",
            "*.json",
            "*.txt"
        }
        
        # Scan package for all files
        all_files = list(self.package_root.rglob("*"))
        
        for file_path in all_files:
            if file_path.is_dir():
                continue
            
            # Check if file matches expected patterns
            relative_path = file_path.relative_to(self.package_root)
            
            # Skip if matches any expected pattern
            is_expected = any(
                relative_path.match(pattern)
                for pattern in expected_patterns
            )
            
            if not is_expected and file_path.suffix not in [".pyc", ".pyo", ".pyd"]:
                unexpected.append({
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix
                })
        
        return unexpected
    
    def get_package_manifest(self) -> Dict[str, Any]:
        """
        Get complete package manifest.
        
        Returns:
            Package manifest with all files and metadata
        """
        manifest = {
            "total_files": 0,
            "total_size_bytes": 0,
            "files_by_type": {},
            "directories": []
        }
        
        all_files = list(self.package_root.rglob("*"))
        
        for file_path in all_files:
            if file_path.is_dir():
                manifest["directories"].append(str(file_path.relative_to(self.package_root)))
            else:
                manifest["total_files"] += 1
                size = file_path.stat().st_size
                manifest["total_size_bytes"] += size
                
                # Count by type
                ext = file_path.suffix or "no_extension"
                if ext not in manifest["files_by_type"]:
                    manifest["files_by_type"][ext] = {"count": 0, "total_size": 0}
                
                manifest["files_by_type"][ext]["count"] += 1
                manifest["files_by_type"][ext]["total_size"] += size
        
        return manifest
