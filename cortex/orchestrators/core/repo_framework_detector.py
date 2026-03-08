"""RepoFrameworkDetector — CAPE sub-phase 136-e.

Detects the programming language and test runner for a repository by
inspecting well-known indicator files:
  - ``requirements.txt``  → Python / pytest
  - ``package.json``      → Node (JavaScript / TypeScript) / jest
  - ``*.csproj``          → C# / .NET / dotnet-test
  - fallback              → Unknown

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
AC-ID: AC-136-CAPE-005c
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass


@dataclass
class FrameworkDetectionResult:
    """Result of :class:`RepoFrameworkDetector`.

    Attributes:
        language:    Detected programming language (e.g. ``"Python"``).
        test_runner: Detected test runner (e.g. ``"pytest"``).
        confidence:  Detection confidence in ``[0.0, 1.0]``.
    """

    language: str
    test_runner: str
    confidence: float = 1.0


class RepoFrameworkDetector:
    """Detect language and test runner from well-known repo indicator files.

    Detection priority (first match wins):
    1. ``requirements.txt`` → Python / pytest
    2. ``package.json``     → Node / jest (or vitest if vitest present)
    3. ``*.csproj``         → C# / dotnet-test
    4. fallback             → Unknown

    Usage::

        detector = RepoFrameworkDetector()
        result = detector.detect(repo_root="/path/to/repo")
        # result.language → "Python"
        # result.test_runner → "pytest"
    """

    def detect(self, *, repo_root: str) -> FrameworkDetectionResult:
        """Detect the framework used in the repository.

        Args:
            repo_root: Absolute path to the root of the repository.

        Returns:
            :class:`FrameworkDetectionResult` with language and test runner.
        """
        # 1. Python — requirements.txt
        req_path = os.path.join(repo_root, "requirements.txt")
        if os.path.isfile(req_path):
            runner = self._detect_python_runner(req_path)
            return FrameworkDetectionResult(language="Python", test_runner=runner)

        # 2. Node — package.json
        pkg_path = os.path.join(repo_root, "package.json")
        if os.path.isfile(pkg_path):
            language, runner = self._detect_node(pkg_path)
            return FrameworkDetectionResult(language=language, test_runner=runner)

        # 3. C# — any *.csproj
        csproj_files = glob.glob(os.path.join(repo_root, "*.csproj"))
        if csproj_files:
            return FrameworkDetectionResult(language="C#", test_runner="dotnet-test")

        # 4. Fallback
        return FrameworkDetectionResult(language="Unknown", test_runner="unknown", confidence=0.0)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_python_runner(req_path: str) -> str:
        """Identify test runner from requirements.txt content."""
        try:
            with open(req_path, encoding="utf-8") as fh:
                content = fh.read().lower()
        except OSError:
            return "pytest"

        if "pytest" in content:
            return "pytest"
        if "unittest" in content:
            return "unittest"
        return "pytest"  # default for Python

    @staticmethod
    def _detect_node(pkg_path: str) -> tuple[str, str]:
        """Identify language and test runner from package.json."""
        try:
            with open(pkg_path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return "Node", "jest"

        all_deps: dict = {}
        all_deps.update(data.get("dependencies", {}))
        all_deps.update(data.get("devDependencies", {}))

        # Determine language (TypeScript if @types or typescript present)
        language = "TypeScript" if ("typescript" in all_deps or "@types/node" in all_deps) else "Node"

        # Determine runner
        if "vitest" in all_deps:
            runner = "vitest"
        elif "jest" in all_deps:
            runner = "jest"
        elif "mocha" in all_deps:
            runner = "mocha"
        else:
            runner = "jest"  # default for Node

        return language, runner
