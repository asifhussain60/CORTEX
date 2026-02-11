"""
Ecosystem Scanner - File Pattern Detection and Tech Stack Analysis.

Scans repository structures to detect languages, frameworks, versions,
and development tools based on file patterns and content analysis.

Phase 34B, Week 1, Increment 2:
- File pattern matching for language detection
- Framework identification from config files and imports
- Version detection from package managers
- Development tool detection

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B specification
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from cortex.orchestrators.intelligence.types import TechStack

logger = logging.getLogger(__name__)


@dataclass
class DetectedTech:
    """Represents a detected technology with confidence score."""

    language: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)  # Files that led to detection

    def __post_init__(self):
        """Validate confidence score."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass
class ScanResult:
    """Result of repository ecosystem scan."""

    success: bool
    tech_stack: Optional[TechStack] = None
    primary_language: Optional[str] = None
    confidence: float = 0.0
    error: Optional[str] = None
    all_languages: List[DetectedTech] = field(default_factory=list)
    scan_duration_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "tech_stack": {
                "language": self.tech_stack.language,
                "frameworks": self.tech_stack.frameworks,
                "version": self.tech_stack.version,
                "tools": self.tech_stack.tools,
            } if self.tech_stack else None,
            "primary_language": self.primary_language,
            "confidence": self.confidence,
            "error": self.error,
            "all_languages": [
                {"language": t.language, "confidence": t.confidence}
                for t in self.all_languages
            ],
            "scan_duration_ms": self.scan_duration_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ScanResult":
        """Reconstruct from dictionary."""
        tech_stack_data = data.get("tech_stack")
        tech_stack = TechStack(
            language=tech_stack_data["language"],
            frameworks=tech_stack_data.get("frameworks", []),
            version=tech_stack_data.get("version"),
        ) if tech_stack_data else None

        return cls(
            success=data["success"],
            tech_stack=tech_stack,
            primary_language=data.get("primary_language"),
            confidence=data.get("confidence", 0.0),
            error=data.get("error"),
            all_languages=[],  # Simplified reconstruction
            scan_duration_ms=data.get("scan_duration_ms", 0.0),
        )


