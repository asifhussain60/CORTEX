"""
AC_START: AC-PHASE44-S1-002
RepositoryScanner - Comprehensive repository scanning for cleanup candidates
Phase 44 Stage 1 - Production Readiness Infrastructure
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class RepositoryScanner:
    """
    Comprehensive repository scanner for Phase 44 cleanup operations.

    Scans for:
    - Root directory pollution (utility scripts, test files)
    - Legacy/orphaned test files
    - Markdown sprawl outside docs/
    - Duplicate implementations (AST-based)
    - Import references for impact analysis

    Usage:
        scanner = RepositoryScanner()
        result = scanner.scan_root_directory("/path/to/repo")
        duplicates = scanner.detect_duplicates(file_list)
    """

    def __init__(self) -> None:
        """Initialize RepositoryScanner."""
        self.exclude_patterns = {
            ".git", ".pytest_cache", "__pycache__", "node_modules",
            ".venv", "venv", ".tox", "dist", "build"
        }

        self.production_files = {
            "README.md", "LICENSE", "LICENSE.md", "CONTRIBUTING.md",
            "Dockerfile", "docker-compose.yml", "Makefile",
            "requirements.txt", "setup.py", "pyproject.toml", "pytest.ini"
        }

    def scan_root_directory(self, root_path: str) -> Dict[str, Any]:
        """
        Scan root directory for cleanup candidates.

        AC-044-S1-01: Inventory includes 100% of root .py files
        AC-044-S1-02: Categorizes files by relocation rules (ENH-062)

        Args:
            root_path: Path to repository root

        Returns:
            Dictionary with categorized files
        """
        root = Path(root_path)
        python_files = []
        utility_scripts = []
        test_files = []
        config_files = []

        try:
            for item in root.iterdir():
                if item.is_file():
                    filename = item.name

                    # Skip production files
                    if filename in self.production_files:
                        continue

                    # Categorize Python files
                    if filename.endswith(".py"):
                        python_files.append(filename)

                        # Categorize by pattern
                        if filename.startswith("test_") or filename.endswith("_test.py"):
                            test_files.append(filename)
                        elif any(pattern in filename for pattern in ["generate_", "run_", "verify_"]):
                            utility_scripts.append(filename)

                    # Config files
                    elif filename.endswith((".yaml", ".yml", ".json", ".toml")):
                        config_files.append(filename)

            return {
                "status": "success",
                "python_files": python_files,
                "utility_scripts": utility_scripts,
                "test_files": test_files,
                "config_files": config_files,
                "total_files": len(python_files) + len(config_files)
            }

        except Exception as e:
            logger.error(f"Failed to scan root directory: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def scan_legacy_tests(self, root_path: str) -> Dict[str, Any]:
        """
        Scan for orphaned/broken test files.

        AC-044-S1-03: Identifies 13+ orphaned test files
        AC-044-S1-04: Analyzes fixtures and imports for each test

        Args:
            root_path: Path to repository root

        Returns:
            Dictionary with legacy test analysis
        """
        root = Path(root_path)
        legacy_dir = root / "tests" / "_legacy_broken"

        if not legacy_dir.exists():
            return {
                "status": "success",
                "legacy_tests_count": 0,
                "tests": []
            }

        legacy_tests = []

        try:
            for test_file in legacy_dir.rglob("test_*.py"):
                # Analyze test file
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse imports and fixtures
                imports = self._extract_imports(content)
                fixtures = self._extract_fixtures(content)

                legacy_tests.append({
                    "file": str(test_file.relative_to(root)),
                    "imports": imports,
                    "fixtures": fixtures,
                    "size_bytes": test_file.stat().st_size
                })

            return {
                "status": "success",
                "legacy_tests_count": len(legacy_tests),
                "tests": legacy_tests
            }

        except Exception as e:
            logger.error(f"Failed to scan legacy tests: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def scan_markdown_sprawl(self, root_path: str) -> Dict[str, Any]:
        """
        Scan for markdown files outside docs/.

        AC-044-S1-05: Identifies 20+ markdown files for archival
        AC-044-S1-06: Excludes README.md and production docs

        Args:
            root_path: Path to repository root

        Returns:
            Dictionary with markdown file candidates
        """
        root = Path(root_path)
        candidates = []

        try:
            # Scan root level
            for md_file in root.glob("*.md"):
                filename = md_file.name

                # Exclude production docs
                if filename in self.production_files:
                    continue

                candidates.append(str(md_file.relative_to(root)))

            # Scan subdirectories (excluding docs/)
            for md_file in root.rglob("*.md"):
                relative = md_file.relative_to(root)

                # Skip docs/ and .github/
                if relative.parts[0] in {"docs", ".github"}:
                    continue

                # Skip production files
                if md_file.name in self.production_files:
                    continue

                candidates.append(str(relative))

            return {
                "status": "success",
                "candidates": candidates,
                "count": len(candidates)
            }

        except Exception as e:
            logger.error(f"Failed to scan markdown files: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def detect_duplicates(self, file_paths: List[str], similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Detect duplicate implementations using AST similarity.

        AC-044-S1-07: Detects 6+ known duplicates (similarity > 0.7)
        AC-044-S1-08: Aligns with ENH-061 duplicate targets

        Args:
            file_paths: List of Python files to analyze
            similarity_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            Dictionary with duplicate pairs and similarity scores
        """
        duplicates = []

        try:
            # Compare each pair of files
            for i, file1 in enumerate(file_paths):
                for file2 in file_paths[i+1:]:
                    similarity = self._calculate_similarity(file1, file2)

                    if similarity >= similarity_threshold:
                        duplicates.append({
                            "file1": file1,
                            "file2": file2,
                            "similarity": similarity
                        })

            return {
                "duplicates_found": len(duplicates),
                "duplicates": duplicates,
                "threshold": similarity_threshold
            }

        except Exception as e:
            logger.error(f"Failed to detect duplicates: {e}")
            return {
                "duplicates_found": 0,
                "duplicates": [],
                "error": str(e)
            }

    def map_import_references(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Map import references for relocation impact analysis.

        AC-044-S1-09: Maps 200+ import references to scan targets
        AC-044-S1-10: Calculates impact scores for relocations

        Args:
            file_paths: List of Python files to analyze

        Returns:
            Dictionary with import map and impact scores
        """
        import_map: Dict[str, List[str]] = {}
        impact_scores: Dict[str, float] = {}

        try:
            from cortex.orchestrators.support.import_reference_analyzer import (
                ImportReferenceAnalyzer,
            )

            analyzer = ImportReferenceAnalyzer()

            for file_path in file_paths:
                refs = analyzer.find_references(file_path, "")

                # Build import map
                for ref in refs:
                    module = ref.get("module", "")
                    if module not in import_map:
                        import_map[module] = []
                    import_map[module].append(file_path)

            # Calculate impact scores (number of files affected)
            for module, files in import_map.items():
                impact_scores[module] = len(files) / len(file_paths)

            return {
                "status": "success",
                "import_map": import_map,
                "impact_scores": impact_scores,
                "total_modules": len(import_map)
            }

        except Exception as e:
            logger.error(f"Failed to map imports: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except SyntaxError:
            pass
        return imports

    def _extract_fixtures(self, content: str) -> List[str]:
        """Extract pytest fixtures from test file."""
        fixtures = []
        # Simple regex-based extraction
        import re
        fixture_pattern = r'@pytest\.fixture(?:\([^)]*\))?\s+def\s+(\w+)'
        fixtures = re.findall(fixture_pattern, content)
        return fixtures

    def _calculate_similarity(self, file1: str, file2: str) -> float:
        """Calculate AST-based similarity between two Python files."""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                content1 = f.read()
            with open(file2, 'r', encoding='utf-8') as f:
                content2 = f.read()

            # Parse ASTs
            tree1 = ast.parse(content1)
            tree2 = ast.parse(content2)

            # Simple similarity: compare function names
            funcs1 = {node.name for node in ast.walk(tree1) if isinstance(node, ast.FunctionDef)}
            funcs2 = {node.name for node in ast.walk(tree2) if isinstance(node, ast.FunctionDef)}

            if not funcs1 and not funcs2:
                return 0.0

            # Jaccard similarity
            intersection = len(funcs1 & funcs2)
            union = len(funcs1 | funcs2)

            return intersection / union if union > 0 else 0.0

        except Exception:
            return 0.0


# AC_COMPLETE: AC-PHASE44-S1-002 ✅ RepositoryScanner implemented with 5 core methods
