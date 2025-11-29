"""
PR Context Builder for Code Review

Purpose:
- Implements dependency-driven context building for Pull Requests
- Parses file imports and references
- Builds dependency graph with 3-level crawling strategy
- Enforces token budget (5-10K tokens target)

Crawl Strategy:
- Level 1 (Always): Changed files
- Level 2 (Always): Direct imports from changed files
- Level 3 (Conditional): Test files if exist
- Level 4 (Capped): Indirect dependencies if total <50 files

Author: Asif Hussain
Created: 2025-11-26
Version: 1.0 (Phase 2)
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages for import analysis."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CSHARP = "csharp"
    JAVA = "java"
    GO = "go"
    UNKNOWN = "unknown"


@dataclass
class FileNode:
    """Represents a file in the dependency graph."""
    path: str
    language: Language
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    is_test: bool = False
    is_changed: bool = False
    token_estimate: int = 0
    level: int = 0  # Crawl level (1=changed, 2=direct import, 3=test, 4=indirect)


@dataclass
class DependencyGraph:
    """Dependency graph for PR context."""
    nodes: Dict[str, FileNode] = field(default_factory=dict)
    changed_files: List[str] = field(default_factory=list)
    direct_imports: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    indirect_deps: List[str] = field(default_factory=list)
    total_tokens: int = 0
    
    def add_node(self, node: FileNode) -> None:
        """Add node to graph."""
        self.nodes[node.path] = node
        
        # Categorize by level
        if node.is_changed:
            if node.path not in self.changed_files:
                self.changed_files.append(node.path)
        elif node.level == 2:
            if node.path not in self.direct_imports:
                self.direct_imports.append(node.path)
        elif node.is_test:
            if node.path not in self.test_files:
                self.test_files.append(node.path)
        elif node.level == 4:
            if node.path not in self.indirect_deps:
                self.indirect_deps.append(node.path)
    
    def get_all_files(self) -> List[str]:
        """Get all files in order: changed → direct imports → tests → indirect."""
        return (
            self.changed_files +
            self.direct_imports +
            self.test_files +
            self.indirect_deps
        )
    
    def get_file_count(self) -> int:
        """Get total file count."""
        return len(self.nodes)


class ImportAnalyzer:
    """
    Multi-language import analyzer.
    
    Supports:
    - Python: import, from...import
    - JavaScript/TypeScript: import, require
    - C#: using
    - Java: import
    - Go: import
    """
    
    # Import patterns by language
    PATTERNS = {
        Language.PYTHON: [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',
        ],
        Language.JAVASCRIPT: [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\([\'"]([^\'"]+)[\'"]\)',
        ],
        Language.TYPESCRIPT: [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\([\'"]([^\'"]+)[\'"]\)',
        ],
        Language.CSHARP: [
            r'^using\s+([a-zA-Z_][a-zA-Z0-9_\.]*);',
        ],
        Language.JAVA: [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_\.]*);',
        ],
        Language.GO: [
            r'import\s+[\'"]([^\'"]+)[\'"]',
        ],
    }
    
    @staticmethod
    def detect_language(filepath: str) -> Language:
        """
        Detect programming language from file extension.
        
        Args:
            filepath: Path to file
        
        Returns:
            Detected language
        """
        ext = Path(filepath).suffix.lower()
        
        mapping = {
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.jsx': Language.JAVASCRIPT,
            '.ts': Language.TYPESCRIPT,
            '.tsx': Language.TYPESCRIPT,
            '.cs': Language.CSHARP,
            '.java': Language.JAVA,
            '.go': Language.GO,
        }
        
        return mapping.get(ext, Language.UNKNOWN)
    
    @staticmethod
    def is_test_file(filepath: str) -> bool:
        """
        Detect if file is a test file.
        
        Patterns:
        - *_test.py, test_*.py
        - *.test.js, *.spec.js
        - *Test.cs, *Tests.cs
        - *Test.java
        
        Args:
            filepath: Path to file
        
        Returns:
            True if test file
        """
        path = Path(filepath)
        name = path.stem.lower()
        
        test_patterns = [
            r'test_',
            r'_test$',
            r'\.test$',
            r'\.spec$',
            r'tests?$',
        ]
        
        for pattern in test_patterns:
            if re.search(pattern, name):
                return True
        
        # Check directory name
        if 'test' in str(path.parent).lower():
            return True
        
        return False
    
    @staticmethod
    def extract_imports(filepath: str, content: str) -> List[str]:
        """
        Extract imports from file content.
        
        Args:
            filepath: Path to file (for language detection)
            content: File content
        
        Returns:
            List of imported module/file names
        """
        language = ImportAnalyzer.detect_language(filepath)
        
        if language == Language.UNKNOWN:
            return []
        
        patterns = ImportAnalyzer.PATTERNS.get(language, [])
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    import_name = match.group(1)
                    imports.append(import_name)
                    break
        
        return imports
    
    @staticmethod
    def estimate_tokens(filepath: str, content: Optional[str] = None) -> int:
        """
        Estimate token count for file.
        
        Rough estimate: 1 token per 4 characters
        
        Args:
            filepath: Path to file
            content: File content (if available)
        
        Returns:
            Estimated token count
        """
        if content:
            return len(content) // 4
        
        # Estimate from file size
        try:
            size = Path(filepath).stat().st_size
            return size // 4
        except:
            return 200  # Default estimate


class PRContextBuilder:
    """
    Builds context for Pull Request analysis using dependency-driven crawling.
    
    Strategy:
    1. Start with changed files (Level 1)
    2. Add direct imports (Level 2)
    3. Add test files (Level 3)
    4. Add indirect dependencies if space allows (Level 4)
    """
    
    def __init__(
        self,
        workspace_root: str,
        max_files: int = 50,
        token_budget: int = 10000,
        include_tests: bool = True,
        include_indirect: bool = False
    ):
        """
        Initialize context builder.
        
        Args:
            workspace_root: Path to workspace root
            max_files: Maximum files to include
            token_budget: Maximum token budget
            include_tests: Include test files
            include_indirect: Include indirect dependencies
        """
        self.workspace_root = Path(workspace_root)
        self.max_files = max_files
        self.token_budget = token_budget
        self.include_tests = include_tests
        self.include_indirect = include_indirect
        
        logger.info(
            f"PRContextBuilder initialized: "
            f"max_files={max_files}, token_budget={token_budget}"
        )
    
    def build_context(
        self,
        changed_files: List[str],
        file_contents: Optional[Dict[str, str]] = None
    ) -> DependencyGraph:
        """
        Build dependency graph for changed files.
        
        Args:
            changed_files: List of changed file paths
            file_contents: Optional dict of file path -> content
        
        Returns:
            Dependency graph
        """
        graph = DependencyGraph()
        file_contents = file_contents or {}
        
        logger.info(f"Building context for {len(changed_files)} changed files")
        
        # Level 1: Process changed files
        for filepath in changed_files:
            node = self._create_file_node(
                filepath,
                file_contents.get(filepath),
                level=1,
                is_changed=True
            )
            graph.add_node(node)
            graph.total_tokens += node.token_estimate
        
        logger.info(
            f"Level 1 complete: {len(changed_files)} files, "
            f"{graph.total_tokens} tokens"
        )
        
        # Level 2: Add direct imports
        if graph.total_tokens < self.token_budget:
            direct_imports = self._find_direct_imports(graph, file_contents)
            
            for filepath in direct_imports:
                if graph.get_file_count() >= self.max_files:
                    logger.warning(f"Max files reached at Level 2: {self.max_files}")
                    break
                
                if graph.total_tokens >= self.token_budget:
                    logger.warning(f"Token budget reached at Level 2: {self.token_budget}")
                    break
                
                node = self._create_file_node(
                    filepath,
                    file_contents.get(filepath),
                    level=2
                )
                graph.add_node(node)
                graph.total_tokens += node.token_estimate
            
            logger.info(
                f"Level 2 complete: +{len(direct_imports)} imports, "
                f"{graph.total_tokens} tokens"
            )
        
        # Level 3: Add test files
        if self.include_tests and graph.total_tokens < self.token_budget:
            test_files = self._find_test_files(changed_files, file_contents)
            
            for filepath in test_files:
                if graph.get_file_count() >= self.max_files:
                    logger.warning(f"Max files reached at Level 3: {self.max_files}")
                    break
                
                if graph.total_tokens >= self.token_budget:
                    logger.warning(f"Token budget reached at Level 3: {self.token_budget}")
                    break
                
                node = self._create_file_node(
                    filepath,
                    file_contents.get(filepath),
                    level=3,
                    is_test=True
                )
                graph.add_node(node)
                graph.total_tokens += node.token_estimate
            
            logger.info(
                f"Level 3 complete: +{len(test_files)} tests, "
                f"{graph.total_tokens} tokens"
            )
        
        # Level 4: Add indirect dependencies (capped)
        if (
            self.include_indirect and
            graph.get_file_count() < self.max_files and
            graph.total_tokens < self.token_budget
        ):
            indirect_deps = self._find_indirect_deps(graph, file_contents)
            remaining_slots = self.max_files - graph.get_file_count()
            
            for filepath in indirect_deps[:remaining_slots]:
                if graph.total_tokens >= self.token_budget:
                    logger.warning(f"Token budget reached at Level 4: {self.token_budget}")
                    break
                
                node = self._create_file_node(
                    filepath,
                    file_contents.get(filepath),
                    level=4
                )
                graph.add_node(node)
                graph.total_tokens += node.token_estimate
            
            logger.info(
                f"Level 4 complete: +{len(indirect_deps[:remaining_slots])} indirect, "
                f"{graph.total_tokens} tokens"
            )
        
        logger.info(
            f"Context building complete: "
            f"{graph.get_file_count()} files, {graph.total_tokens} tokens"
        )
        
        return graph
    
    def _create_file_node(
        self,
        filepath: str,
        content: Optional[str],
        level: int,
        is_changed: bool = False,
        is_test: bool = False
    ) -> FileNode:
        """
        Create file node with metadata.
        
        Args:
            filepath: Path to file
            content: File content (optional)
            level: Crawl level
            is_changed: Whether file is in changed set
            is_test: Whether file is a test file
        
        Returns:
            File node
        """
        # Resolve full path
        full_path = self.workspace_root / filepath
        
        # Load content if not provided
        if content is None and full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = ""
        
        # Detect language and extract imports
        language = ImportAnalyzer.detect_language(filepath)
        imports = ImportAnalyzer.extract_imports(filepath, content or "") if content else []
        
        # Detect if test file (if not already marked)
        if not is_test:
            is_test = ImportAnalyzer.is_test_file(filepath)
        
        # Estimate tokens
        token_estimate = ImportAnalyzer.estimate_tokens(filepath, content)
        
        return FileNode(
            path=filepath,
            language=language,
            imports=imports,
            is_test=is_test,
            is_changed=is_changed,
            token_estimate=token_estimate,
            level=level
        )
    
    def _find_direct_imports(
        self,
        graph: DependencyGraph,
        file_contents: Dict[str, str]
    ) -> List[str]:
        """
        Find files directly imported by changed files.
        
        Args:
            graph: Current dependency graph
            file_contents: File contents cache
        
        Returns:
            List of imported file paths
        """
        direct_imports = set()
        
        for filepath in graph.changed_files:
            node = graph.nodes.get(filepath)
            if not node:
                continue
            
            # Convert import names to file paths
            for import_name in node.imports:
                import_path = self._resolve_import_path(filepath, import_name, node.language)
                
                if import_path and import_path not in graph.nodes:
                    direct_imports.add(import_path)
        
        return list(direct_imports)
    
    def _resolve_import_path(
        self,
        source_file: str,
        import_name: str,
        language: Language
    ) -> Optional[str]:
        """
        Resolve import name to file path.
        
        Args:
            source_file: Source file path
            import_name: Import module/package name
            language: Programming language
        
        Returns:
            Resolved file path or None
        """
        source_dir = Path(source_file).parent
        
        # Language-specific resolution
        if language == Language.PYTHON:
            # Try relative import
            import_path = source_dir / f"{import_name.replace('.', '/')}.py"
            if (self.workspace_root / import_path).exists():
                return str(import_path)
            
            # Try package import
            import_path = Path("src") / f"{import_name.replace('.', '/')}.py"
            if (self.workspace_root / import_path).exists():
                return str(import_path)
        
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            # Relative imports
            if import_name.startswith('.'):
                import_path = (source_dir / import_name).with_suffix('.js')
                if (self.workspace_root / import_path).exists():
                    return str(import_path)
                
                # Try .ts extension
                import_path = import_path.with_suffix('.ts')
                if (self.workspace_root / import_path).exists():
                    return str(import_path)
        
        elif language == Language.CSHARP:
            # C# namespace to file mapping is complex
            # For now, skip external imports
            pass
        
        return None
    
    def _find_test_files(
        self,
        changed_files: List[str],
        file_contents: Dict[str, str]
    ) -> List[str]:
        """
        Find test files related to changed files.
        
        Strategy:
        - Look for test_*.py, *_test.py patterns
        - Look in tests/ directory
        - Match file names
        
        Args:
            changed_files: List of changed files
            file_contents: File contents cache
        
        Returns:
            List of test file paths
        """
        test_files = []
        
        for changed_file in changed_files:
            # Skip if already a test file
            if ImportAnalyzer.is_test_file(changed_file):
                continue
            
            path = Path(changed_file)
            
            # Try test_*.py pattern
            test_path = path.parent / f"test_{path.name}"
            if (self.workspace_root / test_path).exists():
                test_files.append(str(test_path))
            
            # Try *_test.py pattern
            test_path = path.parent / f"{path.stem}_test{path.suffix}"
            if (self.workspace_root / test_path).exists():
                test_files.append(str(test_path))
            
            # Try tests/ directory
            test_path = Path("tests") / path
            if (self.workspace_root / test_path).exists():
                test_files.append(str(test_path))
        
        return test_files
    
    def _find_indirect_deps(
        self,
        graph: DependencyGraph,
        file_contents: Dict[str, str]
    ) -> List[str]:
        """
        Find indirect dependencies (imports of imports).
        
        Args:
            graph: Current dependency graph
            file_contents: File contents cache
        
        Returns:
            List of indirect dependency paths
        """
        indirect_deps = set()
        
        # Process imports from direct imports
        for filepath in graph.direct_imports:
            node = graph.nodes.get(filepath)
            if not node:
                continue
            
            for import_name in node.imports:
                import_path = self._resolve_import_path(filepath, import_name, node.language)
                
                if import_path and import_path not in graph.nodes:
                    indirect_deps.add(import_path)
        
        return list(indirect_deps)


def main():
    """CLI entry point for testing."""
    import sys
    import json
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get workspace root
    workspace_root = os.environ.get('CORTEX_ROOT', os.getcwd())
    
    # Test data
    changed_files = [
        "src/orchestrators/code_review_orchestrator.py",
        "src/tier1/working_memory.py"
    ]
    
    # Initialize builder
    builder = PRContextBuilder(
        workspace_root=workspace_root,
        max_files=50,
        token_budget=10000,
        include_tests=True,
        include_indirect=False
    )
    
    # Build context
    graph = builder.build_context(changed_files)
    
    # Print results
    print("\n=== Dependency Graph ===")
    print(f"Total files: {graph.get_file_count()}")
    print(f"Total tokens: {graph.total_tokens}")
    print(f"\nChanged files ({len(graph.changed_files)}):")
    for f in graph.changed_files:
        print(f"  - {f}")
    print(f"\nDirect imports ({len(graph.direct_imports)}):")
    for f in graph.direct_imports:
        print(f"  - {f}")
    print(f"\nTest files ({len(graph.test_files)}):")
    for f in graph.test_files:
        print(f"  - {f}")
    print(f"\nIndirect deps ({len(graph.indirect_deps)}):")
    for f in graph.indirect_deps:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
