"""ArchetypeClassifier — YAML-driven repository archetype detection.

Classifies a repository into one of 13 canonical archetypes by scoring
file-pattern and keyword signals defined in archetype-definitions.yaml.
The highest-scoring archetype wins; ties resolved alphabetically.

Archetypes: DotNetMonolith, MicroservicesMesh, SPAFrontend, LegacyBatchProcessor,
EventDriven, DataPlatform, MobileNative, EmbeddedSystems, SaaSMultiTenant,
Serverless, MLPlatform, CLITooling, GENERIC (fallback).

Phase: 131 (GAP-131-01 — Intelligence Layer Backport)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

import fnmatch
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ─── Canonical YAML path ──────────────────────────────────────────────────────
_DEFINITIONS_YAML = (
    Path(__file__).parent.parent.parent
    / "cortex-registry" / "knowledge" / "archetypes" / "archetype-definitions.yaml"
)

# ─── Singleton ────────────────────────────────────────────────────────────────
_instance: Optional["ArchetypeClassifier"] = None


def get_archetype_classifier() -> "ArchetypeClassifier":
    """Return the module-level ArchetypeClassifier singleton.

    Instantiates on first call; subsequent calls return the cached instance.

    Returns:
        The singleton :class:`ArchetypeClassifier`.
    """
    global _instance
    if _instance is None:
        _instance = ArchetypeClassifier()
    return _instance


# ─────────────────────────────────────────────────────────────────────────────
# ArchetypeClassifier
# ─────────────────────────────────────────────────────────────────────────────

class ArchetypeClassifier:
    """YAML-driven repository archetype classifier.

    Loads signal definitions from *archetype-definitions.yaml* and scores
    a target repository path against each archetype.  The archetype with
    the highest aggregate signal score is returned.

    Fallback behaviour:
    - Non-existent paths → ``GENERIC`` with score ``0``
    - No signals matched → ``GENERIC`` with score ``0``
    - Score tie → alphabetically first archetype id wins

    Args:
        definitions_yaml: Override path to ``archetype-definitions.yaml``.
            Defaults to the canonical registry path.

    Example::

        clf = ArchetypeClassifier()
        result = clf.classify(Path("/path/to/repo"))
        print(result["archetype"])  # e.g. "DotNetMonolith"
        print(result["score"])      # e.g. 11

    Phase: 131 — GAP-131-01
    """

    def __init__(self, definitions_yaml: Optional[Path] = None) -> None:
        """Initialise and load archetype definitions."""
        self._yaml_path = definitions_yaml or _DEFINITIONS_YAML
        self._archetypes: List[Dict[str, Any]] = []
        self._load_definitions()

    # ── Public API ────────────────────────────────────────────────────────────

    def classify(self, repo_path: Path) -> Dict[str, Any]:
        """Classify a repository into the best-matching archetype.

        Walks the top-level (and one level deep) of *repo_path*, collecting
        all file/directory names and file contents (first 4 KiB per file for
        keyword scanning).  Each archetype signal is evaluated; weighted scores
        are accumulated.  The archetype with the highest score wins.

        Args:
            repo_path: Absolute path to the repository root to classify.

        Returns:
            A dict with keys:
            - ``archetype`` (str): The winning archetype id (e.g. ``"DotNetMonolith"``).
            - ``score`` (int): Aggregate signal score of the winning archetype.
            - ``breakdown`` (dict): Per-archetype score breakdown for diagnostics.
        """
        if not repo_path.exists():
            return {"archetype": "GENERIC", "score": 0, "breakdown": {}}

        # Collect filenames and a sample of file content for keyword matching
        filenames: List[str] = []
        content_sample: str = ""

        try:
            filenames, content_sample = self._scan_repo(repo_path)
        except Exception as exc:  # pragma: no cover
            logger.warning("ArchetypeClassifier scan failed for %s: %s", repo_path, exc)
            return {"archetype": "GENERIC", "score": 0, "breakdown": {}}

        scores: Dict[str, int] = {}
        for arch in self._archetypes:
            arch_id = arch.get("id", "GENERIC")
            if arch_id == "GENERIC":
                continue
            score = self._score_archetype(arch, filenames, content_sample, repo_path)
            scores[arch_id] = score

        if not scores or max(scores.values()) == 0:
            return {"archetype": "GENERIC", "score": 0, "breakdown": scores}

        # Winner = highest score; tie-break alphabetically
        winner = max(sorted(scores.keys()), key=lambda k: scores[k])
        return {"archetype": winner, "score": scores[winner], "breakdown": scores}

    def list_archetypes(self) -> List[str]:
        """Return the list of all known archetype ids (excluding GENERIC).

        Returns:
            Sorted list of canonical archetype id strings.
        """
        return sorted(
            a["id"] for a in self._archetypes if a.get("id") != "GENERIC"
        )

    def get_signals(self, archetype_id: str) -> List[Dict[str, Any]]:
        """Return the signal definitions for a named archetype.

        Args:
            archetype_id: The canonical archetype id string.

        Returns:
            List of signal dicts (each has ``pattern`` or ``keyword`` + ``weight``).
            Empty list if the archetype is unknown.
        """
        for arch in self._archetypes:
            if arch.get("id") == archetype_id:
                return list(arch.get("signals", []))
        return []

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_definitions(self) -> None:
        """Load archetype signal definitions from YAML.

        Falls back to an empty list if the YAML is missing or malformed.
        """
        try:
            import yaml  # type: ignore[import]
            content = yaml.safe_load(self._yaml_path.read_text())
            self._archetypes = content.get("archetypes", [])
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "ArchetypeClassifier: failed to load definitions from %s: %s",
                self._yaml_path,
                exc,
            )
            self._archetypes = []

    def _scan_repo(self, repo_path: Path) -> tuple[List[str], str]:
        """Collect filenames and a content sample from the repo root.

        Scans 2 levels deep (root + immediate subdirectories).  Reads up to
        4 KiB from each file for keyword matching.

        Args:
            repo_path: Repository root directory.

        Returns:
            Tuple of (list of relative filename strings, concatenated content sample).
        """
        filenames: List[str] = []
        content_parts: List[str] = []

        for item in repo_path.iterdir():
            filenames.append(item.name)
            if item.is_file():
                self._sample_file(item, content_parts)
            elif item.is_dir():
                # One level deep
                try:
                    for sub in item.iterdir():
                        filenames.append(f"{item.name}/{sub.name}")
                        if sub.is_file():
                            self._sample_file(sub, content_parts)
                except PermissionError:
                    pass

        return filenames, "\n".join(content_parts)

    @staticmethod
    def _sample_file(path: Path, parts: List[str]) -> None:
        """Read up to 4 KiB from a file and append to *parts* (best-effort)."""
        try:
            parts.append(path.read_bytes()[:4096].decode("utf-8", errors="replace"))
        except Exception:
            pass

    def _score_archetype(
        self,
        arch: Dict[str, Any],
        filenames: List[str],
        content_sample: str,
        repo_path: Path,
    ) -> int:
        """Compute the weighted signal score for a single archetype.

        Args:
            arch: Archetype dict from the definitions YAML.
            filenames: List of filenames found in the repo.
            content_sample: Concatenated file content sample for keyword matching.
            repo_path: Repository root (for glob matching).

        Returns:
            Integer weighted score.
        """
        score = 0
        for signal in arch.get("signals", []):
            weight = int(signal.get("weight", 1))
            if "pattern" in signal:
                pattern = signal["pattern"]
                if self._match_pattern(pattern, filenames):
                    score += weight
            elif "keyword" in signal:
                keyword = signal["keyword"].lower()
                if keyword in content_sample.lower():
                    score += weight
        return score

    @staticmethod
    def _match_pattern(pattern: str, filenames: List[str]) -> bool:
        """Return True if any filename in *filenames* matches *pattern*.

        Strips trailing ``/`` from directory patterns before matching.

        Args:
            pattern: Glob pattern (e.g. ``"*.sln"``, ``"k8s/"``).
            filenames: List of relative filename strings from the scan.

        Returns:
            True if at least one filename matches.
        """
        clean = pattern.rstrip("/")
        for name in filenames:
            if fnmatch.fnmatch(name, clean) or fnmatch.fnmatch(
                name.split("/")[-1], clean
            ):
                return True
        return False
