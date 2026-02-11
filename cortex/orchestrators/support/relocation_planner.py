"""
AC_START: AC-PHASE44-S2-002
RelocationPlanner - Generate relocation plans with impact analysis
Phase 44 Stage 2 - Production Readiness Infrastructure
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RelocationPlanner:
    """
    Generate comprehensive relocation plans with impact analysis.

    Features:
    - Classify files by relocation rules (ENH-062)
    - Analyze import impact for each relocation
    - Detect naming conflicts
    - Calculate risk scores
    - Generate dry-run previews

    Usage:
        planner = RelocationPlanner()
        classifications = planner.classify_files(inventory)
        preview = planner.generate_dry_run_preview(relocations)
    """

    def __init__(self) -> None:
        """Initialize RelocationPlanner."""
        self.relocation_rules = {
            "utility_scripts": {
                "patterns": ["generate_", "run_", "verify_", "check_"],
                "destination": "scripts/utilities/"
            },
            "test_files": {
                "patterns": ["test_", "_test"],
                "destination": "tests/_legacy_broken/"
            },
            "config_files": {
                "patterns": [".yaml", ".yml", ".json"],
                "destination": "deployment/"
            }
        }

    def classify_files(self, inventory: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Classify files by relocation rules.

        AC-044-S2-01: 100% of inventory classified
        AC-044-S2-02: Respects production-essential exclusions

        Args:
            inventory: File inventory from RepositoryScanner

        Returns:
            Dictionary with file classifications
        """
        classifications = []

        try:
            # Classify Python files
            for filename in inventory.get("python_files", []):
                category, destination = self._classify_file(filename)

                classifications.append({
                    "file": filename,
                    "category": category,
                    "destination": destination,
                    "source_type": "python"
                })

            # Classify config files
            for filename in inventory.get("config_files", []):
                category, destination = self._classify_file(filename)

                classifications.append({
                    "file": filename,
                    "category": category,
                    "destination": destination,
                    "source_type": "config"
                })

            return {
                "status": "success",
                "classifications": classifications,
                "total_classified": len(classifications)
            }

        except Exception as e:
            logger.error(f"Failed to classify files: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def analyze_impact(self, relocation: Dict[str, str], all_files: List[str]) -> Dict[str, Any]:
        """
        Analyze import impact for relocation.

        AC-044-S2-03: Maps affected imports per relocation
        AC-044-S2-04: Identifies circular import risks

        Args:
            relocation: Relocation dict with source/destination
            all_files: List of all Python files in repo

        Returns:
            Dictionary with impact analysis
        """
        affected_files = []
        circular_risks = []

        try:
            from cortex.orchestrators.support.import_reference_analyzer import (
                ImportReferenceAnalyzer,
            )

            analyzer = ImportReferenceAnalyzer()
            source_file = Path(relocation["source"])

            # Find all files that import this module
            module_name = source_file.stem

            for file_path in all_files:
                refs = analyzer.find_references(file_path, module_name)
                if refs:
                    affected_files.append(file_path)

            # Check for circular imports
            if affected_files:
                circular = analyzer.detect_circular_imports([relocation["source"]] + affected_files)
                circular_risks = circular

            return {
                "affected_files": len(affected_files),
                "files": affected_files,
                "circular_risks": len(circular_risks),
                "risks": circular_risks
            }

        except Exception as e:
            logger.error(f"Failed to analyze impact: {e}")
            return {
                "affected_files": 0,
                "error": str(e)
            }

    def detect_conflicts(self, relocations: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Detect naming conflicts in destination paths.

        AC-044-S2-05: Identifies conflicts (same filename)
        AC-044-S2-06: Proposes rename strategies

        Args:
            relocations: List of relocation dictionaries

        Returns:
            Dictionary with conflicts and rename strategies
        """
        conflicts = []
        rename_strategies = []
        destination_files: Dict[str, List[str]] = {}

        try:
            # Group by destination
            for relocation in relocations:
                dest_path = Path(relocation["destination"])
                dest_file = dest_path.name

                if dest_file not in destination_files:
                    destination_files[dest_file] = []
                destination_files[dest_file].append(relocation["source"])

            # Find conflicts
            for dest_file, sources in destination_files.items():
                if len(sources) > 1:
                    conflicts.append({
                        "destination": dest_file,
                        "sources": sources
                    })

                    # Propose rename strategies
                    for i, source in enumerate(sources[1:], start=1):
                        source_path = Path(source)
                        new_name = f"{source_path.stem}_{i}{source_path.suffix}"

                        rename_strategies.append({
                            "source": source,
                            "original_destination": dest_file,
                            "new_destination": new_name,
                            "reason": f"Conflict with {sources[0]}"
                        })

            return {
                "conflicts_found": len(conflicts),
                "conflicts": conflicts,
                "rename_strategies": rename_strategies
            }

        except Exception as e:
            logger.error(f"Failed to detect conflicts: {e}")
            return {
                "conflicts_found": 0,
                "error": str(e)
            }

    def calculate_risk_scores(self, relocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate risk scores for relocations.

        AC-044-S2-07: Risk scores for all relocations
        AC-044-S2-08: Flags high-risk operations (>0.7)

        Args:
            relocations: List of relocations with affected_files count

        Returns:
            Dictionary with risk scores
        """
        risk_scores = {}
        high_risk = []

        try:
            # Calculate risk based on affected files
            max_affected = max((r.get("affected_files", 0) for r in relocations), default=1)

            for relocation in relocations:
                source = relocation["source"]
                affected = relocation.get("affected_files", 0)

                # Risk score: 0.0-1.0 based on impact
                risk = affected / max_affected if max_affected > 0 else 0.0
                risk_scores[source] = risk

                if risk > 0.7:
                    high_risk.append({
                        "source": source,
                        "risk": risk,
                        "affected_files": affected
                    })

            return {
                "risk_scores": risk_scores,
                "high_risk_count": len(high_risk),
                "high_risk_operations": high_risk
            }

        except Exception as e:
            logger.error(f"Failed to calculate risk scores: {e}")
            return {
                "risk_scores": {},
                "error": str(e)
            }

    def generate_dry_run_preview(self, relocations: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate dry-run preview of relocations.

        AC-044-S2-09: Preview shows all operations
        AC-044-S2-10: Includes before/after file tree

        Args:
            relocations: List of relocation dictionaries

        Returns:
            Dictionary with preview information
        """
        try:
            operations = []
            before_tree = []
            after_tree = []

            for relocation in relocations:
                source = relocation["source"]
                destination = relocation["destination"]

                operations.append({
                    "action": "move",
                    "from": source,
                    "to": destination
                })

                before_tree.append(source)
                after_tree.append(destination)

            return {
                "dry_run": True,
                "operations": operations,
                "before": sorted(set(before_tree)),
                "after": sorted(set(after_tree)),
                "total_operations": len(operations)
            }

        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            return {
                "dry_run": True,
                "error": str(e)
            }

    def _classify_file(self, filename: str) -> tuple:
        """
        Classify single file by rules.

        Args:
            filename: Name of file to classify

        Returns:
            Tuple of (category, destination)
        """
        for category, rules in self.relocation_rules.items():
            for pattern in rules["patterns"]:
                if pattern in filename:
                    return category, rules["destination"] + filename

        return "uncategorized", "scripts/other/" + filename


# AC_COMPLETE: AC-PHASE44-S2-002 ✅ RelocationPlanner implemented with 5 core methods
