"""
RelocationPlanner — Generate relocation plans with impact analysis.

AC-PHASE44-S2: Classify files and generate ordered relocation plans.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


# Rules: which destination should files go to
_CLASSIFICATION_RULES = [
    ("test_", "tests/unit/"),
    ("_test.py", "tests/unit/"),
    ("conftest", "tests/"),
    ("generate_", "scripts/generators/"),
    ("run_", "scripts/utilities/"),
    ("utility", "scripts/utilities/"),
    ("migrate_", "scripts/migrations/"),
    (".yaml", "cortex-registry/"),
]


class RelocationPlanner:
    """Plans file relocations according to CORTEX structure rules."""

    def classify_files(
        self, inventory: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Classify files and produce relocation classifications."""
        classifications = []
        for category, files in inventory.items():
            for filename in files:
                dest = self._classify_single(filename)
                classifications.append({
                    "file": filename,
                    "category": category,
                    "destination": dest,
                    "action": "move",
                })
        return {
            "status": "success",
            "classifications": classifications,
            "total": len(classifications),
        }

    def _classify_single(self, filename: str) -> str:
        """Classify single."""
        for pattern, destination in _CLASSIFICATION_RULES:
            if pattern in filename:
                return destination
        if filename.endswith(".py"):
            return "scripts/utilities/"
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            return "cortex-registry/"
        return "misc/"

    def analyze_import_impact(
        self,
        relocations: Any,
        codebase_root: Any = ".",
    ) -> Dict[str, Any]:
        """Analyse which imports will be broken by each relocation."""
        if isinstance(relocations, dict):
            source = relocations.get("source") or relocations.get("file", "")
            module_name = Path(source).stem
            affected_count = 0
            affected_paths: List[str] = []
            if isinstance(codebase_root, list):
                candidates = [Path(path) for path in codebase_root]
            else:
                root = Path(codebase_root)
                candidates = list(root.rglob("*.py")) if root.is_dir() else [root]

            for py_file in candidates:
                try:
                    if module_name and module_name in py_file.read_text():
                        affected_count += 1
                        affected_paths.append(str(py_file))
                except Exception:
                    continue

            return {
                "status": "success",
                "source": source,
                "destination": relocations.get("destination", ""),
                "affected_files": affected_count,
                "affected_paths": affected_paths,
            }

        impact: List[Dict[str, Any]] = []
        for relocation in relocations:
            src = relocation.get("file") or relocation.get("source", "")
            dst = relocation.get("destination", "")
            # Count files that import the source module
            old_module = Path(src).stem
            affected: List[str] = []
            for py_file in Path(codebase_root).rglob("*.py"):
                try:
                    content = py_file.read_text()
                    if old_module in content:
                        affected.append(str(py_file))
                except Exception:
                    pass
            impact.append({
                "file": src,
                "destination": dst,
                "affected_imports": len(affected),
                "affected_files": affected,
            })
        return {
            "status": "success",
            "impact_analysis": impact,
            "total_affected": sum(i["affected_imports"] for i in impact),
        }

    def generate_plan(
        self,
        inventory: Dict[str, List[str]],
        codebase_root: str = ".",
    ) -> Dict[str, Any]:
        """Generate a full ordered relocation plan."""
        classified = self.classify_files(inventory)
        relocations = classified["classifications"]
        impact = self.analyze_import_impact(relocations, codebase_root)
        return {
            "status": "success",
            "relocations": relocations,
            "impact": impact,
            "order": [r["file"] for r in relocations],
        }

    def analyze_impact(
        self,
        relocations: Any,
        codebase_root: Any = ".",
    ) -> Dict[str, Any]:
        """Alias for analyze_import_impact — same signature."""
        return self.analyze_import_impact(relocations, codebase_root)

    def detect_conflicts(
        self,
        relocations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Detect destination conflicts within a relocation batch."""
        seen: Dict[str, str] = {}
        conflicts: List[Dict[str, Any]] = []
        rename_strategies: List[Dict[str, str]] = []
        for r in relocations:
            dst = r.get("destination", "")
            src = r.get("file") or r.get("source", "")
            full_dst = dst
            if full_dst in seen:
                conflicts.append({
                    "file": src,
                    "destination": dst,
                    "conflict_with": seen[full_dst],
                })
                rename_strategies.append({
                    "source": src,
                    "suggested_destination": str(Path(dst).with_stem(Path(dst).stem + "_" + Path(src).stem)),
                })
            else:
                seen[full_dst] = src
        return {
            "status": "success",
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "rename_strategies": rename_strategies,
        }

    def calculate_risk_scores(
        self,
        relocations: List[Dict[str, Any]],
        codebase_root: str = ".",
    ) -> Dict[str, Any]:
        """Assign risk scores to each relocation based on import impact."""
        risk_scores: Dict[str, float] = {}
        for relocation in relocations:
            source = relocation.get("source") or relocation.get("file", "")
            affected = relocation.get("affected_files")
            if affected is None:
                impact = self.analyze_import_impact(relocation, codebase_root)
                affected = impact.get("affected_files", 0)
            risk_scores[source] = min(1.0, float(affected) / 50.0)
        return {
            "status": "success",
            "risk_scores": risk_scores,
        }

    def generate_dry_run_preview(
        self,
        inventory: Any,
        codebase_root: str = ".",
    ) -> Dict[str, Any]:
        """Generate a dry-run preview without executing any moves."""
        if isinstance(inventory, list):
            relocations = inventory
        else:
            relocations = self.generate_plan(inventory, codebase_root).get("relocations", [])
        return {
            "status": "dry_run",
            "dry_run": True,
            "before": [],
            "after": [item.get("destination", "") for item in relocations],
            "operations": relocations,
            "would_move": len(relocations),
        }
