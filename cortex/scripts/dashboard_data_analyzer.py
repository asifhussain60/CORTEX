"""
Testable data analysis functions for dashboard generation.

Extracted from generate_dashboard_data.py to enable unit testing.
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

AC-ID: TEST-DASH-REFACTOR-001
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


def analyze_repository(repo_path: Path) -> Dict[str, Any]:
    """
    Analyze repository and return basic statistics.
    
    Args:
        repo_path: Path to repository to analyze
        
    Returns:
        Dictionary with python_files, total_files, total_lines
        
    Raises:
        FileNotFoundError: If repo_path doesn't exist
        NotADirectoryError: If repo_path is not a directory
    """
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_path}")
    
    # Collect all Python files
    python_files = list(repo_path.glob("**/*.py"))
    
    # Filter out unwanted directories
    excluded_patterns = [
        "__pycache__",
        ".venv",
        "venv",
        "site-packages",
        ".git",
        ".vscode",
        ".pytest_cache",
        "node_modules"
    ]
    
    filtered_files = []
    for py_file in python_files:
        file_str = str(py_file)
        if not any(pattern in file_str for pattern in excluded_patterns):
            filtered_files.append(py_file)
    
    # Count total lines
    total_lines = 0
    for py_file in filtered_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                total_lines += len(f.readlines())
        except (OSError, UnicodeDecodeError):
            # Skip files that can't be read
            continue
    
    return {
        "python_files": filtered_files,
        "total_files": len(filtered_files),
        "total_lines": total_lines
    }


def analyze_imports(python_files: List[Path], repo_path: Path) -> Dict[str, Any]:
    """
    Analyze imports from Python files and build import graph.
    
    Args:
        python_files: List of Python file paths to analyze
        repo_path: Base repository path for relative path calculation
        
    Returns:
        Dictionary with modules list and imports list of (source, target) tuples
    """
    from cortex.brain.analysis.ast_analyzer import ASTAnalyzer
    
    ast_analyzer = ASTAnalyzer()
    modules: Set[str] = set()
    imports: List[Tuple[str, str]] = []
    circular_deps: List[List[str]] = []
    
    for py_file in python_files:
        try:
            # Get module name from file path
            rel_path = py_file.relative_to(repo_path)
            module_parts = list(rel_path.parts[:-1])  # Remove filename
            if rel_path.name != "__init__.py":
                module_parts.append(rel_path.stem)
            
            source_module = ".".join(module_parts) if module_parts else rel_path.stem
            
            if not source_module:
                continue
            
            modules.add(source_module)
            
            # Analyze imports
            result = ast_analyzer.analyze_file(py_file)
            if result.success:
                for import_info in result.imports:
                    target_module = import_info.module
                    if target_module:
                        # Include internal or major external dependencies
                        if (target_module.startswith(("cortex", "cortex_brain")) or
                            target_module in ["pytest", "fastapi", "click", "yaml", "pydantic"]):
                            modules.add(target_module)
                            imports.append((source_module, target_module))
        
        except (ValueError, OSError) as e:
            continue
    
    # Detect circular dependencies (simple DFS-based detection)
    circular_deps = _detect_circular_dependencies(imports)
    
    return {
        "modules": list(modules),
        "imports": imports,
        "circular": circular_deps
    }


def _detect_circular_dependencies(imports: List[Tuple[str, str]]) -> List[List[str]]:
    """
    Detect circular dependencies using DFS.
    
    Args:
        imports: List of (source, target) import tuples
        
    Returns:
        List of circular dependency chains
    """
    # Build adjacency list
    graph: Dict[str, List[str]] = {}
    for source, target in imports:
        if source not in graph:
            graph[source] = []
        graph[source].append(target)
    
    # DFS to detect cycles
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    cycles: List[List[str]] = []
    
    def dfs(node: str, path: List[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
        
        rec_stack.remove(node)
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return cycles[:10]  # Limit to 10 cycles for performance


def scan_orchestrators(repo_path: Path) -> List[Dict[str, Any]]:
    """
    Scan repository for orchestrator classes.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of orchestrator metadata dictionaries
    """
    orchestrators = []
    
    # Scan orchestrators directory
    orch_dir = repo_path / "cortex" / "orchestrators"
    if not orch_dir.exists():
        return orchestrators
    
    for py_file in orch_dir.glob("**/*.py"):
        if "__init__.py" in str(py_file):
            continue
        
        # Extract orchestrator name from filename
        name = py_file.stem
        if "orchestrator" in name.lower():
            orchestrators.append({
                "name": _to_class_name(name),
                "path": str(py_file.relative_to(repo_path)),
                "category": _get_orchestrator_category(py_file)
            })
    
    return orchestrators


def _to_class_name(snake_case: str) -> str:
    """Convert snake_case filename to ClassName."""
    parts = snake_case.split('_')
    return ''.join(word.capitalize() for word in parts)


def _get_orchestrator_category(file_path: Path) -> str:
    """Determine orchestrator category from file path."""
    path_str = str(file_path)
    if "cortical" in path_str:
        return "cortical"
    elif "support" in path_str:
        return "support"
    elif "domain" in path_str:
        return "domain"
    else:
        return "core"


def analyze_git_history(repo_path: Path, max_commits: int = 200) -> List[Dict[str, Any]]:
    """
    Analyze git history for timeline.
    
    Args:
        repo_path: Path to repository
        max_commits: Maximum number of commits to analyze
        
    Returns:
        List of commit metadata dictionaries
    """
    from cortex.brain.analysis.git_history_analyzer import GitHistoryAnalyzer
    
    commits = []
    
    try:
        # Get recent commits - GitHistoryAnalyzer requires repo_path parameter
        git_analyzer = GitHistoryAnalyzer(repo_path=repo_path)
        result = git_analyzer.analyze_recent_commits(repo_path, max_commits)
        if result.success:
            for commit_info in result.commits[:max_commits]:
                commits.append({
                    "date": commit_info.date,
                    "commit": commit_info.hash,
                    "message": commit_info.message,
                    "author": commit_info.author,
                    "files_changed": len(commit_info.files) if hasattr(commit_info, 'files') else 0
                })
    except Exception:
        # Return empty list if git analysis fails (not a git repo, etc.)
        pass
    
    return commits


def analyze_file_impact(python_files: List[Path], repo_path: Path) -> Dict[str, Any]:
    """
    Analyze file impact/importance based on import frequency.
    
    Args:
        python_files: List of Python files
        repo_path: Base repository path
        
    Returns:
        Dictionary with file impact rankings
    """
    # Count how many times each file is imported
    import_counts: Dict[str, int] = {}
    
    for py_file in python_files:
        try:
            rel_path = str(py_file.relative_to(repo_path))
            import_counts[rel_path] = 0
        except ValueError:
            continue
    
    # Simple heuristic: files in core directories have higher impact
    core_paths = ["cortex/core", "cortex/brain", "cortex/orchestrators"]
    
    high_impact = []
    medium_impact = []
    low_impact = []
    
    for file_path, count in import_counts.items():
        if any(core in file_path for core in core_paths):
            high_impact.append(file_path)
        elif "tests/" in file_path:
            low_impact.append(file_path)
        else:
            medium_impact.append(file_path)
    
    return {
        "high_impact": high_impact[:50],  # Limit for performance
        "medium_impact": medium_impact[:50],
        "low_impact": low_impact[:50]
    }


def analyze_brain_tiers(repo_path: Path) -> Dict[str, List[str]]:
    """
    Analyze brain tier structure.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        Dictionary mapping tier names to component lists
    """
    tiers = {
        "tier0": [],
        "tier1": [],
        "tier2": [],
        "tier3": []
    }
    
    # Scan cortex_brain directory
    brain_dir = repo_path / "cortex_brain"
    if brain_dir.exists():
        # Tier 0: Governance
        tier0_dir = brain_dir / "tier0"
        if tier0_dir.exists():
            tiers["tier0"] = [f.stem for f in tier0_dir.glob("*.py") if f.name != "__init__.py"]
        
        # Tier 1: Audit
        tier1_dir = brain_dir / "tier1"
        if tier1_dir.exists():
            tiers["tier1"] = [f.stem for f in tier1_dir.glob("*.py") if f.name != "__init__.py"]
        
        # Tier 2: Templates
        tier2_dir = brain_dir / "tier2"
        if tier2_dir.exists():
            tiers["tier2"] = [f.stem for f in tier2_dir.glob("*.py") if f.name != "__init__.py"]
        
        # Tier 3: Knowledge
        tier3_dir = brain_dir / "tier3"
        if tier3_dir.exists():
            tiers["tier3"] = [f.stem for f in tier3_dir.glob("*.py") if f.name != "__init__.py"]
    
    return {"tiers": tiers}
