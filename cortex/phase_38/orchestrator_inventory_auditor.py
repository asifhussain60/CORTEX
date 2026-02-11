"""
Orchestrator Inventory Auditor - Phase 38.0 Stage 2

Discovers, categorizes, and documents all orchestrator files in the CORTEX workspace.
Cross-references with wiring.yaml and generates comprehensive JSON inventory reports.

AC-PHASE38.0-002: Orchestrator Inventory Audit
"""

# AC_START: AC-PHASE38.0-002
# Description: Orchestrator inventory audit for Phase 38.0 remediation

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class OrchestratorInventoryAuditor:
    """
    Auditor for discovering and documenting orchestrator files.

    Scans cortex/orchestrators directory, categorizes files, cross-references
    with wiring.yaml, and generates comprehensive inventory reports.
    """

    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize the auditor with workspace paths.

        Args:
            workspace_root: Root directory of the CORTEX workspace
        """
        self.workspace_root = workspace_root
        self.orchestrators_dir = workspace_root / "cortex" / "orchestrators"
        self.wiring_file = workspace_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"
        self.reports_dir = workspace_root / "cortex-registry" / "_cortex-master" / "reports"

        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def discover_orchestrator_files(self) -> List[Path]:
        """
        Discover all Python files in the orchestrators directory.

        Returns:
            List of Path objects for all .py files found
        """
        if not self.orchestrators_dir.exists():
            return []

        # Recursively find all Python files
        return list(self.orchestrators_dir.rglob("*.py"))

    def categorize_files(self) -> Dict[str, List[Path]]:
        """
        Categorize files into orchestrators and support files.

        Orchestrators are identified by naming conventions:
        - Contains "orchestrator" in filename
        - Contains "engine" in filename
        - Contains "manager" in filename

        Returns:
            Dictionary with 'orchestrators' and 'support_files' lists
        """
        all_files = self.discover_orchestrator_files()

        orchestrators = []
        support_files = []

        for file_path in all_files:
            filename_lower = file_path.stem.lower()

            # Check if file is an orchestrator
            if any(keyword in filename_lower for keyword in [
                "orchestrator", "engine", "manager", "coordinator", "controller"
            ]):
                orchestrators.append(file_path)
            else:
                support_files.append(file_path)

        return {
            "orchestrators": orchestrators,
            "support_files": support_files
        }

    def load_wiring_yaml(self) -> Dict[str, Any]:
        """
        Load and parse the wiring.yaml file.

        Returns:
            Dictionary containing wiring configuration
        """
        if not self.wiring_file.exists():
            return {}

        with open(self.wiring_file, 'r') as f:
            return yaml.safe_load(f) or {}

    def cross_reference_wiring(self) -> Dict[str, List[str]]:
        """
        Cross-reference discovered orchestrators with wiring.yaml.

        Returns:
            Dictionary with:
                - in_wiring: Orchestrators found in both filesystem and wiring
                - not_in_wiring: Orchestrators in filesystem but not wiring
                - wiring_not_found: Orchestrators in wiring but not filesystem
        """
        categories = self.categorize_files()
        orchestrator_files = categories["orchestrators"]

        # Extract orchestrator names from file paths
        orchestrator_names = {
            file_path.stem for file_path in orchestrator_files
        }

        # Load wiring data
        wiring_data = self.load_wiring_yaml()

        # Extract orchestrator names from wiring
        wiring_orchestrators = set()
        if "orchestrators" in wiring_data:
            for orch in wiring_data["orchestrators"]:
                if isinstance(orch, dict) and "name" in orch:
                    wiring_orchestrators.add(orch["name"])
                elif isinstance(orch, str):
                    wiring_orchestrators.add(orch)

        # Cross-reference
        in_wiring = sorted(orchestrator_names & wiring_orchestrators)
        not_in_wiring = sorted(orchestrator_names - wiring_orchestrators)
        wiring_not_found = sorted(wiring_orchestrators - orchestrator_names)

        return {
            "in_wiring": in_wiring,
            "not_in_wiring": not_in_wiring,
            "wiring_not_found": wiring_not_found
        }

    def generate_report(self) -> Path:
        """
        Generate comprehensive JSON inventory report.

        Returns:
            Path to the generated report file
        """
        # Discover and categorize files
        categories = self.categorize_files()
        orchestrators = categories["orchestrators"]
        support_files = categories["support_files"]

        # Cross-reference with wiring
        cross_ref = self.cross_reference_wiring()

        # Build report structure
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "workspace_root": str(self.workspace_root),
            "total_files": len(orchestrators) + len(support_files),
            "orchestrators_count": len(orchestrators),
            "support_files_count": len(support_files),
            "orchestrators": [
                {
                    "name": orch.stem,
                    "path": str(orch.relative_to(self.workspace_root)),
                    "category": self._determine_category(orch)
                }
                for orch in sorted(orchestrators, key=lambda p: p.stem)
            ],
            "support_files": [
                {
                    "name": sf.stem,
                    "path": str(sf.relative_to(self.workspace_root))
                }
                for sf in sorted(support_files, key=lambda p: p.stem)
            ],
            "wiring_cross_reference": cross_ref,
            "phase": "Phase 38.0 - Stage 2",
            "validation": {
                "min_orchestrators_expected": 30,
                "min_support_files_expected": 100,
                "orchestrators_meets_minimum": len(orchestrators) >= 30,
                "support_files_meets_minimum": len(support_files) >= 100
            }
        }

        # Save report
        report_filename = f"orchestrator-inventory-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        report_path = self.reports_dir / report_filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report_path

    def _determine_category(self, file_path: Path) -> str:
        """
        Determine the category of an orchestrator based on its path.

        Args:
            file_path: Path to the orchestrator file

        Returns:
            Category string (core, domain, support, etc.)
        """
        parts = file_path.parts

        # Find orchestrators directory index
        try:
            orch_index = parts.index("orchestrators")
            if orch_index + 1 < len(parts):
                return parts[orch_index + 1]
        except ValueError:
            pass

        return "unknown"


# AC_COMPLETE: AC-PHASE38.0-002 ✅ Orchestrator inventory auditor implemented
