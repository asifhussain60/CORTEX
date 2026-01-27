"""Tier1 Injector - PHASE-DEPLOYMENT-004-multi-repo-gov.

Injects project-specific tier1 governance rules.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml


class Tier1Injector:
    """Injects tier1 rules based on project type.
    
    Loads governance templates (finops, auth, ml, etc.) and validates
    compatibility with tier0 immutable rules.
    """
    
    # Built-in templates
    TEMPLATES = {
        "finops": {
            "profile": "finops",
            "description": "Financial operations governance",
            "rules": ["FIN-001", "FIN-002", "FIN-003", "AUDIT-001"],
            "requirements": ["audit_trail", "data_retention", "encryption"],
        },
        "auth": {
            "profile": "auth",
            "description": "Authentication/authorization governance",
            "rules": ["AUTH-001", "AUTH-002", "SEC-001", "SEC-002"],
            "requirements": ["encryption", "access_control", "session_management"],
        },
        "ml": {
            "profile": "ml",
            "description": "Machine learning governance",
            "rules": ["ML-001", "ML-002", "DATA-001", "DATA-002"],
            "requirements": ["model_versioning", "data_lineage", "reproducibility"],
        },
        "devops": {
            "profile": "devops",
            "description": "DevOps/CI-CD governance",
            "rules": ["CICD-001", "CICD-002", "DEPLOY-001", "DEPLOY-002"],
            "requirements": ["pipeline_validation", "deployment_gates", "rollback"],
        },
        "healthcare": {
            "profile": "healthcare",
            "description": "Healthcare compliance governance",
            "rules": ["HIPAA-001", "HIPAA-002", "PHI-001", "PHI-002"],
            "requirements": ["phi_protection", "audit_logging", "access_control"],
        },
        "legal": {
            "profile": "legal",
            "description": "Legal/compliance governance",
            "rules": ["LEGAL-001", "LEGAL-002", "GDPR-001", "PRIVACY-001"],
            "requirements": ["data_privacy", "consent_management", "retention"],
        },
        "general": {
            "profile": "general",
            "description": "General governance",
            "rules": ["GEN-001", "GEN-002"],
            "requirements": ["code_quality", "documentation"],
        },
    }
    
    # Tier0 rules that cannot be overridden
    TIER0_RULES = [
        "CORE-008",  # Test-first
        "CORE-011",  # Type hints
        "CORE-012",  # Docstrings
        "CORE-017",  # Strict enforcement
        "CORE-018",  # Audit logging
        "CORE-026",  # Git checkpoints
    ]
    
    def __init__(self, templates_path: str = "cortex_brain/tier1/templates"):
        """Initialize tier1 injector.
        
        Args:
            templates_path: Path to tier1 templates.
        """
        self.templates_path = templates_path
    
    def inject_tier1(
        self,
        project_path: str,
        project_type: str,
    ) -> Dict[str, Any]:
        """Inject tier1 rules for a project.
        
        Args:
            project_path: Path to target project.
            project_type: Project type (finops, auth, ml, etc.).
            
        Returns:
            Injection result with applied profile.
        """
        template = self._load_template(project_type)
        
        if not template:
            template = self.TEMPLATES.get("general", {})
        
        # Validate tier0 compatibility
        validation = self.validate_tier0_compatibility(template)
        
        if not validation.get("compatible", True):
            return {
                "success": False,
                "error": "Tier1 rules conflict with tier0",
                "conflicts": validation.get("conflicts", []),
            }
        
        # Write tier1 rules to project
        self._write_tier1_rules(project_path, template)
        
        return {
            "success": True,
            "profile": template.get("profile", project_type),
            "rules": template.get("rules", []),
            "project_path": project_path,
        }
    
    def _load_template(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Load template by profile name.
        
        Args:
            profile_name: Profile name (finops, auth, etc.).
            
        Returns:
            Template dictionary or None.
        """
        # First check built-in templates
        if profile_name in self.TEMPLATES:
            return self.TEMPLATES[profile_name].copy()
        
        # Then check file-based templates
        template_file = Path(self.templates_path) / f"{profile_name}-rules.yaml"
        
        if template_file.exists():
            try:
                with open(template_file) as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        
        return None
    
    def get_template(self, profile_name: str) -> Dict[str, Any]:
        """Get template by profile name.
        
        Args:
            profile_name: Profile name.
            
        Returns:
            Template dictionary.
        """
        return self._load_template(profile_name) or {}
    
    def validate_tier0_compatibility(
        self,
        tier1_rules: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate tier1 rules don't conflict with tier0.
        
        Args:
            tier1_rules: Tier1 rule definitions.
            
        Returns:
            Validation result with compatibility status.
        """
        conflicts = []
        rules = tier1_rules.get("rules", [])
        
        for rule in rules:
            # Check if trying to override a tier0 rule
            for tier0_rule in self.TIER0_RULES:
                if tier0_rule in rule:
                    conflicts.append({
                        "rule": rule,
                        "tier0_rule": tier0_rule,
                        "message": f"Cannot override tier0 rule {tier0_rule}",
                    })
        
        return {
            "compatible": len(conflicts) == 0,
            "conflicts": conflicts,
            "tier0_rules": self.TIER0_RULES,
        }
    
    def detect_conflicts(self, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicting rules within tier1.
        
        Args:
            rules: Rule definitions.
            
        Returns:
            List of detected conflicts.
        """
        conflicts = []
        rule_list = rules.get("rules", [])
        
        # Simple conflict detection: same rule ID with different suffixes
        rule_bases = {}
        for rule in rule_list:
            # Extract base (e.g., "RULE-001" from "RULE-001-allow")
            parts = rule.rsplit("-", 1)
            if len(parts) == 2 and parts[1] in ["allow", "deny", "warn", "block"]:
                base = parts[0]
                action = parts[1]
                
                if base in rule_bases:
                    if rule_bases[base] != action:
                        conflicts.append({
                            "rule1": f"{base}-{rule_bases[base]}",
                            "rule2": rule,
                            "message": f"Conflicting actions for {base}",
                        })
                else:
                    rule_bases[base] = action
        
        return conflicts
    
    def _write_tier1_rules(
        self,
        project_path: str,
        template: Dict[str, Any],
    ) -> bool:
        """Write tier1 rules to project.
        
        Args:
            project_path: Target project path.
            template: Template to write.
            
        Returns:
            True if successful.
        """
        tier1_path = Path(project_path) / "cortex_brain" / "tier1"
        
        try:
            tier1_path.mkdir(parents=True, exist_ok=True)
            
            profile_name = template.get("profile", "general")
            rules_file = tier1_path / f"{profile_name}-rules.yaml"
            
            with open(rules_file, "w") as f:
                yaml.dump(template, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List available tier1 templates.
        
        Returns:
            List of template summaries.
        """
        return [
            {
                "profile": name,
                "description": template.get("description", ""),
                "rule_count": len(template.get("rules", [])),
            }
            for name, template in self.TEMPLATES.items()
        ]


__all__ = ["Tier1Injector"]