class EcosystemScanner:
    """
    Scans repository file structures to detect tech stacks.

    Detection strategy:
    1. File extensions → primary language
    2. Config files → frameworks
    3. Package managers → versions
    4. Tool configs → dev tools

    Example:
        >>> scanner = EcosystemScanner()
        >>> result = scanner.scan_repository("/path/to/repo")
        >>> if result.success:
        ...     print(f"Detected: {result.primary_language}")
        ...     print(f"Frameworks: {result.tech_stack.frameworks}")
    """

    # Language detection patterns (extension → language mapping)
    DEFAULT_PATTERNS = {
        "python": {
            "extensions": [".py", ".pyw", ".pyi"],
            "indicators": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "confidence_boost": 0.2,  # Boost if indicators present
        },
        "javascript": {
            "extensions": [".js", ".mjs", ".cjs"],
            "indicators": ["package.json", "yarn.lock", "npm-shrinkwrap.json"],
            "confidence_boost": 0.2,
        },
        "typescript": {
            "extensions": [".ts", ".tsx", ".d.ts"],
            "indicators": ["tsconfig.json", "package.json"],
            "confidence_boost": 0.25,
        },
        "java": {
            "extensions": [".java"],
            "indicators": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "confidence_boost": 0.2,
        },
        "go": {
            "extensions": [".go"],
            "indicators": ["go.mod", "go.sum"],
            "confidence_boost": 0.3,
        },
        "rust": {
            "extensions": [".rs"],
            "indicators": ["Cargo.toml", "Cargo.lock"],
            "confidence_boost": 0.3,
        },
    }

    # Framework detection patterns (language → framework indicators)
    FRAMEWORK_PATTERNS = {
        "python": {
            "django": ["manage.py", "settings.py", "wsgi.py", "asgi.py"],
            "flask": ["app.py", "application.py"],  # Also check requirements.txt
            "fastapi": [],  # Requires content inspection
            "celery": [],  # Requires content inspection
            "pytest": ["pytest.ini", "conftest.py"],
        },
        "javascript": {
            "react": [".jsx", ".tsx"],  # Also check package.json
            "vue": [".vue"],
            "angular": ["angular.json"],
            "express": [],  # Requires package.json
            "next": ["next.config.js"],
        },
        "typescript": {
            "react": [".tsx"],
            "angular": ["angular.json", "tsconfig.json"],
            "nest": ["nest-cli.json"],
        },
    }

    # Tool detection patterns
    TOOL_PATTERNS = {
        "python": {
            "pytest": ["pytest.ini", "pyproject.toml"],
            "black": ["pyproject.toml", ".black"],
            "flake8": [".flake8", "setup.cfg"],
            "mypy": ["mypy.ini", ".mypy.ini"],
            "pylint": [".pylintrc", "pylintrc"],
        },
        "javascript": {
            "eslint": [".eslintrc", ".eslintrc.json", ".eslintrc.js"],
            "prettier": [".prettierrc", "prettier.config.js"],
            "jest": ["jest.config.js", "jest.config.ts"],
            "webpack": ["webpack.config.js"],
        },
        "common": {
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
            "git": [".gitignore", ".gitattributes"],
        },
    }

    def __init__(
        self,
        file_patterns: Optional[Dict[str, Any]] = None,
        framework_patterns: Optional[Dict[str, Dict[str, List[str]]]] = None,
    ):
        """
        Initialize EcosystemScanner.

        Args:
            file_patterns: Custom language detection patterns (overrides defaults)
            framework_patterns: Custom framework detection patterns
        """
        self.patterns = file_patterns or self.DEFAULT_PATTERNS
        self.framework_detectors = framework_patterns or self.FRAMEWORK_PATTERNS
        logger.debug(f"EcosystemScanner initialized with {len(self.patterns)} language patterns")

    def detect_language(self, files: List[str]) -> Optional[DetectedTech]:
        """
        Detect primary language from file list.

        Args:
            files: List of file paths (relative or absolute)

        Returns:
            DetectedTech with highest confidence, or None if no language detected
        """
        all_languages = self.detect_all_languages(files)
        return all_languages[0] if all_languages else None

    def detect_all_languages(self, files: List[str]) -> List[DetectedTech]:
        """
        Detect all languages present in files.

        Args:
            files: List of file paths

        Returns:
            List of DetectedTech sorted by confidence (highest first)
        """
        language_counts: Dict[str, Tuple[int, List[str]]] = {}  # lang -> (count, evidence)
        total_files = len(files)

        if total_files == 0:
            return []

        # Count files per language
        for file_path in files:
            file_name = Path(file_path).name
            extension = Path(file_path).suffix

            for lang, config in self.patterns.items():
                # Check extension match
                if extension in config["extensions"]:
                    if lang not in language_counts:
                        language_counts[lang] = (0, [])
                    count, evidence = language_counts[lang]
                    language_counts[lang] = (count + 1, evidence + [file_path])

                # Check indicator files
                if file_name in config["indicators"]:
                    if lang not in language_counts:
                        language_counts[lang] = (0, [])
                    count, evidence = language_counts[lang]
                    # Indicators boost confidence
                    boost = int(total_files * config["confidence_boost"])
                    language_counts[lang] = (count + boost, evidence + [file_path])

        # Convert to DetectedTech with confidence scores
        detected = []
        for lang, (count, evidence) in language_counts.items():
            confidence = min(1.0, count / max(1, total_files))
            detected.append(DetectedTech(
                language=lang,
                confidence=confidence,
                evidence=evidence[:5],  # Limit evidence list
            ))

        # Sort by confidence descending
        detected.sort(key=lambda x: x.confidence, reverse=True)
        return detected

    def detect_frameworks(
        self,
        language: str,
        files: List[str],
        content: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        Detect frameworks for a specific language.

        Args:
            language: Primary language
            files: List of file paths
            content: Optional file path -> content mapping for content inspection

        Returns:
            List of detected framework names
        """
        frameworks = []
        content = content or {}
        file_names = [Path(f).name for f in files]

        # Get framework patterns for this language
        lang_frameworks = self.framework_detectors.get(language, {})

        for framework, indicators in lang_frameworks.items():
            # Check file-based indicators
            if any(indicator in file_names for indicator in indicators):
                frameworks.append(framework)
                continue

            # Check extension-based indicators (for React, Vue, etc.)
            if any(indicator.startswith('.') and any(f.endswith(indicator) for f in files)
                   for indicator in indicators):
                frameworks.append(framework)
                continue

            # Content-based detection
            if self._detect_framework_in_content(framework, content):
                frameworks.append(framework)

        return frameworks

    def _detect_framework_in_content(
        self,
        framework: str,
        content: Dict[str, str],
    ) -> bool:
        """
        Detect framework from file content.

        Args:
            framework: Framework name to look for
            content: File path -> content mapping

        Returns:
            True if framework detected
        """
        framework_lower = framework.lower()

        # Check requirements.txt for Python frameworks
        if "requirements.txt" in content:
            if framework_lower in content["requirements.txt"].lower():
                return True

        # Check package.json for JS frameworks
        if "package.json" in content:
            try:
                pkg_data = json.loads(content["package.json"])
                deps = pkg_data.get("dependencies", {})
                dev_deps = pkg_data.get("devDependencies", {})
                all_deps = {**deps, **dev_deps}

                if framework_lower in [dep.lower() for dep in all_deps]:
                    return True
            except json.JSONDecodeError:
                logger.warning("Invalid package.json content")

        # Check Python imports
        for file_path, file_content in content.items():
            if file_path.endswith(".py"):
                if re.search(rf"from\s+{framework_lower}\s+import", file_content, re.IGNORECASE):
                    return True
                if re.search(rf"import\s+{framework_lower}", file_content, re.IGNORECASE):
                    return True

        return False

    def detect_version(
        self,
        language: str,
        files: List[str],
        content: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """
        Detect language/runtime version.

        Args:
            language: Language to detect version for
            files: List of file paths
            content: Optional file content mapping

        Returns:
            Version string if detected, None otherwise
        """
        content = content or {}

        # Python version detection
        if language == "python":
            # Check pyproject.toml
            if "pyproject.toml" in content:
                match = re.search(r'python\s*=\s*["\'][\^~>=<]*(\d+\.\d+)', content["pyproject.toml"])
                if match:
                    return match.group(1)

            # Check .python-version
            if ".python-version" in content:
                return content[".python-version"].strip()

        # JavaScript/Node version detection
        if language in ["javascript", "typescript"]:
            if "package.json" in content:
                try:
                    pkg_data = json.loads(content["package.json"])
                    engines = pkg_data.get("engines", {})
                    node_version = engines.get("node")
                    if node_version:
                        # Extract version number from range spec
                        match = re.search(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+)', node_version)
                        if match:
                            return match.group(1)
                except json.JSONDecodeError:
                    pass

            # Check .nvmrc
            if ".nvmrc" in content:
                return content[".nvmrc"].strip()

        return None

    def detect_tools(
        self,
        language: str,
        files: List[str],
        content: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        Detect development tools.

        Args:
            language: Primary language
            files: List of file paths
            content: Optional file content mapping

        Returns:
            List of detected tool names
        """
        tools = []
        file_names = [Path(f).name for f in files]
        content = content or {}

        # Language-specific tools
        lang_tools = self.TOOL_PATTERNS.get(language, {})
        for tool, indicators in lang_tools.items():
            if any(indicator in file_names for indicator in indicators):
                tools.append(tool)
            elif self._detect_tool_in_content(tool, content):
                tools.append(tool)

        # Common tools (Docker, Git, etc.)
        common_tools = self.TOOL_PATTERNS.get("common", {})
        for tool, indicators in common_tools.items():
            if any(indicator in file_names for indicator in indicators):
                tools.append(tool)

        return tools

    def _detect_tool_in_content(self, tool: str, content: Dict[str, str]) -> bool:
        """Detect tool from content inspection."""
        tool_lower = tool.lower()

        # Check pyproject.toml for Python tools
        if "pyproject.toml" in content:
            if f"[tool.{tool_lower}]" in content["pyproject.toml"].lower():
                return True

        return False

    def scan_repository(self, repo_path: str) -> ScanResult:
        """
        Scan entire repository to detect tech stack.

        Args:
            repo_path: Path to repository root

        Returns:
            ScanResult with detected tech stack
        """
        import time
        start_time = time.time()

        try:
            path = Path(repo_path)

            # Check if path exists
            if not path.exists():
                return ScanResult(
                    success=False,
                    error=f"Path does not exist: {repo_path}",
                )

            # Collect all files (excluding common ignore patterns)
            files = []
            try:
                for pattern in ["**/*.py", "**/*.js", "**/*.ts", "**/*.java", "**/*.go", "**/*.rs"]:
                    for f in path.rglob(pattern):
                        try:
                            rel_path = str(f.relative_to(path))
                            files.append(rel_path)
                        except ValueError:
                            # Handle mock paths that don't support relative_to
                            files.append(str(f))

                # Add config files
                for config_pattern in ["**/requirements.txt", "**/package.json", "**/Cargo.toml", "**/go.mod"]:
                    for f in path.rglob(config_pattern.split("/")[-1]):
                        try:
                            rel_path = str(f.relative_to(path))
                            files.append(rel_path)
                        except ValueError:
                            files.append(str(f))

            except PermissionError as e:
                return ScanResult(
                    success=False,
                    error=f"Permission denied: {e}",
                )

            # Detect primary language
            all_languages = self.detect_all_languages(files)
            if not all_languages:
                return ScanResult(
                    success=True,
                    tech_stack=TechStack(language="unknown"),
                    primary_language="unknown",
                    confidence=0.0,
                    all_languages=[],
                    scan_duration_ms=(time.time() - start_time) * 1000,
                )

            primary = all_languages[0]

            # Detect frameworks (simplified - no content reading in skeleton)
            frameworks = self.detect_frameworks(primary.language, files, {})

            # Detect tools
            tools = self.detect_tools(primary.language, files, {})

            # Detect version (simplified)
            version = self.detect_version(primary.language, files, {})

            # Build tech stack (tools now included in frameworks list)
            # Merge tools into frameworks to maintain functionality
            all_frameworks = list(set(frameworks + tools))

            tech_stack = TechStack(
                language=primary.language,
                frameworks=all_frameworks,
                version=version,
            )

            duration = (time.time() - start_time) * 1000

            return ScanResult(
                success=True,
                tech_stack=tech_stack,
                primary_language=primary.language,
                confidence=primary.confidence,
                all_languages=all_languages,
                scan_duration_ms=duration,
            )

        except Exception as e:
            logger.error(f"Repository scan failed: {e}")
            return ScanResult(
                success=False,
                error=str(e),
                scan_duration_ms=(time.time() - start_time) * 1000,
            )
