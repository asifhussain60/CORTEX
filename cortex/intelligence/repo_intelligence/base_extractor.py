"""BaseExtractor — Abstract Base Class for all repo intelligence extractors.

Every extractor in the Universal Repo Intelligence Engine must subclass
this ABC and implement the ``extract(repo_path)`` method.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Any, Dict


class BaseExtractor(abc.ABC):
    """Abstract base class for all repo intelligence extractors.

    Subclasses must implement :meth:`extract` which scans the given
    repository path and returns a typed result dictionary.
    """

    #: Short kebab/snake identifier used as the key in OnboardingManifest.
    name: str = "base"

    @abc.abstractmethod
    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """Run extraction against *repo_path*.

        Args:
            repo_path: Absolute path to the repository root.

        Returns:
            A dictionary of extractor-specific findings.  Must never raise —
            return an empty-results dict on any error.
        """
        ...  # pragma: no cover
