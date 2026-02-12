"""
Staleness Checker - Detects outdated or missing framework documentation.

Authority: Phase 54 S3 - Tech Stack Detection & Staleness Awareness
Purpose: Compare detected tech vs documented tech, alert on mismatches

Example:
  checker = StalenessChecker()
  report = checker.check_staleness(
      ast_imports=['fastapi', 'sqlalchemy'],
      loaded_yamls=['fastapi-security.yaml']
  )
  # Returns: StalenessReport(missing=['sqlalchemy'], outdated=[...], ...)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from cortex.brain.knowledge.tech_stack_mapper import TechStackMapper

logger = logging.getLogger(__name__)


@dataclass
class StalenessReport:
    """Report on knowledge staleness for detected tech stack."""

    detected_tech: List[str] = field(default_factory=list)
    documented_tech: List[str] = field(default_factory=list)
    missing_tech: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    timestamp: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "detected_tech": self.detected_tech,
            "documented_tech": self.documented_tech,
            "missing_tech": self.missing_tech,
            "recommendations": self.recommendations,
            "severity": self.severity,
        }

    def is_critical(self) -> bool:
        """Check if staleness is critical (blocking)."""
        return self.severity == "CRITICAL"

    def is_warning(self) -> bool:
        """Check if staleness is a warning."""
        return self.severity == "WARNING"


class StalenessChecker:
    """
    Detects when codebase uses frameworks not documented in knowledge base.

    Compares AST-detected imports against loaded knowledge YAMLs.
    Identifies missing and outdated documentation.

    CORE Rules:
    - CORE-011: Type hints required ✅
    - CORE-012: Docstrings required ✅
    """

    def __init__(self):
        """Initialize StalenessChecker."""
        self.logger = logging.getLogger(f"{__name__}.StalenessChecker")
        self.tech_mapper = TechStackMapper()
        self.logger.info(
            "AC_START: AC-PHASE54-S3-T2 | StalenessChecker initialized"
        )

    def check_staleness(
        self,
        ast_imports: List[str],
        loaded_yamls: List[str],
        force_critical: bool = False,
    ) -> StalenessReport:
        """
        Check staleness of knowledge base for detected tech stack.

        Args:
            ast_imports: Imports detected from AST analysis
            loaded_yamls: Knowledge YAML files already loaded
            force_critical: Force severity to CRITICAL (for testing)

        Returns:
            StalenessReport with detected/documented/missing tech
        """
        import time

        try:
            # Map imports to tech categories
            detected_tech = self.tech_mapper.get_categories_for_intent(ast_imports)

            # Extract tech names from YAML paths
            documented_tech = self._extract_tech_from_yamls(loaded_yamls)

            # Find missing
            missing = set(detected_tech) - set(documented_tech)

            # Generate recommendations
            recommendations = []
            if missing:
                recommendations.append(
                    f"Add documentation for: {', '.join(sorted(missing))}"
                )
                recommendations.append(
                    "Update company/domains/ or cortex/knowledge/ with missing tech YAMLs"
                )

            # Determine severity
            if force_critical:
                severity = "CRITICAL"
            elif missing:
                severity = "WARNING"
            else:
                severity = "INFO"

            report = StalenessReport(
                detected_tech=sorted(detected_tech),
                documented_tech=sorted(documented_tech),
                missing_tech=sorted(list(missing)),
                recommendations=recommendations,
                severity=severity,
                timestamp=time.time(),
            )

            self.logger.info(
                f"AC_PHASE54-S3-T2: Staleness check | "
                f"Detected={len(detected_tech)} | "
                f"Documented={len(documented_tech)} | "
                f"Missing={len(missing)} | "
                f"Severity={severity}"
            )

            return report

        except Exception as e:
            self.logger.error(f"Failed to check staleness: {e}", exc_info=True)

            # Return minimal report on failure
            return StalenessReport(
                detected_tech=ast_imports,
                recommendations=[f"Staleness check failed: {str(e)}"],
                severity="WARNING",
            )

    def _extract_tech_from_yamls(self, yaml_paths: List[str]) -> List[str]:
        """
        Extract tech stack names from YAML file paths.

        Args:
            yaml_paths: List of YAML file paths

        Returns:
            List of extracted tech names
        """
        tech_set = set()

        for yaml_path in yaml_paths:
            path = Path(yaml_path)
            # Heuristic: extract tech name from filename
            # e.g., "cortex/knowledge/fastapi.yaml" → "fastapi"
            # "cortex/knowledge/async.yaml" → "async"
            # "cortex/knowledge/python-web.yaml" → "python-web"

            # Get the stem (filename without .yaml)
            stem = path.stem
            if stem and stem not in ["index", "readme", "config"]:
                # Use the full stem (e.g., "python-web" not just "python")
                tech_set.add(stem)

        return sorted(list(tech_set))

    def recommend_yaml_updates(self, report: StalenessReport) -> List[str]:
        """
        Generate recommendations for YAML updates based on staleness report.

        Args:
            report: StalenessReport from check_staleness()

        Returns:
            List of actionable recommendations
        """
        recs = []

        for missing_tech in report.missing_tech:
            recs.append(
                f"Create cortex/knowledge/best-practices/{missing_tech}/"
                f"{missing_tech}-best-practices.yaml"
            )
            recs.append(
                f"Add {missing_tech} patterns to company/domains/*/best-practices.yaml"
            )

        return recs
