"""
ProfileWizard - Quick-start wizard for governance profiles.

Detects project type and suggests appropriate tier1 profile.

AC-ID: AC-DEP-006-02
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import yaml
from datetime import datetime


class ProfileWizard:
    """
    Quick-start wizard for governance profiles.
    
    Detects project type and suggests/applies appropriate tier1 profiles.
    Follows CORE-008 (TDD) and CORE-011 (type hints).
    """
    
    # Detection patterns for project types
    DETECTION_PATTERNS = {
        "finops": {
            "requirements": ["pandas", "numpy", "openpyxl", "xlrd", "finance", "cost"],
            "folders": ["finance", "billing", "cost", "budget"],
            "files": ["*.csv", "financial*.py"]
        },
        "auth": {
            "requirements": ["pyjwt", "authlib", "oauthlib", "passlib", "bcrypt"],
            "folders": ["auth", "authentication", "session", "identity"],
            "files": ["auth*.py", "session*.py", "jwt*.py"]
        },
        "ml": {
            "requirements": ["tensorflow", "torch", "keras", "scikit-learn", "xgboost", "transformers"],
            "folders": ["models", "training", "inference", "ml"],
            "files": ["model*.py", "train*.py"]
        },
        "devops": {
            "requirements": ["ansible", "terraform", "docker", "kubernetes"],
            "folders": [".github/workflows", ".gitlab-ci", "deploy", "infrastructure"],
            "files": ["Dockerfile", "docker-compose.yml", "*.tf"]
        },
        "healthcare": {
            "requirements": ["hl7", "fhir", "pydicom", "medpy"],
            "folders": ["patient", "clinical", "hipaa", "medical"],
            "files": ["patient*.py", "hipaa*.py"]
        },
        "legal": {
            "requirements": ["docx", "pypdf", "pdfplumber"],
            "folders": ["legal", "contracts", "compliance", "documents"],
            "files": ["contract*.py", "legal*.py"]
        }
    }
    
    # Pre-built profile definitions
    PROFILES = {
        "finops-v1.0": {
            "name": "FinOps Profile",
            "version": "1.0",
            "description": "Financial operations governance rules",
            "rule_count": 15,
            "rules": [
                {"id": "FIN-001", "description": "Decimal for currency", "severity": "high"},
                {"id": "FIN-002", "description": "Audit financial changes", "severity": "high"},
                {"id": "FIN-003", "description": "Cost impact in PRs", "severity": "medium"},
                {"id": "FIN-004", "description": "Budget validation", "severity": "high"},
                {"id": "FIN-005", "description": "Rate limit tracking", "severity": "medium"},
                {"id": "FIN-006", "description": "Currency conversion audit", "severity": "medium"},
                {"id": "FIN-007", "description": "Transaction isolation", "severity": "high"},
                {"id": "FIN-008", "description": "Reconciliation checks", "severity": "high"},
                {"id": "FIN-009", "description": "Approval workflow", "severity": "medium"},
                {"id": "FIN-010", "description": "Data retention policy", "severity": "medium"},
                {"id": "FIN-011", "description": "Access control logging", "severity": "high"},
                {"id": "FIN-012", "description": "Error handling standards", "severity": "medium"},
                {"id": "FIN-013", "description": "Backup verification", "severity": "high"},
                {"id": "FIN-014", "description": "Report generation audit", "severity": "medium"},
                {"id": "FIN-015", "description": "Compliance documentation", "severity": "high"}
            ]
        },
        "auth-v1.0": {
            "name": "Authentication Profile",
            "version": "1.0",
            "description": "Authentication and session governance rules",
            "rule_count": 12,
            "rules": [
                {"id": "AUTH-001", "description": "No plaintext passwords", "severity": "critical"},
                {"id": "AUTH-002", "description": "Session timeout required", "severity": "high"},
                {"id": "AUTH-003", "description": "JWT validation mandatory", "severity": "high"},
                {"id": "AUTH-004", "description": "MFA for sensitive ops", "severity": "high"},
                {"id": "AUTH-005", "description": "Secure cookie settings", "severity": "high"},
                {"id": "AUTH-006", "description": "Rate limit auth attempts", "severity": "high"},
                {"id": "AUTH-007", "description": "Audit auth events", "severity": "high"},
                {"id": "AUTH-008", "description": "Token refresh policy", "severity": "medium"},
                {"id": "AUTH-009", "description": "Logout cleanup", "severity": "medium"},
                {"id": "AUTH-010", "description": "Password policy enforcement", "severity": "high"},
                {"id": "AUTH-011", "description": "Account lockout rules", "severity": "high"},
                {"id": "AUTH-012", "description": "Session storage security", "severity": "high"}
            ]
        },
        "ml-v1.0": {
            "name": "Machine Learning Profile",
            "version": "1.0",
            "description": "ML project governance rules",
            "rule_count": 10,
            "rules": [
                {"id": "ML-001", "description": "Model versioning required", "severity": "high"},
                {"id": "ML-002", "description": "Experiment tracking", "severity": "medium"},
                {"id": "ML-003", "description": "Data validation pipeline", "severity": "high"},
                {"id": "ML-004", "description": "Hyperparameter logging", "severity": "medium"},
                {"id": "ML-005", "description": "Model performance baseline", "severity": "high"},
                {"id": "ML-006", "description": "Bias detection required", "severity": "high"},
                {"id": "ML-007", "description": "Reproducibility checks", "severity": "high"},
                {"id": "ML-008", "description": "Feature documentation", "severity": "medium"},
                {"id": "ML-009", "description": "Inference monitoring", "severity": "medium"},
                {"id": "ML-010", "description": "Model card required", "severity": "medium"}
            ]
        },
        "devops-v1.0": {
            "name": "DevOps Profile",
            "version": "1.0",
            "description": "CI/CD and infrastructure governance rules",
            "rule_count": 8,
            "rules": [
                {"id": "DEVOPS-001", "description": "Infrastructure as code", "severity": "high"},
                {"id": "DEVOPS-002", "description": "Immutable deployments", "severity": "high"},
                {"id": "DEVOPS-003", "description": "Rollback capability", "severity": "high"},
                {"id": "DEVOPS-004", "description": "Health checks required", "severity": "high"},
                {"id": "DEVOPS-005", "description": "Logging standards", "severity": "medium"},
                {"id": "DEVOPS-006", "description": "Secret management", "severity": "critical"},
                {"id": "DEVOPS-007", "description": "Automated testing gate", "severity": "high"},
                {"id": "DEVOPS-008", "description": "Change documentation", "severity": "medium"}
            ]
        },
        "healthcare-v1.0": {
            "name": "Healthcare Profile",
            "version": "1.0",
            "description": "HIPAA and healthcare compliance rules",
            "rule_count": 12,
            "rules": [
                {"id": "HIPAA-001", "description": "PHI encryption required", "severity": "critical"},
                {"id": "HIPAA-002", "description": "Access audit logging", "severity": "critical"},
                {"id": "HIPAA-003", "description": "Minimum necessary access", "severity": "high"},
                {"id": "HIPAA-004", "description": "Data retention compliance", "severity": "high"},
                {"id": "HIPAA-005", "description": "Breach notification", "severity": "critical"},
                {"id": "HIPAA-006", "description": "BAA verification", "severity": "high"},
                {"id": "HIPAA-007", "description": "Training documentation", "severity": "medium"},
                {"id": "HIPAA-008", "description": "Risk assessment", "severity": "high"},
                {"id": "HIPAA-009", "description": "Backup encryption", "severity": "high"},
                {"id": "HIPAA-010", "description": "Transmission security", "severity": "high"},
                {"id": "HIPAA-011", "description": "Workstation security", "severity": "medium"},
                {"id": "HIPAA-012", "description": "Incident response plan", "severity": "high"}
            ]
        },
        "legal-v1.0": {
            "name": "Legal Profile",
            "version": "1.0",
            "description": "Legal document management governance rules",
            "rule_count": 10,
            "rules": [
                {"id": "LEGAL-001", "description": "Document versioning", "severity": "high"},
                {"id": "LEGAL-002", "description": "Retention policy compliance", "severity": "high"},
                {"id": "LEGAL-003", "description": "Access control audit", "severity": "high"},
                {"id": "LEGAL-004", "description": "Redaction tracking", "severity": "medium"},
                {"id": "LEGAL-005", "description": "eSignature validation", "severity": "high"},
                {"id": "LEGAL-006", "description": "Conflict checking", "severity": "medium"},
                {"id": "LEGAL-007", "description": "Privilege markers", "severity": "high"},
                {"id": "LEGAL-008", "description": "Matter management", "severity": "medium"},
                {"id": "LEGAL-009", "description": "Chain of custody", "severity": "high"},
                {"id": "LEGAL-010", "description": "Regulatory compliance", "severity": "high"}
            ]
        }
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize ProfileWizard.
        
        Args:
            repo_path: Path to the repository root.
        """
        self.repo_path = Path(repo_path)
    
    def detect_project_type(self) -> str:
        """
        Detect project type based on requirements and structure.
        
        Returns:
            Project type string.
        """
        scores = {ptype: 0 for ptype in self.DETECTION_PATTERNS}
        
        # Check requirements.txt
        requirements_path = self.repo_path / "requirements.txt"
        if requirements_path.exists():
            content = requirements_path.read_text().lower()
            for ptype, patterns in self.DETECTION_PATTERNS.items():
                for req in patterns.get("requirements", []):
                    if req.lower() in content:
                        scores[ptype] += 2
        
        # Check folder structure
        for ptype, patterns in self.DETECTION_PATTERNS.items():
            for folder in patterns.get("folders", []):
                if (self.repo_path / folder).exists():
                    scores[ptype] += 3
        
        # Check file patterns
        for ptype, patterns in self.DETECTION_PATTERNS.items():
            for file_pattern in patterns.get("files", []):
                if list(self.repo_path.glob(file_pattern)):
                    scores[ptype] += 1
        
        # Return highest scoring type
        max_score = max(scores.values())
        if max_score > 0:
            for ptype, score in scores.items():
                if score == max_score:
                    return ptype
        
        return "general"
    
    def suggest_profile(self) -> Dict[str, Any]:
        """
        Suggest appropriate profile based on detection.
        
        Returns:
            Profile suggestion dictionary.
        """
        project_type = self.detect_project_type()
        
        profile_mapping = {
            "finops": "finops-v1.0",
            "auth": "auth-v1.0",
            "ml": "ml-v1.0",
            "devops": "devops-v1.0",
            "healthcare": "healthcare-v1.0",
            "legal": "legal-v1.0",
            "general": "devops-v1.0"  # Default fallback
        }
        
        suggested = profile_mapping.get(project_type, "devops-v1.0")
        profile_info = self.PROFILES.get(suggested, {})
        
        return {
            "profile": suggested,
            "project_type": project_type,
            "confidence": 0.85 if project_type != "general" else 0.5,
            "explanation": f"Detected {project_type} project based on requirements and structure",
            "rule_count": profile_info.get("rule_count", 0),
            "description": profile_info.get("description", "")
        }
    
    def customize_profile(
        self,
        profile: str,
        add_rules: Optional[List[str]] = None,
        remove_rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Customize profile by adding/removing rules.
        
        Args:
            profile: Profile name to customize.
            add_rules: Rules to add.
            remove_rules: Rules to remove.
            
        Returns:
            Customized profile dictionary.
        """
        profile_data = self.PROFILES.get(profile, {})
        rules = [r["id"] for r in profile_data.get("rules", [])]
        
        # Remove specified rules
        if remove_rules:
            rules = [r for r in rules if r not in remove_rules]
        
        # Add new rules
        if add_rules:
            rules.extend(add_rules)
        
        return {
            "base_profile": profile,
            "rules": rules,
            "customized": True,
            "added": add_rules or [],
            "removed": remove_rules or []
        }
    
    def apply_profile(self, profile: str) -> Dict[str, Any]:
        """
        Apply profile to tier1 directory.
        
        Args:
            profile: Profile name to apply.
            
        Returns:
            Result dictionary.
        """
        result = {"success": False, "error": None}
        
        try:
            profile_data = self.PROFILES.get(profile, {})
            
            if not profile_data:
                result["error"] = f"Profile {profile} not found"
                return result
            
            # Create tier1 directory
            tier1_dir = self.repo_path / "cortex_brain" / "tier1"
            tier1_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate YAML content
            content = {
                "profile": profile,
                "version": profile_data.get("version", "1.0"),
                "applied_at": datetime.now().isoformat(),
                "rules": profile_data.get("rules", [])
            }
            
            # Write to file
            output_path = tier1_dir / "domain-rules.yaml"
            output_path.write_text(yaml.dump(content, default_flow_style=False))
            
            result["success"] = True
            result["path"] = str(output_path)
            result["rule_count"] = len(profile_data.get("rules", []))
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def list_available_profiles(self) -> List[Dict[str, Any]]:
        """
        List all available profiles.
        
        Returns:
            List of profile information dictionaries.
        """
        profiles = []
        
        for name, data in self.PROFILES.items():
            profiles.append({
                "name": name,
                "display_name": data.get("name", name),
                "version": data.get("version", "1.0"),
                "description": data.get("description", ""),
                "rule_count": data.get("rule_count", 0)
            })
        
        return profiles
