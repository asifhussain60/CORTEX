# AC_START: AC-PHASE38.0-IMPL-001
# Stage 11: FileRelocationEngine - Detect and relocate misplaced files
# Author: CORTEX Architect | Date: 2026-02-09
# Description: Implements file relocation with reference tracking and validation

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class FileCategory(Enum):
    """File categorization for proper placement."""
    ORCHESTRATOR = "orchestrators"
    AGENT = "agents"
    ORCHESTRATOR_SUPPORT = "orchestrators/support"
    LENS = "lens"
    KNOWLEDGE = "knowledge"
    TEST = "tests"
    DOCUMENTATION = "docs"
    DEPLOYMENT = "deployment"
    GOVERNANCE = "governance"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


@dataclass
class MisplacedFile:
    """Represents a misplaced file with relocation info."""
    file_path: Path
    current_category: FileCategory
    expected_category: FileCategory
    references: List[str]
    severity: str  # "critical", "warning", "info"


@dataclass
class RelocationPlan:
    """Plan for relocating files with validation."""
    file_path: Path
    target_path: Path
    references_to_update: List[Tuple[Path, str, str]]  # (file, old_ref, new_ref)
    rollback_snapshot: Optional[Dict] = None


class FileRelocationEngine:
    """
    Detects misplaced files and creates relocation plans with reference tracking.

    Responsibilities:
    - Scan codebase for files in wrong locations
    - Analyze file content to detect category
    - Find all references to misplaced files
    - Generate relocation plans
    - Execute relocations with rollback capability
    """

    def __init__(self, workspace_root: Path):
        """Initialize with workspace root."""
        self.workspace_root = Path(workspace_root)
        self.category_patterns = self._build_category_patterns()

    def _build_category_patterns(self) -> Dict[FileCategory, Tuple[List[str], List[str]]]:
        """Build file matching patterns for each category."""
        return {
            FileCategory.ORCHESTRATOR: (
                ["_orchestrator.py"],
                ["class", "Orchestrator", "MasterOrchestrator"]
            ),
            FileCategory.AGENT: (
                ["_agent.py"],
                ["class", "Agent", "EnforcementAgent"]
            ),
            FileCategory.LENS: (
                ["lens", "LENS"],
                ["lens_analyze", "LENSOrchestrator"]
            ),
            FileCategory.KNOWLEDGE: (
                ["knowledge"],
                ["best_practices", "standards"]
            ),
            FileCategory.TEST: (
                ["test_"],
                ["def test_", "unittest", "pytest"]
            ),
            FileCategory.GOVERNANCE: (
                ["governance"],
                ["CORE", "policy", "enforcement"]
            ),
        }

    def detect_misplaced_files(self) -> List[MisplacedFile]:
        """Scan and identify all misplaced files."""
        misplaced = []

        # Scan Python files
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            expected_category = self._detect_category(py_file)
            current_category = self._get_current_category(py_file)

            if expected_category != current_category:
                references = self._find_references(py_file)
                severity = self._calculate_severity(expected_category, current_category)

                misplaced.append(MisplacedFile(
                    file_path=py_file,
                    current_category=current_category,
                    expected_category=expected_category,
                    references=references,
                    severity=severity
                ))

        return misplaced

    def _detect_category(self, file_path: Path) -> FileCategory:
        """Detect expected category based on file content and name."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        for category, (patterns, keywords) in self.category_patterns.items():
            # Check filename patterns
            for pattern in patterns:
                if pattern in file_path.name:
                    return category

            # Check content keywords
            for keyword in keywords:
                if keyword in content:
                    return category

        return FileCategory.OTHER

    def _get_current_category(self, file_path: Path) -> FileCategory:
        """Determine current category from file location."""
        rel_path = file_path.relative_to(self.workspace_root)

        if "orchestrators" in rel_path.parts:
            if "support" in rel_path.parts:
                return FileCategory.ORCHESTRATOR_SUPPORT
            return FileCategory.ORCHESTRATOR
        elif "agents" in rel_path.parts:
            return FileCategory.AGENT
        elif "lens" in rel_path.parts:
            return FileCategory.LENS
        elif "knowledge" in rel_path.parts:
            return FileCategory.KNOWLEDGE
        elif "tests" in rel_path.parts:
            return FileCategory.TEST
        elif "docs" in rel_path.parts:
            return FileCategory.DOCUMENTATION
        elif "deployment" in rel_path.parts:
            return FileCategory.DEPLOYMENT
        elif "governance" in rel_path.parts:
            return FileCategory.GOVERNANCE
        elif "infrastructure" in rel_path.parts:
            return FileCategory.INFRASTRUCTURE
        else:
            return FileCategory.OTHER

    def _calculate_severity(self, expected: FileCategory, current: FileCategory) -> str:
        """Calculate severity of misplacement."""
        # Core files misplaced are critical
        core_categories = {FileCategory.ORCHESTRATOR, FileCategory.AGENT, FileCategory.GOVERNANCE}

        if expected in core_categories or current in core_categories:
            return "critical"
        elif expected == FileCategory.TEST or current == FileCategory.TEST:
            return "warning"
        else:
            return "info"

    def _find_references(self, file_path: Path) -> List[str]:
        """Find all references to a file in the codebase."""
        references = []
        module_name = file_path.stem
        import_patterns = [
            f"from {module_name} import",
            f"import {module_name}",
            f'"{module_name}"',
            f"'{module_name}'",
        ]

        for py_file in self.workspace_root.rglob("*.py"):
            if py_file == file_path or self._should_skip(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in import_patterns:
                    if pattern in content:
                        references.append(str(py_file))
                        break
            except Exception:
                pass

        return references

    def create_relocation_plan(self, misplaced_file: MisplacedFile) -> RelocationPlan:
        """Create a detailed relocation plan with reference updates."""
        target_path = self._calculate_target_path(
            misplaced_file.file_path,
            misplaced_file.expected_category
        )

        reference_updates = self._calculate_reference_updates(
            misplaced_file.file_path,
            target_path,
            misplaced_file.references
        )

        return RelocationPlan(
            file_path=misplaced_file.file_path,
            target_path=target_path,
            references_to_update=reference_updates
        )

    def _calculate_target_path(self, current_path: Path, category: FileCategory) -> Path:
        """Calculate target path for relocation."""
        category_mapping = {
            FileCategory.ORCHESTRATOR: "cortex/orchestrators",
            FileCategory.ORCHESTRATOR_SUPPORT: "cortex/orchestrators/support",
            FileCategory.AGENT: "cortex/agents",
            FileCategory.LENS: "cortex/lens",
            FileCategory.KNOWLEDGE: "cortex/knowledge",
            FileCategory.TEST: "tests/unit",
            FileCategory.DOCUMENTATION: "docs",
            FileCategory.GOVERNANCE: "cortex/governance",
            FileCategory.INFRASTRUCTURE: "cortex/infrastructure",
        }

        base_dir = self.workspace_root / category_mapping.get(category, "cortex/other")
        return base_dir / current_path.name

    def _calculate_reference_updates(
        self,
        old_path: Path,
        new_path: Path,
        references: List[str]
    ) -> List[Tuple[Path, str, str]]:
        """Calculate import path updates needed."""
        updates = []
        old_rel = old_path.relative_to(self.workspace_root)
        new_rel = new_path.relative_to(self.workspace_root)

        old_import = str(old_rel).replace("/", ".").replace(".py", "")
        new_import = str(new_rel).replace("/", ".").replace(".py", "")

        for ref_file_str in references:
            ref_file = Path(ref_file_str)
            updates.append((ref_file, old_import, new_import))

        return updates

    def execute_relocation(self, plan: RelocationPlan) -> bool:
        """Execute relocation plan with error handling."""
        try:
            # Create snapshot for rollback
            plan.rollback_snapshot = {
                "file_content": plan.file_path.read_bytes(),
                "original_path": str(plan.file_path),
            }

            # Move file
            plan.target_path.parent.mkdir(parents=True, exist_ok=True)
            plan.file_path.rename(plan.target_path)

            # Update references
            for ref_file, old_import, new_import in plan.references_to_update:
                self._update_import_in_file(ref_file, old_import, new_import)

            return True
        except Exception as e:
            self._rollback_relocation(plan)
            raise RuntimeError(f"Relocation failed: {e}")

    def _update_import_in_file(self, file_path: Path, old_import: str, new_import: str):
        """Update import statement in a file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            updated = content.replace(f"from {old_import}", f"from {new_import}")
            updated = updated.replace(f"import {old_import}", f"import {new_import}")
            file_path.write_text(updated, encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to update imports in {file_path}: {e}")

    def _rollback_relocation(self, plan: RelocationPlan):
        """Rollback a failed relocation."""
        if plan.rollback_snapshot:
            original_path = Path(plan.rollback_snapshot["original_path"])
            original_path.parent.mkdir(parents=True, exist_ok=True)
            original_path.write_bytes(plan.rollback_snapshot["file_content"])

    def _should_skip(self, file_path: Path) -> bool:
        """Determine if file should be skipped."""
        skip_patterns = [".venv", "__pycache__", ".git", "node_modules", ".egg-info"]
        return any(pattern in file_path.parts for pattern in skip_patterns)


# AC_COMPLETE: AC-PHASE38.0-IMPL-001 ✅
