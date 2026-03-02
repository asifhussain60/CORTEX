"""
Tech Stack Analyzer - Automatic Technology Detection.

Authority: Phase 90 Stage 1 - Tech Stack Detection
Purpose: Detect languages, frameworks, libraries from files + AST imports

Detection Methods:
1. File extensions (.py, .cs, .go, .rs, .tsx, etc.)
2. Config files (package.json, pom.xml, Cargo.toml, etc.)
3. AST imports (import flask, using System, etc.)
4. Build tools (requirements.txt, go.mod, Gemfile, etc.)

Supported Stacks:
- Python (Flask, Django, FastAPI)
- .NET (C#, ASP.NET)
- Java (Spring Boot)
- Go
- JavaScript/TypeScript (React, Angular, Vue)
- PHP (Laravel)
- Ruby (Rails)
- Rust

CORE Rules:
- CORE-008: TDD mandatory ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
- CORE-013: No bare except ✅
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
import hashlib

from cortex.lens.models.tech_stack import (
    TechStack,
    TechStackItem,
    TechCategory
)

logger = logging.getLogger(__name__)


class TechStackAnalyzer:
    """
    Analyze repository to detect technology stack.

    Uses multiple detection methods:
    - File extension analysis
    - Configuration file parsing
    - AST import detection
    - Build tool identification

    Examples:
        >>> analyzer = TechStackAnalyzer()
        >>> files = ["app.py", "requirements.txt"]
        >>> imports = ["flask", "sqlalchemy"]
        >>> result = analyzer.analyze(files=files, imports=imports)
        >>> print(result.primary_language)  # "python"
        >>> print(result.frameworks)  # ["flask"]
    """

    # File extension mappings
    EXTENSION_MAP: Dict[str, tuple] = {
        # Python
        ".py": ("python", TechCategory.LANGUAGE, 1.0),
        ".pyi": ("python", TechCategory.LANGUAGE, 0.9),

        # C# / .NET
        ".cs": ("csharp", TechCategory.LANGUAGE, 1.0),
        ".csproj": ("dotnet", TechCategory.FRAMEWORK, 0.9),
        ".sln": ("dotnet", TechCategory.FRAMEWORK, 0.8),

        # Java
        ".java": ("java", TechCategory.LANGUAGE, 1.0),
        ".class": ("java", TechCategory.LANGUAGE, 0.7),

        # Go
        ".go": ("go", TechCategory.LANGUAGE, 1.0),

        # JavaScript/TypeScript
        ".js": ("javascript", TechCategory.LANGUAGE, 1.0),
        ".jsx": ("react", TechCategory.FRAMEWORK, 0.95),
        ".ts": ("typescript", TechCategory.LANGUAGE, 1.0),
        ".tsx": ("react", TechCategory.FRAMEWORK, 0.95),

        # PHP
        ".php": ("php", TechCategory.LANGUAGE, 1.0),

        # Ruby
        ".rb": ("ruby", TechCategory.LANGUAGE, 1.0),

        # Rust
        ".rs": ("rust", TechCategory.LANGUAGE, 1.0),
    }

    # Config file mappings
    CONFIG_FILE_MAP: Dict[str, tuple] = {
        # Python
        "requirements.txt": ("python", TechCategory.BUILD_TOOL, 0.9),
        "setup.py": ("python", TechCategory.BUILD_TOOL, 0.9),
        "pyproject.toml": ("python", TechCategory.BUILD_TOOL, 0.95),
        "Pipfile": ("python", TechCategory.BUILD_TOOL, 0.9),
        "poetry.lock": ("python", TechCategory.BUILD_TOOL, 0.9),

        # Node.js
        "package.json": ("nodejs", TechCategory.RUNTIME, 0.95),
        "package-lock.json": ("nodejs", TechCategory.BUILD_TOOL, 0.8),
        "yarn.lock": ("nodejs", TechCategory.BUILD_TOOL, 0.8),
        "tsconfig.json": ("typescript", TechCategory.LANGUAGE, 0.95),

        # .NET
        "appsettings.json": ("dotnet", TechCategory.FRAMEWORK, 0.7),

        # Java
        "pom.xml": ("maven", TechCategory.BUILD_TOOL, 0.95),
        "build.gradle": ("gradle", TechCategory.BUILD_TOOL, 0.95),
        "application.properties": ("spring-boot", TechCategory.FRAMEWORK, 0.8),

        # Go
        "go.mod": ("go", TechCategory.LANGUAGE, 0.95),
        "go.sum": ("go", TechCategory.BUILD_TOOL, 0.8),

        # PHP
        "composer.json": ("php", TechCategory.BUILD_TOOL, 0.95),
        "artisan": ("laravel", TechCategory.FRAMEWORK, 0.9),

        # Ruby
        "Gemfile": ("ruby", TechCategory.BUILD_TOOL, 0.95),
        "Rakefile": ("ruby", TechCategory.BUILD_TOOL, 0.8),
        "config.ru": ("rack", TechCategory.FRAMEWORK, 0.8),

        # Rust
        "Cargo.toml": ("rust", TechCategory.LANGUAGE, 0.95),
        "Cargo.lock": ("rust", TechCategory.BUILD_TOOL, 0.8),

        # Angular
        "angular.json": ("angular", TechCategory.FRAMEWORK, 0.95),

        # Vue
        "vue.config.js": ("vue", TechCategory.FRAMEWORK, 0.9),
    }

    # Import/package mappings
    IMPORT_MAP: Dict[str, tuple] = {
        # Python frameworks
        "flask": ("flask", TechCategory.FRAMEWORK, 1.0),
        "django": ("django", TechCategory.FRAMEWORK, 1.0),
        "fastapi": ("fastapi", TechCategory.FRAMEWORK, 1.0),

        # Python libraries
        "sqlalchemy": ("sqlalchemy", TechCategory.LIBRARY, 1.0),
        "pydantic": ("pydantic", TechCategory.LIBRARY, 1.0),
        "marshmallow": ("marshmallow", TechCategory.LIBRARY, 0.9),
        "requests": ("requests", TechCategory.LIBRARY, 0.9),
        "numpy": ("numpy", TechCategory.LIBRARY, 1.0),
        "pandas": ("pandas", TechCategory.LIBRARY, 1.0),

        # Python testing
        "pytest": ("pytest", TechCategory.TESTING, 1.0),
        "unittest": ("unittest", TechCategory.TESTING, 0.9),

        # JavaScript/TypeScript
        "react": ("react", TechCategory.FRAMEWORK, 1.0),
        "vue": ("vue", TechCategory.FRAMEWORK, 1.0),
        "angular": ("angular", TechCategory.FRAMEWORK, 1.0),
        "express": ("express", TechCategory.FRAMEWORK, 1.0),
        "next": ("nextjs", TechCategory.FRAMEWORK, 1.0),

        # React hooks
        "useState": ("react", TechCategory.FRAMEWORK, 0.95),
        "useEffect": ("react", TechCategory.FRAMEWORK, 0.95),
    }

    def __init__(self) -> None:
        """Initialize TechStackAnalyzer."""
        self.logger = logging.getLogger(f"{__name__}.TechStackAnalyzer")
        self._cache: Dict[str, TechStack] = {}

    def detect_from_files(self, files: List[str]) -> TechStack:
        """
        Detect tech stack from file paths.

        Analyzes file extensions and configuration files to identify
        languages, frameworks, and build tools.

        Args:
            files: List of file paths (relative or absolute)

        Returns:
            TechStack with detected technologies

        Examples:
            >>> analyzer = TechStackAnalyzer()
            >>> result = analyzer.detect_from_files(["app.py", "requirements.txt"])
            >>> assert "python" in result.languages
        """
        tech_stack = TechStack()

        if not files:
            return tech_stack

        detected_items: Dict[str, TechStackItem] = {}

        for file_path in files:
            file_name = Path(file_path).name
            file_ext = Path(file_path).suffix.lower()

            # Check file extension
            if file_ext in self.EXTENSION_MAP:
                name, category, confidence = self.EXTENSION_MAP[file_ext]
                key = f"{name}:{category.value}"

                if key not in detected_items:
                    detected_items[key] = TechStackItem(
                        name=name,
                        category=category,
                        confidence=confidence,
                        detection_method="file_extension"
                    )
                else:
                    # Increase confidence for multiple files
                    detected_items[key].confidence = min(
                        1.0,
                        detected_items[key].confidence + 0.05
                    )

            # Check config files
            if file_name in self.CONFIG_FILE_MAP:
                name, category, confidence = self.CONFIG_FILE_MAP[file_name]
                key = f"{name}:{category.value}"

                if key not in detected_items:
                    detected_items[key] = TechStackItem(
                        name=name,
                        category=category,
                        confidence=confidence,
                        detection_method="config_file"
                    )

        # Add all detected items
        for item in detected_items.values():
            tech_stack.add_item(item)

        # Calculate overall confidence
        if detected_items:
            tech_stack.confidence_score = sum(
                item.confidence for item in detected_items.values()
            ) / len(detected_items)

        tech_stack.detection_methods.append("file_analysis")

        # Detect TypeScript when tsx/ts files found
        if any(f.endswith(('.tsx', '.ts')) for f in files) and "typescript" not in tech_stack.languages:
            tech_stack.add_item(TechStackItem(
                name="typescript",
                category=TechCategory.LANGUAGE,
                confidence=0.95,
                detection_method="file_extension"
            ))

        # Set primary language
        tech_stack.primary_language = tech_stack.get_primary_language()

        return tech_stack

    def detect_from_ast(self, imports: List[str]) -> TechStack:
        """
        Detect tech stack from AST imports.

        Analyzes import statements to identify frameworks and libraries.

        Args:
            imports: List of import module names

        Returns:
            TechStack with detected technologies

        Examples:
            >>> analyzer = TechStackAnalyzer()
            >>> result = analyzer.detect_from_ast(["flask", "sqlalchemy"])
            >>> assert "flask" in result.frameworks
        """
        tech_stack = TechStack()

        if not imports:
            return tech_stack

        detected_items: Dict[str, TechStackItem] = {}

        for imp in imports:
            # Normalize import (handle submodules)
            base_module = imp.split(".")[0]

            # Check both base and full import
            for module_name in [base_module, imp]:
                if module_name in self.IMPORT_MAP:
                    name, category, confidence = self.IMPORT_MAP[module_name]
                    key = f"{name}:{category.value}"

                    if key not in detected_items:
                        detected_items[key] = TechStackItem(
                            name=name,
                            category=category,
                            confidence=confidence,
                            detection_method="ast_import"
                        )
                    break  # Don't double-count

        # Add all detected items
        for item in detected_items.values():
            tech_stack.add_item(item)

        # Calculate overall confidence
        if detected_items:
            tech_stack.confidence_score = sum(
                item.confidence for item in detected_items.values()
            ) / len(detected_items)

        tech_stack.detection_methods.append("ast_analysis")

        return tech_stack

    def merge_detections(self, *tech_stacks: TechStack) -> TechStack:
        """
        Merge multiple TechStack detection results.

        Combines results from file analysis and AST analysis,
        deduplicating and boosting confidence for items found
        via multiple methods.

        Args:
            *tech_stacks: Variable number of TechStack objects

        Returns:
            Merged TechStack with combined detections

        Examples:
            >>> analyzer = TechStackAnalyzer()
            >>> file_result = analyzer.detect_from_files(["app.py"])
            >>> ast_result = analyzer.detect_from_ast(["flask"])
            >>> merged = analyzer.merge_detections(file_result, ast_result)
            >>> assert merged.confidence_score > file_result.confidence_score
        """
        merged = TechStack()

        # Track items by key (name:category)
        items_by_key: Dict[str, TechStackItem] = {}
        detection_methods_set: Set[str] = set()

        for tech_stack in tech_stacks:
            for item in tech_stack.items:
                key = f"{item.name}:{item.category.value}"

                if key in items_by_key:
                    # Item found via multiple methods - boost confidence
                    existing = items_by_key[key]
                    existing.confidence = min(
                        1.0,
                        existing.confidence + (item.confidence * 0.2)
                    )
                    existing.detection_method = f"{existing.detection_method}+{item.detection_method}"
                else:
                    items_by_key[key] = TechStackItem(
                        name=item.name,
                        category=item.category,
                        version=item.version,
                        confidence=item.confidence,
                        detection_method=item.detection_method
                    )

            detection_methods_set.update(tech_stack.detection_methods)

        # Add all merged items
        for item in items_by_key.values():
            merged.add_item(item)

        # Calculate overall confidence
        if items_by_key:
            merged.confidence_score = sum(
                item.confidence for item in items_by_key.values()
            ) / len(items_by_key)

        merged.detection_methods = list(detection_methods_set)

        # Set primary language
        merged.primary_language = merged.get_primary_language()

        return merged

    def analyze(
        self,
        files: Optional[List[str]] = None,
        imports: Optional[List[str]] = None
    ) -> TechStack:
        """
        Analyze tech stack using all available detection methods.

        Combines file extension analysis, config file detection,
        and AST import analysis for comprehensive stack identification.

        Args:
            files: Optional list of file paths
            imports: Optional list of import statements

        Returns:
            Complete TechStack with merged detections

        Examples:
            >>> analyzer = TechStackAnalyzer()
            >>> result = analyzer.analyze(
            ...     files=["app.py", "requirements.txt"],
            ...     imports=["flask", "sqlalchemy"]
            ... )
            >>> assert "python" in result.languages
            >>> assert "flask" in result.frameworks
        """
        # Check cache
        cache_key = self._get_cache_key(files or [], imports or [])
        if cache_key in self._cache:
            self.logger.debug(f"Cache hit for tech stack analysis: {cache_key[:16]}...")
            return self._cache[cache_key]

        results: List[TechStack] = []

        if files:
            file_result = self.detect_from_files(files)
            results.append(file_result)

        if imports:
            ast_result = self.detect_from_ast(imports)
            results.append(ast_result)

        if not results:
            return TechStack()

        # Merge all detection results
        merged = self.merge_detections(*results)

        # Cache result
        self._cache[cache_key] = merged

        return merged

    def _get_cache_key(self, files: List[str], imports: List[str]) -> str:
        """
        Generate cache key for detection results.

        Args:
            files: List of file paths
            imports: List of imports

        Returns:
            SHA256 hash of inputs
        """
        content = "|".join(sorted(files)) + "||" + "|".join(sorted(imports))
        return hashlib.sha256(content.encode()).hexdigest()


# AC_COMPLETE: AC-PHASE90-S1-T1 ✅
# Description: TechStackAnalyzer GREEN implementation complete
