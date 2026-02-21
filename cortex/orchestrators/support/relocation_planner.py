"""
RelocationPlanner — Generate relocation plans with impact analysis.

AC-PHASE44-S2: Classify files and generate ordered relocation plans.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


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
        relocations: List[Dict[str, Any]],
        codebase_root: str = ".",
    ) -> Dict[str, Any]:
        """Analyse which imports will be broken by each relocation."""
        impact: List[Dict[str, Any]] = []
        for relocation in relocations:
            src = relocation.get("file", "")
            dst = relocation.get("destination", "")
            # Count files that import the source module
            old_module = src.replace("/", ".").replace(".py", "")
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
        relocations: List[Dict[str, Any]],
        codebase_root: str = ".",
    ) -> Dict[str, Any]:
        """Alias for analyze_import_impact — same signature."""
        return self.analyze_import_impact(relocations, codebase_root)

    def detect_conflicts(
        self,
        relocations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Detect destination conflicts within a relocation batch."""
        seen: Dict[str, str] = {}
        conflicts: List[Dict[str, Any]] = []
        for r in relocations:
            dst = r.get("destination", "")
            src = r.get("file", "")
            key = f"{dst}/{src}"
            full_dst = f"{dst}/{Path(src).name}"
            if full_dst in seen:
                conflicts.append({
                    "file": src,
                    "destination": dst,
                    "conflict_with": seen[full_dst],
                })
            else:
                seen[full_dst] = src
        return conflicts

    def calculate_risk_scores(
        self,
        relocations: List[Dict[str, Any]],
        codebase_root: str = ".",
    ) -> List[Dict[str, Any]]:
        """Assign risk scores to each relocation based on import impact."""
        impact = self.analyze_import_impact(relocations, codebase_root)
        scored = []
        for item in impact.get("impact_analysis", []):
            affected = item.get("affected_imports", 0)
            score = "high" if affected > 5 else ("medium" if affected > 1 else "low")
            scored.append({**item, "risk_score": score, "risk_value": affected})
        return scored

    def generate_dry_run_preview(
        self,
        inventory: Dict[str, List[str]],
        codebase_root: str = ".",
    ) -> Dict[str, Any]:
        """Generate a dry-run preview without executing any moves."""
        plan = self.generate_plan(inventory, codebase_root)
        conflicts = self.detect_conflicts(plan.get("relocations", []))
        risks = self.calculate_risk_scores(plan.get("relocations", []), codebase_root)
        return {
            "status": "dry_run",
            "plan": plan,
            "conflicts": conflicts,
            "risks": risks,
            "would_move": len(plan.get("relocations", [])),
        }