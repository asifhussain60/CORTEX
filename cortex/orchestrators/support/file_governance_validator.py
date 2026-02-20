"""
OptimalFolderStateValidator — Ensures CORTEX folder structure is optimal and compliant.

AC-PHASE38-033: Folder structure compliance validation
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

# Files allowed in root directory
_ROOT_ALLOWED_PY = {
    "setup.py", "conftest.py", "setup.cfg", "pyproject.toml",
}
_ROOT_ALLOWED_MD = {
    "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md",
}


class OptimalFolderStateValidator:
    """Validates that CORTEX project files are in their canonical locations."""

    # ── Detection ─────────────────────────────────────────────────────────────

    def find_placement_violations(self, project_root: str) -> List[Dict[str, Any]]:
        """Find all file placement violations in the project."""
        root = Path(project_root)
        violations: List[Dict[str, Any]] = []

        # Check root-level files
        for item in root.iterdir():
            if not item.is_file():
                continue
            name = item.name
            if item.suffix == ".py" and name not in _ROOT_ALLOWED_PY:
                vtype = "py_in_root"
                if name.startswith("test_") or name.endswith("_test.py"):
                    vtype = "test_in_root"
                violations.append({
                    "file": str(item),
                    "violation_type": vtype,
                    "suggested_location": str(root / "tests" / "unit" / name)
                    if "test" in name
                    else str(root / "cortex" / name),
                    "remediation": f"Move {name} to correct location",
                })
            elif item.suffix == ".md" and name not in _ROOT_ALLOWED_MD:
                violations.append({
                    "file": str(item),
                    "violation_type": "md_in_root",
                    "suggested_location": str(root / "docs" / name),
                    "remediation": f"Move {name} to docs/",
                })

        # Check for test files inside cortex/
        cortex_dir = root / "cortex"
        if cortex_dir.exists():
            for py_file in cortex_dir.rglob("*.py"):
                name = py_file.name
                if name.startswith("test_") or name.endswith("_test.py"):
                    violations.append({
                        "file": str(py_file),
                        "violation_type": "test_in_source",
                        "suggested_location": str(
                            root / "tests" / "unit" / py_file.relative_to(cortex_dir)
                        ),
                        "remediation": f"Move {name} to tests/",
                    })

        # Check for orchestrators outside cortex/orchestrators/
        orch_dir = cortex_dir / "orchestrators"
        if cortex_dir.exists():
            for py_file in cortex_dir.glob("*.py"):
                try:
                    content = py_file.read_text()
                    if "class " in content and "Orchestrator" in content:
                        violations.append({
                            "file": str(py_file),
                            "violation_type": "orchestrator_in_root_cortex",
                            "suggested_location": str(orch_dir / py_file.name),
                            "remediation": f"Move {py_file.name} to cortex/orchestrators/",
                        })
                except Exception:
                    pass

        # Check for orchestrators in project root
        for py_file in root.glob("*.py"):
            if py_file.name in _ROOT_ALLOWED_PY:
                continue
            try:
                content = py_file.read_text()
                if "class " in content and "Orchestrator" in content:
                    violations.append({
                        "file": str(py_file),
                        "violation_type": "orchestrator_in_root",
                        "suggested_location": str(orch_dir / py_file.name),
                        "remediation": f"Move {py_file.name} to cortex/orchestrators/",
                    })
            except Exception:
                pass

        return violations

    # ── Reporting ─────────────────────────────────────────────────────────────

    def generate_audit_report(self, project_root: str) -> Dict[str, Any]:
        """Generate a comprehensive placement audit report."""
        root = Path(project_root)
        violations = self.find_placement_violations(project_root)
        py_files = list(root.rglob("*.py"))
        md_files = list(root.rglob("*.md"))
        return {
            "summary": f"Found {len(violations)} placement violations",
            "total_violations": len(violations),
            "violations": violations,
            "total_files": len(py_files) + len(md_files),
            "py_files": len(py_files),
            "python_files": len(py_files),
            "md_files": len(md_files),
            "markdown_files": len(md_files),
            "statistics": {
                "py_files": len(py_files),
                "md_files": len(md_files),
            },
        }

    def generate_remediation_plan(
        self, violations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a step-by-step remediation plan for violations."""
        steps = []
        # Sort: source files before test files (dependency ordering)
        source_violations = [v for v in violations if "test" not in v["file"]]
        test_violations = [v for v in violations if "test" in v["file"]]
        for v in source_violations + test_violations:
            src = v["file"]
            dst = v.get("suggested_location", "")
            steps.append({
                "file": src,
                "action": "move",
                "destination": dst,
                "command": f"git mv {src!r} {dst!r}",
                "violation_type": v.get("violation_type", "unknown"),
                "remediation": v.get("remediation", ""),
            })
        return {
            "steps": steps,
            "remediation_steps": steps,
            "total_steps": len(steps),
        }

    # ── Orchestration ─────────────────────────────────────────────────────────

    def validate_and_remediate(
        self,
        codebase_root: str,
        auto_fix: bool = False,
    ) -> Dict[str, Any]:
        """Validate project structure and optionally auto-remediate."""
        violations = self.find_placement_violations(codebase_root)
        compliant = len(violations) == 0
        plan = self.generate_remediation_plan(violations) if violations else {"steps": []}
        result: Dict[str, Any] = {
            "compliant": compliant,
            "violations": len(violations),
            "violation_details": violations,
            "plan": plan,
        }
        if auto_fix and violations:
            import shutil
            fixed = 0
            for step in plan["steps"]:
                try:
                    src = Path(step["file"])
                    dst = Path(step["destination"])
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    fixed += 1
                except Exception:
                    pass
            result["auto_fixed"] = fixed
        return result
