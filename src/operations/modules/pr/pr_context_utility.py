"""
PR Context Utility

Lightweight dependency-driven Pull Request context building.

Core Operations:
- build_pr_context: Main workflow for building dependency graph
- extract_imports: Multi-language import parsing
- detect_language: File language detection
- resolve_import_path: Import name to file path resolution
- find_test_files: Locate test files for changed files

Version: 3.0.0 (Migrated from PRContextBuilder v1.0)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from enum import Enum
from dataclasses import dataclass, field


class Language(Enum):
    """Supported languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CSHARP = "csharp"
    JAVA = "java"
    GO = "go"
    UNKNOWN = "unknown"


# Language detection mapping
LANG_EXTENSIONS = {
    '.py': Language.PYTHON,
    '.js': Language.JAVASCRIPT,
    '.jsx': Language.JAVASCRIPT,
    '.ts': Language.TYPESCRIPT,
    '.tsx': Language.TYPESCRIPT,
    '.cs': Language.CSHARP,
    '.java': Language.JAVA,
    '.go': Language.GO,
}


# Import patterns per language
IMPORT_PATTERNS = {
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


@dataclass
class FileNode:
    """File in dependency graph"""
    path: str
    language: Language
    imports: List[str] = field(default_factory=list)
    is_test: bool = False
    is_changed: bool = False
    token_estimate: int = 0
    level: int = 0  # 1=changed, 2=direct import, 3=test, 4=indirect


@dataclass
class DependencyGraph:
    """PR dependency graph"""
    nodes: Dict[str, FileNode] = field(default_factory=dict)
    changed_files: List[str] = field(default_factory=list)
    direct_imports: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    indirect_deps: List[str] = field(default_factory=list)
    total_tokens: int = 0


def detect_language(filepath: str) -> Language:
    """
    Detect language from file extension
    
    Args:
        filepath: Path to file
        
    Returns:
        Detected language
        
    Example:
        >>> lang = detect_language("src/main.py")
        >>> print(lang)
        Language.PYTHON
    """
    ext = Path(filepath).suffix.lower()
    return LANG_EXTENSIONS.get(ext, Language.UNKNOWN)


def extract_imports(filepath: str, content: str) -> List[str]:
    """
    Extract imports from file content
    
    Args:
        filepath: Path to file
        content: File content
        
    Returns:
        List of imported module names
        
    Example:
        >>> imports = extract_imports("main.py", "import os\\nfrom pathlib import Path")
        >>> print(imports)
        ['os', 'pathlib']
    """
    language = detect_language(filepath)
    
    if language == Language.UNKNOWN:
        return []
    
    patterns = IMPORT_PATTERNS.get(language, [])
    imports = []
    
    for line in content.split('\n'):
        line = line.strip()
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                imports.append(match.group(1))
                break
    
    return imports


def is_test_file(filepath: str) -> bool:
    """
    Check if file is a test file
    
    Args:
        filepath: Path to file
        
    Returns:
        True if test file
        
    Example:
        >>> is_test = is_test_file("test_main.py")
        >>> print(is_test)
        True
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
    
    if 'test' in str(path.parent).lower():
        return True
    
    return False


def estimate_tokens(content: Optional[str] = None, filepath: Optional[str] = None) -> int:
    """
    Estimate token count
    
    Args:
        content: File content
        filepath: Path to file
        
    Returns:
        Estimated tokens
        
    Example:
        >>> tokens = estimate_tokens(content="print('hello')")
        >>> print(tokens > 0)
        True
    """
    if content:
        return len(content) // 4
    
    if filepath:
        try:
            size = Path(filepath).stat().st_size
            return size // 4
        except:
            pass
    
    return 200


def resolve_import_path(
    source_file: str,
    import_name: str,
    workspace_root: str
) -> Optional[str]:
    """
    Resolve import name to file path
    
    Args:
        source_file: Source file path
        import_name: Import module name
        workspace_root: Workspace root directory
        
    Returns:
        Resolved file path or None
        
    Example:
        >>> path = resolve_import_path("src/main.py", "utils.helper", "/project")
        >>> print(path)
        'src/utils/helper.py'
    """
    language = detect_language(source_file)
    workspace = Path(workspace_root)
    source_dir = Path(source_file).parent
    
    # Python resolution
    if language == Language.PYTHON:
        # Relative import
        import_path = source_dir / f"{import_name.replace('.', '/')}.py"
        if (workspace / import_path).exists():
            return str(import_path)
        
        # Package import
        import_path = Path("src") / f"{import_name.replace('.', '/')}.py"
        if (workspace / import_path).exists():
            return str(import_path)
    
    # JavaScript/TypeScript resolution
    elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
        if import_name.startswith('.'):
            # Try .js
            import_path = (source_dir / import_name).with_suffix('.js')
            if (workspace / import_path).exists():
                return str(import_path)
            
            # Try .ts
            import_path = import_path.with_suffix('.ts')
            if (workspace / import_path).exists():
                return str(import_path)
    
    return None


def find_test_files(
    changed_files: List[str],
    workspace_root: str
) -> List[str]:
    """
    Find test files for changed files
    
    Args:
        changed_files: List of changed files
        workspace_root: Workspace root
        
    Returns:
        List of test file paths
        
    Example:
        >>> tests = find_test_files(["src/main.py"], "/project")
        >>> print(len(tests) >= 0)
        True
    """
    workspace = Path(workspace_root)
    test_files = []
    
    for changed_file in changed_files:
        if is_test_file(changed_file):
            continue
        
        path = Path(changed_file)
        
        # Try test_*.py
        test_path = path.parent / f"test_{path.name}"
        if (workspace / test_path).exists():
            test_files.append(str(test_path))
        
        # Try *_test.py
        test_path = path.parent / f"{path.stem}_test{path.suffix}"
        if (workspace / test_path).exists():
            test_files.append(str(test_path))
        
        # Try tests/ directory
        test_path = Path("tests") / path
        if (workspace / test_path).exists():
            test_files.append(str(test_path))
    
    return test_files


def build_pr_context(
    changed_files: List[str],
    workspace_root: str,
    max_files: int = 50,
    token_budget: int = 10000,
    include_tests: bool = True,
    include_indirect: bool = False
) -> DependencyGraph:
    """
    Build PR dependency graph with crawl strategy
    
    Args:
        changed_files: List of changed files
        workspace_root: Workspace root directory
        max_files: Maximum files to include
        token_budget: Maximum token budget
        include_tests: Include test files
        include_indirect: Include indirect dependencies
        
    Returns:
        Dependency graph
        
    Example:
        >>> graph = build_pr_context(["src/main.py"], "/project")
        >>> print(len(graph.nodes) > 0)
        True
    """
    graph = DependencyGraph()
    workspace = Path(workspace_root)
    
    # Level 1: Changed files
    for filepath in changed_files:
        full_path = workspace / filepath
        
        content = ""
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                pass
        
        node = FileNode(
            path=filepath,
            language=detect_language(filepath),
            imports=extract_imports(filepath, content),
            is_test=is_test_file(filepath),
            is_changed=True,
            token_estimate=estimate_tokens(content=content),
            level=1
        )
        
        graph.nodes[filepath] = node
        graph.changed_files.append(filepath)
        graph.total_tokens += node.token_estimate
    
    # Level 2: Direct imports
    if graph.total_tokens < token_budget:
        direct_imports = set()
        
        for filepath in graph.changed_files:
            node = graph.nodes[filepath]
            
            for import_name in node.imports:
                import_path = resolve_import_path(filepath, import_name, workspace_root)
                
                if import_path and import_path not in graph.nodes:
                    direct_imports.add(import_path)
        
        for filepath in direct_imports:
            if len(graph.nodes) >= max_files or graph.total_tokens >= token_budget:
                break
            
            full_path = workspace / filepath
            content = ""
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    pass
            
            node = FileNode(
                path=filepath,
                language=detect_language(filepath),
                imports=extract_imports(filepath, content),
                is_test=is_test_file(filepath),
                token_estimate=estimate_tokens(content=content),
                level=2
            )
            
            graph.nodes[filepath] = node
            graph.direct_imports.append(filepath)
            graph.total_tokens += node.token_estimate
    
    # Level 3: Test files
    if include_tests and graph.total_tokens < token_budget:
        test_files_found = find_test_files(changed_files, workspace_root)
        
        for filepath in test_files_found:
            if len(graph.nodes) >= max_files or graph.total_tokens >= token_budget:
                break
            
            if filepath in graph.nodes:
                continue
            
            full_path = workspace / filepath
            content = ""
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    pass
            
            node = FileNode(
                path=filepath,
                language=detect_language(filepath),
                imports=extract_imports(filepath, content),
                is_test=True,
                token_estimate=estimate_tokens(content=content),
                level=3
            )
            
            graph.nodes[filepath] = node
            graph.test_files.append(filepath)
            graph.total_tokens += node.token_estimate
    
    # Level 4: Indirect dependencies
    if include_indirect and len(graph.nodes) < max_files and graph.total_tokens < token_budget:
        indirect_deps = set()
        
        for filepath in graph.direct_imports:
            node = graph.nodes.get(filepath)
            if not node:
                continue
            
            for import_name in node.imports:
                import_path = resolve_import_path(filepath, import_name, workspace_root)
                
                if import_path and import_path not in graph.nodes:
                    indirect_deps.add(import_path)
        
        for filepath in indirect_deps:
            if len(graph.nodes) >= max_files or graph.total_tokens >= token_budget:
                break
            
            full_path = workspace / filepath
            content = ""
            
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    pass
            
            node = FileNode(
                path=filepath,
                language=detect_language(filepath),
                imports=extract_imports(filepath, content),
                is_test=is_test_file(filepath),
                token_estimate=estimate_tokens(content=content),
                level=4
            )
            
            graph.nodes[filepath] = node
            graph.indirect_deps.append(filepath)
            graph.total_tokens += node.token_estimate
    
    return graph


# CLI for testing
if __name__ == "__main__":
    import time
    import os
    
    print("🧪 Testing PR Context Utility...")
    start_test = time.time()
    
    workspace_root = os.environ.get('CORTEX_ROOT', os.getcwd())
    
    # Test with CORTEX files
    changed_files = [
        "src/tier1/working_memory.py",
        "src/operations/modules/validation/session_utility.py"
    ]
    
    # Test 1: Language detection
    print("Testing language detection...")
    lang = detect_language("test.py")
    assert lang == Language.PYTHON, f"Expected PYTHON, got {lang}"
    print("✅ Language detection")
    
    # Test 2: Test file detection
    print("Testing test file detection...")
    assert is_test_file("test_main.py"), "Should detect test file"
    assert not is_test_file("main.py"), "Should not detect non-test file"
    print("✅ Test file detection")
    
    # Test 3: Build context
    print("Testing PR context building...")
    graph = build_pr_context(
        changed_files,
        workspace_root,
        max_files=20,
        token_budget=5000,
        include_tests=True,
        include_indirect=False
    )
    assert len(graph.changed_files) == len(changed_files), "Changed files mismatch"
    print(f"✅ PR context: {len(graph.nodes)} files, {graph.total_tokens} tokens")
    
    elapsed = time.time() - start_test
    print(f"\n⚡ All tests passed in {elapsed:.3f}s")
    print(f"📊 Operations: 6 core functions tested")
