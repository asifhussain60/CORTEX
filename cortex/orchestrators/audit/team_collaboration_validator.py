"""TeamCollaborationValidator - AUDIT Mode P1.5 Team Collaboration Check (Stage 6)."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

COMPANY_DOMAINS_DIR = "company/domains"

@dataclass
class CollaborationMetrics:
    has_templates: bool = False
    has_onboarding: bool = False
    has_guidelines: bool = False
    domain_count: int = 0
    readiness_score: float = 0.0

class TeamCollaborationValidator:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.domains_dir = self.repo_root / COMPANY_DOMAINS_DIR

    def validate_all(self) -> Dict[str, Any]:
        domains_exist = self.domains_dir.exists()
        has_templates = (self.domains_dir / "templates").exists() if domains_exist else False
        has_onboarding = (self.domains_dir / "ONBOARDING.md").exists() if domains_exist else False

        issues = []
        if not domains_exist:
            issues.append("P1.5-015: company/domains/ directory missing")
        if not has_templates:
            issues.append("P1.5-015: company/domains/templates/ missing")
        if not has_onboarding:
            issues.append("P1.5-015: ONBOARDING.md missing")

        readiness_score = sum([domains_exist, has_templates, has_onboarding]) / 3.0 * 100

        return {
            "ready": len(issues) == 0,
            "issues": issues,
            "details": {
                "metrics": CollaborationMetrics(
                    has_templates=has_templates,
                    has_onboarding=has_onboarding,
                    has_guidelines=domains_exist,
                    readiness_score=readiness_score
                )
            }
        }

# AC_COMPLETE: AC-PHASE39-015 GREEN ✅
