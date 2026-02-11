"""CORTEX Debug Cleanup - removes debug markers from files."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)
CORTEX_MARKER = "CORTEX_DEBUG"


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    file_path: Path
    original_line_count: int
    cleaned_line_count: int
    markers_removed: int
    success: bool = True
    error: Optional[str] = None


class DebugCleanup:
    """Safe cleanup tool for removing CORTEX debug markers."""

    def __init__(self, session_id: str, repo_path: Path, output_dir: Path) -> None:
        self.session_id = session_id
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir)
        self.backup_dir = self.output_dir / "backups"

    def cleanup(self, injected_files: List[str], verify: bool = True) -> Dict[str, Any]:
        """Remove all CORTEX debug markers from injected files."""
        results: Dict[str, Any] = {
            "session_id": self.session_id,
            "cleanup_time": datetime.now().isoformat(),
            "cleaned_files": [],
            "total_markers_removed": 0,
            "files_processed": 0,
            "files_failed": 0,
            "verified": False,
            "remaining_markers": [],
            "errors": [],
        }

        for rel_path in injected_files:
            file_path = self.repo_path / rel_path
            if not file_path.exists():
                results["errors"].append(f"File not found: {rel_path}")
                results["files_failed"] += 1
                continue
            try:
                cleanup_result = self._cleanup_file(file_path)
                if cleanup_result.success:
                    results["cleaned_files"].append(str(rel_path))
                    results["total_markers_removed"] += cleanup_result.markers_removed
                    results["files_processed"] += 1
                else:
                    results["errors"].append(cleanup_result.error or "Unknown")
                    results["files_failed"] += 1
            except Exception as e:
                results["errors"].append(f"Failed: {rel_path}: {e}")
                results["files_failed"] += 1

        if verify:
            verification = self._verify_cleanup()
            results["verified"] = verification["clean"]
            results["remaining_markers"] = verification["remaining"]
        self._save_cleanup_report(results)
        return results

    def _cleanup_file(self, file_path: Path) -> CleanupResult:
        """Clean a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_lines = content.split('\n')
            cleaned_lines = []
            markers_removed = 0

            for line in original_lines:
                if CORTEX_MARKER in line:
                    stripped = line.strip()
                    if stripped.startswith(('print(', 'console.log(', '#', '//', 'logger.')):
                        markers_removed += 1
                        continue
                cleaned_lines.append(line)

            file_path.write_text('\n'.join(cleaned_lines), encoding='utf-8')
            return CleanupResult(
                file_path=file_path,
                original_line_count=len(original_lines),
                cleaned_line_count=len(cleaned_lines),
                markers_removed=markers_removed,
                success=True,
            )
        except Exception as e:
            return CleanupResult(
                file_path=file_path, original_line_count=0,
                cleaned_line_count=0, markers_removed=0,
                success=False, error=str(e),
            )

    def _verify_cleanup(self) -> Dict[str, Any]:
        """Verify no markers remain."""
        remaining: List[Dict[str, Any]] = []
        for pattern in ["**/*.py", "**/*.js", "**/*.ts"]:
            for fp in self.repo_path.glob(pattern):
                rel = str(fp.relative_to(self.repo_path))
                if any(rel.startswith(p) for p in ["node_modules/", ".git/"]):
                    continue
                try:
                    content = fp.read_text(encoding='utf-8')
                    if CORTEX_MARKER in content:
                        for i, line in enumerate(content.split('\n'), 1):
                            if CORTEX_MARKER in line:
                                remaining.append({"file": rel, "line": i})
                except Exception:
                    pass
        return {"clean": len(remaining) == 0, "remaining": remaining}

    def _save_cleanup_report(self, results: Dict[str, Any]) -> None:
        """Save cleanup report."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "cleanup-report.json", 'w') as f:
            json.dump(results, f, indent=2)


def verify_no_markers(repo_path: Path) -> Dict[str, Any]:
    """Verify no CORTEX markers exist."""
    c = DebugCleanup("verify", repo_path, repo_path / ".cortex-debug")
    return c._verify_cleanup()
