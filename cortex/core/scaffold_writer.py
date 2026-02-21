"""
ScaffoldWriter — disk-emission for workflow scaffold_files.

Writes scaffold files produced by each WorkflowEngine step to disk so that
subsequent steps whose ``depends_on`` gate checks for those files can proceed
without stopping the pipeline mid-run.

AC_START: AC-BADMONOLITH-G2-002
Description: ScaffoldWriter implementation — emit scaffold_files to disk
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
           CORE-028 (snake_case), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScaffoldFile:
    """A single file to be emitted to disk by ScaffoldWriter.

    Attributes:
        path:      Absolute (or relative-to-root) destination path.
        content:   File content to write.
        overwrite: When False, skip writing if the file already exists.
                   Defaults to True — new scaffolds always written.
    """

    path: Path
    content: str
    overwrite: bool = True


class ScaffoldWriter:
    """Writes scaffold files produced by workflow steps to disk.

    Used by ``WorkflowEngine.execute_step()`` after each step completes.
    Parses the ``scaffold_files`` key from the step result, creates any
    missing parent directories, and writes each file — enabling the next
    step's ``depends_on`` gate to find the expected artefacts on disk.

    Example::

        writer = ScaffoldWriter(root=Path("_workspaces/sts/sample-apps/BadMonolith"))
        files  = writer.from_step_output(step_result)
        written = writer.emit(files)
        # → [Path(".../ITaskRepository.cs"), Path(".../TaskRepository.cs"), ...]

    Attributes:
        root: Base directory prepended when step output paths are relative.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        """Initialise ScaffoldWriter.

        Args:
            root: Base directory for relative paths in scaffold output.
                  Defaults to the current working directory.
        """
        self.root: Path = root or Path.cwd()

    # ── public API ────────────────────────────────────────────────────────────

    def emit(self, files: List[ScaffoldFile]) -> List[Path]:
        """Write scaffold files to disk.

        Creates parent directories automatically (``mkdir -p`` semantics).
        Respects the ``overwrite`` flag on each ``ScaffoldFile``.

        Args:
            files: List of :class:`ScaffoldFile` descriptors to write.

        Returns:
            List of :class:`Path` objects that were actually written.
            Files skipped due to ``overwrite=False`` are excluded.
        """
        written: List[Path] = []

        for sf in files:
            target = Path(sf.path)

            if not sf.overwrite and target.exists():
                logger.debug("ScaffoldWriter: skipping existing file %s (overwrite=False)", target)
                continue

            # Create parent directories
            target.parent.mkdir(parents=True, exist_ok=True)

            target.write_text(sf.content, encoding="utf-8")
            written.append(target)
            logger.info("ScaffoldWriter: wrote %s (%d chars)", target, len(sf.content))

        return written

    def from_step_output(self, step_output: Dict[str, Any]) -> List[ScaffoldFile]:
        """Parse scaffold files from a workflow step result dictionary.

        Reads the ``scaffold_files`` key produced by ``WorkflowEngine.execute_step()``.
        Each entry must be a dict with at minimum ``path`` and ``content`` keys.
        An optional ``overwrite`` boolean key is respected (defaults to ``True``).

        Args:
            step_output: The result dict returned by a workflow step executor.
                         Expected shape::

                             {
                               "status": "complete",
                               "scaffold_files": [
                                 {"path": "...", "content": "...", "overwrite": true},
                                 ...
                               ],
                               ...
                             }

        Returns:
            List of :class:`ScaffoldFile` instances parsed from the output.
            Returns an empty list when ``scaffold_files`` is absent or ``None``.
        """
        raw: Any = step_output.get("scaffold_files")
        if not raw:
            return []

        result: List[ScaffoldFile] = []
        for entry in raw:
            if not isinstance(entry, dict):
                logger.warning("ScaffoldWriter: skipping non-dict scaffold entry: %r", entry)
                continue

            path_raw = entry.get("path")
            content = entry.get("content", "")

            if not path_raw:
                logger.warning("ScaffoldWriter: scaffold entry missing 'path' key, skipping")
                continue

            path = Path(str(path_raw))
            # Make relative paths absolute under root
            if not path.is_absolute():
                path = self.root / path

            overwrite: bool = bool(entry.get("overwrite", True))

            result.append(ScaffoldFile(path=path, content=content, overwrite=overwrite))

        return result


# AC_COMPLETE: AC-BADMONOLITH-G2-002 ✅ ScaffoldWriter implementation
