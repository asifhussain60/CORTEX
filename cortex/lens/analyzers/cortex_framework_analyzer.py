"""CortexFrameworkAnalyzer — Self-aware CORTEX repo detection LENS analyzer.

Detects whether a target repository is a CORTEX framework instance by scoring
a set of known CORTEX structural signals.  Returns an ``is_cortex_framework``
boolean flag that gates CORTEX-specific workflow assumptions during onboarding.

A repository must match ≥ 2 distinct signals to be classified as CORTEX.
This prevents false positives from repos that happen to have a folder named
``cortex-registry`` or a ``cortex/`` directory.

Signals detected (regex-free — pure Path checks):
  - ``cortex-registry/`` directory at root            → weight 3
  - ``cortex/orchestrators/`` sub-directory           → weight 4
  - ``.cortex-runtime/`` directory at root            → weight 3
  - ``cortex-master.yaml`` file                       → weight 2
  - ``cortex/__init__.py`` present                    → weight 2
  - ``conftest.py`` + ``pytest.ini`` together         → weight 1 (Python project signal)
  - ``Makefile`` with CORTEX targets                  → weight 1

Confidence = (matched_weight / total_possible_weight), clamped to [0.0, 1.0].

Phase: 131 (GAP-131-02 — Intelligence Layer Backport)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ─── Signal definitions (compiled at class-init per REFACTOR gate) ─────────────
# Each entry: (label, weight, detection_type)
# detection_type: "dir" | "file" | "file+dir" | "file_content"
_SIGNAL_SPECS: List[Tuple[str, int, str]] = [
    ("cortex-registry/",        3, "dir"),
    ("cortex/orchestrators/",   4, "nested_dir"),   # cortex/ + orchestrators/ sub
    (".cortex-runtime/",        3, "dir"),
    ("cortex-master.yaml",      2, "file"),
    ("cortex/__init__.py",      2, "nested_file"),  # cortex/ dir + __init__.py
    ("pytest.ini+conftest.py",  1, "multi_file"),   # both present
    ("Makefile:CORTEX",         1, "file_content"), # Makefile with CORTEX keyword
]

_TOTAL_WEIGHT: int = sum(s[1] for s in _SIGNAL_SPECS)
_MIN_SIGNALS_FOR_POSITIVE: int = 2  # must match at least 2 distinct signals


class CortexFrameworkAnalyzer:
    """LENS analyzer — detects whether a repository is a CORTEX framework instance.

    Checks for canonical CORTEX structural markers without relying on regex
    pattern matching on arbitrary content.  All signal checks are pure
    :class:`pathlib.Path` existence queries except the ``Makefile`` content
    probe (reads first 8 KiB, best-effort).

    Args:
        min_signals: Minimum number of distinct signals required to return
            ``is_cortex_framework=True``.  Defaults to 2.

    Example::

        analyzer = CortexFrameworkAnalyzer()
        result = analyzer.analyze(Path("/path/to/repo"))
        if result["is_cortex_framework"]:
            print("CORTEX repo detected — activating CORTEX-aware checks")

    Phase: 131 — GAP-131-02
    """

    def __init__(self, min_signals: int = _MIN_SIGNALS_FOR_POSITIVE) -> None:
        """Initialise with signal threshold."""
        self._min_signals = min_signals

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze a repository path for CORTEX framework signals.

        Args:
            repo_path: Path to the repository root directory.

        Returns:
            Dict with:
            - ``is_cortex_framework`` (bool): True when ≥ ``min_signals`` matched.
            - ``signals_detected`` (list[str]): Labels of matched signals.
            - ``confidence`` (float): Weighted confidence in [0.0, 1.0].
            - ``score`` (int): Raw weighted signal score.
        """
        if not repo_path.exists():
            return {
                "is_cortex_framework": False,
                "signals_detected": [],
                "confidence": 0.0,
                "score": 0,
            }

        signals_detected: List[str] = []
        total_score: int = 0

        try:
            signals_detected, total_score = self._detect_signals(repo_path)
        except Exception as exc:  # pragma: no cover
            logger.warning("CortexFrameworkAnalyzer.analyze failed for %s: %s", repo_path, exc)

        is_cortex = len(signals_detected) >= self._min_signals
        confidence = min(1.0, total_score / _TOTAL_WEIGHT) if _TOTAL_WEIGHT > 0 else 0.0

        return {
            "is_cortex_framework": is_cortex,
            "signals_detected": signals_detected,
            "confidence": round(confidence, 3),
            "score": total_score,
        }

    def is_cortex_framework(self, repo_path: Path) -> bool:
        """Convenience method — return True if *repo_path* is a CORTEX framework.

        Args:
            repo_path: Path to the repository root directory.

        Returns:
            True when the repository contains ≥ ``min_signals`` CORTEX markers.
        """
        return self.analyze(repo_path)["is_cortex_framework"]

    # ── Private helpers ───────────────────────────────────────────────────────

    def _detect_signals(self, repo_path: Path) -> Tuple[List[str], int]:
        """Run all signal checks and return matched labels + total score."""
        detected: List[str] = []
        score = 0

        # Signal 1: cortex-registry/ directory
        if (repo_path / "cortex-registry").is_dir():
            detected.append("cortex-registry/")
            score += 3

        # Signal 2: cortex/orchestrators/ nested directory
        if (repo_path / "cortex" / "orchestrators").is_dir():
            detected.append("cortex/orchestrators/")
            score += 4

        # Signal 3: .cortex-runtime/ directory
        if (repo_path / ".cortex-runtime").is_dir():
            detected.append(".cortex-runtime/")
            score += 3

        # Signal 4: cortex-master.yaml file
        if (repo_path / "cortex-master.yaml").is_file() or (
            repo_path / "cortex-registry" / "cortex-master.yaml"
        ).is_file():
            detected.append("cortex-master.yaml")
            score += 2

        # Signal 5: cortex/__init__.py
        if (repo_path / "cortex" / "__init__.py").is_file():
            detected.append("cortex/__init__.py")
            score += 2

        # Signal 6: pytest.ini + conftest.py both present
        if (repo_path / "pytest.ini").is_file() and (repo_path / "conftest.py").is_file():
            detected.append("pytest.ini+conftest.py")
            score += 1

        # Signal 7: Makefile containing CORTEX keyword (best-effort, first 8 KiB)
        makefile = repo_path / "Makefile"
        if makefile.is_file():
            try:
                content = makefile.read_bytes()[:8192].decode("utf-8", errors="replace")
                if "cortex" in content.lower() or "CORTEX" in content:
                    detected.append("Makefile:CORTEX")
                    score += 1
            except Exception:
                pass

        return detected, score
