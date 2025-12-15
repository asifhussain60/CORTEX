"""
Cortex Implants Integrator

Provides optional integration of cortex-implants into CORTEX orchestrators.
Implements graceful degradation - system works normally without implants.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from .cortex_implants_loader import (
    CortexImplants,
    load_cortex_implants,
    CortexImplantsLoader
)

logger = logging.getLogger(__name__)


class CortexImplantsIntegrator:
    """
    Integrates cortex-implants with CORTEX orchestrators.
    
    Features:
    - Optional loading (graceful degradation)
    - Repo detection (auto-find implants)
    - Validation augmentation (add company rules)
    - Context enhancement (add company-specific context)
    
    Usage:
        integrator = CortexImplantsIntegrator(repo_path)
        
        # Check if implants present
        if integrator.has_implants():
            # Add company-specific validation
            violations = integrator.validate_against_implants(plan)
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize integrator.
        
        Args:
            repo_path: Repository path (auto-detect if None)
        """
        self.repo_path = repo_path or self._detect_repo()
        self.implants: Optional[CortexImplants] = None
        self._load_implants()
    
    def _detect_repo(self) -> Path:
        """Detect current repository path."""
        # Start from current working directory
        cwd = Path.cwd()
        
        # Check if we're in a repo (has .git or .cortex-implants)
        for parent in [cwd] + list(cwd.parents):
            if (parent / ".git").exists() or (parent / ".cortex-implants").exists():
                return parent
        
        # Default to cwd if no repo detected
        return cwd
    
    def _load_implants(self) -> None:
        """Load cortex-implants if present."""
        try:
            self.implants = load_cortex_implants(self.repo_path)
            if self.implants:
                logger.info(f"🧬 Cortex implants loaded from {self.repo_path}")
                logger.debug(f"   Priority: {self.implants.get_priority()}")
                logger.debug(f"   Rules: {len(self.implants.governance.rules_enabled)}")
        except Exception as e:
            logger.debug(f"No cortex implants found: {e}")
            self.implants = None
    
    def has_implants(self) -> bool:
        """Check if cortex-implants are present."""
        return self.implants is not None
    
    def get_priority(self) -> str:
        """Get implants priority (HIGH/MEDIUM/LOW) or NONE."""
        if not self.has_implants():
            return "NONE"
        return self.implants.get_priority()
    
    def should_override_cortex(self) -> bool:
        """Check if implants should override CORTEX rules."""
        return self.has_implants() and self.get_priority() == "HIGH"
    
    def get_coding_standards(self) -> Optional[Dict[str, Any]]:
        """Get coding standards from implants."""
        if not self.has_implants() or not self.implants.coding_standards:
            return None
        
        # Convert dataclass to dict for orchestrators
        standards = self.implants.coding_standards
        return {
            "naming_conventions": standards.naming_conventions,
            "code_style": standards.code_style,
            "documentation_requirements": standards.documentation_requirements,
            "file_organization": standards.file_organization
        }
    
    def get_architecture_patterns(self) -> Optional[Dict[str, Any]]:
        """Get architecture patterns from implants."""
        if not self.has_implants() or not self.implants.architecture_patterns:
            return None
        
        patterns = self.implants.architecture_patterns
        return {
            "required_patterns": patterns.required_patterns,
            "forbidden_patterns": patterns.forbidden_patterns,
            "layer_architecture": patterns.layer_architecture,
            "design_principles": patterns.design_principles
        }
    
    def get_tech_stack_restrictions(self) -> Optional[Dict[str, Any]]:
        """Get tech stack restrictions from implants."""
        if not self.has_implants() or not self.implants.tech_stack:
            return None
        
        tech = self.implants.tech_stack
        return {
            "approved_libraries": tech.approved_libraries,
            "forbidden_libraries": tech.forbidden_libraries,
            "language_features": tech.language_features
        }
    
    def get_business_rules(self) -> Optional[List[Dict[str, Any]]]:
        """Get business rules from implants."""
        if not self.has_implants() or not self.implants.business_rules:
            return None
        
        rules = self.implants.business_rules
        return [
            {
                "rule_id": rule.get("rule_id"),
                "description": rule.get("description"),
                "validation": rule.get("validation"),
                "test_required": rule.get("test_required", True)
            }
            for rule in (rules.validation_rules or [])
        ]
    
    def get_security_requirements(self) -> Optional[Dict[str, Any]]:
        """Get security requirements from implants."""
        if not self.has_implants() or not self.implants.security_policy:
            return None
        
        security = self.implants.security_policy
        return {
            "authentication_required": security.authentication_required,
            "authorization_required": security.authorization_required,
            "data_classification": security.data_classification,
            "encryption_requirements": security.encryption_requirements
        }
    
    def validate_tech_stack(self, dependencies: List[str]) -> List[str]:
        """
        Validate dependencies against implants tech stack.
        
        Args:
            dependencies: List of libraries to validate
            
        Returns:
            List of validation errors (empty if all valid)
        """
        if not self.has_implants() or not self.implants.tech_stack:
            return []  # No restrictions
        
        tech = self.implants.tech_stack
        violations = []
        
        # Check forbidden libraries
        if tech.forbidden_libraries:
            for dep in dependencies:
                for forbidden_item in tech.forbidden_libraries:
                    forbidden = forbidden_item.get("library", "") if isinstance(forbidden_item, dict) else forbidden_item
                    if forbidden.lower() in dep.lower():
                        reason = forbidden_item.get("reason", "Not allowed") if isinstance(forbidden_item, dict) else "Not allowed"
                        violations.append(
                            f"❌ Forbidden library: {dep} ({reason})"
                        )
        
        # Check approved libraries (if whitelist mode)
        if tech.approved_libraries and len(tech.approved_libraries) > 0:
            # Flatten approved libraries from all languages
            all_approved = []
            for lang_libs in tech.approved_libraries.values():
                if isinstance(lang_libs, list):
                    for lib in lang_libs:
                        if isinstance(lib, dict):
                            all_approved.append(lib.get("name", ""))
                        else:
                            all_approved.append(str(lib))
            
            for dep in dependencies:
                dep_name = dep.split("==")[0].split(">=")[0].strip()
                if not any(approved.lower() in dep_name.lower() 
                          for approved in all_approved if approved):
                    violations.append(
                        f"⚠️  Library not in approved list: {dep}"
                    )
        
        return violations
    
    def validate_architecture(self, plan: Dict[str, Any]) -> List[str]:
        """
        Validate plan against architecture patterns.
        
        Args:
            plan: Feature plan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        if not self.has_implants() or not self.implants.architecture_patterns:
            return []  # No restrictions
        
        patterns = self.implants.architecture_patterns
        violations = []
        
        # Check required patterns present
        if patterns.required_patterns:
            for required in patterns.required_patterns:
                pattern_name = required.get("pattern")
                if pattern_name:
                    # Check if pattern mentioned in plan
                    plan_str = str(plan).lower()
                    if pattern_name.lower() not in plan_str:
                        violations.append(
                            f"⚠️  Required pattern not found: {pattern_name}"
                        )
        
        # Check forbidden patterns absent
        if patterns.anti_patterns:
            plan_str = str(plan).lower()
            for forbidden in patterns.anti_patterns:
                pattern_name = forbidden.get("pattern", "")
                if pattern_name.lower() in plan_str:
                    reason = forbidden.get("reason", "Not recommended")
                    violations.append(
                        f"❌ Anti-pattern detected: {pattern_name} ({reason})"
                    )
        
        return violations
    
    def get_context_summary(self) -> str:
        """
        Get summary of implants for context injection.
        
        Returns:
            Markdown summary of active implants
        """
        if not self.has_implants():
            return ""
        
        gov = self.implants.governance
        lines = [
            "## 🧬 Cortex Implants Active",
            f"**Organization:** {gov.company_name}",
            f"**Project:** {gov.repo_name}",
            f"**Priority:** {self.get_priority()}",
            "",
            "**Active Rules:**"
        ]
        
        if self.implants.coding_standards:
            lines.append("- ✅ Coding Standards")
        if self.implants.architecture_patterns:
            lines.append("- ✅ Architecture Patterns")
        if self.implants.tech_stack:
            lines.append("- ✅ Tech Stack Restrictions")
        if self.implants.business_rules:
            lines.append("- ✅ Business Rules")
        if self.implants.security_policy:
            lines.append("- ✅ Security Policy")
        
        return "\n".join(lines)


# Global singleton for easy access
_integrator_instance: Optional[CortexImplantsIntegrator] = None


def get_implants_integrator(repo_path: Optional[Path] = None) -> CortexImplantsIntegrator:
    """
    Get singleton integrator instance.
    
    Args:
        repo_path: Repository path (optional)
        
    Returns:
        CortexImplantsIntegrator instance
    """
    global _integrator_instance
    if _integrator_instance is None or repo_path is not None:
        _integrator_instance = CortexImplantsIntegrator(repo_path)
    return _integrator_instance


def has_cortex_implants(repo_path: Optional[Path] = None) -> bool:
    """
    Quick check if cortex-implants present.
    
    Args:
        repo_path: Repository path (optional)
        
    Returns:
        True if implants found
    """
    integrator = get_implants_integrator(repo_path)
    return integrator.has_implants()
